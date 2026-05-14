#!/usr/bin/env python3
"""
govmcp.protocol.tasks — 异步任务支持 (MCP 2025.11)

提供异步任务生命周期管理，包括任务创建、状态追踪、结果获取和取消功能。
支持 SSE (Server-Sent Events) 实时推送任务状态变更。
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "pending"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class TaskNotFoundError(Exception):
    """任务不存在异常"""

    pass


class TaskCancelError(Exception):
    """任务取消失败异常"""

    pass


@dataclass
class TaskInfo:
    """任务信息数据类"""

    id: str
    status: TaskStatus
    tool_name: str
    arguments: dict[str, Any]
    progress: float = 0.0
    result: Any | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    timeout: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        result = {
            "id": self.id,
            "status": self.status.value if isinstance(self.status, TaskStatus) else self.status,
            "toolName": self.tool_name,
            "arguments": self.arguments,
            "progress": self.progress,
            "createdAt": self.created_at,
            "metadata": self.metadata,
        }
        if self.started_at is not None:
            result["startedAt"] = self.started_at
        if self.completed_at is not None:
            result["completedAt"] = self.completed_at
        if self.timeout is not None:
            result["timeout"] = self.timeout
        if self.result is not None:
            result["result"] = self.result
        if self.error is not None:
            result["error"] = self.error
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskInfo:
        """从字典创建"""
        status = data.get("status")
        if isinstance(status, str):
            status = TaskStatus(status)
        return cls(
            id=data["id"],
            status=status,
            tool_name=data.get("toolName", ""),
            arguments=data.get("arguments", {}),
            progress=data.get("progress", 0.0),
            result=data.get("result"),
            error=data.get("error"),
            created_at=data.get("createdAt", time.time()),
            started_at=data.get("startedAt"),
            completed_at=data.get("completedAt"),
            timeout=data.get("timeout"),
            metadata=data.get("metadata", {}),
        )


class TaskSubscriber:
    """任务订阅者（用于 SSE）"""

    def __init__(self, task_ids: set[str] | None = None):
        self.task_ids = task_ids
        self.queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._closed = False

    async def send(self, event: dict[str, Any]) -> None:
        """发送事件到订阅者"""
        if self._closed:
            return
        await self.queue.put(event)

    def close(self) -> None:
        """关闭订阅"""
        self._closed = True
        if not self.queue.empty():
            try:
                while True:
                    self.queue.get_nowait()
            except asyncio.QueueEmpty:
                pass

    async def events(self) -> AsyncIterator[dict[str, Any]]:
        """异步事件迭代器"""
        while not self._closed:
            try:
                event = await asyncio.wait_for(self.queue.get(), timeout=30.0)
                yield event
            except asyncio.TimeoutError:
                yield {"type": "heartbeat", "timestamp": time.time()}


class TaskManager:
    """
    异步任务管理器

    负责管理异步任务的完整生命周期，支持：
    - 任务创建和追踪
    - 状态轮询和 SSE 订阅
    - 任务取消和清理
    - 超时控制
    """

    def __init__(self, default_timeout: float = 300.0):
        """
        初始化任务管理器

        Args:
            default_timeout: 默认超时时间（秒）
        """
        self._tasks: dict[str, TaskInfo] = {}
        self._lock = threading.RLock()
        self._subscribers: dict[str, set[TaskSubscriber]] = defaultdict(set)
        self._all_subscribers: set[TaskSubscriber] = set()
        self._default_timeout = default_timeout
        self._tool_registry: dict[str, Callable[..., Any]] = {}
        self._executor: asyncio.AbstractEventLoop | None = None

    def register_tool(self, name: str, handler: Callable[..., Any]) -> None:
        """注册工具处理器"""
        self._tool_registry[name] = handler

    def set_executor(self, loop: asyncio.AbstractEventLoop) -> None:
        """设置事件循环"""
        self._executor = loop

    def _generate_task_id(self) -> str:
        """生成唯一任务ID"""
        return f"task_{uuid.uuid4().hex[:16]}"

    def create_task(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        timeout: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        创建异步任务

        Args:
            tool_name: 工具名称
            arguments: 工具参数
            timeout: 超时时间（秒）
            metadata: 元数据

        Returns:
            任务ID
        """
        task_id = self._generate_task_id()
        timeout = timeout if timeout is not None else self._default_timeout

        task_info = TaskInfo(
            id=task_id,
            status=TaskStatus.PENDING,
            tool_name=tool_name,
            arguments=arguments or {},
            timeout=timeout,
            metadata=metadata or {},
        )

        with self._lock:
            self._tasks[task_id] = task_info

        self._notify_subscribers(task_id, "created", task_info)

        if self._executor:
            asyncio.run_coroutine_threadsafe(self._execute_task_async(task_id), self._executor)

        return task_id

    async def _execute_task_async(self, task_id: str) -> None:
        """异步执行任务"""
        tool_name = None
        arguments = {}
        timeout = self._default_timeout

        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return
            tool_name = task.tool_name
            arguments = task.arguments
            timeout = task.timeout or self._default_timeout
            task.status = TaskStatus.WORKING
            task.started_at = time.time()

        self._notify_subscribers(task_id, "status_changed", task)

        try:
            handler = self._tool_registry.get(tool_name)
            if handler is None:
                raise ValueError(f"Tool not found: {tool_name}")

            if asyncio.iscoroutinefunction(handler):
                result = await asyncio.wait_for(handler(**arguments), timeout=timeout)
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: handler(**arguments)
                )

            with self._lock:
                task = self._tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = time.time()
                task.progress = 1.0

            self._notify_subscribers(task_id, "completed", task)

        except asyncio.TimeoutError:
            with self._lock:
                task = self._tasks[task_id]
                task.status = TaskStatus.FAILED
                task.error = f"Task timeout after {timeout} seconds"
                task.completed_at = time.time()

            self._notify_subscribers(task_id, "failed", task)

        except Exception as e:
            with self._lock:
                task = self._tasks[task_id]
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = time.time()

            self._notify_subscribers(task_id, "failed", task)

    def execute_task_sync(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> str:
        """
        同步执行任务（创建后立即执行）

        Args:
            tool_name: 工具名称
            arguments: 工具参数
            timeout: 超时时间（秒）

        Returns:
            任务ID
        """
        task_id = self._generate_task_id()
        timeout = timeout if timeout is not None else self._default_timeout

        task_info = TaskInfo(
            id=task_id,
            status=TaskStatus.WORKING,
            tool_name=tool_name,
            arguments=arguments or {},
            timeout=timeout,
            started_at=time.time(),
        )

        with self._lock:
            self._tasks[task_id] = task_info

        try:
            handler = self._tool_registry.get(tool_name)
            if handler is None:
                raise ValueError(f"Tool not found: {tool_name}")

            result = handler(**arguments)

            with self._lock:
                task = self._tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = time.time()
                task.progress = 1.0

        except Exception as e:
            with self._lock:
                task = self._tasks[task_id]
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = time.time()

        return task_id

    def get_task_status(self, task_id: str) -> TaskStatus:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态

        Raises:
            TaskNotFoundError: 任务不存在
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise TaskNotFoundError(f"Task not found: {task_id}")
            return task.status

    def get_task_info(self, task_id: str) -> TaskInfo:
        """
        获取完整任务信息

        Args:
            task_id: 任务ID

        Returns:
            任务信息

        Raises:
            TaskNotFoundError: 任务不存在
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise TaskNotFoundError(f"Task not found: {task_id}")
            return task

    def get_task_result(self, task_id: str) -> Any:
        """
        获取任务结果

        Args:
            task_id: 任务ID

        Returns:
            任务结果

        Raises:
            TaskNotFoundError: 任务不存在
            ValueError: 任务尚未完成
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise TaskNotFoundError(f"Task not found: {task_id}")

            if task.status not in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                raise ValueError(f"Task not completed: {task_id}")

            if task.status == TaskStatus.FAILED:
                raise ValueError(f"Task failed: {task.error}")

            return task.result

    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消

        Raises:
            TaskNotFoundError: 任务不存在
            TaskCancelError: 任务无法取消
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise TaskNotFoundError(f"Task not found: {task_id}")

            if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED):
                raise TaskCancelError(f"Task already terminal: {task.status.value}")

            task.status = TaskStatus.CANCELED
            task.completed_at = time.time()

        self._notify_subscribers(task_id, "canceled", task)
        return True

    def list_tasks(
        self,
        status: TaskStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TaskInfo]:
        """
        列出任务

        Args:
            status: 按状态过滤
            limit: 返回数量限制
            offset: 跳过数量

        Returns:
            任务列表
        """
        with self._lock:
            tasks = list(self._tasks.values())

        if status is not None:
            tasks = [t for t in tasks if t.status == status]

        tasks.sort(key=lambda t: t.created_at, reverse=True)

        return tasks[offset : offset + limit]

    def cleanup_completed_tasks(self, max_age: float = 3600.0) -> int:
        """
        清理已完成任务

        Args:
            max_age: 最长保留时间（秒）

        Returns:
            清理的任务数量
        """
        now = time.time()
        removed = 0

        with self._lock:
            to_remove = []
            for task_id, task in self._tasks.items():
                if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED):
                    if task.completed_at is not None and now - task.completed_at > max_age:
                        to_remove.append(task_id)

            for task_id in to_remove:
                del self._tasks[task_id]
                for subscribers in self._subscribers.values():
                    for sub in subscribers:
                        sub.close()
                if task_id in self._subscribers:
                    del self._subscribers[task_id]
                removed += 1

        return removed

    def subscribe(
        self,
        task_id: str | None = None,
        task_ids: set[str] | None = None,
    ) -> TaskSubscriber:
        """
        订阅任务更新

        Args:
            task_id: 特定任务ID
            task_ids: 多个任务ID

        Returns:
            订阅者对象
        """
        target_ids = task_ids.copy() if task_ids else set()
        if task_id:
            target_ids.add(task_id)

        subscriber = TaskSubscriber(target_ids if target_ids else None)

        with self._lock:
            if target_ids:
                for tid in target_ids:
                    self._subscribers[tid].add(subscriber)
            else:
                self._all_subscribers.add(subscriber)

        return subscriber

    def unsubscribe(self, subscriber: TaskSubscriber) -> None:
        """
        取消订阅

        Args:
            subscriber: 订阅者对象
        """
        with self._lock:
            subscriber.close()
            if subscriber in self._all_subscribers:
                self._all_subscribers.discard(subscriber)
            for subscribers in self._subscribers.values():
                subscribers.discard(subscriber)

    def _notify_subscribers(self, task_id: str, event_type: str, task: TaskInfo) -> None:
        """通知订阅者"""
        event = {
            "type": event_type,
            "taskId": task_id,
            "timestamp": time.time(),
            "task": task.to_dict(),
        }

        with self._lock:
            if task_id in self._subscribers:
                for sub in list(self._subscribers[task_id]):
                    asyncio.run_coroutine_threadsafe(
                        sub.send(event), self._executor or asyncio.new_event_loop()
                    )

            for sub in list(self._all_subscribers):
                asyncio.run_coroutine_threadsafe(
                    sub.send(event), self._executor or asyncio.new_event_loop()
                )

    def update_progress(self, task_id: str, progress: float) -> bool:
        """
        更新任务进度

        Args:
            task_id: 任务ID
            progress: 进度值 (0.0 - 1.0)

        Returns:
            是否更新成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            task.progress = max(0.0, min(1.0, progress))

        self._notify_subscribers(task_id, "progress", task)
        return True

    def get_task_stats(self) -> dict[str, Any]:
        """获取任务统计信息"""
        with self._lock:
            total = len(self._tasks)
            by_status = defaultdict(int)
            for task in self._tasks.values():
                by_status[task.status.value] += 1

            return {
                "total": total,
                "byStatus": dict(by_status),
                "subscribers": len(self._all_subscribers)
                + sum(len(subs) for subs in self._subscribers.values()),
            }


from typing import AsyncIterator


class SSEHandler:
    """SSE 事件处理器"""

    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def stream_events(
        self,
        task_ids: list[str] | None = None,
        all_tasks: bool = False,
    ) -> AsyncIterator[str]:
        """生成 SSE 事件流"""
        subscriber = None

        try:
            if all_tasks:
                subscriber = self.task_manager.subscribe()
            elif task_ids:
                subscriber = self.task_manager.subscribe(task_ids=set(task_ids))
            else:
                subscriber = TaskSubscriber()

            async for event in subscriber.events():
                yield f"data: {json.dumps(event)}\n\n"

        finally:
            if subscriber:
                self.task_manager.unsubscribe(subscriber)


def create_sse_response(
    task_manager: TaskManager,
    task_ids: list[str] | None = None,
    all_tasks: bool = False,
) -> dict[str, Any]:
    """
    创建 SSE 响应

    Args:
        task_manager: 任务管理器
        task_ids: 任务ID列表
        all_tasks: 订阅所有任务

    Returns:
        SSE 响应配置
    """
    return {
        "contentType": "text/event-stream",
        "handler": SSEHandler(task_manager),
    }
