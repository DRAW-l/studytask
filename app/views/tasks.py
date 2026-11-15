"""任务相关路由：首页、增删改查、状态调整。"""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..models import STATUSES, form_values, task_values, validate_task_form
from ..services import task_service as service

bp = Blueprint("tasks", __name__)


def _safe_next(default_endpoint: str = "tasks.index") -> str:
    """只允许站内相对地址，避免开放重定向。"""
    target = request.form.get("next") or ""
    if target.startswith("/") and not target.startswith("//"):
        return target
    return url_for(default_endpoint)


@bp.get("/")
def index():
    filters, warnings = service.normalize_filters(request.args)
    tasks = service.enrich(service.list_tasks(filters))
    stats = service.statistics()
    courses = service.distinct_courses()
    for message in warnings:
        flash(message, "warning")
    return render_template(
        "index.html",
        tasks=tasks,
        stats=stats,
        filters=filters,
        courses=courses,
    )


@bp.get("/tasks/new")
def new():
    return render_template(
        "task_form.html",
        mode="create",
        values=task_values(None),
        errors={},
        task=None,
    )


@bp.post("/tasks")
def create():
    data, errors = validate_task_form(request.form)
    if errors:
        return (
            render_template(
                "task_form.html",
                mode="create",
                values=form_values(request.form),
                errors=errors,
                task=None,
            ),
            400,
        )
    service.create_task(data)
    flash("任务创建成功", "success")
    return redirect(url_for("tasks.index"))


@bp.get("/tasks/<int:task_id>")
def detail(task_id: int):
    task = service.get_task(task_id)
    if task is None:
        abort(404, description="任务不存在或已被删除")
    service.enrich([task])
    return render_template("task_detail.html", task=task)


@bp.get("/tasks/<int:task_id>/edit")
def edit(task_id: int):
    task = service.get_task(task_id)
    if task is None:
        abort(404, description="任务不存在或已被删除")
    return render_template(
        "task_form.html",
        mode="edit",
        values=task_values(task),
        errors={},
        task=task,
    )


@bp.post("/tasks/<int:task_id>")
def update(task_id: int):
    task = service.get_task(task_id)
    if task is None:
        abort(404, description="任务不存在或已被删除")

    data, errors = validate_task_form(request.form)
    if errors:
        return (
            render_template(
                "task_form.html",
                mode="edit",
                values=form_values(request.form),
                errors=errors,
                task=task,
            ),
            400,
        )

    service.update_task(task_id, data, status=(request.form.get("status") or "").strip())
    flash("修改成功", "success")
    return redirect(url_for("tasks.detail", task_id=task_id))


@bp.get("/tasks/<int:task_id>/delete")
def confirm_delete(task_id: int):
    task = service.get_task(task_id)
    if task is None:
        abort(404, description="任务不存在或已被删除")
    return render_template("task_confirm_delete.html", task=task)


@bp.post("/tasks/<int:task_id>/delete")
def destroy(task_id: int):
    task = service.get_task(task_id)
    if task is None:
        abort(404, description="任务不存在或已被删除")
    service.delete_task(task_id)
    flash("删除成功", "success")
    return redirect(url_for("tasks.index"))


@bp.post("/tasks/<int:task_id>/status")
def change_status(task_id: int):
    task = service.get_task(task_id)
    if task is None:
        abort(404, description="任务不存在或已被删除")

    status = (request.form.get("status") or "").strip()
    if status not in STATUSES:
        abort(400, description="状态取值非法")

    service.set_status(task_id, status)
    flash("状态已更新", "success")
    return redirect(_safe_next())
