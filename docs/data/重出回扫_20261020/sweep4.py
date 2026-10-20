# -*- coding: utf-8 -*-
"""四日期 × 15 事项 × 12 时辰全量重跑（owners=[]，阳宅），输出 CSV 供新旧对照。

用法：python sweep4.py <ROOT> <OUT.csv>
"""
import csv
import datetime as dt
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = sys.argv[1]
OUT = sys.argv[2]
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score

EVENTS = ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '开业',
          '安床', '作灶', '安葬', '入学', '求医', '签约', '通用']
DATES = ['2026-11-04', '2026-10-23', '2026-07-24', '2026-06-01']
HOURS = list(range(0, 24, 2))

rows = []
for s in DATES:
    d = dt.date.fromisoformat(s)
    for ev in EVENTS:
        for h in HOURS:
            sz = calculate_sizhu(d, h, 0)
            try:
                r = calculate_score(sz, ev, owners=[], house_type='阳宅')
                sd = r.get('score_details') or {}
                total = sd.get('总分', r.get('score'))
                veto = len(r.get('veto_reasons') or [])
                names = '|'.join('%s%+d' % (x.get('name'), x.get('score', 0))
                                 for x in (r.get('shensha_list') or []))
            except Exception as e:                 # noqa: BLE001
                total, veto, names = 'ERR:%s' % str(e)[:40], -1, ''
            rows.append([s, ev, h, sz['hour_gan'] + sz['hour_zhi'],
                         total, veto, names])

with open(OUT, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['date', 'event', 'hour', 'hour_pillar', 'total', 'veto', 'shensha'])
    w.writerows(rows)
print('写出 %d 行 -> %s' % (len(rows), OUT))
