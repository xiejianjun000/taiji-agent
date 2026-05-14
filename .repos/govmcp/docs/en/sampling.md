# protocol.sampling

```include ../govmcp/protocol/sampling.py
```

## Module Documentation

govmcp.protocol.sampling — 异步采样支持 (MCP 2025.11)

提供 LLM 采样能力，支持异步消息生成、采样参数配置和采样策略。

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| 515 | Low | - |

## Exported Functions

### `create_sampling_request(messages: List[Dict[str, Any]], temperature: float = 0.7, max_tokens: int = 4096, ****kwargs) -> SamplingCreateMessageRequest`

`Line:515` `Complexity:Low`

创建采样请求的便捷函数

Args:

    messages: 消息列表

    temperature: 温度参数

    max_tokens: 最大令牌数

    **kwargs: 其他参数

Returns:

    采样请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `messages` | `List[Dict[str, Any]]` | `-` |
| `temperature` (Optional) | `float` | `0.7` |
| `max_tokens` (Optional) | `int` | `4096` |
| `**kwargs` | `Any` | `-` |

#### Returns

`SamplingCreateMessageRequest`

---

## Exported Classes

### `Role`

`Enum Class`  

`Line: 20`  

**Base Classes:** `str | Enum`

消息角色

---

### `SamplingMessageRole`

`Enum Class`  

`Line: 28`  

**Base Classes:** `str | Enum`

采样消息角色 (MCP 2025.11)

---

### `SamplingMessage`

`Dataclass`  

`Line: 37`  

采样消息

#### Attributes

| Name | Type |
|:---|:---|
| `role` | `Union[Role, SamplingMessageRole, str]` |
| `content` | `str` |
| `timestamp` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

#### Decorators

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:49` `Complexity:Low`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'SamplingMessage'`

`Line:61` `Complexity:Low`

从字典创建

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`'SamplingMessage'`

---

---

### `SamplingParameters`

`Dataclass`  

`Line: 78`  

采样参数

#### Attributes

| Name | Type |
|:---|:---|
| `temperature` | `float` |
| `max_tokens` | `int` |
| `top_p` | `float` |
| `stop_sequences` | `Optional[List[str]]` |
| `presence_penalty` | `float` |
| `frequency_penalty` | `float` |
| `model` | `Optional[str]` |
| `system_prompt` | `Optional[str]` |
| `reasoning_effort` | `Optional[str]` |
| `metadata` | `Dict[str, Any]` |

#### Decorators

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:92` `Complexity:Medium`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'SamplingParameters'`

`Line:114` `Complexity:Low`

从字典创建

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`'SamplingParameters'`

---

---

### `SamplingCreateMessageRequest`

`Dataclass`  

`Line: 131`  

采样创建消息请求

#### Attributes

| Name | Type |
|:---|:---|
| `messages` | `List[SamplingMessage]` |
| `system_prompt` | `Optional[str]` |
| `temperature` | `float` |
| `max_tokens` | `int` |
| `stop_sequences` | `Optional[List[str]]` |
| `include_context` | `Optional[str]` |
| `thinking` | `Optional[Dict[str, Any]]` |

#### Decorators

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:150` `Complexity:Medium`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'SamplingCreateMessageRequest'`

`Line:170` `Complexity:Low`

从字典创建

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`'SamplingCreateMessageRequest'`

---

---

### `SamplingResponse`

`Dataclass`  

`Line: 188`  

采样响应

#### Attributes

| Name | Type |
|:---|:---|
| `content` | `str` |
| `model` | `str` |
| `role` | `str` |
| `done` | `bool` |
| `done_reason` | `Optional[str]` |
| `usage` | `Optional[Dict[str, int]]` |
| `thinking` | `Optional[str]` |
| `custom_id` | `Optional[str]` |
| `metadata` | `Dict[str, Any]` |

#### Decorators

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:201` `Complexity:Medium`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'SamplingResponse'`

`Line:222` `Complexity:Low`

从字典创建

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`'SamplingResponse'`

---

---

### `SamplingProvider`

`Line: 237`  

采样提供者接口

#### Decorators

### `sample(self: Any, messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

`Line:240` `Complexity:Low`

同步采样

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[SamplingMessage]` | `-` |
| `parameters` | `SamplingParameters` | `-` |

#### Returns

`SamplingResponse`

---

---

### `SamplingManager`

`Line: 257`  

采样管理器

管理 LLM 采样请求，支持多种模型和采样策略。

#### Decorators

### `register_provider(self: Any, model_name: str, provider: SamplingProvider) -> None`

`Line:270` `Complexity:Low`

注册采样提供者

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_name` | `str` | `-` |
| `provider` | `SamplingProvider` | `-` |

#### Returns

`None`

---

### `set_default_model(self: Any, model_name: str) -> None`

`Line:278` `Complexity:Low`

设置默认模型

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_name` | `str` | `-` |

#### Returns

`None`

---

### `add_hook(self: Any, hook: Callable[[str, Any], None]) -> None`

`Line:282` `Complexity:Low`

添加采样钩子

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `hook` | `Callable[[str, Any], None]` | `-` |

#### Returns

`None`

---

### `remove_hook(self: Any, hook: Callable[[str, Any], None]) -> None`

`Line:286` `Complexity:Low`

移除采样钩子

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `hook` | `Callable[[str, Any], None]` | `-` |

#### Returns

`None`

---

### `_notify_hooks(self: Any, event: str, data: Any) -> None`

`Line:291` `Complexity:Low`

通知钩子

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `event` | `str` | `-` |
| `data` | `Any` | `-` |

#### Returns

`None`

---

### `create_message(self: Any, request: SamplingCreateMessageRequest) -> SamplingResponse`

`Line:299` `Complexity:Medium`

创建采样消息（同步）

Args:

    request: 采样请求

Returns:

    采样响应

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `SamplingCreateMessageRequest` | `-` |

#### Returns

`SamplingResponse`

---

### `_default_sample(self: Any, messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

`Line:433` `Complexity:Low`

默认采样实现

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[SamplingMessage]` | `-` |
| `parameters` | `SamplingParameters` | `-` |

#### Returns

`SamplingResponse`

---

### `get_message_history(self: Any, limit: Optional[int] = None) -> List[SamplingMessage]`

`Line:446` `Complexity:Low`

获取消息历史

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `limit` (Optional) | `Optional[int]` | `None` |

#### Returns

`List[SamplingMessage]`

---

### `clear_history(self: Any) -> None`

`Line:455` `Complexity:Low`

清空消息历史

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`None`

---

### `get_stats(self: Any) -> Dict[str, Any]`

`Line:459` `Complexity:Low`

获取采样统计

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

---

### `EmbeddedSamplingProvider`

`Line: 474`  

**Base Classes:** `SamplingProvider`

嵌入式采样提供者

#### Attributes

| Name | Type |
|:---|:---|
| `model_id` | `str` |

#### Decorators

### `sample(self: Any, messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

`Line:480` `Complexity:Low`

执行采样

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[SamplingMessage]` | `-` |
| `parameters` | `SamplingParameters` | `-` |

#### Returns

`SamplingResponse`

---

### `_generate_content(self: Any, messages: List[SamplingMessage], parameters: SamplingParameters) -> str`

`Line:505` `Complexity:Low`

生成内容

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[SamplingMessage]` | `-` |
| `parameters` | `SamplingParameters` | `-` |

#### Returns

`str`

---

---

## Test Coverage

*No specific tests found for this module.*
