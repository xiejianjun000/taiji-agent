"""
Taiji Agent 生产级压力测试
测试所有核心模块在高并发场景下的性能表现
"""

import asyncio
import gc
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import statistics

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from taiji_agent.taiji_verify import (
    KunGuard,
    QianAdvance,
    FuReturn,
    GuanObserve,
    DeltaSCalculator,
    SymptomMap,
)
from taiji_agent.hermes_provider import (
    HermesProvider,
    TenantManager,
    HermesRequest,
)
from taiji_agent.hermes_engine import (
    HermesAgentEngine,
    CrossSessionMemory,
)
from taiji_agent.event_bus import EventBus, Event, EventType
from taiji_agent.govmcp.crypto import (
    SM4Encryptor,
    SM3Hash,
    AuditTrail,
)
from taiji_agent.govmcp.workflow import ApprovalWorkflow
from taiji_agent.govmcp.tools import GovTools


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    p50_time_ms: float
    p95_time_ms: float
    p99_time_ms: float
    throughput: float
    memory_mb: float


@dataclass
class LoadTestResult:
    """负载测试结果"""
    name: str
    concurrent_users: int
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_latency_ms: float
    max_latency_ms: float
    min_latency_ms: float
    throughput_rps: float
    error_rate: float


def get_memory_mb() -> float:
    """获取当前内存使用（MB）"""
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


class BenchmarkRunner:
    """基准测试运行器"""

    def __init__(self):
        self.results: list[BenchmarkResult] = []

    def run(
        self,
        name: str,
        func,
        iterations: int = 1000,
        warmup: int = 10,
        *args,
        **kwargs,
    ) -> BenchmarkResult:
        """运行基准测试"""
        print(f"\n{'='*60}")
        print(f"Running benchmark: {name}")
        print(f"Iterations: {iterations}, Warmup: {warmup}")
        print(f"{'='*60}")

        gc.collect()
        start_mem = get_memory_mb()

        times = []

        for i in range(warmup):
            func(*args, **kwargs)

        for i in range(iterations):
            gc.disable()
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            gc.enable()

            times.append((end - start) * 1000)

            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{iterations}")

        gc.collect()
        end_mem = get_memory_mb()

        times.sort()
        total_time = sum(times)
        avg_time = statistics.mean(times)
        throughput = iterations / (total_time / 1000)

        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time_ms=total_time,
            avg_time_ms=avg_time,
            min_time_ms=min(times),
            max_time_ms=max(times),
            p50_time_ms=times[int(len(times) * 0.5)],
            p95_time_ms=times[int(len(times) * 0.95)],
            p99_time_ms=times[int(len(times) * 0.99)],
            throughput=throughput,
            memory_mb=end_mem - start_mem,
        )

        self.results.append(result)
        self._print_result(result)

        return result

    def _print_result(self, result: BenchmarkResult):
        """打印结果"""
        print(f"\n📊 Results for {result.name}:")
        print(f"  Total time:    {result.total_time_ms:.2f} ms")
        print(f"  Avg time:      {result.avg_time_ms:.4f} ms")
        print(f"  Min time:      {result.min_time_ms:.4f} ms")
        print(f"  Max time:      {result.max_time_ms:.4f} ms")
        print(f"  P50 latency:   {result.p50_time_ms:.4f} ms")
        print(f"  P95 latency:   {result.p95_time_ms:.4f} ms")
        print(f"  P99 latency:   {result.p99_time_ms:.4f} ms")
        print(f"  Throughput:    {result.throughput:.2f} ops/sec")
        print(f"  Memory delta:  {result.memory_mb:.2f} MB")


class LoadTestRunner:
    """负载测试运行器"""

    def __init__(self):
        self.results: list[LoadTestResult] = []

    async def run(
        self,
        name: str,
        func,
        concurrent_users: int = 10,
        duration_seconds: int = 60,
    ) -> LoadTestResult:
        """运行负载测试"""
        print(f"\n{'='*60}")
        print(f"Running load test: {name}")
        print(f"Concurrent users: {concurrent_users}")
        print(f"Duration: {duration_seconds} seconds")
        print(f"{'='*60}")

        latencies = []
        successes = 0
        failures = 0
        start_time = time.time()
        end_time = start_time + duration_seconds

        async def worker():
            nonlocal successes, failures
            while time.time() < end_time:
                w_start = time.perf_counter()
                try:
                    await func()
                    w_end = time.perf_counter()
                    latencies.append((w_end - w_start) * 1000)
                    successes += 1
                except Exception as e:
                    failures += 1

        tasks = [asyncio.create_task(worker()) for _ in range(concurrent_users)]

        for i in range(0, duration_seconds, 5):
            await asyncio.sleep(5)
            elapsed = time.time() - start_time
            current_rps = (successes + failures) / elapsed if elapsed > 0 else 0
            print(f"  [{elapsed:.0f}s] Success: {successes}, Failed: {failures}, RPS: {current_rps:.2f}")

        await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time
        total_requests = successes + failures

        latencies.sort()

        result = LoadTestResult(
            name=name,
            concurrent_users=concurrent_users,
            duration_seconds=total_time,
            total_requests=total_requests,
            successful_requests=successes,
            failed_requests=failures,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            max_latency_ms=max(latencies) if latencies else 0,
            min_latency_ms=min(latencies) if latencies else 0,
            throughput_rps=total_requests / total_time if total_time > 0 else 0,
            error_rate=failures / total_requests if total_requests > 0 else 0,
        )

        self.results.append(result)
        self._print_result(result)

        return result

    def _print_result(self, result: LoadTestResult):
        """打印结果"""
        print(f"\n📊 Load Test Results for {result.name}:")
        print(f"  Duration:      {result.duration_seconds:.2f} s")
        print(f"  Total reqs:    {result.total_requests}")
        print(f"  Success:       {result.successful_requests}")
        print(f"  Failed:        {result.failed_requests}")
        print(f"  Error rate:    {result.error_rate * 100:.2f}%")
        print(f"  Avg latency:   {result.avg_latency_ms:.2f} ms")
        print(f"  Min latency:   {result.min_latency_ms:.2f} ms")
        print(f"  Max latency:   {result.max_latency_ms:.2f} ms")
        print(f"  Throughput:    {result.throughput_rps:.2f} req/sec")


class StressTestSuite:
    """压力测试套件"""

    def __init__(self):
        self.benchmark_runner = BenchmarkRunner()
        self.load_runner = LoadTestRunner()
        self.start_time = datetime.now()

    async def run_all(self):
        """运行所有测试"""
        print("\n" + "=" * 80)
        print("🚀 Taiji Agent 生产级压力测试")
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        await self.test_taiji_verify()
        await self.test_hermes_provider()
        await self.test_event_bus()
        await self.test_govmcp_crypto()
        await self.test_govmcp_workflow()

        self.print_summary()

    async def test_taiji_verify(self):
        """测试 Taiji Verify 模块"""
        print("\n" + "=" * 80)
        print("🧘 Taiji Verify 模块压力测试")
        print("=" * 80)

        delta_s = DeltaSCalculator()
        kun_guard = KunGuard()
        qian_advance = QianAdvance()

        input_vec = np.random.rand(768)
        ground_vec = np.random.rand(768)

        def test_delta_s():
            delta_s.compute(input_vec, ground_vec)

        self.benchmark_runner.run("DeltaS计算", test_delta_s, iterations=5000)

        def test_kun_guard():
            kun_guard.correct(input_vec, ground_vec)

        self.benchmark_runner.run("坤守修正", test_kun_guard, iterations=3000)

        async def test_hermes_chat():
            provider = HermesProvider()
            request = HermesRequest(
                request_id="test",
                tenant_id="test",
                user_id="test",
                method="chat",
                params={"messages": [{"role": "user", "content": "test"}]},
            )
            await provider.chat(request)

        await self.test_hermes_load(test_hermes_chat, users=20, duration=30)

    async def test_hermes_provider(self):
        """测试 Hermes Provider"""
        print("\n" + "=" * 80)
        print("🔗 Hermes Provider 模块压力测试")
        print("=" * 80)

        provider = HermesProvider()
        manager = TenantManager()
        manager.register_tenant("test", "Test Tenant")
        provider.set_tenant_manager(manager)

        def test_tenant_context():
            request = HermesRequest(
                request_id="test",
                tenant_id="test",
                user_id="test",
                method="chat",
                params={},
            )
            provider._get_tenant_context(request)

        self.benchmark_runner.run("租户上下文获取", test_tenant_context, iterations=10000)

        def test_permission_check():
            manager.check_permission("test", "chat")

        self.benchmark_runner.run("权限检查", test_permission_check, iterations=20000)

    async def test_hermes_load(self, func, users: int, duration: int):
        """Hermes 负载测试"""
        print(f"\n📈 Hermes 负载测试 (用户: {users}, 时长: {duration}s)")
        await self.load_runner.run(
            "Hermes Chat Load",
            func,
            concurrent_users=users,
            duration_seconds=duration,
        )

    async def test_event_bus(self):
        """测试 EventBus"""
        print("\n" + "=" * 80)
        print("📡 EventBus 模块压力测试")
        print("=" * 80)

        bus = EventBus()
        received_count = 0

        async def handler(event):
            nonlocal received_count
            received_count += 1

        bus.subscribe(EventType.LLM_RESPONSE, handler)
        bus.subscribe(EventType.AGENT_START, handler)
        bus.subscribe(EventType.TOOL_CALL, handler)

        def test_publish():
            event = Event(
                event_type=EventType.LLM_RESPONSE,
                data={"content": "test"},
            )
            asyncio.create_task(bus.publish(event))

        self.benchmark_runner.run("EventBus发布", test_publish, iterations=5000)

        print(f"  Received events: {received_count}")

    async def test_govmcp_crypto(self):
        """测试 GovMCP 加密模块"""
        print("\n" + "=" * 80)
        print("🔐 GovMCP 国密加密模块压力测试")
        print("=" * 80)

        key = os.urandom(16)
        sm4 = SM4Encryptor(key)
        data = b"Government sensitive data " * 10

        def test_sm4_encrypt():
            sm4.encrypt(data)

        self.benchmark_runner.run("SM4加密", test_sm4_encrypt, iterations=5000)

        def test_sm3_hash():
            SM3Hash.hash(data)

        self.benchmark_runner.run("SM3哈希", test_sm3_hash, iterations=10000)

        audit = AuditTrail()

        def test_audit_record():
            audit.record_action(
                user_id="test",
                action="create",
                resource="doc",
            )

        self.benchmark_runner.run("审计记录", test_audit_record, iterations=5000)

    async def test_govmcp_workflow(self):
        """测试 GovMCP 审批工作流"""
        print("\n" + "=" * 80)
        print("📋 GovMCP 审批工作流压力测试")
        print("=" * 80)

        workflow = ApprovalWorkflow()

        def test_create_request():
            workflow.create_request(
                title="Test",
                description="Test approval",
                requester="user",
                department="dept",
            )

        self.benchmark_runner.run("创建审批", test_create_request, iterations=3000)

        async def test_workflow():
            request = workflow.create_request(
                title="Load Test",
                description="Load testing",
                requester="user",
                department="dept",
            )
            await workflow.submit_request(request.request_id)

        await self.load_runner.run(
            "审批工作流负载",
            test_workflow,
            concurrent_users=10,
            duration_seconds=20,
        )

    def print_summary(self):
        """打印测试总结"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print("\n" + "=" * 80)
        print("📋 压力测试总结")
        print("=" * 80)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时:   {duration:.2f} 秒")

        print("\n📊 基准测试结果:")
        for result in self.benchmark_runner.results:
            print(f"  [{result.name}] Avg: {result.avg_time_ms:.4f}ms, "
                  f"Throughput: {result.throughput:.2f} ops/sec")

        print("\n📈 负载测试结果:")
        for result in self.load_runner.results:
            print(f"  [{result.name}] RPS: {result.throughput_rps:.2f}, "
                  f"Error Rate: {result.error_rate * 100:.2f}%, "
                  f"Avg Latency: {result.avg_latency_ms:.2f}ms")

        report = self.generate_report(duration)
        print(f"\n📄 详细报告已生成: stress_test_report.json")

        with open("stress_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        print("\n✅ 所有压力测试完成！")

    def generate_report(self, duration: float) -> dict:
        """生成测试报告"""
        return {
            "test_info": {
                "project": "Taiji Agent",
                "version": "1.0.0",
                "start_time": self.start_time.isoformat(),
                "duration_seconds": duration,
            },
            "benchmark_results": [
                {
                    "name": r.name,
                    "iterations": r.iterations,
                    "total_time_ms": r.total_time_ms,
                    "avg_time_ms": r.avg_time_ms,
                    "min_time_ms": r.min_time_ms,
                    "max_time_ms": r.max_time_ms,
                    "p50_time_ms": r.p50_time_ms,
                    "p95_time_ms": r.p95_time_ms,
                    "p99_time_ms": r.p99_time_ms,
                    "throughput": r.throughput,
                    "memory_mb": r.memory_mb,
                }
                for r in self.benchmark_runner.results
            ],
            "load_test_results": [
                {
                    "name": r.name,
                    "concurrent_users": r.concurrent_users,
                    "duration_seconds": r.duration_seconds,
                    "total_requests": r.total_requests,
                    "successful_requests": r.successful_requests,
                    "failed_requests": r.failed_requests,
                    "avg_latency_ms": r.avg_latency_ms,
                    "max_latency_ms": r.max_latency_ms,
                    "min_latency_ms": r.min_latency_ms,
                    "throughput_rps": r.throughput_rps,
                    "error_rate": r.error_rate,
                }
                for r in self.load_runner.results
            ],
        }


async def main():
    """主函数"""
    suite = StressTestSuite()
    await suite.run_all()


if __name__ == "__main__":
    asyncio.run(main())
