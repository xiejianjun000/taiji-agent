# models.adapters.spark

```include ../govmcp/models/adapters/spark.py
```

## Module Documentation

govmcp.models.adapters.spark — 讯飞星火适配器

支持 spark-3.5, spark-4.0, spark-lite

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `SparkAdapter`

`Line: 24`  

**Base Classes:** `LLMAdapter`

讯飞星火大模型适配器

Usage:

    config = ModelConfig(provider=LLMProvider.SPARK, model_id="spark-3.5", ...)

    adapter = SparkAdapter(config)

    response = adapter.chat([{"role": "user", "content": "你好"}])

#### Attributes

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |
| `app_id` | `Optional[str]` |
| `api_key` | `Optional[str]` |
| `api_secret` | `Optional[str]` |

#### Decorators

### `_generate_auth_url(self: Any) -> str`

`Line:52` `Complexity:Medium`

生成讯飞星火鉴权URL

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`str`

---

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`Line:83` `Complexity:Medium`

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

`Line:131` `Complexity:High`

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

`Line:192` `Complexity:Low`

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

### `_format_messages(self: Any, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]`

`Line:208` `Complexity:Medium`

格式化消息为讯飞格式

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[Dict[str, str]]` | `-` |

#### Returns

`List[Dict[str, Any]]`

---

---

## Test Coverage

*No specific tests found for this module.*
