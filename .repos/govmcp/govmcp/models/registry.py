#!/usr/bin/env python3
"""
govmcp.models.registry — 模型注册表

提供 LLMProvider 枚举、ModelConfig 数据类和 ModelRegistry 类，
用于管理所有国产大模型的注册和查询。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

if TYPE_CHECKING:
    from govmcp.models.adapters.base import LLMAdapter


class LLMProvider(Enum):
    """国产大模型厂商枚举"""

    WENXIN = "wenxin"
    QWEN = "qwen"
    ZHIPU = "zhipu"
    SPARK = "spark"
    HUNYUAN = "hunyuan"
    PANGU = "pangu"
    DOUBAO = "doubao"
    GPT360 = "gpt360"
    MINIMAX = "minimax"
    MOONSHOT = "moonshot"
    BAICHUAN = "baichuan"
    SENSECHAT = "sensechat"
    QIZHI = "qizhi"
    TUOSHAI = "tuoshai"
    WANDAO = "wandao"
    WENDA = "wenda"
    INTERNNLM = "internlm"
    MINDCHAT = "mindchat"
    CTYUN = "ctyun"
    UNICOM = "unicom"
    UNKNOWN = "unknown"

    @classmethod
    def from_model_id(cls, model_id: str) -> LLMProvider:
        """根据模型ID推断provider"""
        model_lower = model_id.lower()
        if model_lower.startswith("ernie"):
            return cls.WENXIN
        elif model_lower.startswith("qwen"):
            return cls.QWEN
        elif model_lower.startswith("glm") or model_lower.startswith("chatglm"):
            return cls.ZHIPU
        elif model_lower.startswith("spark"):
            return cls.SPARK
        elif model_lower.startswith("hunyuan"):
            return cls.HUNYUAN
        elif model_lower.startswith("pangu"):
            return cls.PANGU
        elif model_lower.startswith("doubao"):
            return cls.DOUBAO
        elif model_lower.startswith("360gpt"):
            return cls.GPT360
        elif model_lower.startswith("minimax"):
            return cls.MINIMAX
        elif model_lower.startswith("kimi"):
            return cls.MOONSHOT
        elif model_lower.startswith("baichuan"):
            return cls.BAICHUAN
        elif model_lower.startswith("sensechat"):
            return cls.SENSECHAT
        elif model_lower.startswith("qizhi"):
            return cls.QIZHI
        elif model_lower.startswith("tuoshai"):
            return cls.TUOSHAI
        elif model_lower.startswith("wandao"):
            return cls.WANDAO
        elif model_lower.startswith("wenda"):
            return cls.WENDA
        elif model_lower.startswith("internlm"):
            return cls.INTERNNLM
        elif model_lower.startswith("mindchat"):
            return cls.MINDCHAT
        elif model_lower.startswith("ctyun"):
            return cls.CTYUN
        elif model_lower.startswith("unicom"):
            return cls.UNICOM
        return cls.UNKNOWN

    @property
    def adapter_name(self) -> str:
        """获取适配器模块名"""
        mapping = {
            self.WENXIN: "wenxin",
            self.QWEN: "qwen",
            self.ZHIPU: "zhipu",
            self.SPARK: "spark",
            self.HUNYUAN: "hunyuan",
            self.PANGU: "pangu",
            self.DOUBAO: "doubao",
            self.GPT360: "others",
            self.MINIMAX: "minimax",
            self.MOONSHOT: "moonshot",
            self.BAICHUAN: "baichuan",
            self.SENSECHAT: "others",
            self.QIZHI: "others",
            self.TUOSHAI: "others",
            self.WANDAO: "others",
            self.WENDA: "others",
            self.INTERNNLM: "others",
            self.MINDCHAT: "others",
            self.CTYUN: "others",
            self.UNICOM: "others",
        }
        return mapping.get(self, "others")


@dataclass
class ModelConfig:
    """模型配置数据类"""

    provider: LLMProvider
    model_id: str
    api_base: str
    capabilities: dict[str, bool] = field(default_factory=dict)
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    timeout: float = 60.0
    extra: dict[str, Any] = field(default_factory=dict)

    def supports_streaming(self) -> bool:
        """是否支持流式输出"""
        return self.capabilities.get("streaming", True)

    def supports_function_call(self) -> bool:
        """是否支持函数调用"""
        return self.capabilities.get("function_call", False)

    def supports_vision(self) -> bool:
        """是否支持视觉"""
        return self.capabilities.get("vision", False)

    def supports_embedding(self) -> bool:
        """是否支持文本嵌入"""
        return self.capabilities.get("embedding", True)


class ModelRegistry:
    """
    模型注册表

    管理所有国产大模型的配置和适配器实例。

    Usage:
        registry = ModelRegistry()

        # 获取模型配置
        config = registry.get_model("ernie-4.0")

        # 获取适配器
        adapter = registry.get_adapter("ernie-4.0")

        # 调用chat
        response = adapter.chat([{"role": "user", "content": "你好"}])

        # 列出所有模型
        models = registry.list_models()

        # 按provider过滤
        qwen_models = registry.list_models(provider=LLMProvider.QWEN)
    """

    _instance: ModelRegistry | None = None
    _models: dict[str, ModelConfig] = {}
    _adapters: dict[str, Any] = {}

    def __new__(cls) -> ModelRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._models: dict[str, ModelConfig] = {}
            self._adapters: dict[str, Any] = {}
            self._register_builtin_models()
            self._initialized = True

    def _register_builtin_models(self) -> None:
        """注册内置的48个国产大模型"""

        builtin_models = [
            ModelConfig(
                provider=LLMProvider.WENXIN,
                model_id="ernie-4.0",
                api_base="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=8192,
                extra={"model_version": "ernie-4.0-8k"},
            ),
            ModelConfig(
                provider=LLMProvider.WENXIN,
                model_id="ernie-3.5",
                api_base="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-3.5-8k",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=8192,
            ),
            ModelConfig(
                provider=LLMProvider.WENXIN,
                model_id="ernie-3.0",
                api_base="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-3.0-8k",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=8192,
            ),
            ModelConfig(
                provider=LLMProvider.WENXIN,
                model_id="ernie-bot",
                api_base="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-bot",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.QWEN,
                model_id="qwen-turbo",
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=8192,
                extra={"model_name": "qwen-turbo"},
            ),
            ModelConfig(
                provider=LLMProvider.QWEN,
                model_id="qwen-plus",
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=32768,
                extra={"model_name": "qwen-plus"},
            ),
            ModelConfig(
                provider=LLMProvider.QWEN,
                model_id="qwen-max",
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=8192,
                extra={"model_name": "qwen-max"},
            ),
            ModelConfig(
                provider=LLMProvider.QWEN,
                model_id="qwen-long",
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=128000,
                extra={"model_name": "qwen-long"},
            ),
            ModelConfig(
                provider=LLMProvider.QWEN,
                model_id="qwen-7b",
                api_base="http://localhost:8000/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.QWEN,
                model_id="qwen-14b",
                api_base="http://localhost:8000/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.QWEN,
                model_id="qwen-72b",
                api_base="http://localhost:8000/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.ZHIPU,
                model_id="glm-4",
                api_base="https://open.bigmodel.cn/api/paas/v4/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=128000,
                extra={"model_name": "glm-4"},
            ),
            ModelConfig(
                provider=LLMProvider.ZHIPU,
                model_id="glm-4-plus",
                api_base="https://open.bigmodel.cn/api/paas/v4/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=128000,
                extra={"model_name": "glm-4-plus"},
            ),
            ModelConfig(
                provider=LLMProvider.ZHIPU,
                model_id="glm-3-turbo",
                api_base="https://open.bigmodel.cn/api/paas/v4/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=128000,
                extra={"model_name": "glm-3-turbo"},
            ),
            ModelConfig(
                provider=LLMProvider.ZHIPU,
                model_id="chatglm-6b",
                api_base="http://localhost:8000/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.ZHIPU,
                model_id="chatglm2-6b",
                api_base="http://localhost:8000/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=8192,
            ),
            ModelConfig(
                provider=LLMProvider.ZHIPU,
                model_id="chatglm3-6b",
                api_base="http://localhost:8000/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=8192,
            ),
            ModelConfig(
                provider=LLMProvider.SPARK,
                model_id="spark-3.5",
                api_base="https://spark-api.xf-yun.com/v3.5/chat",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.SPARK,
                model_id="spark-4.0",
                api_base="https://spark-api.xf-yun.com/v4.0/chat",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=8192,
            ),
            ModelConfig(
                provider=LLMProvider.SPARK,
                model_id="spark-lite",
                api_base="https://spark-api.xf-yun.com/v3.1/chat",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": False,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.HUNYUAN,
                model_id="hunyuan-lite",
                api_base="https://hunyuan.cloud.tencent.com/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
                extra={"model_name": "hunyuan-lite"},
            ),
            ModelConfig(
                provider=LLMProvider.HUNYUAN,
                model_id="hunyuan-pro",
                api_base="https://hunyuan.cloud.tencent.com/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=8192,
                extra={"model_name": "hunyuan-pro"},
            ),
            ModelConfig(
                provider=LLMProvider.HUNYUAN,
                model_id="hunyuan-standard",
                api_base="https://hunyuan.cloud.tencent.com/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=16384,
                extra={"model_name": "hunyuan-standard"},
            ),
            ModelConfig(
                provider=LLMProvider.PANGU,
                model_id="pangu-alpha",
                api_base="https://www.huaweicloud.com/product/wanda/chat",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": False,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.PANGU,
                model_id="pangu-chat",
                api_base="https://www.huaweicloud.com/product/wanda/chat",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=8192,
            ),
            ModelConfig(
                provider=LLMProvider.DOUBAO,
                model_id="doubao-pro",
                api_base="https://ark.cn-beijing.volces.com/api/v3/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=128000,
                extra={"model_name": "doubao-pro-32k"},
            ),
            ModelConfig(
                provider=LLMProvider.DOUBAO,
                model_id="doubao-lite",
                api_base="https://ark.cn-beijing.volces.com/api/v3/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=32000,
                extra={"model_name": "doubao-lite-32k"},
            ),
            ModelConfig(
                provider=LLMProvider.GPT360,
                model_id="360gpt-pro",
                api_base="https://ai.360.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.GPT360,
                model_id="360gpt-lite",
                api_base="https://ai.360.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.MINIMAX,
                model_id="minimax-abab5",
                api_base="https://api.minimax.chat/v1/text/chatcompletion_v2",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=8192,
            ),
            ModelConfig(
                provider=LLMProvider.MINIMAX,
                model_id="minimax-abab6",
                api_base="https://api.minimax.chat/v1/text/chatcompletion_v2",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=16384,
            ),
            ModelConfig(
                provider=LLMProvider.MINIMAX,
                model_id="minimax-chat",
                api_base="https://api.minimax.chat/v1/text/chatcompletion_v2",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=16384,
            ),
            ModelConfig(
                provider=LLMProvider.MOONSHOT,
                model_id="kimi-chat",
                api_base="https://api.moonshot.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=128000,
                extra={"model_name": "moonshot-v1-8k"},
            ),
            ModelConfig(
                provider=LLMProvider.MOONSHOT,
                model_id="kimi-pro",
                api_base="https://api.moonshot.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=128000,
                extra={"model_name": "moonshot-v1-32k"},
            ),
            ModelConfig(
                provider=LLMProvider.BAICHUAN,
                model_id="baichuan4",
                api_base="https://api.baichuan-ai.com/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.BAICHUAN,
                model_id="baichuan-7b",
                api_base="http://localhost:8000/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.BAICHUAN,
                model_id="baichuan-13b",
                api_base="http://localhost:8000/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.SENSECHAT,
                model_id="sensechat-5",
                api_base="https://api.sensenova.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=16384,
            ),
            ModelConfig(
                provider=LLMProvider.SENSECHAT,
                model_id="sensechat-4",
                api_base="https://api.sensenova.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=8192,
            ),
            ModelConfig(
                provider=LLMProvider.QIZHI,
                model_id="qizhi-chat",
                api_base="https://ai.360.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.TUOSHAI,
                model_id="tuoshai-chat",
                api_base="https://api.tuoshai.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.WANDAO,
                model_id="wandao-chat",
                api_base="https://wandao.h3c.com/api/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.WENDA,
                model_id="wenda-chat",
                api_base="https://api.wenda.com/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.INTERNNLM,
                model_id="internlm-chat",
                api_base="https://api.internlm.ai/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.INTERNNLM,
                model_id="internlm2-chat",
                api_base="https://api.internlm.ai/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": True,
                    "vision": True,
                    "embedding": True,
                },
                max_tokens=128000,
            ),
            ModelConfig(
                provider=LLMProvider.MINDCHAT,
                model_id="mindchat",
                api_base="https://api.mindchat.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.CTYUN,
                model_id="ctyun-chat",
                api_base="https://api.ctyun.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
            ModelConfig(
                provider=LLMProvider.UNICOM,
                model_id="unicom-chat",
                api_base="https://api.unicom.cn/v1/chat/completions",
                capabilities={
                    "streaming": True,
                    "function_call": False,
                    "vision": False,
                    "embedding": True,
                },
                max_tokens=4096,
            ),
        ]

        for config in builtin_models:
            self._models[config.model_id] = config

    def register_model(self, provider: LLMProvider, model_id: str, config: ModelConfig) -> bool:
        """
        注册一个新模型

        Args:
            provider: 模型所属厂商
            model_id: 模型ID
            config: 模型配置

        Returns:
            是否注册成功 (ID不存在时返回True)
        """
        if model_id in self._models:
            return False
        self._models[model_id] = config
        return True

    def get_model(self, model_id: str) -> ModelConfig | None:
        """
        获取模型配置

        Args:
            model_id: 模型ID

        Returns:
            模型配置，不存在时返回None
        """
        return self._models.get(model_id)

    def list_models(self, provider: LLMProvider | None = None) -> list[ModelConfig]:
        """
        列出所有模型

        Args:
            provider: 可选，按provider过滤

        Returns:
            模型配置列表
        """
        if provider is None:
            return list(self._models.values())
        return [m for m in self._models.values() if m.provider == provider]

    def validate_model(self, model_id: str) -> bool:
        """
        验证模型是否已注册

        Args:
            model_id: 模型ID

        Returns:
            是否已注册
        """
        return model_id in self._models

    def get_adapter(self, model_id: str) -> Any | None:
        """
        获取模型的适配器实例

        Args:
            model_id: 模型ID

        Returns:
            适配器实例，不存在时返回None
        """
        if model_id in self._adapters:
            return self._adapters[model_id]

        config = self._models.get(model_id)
        if config is None:
            return None

        adapter_name = config.provider.adapter_name
        try:
            import govmcp.models.adapters as adapter_module

            adapter_cls = getattr(
                adapter_module, f"{adapter_name.title().replace('_', '')}Adapter", None
            )
            if adapter_cls is None:
                adapter_cls = getattr(adapter_module, f"{adapter_name.title()}Adapter", None)
            if adapter_cls is None:
                from govmcp.models.adapters.others import OthersAdapter

                adapter_cls = OthersAdapter
            self._adapters[model_id] = adapter_cls(config)
            return self._adapters[model_id]
        except (AttributeError, ImportError):
            from govmcp.models.adapters.others import OthersAdapter

            return OthersAdapter(config)

    def count(self) -> int:
        """返回已注册模型数量"""
        return len(self._models)

    def get_providers(self) -> list[LLMProvider]:
        """返回所有已使用的provider列表"""
        return list(set(m.provider for m in self._models.values()))

    def clear(self) -> None:
        """清空注册表 (测试用)"""
        self._models.clear()
        self._adapters.clear()

    def __iter__(self) -> Iterator[str]:
        """迭代器支持"""
        return iter(self._models)

    def __len__(self) -> int:
        return len(self._models)


_default_registry: ModelRegistry | None = None


def get_default_registry() -> ModelRegistry:
    """获取默认模型注册表实例"""
    global _default_registry
    if _default_registry is None:
        _default_registry = ModelRegistry()
    return _default_registry


def register_model(provider: LLMProvider, model_id: str, config: ModelConfig) -> bool:
    """全局注册模型"""
    return get_default_registry().register_model(provider, model_id, config)


def get_model(model_id: str) -> ModelConfig | None:
    """全局获取模型配置"""
    return get_default_registry().get_model(model_id)


def list_models(provider: LLMProvider | None = None) -> list[ModelConfig]:
    """全局列出模型"""
    return get_default_registry().list_models(provider)


def validate_model(model_id: str) -> bool:
    """全局验证模型"""
    return get_default_registry().validate_model(model_id)
