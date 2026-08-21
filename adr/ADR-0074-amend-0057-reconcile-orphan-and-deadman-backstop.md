# ADR-0074: ADR-0057 运行反馈修订——reconcile 孤儿标签语义收窄 + dead-man 双层触发

- status: accepted（2026-08-21）
- deciders: 人（owner randypanding，授权裁决"孤儿标签不重要，你处理"）+ AI
- 关联: ADR-0057（管家骨架，本 ADR 修订其两处）、宪法 §6（缺席即停）/§11（唤醒矩阵）、.github#162 之外的 W1 运行反馈（reconcile run 32484413154、deadman 首演 run 32481546304）

## 背景

W1 管家骨架上线后首轮真实运行暴露两处设计问题：

1. **reconcile 检查 (b)"孤儿标签"（closed issue 仍挂 state:*）全是噪音**：
   run 32484413154 报出 6 条，其中 5 条是 #130-134 的 `state:done`——卡完成
   关闭后保留终态标签是状态机的**正常终态形态**，不是漂移；#156 的
   closed+in-progress 属过程卫生瑕疵，不构成治理风险。且 v1 只报告不纠正
   （INV-02：状态标签写须 App 令牌经仲裁），该检查永远只能制造报告噪音。
2. **dead-man 的"缺席→自动停"存在断链**：healthchecks.io（owner 已注册，
   check URL 已配入 org secret DEADMAN_PING_URL，butler-heartbeat 实测
   ping 通）不支持自定义 HTTP header，无法直接回调 GitHub
   repository_dispatch（API 需 Authorization header）——外部服务只能
   "检测+向 owner 告警"，自动 trip 链路缺一段。

## 决策

1. **移除 reconcile 检查 (b)**：closed issue 退出状态机——其 state:* 标签是
   历史事实（label 真相源语义只约束在制工作），不是漂移对象；管家不纠正
   历史（防改史 + INV-02）。僵尸认领 (a) 与隔离超时 (c) 检查不变。
2. **dead-man 双层触发**：
   - **外部层**（宪法 §6 的"必须外部"由它承担）：healthchecks.io 检测
     ping 缺席 → 告警 owner（邮件/Slack，hc.io 账号侧配置）→ owner 一条
     命令触发 trip（runbook 已载）。覆盖"Actions 整体静默"形态。
   - **仓内层**（新增，自动化兜底）：`butler-heartbeat-watch` 周期
     （6h 错峰）查 butler-heartbeat 最近一次成功 run 的陈旧度，超过
     `butler.yaml deadman_stale_hours`（3h = 6 次缺失 ping）→ 自动执行
     deadman-trip（缺席即停）。覆盖"Actions 活着但心跳工作流被禁用/
     改名/损坏"形态。API 查询失败 = infra 红（exit 2）不 trip——同
     ADR-0040 决策 5：假熔断要求人工复位，会停摆整条流水线。
3. **trip 逻辑收敛单一实现**：抽 `governance/deadman-trip.sh`，
   butler-deadman-trip.yml（事件入口）与 heartbeat-watch 共用，防双实现漂移。

## 后果

- 孤儿标签不再出现在 reconcile 报告；已报过的历史 issue 不追溯处理。
- deadman 自动化从"仅演习可用"提升为常态在跑；但仓内层不能覆盖
  "Actions 全挂"（此时 watch 也死）——该形态依赖外部层告警 owner，
  runbook 载明 owner 收到 hc.io 告警后的一键 trip 命令。
- hc.io 侧建议配置：period=30min（对齐 heartbeat cron），grace=60min，
  告警通道 owner 自选（文档 docs/deadman-setup.md）。
- 回滚：revert 本 ADR 对应各 PR（检查恢复 / watch workflow 删除）。
