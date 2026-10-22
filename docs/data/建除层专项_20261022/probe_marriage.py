# -*- coding: utf-8 -*-
"""嫁娶通道建除计分补测（只读）。"""
import io, sys, datetime, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score

STARS = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
seen = {}
per = {s: {'days': 0, 'sum': 0} for s in STARS}
d = datetime.date(2026, 1, 1)
while d <= datetime.date(2026, 12, 31):
    sz = calculate_sizhu(d, 12, 0)
    sz.update({'year': d.year, 'month': d.month, 'day': d.day, 'date': d})
    r = calculate_score(sz, '嫁娶')
    blob = json.dumps(r, ensure_ascii=False, default=str)
    hits = re.findall(r'小黄道[^"，,\n]{0,14}', blob)
    star = [m for m in STARS if ('小黄道' + m) in blob]
    if star:
        st = star[0]
        per[st]['days'] += 1
        for h in hits:
            if st in h:
                seen.setdefault(st, set()).add(h)
    else:
        seen.setdefault('NONE', set()).add('no-xhd')
    d += datetime.timedelta(days=1)
print('嫁娶 小黄道命中天数：', {s: per[s]['days'] for s in STARS})
print('文案样例：', {k: sorted(v)[:3] for k, v in seen.items()})
print('r keys:', [k for k in json.loads(json.dumps(calculate_score(
    dict(calculate_sizhu(datetime.date(2026, 3, 5), 12, 0), year=2026, month=3, day=5,
         date=datetime.date(2026, 3, 5)), '嫁娶'), ensure_ascii=False)) if ('婚' in k or 'detail' in k or '黄' in k)])
