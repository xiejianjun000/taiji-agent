# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- feat: MCP 2025.11 异步任务支持 (govmcp/protocol/tasks.py)
  - TaskStatus 枚举: pending, working, completed, failed, canceled
  - TaskInfo 数据类: 包含 id, status, progress, result, error 等
  - TaskManager 类: create_task, get_task_status, get_task_result, cancel_task, list_tasks, cleanup_completed_tasks
  - SSE 实时推送任务状态变更
- feat: MCP 2025.11 采样支持 (govmcp/protocol/sampling.py)
  - SamplingMessage, SamplingCreateMessageRequest
  - SamplingParameters 参数配置
  - 异步采样支持
- feat: MCP 2025.11 用户交互支持 (govmcp/protocol/elicitation.py)
  - ElicitRequest 用户交互请求
  - URL Mode Elicitation
  - 安全带外交互
- feat: MCP 2025.11 授权扩展 (govmcp/protocol/authorization.py)
  - OAuth 2.0 授权码流程
  - FineGrainedPermissionManager 细粒度权限控制
  - Authorization Extensions
- feat: GovMCPServer 集成新端点
  - /tasks/create, /tasks/status, /tasks/cancel, /tasks/subscribe
  - /sampling/createMessage
  - /elicitation/create, /elicitation/respond
  - /authorization/check
- test: 添加 64 个异步任务相关测试 (tests/test_tasks.py)
- feat: 更新协议版本至 2025.11

### Fixed
- fix: tools/call response uses json.dumps instead of str() (`bcc1134`)
- fix: use npm install instead of npm ci for lock file compatibility (`a9dab6f`)

### Changed
- docs: add CHANGELOG (`4c4c489`)
- docs: add pull request template (`b88b70c`)
- docs: add bug report issue template (`a22bc33`)
- docs: add feature request issue template (`fb2fa2a`)
- docs: 添加架构文档和贡献指南 (`3af08ba`)
- ci: add Dependabot configuration for pip and GitHub Actions (`f97b4c7`)
- ci: add stale issue/PR automation (`46cc2da`)
- ci: update Dependabot with automerged-updates (`1e396cd`)

### Other
- govmcp v1.0 — 国产信创MCP协议首次发布 (`3c0e6fb`)

---

## [1.0.0] - 2024-01-01

### Added
- Basic MCP protocol implementation
- SM2/SM3/SM4 cryptographic primitives
- Server-side MCP protocol handler
- Tool registry system
- Approval workflow engine
- Immutable audit chain