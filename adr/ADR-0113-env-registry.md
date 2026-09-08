# M5 执行环境注册表 schema 扩展定案

- status: accepted
- deciders: CEO agent (owner delegated)
- 关联: W11-C1 (w11-governance-push), DGA-INFRA M5, M7 R-POOL-CALIB

## 背景
M5 执行环境注册表 LinkML 扩展草案（ExecutionEnvironment / IsolationLevel）已通过 C1 路径评审，需进治理仓正本。

## 决策
1. 文件落点：dga/infra/schemas/include/m5-env-registry.md
2. ExecutionEnvironment 与 LogicalEndpoint 为 1:N 关系，不等价
3. IsolationLevel 枚举四级：process / container / vm / bare-metal，隔离降级须经授权（R-POL-02）
4. 环境 trust_label / isolation_level / health / quota 变更属于池组成变化的补充信号，须触发漂移重估候选

## 后果
- ExecutionEnvironment / IsolationLevel 成为 DGA-INFRA 本体扩展
- 本体变更触发 CalibrationDomain 漂移重估（human v1.1 §5.7 第三触发线）
- M7 PoolCompositionChange.target_type = EXECUTION_ENVIRONMENT 可直接映射
