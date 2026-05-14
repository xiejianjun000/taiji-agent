# 多租户数据模型设计

> 设计日期：2026-05-14
> 设计依据：Hermes Agent 多租户章节（deliverables/05-hermes-agent-analysis.md）、技术可行性评估（deliverables/06-technical-feasibility-assessment.md）、现有代码（src/opentaiji/memory/session.py、src/opentaiji/learning/loop.py）
> 版本：v1.0

---

## 目录

1. [设计目标](#1-设计目标)
2. [租户模型](#2-租户模型)
3. [三种隔离策略](#3-三种隔离策略核心)
4. [数据模型设计](#4-数据模型设计)
5. [租户路由中间件](#5-租户路由中间件)
6. [RBAC 权限模型](#6-rbac-权限模型)
7. [存储设计](#7-存储设计)
8. [数据迁移方案](#8-数据迁移方案)
9. [API 设计](#9-api-设计)
10. [实现计划](#10-实现计划)

---

## 1. 设计目标

### 1.1 解决的问题

当前 Taiji Agent 为单租户架构，所有数据共享在 `~/.opentaiji/` 目录下。存在以下问题：

| 问题 | 现状 | 风险 |
|------|------|------|
| **数据隔离** | 所有用户的会话、记忆、技能存储在同一文件系统 | 数据泄露、交叉污染 |
| **配置混淆** | 全局 `~/.opentaiji/` 配置被所有用户共享 | 配置干扰 |
| **无用户管理** | `learning/loop.py` 中 `peer_id` 硬编码为 `"user"` | 无法区分真实用户 |
| **无权限控制** | `memory/session.py` 中无任何权限校验 | 越权访问 |
| **无法水平扩展** | 单机文件存储，无法支撑企业多部门使用 | 扩展瓶颈 |

### 1.2 设计原则

1. **渐进式隔离**：从 POOL（最简）到 INSTANCE（最强），按需升级
2. **最小侵入**：现有单租户代码通过兼容层运行，无需修改
3. **租户感知透明化**：通过上下文注入（ContextVar），业务代码零感知
4. **数据路径可预测**：所有租户数据的存储路径规则统一，便于审计
5. **配置优先**：隔离策略通过配置文件切换，无需代码变更

### 1.3 非功能性需求

| 需求 | 目标 | 衡量方式 |
|------|------|----------|
| **POOL 策略性能损耗** | < 5% | 基准测试对比 |
| **BUCKET 策略性能损耗** | < 10% | 基准测试对比 |
| **租户切换延迟** | < 50ms | 请求到租户上下文注入 |
| **最大租户数（POOL）** | 1000 | 单节点 |
| **最大租户数（BUCKET）** | 100 | 单节点 |
| **数据隔离完备性** | 100% | 渗透测试 |
| **API 兼容性** | 向后兼容 | 现有 API 无需修改 |

---

## 2. 租户模型

### 2.1 租户实体定义

```python
# src/opentaiji/multitenant/models/tenant.py

@dataclass
class Tenant:
    """租户核心模型"""
    tenant_id: str                    # 租户 ID（UUID v4）
    name: str                         # 租户名称（如"娄底市生态环境局"）
    tier: TenantTier                  # 层级：free | pro | enterprise
    status: TenantStatus              # 状态：active | suspended | deleted
    isolation_strategy: IsolationStrategy  # 隔离策略：pool | bucket | instance
    storage_config: Dict[str, Any]    # 存储配置（path/bucket/endpoint）
    department_ids: List[str]         # 下属部门 ID 列表
    config_overrides: Dict[str, Any]  # 配置覆盖（LLM 模型、速率限制等）
    allowed_providers: List[str]      # 允许的 LLM 提供商
    rate_limits: RateLimitConfig      # 速率限制
    created_at: datetime
    updated_at: datetime
```

```yaml
# 租户 YAML 示例
tenants:
  tenant-loudi-epb:
    name: "娄底市生态环境局"
    tier: enterprise
    status: active
    isolation_strategy: pool
    storage_config:
      base_path: /data/opentaiji/tenants/tenant-loudi-epb
    departments:
      - "dept-huanping"
      - "dept-xiaofang"
      - "dept-wuran"
    config_overrides:
      default_model: "qwen-max"
    allowed_providers: ["qwen", "glm", "deepseek"]
    rate_limits:
      requests_per_minute: 200
      tokens_per_day: 50000000

  tenant-demo:
    name: "演示租户"
    tier: free
    status: active
    isolation_strategy: pool
    storage_config:
      base_path: /data/opentaiji/tenants/tenant-demo
    allowed_providers: ["qwen"]
    rate_limits:
      requests_per_minute: 20
      tokens_per_day: 1000000
```

### 2.2 组织架构

```
Tenant（租户）
  ├── Department（部门）
  │     ├── User（用户）
  │     ├── User（用户）
  │     └── ...
  ├── Department（部门）
  │     ├── User（用户）
  │     └── ...
  └── ...
```

```python
@dataclass
class Department:
    """部门模型"""
    dept_id: str                      # 部门 ID（UUID）
    tenant_id: str                    # 所属租户
    name: str                         # 部门名称（如"环评审批科"）
    parent_dept_id: Optional[str]     # 上级部门（支持层级组织）
    dept_type: str                    # 部门类型（business/tech/support）
    created_at: datetime

@dataclass
class TenantUser:
    """租户用户模型"""
    user_id: str                      # 用户 ID（UUID）
    tenant_id: str                    # 所属租户
    department_id: str                # 所属部门
    username: str                     # 登录名
    display_name: str                 # 显示名称
    role: UserRole                    # 角色：admin/user/auditor
    phone: str                        # 手机号
    email: str                        # 邮箱
    status: UserStatus                # 状态：active/disabled
    created_at: datetime
    last_login: Optional[datetime]
```

### 2.3 租户配置

```python
@dataclass
class TenantConfig:
    """租户级配置，控制该租户下所有用户的行为"""
    tenant_id: str
    llm_config: LLMConfig             # LLM 模型配置
    memory_config: MemoryConfig       # 记忆系统配置
    skill_whitelist: List[str]        # 可用技能白名单
    guardrail_config: GuardrailConfig # 安全护栏配置
    audit_config: AuditConfig         # 审计配置
    storage_quota: StorageQuota       # 存储配额
```

---

## 3. 三种隔离策略（核心）

### 3.1 POOL 策略（前缀隔离）

**原理**：所有租户共享同一存储后端，通过租户 ID 作为路径前缀/命名空间实现逻辑隔离。

```
存储结构：
/data/opentaiji/
├── tenants/
│   ├── {tenant_id}/
│   │   ├── sessions/           # 会话数据
│   │   ├── memories/           # 记忆数据
│   │   ├── skills/             # 技能定义
│   │   ├── configs/            # 租户配置
│   │   └── logs/               # 操作日志
│   └── {tenant_id}/
│       └── ...
├── system/                      # 系统级数据（租户注册表等）
└── global_config.yaml           # 全局配置
```

**实现方式**：

```python
class PoolStorage:
    """POOL 策略存储：共享存储 + 路径前缀隔离"""

    def __init__(self, base_path: Path, tenant_id: str):
        self.tenant_path = base_path / "tenants" / tenant_id

    def session_path(self) -> Path:
        return self.tenant_path / "sessions"

    def memory_path(self) -> Path:
        return self.tenant_path / "memories"

    def skill_path(self) -> Path:
        return self.tenant_path / "skills"

    def ensure_dirs(self):
        """确保租户目录结构存在"""
        for subdir in ["sessions", "memories", "skills", "configs", "logs"]:
            (self.tenant_path / subdir).mkdir(parents=True, exist_ok=True)
```

**适用场景**：SaaS 中小规模部署、企业内部多部门、开发/测试环境

**优缺点**：

| 维度 | 评估 |
|------|------|
| 实现复杂度 | 低（仅需改造文件路径） |
| 性能损耗 | < 3%（仅路径前缀开销） |
| 成本 | 最优（共享存储） |
| 隔离强度 | 逻辑隔离（无物理隔离） |
| 最大租户数 | 1000+（受文件系统 inode 限制） |
| 数据泄漏风险 | 中（路径遍历需防御） |
| 备份恢复 | 按目录粒度 |
| 迁移难度 | 无（基础策略） |

### 3.2 BUCKET 策略（独立存储桶）

**原理**：每个租户拥有独立的 SQLite 数据库文件和独立的存储桶（文件系统目录），数据库级别隔离。

```
存储结构：
/data/opentaiji/
├── tenants/
│   ├── {tenant_id}/
│   │   ├── data.db              # 该租户的独立 SQLite 数据库
│   │   ├── sessions.db          # 或按类型拆分多个 DB
│   │   ├── memories/
│   │   │   ├── memory.json
│   │   │   └── profile.json
│   │   ├── skills/
│   │   ├── configs/
│   │   └── logs/
│   └── {tenant_id}/
│       └── ...
├── tenant_registry.db            # 全局租户注册表
└── global_config.yaml
```

**实现方式**：

```python
class BucketStorage:
    """BUCKET 策略存储：每个租户独立数据库文件"""

    def __init__(self, base_path: Path, tenant_id: str):
        self.tenant_path = base_path / "tenants" / tenant_id
        self.db_path = self.tenant_path / "data.db"
        self._connection: Optional[sqlite3.Connection] = None

    def get_connection(self) -> sqlite3.Connection:
        """获取该租户的独立数据库连接"""
        if self._connection is None:
            self.tenant_path.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
        return self._connection

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None
```

**适用场景**：中型企业、数据隔离要求适中的场景、多租户 SaaS 正式环境

**优缺点**：

| 维度 | 评估 |
|------|------|
| 实现复杂度 | 中（需管理多数据库连接池） |
| 性能损耗 | < 8%（独立 DB 连接开销） |
| 成本 | 中（需更多磁盘空间） |
| 隔离强度 | 数据库级物理隔离 |
| 最大租户数 | 100（受文件句柄限制，可通过连接池缓解） |
| 数据泄漏风险 | 低（数据库文件独立） |
| 备份恢复 | 按数据库文件粒度 |
| 迁移难度 | POOL→BUCKET 迁移简单 |

### 3.3 INSTANCE 策略（完全隔离）

**原理**：每个租户运行独立的 Taiji Agent 实例（独立进程/容器），操作系统级隔离。

```
部署结构（Docker）：
docker-compose.yml
├── taiji-system                   # 系统管理服务
│   ├── tenant-manager             # 租户管理 API
│   └── tenant-registry            # 租户注册表
├── taiji-tenant-loudi-epb         # 租户 A 实例
│   ├── data/                      # 完全独立的数据目录
│   ├── config.yaml                # 完全独立的配置
│   └── ...                        # 独立进程
├── taiji-tenant-zhuzhou           # 租户 B 实例
│   ├── data/
│   ├── config.yaml
│   └── ...
└── ...                            # N 个租户实例
```

**实现方式**：

```python
class InstanceManager:
    """INSTANCE 策略管理器：管理租户独立实例"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.instances: Dict[str, TenantInstance] = {}

    async def start_instance(self, tenant: Tenant) -> TenantInstance:
        """启动租户独立实例"""
        instance_dir = self.base_dir / "instances" / tenant.tenant_id
        instance = TenantInstance(
            tenant=tenant,
            instance_dir=instance_dir,
            config=self._generate_instance_config(tenant),
        )
        # 启动子进程
        instance.process = await self._launch_process(instance)
        self.instances[tenant.tenant_id] = instance
        return instance

    async def stop_instance(self, tenant_id: str):
        """停止租户实例"""
        if instance := self.instances.get(tenant_id):
            instance.process.terminate()
            await instance.process.wait()
            del self.instances[tenant_id]
```

**适用场景**：高安全要求政务场景、数据需通过等保三级认证、完全定制化的大客户

**优缺点**：

| 维度 | 评估 |
|------|------|
| 实现复杂度 | 高（需编排管理和健康监测） |
| 性能损耗 | 高（每实例独立资源） |
| 成本 | 最高（N 倍资源） |
| 隔离强度 | 操作系统级完全隔离 |
| 最大租户数 | 受宿主机资源限制 |
| 数据泄漏风险 | 极低（物理/虚拟化隔离） |
| 备份恢复 | 按实例粒度，标准运维工具 |
| 迁移难度 | 需重新部署 |

### 3.4 策略选择流程图

```
是否需要多租户？
  ├── 否 → 保持单租户（兼容模式）
  └── 是 → 选择隔离等级
        ├── 中小企业 / SaaS / 开发测试
        │     └── POOL 策略（推荐起步）
        ├── 中大型企业 / 正式生产环境
        │     └── BUCKET 策略
        └── 政务 / 金融 / 医疗 / 高安全要求
              └── INSTANCE 策略
```

---

## 4. 数据模型设计

### 4.1 用户模型

```yaml
TenantUser:
  id: string (UUID v4)               # 用户唯一标识
  tenant_id: string (UUID v4)        # 所属租户
  department_id: string (UUID v4)    # 所属部门
  username: string                    # 登录名（租户内唯一）
  display_name: string                # 显示名称
  password_hash: string               # 密码哈希（SM3 或 bcrypt）
  role: enum[admin, user, auditor]   # 角色
  phone: string                       # 手机号
  email: string                       # 邮箱
  avatar: string                      # 头像 URL
  status: enum[active, disabled]      # 用户状态
  preferences: dict                   # 用户偏好（JSON）
  created_at: datetime
  updated_at: datetime
  last_login: datetime | null
```

**约束**：
- `(tenant_id, username)` 联合唯一
- `(tenant_id, department_id)` 外键引用

### 4.2 会话模型

```yaml
Session:
  id: string (UUID v4)               # 会话唯一标识
  tenant_id: string (UUID v4)        # 所属租户
  user_id: string (UUID v4)          # 所属用户
  title: string                       # 会话标题
  messages: List[Message]             # 消息列表
  context: dict                       # 会话上下文（JSON）
  metadata: dict                      # 会话元数据（JSON）
  message_count: int                  # 消息数量（冗余优化）
  token_count: int                    # Token 消耗（冗余优化）
  status: enum[active, archived]      # 会话状态
  tags: List[string]                  # 标签（用于分类检索）
  created_at: datetime
  updated_at: datetime
  archived_at: datetime | null

Message:
  id: string (UUID v4)               # 消息唯一标识
  session_id: string (UUID v4)       # 所属会话
  role: enum[user, assistant, system, tool]
  content: string                     # 消息内容
  tool_calls: List[ToolCall] | null   # 工具调用
  tool_results: List[ToolResult] | null  # 工具执行结果
  token_count: int                    # 该消息 Token 数
  metadata: dict                      # 消息元数据
  timestamp: datetime
```

**现有代码适配**（`session.py` 的 `SessionMemory` 改造）：

```python
# 当前: 全局 ~/.opentaiji/memory/ 目录
# 改造后: {tenant_path}/sessions/{session_id}/

class MultiTenantSessionMemory:
    """多租户会话记忆（POOL 策略）"""

    def __init__(self, base_path: Path, tenant_context: TenantContext):
        self.tenant_path = base_path / "tenants" / tenant_context.tenant_id
        self.tenant_path.mkdir(parents=True, exist_ok=True)

    def get_session(self, session_id: str) -> Optional[Session]:
        """获取租户下指定会话"""
        session_file = self.tenant_path / "sessions" / f"{session_id}.json"
        if session_file.exists():
            data = json.loads(session_file.read_text())
            return Session(**data)
        return None

    def save_session(self, session: Session):
        """保存会话（自动注入 tenant_id）"""
        session.tenant_id = get_current_tenant().tenant_id
        session_dir = self.tenant_path / "sessions"
        session_dir.mkdir(parents=True, exist_ok=True)
        session_file = session_dir / f"{session.id}.json"
        session_file.write_text(
            json.dumps(asdict(session), ensure_ascii=False, indent=2)
        )
```

### 4.3 记忆模型

```yaml
Memory:
  id: string (UUID v4)               # 记忆唯一标识
  tenant_id: string (UUID v4)        # 所属租户（隔离关键字段）
  user_id: string (UUID v4)          # 所属用户
  memory_type: enum[fact, preference, context, session, skill]
  key: string                         # 记忆键名
  value: string                       # 记忆值
  embedding: List[float] | null       # 向量嵌入（语义搜索用）
  tags: List[string]                  # 标签
  source: string                      # 来源（user/agent/learning）
  confidence: float                   # 置信度 0.0~1.0
  access_count: int                   # 访问次数
  created_at: datetime
  last_accessed: datetime
  expires_at: datetime | null         # 过期时间（TTL）
```

**现有代码适配**（`learning/loop.py` 的 `HonchoMemory` 改造）：

```python
# 当前: 全局 peer_cards.json / contexts.json
# 改造后: 每个租户独立文件

class MultiTenantHonchoMemory:
    """多租户 Honcho 记忆（POOL 策略）"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self._cache: Dict[str, HonchoMemory] = {}

    def _get_tenant_memory(self, tenant_id: str) -> HonchoMemory:
        """获取或创建租户级 HonchoMemory 实例"""
        if tenant_id not in self._cache:
            tenant_memory_path = self.base_path / "tenants" / tenant_id / "memories" / "honcho"
            tenant_memory = HonchoMemory(memory_dir=tenant_memory_path)
            self._cache[tenant_id] = tenant_memory
        return self._cache[tenant_id]

    def get_peer_card(self, tenant_id: str, user_id: str = "user") -> PeerCard:
        tenant_memory = self._get_tenant_memory(tenant_id)
        return tenant_memory.get_peer_card(user_id)

    def update_peer_card(self, tenant_id: str, user_id: str, **kwargs):
        tenant_memory = self._get_tenant_memory(tenant_id)
        tenant_memory.update_peer_card(user_id, **kwargs)
```

### 4.4 知识库模型

```yaml
KnowledgeBase:
  id: string (UUID v4)               # 知识库唯一标识
  tenant_id: string (UUID v4)        # 所属租户
  name: string                         # 知识库名称
  description: string                  # 知识库描述
  kb_type: enum[document, faq, graph, vector]
  documents: List[KnowledgeDoc]        # 知识文档列表
  embedding_config: dict               # 嵌入配置
  access_roles: List[string]           # 可访问角色
  created_at: datetime
  updated_at: datetime

KnowledgeDoc:
  id: string (UUID v4)               # 文档唯一标识
  kb_id: string (UUID v4)            # 所属知识库
  tenant_id: string (UUID v4)        # 所属租户
  title: string                        # 文档标题
  content: string                      # 文档内容
  source: string                       # 来源（upload/url/api）
  file_type: string                    # 文件类型（pdf/docx/md/txt）
  file_path: string | null             # 文件存储路径
  chunk_count: int                     # 分块数量
  token_count: int                     # Token 数
  tags: List[string]                   # 标签
  status: enum[processing, ready, failed]
  created_at: datetime
  updated_at: datetime
```

**存储路径规则**（POOL 策略）：

```
{base_path}/tenants/{tenant_id}/
├── knowledge/
│   ├── {kb_id}/
│   │   ├── meta.json              # 知识库元数据
│   │   ├── documents/
│   │   │   ├── {doc_id}.json      # 文档内容
│   │   │   ├── {doc_id}.md        # 原始 Markdown
│   │   │   └── {doc_id}_chunks.json  # 分块数据
│   │   └── embeddings.npy         # 向量索引
│   └── ...
└── ...
```

### 4.5 配置模型

```yaml
TenantSettings:
  tenant_id: string (UUID v4)
  llm:
    default_model: string              # 默认模型
    allowed_models: List[string]       # 允许的模型列表
    max_tokens: int                    # 最大 Token
    temperature: float                 # 温度参数
  memory:
    backend: enum[holographic, honcho, hindsight]
    retention_days: int                # 记忆保留天数
    auto_extract: bool                 # 自动提取记忆
  skills:
    enabled_ids: List[string]          # 启用的技能 ID
    disabled_ids: List[string]         # 禁用的技能 ID
    allow_custom: bool                 # 允许用户创建自定义技能
  guardrails:
    enabled: bool
    sensitivity: enum[low, medium, high]
    custom_rules: List[GuardrailRule]
  audit:
    enabled: bool                      # 是否开启审计日志
    retention_days: int                # 审计日志保留天数
  storage:
    max_sessions: int                  # 最大会话数
    max_memories: int                  # 最大记忆数
    max_knowledge_docs: int            # 最大知识文档数
  rate_limits:
    requests_per_minute: int
    tokens_per_day: int
    concurrent_sessions: int
```

---

## 5. 租户路由中间件

### 5.1 租户上下文

使用 Python `contextvars` 实现租户上下文透传，不污染业务代码：

```python
# src/opentaiji/multitenant/context.py

import contextvars
from contextlib import contextmanager
from typing import Optional

tenant_context_var: contextvars.ContextVar[Optional["TenantContext"]] = (
    contextvars.ContextVar("tenant_context", default=None)
)

@dataclass
class TenantContext:
    """租户上下文，贯穿整个请求生命周期"""
    tenant: Tenant
    user: TenantUser
    isolation: IsolationStrategy
    storage: "TenantStorage"

def get_current_tenant() -> Optional[Tenant]:
    """获取当前租户（业务代码无感知）"""
    ctx = tenant_context_var.get()
    return ctx.tenant if ctx else None

def get_current_user() -> Optional[TenantUser]:
    """获取当前用户（业务代码无感知）"""
    ctx = tenant_context_var.get()
    return ctx.user if ctx else None

@contextmanager
def tenant_context(ctx: TenantContext):
    """租户上下文注入上下文管理器"""
    token = tenant_context_var.set(ctx)
    try:
        yield
    finally:
        tenant_context_var.reset(token)
```

### 5.2 中间件实现

```python
# src/opentaiji/multitenant/middleware.py

class TenantAwareMiddleware:
    """
    租户路由中间件。

    拦截进入的所有请求，解析租户身份，注入租户上下文。
    支持多种租户识别方式：
    - HTTP Header: X-Tenant-ID
    - API Key: X-Tenant-API-Key
    - JWT Token: Authorization: Bearer <token>
    - Gateway 平台用户映射
    """

    TENANT_HEADER = "X-Tenant-ID"
    API_KEY_HEADER = "X-Tenant-API-Key"
    AUTH_HEADER = "Authorization"

    def __init__(self, tenant_manager: "TenantManager"):
        self.tenant_manager = tenant_manager

    async def resolve_tenant(self, request: Request) -> Optional[TenantContext]:
        """从请求中解析租户上下文"""
        # 方法1: Header 指定租户 ID
        tenant_id = request.headers.get(self.TENANT_HEADER)
        if tenant_id:
            tenant = await self.tenant_manager.get_tenant(tenant_id)
            user = await self._resolve_user(request, tenant)
            if tenant and user:
                return self._build_context(tenant, user)

        # 方法2: API Key 识别
        api_key = request.headers.get(self.API_KEY_HEADER)
        if api_key:
            tenant = await self.tenant_manager.get_tenant_by_api_key(api_key)
            user = await self._resolve_user(request, tenant)
            if tenant and user:
                return self._build_context(tenant, user)

        # 方法3: JWT Token
        auth = request.headers.get(self.AUTH_HEADER, "")
        if auth.startswith("Bearer "):
            token = auth[7:]
            return await self._resolve_from_token(token)

        return None

    async def __call__(self, request: Request, call_next):
        # 解析租户
        tenant_ctx = await self.resolve_tenant(request)

        if not tenant_ctx:
            return Response(status_code=401, body="Unauthorized: no tenant context")

        # 检查租户状态
        if tenant_ctx.tenant.status == TenantStatus.SUSPENDED:
            return Response(status_code=403, body="Tenant suspended")

        # 注入租户上下文
        with tenant_context(tenant_ctx):
            # 注入存储层
            request.state.storage = tenant_ctx.storage
            response = await call_next(request)
            # 响应中返回租户标识
            response.headers[self.TENANT_HEADER] = tenant_ctx.tenant.tenant_id
            return response
```

### 5.3 数据访问路由

```python
# src/opentaiji/multitenant/router.py

class TenantAwareRouter:
    """
    数据访问路由器。

    根据隔离策略将数据操作路由到对应的存储实现。
    业务代码只调用 route()，无需关心底层存储策略。
    """

    def __init__(self, isolation_manager: "IsolationManager"):
        self.isolation_manager = isolation_manager

    async def route(self, operation: str, data_type: str, **kwargs) -> Any:
        """路由数据操作到正确的存储后端"""
        tenant_ctx = get_current_tenant_context()
        if not tenant_ctx:
            # 回退到单租户模式（向后兼容）
            return await self._legacy_route(operation, data_type, **kwargs)

        storage = tenant_ctx.storage
        isolation = tenant_ctx.isolation

        if isolation == IsolationStrategy.POOL:
            return await self._route_pool(storage, operation, data_type, **kwargs)
        elif isolation == IsolationStrategy.BUCKET:
            return await self._route_bucket(storage, operation, data_type, **kwargs)
        elif isolation == IsolationStrategy.INSTANCE:
            return await self._route_instance(storage, operation, data_type, **kwargs)

    async def _route_pool(self, storage, operation, data_type, **kwargs):
        """POOL 路由：路径 + tenant_id 前缀"""
        # 自动注入 tenant_id 到查询参数
        kwargs["tenant_id"] = get_current_tenant().tenant_id
        return await storage.execute(operation, data_type, **kwargs)

    async def _route_bucket(self, storage, operation, data_type, **kwargs):
        """BUCKET 路由：直接操作租户独立 DB"""
        db = storage.get_connection()
        return await storage.execute_on_db(db, operation, data_type, **kwargs)
```

---

## 6. RBAC 权限模型

### 6.1 角色定义

| 角色 | 级别 | 范围 | 描述 |
|------|------|------|------|
| `super_admin` | 系统级 | 所有租户 | 系统管理员，管理所有租户和系统配置 |
| `tenant_admin` | 租户级 | 单个租户 | 租户管理员，管理该租户下的用户和配置 |
| `department_admin` | 部门级 | 单个部门 | 部门管理员，管理部门用户和数据 |
| `user` | 用户级 | 个人 | 普通用户，使用 Agent 功能 |
| `auditor` | 租户级 | 单个租户 | 审计员，只读访问审计日志 |

### 6.2 权限矩阵

| 操作 | super_admin | tenant_admin | dept_admin | user | auditor |
|------|:-----------:|:------------:|:----------:|:----:|:-------:|
| 管理租户 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 管理租户用户 | ✅ | ✅ | ✅(本部门) | ❌ | ❌ |
| 管理租户配置 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 查看审计日志 | ✅ | ✅ | ✅(本部门) | ❌ | ✅ |
| 创建/编辑会话 | ✅ | ✅ | ✅ | ✅ | ❌ |
| 查看会话 | ✅ | ✅ | ✅(本部门) | ✅(自己的) | ✅ |
| 管理技能 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 管理知识库 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 使用技能 | ✅ | ✅ | ✅ | ✅ | ❌ |
| 查看用户画像 | ✅ | ✅ | ✅(本部门) | ✅(自己的) | ✅ |
| 导出数据 | ✅ | ✅ | ✅(本部门) | ✅(自己的) | ❌ |

### 6.3 数据范围控制

```python
@dataclass
class DataScope:
    """数据范围控制"""
    scope_type: ScopeType              # ALL / TENANT / DEPARTMENT / SELF
    tenant_id: Optional[str]
    department_id: Optional[str]
    user_id: Optional[str]

class RBACManager:
    """RBAC 权限管理器"""

    def check_permission(self, user: TenantUser, operation: str) -> bool:
        """检查用户是否有操作权限"""
        role_permissions = PERMISSION_MATRIX.get(user.role, set())
        return operation in role_permissions

    def get_data_scope(self, user: TenantUser) -> DataScope:
        """获取用户的数据范围"""
        if user.role == UserRole.SUPER_ADMIN:
            return DataScope(ScopeType.ALL)
        elif user.role == UserRole.TENANT_ADMIN:
            return DataScope(ScopeType.TENANT, tenant_id=user.tenant_id)
        elif user.role == UserRole.DEPT_ADMIN:
            return DataScope(
                ScopeType.DEPARTMENT,
                tenant_id=user.tenant_id,
                department_id=user.department_id,
            )
        else:
            return DataScope(
                ScopeType.SELF,
                tenant_id=user.tenant_id,
                user_id=user.user_id,
            )

    def filter_query(self, user: TenantUser, query: dict) -> dict:
        """根据用户数据范围过滤查询条件"""
        scope = self.get_data_scope(user)
        if scope.scope_type == ScopeType.ALL:
            return query
        query["tenant_id"] = scope.tenant_id
        if scope.scope_type == ScopeType.DEPARTMENT:
            query["department_id"] = scope.department_id
        elif scope.scope_type == ScopeType.SELF:
            query["user_id"] = scope.user_id
        return query
```

---

## 7. 存储设计

### 7.1 SQLite（本地优先）

#### 7.1.1 POOL 策略：共享数据库 + 前缀

所有租户共享一个 SQLite 数据库，通过 `tenant_id` 字段隔离：

```sql
-- 全局共享数据库: opentaiji.db

-- 系统表（无 tenant_id，全局共享）
CREATE TABLE system_tenants (
    tenant_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tier TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL
);

-- 租户隔离表（所有操作均 WHERE tenant_id = ?）
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,            -- 隔离字段
    user_id TEXT NOT NULL,
    title TEXT,
    messages TEXT,                      -- JSON
    context TEXT,                       -- JSON
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX idx_sessions_tenant ON sessions(tenant_id);

CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,            -- 隔离字段
    user_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_accessed TEXT
);
CREATE INDEX idx_memories_tenant ON memories(tenant_id);
CREATE INDEX idx_memories_tenant_user ON memories(tenant_id, user_id);

CREATE TABLE skills (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,            -- 隔离字段
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    instructions TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX idx_skills_tenant ON skills(tenant_id);
CREATE UNIQUE INDEX idx_skills_tenant_name ON skills(tenant_id, name);
```

**查询拦截**：所有业务查询自动追加 `tenant_id` 条件：

```python
class TenantAwareQuery:
    """自动注入 tenant_id 的查询构造器"""

    def __init__(self, cursor, tenant_id: str):
        self.cursor = cursor
        self.tenant_id = tenant_id

    def execute(self, sql: str, params: dict = None):
        """自动追加 tenant_id 条件"""
        if "tenant_id" not in sql.lower():
            # 非系统表查询自动追加
            sql = self._inject_tenant_condition(sql)
            params = params or {}
            params["tenant_id"] = self.tenant_id
        return self.cursor.execute(sql, params)

    def _inject_tenant_condition(self, sql: str) -> str:
        """在 WHERE 后追加 AND tenant_id = :tenant_id"""
        if "where" in sql.lower():
            # 已有 WHERE 条件
            idx = sql.lower().index("where") + 5
            space_idx = idx
            while space_idx < len(sql) and sql[space_idx] != ' ':
                space_idx += 1  # skip "where"
            rest = sql[space_idx:]
            return sql[:idx] + " tenant_id = :tenant_id AND " + rest.lstrip()
        else:
            # 无 WHERE 条件
            return sql + " WHERE tenant_id = :tenant_id"
```

#### 7.1.2 BUCKET 策略：每个租户独立数据库文件

```python
class TenantDatabaseManager:
    """租户数据库管理器（BUCKET 策略）"""

    def __init__(self, base_path: Path, max_connections: int = 20):
        self.base_path = base_path
        self._pools: Dict[str, sqlite3.Connection] = {}
        self._lock = asyncio.Lock()

    async def get_db(self, tenant_id: str) -> sqlite3.Connection:
        """获取租户数据库连接"""
        if tenant_id not in self._pools:
            db_path = self.base_path / tenant_id / "data.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(str(db_path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA cache_size=-8000")  # 8MB cache
            conn.row_factory = sqlite3.Row

            self._pools[tenant_id] = conn
            await self._initialize_schema(conn)

        return self._pools[tenant_id]

    async def _initialize_schema(self, conn):
        """初始化租户数据库表结构"""
        schema = """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT,
            messages TEXT,
            context TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        -- 注意：BUCKET 策略下表中无 tenant_id 字段
        -- 因为数据库文件本身已经隔离
        """
        conn.executescript(schema)
        conn.commit()

    async def remove_db(self, tenant_id: str):
        """移除租户数据库（租户删除时调用）"""
        if tenant_id in self._pools:
            self._pools[tenant_id].close()
            del self._pools[tenant_id]

        db_path = self.base_path / tenant_id / "data.db"
        if db_path.exists():
            db_path.unlink()
```

### 7.2 S3 兼容存储（云同步）

#### 7.2.1 路径命名规则

```
S3 Bucket Structure:
s3://opentaiji-data/
├── system/                          # 系统级数据
│   ├── tenants.json                 # 租户注册表
│   └── global_config.yaml
│
├── tenants/
│   ├── {tenant_id}/                 # POOL 策略
│   │   ├── sessions/{session_id}.json
│   │   ├── memories/{memory_id}.json
│   │   ├── skills/{skill_id}.yaml
│   │   ├── knowledge/{kb_id}/
│   │   └── config.yaml
│   │
│   └── {tenant_id}/                 # BUCKET 策略（独立前缀）
│       └── ...
│
└── archived/                        # 归档租户数据
    └── {tenant_id}_{timestamp}.tar.gz
```

#### 7.2.2 访问控制

```python
class S3AccessControl:
    """S3 访问控制策略"""

    def get_tenant_policy(self, tenant_id: str) -> dict:
        """生成租户 IAM 策略，仅允许访问该租户的路径"""
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket",
                    ],
                    "Resource": [
                        f"arn:aws:s3:::opentaiji-data/tenants/{tenant_id}/*",
                        f"arn:aws:s3:::opentaiji-data/tenants/{tenant_id}",
                    ],
                }
            ],
        }

    def get_presigned_url(self, tenant_id: str, key: str, expires: int = 3600) -> str:
        """生成租户级别的预签名 URL"""
        full_key = f"tenants/{tenant_id}/{key}"
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": "opentaiji-data", "Key": full_key},
            ExpiresIn=expires,
        )
```

### 7.3 存储后端抽象

沿用 Hermes 分析报告中的 `StorageBackend` 抽象模式：

```python
# src/opentaiji/multitenant/storage/backends.py

class StorageBackend(ABC):
    """存储后端抽象层"""

    @abstractmethod
    async def read(self, tenant_id: str, key: str) -> bytes: ...
    @abstractmethod
    async def write(self, tenant_id: str, key: str, data: bytes) -> str: ...
    @abstractmethod
    async def delete(self, tenant_id: str, key: str) -> None: ...
    @abstractmethod
    async def list(self, tenant_id: str, prefix: str) -> List[str]: ...


class LocalStorageBackend(StorageBackend):
    """本地文件系统实现"""

    def __init__(self, base_path: Path):
        self.base_path = base_path

    async def read(self, tenant_id: str, key: str) -> bytes:
        path = self.base_path / "tenants" / tenant_id / key
        return path.read_bytes()

    async def write(self, tenant_id: str, key: str, data: bytes) -> str:
        path = self.base_path / "tenants" / tenant_id / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    async def list(self, tenant_id: str, prefix: str) -> List[str]:
        base = self.base_path / "tenants" / tenant_id / prefix
        return [str(p.relative_to(base.parent)) for p in base.rglob("*") if p.is_file()]


class S3StorageBackend(StorageBackend):
    """AWS S3 实现"""

    def __init__(self, bucket: str, prefix: str = "tenants"):
        import boto3
        self.client = boto3.client("s3")
        self.bucket = bucket
        self.prefix = prefix

    async def read(self, tenant_id: str, key: str) -> bytes:
        full_key = f"{self.prefix}/{tenant_id}/{key}"
        result = self.client.get_object(Bucket=self.bucket, Key=full_key)
        return result["Body"].read()

    async def write(self, tenant_id: str, key: str, data: bytes) -> str:
        full_key = f"{self.prefix}/{tenant_id}/{key}"
        self.client.put_object(Bucket=self.bucket, Key=full_key, Body=data)
        return full_key
```

---

## 8. 数据迁移方案

### 8.1 POOL → BUCKET 迁移

**场景**：租户从免费版升级到企业版，需要更强的数据隔离。

```python
class PoolToBucketMigration:
    """POOL 策略 → BUCKET 策略 数据迁移"""

    def __init__(self, base_path: Path, tenant_id: str):
        self.base_path = base_path
        self.tenant_id = tenant_id

    async def migrate(self) -> MigrationResult:
        """执行迁移"""
        # 1. 创建租户独立目录和数据库
        bucket_path = self.base_path / "tenants_bucket" / self.tenant_id
        bucket_path.mkdir(parents=True, exist_ok=True)
        bucket_db = sqlite3.connect(str(bucket_path / "data.db"))

        # 2. 创建表结构
        self._create_schema(bucket_db)

        # 3. 从共享数据库读取该租户所有数据
        pool_db = self._get_pool_connection()
        tables = ["sessions", "memories", "skills", "configs"]

        for table in tables:
            rows = pool_db.execute(
                f"SELECT * FROM {table} WHERE tenant_id = ?",
                (self.tenant_id,)
            ).fetchall()
            self._copy_table(bucket_db, table, rows)

        # 4. 写入校验和
        checksum = self._calculate_checksum(pool_db, bucket_db)
        if checksum.matched:
            # 5. 更新租户配置
            self._update_tenant_strategy(self.tenant_id, IsolationStrategy.BUCKET)
            return MigrationResult(
                success=True,
                records_migrated=checksum.pool_count,
                records_verified=checksum.bucket_count,
            )
        else:
            return MigrationResult(success=False, error="Checksum mismatch")
```

### 8.2 BUCKET → INSTANCE 迁移

**场景**：数据安全要求升级，需要物理隔离。

```python
class BucketToInstanceMigration:
    """BUCKET 策略 → INSTANCE 策略 数据迁移"""

    async def migrate(self, tenant: Tenant) -> MigrationResult:
        """执行迁移"""
        # 1. 准备独立实例环境
        instance_dir = Path(f"/data/opentaiji/instances/{tenant.tenant_id}")
        instance_dir.mkdir(parents=True, exist_ok=True)

        # 2. 生成实例配置
        config = self._generate_instance_config(tenant)
        config_path = instance_dir / "config.yaml"
        config_path.write_text(yaml.dump(config))

        # 3. 复制数据文件
        source_db = Path(f"/data/opentaiji/tenants_bucket/{tenant.tenant_id}/data.db")
        target_db = instance_dir / "data.db"
        shutil.copy2(str(source_db), str(target_db))

        # 4. 生成 Docker Compose 配置
        compose = self._generate_docker_compose(tenant)
        (instance_dir / "docker-compose.yml").write_text(yaml.dump(compose))

        # 5. 启动实例
        instance = await self.instance_manager.start_instance(tenant)

        # 6. 验证实例运行正常
        if await self._health_check(instance):
            return MigrationResult(success=True)
        else:
            return MigrationResult(success=False, error="Instance health check failed")

        # 7. （手动确认）切换 DNS / 负载均衡指向新实例
        # 8. （手动确认）保留旧数据 7 天后清理
```

### 8.3 向下兼容

单租户模式自动检测并兼容：

```python
class LegacyCompatibilityLayer:
    """单租户 → 多租户向下兼容层"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.is_multitenant = (base_path / "tenants").exists()

    def get_storage_path(self) -> Path:
        """获取存储路径（兼容单租户）"""
        if self.is_multitenant:
            ctx = get_current_tenant_context()
            if ctx:
                return self.base_path / "tenants" / ctx.tenant.tenant_id

        # 回退：单租户旧路径
        return self.base_path

    def migrate_legacy_data(self) -> int:
        """将单租户数据迁移到默认租户"""
        if self.is_multitenant:
            legacy_paths = [
                (self.base_path / "memory", "memories"),
                (self.base_path / "sessions", "sessions"),
                (self.base_path / "skills", "skills"),
                (self.base_path / "config.yaml", "configs/config.yaml"),
            ]

            default_tenant_id = "tenant-legacy"
            target = self.base_path / "tenants" / default_tenant_id
            target.mkdir(parents=True, exist_ok=True)

            migrated = 0
            for src, rel_dst in legacy_paths:
                if src.exists():
                    dst = target / rel_dst
                    if src.is_file():
                        shutil.copy2(str(src), str(dst))
                    else:
                        shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
                    migrated += 1
            return migrated
        return 0
```

---

## 9. API 设计

### 9.1 租户管理 API

```
Base URL: /api/v1/admin/tenants

GET    /api/v1/admin/tenants                          # 列出所有租户（分页）
POST   /api/v1/admin/tenants                          # 创建租户
GET    /api/v1/admin/tenants/{tenant_id}              # 获取租户详情
PUT    /api/v1/admin/tenants/{tenant_id}              # 更新租户配置
DELETE /api/v1/admin/tenants/{tenant_id}              # 删除租户（软删除）
POST   /api/v1/admin/tenants/{tenant_id}/suspend      # 暂停租户
POST   /api/v1/admin/tenants/{tenant_id}/activate     # 激活租户
POST   /api/v1/admin/tenants/{tenant_id}/migrate      # 迁移隔离策略
```

**创建租户请求体**：

```json
{
    "name": "娄底市生态环境局",
    "tier": "enterprise",
    "isolation_strategy": "pool",
    "departments": [
        {"name": "环评审批科", "dept_type": "business"},
        {"name": "消防预警科", "dept_type": "business"},
        {"name": "污染监控科", "dept_type": "business"}
    ],
    "allowed_providers": ["qwen", "glm"],
    "rate_limits": {
        "requests_per_minute": 200,
        "tokens_per_day": 50000000
    },
    "admin_user": {
        "username": "admin",
        "password": "initial_password_change_required",
        "display_name": "系统管理员",
        "phone": "13800138000"
    }
}
```

### 9.2 用户管理 API

```
Base URL: /api/v1/tenants/{tenant_id}/users

GET    /api/v1/tenants/{tenant_id}/users                  # 列出用户（分页）
POST   /api/v1/tenants/{tenant_id}/users                  # 创建用户
GET    /api/v1/tenants/{tenant_id}/users/{user_id}        # 获取用户详情
PUT    /api/v1/tenants/{tenant_id}/users/{user_id}        # 更新用户
DELETE /api/v1/tenants/{tenant_id}/users/{user_id}        # 删除用户
POST   /api/v1/tenants/{tenant_id}/users/{user_id}/disable  # 禁用用户
POST   /api/v1/tenants/{tenant_id}/users/{user_id}/enable   # 启用用户

# 部门管理
GET    /api/v1/tenants/{tenant_id}/departments             # 列出部门
POST   /api/v1/tenants/{tenant_id}/departments             # 创建部门
PUT    /api/v1/tenants/{tenant_id}/departments/{dept_id}   # 更新部门
DELETE /api/v1/tenants/{tenant_id}/departments/{dept_id}   # 删除部门
```

### 9.3 数据导出 API

```
POST   /api/v1/tenants/{tenant_id}/export                  # 导出租户所有数据
GET    /api/v1/tenants/{tenant_id}/exports/{export_id}     # 查询导出状态
GET    /api/v1/tenants/{tenant_id}/exports/{export_id}/download  # 下载导出文件
```

**导出格式**：

```json
// 响应
{
    "export_id": "export-20260514-abc123",
    "tenant_id": "tenant-loudi-epb",
    "status": "processing",
    "formats": ["json", "csv"],
    "includes": {
        "sessions": true,
        "memories": true,
        "skills": true,
        "knowledge": true,
        "configs": true,
        "logs": true
    },
    "estimated_size": "45MB",
    "created_at": "2026-05-14T10:00:00Z",
    "download_url": null  // 完成后填充
}
```

### 9.4 租户级 API（业务 API 自动注入）

```
# 以下 API 由 TenantAwareMiddleware 自动注入租户上下文
# 无需在 URL 中显式指定 tenant_id

GET    /api/v1/sessions                           # 当前租户的会话列表
POST   /api/v1/sessions                           # 创建会话
GET    /api/v1/sessions/{session_id}               # 获取会话详情
POST   /api/v1/sessions/{session_id}/messages      # 发送消息

GET    /api/v1/memories                           # 当前租户的记忆列表
POST   /api/v1/memories                           # 添加记忆
DELETE /api/v1/memories/{memory_id}               # 删除记忆

GET    /api/v1/skills                             # 当前租户的技能列表
POST   /api/v1/skills                             # 创建技能

GET    /api/v1/knowledge                          # 当前租户的知识库列表
POST   /api/v1/knowledge                          # 上传知识文档
```

---

## 10. 实现计划

### 10.1 工作量估算

| 模块 | 子任务 | 预估人天 | 依赖 |
|------|--------|:--------:|:----:|
| **P0：基础框架** | | **15** | |
| | 10.1 租户数据模型定义 | 2 | 无 |
| | 10.2 租户上下文（ContextVar） | 1 | 10.1 |
| | 10.3 租户管理器（CRUD） | 3 | 10.1 |
| | 10.4 POOL 策略存储实现 | 3 | 10.2 |
| | 10.5 租户路由中间件 | 2 | 10.2, 10.4 |
| | 10.6 向下兼容层 | 2 | 10.2 |
| | 10.7 单元测试 | 2 | 全部 |
| **P1：隔离策略** | | **15** | |
| | 10.8 BUCKET 策略实现 | 4 | 10.4 |
| | 10.9 租户数据库管理器 | 3 | 10.8 |
| | 10.10 RBAC 权限模型 | 3 | 10.1 |
| | 10.11 租户管理 API | 3 | 10.3 |
| | 10.12 用户管理 API | 2 | 10.10 |
| **P2：增强功能** | | **10** | |
| | 10.13 S3 存储后端 | 2 | 10.4 |
| | 10.14 POOL→BUCKET 迁移工具 | 3 | 10.8 |
| | 10.15 数据导出 API | 2 | 10.3 |
| | 10.16 审计日志集成 | 3 | 10.10 |
| **P3：高级功能** | | **10** | |
| | 10.17 INSTANCE 策略（Docker） | 5 | 10.8 |
| | 10.18 BUCKET→INSTANCE 迁移 | 3 | 10.17 |
| | 10.19 性能基准测试 | 2 | 全部 |

**总计预估：50 人天**

### 10.2 里程碑

```
M1（第 1-2 周）    M2（第 3-4 周）    M3（第 5-6 周）    M4（第 7-8 周）
╔════════════════╗ ╔════════════════╗ ╔════════════════╗ ╔════════════════╗
║ 基础框架 (P0)  ║ ║ 隔离策略 (P1)  ║ ║ 增强功能 (P2)  ║ ║ 高级功能 (P3)  ║
╠════════════════╣ ╠════════════════╣ ╠════════════════╣ ╠════════════════╣
║ • 数据模型     ║ ║ • BUCKET 实现 ║ ║ • S3 后端     ║ ║ • INSTANCE    ║
║ • ContextVar   ║ ║ • RBAC        ║ ║ • 迁移工具    ║ ║   实现        ║
║ • POOL 策略    ║ ║ • 管理 API    ║ ║ • 数据导出    ║ ║ • 迁移验证    ║
║ • 中间件       ║ ║               ║ ║ • 审计日志    ║ ║ • 基准测试    ║
║ • 向下兼容     ║ ║               ║ ║               ║ ║               ║
╚════════════════╝ ╚════════════════╝ ╚════════════════╝ ╚════════════════╝
  ！: 可发布 v1.0     ？: 内部可用        ！: 生产可用          ？: 增强可用
```

### 10.3 验收标准

| 里程碑 | 验收条件 |
|--------|----------|
| **M1** | 现有单租户代码无需修改即可运行；通过 ContextVar 可正确获取租户上下文；POOL 策略下数据按租户路径存储隔离 |
| **M2** | BUCKET 策略可独立工作；RBAC 权限正确拦截越权操作；管理 API 可完成租户 CRUD |
| **M3** | S3 存储读写正确；POOL→BUCKET 迁移工具校验通过；审计日志涵盖所有敏感操作 |
| **M4** | INSTANCE 策略可自动编排 Docker 实例；性能基准测试达到目标；端到端集成测试通过 |

---

## 附录 A：与现有代码的集成点

| 现有文件 | 改造内容 | 改造量 |
|----------|----------|:------:|
| `src/opentaiji/memory/session.py` | `SessionMemory.__init__` 接受 `TenantContext`，路径改为租户感知 | 小 |
| `src/opentaiji/learning/loop.py` | `HonchoMemory` 存储路径改为租户感知；`SelfImprovingLoop.learn_from_interaction` 注入 `tenant_id` | 中 |
| `src/opentaiji/skills/hub.py` | `SkillManager` 存储路径改为租户感知 | 小 |
| `src/opentaiji/providers/` | 无改造（Provider 调用方控制 API Key） | 无 |
| `src/opentaiji/events/bus.py` | 事件中增加 `tenant_id` 字段 | 小 |
| `src/opentaiji/hitl/` | 审批工作流增加 `tenant_id` 上下文 | 中 |
| `src/opentaiji/wfgy/verifier.py` | 无改造（验证器无状态） | 无 |

## 附录 B：租户 ID 生成规则

```
格式: tenant-{prefix}-{random_suffix}
示例: tenant-loudi-epb-a3b2c1

规则:
- prefix: 租户英文标识（2-20 个字符，小写字母 + 连字符）
- random_suffix: 6 位随机小写字母+数字
- 总长度 <= 48 字符
```

## 附录 C：参考来源

- Hermes Agent 多租户设计：`deliverables/05-hermes-agent-analysis.md` 第 3 节
- 技术可行性评估：`deliverables/06-technical-feasibility-assessment.md` 第 2.12 节（整合点 K）
- 现有 SessionMemory：`src/opentaiji/memory/session.py`
- 现有 HonchoMemory / SelfImprovingLoop：`src/opentaiji/learning/loop.py`
