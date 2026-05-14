# crypto.sm

```include ../govmcp/crypto/sm.py
```

## 模块文档

govmcp 国密加密模块 — SM3哈希 + SM4对称加密

SM3: 中国国家密码管理局发布的密码杂凑算法 (GB/T 32905-2016)

输出256位哈希值，强度等同于SHA-256

SM4: 中国国家密码管理局发布的对称加密算法 (GB/T 32907-2016)

128位分组密码，密钥长度128位

生产环境应使用硬件加密模块（HSM）或国密专用芯片。

本模块提供纯软件参考实现，用于开发与测试。

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| 66 | 高 | - |
| 461 | 中 | - |
| 503 | 中 | - |
| 542 | 低 | - |
| 557 | 中 | - |
| 584 | 低 | - |
| 589 | 中 | - |
| 626 | 中 | - |
| 668 | 低 | - |

## 导出函数

### `sm3_hash(data: bytes) -> str`

`行号:66` `复杂度:高`

SM3 国密哈希

Args:

    data: 待哈希数据

Returns:

    64字符十六进制哈希值

Example:

    >>> sm3_hash(b"hello")

    'becbbfaae6548b8bf0cfcad5a27183cd1be6093b...'

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `data` | `bytes` | `-` |

#### 返回

`str`

---

### `sm4_encrypt(plaintext: bytes, key: bytes) -> bytes`

`行号:461` `复杂度:中`

SM4 国密对称加密 (ECB模式)

Args:

    plaintext: 明文 (长度必须为16的倍数)

    key: 128位密钥 (16字节)

Returns:

    密文 (与明文等长)

Raises:

    ValueError: 明文长度不是16的倍数

    ValueError: 密钥长度不是16字节

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `plaintext` | `bytes` | `-` |
| `key` | `bytes` | `-` |

#### 返回

`bytes`

---

### `sm4_decrypt(ciphertext: bytes, key: bytes) -> bytes`

`行号:503` `复杂度:中`

SM4 国密对称解密 (ECB模式)

Args:

    ciphertext: 密文

    key: 128位密钥

Returns:

    明文

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `ciphertext` | `bytes` | `-` |
| `key` | `bytes` | `-` |

#### 返回

`bytes`

---

### `pkcs7_pad(data: bytes, block_size: int = 16) -> bytes`

`行号:542` `复杂度:低`

PKCS7 填充

Args:

    data: 待填充数据

    block_size: 块大小，默认16字节

Returns:

    填充后的数据

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `data` | `bytes` | `-` |
| `block_size` (可选) | `int` | `16` |

#### 返回

`bytes`

---

### `pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes`

`行号:557` `复杂度:中`

PKCS7 去填充

Args:

    data: 填充后的数据

    block_size: 块大小，默认16字节

Returns:

    去填充后的数据

Raises:

    ValueError: 填充格式无效

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `data` | `bytes` | `-` |
| `block_size` (可选) | `int` | `16` |

#### 返回

`bytes`

---

### `generate_sm4_iv() -> bytes`

`行号:584` `复杂度:低`

生成随机SM4 IV（初始化向量）

#### 返回

`bytes`

---

### `sm4_cbc_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes`

`行号:589` `复杂度:中`

SM4-CBC 国密对称加密

Args:

    plaintext: 明文数据

    key: 128位密钥 (16字节)

    iv: 初始化向量 (16字节)

Returns:

    密文

Raises:

    ValueError: 密钥长度不是16字节

    ValueError: IV长度不是16字节

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `plaintext` | `bytes` | `-` |
| `key` | `bytes` | `-` |
| `iv` | `bytes` | `-` |

#### 返回

`bytes`

---

### `sm4_cbc_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes`

`行号:626` `复杂度:中`

SM4-CBC 国密对称解密

Args:

    ciphertext: 密文

    key: 128位密钥 (16字节)

    iv: 初始化向量 (16字节)

Returns:

    明文

Raises:

    ValueError: 密钥长度不是16字节

    ValueError: IV长度不是16字节

    ValueError: 密文长度不是16的倍数

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `ciphertext` | `bytes` | `-` |
| `key` | `bytes` | `-` |
| `iv` | `bytes` | `-` |

#### 返回

`bytes`

---

### `generate_sm4_key() -> bytes`

`行号:668` `复杂度:低`

生成随机SM4密钥

#### 返回

`bytes`

---

## Test Coverage

*No specific tests found for this module.*
