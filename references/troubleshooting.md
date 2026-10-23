# Troubleshooting

## English

### Check recovery, not just a retry

- **Helper missing →** finish dependency setup and `build --test` → require successful fixture exits and `doctor` showing `helper_built=true`; this is not a live-capture test.
- **Duplicate contact →** confirm candidate identity metadata and retry with `--talker` → inspect the new request's exact talker and interval before reading evidence.
- **Report rejected →** use full citation IDs from this request and save again → require `save-analysis` success, matching report/sidecar SHA-256 and evidence supporting the claims.
- **Synthetic demo output exists →** choose a new output directory outside the package → require 3 selected messages, 1 keyword hit, 3 citations and 2 exclusions. Never delete or overwrite old output to make it pass.
- **Zero matches →** inspect the interval and snapshot time without broadening scope → a verified zero count is an honest result, not proof of absence from all history.

### Other symptoms

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

## 中文

### 核对恢复，不只重试

- **缺少辅助程序 →** 完成依赖配置和 `build --test` → 样本成功退出，且 `doctor` 显示 `helper_built=true`；不代表实时采集已测。
- **联系人同名 →** 确认候选身份元数据，使用 `--talker` 重试 → 读证据前核对新请求的准确 talker 与区间。
- **报告被拒绝 →** 改用本次请求的完整引用 ID 并重新保存 → `save-analysis` 成功，报告与配套文件 SHA-256 一致，依据确实支持结论。
- **合成样本输出已存在 →** 另选包外新目录 → 要求选中 3 条、命中 1 条、引用 3 个 ID、排除 2 条；不能为通过而删除或覆盖旧输出。
- **零命中 →** 检查区间与快照时间，不扩大范围 → 核实零计数就是诚实结果，不证明全部历史都不存在。

### 其他症状

- **安装成功但缺少辅助程序：** Skill 安装只复制代码和说明，不包含预编译 EXE 或 Python 依赖。让 Agent 初始化依赖，确认一个账号及其源路径，然后运行 `build --test`。无需修改源码。
- **不支持的微信版本：** 仅接受 4.1.15.56 x64。不得修改版本保护来强行适配其他构建版本。新版本需要经过单独验证的内存/数据库结构适配器。
- **WSL 无法使用 Windows 互操作：** 采集需要访问 Windows 进程和系统编译器。检查互操作功能及 Windows PATH；普通 Linux 只能处理已获授权的分离式快照。不得通过上传数据库来补救。
- **没有合适的 Python：** 安装 Python 3.11+，或使用已有的受管理解释器。在某些 Linux 系统上，venv/ensurepip 是单独的操作系统组件；应采用常规依赖管理流程，不要使用与解释器不匹配的系统 pip。`zstandard==0.25.0` 是唯一的第三方 Python 依赖。
- **存在多个 Weixin 主进程：** 停止操作，确认目标已登录账号/进程。程序不得猜测，也不得全部采集。
- **拒绝访问 / 私有 ACL 检查失败 / 重解析路径：** 使用自己拥有且可信的本地输出父目录；不得自动提权或关闭保护。绝不为了让测试通过而覆盖其他目录的权限。
- **采集期间数据库发生变化：** 最多重试三次；若仍不稳定，停止并报告失败。未经许可，不得强制执行检查点或关闭微信。
- **找不到确切名称或存在重名：** 只展示返回的身份元数据，待所有者确认后使用 `--talker`。名称筛选采用精确匹配，不是模糊匹配。
- **没有消息：** 检查 UTC+8 时间窗口和采集时间戳。可能缺少仅在手机上的记录和 WAL 内容；文件新旧不能证明完整性。不得静默扩大联系人或时间范围。
- **报告被拒绝：** 使用本次请求中的 `[消息:full_64_hex_id]` 引用，不得使用其他请求的 ID 或缩短的 ID。证据非空时，至少需要一条引用。Agent 仍须判断每项主张是否得到证据支持。
- **哈希不匹配：** 不得编辑清单来绕过检查。保留旧数据，报告损坏情况，并仅在所有者授权范围内重新采集。
- **已有私有配置：** 初始化不会覆盖它。为另行授权的账号/设置使用新的私有根目录，旧归档保持不变。使用不同根目录时，必须在每个子命令之前指定该根目录，包括 bootstrap。
