# evalsets/trust-shadow —— 信任门 shadow 决策记录资产与口径

- 状态: active（W5-C2，Cloudbird-Software/.github#225 / ADR-0071）
- 数据生产者: CI-Workflows `.github/workflows/trust-shadow`（纯 shadow，不执行合并）+
  `pipeline/trust-gate/trust_gate.py`（判定/reconcile/unlock-evaluate 引擎，零 LLM）
- 消费者: `trust_gate.py reconcile`（owner 裁决比对）/ `unlock-evaluate`（域解锁判定）/
  `sample`（解锁后 5% 抽审）；北极星对「每周零人类接触合并数」的分母原料（宪法 §8）
- 替代对象: spec v3 risk-score 标量 + ceiling 40（spec v4 修订 1 宪法明裁废除——
  标量把「未知」折叠成「安全」；本资产是其后继：准入=谓词清单，缺证据=拒绝）

## 机制口径（ADR-0071）

- **准入谓词**（真源 = CI-Workflows `pipeline/trust-gate/predicates.yaml`，版本化）：
  全关卡绿 ∧ 证据清单齐全 ∧ 已解锁域。每项证据=一个谓词键；缺位/false=拒绝
  （不是中性、不是降级），报告逐项列出缺失谓词键。
- **shadow 纪律**：域未解锁时判定照常运行，决策以 `would-merge`/`would-reject`
  形态记录（`executed:false` 恒真——引擎与 workflow 均无合并调用权）。
- **解锁判据**：连续 ≥50 例与 owner 裁决一致 且 零逃逸（owner 拒而谓词放行=逃逸）
  且 窗口内陷阱占比 ≥10% → 解锁；任一逃逸/不一致/owner 放行陷阱 → 连击清零
  并落 reset 事件。已解锁域 5% 随机抽人审（sha256 PRF，种子注入=可复现）。
- **永远人签域**（宪法 §5 明确排除，谓词表硬编码）：新功能实现、依赖升级、
  触及公开 API/schema、触及 CI-Workflows 的改动。
- **熔断联动**（ADR-0040）：`AUTO_MERGE_DISABLED` 置位或不可确认 → 判定直接拒绝
  （circuit-breaker-tripped）——只准降级为人签，不准降级为少验。

## 数据格式（trust-shadow/v1 JSONL）

workflow 产出 artifact `trust-shadow/<YYYY-MM-DD>.jsonl`（UTC 日切，逐 run 追加），
本目录为 schema 口径正本（数据经 PR 汇入 archive 时按此校验；append-only）。
每行一个 JSON 对象，`record` 区分五类：

```jsonc
// record=decision —— 一次 shadow 判定（AC-2 原子；由 shadow-record 子命令产出）
{"schema":"trust-shadow/v1","record":"decision","ts":"…","repo":"ORG/REPO","pr":123,
 "head_sha":"<40hex>","run_id":"…","event":"pull_request","domain":"docs-only",
 "mode":"shadow|enforced|excluded","decision":"would-merge","reason":"predicates-ok-shadow",
 "missing_predicates":[],"required_predicates":["gates.gate","diff.ast-equivalence.proven",…],
 "breaker_tripped":false,"trap":false,"sample_review":false,"executed":false}

// record=ruling —— owner 实际裁决（PR merged/closed 后导出；reconcile 的比对输入）
{"schema":"trust-shadow/v1","record":"ruling","ts":"…","repo":"ORG/REPO","pr":123,
 "ruling":"merged|closed","by":"randypanding"}

// record=reconcile —— shadow 决策 × owner 裁决比对结果（reconcile 子命令产出）
{"schema":"trust-shadow/v1","record":"reconcile","ts":"…","repo":"…","pr":123,
 "domain":"docs-only","shadow_decision":"would-merge","owner_ruling":"closed",
 "counted":true,"agreement":false,"escape":true,"trap":false,
 "trap_passed_by_predicate":false,"trap_released_by_owner":false}

// record=unlock —— 解锁/重置事件（unlock-evaluate 子命令产出）
{"schema":"trust-shadow/v1","record":"unlock","ts":"…","domain":"docs-only",
 "event":"unlocked|reset-escape|reset-trap|reset-disagreement","streak_after":50,
 "trigger":{"repo":"…","pr":999,"ts":"…"},   // reset 事件的触发样本（unlocked 无此键，
 "window":50,"traps_in_window":5,"trap_ratio":0.1}  // 代之以 window/traps 统计

// record=sample —— 解锁后 5% 抽审选择（sample 子命令产出；同种子可复现）
{"schema":"trust-shadow/v1","record":"sample","ts":"…","domain":"docs-only",
 "seed":"2026W35","rate":0.05,"total":200,"selected":[17,88,…],"selected_ratio":0.05}
```

约定：

- `executed` 恒为 `false`——shadow 管线无执行权（合并动作不在任何 shadow 记录里出现；
  解锁域的 auto-merge 执行由合并机器人另行审计，不在本 JSONL 伪装）。
- `counted=false`（排除域/human-sign 形态）的 reconcile 行不进域计数，但保留
  （完整审计流，选择性记录=数据被污染的第一步——ADR-0071 风险条款）。
- 陷阱（`trap:true`）由周演习（ADR-0069 种子缺陷台账）在 reconcile 侧标注，
  **不经 PR 作者可影响的通道注入**（作者自标 trap 可稀释解锁判据或制造 reset DoS）。
- `ruling` 只允许 `merged`/`closed`，同 PR 双裁决=输入非法（append-only 不改判）。

## 比对与解锁口径

- **一致**：`would-merge|auto-merge` ↔ `merged`，或 `would-reject|reject` ↔ `closed`。
- **逃逸**：owner `closed` 而谓词放行形态——零逃逸是解锁必要条件；陷阱被谓词
  放行（`trap_passed_by_predicate`）计入逃逸（「本应拒却谓词全绿」的实弹证据）。
- **重置**：任何不一致清零连击；owner 放行陷阱（`trap_released_by_owner`）额外落
  `reset-trap` 事件（AC-3——防 shadow 对齐退化为「人也被带着放行」）。
- **陷阱占比**：解锁窗口内 `trap` 行 / 窗口总行 ≥ 10%；占比不足=样本不合格，
  不解锁（fail-closed：干净流不能自证合格，陷阱是免疫系统的疫苗）。
- **重放序**：按 `ts` 稳定序重放（同 ts 保持输入序）。

## 落位与首版边界（诚实清单）

- 首版（2026-08）：CI-Workflows workflow 产 artifact（90 天保留）；artifact →
  本仓 JSONL 的周期汇入管道（owner 裁决导出 + reconcile + PR 落库）是后续运维
  步骤，本 README 先钉 schema 与口径（schema 先行，数据后至）。
- 域解锁状态真源 = CI-Workflows `pipeline/trust-gate/unlock-state.yaml`
  （三域初始全 locked；解锁/回锁=改该文件走 C1 PR——「一键回锁」即回锁条目）。
