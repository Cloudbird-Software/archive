# ADR-0080: ADR-0056 DECISION-02 修订——验证者 APP 挂载 holdout + 仅测试/验证路径写权

- status: accepted（2026-08-23）
- deciders: 人（owner randypanding）+ AI
- 关联: ADR-0056（被修订）、ADR-0076（AG-1 修订——开发身份唯一与验证者身份独立）、
  ISSUE-263 spec v5 DECISION-01 / IFACE-01 / AC-17 / AC-18 / AC-19、
  Cloudbird-Software/.github#269

## 背景

ADR-0056 DECISION-02 将 holdout 仓的隔离不变量定义为「cloudbrid-agent App
严禁挂载」——读隔离靠 App 安装差异，不靠仓库保密。ISSUE-263 在卡绑定测试与
红队守门制度中进一步识别到：holdout 试卷层的注册、揭封与写入主体必须与
开发身份分离，否则开发 agent 仍可能参与「自我出题-自我判卷」。

ADR-0076 因此将 AG-1 修订为「开发身份唯一（cloudbrid-agent）+ 验证者身份独立
（验证者 APP）」，并明确验证者 APP 可挂载 holdout 仓。但 ADR-0076 本身不做
DECISION-02 隔离不变量的文本修订；该修订由本 ADR-0080 完成。

**时序证据（AC-2）**：在本修订合并前，旧的 drift-check §18 把「任何 App 挂载
holdout」都视为隔离失效。若当时验证者 APP 已存在并挂载 holdout，旧 §18 会
报 P0 漂移；因此 ADR-0076 才在时序约束中要求「AG-1 修订 ADR 合并前不得实施
验证者 APP」。本 ADR 合并后，这一时序约束解除，验证者 APP 挂载 holdout 成为
合法状态。

## 决策

1. **DECISION-02 隔离不变量修订**：
   - `Cloudbird-Software/holdout` 仓对 **cloudbrid-agent App** 保持禁止挂载；
   - 对 **验证者 APP** 开放挂载，但验证者 APP 的写权**仅**覆盖测试/验证路径：
     - holdout 仓内容（entries/、schema/、canary/）；
     - 各仓 `specs/*/suite/**`（spec 级测试设计）；
     - 卡级测试与验收测试注册项。
   - 验证者 APP **不得**持有 workflows/administration/organization_projects/members
     等管理权限；与 cloudbrid-agent 的权限集合在非测试路径上不相交。

2. **drift-check §18 断言同步**：
   - cloudbrid-agent App 的 installation 仓清单含 `holdout` → **P0 漂移**；
   - 验证者 APP 的 installation 仓清单含 `holdout` → **OK（合法）**；
   - 验证者 APP 尚未安装 → INFO/SKIP，不判漂移（实施阶段再断言）；
   - 正向对照（防失明）仍要求 cloudbrid-agent 的 installation 清单非空且含
     `.github`；验证者 APP 安装后若清单非空即可判定。

3. **REPOS.yaml holdout 角色注记同步**：将 `App 不挂载` 改为
   `cloudbrid-agent 严禁挂载；验证者 APP 可挂载并仅用于测试/验证路径写权`，
   并引用 ADR-0080。

4. **时序约束（与 ADR-0076 保持一致）**：
   - 本 ADR 合并前，任何验证者 APP 实施证据（安装记录、凭据分发、holdout
     内容写入、CODEOWNERS 中验证者 APP 条目生效等）出现即判红；
   - 验证者 APP 的安装、凭据配置、workflow 调用迁移必须在本 ADR 合并之后
     按单独的实施卡逐步落地；
   - drift-check §18 与 governance-drift 将本约束作为负向断言纳入。

## 后果

- 正面：holdout 试卷层写入主体明确为验证者 APP，与 ADR-0068 揭封 hash 校验
  链路、AC-17 卡绑定测试注册、AC-18 g060/CODEOWNERS 防线形成完整闭环；
  开发/验证身份分离，切断 agent「自我出题-自我判卷」循环。
- 负面/代价：drift-check §18 需同时关注 cloudbrid-agent 与验证者 APP 两个
  installation；多维护一个 GitHub App 的对账项。
- 风险与缓解：
  - 验证者 APP 权限过宽 → 本 ADR 限定为「仅测试/验证路径写权」，由
    drift-check 对 App 权限与 CODEOWNERS 做 hourly 对账；
  - cloudbrid-agent 借验证者 APP 身份写 holdout → `gh-app-token.sh` 输出显式
    标注 App 名与安装 ID，调用方必须显式指定 `APP=verifier-<name>`；
  - 验证者 APP 实施早于本 ADR 合并 → drift-check §18 负向断言判红并自动开
    issue。
- 回滚：恢复 ADR-0056 原 DECISION-02「App 不挂载」表述；从
  `expected-state.json` 移除 `verifier_app` 块；卸载验证者 APP 对 holdout 的
  访问。

## 验证

- AC-1：drift-check §18 运行时，cloudbrid-agent 挂载 holdout 报 P0 漂移，
  验证者 APP 挂载 holdout 不报漂移。
- AC-2：本 ADR 正文包含修订前时序断言——旧 §18 会把验证者 APP 挂载 holdout
  判为漂移。
- AC-3：`agent-registry` 运行 `python scripts/validate.py` 通过；
  `.github` 运行 `make gates-pr` 通过。
