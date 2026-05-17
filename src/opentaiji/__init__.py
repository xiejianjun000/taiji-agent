"""
OpenTaiji Python Package

融合 Hermes Agent + cgast/harness + OpenTaiji WFGY + Dify + LangGraph + OpenAI Agents SDK
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

from opentaiji.agent.engine import AgentConfig, TaijiAgent
from opentaiji.code import (
    CodeExecutor,
    ExecutionResult,
    ExecutionStatus,
    SandboxConfig,
    SandboxManager,
)
from opentaiji.gateway import MessageGateway, create_gateway
from opentaiji.guardrails import (
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
from opentaiji.handoffs import (
    AgentRegistry,
    Handoff,
    HandoffConfig,
    HandoffContext,
    HandoffManager,
    HandoffResult,
)
from opentaiji.hitl import (
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
from opentaiji.learning import HonchoMemory, SelfImprovingLoop
from opentaiji.mcp import (
    MCPClientAdapter,
    MCPConnectionConfig,
    MCPProtocol,
    MCPResource,
    MCPServerAdapter,
    MCPServerConfig,
    MCPTool,
)
from opentaiji.memory import SessionMemory
from opentaiji.multiagent import (
    AgentMessage,
    AgentRole,
    AgentSwarm,
    AgentTask,
    BaseAgent,
    CoordinationMode,
    MessageBus,
    MultiAgentCoordinator,
)
from opentaiji.multiagent import (
    TaijiAgent as MultiAgent,
)
from opentaiji.observability import (
    ConsoleExporter,
    FileExporter,
    LangSmithExporter,
    SpanKind,
    SpanStatus,
    TraceEvent,
    TraceSpan,
    TracingManager,
)
from opentaiji.providers import AnthropicProvider, OpenAIProvider
from opentaiji.providers.chinese import (
    CHINESE_PROVIDERS,
    DoubaoProvider,
    GLMProvider,
    KimiProvider,
    QwenProvider,
    list_chinese_providers,
)
from opentaiji.skills import Skill, SkillCreator, SkillManager
from opentaiji.souls import Soul, SoulLoader
from opentaiji.tools import ToolRegistry
from opentaiji.visual import (
    ASCIIExporter,
    ExportFormat,
    HTMLExporter,
    JSONExporter,
    MermaidExporter,
    WorkflowExporter,
)
from opentaiji.taiji_verify import (
    DeltaSCalculator,
    DeltaSResult,
    FailureMode,
    FailureModeDetector,
    FailureSeverity,
    FuReturn,
    GateZone,
    KunGuard,
    PolarisCompiler,
    QianAdvance,
    TaijiVerifyEngine,
    VerificationRequest,
    VerificationResponse,
    XunTune,
)
from opentaiji.wfgy import HallucinationDetector, WFGYVerifier
from opentaiji.workflow import (
    ConditionalEdge,
    Edge,
    Node,
    NodeResult,
    WorkflowConfig,
    WorkflowEngine,
    WorkflowGraph,
    WorkflowState,
)

__version__ = "2.1.0"

__all__ = [
    # Core
    "TaijiAgent",
    "AgentConfig",
    # Taiji Verify (太极验证引擎)
    "TaijiVerifyEngine",
    "VerificationRequest",
    "VerificationResponse",
    "DeltaSCalculator",
    "DeltaSResult",
    "GateZone",
    "KunGuard",
    "QianAdvance",
    "FuReturn",
    "XunTune",
    "PolarisCompiler",
    "FailureModeDetector",
    "FailureMode",
    "FailureSeverity",
    # WFGY
    "WFGYVerifier",
    "HallucinationDetector",
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
