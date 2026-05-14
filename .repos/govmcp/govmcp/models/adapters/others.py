#!/usr/bin/env python3
"""
govmcp.models.adapters.others — 其他厂商适配器

支持:
- sensechat-5, sensechat-4 (商汤日日新)
- qizhi-chat (360奇智)
- tuoshai-chat (拓世AI)
- wandao-chat (新华三望道)
- wenda-chat (出门问问)
- internlm-chat, internlm2-chat (书生·浦语)
- mindchat (聆心智能)
- ctyun-chat (天翼云)
- unicom-chat (联通AI)
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, List, Optional

import requests

from govmcp.models.adapters.base import LLMAdapter
from govmcp.models.registry import ModelConfig


class OthersAdapter(LLMAdapter):
    """
    其他国产大模型适配器

    统一处理商汤、360奇智、拓世AI、新华三望道、出门问问、书生·浦语、聆心智能、天翼云、联通AI等厂商。

    Usage:
        config = ModelConfig(provider=LLMProvider.SENSECHAT, model_id="sensechat-5", ...)
        adapter = OthersAdapter(config)
        response = adapter.chat([{"role": "user", "content": "你好"}])
    """

    def __init__(self, config: ModelConfig, api_key: str | None = None) -> None:
        super().__init__(config)
        self.api_key = api_key or ""

    def _build_headers(self) -> dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """
        发送对话请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            回复文本
        """
        params = self.build_request_params(messages, **kwargs)

        try:
            response = requests.post(
                self.api_base,
                headers=self._build_headers(),
                json=params,
                timeout=self.timeout,
            )
            result = response.json()

            if "error" in result:
                raise RuntimeError(f"API错误: {result['error']}")

            return result.get("choices", [{}])[0].get("message", {}).get("content", "")

        except requests.RequestException as e:
            raise RuntimeError(f"请求失败: {e}")

    def stream_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> Iterator[str]:
        """
        发送流式对话请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Yields:
            逐块返回的回复内容
        """
        params = self.build_request_params(messages, stream=True, **kwargs)

        try:
            response = requests.post(
                self.api_base,
                headers=self._build_headers(),
                json=params,
                stream=True,
                timeout=self.timeout,
            )

            for line in response.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            yield delta
                    except json.JSONDecodeError:
                        continue

        except requests.RequestException as e:
            raise RuntimeError(f"流式请求失败: {e}")

    def get_embedding(self, text: str, **kwargs: Any) -> list[float]:
        """
        获取文本嵌入向量

        Args:
            text: 待嵌入的文本
            **kwargs: 其他参数

        Returns:
            嵌入向量
        """
        if not self.config.supports_embedding():
            raise NotImplementedError("该模型不支持文本嵌入")

        raise NotImplementedError(f"{self.model_id} 嵌入功能需要使用专用API")
