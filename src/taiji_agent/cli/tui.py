"""
Taiji Agent TUI — Textual 交互界面 v3.0

布局:
  ┌─ StatusBar ───────────────────────────┐  ← 绿色线框
  │ ⚕ model │ 101K/1M │ [████░░] 50% │ 56s │
  ├─ ChatLog ─────────────────────────────┤
  │ [军哥] → 问题                          │
  │                                        │
  │   💻 shell → command                   │  ← 工具调用
  │   │ result...                          │  ← 工具结果
  │                                        │
  │ 回复内容...                             │
  │ ── 3 tool(s) used ──                  │
  ├─ InputBox ─────────────────────────────┤
  │ ▌                                     │  ← 固定底部
  └────────────────────────────────────────┘
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll, Horizontal
from textual.reactive import reactive
from textual.widgets import (
    Header, Footer, Input, RichLog, Static, ProgressBar, Label
)
from textual.widget import Widget
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.console import RenderableType


# ══════════════════════════════════════════════════════════════
# Widgets
# ══════════════════════════════════════════════════════════════

class StatusBar(Widget):
    """顶部状态栏：模型 │ 已用token/上限 │ 进度条 │ 耗时（含 TaijiVerifyPro 防幻觉状态）"""

    model_name = reactive("deepseek-v4-pro")
    tokens_used = reactive(0)
    tokens_max = reactive(1_000_000)
    elapsed = reactive(0.0)
    streaming = reactive(False)

    # 🆕 TaijiVerifyPro 防幻觉状态追踪
    verify_status = reactive("PASS")  # PASS / LOW_RISK / MEDIUM_RISK / HIGH_RISK / BLOCK
    verify_count_total = 0
    verify_count_blocked = 0
    verify_count_warned = 0

    def update_verify_status(self, status: str):
        """更新 TaijiVerifyPro 防幻觉状态"""
        self.verify_status = status
        self.verify_count_total += 1

        if status == "BLOCK":
            self.verify_count_blocked += 1
        elif status in ("HIGH_RISK", "MEDIUM_RISK"):
            self.verify_count_warned += 1

    def render(self) -> RenderableType:
        pct = min(self.tokens_used / max(self.tokens_max, 1), 1.0)
        bar_width = 10
        filled = int(pct * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        elapsed_str = f"{int(self.elapsed)}s" if self.elapsed < 60 else f"{int(self.elapsed / 60)}m{int(self.elapsed % 60)}s"
        status_icon = "⚕" if self.streaming else "⏸"

        # 🆕 TaijiVerifyPro 状态图标和颜色
        verify_icon_map = {
            "PASS": ("✅", "green"),
            "LOW_RISK": ("🟢", "green"),
            "MEDIUM_RISK": ("🟡", "yellow"),
            "HIGH_RISK": ("🟠", "yellow bold"),
            "BLOCK": ("🔴", "red bold reverse"),
        }
        v_icon, v_style = verify_icon_map.get(self.verify_status, ("✅", "green"))

        # 统计摘要（如果有拦截/警告记录）
        verify_stats = ""
        if self.verify_count_total > 0:
            if self.verify_count_blocked > 0:
                verify_stats = f" | {v_icon} {self.verify_status} (🚫{self.verify_count_blocked})"
            elif self.verify_count_warned > 0:
                verify_stats = f" | {v_icon} {self.verify_status} (⚠{self.verify_count_warned})"
            else:
                verify_stats = f" | {v_icon} {self.verify_status}"

        text = Text()
        text.append(f" {status_icon} ", style="bold green")
        text.append(f"{self.model_name} ", style="bold white")
        text.append("│ ", style="dim")
        text.append(f"{self._fmt_tokens(self.tokens_used)}/{self._fmt_tokens(self.tokens_max)} ", style="cyan")
        text.append("│ ", style="dim")
        text.append(f"[{bar}] ", style="green" if pct < 0.7 else ("yellow" if pct < 0.9 else "red"))
        text.append(f"{int(pct * 100)}%", style="dim")
        # 🆕 添加防幻觉状态显示
        if verify_stats:
            text.append(verify_stats, style=v_style)
        text.append(" │ ", style="dim")
        text.append(f"⏲ {elapsed_str}", style="dim")
        return text

    @staticmethod
    def _fmt_tokens(n: int) -> str:
        if n >= 1_000_000:
            return f"{n / 1_000_000:.0f}M"
        if n >= 1_000:
            return f"{n / 1_000:.1f}K"
        return str(n)


class ChatLog(RichLog):
    """对话日志 — 可滚动，绿色边框，支持文本选择"""

    def on_mount(self):
        self.border_title = "Taiji Agent"
        self.border_subtitle = "Ctrl+C 退出 | Enter 发送 | Shift+Enter 换行"
        self.highlight = True  # 启用文本选择/复制


class InputCompressed(Message):
    """压缩后的用户输入消息 — 从 InputBox 发出"""
    bubble = True

    def __init__(self, text: str):
        super().__init__()
        self.text = text


class InputBox(Input):
    """底部输入框 — 粘贴自动压缩"""

    def on_mount(self):
        self.border_title = "输入"
        self.placeholder = "输入消息，Enter 发送..."

    def on_input_submitted(self, event: Input.Submitted):
        """输入提交后自动压缩"""
        event.stop()
        value = event.value.strip()
        if value:
            compressed = " ".join(value.split())
            self.value = ""
            self.post_message(InputCompressed(compressed))


# ══════════════════════════════════════════════════════════════
# 工具渲染辅助
# ══════════════════════════════════════════════════════════════

TOOL_ICONS = {
    "shell": "💻", "file_read": "📄", "file_write": "✏️",
    "file_list": "📂", "file_search": "🔍", "web_search": "🌐",
    "web_extract": "📰", "memory_save": "🧠", "memory_search": "🔎",
    "execute_code": "🐍", "todo_list": "📋", "todo_add": "➕",
    "todo_done": "✅", "skills_list": "🎯", "skill_view": "📖",
    "skill_manage": "⚙️", "cronjob": "⏰", "git_status": "📊",
    "git_log": "📜",
}


def render_tool_call(raw: str) -> Text:
    """渲染工具调用行为 Text"""
    content = raw[len("__TOOL_CALL__:"):]
    if ";" in content:
        name, args_str = content.split(";", 1)
    else:
        name, args_str = content, "{}"

    icon = TOOL_ICONS.get(name, "🔧")

    detail = ""
    try:
        args = json.loads(args_str)
        for key in ("command", "path", "query", "pattern", "content", "text"):
            if key in args:
                val = str(args[key])
                detail = val[:80].replace("\n", " ")
                if len(val) > 80:
                    detail += "..."
                break
        if not detail:
            detail = str(args)[:80]
    except Exception:
        detail = args_str[:80]

    t = Text()
    t.append(f"  {icon} ", style="bold")
    t.append(f"{name}", style="bold cyan")
    t.append(" → ", style="dim")
    t.append(detail, style="dim")
    return t


def render_tool_result(raw: str) -> Text:
    """渲染工具结果摘要"""
    text = raw[len("__TOOL_RESULT__:"):]
    if not text.strip():
        return Text("")

    lines = text.strip().split("\n")
    preview_lines = []
    for line in lines[:2]:
        if len(line) > 100:
            line = line[:100] + "..."
        preview_lines.append(line)

    preview = " │ ".join(preview_lines)
    if len(lines) > 2:
        preview += f" ... ({len(lines)} lines)"

    t = Text()
    t.append("  │ ", style="dim")
    t.append(preview, style="dim")
    return t


# ══════════════════════════════════════════════════════════════
# 主 App
# ══════════════════════════════════════════════════════════════

class TaijiTUI(App):
    """太极 Agent 之 Textual 界面"""

    CSS = """
    Screen {
        background: #0d1117;
    }

    StatusBar {
        height: 1;
        dock: top;
        padding: 0 1;
        background: #161b22;
        color: #c9d1d9;
    }

    ChatLog {
        border: solid #2e8b57;
        background: #0d1117;
        color: #c9d1d9;
        padding: 1;
        margin: 1 1 0 1;
        overflow-y: auto;
    }

    InputBox {
        dock: bottom;
        margin: 0 1 1 1;
        border: solid #2e8b57;
        background: #161b22;
        color: #e6edf3;
        height: 3;
    }

    InputBox:focus {
        border: solid #3cb371;
        color: #ffffff;
    }

    /* 光标 — 亮蓝色，确保在深色背景上醒目 */
    InputBox > .input--cursor {
        background: #58a6ff;
        color: #ffffff;
    }

    /* placeholder — 暗灰色 */
    InputBox > .input--placeholder {
        color: #6e7681;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "退出", show=False),
        Binding("escape", "focus_input", "输入", show=False),
    ]

    def __init__(self, agent_config=None):
        super().__init__()
        self.agent_config = agent_config
        self.agent = None
        self._streaming = False
        self._start_time = time.time()
        self._total_tokens = 0
        self._model_name = "deepseek-v4-pro"
        # 用户信息（从 SessionMemory 加载）
        self._bot_name = "Taiji"
        self._user_name = "你"

    def compose(self) -> ComposeResult:
        yield StatusBar()
        yield ChatLog()
        yield InputBox()

    def on_mount(self):
        """启动时初始化"""
        # 从环境变量读取模型名
        self._model_name = os.getenv("TAIJI_AGENT_MODEL", "deepseek-v4-pro")

        status = self.query_one(StatusBar)
        status.model_name = self._model_name

        # 加载用户信息
        try:
            from taiji_agent.memory.session import SessionMemory
            mem = SessionMemory()
            saved_bot = mem.get("bot_name")
            saved_user = mem.get("user_name")
            if saved_bot:
                self._bot_name = saved_bot
            if saved_user:
                self._user_name = saved_user
        except Exception:
            pass

        # 启动计时器
        self.set_interval(1, self._update_clock)

        # 显示 Banner
        chat = self.query_one(ChatLog)
        chat.write(Text(f"  {self._model_name} · anthropic · 19 tools · tui v3.0", style="dim"))
        chat.write("")

        # 初始化 Agent
        asyncio.create_task(self._init_agent())

        # 聚焦输入框
        self.query_one(InputBox).focus()

    def _update_clock(self):
        """更新状态栏时钟和 token 进度"""
        status = self.query_one(StatusBar)
        status.elapsed = time.time() - self._start_time
        status.tokens_used = self._total_tokens

    async def _init_agent(self):
        """后台初始化 Agent"""
        chat = self.query_one(ChatLog)
        try:
            from taiji_agent.agent.engine import TaijiAgent, AgentConfig

            if self.agent_config is None:
                config = AgentConfig(
                    provider=os.getenv("TAIJI_AGENT_PROVIDER", "anthropic"),
                    model=self._model_name,
                    api_key=os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"),
                    base_url=os.getenv("ANTHROPIC_BASE_URL") or os.getenv("TAIJI_AGENT_BASE_URL"),
                    stream=True,
                    verify_enabled=os.getenv("TAIJI_AGENT_VERIFY", "true").lower() == "true",
                )
            else:
                config = self.agent_config

            self.agent = TaijiAgent(config=config)
            self._model_name = config.model

            chat.write(Text(f"[{self._bot_name}] 已就绪。直接说需求即可。", style="bold cyan"))
            chat.write("")

            # 启动梦境
            try:
                from taiji_agent.dream.engine import DreamEngine, DreamConfig
                dream_config = DreamConfig(
                    enabled=os.getenv("TAIJI_DREAM_ENABLED", "true").lower() == "true",
                    interval_hours=int(os.getenv("TAIJI_DREAM_INTERVAL_HOURS", "4")),
                    deep_enabled=os.getenv("TAIJI_DREAM_DEEP_ENABLED", "true").lower() == "true",
                )
                if dream_config.enabled:
                    self._dream_engine = DreamEngine(config=dream_config)
                    self._dream_engine.start()
            except Exception:
                pass

        except Exception as e:
            chat.write(Text(f"[red]初始化失败: {e}[/red]", style="red"))

    def action_focus_input(self):
        self.query_one(InputBox).focus()

    # ══════════════════════════════════════════════════════════
    # 消息处理
    # ══════════════════════════════════════════════════════════

    def on_input_box_input_compressed(self, event):
        """处理压缩后的用户输入"""
        user_input = event.text
        chat = self.query_one(ChatLog)

        # / 命令处理
        if user_input.startswith("/"):
            asyncio.create_task(self._handle_command(user_input))
            return

        # 显示用户消息
        user_text = Text()
        user_text.append(f"[{self._user_name}] → ", style="bold green")
        user_text.append(user_input, style="white")
        chat.write(user_text)

        if not self.agent:
            chat.write(Text("  [red]Agent 尚未就绪，请等待...[/red]", style="red"))
            return

        # 异步处理
        self._streaming = True
        asyncio.create_task(self._process_stream(user_input))

    async def _process_stream(self, user_input: str):
        """流式处理 Agent 回复（含 TaijiVerifyPro 防幻觉增强显示）"""
        chat = self.query_one(ChatLog)
        status = self.query_one(StatusBar)
        status.streaming = True

        full_response = ""
        tool_count = 0
        current_text_line = ""

        try:
            async for chunk in self.agent.stream_run(user_input):
                if not chunk:
                    continue

                s = str(chunk)

                if s.startswith("__TOOL_CALL__:"):
                    # 先刷新累积的文本
                    if current_text_line:
                        chat.write(Text(current_text_line, style="white"))
                        current_text_line = ""
                    tool_count += 1
                    chat.write(render_tool_call(s))
                    continue

                if s.startswith("__TOOL_RESULT__:"):
                    if current_text_line:
                        chat.write(Text(current_text_line, style="white"))
                        current_text_line = ""
                    chat.write(render_tool_result(s))
                    continue

                if s.startswith("[") and ("⚠" in s or "已自动停止" in s or "连续" in s):
                    if current_text_line:
                        chat.write(Text(current_text_line, style="white"))
                        current_text_line = ""
                    chat.write(Text(f"  {s}", style="yellow"))
                    continue

                # ════════════════════════════════════
                # 🆕 TaijiVerifyPro 防幻觉结果特殊渲染
                # （带异常保护，确保不影响正常显示）
                # ════════════════════════════════════
                try:
                    if "🚫 [TaijiVerifyPro 拦截]" in s or "[TaijiVerifyPro 拦截]" in s:
                        if current_text_line:
                            chat.write(Text(current_text_line, style="white"))
                            current_text_line = ""
                        self._render_block_alert(chat, s, status)
                        continue

                    if "⚠️ [TaijiVerifyPro 警告]" in s or "[TaijiVerifyPro 警告]" in s:
                        if current_text_line:
                            chat.write(Text(current_text_line, style="white"))
                            current_text_line = ""
                        self._render_warning_alert(chat, s, status)
                        continue

                    if "[TaijiVerifyPro]" in s and "风险评估" in s:
                        if current_text_line:
                            chat.write(Text(current_text_line, style="white"))
                            current_text_line = ""
                        chat.write(Text(f"  {s}", style="cyan"))
                        status.update_verify_status("MEDIUM_RISK")
                        continue
                except Exception as render_err:
                    # 🛡️ 安全回退：如果渲染失败，显示原始文本
                    chat.write(Text(f"  {s}", style="yellow"))
                    continue

                # 累积文本（流式输出逐段累积）
                current_text_line += s
                full_response += s

                # 遇到换行就输出
                if "\n" in current_text_line:
                    parts = current_text_line.split("\n")
                    for part in parts[:-1]:
                        if part.strip():
                            chat.write(Text(part, style="white"))
                    current_text_line = parts[-1]

            # 刷新最后一行
            if current_text_line.strip():
                chat.write(Text(current_text_line, style="white"))

            # 工具计数
            if tool_count > 0:
                chat.write(Text(f"  ── {tool_count} tool(s) used ──", style="dim"))

            # 估计 token
            self._total_tokens += len(user_input) // 4 + len(full_response) // 4

        except Exception as e:
            chat.write(Text(f"  [red]错误: {e}[/red]", style="red"))
        finally:
            status.streaming = False
            chat.write("")
            self._streaming = False

    def _render_block_alert(self, chat, alert_text: str, status):
        """渲染 BLOCK 拦截警报（红色醒目样式）"""
        try:
            import re

            status.update_verify_status("BLOCK")

            # 提取关键信息
            risk_match = re.search(r'风险评分:\s*([\d.]+)%', alert_text)
            risk_score = float(risk_match.group(1)) / 100 if risk_match else 0.9
            time_match = re.search(r'检测耗时:\s*(\d+)ms', alert_text)
            detect_time = time_match.group(1) if time_match else "?"

            # 渲染醒目的拦截框
            chat.write("")
            chat.write(Text(
                f"  {'╔' + '═'*58 + '╗'}",
                style="bold red"
            ))
            chat.write(Text(
                f"  ║  🚫 [TaijiVerifyPro] 内容已被拦截  ".ljust(59) + "║",
                style="bold reverse red"
            ))
            chat.write(Text(
                f"  {'╠' + '═'*58 + '╣'}",
                style="red"
            ))

            # 风险评分进度条（可视化）
            bar_width = 40
            filled = int(bar_width * risk_score)
            bar = "█" * filled + "░" * (bar_width - filled)
            chat.write(Text(
                f"  ║  ⚠️  风险评分: [{bar}] {risk_score:.0%}".ljust(59) + "║",
                style="yellow"
            ))

            # 高风险维度（提取前2个）
            dim_matches = re.findall(r'🔴 (.*?):\s*([\d.]+)%', alert_text)
            if dim_matches:
                for dim_name, dim_score in dim_matches[:2]:
                    chat.write(Text(
                        f"  ║     🔴 {dim_name}: {float(dim_score)/100:.0%}".ljust(59) + "║",
                        style="red"
                    ))

            # 改进建议（提取第1个）
            rec_match = re.search(r'→\s*(.+)', alert_text)
            if rec_match:
                suggestion = rec_match.group(1)[:50]
                chat.write(Text(
                    f"  ║     💡 {suggestion}".ljust(59) + "║",
                    style="dim"
                ))

            chat.write(Text(
                f"  ║  ⏱️  检测耗时: {detect_time}ms".ljust(59) + "║",
                style="dim"
            ))
            chat.write(Text(
                f"  {'╚' + '═'*58 + '╝'}",
                style="bold red"
            ))
            chat.write("")

        except Exception as e:
            # 🛡️ 安全回退：如果复杂渲染失败，显示简化版本
            chat.write(Text(f"\n  🚫 [TaijiVerifyPro 拦截] {alert_text[:100]}...", style="bold red"))
            chat.write("")

    def _render_warning_alert(self, chat, warning_text: str, status):
        """渲染 WARNING 警告（黄色醒目样式）"""
        try:
            import re

            status.update_verify_status("HIGH_RISK")

            # 提取风险评分
            risk_match = re.search(r'([\d.]+)%', warning_text)
            risk_score = float(risk_match.group(1)) / 100 if risk_match else 0.7

            # 提取建议
            suggest_match = re.search(r'建议:\s*(.+)', warning_text)
            suggestion = suggest_match.group(1)[:60] if suggest_match else ""

            # 渲染警告框（紧凑版）
            chat.write("")
            chat.write(Text(
                f"  ┌────────────────────────────────────────────────────┐",
                style="yellow"
            ))
            chat.write(Text(
                f"  │  ⚠️ [TaijiVerifyPro] 幻觉风险较高: {risk_score:.0%}"
                f"{' '*(38 - len(f'{risk_score:.0%}'))}│",
                style="bold yellow"
            ))
            if suggestion:
                chat.write(Text(
                    f"  │     💡 {suggestion}"
                    f"{' '*(45 - min(len(suggestion), 45))}│",
                    style="dim"
                ))
            chat.write(Text(
                f"  └────────────────────────────────────────────────────┘",
                style="yellow"
            ))
            chat.write("")

        except Exception as e:
            # 🛡️ 安全回退：如果渲染失败，显示简化版本
            chat.write(Text(f"\n  ⚠️ [TaijiVerifyPro 警告] {warning_text[:100]}...", style="bold yellow"))
            chat.write("")

    # ══════════════════════════════════════════════════════════
    # 命令处理（/dream 等）
    # ══════════════════════════════════════════════════════════

    async def _handle_command(self, cmd_line: str):
        """处理 / 命令"""
        chat = self.query_one(ChatLog)
        parts = cmd_line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "/dream":
            await self._cmd_dream(args)
        elif cmd == "/help":
            chat.write(Text("  /dream [status|trigger|results]  — 梦境管理", style="cyan"))
            chat.write(Text("  /help                            — 显示帮助", style="cyan"))
            chat.write(Text("  /quit                            — 退出", style="cyan"))
        elif cmd in ("/quit", "/exit", "/q"):
            self.exit()
        else:
            chat.write(Text(f"  未知命令: {cmd}", style="red"))

    async def _cmd_dream(self, args):
        chat = self.query_one(ChatLog)
        sub = args[0] if args else "status"

        try:
            from taiji_agent.dream.engine import DreamEngine, DreamType
            engine = getattr(self, '_dream_engine', None) or DreamEngine()

            if sub in ("trigger", "deep", "light"):
                dtype = DreamType.DEEP if sub != "light" else DreamType.LIGHT
                engine.trigger_dream(dtype)
                chat.write(Text(f"  ✓ 已触发 {dtype.value} 梦境", style="green"))
            elif sub == "results":
                mem_file = Path.home() / ".taiji" / "memory" / "dream_memories.jsonl"
                if mem_file.exists():
                    with open(mem_file) as f:
                        lines = f.readlines()
                    chat.write(Text(f"  梦境记忆: {len(lines)} 条", style="cyan"))
                else:
                    chat.write(Text("  暂无梦境记忆", style="dim"))
            else:  # status
                running = "运行中" if (hasattr(self, '_dream_engine') and self._dream_engine._running) else "未运行"
                chat.write(Text(f"  梦境状态: {running} | 间隔: {engine.config.interval_hours}h", style="cyan"))
        except ImportError:
            chat.write(Text("  梦境系统未启用", style="yellow"))


# ══════════════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════════════

def run_tui(config=None):
    """启动 TUI"""
    app = TaijiTUI(agent_config=config)
    app.run()


if __name__ == "__main__":
    run_tui()
