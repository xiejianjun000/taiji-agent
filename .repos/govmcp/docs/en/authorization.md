# protocol.authorization

```include ../govmcp/protocol/authorization.py
```

## Module Documentation

govmcp.protocol.authorization — 授权扩展 (MCP 2025.11)

提供 OAuth 2.0 授权流程和细粒度权限控制支持：

- OAuth 2.0 授权码流程

- Authorization Extensions

- 细粒度权限控制

- 令牌管理

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| - | - | - |

## Exported Classes

### `GrantType`

`Enum Class`  

`Line: 25`  

**Base Classes:** `str | Enum`

授权类型

---

### `TokenType`

`Enum Class`  

`Line: 34`  

**Base Classes:** `str | Enum`

令牌类型

---

### `AuthorizationScope`

`Enum Class`  

`Line: 41`  

**Base Classes:** `str | Enum`

授权范围

---

### `ClientInfo`

`Dataclass`  

`Line: 57`  

OAuth 客户端信息

#### Attributes

| Name | Type |
|:---|:---|
| `client_id` | `str` |
| `client_secret` | `Optional[str]` |
| `client_name` | `str` |
| `redirect_uris` | `List[str]` |
| `allowed_scopes` | `Set[str]` |
| `grant_types` | `Set[GrantType]` |
| `metadata` | `Dict[str, Any]` |

#### Decorators

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:68` `Complexity:Low`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

---

### `AuthorizationCode`

`Dataclass`  

`Line: 81`  

授权码

#### Attributes

| Name | Type |
|:---|:---|
| `code` | `str` |
| `client_id` | `str` |
| `redirect_uri` | `str` |
| `scopes` | `Set[str]` |
| `user_id` | `str` |
| `code_challenge` | `Optional[str]` |
| `code_challenge_method` | `Optional[str]` |
| `expires_at` | `float` |
| `used` | `bool` |

#### Decorators

### `is_valid(self: Any) -> bool`

`Line:94` `Complexity:Low`

检查是否有效

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `mark_used(self: Any) -> None`

`Line:98` `Complexity:Low`

标记为已使用

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`None`

---

---

### `TokenInfo`

`Dataclass`  

`Line: 104`  

令牌信息

#### Attributes

| Name | Type |
|:---|:---|
| `access_token` | `str` |
| `token_type` | `Union[TokenType, str]` |
| `expires_in` | `int` |
| `refresh_token` | `Optional[str]` |
| `scope` | `Optional[str]` |
| `client_id` | `Optional[str]` |
| `user_id` | `Optional[str]` |
| `issued_at` | `float` |
| `metadata` | `Dict[str, Any]` |

#### Decorators

### `is_expired(self: Any) -> float`

`Line:117` `Complexity:Low`

检查是否过期

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`float`

---

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:121` `Complexity:Low`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'TokenInfo'`

`Line:134` `Complexity:Low`

从字典创建

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`'TokenInfo'`

---

---

### `Permission`

`Dataclass`  

`Line: 150`  

权限

#### Attributes

| Name | Type |
|:---|:---|
| `resource` | `str` |
| `actions` | `Set[str]` |
| `conditions` | `Optional[Dict[str, Any]]` |

#### Decorators

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:157` `Complexity:Low`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'Permission'`

`Line:168` `Complexity:Low`

从字典创建

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### Returns

`'Permission'`

---

---

### `AuthorizationGrant`

`Dataclass`  

`Line: 178`  

授权授予

#### Attributes

| Name | Type |
|:---|:---|
| `grant_id` | `str` |
| `user_id` | `str` |
| `client_id` | `str` |
| `scopes` | `Set[str]` |
| `permissions` | `List[Permission]` |
| `issued_at` | `float` |
| `expires_at` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

#### Decorators

### `is_valid(self: Any) -> bool`

`Line:190` `Complexity:Low`

检查是否有效

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`bool`

---

### `to_dict(self: Any) -> Dict[str, Any]`

`Line:196` `Complexity:Low`

转换为字典

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

---

### `AuthorizationManager`

`Line: 210`  

授权管理器

管理 OAuth 2.0 授权流程和细粒度权限控制。

#### Attributes

| Name | Type |
|:---|:---|
| `access_token_ttl` | `int` |
| `refresh_token_ttl` | `int` |
| `authorization_code_ttl` | `int` |

#### Decorators

### `register_client(self: Any, client_id: str, client_secret: Optional[str] = None, client_name: str = '', redirect_uris: Optional[List[str]] = None, allowed_scopes: Optional[Set[str]] = None, grant_types: Optional[Set[GrantType]] = None, metadata: Optional[Dict[str, Any]] = None) -> ClientInfo`

`Line:238` `Complexity:Low`

注册客户端

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `client_id` | `str` | `-` |
| `client_secret` (Optional) | `Optional[str]` | `None` |
| `client_name` (Optional) | `str` | `''` |
| `redirect_uris` (Optional) | `Optional[List[str]]` | `None` |
| `allowed_scopes` (Optional) | `Optional[Set[str]]` | `None` |
| `grant_types` (Optional) | `Optional[Set[GrantType]]` | `None` |
| `metadata` (Optional) | `Optional[Dict[str, Any]]` | `None` |

#### Returns

`ClientInfo`

---

### `get_client(self: Any, client_id: str) -> Optional[ClientInfo]`

`Line:262` `Complexity:Low`

获取客户端信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `client_id` | `str` | `-` |

#### Returns

`Optional[ClientInfo]`

---

### `validate_client(self: Any, client_id: str, client_secret: Optional[str] = None) -> bool`

`Line:267` `Complexity:Low`

验证客户端凭证

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `client_id` | `str` | `-` |
| `client_secret` (Optional) | `Optional[str]` | `None` |

#### Returns

`bool`

---

### `create_authorization_url(self: Any, client_id: str, redirect_uri: str, scope: Optional[str] = None, state: Optional[str] = None, code_challenge: Optional[str] = None, code_challenge_method: Optional[str] = None) -> str`

`Line:277` `Complexity:High`

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

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `client_id` | `str` | `-` |
| `redirect_uri` | `str` | `-` |
| `scope` (Optional) | `Optional[str]` | `None` |
| `state` (Optional) | `Optional[str]` | `None` |
| `code_challenge` (Optional) | `Optional[str]` | `None` |
| `code_challenge_method` (Optional) | `Optional[str]` | `None` |

#### Returns

`str`

---

### `authorize(self: Any, code: str, user_id: str) -> bool`

`Line:341` `Complexity:Low`

用户授权确认

Args:

    code: 授权码

    user_id: 用户 ID

Returns:

    是否授权成功

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `code` | `str` | `-` |
| `user_id` | `str` | `-` |

#### Returns

`bool`

---

### `exchange_code(self: Any, code: str, client_id: str, client_secret: Optional[str] = None, code_verifier: Optional[str] = None) -> TokenInfo`

`Line:364` `Complexity:Medium`

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

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `code` | `str` | `-` |
| `client_id` | `str` | `-` |
| `client_secret` (Optional) | `Optional[str]` | `None` |
| `code_verifier` (Optional) | `Optional[str]` | `None` |

#### Returns

`TokenInfo`

---

### `refresh_access_token(self: Any, refresh_token: str, client_id: Optional[str] = None, client_secret: Optional[str] = None, scope: Optional[str] = None) -> TokenInfo`

`Line:446` `Complexity:Medium`

刷新访问令牌

Args:

    refresh_token: 刷新令牌

    client_id: 客户端 ID

    client_secret: 客户端密钥

    scope: 新范围

Returns:

    新令牌信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `refresh_token` | `str` | `-` |
| `client_id` (Optional) | `Optional[str]` | `None` |
| `client_secret` (Optional) | `Optional[str]` | `None` |
| `scope` (Optional) | `Optional[str]` | `None` |

#### Returns

`TokenInfo`

---

### `validate_token(self: Any, access_token: str) -> Optional[TokenInfo]`

`Line:518` `Complexity:Low`

验证访问令牌

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `access_token` | `str` | `-` |

#### Returns

`Optional[TokenInfo]`

---

### `revoke_token(self: Any, token: str) -> bool`

`Line:528` `Complexity:Low`

撤销令牌

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `token` | `str` | `-` |

#### Returns

`bool`

---

### `add_authorization_hook(self: Any, hook: Callable[[str, Dict[str, Any]], bool]) -> None`

`Line:539` `Complexity:Low`

添加授权钩子

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `hook` | `Callable[[str, Dict[str, Any]], bool]` | `-` |

#### Returns

`None`

---

### `check_permission(self: Any, token: str, resource: str, action: str) -> bool`

`Line:546` `Complexity:High`

检查权限

Args:

    token: 访问令牌

    resource: 资源

    action: 操作

Returns:

    是否有权限

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `token` | `str` | `-` |
| `resource` | `str` | `-` |
| `action` | `str` | `-` |

#### Returns

`bool`

---

### `grant_permissions(self: Any, grant_id: str, permissions: List[Permission]) -> bool`

`Line:591` `Complexity:Low`

授予权限

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `grant_id` | `str` | `-` |
| `permissions` | `List[Permission]` | `-` |

#### Returns

`bool`

---

### `revoke_permissions(self: Any, grant_id: str, resources: Optional[List[str]] = None) -> bool`

`Line:604` `Complexity:Low`

撤销权限

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `grant_id` | `str` | `-` |
| `resources` (Optional) | `Optional[List[str]]` | `None` |

#### Returns

`bool`

---

### `cleanup_expired(self: Any) -> int`

`Line:621` `Complexity:Medium`

清理过期数据

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`int`

---

### `_verify_pkce(self: Any, verifier: str, challenge: str, method: Optional[str]) -> bool`

`Line:653` `Complexity:Low`

验证 PKCE

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `verifier` | `str` | `-` |
| `challenge` | `str` | `-` |
| `method` | `Optional[str]` | `-` |

#### Returns

`bool`

---

### `get_stats(self: Any) -> Dict[str, Any]`

`Line:668` `Complexity:Low`

获取统计信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### Returns

`Dict[str, Any]`

---

---

### `FineGrainedPermissionManager`

`Line: 681`  

细粒度权限管理器

#### Attributes

| Name | Type |
|:---|:---|
| `authorization_manager` | `AuthorizationManager` |

#### Decorators

### `add_policy(self: Any, policy_id: str, effect: str, principals: List[str], resources: List[str], actions: List[str], conditions: Optional[Dict[str, Any]] = None) -> None`

`Line:689` `Complexity:Low`

添加策略

Args:

    policy_id: 策略 ID

    effect: 效果 (allow/deny)

    principals: 主体列表

    resources: 资源列表

    actions: 操作列表

    conditions: 条件

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy_id` | `str` | `-` |
| `effect` | `str` | `-` |
| `principals` | `List[str]` | `-` |
| `resources` | `List[str]` | `-` |
| `actions` | `List[str]` | `-` |
| `conditions` (Optional) | `Optional[Dict[str, Any]]` | `None` |

#### Returns

`None`

---

### `evaluate(self: Any, principal: str, resource: str, action: str, context: Optional[Dict[str, Any]] = None) -> bool`

`Line:722` `Complexity:Medium`

评估权限

Args:

    principal: 主体

    resource: 资源

    action: 操作

    context: 上下文

Returns:

    是否允许

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `principal` | `str` | `-` |
| `resource` | `str` | `-` |
| `action` | `str` | `-` |
| `context` (Optional) | `Optional[Dict[str, Any]]` | `None` |

#### Returns

`bool`

---

### `_match_principal(self: Any, policy: Dict[str, Any], principal: str) -> bool`

`Line:754` `Complexity:Low`

匹配主体

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy` | `Dict[str, Any]` | `-` |
| `principal` | `str` | `-` |

#### Returns

`bool`

---

### `_match_resource(self: Any, policy: Dict[str, Any], resource: str) -> bool`

`Line:761` `Complexity:Low`

匹配资源

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy` | `Dict[str, Any]` | `-` |
| `resource` | `str` | `-` |

#### Returns

`bool`

---

### `_match_action(self: Any, policy: Dict[str, Any], action: str) -> bool`

`Line:768` `Complexity:Low`

匹配操作

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy` | `Dict[str, Any]` | `-` |
| `action` | `str` | `-` |

#### Returns

`bool`

---

### `_match_conditions(self: Any, policy: Dict[str, Any], context: Dict[str, Any]) -> bool`

`Line:775` `Complexity:Medium`

匹配条件

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy` | `Dict[str, Any]` | `-` |
| `context` | `Dict[str, Any]` | `-` |

#### Returns

`bool`

---

### `remove_policy(self: Any, policy_id: str) -> bool`

`Line:785` `Complexity:Low`

移除策略

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy_id` | `str` | `-` |

#### Returns

`bool`

---

### `get_policies(self: Any, policy_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]`

`Line:793` `Complexity:Low`

获取策略

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy_id` (Optional) | `Optional[str]` | `None` |

#### Returns

`Dict[str, List[Dict[str, Any]]]`

---

---

## Test Coverage

*No specific tests found for this module.*
