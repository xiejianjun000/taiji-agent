#!/usr/bin/env python3
"""
govmcp Documentation Generator
===============================

Advanced documentation generator using AST parsing to extract:
- Complete function signatures with type annotations
- Dataclass, Enum, TypedDict type definitions
- Code examples from docstrings
- Complexity analysis
- Test coverage links

Usage:
    python scripts/generate_docs.py [--lang {zh|en}] [--output DIR] [--verbose]
"""

import argparse
import ast
import hashlib
import importlib.util
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "govmcp"
DOCS_DIR = PROJECT_ROOT / "docs"
TESTS_DIR = PROJECT_ROOT / "tests"


@dataclass
class ParameterInfo:
    name: str
    annotation: str
    default: str | None = None
    is_optional: bool = False
    is_var_positional: bool = False
    is_var_keyword: bool = False


@dataclass
class FunctionInfo:
    name: str
    full_signature: str
    docstring: str
    parameters: list[ParameterInfo]
    returns: str | None
    raises: list[tuple[str, str]]
    examples: list[tuple[str, str]]
    is_async: bool
    complexity: str
    decorators: list[str]
    line_number: int


@dataclass
class ClassInfo:
    name: str
    full_signature: str
    docstring: str
    bases: list[str]
    attributes: list[ParameterInfo]
    methods: list[FunctionInfo]
    properties: list[tuple[str, str, str]]
    line_number: int
    is_dataclass: bool = False
    is_enum: bool = False
    is_typed_dict: bool = False


@dataclass
class TypeAliasInfo:
    name: str
    target_type: str
    docstring: str


@dataclass
class ModuleInfo:
    name: str
    path: str
    file: Path
    docstring: str
    functions: list[FunctionInfo]
    classes: list[ClassInfo]
    type_aliases: list[TypeAliasInfo]
    imports: list[tuple[str, str]]


class ComplexityAnalyzer:
    BRANCH_KEYWORDS = {
        "if",
        "elif",
        "else",
        "for",
        "while",
        "try",
        "except",
        "finally",
        "with",
        "and",
        "or",
    }
    LOOP_KEYWORDS = {"for", "while"}
    EXCEPTION_KEYWORDS = {"try", "except", "finally", "raise"}

    @staticmethod
    def analyze_function(node: ast.FunctionDef) -> str:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return "unknown"

        statements = [n for n in ast.walk(node) if isinstance(n, (ast.stmt))]
        num_statements = len(statements)

        branch_count = sum(
            1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))
        )
        loop_depth = ComplexityAnalyzer._get_loop_depth(node)
        try_depth = ComplexityAnalyzer._get_try_depth(node)

        cyclomatic = 1 + branch_count

        if cyclomatic <= 3 and num_statements <= 10:
            return "low"
        elif cyclomatic <= 7 and num_statements <= 30:
            return "medium"
        elif cyclomatic <= 12:
            return "high"
        else:
            return "very_high"

    @staticmethod
    def _get_loop_depth(node: ast.FunctionDef) -> int:
        max_depth = 0

        def count_depth(n: ast.AST, current_depth: int = 0) -> None:
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            for child in ast.iter_child_nodes(n):
                if isinstance(child, (ast.For, ast.While)):
                    count_depth(child, current_depth + 1)
                else:
                    count_depth(child, current_depth)

        count_depth(node)
        return max_depth

    @staticmethod
    def _get_try_depth(node: ast.FunctionDef) -> int:
        max_depth = 0

        def count_depth(n: ast.AST, current_depth: int = 0) -> None:
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            for child in ast.iter_child_nodes(n):
                if isinstance(child, ast.Try):
                    count_depth(child, current_depth + 1)
                else:
                    count_depth(child, current_depth)

        count_depth(node)
        return max_depth


class DocstringParser:
    PARAM_PATTERN = re.compile(r":param\s+(\w+):\s*(.*)", re.MULTILINE)
    TYPE_PATTERN = re.compile(r":type\s+(\w+):\s*(.*)", re.MULTILINE)
    RETURN_PATTERN = re.compile(r":return[s]?:\s*(.*)", re.IGNORECASE | re.MULTILINE)
    RAISE_PATTERN = re.compile(r":raises?\s+(\w+):\s*(.*)", re.IGNORECASE | re.MULTILINE)
    EXAMPLE_PATTERN = re.compile(r":example[s]?:\s*(.*)", re.IGNORECASE | re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r"```python(.*?)```", re.DOTALL)

    @classmethod
    def parse(cls, docstring: str) -> dict[str, Any]:
        if not docstring:
            return {}

        param_docs = {}
        for match in cls.PARAM_PATTERN.finditer(docstring):
            param_docs[match.group(1)] = match.group(2).strip()

        type_docs = {}
        for match in cls.TYPE_PATTERN.finditer(docstring):
            type_docs[match.group(1)] = match.group(2).strip()

        return_docs = []
        for match in cls.RETURN_PATTERN.finditer(docstring):
            return_docs.append(match.group(1).strip())

        raise_docs = {}
        for match in cls.RAISE_PATTERN.finditer(docstring):
            exc_type = match.group(1)
            raise_docs[exc_type] = match.group(2).strip()

        examples = []
        for match in cls.CODE_BLOCK_PATTERN.finditer(docstring):
            code = match.group(1).strip()
            examples.append(("python", code))

        return {
            "param_docs": param_docs,
            "type_docs": type_docs,
            "return_docs": return_docs,
            "raise_docs": raise_docs,
            "examples": examples,
        }


class AdvancedDocGenerator:
    LANG_TEXTS = {
        "zh": {
            "module_doc_title": "模块文档",
            "functions": "导出函数",
            "classes": "导出类",
            "type_aliases": "类型别名",
            "parameters": "参数",
            "returns": "返回",
            "raises": "异常",
            "examples": "使用示例",
            "complexity": "复杂度",
            "decorators": "装饰器",
            "attributes": "属性",
            "properties": "属性方法",
            "base_classes": "基类",
            "async_function": "异步函数",
            "dataclass": "数据类",
            "enum_class": "枚举类",
            "typed_dict": "类型字典",
            "low": "低",
            "medium": "中",
            "high": "高",
            "very_high": "很高",
            "optional": "可选",
            "line_number": "行号",
            "no_functions": "*无导出函数*",
            "no_classes": "*无导出类*",
            "no_examples": "*无示例*",
            "table_of_contents": "目录",
            "quick_links": "快速链接",
            "api_reference": "API 参考",
            "changelog": "变更日志",
            "index": "首页",
        },
        "en": {
            "module_doc_title": "Module Documentation",
            "functions": "Exported Functions",
            "classes": "Exported Classes",
            "type_aliases": "Type Aliases",
            "parameters": "Parameters",
            "returns": "Returns",
            "raises": "Raises",
            "examples": "Usage Examples",
            "complexity": "Complexity",
            "decorators": "Decorators",
            "attributes": "Attributes",
            "properties": "Properties",
            "base_classes": "Base Classes",
            "async_function": "Async Function",
            "dataclass": "Dataclass",
            "enum_class": "Enum Class",
            "typed_dict": "TypedDict",
            "low": "Low",
            "medium": "Medium",
            "high": "High",
            "very_high": "Very High",
            "optional": "Optional",
            "line_number": "Line",
            "no_functions": "*No exported functions*",
            "no_classes": "*No exported classes*",
            "no_examples": "*No examples*",
            "table_of_contents": "Table of Contents",
            "quick_links": "Quick Links",
            "api_reference": "API Reference",
            "changelog": "Changelog",
            "index": "Index",
        },
    }

    def __init__(self, lang: str = "zh", output_dir: Path | None = None, verbose: bool = False):
        self.lang = lang if lang in ("zh", "en") else "zh"
        self.output_dir = output_dir or DOCS_DIR / self.lang
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        self.texts = self.LANG_TEXTS[self.lang]
        self._type_refs: dict[str, str] = {}
        self._test_mapping: dict[str, list[str]] = {}

    def generate_all(self) -> None:
        if self.verbose:
            print(f"[generate_docs] Starting documentation generation (lang={self.lang})")

        modules = self._scan_modules()
        if self.verbose:
            print(f"[generate_docs] Found {len(modules)} modules")

        self._build_type_references(modules)
        self._scan_test_mapping()

        self._generate_module_docs(modules)
        self._generate_index()
        self._generate_toc()
        self._generate_type_index()

        print(f"[generate_docs] Generated documentation in {self.output_dir}")

    def _build_type_references(self, modules: list[ModuleInfo]) -> None:
        for module in modules:
            for cls in module.classes:
                self._type_refs[cls.name] = f"{module.name}.html#{cls.name}"
            for alias in module.type_aliases:
                self._type_refs[alias.name] = f"{module.name}.html#{alias.name}"

    def _scan_test_mapping(self) -> None:
        if not TESTS_DIR.exists():
            return

        for test_file in TESTS_DIR.rglob("test_*.py"):
            try:
                content = test_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                        class_name = node.name[4:] if node.name.startswith("Test") else node.name
                        if class_name not in self._test_mapping:
                            self._test_mapping[class_name] = []
                        self._test_mapping[class_name].append(
                            f"tests/{test_file.relative_to(PROJECT_ROOT)}"
                        )

                    elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        for target in ast.walk(node):
                            if isinstance(target, ast.Call):
                                if isinstance(target.func, ast.Attribute):
                                    if hasattr(target.func.value, "id"):
                                        class_name = target.func.value.id
                                        if class_name not in self._test_mapping:
                                            self._test_mapping[class_name] = []
                                        self._test_mapping[class_name].append(
                                            f"tests/{test_file.relative_to(PROJECT_ROOT)}"
                                        )
            except (SyntaxError, ValueError):
                pass

    def _scan_modules(self) -> list[ModuleInfo]:
        modules = []
        for py_file in SRC_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            if py_file.name.startswith("_") and py_file.stem not in ("__init__",):
                continue

            module_info = self._parse_module(py_file)
            if module_info:
                modules.append(module_info)
        return modules

    def _parse_module(self, py_file: Path) -> ModuleInfo | None:
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            module_name = py_file.stem
            module_path_parts = py_file.relative_to(SRC_DIR).parent.parts
            if module_path_parts == ("",):
                module_path_str = module_name
            else:
                module_path_str = ".".join([*module_path_parts, module_name])

            docstring = self._extract_docstring(tree)

            imports = []
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append((alias.name, module))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append((alias.name, alias.name))

            functions = []
            classes = []
            type_aliases = []

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_") or node.name in ("__init__", "__all__"):
                        func_info = self._extract_function(node)
                        if func_info:
                            functions.append(func_info)

                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_class(node)
                    if class_info:
                        classes.append(class_info)

                elif isinstance(node, ast.AnnAssign):
                    target = node.target
                    if isinstance(target, ast.Name) and isinstance(node.annotation, ast.Subscript):
                        ann_str = ast.unparse(node.annotation)
                        if "Literal" not in ann_str:
                            type_aliases.append(
                                TypeAliasInfo(
                                    name=target.id,
                                    target_type=ann_str,
                                    docstring="",
                                )
                            )

            return ModuleInfo(
                name=module_name,
                path=module_path_str,
                file=py_file,
                docstring=docstring,
                functions=functions,
                classes=classes,
                type_aliases=type_aliases,
                imports=imports,
            )

        except SyntaxError as e:
            print(f"[generate_docs] Warning: Cannot parse {py_file}: {e}")
            return None

    def _extract_docstring(self, node: ast.AST) -> str:
        docstring = ast.get_docstring(node) or ""
        lines = []
        for line in docstring.strip().split("\n"):
            line = line.strip()
            if line:
                lines.append(line)
        return "\n\n".join(lines)

    def _extract_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> FunctionInfo | None:
        docstring = ast.get_docstring(node) or ""
        parsed = DocstringParser.parse(docstring)

        parameters = []
        defaults = list(node.args.defaults)
        num_defaults = len(defaults)
        num_args = len(node.args.args)
        num_no_default = num_args - num_defaults

        for i, arg in enumerate(node.args.args):
            annotation = ast.unparse(arg.annotation) if arg.annotation else "Any"

            default = None
            if i >= num_no_default:
                try:
                    default_node = defaults[i - num_no_default]
                    default = ast.unparse(default_node)
                except (ValueError, SyntaxError):
                    default = str(defaults[i - num_no_default])

            param = ParameterInfo(
                name=arg.arg,
                annotation=annotation,
                default=default,
                is_optional=i >= num_no_default,
            )
            parameters.append(param)

        for i, arg in enumerate(node.args.posonlyargs or []):
            if arg.arg in ("self", "cls"):
                continue
            annotation = ast.unparse(arg.annotation) if arg.annotation else "Any"
            parameters.insert(
                i,
                ParameterInfo(name=arg.arg, annotation=annotation),
            )

        if node.args.vararg:
            vararg = node.args.vararg
            annotation = ast.unparse(vararg.annotation) if vararg.annotation else "Tuple[Any, ...]"
            parameters.append(
                ParameterInfo(name=f"*{vararg.arg}", annotation=annotation, is_var_positional=True)
            )

        for i, arg in enumerate(node.args.kwonlyargs or []):
            annotation = ast.unparse(arg.annotation) if arg.annotation else "Any"
            default = None
            for j, kw_default in enumerate(node.args.kw_defaults or []):
                if j == i and kw_default:
                    try:
                        default = ast.literal_eval(ast.unparse(kw_default))
                    except (ValueError, SyntaxError):
                        default = ast.unparse(kw_default)

            parameters.append(
                ParameterInfo(
                    name=arg.arg, annotation=annotation, default=default, is_optional=True
                )
            )

        if node.args.kwarg:
            kwarg = node.args.kwarg
            annotation = ast.unparse(kwarg.annotation) if kwarg.annotation else "Dict[str, Any]"
            parameters.append(
                ParameterInfo(name=f"**{kwarg.arg}", annotation=annotation, is_var_keyword=True)
            )

        returns = None
        if node.returns:
            returns = ast.unparse(node.returns)

        raises = []
        for exc_type, desc in parsed.get("raise_docs", {}).items():
            raises.append((exc_type, desc))

        decorators = []
        for decorator in node.decorator_list:
            decorators.append(ast.unparse(decorator))

        full_signature = self._build_signature(node.name, parameters, node.returns)

        complexity = ComplexityAnalyzer.analyze_function(node)

        return FunctionInfo(
            name=node.name,
            full_signature=full_signature,
            docstring=docstring,
            parameters=parameters,
            returns=returns,
            raises=raises,
            examples=parsed.get("examples", []),
            is_async=isinstance(node, ast.AsyncFunctionDef),
            complexity=complexity,
            decorators=decorators,
            line_number=node.lineno,
        )

    def _build_signature(
        self, name: str, parameters: list[ParameterInfo], returns_node: ast.AST | None
    ) -> str:
        parts = []
        for param in parameters:
            if param.is_var_positional:
                parts.append(f"*{param.name}")
            elif param.is_var_keyword:
                parts.append(f"**{param.name}")
            elif param.default is not None:
                parts.append(f"{param.name}: {param.annotation} = {param.default}")
            else:
                parts.append(f"{param.name}: {param.annotation}")

        sig = f"({', '.join(parts)})"

        if returns_node:
            sig += f" -> {ast.unparse(returns_node)}"

        return sig

    def _extract_class(self, node: ast.ClassDef) -> ClassInfo | None:
        docstring = ast.get_docstring(node) or ""

        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except (ValueError, SyntaxError):
                pass

        is_dataclass = any(
            isinstance(d, ast.Name) and d.id == "dataclass" for d in node.decorator_list
        ) or any(
            n
            for n in node.decorator_list
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dataclass"
        )

        is_enum = any(isinstance(base, ast.Name) and base.id == "Enum" for base in node.bases)

        is_typed_dict = any(
            isinstance(base, ast.Attribute)
            and isinstance(base.value, ast.Name)
            and base.value.id == "typing"
            and base.attr == "TypedDict"
            for base in node.bases
        )

        attributes = []
        properties = []
        methods = []

        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                annotation = ast.unparse(item.annotation) if item.annotation else "Any"
                attributes.append(
                    ParameterInfo(
                        name=item.target.id,
                        annotation=annotation,
                        is_optional=item.value is None,
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
                                ParameterInfo(
                                    name=arg.arg,
                                    annotation=annotation,
                                    default=default,
                                    is_optional=i + 1 >= num_no_default,
                                )
                            )

                    elif item.name.startswith("@property") or any(
                        isinstance(d, ast.Name) and d.id == "property" for d in item.decorator_list
                    ):
                        property_type = ast.unparse(item.returns) if item.returns else "Any"
                        property_doc = ast.get_docstring(item) or ""
                        properties.append(
                            (item.name.replace("_", " "), property_type, property_doc)
                        )
                else:
                    method_info = self._extract_function(item)
                    if method_info:
                        methods.append(method_info)

        if is_dataclass:
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    pass

        return ClassInfo(
            name=node.name,
            full_signature=self._build_class_signature(node.name, bases),
            docstring=docstring,
            bases=bases,
            attributes=attributes,
            methods=methods,
            properties=properties,
            line_number=node.lineno,
            is_dataclass=is_dataclass,
            is_enum=is_enum,
            is_typed_dict=is_typed_dict,
        )

    def _build_class_signature(self, name: str, bases: list[str]) -> str:
        if bases:
            return f"class {name}({', '.join(bases)})"
        return f"class {name}"

    def _generate_module_docs(self, modules: list[ModuleInfo]) -> None:
        for module in modules:
            self._write_module_doc(module)

    def _write_module_doc(self, module: ModuleInfo) -> None:
        output_file = self.output_dir / f"{module.name}.md"

        lines = []
        lines.append(f"# {module.path}")
        lines.append("")
        relative_path = module.file.relative_to(SRC_DIR).as_posix()
        lines.append(f"```include ../govmcp/{relative_path}")
        lines.append("```")
        lines.append("")

        lines.append(f"## {self.texts['module_doc_title']}")
        lines.append("")
        if module.docstring:
            lines.append(self._format_docstring(module.docstring))
        lines.append("")

        lines.append(f"### {self.texts['parameters']}")
        lines.append("")
        lines.append(
            f"| {self.texts['line_number']} | {self.texts['complexity']} | {self.texts['decorators']} |"
        )
        lines.append("|:---|:---|:---|")

        if module.functions:
            for func in module.functions:
                decorators_str = ", ".join(func.decorators) if func.decorators else "-"
                async_str = "async " if func.is_async else ""
                complexity_label = self.texts.get(func.complexity, func.complexity)
                lines.append(f"| {func.line_number} | {complexity_label} | {decorators_str} |")
        else:
            lines.append("| - | - | - |")

        lines.append("")

        if module.functions:
            lines.append(f"## {self.texts['functions']}")
            lines.append("")
            for func in module.functions:
                self._write_function_doc(lines, func)

        if module.classes:
            lines.append(f"## {self.texts['classes']}")
            lines.append("")
            for cls in module.classes:
                self._write_class_doc(lines, cls)

        if module.type_aliases:
            lines.append(f"## {self.texts['type_aliases']}")
            lines.append("")
            for alias in module.type_aliases:
                lines.append(f"### `{alias.name}`")
                lines.append("")
                lines.append(f"**Type:** `{alias.target_type}`")
                lines.append("")
                if alias.docstring:
                    lines.append(self._format_docstring(alias.docstring))
                    lines.append("")
                lines.append("---")
                lines.append("")

        lines.append("## Test Coverage")
        lines.append("")
        coverage_tests = self._get_test_coverage(module.name)
        if coverage_tests:
            lines.append("| Test File |")
            lines.append("|:---|")
            for test_file in coverage_tests:
                lines.append(f"| `{test_file}` |")
        else:
            lines.append("*No specific tests found for this module.*")
        lines.append("")

        output_file.write_text("\n".join(lines), encoding="utf-8")

    def _write_function_doc(self, lines: list[str], func: FunctionInfo) -> None:
        async_prefix = "async " if func.is_async else ""
        lines.append(f"### `{async_prefix}{func.name}{func.full_signature}`")
        lines.append("")

        badge_parts = [f"`{self.texts['line_number']}:{func.line_number}`"]
        if func.is_async:
            badge_parts.append(f"`{self.texts['async_function']}`")
        if func.complexity:
            complexity_label = self.texts.get(func.complexity, func.complexity)
            badge_parts.append(f"`{self.texts['complexity']}:{complexity_label}`")

        lines.append(" ".join(badge_parts))
        lines.append("")

        if func.docstring:
            lines.append(self._format_docstring(func.docstring))
            lines.append("")

        if func.parameters:
            lines.append(f"#### {self.texts['parameters']}")
            lines.append("")
            lines.append("| Name | Type | Default |")
            lines.append("|:---|:---|:---|")
            for param in func.parameters:
                default_str = param.default if param.default else "-"
                optional_str = f" ({self.texts['optional']})" if param.is_optional else ""
                lines.append(
                    f"| `{param.name}`{optional_str} | `{param.annotation}` | `{default_str}` |"
                )
            lines.append("")

        if func.returns:
            lines.append(f"#### {self.texts['returns']}")
            lines.append("")
            lines.append(f"`{func.returns}`")
            lines.append("")

        if func.raises:
            lines.append(f"#### {self.texts['raises']}")
            lines.append("")
            lines.append("| Exception | Description |")
            lines.append("|:---|:---|")
            for exc_type, desc in func.raises:
                lines.append(f"| `{exc_type}` | {desc} |")
            lines.append("")

        if func.examples:
            lines.append(f"#### {self.texts['examples']}")
            lines.append("")
            for lang, code in func.examples:
                lines.append(f"```{lang}")
                lines.append(code)
                lines.append("```")
                lines.append("")

        lines.append("---")
        lines.append("")

    def _write_class_doc(self, lines: list[str], cls: ClassInfo) -> None:
        class_type_labels = []
        if cls.is_dataclass:
            class_type_labels.append(self.texts["dataclass"])
        if cls.is_enum:
            class_type_labels.append(self.texts["enum_class"])
        if cls.is_typed_dict:
            class_type_labels.append(self.texts["typed_dict"])

        lines.append(f"### `{cls.name}`")
        lines.append("")

        if class_type_labels:
            lines.append(" ".join(f"`{label}`" for label in class_type_labels) + "  ")
            lines.append("")

        lines.append(f"`{self.texts['line_number']}: {cls.line_number}`  ")
        lines.append("")

        if cls.bases:
            lines.append(f"**{self.texts['base_classes']}:** `{' | '.join(cls.bases)}`")
            lines.append("")

        if cls.docstring:
            lines.append(self._format_docstring(cls.docstring))
            lines.append("")

        if cls.attributes:
            lines.append(f"#### {self.texts['attributes']}")
            lines.append("")
            lines.append("| Name | Type |")
            lines.append("|:---|:---|")
            for attr in cls.attributes:
                lines.append(f"| `{attr.name}` | `{attr.annotation}` |")
            lines.append("")

        if cls.properties:
            lines.append(f"#### {self.texts['properties']}")
            lines.append("")
            lines.append("| Property | Type | Description |")
            lines.append("|:---|:---|:---|")
            for prop_name, prop_type, prop_doc in cls.properties:
                lines.append(f"| `{prop_name}` | `{prop_type}` | {prop_doc} |")
            lines.append("")

        if cls.methods:
            lines.append(f"#### {self.texts['decorators']}")
            lines.append("")
            for method in cls.methods:
                self._write_function_doc(lines, method)

        lines.append("---")
        lines.append("")

    def _format_docstring(self, docstring: str) -> str:
        lines = []
        in_code_block = False
        for line in docstring.strip().split("\n"):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
            lines.append(stripped if in_code_block else line)
        return "\n\n".join(line for line in lines if line)

    def _get_test_coverage(self, module_name: str) -> list[str]:
        return self._test_mapping.get(module_name, [])

    def _generate_index(self) -> None:
        index_file = self.output_dir / "index.md"

        if self.lang == "zh":
            content = f"""# govmcp 文档

> 国产信创MCP协议文档

**版本:** `{PROJECT_ROOT.joinpath("govmcp/__init__.py").read_text().split('__version__ = "')[1].split('"')[0] if "__version__" in PROJECT_ROOT.joinpath("govmcp/__init__.py").read_text() else "1.0.0"}`

## 模块索引

| 模块 | 说明 | 复杂度 |
|:---|:---|:---|
| `govmcp.crypto` | 国密加密模块 (SM2/SM3/SM4) | |
| `govmcp.protocol` | JSON-RPC 2.0 协议层 | |
| `govmcp.tools` | 工具注册中心 | |
| `govmcp.server` | 审批工作流 | |
| `govmcp.models` | 大模型适配 | |

## 快速链接

- [{self.texts["api_reference"]}](api/)
- [{self.texts["changelog"]}](../CHANGELOG.md)
- [测试覆盖率](../tests/)

---
*Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        else:
            content = f"""# govmcp Documentation

> Chinese Government Information MCP Protocol

**Version:** `{PROJECT_ROOT.joinpath("govmcp/__init__.py").read_text().split('__version__ = "')[1].split('"')[0] if "__version__" in PROJECT_ROOT.joinpath("govmcp/__init__.py").read_text() else "1.0.0"}`

## Module Index

| Module | Description | Complexity |
|:---|:---|:---|
| `govmcp.crypto` | GM Cryptographic Module (SM2/SM3/SM4) | |
| `govmcp.protocol` | JSON-RPC 2.0 Protocol Layer | |
| `govmcp.tools` | Tool Registry | |
| `govmcp.server` | Approval Workflow | |
| `govmcp.models` | LLM Adapters | |

## Quick Links

- [{self.texts["api_reference"]}](api/)
- [{self.texts["changelog"]}](../CHANGELOG.md)
- [Test Coverage](../tests/)

---
*Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        index_file.write_text(content, encoding="utf-8")

    def _generate_toc(self) -> None:
        toc_file = self.output_dir / "SUMMARY.md"
        modules = self._scan_modules()

        lines = [f"# {self.texts['table_of_contents']}", ""]
        lines.append(f"- [{self.texts['index']}](README.md)")
        lines.append("")

        by_category = {}
        for module in modules:
            category = module.path.split(".")[0] if "." in module.path else "core"
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(module)

        for category in sorted(by_category.keys()):
            lines.append(f"## {category}")
            lines.append("")
            for module in sorted(by_category[category], key=lambda x: x.name):
                lines.append(f"- [{module.path}]({module.name}.md)")
            lines.append("")

        toc_file.write_text("\n".join(lines), encoding="utf-8")

    def _generate_type_index(self) -> None:
        index_file = self.output_dir / "types.md"

        lines = ["# Type Reference Index", ""]
        lines.append("This document provides a reference for all custom types defined in govmcp.")
        lines.append("")

        by_module = {}
        for type_name, ref in sorted(self._type_refs.items()):
            module = ref.split(".")[0] if "." in ref else "core"
            if module not in by_module:
                by_module[module] = []
            by_module[module].append((type_name, ref))

        for module in sorted(by_module.keys()):
            lines.append(f"## {module}")
            lines.append("")
            lines.append("| Type | Reference |")
            lines.append("|:---|:---|")
            for type_name, ref in sorted(by_module[module]):
                lines.append(f"| `{type_name}` | [{ref}]({ref}) |")
            lines.append("")

        index_file.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="govmcp Advanced Documentation Generator")
    parser.add_argument(
        "--lang",
        choices=["zh", "en"],
        default="zh",
        help="Documentation language (default: zh)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (default: docs/<lang>)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    args = parser.parse_args()

    generator = AdvancedDocGenerator(
        lang=args.lang,
        output_dir=args.output,
        verbose=args.verbose,
    )
    generator.generate_all()

    return 0


if __name__ == "__main__":
    sys.exit(main())
