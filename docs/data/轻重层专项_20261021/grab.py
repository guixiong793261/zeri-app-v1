# -*- coding: utf-8 -*-
"""按短语在协纪/考原/陈书中取上下文（只读，核对轻重原文用）。
用法：python grab.py "短语" [窗口] [文件号,文件号]
"""
import io
import json
import os
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

XJ = r'C:\Temp\xj_full'
XL = r'C:\Temp\xl_full'
CZX = r'C:\Temp\czx_full\czx_pages.json'

phrase = sys.argv[1]
win = int(sys.argv[2]) if len(sys.argv) > 2 else 160
only = sys.argv[3].split(',') if len(sys.argv) > 3 else None

corp = []
for n in range(279216, 279255):
    if only and str(n) not in only:
        continue
    corp.append(('协纪', str(n),
                 open(os.path.join(XJ, '%d.txt' % n), encoding='utf-8',
                      errors='replace').read()))
if not only:
    for n in range(359075, 359082):
        corp.append(('考原', str(n),
                     open(os.path.join(XL, '%d.txt' % n), encoding='utf-8',
                          errors='replace').read()))
    for pg, txt in json.load(open(CZX, encoding='utf-8')):
        corp.append(('陈书', 'p%d' % pg, txt or ''))

total = 0
for book, chap, txt in corp:
    i = txt.find(phrase)
    cnt = 0
    while i >= 0:
        total += 1
        cnt += 1
        print('[%s %s] ...%s...' % (book, chap,
                                    txt[max(0, i - win): i + len(phrase) + win]
                                    .replace('\n', ' ')))
        i = txt.find(phrase, i + len(phrase))
        if cnt >= 4:
            break
print('-- total=%d' % total)
