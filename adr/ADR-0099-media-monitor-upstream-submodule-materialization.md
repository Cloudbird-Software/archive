# ADR-0099: 上游生态 submodule 实体化（Media-Monitor upstream 双轨·轨道 A）

- status: accepted
- date: 2026-08-26
- deciders: owner（randypanding，2026-08-26 会话授权 IR-MM-0001 执行）/ IR-MM-0001 实现会话 agent（登记）
- resolves: IR-MM-0001（Cloudbird-Software/Media-Monitor#16）AC-11 的治理背书——upstream/ 结构变更与 arch-check 守卫属 C1 级决策，需 ADR 正本供后续 PR 引用
- 关联: ADR-0098（同 IR 前置）；IR-MM-0001 D-2（借鉴边界）/ D-3（上游双轨）

## 背景

Media-Monitor upstream/registry.json 登记六个上游观测对象（f2 /
wx_channels_download / MediaCrawler / UI-TARS / scrcpy /
Douyin_TikTok_Download_API），pin 全部 TBD——平台改版时无「上游开源界已
验证的修法参考」可 diff（IR-MM-0001 触发场景之二）；swap-test 无本地基线。

IR-MM-0001 D-3 定调上游双轨：GitHub API 轮询预警（已有 workflow）+
submodule 本地 diff（swap-test 素材）并行。本 ADR 落轨道 A 的实体化。

## 决策

1. **submodule 实体化**：upstream/vendor/ 挂 f2 / wx_channels_download /
   MediaCrawler / UI-TARS 四 submodule（.gitmodules 路径
   upstream/vendor/<slug>）；pin SHA 与 upstream/registry.json 逐条对齐；
   registry 六条目 pin 全落实（scrcpy 保留既有 tag v3.3.4，
   Douyin_TikTok_Download_API 补 pin）。
2. **pin 移动走 PR**：submodule 指针变更是可评审的数据变更，一律 PR
   （不直推）。
3. **编译面隔离（INV-3）**：internal/ 永不 import upstream/——submodule
   是可 diff 的观测副本，不是依赖；quality/arch-check.sh 增守卫拦截违规
   import（fail-closed）。go.mod 保持零 require（submodule 不进编译面，
   依赖政策不破）。
4. **借鉴边界（承 IR D-2）**：f2（Apache-2.0）/ wx_channels_download
   （MIT）/ UI-TARS（Apache-2.0）可参照可搬；MediaCrawler（非商用
   license）只学参数表与绑定知识，不搬代码、不 vendored。

## 影响

- IR-MM-0001 AC-11 可实施：watcher diff 摘要（AC-12）与 swap-test bench
  （AC-13）获得本地 diff 基线。
- 仓库克隆默认不含 submodule 内容（需 --recurse-submodules）；CI 不依赖
  submodule 就位（arch-check 只看 import 语句）。
- 后续触碰 quality/（arch-check 守卫）与 docs/UPSTREAM.md 的 PR 引用
  本 ADR。
