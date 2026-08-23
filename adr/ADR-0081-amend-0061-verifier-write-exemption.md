# ADR-0081: ADR-0061 修订——验证者 APP 合法写豁免通道

- status: accepted（2026-08-23）
- deciders: 人（owner randypanding）+ AI
- 关联: ADR-0061（被修订）、ADR-0076（验证者身份独立）、ADR-0056（holdout 仓）、
  ADR-0068（holdout 揭封 hash 校验）、ADR-0079（spec 阶段攻击面 S1'–S5'）、
  ISSUE-263 spec v5 AC-18 / IFACE-01 / DECISION-01；Cloudbird-Software/.github#270（W1-C3）

## 背景

ADR-0061 确立 g060 锁定机制：验收测试合并后计算 manifest sha256 存
`quality/locks/<card>.json`；非 owner PR 改动锁定路径 → exit 2
（fail-escalate，只人类可解）。唯一合法变更通道是 `Spec-Change: <spec PR#>`
trailer（已合并 spec PR + specVersion 递增）。

ISSUE-263 引入独立验证者 APP（ADR-0076）专责测试/验证路径写操作，但
ADR-0061 原语义未给验证者 APP 任何写豁免——验证者 APP 写的测试文件同样会被
g060 判为非法篡改。本修订在保持 fail-escalate 语义与人类最终裁决的前提下，
为验证者 APP 以“测试作者身份”增加合法写豁免通道。

## 决策

1. **豁免主体**：验证者 APP（由 ADR-0076 定义，本修订生效后方可实施）。身份判定：
   - PR/提交的作者签名与 GitHub App bot 标识一致；
   - App 名/安装 ID 在治理仓 `expected-state.json` 或等效真源中登记为
     `verifier`；
   - 满足 ADR-0076 的时序约束（ADR-0076 合并前不得实施验证者 APP）。

2. **可写路径范围**：验证者 APP 的写豁免**仅**覆盖测试/验证路径：
   - 各仓 `specs/*/suite/**`（spec 级测试设计）；
   - holdout 仓内容（试卷层实体，ADR-0056 DECISION-02 修订后）；
   - 卡级测试文件与验收测试注册项；
   - `quality/locks/<card>.json` 的 CI bot 重算与更新（基于合法
     `Spec-Change` trailer 或验证者 APP 自身发起的测试结构变更）。
   超出上述范围的任何写操作（源码、workflow、治理文件等）不适用本豁免，
   仍按既有规则处理。

3. **豁免条件（与 `Spec-Change` trailer 并列的第二条合法通道）**：
   - 验证者 APP 修改测试路径**必须**与某张已注册卡（card issue）绑定，
     PR body 或提交说明显式引用 `Card: owner/repo#<n>`；
   - 修改内容须属于该卡的测试/验收范围（由卡 AC 列表与 `suite/` 注册清单
     派生）；
   - 改动触发 g060 重算时，新 manifest 须由 CI bot 提交，且提交说明注明
     `Verified-by: verifier-app` 与对应卡号；
   - 不触发 `Spec-Change` trailer 要求——这是专门为测试作者身份保留的
     日常维护通道，但须接受 ADR-0079 红队审计频率（spec/测试设计路径每 PR）。

4. **审计与留痕**：
   - 每次验证者 APP 写测试路径，CI 在 run 日志中记录 App 名、安装 ID、卡号、
     变更路径集、重算前后的 manifest hash；
   - holdout 仓写入须同步更新注册 hash（复用 ADR-0068 揭封机制）；
   - 验证者 APP 的 PR 必须走红队审计（ADR-0079 频率：spec/测试设计路径每 PR），
     `verdict=insufficient` 时机器阻断；
   - 验证者 APP 对自身测试的“自我判卷”冲突由红队/verifier 独立判定；
     验证者 APP 不得单独批准自己的 PR 合并。

5. **与 fail-escalate 的边界**：
   - 人类 owner 仍可通过 CODEOWNERS 批准路径直接修改测试文件，但须走
     `Spec-Change` trailer 或本豁免通道之一；
   - 开发 APP（`cloudbrid-agent`）修改测试路径**不适用**本豁免，仍触发
     exit 2 + 自动开 issue（AC-18）；
   - 验证者 APP 修改非测试路径、或测试路径变更未绑定有效卡、或未走红队审计，
     均按 fail-escalate 处理（exit 2 路由 owner）；
   - 验证者 APP 实施早于 ADR-0076 合并 → 按 ADR-0076 时序约束判红；
     本修订 ADR-0081 合并前，验证者 APP 亦无本豁免（时序断言）。

## 后果

- 正面：验证者 APP 获得合法的日常测试维护写通道，g060 锁定不再误伤独立
  测试作者；ADR-0076 身份分离具备可执行面。
- 负面/代价：验证者 APP 的 PR 同样需走红队审计，增加测试路径变更摩擦；
  需维护 `expected-state.json` 中 verifier App 身份登记。
- 风险与缓解：
  - 验证者 APP 被冒用 → 身份判定依赖 GitHub App bot 签名 + 安装 ID 真源 +
    单仓作用域令牌，三者缺一即 fail；
  - 验证者 APP 越界写源码 → 路径集合显式限定，非测试路径仍 exit 2；
  - 验证者 APP 自我批准 → 合并仍需 owner/红队 survived 判定，验证者 APP
    不持有 approve 豁免。
- 回滚：从治理文件移除验证者 APP 条目、恢复测试路径 CODEOWNERS 为
  owner-only、在 g060 脚本中关闭 verifier 豁免分支即可。

## 验证

- AC-1：ADR-0081 合并后，g060 脚本引用本 ADR 时验证者 APP 的合法写路径有
  明确定义，且与 fail-escalate 语义不冲突（本 ADR 边界条款）。
- AC-2：agent-registry `decisions/` 新增 ADR-0081 墓碑，`INDEX.yaml` 登记
  `content_sha256` 与 archive 正文一致；`python scripts/validate.py` 通过。
- AC-3：治理仓 g060 脚本增加 verifier-app 豁免分支 fixture——验证者 APP
  合法改 `suite/` 通过、开发 APP 改 `suite/` 仍 exit 2。
- AC-4：验证者 APP PR 缺 `Card:` 引用或改非测试路径时，g060 按 fail-escalate
  处理并自动开 issue。
