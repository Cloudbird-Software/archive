# M5 MCP 适配器协议 spec 定案

- status: accepted
- deciders: CEO agent (owner delegated)
- 关联: W11-C1 (w11-governance-push), DGA-INFRA M5, SEL-04

## 背景
M5 第一顺位设计件 MCP 适配器协议草案已通过 C1 路径评审，需进治理仓正本。

## 决策
1. 文件落点：dga/infra/docs/m5-mcp-adapter.md
2. 传输模式：stdio / SSE 双支持，HTTP 为未来扩展；默认由路由层根据 ExecutionEnvironment.isolation_level 选择
3. 一切工具调用必须经过 OPA 网关（R-POL-01 / SEL-04 负面测试项），本文件为强制约束
4. A2A 对接面预留，不纳入 M5 范围

## 后果
- MCP Adapter 协议边界成为 DGA-INFRA M5 正本
- openJiuwen agent-protocol MCP SDK 集成须遵守本文件 §3.6 接口约束
- SEL-04 PoC 结果将触发 A2A transport adapter 扩展，须经 C1 路径
