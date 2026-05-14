# GovMCP - 系统架构

> 国产信创MCP协议 — 国密加密 + 审批工作流 + 不可篡改审计链

## 系统概述

GovMCP 是中国首个政务领域 MCP (Model Context Protocol) 标准实现，在标准 MCP 基础上针对中国政务场景叠加三大核心能力：

- **国密算法**：SM2/SM3/SM4 纯 Python 实现
- **审批工作流**：多级审批链配置
- **不可篡改审计链**：SM3 链式哈希

## 技术栈

### 核心依赖

| 依赖 | 版本 | 说明 |
|:---|:---|:---|
| Python | 3.10+ | 运行环境 |
| cryptography | >=41.0 | 国密算法实现 |
| gmssl | >=3.2 | 国密算法增强（可选） |
| pydantic | >=2.0 | 数据验证 |
| pytest | >=7.0 | 测试框架 |
| ruff | >=0.9.0 | Linting/格式化 |

### 开发工具

| 工具 | 说明 |
|:---|:---|
| ruff | 代码检查 + 格式化 |
| mypy | 类型检查 |
| pytest | 单元测试 |
| Sphinx | 文档生成 |

## 目录结构

```
govmcp/
├── govmcp/                 # 核心源码
│   ├── __init__.py        # 模块入口
│   ├── crypto/            # 国密加密模块
│   │   ├── sm.py          # SM2/SM3/SM4 算法
│   │   ├── sm2.py         # SM2 非对称加密
│   │   └── audit.py       # 审计链
│   ├── protocol/          # 协议层
│   │   ├── server.py      # JSON-RPC 2.0
│   │   ├── tasks.py       # 异步任务
│   │   └── ...
│   ├── models/            # 大模型适配
│   │   ├── registry.py    # 模型注册表
│   │   └── adapters/      # 各厂商适配器
│   ├── tools/            # 工具注册中心
│   │   ├── registry.py    # 工具管理
│   │   └── government/    # 政务工具集
│   ├── transport/         # 传输层
│   │   ├── base.py        # 传输基类
│   │   ├── websocket_server.py
│   │   └── http_server.py
│   └── server.py          # 服务端
├── tests/                 # 测试套件
├── docs/                  # 文档
│   ├── zh/               # 中文文档
│   └── en/               # 英文文档
└── scripts/              # 工具脚本
    ├── generate_docs.py  # 文档生成
    ├── gen_api_docs.py   # API文档
    └── ...
```

## 架构设计

```
┌────────────────────────────────────────────────────────────┐
│                     govmcp 架构                             │
├────────────────────────────────────────────────────────────┤
│  应用层 (App)                                               │
│  政务审批 / 碳排放监管 / 环境审计 / 智慧城市                  │
├────────────────────────────────────────────────────────────┤
│  tools/                 server/                             │
│  ToolRegistry           ApprovalFlow                        │
│  @govmcp_tool           ApprovalStatus                    │
├────────────────────────────────────────────────────────────┤
│  protocol/                                                   │
│  GovMCPServer                                               │
│  JSON-RPC 2.0 over stdio / WebSocket / HTTP                │
├────────────────────────────────────────────────────────────┤
│  crypto/                                                    │
│  SM3哈希    SM4加密    SM2签名    AuditChain               │
└────────────────────────────────────────────────────────────┘
```

## 核心模块

### 1. 国密加密 (govmcp.crypto)

- `sm3_hash()` - SM3 哈希算法
- `sm4_encrypt()` / `sm4_decrypt()` - SM4-ECB 加密
- `sm4_cbc_encrypt()` / `sm4_cbc_decrypt()` - SM4-CBC 加密
- `sm2_encrypt()` / `sm2_decrypt()` - SM2 非对称加密
- `sm2_sign()` / `sm2_verify()` - SM2 签名验签
- `AuditChain` - 不可篡改审计链

### 2. 协议层 (govmcp.protocol)

- `GovMCPServer` - MCP 服务器
- `TaskManager` - 异步任务管理
- `SamplingMessage` - 采样消息
- `ElicitRequest` - 用户交互

### 3. 工具系统 (govmcp.tools)

- `@govmcp_tool` - 工具装饰器
- `ToolRegistry` - 工具注册表
- 100+ 政务专用工具

### 4. 模型适配 (govmcp.models)

- `ModelRegistry` - 模型注册表
- 20 个国产 LLM 厂商适配器
- 48+ 国产大模型支持

## 安全特性

| 特性 | 说明 |
|:---|:---|
| SM3 哈希 | 数据完整性校验 |
| SM4 加密 | 对称加密（ECB/CBC） |
| SM2 签名 | 非对称签名/验签 |
| 审计链 | 防篡改操作记录 |
| 审批工作流 | 多级审批控制 |

## 部署方式

### 本地部署

```bash
pip install -e ".[full,ws,http]"
python -m govmcp
```

### Docker 部署

```bash
docker build -t govmcp:latest .
docker run -p 8000:8000 govmcp:latest
```

## 相关文档

- [README.md](./README.md) - 项目说明
- [CHANGELOG.md](./CHANGELOG.md) - 变更日志
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南
- [docs/zh/README.md](./docs/zh/README.md) - 中文文档
