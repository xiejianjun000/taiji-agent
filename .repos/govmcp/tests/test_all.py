"""
govmcp 全链路集成测试
=====================
测试 crypto / protocol / tools / server 四大模块集成
"""

import json
import os
import sys
import time

import pytest

from govmcp import (
    ApprovalFlow,
    ApprovalStatus,
    AuditChain,
    AuditEntry,
    GovMCPServer,
    ToolRegistry,
    generate_sm2_keypair,
    generate_sm4_key,
    govmcp_tool,
    sm2_calculate_shared_secret,
    sm2_decrypt,
    sm2_derive_key,
    sm2_encrypt,
    sm2_sign,
    sm2_verify,
    sm3_hash,
    sm4_decrypt,
    sm4_encrypt,
)

try:
    from govmcp.crypto.sm import (
        generate_sm4_iv,
        pkcs7_pad,
        pkcs7_unpad,
        sm4_cbc_decrypt,
        sm4_cbc_encrypt,
    )
except ImportError:
    sm4_cbc_encrypt = None
    sm4_cbc_decrypt = None
    generate_sm4_iv = None
    pkcs7_pad = None
    pkcs7_unpad = None


# ============================================================
# Crypto 模块测试
# ============================================================


class TestSM3:
    """SM3 国密哈希"""

    def test_basic_hash(self):
        h = sm3_hash(b"hello")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_empty_input(self):
        h = sm3_hash(b"")
        assert len(h) == 64

    def test_deterministic(self):
        assert sm3_hash(b"govmcp") == sm3_hash(b"govmcp")

    def test_avalanche(self):
        h1 = sm3_hash(b"hello")
        h2 = sm3_hash(b"hallo")
        assert h1 != h2
        diff = sum(a != b for a, b in zip(h1, h2))
        assert diff >= 16


class TestSM4:
    """SM4 国密对称加密"""

    def test_encrypt_decrypt_roundtrip(self):
        key = generate_sm4_key()
        plaintext = b"1234567890ABCDEF" * 2  # 32 bytes = 2 blocks
        ct = sm4_encrypt(plaintext, key)
        pt = sm4_decrypt(ct, key)
        assert pt == plaintext

    def test_single_block(self):
        key = b"\x00" * 16
        pt = b"0123456789ABCDEF"
        ct = sm4_encrypt(pt, key)
        assert len(ct) == 16
        assert sm4_decrypt(ct, key) == pt

    def test_key_wrong_length(self):
        with pytest.raises(ValueError, match="16字节"):
            sm4_encrypt(b"0123456789ABCDEF", b"short")

    def test_plaintext_not_aligned(self):
        key = b"\x00" * 16
        with pytest.raises(ValueError, match="16的倍数"):
            sm4_encrypt(b"not aligned", key)


class TestSM2:
    """SM2 国密非对称加密"""

    def test_keypair_generation(self):
        private_key, public_key = generate_sm2_keypair()
        assert len(private_key) == 32
        assert len(public_key) == 64

    def test_keypair_uniqueness(self):
        kp1 = generate_sm2_keypair()
        kp2 = generate_sm2_keypair()
        assert kp1[0] != kp2[0]
        assert kp1[1] != kp2[1]

    def test_encrypt_decrypt_roundtrip(self):
        private_key, public_key = generate_sm2_keypair()
        plaintext = b"Hello, SM2 encryption!"
        ciphertext = sm2_encrypt(plaintext, public_key)
        assert len(ciphertext) > len(plaintext)
        decrypted = sm2_decrypt(ciphertext, private_key)
        assert decrypted == plaintext

    def test_encrypt_empty_plaintext(self):
        private_key, public_key = generate_sm2_keypair()
        plaintext = b""
        ciphertext = sm2_encrypt(plaintext, public_key)
        assert len(ciphertext) == 96
        decrypted = sm2_decrypt(ciphertext, private_key)
        assert decrypted == plaintext

    def test_encrypt_large_plaintext(self):
        private_key, public_key = generate_sm2_keypair()
        plaintext = b"A" * 10000
        ciphertext = sm2_encrypt(plaintext, public_key)
        decrypted = sm2_decrypt(ciphertext, private_key)
        assert decrypted == plaintext

    def test_encrypt_wrong_public_key_length(self):
        private_key, public_key = generate_sm2_keypair()
        with pytest.raises(ValueError, match="64字节"):
            sm2_encrypt(b"test", private_key[:16])

    def test_decrypt_wrong_private_key_length(self):
        private_key, public_key = generate_sm2_keypair()
        ciphertext = sm2_encrypt(b"test", public_key)
        with pytest.raises(ValueError, match="32字节"):
            sm2_decrypt(ciphertext, public_key[:16])

    def test_decrypt_invalid_ciphertext(self):
        private_key, _ = generate_sm2_keypair()
        with pytest.raises(ValueError):
            sm2_decrypt(b"short", private_key)

    def test_sign_verify_roundtrip(self):
        private_key, public_key = generate_sm2_keypair()
        data = b"Data to sign"
        signature = sm2_sign(data, private_key)
        assert len(signature) == 64
        assert sm2_verify(data, signature, public_key)

    def test_sign_empty_data(self):
        private_key, public_key = generate_sm2_keypair()
        signature = sm2_sign(b"", private_key)
        assert len(signature) == 64
        assert sm2_verify(b"", signature, public_key)

    def test_sign_verify_large_data(self):
        private_key, public_key = generate_sm2_keypair()
        data = b"X" * 100000
        signature = sm2_sign(data, private_key)
        assert sm2_verify(data, signature, public_key)

    def test_verify_wrong_signature(self):
        private_key, public_key = generate_sm2_keypair()
        signature = sm2_sign(b"data", private_key)
        wrong_signature = bytes([b ^ 0xFF for b in signature])
        assert not sm2_verify(b"data", wrong_signature, public_key)

    def test_verify_different_data(self):
        private_key, public_key = generate_sm2_keypair()
        signature = sm2_sign(b"original", private_key)
        assert not sm2_verify(b"modified", signature, public_key)

    def test_verify_wrong_public_key(self):
        private_key, _ = generate_sm2_keypair()
        _, wrong_public = generate_sm2_keypair()
        signature = sm2_sign(b"data", private_key)
        assert not sm2_verify(b"data", signature, wrong_public)

    def test_verify_invalid_signature_length(self):
        _, public_key = generate_sm2_keypair()
        with pytest.raises(ValueError, match="64字节"):
            sm2_verify(b"data", b"short", public_key)

    def test_derive_key_basic(self):
        secret = b"0" * 32
        key = sm2_derive_key(secret, 32)
        assert len(key) == 32

    def test_derive_key_different_outputs(self):
        secret1 = os.urandom(32)
        secret2 = os.urandom(32)
        key1 = sm2_derive_key(secret1, 32)
        key2 = sm2_derive_key(secret2, 32)
        assert key1 != key2

    def test_derive_key_deterministic(self):
        secret = os.urandom(32)
        key1 = sm2_derive_key(secret, 32)
        key2 = sm2_derive_key(secret, 32)
        assert key1 == key2

    def test_derive_key_short_secret(self):
        with pytest.raises(ValueError, match="至少16字节"):
            sm2_derive_key(b"short", 32)

    def test_shared_secret_exchange(self):
        private_a, public_a = generate_sm2_keypair()
        private_b, public_b = generate_sm2_keypair()
        secret_a = sm2_calculate_shared_secret(private_a, public_b)
        secret_b = sm2_calculate_shared_secret(private_b, public_a)
        assert secret_a == secret_b
        assert len(secret_a) == 32

    def test_shared_secret_wrong_private_key_length(self):
        _, public_b = generate_sm2_keypair()
        with pytest.raises(ValueError, match="32字节"):
            sm2_calculate_shared_secret(b"short", public_b)

    def test_shared_secret_wrong_public_key_length(self):
        private_a, _ = generate_sm2_keypair()
        with pytest.raises(ValueError, match="64字节"):
            sm2_calculate_shared_secret(private_a, b"short")

    def test_keypair_public_key_on_curve(self):
        from govmcp.crypto.sm2 import SM2_A, SM2_B, SM2_P, _bytes_to_int

        private_key, public_key = generate_sm2_keypair()
        x = _bytes_to_int(public_key[:32])
        y = _bytes_to_int(public_key[32:])
        lhs = (y * y) % SM2_P
        rhs = (x * x * x + SM2_A * x + SM2_B) % SM2_P
        assert lhs == rhs

    def test_sign_custom_user_id(self):
        private_key, public_key = generate_sm2_keypair()
        custom_id = b"custom_user_12345"
        signature = sm2_sign(b"data", private_key, user_id=custom_id)
        assert sm2_verify(b"data", signature, public_key, user_id=custom_id)

    def test_sign_consistency(self):
        private_key, public_key = generate_sm2_keypair()
        data = b"consistent_data"
        sig1 = sm2_sign(data, private_key)
        sig2 = sm2_sign(data, private_key)
        assert sm2_verify(data, sig1, public_key)
        assert sm2_verify(data, sig2, public_key)


class TestPKCS7:
    """PKCS7 填充/去填充"""

    def test_pad_multiple_of_block(self):
        data = b"0123456789ABCDE"
        padded = pkcs7_pad(data, 16)
        assert len(padded) == 16
        assert padded[:15] == data

    def test_pad_not_aligned(self):
        data = b"Hello"
        padded = pkcs7_pad(data, 16)
        assert len(padded) == 16
        assert padded[:5] == data
        assert padded[5] == 11

    def test_unpad_roundtrip(self):
        original = b"Test data for padding"
        padded = pkcs7_pad(original, 16)
        unpadded = pkcs7_unpad(padded, 16)
        assert unpadded == original

    def test_unpad_invalid_length(self):
        with pytest.raises(ValueError, match="数据长度无效"):
            pkcs7_unpad(b"short", 16)

    def test_unpad_invalid_padding(self):
        data = b"0" * 16
        with pytest.raises(ValueError, match="填充"):
            pkcs7_unpad(data, 16)


class TestSM4CBC:
    """SM4-CBC 国密对称加密"""

    def test_cbc_encrypt_decrypt_roundtrip(self):
        key = generate_sm4_key()
        iv = generate_sm4_iv()
        plaintext = b"1234567890ABCDEF" * 3
        ct = sm4_cbc_encrypt(plaintext, key, iv)
        pt = sm4_cbc_decrypt(ct, key, iv)
        assert pt == plaintext

    def test_cbc_single_block(self):
        key = b"\x00" * 16
        iv = b"\x01" * 16
        pt = b"0123456789ABCDE"
        ct = sm4_cbc_encrypt(pt, key, iv)
        assert len(ct) == 16
        pt2 = sm4_cbc_decrypt(ct, key, iv)
        assert pt2 == pt

    def test_cbc_same_pt_different_ct_with_different_iv(self):
        key = b"\x00" * 16
        plaintext = b"Secret message123"
        iv1 = b"\x00" * 16
        iv2 = b"\xff" * 16
        ct1 = sm4_cbc_encrypt(plaintext, key, iv1)
        ct2 = sm4_cbc_encrypt(plaintext, key, iv2)
        assert ct1 != ct2

    def test_cbc_iv_length_error(self):
        key = b"\x00" * 16
        iv_wrong = b"\x00" * 8
        with pytest.raises(ValueError, match="IV必须为16字节"):
            sm4_cbc_encrypt(b"test", key, iv_wrong)

    def test_cbc_key_length_error(self):
        key = b"\x00" * 8
        iv = b"\x00" * 16
        with pytest.raises(ValueError, match="密钥必须为16字节"):
            sm4_cbc_encrypt(b"test", key, iv)

    def test_cbc_empty_plaintext(self):
        key = generate_sm4_key()
        iv = generate_sm4_iv()
        ct = sm4_cbc_encrypt(b"", key, iv)
        assert len(ct) == 16
        pt = sm4_cbc_decrypt(ct, key, iv)
        assert pt == b""

    def test_cbc_ciphertext_not_multiple_of_block(self):
        key = b"\x00" * 16
        iv = b"\x00" * 16
        with pytest.raises(ValueError, match="16的倍数"):
            sm4_cbc_decrypt(b"short", key, iv)

    def test_cbc_wrong_iv_recovers_wrong_plaintext(self):
        key = b"\x00" * 16
        iv1 = b"\x00" * 16
        iv2 = b"\xff" * 16
        plaintext = b"Original message"
        ct = sm4_cbc_encrypt(plaintext, key, iv1)
        wrong_pt = sm4_cbc_decrypt(ct, key, iv2)
        assert wrong_pt != plaintext

    def test_cbc_generate_iv(self):
        iv = generate_sm4_iv()
        assert len(iv) == 16
        iv2 = generate_sm4_iv()
        assert iv != iv2

    def test_cbc_long_message(self):
        key = generate_sm4_key()
        iv = generate_sm4_iv()
        plaintext = b"A" * 1000
        ct = sm4_cbc_encrypt(plaintext, key, iv)
        assert len(ct) % 16 == 0
        pt = sm4_cbc_decrypt(ct, key, iv)
        assert pt == plaintext

    def test_cbc_with_pkcs7_pad(self):
        key = generate_sm4_key()
        iv = generate_sm4_iv()
        plaintext = b"Variable length data"
        ct = sm4_cbc_encrypt(plaintext, key, iv)
        pt = sm4_cbc_decrypt(ct, key, iv)
        assert pt == plaintext
        assert len(ct) > len(plaintext)


# ============================================================
# Audit 模块测试
# ============================================================


class TestAuditChain:
    """不可篡改审计链"""

    def test_genesis_block(self):
        chain = AuditChain()
        entry = chain.add_entry("init", "system", b"", b"", "approved")
        assert entry.id == 1  # int, not string
        assert entry.prev_hash == "0" * 64
        assert len(entry.current_hash) == 64

    def test_chain_integrity(self):
        chain = AuditChain()
        chain.add_entry("tool_call", "user1", b"input1", b"output1", "approved")
        chain.add_entry("tool_call", "user2", b"input2", b"output2", "approved")
        chain.add_entry("resource_read", "user1", b"", b"data", "approved")
        assert chain.verify()
        assert len(chain.entries) == 3

    def test_tamper_detection(self):
        chain = AuditChain()
        chain.add_entry("op", "user", b"in", b"out", "approved")
        chain.entries[0].operation = "modified"
        assert not chain.verify()

    def test_tamper_detect_input_change(self):
        chain = AuditChain()
        chain.add_entry("op", "user", b"in", b"out", "approved")
        chain.entries[0].input_hash = "f" * 64
        assert not chain.verify()

    def test_export(self):
        chain = AuditChain()
        chain.add_entry("op", "user", b"in", b"out", "approved")
        exported = json.loads(chain.export())
        assert exported["verified"]
        assert len(exported["audit_chain"]) == 1  # key is "audit_chain" not "entries"
        assert exported["audit_chain"][0]["operation"] == "op"

    def test_empty_chain_verify(self):
        chain = AuditChain()
        assert chain.verify()

    def test_to_dict_list(self):
        chain = AuditChain()
        chain.add_entry("op", "u", b"i", b"o", "approved")
        lst = chain.to_dict_list()
        assert len(lst) == 1
        assert lst[0]["operation"] == "op"


# ============================================================
# Tools 模块测试
# ============================================================


class TestToolRegistry:
    """工具注册中心"""

    def test_register_and_list(self):
        reg = ToolRegistry()
        reg.register("test1", "desc1", {"type": "object"}, lambda **kw: "ok")
        reg.register("test2", "desc2", {"type": "object"}, lambda **kw: "ng")
        assert reg.count() == 2
        tools = reg.list_tools()
        assert len(tools) == 2
        assert tools[0]["name"] == "test1"

    def test_call_tool(self):
        reg = ToolRegistry()
        reg.register(
            "add",
            "adds numbers",
            {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}},
            lambda **kw: {"sum": kw["a"] + kw["b"]},
        )
        result = reg.call_tool("add", {"a": 3, "b": 4})
        assert result["content"][0]["type"] == "text"
        assert "7" in result["content"][0]["text"] or "sum" in result["content"][0]["text"]

    def test_call_tool_error(self):
        reg = ToolRegistry()
        reg.register("fail", "always fails", {}, lambda **kw: 1 / 0)
        result = reg.call_tool("fail", {})
        assert result["isError"]

    def test_unregister(self):
        reg = ToolRegistry()
        reg.register("x", "desc", {}, lambda: "ok")
        assert reg.count() == 1
        reg.unregister("x")
        assert reg.count() == 0

    def test_get_raises_keyerror(self):
        """get() raises KeyError for unknown tool"""
        reg = ToolRegistry()
        with pytest.raises(KeyError):
            reg.get("noop")

    def test_call_nonexistent(self):
        """call_tool raises KeyError for unknown tool"""
        reg = ToolRegistry()
        with pytest.raises(KeyError):
            reg.call_tool("noop", {})


class TestGovmcpTool:
    """govmcp_tool 装饰器"""

    def test_auto_infer_schema(self):
        @govmcp_tool()
        def my_tool(x: str, y: int = 0) -> str:
            """My tool docstring"""
            return f"{x}-{y}"

        assert hasattr(my_tool, "_govmcp_meta")
        meta = my_tool._govmcp_meta
        assert meta["name"] == "my_tool"
        assert meta["description"] == "My tool docstring"
        assert "properties" in meta["input_schema"]

    def test_explicit_description(self):
        @govmcp_tool(description="custom desc")
        def func():
            """docstring"""
            pass

        assert func._govmcp_meta["description"] == "custom desc"

    def test_explicit_name(self):
        @govmcp_tool(name="explicit_name")
        def func():
            pass

        assert func._govmcp_meta["name"] == "explicit_name"

    def test_input_schema_required(self):
        @govmcp_tool()
        def func(x: str, y: int):
            pass

        schema = func._govmcp_meta["input_schema"]
        assert "x" in schema.get("required", [])
        assert "y" in schema.get("required", [])


# ============================================================
# Protocol 模块测试
# ============================================================
# GovMCPServer 使用 _mcp_* 方法名 (not _handle_*)


class TestGovMCPServer:
    """MCP 协议服务器"""

    def test_init(self):
        s = GovMCPServer("test", "1.0")
        assert s.name == "test"
        assert s.version == "1.0"

    def test_crypto_init(self):
        key = generate_sm4_key()
        s = GovMCPServer("secure", "1.0", crypto_enabled=True, sm4_key=key)
        assert s.crypto_enabled

    def test_register_tool(self):
        s = GovMCPServer("s", "1.0")
        s.register_tool("echo", "echoes", {"type": "object"}, lambda **kw: kw)
        tools = s._mcp_tools_list({})
        assert len(tools["tools"]) == 1
        assert tools["tools"][0]["name"] == "echo"

    def test_register_resource(self):
        s = GovMCPServer("s", "1.0")
        s.register_resource(
            "docs://readme", "docs", "README", "text/markdown", lambda uri: "# Hello"
        )
        resources = s._mcp_resources_list({})
        assert len(resources["resources"]) == 1

    def test_register_prompt(self):
        s = GovMCPServer("s", "1.0")
        s.register_prompt(
            "greet",
            "greeting prompt",
            [{"name": "user", "required": True}],
            lambda **kw: [{"role": "user", "content": f"Hello {kw['user']}"}],
        )
        prompts = s._mcp_prompts_list({})
        assert len(prompts["prompts"]) == 1

    def test_initialize(self):
        s = GovMCPServer("test-server", "2.0")
        result = s._mcp_initialize({})
        assert result["serverInfo"]["name"] == "test-server"

    def test_sm3_verify(self):
        s = GovMCPServer("s", "1.0")
        h = sm3_hash(b"verify me")
        result = s._mcp_sm3_verify({"data": "verify me", "hash": h})
        assert result["verified"]

    def test_sm3_verify_mismatch(self):
        s = GovMCPServer("s", "1.0")
        result = s._mcp_sm3_verify({"data": "verify me", "hash": "f" * 64})
        assert not result["verified"]

    def test_dispatch_initialize(self):
        s = GovMCPServer("disp-test", "1.0")
        result = s._dispatch("initialize", {})
        assert result["serverInfo"]["name"] == "disp-test"

    def test_dispatch_method_not_found(self):
        s = GovMCPServer("s", "1.0")
        with pytest.raises(ValueError, match="Method not found"):
            s._dispatch("nonexistent/method", {})

    def test_decorator_tool(self):
        """@server.tool() 装饰器注册"""
        s = GovMCPServer("s", "1.0")

        @s.tool(
            "deco-hello",
            description="deco test",
            input_schema={"type": "object", "properties": {"name": {"type": "string"}}},
        )
        def hello(**kw):
            return f"hi {kw['name']}"

        tools = s._mcp_tools_list({})
        assert len(tools["tools"]) == 1
        assert tools["tools"][0]["name"] == "deco-hello"

    def test_decorator_tool_auto_name(self):
        """@server.tool() 自动用函数名"""
        s = GovMCPServer("s", "1.0")

        @s.tool()
        def my_func(**kw):
            pass

        tools = s._mcp_tools_list({})
        assert tools["tools"][0]["name"] == "my_func"

    def test_decorator_resource(self):
        """@server.resource() 装饰器"""
        s = GovMCPServer("s", "1.0")

        @s.resource("docs://readme", name="README", mime_type="text/markdown")
        def readme(uri):
            return "# Hello"

        resources = s._mcp_resources_list({})
        assert len(resources["resources"]) == 1

    def test_decorator_prompt(self):
        """@server.prompt() 装饰器"""
        s = GovMCPServer("s", "1.0")

        @s.prompt("greet", description="greeting")
        def greet(**kw):
            return [{"role": "user", "content": f"hi {kw.get('user', '')}"}]

        prompts = s._mcp_prompts_list({})
        assert len(prompts["prompts"]) == 1


# ============================================================
# Server 模块测试
# ============================================================


class TestApprovalFlow:
    """审批工作流"""

    def test_single_approval_approved(self):
        f = ApprovalFlow(["admin"])
        result = f.approve("admin")
        assert result == ApprovalStatus.APPROVED
        assert f.is_approved()
        assert f.is_complete()

    def test_single_approval_rejected(self):
        f = ApprovalFlow(["admin"])
        result = f.reject("admin")
        assert result == ApprovalStatus.REJECTED
        assert not f.is_approved()

    def test_multi_level_approval(self):
        """每级 approve 返回 APPROVED，流程推进后才 complete"""
        f = ApprovalFlow(["l1", "l2", "l3"])
        r1 = f.approve("l1")
        assert r1 == ApprovalStatus.APPROVED
        assert not f.is_complete()  # 还有两级
        r2 = f.approve("l2")
        assert r2 == ApprovalStatus.APPROVED
        assert not f.is_complete()  # 还有一级
        r3 = f.approve("l3")
        assert r3 == ApprovalStatus.APPROVED
        assert f.is_complete()
        assert f.is_approved()

    def test_wrong_approver_raises(self):
        """错误审批人抛 ValueError"""
        f = ApprovalFlow(["admin"])
        with pytest.raises(ValueError, match="审批人不匹配"):
            f.approve("hacker")

    def test_skip(self):
        f = ApprovalFlow(["l1", "l2"])
        f.skip("bypass level 1")
        assert f.steps[0].status == ApprovalStatus.SKIPPED
        f.approve("l2")
        assert f.is_approved()

    def test_timeout_auto_reject(self):
        f = ApprovalFlow(["admin"], timeout=0.01, auto_approve_on_timeout=False)
        time.sleep(0.02)
        result = f.approve("admin")
        assert result in (ApprovalStatus.TIMEOUT, ApprovalStatus.REJECTED)

    def test_timeout_auto_approve(self):
        f = ApprovalFlow(["admin"], timeout=0.01, auto_approve_on_timeout=True)
        time.sleep(0.02)
        f.approve("admin")
        assert f.is_approved()

    def test_reject_cascade(self):
        f = ApprovalFlow(["l1", "l2", "l3"])
        f.reject("l1")
        assert f.steps[0].status == ApprovalStatus.REJECTED
        assert all(s.status == ApprovalStatus.SKIPPED for s in f.steps[1:])

    def test_to_dict_list(self):
        f = ApprovalFlow(["admin"])
        f.approve("admin")
        lst = f.to_dict_list()
        assert len(lst) == 1
        assert lst[0]["approver"] == "admin"

    def test_empty_approvers(self):
        with pytest.raises(ValueError, match="列表不能为空"):
            ApprovalFlow([])


# ============================================================
# 集成测试：全链路
# ============================================================


def test_full_integration():
    """Server + Tool + Audit + Approval + Crypto 全链路"""
    key = generate_sm4_key()
    s = GovMCPServer("govmcp-int", "1.0", crypto_enabled=True, sm4_key=key)

    # 注册工具
    s.register_tool(
        "calc_carbon",
        "碳排放计算",
        {
            "type": "object",
            "properties": {"fuel": {"type": "string"}, "tons": {"type": "number"}},
            "required": ["fuel", "tons"],
        },
        lambda **kw: {"emission": kw["tons"] * 2.86},
    )

    # MCP initialize
    init = s._mcp_initialize({})
    assert init["serverInfo"]["name"] == "govmcp-int"

    # 列出工具
    tools = s._mcp_tools_list({})
    assert len(tools["tools"]) == 1

    # 调用工具
    result = s._mcp_tools_call({"name": "calc_carbon", "arguments": {"fuel": "coal", "tons": 100}})
    content = result["content"]
    assert len(content) > 0

    # SM3 完整性
    verify = s._mcp_sm3_verify({"data": "integrity", "hash": sm3_hash(b"integrity")})
    assert verify["verified"]

    # 审计链 + 审批流集成
    chain = AuditChain()
    f = ApprovalFlow(["admin"], audit_chain=chain)
    f.approve("admin")
    assert f.is_approved()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))


# ============================================================
# Government Tools Module Tests
# ============================================================


class TestCitizenServiceTools:
    """市民服务工具测试"""

    def test_query_id_card_progress(self):
        from govmcp.tools.government.citizen_service import query_id_card_progress

        result = query_id_card_progress(
            name="张三", id_number="110101199001011234", phone="13800138000"
        )
        assert result["status"] == "success"
        assert "progress" in result["data"]

    def test_query_household_registration(self):
        from govmcp.tools.government.citizen_service import query_household_registration

        result = query_household_registration(id_number="110101199001011234", name="张三")
        assert result["status"] == "success"
        assert result["data"]["name"] == "张三"

    def test_query_social_security_account(self):
        from govmcp.tools.government.citizen_service import query_social_security_account

        result = query_social_security_account(id_number="110101199001011234", name="张三")
        assert result["status"] == "success"
        assert "balance" in result["data"]

    def test_query_social_security_payment(self):
        from govmcp.tools.government.citizen_service import query_social_security_payment

        result = query_social_security_payment(id_number="110101199001011234", year=2026, month=5)
        assert result["status"] == "success"

    def test_query_medical_insurance_account(self):
        from govmcp.tools.government.citizen_service import query_medical_insurance_account

        result = query_medical_insurance_account(id_number="110101199001011234", name="张三")
        assert result["status"] == "success"

    def test_query_housing_fund_account(self):
        from govmcp.tools.government.citizen_service import query_housing_fund_account

        result = query_housing_fund_account(id_number="110101199001011234", name="张三")
        assert result["status"] == "success"

    def test_query_driver_license(self):
        from govmcp.tools.government.citizen_service import query_driver_license

        result = query_driver_license(name="张三", license_no="110000000000000")
        assert result["status"] == "success"

    def test_query_vehicle_info(self):
        from govmcp.tools.government.citizen_service import query_vehicle_info

        result = query_vehicle_info(plate_number="京A12345", id_number="110101199001011234")
        assert result["status"] == "success"


class TestEnterpriseServiceTools:
    """企业服务工具测试"""

    def test_query_business_registration(self):
        from govmcp.tools.government.enterprise_service import query_business_registration

        result = query_business_registration(
            company_name="测试公司", unified_social_credit_code="91110000MA00ABCD01"
        )
        assert result["status"] == "success"

    def test_apply_business_license(self):
        from govmcp.tools.government.enterprise_service import apply_business_license

        result = apply_business_license(
            company_name="测试公司",
            company_type="有限责任公司",
            registered_capital=1000000,
            business_scope="技术开发",
            address="XX市XX区",
            legal_person="张三",
            id_number="110101199001011234",
        )
        assert result["status"] == "success"

    def test_query_tax_registration(self):
        from govmcp.tools.government.enterprise_service import query_tax_registration

        result = query_tax_registration(company_name="测试公司", tax_id="91110000MA00ABCD01")
        assert result["status"] == "success"

    def test_apply_invoice(self):
        from govmcp.tools.government.enterprise_service import apply_invoice

        result = apply_invoice(
            company_name="测试公司",
            tax_id="91110000MA00ABCD01",
            invoice_type="增值税普通发票",
            quantity=50,
        )
        assert result["status"] == "success"


class TestCarbonEmissionTools:
    """碳排放工具测试"""

    def test_input_carbon_emission_data(self):
        from govmcp.tools.government.carbon_emission import input_carbon_emission_data

        result = input_carbon_emission_data(
            company_name="测试公司",
            credit_code="91110000MA00ABCD01",
            reporting_year=2026,
            reporting_quarter=1,
            coal_consumption=100,
            oil_consumption=10,
            natural_gas_consumption=5,
            electricity_consumption=100,
        )
        assert result["status"] == "success"
        assert "total_emission" in result["data"]

    def test_query_carbon_quota(self):
        from govmcp.tools.government.carbon_emission import query_carbon_quota

        result = query_carbon_quota(
            company_name="测试公司", credit_code="91110000MA00ABCD01", year=2026
        )
        assert result["status"] == "success"

    def test_calculate_carbon_footprint(self):
        from govmcp.tools.government.carbon_emission import calculate_carbon_footprint

        result = calculate_carbon_footprint(
            product_name="测试产品",
            raw_materials={"钢材": 100, "塑料": 50},
            manufacturing_energy=500,
            transportation_distance=200,
            packaging_weight=20,
        )
        assert result["status"] == "success"
        assert "carbon_footprint" in result["data"]

    def test_predict_carbon_emission(self):
        from govmcp.tools.government.carbon_emission import predict_carbon_emission

        result = predict_carbon_emission(
            company_name="测试公司", historical_data=[], forecast_years=3
        )
        assert result["status"] == "success"


class TestEnvironmentalTools:
    """环保监测工具测试"""

    def test_query_air_quality(self):
        from govmcp.tools.government.environmental import query_air_quality

        result = query_air_quality(region="北京市", monitoring_station="朝阳站", date="2026-05-13")
        assert result["status"] == "success"
        assert "aqi" in result["data"]

    def test_query_water_quality(self):
        from govmcp.tools.government.environmental import query_water_quality

        result = query_water_quality(river_name="黄河", section_name="兰州断面", date="2026-05-13")
        assert result["status"] == "success"

    def test_query_pollution_discharge_permit(self):
        from govmcp.tools.government.environmental import query_pollution_discharge_permit

        result = query_pollution_discharge_permit(company_name="测试公司", permit_no="PD2024001")
        assert result["status"] == "success"


class TestSmartCityTools:
    """智慧城市工具测试"""

    def test_control_smart_traffic_light(self):
        from govmcp.tools.government.smart_city import control_smart_traffic_light

        result = control_smart_traffic_light(intersection_id="I001", action="绿灯", duration=30)
        assert result["status"] == "success"

    def test_query_public_parking(self):
        from govmcp.tools.government.smart_city import query_public_parking

        result = query_public_parking(district="朝阳区", street="建国路")
        assert result["status"] == "success"

    def test_book_smart_medical(self):
        from govmcp.tools.government.smart_city import book_smart_medical

        result = book_smart_medical(
            patient_name="张三",
            id_number="110101199001011234",
            hospital="北京医院",
            department="内科",
            booking_date="2026-05-20",
        )
        assert result["status"] == "success"


class TestApprovalWorkflowTools:
    """审批工作流工具测试"""

    def test_initiate_approval_workflow(self):
        from govmcp.tools.government.approval_workflow import initiate_approval_workflow

        result = initiate_approval_workflow(
            workflow_name="请假申请",
            applicant_name="张三",
            applicant_department="技术部",
            workflow_type="请假",
            business_data={"days": 3},
        )
        assert result["status"] == "success"

    def test_query_approval_progress(self):
        from govmcp.tools.government.approval_workflow import query_approval_progress

        result = query_approval_progress(workflow_id="WF202605001")
        assert result["status"] == "success"

    def test_submit_approval_comment(self):
        from govmcp.tools.government.approval_workflow import submit_approval_comment

        result = submit_approval_comment(
            workflow_id="WF202605001", approver_name="李四", action="同意", comment="同意申请"
        )
        assert result["status"] == "success"

    def test_generate_approval_document(self):
        from govmcp.tools.government.approval_workflow import generate_approval_document

        result = generate_approval_document(
            workflow_id="WF202605001", document_type="审批表", include_attachments=True
        )
        assert result["status"] == "success"


class TestGovernmentToolsTotal:
    """政务工具库总数验证"""

    def test_tool_count(self):
        from govmcp.tools.government import TOOL_COUNT, TOTAL_TOOLS

        assert TOTAL_TOOLS == 100
        assert TOOL_COUNT["citizen_service"] == 20
        assert TOOL_COUNT["enterprise_service"] == 20
        assert TOOL_COUNT["carbon_emission"] == 15
        assert TOOL_COUNT["environmental"] == 15
        assert TOOL_COUNT["smart_city"] == 15
        assert TOOL_COUNT["approval_workflow"] == 15

    def test_all_tools_importable(self):
        import govmcp.tools.government as gov

        assert hasattr(gov, "citizen_service")
        assert hasattr(gov, "enterprise_service")
        assert hasattr(gov, "carbon_emission")
        assert hasattr(gov, "environmental")
        assert hasattr(gov, "smart_city")
        assert hasattr(gov, "approval_workflow")


# ============================================================
# Models 模块测试
# ============================================================


class TestModelRegistry:
    """模型注册表测试"""

    def test_registry_singleton(self):
        from govmcp.models import ModelRegistry

        r1 = ModelRegistry()
        r2 = ModelRegistry()
        assert r1 is r2

    def test_registry_count(self):
        from govmcp.models import ModelRegistry

        registry = ModelRegistry()
        assert registry.count() >= 48

    def test_get_model_ernie(self):
        from govmcp.models import get_model

        config = get_model("ernie-4.0")
        assert config is not None
        assert config.model_id == "ernie-4.0"

    def test_get_model_qwen(self):
        from govmcp.models import get_model

        config = get_model("qwen-turbo")
        assert config is not None
        assert config.model_id == "qwen-turbo"

    def test_get_model_glm(self):
        from govmcp.models import get_model

        config = get_model("glm-4")
        assert config is not None
        assert config.model_id == "glm-4"

    def test_get_model_spark(self):
        from govmcp.models import get_model

        config = get_model("spark-3.5")
        assert config is not None
        assert config.model_id == "spark-3.5"

    def test_get_model_hunyuan(self):
        from govmcp.models import get_model

        config = get_model("hunyuan-pro")
        assert config is not None
        assert config.model_id == "hunyuan-pro"

    def test_get_model_pangu(self):
        from govmcp.models import get_model

        config = get_model("pangu-chat")
        assert config is not None
        assert config.model_id == "pangu-chat"

    def test_get_model_doubao(self):
        from govmcp.models import get_model

        config = get_model("doubao-pro")
        assert config is not None
        assert config.model_id == "doubao-pro"

    def test_get_model_minimax(self):
        from govmcp.models import get_model

        config = get_model("minimax-abab6")
        assert config is not None
        assert config.model_id == "minimax-abab6"

    def test_get_model_kimi(self):
        from govmcp.models import get_model

        config = get_model("kimi-chat")
        assert config is not None
        assert config.model_id == "kimi-chat"

    def test_get_model_baichuan(self):
        from govmcp.models import get_model

        config = get_model("baichuan4")
        assert config is not None
        assert config.model_id == "baichuan4"

    def test_get_model_sensechat(self):
        from govmcp.models import get_model

        config = get_model("sensechat-5")
        assert config is not None
        assert config.model_id == "sensechat-5"

    def test_get_model_internlm(self):
        from govmcp.models import get_model

        config = get_model("internlm2-chat")
        assert config is not None
        assert config.model_id == "internlm2-chat"

    def test_validate_model(self):
        from govmcp.models import validate_model

        assert validate_model("ernie-4.0")
        assert validate_model("qwen-max")
        assert validate_model("glm-4-plus")
        assert not validate_model("nonexistent-model")

    def test_list_models_by_provider(self):
        from govmcp.models import LLMProvider, list_models

        wenxin_models = list_models(LLMProvider.WENXIN)
        assert len(wenxin_models) == 4
        qwen_models = list_models(LLMProvider.QWEN)
        assert len(qwen_models) == 7

    def test_list_all_models(self):
        from govmcp.models import list_models

        models = list_models()
        assert len(models) >= 48

    def test_register_new_model(self):
        from govmcp.models import LLMProvider, ModelConfig, ModelRegistry

        registry = ModelRegistry()
        initial_count = registry.count()
        new_config = ModelConfig(
            provider=LLMProvider.UNKNOWN,
            model_id="test-model",
            api_base="https://test.com",
            capabilities={},
        )
        result = registry.register_model(LLMProvider.UNKNOWN, "test-model", new_config)
        assert result is True
        assert registry.count() == initial_count + 1

    def test_register_duplicate_model(self):
        from govmcp.models import LLMProvider, ModelConfig, ModelRegistry

        registry = ModelRegistry()
        config = registry.get_model("ernie-4.0")
        result = registry.register_model(LLMProvider.WENXIN, "ernie-4.0", config)
        assert result is False

    def test_model_config_capabilities(self):
        from govmcp.models import get_model

        config = get_model("qwen-turbo")
        assert config.supports_streaming()
        assert config.supports_function_call()
        assert config.supports_vision()
        assert config.supports_embedding()

    def test_adapter_retrieval(self):
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not installed")
        from govmcp.models import ModelRegistry

        registry = ModelRegistry()
        adapter = registry.get_adapter("ernie-4.0")
        assert adapter is not None
        assert adapter.model_id == "ernie-4.0"

    def test_llm_provider_from_model_id(self):
        from govmcp.models import LLMProvider

        assert LLMProvider.from_model_id("ernie-4.0") == LLMProvider.WENXIN
        assert LLMProvider.from_model_id("qwen-turbo") == LLMProvider.QWEN
        assert LLMProvider.from_model_id("glm-4") == LLMProvider.ZHIPU
        assert LLMProvider.from_model_id("spark-3.5") == LLMProvider.SPARK
        assert LLMProvider.from_model_id("hunyuan-pro") == LLMProvider.HUNYUAN

    def test_get_providers(self):
        from govmcp.models import LLMProvider, ModelRegistry

        registry = ModelRegistry()
        providers = registry.get_providers()
        assert LLMProvider.WENXIN in providers
        assert LLMProvider.QWEN in providers
        assert LLMProvider.ZHIPU in providers
        assert len(providers) >= 19
