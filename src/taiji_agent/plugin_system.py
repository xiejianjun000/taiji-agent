"""
Plugin 系统扩展

提供与 Harness Runtime 兼容的 Plugin 接口：
- Plugin 基类
- 生命周期管理
- 激活/停用
- 配置管理
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import yaml

logger = logging.getLogger(__name__)


class PluginState(str, Enum):
    """插件状态"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNLOADING = "unloading"


@dataclass
class PluginConfig:
    """插件配置"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    enabled: bool = True
    priority: int = 0
    settings: dict = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class PluginMetadata:
    """插件元数据"""
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    state: PluginState = PluginState.UNLOADED
    loaded_at: float = 0.0
    activated_at: float = 0.0
    error_message: str = ""


class Plugin(ABC):
    """
    Plugin 基类

    所有插件必须继承此类并实现抽象方法
    """

    config: PluginConfig
    metadata: PluginMetadata

    @abstractmethod
    async def on_load(self) -> bool:
        """
        加载插件

        Returns:
            是否加载成功
        """
        pass

    @abstractmethod
    async def on_unload(self):
        """卸载插件"""
        pass

    async def on_activate(self) -> bool:
        """
        激活插件

        Returns:
            是否激活成功
        """
        return True

    async def on_deactivate(self):
        """停用插件"""
        pass

    async def on_config_update(self, config: dict):
        """配置更新"""
        pass


class PluginInterface:
    """
    插件接口定义

    定义插件可用的标准接口
    """

    def __init__(self, plugin: Plugin):
        self._plugin = plugin

    @property
    def name(self) -> str:
        return self._plugin.config.name

    @property
    def version(self) -> str:
        return self._plugin.config.version

    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        return self._plugin.config.settings.get(key, default)

    def set_config(self, key: str, value: Any):
        """设置配置"""
        self._plugin.config.settings[key] = value

    def is_active(self) -> bool:
        """检查是否激活"""
        return self._plugin.metadata.state == PluginState.ACTIVE


class PluginRegistry:
    """
    插件注册表

    管理插件的注册、加载、激活、停用
    """

    def __init__(self):
        self._plugins: dict[str, Plugin] = {}
        self._plugin_configs: dict[str, PluginConfig] = {}
        self._plugin_interfaces: dict[str, PluginInterface] = {}
        self._load_order: list[str] = []

    def register(
        self,
        plugin_class: type[Plugin],
        config: PluginConfig | None = None,
    ) -> str:
        """
        注册插件

        Args:
            plugin_class: 插件类
            config: 插件配置

        Returns:
            插件ID
        """
        plugin_id = config.name if config else plugin_class.__name__

        if plugin_id in self._plugins:
            logger.warning(f"Plugin already registered: {plugin_id}")
            return plugin_id

        if config is None:
            config = PluginConfig(name=plugin_id)

        self._plugin_configs[plugin_id] = config
        self._load_order.append(plugin_id)

        logger.info(f"Plugin registered: {plugin_id}")
        return plugin_id

    async def load(self, plugin_id: str) -> bool:
        """
        加载插件

        Args:
            plugin_id: 插件ID

        Returns:
            是否加载成功
        """
        if plugin_id not in self._plugin_configs:
            logger.error(f"Plugin config not found: {plugin_id}")
            return False

        if plugin_id in self._plugins:
            logger.warning(f"Plugin already loaded: {plugin_id}")
            return True

        config = self._plugin_configs[plugin_id]

        if not config.enabled:
            logger.info(f"Plugin disabled: {plugin_id}")
            return False

        for dep_id in config.dependencies:
            if dep_id not in self._plugins:
                logger.error(f"Plugin dependency not loaded: {dep_id}")
                return False

        try:
            plugin = self._create_plugin_instance(plugin_id)
            plugin.config = config
            plugin.metadata = PluginMetadata(
                plugin_id=plugin_id,
                name=config.name,
                version=config.version,
                description=config.description,
                author=config.author,
            )

            plugin.metadata.state = PluginState.LOADING

            success = await plugin.on_load()

            if success:
                plugin.metadata.state = PluginState.LOADED
                plugin.metadata.loaded_at = time.time()
                self._plugins[plugin_id] = plugin
                self._plugin_interfaces[plugin_id] = PluginInterface(plugin)
                logger.info(f"Plugin loaded: {plugin_id}")
                return True
            else:
                plugin.metadata.state = PluginState.ERROR
                logger.error(f"Plugin load failed: {plugin_id}")
                return False

        except Exception as e:
            logger.error(f"Plugin load error: {e}")
            return False

    async def activate(self, plugin_id: str) -> bool:
        """
        激活插件

        Args:
            plugin_id: 插件ID

        Returns:
            是否激活成功
        """
        if plugin_id not in self._plugins:
            logger.error(f"Plugin not loaded: {plugin_id}")
            return False

        plugin = self._plugins[plugin_id]

        if plugin.metadata.state == PluginState.ACTIVE:
            return True

        try:
            success = await plugin.on_activate()

            if success:
                plugin.metadata.state = PluginState.ACTIVE
                plugin.metadata.activated_at = time.time()
                logger.info(f"Plugin activated: {plugin_id}")
                return True
            else:
                logger.error(f"Plugin activation failed: {plugin_id}")
                return False

        except Exception as e:
            plugin.metadata.state = PluginState.ERROR
            plugin.metadata.error_message = str(e)
            logger.error(f"Plugin activation error: {e}")
            return False

    async def deactivate(self, plugin_id: str) -> bool:
        """
        停用插件

        Args:
            plugin_id: 插件ID

        Returns:
            是否停用成功
        """
        if plugin_id not in self._plugins:
            return False

        plugin = self._plugins[plugin_id]

        if plugin.metadata.state != PluginState.ACTIVE:
            return True

        try:
            await plugin.on_deactivate()
            plugin.metadata.state = PluginState.INACTIVE
            logger.info(f"Plugin deactivated: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"Plugin deactivation error: {e}")
            return False

    async def unload(self, plugin_id: str) -> bool:
        """
        卸载插件

        Args:
            plugin_id: 插件ID

        Returns:
            是否卸载成功
        """
        if plugin_id not in self._plugins:
            return False

        plugin = self._plugins[plugin_id]

        if plugin.metadata.state == PluginState.ACTIVE:
            await self.deactivate(plugin_id)

        try:
            plugin.metadata.state = PluginState.UNLOADING
            await plugin.on_unload()
            plugin.metadata.state = PluginState.UNLOADED

            del self._plugins[plugin_id]
            self._plugin_interfaces.pop(plugin_id, None)

            logger.info(f"Plugin unloaded: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"Plugin unload error: {e}")
            return False

    async def load_all(self) -> list[str]:
        """加载所有插件"""
        loaded = []

        for plugin_id in self._load_order:
            if await self.load(plugin_id):
                loaded.append(plugin_id)

        return loaded

    async def activate_all(self) -> list[str]:
        """激活所有插件"""
        activated = []

        for plugin_id in self._plugins:
            if await self.activate(plugin_id):
                activated.append(plugin_id)

        return activated

    def get_plugin(self, plugin_id: str) -> Plugin | None:
        """获取插件"""
        return self._plugins.get(plugin_id)

    def get_interface(self, plugin_id: str) -> PluginInterface | None:
        """获取插件接口"""
        return self._plugin_interfaces.get(plugin_id)

    def list_plugins(self, state: PluginState | None = None) -> list[PluginMetadata]:
        """列出插件"""
        plugins = []

        for plugin in self._plugins.values():
            if state is None or plugin.metadata.state == state:
                plugins.append(plugin.metadata)

        return plugins

    def _create_plugin_instance(self, plugin_id: str) -> Plugin:
        """创建插件实例"""
        from taiji_agent.event_bus import EventBusPlugin
        from taiji_agent.taiji_verify.plugins import TaijiVerifyPlugin
        from taiji_agent.govmcp.plugins import GovMCPPlugin

        plugin_map = {
            "eventbus": EventBusPlugin,
            "taiji_verify": TaijiVerifyPlugin,
            "govmcp": GovMCPPlugin,
        }

        plugin_class = plugin_map.get(plugin_id.lower())
        if plugin_class:
            return plugin_class()

        raise ValueError(f"Unknown plugin: {plugin_id}")

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> tuple[cls, list[str]]:
        """
        从 YAML 配置加载

        Returns:
            (registry, errors)
        """
        registry = cls()

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            plugins = config.get("plugins", [])
            errors = []

            for plugin_config in plugins:
                try:
                    config_obj = PluginConfig(**plugin_config)
                    registry.register(None, config_obj)
                except Exception as e:
                    errors.append(f"{plugin_config.get('name', 'unknown')}: {e}")

            return registry, errors

        except Exception as e:
            return registry, [f"Failed to load config: {e}"]


class PluginContext:
    """插件上下文"""

    def __init__(
        self,
        registry: PluginRegistry,
        plugin_id: str,
    ):
        self.registry = registry
        self.plugin_id = plugin_id
        self._shared_data: dict = {}

    def get_plugin(self) -> Plugin | None:
        """获取插件"""
        return self.registry.get_plugin(self.plugin_id)

    def get_interface(self) -> PluginInterface | None:
        """获取插件接口"""
        return self.registry.get_interface(self.plugin_id)

    def set_shared_data(self, key: str, value: Any):
        """设置共享数据"""
        self._shared_data[key] = value

    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """获取共享数据"""
        return self._shared_data.get(key, default)

    def get_other_plugin(self, plugin_id: str) -> Plugin | None:
        """获取其他插件"""
        return self.registry.get_plugin(plugin_id)
