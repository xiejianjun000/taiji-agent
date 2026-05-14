# GovMCP 仓库深度分析报告

> 分析日期: 2026-05-14
> 版本: v1.0.0
> 项目路径: `/Users/mac/Documents/谢建军/taiji-agent/.repos/govmcp/`

---

## 目录

1. [SM4 加密：本地-政务云同步通道设计](#1-sm4-加密本地-政务云同步通道设计)
2. [审批工作流：与 Harness Human-in-the-Loop 对接](#2-审批工作流与-harness-human-in-the-loop-对接)
3. [审计链：不可篡改机制分析](#3-审计链不可篡改机制分析)
4. [政务工具：复用与定制分析](#4-政务工具复用与定制分析)
5. [LLM 适配器：11个国产LLM 统一接口定义](#5-llm-适配器11个国产llm-统一接口定义)
6. [与 Harness 集成：GovMCP 作为 Plugin 接入方案](#6-与-harness-集成govmcp-作为-plugin-接入方案)

---

## 1. SM4 加密：本地-政务云同步通道设计

### 1.1 基础密码学能力（`govmcp/crypto/sm.py`）

GovMCP 完整实现了国密 SM3/SM4 算法（纯软件参考实现，含 `gmssl` 可选依赖硬件加速）：

| 算法 | 标准 | 实现内容 | 文件 |
|------|------|----------|------|
| **SM3** | GB/T 32905-2016 | 256位哈希，SM3初始IV、消息扩展、64轮压缩函数 | `sm.py` 19-128行 |
| **SM4-ECB** | GB/T 32907-2016 | 128位分组，32轮密钥扩展 + 32轮加密/解密 | `sm.py` 460-538行 |
| **SM4-CBC** | — | CBC模式 + PKCS7填充 | `sm.py` 588-663行 |
| **SM2** | GB/T 32918-2016 | 密钥生成、加密/解密、签名/验签、ECDH密钥协商 | `sm2.py` 全文 |
| **KDF** | SM2规范 | 基于SM3的密钥派生函数 | `sm2.py` 125-155行 |

### 1.2 同步通道加密协议设计

基于 GovMCP 现有密码学原语，本地-政务云同步通道建议采用以下协议架构：

```
┌─────────────────────┐            SM2 ECDH 密钥协商         ┌─────────────────────┐
│   本地 Agent         │◄═══════════════════════════════════►│   政务云 MCP Server │
│   (taiji-agent)      │           Session Key: K_session     │   (govmcp Server)   │
└────────┬────────────┘                                      └────────┬────────────┘
         │                                                             │
         │  SM4-CBC(K_session, IV, {JSON-RPC payload}) + SM3 MAC       │
         │◄══════════════════════════════════════════════════════════►  │
         │                                                             │
         │  每条消息: base64(SM4-CBC(JSON)) + "|" + SM3(ciphertext)   │
         │                                                             │
```

**协议步骤**：

1. **密钥协商阶段**：
   - 双方各生成 SM2 密钥对 (`generate_sm2_keypair()`)
   - 交换公钥后，计算 ECDH 共享秘密 (`sm2_calculate_shared_secret()`)
   - 通过 KDF 派生会话密钥 K_session (`sm2_derive_key()`)

2. **消息传输阶段**：
   - 每条消息使用 SM4-CBC 加密 (`sm4_cbc_encrypt()`)
   - 每次加密使用随机 IV（`generate_sm4_iv()`）
   - 密文 Base64 编码后传输
   - 消息头附加 SM3 完整性校验

3. **GovMCP 现有加密传输支持**：
   - `GovMCPServer(crypto_enabled=True)`
   - `_read_message()` (354行) 和 `_write_message()` (373行) 已内置 SM4 加解密支持
   - `_mcp_sm3_verify` 方法 (580行) 提供 SM3 验证的 JSON-RPC 扩展

### 1.3 关键实现代码片段

```python
# GovMCP Server 初始化加密
server = GovMCPServer("taiji-govmcp", "1.0.0", crypto_enabled=True, sm4_key=derived_key)

# 消息写入（自动 SM4 加密 + SM3 哈希）
def _write_message(self, message):
    payload_str = _json_serialize(message)
    message["_sm3"] = sm3_hash(payload_str.encode("utf-8"))  # SM3 完整性
    output = _json_serialize(message)
    if self.crypto_enabled:
        padded = _pkcs7_pad(output.encode("utf-8"))
        ciphertext = sm4_encrypt(padded, self.sm4_key)       # SM4 加密
        output = base64.b64encode(ciphertext).decode("ascii")
```

### 1.4 安全性保障

- **传输加密**：会话级 SM4-CBC，每次 IV 独立
- **完整性**：每条消息带 SM3 哈希，`_verify_inbound_sm3()` 自动验证
- **密钥协商**：SM2 ECDH 提供前向安全性（PFS）
- **防重放**：消息中包含时间戳 + 序列号

---

## 2. 审批工作流：与 Harness Human-in-the-Loop 对接

### 2.1 GovMCP 审批工作流架构

GovMCP 在三个层面提供审批能力：

#### 2.1.1 审批核心引擎（`govmcp/server/approval.py`）

`ApprovalFlow` 类实现多级审批链：

```python
class ApprovalFlow:
    """
    多级审批工作流。按 approvers 列表顺序逐级审批。
    支持全局超时控制，超时后根据 auto_approve_on_timeout 决定行为。
    可选关联 AuditChain 实例，审批动作自动追加审计记录。
    """
```

**核心状态机**：
```
PENDING → [approve() → APPROVED] or [reject() → REJECTED] or [skip() → SKIPPED]
     ↕                                                    
[timeout → TIMEOUT → auto_approve(或auto_reject)]
```

**关键特性**：
- `approve(approver, comment)` - 当前级别审批通过
- `reject(approver, comment)` - 当前级别审批拒绝（终止流程）
- `skip(comment)` - 跳过当前级别（审批人不可用时）
- `_handle_timeout()` - 超时自动通过/拒绝
- `_record_audit()` - 自动追加审计链记录

#### 2.1.2 审批工具层（`govmcp/tools/government/approval_workflow.py`）

提供 15 个 MCP 工具，覆盖完整审批生命周期：

| 工具 | 功能 | 备注 |
|------|------|------|
| `initiate_approval_workflow` | 发起审批流程 | 含工作流类型、业务数据 |
| `query_approval_progress` | 查询审批进度 | 多级流程图 |
| `submit_approval_comment` | 提交审批意见 | 同意/不同意/条件同意 |
| `handle_approval_counter_sign` | 审批加签 | 增加临时节点 |
| `handle_approval_transfer` | 审批改签 | 更换审批人 |
| `handle_approval_joint_sign` | 审批会签 | 多人同时审批 |
| `handle_approval_suspend_resume` | 挂起/恢复 | - |
| `handle_approval_delegation` | 委托代理 | 设置代理人 |
| `query_approval_warning` | 时限预警 | 超时提醒 |
| `query_approval_statistics` | 统计分析 | 通过率、平均时长 |
| `manage_approval_archive` | 归档管理 | 归档/解档 |
| `configure_approval_permission` | 权限配置 | 角色级别金额限制 |
| `manage_approval_template` | 模板管理 | 创建/修改 |
| `apply_approval_digital_signature` | 电子签章 | SM3哈希关联 |
| `generate_approval_document` | 文书生成 | 审批表/批复函 |

#### 2.1.3 协议层审批钩子（`govmcp/protocol/server.py`）

```python
def set_approval_handler(self, handler: Callable[[str, dict[str, Any]], bool]):
    """设置审批处理器。"""
    self._approval_handler = handler

def _check_approval(self, tool_name, params):
    """检查工具调用是否需要审批。"""
    if self._approval_handler is None:
        return True
    return self._approval_handler(tool_name, params)
```

`_mcp_tools_call()` 中调用 `_check_approval()`，若返回 False 则抛出 `PermissionError`。

### 2.2 Harness Human-in-the-Loop 对接方案

Harness 平台提供 Step Group + Approval Step 两种人工审批模式。GovMCP 可通过以下方式对接：

#### 方案：GovMCP 作为外部审批服务

```
┌────────────────────────────────────────────────────────────┐
│  Harness Pipeline                                           │
│  ┌──────────────────────────────────────────┐              │
│  │ Step: Deploy                              │              │
│  │ Step: Harness Approval (HTTP Webhook)     │◄────┐       │
│  │   ↓ trigger                               │     │       │
│  └──────────────────────────────────────────┘     │       │
│                                                    │       │
└────────────────────────────────────────────────────┘       │
                                                              │
┌────────────────────────────────────────────────────┐       │
│  GovMCP Server                                       │     │
│  ┌──────────────────────────────────────────────┐   │     │
│  │ tools/approval_workflow:                     │   │     │
│  │   initiate_approval_workflow()  ─────────────┼───┘     │
│  │   submit_approval_comment()  ◄──────────────┼───┐     │
│  │   query_approval_progress()  ───────────────┼───┘     │
│  │                                              │         │
│  │ ApprovalFlow Engine                          │         │
│  │   - 多级审批链                               │         │
│  │   - 超时自动拒绝/通过                        │         │
│  │   - 审计链自动记录                           │         │
│  └──────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────┘
```

#### 接口设计

**A. Harness Approval Step → GovMCP (Webhook 触发审批)**

```
POST /mcp HTTP/1.1
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "initiate_approval_workflow",
    "arguments": {
      "workflow_name": "Harness-Deploy-Approval-WF-001",
      "applicant_name": "harness-pipeline",
      "applicant_department": "DevOps",
      "workflow_type": "合同",
      "business_data": {
        "pipeline_id": "pipeline-xyz",
        "execution_id": "exec-123",
        "target_env": "production",
        "artifact_version": "v2.3.1"
      }
    }
  },
  "id": 1
}
```

**B. Harness 轮询审批状态**

```
POST /mcp HTTP/1.1
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "query_approval_progress",
    "arguments": {
      "workflow_id": "WF20260513001"
    }
  },
  "id": 2
}
```

**C. GovMCP → Harness (回调通知)**

审批通过/拒绝后，GovMCP 回调 Harness Webhook URL（需扩展）：
```
POST {harness_webhook_url}
{
  "workflow_id": "WF20260513001",
  "status": "approved",
  "action": "同意",
  "comment": "已审核通过，允许部署到生产环境",
  "approver": "张XX",
  "timestamp": "2026-05-14 10:30:00"
}
```

#### 集成点汇总

| 组件 | 集成方式 | 状态 |
|------|----------|------|
| ApprovalFlow 核心引擎 | 直接调用 ApprovalFlow 类 | ✅ 可用 |
| 审批工具 (MCP tools) | JSON-RPC over HTTP/WebSocket | ✅ 可用 |
| `_check_approval()` 钩子 | `server.set_approval_handler()` | ✅ 可用 |
| 审批->审计链 | ApprovalFlow 自动关联 AuditChain | ✅ 可用 |
| Harness 回调 | 需在 `submit_approval_comment` 中扩展回调逻辑 | ⚠️ 待开发 |

---

## 3. 审计链：不可篡改机制分析

### 3.1 实现分析（`govmcp/crypto/audit.py`）

`AuditChain` 类实现基于 SM3 哈希链的防篡改审计：

```python
@dataclass
class AuditEntry:
    id: int                    # 顺序ID
    timestamp: float           # Unix 时间戳
    operation: str             # 操作类型
    operator: str              # 操作者
    input_hash: str            # 输入数据的SM3哈希
    output_hash: str           # 输出数据的SM3哈希
    approval_status: str       # 审批状态
    prev_hash: str             # 前驱记录的current_hash
    current_hash: str          # 本记录的哈希
```

### 3.2 哈希链计算

```
Genesis:  prev_hash = "0000...0000" (64个'0')
          current_hash = SM3(prev_hash || timestamp || operation || input_hash || output_hash)

Record N: prev_hash = Record(N-1).current_hash
          current_hash = SM3(prev_hash || timestamp || operation || input_hash || output_hash)
```

### 3.3 验证机制

`verify()` 方法 (107-147行) 提供三重校验：

```python
def verify(self) -> bool:
    expected_prev = GENESIS_PREV_HASH  # "0" * 64

    for entry in self.entries:
        # ① 前驱哈希链校验
        if entry.prev_hash != expected_prev:
            return False

        # ② 记录ID连续性校验
        if entry.id != expected_id:
            return False

        # ③ 当前哈希重计算校验
        computed_hash = sm3_hash(hash_source.encode("utf-8"))
        if computed_hash != entry.current_hash:
            return False

        expected_prev = entry.current_hash

    return True
```

### 3.4 不可篡改性保证

| 攻击方式 | 防护机制 |
|----------|----------|
| 修改某条记录内容 | ③ 哈希重算失败 |
| 插入伪造记录 | ① 前驱哈希不匹配 或 ② ID连续性中断 |
| 删除某条记录 | ① 后续记录的 prev_hash 指向错误的前驱 |
| 重排记录顺序 | ② ID 连续性破坏 |
| 修改 Genesis | ① 创世块 prev_hash 必须为 64 个 '0' |
| 日期回滚 | ③ 时间戳参与哈希计算，任何修改导致重算失败 |

### 3.5 与审批工作流的集成

`ApprovalFlow` 自动关联 `AuditChain`：

```python
def _record_audit(self, step):
    if self._audit_chain is None:
        return
    self._audit_chain.add_entry(
        operation="approval_step",
        operator=step.approver,
        input_data=f"level={step.level}".encode(),
        output_data=step.comment.encode(),
        approval_status=step.status.value,
    )
```

### 3.6 当前局限性

1. **内存存储**：审计链目前存储在内存中 (`self.entries: list`)，无持久化
2. **无分布式共识**：单机哈希链，需外部机制（如区块链/数据库事务）实现分布式的不可篡改
3. **未加密存储**：审计记录以明文存储，建议对敏感字段使用 SM4 加密

---

## 4. 政务工具：复用与定制分析

### 4.1 现有工具概览

GovMCP 提供 6 大类政务工具模块：

| 模块 | 文件 | 工具数量 | 覆盖领域 |
|------|------|----------|----------|
| **审批工作流** | `approval_workflow.py` | 15 | 发起/查询/意见/加签/改签/会签/委托/归档/模板 |
| **市民服务** | `citizen_service.py` | ~20 | 身份证/户籍/社保/医保/公积金/交通/不动产 |
| **企业服务** | `enterprise_service.py` | ~15 | 工商登记/税务/许可证/知识产权/政府采购 |
| **环保监测** | `environmental.py` | 16 | 空气/水质/土壤/噪声/固废/辐射/排污许可/环评/处罚/清洁生产 |
| **智慧城市** | `smart_city.py` | ~15 | 交通信号/停车/水务/社区/养老/应急指挥 |
| **碳排放管理** | `carbon_emission.py` | ~10 | 碳排放录入/碳交易/碳足迹/碳中和追踪 |

**总计约 90+ 个 MCP 政府工具**。

### 4.2 可直接复用的部分

| 模块 | 可复用工具 | 复用场景 |
|------|-----------|----------|
| **审批工作流** | `initiate_approval_workflow`, `submit_approval_comment`, `query_approval_progress`, `handle_approval_counter_sign`, `handle_approval_transfer`, `handle_approval_joint_sign`, `configure_approval_permission`, `manage_approval_template`, `apply_approval_digital_signature` | 所有需要审批的场景（taiji-agent 的所有 Human-in-the-Loop 操作） |
| **审批业务** | `query_approval_statistics`, `query_approval_warning`, `manage_approval_archive` | 审批管理和运营 |
| **碳排放** | `calculate_carbon_footprint`, `query_carbon_trade_price` | 环境监测和报告 |
| **模板管理** | `manage_approval_template` | 审批流程模板可直接对接业务表单 |

### 4.3 需要为生态环境场景定制的部分

| 模块 | 定制内容 | 原因 |
|------|----------|------|
| **审批工作流** | 扩展 `initiate_approval_workflow` 的 `workflow_type` | 增加生态环境专用流程类型（环评审批、排污许可、危废转移等） |
| **审批权限** | 定制 `configure_approval_permission` | 生态环境部门有独特的角色-权限模型（环保局、监测站、执法队） |
| **环保监测** | `query_air_quality`, `query_water_quality`, `query_soil_pollution` | 需连接真实物联网数据源，而非模拟数据 |
| **碳排放** | `input_carbon_emission_data` | 需要与真实企业碳核算系统对接 |
| **智慧城市** | `control_smart_traffic_light` | 需与城市物联网平台 API 对接 |
| **电子签章** | `apply_approval_digital_signature` | 需对接生态环境部认可的 CA 机构 |

### 4.4 建议的定制优先级

```
高优先级（可直接用于 MVP）：
  1. 审批工作流 → 对接 Harness Human-in-the-Loop
  2. 审计链 → 所有审批和关键操作
  3. 碳排放计算 → 基础碳核算能力

中优先级（需要数据源对接）：
  4. 环保监测 → 连接 IoT 数据平台
  5. 市民/企业服务 → 对接政务数据共享平台

低优先级（按需启用）：
  6. 智慧城市 → 需城市级基础设施
```

---

## 5. LLM 适配器：11个国产LLM 统一接口定义

### 5.1 适配器基类（`govmcp/models/adapters/base.py`）

所有适配器继承自 `LLMAdapter` 抽象基类，定义三个核心抽象方法：

```python
class LLMAdapter(ABC):
    @abstractmethod
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """发送对话请求，返回回复文本"""
        pass

    @abstractmethod
    def stream_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> Iterator[str]:
        """发送流式对话请求，逐块返回"""
        pass

    @abstractmethod
    def get_embedding(self, text: str, **kwargs: Any) -> list[float]:
        """获取文本嵌入向量"""
        pass
```

### 5.2 公共接口

| 方法 | 类型 | 描述 |
|------|------|------|
| `chat()` | abstract | 标准对话，返回完整文本 |
| `stream_chat()` | abstract | 流式对话，返回文本迭代器 |
| `get_embedding()` | abstract | 文本嵌入向量 |
| `format_messages()` | concrete | 格式化消息（system/user/history） |
| `build_request_params()` | concrete | 构建请求参数（model/messages/temperature...） |
| `supports_streaming()` | concrete | 是否支持流式输出 |
| `supports_function_call()` | concrete | 是否支持函数调用 |
| `supports_vision()` | concrete | 是否支持视觉 |
| `supports_embedding()` | concrete | 是否支持文本嵌入 |

### 5.3 11个独立适配器 + 1个通用适配器

| # | 适配器 | 文件 | 覆盖模型 | 厂商 |
|---|--------|------|----------|------|
| 1 | `WenxinAdapter` | `wenxin.py` | ernie-4.0/3.5/3.0/bot | 百度文心 |
| 2 | `QwenAdapter` | `qwen.py` | qwen-turbo/plus/max/long/7b/14b/72b | 阿里通义千问 |
| 3 | `ZhipuAdapter` | `zhipu.py` | glm-4/4-plus/3-turbo, chatglm-6b/2/3 | 智谱GLM |
| 4 | `SparkAdapter` | `spark.py` | spark-3.5/4.0/lite | 科大讯飞星火 |
| 5 | `HunyuanAdapter` | `hunyuan.py` | hunyuan-lite/pro/standard | 腾讯混元 |
| 6 | `PanguAdapter` | `pangu.py` | pangu-alpha/chat | 华为盘古 |
| 7 | `DoubaoAdapter` | `doubao.py` | doubao-pro/lite | 字节豆包 |
| 8 | `MinimaxAdapter` | `minimax.py` | minimax-abab5/abab6/chat | MiniMax |
| 9 | `MoonshotAdapter` | `moonshot.py` | kimi-chat/pro | 月之暗面Kimi |
| 10 | `BaichuanAdapter` | `baichuan.py` | baichuan4/7b/13b | 百川智能 |
| 11 | `OthersAdapter` | `others.py` | 9个厂商统一处理 | 商汤/360/拓世/新华三/出门问问/书生/聆心/天翼云/联通 |
| — | `LLMAdapter` | `base.py` | 抽象基类 | — |

### 5.4 模型注册表（`govmcp/models/registry.py`）

`ModelRegistry` 是单例模式，管理 **48 个内置国产大模型** 的注册和适配器工厂：

```python
class ModelRegistry:
    """单例注册表，管理48个国产大模型"""
    
    def get_adapter(model_id: str) -> LLMAdapter:
        """自动匹配适配器类并返回实例"""
        provider = LLMProvider.from_model_id(model_id)
        adapter_name = provider.adapter_name  # 如 "qwen", "zhipu"
        adapter_cls = getattr(models_module, f"{adapter_name.title()}Adapter")
        return adapter_cls(config)
```

### 5.5 适配器实现模式

以 `QwenAdapter` 为例，实现遵循统一模式：

```python
class QwenAdapter(LLMAdapter):
    def __init__(self, config, api_key=None):
        super().__init__(config)
        self.api_key = api_key or ""

    def _build_headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def chat(self, messages, **kwargs):
        params = self.build_request_params(messages, **kwargs)
        response = requests.post(self.api_base, headers=self._build_headers(), json=params)
        result = response.json()
        return result["choices"][0]["message"]["content"]

    def stream_chat(self, messages, **kwargs):
        params = self.build_request_params(messages, stream=True, **kwargs)
        response = requests.post(..., stream=True)
        for line in response.iter_lines():
            yield chunk["choices"][0]["delta"]["content"]
```

---

## 6. 与 Harness 集成：GovMCP 作为 Plugin 接入方案

### 6.1 架构总图

```
┌─────────────────────────────────────────────────────────────┐
│                        Harness Platform                       │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐   │
│  │ Pipeline     │  │ Template    │  │ Connector         │   │
│  │ (Stage Steps)│  │ (GovMCP WF) │  │ (HTTP/SSE/WS)    │   │
│  └──────┬───────┘  └──────┘──────┘  └────────┬──────────┘   │
│         │                                      │              │
└─────────┼──────────────────────────────────────┼──────────────┘
          │  JSON-RPC 2.0 over HTTP/SSE/WS       │
          ▼                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    GovMCP Server                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Transport Layer: Stdio / WebSocket / HTTP / SSE       │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │  Security Layer: SM4-CBC 加密 + SM3 完整性             │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │  Protocol Layer (GovMCPServer):                        │   │
│  │   • tools/list → 90+ 政务 MCP 工具                     │   │
│  │   • tools/call → 含 _check_approval() 审批检查          │   │
│  │   • tasks/create → 异步任务 + SSE 推送                  │   │
│  │   • authorization/check → OAuth 2.0 鉴权               │   │
│  │   • sm3/verify → 数据完整性验证                        │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │  Business Layer:                                        │   │
│  │   • ApprovalFlow → 多级审批链 + AuditChain              │   │
│  │   • 48 国产 LLM ModelRegistry + 11 适配器               │   │
│  │   • 审批工具 / 环保监测 / 碳排放 / 智慧城市             │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 接入模式对比

| 集成模式 | 传输协议 | 适用场景 | 实现复杂度 |
|----------|----------|----------|------------|
| **Harness HTTP Step** | HTTP JSON-RPC | 审批工作流、工具调用 | 低（直接 HTTP POST） |
| **Harness SSE Step** | SSE Event Stream | 异步任务状态推送 | 中（需要 SSE 处理） |
| **Harness WebSocket** | WebSocket | 实时审批交互 | 中（WebSocket 长连接） |
| **Harness Custom Plugin** | SDK 集成 | 深度集成到 Harness 内部 | 高（需要开发插件） |

### 6.3 GovMCPServer 核心能力矩阵

GovMCPServer 已原生支持的标准 MCP + GovMCP 扩展方法：

```python
def _dispatch(self, method, params):
    handlers = {
        # 标准 MCP 方法
        "initialize":             # 握手 + 能力声明
        "tools/list":             # 列出 90+ 政务工具
        "tools/call":             # 调用工具（含审批检查）
        "resources/list":         # 列出政务数据资源
        "resources/read":         # 读取政务数据资源
        "prompts/list":           # 列出提示模板
        "prompts/get":            # 获取提示模板

        # GovMCP 扩展方法
        "models/list":            # 列出 48 个信创模型
        "sm3/verify":             # SM3 完整性验证
        "tasks/create":           # 创建异步任务
        "tasks/status":           # 查询任务状态
        "tasks/result":           # 获取任务结果
        "tasks/cancel":           # 取消任务
        "tasks/list":             # 列出所有任务
        "tasks/subscribe":        # SSE 订阅任务更新
        "sampling/createMessage": # 采样创建消息
        "elicitation/create":     # 创建用户交互请求
        "elicitation/respond":    # 响应用户交互
        "authorization/check":    # OAuth 2.0 授权检查
    }
```

### 6.4 Harness Plugin 配置示例

```yaml
# harness-govmcp-plugin.yaml
connector:
  name: "GovMCP Server"
  type: "HttpHelmConnector"
  url: "http://govmcp-server:8080/mcp"
  headers:
    Content-Type: "application/json"
    Authorization: "Bearer ${GOVMCP_API_KEY}"

pipeline:
  - stage:
      name: "政务审批"
      steps:
        - step:
            type: "ShellScript"
            name: "发起审批"
            shell: Bash
            script: |
              curl -X POST $GOVMCP_URL \
                -H "Content-Type: application/json" \
                -d '{
                  "jsonrpc": "2.0",
                  "method": "tools/call",
                  "params": {
                    "name": "initiate_approval_workflow",
                    "arguments": {
                      "workflow_name": "审批申请",
                      "applicant_name": "harness",
                      "workflow_type": "采购",
                      "business_data": {
                        "pipeline_id": "${pipeline.sequenceId}"
                      }
                    }
                  }
                }'
```

### 6.5 启动 GovMCPServer

```python
# 方式 1: Stdio 模式（适用于 Docker 容器内）
server = GovMCPServer("taiji-govmcp", "1.0.0",
                      crypto_enabled=True,
                      sm4_key=os.urandom(16))
server.run()

# 方式 2: HTTPServer 模式（适用于 Harness HTTP Connector）
asyncio.run(server.run_http(host="0.0.0.0", port=8080, auth_token="xxx"))

# 方式 3: WebSocket 模式（适用于实时通信）
asyncio.run(server.run_websocket(host="0.0.0.0", port=8080))
```

---

## 附录 A：项目结构总览

```
govmcp/
├── govmcp/
│   ├── __init__.py
│   ├── crypto/                     # 国密加密模块
│   │   ├── __init__.py             #   导出SM2/SM3/SM4/AuditChain
│   │   ├── sm.py                   #   SM3哈希 + SM4对称加密
│   │   ├── sm2.py                  #   SM2非对称加密/签名/ECDH
│   │   └── audit.py                #   不可篡改审计链
│   ├── protocol/                   # MCP协议层
│   │   ├── server.py               #   GovMCPServer (JSON-RPC 2.0)
│   │   ├── authorization.py        #   OAuth 2.0授权 + 细粒度权限
│   │   ├── tasks.py                #   异步任务 + SSE推送
│   │   ├── sampling.py             #   采样
│   │   ├── elicitation.py          #   用户交互请求
│   │   ├── websocket_server.py     #   WebSocket传输层
│   │   └── http_server.py          #   HTTP/SSE传输层
│   ├── tools/                      # 政务工具
│   │   ├── registry.py             #   工具注册中心 + govmcp_tool装饰器
│   │   └── government/
│   │       ├── approval_workflow.py   15 个审批工具
│   │       ├── citizen_service.py     ~20 个市民服务工具
│   │       ├── enterprise_service.py  ~15 个企业服务工具
│   │       ├── environmental.py       16 个环保监测工具
│   │       ├── smart_city.py          ~15 个智慧城市工具
│   │       └── carbon_emission.py     ~10 个碳排放工具
│   ├── models/                     # LLM模型管理
│   │   ├── registry.py             #   48模型注册表 (ModelRegistry单例)
│   │   └── adapters/
│   │       ├── base.py             #   LLMAdapter抽象基类
│   │       ├── wenxin.py           #   百度文心
│   │       ├── qwen.py             #   阿里通义千问
│   │       ├── zhipu.py            #   智谱GLM
│   │       ├── spark.py            #   科大讯飞星火
│   │       ├── hunyuan.py          #   腾讯混元
│   │       ├── pangu.py            #   华为盘古
│   │       ├── doubao.py           #   字节豆包
│   │       ├── minimax.py          #   MiniMax
│   │       ├── moonshot.py         #   月之暗面Kimi
│   │       ├── baichuan.py         #   百川智能
│   │       └── others.py           #   9个厂商统一处理
│   └── server/                     # 审批服务器
│       └── approval.py             #   ApprovalFlow审批工作流引擎
├── docs/zh/                        # 中文文档 (30+ 篇)
├── tests/                          # 测试
├── pyproject.toml                  # 项目配置
└── ARCHITECTURE.md                 # 架构文档
```

## 附录 B：依赖清单

```toml
# 核心依赖
dependencies = ["cryptography>=41.0"]

# 可选依赖
full = ["gmssl>=3.2"]              # 国密硬件加速
ws = ["websockets>=12.0"]          # WebSocket传输
http = ["aiohttp>=3.9.0"]          # HTTP/SSE传输
dev = ["pytest>=7.0", "ruff>=0.9.0", "mypy>=1.2.0"]
```

## 附录 C：关键文件引用

| 内容 | 文件路径 | 行数 |
|------|----------|------|
| SM4-CBC 加密 | `govmcp/crypto/sm.py` | 588-663 |
| SM2 ECDH 密钥协商 | `govmcp/crypto/sm2.py` | 550-589 |
| 审计哈希链 | `govmcp/crypto/audit.py` | 39-187 |
| 审批工作流引擎 | `govmcp/server/approval.py` | 48-387 |
| GovMCPServer 协议层 | `govmcp/protocol/server.py` | 165-929 |
| 审批钩子 | `govmcp/protocol/server.py` | 341-352 |
| OAuth 2.0 授权 | `govmcp/protocol/authorization.py` | 210-799 |
| 异步任务 SSE | `govmcp/protocol/tasks.py` | 140-636 |
| LLM 适配器基类 | `govmcp/models/adapters/base.py` | 16-192 |
| 48模型注册表 | `govmcp/models/registry.py` | 149-933 |
| 审批工具 (15个) | `govmcp/tools/government/approval_workflow.py` | 1-580 |
| 环保监测工具 (16个) | `govmcp/tools/government/environmental.py` | 1-532 |
| 工具注册中心 | `govmcp/tools/registry.py` | 1-329 |
| 碳排放工具 | `govmcp/tools/government/carbon_emission.py` | 1-60+ |
