# OpenTaiji 2.1

**融合 Claude Code 交互体验 + Hermes Agent + Harness + WFGY 防幻觉**
太极哲学驱动的全栈 AI Agent 框架

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/xiejianjun000/open-taiji?style=social)](https://github.com/xiejianjun000/open-taiji/stargazers)

> 太极生两仪，两仪生四象，四象生八卦。
> 确定性（阳）与创造力（阴）的工程化平衡。

---

## 目录

- [设计哲学](#-设计哲学)
- [核心能力](#-核心能力)
- [v2.1 升级亮点](#-v21-升级亮点)
- [快速开始](#-快速开始)
- [项目架构](#-项目架构)
- [API 文档](#-api-文档)
- [测试报告](#-测试报告)
- [路线图](#-路线图)
- [贡献指南](#-贡献指南)
- [FAQ](#-faq)

---

## 🧘 设计哲学

OpenTaiji 遵循三条核心设计原则：

| 原则 | 解释 | 工程体现 |
|------|------|----------|
| **分布式** | 无中心节点，每个 Agent 是独立主体 | Agent Loop + 事件驱动，消息传递通信 |
| **可进化** | 系统不是"写完"的，是"长出来"的 | 自我学习闭环，人格持续迭代，记忆动态增长 |
| **自组织** | 无中央调度，智能体自主决策 | Skills Hub 自创建，任务自规划，上下文自组装 |

### 阴阳平衡

```
阳（确定性）                     阴（创造力）
─────────────────────────────────────────────
WFGY 防幻觉五重验证              LLM 多模型引擎
符号层规则匹配                    Anthropic / OpenAI / 国产模型
多路径自一致性检查                温度控制 / 流式输出
知识溯源索引                      Soul 人格定制化
幻觉风险评分系统                  自我学习闭环
Sandbox 安全沙箱                  Skills Hub 技能市场
```

---

## 🎯 核心能力

### 1. 太极 Agent Loop

基于 Harness 的通用 LLM Agent 运行时，~350 行核心代码：

```python
from taiji_agent import TaijiAgent, AgentConfig

agent = TaijiAgent(config=AgentConfig(
    provider="anthropic",
    model="claude-sonnet-4-20250514",
))
result = await agent.run("分析这段代码的性能瓶颈")
```

### 2. WFGY 防幻觉系统

五重验证管线，是 Taiji Agent 最核心的差异化能力：

| 验证层 | 组件 | 功能 |
|--------|------|------|
| 符号层验证 | `WFGYVerifier` | 基于知识库的事实匹配 |
| 自一致性检查 | `SelfConsistencyChecker` | 多路径采样投票 |
| 知识溯源 | `SourceTracer` | 结论追溯到知识来源 |
| 幻觉检测 | `HallucinationDetector` | 综合评分: WFGY(40%) + 一致性(30%) + 溯源(30%) |
| 风险标注 | 集成 Agent Loop | 高风险输出自动标注 [⚠️] |

### 3. 太极验证引擎 (Taiji Verify)

5 个独立模块，16 种故障模式检测：

| 模块 | 定位 | 功能 |
|------|------|------|
| **Kun Guard** (坤) | 基座稳定 | 知识锚点投影，残差监测 |
| **Qian Advance** (乾) | 创新探索 | 扰动路径生成，稳定区映射 |
| **Fu Return** (复) | 回归校正 | 异常检测，检查点恢复 |
| **Xun Tune** (巽) | 自适应调谐 | 方差调控，因子钳制 |
| **DeltaS** | 阴阳距 | 向量差异计算，门控区映射 |

### 4. Soul 人格引擎

YAML 声明式人格定义，安全、可解释、易定制：

```yaml
# souls/default.yaml
id: default
name: "太极助手"
layers:
  boundaries:
    - "不产生有害、违法或不道德内容"
    - "永远坦诚承认不确定性"
    - "不捏造事实或引用不存在的来源"
  ethics:
    - "追求阴阳平衡，避免极端"
    - "以用户为中心，尊重隐私"
  character:
    traits:
      - "深思熟虑，言行审慎"
      - "善于分析，化繁为简"
    taiji_aspect:
      阳: "分析、推理、逻辑"
      阴: "直觉、创造、共情"
```

支持 CLI 热切换：`/soul default`

### 5. 记忆系统

双层记忆架构：

| 层级 | 组件 | 持久化 | 功能 |
|------|------|--------|------|
| 短期记忆 | `SessionMemory` | JSON 文件 | 键值存储，Todo 管理，会话保存 |
| 长期记忆 | `HonchoMemory` | JSON 文件 | 用户画像，上下文索引，偏好提取 |
| 会话存储 | `SessionStore` | SQLite | 全量对话历史，会话切换，导出 |

### 6. 自我学习闭环

从每次交互中学习，持续进化：

```python
from taiji_agent import SelfImprovingLoop, HonchoMemory, SkillManager, WFGYVerifier

loop = SelfImprovingLoop(
    honcho=HonchoMemory(),
    skill_manager=SkillManager(),
    wfgy_verifier=WFGYVerifier(),
)

# 自动提取偏好、主题、情感，生成技能
learnings = await loop.learn_from_interaction(
    conversation=conversation,
    task="分析代码性能",
    result="使用列表推导式优化",
    tools_used=["file_read", "shell"],
)
```

### 7. Skills Hub 技能市场

| 预置技能 | 类别 | 说明 |
|---------|------|------|
| `github-auth` | 开发 | GitHub 认证配置 |
| `github-pr-workflow` | 开发 | PR 工作流自动化 |
| `code-review` | 开发 | 自动化代码审查 |
| `web-research` | 研究 | 深度网络搜索与信息提取 |
| `document-writer` | 创作 | 专业文档写作辅助 |
| `chinese-context` | 本地化 | 中文语境适配 |
| `planning-with-files` | 规划 | 跨会话任务规划与进度追踪 |

支持 CLI 命令：`/tools` 查看全部 15+ 工具

### 8. 工具系统

15+ 内置工具，覆盖开发全流程：

| 类别 | 工具 |
|------|------|
| 文件操作 | `file_read`, `file_write`, `file_list`, `file_search` |
| Shell | `shell` (含安全围栏检查) |
| Git | `git_status`, `git_log` |
| 网络 | `web_search`, `web_extract` |
| 代码执行 | `execute_code` (含安全沙箱) |
| 记忆 | `memory_search`, `memory_save` |
| 任务管理 | `todo_list`, `todo_add`, `todo_done` |

### 9. 多 Provider 支持

| Provider | 模型系列 | 状态 |
|----------|---------|------|
| Anthropic | Claude 系列 | ✅ |
| OpenAI | GPT 系列 | ✅ |
| 通义千问 (Qwen) | Qwen 系列 | ✅ |
| 智谱 (GLM) | GLM 系列 | ✅ |
| Kimi | Kimi 系列 | ✅ |
| 豆包 (Doubao) | 豆包系列 | ✅ |

支持故障转移：主 Provider 不可用时自动切换到备用。

### 10. 安全系统

| 组件 | 功能 |
|------|------|
| `SecurityFence` | 敏感关键词扫描 + 危险命令过滤 |
| `Sandbox` | 代码执行沙箱 (CPU/内存/磁盘限制) |
| `SandboxPool` | 并行沙箱池 (可配置大小) |
| `KeyManager` | API Key 轮换与审计 |
| `AuditChain` | 操作审计链 (哈希完整性) |
| `SensitiveDataDetector` | 敏感信息检测 (手机/身份证/邮箱) |
| `DesensitizationEngine` | 自动脱敏引擎 |
| `IncidentResponse` | 安全事件响应 |

---

## 🆕 v2.1 升级亮点

对比 v2.0，v2.1 带来以下重大升级：

### 交互体验升级 (Claude Code 对齐)

```
┌────────────────────────────────────────────────────────────┐
│                首次对话体验对比                              │
├──────────────┬─────────────────┬───────────────────────────┤
│     能力      │   Claude Code    │    Taiji Agent 2.1       │
├──────────────┼─────────────────┼───────────────────────────┤
│ 交互式对话    │ ✅               │ ✅                        │
│ 流式输出      │ ✅               │ ✅                        │
│ /help 命令   │ ✅               │ ✅                        │
│ /clear 命令  │ ✅               │ ✅                        │
│ /compact 命令│ ✅               │ ✅ (v2.1 新增)            │
│ /exit 退出   │ ✅               │ ✅ (/exit /quit /q)       │
│ Tab 命令补全 │ ✅               │ ✅                        │
│ 项目上下文检测│ ✅               │ ✅ (v2.1 新增)            │
│ 会话持久化    │ ❌               │ ✅ SQLite (v2.1 新增)    │
│ 多会话管理    │ ❌               │ ✅ /new /switch (v2.1)   │
│ 会话导出      │ ❌               │ ✅ /export Markdown       │
│ 模型热切换    │ ❌               │ ✅ /model (v2.1 新增)    │
│ 人格热切换    │ ❌               │ ✅ /soul                  │
│ WFGY 防幻觉  │ ❌               │ ✅ /wfgy 开关             │
│ 历史回放      │ ❌               │ ✅ /history (v2.1 新增)  │
└──────────────┴─────────────────┴───────────────────────────┘
```

### 工程能力升级

| v2.0 | v2.1 |
|------|------|
| 无会话持久化 | SQLite 全量对话存储 |
| 单次运行 | 交互式多轮对话 |
| 无上下文压缩 | `/compact` 上下文压缩 |
| 无故障转移 | `ProviderRouter` 自动切换 |
| 基础沙箱 | 完整 `SandboxPool` 并行池 |
| 30 个测试 | 387 个测试 (100% 通过) |

### 核心修复

| 修复项 | 影响 |
|--------|------|
| `store_context` 同秒键冲突 | 微秒精度防覆盖 |
| `_generate_skill_id` 中文空ID | 回退到 "custom" |
| `_shell` 安全围栏调用 | SecurityFence + subprocess |
| `_execute_code` SandboxResult | status 属性适配 |
| `readline` PermissionError | 优雅降级 |
| `/q` Tab 补全缺失 | 加入命令列表 |

---

## 📥 快速开始

### 环境要求

- Python >= 3.11
- pip >= 24.0

### 安装

```bash
# 克隆项目
git clone https://github.com/xiejianjun000/open-taiji.git
cd open-taiji

# 创建虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate

# 安装
pip install -e ".[all]"

# 初始化工作环境
taiji_agent init
```

### 首次对话

```bash
# 进入交互式对话模式
taiji_agent

# 或者单次执行
taiji_agent "帮我分析这段代码的性能"
```

启动后将看到：

```
╭────────────────── 🧘 OpenTaiji 2.1 ──────────────────╮
│ 太极 Agent 交互模式                                    │
│                                                       │
│ 模型: claude-sonnet-4-20250514                        │
│ 提供者: anthropic                                      │
│ Soul: default                                         │
│ WFGY防幻觉: ✅ 启用                                    │
│ 流式输出: ✅ 启用                                      │
│ 可用工具: 15 个                                        │
│ 项目: taiji-agent (Python)                            │
│                                                       │
│ 输入 /help 查看全部命令 | 直接输入问题开始对话           │
╰───────────────────────────────────────────────────────╯

[你] → 你好
[太极] → 你好！我是太极 Agent...
```

### Python API

```python
from taiji_agent import TaijiAgent, AgentConfig
import asyncio

async def main():
    config = AgentConfig(
        provider="anthropic",
        model="claude-sonnet-4-20250514",
        wfgy_enabled=True,
    )
    agent = TaijiAgent(config=config)
    result = await agent.run("帮我分析代码性能")
    print(result.content)

asyncio.run(main())
```

### 交互命令一览

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助信息 |
| `/new [名称]` | 创建新会话 |
| `/sessions` | 列出所有保存的会话 |
| `/switch <ID>` | 切换到指定会话 |
| `/delete <ID>` | 删除指定会话 |
| `/history` | 查看对话历史 |
| `/clear` | 清除当前上下文 |
| `/compact` | 压缩上下文（保留系统提示+最近6轮+摘要） |
| `/model <name>` | 切换模型 |
| `/soul <name>` | 切换人格 |
| `/tools` | 列出所有可用工具 |
| `/wfgy [on\|off]` | 开关 WFGY 防幻觉 |
| `/export` | 导出当前会话为 Markdown |
| `/exit` `/quit` `/q` | 退出程序 |

### 环境变量

```bash
# LLM API Keys
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# 国产模型
export DASHSCOOTER_API_KEY="..."      # 通义千问
export ZHIPU_API_KEY="..."            # 智谱 GLM
export MOONSHOT_API_KEY="..."         # Kimi
export DOUBAO_API_KEY="..."           # 豆包

# Agent 配置
export OPENAIJI_PROVIDER="anthropic"
export OPENAIJI_MODEL="claude-sonnet-4-20250514"
export OPENAIJI_WFGY="true"
```

---

## 🧩 项目架构

```
open-taiji/
├── src/taiji_agent/           # 100 个源文件, 28,009 行
│   ├── agent/               # Agent Loop 核心引擎
│   │   └── engine.py        #   TaijiAgent, AgentConfig, TaskResult
│   ├── wfgy/                # WFGY 防幻觉系统
│   │   └── verifier.py      #   WFGYVerifier, HallucinationDetector
│   ├── taiji_verify/        # 太极验证引擎 (5 模块)
│   │   ├── engine.py        #   TaijiVerifyEngine
│   │   ├── kun_guard.py     #   坤 - 基座稳定
│   │   ├── qian_advance.py  #   乾 - 创新探索
│   │   ├── fu_return.py     #   复 - 回归校正
│   │   ├── xun_tune.py      #   巽 - 自适应调谐
│   │   └── delta_s.py       #   阴阳距计算
│   ├── learning/            # 自我学习闭环
│   │   └── loop.py          #   HonchoMemory, SelfImprovingLoop
│   ├── skills/              # 技能系统
│   │   └── hub.py           #   SkillManager, SkillMarket, SkillCreator
│   ├── memory/              # 记忆系统
│   │   └── session.py       #   SessionMemory
│   ├── souls/               # Soul 人格系统
│   │   └── loader.py        #   SoulLoader
│   ├── tools/               # 工具注册表 (15+ 工具)
│   │   └── registry.py      #   ToolRegistry
│   ├── providers/           # LLM Provider
│   │   ├── anthropic.py     #   Claude
│   │   ├── openai.py        #   GPT
│   │   └── failover.py      #   ProviderRouter 故障转移
│   ├── security/            # 安全系统
│   │   ├── sandbox.py       #   SecurityFence, Sandbox, SandboxPool
│   │   ├── key_manager.py   #   KeyManager
│   │   ├── audit.py         #   AuditChain
│   │   ├── desensitize.py   #   DesensitizationEngine
│   │   └── incident.py      #   IncidentResponse
│   ├── events/              # 事件总线
│   │   └── bus.py           #   EventBus (on/emit_sync/abort)
│   ├── plugin/              # 插件系统
│   │   ├── plugin_base.py   #   ConfigurablePlugin, PluginHealth
│   │   └── hooks.py         #   HookManager, SystemEvents
│   ├── cli/                 # 交互式 CLI
│   │   └── main.py          #   InteractiveAgent, SessionStore
│   ├── mcp/                 # MCP 协议集成
│   ├── guardrails/          # 安全护栏
│   ├── observability/       # 全链路追踪
│   ├── hitl/                # 人机协作
│   ├── workflow/            # 状态工作流
│   ├── handoffs/            # Agent 交接
│   ├── code/                # 代码代理
│   └── visual/              # 工作流可视化
├── tests/                   # 12 个测试文件, 7,528 行
│   ├── stress_test.py       # v1 冒烟+压力测试 (30 tests)
│   ├── stress_test_v2.py    # v2 工程压力测试 (20 tests)
│   ├── test_all_systems.py  # 全功能测试 (72 tests)
│   ├── test_out_of_box_e2e.py  # 开箱E2E测试 (51 tests)
│   ├── test_onboarding_parity.py # 首次体验对比 (40 tests)
│   ├── test_security.py     # 安全测试 (47 tests)
│   ├── test_plugin.py       # 插件测试 (60 tests)
│   ├── test_taiji_verify.py # 太极验证测试 (38 tests)
│   ├── test_v2_features.py  # v2 特性测试 (25 tests)
│   ├── test_multi_tenant.py # 多租户测试 (4 tests)
│   └── test_grpc_bridge.py  # gRPC 桥接测试 (可选)
└── pyproject.toml           # 项目配置 (v2.1.0)
```

---

## 📖 API 文档

### 核心导出

```python
# Agent 引擎
from taiji_agent import TaijiAgent, AgentConfig, TaskResult, TaskStatus

# WFGY 防幻觉
from taiji_agent import WFGYVerifier, HallucinationDetector, SelfConsistencyChecker

# 太极验证
from taiji_agent.taiji_verify import TaijiVerifyEngine

# Soul 人格
from taiji_agent import SoulLoader, Soul, inject_soul

# 记忆系统
from taiji_agent import SessionMemory
from taiji_agent import HonchoMemory, PeerCard, LearnedContext, SelfImprovingLoop

# 技能系统
from taiji_agent import SkillManager, SkillMarket, SkillCreator, Skill

# 工具系统
from taiji_agent import ToolRegistry, Tool, ToolResult, ToolSchema

# Provider
from taiji_agent import (
    AnthropicProvider, OpenAIProvider,
    QwenProvider, GLMProvider, KimiProvider, DoubaoProvider,
)
from taiji_agent.providers.failover import ProviderRouter, ProviderEndpoint, FailoverConfig

# 安全系统
from taiji_agent.security.sandbox import (
    Sandbox, SandboxConfig, SandboxPool, SecurityFence,
    SandboxStatus, SandboxResult,
)

# CLI
from taiji_agent.cli.main import InteractiveAgent, SessionStore

# 事件总线
from taiji_agent.events.bus import EventBus

# 插件系统
from taiji_agent.plugin import ConfigurablePlugin, PluginHealth, PluginState

# v2 特性
from taiji_agent.mcp import MCPServerAdapter, MCPClientAdapter, MCPProtocol
from taiji_agent.guardrails import GuardrailManager, ContentFilter, QualityGate
from taiji_agent.observability import TracingManager, ConsoleExporter
from taiji_agent.hitl import ApprovalQueue, ConfidenceGate, CheckpointManager
from taiji_agent.workflow import WorkflowEngine, WorkflowGraph
from taiji_agent.handoffs import HandoffManager, AgentRegistry
from taiji_agent.code import CodeExecutor, SandboxConfig, ExecutionStatus
from taiji_agent.visual import MermaidExporter, WorkflowGraph, ExportFormat
```

---

## 🧪 测试报告

### 全量回归 (2026-05-17)

```
测试套件                          测试数    通过    状态
─────────────────────────────────────────────────────────
stress_test.py (v1 冒烟+压力)       30      30     ✅
stress_test_v2.py (v2 工程压力)     20      20     ✅
test_all_systems.py (全功能)        72      72     ✅
test_out_of_box_e2e.py (开箱E2E)   51      51     ✅
test_onboarding_parity.py (体验对比) 40      40     ✅
test_security.py (安全)             47      47     ✅
test_plugin.py (插件)               60      60     ✅
test_taiji_verify.py (太极验证)     38      38     ✅
test_v2_features.py (v2 特性)       25      25     ✅
test_multi_tenant.py (多租户)        4       4     ✅
─────────────────────────────────────────────────────────
核心测试合计                        387     387    ✅ 100%
─────────────────────────────────────────────────────────
test_grpc_bridge.py (可选: gRPC)    21       -     ⬜ 跳过
```

### 性能基准 (stress_test_v2)

| 测试 | 迭代 | 吞吐量 | 平均延迟 |
|------|------|--------|----------|
| WFGY.verify() | 50,000 | > 10,000 ops/s | < 0.1ms |
| HallucinationDetector.detect() | 30,000 | - | < 0.1ms |
| SecurityFence.check() | 100,000 | > 100,000 ops/s | < 0.01ms |
| SessionStore.save_message() | 5,000 | - | < 5ms |
| SessionStore.load_messages() | 500 | - | < 2s (3,000条) |
| EventBus.emit_sync() | 100,000 | > 10,000 ops/s | < 0.1ms |

---

## 🗺️ 路线图

### ✅ v2.0.0 (已发布)

- [x] WFGY 防幻觉系统
- [x] Soul 人格引擎
- [x] Honcho 记忆系统
- [x] 国产模型支持 (通义千问/智谱/Kimi/豆包)
- [x] 消息网关 (TG/Discord/企微/钉钉/飞书)
- [x] Skills Hub 技能市场 (7 预置)
- [x] 自我学习闭环
- [x] MCP 双向协议集成
- [x] Guardrails / Observability / HITL / Workflow / Handoffs
- [x] Code Agent + Visual Workflow

### ✅ v2.1.0 (当前版本)

- [x] 交互式 CLI (对齐 Claude Code 体验)
- [x] SQLite 会话持久化 (SessionStore)
- [x] 会话管理 (/new /switch /delete /sessions)
- [x] 上下文压缩 (/compact)
- [x] 项目上下文自动检测
- [x] Security Sandbox + SandboxPool
- [x] Provider 故障转移 (ProviderRouter)
- [x] 工具安全围栏 (SecurityFence)
- [x] 387 核心测试 100% 通过
- [x] 开箱 E2E 测试 (51 用例)
- [x] 首次体验对比测试 (40 用例)

### 🔲 v2.2.0 (规划中)

- [ ] 浏览器自动化集成 (Playwright)
- [ ] 语音模式 (TTS/STT)
- [ ] GovMCP 政务场景定制
- [ ] 记忆系统聚合与摘要
- [ ] 多语言 i18n

### 🔲 v3.0.0 (愿景)

- [ ] 生产级 Agent 运行时
- [ ] 完整自我学习闭环
- [ ] 企业级多租户隔离
- [ ] Docker / K8s 部署
- [ ] Agent 市场与分发

---

## 🤝 贡献指南

```bash
# 1. Fork 并克隆
git clone https://github.com/xiejianjun000/open-taiji.git
cd open-taiji

# 2. 创建虚拟环境
python3.11 -m venv .venv && source .venv/bin/activate

# 3. 安装开发依赖
pip install -e ".[dev]"

# 4. 运行测试
pytest tests/ -v --ignore=tests/test_grpc_bridge.py

# 5. 创建分支并提交
git checkout -b feature/your-feature
git commit -m "feat: description"
git push origin feature/your-feature
```

---

## ❓ FAQ

**Q: OpenTaiji 和 LangChain/AutoGen 的区别？**

A: 核心差异化：
- **WFGY 防幻觉** — 独有五重验证管线
- **太极验证引擎** — 5 模块 16 种故障模式检测
- **Soul 人格系统** — YAML 声明式，可热切换
- **自我学习闭环** — 交互→偏好→主题→技能 自动进化
- **政务合规** — GovMCP 支持国密 SM2/SM3/SM4

**Q: 支持哪些国产大模型？**

A: 通义千问 (Qwen)、智谱 (GLM)、Kimi、豆包 (Doubao) — 全部开箱即用。

**Q: 可以商用吗？**

A: 可以。MIT 许可证，无限制。

**Q: 如何升级到 v2.1？**

```bash
git pull origin main
pip install -e ".[all]"
taiji_agent init
```

---

## 📄 License

MIT © OpenTaiji Team

---

<div align="center">

**用太极哲学，构建下一代智能系统。**

*道生一，一生二，二生三，三生万物。*

Made with ❤️ by the OpenTaiji Team

</div>

---

*最后更新：2026-05-17*
*文档版本：v2.1.0*
