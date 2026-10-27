# -*- coding: utf-8 -*-
"""复现 GUI 链路：12点基准扫日 + _inject_best_hour_to_result，观察否决日明细结构。"""
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

d = date(2023, 1, 11)
wushu = calculate_sizhu(d, 12, 0)
wushu.update({'year': 2023, 'month': 1, 'day': 11, 'date': d})
print('12点基准四柱：', wushu['年柱'], wushu['月柱'], wushu['日柱'], wushu['时柱'])
sr0 = calculate_score(wushu, '嫁娶', norm, '阳宅', None, None, None, None, None, None, zeli_mode='pure')
print('12点基准: score=', sr0.get('score'), ' 五行=', (sr0.get('score_details') or {}).get('五行评分'),
      ' 顶层marriage_details条数=', len(sr0.get('marriage_details') or []),
      ' score_breakdown=', (sr0.get('wu_xing_result') or {}).get('score_breakdown'))

result = {'date': '2023-01-11',
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

print('\n===== 注入后 =====')
print('result[sizhu] =', result['sizhu'], ' score=', sr0.get('score'))
sd = sr0.get('score_details') or {}
print('score_details 键:', list(sd.keys()))
print('月令详细:', sd.get('月令详细'))
md = sr0.get('marriage_details') or []
print('顶层 marriage_details 条数:', len(md))
for x in md[:20]:
    print('   ', x)
wr = sr0.get('wu_xing_result') or {}
print('score_breakdown:', wr.get('score_breakdown'))
