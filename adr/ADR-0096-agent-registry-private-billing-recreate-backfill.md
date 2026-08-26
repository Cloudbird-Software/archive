# ADR-0096: agent-registry 私有仓计费止血删除重建回填

- status: accepted
- date: 2026-08-26
- deciders: owner（randypanding，删除重建操作与回填授权）/ PM 会话（回填登记）
- resolves: drift-check §8 报警的 agent-registry 52 笔非 PR commit 豁免登记（.github expected-state.json 同批 PR）；§4 仓库基线与 §7/§16 治理标签漂移的线上复原
- 关联: ADR-0085（agent-registry 退役声明——归档只读态，本 ADR 恢复之）；ADR-0092/0094（直推回填先例与 (a)/(b) 类定性）；ADR-0016（§8 豁免清单附录机制）；ADR-0019（agent-registry 可见性修正为 public——私有计费的历史根源）；ADR-0020（全仓公开政策）

## 背景

agent-registry 建于组织早期（ADR-0001），初始为 **private** 仓。GitHub 安全产品
（code security 等按仓计费项）对该私有仓持续计费，2026-08 账单浮出后 owner 决策止血：
**删除该仓后立即以 public 重建**（repo created_at=2026-08-26T10:45:36Z），从本地镜像
将删除前的 git 历史原样重推（HEAD=`063136672`，与退役时 main 一致）。

删除重建的机械后果（drift-check 全量浮出，共 65 项漂移）：

1. **PR 关联物理消失**：List pull requests associated with commit API 对窗口内全部
   54 笔 commit 返回空——原本经 PR 合法合并的历史（消息带 (#N) 后缀，合并事实曾在）
   在重建仓上全部呈现为"非 PR 直推"，其中 52 笔超 24h 回填时限报 P0；
2. **仓库设置重置**：重建仓 auto-merge=false（§4 基线漂移）；
3. **治理标签丢失**：12 个 state:*/type:* 标签随仓消失（§7/§16 漂移）；
4. **归档态丢失**：ADR-0085 声明的"GitHub 归档只读"未恢复（重建默认未归档）。

**内容保真机械验证**（本 ADR 的豁免背书基础）：退役快照
`archive/retired/agent-registry/`（registry/scripts/standards 三目录，85 文件）与重建仓
main 树逐 git blob SHA 比对——**85/85 全匹配，零差异**；重建未产生任何新 commit
（全部 54 笔 SHA 与删除前一致），净内容变更为零。

## 决策

1. **新增 (c) 类豁免定性：基础设施事件历史重推**——与既有两类并列：
   (a) 破玻璃直推回填（真实的内容直推，事后追认）；(b) 建仓 bootstrap（时序上 PR
   不可能）；(c) 仓级基础设施事件（删除重建/迁移镜像重推）——**无新 commit、零内容
   变更**，"直推"表象源于 PR 关联随仓删除物理消失而非绕过 PR 流程的事实直推。
   事件定性=owner 止血操作（私有计费），授权凭证=本 ADR。
2. **§8 豁免登记**：窗口内全部 54 笔（含 ADR-0030 已登记的 2 笔）逐完整 SHA 落
   expected-state.json `direct_push_exemptions["agent-registry"]`；comment 同步登记
   (c) 类语义。2026-08-31（末笔 commit 08-24 滑出 7 天窗口）前每日报警视为已回填
   已知项。
3. **线上态复原（owner API 操作，已完成）**：auto-merge=true 对齐 §4 基线；12 个
   治理标签按 expected-state 形状重建；**重新归档**恢复 ADR-0085 退役只读态
   （归档后不可再推送=不再产生新 §8 事件）。
4. **教训登记**：全仓公开政策（ADR-0020）下新仓必须以 public 建仓；私有仓的
   GitHub 商业产品计费是真实成本项，建仓时序上"先 private 后改 public"（ADR-0019
   的历史路径）会留下计费尾巴——agent-registry 是该路径的唯一存量受害者，账单
   止血以删除重建完成，不可复制为常规手段（每次重建都会摧毁 PR 关联与
   issues/workflow runs 历史，本 ADR 的 65 项漂移即为代价）。

## 后果

- drift-check §8 对 agent-registry 的 52 笔 P0 报警闭环（豁免登记 + ADR 背书）；
  §4/§7/§16 漂移经线上复原清零。下次 drift run 该仓应仅剩豁免命中 OK 行。
- agent-registry 恢复 ADR-0085 声明的退役只读态：public + archived，快照真源仍为
  `archive/retired/agent-registry/`，ADR 家园仍在本仓（archive/adr/）。
- 若未来 GitHub 对 archived public 仓仍计费（观察项），处置须走新 ADR——不允许
  再次删除重建。
