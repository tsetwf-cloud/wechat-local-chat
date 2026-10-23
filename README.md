# WeChat local chat

An AI Skill to search your own WeChat conversations, organize follow-ups and save Markdown reports with message citations.

搜索本人微信聊天、整理待办，生成消息可追溯 Markdown 报告的 AI Skill。

[English](#english) · [中文](#中文) · [Quick start / 快速开始](#install-and-get-your-first-result) · [中文安装](#安装并得到第一个结果) · [Safe example / 安全样本](examples/README.md) · [Task prompts / 场景示例](examples/prompts.md)

## English

### See what you get

**A question about one conversation → scoped evidence → a local report you can check.**

[![Hermes displaying a saved chat summary / Hermes 展示已保存聊天总结](docs/media/preview.png)](https://github.com/tsetwf-cloud/wechat-local-chat/releases/download/tutorial-v0.1.1/wechat_skill_operation.mp4)

The [recorded workflow](references/video_walkthrough.md) uses nine purpose-built synthetic messages: ask for topics, agreed arrangements and open questions, then follow up about tickets. The model generated the report during recording; the follow-up found one message saying tickets were not booked. This demonstrates saved-snapshot analysis, **not live collection or first-time installation**. Chinese screen/callouts; bilingual guide; silent, automated inputs and real waiting time.

For a smaller result you can reproduce without private data, the [synthetic CLI example](examples/README.md) selects three messages, excludes two controls and saves a report with three verified citation IDs. Its report body is explicitly prewritten; no model is called. The video and CLI example demonstrate different layers, not interchangeable evidence.

### Is this for you?

**Fits:** account owners who want to find an earlier decision, search a keyword, extract follow-ups or separate agreements from open questions in a named/time-scoped conversation.

**Does not fit:** other people's accounts; deleted-message recovery; guaranteed newest/full history; image, voice, video or attachment-body recognition; automatic whole-account monitoring or a complete knowledge-base builder.

**Live capture tested:** Windows WeChat **4.1.15.56 x64**, with WSL Python invoking the Windows toolchain. Other WeChat versions fail closed. Native Windows Python and other Agent installers have not been live-validated. Ordinary Linux can run synthetic/already-approved snapshots, not Windows process capture. [Measured verification](references/verification.md).

### What you receive

- **A scoped request ID:** exact contact, UTC+8 interval, snapshot time and live/saved mode.
- **Local searchable records:** versioned SQLite archive, `messages.jsonl` and `messages.md`; analysis evidence is split into JSON chunks without a total 500-message cutoff.
- **When you request analysis:** `analysis_<id>.md` plus a JSON sidecar with report SHA-256, citation IDs and coverage metadata, under `<PRIVATE_ROOT>/business/requests/<REQUEST_ID>/`.
- **Not included:** automatic Wiki ingestion, report publication, sending WeChat messages, scheduling or a new model service. One Skill includes the local helper, safety instructions and workflow; no separate decryption/security Skill is needed.

Citations use `[消息:FULL_64_HEX_ID]`. The script verifies that IDs belong to the request, **not that the AI's reasoning is correct**. New requests/reports do not overwrite old ones. Current generated report headers and default warnings are Chinese; the public instructions are bilingual.

### Install and get your first result

**1. Install the whole Skill.** In a terminal with Hermes installed, from any directory:

```bash
hermes skills install tsetwf-cloud/wechat-local-chat// --yes
```

The final `//` is intentional: it selects the repository-root Skill in Hermes. The installable package is this repository's root, containing `SKILL.md`, `scripts/`, `tests/`, `references/`, `examples/` and `requirements.txt`; do not install only `SKILL.md`. If source review blocks installation, keep the error and review it; do not bypass with `--force`. For other Agents, retain the whole directory and have the Agent read `SKILL.md`; installation/integration is not verified merely because it accepts Markdown Skills.

**2. Try the safe sample first — no account setup required.** From the repository/installed Skill root, in **Linux/WSL Bash**, using Python 3.11+:

```bash
python3 examples/run_demo.py --output "$HOME/wechat-chat-demo-01"
```

Choose a new output directory outside the package with an existing parent. This sample uses the standard library, explicit demo configuration and synthetic SQLite; it never opens WeChat, installs dependencies or calls a model. Success means **3 selected messages, 1 keyword match, 3 cited IDs and 2 excluded controls**. Open the returned `report_path`; the report and sidecar hashes must agree. [Input, output and inspection steps](examples/README.md). This runner is not supported on native Windows and is not proof of live-capture readiness.

**3. Set up your own account only if you want real-data tasks.** Requires Windows x64, your own logged-in WeChat 4.1.15.56 x64, Python 3.11+, the built-in .NET Framework compiler and WSL Windows interop on the tested route. Setup installs pinned `zstandard==0.25.0`; no WeChat password or saved decryption key is required. Read [privacy and coverage](#privacy-and-coverage) first.

In a new Agent conversation, paste this **Agent prompt, not a terminal command**:

```text
Use wechat-local-chat and guide me through first-time setup.
Check the environment, ask me to confirm my account and exact db_storage directory,
and compile/test the helper. Do not collect any chat yet.
```

After successful setup, replace the placeholders and ask:

```text
Collect my conversation with <EXACT_CONTACT> from <START_DATE> to <END_DATE>, UTC+8.
List agreed actions and unresolved questions. Cite supporting messages and save a
local Markdown report. Do not invent owners or deadlines; state coverage limits.
```

Expect a new request ID and report path. Confirm the contact, requested/effective interval, snapshot time and citations. Duplicate names require confirmation. Calendar end dates include that day; exact end times are exclusive. Installation, helper fixtures and real capture are separate checks; no real-data capture is implied by installing.

### More tasks and recovery

[Copyable prompts](examples/prompts.md) cover safe trial, first setup, follow-ups, keyword-only lookup, reuse without recapture and duplicate names.

- **Need only one keyword?** Reuse a request, ask for literal matches and no analysis. A zero match applies only to that request.
- **Helper missing after installation?** Bootstrap the dependency and run `build --test`; confirm fixtures pass and `doctor` reports the helper built.
- **Duplicate contact name?** Review identity metadata, confirm the talker ID, then retry. Never silently take the first match.
- **Report rejected?** Use full IDs from this request, save again, then verify the sidecar and supporting evidence.

[Full troubleshooting: symptom → action → recovery check](references/troubleshooting.md).

### Privacy and coverage

Collection, decryption, search and saving run locally without chat-upload, WeChat-sending or model-service calls in the core scripts. Dependency setup can download a Python package. **With cloud AI, selected evidence still enters that AI's context; local collection does not mean offline analysis.** Use only your own account and data you are authorized to process.

Private storage retains encrypted copies, plaintext snapshots, archives, requests, evidence and reports with no automatic cleanup. A full underlying snapshot may include multiple contacts; the Agent may read only the requested evidence. This is a workflow rule, not a filesystem sandbox. ACLs are not encryption or protection against administrators/compromised hosts.

- Main databases only: WAL-only recent messages may be missing; no fixed waiting time guarantees completeness.
- No media/attachment bodies, deleted-message recovery or phone-only/unsynced history. A filename is not file content.
- Per-file stable copies and SQLite checks prove neither full history nor an atomic cross-database snapshot. Windows SID does not independently bind an account to a source directory; the owner confirms it.
- No automatic elevation, injection, source-database writes, forced checkpoints, sending, scheduling, report uploads or Wiki merging.

**0.1.1 correction:** 0.1.0 could revive historic evidence after SQLite source-row reuse. 0.1.1 selects current records by stable identity. Old requests/reports are not retroactively repaired; recollect only the authorized scope and regenerate potentially affected reports. [Details](references/verification.md).

### Manual route, package and evidence

Use terminal commands from any directory, replacing `<SKILL_DIR>` and approved placeholders. `python` means your actual Python 3.11+ interpreter; after bootstrap use its returned interpreter:

```text
python <SKILL_DIR>/scripts/chat.py doctor
python <SKILL_DIR>/scripts/bootstrap.py --check
python <SKILL_DIR>/scripts/bootstrap.py
python <SKILL_DIR>/scripts/chat.py init --account YOUR_ACCOUNT --source YOUR_DB_STORAGE
python <SKILL_DIR>/scripts/chat.py build --test
python <SKILL_DIR>/scripts/chat.py collect --name NAME --start YYYY-MM-DD --end YYYY-MM-DD --question TASK
python <SKILL_DIR>/scripts/chat.py context --request REQUEST_ID
python <SKILL_DIR>/scripts/chat.py search --request REQUEST_ID --keyword KEYWORD
python <SKILL_DIR>/scripts/chat.py save-analysis --request REQUEST_ID --file DRAFT.md
python <SKILL_DIR>/scripts/chat.py history
python <SKILL_DIR>/scripts/test.py
```

For a separate data root, put `--root <PRIVATE_ROOT>` before each `chat.py` subcommand and pass the same root to bootstrap. `collect --snapshot DIRECTORY` explicitly reuses approved saved data, never fresh collection. See `--help` for syntax.

`release_files.txt` is the explicit package manifest. Required source, references, tests and the safe example travel together; `docs/media/preview.png` is a repository-only showcase asset and videos remain [Release assets](https://github.com/tsetwf-cloud/wechat-local-chat/releases/tag/tutorial-v0.1.1), not runtime dependencies. Personal config and all real data stay outside the package.

Python tests use synthetic data. `build --test` uses synthetic Windows cryptographic/security fixtures, not real process capture. [Verification](references/verification.md) separates historical live checks from this reader-guide/example update. See [architecture](references/architecture.md), [security](references/security.md), [sources](references/sources.md) and [video provenance](references/video_walkthrough.md).

### License

Original code, documentation and project-created media use [MIT](LICENSE). Third-party software, interfaces and fonts retain their own rights; [notices](references/sources.md). Legal texts remain in their original form. Not affiliated with Tencent; follow applicable law and account/data-processing requirements.

## 中文

### 先看会得到什么

**针对一个会话提问 → 得到限定证据 → 保存能核对依据的本地报告。**

[操作视频与预览](#see-what-you-get)使用九条专门构造的合成消息：整理主要话题、已定安排和待确认问题，再追问门票。模型在录制时实际生成报告；追问命中一条“门票尚未预订”的消息。它展示保存快照的分析，**不展示实时采集和首次安装**。画面、批注为中文，配套双语指南；无声、自动输入、保留真实等待。

想先不用私有数据复现结果，可以运行[合成 CLI 样本](examples/README.md)：选中三条、排除两条对照，保存引用三个有效消息 ID 的报告。其正文明确为预写文本，不调用模型。视频与 CLI 样本验证的是不同层面，不能互相替代。

### 适合你吗？

**适合：**本人账号所有者，想在指定联系人、时间范围内找回过去的决定、搜索关键词、提取待办，或区分共识与待确认问题。

**不适合：**他人账号、已删除消息恢复、保证最新或完整历史、图片/语音/视频/附件正文识别、自动全账号监控，或完整个人资料库搭建。

**实时采集实测路线：**Windows 微信 **4.1.15.56 x64**，WSL Python 调用 Windows 工具链。其他微信版本拒绝执行。原生 Windows Python 和其他 Agent 安装器尚未完成实时验收。普通 Linux 可以处理合成或已授权保存快照，不能采集 Windows 进程。[实测记录](references/verification.md)。

### 你会得到什么

- **独立请求 ID：**记录准确联系人、UTC+8 时间窗、快照时间与实时/保存模式。
- **本地可检索记录：**版本化 SQLite 归档、`messages.jsonl`、`messages.md`；分析证据按 JSON 分块，不将全部消息截断为 500 条。
- **要求分析时：**`analysis_<id>.md` 和 JSON 配套文件，含报告 SHA-256、引用 ID、覆盖元数据，位于 `<PRIVATE_ROOT>/business/requests/<REQUEST_ID>/`。
- **不包含：**自动合入 Wiki、发布报告、发送微信消息、定时任务或新模型服务。一个 Skill 已包括本地辅助程序、安全说明与工作流，不必另装解密或安全 Skill。

引用格式为 `[消息:FULL_64_HEX_ID]`。脚本验证 ID 属于本次请求，**不验证 AI 推理是否正确**。新请求和报告不覆盖旧结果。当前自动生成报告的头部和默认警告为中文；公开使用说明为双语。

### 安装并得到第一个结果

**1. 安装完整 Skill。** 已安装 Hermes 时，在任意目录的终端执行：

```bash
hermes skills install tsetwf-cloud/wechat-local-chat// --yes
```

结尾的 `//` 是有意保留的，用于在 Hermes 中选择仓库根目录 Skill。真正安装的包是本仓库根目录，包括 `SKILL.md`、`scripts/`、`tests/`、`references/`、`examples/` 和 `requirements.txt`，不能只下载 `SKILL.md`。源码审查阻止安装时保留错误并检查，不用 `--force` 绕过。其他 Agent 须保留完整目录并读取 `SKILL.md`；能读取 Markdown Skill 不代表其安装和集成已通过验证。

**2. 先试安全样本——不需要账号配置。** 在仓库或安装包根目录的 **Linux/WSL Bash 终端**，使用 Python 3.11+：

```bash
python3 examples/run_demo.py --output "$HOME/wechat-chat-demo-01"
```

输出选择安装包外的新目录，父目录须已存在。此样本使用标准库、显式演示配置和合成 SQLite，不打开微信、不安装依赖、不调用模型。成功判据：**选中 3 条、关键词命中 1 条、引用 3 个 ID、排除 2 条对照**。打开返回的 `report_path`，报告与配套文件哈希应一致。[输入、输出与核对步骤](examples/README.md)。示例运行器不支持原生 Windows，通过不能证明实时采集准备完成。

**3. 需要处理真实数据时，再配置本人账号。** 要求 Windows x64、本人已登录的微信 4.1.15.56 x64、Python 3.11+、Windows 自带 .NET Framework 编译器；实测路线还要求 WSL Windows 互操作。配置会安装固定依赖 `zstandard==0.25.0`，不需要微信密码，不将解密密钥存入配置。先阅读[隐私与覆盖范围](#隐私与覆盖范围)。

在新 Agent 会话中输入以下**提示词，不是终端命令**：

```text
使用 wechat-local-chat，帮我完成首次配置。
先检查环境，请我确认本人的账号和准确 db_storage 目录，再编译测试本地程序。
暂时不要采集任何聊天。
```

配置成功后，替换占位符并提出任务：

```text
采集我与<准确联系人>从<开始日期>到<结束日期>的聊天，时区 UTC+8。
区分已确定行动与待确认问题，引用消息并保存本地 Markdown 报告。
不要虚构责任人或截止日期，说明覆盖限制。
```

你应得到新请求 ID 和报告路径。核对联系人、请求/实际证据区间、快照时间与引用。同名须确认；结束日期包含当天，精确结束时刻不包含该时刻。安装、辅助程序样本测试、真实采集是分别验收的事项，安装不隐含真实采集授权。

### 更多任务与失败恢复

[可复制提示词](examples/prompts.md)覆盖安全试用、首次配置、待办整理、只查关键词、不重采集追问和同名处理。

- **只查一个关键词？** 复用请求，要求字面匹配且不分析。零命中只适用于本次请求。
- **安装后缺少辅助程序？** 初始化依赖并运行 `build --test`，确认样本通过且 `doctor` 显示辅助程序已构建。
- **联系人同名？** 查看身份元数据、确认 talker ID 后重试，不能静默取首项。
- **报告被拒绝？** 使用本次请求的完整 ID，重新保存，再核对配套文件与依据。

[完整排障：症状 → 动作 → 恢复判据](references/troubleshooting.md)。

### 隐私与覆盖范围

采集、解密、检索和保存都在本地执行，核心脚本不上传聊天、不发送微信消息、不调用模型服务。安装依赖可能下载 Python 软件包。**使用云端 AI 时，筛选后的证据仍会进入该 AI 上下文；本地采集不等于离线分析。**只处理本人账号和有权处理的数据。

私有目录保留加密副本、明文快照、归档、请求、证据和报告，不自动清理。底层完整快照可能包含多个联系人，Agent 只能读取本次请求证据；这是工作流规则，不是文件系统沙箱。ACL 不是加密，不能抵抗管理员或已失陷主机。

- 只处理主数据库，近期仍在 WAL 的消息可能缺失，没有固定等待时长保证完整。
- 不读取媒体/附件正文，不恢复删除消息，不包含手机独有或未同步历史；文件名不等于内容。
- 逐文件稳定复制与 SQLite 检查不能证明历史完整或跨库原子快照。Windows SID 不能独立证明账号与源目录对应，须本人确认。
- 不自动提权、注入、写源数据库、强制 checkpoint、发送消息、定时采集、上传报告或合入 Wiki。

**0.1.1 修复提示：**0.1.0 可能在 SQLite 源行复用后将历史消息混入当前证据；0.1.1 按稳定身份选择当前记录。旧请求和报告不追溯修正，应仅重新采集已授权范围并重做可能受影响报告。[详情](references/verification.md)。

### 手动路线、安装包与证据

[上方手动命令](#manual-route-package-and-evidence)可从任意目录执行，替换安装路径及已批准参数。`python` 表示实际 Python 3.11+，bootstrap 后使用其返回的解释器。命令标识符在两种语言下相同。

另选私有目录时，将 `--root <PRIVATE_ROOT>` 放在每个 `chat.py` 子命令前，bootstrap 也指定相同 root。`collect --snapshot DIRECTORY` 明确复用已授权保存数据，不是新采集。完整语法见 `--help`。

`release_files.txt` 为明确安装包清单；必需源码、参考、测试与安全示例一起保留。`docs/media/preview.png` 仅用于仓库展示，视频是 [Release 附件](https://github.com/tsetwf-cloud/wechat-local-chat/releases/tag/tutorial-v0.1.1)，不是运行依赖。个人配置和所有真实数据位于包外。

Python 测试仅用合成数据；`build --test` 是 Windows 密码学与安全样本，不是真实进程采集。[验证记录](references/verification.md)区分历史实时验收与此次读者指南/样本更新。另见[架构](references/architecture.md)、[安全](references/security.md)、[来源](references/sources.md)和[视频来源](references/video_walkthrough.md)。

### 许可

原创代码、文档与原创媒体采用 [MIT](LICENSE)。第三方软件、界面和字体保留自身权利，见[声明](references/sources.md)。生效法律文本保留原文。本项目与腾讯无隶属关系；使用时遵守适用法律及账号、数据处理要求。
