# runs/ —— PM 运行报告（ADR-0085 决策 8）

每次 run（一场 PM 会话/一张卡/一个 IR 的收口）结束后，PM 向本周文件
`runs/YYYY-WNN.md` **追加**一节报告。一周一文件，append-only（只增不改；
纠错追加 erratum 行）。

## 格式（固定三节，缺节即不合格）

```markdown
---
### <run-id> · <日期> · <PM 标识（模型/会话名）>
scope: [IR-XXXX, #issue, ...]

**事实** ——做了什么、数据、卡点（客观陈述，可被引用核对）
**体感** ——哪里不顺：门禁/文档/工具/流程（明确标注主观）
**改进点** ——每条一行，机械可抽取：
[followup] playbook: <描述>
[followup] policy: <描述>
[followup] gate: <描述>
[followup] tool: <描述>
```

## 闭环（两个机械件，其余靠约定）

1. **写**：PM 自律（PLAYBOOK §4）——收口即写，防遗忘锚点=卡 state:done 前。
2. **聚**：`runs-digest.yml` 周一 04:37 UTC 抽取上周全部 `[followup]` 行 +
   报告摘要，自动开 digest issue（.github 仓）。
3. **消费**：owner 读 digest 逐条处置——转卡 / 转 IR / 否决关掉（留痕）；
   下一个 PM 冷启动必读最近 4 周（PLAYBOOK 入职第三步）。

## 定位（铁律）

- 报告是**经验输入与改进燃料，不是验收证据**——自述不可核实
  （standards/agent event.schema 既有原则的延续，见 ADR-0085 决策 8）。
- 不作为任何 gate 的判定输入；改进落地必须走 IR/卡（过门禁），不得凭报告
  直接改治理。
- `[followup]` 行是唯一机械抓手：一行一提案，不改治理、只登记意向。
