工具模块
========

.. automodule:: govmcp.tools
   :members:
   :undoc-members:
   :show-inheritance:

工具注册中心
------------

.. autoclass:: govmcp.tools.registry.ToolRegistry
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: govmcp.tools.registry.ToolInfo
   :members:
   :undoc-members:
   :show-inheritance:

govmcp_tool 装饰器
------------------

.. autofunction:: govmcp.tools.registry.govmcp_tool

使用示例
~~~~~~~~

.. code-block:: python

   from govmcp import govmcp_tool

   @govmcp_tool(
       name="calculate",
       description="执行数学计算",
       approval_required=True
   )
   def calculate(a: int, b: int, operation: str = "add") -> dict:
       if operation == "add":
           return {"result": a + b}
       elif operation == "sub":
           return {"result": a - b}
       return {"error": "Unknown operation"}

政务工具集
----------

govmcp 包含丰富的政务工具集，覆盖以下领域：

* **市民服务**：身份证、户籍、社保、医保、公积金等
* **企业服务**：工商注册、税务、许可证、知识产权等
* **碳排放**：碳排放数据录入、配额查询、碳交易等
* **环境监测**：空气质量、水质、土壤污染、噪声监测等
* **智慧城市**：交通控制、停车、路灯、水电气暖管理、养老、医疗预约等
* **审批工作流**：工作流发起、进度查询、评论、会签、转派等

详细工具列表请参考 API 文档。
