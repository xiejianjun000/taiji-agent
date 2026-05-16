"""
GovMCP Server MCP 协议兼容性测试

测试 GovMCP Server 作为 MCP Server 的协议兼容性
"""

import asyncio
import json
import pytest


@pytest.fixture
def server():
    """创建 GovMCP Server 实例"""
    from taiji_agent.govmcp.server import GovMCPServer

    srv = GovMCPServer()
    asyncio.run(srv.initialize())
    assert srv.is_initialized
    return srv


class TestGovMCPServerMCPCompatibility:
    """GovMCP Server MCP 协议兼容性测试"""

    def test_initialize(self, server):
        """测试初始化"""
        result = asyncio.run(server.initialize())
        assert result["name"] == "GovMCP"
        assert result["version"] == "1.0.0"
        assert "tools_count" in result
        assert result["tools_count"] == 20

    def test_get_tools_list(self, server):
        """测试获取工具列表 (MCP tools/list)"""
        tools = server.get_tools()
        assert len(tools) == 20
        tool_names = [t["name"] for t in tools]
        assert "sm3_hash" in tool_names
        assert "sm4_encrypt" in tool_names
        assert "sm4_decrypt" in tool_names
        assert "sm2_encrypt" in tool_names
        assert "sm2_decrypt" in tool_names
        assert "approval_create" in tool_names
        assert "approval_approve" in tool_names
        assert "audit_log" in tool_names
        assert "mask_id_number" in tool_names
        assert "validate_id_number" in tool_names

    def test_tool_schema_format(self, server):
        """测试工具 schema 格式符合 MCP 规范"""
        tools = server.get_tools()
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"
            assert "properties" in tool["inputSchema"]

    def test_sm3_hash_tool(self, server):
        """测试 SM3 哈希工具"""
        result = asyncio.run(server.call_tool("sm3_hash", {"data": "test data"}))
        result_dict = json.loads(result)
        assert "hash" in result_dict
        assert result_dict["algorithm"] == "SM3"
        assert len(result_dict["hash"]) == 64

    def test_sm4_encrypt_decrypt(self, server):
        """测试 SM4 加解密工具"""
        encrypt_result = asyncio.run(server.call_tool(
            "sm4_encrypt", {"data": "敏感数据测试"}
        ))
        encrypt_dict = json.loads(encrypt_result)
        assert "encrypted_data" in encrypt_dict
        assert encrypt_dict["algorithm"] == "SM4"

        decrypt_result = asyncio.run(server.call_tool(
            "sm4_decrypt",
            {"encrypted_data": encrypt_dict["encrypted_data"]}
        ))
        decrypt_dict = json.loads(decrypt_result)
        assert decrypt_dict["decrypted_data"] == "敏感数据测试"

    def test_sm2_keygen_encrypt_decrypt(self, server):
        """测试 SM2 密钥生成和加解密"""
        keygen_result = asyncio.run(server.call_tool(
            "sm2_generate_keypair", {"key_id": "test_key"}
        ))
        keygen_dict = json.loads(keygen_result)
        assert keygen_dict["key_id"] == "test_key"
        assert "public_key" in keygen_dict

        encrypt_result = asyncio.run(server.call_tool(
            "sm2_encrypt",
            {"data": "SM2测试数据", "public_key_id": "test_key"}
        ))
        encrypt_dict = json.loads(encrypt_result)
        assert "encrypted_data" in encrypt_dict

        decrypt_result = asyncio.run(server.call_tool(
            "sm2_decrypt",
            {"encrypted_data": encrypt_dict["encrypted_data"], "private_key_id": "test_key"}
        ))
        decrypt_dict = json.loads(decrypt_result)
        assert decrypt_dict["decrypted_data"] == "SM2测试数据"

    def test_approval_workflow(self, server):
        """测试审批工作流工具"""
        create_result = asyncio.run(server.call_tool("approval_create", {
            "title": "测试审批",
            "description": "这是一条测试审批",
            "requester": "user001",
            "department": "技术部"
        }))
        create_dict = json.loads(create_result)
        assert "request_id" in create_dict
        request_id = create_dict["request_id"]

        approve_result = asyncio.run(server.call_tool("approval_approve", {
            "request_id": request_id,
            "approver_id": "manager001",
            "comment": "同意"
        }))
        approve_dict = json.loads(approve_result)
        assert approve_dict["status"] == "approved"

    def test_audit_log_and_query(self, server):
        """测试审计日志工具"""
        log_result = asyncio.run(server.call_tool("audit_log", {
            "action": "test_action",
            "user_id": "test_user",
            "resource": "test_resource",
            "details": {"key": "value"},
            "success": True
        }))
        log_dict = json.loads(log_result)
        assert log_dict["status"] == "logged"

        query_result = asyncio.run(server.call_tool("audit_query", {
            "user_id": "test_user",
            "limit": 10
        }))
        query_dict = json.loads(query_result)
        assert query_dict["count"] >= 1

    def test_audit_chain_verify(self, server):
        """测试审计链验证"""
        asyncio.run(server.call_tool("audit_log", {
            "action": "test_chain",
            "user_id": "chain_user",
            "resource": "chain_resource"
        }))

        verify_result = asyncio.run(server.call_tool("audit_verify", {}))
        verify_dict = json.loads(verify_result)
        assert verify_dict["valid"] is True
        assert "record_count" in verify_dict

    def test_data_masking_tools(self, server):
        """测试数据脱敏工具"""
        id_masked = asyncio.run(server.call_tool("mask_id_number", {
            "id_number": "110101199001011234"
        }))
        id_dict = json.loads(id_masked)
        assert "***" in id_dict["masked"]

        phone_masked = asyncio.run(server.call_tool("mask_phone", {
            "phone": "13812345678"
        }))
        phone_dict = json.loads(phone_masked)
        assert "***" in phone_dict["masked"]

        bank_masked = asyncio.run(server.call_tool("mask_bank_card", {
            "bank_card": "6217000010010010011"
        }))
        bank_dict = json.loads(bank_masked)
        assert "***" in bank_dict["masked"]

    def test_validation_tools(self, server):
        """测试验证工具"""
        valid_id = asyncio.run(server.call_tool("validate_id_number", {
            "id_number": "11010519491231002X"
        }))
        valid_id_dict = json.loads(valid_id)
        assert valid_id_dict["valid"] is True

        valid_credit = asyncio.run(server.call_tool("validate_credit_code", {
            "credit_code": "91110000MA01ABCD2E"
        }))
        valid_credit_dict = json.loads(valid_credit)
        assert valid_credit_dict["valid"] is True

    def test_workday_calculation(self, server):
        """测试工作日计算"""
        result = asyncio.run(server.call_tool("calculate_workday", {
            "start_date": "2026-05-15",
            "days": 5
        }))
        result_dict = json.loads(result)
        assert "result_date" in result_dict

    def test_tool_not_found(self, server):
        """测试工具不存在的情况"""
        result = asyncio.run(server.call_tool("nonexistent_tool", {}))
        result_dict = json.loads(result)
        assert "error" in result_dict
        assert "Tool not found" in result_dict["error"]


class TestGovMCPServerIntegration:
    """GovMCP Server 集成测试"""

    def test_full_workflow(self):
        """测试完整工作流：加密 -> 审批 -> 审计"""
        from taiji_agent.govmcp.server import GovMCPServer

        server = GovMCPServer()
        asyncio.run(server.initialize())

        data = "需要加密的敏感政务数据"
        encrypt_result = asyncio.run(server.call_tool("sm4_encrypt", {"data": data}))
        encrypt_dict = json.loads(encrypt_result)
        encrypted = encrypt_dict["encrypted_data"]

        approval_result = asyncio.run(server.call_tool("approval_create", {
            "title": "数据访问申请",
            "description": f"申请访问加密数据: {encrypted[:20]}...",
            "requester": "officer001",
            "department": "政务服务中心"
        }))
        approval_dict = json.loads(approval_result)
        request_id = approval_dict["request_id"]

        audit_result = asyncio.run(server.call_tool("audit_log", {
            "action": "data_encryption",
            "user_id": "officer001",
            "resource": request_id,
            "details": {"encrypted": True, "algorithm": "SM4"}
        }))
        audit_dict = json.loads(audit_result)
        assert audit_dict["status"] == "logged"

        verify_result = asyncio.run(server.call_tool("audit_verify", {}))
        verify_dict = json.loads(verify_result)
        assert verify_dict["valid"] is True

        print("\n完整工作流测试通过！")


if __name__ == "__main__":
    asyncio.run(TestGovMCPServerIntegration().test_full_workflow())
