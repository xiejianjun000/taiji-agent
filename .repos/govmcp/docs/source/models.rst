大模型适配模块
==============

.. automodule:: govmcp.models
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: govmcp.models.registry.ModelRegistry
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: govmcp.models.registry.ModelConfig
   :members:
   :undoc-members:
   :show-inheritance:

支持的模型
----------

govmcp 支持多种国产大模型，以下是当前支持的模型列表：

+---------------------------+------------------+----------------------------+
| 厂商                      | 模型             | 适配器                     |
+===========================+==================+============================+
| 百度                      | ERNIE Bot        | :doc:`api/govmcp.models.. |
|                          |                  | adapters.wenxin`          |
+---------------------------+------------------+----------------------------+
| 阿里                      | Qwen Turbo       | :doc:`api/govmcp.models.. |
|                          |                  | adapters.qwen`            |
+---------------------------+------------------+----------------------------+
| 字节跳动                  | Doubao Pro       | :doc:`api/govmcp.models.. |
|                          |                  | adapters.doubao`         |
+---------------------------+------------------+----------------------------+
| 腾讯                      | Hunyuan          | :doc:`api/govmcp.models.. |
|                          |                  | adapters.hunyuan`         |
+---------------------------+------------------+----------------------------+
| 智谱 AI                   | GLM-4            | :doc:`api/govmcp.models.. |
|                          |                  | adapters.zhipu`           |
+---------------------------+------------------+----------------------------+
| 科大讯飞                  | Spark V3         | :doc:`api/govmcp.models.. |
|                          |                  | adapters.spark`           |
+---------------------------+------------------+----------------------------+
| 商汤                      | Baichuan         | :doc:`api/govmcp.models.. |
|                          |                  | adapters.baichuan`        |
+---------------------------+------------------+----------------------------+
| 月之暗面                  | Moonshot V1      | :doc:`api/govmcp.models.. |
|                          |                  | adapters.moonshot`        |
+---------------------------+------------------+----------------------------+
| MiniMax                   | ABAB6            | :doc:`api/govmcp.models.. |
|                          |                  | adapters.minimax`         |
+---------------------------+------------------+----------------------------+
| 华为                      | Pangu VIP        | :doc:`api/govmcp.models.. |
|                          |                  | adapters.pangu`           |
+---------------------------+------------------+----------------------------+

基础适配器
----------

.. autoclass:: govmcp.models.adapters.base.BaseAdapter
   :members:
   :undoc-members:
   :show-inheritance:

使用示例
~~~~~~~~

.. code-block:: python

   from govmcp.models import register_model, get_model

   register_model("qwen-turbo", {
       "api_key": "your-api-key",
       "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
   })

   model = get_model("qwen-turbo")
   response = model.chat([
       {"role": "user", "content": "你好"}
   ])
