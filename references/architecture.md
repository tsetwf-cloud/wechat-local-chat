# Architecture

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
