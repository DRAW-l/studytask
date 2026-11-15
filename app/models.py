"""领域常量与表单校验。"""

from datetime import datetime

PRIORITIES = ("高", "中", "低")
STATUSES = ("待完成", "进行中", "已完成")

PRIORITY_ORDER = {name: index for index, name in enumerate(PRIORITIES)}

DATE_FORMAT = "%Y-%m-%d"


def parse_date(value: str):
    """把 YYYY-MM-DD 解析为 date；非法返回 None。"""
    try:
        return datetime.strptime(value.strip(), DATE_FORMAT).date()
    except (ValueError, AttributeError):
        return None


def validate_task_form(form) -> tuple[dict, dict]:
    """校验任务表单。

    返回 (data, errors)。data 为清洗后的字段；errors 为 字段名 -> 提示文案。
    仅校验与任务内容相关的字段，状态由调用方决定。
    """
    errors: dict[str, str] = {}

    title = (form.get("title") or "").strip()
    course = (form.get("course") or "").strip()
    description = (form.get("description") or "").strip()
    due_date = (form.get("due_date") or "").strip()
    priority = (form.get("priority") or "").strip()

    if not title:
        errors["title"] = "任务名称不能为空"
    elif len(title) > 100:
        errors["title"] = "任务名称不能超过 100 字"

    if not course:
        errors["course"] = "所属课程不能为空"
    elif len(course) > 60:
        errors["course"] = "所属课程不能超过 60 字"

    if len(description) > 1000:
        errors["description"] = "任务描述不能超过 1000 字"

    if not due_date:
        errors["due_date"] = "请填写截止日期"
    elif parse_date(due_date) is None:
        errors["due_date"] = "请填写合法的截止日期（YYYY-MM-DD）"

    if priority not in PRIORITIES:
        priority = "中"
        if form.get("priority"):
            errors["priority"] = "优先级取值非法"

    data = {
        "title": title,
        "course": course,
        "description": description,
        "due_date": due_date,
        "priority": priority,
    }
    return data, errors


def form_values(form) -> dict:
    """保留用户输入，供校验失败时回显。"""
    return {
        "title": form.get("title", ""),
        "course": form.get("course", ""),
        "description": form.get("description", ""),
        "due_date": form.get("due_date", ""),
        "priority": form.get("priority") or "中",
        "status": form.get("status") or "待完成",
    }


def task_values(task) -> dict:
    """把数据库行转换为表单初值。"""
    if task is None:
        return {
            "title": "",
            "course": "",
            "description": "",
            "due_date": "",
            "priority": "中",
            "status": "待完成",
        }
    return {
        "title": task["title"],
        "course": task["course"],
        "description": task["description"],
        "due_date": task["due_date"],
        "priority": task["priority"],
        "status": task["status"],
    }
