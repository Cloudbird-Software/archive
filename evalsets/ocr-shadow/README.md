# evalsets/ocr-shadow —— OCR shadow 评估资产与口径

- 状态: active（W2-C4，Cloudbird-Software/.github#217 / ADR-0063）
- 数据生产者: CI-Workflows `.github/workflows/ocr-shadow`（纯 shadow，不阻断合并）
- 消费者: CI-Workflows `pipeline/ocr/precision.py`（post-fix precision 基准管线）

## 范式署名（宪法 §9 署名规则）

| 资产 | 源头 | 许可 | 用途 |
|---|---|---|---|
| 代码评审执行 | [alibaba/open-code-review](https://github.com/alibaba/open-code-review)（OCR）v1.9.9 | Apache-2.0 | shadow 评审器本体（vendored 钉版封装于 CI-Workflows `pipeline/ocr/action.yml`，alibaba/* 不在 actions_policy 白名单故不引用其 Action） |
| post-fix precision 方法学 | [withmartian/code-review-benchmark](https://github.com/withmartian/code-review-benchmark) | MIT | 方法学 fork 自建管线（bot 建议被事后人工修复命中的比例=precision） |
| 选型参考（不作晋升依据） | AACR-Bench | — | 厂商自评+AI 辅助标注+泄漏风险，宪法 §4C 明示仅作参考 |

供应链钉版（ADR-0063 决策 1）：版本+二进制 sha256 双锚定 + SBOM。SBOM 落案于
CI-Workflows `pipeline/ocr/sbom/ocr-v1.9.9.cdx.json`（CycloneDX 1.5 手写清单，
零工具依赖；`pipeline/ocr/tests/test_pins.py` 校验 SBOM↔封装钉锚一致防漂移）。
本仓留评估口径文档（本文件）；升级 OCR 版本 = 更新钉锚三处 + SBOM + 本文件版本注记。

## 数据格式（ocr-shadow/v1 JSONL）

shadow workflow 产出 artifact `ocr-shadow/<YYYY-MM-DD>.jsonl`（UTC 日切，逐 run 追加）。
每行一个 JSON 对象，`record` 字段区分两类：

```jsonc
// record=suggestion —— 后处理保留的一条建议（precision 分子/分母的原子）
{"schema":"ocr-shadow/v1","record":"suggestion","ts":"…","repo":"ORG/REPO","pr":123,
 "head_sha":"<40hex>","run_id":"…","event":"pull_request","model":"glm-4.5-air",
 "ocr":{"version":"1.9.9"},
 "suggestion":{"path":"src/x.py","start_line":11,"end_line":11,"content":"…",
               "rule_id":"injection","existing_code":"…","suggestion_code":"…"}}

// record=summary —— 本次 run 的过滤统计（过滤率指标本体，宪法 §4E）
{"schema":"ocr-shadow/v1","record":"summary","stats":{
 "ocr_status":"success|skipped|…","total":4,"kept":1,
 "dropped_by_reason":{"outside-diff":1,"no-rule-hit":1,"duplicate":1},
 "drop_rate":0.75,"ocr_exit_code":0}}
```

约定：

- `skipped`（如无 LLM 凭据的 N/A 诚实降级）只产 summary 行、零 suggestion 行——
  诚实降级不伪装运行过评审。
- `head_sha` 是行坐标基准：suggestion 的行号以该 PR head 为坐标系。
- 去重键 `(path, start_line, rule_id)`；规则表真源 = CI-Workflows `pipeline/ocr/rules.yaml`。

## precision 口径（post-fix 基准）

- **分母 evaluated**：观察窗内（merge 后 `--window-days`，缺省 14 天）存在后续
  commit 的建议；无后续 commit = `pending_observation`，不入分母。后续全为 bot
  commit 的建议保守计 miss（对晋升阈值取 fail-closed 方向）。
- **命中 hit**：某后续**非 bot** commit 的 diff 触及建议锚定文件，且变更行区间
  （'+' 取新侧、'-' 取旧侧行号——删除坏行也是修复）与建议 `[start_line, end_line]`
  相交（±`--line-tolerance`，缺省 3，吸收行漂移）。
- **污染防御**（ADR-0063 风险条款）：命中判定只认非 bot 修复 commit——人工照
  bot 建议抄修 = 假命中，不计。
- **后续 diff 基线约定**：follow-up diff 须以建议基线（PR head/merge）为参照
  生成（`--followups` fixture 模式即此约定；`--api-repo` 在线模式取默认分支
  commit diff，行漂移由 tolerance 吸收）。
- **时序**：按建议 ts 自然月聚合 + 累积曲线（`series[]`），即"precision 时序"。

## 晋升阈值（ADR-0063 决策 4）

`precision ≥ 0.8 且累积 ≥ 30 例` → `promotion_ready=true`。管线只产数与判定，
**不授权晋升**——shadow→veto 晋升另走 ADR + 信任门流程（宪法 §5）。
首版（2026-08）要求 = 管线可跑 + 自测绿（CI-Workflows `pipeline/ocr/tests/`，
零网络零真实推理），不要求已满 30 例。
