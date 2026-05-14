#!/usr/bin/env python3
"""
govmcp.protocol.authorization — 授权扩展 (MCP 2025.11)

提供 OAuth 2.0 授权流程和细粒度权限控制支持：
- OAuth 2.0 授权码流程
- Authorization Extensions
- 细粒度权限控制
- 令牌管理
"""

from __future__ import annotations

import hashlib
import json
import secrets
import threading
import time
import urllib.parse
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union


class GrantType(str, Enum):
    """授权类型"""

    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    IMPLICIT = "implicit"


class TokenType(str, Enum):
    """令牌类型"""

    BEARER = "bearer"
    MAC = "mac"


class AuthorizationScope(str, Enum):
    """授权范围"""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    EXECUTE = "execute"
    READ_RESOURCES = "resources:read"
    WRITE_RESOURCES = "resources:write"
    READ_TOOLS = "tools:read"
    WRITE_TOOLS = "tools:write"
    READ_PROMPTS = "prompts:read"
    WRITE_PROMPTS = "prompts:write"


@dataclass
class ClientInfo:
    """OAuth 客户端信息"""

    client_id: str
    client_secret: str | None = None
    client_name: str = ""
    redirect_uris: list[str] = field(default_factory=list)
    allowed_scopes: set[str] = field(default_factory=set)
    grant_types: set[GrantType] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "redirect_uris": self.redirect_uris,
            "allowed_scopes": list(self.allowed_scopes),
            "grant_types": [g.value for g in self.grant_types],
            "metadata": self.metadata,
        }


@dataclass
class AuthorizationCode:
    """授权码"""

    code: str
    client_id: str
    redirect_uri: str
    scopes: set[str]
    user_id: str
    code_challenge: str | None = None
    code_challenge_method: str | None = None
    expires_at: float = field(default_factory=lambda: time.time() + 600)
    used: bool = False

    def is_valid(self) -> bool:
        """检查是否有效"""
        return not self.used and time.time() < self.expires_at

    def mark_used(self) -> None:
        """标记为已使用"""
        self.used = True


@dataclass
class TokenInfo:
    """令牌信息"""

    access_token: str
    token_type: TokenType | str
    expires_in: int
    refresh_token: str | None = None
    scope: str | None = None
    client_id: str | None = None
    user_id: str | None = None
    issued_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> float:
        """检查是否过期"""
        return time.time() > (self.issued_at + self.expires_in)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type.value
            if isinstance(self.token_type, TokenType)
            else self.token_type,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TokenInfo:
        """从字典创建"""
        return cls(
            access_token=data.get("access_token", ""),
            token_type=data.get("token_type", TokenType.BEARER),
            expires_in=data.get("expires_in", 3600),
            refresh_token=data.get("refresh_token"),
            scope=data.get("scope"),
            client_id=data.get("client_id"),
            user_id=data.get("user_id"),
            issued_at=data.get("issued_at", time.time()),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Permission:
    """权限"""

    resource: str
    actions: set[str]
    conditions: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        result = {
            "resource": self.resource,
            "actions": list(self.actions),
        }
        if self.conditions:
            result["conditions"] = self.conditions
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Permission:
        """从字典创建"""
        return cls(
            resource=data.get("resource", ""),
            actions=set(data.get("actions", [])),
            conditions=data.get("conditions"),
        )


@dataclass
class AuthorizationGrant:
    """授权授予"""

    grant_id: str
    user_id: str
    client_id: str
    scopes: set[str]
    permissions: list[Permission]
    issued_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """检查是否有效"""
        if self.expires_at and time.time() > self.expires_at:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "grant_id": self.grant_id,
            "user_id": self.user_id,
            "client_id": self.client_id,
            "scopes": list(self.scopes),
            "permissions": [p.to_dict() for p in self.permissions],
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "metadata": self.metadata,
        }


class AuthorizationManager:
    """
    授权管理器

    管理 OAuth 2.0 授权流程和细粒度权限控制。
    """

    def __init__(
        self,
        access_token_ttl: int = 3600,
        refresh_token_ttl: int = 86400 * 7,
        authorization_code_ttl: int = 600,
    ):
        self._clients: dict[str, ClientInfo] = {}
        self._authorization_codes: dict[str, AuthorizationCode] = {}
        self._tokens: dict[str, TokenInfo] = {}
        self._refresh_tokens: dict[str, TokenInfo] = {}
        self._grants: dict[str, AuthorizationGrant] = {}
        self._user_grants: dict[str, list[str]] = {}
        self._lock = threading.RLock()

        self._access_token_ttl = access_token_ttl
        self._refresh_token_ttl = refresh_token_ttl
        self._authorization_code_ttl = authorization_code_ttl

        self._token_generator = secrets.token_urlsafe
        self._authorization_hooks: list[Callable[[str, dict[str, Any]], bool]] = []

    def register_client(
        self,
        client_id: str,
        client_secret: str | None = None,
        client_name: str = "",
        redirect_uris: list[str] | None = None,
        allowed_scopes: set[str] | None = None,
        grant_types: set[GrantType] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ClientInfo:
        """注册客户端"""
        client = ClientInfo(
            client_id=client_id,
            client_secret=client_secret,
            client_name=client_name or client_id,
            redirect_uris=redirect_uris or [],
            allowed_scopes=allowed_scopes or set(),
            grant_types=grant_types or {GrantType.AUTHORIZATION_CODE},
            metadata=metadata or {},
        )
        with self._lock:
            self._clients[client_id] = client
        return client

    def get_client(self, client_id: str) -> ClientInfo | None:
        """获取客户端信息"""
        with self._lock:
            return self._clients.get(client_id)

    def validate_client(self, client_id: str, client_secret: str | None = None) -> bool:
        """验证客户端凭证"""
        with self._lock:
            client = self._clients.get(client_id)
            if not client:
                return False
            if client.client_secret is None:
                return True
            return client.client_secret == client_secret

    def create_authorization_url(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str | None = None,
        state: str | None = None,
        code_challenge: str | None = None,
        code_challenge_method: str | None = None,
    ) -> str:
        """
        创建授权 URL

        Args:
            client_id: 客户端 ID
            redirect_uri: 回调 URI
            scope: 授权范围
            state: 状态参数
            code_challenge: PKCE 挑战
            code_challenge_method: PKCE 方法

        Returns:
            授权 URL
        """
        with self._lock:
            client = self._clients.get(client_id)
            if not client:
                raise ValueError(f"Client not found: {client_id}")

            if redirect_uri not in client.redirect_uris:
                raise ValueError(f"Invalid redirect_uri: {redirect_uri}")

            requested_scopes = set(scope.split()) if scope else set()
            if not requested_scopes.issubset(client.allowed_scopes):
                invalid = requested_scopes - client.allowed_scopes
                raise ValueError(f"Invalid scopes: {invalid}")

            code = self._token_generator(32)

            authorization_code = AuthorizationCode(
                code=code,
                client_id=client_id,
                redirect_uri=redirect_uri,
                scopes=requested_scopes,
                user_id="",
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
                expires_at=time.time() + self._authorization_code_ttl,
            )
            self._authorization_codes[code] = authorization_code

        params = {"response_type": "code", "client_id": client_id}
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if scope:
            params["scope"] = scope
        if state:
            params["state"] = state
        if code_challenge:
            params["code_challenge"] = code_challenge
        if code_challenge_method:
            params["code_challenge_method"] = code_challenge_method

        return f"/authorize?{urllib.parse.urlencode(params)}"

    def authorize(
        self,
        code: str,
        user_id: str,
    ) -> bool:
        """
        用户授权确认

        Args:
            code: 授权码
            user_id: 用户 ID

        Returns:
            是否授权成功
        """
        with self._lock:
            auth_code = self._authorization_codes.get(code)
            if not auth_code or not auth_code.is_valid():
                return False

            auth_code.user_id = user_id
            return True

    def exchange_code(
        self,
        code: str,
        client_id: str,
        client_secret: str | None = None,
        code_verifier: str | None = None,
    ) -> TokenInfo:
        """
        交换授权码获取令牌

        Args:
            code: 授权码
            client_id: 客户端 ID
            client_secret: 客户端密钥
            code_verifier: PKCE 验证器

        Returns:
            令牌信息

        Raises:
            ValueError: 交换失败
        """
        with self._lock:
            if not self.validate_client(client_id, client_secret):
                raise ValueError("Invalid client credentials")

            auth_code = self._authorization_codes.get(code)
            if not auth_code or not auth_code.is_valid():
                raise ValueError("Invalid or expired authorization code")

            if auth_code.client_id != client_id:
                raise ValueError("Client mismatch")

            if code_verifier and auth_code.code_challenge:
                if not self._verify_pkce(
                    code_verifier, auth_code.code_challenge, auth_code.code_challenge_method
                ):
                    raise ValueError("Invalid code verifier")

            auth_code.mark_used()

            access_token = self._token_generator(32)
            refresh_token = self._token_generator(32)

            token_info = TokenInfo(
                access_token=access_token,
                token_type=TokenType.BEARER,
                expires_in=self._access_token_ttl,
                refresh_token=refresh_token,
                scope=" ".join(auth_code.scopes),
                client_id=client_id,
                user_id=auth_code.user_id,
            )
            self._tokens[access_token] = token_info

            refresh_info = TokenInfo(
                access_token=refresh_token,
                token_type=TokenType.BEARER,
                expires_in=self._refresh_token_ttl,
                scope=" ".join(auth_code.scopes),
                client_id=client_id,
                user_id=auth_code.user_id,
            )
            self._refresh_tokens[refresh_token] = refresh_info

            grant_id = self._token_generator(16)
            grant = AuthorizationGrant(
                grant_id=grant_id,
                user_id=auth_code.user_id,
                client_id=client_id,
                scopes=auth_code.scopes,
                permissions=[],
                metadata={"original_code": code},
            )
            self._grants[grant_id] = grant

            if auth_code.user_id not in self._user_grants:
                self._user_grants[auth_code.user_id] = []
            self._user_grants[auth_code.user_id].append(grant_id)

            return token_info

    def refresh_access_token(
        self,
        refresh_token: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        scope: str | None = None,
    ) -> TokenInfo:
        """
        刷新访问令牌

        Args:
            refresh_token: 刷新令牌
            client_id: 客户端 ID
            client_secret: 客户端密钥
            scope: 新范围

        Returns:
            新令牌信息
        """
        with self._lock:
            old_token = self._refresh_tokens.get(refresh_token)
            if not old_token:
                raise ValueError("Invalid refresh token")

            if client_id and old_token.client_id != client_id:
                raise ValueError("Client mismatch")

            if not self.validate_client(old_token.client_id, client_secret):
                raise ValueError("Invalid client credentials")

            requested_scopes = (
                set(scope.split())
                if scope
                else set(
                    auth_code.scopes
                    if (auth_code := self._authorization_codes.get(refresh_token))
                    else old_token.scope.split()
                )
            )
            allowed_scopes = self._clients.get(
                old_token.client_id, ClientInfo(client_id=old_token.client_id)
            ).allowed_scopes
            if not requested_scopes.issubset(allowed_scopes):
                requested_scopes = requested_scopes & allowed_scopes

            access_token = self._token_generator(32)
            new_refresh = self._token_generator(32)

            new_token = TokenInfo(
                access_token=access_token,
                token_type=TokenType.BEARER,
                expires_in=self._access_token_ttl,
                refresh_token=new_refresh,
                scope=" ".join(requested_scopes),
                client_id=old_token.client_id,
                user_id=old_token.user_id,
            )
            self._tokens[access_token] = new_token

            new_refresh_info = TokenInfo(
                access_token=new_refresh,
                token_type=TokenType.BEARER,
                expires_in=self._refresh_token_ttl,
                scope=" ".join(requested_scopes),
                client_id=old_token.client_id,
                user_id=old_token.user_id,
            )
            self._refresh_tokens[new_refresh] = new_refresh_info
            del self._refresh_tokens[refresh_token]

            return new_token

    def validate_token(self, access_token: str) -> TokenInfo | None:
        """验证访问令牌"""
        with self._lock:
            token = self._tokens.get(access_token)
            if not token:
                return None
            if token.is_expired():
                return None
            return token

    def revoke_token(self, token: str) -> bool:
        """撤销令牌"""
        with self._lock:
            if token in self._tokens:
                del self._tokens[token]
                return True
            if token in self._refresh_tokens:
                del self._refresh_tokens[token]
                return True
            return False

    def add_authorization_hook(
        self,
        hook: Callable[[str, dict[str, Any]], bool],
    ) -> None:
        """添加授权钩子"""
        self._authorization_hooks.append(hook)

    def check_permission(
        self,
        token: str,
        resource: str,
        action: str,
    ) -> bool:
        """
        检查权限

        Args:
            token: 访问令牌
            resource: 资源
            action: 操作

        Returns:
            是否有权限
        """
        token_info = self.validate_token(token)
        if not token_info:
            return False

        with self._lock:
            user_grants = self._user_grants.get(token_info.user_id, [])
            for grant_id in user_grants:
                grant = self._grants.get(grant_id)
                if not grant or not grant.is_valid():
                    continue

                if GrantType.READ.value in grant.scopes or GrantType.ADMIN.value in grant.scopes:
                    return True

                for perm in grant.permissions:
                    if perm.resource == resource or perm.resource == "*":
                        if action in perm.actions or "*" in perm.actions:
                            return True

        for hook in self._authorization_hooks:
            try:
                if not hook(token_info.user_id, {"resource": resource, "action": action}):
                    return False
            except Exception:
                pass

        return False

    def grant_permissions(
        self,
        grant_id: str,
        permissions: list[Permission],
    ) -> bool:
        """授予权限"""
        with self._lock:
            grant = self._grants.get(grant_id)
            if not grant:
                return False
            grant.permissions.extend(permissions)
            return True

    def revoke_permissions(
        self,
        grant_id: str,
        resources: list[str] | None = None,
    ) -> bool:
        """撤销权限"""
        with self._lock:
            grant = self._grants.get(grant_id)
            if not grant:
                return False

            if resources:
                grant.permissions = [p for p in grant.permissions if p.resource not in resources]
            else:
                grant.permissions.clear()
            return True

    def cleanup_expired(self) -> int:
        """清理过期数据"""
        now = time.time()
        removed = 0

        with self._lock:
            expired_codes = [
                code for code, auth in self._authorization_codes.items() if now > auth.expires_at
            ]
            for code in expired_codes:
                del self._authorization_codes[code]
                removed += 1

            expired_tokens = [token for token, info in self._tokens.items() if info.is_expired()]
            for token in expired_tokens:
                del self._tokens[token]
                removed += 1

            expired_refresh = [
                token for token, info in self._refresh_tokens.items() if info.is_expired()
            ]
            for token in expired_refresh:
                del self._refresh_tokens[token]
                removed += 1

            expired_grants = [gid for gid, grant in self._grants.items() if not grant.is_valid()]
            for gid in expired_grants:
                del self._grants[gid]
                removed += 1

        return removed

    def _verify_pkce(
        self,
        verifier: str,
        challenge: str,
        method: str | None,
    ) -> bool:
        """验证 PKCE"""
        if method == "S256":
            challenge_calc = hashlib.sha256(verifier.encode()).digest()
            challenge_calc = urllib.parse.quote(challenge_calc)
            return challenge_calc == challenge
        elif method == "plain":
            return verifier == challenge
        return False

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            return {
                "clients": len(self._clients),
                "authorization_codes": len(self._authorization_codes),
                "active_tokens": len(self._tokens),
                "refresh_tokens": len(self._refresh_tokens),
                "grants": len(self._grants),
                "user_grants": len(self._user_grants),
            }


class FineGrainedPermissionManager:
    """细粒度权限管理器"""

    def __init__(self, authorization_manager: AuthorizationManager):
        self._auth_manager = authorization_manager
        self._policies: dict[str, list[dict[str, Any]]] = {}
        self._lock = threading.RLock()

    def add_policy(
        self,
        policy_id: str,
        effect: str,
        principals: list[str],
        resources: list[str],
        actions: list[str],
        conditions: dict[str, Any] | None = None,
    ) -> None:
        """
        添加策略

        Args:
            policy_id: 策略 ID
            effect: 效果 (allow/deny)
            principals: 主体列表
            resources: 资源列表
            actions: 操作列表
            conditions: 条件
        """
        with self._lock:
            if policy_id not in self._policies:
                self._policies[policy_id] = []
            self._policies[policy_id].append(
                {
                    "effect": effect,
                    "principals": principals,
                    "resources": resources,
                    "actions": actions,
                    "conditions": conditions or {},
                }
            )

    def evaluate(
        self,
        principal: str,
        resource: str,
        action: str,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        评估权限

        Args:
            principal: 主体
            resource: 资源
            action: 操作
            context: 上下文

        Returns:
            是否允许
        """
        context = context or {}

        with self._lock:
            for policies in self._policies.values():
                for policy in policies:
                    if self._match_principal(policy, principal):
                        if self._match_resource(policy, resource):
                            if self._match_action(policy, action):
                                if self._match_conditions(policy, context):
                                    return policy["effect"] == "allow"

        return False

    def _match_principal(self, policy: dict[str, Any], principal: str) -> bool:
        """匹配主体"""
        for p in policy["principals"]:
            if p == principal or p == "*":
                return True
        return False

    def _match_resource(self, policy: dict[str, Any], resource: str) -> bool:
        """匹配资源"""
        for r in policy["resources"]:
            if r == resource or r == "*" or resource.startswith(r.rstrip("*")):
                return True
        return False

    def _match_action(self, policy: dict[str, Any], action: str) -> bool:
        """匹配操作"""
        for a in policy["actions"]:
            if a == action or a == "*":
                return True
        return False

    def _match_conditions(self, policy: dict[str, Any], context: dict[str, Any]) -> bool:
        """匹配条件"""
        conditions = policy.get("conditions", {})
        for key, value in conditions.items():
            if key not in context:
                return False
            if context[key] != value:
                return False
        return True

    def remove_policy(self, policy_id: str) -> bool:
        """移除策略"""
        with self._lock:
            if policy_id in self._policies:
                del self._policies[policy_id]
                return True
            return False

    def get_policies(self, policy_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        """获取策略"""
        with self._lock:
            if policy_id:
                return {policy_id: self._policies.get(policy_id, [])}
            return dict(self._policies)
