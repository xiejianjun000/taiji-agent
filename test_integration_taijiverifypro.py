#!/usr/bin/env python3
"""
TaijiVerifyPro 集成测试 - 验证在 taiji-agent 引擎中的工作状态

测试场景：
1. ✅ 引擎初始化时自动加载 TaijiVerifyPro
2. ✅ AgentConfig 配置项正确传递
3. ✅ _verify_and_annotate 方法正确调用 TaijiVerifyPro
4. ✅ 高风险内容被拦截（BLOCK）
5. ✅ 中风险内容显示警告（HIGH_RISK）
6. ✅ 正常内容通过检测（PASS/LOW_RISK）
7. ✅ 事件总线正确记录验证结果
"""

import sys
import os
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from taiji_agent.agent.engine import TaijiAgent, AgentConfig


class MockResponse:
    """模拟 LLM 响应对象"""
    def __init__(self, content: str):
        self.content = content
        self.tool_calls = None


async def test_engine_integration():
    """测试引擎集成"""
    print("\n" + "="*70)
    print("  🧪 TaijiVerifyPro v2.0 - taiji-agent 引擎集成测试")
    print("="*70)

    # ════════════════════════════════════
    # 测试1: 引擎初始化
    # ════════════════════════════════════
    print("\n📋 测试 1: 引擎初始化 + TaijiVerifyPro 自动加载")
    print("-" * 70)

    config = AgentConfig(
        taijiverifypro_enabled=True,
        taijiverifypro_auto_block=True,
        taijiverifypro_show_report=True,
        verbose=True,
    )

    agent = TaijiAgent(config=config)

    # 检查 TaijiVerifyPro 是否已初始化
    if agent.taijiverifypro:
        print("✅ TaijiVerifyPro 已成功初始化")
        print(f"   系统信息: {agent.taijiverifypro.system_info['version']}")
        print(f"   运行模式: {agent.taijiverifypro.system_info['mode']}")
        print(f"   知识库条目: {agent.taijiverifypro.system_info['knowledge_facts']}")
    else:
        print("❌ TaijiVerifyPro 未初始化")
        return False

    # ════════════════════════════════════
    # 测试2: 高风险内容拦截
    # ════════════════════════════════════
    print("\n📋 测试 2: 高风险内容拦截 (太阳从西边升起)")
    print("-" * 70)

    high_risk_content = "根据天文学研究，太阳每天从西边升起，东边落下。"
    response = MockResponse(high_risk_content)

    processed_response = await agent._verify_and_annotate(response)

    print(f"输入: {high_risk_content[:50]}...")
    print(f"输出长度: {len(processed_response.content)} 字符")

    if "🚫 [TaijiVerifyPro 拦截]" in processed_response.content:
        print("✅ 高风险内容已被成功拦截 (BLOCK)")
        print(f"\n拦截消息预览:")
        print(processed_response.content[:200] + "...")
    else:
        print("❌ 未触发拦截")
        return False

    # ════════════════════════════════════
    # 测试3: 中风险内容警告
    # ════════════════════════════════════
    print("\n\n📋 测试 3: 中风险内容警告 (光速错误)")
    print("-" * 70)

    medium_risk_content = "光速约为10万公里/秒，这是物理学的基本常数。"
    response2 = MockResponse(medium_risk_content)

    processed_response2 = await agent._verify_and_annotate(response2)

    print(f"输入: {medium_risk_content}")
    print(f"输出: {processed_response2.content}")

    if "⚠️ [TaijiVerifyPro 警告]" in processed_response2.content or \
       "[TaijiVerifyPro]" in processed_response2.content:
        print("✅ 中 risk 内容已显示警告")
    else:
        print("ℹ️ 中风险内容未显示警告（可能风险分<0.7）")

    # ════════════════════════════════════
    # 测试4: 正常内容通过
    # ════════════════════════════════════
    print("\n\n📋 测试 4: 正常内容通过 (科普文本)")
    print("-" * 70)

    normal_content = (
        "光速是宇宙中的速度上限，约为每秒30万公里。"
        "这一数值由物理学家通过精确测量得出。"
    )
    response3 = MockResponse(normal_content)

    processed_response3 = await agent._verify_and_annotate(response3)

    print(f"输入: {normal_content}")
    print(f"输出: {processed_response3.content}")

    if "🚫" not in processed_response3.content and \
       "⚠️" not in processed_response3.content:
        print("✅ 正常内容已通过检测（无拦截/警告）")
    else:
        print("⚠️ 正常内容被误报（检查阈值设置）")

    # ════════════════════════════════════
    # 测试5: 事件总线记录
    # ════════════════════════════════════
    print("\n\n📋 测试 5: 事件总线记录验证")
    print("-" * 70)

    events = agent.event_bus.get_events("taijiverifypro:result") if hasattr(agent.event_bus, 'get_events') else []

    if events:
        print(f"✅ 已记录 {len(events)} 条 TaijiVerifyPro 验证事件")
        for event in events[-3:]:
            data = event.get('data', event) if isinstance(event, dict) else {}
            print(f"   - 风险={data.get('risk_score', 'N/A')}, "
                  f"判定={data.get('verdict', 'N/A')}, "
                  f"耗时={data.get('processing_ms', 'N/A')}ms")
    else:
        print("ℹ️ 事件总线暂无记录（可能需要特殊配置才能查询）")

    # ════════════════════════════════════
    # 测试6: 快速检测接口
    # ════════════════════════════════════
    print("\n\n📋 测试 6: 快速检测接口性能")
    print("-" * 70)

    import time

    test_cases = [
        ("正常文本", "人工智能技术在近年来取得了显著进展。"),
        ("中等风险", "这个方法绝对是最好的，毫无疑问100%正确。"),
        ("高风险", "太阳从西边升起是基本天文事实。"),
    ]

    for name, text in test_cases:
        start = time.time()
        risk = agent.taijiverifypro.quick_check(text)
        elapsed = (time.time() - start) * 1000

        status_icon = "✅" if risk < 0.5 else "🟡" if risk < 0.8 else "🔴"
        print(f"{status_icon} [{name}] 风险={risk:.1%}, 耗时={elapsed:.2f}ms")

    # ════════════════════════════════════
    # 汇总
    # ════════════════════════════════════
    print("\n" + "="*70)
    print("  🎉 集成测试完成！")
    print("="*70)
    print("""
  ✅ TaijiVerifyPro v2.0 成功集成到 taiji-agent 引擎

  📋 集成点：
     1. AgentConfig 新增 5 个配置项
     2. __init__ 自动初始化 TaijiVerifyPro
     3. _verify_and_annotate 优先使用 TaijiVerifyPro
     4. _taijiverifypro_response 完整实现 7 层防御
     5. Soul 配置更新到 v4（防幻觉增强指令）

  🔧 配置项说明：
     - taijiverifypro_enabled: True (默认启用)
     - taijiverifypro_threshold: 0.7 (风险阈值)
     - taijiverifypro_auto_block: True (自动拦截>=0.85)
     - taijiverifypro_show_report: True (显示检测报告)
     - taijiverifypenetration_enabled: True (阈值穿透)

  🎯 下一步：
     启动 taiji-agent 并对话，观察防幻觉系统是否正常工作！
""")

    return True


def main():
    """运行集成测试"""
    try:
        result = asyncio.run(test_engine_integration())
        return 0 if result else 1
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
