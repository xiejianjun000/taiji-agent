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

from opentaiji.agent.engine import TaijiAgent, AgentConfig
from opentaiji.wfgy import WFGYVerifier, HallucinationDetector
from opentaiji.souls import SoulLoader, Soul
from opentaiji.memory import SessionMemory
from opentaiji.tools import ToolRegistry
from opentaiji.providers import AnthropicProvider, OpenAIProvider
from opentaiji.providers.chinese import (
    QwenProvider,
    GLMProvider,
    KimiProvider,
    DoubaoProvider,
    CHINESE_PROVIDERS,
    list_chinese_providers,
)
from opentaiji.gateway import MessageGateway, create_gateway
from opentaiji.skills import SkillManager, Skill, SkillCreator
from opentaiji.learning import HonchoMemory, SelfImprovingLoop
from opentaiji.multiagent import (
    MultiAgentCoordinator,
    AgentSwarm,
    MessageBus,
    AgentRole,
    CoordinationMode,
    AgentMessage,
    AgentTask,
    BaseAgent,
    TaijiAgent as MultiAgent,
)
from opentaiji.mcp import (
    MCPServerAdapter,
    MCPServerConfig,
    MCPClientAdapter,
    MCPConnectionConfig,
    MCPProtocol,
    MCPTool,
    MCPResource,
)
from opentaiji.guardrails import (
    Guardrail,
    ValidationResult,
    GuardrailConfig,
    GuardrailManager,
    InputGuardrail,
    ContentFilter,
    RateLimitGuardrail,
    OutputGuardrail,
    SensitiveDataFilter,
    QualityGate,
)
from opentaiji.observability import (
    TracingManager,
    TraceSpan,
    TraceEvent,
    SpanStatus,
    SpanKind,
    ConsoleExporter,
    FileExporter,
    LangSmithExporter,
)
from opentaiji.hitl import (
    ApprovalQueue,
    ApprovalRequest,
    ApprovalDecision,
    ApprovalStatus,
    ApprovalConfig,
    ConfidenceGate,
    ConfidenceLevel,
    Checkpoint,
    CheckpointManager,
)
from opentaiji.workflow import (
    WorkflowEngine,
    WorkflowState,
    WorkflowConfig,
    NodeResult,
    WorkflowGraph,
    Node,
    Edge,
    ConditionalEdge,
)
from opentaiji.handoffs import (
    Handoff,
    HandoffConfig,
    HandoffManager,
    HandoffResult,
    HandoffContext,
    AgentRegistry,
)
from opentaiji.code import (
    CodeExecutor,
    ExecutionResult,
    ExecutionStatus,
    SandboxConfig,
    SandboxManager,
)
from opentaiji.visual import (
    WorkflowExporter,
    MermaidExporter,
    ASCIIExporter,
    JSONExporter,
    HTMLExporter,
    ExportFormat,
)


__version__ = "2.0.0"

__all__ = [
    # Core
    "TaijiAgent",
    "AgentConfig",
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
