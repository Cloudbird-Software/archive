# ADR-0119: 撤销 GOVERNANCE EX-1 并退役 cnb-bridge 免费算力桥接

- status: accepted
- deciders: owner randypanding (2026-09-10 批准), CEO Agent (执行)
- 关联: ADR-0085（PM 优先范式转变——退役多 agent 编排层）、ADR-0103（治理总纲吸收——三面分离）、DGA-human-v1.1 §2.1/§3.1/§3.6/§5.7、DGA-A-v1.0 §3 A-10、cnb-bridge/REMOVAL.md

## 背景

治理体系正在向 DGA（可判定治理架构）理论整体迁移（执行方案见 `plans/2026-09-14-github-governance-rebuild.md`）。在此背景下，CNB 免费算力桥接（GOVERNANCE EX-1）被识别为**可删除层**：

1. 六元组闭环单元（DGA-human-v1.1 §2.1）要求 Intent/Context/Capability/Action/Evidence/Accountability 齐备；CNB 桥接仅覆盖 Capability/Action 两层，且 Evidence/Accountability 未纳入治理 schema。
2. 判定锚点不外置原则（§3.6 + 宪法 §14c）要求核心治理闭环永远内化；EX-1 作为云内网池与 CNB 的可删除层，其判定语义已随 ADR-0103 明确为"删除后不变"。
3. cnb-bridge REMOVAL.md 文档化：该仓从立项起就是可删除层，删除后 gate/org-gate/conductor 语义不变。

董事长于 2026-09-10 批准撤销 EX-1（CNB 免费算力桥接例外），本 ADR 记录该决策并执行 Phase 3 本地变更。

## 决定

### 1. 退役快照（先快照后删除，回退铁律）

删除前完成全量快照至 `archive/retired/ex-1-cnb-bridge-20260910/`，内含：

- `cnb-bridge/`：`_repos/cnb-bridge/` 整仓拷贝（排除 `.git`），保留 `REMOVAL.md`、`AGENTS.md`、`accounts.yaml`、`cnb_pool.py`、`selfcloud/`、`tests/` 等全部文件
- `dotgithub/workflows/cnb-dispatch.yml`、`dotgithub/workflows/cnb-audit.yml`：来自 `_repos/.github/.github/workflows/`
- `dotgithub/governance/GOVERNANCE.yaml`、`dotgithub/governance/providers.yaml`：整文件拷贝
- `governance-policy/automation-limits.yaml`：来自 `_repos/.github/governance/policy/automation-limits.yaml`（含 `# ---- CNB 免费算力池参数` 节）
- `README.md`：说明快照来源、时间、对应 ADR-0119

快照 sha256 与源文件比对一致（文件数 33 + 抽 3 文件校验通过）。

### 2. 三接缝拆除（.github 仓，分支 governance/dga-rebuild-phase12）

- 删除 `.github/workflows/cnb-dispatch.yml`、`.github/workflows/cnb-audit.yml`
- 从 `governance/GOVERNANCE.yaml` 删除 EX-1 条目本体（保持 YAML 合法）
- 从 `governance/policy/automation-limits.yaml` 删除 `# ---- CNB 免费算力池参数` 起的 CNB 配置节
- `governance/providers.yaml` 的 `self-cloud-pool` 条目**不删**，改注记为退役状态（条目属资产申报，REMOVAL §selfcloud 步骤 4）

### 3. 治理平面残留引用清理

grep 治理平面（`governance/`、`.github/workflows/`、`scripts/`、`expected-state.json`）中以下路径残留 **有治理语义的引用** 需清理：

- `_repos/.github/governance/expected-state.json`：`org_secrets_required` 中的 `CNB_TOKEN_XUEMEI`、`CNB_TOKEN_P11`
- `_repos/.github/governance/expected-state.json`：`github_app.repositories` 中的 `cnb-bridge`
- `_repos/.github/governance/expected-state.json`：`verifier_app.repositories` 中的 `cnb-bridge`
- `_repos/.github/governance/providers.yaml`：`cnb-pool` 条目本体（REMOVAL.md 步骤 2 要求删除 accounts.yaml 与 HMAC 密钥；providers.yaml 的 `cnb-pool` 条目作为操作性引用一并退役）
- `_repos/.github/AGENTS.md`：`docs/pm/PLAYBOOK.md` 行提及 "CNB 池运维：cnb-bridge 仓"（导航性提及，保留但需在报告中列出）

**不动**：纯历史叙述（docs/、ADR 引用、`cnb-public-mirror.yml`、`cnb-stronghold-probe.yml`——两者属 CNB 私有阵地 stronghold，非免费算力桥接，需单独评估）。

### 4. 本地 cnb-bridge 仓删除

快照校验通过后删除 `_repos/cnb-bridge/`。

## 依据

- cnb-bridge REMOVAL.md：执行清单（步骤 1–5 + §selfcloud 步骤 1–5）
- ADR-0085：退役多 agent 编排层断言（删除后 gate/org-gate/conductor 语义不变）
- ADR-0103：三面分离架构（判定锚点不外置）
- DGA-human-v1.1 §3.6：判定锚点永远内化
- 执行方案 `plans/2026-09-14-github-governance-rebuild.md` §e 2.4 六动作、§f 验收 F-3/F-4/F-5/F-12

## 后果

- **正面**：治理平面删除 5 处操作性引用（2 工作流 + 1 条目 + 1 配置节 + 1 providers 条目），gate/org-gate/conductor 判定语义不变；工作区无歧义残留。
- **负面**：常规开发卡默认执行者需回退付费 API 或申请新常驻机器（CNB 免费算力池退役）。
- **缓解**：退役文件全部快照进 archive/retired/，可追溯；CNB 私有阵地 stronghold（ADR-0108）不受影响，其工作流 `cnb-public-mirror.yml`、`cnb-stronghold-probe.yml` 保留。

## 回退

从 `archive/retired/ex-1-cnb-bridge-20260910/` 快照恢复对应文件到原位即可；GOVERNANCE.yaml / providers.yaml / automation-limits.yaml 按需恢复相关条目。
