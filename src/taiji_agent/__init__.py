"""
Taiji Agent Python Package

融合 Hermes Agent + cgast/harness + Taiji Verify WFGY + Dify + LangGraph + OpenAI Agents SDK
太极哲学驱动的 AI Agent 框架 v2.0

新增功能:
- MCP双向集成 (Dify v1.6.0)
- Guardrails安全护栏 (OpenAI Agents SDK)
- Tracing可观测性 (LangSmith)
- Human-in-the-Loop (Dify v1.13.0)
- Stateful Workflow (LangGraph)
- Agent Handoffs (OpenAI Agents SDK)
- Code Agent (SmolAgents)
- Visual Workflow
"""

from taiji_agent.agent.engine import AgentConfig, TaijiAgent
from taiji_agent.code import (
    CodeExecutor,
    ExecutionResult,
    ExecutionStatus,
    SandboxConfig,
    SandboxManager,
)
from taiji_agent.gateway import MessageGateway, create_gateway
from taiji_agent.guardrails import (
    ContentFilter,
    Guardrail,
    GuardrailConfig,
    GuardrailManager,
    InputGuardrail,
    OutputGuardrail,
    QualityGate,
    RateLimitGuardrail,
    SensitiveDataFilter,
    ValidationResult,
)
from taiji_agent.handoffs import (
    AgentRegistry,
    Handoff,
    HandoffConfig,
    HandoffContext,
    HandoffManager,
    HandoffResult,
)
from taiji_agent.hitl import (
    ApprovalConfig,
    ApprovalDecision,
    ApprovalQueue,
    ApprovalRequest,
    ApprovalStatus,
    Checkpoint,
    CheckpointManager,
    ConfidenceGate,
    ConfidenceLevel,
)
from taiji_agent.learning import HonchoMemory, SelfImprovingLoop
from taiji_agent.mcp import (
    MCPClientAdapter,
    MCPConnectionConfig,
    MCPProtocol,
    MCPResource,
    MCPServerAdapter,
    MCPServerConfig,
    MCPTool,
)
from taiji_agent.memory import SessionMemory
from taiji_agent.multiagent import (
    AgentMessage,
    AgentRole,
    AgentSwarm,
    AgentTask,
    BaseAgent,
    CoordinationMode,
    MessageBus,
    MultiAgentCoordinator,
)
from taiji_agent.multiagent import (
    TaijiAgent as MultiAgent,
)
from taiji_agent.observability import (
    ConsoleExporter,
    FileExporter,
    LangSmithExporter,
    SpanKind,
    SpanStatus,
    TraceEvent,
    TraceSpan,
    TracingManager,
)
from taiji_agent.providers import AnthropicProvider, OpenAIProvider
from taiji_agent.providers.chinese import (
    CHINESE_PROVIDERS,
    DoubaoProvider,
    GLMProvider,
    KimiProvider,
    QwenProvider,
    list_chinese_providers,
)
from taiji_agent.skills import Skill, SkillCreator, SkillManager
from taiji_agent.souls import Soul, SoulLoader
from taiji_agent.tools import ToolRegistry
from taiji_agent.visual import (
    ASCIIExporter,
    ExportFormat,
    HTMLExporter,
    JSONExporter,
    MermaidExporter,
    WorkflowExporter,
)
from taiji_agent.wfgy import HallucinationDetector, WFGYVerifier
from taiji_agent.taiji_verify import (
    DeltaSCalculator,
    DeltaSResult,
    GateZone,
    AnchorExtension,
    XunTune,
    AttentionModulation,
    TunedOutput,
    KunGuard,
    KunGuardResult,
    HazardLevel,
    KnowledgeAnchor,
    QianAdvance,
    QianAdvanceResult,
    PerturbationResult,
    FuReturn,
    RecoveryResult,
    RecoveryState,
    CrashingEvent,
    GuanObserve,
    StateSnapshot,
    TrendAnalysis,
    AnomalyEvent,
    ChangeType,
    PolarisCompiler,
    TaskAtom,
    TaskState,
    TaskType,
    SymptomMap,
    FailurePattern,
    FailureLevel,
    FailureDetection,
    DetectionResult,
)
from taiji_agent.workflow import (
    ConditionalEdge,
    Edge,
    Node,
    NodeResult,
    WorkflowConfig,
    WorkflowEngine,
    WorkflowGraph,
    WorkflowState,
)

__version__ = "2.0.0"

__all__ = [
    # Core
    "TaijiAgent",
    "AgentConfig",
    # WFGY
    "WFGYVerifier",
    "HallucinationDetector",
    # Taiji Verify - 阴阳距
    "DeltaSCalculator",
    "DeltaSResult",
    "GateZone",
    "AnchorExtension",
    # Taiji Verify - 坤守
    "KunGuard",
    "KunGuardResult",
    "HazardLevel",
    "KnowledgeAnchor",
    # Taiji Verify - 乾进
    "QianAdvance",
    "QianAdvanceResult",
    "PerturbationResult",
    # Taiji Verify - 复归
    "FuReturn",
    "RecoveryResult",
    "RecoveryState",
    "CrashingEvent",
    # Taiji Verify - 巽调
    "XunTune",
    "AttentionModulation",
    "TunedOutput",
    # Taiji Verify - 观变
    "GuanObserve",
    "StateSnapshot",
    "TrendAnalysis",
    "AnomalyEvent",
    "ChangeType",
    # Taiji Verify - 北辰编译器
    "PolarisCompiler",
    "TaskAtom",
    "TaskState",
    "TaskType",
    # Taiji Verify - 病候图
    "SymptomMap",
    "FailurePattern",
    "FailureLevel",
    "FailureDetection",
    "DetectionResult",
    # Soul
    "SoulLoader",
    "Soul",
    # Memory
    "SessionMemory",
    # Tools
    "ToolRegistry",
    # Providers
    "AnthropicProvider",
    "OpenAIProvider",
    "QwenProvider",
    "GLMProvider",
    "KimiProvider",
    "DoubaoProvider",
    "CHINESE_PROVIDERS",
    "list_chinese_providers",
    # Gateway
    "MessageGateway",
    "create_gateway",
    # Skills
    "SkillManager",
    "Skill",
    "SkillCreator",
    # Learning
    "HonchoMemory",
    "SelfImprovingLoop",
    # Multi-Agent
    "MultiAgentCoordinator",
    "AgentSwarm",
    "MessageBus",
    "AgentRole",
    "CoordinationMode",
    "AgentMessage",
    "AgentTask",
    "BaseAgent",
    "MultiAgent",
    # MCP Protocol (Dify v1.6.0)
    "MCPServerAdapter",
    "MCPServerConfig",
    "MCPClientAdapter",
    "MCPConnectionConfig",
    "MCPProtocol",
    "MCPTool",
    "MCPResource",
    # Guardrails (OpenAI Agents SDK)
    "Guardrail",
    "ValidationResult",
    "GuardrailConfig",
    "GuardrailManager",
    "InputGuardrail",
    "ContentFilter",
    "RateLimitGuardrail",
    "OutputGuardrail",
    "SensitiveDataFilter",
    "QualityGate",
    # Observability (LangSmith)
    "TracingManager",
    "TraceSpan",
    "TraceEvent",
    "SpanStatus",
    "SpanKind",
    "ConsoleExporter",
    "FileExporter",
    "LangSmithExporter",
    # HITL (Dify v1.13.0)
    "ApprovalQueue",
    "ApprovalRequest",
    "ApprovalDecision",
    "ApprovalStatus",
    "ApprovalConfig",
    "ConfidenceGate",
    "ConfidenceLevel",
    "Checkpoint",
    "CheckpointManager",
    # Workflow (LangGraph)
    "WorkflowEngine",
    "WorkflowState",
    "WorkflowConfig",
    "NodeResult",
    "WorkflowGraph",
    "Node",
    "Edge",
    "ConditionalEdge",
    # Handoffs (OpenAI Agents SDK)
    "Handoff",
    "HandoffConfig",
    "HandoffManager",
    "HandoffResult",
    "HandoffContext",
    "AgentRegistry",
    # Code Agent (SmolAgents)
    "CodeExecutor",
    "ExecutionResult",
    "ExecutionStatus",
    "SandboxConfig",
    "SandboxManager",
    # Visual
    "WorkflowExporter",
    "MermaidExporter",
    "ASCIIExporter",
    "JSONExporter",
    "HTMLExporter",
    "ExportFormat",
]
