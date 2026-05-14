#!/usr/bin/env python3
"""
govmcp.models.adapters.spark — 讯飞星火适配器

支持 spark-3.5, spark-4.0, spark-lite
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

import requests

from govmcp.models.adapters.base import LLMAdapter
from govmcp.models.registry import ModelConfig


class SparkAdapter(LLMAdapter):
    """
    讯飞星火大模型适配器

    Usage:
        config = ModelConfig(provider=LLMProvider.SPARK, model_id="spark-3.5", ...)
        adapter = SparkAdapter(config)
        response = adapter.chat([{"role": "user", "content": "你好"}])
    """

    def __init__(
        self,
        config: ModelConfig,
        app_id: str | None = None,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        super().__init__(config)
        self.app_id = app_id or ""
        self.api_key = api_key or ""
        self.api_secret = api_secret or ""

        self._version = "v3.5"
        if "4.0" in config.model_id:
            self._version = "v4.0"
        elif "lite" in config.model_id:
            self._version = "v3.1"

    def _generate_auth_url(self) -> str:
        """生成讯飞星火鉴权URL"""
        now = datetime.now(timezone.utc)
        date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        signature_origin = f"host: spark-api.xf-yun.com\ndate: {date}\nGET /v{self._version.replace('.', '')}/chat HTTP/1.1"

        signature_sha = hmac.new(
            self.api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature_sha.hex()}"'
        )

        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")

        params = {
            "authorization": authorization,
            "date": date,
            "host": "spark-api.xf-yun.com",
        }

        url = f"{self.api_base}?"
        for k, v in params.items():
            url += f"{k}={requests.utils.quote(v)}&"
        return url.rstrip("&")

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """
        发送对话请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            回复文本
        """
        payload = {
            "header": {
                "app_id": self.app_id,
            },
            "parameter": {
                "chat": {
                    "domain": f"generalv{self._version.replace('.', '.')}",
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                    "top_k": kwargs.get("top_k", 6),
                    "auditing": ["default"],
                }
            },
            "payload": {
                "message": {
                    "text": self._format_messages(messages),
                }
            },
        }

        try:
            response = requests.post(
                self._generate_auth_url(),
                json=payload,
                timeout=self.timeout,
            )
            result = response.json()

            if "header" in result and result["header"].get("code") != 0:
                raise RuntimeError(f"讯飞星火API错误: {result['header'].get('message', 'unknown')}")

            choices = result.get("payload", {}).get("choices", {}).get("text", [])
            return "".join(choice.get("content", "") for choice in choices)

        except requests.RequestException as e:
            raise RuntimeError(f"讯飞星火请求失败: {e}")

    def stream_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> Iterator[str]:
        """
        发送流式对话请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Yields:
            逐块返回的回复内容
        """
        payload = {
            "header": {
                "app_id": self.app_id,
            },
            "parameter": {
                "chat": {
                    "domain": f"generalv{self._version.replace('.', '')}",
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                    "top_k": kwargs.get("top_k", 6),
                    "streaming": True,
                    "auditing": ["default"],
                }
            },
            "payload": {
                "message": {
                    "text": self._format_messages(messages),
                }
            },
        }

        try:
            response = requests.post(
                self._generate_auth_url(),
                json=payload,
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
                        choices = chunk.get("payload", {}).get("choices", {}).get("text", [])
                        for choice in choices:
                            content = choice.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue

        except requests.RequestException as e:
            raise RuntimeError(f"讯飞星火流式请求失败: {e}")

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

        raise NotImplementedError("讯飞星火嵌入功能需要使用专用API")

    def _format_messages(self, messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        """格式化消息为讯飞格式"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                role = "assistant"
            elif role == "assistant":
                role = "user"
            formatted.append({"role": role, "content": msg.get("content", "")})
        return formatted
