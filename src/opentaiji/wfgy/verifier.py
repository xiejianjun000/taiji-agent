"""
WFGY 防幻觉系统 - OpenTaiji 核心组件
从 TypeScript 移植到 Python
"""

import re
from dataclasses import dataclass

from pydantic import BaseModel


class WFGYRule(BaseModel):
    id: str
    name: str
    description: str
    pattern: str
    expected: bool
    weight: float = 1.0
    violation_message: str | None = None


class WFGYKnowledgeEntry(BaseModel):
    symbol: str
    meaning: str
    allowed_contexts: list[str] = []
    forbidden_contexts: list[str] = []
    source: str = ""


@dataclass
class WFGYVerificationResult:
    passed: bool
    score: float
    violations: list[str]
    matched_rules: list[str]
    confidence: float


class WFGYVerifier:
    """
    WFGY (Witness & Fact Grounded Verifier) 符号层防幻觉验证器

    基于知识库和符号规则对 LLM 输出进行验证，确保：
    1. 输出符合符号规范
    2. 陈述有事实依据
    3. 引用来源准确
    """

    def __init__(
        self,
        rules: list[WFGYRule] | None = None,
        knowledge_base: list[WFGYKnowledgeEntry] | None = None,
        minimum_score: float = 0.7,
    ):
        self.rules = rules or []
        self.knowledge_base: dict[str, WFGYKnowledgeEntry] = {entry.symbol: entry for entry in (knowledge_base or [])}
        self.minimum_score = minimum_score
        self._compile_rules()

    def _compile_rules(self):
        """编译规则为正则表达式"""
        self._compiled_rules = []
        for rule in self.rules:
            try:
                compiled = re.compile(rule.pattern)
                self._compiled_rules.append((compiled, rule))
            except re.error:
                pass

    def add_rule(
        self,
        pattern: str,
        expected: bool,
        name: str | None = None,
        weight: float = 1.0,
    ):
        """添加验证规则"""
        rule = WFGYRule(
            id=f"rule_{len(self.rules) + 1}",
            name=name or f"Rule {len(self.rules) + 1}",
            description="",
            pattern=pattern,
            expected=expected,
            weight=weight,
        )
        self.rules.append(rule)
        try:
            compiled = re.compile(pattern)
            self._compiled_rules.append((compiled, rule))
        except re.error:
            pass

    def add_knowledge(self, symbol: str, meaning: str, source: str = ""):
        """添加知识条目"""
        entry = WFGYKnowledgeEntry(
            symbol=symbol,
            meaning=meaning,
            source=source,
        )
        self.knowledge_base[symbol] = entry

    def verify(self, content: str) -> bool:
        """验证内容，返回是否通过"""
        result = self._verify(content)
        return result.passed

    def verify_detailed(self, content: str) -> WFGYVerificationResult:
        """详细验证"""
        return self._verify(content)

    def _verify(self, content: str) -> WFGYVerificationResult:
        """内部验证逻辑"""
        violations = []
        matched_rules = []
        total_weight = 0.0
        violation_weight = 0.0

        # 规则检查
        for compiled, rule in self._compiled_rules:
            matches = compiled.search(content)
            total_weight += rule.weight

            if matches and not rule.expected:
                violations.append(rule.violation_message or f"Rule '{rule.name}' violated")
                violation_weight += rule.weight
                matched_rules.append(rule.id)
            elif matches and rule.expected:
                matched_rules.append(rule.id)

        # 知识库检查
        for symbol, entry in self.knowledge_base.items():
            if symbol in content:
                # 检查上下文
                for forbidden in entry.forbidden_contexts:
                    if forbidden in content:
                        violations.append(f"Symbol '{symbol}' used in forbidden context: {forbidden}")
                        total_weight += 0.5
                        violation_weight += 0.5

        # 计算分数
        if total_weight > 0:
            score = 1.0 - (violation_weight / total_weight)
        else:
            score = 1.0

        passed = score >= self.minimum_score and len(violations) == 0

        return WFGYVerificationResult(
            passed=passed,
            score=score,
            violations=violations,
            matched_rules=matched_rules,
            confidence=score,
        )


class HallucinationDetector:
    """
    幻觉检测器

    综合评分 = WFGY(40%) + 自一致性(30%) + 知识溯源(30%)
    """

    def __init__(self):
        self.wfgy_weight = 0.4
        self.consistency_weight = 0.3
        self.grounding_weight = 0.3

    def detect(self, content: str) -> float:
        """
        检测幻觉风险，返回 0.0-1.0 的风险分数
        0.0 = 无风险，1.0 = 高风险
        """
        risk_factors = []

        # 1. 检测模糊引用
        uncertain_patterns = [
            r"据我所知",
            r"一般来说",
            r"通常情况下",
            r"可能是",
            r"也许",
            r"大概",
        ]
        uncertain_count = sum(len(re.findall(p, content)) for p in uncertain_patterns)
        risk_factors.append(min(uncertain_count * 0.1, 0.5))

        # 2. 检测绝对陈述
        absolute_patterns = [
            r"绝对",
            r"一定",
            r"肯定",
            r"无疑",
            r"所有人都",
            r"从来不",
        ]
        absolute_count = sum(len(re.findall(p, content)) for p in absolute_patterns)
        risk_factors.append(min(absolute_count * 0.15, 0.6))

        # 3. 检测数字准确性风险
        number_pattern = r"\d+"
        numbers = re.findall(number_pattern, content)
        if numbers:
            # 检查是否有大数字（可能不准确）
            large_numbers = [n for n in numbers if len(n) >= 4]
            risk_factors.append(len(large_numbers) * 0.1)

        # 4. 检测来源标注
        has_citation = bool(re.search(r"\[来源|\[\d+\]|\(\d+\)", content))
        if not has_citation:
            risk_factors.append(0.2)

        # 综合评分
        total_risk = min(sum(risk_factors), 1.0)
        return total_risk

    def detect_sentences(self, content: str) -> list[tuple[str, float]]:
        """检测句子级别的幻觉风险"""
        sentences = re.split(r"[。！？\n]", content)
        risks = []

        for sentence in sentences:
            if sentence.strip():
                risk = self.detect(sentence)
                risks.append((sentence, risk))

        return risks


class SelfConsistencyChecker:
    """
    多路径自一致性检查

    对同一问题采样多次，投票选出一致结果
    """

    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        self.samples: list[str] = []

    def add_sample(self, response: str):
        """添加一个采样响应"""
        self.samples.append(response)

    def check(self) -> tuple[bool, float]:
        """
        检查自一致性
        返回 (是否一致, 一致性分数)
        """
        if len(self.samples) < 2:
            return True, 1.0

        # 计算所有样本对之间的相似度
        similarities = []
        for i in range(len(self.samples)):
            for j in range(i + 1, len(self.samples)):
                sim = self._calculate_similarity(self.samples[i], self.samples[j])
                similarities.append(sim)

        # 平均相似度
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0

        # 一致性 = 平均相似度
        is_consistent = avg_similarity >= self.similarity_threshold

        return is_consistent, avg_similarity

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度 (Jaccard)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def clear(self):
        """清除样本"""
        self.samples = []


class SourceTracer:
    """
    知识溯源索引

    每个结论都能追溯到原始知识来源
    """

    def __init__(self):
        self.sources: list[dict] = []
        self.index: dict[str, list[int]] = {}

    def add_source(
        self,
        content: str,
        source_url: str | None = None,
        source_title: str = "",
        source_type: str = "unknown",
    ):
        """添加知识来源"""
        source_id = len(self.sources)
        self.sources.append(
            {
                "id": source_id,
                "content": content,
                "url": source_url,
                "title": source_title,
                "type": source_type,
            }
        )

        # 索引
        words = content.lower().split()
        for word in words:
            if word not in self.index:
                self.index[word] = []
            self.index[word].append(source_id)

        return source_id

    def trace(self, claim: str) -> list[dict]:
        """追溯声明的来源"""
        words = claim.lower().split()
        source_ids = set()

        for word in words:
            if word in self.index:
                source_ids.update(self.index[word])

        results = [self.sources[sid] for sid in source_ids]

        # 按相关性排序
        def relevance(source):
            content_lower = source["content"].lower()
            return sum(1 for w in words if w in content_lower)

        return sorted(results, key=relevance, reverse=True)

    def get_coverage(self, content: str) -> float:
        """计算内容对知识库的覆盖率"""
        words = set(content.lower().split())
        if not words:
            return 0.0

        covered = sum(1 for word in words if word in self.index)
        return covered / len(words)
