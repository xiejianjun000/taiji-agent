"""
Taiji Verify 1.0 -太极验证引擎

基于阴阳距(ΔS)的LLM输出验证系统，包含五大核心模块：
- DeltaS: 阴阳距离计算（余弦相似度）
- KunGuard (坤守/BBMC): 语义残差修正
- QianAdvance (乾进/BBPF): 多路径扰动与稳定性评估
- FuReturn (复归/BBCR): 崩溃恢复状态机
- XunTune (巽调/BBAM): 方差门控注意力调节
"""

from taiji_agent.taiji_verify.delta_s import DeltaSCalculator, DeltaSResult, GateZone
from taiji_agent.taiji_verify.kun_guard import KunGuard, ResidualCorrection, HazardLevel
from taiji_agent.taiji_verify.qian_advance import QianAdvance, PerturbationPath, StabilityScore
from taiji_agent.taiji_verify.fu_return import FuReturn, CollapseState, RecoveryAction
from taiji_agent.taiji_verify.xun_tune import XunTune, AttentionModulation
from taiji_agent.taiji_verify.polaris_compiler import PolarisCompiler, TaskAtom, AtomType
from taiji_agent.taiji_verify.failure_modes import FailureModeDetector, FailureMode, FailureSeverity
from taiji_agent.taiji_verify.engine import TaijiVerifyEngine, VerificationRequest, VerificationResponse

__all__ = [
    # Core engine
    "TaijiVerifyEngine",
    "VerificationRequest", 
    "VerificationResponse",
    # DeltaS
    "DeltaSCalculator",
    "DeltaSResult",
    "GateZone",
    # KunGuard
    "KunGuard",
    "ResidualCorrection",
    "HazardLevel",
    # QianAdvance
    "QianAdvance",
    "PerturbationPath",
    "StabilityScore",
    # FuReturn
    "FuReturn",
    "CollapseState",
    "RecoveryAction",
    # XunTune
    "XunTune",
    "AttentionModulation",
    # Polaris Compiler
    "PolarisCompiler",
    "TaskAtom",
    "AtomType",
    # Failure Modes
    "FailureModeDetector",
    "FailureMode",
    "FailureSeverity",
]

__version__ = "1.0.0"

# Legacy WFGY classes (merged into taiji_verify)
from taiji_agent.taiji_verify.verifier import (
    HallucinationDetector,
    SelfConsistencyChecker,
    SourceTracer,
    WFGYKnowledgeEntry,
    WFGYRule,
    WFGYVerificationResult,
    WFGYVerifier,
)

# ──────────────────────────────────────────────
# TaijiVerifyPro - 业界领先版 (v2.0)
# ──────────────────────────────────────────────
from taiji_agent.taiji_verify.taiji_verify_pro import (
    TaijiVerifyPro,
    VerdictLevel,
    VerifyResult,
    DetectionResult,
    QuickPreChecker,
    SymbolicValidator,
    FactChecker,
    SemanticConsistencyChecker,
    EnhancedFailureModeDetector,
    VectorPipeline,
)

__all__.extend([
    # TaijiVerifyPro
    "TaijiVerifyPro",
    "VerdictLevel",
    "VerifyResult",
    "DetectionResult",
    "QuickPreChecker",
    "SymbolicValidator",
    "FactChecker",
    "SemanticConsistencyChecker",
    "EnhancedFailureModeDetector",
    "VectorPipeline",
])

__version__ = "2.0.0-pro"
