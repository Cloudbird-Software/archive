# ADR-0106: butler deadman_stale_hours 阈值勘误（3→24）与破玻璃直推 (a) 类回填追认

- status: accepted
- date: 2026-09-02
- deciders: owner（randypanding，issue 全量巡检会话授权"能复现的就修复"）/ issue 巡检 agent 会话（修复与回填登记）
- resolves: .github#482（P0 dead-man 假 trip，AUTO_MERGE_DISABLED=true 两连发）的根因修复；.github 仓直推 `847e028` 按附录机制完成 (a) 类回填
- 关联: ADR-0074（dead-man 双层信号链：外部 hc.io 快速层 + 仓内 watch 兜底层）；ADR-0057（宪法 §6 缺席即停）；ADR-0016（§8 豁免清单附录机制）；ADR-0017（直推事件定性与回填语义）；ADR-0093（(b) 类回填先例，本追认为 (a) 类）

## 背景

butler-heartbeat-watch（仓内兜底层，ADR-0074 决策 2 第二层）按
`governance/policy/butler.yaml#thresholds.deadman_stale_hours`（原值 3）检查
butler-heartbeat 最近成功 run 的陈旧度，超阈即调 `governance/deadman-trip.sh`
缺席即停（置 org 变量 AUTO_MERGE_DISABLED=true + 撤 auto-merge + 开 P0）。

原值 3 的假设是 heartbeat cron `*/30` 严格节拍（"连续 6 次缺失"）。但 GitHub
scheduled runs 延迟显著且不受租户控制——实测 9 天/100 次成功 run
（2026-08-24~09-02）：最大间隔 11.4h，25/99 次间隔 >3h。watch 自身 6h 节拍，
间歇观测到"最近成功 >3h"即把 cron 延迟误判为管家缺席：

- 2026-08-31T14:23Z 首次假 trip（.github#482 开立）；
- 2026-09-02T05:02Z 二次假 trip（变量再置位、issue 再评论）。

核验：butler-heartbeat 全程健康（无 workflow 损坏/token 失效），外部层
DEADMAN_PING_URL 已配置——非真缺席，纯阈值误配。假 trip 的代价是整条
automerge 流水线停摆且复位仅人工，误报成本远高于检出延迟收益。

## 决策

1. **阈值勘误 3→24**：2× 观测最坏间隔（11.4h）取上取整，杜绝 cron 延迟误判；
   真缺席的仓内检出延至 ≤30h（watch 6h 节拍），快速检出由外部 dead-man 层
   （hc.io，grace 侧）承担——与 ADR-0074 双层分工一致（仓内层只覆盖
   "Actions 活着但心跳工作流死了"形态，不追求快）。
2. **破玻璃直追认 (a) 类**：修复提交 `847e028`（policy(butler): deadman_stale_hours
   3→24——cron 延迟误判假 trip 勘误）于 2026-09-02 直推 .github main——彼时熔断
   生效中（agent 派发与 automerge 前置检查拒绝启动），走 PR 流程会被自身要修复的
   熔断链拦阻，且 P0 停摆每多一小时损失越大，故破玻璃直推。按 (a) 类逐 SHA 登记
   于 expected-state.json direct_push_exemptions['.github']（本 ADR 即背书）。
3. **复位留痕**：AUTO_MERGE_DISABLED=false 已于 2026-09-02T16:56:39Z PATCH 复位，
   .github#482 留复位评论后关闭（runbook docs/deadman-setup.md 步骤 2/3 完成）。

## 影响

- watch 后续轮次按新阈值校验，cron 延迟不再触发假 trip；真缺席检出 SLA 由
  外部层承担（仓内层 ≤30h 兜底）。
- .github 仓 §8 直推报警对 `847e028` 闭环（豁免登记 + ADR 背书齐备）。
- 教训登记：依赖 GitHub cron 节拍的阈值必须按"实测最坏间隔 × 安全系数"整定，
  不得按 cron 表达式名义节拍整定（scheduled runs 延迟是平台常态，非故障）。
