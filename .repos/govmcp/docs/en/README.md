# GovMCP - Government Model Context Protocol

![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

[中文文档](./README_zh.md) | English

GovMCP (Government Model Context Protocol) is a secure, standards-compliant MCP protocol implementation designed specifically for government and enterprise environments in China. It provides native support for Chinese National Cryptographic algorithms (SM2/SM3/SM4), approval workflows, audit trails, and integration with 19 domestic AI models.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Comparison with Standard MCP](#comparison-with-standard-mcp)
- [Use Cases](#use-cases)
- [Documentation](#documentation)

## Features

### Core Security Features

| Feature | Description |
|---------|-------------|
| **SM2 Encryption** | Chinese elliptic curve public key cryptography for digital signatures and key exchange |
| **SM3 Hash** | Chinese cryptographic hash algorithm for data integrity verification |
| **SM4 Encryption** | Chinese symmetric block cipher for data encryption (128-bit key) |
| **Approval Workflows** | Configurable multi-step approval chains with role-based access |
| **Audit Chains** | Immutable audit trails with cryptographic verification |
| **Transport Security** | TLS 1.3 support with Chinese cipher suites |

### Tool Ecosystem

- **Enterprise Services**: Query enterprise information, licenses, tax records
- **Personal Services**: ID verification, social security, housing fund, medical insurance
- **Approval Services**: Submit applications, query status, approval workflows
- **Security Tools**: SM2/SM3/SM4 encryption and decryption
- **Data Sharing**: Cross-department data sharing with permission control

### Domestic AI Model Support

GovMCP seamlessly integrates with 19 domestic AI models:

| Provider | Model | Status |
|----------|-------|--------|
| Baidu | Ernie (文心一言) | ✅ Supported |
| Alibaba | Qwen (通义千问) | ✅ Supported |
| iFLYTEK | Spark (讯飞星火) | ✅ Supported |
| Zhipu AI | ChatGLM (智谱ChatGLM) | ✅ Supported |
| Huawei Cloud | Pangu (盘古) | ✅ Supported |
| Tencent | Hunyuan (混元) | ✅ Supported |
| Moonshot AI | Kimi | ✅ Supported |
| China Mobile | Jiutian (九天) | ✅ Supported |
| GRG Banking | Hanhai (瀚海) | ✅ Supported |
| AISpeech | DUWA | ✅ Supported |
| Unisound | Shanhai (山海) | ✅ Supported |
| Chumen Wenwen | Monkey (序列猴子) | ✅ Supported |
| Inspur | Yuanwen (源问) | ✅ Supported |
| China Telecom | TeleChat | ✅ Supported |
| China Mobile | BaaS | ✅ Supported |
| OPPO | Andes (安第斯) | ✅ Supported |
| Xiaomi | MiLM | ✅ Supported |
| Huya | Wendao (问道) | ✅ Supported |
| JD.com | Yanxi (言犀) | ✅ Supported |
| ByteDance | Doubao (豆包) | ✅ Supported |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      GovMCP Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     Tools Layer                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │Enterprise│ │ Personal │ │ Approval │ │ Security │   │   │
│  │  │  Tools   │ │  Tools   │ │  Tools   │ │  Tools   │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     Protocol Layer                        │   │
│  │         JSON-RPC 2.0 + SM2/SM3/SM4 + Audit              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     Server Layer                          │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │   GovMCP   │  │ToolRegistry│  │   Model    │        │   │
│  │  │   Server   │  │            │  │  Adapter   │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     Crypto Layer                          │   │
│  │      ┌─────────┐  ┌─────────┐  ┌─────────┐             │   │
│  │      │   SM2   │  │   SM3   │  │   SM4   │             │   │
│  │      │(Asym)   │  │ (Hash)  │  │ (Sym)   │             │   │
│  │      └─────────┘  └─────────┘  └─────────┘             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
# Using pip
pip install govmcp

# From source
git clone https://github.com/govmcp/govmcp.git
cd govmcp
pip install -e .
```

### Basic Usage

```python
import asyncio
from govmcp.server import GovMCPServer
from govmcp.protocol import MCPProtocol

async def main():
    # Create server
    server = GovMCPServer(
        name="govmcp-demo",
        audit_enabled=True,
        encryption_enabled=True
    )

    # Create protocol
    protocol = MCPProtocol()

    # Initialize
    await protocol.initialize()
    print("GovMCP Server initialized!")

    # Call a tool
    result = await protocol.call_tool(
        server=server,
        tool_name="sm4_encrypt",
        arguments={
            "data": "Sensitive Government Data",
            "key": "32-byte-secret-key-for-sm4!!"
        }
    )
    print(f"Encrypted: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### SM2 Digital Signature

```python
from govmcp.crypto import SM2

# Generate key pair
sm2 = SM2()

# Sign
message = b"Government approval document"
signature = sm2.sign(message)

# Verify
is_valid = sm2.verify(message, signature)
print(f"Signature valid: {is_valid}")
```

### Approval Workflow

```python
from govmcp.models import ApprovalFlow, ApprovalStep, ApprovalStatus

flow = ApprovalFlow(
    id="flow-001",
    name="Enterprise Registration Approval",
    steps=[
        ApprovalStep(
            id="step-1",
            name="Window Reception",
            approver_role="window_staff"
        ),
        ApprovalStep(
            id="step-2",
            name="Department Review",
            approver_role="department_head",
            required_approvals=2
        ),
        ApprovalStep(
            id="step-3",
            name="Leadership Approval",
            approver_role="leader"
        )
    ],
    encrypt_data=True
)
```

## Comparison with Standard MCP

| Feature | Standard MCP | GovMCP |
|---------|-------------|--------|
| **Encryption** | Optional (AES-256) | ✅ Native SM2/SM3/SM4 |
| **Audit Trail** | Basic logging | ✅ Cryptographic audit chain |
| **Approval Workflow** | Not supported | ✅ Built-in workflow engine |
| **Role-based Access** | Limited | ✅ Full RBAC support |
| **Domestic Models** | External plugins | ✅ 19 models natively |
| **Government Compliance** | Generic | ✅ Designed for government |
| **Data Sovereignty** | Cloud-dependent | ✅ Fully on-premise |
| **Cryptographic Standards** | International only | ✅ Chinese national standards |

## Use Cases

### 1. Government Approval Processing

```python
# Submit approval application
result = await protocol.call_tool(
    server=server,
    tool_name="submit_approval",
    arguments={
        "flow_id": "enterprise-registration",
        "form_data": {
            "credit_code": "91110000XXXXXXXX",
            "company_name": "Example Corp",
            "business_type": "Technology"
        }
    }
)
```

### 2. Carbon Emission Monitoring

```python
# Query enterprise emission data
result = await protocol.call_tool(
    server=server,
    tool_name="query_carbon_emission",
    arguments={
        "enterprise_id": "ent-001",
        "period": "2024-Q1",
        "region": "Beijing"
    }
)
```

### 3. Cross-department Data Sharing

```python
# Request data sharing
result = await protocol.call_tool(
    server=server,
    tool_name="request_data_share",
    arguments={
        "source_dept": "tax_bureau",
        "data_type": "enterprise_tax_records",
        "purpose": "Annual inspection"
    }
)
```

## Documentation

### Chinese Documentation (docs/zh/)

| Document | Description |
|----------|-------------|
| [README](docs/zh/README.md) | Complete project documentation |
| [Quick Start](docs/zh/QUICKSTART.md) | 30-minute getting started guide |
| [Advanced Guide](docs/zh/ADVANCED.md) | Advanced features and best practices |
| [API Reference](docs/zh/API.md) | Complete API documentation |
| [Security Guide](docs/zh/SECURITY.md) | Security features and configurations |
| [Deployment Guide](docs/zh/DEPLOYMENT.md) | Deployment instructions |

### Project Documentation (Root Directory)

| Document | Description |
|----------|-------------|
| [PROJECT.md](PROJECT.md) | Project vision and roadmap |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture details |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

## License

This project is licensed under the Apache 2.0 License.

## Support

- **Issues**: [GitHub Issues](https://github.com/govmcp/govmcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/govmcp/govmcp/discussions)
- **Documentation**: [https://govmcp.readthedocs.io](https://govmcp.readthedocs.io)

---

**GovMCP** - Empowering Government Digital Transformation with Security and Compliance.
