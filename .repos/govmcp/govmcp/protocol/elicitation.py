#!/usr/bin/env python3
"""
govmcp.protocol.elicitation — 用户交互支持 (MCP 2025.11)

提供安全带外用户交互功能，支持：
- 信息请求（ElicitRequest）
- URL Mode Elicitation
- 表单交互
- 安全提示确认
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union


class ElicitType(str, Enum):
    """交互类型"""

    REQUEST = "request"
    CONFIRM = "confirm"
    INPUT = "input"
    SELECT = "select"
    URL = "url"


class ElicitStatus(str, Enum):
    """交互状态"""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELED = "canceled"


@dataclass
class ElicitRequest:
    """
    用户交互请求

    用于向用户请求额外信息或确认。
    """

    message: str
    requested_schema: dict[str, Any]
    elicit_type: ElicitType | str = ElicitType.REQUEST
    timeout: float = 300.0
    id: str | None = None
    created_at: float | None = None
    expires_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.id is None:
            self.id = f"elicit_{uuid.uuid4().hex[:16]}"
        if self.created_at is None:
            self.created_at = time.time()
        if self.expires_at is None:
            self.expires_at = self.created_at + self.timeout

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "message": self.message,
            "requestedSchema": self.requested_schema,
            "type": self.elicit_type.value
            if isinstance(self.elicit_type, ElicitType)
            else self.elicit_type,
            "timeout": self.timeout,
            "createdAt": self.created_at,
            "expiresAt": self.expires_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ElicitRequest:
        """从字典创建"""
        return cls(
            id=data.get("id"),
            message=data.get("message", ""),
            requested_schema=data.get("requestedSchema", {}),
            elicit_type=data.get("type", "request"),
            timeout=data.get("timeout", 300.0),
            created_at=data.get("createdAt"),
            expires_at=data.get("expiresAt"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ElicitResponse:
    """用户交互响应"""

    request_id: str
    status: ElicitStatus | str
    value: Any | None = None
    error: str | None = None
    responded_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.responded_at is None and self.status != ElicitStatus.PENDING:
            self.responded_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        result = {
            "requestId": self.request_id,
            "status": self.status.value if isinstance(self.status, ElicitStatus) else self.status,
        }
        if self.value is not None:
            result["value"] = self.value
        if self.error is not None:
            result["error"] = self.error
        if self.responded_at is not None:
            result["respondedAt"] = self.responded_at
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ElicitResponse:
        """从字典创建"""
        return cls(
            request_id=data.get("requestId", ""),
            status=data.get("status", ElicitStatus.PENDING),
            value=data.get("value"),
            error=data.get("error"),
            responded_at=data.get("respondedAt"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class URLElicitation:
    """
    URL Mode Elicitation

    通过 URL 方式向用户请求交互。
    """

    url: str
    title: str
    request_id: str
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    body: str | None = None
    timeout: float = 300.0
    created_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        result = {
            "url": self.url,
            "title": self.title,
            "requestId": self.request_id,
            "method": self.method,
            "timeout": self.timeout,
            "createdAt": self.created_at,
        }
        if self.headers:
            result["headers"] = self.headers
        if self.body is not None:
            result["body"] = self.body
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> URLElicitation:
        """从字典创建"""
        return cls(
            url=data.get("url", ""),
            title=data.get("title", ""),
            request_id=data.get("requestId", ""),
            method=data.get("method", "GET"),
            headers=data.get("headers", {}),
            body=data.get("body"),
            timeout=data.get("timeout", 300.0),
            created_at=data.get("createdAt"),
            metadata=data.get("metadata", {}),
        )


class ElicitationHandler:
    """交互处理器接口"""

    def handle_request(
        self,
        request: ElicitRequest,
    ) -> ElicitResponse:
        """处理交互请求"""
        raise NotImplementedError

    def can_handle(self, request: ElicitRequest) -> bool:
        """检查是否可以处理"""
        return False


class ConsoleElicitationHandler(ElicitationHandler):
    """控制台交互处理器"""

    def __init__(self, input_func: Callable[[str], str] | None = None):
        self._input_func = input_func

    def handle_request(self, request: ElicitRequest) -> ElicitResponse:
        """处理交互请求"""
        if request.elicit_type == ElicitType.CONFIRM:
            response = self._get_confirmation(request.message)
            return ElicitResponse(
                request_id=request.id,
                status=ElicitStatus.ACCEPTED if response else ElicitStatus.REJECTED,
                value=response,
            )
        elif request.elicit_type == ElicitType.INPUT:
            response = self._get_input(request.message, request.requested_schema)
            return ElicitResponse(
                request_id=request.id,
                status=ElicitStatus.ACCEPTED,
                value=response,
            )
        else:
            response = self._get_input(request.message, request.requested_schema)
            return ElicitResponse(
                request_id=request.id,
                status=ElicitStatus.ACCEPTED,
                value=response,
            )

    def _get_confirmation(self, message: str) -> bool:
        """获取确认"""
        if self._input_func:
            response = self._input_func(f"{message} (y/n): ")
            return response.lower() in ["y", "yes"]
        return False

    def _get_input(self, message: str, schema: dict[str, Any]) -> Any:
        """获取输入"""
        if self._input_func:
            response = self._input_func(f"{message}: ")
            return response
        return None


class ElicitationManager:
    """
    交互管理器

    管理用户交互请求的生命周期。
    """

    def __init__(self):
        self._pending_requests: dict[str, ElicitRequest] = {}
        self._responses: dict[str, ElicitResponse] = {}
        self._handlers: list[ElicitationHandler] = []
        self._lock = threading.RLock()
        self._default_handler: ElicitationHandler | None = None
        self._callbacks: dict[str, Callable[[ElicitResponse], None]] = {}

    def add_handler(self, handler: ElicitationHandler) -> None:
        """添加处理器"""
        self._handlers.append(handler)

    def set_default_handler(self, handler: ElicitationHandler) -> None:
        """设置默认处理器"""
        self._default_handler = handler

    def register_callback(
        self,
        request_id: str,
        callback: Callable[[ElicitResponse], None],
    ) -> None:
        """注册回调"""
        self._callbacks[request_id] = callback

    def create_request(
        self,
        message: str,
        requested_schema: dict[str, Any] | None = None,
        elicit_type: ElicitType | str = ElicitType.REQUEST,
        timeout: float = 300.0,
        metadata: dict[str, Any] | None = None,
    ) -> ElicitRequest:
        """
        创建交互请求

        Args:
            message: 消息内容
            requested_schema: 请求的数据模式
            elicit_type: 交互类型
            timeout: 超时时间
            metadata: 元数据

        Returns:
            交互请求
        """
        if requested_schema is None:
            requested_schema = {"type": "string"}

        request = ElicitRequest(
            message=message,
            requested_schema=requested_schema,
            elicit_type=elicit_type,
            timeout=timeout,
            metadata=metadata or {},
        )

        with self._lock:
            self._pending_requests[request.id] = request

        return request

    def get_request(self, request_id: str) -> ElicitRequest | None:
        """获取交互请求"""
        with self._lock:
            return self._pending_requests.get(request_id)

    def submit_response(self, response: ElicitResponse) -> bool:
        """
        提交响应

        Args:
            response: 交互响应

        Returns:
            是否提交成功
        """
        with self._lock:
            request = self._pending_requests.get(response.request_id)
            if request is None:
                return False

            if response.status == ElicitStatus.PENDING:
                return False

            del self._pending_requests[response.request_id]
            self._responses[response.request_id] = response

        if response.request_id in self._callbacks:
            callback = self._callbacks.pop(response.request_id)
            try:
                callback(response)
            except Exception:
                pass

        return True

    def accept(
        self,
        request_id: str,
        value: Any,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """接受请求"""
        response = ElicitResponse(
            request_id=request_id,
            status=ElicitStatus.ACCEPTED,
            value=value,
            metadata=metadata or {},
        )
        return self.submit_response(response)

    def reject(
        self,
        request_id: str,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """拒绝请求"""
        response = ElicitResponse(
            request_id=request_id,
            status=ElicitStatus.REJECTED,
            error=error,
            metadata=metadata or {},
        )
        return self.submit_response(response)

    def cancel(self, request_id: str) -> bool:
        """取消请求"""
        with self._lock:
            if request_id not in self._pending_requests:
                return False
            del self._pending_requests[request_id]

        response = ElicitResponse(
            request_id=request_id,
            status=ElicitStatus.CANCELED,
        )
        self._responses[request_id] = response
        return True

    def expire_requests(self) -> int:
        """
        使过期的请求过期

        Returns:
            过期的请求数量
        """
        now = time.time()
        expired = 0

        with self._lock:
            to_expire = []
            for request_id, request in self._pending_requests.items():
                if request.expires_at and now > request.expires_at:
                    to_expire.append(request_id)

            for request_id in to_expire:
                del self._pending_requests[request_id]
                response = ElicitResponse(
                    request_id=request_id,
                    status=ElicitStatus.EXPIRED,
                )
                self._responses[request_id] = response
                expired += 1

        return expired

    def get_pending_requests(
        self,
        limit: int = 100,
    ) -> list[ElicitRequest]:
        """获取待处理的请求"""
        with self._lock:
            requests = list(self._pending_requests.values())
        requests.sort(key=lambda r: r.created_at, reverse=True)
        return requests[:limit]

    def get_response(self, request_id: str) -> ElicitResponse | None:
        """获取响应"""
        with self._lock:
            return self._responses.get(request_id)

    def get_pending_count(self) -> int:
        """获取待处理请求数量"""
        with self._lock:
            return len(self._pending_requests)

    def create_url_elicitation(
        self,
        url: str,
        title: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        body: str | None = None,
        timeout: float = 300.0,
        metadata: dict[str, Any] | None = None,
    ) -> URLElicitation:
        """
        创建 URL 交互

        Args:
            url: 目标 URL
            title: 标题
            method: HTTP 方法
            headers: HTTP 头
            body: 请求体
            timeout: 超时时间
            metadata: 元数据

        Returns:
            URL 交互对象
        """
        request_id = f"url_{uuid.uuid4().hex[:16]}"
        return URLElicitation(
            url=url,
            title=title,
            request_id=request_id,
            method=method,
            headers=headers or {},
            body=body,
            timeout=timeout,
            metadata=metadata or {},
        )

    def create_confirm_request(
        self,
        message: str,
        title: str | None = None,
        timeout: float = 300.0,
    ) -> ElicitRequest:
        """创建确认请求"""
        return self.create_request(
            message=message,
            requested_schema={
                "type": "object",
                "properties": {"confirmed": {"type": "boolean", "description": title or message}},
                "required": ["confirmed"],
            },
            elicit_type=ElicitType.CONFIRM,
            timeout=timeout,
        )

    def create_input_request(
        self,
        message: str,
        field_name: str,
        field_type: str = "string",
        required: bool = True,
        timeout: float = 300.0,
    ) -> ElicitRequest:
        """创建输入请求"""
        return self.create_request(
            message=message,
            requested_schema={
                "type": "object",
                "properties": {field_name: {"type": field_type, "description": message}},
                "required": [field_name] if required else [],
            },
            elicit_type=ElicitType.INPUT,
            timeout=timeout,
        )

    def create_select_request(
        self,
        message: str,
        options: list[str],
        timeout: float = 300.0,
    ) -> ElicitRequest:
        """创建选择请求"""
        return self.create_request(
            message=message,
            requested_schema={
                "type": "object",
                "properties": {
                    "selection": {"type": "string", "enum": options, "description": message}
                },
                "required": ["selection"],
            },
            elicit_type=ElicitType.SELECT,
            timeout=timeout,
        )

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            total_responses = len(self._responses)
            accepted = sum(1 for r in self._responses.values() if r.status == ElicitStatus.ACCEPTED)
            rejected = sum(1 for r in self._responses.values() if r.status == ElicitStatus.REJECTED)
            expired = sum(1 for r in self._responses.values() if r.status == ElicitStatus.EXPIRED)

            return {
                "pending": len(self._pending_requests),
                "total_responses": total_responses,
                "accepted": accepted,
                "rejected": rejected,
                "expired": expired,
            }


def create_secure_prompt_request(
    message: str,
    resource_uri: str | None = None,
    timeout: float = 300.0,
) -> ElicitRequest:
    """
    创建安全提示确认请求

    Args:
        message: 消息内容
        resource_uri: 资源 URI
        timeout: 超时时间

    Returns:
        交互请求
    """
    metadata = {}
    if resource_uri:
        metadata["resourceUri"] = resource_uri

    return ElicitRequest(
        message=message,
        requested_schema={
            "type": "object",
            "properties": {"approved": {"type": "boolean", "description": "是否批准此操作"}},
            "required": ["approved"],
        },
        elicit_type=ElicitType.CONFIRM,
        timeout=timeout,
        metadata=metadata,
    )
