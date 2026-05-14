# crypto.audit

```include ../govmcp/crypto/audit.py
```

## Module Documentation

不可篡改审计链 — SM3哈希链式防篡改

每条审计记录包含操作元数据，并通过SM3哈希链接到前一条记录。

任何对历史记录的修改都会破坏哈希链，可被 verify() 检测。

设计原则:

- 追加写入 (append-only)：无删除/修改接口

- 创世区块：第一条记录的 prev_hash = 64个'0'

- 篡改检测：遍历全链重新计算 current_hash 并与存储值比对

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `AuditEntry`

`Dataclass`  

`Line: 25`  

单条审计记录 — 不可篡改链上的一个区块

#### Attributes

| Name | Type |
|:---|:---|
| `id` | `int` |
| `timestamp` | `float` |
| `operation` | `str` |
| `operator` | `str` |
| `input_hash` | `str` |
| `output_hash` | `str` |
| `approval_status` | `str` |
| `prev_hash` | `str` |
| `current_hash` | `str` |

---

### `AuditChain`

`Line: 39`  

不可篡改审计链

基于SM3哈希的链式数据结构。每条新记录通过 current_hash 锁定

自身内容和前驱记录，形成防篡改链条。

Usage:

    chain = AuditChain()

    chain.add_entry("tool_call", "admin", b"input", b"output", "approved")

    chain.add_entry("resource_read", "user1", b"query", b"result", "approved")

    assert chain.verify()

    print(chain.export())

#### Decorators

### `add_entry(self: Any, operation: str, operator: str, input_data: bytes, output_data: bytes, approval_status: str = 'pending') -> AuditEntry`

`Line:57` `Complexity:Medium`

追加一条审计记录。

Args:

    operation: 操作类型 (如 'tool_call', 'resource_read', 'approval_granted')

    operator: 操作者标识

    input_data: 输入数据（原始字节）

    output_data: 输出数据（原始字节）

    approval_status: 审批状态 (pending/approved/rejected)

Returns:

    新创建的 AuditEntry

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `operation` | `str` | `-` |
| `operator` | `str` | `-` |
| `input_data` | `bytes` | `-` |
| `output_data` | `bytes` | `-` |
| `approval_status` (Optional) | `str` | `'pending'` |

#### Returns

`AuditEntry`

---

### `verify(self: Any) -> bool`

`Line:107` `Complexity:Medium`

验证整条审计链的完整性。

遍历所有记录，重新计算 current_hash 并与存储值比对。

任何篡改（修改数据或插入/删除记录）都会导致验证失败。

Returns:

    True 如果整条链未被篡改

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `to_dict_list(self: Any) -> List[dict]`

`Line:149` `Complexity:Low`

将审计链转换为字典列表，便于序列化。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`List[dict]`

---

### `export(self: Any, indent: int = 2) -> str`

`Line:166` `Complexity:Low`

导出审计链为JSON字符串。

Args:

    indent: JSON缩进空格数

Returns:

    格式化的JSON字符串

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `indent` (Optional) | `int` | `2` |

#### Returns

`str`

---

---

## Test Coverage

*No specific tests found for this module.*
