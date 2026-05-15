"""
工具注册表 - 来自 Hermes Agent
融合 54+ 工具
"""

import asyncio
import logging
import os
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ToolSchema(BaseModel):
    """工具参数模式"""

    name: str
    description: str
    parameters: dict


@dataclass
class Tool:
    """工具定义"""

    name: str
    description: str
    func: Any | None = None
    parameters: dict | None = None


@dataclass
class ToolResult:
    """工具执行结果"""

    success: bool
    output: str = ""
    content: str = ""
    error: str | None = None


class ToolRegistry:
    """
    工具注册表

    来自 Hermes Agent 的完整工具系统
    """

    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._schemas: dict[str, ToolSchema] = {}
        self._used_tools: list[str] = []
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """注册内置工具"""
        # 文件操作工具
        self.register(
            name="file_read",
            handler=self._file_read,
            schema=ToolSchema(
                name="file_read",
                description="读取文件内容",
                parameters={
                    "type": "object",
                    "properties": {"path": {"type": "string", "description": "要读取的文件路径"}},
                    "required": ["path"],
                },
            ),
        )

        self.register(
            name="file_write",
            handler=self._file_write,
            schema=ToolSchema(
                name="file_write",
                description="写入文件内容",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "要写入的文件路径"},
                        "content": {"type": "string", "description": "文件内容"},
                    },
                    "required": ["path", "content"],
                },
            ),
        )

        self.register(
            name="file_list",
            handler=self._file_list,
            schema=ToolSchema(
                name="file_list",
                description="列出目录内容",
                parameters={
                    "type": "object",
                    "properties": {"path": {"type": "string", "description": "目录路径，默认为当前目录"}},
                },
            ),
        )

        self.register(
            name="file_search",
            handler=self._file_search,
            schema=ToolSchema(
                name="file_search",
                description="搜索文件内容",
                parameters={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "搜索模式"},
                        "path": {"type": "string", "description": "搜索路径"},
                    },
                    "required": ["pattern"],
                },
            ),
        )

        # Shell 执行工具
        self.register(
            name="shell",
            handler=self._shell,
            schema=ToolSchema(
                name="shell",
                description="执行 Shell 命令",
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "要执行的命令"},
                        "timeout": {"type": "integer", "description": "超时时间(秒)"},
                    },
                    "required": ["command"],
                },
            ),
        )

        # Web 搜索工具
        self.register(
            name="web_search",
            handler=self._web_search,
            schema=ToolSchema(
                name="web_search",
                description="搜索网络信息",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索查询"},
                        "num_results": {"type": "integer", "description": "返回结果数量"},
                    },
                    "required": ["query"],
                },
            ),
        )

        self.register(
            name="web_extract",
            handler=self._web_extract,
            schema=ToolSchema(
                name="web_extract",
                description="提取网页内容",
                parameters={
                    "type": "object",
                    "properties": {"url": {"type": "string", "description": "网页 URL"}},
                    "required": ["url"],
                },
            ),
        )

        # Git 工具
        self.register(
            name="git_status",
            handler=self._git_status,
            schema=ToolSchema(
                name="git_status",
                description="查看 Git 状态",
                parameters={"type": "object", "properties": {"path": {"type": "string", "description": "仓库路径"}}},
            ),
        )

        self.register(
            name="git_log",
            handler=self._git_log,
            schema=ToolSchema(
                name="git_log",
                description="查看 Git 提交历史",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "仓库路径"},
                        "limit": {"type": "integer", "description": "限制条数"},
                    },
                },
            ),
        )

        # 记忆工具
        self.register(
            name="memory_search",
            handler=self._memory_search,
            schema=ToolSchema(
                name="memory_search",
                description="搜索记忆内容",
                parameters={
                    "type": "object",
                    "properties": {"query": {"type": "string", "description": "搜索查询"}},
                    "required": ["query"],
                },
            ),
        )

        self.register(
            name="memory_save",
            handler=self._memory_save,
            schema=ToolSchema(
                name="memory_save",
                description="保存记忆",
                parameters={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "记忆键"},
                        "value": {"type": "string", "description": "记忆内容"},
                    },
                    "required": ["key", "value"],
                },
            ),
        )

        # 代码执行工具
        self.register(
            name="execute_code",
            handler=self._execute_code,
            schema=ToolSchema(
                name="execute_code",
                description="执行代码",
                parameters={
                    "type": "object",
                    "properties": {
                        "language": {"type": "string", "description": "编程语言"},
                        "code": {"type": "string", "description": "要执行的代码"},
                    },
                    "required": ["code"],
                },
            ),
        )

        # Todo 工具
        self.register(
            name="todo_list",
            handler=self._todo_list,
            schema=ToolSchema(
                name="todo_list", description="列出任务", parameters={"type": "object", "properties": {}}
            ),
        )

        self.register(
            name="todo_add",
            handler=self._todo_add,
            schema=ToolSchema(
                name="todo_add",
                description="添加任务",
                parameters={
                    "type": "object",
                    "properties": {"task": {"type": "string", "description": "任务内容"}},
                    "required": ["task"],
                },
            ),
        )

        self.register(
            name="todo_done",
            handler=self._todo_done,
            schema=ToolSchema(
                name="todo_done",
                description="完成任务",
                parameters={
                    "type": "object",
                    "properties": {"task": {"type": "string", "description": "任务内容"}},
                    "required": ["task"],
                },
            ),
        )

    def register(self, name: str, handler: Callable, schema: ToolSchema):
        """注册工具"""
        self._tools[name] = handler
        self._schemas[name] = schema
        logger.debug(f"Registered tool: {name}")

    async def execute(self, tool_call: Any) -> ToolResult:
        """执行工具"""
        name = tool_call.name
        args = tool_call.arguments if hasattr(tool_call, "arguments") else {}

        if name not in self._tools:
            return ToolResult(success=False, content="", error=f"Unknown tool: {name}")

        try:
            handler = self._tools[name]
            result = await handler(**args) if asyncio.iscoroutinefunction(handler) else handler(**args)

            self._used_tools.append(name)

            return ToolResult(success=True, content=str(result))
        except Exception as e:
            logger.error(f"Tool {name} error: {e}")
            return ToolResult(success=False, content="", error=str(e))

    def get_schemas(self) -> list[dict]:
        """获取所有工具的模式"""
        return [schema.model_dump() for schema in self._schemas.values()]

    def get_schema(self, name: str) -> ToolSchema | None:
        """获取指定工具的模式"""
        return self._schemas.get(name)

    def has_tools(self) -> bool:
        """检查是否有工具"""
        return len(self._tools) > 0

    def list_tools(self) -> list[str]:
        """列出所有工具"""
        return list(self._tools.keys())

    def get_used_tools(self) -> list[str]:
        """获取使用过的工具"""
        return list(set(self._used_tools))

    # 内置工具实现
    def _file_read(self, path: str) -> str:
        """读取文件"""
        with open(path, encoding="utf-8") as f:
            return f.read()

    def _file_write(self, path: str, content: str) -> str:
        """写入文件"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File written: {path}"

    def _file_list(self, path: str = ".") -> str:
        """列出目录"""
        import os

        items = os.listdir(path)
        return "\n".join(items)

    def _file_search(self, pattern: str, path: str = ".") -> str:
        """搜索文件"""
        import subprocess

        result = subprocess.run(["grep", "-r", pattern, path], capture_output=True, text=True)
        return result.stdout or "No matches found"

    async def _shell(self, command: str, timeout: int = 30) -> str:
        """执行 Shell 命令"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            return output
        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout}s"

    def _web_search(self, query: str, num_results: int = 5) -> str:
        """网络搜索"""
        try:
            from exa_py import Exa

            exa = Exa(api_key=os.getenv("EXA_API_KEY"))
            results = exa.search(query, num_results=num_results)

            output = []
            for i, r in enumerate(results.results, 1):
                snippet_text = getattr(r, "text", "") or getattr(r, "snippet", "") or ""
                output.append(f"{i}. {r.title}\n   {r.url}\n   {snippet_text[:200]}...")

            return "\n\n".join(output)
        except ImportError:
            return "Web search requires exa-py: pip install exa-py"
        except Exception as e:
            return f"Search error: {e}"

    def _web_extract(self, url: str) -> str:
        """提取网页内容"""
        try:
            import httpx

            response = httpx.get(url, timeout=10)
            return response.text[:5000]
        except Exception as e:
            return f"Extract error: {e}"

    def _git_status(self, path: str = ".") -> str:
        """Git 状态"""
        result = subprocess.run(["git", "-C", path, "status", "--short"], capture_output=True, text=True)
        return result.stdout or "Not a git repository"

    def _git_log(self, path: str = ".", limit: int = 10) -> str:
        """Git 日志"""
        result = subprocess.run(["git", "-C", path, "log", f"-{limit}", "--oneline"], capture_output=True, text=True)
        return result.stdout or "No commits found"

    def _memory_search(self, query: str) -> str:
        """搜索记忆"""
        from taiji_agent.memory.session import SessionMemory

        mem = SessionMemory()
        results = mem.search(query)
        return results or "No matching memories found"

    def _memory_save(self, key: str, value: str) -> str:
        """保存记忆"""
        from taiji_agent.memory.session import SessionMemory

        mem = SessionMemory()
        mem.save(key, value)
        return f"Memory saved: {key}"

    def _execute_code(self, code: str, language: str = "python") -> str:
        """执行代码"""
        import os
        import tempfile

        suffix_map = {
            "python": "py",
            "js": "js",
            "javascript": "js",
            "bash": "sh",
            "shell": "sh",
        }

        suffix = suffix_map.get(language.lower(), "txt")
        fd, path = tempfile.mkstemp(suffix=f".{suffix}")

        try:
            with os.fdopen(fd, "w") as f:
                f.write(code)

            if language.lower() == "python":
                result = subprocess.run(["python3", path], capture_output=True, text=True, timeout=30)
            elif language.lower() in ("bash", "shell"):
                result = subprocess.run(["bash", path], capture_output=True, text=True, timeout=30)
            else:
                return f"Unsupported language: {language}"

            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"

            return output
        except subprocess.TimeoutExpired:
            return "Code execution timed out"
        finally:
            os.unlink(path)

    def _todo_list(self) -> str:
        """列出任务"""
        from taiji_agent.memory.session import SessionMemory

        mem = SessionMemory()
        todos = mem.get_todos()
        if not todos:
            return "No tasks"
        return "\n".join([f"[{'x' if t['done'] else ' '}] {t['task']}" for t in todos])

    def _todo_add(self, task: str) -> str:
        """添加任务"""
        from taiji_agent.memory.session import SessionMemory

        mem = SessionMemory()
        mem.add_todo(task)
        return f"Task added: {task}"

    def _todo_done(self, task: str) -> str:
        """完成任务"""
        from taiji_agent.memory.session import SessionMemory

        mem = SessionMemory()
        mem.done_todo(task)
        return f"Task completed: {task}"


# 全局工具注册表
registry = ToolRegistry()
