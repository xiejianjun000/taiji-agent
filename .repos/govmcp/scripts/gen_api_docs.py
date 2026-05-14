#!/usr/bin/env python3
"""
govmcp API Documentation Generator
==================================

Generates OpenAPI-style complete API documentation with:
- Full parameter validation descriptions
- Exception documentation
- Usage examples
- Type reference index
- Version information

Usage:
    python scripts/gen_api_docs.py [--lang {zh|en|all}] [--output DIR] [--openapi]
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "govmcp"
DOCS_DIR = PROJECT_ROOT / "docs"


@dataclass
class ParameterSpec:
    name: str
    type: str
    description: str = ""
    required: bool = False
    default: str | None = None
    is_var_positional: bool = False
    is_var_keyword: bool = False
    enum_values: list[str] = field(default_factory=list)


@dataclass
class FunctionSpec:
    name: str
    signature: str
    docstring: str
    parameters: list[ParameterSpec]
    returns: str | None
    raises: list[tuple[str, str]]
    examples: list[tuple[str, str]]
    is_async: bool
    decorators: list[str]
    line_number: int


@dataclass
class ClassSpec:
    name: str
    signature: str
    docstring: str
    bases: list[str]
    attributes: list[ParameterSpec]
    methods: list[FunctionSpec]
    is_dataclass: bool = False
    is_enum: bool = False
    is_typed_dict: bool = False
    enum_values: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class ModuleSpec:
    name: str
    category: str
    path: str
    docstring: str
    functions: list[FunctionSpec]
    classes: list[ClassSpec]
    version_added: str | None = None


class OpenAPIGenerator:
    OPENAPI_TEMPLATE = {
        "openapi": "3.1.0",
        "info": {
            "title": "govmcp API",
            "version": "1.0.0",
            "description": "Chinese Government MCP Protocol API Reference",
        },
        "servers": [{"url": "https://govmcp.opentaiji.com"}],
        "paths": {},
        "components": {"schemas": {}},
    }

    def __init__(self, lang: str = "zh", output_dir: Path | None = None, as_openapi: bool = False):
        self.lang = lang if lang in ("zh", "en") else "zh"
        self.output_dir = output_dir or DOCS_DIR / self.lang
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.as_openapi = as_openapi
        self._type_registry: dict[str, str] = {}
        self._module_registry: dict[str, ModuleSpec] = {}

        self._version = self._get_version()

    def _get_version(self) -> str:
        try:
            init_file = PROJECT_ROOT / "govmcp" / "__init__.py"
            if init_file.exists():
                content = init_file.read_text(encoding="utf-8")
                version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    return version_match.group(1)
        except Exception:
            pass
        return "1.0.0"

    def generate(self) -> None:
        modules = self._scan_modules()
        self._build_type_registry(modules)

        if self.as_openapi:
            self._generate_openapi_json(modules)
        else:
            self._generate_markdown_docs(modules)
            self._generate_type_index()

        print(f"[gen_api_docs] Generated API documentation in {self.output_dir}")

    def _scan_modules(self) -> list[ModuleSpec]:
        modules = []
        for py_file in sorted(SRC_DIR.rglob("*.py")):
            if "__pycache__" in str(py_file):
                continue
            if py_file.name.startswith("_") and py_file.stem != "__init__":
                continue

            module_info = self._parse_module(py_file)
            if module_info and (module_info.functions or module_info.classes):
                modules.append(module_info)
                self._module_registry[module_info.path] = module_info
        return modules

    def _parse_module(self, py_file: Path) -> ModuleSpec | None:
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            module_name = py_file.stem
            module_parts = py_file.relative_to(SRC_DIR).parts[:-1]
            module_category = module_parts[0] if module_parts else module_name

            docstring = self._extract_docstring(tree)

            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_") or node.name == "__init__":
                        func_spec = self._extract_function(node)
                        if func_spec:
                            functions.append(func_spec)
                elif isinstance(node, ast.ClassDef):
                    class_spec = self._extract_class(node)
                    if class_spec:
                        classes.append(class_spec)

            if not functions and not classes:
                return None

            return ModuleSpec(
                name=module_name,
                category=module_category,
                path=self._get_module_path(py_file),
                docstring=docstring,
                functions=functions,
                classes=classes,
            )
        except (SyntaxError, ValueError) as e:
            print(f"[gen_api_docs] Warning: Cannot parse {py_file}: {e}")
            return None

    def _get_module_path(self, py_file: Path) -> str:
        rel_path = py_file.relative_to(PROJECT_ROOT)
        return str(rel_path.parent / py_file.stem).replace("/", ".")

    def _extract_docstring(self, node: ast.AST) -> str:
        docstring = ast.get_docstring(node) or ""
        return "\n\n".join(line.strip() for line in docstring.strip().split("\n") if line.strip())

    def _extract_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> FunctionSpec | None:
        docstring = self._extract_docstring(node)
        params_info = self._parse_docstring_params(docstring)

        parameters = []
        defaults = list(node.args.defaults)
        num_defaults = len(defaults)
        num_args = len(node.args.args)
        num_no_default = num_args - num_defaults

        for i, arg in enumerate(node.args.args):
            if arg.arg in ("self", "cls"):
                continue

            annotation = ast.unparse(arg.annotation) if arg.annotation else "Any"
            description = params_info.get(arg.arg, {}).get("desc", "")
            param_type = params_info.get(arg.arg, {}).get("type", annotation)

            default = None
            if i >= num_no_default:
                try:
                    default_node = defaults[i - num_no_default]
                    default = ast.unparse(default_node)
                except (ValueError, SyntaxError):
                    default = str(defaults[i - num_no_default])

            parameters.append(
                ParameterSpec(
                    name=arg.arg,
                    type=param_type,
                    description=description,
                    required=i < num_no_default,
                    default=default,
                )
            )

        if node.args.vararg:
            vararg = node.args.vararg
            annotation = ast.unparse(vararg.annotation) if vararg.annotation else "Tuple[Any, ...]"
            parameters.append(
                ParameterSpec(
                    name=f"*{vararg.arg}",
                    type=annotation,
                    description="Variable positional arguments",
                    is_var_positional=True,
                )
            )

        for i, arg in enumerate(node.args.kwonlyargs or []):
            annotation = ast.unparse(arg.annotation) if arg.annotation else "Any"
            description = params_info.get(arg.arg, {}).get("desc", "")

            default = None
            if node.args.kw_defaults and i < len(node.args.kw_defaults):
                kw_default = node.args.kw_defaults[i]
                if kw_default:
                    try:
                        default = ast.literal_eval(ast.unparse(kw_default))
                    except (ValueError, SyntaxError):
                        default = ast.unparse(kw_default)

            parameters.append(
                ParameterSpec(
                    name=arg.arg,
                    type=annotation,
                    description=description,
                    required=False,
                    default=default,
                )
            )

        if node.args.kwarg:
            kwarg = node.args.kwarg
            annotation = ast.unparse(kwarg.annotation) if kwarg.annotation else "Dict[str, Any]"
            parameters.append(
                ParameterSpec(
                    name=f"**{kwarg.arg}",
                    type=annotation,
                    description="Variable keyword arguments",
                    is_var_keyword=True,
                )
            )

        returns = None
        if node.returns:
            returns = ast.unparse(node.returns)

        raises = []
        raise_pattern = re.compile(r":raises?\s+(\w+):\s*(.+)", re.IGNORECASE | re.MULTILINE)
        for match in raise_pattern.finditer(docstring):
            raises.append((match.group(1), match.group(2).strip()))

        examples = []
        code_pattern = re.compile(r"```python(.*?)```", re.DOTALL)
        for match in code_pattern.finditer(docstring):
            examples.append(("python", match.group(1).strip()))

        decorators = [ast.unparse(d) for d in node.decorator_list]

        signature = self._build_signature(node.name, parameters, returns)

        return FunctionSpec(
            name=node.name,
            signature=signature,
            docstring=docstring,
            parameters=parameters,
            returns=returns,
            raises=raises,
            examples=examples,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            decorators=decorators,
            line_number=node.lineno,
        )

    def _parse_docstring_params(self, docstring: str) -> dict[str, dict[str, str]]:
        result = {}

        param_pattern = re.compile(r":param\s+(\w+):\s*(.+)", re.MULTILINE)
        for match in param_pattern.finditer(docstring):
            param_name = match.group(1)
            param_desc = match.group(2).strip()
            type_match = re.search(rf":type\s+{param_name}:\s*(.+)", docstring)
            param_type = type_match.group(1).strip() if type_match else "Any"
            result[param_name] = {"desc": param_desc, "type": param_type}

        return result

    def _build_signature(
        self,
        name: str,
        parameters: list[ParameterSpec],
        returns: str | None,
    ) -> str:
        parts = []
        for param in parameters:
            if param.is_var_positional:
                parts.append(f"*{param.name}")
            elif param.is_var_keyword:
                parts.append(f"**{param.name}")
            elif param.default is not None:
                parts.append(f"{param.name}: {param.type} = {param.default}")
            else:
                parts.append(f"{param.name}: {param.type}")

        sig = f"({', '.join(parts)})"

        if returns:
            sig += f" -> {returns}"

        return sig

    def _extract_class(self, node: ast.ClassDef) -> ClassSpec | None:
        docstring = self._extract_docstring(node)

        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except (ValueError, SyntaxError):
                pass

        is_dataclass = any(
            isinstance(d, ast.Name) and d.id == "dataclass" for d in node.decorator_list
        ) or any(
            isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "dataclass"
            for d in node.decorator_list
        )

        is_enum = any(isinstance(base, ast.Name) and base.id == "Enum" for base in node.bases)

        attributes = []
        methods = []
        enum_values = []

        if is_enum:
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            value_str = ast.unparse(item.value) if item.value else ""
                            enum_values.append((target.id, value_str))

        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                annotation = ast.unparse(item.annotation) if item.annotation else "Any"
                attributes.append(
                    ParameterSpec(
                        name=item.target.id,
                        type=annotation,
                        description="",
                    )
                )

            elif isinstance(item, ast.FunctionDef):
                if item.name.startswith("__"):
                    if item.name == "__init__":
                        defaults = list(item.args.defaults)
                        num_defaults = len(defaults)
                        num_args = len(item.args.args)
                        num_no_default = num_args - num_defaults

                        for i, arg in enumerate(item.args.args[1:]):
                            annotation = ast.unparse(arg.annotation) if arg.annotation else "Any"
                            default = None
                            if i + 1 >= num_no_default:
                                try:
                                    default_node = defaults[i + 1 - num_no_default]
                                    default = ast.literal_eval(ast.unparse(default_node))
                                except (ValueError, SyntaxError):
                                    default = ast.unparse(defaults[i + 1 - num_no_default])

                            attributes.append(
                                ParameterSpec(
                                    name=arg.arg,
                                    type=annotation,
                                    description="",
                                    default=default,
                                )
                            )
                else:
                    method_spec = self._extract_function(item)
                    if method_spec:
                        methods.append(method_spec)

        return ClassSpec(
            name=node.name,
            signature=f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}",
            docstring=docstring,
            bases=bases,
            attributes=attributes,
            methods=methods,
            is_dataclass=is_dataclass,
            is_enum=is_enum,
            enum_values=enum_values,
        )

    def _build_type_registry(self, modules: list[ModuleSpec]) -> None:
        for module in modules:
            for cls in module.classes:
                self._type_registry[cls.name] = module.path
            for func in module.functions:
                for param in func.parameters:
                    if param.type not in ("Any", "None", "object") and not param.type.startswith(
                        "Tuple"
                    ):
                        if param.type not in self._type_registry:
                            self._type_registry[param.type] = module.path

    def _generate_openapi_json(self, modules: list[ModuleSpec]) -> None:
        openapi_spec = self.OPENAPI_TEMPLATE.copy()
        openapi_spec["info"]["title"] = "govmcp API"
        openapi_spec["info"]["version"] = self._version

        for module in modules:
            for cls in module.classes:
                schema = self._class_to_schema(cls)
                openapi_spec["components"]["schemas"][cls.name] = schema

            for func in module.functions:
                path_item = {
                    "get" if not func.is_async else "post": {
                        "summary": func.name,
                        "description": func.docstring.split("\n")[0] if func.docstring else "",
                        "parameters": [
                            {
                                "name": param.name,
                                "in": "query",
                                "schema": {"type": "string"},
                                "required": param.required,
                                "description": param.description,
                            }
                            for param in func.parameters
                            if not param.is_var_positional and not param.is_var_keyword
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": (
                                            {"type": func.returns}
                                            if func.returns
                                            else {"type": "object"}
                                        )
                                    }
                                },
                            }
                        },
                    }
                }
                openapi_spec["paths"][f"/{module.path}/{func.name}"] = path_item

        output_file = self.output_dir / "openapi.json"
        output_file.write_text(
            json.dumps(openapi_spec, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def _class_to_schema(self, cls: ClassSpec) -> dict[str, Any]:
        schema = {
            "type": "object",
            "description": cls.docstring.split("\n")[0] if cls.docstring else "",
            "properties": {},
            "required": [],
        }

        if cls.is_dataclass or cls.is_enum:
            schema["type"] = "string" if cls.is_enum else "object"

        for attr in cls.attributes:
            schema["properties"][attr.name] = {"type": "string"}
            if attr.required:
                schema["required"].append(attr.name)

        if cls.enum_values:
            schema["enum"] = [name for name, _ in cls.enum_values]

        return schema

    def _generate_markdown_docs(self, modules: list[ModuleSpec]) -> None:
        output_file = self.output_dir / "API.md"
        lines = []

        lines.extend(self._generate_header())
        lines.extend(self._generate_overview())
        lines.extend(self._generate_quick_start())

        categories = self._group_by_category(modules)
        for category, cat_modules in sorted(categories.items()):
            lines.extend(self._generate_category_section(category, cat_modules))

        lines.extend(self._generate_error_reference())
        lines.extend(self._generate_type_reference())
        lines.extend(self._generate_footer())

        output_file.write_text("\n".join(lines), encoding="utf-8")

    def _generate_header(self) -> list[str]:
        lines = []
        if self.lang == "zh":
            lines.extend(
                [
                    "# govmcp API 参考文档",
                    "",
                    f"> **版本**: `{self._version}`",
                    f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "",
                    "---",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# govmcp API Reference",
                    "",
                    f"> **Version**: `{self._version}`",
                    f"> **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "",
                    "---",
                    "",
                ]
            )
        return lines

    def _generate_overview(self) -> list[str]:
        if self.lang == "zh":
            return [
                "## 概览",
                "",
                "本文档提供了 govmcp 的完整 API 参考。govmcp 是国产信创 MCP 协议实现，支持:",
                "",
                "- **国密加密**: SM2/SM3/SM4 加密算法",
                "- **审批工作流**: 多级审批链配置",
                "- **不可篡改审计链**: SM3 链式哈希",
                "- **模型适配**: 19+ 国产大模型",
                "",
                "---",
                "",
            ]
        else:
            return [
                "## Overview",
                "",
                "This document provides the complete API reference for govmcp. govmcp is a Chinese Government MCP Protocol implementation supporting:",
                "",
                "- **GM Cryptography**: SM2/SM3/SM4 encryption algorithms",
                "- **Approval Workflow**: Multi-level approval chains",
                "- **Immutable Audit Chain**: SM3 chain hashing",
                "- **Model Adapters**: 19+ Chinese LLM models",
                "",
                "---",
                "",
            ]

    def _generate_quick_start(self) -> list[str]:
        if self.lang == "zh":
            return [
                "## 快速开始",
                "",
                "### 安装",
                "",
                "```bash",
                "pip install govmcp",
                "```",
                "",
                "### 基本使用",
                "",
                "```python",
                "from govmcp import GovMCPServer, sm3_hash, ApprovalFlow",
                "",
                "# 创建服务器",
                "server = GovMCPServer('my-server', '1.0')",
                "",
                "# 使用国密哈希",
                "digest = sm3_hash(b'data')",
                "",
                "# 使用审批工作流",
                "flow = ApprovalFlow(['level1', 'level2'])",
                "```",
                "",
                "---",
                "",
            ]
        else:
            return [
                "## Quick Start",
                "",
                "### Installation",
                "",
                "```bash",
                "pip install govmcp",
                "```",
                "",
                "### Basic Usage",
                "",
                "```python",
                "from govmcp import GovMCPServer, sm3_hash, ApprovalFlow",
                "",
                "# Create server",
                "server = GovMCPServer('my-server', '1.0')",
                "",
                "# Use GM hash",
                "digest = sm3_hash(b'data')",
                "",
                "# Use approval workflow",
                "flow = ApprovalFlow(['level1', 'level2'])",
                "```",
                "",
                "---",
                "",
            ]

    def _group_by_category(self, modules: list[ModuleSpec]) -> dict[str, list[ModuleSpec]]:
        categories = {}
        for module in modules:
            if module.category not in categories:
                categories[module.category] = []
            categories[module.category].append(module)
        return categories

    def _generate_category_section(self, category: str, modules: list[ModuleSpec]) -> list[str]:
        lines = []
        category_names = {
            "crypto": ("加密模块", "Cryptography Module"),
            "protocol": ("协议模块", "Protocol Module"),
            "tools": ("工具模块", "Tools Module"),
            "server": ("服务器模块", "Server Module"),
            "models": ("模型模块", "Models Module"),
        }
        cat_zh, cat_en = category_names.get(category, (category, category))

        title = cat_zh if self.lang == "zh" else cat_en
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"**模块路径**: `govmcp.{category}`")
        lines.append("")

        for module in modules:
            lines.extend(self._generate_module_section(module))

        lines.append("---")
        lines.append("")
        return lines

    def _generate_module_section(self, module: ModuleSpec) -> list[str]:
        lines = []
        lines.append(f"### `{module.path}`")
        lines.append("")

        if module.docstring:
            lines.append(module.docstring)
            lines.append("")

        if module.functions:
            if self.lang == "zh":
                lines.append("#### 函数")
            else:
                lines.append("#### Functions")
            lines.append("")

            for func in module.functions:
                lines.extend(self._generate_function_doc(func))

        if module.classes:
            if self.lang == "zh":
                lines.append("#### 类")
            else:
                lines.append("#### Classes")
            lines.append("")

            for cls in module.classes:
                lines.extend(self._generate_class_doc(cls))

        return lines

    def _generate_function_doc(self, func: FunctionSpec) -> list[str]:
        lines = []
        async_prefix = "async " if func.is_async else ""

        lines.append(f"##### `{async_prefix}{func.name}{func.signature}`")
        lines.append("")

        if self.lang == "zh":
            lines.append(f"**位置**: 行 {func.line_number}")
        else:
            lines.append(f"**Location**: Line {func.line_number}")
        lines.append("")

        if func.decorators:
            dec_str = ", ".join(func.decorators)
            lines.append(f"**装饰器**: {dec_str}")
            lines.append("")

        if func.docstring:
            lines.append(
                func.docstring.split("\n")[0] if "\n" in func.docstring else func.docstring
            )
            lines.append("")

        if func.parameters:
            if self.lang == "zh":
                lines.append("**参数**")
            else:
                lines.append("**Parameters**")
            lines.append("")
            lines.append("| 名称 | 类型 | 必需 | 默认值 | 描述 |")
            lines.append("|:---|:---|:---:|:---:|:---|")
            for param in func.parameters:
                required_str = (
                    "是"
                    if self.lang == "zh" and param.required
                    else "Yes"
                    if param.required
                    else ("否" if self.lang == "zh" else "No")
                )
                default_str = param.default if param.default else "-"
                desc_str = (
                    param.description[:50] + "..."
                    if len(param.description) > 50
                    else param.description
                )
                lines.append(
                    f"| `{param.name}` | `{param.type}` | {required_str} | `{default_str}` | {desc_str} |"
                )
            lines.append("")

        if func.returns:
            ret_label = "**返回**" if self.lang == "zh" else "**Returns**"
            lines.append(f"{ret_label} `{func.returns}`")
            lines.append("")

        if func.raises:
            raise_label = "**异常**" if self.lang == "zh" else "**Raises**"
            lines.append(raise_label)
            lines.append("")
            lines.append("| 异常类型 | 描述 |")
            lines.append("|:---|:---|")
            for exc_type, exc_desc in func.raises:
                lines.append(f"| `{exc_type}` | {exc_desc} |")
            lines.append("")

        if func.examples:
            example_label = "**示例**" if self.lang == "zh" else "**Example**"
            lines.append(example_label)
            lines.append("")
            for lang, code in func.examples[:2]:
                lines.append(f"```{lang}")
                lines.append(code)
                lines.append("```")
                lines.append("")

        lines.append("---")
        lines.append("")
        return lines

    def _generate_class_doc(self, cls: ClassSpec) -> list[str]:
        lines = []

        class_type_parts = []
        if cls.is_dataclass:
            class_type_parts.append("数据类" if self.lang == "zh" else "Dataclass")
        if cls.is_enum:
            class_type_parts.append("枚举" if self.lang == "zh" else "Enum")

        lines.append(f"##### `{cls.name}`")
        if class_type_parts:
            lines.append(" ".join(f"`{t}`" for t in class_type_parts))
        lines.append("")

        if cls.bases:
            base_label = "**基类**" if self.lang == "zh" else "**Base Classes**"
            lines.append(f"{base_label}: `{' | '.join(cls.bases)}`")
            lines.append("")

        if cls.docstring:
            lines.append(cls.docstring.split("\n")[0] if "\n" in cls.docstring else cls.docstring)
            lines.append("")

        if cls.enum_values:
            enum_label = "**枚举值**" if self.lang == "zh" else "**Enum Values**"
            lines.append(enum_label)
            lines.append("")
            lines.append("| 名称 | 值 |")
            lines.append("|:---|:---|")
            for name, value in cls.enum_values:
                lines.append(f"| `{name}` | `{value}` |")
            lines.append("")

        if cls.attributes:
            attr_label = "**属性**" if self.lang == "zh" else "**Attributes**"
            lines.append(attr_label)
            lines.append("")
            lines.append("| 名称 | 类型 |")
            lines.append("|:---|:---|")
            for attr in cls.attributes:
                lines.append(f"| `{attr.name}` | `{attr.type}` |")
            lines.append("")

        if cls.methods:
            method_label = "**方法**" if self.lang == "zh" else "**Methods**"
            lines.append(method_label)
            lines.append("")
            for method in cls.methods[:5]:
                async_prefix = "async " if method.is_async else ""
                first_line = method.docstring.split("\n")[0][:60] if method.docstring else ""
                lines.append(f"- `{async_prefix}{method.name}()` - {first_line}")
            if len(cls.methods) > 5:
                lines.append(f"- ... ({len(cls.methods) - 5} more)")
            lines.append("")

        lines.append("---")
        lines.append("")
        return lines

    def _generate_error_reference(self) -> list[str]:
        if self.lang == "zh":
            return [
                "## 异常参考",
                "",
                "| 异常类型 | 说明 |",
                "|:---|:---|",
                "| `ValueError` | 参数值无效 |",
                "| `TypeError` | 参数类型错误 |",
                "| `KeyError` | 键不存在 |",
                "| `RuntimeError` | 运行时错误 |",
                "| `NotImplementedError` | 功能未实现 |",
                "",
                "---",
                "",
            ]
        else:
            return [
                "## Error Reference",
                "",
                "| Error Type | Description |",
                "|:---|:---|",
                "| `ValueError` | Invalid parameter value |",
                "| `TypeError` | Invalid parameter type |",
                "| `KeyError` | Key not found |",
                "| `RuntimeError` | Runtime error |",
                "| `NotImplementedError` | Feature not implemented |",
                "",
                "---",
                "",
            ]

    def _generate_type_reference(self) -> list[str]:
        lines = []
        title = "## 类型引用索引" if self.lang == "zh" else "## Type Reference Index"
        lines.append(title)
        lines.append("")

        by_module = {}
        for type_name, module_path in sorted(self._type_registry.items()):
            if module_path not in by_module:
                by_module[module_path] = []
            by_module[module_path].append(type_name)

        for module_path in sorted(by_module.keys()):
            lines.append(f"### `{module_path}`")
            lines.append("")
            lines.append("| 类型 | 引用 |")
            lines.append("|:---|:---|")
            for type_name in sorted(by_module[module_path]):
                lines.append(f"| `{type_name}` | [{type_name}](#) |")
            lines.append("")

        return lines

    def _generate_type_index(self) -> list[str]:
        lines = []
        title = "## 类型引用索引" if self.lang == "zh" else "## Type Reference Index"
        lines.append(title)
        lines.append("")
        lines.append(f"> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        by_module = {}
        for type_name, module_path in sorted(self._type_registry.items()):
            if module_path not in by_module:
                by_module[module_path] = []
            by_module[module_path].append(type_name)

        for module_path in sorted(by_module.keys()):
            lines.append(f"### `{module_path}`")
            lines.append("")
            lines.append("| 类型 | 模块 |")
            lines.append("|:---|:---|")
            for type_name in sorted(by_module[module_path]):
                lines.append(f"| `{type_name}` | [{module_path}]({module_path}.md) |")
            lines.append("")

        return lines

    def _generate_footer(self) -> list[str]:
        if self.lang == "zh":
            return [
                "---",
                "",
                f"*本文档由 govmcp 文档自动生成系统生成 · 版本 {self._version}*",
            ]
        else:
            return [
                "---",
                "",
                f"*Generated by govmcp Documentation Auto-Generation System · Version {self._version}*",
            ]


def main():
    parser = argparse.ArgumentParser(description="govmcp API Documentation Generator")
    parser.add_argument(
        "--lang",
        choices=["zh", "en", "all"],
        default="all",
        help="Language version to generate (default: all)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (default: docs/<lang>)",
    )
    parser.add_argument(
        "--openapi",
        action="store_true",
        help="Generate OpenAPI JSON instead of Markdown",
    )
    args = parser.parse_args()

    langs = ["zh", "en"] if args.lang == "all" else [args.lang]

    for lang in langs:
        generator = OpenAPIGenerator(
            lang=lang,
            output_dir=args.output,
            as_openapi=args.openapi,
        )
        generator.generate()

    return 0


if __name__ == "__main__":
    sys.exit(main())
