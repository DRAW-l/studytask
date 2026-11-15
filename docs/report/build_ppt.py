"""Build the StudyTask demo deck."""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu

ROOT = Path(r"D:\SoftwareE\StudyTask")
DOCS = ROOT / "docs"
SHOTS = DOCS / "report" / "shots"
OUT = DOCS / "演示PPT.pptx"

W, H = 13.333, 7.5
BLUE = RGBColor(0x25, 0x63, 0xEB)
BLUE_DARK = RGBColor(0x1D, 0x4E, 0xD8)
LIGHT = RGBColor(0xE8, 0xEE, 0xF7)
INK = RGBColor(0x1F, 0x29, 0x37)
GRAY = RGBColor(0x6B, 0x72, 0x80)
RED = RGBColor(0xDC, 0x26, 0x26)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PALE = RGBColor(0xF5, 0xF7, 0xFA)
FONT = "Microsoft YaHei"


def set_font(run, size=16, bold=False, color=INK, font=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set("typeface", font)


def textbox(slide, x, y, w, h, text="", size=16, bold=False, color=INK,
            align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.2):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    for i, line in enumerate(str(text).split("\n")):
        if i:
            p = tf.add_paragraph()
            p.alignment = align
            p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        set_font(r, size, bold, color)
    return tb


def add_bullets(slide, x, y, w, h, items, size=16, color=INK, gap=10):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    first = True
    for item in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(gap)
        p.line_spacing = 1.25
        if isinstance(item, tuple) and len(item) == 2:
            head, rest = item
            r = p.add_run(); r.text = "• " + head
            set_font(r, size, True, color)
            r2 = p.add_run(); r2.text = rest
            set_font(r2, size, False, color)
        else:
            r = p.add_run(); r.text = "• " + item
            set_font(r, size, False, color)


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(1)
    s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            s.adjustments[0] = radius
        except Exception:
            pass
    return s


def add_slide(prs, title, kicker=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(W), Inches(0.09))
    bar.fill.solid(); bar.fill.fore_color.rgb = BLUE
    bar.line.fill.background()
    textbox(slide, 0.65, 0.45, 11.8, 0.7, title, size=28, bold=True)
    if kicker:
        textbox(slide, 0.67, 1.08, 11.8, 0.35, kicker, size=12, color=GRAY)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.66), Inches(1.5), Inches(0.7), Inches(0.05))
    line.fill.solid(); line.fill.fore_color.rgb = BLUE
    line.line.fill.background()
    add_footer(slide, len(prs.slides))
    return slide


def add_footer(slide, number):
    textbox(slide, 0.65, 7.1, 5, 0.25, "StudyTask · 实验一", size=9, color=GRAY)
    textbox(slide, 12.1, 7.1, 0.6, 0.25, str(number), size=9, color=GRAY, align=PP_ALIGN.RIGHT)


def picture(slide, path, x, y, w=None, h=None, caption=None):
    kw = {}
    if w: kw["width"] = Inches(w)
    if h: kw["height"] = Inches(h)
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kw)
    if caption:
        textbox(slide, x, y + pic.height.inches + 0.1, pic.width.inches, 0.3, caption,
                size=10, color=GRAY, align=PP_ALIGN.CENTER)
    return pic


def table(slide, x, y, w, h, rows, col_widths=None, font_size=12):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(h))
    tbl = shape.table
    tbl.rows[0].height = Inches(0.4)
    for i in range(1, len(tbl.rows)):
        tbl.rows[i].height = Inches(0.38)
    if col_widths:
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Inches(cw)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.text = ""
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            p = cell.text_frame.paragraphs[0]
            r = p.add_run(); r.text = str(val)
            if ri == 0:
                set_font(r, font_size, True, WHITE)
                cell.fill.solid(); cell.fill.fore_color.rgb = BLUE
            else:
                set_font(r, font_size, False, INK)
                cell.fill.solid(); cell.fill.fore_color.rgb = WHITE if ri % 2 else PALE
    return tbl


def card(slide, x, y, w, h, title, body):
    rect(slide, x, y, w, h, LIGHT, RGBColor(0xD6, 0xE2, 0xF5))
    rect(slide, x, y, 0.07, h, BLUE, shape=MSO_SHAPE.RECTANGLE)
    textbox(slide, x + 0.28, y + 0.2, w - 0.45, 0.4, title, size=16, bold=True, color=BLUE_DARK)
    textbox(slide, x + 0.28, y + 0.72, w - 0.5, h - 0.9, body, size=12.5, color=INK, line_spacing=1.35)


def code_block(slide, x, y, w, h, lines, size=11):
    box = rect(slide, x, y, w, h, RGBColor(0xF7, 0xF7, 0xF7), RGBColor(0xE5, 0xE7, 0xEB))
    tf = box.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.18); tf.margin_right = Inches(0.12)
    tf.margin_top = Inches(0.16); tf.margin_bottom = Inches(0.1)
    first = True
    for ln in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = 1.1
        r = p.add_run(); r.text = ln
        set_font(r, size, False, RGBColor(0x11, 0x18, 0x27), font="Consolas")
        r._r.get_or_add_rPr().find(qn("a:ea")).set("typeface", FONT)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    prs.core_properties.title = "StudyTask 个人学习任务管理系统 · 演示"
    prs.core_properties.author = ""

    # 1 cover
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0.0, 0.0, W, H, PALE, shape=MSO_SHAPE.RECTANGLE)
    rect(s, 0.0, 0.0, 0.18, H, BLUE, shape=MSO_SHAPE.RECTANGLE)
    textbox(s, 0.9, 1.55, 11.6, 0.5, "软件工程 · 实验一", size=14, color=BLUE, bold=True)
    textbox(s, 0.9, 2.0, 11.6, 1.1, "StudyTask 个人学习任务管理系统", size=40, bold=True)
    textbox(s, 0.9, 3.1, 11.6, 0.6, "设计与实现演示", size=24, color=GRAY)
    line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.92), Inches(3.95), Inches(3.2), Inches(0.05))
    line.fill.solid(); line.fill.fore_color.rgb = BLUE; line.line.fill.background()
    textbox(s, 0.9, 4.2, 8, 0.4, "Python · Flask · SQLite", size=16, color=INK)
    textbox(s, 0.9, 4.65, 8, 0.4, "演示日期：2026-11-15", size=12, color=GRAY)
    textbox(s, 0.9, 5.05, 8, 0.4, "班级：__________　学号：__________　姓名：__________", size=12, color=GRAY)

    # 2 agenda
    s = add_slide(prs, "汇报提纲", "DEMO AGENDA")
    items = [
        ("01", "项目背景与需求范围", "单用户本地任务管理，覆盖 FR-01—FR-10"),
        ("02", "技术方案与系统架构", "Flask + SQLite 四层结构"),
        ("03", "功能演示", "列表、详情、新建与校验、删除确认"),
        ("04", "关键实现与测试结果", "逾期规则、完成率、18 项 pytest"),
        ("05", "问题与反思", "校验重复、误删风险、文档与实现同步"),
    ]
    y = 1.85
    for num, title, desc in items:
        textbox(s, 0.75, y, 0.9, 0.5, num, size=20, bold=True, color=BLUE)
        textbox(s, 1.65, y - 0.03, 10.8, 0.45, title, size=18, bold=True)
        textbox(s, 1.65, y + 0.38, 10.8, 0.35, desc, size=12, color=GRAY)
        y += 1.02

    # 3 scope
    s = add_slide(prs, "项目背景与需求范围", "依据《StudyTask 需求规格说明书》附录 A")
    add_bullets(s, 0.7, 1.85, 6.6, 4.6, [
        ("定位：", "单个在校大学生，本地浏览器访问，无登录、无网络"),
        ("功能：", "FR-01—FR-10 全部实现"),
        ("数据：", "任务名称、课程、描述、截止日期、优先级、状态"),
        ("质量：", "200 条任务可正常操作；重启数据不丢"),
        ("交付：", "源码、requirements.txt、测试、README、设计文档"),
    ], size=15, gap=12)
    rect(s, 7.7, 1.85, 4.9, 4.55, LIGHT, RGBColor(0xD6, 0xE2, 0xF5))
    textbox(s, 8.0, 2.05, 4.3, 0.4, "范围外（SRS A.5）", size=15, bold=True, color=BLUE_DARK)
    add_bullets(s, 8.0, 2.55, 4.3, 3.6, [
        "用户注册与多用户权限",
        "共享任务、邮件/短信通知",
        "第三方日历同步、移动 App",
        "云部署与复杂功能扩展",
    ], size=13, gap=10)

    # 4 architecture
    s = add_slide(prs, "技术方案与系统架构", "四层结构，职责单一")
    picture(s, DOCS / "figs" / "arch.png", 0.6, 1.75, w=6.9, caption="图 1 系统逻辑架构")
    add_bullets(s, 8.0, 1.9, 4.6, 4.6, [
        ("技术栈：", "Python 3.10+、Flask 3.x、SQLite"),
        ("表现层：", "Jinja2 模板，服务端渲染"),
        ("控制层：", "Blueprint 路由与参数处理"),
        ("服务层：", "校验、筛选、统计、逾期判定"),
        ("数据层：", "参数化 SQL，单文件数据库"),
        ("取舍：", "不用 ORM、不用前端框架"),
    ], size=14, gap=10)

    # 5 data + rules
    s = add_slide(prs, "数据库与关键规则", "单表 tasks · 约束与业务规则")
    rows = [
        ["字段", "约束"],
        ["title / course", "1—100 字 / 1—60 字"],
        ["due_date", "YYYY-MM-DD，真实日期"],
        ["priority", "高 / 中 / 低，默认中"],
        ["status", "待完成 / 进行中 / 已完成"],
        ["created_at / updated_at", "服务端自动维护"],
    ]
    table(s, 0.7, 1.8, 6.2, 3.2, rows, col_widths=[2.3, 3.9], font_size=12)
    add_bullets(s, 7.3, 1.85, 5.3, 4.8, [
        ("逾期：", "未完成且截止日期 < 今天"),
        ("即将到期：", "未完成且距今 0—3 天（含边界）"),
        ("完成率：", "已完成 ÷ 总数 × 100%，四舍五入"),
        ("统计口径：", "基于全部任务，不随筛选变化"),
        ("排序：", "截止日期升序 → 优先级 → 创建时间倒序"),
        ("写操作：", "POST + PRG；删除独立确认页"),
    ], size=13.5, gap=10)

    # 6 list
    s = add_slide(prs, "功能演示：任务列表与统计", "首页：统计卡 + 组合筛选 + 逾期标记")
    picture(s, SHOTS / "home-crop.png", 0.55, 1.75, w=8.15)
    add_bullets(s, 9.0, 1.9, 3.75, 4.8, [
        ("统计卡：", "总数、已完成、完成率实时计算"),
        ("筛选：", "课程 / 状态 / 优先级任意组合"),
        ("标记：", "逾期红色、即将到期橙色"),
        ("行内：", "直接调整状态并更新"),
        ("操作：", "查看、编辑、删除"),
    ], size=13, gap=9)

    # 7 detail
    s = add_slide(prs, "功能演示：详情与状态流转", "全部字段 + 逾期提示 + 三态切换")
    picture(s, SHOTS / "detail-crop.png", 0.55, 1.8, w=7.9)
    add_bullets(s, 8.75, 1.95, 3.95, 4.6, [
        ("详情：", "名称、课程、描述、日期、优先级、时间戳"),
        ("提示：", "逾期显示红色提示条"),
        ("状态：", "待完成 / 进行中 / 已完成任意切换"),
        ("一致性：", "列表、详情、统计同源实时读取"),
        ("入口：", "编辑、删除、返回列表"),
    ], size=13, gap=10)

    # 8 form
    s = add_slide(prs, "功能演示：新建任务与校验", "服务端校验为准，错误就地回显")
    picture(s, SHOTS / "form-narrow-crop.png", 0.75, 1.75, w=5.9)
    add_bullets(s, 7.2, 1.9, 5.5, 4.8, [
        ("必填：", "任务名称、所属课程、截止日期"),
        ("校验：", "空值、超长、日期格式与真实日期"),
        ("回显：", "保留已填内容，字段旁提示"),
        ("入库：", "新建固定“待完成”，时间戳自动生成"),
        ("成功后：", "PRG 重定向到列表并提示"),
    ], size=13.5, gap=10)

    # 9 implementation
    s = add_slide(prs, "关键实现", "规则集中、SQL 参数化、失败可恢复")
    add_bullets(s, 0.7, 1.85, 6.0, 4.9, [
        ("组合筛选：", "条件动态拼接，值全部参数绑定"),
        ("完成率：", "total=0 时固定 0%，避免除零"),
        ("日期基准：", "服务器本地日期，精确到日"),
        ("错误处理：", "400 回显、404/405/500 统一页面"),
        ("代码组织：", "服务层可单独测试，模板不含逻辑"),
    ], size=14, gap=12)
    code_block(s, 7.0, 1.9, 5.75, 2.95, [
        "SELECT * FROM tasks",
        "WHERE (:course  IS NULL OR course = :course)",
        "  AND (:status  IS NULL OR status = :status)",
        "  AND (:priority IS NULL OR priority = :priority)",
        "ORDER BY due_date ASC,",
        "  CASE priority WHEN '高' THEN 0",
        "                WHEN '中' THEN 1 ELSE 2 END,",
        "  created_at DESC;",
    ], size=10.5)

    # 10 tests
    s = add_slide(prs, "测试与验证", "18 项自动化测试全部通过")
    rows = [
        ["测试类别", "代表用例", "结果"],
        ["创建与校验", "空名称、超长名称、非法日期", "通过"],
        ["查询与编辑", "详情、404、编辑一致性", "通过"],
        ["删除与状态", "确认删除、非法状态拒绝", "通过"],
        ["筛选与统计", "组合条件、完成率 67%/25%", "通过"],
        ["持久化与排序", "重启后数据仍在、截止日期排序", "通过"],
    ]
    table(s, 0.7, 1.85, 7.9, 3.4, rows, col_widths=[2.2, 4.4, 1.3], font_size=11.5)
    code_block(s, 0.7, 5.2, 7.9, 0.95, [
        "$ pytest -q",
        "18 passed in 0.60s",
    ], size=11)
    add_bullets(s, 9.0, 1.9, 3.7, 4.6, [
        ("单元与集成：", "pytest + 临时数据库"),
        ("边界：", "今天、第 3 天、第 4 天"),
        ("手工验收：", "全流程操作、重启、非法输入"),
        ("结果：", "无严重缺陷，验收项齐全"),
    ], size=12.5, gap=10)

    # 11 lessons
    s = add_slide(prs, "问题与反思", "真实问题、处理方式与经验")
    card(s, 0.7, 1.8, 5.75, 2.3, "校验规则重复", "服务层与数据库都写约束，提示文案不一致。\n以服务端校验为唯一提示来源，数据库约束只做兜底。")
    card(s, 6.85, 1.8, 5.75, 2.3, "删除误操作", "初版用链接直接删除，容易误点。\n改为确认页 + POST 执行，并显示任务信息。")
    card(s, 0.7, 4.35, 5.75, 2.3, "状态字段不一致", "新建与编辑都允许改状态，与“新建固定待完成”冲突。\n新建隐藏该字段，并回写设计文档 6.2 节。")
    card(s, 6.85, 4.35, 5.75, 2.3, "经验", "先设计后编码减少返工；测试覆盖今天、第 3 天、第 4 天等边界；AI 产出必须实际运行验证。")

    # 12 summary
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0.0, 0.0, W, H, PALE, shape=MSO_SHAPE.RECTANGLE)
    rect(s, 0.0, 0.0, 0.18, H, BLUE, shape=MSO_SHAPE.RECTANGLE)
    textbox(s, 0.9, 1.6, 11.6, 0.6, "总结", size=32, bold=True)
    add_bullets(s, 0.95, 2.5, 11.4, 2.6, [
        "完整实现 FR-01—FR-10，满足 A.6 验收标准",
        "四层架构 + 参数化 SQL，规则集中、可测试",
        "18 项自动化测试通过，实际运行验证",
    ], size=16, gap=10)
    textbox(s, 0.9, 5.1, 11.6, 0.8, "谢谢观看，欢迎提问", size=26, bold=True, color=BLUE)

    prs.save(OUT)
    print("saved", OUT, OUT.stat().st_size, "slides", len(prs.slides))


if __name__ == "__main__":
    main()
