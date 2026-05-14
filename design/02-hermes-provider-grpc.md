# Hermes Provider gRPC 接口定义

> **文档状态**: 初稿  
> **作者**: Bob (Architect)  
> **版本**: 1.0.0  
> **日期**: 2026-05-14  

---

## 目录

1. [设计目标](#1-设计目标)
2. [技术选型](#2-技术选型)
3. [.proto 完整定义](#3-proto-完整定义)
4. [类型映射](#4-类型映射)
5. [错误处理与超时策略](#5-错误处理与超时策略)
6. [流式响应设计](#6-流式响应设计)
7. [TS/Python 双栈能力评估](#7-tspython-双栈能力评估)
8. [实现计划](#8-实现计划)

---

## 1. 设计目标

### 1.1 解决的问题

在 Taiji Agent 架构中，**Harness（TypeScript 运行时层）** 和 **Hermes Agent（Python AI 引擎层）** 需要高效、可靠的跨语言通信桥接。

当前现状：

```
┌────────────────────────────────────────┐
│          Harness (TypeScript)           │
│  ┌──────────────┐                      │
│  │ Agent Loop   │──→ LLM Provider ──→  │  OpenAI/Anthropic 等
│  │ (loop.ts)    │                      │
│  └──────────────┘                      │
└────────────────────────────────────────┘
```

目标架构：

```
┌────────────────────────────────────────┐
│          Harness (TypeScript)           │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ Agent Loop   │─→│ HermesProvider  │─┼── gRPC ──┐
│  │ (loop.ts)    │  │ (TS gRPC Client)│ │          │
│  └──────────────┘  └─────────────────┘ │          │
└─────────────────────────────────────────┘          │
                                                     ▼
                              ┌──────────────────────────────────┐
                              │     Hermes Agent (Python)        │
                              │  ┌────────────────────────────┐  │
                              │  │ gRPC Server                │  │
                              │  │  ├─ HermesProvider Service  │  │
                              │  │  ├─ HermesMemory Service    │  │
                              │  │  ├─ HermesSkills Service    │  │
                              │  │  └─ HermesAgent Service     │  │
                              │  └────────────────────────────┘  │
                              │  ┌────────────────────────────┐  │
                              │  │ Hermes Core Engine         │  │
                              │  │  ├─ Agent (run_agent.py)   │  │
                              │  │  ├─ Skills System          │  │
                              │  │  ├─ Memory System          │  │
                              │  │  └─ Tools Registry         │  │
                              │  └────────────────────────────┘  │
                              └──────────────────────────────────┘
```

**核心问题**：
1. Harness 的 Agent Loop（TS）需要调用 Hermes Agent（Python）的 LLM 能力（chat/stream）
2. Harness 需要访问 Hermes 的技能系统、记忆系统和代理执行能力
3. 两者间需要低延迟、高吞吐、强类型的通信协议

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **强类型契约优先** | 所有接口通过 `.proto` 文件定义，双方代码由 protoc 生成，消除手写序列化错误 |
| **流式优先** | LLM 聊天天然是流式的，所有相关接口默认支持 Server Streaming |
| **最小暴露** | 只暴露 Harness 真正需要的接口，不盲目暴露 Hermes 内部实现细节 |
| **向后兼容** | proto 字段使用 `optional` + 合理的默认值，保证服务端/客户端独立升级 |
| **优雅降级** | 服务不可用时（Hermes 宕机），Harness 侧可回退到直接 LLM Provider 调用 |
| **无状态服务** | gRPC 服务本身无状态，会话状态由 Harness 侧维护 |

### 1.3 非功能性需求

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| **P99 延迟** | < 50ms（非流式 Chat） | gRPC 内置 metrics |
| **首包延迟（TTFB）** | < 200ms（流式 Chat） | 首个 chunk 到达时间 |
| **吞吐量** | > 1000 req/s（单实例） | wrk/gRPC benchmark |
| **并发连接数** | > 500 个活跃流 | gRPC HTTP/2 多路复用 |
| **服务可用性** | > 99.9% | 健康检查 + 熔断 |
| **序列化效率** | Protobuf < 10μs 千字节级消息 | 基准测试 |
| **连接恢复** | < 5s 断线重连 | gRPC 内置重连 |

---

## 2. 技术选型

### 2.1 协议对比分析

| 维度 | **gRPC** | **REST/HTTP** | **WebSocket** | **子进程 IPC** |
|------|:--------:|:-------------:|:-------------:|:--------------:|
| **序列化** | Protobuf（二进制，紧凑） | JSON（文本，冗余） | JSON/自定义 | JSON/Pickle |
| **Schema 定义** | `.proto` + 代码生成 | OpenAPI（手动） | 无 | 无 |
| **类型安全** | ✅ 编译时保证 | ❌ 运行时验证 | ❌ 手动验证 | ❌ 无 |
| **流式支持** | ✅ 原生 Server/Bidi Streaming | ❌ SSE（单向） | ✅ 双向 | ❌ 需自行实现 |
| **TS 生态** | `@grpc/grpc-js`（成熟） | `fetch`（原生） | `ws`（原生） | `child_process` |
| **Python 生态** | `grpcio`（原生） | `httpx`/`aiohttp` | `websockets` | `subprocess` |
| **HTTP/2 多路复用** | ✅ 原生 | ❌ HTTP/1.1 | ❌ 单连接 | ❌ |
| **负载均衡** | ✅ K8s/Istio/gRPC LB | ✅ 通用 HTTP LB | ⚠️ 有限 | ❌ |
| **调试友好度** | ⚠️ 需 gRPCurl/gRPCui | ✅ curl 直接测 | ⚠️ 需 ws 工具 | ❌ 低 |
| **学习成本** | 中 | 低 | 低 | 低 |
| **性能（千字节级）** | ⚡ 高 | 中 | 中 | ⚡ 高（同机） |

### 2.2 选型理由

**最终选择：gRPC**，理由如下：

1. **强类型契约**：`.proto` 文件是 TS ↔ Python 之间的"合同"，双方各自编译生成代码，保证类型一致。这是分布式系统中最重要的防错机制。

2. **原生流式支持**：LLM Chat 本质是 Server Streaming（服务端持续吐 token），gRPC 的 Server Streaming RPC 是最自然的匹配。REST + SSE 需要额外处理连接管理和重连。

3. **HTTP/2 多路复用**：单连接承载多个并发流，减少连接建立开销。对于同时运行多个 Agent Loop 的场景至关重要。

4. **生态成熟度**：gRPC 在 K8s/Istio 生态中有天然的支持，适合未来的微服务化和服务网格部署。

5. **性能优势**：Protobuf 序列化比 JSON 小 3-10 倍，解析速度快 10-100 倍，对<50ms 的延迟目标至关重要。

**为什么不选其他方案**：
- **REST/HTTP**：缺少流式原生支持，JSON 序列化开销大，Schema 需额外维护 OpenAPI 文档
- **WebSocket**：无 Schema 约束，连接管理复杂，不适合请求-响应模式
- **子进程 IPC**：同机强耦合，无法分布式部署，无序列化标准，调试困难

### 2.3 架构图

```
┌─────────────────────────────────────────────────────┐
│                Harness (TypeScript)                   │
│                                                       │
│  ┌──────────────────────────────────────────────────┐│
│  │            HermesProvider 客户端                   ││
│  │  ┌─────────────┐ ┌──────────────┐ ┌───────────┐ ││
│  │  │ ChatClient  │ │ MemoryClient │ │SkillsClient│ ││
│  │  │ (streaming) │ │              │ │           │ ││
│  │  └──────┬──────┘ └──────┬───────┘ └─────┬─────┘ ││
│  └─────────┼───────────────┼───────────────┼───────┘│
│            │               │               │         │
└────────────┼───────────────┼───────────────┼─────────┘
             │               │               │
             │    gRPC (HTTP/2, Protobuf)    │
             │               │               │
┌────────────┼───────────────┼───────────────┼─────────┐
│            ▼               ▼               ▼         │
│  ┌──────────────────────────────────────────────────┐│
│  │           Hermes Agent (Python) gRPC Server       ││
│  │                                                   ││
│  │  ┌──────────────┐ ┌───────────┐ ┌──────────────┐ ││
│  │  │HermesProvider │ │HermesMem  │ │HermesSkills  │ ││
│  │  │Service       │ │Service    │ │Service       │ ││
│  │  │(chat/stream) │ │(save/srch)│ │(list/exec)   │ ││
│  │  └──────┬───────┘ └─────┬─────┘ └──────┬───────┘ ││
│  │         │               │              │          ││
│  │         ▼               ▼              ▼          ││
│  │  ┌──────────┐ ┌──────────┐ ┌───────────────────┐ ││
│  │  │ LLM Adpt │ │MemoryMgr│ │ Skills System     │ ││
│  │  │(Anthropic│ │(8 bknd) │ │ (532+ skills)     │ ││
│  │  │ OpenAI..)│ │         │ │                    │ ││
│  │  └──────────┘ └─────────┘ └────────────────────┘ ││
│  └──────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

---

## 3. .proto 完整定义

### 3.1 全局包和导入

```protobuf
syntax = "proto3";

package hermes.v1;

import "google/protobuf/struct.proto";
import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

option go_package = "github.com/taiji-ai/hermes-proto/gen/go/hermes/v1";
option java_package = "com.taiji.hermes.v1";
option java_multiple_files = true;
```

### 3.2 枚举类型

```protobuf
// ── 完成原因枚举 ──────────────────────────────────

enum FinishReason {
  FINISH_REASON_UNSPECIFIED = 0;
  FINISH_REASON_STOP = 1;           // 正常完成
  FINISH_REASON_LENGTH = 2;         // max_tokens 截断
  FINISH_REASON_TOOL_CALLS = 3;     // 工具调用（继续循环）
  FINISH_REASON_ERROR = 4;          // 出错终止
  FINISH_REASON_CANCELLED = 5;      // 用户/系统取消
  FINISH_REASON_CONTENT_FILTERED = 6; // 内容过滤
  FINISH_REASON_RECURSION_LIMIT = 7;  // 递归限制
}

// ── 工具类型枚举 ──────────────────────────────────

enum ToolType {
  TOOL_TYPE_UNSPECIFIED = 0;
  TOOL_TYPE_FUNCTION = 1;           // 标准函数调用
  TOOL_TYPE_CODE_INTERPRETER = 2;   // 代码执行
  TOOL_TYPE_FILE_SEARCH = 3;        // 文件搜索
  TOOL_TYPE_COMPUTER_USE = 4;       // 计算机交互（Hermes computer_use）
  TOOL_TYPE_WEB_SEARCH = 5;         // 网络搜索
  TOOL_TYPE_BROWSER = 6;            // 浏览器自动化
}

// ── 记忆类型枚举 ──────────────────────────────────

enum MemoryType {
  MEMORY_TYPE_UNSPECIFIED = 0;
  MEMORY_TYPE_SESSION = 1;          // 会话记忆（短期）
  MEMORY_TYPE_EPISODIC = 2;         // 情景记忆（长期）
  MEMORY_TYPE_SEMANTIC = 3;         // 语义记忆（知识）
  MEMORY_TYPE_PROCEDURAL = 4;       // 程序记忆（技能）
}

// ── Agent 状态枚举 ────────────────────────────────

enum AgentStatusEnum {
  AGENT_STATUS_UNSPECIFIED = 0;
  AGENT_STATUS_IDLE = 1;            // 空闲
  AGENT_STATUS_RUNNING = 2;         // 运行中
  AGENT_STATUS_PAUSED = 3;          // 暂停（等待输入）
  AGENT_STATUS_WAITING_FEEDBACK = 4; // 等待人工反馈
  AGENT_STATUS_ERROR = 5;           // 错误
  AGENT_STATUS_DONE = 6;            // 完成
}

// ── 记忆后端枚举 ──────────────────────────────────

enum MemoryBackend {
  MEMORY_BACKEND_UNSPECIFIED = 0;
  MEMORY_BACKEND_HOLOGRAPHIC = 1;   // 本地 SQLite（默认）
  MEMORY_BACKEND_HONCHO = 2;        // Honcho 云服务
  MEMORY_BACKEND_HINDSIGHT = 3;     // Hindsight 云/本地
  MEMORY_BACKEND_MEM0 = 4;          // Mem0 云服务
  MEMORY_BACKEND_SUPERMEMORY = 5;   // Supermemory 云服务
  MEMORY_BACKEND_RETAINDB = 6;      // RetainDB 云服务
}
```

### 3.3 HermesProvider Service

```protobuf
// ─────────────────────────────────────────────────────
// HermesProvider — LLM 聊天与嵌入服务
// ─────────────────────────────────────────────────────

service HermesProvider {
  // 非流式 Chat（用于简单问答场景）
  rpc Chat(ChatRequest) returns (ChatResponse);

  // 流式 Chat（Server Streaming，LLM 推流，推荐模式）
  rpc StreamChat(ChatRequest) returns (stream ChatChunk);

  // 获取文本嵌入向量
  rpc GetEmbedding(EmbeddingRequest) returns (EmbeddingResponse);

  // 获取可用模型列表
  rpc GetModels(google.protobuf.Empty) returns (ModelList);
}

// ── 消息类型定义 ──────────────────────────────────

message ChatRequest {
  repeated Message messages = 1;            // 对话历史（必填）
  repeated ToolDefinition tools = 2;        // 可用工具列表
  string model = 3;                         // 模型名称（可选，使用默认）
  optional float temperature = 4;           // 温度（0.0-2.0）
  optional uint32 max_tokens = 5;           // 最大生成 Token 数
  optional bool stream = 6;                 // 是否流式（等效于调用 StreamChat）
  optional string system_prompt = 7;        // 可选的 system prompt 覆盖
  optional string session_id = 8;           // 会话 ID（用于记忆关联）
  map<string, string> metadata = 9;         // 自定义元数据（追踪用）
}

message Message {
  string role = 1;                          // "system" | "user" | "assistant" | "tool"
  string content = 2;                       // 文本内容
  optional string name = 3;                 // 工具执行者名称（tool role 时使用）
  optional string tool_call_id = 4;         // 工具调用 ID（tool role 时使用）
  repeated ToolCall tool_calls = 5;         // 工具调用列表（assistant role 时使用）
}

message ToolDefinition {
  string name = 1;                          // 工具名称
  string description = 2;                   // 工具描述
  google.protobuf.Struct parameters = 3;    // JSON Schema 参数定义
  optional ToolType type = 4;               // 工具类型
}

message ToolCall {
  string id = 1;                            // 工具调用 ID
  string name = 2;                          // 工具名称
  google.protobuf.Struct args = 3;          // 调用参数
}

message ChatResponse {
  string content = 1;                       // 生成的文本内容
  repeated ToolCall tool_calls = 2;         // 工具调用列表
  FinishReason finish_reason = 3;           // 完成原因
  TokenUsage usage = 4;                     // Token 用量
  string model = 5;                         // 实际使用的模型
  optional string session_id = 6;           // 会话 ID
}

message ChatChunk {
  oneof chunk_type {
    string content_delta = 1;               // 文本增量（流式内容）
    ToolCallDelta tool_call_delta = 2;      // 工具调用增量
  }
  optional FinishReason finish_reason = 3;  // 完成原因（仅在最后一个 chunk 设置）
  optional TokenUsage usage = 4;            // Token 用量（仅在最后一个 chunk 设置）
  uint32 index = 5;                         // Chunk 序号（用于排序和去重）
}

message ToolCallDelta {
  string id = 1;                            // 工具调用 ID
  string name = 2;                          // 工具名称
  string args_delta = 3;                    // 参数 JSON 增量
}

message TokenUsage {
  uint32 input_tokens = 1;                  // 输入 Token 数
  uint32 output_tokens = 2;                 // 输出 Token 数
  optional uint32 total_tokens = 3;         // 总计 Token 数
  optional uint32 cached_input_tokens = 4;  // 缓存命中的输入 Token 数
}

message EmbeddingRequest {
  string text = 1;                          // 需要嵌入的文本
  optional string model = 2;                // 嵌入模型名称
  optional string session_id = 3;           // 会话 ID
}

message EmbeddingResponse {
  repeated float embedding = 1;             // 嵌入向量
  uint32 dimensions = 2;                    // 向量维度
  string model = 3;                         // 使用的模型
  TokenUsage usage = 4;                     // Token 用量
}

message ModelList {
  repeated ModelInfo models = 1;
}

message ModelInfo {
  string id = 1;                            // 模型 ID
  string name = 2;                          // 模型显示名称
  string provider = 3;                      // 提供商（openai/anthropic/ollama 等）
  bool supports_tools = 4;                  // 是否支持工具调用
  bool supports_streaming = 5;              // 是否支持流式
  bool supports_embeddings = 6;             // 是否支持嵌入
  optional uint32 max_tokens = 7;           // 最大上下文长度
}
```

### 3.4 HermesMemory Service

```protobuf
// ─────────────────────────────────────────────────────
// HermesMemory — 记忆存取服务
// ─────────────────────────────────────────────────────

service HermesMemory {
  // 保存记忆
  rpc Save(SaveRequest) returns (SaveResponse);

  // 搜索记忆
  rpc Search(SearchRequest) returns (SearchResponse);

  // 获取上下文（为当前对话组装相关记忆）
  rpc GetContext(GetContextRequest) returns (GetContextResponse);

  // 删除记忆
  rpc Delete(DeleteRequest) returns (DeleteResponse);

  // 列出可用记忆后端
  rpc ListBackends(google.protobuf.Empty) returns (MemoryBackendList);
}

message SaveRequest {
  string content = 1;                       // 记忆内容
  MemoryType type = 2;                      // 记忆类型
  optional string session_id = 3;           // 关联会话
  optional string tenant_id = 4;            // 租户 ID（多租户隔离）
  map<string, string> metadata = 5;         // 附加元数据
  optional MemoryBackend backend = 6;       // 目标后端（使用默认）
  repeated float embedding = 7;             // 可选的预计算嵌入向量
}

message SaveResponse {
  string memory_id = 1;                     // 记忆 ID
  bool deduplicated = 2;                    // 是否去重（合并到已有记忆）
  optional string error = 3;                // 错误信息
}

message SearchRequest {
  string query = 1;                         // 搜索查询文本
  optional MemoryType type = 2;             // 按类型过滤
  optional uint32 limit = 3;                // 返回条数上限（默认 10）
  optional float min_score = 4;             // 最低相似度阈值（0.0-1.0）
  optional string session_id = 5;           // 限制到指定会话
  optional string tenant_id = 6;            // 租户 ID
  optional MemoryBackend backend = 7;       // 指定搜索后端
  repeated float query_embedding = 8;       // 可选的预计算查询向量
}

message SearchResponse {
  repeated MemoryItem results = 1;           // 搜索结果
  uint32 total_count = 2;                   // 总匹配数
  float search_time_ms = 3;                 // 搜索耗时（毫秒）
}

message MemoryItem {
  string id = 1;                            // 记忆 ID
  string content = 2;                       // 记忆内容
  MemoryType type = 3;                      // 记忆类型
  float score = 4;                          // 相似度评分
  google.protobuf.Timestamp created_at = 5; // 创建时间
  optional google.protobuf.Timestamp last_accessed = 6; // 最后访问时间
  map<string, string> metadata = 7;         // 附加元数据
  optional string session_id = 8;           // 关联会话
}

message GetContextRequest {
  string query = 1;                         // 当前上下文查询
  optional uint32 max_tokens = 2;           // 上下文 Token 预算
  optional string session_id = 3;           // 会话 ID
  optional string tenant_id = 4;            // 租户 ID
}

message GetContextResponse {
  string context_block = 1;                 // 格式化的上下文文本块
  repeated MemoryItem items = 2;            // 组成上下文的具体记忆项
  uint32 total_tokens = 3;                  // 总 Token 数
}

message DeleteRequest {
  string memory_id = 1;                     // 记忆 ID
  optional string tenant_id = 2;            // 租户 ID
}

message DeleteResponse {
  bool success = 1;
}

message MemoryBackendList {
  repeated MemoryBackendInfo backends = 1;
}

message MemoryBackendInfo {
  MemoryBackend backend = 1;
  string name = 2;
  bool is_available = 3;                    // 是否可用
  optional string description = 4;
}
```

### 3.5 HermesSkills Service

```protobuf
// ─────────────────────────────────────────────────────
// HermesSkills — 技能管理服务
// ─────────────────────────────────────────────────────

service HermesSkills {
  // 列出所有可用技能
  rpc ListSkills(ListSkillsRequest) returns (SkillList);

  // 获取单个技能详情
  rpc GetSkill(GetSkillRequest) returns (Skill);

  // 执行技能
  rpc ExecuteSkill(ExecuteSkillRequest) returns (ExecuteSkillResponse);

  // 流式执行技能
  rpc StreamExecuteSkill(ExecuteSkillRequest) returns (stream SkillExecutionChunk);

  // 创建新技能
  rpc CreateSkill(CreateSkillRequest) returns (Skill);

  // 更新技能
  rpc UpdateSkill(UpdateSkillRequest) returns (Skill);

  // 删除技能
  rpc DeleteSkill(DeleteSkillRequest) returns (DeleteSkillResponse);
}

message ListSkillsRequest {
  optional string category = 1;             // 按类别过滤
  optional string search = 2;               // 关键词搜索
  optional uint32 limit = 3;                // 返回条数上限
  optional uint32 offset = 4;               // 分页偏移
}

message GetSkillRequest {
  string skill_id = 1;                      // 技能 ID
}

message Skill {
  string id = 1;                            // 技能 ID
  string name = 2;                          // 技能名称
  string description = 3;                   // 技能描述
  string version = 4;                       // 版本号
  optional string author = 5;               // 作者
  repeated string platforms = 6;            // 支持平台
  repeated string tags = 7;                 // 标签
  optional string category = 8;             // 类别
  optional string content = 9;              // SKILL.md 内容
  map<string, string> metadata = 10;        // 扩展元数据
  google.protobuf.Timestamp created_at = 11;
  google.protobuf.Timestamp updated_at = 12;
  uint32 usage_count = 13;                  // 使用次数
  optional float average_score = 14;        // 平均评分
}

message SkillList {
  repeated Skill skills = 1;
  uint32 total_count = 2;
}

message ExecuteSkillRequest {
  string skill_id = 1;                      // 技能 ID
  string task = 2;                          // 任务描述
  map<string, string> parameters = 3;       // 执行参数
  optional string session_id = 4;           // 会话 ID
  optional bool stream = 5;                 // 是否流式执行
}

message ExecuteSkillResponse {
  string result = 1;                        // 执行结果
  bool success = 2;                         // 是否成功
  optional string error = 3;                // 错误信息
  optional TokenUsage usage = 4;            // Token 用量
  float execution_time_ms = 5;              // 执行耗时
}

message SkillExecutionChunk {
  oneof chunk_type {
    string text_delta = 1;                  // 文本增量
    string tool_call = 2;                   // 工具调用信息
    string progress = 3;                    // 进度信息
  }
  uint32 index = 4;
  optional bool done = 5;                   // 是否完成
}

message CreateSkillRequest {
  string name = 1;                          // 技能名称
  string description = 2;                   // 技能描述
  string content = 3;                       // SKILL.md 内容
  optional string category = 4;             // 类别
  repeated string tags = 5;                 // 标签
  map<string, string> metadata = 6;         // 扩展元数据
}

message UpdateSkillRequest {
  string skill_id = 1;                      // 技能 ID
  optional string name = 2;
  optional string description = 3;
  optional string content = 4;
  optional string category = 5;
  repeated string tags = 6;
  map<string, string> metadata = 7;
}

message DeleteSkillRequest {
  string skill_id = 1;
}

message DeleteSkillResponse {
  bool success = 1;
}
```

### 3.6 HermesAgent Service

```protobuf
// ─────────────────────────────────────────────────────
// HermesAgent — 完整代理执行服务
// ─────────────────────────────────────────────────────

service HermesAgent {
  // 非流式运行任务（Hermes 自主执行完整任务，返回最终结果）
  rpc RunTask(TaskRequest) returns (TaskResponse);

  // 流式运行任务（实时推送执行过程）
  rpc StreamTask(TaskRequest) returns (stream TaskChunk);

  // 获取 Agent 状态
  rpc GetStatus(AgentStatusRequest) returns (AgentStatus);

  // 取消正在运行的任务
  rpc CancelTask(CancelTaskRequest) returns (CancelTaskResponse);

  // 获取任务执行历史
  rpc GetTaskHistory(TaskHistoryRequest) returns (TaskHistoryResponse);
}

message TaskRequest {
  string task = 1;                          // 任务描述（必填）
  optional string system_prompt = 2;        // 系统提示词
  optional string model = 3;                // 模型选择
  optional uint32 max_iterations = 4;       // 最大迭代次数（默认 25）
  optional float temperature = 5;           // 温度
  optional string session_id = 6;           // 会话 ID
  optional string tenant_id = 7;            // 租户 ID
  map<string, string> metadata = 8;         // 自定义元数据
  optional bool enable_hitl = 9;            // 启用人工干预
  optional uint32 hitl_timeout_seconds = 10; // 人工审批超时（秒）
}

message TaskResponse {
  string result = 1;                        // 最终结果文本
  bool success = 2;                         // 是否成功
  uint32 iterations = 3;                    // 实际迭代次数
  TokenUsage usage = 4;                     // Token 用量
  float execution_time_ms = 5;              // 执行耗时
  repeated TaskStep steps = 6;              // 执行步骤摘要
  optional string error = 7;                // 错误信息
  AgentStatusEnum final_status = 8;         // 最终状态
}

message TaskStep {
  uint32 iteration = 1;                     // 迭代序号
  string action = 2;                        // 动作描述
  optional string thought = 3;              // 思考过程
  optional string tool_name = 4;            // 使用的工具
  optional string tool_result = 5;          // 工具结果摘要
  float duration_ms = 6;                    // 步骤耗时
}

message TaskChunk {
  oneof chunk_type {
    string text_delta = 1;                  // 文本增量
    string thought = 2;                     // 思考过程
    TaskStep step = 3;                      // 步骤信息
    string tool_call = 4;                   // 工具调用
    string tool_result = 5;                 // 工具结果
    HumanInputRequest hitl = 6;             // 人工干预请求
  }
  uint32 index = 7;
  optional AgentStatusEnum status = 8;
  optional bool done = 9;                   // 是否完成
}

message HumanInputRequest {
  string request_id = 1;                    // 请求 ID
  string prompt = 2;                        // 向用户展示的提示
  string type = 3;                          // "confirm" | "choice" | "text" | "review"
  repeated string options = 4;              // 选项（choice 类型时使用）
  optional string artifact = 5;             // 待审核内容（review 类型时使用）
  uint32 timeout_seconds = 6;               // 超时时间
}

message AgentStatusRequest {
  string session_id = 1;                    // 会话 ID
  optional string tenant_id = 2;            // 租户 ID
}

message AgentStatus {
  AgentStatusEnum status = 1;               // 当前状态
  optional string current_task = 2;         // 当前任务
  optional uint32 current_iteration = 3;    // 当前迭代次数
  optional uint32 total_iterations = 4;     // 总迭代次数
  optional TokenUsage usage = 5;            // Token 用量
  optional float uptime_seconds = 6;        // 运行时间
  optional string session_id = 7;           // 会话 ID
}

message CancelTaskRequest {
  string session_id = 1;                    // 会话 ID
  optional string reason = 2;               // 取消原因
}

message CancelTaskResponse {
  bool success = 1;
  optional string cancelled_step = 2;       // 取消时的步骤
}

message TaskHistoryRequest {
  optional string session_id = 1;
  optional uint32 limit = 2;
  optional uint32 offset = 3;
}

message TaskHistoryResponse {
  repeated TaskResponse tasks = 1;
  uint32 total_count = 2;
}
```

### 3.7 完整 proto 文件结构

```
hermes-proto/
├── hermes/
│   └── v1/
│       ├── hermes.proto              # 主文件（import 其他所有）
│       ├── common.proto              # 共享类型（枚举、Message、ToolCall、TokenUsage）
│       ├── provider.proto            # HermesProvider Service
│       ├── memory.proto              # HermesMemory Service
│       ├── skills.proto              # HermesSkills Service
│       └── agent.proto               # HermesAgent Service
├── gen/                              # 生成代码输出目录
│   ├── py/                           # Python (grpcio)
│   │   └── hermes/
│   │       └── v1/
│   │           ├── hermes_pb2.py
│   │           ├── hermes_pb2_grpc.py
│   │           ├── ...
│   └── ts/                           # TypeScript (@grpc/grpc-js)
│       └── hermes/
│           └── v1/
│               ├── hermes.ts
│               ├── hermes_grpc.ts
│               └── ...
├── buf.gen.yaml                      # Buf 生成配置
├── buf.yaml                          # Buf lint + breaking change 检测
└── README.md
```

---

## 4. 类型映射

### 4.1 Protobuf ↔ TypeScript ↔ Python 完整映射

| Protobuf Type | TypeScript (`@grpc/grpc-js`) | Python (`grpcio`) | 说明 |
|--------------|-------------------------------|-------------------|------|
| `string` | `string` | `str` | UTF-8 编码 |
| `int32` | `number` | `int` | 32 位有符号整数 |
| `uint32` | `number` | `int` | 32 位无符号整数 |
| `int64` | `number` / `Long` | `int` | 注意 JS 精度丢失，>2^53 用 Long |
| `float` | `number` | `float` | 32 位浮点 |
| `double` | `number` | `float` | 64 位浮点 |
| `bool` | `boolean` | `bool` | |
| `bytes` | `Buffer` / `Uint8Array` | `bytes` | 二进制数据 |
| `google.protobuf.Struct` | `Record<string, any>` / `JsonValue` | `dict` / `Mapping` | 任意结构化 JSON |
| `google.protobuf.Timestamp` | `Date` / `Timestamp` | `datetime` | ISO 8601 UTC |
| `google.protobuf.Empty` | `{}` | `google.protobuf.empty_pb2.Empty` | 空消息 |
| `oneof` | 联合类型 `{ type: "a", a: A }` | `WhichOneof()` 方法 | 互斥字段 |
| `enum` | `enum` → `number` / `string` | `IntEnum` | 编译时枚举 |
| `repeated T` | `T[]` | `List[T]` / `RepeatedCompositeContainer` | 列表 |
| `map<K,V>` | `Record<K, V>` | `Dict[K, V]` / `MessageMap` | 映射 |
| `optional T` | `T \| undefined` / `null` | `Optional[T]` | 可选字段（proto3） |
| `message` | `interface` / `class` | `class` (Message) | 消息类型 |

### 4.2 核心消息类型映射示例

```typescript
// TypeScript 生成的类型示例（@grpc/grpc-js + protobufjs）
// gen/ts/hermes/v1/provider.ts

export interface IChatRequest {
  messages: IMessage[];
  tools?: IToolDefinition[] | null;
  model: string;
  temperature?: number | null;
  maxTokens?: number | null;
  stream?: boolean | null;
  systemPrompt?: string | null;
  sessionId?: string | null;
  metadata?: { [key: string]: string } | null;
}

export interface IMessage {
  role: string;
  content: string;
  name?: string | null;
  toolCallId?: string | null;
  toolCalls?: IToolCall[] | null;
}

export interface IToolCall {
  id: string;
  name: string;
  args?: google.protobuf.Struct | null;
}
```

```python
# Python 生成的类型示例（grpcio-tools）
# gen/py/hermes/v1/provider_pb2.py

class ChatRequest(google.protobuf.message.Message):
    MESSAGES_FIELD_NUMBER: int
    TOOLS_FIELD_NUMBER: int
    MODEL_FIELD_NUMBER: int
    TEMPERATURE_FIELD_NUMBER: int
    MAX_TOKENS_FIELD_NUMBER: int
    STREAM_FIELD_NUMBER: int
    SYSTEM_PROMPT_FIELD_NUMBER: int
    SESSION_ID_FIELD_NUMBER: int
    METADATA_FIELD_NUMBER: int
    messages: "google.protobuf.internal.containers.RepeatedCompositeContainer[Message]"
    tools: "google.protobuf.internal.containers.RepeatedCompositeContainer[ToolDefinition]"
    model: str
    temperature: float
    max_tokens: int
    stream: bool
    system_prompt: str
    session_id: str
    metadata: "google.protobuf.internal.containers.ScalarMap[str, str]"

class ChatResponse(google.protobuf.message.Message):
    CONTENT_FIELD_NUMBER: int
    TOOL_CALLS_FIELD_NUMBER: int
    FINISH_REASON_FIELD_NUMBER: int
    USAGE_FIELD_NUMBER: int
    MODEL_FIELD_NUMBER: int
    SESSION_ID_FIELD_NUMBER: int
    content: str
    tool_calls: "google.protobuf.internal.containers.RepeatedCompositeContainer[ToolCall]"
    finish_reason: "FinishReason.ValueType"
    usage: "TokenUsage"
    model: str
    session_id: str
```

### 4.3 Hermes 特有类型适配

| Hermes Python 类型 | Protobuf 表示 | 说明 |
|-------------------|---------------|------|
| `AIAgent` | `HermesAgent.RunTask` | 完整的 Agent 执行封装 |
| `MemoryProvider` | `HermesMemory` Service | Provider 模式映射为 RPC |
| `SKILL.md` (YAML frontmatter) | `Skill` message | metadata 字段存储 frontmatter 扩展 |
| `ToolDefinition` (Hermes schema) | `ToolDefinition.parameters` (Struct) | JSON Schema 格式 |
| `ChatChunk` (Hermes generator) | Server Streaming ChatChunk | Generator → gRPC stream |
| `SessionDB` (SQLite) | 由 Hermes side 管理 | gRPC 无状态，不暴露内部存储 |
| `ContextEngine` | `GetContext` RPC | Token 预算管理在 Hermes 侧 |

---

## 5. 错误处理与超时策略

### 5.1 标准错误码

```protobuf
// 在 common.proto 中定义
enum GrpcErrorCode {
  // gRPC 标准错误码映射
  OK = 0;
  CANCELLED = 1;           // 请求被取消
  UNKNOWN = 2;             // 未知错误
  INVALID_ARGUMENT = 3;    // 请求参数无效
  DEADLINE_EXCEEDED = 4;   // 超时
  NOT_FOUND = 5;           // 资源不存在
  ALREADY_EXISTS = 6;      // 资源已存在
  PERMISSION_DENIED = 7;   // 权限不足
  RESOURCE_EXHAUSTED = 8;  // 资源耗尽（rate limit）
  FAILED_PRECONDITION = 9; // 前置条件不满足
  ABORTED = 10;            // 操作中止
  OUT_OF_RANGE = 11;       // 超出范围
  UNIMPLEMENTED = 12;      // 未实现
  INTERNAL = 13;           // 内部错误
  UNAVAILABLE = 14;        // 服务不可用
  DATA_LOSS = 15;          // 数据丢失
  UNAUTHENTICATED = 16;    // 未认证
}
```

### 5.2 业务错误详情

```protobuf
// 在 common.proto 中定义
message ErrorDetail {
  GrpcErrorCode code = 1;
  string message = 2;                    // 人类可读的错误描述
  string detail = 3;                     // 详细错误信息（可包含 stack trace）
  map<string, string> metadata = 4;      // 附加上下文
  optional uint32 retry_after_ms = 5;    // 建议重试间隔（毫秒）
}

// 使用方式：所有 Response 均内嵌 ErrorDetail
message ChatResponse {
  // ... 已有字段 ...
  optional ErrorDetail error = 10;       // 错误详情（成功时不设置）
}
```

**错误场景及对应码**：

| 场景 | gRPC Status Code | HTTP 等价 | 重试策略 |
|------|-----------------|-----------|----------|
| 参数缺失（model 为空） | `INVALID_ARGUMENT` | 400 | ❌ 不重试 |
| 模型不存在 | `NOT_FOUND` | 404 | ❌ 不重试 |
| LLM API 超时 | `DEADLINE_EXCEEDED` | 504 | ✅ 指数退避（3 次） |
| LLM API rate limit | `RESOURCE_EXHAUSTED` | 429 | ✅ 等待后重试（按 `retry_after_ms`） |
| LLM API 临时错误 | `UNAVAILABLE` | 503 | ✅ 指数退避（3 次） |
| Hermes Agent 内部异常 | `INTERNAL` | 500 | ❌ 不重试（需人工排查） |
| 请求取消 | `CANCELLED` | 499 | ❌ 不重试 |
| 记忆后端连接失败 | `UNAVAILABLE` | 503 | ✅ 指数退避（2 次） |
| 技能不存在 | `NOT_FOUND` | 404 | ❌ 不重试 |
| 租户未授权 | `PERMISSION_DENIED` | 403 | ❌ 不重试 |

### 5.3 重试策略

```typescript
// TypeScript 客户端重试策略（harness/src/hermes/retry.ts）

interface RetryConfig {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
  retryableStatusCodes: number[];  // [UNAVAILABLE, DEADLINE_EXCEEDED, RESOURCE_EXHAUSTED]
}

const DEFAULT_RETRY: RetryConfig = {
  maxRetries: 3,
  baseDelayMs: 100,
  maxDelayMs: 5000,
  retryableStatusCodes: [4, 8, 14],  // DEADLINE_EXCEEDED, RESOURCE_EXHAUSTED, UNAVAILABLE
};

// 指数退避 + 抖动
function calculateBackoff(attempt: number, config: RetryConfig): number {
  const delay = Math.min(
    config.baseDelayMs * Math.pow(2, attempt),
    config.maxDelayMs
  );
  // 增加 ±25% 随机抖动，防止惊群效应
  const jitter = delay * (0.75 + Math.random() * 0.5);
  return Math.floor(jitter);
}
```

```python
# Python 服务端重试装饰器（hermes_agent/grpc_server/retry.py）

import asyncio
from functools import wraps
from grpc import StatusCode

def with_server_retry(max_retries=2, base_delay=0.1):
    """服务端内部 LLM 调用重试装饰器（用于 grpc servicer）"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, request, context):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(self, request, context)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries and _is_retryable(e):
                        delay = base_delay * (2 ** attempt) * (0.75 + 0.5 * random())
                        await asyncio.sleep(delay)
                        continue
                    raise
            raise last_error
        return wrapper
    return decorator

def _is_retryable(error: Exception) -> bool:
    """判断是否可重试"""
    # LLM API 超时、rate limit、临时网络错误
    retryable_msgs = ["timeout", "rate limit", "too many requests",
                      "503", "502", "temporary", "internal server"]
    error_str = str(error).lower()
    return any(msg in error_str for msg in retryable_msgs)
```

### 5.4 超时配置

```typescript
// TypeScript 客户端超时配置

interface TimeoutConfig {
  // 非流式 Chat
  chatTimeoutMs: number;           // 默认 60_000 (60s)
  // 流式 Chat（整体超时）
  streamChatTimeoutMs: number;     // 默认 300_000 (5min)
  // 流式首 chunk 超时
  streamFirstChunkTimeoutMs: number; // 默认 10_000 (10s)
  // 记忆操作超时
  memoryTimeoutMs: number;         // 默认 5_000 (5s)
  // 技能执行超时
  skillTimeoutMs: number;          // 默认 120_000 (2min)
  // Agent 任务超时
  agentTaskTimeoutMs: number;      // 默认 600_000 (10min)
}

const DEFAULT_TIMEOUTS: TimeoutConfig = {
  chatTimeoutMs: 60_000,
  streamChatTimeoutMs: 300_000,
  streamFirstChunkTimeoutMs: 10_000,
  memoryTimeoutMs: 5_000,
  skillTimeoutMs: 120_000,
  agentTaskTimeoutMs: 600_000,
};
```

```typescript
// gRPC 客户端调用时设置 deadline

import { credentials } from "@grpc/grpc-js";

function createHermesClient(address: string, timeouts: TimeoutConfig) {
  const client = new HermesProviderClient(
    address,
    credentials.createInsecure()
  );

  return {
    async chat(request: IChatRequest): Promise<IChatResponse> {
      const deadline = new Date();
      deadline.setMilliseconds(deadline.getMilliseconds() + timeouts.chatTimeoutMs);
      return new Promise((resolve, reject) => {
        client.chat(request, { deadline }, (err, response) => {
          if (err) reject(err);
          else resolve(response);
        });
      });
    },

    streamChat(request: IChatRequest): AsyncGenerator<IChatChunk> {
      const deadline = new Date();
      deadline.setMilliseconds(deadline.getMilliseconds() + timeouts.streamChatTimeoutMs);
      const call = client.streamChat(request, { deadline });
      // ... AsyncGenerator 实现
    },
  };
}
```

### 5.5 熔断机制

```typescript
// TypeScript 熔断器（harness/src/hermes/circuit-breaker.ts）

enum CircuitState {
  CLOSED,    // 正常
  OPEN,      // 熔断
  HALF_OPEN, // 半开（尝试恢复）
}

class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount = 0;
  private lastFailureTime = 0;

  constructor(
    private readonly thresholdCount = 5,        // 连续失败次数阈值
    private readonly recoveryTimeoutMs = 30_000, // 恢复超时（30秒）
    private readonly halfOpenMaxRequests = 3,    // 半开状态最大请求数
  ) {}

  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (Date.now() - this.lastFailureTime >= this.recoveryTimeoutMs) {
        this.state = CircuitState.HALF_OPEN;
      } else {
        throw new Error("Circuit breaker is OPEN");
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (err) {
      this.onFailure();
      throw err;
    }
  }

  private onSuccess() {
    this.failureCount = 0;
    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.CLOSED;
      logger.info("Circuit breaker recovered, back to CLOSED");
    }
  }

  private onFailure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    if (this.state === CircuitState.HALF_OPEN ||
        this.failureCount >= this.thresholdCount) {
      this.state = CircuitState.OPEN;
      logger.warn(`Circuit breaker OPEN after ${this.failureCount} failures`);
    }
  }
}
```

---

## 6. 流式响应设计

### 6.1 Server Streaming 模式

使用 gRPC **Server Streaming** RPC 模式：

```
Client (Harness TS)                    Server (Hermes Python)
     │                                       │
     │────── StreamChat(ChatRequest) ────────│
     │                                       │
     │  ◄──── ChatChunk{content_delta:"你好"} │
     │  ◄──── ChatChunk{content_delta:"世界"} │
     │  ◄──── ChatChunk{tool_call_delta{...}} │
     │  ◄──── ChatChunk{content_delta:"!"}    │
     │  ◄──── ChatChunk{finish_reason:STOP,   │
     │                  usage{...}}           │
     │                                       │
     │  (stream closed by server)            │
```

### 6.2 Chunk 格式设计

**Chunk 类型矩阵**：

| `oneof` 类型 | 何时发送 | 包含字段 |
|-------------|---------|---------|
| `content_delta` | LLM 吐出文本 token 时 | 纯文本片段 |
| `tool_call_delta` | LLM 调用工具时 | id, name, args_delta (JSON 片段) |
| `finish_reason` | 流结束时 | 枚举值 |
| `usage` | 流结束时 | input/output/cached tokens |

**典型流式 Chat 输出示例**：

```
Chunk 1:  { index: 0, content_delta: "基于" }
Chunk 2:  { index: 1, content_delta: "您的需求" }
Chunk 3:  { index: 2, content_delta: "，我建议" }
Chunk 4:  { index: 3, content_delta: "如下方案：" }
...
Chunk N:  { index: N, content_delta: "\n\n"} 
Chunk N+1:{ index: N+1, tool_call_delta: {id: "call_1", name: "search_web", args_delta: ""} }
Chunk N+2:{ index: N+2, tool_call_delta: {id: "call_1", args_delta: "{"query": "天"} }
Chunk N+3:{ index: N+3, tool_call_delta: {id: "call_1", args_delta: "气预报"}"} }
Chunk N+4:{ index: N+4, finish_reason: TOOL_CALLS, usage: {input: 150, output: 80} }
```

### 6.3 取消机制

```typescript
// TypeScript 侧 — 使用 AbortController 取消流

class HermesStreamClient {
  private call: ClientReadableStream<IChatChunk> | null = null;

  async *streamChat(
    request: IChatRequest,
    signal?: AbortSignal
  ): AsyncGenerator<IChatChunk> {
    const deadline = new Date();
    deadline.setMilliseconds(deadline.getMilliseconds() + 300_000);

    this.call = this.client.streamChat(request, { deadline });

    // 注册取消回调
    if (signal) {
      signal.addEventListener("abort", () => {
        this.call?.cancel();
        this.call = null;
      });
    }

    try {
      for await (const chunk of this.call) {
        yield chunk;
      }
    } finally {
      this.call = null;
    }
  }

  cancel() {
    this.call?.cancel();
    this.call = null;
  }
}
```

```python
# Python 侧 — gRPC context.cancel() 感知

class HermesProviderServicer(hermes_pb2_grpc.HermesProviderServicer):
    async def StreamChat(self, request, context):
        """流式 Chat gRPC 服务端实现"""

        async def generate():
            try:
                async for chunk in self._llm_chat(request):
                    # 检查客户端是否已取消
                    if context.is_active() is False:
                        logger.info("Client cancelled stream")
                        return
                    yield chunk
            except Exception as e:
                logger.error(f"Stream error: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

        return generate()
```

### 6.4 背压处理

```python
# Python 服务端 — 使用 asyncio.Queue 实现背压

import asyncio
from typing import AsyncIterator

class BackpressureStream:
    """带背压控制的流式发送器"""

    def __init__(self, max_queue_size: int = 64):
        self.queue: asyncio.Queue[Optional[ChatChunk]] = asyncio.Queue(
            maxsize=max_queue_size
        )

    async def produce(self, chunk: ChatChunk):
        """生产者：LLM 输出 → 队列"""
        await self.queue.put(chunk)

    async def finish(self):
        """停止信号"""
        await self.queue.put(None)  # Sentinel

    async def consume(self) -> AsyncIterator[ChatChunk]:
        """消费者：队列 → gRPC stream"""
        while True:
            chunk = await self.queue.get()
            if chunk is None:
                break
            yield chunk
            self.queue.task_done()
```

```typescript
// TypeScript 客户端 — 流量控制

async function* backpressureAdapter(
  stream: AsyncGenerator<IChatChunk>,
  maxBufferSize: number = 128
): AsyncGenerator<IChatChunk> {
  const buffer: IChatChunk[] = [];
  let iterator: AsyncIterator<IChatChunk> | null = null;

  while (true) {
    // 当缓冲区未满时，预取更多数据
    if (buffer.length < maxBufferSize && !iterator) {
      iterator = stream[Symbol.asyncIterator]();
    }

    if (buffer.length > 0) {
      yield buffer.shift()!;
    } else if (iterator) {
      const { value, done } = await iterator.next();
      if (done) break;
      // 可以在这里做节流
      yield value;
    } else {
      break;
    }
  }
}
```

### 6.5 断线重连

```typescript
// 流式断线重连策略

async function* streamWithReconnect(
  request: IChatRequest,
  client: HermesStreamClient,
  maxRetries: number = 3
): AsyncGenerator<IChatChunk> {
  let accumulatedContent = "";

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // 重连时传递已累积的内容，让 LLM 继续
      if (attempt > 0) {
        request = {
          ...request,
          messages: [
            ...request.messages,
            { role: "assistant", content: accumulatedContent }
          ],
        };
      }

      const stream = client.streamChat(request);
      for await (const chunk of stream) {
        if (chunk.contentDelta) {
          accumulatedContent += chunk.contentDelta;
        }
        yield chunk;
      }
      return; // 正常结束
    } catch (err) {
      if (attempt >= maxRetries) throw err;
      const delay = Math.min(1000 * Math.pow(2, attempt), 10_000);
      await new Promise(r => setTimeout(r, delay));
      logger.warn(`Stream reconnect attempt ${attempt + 1}`);
    }
  }
}
```

---

## 7. TS/Python 双栈能力评估

### 7.1 团队现有能力评估

| 能力维度 | TypeScript | Python |
|---------|:----------:|:------:|
| **gRPC 服务端实现** | `@grpc/grpc-js`（需学习） | `grpcio`（需学习） |
| **gRPC 客户端实现** | `@grpc/grpc-js`（需学习） | `grpcio`（需学习） |
| **Proto 编译** | `protoc` + `protobuf-ts` / `protobufjs` | `grpcio-tools` / `buf` |
| **流式处理** | ✅ `AsyncIterator` / `for await...of` | ✅ `AsyncGenerator` / `async for` |
| **并发模型** | ✅ 事件循环 / `Promise.all` | ✅ `asyncio` / `asyncio.gather` |
| **单元测试** | ✅ Vitest / Jest | ✅ pytest |
| **HTTP/2 理解** | ⚠️ 基础了解 | ⚠️ 基础了解 |
| **Protobuf 序列化** | ❌ 无经验 | ❌ 无经验 |
| **gRPC 流式通信** | ❌ 无经验 | ❌ 无经验 |
| **熔断/重试模式** | ✅ 已有实现 | ⚠️ 部分实现 |
| **Hermes Agent 源码** | ❌ 不涉及 | ✅ 当前团队已分析 |
| **Harness Agent Loop** | ✅ 当前团队有 | ❌ 不涉及 |

**评估结论**：
- **TS 侧**：团队熟悉 Harness 的 Agent Loop 和事件系统，但 gRPC/Protobuf 是新技能栈
- **Python 侧**：团队熟悉 Hermes Agent 源码和 asyncio，但 gRPC/Protobuf 也是新技能栈
- **共有短板**：Protobuf schema 设计、gRPC 服务端/客户端实现、流式通信模式

### 7.2 技能差距分析

**需要掌握的新能力**：

| 技能 | 预估学习周期 | 优先级 | 学习资源 |
|------|:----------:|:------:|---------|
| Protobuf Schema 设计 | 2-3 天 | P0 | [Protocol Buffers 官方教程](https://protobuf.dev/) |
| `grpcio` Python 服务端 | 3-5 天 | P0 | [gRPC Python 快速开始](https://grpc.io/docs/languages/python/quickstart/) |
| `@grpc/grpc-js` TS 客户端 | 2-3 天 | P0 | [gRPC Node.js 快速开始](https://grpc.io/docs/languages/node/quickstart/) |
| gRPC Server Streaming 模式 | 1-2 天 | P0 | gRPC 流式 RPC 文档 |
| Buf 工具链（lint/breaking） | 1 天 | P1 | [Buf 官方文档](https://buf.build/docs/) |
| 熔断器 + 重试模式 gRPC 实现 | 1-2 天 | P1 | 参考 Microsoft Polly / resilience4j |
| 性能调优（gRPC 性能） | 2-3 天 | P2 | gRPC Performance Best Practices |

**已具备的可复用能力**：

| 现有能力 | 所在代码 | 可复用程度 |
|----------|---------|:----------:|
| Harness LLMProvider 接口 | `provider.ts` | 直接继承（HermesProvider implements LLMProvider） |
| AsyncGenerator 流式处理 | `loop.ts` | 直接复用（`for await...of` 模式） |
| Python asyncio 并发 | `hermes_state.py` 等 | 直接复用 |
| 重试工具函数 | `retry_utils.py`（Hermes） | 需要适配 gRPC 错误码 |
| 熔断模式（前端） | 现有 Worker 通信 | 需要重写为 gRPC 版本 |
| 日志/追踪 | `hermes_logging.py` | 直接复用 |

**缺失的关键能力**（需培训或招聘填补）：

1. **Proto 版本管理**：proto 文件的向后兼容性管理（breaking change 检测）
2. **gRPC 生产运维**：gRPC 健康检查、负载均衡、连接池管理
3. **流式通信调试**：gRPCurl / gRPCui / 协议分析

### 7.3 培训方案

#### 分阶段学习路径

**第一阶段（第 1-3 天）：Protobuf 基础 + gRPC 概念**

| 天数 | 内容 | 形式 | 产出物 |
|:----:|------|------|--------|
| 1 | Protobuf 语法（message/enum/oneof/service） | 集中培训 2h + 自学 | 一个小型 .proto 文件 |
| 2 | gRPC 架构（HTTP/2/Streaming/Deadline） | 视频 + 文档 | 理解 4 种 RPC 模式 |
| 3 | Buf 工具链（lint/breaking/gen） | 动手实践 | 配置 buf.gen.yaml |

**第二阶段（第 4-7 天）：Python gRPC 服务端实现**

| 天数 | 内容 | 形式 | 产出物 |
|:----:|------|------|--------|
| 4 | `grpcio` 快速入门 + Chat Servicer | 代码实践 | 能响应 Chat 请求 |
| 5 | Server Streaming + 背压控制 | 代码实践 | 完整的 StreamChat |
| 6 | 错误处理 + 拦截器（Interceptor） | 代码实践 | 统一错误处理层 |
| 7 | 健康检查 + 优雅关闭 | 代码实践 | 可生产的 gRPC 服务 |

**第三阶段（第 8-10 天）：TypeScript gRPC 客户端实现**

| 天数 | 内容 | 形式 | 产出物 |
|:----:|------|------|--------|
| 8 | `@grpc/grpc-js` 快速入门 | 代码实践 | 能调用 Chat RPC |
| 9 | 流式客户端 + 取消 + 重连 | 代码实践 | 完整的 StreamChat 客户端 |
| 10 | 熔断器 + 重试 + 超时 | 代码实践 | HermesClient 封装 |

#### 培训方式

| 方式 | 内容 | 预估时长（人天） | 费用 |
|------|------|:--------------:|:----:|
| 内部技术分享（架构师主讲） | Protobuf + gRPC 原理 | 0.5 | 免费 |
| 在线课程（Udemy/Coursera） | "gRPC Master Class" | 2-3（自学） | $50-100/人 |
| 官方文档 + 动手实践 | gRPC.io 官方教程 | 3-5（自学） | 免费 |
| 代码 Review + Pair Programming | HermesProvider 实现 | 2-3 | - |
| **合计** | | **5-10 人天** | **低** |

### 7.4 招聘方案

#### 岗位 JD 建议

**岗位名称**：资深基础设施工程师（gRPC + AI Infra）

**关键技能要求**：
- 精通 **Protocol Buffers**（设计、版本管理、性能调优）
- 精通 **gRPC**（Server Streaming、Interceptor、Deadline Propagation）
- 熟练 **Python**（asyncio、grpcio）或 **TypeScript**（@grpc/grpc-js）
- 了解 **LLM 推理架构**（流式推理、Token 管理）
- 有 **K8s/服务网格** 经验者优先（Istio gRPC 负载均衡）
- 有 **AI Agent** 系统经验者优先

**加分项**：
- 为开源 gRPC 生态做过贡献
- 熟悉 Hermes Agent / LangChain / AutoGPT 等 Agent 框架
- 有分布式系统可靠性工程经验（熔断、重试、超时）

**建议薪资范围**：对标 P6-P7（高级工程师）

#### 推荐招聘渠道

| 渠道 | 适合岗位 | 预期周期 | 预估成本 |
|------|---------|:--------:|:--------:|
| 内部转岗 | 已有 gRPC 经验的内部团队 | 1-2 周 | 低 |
| 猎头（中高端） | 资深 Infra 工程师 | 2-4 周 | 年薪 20-25% |
| Boss直聘/拉勾 | 高级后端工程师 | 2-4 周 | 免费/按效果 |
| GitHub 技术社区 | 开源贡献者 | 4-8 周 | 免费 |
| V2EX / 技术论坛 | 远程/全职 | 2-4 周 | 免费 |

#### 推荐策略

> **优先内部培训（推荐），招聘作为备选**

因为：
1. gRPC 本身学习曲线不陡（5-10 人天即可上手）
2. 团队已有 Python asyncio + TS AsyncGenerator 基础
3. 招聘周期长（2-4 周），不如培训现有团队来得快
4. 该领域人才稀缺（gRPC + AI Agent 双技能集）

**具体建议**：
1. **第 1 周**：架构师带队完成 P0 核心（Provider Service proto + Python 服务端）
2. **第 2 周**：TS 客户端对接 + 端到端测试
3. **同时**：发布招聘 JD，寻找有 gRPC 生产经验的 senior engineer 加入
4. **第 3-4 周**：新成员加入后 review 现有实现 + 补充 Memory/Skills Service

---

## 8. 实现计划

### 8.1 里程碑

```
Phase 1 (P0) — 核心链路打通        Phase 2 (P1) — 能力完善
╔════════════════════════════════╗ ╔════════════════════════════════╗
║  第 1-2 周                     ║ ║  第 3-4 周                     ║
╠════════════════════════════════╣ ╠════════════════════════════════╣
║ T01: 项目基础设施               ║ ║ T04: Memory + Skills 服务     ║
║     proto 文件 + 编译工具链      ║ ║     MemoryService 实现        ║
║     buf 配置                    ║ ║     SkillsService 实现        ║
║     Python 服务端骨架            ║ ║     TS 客户端集成             ║
║     TS 客户端骨架                ║ ╚════════════════════════════════╝
║                                ║
║ T02: HermesProvider 服务        ║ Phase 3 (P2) — 生产加固
║     Chat + StreamChat 实现      ║ ╔════════════════════════════════╗
║     TS 客户端集成到 loop.ts     ║ ║  第 5-6 周                     ║
║     端到端流式测试              ║ ╠════════════════════════════════╣
║                                ║ ║ T05: AgentService + 生产部署   ║
║ T03: 双重执行模式                ║ ║     HermesAgent 服务           ║
║     透明模式（Harness 执行工具）  ║ ║     熔断 + 重试 + 监控         ║
║     委托模式（Hermes 执行工具）  ║ ║     集成测试 + 性能测试        ║
║     GetModels + GetEmbedding    ║ ║     文档 + 运维手册            ║
╚════════════════════════════════╝ ╚════════════════════════════════╝
```

### 8.2 任务分解

| 任务 ID | 任务名称 | 源文件 | 依赖 | 优先级 |
|---------|---------|--------|:----:|:------:|
| T01 | **项目基础设施** | `hermes-proto/`（buf.yaml, buf.gen.yaml, proto 文件）+ `hermes-agent/grpc_server/`（server.py, __init__.py, config.py）+ `harness/src/hermes/`（client.ts, config.ts） | - | P0 |
| T02 | **HermesProvider 核心服务** | `hermes-agent/grpc_server/provider_service.py` + `hermes-agent/grpc_server/adapter.py` + `harness/src/hermes/provider.ts` + `harness/src/hermes/types.ts` + 测试文件 | T01 | P0 |
| T03 | **双重执行模式 + 模型/嵌入** | `hermes-agent/grpc_server/provider_service.py`（透明/委托模式切换）+ `hermes-agent/grpc_server/embedding.py` + `harness/src/hermes/provider.ts`（GetModels/GetEmbedding） | T02 | P1 |
| T04 | **Memory + Skills 服务** | `hermes-agent/grpc_server/memory_service.py` + `hermes-agent/grpc_server/skills_service.py` + `harness/src/hermes/memory-client.ts` + `harness/src/hermes/skills-client.ts` + 测试文件 | T01 | P1 |
| T05 | **HermesAgent 服务 + 生产部署** | `hermes-agent/grpc_server/agent_service.py` + `hermes-agent/grpc_server/interceptors.py`（熔断/重试/监控）+ `harness/src/hermes/agent-client.ts` + `harness/src/hermes/circuit-breaker.ts` + 集成测试 + Dockerfile | T02, T04 | P2 |

### 8.3 工作量估算

| 任务 | 描述 | 预估工时 | 人员 |
|:----:|------|:--------:|:----:|
| T01 | 项目基础设施 | 3-5 人天 | 1 TS + 1 Python |
| T02 | HermesProvider 核心服务 | 5-8 人天 | 1 TS + 1 Python |
| T03 | 双重执行模式 + 模型/嵌入 | 3-5 人天 | 1 Python |
| T04 | Memory + Skills 服务 | 5-8 人天 | 1 TS + 1 Python |
| T05 | HermesAgent 服务 + 生产部署 | 5-8 人天 | 1 TS + 1 Python |
| **合计** | | **21-34 人天** | **2-3 人** |

### 8.4 先决条件

1. **Hermes Agent 以独立服务方式运行**（当前为 CLI 交互式启动，需改造为可后台运行的 gRPC 服务）
2. **Python 3.11+**（gRPC asyncio 支持）
3. **TypeScript 5.x**（`@grpc/grpc-js` 要求）
4. **Buf CLI**（proto 编译和 lint）
5. **poetry** 或 **uv**（Python 依赖管理）

---

## 附录 A：序列流图

### A.1 流式 Chat 完整调用流程

```
Harness TS                        Hermes Python                       LLM API
    │                                   │                               │
    │ 1. runLoop(task)                  │                               │
    │  ┌──────────────┐                 │                               │
    │  │ assemblePrompt│                 │                               │
    │  └──────┬───────┘                 │                               │
    │         │                         │                               │
    │ 2. HermesProvider.chat(req)       │                               │
    │    ───────────────────────────────│                               │
    │         │                         │                               │
    │         │ 3. 验证请求 / 鉴权       │                               │
    │         │ 4. 消息格式转换           │                               │
    │         │ 5. 调用 LLM adpater     │                               │
    │         │    ──────────────────────────────────────────────────────
    │         │                         │                               │
    │         │                 6. stream ChatCompletion                │
    │         │    ◄────────────────────────────────────────────────────
    │         │                         │                               │
    │  ◄──── 7. ChatChunk{text}    ─────│                               │
    │  onText() → ws.send(text:delta)   │                               │
    │         │                         │                               │
    │  ◄──── 8. ChatChunk{text}    ─────│                               │
    │         │                         │                               │
    │  ◄──── 9. ChatChunk{tool_call}───│                               │
    │         │                         │                               │
    │◄──── 10. ChatChunk{done,usage}───│                               │
    │         │                         │                               │
    │ 11. Stream 关闭                   │                               │
    │         │                         │                               │
    │ 12. 解析 tool_calls               │                               │
    │ 13. 执行工具循环                   │                               │
    │         │                         │                               │
    │ 14. 如果还有 tool_call → 继续迭代   │                               │
    │         │                         │                               │
    │ 15. 无 tool_call → 返回最终结果    │                               │
```

### A.2 记忆保存和搜索流程

```
Harness TS                        Hermes Python                   Memory Backend
    │                                   │                              │
    │ 1. HermesMemory.Save(req)         │                              │
    │    ───────────────────────────────│                              │
    │                                   │                              │
    │         │ 2. 提取内容 + 生成嵌入   │                              │
    │         │    ─────────────────────────────────────────────────────
    │         │                  3. embedding API                     │
    │         │    ◄───────────────────────────────────────────────────
    │         │                              │                        │
    │         │ 4. 存储到 Memory Provider    │                        │
    │         │    ──────────────────────────│                        │
    │         │                              │                        │
    │         │      5. SQLite/S3 write      │                        │
    │         │      ──────────────────────────────────────────────────
    │         │                              │                        │
    │  ◄──── 6. SaveResponse{memory_id}───│                        │
    │                                   │                              │
    │                                   │                              │
    │ 7. HermesMemory.Search(req)       │                              │
    │    ───────────────────────────────│                              │
    │                                   │                              │
    │         │ 8. 查询嵌入向量          │                              │
    │         │ 9. 向量相似度搜索        │                              │
    │         │    ─────────────────────────────────────────────────────
    │         │                              │                        │
    │         │      10. 搜索结果            │                        │
    │         │      ◄─────────────────────────────────────────────────
    │         │                              │                        │
    │  ◄──── 11. SearchResponse{items}────│                        │
```

### A.3 Agent 任务执行流程

```
Harness TS                        Hermes Python                      Tools/LLM
    │                                   │                               │
    │ 1. HermesAgent.RunTask(req)       │                               │
    │    ───────────────────────────────│                               │
    │                                   │                               │
    │         │ 2. 启动 AIAgent          │                               │
    │         │ 3. 初始化 Memory        │                               │
    │         │ 4. 加载 Skills          │                               │
    │         │                         │                               │
    │         │ ┌── Agent Loop ──────┐  │                               │
    │         │ │ 5. assemblePrompt  │  │                               │
    │         │ │ 6. call LLM        │──┼───────────────────────────────
    │         │ │ 7. 解析响应        │  │                               │
    │         │ │ 8. 执行工具        │──┼──── tool.execute() ──────────▶
    │         │ │ 9. 保存到 Memory   │  │                               │
    │         │ │ 10. 结果注入下一轮  │  │                               │
    │         │ └────────────────────┘  │                               │
    │         │                         │                               │
    │  ◄──── 11. TaskResponse{result} ──│                               │
```

---

## 附录 B：关键决策记录

| 决策 ID | 决策 | 选项 | 选择 | 理由 |
|---------|------|------|:----:|------|
| ADR-001 | TS/Python 桥接协议 | gRPC/REST/WS/IPC | **gRPC** | 强类型 + 流式原生 + HTTP/2 |
| ADR-002 | Proto 包组织 | 单文件/多文件 | **多文件** | 按服务拆分，易于维护 |
| ADR-003 | 流式模式 | Server/Bidirectional Streaming | **Server Streaming** | LLM 流式是单向（服务端→客户端） |
| ADR-004 | 取消机制 | gRPC cancel / 自定义消息 | **gRPC cancel** | 原生支持，无需额外协议 |
| ADR-005 | 会话管理 | 有状态/无状态 | **无状态** | Harness 维护状态，Hermes 不持有 |
| ADR-006 | 工具执行模式 | 透明/委托 | **双模式** | 根据场景灵活选择 |
| ADR-007 | 嵌入向量生成 | Hermes 侧/Harness 侧 | **Hermes 侧** | 减少跨语言传输，利用 Hermes 的 LLM 适配器 |
| ADR-008 | 熔断器位置 | 客户端/服务端 | **客户端** | Harness 侧控制降级逻辑更灵活 |

---

*文档结束 — Bob (Architect)*
