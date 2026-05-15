"""
EventBus 事件总线 - Python 实现

适配 Harness Runtime 的 TypeScript EventBus，提供：
- 事件类型定义
- 事件订阅/发布
- 事件过滤
- 错误处理
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """事件类型 - 对应 Harness EventBus"""

    AGENT_START = "agent:start"
    AGENT_END = "agent:end"
    AGENT_ERROR = "agent:error"

    LOOP_START = "loop:start"
    LOOP_END = "loop:end"
    LOOP_ITERATION = "loop:iteration"

    LLM_REQUEST = "llm:request"
    LLM_RESPONSE = "llm:response"
    LLM_STREAM = "llm:stream"
    LLM_ERROR = "llm:error"

    TOOL_CALL = "tool:call"
    TOOL_RESULT = "tool:result"
    TOOL_ERROR = "tool:error"

    FEEDBACK_REQUEST = "feedback:request"
    FEEDBACK_RECEIVE = "feedback:receive"
    FEEDBACK_TIMEOUT = "feedback:timeout"

    SESSION_START = "session:start"
    SESSION_END = "session:end"

    SANDBOX_START = "sandbox:start"
    SANDBOX_END = "sandbox:end"
    SANDBOX_ERROR = "sandbox:error"

    TAIJI_VERIFY_START = "taiji:verify_start"
    TAIJI_VERIFY_RESULT = "taiji:verify_result"
    TAIJI_VERIFY_ERROR = "taiji:verify_error"

    USER_MESSAGE = "user:message"
    ASSISTANT_MESSAGE = "assistant:message"


@dataclass
class Event:
    """事件基类"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.AGENT_START
    timestamp: float = field(default_factory=time.time)
    session_id: str = ""
    trace_id: str = ""
    data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "data": self.data,
            "metadata": self.metadata,
        }


@dataclass
class AgentEvent(Event):
    """Agent 事件"""
    agent_id: str = ""
    agent_name: str = ""
    agent_type: str = ""


@dataclass
class LLMEvent(Event):
    """LLM 事件"""
    model: str = ""
    messages: list = field(default_factory=list)
    tools: list = field(default_factory=list)
    tokens_used: int = 0
    latency_ms: float = 0.0


@dataclass
class ToolEvent(Event):
    """工具调用事件"""
    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)
    tool_result: Any = None
    execution_time_ms: float = 0.0


@dataclass
class FeedbackEvent(Event):
    """反馈事件"""
    feedback_type: str = ""
    content: str = ""
    decision: str = ""
    confidence: float = 0.0


@dataclass
class VerifyEvent(Event):
    """Taiji Verify 事件"""
    verify_type: str = ""
    delta_s: float = 0.0
    zone: str = ""
    passed: bool = True
    corrections: list = field(default_factory=list)


class EventFilter:
    """事件过滤器"""

    def __init__(
        self,
        event_types: list[EventType] | None = None,
        session_id: str | None = None,
        trace_id: str | None = None,
        metadata_filter: dict | None = None,
    ):
        self.event_types = set(event_types) if event_types else None
        self.session_id = session_id
        self.trace_id = trace_id
        self.metadata_filter = metadata_filter or {}

    def matches(self, event: Event) -> bool:
        """检查事件是否匹配"""
        if self.event_types and event.event_type not in self.event_types:
            return False

        if self.session_id and event.session_id != self.session_id:
            return False

        if self.trace_id and event.trace_id != self.trace_id:
            return False

        for key, value in self.metadata_filter.items():
            if event.metadata.get(key) != value:
                return False

        return True


SubscriptionId = str


class EventSubscriber:
    """事件订阅者"""

    def __init__(
        self,
        callback: Callable[[Event], Any],
        filter: EventFilter | None = None,
        async_mode: bool = True,
    ):
        self.callback = callback
        self.filter = filter or EventFilter()
        self.async_mode = async_mode
        self.subscription_id: SubscriptionId = str(uuid.uuid4())
        self.active = True

    async def handle(self, event: Event):
        """处理事件"""
        if not self.active:
            return

        if not self.filter.matches(event):
            return

        try:
            if self.async_mode and asyncio.iscoroutinefunction(self.callback):
                await self.callback(event)
            else:
                self.callback(event)
        except Exception as e:
            logger.error(f"Event handler error: {e}")


class EventBus:
    """
    事件总线

    提供事件发布/订阅功能，支持：
    - 同步/异步订阅
    - 事件过滤
    - 通配符订阅
    - 错误处理
    """

    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self._subscribers: dict[EventType, list[EventSubscriber]] = defaultdict(list)
        self._wildcard_subscribers: list[EventSubscriber] = []
        self._event_history: list[Event] = []
        self._max_history: int = 1000
        self._lock = asyncio.Lock()

        self._event_counts: dict[EventType, int] = defaultdict(int)
        self._handlers_errors: int = 0

    def subscribe(
        self,
        event_type: EventType | None = None,
        callback: Callable[[Event], Any] | None = None,
        filter: EventFilter | None = None,
        async_mode: bool = True,
    ) -> SubscriptionId:
        """
        订阅事件

        Args:
            event_type: 事件类型，None 表示订阅所有事件
            callback: 回调函数
            filter: 事件过滤器
            async_mode: 是否异步执行回调

        Returns:
            订阅ID
        """
        if callback is None:
            raise ValueError("callback is required")

        subscriber = EventSubscriber(
            callback=callback,
            filter=filter or EventFilter(),
            async_mode=async_mode,
        )

        if event_type is None:
            self._wildcard_subscribers.append(subscriber)
        else:
            self._subscribers[event_type].append(subscriber)

        if self.enable_logging:
            logger.debug(f"Subscribed to event: {event_type or '*'}")

        return subscriber.subscription_id

    def unsubscribe(self, subscription_id: SubscriptionId) -> bool:
        """取消订阅"""
        for subscribers in self._subscribers.values():
            for i, sub in enumerate(subscribers):
                if sub.subscription_id == subscription_id:
                    sub.active = False
                    subscribers.pop(i)
                    return True

        for i, sub in enumerate(self._wildcard_subscribers):
            if sub.subscription_id == subscription_id:
                sub.active = False
                self._wildcard_subscribers.pop(i)
                return True

        return False

    async def publish(self, event: Event):
        """发布事件"""
        async with self._lock:
            self._event_counts[event.event_type] += 1

            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)

        if self.enable_logging:
            logger.debug(f"Publishing event: {event.event_type.value}")

        tasks = []

        for subscriber in self._subscribers.get(event.event_type, []):
            task = subscriber.handle(event)
            if asyncio.iscoroutine(task):
                tasks.append(task)

        for subscriber in self._wildcard_subscribers:
            task = subscriber.handle(event)
            if asyncio.iscoroutine(task):
                tasks.append(task)

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    self._handlers_errors += 1
                    logger.error(f"Event handler error: {result}")

    def publish_sync(self, event: Event):
        """同步发布事件（用于非异步环境）"""
        import threading

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.publish(event))
        finally:
            loop.close()

    def get_history(
        self,
        event_type: EventType | None = None,
        limit: int = 100,
    ) -> list[Event]:
        """获取事件历史"""
        history = self._event_history

        if event_type:
            history = [e for e in history if e.event_type == event_type]

        return history[-limit:]

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "total_events": sum(self._event_counts.values()),
            "event_counts": {k.value: v for k, v in self._event_counts.items()},
            "active_subscribers": sum(
                len(subs) for subs in self._subscribers.values()
            ) + len(self._wildcard_subscribers),
            "handler_errors": self._handlers_errors,
        }

    def clear_history(self):
        """清空事件历史"""
        self._event_history.clear()
        self._event_counts.clear()


class EventBusManager:
    """事件总线管理器"""

    def __init__(self):
        self._buses: dict[str, EventBus] = {"default": EventBus()}
        self._current_bus: str = "default"

    def create_bus(self, name: str) -> EventBus:
        """创建新的事件总线"""
        if name in self._buses:
            return self._buses[name]

        bus = EventBus()
        self._buses[name] = bus
        return bus

    def get_bus(self, name: str | None = None) -> EventBus:
        """获取事件总线"""
        return self._buses.get(name or self._current_bus, self._buses["default"])

    def set_default_bus(self, name: str):
        """设置默认事件总线"""
        if name in self._buses:
            self._current_bus = name

    def subscribe(
        self,
        event_type: EventType | None = None,
        callback: Callable[[Event], Any] | None = None,
        bus_name: str | None = None,
        **kwargs,
    ) -> SubscriptionId:
        """订阅事件"""
        bus = self.get_bus(bus_name)
        return bus.subscribe(event_type=event_type, callback=callback, **kwargs)

    async def publish(self, event: Event, bus_name: str | None = None):
        """发布事件"""
        bus = self.get_bus(bus_name)
        await bus.publish(event)


_global_event_bus_manager = EventBusManager()


def get_event_bus() -> EventBus:
    """获取全局事件总线"""
    return _global_event_bus_manager.get_bus()


def subscribe(
    event_type: EventType | None = None,
    callback: Callable[[Event], Any] | None = None,
    **kwargs,
) -> SubscriptionId:
    """全局订阅事件"""
    return _global_event_bus_manager.subscribe(
        event_type=event_type, callback=callback, **kwargs
    )


async def publish(event: Event):
    """全局发布事件"""
    await _global_event_bus_manager.publish(event)


class EventBusPlugin:
    """
    EventBus Plugin - 用于集成到 Harness

    提供标准化的 Plugin 接口
    """

    def __init__(self, bus_name: str = "default"):
        self.bus_name = bus_name
        self._subscriptions: list[SubscriptionId] = []

    async def on_load(self):
        """加载插件"""
        logger.info(f"EventBusPlugin loaded: {self.bus_name}")

    async def on_unload(self):
        """卸载插件"""
        bus = get_event_bus()
        for sub_id in self._subscriptions:
            bus.unsubscribe(sub_id)
        logger.info(f"EventBusPlugin unloaded: {self.bus_name}")

    def subscribe(self, event_type: EventType, callback: Callable):
        """订阅事件"""
        sub_id = subscribe(event_type, callback, bus_name=self.bus_name)
        self._subscriptions.append(sub_id)
        return sub_id
