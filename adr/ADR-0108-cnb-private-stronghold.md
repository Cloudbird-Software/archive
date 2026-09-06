# ADR-0108: CNB 私有阵地声明（DGA 三阵地结构——考卷公开、答案密封）

- status: proposed（owner 签署待落=S-7；B1 阵地核验完成前不执行任何迁移）
- deciders: 人（owner randypanding——DGA-ADJUDICATION v1.0 §2，2026-09-06）+ AI（现场编码 agent 依 IR-0010 卡 B1 起草）
- 关联: ADR-0020（效力范围确认为 GitHub org，不变更）；DECISION-02（挂载禁令延伸）；
  INV-04（凭据分域延伸）；IR-0010 卡 B1/B2（执行载体）；DGA v1.1 §4.3 其二·附
  （补丁单 P-1，待原文应用——隔离的两种实现形态）

## 背景

断裂 FR-01 裁决（ADJUDICATION §2）：威胁模型两层分解——agent 行为威胁（本组织执行者
违规读取）可检测，检测式防线充分；外部抽取威胁（平台条款训练权——GitHub ToS D.4 对
公开内容授出 AI 训练权、公开抓取）不可检测，对不可检测的威胁唯一防线是真保密。
判定基准折旧（DGA §4.3）：golden 公开=该用例信息量永久归零，轮换律只对冲增量不能
复活存量。

## 决策

1. **CNB 私有仓 stronghold 为组织私有阵地（真值区）**，承载判定资产答案层。
2. **阵地范围**——可入：holdout 答案层（golden 断言+判分逻辑）、evalsets 答案域、
   判分 rubric、私有 spec、迁移台账、未来的客户实例参数（D-内部 级）。禁入：一切
   开发侧 agent 可读物（spec/代码/卡/AGENTS.md）；D-客户敏感数据（挂宪法触发器，
   触发前不入）；任何与答案层无关的便利性存储。
3. **凭据与访问纪律（INV-04 延伸）**——stronghold token 作用域=单仓读写；存 org
   secret 专用分域；禁止进入：开发侧计算池（cnb-bridge 派单面）、PM 上下文、任何
   agent 会话、GitHub Actions 执行侧（除 verifier 验证路径专用最小凭证）；
   verifier-app 获得唯一验证读权（DECISION-02 延伸：cloudbrid-agent 挂载禁令覆盖
   stronghold）；验证路径凭据 TTL ≤ 单次揭封周期。
4. **与公开面的关系**——GitHub 公开侧仅持有 sealed 指针（id@sha256 引用纪律不变）；
   答案层负载出现在 GitHub 任何仓=漂移事件（drift-check A1 断言执法）。历史暴露
   条目以 supersession 处置（揭封台账墓碑化+重生成新密），不重写 git 历史。
5. **失效语义（DGA §2.3 声明的失败语义）**——CNB 不可用：判定延迟至恢复（E1 判定
   任务只延迟不降质）；灾备恢复经 Gitee 密文 bundle（B7 演练路径）。stronghold
   本身丢失：以台账+Gitee bundle 重建。
6. **回退判据**（ADJUDICATION §2 诚实标注）——CNB 私有仓核验（B1 实测）不满足时，
   位置互换预案（Gitee 私有为阵地、CNB 为镜像一）属 owner 裁决项，agent 不得自选。

## 后果

- 正面：答案层出真实保密域（外部抽取威胁面关闭）；判定基准停止公开折旧；GitHub
  全公开政策效力范围不变（狗粮公示与获客不受损）；
- 代价：私有阵地运维面+1（凭据分域、对账、揭封路径改造）；ADR-0020 的"无豁免路径"
  措辞在 CNB 侧不适用（其效力范围确认为 GitHub org）——本 ADR 即该边界的形式声明；
- 执行门禁：迁移（卡 B2）前置=B1 核验绿+本 ADR owner 签署（S-7）+暴露审计 supersession
  清单确认（S-8，条件触发）。
