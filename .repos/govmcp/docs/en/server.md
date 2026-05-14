# protocol.server

```include ../govmcp/protocol/server.py
```

## Module Documentation

govmcp.protocol.server — GovMCPServer

JSON-RPC 2.0 over stdio 协议层，叠加 govmcp 独有特性：

- SM4 加密传输层（可选，CBC 模式，PKCS7 填充）

- SM3 数据完整性校验（每条消息附带哈希）

- 信创模型注册（48 个国产 LLM）

- 审批工作流集成（预留接口）

- 多传输层支持（Stdio/WebSocket/HTTP/SSE）

兼容标准 MCP 的 initialize / tools/list / tools/call / resources/list / prompts/list 方法。

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `GovMCPServer`

`Line: 165`  

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

#### Attributes

| Name | Type |
|:---|:---|
| `name` | `str` |
| `version` | `str` |
| `crypto_enabled` | `bool` |
| `sm4_key` | `Optional[bytes]` |

#### Decorators

### `register_tool(self: Any, name: str, description: str, input_schema: Dict[str, Any], handler: Callable[..., Any]) -> None`

`Line:239` `Complexity:Low`

注册一个工具。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `name` | `str` | `-` |
| `description` | `str` | `-` |
| `input_schema` | `Dict[str, Any]` | `-` |
| `handler` | `Callable[..., Any]` | `-` |

#### Returns

`None`

---

### `register_resource(self: Any, uri: str, name: str, description: str, mime_type: str, handler: Callable[[str], Any]) -> None`

`Line:254` `Complexity:Low`

注册一个资源。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `uri` | `str` | `-` |
| `name` | `str` | `-` |
| `description` | `str` | `-` |
| `mime_type` | `str` | `-` |
| `handler` | `Callable[[str], Any]` | `-` |

#### Returns

`None`

---

### `register_prompt(self: Any, name: str, description: str, arguments: List[Dict[str, Any]], handler: Callable[..., Any]) -> None`

`Line:271` `Complexity:Low`

注册一个提示模板。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `name` | `str` | `-` |
| `description` | `str` | `-` |
| `arguments` | `List[Dict[str, Any]]` | `-` |
| `handler` | `Callable[..., Any]` | `-` |

#### Returns

`None`

---

### `tool(self: Any, name: str = None, description: str = , input_schema: Dict[str, Any])`

`Line:286` `Complexity:Low`

工具注册装饰器。@server.tool(...)

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `name` (Optional) | `str` | `None` |
| `description` (Optional) | `str` | `-` |
| `input_schema` (Optional) | `Dict[str, Any]` | `-` |

---

### `resource(self: Any, uri: str = None, name: str = , description: str = , mime_type: str = text/plain)`

`Line:303` `Complexity:Low`

资源注册装饰器。@server.resource(...)

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `uri` (Optional) | `str` | `None` |
| `name` (Optional) | `str` | `-` |
| `description` (Optional) | `str` | `-` |
| `mime_type` (Optional) | `str` | `text/plain` |

---

### `prompt(self: Any, name: str = None, description: str = , arguments: List[Dict[str, Any]])`

`Line:320` `Complexity:Low`

提示模板注册装饰器。@server.prompt(...)

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `name` (Optional) | `str` | `None` |
| `description` (Optional) | `str` | `-` |
| `arguments` (Optional) | `List[Dict[str, Any]]` | `-` |

---

### `register_model(self: Any, model_name: str) -> None`

`Line:336` `Complexity:Low`

注册一个额外的信创模型

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `model_name` | `str` | `-` |

#### Returns

`None`

---

### `set_approval_handler(self: Any, handler: Callable[[str, Dict[str, Any]], bool]) -> None`

`Line:341` `Complexity:Low`

设置审批处理器。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `handler` | `Callable[[str, Dict[str, Any]], bool]` | `-` |

#### Returns

`None`

---

### `_check_approval(self: Any, tool_name: str, params: Dict[str, Any]) -> bool`

`Line:345` `Complexity:Low`

检查工具调用是否需要审批。无处理器时默认放行。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `tool_name` | `str` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`bool`

---

### `_read_message(self: Any) -> Optional[Dict[str, Any]]`

`Line:354` `Complexity:Medium`

从 stdin 读取一行消息。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Optional[Dict[str, Any]]`

---

### `_write_message(self: Any, message: Dict[str, Any]) -> None`

`Line:373` `Complexity:Medium`

将消息写出到 stdout。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `Dict[str, Any]` | `-` |

#### Returns

`None`

---

### `_jsonrpc_error(self: Any, req_id: Any, code: int, message: str) -> Dict[str, Any]`

`Line:390` `Complexity:Low`

构造 JSON-RPC 2.0 错误响应

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `req_id` | `Any` | `-` |
| `code` | `int` | `-` |
| `message` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_jsonrpc_response(self: Any, req_id: Any, result: Any) -> Dict[str, Any]`

`Line:398` `Complexity:Low`

构造 JSON-RPC 2.0 成功响应

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `req_id` | `Any` | `-` |
| `result` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_handle_request(self: Any, request: Dict[str, Any]) -> Dict[str, Any]`

`Line:402` `Complexity:Low`

处理单个 JSON-RPC 请求并返回响应

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `request` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_dispatch(self: Any, method: str, params: Dict[str, Any]) -> Any`

`Line:414` `Complexity:Low`

JSON-RPC 方法路由

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `method` | `str` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Any`

---

### `_mcp_initialize(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:443` `Complexity:Low`

initialize — 初始化握手

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_tools_list(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:478` `Complexity:Low`

tools/list — 列出所有已注册工具

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_tools_call(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:491` `Complexity:Medium`

tools/call — 调用指定工具

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_resources_list(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:515` `Complexity:Low`

resources/list — 列出所有已注册资源

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_resources_read(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:529` `Complexity:Medium`

resources/read — 读取指定资源

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_prompts_list(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:551` `Complexity:Low`

prompts/list — 列出所有已注册提示模板

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_prompts_get(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:564` `Complexity:Low`

prompts/get — 获取提示模板内容

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_models_list(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:576` `Complexity:Low`

models/list — 列出信创模型（govmcp 扩展）

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_sm3_verify(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:580` `Complexity:Low`

sm3/verify — SM3 数据完整性验证（govmcp 扩展）

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_tasks_create(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:592` `Complexity:Low`

tasks/create — 创建异步任务

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_tasks_status(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:614` `Complexity:Low`

tasks/status — 获取任务状态

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_tasks_result(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:626` `Complexity:Low`

tasks/result — 获取任务结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_tasks_cancel(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:632` `Complexity:Low`

tasks/cancel — 取消任务

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_tasks_list(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:638` `Complexity:Low`

tasks/list — 列出任务

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_tasks_subscribe(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:658` `Complexity:Low`

tasks/subscribe — 订阅任务更新（SSE）

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_sampling_create_message(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:672` `Complexity:Low`

sampling/createMessage — 创建采样消息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_elicitation_create(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:678` `Complexity:Low`

elicitation/create — 创建用户交互请求

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_elicitation_respond(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:696` `Complexity:Low`

elicitation/respond — 响应用户交互

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_mcp_authorization_check(self: Any, params: Dict[str, Any]) -> Dict[str, Any]`

`Line:710` `Complexity:Low`

authorization/check — 检查授权

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `params` | `Dict[str, Any]` | `-` |

#### Returns

`Dict[str, Any]`

---

### `_verify_inbound_sm3(self: Any, message: Dict[str, Any]) -> bool`

`Line:724` `Complexity:Low`

验证入站消息的 SM3 完整性哈希。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `message` | `Dict[str, Any]` | `-` |

#### Returns

`bool`

---

### `run(self: Any) -> None`

`Line:734` `Complexity:Very High`

启动 stdio 消息循环。

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`None`

---

### `get_transport_info(self: Any) -> Dict[str, Any]`

`Line:916` `Complexity:Low`

获取传输层信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

---

## Type Aliases

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
