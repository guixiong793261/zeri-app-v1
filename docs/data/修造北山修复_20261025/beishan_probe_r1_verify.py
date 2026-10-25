# -*- coding: utf-8 -*-
"""R1 对拍快照：2025/2026 壬山/癸山 check_mountain_day 层年冲山释放与岁破起例
只读：不修改任何业务代码"""
import sys, io, json, datetime as dt, collections
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'd:\自编择日软件\专业级正五行择日软件')
sys.path.insert(0, str(ROOT))
from modules.四柱计算器 import calculate_sizhu
from modules.二十四山择吉天机 import check_mountain_day, check_chong_shan

def scan(year, mountain):
    cnt = collections.Counter()
    nian = 0
    d = dt.date(year, 1, 1)
    while d <= dt.date(year, 12, 31):
        sz = calculate_sizhu(d, 12, 0)
        di = {
            'year_gan': sz.get('year_gan', ''), 'year_zhi': sz.get('year_zhi', ''),
            'month_gan': sz.get('month_gan', ''), 'month_zhi': sz.get('month_zhi', ''),
            'day_gan': sz.get('day_gan', ''), 'day_zhi': sz.get('day_zhi', ''),
            'hour_gan': sz.get('hour_gan', ''), 'hour_zhi': sz.get('hour_zhi', ''),
            'year': d.year,
        }
        r = check_mountain_day(di, mountain, '修造')
        if not r.get('可用', True):
            for s in r.get('凶煞', []):
                cnt[str(s)] += 1
                if str(s) == '年冲山':
                    nian += 1
        d += dt.timedelta(days=1)
    return cnt, nian

out = {}
for y in (2025, 2026):
    for m in ('壬山丙向', '癸山丁向'):
        cnt, nian = scan(y, m)
        out[f'{y}_{m}'] = {'年冲山': nian, '全部凶煞': dict(cnt)}
        print(f'{y} {m}: 年冲山={nian}  全部={dict(cnt)}')
        # 兼向口径回归
        for bk in ('壬山丙向兼亥巳', '壬山丙向兼子午', '癸山丁向兼子午'):
            pass

# 兼向静态规则回归
print('\n=== 兼向回归（静态数据应保持原口径） ===')
print('壬山丙向兼亥巳 忌巳:', check_chong_shan('壬山丙向兼亥巳', '巳'),
      '忌午:', check_chong_shan('壬山丙向兼亥巳', '午'))
print('壬山丙向兼子午 忌午:', check_chong_shan('壬山丙向兼子午', '午'),
      '忌巳:', check_chong_shan('壬山丙向兼子午', '巳'))
print('子山午向 忌午:', check_chong_shan('子山午向', '午'),
      '忌子:', check_chong_shan('子山午向', '子'))
print('午山子向 忌子:', check_chong_shan('午山子向', '子'))

json.dump(out, open(r'C:\Temp\beishan_probe_r1_verify.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('SAVED C:\\Temp\\beishan_probe_r1_verify.json')
