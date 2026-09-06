# neg-results —— 负结果库（IR-0009 卡 C1；schema=DGA-INCREMENT-PACK 6.3）

条目五元组：**已验证不可行 + 原因 + 当时的能力版本 + 当时的环境条件 + 过期条件**（STRAT §7.2）。
负结果绑定能力版本——能力前沿外移使旧负结果复活。

## 文件

```
NEG-xxxx.yaml     条目（五元组+hash 链字段）
LEDGER.jsonl      append-only 台账（id/文件/entry_hash/prev_hash/时间戳）
new_entry.py      登记脚本（fail-closed：字段缺失/枚举非法/链不连续=exit 1）
verify.py         链校验（链断=红）
neg-scan.py       复活钩子扫描（遍历 active 条目，trigger_events 命中→候选清单+evidence 落行）
.github/workflows/neg-scan.yml   周期扫描（weekly cron + workflow_dispatch 模拟切换）
```

## 诚实标注（v1 纪律）

predicates 为自然语言谓词——v1 的复活判定为**半自动**：钩子只做 trigger_events 匹配并产出候选清单，
谓词评估由 owner/下轮扫描人工完成。谓词结构化（可执行表达式）为 v2 演进方向，不入门禁。

复活钩子挂接说明：组织现无独立的"模型切换工作流"（切换=ADR 事件+org var 变更，ADR-0088/0104 先例），
故钩子以周期扫描形态挂接（neg-scan.yml weekly），模型切换后可手动 dispatch 立即扫描——语义等价，
偏差已登记（卡 C1 门禁"模拟切换产生非空输出"由 dispatch 演练承载）。
