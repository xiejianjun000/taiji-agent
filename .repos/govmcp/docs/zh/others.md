# models.adapters.others

```include ../govmcp/models/adapters/others.py
```

## 模块文档

govmcp.models.adapters.others — 其他厂商适配器

支持:

- sensechat-5, sensechat-4 (商汤日日新)

- qizhi-chat (360奇智)

- tuoshai-chat (拓世AI)

- wandao-chat (新华三望道)

- wenda-chat (出门问问)

- internlm-chat, internlm2-chat (书生·浦语)

- mindchat (聆心智能)

- ctyun-chat (天翼云)

- unicom-chat (联通AI)

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| - | - | - |

## 导出类

### `OthersAdapter`

`行号: 28`  

**基类:** `LLMAdapter`

其他国产大模型适配器

统一处理商汤、360奇智、拓世AI、新华三望道、出门问问、书生·浦语、聆心智能、天翼云、联通AI等厂商。

Usage:

    config = ModelConfig(provider=LLMProvider.SENSECHAT, model_id="sensechat-5", ...)

    adapter = OthersAdapter(config)

    response = adapter.chat([{"role": "user", "content": "你好"}])

#### 属性

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

#### 装饰器

### `_build_headers(self: Any) -> Dict[str, str]`

`行号:44` `复杂度:低`

构建请求头

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, str]`

---

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`行号:53` `复杂度:低`

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

`行号:83` `复杂度:高`

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

`行号:124` `复杂度:低`

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
