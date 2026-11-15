"""Generate the figures used by the StudyTask design document."""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Circle

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(r"D:\SoftwareE\StudyTask\docs\figs")
OUT.mkdir(parents=True, exist_ok=True)

EDGE = "#333333"
FILL = "#F5F7FA"
ACCENT = "#E8EEF7"


def box(ax, x, y, w, h, text, fill=FILL, fontsize=11, bold=False):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=1.4,
            edgecolor=EDGE,
            facecolor=fill,
        )
    )
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight="bold" if bold else "normal",
        color="#1A1A1A",
        wrap=True,
    )


def arrow(ax, p1, p2, style="-|>", lw=1.4, ls="-"):
    ax.add_patch(
        FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14, linewidth=lw, linestyle=ls, color=EDGE)
    )


def fig_arch():
    fig, ax = plt.subplots(figsize=(9.6, 6.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    layers = [
        ("表现层（Jinja2 模板）\n首页/列表·新建/编辑·详情·错误页", 7.9),
        ("控制层（Flask Blueprint）\n路由分发·请求参数解析·表单校验", 6.1),
        ("服务层（TaskService）\n逾期/到期判定·统计·组合筛选·状态变更", 4.3),
        ("数据访问层（DAO）\n参数化 SQL·行记录映射·建库/建表", 2.5),
        ("数据层（SQLite 文件 studytask.db）", 1.0),
    ]
    for text, y in layers:
        box(ax, 0.9, y, 8.2, 1.25, text, fill=ACCENT if y == 4.3 else FILL)

    for y_from, y_to in zip([7.9, 6.1, 4.3, 2.5], [7.35, 5.55, 3.75, 2.25]):
        arrow(ax, (5.0, y_from), (5.0, y_to))

    ax.text(5.0, 9.55, "浏览器（桌面端，无登录）", ha="center", va="center", fontsize=11)
    arrow(ax, (5.0, 9.3), (5.0, 9.2), style="-|>")

    fig.tight_layout()
    fig.savefig(OUT / "arch.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_state():
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    nodes = {"待完成": (2.0, 3.0), "进行中": (5.0, 3.0), "已完成": (8.0, 3.0)}
    for name, (x, y) in nodes.items():
        ax.add_patch(Circle((x, y), 0.72, facecolor=ACCENT, edgecolor=EDGE, linewidth=1.4))
        ax.text(x, y, name, ha="center", va="center", fontsize=11)

    ax.add_patch(Circle((0.55, 3.0), 0.12, facecolor="#333333", edgecolor="#333333"))
    arrow(ax, (0.7, 3.0), (1.26, 3.0))
    ax.text(0.95, 3.35, "创建", fontsize=9, ha="center")

    pairs = [("待完成", "进行中", 0.3), ("进行中", "已完成", 0.3), ("待完成", "已完成", 0.95)]
    for a, b, bend in pairs:
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        ax.add_patch(
            FancyArrowPatch(
                (x1 + 0.72, y1 + 0.15),
                (x2 - 0.72, y2 + 0.15),
                connectionstyle=f"arc3,rad=-{bend}",
                arrowstyle="-|>",
                mutation_scale=13,
                linewidth=1.3,
                color=EDGE,
            )
        )
        ax.add_patch(
            FancyArrowPatch(
                (x2 - 0.72, y2 - 0.15),
                (x1 + 0.72, y1 - 0.15),
                connectionstyle=f"arc3,rad=-{bend}",
                arrowstyle="-|>",
                mutation_scale=13,
                linewidth=1.3,
                color=EDGE,
            )
        )

    ax.text(5.0, 3.0, "", ha="center")
    fig.tight_layout()
    fig.savefig(OUT / "state.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_flow():
    fig, ax = plt.subplots(figsize=(7.6, 8.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis("off")

    box(ax, 3.2, 10.6, 3.6, 0.9, "打开新建任务表单", fontsize=10)
    box(ax, 3.2, 9.1, 3.6, 0.9, "填写并提交 POST /tasks", fontsize=10)
    box(ax, 3.2, 7.6, 3.6, 0.9, "服务端校验字段", fontsize=10)

    ax.add_patch(
        Polygon(
            [[5.0, 6.85], [7.1, 5.95], [5.0, 5.05], [2.9, 5.95]],
            closed=True,
            facecolor=ACCENT,
            edgecolor=EDGE,
            linewidth=1.4,
        )
    )
    ax.text(5.0, 5.95, "校验通过？", ha="center", va="center", fontsize=10)

    box(ax, 6.6, 3.9, 2.9, 0.9, "写入数据库\nstatus=待完成", fontsize=9.5)
    box(ax, 0.5, 3.9, 2.9, 0.9, "回显错误信息\n保留已填内容", fontsize=9.5)
    box(ax, 6.6, 2.3, 2.9, 0.9, "重定向到列表页\n（PRG）", fontsize=9.5)
    box(ax, 0.5, 2.3, 2.9, 0.9, "返回表单页（400）", fontsize=9.5)
    box(ax, 6.6, 0.8, 2.9, 0.8, "显示成功提示", fontsize=9.5)

    arrow(ax, (5.0, 10.6), (5.0, 10.0))
    arrow(ax, (5.0, 9.1), (5.0, 8.5))
    arrow(ax, (5.0, 7.6), (5.0, 6.85))
    arrow(ax, (7.1, 5.95), (8.05, 4.8))
    ax.text(7.8, 5.7, "是", fontsize=9)
    arrow(ax, (2.9, 5.95), (1.95, 4.8))
    ax.text(2.15, 5.7, "否", fontsize=9)
    arrow(ax, (8.05, 3.9), (8.05, 3.2))
    arrow(ax, (1.95, 3.9), (1.95, 3.2))
    arrow(ax, (8.05, 2.3), (8.05, 1.6))

    ax.text(5.0, 0.25, "开始于新建表单，结束于列表页的成功提示", ha="center", fontsize=9, color="#666666")
    fig.tight_layout()
    fig.savefig(OUT / "create-flow.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    fig_arch()
    fig_state()
    fig_flow()
    for p in sorted(OUT.glob("*.png")):
        print(p.name, p.stat().st_size)
