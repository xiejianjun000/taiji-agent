# protocol.tasks

```include ../govmcp/protocol/tasks.py
```

## 模块文档

govmcp.protocol.tasks — 异步任务支持 (MCP 2025.11)

提供异步任务生命周期管理，包括任务创建、状态追踪、结果获取和取消功能。

支持 SSE (Server-Sent Events) 实时推送任务状态变更。

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| 616 | 低 | - |

## 导出函数

### `create_sse_response(task_manager: TaskManager, task_ids: Optional[List[str]] = None, all_tasks: bool = False) -> Dict[str, Any]`

`行号:616` `复杂度:低`

创建 SSE 响应

Args:

    task_manager: 任务管理器

    task_ids: 任务ID列表

    all_tasks: 订阅所有任务

Returns:

    SSE 响应配置

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `task_manager` | `TaskManager` | `-` |
| `task_ids` (可选) | `Optional[List[str]]` | `None` |
| `all_tasks` (可选) | `bool` | `False` |

#### 返回

`Dict[str, Any]`

---

## 导出类

### `TaskStatus`

`枚举类`  

`行号: 22`  

**基类:** `str | Enum`

任务状态枚举

---

### `TaskNotFoundError`

`行号: 32`  

**基类:** `Exception`

任务不存在异常

---

### `TaskCancelError`

`行号: 38`  

**基类:** `Exception`

任务取消失败异常

---

### `TaskInfo`

`数据类`  

`行号: 45`  

任务信息数据类

#### 属性

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

#### 装饰器

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:61` `复杂度:中`

转换为字典格式

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'TaskInfo'`

`行号:85` `复杂度:低`

从字典创建

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`'TaskInfo'`

---

---

### `TaskSubscriber`

`行号: 106`  

任务订阅者（用于 SSE）

#### 属性

| Name | Type |
|:---|:---|
| `task_ids` | `Optional[Set[str]]` |

#### 装饰器

### `close(self: Any) -> None`

`行号:120` `复杂度:中`

关闭订阅

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`None`

---

---

### `TaskManager`

`行号: 140`  

异步任务管理器

负责管理异步任务的完整生命周期，支持：

- 任务创建和追踪

- 状态轮询和 SSE 订阅

- 任务取消和清理

- 超时控制

#### 属性

| Name | Type |
|:---|:---|
| `default_timeout` | `float` |

#### 装饰器

### `register_tool(self: Any, name: str, handler: Callable[..., Any]) -> None`

`行号:166` `复杂度:低`

注册工具处理器

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `name` | `str` | `-` |
| `handler` | `Callable[..., Any]` | `-` |

#### 返回

`None`

---

### `set_executor(self: Any, loop: asyncio.AbstractEventLoop) -> None`

`行号:170` `复杂度:低`

设置事件循环

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `loop` | `asyncio.AbstractEventLoop` | `-` |

#### 返回

`None`

---

### `_generate_task_id(self: Any) -> str`

`行号:174` `复杂度:低`

生成唯一任务ID

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`str`

---

### `create_task(self: Any, tool_name: str, arguments: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> str`

`行号:178` `复杂度:中`

创建异步任务

Args:

    tool_name: 工具名称

    arguments: 工具参数

    timeout: 超时时间（秒）

    metadata: 元数据

Returns:

    任务ID

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `tool_name` | `str` | `-` |
| `arguments` (可选) | `Optional[Dict[str, Any]]` | `None` |
| `timeout` (可选) | `Optional[float]` | `None` |
| `metadata` (可选) | `Optional[Dict[str, Any]]` | `None` |

#### 返回

`str`

---

### `execute_task_sync(self: Any, tool_name: str, arguments: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> str`

`行号:276` `复杂度:中`

同步执行任务（创建后立即执行）

Args:

    tool_name: 工具名称

    arguments: 工具参数

    timeout: 超时时间（秒）

Returns:

    任务ID

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `tool_name` | `str` | `-` |
| `arguments` (可选) | `Optional[Dict[str, Any]]` | `None` |
| `timeout` (可选) | `Optional[float]` | `None` |

#### 返回

`str`

---

### `get_task_status(self: Any, task_id: str) -> TaskStatus`

`行号:331` `复杂度:低`

获取任务状态

Args:

    task_id: 任务ID

Returns:

    任务状态

Raises:

    TaskNotFoundError: 任务不存在

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |

#### 返回

`TaskStatus`

---

### `get_task_info(self: Any, task_id: str) -> TaskInfo`

`行号:350` `复杂度:低`

获取完整任务信息

Args:

    task_id: 任务ID

Returns:

    任务信息

Raises:

    TaskNotFoundError: 任务不存在

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |

#### 返回

`TaskInfo`

---

### `get_task_result(self: Any, task_id: str) -> Any`

`行号:369` `复杂度:中`

获取任务结果

Args:

    task_id: 任务ID

Returns:

    任务结果

Raises:

    TaskNotFoundError: 任务不存在

    ValueError: 任务尚未完成

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |

#### 返回

`Any`

---

### `cancel_task(self: Any, task_id: str) -> bool`

`行号:396` `复杂度:中`

取消任务

Args:

    task_id: 任务ID

Returns:

    是否成功取消

Raises:

    TaskNotFoundError: 任务不存在

    TaskCancelError: 任务无法取消

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |

#### 返回

`bool`

---

### `list_tasks(self: Any, status: Optional[TaskStatus] = None, limit: int = 100, offset: int = 0) -> List[TaskInfo]`

`行号:424` `复杂度:低`

列出任务

Args:

    status: 按状态过滤

    limit: 返回数量限制

    offset: 跳过数量

Returns:

    任务列表

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `status` (可选) | `Optional[TaskStatus]` | `None` |
| `limit` (可选) | `int` | `100` |
| `offset` (可选) | `int` | `0` |

#### 返回

`List[TaskInfo]`

---

### `cleanup_completed_tasks(self: Any, max_age: float = 3600.0) -> int`

`行号:451` `复杂度:高`

清理已完成任务

Args:

    max_age: 最长保留时间（秒）

Returns:

    清理的任务数量

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `max_age` (可选) | `float` | `3600.0` |

#### 返回

`int`

---

### `subscribe(self: Any, task_id: Optional[str] = None, task_ids: Optional[Set[str]] = None) -> TaskSubscriber`

`行号:482` `复杂度:中`

订阅任务更新

Args:

    task_id: 特定任务ID

    task_ids: 多个任务ID

Returns:

    订阅者对象

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` (可选) | `Optional[str]` | `None` |
| `task_ids` (可选) | `Optional[Set[str]]` | `None` |

#### 返回

`TaskSubscriber`

---

### `unsubscribe(self: Any, subscriber: TaskSubscriber) -> None`

`行号:512` `复杂度:低`

取消订阅

Args:

    subscriber: 订阅者对象

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `subscriber` | `TaskSubscriber` | `-` |

#### 返回

`None`

---

### `_notify_subscribers(self: Any, task_id: str, event_type: str, task: TaskInfo) -> None`

`行号:526` `复杂度:中`

通知订阅者

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |
| `event_type` | `str` | `-` |
| `task` | `TaskInfo` | `-` |

#### 返回

`None`

---

### `update_progress(self: Any, task_id: str, progress: float) -> bool`

`行号:547` `复杂度:低`

更新任务进度

Args:

    task_id: 任务ID

    progress: 进度值 (0.0 - 1.0)

Returns:

    是否更新成功

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `task_id` | `str` | `-` |
| `progress` | `float` | `-` |

#### 返回

`bool`

---

### `get_task_stats(self: Any) -> Dict[str, Any]`

`行号:567` `复杂度:低`

获取任务统计信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

---

### `SSEHandler`

`行号: 586`  

SSE 事件处理器

#### 属性

| Name | Type |
|:---|:---|
| `task_manager` | `TaskManager` |

---

## Test Coverage

*No specific tests found for this module.*
