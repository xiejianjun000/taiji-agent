# models.adapters.others

```include ../govmcp/models/adapters/others.py
```

## Module Documentation

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

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `OthersAdapter`

`Line: 28`  

**Base Classes:** `LLMAdapter`

其他国产大模型适配器

统一处理商汤、360奇智、拓世AI、新华三望道、出门问问、书生·浦语、聆心智能、天翼云、联通AI等厂商。

Usage:

    config = ModelConfig(provider=LLMProvider.SENSECHAT, model_id="sensechat-5", ...)

    adapter = OthersAdapter(config)

    response = adapter.chat([{"role": "user", "content": "你好"}])

#### Attributes

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

#### Decorators

### `_build_headers(self: Any) -> Dict[str, str]`

`Line:44` `Complexity:Low`

构建请求头

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, str]`

---

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`Line:53` `Complexity:Low`

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

`Line:83` `Complexity:High`

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

`Line:124` `Complexity:Low`

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
