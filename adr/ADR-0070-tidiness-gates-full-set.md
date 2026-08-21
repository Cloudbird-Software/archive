# ADR-0070: 整洁关卡组全量——结构 + AI 导航 + 抗复杂度 + 棘轮

- status: accepted（2026-08-22）
- deciders: 人（owner randypanding）+ AI
- 关联: 宪法 §4A（整洁全景）/§9#5；.github#224（W5-C1）；外部范式：
  dependency-cruiser / import-linter / go-arch-lint（按仓选型）、认知复杂度
  （Sonar 系度量）、CodeScene 因素清单、aider repo-map（宪法 §9 署名规则
  #5）；骨架建于 ADR-0060（W2-C1）

## 背景

宪法 §4A 整洁域列了四组关卡，但 W2 只落了骨架与 spec 面卡点。W5-C1 触发
全量补齐。特别动机：(1) AI 编码的复杂化冲动（死通用性、无逻辑 wrapper、
过度抽象）需要机器对手——人 review 拦不住规模化产生的抽象通胀；(2)
**AI 导航容易度度量是公共知识空白**（§9#5：repo-map token 成本+引用跳数+
agent 定位耗时配对校准——自研）；(3) 全仓指标只许变好的棘轮需要 baseline
与 CI bot 写入纪律。

## 决策

1. **结构架构组**：CRAP diff；认知复杂度阈值（lint 内建规则）；模块形状
   （depthRatio≥3 理想 5、exports≤7、fanOut 上限）；依赖架构按仓选型
   dependency-cruiser（JS/TS）/ import-linter（Python）/ go-arch-lint（Go）
   ——分层/无环/无跨 feature 私连/index 出口纪律；api-surface diff
   （公共 API/路由/DB 迁移/env 集合变更必须显式声明）。判定引擎一律
   用公共知识现成轮子（宪法 §9 原则：不造）。
2. **AI 导航关卡组（自研度量）**：每目录文件数上限（防平铺）；repo-map
   固定 token 预算下符号覆盖率（aider repo-map 方法）；引用图平均跳数/
   直径/环数；文档-符号链接验真（AGENTS.md/docs 引用的符号对 AST 验
   存在）；词表 lint（版本化 glossary，未定义术语即 fail）；抽样任务
   agent 定位耗时配对校准（月度基准任务集——度量与真实 agent 效率的
   相关性验证器）。全部输出指标、超阈值 fail（AC-2）。
3. **抗复杂度组（对 AI 复杂化冲动）**：死通用性检测（未使用的导出/参数/
   配置键）；过度抽象（接口:实现=1:1 计数；新抽象调用点 <3 即拦——
   Rule-of-Three 机械化）；无逻辑 wrapper 套娃计数；每卡净增 LOC 预算；
   抑制标记零增长；豁免审计（豁免必须带理由且进 PR diff 可见，豁免
   行数本身是指标）。
4. **棘轮（AC-3）**：`baseline.json` 全仓指标只许变好；指标变差 → g900
   fail；变好由 CI bot 提交更新——提交者身份校验，agent/人类直接提交
   baseline 变更即 fail；放宽须人类批准的 bot 提交。
5. **阈值唯一来源（AC-4）**：全部阈值只在 `quality/contract.yaml`
   （INV-08 镜像校验：CI-Workflows 钉版下发与各仓 contract.yaml 一致性
   对账）。
6. **验收（AC-1）**：锁定脏 PR fixture（高复杂度/浅模块/跨层依赖/
   eslint-disable/平铺目录）被各关卡逐条拦下且 fixHint 含 ruleId；
   修复后全绿（spec AC-7）。

## 后果

- 正面：AI 复杂化冲动有机器对手；导航质量可度量可回归；指标只升不降
  写入纪律。
- 负面/代价：关卡组全量首启有误报潮 → 棘轮先冻结现状再分批收紧；
  月度定位校准任务是持续性成本。
- 风险与缓解：导航度量与真实效率相关性未证 → 配对校准任务集就是
  验证器，相关性差则调权重（阈值版本化）；死通用性检测误杀预埋扩展点
  → 豁免审计通道。
- 回滚：各关卡独立开关（contract.yaml per-gate enable），可整组退场；
  baseline.json 删除即回无棘轮世界（新增式可拆）。
