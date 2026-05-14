# models.adapters.wenxin

```include ../govmcp/models/adapters/wenxin.py
```

## 模块文档

govmcp.models.adapters.wenxin — 百度文心一言适配器

支持 ernie-4.0, ernie-3.5, ernie-3.0, ernie-bot

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| - | - | - |

## 导出类

### `WenxinAdapter`

`行号: 20`  

**基类:** `LLMAdapter`

百度文心一言适配器

Usage:

    config = ModelConfig(provider=LLMProvider.WENXIN, model_id="ernie-4.0", ...)

    adapter = WenxinAdapter(config)

    response = adapter.chat([{"role": "user", "content": "你好"}])

#### 属性

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |
| `secret_key` | `Optional[str]` |

#### 装饰器

### `_get_access_token(self: Any) -> str`

`行号:39` `复杂度:中`

获取百度access_token

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`str`

---

### `_build_headers(self: Any) -> Dict[str, str]`

`行号:56` `复杂度:低`

构建请求头

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, str]`

---

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`行号:63` `复杂度:中`

发送对话请求

Args:

    messages: 消息列表

    **kwargs: 其他参数

Returns:

    回复文本

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

`行号:95` `复杂度:高`

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

`行号:137` `复杂度:中`

获取文本嵌入向量

Args:

    text: 待嵌入的文本

    **kwargs: 其他参数

Returns:

    嵌入向量

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `text` | `str` | `-` |
| `**kwargs` | `Any` | `-` |

#### 返回

`List[float]`

---

---

## Test Coverage

*No specific tests found for this module.*
