# ADR-0083: T-14 机器化第一面——spec PR suite 强制门 + 红队 required check 落地修正

- status: accepted（2026-08-24）
- deciders: 人（owner randypanding）+ AI
- 关联: ISSUE-263 spec v5（AC-11）；testing.yaml T-14；ADR-0082（红队守门）；ADR-0079；
  Cloudbird-Software/.github#275（W2-C3）；#263 独立验证报告（2026-08-24）

## 背景

#263（卡绑定测试与红队守门制度）W1-W5 波次宣称完成后，独立验证发现三处机器执法断链：

1. T-14（card_bound_test_required）无任何 PR 级执法载体——spec PR 不带 suite/
   可直接合并（#275 因此保持 OPEN）；specs/ISSUE-263 自身即无 suite/。
2. 落盘 main-protection.json 的 adversary required check 携带非法
   `integration_id: 0`——apply.sh PUT 恒 422，线上 ruleset 从未含 adversary，
   W4-C3「纳入 required checks」实际未生效；且 drift-check §1 因 GOVERNANCE_TOKEN
   失效+jq 对非数组响应报错，未能报出该漂移（检测器失明伪装成漂移噪音）。
3. org-required-workflows 钉点指向 CI-Workflows@2d368c2 的
   .github/workflows/adversary-gate.yml——该文件在钉点 ref 上不存在，required
   workflow 悬空，全 org PR 无 adversary check 产生。

## 决策

1. **T-14 第一面（spec PR suite 强制）**：gate.yml 常驻 job——触及
   `specs/**/spec.md` 或新增 `specs/**/` 目录的 PR，必须含同目录 `suite/`
   （≥1 非空测试文件且含真实断言：assert 语句或 unittest/pytest 结构），
   缺失即 gate 红（合并阻断）。fail-closed：files API 失败视同有 specs 变更。
2. **suite 可执行性证明**：gate 同时真实执行 `specs/*/suite/**`
   （unittest 风格、零第三方依赖），spec 的验收测试不可仅为"存在"。
   后续波次再落 fail-before 逐变更与实现 PR 卡测试解析（T-14 第二面）。
3. **ruleset adversary 条目禁带 integration_id**：required_status_checks
   context 条目只写 `{"context": "adversary"}`；`integration_id: 0` 属非法值
   （曾致 apply 422、线上漂移长期潜伏）。check run 由任意合法身份
   （adversary-gate / check_run_writeback App 令牌 / PAT）产出同名即认。
4. **drift-check §1 fail-closed**：ruleset 清单响应非数组 → FATAL exit 2
   （与 §4 仓库清单同款 loud-failure 契约）——API 失败不得伪装成
   「ruleset 不存在」漂移，也不得静默跳过。
5. **org-required-workflows 钉点修复**：adversary-gate.yml 正本移入
   CI-Workflows（源仓），钉点刷新为含该文件的真实 SHA；.github 仓同名
   workflow 保留（本仓 PR 上下文直跑），语义一致。

## 后果

- 正面：T-14 有了第一道机器阻断；红队 verdict 具备线上合并阻断力；
  drift 检测器失明可被一眼识别（exit 2 vs 漂移清单）。
- 负面/成本：specs/** 新增变更的门槛提高（必须先写 suite）；gate 增加
  一个 job 的分钟数（<1min）。
- 风险与缓解：suite 形同虚设（assert True）由红队审计兜底（S1'/S2' 攻击面
  正是"摆拍 AC/no-op 测试"——IR-E2E 实跑已验证红队可捕获）；回滚=revert
  对应 PR，套件目录不强制删除。

## 验证

- IR-E2E 双腿实跑（kimi k2.7 真调用）：弱套件 verdict=insufficient（Veto）、
  强套件 verdict=survived——证明"suite 存在但摆拍"会被红队层拦截，
  与本 ADR 的 gate 层互补成纵深。
