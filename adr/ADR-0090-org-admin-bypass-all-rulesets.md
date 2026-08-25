# ADR-0090: 全 ruleset 统一 org admin bypass 基线 + 漂移监控不变量

- status: accepted（2026-08-25）
- deciders: 人（owner randypanding，直接指令）+ AI（PM 会话，GLM-5.3）
- 关联: ADR-0046（org-required-workflows 钉点——其"无 bypass"设计面被本 ADR 修订）；
  ADR-0010（admin 全系统唯 owner——bypass 安全性的前提不变量）；
  ADR-0016/0017（破玻璃直推与回填机制——bypass 后直推的监控网）；
  ADR-0053/0084/0085（archive/QW_Arena1/cnb-bridge 空仓 bootstrap 死锁先例，
  见 .github 仓 expected-state.json#direct_push_exemptions 登记）；
  ADR-0083（ruleset 平台约束修订——required workflows ref 只接受分支名）

## 背景

组织四个 ruleset 中三个（main-protection / release-tags / codeql-gate）已声明
OrganizationAdmin bypass_mode=always，唯 org-required-workflows 例外——ADR-0046
设计为无 bypass（required workflow 审判不可绕）。该例外造成实际运营摩擦：

- 空仓 bootstrap 死锁：空仓无 base 分支、PR 不可行，required workflow 拦截首推。
  archive（.github#164）、QW_Arena1（.github#345）、cnb-bridge（ADR-0085）三次
  建仓均需变通（对 org ruleset 做秒级临时 exclude / 绕道 contents API），操作
  复杂、全程留痕负担重，且每次都要逐 SHA 登记豁免。
- 基线分裂：同为组织 ruleset，bypass 政策不一致——每新增 ruleset 都要重新
  裁决一次"要不要 bypass"，无机械判据。

owner 裁决（2026-08-25 直接指令）：所有 ruleset 必须有 org admin 可以 bypass，
并按此建立飘移监控基线。

## 决策

1. **全部组织 ruleset 声明 OrganizationAdmin bypass_mode=always**：
   org-required-workflows 补齐声明（本 ADR 的落地件，合并后跑
   `bash governance/apply.sh` 生效）；其余三个已然如此，不动。
2. **飘移监控基线 = drift-check §1 不变量**：§1 既有"落盘文件 ↔ 线上定义"
   逐字段 diff（已含 bypass_actors）之外，新增组织基线断言——每个
   rulesets/*.json 必须声明 OrganizationAdmin/always bypass，缺失即红。
   理由：逐份对账守不住"文件与线上同时摘除"的侵蚀路径（改文件 + 跑 apply
   即可无声去除 bypass，diff 两边一致不报）；不变量把"所有 ruleset 必须
   org admin 可 bypass"从一次性事实变成机械执法面（INV-01/02：判定锚点
   机械）。新 ruleset 文件落地即受检，无需另开卡。
3. **bypass 是已声明、被监控的通道，不是盲区**：admin 绕过 ruleset 的可见
   滥用面均有既有检测网——§8 直推检测（非 PR commit 24h 内检出，豁免须
   逐 SHA + ADR 登记）、§11 CI-Workflows 大版本指针完整性（release-tags
   bypass 强移指针 24h 内检出）、§12 required check 活体存在性。
4. **空仓 bootstrap 路径简化**：bypass 后空仓首推不再死锁——admin 直推
   首属合法路径，仍走 §8 (b) 类豁免登记（ADR-0021 建仓时序豁免，逐 SHA）；
   历史变通操作（临时 exclude 等）不再需要，既有登记保留为历史事实。

## 后果

- 正：四 ruleset bypass 基线统一；空仓 bootstrap 死锁消除；bypass 政策
  机械化执法（摘除任何 ruleset 的 admin bypass 即 §1 红）。
- 负：org admin 可绕过 org-gate/adversary-gate 审判直推 main。接受理由：
  ADR-0010 admin 唯一且为 owner（人的信任锚）；§8 直推检测兜底（24h 检出 +
  豁免须 ADR 背书）；与 main-protection/release-tags 既有 bypass 同权，
  未扩大新的攻击面。
- 中性：未来新增第五个 ruleset 时，其文件须同时声明 bypass，否则 §1
  不变量红；expected-state.json 中"org-required-workflows 无 bypass"的
  历史注释随本 ADR 更新为现状描述。
- 证据面：本 ADR + .github 仓 rulesets/org-required-workflows.json diff +
  drift-check §1 不变量 diff + apply 后 drift-check §1 对 org-required-workflows
  输出 OK（bypass_actors 两侧行为 null/OrganizationAdmin/always）。
