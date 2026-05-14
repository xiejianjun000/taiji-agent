# govmcp · 政务MCP协议

> 国产信创MCP协议 — 国密加密 + 审批工作流 + 不可篡改审计链

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PyPI](https://img.shields.io/badge/PyPI-v1.0.0-orange.svg)](https://pypi.org/project/govmcp/)](https://pypi.org/project/govmcp/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/opentaiji/govmcp/actions)
[![Tests](https://img.shields.io/badge/tests-46%20passed-brightgreen.svg)](tests/)
[![Chinese Government Cryptography](https://img.shields.io/badge/国密-SM2%2FSM3%2FSM4-red.svg)](docs/zh/SECURITY.md)

[English](docs/en/README.md) | 中文

**govmcp** 是 OpenTaiji 产品矩阵的核心通信协议层，在标准 MCP (Model Context Protocol) 基础上，针对中国政务场景叠加三大核心能力：国密加密传输、多级审批工作流、不可篡改审计链。

---

## 目录

- [核心特性](#核心特性)
- [与标准MCP对比](#与标准mcp对比)
- [快速开始](#快速开始)
- [应用场景](#应用场景)
- [模块说明](#模块说明)
- [开发状态](#开发状态)
- [文档导航](#文档导航)
- [License](#license)

---

## 核心特性

### 🔐 国密加密
- **SM3 哈希算法**：纯Python实现，符合GM/T 0004-2012标准
- **SM4 对称加密**：128位分组密码，支持ECB/CBC模式
- **SM2 非对称加密**：（规划中）数字签名与密钥交换

### ✅ 审批工作流
- 多级审批链配置（1-N级）
- 审批状态跟踪（待审批、审批中、已通过、已拒绝）
- 审批意见记录与时间戳
- 会签、加签、转签、委托等高级功能

### 🔗 不可篡改审计链
- SM3链式哈希技术
- 完整操作追溯
- 防篡改验证机制
- JSON格式导出

### 🤖 政务工具集（100+工具）

| 类别 | 工具数 | 示例 |
|:---|:---:|:---|
| 市民服务 | 20 | 身份证、户籍、社保、医保、公积金 |
| 企业服务 | 20 | 工商注册、税务、许可证、知识产权 |
| 碳排放 | 15 | 碳排放填报、配额查询、碳交易 |
| 环境监测 | 15 | 空气质量、水质、土壤污染、噪声 |
| 智慧城市 | 15 | 交通控制、停车、路灯、水电气暖 |
| 审批工作流 | 15 | 流程发起、进度查询、会签、加签 |

### 🔌 信创模型适配
支持11个国产大模型API：

| 模型厂商 | 支持模型 |
|:---|:---|
| 百度 | 文心一言、ERNIE-4.0、ERNIE-3.5 |
| 阿里 | 通义千问、通义千问2.5 |
| 腾讯 | 混元大模型 |
| 字节 | 豆包大模型、扣子 |
| 智谱 | GLM-4、GLM-4V |
| 科大讯飞 | 星火大模型 |
| 华为 | 盘古大模型 |
| 商汤 | 日日新 |
|  MiniMax | MiniMax |
| 百川 | 百川大模型 |
| 月之暗面 | Kimi (Moonshot) |
| 腾讯云 | 腾讯混元(Hunyuan) |
| 出门问问 | 序列猴子 |
| 其它 | Pangu、Others |

---

## 与标准MCP对比

| 特性 | 标准MCP | govmcp |
|:---|:---|:---|
| **加密传输** | 无（可选） | **国密SM2/SM3/SM4** |
| **审批流程** | 无 | **内置多级审批工作流** |
| **审计追溯** | 无 | **不可篡改审计链** |
| **模型适配** | 通用LLM | **19个国产LLM深度适配** |
| **防幻觉** | 无 | **集成WFGY防幻觉引擎** |
| **合规认证** | 无 | **等保2.0/密评合规** |
| **政务工具** | 通用工具 | **100+政务专用工具** |
| **传输协议** | stdio/WebSocket | **stdio + WebSocket** |

---

## 快速开始

### 环境要求

- Python 3.10+
- pip 或 pip3

### 安装

```bash
# 从PyPI安装
pip install govmcp

# 从源码安装（开发版）
pip install -e .

# 完整安装（含硬件加速）
pip install govmcp[full]
```

### 30秒上手

```python
from govmcp import GovMCPServer, govmcp_tool, sm3_hash

server = GovMCPServer("my-server", "1.0", crypto_enabled=True)

@server.tool("hello", description="问好", input_schema={
    "type": "object",
    "properties": {"name": {"type": "string"}},
    "required": ["name"]
})
def hello(**kwargs):
    return f"你好, {kwargs['name']}!"

# 启动stdio消息循环
server.run()
```

### 国密加密

```python
from govmcp import sm3_hash, sm4_encrypt, sm4_decrypt, generate_sm4_key

# SM3 哈希
h = sm3_hash(b"govmcp")
print(h)  # 64位十六进制字符串

# SM4 加解密
key = generate_sm4_key()
ciphertext = sm4_encrypt(b"0123456789ABCDEF", key)
plaintext = sm4_decrypt(ciphertext, key)
```

### 审批工作流

```python
from govmcp import ApprovalFlow, ApprovalStatus

# 三级审批
flow = ApprovalFlow(["部门主管", "中心主任", "局领导"])

flow.approve("部门主管", "同意")
flow.approve("中心主任", "同意")
flow.approve("局领导", "同意")

assert flow.is_approved()
```

### 审计链

```python
from govmcp import AuditChain

chain = AuditChain()
chain.add_entry("tool_call", "operator_001", b"input", b"output", "approved")
chain.add_entry("resource_read", "operator_002", b"", b"data", "approved")

assert chain.verify()
print(chain.export())
```

---

## 应用场景

### 🏛️ 政务审批系统
实现多级审批流程，支持会签、加签、转签等复杂场景，完整记录审批过程。

```python
from govmcp import ApprovalFlow, AuditChain

flow = ApprovalFlow(["科长", "处长", "局长"])
chain = AuditChain()

# 发起审批
flow.start("行政审批申请")
chain.add_entry("approve_start", "admin", b"申请材料", b"待审批", "pending")

# 完成审批
for approver in ["科长", "处长", "局长"]:
    flow.approve(approver, "同意")
    chain.add_entry("approve", approver, b"", b"通过", "approved")

# 验证审计链
assert chain.verify()
```

### 🏭 碳排放监管
对接冷钢碳排放系统，实现碳排放数据填报、配额管理、碳交易等功能。

```python
from govmcp import sm4_encrypt, sm4_decrypt, AuditChain

chain = AuditChain()

# 加密传输碳排放数据
sensitive_data = b"enterprise_carbon_data_2025"
encrypted = sm4_encrypt(sensitive_data, key)

chain.add_entry("carbon_report", "enterprise_001", sensitive_data, encrypted, "encrypted")
```

### 🌿 环境监测预警
实时采集环境监测数据，支持超标预警、联动处置等功能。

### 🏙️ 智慧城市管理
整合交通、停车、路灯、水电气暖等城市基础设施数据，实现智能化管理。

---

## 模块说明

| 模块 | 文件 | 职责 |
|:---|:---|:---|
| `govmcp.crypto` | `sm.py`, `audit.py` | SM3/SM4国密算法、不可篡改审计链 |
| `govmcp.protocol` | `server.py` | JSON-RPC 2.0 over stdio 协议层 |
| `govmcp.tools` | `registry.py` | 工具注册中心 + `@govmcp_tool` 装饰器 |
| `govmcp.server` | `approval.py` | 多级审批工作流 |
| `govmcp.models` | `registry.py`, `adapters/*` | 19个国产LLM模型适配器 |

---

## 开发状态

### 已完成 ✅

- [x] SM3 哈希算法（纯Python实现）
- [x] SM4 对称加密（纯Python实现，ECB/CBC模式）
- [x] 不可篡改审计链（SM3链式哈希）
- [x] 工具注册中心 + @govmcp_tool 装饰器
- [x] JSON-RPC 2.0 over stdio 协议层
- [x] 多级审批工作流
- [x] 信创模型注册（19个国产LLM）

### 开发中 🔧

- [ ] SM2 非对称加密（数字签名、密钥交换）
- [ ] WebSocket 传输层
- [ ] 冷钢碳排放 MCP Server 接入

### 规划中 📋

- [ ] 硬件HSM集成
- [ ] 等保2.0合规认证
- [ ] 密评适配器

---

## 文档导航

### 快速入门
- [中文快速开始](docs/zh/QUICKSTART.md)
- [English Quickstart](docs/en/QUICKSTART.md)

### 完整文档
- [中文完整文档](docs/zh/README.md)
- [English Documentation](docs/en/README.md)

### 高级指南
- [中文高级指南](docs/zh/ADVANCED.md)
- [English Advanced Guide](docs/en/ADVANCED.md)

### API 参考
- [中文API文档](docs/zh/API.md)
- [English API Reference](docs/en/API.md)

### 安全指南
- [中文安全指南](docs/zh/SECURITY.md)
- [English Security Guide](docs/en/SECURITY.md)
- [安全白皮书](docs/SECURITY.md)

### 部署指南
- [中文部署指南](docs/zh/DEPLOYMENT.md)
- [English Deployment Guide](docs/en/DEPLOYMENT.md)

### 项目文档
- [项目愿景与路线图](PROJECT.md)
- [系统架构](ARCHITECTURE.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)

---

## 开发指南

### 运行测试

```bash
# 全量测试
python3 -m pytest tests/ -v

# 单模块测试
python3 -m pytest tests/test_all.py::TestSM3 -v

# 带覆盖率
python3 -m pytest tests/ -v --cov=govmcp --cov-report=html
```

### 代码规范

```bash
# 代码格式化
ruff format .

# 代码检查
ruff check .

# 类型检查
mypy govmcp/
```

---

## 贡献指南

我们欢迎所有形式的贡献！

- 🐛 [报告Bug](https://github.com/opentaiji/govmcp/issues/new?template=bug-report.yml)
- 💡 [提出新功能](https://github.com/opentaiji/govmcp/issues/new?template=feature-request.yml)
- 📖 [完善文档](CONTRIBUTING.md)
- 🔧 [提交Pull Request](CONTRIBUTING.md)

详细贡献流程请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 讨论与支持

- 📋 [Issue Tracker](https://github.com/opentaiji/govmcp/issues)
- 💬 [Discussions](https://github.com/opentaiji/govmcp/discussions)

---

## License

Apache 2.0 — [OpenTaiji Team](https://opentaiji.com)

---

<p align="center">
  <strong>Made with ❤️ by OpenTaiji</strong>
</p>
