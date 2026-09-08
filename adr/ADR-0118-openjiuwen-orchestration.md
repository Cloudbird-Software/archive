# openjiuwen 编排落地方案定案

- status: accepted
- deciders: CEO agent (owner delegated)
- 关联: W11-C1 (w11-governance-push), SEL-04, ADR-0085

## 背景
openjiuwen 编排落地草案已通过 C1 路径评审，需进治理仓正本。

## 决策
1. 文件落点：dga/infra/docs/openjiuwen-orchestration.md
2. Phase A：单代理增强（TeamAgentSpec.build() 包装 PM 会话），替换裸 subprocess.run
3. Phase B：Swarmflow 固定工作流（红队/审计等），用 TeamWorkerBackend 替代手写并行
4. Phase C：复杂协调（autonomous dispatch + Temporal），待 Linux 机
5. 硬约束：不迁移 inbox/outbox 文件协议、不复活声明式 team 注册表（ADR-0085）、不改变波次协议

## 后果
- openjiuwen 编排方案成为 DGA-INFRA 运营层参考设计
- Phase A 试点收益：session checkpoint / model pool 共享 / team tools 可用
- Temporal 工作流落地前，swarmflow 仅 in-process / subprocess worker
