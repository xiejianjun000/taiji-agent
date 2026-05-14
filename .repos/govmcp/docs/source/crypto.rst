国密加密模块
============

.. automodule:: govmcp.crypto
   :members:
   :undoc-members:
   :show-inheritance:

SM3 哈希算法
------------

SM3 是中国国家密码管理局发布的密码杂凑算法，输出 256 位哈希值，强度等同于 SHA-256。

.. autofunction:: govmcp.crypto.sm.sm3_hash

SM4 对称加密
------------

SM4 是中国国家密码管理局发布的对称加密算法，128 位分组密码，密钥长度 128 位。

.. autofunction:: govmcp.crypto.sm.sm4_encrypt

.. autofunction:: govmcp.crypto.sm.sm4_decrypt

.. autofunction:: govmcp.crypto.sm.sm4_cbc_encrypt

.. autofunction:: govmcp.crypto.sm.sm4_cbc_decrypt

SM2 非对称加密
--------------

.. autofunction:: govmcp.crypto.sm2.generate_sm2_keypair

.. autofunction:: govmcp.crypto.sm2.sm2_encrypt

.. autofunction:: govmcp.crypto.sm2.sm2_decrypt

.. autofunction:: govmcp.crypto.sm2.sm2_sign

.. autofunction:: govmcp.crypto.sm2.sm2_verify

审计链
------

.. autoclass:: govmcp.crypto.audit.AuditChain
   :members:
   :undoc-members:

.. autoclass:: govmcp.crypto.audit.AuditEntry
   :members:
   :undoc-members:
