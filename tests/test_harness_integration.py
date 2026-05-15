"""
Harness 整合测试
"""

import asyncio
import pytest

from taiji_agent.event_bus import (
    EventBus,
    Event,
    EventType,
    EventFilter,
    subscribe,
    publish,
    get_event_bus,
)
from taiji_agent.plugin_system import (
    Plugin,
    PluginConfig,
    PluginRegistry,
    PluginState,
)
from taiji_agent.sandbox import (
    DockerSandbox,
    SandboxConfig,
    SandboxType,
    SandboxManager,
    get_sandbox_manager,
)
from taiji_agent.streaming import (
    StreamingResponse,
    StreamConfig,
    StreamType,
    StreamManager,
)


class TestEventBus:
    """EventBus 测试"""

    def test_event_bus_init(self):
        """测试 EventBus 初始化"""
        bus = EventBus()
        assert bus.enable_logging is True
        assert len(bus._subscribers) == 0

    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        """测试发布订阅"""
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.AGENT_START, handler)
        await bus.publish(Event(event_type=EventType.AGENT_START))

        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_event_filter(self):
        """测试事件过滤"""
        bus = EventBus()
        received = []

        filter_obj = EventFilter(
            event_types=[EventType.AGENT_START],
            session_id="session-1",
        )

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.AGENT_START, handler, filter=filter_obj)

        await bus.publish(Event(
            event_type=EventType.AGENT_START,
            session_id="session-1",
        ))

        await bus.publish(Event(
            event_type=EventType.AGENT_START,
            session_id="session-2",
        ))

        assert len(received) == 1

    def test_unsubscribe(self):
        """测试取消订阅"""
        bus = EventBus()

        def handler(event):
            pass

        sub_id = bus.subscribe(EventType.AGENT_START, handler)
        assert bus.unsubscribe(sub_id) is True
        assert bus.unsubscribe("invalid-id") is False

    def test_get_stats(self):
        """测试获取统计"""
        bus = EventBus()
        stats = bus.get_stats()

        assert "total_events" in stats
        assert "active_subscribers" in stats


class TestPluginSystem:
    """Plugin 系统测试"""

    def test_plugin_registry_init(self):
        """测试注册表初始化"""
        registry = PluginRegistry()
        assert len(registry._plugins) == 0

    def test_register_plugin(self):
        """测试注册插件"""
        registry = PluginRegistry()

        class TestPlugin(Plugin):
            async def on_load(self) -> bool:
                return True

            async def on_unload(self):
                pass

        config = PluginConfig(name="test-plugin")
        plugin_id = registry.register(TestPlugin, config)

        assert plugin_id == "test-plugin"

    @pytest.mark.asyncio
    async def test_load_plugin(self):
        """测试加载插件"""
        registry = PluginRegistry()

        class TestPlugin(Plugin):
            async def on_load(self) -> bool:
                return True

            async def on_unload(self):
                pass

        config = PluginConfig(name="test-plugin", enabled=True)
        registry.register(TestPlugin, config)

        registry._create_plugin_instance = lambda x: TestPlugin()
        
        success = await registry.load("test-plugin")
        assert success is True

    def test_list_plugins(self):
        """测试列出插件"""
        registry = PluginRegistry()

        class TestPlugin(Plugin):
            async def on_load(self) -> bool:
                return True

            async def on_unload(self):
                pass

        config = PluginConfig(name="test-plugin")
        registry.register(TestPlugin, config)

        plugins = registry.list_plugins()
        assert isinstance(plugins, list)


class TestSandbox:
    """Docker Sandbox 测试"""

    def test_sandbox_config(self):
        """测试沙箱配置"""
        config = SandboxConfig(
            sandbox_type=SandboxType.HOT,
            memory_limit="1g",
            timeout=120,
        )

        assert config.sandbox_type == SandboxType.HOT
        assert config.memory_limit == "1g"
        assert config.timeout == 120

    @pytest.mark.asyncio
    async def test_sandbox_execute(self):
        """测试沙箱执行"""
        sandbox = DockerSandbox(SandboxConfig(
            sandbox_type=SandboxType.COLD,
            timeout=10,
        ))

        result = await sandbox.execute(
            code='print("Hello World")',
            language="python",
        )

        assert result.success is True
        assert "Hello World" in result.output

    @pytest.mark.asyncio
    async def test_sandbox_manager(self):
        """测试沙箱管理器"""
        manager = get_sandbox_manager()

        result = await manager.execute(
            sandbox_id="test-sandbox",
            code='print("Test")',
            language="python",
        )

        assert result.success is True

    def test_sandbox_stats(self):
        """测试获取统计"""
        sandbox = DockerSandbox()
        stats = sandbox.get_stats()

        assert "config" in stats
        assert "containers" in stats


class TestStreaming:
    """流式响应测试"""

    def test_stream_config(self):
        """测试流配置"""
        config = StreamConfig(
            stream_type=StreamType.WEBSOCKET,
            chunk_size=128,
        )

        assert config.stream_type == StreamType.WEBSOCKET
        assert config.chunk_size == 128

    @pytest.mark.asyncio
    async def test_streaming_response(self):
        """测试流式响应"""
        stream = StreamingResponse(stream_id="test-stream")

        await stream.start()
        assert stream.state.value == "open"

        await stream.send_chunk("Hello")
        await stream.send_chunk(" World")

        await stream.send_done()
        assert stream._closed is True

    @pytest.mark.asyncio
    async def test_stream_manager(self):
        """测试流管理器"""
        manager = StreamManager()

        stream = await manager.create_stream(
            stream_id="test-stream",
            stream_type=StreamType.WEBSOCKET,
        )

        assert stream.stream_id == "test-stream"

        await manager.close_stream("test-stream")


class TestGlobalFunctions:
    """全局函数测试"""

    def test_get_event_bus(self):
        """测试获取全局事件总线"""
        bus = get_event_bus()
        assert bus is not None

    def test_get_sandbox_manager(self):
        """测试获取全局沙箱管理器"""
        manager = get_sandbox_manager()
        assert manager is not None


class TestEventTypes:
    """事件类型测试"""

    def test_event_type_enum(self):
        """测试事件类型枚举"""
        assert EventType.AGENT_START.value == "agent:start"
        assert EventType.AGENT_END.value == "agent:end"
        assert EventType.LLM_REQUEST.value == "llm:request"
        assert EventType.TAIJI_VERIFY_START.value == "taiji:verify_start"


class TestSandboxTypes:
    """沙箱类型测试"""

    def test_sandbox_type_enum(self):
        """测试沙箱类型枚举"""
        assert SandboxType.HOT.value == "hot"
        assert SandboxType.COLD.value == "cold"
        assert SandboxType.WARM.value == "warm"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
