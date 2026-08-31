# ADR-0104: LLM 供应商切换——StepFun Step Plan（step-3.7-flash）与计量层 provider 适配

- status: accepted（2026-08-31）
- deciders: 人（owner randypanding，2026-08-31 直令：Action secrets 已更新 StepFun
  key，要求恢复 adversary gate LLM 节点）+ AI（PM 会话，GLM-5.3）
- 关联: ADR-0048（LLM 供应商接入与 org secret 形态）；ADR-0062（metering 唯一入口
  与 hash 链）；ADR-0067（恶意合规 adversary——judge-deep 考试档案锁定）；
  ADR-0072（llm-verifier 同构档案）；ADR-0085（archive 仓 ADR 家园）

## 背景

LLM 供应商通道自 2026-08-30 起连续故障：原 sensenova（deepseek-v4-flash）通道
429（配额/限流），adversary attack 六连红、specs/** PR 的 adversary check 全线
阻断。owner 于 2026-08-31 更新 org secret `LLM_API_KEY1` 为阶跃星辰（StepFun）
Step Plan 订阅 key，并将 org vars 指向 `LLM_ENDPOINT1=https://api.stepfun.com/step_plan/v1`、
`MODEL1=step-3.7-flash`（文档：platform.stepfun.com step-3.7-flash）。

接入实测暴露三处不兼容：

1. **端点形状**：Step Plan 订阅 key 走 `step_plan/v1` 路径（与标准 API key 的
   `/v1` 不同：标准端点对订阅 key 返回 402 Payment Required）；metering wrapper
   拼 `$LLM_BASE_URL/chat/completions` 对带尾斜杠的 var 产生双斜杠。
2. **常开推理**：step-3.7-flash 无 thinking disabled 档（reasoning_effort
   low/medium/high 三档）；GLM 形 `thinking` 参数被静默忽略，max_tokens=16 的
   连通性探测 completion 全被思维链吃空 → 计量 fail-closed（"2xx 缺内容"）误报。
3. **考试档案锁定**：adversary-config.yaml/models.yaml judge-deep 档锁
   `deepseek-v4-flash`（供应商已不可用），任何改动=C1 变更（本 ADR）。

## 决策

1. **供应商切换**：org vars 语义保持"endpoint+model 二元组"，值切换为
   StepFun Step Plan 通道（`https://api.stepfun.com/step_plan/v1`，无尾斜杠——
   wrapper 以 `$BASE_URL/chat/completions` 拼接）。secret 沿用 `LLM_API_KEY1`
   单枚形态（ADR-0048 不变）。
2. **计量层 provider 适配（显式留痕，不静默）**：metering.py mkreq 按精确 host
   匹配新增 `api.stepfun.com` 分支——GLM 形 `thinking` 翻译为最接近档
   （disabled→reasoning_effort low、enabled→medium）并剔除未知参数；计量记录
   仍按调用方锁定值归档（与既有 api.kimi.com 参数剔除同一先例）。
3. **考试档案换模型**：adversary-config.yaml 与 pipeline/models.yaml 的
   judge-deep 档 model 由 `deepseek-v4-flash` 切为 `step-3.7-flash`
   （prompt/采样/族分离/跨族断言语义不变；prompt_sha256 不涉及）。锁定语义
   不变：换模型仍属 C1，须新 ADR。
4. **连通性探针**：llm-connectivity 探测调用 max_tokens 16→128 且 prompt 改为
   单词应答（常开推理下 16 tokens 恒空正文；成本仍为计量类最小档）。
5. **egress 白名单注释域**：adversary/llm-connectivity 的 harden-runner
   allowed-endpoints 域名清单同步 `api.stepfun.com`（当前 egress-policy=audit，
   清单为文档语义，非阻断面）。

## 后果

- adversary/llm-connectivity 恢复绿；specs/** PR 审计通道闭合。
- 判定模型族标签 sovereign-family 保留（族分离是治理概念，非供应商绑定；
  StepFun 与 builder/test-author 族的供应商级分离由后续 ADR 需要时再断言）。
- spec-author 档（glm-4.5-air + secrets.LLM_API_KEY）不在本 ADR 范围——该通道
  org secret 已删除，恢复属独立决策。
