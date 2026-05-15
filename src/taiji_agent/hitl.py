"""
Human-in-the-Loop 适配模块

提供与 Harness Runtime 的 HITL 功能对接：
- 审批工作流
- 置信度门控
- 检查点管理
- 反馈处理
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class ApprovalStatus(str, Enum):
    """审批状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ConfidenceLevel(str, Enum):
    """置信度等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ApprovalRequest:
    """审批请求"""
    request_id: str
    user_id: str
    agent_id: str
    action: str
    description: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    context: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class ApprovalDecision:
    """审批决策"""
    request_id: str
    decision: ApprovalStatus
    approver_id: str = ""
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


@dataclass
class ConfidenceGate:
    """置信度门控"""
    level: ConfidenceLevel
    threshold: float
    requires_approval: bool = False
    auto_action: str | None = None


@dataclass
class Checkpoint:
    """检查点"""
    checkpoint_id: str
    session_id: str
    state: dict
    created_at: float = field(default_factory=time.time)
    description: str = ""
    metadata: dict = field(default_factory=dict)


class ApprovalQueue:
    """
    审批队列

    管理人工审批请求
    """

    def __init__(self, default_timeout: float = 300.0):
        self.default_timeout = default_timeout
        self._requests: dict[str, ApprovalRequest] = {}
        self._pending: list[str] = []
        self._callbacks: dict[str, list[Callable]] = {}

    def create_request(
        self,
        user_id: str,
        agent_id: str,
        action: str,
        description: str,
        context: dict | None = None,
        timeout: float | None = None,
    ) -> str:
        """创建审批请求"""
        request_id = str(uuid.uuid4())

        request = ApprovalRequest(
            request_id=request_id,
            user_id=user_id,
            agent_id=agent_id,
            action=action,
            description=description,
            expires_at=time.time() + (timeout or self.default_timeout),
            context=context or {},
        )

        self._requests[request_id] = request
        self._pending.append(request_id)

        logger.info(f"Approval request created: {request_id}")
        return request_id

    def get_request(self, request_id: str) -> ApprovalRequest | None:
        """获取审批请求"""
        return self._requests.get(request_id)

    def approve(self, request_id: str, approver_id: str, reason: str = "") -> bool:
        """批准请求"""
        request = self._requests.get(request_id)
        if not request:
            return False

        request.status = ApprovalStatus.APPROVED
        self._pending.remove(request_id)

        decision = ApprovalDecision(
            request_id=request_id,
            decision=ApprovalStatus.APPROVED,
            approver_id=approver_id,
            reason=reason,
        )

        self._trigger_callbacks(request_id, decision)

        logger.info(f"Approval approved: {request_id}")
        return True

    def reject(self, request_id: str, approver_id: str, reason: str = "") -> bool:
        """拒绝请求"""
        request = self._requests.get(request_id)
        if not request:
            return False

        request.status = ApprovalStatus.REJECTED
        if request_id in self._pending:
            self._pending.remove(request_id)

        decision = ApprovalDecision(
            request_id=request_id,
            decision=ApprovalStatus.REJECTED,
            approver_id=approver_id,
            reason=reason,
        )

        self._trigger_callbacks(request_id, decision)

        logger.info(f"Approval rejected: {request_id}")
        return True

    def cancel(self, request_id: str) -> bool:
        """取消请求"""
        request = self._requests.get(request_id)
        if not request:
            return False

        request.status = ApprovalStatus.CANCELLED
        if request_id in self._pending:
            self._pending.remove(request_id)

        logger.info(f"Approval cancelled: {request_id}")
        return True

    def get_pending(self) -> list[ApprovalRequest]:
        """获取待审批请求"""
        now = time.time()
        expired = []

        for request_id in self._pending:
            request = self._requests.get(request_id)
            if request:
                if request.expires_at < now:
                    request.status = ApprovalStatus.TIMEOUT
                    expired.append(request_id)
                else:
                    yield request

        for request_id in expired:
            self._pending.remove(request_id)

    def on_decision(self, request_id: str, callback: Callable):
        """注册决策回调"""
        if request_id not in self._callbacks:
            self._callbacks[request_id] = []
        self._callbacks[request_id].append(callback)

    def _trigger_callbacks(self, request_id: str, decision: ApprovalDecision):
        """触发回调"""
        callbacks = self._callbacks.pop(request_id, [])
        for callback in callbacks:
            try:
                callback(decision)
            except Exception as e:
                logger.error(f"Callback error: {e}")


class ConfidenceGateManager:
    """
    置信度门控管理器

    根据置信度决定是否需要人工审批
    """

    def __init__(self, approval_queue: ApprovalQueue):
        self.approval_queue = approval_queue
        self._gates: dict[str, ConfidenceGate] = {
            "critical": ConfidenceGate(
                level=ConfidenceLevel.CRITICAL,
                threshold=0.3,
                requires_approval=True,
                auto_action=None,
            ),
            "low": ConfidenceGate(
                level=ConfidenceLevel.LOW,
                threshold=0.5,
                requires_approval=False,
                auto_action="warn",
            ),
            "medium": ConfidenceGate(
                level=ConfidenceLevel.MEDIUM,
                threshold=0.7,
                requires_approval=False,
                auto_action=None,
            ),
            "high": ConfidenceGate(
                level=ConfidenceLevel.HIGH,
                threshold=1.0,
                requires_approval=False,
                auto_action="proceed",
            ),
        }

    def evaluate(self, confidence: float) -> tuple[ConfidenceLevel, ConfidenceGate]:
        """评估置信度"""
        if confidence < self._gates["critical"].threshold:
            level = ConfidenceLevel.CRITICAL
        elif confidence < self._gates["low"].threshold:
            level = ConfidenceLevel.LOW
        elif confidence < self._gates["medium"].threshold:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.HIGH

        gate = self._gates[level.value]
        return level, gate

    async def check(
        self,
        confidence: float,
        user_id: str,
        agent_id: str,
        action: str,
        context: dict | None = None,
    ) -> tuple[bool, str | None]:
        """
        检查是否需要审批

        Returns:
            (proceed, approval_id)
        """
        level, gate = self.evaluate(confidence)

        if not gate.requires_approval:
            return True, None

        approval_id = self.approval_queue.create_request(
            user_id=user_id,
            agent_id=agent_id,
            action=action,
            description=f"置信度 {confidence:.2f} ({level.value}) 需要审批",
            context=context,
        )

        return False, approval_id


class CheckpointManager:
    """
    检查点管理器

    保存和恢复会话状态
    """

    def __init__(self):
        self._checkpoints: dict[str, list[Checkpoint]] = {}

    def create(
        self,
        session_id: str,
        state: dict,
        description: str = "",
        metadata: dict | None = None,
    ) -> str:
        """创建检查点"""
        checkpoint_id = str(uuid.uuid4())

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            session_id=session_id,
            state=state,
            description=description,
            metadata=metadata or {},
        )

        if session_id not in self._checkpoints:
            self._checkpoints[session_id] = []

        self._checkpoints[session_id].append(checkpoint)

        logger.info(f"Checkpoint created: {checkpoint_id}")
        return checkpoint_id

    def get(self, checkpoint_id: str) -> Checkpoint | None:
        """获取检查点"""
        for checkpoints in self._checkpoints.values():
            for cp in checkpoints:
                if cp.checkpoint_id == checkpoint_id:
                    return cp
        return None

    def get_latest(self, session_id: str) -> Checkpoint | None:
        """获取最新的检查点"""
        checkpoints = self._checkpoints.get(session_id, [])
        if checkpoints:
            return checkpoints[-1]
        return None

    def restore(self, checkpoint_id: str) -> dict | None:
        """恢复检查点状态"""
        checkpoint = self.get(checkpoint_id)
        if checkpoint:
            logger.info(f"Checkpoint restored: {checkpoint_id}")
            return checkpoint.state.copy()
        return None

    def list_session_checkpoints(self, session_id: str) -> list[Checkpoint]:
        """列出会话的所有检查点"""
        return self._checkpoints.get(session_id, [])

    def delete(self, checkpoint_id: str) -> bool:
        """删除检查点"""
        for session_id, checkpoints in self._checkpoints.items():
            for i, cp in enumerate(checkpoints):
                if cp.checkpoint_id == checkpoint_id:
                    checkpoints.pop(i)
                    logger.info(f"Checkpoint deleted: {checkpoint_id}")
                    return True
        return False


class HITLIntegration:
    """
    Human-in-the-Loop 集成

    整合审批、置信度门控、检查点
    """

    def __init__(self):
        self.approval_queue = ApprovalQueue()
        self.confidence_gate = ConfidenceGateManager(self.approval_queue)
        self.checkpoint_manager = CheckpointManager()

    async def request_approval(
        self,
        confidence: float,
        user_id: str,
        agent_id: str,
        action: str,
        context: dict | None = None,
    ) -> tuple[bool, str | None]:
        """请求审批"""
        proceed, approval_id = await self.confidence_gate.check(
            confidence=confidence,
            user_id=user_id,
            agent_id=agent_id,
            action=action,
            context=context,
        )

        if proceed:
            return True, None

        return False, approval_id

    def approve(self, request_id: str, approver_id: str, reason: str = "") -> bool:
        """批准"""
        return self.approval_queue.approve(request_id, approver_id, reason)

    def reject(self, request_id: str, approver_id: str, reason: str = "") -> bool:
        """拒绝"""
        return self.approval_queue.reject(request_id, approver_id, reason)

    def create_checkpoint(
        self,
        session_id: str,
        state: dict,
        description: str = "",
    ) -> str:
        """创建检查点"""
        return self.checkpoint_manager.create(session_id, state, description)

    def restore_checkpoint(self, checkpoint_id: str) -> dict | None:
        """恢复检查点"""
        return self.checkpoint_manager.restore(checkpoint_id)

    def get_stats(self) -> dict:
        """获取统计"""
        return {
            "pending_approvals": len(list(self.approval_queue.get_pending())),
            "total_checkpoints": sum(
                len(cps) for cps in self.checkpoint_manager._checkpoints.values()
            ),
        }


_global_hitl = HITLIntegration()


def get_hitl() -> HITLIntegration:
    """获取全局 HITL 实例"""
    return _global_hitl
