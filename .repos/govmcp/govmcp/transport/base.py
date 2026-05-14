"""
govmcp.transport.base — 传输层抽象基类

定义 Transport 接口，所有传输方式（Stdio、WebSocket、HTTP）都需实现此接口。
"""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class TransportType(Enum):
    """传输类型枚举"""

    STDIO = "stdio"
    WEBSOCKET = "websocket"
    HTTP = "http"
    SSE = "sse"


@dataclass
class TransportConfig:
    """传输层配置"""

    transport_type: TransportType = TransportType.STDIO
    host: str = "127.0.0.1"
    port: int = 8080
    path: str = "/mcp"
    crypto_enabled: bool = False
    sm4_key: bytes | None = None
    auth_token: str | None = None
    heartbeat_interval: float = 30.0
    max_message_size: int = 10 * 1024 * 1024
    request_timeout: float = 60.0
    cors_enabled: bool = False
    cors_origins: list[str] = field(default_factory=lambda: ["*"])


@dataclass
class Message:
    """MCP 消息封装"""

    method: str
    params: dict[str, Any] = field(default_factory=dict)
    msg_id: str | None = None
    jsonrpc: str = "2.0"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Message:
        """从字典创建消息"""
        return cls(
            method=data.get("method", ""),
            params=data.get("params", {}),
            msg_id=data.get("id"),
            jsonrpc=data.get("jsonrpc", "2.0"),
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        result: dict[str, Any] = {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
        }
        if self.msg_id is not None:
            result["id"] = self.msg_id
        return result


@dataclass
class Response:
    """MCP 响应封装"""

    result: Any = None
    error: dict[str, Any] | None = None
    msg_id: str | None = None
    jsonrpc: str = "2.0"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Response:
        """从字典创建响应"""
        if "error" in data:
            return cls(
                error=data.get("error"),
                msg_id=data.get("id"),
                jsonrpc=data.get("jsonrpc", "2.0"),
            )
        return cls(
            result=data.get("result"),
            msg_id=data.get("id"),
            jsonrpc=data.get("jsonrpc", "2.0"),
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        result: dict[str, Any] = {"jsonrpc": self.jsonrpc}
        if self.msg_id is not None:
            result["id"] = self.msg_id
        if self.error is not None:
            result["error"] = self.error
        else:
            result["result"] = self.result
        return result


class TransportCallbacks(ABC):
    """传输层回调接口"""

    @abstractmethod
    def on_message(self, message: Message) -> None:
        """收到消息回调"""
        pass

    @abstractmethod
    def on_error(self, error: Exception) -> None:
        """错误回调"""
        pass

    @abstractmethod
    def on_disconnect(self) -> None:
        """断开连接回调"""
        pass

    def on_connect(self) -> None:
        """连接成功回调（可选）"""
        pass

    def on_heartbeat(self) -> None:
        """心跳回调（可选）"""
        pass


class Transport(ABC):
    """
    传输层抽象基类

    所有传输方式必须实现以下核心方法:
    - connect: 建立连接
    - disconnect: 断开连接
    - send: 发送消息
    - receive: 接收消息（通过回调）
    """

    def __init__(self, config: TransportConfig | None = None) -> None:
        self.config = config or TransportConfig()
        self._connected: bool = False
        self._callbacks: TransportCallbacks | None = None

    @property
    def connected(self) -> bool:
        """是否已连接"""
        return self._connected

    @property
    def transport_type(self) -> TransportType:
        """传输类型"""
        return self.config.transport_type

    def set_callbacks(self, callbacks: TransportCallbacks) -> None:
        """设置回调处理器"""
        self._callbacks = callbacks

    @abstractmethod
    async def connect(self) -> None:
        """建立连接"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接"""
        pass

    @abstractmethod
    async def send(self, message: Message) -> None:
        """发送消息"""
        pass

    @abstractmethod
    async def send_response(self, response: Response) -> None:
        """发送响应"""
        pass

    async def _safe_handle_message(self, data: dict[str, Any]) -> None:
        """安全处理收到的消息"""
        if self._callbacks is None:
            return

        try:
            if "result" in data or "error" in data:
                response = Response.from_dict(data)
                message = Message(method="_response", params={"response": response.to_dict()})
            else:
                message = Message.from_dict(data)

            self._callbacks.on_message(message)
        except Exception as e:
            self._callbacks.on_error(e)

    def _safe_callback_error(self, error: Exception) -> None:
        """安全调用错误回调"""
        if self._callbacks:
            try:
                self._callbacks.on_error(error)
            except Exception:
                pass


class StdioTransport(Transport):
    """
    Stdio 传输层实现

    通过标准输入/输出进行 JSON-RPC 通信。
    """

    def __init__(self, config: TransportConfig | None = None) -> None:
        super().__init__(config)
        self.config.transport_type = TransportType.STDIO
        self._reader_task: asyncio.Task | None = None
        self._reader_task_legacy: asyncio.Task | None = None

    async def connect(self) -> None:
        """建立 stdio 连接"""
        if self._connected:
            return

        self._connected = True
        if self._callbacks:
            self._callbacks.on_connect()

        loop = asyncio.get_event_loop()
        self._reader_task = loop.create_task(self._read_loop())

    async def disconnect(self) -> None:
        """断开 stdio 连接"""
        if not self._connected:
            return

        self._connected = False

        if self._reader_task:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
            self._reader_task = None

        if self._callbacks:
            self._callbacks.on_disconnect()

    async def send(self, message: Message) -> None:
        """通过 stdout 发送消息"""
        import sys

        output = json.dumps(message.to_dict(), ensure_ascii=False)
        sys.stdout.write(output + "\n")
        sys.stdout.flush()

    async def send_response(self, response: Response) -> None:
        """通过 stdout 发送响应"""
        import sys

        output = json.dumps(response.to_dict(), ensure_ascii=False)
        sys.stdout.write(output + "\n")
        sys.stdout.flush()

    async def _read_loop(self) -> None:
        """读取 stdin 的异步循环"""
        import sys

        loop = asyncio.get_event_loop()

        try:
            while self._connected:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    await self._safe_handle_message(data)
                except json.JSONDecodeError as e:
                    self._safe_callback_error(e)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._safe_callback_error(e)


class WebSocketTransportCallbacks(TransportCallbacks):
    """WebSocket 传输层回调"""

    def __init__(self, transport: WebSocketTransport) -> None:
        self.transport = transport

    def on_message(self, message: Message) -> None:
        if self.transport._callbacks:
            self.transport._callbacks.on_message(message)

    def on_error(self, error: Exception) -> None:
        if self.transport._callbacks:
            self.transport._callbacks.on_error(error)

    def on_disconnect(self) -> None:
        if self.transport._callbacks:
            self.transport._callbacks.on_disconnect()

    def on_connect(self) -> None:
        if self.transport._callbacks:
            self.transport._callbacks.on_connect()


class WebSocketTransport(Transport):
    """
    WebSocket 传输层实现

    支持加密传输和 SM3 消息完整性校验。
    """

    def __init__(self, config: TransportConfig | None = None) -> None:
        super().__init__(config)
        self.config.transport_type = TransportType.WEBSOCKET
        self._ws = None
        self._heartbeat_task: asyncio.Task | None = None

    @property
    def connected(self) -> bool:
        return self._connected and self._ws is not None

    async def connect(self) -> None:
        """建立 WebSocket 连接"""
        try:
            import websockets
        except ImportError:
            raise ImportError("websockets 库未安装。请运行: pip install websockets")

        if self._connected:
            return

        uri = f"ws://{self.config.host}:{self.config.port}{self.config.path}"

        headers = []
        if self.config.auth_token:
            headers.append(f"Bearer {self.config.auth_token}")

        try:
            self._ws = await websockets.connect(
                uri,
                extra_headers=headers if headers else None,
            )
            self._connected = True

            if self._callbacks:
                self._callbacks.on_connect()

            self._heartbeat_task = asyncio.get_event_loop().create_task(self._heartbeat_loop())

            asyncio.get_event_loop().create_task(self._receive_loop())

        except Exception as e:
            self._connected = False
            raise e

    async def disconnect(self) -> None:
        """断开 WebSocket 连接"""
        if not self._connected:
            return

        self._connected = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

        if self._ws:
            await self._ws.close()
            self._ws = None

        if self._callbacks:
            self._callbacks.on_disconnect()

    async def send(self, message: Message) -> None:
        """发送 WebSocket 消息"""
        if not self._ws:
            raise ConnectionError("WebSocket 未连接")

        from govmcp.crypto.sm import pkcs7_pad, sm3_hash, sm4_encrypt

        data = message.to_dict()
        payload = json.dumps(data, ensure_ascii=False)

        if self.config.crypto_enabled and self.config.sm4_key:
            payload_bytes = payload.encode("utf-8")
            padded = pkcs7_pad(payload_bytes)
            ciphertext = sm4_encrypt(padded, self.config.sm4_key)
            payload = base64.b64encode(ciphertext).decode("ascii")
            data = {"_encrypted": True, "data": payload}

        if self.config.crypto_enabled:
            payload_str = json.dumps(data, ensure_ascii=False)
            sm3_val = sm3_hash(payload_str.encode("utf-8"))
            data["_sm3"] = sm3_val

        output = json.dumps(data, ensure_ascii=False)
        await self._ws.send(output)

    async def send_response(self, response: Response) -> None:
        """发送 WebSocket 响应"""
        await self.send(Message(method="_response", params=response.to_dict()))

    async def _receive_loop(self) -> None:
        """接收 WebSocket 消息循环"""
        import base64

        try:
            async for msg in self._ws:  # type: ignore
                if not self._connected:
                    break

                try:
                    data = json.loads(msg)

                    if "_sm3" in data:
                        from govmcp.crypto.sm import sm3_hash

                        expected = data.pop("_sm3")
                        payload_str = json.dumps(
                            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                        )
                        actual = sm3_hash(payload_str.encode("utf-8"))
                        if actual != expected:
                            continue

                    if "_encrypted" in data and self.config.crypto_enabled and self.config.sm4_key:
                        ciphertext = base64.b64decode(data["data"])
                        from govmcp.crypto.sm import pkcs7_unpad, sm4_decrypt

                        plaintext = pkcs7_unpad(sm4_decrypt(ciphertext, self.config.sm4_key))
                        data = json.loads(plaintext.decode("utf-8"))

                    await self._safe_handle_message(data)

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    self._safe_callback_error(e)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._safe_callback_error(e)

    async def _heartbeat_loop(self) -> None:
        """心跳循环"""
        import asyncio

        try:
            while self._connected:
                await asyncio.sleep(self.config.heartbeat_interval)
                if self._connected and self._ws:
                    try:
                        pong_waiter = await self._ws.ping()
                        await asyncio.wait_for(pong_waiter, timeout=10.0)
                    except Exception:
                        break
        except asyncio.CancelledError:
            pass


class HTTPTransport(Transport):
    """
    HTTP/SSE 传输层实现

    支持 Streamable HTTP 和 Server-Sent Events。
    """

    def __init__(self, config: TransportConfig | None = None) -> None:
        super().__init__(config)
        self.config.transport_type = TransportType.HTTP
        self._session = None
        self._server_task: asyncio.Task | None = None

    async def connect(self) -> None:
        """建立 HTTP 连接"""
        try:
            import aiohttp
        except ImportError:
            raise ImportError("aiohttp 库未安装。请运行: pip install aiohttp")

        if self._connected:
            return

        self._session = aiohttp.ClientSession()
        self._connected = True

        if self._callbacks:
            self._callbacks.on_connect()

    async def disconnect(self) -> None:
        """断开 HTTP 连接"""
        if not self._connected:
            return

        self._connected = False

        if self._session:
            await self._session.close()
            self._session = None

        if self._callbacks:
            self._callbacks.on_disconnect()

    async def send(self, message: Message) -> None:
        """发送 HTTP POST 请求"""
        if not self._session:
            raise ConnectionError("HTTP 会话未初始化")

        from govmcp.crypto.sm import pkcs7_pad, sm3_hash, sm4_encrypt

        data = message.to_dict()
        payload = json.dumps(data, ensure_ascii=False)

        headers = {"Content-Type": "application/json"}

        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"

        if self.config.crypto_enabled and self.config.sm4_key:
            import base64

            payload_bytes = payload.encode("utf-8")
            padded = pkcs7_pad(payload_bytes)
            ciphertext = sm4_encrypt(padded, self.config.sm4_key)
            payload = base64.b64encode(ciphertext).decode("ascii")
            data = {"_encrypted": True, "data": payload}
            headers["X-Encrypted"] = "true"

        if self.config.crypto_enabled:
            sm3_val = sm3_hash(payload.encode("utf-8"))
            headers["X-SM3-Hash"] = sm3_val

        url = f"http://{self.config.host}:{self.config.port}{self.config.path}"

        try:
            async with self._session.post(
                url,
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.request_timeout),
            ) as response:
                result = await response.json()
                await self._safe_handle_message(result)
        except Exception as e:
            self._safe_callback_error(e)

    async def send_response(self, response: Response) -> None:
        """HTTP 响应直接返回（由服务器端处理）"""
        pass

    async def get_sse_stream(self) -> Any:
        """获取 SSE 流"""
        if not self._session:
            raise ConnectionError("HTTP 会话未初始化")

        url = f"http://{self.config.host}:{self.config.port}{self.config.path}/sse"

        headers = {}
        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"

        async with self._session.get(
            url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=None),
        ) as response:
            async for line in response.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    await self._safe_handle_message(data)
