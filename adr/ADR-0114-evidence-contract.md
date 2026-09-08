# M6 证据契约 schema 扩展定案

- status: accepted
- deciders: CEO agent (owner delegated)
- 关联: W11-C1 (w11-governance-push), DGA-INFRA M6, archive evidence ledger

## 背景
M6 证据契约 schema 扩展草案已通过 C1 路径评审，需进治理仓正本。

## 决策
1. 文件落点：dga/infra/schemas/include/m6-evidence-contract.md
2. EvidenceEntity 新增字段：restored_from_checkpoint_id / failure_reason_code / checkpoint_event_type / payload_ref / tenant_id / card_ref
3. EvidenceType 枚举扩展：checkpoint_tamper / replay_attempt / orphan_checkpoint_cleaned / evidence-erratum
4. payload_ref 保留策略只增不减（30d/90d/180d/1y/3y/forever）
5. M5 PreliminaryEvidence 为轻量收据，闭环后升级为正式 EvidenceEntity，不直接入 archive 账本

## 后果
- EvidenceEntity schema 与 archive evidence ledger 三层纪律（判定层/轨迹层/丢弃层）正式对齐
- M6 decision-log-pipeline Stage 3 的 schema 转换以本文件为真源
- 控制面 DB 写入 EvidenceEntity 时 tenant_id / card_ref 为必填
