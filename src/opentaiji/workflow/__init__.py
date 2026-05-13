"""
OpenTaiji Workflow Module
状态工作流引擎 - 参考LangGraph设计
"""
from .engine import (
    WorkflowEngine,
    WorkflowState,
    WorkflowConfig,
    NodeResult,
)
from .graph import (
    WorkflowGraph,
    Node,
    Edge,
    ConditionalEdge,
    StateReducer,
)

__all__ = [
    "WorkflowEngine",
    "WorkflowState",
    "WorkflowConfig",
    "NodeResult",
    "WorkflowGraph",
    "Node",
    "Edge",
    "ConditionalEdge",
    "StateReducer",
]
