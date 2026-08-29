# ADR-0103: 治理总纲吸收——裁决模型调和（risk_class=参数包）与声明/执行/判定三面分离（IR-0006 治理背书）

- status: accepted
- date: 2026-08-29
- deciders: owner（randypanding，2026-08-29 会话四项顶级决策问答确认：调和/内部跑通优先/三面分离建议/分散吸收）/ 治理梳理会话 agent（登记）
- resolves: IR-0006（Cloudbird-Software/.github#402）宪法层/控制平面/证据层/执行面的治理背书
- 关联: 宪法 v2.3 §5（specs/IR-0003/constitution.md，硬谓词白名单+shadow 域解锁）；ADR-0003（过程数据三分离）；ADR-0085（PM 优先范式）；ADR-0062（计量 hash 链）；GOVERNANCE.yaml EX-1（外部算力可删除层）

## 背景

《治理战略总纲 v1.0》（愿景：五层平面/五回路/Wave 对象/能力票据/统一证据账本/飞书界面/多租户/治理外输三层）与已签署宪法 v2.3 存在三处实质冲突，且云内网（公网服务器+云电脑池+Vault+LLM 路由）已成事实生产工厂但完全未入治理版图：

1. 总纲 `risk_class` 总旋钮 vs 宪法 §5 已废除标量风险分（硬谓词+shadow）；
2. 总纲 6.1「唯一物理咽喉 broker」vs I6 可移植性铁律与 EX-1「判定永不外置」先例；
3. 总纲本身在 git 之外，违反"凡不能写进 Git 声明的就不能被输出"。

owner 于 2026-08-29 会话逐项裁决（调和/内部跑通优先/三面分离/池化以服务器为锚/日志策略声明式/GitHub 能启动的不自建/PM 凭证收敛 App 令牌/飞书先 outbound 多维表格/分散吸收）。

## 决策

1. **裁决模型调和**：`risk_class` 降格为**参数包选择器**——只选择门禁集/entitlement 档/人工介入点等声明层参数；放行裁决仍由硬谓词白名单+shadow 域解锁决定（宪法 §5 原样不动）。外输语言：档位=参数包+谓词白名单+域解锁进度清单，非风险分。**"裁决"与"配置"分离**：旋钮管配置，不管裁决。
2. **三面分离（控制平面归宿）**：声明面=Git（环境定义/Job Contract/身份映射/票据策略/预算——意图 SSOT）；执行面=多域（云内网+GitHub Actions+CNB，broker 是逻辑契约非物理咽喉，按域物理适配）；判定面=GitHub 恒定（gate 裁决/验收/holdout，永不外置——INV-01/02 延伸）。云内网=执行域+证据冷存储层，不是控制平面的家；env repo 存期望态+云内网上报实况+复用 drift 模式对账（云内网不需要承载声明，只需要服从并对账）。
3. **证据三层（承 ADR-0003 过程数据三分离）**：判定层（裁决/成本/审批/决策语料/hash 链头）落 archive 仓 append-only，hash 链从 metering 平移，月度 checkpoint 滚动归档，永久保留；轨迹层（完整 trace/上下文快照/tool I/O）落云内网对象存储，git 只存 sha256 摘要+指针+保留策略；丢弃层（CI run 日志）走 GitHub 原生保留，账本只记 run URL+conclusion+digest。**payload 指针纪律**：账本只存结论+指针，内联上限 4KB；保留策略（hot/warm/digest-only）声明式进 GOVERNANCE 条款（可 drift 对账、红队可审、随 policy pack 交付）。
4. **执行织物分界**：GitHub 能启动的一律 GitHub Actions（可重跑负载与 CNB 同位同受 EX-1 约束）；自建调度器（服务器上）只承载 GitHub 侧无法启动的——PM 长驻会话与需内网资源（Vault 直连/冷存储/LLM 路由）的作业。**非自建 harness**（不碰模型调用循环/diff/编辑器；≥3 次妥协触发自建判据不变）。池化以公网服务器为锚：唯一出入口+调度器+票据签发；worker 不直连公网；worker 身份=服务器签发的池内短票据（绑定机器非绑定人）。surrogate secret/egress proxy 是该拓扑的副产品，非待建组件。
5. **PM 凭证收敛**：PM 会话的 GitHub 凭证收敛为服务器代签的 cloudbrid-agent 短令牌（gh-app-token 机制上收内网服务器）；JIT 能力分发由服务器端路由工具承担；个人 PAT 退出日常流程（App 令牌失效→owner PAT 应急通道 24h 窗口保留）。
6. **总纲落位**：分散吸收进 .github 仓——18 章节落位表+词汇归并表为 IR-0006 spec 附件；不立独立总纲文档。词汇归并防双 SSOT：Wave≡card issue+wave-plan（扩展 schema 不新建 kind）、Capability Broker≡providers.yaml+dispatch 经纪人+gh-app-token（升级不重建）、证据账本≡metering/butler/drill 三源统一（合并不另立）、Channel manifest≡label→board 投影体系第四投影（label 唯一真源铁律不变）。
7. **飞书 outbound-only**：多维表格看板=factory-floor 投影（每行一卡，字段=状态/关卡/认领者/停留时长），物化视图可 drop & rebuild；inbound 意图通道（污点标记/typed intent）延后另行立项。审批结果落账本，门禁读账本不读飞书。
8. **建设时序**：内部跑通优先（无外部硬时点）——外输三件套（Profile/Policy Pack/Conformance Report）延后；潮玩公司仅计量 tenant tag 先行（showback），分家工程不做。

## 影响

- IR-0006 spec 的落位表与六波次总图以本 ADR 为裁决依据；宪法 v3 修正范围由落位表确定，§5 不动是硬边界；
- providers.yaml 将新增 self-cloud-pool/vault 条目、REPOS.yaml 将新增 env 定义仓条目（GM-4 申报，W1-C）；在此之前云内网"不可检测漂移"盲区仍存（诚实记录）；
- metering/butler/drill 三源 schema 对齐工程启动（hash 链平移不搬移，原 JSONL 只读保留可回退）；
- 外输叙事变化：卖的是"参数包+谓词白名单+域解锁进度"，不是风险分——销售语言与宪法语义一致；
- 代价与风险：两套语言（档位/谓词）并存有心智成本；云内网对账面建成前其上状态不受治理保护（仅凭凭据纪律与拓扑约束兜底）。

## 红线重申

判定语义不随本次吸收改变（生成/裁决分离、fail-closed、append-only、凭据纪律四条恒定）；CNB 与云内网池同为可删除层，删除后 gate/org-gate/conductor 语义不变；多账号 key 轮换维持否决。
