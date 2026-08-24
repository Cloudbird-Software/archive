# retired/ —— 退役层快照（ADR-0085）

范式转变（PM 优先 + GitHub SSOT）后失去存在理由的声明层与实现层，快照于此供
考古；活体 git 历史见各 GitHub 归档仓。

| 目录/文件 | 原属 | 退役原因（ADR-0085 决策 2） |
|---|---|---|
| agent-registry/registry/ | agent-registry L1 | 九类 agent 声明/身份提示/26 I-O schema/teams/skills/tools——为 openjiuwen 编排框架准备，新范式角色载体=Actions 工作流+PM 会话 |
| agent-registry/standards/ | agent-registry L1 | 协作标准（team/event schema 等）——声明层随框架退役；retrospective 语义迁入 runs/ 报告环 |
| agent-registry/scripts/ | agent-registry L1 | validate.py（AR-2 声明门禁）/simulate-wave.py（ADR-0015 场景引擎）——校验对象退役，门禁废止 |
| agent-platform.md | agent-platform L2 | 渲染器/编译器/TUI——唯一职责是把声明渲染到 openjiuwen 运行时，无后续消费者 |
| agent-tools.md | agent-tools L2 | TS 工具服务器（bash/read_file/web_search…）——新范式工具=GitHub workflow+脚本+ghcb |

models.yaml 同随 registry/ 快照（gateway 路由组声明从未建成执行面；别名/配额/
failover 内核并入 cnb-bridge 与 providers.yaml 体系）。

删除即彻底：本目录不参与任何 gate/drift/运行时逻辑，仅为记忆。
