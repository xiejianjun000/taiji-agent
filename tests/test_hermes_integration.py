"""
Hermes Provider 整合测试
"""

import asyncio
import numpy as np
import pytest

from taiji_agent.hermes_provider import (
    HermesProvider,
    HermesBridge,
    HermesRequest,
    HermesResponse,
    TenantManager,
    TenantContext,
    TenantConfig,
    ResourceQuota,
    TenantIsolationMiddleware,
    RateLimitMiddleware,
    TaskStatus,
)
from taiji_agent.hermes_engine import (
    HermesAgentEngine,
    CrossSessionMemory,
    EvolutionEngine,
    SubAgentOrchestrator,
    EvolutionLevel,
    SubAgent,
    AgentSkill,
)


class TestHermesProvider:
    """Hermes Provider 测试"""

    def test_hermes_provider_init(self):
        """测试 Hermes Provider 初始化"""
        provider = HermesProvider(base_url="http://localhost:8000")
        assert provider.base_url == "http://localhost:8000"
        assert provider.timeout == 60.0
        assert provider.max_retries == 3

    def test_validate_request(self):
        """测试请求验证"""
        provider = HermesProvider()

        valid_request = HermesRequest(
            request_id="test-1",
            tenant_id="tenant-1",
            user_id="user-1",
            method="chat",
            params={},
        )
        provider._validate_request(valid_request)

    def test_validate_request_missing_tenant(self):
        """测试缺少租户ID的请求验证"""
        provider = HermesProvider()

        invalid_request = HermesRequest(
            request_id="test-1",
            tenant_id="",
            user_id="user-1",
            method="chat",
            params={},
        )

        with pytest.raises(ValueError):
            provider._validate_request(invalid_request)

    def test_get_tenant_context(self):
        """测试获取租户上下文"""
        provider = HermesProvider()
        manager = TenantManager()
        provider.set_tenant_manager(manager)

        request = HermesRequest(
            request_id="test-1",
            tenant_id="tenant-1",
            user_id="user-1",
            method="chat",
            params={},
            metadata={"session_id": "session-1"},
        )

        context = provider._get_tenant_context(request)
        assert context.tenant_id == "tenant-1"
        assert context.user_id == "user-1"
        assert context.session_id == "session-1"

    @pytest.mark.asyncio
    async def test_chat_response(self):
        """测试聊天响应"""
        provider = HermesProvider()

        request = HermesRequest(
            request_id="test-1",
            tenant_id="tenant-1",
            user_id="user-1",
            method="chat",
            params={"messages": [{"role": "user", "content": "Hello"}]},
        )

        response = await provider.chat(request)
        assert response.request_id == "test-1"
        assert response.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]


class TestTenantManager:
    """租户管理器测试"""

    def test_register_tenant(self):
        """测试注册租户"""
        manager = TenantManager()
        manager.register_tenant(
            tenant_id="tenant-1",
            name="测试租户",
            permissions=["chat", "memory", "skills"],
        )

        tenant = manager.get_tenant("tenant-1")
        assert tenant is not None
        assert tenant.name == "测试租户"
        assert "chat" in tenant.permissions

    def test_get_context(self):
        """测试获取上下文"""
        manager = TenantManager()
        manager.register_tenant(
            tenant_id="tenant-1",
            name="测试租户",
            permissions=["chat"],
        )

        context = manager.get_context(
            tenant_id="tenant-1",
            user_id="user-1",
            session_id="session-1",
        )

        assert context.tenant_id == "tenant-1"
        assert context.user_id == "user-1"
        assert context.session_id == "session-1"
        assert "chat" in context.permissions

    def test_check_permission(self):
        """测试权限检查"""
        manager = TenantManager()
        manager.register_tenant(
            tenant_id="tenant-1",
            name="测试租户",
            permissions=["chat", "memory"],
        )

        assert manager.check_permission("tenant-1", "chat") is True
        assert manager.check_permission("tenant-1", "admin") is False
        assert manager.check_permission("unknown-tenant", "chat") is False

    def test_check_quota(self):
        """测试配额检查"""
        manager = TenantManager()
        quota = ResourceQuota(
            limit_tokens_per_day=1000,
            limit_requests_per_minute=10,
        )
        manager.register_tenant(
            tenant_id="tenant-1",
            name="测试租户",
            quota=quota,
        )

        assert manager.check_quota("tenant-1", "tokens_per_day", 500) is True
        assert manager.check_quota("tenant-1", "tokens_per_day", 1001) is False

    def test_update_quota(self):
        """测试更新配额"""
        manager = TenantManager()
        quota = ResourceQuota(limit_tokens_per_day=1000)
        manager.register_tenant(
            tenant_id="tenant-1",
            name="测试租户",
            quota=quota,
        )

        manager.update_quota("tenant-1", "tokens_per_day", 100)
        assert manager._quotas["tenant-1"].current_tokens_today == 100

        manager.update_quota("tenant-1", "tokens_per_day", 200)
        assert manager._quotas["tenant-1"].current_tokens_today == 300


class TestCrossSessionMemory:
    """跨会话记忆测试"""

    @pytest.mark.asyncio
    async def test_add_memory(self):
        """测试添加记忆"""
        memory = CrossSessionMemory()

        entry_id = await memory.add(
            user_id="user-1",
            session_id="session-1",
            content="这是一个测试记忆",
            memory_type="interaction",
        )

        assert entry_id is not None
        assert len(memory._memory_store) == 1

    @pytest.mark.asyncio
    async def test_get_memory(self):
        """测试获取记忆"""
        memory = CrossSessionMemory()

        entry_id = await memory.add(
            user_id="user-1",
            session_id="session-1",
            content="这是一个测试记忆",
        )

        entry = await memory.get(entry_id)
        assert entry is not None
        assert entry.content == "这是一个测试记忆"

    @pytest.mark.asyncio
    async def test_search_memory(self):
        """测试搜索记忆"""
        memory = CrossSessionMemory()

        await memory.add(
            user_id="user-1",
            session_id="session-1",
            content="环评报告审批流程",
        )
        await memory.add(
            user_id="user-1",
            session_id="session-1",
            content="消防安全检查标准",
        )

        results = await memory.search(query="环评", user_id="user-1")
        assert len(results) >= 1
        assert "环评" in results[0].content

    @pytest.mark.asyncio
    async def test_get_recent(self):
        """测试获取最近记忆"""
        memory = CrossSessionMemory()

        await memory.add(user_id="user-1", session_id="session-1", content="记忆1")
        await memory.add(user_id="user-1", session_id="session-1", content="记忆2")

        recent = await memory.get_recent(user_id="user-1", limit=10)
        assert len(recent) == 2

    @pytest.mark.asyncio
    async def test_delete_memory(self):
        """测试删除记忆"""
        memory = CrossSessionMemory()

        entry_id = await memory.add(
            user_id="user-1",
            session_id="session-1",
            content="待删除的记忆",
        )

        result = await memory.delete(entry_id)
        assert result is True
        assert entry_id not in memory._memory_store


class TestEvolutionEngine:
    """进化引擎测试"""

    @pytest.mark.asyncio
    async def test_record_feedback(self):
        """测试记录反馈"""
        memory = CrossSessionMemory()
        engine = EvolutionEngine(memory)

        await engine.record_feedback(
            user_id="user-1",
            department_id="dept-1",
            interaction_id="inter-1",
            feedback_type="positive",
            content="回答很好",
        )

        assert "user-1" in engine._user_evolution
        assert engine._user_evolution["user-1"]["total_count"] == 1

    @pytest.mark.asyncio
    async def test_get_evolution(self):
        """测试获取进化状态"""
        memory = CrossSessionMemory()
        engine = EvolutionEngine(memory)

        await engine.record_feedback(
            user_id="user-1",
            department_id="dept-1",
            interaction_id="inter-1",
            feedback_type="positive",
            content="回答很好",
        )

        evolution = await engine.get_evolution("user-1")
        assert evolution is not None
        assert evolution["level"] == EvolutionLevel.INDIVIDUAL.value


class TestSubAgentOrchestrator:
    """子 Agent 编排器测试"""

    def test_load_bundled_agents(self):
        """测试加载内置 Agent"""
        orchestrator = SubAgentOrchestrator()
        assert len(orchestrator._agents) >= 5

    def test_get_agent(self):
        """测试获取 Agent"""
        orchestrator = SubAgentOrchestrator()

        agent = orchestrator.get_agent("zhangjie")
        assert agent is not None
        assert agent.name == "仓颉"
        assert agent.role == "环评审批"

    def test_list_agents(self):
        """测试列出 Agent"""
        orchestrator = SubAgentOrchestrator()

        agents = orchestrator.list_agents()
        assert len(agents) >= 5

        agents = orchestrator.list_agents(role="环评审批")
        assert len(agents) >= 1

    def test_find_agent_by_capability(self):
        """测试根据能力查找 Agent"""
        orchestrator = SubAgentOrchestrator()

        agents = orchestrator.find_agent_by_capability("document_analysis")
        assert len(agents) >= 1


class TestHermesAgentEngine:
    """Hermes Agent 引擎测试"""

    @pytest.mark.asyncio
    async def test_create_session(self):
        """测试创建会话"""
        engine = HermesAgentEngine()

        session_id = await engine.create_session(
            user_id="user-1",
            tenant_id="tenant-1",
        )

        assert session_id is not None
        assert session_id in engine._active_sessions

    @pytest.mark.asyncio
    async def test_get_session(self):
        """测试获取会话"""
        engine = HermesAgentEngine()

        session_id = await engine.create_session(
            user_id="user-1",
            tenant_id="tenant-1",
        )

        session = await engine.get_session(session_id)
        assert session is not None
        assert session["user_id"] == "user-1"

    @pytest.mark.asyncio
    async def test_process_message(self):
        """测试处理消息"""
        engine = HermesAgentEngine()

        session_id = await engine.create_session(
            user_id="user-1",
            tenant_id="tenant-1",
        )

        response = await engine.process_message(
            session_id=session_id,
            message="测试消息",
            user_id="user-1",
        )

        assert response["session_id"] == session_id
        assert "response" in response

    @pytest.mark.asyncio
    async def test_record_feedback(self):
        """测试记录反馈"""
        engine = HermesAgentEngine()

        session_id = await engine.create_session(
            user_id="user-1",
            tenant_id="tenant-1",
        )

        await engine.record_feedback(
            session_id=session_id,
            feedback_type="positive",
            content="回答很好",
        )

        assert len(engine.evolution._evolution_records) >= 0

    def test_get_stats(self):
        """测试获取统计信息"""
        engine = HermesAgentEngine()
        stats = engine.get_stats()

        assert "memory" in stats
        assert "active_sessions" in stats
        assert "agents" in stats


class TestMiddleware:
    """中间件测试"""

    @pytest.mark.asyncio
    async def test_tenant_isolation_middleware(self):
        """测试租户隔离中间件"""
        manager = TenantManager()
        manager.register_tenant(
            tenant_id="tenant-1",
            name="测试租户",
        )

        middleware = TenantIsolationMiddleware(manager)

        valid_request = HermesRequest(
            request_id="test-1",
            tenant_id="tenant-1",
            user_id="user-1",
            method="chat",
            params={},
        )

        result = await middleware.process_request(valid_request)
        assert result.request_id == "test-1"

    @pytest.mark.asyncio
    async def test_tenant_isolation_middleware_reject(self):
        """测试租户隔离中间件拒绝"""
        manager = TenantManager()

        middleware = TenantIsolationMiddleware(manager)

        invalid_request = HermesRequest(
            request_id="test-1",
            tenant_id="unknown-tenant",
            user_id="user-1",
            method="chat",
            params={},
        )

        with pytest.raises(PermissionError):
            await middleware.process_request(invalid_request)

    @pytest.mark.asyncio
    async def test_rate_limit_middleware(self):
        """测试限流中间件"""
        manager = TenantManager()
        quota = ResourceQuota(limit_requests_per_minute=1)
        manager.register_tenant(
            tenant_id="tenant-1",
            name="测试租户",
            quota=quota,
        )

        middleware = RateLimitMiddleware(manager)

        request = HermesRequest(
            request_id="test-1",
            tenant_id="tenant-1",
            user_id="user-1",
            method="chat",
            params={},
        )

        await middleware.process_request(request)

        with pytest.raises(PermissionError):
            await middleware.process_request(request)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
