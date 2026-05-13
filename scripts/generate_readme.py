#!/usr/bin/env python3
"""
OpenTaiji README 自动生成器

根据代码包结构动态生成 README.md
"""

import os
import sys
import ast
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "opentaiji"


class CodeScanner:
    """代码扫描器"""
    
    def __init__(self, src_dir: Path):
        self.src_dir = src_dir
    
    def scan_modules(self) -> Dict[str, Dict]:
        """扫描所有模块"""
        modules = {}
        
        for py_file in self.src_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            rel_path = py_file.relative_to(self.src_dir)
            module_path = str(rel_path).replace("/", ".").replace("\\", ".")[:-3]
            
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)
                
                classes = []
                functions = []
                docstring = ast.get_docstring(tree)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_doc = ast.get_docstring(node)
                        classes.append({
                            "name": node.name,
                            "doc": class_doc,
                        })
                    elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                        func_doc = ast.get_docstring(node)
                        functions.append({
                            "name": node.name,
                            "doc": func_doc,
                        })
                
                if classes or functions:
                    modules[module_path] = {
                        "path": rel_path,
                        "classes": classes,
                        "functions": functions,
                        "doc": docstring,
                    }
            except Exception as e:
                print(f"Error parsing {py_file}: {e}")
        
        return modules
    
    def scan_init(self) -> Dict:
        """扫描主 __init__.py"""
        init_file = self.src_dir / "__init__.py"
        if not init_file.exists():
            return {}
        
        try:
            content = init_file.read_text(encoding="utf-8")
            tree = ast.parse(content)
            
            exports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            exports.append(target.id)
            
            return {
                "exports": exports,
                "version": self._extract_version(content),
            }
        except Exception as e:
            print(f"Error parsing __init__.py: {e}")
            return {}
    
    def _extract_version(self, content: str) -> str:
        """提取版本号"""
        for line in content.split("\n"):
            if "__version__" in line:
                parts = line.split("=")
                if len(parts) == 2:
                    return parts[1].strip().strip('"').strip("'")
        return "2.0.0"


class ReadmeGenerator:
    """README 生成器"""
    
    def __init__(self, scanner: CodeScanner):
        self.scanner = scanner
        self.modules = scanner.scan_modules()
        self.init_info = scanner.scan_init()
    
    def generate(self) -> str:
        """生成完整 README"""
        sections = []
        
        sections.append(self._header())
        sections.append(self._features())
        sections.append(self._installation())
        sections.append(self._quick_start())
        sections.append(self._architecture())
        sections.append(self._modules())
        sections.append(self._api_reference())
        sections.append(self._commands())
        sections.append(self._license())
        
        return "\n\n".join(sections)
    
    def _header(self) -> str:
        """生成头部"""
        version = self.init_info.get("version", "2.0.0")
        
        return f'''# OpenTaiji {version}

**融合 Hermes Agent + cgast/harness + OpenTaiji WFGY**
太极哲学驱动的 AI Agent 框架

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 太极生两仪，两仪生四象，四象生八卦。
> 开源 AI Agent 框架，融合多框架精华，专注防幻觉与可靠性。
'''
    
    def _features(self) -> str:
        """生成特性列表"""
        return '''## 特性

### 核心能力
| 特性 | 说明 | 来源 |
|------|------|------|
| **WFGY 防幻觉** | 基于符号层验证，确保 LLM 输出可靠性 | OpenTaiji |
| **Agent Loop** | ~350行核心，极简可观测 | cgast/harness |
| **Soul 人格引擎** | YAML 声明式人格定义，安全可解释 | cgast/harness |
| **记忆系统** | 跨会话记忆，用户画像，语义搜索 | Hermes Honcho |
| **自我学习闭环** | 从交互中学习，自动创建技能 | Hermes |
| **事件驱动** | 完整的事件总线系统 | cgast/harness |

### 工具生态
| 工具数 | 说明 |
|--------|------|
| 15+ | 开箱即用工具 (文件/Shell/Git/搜索等) |

### 模型支持
| 类别 | 模型 |
|------|------|
| 国际 | Anthropic Claude, OpenAI GPT |
| 国产 | 通义千问, 智谱 GLM, Kimi, 豆包 |

### 消息平台
| 平台 | 支持 |
|------|------|
| 5+ | Telegram, Discord, Slack, 企业微信, 钉钉, 飞书 |
'''
    
    def _installation(self) -> str:
        """生成安装说明"""
        return '''## 安装

```bash
# 克隆项目
git clone https://github.com/xiejianjun000/open-taiji.git
cd open-taiji/open-taiji-python

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\\Scripts\\activate  # Windows

# 安装
pip install -e ".[all]"

# 初始化
opentaiji init
```

### 依赖说明

- `[all]` - 安装所有可选依赖
- `[messaging]` - 消息平台支持
- `[voice]` - 语音模式支持
- `[browser]` - 浏览器自动化支持
- `[dev]` - 开发依赖
'''
    
    def _quick_start(self) -> str:
        """生成快速开始"""
        return '''## 快速开始

```python
from opentaiji import TaijiAgent, AgentConfig

# 创建 Agent
config = AgentConfig(
    provider="anthropic",
    model="claude-sonnet-4-20250514",
    wfgy_enabled=True,
    max_iterations=25,
)

agent = TaijiAgent(config=config)

# 运行任务
result = await agent.run("分析这段代码的性能瓶颈")
print(result.content)
```

### 命令行使用

```bash
# 运行 Agent
opentaiji run "帮我分析这段代码的性能"

# 流式输出
opentaiji run --stream "写一个快速排序"

# 交互模式
opentaiji run "解释什么是微服务架构"
```
'''
    
    def _architecture(self) -> str:
        """生成架构图"""
        return '''## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         OpenTaiji 2.0                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │     WFGY     │  │     Soul     │  │    Honcho    │        │
│  │   防幻觉     │  │   人格引擎    │  │   记忆系统    │        │
│  │ (OpenTaiji) │  │  (Harness)   │  │  (Hermes)    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                           │                                     │
│  ┌───────────────────────▼───────────────────────────────┐    │
│  │              Agent Loop (Harness ~350行)              │    │
│  │         prompt → WFGY验证 → LLM → execute            │    │
│  └──────────────────────────────────────────────────────┘    │
│                           │                                     │
│  ┌───────────────────────▼───────────────────────────────┐    │
│  │              工具系统 (15+ Tools)                    │    │
│  │    文件操作 | Shell执行 | Git | Web搜索 | 代码执行    │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```
'''
    
    def _modules(self) -> str:
        """生成模块列表"""
        sections = ["## 模块结构\n"]
        
        # 按目录分组
        module_dirs = {}
        for module_path, info in sorted(self.modules.items()):
            parts = module_path.split(".")
            if len(parts) > 1:
                dir_name = parts[0]
                if dir_name not in module_dirs:
                    module_dirs[dir_name] = []
                module_dirs[dir_name].append((parts[1], info))
            else:
                if "_root" not in module_dirs:
                    module_dirs["_root"] = []
                module_dirs["_root"].append((module_path, info))
        
        for dir_name in sorted(module_dirs.keys()):
            display_name = dir_name.replace("_root", "核心模块")
            sections.append(f"\n### {display_name}\n")
            
            for sub_name, info in sorted(module_dirs[dir_name], key=lambda x: x[0]):
                path = info["path"]
                doc = info["doc"] or ""
                classes = info["classes"]
                functions = info["functions"]
                
                sections.append(f'''#### `{sub_name}` ({path})

{doc[:200]}{"..." if len(doc) > 200 else ""}

''')
                
                if classes:
                    sections.append(f"**类**: {', '.join(c['name'] for c in classes)}\n")
                if functions:
                    sections.append(f"**函数**: {', '.join(f['name'] for f in functions[:5])}")
                    if len(functions) > 5:
                        sections.append(f", ... (+{len(functions)-5} more)")
                    sections.append("\n")
        
        return "".join(sections)
    
    def _api_reference(self) -> str:
        """生成 API 参考"""
        exports = self.init_info.get("exports", [])
        
        return f'''## API 参考

### 主要导出

```python
# 核心
from opentaiji import (
    TaijiAgent,      # Agent 引擎
    AgentConfig,     # 配置类
)

# WFGY 防幻觉
from opentaiji import (
    WFGYVerifier,           # 符号层验证器
    HallucinationDetector,  # 幻觉检测器
)

# Soul 人格
from opentaiji import (
    SoulLoader,    # Soul 加载器
    Soul,          # Soul 数据类
)

# 记忆
from opentaiji import SessionMemory

# 工具
from opentaiji import ToolRegistry

# 国产模型
from opentaiji import (
    QwenProvider,   # 通义千问
    GLMProvider,    # 智谱 GLM
    KimiProvider,   # Kimi
    DoubaoProvider, # 豆包
)

# 消息网关
from opentaiji import MessageGateway, create_gateway

# 技能系统
from opentaiji import SkillManager, Skill, SkillCreator

# 自我学习
from opentaiji import HonchoMemory, SelfImprovingLoop
```

### Agent 配置

```python
config = AgentConfig(
    provider="anthropic",      # LLM 提供商
    model="claude-sonnet-4-20250514",  # 模型
    soul="default",            # 人格
    temperature=0.7,           # 温度
    max_iterations=25,        # 最大迭代
    wfgy_enabled=True,         # 启用 WFGY
    wfgy_threshold=0.7,        # 幻觉阈值
)
```
'''
    
    def _commands(self) -> str:
        """生成命令参考"""
        return '''## 命令

| 命令 | 说明 |
|------|------|
| `opentaiji run <task>` | 运行任务 |
| `opentaiji init` | 初始化配置 |
| `opentaiji souls` | 列出人格 |
| `opentaiji tools` | 列出工具 |
| `opentaiji memory` | 查看记忆 |
| `opentaiji wfgy-check` | WFGY 验证 |

### 配置环境变量

```bash
# LLM API Keys
export ANTHROPIC_API_KEY="sk-..."
export OPENAI_API_KEY="sk-..."
export DASHSCOPE_API_KEY="..."

# 国产模型 Keys
export ZHIPU_API_KEY="..."
export MOONSHOT_API_KEY="..."
export DOUBAO_API_KEY="..."
```
'''
    
    def _license(self) -> str:
        """生成许可"""
        return f'''## License

MIT License - see [LICENSE](LICENSE) 文件

---

*自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*  
*基于 OpenTaiji 源码自动扫描生成*
'''


def main():
    """主函数"""
    print("🔍 扫描 OpenTaiji 代码包...")
    
    scanner = CodeScanner(SRC_DIR)
    generator = ReadmeGenerator(scanner)
    
    readme_content = generator.generate()
    
    readme_path = PROJECT_ROOT / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")
    
    print(f"✅ README.md 已生成: {readme_path}")
    print(f"   模块数: {len(generator.modules)}")
    print(f"   导出项: {len(generator.init_info.get('exports', []))}")


if __name__ == "__main__":
    main()
