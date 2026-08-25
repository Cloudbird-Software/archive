# ADR-0087: X-04 formal_tla 条款从 rejected 激活为 triggered

## 状态
accepted

## 上下文
- testing.yaml X-04 (formal_tla) 处于 `rejected` 状态，理由“无调度器/共识组件”（revisit_when: “写分布式协调组件”）
- IR-0004 AC-7 交付了 `pipeline/testing/formal/trigger.py` + `checklist.yaml`：risk_level 缺失时 fail-closed 的条件触发器
- 触发器不需要 TLA+调度器运行时——它读 YAML checklist 对 spec 文本做机械判定（纯 I/O，无外部依赖）
- ADR-0085 PM 优先范式：PM 自主决定工具使用，门禁由 spec 自然携带

## 决策
X-04 从 `rejected` 移至 `triggered`。触发条件：spec 中 risk_level 字段缺失 → checklist.yaml 任一正条件命中 → trigger.py 报红 → 开发者补充或显式标记 N/A

## 理由
- 仪器已就位（trigger.py + checklist.yaml，IR-0004 #328，28 自测全绿）
- 不需要 revisit_when 条件中的“分布式协调组件”——机械文本判定 ≠ 运行时模型检查
- PM 优先范式下 trigger 即 PM 可选用具（ADR-0085）

## 后果
- testing.yaml X-04 条目：rejected → triggered，触发条件记入条目
- INDEX.yaml 新增条目
- 现有 spec 无需立即改动（触发器按需生效，非强制全量审计）

## 关联
- IR-0004 AC-7 / .github#328
- ADR-0085（PM 优先范式）
- testing.yaml X-04 条目
