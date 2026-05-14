# protocol.http_server

```include ../govmcp/protocol/http_server.py
```

## 模块文档

govmcp.protocol.http_server — HTTP/SSE 传输层服务器

基于 aiohttp 实现 MCP HTTP/SSE 服务器，支持:

- Streamable HTTP 传输

- Server-Sent Events (SSE)

- SM4-CBC 加密传输（可选）

- SM3 消息完整性校验

- Token 认证

- 远程 MCP 连接

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| - | - | - |

## 导出类

### `HTTPMethod`

`枚举类`  

`行号: 49`  

**基类:** `Enum`

HTTP 方法

---

### `HTTPRequest`

`数据类`  

`行号: 57`  

HTTP 请求封装

#### 属性

| Name | Type |
|:---|:---|
| `method` | `str` |
| `path` | `str` |
| `headers` | `Dict[str, str]` |
| `body` | `Optional[Dict[str, Any]]` |
| `query_params` | `Dict[str, str]` |

---

### `HTTPResponse`

`数据类`  

`行号: 68`  

HTTP 响应封装

#### 属性

| Name | Type |
|:---|:---|
| `status` | `int` |
| `headers` | `Dict[str, str]` |
| `body` | `Optional[Any]` |

#### 装饰器

### `to_web_response(self: Any) -> web.Response`

`行号:75` `复杂度:低`

转换为 aiohttp Response

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`web.Response`

---

---

### `HTTPServer`

`行号: 94`  

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

#### 属性

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

#### 装饰器

### `set_message_handler(self: Any, handler: Callable[[HTTPRequest], Any]) -> None`

`行号:179` `复杂度:低`

设置消息处理器。

Args:

    handler: 异步函数，接收 HTTPRequest 并返回响应

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `handler` | `Callable[[HTTPRequest], Any]` | `-` |

#### 返回

`None`

---

### `get_sse_subscriber_count(self: Any) -> int`

`行号:262` `复杂度:低`

获取 SSE 订阅者数量

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`int`

---

### `_setup_routes(self: Any) -> None`

`行号:266` `复杂度:低`

设置路由

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`None`

---

### `_setup_middleware(self: Any) -> None`

`行号:276` `复杂度:低`

设置中间件

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`None`

---

### `_check_auth(self: Any, request: web.Request) -> bool`

`行号:442` `复杂度:低`

检查认证

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `web.Request` | `-` |

#### 返回

`bool`

---

### `_decrypt_body(self: Any, body: Dict[str, Any]) -> Dict[str, Any]`

`行号:452` `复杂度:中`

解密请求体

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `body` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_encrypt_and_sign(self: Any, data: Dict[str, Any]) -> Dict[str, Any]`

`行号:472` `复杂度:中`

加密并签名响应

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_validate_sm3(self: Any, data: Dict[str, Any]) -> bool`

`行号:491` `复杂度:低`

验证 SM3 完整性

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`bool`

---

---

### `HTTPServerFactory`

`行号: 511`  

HTTP 服务器工厂

#### 装饰器

### `create_stdio_compatible(name: str, version: str, handler: Callable[[HTTPRequest], Any], crypto_enabled: bool = False) -> HTTPServer`

`行号:515` `复杂度:低`

创建与 stdio 服务器兼容的 HTTP 服务器

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `version` | `str` | `-` |
| `handler` | `Callable[[HTTPRequest], Any]` | `-` |
| `crypto_enabled` (可选) | `bool` | `False` |

#### 返回

`HTTPServer`

---

### `create_secure(name: str, version: str, handler: Callable[[HTTPRequest], Any], auth_token: str) -> HTTPServer`

`行号:531` `复杂度:低`

创建带认证的 HTTP 服务器

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `version` | `str` | `-` |
| `handler` | `Callable[[HTTPRequest], Any]` | `-` |
| `auth_token` | `str` | `-` |

#### 返回

`HTTPServer`

---

---

## Test Coverage

*No specific tests found for this module.*
