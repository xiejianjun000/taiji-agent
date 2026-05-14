# crypto.sm2

```include ../govmcp/crypto/sm2.py
```

## Module Documentation

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

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| 223 | Medium | - |
| 254 | Medium | - |
| 320 | Medium | - |
| 388 | High | - |
| 455 | High | - |
| 524 | Low | - |
| 551 | Medium | - |

## Exported Functions

### `generate_sm2_keypair() -> Tuple[bytes, bytes]`

`Line:223` `Complexity:Medium`

生成SM2密钥对

Returns:

    Tuple[private_key, public_key]:

    - private_key: 32字节私钥

    - public_key: 64字节公钥 (未压缩格式: x||y)

Example:

    >>> private_key, public_key = generate_sm2_keypair()

    >>> len(private_key), len(public_key)

    (32, 64)

#### Returns

`Tuple[bytes, bytes]`

---

### `sm2_encrypt(plaintext: bytes, public_key: bytes) -> bytes`

`Line:254` `Complexity:Medium`

SM2加密 (C1 || C3 || C2 格式)

使用SM2椭圆曲线公钥加密算法:

1. 使用随机数k生成C1点

2. 计算S = k*P，并计算C3 = SM3(x2 || M || y2)

3. 计算C2 = M XOR t

Args:

    plaintext: 明文数据

    public_key: 64字节公钥

Returns:

    密文: C1(64字节) || C3(32字节) || C2(与明文等长)

Raises:

    ValueError: 公钥格式错误

Example:

    >>> private_key, public_key = generate_sm2_keypair()

    >>> ciphertext = sm2_encrypt(b"hello", public_key)

    >>> len(ciphertext) > len(b"hello")

    True

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `plaintext` | `bytes` | `-` |
| `public_key` | `bytes` | `-` |

#### Returns

`bytes`

---

### `sm2_decrypt(ciphertext: bytes, private_key: bytes) -> bytes`

`Line:320` `Complexity:Medium`

SM2解密

使用SM2椭圆曲线私钥解密算法:

1. 从C1解析点

2. 计算S = d*C1

3. 计算M' = C2 XOR t

4. 验证C3 = SM3(x2 || M' || y2)

Args:

    ciphertext: 密文 (C1||C3||C2格式)

    private_key: 32字节私钥

Returns:

    明文

Raises:

    ValueError: 密文或私钥格式错误

Example:

    >>> private_key, public_key = generate_sm2_keypair()

    >>> ciphertext = sm2_encrypt(b"hello", public_key)

    >>> sm2_decrypt(ciphertext, private_key)

    b'hello'

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `ciphertext` | `bytes` | `-` |
| `private_key` | `bytes` | `-` |

#### Returns

`bytes`

---

### `sm2_sign(data: bytes, private_key: bytes, user_id: bytes = None) -> bytes`

`Line:388` `Complexity:High`

SM2签名 (GB/T 32918-2016)

使用SM2椭圆曲线数字签名算法:

1. 计算Z = SM3(ENTL || ID || a || b || G || P)

2. 计算e = SM3(Z || M)

3. 计算(r + e) mod N != 0

4. 计算s = d^(-1) * (k - r) mod N

Args:

    data: 待签名数据

    private_key: 32字节私钥

    user_id: 用户标识 (默认: b"1234567812345678")

Returns:

    签名: r(32字节) || s(32字节)，共64字节

Example:

    >>> private_key, public_key = generate_sm2_keypair()

    >>> signature = sm2_sign(b"test data", private_key)

    >>> len(signature)

    64

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `data` | `bytes` | `-` |
| `private_key` | `bytes` | `-` |
| `user_id` (Optional) | `bytes` | `None` |

#### Returns

`bytes`

---

### `sm2_verify(data: bytes, signature: bytes, public_key: bytes, user_id: bytes = None) -> bool`

`Line:455` `Complexity:High`

SM2验签

Args:

    data: 原始数据

    signature: 64字节签名 (r || s)

    public_key: 64字节公钥

    user_id: 用户标识 (默认: b"1234567812345678")

Returns:

    验签结果: True 或 False

Example:

    >>> private_key, public_key = generate_sm2_keypair()

    >>> signature = sm2_sign(b"test data", private_key)

    >>> sm2_verify(b"test data", signature, public_key)

    True

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `data` | `bytes` | `-` |
| `signature` | `bytes` | `-` |
| `public_key` | `bytes` | `-` |
| `user_id` (Optional) | `bytes` | `None` |

#### Returns

`bool`

---

### `sm2_derive_key(shared_secret: bytes, key_length: int = 32) -> bytes`

`Line:524` `Complexity:Low`

SM2密钥派生函数 (KDF)

基于SM3的密钥派生函数，用于从共享秘密派生出密钥材料。

Args:

    shared_secret: 共享秘密 (建议32字节)

    key_length: 期望输出的密钥长度 (字节)

Returns:

    派生的密钥

Example:

    >>> key = sm2_derive_key(os.urandom(32), 32)

    >>> len(key)

    32

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `shared_secret` | `bytes` | `-` |
| `key_length` (Optional) | `int` | `32` |

#### Returns

`bytes`

---

### `sm2_calculate_shared_secret(private_key: bytes, peer_public_key: bytes) -> bytes`

`Line:551` `Complexity:Medium`

SM2椭圆曲线Diffie-Hellman密钥交换 - 计算共享秘密

计算 ECDH 共享点坐标，用于密钥派生。

Args:

    private_key: 本端私钥 (32字节)

    peer_public_key: 对端公钥 (64字节)

Returns:

    共享秘密 (x坐标的32字节)

Example:

    >>> private_a, public_a = generate_sm2_keypair()

    >>> private_b, public_b = generate_sm2_keypair()

    >>> secret_a = sm2_calculate_shared_secret(private_a, public_b)

    >>> secret_b = sm2_calculate_shared_secret(private_b, public_a)

    >>> secret_a == secret_b

    True

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `private_key` | `bytes` | `-` |
| `peer_public_key` | `bytes` | `-` |

#### Returns

`bytes`

---

## Test Coverage

*No specific tests found for this module.*
