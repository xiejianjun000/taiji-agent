"""
Taiji Verify 模块初始化

太极验证系统 - 核心防幻觉组件
"""

from taiji_agent.wfgy.verifier import (
    HallucinationDetector,
    SelfConsistencyChecker,
    SourceTracer,
    TaijiVerifyKnowledgeEntry,
    TaijiVerifyRule,
    TaijiVerifyResult,
    TaijiVerifier,
)

WFGYVerifier = TaijiVerifier
WFGYRule = TaijiVerifyRule
WFGYKnowledgeEntry = TaijiVerifyKnowledgeEntry
WFGYVerificationResult = TaijiVerifyResult

__all__ = [
    "TaijiVerifier",
    "TaijiVerifyRule",
    "TaijiVerifyKnowledgeEntry",
    "TaijiVerifyResult",
    "HallucinationDetector",
    "SelfConsistencyChecker",
    "SourceTracer",
]
