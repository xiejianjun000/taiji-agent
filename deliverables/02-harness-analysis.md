# Harness (cgast/harness) 架构分析报告

> 分析日期：2026-05-14
> 分析范围：packages/core/src/, packages/server/src/ws.ts, plugins/sandbox/, packages/desktop/

---

## 目录

1. [EventBus 能否直接作为 Taiji Agent 的事件中枢？](#1-eventbus-能否直接作为-taiji-agent-的事件中枢)
2. [Plugin 接口需要哪些扩展才能支持 Taiji Verify 和 GovMCP？](#2-plugin-接口需要哪些扩展才能支持-taiji-verify-和-govmcp)
3. [Agent Loop 如何替换 LLM Provider 为 Hermes Agent？](#3-agent-loop-如何替换-llm-provider-为-hermes-agent)
4. [TypeScript 和 Python 互操作的最佳方案是什么？](#4-typescript-和-python-互操作的最佳方案是什么)
5. [流式响应如何处理？](#5-流式响应如何处理)
6. [Human-in-the-Loop 如何与政务审批工作流对接？](#6-human-in-the-loop-如何与政务审批工作流对接)

---

## 1. EventBus 能否直接作为 Taiji Agent 的事件中枢？

### 1.1 当前事件类型列表

事件类型定义在 `packages/core/src/events/events.ts`，共 **37 个事件**，按命名空间分组：

| 命名空间 | 事件 | 可修改 | 说明 |
|----------|------|--------|------|
| **agent:** | `agent:start`, `agent:end`, `agent:error` | start 可修改 | Agent 生命周期 |
| **loop:** | `loop:iteration_start`, `loop:iteration_end` | iteration_start 可修改 | Agent Loop 迭代 |
| **prompt:** | `prompt:assemble` | 可修改 | Prompt 组装 |
| **llm:** | `llm:request`, `llm:chunk`, `llm:response`, `llm:error` | request、error 可修改 | LLM 请求/响应 |
| **tool:** | `tool:request`, `tool:start`, `tool:result`, `tool:error`, `tool:register`, `tool:unregister` | request、result 可修改 | 工具调用 |
| **state:** | `state:change` | 不可修改 | 状态变更 |
| **user:** | `user:input`, `user:interrupt`, `user:confirm` | input 可修改 | 用户输入 |
| **skill:** | `skill:activate`, `skill:deactivate` | 不可修改 | 技能激活 |
| **feedback:** | `feedback:request`, `feedback:response`, `feedback:timeout`, `feedback:cancel` | request 可修改 | Human-in-the-Loop |
| **heartbeat:** | `heartbeat:before`, `heartbeat:after`, `heartbeat:skip` | before 可修改 | 心跳监控 |

**可修改事件**（`MODIFIABLE_EVENTS`）：位于 `events.ts:173-184`，共 **10 个**事件允许 Hook 修改 payload 或中止操作。

### 1.2 订阅机制

定义在 `packages/core/src/events/bus.ts`：

- **`on(event, handler, priority?)`**：订阅特定事件，返回取消订阅函数。支持优先级排序（priority 越低越先执行，默认 100）。Handler 签名：`(data) => Promise<void | data | { abort: true }>`。
- **`onAll(listener)`**：订阅所有事件，作为只读监听器（不可修改 payload）。
- **`emit(event, data)`**：异步发射事件。遍历 hooks 链，对于可修改事件，handler 返回值可作为新 payload 继续传递；返回 `{ abort: true }` 可提前终止。
- **`removeAll(event?)`**：清理 hooks。
- **`listenerCount(event)`**：查询注册数量。

### 1.3 与 OpenTaiji Python 版的对比

| 维度 | Harness (TypeScript) | OpenTaiji (Python) |
|------|---------------------|-------------------|
| 文件位置 | `events/bus.ts`, `events/events.ts` | `events/bus.py` |
| 事件定义 | TypeScript 联合类型 `EventName` + 类型映射 `EventPayloads`，编译时类型安全 | 字符串常量类 `Events.AGENT_START`，无类型约束 |
| Hook 优先级 | priority 越低越先执行，插入后排序 | priority 越高越先执行（排序规则相反） |
| 修改机制 | `MODIFIABLE_EVENTS` 集合显式声明，handler 返回值替换 payload | 所有事件 handler 返回值 `{"abort": true}` 可中止，无 payload 替换概念 |
| 订阅返回 | 返回 unsubscribe 闭包函数 | 提供 `off()` 方法取消，需传 handler 引用 |
| 全局监听 | `onAll()` 支持，fire-and-forget | 不支持 |
| 事件历史 | 无内置历史记录 | 内置 `_event_history` 列表（最多 1000 条）+ `get_history()` 方法 |
| 同步发射 | 无 | `emit_sync()` 同步版本 |
| 错误处理 | 捕获错误仅 console.error，不中断链 | 捕获错误记录到 results 列表，继续执行 |
| 类型系统 | 强类型：`EventPayloads[E]` 编译时映射 payload 类型 | 无类型约束，payload 为裸 `dict` |

**关键差异总结**：
1. **类型安全**：TS 版有编译时类型推导，Python 版完全动态
2. **可修改事件**：TS 版通过白名单控制，Python 版所有事件 handler 均可中断但无 payload 替换功能
3. **历史记录**：Python 版支持但不实用（生产环境应使用持久化日志）

### 1.4 扩展建议

EventBus **可以直接作为 Taiji Agent 的事件中枢**，但需要以下扩展：

**必要扩展**：
1. **增加事件类型**：补充政务场景特有的命名空间 `gov:*`（如 `gov:approval`, `gov:escalate`, `gov:compliance_check`）、验证场景 `verify:*`、审批流程 `workflow:*`、稽核 `audit:*`
2. **增加异步中间件支持**：当前仅支持 hook 链，缺少类似 Koa 的 `next()` 中间件模式
3. **增加事件溯源（Event Sourcing）**：作为政务系统，事件溯源是核心合规需求，需内置序列化到 SQLite/PostgreSQL 的能力

**推荐扩展**：
4. **增加事件过滤/路由**：支持通配符订阅 `gov:*`、条件过滤 `metadata.tenant == "dept-a"`
5. **增加错误策略**：支持 retry、dead letter queue、fallback handler
6. **增加性能指标**：事件处理耗时、hook 执行统计、吞吐率监控
7. **增加分布式支持**：Redis 发布订阅桥接或 NATS 集成，支持跨进程事件

---

## 2. Plugin 接口需要哪些扩展才能支持 Taiji Verify 和 GovMCP？

### 2.1 当前 Plugin 接口定义

定义在 `packages/core/src/plugins/plugin.ts`：

```typescript
export interface HarnessPlugin {
  id: string;
  name: string;
  version: string;
  activate(ctx: PluginContext): Promise<void>;
  deactivate(): Promise<void>;
  tools?: ToolDefinition[];
  providers?: LLMProvider[];
  hooks?: AnyHookRegistration[];
  ui?: UIContribution;
}
```

PluginContext：
```typescript
export interface PluginContext {
  state: AgentState;
  store: PersistenceStore;
  bus: EventBus;
  config: PluginConfig;
  log: Logger;
}
```

PluginLoader (`packages/core/src/plugins/loader.ts`) 具备：
- 从目录 / npm 包 / 绝对路径加载
- 自动扫描祖先目录 plugins/ 文件夹
- 调用 `activate()` 后自动注册 tools 和 hooks
- `unloadAll()` 批量反激活

### 2.2 生命周期

```
PluginLoader.loadPlugin()
  ├── resolvePluginPath()    // 定位插件入口
  ├── import()               // 动态加载
  └── plugin.activate(ctx)   // 激活（注册 tools、hooks）
       ├── toolRegistry.register()
       └── bus.on() for hooks

PluginLoader.unloadAll()
  └── plugin.deactivate()    // 反激活
```

**当前缺陷**：缺少中间状态（loading/error/degraded）、缺少热重载、缺少依赖解析。

### 2.3 Taiji Verify 插件设计建议

```typescript
// Taiji Verify Plugin - 验证与合规
export interface VerifyPlugin extends HarnessPlugin {
  // ── 扩展字段 ──
  verifyRules?: VerifyRule[];
  
  // ── 当前已有的 ──
  hooks: [{
    event: "tool:request",     // 拦截每个工具调用做验证
    handler: verifyToolCall,
    priority: 5,               // 高优先级先执行
  }, {
    event: "prompt:assemble",  // 校验 Prompt 合规
    handler: verifyPrompt,
  }, {
    event: "llm:response",     // 校验 LLM 输出
    handler: verifyOutput,
  }, {
    event: "feedback:request",  // 校验审批请求
    handler: verifyFeedbackRequest,
  }];
  
  tools: [/* 验证管理工具 */];
}
```

**所需 Plugin 接口扩展**：
1. **增加 `configSchema` 字段**：声明插件配置的 JSON Schema，支持 UI 动态配置
2. **增加 `dependencies` 字段**：声明对其他插件的依赖（如 verify 依赖 audit）
3. **增加 `healthCheck()` 方法**：运行时健康检查，验证引擎是否可用
4. **增加中间状态**：`states?: PluginState`，支持 degraded/error recovery
5. **增加 `metrics()` 方法**：暴露 Prometheus 指标

### 2.4 GovMCP 插件设计建议

```typescript
// GovMCP Plugin - 政务 MCP 协议适配
export interface GovMCPPlugin extends HarnessPlugin {
  // ── MCP 协议能力 ──
  mcpCapabilities?: {
    resources: boolean;
    tools: boolean;
    prompts: boolean;
    sampling: boolean;  // LLM sampling 能力（LLM ↔ MCP Server）
    roots: boolean;     // 文件系统根目录
  };
  
  // ── 政务协议适配 ──
  govProtocols?: Array<{
    protocol: "HTTP" | "WebSocket" | "gRPC" | "MQ";
    endpoints: GovEndpoint[];
  }>;
  
  hooks: [/* ... */];
}
```

**所需 Plugin 接口扩展**：
1. **增加 `transport` 层定义**：支持 MCP 的 JSON-RPC over stdio/SSE/WebSocket
2. **增加 `capabilities` 声明**：MCP 能力的静态声明（类似 Model Context Protocol 规范）
3. **增加 `async resourceProvider`**：MCP Resource 的按需读取/订阅机制
4. **增加 `promptTemplate` 提供**：MCP Prompt 模板注册
5. **增加权限声明**：`permissions?: string[]`，声明需要访问的政务系统资源

---

## 3. Agent Loop 如何替换 LLM Provider 为 Hermes Agent？

### 3.1 loop.ts 的 ReAct 实现

定义在 `packages/core/src/engine/loop.ts`，标准的 ReAct 模式：

```
for iteration = 1 to maxIterations:
  1. Emit loop:iteration_start (可中止)
  2. assemblePrompt(soul, skills, messages, tools) → system prompt + messages
  3. Emit llm:request (可中止)
  4. provider.chat(request) → AsyncGenerator<ChatChunk>
     - 流式处理 text/tool_call/done/error 四种 chunk
     - 实时 emit llm:chunk → onText 回调
  5. Emit llm:response → state.addMessage
  6. if no toolCalls → break (最终答案)
  7. for each toolCall:
     - Emit tool:request (可中止)
     - tool.execute(args) → state.addMessage (tool result)
  8. Emit loop:iteration_end
```

**终止条件**（按检查顺序）：
1. LLM 返回无 tool call（最终答案）
2. 达到 maxIterations
3. Plugin hook 返回 `{ abort: true }`
4. 用户发送中断信号

### 3.2 Provider 接口设计

定义在 `packages/core/src/providers/provider.ts`：

```typescript
export interface LLMProvider {
  id: string;
  name: string;
  chat(request: ChatRequest): AsyncGenerator<ChatChunk>;
  supportsTools: boolean;
  supportsStreaming: boolean;
  supportsImages: boolean;
}
```

ChatChunk 流式协议：
```typescript
type ChatChunk = 
  | { type: "text"; content?: string; usage?: TokenUsage }
  | { type: "tool_call"; toolCall: ToolCallMessage }
  | { type: "done"; usage?: TokenUsage }
  | { type: "error"; error: string }
```

当前已有实现：`OpenAIProvider`, `AnthropicProvider`, `OllamaProvider`

### 3.3 Hermes Provider 桥接设计

Hermes Agent 是一个独立的 agent 系统。要将其作为 LLM Provider 桥接到 Harness loop，需要实现 **HermesProvider** 适配器：

```typescript
// HermesProvider 桥接适配器
export class HermesProvider implements LLMProvider {
  id = "hermes";
  name = "Hermes Agent";
  supportsTools = true;
  supportsStreaming = true;  // 取决于 Hermes 是否支持 SSE
  supportsImages = false;

  private hermesClient: HermesClient;  // 封装与 Hermes Agent 的通信

  async *chat(request: ChatRequest): AsyncGenerator<ChatChunk> {
    // Step 1: 将 Harness Message[] 转换为 Hermes 格式
    //   - 不同 role 映射（system/user/assistant/tool）
    //   - tool definitions 转换
    const hermesMessages = this.mapMessages(request);
    const hermesTools = request.tools?.map(this.mapTool);
    
    // Step 2: 调用 Hermes Agent API
    //   - Hermes 作为独立进程/服务运行
    //   - 通信方式：gRPC streaming / HTTP SSE / Unix Socket
    const stream = this.hermesClient.chat({
      messages: hermesMessages,
      tools: hermesTools,
      model: request.model,
      temperature: request.temperature,
      maxTokens: request.maxTokens,
    });
    
    // Step 3: 将 Hermes 响应流映射为 ChatChunk
    for await (const chunk of stream) {
      switch (chunk.type) {
        case "text":
          yield { type: "text", content: chunk.delta };
          break;
        case "tool_call":
          yield { type: "tool_call", toolCall: chunk.toolCall };
          break;
        case "usage":
          yield { type: "text", usage: chunk.usage };
          break;
        case "error":
          yield { type: "error", error: chunk.message };
          break;
      }
    }
    yield { type: "done", usage: finalUsage };
  }

  // Step 4: 桥接的关键——工具映射
  //   Hermes Agent 可以自主调用工具，这意味着 loop 中的 tool execution 逻辑
  //   可能会被 Hermes 接管。有两种模式：
  //   A. 透明模式：Hermes 仅作为 LLM，tool calls 由 Harness loop 执行
  //   B. 委托模式：Hermes 作为完整 Agent，自行执行工具，仅返回最终文本
}
```

**通信方案选择**：

| 方案 | 延迟 | 吞吐量 | 实现复杂度 | 可靠性 |
|------|------|--------|-----------|--------|
| HTTP SSE | 中等（序列化开销） | 高 | 低 | 高 |
| gRPC stream | 低 | 高 | 中 | 高 |
| Unix Socket | 低 | 最高 | 中 | 中 |
| Child process stdio | 低 | 高 | 低 | 低 |

**推荐**：HTTP SSE — 最通用，开发和调试最方便，解耦最彻底。Hermes 作为独立服务启动，Harness 通过 HTTP 调用。

---

## 4. TypeScript 和 Python 互操作的最佳方案是什么？

### 4.1 方案比较

| 维度 | gRPC | Thrift | Direct IPC (Unix Socket) | HTTP REST/SSE |
|------|------|--------|-------------------------|---------------|
| **序列化** | Protobuf（二进制，紧凑） | Thrift Binary/Compact | 自定义（JSON/Protobuf） | JSON（文本） |
| **Schema 定义** | `.proto` 文件，代码生成 | `.thrift` 文件，代码生成 | 无/手动定义 | OpenAPI（可选） |
| **流式支持** | 原生 gRPC streaming | 部分支持 | 手动实现 | SSE / WebSocket |
| **TS 支持** | `@grpc/grpc-js` 成熟 | `thrift` npm 包维护一般 | 原生 `net` 模块 | 原生 `fetch` |
| **Python 支持** | `grpcio` 原生 | `thrift` 包 | `asyncio` 原生 | `httpx` / `aiohttp` |
| **性能** | 高（Protobuf + HTTP/2） | 中 | 最高（无协议开销） | 中（JSON 序列化重） |
| **双向流** | 原生支持 | 有限 | 需自行实现 | WebSocket |
| **类型安全** | 代码生成保障 | 代码生成保障 | 无 | Zod/JSON Schema 验证 |
| **调试友好** | 需 gRPCurl 等工具 | 较少工具支持 | 低（二进制/自定协议） | 高（curl 直接测试） |
| **生态系统** | 最成熟，K8s/Istio 生态 | 较老，社区萎缩 | 最小 | 通用，工具丰富 |
| **学习成本** | 中 | 中 | 低（仅 IPC） | 低 |
| **集成 Hermes** | 适合流式通信 | 适合 RPC 调用 | 适合同机高性能 | 最适合快速原型 |

### 4.2 推荐方案

**主推荐**：gRPC + HTTP SSE 混合模式

理由：

1. **gRPC 用于核心 Agent Loop 通信**（Hermes ↔ Harness）：
   - Protobuf 强类型 schema 保证双方类型安全
   - 原生双向流支持（LLM 流式响应天然匹配 gRPC Server Streaming）
   - HTTP/2 多路复用，适合高吞吐量
   - K8s 原生支持（Istio/gRPC 负载均衡）

2. **HTTP SSE 用于 Web 前端**（WS 协议已有）：
   - 前端无需 gRPC-Web（减少依赖）
   - SSE 比 WebSocket 更适合单向流式输出
   - 现有 ws.ts 无需大改

3. **Unix Socket 用于本地插件通信**（同机器高性能）：
   - Docker Sandbox 内或同主机场景

**架构示意**：

```
┌─────────────────────────────────────┐
│         Harness (TypeScript)        │
│  ┌──────────┐  ┌──────────────────┐ │
│  │ Agent    │  │  Plugin Loader    │ │
│  │ Loop     │──│ (Verify/GovMCP)  │ │
│  └────┬─────┘  └──────────────────┘ │
│       │ gRPC stream                 │
│  ┌────▼─────┐                       │
│  │ Hermes   │  ← gRPC/Unix Socket   │
│  │ Provider │                       │
│  └──────────┘                       │
└─────────┬──┬────────────────────────┘
          │  │
    HTTP SSE  WebSocket
          │  │
     ┌────▼──▼────┐
     │  Web Client │
     └─────────────┘
```

**已部署的 OpenTaiji Python 代码集成建议**：
- 当前 `src/opentaiji/events/bus.py` 已经是一个精简版事件总线的 Python 移植
- Harness TS EventBus 的事件可通过统一的事件协议桥接到 Python 端
- 可用 gRPC 双向流实现事件双工同步

---

## 5. 流式响应如何处理？

### 5.1 ws.ts 的 WebSocket 协议分析

WebSocket 处理器定义在 `packages/server/src/ws.ts`，采用 C/S 消息模型。

**客户端 → 服务器消息** (`ClientMessage`)：

| type | 功能 | 说明 |
|------|------|------|
| `ping` | 心跳 | 返回 `pong` |
| `run` | 启动任务 | 参数：`id`, `task`, `config?` |
| `cancel` | 取消任务 | 参数：`id` |
| `feedback` | 反馈响应 | 参数：`requestId`, `response` |

**服务器 → 客户端消息** (`ServerMessage`)：

| type | 触发时机 | 说明 |
|------|----------|------|
| `session:init` | 连接建立 | 返回 `sessionId` |
| `task:start` | run 消息处理开始 | `taskId` |
| `event` | 任何 FORWARDED_EVENTS 触发 | 携带事件名和数据 |
| `text:delta` | `llm:chunk` 中的 text chunk | 实时增量文本 |
| `feedback:request` | `feedback:request` 事件 | 转发给客户端 |
| `task:complete` | agent.run() 完成 | 最终结果 |
| `task:error` | agent.run() 异常 | 错误信息 |
| `error` | WS 协议差错 | PARSE_ERROR / TASK_ACTIVE 等 |

**FORWARDED_EVENTS**（`ws.ts:22-35`）：共 13 个事件，原文转发。

### 5.2 流式处理机制

**文本流**（`text:delta`）：
```
agent.run()
  └── runLoop()
       └── provider.chat() → AsyncGenerator<ChatChunk>
            ├── yield { type: "text", content: "你好" }  ─┐
            ├── yield { type: "text", content: "世界" }  ─┤──→ onText → bus.emit("llm:chunk") → ws.send({ type: "text:delta" })
            └── yield { type: "done" }                    ─┘
```

**事件流**（`event`）：
1. runLoop 过程中每次 bus.emit() 触发对应事件
2. ws.ts 中 `agent.bus.on(eventName, handler)` 注册监听器
3. handler 中 sanitizeEventData() 处理 Error 对象序列化
4. 发送 `{ type: "event", taskId, event, data }`

**流完整链路**：
```
Provider.chat() AsyncGenerator
    ↓ (for await)
loop.ts: for await (const chunk of stream)
    ↓ bus.emit("llm:chunk")
ws.ts: bus.on("llm:chunk") → send(text:delta)
    ↓
Client: WebSocket.onmessage → append to UI
```

**反馈流**（`feedback:request`）：
- HITL 请求作为反馈事件通过 WebSocket 转发
- 客户端（Web UI 或 Electron）展示审批对话框
- 用户响应通过 `feedback` 消息回传
- `DeferredFeedbackAdapter.resolve()` 唤醒暂停的 loop

**当前架构的优势**：
- 流式与事件分离（text:delta 专用于实时文本，event 用于结构化事件）
- 非阻塞设计（agent.run() 异步执行，WebSocket 不阻塞）
- 自动清理（任务完成后取消所有事件监听）

**需改进点**：
1. 缺少背压控制（Backpressure），大数据量下可能 OOM
2. 缺少断线重连恢复（Reconnection & Resume），重连后无法获取之前的流数据
3. 缺少 Rate Limiting
4. 事件序列化过于简单（`sanitizeEventData` 先用 JSON.stringify 再 parse 效率低）

---

## 6. Human-in-the-Loop 如何与政务审批工作流对接？

### 6.1 FeedbackManager 架构

**三层架构**：

```
Agent Loop (loop.ts)
      │
      ▼  feedbackManager.confirm/choose/review/form()
FeedbackManager (manager.ts)
      │  路由 + 超时 + 事件发射 + 状态管理
      ▼
FeedbackAdapter (adapter.ts)
      │  传输层：CLI / WebSocket / Slack / Queue
      ▼
    Human
```

**FeedbackManager 核心职责**：
1. **Adapter 管理**：注册/注销/查找适配器，支持 `canHandle()` 路由选择
2. **请求生命周期**：`buildBase()` → `emit feedback:request` → resolveAdapter → `raceTimeout()` → emit `feedback:response/timeout`
3. **状态管理**：暂停/恢复 AgentState（`state.set("status", "paused")`），保护并发状态
4. **超时处理**：`defaultTimeout=300s`，支持 `defaultDeny` 安全策略
5. **可观测性**：getPendingRequests()、hasPending()、取消

**反馈类型**（`types.ts`）：

| 类型 | 请求 | 响应 | 政务场景映射 |
|------|------|------|-------------|
| `confirm` | 确认操作 | 通过/拒绝 | 审批确认、发文审批 |
| `choice` | 选项选择 | 选中项 | 部门选择、流程分支 |
| `text` | 文本输入 | 自由文本 | 审批意见、批注说明 |
| `review` | 审核（含 artifact） | 通过/驳回/修改/升级 | **公文审批、方案审核** |
| `form` | 表单填写 | 字段值表 | 申请表单、备案登记 |

### 6.2 扩展点分析

**扩展点 1：FeedbackAdapter**（`adapter.ts`）

当前已提供三种内置适配器：
- `AutoApproveAdapter`：测试用自动通过
- `CallbackFeedbackAdapter`：包装回调函数
- `DeferredFeedbackAdapter`：外部事件驱动（WebSocket 使用）

可扩展的适配器模式：

```typescript
// 政务审批适配器示例
export class GovApprovalAdapter implements FeedbackAdapter {
  readonly id = "gov-approval";
  readonly name = "政务审批适配器";
  
  async requestFeedback(request: FeedbackRequest): Promise<FeedbackResponse> {
    switch (request.type) {
      case "review":
        // 1. 根据审批级别路由到不同审批人
        const approver = await this.routeToApprover(request);
        // 2. 通过政务 OA 系统发送审批任务
        await this.govOaClient.sendTask({
          taskId: request.id,
          title: request.prompt,
          content: request.artifact?.content,
          approver: approver,
          deadline: request.timeout,
          priority: request.priority,
        });
        // 3. 等待 OA 回调（通过 Webhook/轮询）
        return this.waitForCallback(request.id);
        
      case "confirm":
        // 政务审批的"一键确认"模式
        if (this.isRapidApproval(request)) {
          return this.rapidApprove(request);
        }
        // 否则走常规审批流程
        return this.standardApprove(request);
    }
  }
}
```

**扩展点 2：TaskChain**（`chain.ts`）

TaskChain 天然适配政务多级审批工作流：

```
Step 1: 起草（Agent Task）
    ↓
Gate 1: 科室审核（review）
    ↓ (approve)
Step 2: 修改完善（Agent Task）
    ↓
Gate 2: 处室会签（form: 填写会签意见）
    ↓ (approve)
Step 3: 生成正式公文（transform）
    ↓
Gate 3: 领导签发（confirm）
    ↓ (approve)
Step 4: 发文归档（Agent Task）
```

**扩展点 3：事件总线 Hook**

通过 `bus.on("tool:request")` 实现审批前的合规检查：
```typescript
bus.on("tool:request", async (data) => {
  if (isSensitiveOperation(data.name, data.args)) {
    // 需要审批的操作自动路由到审批适配器
    const approved = await govApprovalService.preApprove(data);
    if (!approved) return { abort: true, reason: "No approval" };
  }
  return data;
}, 10);
```

### 6.3 政务审批对接建议

**方案：GovAdapter + GovChain 组合模式**

1. **开发 GovApprovalAdapter**：
   - 对接政务 OA 系统的审批 API（HTTP/gRPC）
   - 支持多级审批（一级审批/会签/联合审批）
   - 支持审批时限配置（普通/加急）
   - 支持审批人自动路由（岗位映射）

2. **扩展 FeedbackRequest 类型**：
   - 增加 `gov:countersign`（会签）：多审批人并行审批
   - 增加 `gov:circulate`（传阅）：告知但不要求审批
   - 增加 `gov:archive`（归档）：审批后的归档确认
   - 增加审批流转字段：`govMeta: { level, department, approverRole, deadline }`

3. **审批全流程集成**：

```
┌─────────────────────────────────────────────────────────┐
│                    Taiji Agent                          │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ Agent    │  │ GovChain      │  │ GovApprovalAdapter│ │
│  │ Loop     │──│ 多级审批工作流 │──│ 政务审批通道       │ │
│  └──────────┘  └──────────────┘  └────────┬──────────┘ │
│                                           │            │
└───────────────────────────────────────────┼────────────┘
                                            │ HTTP/gRPC
                                  ┌─────────▼────────┐
                                  │  政务 OA 系统     │
                                  │  (审批任务管理)   │
                                  └────────┬─────────┘
                                           │
                                  ┌─────────▼────────┐
                                  │ 审批人（多级）    │
                                  │ 处室→会签→领导   │
                                  └──────────────────┘
```

4. **关键设计原则**：
   - **不可绕过**：审批请求必须通过 FeedbackManager，不可由 Agent 自行决定跳过
   - **可审计**：所有审批事项记录到 EventBus 事件日志 + SQLite 持久化
   - **可追溯**：使用 GovMCP 插件记录完整审批链（who/what/when/result）
   - **可降级**：审批超时或服务不可用时有安全默认值（defaultDeny=true）
   - **合规保存**：审批记录按政务档案规范保留，支持事后稽核导出

---

## 附录：关键文件索引

| 路径 | 说明 |
|------|------|
| `packages/core/src/events/bus.ts` | 事件总线实现 |
| `packages/core/src/events/events.ts` | 事件类型定义 |
| `packages/core/src/engine/loop.ts` | Agent Loop（ReAct） |
| `packages/core/src/plugins/plugin.ts` | 插件接口定义 |
| `packages/core/src/plugins/loader.ts` | 插件加载器 |
| `packages/core/src/feedback/adapter.ts` | FeedbackAdapter 定义 |
| `packages/core/src/feedback/manager.ts` | FeedbackManager 实现 |
| `packages/core/src/feedback/chain.ts` | TaskChain 工作流 |
| `packages/core/src/feedback/types.ts` | 反馈类型定义 |
| `packages/core/src/providers/provider.ts` | LLMProvider 接口 |
| `packages/core/src/providers/openai.ts` | OpenAI Provider 实现 |
| `packages/core/src/index.ts` | HarnessAgent 工厂与配置 |
| `packages/server/src/ws.ts` | WebSocket 协议 |
| `plugins/sandbox/src/docker.ts` | Docker 沙箱客户端 |
| `packages/desktop/src/main/` | Electron 主进程 |
| `packages/desktop/src/renderer/` | Electron 渲染进程 |
| `src/opentaiji/events/bus.py` | Python 版事件总线 |

---

*报告结束*
