"""业务规则单元测试：逾期、即将到期、完成率。"""

from datetime import date, timedelta

from app.services import task_service


def task(status="待完成", due="2026-11-15"):
    return {"status": status, "due_date": due}


def test_overdue_boundaries():
    today = date(2026, 11, 15)
    assert task_service.is_overdue(task(due="2026-11-14"), today) is True
    assert task_service.is_overdue(task(due="2026-11-15"), today) is False
    assert task_service.is_overdue(task(due="2026-11-16"), today) is False
    assert task_service.is_overdue(task(status="已完成", due="2026-11-01"), today) is False


def test_due_soon_boundaries():
    today = date(2026, 11, 15)
    assert task_service.is_due_soon(task(due="2026-11-15"), today) is True
    assert task_service.is_due_soon(task(due="2026-11-18"), today) is True
    assert task_service.is_due_soon(task(due="2026-11-19"), today) is False
    assert task_service.is_due_soon(task(due="2026-11-14"), today) is False
    assert task_service.is_due_soon(task(status="已完成", due="2026-11-16"), today) is False


def test_due_soon_uses_today_when_omitted():
    today = date.today()
    assert task_service.is_due_soon(task(due=today.isoformat())) is True
    assert task_service.is_due_soon(task(due=(today + timedelta(days=3)).isoformat())) is True
    assert task_service.is_due_soon(task(due=(today + timedelta(days=4)).isoformat())) is False
