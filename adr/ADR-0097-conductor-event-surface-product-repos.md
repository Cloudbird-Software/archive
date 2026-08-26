# ADR-0097: conductor 事件面扩展至产品仓——IR 挂靠自动化收口

- status: accepted
- date: 2026-08-26
- deciders: owner（randypanding）/ PM 会话（方案与实施）
- resolves: ADR-0095 登记的机器面边界——"conductor 状态机事件面当前仅覆盖 .github 仓，产品仓 IR 签署由 owner 手动换签"
- 关联: ADR-0095（IR 挂靠产品仓——本 ADR 为其机器面收口）；ADR-0049/0050（conductor 状态机与找活协议）；ADR-0054/0055（arbiter CAS 租约与转介——租约面已按仓命名空间化，本 ADR 无改动）；ADR-0085（PM 优先四道门禁——T5/T6/T8/T9 谓词随事件面生效于产品仓）

## 背景

ADR-0095 确立"feature IR 开在对应产品仓"，但 conductor 工作流只部署在 .github 仓
（`if: github.repository == '...github'` 守卫 + 工作流文件物理只存在于该仓）。
GitHub 的 issues/issue_comment 事件**只在文件所在仓触发**，org required workflows
又不支持 issue 事件——于是产品仓 IR 的签署（T1/T2）、红队标签（T5/T6）、开卡
（T7）、认领（T3）、收卡（T8）、验收（T9）、bug 流（B1-B5）全部退化人工换签。

周边机制经核查**已是仓位无关**，事件路由是唯一缺口：

| 机制 | 现状 |
|---|---|
| intent.yml 模板 | org 级 .github/ISSUE_TEMPLATE 继承，产品仓无自有模板即生效 ✅ |
| 治理标签 | apply.sh §7 全仓同步（8 产品仓 + 模板仓 12 标签齐全）✅ |
| adversary-gate | org required workflow，目标仓上下文运行 ✅ |
| adversary 审计/回写 | CI-Workflows adversary 按 pr_repo 参数回写任意仓 check ✅ |
| spec-author 管线 | target_repo 输入参数化（IR 所在仓=PR 目标仓）✅ |
| arbiter 租约 | refs/leases/<org>__<repo>__<n> 按仓命名空间 ✅ |
| board 观测面 | board-sync.py 扫 REPOS.yaml 全部 active 仓 ✅ |
| org secrets | CB_APP_ID/AGENT_APP_SECRET/GOVERNANCE_TOKEN vis=all ✅ |
| cloudbrid-agent 挂载 | installation 实含全部 9 目标仓（expected-state 清单陈旧，本 ADR 对齐）✅ |
| **conductor 事件路由** | **仅 .github——本 ADR 补齐** |

## 决策

1. **conductor.yml 改造为仓位无关（同一文件字节部署全仓）**：
   - `route` 守卫 `repository == .github` → `repository_owner == Cloudbird-Software`；
   - 状态机真源不复制：`governance/transitions.yaml` 与 `scripts/gh-app-token.sh`
     经 .github 仓 **sparse-checkout（gov/ 路径）** 就地取用——.github 自身部署
     同文件亦走此路径（单一真源原则不变，transitions.yaml 仍是 .github 仓 C1 资产）；
   - App 令牌按事件仓铸造（`REPO=${{ github.repository }}`，INV-02 语义不变）；
   - spec job `target_repo` 参数化为事件仓；on-failure 评论回事件仓 issue。
   T5（suite 谓词读事件仓 specs/）、T8（跨仓 PR 检索）、T9（验收报告在 IR 仓）
   语义随仓位自然正确。
2. **部署面 = 8 产品仓 + template-service**：Shorts_Director、Script_Writer、
   Use-up-Plan、AI_Web_School、mutual、QW_Arena1、Viral_Radar、Media-Monitor
   （feature IR 挂靠位）+ template-service（新仓由模板继承）。
   **不部署**：.github（治理 IR 位，已有）、arbiter/cnb-bridge/archive/holdout/
   CI-Workflows（基础设施仓——其意图属治理意图，IR 仍开 .github；agent-registry
   已退役归档）。
3. **expected-state.json `github_app.repositories` 对齐现实**：实际挂载面（API
   实查 16 仓）替换陈旧清单——补 QW_Arena1/Viral_Radar/Media-Monitor，去 holdout
   （ADR-0080 起由 verifier-app 挂载）。
4. **卡随 IR 挂靠**（重申 ADR-0095 fan-out 语义）：产品仓 IR 的子卡开在产品仓
   本仓，`Card: <org>/<repo>#<n>` 绑定行与 T8 跨仓 PR 检索已支持；治理 IR 的卡
   仍开 .github。

## 后果

- 产品仓 IR 全生命周期机器化：/start 签署 → spec → redteam → 开卡 /claim →
  PR 合并 T8 收卡 → T9 验收；bug 流 B1-B5 同步生效。owner 从"手动换签每个状态
  标签"中解放，四道门禁谓词在产品仓由同一状态机执法。
- conductor.yml 十仓同字节（.github + 9 仓）——后续演进 = 同一 PR 波次全仓同步
  下发，禁止单仓漂移副本；transitions.yaml 改动无需下发（sparse-checkout 每次运行
  时取 .github main 最新）。
- ROLE-IR/PLAYBOOK/NAVIGATION 的"机器面现状"边界注记随之删除（ADR-0095 的
  最后一条已登记后续工作收口）。
- T6 三元组校验的 repository_dispatch 回传路径两端语义平价（.github 与产品仓
  同样依赖 dispatch 载荷），跨仓回传布线不在本 ADR 范围（现网 T6 仍以标签事件
  为主路径，与 .github 现状一致）。
