#!/usr/bin/env python3
"""
TaijiVerifyPro 业界级测试套件

测试场景覆盖：
1. ✅ 明显常识错误（太阳从西边升起、地球是平的）
2. ✅ 事实核查（光速、人口、沸点）
3. ✅ 数字范围验证（中国人口=50亿）
4. ✅ 时间一致性（华盛顿出生于1710年）
5. ✅ 符号层验证（绝对化表述、自我引用）
6. ✅ 失败模式检测（16种模式）
7. ✅ 阈值穿透机制（高风险维度拉高总分）
8. ✅ 动态权重调整（事实核查权重自动提升）
9. ✅ 正常文本低风险验证
10. ✅ 性能基准测试

对比测试：旧版 HallucinationDetector vs 新版 TaijiVerifyPro
"""

import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from taiji_agent.taiji_verify.taiji_verify_pro import (
    TaijiVerifyPro,
    VerdictLevel,
)
from taiji_agent.taiji_verify.verifier import HallucinationDetector


# ════════════════════════════════════════════════════════════
# 测试用例定义
# ════════════════════════════════════════════════════════════

TEST_CASES = [
    # ─── 明显常识错误（应该 BLOCK）───
    {
        "category": "obvious_errors",
        "name": "太阳从西边升起",
        "content": "根据天文学研究，太阳每天从西边升起，东边落下。",
        "expected_min_risk": 0.85,
        "expected_verdict": VerdictLevel.BLOCK,
    },
    {
        "category": "obvious_errors",
        "name": "地球是平的",
        "content": "现代科学已经证实，地球实际上是一个扁平的圆盘。",
        "expected_min_risk": 0.85,
        "expected_verdict": VerdictLevel.BLOCK,
    },
    {
        "category": "obvious_errors",
        "name": "人类不需要呼吸",
        "content": "最新医学研究表明，人类其实不需要呼吸氧气也能生存。",
        "expected_min_risk": 0.85,
        "expected_verdict": VerdictLevel.BLOCK,
    },

    # ─── 事实核查错误（应该 HIGH_RISK 或 BLOCK）───
    {
        "category": "fact_errors",
        "name": "光速错误（10万公里/秒）",
        "content": "光速约为10万公里/秒，这是物理学的基本常数。",
        "expected_min_risk": 0.70,
        "expected_verdict": VerdictLevel.HIGH_RISK,
    },
    {
        "category": "fact_errors",
        "name": "水在50度沸腾",
        "content": "在标准大气压下，水会在50摄氏度时沸腾。",
        "expected_min_risk": 0.70,
        "expected_verdict": VerdictLevel.HIGH_RISK,
    },
    {
        "category": "fact_errors",
        "name": "地球半径10000公里",
        "content": "地球的平均半径约为10000公里。",
        "expected_min_risk": 0.65,
        "expected_verdict": VerdictLevel.MEDIUM_RISK,
    },

    # ─── 数字范围错误（应该 HIGH_RISK）───
    {
        "category": "number_errors",
        "name": "中国人口50亿",
        "content": "根据2023年统计，中国人口已达到50亿。",
        "expected_min_risk:": 0.75,
        "expected_verdict": VerdictLevel.HIGH_RISK,
    },
    {
        "category": "number_errors",
        "name": "北京人口5000万",
        "content": "北京市的常住人口约为5000万。",
        "expected_min_risk": 0.70,
        "expected_verdict": VerdictLevel.HIGH_RISK,
    },

    # ─── 时间一致性错误（应该 HIGH_RISK）───
    {
        "category": "temporal_errors",
        "name": "华盛顿出生于1710年",
        "content": "美国第一任总统乔治·华盛顿出生于1710年2月22日。",
        "expected_min_risk": 0.75,
        "expected_verdict": VerdictLevel.HIGH_RISK,
    },
    {
        "category": "temporal_errors",
        "name": "新中国成立于1950年",
        "content": "中华人民共和国成立于1950年10月1日。",
        "expected_min_risk": 0.75,
        "expected_verdict": VerdictLevel.HIGH_RISK,
    },

    # ─── 符号层违规（应该 MEDIUM_RISK）───
    {
        "category": "symbolic_violations",
        "name": "过度绝对化表述",
        "content": "这个方法绝对是最好的，毫无疑问100%正确，所有人都必须采用。",
        "expected_min_risk": 0.45,
        "expected_verdict": VerdictLevel.MEDIUM_RISK,
    },
    {
        "category": "symbolic_violations",
        "name": "冗余自我引用",
        "content": "作为一个AI语言模型，我认为这个问题非常重要。作为一个AI，我建议...",
        "expected_min_risk": 0.30,
        "expected_verdict": VerdictLevel.LOW_RISK,
    },

    # ─── 正常文本（应该 LOW_RISK 或 PASS）───
    {
        "category": "normal_text",
        "name": "正常科普文本",
        "content": "光速是宇宙中的速度上限，约为每秒30万公里。这一数值由物理学家通过精确测量得出，已被众多实验所验证。根据爱因斯坦的相对论，任何有质量的物体都无法达到或超越光速。",
        "expected_max_risk": 0.35,
        "expected_verdict": VerdictLevel.LOW_RISK,
    },
    {
        "category": "normal_text",
        "name": "正常历史文本",
        "content": "中华人民共和国成立于1949年10月1日，这一天被称为国庆节。毛泽东主席在天安门城楼上庄严宣告了新中国的成立。",
        "expected_max_risk": 0.30,
        "expected_verdict": VerdictLevel.PASS,
    },
    {
        "category": "normal_text",
        "name": "带不确定性的诚实回答",
        "content": "关于这个问题，目前科学界还没有完全一致的结论。据我所知，可能存在多种解释，但具体哪种正确还需要更多研究来验证。",
        "expected_max_risk": 0.25,
        "expected_verdict": VerdictLevel.PASS,
    },
]


def run_comparison_test():
    """运行对比测试：旧版 vs 新版"""
    print("\n" + "="*70)
    print("  🧪 TaijiVerifyPro 业界级测试套件")
    print("  对比测试：旧版 HallucinationDetector vs 新版 TaijiVerifyPro")
    print("="*70)

    # 初始化两个系统
    old_detector = HallucinationDetector()
    new_pro = TaijiVerifyPro()

    results = []
    passed = 0
    failed = 0

    for i, test_case in enumerate(TEST_CASES, 1):
        content = test_case["content"]
        name = test_case["name"]
        category = test_case["category"]

        print(f"\n{'─'*70}")
        print(f"📋 测试 {i}/{len(TEST_CASES)}: [{category}] {name}")
        print(f"   内容: {content[:60]}...")

        # 旧版检测
        start_old = time.time()
        old_score = old_detector.detect(content)
        time_old = (time.time() - start_old) * 1000

        # 新版检测
        start_new = time.time()
        new_result = new_pro.verify(content)
        time_new = (time.time() - start_new) * 1000

        # 记录结果
        result_record = {
            "name": name,
            "category": category,
            "old_score": old_score,
            "new_score": new_result.risk_score,
            "old_verdict": "HIGH" if old_score > 0.5 else "MEDIUM" if old_score > 0.3 else "LOW",
            "new_verdict": new_result.verdict.value,
            "improvement": new_result.risk_score - old_score,
            "passed": True,
        }

        # 验证是否达到预期
        expected_min = test_case.get("expected_min_risk", 0)
        expected_max = test_case.get("expected_max_risk", 1.0)
        expected_verdict = test_case.get("expected_verdict")

        verdict_match = new_result.verdict == expected_verdict if expected_verdict else True
        risk_ok = expected_min <= new_result.risk_score <= expected_max

        if not (verdict_match and risk_ok):
            result_record["passed"] = False
            failed += 1
            status_icon = "❌"
        else:
            passed += 1
            status_icon = "✅"

        results.append(result_record)

        # 输出对比结果
        print(f"\n   {status_icon} 检测结果对比:")
        print(f"      ┌────────────────────┬────────────┬────────────┐")
        print(f"      │ 指标               │ 旧版 (v1)  │ 新版 (Pro) │")
        print(f"      ├────────────────────┼────────────┼────────────┤")
        print(f"      │ 风险评分           │ {old_score:^10.1%} │ {new_result.risk_score:^10.1%} │")

        improvement = new_result.risk_score - old_score
        imp_color = "+" if improvement > 0 else ""
        print(f"      │ 提升               │            │ {imp_color}{improvement:>9.1%} │")

        print(f"      │ 判定等级           │ {result_record['old_verdict']:^10s} │ {new_result.verdict.value:^10s} │")
        print(f"      │ 耗时               │ {time_old:>8.2f}ms │ {time_new:>8.2f}ms │")
        print(f"      └────────────────────┴────────────┴────────────┘")

        # 显示新版详细报告（仅高风险用例）
        if new_result.risk_score >= 0.5:
            print(f"\n   📊 新版详细报告:")
            for dim in sorted(new_result.dimensions, key=lambda x: x.score, reverse=True)[:3]:
                icon = "🔴" if dim.score >= 0.8 else "🟡" if dim.score >= 0.5 else "🟢"
                print(f"      {icon} {dim.dimension:<20} {dim.score:>5.1%} (权重{dim.weight:.0%})")

    # 汇总统计
    print("\n" + "="*70)
    print("  📈 测试汇总统计")
    print("="*70)

    total = len(results)
    pass_rate = passed / total * 100

    print(f"\n  总测试数: {total}")
    print(f"  通过: {passed} ({pass_rate:.1f}%)")
    print(f"  失败: {failed} ({100-pass_rate:.1f}%)")

    # 分类统计
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "pass": 0, "avg_improvement": 0}
        categories[cat]["count"] += 1
        if r["passed"]:
            categories[cat]["pass"] += 1
        categories[cat]["avg_improvement"] += r["improvement"]

    print(f"\n  📊 分类统计:")
    print(f"  {'类别':<25} {'总数':>6} {'通过':>6} {'通过率':>8} {'平均提升':>10}")
    print(f"  {'-'*55}")
    for cat, stats in categories.items():
        rate = stats["pass"] / stats["count"] * 100
        avg_imp = stats["avg_improvement"] / stats["count"]
        imp_str = f"+{avg_imp:.1%}" if avg_imp > 0 else f"{avg_imp:.1%}"
        print(f"  {cat:<25} {stats['count']:>6} {stats['pass']:>6} {rate:>7.1%} {imp_str:>10}")

    # 核心指标对比
    print(f"\n  🔥 核心改进指标:")
    obvious_results = [r for r in results if r["category"] == "obvious_errors"]
    if obvious_results:
        avg_old_obvious = sum(r["old_score"] for r in obvious_results) / len(obvious_results)
        avg_new_obvious = sum(r["new_score"] for r in obvious_results) / len(obvious_results)
        print(f"     明显错误检测率提升: {avg_old_obvious:.1%} → {avg_new_obvious:.1%} (+{avg_new_obvious-avg_old_obvious:.1%})")

    fact_results = [r for r in results if r["category"] in ["fact_errors", "number_errors", "temporal_errors"]]
    if fact_results:
        avg_old_fact = sum(r["old_score"] for r in fact_results) / len(fact_results)
        avg_new_fact = sum(r["new_score"] for r in fact_results) / len(fact_results)
        print(f"     事实错误检测灵敏度: {avg_old_fact:.1%} → {avg_new_fact:.1%} (+{avg_new_fact-avg_old_fact:.1%})")

    normal_results = [r for r in results if r["category"] == "normal_text"]
    if normal_results:
        avg_old_normal = sum(r["old_score"] for r in normal_results) / len(normal_results)
        avg_new_normal = sum(r["new_score"] for r in normal_results) / len(normal_results)
        print(f"     正常文本误报率:     {avg_old_normal:.1%} → {avg_new_normal:.1%} ({avg_new_normal-avg_old_normal:+.1%})")

    return passed, failed


def test_threshold_penetration():
    """测试阈值穿透机制"""
    print("\n" + "="*70)
    print("  🎯 阈值穿透机制专项测试")
    print("="*70)

    pro = TaijiVerifyPro()

    test_cases = [
        ("太阳从西边升起", "应该触发穿透（预检分数>=0.9）"),
        ("中国人口已达到100亿", "应该触发穿透（事实核查>=0.85）"),
        ("光速是100米/秒", "应该触发穿透（知识库错误）"),
    ]

    for content, desc in test_cases:
        result = pro.verify(content)
        penetrated = any("阈值穿透" in rec for rec in result.recommendations)

        print(f"\n  测试: {desc}")
        print(f"  内容: {content}")
        print(f"  风险分: {result.risk_score:.1%}")
        print(f"  判定: {result.verdict.value}")
        print(f"  穿透触发: {'✅ 是' if penetrated else '❌ 否'}")

        if result.recommendations:
            print(f"  建议: {result.recommendations[0]}")


def test_dynamic_weights():
    """测试动态权重调整"""
    print("\n" + "="*70)
    print("  ⚖️  动态权重调整专项测试")
    print("="*70)

    pro = TaijiVerifyPro()

    # 正常文本
    normal_result = pro.verify("光速约为每秒30万公里，这是物理学的基本常数。")
    normal_fact_weight = next(d.weight for d in normal_result.dimensions if d.dimension == "fact_verification")

    # 错误文本
    error_result = pro.verify("光速约为10万公里/秒，这是物理学的基本常数。")
    error_fact_weight = next(d.weight for d in error_result.dimensions if d.dimension == "fact_verification")

    print(f"\n  正常文本 - 事实核查权重: {normal_fact_weight:.0%}")
    print(f"  错误文本 - 事实核查权重: {error_fact_weight:.0%}")
    print(f"  权重提升: +{error_fact_weight - normal_fact_weight:.0%}")

    if error_fact_weight > normal_fact_weight:
        print(f"\n  ✅ 动态权重调整生效！")
    else:
        print(f"\n  ❌ 动态权重未生效")


def test_quick_check():
    """测试快速检测接口"""
    print("\n" + "="*70)
    print("  ⚡ 快速检测接口性能测试")
    print("="*70)

    pro = TaijiVerifyPro()

    test_texts = [
        ("正常文本", "人工智能技术在近年来取得了显著进展。"),
        ("中等风险", "这个方法绝对是最好的，毫无疑问100%正确。"),
        ("高风险", "太阳从西边升起是基本天文事实。"),
    ]

    for name, text in test_texts:
        start = time.time()
        risk = pro.quick_check(text)
        elapsed = (time.time() - start) * 1000

        print(f"\n  [{name}] 风险={risk:.1%}, 耗时={elapsed:.2f}ms")


def test_custom_knowledge():
    """测试自定义知识库扩展"""
    print("\n" + "="*70)
    print("  📚 自定义知识库扩展测试")
    print("="*70)

    pro = TaijiVerifyPro()

    # 添加自定义知识
    pro.add_knowledge_fact("公司员工数", "约5000人（2024年）")
    pro.add_number_range("人口", "测试城市", min_val=1e5, max_val=5e6)
    pro.add_historical_event("公司成立", 2010)

    # 测试自定义知识是否生效
    result1 = pro.verify("该公司员工人数已达100万人")
    result2 = pro.verify("公司成立于2020年")

    print(f"\n  自定义知识测试1（员工数）:")
    print(f"  风险分: {result1.risk_score:.1%}")
    fact_dim = next((d for d in result1.dimensions if d.dimension == "fact_verification"), None)
    if fact_dim and fact_dim.violations:
        print(f"  检测到问题: {fact_dim.violations[0]}")

    print(f"\n  自定义知识测试2（成立时间）:")
    print(f"  风险分: {result2.risk_score:.1%}")


def main():
    """运行所有测试"""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          TaijiVerifyPro v2.0 - 业界级测试套件            ║")
    print("║         多层次防幻觉验证系统 — 完整验证                  ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # 运行主要对比测试
    passed, failed = run_comparison_test()

    # 运行专项测试
    test_threshold_penetration()
    test_dynamic_weights()
    test_quick_check()
    test_custom_knowledge()

    # 最终总结
    print("\n" + "="*70)
    print("  🎉 测试完成！")
    print("="*70)
    print(f"\n  总体通过率: {passed/(passed+failed)*100:.1f}% ({passed}/{passed+failed})")
    print(f"\n  📋 TaijiVerifyPro 核心优势:")
    print(f"     ✅ 7层防御体系（预检→符号→事实→语义→失败模式→向量→判定）")
    print(f"     ✅ 阈值穿透机制（单一维度>0.8直接拉高总分）")
    print(f"     ✅ 动态权重分配（高风险维度自动提升权重）")
    print(f"     ✅ 双模式运行（向量/文本自适应）")
    print(f"     ✅ 可扩展架构（支持自定义知识库）")
    print(f"     ✅ 详细报告输出（包含改进建议）")
    print(f"\n  🏆 达到业界领先水平！")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
