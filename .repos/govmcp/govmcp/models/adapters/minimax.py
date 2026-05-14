#!/usr/bin/env python3
"""
govmcp.models.adapters.minimax — MiniMax适配器

支持 minimax-abab5, minimax-abab6, minimax-chat
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, List, Optional

import requests

from govmcp.models.adapters.base import LLMAdapter
from govmcp.models.registry import ModelConfig


class MinimaxAdapter(LLMAdapter):
    """
    MiniMax大模型适配器

    Usage:
        config = ModelConfig(provider=LLMProvider.MINIMAX, model_id="minimax-abab6", ...)
        adapter = MinimaxAdapter(config)
        response = adapter.chat([{"role": "user", "content": "你好"}])
    """

    def __init__(
        self, config: ModelConfig, api_key: str | None = None, group_id: str | None = None
    ) -> None:
        super().__init__(config)
        self.api_key = api_key or ""
        self.group_id = group_id or ""

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
        params["model"] = self.model_id
        params["group_id"] = self.group_id

        try:
            response = requests.post(
                self.api_base,
                headers=self._build_headers(),
                json=params,
                timeout=self.timeout,
            )
            result = response.json()

            if "base_resp" in result and result["base_resp"].get("status_code") != 0:
                raise RuntimeError(
                    f"MiniMax API错误: {result['base_resp'].get('status_message', 'unknown')}"
                )

            return result.get("choices", [{}])[0].get("messages", [{}])[0].get("text", "")

        except requests.RequestException as e:
            raise RuntimeError(f"MiniMax请求失败: {e}")

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
        params["model"] = self.model_id
        params["group_id"] = self.group_id

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
                        choices = chunk.get("choices", [{}])
                        if choices:
                            messages_list = choices[0].get("messages", [])
                            for msg in messages_list:
                                text = msg.get("text", "")
                                if text:
                                    yield text
                    except json.JSONDecodeError:
                        continue

        except requests.RequestException as e:
            raise RuntimeError(f"MiniMax流式请求失败: {e}")

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

        embed_url = "https://api.minimax.chat/v1/text/embeddings"

        payload = {
            "model": "embo-01",
            "texts": [text],
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
            raise RuntimeError(f"MiniMax嵌入请求失败: {e}")
