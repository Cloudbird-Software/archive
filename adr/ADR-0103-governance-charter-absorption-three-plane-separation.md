# ADR-0103: 治理总纲吸收——三面分离架构、证据账本统一与云内网入图

- status: accepted（2026-08-29）
- deciders: 人（owner randypanding，2026-08-29 会话逐项锁定——spec amendments 所称
  "11 项锁定决策全集"即本 ADR 决策 1-8 加三项建设次序裁决）+ AI（PM 会话，GLM-5.3）
- 关联: 宪法 v2.3 §5/§12（本 ADR 不推翻、只延伸）；ADR-0003（过程数据三分离——
  证据三层承其谱系）；ADR-0040（成本熔断复位流程，本 ADR 复用不重定义）；
  ADR-0085（PM 范式——执行面语义随本 ADR 扩展）；ADR-0062（metering hash 链——
  判定层账本平移其机制）；IR-0006（Cloudbird-Software/.github#402；规格=
  specs/IR-0006/，含 absorption-map.md 与 wave-plan.md 两附件）

## 背景

owner 撰《治理战略总纲 v1.0》（git 外文档）：五层平面/五回路/Wave 对象/能力票据/
证据账本/飞书界面/多租户/治理外输三层。四个结构性问题必须裁决：

1. **宪法冲突**：总纲 §2.2/§5.1 的 `risk_class: R2` 总旋钮与已签署宪法 v2.3 §5
   （废除标量风险分，硬谓词+shadow 域解锁）直接矛盾——两份宪法级文件互斥。
2. **治理盲区**：云内网（公网服务器+云电脑池+Vault+LLM 路由）已是事实生产工厂，
   但 REPOS.yaml/providers.yaml 均无申报——按 GM-4 哲学未申报=漂移，且该漂移
   不可被检测（对象在 GitHub 之外）。
3. **铁律违背**：总纲正本存于 git 之外，违反"凡不能写进 Git 声明的就不能被输出"。
4. **证据碎片化**：判定/轨迹数据散在三处（metering hash 链、butler audit、
   drill history），三套 schema 互不相通，无 tenant 字段（潮玩公司共用额度无归因）。

## 决策

1. **裁决模型调和——旋钮管配置不管裁决**：总纲 risk_class 降维为**参数包选择器**
   （选门禁集/entitlement 档/人工介入点），放行裁决仍硬谓词白名单+shadow 域解锁
   （宪法 §5 原样不动）。外输语言=参数包+谓词白名单+域解锁进度清单，非风险分。
   任何把裁决语义参数化的条款变更=违宪，须新 ADR 推翻 §5 才可提出。
2. **三面分离**：治理体系按声明面（Git：治理仓 specs/、governance/、env 定义仓）
   /执行面（多域：GitHub Actions、云内网、CNB 池）/判定面（恒定 GitHub CI：
   gate/org-gate/conductor）组织。云内网=执行域+证据冷存储层。判定锚点永不外置
   （INV-02：云内网池与 CNB 同为可删除层，删除后判定语义不变，EX-1 延伸）。
3. **证据账本三层**（承 ADR-0003 过程数据三分离）：判定层（archive 仓 evidence/，
   git 永续，append-only+hash 链平移 ADR-0062+月度 checkpoint，链断=红）/
   轨迹层（内网 blob；git 只存 sha256 摘要+指针+保留策略字段；payload 内联上限
   4KB 超限拒写）/丢弃层（GitHub 事件面 transient）。三源（metering/butler/drill）
   渐进对齐：新事件按 schema v1 双写过渡，原 JSONL 只读冻结（平移不搬移）。
   每条判定记录必含 tenant 字段。
4. **执行织物分界**：GitHub 能启动的一律 GitHub Actions（不自建平行织物）；
   自建调度器只承载 PM 长驻会话与需内网资源作业；池化以公网服务器为锚
   （唯一出入口+调度+票据签发）。调度器=执行面基础设施≠harness
   （自建 harness 判据 ≥3 次妥协不变）。
5. **PM 凭证收敛**：PM 会话 GitHub 凭证由服务器代签 cloudbrid-agent 短令牌
   （单仓作用域+短 TTL≤波次；个人 PAT 退出日常流程，应急回退通道保留 24h 窗口）；
   JIT 能力分发与 elevation 由服务器+arbiter 策略表承担（请求附理由+spec 引用，
   批准记录进账本）。agent 上下文零凭据边界不变（AR-2 延伸）。
6. **总纲分散吸收**：18 章节落位表+词汇归并表（absorption-map.md）为总纲内容
   唯一去向清单；不立独立总纲文档；已被现有机制覆盖的章直接映射（防双 SSOT）；
   总纲原文不进 git，讨论副本一律视为草稿。
7. **飞书 outbound-only**：多维表格=factory-floor 投影体系第四投影（宪法 §12 三投影
   之外新增），label 唯一真源，drop & rebuild 单轮保真，人工修改被下轮纠正并告警；
   inbound 意图通道（污点标记/typed intent）延后另行立项。
8. **建设次序**：内部跑通优先（六波次 W1-W6 按依赖重排，见 wave-plan.md）；
   治理外输三件套（Profile/Policy Pack/Conformance Report）内部跑通后另行立项；
   潮玩公司不做完整分家工程，仅计量 tenant tag 先行。

## 后果

- 正面：宪法冲突消解（§5 不动）；最大治理盲区（云内网）入图可对账；证据面统一
  可查询且 tenant 可归因；总纲权威收编进 git 声明面。
- 代价：三源双写过渡期一个波次（运维双倍写入）；env 定义仓与调度器为新增维护面。
- 红线重申（本 ADR 全程不变）：INV-01 判定语义、INV-02 判定锚点不外置、
  INV-03 append-only、INV-04 凭据纪律（key 只存 org secret/Vault）、
  INV-05 label 唯一真源、INV-06 payload 指针纪律（4KB）。
- 执行载体：IR-0006（#402）六波次；验收=各波次退出判据+specs/IR-0006/acceptance.md
  （T-15 逐条回探十条期望变化+冷上下文六问复测）。
