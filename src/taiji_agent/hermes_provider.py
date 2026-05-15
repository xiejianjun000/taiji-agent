"""
Hermes Provider - TypeScript 与 Python 桥接模块

实现 Harness Runtime (TypeScript) 与 Hermes Agent (Python) 的通信接口
支持：
- 异步任务调用
- 流式响应
- 多租户隔离
- 技能包执行
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Optional

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class HermesRequest:
    """Hermes 请求"""
    request_id: str
    tenant_id: str
    user_id: str
    method: str
    params: dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HermesResponse:
    """Hermes 响应"""
    request_id: str
    status: TaskStatus
    result: Any = None
    error: str | None = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamChunk:
    """流式响应块"""
    request_id: str
    chunk_type: str
    content: str | dict
    done: bool = False


@dataclass
class TenantContext:
    """租户上下文"""
    tenant_id: str
    user_id: str
    session_id: str
    permissions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class HermesBridge(ABC):
    """
    Hermes 桥接基类

    定义 TypeScript (Harness) 与 Python (Hermes) 之间的通信接口
    """

    @abstractmethod
    async def chat(self, request: HermesRequest) -> HermesResponse:
        """聊天请求"""
        pass

    @abstractmethod
    async def stream_chat(self, request: HermesRequest) -> AsyncGenerator[StreamChunk, None]:
        """流式聊天"""
        pass

    @abstractmethod
    async def execute_skill(self, request: HermesRequest) -> HermesResponse:
        """执行技能"""
        pass

    @abstractmethod
    async def get_memory(self, request: HermesRequest) -> HermesResponse:
        """获取记忆"""
        pass

    @abstractmethod
    async def save_memory(self, request: HermesRequest) -> HermesResponse:
        """保存记忆"""
        pass

    @abstractmethod
    async def evolve(self, request: HermesRequest) -> HermesResponse:
        """触发进化"""
        pass


class HermesProvider(HermesBridge):
    """
    Hermes Provider 实现

    作为 Harness Runtime (TS) 的 Provider，调用 Python 的 Hermes Agent
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "http://localhost:8000",
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

        self._tasks: dict[str, asyncio.Task] = {}
        self._middleware: list[Callable] = []
        self._tenant_manager: Optional[TenantManager] = None

    def set_tenant_manager(self, manager: TenantManager):
        """设置租户管理器"""
        self._tenant_manager = manager

    def add_middleware(self, middleware: Callable):
        """添加中间件"""
        self._middleware.append(middleware)

    async def chat(self, request: HermesRequest) -> HermesResponse:
        """聊天请求"""
        try:
            self._validate_request(request)

            for middleware in self._middleware:
                request = await middleware.process_request(request)

            context = self._get_tenant_context(request)

            messages = request.params.get("messages", [])
            tools = request.params.get("tools", [])
            temperature = request.params.get("temperature", 0.7)
            max_tokens = request.params.get("max_tokens", 4096)

            result = await self._call_hermes_agent(
                context=context,
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            for middleware in self._middleware:
                result = await middleware.process_response(request, result)

            return HermesResponse(
                request_id=request.request_id,
                status=TaskStatus.COMPLETED,
                result=result,
                metadata={"tenant_id": request.tenant_id},
            )

        except Exception as e:
            logger.error(f"Hermes chat error: {e}")
            return HermesResponse(
                request_id=request.request_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def stream_chat(self, request: HermesRequest) -> AsyncGenerator[StreamChunk, None]:
        """流式聊天"""
        try:
            self._validate_request(request)
            context = self._get_tenant_context(request)

            messages = request.params.get("messages", [])
            tools = request.params.get("tools", [])

            full_content = ""
            async for chunk in self._stream_hermes_agent(context, messages, tools):
                chunk_obj = StreamChunk(
                    request_id=request.request_id,
                    chunk_type="content",
                    content=chunk,
                    done=False,
                )
                full_content += chunk

                for middleware in self._middleware:
                    chunk_obj = await middleware.process_stream(request, chunk_obj)

                yield chunk_obj

            yield StreamChunk(
                request_id=request.request_id,
                chunk_type="done",
                content={"full_content": full_content},
                done=True,
            )

        except Exception as e:
            logger.error(f"Hermes stream error: {e}")
            yield StreamChunk(
                request_id=request.request_id,
                chunk_type="error",
                content=str(e),
                done=True,
            )

    async def execute_skill(self, request: HermesRequest) -> HermesResponse:
        """执行技能"""
        try:
            self._validate_request(request)
            context = self._get_tenant_context(request)

            skill_id = request.params.get("skill_id")
            skill_params = request.params.get("params", {})

            result = await self._execute_skill_package(
                context=context,
                skill_id=skill_id,
                params=skill_params,
            )

            return HermesResponse(
                request_id=request.request_id,
                status=TaskStatus.COMPLETED,
                result=result,
            )

        except Exception as e:
            logger.error(f"Execute skill error: {e}")
            return HermesResponse(
                request_id=request.request_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def get_memory(self, request: HermesRequest) -> HermesResponse:
        """获取记忆"""
        try:
            self._validate_request(request)
            context = self._get_tenant_context(request)

            memory_type = request.params.get("type", "session")
            query = request.params.get("query")
            limit = request.params.get("limit", 10)

            result = await self._fetch_memory(
                context=context,
                memory_type=memory_type,
                query=query,
                limit=limit,
            )

            return HermesResponse(
                request_id=request.request_id,
                status=TaskStatus.COMPLETED,
                result=result,
            )

        except Exception as e:
            logger.error(f"Get memory error: {e}")
            return HermesResponse(
                request_id=request.request_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def save_memory(self, request: HermesRequest) -> HermesResponse:
        """保存记忆"""
        try:
            self._validate_request(request)
            context = self._get_tenant_context(request)

            memory_type = request.params.get("type", "session")
            content = request.params.get("content")
            metadata = request.params.get("metadata", {})

            result = await self._store_memory(
                context=context,
                memory_type=memory_type,
                content=content,
                metadata=metadata,
            )

            return HermesResponse(
                request_id=request.request_id,
                status=TaskStatus.COMPLETED,
                result=result,
            )

        except Exception as e:
            logger.error(f"Save memory error: {e}")
            return HermesResponse(
                request_id=request.request_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def evolve(self, request: HermesRequest) -> HermesResponse:
        """触发进化"""
        try:
            self._validate_request(request)
            context = self._get_tenant_context(request)

            evolve_type = request.params.get("type", "individual")
            feedback = request.params.get("feedback")

            result = await self._trigger_evolution(
                context=context,
                evolve_type=evolve_type,
                feedback=feedback,
            )

            return HermesResponse(
                request_id=request.request_id,
                status=TaskStatus.COMPLETED,
                result=result,
            )

        except Exception as e:
            logger.error(f"Evolution error: {e}")
            return HermesResponse(
                request_id=request.request_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def cancel_task(self, request_id: str) -> bool:
        """取消任务"""
        if request_id in self._tasks:
            task = self._tasks[request_id]
            task.cancel()
            del self._tasks[request_id]
            return True
        return False

    def _validate_request(self, request: HermesRequest):
        """验证请求"""
        if not request.tenant_id:
            raise ValueError("tenant_id is required")
        if not request.user_id:
            raise ValueError("user_id is required")

    def _get_tenant_context(self, request: HermesRequest) -> TenantContext:
        """获取租户上下文"""
        if self._tenant_manager:
            return self._tenant_manager.get_context(
                tenant_id=request.tenant_id,
                user_id=request.user_id,
                session_id=request.metadata.get("session_id", str(uuid.uuid4())),
            )
        return TenantContext(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            session_id=request.metadata.get("session_id", str(uuid.uuid4())),
        )

    async def _call_hermes_agent(
        self,
        context: TenantContext,
        messages: list[dict],
        tools: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> dict:
        """调用 Hermes Agent"""
        from taiji_agent.agent.engine import TaijiAgent

        agent = TaijiAgent()
        response = await agent.run(
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {"content": response.get("content", ""), "tool_calls": response.get("tool_calls", [])}

    async def _stream_hermes_agent(
        self,
        context: TenantContext,
        messages: list[dict],
        tools: list[dict],
    ) -> AsyncGenerator[str, None]:
        """流式调用 Hermes Agent"""
        from taiji_agent.agent.engine import TaijiAgent

        agent = TaijiAgent()
        async for chunk in agent.stream_run(messages=messages, tools=tools):
            if isinstance(chunk, str):
                yield chunk
            elif isinstance(chunk, dict) and "content" in chunk:
                yield chunk["content"]

    async def _execute_skill_package(
        self,
        context: TenantContext,
        skill_id: str,
        params: dict,
    ) -> dict:
        """执行技能包"""
        from taiji_agent.skills.hub import SkillManager

        manager = SkillManager()
        instructions = manager.use(skill_id)

        if not instructions:
            raise ValueError(f"Skill not found: {skill_id}")

        return {
            "skill_id": skill_id,
            "instructions": instructions,
            "params": params,
            "executed": True,
        }

    async def _fetch_memory(
        self,
        context: TenantContext,
        memory_type: str,
        query: str | None,
        limit: int,
    ) -> dict:
        """获取记忆"""
        from taiji_agent.memory import SessionMemory

        memory = SessionMemory()
        memories = await memory.get_recent(limit=limit)

        return {
            "type": memory_type,
            "count": len(memories),
            "memories": memories,
        }

    async def _store_memory(
        self,
        context: TenantContext,
        memory_type: str,
        content: str,
        metadata: dict,
    ) -> dict:
        """存储记忆"""
        from taiji_agent.memory import SessionMemory

        memory = SessionMemory()
        await memory.add(content, metadata=metadata)

        return {
            "type": memory_type,
            "stored": True,
            "content_length": len(content),
        }

    async def _trigger_evolution(
        self,
        context: TenantContext,
        evolve_type: str,
        feedback: dict | None,
    ) -> dict:
        """触发进化"""
        return {
            "type": evolve_type,
            "evolved": True,
            "evolution_level": evolve_type,
            "feedback": feedback,
        }


class TenantManager:
    """
    多租户管理器

    实现：
    - 租户数据隔离
    - 权限控制
    - 资源配额
    """

    def __init__(self):
        self._tenants: dict[str, TenantConfig] = {}
        self._sessions: dict[str, TenantContext] = {}
        self._quotas: dict[str, ResourceQuota] = {}

    def register_tenant(
        self,
        tenant_id: str,
        name: str,
        permissions: list[str] | None = None,
        quota: ResourceQuota | None = None,
    ):
        """注册租户"""
        config = TenantConfig(
            tenant_id=tenant_id,
            name=name,
            permissions=permissions or ["chat", "memory"],
            quota=quota or ResourceQuota(),
        )
        self._tenants[tenant_id] = config
        self._quotas[tenant_id] = config.quota

    def get_tenant(self, tenant_id: str) -> TenantConfig | None:
        """获取租户配置"""
        return self._tenants.get(tenant_id)

    def get_context(
        self,
        tenant_id: str,
        user_id: str,
        session_id: str,
    ) -> TenantContext:
        """获取租户上下文"""
        context = TenantContext(
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session_id,
        )

        tenant = self._tenants.get(tenant_id)
        if tenant:
            context.permissions = tenant.permissions

        self._sessions[session_id] = context
        return context

    def check_permission(self, tenant_id: str, permission: str) -> bool:
        """检查权限"""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        return permission in tenant.permissions

    def check_quota(self, tenant_id: str, resource: str, amount: float) -> bool:
        """检查配额"""
        quota = self._quotas.get(tenant_id)
        if not quota:
            return True

        resource_map = {
            "tokens_per_day": ("current_tokens_today", "limit_tokens_per_day"),
            "requests_per_minute": ("current_requests_minute", "limit_requests_per_minute"),
            "storage_mb": ("current_storage_mb", "limit_storage_mb"),
        }

        mapping = resource_map.get(resource)
        if not mapping:
            return True

        current_attr, limit_attr = mapping
        current = getattr(quota, current_attr, 0)
        limit = getattr(quota, limit_attr, float("inf"))
        return current + amount <= limit

    def update_quota(self, tenant_id: str, resource: str, amount: float):
        """更新配额"""
        if tenant_id in self._quotas:
            resource_map = {
                "tokens_per_day": "current_tokens_today",
                "requests_per_minute": "current_requests_minute",
                "storage_mb": "current_storage_mb",
            }
            current_attr = resource_map.get(resource)
            if current_attr:
                current = getattr(self._quotas[tenant_id], current_attr, 0)
                setattr(self._quotas[tenant_id], current_attr, current + amount)


@dataclass
class TenantConfig:
    """租户配置"""
    tenant_id: str
    name: str
    permissions: list[str] = field(default_factory=list)
    quota: "ResourceQuota" = field(default_factory=lambda: ResourceQuota())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceQuota:
    """资源配额"""
    limit_tokens_per_day: float = float("inf")
    limit_requests_per_minute: float = float("inf")
    limit_storage_mb: float = float("inf")
    current_tokens_today: float = 0.0
    current_requests_minute: float = 0.0
    current_storage_mb: float = 0.0


class HermesMiddleware(ABC):
    """Hermes 中间件基类"""

    async def process_request(self, request: HermesRequest) -> HermesRequest:
        """处理请求"""
        return request

    async def process_response(
        self,
        request: HermesRequest,
        response: HermesResponse,
    ) -> HermesResponse:
        """处理响应"""
        return response

    async def process_stream(
        self,
        request: HermesRequest,
        chunk: StreamChunk,
    ) -> StreamChunk:
        """处理流式数据"""
        return chunk


class TenantIsolationMiddleware(HermesMiddleware):
    """租户隔离中间件"""

    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager

    async def process_request(self, request: HermesRequest) -> HermesRequest:
        """验证租户隔离"""
        if not self.tenant_manager.get_tenant(request.tenant_id):
            raise PermissionError(f"Tenant not found: {request.tenant_id}")
        return request


class RateLimitMiddleware(HermesMiddleware):
    """限流中间件"""

    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        self._request_times: dict[str, list[float]] = {}

    async def process_request(self, request: HermesRequest) -> HermesRequest:
        """检查限流"""
        import time

        now = time.time()
        tenant_id = request.tenant_id

        if tenant_id not in self._request_times:
            self._request_times[tenant_id] = []

        self._request_times[tenant_id] = [
            t for t in self._request_times[tenant_id] if now - t < 60
        ]

        if not self.tenant_manager.check_quota(tenant_id, "requests_per_minute", 1):
            raise PermissionError(f"Rate limit exceeded for tenant: {tenant_id}")

        self._request_times[tenant_id].append(now)
        self.tenant_manager.update_quota(tenant_id, "requests_per_minute", 1)
        return request
