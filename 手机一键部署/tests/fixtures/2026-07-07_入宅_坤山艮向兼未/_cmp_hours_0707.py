# -*- coding: utf-8 -*-
import io, json, sys
from datetime import date
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root = r'd:\自编择日软件\专业级正五行择日软件'
sys.path.insert(0, root)
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
from modules.喜用神计算器 import calculate_xishen_yongshen

raw = json.load(open(r'C:\Temp\owners_0707.json', encoding='utf-8'))
owners = []
for o in raw:
    bd = date(int(o['y']), int(o['m']), int(o['d']))
    hh = int(o.get('hh', 12))
    xy = calculate_xishen_yongshen(calculate_sizhu(bd, hh, int(o.get('mm', 0))))
    owners.append({'role': o.get('role', ''), '性别': o.get('gender', ''),
                   'name': o.get('name', ''), 'birth_date': bd,
                   'birth_hour': hh, 'birth_minute': int(o.get('mm', 0)),
                   'xishen': xy[0], 'yongshen': xy[1]})

d = date(2026, 7, 7)
shan = '坤山艮向兼未'
hours = [(0,'子'),(2,'丑'),(4,'寅'),(6,'卯'),(8,'辰'),(10,'巳'),
         (12,'午'),(14,'未'),(16,'申'),(18,'酉'),(20,'戌'),(22,'亥')]
rows = []
for hh, hz in hours:
    sz = calculate_sizhu(d, hh, 0)
    sz['year'], sz['month'], sz['day'], sz['date'] = 2026, 7, 7, d
    r = calculate_score(sz, '入宅', owners, '阳宅', shan,
                        None, None, None, None, None, zeli_mode='pure')
    veto = len(r.get('veto_reasons') or [])
    ss = int(any(isinstance(s, dict) and '杀师' in str(s.get('name', ''))
                 for s in (r.get('shensha_list') or [])))
    wx = int((r.get('score_details') or {}).get('五行评分') or 0)
    sc = int(r.get('score') or 0)
    rows.append((hh, hz, sz['月柱'], sz['时柱'], sc, veto, ss, wx))
    print(f"hh={hh:2d} {hz} 月柱={sz['月柱']} 时柱={sz['时柱']} "
          f"总分={sc:4d} 否决={veto} 杀师={ss} 五行原始={wx}")

# 复刻 _rescan_best_hour 比较元组（忽略分金预览，fl/fd=0）：
#   key=(veto, post_score, -杀师, fl, 五行)，candidate > current 则替换
print('\n--- _rescan_best_hour 择优（init=12点午时，严格 > 才替换）---')
cur = next(x for x in rows if x[0] == 12)
def key(x):
    return (x[5], x[4], -x[6], 0, x[7])
for x in rows:
    if x[0] == 12:
        continue
    if key(x) > key(cur):
        print(f"  {x[3]}({x[2]}) 替换 {cur[3]}({cur[2]})  key={key(x)} > {key(cur)}")
        cur = x
print(f"  最终代表：{cur[3]} 月柱={cur[2]} 总分={cur[4]}")

# 入宅建除在两个口径下的值
from modules.shensha.marriage_shensha import get_jianchu
print('\nget_jianchu(date) 固定12点口径 =', get_jianchu(d))
from modules.shensha.marriage_shensha import zhi_index
_jc = ['建','除','满','平','定','执','破','危','成','收','开','闭']
for hh in (4, 12):
    s = calculate_sizhu(d, hh, 0)
    # 日支午
    off = (zhi_index('午') - zhi_index(s['month_zhi'])) % 12
    print(f"hh={hh:2d} 月支={s['month_zhi']} 按真实时柱月建→建除={_jc[off]}")
