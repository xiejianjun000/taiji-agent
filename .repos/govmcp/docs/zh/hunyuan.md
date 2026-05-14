# models.adapters.hunyuan

```include ../govmcp/models/adapters/hunyuan.py
```

## 模块文档

govmcp.models.adapters.hunyuan — 腾讯混元适配器

支持 hunyuan-lite, hunyuan-pro, hunyuan-standard

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| - | - | - |

## 导出类

### `HunyuanAdapter`

`行号: 19`  

**基类:** `LLMAdapter`

腾讯混元大模型适配器

Usage:

    config = ModelConfig(provider=LLMProvider.HUNYUAN, model_id="hunyuan-pro", ...)

    adapter = HunyuanAdapter(config)

    response = adapter.chat([{"role": "user", "content": "你好"}])

#### 属性

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |
| `secret_id` | `Optional[str]` |
| `secret_key` | `Optional[str]` |

#### 装饰器

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`行号:36` `复杂度:中`

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

`行号:72` `复杂度:高`

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

`行号:119` `复杂度:中`

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
