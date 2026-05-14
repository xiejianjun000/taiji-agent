# govmcp API Reference

> **Version**: `1.0.0`
> **Generated**: 2026-05-13 15:57:50

---

## Overview

This document provides the complete API reference for govmcp. govmcp is a Chinese Government MCP Protocol implementation supporting:

- **GM Cryptography**: SM2/SM3/SM4 encryption algorithms
- **Approval Workflow**: Multi-level approval chains
- **Immutable Audit Chain**: SM3 chain hashing
- **Model Adapters**: 19+ Chinese LLM models

---

## Quick Start

### Installation

```bash
pip install govmcp
```

### Basic Usage

```python
from govmcp import GovMCPServer, sm3_hash, ApprovalFlow

# Create server
server = GovMCPServer('my-server', '1.0')

# Use GM hash
digest = sm3_hash(b'data')

# Use approval workflow
flow = ApprovalFlow(['level1', 'level2'])
```

---

## Cryptography Module

**模块路径**: `govmcp.crypto`

### `govmcp.crypto.audit`

不可篡改审计链 — SM3哈希链式防篡改

每条审计记录包含操作元数据，并通过SM3哈希链接到前一条记录。

任何对历史记录的修改都会破坏哈希链，可被 verify() 检测。

设计原则:

- 追加写入 (append-only)：无删除/修改接口

- 创世区块：第一条记录的 prev_hash = 64个'0'

- 篡改检测：遍历全链重新计算 current_hash 并与存储值比对

#### Functions

##### `__init__()`

**Location**: Line 54

---

##### `add_entry(operation: str, operator: str, input_data: bytes, output_data: bytes, approval_status: str = 'pending') -> AuditEntry`

**Location**: Line 57

追加一条审计记录。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `operation` | `str` | Yes | `-` |  |
| `operator` | `str` | Yes | `-` |  |
| `input_data` | `bytes` | Yes | `-` |  |
| `output_data` | `bytes` | Yes | `-` |  |
| `approval_status` | `str` | No | `'pending'` |  |

**Returns** `AuditEntry`

---

##### `verify() -> bool`

**Location**: Line 107

验证整条审计链的完整性。

**Returns** `bool`

---

##### `to_dict_list() -> List[dict]`

**Location**: Line 149

将审计链转换为字典列表，便于序列化。

**Returns** `List[dict]`

---

##### `export(indent: int = 2) -> str`

**Location**: Line 166

导出审计链为JSON字符串。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `indent` | `int` | No | `2` |  |

**Returns** `str`

---

#### Classes

##### `AuditEntry`
`Dataclass`

单条审计记录 — 不可篡改链上的一个区块

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `id` | `int` |
| `timestamp` | `float` |
| `operation` | `str` |
| `operator` | `str` |
| `input_hash` | `str` |
| `output_hash` | `str` |
| `approval_status` | `str` |
| `prev_hash` | `str` |
| `current_hash` | `str` |

---

##### `AuditChain`

不可篡改审计链

**Methods**

- `add_entry()` - 追加一条审计记录。
- `verify()` - 验证整条审计链的完整性。
- `to_dict_list()` - 将审计链转换为字典列表，便于序列化。
- `export()` - 导出审计链为JSON字符串。

---

### `govmcp.crypto.sm`

govmcp 国密加密模块 — SM3哈希 + SM4对称加密

SM3: 中国国家密码管理局发布的密码杂凑算法 (GB/T 32905-2016)

输出256位哈希值，强度等同于SHA-256

SM4: 中国国家密码管理局发布的对称加密算法 (GB/T 32907-2016)

128位分组密码，密钥长度128位

生产环境应使用硬件加密模块（HSM）或国密专用芯片。

本模块提供纯软件参考实现，用于开发与测试。

#### Functions

##### `sm3_hash(data: bytes) -> str`

**Location**: Line 66

SM3 国密哈希

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `bytes` | Yes | `-` |  |

**Returns** `str`

---

##### `sm4_encrypt(plaintext: bytes, key: bytes) -> bytes`

**Location**: Line 461

SM4 国密对称加密 (ECB模式)

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `plaintext` | `bytes` | Yes | `-` |  |
| `key` | `bytes` | Yes | `-` |  |

**Returns** `bytes`

---

##### `sm4_decrypt(ciphertext: bytes, key: bytes) -> bytes`

**Location**: Line 503

SM4 国密对称解密 (ECB模式)

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `ciphertext` | `bytes` | Yes | `-` |  |
| `key` | `bytes` | Yes | `-` |  |

**Returns** `bytes`

---

##### `pkcs7_pad(data: bytes, block_size: int = 16) -> bytes`

**Location**: Line 542

PKCS7 填充

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `bytes` | Yes | `-` |  |
| `block_size` | `int` | No | `16` |  |

**Returns** `bytes`

---

##### `pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes`

**Location**: Line 557

PKCS7 去填充

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `bytes` | Yes | `-` |  |
| `block_size` | `int` | No | `16` |  |

**Returns** `bytes`

---

##### `generate_sm4_iv() -> bytes`

**Location**: Line 584

生成随机SM4 IV（初始化向量）

**Returns** `bytes`

---

##### `sm4_cbc_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes`

**Location**: Line 589

SM4-CBC 国密对称加密

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `plaintext` | `bytes` | Yes | `-` |  |
| `key` | `bytes` | Yes | `-` |  |
| `iv` | `bytes` | Yes | `-` |  |

**Returns** `bytes`

---

##### `sm4_cbc_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes`

**Location**: Line 626

SM4-CBC 国密对称解密

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `ciphertext` | `bytes` | Yes | `-` |  |
| `key` | `bytes` | Yes | `-` |  |
| `iv` | `bytes` | Yes | `-` |  |

**Returns** `bytes`

---

##### `generate_sm4_key() -> bytes`

**Location**: Line 668

生成随机SM4密钥

**Returns** `bytes`

---

### `govmcp.crypto.sm2`

govmcp 国密加密模块 — SM2非对称加密

SM2: 中国国家密码管理局发布的椭圆曲线公钥密码算法 (GB/T 32918-2016)

基于256位椭圆曲线，强度等同于NIST P-256/prime256v1

功能:

- SM2 密钥对生成

- SM2 加密/解密 (ECIES风格)

- SM2 签名/验签 (ECDSA风格)

- SM2 密钥派生函数 (KDF)

生产环境应使用硬件加密模块（HSM）或国密专用芯片。

本模块提供纯软件参考实现，用于开发与测试。

#### Functions

##### `generate_sm2_keypair() -> Tuple[bytes, bytes]`

**Location**: Line 223

生成SM2密钥对

**Returns** `Tuple[bytes, bytes]`

---

##### `sm2_encrypt(plaintext: bytes, public_key: bytes) -> bytes`

**Location**: Line 254

SM2加密 (C1 || C3 || C2 格式)

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `plaintext` | `bytes` | Yes | `-` |  |
| `public_key` | `bytes` | Yes | `-` |  |

**Returns** `bytes`

---

##### `sm2_decrypt(ciphertext: bytes, private_key: bytes) -> bytes`

**Location**: Line 320

SM2解密

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `ciphertext` | `bytes` | Yes | `-` |  |
| `private_key` | `bytes` | Yes | `-` |  |

**Returns** `bytes`

---

##### `sm2_sign(data: bytes, private_key: bytes, user_id: bytes = None) -> bytes`

**Location**: Line 388

SM2签名 (GB/T 32918-2016)

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `bytes` | Yes | `-` |  |
| `private_key` | `bytes` | Yes | `-` |  |
| `user_id` | `bytes` | No | `None` |  |

**Returns** `bytes`

---

##### `sm2_verify(data: bytes, signature: bytes, public_key: bytes, user_id: bytes = None) -> bool`

**Location**: Line 455

SM2验签

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `bytes` | Yes | `-` |  |
| `signature` | `bytes` | Yes | `-` |  |
| `public_key` | `bytes` | Yes | `-` |  |
| `user_id` | `bytes` | No | `None` |  |

**Returns** `bool`

---

##### `sm2_derive_key(shared_secret: bytes, key_length: int = 32) -> bytes`

**Location**: Line 524

SM2密钥派生函数 (KDF)

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `shared_secret` | `bytes` | Yes | `-` |  |
| `key_length` | `int` | No | `32` |  |

**Returns** `bytes`

---

##### `sm2_calculate_shared_secret(private_key: bytes, peer_public_key: bytes) -> bytes`

**Location**: Line 551

SM2椭圆曲线Diffie-Hellman密钥交换 - 计算共享秘密

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `private_key` | `bytes` | Yes | `-` |  |
| `peer_public_key` | `bytes` | Yes | `-` |  |

**Returns** `bytes`

---

---

## Models Module

**模块路径**: `govmcp.models`

### `govmcp.models.adapters.baichuan`

govmcp.models.adapters.baichuan — 百川智能适配器

支持 baichuan4, baichuan-7b, baichuan-13b

#### Functions

##### `__init__(config: ModelConfig, api_key: Optional[str] = None, secret_key: Optional[str] = None) -> None`

**Location**: Line 29

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `api_key` | `Optional[str]` | No | `None` |  |
| `secret_key` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 43

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 73

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 114

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `BaichuanAdapter`

**Base Classes**: `LLMAdapter`

百川智能大模型适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |
| `secret_key` | `Optional[str]` |

**Methods**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.base`

govmcp.models.adapters.base — LLM适配器基类

定义统一的适配器接口，所有厂商适配器都应继承此类。

#### Functions

##### `__init__(config: ModelConfig) -> None`

**Location**: Line 35

初始化适配器

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 51

**装饰器**: abstractmethod

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 69

**装饰器**: abstractmethod

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 87

**装饰器**: abstractmethod

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

##### `format_messages(system: Optional[str] = None, user: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]`

**Location**: Line 104

格式化消息列表

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `system` | `Optional[str]` | No | `None` |  |
| `user` | `Optional[str]` | No | `None` |  |
| `history` | `Optional[List[Dict[str, str]]]` | No | `None` |  |

**Returns** `List[Dict[str, str]]`

---

##### `build_request_params(messages: List[Dict[str, str]], ****kwargs) -> Dict[str, Any]`

**Location**: Line 134

构建请求参数

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Dict[str, Any]`

---

##### `supports_streaming() -> bool`

**Location**: Line 177

是否支持流式输出

**Returns** `bool`

---

##### `supports_function_call() -> bool`

**Location**: Line 181

是否支持函数调用

**Returns** `bool`

---

##### `supports_vision() -> bool`

**Location**: Line 185

是否支持视觉

**Returns** `bool`

---

##### `supports_embedding() -> bool`

**Location**: Line 189

是否支持文本嵌入

**Returns** `bool`

---

#### Classes

##### `LLMAdapter`

**Base Classes**: `ABC`

LLM适配器基类

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |

**Methods**

- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量
- `format_messages()` - 格式化消息列表
- `build_request_params()` - 构建请求参数
- ... (4 more)

---

### `govmcp.models.adapters.doubao`

govmcp.models.adapters.doubao — 字节豆包适配器

支持 doubao-pro, doubao-lite

#### Functions

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**Location**: Line 29

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `api_key` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 40

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 72

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 115

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `DoubaoAdapter`

**Base Classes**: `LLMAdapter`

字节豆包大模型适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**Methods**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.hunyuan`

govmcp.models.adapters.hunyuan — 腾讯混元适配器

支持 hunyuan-lite, hunyuan-pro, hunyuan-standard

#### Functions

##### `__init__(config: ModelConfig, secret_id: Optional[str] = None, secret_key: Optional[str] = None) -> None`

**Location**: Line 29

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `secret_id` | `Optional[str]` | No | `None` |  |
| `secret_key` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 36

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 72

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 119

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `HunyuanAdapter`

**Base Classes**: `LLMAdapter`

腾讯混元大模型适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `secret_id` | `Optional[str]` |
| `secret_key` | `Optional[str]` |

**Methods**

- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.minimax`

govmcp.models.adapters.minimax — MiniMax适配器

支持 minimax-abab5, minimax-abab6, minimax-chat

#### Functions

##### `__init__(config: ModelConfig, api_key: Optional[str] = None, group_id: Optional[str] = None) -> None`

**Location**: Line 29

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `api_key` | `Optional[str]` | No | `None` |  |
| `group_id` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 43

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 77

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 124

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `MinimaxAdapter`

**Base Classes**: `LLMAdapter`

MiniMax大模型适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |
| `group_id` | `Optional[str]` |

**Methods**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.moonshot`

govmcp.models.adapters.moonshot — 月之暗面Kimi适配器

支持 kimi-chat, kimi-pro

#### Functions

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**Location**: Line 29

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `api_key` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 40

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 72

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 115

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `MoonshotAdapter`

**Base Classes**: `LLMAdapter`

月之暗面Kimi大模型适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**Methods**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.others`

govmcp.models.adapters.others — 其他厂商适配器

支持:

- sensechat-5, sensechat-4 (商汤日日新)

- qizhi-chat (360奇智)

- tuoshai-chat (拓世AI)

- wandao-chat (新华三望道)

- wenda-chat (出门问问)

- internlm-chat, internlm2-chat (书生·浦语)

- mindchat (聆心智能)

- ctyun-chat (天翼云)

- unicom-chat (联通AI)

#### Functions

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**Location**: Line 40

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `api_key` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 53

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 83

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 124

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `OthersAdapter`

**Base Classes**: `LLMAdapter`

其他国产大模型适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**Methods**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.pangu`

govmcp.models.adapters.pangu — 华为盘古适配器

支持 pangu-alpha, pangu-chat

#### Functions

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**Location**: Line 29

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `api_key` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 40

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 70

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 111

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `PanguAdapter`

**Base Classes**: `LLMAdapter`

华为盘古大模型适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**Methods**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.qwen`

govmcp.models.adapters.qwen — 阿里通义千问适配器

支持 qwen-turbo, qwen-plus, qwen-max, qwen-long, qwen-7b, qwen-14b, qwen-72b

#### Functions

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**Location**: Line 29

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `api_key` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 43

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 73

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 114

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `QwenAdapter`

**Base Classes**: `LLMAdapter`

阿里通义千问适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**Methods**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.spark`

govmcp.models.adapters.spark — 讯飞星火适配器

支持 spark-3.5, spark-4.0, spark-lite

#### Functions

##### `__init__(config: ModelConfig, app_id: Optional[str] = None, api_key: Optional[str] = None, api_secret: Optional[str] = None) -> None`

**Location**: Line 34

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `app_id` | `Optional[str]` | No | `None` |  |
| `api_key` | `Optional[str]` | No | `None` |  |
| `api_secret` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 83

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 131

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 192

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `SparkAdapter`

**Base Classes**: `LLMAdapter`

讯飞星火大模型适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `app_id` | `Optional[str]` |
| `api_key` | `Optional[str]` |
| `api_secret` | `Optional[str]` |

**Methods**

- `_generate_auth_url()` - 生成讯飞星火鉴权URL
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量
- `_format_messages()` - 格式化消息为讯飞格式

---

### `govmcp.models.adapters.wenxin`

govmcp.models.adapters.wenxin — 百度文心一言适配器

支持 ernie-4.0, ernie-3.5, ernie-3.0, ernie-bot

#### Functions

##### `__init__(config: ModelConfig, api_key: Optional[str] = None, secret_key: Optional[str] = None) -> None`

**Location**: Line 30

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `api_key` | `Optional[str]` | No | `None` |  |
| `secret_key` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 63

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 95

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 137

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `WenxinAdapter`

**Base Classes**: `LLMAdapter`

百度文心一言适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |
| `secret_key` | `Optional[str]` |

**Methods**

- `_get_access_token()` - 获取百度access_token
- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.zhipu`

govmcp.models.adapters.zhipu — 智谱AI GLM适配器

支持 glm-4, glm-4-plus, glm-3-turbo, chatglm-6b, chatglm2-6b, chatglm3-6b

#### Functions

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**Location**: Line 29

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | Yes | `-` |  |
| `api_key` | `Optional[str]` | No | `None` |  |

**Returns** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**Location**: Line 40

发送对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**Location**: Line 72

发送流式对话请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**Location**: Line 115

获取文本嵌入向量

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | Yes | `-` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `List[float]`

---

#### Classes

##### `ZhipuAdapter`

**Base Classes**: `LLMAdapter`

智谱AI GLM适配器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**Methods**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.registry`

govmcp.models.registry — 模型注册表

提供 LLMProvider 枚举、ModelConfig 数据类和 ModelRegistry 类，

用于管理所有国产大模型的注册和查询。

#### Functions

##### `get_default_registry() -> ModelRegistry`

**Location**: Line 907

获取默认模型注册表实例

**Returns** `ModelRegistry`

---

##### `register_model(provider: LLMProvider, model_id: str, config: ModelConfig) -> bool`

**Location**: Line 915

全局注册模型

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `provider` | `LLMProvider` | Yes | `-` |  |
| `model_id` | `str` | Yes | `-` |  |
| `config` | `ModelConfig` | Yes | `-` |  |

**Returns** `bool`

---

##### `get_model(model_id: str) -> Optional[ModelConfig]`

**Location**: Line 920

全局获取模型配置

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | Yes | `-` |  |

**Returns** `Optional[ModelConfig]`

---

##### `list_models(provider: Optional[LLMProvider] = None) -> List[ModelConfig]`

**Location**: Line 925

全局列出模型

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `provider` | `Optional[LLMProvider]` | No | `None` |  |

**Returns** `List[ModelConfig]`

---

##### `validate_model(model_id: str) -> bool`

**Location**: Line 930

全局验证模型

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | Yes | `-` |  |

**Returns** `bool`

---

##### `from_model_id(model_id: str) -> 'LLMProvider'`

**Location**: Line 45

**装饰器**: classmethod

根据模型ID推断provider

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | Yes | `-` |  |

**Returns** `'LLMProvider'`

---

##### `adapter_name() -> str`

**Location**: Line 91

**装饰器**: property

获取适配器模块名

**Returns** `str`

---

##### `supports_streaming() -> bool`

**Location**: Line 132

是否支持流式输出

**Returns** `bool`

---

##### `supports_function_call() -> bool`

**Location**: Line 136

是否支持函数调用

**Returns** `bool`

---

##### `supports_vision() -> bool`

**Location**: Line 140

是否支持视觉

**Returns** `bool`

---

##### `supports_embedding() -> bool`

**Location**: Line 144

是否支持文本嵌入

**Returns** `bool`

---

##### `__init__() -> None`

**Location**: Line 184

**Returns** `None`

---

##### `register_model(provider: LLMProvider, model_id: str, config: ModelConfig) -> bool`

**Location**: Line 791

注册一个新模型

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `provider` | `LLMProvider` | Yes | `-` |  |
| `model_id` | `str` | Yes | `-` |  |
| `config` | `ModelConfig` | Yes | `-` |  |

**Returns** `bool`

---

##### `get_model(model_id: str) -> Optional[ModelConfig]`

**Location**: Line 808

获取模型配置

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | Yes | `-` |  |

**Returns** `Optional[ModelConfig]`

---

##### `list_models(provider: Optional[LLMProvider] = None) -> List[ModelConfig]`

**Location**: Line 820

列出所有模型

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `provider` | `Optional[LLMProvider]` | No | `None` |  |

**Returns** `List[ModelConfig]`

---

##### `validate_model(model_id: str) -> bool`

**Location**: Line 834

验证模型是否已注册

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | Yes | `-` |  |

**Returns** `bool`

---

##### `get_adapter(model_id: str) -> Optional[Any]`

**Location**: Line 846

获取模型的适配器实例

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | Yes | `-` |  |

**Returns** `Optional[Any]`

---

##### `count() -> int`

**Location**: Line 883

返回已注册模型数量

**Returns** `int`

---

##### `get_providers() -> List[LLMProvider]`

**Location**: Line 887

返回所有已使用的provider列表

**Returns** `List[LLMProvider]`

---

##### `clear() -> None`

**Location**: Line 891

清空注册表 (测试用)

**Returns** `None`

---

#### Classes

##### `LLMProvider`
`Enum`

**Base Classes**: `Enum`

国产大模型厂商枚举

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `WENXIN` | `'wenxin'` |
| `QWEN` | `'qwen'` |
| `ZHIPU` | `'zhipu'` |
| `SPARK` | `'spark'` |
| `HUNYUAN` | `'hunyuan'` |
| `PANGU` | `'pangu'` |
| `DOUBAO` | `'doubao'` |
| `GPT360` | `'gpt360'` |
| `MINIMAX` | `'minimax'` |
| `MOONSHOT` | `'moonshot'` |
| `BAICHUAN` | `'baichuan'` |
| `SENSECHAT` | `'sensechat'` |
| `QIZHI` | `'qizhi'` |
| `TUOSHAI` | `'tuoshai'` |
| `WANDAO` | `'wandao'` |
| `WENDA` | `'wenda'` |
| `INTERNNLM` | `'internlm'` |
| `MINDCHAT` | `'mindchat'` |
| `CTYUN` | `'ctyun'` |
| `UNICOM` | `'unicom'` |
| `UNKNOWN` | `'unknown'` |

**Methods**

- `from_model_id()` - 根据模型ID推断provider
- `adapter_name()` - 获取适配器模块名

---

##### `ModelConfig`
`Dataclass`

模型配置数据类

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `provider` | `LLMProvider` |
| `model_id` | `str` |
| `api_base` | `str` |
| `capabilities` | `Dict[str, bool]` |
| `max_tokens` | `int` |
| `temperature` | `float` |
| `top_p` | `float` |
| `timeout` | `float` |
| `extra` | `Dict[str, Any]` |

**Methods**

- `supports_streaming()` - 是否支持流式输出
- `supports_function_call()` - 是否支持函数调用
- `supports_vision()` - 是否支持视觉
- `supports_embedding()` - 是否支持文本嵌入

---

##### `ModelRegistry`

模型注册表

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `_instance` | `Optional['ModelRegistry']` |
| `_models` | `Dict[str, ModelConfig]` |
| `_adapters` | `Dict[str, Any]` |

**Methods**

- `_register_builtin_models()` - 注册内置的48个国产大模型
- `register_model()` - 注册一个新模型
- `get_model()` - 获取模型配置
- `list_models()` - 列出所有模型
- `validate_model()` - 验证模型是否已注册
- ... (4 more)

---

---

## Protocol Module

**模块路径**: `govmcp.protocol`

### `govmcp.protocol.authorization`

govmcp.protocol.authorization — 授权扩展 (MCP 2025.11)

提供 OAuth 2.0 授权流程和细粒度权限控制支持：

- OAuth 2.0 授权码流程

- Authorization Extensions

- 细粒度权限控制

- 令牌管理

#### Functions

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 68

转换为字典

**Returns** `Dict[str, Any]`

---

##### `is_valid() -> bool`

**Location**: Line 94

检查是否有效

**Returns** `bool`

---

##### `mark_used() -> None`

**Location**: Line 98

标记为已使用

**Returns** `None`

---

##### `is_expired() -> float`

**Location**: Line 117

检查是否过期

**Returns** `float`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 121

转换为字典

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'TokenInfo'`

**Location**: Line 134

**装饰器**: classmethod

从字典创建

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `'TokenInfo'`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 157

转换为字典

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'Permission'`

**Location**: Line 168

**装饰器**: classmethod

从字典创建

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `'Permission'`

---

##### `is_valid() -> bool`

**Location**: Line 190

检查是否有效

**Returns** `bool`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 196

转换为字典

**Returns** `Dict[str, Any]`

---

##### `__init__(access_token_ttl: int = 3600, refresh_token_ttl: int = 86400 * 7, authorization_code_ttl: int = 600)`

**Location**: Line 217

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `access_token_ttl` | `int` | No | `3600` |  |
| `refresh_token_ttl` | `int` | No | `86400 * 7` |  |
| `authorization_code_ttl` | `int` | No | `600` |  |

---

##### `register_client(client_id: str, client_secret: Optional[str] = None, client_name: str = '', redirect_uris: Optional[List[str]] = None, allowed_scopes: Optional[Set[str]] = None, grant_types: Optional[Set[GrantType]] = None, metadata: Optional[Dict[str, Any]] = None) -> ClientInfo`

**Location**: Line 238

注册客户端

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | Yes | `-` |  |
| `client_secret` | `Optional[str]` | No | `None` |  |
| `client_name` | `str` | No | `''` |  |
| `redirect_uris` | `Optional[List[str]]` | No | `None` |  |
| `allowed_scopes` | `Optional[Set[str]]` | No | `None` |  |
| `grant_types` | `Optional[Set[GrantType]]` | No | `None` |  |
| `metadata` | `Optional[Dict[str, Any]]` | No | `None` |  |

**Returns** `ClientInfo`

---

##### `get_client(client_id: str) -> Optional[ClientInfo]`

**Location**: Line 262

获取客户端信息

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | Yes | `-` |  |

**Returns** `Optional[ClientInfo]`

---

##### `validate_client(client_id: str, client_secret: Optional[str] = None) -> bool`

**Location**: Line 267

验证客户端凭证

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | Yes | `-` |  |
| `client_secret` | `Optional[str]` | No | `None` |  |

**Returns** `bool`

---

##### `create_authorization_url(client_id: str, redirect_uri: str, scope: Optional[str] = None, state: Optional[str] = None, code_challenge: Optional[str] = None, code_challenge_method: Optional[str] = None) -> str`

**Location**: Line 277

创建授权 URL

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | Yes | `-` |  |
| `redirect_uri` | `str` | Yes | `-` |  |
| `scope` | `Optional[str]` | No | `None` |  |
| `state` | `Optional[str]` | No | `None` |  |
| `code_challenge` | `Optional[str]` | No | `None` |  |
| `code_challenge_method` | `Optional[str]` | No | `None` |  |

**Returns** `str`

---

##### `authorize(code: str, user_id: str) -> bool`

**Location**: Line 341

用户授权确认

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `code` | `str` | Yes | `-` |  |
| `user_id` | `str` | Yes | `-` |  |

**Returns** `bool`

---

##### `exchange_code(code: str, client_id: str, client_secret: Optional[str] = None, code_verifier: Optional[str] = None) -> TokenInfo`

**Location**: Line 364

交换授权码获取令牌

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `code` | `str` | Yes | `-` |  |
| `client_id` | `str` | Yes | `-` |  |
| `client_secret` | `Optional[str]` | No | `None` |  |
| `code_verifier` | `Optional[str]` | No | `None` |  |

**Returns** `TokenInfo`

---

##### `refresh_access_token(refresh_token: str, client_id: Optional[str] = None, client_secret: Optional[str] = None, scope: Optional[str] = None) -> TokenInfo`

**Location**: Line 446

刷新访问令牌

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `refresh_token` | `str` | Yes | `-` |  |
| `client_id` | `Optional[str]` | No | `None` |  |
| `client_secret` | `Optional[str]` | No | `None` |  |
| `scope` | `Optional[str]` | No | `None` |  |

**Returns** `TokenInfo`

---

##### `validate_token(access_token: str) -> Optional[TokenInfo]`

**Location**: Line 518

验证访问令牌

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `access_token` | `str` | Yes | `-` |  |

**Returns** `Optional[TokenInfo]`

---

##### `revoke_token(token: str) -> bool`

**Location**: Line 528

撤销令牌

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `token` | `str` | Yes | `-` |  |

**Returns** `bool`

---

##### `add_authorization_hook(hook: Callable[[str, Dict[str, Any]], bool]) -> None`

**Location**: Line 539

添加授权钩子

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `hook` | `Callable[[str, Dict[str, Any]], bool]` | Yes | `-` |  |

**Returns** `None`

---

##### `check_permission(token: str, resource: str, action: str) -> bool`

**Location**: Line 546

检查权限

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `token` | `str` | Yes | `-` |  |
| `resource` | `str` | Yes | `-` |  |
| `action` | `str` | Yes | `-` |  |

**Returns** `bool`

---

##### `grant_permissions(grant_id: str, permissions: List[Permission]) -> bool`

**Location**: Line 591

授予权限

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `grant_id` | `str` | Yes | `-` |  |
| `permissions` | `List[Permission]` | Yes | `-` |  |

**Returns** `bool`

---

##### `revoke_permissions(grant_id: str, resources: Optional[List[str]] = None) -> bool`

**Location**: Line 604

撤销权限

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `grant_id` | `str` | Yes | `-` |  |
| `resources` | `Optional[List[str]]` | No | `None` |  |

**Returns** `bool`

---

##### `cleanup_expired() -> int`

**Location**: Line 621

清理过期数据

**Returns** `int`

---

##### `get_stats() -> Dict[str, Any]`

**Location**: Line 668

获取统计信息

**Returns** `Dict[str, Any]`

---

##### `__init__(authorization_manager: AuthorizationManager)`

**Location**: Line 684

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `authorization_manager` | `AuthorizationManager` | Yes | `-` |  |

---

##### `add_policy(policy_id: str, effect: str, principals: List[str], resources: List[str], actions: List[str], conditions: Optional[Dict[str, Any]] = None) -> None`

**Location**: Line 689

添加策略

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `policy_id` | `str` | Yes | `-` |  |
| `effect` | `str` | Yes | `-` |  |
| `principals` | `List[str]` | Yes | `-` |  |
| `resources` | `List[str]` | Yes | `-` |  |
| `actions` | `List[str]` | Yes | `-` |  |
| `conditions` | `Optional[Dict[str, Any]]` | No | `None` |  |

**Returns** `None`

---

##### `evaluate(principal: str, resource: str, action: str, context: Optional[Dict[str, Any]] = None) -> bool`

**Location**: Line 722

评估权限

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `principal` | `str` | Yes | `-` |  |
| `resource` | `str` | Yes | `-` |  |
| `action` | `str` | Yes | `-` |  |
| `context` | `Optional[Dict[str, Any]]` | No | `None` |  |

**Returns** `bool`

---

##### `remove_policy(policy_id: str) -> bool`

**Location**: Line 785

移除策略

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `policy_id` | `str` | Yes | `-` |  |

**Returns** `bool`

---

##### `get_policies(policy_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]`

**Location**: Line 793

获取策略

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `policy_id` | `Optional[str]` | No | `None` |  |

**Returns** `Dict[str, List[Dict[str, Any]]]`

---

#### Classes

##### `GrantType`
`Enum`

**Base Classes**: `str | Enum`

授权类型

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `AUTHORIZATION_CODE` | `'authorization_code'` |
| `CLIENT_CREDENTIALS` | `'client_credentials'` |
| `REFRESH_TOKEN` | `'refresh_token'` |
| `IMPLICIT` | `'implicit'` |

---

##### `TokenType`
`Enum`

**Base Classes**: `str | Enum`

令牌类型

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `BEARER` | `'bearer'` |
| `MAC` | `'mac'` |

---

##### `AuthorizationScope`
`Enum`

**Base Classes**: `str | Enum`

授权范围

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `READ` | `'read'` |
| `WRITE` | `'write'` |
| `ADMIN` | `'admin'` |
| `EXECUTE` | `'execute'` |
| `READ_RESOURCES` | `'resources:read'` |
| `WRITE_RESOURCES` | `'resources:write'` |
| `READ_TOOLS` | `'tools:read'` |
| `WRITE_TOOLS` | `'tools:write'` |
| `READ_PROMPTS` | `'prompts:read'` |
| `WRITE_PROMPTS` | `'prompts:write'` |

---

##### `ClientInfo`
`Dataclass`

OAuth 客户端信息

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `client_id` | `str` |
| `client_secret` | `Optional[str]` |
| `client_name` | `str` |
| `redirect_uris` | `List[str]` |
| `allowed_scopes` | `Set[str]` |
| `grant_types` | `Set[GrantType]` |
| `metadata` | `Dict[str, Any]` |

**Methods**

- `to_dict()` - 转换为字典

---

##### `AuthorizationCode`
`Dataclass`

授权码

**Attributes**

| 名称 | 类型 |
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

**Methods**

- `is_valid()` - 检查是否有效
- `mark_used()` - 标记为已使用

---

##### `TokenInfo`
`Dataclass`

令牌信息

**Attributes**

| 名称 | 类型 |
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

**Methods**

- `is_expired()` - 检查是否过期
- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `Permission`
`Dataclass`

权限

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `resource` | `str` |
| `actions` | `Set[str]` |
| `conditions` | `Optional[Dict[str, Any]]` |

**Methods**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `AuthorizationGrant`
`Dataclass`

授权授予

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `grant_id` | `str` |
| `user_id` | `str` |
| `client_id` | `str` |
| `scopes` | `Set[str]` |
| `permissions` | `List[Permission]` |
| `issued_at` | `float` |
| `expires_at` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

**Methods**

- `is_valid()` - 检查是否有效
- `to_dict()` - 转换为字典

---

##### `AuthorizationManager`

授权管理器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `access_token_ttl` | `int` |
| `refresh_token_ttl` | `int` |
| `authorization_code_ttl` | `int` |

**Methods**

- `register_client()` - 注册客户端
- `get_client()` - 获取客户端信息
- `validate_client()` - 验证客户端凭证
- `create_authorization_url()` - 创建授权 URL
- `authorize()` - 用户授权确认
- ... (11 more)

---

##### `FineGrainedPermissionManager`

细粒度权限管理器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `authorization_manager` | `AuthorizationManager` |

**Methods**

- `add_policy()` - 添加策略
- `evaluate()` - 评估权限
- `_match_principal()` - 匹配主体
- `_match_resource()` - 匹配资源
- `_match_action()` - 匹配操作
- ... (3 more)

---

### `govmcp.protocol.elicitation`

govmcp.protocol.elicitation — 用户交互支持 (MCP 2025.11)

提供安全带外用户交互功能，支持：

- 信息请求（ElicitRequest）

- URL Mode Elicitation

- 表单交互

- 安全提示确认

#### Functions

##### `create_secure_prompt_request(message: str, resource_uri: Optional[str] = None, timeout: float = 300.0) -> ElicitRequest`

**Location**: Line 563

创建安全提示确认请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `str` | Yes | `-` |  |
| `resource_uri` | `Optional[str]` | No | `None` |  |
| `timeout` | `float` | No | `300.0` |  |

**Returns** `ElicitRequest`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 67

转换为字典

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'ElicitRequest'`

**Location**: Line 83

**装饰器**: classmethod

从字典创建

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `'ElicitRequest'`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 112

转换为字典

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'ElicitResponse'`

**Location**: Line 129

**装饰器**: classmethod

从字典创建

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `'ElicitResponse'`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 163

转换为字典

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'URLElicitation'`

**Location**: Line 182

**装饰器**: classmethod

从字典创建

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `'URLElicitation'`

---

##### `handle_request(request: ElicitRequest) -> ElicitResponse`

**Location**: Line 200

处理交互请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `ElicitRequest` | Yes | `-` |  |

**Returns** `ElicitResponse`

---

##### `can_handle(request: ElicitRequest) -> bool`

**Location**: Line 207

检查是否可以处理

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `ElicitRequest` | Yes | `-` |  |

**Returns** `bool`

---

##### `__init__(input_func: Optional[Callable[[str], str]] = None)`

**Location**: Line 215

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `input_func` | `Optional[Callable[[str], str]]` | No | `None` |  |

---

##### `handle_request(request: ElicitRequest) -> ElicitResponse`

**Location**: Line 218

处理交互请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `ElicitRequest` | Yes | `-` |  |

**Returns** `ElicitResponse`

---

##### `__init__()`

**Location**: Line 264

---

##### `add_handler(handler: ElicitationHandler) -> None`

**Location**: Line 272

添加处理器

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `ElicitationHandler` | Yes | `-` |  |

**Returns** `None`

---

##### `set_default_handler(handler: ElicitationHandler) -> None`

**Location**: Line 276

设置默认处理器

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `ElicitationHandler` | Yes | `-` |  |

**Returns** `None`

---

##### `register_callback(request_id: str, callback: Callable[[ElicitResponse], None]) -> None`

**Location**: Line 280

注册回调

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | Yes | `-` |  |
| `callback` | `Callable[[ElicitResponse], None]` | Yes | `-` |  |

**Returns** `None`

---

##### `create_request(message: str, requested_schema: Optional[Dict[str, Any]] = None, elicit_type: Union[ElicitType, str] = ElicitType.REQUEST, timeout: float = 300.0, metadata: Optional[Dict[str, Any]] = None) -> ElicitRequest`

**Location**: Line 288

创建交互请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `str` | Yes | `-` |  |
| `requested_schema` | `Optional[Dict[str, Any]]` | No | `None` |  |
| `elicit_type` | `Union[ElicitType, str]` | No | `ElicitType.REQUEST` |  |
| `timeout` | `float` | No | `300.0` |  |
| `metadata` | `Optional[Dict[str, Any]]` | No | `None` |  |

**Returns** `ElicitRequest`

---

##### `get_request(request_id: str) -> Optional[ElicitRequest]`

**Location**: Line 325

获取交互请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | Yes | `-` |  |

**Returns** `Optional[ElicitRequest]`

---

##### `submit_response(response: ElicitResponse) -> bool`

**Location**: Line 330

提交响应

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `response` | `ElicitResponse` | Yes | `-` |  |

**Returns** `bool`

---

##### `accept(request_id: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool`

**Location**: Line 360

接受请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | Yes | `-` |  |
| `value` | `Any` | Yes | `-` |  |
| `metadata` | `Optional[Dict[str, Any]]` | No | `None` |  |

**Returns** `bool`

---

##### `reject(request_id: str, error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool`

**Location**: Line 375

拒绝请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | Yes | `-` |  |
| `error` | `Optional[str]` | No | `None` |  |
| `metadata` | `Optional[Dict[str, Any]]` | No | `None` |  |

**Returns** `bool`

---

##### `cancel(request_id: str) -> bool`

**Location**: Line 390

取消请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | Yes | `-` |  |

**Returns** `bool`

---

##### `expire_requests() -> int`

**Location**: Line 404

使过期的请求过期

**Returns** `int`

---

##### `get_pending_requests(limit: int = 100) -> List[ElicitRequest]`

**Location**: Line 431

获取待处理的请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `limit` | `int` | No | `100` |  |

**Returns** `List[ElicitRequest]`

---

##### `get_response(request_id: str) -> Optional[ElicitResponse]`

**Location**: Line 441

获取响应

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | Yes | `-` |  |

**Returns** `Optional[ElicitResponse]`

---

##### `get_pending_count() -> int`

**Location**: Line 446

获取待处理请求数量

**Returns** `int`

---

##### `create_url_elicitation(url: str, title: str, method: str = 'GET', headers: Optional[Dict[str, str]] = None, body: Optional[str] = None, timeout: float = 300.0, metadata: Optional[Dict[str, Any]] = None) -> URLElicitation`

**Location**: Line 451

创建 URL 交互

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `url` | `str` | Yes | `-` |  |
| `title` | `str` | Yes | `-` |  |
| `method` | `str` | No | `'GET'` |  |
| `headers` | `Optional[Dict[str, str]]` | No | `None` |  |
| `body` | `Optional[str]` | No | `None` |  |
| `timeout` | `float` | No | `300.0` |  |
| `metadata` | `Optional[Dict[str, Any]]` | No | `None` |  |

**Returns** `URLElicitation`

---

##### `create_confirm_request(message: str, title: Optional[str] = None, timeout: float = 300.0) -> ElicitRequest`

**Location**: Line 488

创建确认请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `str` | Yes | `-` |  |
| `title` | `Optional[str]` | No | `None` |  |
| `timeout` | `float` | No | `300.0` |  |

**Returns** `ElicitRequest`

---

##### `create_input_request(message: str, field_name: str, field_type: str = 'string', required: bool = True, timeout: float = 300.0) -> ElicitRequest`

**Location**: Line 506

创建输入请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `str` | Yes | `-` |  |
| `field_name` | `str` | Yes | `-` |  |
| `field_type` | `str` | No | `'string'` |  |
| `required` | `bool` | No | `True` |  |
| `timeout` | `float` | No | `300.0` |  |

**Returns** `ElicitRequest`

---

##### `create_select_request(message: str, options: List[str], timeout: float = 300.0) -> ElicitRequest`

**Location**: Line 526

创建选择请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `str` | Yes | `-` |  |
| `options` | `List[str]` | Yes | `-` |  |
| `timeout` | `float` | No | `300.0` |  |

**Returns** `ElicitRequest`

---

##### `get_stats() -> Dict[str, Any]`

**Location**: Line 546

获取统计信息

**Returns** `Dict[str, Any]`

---

#### Classes

##### `ElicitType`
`Enum`

**Base Classes**: `str | Enum`

交互类型

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `REQUEST` | `'request'` |
| `CONFIRM` | `'confirm'` |
| `INPUT` | `'input'` |
| `SELECT` | `'select'` |
| `URL` | `'url'` |

---

##### `ElicitStatus`
`Enum`

**Base Classes**: `str | Enum`

交互状态

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `PENDING` | `'pending'` |
| `ACCEPTED` | `'accepted'` |
| `REJECTED` | `'rejected'` |
| `EXPIRED` | `'expired'` |
| `CANCELED` | `'canceled'` |

---

##### `ElicitRequest`
`Dataclass`

用户交互请求

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `message` | `str` |
| `requested_schema` | `Dict[str, Any]` |
| `elicit_type` | `Union[ElicitType, str]` |
| `timeout` | `float` |
| `id` | `Optional[str]` |
| `created_at` | `Optional[float]` |
| `expires_at` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

**Methods**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `ElicitResponse`
`Dataclass`

用户交互响应

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `request_id` | `str` |
| `status` | `Union[ElicitStatus, str]` |
| `value` | `Optional[Any]` |
| `error` | `Optional[str]` |
| `responded_at` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

**Methods**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `URLElicitation`
`Dataclass`

URL Mode Elicitation

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `url` | `str` |
| `title` | `str` |
| `request_id` | `str` |
| `method` | `str` |
| `headers` | `Dict[str, str]` |
| `body` | `Optional[str]` |
| `timeout` | `float` |
| `created_at` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

**Methods**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `ElicitationHandler`

交互处理器接口

**Methods**

- `handle_request()` - 处理交互请求
- `can_handle()` - 检查是否可以处理

---

##### `ConsoleElicitationHandler`

**Base Classes**: `ElicitationHandler`

控制台交互处理器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `input_func` | `Optional[Callable[[str], str]]` |

**Methods**

- `handle_request()` - 处理交互请求
- `_get_confirmation()` - 获取确认
- `_get_input()` - 获取输入

---

##### `ElicitationManager`

交互管理器

**Methods**

- `add_handler()` - 添加处理器
- `set_default_handler()` - 设置默认处理器
- `register_callback()` - 注册回调
- `create_request()` - 创建交互请求
- `get_request()` - 获取交互请求
- ... (13 more)

---

### `govmcp.protocol.http_server`

govmcp.protocol.http_server — HTTP/SSE 传输层服务器

基于 aiohttp 实现 MCP HTTP/SSE 服务器，支持:

- Streamable HTTP 传输

- Server-Sent Events (SSE)

- SM4-CBC 加密传输（可选）

- SM3 消息完整性校验

- Token 认证

- 远程 MCP 连接

#### Functions

##### `to_web_response() -> web.Response`

**Location**: Line 75

转换为 aiohttp Response

**Returns** `web.Response`

---

##### `__init__(host: str = '0.0.0.0', port: int = 8080, path: str = '/mcp', sse_path: str = '/mcp/sse', auth_token: Optional[str] = None, crypto_enabled: bool = False, sm4_key: Optional[bytes] = None, max_message_size: int = 10 * 1024 * 1024, request_timeout: float = 60.0, enable_cors: bool = True, cors_origins: Optional[List[str]] = None, enable_sse: bool = True, sse_heartbeat: float = 15.0, log_level: int = logging.INFO) -> None`

**Location**: Line 115

初始化 HTTP 服务器。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `host` | `str` | No | `'0.0.0.0'` |  |
| `port` | `int` | No | `8080` |  |
| `path` | `str` | No | `'/mcp'` |  |
| `sse_path` | `str` | No | `'/mcp/sse'` |  |
| `auth_token` | `Optional[str]` | No | `None` |  |
| `crypto_enabled` | `bool` | No | `False` |  |
| `sm4_key` | `Optional[bytes]` | No | `None` |  |
| `max_message_size` | `int` | No | `10 * 1024 * 1024` |  |
| `request_timeout` | `float` | No | `60.0` |  |
| `enable_cors` | `bool` | No | `True` |  |
| `cors_origins` | `Optional[List[str]]` | No | `None` |  |
| `enable_sse` | `bool` | No | `True` |  |
| `sse_heartbeat` | `float` | No | `15.0` |  |
| `log_level` | `int` | No | `logging.INFO` |  |

**Returns** `None`

---

##### `set_message_handler(handler: Callable[[HTTPRequest], Any]) -> None`

**Location**: Line 179

设置消息处理器。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `Callable[[HTTPRequest], Any]` | Yes | `-` |  |

**Returns** `None`

---

##### `async start(handler: Optional[Callable[[HTTPRequest], Any]] = None) -> None`

**Location**: Line 188

启动 HTTP 服务器。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `Optional[Callable[[HTTPRequest], Any]]` | No | `None` |  |

**Returns** `None`

---

##### `async stop() -> None`

**Location**: Line 219

停止 HTTP 服务器

**Returns** `None`

---

##### `async broadcast_sse(event: str, data: Any) -> int`

**Location**: Line 242

广播 SSE 事件给所有订阅者。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `event` | `str` | Yes | `-` |  |
| `data` | `Any` | Yes | `-` |  |

**Returns** `int`

---

##### `get_sse_subscriber_count() -> int`

**Location**: Line 262

获取 SSE 订阅者数量

**Returns** `int`

---

##### `async handle_message(request: HTTPRequest) -> Optional[Dict[str, Any]]`

**Location**: Line 502

默认消息处理器（需要外部设置实际的处理器）。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `HTTPRequest` | Yes | `-` |  |

**Returns** `Optional[Dict[str, Any]]`

---

##### `create_stdio_compatible(name: str, version: str, handler: Callable[[HTTPRequest], Any], crypto_enabled: bool = False) -> HTTPServer`

**Location**: Line 515

**装饰器**: staticmethod

创建与 stdio 服务器兼容的 HTTP 服务器

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `version` | `str` | Yes | `-` |  |
| `handler` | `Callable[[HTTPRequest], Any]` | Yes | `-` |  |
| `crypto_enabled` | `bool` | No | `False` |  |

**Returns** `HTTPServer`

---

##### `create_secure(name: str, version: str, handler: Callable[[HTTPRequest], Any], auth_token: str) -> HTTPServer`

**Location**: Line 531

**装饰器**: staticmethod

创建带认证的 HTTP 服务器

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `version` | `str` | Yes | `-` |  |
| `handler` | `Callable[[HTTPRequest], Any]` | Yes | `-` |  |
| `auth_token` | `str` | Yes | `-` |  |

**Returns** `HTTPServer`

---

##### `async heartbeat()`

**Location**: Line 405

---

#### Classes

##### `HTTPMethod`
`Enum`

**Base Classes**: `Enum`

HTTP 方法

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `POST` | `'POST'` |
| `GET` | `'GET'` |

---

##### `HTTPRequest`
`Dataclass`

HTTP 请求封装

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `method` | `str` |
| `path` | `str` |
| `headers` | `Dict[str, str]` |
| `body` | `Optional[Dict[str, Any]]` |
| `query_params` | `Dict[str, str]` |

---

##### `HTTPResponse`
`Dataclass`

HTTP 响应封装

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `status` | `int` |
| `headers` | `Dict[str, str]` |
| `body` | `Optional[Any]` |

**Methods**

- `to_web_response()` - 转换为 aiohttp Response

---

##### `HTTPServer`

HTTP/SSE MCP 服务器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `host` | `str` |
| `port` | `int` |
| `path` | `str` |
| `sse_path` | `str` |
| `auth_token` | `Optional[str]` |
| `crypto_enabled` | `bool` |
| `sm4_key` | `Optional[bytes]` |
| `max_message_size` | `int` |
| `request_timeout` | `float` |
| `enable_cors` | `bool` |
| `cors_origins` | `Optional[List[str]]` |
| `enable_sse` | `bool` |
| `sse_heartbeat` | `float` |
| `log_level` | `int` |

**Methods**

- `set_message_handler()` - 设置消息处理器。
- `get_sse_subscriber_count()` - 获取 SSE 订阅者数量
- `_setup_routes()` - 设置路由
- `_setup_middleware()` - 设置中间件
- `_check_auth()` - 检查认证
- ... (3 more)

---

##### `HTTPServerFactory`

HTTP 服务器工厂

**Methods**

- `create_stdio_compatible()` - 创建与 stdio 服务器兼容的 HTTP 服务器
- `create_secure()` - 创建带认证的 HTTP 服务器

---

### `govmcp.protocol.sampling`

govmcp.protocol.sampling — 异步采样支持 (MCP 2025.11)

提供 LLM 采样能力，支持异步消息生成、采样参数配置和采样策略。

#### Functions

##### `create_sampling_request(messages: List[Dict[str, Any]], temperature: float = 0.7, max_tokens: int = 4096, ****kwargs) -> SamplingCreateMessageRequest`

**Location**: Line 515

创建采样请求的便捷函数

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, Any]]` | Yes | `-` |  |
| `temperature` | `float` | No | `0.7` |  |
| `max_tokens` | `int` | No | `4096` |  |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `SamplingCreateMessageRequest`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 49

转换为字典

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'SamplingMessage'`

**Location**: Line 61

**装饰器**: classmethod

从字典创建

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `'SamplingMessage'`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 92

转换为字典

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'SamplingParameters'`

**Location**: Line 114

**装饰器**: classmethod

从字典创建

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `'SamplingParameters'`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 150

转换为字典

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'SamplingCreateMessageRequest'`

**Location**: Line 170

**装饰器**: classmethod

从字典创建

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `'SamplingCreateMessageRequest'`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 201

转换为字典

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'SamplingResponse'`

**Location**: Line 222

**装饰器**: classmethod

从字典创建

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `'SamplingResponse'`

---

##### `sample(messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

**Location**: Line 240

同步采样

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[SamplingMessage]` | Yes | `-` |  |
| `parameters` | `SamplingParameters` | Yes | `-` |  |

**Returns** `SamplingResponse`

---

##### `async sample_async(messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

**Location**: Line 248

异步采样

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[SamplingMessage]` | Yes | `-` |  |
| `parameters` | `SamplingParameters` | Yes | `-` |  |

**Returns** `SamplingResponse`

---

##### `__init__()`

**Location**: Line 264

---

##### `register_provider(model_name: str, provider: SamplingProvider) -> None`

**Location**: Line 270

注册采样提供者

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_name` | `str` | Yes | `-` |  |
| `provider` | `SamplingProvider` | Yes | `-` |  |

**Returns** `None`

---

##### `set_default_model(model_name: str) -> None`

**Location**: Line 278

设置默认模型

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_name` | `str` | Yes | `-` |  |

**Returns** `None`

---

##### `add_hook(hook: Callable[[str, Any], None]) -> None`

**Location**: Line 282

添加采样钩子

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `hook` | `Callable[[str, Any], None]` | Yes | `-` |  |

**Returns** `None`

---

##### `remove_hook(hook: Callable[[str, Any], None]) -> None`

**Location**: Line 286

移除采样钩子

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `hook` | `Callable[[str, Any], None]` | Yes | `-` |  |

**Returns** `None`

---

##### `create_message(request: SamplingCreateMessageRequest) -> SamplingResponse`

**Location**: Line 299

创建采样消息（同步）

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `SamplingCreateMessageRequest` | Yes | `-` |  |

**Returns** `SamplingResponse`

---

##### `async create_message_async(request: SamplingCreateMessageRequest) -> SamplingResponse`

**Location**: Line 365

创建采样消息（异步）

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `SamplingCreateMessageRequest` | Yes | `-` |  |

**Returns** `SamplingResponse`

---

##### `get_message_history(limit: Optional[int] = None) -> List[SamplingMessage]`

**Location**: Line 446

获取消息历史

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `limit` | `Optional[int]` | No | `None` |  |

**Returns** `List[SamplingMessage]`

---

##### `clear_history() -> None`

**Location**: Line 455

清空消息历史

**Returns** `None`

---

##### `get_stats() -> Dict[str, Any]`

**Location**: Line 459

获取采样统计

**Returns** `Dict[str, Any]`

---

##### `__init__(model_id: str)`

**Location**: Line 477

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | Yes | `-` |  |

---

##### `sample(messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

**Location**: Line 480

执行采样

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[SamplingMessage]` | Yes | `-` |  |
| `parameters` | `SamplingParameters` | Yes | `-` |  |

**Returns** `SamplingResponse`

---

##### `async sample_async(messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

**Location**: Line 497

异步执行采样

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[SamplingMessage]` | Yes | `-` |  |
| `parameters` | `SamplingParameters` | Yes | `-` |  |

**Returns** `SamplingResponse`

---

#### Classes

##### `Role`
`Enum`

**Base Classes**: `str | Enum`

消息角色

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `USER` | `'user'` |
| `ASSISTANT` | `'assistant'` |
| `SYSTEM` | `'system'` |

---

##### `SamplingMessageRole`
`Enum`

**Base Classes**: `str | Enum`

采样消息角色 (MCP 2025.11)

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `USER` | `'user'` |
| `ASSISTANT` | `'assistant'` |
| `SYSTEM` | `'system'` |

---

##### `SamplingMessage`
`Dataclass`

采样消息

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `role` | `Union[Role, SamplingMessageRole, str]` |
| `content` | `str` |
| `timestamp` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

**Methods**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `SamplingParameters`
`Dataclass`

采样参数

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `temperature` | `float` |
| `max_tokens` | `int` |
| `top_p` | `float` |
| `stop_sequences` | `Optional[List[str]]` |
| `presence_penalty` | `float` |
| `frequency_penalty` | `float` |
| `model` | `Optional[str]` |
| `system_prompt` | `Optional[str]` |
| `reasoning_effort` | `Optional[str]` |
| `metadata` | `Dict[str, Any]` |

**Methods**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `SamplingCreateMessageRequest`
`Dataclass`

采样创建消息请求

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `messages` | `List[SamplingMessage]` |
| `system_prompt` | `Optional[str]` |
| `temperature` | `float` |
| `max_tokens` | `int` |
| `stop_sequences` | `Optional[List[str]]` |
| `include_context` | `Optional[str]` |
| `thinking` | `Optional[Dict[str, Any]]` |

**Methods**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `SamplingResponse`
`Dataclass`

采样响应

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `content` | `str` |
| `model` | `str` |
| `role` | `str` |
| `done` | `bool` |
| `done_reason` | `Optional[str]` |
| `usage` | `Optional[Dict[str, int]]` |
| `thinking` | `Optional[str]` |
| `custom_id` | `Optional[str]` |
| `metadata` | `Dict[str, Any]` |

**Methods**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `SamplingProvider`

采样提供者接口

**Methods**

- `sample()` - 同步采样

---

##### `SamplingManager`

采样管理器

**Methods**

- `register_provider()` - 注册采样提供者
- `set_default_model()` - 设置默认模型
- `add_hook()` - 添加采样钩子
- `remove_hook()` - 移除采样钩子
- `_notify_hooks()` - 通知钩子
- ... (5 more)

---

##### `EmbeddedSamplingProvider`

**Base Classes**: `SamplingProvider`

嵌入式采样提供者

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `model_id` | `str` |

**Methods**

- `sample()` - 执行采样
- `_generate_content()` - 生成内容

---

### `govmcp.protocol.server`

govmcp.protocol.server — GovMCPServer

JSON-RPC 2.0 over stdio 协议层，叠加 govmcp 独有特性：

- SM4 加密传输层（可选，CBC 模式，PKCS7 填充）

- SM3 数据完整性校验（每条消息附带哈希）

- 信创模型注册（48 个国产 LLM）

- 审批工作流集成（预留接口）

- 多传输层支持（Stdio/WebSocket/HTTP/SSE）

兼容标准 MCP 的 initialize / tools/list / tools/call / resources/list / prompts/list 方法。

#### Functions

##### `__init__(name: str, version: str, crypto_enabled: bool = False, sm4_key: Optional[bytes] = None) -> None`

**Location**: Line 189

初始化 GovMCPServer。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `version` | `str` | Yes | `-` |  |
| `crypto_enabled` | `bool` | No | `False` |  |
| `sm4_key` | `Optional[bytes]` | No | `None` |  |

**Returns** `None`

---

##### `register_tool(name: str, description: str, input_schema: Dict[str, Any], handler: Callable[..., Any]) -> None`

**Location**: Line 239

注册一个工具。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `description` | `str` | Yes | `-` |  |
| `input_schema` | `Dict[str, Any]` | Yes | `-` |  |
| `handler` | `Callable[..., Any]` | Yes | `-` |  |

**Returns** `None`

---

##### `register_resource(uri: str, name: str, description: str, mime_type: str, handler: Callable[[str], Any]) -> None`

**Location**: Line 254

注册一个资源。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `uri` | `str` | Yes | `-` |  |
| `name` | `str` | Yes | `-` |  |
| `description` | `str` | Yes | `-` |  |
| `mime_type` | `str` | Yes | `-` |  |
| `handler` | `Callable[[str], Any]` | Yes | `-` |  |

**Returns** `None`

---

##### `register_prompt(name: str, description: str, arguments: List[Dict[str, Any]], handler: Callable[..., Any]) -> None`

**Location**: Line 271

注册一个提示模板。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `description` | `str` | Yes | `-` |  |
| `arguments` | `List[Dict[str, Any]]` | Yes | `-` |  |
| `handler` | `Callable[..., Any]` | Yes | `-` |  |

**Returns** `None`

---

##### `tool(name: str = None, description: str = , input_schema: Dict[str, Any])`

**Location**: Line 286

工具注册装饰器。@server.tool(...)

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | No | `None` |  |
| `description` | `str` | No | `-` |  |
| `input_schema` | `Dict[str, Any]` | No | `-` |  |

---

##### `resource(uri: str = None, name: str = , description: str = , mime_type: str = text/plain)`

**Location**: Line 303

资源注册装饰器。@server.resource(...)

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `uri` | `str` | No | `None` |  |
| `name` | `str` | No | `-` |  |
| `description` | `str` | No | `-` |  |
| `mime_type` | `str` | No | `text/plain` |  |

---

##### `prompt(name: str = None, description: str = , arguments: List[Dict[str, Any]])`

**Location**: Line 320

提示模板注册装饰器。@server.prompt(...)

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | No | `None` |  |
| `description` | `str` | No | `-` |  |
| `arguments` | `List[Dict[str, Any]]` | No | `-` |  |

---

##### `register_model(model_name: str) -> None`

**Location**: Line 336

注册一个额外的信创模型

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_name` | `str` | Yes | `-` |  |

**Returns** `None`

---

##### `set_approval_handler(handler: Callable[[str, Dict[str, Any]], bool]) -> None`

**Location**: Line 341

设置审批处理器。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `Callable[[str, Dict[str, Any]], bool]` | Yes | `-` |  |

**Returns** `None`

---

##### `run() -> None`

**Location**: Line 734

启动 stdio 消息循环。

**Returns** `None`

---

##### `async run_websocket(host: str = '0.0.0.0', port: int = 8080, path: str = '/mcp', auth_token: Optional[str] = None, heartbeat_interval: float = 30.0) -> None`

**Location**: Line 811

启动 WebSocket 服务器。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `host` | `str` | No | `'0.0.0.0'` |  |
| `port` | `int` | No | `8080` |  |
| `path` | `str` | No | `'/mcp'` |  |
| `auth_token` | `Optional[str]` | No | `None` |  |
| `heartbeat_interval` | `float` | No | `30.0` |  |

**Returns** `None`

---

##### `async run_http(host: str = '0.0.0.0', port: int = 8080, path: str = '/mcp', sse_path: str = '/mcp/sse', auth_token: Optional[str] = None, enable_sse: bool = True, sse_heartbeat: float = 15.0) -> None`

**Location**: Line 855

启动 HTTP/SSE 服务器。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `host` | `str` | No | `'0.0.0.0'` |  |
| `port` | `int` | No | `8080` |  |
| `path` | `str` | No | `'/mcp'` |  |
| `sse_path` | `str` | No | `'/mcp/sse'` |  |
| `auth_token` | `Optional[str]` | No | `None` |  |
| `enable_sse` | `bool` | No | `True` |  |
| `sse_heartbeat` | `float` | No | `15.0` |  |

**Returns** `None`

---

##### `get_transport_info() -> Dict[str, Any]`

**Location**: Line 916

获取传输层信息

**Returns** `Dict[str, Any]`

---

##### `decorator(func: Any)`

**Location**: Line 295

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `func` | `Any` | Yes | `-` |  |

---

##### `decorator(func: Any)`

**Location**: Line 313

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `func` | `Any` | Yes | `-` |  |

---

##### `decorator(func: Any)`

**Location**: Line 329

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `func` | `Any` | Yes | `-` |  |

---

##### `async handler(client_id: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]`

**Location**: Line 842

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | Yes | `-` |  |
| `message` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `Optional[Dict[str, Any]]`

---

##### `async handler(request: HTTPRequest) -> HTTPResponse`

**Location**: Line 892

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `HTTPRequest` | Yes | `-` |  |

**Returns** `HTTPResponse`

---

#### Classes

##### `GovMCPServer`

GovMCPServer — 国产信创 MCP 协议服务器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `name` | `str` |
| `version` | `str` |
| `crypto_enabled` | `bool` |
| `sm4_key` | `Optional[bytes]` |

**Methods**

- `register_tool()` - 注册一个工具。
- `register_resource()` - 注册一个资源。
- `register_prompt()` - 注册一个提示模板。
- `tool()` - 工具注册装饰器。@server.tool(...)
- `resource()` - 资源注册装饰器。@server.resource(...)
- ... (32 more)

---

### `govmcp.protocol.tasks`

govmcp.protocol.tasks — 异步任务支持 (MCP 2025.11)

提供异步任务生命周期管理，包括任务创建、状态追踪、结果获取和取消功能。

支持 SSE (Server-Sent Events) 实时推送任务状态变更。

#### Functions

##### `create_sse_response(task_manager: TaskManager, task_ids: Optional[List[str]] = None, all_tasks: bool = False) -> Dict[str, Any]`

**Location**: Line 616

创建 SSE 响应

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_manager` | `TaskManager` | Yes | `-` |  |
| `task_ids` | `Optional[List[str]]` | No | `None` |  |
| `all_tasks` | `bool` | No | `False` |  |

**Returns** `Dict[str, Any]`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 61

转换为字典格式

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'TaskInfo'`

**Location**: Line 85

**装饰器**: classmethod

从字典创建

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `'TaskInfo'`

---

##### `__init__(task_ids: Optional[Set[str]] = None)`

**Location**: Line 109

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_ids` | `Optional[Set[str]]` | No | `None` |  |

---

##### `async send(event: Dict[str, Any]) -> None`

**Location**: Line 114

发送事件到订阅者

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `event` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `None`

---

##### `close() -> None`

**Location**: Line 120

关闭订阅

**Returns** `None`

---

##### `async events() -> AsyncIterator[Dict[str, Any]]`

**Location**: Line 130

异步事件迭代器

**Returns** `AsyncIterator[Dict[str, Any]]`

---

##### `__init__(default_timeout: float = 300.0)`

**Location**: Line 151

初始化任务管理器

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `default_timeout` | `float` | No | `300.0` |  |

---

##### `register_tool(name: str, handler: Callable[..., Any]) -> None`

**Location**: Line 166

注册工具处理器

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `handler` | `Callable[..., Any]` | Yes | `-` |  |

**Returns** `None`

---

##### `set_executor(loop: asyncio.AbstractEventLoop) -> None`

**Location**: Line 170

设置事件循环

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `loop` | `asyncio.AbstractEventLoop` | Yes | `-` |  |

**Returns** `None`

---

##### `create_task(tool_name: str, arguments: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> str`

**Location**: Line 178

创建异步任务

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `tool_name` | `str` | Yes | `-` |  |
| `arguments` | `Optional[Dict[str, Any]]` | No | `None` |  |
| `timeout` | `Optional[float]` | No | `None` |  |
| `metadata` | `Optional[Dict[str, Any]]` | No | `None` |  |

**Returns** `str`

---

##### `execute_task_sync(tool_name: str, arguments: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> str`

**Location**: Line 276

同步执行任务（创建后立即执行）

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `tool_name` | `str` | Yes | `-` |  |
| `arguments` | `Optional[Dict[str, Any]]` | No | `None` |  |
| `timeout` | `Optional[float]` | No | `None` |  |

**Returns** `str`

---

##### `get_task_status(task_id: str) -> TaskStatus`

**Location**: Line 331

获取任务状态

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `str` | Yes | `-` |  |

**Returns** `TaskStatus`

---

##### `get_task_info(task_id: str) -> TaskInfo`

**Location**: Line 350

获取完整任务信息

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `str` | Yes | `-` |  |

**Returns** `TaskInfo`

---

##### `get_task_result(task_id: str) -> Any`

**Location**: Line 369

获取任务结果

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `str` | Yes | `-` |  |

**Returns** `Any`

---

##### `cancel_task(task_id: str) -> bool`

**Location**: Line 396

取消任务

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `str` | Yes | `-` |  |

**Returns** `bool`

---

##### `list_tasks(status: Optional[TaskStatus] = None, limit: int = 100, offset: int = 0) -> List[TaskInfo]`

**Location**: Line 424

列出任务

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `status` | `Optional[TaskStatus]` | No | `None` |  |
| `limit` | `int` | No | `100` |  |
| `offset` | `int` | No | `0` |  |

**Returns** `List[TaskInfo]`

---

##### `cleanup_completed_tasks(max_age: float = 3600.0) -> int`

**Location**: Line 451

清理已完成任务

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `max_age` | `float` | No | `3600.0` |  |

**Returns** `int`

---

##### `subscribe(task_id: Optional[str] = None, task_ids: Optional[Set[str]] = None) -> TaskSubscriber`

**Location**: Line 482

订阅任务更新

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `Optional[str]` | No | `None` |  |
| `task_ids` | `Optional[Set[str]]` | No | `None` |  |

**Returns** `TaskSubscriber`

---

##### `unsubscribe(subscriber: TaskSubscriber) -> None`

**Location**: Line 512

取消订阅

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `subscriber` | `TaskSubscriber` | Yes | `-` |  |

**Returns** `None`

---

##### `update_progress(task_id: str, progress: float) -> bool`

**Location**: Line 547

更新任务进度

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `str` | Yes | `-` |  |
| `progress` | `float` | Yes | `-` |  |

**Returns** `bool`

---

##### `get_task_stats() -> Dict[str, Any]`

**Location**: Line 567

获取任务统计信息

**Returns** `Dict[str, Any]`

---

##### `__init__(task_manager: TaskManager)`

**Location**: Line 589

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_manager` | `TaskManager` | Yes | `-` |  |

---

##### `async stream_events(task_ids: Optional[List[str]] = None, all_tasks: bool = False) -> AsyncIterator[str]`

**Location**: Line 592

生成 SSE 事件流

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_ids` | `Optional[List[str]]` | No | `None` |  |
| `all_tasks` | `bool` | No | `False` |  |

**Returns** `AsyncIterator[str]`

---

#### Classes

##### `TaskStatus`
`Enum`

**Base Classes**: `str | Enum`

任务状态枚举

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `PENDING` | `'pending'` |
| `WORKING` | `'working'` |
| `COMPLETED` | `'completed'` |
| `FAILED` | `'failed'` |
| `CANCELED` | `'canceled'` |

---

##### `TaskNotFoundError`

**Base Classes**: `Exception`

任务不存在异常

---

##### `TaskCancelError`

**Base Classes**: `Exception`

任务取消失败异常

---

##### `TaskInfo`
`Dataclass`

任务信息数据类

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `id` | `str` |
| `status` | `TaskStatus` |
| `tool_name` | `str` |
| `arguments` | `Dict[str, Any]` |
| `progress` | `float` |
| `result` | `Optional[Any]` |
| `error` | `Optional[str]` |
| `created_at` | `float` |
| `started_at` | `Optional[float]` |
| `completed_at` | `Optional[float]` |
| `timeout` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

**Methods**

- `to_dict()` - 转换为字典格式
- `from_dict()` - 从字典创建

---

##### `TaskSubscriber`

任务订阅者（用于 SSE）

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `task_ids` | `Optional[Set[str]]` |

**Methods**

- `close()` - 关闭订阅

---

##### `TaskManager`

异步任务管理器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `default_timeout` | `float` |

**Methods**

- `register_tool()` - 注册工具处理器
- `set_executor()` - 设置事件循环
- `_generate_task_id()` - 生成唯一任务ID
- `create_task()` - 创建异步任务
- `execute_task_sync()` - 同步执行任务（创建后立即执行）
- ... (11 more)

---

##### `SSEHandler`

SSE 事件处理器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `task_manager` | `TaskManager` |

---

### `govmcp.protocol.websocket_server`

govmcp.protocol.websocket_server — WebSocket 传输层服务器

基于 websockets 库实现 MCP WebSocket 服务器，支持:

- 标准 MCP JSON-RPC 消息格式

- SM4-CBC 加密传输（可选）

- SM3 消息完整性校验

- Token 认证

- 多客户端连接管理

- 心跳检测

#### Functions

##### `__init__(host: str = '0.0.0.0', port: int = 8080, path: str = '/mcp', auth_token: Optional[str] = None, crypto_enabled: bool = False, sm4_key: Optional[bytes] = None, heartbeat_interval: float = 30.0, heartbeat_timeout: float = 60.0, max_message_size: int = 10 * 1024 * 1024, enable_cors: bool = False, cors_origins: Optional[List[str]] = None, log_level: int = logging.INFO) -> None`

**Location**: Line 92

初始化 WebSocket 服务器。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `host` | `str` | No | `'0.0.0.0'` |  |
| `port` | `int` | No | `8080` |  |
| `path` | `str` | No | `'/mcp'` |  |
| `auth_token` | `Optional[str]` | No | `None` |  |
| `crypto_enabled` | `bool` | No | `False` |  |
| `sm4_key` | `Optional[bytes]` | No | `None` |  |
| `heartbeat_interval` | `float` | No | `30.0` |  |
| `heartbeat_timeout` | `float` | No | `60.0` |  |
| `max_message_size` | `int` | No | `10 * 1024 * 1024` |  |
| `enable_cors` | `bool` | No | `False` |  |
| `cors_origins` | `Optional[List[str]]` | No | `None` |  |
| `log_level` | `int` | No | `logging.INFO` |  |

**Returns** `None`

---

##### `set_message_handler(handler: Callable[[str, Dict[str, Any]], Any]) -> None`

**Location**: Line 149

设置消息处理器。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `Callable[[str, Dict[str, Any]], Any]` | Yes | `-` |  |

**Returns** `None`

---

##### `async start(handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None) -> None`

**Location**: Line 158

启动 WebSocket 服务器。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `Optional[Callable[[str, Dict[str, Any]], Any]]` | No | `None` |  |

**Returns** `None`

---

##### `async stop() -> None`

**Location**: Line 186

停止 WebSocket 服务器

**Returns** `None`

---

##### `async broadcast(message: Dict[str, Any]) -> int`

**Location**: Line 211

广播消息给所有已连接的客户端。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `int`

---

##### `get_client_count() -> int`

**Location**: Line 232

获取当前连接数

**Returns** `int`

---

##### `get_authenticated_count() -> int`

**Location**: Line 236

获取已认证连接数

**Returns** `int`

---

##### `async disconnect_client(client_id: str) -> bool`

**Location**: Line 240

断开指定客户端。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | Yes | `-` |  |

**Returns** `bool`

---

##### `async handle_message(client_id: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]`

**Location**: Line 501

默认消息处理器（需要外部设置实际的处理器）。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | Yes | `-` |  |
| `message` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `Optional[Dict[str, Any]]`

---

##### `create_stdio_compatible(name: str, version: str, handler: Callable[[str, Dict[str, Any]], Any], crypto_enabled: bool = False) -> WebSocketServer`

**Location**: Line 516

**装饰器**: staticmethod

创建与 stdio 服务器兼容的 WebSocket 服务器

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `version` | `str` | Yes | `-` |  |
| `handler` | `Callable[[str, Dict[str, Any]], Any]` | Yes | `-` |  |
| `crypto_enabled` | `bool` | No | `False` |  |

**Returns** `WebSocketServer`

---

##### `create_secure(name: str, version: str, handler: Callable[[str, Dict[str, Any]], Any], auth_token: str) -> WebSocketServer`

**Location**: Line 532

**装饰器**: staticmethod

创建带认证的 WebSocket 服务器

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `version` | `str` | Yes | `-` |  |
| `handler` | `Callable[[str, Dict[str, Any]], Any]` | Yes | `-` |  |
| `auth_token` | `str` | Yes | `-` |  |

**Returns** `WebSocketServer`

---

#### Classes

##### `ConnectionState`
`Enum`

**Base Classes**: `Enum`

连接状态

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `CONNECTING` | `'connecting'` |
| `AUTHENTICATING` | `'authenticating'` |
| `AUTHENTICATED` | `'authenticated'` |
| `CLOSED` | `'closed'` |

---

##### `ClientConnection`
`Dataclass`

客户端连接信息

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `client_id` | `str` |
| `websocket` | `Any` |
| `state` | `ConnectionState` |
| `auth_token` | `Optional[str]` |
| `authenticated_at` | `Optional[datetime]` |
| `last_heartbeat` | `datetime` |
| `message_count` | `int` |
| `remote_addr` | `Optional[str]` |
| `headers` | `Dict[str, str]` |

---

##### `WebSocketServer`

WebSocket MCP 服务器

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `host` | `str` |
| `port` | `int` |
| `path` | `str` |
| `auth_token` | `Optional[str]` |
| `crypto_enabled` | `bool` |
| `sm4_key` | `Optional[bytes]` |
| `heartbeat_interval` | `float` |
| `heartbeat_timeout` | `float` |
| `max_message_size` | `int` |
| `enable_cors` | `bool` |
| `cors_origins` | `Optional[List[str]]` |
| `log_level` | `int` |

**Methods**

- `set_message_handler()` - 设置消息处理器。
- `get_client_count()` - 获取当前连接数
- `get_authenticated_count()` - 获取已认证连接数
- `_validate_sm3()` - 验证 SM3 完整性

---

##### `WebSocketServerFactory`

WebSocket 服务器工厂

**Methods**

- `create_stdio_compatible()` - 创建与 stdio 服务器兼容的 WebSocket 服务器
- `create_secure()` - 创建带认证的 WebSocket 服务器

---

---

## Server Module

**模块路径**: `govmcp.server`

### `govmcp.server.approval`

审批工作流模块 — 多级审批链、超时自动拒绝、审计记录关联。

设计原则:

- 多级审批链：按 approvers 顺序逐级审批

- 超时控制：全局超时，到期后根据 auto_approve_on_timeout 决定行为

- 审计关联：可关联 AuditChain 实例，审批动作自动写入审计记录

- 不可逆：approve/reject/skip 均为单向操作，已完成的步骤不可回退

#### Functions

##### `create_single_approval(approver: str, timeout: float = 300) -> ApprovalFlow`

**Location**: Line 361

创建单级审批流。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approver` | `str` | Yes | `-` |  |
| `timeout` | `float` | No | `300` |  |

**Returns** `ApprovalFlow`

---

##### `create_multi_approval(approvers: List[str], timeout: float = 300) -> ApprovalFlow`

**Location**: Line 375

创建多级审批流。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approvers` | `List[str]` | Yes | `-` |  |
| `timeout` | `float` | No | `300` |  |

**Returns** `ApprovalFlow`

---

##### `to_dict() -> dict`

**Location**: Line 37

序列化为字典

**Returns** `dict`

---

##### `__init__(approvers: List[str], timeout: float = 300, auto_approve_on_timeout: bool = False, audit_chain: Any = None)`

**Location**: Line 74

初始化审批流。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approvers` | `List[str]` | Yes | `-` |  |
| `timeout` | `float` | No | `300` |  |
| `auto_approve_on_timeout` | `bool` | No | `False` |  |
| `audit_chain` | `Any` | No | `None` |  |

---

##### `approve(approver: str, comment: str = '') -> ApprovalStatus`

**Location**: Line 188

当前级别审批通过。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approver` | `str` | Yes | `-` |  |
| `comment` | `str` | No | `''` |  |

**Returns** `ApprovalStatus`

---

##### `reject(approver: str, comment: str = '') -> ApprovalStatus`

**Location**: Line 224

当前级别审批拒绝。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approver` | `str` | Yes | `-` |  |
| `comment` | `str` | No | `''` |  |

**Returns** `ApprovalStatus`

---

##### `skip(comment: str = '') -> ApprovalStatus`

**Location**: Line 257

跳过当前审批级别。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `comment` | `str` | No | `''` |  |

**Returns** `ApprovalStatus`

---

##### `is_complete() -> bool`

**Location**: Line 290

审批流程是否已完成（无论通过与否）。

**Returns** `bool`

---

##### `is_approved() -> bool`

**Location**: Line 303

审批是否全部通过。

**Returns** `bool`

---

##### `result() -> ApprovalStatus`

**Location**: Line 316

获取审批流程的最终状态。

**Returns** `ApprovalStatus`

---

##### `to_dict_list() -> List[dict]`

**Location**: Line 340

将所有审批步骤序列化为字典列表。

**Returns** `List[dict]`

---

#### Classes

##### `ApprovalStatus`
`Enum`

**Base Classes**: `Enum`

审批状态枚举

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `PENDING` | `'pending'` |
| `APPROVED` | `'approved'` |
| `REJECTED` | `'rejected'` |
| `TIMEOUT` | `'timeout'` |
| `SKIPPED` | `'skipped'` |

---

##### `ApprovalStep`
`Dataclass`

单个审批步骤的数据记录

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `level` | `int` |
| `approver` | `str` |
| `status` | `ApprovalStatus` |
| `timestamp` | `float` |
| `comment` | `str` |

**Methods**

- `to_dict()` - 序列化为字典

---

##### `ApprovalFlow`

多级审批工作流。

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `approvers` | `List[str]` |
| `timeout` | `float` |
| `auto_approve_on_timeout` | `bool` |
| `audit_chain` | `Any` |

**Methods**

- `_elapsed()` - 已流逝时间（秒）
- `_is_timed_out()` - 检查是否已超时
- `_current_step()` - 获取当前待审批的步骤，若已完成则返回 None
- `_handle_timeout()` - 处理超时情况。
- `_finalize_step()` - 完成当前步骤：推进 current_level，检查是否全部完成。
- ... (8 more)

---

---

## Tools Module

**模块路径**: `govmcp.tools`

### `govmcp.tools.government.approval_workflow`

govmcp.tools.government.approval_workflow — 审批工作流工具模块

提供审批流程发起、进度查询、意见提交、加签改签、会签委托等审批工作流服务的工具函数。

#### Functions

##### `initiate_approval_workflow(workflow_name: str, applicant_name: str, applicant_department: str, workflow_type: str, business_data: Dict[str, Any]) -> Dict[str, Any]`

**Location**: Line 17

**装饰器**: govmcp_tool(name='initiate_approval_workflow', description='发起审批流程')

发起审批工作流。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_name` | `str` | Yes | `-` |  |
| `applicant_name` | `str` | Yes | `-` |  |
| `applicant_department` | `str` | Yes | `-` |  |
| `workflow_type` | `str` | Yes | `-` |  |
| `business_data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_approval_progress(workflow_id: str) -> Dict[str, Any]`

**Location**: Line 58

**装饰器**: govmcp_tool(name='query_approval_progress', description='查询审批进度')

查询审批流程进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `submit_approval_comment(workflow_id: str, approver_name: str, action: str, comment: str) -> Dict[str, Any]`

**Location**: Line 104

**装饰器**: govmcp_tool(name='submit_approval_comment', description='提交审批意见')

提交审批意见。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | Yes | `-` |  |
| `approver_name` | `str` | Yes | `-` |  |
| `action` | `str` | Yes | `-` |  |
| `comment` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `handle_approval_counter_sign(workflow_id: str, current_approver: str, counter_signer: str, reason: str) -> Dict[str, Any]`

**Location**: Line 140

**装饰器**: govmcp_tool(name='handle_approval_counter_sign', description='审批加签处理')

审批加签处理（增加临时审批节点）。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | Yes | `-` |  |
| `current_approver` | `str` | Yes | `-` |  |
| `counter_signer` | `str` | Yes | `-` |  |
| `reason` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `handle_approval_transfer(workflow_id: str, original_approver: str, new_approver: str, reason: str) -> Dict[str, Any]`

**Location**: Line 178

**装饰器**: govmcp_tool(name='handle_approval_transfer', description='审批改签处理')

审批改签处理（更换审批人）。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | Yes | `-` |  |
| `original_approver` | `str` | Yes | `-` |  |
| `new_approver` | `str` | Yes | `-` |  |
| `reason` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `handle_approval_joint_sign(workflow_id: str, approvers: List[str], deadline: str) -> Dict[str, Any]`

**Location**: Line 216

**装饰器**: govmcp_tool(name='handle_approval_joint_sign', description='审批会签处理')

审批会签处理（多人同时审批）。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | Yes | `-` |  |
| `approvers` | `List[str]` | Yes | `-` |  |
| `deadline` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `handle_approval_suspend_resume(workflow_id: str, action: str, reason: Optional[str] = None) -> Dict[str, Any]`

**Location**: Line 251

**装饰器**: govmcp_tool(name='handle_approval_suspend_resume', description='审批挂起恢复')

审批流程挂起或恢复。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | Yes | `-` |  |
| `action` | `str` | Yes | `-` |  |
| `reason` | `Optional[str]` | No | `None` |  |

**Returns** `Dict[str, Any]`

---

##### `handle_approval_delegation(delegator: str, delegatee: str, start_date: str, end_date: str, workflow_types: List[str]) -> Dict[str, Any]`

**Location**: Line 285

**装饰器**: govmcp_tool(name='handle_approval_delegation', description='审批委托代理')

设置审批委托代理。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `delegator` | `str` | Yes | `-` |  |
| `delegatee` | `str` | Yes | `-` |  |
| `start_date` | `str` | Yes | `-` |  |
| `end_date` | `str` | Yes | `-` |  |
| `workflow_types` | `List[str]` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_approval_warning(approver_name: str) -> Dict[str, Any]`

**Location**: Line 324

**装饰器**: govmcp_tool(name='query_approval_warning', description='查询审批时限预警')

查询审批时限预警信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approver_name` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_approval_statistics(department: str, start_date: str, end_date: str) -> Dict[str, Any]`

**Location**: Line 368

**装饰器**: govmcp_tool(name='query_approval_statistics', description='查询审批统计分析')

查询审批流程统计分析。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `department` | `str` | Yes | `-` |  |
| `start_date` | `str` | Yes | `-` |  |
| `end_date` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `manage_approval_archive(workflow_id: str, action: str) -> Dict[str, Any]`

**Location**: Line 410

**装饰器**: govmcp_tool(name='manage_approval_archive', description='审批归档管理')

审批流程归档管理。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | Yes | `-` |  |
| `action` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `configure_approval_permission(role_name: str, workflow_types: List[str], approval_limits: Dict[str, float]) -> Dict[str, Any]`

**Location**: Line 442

**装饰器**: govmcp_tool(name='configure_approval_permission', description='配置审批权限')

配置审批权限。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `role_name` | `str` | Yes | `-` |  |
| `workflow_types` | `List[str]` | Yes | `-` |  |
| `approval_limits` | `Dict[str, float]` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `manage_approval_template(template_name: str, workflow_type: str, stages: List[Dict[str, Any]], action: str) -> Dict[str, Any]`

**Location**: Line 476

**装饰器**: govmcp_tool(name='manage_approval_template', description='审批模板管理')

审批模板管理。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `template_name` | `str` | Yes | `-` |  |
| `workflow_type` | `str` | Yes | `-` |  |
| `stages` | `List[Dict[str, Any]]` | Yes | `-` |  |
| `action` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_approval_digital_signature(workflow_id: str, approver_name: str, signature_type: str) -> Dict[str, Any]`

**Location**: Line 512

**装饰器**: govmcp_tool(name='apply_approval_digital_signature', description='审批电子签章')

审批电子签章应用。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | Yes | `-` |  |
| `approver_name` | `str` | Yes | `-` |  |
| `signature_type` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `generate_approval_document(workflow_id: str, document_type: str, include_attachments: bool = True) -> Dict[str, Any]`

**Location**: Line 550

**装饰器**: govmcp_tool(name='generate_approval_document', description='生成审批文书')

生成审批文书。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | Yes | `-` |  |
| `document_type` | `str` | Yes | `-` |  |
| `include_attachments` | `bool` | No | `True` |  |

**Returns** `Dict[str, Any]`

---

### `govmcp.tools.government.carbon_emission`

govmcp.tools.government.carbon_emission — 碳排放管理工具模块

提供企业碳排放数据录入、碳交易、碳足迹计算、碳中和追踪等碳排放管理服务的工具函数。

#### Functions

##### `input_carbon_emission_data(company_name: str, credit_code: str, reporting_year: int, reporting_quarter: int, coal_consumption: float, oil_consumption: float, natural_gas_consumption: float, electricity_consumption: float) -> Dict[str, Any]`

**Location**: Line 17

**装饰器**: govmcp_tool(name='input_carbon_emission_data', description='录入企业碳排放数据')

录入企业碳排放活动数据。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `credit_code` | `str` | Yes | `-` |  |
| `reporting_year` | `int` | Yes | `-` |  |
| `reporting_quarter` | `int` | Yes | `-` |  |
| `coal_consumption` | `float` | Yes | `-` |  |
| `oil_consumption` | `float` | Yes | `-` |  |
| `natural_gas_consumption` | `float` | Yes | `-` |  |
| `electricity_consumption` | `float` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_carbon_quota(company_name: str, credit_code: str, year: int) -> Dict[str, Any]`

**Location**: Line 72

**装饰器**: govmcp_tool(name='query_carbon_quota', description='查询碳排放配额')

查询企业碳排放配额分配情况。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `credit_code` | `str` | Yes | `-` |  |
| `year` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `trade_carbon_emission_allowance(company_name: str, trade_type: str, quantity: float, price: float) -> Dict[str, Any]`

**Location**: Line 108

**装饰器**: govmcp_tool(name='trade_carbon_emission_allowance', description='碳排放权交易')

碳排放权交易（买入/卖出配额）。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `trade_type` | `str` | Yes | `-` |  |
| `quantity` | `float` | Yes | `-` |  |
| `price` | `float` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `generate_carbon_emission_report(company_name: str, credit_code: str, year: int, report_type: str) -> Dict[str, Any]`

**Location**: Line 145

**装饰器**: govmcp_tool(name='generate_carbon_emission_report', description='生成碳排放报告')

生成企业碳排放报告。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `credit_code` | `str` | Yes | `-` |  |
| `year` | `int` | Yes | `-` |  |
| `report_type` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `calculate_carbon_footprint(product_name: str, raw_materials: Dict[str, float], manufacturing_energy: float, transportation_distance: float, packaging_weight: float) -> Dict[str, Any]`

**Location**: Line 184

**装饰器**: govmcp_tool(name='calculate_carbon_footprint', description='计算碳足迹')

计算产品碳足迹。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `product_name` | `str` | Yes | `-` |  |
| `raw_materials` | `Dict[str, float]` | Yes | `-` |  |
| `manufacturing_energy` | `float` | Yes | `-` |  |
| `transportation_distance` | `float` | Yes | `-` |  |
| `packaging_weight` | `float` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `set_emission_reduction_target(company_name: str, base_year: int, base_emission: float, target_year: int, target_reduction_ratio: float) -> Dict[str, Any]`

**Location**: Line 233

**装饰器**: govmcp_tool(name='set_emission_reduction_target', description='设定减排目标')

设定企业碳减排目标。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `base_year` | `int` | Yes | `-` |  |
| `base_emission` | `float` | Yes | `-` |  |
| `target_year` | `int` | Yes | `-` |  |
| `target_reduction_ratio` | `float` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_carbon_verification(company_name: str, credit_code: str, reporting_year: int, verification_body: str) -> Dict[str, Any]`

**Location**: Line 275

**装饰器**: govmcp_tool(name='apply_carbon_verification', description='申请碳核查')

申请碳排放核查。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `credit_code` | `str` | Yes | `-` |  |
| `reporting_year` | `int` | Yes | `-` |  |
| `verification_body` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `register_ccer_project(company_name: str, project_type: str, project_capacity: float, start_date: str, location: str) -> Dict[str, Any]`

**Location**: Line 311

**装饰器**: govmcp_tool(name='register_ccer_project', description='CCER项目登记')

登记CCER（中国核证自愿减排量）项目。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `project_type` | `str` | Yes | `-` |  |
| `project_capacity` | `float` | Yes | `-` |  |
| `start_date` | `str` | Yes | `-` |  |
| `location` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_carbon_asset_account(company_name: str, credit_code: str) -> Dict[str, Any]`

**Location**: Line 350

**装饰器**: govmcp_tool(name='query_carbon_asset_account', description='查询碳资产账户')

查询企业碳资产账户信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `credit_code` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_carbon_monitoring_data(company_name: str, monitor_point: str, start_date: str, end_date: str) -> Dict[str, Any]`

**Location**: Line 383

**装饰器**: govmcp_tool(name='query_carbon_monitoring_data', description='查询碳排放监测数据')

查询碳排放连续监测数据。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `monitor_point` | `str` | Yes | `-` |  |
| `start_date` | `str` | Yes | `-` |  |
| `end_date` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `analyze_industrial_carbon_emission(industry: str, region: str, year: int) -> Dict[str, Any]`

**Location**: Line 424

**装饰器**: govmcp_tool(name='analyze_industrial_carbon_emission', description='工业碳排放分析')

工业行业碳排放分析。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `industry` | `str` | Yes | `-` |  |
| `region` | `str` | Yes | `-` |  |
| `year` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_energy_consumption(company_name: str, year: int, month: int) -> Dict[str, Any]`

**Location**: Line 463

**装饰器**: govmcp_tool(name='query_energy_consumption', description='查询能源消耗统计')

查询企业能源消耗统计数据。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `year` | `int` | Yes | `-` |  |
| `month` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_green_electricity_trade(company_name: str, year: int) -> Dict[str, Any]`

**Location**: Line 503

**装饰器**: govmcp_tool(name='query_green_electricity_trade', description='查询绿电交易')

查询绿色电力交易信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `year` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `track_carbon_neutrality_progress(company_name: str, target_year: int) -> Dict[str, Any]`

**Location**: Line 547

**装饰器**: govmcp_tool(name='track_carbon_neutrality_progress', description='追踪碳中和进度')

追踪企业碳中和实施进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `target_year` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `predict_carbon_emission(company_name: str, historical_data: List[Dict[str, Any]], forecast_years: int) -> Dict[str, Any]`

**Location**: Line 583

**装饰器**: govmcp_tool(name='predict_carbon_emission', description='碳排放预测分析')

碳排放预测分析。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `historical_data` | `List[Dict[str, Any]]` | Yes | `-` |  |
| `forecast_years` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

### `govmcp.tools.government.citizen_service`

govmcp.tools.government.citizen_service — 市民服务工具模块

提供身份证、户籍、社保、医保、公积金、交通、不动产等市民常用政务服务的工具函数。

#### Functions

##### `query_id_card_progress(name: str, id_number: str, phone: str) -> Dict[str, Any]`

**Location**: Line 17

**装饰器**: govmcp_tool(name='query_id_card_progress', description='查询身份证办理进度')

查询身份证办理进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |
| `phone` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_household_registration(id_number: str, name: str) -> Dict[str, Any]`

**Location**: Line 49

**装饰器**: govmcp_tool(name='query_household_registration', description='查询户籍信息')

查询户籍基本信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | Yes | `-` |  |
| `name` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_social_security_account(id_number: str, name: str) -> Dict[str, Any]`

**Location**: Line 79

**装饰器**: govmcp_tool(name='query_social_security_account', description='查询社保账户信息')

查询社保账户余额和基本信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | Yes | `-` |  |
| `name` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_social_security_payment(id_number: str, year: int, month: int) -> Dict[str, Any]`

**Location**: Line 111

**装饰器**: govmcp_tool(name='query_social_security_payment', description='查询社保缴费记录')

查询社保缴费明细记录。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | Yes | `-` |  |
| `year` | `int` | Yes | `-` |  |
| `month` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_medical_insurance_account(id_number: str, name: str) -> Dict[str, Any]`

**Location**: Line 146

**装饰器**: govmcp_tool(name='query_medical_insurance_account', description='查询医保账户')

查询医保个人账户余额和消费记录。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | Yes | `-` |  |
| `name` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_medical_settlement(id_number: str, start_date: str, end_date: str) -> Dict[str, Any]`

**Location**: Line 178

**装饰器**: govmcp_tool(name='query_medical_settlement', description='查询医保结算记录')

查询医保结算明细。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | Yes | `-` |  |
| `start_date` | `str` | Yes | `-` |  |
| `end_date` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_housing_fund_account(id_number: str, name: str) -> Dict[str, Any]`

**Location**: Line 226

**装饰器**: govmcp_tool(name='query_housing_fund_account', description='查询公积金账户')

查询公积金账户余额。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | Yes | `-` |  |
| `name` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_housing_fund_withdrawal(id_number: str, name: str, withdrawal_type: str, amount: float, bank_name: str, bank_account: str) -> Dict[str, Any]`

**Location**: Line 259

**装饰器**: govmcp_tool(name='apply_housing_fund_withdrawal', description='申请公积金提取')

申请公积金提取。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | Yes | `-` |  |
| `name` | `str` | Yes | `-` |  |
| `withdrawal_type` | `str` | Yes | `-` |  |
| `amount` | `float` | Yes | `-` |  |
| `bank_name` | `str` | Yes | `-` |  |
| `bank_account` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_housing_fund_loan(id_number: str, loan_app_no: str) -> Dict[str, Any]`

**Location**: Line 299

**装饰器**: govmcp_tool(name='query_housing_fund_loan', description='查询公积金贷款进度')

查询公积金贷款申请进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | Yes | `-` |  |
| `loan_app_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_residence_permit(name: str, id_number: str, phone: str) -> Dict[str, Any]`

**Location**: Line 331

**装饰器**: govmcp_tool(name='query_residence_permit', description='查询居住证办理进度')

查询居住证办理进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |
| `phone` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_driver_license(name: str, license_no: str) -> Dict[str, Any]`

**Location**: Line 364

**装饰器**: govmcp_tool(name='query_driver_license', description='查询驾驶证信息')

查询驾驶证信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `license_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_vehicle_info(plate_number: str, id_number: str) -> Dict[str, Any]`

**Location**: Line 397

**装饰器**: govmcp_tool(name='query_vehicle_info', description='查询车辆信息')

查询车辆登记信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `plate_number` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_traffic_violation(plate_number: str, id_number: str) -> Dict[str, Any]`

**Location**: Line 431

**装饰器**: govmcp_tool(name='query_traffic_violation', description='查询交通违章记录')

查询车辆交通违章记录。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `plate_number` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_property_registration(id_number: str, property_address: str) -> Dict[str, Any]`

**Location**: Line 471

**装饰器**: govmcp_tool(name='query_property_registration', description='查询不动产登记信息')

查询不动产登记信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | Yes | `-` |  |
| `property_address` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_utility_bill(account_no: str, bill_type: str) -> Dict[str, Any]`

**Location**: Line 504

**装饰器**: govmcp_tool(name='query_utility_bill', description='查询水电气缴费记录')

查询水电气等公用事业缴费情况。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `account_no` | `str` | Yes | `-` |  |
| `bill_type` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_low_income_assistance(name: str, id_number: str, address: str, income: float, family_size: int) -> Dict[str, Any]`

**Location**: Line 536

**装饰器**: govmcp_tool(name='apply_low_income_assistance', description='申请低保救助')

申请最低生活保障救助。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |
| `address` | `str` | Yes | `-` |  |
| `income` | `float` | Yes | `-` |  |
| `family_size` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_disability_subsidy(name: str, id_number: str, disability_level: str, disability_cert_no: str) -> Dict[str, Any]`

**Location**: Line 572

**装饰器**: govmcp_tool(name='apply_disability_subsidy', description='申请残疾人补贴')

申请残疾人补贴。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |
| `disability_level` | `str` | Yes | `-` |  |
| `disability_cert_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_elderly_benefit_card(name: str, id_number: str, birth_date: str) -> Dict[str, Any]`

**Location**: Line 608

**装饰器**: govmcp_tool(name='apply_elderly_benefit_card', description='申请老年人优待证')

申请老年人优待证。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |
| `birth_date` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `book_marriage_registration(name1: str, id_number1: str, name2: str, id_number2: str, book_date: str, location: str) -> Dict[str, Any]`

**Location**: Line 642

**装饰器**: govmcp_tool(name='book_marriage_registration', description='预约婚姻登记')

预约婚姻登记。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name1` | `str` | Yes | `-` |  |
| `id_number1` | `str` | Yes | `-` |  |
| `name2` | `str` | Yes | `-` |  |
| `id_number2` | `str` | Yes | `-` |  |
| `book_date` | `str` | Yes | `-` |  |
| `location` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `register_fertility_service(name: str, id_number: str, spouse_name: str, spouse_id_number: str, expected_date: str) -> Dict[str, Any]`

**Location**: Line 683

**装饰器**: govmcp_tool(name='register_fertility_service', description='生育服务登记')

生育服务登记（准生证办理）。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |
| `spouse_name` | `str` | Yes | `-` |  |
| `spouse_id_number` | `str` | Yes | `-` |  |
| `expected_date` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

### `govmcp.tools.government.enterprise_service`

govmcp.tools.government.enterprise_service — 企业服务工具模块

提供工商登记、税务、许可证、知识产权、政府采购等企业常用政务服务的工具函数。

#### Functions

##### `query_business_registration(company_name: str, unified_social_credit_code: str) -> Dict[str, Any]`

**Location**: Line 17

**装饰器**: govmcp_tool(name='query_business_registration', description='查询企业工商登记信息')

查询企业工商登记注册信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `unified_social_credit_code` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_business_license(company_name: str, company_type: str, registered_capital: float, business_scope: str, address: str, legal_person: str, id_number: str) -> Dict[str, Any]`

**Location**: Line 51

**装饰器**: govmcp_tool(name='apply_business_license', description='办理营业执照')

申请办理营业执照。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `company_type` | `str` | Yes | `-` |  |
| `registered_capital` | `float` | Yes | `-` |  |
| `business_scope` | `str` | Yes | `-` |  |
| `address` | `str` | Yes | `-` |  |
| `legal_person` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_tax_registration(company_name: str, tax_id: str) -> Dict[str, Any]`

**Location**: Line 91

**装饰器**: govmcp_tool(name='query_tax_registration', description='查询税务登记信息')

查询企业税务登记信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `tax_id` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_invoice(company_name: str, tax_id: str, invoice_type: str, quantity: int) -> Dict[str, Any]`

**Location**: Line 123

**装饰器**: govmcp_tool(name='apply_invoice', description='申领发票')

申领增值税发票。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `tax_id` | `str` | Yes | `-` |  |
| `invoice_type` | `str` | Yes | `-` |  |
| `quantity` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_social_security_account(company_name: str, credit_code: str, legal_person: str, employee_count: int, address: str) -> Dict[str, Any]`

**Location**: Line 159

**装饰器**: govmcp_tool(name='apply_social_security_account', description='办理社保开户')

办理企业社会保险开户。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `credit_code` | `str` | Yes | `-` |  |
| `legal_person` | `str` | Yes | `-` |  |
| `employee_count` | `int` | Yes | `-` |  |
| `address` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_housing_fund_account_enterprise(company_name: str, credit_code: str, employee_count: int, monthly_deposit_base: float) -> Dict[str, Any]`

**Location**: Line 196

**装饰器**: govmcp_tool(name='apply_housing_fund_account_enterprise', description='办理公积金开户')

办理企业住房公积金开户。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `credit_code` | `str` | Yes | `-` |  |
| `employee_count` | `int` | Yes | `-` |  |
| `monthly_deposit_base` | `float` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_environmental_impact_approval(project_name: str, approval_no: str) -> Dict[str, Any]`

**Location**: Line 231

**装饰器**: govmcp_tool(name='query_environmental_impact_approval', description='查询环评审批进度')

查询环境影响评价审批进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `project_name` | `str` | Yes | `-` |  |
| `approval_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_fire_approval(project_name: str, application_no: str) -> Dict[str, Any]`

**Location**: Line 262

**装饰器**: govmcp_tool(name='query_fire_approval', description='查询消防审批进度')

查询建设工程消防设计审核/验收审批进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `project_name` | `str` | Yes | `-` |  |
| `application_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_building_permit(project_name: str, permit_no: str) -> Dict[str, Any]`

**Location**: Line 293

**装饰器**: govmcp_tool(name='query_building_permit', description='查询建筑许可审批进度')

查询建筑工程施工许可审批进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `project_name` | `str` | Yes | `-` |  |
| `permit_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_food_business_license(company_name: str, business_address: str, business_type: str, food_category: str) -> Dict[str, Any]`

**Location**: Line 324

**装饰器**: govmcp_tool(name='apply_food_business_license', description='申请食品经营许可证')

申请食品经营许可证。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `business_address` | `str` | Yes | `-` |  |
| `business_type` | `str` | Yes | `-` |  |
| `food_category` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_drug_operation_license(company_name: str, warehouse_address: str, business_scope: str, storage_capacity: float) -> Dict[str, Any]`

**Location**: Line 359

**装饰器**: govmcp_tool(name='apply_drug_operation_license', description='申请药品经营许可证')

申请药品经营许可证。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `warehouse_address` | `str` | Yes | `-` |  |
| `business_scope` | `str` | Yes | `-` |  |
| `storage_capacity` | `float` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_medical_device_license(company_name: str, product_category: str, business_scope: str) -> Dict[str, Any]`

**Location**: Line 394

**装饰器**: govmcp_tool(name='apply_medical_device_license', description='申请医疗器械经营许可证')

申请医疗器械经营许可证。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `product_category` | `str` | Yes | `-` |  |
| `business_scope` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_intellectual_property(company_name: str, ip_type: str, ip_name: str, application_type: str) -> Dict[str, Any]`

**Location**: Line 427

**装饰器**: govmcp_tool(name='apply_intellectual_property', description='申请知识产权保护')

申请知识产权（著作权、软件著作权等）保护。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `ip_type` | `str` | Yes | `-` |  |
| `ip_name` | `str` | Yes | `-` |  |
| `application_type` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_trademark_registration(company_name: str, trademark_name: str, application_no: str) -> Dict[str, Any]`

**Location**: Line 463

**装饰器**: govmcp_tool(name='query_trademark_registration', description='查询商标注册进度')

查询商标注册申请进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `trademark_name` | `str` | Yes | `-` |  |
| `application_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_patent_application(applicant: str, patent_type: str, application_no: str) -> Dict[str, Any]`

**Location**: Line 496

**装饰器**: govmcp_tool(name='query_patent_application', description='查询专利申请进度')

查询专利申请进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `applicant` | `str` | Yes | `-` |  |
| `patent_type` | `str` | Yes | `-` |  |
| `application_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_high_tech_enterprise(company_name: str, industry: str, rd_expense_ratio: float, patent_count: int) -> Dict[str, Any]`

**Location**: Line 529

**装饰器**: govmcp_tool(name='apply_high_tech_enterprise', description='申请高新技术企业认定')

申请高新技术企业认定。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `industry` | `str` | Yes | `-` |  |
| `rd_expense_ratio` | `float` | Yes | `-` |  |
| `patent_count` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_tech_project(company_name: str, project_name: str, project_type: str, budget: float) -> Dict[str, Any]`

**Location**: Line 565

**装饰器**: govmcp_tool(name='apply_tech_project', description='申报科技项目')

申报科技计划项目。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `project_name` | `str` | Yes | `-` |  |
| `project_type` | `str` | Yes | `-` |  |
| `budget` | `float` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_government_procurement(keyword: str, region: str) -> Dict[str, Any]`

**Location**: Line 601

**装饰器**: govmcp_tool(name='query_government_procurement', description='查询政府采购招标信息')

查询政府采购招标公告信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `keyword` | `str` | Yes | `-` |  |
| `region` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_enterprise_credit_report(company_name: str, credit_code: str) -> Dict[str, Any]`

**Location**: Line 638

**装饰器**: govmcp_tool(name='query_enterprise_credit_report', description='查询企业信用报告')

查询企业信用报告。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `credit_code` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_listing_guidance_progress(company_name: str, stock_code: str) -> Dict[str, Any]`

**Location**: Line 673

**装饰器**: govmcp_tool(name='query_listing_guidance_progress', description='查询上市辅导进度')

查询企业上市辅导进度。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `stock_code` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

### `govmcp.tools.government.environmental`

govmcp.tools.government.environmental — 环保监测工具模块

提供空气质量、水质、土壤、噪声、固废等环境监测和环保监管服务的工具函数。

#### Functions

##### `query_air_quality(region: str, monitoring_station: str, date: str) -> Dict[str, Any]`

**Location**: Line 17

**装饰器**: govmcp_tool(name='query_air_quality', description='查询空气质量监测数据')

查询空气质量监测数据。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `region` | `str` | Yes | `-` |  |
| `monitoring_station` | `str` | Yes | `-` |  |
| `date` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_water_quality(river_name: str, section_name: str, date: str) -> Dict[str, Any]`

**Location**: Line 56

**装饰器**: govmcp_tool(name='query_water_quality', description='查询水质监测数据')

查询水质监测数据。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `river_name` | `str` | Yes | `-` |  |
| `section_name` | `str` | Yes | `-` |  |
| `date` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `detect_soil_pollution(location: str, land_use: str, sampling_date: str) -> Dict[str, Any]`

**Location**: Line 94

**装饰器**: govmcp_tool(name='detect_soil_pollution', description='土壤污染检测')

土壤污染状况检测查询。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `location` | `str` | Yes | `-` |  |
| `land_use` | `str` | Yes | `-` |  |
| `sampling_date` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_noise_monitoring(monitoring_point: str, date: str, time_period: str) -> Dict[str, Any]`

**Location**: Line 133

**装饰器**: govmcp_tool(name='query_noise_monitoring', description='查询噪声监测数据')

查询环境噪声监测数据。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `monitoring_point` | `str` | Yes | `-` |  |
| `date` | `str` | Yes | `-` |  |
| `time_period` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_solid_waste_disposal(company_name: str, waste_type: str) -> Dict[str, Any]`

**Location**: Line 168

**装饰器**: govmcp_tool(name='query_solid_waste_disposal', description='查询固废处理监管信息')

查询固体废物处理处置监管信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `waste_type` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_hazardous_waste_transfer(manifest_no: str) -> Dict[str, Any]`

**Location**: Line 202

**装饰器**: govmcp_tool(name='query_hazardous_waste_transfer', description='查询危险废物转移联单')

查询危险废物转移联单信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `manifest_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_radiation_monitoring(monitoring_location: str, monitoring_type: str, date: str) -> Dict[str, Any]`

**Location**: Line 234

**装饰器**: govmcp_tool(name='query_radiation_monitoring', description='查询辐射环境监测数据')

查询辐射环境监测数据。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `monitoring_location` | `str` | Yes | `-` |  |
| `monitoring_type` | `str` | Yes | `-` |  |
| `date` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_pollution_discharge_permit(company_name: str, permit_no: str) -> Dict[str, Any]`

**Location**: Line 269

**装饰器**: govmcp_tool(name='query_pollution_discharge_permit', description='查询排污许可证信息')

查询企业排污许可证信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `permit_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_environmental_impact_assessment(project_name: str, eia_document_no: str) -> Dict[str, Any]`

**Location**: Line 307

**装饰器**: govmcp_tool(name='query_environmental_impact_assessment', description='查询环境影响评价信息')

查询环境影响评价信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `project_name` | `str` | Yes | `-` |  |
| `eia_document_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_environmental_penalty(company_name: str, region: str) -> Dict[str, Any]`

**Location**: Line 340

**装饰器**: govmcp_tool(name='query_environmental_penalty', description='查询环保处罚记录')

查询企业环保行政处罚记录。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `region` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `apply_cleaner_production_audit(company_name: str, industry: str, production_scale: str) -> Dict[str, Any]`

**Location**: Line 370

**装饰器**: govmcp_tool(name='apply_cleaner_production_audit', description='申请清洁生产审核')

申请清洁生产审核。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `industry` | `str` | Yes | `-` |  |
| `production_scale` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_environmental_acceptance(project_name: str, acceptance_no: str) -> Dict[str, Any]`

**Location**: Line 405

**装饰器**: govmcp_tool(name='query_environmental_acceptance', description='查询环保竣工验收信息')

查询建设项目竣工环境保护验收信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `project_name` | `str` | Yes | `-` |  |
| `acceptance_no` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_environmental_facility_operation(company_name: str, facility_type: str) -> Dict[str, Any]`

**Location**: Line 438

**装饰器**: govmcp_tool(name='query_environmental_facility_operation', description='查询环保设施运行数据')

查询企业环保设施运行数据。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |
| `facility_type` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_ecological_red_line(location: str) -> Dict[str, Any]`

**Location**: Line 473

**装饰器**: govmcp_tool(name='query_ecological_red_line', description='查询生态红线保护区信息')

查询区域生态红线保护信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `location` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_environmental_emergency_response(company_name: str) -> Dict[str, Any]`

**Location**: Line 507

**装饰器**: govmcp_tool(name='query_environmental_emergency_response', description='查询环境应急响应信息')

查询企业环境应急响应相关信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

### `govmcp.tools.government.smart_city`

govmcp.tools.government.smart_city — 智慧城市工具模块

提供智慧交通、智慧水务、智慧社区、智慧养老、应急指挥等智慧城市服务的工具函数。

#### Functions

##### `control_smart_traffic_light(intersection_id: str, action: str, duration: int) -> Dict[str, Any]`

**Location**: Line 17

**装饰器**: govmcp_tool(name='control_smart_traffic_light', description='智慧交通信号灯控制')

智慧交通信号灯控制。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `intersection_id` | `str` | Yes | `-` |  |
| `action` | `str` | Yes | `-` |  |
| `duration` | `int` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_public_parking(district: str, street: str) -> Dict[str, Any]`

**Location**: Line 51

**装饰器**: govmcp_tool(name='query_public_parking', description='查询公共停车位')

查询附近公共停车位信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `district` | `str` | Yes | `-` |  |
| `street` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `manage_smart_streetlight(streetlight_id: str, action: str, brightness: Optional[int] = None) -> Dict[str, Any]`

**Location**: Line 90

**装饰器**: govmcp_tool(name='manage_smart_streetlight', description='智慧路灯管理')

智慧路灯管理控制。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `streetlight_id` | `str` | Yes | `-` |  |
| `action` | `str` | Yes | `-` |  |
| `brightness` | `Optional[int]` | No | `None` |  |

**Returns** `Dict[str, Any]`

---

##### `monitor_smart_water(area: str, meter_id: str) -> Dict[str, Any]`

**Location**: Line 123

**装饰器**: govmcp_tool(name='monitor_smart_water', description='智慧水务监控')

智慧水务监控系统。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `area` | `str` | Yes | `-` |  |
| `meter_id` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `supervise_smart_gas(area: str, meter_id: str) -> Dict[str, Any]`

**Location**: Line 161

**装饰器**: govmcp_tool(name='supervise_smart_gas', description='智慧燃气监管')

智慧燃气监管系统。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `area` | `str` | Yes | `-` |  |
| `meter_id` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `manage_smart_heating(building_id: str, action: str, target_temperature: Optional[float] = None) -> Dict[str, Any]`

**Location**: Line 196

**装饰器**: govmcp_tool(name='manage_smart_heating', description='智慧供热管理')

智慧供热管理系统。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `building_id` | `str` | Yes | `-` |  |
| `action` | `str` | Yes | `-` |  |
| `target_temperature` | `Optional[float]` | No | `None` |  |

**Returns** `Dict[str, Any]`

---

##### `query_smart_community(community_name: str, service_type: str) -> Dict[str, Any]`

**Location**: Line 231

**装饰器**: govmcp_tool(name='query_smart_community', description='智慧社区服务查询')

智慧社区服务查询。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `community_name` | `str` | Yes | `-` |  |
| `service_type` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_smart_city_enforcement(area: str, violation_type: Optional[str] = None) -> Dict[str, Any]`

**Location**: Line 263

**装饰器**: govmcp_tool(name='query_smart_city_enforcement', description='智慧城管执法查询')

智慧城管执法系统查询。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `area` | `str` | Yes | `-` |  |
| `violation_type` | `Optional[str]` | No | `None` |  |

**Returns** `Dict[str, Any]`

---

##### `query_public_bicycle(location: str) -> Dict[str, Any]`

**Location**: Line 302

**装饰器**: govmcp_tool(name='query_public_bicycle', description='查询公共自行车')

查询公共自行车站点信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `location` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_smart_elderly_care(elderly_name: str, id_number: str, service_type: str) -> Dict[str, Any]`

**Location**: Line 343

**装饰器**: govmcp_tool(name='query_smart_elderly_care', description='智慧养老服务查询')

智慧养老服务查询。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `elderly_name` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |
| `service_type` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_smart_education(student_name: str, student_id: str, service_type: str) -> Dict[str, Any]`

**Location**: Line 379

**装饰器**: govmcp_tool(name='query_smart_education', description='智慧教育服务查询')

智慧教育服务查询。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `student_name` | `str` | Yes | `-` |  |
| `student_id` | `str` | Yes | `-` |  |
| `service_type` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `book_smart_medical(patient_name: str, id_number: str, hospital: str, department: str, booking_date: str, doctor: Optional[str] = None) -> Dict[str, Any]`

**Location**: Line 419

**装饰器**: govmcp_tool(name='book_smart_medical', description='智慧医疗预约')

智慧医疗预约挂号。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `patient_name` | `str` | Yes | `-` |  |
| `id_number` | `str` | Yes | `-` |  |
| `hospital` | `str` | Yes | `-` |  |
| `department` | `str` | Yes | `-` |  |
| `booking_date` | `str` | Yes | `-` |  |
| `doctor` | `Optional[str]` | No | `None` |  |

**Returns** `Dict[str, Any]`

---

##### `dispatch_emergency_command(incident_type: str, location: str, severity: str, reporter: str, description: str) -> Dict[str, Any]`

**Location**: Line 462

**装饰器**: govmcp_tool(name='dispatch_emergency_command', description='应急指挥调度')

应急指挥调度系统。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `incident_type` | `str` | Yes | `-` |  |
| `location` | `str` | Yes | `-` |  |
| `severity` | `str` | Yes | `-` |  |
| `reporter` | `str` | Yes | `-` |  |
| `description` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_grid_management(grid_id: str, query_type: str) -> Dict[str, Any]`

**Location**: Line 503

**装饰器**: govmcp_tool(name='query_grid_management', description='网格化管理查询')

网格化管理系统查询。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `grid_id` | `str` | Yes | `-` |  |
| `query_type` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `query_snow亮的视频(camera_id: str, query_type: str, start_time: str, end_time: str) -> Dict[str, Any]`

**Location**: Line 544

**装饰器**: govmcp_tool(name='query_snow亮的视频', description='雪亮工程视频监控查询')

雪亮工程视频监控系统查询。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `camera_id` | `str` | Yes | `-` |  |
| `query_type` | `str` | Yes | `-` |  |
| `start_time` | `str` | Yes | `-` |  |
| `end_time` | `str` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

### `govmcp.tools.registry`

govmcp.tools.registry — 工具注册中心

====================================

提供 ToolRegistry 类用于管理工具注册/注销/列表/调用，

以及 govmcp_tool 装饰器用于便捷地将 Python 函数注册为 MCP 工具。

标准 MCP 输出格式:

- tools/list: {"tools": [{"name": "...", "description": "...", "inputSchema": {...}}]}

- tools/call: {"content": [{"type": "text", "text": "..."}], "isError": false}

#### Functions

##### `govmcp_tool(name: Optional[str] = None, description: str = '', approval_required: bool = False, audit_enabled: bool = True) -> Callable`

**Location**: Line 288

装饰器：将 Python 函数自动注册为 MCP 工具。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `Optional[str]` | No | `None` |  |
| `description` | `str` | No | `''` |  |
| `approval_required` | `bool` | No | `False` |  |
| `audit_enabled` | `bool` | No | `True` |  |

**Returns** `Callable`

---

##### `to_mcp_dict() -> Dict[str, Any]`

**Location**: Line 128

转为标准 MCP tools/list 条目。

**Returns** `Dict[str, Any]`

---

##### `__init__() -> None`

**Location**: Line 154

**Returns** `None`

---

##### `register(name: str, description: str, input_schema: Dict[str, Any], handler: Callable, approval_required: bool = False, audit_enabled: bool = True) -> None`

**Location**: Line 159

注册一个工具。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `description` | `str` | Yes | `-` |  |
| `input_schema` | `Dict[str, Any]` | Yes | `-` |  |
| `handler` | `Callable` | Yes | `-` |  |
| `approval_required` | `bool` | No | `False` |  |
| `audit_enabled` | `bool` | No | `True` |  |

**Returns** `None`

---

##### `unregister(name: str) -> None`

**Location**: Line 193

注销一个工具。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |

**Returns** `None`

---

##### `get(name: str) -> ToolInfo`

**Location**: Line 209

获取工具信息。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |

**Returns** `ToolInfo`

---

##### `count() -> int`

**Location**: Line 226

返回已注册工具数量。

**Returns** `int`

---

##### `list_tools() -> List[Dict[str, Any]]`

**Location**: Line 232

列出所有工具（标准 MCP tools/list 格式）。

**Returns** `List[Dict[str, Any]]`

---

##### `call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]`

**Location**: Line 241

执行工具并返回标准 MCP tools/call 格式。

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | Yes | `-` |  |
| `arguments` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `Dict[str, Any]`

---

##### `decorator(func: Callable) -> Callable`

**Location**: Line 308

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `func` | `Callable` | Yes | `-` |  |

**Returns** `Callable`

---

##### `wrapper(**args, ****kwargs) -> Any`

**Location**: Line 323

**装饰器**: functools.wraps(func)

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `*args` | `Any` | No | `-` | Variable positional arguments |
| `**kwargs` | `Any` | No | `-` | Variable keyword arguments |

**Returns** `Any`

---

#### Classes

##### `ToolInfo`
`Dataclass`

MCP 工具的描述信息。

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `name` | `str` |
| `description` | `str` |
| `input_schema` | `Dict[str, Any]` |
| `handler` | `Callable` |
| `approval_required` | `bool` |
| `audit_enabled` | `bool` |

**Methods**

- `to_mcp_dict()` - 转为标准 MCP tools/list 条目。

---

##### `ToolRegistry`

MCP 工具注册中心。

**Methods**

- `register()` - 注册一个工具。
- `unregister()` - 注销一个工具。
- `get()` - 获取工具信息。
- `count()` - 返回已注册工具数量。
- `list_tools()` - 列出所有工具（标准 MCP tools/list 格式）。
- ... (1 more)

---

---

## transport

**模块路径**: `govmcp.transport`

### `govmcp.transport.base`

govmcp.transport.base — 传输层抽象基类

定义 Transport 接口，所有传输方式（Stdio、WebSocket、HTTP）都需实现此接口。

#### Functions

##### `from_dict(data: Dict[str, Any]) -> Message`

**Location**: Line 54

**装饰器**: classmethod

从字典创建消息

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `Message`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 63

转换为字典

**Returns** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> Response`

**Location**: Line 85

**装饰器**: classmethod

从字典创建响应

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | Yes | `-` |  |

**Returns** `Response`

---

##### `to_dict() -> Dict[str, Any]`

**Location**: Line 99

转换为字典

**Returns** `Dict[str, Any]`

---

##### `on_message(message: Message) -> None`

**Location**: Line 115

**装饰器**: abstractmethod

收到消息回调

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | Yes | `-` |  |

**Returns** `None`

---

##### `on_error(error: Exception) -> None`

**Location**: Line 120

**装饰器**: abstractmethod

错误回调

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `error` | `Exception` | Yes | `-` |  |

**Returns** `None`

---

##### `on_disconnect() -> None`

**Location**: Line 125

**装饰器**: abstractmethod

断开连接回调

**Returns** `None`

---

##### `on_connect() -> None`

**Location**: Line 129

连接成功回调（可选）

**Returns** `None`

---

##### `on_heartbeat() -> None`

**Location**: Line 133

心跳回调（可选）

**Returns** `None`

---

##### `__init__(config: Optional[TransportConfig] = None) -> None`

**Location**: Line 149

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `Optional[TransportConfig]` | No | `None` |  |

**Returns** `None`

---

##### `connected() -> bool`

**Location**: Line 155

**装饰器**: property

是否已连接

**Returns** `bool`

---

##### `transport_type() -> TransportType`

**Location**: Line 160

**装饰器**: property

传输类型

**Returns** `TransportType`

---

##### `set_callbacks(callbacks: TransportCallbacks) -> None`

**Location**: Line 164

设置回调处理器

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `callbacks` | `TransportCallbacks` | Yes | `-` |  |

**Returns** `None`

---

##### `async connect() -> None`

**Location**: Line 169

**装饰器**: abstractmethod

建立连接

**Returns** `None`

---

##### `async disconnect() -> None`

**Location**: Line 174

**装饰器**: abstractmethod

断开连接

**Returns** `None`

---

##### `async send(message: Message) -> None`

**Location**: Line 179

**装饰器**: abstractmethod

发送消息

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | Yes | `-` |  |

**Returns** `None`

---

##### `async send_response(response: Response) -> None`

**Location**: Line 184

**装饰器**: abstractmethod

发送响应

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `response` | `Response` | Yes | `-` |  |

**Returns** `None`

---

##### `__init__(config: Optional[TransportConfig] = None) -> None`

**Location**: Line 220

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `Optional[TransportConfig]` | No | `None` |  |

**Returns** `None`

---

##### `async connect() -> None`

**Location**: Line 226

建立 stdio 连接

**Returns** `None`

---

##### `async disconnect() -> None`

**Location**: Line 238

断开 stdio 连接

**Returns** `None`

---

##### `async send(message: Message) -> None`

**Location**: Line 256

通过 stdout 发送消息

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | Yes | `-` |  |

**Returns** `None`

---

##### `async send_response(response: Response) -> None`

**Location**: Line 264

通过 stdout 发送响应

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `response` | `Response` | Yes | `-` |  |

**Returns** `None`

---

##### `__init__(transport: 'WebSocketTransport') -> None`

**Location**: Line 303

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `transport` | `'WebSocketTransport'` | Yes | `-` |  |

**Returns** `None`

---

##### `on_message(message: Message) -> None`

**Location**: Line 306

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | Yes | `-` |  |

**Returns** `None`

---

##### `on_error(error: Exception) -> None`

**Location**: Line 310

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `error` | `Exception` | Yes | `-` |  |

**Returns** `None`

---

##### `on_disconnect() -> None`

**Location**: Line 314

**Returns** `None`

---

##### `on_connect() -> None`

**Location**: Line 318

**Returns** `None`

---

##### `__init__(config: Optional[TransportConfig] = None) -> None`

**Location**: Line 330

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `Optional[TransportConfig]` | No | `None` |  |

**Returns** `None`

---

##### `connected() -> bool`

**Location**: Line 337

**装饰器**: property

**Returns** `bool`

---

##### `async connect() -> None`

**Location**: Line 340

建立 WebSocket 连接

**Returns** `None`

---

##### `async disconnect() -> None`

**Location**: Line 374

断开 WebSocket 连接

**Returns** `None`

---

##### `async send(message: Message) -> None`

**Location**: Line 396

发送 WebSocket 消息

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | Yes | `-` |  |

**Returns** `None`

---

##### `async send_response(response: Response) -> None`

**Location**: Line 421

发送 WebSocket 响应

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `response` | `Response` | Yes | `-` |  |

**Returns** `None`

---

##### `__init__(config: Optional[TransportConfig] = None) -> None`

**Location**: Line 491

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `Optional[TransportConfig]` | No | `None` |  |

**Returns** `None`

---

##### `async connect() -> None`

**Location**: Line 497

建立 HTTP 连接

**Returns** `None`

---

##### `async disconnect() -> None`

**Location**: Line 513

断开 HTTP 连接

**Returns** `None`

---

##### `async send(message: Message) -> None`

**Location**: Line 527

发送 HTTP POST 请求

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | Yes | `-` |  |

**Returns** `None`

---

##### `async send_response(response: Response) -> None`

**Location**: Line 570

HTTP 响应直接返回（由服务器端处理）

**Parameters**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `response` | `Response` | Yes | `-` |  |

**Returns** `None`

---

##### `async get_sse_stream() -> Any`

**Location**: Line 574

获取 SSE 流

**Returns** `Any`

---

#### Classes

##### `TransportType`
`Enum`

**Base Classes**: `Enum`

传输类型枚举

**Enum Values**

| 名称 | 值 |
|:---|:---|
| `STDIO` | `'stdio'` |
| `WEBSOCKET` | `'websocket'` |
| `HTTP` | `'http'` |
| `SSE` | `'sse'` |

---

##### `TransportConfig`
`Dataclass`

传输层配置

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `transport_type` | `TransportType` |
| `host` | `str` |
| `port` | `int` |
| `path` | `str` |
| `crypto_enabled` | `bool` |
| `sm4_key` | `Optional[bytes]` |
| `auth_token` | `Optional[str]` |
| `heartbeat_interval` | `float` |
| `max_message_size` | `int` |
| `request_timeout` | `float` |
| `cors_enabled` | `bool` |
| `cors_origins` | `List[str]` |

---

##### `Message`
`Dataclass`

MCP 消息封装

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `method` | `str` |
| `params` | `Dict[str, Any]` |
| `msg_id` | `Optional[str]` |
| `jsonrpc` | `str` |

**Methods**

- `from_dict()` - 从字典创建消息
- `to_dict()` - 转换为字典

---

##### `Response`
`Dataclass`

MCP 响应封装

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `result` | `Any` |
| `error` | `Optional[Dict[str, Any]]` |
| `msg_id` | `Optional[str]` |
| `jsonrpc` | `str` |

**Methods**

- `from_dict()` - 从字典创建响应
- `to_dict()` - 转换为字典

---

##### `TransportCallbacks`

**Base Classes**: `ABC`

传输层回调接口

**Methods**

- `on_message()` - 收到消息回调
- `on_error()` - 错误回调
- `on_disconnect()` - 断开连接回调
- `on_connect()` - 连接成功回调（可选）
- `on_heartbeat()` - 心跳回调（可选）

---

##### `Transport`

**Base Classes**: `ABC`

传输层抽象基类

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `Optional[TransportConfig]` |

**Methods**

- `connected()` - 是否已连接
- `transport_type()` - 传输类型
- `set_callbacks()` - 设置回调处理器
- `_safe_callback_error()` - 安全调用错误回调

---

##### `StdioTransport`

**Base Classes**: `Transport`

Stdio 传输层实现

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `Optional[TransportConfig]` |

---

##### `WebSocketTransportCallbacks`

**Base Classes**: `TransportCallbacks`

WebSocket 传输层回调

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `transport` | `'WebSocketTransport'` |

**Methods**

- `on_message()` - 
- `on_error()` - 
- `on_disconnect()` - 
- `on_connect()` - 

---

##### `WebSocketTransport`

**Base Classes**: `Transport`

WebSocket 传输层实现

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `Optional[TransportConfig]` |

**Methods**

- `connected()` - 

---

##### `HTTPTransport`

**Base Classes**: `Transport`

HTTP/SSE 传输层实现

**Attributes**

| 名称 | 类型 |
|:---|:---|
| `config` | `Optional[TransportConfig]` |

---

---

## Error Reference

| Error Type | Description |
|:---|:---|
| `ValueError` | Invalid parameter value |
| `TypeError` | Invalid parameter type |
| `KeyError` | Key not found |
| `RuntimeError` | Runtime error |
| `NotImplementedError` | Feature not implemented |

---

## Type Reference Index

### `govmcp.crypto.audit`

| 类型 | 引用 |
|:---|:---|
| `AuditChain` | [AuditChain](#) |
| `AuditEntry` | [AuditEntry](#) |
| `bytes` | [bytes](#) |
| `int` | [int](#) |
| `str` | [str](#) |

### `govmcp.models.adapters.baichuan`

| 类型 | 引用 |
|:---|:---|
| `BaichuanAdapter` | [BaichuanAdapter](#) |
| `List[Dict[str, str]]` | [List[Dict[str, str]]](#) |
| `Optional[str]` | [Optional[str]](#) |

### `govmcp.models.adapters.base`

| 类型 | 引用 |
|:---|:---|
| `LLMAdapter` | [LLMAdapter](#) |
| `Optional[List[Dict[str, str]]]` | [Optional[List[Dict[str, str]]]](#) |

### `govmcp.models.adapters.doubao`

| 类型 | 引用 |
|:---|:---|
| `DoubaoAdapter` | [DoubaoAdapter](#) |

### `govmcp.models.adapters.hunyuan`

| 类型 | 引用 |
|:---|:---|
| `HunyuanAdapter` | [HunyuanAdapter](#) |

### `govmcp.models.adapters.minimax`

| 类型 | 引用 |
|:---|:---|
| `MinimaxAdapter` | [MinimaxAdapter](#) |

### `govmcp.models.adapters.moonshot`

| 类型 | 引用 |
|:---|:---|
| `MoonshotAdapter` | [MoonshotAdapter](#) |

### `govmcp.models.adapters.others`

| 类型 | 引用 |
|:---|:---|
| `OthersAdapter` | [OthersAdapter](#) |

### `govmcp.models.adapters.pangu`

| 类型 | 引用 |
|:---|:---|
| `PanguAdapter` | [PanguAdapter](#) |

### `govmcp.models.adapters.qwen`

| 类型 | 引用 |
|:---|:---|
| `QwenAdapter` | [QwenAdapter](#) |

### `govmcp.models.adapters.spark`

| 类型 | 引用 |
|:---|:---|
| `SparkAdapter` | [SparkAdapter](#) |

### `govmcp.models.adapters.wenxin`

| 类型 | 引用 |
|:---|:---|
| `WenxinAdapter` | [WenxinAdapter](#) |

### `govmcp.models.adapters.zhipu`

| 类型 | 引用 |
|:---|:---|
| `ZhipuAdapter` | [ZhipuAdapter](#) |

### `govmcp.models.registry`

| 类型 | 引用 |
|:---|:---|
| `LLMProvider` | [LLMProvider](#) |
| `ModelConfig` | [ModelConfig](#) |
| `ModelRegistry` | [ModelRegistry](#) |
| `Optional[LLMProvider]` | [Optional[LLMProvider]](#) |

### `govmcp.protocol.authorization`

| 类型 | 引用 |
|:---|:---|
| `AuthorizationCode` | [AuthorizationCode](#) |
| `AuthorizationGrant` | [AuthorizationGrant](#) |
| `AuthorizationManager` | [AuthorizationManager](#) |
| `AuthorizationScope` | [AuthorizationScope](#) |
| `Callable[[str, Dict[str, Any]], bool]` | [Callable[[str, Dict[str, Any]], bool]](#) |
| `ClientInfo` | [ClientInfo](#) |
| `Dict[str, Any]` | [Dict[str, Any]](#) |
| `FineGrainedPermissionManager` | [FineGrainedPermissionManager](#) |
| `GrantType` | [GrantType](#) |
| `List[Permission]` | [List[Permission]](#) |
| `List[str]` | [List[str]](#) |
| `Optional[Dict[str, Any]]` | [Optional[Dict[str, Any]]](#) |
| `Optional[List[str]]` | [Optional[List[str]]](#) |
| `Optional[Set[GrantType]]` | [Optional[Set[GrantType]]](#) |
| `Optional[Set[str]]` | [Optional[Set[str]]](#) |
| `Permission` | [Permission](#) |
| `TokenInfo` | [TokenInfo](#) |
| `TokenType` | [TokenType](#) |

### `govmcp.protocol.elicitation`

| 类型 | 引用 |
|:---|:---|
| `Callable[[ElicitResponse], None]` | [Callable[[ElicitResponse], None]](#) |
| `ConsoleElicitationHandler` | [ConsoleElicitationHandler](#) |
| `ElicitRequest` | [ElicitRequest](#) |
| `ElicitResponse` | [ElicitResponse](#) |
| `ElicitStatus` | [ElicitStatus](#) |
| `ElicitType` | [ElicitType](#) |
| `ElicitationHandler` | [ElicitationHandler](#) |
| `ElicitationManager` | [ElicitationManager](#) |
| `Optional[Callable[[str], str]]` | [Optional[Callable[[str], str]]](#) |
| `Optional[Dict[str, str]]` | [Optional[Dict[str, str]]](#) |
| `URLElicitation` | [URLElicitation](#) |
| `Union[ElicitType, str]` | [Union[ElicitType, str]](#) |
| `bool` | [bool](#) |
| `float` | [float](#) |

### `govmcp.protocol.http_server`

| 类型 | 引用 |
|:---|:---|
| `Callable[[HTTPRequest], Any]` | [Callable[[HTTPRequest], Any]](#) |
| `HTTPMethod` | [HTTPMethod](#) |
| `HTTPRequest` | [HTTPRequest](#) |
| `HTTPResponse` | [HTTPResponse](#) |
| `HTTPServer` | [HTTPServer](#) |
| `HTTPServerFactory` | [HTTPServerFactory](#) |
| `Optional[Callable[[HTTPRequest], Any]]` | [Optional[Callable[[HTTPRequest], Any]]](#) |
| `Optional[bytes]` | [Optional[bytes]](#) |

### `govmcp.protocol.sampling`

| 类型 | 引用 |
|:---|:---|
| `Callable[[str, Any], None]` | [Callable[[str, Any], None]](#) |
| `EmbeddedSamplingProvider` | [EmbeddedSamplingProvider](#) |
| `List[Dict[str, Any]]` | [List[Dict[str, Any]]](#) |
| `List[SamplingMessage]` | [List[SamplingMessage]](#) |
| `Optional[int]` | [Optional[int]](#) |
| `Role` | [Role](#) |
| `SamplingCreateMessageRequest` | [SamplingCreateMessageRequest](#) |
| `SamplingManager` | [SamplingManager](#) |
| `SamplingMessage` | [SamplingMessage](#) |
| `SamplingMessageRole` | [SamplingMessageRole](#) |
| `SamplingParameters` | [SamplingParameters](#) |
| `SamplingProvider` | [SamplingProvider](#) |
| `SamplingResponse` | [SamplingResponse](#) |

### `govmcp.protocol.server`

| 类型 | 引用 |
|:---|:---|
| `Callable[..., Any]` | [Callable[..., Any]](#) |
| `Callable[[str], Any]` | [Callable[[str], Any]](#) |
| `GovMCPServer` | [GovMCPServer](#) |

### `govmcp.protocol.tasks`

| 类型 | 引用 |
|:---|:---|
| `Optional[TaskStatus]` | [Optional[TaskStatus]](#) |
| `Optional[float]` | [Optional[float]](#) |
| `SSEHandler` | [SSEHandler](#) |
| `TaskCancelError` | [TaskCancelError](#) |
| `TaskInfo` | [TaskInfo](#) |
| `TaskManager` | [TaskManager](#) |
| `TaskNotFoundError` | [TaskNotFoundError](#) |
| `TaskStatus` | [TaskStatus](#) |
| `TaskSubscriber` | [TaskSubscriber](#) |
| `asyncio.AbstractEventLoop` | [asyncio.AbstractEventLoop](#) |

### `govmcp.protocol.websocket_server`

| 类型 | 引用 |
|:---|:---|
| `Callable[[str, Dict[str, Any]], Any]` | [Callable[[str, Dict[str, Any]], Any]](#) |
| `ClientConnection` | [ClientConnection](#) |
| `ConnectionState` | [ConnectionState](#) |
| `Optional[Callable[[str, Dict[str, Any]], Any]]` | [Optional[Callable[[str, Dict[str, Any]], Any]]](#) |
| `WebSocketServer` | [WebSocketServer](#) |
| `WebSocketServerFactory` | [WebSocketServerFactory](#) |

### `govmcp.server.approval`

| 类型 | 引用 |
|:---|:---|
| `ApprovalFlow` | [ApprovalFlow](#) |
| `ApprovalStatus` | [ApprovalStatus](#) |
| `ApprovalStep` | [ApprovalStep](#) |

### `govmcp.tools.government.approval_workflow`

| 类型 | 引用 |
|:---|:---|
| `Dict[str, float]` | [Dict[str, float]](#) |

### `govmcp.tools.registry`

| 类型 | 引用 |
|:---|:---|
| `Callable` | [Callable](#) |
| `ToolInfo` | [ToolInfo](#) |
| `ToolRegistry` | [ToolRegistry](#) |

### `govmcp.transport.base`

| 类型 | 引用 |
|:---|:---|
| `'WebSocketTransport'` | ['WebSocketTransport'](#) |
| `Exception` | [Exception](#) |
| `HTTPTransport` | [HTTPTransport](#) |
| `Message` | [Message](#) |
| `Optional[TransportConfig]` | [Optional[TransportConfig]](#) |
| `Response` | [Response](#) |
| `StdioTransport` | [StdioTransport](#) |
| `Transport` | [Transport](#) |
| `TransportCallbacks` | [TransportCallbacks](#) |
| `TransportConfig` | [TransportConfig](#) |
| `TransportType` | [TransportType](#) |
| `WebSocketTransport` | [WebSocketTransport](#) |
| `WebSocketTransportCallbacks` | [WebSocketTransportCallbacks](#) |

---

*Generated by govmcp Documentation Auto-Generation System · Version 1.0.0*