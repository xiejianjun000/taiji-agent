"""
Taiji Verify 1.0 -太极验证引擎

基于阴阳距(ΔS)的LLM输出验证系统，包含五大核心模块：
- DeltaS: 阴阳距离计算（余弦相似度）
- KunGuard (坤守/BBMC): 语义残差修正
- QianAdvance (乾进/BBPF): 多路径扰动与稳定性评估
- FuReturn (复归/BBCR): 崩溃恢复状态机
- XunTune (巽调/BBAM): 方差门控注意力调节
"""

from opentaiji.taiji_verify.delta_s import DeltaSCalculator, DeltaSResult, GateZone
from opentaiji.taiji_verify.kun_guard import KunGuard, ResidualCorrection, HazardLevel
from opentaiji.taiji_verify.qian_advance import QianAdvance, PerturbationPath, StabilityScore
from opentaiji.taiji_verify.fu_return import FuReturn, CollapseState, RecoveryAction
from opentaiji.taiji_verify.xun_tune import XunTune, AttentionModulation
from opentaiji.taiji_verify.polaris_compiler import PolarisCompiler, TaskAtom, AtomType
from opentaiji.taiji_verify.failure_modes import FailureModeDetector, FailureMode, FailureSeverity
from opentaiji.taiji_verify.engine import TaijiVerifyEngine, VerificationRequest, VerificationResponse

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
