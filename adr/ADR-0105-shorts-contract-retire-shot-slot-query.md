# ADR-0105: Shorts_Director 契约退役——shot_slot_query 下线与 applies_when 谓词内联（IR-0007）

- status: accepted（2026-09-01）
- deciders: 人（owner randypanding：V100 实测优先、仓库完全按新意图重构、
  与"生成一等公民"不符的内容均可丢弃或退役）+ AI（PM 会话，GLM-5.3）
- 关联: ADR-0038（契约兼容性门——本 ADR 依其程序处理 breaking/退役）；
  IR-0007（Shorts_Director spec PR #108，已签署合并）；卡 #110

## 背景

IR-0007 将 Shorts_Director 重构为"生成一等公民"的营销视频实验平台。
旧意图下的镜头槽位查询（ShotSlotQuery）与 planner 时序编译不再服务新
意图，按 owner 指令退役。删除前的最后完整状态由归档 tag
`archive/pre-retire-ir-0007`（指向 98a4b16）钉住，可随时回溯。

## 决策

1. **契约下线**：`schema/entities/shot_slot_query.schema.json` 连同其 G1
   样本（valid/invalid/evolution）、Go 实体层 `internal/slotquery`、
   `internal/planner` 一并删除；contracts 常量与 G2 双语言一致性登记表
   同步收缩。
2. **谓词内联（breaking，按 ADR-0038 留痕放行）**：qc_assertion v1 的
   `applies_when` 由外部 `$ref: shot_slot_query.schema.json` 改为内联
   `$defs.Predicate`——字段白名单扩展 `gen_form`/`model`，移除 semantic
   操作符。消费方 PR 按契约门程序引用 ADR-0038 放行。
3. **policy 收窄（本 ADR 的治理面）**：org policy（.github 仓
   governance/policy/contracts.yaml）中 Shorts_Director 的实体契约声明
   由 glob `schema/entities/**` 收窄为现存 schema 的显式枚举。原因：
   契约门引擎（CI-Workflows @4938955 钉扎版）对声明路径下的文件删除
   （CONTRACT_REMOVED）无条件红、无 ADR 豁免通道；引擎注释认可的唯一
   合法退役路径即"同步更新 policy 声明并引用 ADR"。
   - **有意接受的代价**：新增实体 schema 不再被 glob 自动纳管——新增时
     须同步在 policy 声明中登记一行，漏登由 review 与本索引追溯。
4. **引擎已知陈旧点（登记不修）**：钉扎版 contract_check.py 的 ADR 存在
   性校验仍指向迁移前家园 agent-registry/decisions（≤ADR-0084 可验）；
   ADR-0085 家园单仓化之后的 ADR（含本篇）不在其校验域内。故消费方 PR
   的机判引用须使用 ADR-0038（程序性引用），本 ADR 为实质决策记录；
   CI-Workflows 后续升钉时随修（引擎 ADR_DIR_API → archive/adr/INDEX.yaml）。

## 后果

- 契约面收缩、qc_assertion 自包含；shot_slot_query 消费面归零
  （applies_when 是其唯一消费方）。
- IR-0007 后续各卡若再退役 schema 文件，沿用本 ADR 确立的
  "policy 显式枚举同步 + ADR 留痕"通道，不逐次新开 ADR。
