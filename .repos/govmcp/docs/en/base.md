# models.adapters.base

```include ../govmcp/models/adapters/base.py
```

## Module Documentation

govmcp.models.adapters.base — LLM适配器基类

定义统一的适配器接口，所有厂商适配器都应继承此类。

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `LLMAdapter`

`Line: 16`  

**Base Classes:** `ABC`

LLM适配器基类

定义统一的接口规范，所有厂商适配器都应继承此类并实现：

- chat(): 发送对话请求

- stream_chat(): 流式对话请求

- get_embedding(): 获取文本嵌入

Usage:

    class MyAdapter(LLMAdapter):

        def chat(self, messages, **kwargs) -> str:

            # 实现chat逻辑

            pass

    adapter = MyAdapter(config)

    response = adapter.chat([{"role": "user", "content": "你好"}])

#### Attributes

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |

#### Decorators

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`Line:51` `Complexity:Low`

发送对话请求

Args:

    messages: 消息列表，格式为 [{"role": "user", "content": "..."}, ...]

    **kwargs: 其他参数 (temperature, max_tokens, top_p, stream 等)

Returns:

    模型生成的回复文本

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

`Line:69` `Complexity:Low`

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

`Line:87` `Complexity:Low`

获取文本嵌入向量

Args:

    text: 待嵌入的文本

    **kwargs: 其他参数

Returns:

    嵌入向量列表

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `text` | `str` | `-` |
| `**kwargs` | `Any` | `-` |

#### Returns

`List[float]`

---

### `format_messages(self: Any, system: Optional[str] = None, user: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]`

`Line:104` `Complexity:Medium`

格式化消息列表

Args:

    system: 系统提示

    user: 用户消息

    history: 历史消息

Returns:

    格式化的消息列表

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `system` (Optional) | `Optional[str]` | `None` |
| `user` (Optional) | `Optional[str]` | `None` |
| `history` (Optional) | `Optional[List[Dict[str, str]]]` | `None` |

#### Returns

`List[Dict[str, str]]`

---

### `build_request_params(self: Any, messages: List[Dict[str, str]], ****kwargs) -> Dict[str, Any]`

`Line:134` `Complexity:Medium`

构建请求参数

Args:

    messages: 消息列表

    **kwargs: 其他参数

Returns:

    请求参数字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[Dict[str, str]]` | `-` |
| `**kwargs` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `supports_streaming(self: Any) -> bool`

`Line:177` `Complexity:Low`

是否支持流式输出

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `supports_function_call(self: Any) -> bool`

`Line:181` `Complexity:Low`

是否支持函数调用

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `supports_vision(self: Any) -> bool`

`Line:185` `Complexity:Low`

是否支持视觉

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `supports_embedding(self: Any) -> bool`

`Line:189` `Complexity:Low`

是否支持文本嵌入

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

---

## Test Coverage

*No specific tests found for this module.*
