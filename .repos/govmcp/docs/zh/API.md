# govmcp API 参考文档

> **版本**: `1.0.0`
> **生成时间**: 2026-05-13 15:57:50

---

## 概览

本文档提供了 govmcp 的完整 API 参考。govmcp 是国产信创 MCP 协议实现，支持:

- **国密加密**: SM2/SM3/SM4 加密算法
- **审批工作流**: 多级审批链配置
- **不可篡改审计链**: SM3 链式哈希
- **模型适配**: 19+ 国产大模型

---

## 快速开始

### 安装

```bash
pip install govmcp
```

### 基本使用

```python
from govmcp import GovMCPServer, sm3_hash, ApprovalFlow

# 创建服务器
server = GovMCPServer('my-server', '1.0')

# 使用国密哈希
digest = sm3_hash(b'data')

# 使用审批工作流
flow = ApprovalFlow(['level1', 'level2'])
```

---

## 加密模块

**模块路径**: `govmcp.crypto`

### `govmcp.crypto.audit`

不可篡改审计链 — SM3哈希链式防篡改

每条审计记录包含操作元数据，并通过SM3哈希链接到前一条记录。

任何对历史记录的修改都会破坏哈希链，可被 verify() 检测。

设计原则:

- 追加写入 (append-only)：无删除/修改接口

- 创世区块：第一条记录的 prev_hash = 64个'0'

- 篡改检测：遍历全链重新计算 current_hash 并与存储值比对

#### 函数

##### `__init__()`

**位置**: 行 54

---

##### `add_entry(operation: str, operator: str, input_data: bytes, output_data: bytes, approval_status: str = 'pending') -> AuditEntry`

**位置**: 行 57

追加一条审计记录。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `operation` | `str` | 是 | `-` |  |
| `operator` | `str` | 是 | `-` |  |
| `input_data` | `bytes` | 是 | `-` |  |
| `output_data` | `bytes` | 是 | `-` |  |
| `approval_status` | `str` | 否 | `'pending'` |  |

**返回** `AuditEntry`

---

##### `verify() -> bool`

**位置**: 行 107

验证整条审计链的完整性。

**返回** `bool`

---

##### `to_dict_list() -> List[dict]`

**位置**: 行 149

将审计链转换为字典列表，便于序列化。

**返回** `List[dict]`

---

##### `export(indent: int = 2) -> str`

**位置**: 行 166

导出审计链为JSON字符串。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `indent` | `int` | 否 | `2` |  |

**返回** `str`

---

#### 类

##### `AuditEntry`
`数据类`

单条审计记录 — 不可篡改链上的一个区块

**属性**

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

**方法**

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

#### 函数

##### `sm3_hash(data: bytes) -> str`

**位置**: 行 66

SM3 国密哈希

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `bytes` | 是 | `-` |  |

**返回** `str`

---

##### `sm4_encrypt(plaintext: bytes, key: bytes) -> bytes`

**位置**: 行 461

SM4 国密对称加密 (ECB模式)

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `plaintext` | `bytes` | 是 | `-` |  |
| `key` | `bytes` | 是 | `-` |  |

**返回** `bytes`

---

##### `sm4_decrypt(ciphertext: bytes, key: bytes) -> bytes`

**位置**: 行 503

SM4 国密对称解密 (ECB模式)

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `ciphertext` | `bytes` | 是 | `-` |  |
| `key` | `bytes` | 是 | `-` |  |

**返回** `bytes`

---

##### `pkcs7_pad(data: bytes, block_size: int = 16) -> bytes`

**位置**: 行 542

PKCS7 填充

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `bytes` | 是 | `-` |  |
| `block_size` | `int` | 否 | `16` |  |

**返回** `bytes`

---

##### `pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes`

**位置**: 行 557

PKCS7 去填充

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `bytes` | 是 | `-` |  |
| `block_size` | `int` | 否 | `16` |  |

**返回** `bytes`

---

##### `generate_sm4_iv() -> bytes`

**位置**: 行 584

生成随机SM4 IV（初始化向量）

**返回** `bytes`

---

##### `sm4_cbc_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes`

**位置**: 行 589

SM4-CBC 国密对称加密

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `plaintext` | `bytes` | 是 | `-` |  |
| `key` | `bytes` | 是 | `-` |  |
| `iv` | `bytes` | 是 | `-` |  |

**返回** `bytes`

---

##### `sm4_cbc_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes`

**位置**: 行 626

SM4-CBC 国密对称解密

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `ciphertext` | `bytes` | 是 | `-` |  |
| `key` | `bytes` | 是 | `-` |  |
| `iv` | `bytes` | 是 | `-` |  |

**返回** `bytes`

---

##### `generate_sm4_key() -> bytes`

**位置**: 行 668

生成随机SM4密钥

**返回** `bytes`

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

#### 函数

##### `generate_sm2_keypair() -> Tuple[bytes, bytes]`

**位置**: 行 223

生成SM2密钥对

**返回** `Tuple[bytes, bytes]`

---

##### `sm2_encrypt(plaintext: bytes, public_key: bytes) -> bytes`

**位置**: 行 254

SM2加密 (C1 || C3 || C2 格式)

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `plaintext` | `bytes` | 是 | `-` |  |
| `public_key` | `bytes` | 是 | `-` |  |

**返回** `bytes`

---

##### `sm2_decrypt(ciphertext: bytes, private_key: bytes) -> bytes`

**位置**: 行 320

SM2解密

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `ciphertext` | `bytes` | 是 | `-` |  |
| `private_key` | `bytes` | 是 | `-` |  |

**返回** `bytes`

---

##### `sm2_sign(data: bytes, private_key: bytes, user_id: bytes = None) -> bytes`

**位置**: 行 388

SM2签名 (GB/T 32918-2016)

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `bytes` | 是 | `-` |  |
| `private_key` | `bytes` | 是 | `-` |  |
| `user_id` | `bytes` | 否 | `None` |  |

**返回** `bytes`

---

##### `sm2_verify(data: bytes, signature: bytes, public_key: bytes, user_id: bytes = None) -> bool`

**位置**: 行 455

SM2验签

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `bytes` | 是 | `-` |  |
| `signature` | `bytes` | 是 | `-` |  |
| `public_key` | `bytes` | 是 | `-` |  |
| `user_id` | `bytes` | 否 | `None` |  |

**返回** `bool`

---

##### `sm2_derive_key(shared_secret: bytes, key_length: int = 32) -> bytes`

**位置**: 行 524

SM2密钥派生函数 (KDF)

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `shared_secret` | `bytes` | 是 | `-` |  |
| `key_length` | `int` | 否 | `32` |  |

**返回** `bytes`

---

##### `sm2_calculate_shared_secret(private_key: bytes, peer_public_key: bytes) -> bytes`

**位置**: 行 551

SM2椭圆曲线Diffie-Hellman密钥交换 - 计算共享秘密

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `private_key` | `bytes` | 是 | `-` |  |
| `peer_public_key` | `bytes` | 是 | `-` |  |

**返回** `bytes`

---

---

## 模型模块

**模块路径**: `govmcp.models`

### `govmcp.models.adapters.baichuan`

govmcp.models.adapters.baichuan — 百川智能适配器

支持 baichuan4, baichuan-7b, baichuan-13b

#### 函数

##### `__init__(config: ModelConfig, api_key: Optional[str] = None, secret_key: Optional[str] = None) -> None`

**位置**: 行 29

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `api_key` | `Optional[str]` | 否 | `None` |  |
| `secret_key` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 43

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 73

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 114

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `BaichuanAdapter`

**基类**: `LLMAdapter`

百川智能大模型适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |
| `secret_key` | `Optional[str]` |

**方法**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.base`

govmcp.models.adapters.base — LLM适配器基类

定义统一的适配器接口，所有厂商适配器都应继承此类。

#### 函数

##### `__init__(config: ModelConfig) -> None`

**位置**: 行 35

初始化适配器

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 51

**装饰器**: abstractmethod

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 69

**装饰器**: abstractmethod

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 87

**装饰器**: abstractmethod

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

##### `format_messages(system: Optional[str] = None, user: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]`

**位置**: 行 104

格式化消息列表

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `system` | `Optional[str]` | 否 | `None` |  |
| `user` | `Optional[str]` | 否 | `None` |  |
| `history` | `Optional[List[Dict[str, str]]]` | 否 | `None` |  |

**返回** `List[Dict[str, str]]`

---

##### `build_request_params(messages: List[Dict[str, str]], ****kwargs) -> Dict[str, Any]`

**位置**: 行 134

构建请求参数

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Dict[str, Any]`

---

##### `supports_streaming() -> bool`

**位置**: 行 177

是否支持流式输出

**返回** `bool`

---

##### `supports_function_call() -> bool`

**位置**: 行 181

是否支持函数调用

**返回** `bool`

---

##### `supports_vision() -> bool`

**位置**: 行 185

是否支持视觉

**返回** `bool`

---

##### `supports_embedding() -> bool`

**位置**: 行 189

是否支持文本嵌入

**返回** `bool`

---

#### 类

##### `LLMAdapter`

**基类**: `ABC`

LLM适配器基类

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |

**方法**

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

#### 函数

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**位置**: 行 29

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `api_key` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 40

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 72

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 115

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `DoubaoAdapter`

**基类**: `LLMAdapter`

字节豆包大模型适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**方法**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.hunyuan`

govmcp.models.adapters.hunyuan — 腾讯混元适配器

支持 hunyuan-lite, hunyuan-pro, hunyuan-standard

#### 函数

##### `__init__(config: ModelConfig, secret_id: Optional[str] = None, secret_key: Optional[str] = None) -> None`

**位置**: 行 29

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `secret_id` | `Optional[str]` | 否 | `None` |  |
| `secret_key` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 36

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 72

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 119

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `HunyuanAdapter`

**基类**: `LLMAdapter`

腾讯混元大模型适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `secret_id` | `Optional[str]` |
| `secret_key` | `Optional[str]` |

**方法**

- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.minimax`

govmcp.models.adapters.minimax — MiniMax适配器

支持 minimax-abab5, minimax-abab6, minimax-chat

#### 函数

##### `__init__(config: ModelConfig, api_key: Optional[str] = None, group_id: Optional[str] = None) -> None`

**位置**: 行 29

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `api_key` | `Optional[str]` | 否 | `None` |  |
| `group_id` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 43

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 77

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 124

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `MinimaxAdapter`

**基类**: `LLMAdapter`

MiniMax大模型适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |
| `group_id` | `Optional[str]` |

**方法**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.moonshot`

govmcp.models.adapters.moonshot — 月之暗面Kimi适配器

支持 kimi-chat, kimi-pro

#### 函数

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**位置**: 行 29

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `api_key` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 40

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 72

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 115

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `MoonshotAdapter`

**基类**: `LLMAdapter`

月之暗面Kimi大模型适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**方法**

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

#### 函数

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**位置**: 行 40

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `api_key` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 53

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 83

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 124

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `OthersAdapter`

**基类**: `LLMAdapter`

其他国产大模型适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**方法**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.pangu`

govmcp.models.adapters.pangu — 华为盘古适配器

支持 pangu-alpha, pangu-chat

#### 函数

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**位置**: 行 29

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `api_key` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 40

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 70

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 111

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `PanguAdapter`

**基类**: `LLMAdapter`

华为盘古大模型适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**方法**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.qwen`

govmcp.models.adapters.qwen — 阿里通义千问适配器

支持 qwen-turbo, qwen-plus, qwen-max, qwen-long, qwen-7b, qwen-14b, qwen-72b

#### 函数

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**位置**: 行 29

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `api_key` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 43

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 73

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 114

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `QwenAdapter`

**基类**: `LLMAdapter`

阿里通义千问适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**方法**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.spark`

govmcp.models.adapters.spark — 讯飞星火适配器

支持 spark-3.5, spark-4.0, spark-lite

#### 函数

##### `__init__(config: ModelConfig, app_id: Optional[str] = None, api_key: Optional[str] = None, api_secret: Optional[str] = None) -> None`

**位置**: 行 34

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `app_id` | `Optional[str]` | 否 | `None` |  |
| `api_key` | `Optional[str]` | 否 | `None` |  |
| `api_secret` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 83

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 131

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 192

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `SparkAdapter`

**基类**: `LLMAdapter`

讯飞星火大模型适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `app_id` | `Optional[str]` |
| `api_key` | `Optional[str]` |
| `api_secret` | `Optional[str]` |

**方法**

- `_generate_auth_url()` - 生成讯飞星火鉴权URL
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量
- `_format_messages()` - 格式化消息为讯飞格式

---

### `govmcp.models.adapters.wenxin`

govmcp.models.adapters.wenxin — 百度文心一言适配器

支持 ernie-4.0, ernie-3.5, ernie-3.0, ernie-bot

#### 函数

##### `__init__(config: ModelConfig, api_key: Optional[str] = None, secret_key: Optional[str] = None) -> None`

**位置**: 行 30

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `api_key` | `Optional[str]` | 否 | `None` |  |
| `secret_key` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 63

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 95

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 137

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `WenxinAdapter`

**基类**: `LLMAdapter`

百度文心一言适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |
| `secret_key` | `Optional[str]` |

**方法**

- `_get_access_token()` - 获取百度access_token
- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.adapters.zhipu`

govmcp.models.adapters.zhipu — 智谱AI GLM适配器

支持 glm-4, glm-4-plus, glm-3-turbo, chatglm-6b, chatglm2-6b, chatglm3-6b

#### 函数

##### `__init__(config: ModelConfig, api_key: Optional[str] = None) -> None`

**位置**: 行 29

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `ModelConfig` | 是 | `-` |  |
| `api_key` | `Optional[str]` | 否 | `None` |  |

**返回** `None`

---

##### `chat(messages: List[Dict[str, str]], ****kwargs) -> str`

**位置**: 行 40

发送对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `str`

---

##### `stream_chat(messages: List[Dict[str, str]], ****kwargs) -> Iterator[str]`

**位置**: 行 72

发送流式对话请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, str]]` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Iterator[str]`

---

##### `get_embedding(text: str, ****kwargs) -> List[float]`

**位置**: 行 115

获取文本嵌入向量

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `text` | `str` | 是 | `-` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `List[float]`

---

#### 类

##### `ZhipuAdapter`

**基类**: `LLMAdapter`

智谱AI GLM适配器

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `ModelConfig` |
| `api_key` | `Optional[str]` |

**方法**

- `_build_headers()` - 构建请求头
- `chat()` - 发送对话请求
- `stream_chat()` - 发送流式对话请求
- `get_embedding()` - 获取文本嵌入向量

---

### `govmcp.models.registry`

govmcp.models.registry — 模型注册表

提供 LLMProvider 枚举、ModelConfig 数据类和 ModelRegistry 类，

用于管理所有国产大模型的注册和查询。

#### 函数

##### `get_default_registry() -> ModelRegistry`

**位置**: 行 907

获取默认模型注册表实例

**返回** `ModelRegistry`

---

##### `register_model(provider: LLMProvider, model_id: str, config: ModelConfig) -> bool`

**位置**: 行 915

全局注册模型

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `provider` | `LLMProvider` | 是 | `-` |  |
| `model_id` | `str` | 是 | `-` |  |
| `config` | `ModelConfig` | 是 | `-` |  |

**返回** `bool`

---

##### `get_model(model_id: str) -> Optional[ModelConfig]`

**位置**: 行 920

全局获取模型配置

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | 是 | `-` |  |

**返回** `Optional[ModelConfig]`

---

##### `list_models(provider: Optional[LLMProvider] = None) -> List[ModelConfig]`

**位置**: 行 925

全局列出模型

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `provider` | `Optional[LLMProvider]` | 否 | `None` |  |

**返回** `List[ModelConfig]`

---

##### `validate_model(model_id: str) -> bool`

**位置**: 行 930

全局验证模型

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | 是 | `-` |  |

**返回** `bool`

---

##### `from_model_id(model_id: str) -> 'LLMProvider'`

**位置**: 行 45

**装饰器**: classmethod

根据模型ID推断provider

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | 是 | `-` |  |

**返回** `'LLMProvider'`

---

##### `adapter_name() -> str`

**位置**: 行 91

**装饰器**: property

获取适配器模块名

**返回** `str`

---

##### `supports_streaming() -> bool`

**位置**: 行 132

是否支持流式输出

**返回** `bool`

---

##### `supports_function_call() -> bool`

**位置**: 行 136

是否支持函数调用

**返回** `bool`

---

##### `supports_vision() -> bool`

**位置**: 行 140

是否支持视觉

**返回** `bool`

---

##### `supports_embedding() -> bool`

**位置**: 行 144

是否支持文本嵌入

**返回** `bool`

---

##### `__init__() -> None`

**位置**: 行 184

**返回** `None`

---

##### `register_model(provider: LLMProvider, model_id: str, config: ModelConfig) -> bool`

**位置**: 行 791

注册一个新模型

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `provider` | `LLMProvider` | 是 | `-` |  |
| `model_id` | `str` | 是 | `-` |  |
| `config` | `ModelConfig` | 是 | `-` |  |

**返回** `bool`

---

##### `get_model(model_id: str) -> Optional[ModelConfig]`

**位置**: 行 808

获取模型配置

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | 是 | `-` |  |

**返回** `Optional[ModelConfig]`

---

##### `list_models(provider: Optional[LLMProvider] = None) -> List[ModelConfig]`

**位置**: 行 820

列出所有模型

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `provider` | `Optional[LLMProvider]` | 否 | `None` |  |

**返回** `List[ModelConfig]`

---

##### `validate_model(model_id: str) -> bool`

**位置**: 行 834

验证模型是否已注册

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | 是 | `-` |  |

**返回** `bool`

---

##### `get_adapter(model_id: str) -> Optional[Any]`

**位置**: 行 846

获取模型的适配器实例

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | 是 | `-` |  |

**返回** `Optional[Any]`

---

##### `count() -> int`

**位置**: 行 883

返回已注册模型数量

**返回** `int`

---

##### `get_providers() -> List[LLMProvider]`

**位置**: 行 887

返回所有已使用的provider列表

**返回** `List[LLMProvider]`

---

##### `clear() -> None`

**位置**: 行 891

清空注册表 (测试用)

**返回** `None`

---

#### 类

##### `LLMProvider`
`枚举`

**基类**: `Enum`

国产大模型厂商枚举

**枚举值**

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

**方法**

- `from_model_id()` - 根据模型ID推断provider
- `adapter_name()` - 获取适配器模块名

---

##### `ModelConfig`
`数据类`

模型配置数据类

**属性**

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

**方法**

- `supports_streaming()` - 是否支持流式输出
- `supports_function_call()` - 是否支持函数调用
- `supports_vision()` - 是否支持视觉
- `supports_embedding()` - 是否支持文本嵌入

---

##### `ModelRegistry`

模型注册表

**属性**

| 名称 | 类型 |
|:---|:---|
| `_instance` | `Optional['ModelRegistry']` |
| `_models` | `Dict[str, ModelConfig]` |
| `_adapters` | `Dict[str, Any]` |

**方法**

- `_register_builtin_models()` - 注册内置的48个国产大模型
- `register_model()` - 注册一个新模型
- `get_model()` - 获取模型配置
- `list_models()` - 列出所有模型
- `validate_model()` - 验证模型是否已注册
- ... (4 more)

---

---

## 协议模块

**模块路径**: `govmcp.protocol`

### `govmcp.protocol.authorization`

govmcp.protocol.authorization — 授权扩展 (MCP 2025.11)

提供 OAuth 2.0 授权流程和细粒度权限控制支持：

- OAuth 2.0 授权码流程

- Authorization Extensions

- 细粒度权限控制

- 令牌管理

#### 函数

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 68

转换为字典

**返回** `Dict[str, Any]`

---

##### `is_valid() -> bool`

**位置**: 行 94

检查是否有效

**返回** `bool`

---

##### `mark_used() -> None`

**位置**: 行 98

标记为已使用

**返回** `None`

---

##### `is_expired() -> float`

**位置**: 行 117

检查是否过期

**返回** `float`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 121

转换为字典

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'TokenInfo'`

**位置**: 行 134

**装饰器**: classmethod

从字典创建

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `'TokenInfo'`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 157

转换为字典

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'Permission'`

**位置**: 行 168

**装饰器**: classmethod

从字典创建

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `'Permission'`

---

##### `is_valid() -> bool`

**位置**: 行 190

检查是否有效

**返回** `bool`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 196

转换为字典

**返回** `Dict[str, Any]`

---

##### `__init__(access_token_ttl: int = 3600, refresh_token_ttl: int = 86400 * 7, authorization_code_ttl: int = 600)`

**位置**: 行 217

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `access_token_ttl` | `int` | 否 | `3600` |  |
| `refresh_token_ttl` | `int` | 否 | `86400 * 7` |  |
| `authorization_code_ttl` | `int` | 否 | `600` |  |

---

##### `register_client(client_id: str, client_secret: Optional[str] = None, client_name: str = '', redirect_uris: Optional[List[str]] = None, allowed_scopes: Optional[Set[str]] = None, grant_types: Optional[Set[GrantType]] = None, metadata: Optional[Dict[str, Any]] = None) -> ClientInfo`

**位置**: 行 238

注册客户端

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | 是 | `-` |  |
| `client_secret` | `Optional[str]` | 否 | `None` |  |
| `client_name` | `str` | 否 | `''` |  |
| `redirect_uris` | `Optional[List[str]]` | 否 | `None` |  |
| `allowed_scopes` | `Optional[Set[str]]` | 否 | `None` |  |
| `grant_types` | `Optional[Set[GrantType]]` | 否 | `None` |  |
| `metadata` | `Optional[Dict[str, Any]]` | 否 | `None` |  |

**返回** `ClientInfo`

---

##### `get_client(client_id: str) -> Optional[ClientInfo]`

**位置**: 行 262

获取客户端信息

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | 是 | `-` |  |

**返回** `Optional[ClientInfo]`

---

##### `validate_client(client_id: str, client_secret: Optional[str] = None) -> bool`

**位置**: 行 267

验证客户端凭证

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | 是 | `-` |  |
| `client_secret` | `Optional[str]` | 否 | `None` |  |

**返回** `bool`

---

##### `create_authorization_url(client_id: str, redirect_uri: str, scope: Optional[str] = None, state: Optional[str] = None, code_challenge: Optional[str] = None, code_challenge_method: Optional[str] = None) -> str`

**位置**: 行 277

创建授权 URL

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | 是 | `-` |  |
| `redirect_uri` | `str` | 是 | `-` |  |
| `scope` | `Optional[str]` | 否 | `None` |  |
| `state` | `Optional[str]` | 否 | `None` |  |
| `code_challenge` | `Optional[str]` | 否 | `None` |  |
| `code_challenge_method` | `Optional[str]` | 否 | `None` |  |

**返回** `str`

---

##### `authorize(code: str, user_id: str) -> bool`

**位置**: 行 341

用户授权确认

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `code` | `str` | 是 | `-` |  |
| `user_id` | `str` | 是 | `-` |  |

**返回** `bool`

---

##### `exchange_code(code: str, client_id: str, client_secret: Optional[str] = None, code_verifier: Optional[str] = None) -> TokenInfo`

**位置**: 行 364

交换授权码获取令牌

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `code` | `str` | 是 | `-` |  |
| `client_id` | `str` | 是 | `-` |  |
| `client_secret` | `Optional[str]` | 否 | `None` |  |
| `code_verifier` | `Optional[str]` | 否 | `None` |  |

**返回** `TokenInfo`

---

##### `refresh_access_token(refresh_token: str, client_id: Optional[str] = None, client_secret: Optional[str] = None, scope: Optional[str] = None) -> TokenInfo`

**位置**: 行 446

刷新访问令牌

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `refresh_token` | `str` | 是 | `-` |  |
| `client_id` | `Optional[str]` | 否 | `None` |  |
| `client_secret` | `Optional[str]` | 否 | `None` |  |
| `scope` | `Optional[str]` | 否 | `None` |  |

**返回** `TokenInfo`

---

##### `validate_token(access_token: str) -> Optional[TokenInfo]`

**位置**: 行 518

验证访问令牌

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `access_token` | `str` | 是 | `-` |  |

**返回** `Optional[TokenInfo]`

---

##### `revoke_token(token: str) -> bool`

**位置**: 行 528

撤销令牌

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `token` | `str` | 是 | `-` |  |

**返回** `bool`

---

##### `add_authorization_hook(hook: Callable[[str, Dict[str, Any]], bool]) -> None`

**位置**: 行 539

添加授权钩子

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `hook` | `Callable[[str, Dict[str, Any]], bool]` | 是 | `-` |  |

**返回** `None`

---

##### `check_permission(token: str, resource: str, action: str) -> bool`

**位置**: 行 546

检查权限

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `token` | `str` | 是 | `-` |  |
| `resource` | `str` | 是 | `-` |  |
| `action` | `str` | 是 | `-` |  |

**返回** `bool`

---

##### `grant_permissions(grant_id: str, permissions: List[Permission]) -> bool`

**位置**: 行 591

授予权限

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `grant_id` | `str` | 是 | `-` |  |
| `permissions` | `List[Permission]` | 是 | `-` |  |

**返回** `bool`

---

##### `revoke_permissions(grant_id: str, resources: Optional[List[str]] = None) -> bool`

**位置**: 行 604

撤销权限

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `grant_id` | `str` | 是 | `-` |  |
| `resources` | `Optional[List[str]]` | 否 | `None` |  |

**返回** `bool`

---

##### `cleanup_expired() -> int`

**位置**: 行 621

清理过期数据

**返回** `int`

---

##### `get_stats() -> Dict[str, Any]`

**位置**: 行 668

获取统计信息

**返回** `Dict[str, Any]`

---

##### `__init__(authorization_manager: AuthorizationManager)`

**位置**: 行 684

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `authorization_manager` | `AuthorizationManager` | 是 | `-` |  |

---

##### `add_policy(policy_id: str, effect: str, principals: List[str], resources: List[str], actions: List[str], conditions: Optional[Dict[str, Any]] = None) -> None`

**位置**: 行 689

添加策略

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `policy_id` | `str` | 是 | `-` |  |
| `effect` | `str` | 是 | `-` |  |
| `principals` | `List[str]` | 是 | `-` |  |
| `resources` | `List[str]` | 是 | `-` |  |
| `actions` | `List[str]` | 是 | `-` |  |
| `conditions` | `Optional[Dict[str, Any]]` | 否 | `None` |  |

**返回** `None`

---

##### `evaluate(principal: str, resource: str, action: str, context: Optional[Dict[str, Any]] = None) -> bool`

**位置**: 行 722

评估权限

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `principal` | `str` | 是 | `-` |  |
| `resource` | `str` | 是 | `-` |  |
| `action` | `str` | 是 | `-` |  |
| `context` | `Optional[Dict[str, Any]]` | 否 | `None` |  |

**返回** `bool`

---

##### `remove_policy(policy_id: str) -> bool`

**位置**: 行 785

移除策略

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `policy_id` | `str` | 是 | `-` |  |

**返回** `bool`

---

##### `get_policies(policy_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]`

**位置**: 行 793

获取策略

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `policy_id` | `Optional[str]` | 否 | `None` |  |

**返回** `Dict[str, List[Dict[str, Any]]]`

---

#### 类

##### `GrantType`
`枚举`

**基类**: `str | Enum`

授权类型

**枚举值**

| 名称 | 值 |
|:---|:---|
| `AUTHORIZATION_CODE` | `'authorization_code'` |
| `CLIENT_CREDENTIALS` | `'client_credentials'` |
| `REFRESH_TOKEN` | `'refresh_token'` |
| `IMPLICIT` | `'implicit'` |

---

##### `TokenType`
`枚举`

**基类**: `str | Enum`

令牌类型

**枚举值**

| 名称 | 值 |
|:---|:---|
| `BEARER` | `'bearer'` |
| `MAC` | `'mac'` |

---

##### `AuthorizationScope`
`枚举`

**基类**: `str | Enum`

授权范围

**枚举值**

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
`数据类`

OAuth 客户端信息

**属性**

| 名称 | 类型 |
|:---|:---|
| `client_id` | `str` |
| `client_secret` | `Optional[str]` |
| `client_name` | `str` |
| `redirect_uris` | `List[str]` |
| `allowed_scopes` | `Set[str]` |
| `grant_types` | `Set[GrantType]` |
| `metadata` | `Dict[str, Any]` |

**方法**

- `to_dict()` - 转换为字典

---

##### `AuthorizationCode`
`数据类`

授权码

**属性**

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

**方法**

- `is_valid()` - 检查是否有效
- `mark_used()` - 标记为已使用

---

##### `TokenInfo`
`数据类`

令牌信息

**属性**

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

**方法**

- `is_expired()` - 检查是否过期
- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `Permission`
`数据类`

权限

**属性**

| 名称 | 类型 |
|:---|:---|
| `resource` | `str` |
| `actions` | `Set[str]` |
| `conditions` | `Optional[Dict[str, Any]]` |

**方法**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `AuthorizationGrant`
`数据类`

授权授予

**属性**

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

**方法**

- `is_valid()` - 检查是否有效
- `to_dict()` - 转换为字典

---

##### `AuthorizationManager`

授权管理器

**属性**

| 名称 | 类型 |
|:---|:---|
| `access_token_ttl` | `int` |
| `refresh_token_ttl` | `int` |
| `authorization_code_ttl` | `int` |

**方法**

- `register_client()` - 注册客户端
- `get_client()` - 获取客户端信息
- `validate_client()` - 验证客户端凭证
- `create_authorization_url()` - 创建授权 URL
- `authorize()` - 用户授权确认
- ... (11 more)

---

##### `FineGrainedPermissionManager`

细粒度权限管理器

**属性**

| 名称 | 类型 |
|:---|:---|
| `authorization_manager` | `AuthorizationManager` |

**方法**

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

#### 函数

##### `create_secure_prompt_request(message: str, resource_uri: Optional[str] = None, timeout: float = 300.0) -> ElicitRequest`

**位置**: 行 563

创建安全提示确认请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `str` | 是 | `-` |  |
| `resource_uri` | `Optional[str]` | 否 | `None` |  |
| `timeout` | `float` | 否 | `300.0` |  |

**返回** `ElicitRequest`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 67

转换为字典

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'ElicitRequest'`

**位置**: 行 83

**装饰器**: classmethod

从字典创建

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `'ElicitRequest'`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 112

转换为字典

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'ElicitResponse'`

**位置**: 行 129

**装饰器**: classmethod

从字典创建

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `'ElicitResponse'`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 163

转换为字典

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'URLElicitation'`

**位置**: 行 182

**装饰器**: classmethod

从字典创建

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `'URLElicitation'`

---

##### `handle_request(request: ElicitRequest) -> ElicitResponse`

**位置**: 行 200

处理交互请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `ElicitRequest` | 是 | `-` |  |

**返回** `ElicitResponse`

---

##### `can_handle(request: ElicitRequest) -> bool`

**位置**: 行 207

检查是否可以处理

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `ElicitRequest` | 是 | `-` |  |

**返回** `bool`

---

##### `__init__(input_func: Optional[Callable[[str], str]] = None)`

**位置**: 行 215

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `input_func` | `Optional[Callable[[str], str]]` | 否 | `None` |  |

---

##### `handle_request(request: ElicitRequest) -> ElicitResponse`

**位置**: 行 218

处理交互请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `ElicitRequest` | 是 | `-` |  |

**返回** `ElicitResponse`

---

##### `__init__()`

**位置**: 行 264

---

##### `add_handler(handler: ElicitationHandler) -> None`

**位置**: 行 272

添加处理器

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `ElicitationHandler` | 是 | `-` |  |

**返回** `None`

---

##### `set_default_handler(handler: ElicitationHandler) -> None`

**位置**: 行 276

设置默认处理器

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `ElicitationHandler` | 是 | `-` |  |

**返回** `None`

---

##### `register_callback(request_id: str, callback: Callable[[ElicitResponse], None]) -> None`

**位置**: 行 280

注册回调

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | 是 | `-` |  |
| `callback` | `Callable[[ElicitResponse], None]` | 是 | `-` |  |

**返回** `None`

---

##### `create_request(message: str, requested_schema: Optional[Dict[str, Any]] = None, elicit_type: Union[ElicitType, str] = ElicitType.REQUEST, timeout: float = 300.0, metadata: Optional[Dict[str, Any]] = None) -> ElicitRequest`

**位置**: 行 288

创建交互请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `str` | 是 | `-` |  |
| `requested_schema` | `Optional[Dict[str, Any]]` | 否 | `None` |  |
| `elicit_type` | `Union[ElicitType, str]` | 否 | `ElicitType.REQUEST` |  |
| `timeout` | `float` | 否 | `300.0` |  |
| `metadata` | `Optional[Dict[str, Any]]` | 否 | `None` |  |

**返回** `ElicitRequest`

---

##### `get_request(request_id: str) -> Optional[ElicitRequest]`

**位置**: 行 325

获取交互请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | 是 | `-` |  |

**返回** `Optional[ElicitRequest]`

---

##### `submit_response(response: ElicitResponse) -> bool`

**位置**: 行 330

提交响应

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `response` | `ElicitResponse` | 是 | `-` |  |

**返回** `bool`

---

##### `accept(request_id: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool`

**位置**: 行 360

接受请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | 是 | `-` |  |
| `value` | `Any` | 是 | `-` |  |
| `metadata` | `Optional[Dict[str, Any]]` | 否 | `None` |  |

**返回** `bool`

---

##### `reject(request_id: str, error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool`

**位置**: 行 375

拒绝请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | 是 | `-` |  |
| `error` | `Optional[str]` | 否 | `None` |  |
| `metadata` | `Optional[Dict[str, Any]]` | 否 | `None` |  |

**返回** `bool`

---

##### `cancel(request_id: str) -> bool`

**位置**: 行 390

取消请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | 是 | `-` |  |

**返回** `bool`

---

##### `expire_requests() -> int`

**位置**: 行 404

使过期的请求过期

**返回** `int`

---

##### `get_pending_requests(limit: int = 100) -> List[ElicitRequest]`

**位置**: 行 431

获取待处理的请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `limit` | `int` | 否 | `100` |  |

**返回** `List[ElicitRequest]`

---

##### `get_response(request_id: str) -> Optional[ElicitResponse]`

**位置**: 行 441

获取响应

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request_id` | `str` | 是 | `-` |  |

**返回** `Optional[ElicitResponse]`

---

##### `get_pending_count() -> int`

**位置**: 行 446

获取待处理请求数量

**返回** `int`

---

##### `create_url_elicitation(url: str, title: str, method: str = 'GET', headers: Optional[Dict[str, str]] = None, body: Optional[str] = None, timeout: float = 300.0, metadata: Optional[Dict[str, Any]] = None) -> URLElicitation`

**位置**: 行 451

创建 URL 交互

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `url` | `str` | 是 | `-` |  |
| `title` | `str` | 是 | `-` |  |
| `method` | `str` | 否 | `'GET'` |  |
| `headers` | `Optional[Dict[str, str]]` | 否 | `None` |  |
| `body` | `Optional[str]` | 否 | `None` |  |
| `timeout` | `float` | 否 | `300.0` |  |
| `metadata` | `Optional[Dict[str, Any]]` | 否 | `None` |  |

**返回** `URLElicitation`

---

##### `create_confirm_request(message: str, title: Optional[str] = None, timeout: float = 300.0) -> ElicitRequest`

**位置**: 行 488

创建确认请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `str` | 是 | `-` |  |
| `title` | `Optional[str]` | 否 | `None` |  |
| `timeout` | `float` | 否 | `300.0` |  |

**返回** `ElicitRequest`

---

##### `create_input_request(message: str, field_name: str, field_type: str = 'string', required: bool = True, timeout: float = 300.0) -> ElicitRequest`

**位置**: 行 506

创建输入请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `str` | 是 | `-` |  |
| `field_name` | `str` | 是 | `-` |  |
| `field_type` | `str` | 否 | `'string'` |  |
| `required` | `bool` | 否 | `True` |  |
| `timeout` | `float` | 否 | `300.0` |  |

**返回** `ElicitRequest`

---

##### `create_select_request(message: str, options: List[str], timeout: float = 300.0) -> ElicitRequest`

**位置**: 行 526

创建选择请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `str` | 是 | `-` |  |
| `options` | `List[str]` | 是 | `-` |  |
| `timeout` | `float` | 否 | `300.0` |  |

**返回** `ElicitRequest`

---

##### `get_stats() -> Dict[str, Any]`

**位置**: 行 546

获取统计信息

**返回** `Dict[str, Any]`

---

#### 类

##### `ElicitType`
`枚举`

**基类**: `str | Enum`

交互类型

**枚举值**

| 名称 | 值 |
|:---|:---|
| `REQUEST` | `'request'` |
| `CONFIRM` | `'confirm'` |
| `INPUT` | `'input'` |
| `SELECT` | `'select'` |
| `URL` | `'url'` |

---

##### `ElicitStatus`
`枚举`

**基类**: `str | Enum`

交互状态

**枚举值**

| 名称 | 值 |
|:---|:---|
| `PENDING` | `'pending'` |
| `ACCEPTED` | `'accepted'` |
| `REJECTED` | `'rejected'` |
| `EXPIRED` | `'expired'` |
| `CANCELED` | `'canceled'` |

---

##### `ElicitRequest`
`数据类`

用户交互请求

**属性**

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

**方法**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `ElicitResponse`
`数据类`

用户交互响应

**属性**

| 名称 | 类型 |
|:---|:---|
| `request_id` | `str` |
| `status` | `Union[ElicitStatus, str]` |
| `value` | `Optional[Any]` |
| `error` | `Optional[str]` |
| `responded_at` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

**方法**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `URLElicitation`
`数据类`

URL Mode Elicitation

**属性**

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

**方法**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `ElicitationHandler`

交互处理器接口

**方法**

- `handle_request()` - 处理交互请求
- `can_handle()` - 检查是否可以处理

---

##### `ConsoleElicitationHandler`

**基类**: `ElicitationHandler`

控制台交互处理器

**属性**

| 名称 | 类型 |
|:---|:---|
| `input_func` | `Optional[Callable[[str], str]]` |

**方法**

- `handle_request()` - 处理交互请求
- `_get_confirmation()` - 获取确认
- `_get_input()` - 获取输入

---

##### `ElicitationManager`

交互管理器

**方法**

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

#### 函数

##### `to_web_response() -> web.Response`

**位置**: 行 75

转换为 aiohttp Response

**返回** `web.Response`

---

##### `__init__(host: str = '0.0.0.0', port: int = 8080, path: str = '/mcp', sse_path: str = '/mcp/sse', auth_token: Optional[str] = None, crypto_enabled: bool = False, sm4_key: Optional[bytes] = None, max_message_size: int = 10 * 1024 * 1024, request_timeout: float = 60.0, enable_cors: bool = True, cors_origins: Optional[List[str]] = None, enable_sse: bool = True, sse_heartbeat: float = 15.0, log_level: int = logging.INFO) -> None`

**位置**: 行 115

初始化 HTTP 服务器。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `host` | `str` | 否 | `'0.0.0.0'` |  |
| `port` | `int` | 否 | `8080` |  |
| `path` | `str` | 否 | `'/mcp'` |  |
| `sse_path` | `str` | 否 | `'/mcp/sse'` |  |
| `auth_token` | `Optional[str]` | 否 | `None` |  |
| `crypto_enabled` | `bool` | 否 | `False` |  |
| `sm4_key` | `Optional[bytes]` | 否 | `None` |  |
| `max_message_size` | `int` | 否 | `10 * 1024 * 1024` |  |
| `request_timeout` | `float` | 否 | `60.0` |  |
| `enable_cors` | `bool` | 否 | `True` |  |
| `cors_origins` | `Optional[List[str]]` | 否 | `None` |  |
| `enable_sse` | `bool` | 否 | `True` |  |
| `sse_heartbeat` | `float` | 否 | `15.0` |  |
| `log_level` | `int` | 否 | `logging.INFO` |  |

**返回** `None`

---

##### `set_message_handler(handler: Callable[[HTTPRequest], Any]) -> None`

**位置**: 行 179

设置消息处理器。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `Callable[[HTTPRequest], Any]` | 是 | `-` |  |

**返回** `None`

---

##### `async start(handler: Optional[Callable[[HTTPRequest], Any]] = None) -> None`

**位置**: 行 188

启动 HTTP 服务器。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `Optional[Callable[[HTTPRequest], Any]]` | 否 | `None` |  |

**返回** `None`

---

##### `async stop() -> None`

**位置**: 行 219

停止 HTTP 服务器

**返回** `None`

---

##### `async broadcast_sse(event: str, data: Any) -> int`

**位置**: 行 242

广播 SSE 事件给所有订阅者。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `event` | `str` | 是 | `-` |  |
| `data` | `Any` | 是 | `-` |  |

**返回** `int`

---

##### `get_sse_subscriber_count() -> int`

**位置**: 行 262

获取 SSE 订阅者数量

**返回** `int`

---

##### `async handle_message(request: HTTPRequest) -> Optional[Dict[str, Any]]`

**位置**: 行 502

默认消息处理器（需要外部设置实际的处理器）。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `HTTPRequest` | 是 | `-` |  |

**返回** `Optional[Dict[str, Any]]`

---

##### `create_stdio_compatible(name: str, version: str, handler: Callable[[HTTPRequest], Any], crypto_enabled: bool = False) -> HTTPServer`

**位置**: 行 515

**装饰器**: staticmethod

创建与 stdio 服务器兼容的 HTTP 服务器

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `version` | `str` | 是 | `-` |  |
| `handler` | `Callable[[HTTPRequest], Any]` | 是 | `-` |  |
| `crypto_enabled` | `bool` | 否 | `False` |  |

**返回** `HTTPServer`

---

##### `create_secure(name: str, version: str, handler: Callable[[HTTPRequest], Any], auth_token: str) -> HTTPServer`

**位置**: 行 531

**装饰器**: staticmethod

创建带认证的 HTTP 服务器

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `version` | `str` | 是 | `-` |  |
| `handler` | `Callable[[HTTPRequest], Any]` | 是 | `-` |  |
| `auth_token` | `str` | 是 | `-` |  |

**返回** `HTTPServer`

---

##### `async heartbeat()`

**位置**: 行 405

---

#### 类

##### `HTTPMethod`
`枚举`

**基类**: `Enum`

HTTP 方法

**枚举值**

| 名称 | 值 |
|:---|:---|
| `POST` | `'POST'` |
| `GET` | `'GET'` |

---

##### `HTTPRequest`
`数据类`

HTTP 请求封装

**属性**

| 名称 | 类型 |
|:---|:---|
| `method` | `str` |
| `path` | `str` |
| `headers` | `Dict[str, str]` |
| `body` | `Optional[Dict[str, Any]]` |
| `query_params` | `Dict[str, str]` |

---

##### `HTTPResponse`
`数据类`

HTTP 响应封装

**属性**

| 名称 | 类型 |
|:---|:---|
| `status` | `int` |
| `headers` | `Dict[str, str]` |
| `body` | `Optional[Any]` |

**方法**

- `to_web_response()` - 转换为 aiohttp Response

---

##### `HTTPServer`

HTTP/SSE MCP 服务器

**属性**

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

**方法**

- `set_message_handler()` - 设置消息处理器。
- `get_sse_subscriber_count()` - 获取 SSE 订阅者数量
- `_setup_routes()` - 设置路由
- `_setup_middleware()` - 设置中间件
- `_check_auth()` - 检查认证
- ... (3 more)

---

##### `HTTPServerFactory`

HTTP 服务器工厂

**方法**

- `create_stdio_compatible()` - 创建与 stdio 服务器兼容的 HTTP 服务器
- `create_secure()` - 创建带认证的 HTTP 服务器

---

### `govmcp.protocol.sampling`

govmcp.protocol.sampling — 异步采样支持 (MCP 2025.11)

提供 LLM 采样能力，支持异步消息生成、采样参数配置和采样策略。

#### 函数

##### `create_sampling_request(messages: List[Dict[str, Any]], temperature: float = 0.7, max_tokens: int = 4096, ****kwargs) -> SamplingCreateMessageRequest`

**位置**: 行 515

创建采样请求的便捷函数

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[Dict[str, Any]]` | 是 | `-` |  |
| `temperature` | `float` | 否 | `0.7` |  |
| `max_tokens` | `int` | 否 | `4096` |  |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `SamplingCreateMessageRequest`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 49

转换为字典

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'SamplingMessage'`

**位置**: 行 61

**装饰器**: classmethod

从字典创建

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `'SamplingMessage'`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 92

转换为字典

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'SamplingParameters'`

**位置**: 行 114

**装饰器**: classmethod

从字典创建

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `'SamplingParameters'`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 150

转换为字典

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'SamplingCreateMessageRequest'`

**位置**: 行 170

**装饰器**: classmethod

从字典创建

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `'SamplingCreateMessageRequest'`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 201

转换为字典

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'SamplingResponse'`

**位置**: 行 222

**装饰器**: classmethod

从字典创建

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `'SamplingResponse'`

---

##### `sample(messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

**位置**: 行 240

同步采样

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[SamplingMessage]` | 是 | `-` |  |
| `parameters` | `SamplingParameters` | 是 | `-` |  |

**返回** `SamplingResponse`

---

##### `async sample_async(messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

**位置**: 行 248

异步采样

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[SamplingMessage]` | 是 | `-` |  |
| `parameters` | `SamplingParameters` | 是 | `-` |  |

**返回** `SamplingResponse`

---

##### `__init__()`

**位置**: 行 264

---

##### `register_provider(model_name: str, provider: SamplingProvider) -> None`

**位置**: 行 270

注册采样提供者

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_name` | `str` | 是 | `-` |  |
| `provider` | `SamplingProvider` | 是 | `-` |  |

**返回** `None`

---

##### `set_default_model(model_name: str) -> None`

**位置**: 行 278

设置默认模型

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_name` | `str` | 是 | `-` |  |

**返回** `None`

---

##### `add_hook(hook: Callable[[str, Any], None]) -> None`

**位置**: 行 282

添加采样钩子

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `hook` | `Callable[[str, Any], None]` | 是 | `-` |  |

**返回** `None`

---

##### `remove_hook(hook: Callable[[str, Any], None]) -> None`

**位置**: 行 286

移除采样钩子

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `hook` | `Callable[[str, Any], None]` | 是 | `-` |  |

**返回** `None`

---

##### `create_message(request: SamplingCreateMessageRequest) -> SamplingResponse`

**位置**: 行 299

创建采样消息（同步）

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `SamplingCreateMessageRequest` | 是 | `-` |  |

**返回** `SamplingResponse`

---

##### `async create_message_async(request: SamplingCreateMessageRequest) -> SamplingResponse`

**位置**: 行 365

创建采样消息（异步）

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `SamplingCreateMessageRequest` | 是 | `-` |  |

**返回** `SamplingResponse`

---

##### `get_message_history(limit: Optional[int] = None) -> List[SamplingMessage]`

**位置**: 行 446

获取消息历史

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `limit` | `Optional[int]` | 否 | `None` |  |

**返回** `List[SamplingMessage]`

---

##### `clear_history() -> None`

**位置**: 行 455

清空消息历史

**返回** `None`

---

##### `get_stats() -> Dict[str, Any]`

**位置**: 行 459

获取采样统计

**返回** `Dict[str, Any]`

---

##### `__init__(model_id: str)`

**位置**: 行 477

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_id` | `str` | 是 | `-` |  |

---

##### `sample(messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

**位置**: 行 480

执行采样

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[SamplingMessage]` | 是 | `-` |  |
| `parameters` | `SamplingParameters` | 是 | `-` |  |

**返回** `SamplingResponse`

---

##### `async sample_async(messages: List[SamplingMessage], parameters: SamplingParameters) -> SamplingResponse`

**位置**: 行 497

异步执行采样

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `messages` | `List[SamplingMessage]` | 是 | `-` |  |
| `parameters` | `SamplingParameters` | 是 | `-` |  |

**返回** `SamplingResponse`

---

#### 类

##### `Role`
`枚举`

**基类**: `str | Enum`

消息角色

**枚举值**

| 名称 | 值 |
|:---|:---|
| `USER` | `'user'` |
| `ASSISTANT` | `'assistant'` |
| `SYSTEM` | `'system'` |

---

##### `SamplingMessageRole`
`枚举`

**基类**: `str | Enum`

采样消息角色 (MCP 2025.11)

**枚举值**

| 名称 | 值 |
|:---|:---|
| `USER` | `'user'` |
| `ASSISTANT` | `'assistant'` |
| `SYSTEM` | `'system'` |

---

##### `SamplingMessage`
`数据类`

采样消息

**属性**

| 名称 | 类型 |
|:---|:---|
| `role` | `Union[Role, SamplingMessageRole, str]` |
| `content` | `str` |
| `timestamp` | `Optional[float]` |
| `metadata` | `Dict[str, Any]` |

**方法**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `SamplingParameters`
`数据类`

采样参数

**属性**

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

**方法**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `SamplingCreateMessageRequest`
`数据类`

采样创建消息请求

**属性**

| 名称 | 类型 |
|:---|:---|
| `messages` | `List[SamplingMessage]` |
| `system_prompt` | `Optional[str]` |
| `temperature` | `float` |
| `max_tokens` | `int` |
| `stop_sequences` | `Optional[List[str]]` |
| `include_context` | `Optional[str]` |
| `thinking` | `Optional[Dict[str, Any]]` |

**方法**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `SamplingResponse`
`数据类`

采样响应

**属性**

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

**方法**

- `to_dict()` - 转换为字典
- `from_dict()` - 从字典创建

---

##### `SamplingProvider`

采样提供者接口

**方法**

- `sample()` - 同步采样

---

##### `SamplingManager`

采样管理器

**方法**

- `register_provider()` - 注册采样提供者
- `set_default_model()` - 设置默认模型
- `add_hook()` - 添加采样钩子
- `remove_hook()` - 移除采样钩子
- `_notify_hooks()` - 通知钩子
- ... (5 more)

---

##### `EmbeddedSamplingProvider`

**基类**: `SamplingProvider`

嵌入式采样提供者

**属性**

| 名称 | 类型 |
|:---|:---|
| `model_id` | `str` |

**方法**

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

#### 函数

##### `__init__(name: str, version: str, crypto_enabled: bool = False, sm4_key: Optional[bytes] = None) -> None`

**位置**: 行 189

初始化 GovMCPServer。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `version` | `str` | 是 | `-` |  |
| `crypto_enabled` | `bool` | 否 | `False` |  |
| `sm4_key` | `Optional[bytes]` | 否 | `None` |  |

**返回** `None`

---

##### `register_tool(name: str, description: str, input_schema: Dict[str, Any], handler: Callable[..., Any]) -> None`

**位置**: 行 239

注册一个工具。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `description` | `str` | 是 | `-` |  |
| `input_schema` | `Dict[str, Any]` | 是 | `-` |  |
| `handler` | `Callable[..., Any]` | 是 | `-` |  |

**返回** `None`

---

##### `register_resource(uri: str, name: str, description: str, mime_type: str, handler: Callable[[str], Any]) -> None`

**位置**: 行 254

注册一个资源。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `uri` | `str` | 是 | `-` |  |
| `name` | `str` | 是 | `-` |  |
| `description` | `str` | 是 | `-` |  |
| `mime_type` | `str` | 是 | `-` |  |
| `handler` | `Callable[[str], Any]` | 是 | `-` |  |

**返回** `None`

---

##### `register_prompt(name: str, description: str, arguments: List[Dict[str, Any]], handler: Callable[..., Any]) -> None`

**位置**: 行 271

注册一个提示模板。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `description` | `str` | 是 | `-` |  |
| `arguments` | `List[Dict[str, Any]]` | 是 | `-` |  |
| `handler` | `Callable[..., Any]` | 是 | `-` |  |

**返回** `None`

---

##### `tool(name: str = None, description: str = , input_schema: Dict[str, Any])`

**位置**: 行 286

工具注册装饰器。@server.tool(...)

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 否 | `None` |  |
| `description` | `str` | 否 | `-` |  |
| `input_schema` | `Dict[str, Any]` | 否 | `-` |  |

---

##### `resource(uri: str = None, name: str = , description: str = , mime_type: str = text/plain)`

**位置**: 行 303

资源注册装饰器。@server.resource(...)

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `uri` | `str` | 否 | `None` |  |
| `name` | `str` | 否 | `-` |  |
| `description` | `str` | 否 | `-` |  |
| `mime_type` | `str` | 否 | `text/plain` |  |

---

##### `prompt(name: str = None, description: str = , arguments: List[Dict[str, Any]])`

**位置**: 行 320

提示模板注册装饰器。@server.prompt(...)

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 否 | `None` |  |
| `description` | `str` | 否 | `-` |  |
| `arguments` | `List[Dict[str, Any]]` | 否 | `-` |  |

---

##### `register_model(model_name: str) -> None`

**位置**: 行 336

注册一个额外的信创模型

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `model_name` | `str` | 是 | `-` |  |

**返回** `None`

---

##### `set_approval_handler(handler: Callable[[str, Dict[str, Any]], bool]) -> None`

**位置**: 行 341

设置审批处理器。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `Callable[[str, Dict[str, Any]], bool]` | 是 | `-` |  |

**返回** `None`

---

##### `run() -> None`

**位置**: 行 734

启动 stdio 消息循环。

**返回** `None`

---

##### `async run_websocket(host: str = '0.0.0.0', port: int = 8080, path: str = '/mcp', auth_token: Optional[str] = None, heartbeat_interval: float = 30.0) -> None`

**位置**: 行 811

启动 WebSocket 服务器。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `host` | `str` | 否 | `'0.0.0.0'` |  |
| `port` | `int` | 否 | `8080` |  |
| `path` | `str` | 否 | `'/mcp'` |  |
| `auth_token` | `Optional[str]` | 否 | `None` |  |
| `heartbeat_interval` | `float` | 否 | `30.0` |  |

**返回** `None`

---

##### `async run_http(host: str = '0.0.0.0', port: int = 8080, path: str = '/mcp', sse_path: str = '/mcp/sse', auth_token: Optional[str] = None, enable_sse: bool = True, sse_heartbeat: float = 15.0) -> None`

**位置**: 行 855

启动 HTTP/SSE 服务器。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `host` | `str` | 否 | `'0.0.0.0'` |  |
| `port` | `int` | 否 | `8080` |  |
| `path` | `str` | 否 | `'/mcp'` |  |
| `sse_path` | `str` | 否 | `'/mcp/sse'` |  |
| `auth_token` | `Optional[str]` | 否 | `None` |  |
| `enable_sse` | `bool` | 否 | `True` |  |
| `sse_heartbeat` | `float` | 否 | `15.0` |  |

**返回** `None`

---

##### `get_transport_info() -> Dict[str, Any]`

**位置**: 行 916

获取传输层信息

**返回** `Dict[str, Any]`

---

##### `decorator(func: Any)`

**位置**: 行 295

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `func` | `Any` | 是 | `-` |  |

---

##### `decorator(func: Any)`

**位置**: 行 313

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `func` | `Any` | 是 | `-` |  |

---

##### `decorator(func: Any)`

**位置**: 行 329

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `func` | `Any` | 是 | `-` |  |

---

##### `async handler(client_id: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]`

**位置**: 行 842

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | 是 | `-` |  |
| `message` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `Optional[Dict[str, Any]]`

---

##### `async handler(request: HTTPRequest) -> HTTPResponse`

**位置**: 行 892

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `request` | `HTTPRequest` | 是 | `-` |  |

**返回** `HTTPResponse`

---

#### 类

##### `GovMCPServer`

GovMCPServer — 国产信创 MCP 协议服务器

**属性**

| 名称 | 类型 |
|:---|:---|
| `name` | `str` |
| `version` | `str` |
| `crypto_enabled` | `bool` |
| `sm4_key` | `Optional[bytes]` |

**方法**

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

#### 函数

##### `create_sse_response(task_manager: TaskManager, task_ids: Optional[List[str]] = None, all_tasks: bool = False) -> Dict[str, Any]`

**位置**: 行 616

创建 SSE 响应

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_manager` | `TaskManager` | 是 | `-` |  |
| `task_ids` | `Optional[List[str]]` | 否 | `None` |  |
| `all_tasks` | `bool` | 否 | `False` |  |

**返回** `Dict[str, Any]`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 61

转换为字典格式

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> 'TaskInfo'`

**位置**: 行 85

**装饰器**: classmethod

从字典创建

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `'TaskInfo'`

---

##### `__init__(task_ids: Optional[Set[str]] = None)`

**位置**: 行 109

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_ids` | `Optional[Set[str]]` | 否 | `None` |  |

---

##### `async send(event: Dict[str, Any]) -> None`

**位置**: 行 114

发送事件到订阅者

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `event` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `None`

---

##### `close() -> None`

**位置**: 行 120

关闭订阅

**返回** `None`

---

##### `async events() -> AsyncIterator[Dict[str, Any]]`

**位置**: 行 130

异步事件迭代器

**返回** `AsyncIterator[Dict[str, Any]]`

---

##### `__init__(default_timeout: float = 300.0)`

**位置**: 行 151

初始化任务管理器

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `default_timeout` | `float` | 否 | `300.0` |  |

---

##### `register_tool(name: str, handler: Callable[..., Any]) -> None`

**位置**: 行 166

注册工具处理器

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `handler` | `Callable[..., Any]` | 是 | `-` |  |

**返回** `None`

---

##### `set_executor(loop: asyncio.AbstractEventLoop) -> None`

**位置**: 行 170

设置事件循环

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `loop` | `asyncio.AbstractEventLoop` | 是 | `-` |  |

**返回** `None`

---

##### `create_task(tool_name: str, arguments: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> str`

**位置**: 行 178

创建异步任务

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `tool_name` | `str` | 是 | `-` |  |
| `arguments` | `Optional[Dict[str, Any]]` | 否 | `None` |  |
| `timeout` | `Optional[float]` | 否 | `None` |  |
| `metadata` | `Optional[Dict[str, Any]]` | 否 | `None` |  |

**返回** `str`

---

##### `execute_task_sync(tool_name: str, arguments: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> str`

**位置**: 行 276

同步执行任务（创建后立即执行）

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `tool_name` | `str` | 是 | `-` |  |
| `arguments` | `Optional[Dict[str, Any]]` | 否 | `None` |  |
| `timeout` | `Optional[float]` | 否 | `None` |  |

**返回** `str`

---

##### `get_task_status(task_id: str) -> TaskStatus`

**位置**: 行 331

获取任务状态

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `str` | 是 | `-` |  |

**返回** `TaskStatus`

---

##### `get_task_info(task_id: str) -> TaskInfo`

**位置**: 行 350

获取完整任务信息

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `str` | 是 | `-` |  |

**返回** `TaskInfo`

---

##### `get_task_result(task_id: str) -> Any`

**位置**: 行 369

获取任务结果

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `str` | 是 | `-` |  |

**返回** `Any`

---

##### `cancel_task(task_id: str) -> bool`

**位置**: 行 396

取消任务

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `str` | 是 | `-` |  |

**返回** `bool`

---

##### `list_tasks(status: Optional[TaskStatus] = None, limit: int = 100, offset: int = 0) -> List[TaskInfo]`

**位置**: 行 424

列出任务

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `status` | `Optional[TaskStatus]` | 否 | `None` |  |
| `limit` | `int` | 否 | `100` |  |
| `offset` | `int` | 否 | `0` |  |

**返回** `List[TaskInfo]`

---

##### `cleanup_completed_tasks(max_age: float = 3600.0) -> int`

**位置**: 行 451

清理已完成任务

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `max_age` | `float` | 否 | `3600.0` |  |

**返回** `int`

---

##### `subscribe(task_id: Optional[str] = None, task_ids: Optional[Set[str]] = None) -> TaskSubscriber`

**位置**: 行 482

订阅任务更新

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `Optional[str]` | 否 | `None` |  |
| `task_ids` | `Optional[Set[str]]` | 否 | `None` |  |

**返回** `TaskSubscriber`

---

##### `unsubscribe(subscriber: TaskSubscriber) -> None`

**位置**: 行 512

取消订阅

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `subscriber` | `TaskSubscriber` | 是 | `-` |  |

**返回** `None`

---

##### `update_progress(task_id: str, progress: float) -> bool`

**位置**: 行 547

更新任务进度

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_id` | `str` | 是 | `-` |  |
| `progress` | `float` | 是 | `-` |  |

**返回** `bool`

---

##### `get_task_stats() -> Dict[str, Any]`

**位置**: 行 567

获取任务统计信息

**返回** `Dict[str, Any]`

---

##### `__init__(task_manager: TaskManager)`

**位置**: 行 589

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_manager` | `TaskManager` | 是 | `-` |  |

---

##### `async stream_events(task_ids: Optional[List[str]] = None, all_tasks: bool = False) -> AsyncIterator[str]`

**位置**: 行 592

生成 SSE 事件流

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `task_ids` | `Optional[List[str]]` | 否 | `None` |  |
| `all_tasks` | `bool` | 否 | `False` |  |

**返回** `AsyncIterator[str]`

---

#### 类

##### `TaskStatus`
`枚举`

**基类**: `str | Enum`

任务状态枚举

**枚举值**

| 名称 | 值 |
|:---|:---|
| `PENDING` | `'pending'` |
| `WORKING` | `'working'` |
| `COMPLETED` | `'completed'` |
| `FAILED` | `'failed'` |
| `CANCELED` | `'canceled'` |

---

##### `TaskNotFoundError`

**基类**: `Exception`

任务不存在异常

---

##### `TaskCancelError`

**基类**: `Exception`

任务取消失败异常

---

##### `TaskInfo`
`数据类`

任务信息数据类

**属性**

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

**方法**

- `to_dict()` - 转换为字典格式
- `from_dict()` - 从字典创建

---

##### `TaskSubscriber`

任务订阅者（用于 SSE）

**属性**

| 名称 | 类型 |
|:---|:---|
| `task_ids` | `Optional[Set[str]]` |

**方法**

- `close()` - 关闭订阅

---

##### `TaskManager`

异步任务管理器

**属性**

| 名称 | 类型 |
|:---|:---|
| `default_timeout` | `float` |

**方法**

- `register_tool()` - 注册工具处理器
- `set_executor()` - 设置事件循环
- `_generate_task_id()` - 生成唯一任务ID
- `create_task()` - 创建异步任务
- `execute_task_sync()` - 同步执行任务（创建后立即执行）
- ... (11 more)

---

##### `SSEHandler`

SSE 事件处理器

**属性**

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

#### 函数

##### `__init__(host: str = '0.0.0.0', port: int = 8080, path: str = '/mcp', auth_token: Optional[str] = None, crypto_enabled: bool = False, sm4_key: Optional[bytes] = None, heartbeat_interval: float = 30.0, heartbeat_timeout: float = 60.0, max_message_size: int = 10 * 1024 * 1024, enable_cors: bool = False, cors_origins: Optional[List[str]] = None, log_level: int = logging.INFO) -> None`

**位置**: 行 92

初始化 WebSocket 服务器。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `host` | `str` | 否 | `'0.0.0.0'` |  |
| `port` | `int` | 否 | `8080` |  |
| `path` | `str` | 否 | `'/mcp'` |  |
| `auth_token` | `Optional[str]` | 否 | `None` |  |
| `crypto_enabled` | `bool` | 否 | `False` |  |
| `sm4_key` | `Optional[bytes]` | 否 | `None` |  |
| `heartbeat_interval` | `float` | 否 | `30.0` |  |
| `heartbeat_timeout` | `float` | 否 | `60.0` |  |
| `max_message_size` | `int` | 否 | `10 * 1024 * 1024` |  |
| `enable_cors` | `bool` | 否 | `False` |  |
| `cors_origins` | `Optional[List[str]]` | 否 | `None` |  |
| `log_level` | `int` | 否 | `logging.INFO` |  |

**返回** `None`

---

##### `set_message_handler(handler: Callable[[str, Dict[str, Any]], Any]) -> None`

**位置**: 行 149

设置消息处理器。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `Callable[[str, Dict[str, Any]], Any]` | 是 | `-` |  |

**返回** `None`

---

##### `async start(handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None) -> None`

**位置**: 行 158

启动 WebSocket 服务器。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `handler` | `Optional[Callable[[str, Dict[str, Any]], Any]]` | 否 | `None` |  |

**返回** `None`

---

##### `async stop() -> None`

**位置**: 行 186

停止 WebSocket 服务器

**返回** `None`

---

##### `async broadcast(message: Dict[str, Any]) -> int`

**位置**: 行 211

广播消息给所有已连接的客户端。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `int`

---

##### `get_client_count() -> int`

**位置**: 行 232

获取当前连接数

**返回** `int`

---

##### `get_authenticated_count() -> int`

**位置**: 行 236

获取已认证连接数

**返回** `int`

---

##### `async disconnect_client(client_id: str) -> bool`

**位置**: 行 240

断开指定客户端。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | 是 | `-` |  |

**返回** `bool`

---

##### `async handle_message(client_id: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]`

**位置**: 行 501

默认消息处理器（需要外部设置实际的处理器）。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `client_id` | `str` | 是 | `-` |  |
| `message` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `Optional[Dict[str, Any]]`

---

##### `create_stdio_compatible(name: str, version: str, handler: Callable[[str, Dict[str, Any]], Any], crypto_enabled: bool = False) -> WebSocketServer`

**位置**: 行 516

**装饰器**: staticmethod

创建与 stdio 服务器兼容的 WebSocket 服务器

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `version` | `str` | 是 | `-` |  |
| `handler` | `Callable[[str, Dict[str, Any]], Any]` | 是 | `-` |  |
| `crypto_enabled` | `bool` | 否 | `False` |  |

**返回** `WebSocketServer`

---

##### `create_secure(name: str, version: str, handler: Callable[[str, Dict[str, Any]], Any], auth_token: str) -> WebSocketServer`

**位置**: 行 532

**装饰器**: staticmethod

创建带认证的 WebSocket 服务器

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `version` | `str` | 是 | `-` |  |
| `handler` | `Callable[[str, Dict[str, Any]], Any]` | 是 | `-` |  |
| `auth_token` | `str` | 是 | `-` |  |

**返回** `WebSocketServer`

---

#### 类

##### `ConnectionState`
`枚举`

**基类**: `Enum`

连接状态

**枚举值**

| 名称 | 值 |
|:---|:---|
| `CONNECTING` | `'connecting'` |
| `AUTHENTICATING` | `'authenticating'` |
| `AUTHENTICATED` | `'authenticated'` |
| `CLOSED` | `'closed'` |

---

##### `ClientConnection`
`数据类`

客户端连接信息

**属性**

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

**属性**

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

**方法**

- `set_message_handler()` - 设置消息处理器。
- `get_client_count()` - 获取当前连接数
- `get_authenticated_count()` - 获取已认证连接数
- `_validate_sm3()` - 验证 SM3 完整性

---

##### `WebSocketServerFactory`

WebSocket 服务器工厂

**方法**

- `create_stdio_compatible()` - 创建与 stdio 服务器兼容的 WebSocket 服务器
- `create_secure()` - 创建带认证的 WebSocket 服务器

---

---

## 服务器模块

**模块路径**: `govmcp.server`

### `govmcp.server.approval`

审批工作流模块 — 多级审批链、超时自动拒绝、审计记录关联。

设计原则:

- 多级审批链：按 approvers 顺序逐级审批

- 超时控制：全局超时，到期后根据 auto_approve_on_timeout 决定行为

- 审计关联：可关联 AuditChain 实例，审批动作自动写入审计记录

- 不可逆：approve/reject/skip 均为单向操作，已完成的步骤不可回退

#### 函数

##### `create_single_approval(approver: str, timeout: float = 300) -> ApprovalFlow`

**位置**: 行 361

创建单级审批流。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approver` | `str` | 是 | `-` |  |
| `timeout` | `float` | 否 | `300` |  |

**返回** `ApprovalFlow`

---

##### `create_multi_approval(approvers: List[str], timeout: float = 300) -> ApprovalFlow`

**位置**: 行 375

创建多级审批流。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approvers` | `List[str]` | 是 | `-` |  |
| `timeout` | `float` | 否 | `300` |  |

**返回** `ApprovalFlow`

---

##### `to_dict() -> dict`

**位置**: 行 37

序列化为字典

**返回** `dict`

---

##### `__init__(approvers: List[str], timeout: float = 300, auto_approve_on_timeout: bool = False, audit_chain: Any = None)`

**位置**: 行 74

初始化审批流。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approvers` | `List[str]` | 是 | `-` |  |
| `timeout` | `float` | 否 | `300` |  |
| `auto_approve_on_timeout` | `bool` | 否 | `False` |  |
| `audit_chain` | `Any` | 否 | `None` |  |

---

##### `approve(approver: str, comment: str = '') -> ApprovalStatus`

**位置**: 行 188

当前级别审批通过。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approver` | `str` | 是 | `-` |  |
| `comment` | `str` | 否 | `''` |  |

**返回** `ApprovalStatus`

---

##### `reject(approver: str, comment: str = '') -> ApprovalStatus`

**位置**: 行 224

当前级别审批拒绝。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approver` | `str` | 是 | `-` |  |
| `comment` | `str` | 否 | `''` |  |

**返回** `ApprovalStatus`

---

##### `skip(comment: str = '') -> ApprovalStatus`

**位置**: 行 257

跳过当前审批级别。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `comment` | `str` | 否 | `''` |  |

**返回** `ApprovalStatus`

---

##### `is_complete() -> bool`

**位置**: 行 290

审批流程是否已完成（无论通过与否）。

**返回** `bool`

---

##### `is_approved() -> bool`

**位置**: 行 303

审批是否全部通过。

**返回** `bool`

---

##### `result() -> ApprovalStatus`

**位置**: 行 316

获取审批流程的最终状态。

**返回** `ApprovalStatus`

---

##### `to_dict_list() -> List[dict]`

**位置**: 行 340

将所有审批步骤序列化为字典列表。

**返回** `List[dict]`

---

#### 类

##### `ApprovalStatus`
`枚举`

**基类**: `Enum`

审批状态枚举

**枚举值**

| 名称 | 值 |
|:---|:---|
| `PENDING` | `'pending'` |
| `APPROVED` | `'approved'` |
| `REJECTED` | `'rejected'` |
| `TIMEOUT` | `'timeout'` |
| `SKIPPED` | `'skipped'` |

---

##### `ApprovalStep`
`数据类`

单个审批步骤的数据记录

**属性**

| 名称 | 类型 |
|:---|:---|
| `level` | `int` |
| `approver` | `str` |
| `status` | `ApprovalStatus` |
| `timestamp` | `float` |
| `comment` | `str` |

**方法**

- `to_dict()` - 序列化为字典

---

##### `ApprovalFlow`

多级审批工作流。

**属性**

| 名称 | 类型 |
|:---|:---|
| `approvers` | `List[str]` |
| `timeout` | `float` |
| `auto_approve_on_timeout` | `bool` |
| `audit_chain` | `Any` |

**方法**

- `_elapsed()` - 已流逝时间（秒）
- `_is_timed_out()` - 检查是否已超时
- `_current_step()` - 获取当前待审批的步骤，若已完成则返回 None
- `_handle_timeout()` - 处理超时情况。
- `_finalize_step()` - 完成当前步骤：推进 current_level，检查是否全部完成。
- ... (8 more)

---

---

## 工具模块

**模块路径**: `govmcp.tools`

### `govmcp.tools.government.approval_workflow`

govmcp.tools.government.approval_workflow — 审批工作流工具模块

提供审批流程发起、进度查询、意见提交、加签改签、会签委托等审批工作流服务的工具函数。

#### 函数

##### `initiate_approval_workflow(workflow_name: str, applicant_name: str, applicant_department: str, workflow_type: str, business_data: Dict[str, Any]) -> Dict[str, Any]`

**位置**: 行 17

**装饰器**: govmcp_tool(name='initiate_approval_workflow', description='发起审批流程')

发起审批工作流。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_name` | `str` | 是 | `-` |  |
| `applicant_name` | `str` | 是 | `-` |  |
| `applicant_department` | `str` | 是 | `-` |  |
| `workflow_type` | `str` | 是 | `-` |  |
| `business_data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_approval_progress(workflow_id: str) -> Dict[str, Any]`

**位置**: 行 58

**装饰器**: govmcp_tool(name='query_approval_progress', description='查询审批进度')

查询审批流程进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `submit_approval_comment(workflow_id: str, approver_name: str, action: str, comment: str) -> Dict[str, Any]`

**位置**: 行 104

**装饰器**: govmcp_tool(name='submit_approval_comment', description='提交审批意见')

提交审批意见。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | 是 | `-` |  |
| `approver_name` | `str` | 是 | `-` |  |
| `action` | `str` | 是 | `-` |  |
| `comment` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `handle_approval_counter_sign(workflow_id: str, current_approver: str, counter_signer: str, reason: str) -> Dict[str, Any]`

**位置**: 行 140

**装饰器**: govmcp_tool(name='handle_approval_counter_sign', description='审批加签处理')

审批加签处理（增加临时审批节点）。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | 是 | `-` |  |
| `current_approver` | `str` | 是 | `-` |  |
| `counter_signer` | `str` | 是 | `-` |  |
| `reason` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `handle_approval_transfer(workflow_id: str, original_approver: str, new_approver: str, reason: str) -> Dict[str, Any]`

**位置**: 行 178

**装饰器**: govmcp_tool(name='handle_approval_transfer', description='审批改签处理')

审批改签处理（更换审批人）。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | 是 | `-` |  |
| `original_approver` | `str` | 是 | `-` |  |
| `new_approver` | `str` | 是 | `-` |  |
| `reason` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `handle_approval_joint_sign(workflow_id: str, approvers: List[str], deadline: str) -> Dict[str, Any]`

**位置**: 行 216

**装饰器**: govmcp_tool(name='handle_approval_joint_sign', description='审批会签处理')

审批会签处理（多人同时审批）。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | 是 | `-` |  |
| `approvers` | `List[str]` | 是 | `-` |  |
| `deadline` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `handle_approval_suspend_resume(workflow_id: str, action: str, reason: Optional[str] = None) -> Dict[str, Any]`

**位置**: 行 251

**装饰器**: govmcp_tool(name='handle_approval_suspend_resume', description='审批挂起恢复')

审批流程挂起或恢复。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | 是 | `-` |  |
| `action` | `str` | 是 | `-` |  |
| `reason` | `Optional[str]` | 否 | `None` |  |

**返回** `Dict[str, Any]`

---

##### `handle_approval_delegation(delegator: str, delegatee: str, start_date: str, end_date: str, workflow_types: List[str]) -> Dict[str, Any]`

**位置**: 行 285

**装饰器**: govmcp_tool(name='handle_approval_delegation', description='审批委托代理')

设置审批委托代理。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `delegator` | `str` | 是 | `-` |  |
| `delegatee` | `str` | 是 | `-` |  |
| `start_date` | `str` | 是 | `-` |  |
| `end_date` | `str` | 是 | `-` |  |
| `workflow_types` | `List[str]` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_approval_warning(approver_name: str) -> Dict[str, Any]`

**位置**: 行 324

**装饰器**: govmcp_tool(name='query_approval_warning', description='查询审批时限预警')

查询审批时限预警信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `approver_name` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_approval_statistics(department: str, start_date: str, end_date: str) -> Dict[str, Any]`

**位置**: 行 368

**装饰器**: govmcp_tool(name='query_approval_statistics', description='查询审批统计分析')

查询审批流程统计分析。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `department` | `str` | 是 | `-` |  |
| `start_date` | `str` | 是 | `-` |  |
| `end_date` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `manage_approval_archive(workflow_id: str, action: str) -> Dict[str, Any]`

**位置**: 行 410

**装饰器**: govmcp_tool(name='manage_approval_archive', description='审批归档管理')

审批流程归档管理。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | 是 | `-` |  |
| `action` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `configure_approval_permission(role_name: str, workflow_types: List[str], approval_limits: Dict[str, float]) -> Dict[str, Any]`

**位置**: 行 442

**装饰器**: govmcp_tool(name='configure_approval_permission', description='配置审批权限')

配置审批权限。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `role_name` | `str` | 是 | `-` |  |
| `workflow_types` | `List[str]` | 是 | `-` |  |
| `approval_limits` | `Dict[str, float]` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `manage_approval_template(template_name: str, workflow_type: str, stages: List[Dict[str, Any]], action: str) -> Dict[str, Any]`

**位置**: 行 476

**装饰器**: govmcp_tool(name='manage_approval_template', description='审批模板管理')

审批模板管理。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `template_name` | `str` | 是 | `-` |  |
| `workflow_type` | `str` | 是 | `-` |  |
| `stages` | `List[Dict[str, Any]]` | 是 | `-` |  |
| `action` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_approval_digital_signature(workflow_id: str, approver_name: str, signature_type: str) -> Dict[str, Any]`

**位置**: 行 512

**装饰器**: govmcp_tool(name='apply_approval_digital_signature', description='审批电子签章')

审批电子签章应用。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | 是 | `-` |  |
| `approver_name` | `str` | 是 | `-` |  |
| `signature_type` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `generate_approval_document(workflow_id: str, document_type: str, include_attachments: bool = True) -> Dict[str, Any]`

**位置**: 行 550

**装饰器**: govmcp_tool(name='generate_approval_document', description='生成审批文书')

生成审批文书。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `workflow_id` | `str` | 是 | `-` |  |
| `document_type` | `str` | 是 | `-` |  |
| `include_attachments` | `bool` | 否 | `True` |  |

**返回** `Dict[str, Any]`

---

### `govmcp.tools.government.carbon_emission`

govmcp.tools.government.carbon_emission — 碳排放管理工具模块

提供企业碳排放数据录入、碳交易、碳足迹计算、碳中和追踪等碳排放管理服务的工具函数。

#### 函数

##### `input_carbon_emission_data(company_name: str, credit_code: str, reporting_year: int, reporting_quarter: int, coal_consumption: float, oil_consumption: float, natural_gas_consumption: float, electricity_consumption: float) -> Dict[str, Any]`

**位置**: 行 17

**装饰器**: govmcp_tool(name='input_carbon_emission_data', description='录入企业碳排放数据')

录入企业碳排放活动数据。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `credit_code` | `str` | 是 | `-` |  |
| `reporting_year` | `int` | 是 | `-` |  |
| `reporting_quarter` | `int` | 是 | `-` |  |
| `coal_consumption` | `float` | 是 | `-` |  |
| `oil_consumption` | `float` | 是 | `-` |  |
| `natural_gas_consumption` | `float` | 是 | `-` |  |
| `electricity_consumption` | `float` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_carbon_quota(company_name: str, credit_code: str, year: int) -> Dict[str, Any]`

**位置**: 行 72

**装饰器**: govmcp_tool(name='query_carbon_quota', description='查询碳排放配额')

查询企业碳排放配额分配情况。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `credit_code` | `str` | 是 | `-` |  |
| `year` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `trade_carbon_emission_allowance(company_name: str, trade_type: str, quantity: float, price: float) -> Dict[str, Any]`

**位置**: 行 108

**装饰器**: govmcp_tool(name='trade_carbon_emission_allowance', description='碳排放权交易')

碳排放权交易（买入/卖出配额）。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `trade_type` | `str` | 是 | `-` |  |
| `quantity` | `float` | 是 | `-` |  |
| `price` | `float` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `generate_carbon_emission_report(company_name: str, credit_code: str, year: int, report_type: str) -> Dict[str, Any]`

**位置**: 行 145

**装饰器**: govmcp_tool(name='generate_carbon_emission_report', description='生成碳排放报告')

生成企业碳排放报告。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `credit_code` | `str` | 是 | `-` |  |
| `year` | `int` | 是 | `-` |  |
| `report_type` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `calculate_carbon_footprint(product_name: str, raw_materials: Dict[str, float], manufacturing_energy: float, transportation_distance: float, packaging_weight: float) -> Dict[str, Any]`

**位置**: 行 184

**装饰器**: govmcp_tool(name='calculate_carbon_footprint', description='计算碳足迹')

计算产品碳足迹。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `product_name` | `str` | 是 | `-` |  |
| `raw_materials` | `Dict[str, float]` | 是 | `-` |  |
| `manufacturing_energy` | `float` | 是 | `-` |  |
| `transportation_distance` | `float` | 是 | `-` |  |
| `packaging_weight` | `float` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `set_emission_reduction_target(company_name: str, base_year: int, base_emission: float, target_year: int, target_reduction_ratio: float) -> Dict[str, Any]`

**位置**: 行 233

**装饰器**: govmcp_tool(name='set_emission_reduction_target', description='设定减排目标')

设定企业碳减排目标。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `base_year` | `int` | 是 | `-` |  |
| `base_emission` | `float` | 是 | `-` |  |
| `target_year` | `int` | 是 | `-` |  |
| `target_reduction_ratio` | `float` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_carbon_verification(company_name: str, credit_code: str, reporting_year: int, verification_body: str) -> Dict[str, Any]`

**位置**: 行 275

**装饰器**: govmcp_tool(name='apply_carbon_verification', description='申请碳核查')

申请碳排放核查。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `credit_code` | `str` | 是 | `-` |  |
| `reporting_year` | `int` | 是 | `-` |  |
| `verification_body` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `register_ccer_project(company_name: str, project_type: str, project_capacity: float, start_date: str, location: str) -> Dict[str, Any]`

**位置**: 行 311

**装饰器**: govmcp_tool(name='register_ccer_project', description='CCER项目登记')

登记CCER（中国核证自愿减排量）项目。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `project_type` | `str` | 是 | `-` |  |
| `project_capacity` | `float` | 是 | `-` |  |
| `start_date` | `str` | 是 | `-` |  |
| `location` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_carbon_asset_account(company_name: str, credit_code: str) -> Dict[str, Any]`

**位置**: 行 350

**装饰器**: govmcp_tool(name='query_carbon_asset_account', description='查询碳资产账户')

查询企业碳资产账户信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `credit_code` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_carbon_monitoring_data(company_name: str, monitor_point: str, start_date: str, end_date: str) -> Dict[str, Any]`

**位置**: 行 383

**装饰器**: govmcp_tool(name='query_carbon_monitoring_data', description='查询碳排放监测数据')

查询碳排放连续监测数据。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `monitor_point` | `str` | 是 | `-` |  |
| `start_date` | `str` | 是 | `-` |  |
| `end_date` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `analyze_industrial_carbon_emission(industry: str, region: str, year: int) -> Dict[str, Any]`

**位置**: 行 424

**装饰器**: govmcp_tool(name='analyze_industrial_carbon_emission', description='工业碳排放分析')

工业行业碳排放分析。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `industry` | `str` | 是 | `-` |  |
| `region` | `str` | 是 | `-` |  |
| `year` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_energy_consumption(company_name: str, year: int, month: int) -> Dict[str, Any]`

**位置**: 行 463

**装饰器**: govmcp_tool(name='query_energy_consumption', description='查询能源消耗统计')

查询企业能源消耗统计数据。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `year` | `int` | 是 | `-` |  |
| `month` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_green_electricity_trade(company_name: str, year: int) -> Dict[str, Any]`

**位置**: 行 503

**装饰器**: govmcp_tool(name='query_green_electricity_trade', description='查询绿电交易')

查询绿色电力交易信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `year` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `track_carbon_neutrality_progress(company_name: str, target_year: int) -> Dict[str, Any]`

**位置**: 行 547

**装饰器**: govmcp_tool(name='track_carbon_neutrality_progress', description='追踪碳中和进度')

追踪企业碳中和实施进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `target_year` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `predict_carbon_emission(company_name: str, historical_data: List[Dict[str, Any]], forecast_years: int) -> Dict[str, Any]`

**位置**: 行 583

**装饰器**: govmcp_tool(name='predict_carbon_emission', description='碳排放预测分析')

碳排放预测分析。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `historical_data` | `List[Dict[str, Any]]` | 是 | `-` |  |
| `forecast_years` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

### `govmcp.tools.government.citizen_service`

govmcp.tools.government.citizen_service — 市民服务工具模块

提供身份证、户籍、社保、医保、公积金、交通、不动产等市民常用政务服务的工具函数。

#### 函数

##### `query_id_card_progress(name: str, id_number: str, phone: str) -> Dict[str, Any]`

**位置**: 行 17

**装饰器**: govmcp_tool(name='query_id_card_progress', description='查询身份证办理进度')

查询身份证办理进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |
| `phone` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_household_registration(id_number: str, name: str) -> Dict[str, Any]`

**位置**: 行 49

**装饰器**: govmcp_tool(name='query_household_registration', description='查询户籍信息')

查询户籍基本信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | 是 | `-` |  |
| `name` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_social_security_account(id_number: str, name: str) -> Dict[str, Any]`

**位置**: 行 79

**装饰器**: govmcp_tool(name='query_social_security_account', description='查询社保账户信息')

查询社保账户余额和基本信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | 是 | `-` |  |
| `name` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_social_security_payment(id_number: str, year: int, month: int) -> Dict[str, Any]`

**位置**: 行 111

**装饰器**: govmcp_tool(name='query_social_security_payment', description='查询社保缴费记录')

查询社保缴费明细记录。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | 是 | `-` |  |
| `year` | `int` | 是 | `-` |  |
| `month` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_medical_insurance_account(id_number: str, name: str) -> Dict[str, Any]`

**位置**: 行 146

**装饰器**: govmcp_tool(name='query_medical_insurance_account', description='查询医保账户')

查询医保个人账户余额和消费记录。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | 是 | `-` |  |
| `name` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_medical_settlement(id_number: str, start_date: str, end_date: str) -> Dict[str, Any]`

**位置**: 行 178

**装饰器**: govmcp_tool(name='query_medical_settlement', description='查询医保结算记录')

查询医保结算明细。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | 是 | `-` |  |
| `start_date` | `str` | 是 | `-` |  |
| `end_date` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_housing_fund_account(id_number: str, name: str) -> Dict[str, Any]`

**位置**: 行 226

**装饰器**: govmcp_tool(name='query_housing_fund_account', description='查询公积金账户')

查询公积金账户余额。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | 是 | `-` |  |
| `name` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_housing_fund_withdrawal(id_number: str, name: str, withdrawal_type: str, amount: float, bank_name: str, bank_account: str) -> Dict[str, Any]`

**位置**: 行 259

**装饰器**: govmcp_tool(name='apply_housing_fund_withdrawal', description='申请公积金提取')

申请公积金提取。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | 是 | `-` |  |
| `name` | `str` | 是 | `-` |  |
| `withdrawal_type` | `str` | 是 | `-` |  |
| `amount` | `float` | 是 | `-` |  |
| `bank_name` | `str` | 是 | `-` |  |
| `bank_account` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_housing_fund_loan(id_number: str, loan_app_no: str) -> Dict[str, Any]`

**位置**: 行 299

**装饰器**: govmcp_tool(name='query_housing_fund_loan', description='查询公积金贷款进度')

查询公积金贷款申请进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | 是 | `-` |  |
| `loan_app_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_residence_permit(name: str, id_number: str, phone: str) -> Dict[str, Any]`

**位置**: 行 331

**装饰器**: govmcp_tool(name='query_residence_permit', description='查询居住证办理进度')

查询居住证办理进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |
| `phone` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_driver_license(name: str, license_no: str) -> Dict[str, Any]`

**位置**: 行 364

**装饰器**: govmcp_tool(name='query_driver_license', description='查询驾驶证信息')

查询驾驶证信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `license_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_vehicle_info(plate_number: str, id_number: str) -> Dict[str, Any]`

**位置**: 行 397

**装饰器**: govmcp_tool(name='query_vehicle_info', description='查询车辆信息')

查询车辆登记信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `plate_number` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_traffic_violation(plate_number: str, id_number: str) -> Dict[str, Any]`

**位置**: 行 431

**装饰器**: govmcp_tool(name='query_traffic_violation', description='查询交通违章记录')

查询车辆交通违章记录。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `plate_number` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_property_registration(id_number: str, property_address: str) -> Dict[str, Any]`

**位置**: 行 471

**装饰器**: govmcp_tool(name='query_property_registration', description='查询不动产登记信息')

查询不动产登记信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `id_number` | `str` | 是 | `-` |  |
| `property_address` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_utility_bill(account_no: str, bill_type: str) -> Dict[str, Any]`

**位置**: 行 504

**装饰器**: govmcp_tool(name='query_utility_bill', description='查询水电气缴费记录')

查询水电气等公用事业缴费情况。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `account_no` | `str` | 是 | `-` |  |
| `bill_type` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_low_income_assistance(name: str, id_number: str, address: str, income: float, family_size: int) -> Dict[str, Any]`

**位置**: 行 536

**装饰器**: govmcp_tool(name='apply_low_income_assistance', description='申请低保救助')

申请最低生活保障救助。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |
| `address` | `str` | 是 | `-` |  |
| `income` | `float` | 是 | `-` |  |
| `family_size` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_disability_subsidy(name: str, id_number: str, disability_level: str, disability_cert_no: str) -> Dict[str, Any]`

**位置**: 行 572

**装饰器**: govmcp_tool(name='apply_disability_subsidy', description='申请残疾人补贴')

申请残疾人补贴。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |
| `disability_level` | `str` | 是 | `-` |  |
| `disability_cert_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_elderly_benefit_card(name: str, id_number: str, birth_date: str) -> Dict[str, Any]`

**位置**: 行 608

**装饰器**: govmcp_tool(name='apply_elderly_benefit_card', description='申请老年人优待证')

申请老年人优待证。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |
| `birth_date` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `book_marriage_registration(name1: str, id_number1: str, name2: str, id_number2: str, book_date: str, location: str) -> Dict[str, Any]`

**位置**: 行 642

**装饰器**: govmcp_tool(name='book_marriage_registration', description='预约婚姻登记')

预约婚姻登记。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name1` | `str` | 是 | `-` |  |
| `id_number1` | `str` | 是 | `-` |  |
| `name2` | `str` | 是 | `-` |  |
| `id_number2` | `str` | 是 | `-` |  |
| `book_date` | `str` | 是 | `-` |  |
| `location` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `register_fertility_service(name: str, id_number: str, spouse_name: str, spouse_id_number: str, expected_date: str) -> Dict[str, Any]`

**位置**: 行 683

**装饰器**: govmcp_tool(name='register_fertility_service', description='生育服务登记')

生育服务登记（准生证办理）。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |
| `spouse_name` | `str` | 是 | `-` |  |
| `spouse_id_number` | `str` | 是 | `-` |  |
| `expected_date` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

### `govmcp.tools.government.enterprise_service`

govmcp.tools.government.enterprise_service — 企业服务工具模块

提供工商登记、税务、许可证、知识产权、政府采购等企业常用政务服务的工具函数。

#### 函数

##### `query_business_registration(company_name: str, unified_social_credit_code: str) -> Dict[str, Any]`

**位置**: 行 17

**装饰器**: govmcp_tool(name='query_business_registration', description='查询企业工商登记信息')

查询企业工商登记注册信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `unified_social_credit_code` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_business_license(company_name: str, company_type: str, registered_capital: float, business_scope: str, address: str, legal_person: str, id_number: str) -> Dict[str, Any]`

**位置**: 行 51

**装饰器**: govmcp_tool(name='apply_business_license', description='办理营业执照')

申请办理营业执照。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `company_type` | `str` | 是 | `-` |  |
| `registered_capital` | `float` | 是 | `-` |  |
| `business_scope` | `str` | 是 | `-` |  |
| `address` | `str` | 是 | `-` |  |
| `legal_person` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_tax_registration(company_name: str, tax_id: str) -> Dict[str, Any]`

**位置**: 行 91

**装饰器**: govmcp_tool(name='query_tax_registration', description='查询税务登记信息')

查询企业税务登记信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `tax_id` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_invoice(company_name: str, tax_id: str, invoice_type: str, quantity: int) -> Dict[str, Any]`

**位置**: 行 123

**装饰器**: govmcp_tool(name='apply_invoice', description='申领发票')

申领增值税发票。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `tax_id` | `str` | 是 | `-` |  |
| `invoice_type` | `str` | 是 | `-` |  |
| `quantity` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_social_security_account(company_name: str, credit_code: str, legal_person: str, employee_count: int, address: str) -> Dict[str, Any]`

**位置**: 行 159

**装饰器**: govmcp_tool(name='apply_social_security_account', description='办理社保开户')

办理企业社会保险开户。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `credit_code` | `str` | 是 | `-` |  |
| `legal_person` | `str` | 是 | `-` |  |
| `employee_count` | `int` | 是 | `-` |  |
| `address` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_housing_fund_account_enterprise(company_name: str, credit_code: str, employee_count: int, monthly_deposit_base: float) -> Dict[str, Any]`

**位置**: 行 196

**装饰器**: govmcp_tool(name='apply_housing_fund_account_enterprise', description='办理公积金开户')

办理企业住房公积金开户。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `credit_code` | `str` | 是 | `-` |  |
| `employee_count` | `int` | 是 | `-` |  |
| `monthly_deposit_base` | `float` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_environmental_impact_approval(project_name: str, approval_no: str) -> Dict[str, Any]`

**位置**: 行 231

**装饰器**: govmcp_tool(name='query_environmental_impact_approval', description='查询环评审批进度')

查询环境影响评价审批进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `project_name` | `str` | 是 | `-` |  |
| `approval_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_fire_approval(project_name: str, application_no: str) -> Dict[str, Any]`

**位置**: 行 262

**装饰器**: govmcp_tool(name='query_fire_approval', description='查询消防审批进度')

查询建设工程消防设计审核/验收审批进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `project_name` | `str` | 是 | `-` |  |
| `application_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_building_permit(project_name: str, permit_no: str) -> Dict[str, Any]`

**位置**: 行 293

**装饰器**: govmcp_tool(name='query_building_permit', description='查询建筑许可审批进度')

查询建筑工程施工许可审批进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `project_name` | `str` | 是 | `-` |  |
| `permit_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_food_business_license(company_name: str, business_address: str, business_type: str, food_category: str) -> Dict[str, Any]`

**位置**: 行 324

**装饰器**: govmcp_tool(name='apply_food_business_license', description='申请食品经营许可证')

申请食品经营许可证。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `business_address` | `str` | 是 | `-` |  |
| `business_type` | `str` | 是 | `-` |  |
| `food_category` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_drug_operation_license(company_name: str, warehouse_address: str, business_scope: str, storage_capacity: float) -> Dict[str, Any]`

**位置**: 行 359

**装饰器**: govmcp_tool(name='apply_drug_operation_license', description='申请药品经营许可证')

申请药品经营许可证。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `warehouse_address` | `str` | 是 | `-` |  |
| `business_scope` | `str` | 是 | `-` |  |
| `storage_capacity` | `float` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_medical_device_license(company_name: str, product_category: str, business_scope: str) -> Dict[str, Any]`

**位置**: 行 394

**装饰器**: govmcp_tool(name='apply_medical_device_license', description='申请医疗器械经营许可证')

申请医疗器械经营许可证。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `product_category` | `str` | 是 | `-` |  |
| `business_scope` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_intellectual_property(company_name: str, ip_type: str, ip_name: str, application_type: str) -> Dict[str, Any]`

**位置**: 行 427

**装饰器**: govmcp_tool(name='apply_intellectual_property', description='申请知识产权保护')

申请知识产权（著作权、软件著作权等）保护。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `ip_type` | `str` | 是 | `-` |  |
| `ip_name` | `str` | 是 | `-` |  |
| `application_type` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_trademark_registration(company_name: str, trademark_name: str, application_no: str) -> Dict[str, Any]`

**位置**: 行 463

**装饰器**: govmcp_tool(name='query_trademark_registration', description='查询商标注册进度')

查询商标注册申请进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `trademark_name` | `str` | 是 | `-` |  |
| `application_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_patent_application(applicant: str, patent_type: str, application_no: str) -> Dict[str, Any]`

**位置**: 行 496

**装饰器**: govmcp_tool(name='query_patent_application', description='查询专利申请进度')

查询专利申请进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `applicant` | `str` | 是 | `-` |  |
| `patent_type` | `str` | 是 | `-` |  |
| `application_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_high_tech_enterprise(company_name: str, industry: str, rd_expense_ratio: float, patent_count: int) -> Dict[str, Any]`

**位置**: 行 529

**装饰器**: govmcp_tool(name='apply_high_tech_enterprise', description='申请高新技术企业认定')

申请高新技术企业认定。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `industry` | `str` | 是 | `-` |  |
| `rd_expense_ratio` | `float` | 是 | `-` |  |
| `patent_count` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_tech_project(company_name: str, project_name: str, project_type: str, budget: float) -> Dict[str, Any]`

**位置**: 行 565

**装饰器**: govmcp_tool(name='apply_tech_project', description='申报科技项目')

申报科技计划项目。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `project_name` | `str` | 是 | `-` |  |
| `project_type` | `str` | 是 | `-` |  |
| `budget` | `float` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_government_procurement(keyword: str, region: str) -> Dict[str, Any]`

**位置**: 行 601

**装饰器**: govmcp_tool(name='query_government_procurement', description='查询政府采购招标信息')

查询政府采购招标公告信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `keyword` | `str` | 是 | `-` |  |
| `region` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_enterprise_credit_report(company_name: str, credit_code: str) -> Dict[str, Any]`

**位置**: 行 638

**装饰器**: govmcp_tool(name='query_enterprise_credit_report', description='查询企业信用报告')

查询企业信用报告。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `credit_code` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_listing_guidance_progress(company_name: str, stock_code: str) -> Dict[str, Any]`

**位置**: 行 673

**装饰器**: govmcp_tool(name='query_listing_guidance_progress', description='查询上市辅导进度')

查询企业上市辅导进度。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `stock_code` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

### `govmcp.tools.government.environmental`

govmcp.tools.government.environmental — 环保监测工具模块

提供空气质量、水质、土壤、噪声、固废等环境监测和环保监管服务的工具函数。

#### 函数

##### `query_air_quality(region: str, monitoring_station: str, date: str) -> Dict[str, Any]`

**位置**: 行 17

**装饰器**: govmcp_tool(name='query_air_quality', description='查询空气质量监测数据')

查询空气质量监测数据。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `region` | `str` | 是 | `-` |  |
| `monitoring_station` | `str` | 是 | `-` |  |
| `date` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_water_quality(river_name: str, section_name: str, date: str) -> Dict[str, Any]`

**位置**: 行 56

**装饰器**: govmcp_tool(name='query_water_quality', description='查询水质监测数据')

查询水质监测数据。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `river_name` | `str` | 是 | `-` |  |
| `section_name` | `str` | 是 | `-` |  |
| `date` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `detect_soil_pollution(location: str, land_use: str, sampling_date: str) -> Dict[str, Any]`

**位置**: 行 94

**装饰器**: govmcp_tool(name='detect_soil_pollution', description='土壤污染检测')

土壤污染状况检测查询。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `location` | `str` | 是 | `-` |  |
| `land_use` | `str` | 是 | `-` |  |
| `sampling_date` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_noise_monitoring(monitoring_point: str, date: str, time_period: str) -> Dict[str, Any]`

**位置**: 行 133

**装饰器**: govmcp_tool(name='query_noise_monitoring', description='查询噪声监测数据')

查询环境噪声监测数据。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `monitoring_point` | `str` | 是 | `-` |  |
| `date` | `str` | 是 | `-` |  |
| `time_period` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_solid_waste_disposal(company_name: str, waste_type: str) -> Dict[str, Any]`

**位置**: 行 168

**装饰器**: govmcp_tool(name='query_solid_waste_disposal', description='查询固废处理监管信息')

查询固体废物处理处置监管信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `waste_type` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_hazardous_waste_transfer(manifest_no: str) -> Dict[str, Any]`

**位置**: 行 202

**装饰器**: govmcp_tool(name='query_hazardous_waste_transfer', description='查询危险废物转移联单')

查询危险废物转移联单信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `manifest_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_radiation_monitoring(monitoring_location: str, monitoring_type: str, date: str) -> Dict[str, Any]`

**位置**: 行 234

**装饰器**: govmcp_tool(name='query_radiation_monitoring', description='查询辐射环境监测数据')

查询辐射环境监测数据。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `monitoring_location` | `str` | 是 | `-` |  |
| `monitoring_type` | `str` | 是 | `-` |  |
| `date` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_pollution_discharge_permit(company_name: str, permit_no: str) -> Dict[str, Any]`

**位置**: 行 269

**装饰器**: govmcp_tool(name='query_pollution_discharge_permit', description='查询排污许可证信息')

查询企业排污许可证信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `permit_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_environmental_impact_assessment(project_name: str, eia_document_no: str) -> Dict[str, Any]`

**位置**: 行 307

**装饰器**: govmcp_tool(name='query_environmental_impact_assessment', description='查询环境影响评价信息')

查询环境影响评价信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `project_name` | `str` | 是 | `-` |  |
| `eia_document_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_environmental_penalty(company_name: str, region: str) -> Dict[str, Any]`

**位置**: 行 340

**装饰器**: govmcp_tool(name='query_environmental_penalty', description='查询环保处罚记录')

查询企业环保行政处罚记录。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `region` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `apply_cleaner_production_audit(company_name: str, industry: str, production_scale: str) -> Dict[str, Any]`

**位置**: 行 370

**装饰器**: govmcp_tool(name='apply_cleaner_production_audit', description='申请清洁生产审核')

申请清洁生产审核。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `industry` | `str` | 是 | `-` |  |
| `production_scale` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_environmental_acceptance(project_name: str, acceptance_no: str) -> Dict[str, Any]`

**位置**: 行 405

**装饰器**: govmcp_tool(name='query_environmental_acceptance', description='查询环保竣工验收信息')

查询建设项目竣工环境保护验收信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `project_name` | `str` | 是 | `-` |  |
| `acceptance_no` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_environmental_facility_operation(company_name: str, facility_type: str) -> Dict[str, Any]`

**位置**: 行 438

**装饰器**: govmcp_tool(name='query_environmental_facility_operation', description='查询环保设施运行数据')

查询企业环保设施运行数据。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |
| `facility_type` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_ecological_red_line(location: str) -> Dict[str, Any]`

**位置**: 行 473

**装饰器**: govmcp_tool(name='query_ecological_red_line', description='查询生态红线保护区信息')

查询区域生态红线保护信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `location` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_environmental_emergency_response(company_name: str) -> Dict[str, Any]`

**位置**: 行 507

**装饰器**: govmcp_tool(name='query_environmental_emergency_response', description='查询环境应急响应信息')

查询企业环境应急响应相关信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `company_name` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

### `govmcp.tools.government.smart_city`

govmcp.tools.government.smart_city — 智慧城市工具模块

提供智慧交通、智慧水务、智慧社区、智慧养老、应急指挥等智慧城市服务的工具函数。

#### 函数

##### `control_smart_traffic_light(intersection_id: str, action: str, duration: int) -> Dict[str, Any]`

**位置**: 行 17

**装饰器**: govmcp_tool(name='control_smart_traffic_light', description='智慧交通信号灯控制')

智慧交通信号灯控制。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `intersection_id` | `str` | 是 | `-` |  |
| `action` | `str` | 是 | `-` |  |
| `duration` | `int` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_public_parking(district: str, street: str) -> Dict[str, Any]`

**位置**: 行 51

**装饰器**: govmcp_tool(name='query_public_parking', description='查询公共停车位')

查询附近公共停车位信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `district` | `str` | 是 | `-` |  |
| `street` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `manage_smart_streetlight(streetlight_id: str, action: str, brightness: Optional[int] = None) -> Dict[str, Any]`

**位置**: 行 90

**装饰器**: govmcp_tool(name='manage_smart_streetlight', description='智慧路灯管理')

智慧路灯管理控制。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `streetlight_id` | `str` | 是 | `-` |  |
| `action` | `str` | 是 | `-` |  |
| `brightness` | `Optional[int]` | 否 | `None` |  |

**返回** `Dict[str, Any]`

---

##### `monitor_smart_water(area: str, meter_id: str) -> Dict[str, Any]`

**位置**: 行 123

**装饰器**: govmcp_tool(name='monitor_smart_water', description='智慧水务监控')

智慧水务监控系统。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `area` | `str` | 是 | `-` |  |
| `meter_id` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `supervise_smart_gas(area: str, meter_id: str) -> Dict[str, Any]`

**位置**: 行 161

**装饰器**: govmcp_tool(name='supervise_smart_gas', description='智慧燃气监管')

智慧燃气监管系统。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `area` | `str` | 是 | `-` |  |
| `meter_id` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `manage_smart_heating(building_id: str, action: str, target_temperature: Optional[float] = None) -> Dict[str, Any]`

**位置**: 行 196

**装饰器**: govmcp_tool(name='manage_smart_heating', description='智慧供热管理')

智慧供热管理系统。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `building_id` | `str` | 是 | `-` |  |
| `action` | `str` | 是 | `-` |  |
| `target_temperature` | `Optional[float]` | 否 | `None` |  |

**返回** `Dict[str, Any]`

---

##### `query_smart_community(community_name: str, service_type: str) -> Dict[str, Any]`

**位置**: 行 231

**装饰器**: govmcp_tool(name='query_smart_community', description='智慧社区服务查询')

智慧社区服务查询。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `community_name` | `str` | 是 | `-` |  |
| `service_type` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_smart_city_enforcement(area: str, violation_type: Optional[str] = None) -> Dict[str, Any]`

**位置**: 行 263

**装饰器**: govmcp_tool(name='query_smart_city_enforcement', description='智慧城管执法查询')

智慧城管执法系统查询。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `area` | `str` | 是 | `-` |  |
| `violation_type` | `Optional[str]` | 否 | `None` |  |

**返回** `Dict[str, Any]`

---

##### `query_public_bicycle(location: str) -> Dict[str, Any]`

**位置**: 行 302

**装饰器**: govmcp_tool(name='query_public_bicycle', description='查询公共自行车')

查询公共自行车站点信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `location` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_smart_elderly_care(elderly_name: str, id_number: str, service_type: str) -> Dict[str, Any]`

**位置**: 行 343

**装饰器**: govmcp_tool(name='query_smart_elderly_care', description='智慧养老服务查询')

智慧养老服务查询。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `elderly_name` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |
| `service_type` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_smart_education(student_name: str, student_id: str, service_type: str) -> Dict[str, Any]`

**位置**: 行 379

**装饰器**: govmcp_tool(name='query_smart_education', description='智慧教育服务查询')

智慧教育服务查询。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `student_name` | `str` | 是 | `-` |  |
| `student_id` | `str` | 是 | `-` |  |
| `service_type` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `book_smart_medical(patient_name: str, id_number: str, hospital: str, department: str, booking_date: str, doctor: Optional[str] = None) -> Dict[str, Any]`

**位置**: 行 419

**装饰器**: govmcp_tool(name='book_smart_medical', description='智慧医疗预约')

智慧医疗预约挂号。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `patient_name` | `str` | 是 | `-` |  |
| `id_number` | `str` | 是 | `-` |  |
| `hospital` | `str` | 是 | `-` |  |
| `department` | `str` | 是 | `-` |  |
| `booking_date` | `str` | 是 | `-` |  |
| `doctor` | `Optional[str]` | 否 | `None` |  |

**返回** `Dict[str, Any]`

---

##### `dispatch_emergency_command(incident_type: str, location: str, severity: str, reporter: str, description: str) -> Dict[str, Any]`

**位置**: 行 462

**装饰器**: govmcp_tool(name='dispatch_emergency_command', description='应急指挥调度')

应急指挥调度系统。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `incident_type` | `str` | 是 | `-` |  |
| `location` | `str` | 是 | `-` |  |
| `severity` | `str` | 是 | `-` |  |
| `reporter` | `str` | 是 | `-` |  |
| `description` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_grid_management(grid_id: str, query_type: str) -> Dict[str, Any]`

**位置**: 行 503

**装饰器**: govmcp_tool(name='query_grid_management', description='网格化管理查询')

网格化管理系统查询。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `grid_id` | `str` | 是 | `-` |  |
| `query_type` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `query_snow亮的视频(camera_id: str, query_type: str, start_time: str, end_time: str) -> Dict[str, Any]`

**位置**: 行 544

**装饰器**: govmcp_tool(name='query_snow亮的视频', description='雪亮工程视频监控查询')

雪亮工程视频监控系统查询。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `camera_id` | `str` | 是 | `-` |  |
| `query_type` | `str` | 是 | `-` |  |
| `start_time` | `str` | 是 | `-` |  |
| `end_time` | `str` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

### `govmcp.tools.registry`

govmcp.tools.registry — 工具注册中心

====================================

提供 ToolRegistry 类用于管理工具注册/注销/列表/调用，

以及 govmcp_tool 装饰器用于便捷地将 Python 函数注册为 MCP 工具。

标准 MCP 输出格式:

- tools/list: {"tools": [{"name": "...", "description": "...", "inputSchema": {...}}]}

- tools/call: {"content": [{"type": "text", "text": "..."}], "isError": false}

#### 函数

##### `govmcp_tool(name: Optional[str] = None, description: str = '', approval_required: bool = False, audit_enabled: bool = True) -> Callable`

**位置**: 行 288

装饰器：将 Python 函数自动注册为 MCP 工具。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `Optional[str]` | 否 | `None` |  |
| `description` | `str` | 否 | `''` |  |
| `approval_required` | `bool` | 否 | `False` |  |
| `audit_enabled` | `bool` | 否 | `True` |  |

**返回** `Callable`

---

##### `to_mcp_dict() -> Dict[str, Any]`

**位置**: 行 128

转为标准 MCP tools/list 条目。

**返回** `Dict[str, Any]`

---

##### `__init__() -> None`

**位置**: 行 154

**返回** `None`

---

##### `register(name: str, description: str, input_schema: Dict[str, Any], handler: Callable, approval_required: bool = False, audit_enabled: bool = True) -> None`

**位置**: 行 159

注册一个工具。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `description` | `str` | 是 | `-` |  |
| `input_schema` | `Dict[str, Any]` | 是 | `-` |  |
| `handler` | `Callable` | 是 | `-` |  |
| `approval_required` | `bool` | 否 | `False` |  |
| `audit_enabled` | `bool` | 否 | `True` |  |

**返回** `None`

---

##### `unregister(name: str) -> None`

**位置**: 行 193

注销一个工具。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |

**返回** `None`

---

##### `get(name: str) -> ToolInfo`

**位置**: 行 209

获取工具信息。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |

**返回** `ToolInfo`

---

##### `count() -> int`

**位置**: 行 226

返回已注册工具数量。

**返回** `int`

---

##### `list_tools() -> List[Dict[str, Any]]`

**位置**: 行 232

列出所有工具（标准 MCP tools/list 格式）。

**返回** `List[Dict[str, Any]]`

---

##### `call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]`

**位置**: 行 241

执行工具并返回标准 MCP tools/call 格式。

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `name` | `str` | 是 | `-` |  |
| `arguments` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `Dict[str, Any]`

---

##### `decorator(func: Callable) -> Callable`

**位置**: 行 308

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `func` | `Callable` | 是 | `-` |  |

**返回** `Callable`

---

##### `wrapper(**args, ****kwargs) -> Any`

**位置**: 行 323

**装饰器**: functools.wraps(func)

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `*args` | `Any` | 否 | `-` | Variable positional arguments |
| `**kwargs` | `Any` | 否 | `-` | Variable keyword arguments |

**返回** `Any`

---

#### 类

##### `ToolInfo`
`数据类`

MCP 工具的描述信息。

**属性**

| 名称 | 类型 |
|:---|:---|
| `name` | `str` |
| `description` | `str` |
| `input_schema` | `Dict[str, Any]` |
| `handler` | `Callable` |
| `approval_required` | `bool` |
| `audit_enabled` | `bool` |

**方法**

- `to_mcp_dict()` - 转为标准 MCP tools/list 条目。

---

##### `ToolRegistry`

MCP 工具注册中心。

**方法**

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

#### 函数

##### `from_dict(data: Dict[str, Any]) -> Message`

**位置**: 行 54

**装饰器**: classmethod

从字典创建消息

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `Message`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 63

转换为字典

**返回** `Dict[str, Any]`

---

##### `from_dict(data: Dict[str, Any]) -> Response`

**位置**: 行 85

**装饰器**: classmethod

从字典创建响应

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `data` | `Dict[str, Any]` | 是 | `-` |  |

**返回** `Response`

---

##### `to_dict() -> Dict[str, Any]`

**位置**: 行 99

转换为字典

**返回** `Dict[str, Any]`

---

##### `on_message(message: Message) -> None`

**位置**: 行 115

**装饰器**: abstractmethod

收到消息回调

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | 是 | `-` |  |

**返回** `None`

---

##### `on_error(error: Exception) -> None`

**位置**: 行 120

**装饰器**: abstractmethod

错误回调

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `error` | `Exception` | 是 | `-` |  |

**返回** `None`

---

##### `on_disconnect() -> None`

**位置**: 行 125

**装饰器**: abstractmethod

断开连接回调

**返回** `None`

---

##### `on_connect() -> None`

**位置**: 行 129

连接成功回调（可选）

**返回** `None`

---

##### `on_heartbeat() -> None`

**位置**: 行 133

心跳回调（可选）

**返回** `None`

---

##### `__init__(config: Optional[TransportConfig] = None) -> None`

**位置**: 行 149

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `Optional[TransportConfig]` | 否 | `None` |  |

**返回** `None`

---

##### `connected() -> bool`

**位置**: 行 155

**装饰器**: property

是否已连接

**返回** `bool`

---

##### `transport_type() -> TransportType`

**位置**: 行 160

**装饰器**: property

传输类型

**返回** `TransportType`

---

##### `set_callbacks(callbacks: TransportCallbacks) -> None`

**位置**: 行 164

设置回调处理器

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `callbacks` | `TransportCallbacks` | 是 | `-` |  |

**返回** `None`

---

##### `async connect() -> None`

**位置**: 行 169

**装饰器**: abstractmethod

建立连接

**返回** `None`

---

##### `async disconnect() -> None`

**位置**: 行 174

**装饰器**: abstractmethod

断开连接

**返回** `None`

---

##### `async send(message: Message) -> None`

**位置**: 行 179

**装饰器**: abstractmethod

发送消息

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | 是 | `-` |  |

**返回** `None`

---

##### `async send_response(response: Response) -> None`

**位置**: 行 184

**装饰器**: abstractmethod

发送响应

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `response` | `Response` | 是 | `-` |  |

**返回** `None`

---

##### `__init__(config: Optional[TransportConfig] = None) -> None`

**位置**: 行 220

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `Optional[TransportConfig]` | 否 | `None` |  |

**返回** `None`

---

##### `async connect() -> None`

**位置**: 行 226

建立 stdio 连接

**返回** `None`

---

##### `async disconnect() -> None`

**位置**: 行 238

断开 stdio 连接

**返回** `None`

---

##### `async send(message: Message) -> None`

**位置**: 行 256

通过 stdout 发送消息

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | 是 | `-` |  |

**返回** `None`

---

##### `async send_response(response: Response) -> None`

**位置**: 行 264

通过 stdout 发送响应

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `response` | `Response` | 是 | `-` |  |

**返回** `None`

---

##### `__init__(transport: 'WebSocketTransport') -> None`

**位置**: 行 303

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `transport` | `'WebSocketTransport'` | 是 | `-` |  |

**返回** `None`

---

##### `on_message(message: Message) -> None`

**位置**: 行 306

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | 是 | `-` |  |

**返回** `None`

---

##### `on_error(error: Exception) -> None`

**位置**: 行 310

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `error` | `Exception` | 是 | `-` |  |

**返回** `None`

---

##### `on_disconnect() -> None`

**位置**: 行 314

**返回** `None`

---

##### `on_connect() -> None`

**位置**: 行 318

**返回** `None`

---

##### `__init__(config: Optional[TransportConfig] = None) -> None`

**位置**: 行 330

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `Optional[TransportConfig]` | 否 | `None` |  |

**返回** `None`

---

##### `connected() -> bool`

**位置**: 行 337

**装饰器**: property

**返回** `bool`

---

##### `async connect() -> None`

**位置**: 行 340

建立 WebSocket 连接

**返回** `None`

---

##### `async disconnect() -> None`

**位置**: 行 374

断开 WebSocket 连接

**返回** `None`

---

##### `async send(message: Message) -> None`

**位置**: 行 396

发送 WebSocket 消息

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | 是 | `-` |  |

**返回** `None`

---

##### `async send_response(response: Response) -> None`

**位置**: 行 421

发送 WebSocket 响应

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `response` | `Response` | 是 | `-` |  |

**返回** `None`

---

##### `__init__(config: Optional[TransportConfig] = None) -> None`

**位置**: 行 491

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `config` | `Optional[TransportConfig]` | 否 | `None` |  |

**返回** `None`

---

##### `async connect() -> None`

**位置**: 行 497

建立 HTTP 连接

**返回** `None`

---

##### `async disconnect() -> None`

**位置**: 行 513

断开 HTTP 连接

**返回** `None`

---

##### `async send(message: Message) -> None`

**位置**: 行 527

发送 HTTP POST 请求

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `message` | `Message` | 是 | `-` |  |

**返回** `None`

---

##### `async send_response(response: Response) -> None`

**位置**: 行 570

HTTP 响应直接返回（由服务器端处理）

**参数**

| 名称 | 类型 | 必需 | 默认值 | 描述 |
|:---|:---|:---:|:---:|:---|
| `response` | `Response` | 是 | `-` |  |

**返回** `None`

---

##### `async get_sse_stream() -> Any`

**位置**: 行 574

获取 SSE 流

**返回** `Any`

---

#### 类

##### `TransportType`
`枚举`

**基类**: `Enum`

传输类型枚举

**枚举值**

| 名称 | 值 |
|:---|:---|
| `STDIO` | `'stdio'` |
| `WEBSOCKET` | `'websocket'` |
| `HTTP` | `'http'` |
| `SSE` | `'sse'` |

---

##### `TransportConfig`
`数据类`

传输层配置

**属性**

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
`数据类`

MCP 消息封装

**属性**

| 名称 | 类型 |
|:---|:---|
| `method` | `str` |
| `params` | `Dict[str, Any]` |
| `msg_id` | `Optional[str]` |
| `jsonrpc` | `str` |

**方法**

- `from_dict()` - 从字典创建消息
- `to_dict()` - 转换为字典

---

##### `Response`
`数据类`

MCP 响应封装

**属性**

| 名称 | 类型 |
|:---|:---|
| `result` | `Any` |
| `error` | `Optional[Dict[str, Any]]` |
| `msg_id` | `Optional[str]` |
| `jsonrpc` | `str` |

**方法**

- `from_dict()` - 从字典创建响应
- `to_dict()` - 转换为字典

---

##### `TransportCallbacks`

**基类**: `ABC`

传输层回调接口

**方法**

- `on_message()` - 收到消息回调
- `on_error()` - 错误回调
- `on_disconnect()` - 断开连接回调
- `on_connect()` - 连接成功回调（可选）
- `on_heartbeat()` - 心跳回调（可选）

---

##### `Transport`

**基类**: `ABC`

传输层抽象基类

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `Optional[TransportConfig]` |

**方法**

- `connected()` - 是否已连接
- `transport_type()` - 传输类型
- `set_callbacks()` - 设置回调处理器
- `_safe_callback_error()` - 安全调用错误回调

---

##### `StdioTransport`

**基类**: `Transport`

Stdio 传输层实现

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `Optional[TransportConfig]` |

---

##### `WebSocketTransportCallbacks`

**基类**: `TransportCallbacks`

WebSocket 传输层回调

**属性**

| 名称 | 类型 |
|:---|:---|
| `transport` | `'WebSocketTransport'` |

**方法**

- `on_message()` - 
- `on_error()` - 
- `on_disconnect()` - 
- `on_connect()` - 

---

##### `WebSocketTransport`

**基类**: `Transport`

WebSocket 传输层实现

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `Optional[TransportConfig]` |

**方法**

- `connected()` - 

---

##### `HTTPTransport`

**基类**: `Transport`

HTTP/SSE 传输层实现

**属性**

| 名称 | 类型 |
|:---|:---|
| `config` | `Optional[TransportConfig]` |

---

---

## 异常参考

| 异常类型 | 说明 |
|:---|:---|
| `ValueError` | 参数值无效 |
| `TypeError` | 参数类型错误 |
| `KeyError` | 键不存在 |
| `RuntimeError` | 运行时错误 |
| `NotImplementedError` | 功能未实现 |

---

## 类型引用索引

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

*本文档由 govmcp 文档自动生成系统生成 · 版本 1.0.0*