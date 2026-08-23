# ADR-0082: 红队守门制度收口——默认 verifier 范式、CNB 通道与 fallback、五轮 dogfood

- status: accepted（2026-08-23）
- deciders: 人（owner randypanding）+ AI
- 关联: ISSUE-263 spec v5（卡绑定测试与红队守门制度）；ADR-0072（LLM-as-a-Verifier
  范式，arXiv:2607.05391）；ADR-0067（恶意合规 adversary / 攻击面 S1–S5 / S1'–S5'）；
  ADR-0062（metering wrapper + hash 链）；ADR-0061（g060 测试分片锁定）；
  ADR-0079（ADR-0067 修订——spec 阶段攻击面）；ADR-0068（holdout 揭封）；
  ADR-0048（LLM endpoint 直连 provider）；ADR-0040（automation-limits 护栏）；
  Cloudbird-Software/.github#288（W5-C3）

## 背景

ISSUE-263 五轮红队审计（R1–R5，CNB 轮）后，卡绑定测试与红队守门制度已从
零散 ADR/条款收口为一套可执行、可审计、可逆的闭环。本 ADR 是"收口 ADR"：
把分散在 spec AC、ADR-0067/0072/0061/0062/0068、五轮 dogfood 中的关键决策
凝成一份真源（正本存 archive，墓碑存 agent-registry/decisions/），供
AGENTS.md 入口协议与下游状态机引用。

本轮核心经验（R1–R5 dogfood 教训）：
- R1：IR 保真度丢失、blastRadius 结构失真——攻击面须向 spec 阶段重定义（→ ADR-0079 S1'–S5'）。
- R2：S5 错误路径守卫缺失（spec 路径缺 check 必须红、作废须转 insufficient、
  no-attempts 状态后果）；反摆拍断言须逐 run 常驻化。
- R3：正向上报回路缺失、T5/T6 未列入册、意图道闸无命中被误挂失败语义、
  holdout/AG-1 时序判红、锁卡语义收窄至白卷、道闸跳过留痕。
- R4：fail-closed 总原则（判定工具链任何环节异常一律判红或转 needs-human，
  不存在"未定义默认绿"分支）；ADR-0072/0062/0068 承接引用；blastRadius 补
  holdout 仓与 agent-registry 真源；白卷不挂失败分支；criteria 溯源；golden 盲化；
  T6 三元组（卡 ID+specVersion+审计 run ID）；五轮后收敛。

## 决策

### 1. 默认 verifier 范式（AC-1 / AC-7 / INV-01）

任何 LLM 参与判定的环节**必须**采用开源 LLM-as-a-Verifier 实践（引用
arXiv:2607.05391，与 ADR-0072 同一外部范式），包含四件套：
- 绝对细粒度 reward（逐 criterion 连续分 0.0–1.0，不接受散文结论）；
- criteria 分解（一卡一文件，机器可追溯到对应卡的 AC 列表）；
- K 次重复评估（默认 K=3，为暴露成本旋钮，降档须留痕）；
- 阈值 gate（单 criterion 阈值 + 全局阈值，全过=survived，任一不达=insufficient）。

约束：
- PPT 锦标赛仅作 best-of-N 选择层，胜率**不得**作为 gate 输入（负向断言）；
- 运行时证据（CI 日志含 llm-verifier 实际调用记录、逐 criterion 连续分 JSON
  与 token 消耗）由独立于 verifier 的采集组件写入，不接受"声明已写入"。

### 2. endpoint 三探测（AC-10 / IFACE-02）

每次 verifier run 前**必须**探测 endpoint，防探测后动态降级：
- 检测 logprobs 有无、top_logprobs 上限、prefill/structured_outputs 支持；
- 结果决定打分抽取路径与精度预期并写入报告；
- 不满足最低要求的 endpoint 配置即 fail-closed（探测本身失败/超时不得误判为通过）；
- 探测结果与 LLM 响应 usage 中的 model/endpoint 指纹交叉一致，不一致即判红；
- top_logprobs 截断造成的精度折损必须在 run 报告中声明。

### 3. token 账与 metering 交叉核对（AC-11 / BUDGET-01 / INV-04）

- verifier token 成本随 run 持久化挂接 ADR-0062 metering wrapper；
- 与 LLM 响应 usage 字段交叉核对，偏差超阈值（相对>5% 或绝对>50 tokens）时
  该 run 判定作废并转人工（非仅告警，`fail_closed_action: void_and_escalate`）；
- 预算口径纳入 `automation-limits.yaml` `llm_tokens.verifier` 档（数据源复用
  ciw-metering `records-*.jsonl` `role=verifier` 切片，不新建计量通道）；
- K 与 pivots 为暴露成本旋钮，降档须留痕且不得改动判定语义与阈值。

### 4. 红队守门范围与 veto 语义（BEH-01 / AC-14 / DECISION-02）

红队审计覆盖意图→spec→测试设计路径，该路径每个 PR 都必须经红队审计并作为
合并阻断项：
- 语义审计 `verdict=insufficient` 时机器阻断（state 转 needs-human，无法进入
  wave-planned）；`survived` 才放行；
- 意图探索（S6–S8）不产生阻断性判定，命中带证据报人裁决；无命中须落盘留痕
  （正常结果，区别于未运行）；
- **白卷**（无任何产出）仅留痕+报人，不进入失败/锁卡分支——意图道闸的任何形态
  输出永不构成机器阻断；跳过与无命中为 schema 互异的两类工件；
- 开发实现路径 PR 不走红队审计，只跑确定性测试与 holdout 测试。

### 5. g060 测试分片锁定（AC-18 / ADR-0061 语义扩展）

`specs/*/suite/**` 按 IR 分片锁定，CODEOWNER = 验证者 APP + 人类 owner：
- 非 verifier-app/owner 改测试 exit 2 + 自动开 issue 路由 owner 裁决；
- 裁决闭环：终态机器可核（accepted/rejected）+ TTL（48h）+ dead-man 提醒；
- ADR-0061 已修订为验证者 APP 定义合法写豁免通道（ADR-0081）。

### 6. CNB dispatch 通道与 fallback 链（W3-C4 .github#280）

经 CNB（api.cnb.cool）分发红队/verifier 任务到云端沙箱，与自有 API 构成 fallback：
- **CNB**（主通道）：`CNB_TOKEN` org secret 注入，canary 先行（30–60s echo 任务）
  验证云端存活后再派真实任务；凭据纪律——CNB 沙箱只接触公开内容，零 GitHub 凭据
  （派发前凭据形状扫描，发现即拒绝 fail-closed）；
- **自有 API**（回退）：CNB 失败时回退到 `vars.LLM_ENDPOINT` 直连（ADR-0048）；
- **no-attempts**（兜底）：自有 API 也失败→锁 needs-human + 自动开 issue；
- **熔断**：连续 3 次 fallback 或 CNB 额度尽→自动开 `type:infra` issue 报人。

### 7. 可逆性设计（DECISION-03）

- 红队 check 可从 required checks 摘除；
- T5/T6 可停用；
- 意图道闸可整体关停；
- llm-verifier 实现可替换，但替换物必须仍满足默认范式四件套（§1）。

## 后果

- **真源分工**：agent-registry/decisions/ 存墓碑（指向 archive 正本），archive/adr/
  存正本（append-only，字节保真）。drift-check §10 经 INDEX.yaml 解析 archive 正本。
- **入口协议引用**：.github/AGENTS.md 入口协议块引用本 ADR 与 g060 制度，作为
  agent 进入治理仓的必读契约。
- **执行层引用**：CI-Workflows `pipeline/adversary/llm_verifier.py`、
  `cnb_bridge.py`、.github `scripts/g060-lock.sh` / `g060-escalation.py`
  为本 ADR 的机内实现；判定语义变更须同步修订本 ADR（C1 路径）。
- **收敛**：五轮 dogfood 后本 IR 红队守门制度收口；后续条款增量走 spec v5 C1
  调整路径（PR + ADR + owner-merge），不再新增独立制度。
