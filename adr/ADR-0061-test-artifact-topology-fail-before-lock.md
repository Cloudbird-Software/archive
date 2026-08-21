# ADR-0061: 测试产物拓扑——fail-before + lock-tests + g060 + Makefile 三命令

- status: accepted（2026-08-22）
- deciders: 人（owner randypanding）+ AI
- 关联: 宪法 §4A（测试先行+哈希锁定）/§4E（卡级 test-first 产物拓扑）、
  .github#215（W2-C2）、spec v3 INV-03；W2-C1 骨架（ADR-0060）之上长出

## 背景

宪法 §4A 要求"测试先行（fail-before：红必须是断言失败）+ 哈希锁定（g060）"。
现状两个缺口：(1) "先写实现后补测试"与真正的 test-first 在 git 历史上无法被
机器区分——测试 commit 与实现 commit 的先后、以及测试在实现前是否真的红过，
没有关卡判定；(2) 已合并的验收测试可被后续 PR"顺手改绿"——测试被改而不是
实现被修，无人拦截。卡 #215 触发：把 test-first 产物拓扑落成机器判定。

## 决策

1. **产物拓扑**：一张卡的产出分三段——test-author 先行 commit（验收测试集，
   `make card-test CARD=<n>` 入口）→ 实现 commit → lock-tests 锁定。CI 判定
   AC-1：测试 commit 早于实现 commit（git 历史可证）；新测试在实现前分支上
   的运行记录必须红，且红因=断言失败——import/编译/收集错误不算红
   （区分 exit code 来源：assert 失败 vs collection error，后者判 exit 3）。
2. **lock-tests 哈希锁定**：验收测试合并即计算锁定路径 manifest sha256 存
   `quality/locks/<card>.json`；`g060-test-tamper`：非 owner PR 改动锁定路径
   → exit 2（fail-escalate，只人类可解）（AC-2）。
3. **Spec-Change trailer 例外**：动锁定集的唯一合法通道=commit 带
   `Spec-Change: <spec PR#>` trailer；g060 回查该 spec PR 已合并且
   specVersion 递增，二者缺一即伪造，同样 exit 2（AC-2）。
4. **合法 spec 变更路径（AC-3）**：已合并 spec PR + trailer + specVersion
   递增 → lock-tests 重算锁定集；manifest 更新由 CI bot 提交，人类与 agent
   直接提交 manifest 变更即 fail（提交者身份校验）。
5. **Makefile 三命令**：`card-test` / `gates-fast` / `gates-pr` 与 CI 跑
   同一编排器入口（同一脚本、同一 GATE_* env 注入协议），本地与 CI 结果一致
   （AC-4）；gates-pr 供提 PR 前全量本地复现。
6. **负控制**：g060 自带测试——伪造 trailer fixture 必须被拒、合法 spec
   变更 fixture 必须放行。

## 后果

- 正面：test-first 从纪律变 git 历史可证的机器判定；锁定集关死"改测试变绿"
  的旁路。
- 负面/代价：合法重构想动锁定测试必须走 spec 变更流程，摩擦上升（设计
  使然——验收测试就是合同）；card-test 首次运行必然红，新手需理解这是特性。
- 风险与缓解："断言失败"判定器误判 collection error → 判定器自带负控制
  fixture；bot 提交被冒充 → 提交者身份校验（GitHub App bot 标识）。
- 回滚：摘除 g060 与 Makefile 目标即回无锁定世界；locks/ 是新增文件，
  删除无级联（新增式可拆）。
