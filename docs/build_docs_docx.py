#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
把《择日大师_完整说明书_v2.2.1.md》转成方便阅读的 Word（.docx）。

与 PDF 不同，本转换刻意取消「每节强制分页」，改用紧凑排版：
  · 页边距 1.9cm，正文 10.5pt，行距 1.25，段后 3pt
  · 篇标题（h1）不另起页，只加大段前距，避免大面积空白
  · 表格 8.5pt、自动宽度、表头跨页重复
  · 内置 Word 标题样式（h1–h3），可用导航窗格与「更新目录」生成页码

用法：python docs/build_docs_docx.py
依赖：python-docx
"""
import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

DOCS = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DOCS, '择日大师_完整说明书_v2.2.1.md')
OUT = os.path.join(DOCS, '择日大师_完整说明书_v2.2.1.docx')

FONT_CN = '宋体'
FONT_HEAD = '微软雅黑'
FONT_MONO = 'Consolas'


def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def set_run_font(run, name=FONT_CN, size=None, bold=None, color=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    rfonts.set(qn('w:eastAsia'), name)
    rfonts.set(qn('w:ascii'), name)
    rfonts.set(qn('w:hAnsi'), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


def shade(paragraph_or_cell, fill):
    el = paragraph_or_cell._element
    pr = el.get_or_add_tcPr() if el.tag.endswith('tc') else el.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    pr.append(shd)


def add_bottom_border(paragraph, color='BBBBBB', size='6'):
    ppr = paragraph._element.get_or_add_pPr()
    borders = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), size)
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), color)
    borders.append(bottom)
    ppr.append(borders)


INLINE = re.compile(
    r'(<span style="color:#c00000">|</span>|'
    r'<span style="color:#(?:[0-9a-fA-F]{6})">|\*\*|\\)')


def add_inline(paragraph, text, base_size=10.5, base_bold=False, color=None):
    """处理 **粗体**、`代码`、<span style="color:#c00000">红字</span>。"""
    pos = 0
    bold = base_bold
    red = False
    text = text.replace('<br/>', ' ').replace('<br />', ' ')
    while pos < len(text):
        m = INLINE.search(text, pos)
        if not m:
            _emit(paragraph, text[pos:], base_size, bold, red or color)
            break
        if m.start() > pos:
            _emit(paragraph, text[pos:m.start()], base_size, bold, red or color)
        tok = m.group(0)
        if tok.startswith('<span'):
            red = True
        elif tok == '</span>':
            red = False
        elif tok == '**':
            bold = not bold
        pos = m.end()


def _emit(paragraph, chunk, size, bold, color):
    """按 `代码` 切分并逐段写入。"""
    parts = re.split(r'(`[^`]*`)', chunk)
    for p in parts:
        if not p:
            continue
        if p.startswith('`') and p.endswith('`') and len(p) > 1:
            r = paragraph.add_run(p[1:-1])
            set_run_font(r, FONT_MONO, size - 1.0, bold, '333333')
        else:
            r = paragraph.add_run(p)
            set_run_font(r, FONT_CN, size, bold, 'C00000' if color else None)


def strip_html(s):
    s = re.sub(r'<[^>]+>', '', s)
    return s.replace('&nbsp;', ' ').strip()


def parse_blocks(md):
    """把 Markdown 切成块：heading / para / table / list / quote / code / hr。"""
    lines = md.splitlines()
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if s.startswith('```'):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            blocks.append(('code', '\n'.join(buf)))
            continue
        if s == '[TOC]':
            i += 1
            continue
        if s.startswith('<div') or s.startswith('</div') or s.startswith('<div '):
            i += 1
            continue
        m = re.match(r'^(#{1,4})\s+(.*)$', s)
        if m:
            blocks.append(('h%d' % len(m.group(1)), m.group(2).strip()))
            i += 1
            continue
        if re.match(r'^---+\s*$', s):
            blocks.append(('hr', ''))
            i += 1
            continue
        if s.startswith('|') and i + 1 < n and re.match(r'^\|[\s\-:|]+\|\s*$', lines[i + 1].strip()):
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not re.match(r'^[\s\-:|]+$', '|'.join(cells)):
                    rows.append(cells)
                i += 1
            blocks.append(('table', rows))
            continue
        if s.startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip().lstrip('>').strip())
                i += 1
            blocks.append(('quote', [b for b in buf if b]))
            continue
        if re.match(r'^(\d+\.|[-*+])\s+', s):
            items = []
            while i < n:
                cur = lines[i]
                m2 = re.match(r'^(\s*)(\d+\.|[-*+])\s+(.*)$', cur)
                if not m2:
                    break
                items.append((len(m2.group(1)) // 2, m2.group(2), m2.group(3).strip()))
                i += 1
            blocks.append(('list', items))
            continue
        # 普通段落：吸收连续的非空、非特殊行
        buf = [s]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(('#', '|', '>', '```', '---')
                                          ) or re.match(r'^(\d+\.|[-*+])\s+', nxt)):
                break
            buf.append(nxt)
            i += 1
        blocks.append(('para', ' '.join(buf)))
    return blocks


def setup(doc):
    sec = doc.sections[0]
    sec.top_margin = Cm(1.9)
    sec.bottom_margin = Cm(1.9)
    sec.left_margin = Cm(2.0)
    sec.right_margin = Cm(2.0)

    normal = doc.styles['Normal']
    normal.font.name = FONT_CN
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn('w:eastAsia'), FONT_CN)
    pf = normal.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.25

    specs = {
        'Heading 1': (17, '5C1010', 18, 6),
        'Heading 2': (13, '7A1414', 12, 4),
        'Heading 3': (11.5, '333333', 8, 3),
    }
    for name, (size, color, before, after) in specs.items():
        st = doc.styles[name]
        st.font.name = FONT_HEAD
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor.from_string(color)
        rpr = st.element.get_or_add_rPr()
        rfonts = rpr.find(qn('w:rFonts'))
        if rfonts is None:
            rfonts = OxmlElement('w:rFonts')
            rpr.append(rfonts)
        rfonts.set(qn('w:eastAsia'), FONT_HEAD)
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True
        st.paragraph_format.line_spacing = 1.15


def add_footer(doc):
    footer = doc.sections[0].footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('专业级正五行择日软件 · 完整说明书 v2.2.1　　')
    set_run_font(r, FONT_CN, 8, False, '888888')
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), 'PAGE')
    inner = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = '1'
    inner.append(t)
    fld.append(inner)
    p._element.append(fld)


def auto_widths(rows, total_cm=17.0):
    """按各列最长文本分配列宽，避免窄列被挤成竖排。"""
    cols = max(len(r) for r in rows)
    scores = []
    for ci in range(cols):
        longest = max((len(rows[ri][ci]) if ci < len(rows[ri]) else 0) for ri in range(len(rows)))
        scores.append(min(max(longest, 4), 46))
    s = sum(scores)
    widths = [max(1.8, min(7.6, total_cm * sc / s)) for sc in scores]
    # 归一化到整页可用宽度
    k = total_cm / sum(widths)
    return [w * k for w in widths]


def apply_widths(table, widths):
    """固定列宽：除单元格宽外，还需把 tblW 与 tblLayout 一并写死，否则 Word 会重算。"""
    table.autofit = False
    twips = int(sum(widths) * 567)
    tbl = table._tbl
    pr = tbl.tblPr
    for tag in ('w:tblW', 'w:tblLayout'):
        old = pr.find(qn(tag))
        if old is not None:
            pr.remove(old)
    tw = OxmlElement('w:tblW')
    tw.set(qn('w:type'), 'dxa')
    tw.set(qn('w:w'), str(twips))
    pr.append(tw)
    layout = OxmlElement('w:tblLayout')
    layout.set(qn('w:type'), 'fixed')
    pr.append(layout)
    for ci, w in enumerate(widths):
        for cell in table.columns[ci].cells:
            cell.width = Cm(w)


def build():
    md = read(SRC)
    blocks = parse_blocks(md)
    doc = Document()
    setup(doc)
    add_footer(doc)

    # 标题区（紧凑，不单独占一整页）
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('专业级正五行择日软件')
    set_run_font(r, FONT_HEAD, 11, False, '8B6A3F')
    p.paragraph_format.space_before = Pt(6)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('完整说明书')
    set_run_font(r, FONT_HEAD, 30, True, '5C1010')
    p.paragraph_format.space_after = Pt(4)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('使用指南 · 历法基石 · 神煞族谱 · 制化山家 · 评分总则 · 争议铁案 · 速查附录')
    set_run_font(r, FONT_CN, 10, False, '444444')
    p.paragraph_format.space_after = Pt(2)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('版本 v2.2.1　·　适用软件 v2.2.1-release　·　2026-11-03')
    set_run_font(r, FONT_CN, 9, False, '666666')
    p.paragraph_format.space_after = Pt(10)
    add_bottom_border(p, '8B1A1A', '12')

    # 静态导航（无页码，Word 内可用导航窗格/更新目录获得页码）
    nav = doc.add_paragraph()
    r = nav.add_run('全书导航')
    set_run_font(r, FONT_HEAD, 12, True, '5C1010')
    nav.paragraph_format.space_before = Pt(6)
    nav.paragraph_format.space_after = Pt(4)

    heads = [(b[0], b[1]) for b in blocks if b[0] in ('h1', 'h2')]
    for lvl, text in heads:
        text = strip_html(text).replace('**', '')
        q = doc.add_paragraph()
        q.paragraph_format.space_after = Pt(0)
        q.paragraph_format.left_indent = Cm(0.0 if lvl == 'h1' else 0.55)
        q.paragraph_format.line_spacing = 1.05
        r = q.add_run(text)
        set_run_font(r, FONT_HEAD if lvl == 'h1' else FONT_CN,
                     9.5 if lvl == 'h1' else 9,
                     lvl == 'h1', '5C1010' if lvl == 'h1' else '444444')

    doc.add_paragraph()

    for kind, payload in blocks:
        if kind in ('h1', 'h2', 'h3', 'h4'):
            lvl = int(kind[1])
            style = 'Heading %d' % min(lvl, 3)
            h = doc.add_paragraph(style=style)
            add_inline(h, payload, base_size={1: 17, 2: 13, 3: 11.5, 4: 11}[lvl],
                       base_bold=True)
            if lvl == 1:
                add_bottom_border(h, '8B1A1A', '8')
        elif kind == 'para':
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            add_inline(p, payload)
        elif kind == 'quote':
            for seg in payload:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.5)
                p.paragraph_format.space_after = Pt(2)
                shade(p, 'FAF6EF')
                add_inline(p, seg, base_size=9.5, color='3D3323')
        elif kind == 'hr':
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            add_bottom_border(p, 'DDDDDD', '6')
        elif kind == 'code':
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.05
            shade(p, 'F5F5F5')
            r = p.add_run(payload)
            set_run_font(r, FONT_MONO, 8.5, False, '333333')
        elif kind == 'list':
            for indent, marker, text in payload:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.55 + 0.55 * indent)
                p.paragraph_format.first_line_indent = Cm(-0.55)
                p.paragraph_format.space_after = Pt(2)
                bullet = '·' if marker in ('-', '*', '+') else marker
                r = p.add_run(bullet + ' ')
                set_run_font(r, FONT_CN, 10.5, False, '7A1414')
                add_inline(p, text)
        elif kind == 'table':
            rows = payload
            if not rows:
                continue
            cols = max(len(r) for r in rows)
            table = doc.add_table(rows=len(rows), cols=cols)
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = True
            for ri, row in enumerate(rows):
                for ci in range(cols):
                    cell = table.cell(ri, ci)
                    cell.text = ''
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = 1.05
                    txt = row[ci] if ci < len(row) else ''
                    add_inline(p, txt, base_size=8.5, base_bold=(ri == 0))
                    if ri == 0:
                        shade(cell, 'F2E6E6')
            # 表头跨页重复
            tr = table.rows[0]._tr
            trpr = tr.get_or_add_trPr()
            th = OxmlElement('w:tblHeader')
            th.set(qn('w:val'), 'true')
            trpr.append(th)
            apply_widths(table, auto_widths(rows))
            doc.add_paragraph().paragraph_format.space_after = Pt(2)

    props = doc.core_properties
    props.title = '择日大师 · 完整说明书 v2.2.1'
    props.subject = '专业级正五行择日软件官方文档'
    props.author = '专业择日团队'
    doc.save(OUT)
    return OUT


if __name__ == '__main__':
    out = build()
    print('[OK] docx:', out, '%.2f MB' % (os.path.getsize(out) / 1024 / 1024))
