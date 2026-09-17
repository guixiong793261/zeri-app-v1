# -*- coding: utf-8 -*-
"""端到端验证 _inject_best_hour_to_result 在交节日把月柱纠正为真实时柱(甲午)。"""
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

raw = json.load(open(r'C:\Temp\owners_0707.json', encoding='utf-8'))
gui, norm = [], []
for o in raw:
    bd = date(int(o['y']), int(o['m']), int(o['d']))
    hh = int(o.get('hh', 12))
    xy = calculate_xishen_yongshen(calculate_sizhu(bd, hh, int(o.get('mm', 0))))
    gui.append({'role': _V(o.get('role','')), 'name': _V(o.get('name','')),
                'gender': _V(o.get('gender','')), 'year': _V(o['y']),
                'month': _V(o['m']), 'day': _V(o['d']), 'hour': _V(hh),
                'minute': _V(int(o.get('mm',0))), 'xishen': _V(xy[0]),
                'yongshen': _V(xy[1])})
    norm.append({'role': o.get('role',''), '性别': o.get('gender',''),
                 'name': o.get('name',''), 'birth_date': bd, 'birth_hour': hh,
                 'birth_minute': int(o.get('mm',0)), 'xishen': xy[0], 'yongshen': xy[1]})

d = date(2026, 7, 7)
shan = '坤山艮向兼未'
# 扫日基准：12:00（已交小暑→乙未月）
wushu = calculate_sizhu(d, 12, 0)
wushu.update({'year': 2026, 'month': 7, 'day': 7, 'date': d})
print('12点基准四柱：', wushu['年柱'], wushu['月柱'], wushu['日柱'], wushu['时柱'])
score_result = calculate_score(wushu, '入宅', norm, '阳宅', shan,
                               None, None, None, None, None, zeli_mode='pure')
print('12点基准评分：', score_result.get('score'))

result = {'date': '2026-07-07',
          'sizhu': f"{wushu['年柱']} {wushu['月柱']} {wushu['日柱']} {wushu['时柱']}",
          'score': score_result.get('score'), 'level': score_result.get('level')}

# 加载主程序，绑定真实方法到轻量 fake
spec = importlib.util.spec_from_file_location('zhuchengxu', root + r'\主程序.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class FakeApp:
    shan_xiang = _V(shan)
    jian_xiang = _V('')
    zaozhu_mode = None
    def _get_zeli_mode(self): return 'pure'

app = FakeApp()
app._inject = types.MethodType(mod.ZeriApp._inject_best_hour_to_result, app)
app._inject(result, score_result, '入宅', norm, d, wushu,
            house_type='阳宅', shan_xiang=shan)

print('\n===== 注入后 =====')
print('result[sizhu] =', result['sizhu'])
sz = score_result.get('sizhu') if isinstance(score_result.get('sizhu'), dict) else {}
print('detail月柱 =', sz.get('月柱'), ' 时柱 =', sz.get('时柱'))
print('总分 =', score_result.get('score'), ' 等级 =', score_result.get('level'))
print('宜忌：')
for x in score_result.get('ji_list', []):
    print('  忌:', x)
det = (score_result.get('wu_xing_result') or {}).get('details')
print('五行详情类型:', type(det).__name__)
# 综合评语里的日主/月支
reason = score_result.get('reason') or ''
rtext = ' '.join(map(str, reason)) if isinstance(reason, (list, tuple)) else str(reason)
for kw in ('月令午', '月令未', '午中', '未中', '自刑', '六合', '建日', '闭日'):
    if kw in rtext:
        print('评语含:', kw)
