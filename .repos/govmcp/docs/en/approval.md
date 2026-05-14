# server.approval

```include ../govmcp/server/approval.py
```

## Module Documentation

审批工作流模块 — 多级审批链、超时自动拒绝、审计记录关联。

设计原则:

- 多级审批链：按 approvers 顺序逐级审批

- 超时控制：全局超时，到期后根据 auto_approve_on_timeout 决定行为

- 审计关联：可关联 AuditChain 实例，审批动作自动写入审计记录

- 不可逆：approve/reject/skip 均为单向操作，已完成的步骤不可回退

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| 361 | Low | - |
| 375 | Low | - |

## Exported Functions

### `create_single_approval(approver: str, timeout: float = 300) -> ApprovalFlow`

`Line:361` `Complexity:Low`

创建单级审批流。

Args:

    approver: 审批人标识

    timeout: 超时时间（秒）

Returns:

    配置好的 ApprovalFlow 实例

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `approver` | `str` | `-` |
| `timeout` (Optional) | `float` | `300` |

#### Returns

`ApprovalFlow`

---

### `create_multi_approval(approvers: List[str], timeout: float = 300) -> ApprovalFlow`

`Line:375` `Complexity:Low`

创建多级审批流。

Args:

    approvers: 审批人列表（按审批顺序）

    timeout: 超时时间（秒）

Returns:

    配置好的 ApprovalFlow 实例

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `approvers` | `List[str]` | `-` |
| `timeout` (Optional) | `float` | `300` |

#### Returns

`ApprovalFlow`

---

## Exported Classes

### `ApprovalStatus`

`Enum Class`  

`Line: 17`  

**Base Classes:** `Enum`

审批状态枚举

---

### `ApprovalStep`

`Dataclass`  

`Line: 28`  

单个审批步骤的数据记录

#### Attributes

| Name | Type |
|:---|:---|
| `level` | `int` |
| `approver` | `str` |
| `status` | `ApprovalStatus` |
| `timestamp` | `float` |
| `comment` | `str` |

#### Decorators

### `to_dict(self: Any) -> dict`

`Line:37` `Complexity:Low`

序列化为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`dict`

---

---

### `ApprovalFlow`

`Line: 48`  

多级审批工作流。

按 approvers 列表顺序逐级审批。支持全局超时控制，

超时后根据 auto_approve_on_timeout 标志自动通过或拒绝。

可选关联 AuditChain 实例，审批动作自动追加审计记录。

Usage:

    # 两级审批，5分钟超时

    flow = ApprovalFlow(["dept_head", "director"], timeout=300)

    # 第一级审批通过

    status = flow.approve("dept_head", "同意")

    assert status == ApprovalStatus.APPROVED

    # 第二级审批通过

    status = flow.approve("director")

    assert flow.is_approved()

    # 结果

    print(flow.result())        # ApprovalStatus.APPROVED

    print(flow.to_dict_list())  # 可序列化列表

#### Attributes

| Name | Type |
|:---|:---|
| `approvers` | `List[str]` |
| `timeout` | `float` |
| `auto_approve_on_timeout` | `bool` |
| `audit_chain` | `Any` |

#### Decorators

### `_elapsed(self: Any) -> float`

`Line:109` `Complexity:Low`

已流逝时间（秒）

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`float`

---

### `_is_timed_out(self: Any) -> bool`

`Line:113` `Complexity:Low`

检查是否已超时

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `_current_step(self: Any) -> Optional[ApprovalStep]`

`Line:117` `Complexity:Low`

获取当前待审批的步骤，若已完成则返回 None

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Optional[ApprovalStep]`

---

### `_handle_timeout(self: Any) -> Optional[ApprovalStatus]`

`Line:123` `Complexity:Medium`

处理超时情况。

若未超时或已无待审批步骤，返回 None。

若超时：

  - auto_approve_on_timeout=True  → 标记当前步骤为 APPROVED

  - auto_approve_on_timeout=False → 标记当前步骤为 TIMEOUT

返回应用的状态。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Optional[ApprovalStatus]`

---

### `_finalize_step(self: Any, step: ApprovalStep) -> None`

`Line:152` `Complexity:Medium`

完成当前步骤：推进 current_level，检查是否全部完成。

若审批被拒绝或超时（且非自动通过），整个流程终止。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `step` | `ApprovalStep` | `-` |

#### Returns

`None`

---

### `_record_audit(self: Any, step: ApprovalStep) -> None`

`Line:170` `Complexity:Low`

向关联的审计链追加记录

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `step` | `ApprovalStep` | `-` |

#### Returns

`None`

---

### `approve(self: Any, approver: str, comment: str = '') -> ApprovalStatus`

`Line:188` `Complexity:Medium`

当前级别审批通过。

Args:

    approver: 审批人标识，必须匹配当前级别的审批人

    comment: 审批备注

Returns:

    当前步骤的最终状态

Raises:

    ValueError: 审批人不匹配当前级别

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `approver` | `str` | `-` |
| `comment` (Optional) | `str` | `''` |

#### Returns

`ApprovalStatus`

---

### `reject(self: Any, approver: str, comment: str = '') -> ApprovalStatus`

`Line:224` `Complexity:Medium`

当前级别审批拒绝。

Args:

    approver: 审批人标识，必须匹配当前级别的审批人

    comment: 拒绝原因

Returns:

    当前步骤的最终状态

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `approver` | `str` | `-` |
| `comment` (Optional) | `str` | `''` |

#### Returns

`ApprovalStatus`

---

### `skip(self: Any, comment: str = '') -> ApprovalStatus`

`Line:257` `Complexity:Medium`

跳过当前审批级别。

用于审批人不可用（请假、调岗等）时的应急处理。

跳过后推进到下一级别继续审批。

Args:

    comment: 跳过原因

Returns:

    当前步骤的最终状态

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `comment` (Optional) | `str` | `''` |

#### Returns

`ApprovalStatus`

---

### `is_complete(self: Any) -> bool`

`Line:290` `Complexity:Low`

审批流程是否已完成（无论通过与否）。

Returns:

    True 如果所有审批步骤均已处理或流程已终止

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `is_approved(self: Any) -> bool`

`Line:303` `Complexity:Low`

审批是否全部通过。

Returns:

    True 如果所有级别均已通过（包括超时自动通过）

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `result(self: Any) -> ApprovalStatus`

`Line:316` `Complexity:Medium`

获取审批流程的最终状态。

- 全部通过 → APPROVED

- 被拒绝（含超时拒绝） → REJECTED

- 尚未完成 → PENDING

Returns:

    流程最终状态

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`ApprovalStatus`

---

### `to_dict_list(self: Any) -> List[dict]`

`Line:340` `Complexity:Low`

将所有审批步骤序列化为字典列表。

Returns:

    审批步骤列表，每个元素为一个 dict

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`List[dict]`

---

---

## Test Coverage

*No specific tests found for this module.*
