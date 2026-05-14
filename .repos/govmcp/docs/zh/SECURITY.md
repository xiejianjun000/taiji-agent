# 政务MCP协议 安全指南

本文档描述了 govmcp 项目中的安全特性和最佳实践。

## 目录

- [安全架构概述](#安全架构概述)
- [国密算法支持](#国密算法支持)
- [数据加密](#数据加密)
- [身份认证](#身份认证)
- [权限控制](#权限控制)
- [审计追踪](#审计追踪)
- [安全配置](#安全配置)
- [最佳实践](#最佳实践)
- [常见安全问题](#常见安全问题)

---

## 安全架构概述

govmcp 采用多层安全防护架构：

```
┌─────────────────────────────────────────────────────────┐
│                    安全防护层                            │
├─────────────────────────────────────────────────────────┤
│  身份认证  │  权限控制  │  数据加密  │  审计追踪  │  传输安全  │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    协议层                                │
├─────────────────────────────────────────────────────────┤
│           MCP 协议 (JSON-RPC 2.0 + 国密扩展)            │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    服务层                                │
├─────────────────────────────────────────────────────────┤
│     服务器  │  工具注册  │  审批引擎  │  审计引擎      │
└─────────────────────────────────────────────────────────┘
```

### 核心安全原则

1. **最小权限原则**：每个组件只拥有完成其功能所需的最小权限
2. **纵深防御**：多层安全防护，单点失效不会导致全面沦陷
3. **默认安全**：安全配置默认启用，无需额外设置
4. **隐私保护**：敏感数据全程加密，最小化明文传输

---

## 国密算法支持

### SM2 非对称加密

SM2是国家密码管理局发布的椭圆曲线公钥密码算法，用于：
- 数字签名
- 密钥交换
- 公钥加密

#### 密钥生成

```python
from govmcp.crypto import SM2

sm2 = SM2()
print(f"私钥: {sm2.private_key.hex()}")
print(f"公钥: {sm2.public_key.hex()}")
```

#### 签名和验签

```python
# 签名
message = b"政务审批数据-2024-001"
signature = sm2.sign(message)

# 验签
is_valid = sm2.verify(message, signature)
assert is_valid, "签名验证失败"
```

#### 安全建议

- 私钥必须安全存储，禁止硬编码或日志输出
- 生产环境建议使用硬件安全模块(HSM)存储私钥
- 定期轮换密钥，建议周期为1年

---

### SM3 密码杂凑

SM3是国产密码杂凑算法，输出256位摘要，用于：
- 数据完整性校验
- 消息认证
- 随机数生成种子

#### 使用示例

```python
from govmcp.crypto import sm3_hash

data = "需要完整性保护的数据"
digest = sm3_hash(data)
print(f"SM3摘要: {digest}")
```

#### 安全特性

- 抗碰撞性：无法找到两个不同消息产生相同摘要
- 抗修改性：消息任何修改都会导致摘要变化
- 单向性：无法从摘要反推原始消息

---

### SM4 对称加密

SM4是国产分组密码算法，分组长度128位，密钥长度128位，用于：
- 数据加密存储
- 敏感信息传输
- 批量数据保护

#### 加密示例

```python
from govmcp.crypto import SM4

# 生成密钥（必须32字节）
key = b"32-byte-secret-key-for-sm4!!"

sm4 = SM4(key=key)

# 加密字符串
plaintext = "政务敏感数据"
encrypted = sm4.encrypt_str(plaintext)

# 解密
decrypted = sm4.decrypt_str(encrypted)
assert plaintext == decrypted
```

#### 安全建议

- 密钥必须32字节，不足需填充，超长需截断
- 同一密钥不建议加密过多数据，建议定期轮换
- 密钥存储使用密钥派生函数(KDF)，不要直接使用原始密钥

---

## 数据加密

### 传输加密

#### 启用传输加密

```python
from govmcp.server import GovMCPServer

server = GovMCPServer(
    name="安全政务服务",
    encryption_enabled=True  # 默认启用
)
```

#### 加密请求和响应

```python
from govmcp.protocol import MCPProtocol

protocol = MCPProtocol()

# 调用工具时自动加密参数
result = await protocol.call_tool(
    server=server,
    tool_name="query_enterprise_info",
    arguments={"credit_code": "91110000XXXXXXXX"},
    encrypt_args=True  # 默认加密
)
```

### 存储加密

#### 敏感数据标记

```python
from govmcp.models import Tool

tool = Tool(
    name="query_social_security",
    description="社保信息查询",
    encrypted=True,  # 标记为敏感数据
    input_schema={...},
    output_schema={...}
)
```

#### 审计数据加密

```python
from govmcp.models import AuditChain

chain = AuditChain(chain_id="audit-2024-001")

# 审计记录默认加密存储
chain.add_record(record)
```

---

## 身份认证

### 认证流程

```
┌────────┐    1.认证请求    ┌────────────┐    2.验证凭证   ┌────────────┐
│ 客户端 │ ──────────────> │  MCP服务器  │ ─────────────> │ 认证服务    │
│        │                 │            │  <──────────── │            │
│        │ <────────────── │            │   3.认证结果   │            │
└────────┘    4.会话令牌    └────────────┘                └────────────┘
```

### 认证实现

```python
from govmcp.server import GovMCPServer
from govmcp.auth import GovMCPToken

class SecureGovServer(GovMCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._auth_tokens = {}

    def authenticate(self, credentials: dict) -> str:
        """验证凭证并返回令牌"""
        user_id = credentials.get("user_id")
        password = credentials.get("password")

        # 验证逻辑（实际应连接认证服务）
        if self._verify_credentials(user_id, password):
            token = GovMCPToken.generate(user_id)
            self._auth_tokens[token] = user_id
            return token
        raise AuthenticationError("认证失败")

    def _verify_credentials(self, user_id: str, password: str) -> bool:
        """验证用户凭证"""
        # 实现实际的验证逻辑
        return True

    def verify_token(self, token: str) -> bool:
        """验证令牌有效性"""
        return token in self._auth_tokens
```

### 令牌管理

```python
from govmcp.auth import TokenManager

manager = TokenManager(
    secret_key="安全的密钥",
    expire_hours=8,      # 令牌8小时过期
    refresh_enabled=True  # 启用刷新
)

# 生成令牌
token = manager.generate_token(user_id="user-001", roles=["admin"])

# 验证令牌
payload = manager.verify_token(token)

# 刷新令牌
new_token = manager.refresh_token(token)
```

---

## 权限控制

### 基于角色的访问控制(RBAC)

```
                    ┌─────────────┐
                    │   管理员     │ (role: admin)
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │   审批员     │ │   窗口人员   │ │   查询人员   │
    │ (approver) │ │  (window)   │ │   (viewer)  │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │               │
           ▼               ▼               ▼
    审批工具集        受理工具集       查询工具集
```

### 权限配置

```python
from govmcp.models import Tool, Permission

# 定义需要特定权限的工具
tool = Tool(
    name="query_social_security",
    description="社保信息查询",
    permissions=[
        "social_security:read",
        "personal_info:access"
    ],
    encrypted=True
)
```

### 权限检查

```python
from govmcp.auth import PermissionChecker

checker = PermissionChecker()

# 定义角色权限
role_permissions = {
    "admin": ["*"],  # 管理员拥有所有权限
    "approver": [
        "approval:*",
        "query:*",
        "sm4:*"
    ],
    "window": [
        "query:basic",
        "submit:approval"
    ],
    "viewer": [
        "query:public"
    ]
}

def check_permission(role: str, required_permission: str) -> bool:
    """检查角色是否拥有特定权限"""
    perms = role_permissions.get(role, [])
    if "*" in perms:
        return True
    return required_permission in perms

# 使用示例
assert check_permission("admin", "approval:submit") == True
assert check_permission("viewer", "approval:submit") == False
```

---

## 审计追踪

### 审计链

```python
from govmcp.models import AuditChain, AuditRecord
from datetime import datetime

chain = AuditChain(chain_id="audit-2024-001")

# 添加操作记录
chain.add_record(AuditRecord(
    timestamp=datetime.now(),
    operator="user-001",
    operation="query_enterprise_info",
    resource="credit_code:91110000XXXXXXXX",
    details={"reason": "企业年报审核"},
    previous_hash=chain.get_last_hash(),
    signature="..."  # SM2签名
))

# 验证完整性
is_valid = chain.verify()
assert is_valid, "审计链验证失败"
```

### 审计日志配置

```python
from govmcp.server import GovMCPServer

server = GovMCPServer(
    name="审计服务器",
    audit_enabled=True,
    audit_config={
        "log_level": "INFO",
        "log_path": "/var/log/govmcp/audit.log",
        "log_rotation": "daily",
        "retention_days": 180,  # 保留180天
        "encrypt_logs": True    # 加密日志
    }
)
```

### 审计事件类型

| 事件类型 | 描述 | 记录内容 |
|---------|------|---------|
| authentication | 身份认证 | 用户、IP、时间、结果 |
| authorization | 权限检查 | 用户、权限、结果 |
| data_access | 数据访问 | 用户、资源、操作 |
| data_modification | 数据修改 | 用户、资源、变更前后 |
| system_event | 系统事件 | 事件类型、详情 |

---

## 安全配置

### 配置文件示例

```yaml
# config/security.yaml
security:
  # 加密配置
  encryption:
    algorithm: sm4  # sm4/sm2
    key_rotation_days: 90

  # 认证配置
  authentication:
    type: token  # token/oauth2/cert
    token_expire_hours: 8
    refresh_enabled: true

  # 审计配置
  audit:
    enabled: true
    log_path: /var/log/govmcp/audit.log
    retention_days: 180
    encrypt_logs: true

  # 传输安全
  transport:
    tls_enabled: true
    tls_version: "1.3"
    verify_client_cert: true

  # 访问控制
  access_control:
    ip_whitelist:
      - "10.0.0.0/8"
      - "192.168.0.0/16"
    rate_limit:
      enabled: true
      requests_per_minute: 100
```

### 环境变量配置

```bash
# 安全相关环境变量
export GOVMCP_ENCRYPTION_ENABLED=true
export GOVMCP_AUDIT_ENABLED=true
export GOVMCP_SM4_KEY=your-32-byte-key
export GOVMCP_TOKEN_SECRET=your-token-secret
export GOVMCP_TLS_CERT=/path/to/cert.pem
export GOVMCP_TLS_KEY=/path/to/key.pem
```

---

## 最佳实践

### 开发阶段

1. **敏感信息处理**
   - 禁止在代码中硬编码密钥
   - 使用环境变量或密钥管理服务
   - 日志中脱敏处理

   ```python
   # 错误示例
   key = "32-byte-key-in-code"

   # 正确示例
   import os
   key = os.environ.get("GOVMCP_SM4_KEY")
   if not key:
       raise ValueError("缺少加密密钥配置")
   ```

2. **输入验证**
   ```python
   def validate_input(data: dict) -> bool:
       required_fields = ["credit_code", "applicant_id"]
       for field in required_fields:
           if field not in data:
               raise ValidationError(f"缺少必需字段: {field}")

       # 格式验证
       if not re.match(r"^\d{18}$", data["credit_code"]):
           raise ValidationError("统一社会信用代码格式错误")

       return True
   ```

3. **安全编码**
   ```python
   # 使用参数化查询（防止注入）
   def query_enterprise(credit_code: str):
       # 安全：使用参数化查询
       cursor.execute(
           "SELECT * FROM enterprises WHERE credit_code = ?",
           (credit_code,)
       )

       # 危险：不使用参数化
       cursor.execute(
           f"SELECT * FROM enterprises WHERE credit_code = '{credit_code}'"
       )
   ```

### 部署阶段

1. **安全配置检查清单**
   - [ ] 启用传输层加密(TLS)
   - [ ] 配置国密算法为首选
   - [ ] 启用审计日志
   - [ ] 配置访问控制列表
   - [ ] 设置密钥轮换策略
   - [ ] 配置安全告警

2. **容器安全**
   ```dockerfile
   # 使用非root用户运行
   USER nonroot

   # 只读文件系统
   READONLY=true

   # 限制资源
   MEMORY=512m
   CPU=1
   ```

3. **网络安全**
   ```yaml
   # Kubernetes 网络策略
   networkPolicy:
     ingress:
       - from:
           - namespaceSelector:
               matchLabels:
                 name: government
     egress:
       - to:
           - podSelector:
               matchLabels:
                 app: govmcp-server
   ```

### 运维阶段

1. **密钥管理**
   - 定期轮换密钥（建议90天）
   - 使用密钥管理服务(KMS)
   - 记录密钥使用审计日志

2. **日志监控**
   ```python
   # 配置安全告警
   security_alerts:
     - type: multiple_failed_logins
       threshold: 5
       window_minutes: 10
       action: lock_account

     - type: unusual_data_access
       pattern: "*:sensitive:*"
       threshold: 100
       window_hours: 1
       action: notify_security_team

     - type: audit_chain_modified
       action: block_and_notify
   ```

3. **定期安全评估**
   - 渗透测试（每年至少1次）
   - 代码安全审计
   - 依赖漏洞扫描
   - 配置合规检查

---

## 常见安全问题

### Q1: 如何安全存储密钥？

**推荐方案：**
1. 使用硬件安全模块(HSM)
2. 使用云服务商KMS（如阿里云KMS）
3. 使用环境变量（容器环境）

**不推荐：**
- 硬编码在代码中
- 存储在版本控制系统
- 明文存储在配置文件

### Q2: 如何防止SQL注入？

```python
# 使用ORM框架
from sqlalchemy.orm import Session

def query_with_orm(session: Session, credit_code: str):
    result = session.query(Enterprise).filter(
        Enterprise.credit_code == credit_code
    ).first()
    return result

# 使用参数化查询
def query_with_params(cursor, credit_code: str):
    cursor.execute(
        "SELECT * FROM enterprises WHERE credit_code = ?",
        (credit_code,)
    )
```

### Q3: 如何处理敏感数据？

```python
import re

def mask_sensitive_data(data: dict) -> dict:
    """敏感数据脱敏"""
    masked = data.copy()

    # 身份证号脱敏
    if "id_card" in masked:
        id_card = masked["id_card"]
        masked["id_card"] = f"{id_card[:6]}****{id_card[-4:]}"

    # 手机号脱敏
    if "phone" in masked:
        phone = masked["phone"]
        masked["phone"] = f"{phone[:3]}****{phone[-4:]}"

    # 银行卡脱敏
    if "bank_card" in masked:
        bank_card = masked["bank_card"]
        masked["bank_card"] = f"{bank_card[:4]}****{bank_card[-4:]}"

    return masked
```

### Q4: 如何安全日志记录？

```python
import logging
from govmcp.crypto import SM4

class SecureLogger:
    def __init__(self, key: bytes):
        self.sm4 = SM4(key=key)

    def log(self, level: str, message: str, **kwargs):
        # 敏感字段脱敏
        safe_kwargs = mask_sensitive_data(kwargs)

        # 加密存储
        encrypted_msg = self.sm4.encrypt_str(
            f"{message} | {safe_kwargs}"
        )

        logging.log(
            getattr(logging, level),
            encrypted_msg
        )
```

---

## 相关链接

- [快速开始指南](./QUICKSTART.md)
- [高级指南](./ADVANCED.md)
- [API参考](./API.md)
- [部署指南](./DEPLOYMENT.md)
