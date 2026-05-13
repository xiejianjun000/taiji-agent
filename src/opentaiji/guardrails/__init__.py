"""
OpenTaiji Guardrails Module
安全护栏系统 - 参考OpenAI Agents SDK设计
"""
from .core import Guardrail, ValidationResult, GuardrailConfig, GuardrailManager, CompositeGuardrail
from .input_guardrail import InputGuardrail, ContentFilter, RateLimitGuardrail, ProfanityFilter, LengthGuardrail
from .output_guardrail import OutputGuardrail, SensitiveDataFilter, QualityGate, HallucinationGate

__all__ = [
    "Guardrail",
    "ValidationResult",
    "GuardrailConfig",
    "GuardrailManager",
    "CompositeGuardrail",
    "InputGuardrail",
    "ContentFilter",
    "RateLimitGuardrail",
    "ProfanityFilter",
    "LengthGuardrail",
    "OutputGuardrail",
    "SensitiveDataFilter",
    "QualityGate",
    "HallucinationGate",
]
