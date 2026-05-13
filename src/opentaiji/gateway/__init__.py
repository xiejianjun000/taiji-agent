"""
消息网关模块
"""

from opentaiji.gateway.core import (
    MessageGateway,
    PlatformAdapter,
    Message,
    OutgoingMessage,
    MessagePlatform,
    create_gateway,
    TelegramAdapter,
    DiscordAdapter,
    WeChatWorkAdapter,
    DingTalkAdapter,
    FeishuAdapter,
)

__all__ = [
    "MessageGateway",
    "PlatformAdapter", 
    "Message",
    "OutgoingMessage",
    "MessagePlatform",
    "create_gateway",
    "TelegramAdapter",
    "DiscordAdapter",
    "WeChatWorkAdapter",
    "DingTalkAdapter",
    "FeishuAdapter",
]
