# ADR-0082: 红队守门 ADR 收口——默认 verifier 范式、红队守门制度与五轮 dogfood 经验

- status: accepted（2026-08-23）
- deciders: 人（owner randypanding）+ AI
- 关联: ADR-0067（恶意合规 adversary）、ADR-0072（verifier 入职考试校准）、
  ADR-0076（验证者身份独立）、ADR-0079（spec 阶段攻击面 S1'–S5'）、
  ADR-0061（g060 锁定）、ADR-0062（metering wrapper）、ADR-0068（holdout 揭封）、
  ISSUE-263 spec v5 AC-1..AC-20 / DECISION-01..05；Cloudbird-Software/.github#288（W5-C3）

## 背景

ISSUE-263 五轮 dogfood（R1–R5，CNB 轮）暴露了 IR 保真度丢失、blastRadius 结构
失真、S5 错误路径守卫缺失、正向上报回路缺失、fail-closed 总原则未固化等问题。
本 ADR 作为红队守门制度的收口，将五轮 dogfood 经验制度化：默认 verifier 范式、
红队守门范围、CNB 通道与 fallback 链、以及五轮后收敛的验收标准。

## 决策

### 1. 默认 verifier 范式（承接 ADR-0072 / AC-1 / INV-01）

任何 LLM 参与判定的环节必须采用开源 LLM-as-a-Verifier 实践（arXiv:2607.05391）：
- 绝对细粒度 reward：逐 criterion 连续分（0.0–1.0），不接受散文结论；
- criteria 分解：一卡一文件，机器可追溯到对应卡的 AC 列表；
- K 次重复评估：默认 K=3，降档须留痕且不得改动判定语义与阈值；
- 阈值 gate：综合分 < 阈值 → verdict insufficient（blocking）；
- endpoint 三探测：每次 run 前探测 logprobs 有无、top_logprobs 上限、
  prefill/structured_outputs 支持；不满足最低要求即 fail-closed；
- token 账与 metering 交叉核对：偏差超阈值（默认 10%）run 作废转人工。

### 2. 红队守门范围（承接 ADR-0067 / ADR-0079 / DECISION-02 / BEH-01）

红队审计覆盖意图→spec→测试设计路径，该路径每个 PR 都必须经红队审计并作为
合并阻断项：
- 语义审计 verdict=insufficient 时机器阻断（state → needs-human）；
- survived 才放行（state 可转 wave-planned）；
- 开发实现路径 PR 不走红队审计，只跑确定性测试与 holdout 测试；
- spec 路径 PR 缺失 adversary check（漏配/被摘除/被跳过）时 CI 必须红
  （负向断言）。

### 3. CNB 通道与 fallback 链（承接 W3-C4 / AC-6 / AC-15）

红队 AI 以 GitHub Actions job 形态在沙箱中执行：
- 配置面恰为 1 个 org secret（CNB_TOKEN）+ 1 个 org variable；
- 沙箱内对 env 全量做凭据形状扫描，出现第 2 个凭据即判红（负向断言）；
- canary 先行（30–60s echo 任务）验证通道可用性；
- fallback 链：CNB→自有 API→no-attempts（锁 needs-human + 自动开 issue）；
- 连续 3 次 fallback 或额度尽 → 自动开 type:infra issue。

### 4. 五轮 dogfood 经验制度化（承接 spec rev2–rev5）

五轮 dogfood 的核心教训已纳入 spec v5 各条款：
- rev2：blastRadius 结构失真 → 补 holdout 仓与 agent-registry 真源；
- rev3：S5 错误路径守卫缺失 → spec 路径缺 check 必须红、作废须转 insufficient、
  no-attempts 状态后果；反摆拍断言逐 run 常驻化；
- rev4：正向上报回路缺失 → T5/T6 入册、意图道闸无命中被误挂失败语义、
  holdout/AG-1 时序判红、锁卡语义收窄至白卷、道闸跳过留痕；
- rev5：fail-closed 总原则 → ADR-0072/0062/0068 承接引用、白卷不挂失败分支、
  criteria 溯源、golden 盲化、T6 三元组、五轮后收敛。

### 5. 收敛标准（AC-20 / DECISION-05）

五轮后收敛的判定：一张真实卡走完完整流程
ir-signed→spec→redteam→（Veto 一次→修复→survived）→wave-planned→认领→
PR 绑定卡测试→合并全程；Veto 理由与修复 diff 经机械核对证明修复确实回应了
该理由；"Veto 过一次"不构成可复用资历，每卡红队守门相互独立。

## 后果

- 正面：红队守门制度形成完整闭环（verifier 范式 + 守门范围 + CNB 通道 +
  五轮经验制度化）；spec v5 各条款均有执行层引用（死条款判失败）。
- 负面/代价：红队审计增加 spec/测试设计路径变更摩擦；CNB 通道需维护 canary
  + fallback 链；verifier 范式需 K 次重复调用，token 成本较高。
- 风险与缓解：
  - verifier 被冒用 → 身份判定依赖 GitHub App bot 签名 + 安装 ID 真源 +
    单仓作用域令牌；
  - CNB 通道凭据泄露 → 凭据纪律扫描（env 全量，第 2 个凭据即判红）；
  - 红队审计被绕过 → 负向断言（spec 路径缺 adversary check 必须红）。
- 回滚：T5/T6 可停用；意图道闸可整体关停；llm-verifier 实现可替换（替换物
  必须仍满足默认范式四件套）；CNB 通道可关闭。

## 验证

- AC-1：ADR-0082 合并后，agent-registry `decisions/` 新增 ADR-0082 墓碑，
  `INDEX.yaml` 登记 `content_sha256` 与 archive 正文一致；
  `python scripts/validate.py` 通过。
- AC-2：`.github/AGENTS.md` 入口协议引用红队守门 ADR 与 g060 制度。
- AC-3：spec v5 各条款（T-14/T-15/AR-10/AC-1..AC-20）均有至少一处执行逻辑
  引用（新条款被至少一处执行逻辑引用，死条款判失败）。
- AC-4：五轮 dogfood 经验制度化——spec rev2–rev5 的每条教训均有对应条款/
  执行逻辑承接。
