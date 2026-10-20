# -*- coding: utf-8 -*-
"""2026 全年回扫（12:00 午时，15 事项，owners=[]，阳宅）：输出 CSV。

用法：python sweep_year.py <ROOT> <OUT.csv>
"""
import csv
import datetime as dt
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score

EVENTS = ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '开业',
          '安床', '作灶', '安葬', '入学', '求医', '签约', '通用']
WATCH = ['土符', '红嘴朱雀', '受死日', '岁破', '病符', '十恶大败', '大时',
         '土王用事', '劫煞', '天吏', '大煞', '八专', '四击']

rows = []
d = dt.date(2026, 1, 1)
while d <= dt.date(2026, 12, 31):
    sz = calculate_sizhu(d, 12, 0)
    for ev in EVENTS:
        r = calculate_score(sz, ev, owners=[], house_type='阳宅')
        sd = r.get('score_details') or {}
        sl = r.get('shensha_list') or []
        names = {x.get('name'): x.get('score', 0) for x in sl}
        rows.append([d.isoformat(), ev, sd.get('总分'), r.get('level'),
                     sd.get('五行评分'),
                     1 if '强制归零' in str(sd.get('说明', '')) else 0,
                     '|'.join('%s%+d' % (k, v) for k, v in names.items()
                              if k in WATCH)])
    d += dt.timedelta(days=1)

with open(OUT, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['date', 'event', 'total', 'level', 'wx', 'zeroed', 'watch'])
    w.writerows(rows)
print('写出 %d 行' % len(rows))
