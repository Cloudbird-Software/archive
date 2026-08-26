# ADR-0100: vision 层解冻接 UI-TARS（Media-Monitor upstream 双轨·轨道 B）

- status: accepted
- date: 2026-08-26
- deciders: owner（randypanding，2026-08-26 会话授权 IR-MM-0001 执行）/ IR-MM-0001 实现会话 agent（登记）
- resolves: IR-MM-0001（Cloudbird-Software/Media-Monitor#16）AC-14 的治理背书——internal/vision 解冻与端点配置语义属 C1 级决策，需 ADR 正本供后续 PR 引用
- 关联: ADR-0099（同 IR 双轨另一面）；IR-MM-0001 D-4（vision 选型）/ D-5（shipinhao 降级）

## 背景

Media-Monitor internal/vision 自建仓起冻结（当期无端点可接）。平台改版
频发场景下，契约红后除「上游 diff 参考」（轨道 A）外还需「vision 驱动的
API 形态重发现」路径：真机走采集路径 + netcapture 录 HAR → 候选
fixture → 契约补丁提案（IR-MM-0001 BEH-11..13）。

IR-MM-0001 D-4 定调选型 UI-TARS（upstream registry 已登记 Apache-2.0），
接入形态为 OpenAI 兼容端点（ENV-REQ-3 既定方案）。

## 决策

1. **vision 层解冻**：internal/vision 的 Provider 接 OpenAI 兼容
   chat-completions 端点（环境变量 MEDIAMON_VISION_ENDPOINT），输入截图
   + 任务描述 → 输出语义动作序列。
2. **定位是重发现器，不是备胎采集器**：vision 驱动真机走采集路径 →
   netcapture 录 HAR → 转候选 fixture → 契约补丁提案；兼作契约全红时的
   降级采集通道（屏幕数据直读）。语义动作词汇表对齐 internal/adb 既有
   能力（tap / swipe / text / screencap / uidump）。
3. **fail-closed 语义**：MEDIAMON_VISION_ENDPOINT 未配置时调用 vision
   显式报错，不静默跳过（INV-1 口径）。
4. **flow 蒸馏回写机制保持**：成功 run 蒸馏为 flow script 的现有机制不
   动，解冻不重构。

## 影响

- IR-MM-0001 AC-14 可实施；与 netcapture→fixture 转换器（AC-15）组合
  构成改版适配轨道 B 闭环。
- shipinhao（无稳定端点）经本轨道覆盖：netcapture+vision 专属通道
  （IR D-5），不进契约体系。
- 端点属 owner 提供环境（ENV-REQ-3）；仓库不含任何模型权重或端点凭据
  （INV-6）。
- 后续触碰 internal/vision 与 docs/ 的相关 PR 引用本 ADR。
