"""
GovMCP 整合测试
"""

import asyncio
import datetime
import pytest

from taiji_agent.govmcp.crypto import (
    SM2Encryptor,
    SM4Encryptor,
    SM3Hash,
    KeyManager,
    AuditTrail,
    KeyPair,
)
from taiji_agent.govmcp.workflow import (
    ApprovalWorkflow,
    ApprovalStatus,
    ApprovalStep,
    Approver,
)
from taiji_agent.govmcp.tools import (
    GovTools,
    IDNumberHelper,
    SocialCreditCodeHelper,
    CalendarHelper,
)
from taiji_agent.govmcp.plugins import GovMCPPlugin


class TestCrypto:
    """国密加密测试"""

    def test_sm3_hash(self):
        """SM3 哈希测试"""
        data = b"Hello, Taiji Agent!"
        hash1 = SM3Hash.hash(data)
        hash2 = SM3Hash.hash(data)
        
        assert hash1 == hash2
        assert len(hash1) > 0

    def test_sm4_encrypt_decrypt(self):
        """SM4 加密解密测试"""
        import os
        
        key = os.urandom(16)
        encryptor = SM4Encryptor(key)
        
        plaintext = b"Government data encryption test"
        ciphertext = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(ciphertext)
        
        assert decrypted == plaintext

    def test_key_manager(self):
        """密钥管理器测试"""
        km = KeyManager()
        
        key_pair = km.generate_sm2_key_pair("test")
        assert key_pair.private_key is not None
        assert key_pair.public_key is not None
        
        key = km.generate_sm4_key("test")
        assert len(key) == 16
        
        assert km.get_sm2_key_pair("test") is not None
        assert km.get_sm4_key("test") is not None

    def test_audit_trail(self):
        """审计追踪测试"""
        audit = AuditTrail()
        
        audit.record_action(
            user_id="user-1",
            action="create",
            resource="document-1",
        )
        
        audit.record_action(
            user_id="user-2",
            action="approve",
            resource="document-1",
        )
        
        records = audit.get_records()
        assert len(records) == 2
        
        valid, errors = audit.verify_chain()
        assert valid is True
        assert len(errors) == 0


class TestApprovalWorkflow:
    """审批工作流测试"""

    @pytest.mark.asyncio
    async def test_create_and_submit_request(self):
        """创建并提交审批测试"""
        workflow = ApprovalWorkflow()
        
        request = workflow.create_request(
            title="Project Approval",
            description="EIA project approval",
            requester="user-1",
            department="EPA",
        )
        
        assert request.request_id is not None
        assert request.status == ApprovalStatus.DRAFT
        
        await workflow.submit_request(request.request_id)
        
        updated = workflow.get_request(request.request_id)
        assert updated.status == ApprovalStatus.PENDING

    @pytest.mark.asyncio
    async def test_approve_request(self):
        """批准审批测试"""
        workflow = ApprovalWorkflow()
        
        request = workflow.create_request(
            title="Project Approval",
            description="EIA project approval",
            requester="user-1",
            department="EPA",
        )
        
        await workflow.submit_request(request.request_id)
        decision = await workflow.approve(
            request_id=request.request_id,
            approver_id="manager",
            comment="Approved",
        )
        
        assert decision.action.value == "approve"
        
        updated = workflow.get_request(request.request_id)
        assert updated.status in [
            ApprovalStatus.APPROVED,
            ApprovalStatus.COMPLETED,
        ]

    @pytest.mark.asyncio
    async def test_reject_request(self):
        """拒绝审批测试"""
        workflow = ApprovalWorkflow()
        
        request = workflow.create_request(
            title="Project Approval",
            description="EIA project approval",
            requester="user-1",
            department="EPA",
        )
        
        await workflow.submit_request(request.request_id)
        decision = await workflow.reject(
            request_id=request.request_id,
            approver_id="manager",
            comment="Missing documents",
        )
        
        assert decision.action.value == "reject"
        
        updated = workflow.get_request(request.request_id)
        assert updated.status == ApprovalStatus.REJECTED

    def test_list_requests(self):
        """列出审批请求测试"""
        workflow = ApprovalWorkflow()
        
        workflow.create_request(
            title="Project1",
            description="Description1",
            requester="user-1",
            department="EPA",
        )
        
        workflow.create_request(
            title="Project2",
            description="Description2",
            requester="user-1",
            department="EPA",
        )
        
        requests = workflow.list_requests(user_id="user-1")
        assert len(requests) == 2


class TestGovTools:
    """政务工具测试"""

    def test_id_number_validation(self):
        """身份证号验证测试"""
        valid_id = "110101199003077758"
        invalid_id = "11010119900307775X"
        
        assert IDNumberHelper.validate_id_number(valid_id) is True
        assert IDNumberHelper.validate_id_number(invalid_id) is False

    def test_id_number_masking(self):
        """身份证号脱敏测试"""
        masked = IDNumberHelper.mask_id_number("110101199003077758")
        assert masked == "110101********7758"

    def test_extract_birthday(self):
        """提取生日测试"""
        birthday = IDNumberHelper.extract_birthday("110101199003077758")
        assert birthday is not None
        assert birthday.year == 1990
        assert birthday.month == 3
        assert birthday.day == 7

    def test_credit_code_validation(self):
        """统一社会信用代码验证测试"""
        code = "911100007178299245"
        assert SocialCreditCodeHelper.validate_credit_code(code) is True

    def test_phone_masking(self):
        """手机号脱敏测试"""
        masked = GovTools.masking.mask_phone("13800138000")
        assert masked == "138****8000"

    def test_workday_calculation(self):
        """工作日计算测试"""
        monday = datetime.date(2024, 12, 23)
        friday = datetime.date(2024, 12, 27)
        
        assert CalendarHelper.is_workday(monday) is True
        
        workdays = CalendarHelper.calculate_workdays(monday, friday)
        assert workdays >= 1


class TestGovMCPPlugin:
    """GovMCP 插件测试"""

    @pytest.mark.asyncio
    async def test_plugin_load_activate(self):
        """插件加载和激活测试"""
        plugin = GovMCPPlugin()
        
        loaded = await plugin.on_load()
        assert loaded is True
        
        activated = await plugin.on_activate()
        assert activated is True

    @pytest.mark.asyncio
    async def test_plugin_encryption(self):
        """插件加密解密测试"""
        plugin = GovMCPPlugin()
        await plugin.on_load()
        
        data = b"Sensitive government data"
        encrypted = await plugin.encrypt_sm4(data)
        decrypted = await plugin.decrypt_sm4(encrypted)
        
        assert decrypted == data

    @pytest.mark.asyncio
    async def test_plugin_hashing(self):
        """插件哈希测试"""
        plugin = GovMCPPlugin()
        
        data = b"Government data"
        hash1 = await plugin.hash_sm3(data)
        hash2 = await plugin.hash_sm3(data)
        
        assert hash1 == hash2

    @pytest.mark.asyncio
    async def test_plugin_audit_log(self):
        """插件审计日志测试"""
        plugin = GovMCPPlugin()
        await plugin.on_load()
        
        await plugin.log_audit(
            action="create",
            user_id="user-1",
            resource="doc-1",
        )
        
        await plugin.log_audit(
            action="approve",
            user_id="user-2",
            resource="doc-1",
        )
        
        logs = plugin.get_audit_logs()
        assert len(logs) == 2

    @pytest.mark.asyncio
    async def test_plugin_approval(self):
        """插件审批流程测试"""
        plugin = GovMCPPlugin()
        await plugin.on_load()
        
        request_id = await plugin.create_approval(
            title="EIA Approval",
            description="Environmental assessment approval",
            requester="user-1",
            department="EPA",
        )
        
        await plugin.submit_approval(request_id)
        await plugin.approve(request_id, "manager", "Approved")
        
        status = plugin.get_approval_status(request_id)
        assert status["found"] is True

    @pytest.mark.asyncio
    async def test_plugin_audit_chain(self):
        """插件审计链验证测试"""
        plugin = GovMCPPlugin()
        await plugin.on_load()
        
        for i in range(3):
            await plugin.log_audit(
                action=f"action-{i}",
                user_id="user-1",
                resource=f"resource-{i}",
            )
        
        valid, errors = plugin.verify_audit_chain()
        assert valid is True
        assert len(errors) == 0

    def test_plugin_stats(self):
        """插件统计测试"""
        plugin = GovMCPPlugin()
        
        stats = plugin.get_stats()
        assert "state" in stats
        assert "audit_entries" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
