# models.registry

```include ../govmcp/models/registry.py
```

## 模块文档

govmcp.models.registry — 模型注册表

提供 LLMProvider 枚举、ModelConfig 数据类和 ModelRegistry 类，

用于管理所有国产大模型的注册和查询。

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| 907 | 低 | - |
| 915 | 低 | - |
| 920 | 低 | - |
| 925 | 低 | - |
| 930 | 低 | - |

## 导出函数

### `get_default_registry() -> ModelRegistry`

`行号:907` `复杂度:低`

获取默认模型注册表实例

#### 返回

`ModelRegistry`

---

### `register_model(provider: LLMProvider, model_id: str, config: ModelConfig) -> bool`

`行号:915` `复杂度:低`

全局注册模型

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `provider` | `LLMProvider` | `-` |
| `model_id` | `str` | `-` |
| `config` | `ModelConfig` | `-` |

#### 返回

`bool`

---

### `get_model(model_id: str) -> Optional[ModelConfig]`

`行号:920` `复杂度:低`

全局获取模型配置

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `model_id` | `str` | `-` |

#### 返回

`Optional[ModelConfig]`

---

### `list_models(provider: Optional[LLMProvider] = None) -> List[ModelConfig]`

`行号:925` `复杂度:低`

全局列出模型

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `provider` (可选) | `Optional[LLMProvider]` | `None` |

#### 返回

`List[ModelConfig]`

---

### `validate_model(model_id: str) -> bool`

`行号:930` `复杂度:低`

全局验证模型

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `model_id` | `str` | `-` |

#### 返回

`bool`

---

## 导出类

### `LLMProvider`

`枚举类`  

`行号: 19`  

**基类:** `Enum`

国产大模型厂商枚举

#### 装饰器

### `from_model_id(cls: Any, model_id: str) -> 'LLMProvider'`

`行号:45` `复杂度:很高`

根据模型ID推断provider

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `model_id` | `str` | `-` |

#### 返回

`'LLMProvider'`

---

### `adapter_name(self: Any) -> str`

`行号:91` `复杂度:低`

获取适配器模块名

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`str`

---

---

### `ModelConfig`

`数据类`  

`行号: 119`  

模型配置数据类

#### 属性

| Name | Type |
|:---|:---|
| `provider` | `LLMProvider` |
| `model_id` | `str` |
| `api_base` | `str` |
| `capabilities` | `Dict[str, bool]` |
| `max_tokens` | `int` |
| `temperature` | `float` |
| `top_p` | `float` |
| `timeout` | `float` |
| `extra` | `Dict[str, Any]` |

#### 装饰器

### `supports_streaming(self: Any) -> bool`

`行号:132` `复杂度:低`

是否支持流式输出

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `supports_function_call(self: Any) -> bool`

`行号:136` `复杂度:低`

是否支持函数调用

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `supports_vision(self: Any) -> bool`

`行号:140` `复杂度:低`

是否支持视觉

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `supports_embedding(self: Any) -> bool`

`行号:144` `复杂度:低`

是否支持文本嵌入

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

---

### `ModelRegistry`

`行号: 149`  

模型注册表

管理所有国产大模型的配置和适配器实例。

Usage:

    registry = ModelRegistry()

    # 获取模型配置

    config = registry.get_model("ernie-4.0")

    # 获取适配器

    adapter = registry.get_adapter("ernie-4.0")

    # 调用chat

    response = adapter.chat([{"role": "user", "content": "你好"}])

    # 列出所有模型

    models = registry.list_models()

    # 按provider过滤

    qwen_models = registry.list_models(provider=LLMProvider.QWEN)

#### 属性

| Name | Type |
|:---|:---|
| `_instance` | `Optional['ModelRegistry']` |
| `_models` | `Dict[str, ModelConfig]` |
| `_adapters` | `Dict[str, Any]` |

#### 装饰器

### `_register_builtin_models(self: Any) -> None`

`行号:191` `复杂度:低`

注册内置的48个国产大模型

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`None`

---

### `register_model(self: Any, provider: LLMProvider, model_id: str, config: ModelConfig) -> bool`

`行号:791` `复杂度:低`

注册一个新模型

Args:

    provider: 模型所属厂商

    model_id: 模型ID

    config: 模型配置

Returns:

    是否注册成功 (ID不存在时返回True)

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `provider` | `LLMProvider` | `-` |
| `model_id` | `str` | `-` |
| `config` | `ModelConfig` | `-` |

#### 返回

`bool`

---

### `get_model(self: Any, model_id: str) -> Optional[ModelConfig]`

`行号:808` `复杂度:低`

获取模型配置

Args:

    model_id: 模型ID

Returns:

    模型配置，不存在时返回None

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_id` | `str` | `-` |

#### 返回

`Optional[ModelConfig]`

---

### `list_models(self: Any, provider: Optional[LLMProvider] = None) -> List[ModelConfig]`

`行号:820` `复杂度:低`

列出所有模型

Args:

    provider: 可选，按provider过滤

Returns:

    模型配置列表

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `provider` (可选) | `Optional[LLMProvider]` | `None` |

#### 返回

`List[ModelConfig]`

---

### `validate_model(self: Any, model_id: str) -> bool`

`行号:834` `复杂度:低`

验证模型是否已注册

Args:

    model_id: 模型ID

Returns:

    是否已注册

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_id` | `str` | `-` |

#### 返回

`bool`

---

### `get_adapter(self: Any, model_id: str) -> Optional[Any]`

`行号:846` `复杂度:中`

获取模型的适配器实例

Args:

    model_id: 模型ID

Returns:

    适配器实例，不存在时返回None

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_id` | `str` | `-` |

#### 返回

`Optional[Any]`

---

### `count(self: Any) -> int`

`行号:883` `复杂度:低`

返回已注册模型数量

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`int`

---

### `get_providers(self: Any) -> List[LLMProvider]`

`行号:887` `复杂度:低`

返回所有已使用的provider列表

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`List[LLMProvider]`

---

### `clear(self: Any) -> None`

`行号:891` `复杂度:低`

清空注册表 (测试用)

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`None`

---

---

## 类型别名

### `_default_registry`

**Type:** `Optional[ModelRegistry]`

---

## Test Coverage

| Test File |
|:---|
| `tests/tests/test_all.py` |
| `tests/tests/test_all.py` |
| `tests/tests/test_all.py` |
| `tests/tests/test_all.py` |
| `tests/tests/test_all.py` |
| `tests/tests/test_all.py` |
| `tests/tests/test_all.py` |
| `tests/tests/test_all.py` |
