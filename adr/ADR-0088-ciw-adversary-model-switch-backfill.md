# ADR-0088: CI-Workflows 破玻璃直推回填——adversary 判定模型紧急切换与误置配置清理

- status: accepted
- date: 2026-08-25
- deciders: owner（事件落盘）/ PM 会话（回填登记）
- resolves: drift-check §8 报警的 4 个非 PR commit（766d2c89 / 5f2684f1 / f59ba5f5 / 8f47bcbb）按 ADR-0016 附录机制完成回填（本 ADR + expected-state.json §8 豁免登记 PR）

## 背景

2026-08-25 05:49–05:55Z，org secrets LLM_API_KEY_SENSENOVA / LLM_API_KEY1 相继轮换；adversary 判定链（judge-deep，IR-0004 红队燃料管道运行配置，.github#315）需随之切换到 deepseek-v4-flash。owner 于 06:45–06:51Z 在 CI-Workflows main 直接落盘 4 个 commit（均未经 PR）：

1. `766d2c89a27e05c6afefd1963c6020be361edc23`（06:45）"fix(adversary): switch judge-deep to deepseek-v4-flash (#315)"——首次落盘误将 adversary-config.yaml / models.yaml 放到仓库根目录；
2. `5f2684f1e13d33c5f8e260440794324286603bdf`（06:51）删除误置的根目录 models.yaml；
3. `f59ba5f5eb238349e225393703ba084b0060287b`（06:51）删除误置的根目录 adversary-config.yaml；
4. `8f47bcbb05208e5d376d460c3b6e35913883ba09`（06:51）"fix(adversary): switch judge-deep to deepseek-v4-flash (#315)"——正式修改 pipeline/adversary/adversary-config.yaml 与 pipeline/models.yaml（+26/-26、+30/-30，模型别名切换）。

## 决策

1. 追认该 4 次直推为破玻璃事件（ADR-0006 语义），回填三件套 = 本 ADR + .github expected-state.json §8 豁免登记 PR（同日提交，24h 时限内）。
2. 净变更定性：窗口结束时唯一存活变更 = `pipeline/adversary/` 判定模型配置切换（deepseek-v4-flash）；根目录两文件为误置产物并在同一 6 分钟窗口内自我清理。不涉及治理实质内容变更。
3. 教训登记：运行配置热修同样应走 PR（CI-Workflows PR 流程在案运转，且 org-required-workflows 无 bypass 时 admin 直推是唯一旁路）；确需破玻璃时，落盘后应立即回填登记，不应依赖后续 commit 的"自我清理"掩盖中间态——§8 逐 SHA 执法不看净变更。

## 后果

- §8 对这 4 个 commit 的后续每日报警（至 2026-09-01 滑出 7 天检测窗口）视为已回填已知项，不触发新的处置动作。
- 关联修复：同批 .github PR 一并修复 apply.sh 对 archived（retired）仓的写 FAIL 噪音（ADR-0085 退役仓只读，幂等 apply 应跳过）。
