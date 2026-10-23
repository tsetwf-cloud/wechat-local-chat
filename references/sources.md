# Sources and license boundary

## English

The Python business selection/archive/request implementation and this package's orchestration are local implementations. No source or text from the noncommercial `mcncarl/yichen-skills/yichen-wechat-local-vault` was bundled; its Windows detached-snapshot design was surveyed but is not a runtime dependency.

The Config.Cipher runtime layout traversal is adapted from:

- Repository: https://github.com/TANGandXUE/wcdb-key-tool
- Fixed reviewed commit: `79f1b5b92e12c66aa281b4a60a3c478b5f547dfa`
- License: MIT; original notice retained in `THIRD_PARTY_LICENSE.txt`.
- Derived area: `scripts/native/src/Runtime.cs` (memory object discovery/layout); refactored read-only handle use, buffer lifetime, process gates and capture/archive work belong to this package.

The .NET Framework compiler and `winsqlite3.dll` are Windows system components, not redistributed binaries. `zstandard==0.25.0` is obtained separately during setup under its own distribution license; its code/wheels are not vendored here.

SQLite main-database/WAL behavior reference: https://sqlite.org/wal.html . This package intentionally does not merge WAL and makes no fixed-delay completeness claim.

Hermes install/Skill reference: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/ . Installation should retrieve the complete directory including support files, not just the frontmatter document.

### Tutorial media

Project-created video and screenshot contributions use MIT; third-party software, interfaces and fonts retain their rights. The recording uses Hermes, FFmpeg, X11, Xvfb, xterm, tmux and xdotool without redistributing their binaries. Microsoft YaHei is rasterized in the approved recording; no font files or font rights are distributed. The nine messages are purpose-built synthetic records, not anonymized private chats. No source database, key or credential is included. Product names/interfaces do not imply endorsement. See [the bilingual walkthrough](video_walkthrough.md).

## 中文

Python 的业务筛选、归档、请求处理，以及本包的编排均为本地实现。未打包非商用项目 `mcncarl/yichen-skills/yichen-wechat-local-vault` 的任何源码或文本；曾调研其 Windows 分离式快照设计，但它不是运行时依赖。

Config.Cipher 运行时布局遍历改编自：

- 仓库：https://github.com/TANGandXUE/wcdb-key-tool
- 固定审阅提交：`79f1b5b92e12c66aa281b4a60a3c478b5f547dfa`
- 许可证：MIT；原始声明保留在 `THIRD_PARTY_LICENSE.txt` 中。
- 衍生部分：`scripts/native/src/Runtime.cs`（内存对象发现/布局）；重构后的只读句柄使用、缓冲区生命周期、进程准入检查及采集/归档工作属于本包。

.NET Framework 编译器和 `winsqlite3.dll` 是 Windows 系统组件，并未作为二进制文件再分发。`zstandard==0.25.0` 在设置环境时另行获取，遵循其自身的分发许可证；本仓库不内置其代码或 wheel 文件。

SQLite 主数据库/WAL 行为参考：https://sqlite.org/wal.html 。本包有意不合并 WAL，也不声称等待固定时长即可保证完整性。

Hermes 安装/Skill 参考：https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/ 。安装时应获取包含支持文件的完整目录，而不只是带有 frontmatter 的文档。

### 教程素材

项目原创视频和截图贡献使用 MIT，第三方软件、界面和字体保留各自权利。录制使用 Hermes、FFmpeg、X11、Xvfb、xterm、tmux、xdotool，不分发它们的二进制。已认可视频使用 Microsoft YaHei 渲染为像素，不分发字体文件或转让字体权利。九条消息为专门构造的合成记录，不是真实私聊的匿名改写。素材不包含源数据库、密钥或凭据。产品名称和界面不代表背书。见[双语步骤指南](video_walkthrough.md)。
