# Verification record · 0.1.1

## English

Local verification date: 2026-10-22. This record describes observed results, not universal compatibility.

## Supported and exercised environment

- Windows x64, logged-in WeChat 4.1.15.56 x64.
- WSL Python 3.12 invoking Windows PowerShell, built-in Framework64 C# compiler, and system winsqlite3.dll.
- Full source copied to a new install directory on the Linux filesystem. Build stages only the named sources into the private Windows build directory; no developer paths are required.
- New private root separate from the legacy implementation. Existing legacy config/data/source were left unchanged.
- Native Windows Python, arbitrary Linux/macOS capture, other WeChat versions and other Agent installers were **not** live-validated.

## Observed results

- 46 Python synthetic tests passed, including source-row reuse without historic evidence revival, pre-existing linked output rejection, refusal of a nonprivate saved-snapshot output root, clipped report coverage, >500-message traversal, name ambiguity, exact time bounds, mutation/hash failure, version rollback, cross-scope rejection, CLI invocation from another working directory and runtime setup/build checks.
- Actual Windows compile and both bundled native fixture executables succeeded: six crypto/capture checks and four security regression checks. These are synthetic, not live key/process compatibility tests.
- Fresh live capture in the separately initialized root succeeded for one previously owner-authorized contact/time interval: three matching messages.
- Keyword search, two evidence chunks, current authorized AI analysis, and local report registration succeeded. Report cited all three scoped message IDs. Personal account, name, message bodies, IDs and paths are excluded from this public record.
- Repeating live capture for the same scope returned added=0, updated=0, unchanged=3, missing=0.
- Main-only provenance, nonzero-page HMAC and SQLite integrity are required by the adapter. WAL is intentionally excluded; the three-message result does not prove complete history.
- Fresh dependency installation succeeded with a configured alternate Python package index after the default download timed out. This is an environment/network issue; no alternate model or chat upload was used.

## Clean local installation

The actual Hermes quarantine → community scan → install implementation installed the complete 31-file release manifest into an isolated test home. The installed file set exactly matched the manifest. All 46 synthetic Python tests passed again from the 0.1.1 installed location with a different working directory. The 0.1.1 installed package also repeated the original live scope successfully (three unchanged messages with unchanged stable IDs), created evidence chunks and registered a hash-verified report with explicit coverage metadata. The earlier 0.1.0 GitHub CLI fetch/install was separately verified and its 30 installer-delivered files matched the repository byte-for-byte; the installer intentionally omits repository-only `.gitignore`.

## 0.1.1 correctness correction

A late synthetic audit reproduced source-row reuse: after a server-ID message disappeared and another message reused its SQLite row, the 0.1.0 current view could incorrectly include the historic payload. Version 0.1.1 selects current records using the same canonical archive identity as storage, not source row coordinates. The regression exercises collect → load → context, verifies added/unchanged/missing counts, retains historic rows in the archive, and leaves prior requests unchanged. Old immutable requests/reports are not retroactively repaired; recollect the authorized scope and regenerate analysis before relying on potentially affected results.

## Installation scanner

Hermes community-source static scan returned SAFE / ALLOWED after narrowing config access to a named environment variable and isolating the test environment mock. No scanner rules, allowlists, ignores or force overrides were changed. Eight medium informational findings remain: explicit subprocess execution for local compiler/helper/test/package installation and the standard Zstandard magic-byte literal. They are visible rather than suppressed. A passing scanner is not a sandbox, runtime no-egress proof or complete native-code security audit.

All private configuration, captures, evidence and reports remain outside the public package. See security.md for retention and processing boundaries.

## 中文

### 验证记录 · 0.1.1

本地验证日期：2026-10-22。本记录描述实际观察到的结果，不代表普遍兼容性。

### 已支持并实际执行过的环境

- Windows x64，已登录的微信 4.1.15.56 x64。
- WSL Python 3.12 调用 Windows PowerShell、内置 Framework64 C# 编译器及系统 winsqlite3.dll。
- 完整源码复制到 Linux 文件系统上的新安装目录。构建时只将指定源码暂存到私有 Windows 构建目录，不需要开发者路径。
- 新私有根目录与旧实现分离。已有的旧配置、数据和源码均未更改。
- 原生 Windows Python、任意 Linux/macOS 采集、其他微信版本以及其他 Agent 安装器均**未经**真实采集验证。

### 观察到的结果

- 46 项 Python 合成测试通过，覆盖源数据行复用时不让历史证据重新进入当前视图、拒绝预先存在的链接型输出、拒绝非私有的已保存快照输出根目录、报告覆盖范围截短、>500 条消息遍历、名称歧义、精确时间边界、变更/哈希失败、版本回滚、跨范围拒绝、从其他工作目录调用 CLI，以及运行环境设置/构建检查。
- 实际 Windows 编译和随包提供的两个原生固定样例可执行程序均成功：六项加密/采集检查、四项安全回归检查。这些使用合成数据，不是真实密钥/进程兼容性测试。
- 在单独初始化的根目录中，对一个此前已获所有者授权的联系人/时间区间进行全新实时采集成功，得到三条匹配消息。
- 关键词检索、两个证据分块、当前已获授权 AI 的分析以及本地报告登记均成功。报告引用了该范围内全部三条消息的 ID。本公开记录不包含个人账号、姓名、消息正文、ID 和路径。
- 对相同范围重复实时采集，返回 added=0, updated=0, unchanged=3, missing=0。
- 适配器要求记录仅主数据库的来源信息，并通过非零页 HMAC 和 SQLite 完整性检查。有意不包含 WAL；三条消息的结果不能证明历史完整。
- 默认下载超时后，使用已配置的备用 Python 软件包索引完成了全新依赖安装。这是环境/网络问题；未使用替代模型，也未上传聊天记录。

### 干净环境中的本地安装

实际 Hermes 隔离区 → 社区扫描 → 安装流程将完整的 31 文件发布清单安装到隔离测试主目录。已安装文件集合与清单完全一致。在不同工作目录下，从 0.1.1 安装位置再次运行，全部 46 项 Python 合成测试通过。0.1.1 安装包还成功重复了原先的实时范围采集（三条消息均未变化，稳定 ID 也未变化），创建证据分块，并登记了带明确覆盖范围元数据、通过哈希验证的报告。此前的 0.1.0 GitHub CLI 获取/安装另行验证过，安装器交付的 30 个文件与仓库逐字节一致；安装器有意省略仅用于仓库的 `.gitignore`。

### 0.1.1 正确性修正

后期合成审计复现了源数据行复用问题：带服务器 ID 的消息消失后，另一条消息复用其 SQLite 行，0.1.0 当前视图可能错误地包含历史内容。0.1.1 使用与存储一致的规范归档身份来选择当前记录，不再依赖源数据行坐标。回归测试覆盖 collect → load → context，验证 added/unchanged/missing 计数，在归档中保留历史行，并保持先前请求不变。旧的不可变请求/报告不会被追溯修复；依赖可能受影响的结果之前，应重新采集已获授权的范围并重新生成分析。

### 安装扫描器

将配置访问收窄到一个指定环境变量，并隔离测试环境模拟后，Hermes 社区来源静态扫描返回 SAFE / ALLOWED。未修改扫描规则、允许列表、忽略项或强制覆盖设置。仍有八项中等级别的信息性发现：为本地编译器、辅助程序、测试和软件包安装显式执行子进程，以及标准 Zstandard 魔数字节字面量。这些发现保持可见，未被屏蔽。扫描通过不等于具备沙箱、运行时无外传证明或完整的原生代码安全审计。

所有私有配置、采集数据、证据和报告均保留在公开包之外。保留与处理边界见 security.md。
