"""
GovMCP 集成测试 - 验证 GovMCP 与 Taiji Agent 的集成
"""

import asyncio
import json
import pytest


@pytest.fixture
def integration():
    """创建集成实例"""
    from taiji_agent.govmcp_integration import create_govmcp_integration

    integration = asyncio.run(create_govmcp_integration())
    return integration


class TestGovMCPIntegration:
    """GovMCP 集成测试"""

    def test_integration_initialize(self, integration):
        """测试集成初始化"""
        info = integration.get_server_info()
        assert info["initialized"] is True
        assert info["name"] == "GovMCP"
        assert info["tools_count"] == 20

    def test_get_all_tools(self, integration):
        """测试获取所有工具"""
        tools = integration.get_tools()
        assert len(tools) == 20

        tool_names = [t["name"] for t in tools]
        assert "sm3_hash" in tool_names
        assert "sm4_encrypt" in tool_names
        assert "approval_create" in tool_names
        assert "audit_log" in tool_names
        assert "mask_id_number" in tool_names

    def test_tool_categories(self, integration):
        """测试工具分类"""
        info = integration.get_server_info()
        categories = info["categories"]

        assert categories["crypto"] > 0
        assert categories["workflow"] > 0
        assert categories["audit"] > 0
        assert categories["gov"] > 0

    def test_crypto_tool_call(self, integration):
        """测试加密工具调用"""
        result = asyncio.run(integration.call_tool("sm3_hash", {"data": "test data"}))
        result_dict = json.loads(result)
        assert "hash" in result_dict
        assert result_dict["algorithm"] == "SM3"

    def test_approval_workflow(self, integration):
        """测试审批工作流"""
        result = asyncio.run(integration.call_tool("approval_create", {
            "title": "集成测试审批",
            "description": "测试审批工作流",
            "requester": "test_user",
            "department": "测试部",
        }))
        result_dict = json.loads(result)
        assert "request_id" in result_dict

        request_id = result_dict["request_id"]
        approve_result = asyncio.run(integration.call_tool("approval_approve", {
            "request_id": request_id,
            "approver_id": "manager",
            "comment": "同意",
        }))
        approve_dict = json.loads(approve_result)
        assert approve_dict["status"] == "approved"

    def test_audit_logging(self, integration):
        """测试审计日志"""
        asyncio.run(integration.call_tool("audit_log", {
            "action": "test_action",
            "user_id": "test_user",
            "resource": "test_resource",
            "details": {"key": "value"},
        }))

        query_result = asyncio.run(integration.call_tool("audit_query", {
            "user_id": "test_user",
        }))
        query_dict = json.loads(query_result)
        assert query_dict["count"] >= 1

    def test_data_masking(self, integration):
        """测试数据脱敏"""
        result = asyncio.run(integration.call_tool("mask_id_number", {
            "id_number": "11010519491231002X",
        }))
        result_dict = json.loads(result)
        assert "***" in result_dict["masked"]


@pytest.fixture
def engine():
    """创建增强引擎实例"""
    from taiji_agent.gov_enhanced_engine import GovEnhancedHermesEngine

    eng = GovEnhancedHermesEngine()
    asyncio.run(eng.enable_govmcp())
    return eng


class TestGovEnhancedEngine:
    """Gov 增强引擎测试"""

    def test_enable_govmcp(self, engine):
        """测试启用 GovMCP"""
        assert engine.govmcp_enabled is True
        info = asyncio.run(engine.enable_govmcp())
        assert info["initialized"] is True

    def test_get_govmcp_tools(self, engine):
        """测试获取工具列表"""
        tools = engine.get_govmcp_tools()
        assert len(tools) == 20

    def test_encrypt_decrypt(self, engine):
        """测试加密解密"""
        original = "敏感政务数据"
        encrypted = asyncio.run(engine.encrypt_data(original))
        encrypted_dict = json.loads(encrypted)
        assert "encrypted_data" in encrypted_dict

        decrypted = asyncio.run(engine.decrypt_data(
            encrypted_dict["encrypted_data"],
            key_id=encrypted_dict["key_id"],
        ))
        decrypted_dict = json.loads(decrypted)
        assert decrypted_dict["decrypted_data"] == original

    def test_hash_data(self, engine):
        """测试数据哈希"""
        result = asyncio.run(engine.hash_data("test data"))
        result_dict = json.loads(result)
        assert "hash" in result_dict
        assert len(result_dict["hash"]) == 64

    def test_approval_flow(self, engine):
        """测试审批流程"""
        result = asyncio.run(engine.create_approval(
            title="数据访问申请",
            description="申请访问加密数据",
            requester="user001",
            department="政务中心",
        ))
        result_dict = json.loads(result)
        request_id = result_dict["request_id"]

        approve_result = asyncio.run(engine.approve_approval(
            request_id=request_id,
            approver_id="manager001",
            comment="同意访问",
        ))
        approve_dict = json.loads(approve_result)
        assert approve_dict["status"] == "approved"

    def test_audit_chain(self, engine):
        """测试审计链"""
        asyncio.run(engine.log_audit(
            action="test_audit",
            user_id="test_user",
            resource="test_resource",
        ))

        verify_result = asyncio.run(engine.verify_audit_chain())
        verify_dict = json.loads(verify_result)
        assert verify_dict["valid"] is True

    def test_mask_sensitive_data(self, engine):
        """测试敏感数据脱敏"""
        result = asyncio.run(engine.mask_sensitive_data("phone", "13812345678"))
        result_dict = json.loads(result)
        assert "***" in result_dict["masked"]

    def test_validate_gov_data(self, engine):
        """测试政务数据验证"""
        result = asyncio.run(engine.validate_gov_data(
            "credit_code",
            "91110000MA01ABCD2E",
        ))
        result_dict = json.loads(result)
        assert result_dict["valid"] is True

    def test_stats(self, engine):
        """测试统计信息"""
        stats = engine.get_stats()
        assert "govmcp" in stats
        assert stats["govmcp"]["enabled"] is True


@pytest.fixture
def bridge():
    """创建 Bridge 实例"""
    from taiji_agent.govmcp_bridge import GovMCPBridge

    brdg = GovMCPBridge(host="127.0.0.1", port=18081)
    asyncio.run(brdg.initialize())
    return brdg


class TestGovMCPBridge:
    """GovMCP Bridge 测试"""

    def test_bridge_initialize(self, bridge):
        """测试 Bridge 初始化"""
        assert bridge._initialized is True

    def test_health_check(self, bridge):
        """测试健康检查"""
        response = asyncio.run(bridge._handle_health(None))
        assert response.status == 200


@pytest.fixture
def adapter():
    """创建适配器实例"""
    from taiji_agent.govmcp_integration import create_govmcp_integration
    from taiji_agent.govmcp_integration import GovMCPToolAdapter

    integration = asyncio.run(create_govmcp_integration())
    return GovMCPToolAdapter(integration)


class TestGovMCPToolAdapter:
    """GovMCP 工具适配器测试"""

    def test_to_hermes_tools(self, adapter):
        """测试转换为 Hermes 工具格式"""
        tools = adapter.to_hermes_tools()
        assert len(tools) > 0

        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "category" in tool

    def test_tool_categories(self, adapter):
        """测试工具分类"""
        tools = adapter.to_hermes_tools()
        categories = {t["category"] for t in tools}
        assert "crypto" in categories
        assert "workflow" in categories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
