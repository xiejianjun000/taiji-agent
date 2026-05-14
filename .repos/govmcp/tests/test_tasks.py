#!/usr/bin/env python3
"""
govmcp 异步任务及 MCP 2025.11 规范测试
==========================================

测试异步任务、采样、用户交互和授权功能。
"""

import asyncio
import time
from typing import Any

import pytest

from govmcp.protocol.authorization import (
    AuthorizationCode,
    AuthorizationManager,
    AuthorizationScope,
    ClientInfo,
    FineGrainedPermissionManager,
    GrantType,
    Permission,
    TokenInfo,
    TokenType,
)
from govmcp.protocol.elicitation import (
    ConsoleElicitationHandler,
    ElicitationManager,
    ElicitRequest,
    ElicitResponse,
    ElicitStatus,
    ElicitType,
    URLElicitation,
    create_secure_prompt_request,
)
from govmcp.protocol.sampling import (
    EmbeddedSamplingProvider,
    SamplingCreateMessageRequest,
    SamplingManager,
    SamplingMessage,
    SamplingMessageRole,
    SamplingParameters,
    SamplingResponse,
    create_sampling_request,
)
from govmcp.protocol.tasks import (
    SSEHandler,
    TaskCancelError,
    TaskInfo,
    TaskManager,
    TaskNotFoundError,
    TaskStatus,
    TaskSubscriber,
    create_sse_response,
)


class TestTaskStatus:
    """TaskStatus 枚举测试"""

    def test_task_status_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.WORKING.value == "working"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELED.value == "canceled"

    def test_task_status_count(self):
        assert len(TaskStatus) == 5


class TestTaskInfo:
    """TaskInfo 数据类测试"""

    def test_task_info_creation(self):
        task = TaskInfo(
            id="test_001",
            status=TaskStatus.PENDING,
            tool_name="test_tool",
            arguments={"arg1": "value1"},
        )
        assert task.id == "test_001"
        assert task.status == TaskStatus.PENDING
        assert task.tool_name == "test_tool"
        assert task.arguments == {"arg1": "value1"}
        assert task.progress == 0.0

    def test_task_info_to_dict(self):
        task = TaskInfo(
            id="test_002",
            status=TaskStatus.COMPLETED,
            tool_name="calc",
            arguments={},
            result={"value": 42},
        )
        d = task.to_dict()
        assert d["id"] == "test_002"
        assert d["status"] == "completed"
        assert d["result"]["value"] == 42

    def test_task_info_from_dict(self):
        data = {
            "id": "test_003",
            "status": "failed",
            "toolName": "failing_tool",
            "arguments": {},
            "error": "Something went wrong",
        }
        task = TaskInfo.from_dict(data)
        assert task.id == "test_003"
        assert task.status == TaskStatus.FAILED
        assert task.error == "Something went wrong"


class TestTaskManager:
    """TaskManager 测试"""

    def test_create_task(self):
        manager = TaskManager()
        task_id = manager.create_task("test_tool", {"key": "value"})
        assert task_id.startswith("task_")
        assert len(task_id) > 5

    def test_get_task_status(self):
        manager = TaskManager()
        task_id = manager.create_task("test_tool", {})
        status = manager.get_task_status(task_id)
        assert status == TaskStatus.PENDING

    def test_get_task_info(self):
        manager = TaskManager()
        task_id = manager.create_task("my_tool", {"a": 1})
        info = manager.get_task_info(task_id)
        assert info.id == task_id
        assert info.tool_name == "my_tool"

    def test_get_nonexistent_task(self):
        manager = TaskManager()
        with pytest.raises(TaskNotFoundError):
            manager.get_task_status("nonexistent_id")

    def test_get_task_result_not_completed(self):
        manager = TaskManager()
        task_id = manager.create_task("test_tool", {})
        with pytest.raises(ValueError, match="not completed"):
            manager.get_task_result(task_id)

    def test_cancel_task(self):
        manager = TaskManager()
        task_id = manager.create_task("test_tool", {})
        success = manager.cancel_task(task_id)
        assert success is True
        status = manager.get_task_status(task_id)
        assert status == TaskStatus.CANCELED

    def test_cancel_nonexistent_task(self):
        manager = TaskManager()
        with pytest.raises(TaskNotFoundError):
            manager.cancel_task("nonexistent_id")

    def test_cancel_already_completed(self):
        manager = TaskManager()
        task_id = manager.execute_task_sync("test_tool", {})
        with pytest.raises(TaskCancelError):
            manager.cancel_task(task_id)

    def test_list_tasks(self):
        manager = TaskManager()
        for i in range(5):
            manager.create_task(f"tool_{i}", {})
        tasks = manager.list_tasks()
        assert len(tasks) == 5

    def test_list_tasks_filter_by_status(self):
        manager = TaskManager()
        task_id = manager.create_task("tool_1", {})
        manager.execute_task_sync("tool_2", {})
        pending = manager.list_tasks(status=TaskStatus.PENDING)
        assert len(pending) >= 1

    def test_cleanup_completed_tasks(self):
        manager = TaskManager()
        manager.execute_task_sync("tool", {})
        manager.execute_task_sync("tool", {})
        removed = manager.cleanup_completed_tasks(max_age=0.0)
        assert removed >= 2

    def test_update_progress(self):
        manager = TaskManager()
        task_id = manager.create_task("test_tool", {})
        success = manager.update_progress(task_id, 0.5)
        assert success is True
        info = manager.get_task_info(task_id)
        assert info.progress == 0.5

    def test_update_progress_invalid_task(self):
        manager = TaskManager()
        success = manager.update_progress("nonexistent", 0.5)
        assert success is False

    def test_get_task_stats(self):
        manager = TaskManager()
        manager.create_task("tool_1", {})
        manager.execute_task_sync("tool_2", {})
        stats = manager.get_task_stats()
        assert "total" in stats
        assert "byStatus" in stats


class TestTaskExecution:
    """任务执行测试"""

    def test_sync_task_execution(self):
        manager = TaskManager()
        manager.register_tool("add", lambda a, b: {"sum": a + b})
        task_id = manager.execute_task_sync("add", {"a": 3, "b": 4})
        result = manager.get_task_result(task_id)
        assert result["sum"] == 7

    def test_sync_task_failure(self):
        manager = TaskManager()
        manager.register_tool("fail", lambda: 1 / 0)
        task_id = manager.execute_task_sync("fail", {})
        status = manager.get_task_status(task_id)
        assert status == TaskStatus.FAILED

    def test_sync_task_not_found(self):
        manager = TaskManager()
        task_id = manager.execute_task_sync("nonexistent", {})
        status = manager.get_task_status(task_id)
        assert status == TaskStatus.FAILED


class TestTaskSubscribers:
    """任务订阅者测试"""

    def test_subscribe_specific_task(self):
        manager = TaskManager()
        task_id = manager.create_task("tool", {})
        subscriber = manager.subscribe(task_id=task_id)
        assert subscriber is not None
        assert subscriber.task_ids is not None
        assert task_id in subscriber.task_ids

    def test_subscribe_all_tasks(self):
        manager = TaskManager()
        subscriber = manager.subscribe()
        assert subscriber is not None
        assert subscriber.task_ids is None

    def test_unsubscribe(self):
        manager = TaskManager()
        subscriber = manager.subscribe()
        manager.unsubscribe(subscriber)
        assert subscriber._closed is True


class TestSamplingMessage:
    """采样消息测试"""

    def test_sampling_message_creation(self):
        msg = SamplingMessage(
            role=SamplingMessageRole.USER,
            content="Hello, world!",
        )
        assert msg.role == SamplingMessageRole.USER
        assert msg.content == "Hello, world!"
        assert msg.timestamp is not None

    def test_sampling_message_to_dict(self):
        msg = SamplingMessage(
            role=SamplingMessageRole.ASSISTANT,
            content="Response",
        )
        d = msg.to_dict()
        assert d["role"] == "assistant"
        assert d["content"] == "Response"

    def test_sampling_message_from_dict(self):
        data = {"role": "user", "content": "Test message"}
        msg = SamplingMessage.from_dict(data)
        assert msg.role == SamplingMessageRole.USER
        assert msg.content == "Test message"


class TestSamplingParameters:
    """采样参数测试"""

    def test_default_parameters(self):
        params = SamplingParameters()
        assert params.temperature == 0.7
        assert params.max_tokens == 4096
        assert params.top_p == 0.9

    def test_parameters_to_dict(self):
        params = SamplingParameters(temperature=0.5, max_tokens=2048)
        d = params.to_dict()
        assert d["temperature"] == 0.5
        assert d["maxTokens"] == 2048

    def test_parameters_from_dict(self):
        data = {"temperature": 0.8, "maxTokens": 1024}
        params = SamplingParameters.from_dict(data)
        assert params.temperature == 0.8
        assert params.max_tokens == 1024


class TestSamplingRequest:
    """采样请求测试"""

    def test_create_message_request(self):
        request = SamplingCreateMessageRequest(
            messages=[SamplingMessage(role=SamplingMessageRole.USER, content="Hi")],
            temperature=0.9,
        )
        assert len(request.messages) == 1
        assert request.temperature == 0.9

    def test_create_message_request_from_dict(self):
        data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.5,
        }
        request = SamplingCreateMessageRequest.from_dict(data)
        assert len(request.messages) == 1
        assert request.messages[0].content == "Hello"


class TestSamplingResponse:
    """采样响应测试"""

    def test_response_creation(self):
        response = SamplingResponse(
            content="Generated text",
            model="qwen-turbo",
        )
        assert response.content == "Generated text"
        assert response.done is True

    def test_response_to_dict(self):
        response = SamplingResponse(
            content="Test",
            model="test-model",
            usage={"total_tokens": 100},
        )
        d = response.to_dict()
        assert d["content"] == "Test"
        assert d["usage"]["total_tokens"] == 100


class TestSamplingManager:
    """采样管理器测试"""

    def test_create_message(self):
        manager = SamplingManager()
        request = SamplingCreateMessageRequest(
            messages=[SamplingMessage(role=SamplingMessageRole.USER, content="Say hello")],
        )
        response = manager.create_message(request)
        assert response.content is not None
        assert response.model is not None

    def test_get_message_history(self):
        manager = SamplingManager()
        request = SamplingCreateMessageRequest(
            messages=[SamplingMessage(role=SamplingMessageRole.USER, content="Test")],
        )
        manager.create_message(request)
        history = manager.get_message_history()
        assert len(history) >= 2

    def test_clear_history(self):
        manager = SamplingManager()
        request = SamplingCreateMessageRequest(
            messages=[SamplingMessage(role=SamplingMessageRole.USER, content="Test")],
        )
        manager.create_message(request)
        manager.clear_history()
        assert len(manager.get_message_history()) == 0


class TestEmbeddedSamplingProvider:
    """嵌入式采样提供者测试"""

    def test_sample(self):
        provider = EmbeddedSamplingProvider("test-model")
        messages = [SamplingMessage(role=SamplingMessageRole.USER, content="Hello")]
        params = SamplingParameters()
        response = provider.sample(messages, params)
        assert response.model == "test-model"
        assert response.content is not None

    def test_sample_async(self):
        provider = EmbeddedSamplingProvider("async-model")
        messages = [SamplingMessage(role=SamplingMessageRole.USER, content="Test")]
        params = SamplingParameters()
        response = asyncio.run(provider.sample_async(messages, params))
        assert response.model == "async-model"


class TestElicitRequest:
    """用户交互请求测试"""

    def test_creation(self):
        request = ElicitRequest(
            message="Please confirm",
            requested_schema={"type": "boolean"},
            elicit_type=ElicitType.CONFIRM,
        )
        assert request.message == "Please confirm"
        assert request.elicit_type == ElicitType.CONFIRM
        assert request.id is not None

    def test_to_dict(self):
        request = ElicitRequest(
            message="Test",
            requested_schema={},
        )
        d = request.to_dict()
        assert d["message"] == "Test"
        assert "id" in d


class TestElicitResponse:
    """用户交互响应测试"""

    def test_accepted_response(self):
        response = ElicitResponse(
            request_id="req_001",
            status=ElicitStatus.ACCEPTED,
            value={"confirmed": True},
        )
        assert response.status == ElicitStatus.ACCEPTED
        assert response.value["confirmed"] is True


class TestElicitationManager:
    """交互管理器测试"""

    def test_create_request(self):
        manager = ElicitationManager()
        request = manager.create_request(
            message="Please enter your name",
            requested_schema={"type": "string"},
        )
        assert request.id is not None
        assert manager.get_pending_count() == 1

    def test_accept_request(self):
        manager = ElicitationManager()
        request = manager.create_request(message="Confirm?", requested_schema={})
        success = manager.accept(request.id, {"confirmed": True})
        assert success is True
        assert manager.get_pending_count() == 0

    def test_reject_request(self):
        manager = ElicitationManager()
        request = manager.create_request(message="Confirm?", requested_schema={})
        success = manager.reject(request.id, "User declined")
        assert success is True

    def test_cancel_request(self):
        manager = ElicitationManager()
        request = manager.create_request(message="Confirm?", requested_schema={})
        success = manager.cancel(request.id)
        assert success is True

    def test_get_stats(self):
        manager = ElicitationManager()
        manager.create_request(message="Test 1", requested_schema={})
        manager.create_request(message="Test 2", requested_schema={})
        stats = manager.get_stats()
        assert stats["pending"] == 2


class TestURLElicitation:
    """URL 交互测试"""

    def test_url_elicitation_creation(self):
        url_elicit = URLElicitation(
            url="https://example.com/auth",
            title="Authorization",
            request_id="url_001",
        )
        assert url_elicit.url == "https://example.com/auth"
        assert url_elicit.method == "GET"

    def test_url_elicitation_to_dict(self):
        url_elicit = URLElicitation(
            url="https://example.com",
            title="Test",
            request_id="url_002",
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        d = url_elicit.to_dict()
        assert d["url"] == "https://example.com"
        assert d["method"] == "POST"


class TestAuthorizationManager:
    """授权管理器测试"""

    def test_register_client(self):
        manager = AuthorizationManager()
        client = manager.register_client(
            client_id="app_001",
            client_secret="secret123",
            client_name="Test App",
            redirect_uris=["https://example.com/callback"],
        )
        assert client.client_id == "app_001"
        assert "secret123" in str(client.client_secret)

    def test_validate_client(self):
        manager = AuthorizationManager()
        manager.register_client(
            client_id="app_002",
            client_secret="secret",
        )
        assert manager.validate_client("app_002", "secret") is True
        assert manager.validate_client("app_002", "wrong") is False

    def test_create_authorization_url(self):
        manager = AuthorizationManager()
        manager.register_client(
            client_id="app_003",
            redirect_uris=["https://example.com/cb"],
            allowed_scopes={"read", "write"},
        )
        url = manager.create_authorization_url(
            client_id="app_003",
            redirect_uri="https://example.com/cb",
            scope="read write",
        )
        assert "client_id=app_003" in url
        assert "scope=read+write" in url or "scope=read%20write" in url

    def test_exchange_code(self):
        manager = AuthorizationManager()
        manager.register_client(
            client_id="app_004",
            client_secret="secret",
            redirect_uris=["https://example.com/cb"],
            allowed_scopes={"read"},
        )
        manager.authorize("test_code", "user_001")
        with pytest.raises(ValueError):
            manager.exchange_code("invalid_code", "app_004", "secret")

    def test_validate_token(self):
        manager = AuthorizationManager()
        manager.register_client(
            client_id="app_005",
            client_secret="secret",
            redirect_uris=["https://example.com/cb"],
        )
        token = manager.validate_token("nonexistent_token")
        assert token is None

    def test_check_permission(self):
        manager = AuthorizationManager()
        allowed = manager.check_permission("invalid_token", "resource", "read")
        assert allowed is False


class TestFineGrainedPermissionManager:
    """细粒度权限管理器测试"""

    def test_add_policy(self):
        auth_manager = AuthorizationManager()
        perm_manager = FineGrainedPermissionManager(auth_manager)
        perm_manager.add_policy(
            policy_id="policy_001",
            effect="allow",
            principals=["user_001"],
            resources=["documents:*"],
            actions=["read", "write"],
        )
        policies = perm_manager.get_policies("policy_001")
        assert len(policies["policy_001"]) == 1

    def test_evaluate_permission(self):
        auth_manager = AuthorizationManager()
        perm_manager = FineGrainedPermissionManager(auth_manager)
        perm_manager.add_policy(
            policy_id="policy_002",
            effect="allow",
            principals=["admin"],
            resources=["*"],
            actions=["*"],
        )
        allowed = perm_manager.evaluate("admin", "any_resource", "any_action")
        assert allowed is True

    def test_evaluate_denied(self):
        auth_manager = AuthorizationManager()
        perm_manager = FineGrainedPermissionManager(auth_manager)
        perm_manager.add_policy(
            policy_id="policy_003",
            effect="deny",
            principals=["blocked_user"],
            resources=["secret:*"],
            actions=["*"],
        )
        allowed = perm_manager.evaluate("blocked_user", "secret:file", "read")
        assert allowed is False

    def test_remove_policy(self):
        auth_manager = AuthorizationManager()
        perm_manager = FineGrainedPermissionManager(auth_manager)
        perm_manager.add_policy("policy_004", "allow", [], [], [])
        removed = perm_manager.remove_policy("policy_004")
        assert removed is True


class TestGovMCPServerIntegration:
    """GovMCPServer 集成测试"""

    def test_server_task_endpoints(self):
        from govmcp.protocol.server import GovMCPServer

        server = GovMCPServer("test-server", "1.0.0")

        @server.tool("echo", description="Echo tool")
        def echo(msg: str) -> str:
            return f"Echo: {msg}"

        result = server._dispatch(
            "tasks/create",
            {
                "toolName": "echo",
                "arguments": {"msg": "hello"},
            },
        )
        assert "taskId" in result

        task_id = result["taskId"]
        status = server._dispatch("tasks/status", {"taskId": task_id})
        assert status["taskId"] == task_id

    def test_server_sampling_endpoint(self):
        from govmcp.protocol.server import GovMCPServer

        server = GovMCPServer("test-server", "1.0.0")
        result = server._dispatch(
            "sampling/createMessage",
            {
                "messages": [{"role": "user", "content": "Hello"}],
            },
        )
        assert "content" in result

    def test_server_elicitation_endpoint(self):
        from govmcp.protocol.server import GovMCPServer

        server = GovMCPServer("test-server", "1.0.0")
        result = server._dispatch(
            "elicitation/create",
            {
                "message": "Please confirm",
                "requestedSchema": {"type": "boolean"},
                "type": "confirm",
            },
        )
        assert "id" in result

    def test_server_capabilities(self):
        from govmcp.protocol.server import GovMCPServer

        server = GovMCPServer("test-server", "1.0.0")
        result = server._mcp_initialize({})
        caps = result["capabilities"]
        assert "tasks" in caps
        assert "sampling" in caps
        assert "elicitation" in caps
        assert "authorization" in caps


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
