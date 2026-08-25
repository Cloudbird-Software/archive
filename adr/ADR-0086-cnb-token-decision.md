# ADR-0086: CNB 高权限 token 保持——管理简单性优先与三层缓解

- status: accepted（2026-08-24）
- deciders: 人（owner randypanding，管理简单性优先裁决）+ AI（实现卡执行会话，GLM-5.3）
- 关联: IR-0004（Cloudbird-Software/.github#315，DECISION-01/AC-21，实现卡 #320）；
  ADR-0085（PM 优先范式——决策 6 CNB 底座与决策 7 凭据最小方案为本 ADR 的上游
  框架）；ADR-0082（红队守门收口——CNB 通道链与其"配置面恰为 1 org secret"
  口径）；ADR-0044（gh_app_token 硬化——组织凭据纪律谱系）；本仓 RUNBOOK.md
  （缓解条款③泄漏应急的逐步命令）、REMOVAL.md（退休时 secret 清理清单）

## 背景

cnb-bridge 以多账号池（accounts.yaml，CNB_TOKEN_<ALIAS> org secret 族）桥接
CNB 免费算力（ADR-0085 决策 6）。CNB 平台令牌不提供细粒度 scoped token：
现有令牌对账号内仓库与配额面均为高权限（读配额、talk 仓读写、开窗口）。
IR-0004 AC-21 要求 token 治理决策入册：高权限保持还是收敛。备选方案为
"每用途一令牌"（配额只读/派单读写分桶）——需要 owner 在 CNB 侧维护 2N 个
令牌的生命周期（创建/轮换/吊销/审计 × 账号数），且平台侧无法强制 scope
边界，分桶只是名义收敛。

owner 裁决（2026-08-24，IR-0004 DECISION-01）：**保持高权限 token 不变**，
管理简单性优先——凭据的真实暴露面不在令牌权限粒度，而在令牌的存放与
传播路径；把工程投入放在后者。

## 决策

1. **高权限 token 保持**：每账号恰 1 个 org secret（`CNB_TOKEN_<ALIAS>`，
   DECISION-06 同形口径），不做用途分桶；管理面=加账号即加一个 secret，
   零额外代码（ADR-0085 决策 6）。
2. **缓解①仅 org secret**：令牌唯一存放处是 GitHub org secret（可见性经
   `--repos` 收敛到 `.github` 与 `cnb-bridge` 两仓的接缝工作流）；仓内只存
   `secret_ref`；周审计对 org secret 清单对账，出现未登记 `CNB_TOKEN_*`
   形态 secret 即红（DECISION-06 检测载体）。
3. **缓解②永不进 agent 上下文与外部沙箱**：令牌只在接缝工作流的单步
   进程 env 内出现（不落 GITHUB_ENV/日志/摘要）；派单任务文本经凭据形状
   扫描预检（CNB_TOKEN/ghp_/github_pat_/PRIVATE KEY 命中即拒发）；PM/agent
   调用一律借道 dispatch 经纪人（ADR-0085 决策 7），任何 key 不进 PM 上下文
   与 CNB 沙箱。
4. **缓解③泄漏应急三步 runbook 化**：吊销 → 轮换 → 审计，逐步命令见本仓
   [RUNBOOK.md](RUNBOOK.md) 事故流程（§4）；三步完成前账号置 degraded 阻断
   调度。本 ADR 只裁决策，执行细则以 RUNBOOK 为准。
5. **回归防护**：派单任务文本凭据扫描为常驻预检（cnb-dispatch preflight
   步），扫描步骤缺失或未运行即红（AC-21 防回归）；本仓测试含源码零
   token 字面量断言（tests 延续 cnb_pool 先例）。

## 后果

- 正：owner 凭据运维成本恒定（N 账号 N secret）；轮换/吊销单点操作；
  DECISION-06 时序护栏与周审计对账口径不被分桶复杂化。
- 负：单令牌泄漏的爆炸半径=该账号全部能力（配额读取+talk 仓读写）。
  接受理由：爆炸半径被缓解②的传播路径收敛限制（令牌不出 secret/工作流
  进程面），且缓解③保证泄漏后可检测（审计对账）可恢复（三步应急）。
- 中性：若 CNB 未来提供细粒度 scoped token，重开 ADR 评估分桶；本 ADR
  不预支该假设。
- 证据面：ADR diff（本文件）、org secret 存在性查询记录（`gh secret list`
  只显名不显值）、凭据扫描测试运行记录（AC-21 运行时证据三件）随周审计
  与入职 runbook 落盘。
