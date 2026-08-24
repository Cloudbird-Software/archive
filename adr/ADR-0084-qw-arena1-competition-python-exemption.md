# ADR-0084: QW_Arena1 建仓申报与语言规范豁免——千问 AI Arena「一键出海」参赛仓（Python）

- status: accepted（2026-08-24）
- deciders: 人（owner randypanding）+ AI
- 关联: IR（Cloudbird-Software/.github#345——比赛原始要求全量冻结）；
  governance/REPOS.yaml（GM-4 申报入图）；governance/policy/languages.yaml（豁免对象）；
  GOVERNANCE flows.new_repo；ADR-0020（组织全仓公开政策）；ADR-0023（AI_Web_School
  语言准入豁免先例）；ADR-0025（agent-platform Python 准入先例）

## 背景

owner 报名参加千问 AI Arena「一键出海：商品素材全自动生成任务」（阿里 · 千问 AI 平台主办，
Aidge 联合主办，提交截止 2026-08-31，目标金奖）。参赛 Agent 的运行时契约由赛方规定：
产物 ZIP ≤100MB、根目录 `agent/`、入口文件四选一（agent.py / agent.js / agent.jar /
agent ELF）、依赖声明按运行时四选一（requirements.txt / package.json / pom.xml / go.mod）、
沙箱（Debian 12，Python 3.12 / Node 22 / JDK 17 / Go 1.22 四运行时）**零网络安装**——
全部依赖必须 vendored 进 ZIP；单次运行墙钟 ≤30 分钟、内存 ≤4GB；网络白名单仅千问模型
服务与模型产物 URL。

组织现行语言政策（languages.yaml application 层）默认 go，python 仅限
"agent-runtime integration only"（ADR-0025）。参赛仓不属于该准入情形，且比赛剩余
时间窗仅 7 天，预研（Spike）资产为 Python（路径解析/图像合成/类目匹配/视频兜底链）。
按 flows.new_repo 建仓需要语言选型依据；与政策冲突须组织层面登记豁免（本 ADR）。

## 决策

1. **建仓 QW_Arena1**：L2 实现层、public（ADR-0020 全仓公开政策）、template-service
   基线派生、按 scripts/new-repo-init.sh 完成基线设置（squash-only/合并删分支/auto-merge/
   wiki+projects 关）+ production environment（B 档）+ cloudbrid-agent 挂载（AG-4），
   并申报入 governance/REPOS.yaml（GM-4）。
   **bootstrap 豁免（ADR-0024 直推豁免先例的空仓变体）**：建仓时模板派生未生效
   （组织 rulesets 与 production environment 已配置但仓库为空仓——PR 流程在空仓上
   不可行，无 base 分支；组织级 org-required-workflows 规则对空仓直推 main 构成
   死锁）。template-service 基线 72 文件由 owner 凭据经临时 bootstrap 分支落盘、
   建立 main 后切换默认分支完成导入（全程未触碰组织 rulesets，main 根树与
   template-service 逐文件 sha 一致）；本条为该一次性豁免的登记，此后本仓一切
   变更必须走 PR+squash（BP-1）。
2. **语言选型：Python**。理由：
   a. 赛方入口契约下 Python 是预研资产与生态的最优解——Pillow 的 CJK 文字渲染成熟
      （图内多语言文字层是比赛刚需，模型直出韩/葡文字乱码风险高），图像/视频处理链
      Python 生态最全；
   b. 沙箱提供 Python 3.12，36 模型白名单的调用（DashScope/OpenAI 兼容）Python SDK
      一等公民；
   c. 7 天窗口内换语言重写 = 放弃参赛，不符合参赛目标。
3. **语言规范豁免（组织层面声明）**：languages.yaml 对 QW_Arena1 **整体豁免**——
   application 层 Go 基线与 PY-1/PY-2 等 gate 级语言规则均不适用于本仓。特殊原因
   （三条件同时成立）：
   a. **外部契约优先**：运行时形态（入口文件名/依赖声明格式 requirements.txt/
      agent.json/ZIP ≤100MB 全量依赖 vendored/零网络安装）由赛方规定，组织
      PY-2 的 uv lock 工作流与"离线 vendored ZIP"交付物形态直接冲突；
   b. **部署目标是比赛沙箱而非组织基础设施**：30 分钟/4GB/限流硬约束下，工程决策
      以比赛得分为最高优先级（IR #345 约束一）；
   c. **有限生命周期**：提交截止 2026-08-31，评审后按决策 5 退役，不是长寿命生产
      服务——语言政策"可维护生产代码库"的目标对象在本仓不成立。
4. **豁免边界（不豁免项）**：全仓公开（ADR-0020）、默认分支 PR+squash（BP-1）、
   gate/org-gate/adversary 双轨 required check、hygiene（gitleaks/zizmor）、
   CODEOWNERS、REPOS.yaml 申报义务（GM-4）、依赖审批 SLA（dependency_policy）——
   治理基线不变，仅语言规范面豁免。
5. **退役条款**：比赛评审结束（预计 2026-09 中下旬）后，QW_Arena1 转入 archived
   状态或删除；状态变更走 C1 PR 并引用本 ADR；参赛产物（提交 ZIP、评测记录、
   strategy_document）归档留痕后再处置。
6. **不修改 languages.yaml 本体**：豁免是仓级例外登记（本 ADR + REPOS.yaml role
   注记），不是组织政策修订——防止"比赛特例"稀释政策普适性（ADR-0023 同款先例）。
   任何新仓援引本豁免须新 ADR 论证三条件（外部契约/部署目标/有限生命周期）同时成立。

## 后果

- 正面：参赛获得治理化承接（可追溯/可审计/红队可锚定 IR #345）；7 天窗口内预研
  资产直接复用；语言例外有明确边界、理由与退役路径，不留政策松动口实。
- 负面/成本：组织内出现 AI_Web_School（ADR-0023）之后第二个语言豁免仓——豁免面
  扩大；template-service 继承的 Node 脚手架（package.json/tsconfig 等）在本仓
  首个实现 PR 中替换为 Python 结构（首 PR 落语言选型说明，引用本 ADR）。
- 风险与缓解：豁免被泛化援引为"任意仓可不遵守语言政策"——本 ADR 决策 6 显式限定
  三条件同时成立方可援引，且 REPOS.yaml role 注记即 drift-check 审计锚点。

## 验证

- QW_Arena1 仓线上存在且 public；REPOS.yaml 申报条目与线上一致（drift-check §7a）
- bootstrap 留痕：QW_Arena1 main 根树 72 文件与 template-service 逐文件 sha
  一致（ADR-0024 先例的空仓补救形态）；此后变更全部经 PR
- new-repo-init.sh 四步验证记录：基线设置 + production environment
  （required_reviewers + branch_policy）+ cloudbrid-agent 挂载（AG-4）
- 本 ADR 双落盘：agent-registry/decisions/ 墓碑 + INDEX.yaml 登记 + archive/adr/
  正本——archive verify.yml 三向 sha256 闭环背书（born-in-archive 分支）
- IR（.github#345）第一部分比赛原始要求与官方比赛页逐节可对照——spec 红队审查锚点成立
