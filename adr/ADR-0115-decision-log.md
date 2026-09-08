# M6 Decision Log 管道 spec 定案

- status: accepted
- deciders: CEO agent (owner delegated)
- 关联: W11-C1 (w11-governance-push), DGA-INFRA M6, CMP-08/09

## 背景
M6 Decision Log 管道五阶段 spec 草案已通过 C1 路径评审，需进治理仓正本。

## 决策
1. 文件落点：dga/infra/docs/m6-decision-log-pipeline.md
2. 五阶段：Collection & Buffer -> Enrichment & Correlation -> Evidence Extraction -> Object Storage Ingestion -> Ledger Registration
3. fail-closed 语义：任何阶段异常/超时/数据缺失 = 红，不生成伪成功证据
4. 不降质：禁用 sampling / truncation；允许的降级仅为延迟与暂停
5. 背压链：Stage 5 -> Stage 4 -> Stage 3 -> Stage 1 -> 控制面

## 后果
- Decision Log 管道五阶段成为 DGA-INFRA M6 正本
- OTel Collector / 对象存储 / 控制面 DB 三方责任边界明确
- reconciliation job 补齐 staged 记录为闭环
