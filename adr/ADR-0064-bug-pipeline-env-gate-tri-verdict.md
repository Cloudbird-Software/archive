# ADR-0064: Bug 流水线——env-gate + 哨兵自证 + 三值判定 + cannot-reproduce

- status: accepted（2026-08-22）
- deciders: 人（owner randypanding）+ AI
- 关联: 宪法 §3（Bug 流：复现前置、签署点后移）/§9#6；.github#218（W3-C1）；
  外部范式：SWT-bench F→P 判定协议 + Agentless 分层定位 + mini-SWE-agent
  极简循环 + EPR 集合投票（宪法 §9 署名规则 #6）

## 背景

宪法 §3 立 Bug 流铁律："复现前置，签署点后移"。现状痛点：bug 单直接进修复，
复现失败无法区分"环境漂移"与"bug 不存在"——误关真 bug 的代价不可见；且
无环境自证的复现结论本身不可信（环境坏了跑什么都是绿的）。卡 #218 触发：
把 reproduce 阶段落成免签的机器流水线。判定协议=SWT-bench F→P 的三值扩展：
`(base 上 fail, fix 上 pass)=复现`、`(base 上 pass)=证伪`、
`环境错/超时/翻转异常=不可判定`。

## 决策

1. **bug issue form**：结构化上报（repo/版本/环境指纹/复现步骤/症状签名），
   打 `bug` 标签即进 reproduce 阶段（免签——区别于 Feature 流的 spec 前置）。
2. **env-gate（锁依赖镜像）**：复现环境锁定=基础镜像 digest + lockfile
   hash 双锁；与上报环境指纹对账，不一致判"不可判定"而非"证伪"。
3. **哨兵环境自证（fail-closed）**：复现运行前必须通过——基线测试套件
   全绿 ∧ 故意失败的哨兵测试必须红（证明这套环境真的会红）；自证日志
   缺失 → 不做任何判定，直接 fail 变红（AC-1）。
4. **三值判定（AC-1/AC-2/AC-3）**：复现=base fail ∧ repro 脚本 pass →
   打 `reproduced`，产 failing repro test（挂 BUG-n 标记）→ owner 签 →
   锁定（ADR-0061）→ 修复走正常关卡；证伪=base 上 pass → 打
   `cannot-reproduce`，**不 close 单**；不可判定=环境错/超时（30min）/
   翻转异常 → 打 `inconclusive`，换新环境重试一次，仍不可判定 →
   needs-human。
5. **cannot-reproduce 指纹绕过**：症状指纹=仓+症状摘要+关键栈的 sha256；
   同指纹二次上报自动绕过重复流程直挂同指纹台账（防同一 bug 反复走全流程）。
6. **误关率抽样（AC-4）**：每周随机抽 3 单人工复核，误关率成数字进
   dashboard（宪法 §3"误关率每周抽样成数字"）。
7. **署名条款**：判定协议源自 SWT-bench F→P（测试先行判 bug 真伪的基准
   协议）扩展为三值；定位辅助参考 Agentless 分层定位；闭环结构参考
   mini-SWE-agent；多源投票参考 EPR 集合（宪法 §9#6）。

## 后果

- 正面：消灭"改了但没修"与"误关真 bug"两类损失；环境自证让"复现失败"
  有了可分辨的三种语义，不再被迫二值化。
- 负面/代价：不可判定路径消耗环境资源（重试一次）；30min 超时上限使
  慢复现 bug 需人工介入。
- 风险与缓解：哨兵自证被绕过（环境伪装绿）→ 自证日志入审计，周演习
  （ADR-0069）可注入"哨兵失灵"样本；repro test 本身 flaky → 进 flaky
  预算制（§4A）管辖。
- 回滚：bug form + reproduce workflow 均新增式，摘除即回 label+人工流；
   transitions.yaml 增补的标签转移可随摘除回退。
