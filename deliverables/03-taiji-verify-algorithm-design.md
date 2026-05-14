# 太极 Verify 算法设计草案

> 基于 WFGY 协议蓝图 · 太极哲学命名体系
> 版本: 0.1 (设计草案)
> 生成日期: 2026-05-14

---

## 目录

1. [设计总纲](#1-设计总纲)
2. [核心算法模块](#2-核心算法模块)
3. [系统架构](#3-系统架构)
4. [接口定义](#4-接口定义)
5. [实现路线图](#5-实现路线图)

---

## 1. 设计总纲

### 1.1 设计理念

太极 Verify 算法的三大哲学支柱:

| 哲学 | 协议映射 | 工程意义 |
|------|----------|----------|
| 阴阳平衡 | 阴阳距 ΔS 度量语义对齐程度 | 提供可计算的语义对标指标 |
| 刚柔并济 | 坤守(稳定) + 乾进(探索) 的动态平衡 | 在保守和探索之间自动调节 |
| 周而复始 | 复归崩溃逆转变为系统提供韧性 | 自恢复能力，故障不扩散 |

### 1.2 算法运行原则

1. **编译优先，拒绝直接执行**: 自然语言不可直接执行，必须通过北辰编译器
2. **度量先行，验证后行**: 只有通过阴阳距检查的状态才能继续
3. **单原子原则**: 每回合只执行一个活性原子
4. **真值先于表达**: 真值承载工作必须优先于表达工作
5. **泄漏阻断**: 任何回合不允许下游内容泄漏至当前输出

### 1.3 关键假设

- 嵌入向量可使用任一标准文本嵌入模型（如 text-embedding-3-small, 1536 维）
- I 和 G 使用同一嵌入模型以确保 cosine 可比性
- 北辰编译器运行在 LLM 的思维链内或作为结构化预处理步骤
- 默认可信上下文由系统规则 + 用户请求构成

---

## 2. 核心算法模块

### 2.1 阴阳距计算器 (ΔS Calculator)

#### 算法签名

```python
def calculate_delta_s(
    I: np.ndarray,      # 当前状态的嵌入向量 [d,]
    G: np.ndarray,      # 目标状态的嵌入向量 [d,]
    anchors: Optional[AnchorSet] = None,  # 锚点集合
    weights: Optional[Dict[str, float]] = None,  # 锚点权重
    dim_renormalize: bool = True
) -> DeltaSResult:
```

#### 算法流程

```
Algorithm: calculate_delta_s
Input: I, G, anchors?, weights?, renormalize?
Output: ΔS, sim_raw, zone, zone_enum

1.  BASE_SIM = cosine_similarity(I, G)
   a. cos(I, G) = (I·G) / (‖I‖·‖G‖)
   b. If dim_renormalize: I = I / ‖I‖; G = G / ‖G‖

2.  ΔS_raw = 1.0 - BASE_SIM

3.  IF anchors 存在:
   a. w_e, w_r, w_c = weights or {0.5, 0.3, 0.2}
   b. sim_e = mean([cos(I_e, G_e) for each entity anchor])
   c. sim_r = mean([cos(I_r, G_r) for each relation anchor])
   d. sim_c = mean([cos(I_c, G_c) for each constraint anchor])
   e. sim_est = w_e*sim_e + w_r*sim_r + w_c*sim_c
   f. sim_est = clip(sim_est, 0.0, 1.0)
   g. ΔS = 1.0 - sim_est
   ELSE:
   h. ΔS = ΔS_raw

4.  DETERMINE ZONE:
   IF ΔS < 0.40: zone = SAFE, zone_enum = 0
   ELIF ΔS < 0.60: zone = TRANSIT, zone_enum = 1
   ELIF ΔS < 0.85: zone = RISK, zone_enum = 2
   ELSE: zone = DANGER, zone_enum = 3

5.  RETURN DeltaSResult(ΔS, BASE_SIM, zone, zone_enum)
```

#### 数据结构

```python
@dataclass
class DeltaSResult:
    delta_s: float            # 阴阳距 [0, 1]
    similarity_raw: float     # 原始相似度
    zone: str                 # "safe" | "transit" | "risk" | "danger"
    zone_enum: int            # 0 | 1 | 2 | 3

@dataclass
class AnchorSet:
    entities: List[Tuple[np.ndarray, np.ndarray]]  # [(I_e, G_e), ...]
    relations: List[Tuple[np.ndarray, np.ndarray]]
    constraints: List[Tuple[np.ndarray, np.ndarray]]
```

### 2.2 坤守语义残差修正器 (BBMC Kun Guard)

#### 算法签名

```python
def kun_guard(
    I: np.ndarray,      # 当前嵌入
    G: np.ndarray,      # 目标嵌入
    context_tokens: int, # 上下文 token 数（用于 c 因子计算）
    B_c: float = 0.85,  # 崩溃阈值
    record_threshold: float = 0.60,  # 记录阈值
    exemplar_threshold: float = 0.35  # 典范阈值
) -> KunGuardResult:
```

#### 算法流程

```
Algorithm: kun_guard
Input: I, G, context_tokens, B_c, record_threshold, exemplar_threshold
Output: B_residual, norm_B, action, memory_record?

1.  COMPUTE matching coefficient m:
    m = cos(I, G)  # 范围 [0, 1]

2.  COMPUTE context factor c:
    c = (context_tokens / 100.0)       # Δtoken / 100
    c = clip(c, 0.2, 1.5)              # 限制范围

3.  COMPUTE residual B:
    B = I - G + m * c**2               # 向量残差
    norm_B = ‖B‖₂                       # L2 范数

4.  COMPUTE ΔS (reuse calculate_delta_s):
    delta_s = 1.0 - m                   # ΔS = 1 - cos(I, G)

5.  DETERMINE hazard_level:
    IF norm_B >= B_c:
        hazard = "COLLAPSE"            # 触发复归
    ELIF norm_B >= 0.85 * B_c:
        hazard = "WARNING"
    ELSE:
        hazard = "NORMAL"

6.  DETERMINE memory_action:
    IF delta_s > record_threshold:
        memory = "RECORD_HARD"
    ELIF delta_s < exemplar_threshold:
        memory = "RECORD_EXEMPLAR"
    ELSE:
        memory = "NO_RECORD"

7.  ATTEMPT residual minimization (if hazard == WARNING):
    # 投影法: 将 B 投影至 G 方向，保留正交残差
    B_proj = (B·G / ‖G‖²) * G          # 平行于 G 的分量
    B_orth = B - B_proj                 # 正交于 G 的分量
    B_min = B_proj * 0.5 + B_orth       # 衰减平行分量
    norm_B_min = ‖B_min‖₂

    IF norm_B_min < norm_B:
        B = B_min; norm_B = norm_B_min

8.  RETURN KunGuardResult(B, norm_B, hazard, memory, delta_s)
```

#### 数据结构

```python
@dataclass
class KunGuardResult:
    B_residual: np.ndarray    # 残差向量
    norm_B: float             # 残差 L2 范数
    hazard: str               # "NORMAL" | "WARNING" | "COLLAPSE"
    memory_action: str        # "NO_RECORD" | "RECORD_HARD" | "RECORD_EXEMPLAR"
    delta_s: float            # 阴阳距

@dataclass
class MemoryRecord:
    topic: str                # 主题标签
    module: str               # "BBMC" | "BBPF" | "BBCR" | "BBAM"
    delta_s: float            # 阴阳距
    lambda_state: str         # λ 状态
    timestamp: float          # 时间戳
    insight_encoded: str      # 编码洞察
```

### 2.3 乾进多路径演进器 (BBPF Qian Advance)

#### 算法签名

```python
def qian_advance(
    x: np.ndarray,              # 当前语义状态
    G: np.ndarray,              # 目标嵌入
    delta_s_prev: float,        # 前一步阴阳距
    delta_s_now: float,         # 当前阴阳距
    k_paths: int = 3,           # 并行路径数
    noise_scale: float = 0.1,   # 扰动尺度
    theta_c: float = 0.75,      # 耦合阈值
    zeta_min: float = 0.10,     # 最小推进
    omega: float = 1.0,         # 推进指数
    phi_delta: float = 0.15,    # 翻转幅度
    epsilon: float = 0.0,       # 偏置项
    hysteresis_h: float = 0.02  # 迟滞窗口
) -> QianAdvanceResult:
```

#### 算法流程

```
Algorithm: qian_advance
Input: x, G, delta_s_prev, delta_s_now, k_paths, noise_scale,
       theta_c, zeta_min, omega, phi_delta, epsilon, hysteresis_h
Output: candidates[], bridge_enabled, W_c, f_S

Phase 1 — Coupler Computation:

1.  B_s = delta_s_now                    # 当前张力

2.  IF t == 1:
        prog = zeta_min                   # 初始步长
    ELSE:
        prog = max(zeta_min, delta_s_prev - delta_s_now)

3.  P = pow(prog, omega)                 # 推进力

4.  alt = resolve_alt_anchor(
        anchors_history, hysteresis_h
    )                                     # 锚点翻转方向 (+1/-1)
    Phi = phi_delta * alt + epsilon       # 反转项

5.  W_c = clip(B_s * P + Phi, -theta_c, +theta_c)
       # 耦合器输出，范围 [-theta_c, +theta_c]

Phase 2 — Multi-Path Perturbation:

6.  candidates = []
    FOR i in range(k_paths):
        epsilon_i = noise_scale * (1.0 + 0.5 * random_gauss())
        V_i = epsilon_i * random_unit_vector(dim=x.shape[0])
        candidate = x + V_i
        sim_i = cos(candidate, G)
        ΔS_i = 1.0 - sim_i
        candidates.append({
            "state": candidate,
            "delta_s": ΔS_i,
            "noise": epsilon_i
        })

    # 按 ΔS 升序排序（越接近目标越优先）
    candidates.sort(key=lambda c: c["delta_s"])

Phase 3 — Stability Score:

7.  mean_ΔS = mean([c["delta_s"] for c in candidates])
    f_S = 1.0 / (1.0 + mean_ΔS)

Phase 4 — Bridge Decision:

8.  bridge_enabled = (
        delta_s_now < delta_s_prev       # ΔS 降低
        AND abs(W_c) < 0.5 * theta_c     # 耦合器不饱和
        AND WDT_pass                     # 唯理门检查
    )

9.  IF bridge_enabled:
        bridge = {
            "reason": "ΔS decreased, coupler unsaturated",
            "prior_delta_s": delta_s_prev,
            "new_path": candidates[0]["state"]
        }

10. RETURN (candidates, bridge_enabled, W_c, f_S)
```

#### 参数调优建议

| 场景 | k_paths | noise_scale | zeta_min | omega | 说明 |
|------|---------|-------------|----------|-------|------|
| 精确问答 | 2-3 | 0.05 | 0.10 | 1.5 | 高聚焦，小扰动 |
| 政策检索 | 3-4 | 0.05 | 0.15 | 1.0 | 中等聚焦 |
| 创意思考 | 5-8 | 0.20 | 0.05 | 0.8 | 大探索空间 |
| 故障恢复 | 1-2 | 0.02 | 0.20 | 2.0 | 稳妥优先 |

#### 数据结构

```python
@dataclass
class CandidatePath:
    state: np.ndarray
    delta_s: float
    noise_level: float

@dataclass
class QianAdvanceResult:
    candidates: List[CandidatePath]
    bridge_enabled: bool
    bridge_record: Optional[Dict]    # 桥接记录
    coupler_output: float            # W_c
    stability_score: float           # f_S
```

### 2.4 复归崩溃恢复器 (BBCR Fu Return)

#### 算法签名

```python
def fu_return(
    B_norm: float,          # 坤守残差范数
    f_S: float,             # 乾进稳定度
    lambda_state: str,      # λ 状态
    B_c: float = 0.85,      # 崩溃阈值
    eps: float = 0.0,       # 稳定性阈值
    node_history: List[MemoryRecord],  # 历史节点
    max_rollback: int = 5   # 最大回退步数
) -> FuReturnResult:
```

#### 算法状态机

```
┌─────────────────────────────────────────────────────────────┐
│                    复归状态机 (Fu Return FSM)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 检查条件: norm(B) ≥ B_c OR f(S) < eps OR            │   │
│  │          lambda_state == "chaotic"                   │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │ False                              │
│                       ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 正常退出: 返回 NORMAL                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                       │ True                               │
│                       ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Phase 1: COLLAPSE                                   │   │
│  │   - 记录崩溃点信息                                    │   │
│  │   - 保存当前状态快照 (S_t, dB)                       │   │
│  │   - 标记所有 ACTIVE 原子为 DEFERRED                  │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Phase 2: RESET                                      │   │
│  │   - 回溯: 在 history 中找到最近 convergent 节点     │   │
│  │   - rollback_count ≤ max_rollback                    │   │
│  │   - S_anchor = 回溯节点的嵌入状态                     │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                    │
│                       ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Phase 3: REBIRTH                                    │   │
│  │   - S_next = (S_anchor + G) / 2                     │   │
│  │     （锚点状态与目标状态的插值，β=0.5)               │   │
│  │   - 验证: ΔS(S_next, G) 是否在 SAFE 区             │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                    │
│          ┌────────────┼────────────┐                       │
│          ▼            ▼            ▼                       │
│     ┌─────────┐ ┌─────────┐ ┌─────────┐                   │
│     │ 重生成功 │ │ 重生失败 │ │ 需用户  │                   │
│     │ RETURN  │ │ RETURN  │ │ 确认    │                   │
│     │ REBIRTH │ │ FAILURE │ │ RETURN  │                   │
│     └─────────┘ └─────────┘ └─────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### λ 状态机

```python
def compute_lambda(
    delta_s_t: float,       # 当前 ΔS
    delta_s_t_minus_1: float,  # 前一步 ΔS
    history: List[float],   # ΔS 历史
    anchors_stable: bool    # 锚点是否稳定
) -> str:
    """
    计算 λ (李雅普诺夫指数) 状态。

    Returns: "convergent" | "recursive" | "divergent" | "chaotic"
    """
    Delta = delta_s_t - delta_s_t_minus_1
    window = min(len(history), 5)
    E_res = np.mean(history[-window:]) if history else 0.0

    if Delta <= -0.02 and (len(history) < 2 or history[-1] >= history[-2] if len(history)>=2 else True):
        # Delta 显著为负 且 共振非增
        return "convergent"

    elif abs(Delta) < 0.02 and _is_flat(history, window):
        # Delta 接近零 且 共振平坦
        return "recursive"

    elif -0.02 < Delta <= 0.04 and _is_oscillating(history, window):
        # Delta 在小正区间 且 震荡
        return "divergent"

    elif Delta > 0.04 or not anchors_stable:
        # Delta 大幅增大 或 锚点冲突
        return "chaotic"

    else:
        return "recursive"  # 兜底
```

#### 数据结构

```python
@dataclass
class FuReturnResult:
    action_taken: str        # "NORMAL" | "COLLAPSE" | "REBIRTH" | "FAILURE" | "USER_CONFIRM"
    rollback_count: int      # 回退步数
    anchor_state: np.ndarray # 锚点状态
    new_state: np.ndarray    # 重生后状态
    recovery_delta_s: float  # 重生后的 ΔS
    failure_reason: Optional[str]
```

### 2.5 巽调注意力调制器 (BBAM Xun Tune)

#### 算法签名

```python
def xun_tune(
    attention_scores: np.ndarray,   # 原始注意力分数 [batch, seq_len]
    gamma: float = 0.618,           # 调制因子 (太极黄金比例)
    W_c: float = 0.0,               # 耦合器输出
    k_c: float = 0.25,              # 耦合灵敏度
    alpha_ref: str = "uniform",     # 参考注意力模式
    alpha_blend_range: Tuple[float, float] = (0.35, 0.65)
) -> XunTuneResult:
```

#### 算法流程

```
Algorithm: xun_tune
Input: attention_scores, gamma, W_c, k_c, alpha_ref, alpha_blend_range
Output: modulated_attention, gate_factor, alpha_mono

1.  COMPUTE attention statistics:
    a_raw = attention_scores
    μ_a = mean(a_raw)                  # 注意力均值
    σ_a = std(a_raw)                   # 注意力标准差

2.  COMPUTE gate modulation factor:
    gate_factor = exp(-gamma * σ_a)    # 方差门控
    # 高方差 → 门控因子小 → 平滑注意力
    # 低方差 → 门控因子大 → 保持原样

3.  MODULATE attention:
    a_hat = a_raw * gate_factor        # 逐元素乘

4.  COMPUTE α_mono (注意力单调解):
    # 耦合器驱动的 α_blend
    alpha_blend = 0.50 + k_c * tanh(W_c)
    alpha_blend = clip(alpha_blend, alpha_blend_range[0], alpha_blend_range[1])

    # 混合
    IF alpha_ref == "uniform":
        a_ref = ones_like(a_hat) / len(a_hat)  # 均匀注意力
    a_final = alpha_blend * a_hat + (1 - alpha_blend) * a_ref

5.  NORMALIZE:
    a_final = softmax(a_final)         # 确保总和为 1

6.  RETURN (a_final, gate_factor, alpha_blend)
```

#### γ 自动调节策略

实现一个辅助函数，根据当前系统状态自动调节 γ：

```python
def auto_gamma(
    lambda_state: str,     # λ 状态
    delta_s: float,        # 阴阳距
    base_gamma: float = 0.618
) -> float:
    """
    根据系统状态自动调节 γ 值。

    调节规则:
    - δ (chaotic): γ ↑ 增加聚焦，压制噪声
    - convergent: γ 维持 base_gamma
    - divergent: γ ↓ 让注意力更多样化
    - ΔS 高: γ ↑ 聚焦目标
    """
    adjustments = {
        "chaotic": +0.2,        # γ = 0.818: 强聚焦
        "convergent": +0.0,     # γ = 0.618: 平衡态
        "divergent": -0.1,      # γ = 0.518: 允许多样性
        "recursive": +0.05      # γ = 0.668: 轻微聚焦跳出循环
    }

    gamma = base_gamma + adjustments.get(lambda_state, 0.0)

    # ΔS 高时额外增加聚焦
    if delta_s > 0.60:
        gamma += 0.1

    return clip(gamma, 0.2, 1.2)
```

#### 数据结构

```python
@dataclass
class XunTuneResult:
    modulated_attention: np.ndarray    # 调制后注意力
    gate_factor: float                  # 方差门控因子
    alpha_blend: float                  # 混合因子
    attention_std: float                # 原注意力标准差
    gamma_used: float                   # 使用的 γ 值
```

---

## 3. 系统架构

### 3.1 模块调用流程图

```
用户请求 (自然语言)
    │
    ▼
┌────────────────────────────────────────────────────────────────┐
│                   北辰编译器 (Polaris)                          │
│  步骤 1: GOAL_COMPILATION (目标编译)                          │
│  步骤 2: TASK_GRAPH (构建任务依赖图)                          │
│  步骤 3: ATOM_TABLE (创建原子任务表)                          │
│  步骤 4: EXECUTION_TOKEN_BOARD (令牌分配)                     │
│  步骤 5: ROUND_LOCK (锁定执行原子)                            │
└────────────────────────────────────────┬───────────────────────┘
                                         │
                                         ▼
┌────────────────────────────────────────────────────────────────┐
│                   太极力学引擎 (Taiji Engine)                   │
│                                                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │ 阴阳距    │    │ 坤守     │    │ 乾进     │    │ 巽调     │ │
│  │ ΔS Calc  │◄───┤ BBMC    │◄───┤ BBPF    │◄───┤ BBAM    │ │
│  │          │    │ 残差修正  │    │ 多路径   │    │ 注意力调制│ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│       │               │               │               │       │
│       ▼               ▼               ▼               ▼       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              复归 BBCR (崩溃恢复)                      │    │
│  │  当 norm(B) ≥ B_c 或 f(S) < ε 或 λ == chaotic 时触发 │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              语义树 (Semantic Tree)                     │    │
│  │  MemoryRecord: {topic, module, ΔS, λ, insight, t}     │    │
│  │  ΔS > 0.60强制记录 || ΔS < 0.35典范记录                │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────┬───────────────────────┘
                                         │
                                         ▼
┌────────────────────────────────────────────────────────────────┐
│                下游泄漏审计 + 回合结果                        │
│  DOWNSTREAM_LEAK_AUDIT: 检查输出与预期类型是否匹配           │
└────────────────────────────────────────────────────────────────┘
```

### 3.2 数据流

```
用户输入
    │
    ▼
[嵌入层] → I_embedding
    │
    ▼
[目标构建] → G_embedding (从用户请求+系统规则+可信上下文推导)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 主循环 (每步推理迭代):                                          │
│                                                                 │
│  1. ΔS = calculate_delta_s(I, G)    ← 张力度量                  │
│                                                                 │
│  2. BBMC_result = kun_guard(I, G)   ← 残差修正 + 崩溃检测       │
│     IF BBMC_result.hazard == "COLLAPSE":                        │
│         BBCR_result = fu_return(...)  ← 触发崩溃恢复            │
│         I = BBCR_result.new_state                                │
│         CONTINUE                                                 │
│                                                                 │
│  3. λ = compute_lambda(ΔS_t, ΔS_t-1, history) ← 稳定性评估     │
│     IF λ == "chaotic": 同上触发复归                             │
│                                                                 │
│  4. 候选路径 = qian_advance(I, G, ...)  ← 多路径探索            │
│     IF bridge_enabled: 启用乾进桥接                             │
│                                                                 │
│  5. 注意力调制 = xun_tune(attention, γ自动调节)  ← 注意力平衡  │
│                                                                 │
│  6. 更新语义树: 根据 ΔS 和 λ 决定是否记录节点                  │
│                                                                 │
│  7. 北辰审计: 运行 DOWNSTREAM_LEAK_AUDIT                        │
│     IF Leak_Detected: 回合失败，移除泄漏内容                     │
│                                                                 │
│  8. 推进: I = 选择的最优候选路径状态                             │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
[输出生成] (仅当所有检查通过)
```

### 3.3 核心数据流

```python
@dataclass
class TaijiEngineState:
    # 当前状态
    I_current: np.ndarray           # 当前嵌入
    G_target: np.ndarray            # 目标嵌入
    context_tokens: int             # 上下文 token 数

    # 历史
    delta_s_history: List[float]    # ΔS 历史
    lambda_history: List[str]       # λ 历史
    node_history: List[MemoryRecord]  # 语义节点历史

    # 北辰编译器
    task_graph: Optional[Dict]      # 任务图
    active_atom: Optional[str]      # 当前活性原子
    round_id: int                   # 回合 ID

    # 参数
    B_c: float = 0.85               # 崩溃阈值
    gamma: float = 0.618            # 调制因子
    theta_c: float = 0.75           # 耦合阈值
    zeta_min: float = 0.10          # 最小推进
    k_c: float = 0.25               # 耦合灵敏度
```

---

## 4. 接口定义

### 4.1 统一引擎接口

```python
class TaijiVerifyEngine:
    """太极 Verify 引擎主接口"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化引擎
        默认配置见 Flagship Defaults
        """
        self.config = {
            "B_c": 0.85,
            "gamma": 0.618,
            "theta_c": 0.75,
            "zeta_min": 0.10,
            "alpha_blend": 0.50,
            "m": 0,
            "c": 1,
            "omega": 1.0,
            "phi_delta": 0.15,
            "epsilon": 0.0,
            "k_c": 0.25,
        }
        self.state = TaijiEngineState(...)

    def step(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        单步推理迭代。
        返回包含 ΔS, λ, 动作建议, 输出 的完整状态包。
        """
        ...

    def compile_goal(self, user_input: str) -> Dict:
        """
        北辰编译器: 编译用户目标为可执行任务图。
        Returns: {goal_compilation, task_graph, atom_table}
        """
        ...

    def audit_leak(self, output: str, expected_kind: str) -> bool:
        """
        下游泄漏审计。
        Returns: True 如果有泄漏，False 如果通过。
        """
        ...

    def export_semantic_tree(self, format: str = "txt") -> str:
        """
        导出语义树。
        """
        ...

    def get_metrics(self) -> Dict:
        """
        获取当前指标: ΔS, λ, f_S, norm_B, active_atom 等。
        """
        ...
```

### 4.2 回调接口 (供集成方实现)

```python
class EmbeddingProvider:
    """嵌入向量提供者接口"""
    def embed(self, text: str) -> np.ndarray: ...

class LLMProvider:
    """LLM 提供者接口"""
    def generate(self, prompt: str, attention_hook: Optional[Callable] = None) -> str: ...

class MemoryStore:
    """语义树持久化接口"""
    def save(self, record: MemoryRecord): ...
    def search(self, query_vector: np.ndarray, k: int) -> List[MemoryRecord]: ...
    def get_history(self) -> List[MemoryRecord]: ...
```

---

## 5. 实现路线图

### 5.1 阶段划分

| 阶段 | 名称 | 内容 | 交付物 | 预计工作量 |
|------|------|------|--------|-----------|
| P0 | 核心度量 | ΔS 计算器 + λ 状态机 + 闸区判断 | Python 模块 (100-150 行) | 1-2 天 |
| P0 | 北辰编译器规则引擎 | 目标编译 + 任务图 + 原子表 + 令牌板 | Python DSL/Prompt 模板 (200-300 行) | 2-3 天 |
| P1 | 坤守实现 | BBMC 残差计算 + 最小化 + 危险检测 | Python 模块 (150-200 行) | 1-2 天 |
| P1 | 巽调实现 | BBAM 方差门控 + alpha_blend + 自动 γ | Python 模块 (100-150 行) | 1 天 |
| P2 | 复归实现 | BBCR 状态机 + 崩溃检测 + 回退 + 重生 | Python 状态机 (200-300 行) | 2-3 天 |
| P2 | 语义树持久化 | 节点存储 + 检索 + 导出 | 轻量级数据层 (150-200 行) | 1-2 天 |
| P3 | 乾进实现 | BBPF 多路径扰动 + 耦合器 + 桥接 | Python 模块 (200-250 行) | 2-3 天 |
| P3 | 下游泄漏审计 | 输出类型校验 + 泄漏检测 + 洁净修复 | Python 规则引擎 (100-150 行) | 1 天 |
| P4 | 集成测试 | 16 种失败模式的模拟验证 + 政务场景 | 测试套件 + 基准脚本 | 3-5 天 |

### 5.2 优先实现策略

**建议首发**: 阴阳距 ΔS + 北辰编译器
- 这两个模块独立性强、成本低、可视化效果好
- 可实现"输入 → 度量 → 编译 → 约束执行"的最小可行管道
- 为后续坤守/巽调提供度量和执行基础

### 5.3 基准验证指标

以 WFGY v1.0 报告的内部测试为参照:

| 指标 | 基线 (传统 LLM) | 目标 (太极 Verify) | 提升幅度 |
|------|-----------------|-------------------|----------|
| 推理准确率 | 46.7% | 57.2%+ | ≥+22.4% |
| 链有效性 | 34.1% | 48.5%+ | ≥+42.1% |
| 稳定性 (1/σ) | 1.0x | 3.6x | ≥3.6x |
| ΔS 合格率 | 未测量 | ≥0.90 | - |
| 覆盖率 | 未测量 | ≥0.70 | - |

### 5.4 政务场景适配注意事项

| 场景 | 特殊要求 | 参数调整建议 |
|------|----------|-------------|
| 政策问答 | 高一致性、低创造性 | B_c=0.80, gamma=0.70, k_paths=2 |
| 政策解读 | 准确性+可读性 | B_c=0.85, gamma=0.618, k_paths=3 |
| 窗口咨询 | 高可用性、快恢复 | B_c=0.75, eps=0.05, max_rollback=3 |
| 舆情摘要 | 多样性+忠实度 | gamma=0.50, k_paths=5, alpha_blend=0.45 |
| 内部知识库 | 精确检索、严格对齐 | B_c=0.90, gamma=0.80, anchors_weight=(0.6,0.3,0.1) |

---

## 附录 A: 参数默认值速查

| 符号 | 默认值 | 所属模块 | 含义 |
|------|--------|----------|------|
| B_c | 0.85 | BBCR, BBMC | 崩溃阈值 |
| γ | 0.618 | BBAM | 调制因子（太极黄金比例） |
| θ_c | 0.75 | BBPF | 耦合器裁剪上限 |
| ζ_min | 0.10 | BBPF | 最小推进 |
| α_ref | uniform | BBAM | 参考注意力模式 |
| m | 0 | BBMC | 匹配系数（默认为 cos(I,G)） |
| c | 1 | BBMC | 上下文因子 |
| ω | 1.0 | BBPF | 推进指数 |
| φ_δ | 0.15 | BBPF | 翻转幅度 |
| ε | 0.0 | BBCR | 稳定性阈值偏置 |
| k_c | 0.25 | BBAM | 耦合灵敏度 |
| h | 0.02 | BBPF | 锚点翻转迟滞窗口 |

## 附录 B: 16 种失败模式 → 检测器映射

| 失败模式编号 | 检测器 | 主要指标 | 触发模块 |
|-------------|--------|----------|----------|
| No.1 | ΔS > 0.45 | ΔS | 坤守 BBMC |
| No.2 | λ == divergent + ΔS 不降 | λ | 复归 BBCR |
| No.3 | ΔS 趋势线 > 0.05/步 | ΔS 序列 | 乾进 BBPF |
| No.4 | ΔS < 0.20 + 低置信度 | ΔS + 置信度 | 坤守 BBMC |
| No.5 | sim_est < cos(I,G) 显著 | 锚点扩展 | 阴阳距 ΔS |
| No.6 | norm(B) ≥ B_c | 残差范数 | 复归 BBCR |
| No.7 | 语义树检索为空 | 节点存在性 | 语义树 |
| No.8 | λ == recursive 持续 3 步以上 | λ 历史 | 北辰审计 |
| No.9 | σ(a) > 0.5 | 注意力方差 | 巽调 BBAM |
| No.10 | k_paths < 2 | 路径计数 | 乾进 BBPF |
| No.11 | λ == chaotic + 符号模式 | λ + 模式 | 复归 BBCR |
| No.12 | λ == recursive 循环 | λ 循环 | 复归 BBCR |
| No.13 | 多智能体 ΔS 冲突 | 跨智能体 ΔS | 北辰任务图 |
| No.14 | BLOCKED 原子过多 | 原子状态 | 北辰编译器 |
| No.15 | 依赖图有环 | 图拓扑 | 北辰编译器 |
| No.16 | 首次 ΔS == 1.0 | ΔS | 阴阳距 ΔS |

---

*设计草案结束 · 版本 0.1*
