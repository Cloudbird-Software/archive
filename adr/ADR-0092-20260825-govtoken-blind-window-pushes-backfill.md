# ADR-0092: 2026-08-25 GOVERNANCE_TOKEN 失明窗口直推批次回填

- status: accepted
- date: 2026-08-25
- deciders: owner（建仓/直推事件）/ PM 会话（回填登记）
- resolves: drift-check §8 报警的 3 个非 PR commit（Viral_Radar db02d592、archive be94906f / c1d31e10）按 ADR-0016 附录机制完成回填（本 ADR + .github expected-state.json §8 豁免登记 PR）
- 关联: ADR-0091（Viral_Radar 建仓申报与语言豁免——本 ADR 承接其决策 1 的 bootstrap 定性，不重复申报）；ADR-0089（同日晨间直推回填批次先例）

## 背景

GOVERNANCE_TOKEN 轮换后全量验证（run 32852115897，2026-08-25 13:21Z）浮出 4 条漂移，
均为 token 失明窗口（08-24 05:32 起 30+ 小时）内积累的存量项。其中 GM-4 未申报仓
与语言豁免由 ADR-0091 承接；本 ADR 回填剩余的 §8 直推报警项：

**Viral_Radar 仓（bootstrap 直推，1 笔，(b) 类）**：
- `db02d59268a5006747e04e4cdbba9c52d5852b32`（2026-08-25 13:05Z）"Initial commit"——
  template-service 模板经 GitHub 官方 generate endpoint 实例化落 main（75 文件：
  quality/gates、AGENTS.md、CODEOWNERS、CI-Workflows@v1 引用等），定性见 ADR-0091
  决策 1（官方模板机制，非 agent 直推）；建仓时序上 PR 不可行，且 ADR-0090 后
  org-required-workflows 已有 OrganizationAdmin bypass，空仓首推合法——按 (b) 类
  逐 SHA 登记。

**archive 仓（运行报告直推，2 笔，(a) 类破玻璃）**：
- `c1d31e10e7798e82f1d0de022f58ae15382af1fe` "runs: W35 补记 bypass 基线会话
  （ADR-0090/#369 + 漂移误报清零 #370 + agent-registry 死信清理）"；
- `be94906f09b8e810449be11be63aff8ecf1bdf0f` "runs: W36 #366 第二批收口会话
  （五项高频阻断全清 + CIW 两红清零 + drift 分通道补全）"；
- 均为 PM 会话运行报告直推（append-only 追加，无既有内容改动），未走 PR——
  调查与定性记录于 GOVERNANCE_TOKEN 验证会话运行报告（archive#27）。

## 决策

1. **Viral_Radar bootstrap 豁免登记**：(b) 类（建仓时序豁免），定性援引 ADR-0091
   决策 1；expected-state.json §8 逐完整 SHA 登记。
2. **archive 两笔追认为破玻璃事件**（ADR-0006 语义）：净变更为运行报告追加
   （append-only，非治理规则变更）；回填 = 本 ADR + .github 豁免登记 PR。
3. **教训登记**：运行报告是治理文件面（archive 仓 C1），必须走 PR——本日
   GOVERNANCE_TOKEN 验证会话已立先例（archive#27 走 PR）；直推报告制造了其
   自身报告内容之外的漂移报警，且失明窗口内 §8 报警无人可见，问题被推迟到
   token 恢复后才浮出。

## 后果

- §8：3 个 commit 的后续每日报警（至 2026-09-01 滑出 7 天检测窗口）视为已回填已知项。
- 与 ADR-0088/0089 同为 2026-08-25 直推回填批次；本批 3 笔与晨间批次 4 笔合计
  覆盖该日全部 §8 报警项。
- Viral_Radar 后续治理接入按 template-service 继承面自然运转，无需额外动作。
