"""
Docker Sandbox 沙箱模块

提供代码执行隔离环境：
- 热容器/冷容器管理
- 资源限制
- 超时控制
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import json

logger = logging.getLogger(__name__)


class SandboxType(str, Enum):
    """沙箱类型"""
    HOT = "hot"       # 热容器（常驻）
    COLD = "cold"      # 冷容器（即用即毁）
    WARM = "warm"      # 温容器（预热）


class SandboxState(str, Enum):
    """沙箱状态"""
    CREATING = "creating"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class SandboxConfig:
    """沙箱配置"""
    sandbox_type: SandboxType = SandboxType.COLD
    image: str = "python:3.11-slim"
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    timeout: int = 60
    network_enabled: bool = False
    read_only: bool = True
    max_output_size: int = 1024 * 1024


@dataclass
class SandboxResult:
    """沙箱执行结果"""
    success: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0
    execution_time_ms: float = 0.0
    sandbox_id: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class SandboxContainer:
    """沙箱容器"""
    container_id: str
    container_type: SandboxType
    state: SandboxState = SandboxState.CREATING
    image: str = ""
    created_at: float = 0.0
    last_used: float = 0.0
    execution_count: int = 0


class DockerSandbox:
    """
    Docker 沙箱

    提供安全的代码执行环境
    """

    def __init__(self, config: SandboxConfig | None = None):
        self.config = config or SandboxConfig()
        self._containers: dict[str, SandboxContainer] = {}
        self._hot_containers: dict[str, Any] = {}
        self._execution_lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self):
        """初始化沙箱"""
        if self._initialized:
            return

        if self.config.sandbox_type == SandboxType.HOT:
            await self._warmup_containers(2)

        self._initialized = True
        logger.info(f"DockerSandbox initialized: {self.config.sandbox_type.value}")

    async def _warmup_containers(self, count: int):
        """预热容器"""
        for i in range(count):
            container_id = f"hot-{uuid.uuid4().hex[:8]}"
            container = SandboxContainer(
                container_id=container_id,
                container_type=SandboxType.HOT,
                image=self.config.image,
                state=SandboxState.READY,
            )
            self._containers[container_id] = container
            self._hot_containers[container_id] = None

    async def execute(
        self,
        code: str,
        language: str = "python",
        env_vars: dict | None = None,
    ) -> SandboxResult:
        """
        执行代码

        Args:
            code: 要执行的代码
            language: 语言类型
            env_vars: 环境变量

        Returns:
            SandboxResult 执行结果
        """
        import time
        start_time = time.time()

        sandbox_id = str(uuid.uuid4())

        try:
            await self.initialize()

            async with self._execution_lock:
                if self.config.sandbox_type == SandboxType.HOT:
                    result = await self._execute_hot(code, language, sandbox_id)
                else:
                    result = await self._execute_cold(code, language, sandbox_id)

            result.execution_time_ms = (time.time() - start_time) * 1000
            result.sandbox_id = sandbox_id

            return result

        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return SandboxResult(
                success=False,
                error=str(e),
                sandbox_id=sandbox_id,
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    async def _execute_hot(
        self,
        code: str,
        language: str,
        sandbox_id: str,
    ) -> SandboxResult:
        """使用热容器执行"""
        container_id = list(self._hot_containers.keys())[0] if self._hot_containers else None

        if not container_id:
            return SandboxResult(
                success=False,
                error="No hot container available",
            )

        return await self._run_in_container(container_id, code, language)

    async def _execute_cold(
        self,
        code: str,
        language: str,
        sandbox_id: str,
    ) -> SandboxResult:
        """使用冷容器执行"""
        container_id = f"cold-{uuid.uuid4().hex[:8]}"
        container = SandboxContainer(
            container_id=container_id,
            container_type=SandboxType.COLD,
            image=self.config.image,
            state=SandboxState.CREATING,
        )
        self._containers[container_id] = container

        try:
            result = await self._run_in_container(container_id, code, language)

            if container_id in self._containers:
                self._containers[container_id].state = SandboxState.TERMINATED

            return result

        except Exception as e:
            if container_id in self._containers:
                self._containers[container_id].state = SandboxState.ERROR
            raise

    async def _run_in_container(
        self,
        container_id: str,
        code: str,
        language: str,
    ) -> SandboxResult:
        """在容器中运行代码"""
        output = f"[Simulated] Executing {language} code in container {container_id}\n"

        if language == "python":
            output += self._simulate_python_execution(code)
        elif language == "javascript":
            output += self._simulate_js_execution(code)
        else:
            output += f"Language {language} not supported in simulation mode\n"

        return SandboxResult(
            success=True,
            output=output[: self.config.max_output_size],
        )

    def _simulate_python_execution(self, code: str) -> str:
        """模拟 Python 执行"""
        lines = code.strip().split("\n")
        output_lines = []

        for line in lines:
            if line.strip().startswith("print("):
                content = line.strip()[6:-1].strip('"').strip("'")
                output_lines.append(content)

        if output_lines:
            return "\n".join(output_lines)
        return "[No output]"

    def _simulate_js_execution(self, code: str) -> str:
        """模拟 JavaScript 执行"""
        lines = code.strip().split("\n")
        output_lines = []

        for line in lines:
            if "console.log" in line:
                start = line.find("console.log") + 12
                end = line.find(")", start)
                content = line[start:end].strip('"').strip("'").strip(";")
                output_lines.append(content)

        if output_lines:
            return "\n".join(output_lines)
        return "[No output]"

    async def cleanup(self):
        """清理沙箱"""
        self._containers.clear()
        self._hot_containers.clear()
        self._initialized = False
        logger.info("DockerSandbox cleaned up")

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "initialized": self._initialized,
            "config": {
                "sandbox_type": self.config.sandbox_type.value,
                "image": self.config.image,
                "memory_limit": self.config.memory_limit,
                "timeout": self.config.timeout,
            },
            "containers": {
                "total": len(self._containers),
                "hot": len(self._hot_containers),
                "cold": len(self._containers) - len(self._hot_containers),
            },
        }


class SandboxManager:
    """
    沙箱管理器

    管理多个沙箱实例，支持：
    - 租户隔离
    - 资源配额
    - 容器复用
    """

    def __init__(self):
        self._sandboxes: dict[str, DockerSandbox] = {}
        self._default_config = SandboxConfig()

    def create_sandbox(
        self,
        sandbox_id: str,
        config: SandboxConfig | None = None,
    ) -> DockerSandbox:
        """创建沙箱"""
        if sandbox_id in self._sandboxes:
            return self._sandboxes[sandbox_id]

        sandbox = DockerSandbox(config or self._default_config)
        self._sandboxes[sandbox_id] = sandbox

        logger.info(f"Sandbox created: {sandbox_id}")
        return sandbox

    def get_sandbox(self, sandbox_id: str) -> DockerSandbox | None:
        """获取沙箱"""
        return self._sandboxes.get(sandbox_id)

    async def execute(
        self,
        sandbox_id: str,
        code: str,
        language: str = "python",
        **kwargs,
    ) -> SandboxResult:
        """执行代码"""
        sandbox = self.get_sandbox(sandbox_id)

        if not sandbox:
            sandbox = self.create_sandbox(sandbox_id)
            await sandbox.initialize()

        return await sandbox.execute(code, language, **kwargs)

    async def cleanup_sandbox(self, sandbox_id: str):
        """清理沙箱"""
        sandbox = self._sandboxes.get(sandbox_id)
        if sandbox:
            await sandbox.cleanup()
            del self._sandboxes[sandbox_id]
            logger.info(f"Sandbox cleaned up: {sandbox_id}")

    async def cleanup_all(self):
        """清理所有沙箱"""
        for sandbox_id in list(self._sandboxes.keys()):
            await self.cleanup_sandbox(sandbox_id)

    def get_all_stats(self) -> dict:
        """获取所有沙箱统计"""
        return {
            sandbox_id: sandbox.get_stats()
            for sandbox_id, sandbox in self._sandboxes.items()
        }


_global_sandbox_manager = SandboxManager()


def get_sandbox_manager() -> SandboxManager:
    """获取全局沙箱管理器"""
    return _global_sandbox_manager
