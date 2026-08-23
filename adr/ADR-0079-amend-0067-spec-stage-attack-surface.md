# ADR-0079: ADR-0067 修订——spec 阶段攻击面 S1'–S5' + 每 PR 频率

- status: accepted（2026-08-23）
- deciders: 人（owner randypanding）+ AI
- 关联: ADR-0067（被修订）、ISSUE-263 DECISION-04、Cloudbird-Software/.github#271（W1-C4）、宪法 §4E/§4C、spec AC-5/AC-16

## 背景

ADR-0067 将"恶意合规 adversary"攻击面定义为代码实现层的五类漏洞（硬编码期望、测试特例分支、no-op 桩、永久缓存、忽略错误路径），在实现 PR 阶段判定"套件不充分"（insufficient）并阻塞合并。ISSUE-263 将红队守门范围从实现 PR 上移到"意图→spec→测试设计"路径，因此攻击面必须面向文本工件重定义。

#263 五轮 dogfood 报告（R1–R5，评论链红队报告）反复暴露两类核心问题：

- **AC 可摆拍性**：spec/AC 写得像验收标准，实则缺少可机械核对的证据锚点，实现可通过"形式上满足、实质上背叛意图"的偷懒方式通过。
- **IR 保真度丢失**：`irRef`、`blastRadius`、`specVersion` 与运行时刻工件或 issue 时间线不一致，导致红队/verifier 报告的证据链失真。

DECISION-04 要求将 ADR-0067 的攻击面面向文本工件重定义，并随本修订案一并落文。

## 决策

1. **攻击面重定义（S1'–S5'）**：原 ADR-0067 的 S1–S5 针对代码实现；本修订将其映射为文本工件/设计阶段的攻击面 S1'–S5'，并新增 **IR 保真度核对**维度。红队审计 spec/测试设计路径 PR 时按以下清单检查，版本随本 ADR 落文：
   - **S1' 硬编码期望 / AC 可摆拍性**：AC 使用可被具体实现"摆拍"满足的描述，缺少不变量、机械核对或外部可观测谓词。例如仅断言"日志存在"而未要求"由独立采集组件写入、与 endpoint usage 字段交叉核对、基准版本在 run 开始时动态获取"。
   - **S2' 测试特例分支 / 路径覆盖缺失**：spec 或测试设计只覆盖 happy path，对异常、边界、负向路径无断言；实现可通过为特定用例写特例分支而非通用方案来通过验收。
   - **S3' no-op 桩 / 空洞测试**：测试文件存在但断言弱或无效（如恒真断言、未调用被测代码）；或 spec 声称引入某机制（如 llm-verifier / 机械核对）但没有可执行的验收路径。
   - **S4' 永久缓存 / 状态污染**：spec 未界定缓存、fixture、状态生命周期；测试间共享可变状态，或 IR 记录引用的工件版本（SHA、抓取时间）与运行时刻真实工件不一致，导致结果不可复现。
   - **S5' 忽略错误路径 / 失效降级缺失**：spec 对 LLM 不可用、endpoint 探测失败、核对脚本崩溃、配置面枚举失败、无 verdict 等失败路径未定义 fail-closed 行为；或 `no-attempts`/空报告/白卷被误当作 `survived` 放行。

2. **IR 保真度核对**：除 S1'–S5' 外，spec 阶段的 redteam 报告必须对以下 IR 元数据做机械核对：
   - `irRef` 与 issue 编号、标题、状态是否一致；
   - `specVersion` 与当前评审的 spec 文件版本是否一致；
   - `blastRadius` 声明的 `repo:path` 集合与 PR diff 实际变更路径是否一致；
   - 任何引用被核对作废时，该条命中强制转 `insufficient`（作废是判定，不是记录）。

3. **判定语义不变**：保留 ADR-0067 三值语义：
   - `verdict=insufficient` → 机器阻断，状态转 `needs-human`，必须修复并重新审计；
   - `verdict=survived` → 放行，但报告必须含 ≥1 条带证据引用的攻击尝试记录（防白卷/恒绿 prompt）；
   - `verdict=no-attempts` / 空报告 / 白卷 → infra 失败，有界重试 ≤2 次后转 `needs-human` 并自动开 issue。
   红队不持有写权限；人类 owner 可按 `needs-human` 复核通道裁决。

4. **频率修订**：红队审计从"spec PR 阶段 + 波次收口"改为"意图→spec→测试设计路径的每个 PR"。具体由路径集合确定性派生：
   - `specs/**` 实质内容变更 → 必须走红队审计；
   - `suite/`、`testing.yaml`、测试设计相关路径变更 → 必须走红队审计；
   - 纯实现代码路径 PR 不强制红队审计（保留 DECISION-02 豁免），但须跑卡绑定测试与 holdout。
   漏配/被摘除/被跳过 adversary check 时 CI 必须红（负向断言）。

5. **意图探索 S6–S8（requires_explore）**：S6–S8 不进入 `insufficient`/`survived` 判定，仅作为意图层道闸，命中后带证据报人裁决：
   - **S6 重复已有功能**：spec 意图与现有功能/ADR/机制重复，但未显式引用或说明差异；
   - **S7 违反治理约束**：spec 与 `GOVERNANCE.yaml`、`transitions.yaml`、`REPOS.yaml` 等治理文件冲突；
   - **S8 blastRadius 集合比对**：spec 声明的 `blastRadius` 与实际 PR diff / 历史 issue 时间线不一致（确定性脚本，可脱离 LLM 运行；脚本崩溃或两次运行结果不一致时该次 S8 判定作废）。
   S6–S8 在 `attack-strategies.yaml` 中标记 `requires_explore: true`；每次 run 须产出"本轮是否发现 S6–S8"字段，无命中须落盘"无命中"记录。

6. **攻击策略与素材**：`attack-strategies.yaml` 引用本 ADR 作为 spec 阶段攻击面的 normative 定义；#263 dogfood 报告 R1–R5 作为首批素材存档，红队审计时可复用其中的摆拍模式与 IR 失真案例。

## 后果

- 正面：spec/测试设计阶段即可捕获"AC 可摆拍"与"IR 失真"，避免将质量债务带到实现阶段；攻击面清单从代码层扩展到文本层，与 ISSUE-263 守门范围对齐。
- 负面/代价：spec 路径 PR 每次都要走红队审计，judge-deep 档调用频率上升；LLM 对文本工件的判定可能比代码层更主观，误报率略高。
- 风险与缓解：
  - 人类 owner 可能因疲劳而误点放行 → `needs-human` 裁决必须留判例，且机械核对（IR 保真度、证据引用）为必要输入；
  - adversary prompt 弱化 → 保持 prompt 版本锁定 + 周演习（ADR-0069）注入弱 spec 样本；
  - S6–S8 误判为阻断 → 明确标记 `requires_explore`，只报人不阻断。
- 回滚：可将本 ADR 从 required ADR 引用清单中摘除，红队审计退回到 ADR-0067 原范围（仅实现 PR / 波次收口）。
