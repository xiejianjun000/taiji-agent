"""
govmcp 传输层测试

测试传输层组件: Transport 基类、StdioTransport、WebSocketTransport、HTTPTransport、
WebSocketServer、HTTPServer 等。
"""

import asyncio
import base64
import json
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from govmcp.crypto.sm import pkcs7_pad, pkcs7_unpad, sm3_hash, sm4_cbc_decrypt, sm4_cbc_encrypt
from govmcp.transport.base import (
    HTTPTransport,
    Message,
    Response,
    StdioTransport,
    Transport,
    TransportCallbacks,
    TransportConfig,
    TransportType,
    WebSocketTransport,
)


class TestTransportConfig:
    """测试 TransportConfig"""

    def test_default_config(self):
        config = TransportConfig()
        assert config.transport_type == TransportType.STDIO
        assert config.host == "127.0.0.1"
        assert config.port == 8080
        assert config.crypto_enabled is False
        assert config.auth_token is None

    def test_custom_config(self):
        config = TransportConfig(
            transport_type=TransportType.WEBSOCKET,
            host="0.0.0.0",
            port=9000,
            auth_token="test-token",
            crypto_enabled=True,
        )
        assert config.transport_type == TransportType.WEBSOCKET
        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.auth_token == "test-token"
        assert config.crypto_enabled is True

    def test_config_with_sm4_key(self):
        key = b"1234567890abcdef"
        config = TransportConfig(sm4_key=key)
        assert config.sm4_key == key


class TestMessage:
    """测试 Message 类"""

    def test_message_creation(self):
        msg = Message(method="test.method", params={"key": "value"}, msg_id="1")
        assert msg.method == "test.method"
        assert msg.params == {"key": "value"}
        assert msg.msg_id == "1"
        assert msg.jsonrpc == "2.0"

    def test_message_from_dict(self):
        data = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 42,
        }
        msg = Message.from_dict(data)
        assert msg.method == "tools/list"
        assert msg.params == {}
        assert msg.msg_id == 42

    def test_message_to_dict(self):
        msg = Message(method="test", params={"a": 1}, msg_id="abc")
        result = msg.to_dict()
        assert result["method"] == "test"
        assert result["params"] == {"a": 1}
        assert result["id"] == "abc"
        assert result["jsonrpc"] == "2.0"

    def test_message_without_id(self):
        msg = Message(method="notification")
        result = msg.to_dict()
        assert "id" not in result


class TestResponse:
    """测试 Response 类"""

    def test_response_success(self):
        resp = Response(result={"status": "ok"}, msg_id="1")
        assert resp.result == {"status": "ok"}
        assert resp.msg_id == "1"
        assert resp.error is None

    def test_response_error(self):
        resp = Response(error={"code": -32600, "message": "Invalid Request"}, msg_id="2")
        assert resp.error == {"code": -32600, "message": "Invalid Request"}
        assert resp.result is None

    def test_response_from_dict(self):
        data = {"jsonrpc": "2.0", "result": {"tools": []}, "id": 1}
        resp = Response.from_dict(data)
        assert resp.result == {"tools": []}
        assert resp.msg_id == 1

    def test_response_from_dict_error(self):
        data = {"jsonrpc": "2.0", "error": {"code": -32601}, "id": 2}
        resp = Response.from_dict(data)
        assert resp.error == {"code": -32601}
        assert resp.msg_id == 2


class TestTransportCallbacks:
    """测试 TransportCallbacks 抽象类"""

    def test_callbacks_is_abstract(self):
        assert hasattr(TransportCallbacks, "on_message")
        assert hasattr(TransportCallbacks, "on_error")
        assert hasattr(TransportCallbacks, "on_disconnect")
        assert hasattr(TransportCallbacks, "on_connect")
        assert hasattr(TransportCallbacks, "on_heartbeat")
        with pytest.raises(TypeError):
            TransportCallbacks()

    def test_callbacks_concrete_implementation(self):
        callbacks = MockCallbacks()
        callbacks.on_message(Message(method="test"))
        assert len(callbacks.messages) == 1
        callbacks.on_error(Exception("test error"))
        assert len(callbacks.errors) == 1
        callbacks.on_connect()
        assert callbacks.connected is True
        callbacks.on_disconnect()
        assert callbacks.disconnected is True


class TestStdioTransport:
    """测试 StdioTransport"""

    def test_stdio_transport_creation(self):
        transport = StdioTransport()
        assert transport.transport_type == TransportType.STDIO
        assert transport.connected is False

    def test_stdio_transport_config(self):
        config = TransportConfig(transport_type=TransportType.STDIO)
        transport = StdioTransport(config)
        assert transport.config.transport_type == TransportType.STDIO

    @pytest.mark.asyncio
    async def test_stdio_connect(self):
        transport = StdioTransport()
        await transport.connect()
        assert transport.connected is True

    @pytest.mark.asyncio
    async def test_stdio_disconnect(self):
        transport = StdioTransport()
        await transport.connect()
        await transport.disconnect()
        assert transport.connected is False

    @pytest.mark.asyncio
    async def test_stdio_disconnect_when_not_connected(self):
        transport = StdioTransport()
        await transport.disconnect()
        assert transport.connected is False

    @pytest.mark.asyncio
    async def test_stdio_send(self):
        transport = StdioTransport()
        msg = Message(method="test", msg_id="1")
        with patch("sys.stdout") as mock_stdout:
            await transport.send(msg)
            mock_stdout.write.assert_called_once()
            written = mock_stdout.write.call_args[0][0]
            data = json.loads(written)
            assert data["method"] == "test"


class MockCallbacks(TransportCallbacks):
    """测试用回调实现"""

    def __init__(self):
        self.messages = []
        self.errors = []
        self.connected = False
        self.disconnected = False
        self.heartbeats = 0

    def on_message(self, message: Message) -> None:
        self.messages.append(message)

    def on_error(self, error: Exception) -> None:
        self.errors.append(error)

    def on_disconnect(self) -> None:
        self.disconnected = True

    def on_connect(self) -> None:
        self.connected = True

    def on_heartbeat(self) -> None:
        self.heartbeats += 1


class TestWebSocketTransport:
    """测试 WebSocketTransport"""

    def test_websocket_transport_creation(self):
        transport = WebSocketTransport()
        assert transport.transport_type == TransportType.WEBSOCKET
        assert transport.connected is False

    def test_websocket_transport_with_config(self):
        config = TransportConfig(
            transport_type=TransportType.WEBSOCKET,
            host="localhost",
            port=8080,
            crypto_enabled=True,
        )
        transport = WebSocketTransport(config)
        assert transport.config.host == "localhost"
        assert transport.config.crypto_enabled is True

    @pytest.mark.asyncio
    async def test_websocket_disconnect_when_not_connected(self):
        transport = WebSocketTransport()
        await transport.disconnect()
        assert transport.connected is False


class TestHTTPTransport:
    """测试 HTTPTransport"""

    def test_http_transport_creation(self):
        transport = HTTPTransport()
        assert transport.transport_type == TransportType.HTTP
        assert transport.connected is False

    def test_http_transport_with_config(self):
        config = TransportConfig(
            transport_type=TransportType.HTTP,
            host="example.com",
            port=80,
            auth_token="secret",
        )
        transport = HTTPTransport(config)
        assert transport.config.host == "example.com"
        assert transport.config.auth_token == "secret"

    @pytest.mark.asyncio
    async def test_http_disconnect_when_not_connected(self):
        transport = HTTPTransport()
        await transport.disconnect()
        assert transport.connected is False


class TestSM3Hash:
    """测试 SM3 哈希功能"""

    def test_sm3_hash_basic(self):
        data = b"hello world"
        result = sm3_hash(data)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_sm3_hash_consistency(self):
        data = b"test data"
        hash1 = sm3_hash(data)
        hash2 = sm3_hash(data)
        assert hash1 == hash2

    def test_sm3_hash_different_inputs(self):
        hash1 = sm3_hash(b"data1")
        hash2 = sm3_hash(b"data2")
        assert hash1 != hash2

    def test_sm3_hash_empty(self):
        result = sm3_hash(b"")
        assert isinstance(result, str)
        assert len(result) == 64


class TestSM4CBC:
    """测试 SM4-CBC 加密功能"""

    def test_sm4_cbc_encrypt_decrypt(self):
        plaintext = b"Hello, World!"
        key = b"1234567890abcdef"
        iv = b"1234567890abcdef"

        ciphertext = sm4_cbc_encrypt(plaintext, key, iv)
        decrypted = sm4_cbc_decrypt(ciphertext, key, iv)

        assert ciphertext != plaintext
        assert decrypted == plaintext

    def test_sm4_cbc_with_padding(self):
        plaintext = b"A" * 100
        key = b"1234567890abcdef"
        iv = b"1234567890abcdef"

        ciphertext = sm4_cbc_encrypt(plaintext, key, iv)
        decrypted = sm4_cbc_decrypt(ciphertext, key, iv)

        assert decrypted == plaintext

    def test_sm4_cbc_invalid_key_length(self):
        with pytest.raises(ValueError):
            sm4_cbc_encrypt(b"test", b"short", b"1234567890abcdef")

    def test_sm4_cbc_invalid_iv_length(self):
        with pytest.raises(ValueError):
            sm4_cbc_encrypt(b"test", b"1234567890abcdef", b"short")


class TestPKCS7Padding:
    """测试 PKCS7 填充"""

    def test_pkcs7_pad_multiple_of_block(self):
        data = b"A" * 16
        padded = pkcs7_pad(data, 16)
        assert len(padded) == 32
        assert padded[-16:] == bytes([16] * 16)

    def test_pkcs7_pad_partial_block(self):
        data = b"A" * 10
        padded = pkcs7_pad(data, 16)
        assert len(padded) == 16
        assert padded[-6:] == bytes([6] * 6)

    def test_pkcs7_unpad(self):
        original = b"Test data"
        padded = pkcs7_pad(original, 16)
        unpadded = pkcs7_unpad(padded, 16)
        assert unpadded == original


class TestTransportCallbacksIntegration:
    """测试传输层回调集成"""

    def test_callbacks_set_and_trigger(self):
        transport = StdioTransport()
        callbacks = MockCallbacks()
        transport.set_callbacks(callbacks)

        assert transport._callbacks is callbacks

    def test_message_to_dict_integration(self):
        msg = Message(
            method="tools/call",
            params={"name": "test_tool", "arguments": {}},
            msg_id="42",
        )
        data = msg.to_dict()

        assert data["method"] == "tools/call"
        assert data["params"]["name"] == "test_tool"
        assert data["id"] == "42"


class TestTransportType:
    """测试 TransportType 枚举"""

    def test_transport_type_values(self):
        assert TransportType.STDIO.value == "stdio"
        assert TransportType.WEBSOCKET.value == "websocket"
        assert TransportType.HTTP.value == "http"
        assert TransportType.SSE.value == "sse"

    def test_transport_type_iteration(self):
        types = list(TransportType)
        assert len(types) == 4
        assert TransportType.STDIO in types
        assert TransportType.WEBSOCKET in types


class TestMessageIntegration:
    """测试消息类的集成使用"""

    def test_json_rpc_request_message(self):
        msg = Message(
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "test", "version": "1.0"},
            },
            msg_id="1",
        )

        data = msg.to_dict()
        json_str = json.dumps(data, ensure_ascii=False)
        parsed = json.loads(json_str)

        assert parsed["jsonrpc"] == "2.0"
        assert parsed["method"] == "initialize"
        assert "protocolVersion" in parsed["params"]

    def test_json_rpc_response_message(self):
        resp = Response(
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
            },
            msg_id="1",
        )

        data = resp.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert "capabilities" in data["result"]

    def test_notification_message(self):
        msg = Message(method="notifications/initialized")
        data = msg.to_dict()
        assert "id" not in data
        assert data["method"] == "notifications/initialized"


class TestCryptoIntegration:
    """测试加密功能集成"""

    def test_encrypted_message_flow(self):
        plaintext = b"Hello, GovMCP!"
        key = b"1234567890abcdef"
        iv = b"1234567890abcdef"

        ciphertext = sm4_cbc_encrypt(plaintext, key, iv)
        decrypted = sm4_cbc_decrypt(ciphertext, key, iv)

        assert decrypted == plaintext
        assert ciphertext != plaintext

    def test_message_with_sm3_hash(self):
        msg_data = {"method": "test", "params": {}}
        payload = json.dumps(msg_data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        sm3 = sm3_hash(payload.encode("utf-8"))

        assert isinstance(sm3, str)
        assert len(sm3) == 64

        msg_data_verify = {"method": "test", "params": {}, "_sm3": sm3}
        verify_payload = json.dumps(
            msg_data_verify, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        verify_sm3 = sm3_hash(verify_payload.encode("utf-8"))

        assert verify_sm3 != sm3

        verify_data = {"method": "test", "params": {}}
        verify_data_payload = json.dumps(
            verify_data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        original_sm3 = sm3_hash(verify_data_payload.encode("utf-8"))
        assert len(original_sm3) == 64


class TestBase64Encoding:
    """测试 Base64 编码"""

    def test_base64_encode_decode(self):
        data = b"Hello, World!"
        encoded = base64.b64encode(data).decode("ascii")
        decoded = base64.b64decode(encoded)
        assert decoded == data

    def test_base64_encrypted_data(self):
        plaintext = b"Secret message"
        key = b"1234567890abcdef"
        iv = b"1234567890abcdef"

        ciphertext = sm4_cbc_encrypt(plaintext, key, iv)
        encoded = base64.b64encode(ciphertext).decode("ascii")

        decoded = base64.b64decode(encoded)
        decrypted = sm4_cbc_decrypt(decoded, key, iv)

        assert decrypted == plaintext


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
