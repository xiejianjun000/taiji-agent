# protocol.websocket_server

```include ../govmcp/protocol/websocket_server.py
```

## Module Documentation

govmcp.protocol.websocket_server — WebSocket 传输层服务器

基于 websockets 库实现 MCP WebSocket 服务器，支持:

- 标准 MCP JSON-RPC 消息格式

- SM4-CBC 加密传输（可选）

- SM3 消息完整性校验

- Token 认证

- 多客户端连接管理

- 心跳检测

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `ConnectionState`

`Enum Class`  

`Line: 49`  

**Base Classes:** `Enum`

连接状态

---

### `ClientConnection`

`Dataclass`  

`Line: 59`  

客户端连接信息

#### Attributes

| Name | Type |
|:---|:---|
| `client_id` | `str` |
| `websocket` | `Any` |
| `state` | `ConnectionState` |
| `auth_token` | `Optional[str]` |
| `authenticated_at` | `Optional[datetime]` |
| `last_heartbeat` | `datetime` |
| `message_count` | `int` |
| `remote_addr` | `Optional[str]` |
| `headers` | `Dict[str, str]` |

---

### `WebSocketServer`

`Line: 73`  

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

#### Attributes

| Name | Type |
|:---|:---|
| `host` | `str` |
| `port` | `int` |
| `path` | `str` |
| `auth_token` | `Optional[str]` |
| `crypto_enabled` | `bool` |
| `sm4_key` | `Optional[bytes]` |
| `heartbeat_interval` | `float` |
| `heartbeat_timeout` | `float` |
| `max_message_size` | `int` |
| `enable_cors` | `bool` |
| `cors_origins` | `Optional[List[str]]` |
| `log_level` | `int` |

#### Decorators

### `set_message_handler(self: Any, handler: Callable[[str, Dict[str, Any]], Any]) -> None`

`Line:149` `Complexity:Low`

设置消息处理器。

Args:

    handler: 异步函数，接收 (client_id, message) 并返回响应

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `handler` | `Callable[[str, Dict[str, Any]], Any]` | `-` |

#### Returns

`None`

---

### `get_client_count(self: Any) -> int`

`Line:232` `Complexity:Low`

获取当前连接数

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`int`

---

### `get_authenticated_count(self: Any) -> int`

`Line:236` `Complexity:Low`

获取已认证连接数

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`int`

---

### `_validate_sm3(self: Any, data: Dict[str, Any], client: ClientConnection) -> bool`

`Line:435` `Complexity:Medium`

验证 SM3 完整性

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |
| `client` | `ClientConnection` | `-` |

#### Returns

`bool`

---

---

### `WebSocketServerFactory`

`Line: 512`  

WebSocket 服务器工厂

#### Decorators

### `create_stdio_compatible(name: str, version: str, handler: Callable[[str, Dict[str, Any]], Any], crypto_enabled: bool = False) -> WebSocketServer`

`Line:516` `Complexity:Low`

创建与 stdio 服务器兼容的 WebSocket 服务器

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `version` | `str` | `-` |
| `handler` | `Callable[[str, Dict[str, Any]], Any]` | `-` |
| `crypto_enabled` (Optional) | `bool` | `False` |

#### Returns

`WebSocketServer`

---

### `create_secure(name: str, version: str, handler: Callable[[str, Dict[str, Any]], Any], auth_token: str) -> WebSocketServer`

`Line:532` `Complexity:Low`

创建带认证的 WebSocket 服务器

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `version` | `str` | `-` |
| `handler` | `Callable[[str, Dict[str, Any]], Any]` | `-` |
| `auth_token` | `str` | `-` |

#### Returns

`WebSocketServer`

---

---

## Test Coverage

*No specific tests found for this module.*
