#!/usr/bin/env python3
"""
govmcp.models.adapters — 各厂商LLM适配器

提供统一的适配器接口，封装各厂商SDK的差异。
"""

from __future__ import annotations

__all__ = [
    "LLMAdapter",
    "WenxinAdapter",
    "QwenAdapter",
    "ZhipuAdapter",
    "SparkAdapter",
    "HunyuanAdapter",
    "PanguAdapter",
    "DoubaoAdapter",
    "MinimaxAdapter",
    "MoonshotAdapter",
    "BaichuanAdapter",
    "OthersAdapter",
]

from govmcp.models.adapters.baichuan import BaichuanAdapter
from govmcp.models.adapters.base import LLMAdapter
from govmcp.models.adapters.doubao import DoubaoAdapter
from govmcp.models.adapters.hunyuan import HunyuanAdapter
from govmcp.models.adapters.minimax import MinimaxAdapter
from govmcp.models.adapters.moonshot import MoonshotAdapter
from govmcp.models.adapters.others import OthersAdapter
from govmcp.models.adapters.pangu import PanguAdapter
from govmcp.models.adapters.qwen import QwenAdapter
from govmcp.models.adapters.spark import SparkAdapter
from govmcp.models.adapters.wenxin import WenxinAdapter
from govmcp.models.adapters.zhipu import ZhipuAdapter
