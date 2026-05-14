# protocol.server

```include ../govmcp/protocol/server.py
```

## 模块文档

govmcp.protocol.server — GovMCPServer

JSON-RPC 2.0 over stdio 协议层，叠加 govmcp 独有特性：

- SM4 加密传输层（可选，CBC 模式，PKCS7 填充）

- SM3 数据完整性校验（每条消息附带哈希）

- 信创模型注册（48 个国产 LLM）

- 审批工作流集成（预留接口）

- 多传输层支持（Stdio/WebSocket/HTTP/SSE）

兼容标准 MCP 的 initialize / tools/list / tools/call / resources/list / prompts/list 方法。

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| - | - | - |

## 导出类

### `GovMCPServer`

`行号: 165`  

GovMCPServer — 国产信创 MCP 协议服务器

实现 JSON-RPC 2.0，兼容标准 MCP 协议，

并叠加 govmcp 独有的 SM4 加密传输层和 SM3 数据完整性校验。

支持多种传输方式: Stdio, WebSocket, HTTP/SSE。

用法:

    server = GovMCPServer("my-gov-server", "1.0.0", crypto_enabled=True)

    @server.tool("greet", description="打招呼", input_schema={...})

    def greet(name: str) -> str:

        return f"你好, {name}!"

    server.run()  # 启动 stdio 消息循环

    # 或者启动 WebSocket 服务器:

    asyncio.run(server.run_websocket(host="0.0.0.0", port=8080))

    # 或者启动 HTTP 服务器:

    asyncio.run(server.run_http(host="0.0.0.0", port=8080))

#### 属性

| Name | Type |
|:---|:---|
| `name` | `str` |
| `version` | `str` |
| `crypto_enabled` | `bool` |
| `sm4_key` | `Optional[bytes]` |

#### 装饰器

### `register_tool(self: Any, name: str, description: str, input_schema: Dict[str, Any], handler: Callable[..., Any]) -> None`

`行号:239` `复杂度:低`

注册一个工具。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `name` | `str` | `-` |
| `description` | `str` | `-` |
| `input_schema` | `Dict[str, Any]` | `-` |
| `handler` | `Callable[..., Any]` | `-` |

#### 返回

`None`

---

### `register_resource(self: Any, uri: str, name: str, description: str, mime_type: str, handler: Callable[[str], Any]) -> None`

`行号:254` `复杂度:低`

注册一个资源。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `uri` | `str` | `-` |
| `name` | `str` | `-` |
| `description` | `str` | `-` |
| `mime_type` | `str` | `-` |
| `handler` | `Callable[[str], Any]` | `-` |

#### 返回

`None`

---

### `register_prompt(self: Any, name: str, description: str, arguments: List[Dict[str, Any]], handler: Callable[..., Any]) -> None`

`行号:271` `复杂度:低`

注册一个提示模板。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `name` | `str` | `-` |
| `description` | `str` | `-` |
| `arguments` | `List[Dict[str, Any]]` | `-` |
| `handler` | `Callable[..., Any]` | `-` |

#### 返回

`None`

---

### `tool(self: Any, name: str = None, description: str = , input_schema: Dict[str, Any])`

`行号:286` `复杂度:低`

工具注册装饰器。@server.tool(...)

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `name` (可选) | `str` | `None` |
| `description` (可选) | `str` | `-` |
| `input_schema` (可选) | `Dict[str, Any]` | `-` |

---

### `resource(self: Any, uri: str = None, name: str = , description: str = , mime_type: str = text/plain)`

`行号:303` `复杂度:低`

资源注册装饰器。@server.resource(...)

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `uri` (可选) | `str` | `None` |
| `name` (可选) | `str` | `-` |
| `description` (可选) | `str` | `-` |
| `mime_type` (可选) | `str` | `text/plain` |

---

### `prompt(self: Any, name: str = None, description: str = , arguments: List[Dict[str, Any]])`

`行号:320` `复杂度:低`

提示模板注册装饰器。@server.prompt(...)

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `name` (可选) | `str` | `None` |
| `description` (可选) | `str` | `-` |
| `arguments` (可选) | `List[Dict[str, Any]]` | `-` |

---

### `register_model(self: Any, model_name: str) -> None`

`行号:336` `复杂度:低`

注册一个额外的信创模型

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_name` | `str` | `-` |

#### 返回

`None`

---

### `set_approval_handler(self: Any, handler: Callable[[str, Dict[str, Any]], bool]) -> None`

`行号:341` `复杂度:低`

设置审批处理器。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `handler` | `Callable[[str, Dict[str, Any]], bool]` | `-` |

#### 返回

`None`

---

### `_check_approval(self: Any, tool_name: str, params: Dict[str, Any]) -> bool`

`行号:345` `复杂度:低`

检查工具调用是否需要审批。无处理器时默认放行。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `tool_name` | `str` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`bool`

---

### `_read_message(self: Any) -> Optional[Dict[str, Any]]`

`行号:354` `复杂度:中`

从 stdin 读取一行消息。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Optional[Dict[str, Any]]`

---

### `_write_message(self: Any, message: Dict[str, Any]) -> None`

`行号:373` `复杂度:中`

将消息写出到 stdout。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `Dict[str, Any]` | `-` |

#### 返回

`None`

---

### `_jsonrpc_error(self: Any, req_id: Any, code: int, message: str) -> Dict[str, Any]`

`行号:390` `复杂度:低`

构造 JSON-RPC 2.0 错误响应

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `req_id` | `Any` | `-` |
| `code` | `int` | `-` |
| `message` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_jsonrpc_response(self: Any, req_id: Any, result: Any) -> Dict[str, Any]`

`行号:398` `复杂度:低`

构造 JSON-RPC 2.0 成功响应

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `req_id` | `Any` | `-` |
| `result` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_handle_request(self: Any, request: Dict[str, Any]) -> Dict[str, Any]`

`行号:402` `复杂度:低`

处理单个 JSON-RPC 请求并返回响应

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_dispatch(self: Any, method: str, params: Dict[str, Any]) -> Any`

`行号:414` `复杂度:低`

JSON-RPC 方法路由

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `method` | `str` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Any`

---

### `_mcp_initialize(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:443` `复杂度:低`

initialize — 初始化握手

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_tools_list(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:478` `复杂度:低`

tools/list — 列出所有已注册工具

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_tools_call(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:491` `复杂度:中`

tools/call — 调用指定工具

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_resources_list(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:515` `复杂度:低`

resources/list — 列出所有已注册资源

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_resources_read(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:529` `复杂度:中`

resources/read — 读取指定资源

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_prompts_list(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:551` `复杂度:低`

prompts/list — 列出所有已注册提示模板

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_prompts_get(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:564` `复杂度:低`

prompts/get — 获取提示模板内容

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_models_list(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:576` `复杂度:低`

models/list — 列出信创模型（govmcp 扩展）

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_sm3_verify(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:580` `复杂度:低`

sm3/verify — SM3 数据完整性验证（govmcp 扩展）

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_tasks_create(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:592` `复杂度:低`

tasks/create — 创建异步任务

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_tasks_status(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:614` `复杂度:低`

tasks/status — 获取任务状态

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_tasks_result(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:626` `复杂度:低`

tasks/result — 获取任务结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_tasks_cancel(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:632` `复杂度:低`

tasks/cancel — 取消任务

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_tasks_list(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:638` `复杂度:低`

tasks/list — 列出任务

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_tasks_subscribe(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:658` `复杂度:低`

tasks/subscribe — 订阅任务更新（SSE）

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_sampling_create_message(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:672` `复杂度:低`

sampling/createMessage — 创建采样消息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_elicitation_create(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:678` `复杂度:低`

elicitation/create — 创建用户交互请求

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_elicitation_respond(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:696` `复杂度:低`

elicitation/respond — 响应用户交互

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_mcp_authorization_check(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`行号:710` `复杂度:低`

authorization/check — 检查授权

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### 返回

`Dict[str, Any]`

---

### `_verify_inbound_sm3(self: Any, message: Dict[str, Any]) -> bool`

`行号:724` `复杂度:低`

验证入站消息的 SM3 完整性哈希。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `Dict[str, Any]` | `-` |

#### 返回

`bool`

---

### `run(self: Any) -> None`

`行号:734` `复杂度:很高`

启动 stdio 消息循环。

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`None`

---

### `get_transport_info(self: Any) -> Dict[str, Any]`

`行号:916` `复杂度:低`

获取传输层信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

---

## 类型别名

### `XINCHUANG_MODELS`

**Type:** `List[str]`

---

## Test Coverage

| Test File |
|:---|
| `tests/tests/test_tasks.py` |
| `tests/tests/test_tasks.py` |
| `tests/tests/test_tasks.py` |
| `tests/tests/test_tasks.py` |
| `tests/tests/test_tasks.py` |
| `tests/tests/test_tasks.py` |
