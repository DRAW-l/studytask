"""Convert docs/设计说明书.md into a formatted Word document."""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

DOCS = Path(r"D:\SoftwareE\StudyTask\docs")
MD = DOCS / "设计说明书.md"
DOCX = DOCS / "设计说明书.docx"

BODY_FONT = "宋体"
HEAD_FONT = "黑体"
ASCII_FONT = "Times New Roman"
CODE_FONT = "Consolas"


def set_run_font(run, eastasia=BODY_FONT, ascii_font=ASCII_FONT, size=None, bold=None, color=None):
    run.font.name = ascii_font
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), ascii_font)
    rfonts.set(qn("w:hAnsi"), ascii_font)
    rfonts.set(qn("w:eastAsia"), eastasia)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def shade(cell_or_par, fill="F2F2F2"):
    el = cell_or_par._element
    if el.tag == qn("w:tc"):
        pr = el.get_or_add_tcPr()
    else:
        pr = el.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pr.append(shd)


def add_field(paragraph, instr):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_text = OxmlElement("w:t")
    fld_text.text = "1"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr_el)
    run._r.append(fld_sep)
    run._r.append(fld_text)
    run._r.append(fld_end)
    set_run_font(run, size=10.5)


def setup_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = ASCII_FONT
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(0)

    for name, size in (("Heading 1", 18), ("Heading 2", 15), ("Heading 3", 13)):
        st = doc.styles[name]
        st.font.name = ASCII_FONT
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), HEAD_FONT)
        st.paragraph_format.space_before = Pt(18 if name == "Heading 1" else 12)
        st.paragraph_format.space_after = Pt(10 if name == "Heading 1" else 6)
        st.paragraph_format.keep_with_next = True


def setup_page(doc):
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.8)
    section.right_margin = Cm(2.6)

    header_p = section.header.paragraphs[0]
    header_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header_p.add_run("StudyTask 个人学习任务管理系统 · 设计说明书")
    set_run_font(run, size=9, color=RGBColor(0x66, 0x66, 0x66))

    footer_p = section.footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(footer_p, " PAGE ")


def add_cover(doc, meta):
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(meta.get("title", ""))
    set_run_font(r, eastasia=HEAD_FONT, size=26, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    r = p.add_run(meta.get("subtitle", ""))
    set_run_font(r, eastasia=HEAD_FONT, size=20, bold=True)

    for _ in range(4):
        doc.add_paragraph()

    info = [
        ("课程名称", meta.get("course", "")),
        ("实验项目", meta.get("lab", "")),
        ("文档版本", meta.get("version", "")),
        ("编写日期", meta.get("date", "")),
        ("班级", ""),
        ("学号", ""),
        ("姓名", ""),
    ]
    table = doc.add_table(rows=len(info), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = False
    for i, (k, v) in enumerate(info):
        row = table.rows[i]
        row.cells[0].width = Cm(4.5)
        row.cells[1].width = Cm(7.5)
        p0 = row.cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run(k)
        set_run_font(r0, size=12, bold=True)
        p1 = row.cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(v)
        set_run_font(r1, size=12)

    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("依据：《StudyTask 需求规格说明书》（附录 A）")
    set_run_font(r, size=10.5, color=RGBColor(0x55, 0x55, 0x55))

    doc.add_page_break()


def add_toc(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("目　录")
    set_run_font(r, eastasia=HEAD_FONT, size=16, bold=True)
    p.paragraph_format.space_after = Pt(12)

    p = doc.add_paragraph()
    add_field(p, ' TOC \\o "1-2" \\h \\z \\u ')
    doc.add_page_break()


def enable_update_fields(doc):
    settings = doc.settings.element
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    settings.append(el)


def add_inline(paragraph, text, size=12, bold_default=False):
    tokens = re.split(r"(\*\*.+?\*\*|`.+?`)", text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            r = paragraph.add_run(tok[2:-2])
            set_run_font(r, size=size, bold=True)
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            r = paragraph.add_run(tok[1:-1])
            set_run_font(r, eastasia=CODE_FONT, ascii_font=CODE_FONT, size=size - 1)
        else:
            r = paragraph.add_run(tok)
            set_run_font(r, size=size, bold=bold_default)


def add_paragraph(doc, text, indent=True):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(3)
    if indent:
        p.paragraph_format.first_line_indent = Pt(24)
    add_inline(p, text)
    return p


def add_bullet(doc, text, ordered=False, index=None):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(24)
    p.paragraph_format.first_line_indent = Pt(-12)
    p.paragraph_format.space_after = Pt(2)
    prefix = f"{index}. " if ordered else "• "
    r = p.add_run(prefix)
    set_run_font(r, size=12)
    add_inline(p, text)


def add_code(doc, lines, lang=""):
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    shade(cell, "F7F7F7")
    cell.paragraphs[0].text = ""
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(line)
        set_run_font(r, eastasia="微软雅黑", ascii_font=CODE_FONT, size=9)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_image(doc, alt, path):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Cm(15.2))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(8)
    r = cap.add_run(alt)
    set_run_font(r, size=10.5, color=RGBColor(0x55, 0x55, 0x55))


def add_table(doc, rows):
    header = [c.strip() for c in rows[0].strip().strip("|").split("|")]
    body = []
    for line in rows[2:]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        body.append(cells[: len(header)])

    table = doc.add_table(rows=len(body) + 1, cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    tr_pr = table.rows[0]._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)
    for row in table.rows:
        row_pr = row._tr.get_or_add_trPr()
        cant_split = OxmlElement("w:cantSplit")
        row_pr.append(cant_split)

    for j, text in enumerate(header):
        cell = table.rows[0].cells[j]
        shade(cell, "E8EEF7")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        set_run_font(r, size=10.5, bold=True)

    for i, cells in enumerate(body, 1):
        for j, text in enumerate(cells):
            p = table.rows[i].cells[j].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            add_inline(p, text, size=10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_quote(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    set_run_font(r, size=11)
    r.italic = True


def parse_meta(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    meta = {}
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[end + 5 :]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    global DOCX
    if "--out" in sys.argv:
        DOCX = Path(sys.argv[sys.argv.index("--out") + 1])
    text = MD.read_text(encoding="utf-8")
    meta, body = parse_meta(text)

    doc = Document()
    setup_styles(doc)
    setup_page(doc)
    doc.core_properties.title = meta.get("title", "")
    doc.core_properties.subject = meta.get("subtitle", "")

    add_cover(doc, meta)
    add_toc(doc)
    enable_update_fields(doc)

    lines = body.splitlines()
    i = 0
    first_h1 = True
    buf = []

    def flush():
        nonlocal buf
        if buf:
            add_paragraph(doc, " ".join(x.strip() for x in buf))
            buf = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush()
            lang = stripped[3:].strip()
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            add_code(doc, code, lang)
            i += 1
            continue

        m = re.match(r"!\[(.*?)\]\((.*?)\)", stripped)
        if m:
            flush()
            alt, rel = m.group(1), m.group(2)
            path = (MD.parent / rel).resolve()
            if path.exists():
                add_image(doc, alt, path)
            i += 1
            continue

        if stripped.startswith("#"):
            flush()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[level:].strip()
            h = doc.add_heading(level=min(level, 3))
            if level == 1 and not first_h1:
                h.paragraph_format.page_break_before = True
            if level == 1:
                first_h1 = False
            r = h.add_run(title)
            set_run_font(r, eastasia=HEAD_FONT, size={1: 18, 2: 15, 3: 13}[min(level, 3)], bold=True)
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            add_table(doc, rows)
            continue

        if stripped.startswith("- "):
            flush()
            add_bullet(doc, stripped[2:])
            i += 1
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            flush()
            add_bullet(doc, m.group(2), ordered=True, index=m.group(1))
            i += 1
            continue

        if stripped.startswith(">"):
            flush()
            add_quote(doc, stripped.lstrip("> ").strip())
            i += 1
            continue

        if not stripped:
            flush()
            i += 1
            continue

        buf.append(line)
        i += 1

    flush()
    doc.save(DOCX)
    print("saved", DOCX, DOCX.stat().st_size)


if __name__ == "__main__":
    main()
