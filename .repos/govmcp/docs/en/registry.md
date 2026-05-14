# models.registry

```include ../govmcp/models/registry.py
```

## Module Documentation

govmcp.models.registry — 模型注册表

提供 LLMProvider 枚举、ModelConfig 数据类和 ModelRegistry 类，

用于管理所有国产大模型的注册和查询。

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| 907 | Low | - |
| 915 | Low | - |
| 920 | Low | - |
| 925 | Low | - |
| 930 | Low | - |

## Exported Functions

### `get_default_registry() -> ModelRegistry`

`Line:907` `Complexity:Low`

获取默认模型注册表实例

#### Returns

`ModelRegistry`

---

### `register_model(provider: LLMProvider, model_id: str, config: ModelConfig) -> bool`

`Line:915` `Complexity:Low`

全局注册模型

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `provider` | `LLMProvider` | `-` |
| `model_id` | `str` | `-` |
| `config` | `ModelConfig` | `-` |

#### Returns

`bool`

---

### `get_model(model_id: str) -> Optional[ModelConfig]`

`Line:920` `Complexity:Low`

全局获取模型配置

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `model_id` | `str` | `-` |

#### Returns

`Optional[ModelConfig]`

---

### `list_models(provider: Optional[LLMProvider] = None) -> List[ModelConfig]`

`Line:925` `Complexity:Low`

全局列出模型

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `provider` (Optional) | `Optional[LLMProvider]` | `None` |

#### Returns

`List[ModelConfig]`

---

### `validate_model(model_id: str) -> bool`

`Line:930` `Complexity:Low`

全局验证模型

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `model_id` | `str` | `-` |

#### Returns

`bool`

---

## Exported Classes

### `LLMProvider`

`Enum Class`  

`Line: 19`  

**Base Classes:** `Enum`

国产大模型厂商枚举

#### Decorators

### `from_model_id(cls: Any, model_id: str) -> 'LLMProvider'`

`Line:45` `Complexity:Very High`

根据模型ID推断provider

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `model_id` | `str` | `-` |

#### Returns

`'LLMProvider'`

---

### `adapter_name(self: Any) -> str`

`Line:91` `Complexity:Low`

获取适配器模块名

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`str`

---

---

### `ModelConfig`

`Dataclass`  

`Line: 119`  

模型配置数据类

#### Attributes

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

#### Decorators

### `supports_streaming(self: Any) -> bool`

`Line:132` `Complexity:Low`

是否支持流式输出

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `supports_function_call(self: Any) -> bool`

`Line:136` `Complexity:Low`

是否支持函数调用

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `supports_vision(self: Any) -> bool`

`Line:140` `Complexity:Low`

是否支持视觉

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `supports_embedding(self: Any) -> bool`

`Line:144` `Complexity:Low`

是否支持文本嵌入

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

---

### `ModelRegistry`

`Line: 149`  

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

#### Attributes

| Name | Type |
|:---|:---|
| `_instance` | `Optional['ModelRegistry']` |
| `_models` | `Dict[str, ModelConfig]` |
| `_adapters` | `Dict[str, Any]` |

#### Decorators

### `_register_builtin_models(self: Any) -> None`

`Line:191` `Complexity:Low`

注册内置的48个国产大模型

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`None`

---

### `register_model(self: Any, provider: LLMProvider, model_id: str, config: ModelConfig) -> bool`

`Line:791` `Complexity:Low`

注册一个新模型

Args:

    provider: 模型所属厂商

    model_id: 模型ID

    config: 模型配置

Returns:

    是否注册成功 (ID不存在时返回True)

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `provider` | `LLMProvider` | `-` |
| `model_id` | `str` | `-` |
| `config` | `ModelConfig` | `-` |

#### Returns

`bool`

---

### `get_model(self: Any, model_id: str) -> Optional[ModelConfig]`

`Line:808` `Complexity:Low`

获取模型配置

Args:

    model_id: 模型ID

Returns:

    模型配置，不存在时返回None

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_id` | `str` | `-` |

#### Returns

`Optional[ModelConfig]`

---

### `list_models(self: Any, provider: Optional[LLMProvider] = None) -> List[ModelConfig]`

`Line:820` `Complexity:Low`

列出所有模型

Args:

    provider: 可选，按provider过滤

Returns:

    模型配置列表

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `provider` (Optional) | `Optional[LLMProvider]` | `None` |

#### Returns

`List[ModelConfig]`

---

### `validate_model(self: Any, model_id: str) -> bool`

`Line:834` `Complexity:Low`

验证模型是否已注册

Args:

    model_id: 模型ID

Returns:

    是否已注册

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_id` | `str` | `-` |

#### Returns

`bool`

---

### `get_adapter(self: Any, model_id: str) -> Optional[Any]`

`Line:846` `Complexity:Medium`

获取模型的适配器实例

Args:

    model_id: 模型ID

Returns:

    适配器实例，不存在时返回None

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_id` | `str` | `-` |

#### Returns

`Optional[Any]`

---

### `count(self: Any) -> int`

`Line:883` `Complexity:Low`

返回已注册模型数量

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`int`

---

### `get_providers(self: Any) -> List[LLMProvider]`

`Line:887` `Complexity:Low`

返回所有已使用的provider列表

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`List[LLMProvider]`

---

### `clear(self: Any) -> None`

`Line:891` `Complexity:Low`

清空注册表 (测试用)

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`None`

---

---

## Type Aliases

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
