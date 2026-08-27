# ADR-0102: Media-Monitor 视频号 netcapture+解密专属通道与 upstream 实体化扩展（IR-MM-0002 S1/S2/S3）

- status: accepted
- date: 2026-08-27
- deciders: owner（randypanding，2026-08-27 会话授权 IR-MM-0002 执行，并明示「凡借鉴的开源项目须经 submodule 获取上游信息」）/ IR-MM-0002 实现会话 agent（登记）
- resolves: IR-MM-0002（Cloudbird-Software/Media-Monitor#86）AC-6/AC-7/AC-8 的治理背书
- 关联: ADR-0099（upstream 实体化先例）；IR-MM-0001 D-4/D-5（shipinhao 降级为 netcapture+vision 专属通道）

## 背景

视频号（微信 Channels）无稳定 web API 端点（IR-MM-0001 D-5 既定不走契约
体系）。其媒体流经微信 CDN 分发且**载荷加密**：解密密钥由客户端单独请求
获取，视频字节需以 Isaac64 PRNG 密钥流 XOR 还原。开源界已有可验证的完整
实现链（拦截 → 取 key → 解密），但 Media-Monitor 的 upstream registry 尚未
实体化这些参考副本——平台改版时无可 diff 上游。

## 决策

1. **通道形态**：沿用 D-5 专属通道——微信 PC 客户端（owner 登录态）+ 本机
   代理（netcapture）捕获媒体流 URL 与 key 请求 → 解密引擎产出标准
   artifact（{path, bytes, sha256}）。不建 shipinhao 契约（无稳定端点，
   INV-5 契约面不收录）。
2. **解密引擎**：Go stdlib 实现 Isaac64 PRNG + XOR 密钥流（无新依赖）；
   `shipinhao_resolve` MCP 工具封装 session → 下载+解密+校验全链；
   fail-closed：无会话 / 无 key / 解密完整性校验不过 → 显式错误码。
3. **upstream 实体化扩展（承 ADR-0099 先例与 owner 2026-08-27 明示）**：
   - **Evil0ctal/WeChat-Channels-Video-File-Decryption（MIT，allowed）**：
     解密算法语义正本（Isaac64 keystream + XOR + WASM 模块行为）。
   - **putyy/res-downloader（Apache-2.0，allowed）**：代理嗅探下载器架构
     参考（Go 同语言；多平台资源拦截分类器形态）。
   - 两者以 submodule 落 upstream/vendor/ + registry pin（SHA 对齐）+
     license verdict；internal/ 永不 import upstream/（INV-3 不变）。
   - **ltaoo/wx_channels_download（MIT-Commons，已 pin allowed）**：既有
     参考维持——客户端注入形态的对照组。
4. **借鉴边界**：以上三家均可参照可搬；MediaCrawler（forbidden）不涉及；
   XHS-Downloader（GPL-3.0）禁运不涉及。

## 影响

- IR-MM-0002 AC-6/AC-7/AC-8 可实施；watcher 对新增两 submodule 出
  diff 摘要（改版预警面扩大）。
- 视频号通道的登录态归微信客户端自有（owner 扫码），不经账号池 cookie——
  合规边界（不做代登录）自然成立。
- Isaac64 实现纯 stdlib，go.mod 保持零 require。
