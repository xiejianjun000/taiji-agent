"""govmcp 文档生成脚本"""

from scripts.gen_api_docs import main as gen_api_docs_main
from scripts.gen_changelog import main as gen_changelog_main
from scripts.generate_docs import main as generate_docs_main
from scripts.update_readme import main as update_readme_main

__all__ = [
    "generate_docs_main",
    "gen_api_docs_main",
    "gen_changelog_main",
    "update_readme_main",
]
