# Taiji-Agent 白皮书

## 基于太极哲学的 AI 智能体防幻觉验证框架

**版本**: 2.0.0  
**日期**: 2026年5月  

---

## 目录

1. [摘要](#1-摘要)
2. [背景与问题陈述](#2-背景与问题陈述)
3. [设计哲学：太极与 AI 验证的映射](#3-设计哲学太极与-ai-验证的映射)
4. [系统架构](#4-系统架构)
5. [Taiji Verify 核心算法](#5-taiji-verify-核心算法)
6. [病候图：16 种失败模式检测体系](#6-病候图16-种失败模式检测体系)
7. [Hermes 引擎：三层进化与跨会话记忆](#7-hermes-引擎三层进化与跨会话记忆)
8. [GovMCP：政务合规模块](#8-govmcp政务合规模块)
9. [Harness 运行时层](#9-harness-运行时层)
10. [安全模型与信任边界](#10-安全模型与信任边界)
11. [性能基准](#11-性能基准)
12. [应用场景](#12-应用场景)
13. [路线图](#13-路线图)
14. [参考文献](#14-参考文献)

---

## 1. 摘要

大语言模型（LLM）在政务、金融、医疗等高可信场景中的部署面临一个根本性挑战：**幻觉（Hallucination）**——模型生成看似合理但缺乏事实依据的内容。现有解决方案多采用单一维度的后置过滤，无法在语义空间中建立系统性的可信度度量。

**Taiji-Agent v2.0** 提出了一种基于东方太极哲学的 AI 智能体防幻觉验证框架。该框架将《易经》八卦体系与动力系统理论、李雅普诺夫稳定性分析、余弦语义距离等现代数学工具深度融合，构建了八层验证管道：

| 八卦 | 模块 | 功能 | 核心算法 |
|------|------|------|----------|
| ☰ 乾 | QianAdvance | 语义演进稳定性评估 | 多路径扰动算法 f_S = 1/(1+mean(Δ)) |
| ☷ 坤 | KunGuard | 语义残差修正 | B = I - G + m·c² |
| ☵ 坎 | DeltaS | 阴阳距计算 | ΔS = 1 - cos(I, G') |
| ☲ 离 | FuReturn | 崩溃逆转恢复 | 李雅普诺夫指数 λ 监测 |
| ☴ 巽 | XunTune | 方差门控注意力调节 | factor = exp(-γ·σ²), γ=0.618 |
| ☶ 艮 | GuanObserve | 状态追踪与异常检测 | 滑动窗口趋势分析 |
| ☱ 兑 | Polaris | 北辰目标编译器 | 任务原子化与令牌板 |
| ☳ 震 | SymptomMap | 16种失败模式检测 | 7层16模式检测器矩阵 |

本白皮书详细阐述该框架的设计哲学、数学基础、系统架构与工程实现。

---

## 2. 背景与问题陈述

### 2.1 幻觉问题的本质

LLM 幻觉并非随机错误，而是模型在语义空间中的系统性偏移。从动力系统视角看，当模型的状态向量偏离知识吸引子（Knowledge Attractor）时，输出即进入不可信区域。这种偏移具有以下特征：

- **渐近性**：偏移往往从微小残差开始，逐步累积
- **非线性**：小的输入扰动可能导致大的输出偏移（混沌边缘）
- **上下文依赖**：同一模型在不同知识域的偏移模式不同
- **自强化**：一旦偏移发生，后续生成会进一步偏离事实

### 2.2 现有方案的局限

| 方案 | 局限 |
|------|------|
| 基于规则的后置过滤 | 无法捕捉语义层面的偏移 |
| 检索增强生成（RAG） | 检索本身可能引入噪声或过时知识 |
| 自一致性采样 | 计算成本高，且一致性≠正确性 |
| 知识图谱约束 | 构建成本高，覆盖面有限 |
| 对齐训练（RLHF） | 无法完全消除幻觉，仅降低频率 |

### 2.3 Taiji-Agent 的核心洞察

Taiji-Agent 的核心洞察是：**防幻觉不是单一检测问题，而是动力系统的稳定性控制问题**。需要：

1. **度量偏移**：量化输出与知识基准的语义距离
2. **评估稳定性**：判断系统是否处于稳定吸引子附近
3. **检测前兆**：在偏移发生前识别早期信号
4. **修正偏移**：将输出拉回可信区域
5. **恢复崩溃**：当系统失控时执行逆转恢复
6. **门控注意力**：根据不确定性调节输出权重
7. **追踪状态**：持续监控语义轨迹
8. **编译目标**：将模糊目标分解为可验证的原子任务

这八个维度恰好对应《易经》八卦，构成了完整的验证闭环。

---

## 3. 设计哲学：太极与 AI 验证的映射

### 3.1 太极生两仪

太极的核心思想是阴阳对立统一。在 AI 验证语境下：

- **阴（Yin）**：知识基准（Ground Truth）—— 静态的、确定的、守恒的
- **阳（Yang）**：模型输出（LLM Output）—— 动态的、生成的、变化的

阴阳距 ΔS = 1 - cos(I, G) 正是度量"阳"偏离"阴"的程度。当 ΔS → 0，阴阳合一，输出可信；当 ΔS → 1，阴阳分离，输出不可信。

### 3.2 两仪生四象

阴阳距的四闸区体系对应四象：

```
                    ΔS
    ┌──────────┬──────────┬──────────┬──────────┐
    │  太阴    │   少阳   │   少阴   │   太阳   │
    │  SAFE    │  TRANSIT │   RISK   │  DANGER  │
    │  < 0.4   │  0.4-0.6 │  0.6-0.85│  ≥ 0.85  │
    │  可信    │  需关注  │  需修正  │  必须拦截 │
    └──────────┴──────────┴──────────┴──────────┘
```

### 3.3 四象生八卦

八卦与验证模块的完整映射：

```
                    太极 (Taiji Verify)
                        │
            ┌───────────┴───────────┐
          阴 (守)                  阳 (进)
          │                        │
     ┌────┴────┐              ┌────┴────┐
   坤守      坎距           乾进      离复归
  KunGuard  DeltaS       QianAdvance  FuReturn
  残差修正   阴阳距       稳定性评估   崩溃逆转
     │                        │
  ┌──┴──┐                 ┌──┴──┐
 艮观变  巽调            兑北辰  震病候
GuanObserve XunTune    Polaris SymptomMap
 状态追踪  注意力调节    目标编译  失败检测
```

### 3.4 黄金比例 γ = 0.618

巽调模块的敏感度系数 γ 默认取 0.618，这一数值源自太极图中的黄金分割比例。在门控公式 factor = exp(-γ·σ²) 中，γ = 0.618 提供了最优的灵敏度-鲁棒性平衡：

- γ 过小：对方差不敏感，无法有效抑制不确定输出
- γ 过大：过于敏感，可能误杀合理输出
- γ = 0.618：在数学上对应黄金分割点，是信息论意义下的最优折中

---

## 4. 系统架构

### 4.1 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                     应用层 (Application)                 │
│   CLI / Gateway / Visual Export / UI Preview            │
├─────────────────────────────────────────────────────────┤
│                   Agent 引擎层 (Engine)                  │
│   TaijiAgent Loop / Tool Execution / Soul Injection     │
├──────────────┬──────────────────────┬───────────────────┤
│  Hermes 层   │   Taiji Verify 层    │   GovMCP 层       │
│  跨会话记忆   │   八卦验证管道       │   政务合规         │
│  三层进化     │   防幻觉检测         │   国密加密         │
│  子Agent编排  │   失败模式检测       │   审批工作流       │
├──────────────┴──────────────────────┴───────────────────┤
│                   Harness 运行时层                       │
│   EventBus / Plugin / Sandbox / Streaming / HITL        │
├─────────────────────────────────────────────────────────┤
│                   基础设施层 (Infrastructure)             │
│   LLM Providers / MCP Protocol / Observability / Memory │
└─────────────────────────────────────────────────────────┘
```

### 4.2 模块清单

| 层级 | 模块 | 源码路径 | 核心类 |
|------|------|----------|--------|
| Agent | 引擎 | `agent/engine.py` | `TaijiAgent` |
| Agent | CLI | `cli/main.py` | 命令行入口 |
| Hermes | 核心引擎 | `hermes_engine.py` | `HermesAgentEngine` |
| Hermes | 提供商 | `hermes_provider.py` | `HermesProvider` |
| Verify | 阴阳距 | `taiji_verify/delta_s.py` | `DeltaSCalculator` |
| Verify | 坤守 | `taiji_verify/kun_guard.py` | `KunGuard` |
| Verify | 乾进 | `taiji_verify/qian_advance.py` | `QianAdvance` |
| Verify | 复归 | `taiji_verify/fu_return.py` | `FuReturn` |
| Verify | 巽调 | `taiji_verify/xun_tune.py` | `XunTune` |
| Verify | 观变 | `taiji_verify/guan_observe.py` | `GuanObserve` |
| Verify | 北辰 | `taiji_verify/polaris.py` | `PolarisCompiler` |
| Verify | 病候图 | `taiji_verify/symptom_map.py` | `SymptomMap` |
| Verify | 符号验证 | `wfgy/verifier.py` | `TaijiVerifier`, `HallucinationDetector` |
| GovMCP | 服务器 | `govmcp/server.py` | `GovMCPServer` |
| GovMCP | 集成 | `govmcp_integration.py` | `GovMCPIntegration` |
| GovMCP | 国密 | `govmcp/crypto.py` | SM2/SM3/SM4 |
| Harness | 事件总线 | `event_bus.py` | `EventBus` |
| Harness | 插件 | `plugin_system.py` | `Plugin` |
| Harness | 沙箱 | `sandbox.py` | 代码隔离执行 |
| Harness | 流式 | `streaming.py` | 异步流处理 |
| Harness | HITL | `hitl.py` | 人机协同 |
| 基础 | LLM | `providers/` | OpenAI/Anthropic/通义/豆包 |
| 基础 | MCP | `mcp/` | Client/Server/Protocol |
| 基础 | 记忆 | `memory/session.py` | `SessionMemory` |
| 基础 | 可观测 | `observability/` | Tracing/Export |
| 基础 | 工作流 | `workflow/` | Graph/Engine |
| 基础 | 护栏 | `guardrails/` | Input/Output Guardrail |
| 基础 | 交接 | `handoffs/` | Agent Handoff |
| 基础 | 多Agent | `multiagent/` | Coordinator |
| 基础 | 学习 | `learning/loop.py` | Self-Learning Loop |
| 基础 | 技能 | `skills/hub.py` | SkillHub |
| 基础 | 灵魂 | `souls/loader.py` | SoulLoader |
| 基础 | 工具 | `tools/registry.py` | ToolRegistry |
| 基础 | 网关 | `gateway/core.py` | 多平台网关 |
| 基础 | 代码执行 | `code/executor.py` | 沙箱执行器 |

### 4.3 数据流

```
用户输入
  │
  ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Input       │    │  Agent       │    │  LLM         │
│  Guardrail   │───▶│  Engine      │───▶│  Provider    │
│  (过滤/限速)  │    │  (Loop)      │    │  (调用模型)   │
└──────────────┘    └──────┬───────┘    └──────┬───────┘
                           │                    │
                           │    ┌───────────────┘
                           │    │ LLM 原始输出
                           ▼    ▼
                    ┌──────────────────┐
                    │  Taiji Verify    │
                    │  八卦验证管道     │
                    │                  │
                    │  ① DeltaS 阴阳距  │
                    │  ② KunGuard 修正  │
                    │  ③ QianAdvance   │
                    │    稳定性评估     │
                    │  ④ XunTune 门控  │
                    │  ⑤ FuReturn 恢复 │
                    │  ⑥ GuanObserve   │
                    │    状态追踪      │
                    │  ⑦ SymptomMap    │
                    │    失败模式检测   │
                    │  ⑧ Polaris 编译  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Output          │
                    │  Guardrail       │
                    │  (敏感数据过滤/   │
                    │   质量门禁)       │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  HITL            │
                    │  (人工审批/       │
                    │   置信度评估)     │
                    └────────┬─────────┘
                             │
                             ▼
                         用户输出
```

---

## 5. Taiji Verify 核心算法

### 5.1 DeltaS —— 阴阳距计算（☵ 坎）

#### 5.1.1 数学定义

阴阳距是 Taiji Verify 的基础度量，定义为输入向量 I 与知识向量 G 之间的余弦距离：

$$\Delta S = 1 - \cos(I, G') = 1 - \frac{I \cdot G'}{\|I\| \cdot \|G'\|}$$

其中 $G'$ 是知识向量与锚点向量的加权融合：

$$G' = \text{normalize}\left(G + \sum_{i} w_i \cdot A_i\right)$$

$A_i$ 为第 i 个锚点扩展向量，$w_i$ 为其权重。

#### 5.1.2 四闸区映射

| 闸区 | ΔS 范围 | 含义 | 动作 |
|------|---------|------|------|
| SAFE | [0, 0.4) | 输出与知识高度一致 | 直接放行 |
| TRANSIT | [0.4, 0.6) | 存在轻微偏移 | 标记关注 |
| RISK | [0.6, 0.85) | 显著偏移 | 触发修正 |
| DANGER | [0.85, 1.0] | 严重偏离 | 强制拦截 |

#### 5.1.3 锚点扩展机制

DeltaSCalculator 支持知识锚点扩展，允许将多个知识源融合为增强的基准向量：

```python
calc = DeltaSCalculator()
calc.add_anchor("环保法规第十二条", weight=1.0)
calc.add_anchor("排放标准GB13271", weight=0.8)
result = calc.compute_from_texts(
    input_text="该项目排放达标",
    ground_truth="项目排放浓度符合国家标准",
    embed_fn=my_embedder,
)
```

锚点融合公式确保知识基准不是单一来源，而是多维知识空间的投影，从而提高验证的鲁棒性。

### 5.2 KunGuard —— 语义残差修正（☷ 坤）

#### 5.2.1 核心公式

坤守模块的核心是语义残差修正公式：

$$B = I - G + m \cdot c^2$$

其中：
- $I$：输入向量（LLM 输出的 Embedding）
- $G$：知识向量（Ground Truth 的 Embedding）
- $m$：残差修正系数（默认 0.5）
- $c$：知识库置信度向量

该公式的直觉是：将输出向量减去知识偏差（I - G），再加上知识置信度的加权修正（m·c²），使修正后的向量更接近知识基准。

#### 5.2.2 四级危害体系

| 等级 | 残差范围 | 含义 | 处置 |
|------|----------|------|------|
| LOW | [0, 0.3) | 低风险 | 无需修正 |
| MEDIUM | [0.3, 0.6) | 中等风险 | 建议修正 |
| HIGH | [0.6, 0.9) | 高风险 | 必须修正 |
| CRITICAL | [0.9, 1.0] | 严重风险 | 强制拦截 |

#### 5.2.3 知识锚点投影

当残差超过阈值时，KunGuard 将修正向量投影到最近的知识锚点方向：

$$V_{\text{projected}} = (1 - s) \cdot V_{\text{corrected}} + s \cdot A_{\text{nearest}}$$

其中 $s$ 为与最近锚点的余弦相似度。这种投影确保修正不会将输出推向知识空间中的"无人区"。

### 5.3 QianAdvance —— 语义演进稳定性评估（☰ 乾）

#### 5.3.1 多路径扰动算法

乾进模块通过多路径扰动分析评估语义稳定性：

1. 对输入向量 V 生成 k 条扰动路径：$V_i' = V + \epsilon_i$，其中 $\epsilon_i \sim \mathcal{N}(0, \sigma^2)$
2. 计算每条路径的距离变化：$\Delta_i = \|V_{\text{norm}} - V_i'_{\text{norm}}\|$
3. 计算稳定性得分：

$$f_S = \frac{1}{1 + \overline{\Delta}}$$

其中 $\overline{\Delta} = \frac{1}{k}\sum_{i=1}^{k} \Delta_i$。

#### 5.3.2 稳定性分区

| 区域 | f_S 范围 | 含义 |
|------|----------|------|
| STABLE | [0.7, 1.0] | 系统稳定，输出可靠 |
| MARGINAL | [0.4, 0.7) | 边缘稳定，需要关注 |
| UNSTABLE | [0.2, 0.4) | 不稳定，建议修正 |
| CHAOTIC | [0, 0.2) | 混沌状态，必须拦截 |

#### 5.3.3 语义演进优化

当稳定性不足时，QianAdvance 执行迭代优化：

1. 在每轮迭代中生成 k 条扰动路径
2. 筛选相似度 > 0.8 的稳定路径
3. 对稳定路径取均值作为新的基准向量
4. 重复直到稳定性达标或达到最大迭代次数

该算法的收敛性由收敛阈值（默认 0.01）和最大迭代次数（默认 10）保证。

### 5.4 FuReturn —— 崩溃逆转恢复（☲ 离）

#### 5.4.1 李雅普诺夫指数监测

复归模块引入动力系统的李雅普诺夫指数来监测语义崩溃：

$$\lambda = \lim_{t \to \infty} \frac{1}{t} \ln\left|\frac{\delta(t)}{\delta(0)}\right|$$

在实际计算中，使用状态历史序列的离散近似：

$$\lambda \approx \frac{1}{N} \sum_{i=1}^{N} \frac{\ln(\|S_i\| / \|S_{i-1}\|)}{\Delta t}$$

- $\lambda > 0$：系统发散（不稳定），可能发生幻觉
- $\lambda < 0$：系统收敛（稳定），输出可信

#### 5.4.2 状态机驱动的恢复

```
NORMAL ──(λ > 0.5 or residual > 0.6)──▶ WARNING
WARNING ──(λ > Bc or residual > 0.9)──▶ CRASHING
CRASHING ──▶ RECOVERING ──▶ RECOVERED / FAILED
```

#### 5.4.3 自适应恢复策略

| 李雅普诺夫指数 | 恢复策略 | 描述 |
|----------------|----------|------|
| λ > 1.0 | 硬重置 | 直接替换为稳定参考向量 |
| 0.5 < λ ≤ 1.0 | 快速收敛 | 线性插值向参考向量恢复 |
| λ ≤ 0.5 | 微调 | 以 α=0.1 的步长缓慢修正 |

恢复公式（快速收敛模式）：

$$V_{\text{recovered}} = (1 - \alpha) \cdot V_{\text{current}} + \alpha \cdot V_{\text{stable}}$$

其中 $\alpha = \min(0.3, \frac{1}{n+1})$，n 为尝试次数。

### 5.5 XunTune —— 方差门控注意力调节（☴ 巽）

#### 5.5.1 门控公式

$$\text{factor} = e^{-\gamma \cdot \sigma^2}$$

其中：
- $\sigma^2$：输出分布的方差
- $\gamma$：敏感度系数，默认 0.618（太极黄金比例）
- factor ∈ [min_factor, 1.0]，min_factor 默认 0.05

#### 5.5.2 物理直觉

当模型对某个输出不确定时，多次采样的方差 $\sigma^2$ 会很大，门控因子趋近于 0，从而降低该输出在最终融合中的权重。反之，当模型确信时，方差小，门控因子接近 1，保持原有注意力。

#### 5.5.3 多输出融合

对于 LLM 多层输出的融合：

$$V_{\text{fused}} = \sum_{i} w_i' \cdot V_i, \quad w_i' = \frac{w_i \cdot \text{factor}_i}{\sum_j w_j \cdot \text{factor}_j}$$

### 5.6 GuanObserve —— 状态追踪与异常检测（☶ 艮）

#### 5.6.1 滑动窗口追踪

观变模块维护一个大小为 W 的滑动窗口，记录状态向量的时序快照：

$$\text{History} = [S_{t-W+1}, S_{t-W+2}, \ldots, S_t]$$

每个快照包含：时间戳、状态向量、与参考向量的相似度、变化类型。

#### 5.6.2 变化类型检测

| 类型 | 判定条件 | 含义 |
|------|----------|------|
| STABLE | |Δsim| ≤ 0.05 | 状态稳定 |
| GRADUAL | 0.05 < |Δsim| ≤ abrupt_threshold | 渐变趋势 |
| ABRUPT | |Δsim| > abrupt_threshold | 突变事件 |
| ANOMALY | sim < similarity_threshold | 异常偏移 |

#### 5.6.3 趋势分析

使用线性回归拟合相似度序列的趋势方向：

$$\text{trend} = \text{polyfit}([0, 1, \ldots, W-1], [s_0, s_1, \ldots, s_{W-1}], 1)[0]$$

- trend > 0：相似度上升，系统趋于稳定
- trend < 0：相似度下降，系统趋于不稳定

异常分数定义为：

$$\text{anomaly\_score} = \frac{1}{W} \sum_{i=0}^{W-1} (1 - s_i)$$

### 5.7 Polaris —— 北辰目标编译器（☱ 兑）

#### 5.7.1 六阶段执行管道

```
GOAL_COMPILATION → TASK_GRAPH → ATOM_TABLE → EXECUTION_TOKEN_BOARD → ROUND_LOCK → CLOSURE_RECORD
```

1. **目标编译**：将自然语言目标解析为任务原子序列
2. **任务图构建**：建立原子间的依赖关系
3. **原子表管理**：维护所有任务原子的状态
4. **执行令牌板**：为每个原子分配执行令牌，控制执行顺序
5. **轮次锁**：确保同一轮次内的原子性执行
6. **关闭记录**：记录执行结果和关闭信息

#### 5.7.2 任务原子化

每个 TaskAtom 包含：

```python
@dataclass
class TaskAtom:
    atom_id: str           # 唯一标识
    type: TaskType         # ATOMIC / COMPOSITE / CONDITIONAL
    description: str       # 任务描述
    state: TaskState       # PENDING / ACTIVE / BLOCKED / COMPLETED / FAILED
    dependencies: list[str] # 依赖的原子ID列表
    result: Any            # 执行结果
    error: str | None      # 错误信息
```

#### 5.7.3 依赖感知调度

编译器采用依赖感知的轮次调度：

1. 每轮获取所有未认领且依赖已完成的令牌
2. 按优先级排序后依次执行
3. 轮次锁保证同一轮内的原子性
4. 所有原子完成或失败后生成关闭记录

---

## 6. 病候图：16 种失败模式检测体系

### 6.1 七层检测架构

SymptomMap 将 AI 系统的失败模式分为七个层级，共 16 种检测器：

```
┌─────────────────────────────────────────┐
│  Safety 层 (1种)                         │
│  └─ SAFETY_BREACH: 安全边界突破          │
├─────────────────────────────────────────┤
│  Knowledge 层 (1种)                      │
│  └─ KNOWLEDGE_CONFLICT: 知识冲突         │
├─────────────────────────────────────────┤
│  Tool 层 (2种)                           │
│  ├─ TOOL_MISUSE: 工具误用               │
│  └─ TOOL_API_FAILURE: API调用失败        │
├─────────────────────────────────────────┤
│  Agent 层 (3种)                          │
│  ├─ AGENT_ROLE_MISMATCH: 角色错位        │
│  ├─ AGENT_GOAL_DRIFT: 目标漂移           │
│  └─ AGENT_REFUSAL: 拒绝执行             │
├─────────────────────────────────────────┤
│  Memory 层 (3种)                         │
│  ├─ MEMORY_CONFUSION: 记忆混淆           │
│  ├─ MEMORY_CONTEXT_LOSS: 上下文丢失      │
│  └─ MEMORY_CONTAMINATION: 记忆污染       │
├─────────────────────────────────────────┤
│  Reasoning 层 (4种)                      │
│  ├─ REASONING_LOGICAL_JUMP: 逻辑跳跃     │
│  ├─ REASONING_CIRCULAR: 循环推理         │
│  ├─ REASONING_HALLUCINATION: 幻觉生成    │
│  └─ REASONING_MATH_ERROR: 数学错误       │
├─────────────────────────────────────────┤
│  RAG 层 (4种)                            │
│  ├─ RAG_RETRIEVAL_FAILURE: 检索失败      │
│  ├─ RAG_LOW_RELEVANCE: 相关性不足        │
│  ├─ RAG_OUTDATED_KNOWLEDGE: 过时知识     │
│  └─ RAG_NOISE_INJECTION: 噪声注入       │
└─────────────────────────────────────────┘
```

### 6.2 检测器设计模式

所有检测器继承自抽象基类 `Detector`：

```python
class Detector(ABC):
    @abstractmethod
    def detect(self, input_text: str, context: dict | None = None) -> FailureDetection | None: ...

    @property
    @abstractmethod
    def pattern(self) -> FailurePattern: ...
```

每个检测器返回 `FailureDetection`，包含：
- 失败模式类型（pattern）
- 所属层级（level）
- 置信度（confidence）
- 描述（description）
- 修复建议（suggested_fix）
- 证据（evidence）

### 6.3 风险评分

总体风险评分基于所有触发检测器的置信度加权均值：

$$\text{risk} = \frac{1}{N}\sum_{i=1}^{N} c_i$$

其中 $c_i$ 为第 i 个触发检测器的置信度。当 risk < 0.5 时判定为通过。

### 6.4 典型检测逻辑示例

**逻辑跳跃检测**（ReasoningLogicalJumpDetector）：扫描文本中的逻辑跳跃指示词（"显然"、"不言而喻"、"由此可见"等），当指示词出现 ≥ 3 次时触发。

**幻觉生成检测**（ReasoningHallucinationDetector）：识别未经证实的断言模式（"根据内部知识"、"研究表明"、"数据显示"等），对缺乏引用支持的断言标记为幻觉风险。

**数学错误检测**（ReasoningMathErrorDetector）：使用正则表达式提取文本中的数学表达式，验证计算结果的正确性。

---

## 7. Hermes 引擎：三层进化与跨会话记忆

### 7.1 跨会话记忆系统

CrossSessionMemory 实现了持久化的记忆存储与检索：

- **记忆条目**：包含用户ID、会话ID、内容、Embedding、重要性评分、标签
- **多维索引**：按用户、会话、内容关键词建立索引
- **向量检索**：支持基于 Embedding 的语义搜索
- **上下文组装**：将近期记忆与语义相关记忆融合为上下文窗口
- **自动清理**：基于重要性评分和时间的 LRU 淘汰策略

### 7.2 三层进化机制

```
┌─────────────────────────────────────────────┐
│  系统进化 (SYSTEM)                           │
│  阈值: 100次反馈, 成功率 ≥ 85%               │
│  效果: 全局共享优化                           │
├─────────────────────────────────────────────┤
│  部门进化 (DEPARTMENT)                       │
│  阈值: 20次反馈, 成功率 ≥ 80%                │
│  效果: 同部门内共享优化                        │
├─────────────────────────────────────────────┤
│  个体进化 (INDIVIDUAL)                       │
│  阈值: 5次反馈, 成功率 ≥ 70%                 │
│  效果: 针对单个用户的个性化优化                 │
└─────────────────────────────────────────────┘
```

进化触发条件：当某实体的反馈数量和成功率同时超过阈值时，自动触发进化，更新响应模式和技能权重。

### 7.3 十三神子 Agent 编排

Hermes 内置五个领域子 Agent，以中国古代神话人物命名：

| Agent | 名称 | 领域 | 核心技能 |
|-------|------|------|----------|
| zhangjie | 仓颉 | 环评审批 | document_analysis, policy_check, approval_workflow |
| zhurong | 祝融 | 消防预警 | safety_inspection, risk_assessment, alert_generation |
| shennong | 神农 | 污染监测 | data_collection, pollution_analysis, report_generation |
| fuxi | 伏羲 | 数据分析 | statistics, machine_learning, visualization |
| yu | 禹 | 水利工程 | engineering_consult, project_planning, resource_allocation |

子 Agent 通过 `SubAgentOrchestrator` 进行任务分发、状态追踪和结果回收。

---

## 8. GovMCP：政务合规模块

### 8.1 设计目标

GovMCP 模块为 Taiji Agent 提供政务场景的合规能力：

- **国密加密**：SM2（非对称加密）、SM3（哈希）、SM4（对称加密）
- **审批工作流**：多级审批、条件分支、超时处理
- **审计日志**：全链路操作记录、防篡改、可追溯
- **政务工具**：数据脱敏、格式验证、日历计算

### 8.2 MCP 协议集成

GovMCP 基于 Model Context Protocol（MCP）标准，既可作为 MCP Server 对外提供服务，也可通过 MCP Client 连接外部工具：

```
┌──────────────┐     MCP Protocol     ┌──────────────┐
│  Taiji Agent │◄────────────────────▶│  GovMCP      │
│  (MCP Client)│                      │  Server      │
└──────────────┘                      └──────────────┘
       │                                     │
       │  ToolAdapter                        │  国密/审批/审计
       ▼                                     ▼
  Hermes Agent                         政务工具集
```

### 8.3 工具分类

| 类别 | 工具示例 | 说明 |
|------|----------|------|
| crypto | sm2_encrypt, sm2_decrypt, sm3_hash, sm4_encrypt | 国密算法套件 |
| workflow | approval_create, approval_approve, approval_reject | 审批工作流 |
| audit | audit_log, audit_query, audit_export | 审计日志 |
| gov | data_mask, format_validate, calendar_calculate | 政务通用工具 |

---

## 9. Harness 运行时层

### 9.1 事件总线

EventBus 实现发布-订阅模式，支持以下事件类型：

| 事件类型 | 触发时机 |
|----------|----------|
| LLM_REQUEST | LLM 请求发送前 |
| LLM_RESPONSE | LLM 响应返回后 |
| TOOL_CALL | 工具调用时 |
| TOOL_RESULT | 工具返回结果时 |
| AGENT_START | Agent 启动时 |
| AGENT_END | Agent 结束时 |
| TAIJI_VERIFY_RESULT | Taiji Verify 验证完成时 |

### 9.2 插件系统

Plugin 基类定义了插件生命周期：

```python
class Plugin(ABC):
    async def on_load(self) -> bool: ...    # 加载
    async def on_unload(self): ...          # 卸载
    async def on_activate(self) -> bool: ... # 激活
    async def on_deactivate(self): ...      # 停用
```

TaijiVerifyPlugin 即通过此机制集成到运行时，订阅 LLM_RESPONSE 事件自动执行验证。

### 9.3 沙箱执行

代码执行器提供隔离的执行环境：

- 资源限制：CPU 时间、内存使用、文件系统访问
- 超时控制：可配置的执行超时
- 输出捕获：标准输出和错误输出的完整捕获

### 9.4 人机协同（HITL）

HITL 模块提供三个层次的介入机制：

| 组件 | 功能 | 触发条件 |
|------|------|----------|
| Approval | 人工审批 | 高风险操作 |
| Checkpoint | 断点保存/恢复 | 关键决策点 |
| Confidence | 置信度评估 | 自动判断是否需要人工 |

---

## 10. 安全模型与信任边界

### 10.1 纵深防御体系

```
┌─────────────────────────────────────────────────┐
│  第1层: Input Guardrail (输入护栏)               │
│  ├─ 内容过滤: 敏感词/违规内容                     │
│  ├─ 速率限制: 防止滥用                           │
│  └─ 长度限制: 防止上下文溢出                      │
├─────────────────────────────────────────────────┤
│  第2层: Taiji Verify (八卦验证管道)               │
│  ├─ DeltaS: 语义偏移度量                         │
│  ├─ KunGuard: 残差修正                           │
│  ├─ QianAdvance: 稳定性评估                      │
│  ├─ XunTune: 不确定性门控                        │
│  ├─ FuReturn: 崩溃恢复                           │
│  ├─ GuanObserve: 状态追踪                        │
│  ├─ SymptomMap: 失败模式检测                     │
│  └─ Polaris: 目标编译                            │
├─────────────────────────────────────────────────┤
│  第3层: Output Guardrail (输出护栏)               │
│  ├─ 敏感数据过滤: PII/密钥/内部信息               │
│  ├─ 质量门禁: 格式/完整性检查                     │
│  └─ 幻觉门禁: 基于验证结果的最终拦截               │
├─────────────────────────────────────────────────┤
│  第4层: HITL (人机协同)                           │
│  ├─ 置信度评估: 自动判断是否需要人工               │
│  ├─ 审批流程: 高风险操作的人工确认                 │
│  └─ 断点恢复: 异常场景的状态回滚                   │
├─────────────────────────────────────────────────┤
│  第5层: GovMCP (政务合规)                         │
│  ├─ 国密加密: 数据传输和存储加密                   │
│  ├─ 审计日志: 全链路操作记录                       │
│  └─ 审批工作流: 多级审批机制                       │
└─────────────────────────────────────────────────┘
```

### 10.2 信任边界

| 信任级别 | 条件 | 允许操作 |
|----------|------|----------|
| TRUSTED | ΔS < 0.4 且 f_S > 0.7 且无失败模式 | 全部操作 |
| CONDITIONAL | 0.4 ≤ ΔS < 0.6 或存在 LOW/MEDIUM 失败 | 有限操作，需记录 |
| SUSPICIOUS | 0.6 ≤ ΔS < 0.85 或存在 HIGH 失败 | 需人工确认 |
| BLOCKED | ΔS ≥ 0.85 或存在 CRITICAL 失败 | 拦截输出 |

### 10.3 符号层验证

除向量空间验证外，Taiji Agent 还实现了符号层验证（`wfgy/verifier.py`）：

- **TaijiVerifier**：基于正则规则和知识库的符号验证
- **HallucinationDetector**：综合评分 = Taiji Verify(40%) + 自一致性(30%) + 知识溯源(30%)
- **SelfConsistencyChecker**：多路径采样 + Jaccard 相似度投票
- **SourceTracer**：知识溯源索引，每个结论可追溯到原始来源

---

## 11. 性能基准

### 11.1 覆盖率

| 等级 | 模块数 | 代表模块 |
|------|--------|----------|
| >80% (优秀) | 12 | kun_guard(89%), xun_tune(88%), govmcp_integration(88%), polaris(86%) |
| 60-80% (良好) | 14 | event_bus(70%), hermes_engine(72%), sandbox(66%) |
| 40-60% (需加强) | 12 | tools(43%), agent_engine(43%), guardrails(44%) |
| <40% (严重不足) | 45 | cli(0%), hitl模块(0%), plugins(0%), mcp(21%) |

总覆盖率：51%（分支覆盖）。

### 11.2 验证管道延迟

基于 128 维 Embedding 的单次验证延迟（不含 LLM 调用）：

| 模块 | 平均延迟 | 说明 |
|------|----------|------|
| DeltaS | < 1ms | 纯向量运算 |
| KunGuard | < 1ms | 向量运算 + 锚点投影 |
| QianAdvance | ~5ms | k=5 路径扰动 |
| XunTune | < 1ms | 方差计算 + 指数运算 |
| FuReturn | < 1ms | 状态机判定 |
| GuanObserve | < 1ms | 窗口内统计 |
| SymptomMap | ~2ms | 16 个检测器遍历 |

完整管道端到端延迟约 10ms（不含 Embedding 计算和 LLM 调用）。

---

## 12. 应用场景

### 12.1 政务环评审批

```
用户: "请分析该项目的环评报告"
  │
  ▼
TaijiAgent
  ├─ Polaris 编译目标 → [检索文档, 提取指标, 对比标准, 生成报告]
  ├─ 调用 仓颉 子Agent 执行环评审批流程
  ├─ DeltaS 验证报告与法规的一致性
  ├─ KunGuard 修正可能的语义偏移
  ├─ GovMCP 审批工作流 + 国密加密
  └─ HITL 人工确认高风险结论
```

### 12.2 金融合规审查

- **DeltaS**：验证分析报告与监管条文的一致性
- **SymptomMap**：检测数据引用错误、逻辑跳跃
- **GovMCP**：数据脱敏、审计日志
- **FuReturn**：当分析出现矛盾时自动回退

### 12.3 医疗辅助诊断

- **DeltaS**：验证诊断建议与医学知识库的一致性
- **QianAdvance**：评估诊断结论的稳定性
- **SymptomMap**：检测过度自信、循环推理
- **HITL**：高风险诊断必须经医生确认

### 12.4 多 Agent 协作

- **Polaris**：将复杂任务编译为原子任务图
- **Handoffs**：Agent 间的任务交接与状态传递
- **Multiagent Coordinator**：并行/串行/层级协同模式
- **GuanObserve**：追踪各 Agent 的状态变化

---

## 13. 路线图

### v2.1（计划）

- [ ] 补全 45 个 <40% 覆盖率模块的测试
- [ ] 同步 test_taiji_verify.py 与 v2.0 API
- [ ] ruff 代码风格统一（639 个问题修复）
- [ ] str+Enum 迁移到 enum.StrEnum

### v2.2（计划）

- [ ] DeltaS 自适应阈值：根据领域动态调整闸区边界
- [ ] QianAdvance 可微分化：支持梯度回传的稳定性优化
- [ ] SymptomMap LLM 增强：利用 LLM 进行深度语义检测
- [ ] FuReturn 预测性恢复：基于趋势预测提前触发恢复

### v3.0（远期）

- [ ] 多模态验证：图像/表格/公式的幻觉检测
- [ ] 联邦验证：跨组织的知识基准共享
- [ ] 因果推理：从相关性检测升级为因果性验证
- [ ] 自进化验证：验证规则自身的自动优化

---

## 14. 参考文献

1. **Lyapunov Stability Theory** — Lyapunov, A.M. (1892). *The General Problem of the Stability of Motion*.
2. **Cosine Similarity in Semantic Space** — Salton, G. & McGill, M.J. (1983). *Introduction to Modern Information Retrieval*.
3. **Self-Consistency Sampling** — Wang, X. et al. (2022). *Self-Consistency Improves Chain of Thought Reasoning in Language Models*.
4. **Model Context Protocol** — Anthropic (2024). *MCP Specification*.
5. **SM2/SM3/SM4 National Cryptography Standards** — GM/T 0003-2012, GM/T 0004-2012, GM/T 0002-2012.
6. **《周易》** — 周文王 (约公元前1046年). *I Ching: Book of Changes*.
7. **Golden Ratio in Information Theory** — Stakhov, A.P. (2009). *The Mathematics of Harmony*.

---

*本白皮书基于 Taiji-Agent v2.0.0 源码（83 个 Python 文件，18,737 行）撰写，所有算法描述与代码实现一一对应。*
