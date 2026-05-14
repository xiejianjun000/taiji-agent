#!/usr/bin/env python3
"""
govmcp.models — 国产大模型适配层

提供统一的模型注册表和厂商适配器接口，
支持 48 个国产 LLM 的无缝切换。

模块结构:
- registry: 模型注册表 (LLMProvider枚举, ModelConfig, ModelRegistry)
- adapters: 各厂商适配器
    - base: LLMAdapter 基类
    - wenxin: 百度文心一言
    - qwen: 阿里通义千问
    - zhipu: 智谱AI GLM
    - spark: 讯飞星火
    - hunyuan: 腾讯混元
    - pangu: 华为盘古
    - doubao: 字节豆包
    - minimax: MiniMax
    - moonshot: 月之暗面Kimi
    - baichuan: 百川智能
    - others: 其他厂商 (360奇智, 拓世AI, 望道, 出门问问, 书生浦语, 聆心智能, 天翼云, 联通AI)

Usage:
    from govmcp.models import ModelRegistry, LLMProvider

    registry = ModelRegistry()
    config = registry.get_model("ernie-4.0")
    adapter = registry.get_adapter("ernie-4.0")
    response = adapter.chat([{"role": "user", "content": "你好"}])
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = [
    "LLMProvider",
    "ModelConfig",
    "ModelRegistry",
    "LLMAdapter",
    "register_model",
    "get_model",
    "list_models",
    "validate_model",
]

from govmcp.models.adapters.base import LLMAdapter
from govmcp.models.registry import (
    LLMProvider,
    ModelConfig,
    ModelRegistry,
    get_model,
    list_models,
    register_model,
    validate_model,
)
