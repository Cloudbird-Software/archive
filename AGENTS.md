# AGENTS.md（索引型——append-only 记忆层，只放不可推断的约束）

## 命令

- 迁移保真校验：`python3 scripts/verify_migration.py`（PR/push/weekly 自动跑：`.github/workflows/verify.yml`，INDEX ↔ adr/ ↔ 源 commit 三向 sha256 闭环）

## 硬规则（违反 = PR 打回）

1. 认证：一切 push/PR 用 cloudbrid-agent App 令牌，禁个人 PAT。获取（脚本 pin 到已审阅提交，禁 `curl|bash` 浮动 main 指针，ADR-0021）：
   `GH_TOKEN=$(REPO=archive bash <(curl -sS https://raw.githubusercontent.com/Cloudbird-Software/.github/f72d9520706c8fca974d92456f65cae5c1412bb7/scripts/gh-app-token.sh))`
2. append-only：只增不删不改（含重命名/移动）；历史要修正 = 新增勘误文件，不动原件
3. ADR 正本字节保真（verify_migration.py 强制）；ADR 状态不写在本仓文件——唯一真源 = agent-registry `decisions/INDEX.yaml`；新 ADR 落位流程见 [README.md](README.md) 引 ADR-0053 决策 3
4. 变更一律走 PR（direct_push_exemptions 仅建仓 bootstrap 一次）；一个 PR 一件事，diff < 400 行；提交信息用 Conventional Commits

## 索引（用到再读，不要全读）

| 场景 | 读这个 |
| --- | --- |
| 本仓角色 / 目录落位 / append-only 细则 | [README.md](README.md)（宪法 §1 记忆层） |
| 找某条 ADR | [adr/](adr/)（lifecycle/decision_status 查 agent-registry `decisions/INDEX.yaml`） |
| PM 运行报告 | `runs/`（周度 digest） |
| 退役层快照（agent-registry / agent-platform / agent-tools） | `retired/` |
| 规划回归集 / 评估集 | `evalsets/`（ocr-shadow / trust-shadow / verifier-exam） |
