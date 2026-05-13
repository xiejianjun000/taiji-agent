#!/usr/bin/env bash
# OpenTaiji Git 钩子安装脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo "🔧 安装 Git 钩子..."

# 创建 hooks 目录（如果不存在）
mkdir -p "$HOOKS_DIR"

# 复制 pre-commit 钩子
cp "$SCRIPT_DIR/pre-commit.py" "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-commit"

# 尝试让钩子可执行
chmod +x "$SCRIPT_DIR/pre-commit.py" 2>/dev/null || true

echo "✅ Git 钩子已安装!"
echo ""
echo "现在每次提交 Python 代码时，README.md 会自动更新"
echo ""
echo "跳过钩子方法: git commit --no-verify -m 'message'"
