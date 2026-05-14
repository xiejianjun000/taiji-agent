# models.adapters.wenxin

```include ../govmcp/models/adapters/wenxin.py
```

## Module Documentation

govmcp.models.adapters.wenxin — 百度文心一言适配器

支持 ernie-4.0, ernie-3.5, ernie-3.0, ernie-bot

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `WenxinAdapter`

`Line: 20`  

**Base Classes:** `LLMAdapter`

百度文心一言适配器

Usage:

    config = ModelConfig(provider=LLMProvider.WENXIN, model_id="ernie-4.0", ...)

    adapter = WenxinAdapter(config)

    response = adapter.chat([{"role": "user", "content": "你好"}])

#### Attributes

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |
| `secret_key` | `Optional[str]` |

#### Decorators

### `_get_access_token(self: Any) -> str`

`Line:39` `Complexity:Medium`

获取百度access_token

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`str`

---

### `_build_headers(self: Any) -> Dict[str, str]`

`Line:56` `Complexity:Low`

构建请求头

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, str]`

---

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`Line:63` `Complexity:Medium`

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

`Line:95` `Complexity:High`

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

`Line:137` `Complexity:Medium`

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
