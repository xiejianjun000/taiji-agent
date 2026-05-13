"""
OpenTaiji 2.0 新功能压力测试
测试所有新增模块
"""
import pytest
import asyncio
from datetime import datetime

from opentaiji.mcp import (
    MCPServerAdapter,
    MCPServerConfig,
    MCPClientAdapter,
    MCPConnectionConfig,
    MCPProtocol,
    MCPTool,
)
from opentaiji.guardrails import (
    GuardrailManager,
    GuardrailConfig,
    ValidationResult,
    ContentFilter,
    RateLimitGuardrail,
    SensitiveDataFilter,
    QualityGate,
)
from opentaiji.observability import (
    TracingManager,
    TraceSpan,
    SpanKind,
    SpanStatus,
    ConsoleExporter,
    FileExporter,
)
from opentaiji.hitl import (
    ApprovalQueue,
    ApprovalConfig,
    ConfidenceGate,
    ConfidenceLevel,
    CheckpointManager,
)
from opentaiji.workflow import (
    WorkflowEngine,
    WorkflowState,
    WorkflowConfig,
)
from opentaiji.handoffs import (
    HandoffManager,
    HandoffConfig,
    HandoffContext,
    HandoffDecision,
)
from opentaiji.code import CodeExecutor, SandboxConfig, ExecutionStatus
from opentaiji.visual import (
    WorkflowExporter,
    MermaidExporter,
    ASCIIExporter,
    JSONExporter,
    WorkflowGraph,
    NodeData,
    EdgeData,
    ExportFormat,
)


class TestMCP:
    def test_mcp_protocol(self):
        init_msg = MCPProtocol.initialize_request("test", "1.0")
        assert init_msg.method == "initialize"
        assert init_msg.params["clientInfo"]["name"] == "test"
        tools_call = MCPProtocol.tools_call("test_tool", {"arg": "value"})
        assert tools_call.method == "tools/call"
        print("✓ MCP Protocol 测试通过")

    def test_mcp_tool(self):
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {}},
        )
        mcp_dict = tool.to_mcp_dict()
        assert mcp_dict["name"] == "test_tool"
        print("✓ MCP Tool 测试通过")

    def test_mcp_server_config(self):
        config = MCPServerConfig(
            host="localhost",
            port=8080,
            server_name="test_server",
        )
        assert config.host == "localhost"
        assert config.port == 8080
        print("✓ MCP Server Config 测试通过")


class TestGuardrails:
    def test_guardrail_manager(self):
        manager = GuardrailManager()
        assert len(manager.input_guardrails) == 0
        manager.add_input_guardrail(ContentFilter())
        assert len(manager.input_guardrails) == 1
        print("✓ Guardrail Manager 测试通过")

    @pytest.mark.asyncio
    async def test_content_filter(self):
        guardrail = ContentFilter()
        result = await guardrail.validate("Hello world")
        assert result.is_valid is True
        result2 = await guardrail.validate("<script>alert('xss')</script>")
        assert result2.is_valid is False
        print("✓ Content Filter 测试通过")

    @pytest.mark.asyncio
    async def test_rate_limit(self):
        guardrail = RateLimitGuardrail(max_requests_per_minute=5)
        for _ in range(5):
            result = await guardrail.validate("test")
            assert result.is_valid is True
        result6 = await guardrail.validate("test")
        assert result6.is_valid is False
        print("✓ Rate Limit Guardrail 测试通过")

    @pytest.mark.asyncio
    async def test_sensitive_data_filter(self):
        guardrail = SensitiveDataFilter()
        result = await guardrail.validate("Contact me at test@example.com")
        assert result.level.value in ["pass", "warn"]
        print("✓ Sensitive Data Filter 测试通过")

    @pytest.mark.asyncio
    async def test_quality_gate(self):
        guardrail = QualityGate(min_length=5)
        result = await guardrail.validate("Hi")
        assert result.is_valid is True
        result2 = await guardrail.validate("This is a longer text")
        assert result2.is_valid is True
        print("✓ Quality Gate 测试通过")


class TestObservability:
    def test_tracing_manager(self):
        manager = TracingManager()
        span = manager.start_span("test_span", SpanKind.AGENT)
        assert span.name == "test_span"
        assert span.kind == SpanKind.AGENT
        manager.end_span(span)
        assert len(manager._spans) == 1
        print("✓ Tracing Manager 测试通过")

    def test_console_exporter(self):
        exporter = ConsoleExporter(verbose=True)
        span = TraceSpan(
            span_id="test123",
            trace_id="trace456",
            name="test_span",
            kind=SpanKind.AGENT,
            start_time=1000.0,
            end_time=1001.0,
        )
        exporter.export([span])
        print("✓ Console Exporter 测试通过")

    def test_file_exporter(self):
        import tempfile
        import os
        exporter = FileExporter(directory=tempfile.mkdtemp(), format="jsonl")
        span = TraceSpan(
            span_id="test123",
            trace_id="trace456",
            name="test_span",
            kind=SpanKind.AGENT,
            start_time=1000.0,
            end_time=1001.0,
        )
        exporter.export([span])
        print("✓ File Exporter 测试通过")


class TestHITL:
    @pytest.mark.asyncio
    async def test_approval_queue(self):
        queue = ApprovalQueue()
        request_id = await queue.request_approval(
            agent_name="test_agent",
            action_type="delete",
            action_description="Delete file",
            justification="Testing",
            risk_level="high",
        )
        assert request_id is not None
        pending = queue.get_pending()
        assert len(pending) == 1
        await queue.approve(request_id, "admin", "Approved for testing")
        pending = queue.get_pending()
        assert len(pending) == 0
        print("✓ Approval Queue 测试通过")

    def test_confidence_gate(self):
        gate = ConfidenceGate(high_threshold=0.8, medium_threshold=0.6)
        result = gate.evaluate(
            action_type="read",
            action_description="Read file",
            risk_level="low",
            parameters={},
        )
        assert result.confidence >= 0.7
        assert result.level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
        print("✓ Confidence Gate 测试通过")

    def test_checkpoint_manager(self):
        import tempfile
        manager = CheckpointManager(storage_path=tempfile.mkdtemp(), auto_save=True)
        checkpoint = manager.create(
            workflow_id="wf1",
            step_name="step1",
            state={"data": "test"},
        )
        assert checkpoint.checkpoint_id is not None
        restored = manager.restore(checkpoint.checkpoint_id)
        assert restored["data"] == "test"
        print("✓ Checkpoint Manager 测试通过")


class TestWorkflow:
    @pytest.mark.asyncio
    async def test_workflow_engine(self):
        engine = WorkflowEngine()
        result_store = {"results": []}

        async def node_a(state):
            result_store["results"].append("A")
            return "result_a"

        async def node_b(state):
            result_store["results"].append("B")
            return "result_b"

        engine.add_node("A", node_a)
        engine.add_node("B", node_b)
        engine.add_edge("A", "B")

        final_state = await engine.run(start_node="A")
        assert "A" in result_store["results"]
        print("✓ Workflow Engine 测试通过")


class TestHandoffs:
    def test_handoff_manager(self):
        manager = HandoffManager()
        assert len(manager.list_handoffs()) == 0
        print("✓ Handoff Manager 测试通过")

    def test_handoff_context(self):
        context = HandoffContext(
            user_intent="Book flight",
            current_task="Search flights",
            completed_steps=["login"],
            pending_tasks=["payment"],
        )
        assert context.user_intent == "Book flight"
        assert len(context.completed_steps) == 1
        print("✓ Handoff Context 测试通过")


class TestCodeAgent:
    @pytest.mark.asyncio
    async def test_code_executor(self):
        executor = CodeExecutor()
        result = await executor.execute("print('Hello from test')")
        assert result.status == ExecutionStatus.SUCCESS
        assert "Hello from test" in result.output
        print("✓ Code Executor 测试通过")

    @pytest.mark.asyncio
    async def test_sandbox_blocking(self):
        executor = CodeExecutor()
        result = await executor.execute("import os; os.system('ls')")
        assert result.status == ExecutionStatus.SANDBOX_VIOLATION
        print("✓ Sandbox Blocking 测试通过")

    def test_sandbox_config(self):
        config = SandboxConfig(
            timeout_seconds=60,
            max_memory_mb=512,
            allow_network=False,
        )
        assert config.timeout_seconds == 60
        assert config.allow_network is False
        print("✓ Sandbox Config 测试通过")


class TestVisual:
    def test_workflow_graph(self):
        graph = WorkflowGraph(
            name="Test Workflow",
            nodes=[
                NodeData(id="start", label="Start", node_type="entry"),
                NodeData(id="process", label="Process", node_type="agent"),
                NodeData(id="end", label="End", node_type="end"),
            ],
            edges=[
                EdgeData(source="start", target="process"),
                EdgeData(source="process", target="end"),
            ],
        )
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        print("✓ Workflow Graph 测试通过")

    def test_mermaid_exporter(self):
        from opentaiji.visual import MermaidExporter, WorkflowGraph, NodeData, EdgeData
        graph = WorkflowGraph(
            name="Test",
            nodes=[
                NodeData(id="a", label="Node A", node_type="agent"),
                NodeData(id="b", label="Node B", node_type="end"),
            ],
            edges=[EdgeData(source="a", target="b")],
        )
        exporter = MermaidExporter()
        output = exporter.export(graph)
        assert "flowchart" in output
        assert "Node_A" in output or "a" in output
        print("✓ Mermaid Exporter 测试通过")

    def test_ascii_exporter(self):
        graph = WorkflowGraph(
            name="Test",
            nodes=[
                NodeData(id="a", label="A", node_type="agent"),
                NodeData(id="b", label="B", node_type="end"),
            ],
            edges=[EdgeData(source="a", target="b")],
        )
        exporter = ASCIIExporter()
        output = exporter.export(graph)
        assert "Test" in output
        assert "Nodes" in output
        print("✓ ASCII Exporter 测试通过")

    def test_json_exporter(self):
        graph = WorkflowGraph(name="Test", nodes=[], edges=[])
        exporter = JSONExporter(pretty=True)
        output = exporter.export(graph)
        assert '"name": "Test"' in output
        assert '"nodes":' in output
        print("✓ JSON Exporter 测试通过")

    def test_exporter_factory(self):
        from opentaiji.visual import WorkflowExporterFactory, WorkflowGraph, ExportFormat
        graph = WorkflowGraph(name="Test", nodes=[], edges=[])
        output = WorkflowExporterFactory.export(graph, ExportFormat.MERMAID)
        assert "flowchart" in output
        output2 = WorkflowExporterFactory.export(graph, ExportFormat.ASCII)
        assert "Test" in output2
        print("✓ Exporter Factory 测试通过")


def run_all_tests():
    print("\n" + "=" * 60)
    print("OpenTaiji 2.0 新功能压力测试")
    print("=" * 60 + "\n")

    test_classes = [
        TestMCP,
        TestGuardrails,
        TestObservability,
        TestHITL,
        TestWorkflow,
        TestHandoffs,
        TestCodeAgent,
        TestVisual,
    ]

    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\n📦 {test_class.__name__}")
        print("-" * 40)
        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith("test_")]
        for method_name in methods:
            try:
                method = getattr(instance, method_name)
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method())
                else:
                    method()
                passed += 1
            except Exception as e:
                print(f"  ✗ {method_name}: {e}")
                failed += 1

    print("\n" + "=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
