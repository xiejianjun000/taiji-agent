#!/usr/bin/env python3
"""
govmcp.models.adapters.wenxin — 百度文心一言适配器

支持 ernie-4.0, ernie-3.5, ernie-3.0, ernie-bot
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterator, List, Optional

import requests

from govmcp.models.adapters.base import LLMAdapter
from govmcp.models.registry import ModelConfig


class WenxinAdapter(LLMAdapter):
    """
    百度文心一言适配器

    Usage:
        config = ModelConfig(provider=LLMProvider.WENXIN, model_id="ernie-4.0", ...)
        adapter = WenxinAdapter(config)
        response = adapter.chat([{"role": "user", "content": "你好"}])
    """

    def __init__(
        self, config: ModelConfig, api_key: str | None = None, secret_key: str | None = None
    ) -> None:
        super().__init__(config)
        self.api_key = api_key or ""
        self.secret_key = secret_key or ""
        self._access_token: str | None = None
        self._token_expires_at: float = 0

    def _get_access_token(self) -> str:
        """获取百度access_token"""
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key,
        }
        response = requests.post(token_url, params=params, timeout=10)
        data = response.json()
        self._access_token = data.get("access_token", "")
        self._token_expires_at = time.time() + data.get("expires_in", 3600) - 60
        return self._access_token

    def _build_headers(self) -> dict[str, str]:
        """构建请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_access_token()}",
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

        url = f"{self.api_base}?access_token={self._get_access_token()}"

        try:
            response = requests.post(
                url,
                headers=self._build_headers(),
                json=params,
                timeout=self.timeout,
            )
            result = response.json()

            if "error_code" in result:
                raise RuntimeError(f"文心一言API错误: {result.get('error_msg', result)}")

            return result.get("choices", [{}])[0].get("message", {}).get("content", "")

        except requests.RequestException as e:
            raise RuntimeError(f"文心一言请求失败: {e}")

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
        url = f"{self.api_base}?access_token={self._get_access_token()}"

        try:
            response = requests.post(
                url,
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
            raise RuntimeError(f"文心一言流式请求失败: {e}")

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

        embed_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings"
        params = {
            "access_token": self._get_access_token(),
        }

        payload = {
            "input": text,
            "model": "ernie-text-embedding",
        }

        try:
            response = requests.post(
                embed_url,
                headers=self._build_headers(),
                json=payload,
                params=params,
                timeout=self.timeout,
            )
            result = response.json()
            return result.get("data", [{}])[0].get("embedding", [])

        except requests.RequestException as e:
            raise RuntimeError(f"文心一言嵌入请求失败: {e}")
