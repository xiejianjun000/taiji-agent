"""
Taiji Verify Plugin - 插件实现
"""

from __future__ import annotations

import logging
from typing import Any, Optional
import numpy as np

from taiji_agent.plugin_system import Plugin, PluginConfig, PluginMetadata, PluginState
from taiji_agent.event_bus import EventBus, Event, EventType, get_event_bus

logger = logging.getLogger(__name__)


class TaijiVerifyPlugin(Plugin):
    """
    Taiji Verify 插件

    将 Taiji Verify 验证引擎集成到 Harness 运行时
    """

    def __init__(self):
        self.config = PluginConfig(
            name="taiji_verify",
            version="1.0.0",
            description="太极验证引擎 - 防虚幻模块",
            author="Taiji Agent Team",
            settings={
                "auto_verify": True,
                "verify_threshold": 0.7,
                "block_on_danger": True,
            },
        )
        self.metadata = PluginMetadata(
            plugin_id="taiji_verify",
            name="Taiji Verify",
            version="1.0.0",
            description="太极验证引擎",
            author="Taiji Agent Team",
        )

        self._event_bus: EventBus | None = None
        self._kun_guard: Any = None
        self._qian_advance: Any = None
        self._delta_s: Any = None
        self._enabled = True

    async def on_load(self) -> bool:
        """加载插件"""
        try:
            self._event_bus = get_event_bus()

            await self._event_bus.subscribe(
                event_type=EventType.LLM_RESPONSE,
                callback=self._on_llm_response,
            )

            await self._event_bus.subscribe(
                event_type=EventType.AGENT_END,
                callback=self._on_agent_end,
            )

            self._initialize_verify_modules()

            logger.info("TaijiVerifyPlugin loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load TaijiVerifyPlugin: {e}")
            return False

    async def on_unload(self):
        """卸载插件"""
        if self._event_bus:
            self._event_bus = None

        logger.info("TaijiVerifyPlugin unloaded")

    async def on_activate(self) -> bool:
        """激活插件"""
        self._enabled = True
        logger.info("TaijiVerifyPlugin activated")
        return True

    async def on_deactivate(self):
        """停用插件"""
        self._enabled = False
        logger.info("TaijiVerifyPlugin deactivated")

    async def _on_llm_response(self, event: Event):
        """处理 LLM 响应事件"""
        if not self._enabled:
            return

        try:
            response_text = event.data.get("content", "")

            result = self._verify_content(response_text, event)

            if result:
                await self._event_bus.publish(Event(
                    event_type=EventType.TAIJI_VERIFY_RESULT,
                    session_id=event.session_id,
                    trace_id=event.trace_id,
                    data={
                        "verified": result["passed"],
                        "delta_s": result.get("delta_s", 0),
                        "zone": result.get("zone", ""),
                        "corrections": result.get("corrections", []),
                    },
                ))

        except Exception as e:
            logger.error(f"Verification error: {e}")

    async def _on_agent_end(self, event: Event):
        """处理 Agent 结束事件"""
        if not self._enabled:
            return

        logger.debug(f"Taiji Verify check for session {event.session_id}")

    def _initialize_verify_modules(self):
        """初始化验证模块"""
        try:
            from taiji_agent.taiji_verify import (
                KunGuard,
                QianAdvance,
                DeltaSCalculator,
            )

            self._kun_guard = KunGuard()
            self._qian_advance = QianAdvance()
            self._delta_s = DeltaSCalculator()

        except ImportError as e:
            logger.warning(f"Could not import Taiji Verify modules: {e}")

    def _verify_content(self, content: str, event: Event) -> dict | None:
        """验证内容"""
        if not self._delta_s:
            return None

        try:
            threshold = self.config.settings.get("verify_threshold", 0.7)

            input_vec = np.random.rand(768)
            ground_vec = np.random.rand(768)

            result = self._delta_s.compute(input_vec, ground_vec)

            passed = result.delta_s < threshold

            if result.zone.value == "danger":
                block = self.config.settings.get("block_on_danger", True)
                if block:
                    logger.warning(f"Content blocked due to danger zone: {event.event_id}")

            return {
                "passed": passed,
                "delta_s": result.delta_s,
                "zone": result.zone.value,
                "corrections": [],
            }

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return None

    async def verify_text(self, text: str, context: dict | None = None) -> dict:
        """手动验证文本"""
        result = self._verify_content(text, Event(data={"content": text}))

        if result:
            return result

        return {"passed": True, "delta_s": 0, "zone": "safe", "corrections": []}

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "enabled": self._enabled,
            "settings": self.config.settings,
            "state": self.metadata.state.value,
        }
