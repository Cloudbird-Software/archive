# M7 漂移重估工作流设计定案

- status: accepted
- deciders: CEO agent (owner delegated)
- 关联: W11-C1 (w11-governance-push), DGA-INFRA M7, R-POOL-CALIB

## 背景
M7 漂移重估工作流设计草案已通过 C1 路径评审，需进治理仓正本。

## 决策
1. 文件落点：dga/infra/docs/m7-drift-reassessment.md
2. 复用 M3 feedback_loop.py 六段骨架，映射为漂移重估六段
3. AutoSuspendMixin 抽象 approval_wait 四件套（signal / wait_condition / timeout / marker），M7/M8 统一超时语义
4. outcome=suspended 不自动恢复，须 owner 人工介入（MET-01 安全边界）
5. PoolCompositionChange 事件 schema 采用 JSONB 内嵌快照，保持值对象完整性

## 后果
- DriftReassessmentWorkflow 状态机与活动签名成为 DGA-INFRA M7 正本
- M8 故障演练可复用 AutoSuspendMixin
- Temporal workflow 实现须引用本文件活动签名
