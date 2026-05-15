"""
国产模型 Provider 模块
"""

from typing import Any

from taiji_agent.providers.base import LLMProvider
from taiji_agent.providers.chinese.doubao import DoubaoProvider
from taiji_agent.providers.chinese.glm import GLMProvider
from taiji_agent.providers.chinese.kimi import KimiProvider
from taiji_agent.providers.chinese.qwen import QwenProvider

CHINESE_PROVIDERS: dict[str, dict[str, Any]] = {
    "qwen": {
        "name": "通义千问",
        "provider": QwenProvider,
        "models": ["qwen-plus", "qwen-max", "qwen-turbo", "qwen-coder-plus"],
        "default_model": "qwen-plus",
        "env_key": "DASHSCOPE_API_KEY",
        "features": ["对话", "代码", "中文优化"],
        "context_window": 128000,
    },
    "glm": {
        "name": "智谱 GLM",
        "provider": GLMProvider,
        "models": ["glm-4-plus", "glm-4-flash", "glm-4", "glm-4v"],
        "default_model": "glm-4-flash",
        "env_key": "ZHIPU_API_KEY",
        "features": ["对话", "长上下文", "中文理解"],
        "context_window": 128000,
    },
    "kimi": {
        "name": "Kimi",
        "provider": KimiProvider,
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "default_model": "moonshot-v1-8k",
        "env_key": "MOONSHOT_API_KEY",
        "features": ["长上下文", "代码", "中文"],
        "context_window": 128000,
    },
    "doubao": {
        "name": "豆包",
        "provider": DoubaoProvider,
        "models": ["doubao-pro-32k", "doubao-lite-32k", "doubao-embedding"],
        "default_model": "doubao-pro-32k",
        "env_key": "DOUBAO_API_KEY",
        "features": ["对话", "中文优化", "低成本"],
        "context_window": 32000,
    },
}


def get_chinese_provider(provider_name: str, **kwargs: Any) -> LLMProvider:
    """获取国产模型 Provider"""
    if provider_name not in CHINESE_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}")

    config = CHINESE_PROVIDERS[provider_name]
    provider_class: type[LLMProvider] = config["provider"]

    return provider_class(**kwargs)


def list_chinese_providers() -> dict:
    """列出所有国产模型"""
    return {
        name: {
            "name": cfg["name"],
            "models": cfg["models"],
            "default_model": cfg["default_model"],
            "features": cfg["features"],
            "context_window": cfg["context_window"],
        }
        for name, cfg in CHINESE_PROVIDERS.items()
    }


__all__ = [
    "QwenProvider",
    "GLMProvider",
    "KimiProvider",
    "DoubaoProvider",
    "CHINESE_PROVIDERS",
    "get_chinese_provider",
    "list_chinese_providers",
]
