"""端到端路由测试：覆盖 FR-01 至 FR-10 的主要路径。"""

from datetime import date

from app import create_app
from app.services import task_service


def make_task(client, **overrides):
    data = {
        "title": "写实验报告",
        "course": "软件工程",
        "description": "完成实验一的设计说明",
        "due_date": "2026-11-20",
        "priority": "中",
    }
    data.update(overrides)
    return client.post("/tasks", data=data, follow_redirects=False)


def test_index_empty(client):
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "还没有任务" in body
    assert "0%" in body


def test_create_task_success(client, app):
    response = make_task(client)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with app.app_context():
        tasks = task_service.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "写实验报告"
    assert tasks[0]["status"] == "待完成"

    page = client.get("/").get_data(as_text=True)
    assert "写实验报告" in page
    assert "任务创建成功" in page


def test_create_task_validation(client, app):
    response = make_task(client, title="", course="", due_date="")
    body = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "任务名称不能为空" in body
    assert "所属课程不能为空" in body
    assert "请填写截止日期" in body

    with app.app_context():
        assert task_service.list_tasks() == []


def test_create_task_invalid_date(client):
    response = make_task(client, due_date="2026-02-30")
    assert response.status_code == 400
    assert "请填写合法的截止日期" in response.get_data(as_text=True)


def test_create_task_title_too_long(client):
    response = make_task(client, title="任" * 101)
    assert response.status_code == 400
    assert "任务名称不能超过 100 字" in response.get_data(as_text=True)


def test_detail_and_404(client):
    make_task(client)
    from app.services import task_service

    with client.application.app_context():
        task_id = task_service.list_tasks()[0]["id"]

    ok = client.get(f"/tasks/{task_id}")
    assert ok.status_code == 200
    assert "写实验报告" in ok.get_data(as_text=True)

    missing = client.get("/tasks/9999")
    assert missing.status_code == 404
    assert "页面不存在" in missing.get_data(as_text=True)


def test_edit_task(client, app):
    make_task(client)
    with app.app_context():
        task_id = task_service.list_tasks()[0]["id"]

    form = client.get(f"/tasks/{task_id}/edit")
    assert form.status_code == 200
    assert "写实验报告" in form.get_data(as_text=True)

    response = client.post(
        f"/tasks/{task_id}",
        data={
            "title": "改写实验报告",
            "course": "软件工程",
            "description": "",
            "due_date": "2026-11-22",
            "priority": "高",
            "status": "进行中",
        },
    )
    assert response.status_code == 302

    detail = client.get(f"/tasks/{task_id}").get_data(as_text=True)
    assert "改写实验报告" in detail
    assert "进行中" in detail
    assert "高" in detail


def test_delete_flow(client, app):
    make_task(client)
    with app.app_context():
        task_id = task_service.list_tasks()[0]["id"]

    confirm = client.get(f"/tasks/{task_id}/delete")
    assert confirm.status_code == 200
    assert "确认删除" in confirm.get_data(as_text=True)

    response = client.post(f"/tasks/{task_id}/delete")
    assert response.status_code == 302
    assert client.get(f"/tasks/{task_id}").status_code == 404

    with app.app_context():
        assert task_service.list_tasks() == []


def test_status_change(client, app):
    make_task(client)
    with app.app_context():
        task_id = task_service.list_tasks()[0]["id"]

    response = client.post(f"/tasks/{task_id}/status", data={"status": "已完成"})
    assert response.status_code == 302

    with app.app_context():
        assert task_service.get_task(task_id)["status"] == "已完成"

    invalid = client.post(f"/tasks/{task_id}/status", data={"status": "未知状态"})
    assert invalid.status_code == 400


def test_filters_combined(client, app):
    make_task(client, title="数据结构作业", course="数据结构")
    make_task(client, title="软件工程作业", course="软件工程")
    make_task(client, title="已完成任务", course="软件工程", priority="高")

    with app.app_context():
        done_id = [t for t in task_service.list_tasks() if t["title"] == "已完成任务"][0]["id"]
    client.post(f"/tasks/{done_id}/status", data={"status": "已完成"})

    page = client.get("/?course=软件工程&status=进行中&priority=中").get_data(as_text=True)
    assert "没有符合筛选条件的任务" in page

    page = client.get("/?course=软件工程&status=已完成").get_data(as_text=True)
    assert "已完成任务" in page
    assert "数据结构作业" not in page


def test_invalid_filter_ignored(client):
    make_task(client)
    page = client.get("/?status=未知").get_data(as_text=True)
    assert "部分筛选条件无效，已忽略" in page
    assert "写实验报告" in page


def test_statistics_rate(client, app):
    make_task(client, title="任务A")
    make_task(client, title="任务B")
    make_task(client, title="任务C")

    with app.app_context():
        ids = [t["id"] for t in task_service.list_tasks()]
    client.post(f"/tasks/{ids[0]}/status", data={"status": "已完成"})
    client.post(f"/tasks/{ids[1]}/status", data={"status": "已完成"})

    page = client.get("/").get_data(as_text=True)
    assert "67%" in page
    assert "任务总数" in page

    with app.app_context():
        stats = task_service.statistics()
    assert stats == {"total": 3, "completed": 2, "rate": 67}


def test_overdue_and_due_soon_flags(client, app):
    today = date.today()
    past = today.replace(year=today.year - 1).isoformat()
    soon = today.fromordinal(today.toordinal() + 2).isoformat()

    make_task(client, title="逾期任务", due_date=past)
    make_task(client, title="即将到期任务", due_date=soon)

    page = client.get("/").get_data(as_text=True)
    assert "逾期" in page
    assert "即将到期" in page


def test_persistence_across_restart(tmp_path):
    database = str(tmp_path / "persist.db")
    first = create_app({"TESTING": True, "SECRET_KEY": "t", "DATABASE": database})
    client = first.test_client()
    make_task(client, title="重启后仍在")

    second = create_app({"TESTING": True, "SECRET_KEY": "t", "DATABASE": database})
    page = second.test_client().get("/").get_data(as_text=True)
    assert "重启后仍在" in page


def test_sorting_by_due_date_then_priority(client):
    make_task(client, title="较晚低优", due_date="2026-12-01", priority="低")
    make_task(client, title="较早高优", due_date="2026-11-01", priority="高")
    make_task(client, title="同日晚优", due_date="2026-12-01", priority="低")

    page = client.get("/").get_data(as_text=True)
    assert page.index("较早高优") < page.index("同日晚优")
