# -*- coding: utf-8 -*-
"""全年回扫最终汇总（区分门槛归零，输出 JSON）。"""
import collections
import csv
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def load(p):
    return {(r['date'], r['event']): r for r in csv.DictReader(
        open(p, encoding='utf-8-sig'))}


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


o, n = load(r'C:\Temp\yr_old.csv'), load(r'C:\Temp\yr_new.csv')

st = collections.Counter()
delta_ev = collections.Counter()
lv = collections.Counter()
down = []
up = 0
for k in o:
    a, b = o[k], n[k]
    z = a['zeroed'] == '1' or b['zeroed'] == '1'
    d = int(float(b['total'])) - int(float(a['total']))
    if z:
        st['zeroed'] += 1
    if d:
        st['changed_all'] += 1
        if z:
            st['changed_zeroed'] += 1
        else:
            st['changed_inscope'] += 1
            delta_ev[k[1]] += d
    if a['level'] != b['level']:
        st['lv_all'] += 1
        if z:
            st['lv_zeroed'] += 1
        else:
            st['lv_inscope'] += 1
        lv[(a['level'], b['level'])] += 1
    if not z and d < 0 and a['level'] != b['level']:
        down.append((d, k[0], k[1], a['total'], b['total'],
                     a['level'], b['level'], b['watch']))
    if not z and d > 0 and a['level'] != b['level']:
        up += 1

print('单元格 %d' % len(o))
for kk in ('changed_all', 'changed_zeroed', 'changed_inscope',
           'lv_all', 'lv_zeroed', 'lv_inscope', 'zeroed'):
    print('  %-16s %d' % (kk, st[kk]))
print('口径内降档 %d／升档 %d' % (len(down), up))
print('\n口径内 Δ合计（按事项）')
for e, v in delta_ev.most_common():
    print('  %-4s %+7d' % (e, v))
print('\n口径内等级迁移（前 12）')
for (x, y), v in lv.most_common():
    if x != y and not (x == '★★★★★ 上吉' or y == '★★★★★ 上吉'):
        pass
for (x, y), v in lv.most_common(14):
    print('  %s → %s : %d' % (x, y, v))
print('\n口径内降档（最重 10）')
for d, ds, ev, t1, t2, l1, l2, w in sorted(down)[:10]:
    print('  %s %-4s %s→%s (%+d) %s→%s | %s' % (ds, ev, t1, t2, d, l1, l2, w))
print('\n口径内升档（最重 10）')
for d, ds, ev, t1, t2, l1, l2, w in sorted(down)[::-1][:0]:
    pass
top_up = []
for k in o:
    a, b = o[k], n[k]
    if a['zeroed'] == '1' or b['zeroed'] == '1':
        continue
    d = int(float(b['total'])) - int(float(a['total']))
    if d > 0 and a['level'] != b['level']:
        top_up.append((d, k[0], k[1], a['total'], b['total'], a['level'],
                       b['level'], b['watch']))
for d, ds, ev, t1, t2, l1, l2, w in sorted(top_up)[::-1][:10]:
    print('  %s %-4s %s→%s (%+d) %s→%s | %s' % (ds, ev, t1, t2, d, l1, l2, w))

json.dump({
    'cells': len(o),
    'changed_all': st['changed_all'],
    'changed_zeroed': st['changed_zeroed'],
    'changed_inscope': st['changed_inscope'],
    'lv_all': st['lv_all'], 'lv_zeroed': st['lv_zeroed'],
    'lv_inscope': st['lv_inscope'],
    'zeroed_cells': st['zeroed'],
    'down_inscope': len(down), 'up_inscope': up,
    'delta_by_event': dict(delta_ev),
    'delta_by_event_zeroed_included': None,
    'level_pairs': {'%s->%s' % k: v for k, v in lv.items()},
    'down_samples': [{'date': ds, 'event': ev, 'old': t1, 'new': t2,
                      'delta': d, 'old_level': l1, 'new_level': l2,
                      'watch': w} for d, ds, ev, t1, t2, l1, l2, w
                     in sorted(down)[:20]],
    'up_samples': [{'date': ds, 'event': ev, 'old': t1, 'new': t2,
                    'delta': d, 'old_level': l1, 'new_level': l2,
                    'watch': w} for d, ds, ev, t1, t2, l1, l2, w
                   in sorted(top_up)[::-1][:20]],
}, open(r'C:\Temp\yr_final.json', 'w', encoding='utf-8'),
    ensure_ascii=False, indent=1)
print('\nJSON -> C:\\Temp\\yr_final.json')
