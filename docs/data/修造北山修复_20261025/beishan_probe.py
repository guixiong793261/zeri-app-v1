# -*- coding: utf-8 -*-
"""北山过度否决只读探针：2025（乙巳·煞东）壬山丙向 修造，逐日收集否决源构成"""
import sys, io, json, datetime as dt, collections
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'd:\自编择日软件\专业级正五行择日软件')
sys.path.insert(0, str(ROOT))
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer

for mode in ('feixing', 'pure'):
    sc = Scorer()
    cnt = collections.Counter()
    samples = {}
    nonveto = 0
    d = dt.date(2025, 1, 1)
    while d <= dt.date(2025, 12, 31):
        sz = calculate_sizhu(d, 12, 0)
        sz.update({'date': d, 'year': 2025, 'month': d.month, 'day': d.day})
        r = sc.score(sz, '修造', shan_xiang='壬山丙向', zeli_mode=mode)
        vr = r.get('veto_reasons') or []
        if not vr:
            nonveto += 1
        for v in vr:
            key = str(v)[:28]
            cnt[key] += 1
            samples.setdefault(key, d.isoformat())
        d += dt.timedelta(days=1)
    print(f'== {mode} 壬山丙向 2025: 非否决={nonveto}/365 ==')
    for k, c in cnt.most_common(12):
        print(f'  {c:4} 起={samples[k]}  {k}')

# 对照：子山/癸山 2025 取代表否决源
sc = Scorer()
for sx in ('子山午向', '癸山丁向'):
    cnt2 = collections.Counter()
    d = dt.date(2025, 1, 1)
    while d <= dt.date(2025, 12, 31):
        sz = calculate_sizhu(d, 12, 0)
        sz.update({'date': d, 'year': 2025, 'month': d.month, 'day': d.day})
        r = sc.score(sz, '修造', shan_xiang=sx, zeli_mode='feixing')
        for v in (r.get('veto_reasons') or []):
            cnt2[str(v)[:28]] += 1
        d += dt.timedelta(days=1)
    print(f'== feixing {sx} 2025 否决源TOP5 ==')
    for k, c in cnt2.most_common(5):
        print(f'  {c:4}  {k}')
print('PROBE_DONE')
