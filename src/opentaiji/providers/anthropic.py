"""
Anthropic Provider
"""

import os
from collections.abc import AsyncGenerator
from typing import Any

from opentaiji.providers.base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    """Anthropic Claude Provider"""

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-4-20250514", **kwargs):
        super().__init__(api_key=api_key, model=model, **kwargs)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

    def _get_client(self):
        """获取客户端"""
        if self.client is None:
            try:
                from anthropic import AsyncAnthropic

                self.client = AsyncAnthropic(api_key=self.api_key)
            except ImportError as e:
                raise ImportError("anthropic package not installed: pip install anthropic") from e
        return self.client

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        **kwargs,
    ) -> LLMResponse:
        """发送聊天请求"""
        client = self._get_client()

        # 转换消息格式
        formatted_messages: list[dict[str, Any]] = []
        for msg in messages:
            if msg["role"] == "system":
                formatted_messages.insert(0, {"role": "user", "content": f"[System] {msg['content']}"})
            else:
                formatted_messages.append(msg)

        # 构建请求
        request_params = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            request_params["tools"] = tools

        try:
            response = await client.messages.create(**request_params)

            # 解析响应
            content_blocks = response.content

            text_content = None
            tool_calls = None

            for block in content_blocks:
                if block.type == "text":
                    text_content = block.text
                elif block.type == "tool_use":
                    if tool_calls is None:
                        tool_calls = []
                    tool_calls.append(
                        {
                            "name": block.name,
                            "arguments": block.input,
                            "id": block.id,
                        }
                    )

            return LLMResponse(
                content=text_content,
                tool_calls=tool_calls,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                model=self.model,
                raw=response,
            )
        except Exception as e:
            return LLMResponse(
                content=f"Error: {str(e)}",
                raw=response if "response" in locals() else None,
            )

    async def stream_chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        client = self._get_client()

        formatted_messages: list[dict[str, Any]] = []
        for msg in messages:
            if msg["role"] == "system":
                formatted_messages.insert(0, {"role": "user", "content": f"[System] {msg['content']}"})
            else:
                formatted_messages.append(msg)

        request_params: dict[str, Any] = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if tools:
            request_params["tools"] = tools

        async with client.messages.stream(**request_params) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        yield event.delta.text
                    elif hasattr(event.delta, "partial_json"):
                        yield event.delta.partial_json

    def estimate_tokens(self, text: str) -> int:
        """估算 token 数量 (粗略)"""
        return len(text) // 4
