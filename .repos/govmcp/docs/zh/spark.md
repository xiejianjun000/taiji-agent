# models.adapters.spark

```include ../govmcp/models/adapters/spark.py
```

## 模块文档

govmcp.models.adapters.spark — 讯飞星火适配器

支持 spark-3.5, spark-4.0, spark-lite

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| - | - | - |

## 导出类

### `SparkAdapter`

`行号: 24`  

**基类:** `LLMAdapter`

讯飞星火大模型适配器

Usage:

    config = ModelConfig(provider=LLMProvider.SPARK, model_id="spark-3.5", ...)

    adapter = SparkAdapter(config)

    response = adapter.chat([{"role": "user", "content": "你好"}])

#### 属性

| Name | Type |
|:---|:---|
| `config` | `ModelConfig` |
| `app_id` | `Optional[str]` |
| `api_key` | `Optional[str]` |
| `api_secret` | `Optional[str]` |

#### 装饰器

### `_generate_auth_url(self: Any) -> str`

`行号:52` `复杂度:中`

生成讯飞星火鉴权URL

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`str`

---

### `chat(self: Any, messages: List[Dict[str, str]], ****kwargs) -> str`

`行号:83` `复杂度:中`

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

`行号:131` `复杂度:高`

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

`行号:192` `复杂度:低`

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

### `_format_messages(self: Any, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]`

`行号:208` `复杂度:中`

格式化消息为讯飞格式

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `messages` | `List[Dict[str, str]]` | `-` |

#### 返回

`List[Dict[str, Any]]`

---

---

## Test Coverage

*No specific tests found for this module.*
