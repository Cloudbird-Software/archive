# ADR-0091: Viral_Radar 建仓申报与 Python 多模态复用豁免——全网爆款对标分析系统

- status: accepted（2026-08-25）
- deciders: 人（owner randypanding）+ AI（PM 会话，GLM-5.3）
- 关联: IR（Cloudbird-Software/Viral_Radar#1——需求意图登记书全量冻结）；
  governance/REPOS.yaml（GM-4 申报入图）；governance/policy/languages.yaml（豁免对象）；
  GOVERNANCE flows.new_repo；ADR-0020（组织全仓公开政策）；ADR-0023（AI_Web_School
  语言准入豁免先例）；ADR-0084（QW_Arena1 语言豁免先例——本 ADR 区别：多模态生态
  复用而非外部比赛契约）；ADR-0090（org admin bypass 基线——本仓 bootstrap 路径
  依其决策 4 简化）；ADR-0002（LLM Gateway 常驻服务模式——本仓 LLM 网关层沿用）；
  ADR-0039（依赖供应链白名单——决策 5 许可判定的现行模型）；ADR-0026（PURL 精确
  豁免通道——非白名单许可的唯一例外路径）

## 背景

owner 提出业务需求（IR Viral_Radar#1）：对微信视频号、抖音、小红书三大平台的
5-20 个对标账号做数据采集（近 6 个月）、多模态文案提取（ASR 带时间戳 + OCR 花字
字幕）、大模型秒级爆款逻辑拆解、单账号深度报告 + 多账号聚合报告，并基于拆解逻辑
生成新脚本草稿与拍摄 SOP。系统形态为"微内核 + 多平台适配器"异步流水线。

建仓已完成：Viral_Radar（public，L2）经 template-service 官方模板实例化 API
（generate endpoint）创建——模板基线由 GitHub 模板机制直接落 main（含
ci.yml/hygiene/quality 脚手架），new-repo-init.sh 四步基线（squash-only/合并删
分支/auto-merge/wiki+projects 关）与治理标签（type:*/state:* 全套）已同步。
按 flows.new_repo，语言选型依据与政策豁免须本 ADR 登记；REPOS.yaml 申报入图
（GM-4）随后以独立 PR 落地（.github 仓）。

开源能力调研（选型依据，广泛搜索结论）：目标域的核心可复用资产主要沉淀在
Python 生态——ASR 层 faster-whisper（MIT，CTranslate2 推理，原生 segment 级
时间戳）；OCR 层 RapidOCR（Apache-2.0，ONNX 离线推理）/PaddleOCR
（Apache-2.0）；LLM 网关层 LiteLLM（MIT，OpenAI 格式统一 100+ provider，含
成本追踪/降级/fallback）。采集层参考资产生态混布：MediaCrawler（Python，
抖音/小红书/快手/B站/微博，CDP 模式）与 wx_channel（**Go** 实现，MIT，视频号
下载）——采集通道本仓自研（见决策 5"参考不依赖"），不构成语言选型输入；
语言选型由 ASR/OCR/LLM 网关三层推理生态钉死（Go/TS 在该域无同等成熟度组合）。

组织现行语言政策（languages.yaml application 层）默认 go，python 仅限
"agent-runtime integration only"（ADR-0025），且 ADR-0085 后新仓 Python 准入
回归默认拒绝。本仓选 Python 与政策冲突，须组织层面登记豁免。

## 决策

1. **建仓申报 Viral_Radar**：L2 实现层、public（ADR-0020）、template-service
   基线派生（generate endpoint 实例化——模板内容落 main 属 GitHub 官方模板机制，
   非 agent 直推；此后本仓一切变更走 PR+squash（BP-1））、new-repo-init.sh 基线
   已完成、申报入 governance/REPOS.yaml（GM-4，独立 PR 引用本 ADR）。
2. **语言选型：Python**。理由：
   a. **多模态推理链生态垄断**：ASR（faster-whisper/whisper.cpp 绑定）、OCR
      （RapidOCR/PaddleOCR）、视频音轨分离（ffmpeg-python）、LLM 网关（LiteLLM
      SDK）的成熟开源实现均为 Python 一等公民；Go/TS 侧需自行封装或绑定二进制，
      复用面塌缩为"调用方"而非"复用方"；
   b. **复用优先原则**（IR 明示"优先考虑复用开源项目的能力"）：选 Python =
      直接复用上述五层资产；选 Go = 对每层重写适配，违背 IR 约束；
   c. **AI 总线/LLM 网关层沿用 ADR-0002 模式**（LiteLLM 常驻网关），其 Python
      SDK 与组织既有 LLM Gateway 形态一致。
3. **语言规范豁免（组织层面声明）**：languages.yaml 对 Viral_Radar **整体豁免**
   ——application 层 Go 基线与 PY-1/PY-2 等 gate 级语言规则均不适用。理由
   （与 ADR-0023/0084 先例同构，但条件不同——本仓是"生态复用"型豁免）：
   a. **复用外部契约优先**：核心能力（ASR 时间戳输出/OCR 中文识别/LLM 网关）
      由外部开源项目提供，其 API 形态钉死 Python；组织 Go 基线与"复用优先"
      的 IR 约束直接冲突，IR 是更高优先级的需求源；
   b. **多模态域无 Go 等价物**：这不是偏好问题而是生态事实——组织语言政策
      的 rationale（"训练数据海量、写法单一"）在多模态推理域反转：Python 的
      多模态样本量远超 Go；
   c. **与 QW_Arena1 的边界**：ADR-0084 是"外部契约+有限生命周期"豁免（比赛
      仓，赛后退役）；本仓是"生态复用"豁免（长寿命产品仓）——援引本豁免的新仓
      必须证明目标域核心能力沉淀在 Python 生态且无 Go/TS 等价物，否则不成立。
4. **豁免边界（不豁免项）**：全仓公开（ADR-0020）、默认分支 PR+squash（BP-1）、
   gate/org-gate/adversary 双轨 required check、hygiene（gitleaks/zizmor）、
   CODEOWNERS、REPOS.yaml 申报义务（GM-4）、依赖审批（dependency_policy——
   见决策 5 的许可面约束）、suppression-budget/quality-gates——治理基线不变，
   仅语言规范面豁免。
5. **开源选型登记与许可裁决**（dependency_policy proposal 格式：
   name/purpose/license/stdlib_alternative；许可判定按 ADR-0039 白名单模型
   ——deny-by-default，不在 allow-licenses 即红）：
   - **faster-whisper**（MIT）：ASR 引擎，segment 级时间戳原生输出，满足 IR-3.1
     强制要求。stdlib_alternative：无（自训 ASR 不可行）。
   - **RapidOCR**（Apache-2.0）：OCR 引擎，ONNX 离线推理，中英识别满足 IR-3.2。
     注：仓库代码 Apache-2.0，但其所用 PP-OCR 模型权重版权归 Baidu（模型与
     工程代码版权分离——上游文档明示），商用合规面在首个依赖引入 PR 复核。
     stdlib_alternative：无。
   - **LiteLLM**（MIT，open core）：LLM 网关层，满足 NFR-3 大模型抽象层
     （本地/第三方热切换）。stdlib_alternative：无（自研网关成本远超复用）。
   - **yt-dlp**（Unlicense）：通用媒体流下载内核（仅其提取器框架作为参考实现，
     不直接用于三目标平台）。stdlib_alternative：无。
   - **MediaCrawler**（自定义非商用学习许可——不在 ADR-0039 白名单）：
     抖音/小红书采集能力参考。裁决：**不 vendored、不分发、不直接依赖其代码**
     ——本仓以适配器模式自研采集通道，MediaCrawler 仅作协议/登录态处理的技术
     参照。按 ADR-0039 白名单语义，其许可 deny-by-default：若未来确需直接依赖，
     仅可经 ADR-0026 PURL 精确豁免通道（allow-dependencies-licenses）逐版本
     豁免并须独立 ADR 论证，"owner 批准"本身不构成放行判据。
   - **wx_channel**（MIT，Go 实现）：视频号采集参考，同 MediaCrawler"参考不
     依赖"裁决（许可虽在白名单，但采集通道本仓自研的决策不变）。
   风险与缓解：采集层反爬对抗是持续成本（IR Action Item 明示"自研 vs 采购
   第三方数据 API"待评估）——本 ADR 仅锁"参考不依赖"姿态，采购/自研裁决留给
   后续 spec 阶段红队审查。
6. **合规红线（随 ADR 固化）**：IR 边界"仅采集公开可浏览数据及已授权自有账号
   数据"为 spec 级不变量候选；频控/代理池（NFR-1）不得演化为对目标平台的
   高频压迫——spec 阶段红队（adversary-gate）将对采集节流策略重点审查。

## 后果

- 正面：需求获得治理化承接（IR#1 可追溯/可审计/红队可锚定）；五层开源资产
  复用路径明确；语言例外有清晰边界与援引条件；采集层许可风险前置隔离
  （参考不依赖）。
- 负面/成本：组织第三个 Python 豁免仓（AI_Web_School/QW_Arena1 之后）——
  豁免面继续扩大；多模态推理链引入重依赖（CTranslate2/ONNXRuntime），CI 需
  处理模型权重缓存与测试时长；template-service 继承的 Node 脚手架在本仓首个
  实现 PR 中替换为 Python 结构（引用本 ADR）。
- 风险与缓解：豁免被泛化援引——决策 3c 显式限定"生态复用"条件（核心能力
  Python 垄断 + 无等价物 + IR 明示复用优先），REPOS.yaml role 注记即
  drift-check 审计锚点；采集层合规风险——决策 5/6 的"参考不依赖"与公开数据
  边界由 spec 红队二次把关。

## 验证

- Viral_Radar 仓线上存在且 public；template 基线 72 文件与 template-service
  逐文件 sha 一致（generate endpoint 官方实例化，git trees recursive=1 对账
  已复核）
- new-repo-init.sh 基线验证记录：squash-only/合并删分支/auto-merge/wiki+projects
  关 + 治理标签全套（type:*/state:*）已同步
- IR（Viral_Radar#1）九字段与原始需求文档逐节可对照——spec 红队审查锚点成立
- REPOS.yaml 申报条目：本 ADR 合并后以独立 PR 落地（.github 仓，引用本
  ADR——GM-4；本 ADR 不宣称其已完成）
- 本 ADR 双落盘：archive/adr/ 正本 + INDEX.yaml 登记（born-in-archive，
  source_closed 后无墓碑义务）
