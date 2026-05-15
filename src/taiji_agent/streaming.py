"""
流式响应处理模块

提供：
- WebSocket 流式响应
- Server-Sent Events (SSE)
- 流式事件处理
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

import aiohttp
from aiohttp import web

logger = logging.getLogger(__name__)


class StreamType(str, Enum):
    """流类型"""
    WEBSOCKET = "websocket"
    SSE = "sse"
    CHUNKED = "chunked"


class StreamState(str, Enum):
    """流状态"""
    CONNECTING = "connecting"
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"


@dataclass
class StreamMessage:
    """流消息"""
    message_id: str
    stream_id: str
    message_type: str
    content: str | dict = ""
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


@dataclass
class StreamConfig:
    """流配置"""
    stream_type: StreamType = StreamType.WEBSOCKET
    chunk_size: int = 64
    buffer_size: int = 100
    timeout: float = 60.0
    heartbeat_interval: float = 30.0


class StreamHandler(ABC):
    """流处理器基类"""

    @abstractmethod
    async def on_connect(self, stream_id: str) -> bool:
        """连接建立"""
        pass

    @abstractmethod
    async def on_message(self, stream_id: str, message: StreamMessage):
        """收到消息"""
        pass

    @abstractmethod
    async def on_disconnect(self, stream_id: str):
        """连接断开"""
        pass

    @abstractmethod
    async def send(self, stream_id: str, message: StreamMessage) -> bool:
        """发送消息"""
        pass


class StreamingResponse:
    """
    流式响应处理器

    处理 LLM 流式响应，支持：
    - 分块发送
    - 心跳检测
    - 错误恢复
    """

    def __init__(
        self,
        stream_id: str,
        handler: StreamHandler | None = None,
        config: StreamConfig | None = None,
    ):
        self.stream_id = stream_id
        self.handler = handler
        self.config = config or StreamConfig()
        self.state = StreamState.CONNECTING

        self._buffer: list[StreamMessage] = []
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=self.config.buffer_size)
        self._closed = False
        self._tasks: list[asyncio.Task] = []

    async def start(self):
        """启动流"""
        self.state = StreamState.OPEN

        if self.handler:
            await self.handler.on_connect(self.stream_id)

        self._tasks.append(asyncio.create_task(self._process_queue()))
        self._tasks.append(asyncio.create_task(self._heartbeat()))

        logger.info(f"StreamingResponse started: {self.stream_id}")

    async def stop(self):
        """停止流"""
        self.state = StreamState.CLOSING
        self._closed = True

        for task in self._tasks:
            task.cancel()

        if self.handler:
            await self.handler.on_disconnect(self.stream_id)

        self.state = StreamState.CLOSED
        logger.info(f"StreamingResponse stopped: {self.stream_id}")

    async def send_chunk(self, content: str, metadata: dict | None = None):
        """发送数据块"""
        if self._closed:
            return

        message = StreamMessage(
            message_id=str(uuid.uuid4()),
            stream_id=self.stream_id,
            message_type="chunk",
            content=content,
            metadata=metadata or {},
        )

        await self._queue.put(message)

    async def send_done(self, metadata: dict | None = None):
        """发送完成信号"""
        message = StreamMessage(
            message_id=str(uuid.uuid4()),
            stream_id=self.stream_id,
            message_type="done",
            content="",
            metadata=metadata or {},
        )

        await self._queue.put(message)
        await self.stop()

    async def send_error(self, error: str, metadata: dict | None = None):
        """发送错误"""
        message = StreamMessage(
            message_id=str(uuid.uuid4()),
            stream_id=self.stream_id,
            message_type="error",
            content=error,
            metadata=metadata or {},
        )

        await self._queue.put(message)
        await self.stop()

    async def _process_queue(self):
        """处理消息队列"""
        while not self._closed:
            try:
                message = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=self.config.timeout,
                )

                if self.handler:
                    await self.handler.send(self.stream_id, message)

                self._buffer.append(message)

                if len(self._buffer) > self.config.buffer_size:
                    self._buffer.pop(0)

            except asyncio.TimeoutError:
                logger.warning(f"Stream timeout: {self.stream_id}")
                break
            except Exception as e:
                logger.error(f"Stream processing error: {e}")
                await self.send_error(str(e))
                break

    async def _heartbeat(self):
        """心跳检测"""
        while not self._closed:
            await asyncio.sleep(self.config.heartbeat_interval)

            if not self._closed:
                heartbeat = StreamMessage(
                    message_id=str(uuid.uuid4()),
                    stream_id=self.stream_id,
                    message_type="heartbeat",
                    content="ping",
                )

                try:
                    if self.handler:
                        await self.handler.send(self.stream_id, heartbeat)
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
                    break

    def get_buffer(self) -> list[StreamMessage]:
        """获取缓冲区"""
        return self._buffer.copy()


class WebSocketHandler(StreamHandler):
    """WebSocket 流处理器"""

    def __init__(self):
        self._websockets: dict[str, Any] = {}

    async def on_connect(self, stream_id: str, ws: Any = None) -> bool:
        """连接建立"""
        self._websockets[stream_id] = ws
        logger.info(f"WebSocket connected: {stream_id}")
        return True

    async def on_message(self, stream_id: str, message: StreamMessage):
        """收到消息"""
        pass

    async def on_disconnect(self, stream_id: str):
        """连接断开"""
        self._websockets.pop(stream_id, None)
        logger.info(f"WebSocket disconnected: {stream_id}")

    async def send(self, stream_id: str, message: StreamMessage) -> bool:
        """发送消息"""
        ws = self._websockets.get(stream_id)
        if not ws:
            return False

        try:
            data = {
                "message_id": message.message_id,
                "type": message.message_type,
                "content": message.content,
                "timestamp": message.timestamp,
            }

            await ws.send_json(data)
            return True

        except Exception as e:
            logger.error(f"WebSocket send error: {e}")
            return False


class SSEHandler(StreamHandler):
    """Server-Sent Events 流处理器"""

    def __init__(self):
        self._responses: dict[str, asyncio.Queue] = {}

    async def on_connect(self, stream_id: str) -> bool:
        """连接建立"""
        self._responses[stream_id] = asyncio.Queue()
        logger.info(f"SSE connected: {stream_id}")
        return True

    async def on_message(self, stream_id: str, message: StreamMessage):
        """收到消息"""
        queue = self._responses.get(stream_id)
        if queue:
            await queue.put(message)

    async def on_disconnect(self, stream_id: str):
        """连接断开"""
        self._responses.pop(stream_id, None)
        logger.info(f"SSE disconnected: {stream_id}")

    async def send(self, stream_id: str, message: StreamMessage) -> bool:
        """发送消息（模拟）"""
        return True

    async def stream_events(self, stream_id: str) -> AsyncGenerator[str, None]:
        """生成 SSE 事件流"""
        queue = self._responses.get(stream_id)

        if not queue:
            return

        while True:
            try:
                message = await asyncio.wait_for(queue.get(), timeout=30)

                if message.message_type == "heartbeat":
                    yield f"event: heartbeat\ndata: ping\n\n"
                elif message.message_type == "error":
                    yield f"event: error\ndata: {message.content}\n\n"
                elif message.message_type == "done":
                    yield f"event: done\ndata: complete\n\n"
                    break
                else:
                    yield f"data: {json.dumps({'content': message.content})}\n\n"

            except asyncio.TimeoutError:
                yield f": heartbeat\n\n"


class LLMStreamAdapter:
    """
    LLM 流式响应适配器

    将不同 LLM 提供商的流式响应转换为统一格式
    """

    def __init__(self):
        self._handlers: dict[str, Callable] = {}

    def register_handler(self, provider: str, handler: Callable):
        """注册处理器"""
        self._handlers[provider] = handler

    async def stream_openai(
        self,
        response: Any,
        stream: StreamingResponse,
    ):
        """OpenAI 流式响应处理"""
        try:
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    await stream.send_chunk(content)

            await stream.send_done()

        except Exception as e:
            await stream.send_error(str(e))

    async def stream_anthropic(
        self,
        response: Any,
        stream: StreamingResponse,
    ):
        """Anthropic 流式响应处理"""
        try:
            async for event in response:
                if hasattr(event, "completion") and event.completion:
                    content = event.completion
                    await stream.send_chunk(content)

            await stream.send_done()

        except Exception as e:
            await stream.send_error(str(e))

    async def stream_generic(
        self,
        generator: AsyncGenerator[str, None],
        stream: StreamingResponse,
    ):
        """通用流式响应处理"""
        try:
            async for chunk in generator:
                await stream.send_chunk(chunk)

            await stream.send_done()

        except Exception as e:
            await stream.send_error(str(e))


class StreamManager:
    """
    流管理器

    管理多个流式连接
    """

    def __init__(self):
        self._streams: dict[str, StreamingResponse] = {}
        self._ws_handler = WebSocketHandler()
        self._sse_handler = SSEHandler()
        self._adapter = LLMStreamAdapter()

    async def create_stream(
        self,
        stream_id: str | None = None,
        stream_type: StreamType = StreamType.WEBSOCKET,
        config: StreamConfig | None = None,
    ) -> StreamingResponse:
        """创建流"""
        stream_id = stream_id or str(uuid.uuid4())

        stream = StreamingResponse(
            stream_id=stream_id,
            handler=self._ws_handler if stream_type == StreamType.WEBSOCKET else self._sse_handler,
            config=config,
        )

        self._streams[stream_id] = stream
        await stream.start()

        return stream

    async def get_stream(self, stream_id: str) -> StreamingResponse | None:
        """获取流"""
        return self._streams.get(stream_id)

    async def close_stream(self, stream_id: str):
        """关闭流"""
        stream = self._streams.get(stream_id)
        if stream:
            await stream.stop()
            del self._streams[stream_id]

    async def close_all(self):
        """关闭所有流"""
        for stream_id in list(self._streams.keys()):
            await self.close_stream(stream_id)

    def get_stats(self) -> dict:
        """获取统计"""
        return {
            "active_streams": len(self._streams),
            "streams": {
                sid: {"state": s.state.value, "buffer_size": len(s._buffer)}
                for sid, s in self._streams.items()
            },
        }


_global_stream_manager = StreamManager()


def get_stream_manager() -> StreamManager:
    """获取全局流管理器"""
    return _global_stream_manager
