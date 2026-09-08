# ADR-0110: M5 Harness 架构 spec 定案

- status: accepted
- deciders: CEO agent (owner delegated)
- 关联: W11-C1 (w11-governance-push), DGA-INFRA M5

## 背景
M5 第一顺位设计件 Harness 架构 spec 草案已通过 C1 路径评审，需进治理仓正本。

## 决策
1. 文件落点：dga/infra/docs/m5-harness-spec.md
2. 命名：保留 harness 架构 spec 语义，不拆分为多文件
3. 接口边界（MCP 适配器 / 检查点外置 / 执行环境路由）以本文件为准，后续 M5 实现 PR 须引用本文件段落编号

## 后果
- Harness / MCP Adapter / Checkpoint 三层接口边界成为 DGA-INFRA M5 正本
- 后续 schema 扩展（ExecutionEnvironment / IsolationLevel）须与本文件 §5 对齐
- M6 证据契约 / M7 漂移重估可引用本文件状态机与恢复流程
