#!/usr/bin/env python3
"""
govmcp CHANGELOG Generator
==========================

Advanced changelog generator with full Conventional Commits support:
- Perfect Conventional Commits parsing
- Automatic breaking change detection
- Semantic version suggestions
- Commit links
- Multi-language support
- Diff statistics

Usage:
    python scripts/gen_changelog.py [--output FILE] [--from-tag TAG] [--lang {zh|en}]
                                   [--include-commit-links] [--unreleased]
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_FILE = PROJECT_ROOT / "CHANGELOG.md"


COMMIT_TYPES = {
    "feat": {"zh": "新增", "en": "Added", "scope": "Features"},
    "fix": {"zh": "修复", "en": "Fixed", "scope": "Bug Fixes"},
    "docs": {"zh": "文档", "en": "Changed", "scope": "Documentation"},
    "style": {"zh": "格式", "en": "Changed", "scope": "Styling"},
    "refactor": {"zh": "重构", "en": "Changed", "scope": "Refactoring"},
    "perf": {"zh": "性能", "en": "Changed", "scope": "Performance"},
    "test": {"zh": "测试", "en": "Changed", "scope": "Tests"},
    "build": {"zh": "构建", "en": "Changed", "scope": "Build System"},
    "ci": {"zh": "CI/CD", "en": "Changed", "scope": "CI/CD"},
    "chore": {"zh": "维护", "en": "Changed", "scope": "Maintenance"},
    "revert": {"zh": "回退", "en": "Reverted", "scope": "Reverts"},
}

CONVENTIONAL_COMMITS_REGEX = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\(([^)]+)\))?"
    r"(!)?"  # Breaking change indicator
    r":\s+(.+)$"
)

FOOTER_BREAKING_REGEX = re.compile(r"^BREAKING[- ]CHANGE:\s*(.+)$", re.IGNORECASE | re.MULTILINE)


@dataclass
class CommitInfo:
    hash_full: str
    hash_short: str
    type: str
    scope: str | None
    subject: str
    body: str
    is_breaking: bool
    breaking_description: str
    footer_notes: dict[str, str]
    author: str
    date: str
    files_changed: list[str]
    insertions: int
    deletions: int


@dataclass
class VersionSuggestion:
    current_version: str
    suggested_version: str
    change_type: str
    breaking_changes: list[str]
    features: list[str]
    fixes: list[str]


@dataclass
class DiffStats:
    total_commits: int
    total_files: int
    insertions: int
    deletions: int
    by_type: dict[str, int]
    by_author: dict[str, int]


class SemanticVersioner:
    @staticmethod
    def suggest_version(
        commits: list[CommitInfo],
        current_version: str,
    ) -> VersionSuggestion:
        has_breaking = any(c.is_breaking for c in commits)
        has_features = any(c.type == "feat" for c in commits)
        has_fixes = any(c.type == "fix" for c in commits)

        major, minor, patch = SemanticVersioner._parse_version(current_version)

        if has_breaking:
            suggested = f"{major + 1}.0.0"
            change_type = "major"
        elif has_features:
            suggested = f"{major}.{minor + 1}.0"
            change_type = "minor"
        elif has_fixes:
            suggested = f"{major}.{minor}.{patch + 1}"
            change_type = "patch"
        else:
            suggested = current_version
            change_type = "none"

        return VersionSuggestion(
            current_version=current_version,
            suggested_version=suggested,
            change_type=change_type,
            breaking_changes=[c.subject for c in commits if c.is_breaking],
            features=[c.subject for c in commits if c.type == "feat"],
            fixes=[c.subject for c in commits if c.type == "fix"],
        )

    @staticmethod
    def _parse_version(version: str) -> tuple[int, int, int]:
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", version)
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3))
        return 1, 0, 0


class DiffAnalyzer:
    @staticmethod
    def analyze(range_spec: str) -> DiffStats:
        stats = DiffStats(
            total_commits=0,
            total_files=0,
            insertions=0,
            deletions=0,
            by_type={},
            by_author={},
        )

        total_output = subprocess.run(
            ["git", "rev-list", "--count", range_spec],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if total_output.returncode == 0:
            stats.total_commits = int(total_output.stdout.strip() or 0)

        shortstat_output = subprocess.run(
            ["git", "diff", "--shortstat", range_spec],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if shortstat_output.returncode == 0:
            match = re.search(
                r"(\d+)\s+file(?:s)?\s+changed(?:,\s+(\d+)\s+insertion(?:s)?(?:\(\+\))?)?(?:,\s+(\d+)\s+deletion(?:s)?(?:\(-\))?)?",
                shortstat_output.stdout,
            )
            if match:
                stats.total_files = int(match.group(1) or 0)
                stats.insertions = int(match.group(2) or 0)
                stats.deletions = int(match.group(3) or 0)

        return stats


class ChangelogGenerator:
    COMMIT_LINK_TEMPLATE = {
        "github": "https://github.com/opentaiji/govmcp/commit/{hash}",
        "gitlab": "https://git.opentaiji.com/opentaiji/govmcp/-/commit/{hash}",
    }

    def __init__(
        self,
        output_file: Path | None = None,
        lang: str = "zh",
        include_commit_links: bool = True,
        unreleased_only: bool = False,
        commit_link_template: str = "github",
    ):
        self.output_file = output_file or OUTPUT_FILE
        self.lang = lang if lang in ("zh", "en") else "zh"
        self.include_commit_links = include_commit_links
        self.unreleased_only = unreleased_only
        self.commit_link_template = self.COMMIT_LINK_TEMPLATE.get(
            commit_link_template, self.COMMIT_LINK_TEMPLATE["github"]
        )

    def generate(self, from_tag: str | None = None) -> None:
        commits = self._get_commits(from_tag)
        categorized = self._categorize_commits(commits)
        version_suggestion = self._get_version_suggestion(from_tag, commits)
        diff_stats = self._get_diff_stats(from_tag)

        content = self._build_changelog(
            categorized,
            version_suggestion,
            diff_stats,
        )

        self.output_file.write_text(content, encoding="utf-8")
        print(f"[gen_changelog] Generated {self.output_file}")

        if version_suggestion.change_type != "none":
            print(f"[gen_changelog] Suggested version: {version_suggestion.suggested_version}")

    def _run_git(self, args: list[str]) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"[gen_changelog] Git error: {e}")
            return ""
        except FileNotFoundError:
            print("[gen_changelog] Error: git not found")
            return ""

    def _get_commits(self, from_tag: str | None = None) -> list[CommitInfo]:
        if from_tag:
            range_spec = f"{from_tag}..HEAD"
        else:
            range_spec = "HEAD"

        output = self._run_git(
            [
                "log",
                "--format=%H|%h|%s|%b|%an|%ai",
                "--reverse",
                range_spec,
            ]
        )

        if not output:
            return []

        commits = []
        for line in output.split("\n"):
            if not line.strip():
                continue
            parts = line.split("|", 5)
            if len(parts) >= 3:
                commit = self._parse_commit(parts)
                if commit:
                    commits.append(commit)

        return commits

    def _parse_commit(self, parts: list[str]) -> CommitInfo | None:
        if len(parts) < 3:
            return None

        hash_full = parts[0]
        hash_short = parts[1]
        subject = parts[2]
        body = parts[3] if len(parts) > 3 else ""
        author = parts[4] if len(parts) > 4 else ""
        date = parts[5] if len(parts) > 5 else ""

        commit_type, scope, is_breaking, message = self._parse_commit_message(subject)

        breaking_description = ""
        footer_notes = {}

        if body:
            for match in FOOTER_BREAKING_REGEX.finditer(body):
                is_breaking = True
                breaking_description = match.group(1).strip()

            footer_pattern = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)
            for match in footer_pattern.finditer(body):
                footer_notes[match.group(1)] = match.group(2).strip()

        return CommitInfo(
            hash_full=hash_full,
            hash_short=hash_short,
            type=commit_type,
            scope=scope,
            subject=message,
            body=body,
            is_breaking=is_breaking,
            breaking_description=breaking_description,
            footer_notes=footer_notes,
            author=author,
            date=date,
            files_changed=[],
            insertions=0,
            deletions=0,
        )

    def _parse_commit_message(self, subject: str) -> tuple[str, str | None, bool, str]:
        match = CONVENTIONAL_COMMITS_REGEX.match(subject)
        if match:
            commit_type = match.group(1)
            scope = match.group(2)
            is_breaking = match.group(3) == "!" or "BREAKING CHANGE" in subject.upper()
            message = match.group(4)
            return commit_type, scope, is_breaking, message

        return "other", None, False, subject

    def _categorize_commits(self, commits: list[CommitInfo]) -> dict[str, list[CommitInfo]]:
        categorized: dict[str, list[CommitInfo]] = {
            "breaking": [],
            "feat": [],
            "fix": [],
            "docs": [],
            "style": [],
            "refactor": [],
            "perf": [],
            "test": [],
            "build": [],
            "ci": [],
            "chore": [],
            "revert": [],
            "other": [],
        }

        for commit in commits:
            if commit.is_breaking:
                categorized["breaking"].append(commit)
            elif commit.type in categorized:
                categorized[commit.type].append(commit)
            else:
                categorized["other"].append(commit)

        return categorized

    def _get_version_suggestion(
        self, from_tag: str | None, commits: list[CommitInfo]
    ) -> VersionSuggestion | None:
        current_version = self._get_current_version(from_tag)
        if not current_version:
            return None

        return SemanticVersioner.suggest_version(commits, current_version)

    def _get_current_version(self, from_tag: str | None) -> str | None:
        if from_tag:
            version = from_tag.lstrip("v")
            if re.match(r"\d+\.\d+\.\d+", version):
                return version

        pyproject = PROJECT_ROOT / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8")
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)

        init_file = PROJECT_ROOT / "govmcp" / "__init__.py"
        if init_file.exists():
            content = init_file.read_text(encoding="utf-8")
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)

        return None

    def _get_diff_stats(self, from_tag: str | None) -> DiffStats | None:
        if from_tag:
            range_spec = f"{from_tag}..HEAD"
            return DiffAnalyzer.analyze(range_spec)
        return None

    def _build_changelog(
        self,
        categorized: dict[str, list[CommitInfo]],
        version_suggestion: VersionSuggestion | None,
        diff_stats: DiffStats | None,
    ) -> str:
        lines = []

        lines.extend(self._build_header())

        if version_suggestion:
            lines.extend(self._build_version_section(version_suggestion))

        lines.extend(self._build_unreleased_section(categorized, diff_stats))

        lines.extend(self._build_existing_releases())

        return "\n".join(lines)

    def _build_header(self) -> list[str]:
        if self.lang == "zh":
            return [
                "# Changelog",
                "",
                "所有重要的项目变更都会记录在此文件中。",
                "",
                "格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，",
                "本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/spec/v2.0.0.html)。",
                "",
            ]
        else:
            return [
                "# Changelog",
                "",
                "All notable changes to this project will be documented in this file.",
                "",
                "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),",
                "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
                "",
            ]

    def _build_version_section(self, version_suggestion: VersionSuggestion) -> list[str]:
        lines = []

        badge = self._get_version_badge(version_suggestion.change_type)

        if self.lang == "zh":
            lines.extend(
                [
                    f"## [{version_suggestion.suggested_version}] - {datetime.now().strftime('%Y-%m-%d')}",
                    "",
                    f"{badge}",
                    "",
                    f"**建议版本升级**: {version_suggestion.suggested_version} (基于 {version_suggestion.change_type} 类型变更)",
                    "",
                ]
            )

            if version_suggestion.breaking_changes:
                lines.append("### ⚠️ 破坏性变更")
                lines.append("")
                for change in version_suggestion.breaking_changes:
                    lines.append(f"- {change}")
                lines.append("")

            if version_suggestion.features:
                lines.append("### ✨ 新增")
                lines.append("")
                for feature in version_suggestion.features:
                    lines.append(f"- {feature}")
                lines.append("")

            if version_suggestion.fixes:
                lines.append("### 🐛 修复")
                lines.append("")
                for fix in version_suggestion.fixes:
                    lines.append(f"- {fix}")
                lines.append("")
        else:
            lines.extend(
                [
                    f"## [{version_suggestion.suggested_version}] - {datetime.now().strftime('%Y-%m-%d')}",
                    "",
                    f"{badge}",
                    "",
                    f"**Suggested Version Bump**: {version_suggestion.suggested_version} (based on {version_suggestion.change_type} changes)",
                    "",
                ]
            )

            if version_suggestion.breaking_changes:
                lines.append("### ⚠️ Breaking Changes")
                lines.append("")
                for change in version_suggestion.breaking_changes:
                    lines.append(f"- {change}")
                lines.append("")

            if version_suggestion.features:
                lines.append("### ✨ Added")
                lines.append("")
                for feature in version_suggestion.features:
                    lines.append(f"- {feature}")
                lines.append("")

            if version_suggestion.fixes:
                lines.append("### 🐛 Fixed")
                lines.append("")
                for fix in version_suggestion.fixes:
                    lines.append(f"- {fix}")
                lines.append("")

        return lines

    def _get_version_badge(self, change_type: str) -> str:
        badges = {
            "major": "[![Breaking](https://img.shields.io/badge/-20BREAKING-20-red)]",
            "minor": "[![Feature](https://img.shields.io/badge/-20FEATURE-20-green)]",
            "patch": "[![Patch](https://img.shields.io/badge/-20PATCH-20-blue)]",
            "none": "[![Unchanged](https://img.shields.io/badge/-20UNCHANGED-20-gray)]",
        }
        return badges.get(change_type, "")

    def _build_unreleased_section(
        self,
        categorized: dict[str, list[CommitInfo]],
        diff_stats: DiffStats | None,
    ) -> list[str]:
        lines = []

        if self.lang == "zh":
            lines.extend(
                [
                    "## [Unreleased]",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## [Unreleased]",
                    "",
                ]
            )

        has_changes = any(categorized[cat] for cat in categorized if cat not in ("other",))

        if not has_changes:
            if self.lang == "zh":
                lines.extend(
                    [
                        "### 新增",
                        "- 初始版本发布",
                        "",
                    ]
                )
            else:
                lines.extend(
                    [
                        "### Added",
                        "- Initial release",
                        "",
                    ]
                )
            return lines

        if categorized["breaking"]:
            lines.extend(self._build_breaking_section(categorized["breaking"]))

        if categorized["feat"]:
            lines.extend(self._build_type_section("feat", categorized["feat"], "feat"))

        if categorized["fix"]:
            lines.extend(self._build_type_section("fix", categorized["fix"], "fix"))

        other_types = ["docs", "style", "refactor", "perf", "test", "build", "ci", "chore"]
        other_commits = []
        for cat_type in other_types:
            other_commits.extend(categorized[cat_type])

        if other_commits:
            lines.extend(self._build_changed_section(other_commits, other_types))

        if categorized["revert"]:
            lines.extend(self._build_revert_section(categorized["revert"]))

        if categorized["other"]:
            lines.extend(self._build_other_section(categorized["other"]))

        if diff_stats:
            lines.extend(self._build_diff_stats_section(diff_stats))

        return lines

    def _build_breaking_section(self, commits: list[CommitInfo]) -> list[str]:
        lines = []

        if self.lang == "zh":
            lines.append("### ⚠️ 破坏性变更")
        else:
            lines.append("### ⚠️ Breaking Changes")
        lines.append("")

        for commit in commits:
            scope_str = f"**({commit.scope})** " if commit.scope else ""
            commit_link = (
                self._get_commit_link(commit.hash_short) if self.include_commit_links else ""
            )
            lines.append(f"- {scope_str}{commit.subject} {commit_link}")

            if commit.breaking_description:
                lines.append(f"  - {commit.breaking_description}")

        lines.append("")
        return lines

    def _build_type_section(
        self, type_key: str, commits: list[CommitInfo], section_key: str
    ) -> list[str]:
        lines = []
        type_info = COMMIT_TYPES.get(type_key, {})
        section_title = type_info.get(self.lang, type_info.get("en", type_key.capitalize()))

        if section_key == "feat":
            if self.lang == "zh":
                lines.append("### ✨ 新增")
            else:
                lines.append("### ✨ Added")
        elif section_key == "fix":
            if self.lang == "zh":
                lines.append("### 🐛 修复")
            else:
                lines.append("### 🐛 Fixed")
        else:
            lines.append(f"### {section_title}")

        lines.append("")

        for commit in commits:
            scope_str = f"**({commit.scope})** " if commit.scope else ""
            commit_link = (
                self._get_commit_link(commit.hash_short) if self.include_commit_links else ""
            )
            lines.append(f"- {scope_str}{commit.subject} {commit_link}")

        lines.append("")
        return lines

    def _build_changed_section(self, commits: list[CommitInfo], type_keys: list[str]) -> list[str]:
        lines = []

        if self.lang == "zh":
            lines.append("### 🔄 变更")
        else:
            lines.append("### 🔄 Changed")
        lines.append("")

        for commit in commits:
            scope_str = f"**({commit.scope})** " if commit.scope else ""
            commit_link = (
                self._get_commit_link(commit.hash_short) if self.include_commit_links else ""
            )
            lines.append(f"- {scope_str}{commit.subject} {commit_link}")

        lines.append("")
        return lines

    def _build_revert_section(self, commits: list[CommitInfo]) -> list[str]:
        lines = []

        if self.lang == "zh":
            lines.append("### ↩️ 回退")
        else:
            lines.append("### ↩️ Reverted")
        lines.append("")

        for commit in commits:
            scope_str = f"**({commit.scope})** " if commit.scope else ""
            commit_link = (
                self._get_commit_link(commit.hash_short) if self.include_commit_links else ""
            )
            lines.append(f"- {scope_str}{commit.subject} {commit_link}")

        lines.append("")
        return lines

    def _build_other_section(self, commits: list[CommitInfo]) -> list[str]:
        lines = []

        if self.lang == "zh":
            lines.append("### 📝 其他")
        else:
            lines.append("### 📝 Other")
        lines.append("")

        for commit in commits:
            commit_link = (
                self._get_commit_link(commit.hash_short) if self.include_commit_links else ""
            )
            lines.append(f"- {commit.subject} {commit_link}")

        lines.append("")
        return lines

    def _build_diff_stats_section(self, stats: DiffStats) -> list[str]:
        lines = []

        if self.lang == "zh":
            lines.extend(
                [
                    "### 统计",
                    "",
                    f"- 提交数: {stats.total_commits}",
                    f"- 文件变更: {stats.total_files} 个文件",
                    f"- 新增行数: +{stats.insertions}",
                    f"- 删除行数: -{stats.deletions}",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "### Statistics",
                    "",
                    f"- Commits: {stats.total_commits}",
                    f"- Files changed: {stats.total_files}",
                    f"- Insertions: +{stats.insertions}",
                    f"- Deletions: -{stats.deletions}",
                    "",
                ]
            )

        return lines

    def _build_existing_releases(self) -> list[str]:
        lines = []

        lines.extend(
            [
                "---",
                "",
            ]
        )

        if self.lang == "zh":
            lines.extend(
                [
                    "## 历史版本",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## Older Entries",
                    "",
                ]
            )

        tags = self._get_tags()
        if tags:
            for tag in tags[:10]:
                tag_version = tag.lstrip("v")
                lines.append(f"- [{tag_version}]({self._get_tag_link(tag)})")
        else:
            if self.lang == "zh":
                lines.extend(
                    [
                        "### [1.0.0] - 2024-01-01",
                        "",
                        "### 新增",
                        "- 基本 MCP 协议实现",
                        "- SM2/SM3/SM4 加密原语",
                        "- 服务器端 MCP 协议处理器",
                        "- 工具注册系统",
                        "- 审批工作流引擎",
                        "- 不可篡改审计链",
                        "",
                    ]
                )
            else:
                lines.extend(
                    [
                        "### [1.0.0] - 2024-01-01",
                        "",
                        "### Added",
                        "- Basic MCP protocol implementation",
                        "- SM2/SM3/SM4 cryptographic primitives",
                        "- Server-side MCP protocol handler",
                        "- Tool registry system",
                        "- Approval workflow engine",
                        "- Immutable audit chain",
                        "",
                    ]
                )

        return lines

    def _get_tags(self) -> list[str]:
        output = self._run_git(["tag", "--sort=-version:refname"])
        if not output:
            return []
        return [tag.strip() for tag in output.split("\n") if tag.strip()]

    def _get_commit_link(self, hash_short: str) -> str:
        link = self.commit_link_template.format(hash=hash_short)
        return rf"[\`{hash_short}\`]({link})"

    def _get_tag_link(self, tag: str) -> str:
        if "github" in self.commit_link_template:
            return f"https://github.com/opentaiji/govmcp/releases/tag/{tag}"
        return "#"

    def _get_tags_with_dates(self) -> dict[str, str]:
        output = self._run_git(["tag", "-l", "--format=%(refname:short) %(creatordate:short)"])
        tags = {}
        for line in output.split("\n"):
            parts = line.split()
            if len(parts) >= 2:
                tags[parts[0]] = parts[1]
        return tags


def main():
    parser = argparse.ArgumentParser(description="govmcp CHANGELOG Generator")
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help=f"Output file (default: {OUTPUT_FILE})",
    )
    parser.add_argument(
        "--from-tag",
        help="Generate from specified tag (default: all commits)",
    )
    parser.add_argument(
        "--lang",
        choices=["zh", "en"],
        default="zh",
        help="Language (default: zh)",
    )
    parser.add_argument(
        "--include-links",
        action="store_true",
        default=True,
        help="Include commit links (default: true)",
    )
    parser.add_argument(
        "--no-links",
        action="store_true",
        help="Exclude commit links",
    )
    parser.add_argument(
        "--unreleased",
        action="store_true",
        help="Only show unreleased changes",
    )
    parser.add_argument(
        "--link-template",
        choices=["github", "gitlab"],
        default="github",
        help="Commit link template (default: github)",
    )
    args = parser.parse_args()

    generator = ChangelogGenerator(
        output_file=args.output,
        lang=args.lang,
        include_commit_links=not args.no_links,
        unreleased_only=args.unreleased,
        commit_link_template=args.link_template,
    )

    generator.generate(from_tag=args.from_tag)

    return 0


if __name__ == "__main__":
    sys.exit(main())
