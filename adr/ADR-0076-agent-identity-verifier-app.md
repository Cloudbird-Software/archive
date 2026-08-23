# ADR-0076: AG-1 修订——开发身份唯一与验证者身份独立

- status: accepted（2026-08-23）
- deciders: 人（owner randypanding）+ AI
- 关联: 宪法 §4D（AGENTS.md 索引型）、§6（缺席即停）、§11（入口协议）；
  ISSUE-263 spec v5 DECISION-01 / IFACE-01；
  前置：ADR-0053（archive 迁移与墓碑索引）、ADR-0056（holdout 仓与泄漏诱饵）、
  ADR-0061（测试产物拓扑与 g060）、ADR-0068（holdout 揭封 hash 校验）。

## 背景

AG-1 当前表述为“agent 写仓库唯一身份 = App(cloudbrid-agent)”。ISSUE-263
在卡绑定测试与红队守门制度中识别到：开发 agent 同时承担“实现代码”与
“写测试/验收标准”两个角色时，存在自我出题、自我判卷的同义反复风险
（fake_tests 属于组织风险 posture 前三项）。红队审计与 verifier 机制要求
测试相关内容（suite/、holdout 试卷、卡级测试）必须由与开发身份独立的
主体负责，才能构成可信的 fail-before 与 holdout 揭封链路。

因此 AG-1 需要由“单一身份”修订为“开发身份唯一 + 验证者身份独立”：
开发动作仍只由 `cloudbrid-agent` 执行；测试/验证路径的写权归新设
验证者 APP，开发 agent 对测试路径的修改将被拒绝并触发结构化上报。

## 决策

1. **AG-1 修订**：组织内 agent 写仓库的开发身份保持唯一，仍为
   GitHub App `cloudbrid-agent`；同时新设独立的“验证者 APP”，专责
   测试/验证相关路径的写操作。

2. **开发身份边界（cloudbrid-agent）**：
   - 单仓作用域、1h 过期、磁盘不落长期凭据（AG-2 不变）；
   - 权限维持 contents/issues/PRs:write，**不得**新增测试路径写豁免；
   - 对 `suite/`、`holdout`、卡测试文件等测试/验证路径的写操作，
     由 g060 关卡与 CODEOWNERS 机制拒绝（exit 2 并开 issue 路由 owner）。

3. **验证者 APP 身份边界**：
   - 新设独立 GitHub App（本 ADR 仅做身份面定义，APP 实体安装与
     凭据分发在 ADR-0076 合并后按 IR 实施）；
   - 单仓作用域、1h 过期，与 cloudbrid-agent 使用同一套
     `scripts/gh-app-token.sh` 签发逻辑；
   - 写权**仅**覆盖测试/验证路径：
     - 各仓 `specs/*/suite/**`（spec 级测试设计）；
     - holdout 仓内容（试卷层实体，ADR-0056 DECISION-02 后续修订）；
     - 卡级测试与验收测试注册项；
   - **不得**持有 workflows/administration/organization_projects/members
     等管理权限；与 cloudbrid-agent 的权限集合不相交于非测试路径。

4. **CODEOWNERS 与 g060 语义扩展**：
   - 测试相关路径的 CODEOWNERS = 验证者 APP + 人类 owner；
   - g060 语义由 ADR-0061 扩展至 `specs/*/suite/**` 等 IR 分片测试路径，
     非验证者 APP/owner 修改时 exit 2 并自动开 issue；
   - ADR-0061 的同步修订为验证者 APP 定义合法写豁免通道（该修订合并前
     验证者 APP 无写豁免）。

5. **holdout 仓挂载**：
   - 验证者 APP 可挂载 holdout 仓，作为试卷层写入主体；
   - holdout 注册主体为验证者 APP，机器校验 PR 引用的 holdout hash
     与已注册记录一致（复用 ADR-0068 揭封 hash 校验机制，仅新增身份面）；
   - 非验证者 APP 写入 holdout 内容被拒（覆盖跨仓场景）。

6. **时序约束（本 ADR 合并前不得实施）**：
   - **AG-1 修订 ADR（即本 ADR）未合并前，任何验证者 APP 实施证据
     （安装记录、凭据分发、测试路径写入、CODEOWNERS 中验证者 APP
     条目生效等）出现即判红**；
   - 验证者 APP 的安装、凭据配置、workflow 调用迁移必须在 ADR-0076
     合并之后按单独的实施卡逐步落地；
   - 漂移检测与 governance-drift 将本约束纳入 drift-check §18 断言
     随 ADR-0056 DECISION-02 修订同步更新。

7. **开发 agent 发现测试/AC 错误的上报通道**：
   - 开发 agent 发现验收测试或 AC 语义有误时，不得自行修改测试文件，
     须通过结构化 issue 上报（引用 test/AC 编号）路由 owner；
   - TTL 内 owner 裁决，裁决前暂停该卡相关合并；
   - 这是“发现错误”的合法上报通道，与防篡改阻断互补。

## 后果

- 正面：开发/验证身份分离，切断 agent“自我出题-自我判卷”循环；
  测试路径写权由独立 APP 持有，红队守门与 verifier 机制具备可信执行面；
  holdout 试卷层写入主体明确，ADR-0068 hash 校验链路完整。
- 负面/代价：组织需多维护一个 GitHub App；每次测试路径 PR 需要
  验证者 APP 或 owner 参与，可能增加 short-term 延迟；
  g060 与 CODEOWNERS 的扩展需要一次 ADR-0061 同步修订。
- 风险与缓解：
  - 验证者 APP 权限过宽 → 本 ADR 明确限定为“仅测试/验证路径写权”，
    由 drift-check 对 App 权限与 CODEOWNERS 做 hourly 对账；
  - 验证者 APP 与开发 APP 共用签发脚本导致身份混淆 →
    `gh-app-token.sh` 输出显式标注 App 名与安装 ID，调用方必须
    显式指定 `APP=verifier-<name>`；
  - 验证者 APP 实施早于 ADR 合并 → 由 drift-check §18 与 governance-drift
    的负向断言判红，并自动开 issue。
- 回滚：移除验证者 APP 安装、恢复测试路径 CODEOWNERS 为 owner-only、
  在 GOVERNANCE.yaml 将 AG-1 回写为单一 cloudbrid-agent 身份即可。

## 验证

- AC-1：agent-registry `decisions/` 新增 ADR-0076 墓碑，`INDEX.yaml`
  登记 content_sha256 与 archive 正文一致；`python scripts/validate.py`
  通过。
- AC-2：.github 治理仓 `governance/GOVERNANCE.yaml` AG-1 intent 更新为
  “开发身份唯一（cloudbrid-agent）+ 验证者身份独立（新设验证者 APP，
  仅测试/验证路径写权）”，`make gates-pr` 通过。
- AC-3：ADR-0076 正文包含时序约束——AG-1 修订 ADR 合并前出现验证者 APP
  实施证据即判红。
- AC-4（后续实施卡）：开发 APP 改 `suite/` 路径触发 exit 2 + 自动开 issue；
  验证者 APP 查询记录显示其权限范围仅含测试/验证路径。
