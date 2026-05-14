# protocol.http_server

```include ../govmcp/protocol/http_server.py
```

## Module Documentation

govmcp.protocol.http_server — HTTP/SSE 传输层服务器

基于 aiohttp 实现 MCP HTTP/SSE 服务器，支持:

- Streamable HTTP 传输

- Server-Sent Events (SSE)

- SM4-CBC 加密传输（可选）

- SM3 消息完整性校验

- Token 认证

- 远程 MCP 连接

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `HTTPMethod`

`Enum Class`  

`Line: 49`  

**Base Classes:** `Enum`

HTTP 方法

---

### `HTTPRequest`

`Dataclass`  

`Line: 57`  

HTTP 请求封装

#### Attributes

| Name | Type |
|:---|:---|
| `method` | `str` |
| `path` | `str` |
| `headers` | `Dict[str, str]` |
| `body` | `Optional[Dict[str, Any]]` |
| `query_params` | `Dict[str, str]` |

---

### `HTTPResponse`

`Dataclass`  

`Line: 68`  

HTTP 响应封装

#### Attributes

| Name | Type |
|:---|:---|
| `status` | `int` |
| `headers` | `Dict[str, str]` |
| `body` | `Optional[Any]` |

#### Decorators

### `to_web_response(self: Any) -> web.Response`

`Line:75` `Complexity:Low`

转换为 aiohttp Response

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`web.Response`

---

---

### `HTTPServer`

`Line: 94`  

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

#### Attributes

| Name | Type |
|:---|:---|
| `host` | `str` |
| `port` | `int` |
| `path` | `str` |
| `sse_path` | `str` |
| `auth_token` | `Optional[str]` |
| `crypto_enabled` | `bool` |
| `sm4_key` | `Optional[bytes]` |
| `max_message_size` | `int` |
| `request_timeout` | `float` |
| `enable_cors` | `bool` |
| `cors_origins` | `Optional[List[str]]` |
| `enable_sse` | `bool` |
| `sse_heartbeat` | `float` |
| `log_level` | `int` |

#### Decorators

### `set_message_handler(self: Any, handler: Callable[[HTTPRequest], Any]) -> None`

`Line:179` `Complexity:Low`

设置消息处理器。

Args:

    handler: 异步函数，接收 HTTPRequest 并返回响应

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `handler` | `Callable[[HTTPRequest], Any]` | `-` |

#### Returns

`None`

---

### `get_sse_subscriber_count(self: Any) -> int`

`Line:262` `Complexity:Low`

获取 SSE 订阅者数量

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`int`

---

### `_setup_routes(self: Any) -> None`

`Line:266` `Complexity:Low`

设置路由

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`None`

---

### `_setup_middleware(self: Any) -> None`

`Line:276` `Complexity:Low`

设置中间件

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`None`

---

### `_check_auth(self: Any, request: web.Request) -> bool`

`Line:442` `Complexity:Low`

检查认证

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `web.Request` | `-` |

#### Returns

`bool`

---

### `_decrypt_body(self: Any, body: Dict[str, Any]) -> Dict[str, Any]`

`Line:452` `Complexity:Medium`

解密请求体

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `body` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_encrypt_and_sign(self: Any, data: Dict[str, Any]) -> Dict[str, Any]`

`Line:472` `Complexity:Medium`

加密并签名响应

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_validate_sm3(self: Any, data: Dict[str, Any]) -> bool`

`Line:491` `Complexity:Low`

验证 SM3 完整性

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`bool`

---

---

### `HTTPServerFactory`

`Line: 511`  

HTTP 服务器工厂

#### Decorators

### `create_stdio_compatible(name: str, version: str, handler: Callable[[HTTPRequest], Any], crypto_enabled: bool = False) -> HTTPServer`

`Line:515` `Complexity:Low`

创建与 stdio 服务器兼容的 HTTP 服务器

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `version` | `str` | `-` |
| `handler` | `Callable[[HTTPRequest], Any]` | `-` |
| `crypto_enabled` (Optional) | `bool` | `False` |

#### Returns

`HTTPServer`

---

### `create_secure(name: str, version: str, handler: Callable[[HTTPRequest], Any], auth_token: str) -> HTTPServer`

`Line:531` `Complexity:Low`

创建带认证的 HTTP 服务器

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `version` | `str` | `-` |
| `handler` | `Callable[[HTTPRequest], Any]` | `-` |
| `auth_token` | `str` | `-` |

#### Returns

`HTTPServer`

---

---

## Test Coverage

*No specific tests found for this module.*
