# Safe first result / 安全的第一个结果

## English

This example exercises the real `scripts/chat.py` CLI with purpose-built synthetic SQLite databases. It never opens WeChat, reads your default private configuration, installs dependencies or calls a model. **The report body is prewritten fixture text, not AI-generated reasoning.** The separate [video](../references/video_walkthrough.md) shows actual Agent/model interaction.

### Input → task → output

The generated `Demo Peer` conversation contains three messages on October 1, 2024 (UTC+8):

- 09:00, peer: “I will send the proposal by Friday.”
- 09:05, self: “I will review it after delivery.”
- 09:10, peer: “Room booking is still unconfirmed.”

Two controls must be excluded: one message from the next day, and one from another conversation. These are invented records, not anonymized private chats. The snapshot cutoff is `2024-10-02T00:00:00+08:00`.

The example selects `Demo Peer` on `2024-10-01`, creates evidence chunks, searches for `booking`, then saves the prewritten body using the actual request's full citation IDs. Expected output:

- `selected_messages`: **3**
- `keyword_matches`: **1**
- `cited_messages`: **3**
- `excluded_controls`: **2**
- `source_mode`: `saved-snapshot`; `wal_included`: `false`; `model_called`: `false`
- A local `analysis_<id>.md` plus JSON sidecar with matching report SHA-256 and citation IDs.

### Run it without real WeChat data

Tested route: Linux/WSL, Python 3.12. Requires Python 3.11+. This text-only example uses the standard library; the full suite and real compressed messages require the pinned `zstandard` dependency. Native Windows is deliberately not supported by this example runner, and passing it does not validate live capture or an Agent installer.

From the **repository/installed Skill root**, run in a **Linux/WSL Bash terminal**. `python3` must resolve to Python 3.11+; choose another interpreter explicitly if needed:

```bash
python3 examples/run_demo.py --output "$HOME/wechat-chat-demo-01"
```

The output directory must not exist, its parent must already exist, and it must be outside the installed package. Choose another new name for another run. The runner rejects existing output rather than deleting or overwriting it. It uses an explicit demo-only private root, never your normal account configuration. It leaves generated synthetic files for inspection; there is no automatic cleanup.

Open `report_path` returned by the command. Confirm the three cited lines, `saved-snapshot` provenance, the effective UTC+8 interval, and no `OUTSIDE_SELECTED_SCOPE` text in the report. The Chinese coverage header is current runtime behavior; it is not localized by this documentation update. Each run creates new request/report IDs, so byte-for-byte output equality is not expected. Use the counts, citation membership and that run's sidecar hash instead.

To have an Agent run only this example, paste into the Agent, not a terminal:

```text
Read wechat-local-chat/SKILL.md and examples/README.md. Run only the synthetic
examples/run_demo.py example into a new directory outside the package.
Do not initialize my account, open WeChat, collect real data or call a new model.
Show the returned counts, report path and whether the report/sidecar hash matches.
Explain that the report body is prewritten, not AI-generated analysis.
```

Adjust the Skill path to its actual installed location; an Agent needs local execution permission. See [task prompts](prompts.md) for real-data tasks after separately authorized setup.

## 中文

此示例使用专门构造的合成 SQLite 数据库，实际调用 `scripts/chat.py`。不会打开微信、读取默认私有配置、安装依赖或调用模型。**报告正文是预写测试文本，不是 AI 推理结果。**另有[操作视频](../references/video_walkthrough.md)展示真实 Agent 和模型交互。

### 输入 → 任务 → 输出

生成的 `Demo Peer` 会话包含 2024 年 10 月 1 日（UTC+8）的三条消息，原文为英文：

- 09:00，对方：“I will send the proposal by Friday.”（周五前发送方案。）
- 09:05，本人：“I will review it after delivery.”（收到后评审。）
- 09:10，对方：“Room booking is still unconfirmed.”（会议室预订尚未确认。）

另外放入两条必须排除的对照消息：次日的一条消息、另一会话的一条消息。这些都是虚构记录，不是真实私聊的匿名改写。快照截止 `2024-10-02T00:00:00+08:00`。

示例筛选 `Demo Peer` 在 `2024-10-01` 的消息、生成证据分块、搜索 `booking`，再使用本次请求的完整引用 ID 保存预写正文。预期结果：

- `selected_messages`：**3**
- `keyword_matches`：**1**
- `cited_messages`：**3**
- `excluded_controls`：**2**
- `source_mode` 为 `saved-snapshot`；`wal_included` 为 `false`；`model_called` 为 `false`。
- 本地 `analysis_<id>.md` 及 JSON 配套文件，报告 SHA-256 与引用 ID 核对一致。

### 不使用真实微信数据运行

实测路线：Linux/WSL、Python 3.12，要求 Python 3.11+。此纯文本样本仅使用标准库；完整测试和真实压缩消息需要固定版本的 `zstandard`。此示例运行器明确不支持原生 Windows；通过不能证明实时采集或某个 Agent 安装器可用。

在**仓库或已安装 Skill 根目录**的 **Linux/WSL Bash 终端**执行。`python3` 必须对应 Python 3.11+，否则明确改用其他解释器：

```bash
python3 examples/run_demo.py --output "$HOME/wechat-chat-demo-01"
```

输出目录必须尚不存在、父目录已存在，并位于安装包之外。再次运行时另取新目录名。运行器拒绝已有输出，不删除或覆盖。它使用显式指定的演示私有根目录，不读取日常账号配置。生成的合成文件保留供核对，不自动清理。

打开命令返回的 `report_path`，确认三条带引用正文、`saved-snapshot` 来源、实际 UTC+8 时间窗，以及报告没有 `OUTSIDE_SELECTED_SCOPE` 文本。中文覆盖范围头是当前运行时行为，本次文档更新不将它多语化。每次运行都会生成新请求和报告 ID，因此不比较两次文件字节；检查计数、引用归属与本次配套文件哈希。

让 Agent 仅运行此示例时，向 Agent 提问，不是在终端执行：

```text
读取 wechat-local-chat/SKILL.md 和 examples/README.md。
只运行合成 examples/run_demo.py 示例，输出到安装包外的新目录。
不要初始化我的账号、打开微信、采集真实数据或调用新模型。
给出返回计数、报告路径，以及报告和配套文件哈希是否一致。
说明报告正文是预写样本，不是 AI 生成的分析。
```

按实际安装位置调整 Skill 路径，Agent 需要本地执行权限。另行授权并完成真实账号配置后，见[场景提示词](prompts.md)。
