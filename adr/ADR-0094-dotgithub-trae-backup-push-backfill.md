# ADR-0094: .github 仓 trae 会话终止备份直推回填

- status: accepted
- date: 2026-08-26
- deciders: owner（randypanding，2026-08-26 会话内明示授权）/ 治理巡检 agent 会话（回填登记）
- resolves: drift-check §8 报警的 .github 非 PR commit 89f57e6c 按附录机制完成回填（.github #383）
- 关联: ADR-0092（直推批次回填先例与 (a)/(b) 类定性）；ADR-0016（§8 豁免清单附录机制）；ADR-0017（直推事件定性与回填语义）

## 背景

2026-08-25 17:39Z，trae 会话（traeagent）终止前向 .github main 直推一笔：

- `89f57e6c2fd4dd8d1e5d329e54a63d21ee0fb68b`（author/committer=traeagent via
  Co-authored-by）"chore: pre-termination backup"

净变更为两个**二进制工具产物**的 blob 更新（`.trae-html-share-packages/scripts/
create-cloudbird-agent-app.html.zip`、`create-verifier-app.html.zip`，git 统计
+0/-0 行）——Trae IDE 的会话分享包缓存，非治理规则、非脚本、非文档面。

## 决策

1. **追认为 (a) 类破玻璃事件**（ADR-0006 语义，ADR-0092 决策 2 同款）：净变更
   为工具产物备份，零治理面触碰；回填 = 本 ADR + .github expected-state.json
   §8 豁免登记 PR。
2. **教训登记**：IDE 工具的会话产物目录（`.trae-*`）不应进入治理仓工作树——
   建议后续将其加入 .gitignore 或迁移至仓外存储；该加固属 .github 仓常规 PR，
   不在本 ADR 范围。

## 影响

- drift-check §8 对该笔报警闭环（豁免登记 + ADR 背书齐备）。
- 不改变任何既有 ADR 状态与内容。
