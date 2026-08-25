# ADR-0089: 2026-08-25 晨间直推批次回填——archive INDEX 补登记与 QW_Arena1 比赛内容落盘

- status: accepted
- date: 2026-08-25
- deciders: owner（事件落盘）/ PM 会话（回填登记）
- resolves: drift-check §8 报警的 4 个非 PR commit（archive 1d24dea9 / QW_Arena1 eb5da0dc、ed67646d、63397801）按 ADR-0016 附录机制完成回填（本 ADR + expected-state.json §8 豁免登记 PR）

## 背景

owner 2026-08-25 晨间会话（约 05:52–07:13Z）在两个仓直接落盘 4 个 commit（均未经 PR）：

**archive 仓（治理文件，1 笔）**：
- `1d24dea9a1515714749be6e3964efb0a83ceceb1`（07:13）"docs: add ADR-0087 to INDEX.yaml"——ADR-0087 正本此前已经 archive#21（PR）合入，但 INDEX.yaml 登记漏随该 PR，事后直推补登记。

**QW_Arena1 仓（比赛内容文档，3 笔）**：
- `eb5da0dc9f42a88129648a04b0783bdb6bb8c40b`（05:52）"Create machine-readable brief for AI competition"——千问 AI Arena 比赛机读摘要（IR #345 冻结契约的执行材料）；
- `ed67646d796f9e9d2ec48bdf8073a20d40ce0399`（05:53）"Create Arena_Detail.md"——比赛细节文档；
- `63397801a130db173341ee1ff680c02100b8e0ea`（06:56）"Update Plan.md"——参赛计划更新。

## 决策

1. 追认该 4 次直推为破玻璃事件（ADR-0006 语义），回填 = 本 ADR + .github expected-state.json §8 豁免登记 PR（同日提交，24h 时限内）。
2. 净变更定性：archive 1 笔为纯登记性 INDEX 补录（正本路径与 sha 与 PR #21 合入版一致，无决策内容变更）；QW_Arena1 3 笔为比赛内容文档（不触及治理/workflow/依赖面）。与 ADR-0088 同日的 CI-Workflows 4 笔（adversary 模型切换）合计为本日全部 §8 报警项。
3. 教训登记：INDEX.yaml 登记应与 ADR 正本同 PR 提交（archive#21 的遗漏导致补登记直推）；内容文档亦应走 PR——QW_Arena1 已有 PR 能力（bootstrap 豁免期已过）。

## 后果

- §8 对这 4 个 commit 的后续每日报警（至 2026-09-01 滑出 7 天检测窗口）视为已回填已知项。
- 本 ADR 与 ADR-0088 同为 2026-08-25 直推回填批次；两 ADR 的豁免登记合并于同一 .github PR。
