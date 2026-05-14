#!/usr/bin/env python3
"""
govmcp.models.adapters.doubao — 字节豆包适配器

支持 doubao-pro, doubao-lite
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, List, Optional

import requests

from govmcp.models.adapters.base import LLMAdapter
from govmcp.models.registry import ModelConfig


class DoubaoAdapter(LLMAdapter):
    """
    字节豆包大模型适配器

    Usage:
        config = ModelConfig(provider=LLMProvider.DOUBAO, model_id="doubao-pro", ...)
        adapter = DoubaoAdapter(config)
        response = adapter.chat([{"role": "user", "content": "你好"}])
    """

    def __init__(self, config: ModelConfig, api_key: str | None = None) -> None:
        super().__init__(config)
        self.api_key = api_key or ""

    def _build_headers(self) -> dict[str, str]:
        """构建请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

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
        if self.config.extra.get("model_name"):
            params["model"] = self.config.extra["model_name"]

        try:
            response = requests.post(
                self.api_base,
                headers=self._build_headers(),
                json=params,
                timeout=self.timeout,
            )
            result = response.json()

            if "error" in result:
                raise RuntimeError(f"字节豆包API错误: {result['error']}")

            return result.get("choices", [{}])[0].get("message", {}).get("content", "")

        except requests.RequestException as e:
            raise RuntimeError(f"字节豆包请求失败: {e}")

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
        if self.config.extra.get("model_name"):
            params["model"] = self.config.extra["model_name"]

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
            raise RuntimeError(f"字节豆包流式请求失败: {e}")

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

        embed_url = "https://ark.cn-beijing.volces.com/api/v3/embeddings"

        payload = {
            "model": "embedding-model",
            "input": text,
        }

        try:
            response = requests.post(
                embed_url,
                headers=self._build_headers(),
                json=payload,
                timeout=self.timeout,
            )
            result = response.json()
            return result.get("data", [{}])[0].get("embedding", [])

        except requests.RequestException as e:
            raise RuntimeError(f"字节豆包嵌入请求失败: {e}")
