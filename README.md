# 微信本地会话采集与分析 · 一个 Skill

给 AI 一句话：**采集某人的某段聊天，搜索或按要求分析，并给出消息依据。**

一个 Skill 包负责整个流程，不需要另外安装安全 Skill、解密 Skill、HTTP服务或模型插件。所有工具源码随包提供，首次由 Agent 做环境检查、安装一个解码依赖、确认账号和数据库路径、编译本地解密程序。之后不需要修改源码。

> 实验性首版。仅支持 Windows 微信 **4.1.15.56 x64** 的主数据库，不支持任意微信版本。当前本地实测路线以 `references/verification.md` 为准。安装完成不等于所有电脑、微信版本都能采集。

## 安装

Hermes 用户安装整个仓库 Skill，而不是只下载 `SKILL.md`：

```bash
hermes skills install tsetwf-cloud/wechat-local-chat/ --yes
```

源码审查会扫描整个包。不要使用 `--force` 绕过阻止结果；若安装失败，保留错误信息并先审查原因。

安装后在新会话中对 Agent 说：

```text
使用 wechat-local-chat，帮我完成首次配置。
```

Agent 按 `SKILL.md` 引导检查。需要 Windows、已登录的受支持微信、Python 3.11+，以及 Windows 自带 .NET Framework 编译器。WSL 需 Windows 互操作可用。首次只需确认自己的账号标识和准确的 `db_storage` 路径，不需要提供微信密码或密钥。

其他支持 Agent Skills 的工具可以安装完整目录、读取根 `SKILL.md`；必须同时保留 `scripts/`、`tests/`、`requirements.txt` 等支持文件。未声明已经对所有 Agent 平台验证安装。

## 日常使用

```text
采集张三2026年10月1日至10月20日的聊天，整理项目待办，每项给出依据。
查看李四昨天14:00到18:00的聊天，只搜索“交付”，不要分析。
使用上次请求里的记录，区分已确定事项和待确认问题，不重新采集。
```

精确匹配备注、昵称或账号；同名时先确认，不猜首个联系人。日期按北京时间，日期结束值包含当天，具体时刻结束值不包含那个时刻。每次请求有独立编号，旧报告不随新采集覆盖。

## 工具做什么，AI做什么

```text
用户任务 → 一个 Skill 的操作与安全规则
               ↓
本地工具：主库采集/解密 → 名称时间筛选 → 版本归档 → 分块证据
               ↓
当前已授权 AI：按问题分析、逐项引用消息
               ↓
本地工具：校验消息引用 → 保存 Markdown报告和校验元数据
```

采集、解密、检索和保存脚本不会调用模型、发送微信消息或上传聊天。安装依赖可能下载 Python 软件包；如果你使用云端 AI，筛选出的聊天证据仍会进入该 AI 的上下文。**采集本地执行，不代表分析全程离线。**

## 手动命令（进阶）

从任意工作目录调用安装目录中的脚本，替换 `<SKILL_DIR>`、`<PRIVATE_ROOT>` 和示例字段。`python` 表示实际可用的 Python 3.11+；若启动了私有环境，后续使用返回的解释器路径。

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
```

指定独立数据目录时，用 `--root <PRIVATE_ROOT>` 放在子命令之前；所有后续操作使用同一个 root。`collect --snapshot DIRECTORY` 表示明确复用已授权旧快照，不会伪装成刚刚采集。完整命令见 `--help`。

引用格式为 `[消息:完整64位消息ID]`。报告保存会检查引用确实属于本次请求，但不会自动证明分析正确。

## 个人数据与源代码分离

公开包只包含通用代码、规则、空配置模板、许可和合成测试。个人账号和源路径由首次初始化写入仓库外的 `config.json`；默认根基于 Windows 用户 LocalAppData，不依赖开发者电脑目录。解密密钥不作为配置保存。

数据库原始副本、明文快照、聊天归档、请求、证据和报告都留在私有根目录。快照可能包含多个联系人的底层数据，但 AI 只能读取当前明确范围的证据。快照与旧版本会保留，没有自动清理。

## 已知边界

- **不处理 WAL。** 最近提交但仍在 WAL 的消息可能缺失，没有固定等待时长保证完整。
- 不读取图片、语音、视频及附件本体；文件标题不等于文件内容。
- 不恢复已删除消息，不读取手机独有/尚未同步本机记录。
- 逐文件稳定复制不是跨库原子事务快照；SQLite完整性通过不代表聊天历史完整。
- Windows SID匹配不等于微信账号绑定，源账号与目录仍需本人确认。
- 不自动提权、注入、修改微信源库、强制checkpoint、发送消息、定时采集、上传报告或合入Wiki。
- ACL不是加密，不能抵抗管理员或已经失陷的主机。

## 测试

```text
python <SKILL_DIR>/scripts/test.py
python <SKILL_DIR>/scripts/chat.py build --test
```

Python测试只用合成数据，C#测试只用合成密码学/文件样本，不读取真实聊天或进程。真实采集是另一项需账号本人授权的验收。实测范围、数量与结果记录在 [验证说明](references/verification.md)，不公开私聊原文或个人配置。

## 结构与来源

- `SKILL.md`：一个完整任务入口，内含安全约束。
- `scripts/chat.py`：统一命令入口；其余 Python/C# 文件按职责拆分。
- `references/`：架构、隐私、排障、验证与来源说明。
- `tests/`：无个人数据的合成测试。
- `config.example.json`：只含字段的空模板。

详见 [架构](references/architecture.md)、[安全边界](references/security.md)、[排障](references/troubleshooting.md)。本工具与腾讯无隶属关系，只用于本人有权访问的数据。使用前遵守所在地法律、账号与数据处理要求。
