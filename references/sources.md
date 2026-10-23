# 来源与许可证边界

## 本项目实现与参考设计

Python 的业务筛选、归档、请求处理，以及本包的编排均为本地实现。

项目曾调研非商用项目 `mcncarl/yichen-skills/yichen-wechat-local-vault` 的 Windows 分离式快照设计，但未打包它的任何源码或文本，也不将它作为运行时依赖。

## 改编的第三方代码

Config.Cipher 运行时布局遍历改编自以下项目：

- 仓库：https://github.com/TANGandXUE/wcdb-key-tool
- 固定审阅提交：`79f1b5b92e12c66aa281b4a60a3c478b5f547dfa`
- 许可证：MIT。原始声明保留在 `THIRD_PARTY_LICENSE.txt` 中。
- 衍生部分：`scripts/native/src/Runtime.cs` 中的内存对象发现与布局遍历。

重构后的只读句柄使用、缓冲区生命周期、进程准入检查，以及采集和归档工作属于本包。

## 系统组件与另行安装的依赖

.NET Framework 编译器和 `winsqlite3.dll` 是 Windows 系统组件，本项目不随包分发它们的二进制文件。

`zstandard==0.25.0` 在设置环境时另行获取，遵循其自身的分发许可证。本仓库不内置它的代码或 wheel 文件。

## 技术参考

- [SQLite 主数据库与 WAL 行为](https://sqlite.org/wal.html)：本包有意不合并 WAL，也不声称等待固定时长就能保证消息完整。
- [Hermes 的 Skill 安装说明](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)：安装时应获取包含支持文件的完整目录，不能只获取带有文档头部元数据的入口文件。

## 教程视频与截图

项目原创的视频和截图贡献使用 MIT 许可证。第三方软件、界面和字体保留各自权利，项目许可证不代替这些权利。

录制使用 Hermes、FFmpeg、X11、Xvfb、xterm、tmux 和 xdotool，但不分发它们的二进制文件。已认可的视频使用 Microsoft YaHei（微软雅黑）渲染为像素，不分发字体文件，也不转让字体权利。

视频中的九条消息是专门构造的合成记录，不是真实私聊的匿名改写。素材不包含源数据库、密钥或凭据。出现产品名称和界面不代表相关产品为本项目背书。

具体演示内容见[视频步骤与录制说明](video_walkthrough.md)。
