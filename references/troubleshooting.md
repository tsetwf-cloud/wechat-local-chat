# Troubleshooting

- **Install succeeds but helper missing:** Skill installation copies code/instructions, not a precompiled EXE or Python dependency. Let the Agent bootstrap the dependency, confirm one account/source, and run `build --test`. No source editing is needed.
- **Unsupported WeChat:** only 4.1.15.56 x64 is accepted. Do not edit the version guard to force another build. New versions need a separately validated memory/schema adapter.
- **WSL Windows interop unavailable:** capture requires the Windows process and system compiler. Check interop and Windows PATH; ordinary Linux can only process approved detached snapshots. Do not upload the database to compensate.
- **No suitable Python:** install Python 3.11+ or use an existing managed interpreter. On some Linux systems venv/ensurepip is a separate OS component; use your normal dependency-management procedure, not mismatched system pip. `zstandard==0.25.0` is the only third-party Python dependency.
- **Multiple Weixin main processes:** stop and confirm the intended logged-in account/process. The program must not guess or gather all of them.
- **Access denied / private ACL failure / reparse path:** use an owned, trusted local output parent; do not elevate or disable protections automatically. Never overwrite another directory's permissions to make a test pass.
- **Database changed during capture:** retry up to three times; if still unstable stop and report failure. Do not force a checkpoint or close WeChat without permission.
- **No exact name or duplicate names:** show the returned identity metadata only, then use `--talker` after owner confirmation. Name selection is exact, not fuzzy.
- **No messages:** check the UTC+8 window and captured-at timestamp. Phone-only records and WAL may be absent; file age does not prove completeness. Do not broaden contacts/time silently.
- **Report rejected:** use `[消息:full_64_hex_id]` citations from this request, not another request or shortened IDs. At least one citation is needed for nonempty evidence. The Agent must still assess whether each claim is supported.
- **Hashes mismatch:** do not edit manifests to bypass. Keep the old data, report the corruption and recapture only within the owner's scope.
- **Private config exists:** initialization does not overwrite it. Use a new private root for a separately authorized account/setup; old archives stay intact. A different root must be supplied before every subcommand, including bootstrap.
