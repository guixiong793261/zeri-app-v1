# -*- coding: utf-8 -*-
"""探针v3：找2025年午时（12:00）无吉神制化的日子，验证时冲山（无制化）入忌-15+专项-10"""
import sys, io, datetime as dt
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'd:\自编择日软件\专业级正五行择日软件')
sys.path.insert(0, str(ROOT))
from modules.四柱计算器 import calculate_sizhu
from modules.二十四山择吉天机 import check_chong_shan, check_mountain_day
from modules.评分器 import Scorer

MOUNTAIN = '壬山丙向'
target = None
d = dt.date(2025, 1, 1)
while d <= dt.date(2025, 3, 31):
    sz = calculate_sizhu(d, 12, 0)
    if sz['hour_zhi'] == '午' and check_chong_shan(MOUNTAIN, sz['hour_zhi']):
        di = {k: sz[k] for k in ('year_gan','year_zhi','month_gan','month_zhi','day_gan','day_zhi','hour_gan','hour_zhi')}
        di['year'] = d.year
        r = check_mountain_day(di, MOUNTAIN, '修造')
        shi_warns = [w for w in r.get('警告', []) if '时冲山' in w]
        if shi_warns and any('（无制化）' in w for w in shi_warns):
            target = (d, sz, r)
            break
    d += dt.timedelta(days=1)

if not target:
    print('未找到时冲山（无制化）的日子'); sys.exit(0)

d, sz, r = target
print('命中日 =', d, '日柱 =', sz['day_gan']+sz['day_zhi'], '时柱 =', sz['hour_gan']+sz['hour_zhi'])
print('check_mountain_day 可用 =', r.get('可用', True), '| 警告 =', r.get('警告', []))

sc = Scorer()
sz2 = dict(sz); sz2.update({'date': d, 'year': 2025, 'month': d.month, 'day': d.day})
res = sc.score(sz2, '修造', shan_xiang=MOUNTAIN, zeli_mode='pure')
print('veto =', res.get('veto_reasons'))
hits = [j for j in sc.ji_list if '时冲山' in str(j)]
print('ji_list 时冲山 =', hits)
print('final_score =', sc.final_score)
import json
json.dump({'date': str(d), 'sizhu': sz['hour_gan']+sz['hour_zhi'],
           'check_chong_shan_wu': check_chong_shan(MOUNTAIN, '午'),
           'warnings': r.get('警告', []), 'ji_list_shichong': hits,
           'final_score': sc.final_score},
          open(r'd:\自编择日软件\专业级正五行择日软件\docs\data\修造北山修复_20261025\r2_hour.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('R2_HOUR_PROBE_V3_DONE')
