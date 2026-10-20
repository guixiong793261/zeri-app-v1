# -*- coding: utf-8 -*-
"""四日 720 单元格归因合计（条目级分值差 + 总分差）。"""
import collections
import csv
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def split(s):
    out = {}
    for x in (s or '').split('|'):
        if not x:
            continue
        for i in range(len(x) - 1, 0, -1):
            if x[i] in '+-':
                try:
                    out[x[:i]] = int(x[i:])
                    break
                except ValueError:
                    continue
    return out


def load(p):
    return {(r['date'], r['event'], r['hour']): r for r in csv.DictReader(
        open(p, encoding='utf-8-sig'))}


o, n = load(r'C:\Temp\sw_old.csv'), load(r'C:\Temp\sw_new.csv')
att = collections.Counter()
cells_delta = 0
per_date = collections.Counter()
for k in o:
    a, b = o[k], n[k]
    if a['total'] == 'ERR' or b['total'] == 'ERR':
        continue
    d = int(float(b['total'])) - int(float(a['total']))
    cells_delta += d
    per_date[k[0]] += d
    ow, nw = split(a['shensha']), split(b['shensha'])
    for nm, v in ow.items():
        if nw.get(nm) != v:
            att[nm] += (nw.get(nm, 0) - v)
    for nm, v in nw.items():
        if nm not in ow:
            att[nm] += v
print('720 格总分 Δ 合计 %+d' % cells_delta)
for d, v in per_date.items():
    print('  %s %+d' % (d, v))
print('\n条目级分值差（四日 12 时辰累计）：')
for nm, v in att.most_common():
    print('  %-8s %+7d' % (nm, v))
