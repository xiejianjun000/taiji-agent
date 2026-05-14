# protocol.tasks

```include ../govmcp/protocol/tasks.py
```

## Module Documentation

govmcp.protocol.tasks — 异步任务支持 (MCP 2025.11)

提供异步任务生命周期管理，包括任务创建、状态追踪、结果获取和取消功能。

支持 SSE (Server-Sent Events) 实时推送任务状态变更。

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| 616 | Low | - |

## Exported Functions

### `create_sse_response(task_manager: TaskManager, task_ids: Optional[List[str]] = None, all_tasks: bool = False) -> Dict[str, Any]`

`Line:616` `Complexity:Low`

创建 SSE 响应

Args:

    task_manager: 任务管理器

    task_ids: 任务ID列表

    all_tasks: 订阅所有任务

Returns:

    SSE 响应配置

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `task_manager` | `TaskManager` | `-` |
| `task_ids` (Optional) | `Optional[List[str]]` | `None` |
| `all_tasks` (Optional) | `bool` | `False` |

#### Returns

`Dict[str, Any]`

---

## Exported Classes

### `TaskStatus`

`Enum Class`  

`Line: 22`  

**Base Classes:** `str | Enum`

任务状态枚举

---

### `TaskNotFoundError`

`Line: 32`  

**Base Classes:** `Exception`

任务不存在异常

---

### `TaskCancelError`

`Line: 38`  

**Base Classes:** `Exception`

任务取消失败异常

---

### `TaskInfo`

`Dataclass`  

`Line: 45`  

任务信息数据类

#### Attributes

| Name | Type |
|:---|:---|
| `id` | `str` |
| `status` | `TaskStatus` |
| `tool_name` | `str` |
| `arguments` | `Dict[str, Any]` |
| `progress` | `float` |
| `result` | `Optional[Any]` |
| `error` | `Optional[str]` |
| `created_at` | `float` |
| `started_at` | `Optional[float]` |
| `completed_at` | `Optional[float]` |
| `timeout` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

#### Decorators

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:61` `Complexity:Medium`

转换为字典格式

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'TaskInfo'`

`Line:85` `Complexity:Low`

从字典创建

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`'TaskInfo'`

---

---

### `TaskSubscriber`

`Line: 106`  

任务订阅者（用于 SSE）

#### Attributes

| Name | Type |
|:---|:---|
| `task_ids` | `Optional[Set[str]]` |

#### Decorators

### `close(self: Any) -> None`

`Line:120` `Complexity:Medium`

关闭订阅

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`None`

---

---

### `TaskManager`

`Line: 140`  

异步任务管理器

负责管理异步任务的完整生命周期，支持：

- 任务创建和追踪

- 状态轮询和 SSE 订阅

- 任务取消和清理

- 超时控制

#### Attributes

| Name | Type |
|:---|:---|
| `default_timeout` | `float` |

#### Decorators

### `register_tool(self: Any, name: str, handler: Callable[..., Any]) -> None`

`Line:166` `Complexity:Low`

注册工具处理器

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `name` | `str` | `-` |
| `handler` | `Callable[..., Any]` | `-` |

#### Returns

`None`

---

### `set_executor(self: Any, loop: asyncio.AbstractEventLoop) -> None`

`Line:170` `Complexity:Low`

设置事件循环

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `loop` | `asyncio.AbstractEventLoop` | `-` |

#### Returns

`None`

---

### `_generate_task_id(self: Any) -> str`

`Line:174` `Complexity:Low`

生成唯一任务ID

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`str`

---

### `create_task(self: Any, tool_name: str, arguments: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> str`

`Line:178` `Complexity:Medium`

创建异步任务

Args:

    tool_name: 工具名称

    arguments: 工具参数

    timeout: 超时时间（秒）

    metadata: 元数据

Returns:

    任务ID

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `tool_name` | `str` | `-` |
| `arguments` (Optional) | `Optional[Dict[str, Any]]` | `None` |
| `timeout` (Optional) | `Optional[float]` | `None` |
| `metadata` (Optional) | `Optional[Dict[str, Any]]` | `None` |

#### Returns

`str`

---

### `execute_task_sync(self: Any, tool_name: str, arguments: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> str`

`Line:276` `Complexity:Medium`

同步执行任务（创建后立即执行）

Args:

    tool_name: 工具名称

    arguments: 工具参数

    timeout: 超时时间（秒）

Returns:

    任务ID

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `tool_name` | `str` | `-` |
| `arguments` (Optional) | `Optional[Dict[str, Any]]` | `None` |
| `timeout` (Optional) | `Optional[float]` | `None` |

#### Returns

`str`

---

### `get_task_status(self: Any, task_id: str) -> TaskStatus`

`Line:331` `Complexity:Low`

获取任务状态

Args:

    task_id: 任务ID

Returns:

    任务状态

Raises:

    TaskNotFoundError: 任务不存在

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |

#### Returns

`TaskStatus`

---

### `get_task_info(self: Any, task_id: str) -> TaskInfo`

`Line:350` `Complexity:Low`

获取完整任务信息

Args:

    task_id: 任务ID

Returns:

    任务信息

Raises:

    TaskNotFoundError: 任务不存在

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |

#### Returns

`TaskInfo`

---

### `get_task_result(self: Any, task_id: str) -> Any`

`Line:369` `Complexity:Medium`

获取任务结果

Args:

    task_id: 任务ID

Returns:

    任务结果

Raises:

    TaskNotFoundError: 任务不存在

    ValueError: 任务尚未完成

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |

#### Returns

`Any`

---

### `cancel_task(self: Any, task_id: str) -> bool`

`Line:396` `Complexity:Medium`

取消任务

Args:

    task_id: 任务ID

Returns:

    是否成功取消

Raises:

    TaskNotFoundError: 任务不存在

    TaskCancelError: 任务无法取消

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |

#### Returns

`bool`

---

### `list_tasks(self: Any, status: Optional[TaskStatus] = None, limit: int = 100, offset: int = 0) -> List[TaskInfo]`

`Line:424` `Complexity:Low`

列出任务

Args:

    status: 按状态过滤

    limit: 返回数量限制

    offset: 跳过数量

Returns:

    任务列表

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `status` (Optional) | `Optional[TaskStatus]` | `None` |
| `limit` (Optional) | `int` | `100` |
| `offset` (Optional) | `int` | `0` |

#### Returns

`List[TaskInfo]`

---

### `cleanup_completed_tasks(self: Any, max_age: float = 3600.0) -> int`

`Line:451` `Complexity:High`

清理已完成任务

Args:

    max_age: 最长保留时间（秒）

Returns:

    清理的任务数量

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `max_age` (Optional) | `float` | `3600.0` |

#### Returns

`int`

---

### `subscribe(self: Any, task_id: Optional[str] = None, task_ids: Optional[Set[str]] = None) -> TaskSubscriber`

`Line:482` `Complexity:Medium`

订阅任务更新

Args:

    task_id: 特定任务ID

    task_ids: 多个任务ID

Returns:

    订阅者对象

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` (Optional) | `Optional[str]` | `None` |
| `task_ids` (Optional) | `Optional[Set[str]]` | `None` |

#### Returns

`TaskSubscriber`

---

### `unsubscribe(self: Any, subscriber: TaskSubscriber) -> None`

`Line:512` `Complexity:Low`

取消订阅

Args:

    subscriber: 订阅者对象

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `subscriber` | `TaskSubscriber` | `-` |

#### Returns

`None`

---

### `_notify_subscribers(self: Any, task_id: str, event_type: str, task: TaskInfo) -> None`

`Line:526` `Complexity:Medium`

通知订阅者

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |
| `event_type` | `str` | `-` |
| `task` | `TaskInfo` | `-` |

#### Returns

`None`

---

### `update_progress(self: Any, task_id: str, progress: float) -> bool`

`Line:547` `Complexity:Low`

更新任务进度

Args:

    task_id: 任务ID

    progress: 进度值 (0.0 - 1.0)

Returns:

    是否更新成功

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |
| `progress` | `float` | `-` |

#### Returns

`bool`

---

### `get_task_stats(self: Any) -> Dict[str, Any]`

`Line:567` `Complexity:Low`

获取任务统计信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

---

### `SSEHandler`

`Line: 586`  

SSE 事件处理器

#### Attributes

| Name | Type |
|:---|:---|
| `task_manager` | `TaskManager` |

---

## Test Coverage

*No specific tests found for this module.*
