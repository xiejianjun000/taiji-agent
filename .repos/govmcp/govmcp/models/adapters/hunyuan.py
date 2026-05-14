#!/usr/bin/env python3
"""
govmcp.models.adapters.hunyuan — 腾讯混元适配器

支持 hunyuan-lite, hunyuan-pro, hunyuan-standard
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, List, Optional

import requests

from govmcp.models.adapters.base import LLMAdapter
from govmcp.models.registry import ModelConfig


class HunyuanAdapter(LLMAdapter):
    """
    腾讯混元大模型适配器

    Usage:
        config = ModelConfig(provider=LLMProvider.HUNYUAN, model_id="hunyuan-pro", ...)
        adapter = HunyuanAdapter(config)
        response = adapter.chat([{"role": "user", "content": "你好"}])
    """

    def __init__(
        self, config: ModelConfig, secret_id: str | None = None, secret_key: str | None = None
    ) -> None:
        super().__init__(config)
        self.secret_id = secret_id or ""
        self.secret_key = secret_key or ""

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

        headers = {
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.api_base,
                headers=headers,
                json=params,
                timeout=self.timeout,
            )
            result = response.json()

            if "error" in result:
                raise RuntimeError(f"腾讯混元API错误: {result['error']}")

            return result.get("choices", [{}])[0].get("message", {}).get("content", "")

        except requests.RequestException as e:
            raise RuntimeError(f"腾讯混元请求失败: {e}")

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

        headers = {
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.api_base,
                headers=headers,
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
            raise RuntimeError(f"腾讯混元流式请求失败: {e}")

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

        embed_url = "https://hunyuan.cloud.tencent.com/embeddings"

        payload = {
            "model": "hunyuan-embedding",
            "input": text,
        }

        try:
            response = requests.post(
                embed_url,
                json=payload,
                timeout=self.timeout,
            )
            result = response.json()
            return result.get("data", [{}])[0].get("embedding", [])

        except requests.RequestException as e:
            raise RuntimeError(f"腾讯混元嵌入请求失败: {e}")
