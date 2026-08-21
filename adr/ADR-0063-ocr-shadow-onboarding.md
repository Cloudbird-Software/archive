# ADR-0063: OCR shadow 接入——钉版 + 确定性后处理 + post-fix precision 管线

- status: accepted（2026-08-22）
- deciders: 人（owner randypanding）+ AI
- 关联: 宪法 §4C（代码评审基础设施=OCR）/§5（shadow→veto 晋升）、§9#2；
  .github#217（W2-C4）；外部范式：alibaba/open-code-review（Apache-2.0）、
  withmartian/code-review-benchmark（post-fix 方法学，MIT fork）、
  CodeRabbit 免费层（shadow 补充）、AACR-Bench（仅选型参考）、Kodus（B 计划）

## 背景

宪法 §4C 裁定代码评审基础设施采用 OCR（alibaba/open-code-review）：
确定性工程硬约束（文件筛选/打包/规则匹配/定位与反思模块）+ LLM 只做判断，
precision-first 与 veto-only 天然契合。但引入评审器不等于给它执法权——
宪法 §5 要求先 shadow：做出建议但不阻断，用数据证明 precision 达标才可
提议升 veto 关卡。同时外部 LLM 工具的供应链风险（供应链投毒/telemetry
外泄）必须按 §2 security-response 纪律钉死。卡 #217 触发接入。

## 决策

1. **供应链钉版（AC-1）**：OCR 引入=版本+tarball sha256 双锚定；SBOM 落案
   入 archive；telemetry 默认关闭，无法关闭的出口流量经 egress 审计
   （harden-runner 日志）通过——三件套齐才允许进 workflow。
2. **封装形态**：CI-Workflows 提供 reusable workflow 封装（各仓引用不各自
   安装），shadow 模式挂全公开仓 PR。
3. **输出确定性后处理（AC-2）**：OCR 建议必须过三重过滤——file:line 落在
   PR diff 内、命中声明规则集、去重；不过则丢弃并计数。过滤率（丢弃数/
   原始建议数）本身是指标，进 dashboard——评审器质量退化在后处理层可见
   （宪法 §4E"过滤率本身是指标"）。
4. **post-fix precision 管线（AC-3）**：shadow 建议→关联 PR→观察窗口内
   bot 建议被事后修复 commit 命中的比例=precision（withmartian 方法学，
   MIT fork 自建管线）；产出 precision 时序向 §14 阈值累积——晋升判据
   `precision ≥0.8 且 ≥30 例`；AACR-Bench 只作选型参考不作晋升依据
   （厂商自评+AI 辅助标注+泄漏风险，宪法 §4C 明示）。
5. **shadow 期纪律（AC-4）**：OCR 输出零阻断（纯记录）、无 approve 形态、
   不写 PR review state；晋升 veto 另走 ADR + 信任门流程，本 ADR 不授权。
6. **补充与备选**：CodeRabbit 免费层挂全公开仓作高召回 shadow 补充
   （其输出同经后处理）；OCR 不可用时 B 计划=Kodus。

## 后果

- 正面：评审建议有 precision 数字背书，晋升不靠感觉；外部工具供应链
  风险被钉版+SBOM+审计三件套锁住。
- 负面/代价：OCR 低召回是设计取舍（宪法 §10.3 诚实清单——漏报由确定性
  关卡+对抗+holdout 兜底，评审不是安全网）；post-fix 观察窗口使 precision
  有滞后性。
- 风险与缓解：后过滤过猛滤掉真建议 → 过滤率指标可见可归因；shadow 数据
  被污染（人工照 bot 建议修=假命中）→ 命中判定只认非 bot 修复 commit。
- 回滚：shadow 零阻断，删 workflow 即退场；钉版资产与 SBOM 留 archive
  无运行时副作用（新增式可拆）。
