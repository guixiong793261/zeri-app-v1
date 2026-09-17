# -*- coding: utf-8 -*-
import io, json, sys
from datetime import date
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root = r'd:\自编择日软件\专业级正五行择日软件'
sys.path.insert(0, root)
from modules.四柱计算器 import calculate_sizhu, get_lunar_date
from modules.婚嫁评分算法 import is_sansang, get_day_ganzhi
from modules.评分器 import calculate_score
from modules.喜用神计算器 import calculate_xishen_yongshen

d = date(2023, 1, 11)
li = get_lunar_date(d)
print('农历信息:', li)
print('日柱:', get_day_ganzhi(d))
print('is_sansang(己巳,腊月):', is_sansang(d))

sz = calculate_sizhu(d, 0, 0)  # 甲子时（推荐时柱）
sz.update({'year': 2023, 'month': 1, 'day': 11, 'date': d})
print('四柱:', sz['年柱'], sz['月柱'], sz['日柱'], sz['时柱'])

raw = json.load(open(r'C:\Temp\owners_0111.json', encoding='utf-8'))
norm = []
for o in raw:
    bd = date(int(o['y']), int(o['m']), int(o['d']))
    xy = calculate_xishen_yongshen(calculate_sizhu(bd, int(o.get('hh', 12)), 0))
    norm.append({'role': o['role'], '性别': o['gender'], 'name': o['name'],
                 'birth_date': bd, 'birth_hour': int(o.get('hh', 12)), 'birth_minute': 0,
                 'xishen': xy[0], 'yongshen': xy[1]})

r = calculate_score(sz, '嫁娶', norm, '阳宅', None, None, None, None, None, None, zeli_mode='pure')
print('\n总分:', r.get('score'), '等级:', r.get('level'))
sd = r.get('score_details') or {}
print('\nscore_details 键:')
for k in sd.keys():
    v = sd[k]
    s = str(v)
    print('  -', k, '=', s[:100].replace('\n', ' '))
