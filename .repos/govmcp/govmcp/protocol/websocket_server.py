"""
govmcp.protocol.websocket_server — WebSocket 传输层服务器

基于 websockets 库实现 MCP WebSocket 服务器，支持:
- 标准 MCP JSON-RPC 消息格式
- SM4-CBC 加密传输（可选）
- SM3 消息完整性校验
- Token 认证
- 多客户端连接管理
- 心跳检测
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

try:
    import websockets
    from websockets.server import WebSocketServerProtocol, serve

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    websockets = None

from govmcp.crypto.sm import (
    generate_sm4_iv,
    generate_sm4_key,
    pkcs7_pad,
    pkcs7_unpad,
    sm3_hash,
    sm4_cbc_decrypt,
    sm4_cbc_encrypt,
)

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """连接状态"""

    CONNECTING = "connecting"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    CLOSED = "closed"


@dataclass
class ClientConnection:
    """客户端连接信息"""

    client_id: str
    websocket: Any
    state: ConnectionState = ConnectionState.CONNECTING
    auth_token: str | None = None
    authenticated_at: datetime | None = None
    last_heartbeat: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    remote_addr: str | None = None
    headers: dict[str, str] = field(default_factory=dict)


class WebSocketServer:
    """
    WebSocket MCP 服务器

    提供高性能的 WebSocket 传输层，支持国密加密和认证。

    用法:
        async def handler(server, client_id, message):
            return await server.handle_message(client_id, message)

        server = WebSocketServer(
            host="0.0.0.0",
            port=8080,
            auth_token="secret-token",
            crypto_enabled=True,
        )
        await server.start(handler)
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        path: str = "/mcp",
        auth_token: str | None = None,
        crypto_enabled: bool = False,
        sm4_key: bytes | None = None,
        heartbeat_interval: float = 30.0,
        heartbeat_timeout: float = 60.0,
        max_message_size: int = 10 * 1024 * 1024,
        enable_cors: bool = False,
        cors_origins: list[str] | None = None,
        log_level: int = logging.INFO,
    ) -> None:
        """
        初始化 WebSocket 服务器。

        Args:
            host: 绑定主机地址
            port: 绑定端口
            path: WebSocket 路径
            auth_token: 认证 Token（可选）
            crypto_enabled: 是否启用 SM4-CBC 加密
            sm4_key: SM4 密钥（16字节），为 None 时自动生成
            heartbeat_interval: 心跳间隔（秒）
            heartbeat_timeout: 心跳超时（秒）
            max_message_size: 最大消息大小（字节）
            enable_cors: 是否启用 CORS
            cors_origins: CORS 允许的来源列表
            log_level: 日志级别
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets 库未安装。请运行: pip install websockets")

        self.host = host
        self.port = port
        self.path = path
        self.auth_token = auth_token
        self.crypto_enabled = crypto_enabled
        self.sm4_key: bytes = sm4_key if sm4_key else generate_sm4_key()
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.max_message_size = max_message_size
        self.enable_cors = enable_cors
        self.cors_origins = cors_origins or ["*"]

        self._handler: Callable[..., Any] | None = None
        self._clients: dict[str, ClientConnection] = {}
        self._client_lock = asyncio.Lock()
        self._running = False
        self._server = None
        self._heartbeat_task: asyncio.Task | None = None

        logging.basicConfig(level=log_level)
        self._logger = logging.getLogger(__name__)

    def set_message_handler(self, handler: Callable[[str, dict[str, Any]], Any]) -> None:
        """
        设置消息处理器。

        Args:
            handler: 异步函数，接收 (client_id, message) 并返回响应
        """
        self._handler = handler

    async def start(self, handler: Callable[[str, dict[str, Any]], Any] | None = None) -> None:
        """
        启动 WebSocket 服务器。

        Args:
            handler: 消息处理器（可选）
        """
        if handler:
            self._handler = handler

        if not self._handler:
            raise ValueError("必须设置消息处理器")

        self._running = True
        self._server = await serve(
            self._handle_client,
            self.host,
            self.port,
            max_size=self.max_message_size,
            ping_interval=self.heartbeat_interval,
            ping_timeout=self.heartbeat_timeout,
        )

        self._heartbeat_task = asyncio.create_task(self._heartbeat_check())

        addr = self._server.sockets[0].getsockname()
        self._logger.info(f"WebSocket 服务器已启动: ws://{addr[0]}:{addr[1]}{self.path}")

    async def stop(self) -> None:
        """停止 WebSocket 服务器"""
        self._running = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        async with self._client_lock:
            for client in self._clients.values():
                try:
                    await client.websocket.close()
                except Exception:
                    pass
            self._clients.clear()

        if self._server:
            self._server.close()
            await self._server.wait_closed()

        self._logger.info("WebSocket 服务器已停止")

    async def broadcast(self, message: dict[str, Any]) -> int:
        """
        广播消息给所有已连接的客户端。

        Args:
            message: 要广播的消息

        Returns:
            发送到的客户端数量
        """
        count = 0
        async with self._client_lock:
            for client in self._clients.values():
                if client.state == ConnectionState.AUTHENTICATED:
                    try:
                        await self._send_message(client, message)
                        count += 1
                    except Exception as e:
                        self._logger.warning(f"广播失败: {e}")
        return count

    def get_client_count(self) -> int:
        """获取当前连接数"""
        return len(self._clients)

    def get_authenticated_count(self) -> int:
        """获取已认证连接数"""
        return sum(1 for c in self._clients.values() if c.state == ConnectionState.AUTHENTICATED)

    async def disconnect_client(self, client_id: str) -> bool:
        """
        断开指定客户端。

        Args:
            client_id: 客户端 ID

        Returns:
            是否成功断开
        """
        async with self._client_lock:
            client = self._clients.get(client_id)
            if client:
                try:
                    await client.websocket.close()
                except Exception:
                    pass
                del self._clients[client_id]
                return True
        return False

    async def _handle_client(
        self,
        websocket: WebSocketServerProtocol,
        path: str,
    ) -> None:
        """处理客户端连接"""
        client_id = str(uuid.uuid4())
        remote_addr = websocket.remote_address[0] if websocket.remote_address else "unknown"

        headers = {}
        if hasattr(websocket, "request_headers"):
            for name, value in websocket.request_headers.items():
                headers[name.lower().decode()] = (
                    value.decode() if isinstance(name, bytes) else str(name)
                )
                headers[value.lower().decode()] = (
                    value.decode() if isinstance(value, bytes) else str(value)
                )

        client = ClientConnection(
            client_id=client_id,
            websocket=websocket,
            remote_addr=remote_addr,
            headers=headers,
        )

        async with self._client_lock:
            self._clients[client_id] = client

        self._logger.info(f"客户端连接: {client_id} ({remote_addr})")

        try:
            if self.auth_token:
                client.state = ConnectionState.AUTHENTICATING
                await self._authenticate_client(client)
            else:
                client.state = ConnectionState.AUTHENTICATED
                client.authenticated_at = datetime.now()

            if client.state != ConnectionState.AUTHENTICATED:
                return

            await self._message_loop(client)

        except websockets.exceptions.ConnectionClosed:
            self._logger.info(f"客户端断开: {client_id}")
        except Exception as e:
            self._logger.error(f"客户端错误 {client_id}: {e}")
        finally:
            async with self._client_lock:
                if client_id in self._clients:
                    del self._clients[client_id]
            self._logger.info(f"客户端清理: {client_id} (共 {len(self._clients)} 个连接)")

    async def _authenticate_client(self, client: ClientConnection) -> bool:
        """认证客户端"""
        try:
            auth_message = await asyncio.wait_for(client.websocket.recv(), timeout=10.0)

            try:
                data = json.loads(auth_message)
            except json.JSONDecodeError:
                if self.crypto_enabled:
                    try:
                        ciphertext = base64.b64decode(auth_message)
                        plaintext = pkcs7_unpad(
                            sm4_cbc_decrypt(ciphertext, self.sm4_key, self.sm4_key)
                        )
                        data = json.loads(plaintext.decode("utf-8"))
                    except Exception:
                        return False
                else:
                    return False

            token = (
                data.get("token")
                or data.get("auth_token")
                or data.get("Authorization", "").replace("Bearer ", "")
            )
            if token == self.auth_token:
                client.state = ConnectionState.AUTHENTICATED
                client.authenticated_at = datetime.now()
                client.auth_token = token
                self._logger.info(f"客户端认证成功: {client.client_id}")
                await self._send_message(
                    client,
                    {"jsonrpc": "2.0", "id": data.get("id"), "result": {"authenticated": True}},
                )
                return True
            else:
                await self._send_message(
                    client,
                    {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "error": {"code": -32001, "message": "认证失败"},
                    },
                )
                return False

        except asyncio.TimeoutError:
            self._logger.warning(f"认证超时: {client.client_id}")
            return False
        except Exception as e:
            self._logger.error(f"认证错误: {e}")
            return False

    async def _message_loop(self, client: ClientConnection) -> None:
        """消息循环"""
        async for message in client.websocket:
            if not self._running:
                break

            client.last_heartbeat = datetime.now()

            try:
                data = await self._decrypt_and_parse(message, client)
                if data is None:
                    continue

                self._validate_sm3(data, client)

                response = await self._handler(client.client_id, data)

                if response is not None:
                    await self._send_message(client, response)

                client.message_count += 1

            except json.JSONDecodeError as e:
                self._logger.warning(f"JSON 解析错误 {client.client_id}: {e}")
                await self._send_message(
                    client,
                    {"jsonrpc": "2.0", "error": {"code": -32700, "message": f"Parse error: {e}"}},
                )
            except Exception as e:
                self._logger.error(f"消息处理错误 {client.client_id}: {e}")
                await self._send_message(
                    client,
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": f"Internal error: {e}"},
                    },
                )

    async def _decrypt_and_parse(
        self, message: str, client: ClientConnection
    ) -> dict[str, Any] | None:
        """解密并解析消息"""
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            if self.crypto_enabled:
                try:
                    ciphertext = base64.b64decode(message)
                    iv = self.sm4_key
                    plaintext = pkcs7_unpad(sm4_cbc_decrypt(ciphertext, self.sm4_key, iv))
                    data = json.loads(plaintext.decode("utf-8"))
                except Exception:
                    return None
            else:
                return None

        if "_encrypted" in data and self.crypto_enabled:
            try:
                ciphertext = base64.b64decode(data.get("data", ""))
                iv = self.sm4_key
                plaintext = pkcs7_unpad(sm4_cbc_decrypt(ciphertext, self.sm4_key, iv))
                data = json.loads(plaintext.decode("utf-8"))
            except Exception:
                return None

        return data

    def _validate_sm3(self, data: dict[str, Any], client: ClientConnection) -> bool:
        """验证 SM3 完整性"""
        if "_sm3" not in data:
            return True

        expected = data.pop("_sm3")
        payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        actual = sm3_hash(payload.encode("utf-8"))

        if actual != expected:
            self._logger.warning(
                f"SM3 校验失败 {client.client_id}: expected={expected}, actual={actual}"
            )
            return False
        return True

    async def _send_message(self, client: ClientConnection, message: dict[str, Any]) -> None:
        """发送消息（带加密和 SM3）"""
        data = message.copy()

        payload = json.dumps(data, ensure_ascii=False)

        if self.crypto_enabled:
            iv = generate_sm4_iv()
            ciphertext = sm4_cbc_encrypt(payload.encode("utf-8"), self.sm4_key, iv)
            data = {
                "_encrypted": True,
                "iv": base64.b64encode(iv).decode("ascii"),
                "data": base64.b64encode(ciphertext).decode("ascii"),
            }
            payload = json.dumps(data, ensure_ascii=False)

        sm3_val = sm3_hash(payload.encode("utf-8"))
        data["_sm3"] = sm3_val

        output = json.dumps(data, ensure_ascii=False)
        await client.websocket.send(output)

    async def _heartbeat_check(self) -> None:
        """心跳检查"""
        while self._running:
            try:
                await asyncio.sleep(10.0)

                now = datetime.now()
                timeout_threshold = now.timestamp() - self.heartbeat_timeout

                async with self._client_lock:
                    expired = []
                    for client_id, client in self._clients.items():
                        if client.last_heartbeat.timestamp() < timeout_threshold:
                            expired.append(client_id)

                    for client_id in expired:
                        self._logger.warning(f"心跳超时，断开: {client_id}")
                        try:
                            await self._clients[client_id].websocket.close()
                        except Exception:
                            pass
                        del self._clients[client_id]

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"心跳检查错误: {e}")

    async def handle_message(
        self, client_id: str, message: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        默认消息处理器（需要外部设置实际的处理器）。

        此方法可被子类重写或通过 set_message_handler 替换。
        """
        return None


class WebSocketServerFactory:
    """WebSocket 服务器工厂"""

    @staticmethod
    def create_stdio_compatible(
        name: str,
        version: str,
        handler: Callable[[str, dict[str, Any]], Any],
        crypto_enabled: bool = False,
    ) -> WebSocketServer:
        """创建与 stdio 服务器兼容的 WebSocket 服务器"""
        return WebSocketServer(
            host="127.0.0.1",
            port=8765,
            path="/mcp",
            crypto_enabled=crypto_enabled,
            heartbeat_interval=30.0,
        )

    @staticmethod
    def create_secure(
        name: str,
        version: str,
        handler: Callable[[str, dict[str, Any]], Any],
        auth_token: str,
    ) -> WebSocketServer:
        """创建带认证的 WebSocket 服务器"""
        server = WebSocketServer(
            host="0.0.0.0",
            port=8080,
            path="/mcp",
            auth_token=auth_token,
            crypto_enabled=True,
            heartbeat_interval=30.0,
        )
        return server
