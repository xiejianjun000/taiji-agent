#!/usr/bin/env python3
"""
TaijiVerifyPro TUI 界面增强测试
模拟 TUI 中的防幻觉结果显示（无需启动完整 Textual 应用）
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from rich.console import Console
from rich.text import Text


# ════════════════════════════════════════════════════════
# 从 tui.py 提取的渲染函数（用于测试）
# ════════════════════════════════════════════════════════

def render_block_alert(console, alert_text: str):
    """渲染 BLOCK 拦截警报（红色醒目样式）"""
    # 提取关键信息
    risk_match = re.search(r'风险评分:\s*([\d.]+)%', alert_text)
    risk_score = float(risk_match.group(1)) / 100 if risk_match else 0.9
    time_match = re.search(r'检测耗时:\s*(\d+)ms', alert_text)
    detect_time = time_match.group(1) if time_match else "?"

    console.print("")
    console.print(
        f"  {'╔' + '═'*58 + '╗'}",
        style="bold red"
    )
    console.print(
        f"  ║  🚫 [TaijiVerifyPro] 内容已被拦截  ".ljust(59) + "║",
        style="bold reverse red"
    )
    console.print(
        f"  {'╠' + '═'*58 + '╣'}",
        style="red"
    )

    # 风险评分进度条（可视化）
    bar_width = 40
    filled = int(bar_width * risk_score)
    bar = "█" * filled + "░" * (bar_width - filled)
    console.print(
        f"  ║  ⚠️  风险评分: [{bar}] {risk_score:.0%}".ljust(59) + "║",
        style="yellow"
    )

    # 高风险维度（提取前2个）
    dim_matches = re.findall(r'🔴 (.*?):\s*([\d.]+)%', alert_text)
    if dim_matches:
        for dim_name, dim_score in dim_matches[:2]:
            console.print(
                f"  ║     🔴 {dim_name}: {float(dim_score)/100:.0%}".ljust(59) + "║",
                style="red"
            )

    # 改进建议（提取第1个）
    rec_match = re.search(r'→\s*(.+)', alert_text)
    if rec_match:
        suggestion = rec_match.group(1)[:50]
        console.print(
            f"  ║     💡 {suggestion}".ljust(59) + "║",
            style="dim"
        )

    console.print(
        f"  ║  ⏱️  检测耗时: {detect_time}ms".ljust(59) + "║",
        style="dim"
    )
    console.print(
        f"  {'╚' + '═'*58 + '╝'}",
        style="bold red"
    )
    console.print("")


def render_warning_alert(console, warning_text: str):
    """渲染 WARNING 警告（黄色醒目样式）"""
    risk_match = re.search(r'([\d.]+)%', warning_text)
    risk_score = float(risk_match.group(1)) / 100 if risk_match else 0.7

    suggest_match = re.search(r'建议:\s*(.+)', warning_text)
    suggestion = suggest_match.group(1)[:60] if suggest_match else ""

    console.print("")
    console.print(
        f"  ┌────────────────────────────────────────────────────┐",
        style="yellow"
    )
    console.print(
        f"  │  ⚠️ [TaijiVerifyPro] 幻觉风险较高: {risk_score:.0%}"
        f"{' '*(38 - len(f'{risk_score:.0%}'))}│",
        style="bold yellow"
    )
    if suggestion:
        console.print(
            f"  │     💡 {suggestion}"
            f"{' '*(45 - min(len(suggestion), 45))}│",
            style="dim"
        )
    console.print(
        f"  └────────────────────────────────────────────────────┘",
        style="yellow"
    )
    console.print("")


def main():
    console = Console()

    print("\n" + "="*70)
    print("  🎨 TaijiVerifyPro v2.0 - TUI 界面增强预览")
    print("  （模拟终端显示效果）")
    print("="*70)

    # ════════════════════════════════════
    # 场景1：BLOCK 拦截（太阳从西边升起）
    # ════════════════════════════════════
    console.print("\n[bold cyan]━━━ 场景1: 用户问「太阳为什么从西边升起？」[/bold cyan]")
    console.print("[dim]用户输入:[/dim] 太阳为什么从西边升起？")
    console.print("[dim]AI原始回复:[/dim] 根据天文学研究，太阳每天从西边升起，东边落下。")
    console.print("[dim]防幻觉检测结果:[/dim]")
    
    BLOCK_ALERT = """\
============================================================
🚫 [TaijiVerifyPro 拦截] 防幻觉检测发现高风险内容
============================================================
⚠️  风险评分: 90.0% (阈值: 70%)
📊  判定等级: BLOCK
⏱️  检测耗时: 2ms

🔍 高风险维度:
   🔴 quick_precheck: 95.0%
      ⚠ 天文学常识错误（置信度95%）

💡 改进建议:
   → ⚠ 阈值穿透强制触发：检测到高风险维度 =95%，总分强制提升至90%
============================================================\
"""
    render_block_alert(console, BLOCK_ALERT)

    # ════════════════════════════════════
    # 场景2：WARNING 警告（光速错误）
    # ════════════════════════════════════
    console.print("\n[bold cyan]━━━ 场景2: 用户问「光速是多少？」[/bold cyan]")
    console.print("[dim]用户输入:[/dim] 光速是多少？我听说大约是10万公里每秒。")
    console.print("[dim]AI原始回复:[/dim] 光速约为10万公里每秒，这是物理学的基本常数。")
    console.print("[dim]防幻觉检测结果:[/dim]")
    
    WARNING_TEXT = "⚠️ [TaijiVerifyPro 警告] 幻觉风险较高: 78.0%\n建议: ⚠ 事实核查发现异常，已提升该维度权重"
    render_warning_alert(console, WARNING_TEXT)

    # ════════════════════════════════════
    # 场景3：StatusBar 显示示例
    # ════════════════════════════════════
    console.print("\n[bold cyan]━━━ StatusBar 状态栏显示示例[/bold cyan]")
    console.print("[dim]（修复后会在状态栏右侧显示防幻觉统计）[/dim]\n")

    status_examples = [
        ("PASS", "✅ PASS", "green", 0, 0),
        ("HIGH_RISK", "🟠 HIGH_RISK (⚠1)", "yellow bold", 0, 1),
        ("BLOCK", "🔴 BLOCK (🚫1)", "red bold reverse", 1, 0),
    ]

    for status, label, style, blocked, warned in status_examples:
        text = Text()
        text.append(f" ⚕ deepseek-v4-pro │ ", style="")
        text.append(f"101K/1M │ ", style="dim")
        text.append(f"[████████░░░░░░░░░░░░░░░░] 50%", style="green")
        text.append(f" │ {label}", style=style)
        text.append(" │ 56s │ ◉")
        
        console.print(text)
        console.print(f"[dim]{status}: 已拦截={blocked}, 已警告={warned}[/dim]\n")

    # ════════════════════════════════════
    # 对比：修复前 vs 修复后
    # ════════════════════════════════════
    console.print("[bold cyan]━━━ 对比：修复前 vs 修复后[/bold cyan]\n")

    console.print("[bold yellow]❌ 修复前（纯文本，无视觉区分）：[/bold yellow]")
    console.print("""
  根据天文学研究，太阳每天从西边升起，东边落下。
  
  ============================================================
  🚫 [TaijiVerifyPro 拦截] 防幻觉检测发现高风险内容
  ============================================================
  ⚠️  风险评分: 90.0% (阈值: 70%)
  📊  判定等级: BLOCK
  ... (400+ 字符的完整报告，与对话混杂)
""")

    console.print("[bold green]✅ 修复后（彩色框+进度条+紧凑信息）：[/bold green]")
    render_block_alert(console, BLOCK_ALERT)

    # ════════════════════════════════════
    # 总结
    # ════════════════════════════════════
    console.print("="*70)
    console.print("  ✅ TUI 界面增强完成！")
    console.print("="*70)
    console.print("""
  [bold]改进点：[/bold]
     1. ✅ [red]BLOCK[/red] 内容用红色醒目框显示（带进度条可视化）
     2. ✅ [yellow]WARNING[/yellow] 内容用黄色紧凑框显示
     3. ✅ StatusBar 右侧显示防幻觉状态图标和统计
     4. ✅ 自动提取关键信息（风险分、耗时、建议）
     5. ✅ 信息精简，不影响阅读体验

  [bold]下一步：[/bold]
     重启 taiji-agent TUI 后即可看到新界面效果！
""")


if __name__ == "__main__":
    main()
