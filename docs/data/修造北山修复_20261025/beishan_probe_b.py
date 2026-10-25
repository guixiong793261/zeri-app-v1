# -*- coding: utf-8 -*-
"""北山排查探针B：评分器层完整否决源统计（不截断key），并追踪正体大凶形态
只读：不修改任何业务代码"""
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
    hit_nianchong = 0
    nonveto = 0
    d = dt.date(2025, 1, 1)
    while d <= dt.date(2025, 12, 31):
        sz = calculate_sizhu(d, 12, 0)
        sz.update({'date': d, 'year': 2025, 'month': d.month, 'day': d.day})
        r = sc.score(sz, '修造', shan_xiang='壬山丙向', zeli_mode=mode)
        vr = [str(v) for v in (r.get('veto_reasons') or [])]
        if not vr:
            nonveto += 1
        for v in vr:
            cnt[v] += 1
            if '年冲山' in v:
                hit_nianchong += 1
        d += dt.timedelta(days=1)
    print(f'== {mode} 壬山丙向 2025: 非否决={nonveto}/365, 含"年冲山"的veto条次={hit_nianchong} ==')
    for k, c in cnt.most_common(20):
        print(f'  {c:4}  {k}')
    print()

json.dump({'note': '完整key不截断'}, open(r'C:\Temp\beishan_probe_b.json', 'w', encoding='utf-8'))
print('PROBE_DONE')
