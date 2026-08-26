# evalsets/verifier-exam —— verifier 入职考试冻结集（口径与存档声明）

- 状态: active（W5-C3，Cloudbird-Software/.github#226 / ADR-0072）
- 数据消费者: CI-Workflows `pipeline/verifier-exam/`（钉版副本 + freeze_hash 漂移日检）
- 关联卡 AC: AC-1（考试全过才注册）/ AC-2（金丝雀 100% 判负）/ 双序一致率 ≥0.90

## 范式署名（宪法 §9 署名规则 #3）

| 资产 | 源头 | 用途 |
|---|---|---|
| 考试方法论 | LLM-as-a-Verifier（arXiv:2607.05391 + 同名开源实现） | 入职考试整体范式：判据分解、连续分、重复评估降方差 |
| 生成式子集形态 | RewardBench2（allenai，生成式赛道数据格式） | `v1/rewardbench2-generative.jsonl` 条目结构（prompt/responses[2]/label）对齐 |
| 对抗子集形态 | LLMBar（Prasad et al., Microsoft，对抗配对评测） | `v1/llmbar-adversarial.jsonl` obvious/subtle 干扰项形态对齐 |
| null-model 金丝雀 | null-model 攻击实证（arXiv:2410.07137） | 空响应/模板复读/无理由拒绝必须 100% 判负 |
| 双序（位置交换） | MT-Bench 位置交换协议（arXiv:2306.05685） | 同题两序呈现，一致率 ≥0.90 才过 |
| 校准 | 敏感度/特异度校准（arXiv:2511.21140，ICML'26） | CI-Workflows `pipeline/verifier-exam/calibrate.py` |

**数据来源声明**：全部条目为自构造（self-constructed），结构对齐上述来源的数据格式，
**未再分发任何上游数据**；署名=方法与形态来源，不是数据许可转移。

## 冻结协议（ADR-0072 决策 1）

- 版本目录 `v1/`，冻结锚 = `v1/manifest.json` 的逐文件 sha256 + 总 `freeze_hash`
  （= sha256(按文件名排序的 `<name> <sha256>\n` 行)，UTF-8）。
- **任何字节改动（含增删条目、改序、改空白）即破坏哈希。改集=开新版本目录
  `vN/` 并在本文件版本史登记**；禁止原地修改。
- 运行时校验：CI-Workflows 侧持有钉版副本 + `exam-pin.yaml`（记 freeze_hash），
  考试 runner 每次开考先复算哈希（不匹配=exit 2，fail-closed）；每日 drift 检查
  比对本仓 main 的 manifest 与钉版 pin——本仓被改动而版本号未升 → main 上红。
- 金丝雀轮换：owner 月度补给新版本（新版本目录），旧版本成绩档案保持可追溯。

## 组成（v1.0.0，冻结于 2026-08-22）

| 文件 | 条目 | 判定形态 | 门阈值（真源=CI-Workflows `pipeline/verifier-exam/exam-policy.yaml`） |
|---|---|---|---|
| `rewardbench2-generative.jsonl` | 20 | 成对偏好 | accuracy ≥ 0.70 |
| `llmbar-adversarial.jsonl` | 20 | 成对偏好（obvious 10 + subtle 10） | accuracy ≥ 0.60 |
| `null-canaries.jsonl` | 24 | 单响应判负（empty 8 / parrot 8 / refusal 8） | negative_rate = 1.00（100% 判负） |
| 双序一致率 | 复用上述 40 条成对条目 | 两序呈现 | agreement ≥ 0.90 |

条目黄金标签（`label`/`expected`）与 `gold_rationale` 字段仅供维护者复核，
**禁止进入判官输入通道**（对抗防御：输入隔离，宪法 §4C/ADR-0072 决策 7）。

## 成绩存档声明（ADR-0072 决策 2）

- 存档键 = `judge_id@exam_version@prompt_hash12`（模型换代或 prompt 改动即重考，
  档案可追溯）。
- 存档载体 = CI-Workflows `verifier-exam` workflow 的 JSONL artifact
  （`verifier-exam-results`，retention 90 天）；每行一条考试记录，含全部分项
  得分/阈值/整体判定/锁定配置（模型别名+prompt 版本+采样参数）/考试集 freeze_hash。
- 执照挂接：随 ADR-0085 退役（agent-registry 归档，verifier-license.py 停维）——
  历史机制快照见 `retired/agent-registry/`；当前考试成绩仅作 shadow 观察与
  校准数据源，不构成持证判定。

## 版本史

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-08-22 | 首版冻结（freeze_hash 见 v1/manifest.json） |
