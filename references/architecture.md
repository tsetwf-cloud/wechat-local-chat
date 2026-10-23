# Architecture

## English

One installed Skill, one `scripts/chat.py` command entry, modular deterministic implementations. The current AI performs reasoning; it is not a Python background service.

```text
Owner's name/time/task
        ↓
SKILL.md rules and current Agent
        ↓ terminal
chat.py command entry
        ↓
runtime.py: private setup, environment, compiler
run_selected.py: capture adapter
        ↓
native/src/Main.cs + Probe.cs + Runtime.cs
        ↓
private main-db snapshot
        ↓
business.py: exact identity/time, request orchestration
selected_chat.py: shard queries, decode, stable IDs, persistence
        ↓
workflow.py: versions, changes, locks, hashes, atomic current pointer
        ↓
business.py context → selected evidence JSON → current authorized AI
        ↓
local draft → save-analysis citation check → report.md + metadata.json
```

Source code can be installed anywhere and invoked from any working directory. `config.json` and all data live under a separate private root. Use `--root` consistently to override the default; it appears before the subcommand. `config.example.json` contains no real account or source.

Repeated identical account/contact/time scopes share a version series; every request ID pins a generation and its artifact hashes. Different scopes do not overwrite one another. A failed publication does not replace an older successful generation. Later missing rows are not deletion proof. Historical payloads remain in SQLite and prior generations but must not reappear as current evidence when absent from the current capture.

The decryptor accepts one database at a time and can run without any AI. The Skill integrates it with named/time-scoped work and evidence discipline. No separate security Skill, external extraction service, token-authorized local HTTP server, WeChat sending API, cron job or Wiki dependency is required.

## 中文

一个已安装的 Skill、一个 `scripts/chat.py` 命令入口，以及模块化的确定性实现。推理由当前 AI 完成，而不是由 Python 后台服务完成。

```text
所有者指定的名称/时间/任务
        ↓
SKILL.md 规则与当前 Agent
        ↓ terminal
chat.py 命令入口
        ↓
runtime.py：私有环境设置、运行环境、编译器
run_selected.py：采集适配器
        ↓
native/src/Main.cs + Probe.cs + Runtime.cs
        ↓
私有主数据库快照
        ↓
business.py：精确身份/时间筛选、请求编排
selected_chat.py：分片查询、解码、稳定 ID、持久化
        ↓
workflow.py：版本、变更、锁、哈希、原子更新的当前版本指针
        ↓
business.py context → 筛选后的证据 JSON → 当前已获授权的 AI
        ↓
本地草稿 → save-analysis 引用检查 → report.md + metadata.json
```

源码可以安装在任意位置，也可从任意工作目录调用。`config.json` 和所有数据均位于独立的私有根目录。覆盖默认根目录时，必须始终使用 `--root`，并将其放在子命令之前。`config.example.json` 不包含真实账号或源路径。

重复请求相同的账号/联系人/时间范围时，会共用一个版本序列；每个请求 ID 固定指向某一代数据及其产物哈希。不同范围不会相互覆盖。发布新一代产物失败时，不会替换之前成功的版本。后续缺失的行不是删除证据。历史内容保留在 SQLite 和先前版本中，但若当前采集已不包含这些内容，就不得将其重新作为当前证据呈现。

解密器一次接受一个数据库，不依赖任何 AI 也可运行。此 Skill 将解密器与指定名称/时间范围的任务及证据规范结合起来。无需单独的安全 Skill、外部提取服务、基于令牌授权的本地 HTTP 服务器、微信消息发送 API、cron 定时任务或 Wiki 依赖。
