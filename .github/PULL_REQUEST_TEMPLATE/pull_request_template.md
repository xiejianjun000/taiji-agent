name: 🚀 OpenTaiji Pull Request
description: 提交 Pull Request
title: "[PR] "
labels: ["pr"]
body:
  - type: markdown
    attributes:
      value: |
        ## 📝 Pull Request 描述

  - type: textarea
    id: description
    attributes:
      label: 详细描述
      placeholder: |
        请描述这个 PR 的内容和目的。
        
        - 修复了什么问题？
        - 增加了什么功能？
        - 有什么 Breaking Changes？
    validations:
      required: true

  - type: textarea
    id: type
    attributes:
      label: PR 类型
      placeholder: |
        - [ ] Bug 修复 (bug fix)
        - [ ] 新功能 (new feature)
        - [ ] 文档更新 (documentation)
        - [ ] 代码重构 (refactoring)
        - [ ] 性能优化 (performance)
        - [ ] 测试更新 (test)
        - [ ] 构建/CI (build/ci)
    validations:
      required: true

  - type: textarea
    id: testing
    attributes:
      label: 测试说明
      placeholder: |
        请描述你进行了哪些测试来验证这个 PR。
    validations:
      required: false

  - type: textarea
    id: checklist
    attributes:
      label: 检查清单
      placeholder: |
        - [ ] 代码通过 ruff 检查
        - [ ] 代码通过 mypy 类型检查
        - [ ] 所有测试通过
        - [ ] 添加了必要的单元测试
        - [ ] 更新了相关文档
    validations:
      required: false

  - type: input
    id: related
    attributes:
      label: 关联的 Issue
      placeholder: 相关的 Issue 编号（如 #123）
    validations:
      required: false
