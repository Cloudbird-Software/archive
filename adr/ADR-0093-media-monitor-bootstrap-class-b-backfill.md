# ADR-0093: Media-Monitor 建仓 bootstrap 直推 (b) 类豁免追认与幽灵引用消除

- status: accepted
- date: 2026-08-26
- deciders: owner（randypanding，2026-08-26 会话内明示授权）/ 治理巡检 agent 会话（回填登记）
- resolves: drift-check §8 报警的 Media-Monitor 非 PR commit 30dfa385 按附录机制完成回填；消除该 commit message 中的幽灵 ADR 编号引用（原引用 0093 时本 ADR 尚不存在）
- 关联: ADR-0092（同日 bootstrap 直推回填先例，(b) 类定性援引其决策 1）；ADR-0016（§8 豁免清单附录机制）；ADR-0017（直推事件定性与回填语义）

## 背景

Media-Monitor（多平台媒体与受众监控工具，go stdlib-only）于 2026-08-25 建仓。
建仓 bootstrap 直推一笔：

- `30dfa3858d6299dbe3bdfdd47bcd79a89d7f4953`（2026-08-25 16:46:41Z，
  author=committer=cloudbrid-agent[bot]）"chore: bootstrap template-service
  baseline for Media-Monitor (ADR-0093, bootstrap class b)"——template-service
  模板基线落 main（gate（CI-Workflows@v1 聚合）/AGENTS.md 入口协议块/CODEOWNERS/
  dependabot）。

commit message 引用了当时尚未写成的 ADR 编号 0093（预占编号未落地）——
2026-08-25 17:52 的 .github gate（adr-required，PR #381 首验）以「幽灵 ADR」
拒绝该引用，治理面存在两处缺口：§8 直推未回填、编号引用无正本。

回填链已完成的部分：
- 回填 PR [Media-Monitor#1](https://github.com/Cloudbird-Software/Media-Monitor/pull/1)
  "bootstrap: media-monitor product baseline on org template" 已合并；
- REPOS.yaml 已申报（layer L2 / status active / role 注明治理面随 bootstrap 落地）；
- §8 豁免登记 PR [.github#381](https://github.com/Cloudbird-Software/.github/pull/381)
  已合并（direct_push_exemptions 逐完整 SHA 登记，最初援引 ADR-0092）。

## 决策

1. **追认为 (b) 类建仓时序豁免**（ADR-0092 决策 1 同款定性）：空仓首推时 PR
   不可行；org-required-workflows 于 ADR-0090 后已有 OrganizationAdmin bypass，
   bootstrap 直推合法——按 (b) 类逐 SHA 登记（已由 .github#381 落地）。
2. **本 ADR 即编号 0093 的正本**：补齐 commit message 引用的落点，消除幽灵
   引用；INDEX.yaml 同步登记（content_sha256 锚定字节保真，ADR-0053 机制）。
3. **教训登记**：预占 ADR 编号必须与 ADR 正本同一变更落地，否则编号引用即
   幽灵（adr-required fail-closed 拒绝）；建仓会话应先写 ADR 再推 commit，
   或 commit message 只引既有 ADR。

## 影响

- drift-check §8 对 Media-Monitor 的报警闭环（豁免登记 + ADR 背书齐备）。
- gate adr-required 对「ADR-0093」字面引用自此可解析（INDEX 命中 + active）。
- 不改变任何既有 ADR 的状态与内容。
