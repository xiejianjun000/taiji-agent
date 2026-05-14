# govmcp 快速开始指南

> 30分钟上手 govmcp

本文档将帮助您在最短时间内了解并开始使用 govmcp。

---

## 目录

- [环境准备](#环境准备)
- [安装 govmcp](#安装-govmcp)
- [第一个应用](#第一个应用)
- [国密加密示例](#国密加密示例)
- [审批工作流示例](#审批工作流示例)
- [审计链示例](#审计链示例)
- [政务工具使用](#政务工具使用)
- [下一步](#下一步)

---

## 环境准备

### 系统要求

| 要求 | 说明 |
|:---|:---|
| Python | 3.10 或更高版本 |
| 操作系统 | Linux/macOS/Windows |
| 内存 | 最低 4GB，推荐 8GB+ |
| 磁盘 | 最低 500MB 可用空间 |

### 检查 Python 版本

```bash
python3 --version
# Python 3.10.0 或更高

# 如果版本低于 3.10，请先升级 Python
```

### 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv govmcp-env

# 激活虚拟环境
# Linux/macOS
source govmcp-env/bin/activate

# Windows
.\govmcp-env\Scripts\activate
```

---

## 安装 govmcp

### 方式一：从 PyPI 安装（推荐）

```bash
pip install govmcp
```

### 方式二：从源码安装

```bash
# 克隆仓库
git clone https://github.com/opentaiji/govmcp.git
cd govmcp

# 安装
pip install -e .
```

### 方式三：安装完整版本（含硬件加速）

```bash
pip install govmcp[full]
```

### 验证安装

```bash
python -c "import govmcp; print(govmcp.__version__)"
# 1.0.0
```

---

## 第一个应用

### 基础示例：创建 MCP 服务器

```python
from govmcp import GovMCPServer, govmcp_tool

# 创建服务器实例
server = GovMCPServer(
    name="my-government-server",
    version="1.0.0",
    crypto_enabled=True  # 启用国密加密
)

# 定义工具
@server.tool(
    name="get_citizen_info",
    description="获取市民信息",
    input_schema={
        "type": "object",
        "properties": {
            "citizen_id": {
                "type": "string",
                "description": "市民身份证号"
            }
        },
        "required": ["citizen_id"]
    }
)
def get_citizen_info(citizen_id: str) -> dict:
    return {
        "citizen_id": citizen_id,
        "name": "张三",
        "address": "北京市朝阳区xxx"
    }

# 启动服务器
server.run()
```

### 运行服务器

```bash
python my_server.py
```

服务器将启动 stdio 消息循环，等待来自 MCP 客户端的请求。

---

## 国密加密示例

### SM3 哈希

SM3 是一种密码学哈希函数，用于生成数据的"数字指纹"。

```python
from govmcp import sm3_hash

# 对数据进行哈希
data = b"政务文件内容"
hash_value = sm3_hash(data)

print(f"原始数据: {data}")
print(f"SM3哈希: {hash_value}")
print(f"哈希长度: {len(hash_value)} 字符")

# 输出示例：
# 原始数据: b'政务文件内容'
# SM3哈希: 3a2f5f3b8c9d1e4a7f6b8c9d1e4a7f6b8c9d1e4a7f6b8c9d1e4a7f6b8c9d1e4a
# 哈希长度: 64 字符
```

### SM4 对称加密

SM4 是一种对称加密算法，用于加密敏感数据。

```python
from govmcp import sm4_encrypt, sm4_decrypt, generate_sm4_key

# 方式一：自动生成密钥
key = generate_sm4_key()
print(f"生成的SM4密钥: {key.hex()}")

# 方式二：使用指定的密钥（32字节十六进制字符串）
specified_key = "0123456789abcdef0123456789abcdef"
key = bytes.fromhex(specified_key)

# 加密数据（需要16字节对齐）
plaintext = b"这是一段需要加密的政务数据      "  # 补齐到16字节倍数
ciphertext = sm4_encrypt(plaintext, key)

print(f"明文: {plaintext}")
print(f"密文: {ciphertext.hex()}")

# 解密数据
decrypted = sm4_decrypt(ciphertext, key)
print(f"解密后: {decrypted}")

# 验证
assert plaintext == decrypted, "解密后数据不一致"
```

### CBC 模式加密

```python
from govmcp import sm4_cbc_encrypt, sm4_cbc_decrypt, generate_sm4_key

key = generate_sm4_key()
iv = b"1234567890abcdef"  # 16字节初始化向量

plaintext = b"需要加密的敏感数据"

ciphertext = sm4_cbc_encrypt(plaintext, key, iv)
decrypted = sm4_cbc_decrypt(ciphertext, key, iv)

assert plaintext == decrypted
```

---

## 审批工作流示例

### 创建审批流程

```python
from govmcp import ApprovalFlow, ApprovalStatus

# 定义审批链（按照审批顺序）
approvers = [
    "部门主管-李明",
    "中心主任-王芳",
    "局领导-张强"
]

# 创建审批流程
flow = ApprovalFlow(approvers)

# 发起审批申请
flow.start(
    title="关于采购办公设备的申请",
    applicant="申请人-陈某",
    content="申请采购台式电脑5台，预算10万元"
)

print(f"审批状态: {flow.get_status()}")
print(f"当前待审批: {flow.get_current_approver()}")

# 一级审批
flow.approve(
    approver="部门主管-李明",
    comment="设备需求合理，同意上报"
)

# 二级审批
flow.approve(
    approver="中心主任-王芳",
    comment="符合年度预算安排"
)

# 三级审批（最终决策）
flow.approve(
    approver="局领导-张强",
    comment="批准采购"
)

# 验证审批结果
print(f"审批状态: {flow.get_status()}")
print(f"是否已完成: {flow.is_approved()}")

# 获取完整审批记录
records = flow.get_approval_records()
for record in records:
    print(f"{record['approver']}: {record['comment']} ({record['timestamp']})")
```

### 审批拒绝处理

```python
from govmcp import ApprovalFlow, ApprovalStatus

flow = ApprovalFlow(["部门主管", "中心主任", "局领导"])
flow.start("申请")

# 一级通过
flow.approve("部门主管", "同意")

# 二级拒绝
flow.reject("中心主任", "预算超标，拒绝")

print(f"审批状态: {flow.get_status()}")
print(f"是否通过: {flow.is_approved()}")  # False
print(f"拒绝理由: {flow.get_rejection_reason()}")  # 预算超标，拒绝
```

### 会签审批

```python
from govmcp import ApprovalFlow, ApprovalStatus

# 创建需要会签的审批流程
flow = ApprovalFlow(["财务部", "审计部", "领导"], require_countersign=True)

flow.start("联合审批项目")

# 财务部会签
flow.approve("财务部", "财务审核通过")

# 审计部会签
flow.approve("审计部", "审计审核通过")

# 领导最终审批
flow.approve("领导", "批准执行")

assert flow.is_approved()
```

---

## 审计链示例

### 基本使用

```python
from govmcp import AuditChain

# 创建审计链实例
chain = AuditChain()

# 记录操作
chain.add_entry(
    action="document_upload",
    operator="admin_user",
    input_data=b"上传的文档内容",
    output_data=b"文档已存储",
    result="success"
)

# 记录审批操作
chain.add_entry(
    action="approval_complete",
    operator="approver_001",
    input_data=b"申请材料",
    output_data=b"审批通过",
    result="approved"
)

# 验证审计链完整性
is_valid = chain.verify()
print(f"审计链完整性验证: {'通过' if is_valid else '失败'}")

# 导出审计记录
audit_export = chain.export()
print(audit_export)
```

### 完整审计示例

```python
from govmcp import AuditChain, ApprovalFlow, sm3_hash

# 创建审计链
chain = AuditChain()

# 1. 用户登录
chain.add_entry(
    action="user_login",
    operator="operator_zhang",
    input_data=b"",
    output_data=b"登录成功",
    result="success"
)

# 2. 创建审批流程
flow = ApprovalFlow(["主管A", "主管B"])
flow.start("重要事项申请")

chain.add_entry(
    action="workflow_start",
    operator="operator_zhang",
    input_data=b"申请内容",
    output_data=b"流程ID-001",
    result="started"
)

# 3. 主管审批
flow.approve("主管A", "同意")
chain.add_entry(
    action="approval",
    operator="主管A",
    input_data=b"申请材料",
    output_data=b"一级审批通过",
    result="approved"
)

# 4. 数据修改
chain.add_entry(
    action="data_modify",
    operator="operator_zhang",
    input_data=b"原始数据",
    output_data=b"新数据",
    result="modified"
)

# 5. 验证完整性
assert chain.verify(), "审计链验证失败"

# 6. 导出存档
import json
with open("audit_log.json", "w", encoding="utf-8") as f:
    json.dump(chain.export(), f, ensure_ascii=False, indent=2)
```

---

## 政务工具使用

### 市民服务工具

```python
from govmcp.tools.government import citizen_service

# 查询社保信息
result = citizen_service.query_social_security(
    citizen_id="110101199001011234"
)
print(f"社保信息: {result}")

# 查询公积金
result = citizen_service.query_housing_fund(
    citizen_id="110101199001011234"
)

# 查询医保
result = citizen_service.query_medical_insurance(
    citizen_id="110101199001011234"
)
```

### 企业服务工具

```python
from govmcp.tools.government import enterprise_service

# 查询企业工商信息
result = enterprise_service.query_business_info(
    credit_code="91110000123456789X"
)

# 查询税务登记
result = enterprise_service.query_tax_registration(
    credit_code="91110000123456789X"
)
```

### 碳排放工具

```python
from govmcp.tools.government import carbon_emission

# 碳排放数据填报
result = carbon_emission.submit_carbon_data(
    enterprise_id="ENT001",
    year=2025,
    quarter=1,
    emissions={
        "scope1": 1500.5,
        "scope2": 3000.2,
        "scope3": 800.0
    }
)

# 查询碳配额
result = carbon_emission.query_carbon_quota(
    enterprise_id="ENT001",
    year=2025
)
```

---

## 下一步

恭喜完成快速开始！现在您可以：

### 深入学习
- 📖 [高级指南](ADVANCED.md) - 学习高级特性和最佳实践
- 📚 [API 参考](API.md) - 查看完整的 API 文档
- 🔒 [安全指南](SECURITY.md) - 了解安全配置和最佳实践
- 🚀 [部署指南](DEPLOYMENT.md) - 学习生产环境部署

### 示例项目
- 查看 [govmcp/examples](https://github.com/opentaiji/govmcp/tree/main/examples) 获取完整示例
- 参考 [官方教程](https://govmcp.opentaiji.com/tutorials)

### 获取帮助
- 🐛 遇到问题？提交 [Issue](https://github.com/opentaiji/govmcp/issues)
- 💬 加入讨论 [Discussions](https://github.com/opentaiji/govmcp/discussions)
- 📧 联系团队: support@opentaiji.com

---

[← 返回文档首页](README.md) | [高级指南 →](ADVANCED.md)
