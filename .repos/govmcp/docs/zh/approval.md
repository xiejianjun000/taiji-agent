# server.approval

```include ../govmcp/server/approval.py
```

## 模块文档

审批工作流模块 — 多级审批链、超时自动拒绝、审计记录关联。

设计原则:

- 多级审批链：按 approvers 顺序逐级审批

- 超时控制：全局超时，到期后根据 auto_approve_on_timeout 决定行为

- 审计关联：可关联 AuditChain 实例，审批动作自动写入审计记录

- 不可逆：approve/reject/skip 均为单向操作，已完成的步骤不可回退

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| 361 | 低 | - |
| 375 | 低 | - |

## 导出函数

### `create_single_approval(approver: str, timeout: float = 300) -> ApprovalFlow`

`行号:361` `复杂度:低`

创建单级审批流。

Args:

    approver: 审批人标识

    timeout: 超时时间（秒）

Returns:

    配置好的 ApprovalFlow 实例

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `approver` | `str` | `-` |
| `timeout` (可选) | `float` | `300` |

#### 返回

`ApprovalFlow`

---

### `create_multi_approval(approvers: List[str], timeout: float = 300) -> ApprovalFlow`

`行号:375` `复杂度:低`

创建多级审批流。

Args:

    approvers: 审批人列表（按审批顺序）

    timeout: 超时时间（秒）

Returns:

    配置好的 ApprovalFlow 实例

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `approvers` | `List[str]` | `-` |
| `timeout` (可选) | `float` | `300` |

#### 返回

`ApprovalFlow`

---

## 导出类

### `ApprovalStatus`

`枚举类`  

`行号: 17`  

**基类:** `Enum`

审批状态枚举

---

### `ApprovalStep`

`数据类`  

`行号: 28`  

单个审批步骤的数据记录

#### 属性

| Name | Type |
|:---|:---|
| `level` | `int` |
| `approver` | `str` |
| `status` | `ApprovalStatus` |
| `timestamp` | `float` |
| `comment` | `str` |

#### 装饰器

### `to_dict(self: Any) -> dict`

`行号:37` `复杂度:低`

序列化为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`dict`

---

---

### `ApprovalFlow`

`行号: 48`  

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

#### 属性

| Name | Type |
|:---|:---|
| `approvers` | `List[str]` |
| `timeout` | `float` |
| `auto_approve_on_timeout` | `bool` |
| `audit_chain` | `Any` |

#### 装饰器

### `_elapsed(self: Any) -> float`

`行号:109` `复杂度:低`

已流逝时间（秒）

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`float`

---

### `_is_timed_out(self: Any) -> bool`

`行号:113` `复杂度:低`

检查是否已超时

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `_current_step(self: Any) -> Optional[ApprovalStep]`

`行号:117` `复杂度:低`

获取当前待审批的步骤，若已完成则返回 None

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Optional[ApprovalStep]`

---

### `_handle_timeout(self: Any) -> Optional[ApprovalStatus]`

`行号:123` `复杂度:中`

处理超时情况。

若未超时或已无待审批步骤，返回 None。

若超时：

  - auto_approve_on_timeout=True  → 标记当前步骤为 APPROVED

  - auto_approve_on_timeout=False → 标记当前步骤为 TIMEOUT

返回应用的状态。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Optional[ApprovalStatus]`

---

### `_finalize_step(self: Any, step: ApprovalStep) -> None`

`行号:152` `复杂度:中`

完成当前步骤：推进 current_level，检查是否全部完成。

若审批被拒绝或超时（且非自动通过），整个流程终止。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `step` | `ApprovalStep` | `-` |

#### 返回

`None`

---

### `_record_audit(self: Any, step: ApprovalStep) -> None`

`行号:170` `复杂度:低`

向关联的审计链追加记录

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `step` | `ApprovalStep` | `-` |

#### 返回

`None`

---

### `approve(self: Any, approver: str, comment: str = '') -> ApprovalStatus`

`行号:188` `复杂度:中`

当前级别审批通过。

Args:

    approver: 审批人标识，必须匹配当前级别的审批人

    comment: 审批备注

Returns:

    当前步骤的最终状态

Raises:

    ValueError: 审批人不匹配当前级别

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `approver` | `str` | `-` |
| `comment` (可选) | `str` | `''` |

#### 返回

`ApprovalStatus`

---

### `reject(self: Any, approver: str, comment: str = '') -> ApprovalStatus`

`行号:224` `复杂度:中`

当前级别审批拒绝。

Args:

    approver: 审批人标识，必须匹配当前级别的审批人

    comment: 拒绝原因

Returns:

    当前步骤的最终状态

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `approver` | `str` | `-` |
| `comment` (可选) | `str` | `''` |

#### 返回

`ApprovalStatus`

---

### `skip(self: Any, comment: str = '') -> ApprovalStatus`

`行号:257` `复杂度:中`

跳过当前审批级别。

用于审批人不可用（请假、调岗等）时的应急处理。

跳过后推进到下一级别继续审批。

Args:

    comment: 跳过原因

Returns:

    当前步骤的最终状态

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `comment` (可选) | `str` | `''` |

#### 返回

`ApprovalStatus`

---

### `is_complete(self: Any) -> bool`

`行号:290` `复杂度:低`

审批流程是否已完成（无论通过与否）。

Returns:

    True 如果所有审批步骤均已处理或流程已终止

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `is_approved(self: Any) -> bool`

`行号:303` `复杂度:低`

审批是否全部通过。

Returns:

    True 如果所有级别均已通过（包括超时自动通过）

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `result(self: Any) -> ApprovalStatus`

`行号:316` `复杂度:中`

获取审批流程的最终状态。

- 全部通过 → APPROVED

- 被拒绝（含超时拒绝） → REJECTED

- 尚未完成 → PENDING

Returns:

    流程最终状态

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`ApprovalStatus`

---

### `to_dict_list(self: Any) -> List[dict]`

`行号:340` `复杂度:低`

将所有审批步骤序列化为字典列表。

Returns:

    审批步骤列表，每个元素为一个 dict

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`List[dict]`

---

---

## Test Coverage

*No specific tests found for this module.*
