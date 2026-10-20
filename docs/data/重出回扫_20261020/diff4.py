# -*- coding: utf-8 -*-
"""四日期 12:00 条目级 diff（新旧）。用法：python diff4.py"""
import csv
import io
import json
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
lv_o, lv_n = {}, {}
for tag, path, store in (('o', r'C:\Temp\lv_old.txt', lv_o),
                         ('n', r'C:\Temp\lv_new.txt', lv_n)):
    for line in open(path, encoding='utf-8'):
        line = line.strip().lstrip('\ufeff')
        p = line.split('|')
        if len(p) == 4:
            store[(p[0], p[1])] = (p[2], p[3])

out = {}
for d in ('2026-11-04', '2026-10-23', '2026-07-24', '2026-06-01'):
    print('\n===== %s =====' % d)
    out[d] = []
    for ev in ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '开业',
               '安床', '作灶', '安葬', '入学', '求医', '签约', '通用']:
        k = (d, ev, '12')
        a, b = o[k], n[k]
        ow, nw = split(a['shensha']), split(b['shensha'])
        added = {x: nw[x] for x in nw if x not in ow}
        removed = {x: ow[x] for x in ow if x not in nw}
        changed = {x: (ow[x], nw[x]) for x in ow if x in nw and ow[x] != nw[x]}
        lo, ln = lv_o.get((d, ev)), lv_n.get((d, ev))
        rec = {'date': d, 'event': ev, 'old_total': a['total'],
               'new_total': b['total'],
               'delta': int(float(b['total'])) - int(float(a['total'])),
               'old_level': lo[1] if lo else None,
               'new_level': ln[1] if ln else None,
               'added': added, 'removed': removed, 'changed': changed,
               'ss_sum_old': sum(ow.values()), 'ss_sum_new': sum(nw.values())}
        out[d].append(rec)
        if rec['delta'] or added or removed or changed:
            print(' %-4s %s→%s (%+d) %s→%s' % (
                ev, a['total'], b['total'], rec['delta'],
                lo[1] if lo else '?', ln[1] if ln else '?'))
            if removed:
                print('    消失:', removed)
            if added:
                print('    新增:', added)
            if changed:
                print('    变分:', changed)

json.dump(out, open(r'C:\Temp\diff4.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\nJSON -> C:\\Temp\\diff4.json')
