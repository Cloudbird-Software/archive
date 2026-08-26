# ADR-0095: AGENTS.md 按角色路由重构 + IR 挂靠产品仓

- status: accepted
- date: 2026-08-26
- deciders: owner（randypanding，2026-08-26 会话内明示授权）/ 治理 agent 会话（起草与执行）
- resolves: 各仓 AGENTS.md 未能把组织级意图（按意图/角色进入对应流程）传达给落地 agent；「IR 一律在 .github 仓开」的规定与 PM 优先范式下产品仓自治的现实错位
- 关联: ADR-0085（PM 优先范式，本 ADR 在其四道门禁框架内细化入口路由）；ADR-0055（统一入口协议块，本 ADR 将其升级 v2 并全仓下发）；ADR-0082（红队守门——spec PR 测试设计攻击面）；ADR-0083（suite 门）；ADR-0061/0081（g060 测试锁定）；ADR-0064（bug 流）；ADR-0056/0080（holdout 试卷层与隔离）

## 背景

PM 优先范式运行以来暴露两个入口面断裂（用户 2026-08-26 会话明示）：

1. **各仓 AGENTS.md 只覆盖「找卡干活」单一意图**。陌生 agent 从任意仓落地后，
   不知道组织期望它按意图选路（开 IR / 开 spec / 实现 / 验收与修 bug），
   治理文件（testing.yaml 测试种类、holdout 机制、CNB 弱模型池、fan-out 态度、
   bug 流）没有被路由到应该读它的角色手里。
2. **「IR 一律在 .github 仓开」（PLAYBOOK §2 / NAVIGATION §2 / profile README）
   把意图账本与实现仓割裂**：IR 本质只是一个 issue（意图记录），挂在对应产品仓
   才与「spec 与 suite 随实现仓走」一致；跨仓 IR 引用（如 Viral_Radar#1 先例）
   早已存在。规定与现实脱节。

## 决策

1. **IR 挂靠产品仓**：feature/产品意图的 IR 一律开在对应产品仓（issue 即 IR，
   无需任何 PR）；治理意图的 IR 仍开在 .github 仓。废止「IR 一律在 .github 仓开」
   的全部文档规定。issue 模板经 org 级 `.github/ISSUE_TEMPLATE` 继承自动可用
   （intent.yml）；`type:intent` 等治理标签由 apply.sh §7 同步到受管仓。
   IR 编号 `IR-NNNN` 全局唯一，由开立者分配（开立前用 `bash ghcb board` 各仓
   核对已用编号）；机器侧编号仍从 issue 标题提取（conductor / ghcb 现状不变）。
2. **AGENTS.md 按意图路由四角色**，每仓 AGENTS.md 携带「角色路由」节，指引
   文件统一落在 .github 仓 `docs/agent/`：
   - `ROLE-IR.md`——开 IR（意图受理：开在本仓、字段全必填、不代签）
   - `ROLE-SPEC.md`——IR→spec（spec PR 流程：测试设计逐类讨论、红队、holdout
     注册；**spec agent 不得直接实现**）
   - `ROLE-IMPLEMENT.md`——实现（PM 职责：优先弱模型、fan-out 态度、边做边推
     PR、全 CI/review 清零才合并、弱模型 3 次不过 PM 接手、holdout 失败处置）
   - `ROLE-ACCEPT.md`——验收与 bug 修复（检查卡/IR 完成度；bug 复现三值判定）
3. **入口协议块升级 v2**（ADR-0055 机制内升版）：新增第 0 步「按意图定角色」，
   指向 .github 仓 docs/agent/ 四文件；v2 块经 template-service（canon 真源）
   下发到全部活跃受管仓——REPOS.yaml 的 `entry_protocol: true` 标注扩展到
   全部活跃仓（drift-check §17 逐字节对账随之全仓生效）。
4. **spec PR 的测试设计硬性要求**（对 PLAYBOOK §2 的补充，执法面不变）：
   spec 的测试设计节必须逐类过 `governance/policy/testing.yaml` 清单
   （差分 T-09 / 属性 T-01 / 模糊 T-04 / 变异 T-10 / 蜕变 L-03 / LLM 产品族 /
   重写项目族 / 触发式族……），每类明确 adopt 或 reject 并给理由（讨论留痕）；
   必须包含 holdout 测试设计（条目经验证者 APP 注册到 holdout 仓，引用仅
   `id@sha8`）。红队（ADR-0082）对 spec PR 的测试设置是否合理进行攻击与讨论
   ——测试设计不充分即 insufficient（adversary-gate required check 红）。
5. **实现角色的弱模型优先纪律**（对 PLAYBOOK §4 的补充）：卡面 AC 已足够清晰
   且有测试控制质量，故优先用弱模型完成——自带子 agent，或 CNB 免费算力池
   （`bash ghcb dispatch`，见 providers.yaml / cnb-bridge 仓）。fan-out 是工具
   不是流程（IR-0004 AC-9/AC-10 原口径）：用不用、并行度多少由 PM 裁量，
   不用完全合法；产物 append-only（ADR-0062）。一边做一边推 PR；PR 必须解决
   完全部 CI 与 review 问题方可合并；弱模型同一 PR 修红重试达上限
   （auto_fix.max_attempts，默认 3）仍未过 → PM 自己完成。holdout 测试失败：
   修实现、永不改试卷（g060 锁 + DECISION-02 隔离），走 quarantine /
   needs-human 路径等 owner 裁决。
6. **验收与 bug 修复角色流程**（对 PLAYBOOK §5 + ADR-0064 的入口收口）：
   人类让 agent 处理 issues 时走 ROLE-ACCEPT.md——对全部工作卡与 IR 检查完成
   度，未完成的开 bug issue 后修复、修复后关闭；bug/incident 先复现（B1–B5
   机器复现），无法复现的关闭（留复现尝试记录），能复现的修复→推 PR→处理完
   全部 CI/review→合并→关闭 issue。
7. **宪法 §4D / CG-1 行数指引修订**：AGENTS.md 允许在「命令+硬规则+索引」
   索引型正文之外携带入口协议块与角色路由节（二者是组织意图的下发面，不计入
   ≤30 行的正文预算）；.github 仓豁免上限维持 60 行（test-navigation.sh §B）。

## 机器面边界（诚实申报）

本 ADR 只改「规定与指引面」。以下机器面保持现状、登记为后续跟进（不阻塞本
决策生效——文档规定先行的先例见 #363 落点）：

- conductor 状态机事件面仍限 .github 仓（conductor.yml route job 的 repository
  guard）：产品仓 IR/卡的 `state:*` 转移暂由 owner 手动打标签或 /start 评论，
  跨仓事件面扩展另立卡。
- dashboard-update.py 的 IR 统计仍以 .github 仓 type:intent 为口径。
- `ghcb accept` 已随本批次支持 `[repo]` 参数（scripts/ghcb）；board/next 等
  子命令本就按仓参数化。

## 后果

- 正面：任意仓落地的 agent 在 30 秒内按意图选对流程；意图账本与实现仓统一；
  spec 测试设计与 holdout 有了不可绕过的入口指引；弱模型优先与 3 次熔断的
  上升策略从 PLAYBOOK 深文提升到每仓 AGENTS.md 面。
- 负面/成本：14 个仓各一笔 AGENTS.md PR（协议块 v2 + 角色路由节）；
  drift §17 对账范围扩大——任何协议块变更须全仓同步（模板机制不变）。
- 合并顺序（顺序错了窗口期 drift 红）：本 ADR（archive）→ template-service
  （canon v2）→ 其余各仓 → .github（自身 AGENTS.md v2 + REPOS.yaml 标注）。
