# govmcp 中文完整文档

> 国产信创MCP协议 — 国密加密 + 审批工作流 + 不可篡改审计链

[English](../en/README.md) | 首页

---

## 目录

- [项目概述](#项目概述)
- [核心特性](#核心特性)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [国密加密](#国密加密)
- [审批工作流](#审批工作流)
- [审计链](#审计链)
- [政务工具集](#政务工具集)
- [信创模型适配](#信创模型适配)
- [安全指南](#安全指南)
- [部署指南](DEPLOYMENT.md)
- [高级指南](ADVANCED.md)
- [API参考](API.md)

---

## 项目概述

### 什么是 govmcp

**govmcp** 是 OpenTaiji 产品矩阵的核心通信协议层，专为中国政务场景设计的 Model Context Protocol (MCP) 实现。它在标准 MCP 基础上叠加了三大核心能力：

1. **国密加密传输**：使用 SM2/SM3/SM4 国密算法确保数据安全
2. **多级审批工作流**：内置灵活的审批流程引擎
3. **不可篡改审计链**：基于 SM3 链式哈希的完整操作追溯

### 设计目标

- 符合中国政府信息安全法规要求
- 支持信创环境（国产操作系统、芯片、数据库）
- 与现有政务系统无缝集成
- 提供开箱即用的政务场景支持

---

## 核心特性

### 🔐 国密加密

| 算法 | 类型 | 用途 | 状态 |
|:---|:---|:---|:---:|
| SM3 | 哈希算法 | 数据完整性验证、数字签名 | ✅ 已实现 |
| SM4 | 对称加密 | 数据加密传输 | ✅ 已实现 |
| SM2 | 非对称加密 | 数字签名、密钥交换 | 📋 规划中 |

### ✅ 审批工作流

- 多级审批链（1-N级可配置）
- 审批状态流转（待审批 → 审批中 → 已通过/已拒绝）
- 审批意见记录
- 会签、加签、转签、委托等高级功能

### 🔗 不可篡改审计链

- SM3 链式哈希技术
- 每次操作生成不可篡改的审计记录
- 支持完整性和真实性验证
- JSON 格式导出，便于存档和分析

### 🤖 政务工具集（100+工具）

| 类别 | 数量 | 覆盖范围 |
|:---|:---:|:---|
| 市民服务 | 20 | 身份证、户籍、社保、医保、公积金、驾驶证、车辆等 |
| 企业服务 | 20 | 工商注册、税务、许可证、知识产权、政府采购等 |
| 碳排放 | 15 | 碳排放填报、配额查询、碳交易、碳足迹计算等 |
| 环境监测 | 15 | 空气质量、水质、土壤污染、噪声监测、固废管理等 |
| 智慧城市 | 15 | 交通控制、停车、路灯、水电气暖、养老医疗等 |
| 审批工作流 | 15 | 流程发起、进度查询、会签、加签、转签等 |

### 🔌 信创模型适配

支持 19 个国产大模型：

- 百度：文心一言、ERNIE-4.0、ERNIE-3.5
- 阿里：通义千问、通义千问2.5
- 腾讯：混元大模型
- 字节：豆包大模型、扣子
- 智谱：GLM-4、GLM-4V
- 科大讯飞：星火大模型
- 华为：盘古大模型
- 商汤：日日新
- MiniMax：MiniMax
- 百川：百川大模型
- 月之暗面：Kimi (Moonshot)
- 腾讯云：腾讯混元(Hunyuan)
- 出门问问：序列猴子
- 其它：Pangu、Others

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                         应用层 (App)                        │
│   政务审批系统 │ 碳排放监管 │ 环境监测 │ 智慧城市 │ ...      │
├─────────────────────────────────────────────────────────────┤
│                      govmcp 协议层                           │
├─────────────────┬─────────────────┬─────────────────────────┤
│   tools/        │   server/       │      protocol/         │
│   工具注册中心   │   审批工作流    │   JSON-RPC 2.0        │
│   @govmcp_tool  │   ApprovalFlow  │   GovMCPServer        │
├─────────────────┴─────────────────┴─────────────────────────┤
│                      crypto/ (国密层)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │    SM3      │  │    SM4      │  │    AuditChain       ││
│  │   哈希      │  │   对称加密   │  │   不可篡改审计链     ││
│  └─────────────┘  └─────────────┘  └─────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## 快速开始

详细教程请参阅 [快速开始指南](QUICKSTART.md)。

### 环境要求

- Python 3.10+
- pip 或 pip3

### 安装

```bash
# 从 PyPI 安装
pip install govmcp

# 从源码安装
pip install -e .

# 完整安装（含硬件加速）
pip install govmcp[full]
```

### 基本使用

```python
from govmcp import GovMCPServer, govmcp_tool

server = GovMCPServer("my-server", "1.0", crypto_enabled=True)

@server.tool("hello", description="问候语", input_schema={
    "type": "object",
    "properties": {"name": {"type": "string"}},
    "required": ["name"]
})
def hello(**kwargs):
    return f"你好, {kwargs['name']}!"

server.run()
```

---

## 国密加密

### SM3 哈希

```python
from govmcp import sm3_hash

data = b"Hello, govmcp!"
hash_value = sm3_hash(data)
print(hash_value)  # 64位十六进制字符串
```

### SM4 加解密

```python
from govmcp import sm4_encrypt, sm4_decrypt, generate_sm4_key

# 生成密钥
key = generate_sm4_key()

# 加密
plaintext = b"政务敏感数据"
ciphertext = sm4_encrypt(plaintext, key)

# 解密
decrypted = sm4_decrypt(ciphertext, key)
```

详细使用请参阅 [API 参考](API.md)。

---

## 审批工作流

```python
from govmcp import ApprovalFlow, ApprovalStatus

# 创建三级审批流程
flow = ApprovalFlow(["部门主管", "中心主任", "局领导"])

# 发起审批
flow.start("行政审批申请-001")

# 一级审批
flow.approve("部门主管", "材料齐全，同意上报")

# 二级审批
flow.approve("中心主任", "符合规定，同意")

# 三级审批（最终决策）
flow.approve("局领导", "批准执行")

# 验证审批完成
assert flow.is_approved()
```

详细使用请参阅 [高级指南](ADVANCED.md)。

---

## 审计链

```python
from govmcp import AuditChain

# 创建审计链
chain = AuditChain()

# 添加审计记录
chain.add_entry(
    action="tool_call",
    operator="operator_001",
    input_data=b"申请材料",
    output_data=b"审批通过",
    result="approved"
)

# 添加更多记录
chain.add_entry(
    action="resource_read",
    operator="operator_002",
    input_data=b"",
    output_data=b"历史数据",
    result="success"
)

# 验证审计链完整性
assert chain.verify()

# 导出审计记录
audit_log = chain.export()
print(audit_log)
```

---

## 政务工具集

### 市民服务

```python
from govmcp.tools.government import citizen_service

# 查询社保信息
result = citizen_service.query_social_security(citizen_id="...")
```

### 企业服务

```python
from govmcp.tools.government import enterprise_service

# 查询企业工商信息
result = enterprise_service.query_business_license(credit_code="...")
```

### 碳排放

```python
from govmcp.tools.government import carbon_emission

# 碳排放数据填报
result = carbon_emission.submit_carbon_data(
    enterprise_id="...",
    year=2025,
    quarter=1,
    emissions={"scope1": 1000, "scope2": 2000}
)
```

详细工具列表请参阅 [API 参考](API.md)。

---

## 信创模型适配

```python
from govmcp.models import ModelRegistry

# 获取模型适配器
registry = ModelRegistry()

# 使用百度文心一言
ernie = registry.get_adapter("baidu-ernie")
response = ernie.chat("你好，请介绍一下政务服务机器人")

# 使用阿里通义千问
qwen = registry.get_adapter("ali-qwen")
response = qwen.chat("如何办理营业执照？")
```

---

## 安全指南

govmcp 严格遵循中国政府信息安全标准：

- ✅ 符合等保2.0要求
- ✅ 支持密评合规
- ✅ 端到端加密传输
- ✅ 不可篡改审计

详细安全配置请参阅：
- [安全指南](SECURITY.md)
- [安全白皮书](../SECURITY.md)

---

## 常见问题

### Q: govmcp 与标准 MCP 有什么区别？

A: govmcp 在标准 MCP 基础上增加了国密加密、审批工作流和审计链三大核心能力，专为政务场景设计。

### Q: 支持哪些操作系统？

A: 支持所有主流操作系统，包括：
- Linux（麒麟、统信UOS等信创系统）
- Windows
- macOS

### Q: 如何获取技术支持？

A: 您可以通过以下方式获取支持：
- 提交 [Issue](https://github.com/opentaiji/govmcp/issues)
- 加入 [Discussions](https://github.com/opentaiji/govmcp/discussions)

---

## 更新日志

详细更新记录请参阅 [CHANGELOG.md](../../CHANGELOG.md)。

---

## License

Apache 2.0 — OpenTaiji Team
