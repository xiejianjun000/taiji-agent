# protocol.authorization

```include ../govmcp/protocol/authorization.py
```

## 模块文档

govmcp.protocol.authorization — 授权扩展 (MCP 2025.11)

提供 OAuth 2.0 授权流程和细粒度权限控制支持：

- OAuth 2.0 授权码流程

- Authorization Extensions

- 细粒度权限控制

- 令牌管理

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| - | - | - |

## 导出类

### `GrantType`

`枚举类`  

`行号: 25`  

**基类:** `str | Enum`

授权类型

---

### `TokenType`

`枚举类`  

`行号: 34`  

**基类:** `str | Enum`

令牌类型

---

### `AuthorizationScope`

`枚举类`  

`行号: 41`  

**基类:** `str | Enum`

授权范围

---

### `ClientInfo`

`数据类`  

`行号: 57`  

OAuth 客户端信息

#### 属性

| Name | Type |
|:---|:---|
| `client_id` | `str` |
| `client_secret` | `Optional[str]` |
| `client_name` | `str` |
| `redirect_uris` | `List[str]` |
| `allowed_scopes` | `Set[str]` |
| `grant_types` | `Set[GrantType]` |
| `metadata` | `Dict[str, Any]` |

#### 装饰器

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:68` `复杂度:低`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

---

### `AuthorizationCode`

`数据类`  

`行号: 81`  

授权码

#### 属性

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

#### 装饰器

### `is_valid(self: Any) -> bool`

`行号:94` `复杂度:低`

检查是否有效

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `mark_used(self: Any) -> None`

`行号:98` `复杂度:低`

标记为已使用

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`None`

---

---

### `TokenInfo`

`数据类`  

`行号: 104`  

令牌信息

#### 属性

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

#### 装饰器

### `is_expired(self: Any) -> float`

`行号:117` `复杂度:低`

检查是否过期

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`float`

---

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:121` `复杂度:低`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'TokenInfo'`

`行号:134` `复杂度:低`

从字典创建

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`'TokenInfo'`

---

---

### `Permission`

`数据类`  

`行号: 150`  

权限

#### 属性

| Name | Type |
|:---|:---|
| `resource` | `str` |
| `actions` | `Set[str]` |
| `conditions` | `Optional[Dict[str, Any]]` |

#### 装饰器

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:157` `复杂度:低`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

### `from_dict(cls: Any, data: Dict[str, Any]) -> 'Permission'`

`行号:168` `复杂度:低`

从字典创建

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `cls` | `Any` | `-` |
| `data` | `Dict[str, Any]` | `-` |

#### 返回

`'Permission'`

---

---

### `AuthorizationGrant`

`数据类`  

`行号: 178`  

授权授予

#### 属性

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

#### 装饰器

### `is_valid(self: Any) -> bool`

`行号:190` `复杂度:低`

检查是否有效

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`bool`

---

### `to_dict(self: Any) -> Dict[str, Any]`

`行号:196` `复杂度:低`

转换为字典

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

---

### `AuthorizationManager`

`行号: 210`  

授权管理器

管理 OAuth 2.0 授权流程和细粒度权限控制。

#### 属性

| Name | Type |
|:---|:---|
| `access_token_ttl` | `int` |
| `refresh_token_ttl` | `int` |
| `authorization_code_ttl` | `int` |

#### 装饰器

### `register_client(self: Any, client_id: str, client_secret: Optional[str] = None, client_name: str = '', redirect_uris: Optional[List[str]] = None, allowed_scopes: Optional[Set[str]] = None, grant_types: Optional[Set[GrantType]] = None, metadata: Optional[Dict[str, Any]] = None) -> ClientInfo`

`行号:238` `复杂度:低`

注册客户端

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `client_id` | `str` | `-` |
| `client_secret` (可选) | `Optional[str]` | `None` |
| `client_name` (可选) | `str` | `''` |
| `redirect_uris` (可选) | `Optional[List[str]]` | `None` |
| `allowed_scopes` (可选) | `Optional[Set[str]]` | `None` |
| `grant_types` (可选) | `Optional[Set[GrantType]]` | `None` |
| `metadata` (可选) | `Optional[Dict[str, Any]]` | `None` |

#### 返回

`ClientInfo`

---

### `get_client(self: Any, client_id: str) -> Optional[ClientInfo]`

`行号:262` `复杂度:低`

获取客户端信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `client_id` | `str` | `-` |

#### 返回

`Optional[ClientInfo]`

---

### `validate_client(self: Any, client_id: str, client_secret: Optional[str] = None) -> bool`

`行号:267` `复杂度:低`

验证客户端凭证

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `client_id` | `str` | `-` |
| `client_secret` (可选) | `Optional[str]` | `None` |

#### 返回

`bool`

---

### `create_authorization_url(self: Any, client_id: str, redirect_uri: str, scope: Optional[str] = None, state: Optional[str] = None, code_challenge: Optional[str] = None, code_challenge_method: Optional[str] = None) -> str`

`行号:277` `复杂度:高`

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

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `client_id` | `str` | `-` |
| `redirect_uri` | `str` | `-` |
| `scope` (可选) | `Optional[str]` | `None` |
| `state` (可选) | `Optional[str]` | `None` |
| `code_challenge` (可选) | `Optional[str]` | `None` |
| `code_challenge_method` (可选) | `Optional[str]` | `None` |

#### 返回

`str`

---

### `authorize(self: Any, code: str, user_id: str) -> bool`

`行号:341` `复杂度:低`

用户授权确认

Args:

    code: 授权码

    user_id: 用户 ID

Returns:

    是否授权成功

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `code` | `str` | `-` |
| `user_id` | `str` | `-` |

#### 返回

`bool`

---

### `exchange_code(self: Any, code: str, client_id: str, client_secret: Optional[str] = None, code_verifier: Optional[str] = None) -> TokenInfo`

`行号:364` `复杂度:中`

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

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `code` | `str` | `-` |
| `client_id` | `str` | `-` |
| `client_secret` (可选) | `Optional[str]` | `None` |
| `code_verifier` (可选) | `Optional[str]` | `None` |

#### 返回

`TokenInfo`

---

### `refresh_access_token(self: Any, refresh_token: str, client_id: Optional[str] = None, client_secret: Optional[str] = None, scope: Optional[str] = None) -> TokenInfo`

`行号:446` `复杂度:中`

刷新访问令牌

Args:

    refresh_token: 刷新令牌

    client_id: 客户端 ID

    client_secret: 客户端密钥

    scope: 新范围

Returns:

    新令牌信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `refresh_token` | `str` | `-` |
| `client_id` (可选) | `Optional[str]` | `None` |
| `client_secret` (可选) | `Optional[str]` | `None` |
| `scope` (可选) | `Optional[str]` | `None` |

#### 返回

`TokenInfo`

---

### `validate_token(self: Any, access_token: str) -> Optional[TokenInfo]`

`行号:518` `复杂度:低`

验证访问令牌

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `access_token` | `str` | `-` |

#### 返回

`Optional[TokenInfo]`

---

### `revoke_token(self: Any, token: str) -> bool`

`行号:528` `复杂度:低`

撤销令牌

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `token` | `str` | `-` |

#### 返回

`bool`

---

### `add_authorization_hook(self: Any, hook: Callable[[str, Dict[str, Any]], bool]) -> None`

`行号:539` `复杂度:低`

添加授权钩子

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `hook` | `Callable[[str, Dict[str, Any]], bool]` | `-` |

#### 返回

`None`

---

### `check_permission(self: Any, token: str, resource: str, action: str) -> bool`

`行号:546` `复杂度:高`

检查权限

Args:

    token: 访问令牌

    resource: 资源

    action: 操作

Returns:

    是否有权限

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `token` | `str` | `-` |
| `resource` | `str` | `-` |
| `action` | `str` | `-` |

#### 返回

`bool`

---

### `grant_permissions(self: Any, grant_id: str, permissions: List[Permission]) -> bool`

`行号:591` `复杂度:低`

授予权限

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `grant_id` | `str` | `-` |
| `permissions` | `List[Permission]` | `-` |

#### 返回

`bool`

---

### `revoke_permissions(self: Any, grant_id: str, resources: Optional[List[str]] = None) -> bool`

`行号:604` `复杂度:低`

撤销权限

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `grant_id` | `str` | `-` |
| `resources` (可选) | `Optional[List[str]]` | `None` |

#### 返回

`bool`

---

### `cleanup_expired(self: Any) -> int`

`行号:621` `复杂度:中`

清理过期数据

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`int`

---

### `_verify_pkce(self: Any, verifier: str, challenge: str, method: Optional[str]) -> bool`

`行号:653` `复杂度:低`

验证 PKCE

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `verifier` | `str` | `-` |
| `challenge` | `str` | `-` |
| `method` | `Optional[str]` | `-` |

#### 返回

`bool`

---

### `get_stats(self: Any) -> Dict[str, Any]`

`行号:668` `复杂度:低`

获取统计信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |

#### 返回

`Dict[str, Any]`

---

---

### `FineGrainedPermissionManager`

`行号: 681`  

细粒度权限管理器

#### 属性

| Name | Type |
|:---|:---|
| `authorization_manager` | `AuthorizationManager` |

#### 装饰器

### `add_policy(self: Any, policy_id: str, effect: str, principals: List[str], resources: List[str], actions: List[str], conditions: Optional[Dict[str, Any]] = None) -> None`

`行号:689` `复杂度:低`

添加策略

Args:

    policy_id: 策略 ID

    effect: 效果 (allow/deny)

    principals: 主体列表

    resources: 资源列表

    actions: 操作列表

    conditions: 条件

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy_id` | `str` | `-` |
| `effect` | `str` | `-` |
| `principals` | `List[str]` | `-` |
| `resources` | `List[str]` | `-` |
| `actions` | `List[str]` | `-` |
| `conditions` (可选) | `Optional[Dict[str, Any]]` | `None` |

#### 返回

`None`

---

### `evaluate(self: Any, principal: str, resource: str, action: str, context: Optional[Dict[str, Any]] = None) -> bool`

`行号:722` `复杂度:中`

评估权限

Args:

    principal: 主体

    resource: 资源

    action: 操作

    context: 上下文

Returns:

    是否允许

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `principal` | `str` | `-` |
| `resource` | `str` | `-` |
| `action` | `str` | `-` |
| `context` (可选) | `Optional[Dict[str, Any]]` | `None` |

#### 返回

`bool`

---

### `_match_principal(self: Any, policy: Dict[str, Any], principal: str) -> bool`

`行号:754` `复杂度:低`

匹配主体

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy` | `Dict[str, Any]` | `-` |
| `principal` | `str` | `-` |

#### 返回

`bool`

---

### `_match_resource(self: Any, policy: Dict[str, Any], resource: str) -> bool`

`行号:761` `复杂度:低`

匹配资源

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy` | `Dict[str, Any]` | `-` |
| `resource` | `str` | `-` |

#### 返回

`bool`

---

### `_match_action(self: Any, policy: Dict[str, Any], action: str) -> bool`

`行号:768` `复杂度:低`

匹配操作

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy` | `Dict[str, Any]` | `-` |
| `action` | `str` | `-` |

#### 返回

`bool`

---

### `_match_conditions(self: Any, policy: Dict[str, Any], context: Dict[str, Any]) -> bool`

`行号:775` `复杂度:中`

匹配条件

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy` | `Dict[str, Any]` | `-` |
| `context` | `Dict[str, Any]` | `-` |

#### 返回

`bool`

---

### `remove_policy(self: Any, policy_id: str) -> bool`

`行号:785` `复杂度:低`

移除策略

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy_id` | `str` | `-` |

#### 返回

`bool`

---

### `get_policies(self: Any, policy_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]`

`行号:793` `复杂度:低`

获取策略

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `self` | `Any` | `-` |
| `policy_id` (可选) | `Optional[str]` | `None` |

#### 返回

`Dict[str, List[Dict[str, Any]]]`

---

---

## Test Coverage

*No specific tests found for this module.*
