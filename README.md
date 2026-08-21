# archive —— 记忆层（宪法 §1）

> 层：L1 记忆层 ｜ org: `Cloudbird-Software` ｜ 建仓：W1-C1（.github#164，ADR-0053） ｜ 状态真源：`agent-registry/decisions/INDEX.yaml`

## 角色

宪法（`specs/IR-0003/constitution.md`）§1 结构分层的记忆层，四类内容落位于此：

| 内容 | 目录/落位 | 状态 |
|---|---|---|
| **ADR 归档正本**（全部历史 ADR，字节保真） | `adr/` | W1-C1 首批迁移 |
| 规划回归集（Top-N 历史意图重放样本） | 后续波次 | 未落位 |
| 事件 JSONL（审计/飞轮原料快照） | 后续波次 | 未落位 |
| 红队报告 | 后续波次 | 未落位 |

宪法 §13 推论二：本仓不只是治理副产物仓库——事件 JSONL、golden 集、校准集、
红队报告、规划回归集是**训练与评估飞轮的原料**，属战略资产。

## append-only 约定

- **只增不删不改**：任何文件一经合入永不删除、永不 rewrite（含重命名/移动）。
- 历史文件需要修正时新增勘误文件，不改动原件。
- 宪法 §10.1（供应商单点缓解）：本仓内容属"关键产物可异地备份"范围，
  异地备份策略由后续波次落位（本 README 占位注记）。
- 变更一律走 PR（本 README 的建仓 bootstrap commit 是唯一豁免直推，
  已登记 `.github` 仓 `governance/expected-state.json` direct_push_exemptions）。

## 目录约定

```
adr/                     # ADR 归档正本（字节保真——与迁移时 agent-registry/decisions/ 源文件逐字节一致）
scripts/verify_migration.py  # 迁移保真校验（INDEX ↔ adr/ ↔ 源 commit 三向 sha256 闭环）
.github/workflows/verify.yml # PR + push + weekly 跑 verify_migration.py
```

**ADR 状态不写在本仓文件里**（保持字节一致）；每个 ADR 的
`lifecycle: active|superseded|archived` 与 `decision_status: accepted|proposed`
唯一真源 = `agent-registry/decisions/INDEX.yaml`（墓碑索引，ADR-0053）。
新 ADR 的落位流程见 ADR-0053 决策 3：正本入本仓 `adr/` + agent-registry 落墓碑
+ INDEX.yaml 登记 entry。
