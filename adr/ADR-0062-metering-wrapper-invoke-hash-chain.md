# ADR-0062: 计量 wrapper 完整版——invoke 聚合 + 产物 hash 链 + LLM 预算通道

- status: accepted（2026-08-22）
- deciders: 人（owner randypanding）+ AI
- 关联: 宪法 §4A（计量）/§8（成本指标）、.github#216（W2-C3）、spec BEH-09、
  INV-06（无绕过直连）；预算熔断沿用 ADR-0040；spike T8 流式分片教训

## 背景

宪法要求一切 LLM 调用可计量、可归账、可审计。spike T8 暴露核心教训：
`LLM_STREAM_OUTPUT` 按流式分片打点，一次 invoke 被计成 N 条记录——成本
虚增、去重失败，必须按 invoke 聚合。同时 cost-check 的 LLM 预算通道此前的
数据源一直是 pending（ADR-0059 记录），单 IR 美元（宪法 §8）无数据可算。
卡 #216 触发：计量 wrapper 从 spike 形态升完整版。

## 决策

1. **唯一入口（INV-06）**：一切 LLM 调用经计量 wrapper，SDK 直连=违约；
   静态扫描关卡（直连 SDK 的 import/实例化模式）命中即 exit 1（AC-3），
   扫描模式库版本化，新绕过手法回流模式库。
2. **按 invoke 聚合**：一次 invoke（含多轮流式分片与工具回调）恰一条记录，
   聚合键=invoke_id；AC-1 判定：构造含流式的调用，落盘记录数==invoke 数，
   字段过计量 schema。
3. **BEH-09 字段齐全（AC-2）**：每条记录含 model alias（经 gateway）、
   prompt 版本+hash、seed、采样参数（temperature/top_p/max_tokens）、
   输入/输出 token 用量、耗时、调用方角色档、产物引用。
4. **产物 hash 链**：每阶段产物落盘即算 sha256，记录 prev_hash 形成链；
   链校验脚本可从任一断点验证整链完整性（防事后改产物）——红队报告、
   spec、golden 集等飞轮原料（宪法 §13 推论二）的可信度由链条背书。
5. **预算通道（AC-4）**：计量记录按角色档归账；cost-check（每小时，
   ADR-0057 cron）读取归账结果替代 pending 数据源，产出单 IR 美元、
   管家美元/周；超限熔断沿用 org 变量 `AUTO_MERGE_DISABLED`（ADR-0040），
   只降级为人签、不降级为少验（宪法 §5）。
6. **判定物有效性（§4E）**：wrapper 自带测试套件——流式聚合单测、
   hash 链篡改负控制（改一个中间产物，链校验必须红）。

## 后果

- 正面：成本可归账、产物可审计、数据飞轮原料有完整性背书。
- 负面/代价：wrapper 是热路径单点，性能开销与升级风险集中；计量记录
  体量增长（JSONL 落 archive 策略随飞轮卡落位）。
- 风险与缓解：静态扫描漏掉动态构造的直连 → 模式库版本化+红队攻击面
  （§4E 生产者红队持续攻击）；计量缺失本身按 §5 语义处理——缺证据=拒绝，
  不静默降级。
- 回滚：wrapper 可降级为纯透传（无计量运行），但计量缺失会让依赖计量
  证据的关卡显式黄/红，fail-closed 不假装闭环；摘除 wrapper 需同步摘除
  预算通道数据源声明。
