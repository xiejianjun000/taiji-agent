# protocol.sampling

```include ../govmcp/protocol/sampling.py
```

## 模块文档

govmcp.protocol.sampling — 异步采样支持 (MCP 2025.11)

提供 LLM 采样能力，支持异步消息生成、采样参数配置和采样策略。

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| 515 | 低 | - |

## 导出函数

### `create_sampling_request(messages: List[Dict[str, Any]], temperature: float = 0.7, max_tokens: int = 4096, ****kwargs) -> SamplingCreateMessageRequest`

`行号:515` `复杂度:低`

创建采样请求的便捷函数

Args:

    messages: 消息列表

    temperature: 温度参数

    max_tokens: 最大令牌数

    **kwargs: 其他参数

Returns:

    采样请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `messages` | `List[Dict[str, Any]]` | `-` |
| `temperature` (可选) | `float` | `0.7` |
| `max_tokens` (可选) | `int` | `4096` |
| `**kwargs` | `Any` | `-` |

#### 返回

`SamplingCreateMessageRequest`

---

## 导出类

### `Role`

`枚举类`  

`行号: 20`  

**基类:** `str | Enum`

消息角色

---

### `SamplingMessageRole`

`枚举类`  

`行号: 28`  

**基类:** `str | Enum`

采样消息角色 (MCP 2025.11)

---

### `SamplingMessage`

`数据类`  

`行号: 37`  

采样消息

#### 属性

| Name | Type |
|:---|:---|
| `role` | `Union[Role, SamplingMessageRole, str]` |
| `content` | `str` |
| `timestamp` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

#### 装饰器

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:49` `复杂度:低`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'SamplingMessage'`

`行号:61` `复杂度:低`

从字典创建

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`'SamplingMessage'`

---

---

### `SamplingParameters`

`数据类`  

`行号: 78`  

采样参数

#### 属性

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

#### 装饰器

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:92` `复杂度:中`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'SamplingParameters'`

`行号:114` `复杂度:低`

从字典创建

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`'SamplingParameters'`

---

---

### `SamplingCreateMessageRequest`

`数据类`  

`行号: 131`  

采样创建消息请求

#### 属性

| Name | Type |
|:---|:---|
| `messages` | `List[SamplingMessage]` |
| `system_prompt` | `Optional[str]` |
| `temperature` | `float` |
| `max_tokens` | `int` |
| `stop_sequences` | `Optional[List[str]]` |
| `include_context` | `Optional[str]` |
| `thinking` | `Optional[Dict[str, Any]]` |

#### 装饰器

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:150` `复杂度:中`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'SamplingCreateMessageRequest'`

`行号:170` `复杂度:低`

从字典创建

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`'SamplingCreateMessageRequest'`

---

---

### `SamplingResponse`

`数据类`  

`行号: 188`  

采样响应

#### 属性

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

#### 装饰器

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:201` `复杂度:中`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'SamplingResponse'`

`行号:222` `复杂度:低`

从字典创建

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`'SamplingResponse'`

---

---

### `SamplingProvider`

`行号: 237`  

采样提供者接口

#### 装饰器

### `sample(self: Any, messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

`行号:240` `复杂度:低`

同步采样

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[SamplingMessage]` | `-` |
| `parameters` | `SamplingParameters` | `-` |

#### 返回

`SamplingResponse`

---

---

### `SamplingManager`

`行号: 257`  

采样管理器

管理 LLM 采样请求，支持多种模型和采样策略。

#### 装饰器

### `register_provider(self: Any, model_name: str, provider: SamplingProvider) -> None`

`行号:270` `复杂度:低`

注册采样提供者

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_name` | `str` | `-` |
| `provider` | `SamplingProvider` | `-` |

#### 返回

`None`

---

### `set_default_model(self: Any, model_name: str) -> None`

`行号:278` `复杂度:低`

设置默认模型

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_name` | `str` | `-` |

#### 返回

`None`

---

### `add_hook(self: Any, hook: Callable[[str, Any], None]) -> None`

`行号:282` `复杂度:低`

添加采样钩子

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `hook` | `Callable[[str, Any], None]` | `-` |

#### 返回

`None`

---

### `remove_hook(self: Any, hook: Callable[[str, Any], None]) -> None`

`行号:286` `复杂度:低`

移除采样钩子

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `hook` | `Callable[[str, Any], None]` | `-` |

#### 返回

`None`

---

### `_notify_hooks(self: Any, event: str, data: Any) -> None`

`行号:291` `复杂度:低`

通知钩子

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `event` | `str` | `-` |
| `data` | `Any` | `-` |

#### 返回

`None`

---

### `create_message(self: Any, request: SamplingCreateMessageRequest) -> SamplingResponse`

`行号:299` `复杂度:中`

创建采样消息（同步）

Args:

    request: 采样请求

Returns:

    采样响应

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `SamplingCreateMessageRequest` | `-` |

#### 返回

`SamplingResponse`

---

### `_default_sample(self: Any, messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

`行号:433` `复杂度:低`

默认采样实现

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[SamplingMessage]` | `-` |
| `parameters` | `SamplingParameters` | `-` |

#### 返回

`SamplingResponse`

---

### `get_message_history(self: Any, limit: Optional[int] = None) -> List[SamplingMessage]`

`行号:446` `复杂度:低`

获取消息历史

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `limit` (可选) | `Optional[int]` | `None` |

#### 返回

`List[SamplingMessage]`

---

### `clear_history(self: Any) -> None`

`行号:455` `复杂度:低`

清空消息历史

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`None`

---

### `get_stats(self: Any) -> Dict[str, Any]`

`行号:459` `复杂度:低`

获取采样统计

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

---

### `EmbeddedSamplingProvider`

`行号: 474`  

**基类:** `SamplingProvider`

嵌入式采样提供者

#### 属性

| Name | Type |
|:---|:---|
| `model_id` | `str` |

#### 装饰器

### `sample(self: Any, messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

`行号:480` `复杂度:低`

执行采样

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[SamplingMessage]` | `-` |
| `parameters` | `SamplingParameters` | `-` |

#### 返回

`SamplingResponse`

---

### `_generate_content(self: Any, messages: List[SamplingMessage], parameters: SamplingParameters) -> str`

`行号:505` `复杂度:低`

生成内容

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[SamplingMessage]` | `-` |
| `parameters` | `SamplingParameters` | `-` |

#### 返回

`str`

---

---

## Test Coverage

*No specific tests found for this module.*
