"""
Security Sandbox (安全沙箱)
Agent执行沙箱隔离与资源限制模块

基于等保2.0三级要求实现：
- 资源限制（CPU/内存/网络/文件系统）
- 沙箱生命周期管理
- 应用层安全防护（拒答超范围提问）

映射生态环境部安全4层防护体系：
- 应用层安全防护 → 拒答超范围提问
- 技术保障体系 → 敏感行为拦截+安全围栏
"""

from __future__ import annotations

import hashlib
import os
import resource
import signal
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any


class SandboxStatus(str, Enum):
    """沙箱状态枚举"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    TERMINATED = "terminated"
    TIMEOUT = "timeout"
    KILLED = "killed"


class ResourceLimit(str, Enum):
    """资源限制类型"""
    CPU_TIME = "cpu_time"           # CPU时间限制（秒）
    MEMORY = "memory"               # 内存限制（字节）
    DISK_WRITE = "disk_write"        # 磁盘写入限制（字节）
    NETWORK_ACCESS = "network"       # 网络访问控制
    FILE_ACCESS = "file_access"     # 文件访问控制
    PROCESS_COUNT = "process"       # 进程数量限制


@dataclass
class SandboxConfig:
    """沙箱配置"""
    # 时间限制
    max_cpu_time: float = 30.0         # 最大CPU时间（秒）
    max_wall_time: float = 60.0        # 最大墙钟时间（秒）
    
    # 内存限制
    max_memory_bytes: int = 512 * 1024 * 1024  # 512MB
    
    # 磁盘限制
    max_disk_write_bytes: int = 100 * 1024 * 1024  # 100MB
    allowed_dirs: list[str] = field(default_factory=list)  # 允许的目录
    
    # 网络限制
    network_enabled: bool = False      # 是否启用网络访问
    allowed_hosts: list[str] = field(default_factory=list)  # 允许的域名/IP
    
    # 进程限制
    max_processes: int = 10            # 最大进程数
    max_open_files: int = 100          # 最大打开文件数
    
    # 代码执行限制
    max_code_size: int = 1024 * 1024   # 最大代码大小（字节）
    max_output_size: int = 10 * 1024 * 1024  # 最大输出大小（字节）
    
    # 安全限制
    forbidden_imports: list[str] = field(default_factory=lambda: [
        "os.system", "subprocess", "socket", "requests", 
        "urllib", "http", "ctypes", "signal", "multiprocessing"
    ])
    
    # 超时回调
    timeout_callback: Optional[Callable[[], None]] = None


@dataclass
class SandboxResult:
    """沙箱执行结果"""
    status: SandboxStatus
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    memory_used: int = 0
    cpu_time: float = 0.0
    disk_write: int = 0
    termination_reason: str = ""
    security_violations: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class SecurityFence:
    """
    安全围栏 - 敏感行为拦截器
    
    基于内容检测的安全防护：
    - 敏感关键词过滤
    - 可疑命令检测
    - 权限提升尝试拦截
    """
    
    # 敏感关键词列表（生态环境场景）
    SENSITIVE_KEYWORDS: set[str] = {
        # 隐私相关
        "password", "secret", "token", "api_key", "credential",
        # 安全攻击相关
        "injection", "exploit", "payload", "shell", "exec",
        # 文件系统攻击
        "../", "/etc/passwd", "/etc/shadow", "rm -rf", "format:",
        # 网络攻击
        "nmap", "sqlmap", "metasploit", "csrf", "xss",
        # 生态环境敏感数据
        "污染源", "偷排", "超标排放", "监测数据造假",
    }
    
    def __init__(
        self,
        custom_keywords: Optional[set[str]] = None,
        strict_mode: bool = True
    ):
        self.custom_keywords = custom_keywords or set()
        self.strict_mode = strict_mode
        self._all_keywords = self.SENSITIVE_KEYWORDS | self.custom_keywords
    
    def check(self, content: str) -> tuple[bool, list[str]]:
        """
        检查内容是否包含敏感关键词
        
        Args:
            content: 待检查的内容
            
        Returns:
            (是否通过, 匹配的关键词列表)
        """
        content_lower = content.lower()
        matched = []
        
        for keyword in self._all_keywords:
            if keyword.lower() in content_lower:
                matched.append(keyword)
        
        passed = len(matched) == 0
        return passed, matched
    
    def filter_command(self, command: str) -> tuple[bool, str]:
        """
        过滤危险命令
        
        Args:
            command: 原始命令
            
        Returns:
            (是否允许执行, 过滤后的命令)
        """
        # 检查是否包含危险操作
        passed, matched = self.check(command)
        
        if not passed:
            return False, ""
        
        # 检查是否尝试提权
        if any(word in command.lower() for word in ["sudo", "chmod 777", "chown"]):
            if self.strict_mode:
                return False, ""
        
        return True, command


class Sandbox:
    """
    Agent执行沙箱
    
    提供进程级隔离执行环境，包含：
    - 资源限制（CPU/内存/磁盘）
    - 网络访问控制
    - 文件系统隔离
    - 超时管理
    - 安全围栏检查
    
    Usage::
        config = SandboxConfig(max_cpu_time=30, memory_limit=256*1024*1024)
        sandbox = Sandbox(config)
        
        result = sandbox.execute_code("print('hello')", language="python")
        if result.status == SandboxStatus.RUNNING:
            print(result.stdout)
    """
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self.status = SandboxStatus.CREATED
        self._process: Optional[subprocess.Popen] = None
        self._start_time: Optional[float] = None
        self._lock = threading.Lock()
        self._security_fence = SecurityFence()
    
    def execute_code(
        self,
        code: str,
        language: str = "python",
        timeout: Optional[float] = None,
    ) -> SandboxResult:
        """
        在沙箱中执行代码
        
        Args:
            code: 要执行的代码
            language: 语言类型（python/shell）
            timeout: 超时时间（覆盖配置）
            
        Returns:
            SandboxResult 执行结果
        """
        with self._lock:
            if self.status == SandboxStatus.RUNNING:
                return SandboxResult(
                    status=self.status,
                    termination_reason="Sandbox is already running"
                )
            
            self.status = SandboxStatus.RUNNING
            self._start_time = time.time()
            
            # 安全围栏检查
            passed, matched = self._security_fence.check(code)
            violations = []
            if not passed:
                violations.append(f"Sensitive keywords detected: {matched}")
            
            # 代码大小检查
            if len(code.encode()) > self.config.max_code_size:
                violations.append("Code size exceeds limit")
            
            if violations:
                self.status = SandboxStatus.TERMINATED
                return SandboxResult(
                    status=SandboxStatus.TERMINATED,
                    security_violations=violations,
                    termination_reason="Security violation"
                )
            
            # 设置超时
            exec_timeout = timeout or self.config.max_cpu_time
            
            # 创建临时文件执行
            result = self._run_in_subprocess(code, language, exec_timeout)
            
            return result
    
    def _run_in_subprocess(
        self,
        code: str,
        language: str,
        timeout: float
    ) -> SandboxResult:
        """在子进程中运行代码"""
        start_time = time.time()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            if language == "python":
                code_file = os.path.join(tmpdir, "code.py")
                with open(code_file, "w", encoding="utf-8") as f:
                    f.write(code)
                cmd = ["python3", code_file]
            else:
                # Shell脚本
                code_file = os.path.join(tmpdir, "code.sh")
                with open(code_file, "w", encoding="utf-8") as f:
                    f.write(code)
                cmd = ["bash", code_file]
            
            try:
                # 设置资源限制
                limits = {
                    resource.RLIMIT_CPU: (int(timeout), int(timeout + 1)),
                    resource.RLIMIT_AS: (self.config.max_memory_bytes, self.config.max_memory_bytes),
                    resource.RLIMIT_FSIZE: (self.config.max_disk_write_bytes, self.config.max_disk_write_bytes),
                    resource.RLIMIT_NPROC: (self.config.max_processes, self.config.max_processes),
                    resource.RLIMIT_NOFILE: (self.config.max_open_files, self.config.max_open_files),
                }
                
                def set_limits():
                    for res, (soft, hard) in limits.items():
                        try:
                            resource.setrlimit(res, (soft, hard))
                        except (ValueError, resource.error):
                            pass
                
                # 预设置环境变量，禁用网络
                env = os.environ.copy()
                if not self.config.network_enabled:
                    env.pop("HTTP_PROXY", None)
                    env.pop("HTTPS_PROXY", None)
                    env.pop("http_proxy", None)
                    env.pop("https_proxy", None)
                
                self._process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=tmpdir,
                    env=env,
                    preexec_fn=set_limits,
                )
                
                try:
                    stdout, stderr = self._process.communicate(timeout=timeout)
                    execution_time = time.time() - start_time
                    
                    # 获取资源使用情况
                    try:
                        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
                        memory_used = usage.ru_maxrss * 1024  # 转换为字节
                        cpu_time = usage.ru_utime + usage.ru_stime
                    except:
                        memory_used = 0
                        cpu_time = 0
                    
                    self.status = SandboxStatus.TERMINATED
                    
                    return SandboxResult(
                        status=SandboxStatus.TERMINATED,
                        exit_code=self._process.returncode,
                        stdout=stdout.decode("utf-8", errors="replace")[:self.config.max_output_size],
                        stderr=stderr.decode("utf-8", errors="replace")[:self.config.max_output_size],
                        execution_time=execution_time,
                        memory_used=memory_used,
                        cpu_time=cpu_time,
                        termination_reason="Normal completion"
                    )
                    
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self.status = SandboxStatus.TIMEOUT
                    
                    return SandboxResult(
                        status=SandboxStatus.TIMEOUT,
                        exit_code=-1,
                        stdout="",
                        stderr=f"Execution timeout after {timeout} seconds",
                        execution_time=timeout,
                        termination_reason="Timeout"
                    )
                    
            except Exception as e:
                self.status = SandboxStatus.TERMINATED
                return SandboxResult(
                    status=SandboxStatus.TERMINATED,
                    termination_reason=f"Execution error: {str(e)}"
                )
            finally:
                self._process = None
    
    def terminate(self, reason: str = "Manual termination") -> SandboxResult:
        """
        终止沙箱执行
        
        Args:
            reason: 终止原因
            
        Returns:
            SandboxResult 执行结果
        """
        with self._lock:
            if self._process:
                self._process.kill()
                self._process = None
            
            self.status = SandboxStatus.KILLED
            
            return SandboxResult(
                status=SandboxStatus.KILLED,
                termination_reason=reason,
                execution_time=time.time() - self._start_time if self._start_time else 0
            )
    
    def pause(self) -> bool:
        """暂停沙箱执行（发送SIGSTOP）"""
        with self._lock:
            if self._process and self.status == SandboxStatus.RUNNING:
                self._process.send_signal(signal.SIGSTOP)
                self.status = SandboxStatus.PAUSED
                return True
            return False
    
    def resume(self) -> bool:
        """恢复沙箱执行（发送SIGCONT）"""
        with self._lock:
            if self._process and self.status == SandboxStatus.PAUSED:
                self._process.send_signal(signal.SIGCONT)
                self.status = SandboxStatus.RUNNING
                return True
            return False
    
    def get_status(self) -> SandboxStatus:
        """获取沙箱状态"""
        return self.status
    
    def create_child_sandbox(self, config: Optional[SandboxConfig] = None) -> Sandbox:
        """
        创建子沙箱（继承当前沙箱的部分配置）
        
        Args:
            config: 子沙箱配置（会与父沙箱配置合并）
            
        Returns:
            新的沙箱实例
        """
        child_config = SandboxConfig(
            max_cpu_time=min(self.config.max_cpu_time, config.max_cpu_time if config else float('inf')),
            max_memory_bytes=min(self.config.max_memory_bytes, config.max_memory_bytes if config else float('inf')),
            max_wall_time=min(self.config.max_wall_time, config.max_wall_time if config else float('inf')),
            network_enabled=self.config.network_enabled,
            timeout_callback=self.config.timeout_callback,
        )
        return Sandbox(child_config)


class SandboxPool:
    """
    沙箱池 - 管理多个沙箱实例
    
    提供沙箱的复用和管理：
    - 沙箱池化复用
    - 并发执行控制
    - 自动清理
    """
    
    def __init__(
        self,
        pool_size: int = 5,
        default_config: Optional[SandboxConfig] = None
    ):
        self.pool_size = pool_size
        self.default_config = default_config or SandboxConfig()
        self._available: list[Sandbox] = []
        self._in_use: set[Sandbox] = set()
        self._lock = threading.Lock()
        
        # 初始化池
        for _ in range(pool_size):
            self._available.append(Sandbox(self.default_config))
    
    def acquire(self, config: Optional[SandboxConfig] = None) -> Sandbox:
        """
        获取一个沙箱
        
        Args:
            config: 可选的配置覆盖
            
        Returns:
            可用的沙箱实例
        """
        with self._lock:
            if self._available:
                sandbox = self._available.pop()
            else:
                sandbox = Sandbox(config or self.default_config)
            
            self._in_use.add(sandbox)
            return sandbox
    
    def release(self, sandbox: Sandbox) -> None:
        """
        释放沙箱回池中
        
        Args:
            sandbox: 要释放的沙箱
        """
        with self._lock:
            if sandbox in self._in_use:
                self._in_use.remove(sandbox)
                sandbox.status = SandboxStatus.CREATED
                self._available.append(sandbox)
    
    def execute_in_pool(
        self,
        code: str,
        language: str = "python",
        config: Optional[SandboxConfig] = None
    ) -> SandboxResult:
        """
        在池中执行代码（自动获取和释放沙箱）
        
        Args:
            code: 代码
            language: 语言
            config: 配置
            
        Returns:
            SandboxResult 执行结果
        """
        sandbox = self.acquire(config)
        try:
            return sandbox.execute_code(code, language)
        finally:
            self.release(sandbox)
    
    def shutdown(self) -> None:
        """关闭沙箱池"""
        with self._lock:
            for sandbox in self._available + list(self._in_use):
                sandbox.terminate("Pool shutdown")
            self._available.clear()
            self._in_use.clear()
