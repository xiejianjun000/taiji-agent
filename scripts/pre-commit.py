#!/usr/bin/env python3
"""
预提交钩子 - 在提交前自动更新 README

使用方法:
    python scripts/pre-commit.py

或者添加到 .git/hooks/pre-commit:
    #!/bin/sh
    python scripts/pre-commit.py
"""

import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def run_generate_readme():
    """运行 README 生成器"""
    print("🔄 检测到代码变更，正在更新 README...")
    
    script_path = PROJECT_ROOT / "scripts" / "generate_readme.py"
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    
    if result.returncode == 0:
        print(result.stdout)
        
        # 检查 README 是否变更
        result = subprocess.run(
            ["git", "diff", "--name-only", "README.md"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        
        if result.stdout.strip():
            print("📝 README.md 已更新，自动添加到暂存区...")
            subprocess.run(
                ["git", "add", "README.md"],
                cwd=PROJECT_ROOT,
            )
            return True
    else:
        print(f"⚠️  README 生成失败: {result.stderr}")
    
    return False


def check_staged_changes():
    """检查暂存区变更"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    
    staged_files = result.stdout.strip().split("\n")
    python_files = [f for f in staged_files if f.endswith(".py") and f.startswith("src/")]
    
    return len(python_files) > 0


def main():
    """主函数"""
    # 检查是否有 Python 文件变更
    if check_staged_changes():
        run_generate_readme()
    else:
        print("✅ 没有检测到 Python 代码变更，跳过 README 更新")


if __name__ == "__main__":
    main()
