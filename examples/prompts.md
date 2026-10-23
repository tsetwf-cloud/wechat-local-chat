# Task prompts / 场景提示词

## English

Paste these into an Agent, not a shell. Replace contact/date placeholders with your intended scope. Real-data tasks require your own account, supported environment and completed setup. The Agent must clarify missing scope, not infer authorization for all chats. Cloud AI receives selected evidence under your existing authorization; [privacy](../references/security.md).

### 1. Try without private data

```text
Use wechat-local-chat. Read examples/README.md and run only its synthetic CLI example.
Do not configure my account or collect real WeChat data. Verify output counts and
report citations, and label the report body as prewritten fixture text.
```

Success: 3 selected messages, 1 keyword match, 3 cited IDs, 2 excluded controls. This does not test live capture or AI reasoning.

### 2. First-time real-data setup

```text
Use wechat-local-chat and guide me through first-time setup.
Check the environment first, ask me to confirm my account and exact db_storage directory,
and keep configuration outside the installed package. Do not collect any chat yet.
```

Success: environment/dependency checks and `build --test` pass. Setup alone does not prove a real capture.

### 3. Collect a scoped conversation and organize follow-ups

```text
Use wechat-local-chat. Collect my conversation with <EXACT_CONTACT> from <START_DATE>
to <END_DATE>, UTC+8. Separate agreed actions from unresolved questions, cite the
supporting messages, and save a local Markdown report. Mark an owner or due date
as unknown unless explicitly supported. State snapshot time and coverage limits.
```

Success: new request ID, scoped evidence and saved report path; full citations belong to that request. Calendar end dates are inclusive. Missing records are not proof that an event did not happen.

### 4. Literal keyword lookup, without analysis

```text
Reuse request <REQUEST_ID>; do not recapture. Search only for the literal keyword
<KEYWORD>. Return matching messages with times and full IDs. Do not produce an analysis.
```

Success: reported count matches the returned scoped hits. A zero match means no literal match in this request, not absence from all WeChat history.

### 5. Follow-up using the same evidence

```text
Reuse request <REQUEST_ID>, without recapturing or widening the time/contact scope.
Distinguish confirmed decisions, personal suggestions and unresolved questions.
Cite messages and save a new report; keep the earlier report unchanged.
```

Success: analysis uses the same request; a new report path is returned. Citation existence checks do not prove reasoning correctness.

### 6. Resolve duplicate names safely

```text
The contact name is ambiguous. Show candidate identity metadata only; do not read
other conversations to guess. Wait for me to confirm the exact talker ID.
```

Success: no silent first-match selection. See [troubleshooting](../references/troubleshooting.md) for recovery checks.

## 中文

以下内容粘贴到 Agent，不是终端。将联系人和日期占位符替换为本次范围。真实数据任务需要本人账号、支持环境和已完成的配置。范围缺失时 Agent 应提问，不推定全账号授权。云端 AI 在已有授权边界内接收筛选证据，见[隐私说明](../references/security.md)。

### 1. 不使用私有数据试用

```text
使用 wechat-local-chat，读取 examples/README.md，只运行其中的合成 CLI 示例。
不要配置我的账号或采集真实微信。核对输出计数与报告引用，
明确说明报告正文是预写测试文本。
```

成功判据：选中 3 条、关键词命中 1 条、引用 3 个 ID、排除 2 条对照。不验证实时采集或 AI 推理。

### 2. 真实数据首次配置

```text
使用 wechat-local-chat，帮我完成首次配置。
先检查环境，请我确认本人的账号和准确 db_storage 目录，
配置保存在安装包之外。暂时不要采集任何聊天。
```

成功判据：环境、依赖检查与 `build --test` 通过。仅配置成功不证明真实采集可用。

### 3. 采集指定会话并整理待办

```text
使用 wechat-local-chat，采集我与<准确联系人>从<开始日期>到<结束日期>的聊天，时区 UTC+8。
区分已确定行动与待确认问题，给出消息依据并保存本地 Markdown 报告。
责任人或截止日期没有明确依据时标为未知，说明快照时间与覆盖限制。
```

成功判据：新请求 ID、限定证据和报告路径，完整引用属于本次请求。结束日期包含当天。缺失记录不能证明某事没有发生。

### 4. 只查字面关键词，不分析

```text
复用请求<REQUEST_ID>，不要重新采集。只搜索字面关键词<关键词>，
返回命中消息、时间与完整 ID，不生成分析。
```

成功判据：报告计数等于范围内返回命中数。零命中只表示本次请求没有字面匹配，不代表全部微信历史都没有。

### 5. 使用同一证据继续追问

```text
复用请求<REQUEST_ID>，不重新采集，不扩大联系人与时间范围。
区分已确认决定、个人建议和待确认问题，引用消息并保存新报告，保留旧报告不变。
```

成功判据：使用同一请求，返回新报告路径。引用存在不等于推理正确。

### 6. 安全处理同名联系人

```text
联系人有同名歧义，只展示候选身份元数据，不读取其他会话来猜测。
等我确认准确 talker ID 后再继续。
```

成功判据：没有静默选择第一个匹配项。恢复检查见[排障说明](../references/troubleshooting.md)。
