# protocol.elicitation

```include ../govmcp/protocol/elicitation.py
```

## Module Documentation

govmcp.protocol.elicitation — 用户交互支持 (MCP 2025.11)

提供安全带外用户交互功能，支持：

- 信息请求（ElicitRequest）

- URL Mode Elicitation

- 表单交互

- 安全提示确认

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| 563 | Low | - |

## Exported Functions

### `create_secure_prompt_request(message: str, resource_uri: Optional[str] = None, timeout: float = 300.0) -> ElicitRequest`

`Line:563` `Complexity:Low`

创建安全提示确认请求

Args:

    message: 消息内容

    resource_uri: 资源 URI

    timeout: 超时时间

Returns:

    交互请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `message` | `str` | `-` |
| `resource_uri` (Optional) | `Optional[str]` | `None` |
| `timeout` (Optional) | `float` | `300.0` |

#### Returns

`ElicitRequest`

---

## Exported Classes

### `ElicitType`

`Enum Class`  

`Line: 22`  

**Base Classes:** `str | Enum`

交互类型

---

### `ElicitStatus`

`Enum Class`  

`Line: 32`  

**Base Classes:** `str | Enum`

交互状态

---

### `ElicitRequest`

`Dataclass`  

`Line: 43`  

用户交互请求

用于向用户请求额外信息或确认。

#### Attributes

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

#### Decorators

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:67` `Complexity:Low`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'ElicitRequest'`

`Line:83` `Complexity:Low`

从字典创建

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`'ElicitRequest'`

---

---

### `ElicitResponse`

`Dataclass`  

`Line: 98`  

用户交互响应

#### Attributes

| Name | Type |
|:---|:---|
| `request_id` | `str` |
| `status` | `Union[ElicitStatus, str]` |
| `value` | `Optional[Any]` |
| `error` | `Optional[str]` |
| `responded_at` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

#### Decorators

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:112` `Complexity:Medium`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'ElicitResponse'`

`Line:129` `Complexity:Low`

从字典创建

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`'ElicitResponse'`

---

---

### `URLElicitation`

`Dataclass`  

`Line: 142`  

URL Mode Elicitation

通过 URL 方式向用户请求交互。

#### Attributes

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

#### Decorators

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:163` `Complexity:Medium`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'URLElicitation'`

`Line:182` `Complexity:Low`

从字典创建

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`'URLElicitation'`

---

---

### `ElicitationHandler`

`Line: 197`  

交互处理器接口

#### Decorators

### `handle_request(self: Any, request: ElicitRequest) -> ElicitResponse`

`Line:200` `Complexity:Low`

处理交互请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `ElicitRequest` | `-` |

#### Returns

`ElicitResponse`

---

### `can_handle(self: Any, request: ElicitRequest) -> bool`

`Line:207` `Complexity:Low`

检查是否可以处理

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `ElicitRequest` | `-` |

#### Returns

`bool`

---

---

### `ConsoleElicitationHandler`

`Line: 212`  

**Base Classes:** `ElicitationHandler`

控制台交互处理器

#### Attributes

| Name | Type |
|:---|:---|
| `input_func` | `Optional[Callable[[str], str]]` |

#### Decorators

### `handle_request(self: Any, request: ElicitRequest) -> ElicitResponse`

`Line:218` `Complexity:Low`

处理交互请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `ElicitRequest` | `-` |

#### Returns

`ElicitResponse`

---

### `_get_confirmation(self: Any, message: str) -> bool`

`Line:242` `Complexity:Low`

获取确认

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |

#### Returns

`bool`

---

### `_get_input(self: Any, message: str, schema: Dict[str, Any]) -> Any`

`Line:249` `Complexity:Low`

获取输入

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |
| `schema` | `Dict[str, Any]` | `-` |

#### Returns

`Any`

---

---

### `ElicitationManager`

`Line: 257`  

交互管理器

管理用户交互请求的生命周期。

#### Decorators

### `add_handler(self: Any, handler: ElicitationHandler) -> None`

`Line:272` `Complexity:Low`

添加处理器

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `handler` | `ElicitationHandler` | `-` |

#### Returns

`None`

---

### `set_default_handler(self: Any, handler: ElicitationHandler) -> None`

`Line:276` `Complexity:Low`

设置默认处理器

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `handler` | `ElicitationHandler` | `-` |

#### Returns

`None`

---

### `register_callback(self: Any, request_id: str, callback: Callable[[ElicitResponse], None]) -> None`

`Line:280` `Complexity:Low`

注册回调

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |
| `callback` | `Callable[[ElicitResponse], None]` | `-` |

#### Returns

`None`

---

### `create_request(self: Any, message: str, requested_schema: Optional[Dict[str, Any]] = None, elicit_type: Union[ElicitType, str] = ElicitType.REQUEST, timeout: float = 300.0, metadata: Optional[Dict[str, Any]] = None) -> ElicitRequest`

`Line:288` `Complexity:Low`

创建交互请求

Args:

    message: 消息内容

    requested_schema: 请求的数据模式

    elicit_type: 交互类型

    timeout: 超时时间

    metadata: 元数据

Returns:

    交互请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |
| `requested_schema` (Optional) | `Optional[Dict[str, Any]]` | `None` |
| `elicit_type` (Optional) | `Union[ElicitType, str]` | `ElicitType.REQUEST` |
| `timeout` (Optional) | `float` | `300.0` |
| `metadata` (Optional) | `Optional[Dict[str, Any]]` | `None` |

#### Returns

`ElicitRequest`

---

### `get_request(self: Any, request_id: str) -> Optional[ElicitRequest]`

`Line:325` `Complexity:Low`

获取交互请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |

#### Returns

`Optional[ElicitRequest]`

---

### `submit_response(self: Any, response: ElicitResponse) -> bool`

`Line:330` `Complexity:Medium`

提交响应

Args:

    response: 交互响应

Returns:

    是否提交成功

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `response` | `ElicitResponse` | `-` |

#### Returns

`bool`

---

### `accept(self: Any, request_id: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool`

`Line:360` `Complexity:Low`

接受请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |
| `value` | `Any` | `-` |
| `metadata` (Optional) | `Optional[Dict[str, Any]]` | `None` |

#### Returns

`bool`

---

### `reject(self: Any, request_id: str, error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool`

`Line:375` `Complexity:Low`

拒绝请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |
| `error` (Optional) | `Optional[str]` | `None` |
| `metadata` (Optional) | `Optional[Dict[str, Any]]` | `None` |

#### Returns

`bool`

---

### `cancel(self: Any, request_id: str) -> bool`

`Line:390` `Complexity:Low`

取消请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |

#### Returns

`bool`

---

### `expire_requests(self: Any) -> int`

`Line:404` `Complexity:Medium`

使过期的请求过期

Returns:

    过期的请求数量

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`int`

---

### `get_pending_requests(self: Any, limit: int = 100) -> List[ElicitRequest]`

`Line:431` `Complexity:Low`

获取待处理的请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `limit` (Optional) | `int` | `100` |

#### Returns

`List[ElicitRequest]`

---

### `get_response(self: Any, request_id: str) -> Optional[ElicitResponse]`

`Line:441` `Complexity:Low`

获取响应

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request_id` | `str` | `-` |

#### Returns

`Optional[ElicitResponse]`

---

### `get_pending_count(self: Any) -> int`

`Line:446` `Complexity:Low`

获取待处理请求数量

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`int`

---

### `create_url_elicitation(self: Any, url: str, title: str, method: str = 'GET', headers: Optional[Dict[str, str]] = None, body: Optional[str] = None, timeout: float = 300.0, metadata: Optional[Dict[str, Any]] = None) -> URLElicitation`

`Line:451` `Complexity:Low`

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

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `url` | `str` | `-` |
| `title` | `str` | `-` |
| `method` (Optional) | `str` | `'GET'` |
| `headers` (Optional) | `Optional[Dict[str, str]]` | `None` |
| `body` (Optional) | `Optional[str]` | `None` |
| `timeout` (Optional) | `float` | `300.0` |
| `metadata` (Optional) | `Optional[Dict[str, Any]]` | `None` |

#### Returns

`URLElicitation`

---

### `create_confirm_request(self: Any, message: str, title: Optional[str] = None, timeout: float = 300.0) -> ElicitRequest`

`Line:488` `Complexity:Low`

创建确认请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |
| `title` (Optional) | `Optional[str]` | `None` |
| `timeout` (Optional) | `float` | `300.0` |

#### Returns

`ElicitRequest`

---

### `create_input_request(self: Any, message: str, field_name: str, field_type: str = 'string', required: bool = True, timeout: float = 300.0) -> ElicitRequest`

`Line:506` `Complexity:Low`

创建输入请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |
| `field_name` | `str` | `-` |
| `field_type` (Optional) | `str` | `'string'` |
| `required` (Optional) | `bool` | `True` |
| `timeout` (Optional) | `float` | `300.0` |

#### Returns

`ElicitRequest`

---

### `create_select_request(self: Any, message: str, options: List[str], timeout: float = 300.0) -> ElicitRequest`

`Line:526` `Complexity:Low`

创建选择请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `str` | `-` |
| `options` | `List[str]` | `-` |
| `timeout` (Optional) | `float` | `300.0` |

#### Returns

`ElicitRequest`

---

### `get_stats(self: Any) -> Dict[str, Any]`

`Line:546` `Complexity:Low`

获取统计信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

---

## Test Coverage

*No specific tests found for this module.*
