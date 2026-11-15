# StudyTask 个人学习任务管理系统

单用户、本地运行的学习任务管理 Web 应用，依据 `docs/设计说明书.md` 实现。

- 技术栈：Python 3.10+ / Flask 3.x / SQLite（标准库 `sqlite3`）
- 无登录、无网络依赖，数据保存在本机 `instance/studytask.db`
- 中文界面，支持任务增删改查、组合筛选、状态调整、逾期提醒与完成率统计

## 快速开始

```bash
# 1. 创建并激活虚拟环境（可选）
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动（首次启动自动建库）
python run.py
```

浏览器打开 <http://127.0.0.1:5000>。

数据库文件在首次启动时自动创建于 `instance/studytask.db`；删除该文件后重启即可得到空库。

## 运行测试

```bash
pytest -q
```

测试使用临时数据库，不会影响 `instance/studytask.db`。

## 功能说明

| 需求 | 实现位置 |
| --- | --- |
| FR-01 创建任务 | `POST /tasks`，`app/views/tasks.py`、`app/models.py` |
| FR-02 列表与详情 | `GET /`、`GET /tasks/<id>` |
| FR-03 修改任务 | `GET/POST /tasks/<id>/edit`、`POST /tasks/<id>` |
| FR-04 删除任务 | 确认页 + `POST /tasks/<id>/delete` |
| FR-05 状态调整 | `POST /tasks/<id>/status`、列表行内与详情页按钮 |
| FR-06 组合筛选 | `GET /?course=&status=&priority=` |
| FR-07 逾期与即将到期 | `app/services/task_service.py` 的 `is_overdue` / `is_due_soon` |
| FR-08 首页统计 | 首页统计卡，`statistics()` |
| FR-09 数据持久化 | SQLite 文件，重启不丢失 |
| FR-10 中文界面与错误提示 | 模板文案、表单回显、404/400/405/500 错误页 |

业务规则：

- 逾期：未完成且截止日期早于今天。
- 即将到期：未完成且距今天 0—3 天（含边界）。
- 完成率：已完成数 / 总数 × 100%，四舍五入取整；总数为 0 时显示 0%。
- 默认排序：截止日期升序 → 优先级（高/中/低）→ 创建时间倒序。
- 新建任务固定为“待完成”，状态可在列表或详情页调整。

## 目录结构

```
StudyTask/
├─ run.py                 启动入口
├─ requirements.txt
├─ schema.sql             建表与索引
├─ app/
│  ├─ __init__.py         应用工厂与错误处理
│  ├─ config.py           配置
│  ├─ db.py               SQLite 连接与初始化
│  ├─ models.py           常量与表单校验
│  ├─ services/           业务规则
│  ├─ views/              路由
│  ├─ templates/          Jinja2 模板
│  └─ static/style.css
├─ tests/                 pytest 用例
├─ docs/                  设计说明书（Markdown + Word + 插图）
└─ instance/              运行时数据库（自动生成，不提交）
```

## 设计文档

- `docs/设计说明书.md`
- `docs/设计说明书.docx`
- `docs/实验报告.md` / `docs/实验报告.docx`（3 页）
- `docs/演示PPT.pptx`（12 页演示文稿）

## 已知限制

- 单用户、单进程，不做并发控制与权限隔离。
- 日期判断使用服务器本地日期。
- 不提供分页与数据导入导出。
