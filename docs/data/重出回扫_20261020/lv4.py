# -*- coding: utf-8 -*-
"""四日期 12:00 等级对照（新旧）：python lv4.py <ROOT>"""
import datetime as dt
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score

EVENTS = ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '开业',
          '安床', '作灶', '安葬', '入学', '求医', '签约', '通用']
for s in ('2026-11-04', '2026-10-23', '2026-07-24', '2026-06-01'):
    sz = calculate_sizhu(dt.date.fromisoformat(s), 12, 0)
    for ev in EVENTS:
        r = calculate_score(sz, ev, owners=[], house_type='阳宅')
        sd = r.get('score_details') or {}
        print('%s|%s|%s|%s' % (s, ev, sd.get('总分'), r.get('level')))
