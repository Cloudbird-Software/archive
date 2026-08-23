# ADR-0075: canary C4/C5 预期勘误——承认双轨 main-protection + SHA/双形态供应链引用

- status: accepted（2026-08-22）
- deciders: 人（owner randypanding）+ AI
- 关联: ADR-0056（canary 仓与泄漏诱饵）、ISSUE-257、Cloudbird-Software/.github#259

## 背景

ADR-0056 设立 canary 仓作为 holdout 试卷的泄漏诱饵与入口断言。canary 连续红（#257）暴露两处预期与 C6 钉扎政策不一致：

1. **C4 供应链入口断言单一形态**：原预期要求所有 `uses:` 引用必须形如 `@vN`。但组织 CI-Workflows 透传存在两种合法形态：语义版本 `@vN` 与 40-hex SHA 加 `ciw-ref` 透传。C6 钉扎政策已承认 SHA 形态，C4 仍按单一形态断言导致误报。
2. **C5 main-protection required checks 单轨**：原预期本地 `main-protection` ruleset 的 required checks 为单轨 `['gate']`。BP-2 观察期引入 org-required-workflows，本地轨与组织轨并存，required checks 实际为 `['gate','org-gate']`。
3. **C6 uses: 正则误匹配**：canary 扫描 `uses:` 时把注释里的 `'uses: pin 同值'` 与脚本字符串也匹配进来，导致全钉扎文件被误报为 INFRA。

## 决策

1. **C4 承认双合法形态**：`uses:` 供应链入口断言接受 `@vN | 40-hex SHA+ciw-ref 透传`。两种形态均视为合规；不强制统一为单一形态。
2. **C5 更新为双轨**：`main-protection` required checks 预期由 `['gate']` 改为 `['gate','org-gate']`。BP-2 观察期结束前保留双轨；退役本地轨需未来新 ADR。
3. **选型倾向 SHA-only**：不变性 + 可审计角度，优先使用 40-hex SHA；但 `@vN` 仍合法，不得因形态差异判红。
4. **C6 uses: 正则排除注释/字符串**：canary 扫描 `uses:` 时排除 YAML 注释与脚本字符串，避免误报。

## 后果

- 正面：canary 误报率下降；C4/C5 预期与 C6 钉扎政策、BP-2 组织轨一致；C6 不再把注释/字符串当真实依赖断言。
- 负面/代价：双轨并存增加 ruleset 复杂度；退役本地轨需额外 ADR；扫描规则需维护注释/字符串排除列表。
- 风险与缓解：形态不统一可能弱化供应链可审计性 → 倾向 SHA-only 并在 canary 报告中标记形态；org-gate 缺失时本地 gate 仍兜底；排除列表遗漏导致漏报 → 纳入周演习（ADR-0069）样本。
- 回滚：恢复 C4 单一 `@vN` 断言与 C5 单轨预期，但会与 C6/BP-2 冲突，除非同步退役 org-gate。
