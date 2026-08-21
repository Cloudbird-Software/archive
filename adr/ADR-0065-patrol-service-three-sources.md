# ADR-0065: patrol 巡逻服务——三源场景 + 指纹去重频控 + 毕业机制

- status: accepted（2026-08-22）
- deciders: 人（owner randypanding）+ AI
- 关联: 宪法 §3（patrol：场景三源/observation 桶/毕业机制）/§8（patrol yield）；
  .github#219（W3-C2）；指纹去重沿用 drift-report 模式（先例 ADR-0020 系列）

## 背景

宪法 §3 定义 patrol：持续对运行中系统做对抗性探测，但立了三条纪律——
只在机器可判定 oracle 违约时开单（"看着不对"不算）；LLM 主观怀疑只进
observation 桶且两次独立出现才升级；抓到真 bug 的场景毕业进 CI 回归并
离开 patrol 语料（防对已知缺陷反复开单刷熟）。现状无任何巡逻面：逃逸过的
模式没有系统性再攻击，AC 注册表里的声明没有运行时对账。卡 #219 触发。

## 决策

1. **三源场景生成**：(a) AC 注册表派生——从 quality/ 的 AC UID 自动生成
   运行时检查场景（声明 vs 实际行为对账）；(b) 历史逃逸模式攻击语法——
   逃逸模式库（drift/红队/演习沉淀）参数化生成变体再攻击；(c) LLM 前沿
   探索 + metamorphic 关系（等价变换下 oracle 不变式必须保持）。
2. **开单判据（AC-1）**：仅机器可判定 oracle 违约开 bug IR（崩溃/5xx/
   schema 违约/不变量破坏/性能预算超限），单必附 trace+指纹；LLM"看着
   不对"只进 observation 桶，两次独立（不同场景或不同 run）出现才升级
   开单。
3. **指纹去重 + 频控（AC-2）**：指纹=场景 ID+症状 sha256，同指纹不重复
   开单（沿用 drift-report 指纹去重模式）；每仓每日开单上限与 run 频率
   在 `governance/policy/patrol.yaml` 版本化，改动走 C1。
4. **毕业机制（AC-3）**：场景抓到真 bug（经 ADR-0064 reproduce 复现成功）
   → 场景转 CI 回归套件 + 从 patrol 语料库移除——patrol 对已毕业生效的
   缺陷反复报警只会污染 yield。
5. **权限最小化**：patrol 只读运行（探针）+ 开 issue 权限；不得改代码、
   不得改状态标签（写状态归 arbiter，INV-02 一致）。
6. **yield 度量（AC-4）**：每百次运行唯一真 bug 数、开单复现存活率；
   信噪比（真 bug/开单数）低于阈值自动降频并开 needs-human 复核——
   yield 进成本指标组（宪法 §8、ADR-0073 dashboard）。

## 后果

- 正面：逃逸模式获得系统性再攻击面；AC 声明有运行时对账；observation
  桶防 LLM 幻觉灌水开单。
- 负面/代价：三源生成的算力与 LLM 成本（计入管家美元/周）；毕业-离库
  使语料库需要持续补给（LLM 前沿探索源承担）。
- 风险与缓解：metamorphic oracle 自身有 bug → 每个 oracle 带负控制
  （已知违约样本必须被抓）；频控过松刷屏/过紧漏报 → 频控参数版本化+
  yield 数据驱动调参。
- 回滚：patrol workflow 摘除即停（cron 停即静默，§6 缺席纪律由 dead-man
  统一监督）；语料库与指纹台账留存无害。
