"""Build a compact <=4 page report docx from docs/实验报告.md."""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

DOCS = Path(r"D:\SoftwareE\StudyTask\docs")
MD = DOCS / "实验报告.md"
DOCX = DOCS / "实验报告.docx"

BODY = "宋体"
HEAD = "黑体"
ASCII = "Times New Roman"
CODE = "Consolas"


def font(run, size=10.5, bold=False, eastasia=BODY, ascii_font=ASCII, color=None):
    run.font.name = ascii_font
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), ascii_font)
    rfonts.set(qn("w:hAnsi"), ascii_font)
    rfonts.set(qn("w:eastAsia"), eastasia)
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color


def shade(cell, fill="F2F2F2"):
    tcpr = cell._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def page_field(par):
    run = par.add_run()
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = " PAGE "
    s = OxmlElement("w:fldChar"); s.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = "1"
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    for el in (b, it, s, t, e):
        run._r.append(el)
    font(run, size=9)


def inline(par, text, size=10.5):
    for tok in re.split(r"(\*\*.+?\*\*|`.+?`)", text):
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            r = par.add_run(tok[2:-2]); font(r, size=size, bold=True)
        elif tok.startswith("`") and tok.endswith("`"):
            r = par.add_run(tok[1:-1]); font(r, size=size - 0.5, eastasia="微软雅黑", ascii_font=CODE)
        else:
            r = par.add_run(tok); font(r, size=size)


def para(doc, text, indent=True):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_after = Pt(2)
    if indent:
        p.paragraph_format.first_line_indent = Pt(21)
    inline(p, text)


def bullet(doc, text, idx=None):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(21)
    p.paragraph_format.first_line_indent = Pt(-10)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(f"{idx}. " if idx else "• ")
    font(r, size=10.5)
    inline(p, text)


def table(doc, rows):
    header = [c.strip() for c in rows[0].strip().strip("|").split("|")]
    body = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in rows[2:]]
    t = doc.add_table(rows=len(body) + 1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER

    tr_pr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); tr_pr.append(th)
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    for j, h in enumerate(header):
        cell = t.rows[0].cells[j]
        shade(cell)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); font(r, size=9, bold=True)
    for i, row in enumerate(body, 1):
        for j, val in enumerate(row[: len(header)]):
            p = t.rows[i].cells[j].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            inline(p, val, size=9)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def code(doc, lines):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    cell = t.rows[0].cells[0]
    shade(cell, "F7F7F7")
    for i, ln in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(ln); font(r, size=8.5, eastasia="微软雅黑", ascii_font=CODE)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def image(doc, alt, path):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    pic = p.add_run().add_picture(str(path), width=Cm(13.2))
    cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(4)
    r = cap.add_run(alt); font(r, size=9, color=RGBColor(0x55, 0x55, 0x55))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = MD.read_text(encoding="utf-8")
    doc = Document()

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    sec.left_margin = sec.right_margin = Cm(2.3)

    normal = doc.styles["Normal"]
    normal.font.name = ASCII
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY)
    normal.paragraph_format.line_spacing = 1.3
    normal.paragraph_format.space_after = Pt(0)

    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    page_field(footer)

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()

        if s.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            code(doc, buf)
            i += 1
            continue

        m = re.match(r"!\[(.*?)\]\((.*?)\)", s)
        if m:
            path = (MD.parent / m.group(2)).resolve()
            if path.exists():
                image(doc, m.group(1), path)
            i += 1
            continue

        if s.startswith("# "):
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run(s[2:]); font(r, size=16, bold=True, eastasia=HEAD)
            i += 1
            continue

        if s.startswith("## "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(s[3:]); font(r, size=12, bold=True, eastasia=HEAD)
            i += 1
            continue

        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i]); i += 1
            table(doc, rows)
            continue

        if s.startswith("- "):
            bullet(doc, s[2:]); i += 1; continue

        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            bullet(doc, m.group(2), idx=m.group(1)); i += 1; continue

        if not s:
            i += 1; continue

        if s.startswith("课程：") or s.startswith("班级："):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(1)
            inline(p, s, size=10.5)
            i += 1
            continue

        para(doc, s)
        i += 1

    doc.save(DOCX)
    print("saved", DOCX, DOCX.stat().st_size)


if __name__ == "__main__":
    main()
