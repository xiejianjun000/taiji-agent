# Hermes Agent 架构分析报告

> 分析日期：2026-05-14
> 代码仓库：[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
> 分析范围：技能系统、进化机制、多租户、Harness 集成、记忆系统

---

## 目录

1. [技能系统：Hermes SKILL.md vs OpenClaw SKILL.md 标准](#1-技能系统hermes-skillmd-vs-openclaw-skillmd-标准)
2. [三级进化机制设计（evolution/ 模块）](#2-三级进化机制设计evolution-模块)
3. [多租户数据隔离设计（multiTenant/ 模块）](#3-多租户数据隔离设计multitenant-模块)
4. [Hermes 与 Harness 的 TS/Python 互操作方案比较](#4-hermes-与-harness-的-tspython-互操作方案比较)
5. [记忆系统：8 种后端对比与推荐方案](#5-记忆系统8-种后端对比与推荐方案)

---

## 1. 技能系统：Hermes SKILL.md vs OpenClaw SKILL.md 标准

### 1.1 Hermes 技能系统架构

Hermes 的技能系统是**文件驱动的**，每个技能是一个包含 `SKILL.md` 文件的目录，其核心架构如下：

```
skills/                          # 内置技能（25+ 类别，532 个文件）
├── category-name/               # 技能类别目录
│   ├── DESCRIPTION.md           # 类别描述
│   └── skill-name/              # 单个技能目录
│       ├── SKILL.md             # 技能定义文件（核心）
│       ├── references/          # 参考文档
│       ├── templates/           # 模板文件
│       ├── scripts/             # 辅助脚本
│       └── assets/              # 静态资源
optional-skills/                 # 可选技能（默认不激活）
```

**关键架构组件：**

| 组件 | 文件 | 职责 |
|------|------|------|
| SKILL.md 解析 | `agent/skill_utils.py` | YAML frontmatter 解析、平台匹配、禁用列表 |
| 技能预处理 | `agent/skill_preprocessing.py` | 模板变量 `${...}` 替换、内联 shell 执行 `!`cmd`` |
| 提示词组装 | `agent/prompt_builder.py` | 扫描所有技能目录、组装技能索引到 system prompt |
| 技能管理工具 | `tools/skill_manager_tool.py` | Agent 创建/编辑/删除技能的工具接口 |
| 技能使用追踪 | `tools/skill_usage.py` | 技能调用频率和效果追踪 |
| 技能 Hub | `tools/skills_hub.py` | 从远程 Hub 安装/更新技能 |
| 安全扫描 | `tools/skills_guard.py` | 扫描技能脚本中的安全风险 |

### 1.2 SKILL.md Frontmatter 格式

Hermes SKILL.md 使用 YAML frontmatter（markdown 头部 `---` 块）：

```yaml
---
name: subagent-driven-development
description: "Execute plans via delegate_task subagents (2-stage review)."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]          # 平台限制
metadata:
  hermes:
    tags: [delegation, subagent, workflow]  # 标签分类
    related_skills: [writing-plans, ...]     # 关联技能
    config:                                  # 声明所需配置
      - key: wiki.path
        description: Wiki directory path
        default: "~/wiki"
    fallback_for_toolsets: [...]              # 条件激活
    requires_toolsets: [...]                  # 前置工具集
---
```

### 1.3 OpenClaw 标准对比

Hermes 的 README 明确声明 **[agentskills.io](https://agentskills.io) 兼容**，且提供了 `hermes claw migrate` 迁移命令。两者核心差异：

| 维度 | Hermes SKILL.md | OpenClaw SKILL.md 标准 |
|------|----------------|----------------------|
| **格式** | YAML frontmatter + Markdown body | YAML frontmatter + Markdown body |
| **文件命名** | `SKILL.md`（大小写敏感） | `SKILL.md`（标准） |
| **frontmatter 字段** | `name`, `description`, `version`, `author`, `license`, `platforms` | 近似的核心字段 |
| **标签系统** | `metadata.hermes.tags`（嵌套） | 顶层 `tags`（扁平） |
| **配置声明** | `metadata.hermes.config`（嵌套） | 无标准配置声明 |
| **平台过滤** | `platforms: [linux, macos, windows]` | 无标准平台过滤 |
| **关联技能** | `metadata.hermes.related_skills` | 无标准关联机制 |
| **条件激活** | `fallback_for_toolsets`, `requires_toolsets` | 无 |
| **模板变量** | `${HERMES_SKILL_DIR}`, `${HERMES_SESSION_ID}` | 无 |
| **内联 shell** | `` !`date +%Y-%m-%d` `` | 无 |
| **外部技能目录** | 支持 `skills.external_dirs` 配置 | 无 |
| **安全扫描** | `skills_guard.py` 自动扫描 | 无 |
| **技能创建** | Agent 通过工具自主创建 | 手动创建 |
| **Hub 安装** | `skills_hub.py` | Hub 安装 |

### 1.4 核心差异总结

| 特性 | Hermes | OpenClaw 标准 | 影响 |
|------|--------|--------------|------|
| **条件激活** | 支持工具集依赖 | 无 | 技能可声明前置条件 |
| **配置注入** | 支持声明式配置 | 无 | 无需硬编码 API key |
| **平台感知** | 跨平台过滤 | 无 | 限制平台特定技能 |
| **安全体系** | 内置扫描 | 无 | 防止恶意技能 |
| **元数据深度** | 嵌套命名空间 | 扁平 | 避免字段冲突 |
| **agent 自主性** | Agent 可自主创建 | 需手动 | 自我改进循环 |

**兼容性结论**：Hermes SKILL.md 是 OpenClaw SKILL.md 标准的**超集**。Hermes 兼容 OpenClaw 的基本 SKILL.md 格式（`name`、`description`），并在此基础上添加了大量 Hermes 特有字段（放在 `metadata.hermes` 命名空间下避免冲突）。从 OpenClaw 迁移理论上只需复制 `SKILL.md` 文件，额外功能可逐步启用。

---

## 2. 三级进化机制设计（evolution/ 模块）

### 2.1 背景

Hermes Agent 当前有**初步的自我改进能力**：
- Agent 可通过 `skill_manager_tool` 自主创建技能
- 技能通过 `skill_usage.py` 追踪使用频率
- 周期性 nudges 提醒 Agent 持久化知识
- `curator.py` / `curator_backup.py` 负责记忆整理

但**没有结构化的三级进化（个人 → 部门 → 系统）机制**。以下是从零设计的完整方案。

### 2.2 模块结构

```
hermes-agent/evolution/
├── __init__.py                          # 包入口
├── base.py                              # 进化基类
├── core/                                # 核心引擎
│   ├── __init__.py
│   ├── evolution_engine.py              # 进化引擎主循环
│   ├── evolution_state.py               # 进化状态管理（SQLite）
│   ├── scored_selector.py               # 择优选择算法
│   └── mutation_operator.py             # 变异算子（策略调整）
│
├── individual/                          # 个人级进化（L1）
│   ├── __init__.py
│   ├── skill_optimizer.py              # 技能优化（合并/拆分/重写）
│   ├── prompt_tuner.py                 # 提示词参数调优
│   ├── workflow_learner.py             # 工作流模式学习
│   └── feedback_collector.py           # 隐式反馈收集
│
├── department/                          # 部门级进化（L2）
│   ├── __init__.py
│   ├── knowledge_graph.py              # 跨技能知识图谱
│   ├── capability_discovery.py         # 能力盲点发现
│   ├── coordination_optimizer.py       # 协作流程优化
│   └── training_generator.py           # 训练数据生成
│
├── system/                              # 系统级进化（L3）
│   ├── __init__.py
│   ├── architecture_evolver.py         # 架构自我演化
│   ├── meta_policy.py                  # 元策略（进化策略的进化）
│   ├── population_health.py           # 群体健康度监控
│   └── curriculum_designer.py          # 课程表设计
│
├── metrics/                             # 评估体系
│   ├── __init__.py
│   ├── skill_quality.py                # 技能质量评估
│   ├── efficiency_score.py             # 效率评分
│   └── diversity_score.py             # 多样性评分
│
└── storage/                             # 持久化
    ├── __init__.py
    ├── evolution_db.py                 # 进化记录数据库
    └── artifact_store.py               # 制品存储
```

### 2.3 核心算法设计

#### 2.3.1 进化引擎主循环（`evolution_engine.py`）

```python
class EvolutionEngine:
    """
    三级进化引擎主循环。

    算法流程：
    1. COLLECT 阶段：收集所有可观测指标
    2. EVALUATE 阶段：三级评估（技能质量 → 协作效率 → 系统健康度）
    3. SELECT 阶段：择优选择候选个体
    4. MUTATE 阶段：生成变异（策略调整/技能优化）
    5. VALIDATE 阶段：验证变异效果
    6. PROMOTE 阶段：将成功变异提升到更高级别
    """

    def __init__(self, config: EvolutionConfig):
        self.config = config
        self.state = EvolutionState()  # SQLite 持久化
        self.db = EvolutionDB()

    async def run_cycle(self, context: EvolutionContext) -> EvolutionReport:
        # Phase 1: Collect metrics from all levels
        metrics = await self._collect_all_metrics(context)

        # Phase 2: Evaluate fitness
        scores = self._evaluate_fitness(metrics)

        # Phase 3: Select candidates for mutation
        candidates = self._select_candidates(scores)

        # Phase 4: Apply mutations
        mutations = await self._apply_mutations(candidates, context)

        # Phase 5: Validate mutations
        validated = await self._validate_mutations(mutations)

        # Phase 6: Promote successful mutations
        promotions = self._promote_if_warranted(validated)

        # Record and report
        return self._finalize_cycle(metrics, scores, promotions)
```

#### 2.3.2 三级评估算法

```python
def _evaluate_fitness(self, metrics: AllMetrics) -> FitnessScores:
    """三级适应性评分计算。"""

    # L1: Individual fitness（个人级：技能完成度、用户满意度）
    individual_score = (
        w1 * metrics.skill_completion_rate  # 技能完成率
        + w2 * metrics.user_satisfaction     # 用户满意度（隐式）
        + w3 * metrics.efficiency_gain       # 效率 gain
        - w4 * metrics.error_rate            # 错误率惩罚
    )

    # L2: Department fitness（部门级：技能互补性、协作效率）
    department_score = (
        w5 * metrics.coverage_gap_reduction   # 能力覆盖缺口缩小
        + w6 * metrics.coordination_overhead  # 协调开销降低
        + w7 * metrics.knowledge_transfer     # 知识传递效果
    )

    # L3: System fitness（系统级：整体健康度、多样性）
    system_score = (
        w8 * metrics.population_diversity     # 技能多样性
        + w9 * metrics.adaptation_speed       # 适应新任务速度
        + w10 * metrics.anti_fragility        # 反脆弱性（扰动下的恢复力）
        - w11 * metrics.bloat_penalty         # 冗余技能惩罚
    )

    return FitnessScores(
        individual=individual_score,
        department=department_score,
        system=system_score,
        composite=(
            α * individual_score
            + β * department_score
            + γ * system_score
        )
    )
```

#### 2.3.3 择优选择算法（`scored_selector.py`）

使用**多目标 Pareto 优化** + **锦标赛选择**：

```python
class ScoredSelector:
    def select(self, population: List[Skill], scores: FitnessScores,
               strategy: SelectionStrategy) -> List[Skill]:
        if strategy == SelectionStrategy.TOURNAMENT:
            return self._tournament_select(population, scores, k=3)
        elif strategy == SelectionStrategy.PARETO:
            return self._pareto_front_select(population, scores)
        elif strategy == SelectionStrategy.ROULETTE:
            return self._roulette_select(population, scores)

    def _tournament_select(self, pop, scores, k):
        """锦标赛选择：随机取 k 个，选最优。"""
        selected = []
        for _ in range(len(pop) // 2):
            tournament = random.sample(list(enumerate(pop)), k)
            winner = max(tournament, key=lambda x: scores[x[0]])
            selected.append(winner[1])
        return selected

    def _pareto_front_select(self, pop, scores):
        """Pareto 前沿选择：保留在所有维度上非支配的解。"""
        # Pareto 支配判断
        dominated = [False] * len(pop)
        for i in range(len(pop)):
            for j in range(len(pop)):
                if i != j and self._dominates(scores[j], scores[i]):
                    dominated[i] = True
                    break
        return [s for i, s in enumerate(pop) if not dominated[i]]
```

#### 2.3.4 变异算子（`mutation_operator.py`）

```python
class MutationOperator:
    """策略变异算子，控制进化探索的广度。"""

    def mutate(self, skill: Skill, level: EvolutionLevel) -> Skill:
        if level == EvolutionLevel.INDIVIDUAL:
            return self._individual_mutate(skill)
        elif level == EvolutionLevel.DEPARTMENT:
            return self._department_mutate(skill)
        else:
            return self._system_mutate(skill)

    def _individual_mutate(self, skill: Skill) -> Skill:
        """个人级变异：参数微调、步骤优化、错误修复。"""
        mutations = [
            self._tune_parameters,
            self._optimize_steps,
            self._fix_known_errors,
            self._add_variants,
        ]
        return random.choice(mutations)(skill)

    def _department_mutate(self, skill: Skill) -> Skill:
        """部门级变异：技能合并/拆分、知识注入、协作改进。"""
        mutations = [
            self._merge_with_complementary,
            self._split_into_subskills,
            self._inject_knowledge_graph,
            self._add_coordination_hooks,
        ]
        return random.choice(mutations)(skill)

    def _system_mutate(self, skill: Skill) -> Skill:
        """系统级变异：架构级变更、新范式引入、抽象层次提升。"""
        mutations = [
            self._abstract_generalize,
            self._cross_pollinate,
            self._introduce_meta_pattern,
            self._rewrite_architecture,
        ]
        return random.choice(mutations)(skill)
```

#### 2.3.5 自我进化终止条件（重要设计特性）

```python
def should_stop_evolution(self, history: List[CycleResult]) -> bool:
    """判断进化是否应暂停（防止过度进化/振荡）。"""
    recent = history[-5:]

    # 1. 收敛条件：最近 N 轮改进小于阈值
    if all(r.improvement < CONVERGENCE_THRESHOLD for r in recent):
        return True

    # 2. 振荡检测：得分来回跳
    if self._is_oscillating(recent):
        return True  # 暂停并记录，等待外部新信号

    # 3. 负收益检测：进化成本 > 收益
    evolution_cost = sum(r.computation_cost for r in recent)
    total_benefit = sum(r.improvement for r in recent)
    if evolution_cost > total_benefit * EVOLUTION_COST_RATIO:
        return True

    return False
```

### 2.4 与现有 Hermes 模块的集成点

| 现有模块 | 集成方式 |
|----------|---------|
| `skill_manager_tool.py` | 扩展 `edit` 动作为变异算子的执行接口 |
| `skill_usage.py` | 提供 L1 适应性评分数据 |
| `skill_utils.py` | 复用 YAML frontmatter 解析 |
| `curator.py` | 将 curate 决策纳入进化反馈 |
| `hermes_state.py` | 共用 SessionDB 存储进化状态 |
| `gateway/` | 通过平台渠道收集用户隐式反馈 |

### 2.5 综合说明

本设计**不依赖 evolution/ 模块的原位存在**，而是将其设计为 Hermes 的**可选增强模块**，通过标准的 `MemoryProvider` 风格的注册接口（`EvolutionProvider`）来提供"自我进化"能力。核心思路是：

- **L1 个人进化**：复用现有 `skill_manager_tool`，增加自动变异与验证
- **L2 部门进化**：基于 `skill_usage.py` + 知识图谱，优化协作效率
- **L3 系统进化**：新增元策略调度器，控制全局进化节奏

---

## 3. 多租户数据隔离设计（multiTenant/ 模块）

### 3.1 背景

Hermes Agent 当前**没有多租户支持**。其数据存储策略是：

- `~/.hermes/config.yaml`：全局配置（单用户）
- `~/.hermes/.env`：API keys
- `~/.hermes/sessions/`：SQLite 会话存储
- `~/.hermes/skills/`：用户技能目录

Hermes 支持 `-p`/`--profile` 参数实现有限的 profile 隔离，但不是完整的多租户。以下设计可同时处理 S3、阿里云 OSS、MinIO 等多种对象存储后端。

### 3.2 数据模型设计

#### 3.2.1 租户模型

```python
# multiTenant/models/tenant.py
@dataclass
class Tenant:
    """租户核心模型。"""
    tenant_id: str                    # 租户 ID（UUID）
    name: str                         # 租户名称
    tier: TenantTier                  # 层级：free | pro | enterprise
    status: TenantStatus              # 状态：active | suspended | deleted
    storage_backend: StorageBackend   # 存储后端：s3 | oss | minio | local
    storage_config: Dict[str, Any]    # 存储配置（bucket/region/endpoint）
    created_at: datetime
    config_overrides: Dict[str, Any]  # 配置覆盖
    allowed_providers: List[str]      # 允许的 LLM 提供商
    rate_limits: RateLimitConfig      # 速率限制
```

#### 3.2.2 存储后端抽象

```python
# multiTenant/storage/backends.py
class StorageBackend(ABC):
    """对象存储抽象层，支持 S3/OSS/MinIO/Local。"""

    @abstractmethod
    async def read_blob(self, tenant_id: str, key: str) -> bytes: ...
    @abstractmethod
    async def write_blob(self, tenant_id: str, key: str, data: bytes) -> str: ...
    @abstractmethod
    async def delete_blob(self, tenant_id: str, key: str) -> None: ...
    @abstractmethod
    async def list_blobs(self, tenant_id: str, prefix: str) -> List[str]: ...
    @abstractmethod
    async def ensure_tenant_bucket(self, tenant_id: str) -> str: ...


class S3Backend(StorageBackend):
    """AWS S3 实现。每个租户一个 prefix 或 bucket。"""

    def __init__(self, config: S3Config):
        self.client = boto3.client(
            's3',
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
            region_name=config.region,
        )
        self.base_bucket = config.bucket

    async def read_blob(self, tenant_id: str, key: str) -> bytes:
        full_key = f"tenants/{tenant_id}/{key}"
        result = await self.client.get_object(Bucket=self.base_bucket, Key=full_key)
        return await result['Body'].read()

    async def ensure_tenant_bucket(self, tenant_id: str) -> str:
        """S3 按 prefix 隔离（或为每个租户创建独立 bucket）。"""
        # 验证 prefix 存在即可，无需创建实际 bucket
        return f"{self.base_bucket}/tenants/{tenant_id}"


class OSSBackend(StorageBackend):
    """阿里云 OSS 实现。"""

    def __init__(self, config: OSSConfig):
        import oss2
        self.auth = oss2.Auth(config.access_key, config.secret_key)
        self.bucket = oss2.Bucket(self.auth, config.endpoint, config.bucket)

    async def read_blob(self, tenant_id: str, key: str) -> bytes:
        full_key = f"tenants/{tenant_id}/{key}"
        result = self.bucket.get_object(full_key)
        return result.read()


class MinIOBackend(StorageBackend):
    """MinIO 实现（兼容 S3 API）。"""

    def __init__(self, config: MinIOConfig):
        from minio import Minio
        self.client = Minio(
            config.endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.use_ssl,
        )
        self.base_bucket = config.bucket

    async def read_blob(self, tenant_id: str, key: str) -> bytes:
        full_key = f"tenants/{tenant_id}/{key}"
        response = self.client.get_object(self.base_bucket, full_key)
        data = response.read()
        response.close()
        return data


class LocalBackend(StorageBackend):
    """本地文件系统实现（开发/单机场景）。"""

    def __init__(self, config: LocalConfig):
        self.base_path = Path(config.base_path)

    async def read_blob(self, tenant_id: str, key: str) -> bytes:
        path = self.base_path / tenant_id / key
        return path.read_bytes()

    async def write_blob(self, tenant_id: str, key: str, data: bytes) -> str:
        path = self.base_path / tenant_id / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)
```

#### 3.2.3 数据隔离方案

```python
# multiTenant/isolation/manager.py
class IsolationManager:
    """
    数据隔离管理器。

    隔离策略选择：
    - POOL: 共享存储池，按 Prefix/Tag 隔离（成本最优）
    - BUCKET: 每个租户独立 Bucket/Container（安全适中）
    - INSTANCE: 每个租户独立基础设施（安全最高）
    """

    def __init__(self, isolation_strategy: IsolationStrategy):
        self.strategy = isolation_strategy
        self.backends: Dict[StorageBackendType, StorageBackend] = {}

    async def get_tenant_storage(self, tenant: Tenant) -> TenantStorage:
        """获取租户的隔离存储句柄。"""
        backend = self._resolve_backend(tenant.storage_backend)

        if self.strategy == IsolationStrategy.POOL:
            # 共享存储 + prefix 隔离
            return PoolStorage(backend, tenant.tenant_id)

        elif self.strategy == IsolationStrategy.BUCKET:
            # 独立 bucket/container
            bucket = await backend.ensure_tenant_bucket(tenant.tenant_id)
            return BucketStorage(backend, bucket)

        elif self.strategy == IsolationStrategy.INSTANCE:
            # 完全隔离实例（不同数据库/进程）
            return InstanceStorage(tenant)
```

#### 3.2.4 数据分区矩阵

| 数据类型 | POOL 策略 | BUCKET 策略 | INSTANCE 策略 |
|----------|-----------|-------------|---------------|
| 会话数据 | `sessions/{tenant_id}/` | 独立 DB 中的表 | 独立 DB 实例 |
| 技能定义 | `skills/{tenant_id}/` | 独立 Bucket | 独立存储 |
| 记忆/状态 | `memories/{tenant_id}/` | 独立向量索引 | 独立向量 DB |
| 配置文件 | `configs/{tenant_id}/` | 独立配置文件 | 独立配置中心 |
| 日志 | `logs/{tenant_id}/` | 独立日志流 | 独立日志集群 |
| LLM API Keys | 加密存储 + 租户作用域 | 加密 + 租户隔离 | 独立密钥管理 |

#### 3.2.5 租户路由中间件

```python
# multiTenant/middleware.py
class TenantAwareMiddleware:
    """请求路由中间件：根据请求来源路由到正确的租户上下文。"""

    TENANT_HEADER = "X-Tenant-ID"
    TENANT_API_KEY_HEADER = "X-Tenant-API-Key"

    async def resolve_tenant(self, request: Request) -> Optional[Tenant]:
        # 方法1：Header 中指定租户 ID
        tenant_id = request.headers.get(self.TENANT_HEADER)
        if tenant_id:
            return await self._load_tenant(tenant_id)

        # 方法2：API Key 识别租户
        api_key = request.headers.get(self.TENANT_API_KEY_HEADER)
        if api_key:
            return await self._tenant_by_api_key(api_key)

        # 方法3：Gateway 平台用户映射
        platform_user = request.state.platform_user
        if platform_user:
            return await self._tenant_by_platform_user(platform_user)

        return None

    async def __call__(self, request: Request, call_next):
        tenant = await self.resolve_tenant(request)
        if tenant and tenant.status == TenantStatus.SUSPENDED:
            return Response(status_code=403, body="Tenant suspended")

        request.state.tenant = tenant
        context = TenantContext(tenant=tenant, isolation=self._get_isolation())
        with tenant_context(context):
            response = await call_next(request)
            response.headers["X-Tenant-ID"] = tenant.tenant_id
            return response
```

### 3.3 与现有 Hermes 架构的集成

```python
# 集成到 run_agent.py
class AIAgent:
    def __init__(self, ..., tenant: Optional[Tenant] = None):
        self.tenant = tenant
        if tenant:
            # 根据租户配置覆盖 Hermes 默认配置
            self._apply_tenant_config(tenant.config_overrides)
            # 使用租户隔离的存储
            self.storage = isolation_manager.get_tenant_storage(tenant)
            # 租户级速率限制
            self.rate_limiter = TenantRateLimiter(tenant.rate_limits)
```

### 3.4 多对象存储支持的统一配置

```yaml
# config.yaml 中的多租户配置示例
multitenant:
  enabled: true
  isolation_strategy: pool  # pool | bucket | instance

  storage:
    default_backend: s3
    backends:
      s3:
        type: s3
        bucket: hermes-agent-data
        region: us-east-1
        # credentials from env: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
      oss:
        type: oss
        bucket: hermes-agent-data
        endpoint: oss-cn-hangzhou.aliyuncs.com
        # credentials from env: OSS_ACCESS_KEY_ID, OSS_SECRET_ACCESS_KEY
      minio:
        type: minio
        endpoint: minio.example.com:9000
        bucket: hermes-agent-data
        use_ssl: true
        # credentials from env: MINIO_ACCESS_KEY, MINIO_SECRET_KEY
      local:
        type: local
        base_path: /var/hermes/data

  tenants:
    tenant-abc123:
      name: "企业A"
      tier: enterprise
      storage_backend: s3
      allowed_providers: [openai, anthropic]
      rate_limits:
        requests_per_minute: 100
        tokens_per_day: 10000000
```

---

## 4. Hermes 与 Harness 的 TS/Python 互操作方案比较

### 4.1 Hermes 的互操作方案

Hermes Agent 是**纯 Python** 实现，其与外部系统（包括 TypeScript/JavaScript）的通信依赖以下模式：

#### 4.1.1 ACP 协议（Agent Communication Protocol）

```
hermes-agent/acp_adapter/
├── __init__.py
├── __main__.py        # 入口
├── auth.py            # 认证
├── entry.py           # 端点注册
├── events.py          # 事件系统
├── permissions.py     # 权限
├── server.py          # ACP 服务器（基于 HTTP/SSE）
├── session.py         # 会话管理
└── tools.py           # 工具注册和服务
```

ACP 是 Hermes 对外暴露的标准协议，IDE 集成（VS Code、Zed、JetBrains）通过 ACP 与 Hermes 通信。ACP 基于 HTTP + Server-Sent Events，支持 JSON 序列化，不限制客户端语言。

#### 4.1.2 MCP 支持（Model Context Protocol）

```python
# tools/mcp_tool.py — MCP 客户端
# agent/transports/hermes_tools_mcp_server.py — MCP 服务端
```

Hermes 既是 MCP 客户端（调用外部 MCP Server），也是 MCP 服务端（对外暴露 Hermes 工具）。

#### 4.1.3 Gateway 平台适配器

每个平台（Telegram, Discord, Slack 等）通过 HTTP Webhook + JSON 与 Hermes Gateway 通信：
```
gateway/platforms/
├── telegram.py
├── discord.py
├── slack.py
├── whatsapp.py
├── feishu.py
├── ... (34 个平台适配器)
```

#### 4.1.4 Terminal 后端（环境执行）

```python
# tools/environments/ — 7 种终端后端
├── local.py           # 本地 shell
├── docker.py          # Docker 容器
├── ssh.py             # SSH 远程
├── modal.py           # Modal serverless
├── daytona.py         # Daytona
├── singularity.py     # Singularity 容器
└── vercel.py          # Vercel Sandbox
```

#### 4.1.5 Node.js 桥接

Hermes 内置 Node.js 依赖（见 `package.json`），通过子进程执行 Node.js 脚本：

```python
# ui-tui/ — Ink (React) 终端 UI
# 通过 tui_gateway/ JSON-RPC 与 Python 后端通信
```

### 4.2 Harness 的 TS/Python 互操作方案（对比）

| 维度 | Hermes Agent | Taiji Harness |
|------|-------------|---------------|
| **主语言** | Python（单一） | TypeScript + Python（双栈） |
| **通信协议** | ACP (HTTP/SSE) | gRPC + JSON-RPC |
| **进程模型** | 单一进程 + 子进程 | 双进程（TS worker + Python worker） |
| **技能格式** | SKILL.md（纯文本） | TypeScript 函数类 |
| **工具定义** | Python 函数 + 注册 | TypeScript 接口定义 |
| **记忆存储** | Python 实现 | 通过 gRPC 调用 |
| **LLM 调用点** | Python 直接调用 | TypeScript worker 调用 |
| **跨语言效率** | 低（子进程通信） | 高（gRPC 流式） |
| **IDE 集成** | ACP 协议 | LSP + VS Code 扩展 |
| **序列化** | JSON | Protocol Buffers |
| **流式支持** | SSE | gRPC streaming |

### 4.3 关键差异分析

#### 4.3.1 架构哲学差异

```
Hermes（Python 中心）：
┌─────────────────────┐
│  AIAgent (Python)   │
│  ┌───────────────┐  │
│  │ Skill MD      │◄─┤── SKILL.md 文件
│  │ Tool Registry │  │
│  │ Memory Mgr    │  │
│  └───────┬───────┘  │
│          │ ACP/MCP  │
│          ▼          │
│  ┌───────────────┐  │
│  │ TS UI (TUI)   │  │
│  │ JS Tools      │  │
│  └───────────────┘  │
└─────────────────────┘

Harness（TS/Python 双栈）：
┌──────────────────────────┐
│  AgentHarness            │
│  ┌────────┐ ┌─────────┐  │
│  │TS Agent├─┤Py Agent │  │
│  │Worker  │ │Worker   │  │
│  │(LLM,   │ │(Tools,  │  │
│  │ Skills)│ │ Memory) │  │
│  └───┬────┘ └────┬────┘  │
│      │   gRPC    │       │
│      └───────────┘       │
│  ┌─────────────────────┐  │
│  │ Shared Event Bus    │  │
│  │ Protocol Buffers    │  │
│  └─────────────────────┘  │
└──────────────────────────┘
```

#### 4.3.2 互操作模式对比

| 场景 | Hermes 方案 | Harness 方案 | 优劣 |
|------|------------|-------------|------|
| **LLM 调用 → 工具执行** | Python 完成全部 | TS 调用 LLM → gRPC 调用 Python 执行工具 | Harness 解耦更清晰 |
| **技能定义 → 执行** | 文件系统 + 嵌入提示词 | TypeScript 函数 + 编译验证 | Hermes 灵活，Harness 类型安全 |
| **跨语言数据传递** | JSON（子进程 stdin/stdout） | Protocol Buffers（gRPC 流） | Harness 效率更高 |
| **实时流式输出** | Python generator → SSE | gRPC Server-Side Streaming | Harness 更可靠 |
| **状态同步** | 锁文件 + 轮询 | gRPC bidirectional streaming | Harness 实时性更好 |
| **部署复杂度** | 低（纯 Python） | 中（双语言运行时） | Hermes 更简单 |

#### 4.3.3 推荐的混合方案

最优方案是结合两者优势：

```python
# 在 Hermes 中集成 Harness 式 gRPC 通信
# hermes-agent/agent/harness_bridge.py
class HermesHarnessBridge:
    """
    Hermes ↔ Harness 互操作桥接。

    Hermes 将关键数据（技能、记忆、工具结果）通过 gRPC
    暴露给 Harness 的 TypeScript Agent Worker。
    """

    def __init__(self, grpc_port: int = 50051):
        self.server = grpc.aio.server()
        self._register_hermes_services()

    def _register_hermes_services(self):
        # 注册 Hermes 服务
        add_HermesSkillServicer_to_server(
            HermesSkillServicer(self), self.server
        )
        add_HermesMemoryServicer_to_server(
            HermesMemoryServicer(self), self.server
        )
        add_HermesToolServicer_to_server(
            HermesToolServicer(self), self.server
        )

    async def start(self):
        self.server.add_insecure_port(f'[::]:{self.port}')
        await self.server.start()

    async def stop(self):
        await self.server.stop(grace=5)
```

```typescript
// 在 Harness 中消费 Hermes gRPC 服务
// harness/src/hermes-client.ts
class HermesClient {
  private client: HermesServiceClient;

  async getSkill(skillName: string): Promise<SkillDefinition> {
    const response = await this.client.getSkill({
      name: skillName,
      format: SkillFormat.PROTO
    });
    return this.protoToSkill(response);
  }

  async executeMemoryRecall(query: string): Promise<MemoryResult> {
    const stream = this.client.recallMemory({
      query,
      maxResults: 10,
      backend: MemoryBackend.HOLOGRAPHIC
    });
    return this.collectStream(stream);
  }
}
```

---

## 5. 记忆系统：8 种后端对比与推荐方案

### 5.1 总体架构

Hermes 的记忆系统采用 **Provider 模式**，由 `MemoryManager` 统一管理：

```
MemoryManager (agent/memory_manager.py)
  ├── 内置 Memory Provider（默认）
  └── 外部 Memory Provider（同时仅激活一个）
       ├── byterover
       ├── hindsight (cloud / local_embedded / local_external)
       ├── holographic (local SQLite)
       ├── honcho
       ├── mem0
       ├── openviking
       ├── retaindb
       └── supermemory
```

**核心接口**（`agent/memory_provider.py`）：

| 钩子方法 | 调用时机 | 用途 |
|----------|---------|------|
| `initialize()` | Agent 启动 | 连接后端、创建资源 |
| `system_prompt_block()` | 构建 system prompt | 注入静态上下文 |
| `prefetch()` | 每轮 LLM 调用前 | 背景召回，注入记忆上下文 |
| `sync_turn()` | 每轮 LLM 调用后 | 持久化本轮对话 |
| `get_tool_schemas()` | 构建工具 schema | 暴露搜索/存储工具 |
| `handle_tool_call()` | 工具调用时 | 分发工具请求 |
| `shutdown()` | Agent 退出 | 清理连接 |
| 可选钩子 | 见下面各 Provider | 事件订阅 |

### 5.2 8 种后端对比

#### 5.2.1 Holographic（全息记忆）

| 属性 | 值 |
|------|-----|
| **类型** | 本地 SQLite |
| **依赖** | 无（SQLite 内置，NumPy 可选） |
| **网络** | 无需联网 |
| **价格** | 免费 |
| **部署** | 零配置 |

**特性：**
- FTS5 全文搜索
- 信任评分系统（`fact_feedback` 工具）
- 实体解析（Entity resolution）
- HRR（Holographic Reduced Representations）矢量合成检索
- 工具：`fact_store`（9 种操作）+ `fact_feedback`

**适用场景：** 本地开发、单用户、隐私优先、离线环境

#### 5.2.2 Honcho

| 属性 | 值 |
|------|-----|
| **类型** | 云端 API / 自托管 |
| **依赖** | `honcho-ai` SDK |
| **网络** | 需要 |
| **价格** | 按量计费 |
| **部署** | 云/自托管 |

**特性：**
- 双用户建模（user + AI 双角色）
- 多轮辩证推理（Dialectic multi-pass reasoning）
- 自动上下文摘要
- 会话策略：`per-directory` / `per-repo` / `per-session` / `global`
- 三层召回模式：`hybrid` / `context` / `tools`
- cadence 控制（频率成本平衡）
- 双向工具（5 个工具）

**适用场景：** 需要深度用户建模、跨会话记忆持久化、多 profile 场景

#### 5.2.3 Hindsight

| 属性 | 值 |
|------|-----|
| **类型** | 云端 / 本地内嵌 / 本地外部 |
| **依赖** | `hindsight-client` |
| **网络** | 依模式而定 |
| **价格** | 云端付费/本地免费 |
| **部署** | 三种模式灵活 |

**特性：**
- 知识图谱 + 语义搜索（multi-strategy retrieval）
- 实体解析
- 内嵌 LLM（支持 OpenAI/Anthropic/Gemini 等 9 种提供方）
- 自动记忆提取（retain）
- 跨记忆合成推理（reflect）
- 内存 Bank 隔离（支持模板化 ID）
- 异步 retain 处理
- 3 个工具：`hindsight_retain` / `hindsight_recall` / `hindsight_reflect`

**适用场景：** 需要知识图谱能力、希望保留数据本地、多模式部署弹性的场景

#### 5.2.4 Mem0

| 属性 | 值 |
|------|-----|
| **类型** | 云端 API |
| **依赖** | `mem0ai` SDK |
| **网络** | 需要 |
| **价格** | 按量计费 |
| **部署** | 仅云 |

**特性：**
- LLM 自动事实提取
- 语义搜索 + 重排序
- 自动去重
- 3 个工具：`mem0_profile` / `mem0_search` / `mem0_conclude`

**适用场景：** 简单集成、需要自动事实提取、可接受外部服务

#### 5.2.5 Supermemory

| 属性 | 值 |
|------|-----|
| **类型** | 云端 API |
| **依赖** | `supermemory` SDK |
| **网络** | 需要 |
| **价格** | 按量计费 |
| **部署** | 仅云 |

**特性：**
- 语义长期记忆
- 自动/手动存储
- session-end 对话摄取
- 多容器模式（multi-container tags）
- Profile 作用域容器
- 4 个工具：`supermemory_store` / `supermemory_search` / `supermemory_forget` / `supermemory_profile`

**适用场景：** 需要多容器隔离、精细化控制的记忆管理

#### 5.2.6 RetainDB

| 属性 | 值 |
|------|-----|
| **类型** | 云端 API |
| **依赖** | `requests` |
| **网络** | 需要 |
| **价格** | $20/月 |
| **部署** | 仅云 |

**特性：**
- 混合搜索（向量 + BM25 + 重排序）
- 7 种记忆类型
- 5 个工具：`retaindb_profile` / `retaindb_search` / `retaindb_context` / `retaindb_remember` / `retaindb_forget`

**适用场景：** 结构化记忆类型、需要专业记忆管理

#### 5.2.7 OpenViking（字节跳动）

| 属性 | 值 |
|------|-----|
| **类型** | 本地服务 |
| **依赖** | `openviking` SDK + `openviking-server` |
| **网络** | 本地 |
| **价格** | 免费 |
| **部署** | 需运行独立服务 |

**特性：**
- 文件系统式知识层级
- 分层检索（fast/deep/auto）
- URI 式访问（`viking://`）
- 5 个工具：`viking_search` / `viking_read` / `viking_browse` / `viking_remember` / `viking_add_resource`

**适用场景：** 需要结构化知识库、文件系统导航式交互

#### 5.2.8 ByteRover

| 属性 | 值 |
|------|-----|
| **类型** | 本地 CLI |
| **依赖** | `brv` CLI |
| **网络** | 可选云同步 |
| **价格** | 免费 |
| **部署** | 需安装 CLI |

**特性：**
- 层级知识树
- 分层检索（模糊文本 → LLM 驱动搜索）
- 3 个工具：`brv_query` / `brv_curate` / `brv_status`

**适用场景：** 极简记忆、本地优先、树形知识结构

### 5.3 横向对比矩阵

| 维度 | Holographic | Honcho | Hindsight | Mem0 | Supermemory | RetainDB | OpenViking | ByteRover |
|------|:-----------:|:------:|:---------:|:----:|:-----------:|:--------:|:----------:|:---------:|
| **部署模式** | 本地内嵌 | 云/自托管 | 三模式 | 云 | 云 | 云 | 本地服务 | 本地CLI |
| **联网要求** | 否 | 是 | 可选 | 是 | 是 | 是 | 否 | 可选 |
| **AI 提取** | 否 | 是（辩证推理） | 是（reflect） | 是（自动） | 是 | 是 | 否 | 否 |
| **语义搜索** | FTS5 | ✓ | ✓ | ✓ | ✓ | ✓（+BM25） | ✓ | ✓ |
| **知识图谱** | ✓（实体） | ✓（双角色） | ✓ | 否 | 否 | 否 | ✓（层级） | ✓（树形） |
| **向量维度** | 1024 (HRR) | SDK 管理 | SDK 管理 | 默认 | SDK 管理 | SDK 管理 | SDK 管理 | 外部 |
| **最大工具数** | 2 | 5 | 3 | 3 | 4 | 5 | 5 | 3 |
| **成本** | 免费 | 按量 | 免费/付费 | 按量 | 按量 | $20/月 | 免费 | 免费 |
| **无 DSN** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **跨会话** | ✓ | ✓（强） | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **多Profile** | 否 | ✓（host blocks） | ✓（bank模板） | 否 | ✓（容器） | ✓（project） | 否 | 否 |
| **用户建模** | 简单 | 深度（辩证） | 中等（reflect） | 中等 | 中等 | 中等 | 无 | 无 |
| **隐私等级** | ★★★★★ | ★★★ | ★★★★ | ★★ | ★★ | ★★ | ★★★★ | ★★★★★ |
| **成熟度** | ★★★ | ★★★★ | ★★★★ | ★★★ | ★★★ | ★★ | ★★ | ★★ |

### 5.4 推荐方案

#### 5.4.1 开发/测试环境

```
首选：Holographic
理由：
- 零配置，零成本
- 开箱即用（SQLite 内置）
- 功能完善（FTS5 + 实体解析 + HRR）
- 完全的离线支持和隐私保障
```

#### 5.4.2 个人/小团队生产环境

```
首选：Hindsight（local_embedded 模式）
理由：
- 知识图谱支持，记忆关联性强
- 使用本地 LLM，数据不出本地
- reflect 自动提炼高价值信息
- 三种模式灵活切换（从本地平滑迁移到云端）
- 比单机 Holographic 更强的检索能力

备选：Honcho
理由：
- 最成熟的用户建模能力
- 辩证推理深度可控
- 多 Profile 支持完善
- 适合需要深度个性化的场景
```

#### 5.4.3 企业/多用户生产环境

```
首选：Honcho + Holographic 分层架构
理由：
- Honcho 提供跨会话、多用户的深度建模
- Holographic 作为本地回退和即时记忆
- Honcho 的多 Profile 支持直接映射企业租户
- 辩证推理可调，控制成本

外部存储方案：
- S3/OSS/MinIO：Hindsight cloud 模式
- 自托管：自建 Honcho 或 Hindsight local_external
```

#### 5.4.4 数据敏感性考量

| 数据敏感度 | 推荐方案 | 原因 |
|-----------|---------|------|
| **极高**（金融/医疗） | Holographic / OpenViking | 完全本地，零外传 |
| **高**（企业内部） | Hindsight(local) | 本地 LLM，可控 |
| **中**（个人助手） | Honcho | 按量付费，能力强 |
| **低**（通用助手） | Mem0 / Supermemory | 集成最简单 |

#### 5.4.5 插件开发建议

当前 `plugins/memory/` 中 `hindsight`、`honcho`、`holographic` 的代码最为成熟。推荐参考：

- **本地后端模板**：`holographic`（最简单，零依赖）
- **云后端模板**：`supermemory`（API 封装清晰）
- **混合模式模板**：`hindsight`（三种部署模式设计最佳）
- **工具丰富度模板**：`honcho`（5 个工具 + 深度配置）

---

## 附录 A：模块文件统计

| 模块 | 文件数 | 核心文件 |
|------|--------|---------|
| `agent/` | ~63 | `run_agent.py` (817KB)、`memory_manager.py`、`prompt_builder.py` |
| `skills/` | 532+ | 25+ 类别，每类别含 SKILL.md |
| `tools/` | 82 | `delegate_tool.py`、`skill_manager_tool.py`、`registry.py` |
| `plugins/` | 15+ 子模块 | `memory/` (8种)、`context_engine/` |
| `gateway/` | ~34 平台 | `run.py`、`platforms/` 各适配器 |
| `cron/` | 3 | `scheduler.py`、`jobs.py` |
| `acp_adapter/` | 8 | `server.py`、`auth.py`、`tools.py` |
| `hermes_cli/` | 80 | CLI 配置、皮肤引擎、安装向导 |
| `tests/` | ~900 | ~17,000 测试用例 |

## 附录 B：关键术语对照

| Hermes 术语 | 说明 | 对应概念 |
|-------------|------|---------|
| SKILL.md | 技能定义文件（YAML frontmatter + Markdown） | 相当于指令集 |
| MemoryProvider | 记忆提供者插件接口 | 持久化后端 |
| ContextEngine | 上下文管理引擎 | Token 预算管理 |
| Gateway | 消息网关 | 多平台统一入口 |
| Toolset | 工具集组合 | 按场景分组的工具集合 |
| Subagent | 子代理（隔离执行上下文） | 任务委派 |
| ACP | Agent Communication Protocol | IDE 集成协议 |
| MCP | Model Context Protocol | 模型上下文协议 |

---

*报告完毕。本分析基于 Hermes Agent 仓库代码，结合 taiji-agent 的 OpenClaw 标准理解与 Harness 架构设计而成。*
