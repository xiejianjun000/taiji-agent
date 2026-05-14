# govmcp · 政务MCP协议

> 仓库: git.opentaiji.com (私有)  
> 创建: 2026-04-30  
> 定位: 中国政务 MCP 标准

---

## 核心差异化

| 标准 MCP | govmcp |
|:---|:---|
| 无加密要求 | 国密 SM2/SM3/SM4 |
| 无审批流程 | 内置审批工作流 |
| 无审计要求 | 不可篡改审计链 |
| 通用 LLM | 信创适配（19国产 LLM） |
| 无防幻觉 | 集成 WFGY 防幻觉引擎 |

## 在 TaijiVerify 中的角色

TaijiVerify 通过 govmcp 作为协议出口：
- `mcp-taiji-verify/tools/audit_text`
- `mcp-taiji-verify/tools/audit_visual`
- `mcp-taiji-verify/tools/governance_check`

→ 最终目标：任何支持 MCP 的 AI 应用可通过 govmcp 直接调用 TaijiVerify 的防虚幻能力。
