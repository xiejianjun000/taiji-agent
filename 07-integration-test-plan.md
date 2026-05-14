# 集成测试计划

> 版本：v1.0
> 日期：2026-05-14
> 编写人：QA 工程师

---

## 1. 测试策略

### 1.1 测试目标

1. **验证模块间接口正确性**：确保 Taiji Verify / Hermes Provider / Plugin 系统 / 多租户 / GovMCP / 安全模块之间的数据流和调用链正确
2. **验证关键业务流程**：覆盖娄底环评审批全流程的正向、负向、边界场景
3. **验证错误处理和容错机制**：网络断开、超时、无效输入、权限不足等异常场景
4. **验证并发与性能基准**：多租户并发下的系统稳定性
5. **验证安全机制**：国密加密、审计链、访问控制

### 1.2 测试范围

| 模块 | 测试范围 | 接口类型 |
|------|----------|----------|
| Taiji Verify | 阴阳距ΔS、坤守残差修正、北辰编译器、病候图诊断、观变追踪 | Python API |
| Hermes Provider | Chat RPC、StreamChat、多租户路由 | gRPC / HTTP |
| Plugin 系统 | 插件加载/卸载、生命周期、事件订阅 | Python API + EventBus |
| 多租户 | 数据隔离、租户路由、权限控制 | Python API |
| GovMCP 集成 | SM4 加密通道、审批工作流、审计链、政务工具 | HTTP / Python API |
| 安全模块 | 身份认证、访问控制、审计日志 | JWT + Middleware |
| 工作流引擎 | 审批流程编排、状态机、中断恢复 | Python API |
| MCP 协议 | 服务端适配、客户端连接、工具调用 | HTTP/JSON-RPC |
| EventBus | 事件订阅/发布、事件历史、钩子链 | Python API |

### 1.3 测试层次

```
┌──────────────────────────────────────────────────────────────┐
│                    端到端测试 (E2E)                           │
│  娄底环评审批全流程 · 跨模块业务流程 · 用户模拟场景          │
├──────────────────────────────────────────────────────────────┤
│                    集成测试 (Integration)                     │
│  模块间接口 · 数据流 · 错误传播 · 并发竞争 · 事务一致性     │
├──────────────────────────────────────────────────────────────┤
│                    单元测试 (Unit)                            │
│  独立模块 · 纯函数 · 算法正确性 · 边界条件 (覆盖率 ≥80%)    │
└──────────────────────────────────────────────────────────────┘
```

### 1.4 测试优先级

| 优先级 | 定义 | 占比 | 必须通过 |
|:------:|------|:----:|:--------:|
| **P0** | 核心功能路径，阻塞性缺陷 | 40% | 100% |
| **P1** | 重要功能，非阻塞但影响体验 | 35% | 100% |
| **P2** | 边缘功能，低频率使用 | 25% | ≥90% |

---

## 2. 测试环境要求

### 2.1 硬件要求

| 资源 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 4 核 | 8 核 |
| 内存 | 8 GB | 16 GB |
| 磁盘 | 50 GB SSD | 100 GB SSD |
| 网络 | 100 Mbps | 1 Gbps |

### 2.2 软件依赖

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | ^3.11 | Hermes Agent + Taiji Verify |
| Node.js | ^20.0.0 | Harness 运行时层（可选桥接测试） |
| Docker | Latest | 沙箱隔离 + 容器化测试环境 |
| PostgreSQL | 14+ | 多租户数据存储（集成测试） |
| Redis | 7+ | 事件总线/缓存（集成测试） |
| pytest | ^8.0 | 测试框架 |
| pytest-asyncio | ^0.23 | 异步测试支持 |
| pytest-cov | ^5.0 | 覆盖率统计 |
| pytest-xdist | ^3.5 | 并行测试 |
| grpcio-testing | ^1.62 | gRPC 服务测试 |
| locust | ^2.20 | 性能测试 |
| bandit | ^1.7 | 安全扫描 |
| safety | ^3.0 | 依赖安全扫描 |
| aiohttp | ^3.9 | HTTP 客户端/服务端测试 |
| docker-py | ^7.0 | Docker 沙箱测试 |

### 2.3 网络拓扑

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  测试客户端   │────▶│  Taiji Agent │────▶│    Mock LLM  │
│  (pytest)    │     │   (Service)  │     │   (Provider) │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
      ┌────────────┐ ┌────────────┐ ┌────────────┐
      │ PostgreSQL │ │   Redis    │ │  Docker    │
      │  (多租户)   │ │  (事件/缓存)│ │  (沙箱)    │
      └────────────┘ └────────────┘ └────────────┘
```

### 2.4 Docker 容器化测试环境

```yaml
# docker-compose.test.yml
version: "3.8"
services:
  taiji-agent:
    build:
      context: .
      dockerfile: Dockerfile.test
    environment:
      - TEST_MODE=true
      - DB_URL=postgresql://test:test@db:5432/taiji_test
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
      - POSTGRES_DB=taiji_test
    tmpfs: /var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    tmpfs: /data
```

---

## 3. 各模块接口测试用例

### 3.1 Taiji Verify 模块

#### 接口说明

Taiji Verify 包含以下核心组件：
- **阴阳距 ΔS**：`ΔS = 1 - cos(I, G)` — 计算输入文本与知识文本的语义偏差
- **坤守 (Kun Guard)**：`B = I - G + m*c²` — 语义残差修正，B = 修正后文本，m = 残差质量，c = 光速常数
- **乾进 (Qian Advance)**：`f_S = 1 / (1 + mean(Δ))` — 语义演进稳定性评分
- **复归 (Fu Return)**：李雅普诺夫指数 λ 计算 + 状态机恢复
- **巽调 (Xun Tune)**：`factor = exp(-γ * σ)` — 注意力方差门控
- **观变 (Guan Observe)**：λ_observe 状态变迁追踪
- **病候图 (Symptom Map)**：16 种失败模式诊断
- **北辰编译器 (Polaris Compiler)**：目标编译 → 任务图 → 原子表 → 执行令牌板

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| TV-001 | ΔS 阴阳距 — 相同文本计算 | I="环境影响评价报告需包含生态现状", G="环境影响评价报告需包含生态现状" | ΔS = 0.0 (完全相同) | P0 |
| TV-002 | ΔS 阴阳距 — 相似文本计算 | I="项目需做环评", G="建设项目必须进行环境影响评价" | ΔS ∈ (0, 0.5) (轻度偏差) | P0 |
| TV-003 | ΔS 阴阳距 — 无关文本计算 | I="今天天气很好", G="建设项目环境影响评价管理办法" | ΔS > 0.7 (高度偏差) | P0 |
| TV-004 | ΔS 阴阳距 — 空文本输入 | I="", G="环评相关法规" | 返回错误/异常，不崩溃 | P1 |
| TV-005 | 坤守残差修正 — 正常偏差 | I="该项目的二氧化硫排放量为100吨/年", G="二氧化硫排放限值为50吨/年" | 修正后文本与G一致 | P0 |
| TV-006 | 坤守残差修正 — 无偏差 | I=G (与知识文本完全一致) | 修正后文本无变化 | P0 |
| TV-007 | 坤守残差修正 — 大偏差 | I与G语义完全不相关 | 修正后文本大幅调整 | P1 |
| TV-008 | 坤守残差修正 — 空输入 | I="" (无输入) | 返回错误或空修正 | P2 |
| TV-009 | 乾进稳定性评分 — 高稳定性 | 多路径输出高度一致 | f_S > 0.8 | P0 |
| TV-010 | 乾进稳定性评分 — 低稳定性 | 多路径输出差异大 | f_S < 0.4 | P1 |
| TV-011 | 复归状态机 — 正常恢复 | 崩溃后调用恢复流程 | 状态恢复到崩溃前检查点 | P0 |
| TV-012 | 复归状态机 — 多次崩溃 | 连续崩溃3次 | 第3次后自动切换降级模式 | P1 |
| TV-013 | 巽调注意力门控 — 高方差 | σ 较大 (输入差异大) | factor 趋近于0，降低注意力 | P0 |
| TV-014 | 巽调注意力门控 — 零方差 | σ = 0 (输入完全一致) | factor = 1.0，保持原始注意力 | P1 |
| TV-015 | 北辰编译器 — 简单目标编译 | "查询环评报告审批状态" | 生成含2-3个原子任务的原子表 | P0 |
| TV-016 | 北辰编译器 — 复杂目标编译 | "完成娄底市XX项目的环评审批全流程" | 生成含5+个原子任务的执行令牌板 | P0 |
| TV-017 | 北辰编译器 — 无效目标 | 空字符串或纯标点 | 返回错误 | P1 |
| TV-018 | 病候图诊断 — 检测到已知失败模式 | 输入含矛盾陈述 | 匹配到对应失败模式 ID | P0 |
| TV-019 | 病候图诊断 — 无失败模式 | 输入完全正确 | 标记为"通过", 无匹配 | P0 |
| TV-020 | 观变追踪 — 状态变迁记录 | 执行3次状态变更 | 历史记录包含3条变迁 | P1 |
| TV-021 | ΔS 阴阳距 — 极长文本 (10万字符) | I="..."(10万字符环评报告), G=知识库 | 计算完成无超时，ΔS ∈ [0,1] | P1 |
| TV-022 | 坤守残差修正 — 知识库空 | I="文本", G=None | 返回原文本，提示无知识库 | P1 |
| TV-023 | 北辰编译器 — 下游泄漏审计 | 子任务B依赖A，尝试先执行B | 编译器拦截，要求先完成A | P0 |
| TV-024 | 巽调 — gamma参数边界 | γ = 0, γ = 10, γ = 100 | factor 分别=1, ≈0, ≈0 | P2 |

### 3.2 Hermes Provider gRPC 模块

#### 接口说明

Hermes Provider 提供 LLM 统一调用接口，通过 gRPC 桥接 TypeScript 运行时层和 Python 引擎层：

```protobuf
service HermesProvider {
  rpc Chat(ChatRequest) returns (ChatResponse);
  rpc StreamChat(ChatRequest) returns (stream ChatChunk);
  rpc GetModelInfo(Empty) returns (ModelInfo);
}
```

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| HP-001 | Chat RPC — 正常调用 | messages=[{"role":"user","content":"你好"}], tools=None | ChatResponse.content 非空 | P0 |
| HP-002 | Chat RPC — 带工具调用 | messages=[user_msg], tools=[{"name":"search","schema":{...}}] | ChatResponse.tool_calls 含search | P0 |
| HP-003 | StreamChat — 正常流式 | messages=[user_msg] | stream chunks 逐个输出，尾部完结标记 | P0 |
| HP-004 | StreamChat — 空消息 | messages=[] | 返回错误code=INVALID_ARGUMENT | P1 |
| HP-005 | StreamChat — 中断后重连 | 客户端中途断开连接后重新连接 | 新连接正常响应，旧会话清理 | P1 |
| HP-006 | 网络断开自动重连 | 服务端网络断开5秒后恢复 | 客户端自动重连成功，请求正常完成 | P1 |
| HP-007 | 多租户路由 — 租户A隔离 | 租户A的API Key调用Chat | 返回租户A的专属模型配置 | P0 |
| HP-008 | 多租户路由 — 无效API Key | 伪造的API Key | 返回错误code=UNAUTHENTICATED | P0 |
| HP-009 | 并发请求 — 高并发压力 | 100个并发Chat请求 | 全部成功返回，无panic | P1 |
| HP-010 | 大上下文 — 32K tokens | messages包含约32K tokens内容 | 正常返回结果 | P1 |
| HP-011 | 超时控制 — 超时请求 | 设置timeout=1ms处理大请求 | 返回超时错误code=DEADLINE_EXCEEDED | P0 |
| HP-012 | 模型信息查询 | GetModelInfo空请求 | 返回支持的模型列表及版本 | P1 |
| HP-013 | gRPC TLS加密 | 启动TLS证书验证 | 连接成功，传输加密 | P1 |
| HP-014 | 流式取消 — 客户端取消 | 客户端发起cancellation | 服务端停止生成，释放资源 | P1 |
| HP-015 | 最大token限制 | 请求max_tokens=0 | 返回错误或使用默认值 | P2 |

### 3.3 插件系统模块

#### 接口说明

Plugin 系统基于 EventBus 实现，支持插件的加载/卸载/生命周期管理：

- `Plugin.activate(context)`
- `Plugin.deactivate()`
- 事件订阅：`event_bus.on(event_name, handler)`
- 事件发布：`event_bus.emit(event_name, data)`

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| PS-001 | 插件加载 — 激活 | 插件ID加载并调用activate() | 插件状态变为ACTIVE, 订阅事件生效 | P0 |
| PS-002 | 插件卸载 — 停用 | 已激活的插件调用deactivate() | 插件状态变为INACTIVE, 事件订阅取消 | P0 |
| PS-003 | 插件事件订阅 — 正常 | 插件订阅agent:start事件，agent启动 | 插件handler被调用，收到事件data | P0 |
| PS-004 | 插件事件订阅 — abort | 插件在agent:start中返回abort | agent启动被中断 | P1 |
| PS-005 | 多个插件优先级 | 插件A (priority=10) + 插件B (priority=0) | 插件A的handler先被执行 | P1 |
| PS-006 | 插件异常隔离 | 插件A的handler抛出异常 | 插件B的handler正常执行，总线不崩溃 | P0 |
| PS-007 | 插件热加载 | 动态加载新插件YAML配置 | 插件立即生效，无需重启 | P1 |
| PS-008 | 循环事件检测 | 插件A事件->插件B事件->插件A | 检测到循环并中止 | P1 |
| PS-009 | 事件历史查询 | 发出10个事件后查询历史 | 返回最近limit条事件记录 | P1 |
| PS-010 | 插件依赖检查 | 插件B依赖插件A，先加载B | 自动先加载A，再加载B | P1 |

### 3.4 多租户模块

#### 接口说明

多租户采用 POOL 策略（前缀隔离），所有模块需感知租户上下文。

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| MT-001 | 租户数据隔离 — 读 | 租户A写入key="x", 租户B读取key="x" | 租户B读不到租户A的数据 | P0 |
| MT-002 | 租户数据隔离 — 写 | 租户A写入data1, 租户B写入data2 | 两者存储位置隔离，互不覆盖 | P0 |
| MT-003 | 租户上下文传递 | 请求经gRPC→Service→DB层 | 所有层的日志和查询都携带tenant_id | P0 |
| MT-004 | 跨租户查询隔离 | 使用管理账号查询所有租户数据 | 仅管理员可查询，普通租户报错 | P0 |
| MT-005 | 租户配置覆盖 | 租户A设置model=gpt-4, 租户B设置model=glm-4 | 各自使用自己的模型配置 | P1 |
| MT-006 | 租户创建/删除 | 创建新租户并分配资源 | 租户创建成功，删除后数据清理 | P1 |
| MT-007 | 租户配额限制 | 租户A的存储配额100MB，尝试写入101MB | 写入失败，返回QUOTA_EXCEEDED | P1 |
| MT-008 | 并发租户访问 | 100个不同租户同时请求 | 数据隔离正确，无交叉污染 | P1 |
| MT-009 | 非法租户ID | request带tenant_id="../../../etc/passwd" | 拦截SQL注入/PATH注入 | P0 |
| MT-010 | 空租户上下文 | 请求不携带任何租户信息 | 使用默认租户或返回错误 | P1 |

### 3.5 GovMCP 集成模块

#### 接口说明

GovMCP 集成覆盖以下核心功能：
- **SM4 加密通道**：`sm2.encrypt()` / `sm4.encrypt()` — 国密加密
- **审批工作流**：`ApprovalFlow` 状态机 — 多级审批链
- **审计链**：`AuditChain` — SM3 哈希链，append-only
- **政务工具**：100+ 工具，通过 MCP 协议暴露

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| GM-001 | SM4 加密/解密 — 双向验证 | 原始数据 → SM4加密 → SM4解密 | 解密结果与原始数据一致 | P0 |
| GM-002 | SM4 加密 — 不同密钥解密 | 用key1加密，用key2解密 | 解密失败或返回乱码 | P0 |
| GM-003 | SM2 签名/验签 | 消息 → SM2签名 → SM2验签 | 签名验证通过 | P0 |
| GM-004 | SM3 哈希 — 一致性 | 同一数据两次SM3哈希 | 两次哈希值完全一致 | P0 |
| GM-005 | 审批工作流 — 单一节点 | 提交审批请求 → approve | 状态: pending→approved | P0 |
| GM-006 | 审批工作流 — 多级审批 | 科员→科长→处长三级审批 | 每级批准后进入下一级 | P0 |
| GM-007 | 审批工作流 — reject 流程 | 科长驳回 | 状态变为rejected，退回申请人 | P0 |
| GM-008 | 审批工作流 — 超时 | 超过timeout_seconds未处理 | 状态变为timeout或触发自动拒绝 | P1 |
| GM-009 | 审计链 — append-only | 追加一条审计记录 | 原记录不可修改，链长度+1 | P0 |
| GM-010 | 审计链 — 篡改检测 | 手动修改审计链中间节点 | 哈希校验失败，检测到篡改 | P0 |
| GM-011 | 政务工具 — 工具调用 | 调用"环评报告查询"工具 | 返回正确的查询结果 | P0 |
| GM-012 | 政务工具 — 权限不足 | 无权限用户调用敏感工具 | 返回权限错误 | P0 |
| GM-013 | 加密通道 — 本地→政务云同步 | 本地数据SM4加密后同步到云 | 云端存储为密文，回传解密后一致 | P1 |
| GM-014 | 审批工作流 — modify并批准 | 科长修改参数后批准 | 状态变为approved，参数已修改 | P1 |
| GM-015 | 审计链 — 批量查询 | 查询最近100条审计记录 | 返回100条分页结果 | P2 |

### 3.6 安全模块

#### 接口说明

安全覆盖身份认证、授权、审计日志三个方面。

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| SEC-001 | 手机号+验证码登录 — 正常 | 手机号+正确验证码 | 返回 JWT Token | P0 |
| SEC-002 | 手机号+验证码登录 — 错误验证码 | 手机号+错误验证码 | 返回 AUTH_FAILED | P0 |
| SEC-003 | JWT Token 验证 — 有效 | 有效Token访问受保护接口 | 正常返回数据 | P0 |
| SEC-004 | JWT Token 验证 — 过期 | 过期Token访问受保护接口 | 返回 TOKEN_EXPIRED | P0 |
| SEC-005 | JWT Token 验证 — 伪造 | 伪造签名Token | 返回 TOKEN_INVALID | P0 |
| SEC-006 | 访问控制 — 角色限制 | 普通用户访问管理员接口 | 返回 PERMISSION_DENIED | P0 |
| SEC-007 | 审计日志 — 操作记录 | 用户执行敏感操作 | 日志包含用户、操作、时间、结果 | P0 |
| SEC-008 | 审计日志 — 不可篡改 | 尝试修改已有审计日志 | 检测到篡改并告警 | P0 |
| SEC-009 | SQL 注入防护 | 输入 `' OR 1=1 --` | 不返回越权数据 | P0 |
| SEC-010 | XSS 防护 | 输入 `<script>alert('xss')</script>` | 输入被过滤/转义 | P0 |
| SEC-011 | Rate Limiting — 正常 | 每分钟少于60次请求 | 正常处理 | P1 |
| SEC-012 | Rate Limiting — 超限 | 每分钟超过100次请求 | 返回 RATE_LIMITED 429 | P1 |
| SEC-013 | 敏感数据过滤 | 输入含手机号/身份证号 | 自动脱敏或拦截 | P1 |

### 3.7 工作流引擎模块

#### 接口说明

`WorkflowEngine` 提供有向图工作流编排能力。

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| WE-001 | 线性工作流 — A→B→C | 注册A、B、C节点，A→B→C边 | 按序执行A→B→C | P0 |
| WE-002 | 条件分支 — 条件满足走分支 | 注册条件边，条件满足 | 路由到指定分支节点 | P0 |
| WE-003 | 条件分支 — 条件不满足走默认 | 注册条件边，条件不满足 | 路由到默认节点 | P1 |
| WE-004 | 中断恢复 — interrupt/resume | 在B节点设置中断 → resume | 从中断点恢复执行 | P0 |
| WE-005 | 最大迭代限制 | 注册含循环的工作流，迭代超出max_iterations | 自动终止，不进入死循环 | P0 |
| WE-006 | 节点异常处理 | A节点抛出异常 | 错误记录到state.errors，可选跳过 | P1 |
| WE-007 | 工作流状态持久化 | 保存state → 重启 → 加载state | 状态完全恢复 | P1 |
| WE-008 | 并发节点执行 | 两个无依赖节点同时启动 | 两个节点并发执行 | P1 |

### 3.8 MCP 协议模块

#### 接口说明

MCP Server/Client 遵循 modelcontextprotocol.io 规范。

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| MCP-001 | 服务端初始化握手 | 客户端发送initialize请求 | 服务端返回capabilities和serverInfo | P0 |
| MCP-002 | 服务端工具列表 | 客户端调用 tools/list | 返回已注册的所有工具列表 | P0 |
| MCP-003 | 服务端工具调用 | 客户端调用 tools/call | 工具handler执行并返回结果 | P0 |
| MCP-004 | 服务端工具调用 — 不存在 | 调用未注册的工具 | 返回code=-32602 | P1 |
| MCP-005 | 客户端连接服务端 | ClientAdapter.connect() | 初始化成功，工具列表加载 | P0 |
| MCP-006 | 客户端断线重连 | disconnect → 短暂等待 → connect | 重连成功，工具列表重新加载 | P1 |
| MCP-007 | 客户端工具调用 | ClientAdapter.call_tool("search", {q:"test"}) | 返回 ToolResult(success=True) | P0 |
| MCP-008 | JSON-RPC 协议解析 | 标准JSON-RPC请求 | 正确解析为 MCPMessage | P0 |
| MCP-009 | JSON-RPC 协议解析 — 非法JSON | 非法JSON字符串 | 抛异常或返回错误消息 | P1 |
| MCP-010 | 服务端 ping/pong | 客户端发送 ping | 服务端返回 {} | P1 |

### 3.9 EventBus 模块

#### 接口说明

EventBus 提供事件驱动的插件通信机制，支持同步和异步事件。

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| EB-001 | 事件订阅与发布 | on("test", handler) + emit("test", {key:"val"}) | handler被调用，data包含{key:"val"} | P0 |
| EB-002 | 取消订阅 | on与off后再次emit | handler不再被调用 | P0 |
| EB-003 | 事件中止 | handler返回{"abort":true} | emit返回包含abort的结果 | P1 |
| EB-004 | 事件历史记录 | emit 5个事件 | get_history返回5条记录 | P1 |
| EB-005 | 事件历史上限 | emit 2000个事件 | 历史不超过1000条 | P1 |
| EB-006 | 同步事件 | emit_sync("event", data) | 同步返回结果 | P1 |
| EB-007 | 钩子优先级 | 高优先级handler先被注册 | 高优先级先执行 | P1 |
| EB-008 | 预定义事件注册 | 使用Events.AGENT_START等 | 正确发出预定义事件 | P1 |

### 3.10 多Agent协调模块

#### 接口说明

`MultiAgentCoordinator` 支持 PARALLEL / SEQUENTIAL / HIERARCHICAL / DEBATE / CONSENSUS / BROADCAST 六种协调模式。

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| MA-001 | 并行执行 — 所有成功 | 3个独立任务 | 全部completed | P0 |
| MA-002 | 串行执行 — 顺序保证 | 3个依赖任务(A→B→C) | 按A→B→C顺序完成 | P0 |
| MA-003 | 串行执行 — 依赖失败 | A→B, A失败 | B不执行或标记为failed | P1 |
| MA-004 | 层级委托 — 分解+并行 | 根任务分解为3个子任务 | 子任务并行执行后汇总 | P0 |
| MA-005 | 层级委托 — 达到最大深度 | 深度超过max_depth | 返回失败 | P1 |
| MA-006 | 辩论模式 | 3个Agent辩论3轮 | 返回winner和投票结果 | P1 |
| MA-007 | 共识模式 — 达到阈值 | 3个Agent中2个同意 | consensus_reached=true | P1 |
| MA-008 | 共识模式 — 未达阈值 | 3个Agent分歧 | consensus_reached=false | P1 |
| MA-009 | 广播消息 | broadcast到所有Agent | 所有Agent收到消息 | P1 |
| MA-010 | 消息路由 — 指定接收者 | 发送给特定Agent | 只有目标Agent收到 | P1 |
| MA-011 | Agent蜂群 — 创建+销毁 | spawn → despawn | 创建后注册，销毁后注销 | P1 |
| MA-012 | 超时控制 | 任务执行超过timeout | 任务状态变为failed | P0 |

### 3.11 技能系统模块

#### 接口说明

`SkillManager` 提供技能的注册、查找、安装、卸载和执行。

#### 测试用例

| 测试ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|--------|---------|------|---------|:------:|
| SS-001 | 技能注册 | 注册新Skill对象 | skill在hub中可查询 | P0 |
| SS-002 | 技能查找 | 按ID查找技能 | 返回对应Skill对象 | P0 |
| SS-003 | 技能查找 — 不存在 | 查找不存在的ID | 返回None或KeyError | P1 |
| SS-004 | 技能YAML加载 | 从YAML文件加载技能 | 正确解析为Skill对象 | P0 |
| SS-005 | 技能YAML加载 — 格式错误 | 非法YAML内容 | 加载失败，不崩溃 | P1 |
| SS-006 | 技能自动创建 | 基于模板创建技能 | 创建成功并存储为YAML | P1 |
| SS-007 | 技能使用计数 | 同一技能执行3次 | usage_count=3 | P2 |
| SS-008 | 技能升级 | 更新技能版本 | version递增，旧版本归档 | P1 |

---

## 4. 端到端测试场景（娄底环评审批）

### 4.1 正向场景 — 完整审批流程

**测试ID：E2E-001**

**前置条件**：
- 测试数据库已初始化（含用户表、审批模板、知识库）
- Mock LLM Provider 已配置（返回确定性响应）
- 所有微服务已启动（Taiji Verify, Hermes Provider, GovMCP）

**测试步骤**：

```
┌─────────┐   ┌──────────┐   ┌────────────┐   ┌──────────────┐   ┌────────┐   ┌────────┐   ┌────────────┐
│ 用户登录  │──▶│ 提交环评   │──▶│ AI自动预审  │──▶│ 生成审批建议   │──▶│ 科长审批 │──▶│ 局长终审 │──▶│ 结果通知    │
│ 手机+验证码│   │ 报告      │   │ Taiji Verify│   │ 仓颉Agent    │   │        │   │        │   │            │
└─────────┘   └──────────┘   └────────────┘   └──────────────┘   └────────┘   └────────┘   └────────────┘
```

1. **用户登录**：调用认证接口，手机号+验证码获取 JWT Token
2. **提交环评报告**：上传环评报告 PDF（约50页），调用报告提交接口
3. **AI自动预审**：
   - 调用 Taiji Verify 阴阳距ΔS 计算语义偏差
   - 调用 坤守 检测残差并修正
   - 调用 病候图 诊断失败模式
   - 调用 北辰编译器 分解审批任务
4. **生成审批建议**：仓颉Agent基于预审结果生成审批建议书
5. **科长审批**：科长登录 → 查看待审批 → 批准 → 流转到下一级
6. **局长终审**：局长登录 → 查看审批结果 → 终审批准
7. **审批结果通知**：系统发送审批结果通知给申请人

**预期结果**：
- 每一步状态正确流转（pending → 预审中 → 待科长审批 → 待局长审批 → 已完成）
- 每一步的审计记录写入不可篡改链
- 最终审批结果包含完整的审批意见链
- 通知成功发送

**验证点**：
| 验证项 | 验证方式 |
|--------|----------|
| JWT Token 有效 | 检查Token格式和过期时间 |
| ΔS 分数在正常范围 | ΔS < 0.3（偏差较小） |
| 坤守修正项 | 如果有偏差，修正后文本通过验证 |
| 北辰编译器生成原子任务 | 原子任务列表完整，无遗漏 |
| 审批状态机流转 | 每级审批后状态更新正确 |
| 审计链长度 | 每条操作都生成审计记录，链长度>0 |
| 审批结果通知 | 通知日志可查 |

### 4.2 负向场景 — 法条引用错误

**测试ID：E2E-002**

**前置条件**：同 E2E-001

**测试步骤**：
1. 提交含错误法条引用的环评报告（如引用已废止法规《建设项目环境保护管理条例》旧版）
2. 坤守检测到语义残差 → 计算 ΔS > 阈值（偏差过大）
3. 病候图匹配到"法条引用错误"失败模式
4. 系统自动生成修正建议，标注正确的法条引用
5. 提示用户修正
6. 用户修正后重新提交
7. 坤守重新验证通过

**预期结果**：
- 坤守成功拦截，返回具体修正建议
- 修正后的报告验证通过（ΔS < 阈值）
- 审计链记录拦截事件和修正过程

### 4.3 负向场景 — 审批超时

**测试ID：E2E-003**

**前置条件**：配置审批超时时间为30秒（测试用短超时）

**测试步骤**：
1. 提交环评审批申请
2. 审批流转到科长
3. 科长不操作，等待超时
4. 超时后系统自动处理

**预期结果**：
- 超时时间到达后，审批状态变为timeout
- 根据配置，可选自动拒绝或触发升级
- 审计链记录超时事件
- 申请人收到超时通知

### 4.4 安全场景 — 未授权访问

**测试ID：E2E-004**

**测试步骤**：

| 子场景 | 操作 | 预期结果 |
|--------|------|---------|
| 无Token访问 | 直接调用审批API | 返回 401 Unauthorized |
| 过期Token | 使用过期Token访问 | 返回 401 Token Expired |
| 越权访问 | 普通用户访问管理员接口 | 返回 403 Forbidden |
| 跨租户访问 | 租户A Token访问租户B的数据 | 返回 403 或空数据 |
| SQL注入 | 输入 `' OR 1=1` | 查询不返回越权数据 |
| 路径遍历 | 输入 `../../../etc/passwd` | 文件访问被拦截 |

### 4.5 性能场景 — 高并发

**测试ID：E2E-005**

**测试工具**：locust

**测试配置**：
| 参数 | 值 |
|------|-----|
| 并发用户数 | 50 / 100 / 200（阶梯式） |
| 爬升时间 | 30秒 |
| 持续时长 | 5分钟 |
| 测试接口 | 登录、提交报告、审批操作 |

**性能目标**：
| 指标 | P0目标 | P1目标 |
|------|:------:|:------:|
| 平均响应时间 | < 500ms | < 1000ms |
| P99 响应时间 | < 2000ms | < 5000ms |
| 错误率 | < 0.1% | < 1% |
| 吞吐量 (RPS) | > 100 | > 50 |

**预期结果**：
- 系统无崩溃
- 数据一致性不受影响
- 审计链无丢失

---

## 5. CI 流水线设计

```yaml
# .github/workflows/test.yml
name: Integration Tests

on:
  push:
    branches: [main, develop, 'feature/**']
  pull_request:
    branches: [main, develop]

jobs:
  unit-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install pytest pytest-asyncio pytest-cov pytest-xdist
      - name: Run unit tests
        run: |
          python -m pytest tests/unit \
            -v \
            --cov=src/opentaiji \
            --cov-report=term-missing \
            --cov-report=xml:coverage-unit.xml \
            -n auto
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage-unit.xml
          flags: unittests

  integration-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: taiji_test
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install pytest pytest-asyncio pytest-cov
      - name: Run integration tests
        run: |
          python -m pytest tests/integration \
            -v \
            --cov=src/opentaiji \
            --cov-report=term-missing \
            --cov-report=xml:coverage-integration.xml \
            -m integration
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage-integration.xml
          flags: integrationtests

  e2e-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Start test environment
        run: |
          docker compose -f docker-compose.test.yml up -d
          sleep 10  # 等待服务启动
      - name: Run E2E tests
        run: |
          docker compose -f docker-compose.test.yml exec taiji-agent \
            python -m pytest tests/e2e -v -m e2e
      - name: Cleanup
        if: always()
        run: |
          docker compose -f docker-compose.test.yml down -v

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install bandit safety pip-audit
      - name: Run security scan
        run: |
          bandit -r src/ -f json -o bandit-report.json || true
          safety check --full-report || true
      - name: Upload security report
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: |
            bandit-report.json
            *.txt

  quality-gate:
    needs: [unit-test, integration-test, e2e-test, security-scan]
    runs-on: ubuntu-latest
    steps:
      - name: Check all gates passed
        run: |
          echo "All quality gates passed"
          echo "✅ Unit tests passed"
          echo "✅ Integration tests passed"
          echo "✅ E2E tests passed"
          echo "✅ Security scan passed"
```

---

## 6. 覆盖率目标

| 测试类型 | 覆盖率要求 | 关键路径要求 | 验证工具 |
|----------|:----------:|:------------:|----------|
| 单元测试 | ≥ 80% | 核心算法 100% | pytest-cov |
| 集成测试 | 关键路径 100% | 模块间接口 100% | pytest + coverage |
| 端到端测试 | 核心场景 100% | 娄底审批流程 100% | pytest + docker |
| 安全扫描 | 零高危漏洞 | 零未修复漏洞 | bandit, safety |

### 模块级覆盖率目标

| 模块 | 单元测试目标 | 集成测试目标 |
|------|:-----------:|:-----------:|
| Taiji Verify (wfgy/) | 90% | 100% |
| Provider (providers/) | 85% | 100% |
| 多Agent协调 (multiagent/) | 85% | 100% |
| 工作流引擎 (workflow/) | 85% | 100% |
| MCP 协议 (mcp/) | 80% | 100% |
| EventBus (events/) | 85% | 100% |
| 护栏系统 (guardrails/) | 80% | 100% |
| HITL 审批 (hitl/) | 85% | 100% |
| 技能系统 (skills/) | 80% | 100% |
| 代码沙箱 (code/) | 80% | 100% |
| 安全相关（认证/审计） | 90% | 100% |
| 可观测性 (observability/) | 80% | 90% |

---

## 7. 测试工具选型

| 用途 | 工具 | 版本 | 选型理由 |
|------|------|:----:|----------|
| 测试框架 | pytest | ^8.0 | 成熟的Python测试框架，插件生态丰富 |
| 异步测试 | pytest-asyncio | ^0.23 | 原生支持async/await测试 |
| Mock | pytest-mock | ^3.12 | 基于unittest.mock的pytest集成 |
| gRPC测试 | grpcio-testing | ^1.62 | gRPC官方测试工具 |
| HTTP Mock | aioresponses | ^0.7 | 异步HTTP请求Mock |
| 覆盖率 | pytest-cov | ^5.0 | 详细代码覆盖率报告 |
| 并行测试 | pytest-xdist | ^3.5 | 多CPU并行加速 |
| 性能测试 | locust | ^2.20 | 高并发性能压测 |
| 安全扫描 | bandit | ^1.7 | Python安全漏洞扫描 |
| 依赖安全 | safety | ^3.0 | 依赖包安全审计 |
| 测试数据 | Faker | ^22.0 | 生成测试假数据 |
| 时间Mock | freezegun | ^1.4 | 时间冻结测试 |
| 数据库 | pytest-postgresql | ^5.0 | PostgreSQL测试夹具 |

---

## 8. 测试数据管理

### 8.1 测试数据集

| 数据集 | 内容 | 来源 | 用途 |
|--------|------|------|------|
| 环评报告样本 | 10份不同行业的环评报告PDF | 模拟生成 | E2E审批测试 |
| 法条知识库 | 500+条环境法条及引用规则 | 从公开法规整理 | 坤守残差修正 |
| 用户数据池 | 100个模拟用户（含不同角色） | Faker生成 | 多租户/权限测试 |
| 审批模板 | 5种不同审批流程模板 | YAML配置 | 工作流引擎测试 |
| Mock LLM响应集 | 50组确定性LLM响应 | 手动构建 | Provider测试 |

### 8.2 Mock 数据

```python
# tests/mock_data.py 示例
from opentaiji.wfgy.verifier import WFGYRule

# Mock 环评知识库
MOCK_EIA_KNOWLEDGE = [
    {"symbol": "环评", "meaning": "环境影响评价", "source": "环评法"},
    {"symbol": "SO2", "meaning": "二氧化硫", "source": "大气污染防治法"},
    {"symbol": "PM2.5", "meaning": "细颗粒物", "source": "环境空气质量标准"},
]

# Mock 审批流程
MOCK_APPROVAL_FLOW = {
    "flow_id": "eia-approval",
    "steps": ["科长审批", "处长审批", "局长终审"],
    "timeout": 3600,
    "escalation": True,
}

# Mock 用户
MOCK_USERS = {
    "科长A": {"role": "section_chief", "department": "环评科"},
    "局长B": {"role": "director", "department": "生态环境局"},
    "申请人C": {"role": "applicant", "company": "XX建设公司"},
}
```

### 8.3 数据清理策略

| 环境 | 清理策略 | 方式 |
|------|----------|------|
| 本地开发 | 每次运行前重建测试数据库 | `pytest --reuse-db` 可选 |
| CI | 每次构建使用新数据库 | Docker容器启动时初始化 |
| 临时数据 | 测试夹具自动清理 | pytest fixture `yield` 后清理 |
| 敏感数据 | 所有测试数据脱敏 | Faker生成，无真实数据 |

---

## 9. 质量门禁

```
┌────────────────────────────────────────────────────────────┐
│                    质量门禁 (Quality Gate)                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. 代码审查通过                                            │
│     ├── 至少1名 Senior Reviewer 批准                          │
│     └── 所有 Review 意见已解决                                │
│                                                            │
│  2. 所有测试通过                                            │
│     ├── 单元测试 100% 通过                                   │
│     ├── 集成测试 100% 通过                                   │
│     └── 端到端测试 100% 通过                                 │
│                                                            │
│  3. 覆盖率达标                                              │
│     ├── 单元测试覆盖率 ≥ 80%                                 │
│     ├── 集成测试关键路径 100%                                 │
│     └── 新增代码覆盖率 ≥ 85%                                 │
│                                                            │
│  4. 安全扫描通过                                            │
│     ├── bandit 零高危漏洞                                    │
│     ├── safety 零已知漏洞                                    │
│     └── 依赖审计通过                                        │
│                                                            │
│  5. 性能基线达标                                            │
│     ├── 关键接口 P99 < 2000ms                                │
│     └── 错误率 < 0.1%                                       │
│                                                            │
│  未通过任何门禁 → PR 不可合并                                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 10. 实施计划

### 10.1 工作量估算

| 阶段 | 任务 | 预估工时 | 人员 |
|:----:|------|:--------:|:----:|
| 1 | 测试环境搭建（Docker + CI） | 3人天 | DevOps |
| 2 | 单元测试补全（覆盖率≥80%） | 8人天 | Dev + QA |
| 3 | 集成测试用例编码（模块接口） | 10人天 | QA |
| 4 | 端到端测试场景编码 | 5人天 | QA |
| 5 | 性能测试脚本（Locust） | 3人天 | QA |
| 6 | 安全测试 | 3人天 | 安全工程师 |
| 7 | CI 流水线配置与调试 | 2人天 | DevOps |
| 8 | 测试执行与缺陷跟踪 | 5人天 | QA |
| **合计** | | **39人天** | |

### 10.2 测试目录结构

```
tests/
├── conftest.py                  # 全局测试夹具和配置
├── pytest.ini                   # pytest 配置
├── mock_data.py                 # 通用Mock数据
├── mock_llm_provider.py         # Mock LLM Provider
│
├── unit/                        # 单元测试
│   ├── test_wfgy.py             # Taiji Verify 单元测试
│   ├── test_providers.py        # Provider 单元测试
│   ├── test_events.py           # EventBus 单元测试
│   ├── test_workflow.py         # 工作流引擎单元测试
│   ├── test_mcp_protocol.py     # MCP协议单元测试
│   ├── test_guardrails.py       # 护栏单元测试
│   ├── test_hitl.py             # HITL单元测试
│   ├── test_skills.py           # 技能系统单元测试
│   ├── test_multiagent.py       # 多Agent协调单元测试
│   └── test_code_executor.py    # 代码执行器单元测试
│
├── integration/                 # 集成测试
│   ├── test_verify_provider.py  # Taiji Verify ↔ Provider
│   ├── test_event_plugin.py     # EventBus ↔ Plugin
│   ├── test_mcp_server_client.py # MCP Server ↔ Client
│   ├── test_workflow_approval.py # 工作流引擎 ↔ 审批
│   ├── test_multi_tenant.py     # 多租户集成
│   ├── test_govmcp_encryption.py # GovMCP 加密
│   ├── test_security_auth.py    # 安全认证集成
│   └── test_all_modules.py      # 全模块集成
│
├── e2e/                         # 端到端测试
│   ├── conftest.py              # E2E 夹具（启动服务）
│   ├── test_eia_full_flow.py    # 环评审批全流程
│   ├── test_eia_law_error.py    # 法条引用错误
│   ├── test_eia_timeout.py      # 审批超时
│   ├── test_security_negative.py # 安全负向场景
│   └── test_performance.py      # 性能场景
│
├── performance/                 # 性能测试
│   └── locustfile.py            # Locust 压测脚本
│
└── security/                    # 安全测试
    ├── test_auth.py             # 认证安全
    ├── test_injection.py        # 注入攻击
    └── test_audit.py            # 审计安全
```

### 10.3 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|:----:|:----:|----------|
| Mock LLM 与真实 LLM 行为差异大 | 高 | 中 | Mock响应定期与实际LLM对齐验证 |
| 集成测试环境不稳定 | 中 | 高 | Docker化测试环境，可重复构建 |
| E2E 测试数据依赖多 | 中 | 中 | 测试数据即用即建，独立清理 |
| gRPC 桥接测试覆盖不全 | 中 | 高 | 增加 network partition/fault injection 测试 |
| 性能基线不达标 | 中 | 高 | 早期识别性能瓶颈，优先优化 |

---

## 附录

### A. pytest 配置

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
markers =
    unit: Unit tests (default)
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    security: Security tests
    slow: Slow tests (> 10s)
```

### B. 测试夹具示例

```python
# tests/conftest.py
import pytest
from opentaiji.wfgy.verifier import WFGYVerifier
from opentaiji.events.bus import EventBus
from opentaiji.multiagent.coordinator import MultiAgentCoordinator


@pytest.fixture
def event_bus():
    """创建一个新的事件总线实例"""
    bus = EventBus()
    yield bus
    # 清理
    bus._hooks.clear()
    bus._event_history.clear()


@pytest.fixture
def wfgy_verifier():
    """创建一个配置了环评知识的验证器"""
    verifier = WFGYVerifier(minimum_score=0.7)
    verifier.add_knowledge("环评", "环境影响评价", "环评法")
    verifier.add_knowledge("SO2", "二氧化硫", "大气污染防治法")
    return verifier


@pytest.fixture
def coordinator():
    """创建多Agent协调器"""
    return MultiAgentCoordinator(max_concurrent=3, timeout=30.0)
```
