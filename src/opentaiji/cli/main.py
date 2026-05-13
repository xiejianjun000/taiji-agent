"""
OpenTaiji CLI - 命令行界面
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from opentaiji.agent.engine import TaijiAgent, AgentConfig
from opentaiji.wfgy import WFGYVerifier, HallucinationDetector
from opentaiji.souls import SoulLoader
from opentaiji.memory import SessionMemory
from opentaiji.tools import registry

console = Console()


def load_config() -> AgentConfig:
    """加载配置"""
    config = AgentConfig()
    
    # 从环境变量或配置文件加载
    config.api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    config.provider = os.getenv("OPENAIJI_PROVIDER", "anthropic")
    config.model = os.getenv("OPENAIJI_MODEL", "claude-sonnet-4-20250514")
    config.workdir = os.getenv("OPENAIJI_WORKDIR", ".")
    config.wfgy_enabled = os.getenv("OPENAIJI_WFGY", "true").lower() == "true"
    
    return config


async def run_agent(task: str, config: AgentConfig, stream: bool = False):
    """运行 Agent"""
    agent = TaijiAgent(config=config)
    
    if stream:
        console.print(Panel("[bold blue]太极 Agent[/bold blue] 启动中..."))
        full_response = ""
        
        async for chunk in agent.stream_run(task):
            print(chunk, end="", flush=True)
            full_response += chunk
        print()
    else:
        console.print(Panel("[bold blue]太极 Agent[/bold blue] 思考中..."))
        
        result = await agent.run(task)
        
        if result.status.value == "completed":
            console.print(Panel(
                f"[green]✓ 完成 ({result.iterations} 次迭代)[/green]\n\n"
                f"{result.content}"
            ))
        else:
            console.print(Panel(
                f"[yellow]⚠ {result.error}[/yellow]"
            ))


@click.group()
@click.version_option(version="2.0.0")
def cli():
    """OpenTaiji 2.0 - 融合 Hermes Agent + Harness + WFGY"""
    pass


@cli.command()
@click.argument("task", required=False)
@click.option("--provider", "-p", default="anthropic", help="LLM Provider")
@click.option("--model", "-m", default="claude-sonnet-4-20250514", help="Model name")
@click.option("--api-key", "-k", default=None, help="API Key")
@click.option("--soul", "-s", default="default", help="Soul to use")
@click.option("--no-wfgy", is_flag=True, help="Disable WFGY")
@click.option("--stream/--no-stream", default=True, help="Stream response")
def run(task: Optional[str], provider: str, model: str, api_key: Optional[str], soul: str, no_wfgy: bool, stream: bool):
    """运行 Agent"""
    if not task:
        console.print("[yellow]请提供任务描述[/yellow]")
        return
    
    config = AgentConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        soul=soul,
        wfgy_enabled=not no_wfgy,
        stream=stream,
    )
    
    asyncio.run(run_agent(task, config, stream))


@cli.command()
def init():
    """初始化 OpenTaiji"""
    home = Path.home() / ".opentaiji"
    home.mkdir(parents=True, exist_ok=True)
    
    # 创建目录结构
    (home / "souls").mkdir(exist_ok=True)
    (home / "memory").mkdir(exist_ok=True)
    (home / "skills").mkdir(exist_ok=True)
    (home / "logs").mkdir(exist_ok=True)
    
    # 创建示例配置
    config_file = home / "config.yaml"
    if not config_file.exists():
        config_file.write_text("""# OpenTaiji 配置
provider: anthropic
model: claude-sonnet-4-20250514
soul: default
wfgy_enabled: true
max_iterations: 25
""")
    
    console.print(f"[green]✓ 初始化完成[/green]")
    console.print(f"配置目录: {home}")


@cli.command()
def souls():
    """列出可用的 Souls"""
    loader = SoulLoader()
    available = loader.list_souls()
    
    console.print("[bold]可用的 Souls:[/bold]")
    for soul_id in available:
        soul = loader.load(soul_id)
        console.print(f"  • {soul_id}: {soul.name}")


@cli.command()
def tools():
    """列出可用的工具"""
    tool_list = registry.list_tools()
    
    console.print(f"[bold]可用的工具 ({len(tool_list)}):[/bold]")
    for tool in sorted(tool_list):
        schema = registry.get_schema(tool)
        if schema:
            console.print(f"  • {tool}: {schema.description[:50]}...")


@cli.command()
def memory():
    """查看记忆"""
    mem = SessionMemory()
    console.print("[bold]记忆内容:[/bold]")
    
    for key, entry in list(mem._memory.items())[:10]:
        console.print(f"  [{key}] {entry['value'][:100]}...")


@cli.command()
@click.option("--text", "-t", required=True, help="要检测的文本")
def wfgy_check(text: str):
    """WFGY 验证文本"""
    verifier = WFGYVerifier()
    detector = HallucinationDetector()
    
    passed = verifier.verify(text)
    risk = detector.detect(text)
    
    console.print(f"[bold]WFGY 验证结果:[/bold]")
    console.print(f"  通过: {'✓' if passed else '✗'}")
    console.print(f"  幻觉风险: {risk:.1%}")
    
    result = verifier.verify_detailed(text)
    if result.violations:
        console.print(f"[yellow]违规项:[/yellow]")
        for v in result.violations:
            console.print(f"  • {v}")


def main():
    """CLI 入口"""
    if len(sys.argv) == 1:
        cli.main(["run", "--help"])
    else:
        cli()


if __name__ == "__main__":
    main()
