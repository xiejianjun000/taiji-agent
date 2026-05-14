# 插件系统设计文档 > 版本: 1.0.0 > 日期: 2026-05-14 > 状态: 初稿 --- ## 目录 1. [设计目标](#1-设计目标) 2. [Plugin 接口定义](#2-plugin-接口定义) 3. [生命周期管理](#3-生命周期管理) 4. [Plugin Loader 设计](#4-plugin-loader-设计) 5. [Taiji Verify Plugin 设计](#5-taiji-verify-plugin-设计) 6. [GovMCP Plugin 设计](#6-govmcp-plugin-设计) 7. [插件间依赖管理](#7-插件间依赖管理) 8. [安全沙箱](#8-安全沙箱) 9. [配置与部署](#9-配置与部署) 10. [实现计划](#10-实现计划) --- ## 1. 设计目标 ### 1.1 解决的问题 Taiji Agent 当前没有标准的插件系统，导致以下问题： | 问题 | 说明 | |------|------| | **功能耦合** | Verify 验证逻辑、GovMCP 政务能力与核心 Agent 代码耦合，难以独立开发和测试 | | **扩展困难** | 新增政务能力（如审批流程、环保监测）需要修改核心代码 | | **部署笨重** | 无法按需加载功能模块，所有功能必须一起部署 | | **缺少隔离** | 插件之间、插件与核心之间没有明确的边界和隔离机制 | | **生命周期缺失** | 没有统一的激活/停用/热加载机制 | ### 1.2 设计原则 | 原则 | 说明 | |------|------| | **接口兼容** | Python 版 Plugin 接口与 Harness TypeScript 版保持概念一致（`activate`/`deactivate` + `PluginContext`） | | **声明式配置** | 插件使用 YAML 描述自身信息（ID、版本、依赖、权限、配置 schema） | | **松耦合** | 插件通过 EventBus 与核心交互，不直接依赖核心内部实现 | | **渐进增强** | 从静态加载起步，逐步支持动态热插拔、安全沙箱 | | **可观测** | 每个插件暴露健康检查、指标采集接口 | | **安全优先** | 插件运行在受限环境中，权限最小化原则 | ### 1.3 与 Harness Plugin 的兼容性 | 维度 | Harness (TypeScript) | Taiji Agent (Python) | 兼容策略 | |------|---------------------|----------------------|----------| | 核心接口 | `activate(ctx)`, `deactivate()` | 同名方法 | 直接映射 | | 上下文 | `PluginContext` | `PluginContext` | 扩展增加 `event_bus`、`data_dir`、`logger` | | 声明字段 | `tools`, `hooks`, `providers`, `ui` | 同名字段 | 增加 `config_schema`, `dependencies`, `permissions` | | 加载方式 | `import()` 动态导入 | `importlib.import_module()` | Python 原生支持 | | 构建工具 | npm/pnpm | pip/setuptools | Python 包管理 | | 配置文件 | `harness.config.yaml` | `plugin.yaml` | 新增 YAML 格式 | **跨语言桥接**：TypeScript 端的 Harness 插件可以远程桥接到 Taiji Agent Plugin 系统（通过 gRPC Gateway Plugin），实现跨语言互操作。 --- ## 2. Plugin 接口定义 ### 2.1 核心接口 ```python from abc import ABC, abstractmethod from dataclasses import dataclass, field from pathlib import Path from typing import Any, Optional from enum import Enum, auto class PluginHealth(Enum): HEALTHY = auto() DEGRADED = auto() UNHEALTHY = auto() ERROR = auto() class PluginState(Enum): REGISTERED = "registered" LOADING = "loading" LOADED = "loaded" ACTIVATING = "activating" ACTIVE = "active" DEACTIVATING = "deactivating" DEACTIVATED = "deactivated" ERROR = "error" class ToolDefinition: """工具定义 - 与 Harness ToolDefinition 兼容""" name: str description: str parameters: dict # JSON Schema handler: callable class HookRegistration: """事件钩子注册 - 与 Harness AnyHookRegistration 兼容""" event: str # 事件名称 (如 "tool:request") handler: callable # async handler(data) -> data | {"abort": True} priority: int = 100 # 越小越优先 @dataclass class PluginContext: """插件上下文 - 扩展自 Harness PluginContext""" plugin_id: str event_bus: "EventBus" # 事件总线引用 config: dict # 插件配置（来自 YAML 或运行时注入） data_dir: Path # 插件私有数据目录 logger: "Logger" # 带插件前缀的日志记录器 state_manager: "AgentState" # Agent 状态管理器 store: "PersistenceStore" # 持久化存储 # 可选字段 tool_registry: Optional["ToolRegistry"] = None secret_store: Optional["SecretStore"] = None @dataclass class PluginDependency: """插件依赖声明""" plugin_id: str version_spec: str # 语义版本号约束，如 ">=1.0.0, <2.0.0" optional: bool = False @dataclass class PluginMetadata: """插件元数据""" id: str name: str version: str description: str = "" author: str = "" homepage: str = "" license: str = "" dependencies: list[PluginDependency] = field(default_factory=list) permissions: list[str] = field(default_factory=list) # 所需权限列表 config_schema: Optional[dict] = None # JSON Schema min_agent_version: str = "1.0.0" tags: list[str] = field(default_factory=list) class Plugin(ABC): """插件基类 - 兼容 Harness 的 HarnessPlugin 接口""" # ── 元数据（由 YAML 或子类定义） ── metadata: PluginMetadata # ── 能力声明（与 HarnessPlugin 兼容） ── tools: list[ToolDefinition] = [] hooks: list[HookRegistration] = [] ui_contributions: Optional[dict] = None def __init__(self, metadata: PluginMetadata): self.metadata = metadata self._state = PluginState.REGISTERED self._context: Optional[PluginContext] = None # ── 生命周期方法 ── @abstractmethod async def activate(self, ctx: PluginContext) -> None: """ 激活插件。 - 注册工具、钩子 - 初始化资源（数据库连接、网络客户端、文件句柄） - 在 activate() 中抛异常将导致状态回退到 ERROR """ pass @abstractmethod async def deactivate(self) -> None: """ 停用插件。 - 释放资源 - 取消事件监听 - 关闭网络连接 """ pass # ── 运行时接口 ── async def health_check(self) -> PluginHealth: """ 健康检查。 默认返回 HEALTHY，子类可重写以检查依赖服务可用性。 """ return PluginHealth.HEALTHY async def get_metrics(self) -> dict[str, Any]: """ 获取插件指标。 返回 Prometheus 兼容的键值对。 """ return {} # ── 配置接口 ── def get_config(self, key: str, default: Any = None) -> Any: """获取配置值""" if self._context is None: return default return self._context.config.get(key, default) def set_config(self, key: str, value: Any) -> None: """更新配置值""" if self._context is not None: self._context.config[key] = value # ── 内部管理 ── @property def state(self) -> PluginState: return self._state @state.setter def state(self, value: PluginState): self._state = value if self._context and self._context.logger: self._context.logger.info(f"State changed to: {value.value}") ``` ### 2.2 配置验证接口 ```python from jsonschema import validate, ValidationError class ConfigurablePlugin(Plugin): """支持配置 Schema 验证的插件基类""" def validate_config(self, config: dict) -> list[str]: """ 验证配置是否符合 metadata.config_schema。 返回错误列表，空列表表示验证通过。 """ if self.metadata.config_schema is None: return [] errors = [] try: validate(instance=config, schema=self.metadata.config_schema) except ValidationError as e: errors.append(str(e)) return errors ``` ### 2.3 日志接口 ```python import logging class PluginLogger: """带插件前缀的日志记录器""" def __init__(self, plugin_id: str): self._logger = logging.getLogger(f"plugin.{plugin_id}") self._prefix = f"[{plugin_id}]" def debug(self, message: str, *args, **kwargs): self._logger.debug(f"{self._prefix} {message}", *args, **kwargs) def info(self, message: str, *args, **kwargs): self._logger.info(f"{self._prefix} {message}", *args, **kwargs) def warn(self, message: str, *args, **kwargs): self._logger.warning(f"{self._prefix} {message}", *args, **kwargs) def error(self, message: str, *args, **kwargs): self._logger.error(f"{self._prefix} {message}", *args, **kwargs) ``` --- ## 3. 生命周期管理 ### 3.1 状态机 ``` ┌──────────────────────────────────────┐ │ 插件生命周期状态机 │ └──────────────────────────────────────┘ +-----------+ | REGISTERED| ◄── 发现但未加载 +-----+-----+ │ load()│ ▼ +-----------+ ┌─────►| LOADING | ──── 动态导入模块 │ +-----+-----+ │ │ │ 成功 │ 失败 │ ▼ ▼ │ +-----------+ +-------+ │ | LOADED | | ERROR | │ +-----+-----+ +---+---+ │ │ ▲ │ activate()│ │ │ ▼ │ │ +-----------+ │ │ |ACTIVATING |──────┘ activate() 抛异常 │ +-----+-----+ │ │ │ 成功 │ │ ▼ │ +-----------+ │ ┌───►| ACTIVE | ◄── 正常运行 │ │ +-----+-----+ │ │ │ │ │deactivate()│ │ │ ▼ │ │ +-----------+ │ ├────|DEACTIVAT- | ──── deactivate() 抛异常不影响卸载 │ │ |ING | │ │ +-----+-----+ │ │ │ │ │ ▼ │ │ +-----------+ │ └────|DEACTIVATED| ──── 可重新激活或卸载 │ +-----+-----+ │ │ │ uninstall│ │ ▼ │ (移除) │ │ health_check 失败 → DEGRADED 或 UNHEALTHY │ +-----------+ │ | ACTIVE | ── health_check() → DEGRADED │ |(DEGRADED) | │ +-----------+ │ │ │ 重试成功 │ 重试失败 │ ▼ ▼ │ +-----------+ +-----------+ │ | ACTIVE | | DEACTIVAT- | │ +-----------+ |ING→ERROR | │ +-----------+ ``` ### 3.2 状态转换定义 | 当前状态 | 操作 | 下一状态 | 说明 | |----------|------|----------|------| | `REGISTERED` | `load()` | `LOADING` | Loader 开始导入模块 | | `LOADING` | 导入成功 | `LOADED` | 模块已导入，但未激活 | | `LOADING` | 导入失败 | `ERROR` | 导入异常或模块不合法 | | `LOADED` | `activate()` | `ACTIVATING` | 开始执行激活逻辑 | | `ACTIVATING` | 激活成功 | `ACTIVE` | 正常服务状态 | | `ACTIVATING` | 激活失败 | `ERROR` | 清理已分配资源后转入 ERROR | | `ACTIVE` | `deactivate()` | `DEACTIVATING` | 开始执行停用逻辑 | | `ACTIVE` | health_check 失败 | `ACTIVE(DEGRADED)` | 标记降级，不影响已有请求 | | `ACTIVE(DEGRADED)` | 自动重试成功 | `ACTIVE` | 恢复健康 | | `ACTIVE(DEGRADED)` | 自动重试超限 | `DEACTIVATING` | 触发停用 | | `DEACTIVATING` | 完成 | `DEACTIVATED` | 停用完成，可重激活 | | `DEACTIVATING` | 发生错误 | `ERROR` | 停用过程异常 | | `DEACTIVATED` | `activate()` | `ACTIVATING` | 重新激活 | | `DEACTIVATED` | `uninstall()` | — | 从管理器中移除 | | `ERROR` | `reset()` | `REGISTERED` | 重置后重新注册 | ### 3.3 生命周期管理器接口 ```python class PluginLifecycleManager: """ 插件生命周期管理器。 负责状态转换的原子性、异常处理和事件通知。 """ async def load(self, plugin: Plugin) -> None: """加载插件：REGISTERED → LOADED""" async def activate(self, plugin: Plugin) -> None: """激活插件：LOADED → ACTIVE""" async def deactivate(self, plugin: Plugin) -> None: """停用插件：ACTIVE → DEACTIVATED""" async def uninstall(self, plugin: Plugin) -> None: """卸载插件：DEACTIVATED → 移除""" async def reload(self, plugin: Plugin) -> None: """热重载：ACTIVE → LOADING → ACTIVE""" async def get_state(self, plugin_id: str) -> PluginState: """查询插件当前状态""" async def list_states(self) -> dict[str, PluginState]: """列出所有插件状态""" ``` 状态转换过程中自动发射 EventBus 事件： ```python # Loader emits lifecycle events event_bus.emit("plugin:before_load", {"plugin_id": plugin_id}) event_bus.emit("plugin:after_load", {"plugin_id": plugin_id, "success": True}) event_bus.emit("plugin:before_activate", {"plugin_id": plugin_id}) event_bus.emit("plugin:after_activate", {"plugin_id": plugin_id, "success": True}) event_bus.emit("plugin:error", {"plugin_id": plugin_id, "error": str(err)}) ``` --- ## 4. Plugin Loader 设计 ### 4.1 整体架构 ``` ┌──────────────────────────────────────────────────────────────────────┐ │ PluginLoader │ │ │ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────────┐ │ │ │ PluginScanner │ │ Dependency │ │ PluginRegistry │ │ │ │ • 目录扫描 │ │ Resolver │ │ • ID → Plugin 映射 │ │ │ │ • YAML 解析 │ │ • 拓扑排序 │ │ • 状态跟踪 │ │ │ │ • 热插拔 Watch│ │ • 循环检测 │ │ • 版本索引 │ │ │ └──────┬───────┘ │ • 版本匹配 │ └──────────────────────────────┘ │ │ │ └──────┬───────┘ │ │ ▼ ▼ │ │ ┌──────────────────────────────────────────────────────────────────┐ │ │ │ PluginFactory │ │ │ │ • importlib.import_module() 动态导入 │ │ │ │ • instantiate 插件实例 │ │ │ │ • 注入 PluginContext │ │ │ └──────────────────────────────────────────────────────────────────┘ │ │ │ │ ┌──────────────────────────────────────────────────────────────────┐ │ │ │ PluginSandbox (可选) │ │ │ │ • subprocess 隔离 / Docker 隔离 │ │ │ │ • 资源限制 (CPU/Memory/IO) │ │ │ │ • 权限检查 (permissions ACL) │ │ │ └──────────────────────────────────────────────────────────────────┘ │ └──────────────────────────────────────────────────────────────────────┘ ``` ### 4.2 PluginLoader 核心类 ```python import importlib import os import yaml from pathlib import Path class PluginLoader: """ 插件加载器。 负责发现、解析、验证、加载、激活插件。 """ def __init__( self, plugin_dirs: list[Path] | None = None, event_bus: "EventBus" = None, registry: "PluginRegistry" = None, lifecycle: "PluginLifecycleManager" = None, enable_watchdog: bool = False, ): self.plugin_dirs = plugin_dirs or [Path.cwd() / "plugins"] self.event_bus = event_bus self.registry = registry or PluginRegistry() self.lifecycle = lifecycle or PluginLifecycleManager() self._watcher: Optional[FileWatcher] = None self._enable_watchdog = enable_watchdog # 自动发现祖先目录的 plugins/ 文件夹 self._discover_ancestor_plugins() def _discover_ancestor_plugins(self): """向上遍历目录树，发现 plugins/ 文件夹""" dir_current = Path.cwd() while True: parent = dir_current.parent if parent == dir_current: break candidate = parent / "plugins" if candidate not in self.plugin_dirs and candidate.is_dir(): self.plugin_dirs.append(candidate) dir_current = parent async def load_all(self) -> list[Plugin]: """ 扫描所有插件目录，解析依赖，按拓扑序加载和激活。 """ # Step 1: 扫描并解析所有插件 discovered = self._scan_all() if not discovered: return [] # Step 2: 依赖解析 + 拓扑排序 ordered = self._resolve_dependencies(discovered) # Step 3: 按序加载 loaded: list[Plugin] = [] for meta in ordered: plugin = await self._load_single(meta) if plugin: loaded.append(plugin) # Step 4: 启动热插拔文件监听 if self._enable_watchdog: self._start_watchdog() return loaded def _scan_all(self) -> list[PluginMetadata]: """扫描所有插件目录，返回元数据列表""" discovered = [] for plugin_dir in self.plugin_dirs: if not plugin_dir.is_dir(): continue for entry in sorted(plugin_dir.iterdir()): if not entry.is_dir(): continue yaml_path = entry / "plugin.yaml" if not yaml_path.exists(): continue meta = self._parse_yaml(yaml_path) if meta: meta._plugin_dir = entry # 存储目录路径 discovered.append(meta) return discovered def _parse_yaml(self, yaml_path: Path) -> PluginMetadata | None: """解析 plugin.yaml 文件""" try: with open(yaml_path, "r", encoding="utf-8") as f: data = yaml.safe_load(f) deps = [] for dep in data.get("dependencies", []): deps.append(PluginDependency( plugin_id=dep["id"], version_spec=dep.get("version", "*"), optional=dep.get("optional", False), )) return PluginMetadata( id=data["id"], name=data.get("name", data["id"]), version=data["version"], description=data.get("description", ""), author=data.get("author", ""), homepage=data.get("homepage", ""), license=data.get("license", ""), dependencies=deps, permissions=data.get("permissions", []), config_schema=data.get("config_schema"), min_agent_version=data.get("min_agent_version", "1.0.0"), tags=data.get("tags", []), ) except Exception as e: print(f"Failed to parse {yaml_path}: {e}") return None async def _load_single(self, meta: PluginMetadata) -> Plugin | None: """加载单个插件""" if meta.id in self.registry: return self.registry.get(meta.id) try: # 确定模块入口 entry = self._resolve_entry(meta) if not entry: return None # 动态导入 spec = importlib.util.spec_from_file_location(meta.id, entry) if not spec or not spec.loader: raise ImportError(f"Cannot load plugin module: {entry}") module = importlib.util.module_from_spec(spec) spec.loader.exec_module(module) # 查找插件类 plugin_cls = self._find_plugin_class(module) if not plugin_cls: raise ImportError(f"No Plugin subclass found in {entry}") # 实例化 plugin = plugin_cls(meta) self.registry.register(plugin) # 加载（但不激活） await plugin.load(self._create_context(meta)) return plugin except Exception as e: print(f"Failed to load plugin {meta.id}: {e}") return None def _resolve_entry(self, meta: PluginMetadata) -> Path | None: """解析插件入口文件（main 字段或默认 main.py）""" plugin_dir = getattr(meta, "_plugin_dir", None) if not plugin_dir: return None # 优先使用 YAML 中定义的 main yaml_path = plugin_dir / "plugin.yaml" if yaml_path.exists(): with open(yaml_path, "r") as f: data = yaml.safe_load(f) main = data.get("main", "main.py") else: main = "main.py" entry = plugin_dir / main return entry if entry.exists() else None def _resolve_dependencies( self, plugins: list[PluginMetadata] ) -> list[PluginMetadata]: """ 依赖解析 + 拓扑排序。 检查循环依赖、版本冲突，返回按依赖顺序排列的列表。 """ resolver = DependencyResolver(plugins) return resolver.resolve() def _start_watchdog(self): """启动文件监听，支持热插拔""" from watchdog.observers import Observer self._watcher = FileWatcher(self.plugin_dirs, self._on_plugin_changed) self._watcher.start() ``` ### 4.3 扫描机制 | 扫描策略 | 说明 | |----------|------| | **目录扫描** | 遍历 `plugins/` 下所有子目录，检查 `plugin.yaml` 是否存在 | | **祖先目录扫描** | 向上遍历目录树，发现所有 `plugins/` 目录（支持 monorepo） | | **包索引扫描** | 可选：从已安装的 Python 包中发现带有 `taiji-plugin` entry point 的包 | 支持三种发现模式： ``` # 1. 本地目录插件 plugins/ taiji-verify/ plugin.yaml main.py ... # 2. Python 包插件（通过 entry_points） pip install taiji-plugin-govmcp # 自动发现 entry_points 中的 "taiji.plugins" 组 # 3. 远程插件（按需加载） plugins/ remote-plugins.yaml # 定义远程插件地址，惰性加载 ``` ### 4.4 YAML 声明式配置 ```yaml # plugin.yaml id: taiji-verify name: Taiji Verify version: "1.0.0" description: "太极验证引擎 - 阴阳距 + 北辰编译器 + 坤守/乾进/复归/巽调" author: "Taiji Team" homepage: "https://taiji-agent.example.com/plugins/verify" license: "MIT" main: "main.py" # 入口文件，默认为 main.py min_agent_version: "1.0.0" # 依赖 dependencies: - id: event-bus version: ">=1.0.0" - id: embedding-service version: ">=0.5.0" optional: true # 可选依赖 # 所需权限 permissions: - "eventbus:subscribe:tool:request" - "eventbus:subscribe:llm:response" - "eventbus:subscribe:prompt:assemble" - "eventbus:emit:verify:*" - "storage:read:verify-rules" - "storage:write:verify-results" # 配置 Schema（JSON Schema） config_schema: type: object required: - mode properties: mode: type: string enum: [strict, moderate, permissive] default: moderate min_delta_s: type: number minimum: 0.0 maximum: 1.0 default: 0.3 enable_bbmc: type: boolean default: true enable_bbpf: type: boolean default: true # 默认配置 config: mode: moderate min_delta_s: 0.3 enable_bbmc: true enable_bbpf: true # 标签 tags: - verify - safety - compliance ``` ### 4.5 依赖解析 `DependencyResolver` 类实现： ```python class DependencyResolver: def __init__(self, plugins: list[PluginMetadata]): self.plugins = {p.id: p for p in plugins} def resolve(self) -> list[PluginMetadata]: """ Kahn 拓扑排序 + 循环依赖检测 + 版本冲突检测。 返回按依赖顺序排列的列表（前置依赖在前）。 """ # Step 1: 构建入度表和邻接表 in_degree: dict[str, int] = {p.id: 0 for p in self.plugins.values()} adj: dict[str, list[str]] = {p.id: [] for p in self.plugins.values()} for plugin in self.plugins.values(): for dep in plugin.dependencies: if dep.plugin_id in self.plugins: adj.setdefault(dep.plugin_id, []).append(plugin.id) in_degree[plugin.id] = in_degree.get(plugin.id, 0) + 1 # Step 2: Kahn 拓扑排序 queue = deque([pid for pid, deg in in_degree.items() if deg == 0]) ordered = [] while queue: pid = queue.popleft() ordered.append(self.plugins[pid]) for neighbor in adj.get(pid, []): in_degree[neighbor] -= 1 if in_degree[neighbor] == 0: queue.append(neighbor) # Step 3: 循环依赖检测 if len(ordered) != len(self.plugins): unresolved = set(self.plugins.keys()) - {p.id for p in ordered} raise CircularDependencyError(f"Circular dependency detected: {unresolved}") # Step 4: 版本冲突检测 self._check_version_conflicts(ordered) return ordered def _check_version_conflicts(self, plugins: list[PluginMetadata]): """检查同一插件的多个版本是否存在冲突""" version_map: dict[str, set[str]] = {} for p in plugins: version_map.setdefault(p.id, set()).add(p.version) for pid, versions in version_map.items(): if len(versions) > 1: raise VersionConflictError( f"Plugin {pid} has multiple versions: {versions}" ) ``` ### 4.6 版本冲突检测 使用语义化版本号（SemVer）兼容性检查： ```python import semver def check_version_compatibility( actual_version: str, version_spec: str ) -> bool: """ 检查实际版本是否满足版本约束。 version_spec 示例: ">=1.0.0", ">=1.0.0, <2.0.0", "~1.2.3", "^1.0.0" """ try: actual = semver.Version.parse(actual_version) for constraint in version_spec.split(","): constraint = constraint.strip() if constraint.startswith(">="): if actual < semver.Version.parse(constraint[2:]): return False elif constraint.startswith("<="): if actual > semver.Version.parse(constraint[2:]): return False elif constraint.startswith(">"): if actual <= semver.Version.parse(constraint[1:]): return False elif constraint.startswith("<"): if actual >= semver.Version.parse(constraint[1:]): return False elif constraint.startswith("=="): if actual != semver.Version.parse(constraint[2:]): return False elif constraint.startswith("^"): # ^1.2.3 → >=1.2.3, <2.0.0 lower = semver.Version.parse(constraint[1:]) upper = semver.Version(lower.major + 1, 0, 0) if not (lower <= actual < upper): return False elif constraint.startswith("~"): # ~1.2.3 → >=1.2.3, <1.3.0 lower = semver.Version.parse(constraint[1:]) upper = semver.Version(lower.major, lower.minor + 1, 0) if not (lower <= actual < upper): return False elif constraint == "*": continue return True except Exception: return False ``` ### 4.7 热插拔（文件监听 Watchdog） ```python from watchdog.observers import Observer from watchdog.events import FileSystemEventHandler class PluginFileHandler(FileSystemEventHandler): """监听插件目录变化，触发热加载/重载/卸载""" def __init__(self, loader: "PluginLoader", plugin_dir: Path): self.loader = loader self.plugin_dir = plugin_dir def on_created(self, event): """新插件加入 → 尝试加载""" if event.is_directory and (event.src_path / "plugin.yaml").exists(): asyncio.create_task(self.loader.load_single_from_dir(event.src_path)) def on_modified(self, event): """插件文件修改 → 热重载""" if event.src_path.endswith((".py", ".yaml", ".yml")): asyncio.create_task(self.loader.reload_plugin_by_path(event.src_path)) def on_deleted(self, event): """插件目录删除 → 自动停用""" if event.is_directory: plugin_id = Path(event.src_path).name asyncio.create_task(self.loader.unload_plugin(plugin_id)) class FileWatcher: """文件系统监听器""" def __init__( self, plugin_dirs: list[Path], on_change_handler: callable ): self._observer = Observer() for plugin_dir in plugin_dirs: handler = PluginFileHandler(on_change_handler, plugin_dir) self._observer.schedule(handler, str(plugin_dir), recursive=True) def start(self): self._observer.start() def stop(self): self._observer.stop() self._observer.join() ``` --- ## 5. Taiji Verify Plugin 设计 ### 5.1 Plugin 配置 (YAML) ```yaml # plugins/taiji-verify/plugin.yaml id: taiji-verify name: Taiji Verify Engine version: "1.0.0" description: "太极验证引擎 — 基于WFGY 5.0协议的验证与合规系统" author: "Taiji Team" main: "main.py" dependencies: - id: event-bus version: ">=1.0.0" - id: embedding-service version: ">=0.5.0" optional: true permissions: - "eventbus:subscribe:tool:request" - "eventbus:subscribe:llm:response" - "eventbus:subscribe:prompt:assemble" - "eventbus:emit:verify:*" - "storage:read:verify-rules" - "storage:write:verify-results" config_schema: type: object properties: mode: type: string enum: [strict, moderate, permissive] default: moderate min_delta_s: type: number minimum: 0.0 maximum: 1.0 default: 0.3 enable_bbmc: type: boolean default: true enable_bbpf: type: boolean default: true enable_bbcr: type: boolean default: false enable_bbam: type: boolean default: false config: mode: moderate min_delta_s: 0.3 enable_bbmc: true enable_bbpf: true enable_bbcr: false enable_bbam: false ``` ### 5.2 Hook 点（与 EventBus 集成） Taiji Verify Plugin 在以下事件点注入验证逻辑： | 事件 | 优先级 | 验证类型 | 说明 | |------|--------|----------|------| | `prompt:assemble` | 5 | 合规检查 | 检查 Prompt 是否包含敏感词、是否触发审核规则 | | `tool:request` | 10 | 操作验证 | 对每次工具调用做风险评估（阴阳距 ΔS 计算） | | `llm:response` | 10 | 输出校验 | 校验 LLM 输出是否合规、是否包含禁止内容 | | `feedback:request` | 10 | 审批验证 | 验证审批请求的完整性和合规性 | | `loop:iteration_start` | 5 | 循环控制 | 检测 agent 是否进入死循环或异常迭代 | ```python # plugins/taiji-verify/main.py from taiji.plugin import Plugin, PluginContext, HookRegistration, PluginHealth class TaijiVerifyPlugin(Plugin): """太极验证引擎插件""" tools = [ # 暴露验证管理工具 ToolDefinition(name="verify_check_rule", ...), ToolDefinition(name="verify_query_result", ...), ToolDefinition(name="verify_update_config", ...), ToolDefinition(name="verify_get_report", ...), ] hooks = [ HookRegistration(event="prompt:assemble", handler="on_prompt_assemble", priority=5), HookRegistration(event="tool:request", handler="on_tool_request", priority=10), HookRegistration(event="llm:response", handler="on_llm_response", priority=10), HookRegistration(event="feedback:request", handler="on_feedback_request", priority=10), HookRegistration(event="loop:iteration_start", handler="on_iteration_start", priority=5), ] async def activate(self, ctx: PluginContext) -> None: """ 激活验证引擎： 1. 加载验证规则库（阴阳距阈值、失败模式模板） 2. 初始化嵌入模型（用于语义相似度计算） 3. 注册验证工具和钩子 """ self.mode = ctx.config.get("mode", "moderate") self.min_delta_s = ctx.config.get("min_delta_s", 0.3) self._embedding_model = None # 初始化北辰编译器 self._compiler = BeichenCompiler() # 按需初始化各算法模块 if ctx.config.get("enable_bbmc", True): self._bbmc = 坤守(Kun Guard)(ctx) if ctx.config.get("enable_bbpf", True): self._bbpf = 乾进(Qian Advance)(ctx) if ctx.config.get("enable_bbcr", False): self._bbcr = 复归(Fu Return)(ctx) if ctx.config.get("enable_bbam", False): self._bbam = 巽调(Xun Tune)(ctx) ctx.logger.info(f"Taiji Verify activated in {self.mode} mode") async def deactivate(self) -> None: """释放嵌入模型、关闭向量索引""" self._embedding_model = None self._bbmc = None self._bbpf = None self._bbcr = None self._bbam = None async def health_check(self) -> PluginHealth: """检查嵌入模型和向量索引是否可用""" if self._embedding_model is None: return PluginHealth.DEGRADED return PluginHealth.HEALTHY # ── Hook handlers ── async def on_prompt_assemble(self, data: dict) -> dict: """ Prompt 合规检查。 检查敏感词、政策合规性。 在 strict 模式下，不合规的 prompt 会被阻止。 """ prompt = data.get("prompt", "") violations = self._check_prompt_compliance(prompt) if violations and self.mode == "strict": return {"abort": True, "reason": f"Prompt violates rules: {violations}"} return data async def on_tool_request(self, data: dict) -> dict: """ 工具调用验证 — 核心验证点。 使用阴阳距 ΔS 计算工具调用与预期意图的偏差。 偏差过大则拒绝或转人工审批。 """ tool_name = data.get("name", "") tool_args = data.get("args", {}) # 计算阴阳距 ΔS delta_s = await self._calculate_delta_s(tool_name, tool_args) if delta_s > self.min_delta_s: # 偏差过大 if self.mode == "strict": return {"abort": True, "reason": f"Tool call rejected: ΔS={delta_s:.3f} > threshold={self.min_delta_s}"} elif self.mode == "moderate": # 标记为需审批，不直接阻止 data["requires_approval"] = True data["verify_delta_s"] = delta_s return data return data async def on_llm_response(self, data: dict) -> dict: """校验 LLM 输出是否包含禁止内容""" content = data.get("content", "") violations = self._check_output_compliance(content) if violations: self._context.logger.warn(f"LLM output violations: {violations}") if self.mode == "strict": return {"abort": True, "reason": f"Output rejected: {violations}"} return data async def on_feedback_request(self, data: dict) -> dict: """审批请求验证""" feedback_type = data.get("type", "") feedback_data = data.get("data", {}) compliance = self._check_feedback_compliance(feedback_type, feedback_data) if not compliance["pass"]: return {"abort": True, "reason": compliance["reason"]} return data async def on_iteration_start(self, data: dict) -> dict: """循环控制：检测异常迭代""" iteration = data.get("iteration", 0) max_iterations = data.get("max_iterations", 50) if iteration > max_iterations * 0.9: self._context.logger.warn(f"Near max iterations: {iteration}/{max_iterations}") return data # ── 内部实现 ── async def _calculate_delta_s(self, tool_name: str, tool_args: dict) -> float: """ 阴阳距 ΔS 计算。 ΔS = 1 - cos(I, G) 其中 I 为意图向量，G 为目标向量。 """ # Step 1: 获取预期目标向量 G g = self._get_target_vector(tool_name) # Step 2: 计算实际意图向量 I i = await self._get_intent_vector(tool_name, tool_args) # Step 3: 计算余弦距离 cosine_sim = self._cosine_similarity(i, g) # ΔS = 1 - cos(I, G)，取值 [0, 2] return 1.0 - cosine_sim def _check_prompt_compliance(self, prompt: str) -> list[str]: """检查 prompt 合规性""" violations = [] # 基于规则的合规检查 for rule in self._compliance_rules: if rule.matches(prompt): violations.append(rule.description) return violations def _check_output_compliance(self, content: str) -> list[str]: """检查 LLM 输出合规性""" violations = [] for rule in self._output_rules: if rule.matches(content): violations.append(rule.description) return violations ``` ### 5.3 验证流水线 ``` Agent Loop 执行流 ═══════════════════ ┌─────────────┐ │ 用户输入 │ └──────┬──────┘ │ ▼ ┌──────────────────────────────────────────────────┐ │ ① Prompt 组装 │ │ └─ bus.emit("prompt:assemble") ───────────────┐ │ │ ├─ Verify Plugin (priority 5) │ │ │ │ └─ 合规检查 + 敏感词过滤 │ │ │ ├─ 其他 Plugin │ │ │ └─ 核心模块 │ │ └──────────────────────────────────────────────────┘ │ ▼ ┌──────────────────────────────────────────────────┐ │ ② LLM 调用 │ │ └─ bus.emit("llm:request") │ └──────────────────────────────────────────────────┘ │ ▼ ┌──────────────────────────────────────────────────┐ │ ③ LLM 响应 │ │ └─ bus.emit("llm:response") ─────────────────┐ │ │ ├─ Verify Plugin (priority 10) │ │ │ │ └─ 输出合规校验 │ │ │ └─ 核心模块 │ │ └──────────────────────────────────────────────────┘ │ ├── 无工具调用 ──► 返回最终结果 │ ▼ 有工具调用 ┌──────────────────────────────────────────────────┐ │ ④ 工具调用验证 │ │ └─ bus.emit("tool:request") ─────────────────┐ │ │ ├─ Verify Plugin (priority 10) │ │ │ │ ├─ 阴阳距 ΔS 计算 │ │ │ │ ├─ 坤守残差修正 (坤守(Kun Guard)) │ │ │ │ ├─ 乾进多路径扰动 (乾进(Qian Advance)) │ │ │ │ └─ 决定: 放行 / 审批 / 拒绝 │ │ │ └─ 核心模块 │ │ └──────────────────────────────────────────────────┘ │ ├── 通过 ──► 执行工具 ├── 需审批 ──► 进入 HITL 审批流程 └── 拒绝 ──► 返回错误信息 ``` ### 5.4 关键代码结构 ```python # plugins/taiji-verify/ # ├── plugin.yaml # ├── main.py # 插件入口 # ├── compiler/ # │ ├── __init__.py # │ └── beichen.py # 北辰编译器 # ├── verify/ # │ ├── __init__.py # │ ├── delta_s.py # 阴阳距 ΔS 计算 # │ ├── bbmc.py # 坤守 (坤守(Kun Guard)) # │ ├── bbpf.py # 乾进 (乾进(Qian Advance)) # │ ├── bbcr.py # 复归 (复归(Fu Return)) # │ └── bbam.py # 巽调 (巽调(Xun Tune)) # ├── rules/ # │ ├── __init__.py # │ ├── compliance.py # 合规规则 # │ └── failure_modes.py # 16种失败模式 # └── tools/ # ├── __init__.py # ├── manage_rules.py # └── query_results.py ``` --- ## 6. GovMCP Plugin 设计 ### 6.1 Plugin 配置 (YAML) ```yaml # plugins/taiji-govmcp/plugin.yaml id: taiji-govmcp name: GovMCP Integration version: "1.0.0" description: "政务 MCP 协议适配 — 国密加密 + 审批工作流 + 审计链 + 政务工具" author: "Taiji Team" main: "main.py" dependencies: - id: event-bus version: ">=1.0.0" - id: taiji-verify version: ">=1.0.0" optional: true permissions: - "eventbus:subscribe:feedback:*" - "eventbus:subscribe:tool:result" - "eventbus:emit:gov:*" - "eventbus:emit:audit:*" - "network:connect:gov-cloud" - "network:connect:gov-oa" - "storage:read:gov-config" - "storage:write:audit-log" - "crypto:sm4" - "crypto:sm3" config_schema: type: object required: - gov_cloud properties: gov_cloud: type: object properties: endpoint: type: string format: uri auth_token: type: string crypto_enabled: type: boolean default: true sm4_key: type: string description: "Base64 encoded SM4 key" approval: type: object properties: default_timeout: type: integer default: 3600 auto_approve_on_timeout: type: boolean default: false default_deny: type: boolean default: true audit_enabled: type: boolean default: true oa_integration: type: object properties: endpoint: type: string format: uri api_key: type: string config: gov_cloud: endpoint: "https://gov-cloud.example.com/mcp" crypto_enabled: true approval: default_timeout: 3600 auto_approve_on_timeout: false default_deny: true audit_enabled: true ``` ### 6.2 审批工作流集成 GovMCP Plugin 将 Harness 的 Human-in-the-Loop 系统与 GovMCP 的 `ApprovalFlow` 引擎对接： ``` ┌────────────────────────────────────────────────────────────────┐ │ Taiji Agent Runtime │ │ │ │ ┌──────────────────────┐ ┌────────────────────────────┐ │ │ │ Agent Loop │ │ GovMCP Plugin │ │ │ │ (ReAct) │ │ │ │ │ │ │ │ ┌──────────────────┐ │ │ │ │ feedback.confirm()────┼────┼─►│ GovApprovalAdapter│ │ │ │ │ feedback.review()─────┼────┼─►│ (Feedback │ │ │ │ │ feedback.form()───────┼────┼─►│ Adapter) │ │ │ │ └──────────────────────┘ │ └────────┬─────────┘ │ │ │ │ │ │ │ │ │ ┌────────▼─────────┐ │ │ │ │ │ApprovalFlow Engine│ │ │ │ │ │ (多级审批链) │ │ │ │ │ └────────┬─────────┘ │ │ │ │ │ │ │ │ │ ┌────────▼─────────┐ │ │ │ │ │ AuditChain │ │ │ │ │ │ (SM3哈希链) │ │ │ │ │ └──────────────────┘ │ │ │ └────────────────────────────┘ │ │ │ │ └────────────────────────────────────────┼────────────────────────┘ │ │ SM4 加密通道 ▼ ┌────────────────────────────────────────┐ │ GovMCP Server │ │ (独立进程 / Docker 容器) │ │ │ │ 15 审批工具 + 6 大类政务工具 │ │ 48 国产 LLM 适配器 │ │ 认证授权 + 异步任务 + SSE 推送 │ └────────────────────────────────────────┘ ``` ### 6.3 Plugin 接口实现 ```python # plugins/taiji-govmcp/main.py from taiji.plugin import Plugin, PluginContext, PluginHealth class GovMCPPlugin(Plugin): """GovMCP 政务集成插件""" tools = [ # 审批工作流工具 ToolDefinition(name="initiate_approval_workflow", ...), ToolDefinition(name="query_approval_progress", ...), ToolDefinition(name="submit_approval_comment", ...), ToolDefinition(name="handle_approval_counter_sign", ...), ToolDefinition(name="handle_approval_joint_sign", ...), # 政务工具（代理到 GovMCP Server） ToolDefinition(name="query_carbon_emission", ...), ToolDefinition(name="query_environmental_data", ...), ] hooks = [ # 审批相关钩子 HookRegistration(event="feedback:request", handler="on_feedback_request", priority=50), HookRegistration(event="tool:result", handler="on_tool_result", priority=50), ] async def activate(self, ctx: PluginContext) -> None: """ 激活 GovMCP 插件： 1. 建立 SM4 加密通道连接 2. 初始化审批工作流引擎 3. 启动审计链 4. 注册政务工具 """ # 连接政务云 gov_config = ctx.config.get("gov_cloud", {}) self._gov_client = GovMCPClient( endpoint=gov_config.get("endpoint"), crypto_enabled=gov_config.get("crypto_enabled", True), sm4_key=gov_config.get("sm4_key"), ) await self._gov_client.connect() # 初始化审批引擎 approval_config = ctx.config.get("approval", {}) self._approval_flow = ApprovalFlow( default_timeout=approval_config.get("default_timeout", 3600), auto_approve_on_timeout=approval_config.get("auto_approve_on_timeout", False), audit_enabled=approval_config.get("audit_enabled", True), ) # 初始化审计链 self._audit_chain = AuditChain() if approval_config.get("audit_enabled", True): self._approval_flow.set_audit_chain(self._audit_chain) # 注册审批适配器到 FeedbackManager adapter = GovApprovalAdapter( gov_client=self._gov_client, approval_flow=self._approval_flow, audit_chain=self._audit_chain, ) feedback_manager = ctx.state_manager.get("feedback_manager") if feedback_manager: feedback_manager.register_adapter(adapter) # 注册 GovMCP 认证头 self._gov_client.set_auth_header(gov_config.get("auth_token", "")) ctx.logger.info(f"GovMCP plugin activated, endpoint={gov_config.get('endpoint')}") async def deactivate(self) -> None: """关闭加密通道，持久化审计链，释放资源""" if self._audit_chain: await self._persist_audit_chain() if self._gov_client: await self._gov_client.disconnect() self._approval_flow = None self._audit_chain = None async def health_check(self) -> PluginHealth: """检查政务云连接是否正常""" if not self._gov_client or not self._gov_client.is_connected: return PluginHealth.UNHEALTHY return PluginHealth.HEALTHY # ── Hook handlers ── async def on_feedback_request(self, data: dict) -> dict: """ 拦截 Harness 的 feedback:request 事件。 将反馈请求路由到政务审批工作流。 """ feedback_type = data.get("type", "") if feedback_type in ("review", "confirm", "form"): # 转换为政务审批请求 approval_id = await self._approval_flow.create_approval( workflow_type=self._map_feedback_type(feedback_type), applicant=data.get("requester", "system"), business_data=data.get("data", {}), ) data["gov_approval_id"] = approval_id # 将审批追加到审计链 self._audit_chain.add_entry( operation=f"approval:{feedback_type}", operator="system", input_data=json.dumps(data).encode(), output_data=approval_id.encode(), approval_status="PENDING", ) return data async def on_tool_result(self, data: dict) -> dict: """记录工具执行结果到审计链""" tool_name = data.get("name", "") tool_result = data.get("result", {}) self._audit_chain.add_entry( operation=f"tool:{tool_name}", operator="agent", input_data=json.dumps(data.get("args", {})).encode(), output_data=json.dumps(tool_result).encode(), approval_status="EXECUTED", ) return data ``` ### 6.4 GovApprovalAdapter 实现 ```python class GovApprovalAdapter(FeedbackAdapter): """ 政务审批适配器 — 桥接 Harness FeedbackManager 与 GovMCP ApprovalFlow。 """ id = "gov-approval" name = "政务审批适配器" def __init__(self, gov_client, approval_flow, audit_chain): self._gov_client = gov_client self._approval_flow = approval_flow self._audit_chain = audit_chain async def request_feedback(self, request: FeedbackRequest) -> FeedbackResponse: """ 处理不同类型的审批请求。 映射到 GovMCP 审批工作流。 """ if request.type == "review": return await self._handle_review(request) elif request.type == "confirm": return await self._handle_confirm(request) elif request.type == "form": return await self._handle_form(request) elif request.type == "choice": return await self._handle_choice(request) async def _handle_review(self, request: FeedbackRequest) -> FeedbackResponse: """ 审核请求 — 多级审批。 1. 根据审批级别路由到不同审批人 2. 通过政务 OA 系统发送审批任务 3. 等待审批结果 """ # Step 1: 确定审批级别 level = self._determine_approval_level(request) approvers = await self._route_to_approvers(request, level) # Step 2: 创建审批流程 workflow_id = await self._gov_client.tools.call( "initiate_approval_workflow", arguments={ "workflow_name": request.prompt[:100], "applicant_name": request.requester, "workflow_type": "审核", "business_data": { "request_id": request.id, "content": request.artifact.content if request.artifact else "", "approvers": approvers, } } ) # Step 3: 等待审批结果（轮询 + 超时） start_time = time.time() deadline = start_time + (request.timeout or 3600) while time.time() < deadline: progress = await self._gov_client.tools.call( "query_approval_progress", arguments={"workflow_id": workflow_id["result"]} ) status = progress.get("result", {}).get("status") if status == "APPROVED": return FeedbackResponse(approved=True, comment=progress.get("comment")) elif status == "REJECTED": return FeedbackResponse(approved=False, comment=progress.get("comment")) elif status == "TIMEOUT": if self._approval_flow.auto_approve_on_timeout: return FeedbackResponse(approved=True, comment="Auto-approved on timeout") return FeedbackResponse(approved=False, comment="Timeout denied by policy") await asyncio.sleep(5) return FeedbackResponse(approved=False, comment="Approval timeout") ``` ### 6.5 加密通道管理 ```python class GovMCPChannel: """ 本地 ↔ 政务云加密通信通道。 使用 GovMCP 的 SM4-CBC + SM3 协议。 """ def __init__(self, endpoint: str, crypto_enabled: bool = True, sm4_key: str = None): self.endpoint = endpoint self.crypto_enabled = crypto_enabled self._sm4_key = sm4_key self._session: Optional[aiohttp.ClientSession] = None self._sequence = 0 async def connect(self): self._session = aiohttp.ClientSession() if self.crypto_enabled and not self._sm4_key: # 自动执行 SM2 ECDH 密钥协商 self._sm4_key = await self._key_exchange() return self async def disconnect(self): if self._session: await self._session.close() async def send_request(self, method: str, params: dict) -> dict: """ 发送加密的 JSON-RPC 请求。 协议格式： base64(SM4-CBC(IV, JSON-RPC payload)) | SM3(ciphertext) """ self._sequence += 1 payload = { "jsonrpc": "2.0", "method": method, "params": params, "id": self._sequence, } if self.crypto_enabled: # SM4 加密 payload_str = json.dumps(payload) iv = os.urandom(16) ciphertext = sm4_cbc_encrypt(payload_str.encode(), self._sm4_key, iv) encoded = base64.b64encode(iv + ciphertext).decode("ascii") # SM3 完整性校验 mac = sm3_hash(ciphertext) body = f"{encoded}|{mac}" headers = {"Content-Type": "text/plain"} else: body = json.dumps(payload) headers = {"Content-Type": "application/json"} async with self._session.post( self.endpoint, data=body, headers=headers ) as resp: response_body = await resp.text() if self.crypto_enabled: # 解密响应 encoded, mac = response_body.split("|") raw = base64.b64decode(encoded) iv = raw[:16] ciphertext = raw[16:] decrypted = sm4_cbc_decrypt(ciphertext, self._sm4_key, iv) return json.loads(decrypted.decode()) else: return json.loads(response_body) async def _key_exchange(self) -> bytes: """SM2 ECDH 密钥协商""" # 生成本地 SM2 密钥对 local_private, local_public = generate_sm2_keypair() # 发送公钥给服务器 resp = await self.send_request("key_exchange", {"public_key": local_public.hex()}) server_public = bytes.fromhex(resp["result"]["public_key"]) # 计算共享秘密 shared_secret = sm2_calculate_shared_secret(local_private, server_public) # KDF 派生会话密钥 return sm2_derive_key(shared_secret, 16) ``` ### 6.6 审计链对接 ```python class AuditChainPlugin: """ 审计链 — 基于 SM3 哈希链的不可篡改审计。 对接 GovMCP 的 AuditChain 实现。 """ def __init__(self, storage: PersistenceStore): self._chain = AuditChain() self._storage = storage async def record( self, operation: str, operator: str, input_data: bytes, output_data: bytes, approval_status: str ) -> str: """记录审计条目，返回当前哈希""" entry = self._chain.add_entry( operation=operation, operator=operator, input_data=input_data, output_data=output_data, approval_status=approval_status, ) # 持久化到存储（SQLite / PostgreSQL） await self._storage.append("audit_chain", { "id": entry.id, "timestamp": entry.timestamp, "operation": entry.operation, "operator": entry.operator, "input_hash": entry.input_hash, "output_hash": entry.output_hash, "approval_status": entry.approval_status, "prev_hash": entry.prev_hash, "current_hash": entry.current_hash, }) return entry.current_hash async def verify(self) -> bool: """验证整个审计链的完整性""" return self._chain.verify() async def export(self, path: Path) -> None: """导出审计链为 JSON 文件""" entries = self._chain.entries with open(path, "w", encoding="utf-8") as f: json.dump([entry.__dict__ for entry in entries], f, ensure_ascii=False, indent=2) ``` --- ## 7. 插件间依赖管理 ### 7.1 依赖声明 插件在 `plugin.yaml` 中声明依赖： ```yaml # 依赖声明语法 dependencies: - id: event-bus # 依赖的插件 ID version: ">=1.0.0,<2.0.0" # 语义版本约束 optional: false # 是否可选（默认 false） - id: embedding-service version: ">=0.5.0" optional: true # 可选依赖：存在则使用，不存在可降级 ``` 依赖类型： | 类型 | 说明 | 示例 | |------|------|------| | **硬依赖** | 插件激活前必须满足，否则报错 | `taiji-verify` 依赖 `event-bus` | | **软依赖** | 可选，缺失时插件以降级模式运行 | `taiji-govmcp` 可选依赖 `taiji-verify` | | **服务依赖** | 依赖外部服务而非插件 | 嵌入模型、向量数据库 | ### 7.2 循环依赖检测 使用 Kahn 拓扑排序 + DFS 回溯检测： ```python class CircularDependencyError(Exception): """循环依赖异常""" pass class DependencyGraph: """依赖图分析工具""" def __init__(self): self._graph: dict[str, set[str]] = {} self._plugins: dict[str, PluginMetadata] = {} def add_plugin(self, meta: PluginMetadata): self._plugins[meta.id] = meta self._graph.setdefault(meta.id, set()) for dep in meta.dependencies: if not dep.optional: # 仅硬依赖参与拓扑排序 self._graph.setdefault(meta.id, set()).add(dep.plugin_id) def detect_cycle(self) -> list[list[str]] | None: """ DFS 检测所有循环依赖路径。 返回循环路径列表，无循环返回 None。 """ WHITE, GRAY, BLACK = 0, 1, 2 color = {pid: WHITE for pid in self._graph} parent = {} cycles = [] def dfs(node, path): color[node] = GRAY path.append(node) for neighbor in self._graph.get(node, set()): if neighbor not in color: # 跳过未注册的依赖 continue if color[neighbor] == GRAY: # 发现循环 cycle_start = path.index(neighbor) cycles.append(path[cycle_start:] + [neighbor]) elif color[neighbor] == WHITE: parent[neighbor] = node dfs(neighbor, path) path.pop() color[node] = BLACK for node in self._graph: if color[node] == WHITE: dfs(node, []) return cycles if cycles else None ``` ### 7.3 版本兼容性矩阵 | 插件 A 版本 | 插件 B 版本 | 兼容性 | |-------------|-------------|--------| | verifier 1.0.x | event-bus 1.0.x | ✅ 兼容 | | verifier 1.0.x | event-bus 2.0.x | ❌ 不兼容（有 Breaking Change） | | verifier 1.0.x | govmcp 1.0.x | ✅ 兼容（无直接依赖） | | verifier 1.0.x | govmcp 2.0.x | ⚠️ 需验证（接口稳定） | 版本冲突解决策略： 1. **严格匹配**：根据 `version_spec` 精确匹配，不符合则报错 2. **多版本共存**：同一插件不同版本可同时加载（命名空间隔离） 3. **版本升级**：提供 `upgrade` 命令自动解析依赖树并升级 --- ## 8. 安全沙箱 ### 8.1 权限控制 插件声明所需权限，加载时由权限管理器检查： ```python class PermissionManager: """ 插件权限管理器。 基于白名单模型：插件只能使用已声明的权限。 未声明的权限操作自动拒绝。 """ def __init__(self): # 预定义权限层级 self._permission_hierarchy = { "eventbus:subscribe": ["eventbus:subscribe:*"], "eventbus:emit": ["eventbus:emit:*"], "storage:read": ["storage:read:*"], "storage:write": ["storage:write:*"], "network:connect": ["network:connect:*"], "crypto": ["crypto:*"], "filesystem:read": ["filesystem:read:*"], "filesystem:write": ["filesystem:write:*"], } def check_permission(self, plugin_id: str, permission: str) -> bool: """检查插件是否有特定权限""" granted = self._granted_permissions.get(plugin_id, set()) # 精确匹配 if permission in granted: return True # 通配符匹配 for gp in granted: if self._wildcard_match(gp, permission): return True return False def _wildcard_match(self, pattern: str, target: str) -> bool: """通配符匹配，如 eventbus:* 匹配 eventbus:subscribe:tool:request""" pattern_parts = pattern.split(":") target_parts = target.split(":") for p, t in zip(pattern_parts, target_parts): if p == "*": return True if p != t: return False return len(pattern_parts) <= len(target_parts) ``` **预定义权限层级**： | 权限 | 说明 | 等级 | |------|------|------| | `eventbus:subscribe:read` | 只读事件订阅 | L1 | | `eventbus:subscribe:tool:request` | 监听工具调用 | L2 | | `eventbus:emit:verify:*` | 发射验证事件 | L2 | | `storage:read:verify-rules` | 读取验证规则 | L2 | | `storage:write:verify-results` | 写入验证结果 | L3 | | `network:connect:gov-cloud` | 连接政务云 | L3 | | `crypto:sm4` | 使用 SM4 加密 | L3 | | `crypto:sm3` | 使用 SM3 哈希 | L3 | | `filesystem:write:plugin-data` | 写入插件数据目录 | L3 | | `network:listen` | 监听网络端口 | L4（需审批） | ### 8.2 资源限制 | 维度 | 限制措施 | 默认值 | |------|----------|--------| | **CPU** | 子进程 cgroups / Docker CPU shares | 1 vCPU | | **内存** | `resource.setrlimit(RLIMIT_AS)` | 512 MB | | **磁盘写入** | 限制插件数据目录配额 | 100 MB | | **并发请求** | Semaphore 限制并发数 | 10 | | **网络访问** | ACL 白名单（仅允许声明的主机） | 仅政务云端点 | | **执行时间** | `asyncio.wait_for()` 超时控制 | 30s（同步），300s（异步） | | **文件描述符** | `resource.setrlimit(RLIMIT_NOFILE)` | 100 | ### 8.3 隔离策略 | 隔离级别 | 描述 | 适用场景 | 实现成本 | |----------|------|----------|----------| | **Level 0** (进程内) | 插件在同一进程运行，通过 Python 命名空间隔离 | 验证工具、审批适配 | 低 | | **Level 1** (子进程) | 插件在独立子进程运行，IPC 通信 | CPU 密集型插件 | 中 | | **Level 2** (Docker) | 每个插件一个 Docker 容器，完整隔离 | 高安全要求的政务插件 | 高 | | **Level 3** (gVisor) | 微虚拟机级隔离，更严格的安全边界 | 运行第三方未知插件 | 极高 | **默认策略**：Level 0（系统插件）+ Level 1（第三方插件） ```python class PluginSandbox: """ 插件沙箱管理器。 根据插件的 permissions 和安全等级选择隔离策略。 """ ISOLATION_LEVELS = { "SYSTEM": 0, # 内置系统插件，进程内运行 "TRUSTED": 0, # 可信任的官方插件 "THIRD_PARTY": 1, # 第三方插件，子进程隔离 "UNTRUSTED": 2, # 不可信插件，Docker 隔离 } def __init__(self): self._sandboxes: dict[str, BaseSandbox] = {} async def start_sandbox(self, plugin: Plugin) -> BaseSandbox: """根据插件安全等级启动合适的沙箱""" level = self._determine_level(plugin) if level == 0: return InProcessSandbox(plugin) elif level == 1: return SubProcessSandbox(plugin) elif level == 2: return DockerSandbox(plugin) async def execute(self, plugin_id: str, func: str, args: tuple) -> Any: """在沙箱中执行函数""" sandbox = self._sandboxes.get(plugin_id) if not sandbox: raise SandboxError(f"Plugin {plugin_id} not in sandbox") return await sandbox.execute(func, args) ``` --- 

### 8.4 SubProcess 隔离方案

SubProcess 隔离级别通过独立子进程运行插件，使用 IPC 通信实现安全隔离：

```python
import asyncio
import multiprocessing as mp
import json
import uuid
from dataclasses import dataclass
from typing import Any, Optional
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeoutError

@dataclass
class SubProcessSandboxConfig:
    """子进程沙箱配置"""
    max_memory_mb: int = 512          # 最大内存 (MB)
    max_cpu_percent: int = 100       # 最大CPU占用百分比
    max_execution_seconds: int = 30  # 最大执行时间 (秒)
    max_file_size_mb: int = 100      # 最大文件大小 (MB)
    allowed_modules: list[str] = None # 允许导入的模块列表
    env_vars: dict[str, str] = None  # 环境变量白名单

class SubProcessSandbox:
    """
    子进程沙箱实现。
    插件在独立子进程中运行，通过 IPC 与主进程通信。
    """
    
    def __init__(self, plugin: Plugin, config: Optional[SubProcessSandboxConfig] = None):
        self.plugin = plugin
        self.config = config or SubProcessSandboxConfig()
        self._process: Optional[mp.Process] = None
        self._pipe: Optional[mp.Connection] = None
        self._executor = ProcessPoolExecutor(max_workers=1)
        self._sandbox_id = str(uuid.uuid4())
        
    async def start(self) -> None:
        """启动子进程沙箱"""
        # 创建管道用于 IPC
        parent_conn, child_conn = mp.Pipe()
        self._pipe = parent_conn
        
        # 使用 spawn 方式创建进程（更安全）
        ctx = mp.get_context('spawn')
        
        # 准备进程启动参数
        process_args = (
            child_conn,
            self.plugin.metadata.id,
            self.config,
            self._sandbox_id
        )
        
        # 启动子进程
        self._process = ctx.Process(
            target=_subprocess_entry,
            args=process_args,
            daemon=True
        )
        self._process.start()
        
        # 等待子进程就绪
        await self._wait_ready()
        
    async def execute(self, func_name: str, args: tuple, kwargs: dict) -> Any:
        """
        在子进程中执行函数。
        通过管道发送请求并接收结果。
        """
        if not self._pipe:
            raise SandboxError("Sandbox not started")
        
        # 构造请求
        request = {
            "type": "execute",
            "func": func_name,
            "args": args,
            "kwargs": kwargs,
            "request_id": str(uuid.uuid4())
        }
        
        # 发送请求
        self._pipe.send(request)
        
        # 等待结果（带超时）
        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    self._pipe.recv
                ),
                timeout=self.config.max_execution_seconds
            )
            
            if result.get("error"):
                raise SandboxError(f"Execution error: {result['error']}")
            
            return result.get("result")
            
        except FuturesTimeoutError:
            raise SandboxError(f"Execution timeout after {self.config.max_execution_seconds}s")
    
    async def _wait_ready(self, timeout: int = 5) -> None:
        """等待子进程就绪"""
        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    self._pipe.recv
                ),
                timeout=timeout
            )
            if result.get("type") != "ready":
                raise SandboxError("Subprocess failed to start")
        except asyncio.TimeoutError:
            raise SandboxError("Subprocess startup timeout")
    
    async def stop(self) -> None:
        """停止子进程沙箱"""
        if self._pipe:
            try:
                self._pipe.send({"type": "shutdown"})
                self._pipe.close()
            except:
                pass
            self._pipe = None
        
        if self._process:
            self._process.join(timeout=3)
            if self._process.is_alive():
                self._process.terminate()
            self._process = None
        
        self._executor.shutdown(wait=False)

def _subprocess_entry(conn: mp.Connection, plugin_id: str, config: SubProcessSandboxConfig, sandbox_id: str) -> None:
    """
    子进程入口函数。
    在子进程中加载插件并处理主进程请求。
    """
    import sys
    import os
    import resource
    
    # 设置资源限制
    def set_resource_limits():
        # 内存限制
        memory_limit = config.max_memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
        
        # CPU时间限制
        resource.setrlimit(resource.RLIMIT_CPU, (config.max_execution_seconds, config.max_execution_seconds + 10))
        
        # 文件大小限制
        file_limit = config.max_file_size_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
        
        # 进程数限制
        resource.setrlimit(resource.RLIMIT_NPROC, (5, 5))
        
        # 文件描述符限制
        resource.setrlimit(resource.RLIMIT_NOFILE, (50, 50))
    
    set_resource_limits()
    
    # 设置环境变量（只保留白名单中的变量）
    if config.env_vars:
        # 保留指定的环境变量
        allowed_vars = set(config.env_vars.keys()) | {'PATH', 'PYTHONPATH'}
        for key in list(os.environ.keys()):
            if key not in allowed_vars:
                del os.environ[key]
        # 添加白名单中的环境变量
        os.environ.update(config.env_vars)
    
    # 模块白名单限制
    original_import = __builtins__.__import__
    allowed_module_set = set(config.allowed_modules or [])
    
    def safe_import(name, *args, **kwargs):
        # 检查是否在白名单中
        root_module = name.split('.')[0]
        if allowed_module_set and root_module not in allowed_module_set:
            raise ImportError(f"Module '{name}' not allowed in sandbox")
        return original_import(name, *args, **kwargs)
    
    __builtins__.__import__ = safe_import
    
    # 加载插件
    plugin_instance = None
    try:
        # 动态导入插件模块
        module = __import__(f"plugins.{plugin_id}.main", fromlist=['main'])
        plugin_class = getattr(module, 'Plugin')
        plugin_instance = plugin_class()
    except Exception as e:
        conn.send({"type": "error", "error": str(e)})
        return
    
    # 发送就绪信号
    conn.send({"type": "ready", "sandbox_id": sandbox_id})
    
    # 处理请求循环
    while True:
        try:
            request = conn.recv()
        except EOFError:
            break
        
        if request.get("type") == "shutdown":
            break
        
        if request.get("type") == "execute":
            result = {"request_id": request.get("request_id")}
            try:
                func = getattr(plugin_instance, request.get("func"))
                args = request.get("args", ())
                kwargs = request.get("kwargs", {})
                
                # 在子进程中执行（已经是异步的简单调用）
                import asyncio
                loop = asyncio.new_event_loop()
                try:
                    ret = loop.run_until_complete(func(*args, **kwargs))
                    result["result"] = ret
                finally:
                    loop.close()
                    
            except Exception as e:
                result["error"] = str(e)
            
            conn.send(result)
```

**SubProcess 沙箱特点**：
- 独立进程内存空间，无法直接访问主进程内存
- 通过管道（Pipe）进行进程间通信
- 使用 `resource` 模块设置系统资源限制（CPU、内存、文件大小等）
- 支持模块白名单，限制插件可导入的 Python 模块
- 支持环境变量白名单控制

### 8.5 Docker 沙箱方案

Docker 隔离级别通过容器技术实现完整隔离：

```python
import asyncio
import aiohttp
import json
import uuid
import tempfile
import os
from dataclasses import dataclass
from typing import Any, Optional
from pathlib import Path

@dataclass
class DockerSandboxConfig:
    """Docker 沙箱配置"""
    image: str = "taiji-agent/plugin-sandbox:latest"  # 沙箱基础镜像
    memory_limit: str = "512m"        # 内存限制
    cpu_limit: float = 1.0           # CPU 核心数
    network_mode: str = "none"       # 网络模式（none/bridge/custom）
    readonly_fs: bool = True         # 只读文件系统
    max_execution_seconds: int = 300 # 最大执行时间
    volumes: dict[str, str] = None   # 挂载卷 {host_path: container_path}

class DockerSandbox:
    """
    Docker 沙箱实现。
    每个插件运行在独立的 Docker 容器中。
    """
    
    def __init__(self, plugin: Plugin, config: Optional[DockerSandboxConfig] = None):
        self.plugin = plugin
        self.config = config or DockerSandboxConfig()
        self._container_id: Optional[str] = None
        self._work_dir: Optional[Path] = None
        self._sandbox_id = str(uuid.uuid4())
        self._docker_host = os.environ.get("DOCKER_HOST", "unix:///var/run/docker.sock")
        
    async def start(self) -> None:
        """启动 Docker 容器"""
        # 创建工作目录
        self._work_dir = Path(tempfile.mkdtemp(prefix=f"sandbox_{self._sandbox_id}_"))
        
        # 准备挂载卷
        volumes = {
            str(self._work_dir): {"bind": "/workspace", "mode": "rw"}
        }
        if self.config.volumes:
            volumes.update(self.config.volumes)
        
        # 构造 docker run 命令
        docker_cmd = self._build_docker_command(volumes)
        
        # 执行 docker run
        result = await self._exec_docker(docker_cmd)
        self._container_id = result["Id"]
        
        # 等待容器就绪
        await self._wait_container_ready()
        
    def _build_docker_command(self, volumes: dict) -> list:
        """构建 docker run 命令"""
        cmd = [
            "docker", "run",
            "--rm",                           # 容器停止后自动删除
            "--name", f"sandbox_{self._sandbox_id}",
            "--memory", self.config.memory_limit,
            "--cpus", str(self.config.cpu_limit),
            "--network", self.config.network_mode,
            "--read-only" if self.config.readonly_fs else "",
            "--security-opt", "no-new-privileges",
            "--cap-drop", "ALL",
            "--pids-limit", "50",
            "--user", "1000:1000",            # 非 root 用户运行
        ]
        
        # 添加环境变量（安全）
        cmd.extend([
            "-e", f"PLUGIN_ID={self.plugin.metadata.id}",
            "-e", f"SANDBOX_ID={self._sandbox_id}",
        ])
        
        # 添加挂载卷
        for host_path, mount_config in volumes.items():
            cmd.extend([
                "-v", f"{host_path}:{mount_config['bind']}:{mount_config['mode']}"
            ])
        
        # 镜像和启动命令
        cmd.extend([
            self.config.image,
            "python", "-m", "sandbox.server"
        ])
        
        return [c for c in cmd if c]  # 过滤空字符串
    
    async def execute(self, func_name: str, args: tuple, kwargs: dict) -> Any:
        """通过 HTTP API 在容器中执行函数"""
        if not self._container_id:
            raise SandboxError("Container not started")
        
        # 调用容器内的沙箱服务
        url = f"http://localhost:8000/execute"
        
        payload = {
            "function": func_name,
            "args": args,
            "kwargs": kwargs,
            "timeout": self.config.max_execution_seconds
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.max_execution_seconds + 10)
                ) as response:
                    result = await response.json()
                    
                    if result.get("error"):
                        raise SandboxError(f"Execution error: {result['error']}")
                    
                    return result.get("result")
                    
            except aiohttp.ClientError as e:
                raise SandboxError(f"Container communication error: {e}")
    
    async def _wait_container_ready(self, timeout: int = 30) -> None:
        """等待容器就绪"""
        for _ in range(timeout):
            try:
                # 检查容器是否运行
                result = await self._exec_docker(["docker", "inspect", "-f", "{{.State.Running}}", self._container_id])
                if result[0].get("Value", "").strip() == "true":
                    return
            except:
                pass
            await asyncio.sleep(1)
        
        raise SandboxError("Container startup timeout")
    
    async def _exec_docker(self, cmd: list) -> dict:
        """执行 docker 命令"""
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise SandboxError(f"Docker command failed: {stderr.decode()}")
        
        try:
            return json.loads(stdout.decode())
        except json.JSONDecodeError:
            return {"Value": stdout.decode()}
    
    async def stop(self) -> None:
        """停止并清理 Docker 容器"""
        if self._container_id:
            try:
                await self._exec_docker(["docker", "stop", "-t", "5", self._container_id])
            except:
                pass
            self._container_id = None
        
        # 清理工作目录
        if self._work_dir and self._work_dir.exists():
            import shutil
            shutil.rmtree(self._work_dir, ignore_errors=True)
```

**Docker 沙箱特点**：
- 完整操作系统级隔离
- 独立的网络命名空间（可选关闭网络）
- 只读文件系统增强安全性
- 强制删除 capabilities，限制特权操作
- PID 限制防止 Fork 炸弹
- 非 root 用户运行
- 可通过挂载卷共享数据

### 8.6 超时和回收机制

```python
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

class ResourceState(Enum):
    IDLE = "idle"              # 空闲，可回收
    BUSY = "busy"              # 忙碌中
    TIMEOUT = "timeout"        # 执行超时
    ERROR = "error"            # 执行错误

@dataclass
class SandboxResource:
    """沙箱资源记录"""
    sandbox_id: str
    plugin_id: str
    sandbox: BaseSandbox
    state: ResourceState = ResourceState.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    execution_count: int = 0
    timeout_count: int = 0
    error_count: int = 0

class SandboxResourceManager:
    """
    沙箱资源管理器。
    负责沙箱的生命周期、复用和回收。
    """
    
    def __init__(
        self,
        idle_timeout_seconds: int = 300,      # 空闲超时时间
        max_execution_seconds: int = 300,     # 最大执行时间
        max_timeout_count: int = 3,           # 最大超时次数
        cleanup_interval_seconds: int = 60,    # 清理检查间隔
    ):
        self.idle_timeout = timedelta(seconds=idle_timeout_seconds)
        self.max_execution = max_execution_seconds
        self.max_timeout_count = max_timeout_count
        self._resources: Dict[str, SandboxResource] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def get_sandbox(self, plugin: Plugin) -> BaseSandbox:
        """获取或创建沙箱实例"""
        # 查找可复用的空闲沙箱
        for resource in self._resources.values():
            if (resource.plugin_id == plugin.metadata.id and 
                resource.state == ResourceState.IDLE and
                datetime.now() - resource.last_used < self.idle_timeout):
                return resource.sandbox
        
        # 创建新沙箱
        sandbox = await self._create_sandbox(plugin)
        resource = SandboxResource(
            sandbox_id=sandbox._sandbox_id if hasattr(sandbox, '_sandbox_id') else str(id(sandbox)),
            plugin_id=plugin.metadata.id,
            sandbox=sandbox
        )
        self._resources[resource.sandbox_id] = resource
        
        # 启动清理任务
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        return sandbox
    
    async def execute(
        self, 
        sandbox: BaseSandbox, 
        func_name: str, 
        args: tuple, 
        kwargs: dict
    ) -> Any:
        """执行沙箱函数，带超时控制"""
        sandbox_id = getattr(sandbox, '_sandbox_id', str(id(sandbox)))
        resource = self._resources.get(sandbox_id)
        
        if not resource:
            raise SandboxError("Sandbox not registered")
        
        resource.state = ResourceState.BUSY
        resource.last_used = datetime.now()
        resource.execution_count += 1
        
        try:
            result = await asyncio.wait_for(
                sandbox.execute(func_name, args, kwargs),
                timeout=self.max_execution
            )
            resource.state = ResourceState.IDLE
            return result
            
        except asyncio.TimeoutError:
            resource.state = ResourceState.TIMEOUT
            resource.timeout_count += 1
            raise SandboxTimeoutError(f"Execution timeout after {self.max_execution}s")
            
        except Exception as e:
            resource.state = ResourceState.ERROR
            resource.error_count += 1
            raise SandboxError(f"Execution error: {e}")
            
        finally:
            if resource.state == ResourceState.IDLE:
                resource.last_used = datetime.now()
    
    async def release_sandbox(self, sandbox_id: str) -> None:
        """释放沙箱资源"""
        resource = self._resources.get(sandbox_id)
        if resource:
            try:
                await resource.sandbox.stop()
            except:
                pass
            del self._resources[sandbox_id]
    
    async def _cleanup_loop(self) -> None:
        """定期清理过期沙箱"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval_seconds)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception:
                pass
    
    async def _cleanup_expired(self) -> None:
        """清理过期和超限的沙箱"""
        now = datetime.now()
        to_remove = []
        
        for sandbox_id, resource in self._resources.items():
            # 清理空闲超时的沙箱
            if (resource.state == ResourceState.IDLE and 
                now - resource.last_used > self.idle_timeout):
                to_remove.append(sandbox_id)
                continue
            
            # 清理超时次数超限的沙箱
            if resource.timeout_count >= self.max_timeout_count:
                to_remove.append(sandbox_id)
                continue
        
        for sandbox_id in to_remove:
            await self.release_sandbox(sandbox_id)
    
    async def get_stats(self) -> dict:
        """获取沙箱统计信息"""
        total = len(self._resources)
        idle = sum(1 for r in self._resources.values() if r.state == ResourceState.IDLE)
        busy = sum(1 for r in self._resources.values() if r.state == ResourceState.BUSY)
        
        return {
            "total": total,
            "idle": idle,
            "busy": busy,
            "total_executions": sum(r.execution_count for r in self._resources.values()),
            "total_timeouts": sum(r.timeout_count for r in self._resources.values()),
        }
```

**超时和回收机制特点**：
- **执行超时**：单次执行有最大时间限制，防止插件死锁
- **空闲回收**：空闲沙箱在超时后自动清理，释放资源
- **错误追踪**：记录每个沙箱的超时和错误次数
- **自动降级**：连续超时的沙箱会被标记并替换
- **统计监控**：提供沙箱使用统计便于运维监控



## 9. 配置与部署 ### 9.1 插件目录结构 ``` plugins/ ├── taiji-verify/ # 太极验证插件 │ ├── plugin.yaml # 插件声明文件 │ ├── main.py # 插件入口 │ ├── compiler/ │ │ └── beichen.py # 北辰编译器 │ ├── verify/ │ │ ├── delta_s.py # 阴阳距 │ │ ├── bbmc.py # 坤守 │ │ ├── bbpf.py # 乾进 │ │ ├── bbcr.py # 复归 │ │ └── bbam.py # 巽调 │ ├── rules/ │ │ ├── compliance.yaml # 合规规则（YAML） │ │ └── failure_modes.yaml # 失败模式（YAML） │ └── tools/ │ ├── manage_rules.py │ └── query_results.py │ ├── taiji-govmcp/ # 政务 MCP 插件 │ ├── plugin.yaml │ ├── main.py │ ├── gov_client.py # GovMCP 客户端 │ ├── approval_adapter.py # 审批适配器 │ ├── audit_chain.py # 审计链 │ ├── crypto/ │ │ ├── sm.py # SM3/SM4 │ │ └── sm2.py # SM2 │ └── tools/ │ ├── approval_tools.py │ └── gov_services.py │ ├── event-bus/ # 事件总线（核心） │ ├── plugin.yaml │ └── main.py │ └── embedding-service/ # 嵌入服务（可选） ├── plugin.yaml └── main.py ``` ### 9.2 配置文件格式 **主配置 (agent.yaml)**： ```yaml # config/agent.yaml — Taiji Agent 主配置 agent: name: "Taiji Agent" version: "1.0.0" mode: "production" log_level: "info" plugins: enabled: - taiji-verify - taiji-govmcp directories: - ./plugins - /usr/share/taiji/plugins auto_discover: true # 自动扫描插件目录 enable_watchdog: true # 启用文件监听热插拔 enable_sandbox: false # 启用沙箱隔离 # 插件级配置覆盖 config: taiji-verify: mode: moderate min_delta_s: 0.3 taiji-govmcp: gov_cloud: endpoint: "https://gov-cloud.example.com/mcp" approval: default_timeout: 3600 ``` **插件级配置 (plugin.yaml)**： 见第 5.1 节和第 6.1 节的 YAML 示例。 ### 9.3 部署策略 | 部署模式 | 说明 | 适用阶段 | |----------|------|----------| | **开发模式** | 直接加载 `plugins/` 目录，Watchdog 启用，日志级别 debug | 开发 | | **测试模式** | 加载指定插件集，模拟模式运行（auto-approve 审批） | 集成测试 | | **单机生产** | 静态加载，沙箱关闭，性能最优 | 单机部署 | | **分布式生产** | 插件跨进程/容器部署，通过 gRPC 通信 | 集群部署 | 部署生命周期： ``` # 1. 安装（文件拷贝 + 依赖安装） ./taiji plugin install path/to/plugin.tar.gz # 2. 列出已安装插件 ./taiji plugin list # 3. 启用/禁用插件 ./taiji plugin enable taiji-verify ./taiji plugin disable taiji-govmcp # 4. 查看插件状态 ./taiji plugin status taiji-verify # 5. 更新插件 ./taiji plugin update taiji-verify # 6. 卸载插件 ./taiji plugin uninstall taiji-verify ``` --- ## 10. 实现计划 ### 10.1 工作量估算 | 组件 | 子模块 | 预估工时 | 优先级 | |------|--------|----------|--------| | **核心接口** | Plugin 基类定义 | 2 人天 | P0 | | | PluginContext 实现 | 1 人天 | P0 | | | PluginLogger | 0.5 人天 | P0 | | **PluginLoader** | 目录扫描 + YAML 解析 | 3 人天 | P0 | | | 动态导入 (importlib) | 2 人天 | P0 | | | 祖先目录发现 | 1 人天 | P0 | | **生命周期** | 状态机管理 | 3 人天 | P0 | | | 状态转换事件发射 | 1 人天 | P0 | | | Error/Degraded 处理 | 2 人天 | P1 | | **依赖管理** | 拓扑排序 + 循环检测 | 3 人天 | P0 | | | 版本冲突检测 | 2 人天 | P1 | | | SemVer 兼容性检查 | 1 人天 | P1 | | **热插拔** | Watchdog 文件监听 | 2 人天 | P1 | | | 热重载逻辑 | 3 人天 | P2 | | **安全沙箱** | 子进程隔离 | 3 人天 | P1 | | | Docker 隔离 | 3 人天 | P2 | | | 权限管理器 | 2 人天 | P1 | | **Taiji Verify** | Plugin 主体 + Hook 注册 | 3 人天 | P0 | | | 阴阳距 ΔS 集成 | 2 人天 | P0 | | | 北辰编译器集成 | 2 人天 | P0 | | | 坤守/乾进/复归/巽调 | 8 人天 | P1 | | **GovMCP Plugin** | Plugin 主体 + Hook 注册 | 3 人天 | P0 | | | GovApprovalAdapter | 3 人天 | P0 | | | 加密通道管理 | 2 人天 | P0 | | | 审计链对接 | 2 人天 | P0 | | | 政务工具代理 | 3 人天 | P1 | | **测试** | 单元测试 | 5 人天 | P0 | | | 集成测试 | 5 人天 | P0 | | | 端到端测试 | 5 人天 | P1 | | **文档** | API 文档 | 2 人天 | P1 | | | 开发者指南 | 2 人天 | P1 | **总计：约 80-90 人天** ### 10.2 依赖关系 ``` Plugin 核心接口 ──────────────────────────────┐ │ │ ├── PluginLoader ── 依赖管理 ── 热插拔 │ │ │ └── 生命周期管理 │ │ Plugin 核心完成 ────────────────────────────────┤ │ │ ├── 安全沙箱 │ │ │ ├── Taiji Verify Plugin ──────┐ │ │ ├── 阴阳距 ΔS │ │ │ ├── 北辰编译器 │ │ │ └── 坤守/乾进/复归/巽调 │ │ │ │ │ └── GovMCP Plugin ────────────┤ │ ├── 加密通道 │ │ ├── 审批适配器 │ │ ├── 审计链 │ │ └── 政务工具代理 │ │ │ ┌────────┘ ▼ 系统集成验证 + 端到端测试 ``` ### 10.3 里程碑 ``` 里程碑 1：Plugin 核心 (Week 1-2) 里程碑 2：Taiji Verify (Week 3-4) ╔══════════════════════════════╗ ╔══════════════════════════════╗ ║ • Plugin 基类 + Context ║ ║ • Verify Plugin 主体 ║ ║ • PluginLoader（静态加载） ║ ║ • 阴阳距 ΔS 集成 ║ ║ • YAML 解析 ║ ║ • 北辰编译器集成 ║ ║ • 生命周期状态机 ║ ║ • 5 个 Hook 注册 ║ ║ • 依赖解析 + 拓扑排序 ║ ║ • 验证流水线集成测试 ║ ║ • 单元测试覆盖率 > 80% ║ ║ • 单元测试覆盖率 > 80% ║ ╚══════════════════════════════╝ ╚══════════════════════════════╝ 里程碑 3：GovMCP Plugin (Week 5-6) 里程碑 4：进阶能力 (Week 7-8) ╔══════════════════════════════╗ ╔══════════════════════════════╗ ║ • GovMCP Plugin 主体 ║ ║ • 热插拔 Watchdog ║ ║ • SM4 加密通道 ║ ║ • 安全沙箱（子进程） ║ ║ • GovApprovalAdapter ║ ║ • 权限管理器 ║ ║ • AuditChain 对接 ║ ║ • 坤守/乾进/复归/巽调 ║ ║ • 工具代理转接 ║ ║ • 政务工具代理 ║ ║ • 集成测试 ║ ║ • 端到端测试 ║ ╚══════════════════════════════╝ ╚══════════════════════════════╝ 里程碑 5：发布 (Week 9-10) ╔══════════════════════════════╗ ║ • 文档完善 ║ ║ • 开发者指南 ║ ║ • CLI 工具（plugin 子命令） ║ ║ • 性能优化 + 压力测试 ║ ║ • 全量集成测试 ║ ║ • 发布 v1.0.0 ║ ╚══════════════════════════════╝ ``` ### 10.4 风险与缓解 | 风险 | 影响 | 概率 | 缓解措施 | |------|------|:----:|----------| | Python importlib 动态加载复杂 | 加载失败 | 低 | 先实现简单的字符串路径导入，再优化 | | 热插拔状态一致性 | 状态混乱 | 中 | 热重载时使用读写锁，确保操作原子性 | | 插件依赖解析器性能 | 启动慢 | 低 | 缓存解析结果，增量更新 | | 安全沙箱降低性能 | 吞吐下降 | 中 | 默认 Level 0，按需启用更高级别 | | GovMCP SM4 和 Python 兼容性 | 加密失败 | 低 | 使用纯 Python 实现（不依赖 gmssl 硬件加速） | --- ## 附录 A：与 Harness Plugin 接口对照表 | Harness (TypeScript) | Taiji Agent (Python) | 说明 | |----------------------|----------------------|------| | `HarnessPlugin` | `Plugin` | 核心接口 | | `PluginContext` | `PluginContext` | 上下文（扩展了 data_dir/logger） | | `activate(ctx)` | `async activate(ctx)` | 激活方法 | | `deactivate()` | `async deactivate()` | 停用方法 | | `tools` | `tools` | 工具定义列表 | | `hooks` | `hooks` | 事件钩子列表 | | `ui` | `ui_contributions` | UI 贡献 | | `PluginConfig` | `PluginContext.config` | 配置接口 | | `Logger` | `PluginLogger` | 日志接口 | | `PluginLoader` | `PluginLoader` | 加载器（扩展了 YAML 支持） | | — | `metadata` | 元数据（YAML 声明） | | — | `dependencies` | 依赖声明 | | — | `permissions` | 权限声明 | | — | `config_schema` | 配置 Schema | | — | `health_check()` | 健康检查 | | — | `get_metrics()` | 指标采集 | | — | `PluginState` | 状态枚举 | ## 附录 B：EventBus 事件扩展 新增事件类型以支持插件系统： | 事件名称 | 说明 | Payload | |----------|------|---------| | `plugin:before_load` | 插件加载前 | `{plugin_id, plugin_dir}` | | `plugin:after_load` | 插件加载后 | `{plugin_id, success, error?}` | | `plugin:before_activate` | 插件激活前 | `{plugin_id}` | | `plugin:after_activate` | 插件激活后 | `{plugin_id, success, error?}` | | `plugin:before_deactivate` | 插件停用前 | `{plugin_id}` | | `plugin:after_deactivate` | 插件停用后 | `{plugin_id, success, error?}` | | `plugin:error` | 插件异常 | `{plugin_id, state, error}` | | `plugin:health_change` | 健康状态变化 | `{plugin_id, old_health, new_health}` | | `verify:compliance_check` | 合规检查结果 | `{tool_name, delta_s, action}` | | `gov:approval` | 政务审批事件 | `{approval_id, status, approver}` | | `gov:audit` | 审计记录事件 | `{entry_id, operation, hash}` | 