# AI_DEV_LOG

> 项目：StudyTask 个人学习任务管理系统
> 课程：软件工程 · 实验一
> 记录范围：2026-11-15 与 AI 助手的完整协作过程
> 说明：本文件由 AI 根据对话记录整理，关键判断与验证需由本人复核确认。

## 一、协作概览

本次协作从环境准备开始，依次完成插件安装、资料蒸馏、设计文档撰写、项目编码和界面打磨。整体模式是：**AI 先给出方案或影响范围，本人确认后再执行；AI 产出后用测试或浏览器实际验证**。

- 运行环境：Windows 11 / Python 3.14 / OpenCode 2.3.0（桌面版）
- 项目目录：`D:\SoftwareE\StudyTask`
- 设计依据：《StudyTask 需求规格说明书》（`D:\SoftwareE\附录.docx` 附录 A）
- 最终结果：Flask + SQLite 应用可运行，`pytest` 18 项全部通过

## 二、关键协作事件

| 序号 | 时间 / 版本 | 任务与发给 AI 的关键指令 | AI 产出与问题 | 本人判断 / 验证 |
| --- | --- | --- | --- | --- |
| 1 | 2026-11-15 / 环境准备 | “安装 omo-slim 插件” | 发现本机无 bun、无 `opencode` 命令；创建 `opencode.cmd` 转发桌面版 CLI，用 `npx` 安装 `oh-my-opencode-slim@3.0.7`；因无 OpenAI/Go 订阅，把预设改为 deepseek 模型并重载生效 | 确认 `opencode --version`、`mcp list` 与 explorer 子智能体 ping 均正常，接受 deepseek 预设 |
| 2 | 2026-11-15 / 插件 | “安装 draw.io 插件” | 查明 npm 上的 `opencode-drawio` 是 V1 插件 API，在 OpenCode 2.3 下报 “must export a default definition”；改为官方方案：安装 drawio skill + `@drawio/mcp` | 接受替代方案；验证 MCP 连接成功（8 个工具） |
| 3 | 2026-11-15 / 插件 | “安装蒸馏插件 nt”，提供 GitHub release v0.31.0 地址 | 直连 github.com 超时，改用 gh-proxy 镜像下载 `nt_0.31.0_windows_amd64.zip`，对照官方 checksums 校验 SHA256；安装到 `%LOCALAPPDATA%\Programs\nt`；执行 `nt opencode install`；把 V1 形式 `mcp.nt` 改为 V2 `mcp.servers.nt`；禁用不兼容的 V1 插件 `nt-memory.ts` | 确认 22 个 nt 工具、`/distill` `/learn` `/recall` 可用；接受禁用 V1 插件，接受静态 `nt-rules.md` 注入方案 |
| 4 | 2026-11-15 / 资料蒸馏 | “蒸馏 `D:\SoftwareE\资料库` 内的所有文档资料，先告诉步骤” | 预检 630 个文件 / 373 MB，筛出 83 份文档；给出抽取 → 文档卡 → 主题卡 → 落盘 → 验收五步方案；确认后抽取 186 万字符（Office COM 兜底旧格式），并行 17 批生成 83 张文档卡 + 8 张主题卡 + `INDEX.md` / `REPORT.md` | 选择“输出到 `D:\SoftwareE\Output`”“文档卡 + 主题卡（推荐）”；抽查卡片与索引链接后接受 |
| 5 | 2026-11-15 / 设计文档 | “严格依据附件《StudyTask 需求规格说明书》撰写设计说明书，待确认后再执行” | 解析 `附录.docx`（5,210 字、7 张表），提出 13 章目录和 6 条设计判断；确认后生成 Markdown 与 Word（44 页、3 张图、自动目录）；后补充 6.2 节“状态字段仅编辑页出现” | 确认“docx + Markdown”“不写测试章节”；核对了章节结构与图 3-1/4-1/7-1 的渲染 |
| 6 | 2026-11-15 / 编码 | “根据设计说明书，用 Python + Flask + SQLite 开发项目，源码输出到该文件夹” | 按四层架构实现：应用工厂、sqlite3 数据访问、服务层、9 条路由、6 个模板、错误页；编写 18 个 pytest 用例；修正 `task_service` 相对导入、补 `update_task` 状态字段 | `pytest` 18 项通过；浏览器实测创建任务成功、统计从 4/1/25% 变为 5/1/20%、控制台无错误 |
| 7 | 2026-11-15 / 界面 | “页脚文字居中，整体页面也要居中” | 页脚 `text-align: center`；`.wrap` 显式 `margin-left/right: auto`；`html` 增加 `scrollbar-gutter: stable both-edges`；`body` 改为纵向 flex 保证页脚贴底 | 浏览器实测内容左右各 31px，页脚文字居中 |
| 8 | 2026-11-15 / 界面 | “所有页面均要居中” | 发现表单/确认页的窄卡片（760px）仍靠左，给 `.form-panel` 补 `margin-left/right: auto` | 逐页测量首页、表单、删除确认、404 的左右留白，均相等 |
| 9 | 2026-11-15 / 界面 | “把同一类型字体样式统一” | 引入字体令牌（`--font-sans`、字号、行高）；改为 Microsoft YaHei 优先，统一中英文与数字；表单控件显式字体并统一 40px 高；日期控件内部伪元素也指定同一字族 | 计算样式核对：body/input/select/textarea/date 字族一致，控件高度 40px；18 项测试通过 |
| 10 | 2026-11-15 / 界面 | “状态栏的待完成、更新字体修改成统一样式” | 表格内的状态下拉框从 15px 改为 13px，与「更新」按钮一致；两者统一 32px 高度、行高和字族；表头加 `nowrap` 避免拆行 | 计算样式均为 `13px / Microsoft YaHei / 32px`；测试通过 |
| 11 | 2026-11-15 / 记录 | “将我们之间对话整理成 md 文件，导出到 AI_DEV_LOG.md” | 生成本文件，按实验指导书 D.2 建议格式记录关键协作事件 | 待本人复核后提交 |

## 三、关键决策与人工把关

| 决策点 | AI 建议 | 本人决定 |
| --- | --- | --- |
| 插件模型选择 | 本机没有 OpenAI / OpenCode Go 订阅，默认预设不可用 | 改用 deepseek 模型（v4-pro + flash） |
| draw.io 集成方式 | V1 插件不兼容 V2，改用官方 skill + MCP | 接受 |
| nt 的 V1 记忆插件 | 在 OpenCode 2.3 中无法加载，建议禁用 | 接受，保留 MCP + 技能 + 命令 |
| 蒸馏产出位置 | 建议本地 md + nt 入库 | 指定输出到 `D:\SoftwareE\Output` |
| 蒸馏粒度 | 文档卡 + 主题卡最完整 | 选择文档卡 + 主题卡 |
| 设计说明书交付 | Markdown 便于修改，docx 便于提交 | 两者都要 |
| SRS 缺失的 T1–T10 | 可自拟或等补充 | 不写测试章节，仅保留 A.6 验收对照 |
| 状态字段 | 新建固定“待完成”，编辑页可改 | 接受，并补充到设计文档 6.2 节 |

## 四、问题与修复记录

| 问题 | 现象 | 处理 |
| --- | --- | --- |
| 缺少 bun | `bunx oh-my-opencode-slim install` 无法执行 | 改用 `npx` 安装 |
| 缺少 `opencode` 命令 | 安装器检测失败 | 创建 `%APPDATA%\npm\opencode.cmd` 转发桌面版 CLI |
| GitHub 直连超时 | release 下载失败 | 改用 gh-proxy 镜像，并用官方 `checksums.txt` 校验 SHA256 |
| V1 / V2 插件 API 不兼容 | `nt-memory.ts`、`opencode-drawio` 加载报错 | 禁用 V1 插件，改用官方 skill / MCP 方案 |
| V1 MCP 配置格式 | 安装器写入 `mcp.nt` | 手工改为 V2 的 `mcp.servers.nt`，重载后连接正常 |
| 抽取脚本返回值不一致 | `ValueError: not enough values to unpack` | 统一 `extract_pptx` 返回三元组 |
| 伪 `.pptx` 文件 | `PackageNotFoundError`（实际是 OLE2 旧格式） | 复制为 `.ppt` 后用 Office COM 打开，成功提取 78 页 |
| Word 文档被占用 | 重新导出 docx 时报 `PermissionError` | 暂存为 `docs/_work/设计说明书.new.docx`，待关闭 WPS/Word 后替换 |
| 窄窗口表格横向溢出 | 6 列表格最小宽度 780px | 保留横向滚动，单元格 `nowrap` 避免表头/日期拆行 |

## 五、交付物清单

| 类别 | 位置 |
| --- | --- |
| 应用源码 | `D:\SoftwareE\StudyTask\app\`、`run.py`、`schema.sql` |
| 测试 | `D:\SoftwareE\StudyTask\tests\`（18 个用例） |
| 设计文档 | `D:\SoftwareE\StudyTask\docs\设计说明书.md` / `.docx` |
| 插图 | `D:\SoftwareE\StudyTask\docs\figs\` |
| 运行说明 | `D:\SoftwareE\StudyTask\README.md` |
| 资料蒸馏结果 | `D:\SoftwareE\Output\docs\`（83 篇）、`themes\`（8 篇）、`INDEX.md`、`REPORT.md` |
| 全局配置 | `C:\Users\<用户>\.config\opencode\opencode.json`、`oh-my-opencode-slim.json` |

## 六、反思

1. **先确认再执行**：插件安装、资料蒸馏、设计文档三次都先给出方案和影响范围，确认后再动手，避免了方向性返工。
2. **验证优先于声明**：插件是否生效以 `mcp list`、`/api/agent`、实际请求为准；蒸馏结果用清单、占位符扫描和抽样对照验收。
3. **兼容性是主要风险**：本次两次踩到 OpenCode V1/V2 插件 API 差异；后续引入第三方插件应先确认目标版本。
4. **文档与实现同步**：设计说明书写明“新建固定待完成”，实现即按此执行，并回头补充了 6.2 节说明，避免文档与代码脱节。
5. **尚存局限**：资料蒸馏未覆盖图片/公式内容；`Java设计模式ppt.pdf` 为扫描件，仅有 3,335 字符可提取；设计文档 Word 版还有一处待替换。
