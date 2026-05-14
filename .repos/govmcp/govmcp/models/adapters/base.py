#!/usr/bin/env python3
"""
govmcp.models.adapters.base — LLM适配器基类

定义统一的适配器接口，所有厂商适配器都应继承此类。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional

from govmcp.models.registry import ModelConfig


class LLMAdapter(ABC):
    """
    LLM适配器基类

    定义统一的接口规范，所有厂商适配器都应继承此类并实现：
    - chat(): 发送对话请求
    - stream_chat(): 流式对话请求
    - get_embedding(): 获取文本嵌入

    Usage:
        class MyAdapter(LLMAdapter):
            def chat(self, messages, **kwargs) -> str:
                # 实现chat逻辑
                pass

        adapter = MyAdapter(config)
        response = adapter.chat([{"role": "user", "content": "你好"}])
    """

    def __init__(self, config: ModelConfig) -> None:
        """
        初始化适配器

        Args:
            config: 模型配置
        """
        self.config = config
        self.model_id = config.model_id
        self.api_base = config.api_base
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        self.top_p = config.top_p
        self.timeout = config.timeout

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """
        发送对话请求

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}, ...]
            **kwargs: 其他参数 (temperature, max_tokens, top_p, stream 等)

        Returns:
            模型生成的回复文本
        """
        pass

    @abstractmethod
    def stream_chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> Iterator[str]:
        """
        发送流式对话请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Yields:
            逐块返回的回复内容
        """
        pass

    @abstractmethod
    def get_embedding(
        self,
        text: str,
        **kwargs: Any,
    ) -> list[float]:
        """
        获取文本嵌入向量

        Args:
            text: 待嵌入的文本
            **kwargs: 其他参数

        Returns:
            嵌入向量列表
        """
        pass

    def format_messages(
        self,
        system: str | None = None,
        user: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> list[dict[str, str]]:
        """
        格式化消息列表

        Args:
            system: 系统提示
            user: 用户消息
            history: 历史消息

        Returns:
            格式化的消息列表
        """
        result: list[dict[str, str]] = []

        if system:
            result.append({"role": "system", "content": system})

        if history:
            result.extend(history)

        if user:
            result.append({"role": "user", "content": user})

        return result

    def build_request_params(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        构建请求参数

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            请求参数字典
        """
        params: dict[str, Any] = {
            "model": self.model_id,
            "messages": messages,
        }

        if kwargs.get("temperature") is not None:
            params["temperature"] = kwargs["temperature"]
        else:
            params["temperature"] = self.temperature

        if kwargs.get("max_tokens") is not None:
            params["max_tokens"] = kwargs["max_tokens"]
        else:
            params["max_tokens"] = self.max_tokens

        if kwargs.get("top_p") is not None:
            params["top_p"] = kwargs["top_p"]
        else:
            params["top_p"] = self.top_p

        if kwargs.get("stream"):
            params["stream"] = True

        if kwargs.get("stop"):
            params["stop"] = kwargs["stop"]

        return params

    def supports_streaming(self) -> bool:
        """是否支持流式输出"""
        return self.config.supports_streaming()

    def supports_function_call(self) -> bool:
        """是否支持函数调用"""
        return self.config.supports_function_call()

    def supports_vision(self) -> bool:
        """是否支持视觉"""
        return self.config.supports_vision()

    def supports_embedding(self) -> bool:
        """是否支持文本嵌入"""
        return self.config.supports_embedding()
