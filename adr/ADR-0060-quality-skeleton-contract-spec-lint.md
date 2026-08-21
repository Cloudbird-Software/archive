# ADR-0060: quality/ 骨架——contract.yaml 唯一阈值源 + spec lint（EARS/禁词/追溯闭合）+ g010

- status: accepted（2026-08-22）
- deciders: 人（owner randypanding）+ AI
- 关联: 宪法 §4A（阈值唯一来源）/§4E（追溯闭合）、.github#214（W2-C1）；
  外部范式：OpenSpec validate 模式 + StrictDoc UID 追溯模型 + EARS 六句型
  （宪法 §9 署名规则 #1）

## 背景

宪法 §4A 立铁律："阈值唯一来源 = quality/contract.yaml"。W1 收口后各产品仓
即将进入 W2 测试合规内核建设，但 template-service 尚无 quality/ 骨架——阈值
仍散落在各 workflow 的硬编码数字里，改一个阈值要翻 N 个仓；spec（.md）的验收
条款是散文，BEH 句无句型约束、模糊词（"合理/适当/尽可能"）无法被机器判定，
追溯（IR↔SPEC↔AC↔Card↔测试）靠人眼。卡 #214 触发：先落骨架与第一条关卡
g010，后续 W2-W5 关卡全部长在这个骨架上。

## 决策

1. **quality/ 骨架随 template-service 脚手架下发**（随后经 C1 scaffold 机制
   下发各产品仓）：`quality/contract.yaml` 是唯一阈值来源（机器可读 YAML，
   键=关卡 ID，值=阈值+单位+生效版本）；全仓 grep 断言关卡脚本与 workflow 内
   无硬编码数字阈值（AC-1），命中即 fail。
2. **关卡统一 CLI 契约（IFACE-04）**：每关卡一个入口脚本，经 `GATE_*` env
   注入上下文（GATE_PR/GATE_CARD/GATE_SPEC 等）；exit 语义四值：
   `0`=通过、`1`=fail-fixable（agent 可自修）、`2`=fail-escalate（只人类可解，
   如篡改类违规）、`3`=infra-error（环境故障，重试不计红）（AC-4）；每次运行
   落盘 gate-report JSON 且必须过 gate-report schema 校验（不过 schema 本身
   即 exit 3）。
3. **g010-spec-schema**：校验 spec.md 结构（H1/元数据块/AC 编号连续）；
   BEH 条款必须匹配 EARS 六句型正则（While/When/Where/…六句型，Given-When-Then
   归一化），不匹配即 exit 1 且 fixHint 指向具体违规行号（AC-2）。
4. **模糊禁词表（版本化）**：`合理/适当/尽可能/尽量/必要时/大概/等等` 等词
   出现在 AC/BEH 条款即 exit 1；唯一豁免=条款显式绑定 BUDGET 编号
   （如"预算 BUDGET-01"标注行），豁免必须可 grep 复核。
5. **UID 追溯闭合**：全链 UID 引用 IR↔SPEC↔AC↔Card↔测试↔代码；三类断链
   逐一 exit 1 并输出 UID（AC-3）——孤儿条款（有 AC 无卡无测试）、镀金范围
   （测试引用不存在的 AC）、断链（引用不存在的 UID）。
6. **lint 自身的判定物有效性（宪法 §4E）**：g010 自带负控制测试集（非法
   spec fixture 必须红、合法 fixture 必须绿），变更 lint 逻辑必须带测试。

## 后果

- 正面：阈值单源可审计；AC 从散文变可判定；追溯断链机器抓，镀金无处藏。
- 负面/代价：EARS 正则有误报面（合法句式被拦）→ 句型正则与禁词表随
  contract.yaml 版本化，放宽须 ADR；spec 作者多一层约束（设计使然）。
- 风险与缓解：lint 自身 bug 阻塞流水线 → g010 属 fail-fixable（exit 1），
  agent 可修；infra 故障显式 exit 3 不污染红绿统计。
- 回滚：quality/ 为新增目录，删目录即回原状；无状态迁移、无数据回填
  （卡面可逆性偏好：新增式可拆）。
