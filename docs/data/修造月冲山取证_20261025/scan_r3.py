# -*- coding: utf-8 -*-
"""R3 月冲山专项：三库全卷扫描（只读）

冻结词表（v1.0 判据：词表冻结、全卷扫无抽样、命中逐条核读、伪共现排除）：
- 主题词：月冲山 / 月建冲山 / 月令冲山 / 月冲 / 月破 / 月家 / 月建所冲 / 月建对冲 / 月破山 / 山家
- 语境词（宽松，仅统计命中量供聚焦）：冲山

三库层级：协纪主锚（xj_full 39 txt）→ 考原互校（xl_full 7 txt）→ 陈书第三参照（czx_pages.json 1130 页）。
输出：scan_r3.json（逐命中：库/出处/原文节录/前后文）
"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

XJ = r'C:\Temp\xj_full'
XL = r'C:\Temp\xl_full'
CZX = r'C:\Temp\czx_full\czx_pages.json'
OUT = r'C:\Temp\scan_r3.json'

THEME = ['月冲山', '月建冲山', '月令冲山', '月冲', '月破', '月家', '月建所冲',
         '月建对冲', '月破山', '山家月']
LOOSE = ['冲山']

hits = []

def norm(t):
    return re.sub(r'\s+', '', t or '')

def add(lib, src, text, ctx_before, ctx_after):
    hits.append({'库': lib, '出处': src, '原文': norm(text), '前': norm(ctx_before), '后': norm(ctx_after)})

# 协纪 + 考原（txt 全文，逐行 + 前一行后一行）
for lib, d in (('协纪', XJ), ('考原', XL)):
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.txt'):
            continue
        src = fn[:-4]
        path = os.path.join(d, fn)
        with open(path, encoding='utf-8', errors='ignore') as f:
            lines = f.read().split('\n')
        for i, ln in enumerate(lines):
            if any(k in ln for k in THEME):
                add(lib, src, ln, lines[i-1] if i > 0 else '',
                    lines[i+1] if i+1 < len(lines) else '')

# 陈书（页）
czx = json.load(open(CZX, encoding='utf-8'))
for page, text in czx:
    if not text:
        continue
    for k in THEME:
        if k in text:
            add('陈书', f'p{page}', text[:120], '', '')
            break

loose_count = {'协纪': 0, '考原': 0, '陈书': 0}
for lib, d in (('协纪', XJ), ('考原', XL)):
    for fn in sorted(os.listdir(d)):
        if fn.endswith('.txt'):
            with open(os.path.join(d, fn), encoding='utf-8', errors='ignore') as f:
                t = f.read()
            loose_count[lib] += sum(t.count(k) for k in LOOSE)
for page, text in czx:
    if text:
        loose_count['陈书'] += sum(text.count(k) for k in LOOSE)

print(f'主题词命中总数 = {len(hits)}')
from collections import Counter
print('按库:', dict(Counter(h['库'] for h in hits)))
print('宽松词[冲山]命中量(全库):', loose_count)
json.dump({'theme_hits': hits, 'loose_count': loose_count},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('SAVED', OUT)
