# models.adapters.base

```include ../govmcp/models/adapters/base.py
```

## 模块文档

govmcp.models.adapters.base — LLM适配器基类

定义统一的适配器接口，所有厂商适配器都应继承此类。

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| - | - | - |

## 导出类

### `LLMAdapter`

`行号: 16`  

**基类:** `ABC`

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

#### 属性

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |

#### 装饰器

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`行号:51` `复杂度:低`

发送对话请求

Args:

    messages: 消息列表，格式为 [{"role": "user", "content": "..."}, ...]

    **kwargs: 其他参数 (temperature, max_tokens, top_p, stream 等)

Returns:

    模型生成的回复文本

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[Dict[str, str]]` | `-` |
| `**kwargs` | `Any` | `-` |

#### 返回

`str`

---

### `stream_chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

`行号:69` `复杂度:低`

发送流式对话请求

Args:

    messages: 消息列表

    **kwargs: 其他参数

Yields:

    逐块返回的回复内容

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[Dict[str, str]]` | `-` |
| `**kwargs` | `Any` | `-` |

#### 返回

`Iterator[str]`

---

### `get_embedding(self: Any, text: str, ****kwargs) -> List[float]`

`行号:87` `复杂度:低`

获取文本嵌入向量

Args:

    text: 待嵌入的文本

    **kwargs: 其他参数

Returns:

    嵌入向量列表

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `text` | `str` | `-` |
| `**kwargs` | `Any` | `-` |

#### 返回

`List[float]`

---

### `format_messages(self: Any, system: Optional[str] = None, user: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]`

`行号:104` `复杂度:中`

格式化消息列表

Args:

    system: 系统提示

    user: 用户消息

    history: 历史消息

Returns:

    格式化的消息列表

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `system` (可选) | `Optional[str]` | `None` |
| `user` (可选) | `Optional[str]` | `None` |
| `history` (可选) | `Optional[List[Dict[str, str]]]` | `None` |

#### 返回

`List[Dict[str, str]]`

---

### `build_request_params(self: Any, messages: List[Dict[str, str]], ****kwargs) -> Dict[str, Any]`

`行号:134` `复杂度:中`

构建请求参数

Args:

    messages: 消息列表

    **kwargs: 其他参数

Returns:

    请求参数字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[Dict[str, str]]` | `-` |
| `**kwargs` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `supports_streaming(self: Any) -> bool`

`行号:177` `复杂度:低`

是否支持流式输出

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `supports_function_call(self: Any) -> bool`

`行号:181` `复杂度:低`

是否支持函数调用

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `supports_vision(self: Any) -> bool`

`行号:185` `复杂度:低`

是否支持视觉

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `supports_embedding(self: Any) -> bool`

`行号:189` `复杂度:低`

是否支持文本嵌入

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

---

## Test Coverage

*No specific tests found for this module.*
