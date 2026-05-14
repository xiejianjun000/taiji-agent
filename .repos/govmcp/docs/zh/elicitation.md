# protocol.elicitation

```include ../govmcp/protocol/elicitation.py
```

## 模块文档

govmcp.protocol.elicitation — 用户交互支持 (MCP 2025.11)

提供安全带外用户交互功能，支持：

- 信息请求（ElicitRequest）

- URL Mode Elicitation

- 表单交互

- 安全提示确认

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| 563 | 低 | - |

## 导出函数

### `create_secure_prompt_request(message: str, resource_uri: Optional[str] = None, timeout: float = 300.0) -> ElicitRequest`

`行号:563` `复杂度:低`

创建安全提示确认请求

Args:

    message: 消息内容

    resource_uri: 资源 URI

    timeout: 超时时间

Returns:

    交互请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `message` | `str` | `-` |
| `resource_uri` (可选) | `Optional[str]` | `None` |
| `timeout` (可选) | `float` | `300.0` |

#### 返回

`ElicitRequest`

---

## 导出类

### `ElicitType`

`枚举类`  

`行号: 22`  

**基类:** `str | Enum`

交互类型

---

### `ElicitStatus`

`枚举类`  

`行号: 32`  

**基类:** `str | Enum`

交互状态

---

### `ElicitRequest`

`数据类`  

`行号: 43`  

用户交互请求

用于向用户请求额外信息或确认。

#### 属性

| Name | Type |
|:---|:---|
| `message` | `str` |
| `requested_schema` | `Dict[str, Any]` |
| `elicit_type` | `Union[ElicitType, str]` |
| `timeout` | `float` |
| `id` | `Optional[str]` |
| `created_at` | `Optional[float]` |
| `expires_at` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

#### 装饰器

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:67` `复杂度:低`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'ElicitRequest'`

`行号:83` `复杂度:低`

从字典创建

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`'ElicitRequest'`

---

---

### `ElicitResponse`

`数据类`  

`行号: 98`  

用户交互响应

#### 属性

| Name | Type |
|:---|:---|
| `request_id` | `str` |
| `status` | `Union[ElicitStatus, str]` |
| `value` | `Optional[Any]` |
| `error` | `Optional[str]` |
| `responded_at` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

#### 装饰器

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:112` `复杂度:中`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'ElicitResponse'`

`行号:129` `复杂度:低`

从字典创建

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`'ElicitResponse'`

---

---

### `URLElicitation`

`数据类`  

`行号: 142`  

URL Mode Elicitation

通过 URL 方式向用户请求交互。

#### 属性

| Name | Type |
|:---|:---|
| `url` | `str` |
| `title` | `str` |
| `request_id` | `str` |
| `method` | `str` |
| `headers` | `Dict[str, str]` |
| `body` | `Optional[str]` |
| `timeout` | `float` |
| `created_at` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

#### 装饰器

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:163` `复杂度:中`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'URLElicitation'`

`行号:182` `复杂度:低`

从字典创建

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`'URLElicitation'`

---

---

### `ElicitationHandler`

`行号: 197`  

交互处理器接口

#### 装饰器

### `handle_request(self: Any, request: ElicitRequest) -> ElicitResponse`

`行号:200` `复杂度:低`

处理交互请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `ElicitRequest` | `-` |

#### 返回

`ElicitResponse`

---

### `can_handle(self: Any, request: ElicitRequest) -> bool`

`行号:207` `复杂度:低`

检查是否可以处理

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `ElicitRequest` | `-` |

#### 返回

`bool`

---

---

### `ConsoleElicitationHandler`

`行号: 212`  

**基类:** `ElicitationHandler`

控制台交互处理器

#### 属性

| Name | Type |
|:---|:---|
| `input_func` | `Optional[Callable[[str], str]]` |

#### 装饰器

### `handle_request(self: Any, request: ElicitRequest) -> ElicitResponse`

`行号:218` `复杂度:低`

处理交互请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `ElicitRequest` | `-` |

#### 返回

`ElicitResponse`

---

### `_get_confirmation(self: Any, message: str) -> bool`

`行号:242` `复杂度:低`

获取确认

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |

#### 返回

`bool`

---

### `_get_input(self: Any, message: str, schema: Dict[str, Any]) -> Any`

`行号:249` `复杂度:低`

获取输入

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |
| `schema` | `Dict[str, Any]` | `-` |

#### 返回

`Any`

---

---

### `ElicitationManager`

`行号: 257`  

交互管理器

管理用户交互请求的生命周期。

#### 装饰器

### `add_handler(self: Any, handler: ElicitationHandler) -> None`

`行号:272` `复杂度:低`

添加处理器

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `handler` | `ElicitationHandler` | `-` |

#### 返回

`None`

---

### `set_default_handler(self: Any, handler: ElicitationHandler) -> None`

`行号:276` `复杂度:低`

设置默认处理器

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `handler` | `ElicitationHandler` | `-` |

#### 返回

`None`

---

### `register_callback(self: Any, request_id: str, callback: Callable[[ElicitResponse], None]) -> None`

`行号:280` `复杂度:低`

注册回调

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |
| `callback` | `Callable[[ElicitResponse], None]` | `-` |

#### 返回

`None`

---

### `create_request(self: Any, message: str, requested_schema: Optional[Dict[str, Any]] = None, elicit_type: Union[ElicitType, str] = ElicitType.REQUEST, timeout: float = 300.0, metadata: Optional[Dict[str, Any]] = None) -> ElicitRequest`

`行号:288` `复杂度:低`

创建交互请求

Args:

    message: 消息内容

    requested_schema: 请求的数据模式

    elicit_type: 交互类型

    timeout: 超时时间

    metadata: 元数据

Returns:

    交互请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |
| `requested_schema` (可选) | `Optional[Dict[str, Any]]` | `None` |
| `elicit_type` (可选) | `Union[ElicitType, str]` | `ElicitType.REQUEST` |
| `timeout` (可选) | `float` | `300.0` |
| `metadata` (可选) | `Optional[Dict[str, Any]]` | `None` |

#### 返回

`ElicitRequest`

---

### `get_request(self: Any, request_id: str) -> Optional[ElicitRequest]`

`行号:325` `复杂度:低`

获取交互请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |

#### 返回

`Optional[ElicitRequest]`

---

### `submit_response(self: Any, response: ElicitResponse) -> bool`

`行号:330` `复杂度:中`

提交响应

Args:

    response: 交互响应

Returns:

    是否提交成功

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `response` | `ElicitResponse` | `-` |

#### 返回

`bool`

---

### `accept(self: Any, request_id: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool`

`行号:360` `复杂度:低`

接受请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |
| `value` | `Any` | `-` |
| `metadata` (可选) | `Optional[Dict[str, Any]]` | `None` |

#### 返回

`bool`

---

### `reject(self: Any, request_id: str, error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool`

`行号:375` `复杂度:低`

拒绝请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |
| `error` (可选) | `Optional[str]` | `None` |
| `metadata` (可选) | `Optional[Dict[str, Any]]` | `None` |

#### 返回

`bool`

---

### `cancel(self: Any, request_id: str) -> bool`

`行号:390` `复杂度:低`

取消请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |

#### 返回

`bool`

---

### `expire_requests(self: Any) -> int`

`行号:404` `复杂度:中`

使过期的请求过期

Returns:

    过期的请求数量

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`int`

---

### `get_pending_requests(self: Any, limit: int = 100) -> List[ElicitRequest]`

`行号:431` `复杂度:低`

获取待处理的请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `limit` (可选) | `int` | `100` |

#### 返回

`List[ElicitRequest]`

---

### `get_response(self: Any, request_id: str) -> Optional[ElicitResponse]`

`行号:441` `复杂度:低`

获取响应

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |

#### 返回

`Optional[ElicitResponse]`

---

### `get_pending_count(self: Any) -> int`

`行号:446` `复杂度:低`

获取待处理请求数量

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`int`

---

### `create_url_elicitation(self: Any, url: str, title: str, method: str = 'GET', headers: Optional[Dict[str, str]] = None, body: Optional[str] = None, timeout: float = 300.0, metadata: Optional[Dict[str, Any]] = None) -> URLElicitation`

`行号:451` `复杂度:低`

创建 URL 交互

Args:

    url: 目标 URL

    title: 标题

    method: HTTP 方法

    headers: HTTP 头

    body: 请求体

    timeout: 超时时间

    metadata: 元数据

Returns:

    URL 交互对象

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `url` | `str` | `-` |
| `title` | `str` | `-` |
| `method` (可选) | `str` | `'GET'` |
| `headers` (可选) | `Optional[Dict[str, str]]` | `None` |
| `body` (可选) | `Optional[str]` | `None` |
| `timeout` (可选) | `float` | `300.0` |
| `metadata` (可选) | `Optional[Dict[str, Any]]` | `None` |

#### 返回

`URLElicitation`

---

### `create_confirm_request(self: Any, message: str, title: Optional[str] = None, timeout: float = 300.0) -> ElicitRequest`

`行号:488` `复杂度:低`

创建确认请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |
| `title` (可选) | `Optional[str]` | `None` |
| `timeout` (可选) | `float` | `300.0` |

#### 返回

`ElicitRequest`

---

### `create_input_request(self: Any, message: str, field_name: str, field_type: str = 'string', required: bool = True, timeout: float = 300.0) -> ElicitRequest`

`行号:506` `复杂度:低`

创建输入请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |
| `field_name` | `str` | `-` |
| `field_type` (可选) | `str` | `'string'` |
| `required` (可选) | `bool` | `True` |
| `timeout` (可选) | `float` | `300.0` |

#### 返回

`ElicitRequest`

---

### `create_select_request(self: Any, message: str, options: List[str], timeout: float = 300.0) -> ElicitRequest`

`行号:526` `复杂度:低`

创建选择请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |
| `options` | `List[str]` | `-` |
| `timeout` (可选) | `float` | `300.0` |

#### 返回

`ElicitRequest`

---

### `get_stats(self: Any) -> Dict[str, Any]`

`行号:546` `复杂度:低`

获取统计信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

---

## Test Coverage

*No specific tests found for this module.*
