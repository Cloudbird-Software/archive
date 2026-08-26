# ADR-0098: Media-Monitor license 门禁全量拆除

- status: accepted
- date: 2026-08-26
- deciders: owner（randypanding，2026-08-26 会话内明示）/ IR-MM-0001 实现会话 agent（登记）
- resolves: IR-MM-0001（Cloudbird-Software/Media-Monitor#16）AC-1 的治理背书——license 门禁拆除属 C1 级决策，需 ADR 正本供后续 PR 引用
- 关联: ADR-0093（Media-Monitor 建仓背景）；IR-MM-0001 D-1（拆除决策原文）

## 背景

Media-Monitor 建仓基线自带 license 门禁（internal/license 包 +
cmd/mediad / cmd/mediad-mcp / cmd/mediactl 三入口 wiring +
MEDIAMON_LICENSE_DIR / MEDIAMON_LICENSE_PUBKEY / MEDIAMON_LICENSE_REQUIRED
三环境变量）：全部采集与动作类 MCP 工具（search_items / comments / replies /
users / group_members / resolve_video / collects / im_unread / send_message）
被 gate fail-closed 包裹，无 license 配置即拒绝调用。

IR-MM-0001（原子采集 MCP 化·账号历史回溯·上游双轨适配·真机自优化实验室）
要求采集原子对 AI 消费方一等公民开放（MCP 工具面为默认通道）——license
门禁与该意图直接冲突。owner 于 2026-08-26 会话明示拆除。

## 决策

1. **license 门禁全量拆除**：internal/license 包（gate.go / license.go 及
   其测试）删除；三个 cmd 的 wireLicense / loadLicenseGate 等 wiring 全清；
   MEDIAMON_LICENSE_* 三环境变量失效（设置后无行为变化）；
   cmd/mediad-mcp 的 gatedTools 名单与 gateWrap 逻辑删除。
2. **docs/HARDENING.md 保留**：作为未来 license 重建的规范位（交付管线
   打包层的重建契约），本 ADR 不删除该文档。
3. **重建路径**：未来 license 经 HARDENING 交付管线在打包层重建（部署物
   携带、非源码仓门禁）；在此之前仓库无 license 语义。
4. **质量关卡不降级**：hygiene / zizmor / gitleaks 关卡保持原强度
   （拆除的是产品 license 门禁，非 CI 质量门禁）。

## 影响

- IR-MM-0001 AC-1 可实施：全部采集与动作类 MCP 工具在无 license 配置下
  直接可调用。
- gated 工具名单（docs/ARCHITECTURE.md / README.md 中 license 描述）同步
  清除；后续 PR 触碰 docs/（C1 路径）引用本 ADR。
- 既有 license 协议文档（docs/LICENSE-PROTOCOL.md）仅存档用途，不构成
  运行时行为。
- 本仓（Media-Monitor）与 archive 仓互不新增依赖；无代码影响面外溢。
