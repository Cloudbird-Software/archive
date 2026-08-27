# ADR-0101: Media-Monitor 小红书视频流下载契约与引擎签名头通道（IR-MM-0002 X2/X3）

- status: accepted
- date: 2026-08-27
- deciders: owner（randypanding，2026-08-27 会话授权 IR-MM-0002 执行）/ IR-MM-0002 实现会话 agent（登记）
- resolves: IR-MM-0002（Cloudbird-Software/Media-Monitor#86）AC-3/AC-4/AC-5 的治理背书——契约面新增平台下载能力与引擎签名语义变更属 C1 级决策
- 关联: ADR-0099（upstream 实体化）；IR-MM-0001 D-2（借鉴边界）/ INV-1（fail-closed）

## 背景

IR-MM-0002 触发场景之一（2026-08-27 实测）：VR 仓 IR-0001 IR-2.1 要求小红书
短视频流下载，Media-Monitor 现状 `download_video platform=xhs` fail-closed
（无 video_download 契约）。小红书 web API 的签名（x-s / x-s-common）作用于
**HTTP 请求头**而非 URL query——引擎现有签名管线只支持 query 路由与校验。

## 决策

1. **契约**：落地 `xhs-video-download`（POST /api/sns/web/v1/feed，占位符
   note_id 进 body，cookie.required=[web_session, a1]），binding 提取
   `video.media.stream.h264[*].master_url`（binder 已支持数组下标路径）。
2. **引擎签名头通道（IFACE-7）**：`Signature.Headers []string` 新契约字段——
   签名输出 kv 按声明路由进 HTTP 头；`signature.required` 校验改为 query OR
   headers 双侧 fail-closed。既有 douyin 契约（query 签名）零行为变化。
3. **签名算法部署自有**：signsvc 维持 node provider 架构（ADR 无需变更），
   xhs 签名脚本属部署侧资产（HARDENING M3：算法不入客户端仓）。live 灰由
   owner 环境验收。
4. **借鉴边界（承 IR-MM-0001 D-2 口径）**：
   - **Johnserf-Seed/f2（Apache-2.0，已 pin allowed）**：xhs 端点参数表与
     请求形态的可参照可搬正本。
   - **NanmiCoder/MediaCrawler（非商用，forbidden）**：维持 knowledge-only，
     不搬代码。
   - **JoeanAmier/XHS-Downloader（GPL-3.0）**：组织依赖政策禁运
     （AGPL/GPL-3.0/SSPL），**不入 registry、不 submodule、不搬代码**；
     仅限黑盒行为观察。

## 影响

- `resolve_video` / `download_video` MCP 工具零改动获得 xhs 能力
  （契约即原子，INV-5）；live 调用在签名脚本部署前保持 fail-closed。
- 离线金样 canary 扩展（fixtures × contracts），offline 面先行验收。
- 引擎签名语义保持 INV-1：缺失即显式错误，无静默降级。
