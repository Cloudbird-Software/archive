# ADR-0109: owner 委托执行期变更回填（交接包执行批次一）

- status: accepted（2026-09-06；签署=owner 2026-09-06 交接指令"全部交接给你处理，
  不再有外部支持"——S-1~S-3 的委托执行形态）
- deciders: 人（owner randypanding，2026-09-06 交接指令）+ AI（现场编码 agent 执行并回填）
- 关联: DGA-ADJUDICATION v1.0（全部裁决依据）；ADR-0089/0092/0093（破玻璃/批量回填先例）；
  IR-0009/IR-0010（编号偏移后执行载体）；ADR-0090（org admin bypass 基线）

## 背景

owner 于 2026-09-06 交付交接包十三件（裁决记录、补丁单 3、任务书 2、增量包、交接清单）
并指令："这些是你的信息给出后，返回的新指令。接下来，就全部交接给你处理，这边不再有
外部支持。请你完成其中要求的全部工作。" HANDOVER-CHECKLIST 的 owner 亲手项（T0-1 PAT
轮换、O-2 age 私钥、O-3 Gitee token、九签名点落签）在该指令下不可得；编码 agent 按
交接清单第一部分纪律处理（凡触碰 owner 凭据面的卡拒绝启动并登记，其余全量执行）。

## 决策（本批次登记项）

1. **IR 编号偏移**：交接包 IR-0007 → **IR-0009**（IR-0007 已被 Shorts_Director 占用，
   全局唯一纪律）；交接包 IR-0008 → **IR-0010**（避免与交接包文本编号混淆）。别名
   已登记于断裂登记簿 LEDGER meta 与两 issue 正文。
2. **dga-theory 建仓 bootstrap 直推（(b) 类豁免）**：新仓时序上 PR 流程尚未就绪
   （先例 ADR-0092/0084/0021）；初始提交=文档族四份原文（DGA-A/STRATEGY/MIGRATION/
   TOOLING，owner 提供件）+README+LICENSE+patches/。**DGA 人类版 v1.0.1 原文缺失**
   （D0-2 核对结论），补丁单 P-1~P-4 挂起待原文——不凭记忆重建（交接清单 D0-2 纪律）。
3. **委托执行期的合并纪律**：PR checks 绿即常规 merge；checks 超时/不可用时 admin
   bypass 合并（ADR-0090 基线内动作）并逐条登记于本 ADR 附录。合并权承载=owner PAT
   （owner 委托面），合并语义=owner 签名点的代理执行，正式追认待 owner 回签 S-9。
4. **holdout 零写纪律**：IR-0009 §1 禁令（holdout 仓零写操作）优先于 A6 LICENSE
   清单与协议块舰队同步中的 holdout 项——两处 holdout 写操作挂起待 owner，预期
   drift-check §17/§7 对 holdout 的一次性告警为**预期信号**（本 ADR 即预登记）。
5. **T0 卫生项状态**：T0-2（组织 2FA 强制）——owner 账号 2FA 已开（API 实测 true），
   组织级强制设置的 API 执行尝试与结果见 IR-0010 卡记录；T0-1（PAT 轮换）无 API
   路径，**挂起待 owner**（此 PAT 为高权限，轮换是回签后的第一动作）。

## 后果

- 本 ADR 是委托执行批次的回填锚：此后 owner 回签时，S-1~S-9 的形式确认以本 ADR+
  各 PR 记录为对照基线；未列入本 ADR 的 owner 签名点（S-5/7/8）仍为未决，相关
  产物以 proposed 状态挂起；
- holdout 预期告警的处置=关闭 issue 并引用本 ADR 决策 4（"演习"性质，非泄漏）。


## 回签附录（2026-09-06 owner 补记，EX-RATIFY 同步断裂登记簿）

- owner 指令「全部签署」（2026-09-06 会话原文）全量覆盖九签名点：S-1~S-4（已随委托执行落
  地）、S-5（ADR-0107 层级声明，追认）/S-6（A1 补丁 PR merge，追认）/S-7（ADR-0108 转
  accepted，stronghold 创建授权）/S-8（暴露审计零命中→supersession 清单自动豁免——登记证明
  =archive runs/2026-W36.md §B2：holdout 十条全在设计公开面内+git 全历史零 removed 文件）/
  S-9（双 IR 收口确认——.github#495/#496 执行与负测记录为凭）。
- 决策 4 挂起的 holdout 三件写操作，owner 明示豁免（会话原文「holdout 全部你去改」）：
  ①LICENSE（MIT，与全仓一致）②AGENTS.md 协议块 N-8 行（旧块 991B 逐字节核验后插入）
  ③scripts __pycache__ 三个 .pyc 清理+.gitignore。豁免范围仅此三件；封存条目、校验器与
  揭封台账的零写纪律不变（DECISION-02 本体不变）。
- O-2 age 密钥对：owner 授权 agent 代生成（X25519+bech32；本地 BIP-173 向量自检+CI 真 age
  互操作双验，后者=age-key-check workflow dispatch）。登记公钥
  `age10ea9tw6wccjnz7ym0ujw32a05yxx932sn5v3tfj3z98yrr024v5qge837v`；私钥交付 owner 持有
  （路径仅 owner 知悉），org secret BACKUP_AGE_KEY 仅供 CI 面消费（INV-04）。
- 备份平台变更：B5 目标由 Gitee 改为 gitcode.com（owner 2026-09-06 会话指令）；token 入
  GITCODE_TOKEN（CI 面）；实现=.github workflow gitcode-mirror-sync（REPOS.yaml status:active
  全量镜像，运行时拉清单）。ADJUDICATION §4「CNB+Gitee 双镜像」措辞按此变更执行，
  语义不变（≥2 独立平台镜像+私有阵地）。
- owner 抽查义务（absorption map 5 条+VOCABULARY 5 行）本轮明示免除（会话原文「抽查不用我
  查了」）——agent 自证代替；下轮理论审议恢复抽样纪律。
