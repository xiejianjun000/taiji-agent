# OpenTaiji Python Package

## 目录结构

```
opentaiji-python/
├── src/opentaiji/           # 源代码
│   ├── agent/              # Agent 引擎
│   ├── wfgy/               # WFGY 防幻觉
│   ├── souls/              # Soul 人格
│   ├── memory/             # 记忆系统
│   ├── learning/           # 自我学习
│   ├── tools/              # 工具系统
│   ├── providers/          # LLM 提供商
│   │   └── chinese/       # 国产模型
│   ├── gateway/            # 消息网关
│   ├── skills/             # 技能系统
│   ├── events/             # 事件总线
│   └── cli/                # CLI
├── tests/                  # 测试
│   └── stress_test.py      # 压力测试
├── scripts/                # 脚本
│   ├── generate_readme.py  # README 生成器
│   ├── pre-commit.py       # 预提交钩子
│   └── install-hooks.sh    # 钩子安装
└── pyproject.toml          # 项目配置
```

## 开发流程

### 1. 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 2. 运行测试

```bash
# 运行所有测试
pytest

# 运行压力测试
python tests/stress_test.py

# 生成 README
python scripts/generate_readme.py
```

### 3. 安装 Git 钩子

```bash
bash scripts/install-hooks.sh
```

### 4. 提交代码

```bash
git add .
git commit -m "描述"
# README 会自动更新
```

## 贡献

欢迎提交 Pull Request！
