"""
govmcp.protocol.http_server — HTTP/SSE 传输层服务器

基于 aiohttp 实现 MCP HTTP/SSE 服务器，支持:
- Streamable HTTP 传输
- Server-Sent Events (SSE)
- SM4-CBC 加密传输（可选）
- SM3 消息完整性校验
- Token 认证
- 远程 MCP 连接
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

try:
    import aiohttp
    from aiohttp import web

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None
    web = None

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


class HTTPMethod(Enum):
    """HTTP 方法"""

    POST = "POST"
    GET = "GET"


@dataclass
class HTTPRequest:
    """HTTP 请求封装"""

    method: str
    path: str
    headers: dict[str, str]
    body: dict[str, Any] | None = None
    query_params: dict[str, str] = field(default_factory=dict)


@dataclass
class HTTPResponse:
    """HTTP 响应封装"""

    status: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    body: Any | None = None

    def to_web_response(self) -> web.Response:
        """转换为 aiohttp Response"""
        headers = {
            "Content-Type": "application/json",
            **self.headers,
        }

        if self.body is not None:
            body_str = json.dumps(self.body, ensure_ascii=False)
        else:
            body_str = ""

        return web.Response(
            text=body_str,
            status=self.status,
            headers=headers,
        )


class HTTPServer:
    """
    HTTP/SSE MCP 服务器

    提供 HTTP 和 SSE 传输层，支持国密加密和认证。

    用法:
        async def handler(request: HTTPRequest) -> HTTPResponse:
            message = request.body
            result = await server.handle_message(message)
            return HTTPResponse(body=result)

        server = HTTPServer(
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
        sse_path: str = "/mcp/sse",
        auth_token: str | None = None,
        crypto_enabled: bool = False,
        sm4_key: bytes | None = None,
        max_message_size: int = 10 * 1024 * 1024,
        request_timeout: float = 60.0,
        enable_cors: bool = True,
        cors_origins: list[str] | None = None,
        enable_sse: bool = True,
        sse_heartbeat: float = 15.0,
        log_level: int = logging.INFO,
    ) -> None:
        """
        初始化 HTTP 服务器。

        Args:
            host: 绑定主机地址
            port: 绑定端口
            path: MCP 端点路径
            sse_path: SSE 端点路径
            auth_token: 认证 Token（可选）
            crypto_enabled: 是否启用 SM4-CBC 加密
            sm4_key: SM4 密钥（16字节），为 None 时自动生成
            max_message_size: 最大消息大小（字节）
            request_timeout: 请求超时（秒）
            enable_cors: 是否启用 CORS
            cors_origins: CORS 允许的来源列表
            enable_sse: 是否启用 SSE
            sse_heartbeat: SSE 心跳间隔（秒）
            log_level: 日志级别
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError("aiohttp 库未安装。请运行: pip install aiohttp")

        self.host = host
        self.port = port
        self.path = path
        self.sse_path = sse_path
        self.auth_token = auth_token
        self.crypto_enabled = crypto_enabled
        self.sm4_key: bytes = sm4_key if sm4_key else generate_sm4_key()
        self.max_message_size = max_message_size
        self.request_timeout = request_timeout
        self.enable_cors = enable_cors
        self.cors_origins = cors_origins or ["*"]
        self.enable_sse = enable_sse
        self.sse_heartbeat = sse_heartbeat

        self._handler: Callable[[HTTPRequest], Any] | None = None
        self._sse_handlers: dict[str, asyncio.Queue] = {}
        self._running = False
        self._app: web.Application | None = None
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self._heartbeat_tasks: dict[str, asyncio.Task] = {}

        logging.basicConfig(level=log_level)
        self._logger = logging.getLogger(__name__)

    def set_message_handler(self, handler: Callable[[HTTPRequest], Any]) -> None:
        """
        设置消息处理器。

        Args:
            handler: 异步函数，接收 HTTPRequest 并返回响应
        """
        self._handler = handler

    async def start(self, handler: Callable[[HTTPRequest], Any] | None = None) -> None:
        """
        启动 HTTP 服务器。

        Args:
            handler: 消息处理器（可选）
        """
        if handler:
            self._handler = handler

        if not self._handler:
            raise ValueError("必须设置消息处理器")

        self._running = True
        self._app = web.Application(client_max_size=self.max_message_size)

        self._setup_routes()
        self._setup_middleware()

        self._runner = web.AppRunner(self._app)
        await self._runner.setup()

        self._site = web.TCPSite(
            self._runner,
            self.host,
            self.port,
        )
        await self._site.start()

        self._logger.info(f"HTTP 服务器已启动: http://{self.host}:{self.port}{self.path}")

    async def stop(self) -> None:
        """停止 HTTP 服务器"""
        self._running = False

        for task in self._heartbeat_tasks.values():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._heartbeat_tasks.clear()

        for queue in self._sse_handlers.values():
            await queue.put(None)
        self._sse_handlers.clear()

        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()

        self._logger.info("HTTP 服务器已停止")

    async def broadcast_sse(self, event: str, data: Any) -> int:
        """
        广播 SSE 事件给所有订阅者。

        Args:
            event: 事件类型
            data: 事件数据

        Returns:
            发送到的订阅者数量
        """
        message = f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
        count = 0

        for queue in self._sse_handlers.values():
            await queue.put(message)
            count += 1

        return count

    def get_sse_subscriber_count(self) -> int:
        """获取 SSE 订阅者数量"""
        return len(self._sse_handlers)

    def _setup_routes(self) -> None:
        """设置路由"""
        self._app.router.add_post(self.path, self._handle_post)
        self._app.router.add_get(self.path, self._handle_get)
        self._app.router.add_options(self.path, self._handle_cors_preflight)

        if self.enable_sse:
            self._app.router.add_get(self.sse_path, self._handle_sse)
            self._app.router.add_options(self.sse_path, self._handle_cors_preflight)

    def _setup_middleware(self) -> None:
        """设置中间件"""
        if self.enable_cors:
            self._app.middlewares.append(self._cors_middleware)

    @web.middleware
    async def _cors_middleware(
        self,
        request: web.Request,
        handler: Callable,
    ) -> web.Response:
        """CORS 中间件"""
        if request.method == "OPTIONS":
            response = web.Response()
        else:
            response = await handler(request)

        origin = request.headers.get("Origin", "*")
        if origin in self.cors_origins or "*" in self.cors_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Encrypted, X-SM3-Hash"
            )
            response.headers["Access-Control-Max-Age"] = "3600"

        return response

    async def _handle_post(self, request: web.Request) -> web.Response:
        """处理 POST 请求"""
        try:
            if self.auth_token and not self._check_auth(request):
                return web.json_response(
                    {"jsonrpc": "2.0", "error": {"code": -32001, "message": "认证失败"}},
                    status=401,
                )

            body = await request.json()

            body = self._decrypt_body(body)

            if "_sm3" in body:
                if not self._validate_sm3(body):
                    return web.json_response(
                        {"jsonrpc": "2.0", "error": {"code": -32600, "message": "SM3 校验失败"}},
                        status=400,
                    )

            http_request = HTTPRequest(
                method="POST",
                path=request.path,
                headers=dict(request.headers),
                body=body,
                query_params=dict(request.query),
            )

            response = await self._handler(http_request)

            if isinstance(response, HTTPResponse):
                return response.to_web_response()
            elif isinstance(response, dict):
                response_data = self._encrypt_and_sign(response)
                return web.json_response(response_data)
            else:
                return web.json_response(response)

        except json.JSONDecodeError:
            return web.json_response(
                {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Invalid JSON"}},
                status=400,
            )
        except Exception as e:
            self._logger.error(f"POST 处理错误: {e}")
            return web.json_response(
                {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}},
                status=500,
            )

    async def _handle_get(self, request: web.Request) -> web.Response:
        """处理 GET 请求（用于健康检查等）"""
        return web.json_response(
            {
                "status": "ok",
                "service": "govmcp-http",
                "path": self.path,
                "sse_enabled": self.enable_sse,
                "crypto_enabled": self.crypto_enabled,
            }
        )

    async def _handle_cors_preflight(self, request: web.Request) -> web.Response:
        """处理 CORS 预检请求"""
        response = web.Response()
        origin = request.headers.get("Origin", "*")
        if origin in self.cors_origins or "*" in self.cors_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Encrypted, X-SM3-Hash"
            )
            response.headers["Access-Control-Max-Age"] = "3600"
        return response

    async def _handle_sse(self, request: web.Request) -> web.StreamResponse:
        """处理 SSE 连接"""
        if self.auth_token and not self._check_auth(request):
            return web.json_response(
                {"error": "认证失败"},
                status=401,
            )

        client_id = str(uuid.uuid4())
        queue: asyncio.Queue = asyncio.Queue()
        self._sse_handlers[client_id] = queue

        self._logger.info(f"SSE 客户端连接: {client_id}")

        response = web.StreamResponse(
            status=200,
            reason="OK",
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
        await response.prepare(request)

        async def heartbeat():
            try:
                while True:
                    await asyncio.sleep(self.sse_heartbeat)
                    await response.write(b": heartbeat\n\n")
            except asyncio.CancelledError:
                pass
            except Exception:
                pass

        heartbeat_task = asyncio.create_task(heartbeat())
        self._heartbeat_tasks[client_id] = heartbeat_task

        try:
            while self._running:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    if message is None:
                        break
                    await response.write(message.encode("utf-8"))
                except asyncio.TimeoutError:
                    try:
                        await response.write(b": keepalive\n\n")
                    except Exception:
                        break
        except Exception as e:
            self._logger.warning(f"SSE 错误 {client_id}: {e}")
        finally:
            if client_id in self._heartbeat_tasks:
                self._heartbeat_tasks[client_id].cancel()
                del self._heartbeat_tasks[client_id]
            if client_id in self._sse_handlers:
                del self._sse_handlers[client_id]
            self._logger.info(f"SSE 客户端断开: {client_id}")

        return response

    def _check_auth(self, request: web.Request) -> bool:
        """检查认证"""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        else:
            token = request.headers.get("X-Auth-Token", "")

        return token == self.auth_token

    def _decrypt_body(self, body: dict[str, Any]) -> dict[str, Any]:
        """解密请求体"""
        if not self.crypto_enabled:
            return body

        if body.get("_encrypted"):
            try:
                ciphertext = base64.b64decode(body.get("data", ""))
                iv_str = body.get("iv", "")
                if iv_str:
                    iv = base64.b64decode(iv_str)
                else:
                    iv = self.sm4_key
                plaintext = pkcs7_unpad(sm4_cbc_decrypt(ciphertext, self.sm4_key, iv))
                return json.loads(plaintext.decode("utf-8"))
            except Exception:
                return body

        return body

    def _encrypt_and_sign(self, data: dict[str, Any]) -> dict[str, Any]:
        """加密并签名响应"""
        result = data.copy()

        if self.crypto_enabled:
            payload = json.dumps(data, ensure_ascii=False)
            iv = generate_sm4_iv()
            ciphertext = sm4_cbc_encrypt(payload.encode("utf-8"), self.sm4_key, iv)
            result = {
                "_encrypted": True,
                "iv": base64.b64encode(iv).decode("ascii"),
                "data": base64.b64encode(ciphertext).decode("ascii"),
            }

        payload = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        result["_sm3"] = sm3_hash(payload.encode("utf-8"))

        return result

    def _validate_sm3(self, data: dict[str, Any]) -> bool:
        """验证 SM3 完整性"""
        if "_sm3" not in data:
            return True

        expected = data.pop("_sm3")
        payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        actual = sm3_hash(payload.encode("utf-8"))

        return actual == expected

    async def handle_message(self, request: HTTPRequest) -> dict[str, Any] | None:
        """
        默认消息处理器（需要外部设置实际的处理器）。

        此方法可被子类重写或通过 set_message_handler 替换。
        """
        return None


class HTTPServerFactory:
    """HTTP 服务器工厂"""

    @staticmethod
    def create_stdio_compatible(
        name: str,
        version: str,
        handler: Callable[[HTTPRequest], Any],
        crypto_enabled: bool = False,
    ) -> HTTPServer:
        """创建与 stdio 服务器兼容的 HTTP 服务器"""
        return HTTPServer(
            host="127.0.0.1",
            port=8766,
            path="/mcp",
            crypto_enabled=crypto_enabled,
            enable_sse=True,
        )

    @staticmethod
    def create_secure(
        name: str,
        version: str,
        handler: Callable[[HTTPRequest], Any],
        auth_token: str,
    ) -> HTTPServer:
        """创建带认证的 HTTP 服务器"""
        return HTTPServer(
            host="0.0.0.0",
            port=8080,
            path="/mcp",
            auth_token=auth_token,
            crypto_enabled=True,
            enable_cors=True,
            enable_sse=True,
        )
