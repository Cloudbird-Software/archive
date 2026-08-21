# ADR-0068: holdout 揭封 gate——hash 校验 + 计数化展示 + 详情回写 + 日志审计

- status: accepted（2026-08-22）
- deciders: 人（owner randypanding）+ AI
- 关联: 宪法 §4B（holdout 揭封）/§1（试卷层）、§14 阈值；.github#222（W4-C3）；
  holdout 仓与条目 schema、泄漏诱饵由 W1-C4（.github#167，ADR-0056）建立

## 背景

holdout（宪法 §1 试卷层）在 W1-C4 已实体化为独立仓：封存验收场景+golden
集+泄漏诱饵，owner 直管。缺的是揭封的机器形态：揭封凭据若实现阶段可得，
试卷即泄漏；揭封结果若以明细形式出现在 PR 界面，agent 可从 check 输出
"读题"；揭封记录若可改写，试卷消耗不可审计。卡 #222 触发：落揭封 gate。

## 决策

1. **凭据隔离**：揭封凭据（unseal token）仅 verdict workflow 的环境可用
   （环境级绑定）；实现阶段全部 workflow 无此凭据——结构上接触不到
   holdout 内容（W1-C4 的 drift 断言持续保证 agent 未挂载 holdout 仓）。
2. **揭封流程（AC-1）**：校验条目 `sealed_sha256`（不匹配=fail-closed 拒揭，
   防试卷被篡改后静默重跑）→ 执行场景 → 计数。
3. **计数化展示（AC-1）**：PR check 只显示通过计数（如 `holdout 47/50`），
   无任何明细、无失败条目名——防从 PR 界面读题；详情（逐条结果）写
   holdout 仓 issue，过 W1-C4 条目 schema 校验，仅 owner 与 verdict 上下文
   可达。
4. **揭封记录 append-only（AC-3）**：每条含 sealed_sha256 校验结果、run_id、
   计数、时间戳；永不改写（append-only 台账，与 archive 仓同纪律）。
5. **泄漏审计（AC-2）**：实现阶段全部 workflow 日志扫描——无 holdout 内容
   出现；泄漏诱饵（W1-C4 部署的独特标记样本）出现于任何日志/agent 上下文
   即报警（宪法 §6）。
6. **通过率差升级（AC-4）**：holdout 与主套件通过率差超 5%（§14 阈值）→
   该 PR verdict 不过 + needs-human——主套件绿而 holdout 显著差=实现
   "对着主套件调参"的信号，fail-closed 不放过。

## 后果

- 正面：试卷保密性由凭据隔离+计数化+日志审计三面机器背书；通过率差
  成为逃逸前哨指标（§4E 系统级回归）。
- 负面/代价：计数化让失败调试困难（设计使然——正是不给"对着考试调"
  的通道，owner 经 holdout 仓 issue 看详情）；每次揭封消耗 Actions 与
  LLM 预算。
- 风险与缓解：凭据泄漏 → 诱饵联动报警（ADR-0069 周演习联动检查）；
  通过率差误报（holdout 样本本身 flaky）→ holdout 样本准入带稳定性
  验证（owner 月度补给职责，§2）。
- 回滚：gate 摘除后 holdout 仍封存无损（试卷未动）；揭封台账 append-only
  不需回滚。
