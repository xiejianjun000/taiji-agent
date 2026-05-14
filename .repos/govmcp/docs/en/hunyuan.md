# models.adapters.hunyuan

```include ../govmcp/models/adapters/hunyuan.py
```

## Module Documentation

govmcp.models.adapters.hunyuan — 腾讯混元适配器

支持 hunyuan-lite, hunyuan-pro, hunyuan-standard

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `HunyuanAdapter`

`Line: 19`  

**Base Classes:** `LLMAdapter`

腾讯混元大模型适配器

Usage:

    config = ModelConfig(provider=LLMProvider.HUNYUAN, model_id="hunyuan-pro", ...)

    adapter = HunyuanAdapter(config)

    response = adapter.chat([{"role": "user", "content": "你好"}])

#### Attributes

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |
| `secret_id` | `Optional[str]` |
| `secret_key` | `Optional[str]` |

#### Decorators

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`Line:36` `Complexity:Medium`

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

`Line:72` `Complexity:High`

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

`Line:119` `Complexity:Medium`

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
