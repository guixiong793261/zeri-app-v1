# -*- coding: utf-8 -*-
"""北山排查探针A：2025年壬山丙向"年冲山"逐日实测
目标：确认 check_chong_shan 年支判定为何不是全年恒真，89天的构成是什么
只读：不修改任何业务代码"""
import sys, io, datetime as dt, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'd:\自编择日软件\专业级正五行择日软件')
sys.path.insert(0, str(ROOT))
from modules.四柱计算器 import calculate_sizhu
from modules.二十四山择吉天机 import check_mountain_day, check_chong_shan, get_mountain_data

MOUNTAIN = '壬山丙向'

# 0. 静态数据快照
md = get_mountain_data(MOUNTAIN)
ai = (md or {}).get('avoid_info', {})
print('=== 壬山丙向 avoid_info.chongshan =', repr(ai.get('chongshan')))
print('=== check_chong_shan(壬山丙向, 巳) =', check_chong_shan(MOUNTAIN, '巳'))
print('=== check_chong_shan(壬山丙向, 辰) =', check_chong_shan(MOUNTAIN, '辰'))

# 1. 逐日实测
hit_days = []          # 年冲山出现日
year_zhi_set = {}      # year_zhi 分布
veto_by_reason = {}    # 凶煞条目计数
total_veto = 0
d = dt.date(2025, 1, 1)
while d <= dt.date(2025, 12, 31):
    sz = calculate_sizhu(d, 12, 0)
    di = {
        'year_gan': sz.get('year_gan', ''), 'year_zhi': sz.get('year_zhi', ''),
        'month_gan': sz.get('month_gan', ''), 'month_zhi': sz.get('month_zhi', ''),
        'day_gan': sz.get('day_gan', ''), 'day_zhi': sz.get('day_zhi', ''),
        'hour_gan': sz.get('hour_gan', ''), 'hour_zhi': sz.get('hour_zhi', ''),
        'year': d.year,
    }
    yz = di['year_zhi']
    year_zhi_set[yz] = year_zhi_set.get(yz, 0) + 1
    r = check_mountain_day(di, MOUNTAIN, '修造')
    if not r.get('可用', True):
        total_veto += 1
        for s in r.get('凶煞', []):
            key = str(s)
            veto_by_reason[key] = veto_by_reason.get(key, 0) + 1
            if key == '年冲山':
                hit_days.append((str(d), yz, di['month_zhi'], di['day_zhi']))
    d += dt.timedelta(days=1)

print('\n=== 2025 壬山丙向 check_mountain_day 否决总天次 =', total_veto)
print('=== year_zhi 分布 =', year_zhi_set)
print('=== 凶煞条目计数（TOP）:')
for k, v in sorted(veto_by_reason.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')

print(f'\n=== "年冲山"出现天次 = {len(hit_days)}')
print('=== 前5天 =', hit_days[:5])
print('=== 后5天 =', hit_days[-5:])

# 2. 验证假设：年冲山出现日 的 year_zhi 都是什么？
yz_in_hits = {}
for _, yz, _, _ in hit_days:
    yz_in_hits[yz] = yz_in_hits.get(yz, 0) + 1
print('=== 年冲山出现日的 year_zhi 分布 =', yz_in_hits)

json.dump({'hit_days': hit_days, 'veto_by_reason': veto_by_reason,
           'year_zhi_set': year_zhi_set, 'total_veto': total_veto},
          open(r'C:\Temp\beishan_probe_a.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('SAVED C:\\Temp\\beishan_probe_a.json')
