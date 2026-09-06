# fractures —— 断裂登记簿（IR-0009 卡 A7；STRAT §8.3 的 DGA 语义开通）

**规则**：发现 → 登记（任何人/agent 可写条目，经 PR）→ 月度理论审议（S5 主持）→ 二选一裁决
（**实例修正** / **理论升版**），**禁止第三选项**（"实践例外"）。

- `LEDGER.jsonl`：append-only hash 链（INV-03 同款，链断=红）；`scripts/verify_fractures.py` 随时巡检；
- 条目字段：编号（FR-NNNN）/ 冲突描述 / 双方依据 / 裁决引用（ADJUDICATION §x）/ 状态（open|closed）/ 日期；
- `type: meta` 行承载建制性注记（如 IR 编号偏移、委托执行授权）；
- 阻塞性断裂（阻止波次推进）48 小时内裁决，非阻塞维持月度审议（MIG §7 迁移期条款沿用）。

首批条目：FR-001~008（closed，裁决=DGA-ADJUDICATION v1.0）+ FR-009（open：DGA 人类版原文缺件）。
