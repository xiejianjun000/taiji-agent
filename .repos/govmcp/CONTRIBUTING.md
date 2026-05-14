# GovMCP - 贡献指南

感谢您对 GovMCP 的关注！

## 开发环境

### 环境要求

| 要求 | 版本 | 说明 |
|:---|:---|:---|
| Python | 3.10+ | 推荐 3.11 |
| pip | 最新版 | 包管理器 |
| Git | 2.0+ | 版本控制 |

### 安装开发依赖

```bash
# 克隆仓库
git clone https://github.com/xiejianjun000/govmcp.git
cd govmcp

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -e ".[dev]"
# 或安装全部依赖
pip install -e ".[full,ws,http]"
```

## 常用命令

| 命令 | 说明 |
|:---|:---|
| `pip install -e ".[dev]"` | 安装开发依赖 |
| `pytest tests/` | 运行测试 |
| `pytest tests/ -v` | 运行测试（详细输出） |
| `pytest tests/ --cov=govmcp` | 运行测试（覆盖率） |
| `ruff check .` | 代码检查 |
| `ruff format .` | 代码格式化 |
| `ruff check . --fix` | 自动修复代码问题 |
| `mypy govmcp/` | 类型检查 |
| `python scripts/generate_docs.py` | 生成文档 |
| `python -m govmcp` | 启动服务 |

## 代码规范

### Python 版本

- 使用 Python 3.10+ 语法
- 支持类型注解（推荐使用）
- 遵循 PEP 8 规范

### 类型注解

```python
from typing import List, Optional

def process_data(data: bytes, options: Optional[dict] = None) -> dict:
    """处理数据"""
    return {"result": data.hex()}
```

### 文档字符串

```python
def sm3_hash(data: bytes) -> str:
    """计算 SM3 哈希值。

    Args:
        data: 输入数据（字节串）

    Returns:
        十六进制格式的哈希值

    Example:
        >>> sm3_hash(b"hello")
        '1abd21a2...'
    """
    pass
```

### 提交规范

使用 Conventional Commits 格式：

```
<type>(<scope>): <subject>

feat(crypto): 添加 SM4-CBC 加密模式
fix(server): 修复 stdio 读取问题
docs(readme): 更新快速开始指南
test(models): 添加模型注册表测试
refactor(protocol): 重构任务管理模块
```

**类型说明**：

| 类型 | 说明 |
|:---|:---|
| feat | 新功能 |
| fix | 缺陷修复 |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构 |
| test | 测试相关 |
| chore | 构建/工具相关 |

## 测试规范

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_all.py

# 运行特定测试类
pytest tests/test_all.py::TestSM2

# 运行带覆盖率的测试
pytest tests/ --cov=govmcp --cov-report=html
```

### 编写测试

```python
import pytest
from govmcp.crypto.sm import sm3_hash

class TestSM3:
    def test_basic_hash(self):
        """测试基本哈希功能"""
        result = sm3_hash(b"hello")
        assert isinstance(result, str)
        assert len(result) == 64  # SM3 哈希长度为 64 字符

    def test_empty_input(self):
        """测试空输入"""
        result = sm3_hash(b"")
        assert len(result) == 64
```

## 文档规范

### 文档生成

```bash
# 生成中文文档
python scripts/generate_docs.py --lang zh

# 生成英文文档
python scripts/generate_docs.py --lang en

# 生成 API 文档
python scripts/gen_api_docs.py --lang all

# 更新 README 统计
python scripts/update_readme.py
```

### 文档要求

- 所有公共函数必须包含 docstring
- 复杂逻辑需要添加注释说明
- 示例代码需要可执行验证

## Pull Request 流程

1. **Fork 仓库** - 点击 GitHub 右上角 Fork
2. **创建分支** - `git checkout -b feature/my-feature`
3. **开发** - 按照代码规范开发
4. **测试** - 确保所有测试通过
5. **提交** - 使用 Conventional Commits 格式
6. **推送** - `git push origin feature/my-feature`
7. **PR** - 创建 Pull Request 并填写模板

## 问题反馈

### Bug 报告

请提供以下信息：

- 环境信息（Python 版本、操作系统）
- 复现步骤
- 期望行为 vs 实际行为
- 相关日志/错误信息

### 功能建议

请说明：

- 使用场景
- 期望功能
- 可能的替代方案

## 许可证

通过贡献代码，您同意将代码以 Apache 2.0 许可证发布。

## 联系方式

- GitHub Issues: https://github.com/xiejianjun000/govmcp/issues
- 邮箱: contact@opentaiji.com
