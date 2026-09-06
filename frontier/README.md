# frontier —— 能力前沿资产（IR-0009 卡 C2；schema=DGA-INCREMENT-PACK 6.4）

- `FRONTIER-SNAPSHOT-vN.yaml`：按模型切换事件版本化（vN+1 必填 deltas_from_previous）——快照序列即前沿漂移史；
- `FRONTIER-EVENTS.jsonl`：漂移事件流（append-only hash 链）：boundary_shift | capability_gain | capability_loss | contract_drift；
- **失败分类字段增量**（verifier-exam 判读协议 v2，自下一校准周期起强制采集；仅不通过时必填）：

```yaml
failure_classification:
  category: 误判真值 | 漏检缺陷 | 过度拒绝 | 判据理解错误 | 领域知识缺口 | 长上下文失效 | 协议/格式错误 | 其他
  confidence_behavior: 高置信错误 | 低置信犹豫 | 无置信输出
  detectability: 自动可检 | 需人工复核 | 不可检
```

三子字段受控枚举，schema 校验器执法（非法枚举必须被拒）；分类数据回流 FRONTIER 快照与 T-04 失败模式分布映射。
**待办（卡 C2 门禁）**：快照 v1 从原始事件流重放一致——重放器挂下一校准周期收口（owner 抽查时一并验收）。
