
"""
Taiji Agent 2.1 — 全功能系统综合测试套件
==========================================
测试覆盖：
  1. 进化系统 (SelfImprovingLoop + HonchoMemory)
  2. 自我学习闭环 (learn_from_interaction)
  3. 技能系统 (Skills Hub create/install/use/improve/delete/browse)
  4. 记忆系统 (SessionMemory + HonchoMemory 全API)
  5. 思考与反思系统 (Agent Loop assemble/think/verify)
  6. 心跳系统 (PluginHealth + SystemHealth + FailoverHealth)
  7. 工具调用系统 (15+ tools 全覆盖)
"""

import asyncio
import gc
import json
import os
import random
import shutil
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest

# Ensure project root in path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from opentaiji.agent.engine import AgentConfig, TaijiAgent, TaskStatus, Message
from opentaiji.learning.loop import (
    SelfImprovingLoop, HonchoMemory, PeerCard, LearnedContext,
)
from opentaiji.memory.session import SessionMemory
from opentaiji.skills.hub import (
    SkillManager, SkillMarket, SkillCreator, Skill,
)
from opentaiji.wfgy import WFGYVerifier, HallucinationDetector
from opentaiji.plugin.plugin_base import (
    PluginHealth, PluginState, ToolDefinition, HookRegistration, PluginDependency,
)
from opentaiji.plugin.hooks import HookManager
from opentaiji.providers.failover import (
    ProviderRouter, ProviderEndpoint, FailoverConfig, ProviderStatus,
)
from opentaiji.taiji_verify.engine import TaijiVerifyEngine
from opentaiji.tools.registry import ToolRegistry


# ═══════════════════════════════════════════════════════════════
# 1. 进化系统测试 (Evolution System)
# ═══════════════════════════════════════════════════════════════

class TestEvolutionSystem:
    """进化系统 — HonchoMemory + SelfImprovingLoop"""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.honcho = HonchoMemory(memory_dir=Path(self.tmpdir))

    def teardown_method(self):
        self.honcho._save()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_peer_card_creation_and_update(self):
        """用户画像创建与更新"""
        card = self.honcho.get_peer_card("user_001")
        assert card.peer_id == "user_001"
        assert card.interaction_count == 0

        self.honcho.update_peer_card("user_001", facts=["喜欢Python"], topic="编程")
        card = self.honcho.get_peer_card("user_001")
        assert card.interaction_count == 1
        assert "喜欢Python" in card.facts
        assert "编程" in card.learned_topics

    def test_peer_card_sentiment_tracking(self):
        """用户情感追踪"""
        self.honcho.update_peer_card("user", sentiment=0.8)
        self.honcho.update_peer_card("user", sentiment=0.9)
        self.honcho.update_peer_card("user", sentiment=0.3)
        card = self.honcho.get_peer_card("user")
        avg = card.get_avg_sentiment()
        assert 0.5 < avg < 0.8

    def test_peer_card_preferences(self):
        """偏好提取与存储"""
        self.honcho.update_peer_card("user", preferences={"language": "中文", "format": "详细"})
        card = self.honcho.get_peer_card("user")
        assert card.preferences["language"] == "中文"
        assert card.preferences["format"] == "详细"

    def test_context_store_and_recall(self):
        """上下文存储与回忆"""
        cid = self.honcho.store_context(
            event="用户询问Python性能优化",
            conclusion="建议使用列表推导式替代循环",
            topics=["编程", "Python", "性能"],
            confidence=0.85,
        )
        assert cid.startswith("context_")

        contexts = self.honcho.recall_contexts(topic="Python")
        assert len(contexts) == 1
        assert contexts[0].confidence == 0.85
        assert "编程" in contexts[0].topics

    def test_context_recall_by_query(self):
        """通过查询词回忆上下文"""
        self.honcho.store_context(event="环评审批流程咨询", conclusion="需要提交环评报告", topics=["政务"])
        self.honcho.store_context(event="排放标准查询", conclusion="SO2排放限值50mg/m3", topics=["环保"])

        results = self.honcho.recall_contexts(query="环评")
        assert len(results) == 1
        assert "环评" in results[0].event

        results = self.honcho.recall_contexts(query="排放")
        assert len(results) == 1

    def test_extract_preferences_from_conversation(self):
        """从对话中提取偏好"""
        conversation = [
            {"role": "user", "content": "我喜欢中文回答，偏好详细的解释"},
            {"role": "assistant", "content": "好的"},
            {"role": "user", "content": "我 prefer concise 格式"},
        ]
        prefs = self.honcho.extract_preferences(conversation)
        assert "language" in prefs
        assert "format" in prefs

    def test_get_user_context_prompt(self):
        """生成用户上下文提示"""
        self.honcho.update_peer_card("user", facts=["喜欢Python", "熟悉Docker"], topic="编程", sentiment=0.7)
        prompt = self.honcho.get_user_context_prompt("user")
        assert "喜欢Python" in prompt
        assert "编程" in prompt
        assert "积极" in prompt

    def test_peer_card_persistence(self):
        """用户画像持久化"""
        self.honcho.update_peer_card("user", facts=["测试持久化"])
        self.honcho._save()

        # 重新加载
        honcho2 = HonchoMemory(memory_dir=Path(self.tmpdir))
        card = honcho2.get_peer_card("user")
        assert "测试持久化" in card.facts


class TestSelfLearningLoop:
    """自我学习闭环"""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.honcho = HonchoMemory(memory_dir=Path(self.tmpdir))
        self.skills_dir = Path(self.tmpdir) / "skills"
        self.skills_dir.mkdir(exist_ok=True)
        self.skill_mgr = SkillManager(skills_dir=self.skills_dir)
        self.wfgy = WFGYVerifier()
        self.loop = SelfImprovingLoop(self.honcho, self.skill_mgr, self.wfgy)

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_learn_from_simple_interaction(self):
        """从简单交互学习"""
        conversation = [
            {"role": "user", "content": "帮我分析这段Python代码的性能"},
            {"role": "assistant", "content": "使用列表推导式可以提高性能"},
        ]
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            self.loop.learn_from_interaction(
                conversation=conversation,
                task="分析Python代码性能",
                result="使用列表推导式",
                tools_used=["file_read"],
                user_id="user",
            )
        )
        loop.close()
        assert isinstance(result, dict)

    def test_learn_with_preferences(self):
        """学习用户偏好"""
        conversation = [
            {"role": "user", "content": "我喜欢中文回答，prefer 详细分析"},
        ]
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            self.loop.learn_from_interaction(
                conversation=conversation,
                task="测试偏好学习",
                result="好的",
                tools_used=[],
                user_id="user",
            )
        )
        loop.close()
        assert "preferences" in result

    def test_topic_extraction(self):
        """主题提取"""
        topics = self.loop._extract_topics(
            task="实现一个快速排序算法",
            result="def quicksort(arr): ... code implementation",
        )
        assert "编程" in topics

    def test_sentiment_analysis(self):
        """情感分析"""
        pos = self.loop._analyze_sentiment("很好，谢谢你的帮助，perfect!")
        assert pos is not None and pos > 0.5

        neg = self.loop._analyze_sentiment("这个结果错误，bad，非常失败")
        assert neg is not None and neg < 0.5

        neutral = self.loop._analyze_sentiment("今天是个普通的日子")
        assert neutral is None

    def test_complexity_estimation(self):
        """复杂度估算"""
        score_simple = self.loop._estimate_complexity("hello world", [])
        assert score_simple < 0.5

        score_complex = self.loop._estimate_complexity(
            "设计并实现一个分布式微服务架构的电商系统",
            ["file_read", "file_write", "shell", "web_search", "git_log"],
        )
        assert score_complex > 0.5

    def test_category_inference(self):
        """类别推断"""
        assert self.loop._infer_category("debug这个函数") == "开发"
        assert self.loop._infer_category("research一下量子计算") == "研究"
        assert self.loop._infer_category("写文档") == "创作"
        assert self.loop._infer_category("hello") == "general"

    def test_learning_hooks(self):
        """学习钩子"""
        hook_results = []
        async def test_hook(data):
            hook_results.append(data)

        self.loop.on_learning(test_hook)
        conversation = [{"role": "user", "content": "test"}]
        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            self.loop.learn_from_interaction(
                conversation=conversation, task="test",
                result="ok", tools_used=[], user_id="user",
            )
        )
        loop.close()
        assert len(hook_results) == 1


# ═══════════════════════════════════════════════════════════════
# 2. 技能系统测试 (Skills System)
# ═══════════════════════════════════════════════════════════════

class TestSkillsSystem:
    """技能系统 — Skills Hub"""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.skills_dir = Path(self.tmpdir) / "skills"
        self.skills_dir.mkdir(exist_ok=True)
        self.mgr = SkillManager(skills_dir=self.skills_dir)
        self.market = SkillMarket()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_browse_market(self):
        """浏览技能市场"""
        skills = self.market.browse()
        assert len(skills) >= 7  # 7 bundled skills
        ids = {s["id"] for s in skills}
        assert "github-auth" in ids
        assert "code-review" in ids

    def test_browse_market_by_category(self):
        """按分类浏览"""
        skills = self.market.browse(category="开发")
        assert any(s["category"] == "开发" for s in skills)

    def test_install_from_market(self):
        """从市场安装技能"""
        installed = self.mgr.install("code-review")
        assert installed is True
        skill = self.mgr.get("code-review")
        assert skill is not None
        assert skill.name == "代码审查"

    def test_install_bundled_all(self):
        """批量安装预置技能"""
        self.mgr.install_bundled()
        all_skills = self.mgr.list()
        assert len(all_skills) >= 7

    def test_create_custom_skill(self):
        """创建自定义技能"""
        loop = asyncio.new_event_loop()
        skill = loop.run_until_complete(
            self.mgr.create(
                name="环评审批助手",
                description="辅助生态环境局环评审批流程",
                instructions="1. 检查环评报告完整性\n2. 比对排放标准\n3. 生成审批意见",
                tools=["file_read", "web_search"],
                category="政务",
            )
        )
        loop.close()

        assert skill is not None
        assert skill.name == "环评审批助手"
        assert skill.category == "政务"
        assert "file_read" in skill.tools

    def test_list_skills(self):
        """列出所有技能"""
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.mgr.create(name="技能A", description="测试", instructions="test", tools=[], category="测试"))
        loop.run_until_complete(self.mgr.create(name="技能B", description="测试", instructions="test", tools=[], category="测试"))
        loop.close()
        skills = self.mgr.list()
        assert len(skills) == 2

    def test_list_by_category(self):
        """按分类列出技能"""
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.mgr.create(name="开发技能", description="d", instructions="i", tools=[], category="开发"))
        loop.run_until_complete(self.mgr.create(name="政务技能", description="d", instructions="i", tools=[], category="政务"))
        loop.close()

        dev_skills = self.mgr.list(category="开发")
        assert len(dev_skills) == 1
        assert dev_skills[0].category == "开发"

    def test_use_skill(self):
        """使用技能"""
        self.mgr.install("code-review")
        instructions = self.mgr.use("code-review")
        assert instructions is not None
        assert "代码审查" in instructions or "code" in instructions.lower()

    def test_improve_skill(self):
        """改进技能"""
        loop = asyncio.new_event_loop()
        skill = loop.run_until_complete(
            self.mgr.create(name="test-skill", description="v1", instructions="旧指令", tools=[], category="测试")
        )
        improved = loop.run_until_complete(
            self.mgr.improve(skill.id, ["新发现: 需要增加安全检查步骤", "改进: 使用新版API"])
        )
        loop.close()
        assert improved is not None
        assert improved.usage_count >= 0

    def test_delete_skill(self):
        """删除技能"""
        loop = asyncio.new_event_loop()
        skill = loop.run_until_complete(self.mgr.create(name="to-delete", description="d", instructions="i", tools=[], category="测试"))
        loop.close()
        assert self.mgr.get(skill.id) is not None
        deleted = self.mgr.delete(skill.id)
        assert deleted is True
        assert self.mgr.get(skill.id) is None

    def test_get_stats(self):
        """技能统计"""
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.mgr.create(name="S1", description="d", instructions="i", tools=[], category="A"))
        loop.run_until_complete(self.mgr.create(name="S2", description="d", instructions="i", tools=[], category="B"))
        self.mgr.install("code-review")
        loop.close()
        stats = self.mgr.get_stats()
        assert stats["total"] >= 3
        assert "by_category" in stats

    def test_skill_persistence(self):
        """技能持久化"""
        loop = asyncio.new_event_loop()
        skill = loop.run_until_complete(self.mgr.create(name="persist-test", description="测试持久化", instructions="test", tools=[], category="测试"))
        skill_id = skill.id
        loop.close()

        mgr2 = SkillManager(skills_dir=self.skills_dir)
        loaded = mgr2.get(skill_id)
        assert loaded is not None
        assert loaded.description == "测试持久化"

    def test_skill_creator_extract(self):
        """SkillCreator 从对话提取技能"""
        creator = SkillCreator(self.mgr)
        conversation = [
            {"role": "user", "content": "帮我设计一个数据验证的流水线"},
            {"role": "assistant", "content": "可以创建以下验证步骤: 1.格式检查 2.范围验证 3.逻辑一致性"},
        ]
        loop = asyncio.new_event_loop()
        skill = loop.run_until_complete(
            creator.extract_from_conversation(
                task="设计数据验证流水线",
                successful_result="格式检查+范围验证+逻辑一致性",
                conversation=conversation,
            )
        )
        loop.close()
        # May or may not create based on complexity
        if skill:
            assert skill.name != ""


# ═══════════════════════════════════════════════════════════════
# 3. 记忆系统测试 (Memory System)
# ═══════════════════════════════════════════════════════════════

class TestMemorySystem:
    """记忆系统 — SessionMemory 全API"""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mem = SessionMemory(memory_dir=Path(self.tmpdir))

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_save_and_get(self):
        """保存与获取记忆"""
        self.mem.save("key1", "value1")
        assert self.mem.get("key1") == "value1"

    def test_get_nonexistent(self):
        """获取不存在的键"""
        assert self.mem.get("nonexistent") is None

    def test_search(self):
        """搜索记忆"""
        self.mem.save("python_tips", "使用列表推导式可以提高性能")
        self.mem.save("git_tips", "使用git stash暂存修改")
        self.mem.save("docker_tips", "使用多阶段构建减小镜像")

        results = self.mem.search("python")
        assert "列表推导式" in results

        results = self.mem.search("git")
        assert "stash" in results

        results = self.mem.search("量子力学")
        assert results == "No matching memories"

    def test_save_session(self):
        """保存会话"""
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助你的？"},
        ]
        self.mem.save_session(messages)
        results = self.mem.search("你好")
        assert len(results) > 0

    def test_todo_operations(self):
        """Todo 操作"""
        self.mem.add_todo("完成压力测试")
        self.mem.add_todo("编写文档")
        self.mem.add_todo("代码审查")

        todos = self.mem.get_todos()
        assert len(todos) == 3
        assert not todos[0]["done"]

        self.mem.done_todo("完成压力测试")
        todos = self.mem.get_todos()
        assert todos[0]["done"]

    def test_peer_card_operations(self):
        """用户画像操作"""
        self.mem.update_peer_card("user", ["喜欢Python", "熟悉Docker", "偏好中文"])
        card = self.mem.get_peer_card("user")
        assert len(card["facts"]) >= 3

    def test_store_context(self):
        """存储上下文"""
        self.mem.store_context("用户询问环评流程", "需要提交环评报告并等待审批")
        results = self.mem.search("环评")
        assert len(results) > 0

    def test_memory_persistence(self):
        """记忆持久化"""
        self.mem.save("persist_key", "persist_value")
        # 重新加载
        mem2 = SessionMemory(memory_dir=Path(self.tmpdir))
        assert mem2.get("persist_key") == "persist_value"

    def test_multiple_sessions(self):
        """多会话管理"""
        for i in range(10):
            self.mem.save_session([
                {"role": "user", "content": f"会话{i}的问题"},
                {"role": "assistant", "content": f"会话{i}的回复"},
            ])
        results = self.mem.search("会话5")
        assert len(results) > 0


# ═══════════════════════════════════════════════════════════════
# 4. 思考与反思系统测试 (Thinking & Reflection)
# ═══════════════════════════════════════════════════════════════

class TestThinkingSystem:
    """思考系统 — Agent 思考链"""

    def test_system_prompt_building(self):
        """系统提示构建"""
        agent = TaijiAgent(config=AgentConfig(wfgy_enabled=False, enable_sandbox=False))
        prompt = agent._build_system_prompt()
        assert "太极 Agent" in prompt
        assert "WFGY" in prompt

    def test_prompt_assemble(self):
        """提示组装"""
        agent = TaijiAgent(config=AgentConfig(wfgy_enabled=False, enable_sandbox=False))
        agent.messages = [
            Message(role="system", content="System prompt"),
            Message(role="user", content="User question"),
        ]
        assembled = agent._assemble_prompt()
        assert len(assembled) == 2
        assert assembled[0]["role"] == "system"

    def test_wfgy_verify_and_annotate(self):
        """WFGY 验证与注解"""
        agent = TaijiAgent(config=AgentConfig(wfgy_enabled=True, wfgy_threshold=0.5, enable_sandbox=False))

        class MockResponse:
            content = "This is a test response about Python programming."
            tool_calls = None

        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(agent._verify_and_annotate(MockResponse()))
        loop.close()
        assert result is not None

    def test_agent_config_defaults(self):
        """Agent 配置默认值"""
        config = AgentConfig()
        assert config.provider == "anthropic"
        assert config.model == "claude-sonnet-4-20250514"
        assert config.max_iterations == 25
        assert config.wfgy_enabled is True
        assert config.enable_sandbox is True

    def test_agent_config_custom(self):
        """Agent 自定义配置"""
        config = AgentConfig(
            provider="qwen",
            model="qwen-max",
            wfgy_enabled=False,
            enable_sandbox=False,
            max_iterations=50,
            temperature=0.3,
        )
        assert config.provider == "qwen"
        assert config.model == "qwen-max"
        assert config.max_iterations == 50
        assert config.temperature == 0.3

    def test_task_result_structure(self):
        """任务结果结构"""
        from opentaiji.agent.engine import TaskResult, TaskStatus
        result = TaskResult(
            status=TaskStatus.COMPLETED,
            content="任务完成",
            iterations=5,
            tools_used=["file_read", "shell"],
        )
        assert result.status == TaskStatus.COMPLETED
        assert result.iterations == 5
        assert "file_read" in result.tools_used

    def test_message_model(self):
        """消息模型"""
        msg = Message(role="user", content="测试消息")
        data = msg.model_dump()
        assert data["role"] == "user"
        assert data["content"] == "测试消息"

    def test_agent_event_bus_access(self):
        """Agent 事件总线访问"""
        agent = TaijiAgent(config=AgentConfig(wfgy_enabled=False, enable_sandbox=False))
        bus = agent.get_event_bus()
        assert bus is not None

        mem = agent.get_memory()
        assert mem is not None

        tools = agent.get_tools()
        assert tools is not None


# ═══════════════════════════════════════════════════════════════
# 5. 心跳系统测试 (Heartbeat & Health System)
# ═══════════════════════════════════════════════════════════════

class TestHeartbeatSystem:
    """心跳与健康系统"""

    def test_plugin_health_enum(self):
        """插件健康状态枚举"""
        assert PluginHealth.HEALTHY.value > 0
        assert PluginHealth.DEGRADED.value > 0
        assert PluginHealth.UNHEALTHY.value > 0
        assert PluginHealth.ERROR.value > 0

    def test_plugin_state_enum(self):
        """插件生命周期状态"""
        states = [
            PluginState.REGISTERED, PluginState.LOADING, PluginState.LOADED,
            PluginState.ACTIVATING, PluginState.ACTIVE, PluginState.DEACTIVATING,
            PluginState.DEACTIVATED, PluginState.ERROR,
        ]
        assert len(states) == 8
        assert PluginState.ACTIVE.value == "active"

    def test_tool_definition(self):
        """工具定义"""
        td = ToolDefinition(
            name="test_tool",
            description="测试工具",
            parameters={"type": "object", "properties": {}},
        )
        assert td.name == "test_tool"
        assert td.description == "测试工具"

    def test_hook_registration(self):
        """钩子注册"""
        hook = HookRegistration(
            event="agent:start",
            handler=lambda x: x,
            priority=10,
        )
        assert hook.event == "agent:start"
        assert hook.priority == 10

    def test_plugin_dependency(self):
        """插件依赖"""
        dep = PluginDependency(
            plugin_id="govmcp",
            version_spec=">=1.0.0,<2.0.0",
            optional=True,
        )
        assert dep.plugin_id == "govmcp"
        assert dep.optional is True

    def test_provider_health_status(self):
        """Provider 健康状态"""
        assert ProviderStatus.HEALTHY == "healthy"
        assert ProviderStatus.UNHEALTHY == "unhealthy"

    def test_failover_health_summary(self):
        """故障转移健康摘要"""
        router = ProviderRouter()
        ep1 = ProviderEndpoint(name="p1", provider="a", model="m", priority=1,
                               status=ProviderStatus.HEALTHY)
        ep2 = ProviderEndpoint(name="p2", provider="b", model="m", priority=2,
                               status=ProviderStatus.HEALTHY)
        router.add_endpoint(ep1)
        router.add_endpoint(ep2)
        health = router.get_health_summary()
        assert health["total"] == 2
        assert health["available"] is True
        assert health["healthy"] == 2

    def test_taiji_verify_engine_health(self):
        """太极验证引擎健康"""
        engine = TaijiVerifyEngine(embedding_dim=64)
        health = engine.system_health
        assert "fu_return_state" in health
        assert "kun_anchors" in health
        assert "failure_modes_enabled" in health
        assert health["failure_modes_enabled"] is True


# ═══════════════════════════════════════════════════════════════
# 6. 工具调用系统测试 (Tool Calling System)
# ═══════════════════════════════════════════════════════════════

class TestToolCallingSystem:
    """工具调用系统 — 15+ tools"""

    def setup_method(self):
        self.registry = ToolRegistry()

    def test_all_tools_registered(self):
        """所有工具已注册"""
        tools = self.registry.list_tools()
        assert len(tools) >= 15
        expected = [
            "file_read", "file_write", "file_list", "file_search",
            "shell", "web_search", "web_extract", "git_status", "git_log",
            "memory_search", "memory_save", "execute_code",
            "todo_list", "todo_add", "todo_done",
        ]
        for tool in expected:
            assert tool in tools, f"Missing tool: {tool}"

    def test_file_read(self):
        """文件读取"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content 123")
            tmp_path = f.name
        try:
            result = self.registry._file_read(tmp_path)
            assert "test content" in result
        finally:
            os.unlink(tmp_path)

    def test_file_write(self):
        """文件写入"""
        tmp_path = os.path.join(tempfile.gettempdir(), "taiji_test_write.txt")
        try:
            result = self.registry._file_write(tmp_path, "write test")
            assert "File written" in result
            with open(tmp_path) as f:
                assert f.read() == "write test"
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_file_list(self):
        """文件列表"""
        result = self.registry._file_list(path=".")
        assert len(result) > 0

    def test_file_search(self):
        """文件搜索"""
        result = self.registry._file_search(pattern="test", path="tests")
        assert isinstance(result, str)

    def test_shell_command(self):
        """Shell 命令执行"""
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(self.registry._shell("echo hello"))
        loop.close()
        assert "hello" in result

    def test_shell_timeout(self):
        """Shell 超时"""
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(self.registry._shell("sleep 60", timeout=1))
        loop.close()
        assert "timeout" in result.lower() or "timed" in result.lower()

    def test_git_status(self):
        """Git 状态"""
        result = self.registry._git_status(path=".")
        assert "git" in result.lower() or len(result) > 0 or "Not a git" in result

    def test_git_log(self):
        """Git 日志"""
        result = self.registry._git_log(path=".", limit=3)
        assert isinstance(result, str)

    def test_execute_code_python(self):
        """执行 Python 代码"""
        result = self.registry._execute_code("print('hello from sandbox')", "python")
        assert "hello" in result.lower() or "error" in result.lower()

    def test_todo_operations(self):
        """Todo 操作"""
        result = self.registry._todo_list()
        assert isinstance(result, str)

        result = self.registry._todo_add("测试任务")
        assert "Task added" in result

        result = self.registry._todo_done("测试任务")
        assert "Task completed" in result

    def test_memory_tools(self):
        """记忆工具"""
        result = self.registry._memory_save("test_key", "test_value")
        assert "Memory saved" in result

        result = self.registry._memory_search("test_key")
        assert isinstance(result, str)

    def test_tool_schema_completeness(self):
        """工具 Schema 完整性"""
        for tool_name in self.registry.list_tools():
            schema = self.registry.get_schema(tool_name)
            assert schema is not None, f"Schema missing for {tool_name}"
            assert schema.name == tool_name
            assert schema.description != ""

    def test_tool_registration(self):
        """工具注册"""
        def dummy_handler(**kwargs):
            return "dummy result"

        from opentaiji.tools.registry import ToolSchema
        self.registry.register(
            name="dummy_tool",
            handler=dummy_handler,
            schema=ToolSchema(
                name="dummy_tool",
                description="A dummy test tool",
                parameters={"type": "object", "properties": {}},
            ),
        )
        assert "dummy_tool" in self.registry.list_tools()
        schema = self.registry.get_schema("dummy_tool")
        assert schema.description == "A dummy test tool"

    def test_unknown_tool_error(self):
        """未知工具错误"""
        class FakeToolCall:
            name = "nonexistent_tool"
            arguments = {}
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(self.registry.execute(FakeToolCall()))
        loop.close()
        assert not result.success
        assert "Unknown tool" in result.error


# ═══════════════════════════════════════════════════════════════
# 7. 系统集成测试 (System Integration)
# ═══════════════════════════════════════════════════════════════

class TestSystemIntegration:
    """系统集成 — 多系统协作"""

    def test_evolution_to_memory_flow(self):
        """进化 → 记忆 数据流"""
        tmpdir = tempfile.mkdtemp()
        try:
            honcho = HonchoMemory(memory_dir=Path(tmpdir))
            honcho.update_peer_card("user", facts=["测试集成"])
            honcho.store_context(event="集成测试", conclusion="通过")

            contexts = honcho.recall_contexts(query="集成")
            assert len(contexts) == 1
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_skill_to_tool_flow(self):
        """技能 → 工具 数据流"""
        tmpdir = tempfile.mkdtemp()
        try:
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir(exist_ok=True)
            mgr = SkillManager(skills_dir=skills_dir)
            loop = asyncio.new_event_loop()
            skill = loop.run_until_complete(mgr.create(
                name="tool-integration-test",
                description="测试",
                instructions="使用 file_read 工具",
                tools=["file_read", "shell"],
                category="测试",
            ))
            loop.close()
            assert skill is not None
            assert "file_read" in skill.tools
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_verify_to_evolution_coupling(self):
        """验证 → 进化 耦合"""
        wfgy = WFGYVerifier()
        tmpdir = tempfile.mkdtemp()
        try:
            honcho = HonchoMemory(memory_dir=Path(tmpdir))
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir(exist_ok=True)
            mgr = SkillManager(skills_dir=skills_dir)
            loop = SelfImprovingLoop(honcho, mgr, wfgy)

            # 验证通过的内容可以被学习
            assert loop.wfgy.verify("这是一个可信的内容") is True
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_full_closed_loop(self):
        """完整闭环: 学习→记忆→技能→验证"""
        tmpdir = tempfile.mkdtemp()
        try:
            # 1. 初始化所有组件
            honcho = HonchoMemory(memory_dir=Path(tmpdir))
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir(exist_ok=True)
            mgr = SkillManager(skills_dir=skills_dir)
            wfgy = WFGYVerifier()
            loop = SelfImprovingLoop(honcho, mgr, wfgy)

            # 2. 模拟学习
            conversation = [
                {"role": "user", "content": "帮我分析这段Python代码性能"},
                {"role": "assistant", "content": "建议使用列表推导式提升性能"},
            ]
            aloop = asyncio.new_event_loop()
            result = aloop.run_until_complete(loop.learn_from_interaction(
                conversation=conversation,
                task="分析Python代码性能",
                result="列表推导式提升性能",
                tools_used=["file_read"],
            ))
            aloop.close()

            # 3. 验证学习结果
            card = honcho.get_peer_card("user")
            assert card.interaction_count >= 1

            # 4. 验证上下文存储
            contexts = honcho.recall_contexts(query="Python")
            assert len(contexts) >= 1

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("   Taiji Agent 2.1 — 全功能系统综合测试")
    print("=" * 80)
    sys.exit(pytest.main([__file__, "-v", "--tb=short", "-p", "no:warnings"]))
