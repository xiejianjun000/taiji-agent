"""
Hermes Agent 核心引擎

实现：
- 跨会话记忆管理
- 三层进化机制（个体→部门→系统）
- 子 Agent 编排
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np

logger = logging.getLogger(__name__)


class EvolutionLevel(str, Enum):
    """进化层级"""
    INDIVIDUAL = "individual"     # 个体进化
    DEPARTMENT = "department"     # 部门进化
    SYSTEM = "system"            # 系统进化


@dataclass
class MemoryEntry:
    """记忆条目"""
    entry_id: str
    user_id: str
    session_id: str
    content: str
    embedding: np.ndarray | None = None
    timestamp: float = field(default_factory=time.time)
    memory_type: str = "interaction"
    importance: float = 0.5
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class EvolutionRecord:
    """进化记录"""
    record_id: str
    evolution_level: EvolutionLevel
    trigger: str
    feedback: str
    changes: list[str]
    timestamp: float = field(default_factory=time.time)
    success: bool = True
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentSkill:
    """Agent 技能"""
    skill_id: str
    name: str
    description: str
    confidence: float = 1.0
    usage_count: int = 0
    last_used: float = 0.0
    evolved_from: str | None = None


@dataclass
class SubAgent:
    """子 Agent 定义"""
    agent_id: str
    name: str
    role: str
    description: str
    skills: list[AgentSkill] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    priority: int = 0
    active: bool = True


class CrossSessionMemory:
    """
    跨会话记忆系统

    功能：
    - 持久化记忆存储
    - 向量检索
    - 上下文管理
    - 记忆重要性评分
    """

    def __init__(
        self,
        max_entries: int = 10000,
        similarity_threshold: float = 0.7,
        embedding_dim: int = 768,
    ):
        self.max_entries = max_entries
        self.similarity_threshold = similarity_threshold
        self.embedding_dim = embedding_dim

        self._memory_store: dict[str, MemoryEntry] = {}
        self._user_memories: dict[str, list[str]] = {}
        self._session_memories: dict[str, list[str]] = {}
        self._embeddings: dict[str, np.ndarray] = {}

    async def add(
        self,
        user_id: str,
        session_id: str,
        content: str,
        memory_type: str = "interaction",
        importance: float = 0.5,
        tags: list[str] | None = None,
        embedding: np.ndarray | None = None,
        metadata: dict | None = None,
    ) -> str:
        """添加记忆"""
        entry_id = str(uuid.uuid4())

        entry = MemoryEntry(
            entry_id=entry_id,
            user_id=user_id,
            session_id=session_id,
            content=content,
            embedding=embedding,
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
        )

        self._memory_store[entry_id] = entry

        if user_id not in self._user_memories:
            self._user_memories[user_id] = []
        self._user_memories[user_id].append(entry_id)

        if session_id not in self._session_memories:
            self._session_memories[session_id] = []
        self._session_memories[session_id].append(entry_id)

        if embedding is not None:
            self._embeddings[entry_id] = embedding

        await self._cleanup_old_entries()

        return entry_id

    async def get(self, entry_id: str) -> MemoryEntry | None:
        """获取记忆"""
        return self._memory_store.get(entry_id)

    async def search(
        self,
        query: str,
        user_id: str | None = None,
        limit: int = 10,
        memory_type: str | None = None,
    ) -> list[MemoryEntry]:
        """搜索记忆"""
        results = []

        entries = self._get_entries_by_user(user_id) if user_id else self._memory_store.values()

        for entry in entries:
            if memory_type and entry.memory_type != memory_type:
                continue

            if query.lower() in entry.content.lower():
                results.append(entry)

        results.sort(key=lambda e: (e.importance, e.timestamp), reverse=True)
        return results[:limit]

    async def get_recent(
        self,
        user_id: str | None = None,
        session_id: str | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """获取最近记忆"""
        if session_id:
            entry_ids = self._session_memories.get(session_id, [])
            entries = [self._memory_store[eid] for eid in entry_ids if eid in self._memory_store]
        elif user_id:
            entry_ids = self._user_memories.get(user_id, [])
            entries = [self._memory_store[eid] for eid in entry_ids if eid in self._memory_store]
        else:
            entries = list(self._memory_store.values())

        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]

    async def get_context(
        self,
        user_id: str,
        session_id: str,
        current_query: str | None = None,
        window_size: int = 5,
    ) -> list[MemoryEntry]:
        """获取上下文记忆"""
        recent = await self.get_recent(user_id=user_id, session_id=session_id, limit=window_size)

        if current_query:
            similar = await self.search(query=current_query, user_id=user_id, limit=3)
            for entry in similar:
                if entry not in recent:
                    recent.append(entry)

        return recent

    async def delete(self, entry_id: str) -> bool:
        """删除记忆"""
        if entry_id not in self._memory_store:
            return False

        entry = self._memory_store[entry_id]

        if entry.user_id in self._user_memories:
            self._user_memories[entry.user_id].remove(entry_id)

        if entry.session_id in self._session_memories:
            self._session_memories[entry.session_id].remove(entry_id)

        self._embeddings.pop(entry_id, None)
        del self._memory_store[entry_id]

        return True

    async def update_importance(self, entry_id: str, importance: float):
        """更新重要性"""
        if entry_id in self._memory_store:
            self._memory_store[entry_id].importance = importance

    def _get_entries_by_user(self, user_id: str | None) -> list[MemoryEntry]:
        """获取用户的所有记忆"""
        if not user_id:
            return list(self._memory_store.values())

        entry_ids = self._user_memories.get(user_id, [])
        return [self._memory_store[eid] for eid in entry_ids if eid in self._memory_store]

    async def _cleanup_old_entries(self):
        """清理旧记忆"""
        if len(self._memory_store) <= self.max_entries:
            return

        entries = list(self._memory_store.values())
        entries.sort(key=lambda e: (e.importance, e.timestamp))

        to_remove = len(self._memory_store) - self.max_entries
        for entry in entries[:to_remove]:
            await self.delete(entry.entry_id)

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "total_entries": len(self._memory_store),
            "user_count": len(self._user_memories),
            "session_count": len(self._session_memories),
        }


class EvolutionEngine:
    """
    三层进化引擎

    进化层级：
    1. INDIVIDUAL - 个体进化：基于用户个人反馈优化
    2. DEPARTMENT - 部门进化：同部门内共享优化
    3. SYSTEM - 系统进化：全局共享优化
    """

    def __init__(self, memory: CrossSessionMemory):
        self.memory = memory
        self._evolution_records: list[EvolutionRecord] = []
        self._user_evolution: dict[str, dict] = {}
        self._department_evolution: dict[str, dict] = {}
        self._system_evolution: dict = {}

        self._thresholds = {
            "individual": {"feedback_count": 5, "success_rate": 0.7},
            "department": {"feedback_count": 20, "success_rate": 0.8},
            "system": {"feedback_count": 100, "success_rate": 0.85},
        }

    async def record_feedback(
        self,
        user_id: str,
        department_id: str,
        interaction_id: str,
        feedback_type: str,
        content: str,
    ):
        """记录反馈"""
        if user_id not in self._user_evolution:
            self._user_evolution[user_id] = {
                "feedbacks": [],
                "success_count": 0,
                "total_count": 0,
            }

        self._user_evolution[user_id]["feedbacks"].append({
            "type": feedback_type,
            "content": content,
            "timestamp": time.time(),
            "interaction_id": interaction_id,
        })
        self._user_evolution[user_id]["total_count"] += 1

        if feedback_type == "positive":
            self._user_evolution[user_id]["success_count"] += 1

        await self._check_individual_evolution(user_id)
        await self._check_department_evolution(department_id)

    async def _check_individual_evolution(self, user_id: str):
        """检查个体进化"""
        if user_id not in self._user_evolution:
            return

        data = self._user_evolution[user_id]
        threshold = self._thresholds["individual"]

        if data["total_count"] >= threshold["feedback_count"]:
            success_rate = data["success_count"] / data["total_count"]
            if success_rate >= threshold["success_rate"]:
                await self._trigger_evolution(user_id, EvolutionLevel.INDIVIDUAL)

    async def _check_department_evolution(self, department_id: str):
        """检查部门进化"""
        if department_id not in self._department_evolution:
            self._department_evolution[department_id] = {
                "feedbacks": [],
                "success_count": 0,
                "total_count": 0,
            }

        data = self._department_evolution[department_id]
        threshold = self._thresholds["department"]

        if data["total_count"] >= threshold["feedback_count"]:
            success_rate = data["success_count"] / data["total_count"]
            if success_rate >= threshold["success_rate"]:
                await self._trigger_evolution(department_id, EvolutionLevel.DEPARTMENT)

    async def _trigger_evolution(
        self,
        entity_id: str,
        level: EvolutionLevel,
    ):
        """触发进化"""
        record = EvolutionRecord(
            record_id=str(uuid.uuid4()),
            evolution_level=level,
            trigger=f"Auto-triggered for {entity_id}",
            feedback="Success rate threshold met",
            changes=["Updated response patterns", "Optimized skill weights"],
        )

        self._evolution_records.append(record)

        logger.info(f"Evolution triggered: {level.value} for {entity_id}")

    async def get_evolution(self, entity_id: str) -> dict | None:
        """获取进化状态"""
        if entity_id in self._user_evolution:
            return {
                "level": EvolutionLevel.INDIVIDUAL.value,
                "data": self._user_evolution[entity_id],
            }
        if entity_id in self._department_evolution:
            return {
                "level": EvolutionLevel.DEPARTMENT.value,
                "data": self._department_evolution[entity_id],
            }
        return None

    def get_history(self, limit: int = 10) -> list[EvolutionRecord]:
        """获取进化历史"""
        return sorted(
            self._evolution_records,
            key=lambda r: r.timestamp,
            reverse=True,
        )[:limit]


class SubAgentOrchestrator:
    """
    子 Agent 编排器

    管理十三神智能体等子 Agent 的调度和协作
    """

    BUNDLED_AGENTS = {
        "zhangjie": {
            "name": "仓颉",
            "role": "环评审批",
            "description": "负责环境影响评价审批相关任务",
            "skills": ["document_analysis", "policy_check", "approval_workflow"],
            "priority": 1,
        },
        "zhurong": {
            "name": "祝融",
            "role": "消防预警",
            "description": "负责消防安全检查和预警任务",
            "skills": ["safety_inspection", "risk_assessment", "alert_generation"],
            "priority": 1,
        },
        "shennong": {
            "name": "神农",
            "role": "污染监测",
            "description": "负责环境污染监测和数据分析",
            "skills": ["data_collection", "pollution_analysis", "report_generation"],
            "priority": 1,
        },
        "fuxi": {
            "name": "伏羲",
            "role": "数据分析",
            "description": "负责数据分析和模型构建",
            "skills": ["statistics", "machine_learning", "visualization"],
            "priority": 2,
        },
        "yu": {
            "name": "禹",
            "role": "水利工程",
            "description": "负责水利工程相关咨询",
            "skills": ["engineering_consult", "project_planning", "resource_allocation"],
            "priority": 2,
        },
    }

    def __init__(self):
        self._agents: dict[str, SubAgent] = {}
        self._load_bundled_agents()
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._running_tasks: dict[str, asyncio.Task] = {}

    def _load_bundled_agents(self):
        """加载内置 Agent"""
        for agent_id, config in self.BUNDLED_AGENTS.items():
            skills = [
                AgentSkill(
                    skill_id=skill_id,
                    name=skill_id.replace("_", " ").title(),
                    description=f"Skill for {skill_id}",
                )
                for skill_id in config.get("skills", [])
            ]

            self._agents[agent_id] = SubAgent(
                agent_id=agent_id,
                name=config["name"],
                role=config["role"],
                description=config["description"],
                skills=skills,
                capabilities=config.get("skills", []),
                priority=config.get("priority", 0),
                active=True,
            )

    def get_agent(self, agent_id: str) -> SubAgent | None:
        """获取 Agent"""
        return self._agents.get(agent_id)

    def list_agents(
        self,
        role: str | None = None,
        active_only: bool = True,
    ) -> list[SubAgent]:
        """列出 Agent"""
        agents = list(self._agents.values())

        if active_only:
            agents = [a for a in agents if a.active]

        if role:
            agents = [a for a in agents if a.role == role]

        return sorted(agents, key=lambda a: a.priority)

    def find_agent_by_capability(self, capability: str) -> list[SubAgent]:
        """根据能力查找 Agent"""
        return [
            agent for agent in self._agents.values()
            if capability in agent.capabilities and agent.active
        ]

    async def dispatch_task(
        self,
        agent_id: str,
        task: dict,
        callback: Callable | None = None,
    ) -> str:
        """分发任务"""
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        task_id = str(uuid.uuid4())

        task_obj = {
            "task_id": task_id,
            "agent_id": agent_id,
            "task": task,
            "callback": callback,
            "status": "pending",
        }

        await self._task_queue.put(task_obj)

        asyncio.create_task(self._process_task(task_obj))

        return task_id

    async def _process_task(self, task: dict):
        """处理任务"""
        task_id = task["task_id"]

        try:
            self._running_tasks[task_id] = asyncio.current_task()
            task["status"] = "running"

            await asyncio.sleep(0.1)

            task["status"] = "completed"
            task["result"] = {"success": True, "agent": task["agent_id"]}

            if task["callback"]:
                await task["callback"](task["result"])

        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)

        finally:
            self._running_tasks.pop(task_id, None)

    def get_task_status(self, task_id: str) -> str | None:
        """获取任务状态"""
        for task in self._running_tasks.values():
            if task.get("task_id") == task_id:
                return task.get("status")
        return None


class HermesAgentEngine:
    """
    Hermes Agent 核心引擎

    整合：
    - 跨会话记忆
    - 三层进化
    - 子 Agent 编排
    """

    def __init__(self):
        self.memory = CrossSessionMemory()
        self.evolution = EvolutionEngine(self.memory)
        self.orchestrator = SubAgentOrchestrator()

        self._active_sessions: dict[str, dict] = {}

    async def create_session(
        self,
        user_id: str,
        tenant_id: str,
        session_config: dict | None = None,
    ) -> str:
        """创建会话"""
        session_id = str(uuid.uuid4())

        self._active_sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "created_at": time.time(),
            "config": session_config or {},
            "context": [],
        }

        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        """获取会话"""
        return self._active_sessions.get(session_id)

    async def add_to_context(
        self,
        session_id: str,
        role: str,
        content: str,
    ):
        """添加到会话上下文"""
        if session_id in self._active_sessions:
            self._active_sessions[session_id]["context"].append({
                "role": role,
                "content": content,
                "timestamp": time.time(),
            })

    async def process_message(
        self,
        session_id: str,
        message: str,
        user_id: str,
    ) -> dict:
        """处理消息"""
        session = self._active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        await self.add_to_context(session_id, "user", message)

        context = await self.memory.get_context(
            user_id=user_id,
            session_id=session_id,
            current_query=message,
        )

        response = f"Processed: {message[:50]}..."

        await self.memory.add(
            user_id=user_id,
            session_id=session_id,
            content=message,
            memory_type="interaction",
            importance=0.6,
        )

        await self.add_to_context(session_id, "assistant", response)

        return {
            "session_id": session_id,
            "response": response,
            "context_used": len(context),
        }

    async def record_feedback(
        self,
        session_id: str,
        feedback_type: str,
        content: str,
    ):
        """记录反馈"""
        session = self._active_sessions.get(session_id)
        if not session:
            return

        await self.evolution.record_feedback(
            user_id=session["user_id"],
            department_id=session.get("department_id", "default"),
            interaction_id=session_id,
            feedback_type=feedback_type,
            content=content,
        )

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "memory": self.memory.get_stats(),
            "active_sessions": len(self._active_sessions),
            "agents": len(self.orchestrator._agents),
            "evolution_records": len(self.evolution._evolution_records),
        }
