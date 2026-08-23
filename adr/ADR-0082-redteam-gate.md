# ADR-0082: 红队守门制度收口——默认 verifier 范式、CNB 通道与 fallback、五轮 dogfood 经验

- status: accepted（2026-08-24）
- deciders: 人（owner randypanding）+ AI
- 关联: ADR-0067（恶意合规 adversary）、ADR-0079（spec 阶段攻击面 S1'–S5'）、
  ADR-0072（LLM-as-a-Verifier 范式）、ADR-0062（metering wrapper）、
  ADR-0076（验证者身份独立）、ADR-0081（验证者写豁免）、ADR-0055（入口协议）、
  ISSUE-263 spec v5（AC-1…AC-20 / INV / BEH / IFACE / BUDGET / DECISION / ASSUMPTION）；
  Cloudbird-Software/.github#288（W5-C3）

## 背景

ISSUE-263 经历五轮红队审计（R1–R5，CNB 轮），每轮均 verdict=insufficient，
暴露出 IR 保真度丢失、blastRadius 结构失真、攻击面需向 spec 阶段重定义、
S5 错误路径守卫缺失、正向上报回路缺失、T5/T6 未入册、意图道闸无命中被误挂失败语义、
holdout/AG-1 时序判红、锁卡语义收窄至白卷、道闸跳过留痕、fail-closed 总原则等
系统性缺陷（spec.md amendments rev2–rev5）。

前五轮在"实现路径红队守门"层面已收敛；本 ADR 将收敛点扩展到判定范式、
执行通道与经验制度化三层，作为 ISSUE-263 红队守门制度的收口决策。

## 决策

### 1. 默认 verifier 范式（承接 ADR-0072）

任何 LLM 参与判定的环节必须采用开源 LLM-as-a-Verifier 实践四件套（INV-01）：
绝对细粒度 reward、criteria 分解、K 次重复评估、阈值 gate，输出结构化连续分
（0.0–1.0 连续量），不接受散文结论。具体约束：

- **criteria 溯源**：一卡一 criteria 文件，机器可追溯到对应卡的 AC 列表
  （criteria id = AC-NN）；criteria 文件每次变更必须重新标定，标定记录与
  criteria SHA 强一致（AC-1 / AC-8）。
- **endpoint 三探测**：每次 verifier run 前探测 logprobs 有无、top_logprobs 上限、
  prefill/structured_outputs 支持；探测结果决定打分抽取路径与精度预期并写入报告；
  不满足最低要求即 fail-closed；探测失败/超时不得误判为通过；top_logprobs 截断
  造成的精度折损必须在 run 报告中声明（AC-10 / IFACE-02）。
- **token 账与 metering 交叉核对**：token 成本持久化挂接 ADR-0062 metering wrapper，
  与 LLM 响应 usage 字段交叉核对；偏差超阈值（相对 5% 或绝对 50 tokens）时该 run
  判定作废（verdict=void）并转人工，非仅告警（AC-11 / BUDGET-01）。
- **成本旋钮**：K 与 pivots 为暴露的成本旋钮；降档须留痕且不得改动判定语义与阈值
  （BUDGET-01）；默认取保守高值（K=3, pivots=1，ASSUMPTION-03）。
- **PPT 锦标赛定位**：仅作 best-of-N 选择层，胜率不得作为 gate 输入（负向断言，
  AC-1 / INV-01）。

### 2. 红队守门制度（ADR-0067/0079 收口）

红队审计覆盖意图→spec→测试设计路径（BEH-01/DECISION-02），该路径每个 PR 必须
经红队审计并作为合并阻断项。语义审计 verdict=insufficient 时机器阻断，survived
才放行。制度要点：

- **攻击面**：S1'–S5'（spec/测试设计文本攻击面，ADR-0079）用于 spec/测试路径；
  S1–S5（代码实现攻击面，ADR-0067）用于实现路径。
- **意图道闸 S6–S8**：只报人不阻断（AC-5/AC-16）；每卡实跑并留痕（无命中也产出
  "无命中"落盘记录，区别于未运行；跳过须显式留痕原因）；S8 为确定性脚本，可脱离
  LLM 独立运行且结果可复现；道闸的任何形态输出永不构成机器阻断（AC-5）。
- **卡绑定测试**：实现 PR 绑定卡后自动走卡对应测试集与已注册 holdout 测试（合并阻断，
  AC-3/AC-17）；spec PR 须含 suite/（至少一个非空测试文件且含有效断言，缺失即阻断）。
- **有界重试**：红队 run 失败/无产出/白卷 → 有界重试 ≤2 次（重试计数以不可篡改的
  run ID 序列工件为准）后自动开特定标签 issue、停止规划 agent 相关产出并提醒人类
  （AC-15）。
- **白卷语义**：no-attempts/空报告 run 之后该卡锁定 needs-human、不得进入 wave-planned
  并 dead-man 提醒；白卷不得视为红队已通过；普通 run 失败只重试+开 issue，不锁卡
  （AC-15）。
- **证据核对铁律**：每条引用由代码对运行时刻真实工件做字符串级机械匹配
  （AC-9/INV-03）；核对不通过的命中作废并记录；作废是判定不是记录——任一引用被
  核对作废时该报告 verdict 强制转 insufficient。

### 3. CNB 执行通道与 fallback 链（W3-C4）

红队/verifier AI 以 GitHub Actions job 形态在沙箱中执行（BEH-02/AC-6）。
为防 provider 单点故障与额度耗尽，设立三级 fallback 链：

- **CNB 主通道**（api.cnb.cool）：CNB_TOKEN org secret 注入；canary 先行
  （30–60s echo 任务验证云端存活）→ 窗口抢占/投递/轮询/收集。
- **自有 API 回退**：CNB 失败时回退到 LLM_ENDPOINT 直连（ADR-0048）。
- **no-attempts**：自有 API 也失败 → 锁 needs-human + 自动开 issue，不产出判定。
- **熔断**：连续 3 次 fallback 或 CNB 额度尽（429/402）→ 自动开 type:infra issue 报人。

凭据纪律（INV-02 / AC-6）：CNB 沙箱只接触公开内容，零 GitHub 凭据注入。派发前
经 credential_audit() 扫描 payload，命中 GitHub 凭据形状即拒绝派发（fail-closed）。

### 4. fail-closed 总原则（INV-04）

判定工具链任何环节异常（LLM 不可用、核对脚本崩溃、golden 加载失败、配置面枚举
失败、无 verdict、探测失败）一律判红或转 needs-human——不存在"未定义默认绿"分支。
一次性演示不构成合规证据。

### 5. 五轮 dogfood 经验制度化（R1–R5）

五轮红队审计的核心教训已写入 spec.md（amendments rev2–rev5）与各 ADR 修订。
本 ADR 将其中的可复用模式固化为制度：

- **IR 保真度**：spec 实施必须被至少一处执行逻辑引用（死条款判失败）；新条款
  必须被 drift-check 或 CI 读取（AC-19）。
- **blastRadius 完整性**：spec IR 须列出所有受影响的仓库/路径；drift-check 断言
  随 ADR 修订同步更新（AC-19）；holdout 仓与 agent-registry 真源必须列入 blastRadius。
- **时序断言**：验证者 APP 实施不得早于 ADR-0076 合并；AG-1 修订 ADR 合并前出现
  验证者 APP 实施证据即判红（IFACE-01 / AC-18）。
- **负向断言常驻**：关键反摆拍断言（golden 回归、无绕过转移断言、机械核对、配置面
  校验）逐 run 常驻 CI，非一次性验收动作。
- **收敛判定**：五轮后红队守门制度从"发现缺陷"转入"维护模式"——新增条款须至少被
  一处执行逻辑引用，审计频率维持 ADR-0079 的每 PR 要求。

## 后果

- 正面：ISSUE-263 红队守门制度在判定范式、执行通道、经验三层同步收敛；
  默认 verifier 范式与 fail-closed 总原则消除了多轮审计暴露的"未定义默认绿"；
  CNB fallback 链提升了执行通道的韧性。
- 负面/代价：每卡 verifier run 成本上升（K=3 重复 + 三探测 + metering 核对）；
  criteria 变更触发重标定增加治理摩擦；fallback 链与熔断逻辑增加运维面。
- 风险与缓解：
  - CNB 凭据泄露 → 凭据审计 fail-closed + public_only 标记 + 单仓作用域 CNB_TOKEN；
  - verifier 库不可用 → 回退到自研解析（文本 JSON 抽取），仍满足四件套；
  - golden 集过时 → golden 回归纳入 CI 常驻 required check，每次 run 全量重放。
- 回滚：关闭 CNB 通道（设 CNB_ENABLED=false）、恢复 verifier K=1、移除 fallback 链
  即可回退到直连 provider 单通道形态。

## 验证

- AC-1：`pipeline/adversary/llm_verifier.py` 实现 endpoint 三探测 + metering 交叉核对，
  报告 schema `llm-verifier-report/v1` 与 W3-C1/W3-C5 一致；criteria 文件一卡一份且
  id 对应 AC 编号。
- AC-2：`pipeline/adversary/cnb_bridge.py` 实现 CNB→own-api→no-attempts fallback 链，
  凭据审计 fail-closed；连续 3 次 fallback 触发 type:infra issue。
- AC-3：`governance/policy/automation-limits.yaml` 新增 verifier 专属口径
  （cross_check.deviation_pct=5 / deviation_abs=50 / cost_knobs.k_default=3）。
- AC-4：`agent-registry/decisions/ADR-0082-redteam-gate.md` 墓碑 + INDEX.yaml 登记
  content_sha256 与本文件一致；`python scripts/validate.py` 通过。
- AC-5：`.github/AGENTS.md` 入口协议引用本 ADR 与 g060 制度（W5-C3）。
