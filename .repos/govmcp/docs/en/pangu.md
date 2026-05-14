# models.adapters.pangu

```include ../govmcp/models/adapters/pangu.py
```

## Module Documentation

govmcp.models.adapters.pangu — 华为盘古适配器

支持 pangu-alpha, pangu-chat

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `PanguAdapter`

`Line: 19`  

**Base Classes:** `LLMAdapter`

华为盘古大模型适配器

Usage:

    config = ModelConfig(provider=LLMProvider.PANGU, model_id="pangu-chat", ...)

    adapter = PanguAdapter(config)

    response = adapter.chat([{"role": "user", "content": "你好"}])

#### Attributes

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

#### Decorators

### `_build_headers(self: Any) -> Dict[str, str]`

`Line:33` `Complexity:Low`

构建请求头

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, str]`

---

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`Line:40` `Complexity:Low`

发送对话请求

Args:

    messages: 消息列表

    **kwargs: 其他参数

Returns:

    回复文本

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[Dict[str, str]]` | `-` |
| `**kwargs` | `Any` | `-` |

#### Returns

`str`

---

### `stream_chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

`Line:70` `Complexity:High`

发送流式对话请求

Args:

    messages: 消息列表

    **kwargs: 其他参数

Yields:

    逐块返回的回复内容

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[Dict[str, str]]` | `-` |
| `**kwargs` | `Any` | `-` |

#### Returns

`Iterator[str]`

---

### `get_embedding(self: Any, text: str, ****kwargs) -> List[float]`

`Line:111` `Complexity:Low`

获取文本嵌入向量

Args:

    text: 待嵌入的文本

    **kwargs: 其他参数

Returns:

    嵌入向量

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `text` | `str` | `-` |
| `**kwargs` | `Any` | `-` |

#### Returns

`List[float]`

---

---

## Test Coverage

*No specific tests found for this module.*
