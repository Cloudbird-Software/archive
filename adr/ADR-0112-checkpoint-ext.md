# M5 检查点外置接口 spec 定案

- status: accepted
- deciders: CEO agent (owner delegated)
- 关联: W11-C1 (w11-governance-push), DGA-INFRA M5, CMP-09

## 背景
M5 检查点外置接口完整 spec 草案已通过 C1 路径评审，需进治理仓正本。

## 决策
1. 文件落点：dga/infra/docs/m5-checkpoint-ext.md
2. Checkpoint schema 版本策略：SemVer，向下兼容，major 变更触发 S5 升级
3. 大结果外置指针级摘要（results_uri 字符串 + ETag，不包含对象内容本身）
4. resume_token 一次性语义 + 30 秒预留窗口 + compare-and-swap 防并发
5. WORM 锁释放条件：执行收据闭环 + 漂移重估消费 + 保留期届满

## 后果
- 检查点对象 schema / REST 接口 / 跨环境恢复流程成为 DGA-INFRA M5 正本
- M6 EvidenceEntity 新增字段（restored_from_checkpoint_id / failure_reason_code / checkpoint_event_type）须引用本文件 §2 类型定义
- 对象存储选型（SEL-07）须满足版本化 + WORM + 原子 CAS 能力
