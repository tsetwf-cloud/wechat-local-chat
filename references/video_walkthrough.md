# WeChat Skill walkthrough

## English

[Captioned video](https://github.com/tsetwf-cloud/wechat-local-chat/releases/download/tutorial-v0.1.1/wechat_skill_operation.mp4) · [Continuous original](https://github.com/tsetwf-cloud/wechat-local-chat/releases/download/tutorial-v0.1.1/wechat_skill_operation_raw.mp4) · [Media release](https://github.com/tsetwf-cloud/wechat-local-chat/releases/tag/tutorial-v0.1.1) · [README](../README.md#english)

### Follow the user workflow

Install the complete Skill and finish account/source setup using the README before trying your own authorized scope. The recording starts after installation and uses an explicitly saved synthetic snapshot. It is a usage tutorial, not a first-run installation or live Windows capture recording.

- **00:00–00:22, state the task.** Specify the contact, dates, desired summary and need for supporting messages. The on-screen Chinese request asks for key topics, confirmed arrangements and open questions using saved records.
- **00:22–00:32, load the Skill.** The actual `skill wechat-local-chat` tool record appears. The user supplies the task rather than entering every underlying command.
- **00:32–01:15, read scoped evidence.** Local tools select the named/time-scoped records and the Agent reads evidence chunks. This illustrates the README privacy and evidence boundary.
- **01:15–02:18, organize and save.** The model generates a report, distinguishes arrangements from unresolved questions, and saves a Markdown file with full message citations.
- **02:18–02:24.50, review the summary.** The actual final answer appears after processing. A plan is not presented as an accomplished event.
- **02:24.50–03:02, ask a follow-up.** Search only for tickets in the same request; do not recapture or broaden the scope.
- **03:02–03:14.48, verify a match.** One message at 10:22 says the science museum is a rainy-day alternative and tickets have not been booked.
- **03:14.48–03:33.12, open the saved report.** Scroll the actual local Markdown to inspect coverage, conclusions and message references. This demonstrates the expected deliverable.

### Recording facts

- Original: 1600×1000, 25 fps, 5328 frames, 213.12 seconds. Captioned: 1600×1120, same frame count and duration, silent.
- Real Hermes CLI running on Linux X11; actual mouse movement, clicks, input and scrolling are driven by AI automation using tmux/xdotool. This is not a human typing and not an animated mock interface.
- The contact Xiaolin and nine in-range messages are purpose-built synthetic records, not anonymized versions of real private chats. Saved-snapshot evidence cutoff: `2026-10-22T14:00:00+08:00`.
- The installed Skill actually runs `collect --snapshot`, `context`, `save-analysis` and `search`. There is no live Windows WeChat acquisition/decryption in this footage.
- Replies and the report were generated during recording by the configured model, not prewritten or replayed. The final displayed report hash matches the saved report; all nine citation IDs match the request's context. The ticket search returns one match at 10:22.
- Post-production adds Chinese callouts below the original frame and yellow focus outlines. There is no crop of the original screen, cut, speed change, substituted reply or inserted success screenshot. Screen and burned-in callouts remain Chinese; this guide supplies English and Chinese explanation rather than claiming an English-captioned video.
- Model labels and some development paths remain visible. Selected terminal text and representative frames were reviewed before publication; no obvious credentials, real contact details or real private chats were found. This is not a forensic audit of every pixel.
- Installation, account configuration, live Windows capture, WAL-only recent messages and media-body processing are not recorded. Linux X11 footage does not validate a native Windows/macOS recording backend.

### Files and rights

This product repository is the primary tutorial destination. [agent-operation-recording](https://github.com/tsetwf-cloud/agent-operation-recording) is the tool used to record and annotate it; that repository retains a labeled production case study, not the primary product guide.

Release assets: `wechat_skill_operation.mp4`, `wechat_skill_operation_raw.mp4`, this bilingual guide as `video_walkthrough.md`, and `SHA256SUMS.txt`. The repository includes the actual preview frame at `docs/media/preview.png` so README readers can identify the workflow without downloading first. Videos are Release assets rather than part of the installed Skill package; the guide is included in `release_files.txt`, while the preview is a repository-only asset.

Project-created media contributions use the MIT License. Hermes, FFmpeg, X11, Xvfb, xterm, tmux and xdotool keep their own licenses; no tool binaries are bundled. The video rasterizes a locally installed Microsoft YaHei font; no font binaries or font license rights are distributed. Application interfaces and names retain third-party rights and do not imply endorsement. See [sources](sources.md).

Frame counts, decoding and hashes verify files, not all business claims or forensic authenticity.

## 中文

[批注视频](https://github.com/tsetwf-cloud/wechat-local-chat/releases/download/tutorial-v0.1.1/wechat_skill_operation.mp4) · [连续原片](https://github.com/tsetwf-cloud/wechat-local-chat/releases/download/tutorial-v0.1.1/wechat_skill_operation_raw.mp4) · [教程素材 Release](https://github.com/tsetwf-cloud/wechat-local-chat/releases/tag/tutorial-v0.1.1) · [README](../README.md#中文)

### 按用户操作路线学习

处理自己的授权数据前，先按 README 安装完整 Skill，并完成账号和源目录配置。视频从安装完成后开始，明确使用合成数据的保存快照。这是使用教程，不是首次安装或 Windows 实时采集录像。

- **00:00–00:22，提出任务。** 说明联系人、日期、总结目标及消息依据要求。画面中的中文请求要求复用保存记录，整理主要话题、已定安排与待确认问题。
- **00:22–00:32，加载 Skill。** 画面出现实际的 `skill wechat-local-chat` 工具记录。用户提出目标，不用输入每条底层命令。
- **00:32–01:15，读取范围内证据。** 本地工具按对象和时间筛选，Agent 读取分块证据，对应 README 的隐私与证据边界。
- **01:15–02:18，整理并保存。** 模型生成报告，区分已定安排和待确认问题，保存带完整消息引用的 Markdown。
- **02:18–02:24.50，查看总结。** 处理结束后展示真实最终答复，不把计划写成已完成事件。
- **02:24.50–03:02，继续追问。** 在同一请求里只搜索门票，不重新采集，也不扩大范围。
- **03:02–03:14.48，核对命中。** 10:22 的一条消息提到科技馆是雨天备选，门票尚未预订。
- **03:14.48–03:33.12，打开保存报告。** 滚动实际本地 Markdown，查看覆盖范围、结论和消息引用，展示最终应得到的产物。

### 录制事实

- 连续原片：1600×1000、25 fps、5328 帧、213.12 秒。批注版：1600×1120，帧数与时长一致，无声。
- 真实 Hermes CLI 运行于 Linux X11；AI 通过 tmux/xdotool 自动操作真实鼠标、点击、输入与滚动，不是人类手工输入，也不是动画模拟界面。
- 联系人小林与九条范围内消息都是专门构造的合成记录，不是真实私聊的匿名改写。保存快照证据截止 `2026-10-22T14:00:00+08:00`。
- 实际调用已安装 Skill 的 `collect --snapshot`、`context`、`save-analysis` 和 `search`。视频中没有实时采集或解密 Windows 微信。
- 回复和报告由已配置模型在录制时实际生成，不是预写或重放。最终展示报告的哈希与保存版本一致，全部九个引用 ID 对应本次上下文；门票搜索命中一条，时间为 10:22。
- 后期在原画面下增加中文批注，并加黄色重点框。未裁切原画面、剪辑、变速、替换回复或插入成功截图。画面和烧录批注仍为中文；本文提供英中说明，不宣称视频已改为英文字幕版。
- 画面保留模型名称和部分开发路径。公开前已检查选定终端文本和代表性画面，未发现明显凭据、真实联系方式或真实私聊；不等于逐像素法证审计。
- 未录安装、账号配置、Windows 实时采集、WAL 近期消息或媒体正文。Linux X11 录像不能证明原生 Windows/macOS 录屏后端完成验收。

### 文件与权利

本产品仓库是教程主要归属。[agent-operation-recording](https://github.com/tsetwf-cloud/agent-operation-recording) 是录制和批注工具，该仓库保留明确标注的制作案例，不替代本项目使用指南。

Release 附件为 `wechat_skill_operation.mp4`、`wechat_skill_operation_raw.mp4`、本文双语副本 `video_walkthrough.md` 和 `SHA256SUMS.txt`。仓库内包含实际截帧 `docs/media/preview.png`，读者无需先下载视频就能辨认流程。视频放在 Release，不塞入安装 Skill 包；本指南加入 `release_files.txt`，预览图属于仓库展示素材，不进入该安装清单。

项目原创视频贡献采用 MIT 许可。Hermes、FFmpeg、X11、Xvfb、xterm、tmux、xdotool 各自保留许可，不随包分发二进制。视频使用本机 Microsoft YaHei 字体渲染为像素，不分发字体文件或转让字体权利。第三方应用界面和名称保留各自权利，不代表背书。见[来源说明](sources.md)。

帧数、解码和哈希只能核对文件，不能证明全部业务结论或法证真实性。
