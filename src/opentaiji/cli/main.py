"""
OpenTaiji CLI - 增强版交互式命令行界面
升级 v2.1: 持续性多轮对话 + 会话管理 + 自动补全 + 历史回放
"""

import asyncio
import atexit
import json
import os
import readline
import shlex
import signal
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from opentaiji.agent.engine import AgentConfig, TaijiAgent, TaskStatus
from opentaiji.memory import SessionMemory
from opentaiji.souls import SoulLoader
from opentaiji.tools import registry
from opentaiji.wfgy import HallucinationDetector, WFGYVerifier

console = Console()

# ══════════════════════════════════════════════════════════════
# 会话持久化层 (SQLite) — 搬迁 Claude Code 会话管理能力
# ══════════════════════════════════════════════════════════════

class SessionStore:
    """会话持久化存储 — 基于 SQLite"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path.home() / ".opentaiji" / "sessions.db"
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._init_tables()

    def _init_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                model TEXT DEFAULT 'claude-sonnet-4-20250514',
                provider TEXT DEFAULT 'anthropic',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_calls TEXT,
                tool_call_id TEXT,
                token_estimate INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS session_meta (
                session_id TEXT PRIMARY KEY,
                wfgy_blocked INTEGER DEFAULT 0,
                wfgy_warnings INTEGER DEFAULT 0,
                tools_used TEXT DEFAULT '[]',
                summary TEXT DEFAULT '',
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
            CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at DESC);
        """)
        self.conn.commit()
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")

    def create_session(self, name: str = "", model: str = "claude-sonnet-4-20250514", provider: str = "anthropic") -> str:
        sid = datetime.now().strftime("%Y%m%d-%H%M%S-") + os.urandom(4).hex()
        name = name or f"会话 {sid[:15]}"
        self.conn.execute(
            "INSERT INTO sessions (id, name, model, provider) VALUES (?, ?, ?, ?)",
            (sid, name, model, provider),
        )
        self.conn.commit()
        return sid

    def list_sessions(self, limit: int = 20) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id, name, model, provider, created_at, updated_at, message_count, total_tokens "
            "FROM sessions ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        cols = ["id", "name", "model", "provider", "created_at", "updated_at", "message_count", "total_tokens"]
        return [dict(zip(cols, r)) for r in rows]

    def save_message(self, session_id: str, role: str, content: str, tool_calls=None, tool_call_id=None):
        token_est = len(content) // 4 if content else 0
        self.conn.execute(
            "INSERT INTO messages (session_id, role, content, tool_calls, tool_call_id, token_estimate) "
            "VALUES (?,?,?,?,?,?)",
            (session_id, role, content, json.dumps(tool_calls) if tool_calls else None, tool_call_id, token_est),
        )
        self.conn.execute(
            "UPDATE sessions SET updated_at=CURRENT_TIMESTAMP, message_count = message_count + 1, "
            "total_tokens = total_tokens + ? WHERE id=?",
            (token_est, session_id),
        )
        self.conn.commit()

    def load_messages(self, session_id: str, limit: int = 200) -> list[dict]:
        rows = self.conn.execute(
            "SELECT role, content, tool_calls, tool_call_id FROM messages "
            "WHERE session_id=? ORDER BY id ASC LIMIT ?",
            (session_id, limit),
        ).fetchall()
        msgs = []
        for r in rows:
            msg = {"role": r[0], "content": r[1]}
            if r[2]:
                msg["tool_calls"] = json.loads(r[2])
            if r[3]:
                msg["tool_call_id"] = r[3]
            msgs.append(msg)
        return msgs

    def update_meta(self, session_id: str, **kwargs):
        existing = self.conn.execute(
            "SELECT 1 FROM session_meta WHERE session_id=?", (session_id,)
        ).fetchone()
        if existing:
            sets = ", ".join(f"{k}=?" for k in kwargs)
            vals = list(kwargs.values()) + [session_id]
            self.conn.execute(f"UPDATE session_meta SET {sets} WHERE session_id=?", vals)
        else:
            keys = ", ".join(kwargs.keys())
            placeholders = ", ".join("?" for _ in kwargs)
            self.conn.execute(
                f"INSERT INTO session_meta (session_id, {keys}) VALUES (?, {placeholders})",
                [session_id] + list(kwargs.values()),
            )
        self.conn.commit()

    def get_meta(self, session_id: str) -> dict:
        row = self.conn.execute(
            "SELECT * FROM session_meta WHERE session_id=?", (session_id,)
        ).fetchone()
        if row:
            return dict(zip(["session_id", "wfgy_blocked", "wfgy_warnings", "tools_used", "summary"], row))
        return {}

    def delete_session(self, session_id: str):
        self.conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()


_session_store: Optional[SessionStore] = None

def get_session_store() -> SessionStore:
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
        atexit.register(_session_store.close)
    return _session_store


# ══════════════════════════════════════════════════════════════
# 交互式对话引擎 — 搬迁 Claude Code 持续对话核心体验
# ══════════════════════════════════════════════════════════════

class InteractiveAgent:
    """交互式太极 Agent — 多轮对话 + 会话切换 + 命令系统"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent: Optional[TaijiAgent] = None
        self.store = get_session_store()
        self.session_id: Optional[str] = None
        self._stop_flag = False
        self._init_readline()

    def _init_readline(self):
        hist_file = Path.home() / ".opentaiji" / ".history"
        hist_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            readline.read_history_file(str(hist_file))
        except (FileNotFoundError, PermissionError, OSError):
            pass
        readline.set_history_length(1000)
        atexit.register(lambda: readline.write_history_file(str(hist_file)))

        self._commands = [
            "/help", "/new", "/sessions", "/switch", "/delete",
            "/history", "/clear", "/compact", "/model", "/soul",
            "/tools", "/wfgy", "/export", "/exit", "/quit", "/q",
        ]

        def completer(text, state):
            options = [c for c in self._commands if c.startswith(text)]
            if state < len(options):
                return options[state]
            return None

        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

    async def _init_agent(self):
        self.agent = TaijiAgent(config=self.config)

    async def start(self, session_id: Optional[str] = None):
        await self._init_agent()

        if session_id:
            sessions = self.store.list_sessions(limit=100)
            matched = [s for s in sessions if s["id"].startswith(session_id)]
            if matched:
                self.session_id = matched[0]["id"]
                self._restore_context()
                console.print(Panel(f"[green]✓ 已恢复会话: {self.session_id}[/green]", title="会话"))
            else:
                console.print(f"[yellow]未找到会话 {session_id}，创建新会话[/yellow]")
                self.session_id = self.store.create_session(model=self.config.model)
                console.print(Panel(f"[green]✓ 新会话: {self.session_id}[/green]", title="会话"))
        else:
            self.session_id = self.store.create_session(model=self.config.model)
            console.print(Panel(f"[green]✓ 新会话: {self.session_id}[/green]", title="会话"))

        # 项目上下文检测
        import os as _os
        project_info = ""
        cwd = _os.getcwd()
        git_dir = _os.path.join(cwd, ".git")
        if _os.path.exists(git_dir):
            project_name = _os.path.basename(cwd)
            project_info = f"\n项目: [cyan]{project_name}[/cyan]"
            # 尝试检测语言
            for lang_file, lang_name in [
                ("pyproject.toml", "Python"), ("package.json", "Node.js"),
                ("go.mod", "Go"), ("Cargo.toml", "Rust"),
                ("pom.xml", "Java"), ("Gemfile", "Ruby"),
            ]:
                if _os.path.exists(_os.path.join(cwd, lang_file)):
                    project_info += f" ([dim]{lang_name}[/dim])"
                    break

        tool_count = len(registry.list_tools())
        banner = Panel(
            f"[bold blue]太极 Agent 交互模式[/bold blue]\n\n"
            f"模型: {self.config.model}\n"
            f"提供者: {self.config.provider}\n"
            f"Soul: {self.config.soul}\n"
            f"WFGY防幻觉: {'✅ 启用' if self.config.wfgy_enabled else '❌ 禁用'}\n"
            f"流式输出: {'✅ 启用' if self.config.stream else '❌ 禁用'}\n"
            f"可用工具: [cyan]{tool_count} 个[/cyan]{project_info}\n\n"
            f"[dim]输入 /help 查看全部命令 | 直接输入问题开始对话[/dim]",
            title="🧘 OpenTaiji 2.1",
        )
        console.print(banner)

        signal.signal(signal.SIGINT, self._handle_sigint)
        await self._chat_loop()

    def _handle_sigint(self, signum, frame):
        console.print("\n[yellow]⚠ 使用 /exit 退出[/yellow]")
        self._stop_flag = False  # 不退出，只中断当前输入

    def _restore_context(self):
        msgs = self.store.load_messages(self.session_id)
        if self.agent and msgs:
            from opentaiji.agent.engine import Message
            restored = []
            for m in msgs:
                restored.append(Message(
                    role=m["role"],
                    content=m["content"],
                    tool_calls=m.get("tool_calls"),
                    tool_call_id=m.get("tool_call_id"),
                ))
            self.agent.messages = restored
            console.print(f"[dim]已恢复 {len(restored)} 条历史消息[/dim]")

    async def _chat_loop(self):
        while not self._stop_flag:
            try:
                user_input = input("\n[你] → ").strip()
            except EOFError:
                console.print("\n[yellow]👋 再见！[/yellow]")
                break

            if not user_input:
                continue

            if user_input.startswith("/"):
                self._stop_flag = await self._handle_command(user_input)
                if self._stop_flag:
                    break
                continue

            await self._process_message(user_input)

    async def _process_message(self, user_input: str):
        self.store.save_message(self.session_id, "user", user_input)

        if self.agent is None:
            await self._init_agent()
        self.agent.messages.append(
            type("Message", (), {
                "role": "user", "content": user_input,
                "tool_calls": None, "tool_call_id": None
            })()
        )

        console.print("\n[太极] → ", end="")
        full_response = ""

        try:
            async for chunk in self.agent.stream_run(user_input):
                if chunk:
                    print(chunk, end="", flush=True)
                    full_response += chunk
            print()
        except Exception as e:
            console.print(f"\n[red]错误: {e}[/red]")
            return

        # WFGY 质量报告
        if self.config.wfgy_enabled and self.agent:
            risk = self.agent.hallucination_detector.detect(full_response)
            if risk > 0.3:
                color = "red" if risk > 0.5 else "yellow"
                console.print(f"[{color}][WFGY 幻觉风险: {risk:.1%}][/{color}]")
                self.store.update_meta(self.session_id, wfgy_warnings=1)

        self.store.save_message(self.session_id, "assistant", full_response)
        self.store.update_meta(
            self.session_id,
            tools_used=json.dumps(self.agent.tools.get_used_tools() if self.agent else []),
        )

    async def _handle_command(self, cmd_line: str) -> bool:
        parts = shlex.split(cmd_line)
        cmd = parts[0].lower()
        args = parts[1:]

        handlers = {
            "/exit": lambda: (console.print("[yellow]👋 再见！[/yellow]"), True)[1],
            "/quit": lambda: (console.print("[yellow]👋 再见！[/yellow]"), True)[1],
            "/q": lambda: (console.print("[yellow]👋 再见！[/yellow]"), True)[1],
            "/help": lambda: self._show_help(),
            "/new": lambda: asyncio.create_task(self._cmd_new(args)),
            "/sessions": lambda: self._cmd_list_sessions(),
            "/switch": lambda: asyncio.create_task(self._cmd_switch(args)),
            "/delete": lambda: self._cmd_delete(args),
            "/history": lambda: self._cmd_history(),
            "/clear": lambda: self._cmd_clear(),
            "/compact": lambda: self._cmd_compact(),
            "/model": lambda: self._cmd_model(args),
            "/soul": lambda: self._cmd_soul(args),
            "/tools": lambda: self._cmd_tools(),
            "/wfgy": lambda: self._cmd_wfgy(args),
            "/export": lambda: self._cmd_export(),
        }

        if cmd in handlers:
            result = handlers[cmd]()
            return result if isinstance(result, bool) else False
        else:
            console.print(f"[red]未知命令: {cmd}。输入 /help 查看帮助[/red]")
            return False

    def _show_help(self):
        table = Table(title="Taiji Agent 交互命令", show_header=True, header_style="bold cyan")
        table.add_column("命令", style="cyan", width=18)
        table.add_column("说明", style="green", width=30)
        table.add_column("示例", style="dim", width=25)

        for cmd, desc, ex in [
            ("/help", "显示帮助信息", "/help"),
            ("/new [名称]", "创建新会话", "/new 环评项目分析"),
            ("/sessions", "列出所有保存的会话", "/sessions"),
            ("/switch <ID>", "切换到指定会话", "/switch 20260517"),
            ("/delete <ID>", "删除指定会话", "/delete 20260517-001"),
            ("/history", "查看当前会话对话历史", "/history"),
            ("/clear", "清除当前会话上下文", "/clear"),
            ("/compact", "压缩上下文（保留摘要）", "/compact"),
            ("/model <name>", "切换模型", "/model claude-sonnet-4-20250514"),
            ("/soul <name>", "切换人格", "/soul default"),
            ("/tools", "列出所有可用工具", "/tools"),
            ("/wfgy [on|off]", "开关 WFGY 防幻觉", "/wfgy off"),
            ("/export", "导出当前会话为 Markdown", "/export"),
            ("/exit, /quit, /q", "退出程序", "/exit"),
        ]:
            table.add_row(cmd, desc, ex)
        console.print(table)
        return False

    async def _cmd_new(self, args):
        name = args[0] if args else ""
        self.session_id = self.store.create_session(name=name, model=self.config.model)
        if self.agent:
            self.agent.messages = []
        console.print(f"[green]✓ 新会话已创建: {self.session_id}[/green]")
        return False

    def _cmd_list_sessions(self):
        sessions = self.store.list_sessions()
        if not sessions:
            console.print("[dim]暂无保存的会话[/dim]")
            return False
        table = Table(title=f"会话列表 ({len(sessions)})", show_header=True)
        table.add_column("ID", style="cyan", width=18)
        table.add_column("名称", style="green", width=25)
        table.add_column("模型", style="blue", width=28)
        table.add_column("消息", justify="right", width=6)
        table.add_column("更新时间", width=20)
        for s in sessions:
            marker = " ←" if s["id"] == self.session_id else ""
            table.add_row(
                s["id"][:16] + marker,
                s["name"],
                s["model"],
                str(s["message_count"]),
                (s["updated_at"] or s["created_at"] or "")[:19],
            )
        console.print(table)
        return False

    async def _cmd_switch(self, args):
        if not args:
            console.print("[red]用法: /switch <会话ID前缀>[/red]")
            return False
        prefix = args[0]
        sessions = self.store.list_sessions(limit=100)
        matched = [s for s in sessions if s["id"].startswith(prefix)]
        if matched:
            self.session_id = matched[0]["id"]
            self._restore_context()
            console.print(f"[green]✓ 已切换到: {self.session_id} ({matched[0]['name']})[/green]")
        else:
            console.print(f"[red]未找到匹配的会话: {prefix}[/red]")
        return False

    def _cmd_delete(self, args):
        if not args:
            console.print("[red]用法: /delete <会话ID前缀>[/red]")
            return False
        prefix = args[0]
        sessions = self.store.list_sessions(limit=100)
        matched = [s for s in sessions if s["id"].startswith(prefix)]
        if matched:
            self.store.delete_session(matched[0]["id"])
            if self.session_id == matched[0]["id"]:
                self.session_id = None
            console.print(f"[green]✓ 已删除会话: {matched[0]['id']}[/green]")
        else:
            console.print(f"[red]未找到匹配的会话: {prefix}[/red]")
        return False

    def _cmd_history(self):
        if not self.session_id:
            console.print("[red]无活跃会话[/red]")
            return False
        msgs = self.store.load_messages(self.session_id, limit=30)
        if not msgs:
            console.print("[dim]暂无对话历史[/dim]")
            return False
        for i, msg in enumerate(msgs, 1):
            role_color = "cyan" if msg["role"] == "user" else "green"
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            content_preview = msg["content"][:150].replace("\n", " ")
            console.print(f"[{role_color}]{i}. {role_icon} {content_preview}...[/{role_color}]")
        return False

    def _cmd_clear(self):
        if self.agent:
            self.agent.messages = []
        console.print("[yellow]✓ 上下文已清除（会话消息仍保留在数据库中）[/yellow]")
        return False

    def _cmd_compact(self):
        """压缩上下文 — 保留系统提示 + 最新对话 + 摘要历史"""
        if not self.agent or not self.agent.messages:
            console.print("[yellow]无活跃上下文可压缩[/yellow]")
            return False

        msgs = self.agent.messages
        if len(msgs) <= 4:
            console.print(f"[dim]上下文仅 {len(msgs)} 条，无需压缩[/dim]")
            return False

        # 保留 system + 最近 3 轮
        system_msgs = [m for m in msgs if hasattr(m, 'role') and m.role == "system"]
        recent = msgs[-6:]  # 最近 3 轮对话（user+assistant）

        # 生成历史摘要
        old_msgs = [m for m in msgs if m not in recent and m not in system_msgs]
        summary_parts = []
        for m in old_msgs:
            content = getattr(m, 'content', '') or ''
            if content and len(content) > 10:
                summary_parts.append(f"[{getattr(m, 'role', '?')}] {content[:80]}...")

        if summary_parts:
            from opentaiji.agent.engine import Message
            summary = "## 历史对话摘要\n" + "\n".join(summary_parts[-20:])
            # 重建消息列表: system + summary + recent
            self.agent.messages = system_msgs + [
                Message(role="user", content="(前文摘要)"),
                Message(role="assistant", content=summary),
            ] + [m for m in recent if getattr(m, 'role', '') != 'system']

        before = len(msgs)
        after = len(self.agent.messages)
        console.print(f"[green]✓ 上下文已压缩: {before} 条 → {after} 条[/green]")
        return False

    def _cmd_model(self, args):
        if not args:
            console.print(f"当前模型: [cyan]{self.config.model}[/cyan]")
            return False
        self.config.model = args[0]
        console.print(f"[green]✓ 已切换模型: {self.config.model}[/green]")
        return False

    def _cmd_soul(self, args):
        if not args:
            console.print(f"当前 Soul: [cyan]{self.config.soul}[/cyan]")
            return False
        self.config.soul = args[0]
        console.print(f"[green]✓ 已切换 Soul: {self.config.soul}[/green]")
        return False

    def _cmd_tools(self):
        tools_list = registry.list_tools()
        table = Table(title=f"可用工具 ({len(tools_list)})", show_header=True)
        table.add_column("工具名", style="cyan", width=18)
        table.add_column("描述", style="green", width=55)
        for t in sorted(tools_list):
            schema = registry.get_schema(t)
            desc = schema.description[:70] if schema else "N/A"
            table.add_row(t, desc)
        console.print(table)
        return False

    def _cmd_wfgy(self, args):
        if not args:
            status = "✅ 启用" if self.config.wfgy_enabled else "❌ 禁用"
            console.print(f"WFGY 防幻觉: {status}")
            return False
        self.config.wfgy_enabled = args[0].lower() in ("on", "true", "1", "enable")
        status = "✅ 启用" if self.config.wfgy_enabled else "❌ 禁用"
        console.print(f"[green]✓ WFGY 防幻觉: {status}[/green]")
        return False

    def _cmd_export(self):
        if not self.session_id:
            console.print("[red]无活跃会话[/red]")
            return False
        msgs = self.store.load_messages(self.session_id)
        export_dir = Path.home() / ".opentaiji" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        export_path = export_dir / f"taiji-{self.session_id}.md"

        with open(export_path, "w", encoding="utf-8") as f:
            f.write(f"# Taiji Agent 会话导出\n\n")
            f.write(f"- 会话ID: {self.session_id}\n")
            f.write(f"- 模型: {self.config.model}\n")
            f.write(f"- 提供者: {self.config.provider}\n")
            f.write(f"- 导出时间: {datetime.now().isoformat()}\n")
            f.write(f"- 消息数: {len(msgs)}\n\n---\n\n")
            for msg in msgs:
                role = "👤 用户" if msg["role"] == "user" else "🤖 太极助手"
                f.write(f"### {role}\n\n{msg['content']}\n\n---\n\n")

        console.print(f"[green]✓ 已导出 {len(msgs)} 条消息到: {export_path}[/green]")
        return False


# ══════════════════════════════════════════════════════════════
# CLI 命令组
# ══════════════════════════════════════════════════════════════

def load_config() -> AgentConfig:
    config = AgentConfig()
    config.api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    config.provider = os.getenv("OPENAIJI_PROVIDER", "anthropic")
    config.model = os.getenv("OPENAIJI_MODEL", "claude-sonnet-4-20250514")
    config.workdir = os.getenv("OPENAIJI_WORKDIR", ".")
    config.wfgy_enabled = os.getenv("OPENAIJI_WFGY", "true").lower() == "true"
    return config


async def run_agent(task: str, config: AgentConfig, stream: bool = False):
    agent = TaijiAgent(config=config)
    if stream:
        console.print(Panel("[bold blue]太极 Agent[/bold blue] 启动中..."))
        full_response = ""
        async for chunk in agent.stream_run(task):
            print(chunk, end="", flush=True)
            full_response += chunk
        print()
        if config.wfgy_enabled:
            risk = agent.hallucination_detector.detect(full_response)
            if risk > 0.3:
                console.print(f"[yellow][WFGY 幻觉风险: {risk:.1%}][/yellow]")
    else:
        console.print(Panel("[bold blue]太极 Agent[/bold blue] 思考中..."))
        result = await agent.run(task)
        if result.status.value == "completed":
            console.print(Panel(f"[green]✓ 完成 ({result.iterations} 次迭代)[/green]\n\n{result.content}"))
        else:
            console.print(Panel(f"[yellow]⚠ {result.error}[/yellow]"))


@click.group()
@click.version_option(version="2.1.0")
def cli():
    """OpenTaiji 2.1 — 融合 Hermes Agent + Harness + WFGY + 交互式对话"""


@cli.command()
@click.argument("task", required=False)
@click.option("--provider", "-p", default="anthropic", help="LLM Provider")
@click.option("--model", "-m", default="claude-sonnet-4-20250514", help="Model name")
@click.option("--api-key", "-k", default=None, help="API Key")
@click.option("--soul", "-s", default="default", help="Soul to use")
@click.option("--no-wfgy", is_flag=True, help="Disable WFGY anti-hallucination")
@click.option("--stream/--no-stream", default=True, help="Stream response")
@click.option("--session", default=None, help="恢复指定会话ID")
def interactive(task, provider, model, api_key, soul, no_wfgy, stream, session):
    """
    进入交互式对话模式

    不提供 TASK 参数进入交互模式，提供则单次执行。
    """
    config = AgentConfig(
        provider=provider, model=model, api_key=api_key,
        soul=soul, wfgy_enabled=not no_wfgy, stream=stream,
    )
    if task:
        asyncio.run(run_agent(task, config, stream))
    else:
        ia = InteractiveAgent(config)
        asyncio.run(ia.start(session_id=session))


@cli.command()
def init():
    """初始化 OpenTaiji 工作环境"""
    home = Path.home() / ".opentaiji"
    for d in ["souls", "memory", "skills", "logs", "exports"]:
        (home / d).mkdir(parents=True, exist_ok=True)

    config_file = home / "config.yaml"
    if not config_file.exists():
        config_file.write_text("""# OpenTaiji 2.1 配置
provider: anthropic
model: claude-sonnet-4-20250514
soul: default
wfgy_enabled: true
wfgy_threshold: 0.5
max_iterations: 25
stream: true
""")
    store = SessionStore()
    store.close()

    console.print("[green]✓ OpenTaiji 2.1 初始化完成[/green]")
    console.print(f"配置目录: {home}")
    console.print(f"会话数据库: {home / 'sessions.db'}")
    console.print()
    console.print("[bold]快速开始:[/bold]")
    console.print("  taiji          # 进入交互式对话模式")
    console.print("  taiji \"你好\"   # 单次对话")


@cli.command()
def souls():
    """列出可用的 Souls (人格)"""
    loader = SoulLoader()
    available = loader.list_souls()
    console.print("[bold]可用的 Souls:[/bold]")
    for soul_id in available:
        soul = loader.load(soul_id)
        console.print(f"  • {soul_id}: {soul.name}")


@cli.command()
def tools():
    """列出可用工具"""
    tool_list = registry.list_tools()
    table = Table(title=f"可用工具 ({len(tool_list)})")
    table.add_column("工具", style="cyan", width=18)
    table.add_column("描述", style="green", width=60)
    for t in sorted(tool_list):
        schema = registry.get_schema(t)
        desc = schema.description[:80] if schema else "N/A"
        table.add_row(t, desc)
    console.print(table)


@cli.command()
@click.option("--limit", "-n", default=10, help="显示条数")
def sessions(limit):
    """查看保存的会话列表"""
    store = SessionStore()
    sessions_list = store.list_sessions(limit=limit)
    store.close()
    if not sessions_list:
        console.print("[dim]暂无保存的会话[/dim]")
        return
    table = Table(title=f"会话列表 ({len(sessions_list)})")
    table.add_column("ID", style="cyan", width=18)
    table.add_column("名称", style="green", width=25)
    table.add_column("模型", style="blue", width=28)
    table.add_column("消息", justify="right")
    table.add_column("更新时间")
    for s in sessions_list:
        table.add_row(s["id"][:16], s["name"], s["model"], str(s["message_count"]), (s["updated_at"] or "")[:19])
    console.print(table)


@cli.command()
@click.argument("session_id", required=False)
def memory(session_id):
    """查看会话记录或内存记忆"""
    if session_id:
        store = SessionStore()
        msgs = store.load_messages(session_id, limit=50)
        store.close()
        console.print(f"[bold]会话 {session_id} ({len(msgs)} 条):[/bold]")
        for msg in msgs:
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            console.print(f"{role_icon} {msg['content'][:200]}...")
    else:
        mem = SessionMemory()
        console.print("[bold]短期记忆:[/bold]")
        items = list(mem._memory.items())[:10]
        if items:
            for key, entry in items:
                console.print(f"  [{key}] {entry['value'][:100]}...")
        else:
            console.print("  [dim](空)[/dim]")


@cli.command()
@click.option("--text", "-t", required=True, help="要检测的文本")
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
def wfgy_check(text, verbose):
    """WFGY 防幻觉验证文本"""
    verifier = WFGYVerifier()
    detector = HallucinationDetector()
    passed = verifier.verify(text)
    risk = detector.detect(text)

    console.print("[bold]WFGY 验证结果:[/bold]")
    status = "✓" if passed else "✗"
    risk_color = "green" if risk < 0.3 else ("yellow" if risk < 0.5 else "red")
    console.print(f"  通过: {status}")
    console.print(f"  幻觉风险: [{risk_color}]{risk:.1%}[/{risk_color}]")

    if verbose:
        result = verifier.verify_detailed(text)
        if result.violations:
            console.print("[yellow]违规项:[/yellow]")
            for v in result.violations:
                console.print(f"  • {v}")
        levels = [
            (0.3, "green", "安全 — 输出可信度高"),
            (0.5, "yellow", "注意 — 建议人工复核"),
            (0.7, "red", "警告 — 存在明显幻觉风险"),
            (1.0, "bold red", "危险 — 强烈建议拦截"),
        ]
        for threshold, color, msg in levels:
            if risk < threshold:
                console.print(f"[{color}]{msg}[/{color}]")
                break


@cli.command()
@click.argument("session_id", required=False)
def export(session_id):
    """导出会话为 Markdown 文件"""
    store = SessionStore()
    if session_id:
        sessions_list = [{"id": session_id, "name": session_id}]
    else:
        sessions_list = store.list_sessions(limit=1)
    if not sessions_list:
        console.print("[red]无可用会话[/red]")
        store.close()
        return
    s = sessions_list[0]
    msgs = store.load_messages(s["id"])
    export_dir = Path.home() / ".opentaiji" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = export_dir / f"taiji-{s['id']}.md"

    with open(export_path, "w", encoding="utf-8") as f:
        f.write(f"# Taiji Agent 会话导出\n\n")
        f.write(f"- 会话ID: {s['id']}\n")
        f.write(f"- 导出时间: {datetime.now().isoformat()}\n")
        f.write(f"- 消息数: {len(msgs)}\n\n---\n\n")
        for msg in msgs:
            role = "👤 用户" if msg["role"] == "user" else "🤖 太极助手"
            f.write(f"### {role}\n\n{msg['content']}\n\n---\n\n")
    console.print(f"[green]✓ 已导出 {len(msgs)} 条消息到: {export_path}[/green]")
    store.close()


def main():
    """CLI 入口 — 默认进入交互模式"""
    if len(sys.argv) == 1:
        cli.main(["interactive"])
    else:
        cli()


if __name__ == "__main__":
    main()
