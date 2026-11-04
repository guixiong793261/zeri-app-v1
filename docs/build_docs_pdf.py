#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
构建 v2.2.1 官方文档：
  1) 合并分册为两本 Markdown（用户操作手册 / 算法与典据白皮书）
  2) 转 HTML（A4、中文衬线、封面、自动目录、表格样式、红标保留）
  3) 用 Edge headless + CDP 打印为 PDF（带页眉页脚与页码）

用法：python docs/build_docs_pdf.py [--skip-pdf]
依赖：markdown、websocket-client；Edge 安装于默认路径。
"""
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

DOCS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DOCS)

MANUAL_SRC = os.path.join(DOCS, '手册_用户操作手册_B1.md')
B2 = os.path.join(DOCS, '白皮书_第二四部分_历法与评分总则_B2.md')
B3 = os.path.join(DOCS, '白皮书_第三部分_吉神族卡_B3.md')
B4 = os.path.join(DOCS, '白皮书_第三部分_凶煞族卡_B4.md')
B5 = os.path.join(DOCS, '白皮书_第三部分_制化与山家体系_B5.md')
B6 = os.path.join(DOCS, '白皮书_第五部分_争议裁决总录_B6.md')
B7 = os.path.join(DOCS, '白皮书_附录_速查表与术语表_B7.md')

MANUAL_OUT = os.path.join(DOCS, '择日大师_用户操作手册_v2.2.1.md')
WHITE_OUT = os.path.join(DOCS, '择日大师_算法与典据白皮书_v2.2.1.md')
FULL_OUT = os.path.join(DOCS, '择日大师_完整说明书_v2.2.1.md')

EDGE_CANDIDATES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]


def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def build_manual():
    body = read(MANUAL_SRC)
    body = body.replace('| 版本 | V1.0（B1 批次稿） |', '| 版本 | v2.2.1（正式发布版） |')
    body = body.replace('《算法与典据白皮书（说明书）》第二、四部分（B2 批次稿）',
                        '《算法与典据白皮书》v2.2.1')
    body = body.replace('本文为文字稿；标注「配图 1-1」处将在排版阶段插入实机截图，正文不依赖截图亦可完成操作',
                        '本文为文字稿；标注「配图 1-1」处预留实机截图位，正文不依赖截图亦可完成操作')
    # 去掉 B1 自带的纯文本目录，改用自动生成的带锚点目录
    body = re.sub(r'^## 目录\n.*?\n---\n', '', body, count=1, flags=re.S | re.M)
    cover = f"""<div class="cover">
<div class="cover-kicker">专业级正五行择日软件</div>
<div class="cover-title">用户操作手册</div>
<div class="cover-sub">从三分钟上手，到红帖三态与实战排雷</div>
<div class="cover-meta">版本 v2.2.1　·　适用软件 v2.2.1-release　·　2026-11-03</div>
<div class="cover-line"></div>
<div class="cover-note">本手册面向择日师、学徒与日常使用者。<br/>配套《算法与典据白皮书》v2.2.1 查阅底层算法与典据。</div>
</div>
"""
    write(MANUAL_OUT, cover + '\n[TOC]\n\n' + body)
    return MANUAL_OUT


def build_full():
    """把 B1 操作篇 + B2 历法/评分篇 + B3–B7 白皮书分册，合为一本完整说明书。"""
    b1 = read(MANUAL_SRC)
    b1 = b1.replace('| 版本 | V1.0（B1 批次稿） |', '| 版本 | v2.2.1（正式发布版） |')
    b1 = b1.replace('| 配套文档 | 《算法与典据白皮书（说明书）》第二、四部分（B2 批次稿） |',
                    '| 配套章节 | 本书第二篇（历法）、第三篇（神煞）、第四篇（评分）、第五篇（裁决） |')
    b1 = b1.replace('本文为文字稿；标注「配图 1-1」处将在排版阶段插入实机截图，正文不依赖截图亦可完成操作',
                    '本文为文字稿；标注「配图 1-1」处预留实机截图位，正文不依赖截图亦可完成操作')
    b1 = re.sub(r'^## 目录\n.*?\n---\n', '', b1, count=1, flags=re.S | re.M)
    b1 = b1.replace('# 专业级正五行择日软件 · 用户操作手册',
                    '# 第一篇 · 使用指南（第 1–11 章）\n\n'
                    '> 本编只讲「怎么用」：从三分钟出第一张红帖，到红帖三态、慎用日与实战排雷。'
                    '不想看算法的读者，读完本编即可上手。\n', 1)

    b2 = read(B2)
    m = re.search(r'^# 第二部分 底层历法机制', b2, re.M)
    split = re.search(r'^# 第四部分 评分总则与五大核心事项', b2, re.M)
    if not (m and split):
        raise SystemExit('B2 结构不符，无法合并')
    part2 = b2[m.start():split.start()].rstrip() + '\n'
    part4 = b2[split.start():].rstrip() + '\n'
    part2 = part2.replace('# 第二部分 底层历法机制',
                          '# 第二篇 · 历法基石（第 7–10 章）', 1)
    part4 = part4.replace('# 第四部分 评分总则与五大核心事项',
                          '# 第四篇 · 评分总则与五大核心事项（第 11–17 章）', 1)

    def retitle(path, old, new):
        t = read(path).strip() + '\n'
        if old not in t:
            raise SystemExit(f'{os.path.basename(path)} 未找到标题「{old}」')
        return t.replace(old, new, 1)

    b3 = retitle(B3, '# 第三部分（上）· 吉神族逐项卡', '# 第三篇（上）· 吉神族逐项卡')
    b4 = retitle(B4, '# 第三部分（下）· 凶煞族逐项卡', '# 第三篇（下）· 凶煞族逐项卡')
    b5 = retitle(B5, '# 第三部分（末）· 制化与山家体系', '# 第三篇（末）· 制化与山家体系')
    b6 = retitle(B6, '# 第五部分 · 争议裁决总录', '# 第五篇 · 争议裁决总录')
    b7 = retitle(B7, '# 附录 · 神煞速查表与术语表', '# 附录 A–G · 神煞速查表与术语表')

    cover = """<div class="cover">
<div class="cover-kicker">专业级正五行择日软件</div>
<div class="cover-title">完整说明书</div>
<div class="cover-sub">使用指南 · 历法基石 · 神煞族谱 · 制化山家 · 评分总则 · 争议铁案 · 速查附录</div>
<div class="cover-meta">版本 v2.2.1　·　适用软件 v2.2.1-release　·　2026-11-03</div>
<div class="cover-line"></div>
<div class="cover-note">三库主锚：《协纪辨方书》（主锚）·《御定星历考原》（互校）·《陈子性藏书》（第三参照）<br/>凡无典据者，只可提示，不可定罪。</div>
</div>
"""

    preface = """
# 前言 · 怎么读这一本书

本书把原先分开的《用户操作手册》与《算法与典据白皮书》合成一册，**一册到底，前后互证**：前面教你怎么点，后面讲清为什么这样算、凭什么这样判。

## 全书结构

| 篇 | 章节号 | 内容 | 谁该读 |
| --- | --- | --- | --- |
| 第一篇 使用指南 | 第 1–11 章 | 上手、界面、参数、读结果、反推、红帖三态、导出、实战、FAQ、小词典 | 所有人，第一次使用必读 |
| 第二篇 历法基石 | 第 7–10 章 | 晚子时派、节气换柱、真太阳时、四柱与时辰、农历与神煞取用 | 想弄明白「日子是怎么算出来的」 |
| 第三篇 神煞族谱与制化山家 | 3.x / 4.x / 5.x | 吉神族卡、凶煞族卡（HARD_VETO 红标）、制化矩阵、山家封禁、扶山补龙相主 | 择日师、审课者 |
| 第四篇 评分总则 | 第 11–17 章 | 总分公式、五大事项、等级映射、扣分家族、247 分例算、代码索引 | 择日师、维护者 |
| 第五篇 争议裁决 | 6.x | 十六桩「扒皮」铁案：杀师日、红嘴朱雀、出行方向、年三煞四柱…… | 想追问「凭什么」的人 |
| 附录 A–G | — | 191 项神煞速查总表、核心起例、五通道否决表、测试基线、版本链、术语表 | 出稿前人工复核、打印张贴 |

> **编号说明**：为不改动任何跨册引用与测试断言，章节号沿用分册原始锚点——所以第二篇从「第 7 章」起、第三篇用 3.x/4.x/5.x、第五篇用 6.x。**篇内唯一，跨篇引用一律带篇名**，不影响阅读。

## 三条阅读路径

1. **只想择日**：第一篇 → 第 5 章（读结果）→ 第 7 章（红帖三态）→ 第 10 章（FAQ）。
2. **想审课**：第一篇第 5 章 → 第四篇第 11 章（总分公式）→ 第三篇（认神煞）→ 附录 A（查分值与否决）。
3. **想追责**：第五篇（先看铁案结论）→ 第三篇对应族卡（看现在怎么判）→ 第四篇附录 B（看代码在哪一行）。

## 三条贯穿全书的铁律

1. **否决只能来自代码显式否决点**，分数扣到负数仍是「凶」，不是「否决」。
2. **无典据不放宽、无典据不定罪**：无载者只作提示，不作否决。
3. **数字的唯一真源是 `modules/事项标准.py` 的 `SHENSHA_SCORES`**；本书与代码冲突时，以代码为准，并回填本书。
"""

    merged = (
        cover + preface + '\n[TOC]\n\n' +
        b1 + '\n' + part2 + '\n' + b3 + '\n' + b4 + '\n' + b5 + '\n' +
        part4 + '\n' + b6 + '\n' + b7
    )
    write(FULL_OUT, merged)
    return FULL_OUT


def build_whitepaper():
    b2 = read(B2)
    # 去掉 B2 的标题/版本表/目录，只保留正文
    m = re.search(r'^# 第二部分 底层历法机制', b2, re.M)
    if not m:
        raise SystemExit('B2 中未找到「# 第二部分 底层历法机制」')
    b2_front_drop = b2[m.start():]
    split = re.search(r'^# 第四部分 评分总则与五大核心事项', b2_front_drop, re.M)
    if not split:
        raise SystemExit('B2 中未找到「# 第四部分 评分总则与五大核心事项」')
    part2 = b2_front_drop[:split.start()].rstrip() + '\n'
    part4 = b2_front_drop[split.start():].rstrip() + '\n'

    def keep_all(path):
        return read(path).strip() + '\n'

    b3 = keep_all(B3)
    b4 = keep_all(B4)
    b5 = keep_all(B5)
    b6 = keep_all(B6)
    b7 = keep_all(B7)

    cover = """<div class="cover">
<div class="cover-kicker">专业级正五行择日软件</div>
<div class="cover-title">算法与典据白皮书</div>
<div class="cover-sub">历法基石 · 神煞族卡 · 制化山家 · 争议铁案</div>
<div class="cover-meta">版本 v2.2.1　·　适用软件 v2.2.1-release　·　2026-11-03</div>
<div class="cover-line"></div>
<div class="cover-note">三库主锚：《协纪辨方书》（主锚）·《御定星历考原》（互校）·《陈子性藏书》（第三参照）<br/>凡无典据者，只可提示，不可定罪。</div>
</div>
"""

    preface = """
# 前言 · 本书的编号与读法

本书由七个分册合并而成，为保留跨册引用与测试断言的稳定性，**章节号沿用分册锚点，不因合并重排**：

| 部分 | 章节号 | 来源分册 |
| --- | --- | --- |
| 第二部分 底层历法机制 | 第 7–10 章 | B2 |
| 第三部分 神煞族卡与制化山家 | 3.x / 4.x / 5.x | B3 / B4 / B5 |
| 第四部分 评分总则与五大核心事项 | 第 11–17 章 | B2 |
| 第五部分 争议裁决总录 | 6.x | B6 |
| 附录 | 附录 A–G | B7 |

> 读法建议：**先读第四部分第 11 章的总分公式，再回头看第三部分的族卡**——先有账本，再认神煞。
> 所有数字的唯一真源是 `modules/事项标准.py` 的 `SHENSHA_SCORES`；本皮书与代码冲突时，以代码为准。
"""

    merged = (
        cover + preface +
        '\n' + part2.split('# 第二部分 底层历法机制', 1)[0] +
        '# 第二部分 底层历法机制\n\n' + part2.split('# 第二部分 底层历法机制', 1)[-1].lstrip('\n') +
        '\n' + b3 +
        '\n' + b4 +
        '\n' + b5 +
        '\n# 第四部分 评分总则与五大核心事项\n\n' + part4.split('# 第四部分 评分总则与五大核心事项', 1)[-1].lstrip('\n') +
        '\n' + b6 +
        '\n' + b7
    )
    write(WHITE_OUT, merged)
    return WHITE_OUT


CSS = """
@page { size: A4; margin: 20mm 16mm 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "Microsoft YaHei", "SimSun", "Noto Serif CJK SC", serif;
       font-size: 10.5pt; line-height: 1.72; color: #1a1a1a; }
h1 { font-size: 20pt; margin: 0 0 12pt; padding-bottom: 6pt;
     border-bottom: 2.4pt solid #8b1a1a; color: #5c1010; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 14pt; margin: 18pt 0 8pt; color: #7a1414;
     page-break-before: always; page-break-after: avoid; }
h3 { font-size: 12pt; margin: 14pt 0 6pt; color: #333; page-break-after: avoid; }
p, li { orphans: 2; widows: 2; }
table { width: 100%; border-collapse: collapse; margin: 8pt 0 12pt;
        font-size: 8.6pt; line-height: 1.35; page-break-inside: auto; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #f2e6e6; color: #5c1010; border: 0.6pt solid #b9a3a3;
     padding: 4pt 4pt; text-align: left; font-weight: 700; }
td { border: 0.6pt solid #cfc3c3; padding: 3.6pt 4pt; vertical-align: top; }
tbody tr:nth-child(even) td { background: #fbf7f7; }
blockquote { margin: 8pt 0; padding: 6pt 10pt; border-left: 3pt solid #b08a4a;
             background: #faf6ef; color: #3d3323; font-size: 9.6pt; }
code { font-family: "Consolas", "Courier New", monospace; font-size: 9pt;
       background: #f4f4f4; padding: 1pt 3pt; border-radius: 2pt; }
pre { background: #f6f6f6; border: 0.6pt solid #ddd; padding: 8pt;
      page-break-inside: avoid; }
pre code { background: none; }
hr { border: none; border-top: 0.6pt solid #ddd; margin: 14pt 0; }
a { color: #7a1414; text-decoration: none; }
.cover { page-break-after: always; text-align: center; padding-top: 48mm; }
.cover-kicker { font-size: 12pt; letter-spacing: 6pt; color: #8b6a3f; }
.cover-title { font-size: 38pt; font-weight: 800; color: #5c1010; margin: 10mm 0 6mm;
               letter-spacing: 4pt; }
.cover-sub { font-size: 13pt; color: #444; margin-bottom: 16mm; }
.cover-meta { font-size: 10.5pt; color: #666; }
.cover-line { width: 90mm; height: 2.4pt; background: #8b1a1a; margin: 12mm auto; }
.cover-note { font-size: 9.6pt; color: #666; line-height: 2; }
.toc { page-break-before: always; page-break-after: always; }
.toc .toctitle { display: block; text-align: center; letter-spacing: 8pt;
                 font-size: 18pt; font-weight: 700; color: #5c1010; margin: 0 0 10mm; }
.toc > ul { list-style: none; padding-left: 0; column-count: 2; column-gap: 10mm; }
.toc ul ul { padding-left: 8pt; }
.toc li { font-size: 9.2pt; margin: 2pt 0; break-inside: avoid; }
.toc > ul > li > a { font-weight: 700; color: #5c1010; }
"""


def md_to_html(md_text, title, with_toc, toc_depth='1-2'):
    import markdown
    text = md_text
    if with_toc:
        # 在封面之后插入 [TOC]
        text = text.replace('</div>\n\n# ', '</div>\n\n[TOC]\n\n# ', 1)
    html_body = markdown.markdown(
        text,
        extensions=['toc', 'tables', 'fenced_code', 'sane_lists', 'attr_list'],
        extension_configs={'toc': {'toc_depth': toc_depth, 'permalink': False, 'title': '目　录'}},
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{title}</title><style>{CSS}</style></head>
<body>{html_body}</body></html>"""


def wait_port(port, timeout=20):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/version', timeout=1) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            time.sleep(0.3)
    return None


def cdp_pdf(edge, html_path, pdf_path, header_left):
    from websocket import create_connection
    profile = os.path.join(os.environ.get('TEMP', r'C:\Temp'), '_edge_pdf_profile')
    shutil.rmtree(profile, ignore_errors=True)
    proc = subprocess.Popen([
        edge, '--headless=new', '--disable-gpu', '--no-first-run',
        '--no-default-browser-check', '--remote-debugging-port=9223',
        f'--user-data-dir={profile}', 'about:blank',
    ])
    try:
        ver = wait_port(9223)
        if not ver:
            raise RuntimeError('Edge CDP 未启动')
        url = 'file:///' + html_path.replace('\\', '/')
        req = urllib.request.Request(
            'http://127.0.0.1:9223/json/new?' + urllib.parse.quote(url, safe=':/'),
            method='PUT')
        with urllib.request.urlopen(req, timeout=10) as r:
            target = json.loads(r.read().decode('utf-8'))
        ws = create_connection(target['webSocketDebuggerUrl'], timeout=30)
        mid = 0

        def send(method, params=None):
            nonlocal mid
            mid += 1
            ws.send(json.dumps({'id': mid, 'method': method, 'params': params or {}}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get('id') == mid:
                    return msg

        send('Page.enable')
        send('Runtime.enable')
        for _ in range(60):
            r = send('Runtime.evaluate', {'expression': 'document.readyState'})
            if r.get('result', {}).get('result', {}).get('value') == 'complete':
                break
            time.sleep(0.2)
        # 长文档（150 页级）必须在字体就绪 + 打印媒体重排完成后再打印，
        # 否则 printToPDF 会在中途截断（实测 150 页被截成 93/110 页）。
        send('Runtime.evaluate', {'expression': 'document.fonts.ready.then(() => 1)',
                                  'awaitPromise': True})
        send('Emulation.setEmulatedMedia', {'media': 'print'})
        time.sleep(3)
        footer = ('<div style="width:100%;font-size:8px;color:#888;text-align:center;'
                  'font-family:Microsoft YaHei">'
                  '<span class="pageNumber"></span> / <span class="totalPages"></span></div>')
        header = (f'<div style="width:100%;font-size:8px;color:#888;'
                  f'font-family:Microsoft YaHei;padding:0 16mm;">{header_left}</div>')
        r = send('Page.printToPDF', {
            'printBackground': True,
            'paperWidth': 8.27, 'paperHeight': 11.69,
            'marginTop': 0.79, 'marginBottom': 0.71,
            'marginLeft': 0.63, 'marginRight': 0.63,
            'displayHeaderFooter': True,
            'headerTemplate': header, 'footerTemplate': footer,
        })
        data = r.get('result', {}).get('data')
        if not data:
            raise RuntimeError('printToPDF 无数据: ' + json.dumps(r)[:500])
        with open(pdf_path, 'wb') as f:
            f.write(base64.b64decode(data))
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


def edge_print_fallback(edge, html_path, pdf_path):
    subprocess.run([
        edge, '--headless=new', '--disable-gpu', '--no-first-run',
        '--no-default-browser-check',
        f'--print-to-pdf={pdf_path}',
        '--print-to-pdf-no-header',
        'file:///' + html_path.replace('\\', '/'),
    ], check=True, timeout=120)


def main():
    manual_md = build_manual()
    white_md = build_whitepaper()
    full_md = build_full()
    print('[OK] merged:', os.path.basename(manual_md), os.path.basename(white_md),
          os.path.basename(full_md))
    if '--skip-pdf' in sys.argv:
        return
    edge = find_edge()
    if not edge:
        raise SystemExit('未找到 Edge，可先合并 Markdown 后用其他工具转 PDF')
    jobs = [
        (manual_md, os.path.join(DOCS, '择日大师_用户操作手册_v2.2.1.pdf'),
         '专业级正五行择日软件 · 用户操作手册 v2.2.1', True, '2-2'),
        (white_md, os.path.join(DOCS, '择日大师_算法与典据白皮书_v2.2.1.pdf'),
         '专业级正五行择日软件 · 算法与典据白皮书 v2.2.1', True, '1-2'),
        # 完整说明书：目录靠 Markdown 里的 [TOC] 标记，此处 with_toc=False
        (full_md, os.path.join(DOCS, '择日大师_完整说明书_v2.2.1.pdf'),
         '专业级正五行择日软件 · 完整说明书 v2.2.1', False, '1-2'),
    ]
    for md_path, pdf_path, header, with_toc, toc_depth in jobs:
        html = md_to_html(read(md_path), header, with_toc, toc_depth)
        html_path = md_path[:-3] + '.html'
        write(html_path, html)
        try:
            cdp_pdf(edge, html_path, pdf_path, header)
            print('[OK] pdf(CDP):', pdf_path)
        except Exception as e:
            print('[WARN] CDP 失败，改走 --print-to-pdf:', e)
            edge_print_fallback(edge, html_path, pdf_path)
            print('[OK] pdf(fallback):', pdf_path)
        # HTML 作为中间产物，PDF 成功后删除
        try:
            os.remove(html_path)
        except OSError:
            pass


if __name__ == '__main__':
    main()
