# M7 成本熔断策略 spec 定案

- status: accepted
- deciders: CEO agent (owner delegated)
- 关联: W11-C1 (w11-governance-push), DGA-INFRA M7, cost-check.sh, R-POOL-BUDGET

## 背景
M7 成本熔断策略完整 spec 草案已通过 C1 路径评审，需进治理仓正本。

## 决策
1. 文件落点：dga/infra/policies/m7-circuit-breaker.md
2. 预算四元组统一 schema（BudgetQuadruple / CostBudgetChannel），对齐 cost-check.sh 三通道
3. 熔断五态状态机：CLOSED / WARNING / OPEN / HALF_OPEN / INFRA_FAIL
4. fail-closed 语义：INFRA 故障时不盲置熔断、不静默归零
5. 复位仅人工：S5 / owner 通过控制面 API POST /v1/pool/breaker/reset（需 approval_ref）

## 后果
- 成本熔断五态状态机与 BudgetQuadruple schema 成为 DGA-INFRA M7 正本
- cost-check.sh 硬停档 / 告警档 / INFRA 故障四区间行为升格为控制面策略
- PoolHealthSnapshot 扩展字段（budget_utilization_pct / circuit_breaker_state 等）须引用本文件
