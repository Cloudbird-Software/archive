# 退役快照：EX-1 CNB 免费算力桥接（2026-09-10）

> 来源：董事长 2026-09-10 批准撤销 GOVERNANCE EX-1（CNB 免费算力桥接例外）
> 执行：ADR-0119 Phase 3 本地变更
> 时间：2026-09-10

## 快照内容

- `cnb-bridge/`：`_repos/cnb-bridge/` 整仓拷贝（已排除 `.git`），含 `REMOVAL.md`、`AGENTS.md`、`accounts.yaml`、`cnb_pool.py`、`selfcloud/`、`tests/` 等全部文件
- `dotgithub/workflows/cnb-dispatch.yml`：来自 `_repos/.github/.github/workflows/cnb-dispatch.yml`
- `dotgithub/workflows/cnb-audit.yml`：来自 `_repos/.github/.github/workflows/cnb-audit.yml`
- `dotgithub/governance/GOVERNANCE.yaml`：来自 `_repos/.github/governance/GOVERNANCE.yaml`（含 EX-1 条目本体）
- `dotgithub/governance/providers.yaml`：来自 `_repos/.github/governance/providers.yaml`（含 `self-cloud-pool` 条目）
- `governance-policy/automation-limits.yaml`：来自 `_repos/.github/governance/policy/automation-limits.yaml`（含 `# ---- CNB 免费算力池参数` 节）

## 对应决策

- **ADR-0119**：治理体系 DGA 重构与旧声明层退役（status: accepted, date: 2026-09-10）
- **执行方案**：`plans/2026-09-14-github-governance-rebuild.md` §b 退役条目 13–18、§e 2.4、§f 验收 F-3/F-4/F-5/F-12

## 回退说明

若需回退 EX-1 撤销，从本快照恢复对应文件到原位即可：
1. `cnb-bridge/` 整仓复制回 `_repos/cnb-bridge/`
2. 两工作流复制回 `_repos/.github/.github/workflows/`
3. GOVERNANCE.yaml / providers.yaml / automation-limits.yaml 按需恢复相关条目

> archive 仓 append-only：本快照只增不删不改历史。
