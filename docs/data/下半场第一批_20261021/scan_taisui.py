# -*- coding: utf-8 -*-
"""太岁 三库全扫（只读）：判定是否存在「日辰」用忌语境。"""
import json, os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def load():
    c = []
    for n in range(279216, 279255):
        c.append(('协纪', str(n), open(os.path.join(r'C:\Temp\xj_full', '%d.txt' % n), encoding='utf-8').read()))
    for n in range(359075, 359082):
        c.append(('考原', str(n), open(os.path.join(r'C:\Temp\xl_full', '%d.txt' % n), encoding='utf-8').read()))
    for pg, t in json.load(open(r'C:\Temp\czx_full\czx_pages.json', encoding='utf-8')):
        c.append(('陈书', 'p%d' % pg, t or ''))
    return c

res = []
for book, chap, t in load():
    i = 0
    while True:
        i = t.find('太岁', i)
        if i < 0:
            break
        res.append({'book': book, 'chap': chap, 'ctx': t[max(0, i - 90): i + 150].replace('\n', ' ')})
        i += 2

print('总命中', len(res))
from collections import Counter
print(Counter(x['book'] for x in res))
# 日辰嫌疑：出现「日」且在「忌」语境
sus = [x for x in res if ('忌' in x['ctx'] or '不宜' in x['ctx']) and ('日' in x['ctx'])]
print('含忌且含日 命中', len(sus))
for x in sus[:25]:
    print('--', x['book'], x['chap'], '|', x['ctx'][:260])
json.dump(res, open(r'C:\Temp\taisui_scan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
