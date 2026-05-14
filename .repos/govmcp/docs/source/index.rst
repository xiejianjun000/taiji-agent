govmcp 文档
============

.. toctree::
   :maxdepth: 2
   :caption: 目录

   crypto
   protocol
   tools
   models
   api/index

简介
----

**govmcp** 是国产信创 MCP (Model Context Protocol) 标准实现，在标准 MCP 协议基础上叠加三大核心能力：

- 国密加密传输（SM2/SM3/SM4）
- 多级审批工作流
- 不可篡改审计链

快速开始
--------

安装
~~~~

.. code-block:: bash

   pip install govmcp

基础使用
~~~~~~~~

.. code-block:: python

   from govmcp import GovMCPServer, govmcp_tool

   server = GovMCPServer("my-server", "1.0", crypto_enabled=True)

   @server.tool("hello", description="问好")
   def hello(name: str) -> str:
       return f"你好, {name}!"

   server.run()

国密加密
~~~~~~~~

.. code-block:: python

   from govmcp import sm3_hash, sm4_encrypt, sm4_decrypt, generate_sm4_key

   key = generate_sm4_key()
   ciphertext = sm4_encrypt(b"Hello, World!", key)
   plaintext = sm4_decrypt(ciphertext, key)

审批工作流
~~~~~~~~~~

.. code-block:: python

   from govmcp import ApprovalFlow, ApprovalStatus

   flow = ApprovalFlow(["部门主管", "中心主任", "局领导"])
   flow.approve("部门主管", "同意")
   flow.approve("中心主任", "同意")
   flow.approve("局领导", "同意")

   assert flow.is_approved()

模块索引
--------

* :doc:`crypto` - 国密加密模块
* :doc:`protocol` - JSON-RPC 2.0 协议层
* :doc:`tools` - 工具注册中心
* :doc:`models` - 大模型适配层

API 参考
--------

* :doc:`api/index` - 完整 API 文档

索引
----

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
