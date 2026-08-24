# ADR-0085: PM 优先范式转变——阶段门禁 + 阶段内自主，多 agent 编排层退役

- status: accepted（2026-08-25）
- deciders: 人（owner randypanding，2026-08-24 夜间裁决四点 + 全量授权执行）+ AI（首位 PM 会话，GLM-5.3）
- 关联: ADR-0053（archive 记忆层与 ADR 迁移——本 ADR 收口其双世界）；ADR-0049
  （conductor 状态机）；ADR-0050（spec-author）；ADR-0055（入口协议）；ADR-0057
  （管家唤醒矩阵）；ADR-0082（红队守门）；ADR-0083（suite 门）；IR-0004
  （Cloudbird-Software/.github#315，CNB 底座与 fan-out——执行者语义随本 ADR 修订）；
  IR-0005（Cloudbird-Software/.github，本 ADR 的实施载体）

## 背景

组织此前按"多 agent 编排框架"预设建设：agent-registry 声明九类 agent 身份/身份
提示词/26 个 I/O schema/teams/skills/tools，agent-platform 把声明渲染到 openjiuwen
运行时，agent-tools 提供 TS 工具服务器。2026-08-24 owner 形成新认识并裁决：

1. **强模型的规划能力已足以承担项目经理（PM）角色**；软件开发的不确定性无法
   全靠预设流程定义清楚。公司只规定**阶段门禁**（IR→spec / spec+suite 过红队→
   开卡 / 卡完成+全 gate 绿 / IR 全面验收四道），**阶段内部怎么调用资源与工具，
   完全交给 PM 自主决定**——上升策略不预设，先由 PM 实践、经运行报告沉淀后再成文。
2. **CNB 免费算力（多账号池）为默认开发主力**：常规实现卡默认派 CNB 沙箱，
   强模型 PM 处理 gate 红/语义敏感的上升问题。IR-0004 的决策矩阵"低决策密度"
   分支执行者由本裁决确定为 CNB 优先。
3. **暂不做强可观测性建设**：以 PM 运行报告（archive/runs/）+ 周度机械 digest
   构成最小持续改进闭环，指标化等范式稳定后再议。
4. **GitHub 即 SSOT**：状态机（conductor）+ Actions 内角色（红队/验证者/PM 自起
   协议）已覆盖编排框架的全部现实职能，显式 agent 身份声明层失去存在理由。

冷上下文 PM 模拟（2026-08-24，六问协议）证实旧入口仅为"工人"视角：找不到 PM
角色入口、全流水线视图、资源目录、复盘落点与凭据获取方式——范式转变即修复
这些断点。

## 决策

1. **四道阶段门禁为组织控制的全部过程面**；阶段内资源调用方式不设预设流程。
   PM 自主性的不可触碰边界（恒定）：判定语义（生成/裁决分离，INV-01/02）、
   fail-closed 语义、append-only 账本、一切凭据纪律。自主的是生成路径，
   永不自主的是判定语义。
2. **退役多 agent 编排层**：agent-registry 仓的 registry/（agents/identities/
   schemas/teams/skills/tools）、models.yaml、standards/、validate.py、
   simulate-wave.py 快照入 archive/retired/ 后整仓 GitHub 归档；
   agent-platform、agent-tools 两仓整仓 GitHub 归档（git 历史即存档）。
   GOVERNANCE agent_runtime 域（AR-1..AR-9 声明类条款）随之重写。
3. **ADR 家园单仓化**：INDEX.yaml 墓碑索引从 agent-registry/decisions/ 迁至
   archive/adr/INDEX.yaml，与正本同仓；gate.yml / org-gate.yml / drift-check §10
   三处校验改址 archive/adr/。新 ADR 直接 PR 至 archive/adr/ 并更新 INDEX。
   （ADR-0053 双世界自此合并为单世界。）
4. **AGENTS.md 重写为 PM 手册**（entry-protocol v1 块字节不变，保 §17 对账），
   新增 docs/pm/PLAYBOOK.md（阶段手册：资源目录/用法/代价/红线）。
   ghcb 扩展 board（全状态流水线视图）/dispatch（CNB 派单）/accept（验收报告
   草稿）/report（运行报告骨架）四个子命令。
5. **状态机补洞与新门**（transitions.yaml + conductor）：T7 wave-planned→ready
   （卡具备认领条件）；T8 in-progress→done（谓词=存在绑定本卡且已合并的 PR，
   机械查证 Card: 元数据）；T9 IR 级验收 wave-planned→done（谓词=全部子卡
   state:done + specs/IR-*/acceptance.md 验收报告存在）。T1/T2 的
   action: invoke:spec-author 降级为 noop——spec-author 流水线保留为可选快速
   通道，PM 自著 spec 与流水线产出在门禁面前制度等价（PR338 先例追认）。
6. **CNB 底座落地**（承接 IR-0004 D 组，按本 ADR 裁决 2 修订执行者语义）：
   独立仓 cnb-bridge（L2，可删除层）集中多账号池（accounts.yaml，无明文
   token）、派单协议（issue 窗口 @CodeBuddy + work_mode）、配额账本、
   work-inbox PM 自起协议、REMOVAL.md 单页删除清单。org secrets
   CNB_TOKEN_<ALIAS> 为唯一凭据通道；.github 侧 cnb-dispatch/cnb-audit 两
   工作流 + GOVERNANCE EX-1 声明条目构成三接缝。隔离审计 grep 口径＝操作性
   引用（endpoint/token/派单协议字样），目录导航性提及（如仓库名）不计入。
7. **凭据最小方案**（池化工具通用）：org secret 保险箱 + workflow 经纪人 +
   无密钥目录（governance/providers.yaml）+ 计量 wrapper。PM 上下文永不出现
   任何 key；调用一律借道 dispatch 工作流。加工具=加 secret+加目录条目，零代码。
8. **运行报告闭环**（最小机制）：PM 每次 run 结束向 archive/runs/YYYY-WNN.md
   追加三节式报告（事实/体感/改进点，改进点为 [followup] 行）；archive 仓
   runs-digest.yml 周一抽取全部 [followup] 行开 digest issue；owner 处置
   （转卡/转 IR/否决留痕）；新 PM 冷启动必读最近 4 周（PLAYBOOK 入职第三步）。
   报告是经验输入与改进燃料，**不是验收证据**（自述不可核实原则，
   event.schema 既有先例）。
9. **验收测试制度化**：冷上下文六问协议（第一天干什么/进行中工作/IR→spec
   路径/可调资源/复盘落点/key 获取）作为 PM 入口面的回归测试——范式类变更
   后重跑，六问全答出且零断链方为过。

## 后果

- IR-0004 spec 以 rev6 修订（CNB 默认实现主力、ASSUMPTION-03 升格 DECISION、
  AC-10 低决策密度分支执行者=CNB），其余 21 条 AC 与实施波次卡不变。
- verifier_app / cloudbrid-agent 对退役仓的挂载保留只读（archived 仓写路径
  自然失效），清单收敛随下次 App 权限窗口处理。
- openjiuwen 上游（REPOS.yaml external_upstreams）停止消费，条目移除。
- 本 ADR 正本与 INDEX 登记即为新流程首个用例：archive/adr PR + INDEX 更新，
  gate 双世界校验从本 PR 起指向单世界。
