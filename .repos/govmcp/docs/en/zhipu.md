# models.adapters.zhipu

```include ../govmcp/models/adapters/zhipu.py
```

## Module Documentation

govmcp.models.adapters.zhipu — 智谱AI GLM适配器

支持 glm-4, glm-4-plus, glm-3-turbo, chatglm-6b, chatglm2-6b, chatglm3-6b

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `ZhipuAdapter`

`Line: 19`  

**Base Classes:** `LLMAdapter`

智谱AI GLM适配器

Usage:

    config = ModelConfig(provider=LLMProvider.ZHIPU, model_id="glm-4", ...)

    adapter = ZhipuAdapter(config)

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

`Line:40` `Complexity:Medium`

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

`Line:115` `Complexity:Medium`

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
