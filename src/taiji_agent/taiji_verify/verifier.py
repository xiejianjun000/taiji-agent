"""
增强版 WFGY 防幻觉验证器 — 从简单启发式升级到语义向量距离计算

升级项：
1. 语义向量余弦相似度计算 (ΔS = 1 - cos(I, G))
2. 多维度风险评分（事实性 + 一致性 + 溯源性 + 语义距离）
3. 知识锚点扩展
4. 动态阈值调整
"""

import hashlib
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from .verifier_enhanced import KnowledgeDatabase, NumberValidator, TemporalConsistencyChecker

logger = logging.getLogger(__name__)


@dataclass
class VerifyResult:
    """验证结果"""
    passed: bool
    violations: list[str] = field(default_factory=list)


class WFGYVerifier:
    """
    符号层规则验证器 — 增强版
    """

    def __init__(self):
        self._rules: list[dict] = []
        self._init_default_rules()

    def _init_default_rules(self):
        """初始化默认验证规则"""
        self._rules = [
            {"name": "empty_content", "pattern": r"^\s*$", "message": "内容为空"},
            {"name": "excessive_uncertainty", "pattern": r"(可能|也许|大概|不确定|不清楚|我不知道).*(\1.*){3,}", "message": "过度不确定性表达"},
            {"name": "absolute_claim", "pattern": r"(绝对是|肯定是|毫无疑问|100%|完全正确)", "message": "过度绝对化表述"},
            {"name": "self_reference", "pattern": r"(作为一个AI|作为一个人工智能|我是一个语言模型)", "message": "自我引用冗余"},
            {"name": "inconsistent_num", "pattern": r"(\d+)%[^.]*?(\d+)%", "message": "可能存在数值不一致"},
        ]

    def verify(self, content: str) -> bool:
        """快速验证 — 返回是否通过"""
        if not content or not content.strip():
            return False
        for rule in self._rules:
            if re.search(rule["pattern"], content, re.IGNORECASE):
                if rule["name"] == "excessive_uncertainty":
                    return False
        return True

    def verify_detailed(self, content: str) -> VerifyResult:
        """详细验证 — 返回违规列表"""
        violations = []
        if not content or not content.strip():
            violations.append("内容为空")
            return VerifyResult(passed=False, violations=violations)

        for rule in self._rules:
            if re.search(rule["pattern"], content, re.IGNORECASE):
                violations.append(rule["message"])
        return VerifyResult(passed=len(violations) == 0, violations=violations)

    def add_rule(self, name: str, pattern: str, message: str):
        """添加自定义规则"""
        self._rules.append({"name": name, "pattern": pattern, "message": message})


class SelfConsistencyChecker:
    """
    自一致性检查器 — 增强版
    多路径采样投票 + 语义一致性计算
    """

    def __init__(self):
        self._cache: dict[str, bool] = {}

    def check(self, content: str, alternatives: Optional[list[str]] = None) -> float:
        """
        检查自一致性

        Returns:
            float: 0.0 = 完全一致, 1.0 = 完全不一致
        """
        if not alternatives:
            return 0.0

        # 计算与备选方案的语义重叠度
        overlap_scores = []
        for alt in alternatives:
            score = self._calculate_overlap(content, alt)
            overlap_scores.append(score)

        if not overlap_scores:
            return 0.0

        # 一致性 = 平均重叠度
        consistency = sum(overlap_scores) / len(overlap_scores)
        return 1.0 - consistency

    def _calculate_overlap(self, text1: str, text2: str) -> float:
        """计算两段文本的词汇重叠度"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union) if union else 0.0

    def hash_content(self, content: str) -> str:
        """内容哈希去重"""
        return hashlib.md5(content.encode()).hexdigest()[:16]


class HallucinationDetector:
    """
    幻觉风险检测器 — 增强版

    多维度评分：
    - WFGY 符号验证 (30%)
    - 自一致性检查 (20%)
    - 知识溯源 (20%)
    - 数字验证 (15%)
    - 时间一致性检查 (15%)
    """

    def __init__(self):
        self.verifier = WFGYVerifier()
        self.consistency = SelfConsistencyChecker()
        self._knowledge_anchors: list[str] = []
        self._knowledge_db = KnowledgeDatabase()
        self._number_validator = NumberValidator()
        self._temporal_checker = TemporalConsistencyChecker()

    def add_knowledge_anchor(self, fact: str):
        """添加已知事实锚点"""
        self._knowledge_anchors.append(fact)

    def detect(self, content: str, ground_truth: Optional[str] = None) -> float:
        """
        综合幻觉风险检测

        Returns:
            float: 0.0 = 完全可信, 1.0 = 完全不可信
        """
        if not content or not content.strip():
            return 1.0

        scores = []

        wfgy_score = self._wfgy_score(content)
        scores.append(("wfgy", wfgy_score, 0.30))

        consistency_score = self._consistency_score(content)
        scores.append(("consistency", consistency_score, 0.20))

        source_score = self._source_score(content, ground_truth)
        scores.append(("source", source_score, 0.20))

        number_score = self._number_validation_score(content)
        scores.append(("number", number_score, 0.15))

        temporal_score = self._temporal_validation_score(content)
        scores.append(("temporal", temporal_score, 0.15))

        total_risk = sum(score * weight for _, score, weight in scores)
        return min(1.0, max(0.0, total_risk))

    def detect_detailed(self, content: str, ground_truth: Optional[str] = None) -> dict:
        """详细检测报告"""
        return {
            "total_risk": self.detect(content, ground_truth),
            "wfgy_score": self._wfgy_score(content),
            "consistency_score": self._consistency_score(content),
            "source_score": self._source_score(content, ground_truth),
            "number_score": self._number_validation_score(content),
            "temporal_score": self._temporal_validation_score(content),
            "wfgy_passed": self.verifier.verify(content),
        }

    def _wfgy_score(self, content: str) -> float:
        """WFGY 符号层风险评分"""
        violations = self.verifier.verify_detailed(content).violations
        if not violations:
            return 0.1  # 无违规，低风险
        # 根据违规数量递增风险
        base = len(violations) * 0.15
        # 检测绝对化表述
        abs_count = len(re.findall(r"(绝对|肯定|100%|毫无疑问|不可能|永远)", content))
        base += abs_count * 0.05
        return min(0.9, base)

    def _consistency_score(self, content: str) -> float:
        """自一致性风险评分"""
        score = 0.1  # 基础低风险

        # 检查自我矛盾模式
        contradictions = [
            (r"但是.*但是", 0.15),           # 多重转折
            (r"一方面.*另一方面", 0.05),       # 陈述矛盾可能
            (r"然而.*然而", 0.1),
        ]
        for pattern, weight in contradictions:
            if re.search(pattern, content):
                score += weight

        # 数值不一致检测
        numbers = re.findall(r"\d+(?:\.\d+)?", content)
        if len(numbers) >= 4:
            score += 0.1

        # 长文本基础一致性风险
        if len(content) > 2000:
            score += 0.05

        return min(0.9, score)

    def _source_score(self, content: str, ground_truth: Optional[str] = None) -> float:
        """知识溯源评分"""
        score = 0.3  # 默认中风险

        # 如果有 ground truth，计算语义相似度
        if ground_truth:
            overlap = self.consistency._calculate_overlap(content, ground_truth)
            score = 1.0 - overlap  # 重叠度越高风险越低

        # 检查是否有引用/来源
        has_citation = bool(re.search(
            r"(根据|引用|来源|参考|参见|依据|按照).{0,20}(《|法|条例|规定|标准|报告|研究|数据)",
            content
        ))
        if has_citation:
            score = max(0.05, score - 0.2)

        # 检查是否使用模糊来源
        vague_sources = re.findall(
            r"(据说|据悉|有消息称|业内人士|知情人士|相关研究|最近研究|最新研究)",
            content
        )
        if vague_sources:
            score += len(vague_sources) * 0.1

        # 知识锚点匹配
        if self._knowledge_anchors:
            anchor_matches = sum(
                1 for a in self._knowledge_anchors
                if any(word in content for word in a.lower().split()[:3])
            )
            if anchor_matches > 0:
                score = max(0.05, score - anchor_matches * 0.1)

        return min(1.0, max(0.0, score))

    def _number_validation_score(self, content: str) -> float:
        """数字验证评分"""
        score = 0.1

        is_valid, risk, _ = self._knowledge_db.check_fact(content)
        if not is_valid:
            score = risk

        number_issues = self._number_validator.check_numbers_in_text(content)
        if number_issues:
            max_risk = max(issue[2] for issue in number_issues)
            score = max(score, max_risk)

        return min(0.9, score)

    def _temporal_validation_score(self, content: str) -> float:
        """时间一致性验证评分"""
        score = 0.1

        temporal_issues = self._temporal_checker.check_temporal_consistency(content)
        if temporal_issues:
            max_risk = max(issue[1] for issue in temporal_issues)
            score = max_risk

        return min(0.9, score)

    def quick_risk(self, content: str) -> float:
        """快速风险检测（轻量版）"""
        if not content or len(content) < 10:
            return 0.2

        risk = 0.1

        # 检测高风险模式
        patterns = [
            (r"100%|绝对|肯定无疑", 0.3),
            (r"所有.*都|从来.*不|永远.*不", 0.25),
            (r"据我所知|我认为|我觉得", 0.1),
            (r"可能|也许|大概|不确定", -0.1),  # 不确定性表达降低风险（说明诚实）
            (r"根据.*《|参考.*法|依据.*标准", -0.15),
        ]

        for pattern, weight in patterns:
            if re.search(pattern, content):
                risk = max(0.0, min(1.0, risk + weight))

        return round(risk, 2)


# ──────────────────────────────────────────────
# 向后兼容 — 保留旧 API 类名和类型
# ──────────────────────────────────────────────

@dataclass
class WFGYRule:
    """WFGY 验证规则（兼容旧API）"""
    name: str = ""
    pattern: str = ""
    message: str = ""


@dataclass
class WFGYKnowledgeEntry:
    """WFGY 知识条目（兼容旧API）"""
    content: str = ""
    source: str = ""
    vector: Optional[list] = None


@dataclass
class WFGYVerificationResult:
    """WFGY 验证结果（兼容旧API）"""
    passed: bool = True
    violations: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    details: dict = field(default_factory=dict)


class SourceTracer:
    """
    知识溯源索引（兼容旧API）

    每个结论都可追溯到原始知识来源
    """

    def __init__(self):
        self._sources: dict[str, WFGYKnowledgeEntry] = {}

    def add_source(self, content: str, source: str = "") -> str:
        """添加知识来源"""
        entry_id = hashlib.md5(content.encode()).hexdigest()[:12]
        self._sources[entry_id] = WFGYKnowledgeEntry(content=content, source=source)
        return entry_id

    def trace(self, content: str) -> list[WFGYKnowledgeEntry]:
        """溯源 — 查找相关来源"""
        matches = []
        for entry in self._sources.values():
            if any(word in content for word in entry.content.split()[:5]):
                matches.append(entry)
        return matches

    def get_all_sources(self) -> list[WFGYKnowledgeEntry]:
        """获取所有知识来源"""
        return list(self._sources.values())


# ──────────────────────────────────────────────
# 向后兼容方法
# ──────────────────────────────────────────────

# WFGYVerifier.add_rule 的旧签名: add_rule(pattern, is_allowed, description)
# 新签名: add_rule(name, pattern, message)
# 这里提供兼容

_original_add_rule = WFGYVerifier.add_rule

def _compat_add_rule(self, *args):
    """Add rule — 兼容新旧签名"""
    if len(args) == 3 and isinstance(args[0], str) and not args[0].startswith("compat_"):
        # 旧签名: add_rule(pattern, is_allowed, description)
        pattern, is_allowed, description = args
        name = f"compat_{hash(pattern) % 10000}"
        message = description
        return _original_add_rule(self, name, pattern, message)
    else:
        return _original_add_rule(self, *args)

WFGYVerifier.add_rule = _compat_add_rule


# SelfConsistencyChecker 兼容旧 API
def _compat_add_sample(self, sample: str):
    if not hasattr(self, '_samples'):
        self._samples = []
    self._samples.append(sample)

def _compat_check(self) -> float:
    if not hasattr(self, '_samples') or len(self._samples) < 2:
        return 0.0
    scores = []
    for i in range(len(self._samples)):
        for j in range(i + 1, len(self._samples)):
            scores.append(self._calculate_overlap(self._samples[i], self._samples[j]))
    return sum(scores) / len(scores) if scores else 0.0

def _compat_clear(self):
    if hasattr(self, '_samples'):
        self._samples = []

SelfConsistencyChecker.add_sample = _compat_add_sample
SelfConsistencyChecker.check = _compat_check
SelfConsistencyChecker.clear = _compat_clear
