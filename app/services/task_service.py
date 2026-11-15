"""任务业务规则：查询、筛选、统计、逾期判定、增删改。"""

from datetime import date, datetime, timedelta

from ..db import get_db
from ..models import PRIORITIES, STATUSES

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def now_text() -> str:
    return datetime.now().strftime(TIMESTAMP_FORMAT)


# --------------------------------------------------------------------------
# 查询
# --------------------------------------------------------------------------

def list_tasks(filters: dict | None = None) -> list[dict]:
    filters = filters or {}
    clauses = []
    params: list = []

    for field in ("course", "status", "priority"):
        value = filters.get(field)
        if value:
            clauses.append(f"{field} = ?")
            params.append(value)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
        SELECT * FROM tasks
        {where}
        ORDER BY due_date ASC,
                 CASE priority WHEN '高' THEN 0 WHEN '中' THEN 1 ELSE 2 END ASC,
                 created_at DESC
    """
    rows = get_db().execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def get_task(task_id: int) -> dict | None:
    row = get_db().execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row) if row else None


def distinct_courses() -> list[str]:
    rows = get_db().execute("SELECT DISTINCT course FROM tasks ORDER BY course").fetchall()
    return [row["course"] for row in rows]


def statistics() -> dict:
    row = get_db().execute(
        "SELECT COUNT(*) AS total, "
        "COALESCE(SUM(CASE WHEN status = '已完成' THEN 1 ELSE 0 END), 0) AS completed "
        "FROM tasks"
    ).fetchone()
    total = row["total"] or 0
    completed = row["completed"] or 0
    rate = int(completed * 100 / total + 0.5) if total else 0
    return {"total": total, "completed": completed, "rate": rate}


# --------------------------------------------------------------------------
# 写操作
# --------------------------------------------------------------------------

def create_task(data: dict) -> int:
    stamp = now_text()
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO tasks (title, course, description, due_date, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, '待完成', ?, ?)
        """,
        (
            data["title"],
            data["course"],
            data.get("description", ""),
            data["due_date"],
            data["priority"],
            stamp,
            stamp,
        ),
    )
    db.commit()
    return int(cursor.lastrowid)


def update_task(task_id: int, data: dict, status: str | None = None) -> bool:
    db = get_db()
    sets = [
        "title = ?",
        "course = ?",
        "description = ?",
        "due_date = ?",
        "priority = ?",
        "updated_at = ?",
    ]
    params: list = [
        data["title"],
        data["course"],
        data.get("description", ""),
        data["due_date"],
        data["priority"],
        now_text(),
    ]
    if status in STATUSES:
        sets.append("status = ?")
        params.append(status)
    params.append(task_id)

    cursor = db.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id = ?", params)
    db.commit()
    return cursor.rowcount > 0


def delete_task(task_id: int) -> bool:
    db = get_db()
    cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return cursor.rowcount > 0


def set_status(task_id: int, status: str) -> bool:
    if status not in STATUSES:
        return False
    db = get_db()
    cursor = db.execute(
        "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
        (status, now_text(), task_id),
    )
    db.commit()
    return cursor.rowcount > 0


# --------------------------------------------------------------------------
# 逾期与到期
# --------------------------------------------------------------------------

def is_overdue(task: dict, today: date | None = None) -> bool:
    today = today or date.today()
    if task["status"] == "已完成":
        return False
    due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
    return due < today


def is_due_soon(task: dict, today: date | None = None) -> bool:
    today = today or date.today()
    if task["status"] == "已完成":
        return False
    due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
    return 0 <= (due - today).days <= 3


def enrich(tasks: list[dict], today: date | None = None) -> list[dict]:
    today = today or date.today()
    for task in tasks:
        task["overdue"] = is_overdue(task, today)
        task["due_soon"] = is_due_soon(task, today)
    return tasks


# --------------------------------------------------------------------------
# 筛选参数
# --------------------------------------------------------------------------

def normalize_filters(args) -> tuple[dict, list[str]]:
    """把查询参数规范化为筛选条件；非法枚举值忽略并给出提示。"""
    filters: dict[str, str | None] = {"course": None, "status": None, "priority": None}
    warnings: list[str] = []

    course = (args.get("course") or "").strip()
    if course:
        filters["course"] = course

    status = (args.get("status") or "").strip()
    if status:
        if status in STATUSES:
            filters["status"] = status
        else:
            warnings.append("部分筛选条件无效，已忽略")

    priority = (args.get("priority") or "").strip()
    if priority:
        if priority in PRIORITIES:
            filters["priority"] = priority
        else:
            warnings.append("部分筛选条件无效，已忽略")

    return filters, warnings
