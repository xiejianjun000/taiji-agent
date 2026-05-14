# govmcp 高级指南

> 深入了解 govmcp 的高级特性和最佳实践

---

## 目录

- [自定义审批流程](#自定义审批流程)
- [审计链高级应用](#审计链高级应用)
- [国密加密进阶](#国密加密进阶)
- [工具注册中心](#工具注册中心)
- [模型适配器](#模型适配器)
- [协议层扩展](#协议层扩展)
- [性能优化](#性能优化)
- [最佳实践](#最佳实践)

---

## 自定义审批流程

### 动态审批链

```python
from govmcp import ApprovalFlow, ApprovalStatus
from typing import List

class DynamicApprovalFlow:
    """支持动态调整的审批流程"""

    def __init__(self, base_approvers: List[str]):
        self.flow = ApprovalFlow(base_approvers)
        self.delegation_rules = {}

    def add_delegation(self, from_approver: str, to_approver: str):
        """设置委托规则"""
        self.delegation_rules[from_approver] = to_approver

    def approve_with_delegation(self, approver: str, comment: str):
        """带委托的审批"""
        if approver in self.delegation_rules:
            actual_approver = self.delegation_rules[approver]
            print(f"{approver} 委托 {actual_approver} 审批")
            self.flow.approve(actual_approver, f"[委托] {comment}")
        else:
            self.flow.approve(approver, comment)

    def add_extra_approver(self, approver: str, position: str = "append"):
        """添加额外审批人"""
        if position == "append":
            self.flow.add_approver(approver)
        elif position == "prepend":
            self.flow.add_approver(approver, at_front=True)
        else:
            self.flow.insert_approver(approver, position)

# 使用示例
flow = DynamicApprovalFlow(["科长", "处长", "局长"])

# 设置委托
flow.add_delegation("处长", "副处长")

# 审批
flow.approve_with_delegation("处长", "因出差委托副处长审批")
```

### 条件审批

```python
from govmcp import ApprovalFlow
from decimal import Decimal

class ConditionalApprovalFlow(ApprovalFlow):
    """条件审批流程"""

    def __init__(self, approvers: list):
        super().__init__(approvers)
        self.rules = []

    def add_rule(self, condition: callable, action: str, approver: str):
        """添加审批规则"""
        self.rules.append({
            "condition": condition,
            "action": action,
            "approver": approver
        })

    def evaluate_rules(self, context: dict):
        """评估所有规则"""
        triggered_actions = []
        for rule in self.rules:
            if rule["condition"](context):
                triggered_actions.append({
                    "action": rule["action"],
                    "approver": rule["approver"]
                })
        return triggered_actions

# 使用示例
flow = ConditionalApprovalFlow(["主管"])

# 添加规则
flow.add_rule(
    condition=lambda ctx: ctx.get("amount", 0) > 100000,
    action="extra_review",
    approver="财务总监"
)

flow.add_rule(
    condition=lambda ctx: ctx.get("risk_level") == "high",
    action="compliance_check",
    approver="合规主管"
)

# 评估
context = {
    "amount": 150000,
    "risk_level": "high"
}
actions = flow.evaluate_rules(context)
print(f"触发的审批动作: {actions}")
```

### 并行审批与会签

```python
from govmcp import ApprovalFlow, ApprovalStatus
from concurrent.futures import ThreadPoolExecutor
import asyncio

class ParallelApprovalFlow:
    """并行审批流程"""

    def __init__(self, approvers: list):
        self.approvers = approvers
        self.approval_states = {a: None for a in approvers}
        self.require_all = True  # 是否需要全部通过

    def approve_parallel(self, approvers: list, comments: dict):
        """并行审批"""
        for approver in approvers:
            if approver in comments:
                self.approval_states[approver] = {
                    "status": ApprovalStatus.APPROVED,
                    "comment": comments[approver]
                }

    def is_complete(self) -> bool:
        """检查是否完成"""
        if self.require_all:
            return all(s is not None for s in self.approval_states.values())
        return any(s is not None for s in self.approval_states.values())

# 会签示例
class CountersignFlow:
    """会签审批"""

    def __init__(self, departments: list):
        self.departments = departments
        self.countersigns = {}

    def submit_countersign(self, department: str, approved: bool, comment: str):
        """提交会签意见"""
        self.countersigns[department] = {
            "approved": approved,
            "comment": comment
        }

    def is_all_countersigned(self) -> bool:
        """检查是否全部会签"""
        return len(self.countersigns) == len(self.departments)

    def get_result(self) -> dict:
        """获取会签结果"""
        if not self.is_all_countersigned():
            return {"status": "pending"}

        all_approved = all(c["approved"] for c in self.countersigns.values())
        return {
            "status": "approved" if all_approved else "rejected",
            "countersigns": self.countersigns
        }

# 使用示例
cs_flow = CountersignFlow(["财务部", "审计部", "法务部"])

cs_flow.submit_countersign("财务部", True, "财务审核通过")
cs_flow.submit_countersign("审计部", True, "审计审核通过")
cs_flow.submit_countersign("法务部", True, "法务审核通过")

result = cs_flow.get_result()
print(f"会签结果: {result}")
```

---

## 审计链高级应用

### 分层审计链

```python
from govmcp import AuditChain, sm3_hash

class HierarchicalAuditChain:
    """分层审计链"""

    def __init__(self):
        self.chains = {}  # 按类别分类的审计链
        self.root_chain = AuditChain()  # 根链

    def create_chain(self, category: str):
        """创建分类审计链"""
        self.chains[category] = AuditChain()

    def add_entry(self, category: str, action: str, operator: str,
                  input_data: bytes, output_data: bytes, result: str):
        """添加审计记录"""
        # 添加到分类链
        if category not in self.chains:
            self.create_chain(category)
        self.chains[category].add_entry(action, operator, input_data, output_data, result)

        # 添加到根链
        entry_hash = sm3_hash(f"{category}:{action}:{operator}".encode())
        self.root_chain.add_entry(action, operator, input_data, output_data, result)

    def verify_category(self, category: str) -> bool:
        """验证分类链"""
        if category not in self.chains:
            return False
        return self.chains[category].verify()

    def verify_all(self) -> dict:
        """验证所有链"""
        results = {"root": self.root_chain.verify()}
        for category, chain in self.chains.items():
            results[category] = chain.verify()
        return results

# 使用示例
hchain = HierarchicalAuditChain()

hchain.add_entry("finance", "transfer", "user_001",
                 b"amount:1000", b"success", "completed")
hchain.add_entry("approval", "approve", "manager_001",
                 b"request_id:123", b"approved", "approved")

results = hchain.verify_all()
print(f"验证结果: {results}")
```

### 审计链持久化

```python
import json
import sqlite3
from govmcp import AuditChain

class PersistentAuditChain(AuditChain):
    """持久化审计链"""

    def __init__(self, db_path: str = "audit.db"):
        super().__init__()
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain_id TEXT NOT NULL,
                action TEXT NOT NULL,
                operator TEXT NOT NULL,
                input_hash TEXT NOT NULL,
                output_hash TEXT NOT NULL,
                result TEXT NOT NULL,
                prev_hash TEXT,
                entry_hash TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save(self):
        """保存到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for entry in self.entries:
            cursor.execute("""
                INSERT INTO audit_entries
                (chain_id, action, operator, input_hash, output_hash,
                 result, prev_hash, entry_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.chain_id,
                entry["action"],
                entry["operator"],
                entry["input_hash"],
                entry["output_hash"],
                entry["result"],
                entry["prev_hash"],
                entry["entry_hash"]
            ))

        conn.commit()
        conn.close()

    @classmethod
    def load(cls, chain_id: str, db_path: str = "audit.db"):
        """从数据库加载"""
        chain = cls(db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT action, operator, input_hash, output_hash,
                   result, prev_hash, entry_hash
            FROM audit_entries
            WHERE chain_id = ?
            ORDER BY id
        """, (chain_id,))

        for row in cursor.fetchall():
            entry = {
                "action": row[0],
                "operator": row[1],
                "input_hash": row[2],
                "output_hash": row[3],
                "result": row[4],
                "prev_hash": row[5],
                "entry_hash": row[6]
            }
            chain.entries.append(entry)

        conn.close()
        return chain

# 使用示例
chain = PersistentAuditChain("production_audit.db")

chain.add_entry("document", "sign", "operator_001",
                b"doc_content", b"signed", "completed")

chain.save()

# 重新加载
loaded_chain = PersistentAuditChain.load("default")
print(f"加载记录数: {len(loaded_chain.entries)}")
```

---

## 国密加密进阶

### 密钥派生

```python
from govmcp.crypto.sm import sm3_kdf, sm3_hmac

class KeyDerivation:
    """密钥派生"""

    @staticmethod
    def derive_key(master_key: bytes, info: bytes, length: int = 32) -> bytes:
        """使用SM3 KDF派生密钥"""
        return sm3_kdf(master_key + info, length)

    @staticmethod
    def hmac(key: bytes, message: bytes) -> bytes:
        """SM3 HMAC"""
        return sm3_hmac(key, message)

# 使用示例
kd = KeyDerivation()

master = b"master_key_for_production"
info = b"encryption_key_derivation"

encryption_key = kd.derive_key(master, info, 32)
mac_key = kd.derive_key(master, info + b"_mac", 32)

print(f"派生加密密钥: {encryption_key.hex()}")
print(f"派生MAC密钥: {mac_key.hex()}")
```

### 密钥轮换

```python
from govmcp import sm4_encrypt, sm4_decrypt, generate_sm4_key
from cryptography.fernet import Fernet
import json

class KeyRotationManager:
    """密钥轮换管理器"""

    def __init__(self):
        self.current_key = generate_sm4_key()
        self.key_history = []  # 存储历史密钥用于解密

    def rotate_key(self):
        """轮换密钥"""
        self.key_history.append({
            "key": self.current_key,
            "rotated_at": "2025-05-13T10:00:00Z"
        })
        self.current_key = generate_sm4_key()
        print("密钥已轮换")

    def encrypt_with_current_key(self, data: bytes) -> dict:
        """使用当前密钥加密"""
        ciphertext = sm4_encrypt(data, self.current_key)
        return {
            "ciphertext": ciphertext,
            "key_version": len(self.key_history) + 1
        }

    def decrypt(self, encrypted_data: dict) -> bytes:
        """解密（尝试所有历史密钥）"""
        ciphertext = encrypted_data["ciphertext"]
        key_version = encrypted_data["key_version"]

        # 尝试当前密钥
        try:
            return sm4_decrypt(ciphertext, self.current_key)
        except:
            pass

        # 尝试历史密钥
        for history in reversed(self.key_history):
            try:
                return sm4_decrypt(ciphertext, history["key"])
            except:
                continue

        raise ValueError("无法解密，数据可能已损坏")

# 使用示例
manager = KeyRotationManager()

# 加密数据
encrypted = manager.encrypt_with_current_key(b"敏感政务数据")
print(f"加密版本: {encrypted['key_version']}")

# 解密
decrypted = manager.decrypt(encrypted)
print(f"解密结果: {decrypted}")
```

---

## 工具注册中心

### 自定义工具

```python
from govmcp.tools import ToolRegistry, govmcp_tool

# 获取注册中心实例
registry = ToolRegistry()

# 定义工具
@govmcp_tool(
    name="custom_carbon_query",
    description="查询企业碳排放数据",
    category="carbon_emission",
    input_schema={
        "type": "object",
        "properties": {
            "enterprise_id": {"type": "string"},
            "start_date": {"type": "string"},
            "end_date": {"type": "string"}
        },
        "required": ["enterprise_id"]
    }
)
def custom_carbon_query(enterprise_id: str, start_date: str = None,
                        end_date: str = None) -> dict:
    """自定义碳排放查询工具实现"""
    return {
        "enterprise_id": enterprise_id,
        "data": [
            {"date": "2025-01", "emissions": 100.5},
            {"date": "2025-02", "emissions": 95.3}
        ]
    }

# 注册工具
registry.register(custom_carbon_query)

# 列出所有工具
tools = registry.list_tools()
print(f"已注册工具数: {len(tools)}")

# 获取特定工具
tool = registry.get_tool("custom_carbon_query")
print(f"工具详情: {tool}")
```

### 工具中间件

```python
from govmcp.tools import ToolRegistry
from functools import wraps

def audit_middleware(func):
    """审计中间件"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[AUDIT] 调用工具: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[AUDIT] 工具执行完成: {func.__name__}")
        return result
    return wrapper

def retry_middleware(max_retries: int = 3):
    """重试中间件"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_retries - 1:
                        raise
                    print(f"重试 {i+1}/{max_retries}: {e}")
        return wrapper
    return decorator

# 应用中间件
registry = ToolRegistry()
registry.add_middleware(audit_middleware)
registry.add_middleware(retry_middleware(max_retries=3))
```

---

## 模型适配器

### 创建自定义适配器

```python
from govmcp.models.adapters.base import BaseModelAdapter

class CustomModelAdapter(BaseModelAdapter):
    """自定义模型适配器"""

    def __init__(self, api_key: str, base_url: str = None):
        super().__init__(model_name="custom-model")
        self.api_key = api_key
        self.base_url = base_url or "https://api.example.com"

    def chat(self, message: str, **kwargs) -> str:
        """发送聊天请求"""
        # 实现具体逻辑
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": message}]
        }
        # 发送请求...
        return "模型响应"

    def embed(self, text: str) -> list:
        """生成嵌入向量"""
        # 实现具体逻辑
        return [0.1, 0.2, 0.3]

    def validate_config(self) -> bool:
        """验证配置"""
        return bool(self.api_key)

# 注册适配器
from govmcp.models import ModelRegistry

registry = ModelRegistry()
registry.register_adapter("custom", CustomModelAdapter)

# 使用
adapter = registry.get_adapter("custom", api_key="xxx")
response = adapter.chat("你好")
```

---

## 协议层扩展

### 自定义消息处理器

```python
from govmcp.protocol.server import GovMCPServer, JSONRPCRequest, JSONRPCResponse

class CustomHandler:
    """自定义消息处理器"""

    def __init__(self, server: GovMCPServer):
        self.server = server

    def handle_batch_request(self, requests: list) -> list:
        """处理批量请求"""
        responses = []
        for req in requests:
            response = self.server.handle_message(req)
            responses.append(response)
        return responses

    def handle_notification(self, method: str, params: dict):
        """处理通知（无响应）"""
        if method == "shutdown":
            self.server.shutdown()
        elif method == "logging":
            self._handle_logging(params)

    def _handle_logging(self, params: dict):
        """处理日志通知"""
        level = params.get("level", "info")
        message = params.get("message", "")
        print(f"[{level.upper()}] {message}")
```

### WebSocket 传输层

```python
import asyncio
import websockets
from govmcp.protocol.server import GovMCPServer

class WebSocketServer:
    """WebSocket传输层"""

    def __init__(self, server: GovMCPServer, host: str = "0.0.0.0", port: int = 8765):
        self.server = server
        self.host = host
        self.port = port
        self.clients = set()

    async def handle_client(self, websocket, path):
        """处理客户端连接"""
        self.clients.add(websocket)
        try:
            async for message in websocket:
                # 处理消息
                response = self.server.handle_message(message)
                if response:
                    await websocket.send(response)
        finally:
            self.clients.remove(websocket)

    async def start(self):
        """启动服务器"""
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"WebSocket服务器启动: ws://{self.host}:{self.port}")
            await asyncio.Future()  # 运行永续

# 使用示例
server = GovMCPServer("ws-server", "1.0.0")
asyncio.run(WebSocketServer(server).start())
```

---

## 性能优化

### 连接池

```python
from govmcp.models import ModelRegistry
from queue import Queue
from threading import Lock

class ConnectionPool:
    """连接池"""

    def __init__(self, factory, min_size: int = 2, max_size: int = 10):
        self.factory = factory
        self.min_size = min_size
        self.max_size = max_size
        self.pool = Queue(maxsize=max_size)
        self.lock = Lock()
        self._init_connections()

    def _init_connections(self):
        """初始化连接"""
        for _ in range(self.min_size):
            conn = self.factory.create_connection()
            self.pool.put(conn)

    def acquire(self):
        """获取连接"""
        try:
            return self.pool.get_nowait()
        except:
            with self.lock:
                if self.pool.qsize() < self.max_size:
                    conn = self.factory.create_connection()
                    return conn
            return self.pool.get()

    def release(self, conn):
        """释放连接"""
        try:
            self.pool.put_nowait(conn)
        except:
            self.factory.close_connection(conn)

# 使用示例
pool = ConnectionPool(
    factory=ModelRegistry(),
    min_size=2,
    max_size=10
)

conn = pool.acquire()
# 使用连接...
pool.release(conn)
```

### 批量处理

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

class BatchProcessor:
    """批量处理器"""

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def process_batch(self, tasks: List[dict], handler: callable) -> List[dict]:
        """批量处理任务"""
        futures = {
            self.executor.submit(handler, task): task
            for task in tasks
        }

        results = []
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
                results.append({"task": task, "result": result, "error": None})
            except Exception as e:
                results.append({"task": task, "result": None, "error": str(e)})

        return results

    def shutdown(self):
        """关闭处理器"""
        self.executor.shutdown(wait=True)

# 使用示例
def process_carbon_data(data: dict) -> dict:
    # 处理碳排放数据
    return {"processed": True, "data": data}

processor = BatchProcessor(max_workers=8)
tasks = [{"id": i, "emissions": i * 10} for i in range(100)]
results = processor.process_batch(tasks, process_carbon_data)
processor.shutdown()
```

---

## 最佳实践

### 错误处理

```python
from govmcp import GovMCPServer
from typing import Optional

class RobustServer(GovMCPServer):
    """健壮的服务器实现"""

    def handle_error(self, error: Exception) -> dict:
        """统一错误处理"""
        error_code = self._get_error_code(error)
        error_message = str(error)

        # 记录错误
        print(f"[ERROR] {error_code}: {error_message}")

        return {
            "jsonrpc": "2.0",
            "error": {
                "code": error_code,
                "message": error_message,
                "data": {"type": type(error).__name__}
            }
        }

    def _get_error_code(self, error: Exception) -> int:
        """获取错误代码"""
        error_mapping = {
            ValueError: -32602,
            KeyError: -32602,
            PermissionError: -32603,
            TimeoutError: -32603,
            Exception: -32603
        }
        return error_mapping.get(type(error), -32603)
```

### 日志记录

```python
import logging
from govmcp import AuditChain

class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str, audit_chain: AuditChain = None):
        self.logger = logging.getLogger(name)
        self.audit_chain = audit_chain

    def log_operation(self, level: str, operation: str, **kwargs):
        """记录操作日志"""
        log_entry = {
            "operation": operation,
            **kwargs
        }

        # 记录到标准日志
        getattr(self.logger, level)(str(log_entry))

        # 记录到审计链
        if self.audit_chain:
            self.audit_chain.add_entry(
                action=operation,
                operator=kwargs.get("operator", "system"),
                input_data=str(kwargs.get("input", "")).encode(),
                output_data=str(kwargs.get("output", "")).encode(),
                result=kwargs.get("result", "completed")
            )

# 使用示例
logger = StructuredLogger("govmcp.app", AuditChain())
logger.log_operation("info", "user_login", operator="user_001", ip="192.168.1.1")
```

---

[← 快速开始](QUICKSTART.md) | [API参考 →](API.md)
