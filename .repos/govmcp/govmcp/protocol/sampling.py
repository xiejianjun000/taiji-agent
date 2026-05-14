#!/usr/bin/env python3
"""
govmcp.protocol.sampling — 异步采样支持 (MCP 2025.11)

提供 LLM 采样能力，支持异步消息生成、采样参数配置和采样策略。
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

if TYPE_CHECKING:
    from govmcp.models import ModelConfig


class Role(str, Enum):
    """消息角色"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SamplingMessageRole(str, Enum):
    """采样消息角色 (MCP 2025.11)"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class SamplingMessage:
    """采样消息"""

    role: Role | SamplingMessageRole | str
    content: str
    timestamp: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "role": self.role.value
            if isinstance(self.role, (Role, SamplingMessageRole))
            else self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SamplingMessage:
        """从字典创建"""
        role = data.get("role", "user")
        if isinstance(role, str):
            try:
                role = SamplingMessageRole(role)
            except ValueError:
                role = Role(role) if role in [r.value for r in Role] else role
        return cls(
            role=role,
            content=data.get("content", ""),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SamplingParameters:
    """采样参数"""

    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    stop_sequences: list[str] | None = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    model: str | None = None
    system_prompt: str | None = None
    reasoning_effort: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        result = {
            "temperature": self.temperature,
            "maxTokens": self.max_tokens,
            "topP": self.top_p,
            "presencePenalty": self.presence_penalty,
            "frequencyPenalty": self.frequency_penalty,
        }
        if self.stop_sequences:
            result["stopSequences"] = self.stop_sequences
        if self.model:
            result["model"] = self.model
        if self.system_prompt:
            result["systemPrompt"] = self.system_prompt
        if self.reasoning_effort:
            result["reasoningEffort"] = self.reasoning_effort
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SamplingParameters:
        """从字典创建"""
        return cls(
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("maxTokens", 4096),
            top_p=data.get("topP", 0.9),
            stop_sequences=data.get("stopSequences"),
            presence_penalty=data.get("presencePenalty", 0.0),
            frequency_penalty=data.get("frequencyPenalty", 0.0),
            model=data.get("model"),
            system_prompt=data.get("systemPrompt"),
            reasoning_effort=data.get("reasoningEffort"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SamplingCreateMessageRequest:
    """采样创建消息请求"""

    messages: list[SamplingMessage]
    system_prompt: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    stop_sequences: list[str] | None = None
    include_context: str | None = None
    thinking: dict[str, Any] | None = None

    def __post_init__(self):
        if isinstance(self.messages, list) and len(self.messages) > 0:
            if not isinstance(self.messages[0], SamplingMessage):
                self.messages = [
                    SamplingMessage.from_dict(m) if isinstance(m, dict) else m
                    for m in self.messages
                ]

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        result = {
            "messages": [
                m.to_dict() if isinstance(m, SamplingMessage) else m for m in self.messages
            ],
        }
        if self.system_prompt:
            result["systemPrompt"] = self.system_prompt
        result["temperature"] = self.temperature
        result["maxTokens"] = self.max_tokens
        if self.stop_sequences:
            result["stopSequences"] = self.stop_sequences
        if self.include_context:
            result["includeContext"] = self.include_context
        if self.thinking:
            result["thinking"] = self.thinking
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SamplingCreateMessageRequest:
        """从字典创建"""
        messages = data.get("messages", [])
        parsed_messages = [
            SamplingMessage.from_dict(m) if isinstance(m, dict) else m for m in messages
        ]
        return cls(
            messages=parsed_messages,
            system_prompt=data.get("systemPrompt"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("maxTokens", 4096),
            stop_sequences=data.get("stopSequences"),
            include_context=data.get("includeContext"),
            thinking=data.get("thinking"),
        )


@dataclass
class SamplingResponse:
    """采样响应"""

    content: str
    model: str
    role: str = "assistant"
    done: bool = True
    done_reason: str | None = None
    usage: dict[str, int] | None = None
    thinking: str | None = None
    custom_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        result = {
            "content": self.content,
            "model": self.model,
            "role": self.role,
            "done": self.done,
        }
        if self.done_reason:
            result["doneReason"] = self.done_reason
        if self.usage:
            result["usage"] = self.usage
        if self.thinking:
            result["thinking"] = self.thinking
        if self.custom_id:
            result["customId"] = self.custom_id
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SamplingResponse:
        """从字典创建"""
        return cls(
            content=data.get("content", ""),
            model=data.get("model", ""),
            role=data.get("role", "assistant"),
            done=data.get("done", True),
            done_reason=data.get("doneReason"),
            usage=data.get("usage"),
            thinking=data.get("thinking"),
            custom_id=data.get("customId"),
            metadata=data.get("metadata", {}),
        )


class SamplingProvider:
    """采样提供者接口"""

    def sample(
        self,
        messages: list[SamplingMessage],
        parameters: SamplingParameters,
    ) -> SamplingResponse:
        """同步采样"""
        raise NotImplementedError

    async def sample_async(
        self,
        messages: list[SamplingMessage],
        parameters: SamplingParameters,
    ) -> SamplingResponse:
        """异步采样"""
        raise NotImplementedError


class SamplingManager:
    """
    采样管理器

    管理 LLM 采样请求，支持多种模型和采样策略。
    """

    def __init__(self):
        self._providers: dict[str, SamplingProvider] = {}
        self._default_model: str | None = None
        self._message_history: list[SamplingMessage] = []
        self._hooks: list[Callable[[str, Any], None]] = []

    def register_provider(
        self,
        model_name: str,
        provider: SamplingProvider,
    ) -> None:
        """注册采样提供者"""
        self._providers[model_name] = provider

    def set_default_model(self, model_name: str) -> None:
        """设置默认模型"""
        self._default_model = model_name

    def add_hook(self, hook: Callable[[str, Any], None]) -> None:
        """添加采样钩子"""
        self._hooks.append(hook)

    def remove_hook(self, hook: Callable[[str, Any], None]) -> None:
        """移除采样钩子"""
        if hook in self._hooks:
            self._hooks.remove(hook)

    def _notify_hooks(self, event: str, data: Any) -> None:
        """通知钩子"""
        for hook in self._hooks:
            try:
                hook(event, data)
            except Exception:
                pass

    def create_message(
        self,
        request: SamplingCreateMessageRequest,
    ) -> SamplingResponse:
        """
        创建采样消息（同步）

        Args:
            request: 采样请求

        Returns:
            采样响应
        """
        model = request.messages[0].content if request.messages else ""
        messages = list(request.messages)

        if request.system_prompt:
            messages.insert(
                0,
                SamplingMessage(
                    role=SamplingMessageRole.SYSTEM,
                    content=request.system_prompt,
                ),
            )

        parameters = SamplingParameters(
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop_sequences=request.stop_sequences,
            model=request.include_context or self._default_model,
            system_prompt=request.system_prompt,
            reasoning_effort=request.thinking.get("budget_tokens") if request.thinking else None,
        )

        self._notify_hooks(
            "before_sample",
            {
                "messages": messages,
                "parameters": parameters,
            },
        )

        provider = None
        if parameters.model and parameters.model in self._providers:
            provider = self._providers[parameters.model]
        elif self._default_model and self._default_model in self._providers:
            provider = self._providers[self._default_model]

        if provider:
            response = provider.sample(messages, parameters)
        else:
            response = self._default_sample(messages, parameters)

        self._message_history.extend(messages)
        self._message_history.append(
            SamplingMessage(
                role=SamplingMessageRole.ASSISTANT,
                content=response.content,
                metadata={"usage": response.usage} if response.usage else {},
            )
        )

        self._notify_hooks("after_sample", response)

        return response

    async def create_message_async(
        self,
        request: SamplingCreateMessageRequest,
    ) -> SamplingResponse:
        """
        创建采样消息（异步）

        Args:
            request: 采样请求

        Returns:
            采样响应
        """
        import asyncio

        model = request.messages[0].content if request.messages else ""
        messages = list(request.messages)

        if request.system_prompt:
            messages.insert(
                0,
                SamplingMessage(
                    role=SamplingMessageRole.SYSTEM,
                    content=request.system_prompt,
                ),
            )

        parameters = SamplingParameters(
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop_sequences=request.stop_sequences,
            model=request.include_context or self._default_model,
            system_prompt=request.system_prompt,
            reasoning_effort=request.thinking.get("budget_tokens") if request.thinking else None,
        )

        self._notify_hooks(
            "before_sample",
            {
                "messages": messages,
                "parameters": parameters,
            },
        )

        provider = None
        if parameters.model and parameters.model in self._providers:
            provider = self._providers[parameters.model]
        elif self._default_model and self._default_model in self._providers:
            provider = self._providers[self._default_model]

        if provider:
            response = await provider.sample_async(messages, parameters)
        else:
            response = await asyncio.to_thread(self._default_sample, messages, parameters)

        self._message_history.extend(messages)
        self._message_history.append(
            SamplingMessage(
                role=SamplingMessageRole.ASSISTANT,
                content=response.content,
                metadata={"usage": response.usage} if response.usage else {},
            )
        )

        self._notify_hooks("after_sample", response)

        return response

    def _default_sample(
        self,
        messages: list[SamplingMessage],
        parameters: SamplingParameters,
    ) -> SamplingResponse:
        """默认采样实现"""
        last_message = messages[-1].content if messages else ""
        return SamplingResponse(
            content=f"Echo: {last_message[:100]}",
            model=parameters.model or "default",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )

    def get_message_history(
        self,
        limit: int | None = None,
    ) -> list[SamplingMessage]:
        """获取消息历史"""
        if limit:
            return self._message_history[-limit:]
        return list(self._message_history)

    def clear_history(self) -> None:
        """清空消息历史"""
        self._message_history.clear()

    def get_stats(self) -> dict[str, Any]:
        """获取采样统计"""
        total_tokens = sum(
            m.metadata.get("usage", {}).get("total_tokens", 0)
            for m in self._message_history
            if m.role == SamplingMessageRole.ASSISTANT
        )
        return {
            "total_messages": len(self._message_history),
            "total_tokens": total_tokens,
            "registered_providers": list(self._providers.keys()),
            "default_model": self._default_model,
        }


class EmbeddedSamplingProvider(SamplingProvider):
    """嵌入式采样提供者"""

    def __init__(self, model_id: str):
        self.model_id = model_id

    def sample(
        self,
        messages: list[SamplingMessage],
        parameters: SamplingParameters,
    ) -> SamplingResponse:
        """执行采样"""
        content = self._generate_content(messages, parameters)
        return SamplingResponse(
            content=content,
            model=self.model_id,
            usage={
                "prompt_tokens": 10,
                "completion_tokens": len(content.split()),
                "total_tokens": 10 + len(content.split()),
            },
        )

    async def sample_async(
        self,
        messages: list[SamplingMessage],
        parameters: SamplingParameters,
    ) -> SamplingResponse:
        """异步执行采样"""
        return self.sample(messages, parameters)

    def _generate_content(
        self,
        messages: list[SamplingMessage],
        parameters: SamplingParameters,
    ) -> str:
        """生成内容"""
        last_message = messages[-1].content if messages else ""
        return f"[{self.model_id}] Processed: {last_message}"


def create_sampling_request(
    messages: list[dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: int = 4096,
    **kwargs: Any,
) -> SamplingCreateMessageRequest:
    """
    创建采样请求的便捷函数

    Args:
        messages: 消息列表
        temperature: 温度参数
        max_tokens: 最大令牌数
        **kwargs: 其他参数

    Returns:
        采样请求
    """
    parsed_messages = [SamplingMessage.from_dict(m) if isinstance(m, dict) else m for m in messages]
    return SamplingCreateMessageRequest(
        messages=parsed_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
