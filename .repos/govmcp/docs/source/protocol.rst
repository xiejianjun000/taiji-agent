协议层
======

.. automodule:: govmcp.protocol
   :members:
   :undoc-members:
   :show-inheritance:

GovMCPServer
------------

.. autoclass:: govmcp.protocol.server.GovMCPServer
   :members:
   :undoc-members:
   :show-inheritance:

JSON-RPC 2.0
-------------

govmcp 协议层基于 JSON-RPC 2.0 规范，支持以下方法：

* ``tools/list`` - 列出所有可用工具
* ``tools/call`` - 调用指定工具
* ``initialize`` - 初始化连接
* ``ping`` - 心跳检测

消息格式
~~~~~~~~

请求格式：

.. code-block:: json

   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/list",
     "params": {}
   }

响应格式：

.. code-block:: json

   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "tools": [...]
     }
   }

错误格式：

.. code-block:: json

   {
     "jsonrpc": "2.0",
     "id": 1,
     "error": {
       "code": -32600,
       "message": "Invalid Request"
     }
   }
