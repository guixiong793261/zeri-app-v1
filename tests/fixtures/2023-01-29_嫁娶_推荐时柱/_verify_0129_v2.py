# -*- coding: utf-8 -*-
"""复现 2023-01-29 嫁娶：inject链路，检查推荐时柱/分数/tail重复/夫星项。"""
import io, json, sys, types, importlib.util
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


class _V:
    def __init__(self, v): self.v = '' if v is None else str(v)
    def get(self): return self.v


raw = json.load(open(r'C:\Temp\owners_0111.json', encoding='utf-8'))
norm = []
for o in raw:
    bd = date(int(o['y']), int(o['m']), int(o['d']))
    xy = calculate_xishen_yongshen(calculate_sizhu(bd, int(o.get('hh', 12)), 0))
    norm.append({'role': o['role'], '性别': o['gender'], 'name': o['name'],
                 'birth_date': bd, 'birth_hour': 12, 'birth_minute': 0,
                 'xishen': xy[0], 'yongshen': xy[1]})

d = date(2023, 1, 29)
wushu = calculate_sizhu(d, 12, 0)
wushu.update({'year': 2023, 'month': 1, 'day': 29, 'date': d})
sr0 = calculate_score(wushu, '嫁娶', norm, '阳宅', None, None, None, None, None, None, zeli_mode='pure')
result = {'date': '2023-01-29',
          'sizhu': f"{wushu['年柱']} {wushu['月柱']} {wushu['日柱']} {wushu['时柱']}",
          'score': sr0.get('score'), 'level': sr0.get('level')}

spec = importlib.util.spec_from_file_location('zhuchengxu', root + r'\主程序.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FakeApp:
    shan_xiang = _V('')
    jian_xiang = _V('')
    zaozhu_mode = None
    def _get_zeli_mode(self): return 'pure'


app = FakeApp()
app._inject = types.MethodType(mod.ZeriApp._inject_best_hour_to_result, app)
app._inject(result, sr0, '嫁娶', norm, d, wushu, house_type='阳宅', shan_xiang=None)

print('注入后四柱：', result['sizhu'], ' score=', sr0.get('score'), ' level=', sr0.get('level'))
sd = sr0.get('score_details') or {}
print('五行评分:', sd.get('五行评分'), '原始:', sd.get('五行原始分'),
      ' 月令:', sd.get('月令得分'), ' 喜用:', sd.get('喜用神得分'),
      ' 总分:', sd.get('总分'), ' 否决:', sd.get('否决原因'))
s = 0
for nm, sc in (sr0.get('marriage_details') or []):
    print('   %+4d' % sc, nm[:70])
    try:
        s += int(sc)
    except Exception:
        pass
print('明细加总 =', s)
reason = str(sr0.get('reason') or '')
_tail = reason.split('月令分析：', 1)[1] if '月令分析：' in reason else ''
print('tail内 日主x', _tail.count('日主：'), ' 地支冲害x', _tail.count('地支冲害：'),
      ' 命局吉神x', _tail.count('命局吉神：'),
      ' 开头带五行前缀:', reason.split(chr(10))[0].startswith('五行：'))
print('评语含夫星受克:', '夫星受克' in reason, ' 含冲夫星:', '冲夫星' in reason)
