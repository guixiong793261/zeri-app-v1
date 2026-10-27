# -*- coding: utf-8 -*-
"""复现并验证 2023-01-29 嫁娶综合评语 tail 大段重复修复（经真实 _inject_best_hour_to_result）。"""
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


raw = json.load(open(r'C:\Temp\owners_0129.json', encoding='utf-8'))
norm = []
for o in raw:
    bd = date(int(o['y']), int(o['m']), int(o['d']))
    hh = int(o.get('hh', 12))
    xy = calculate_xishen_yongshen(calculate_sizhu(bd, hh, int(o.get('mm', 0))))
    norm.append({'role': o.get('role', ''), '性别': o.get('gender', ''),
                 'name': o.get('name', ''), 'birth_date': bd, 'birth_hour': hh,
                 'birth_minute': int(o.get('mm', 0)), 'xishen': xy[0], 'yongshen': xy[1]})
    print(o['role'], '喜用神：', xy)

d = date(2023, 1, 29)
wushu = calculate_sizhu(d, 12, 0)
wushu.update({'year': 2023, 'month': 1, 'day': 29, 'date': d})
print('12点基准四柱：', wushu['年柱'], wushu['月柱'], wushu['日柱'], wushu['时柱'])

score_result = calculate_score(wushu, '嫁娶', norm, '阳宅', None,
                               None, None, None, None, None, zeli_mode='pure')
print('12点基准评分：', score_result.get('score'))

result = {'date': '2023-01-29',
          'sizhu': f"{wushu['年柱']} {wushu['月柱']} {wushu['日柱']} {wushu['时柱']}",
          'score': score_result.get('score'), 'level': score_result.get('level')}

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
app._inject(result, score_result, '嫁娶', norm, d, wushu,
            house_type='阳宅', shan_xiang=None)

print('\n===== 注入后 =====')
print('result[sizhu] =', result['sizhu'])
print('总分 =', score_result.get('score'), ' 等级 =', score_result.get('level'))
reason = str(score_result.get('reason') or '')
print('---- 综合评语 ----')
print(reason)
print('------------------')
_tail = reason.split('月令分析：', 1)[1] if '月令分析：' in reason else ''
checks = {
    '开头=嫁娶要点(无五行前缀)': reason.split('\n')[0].startswith('嫁娶要点：'),
    '月令分析仅1次': reason.count('月令分析：') == 1,
    '日主段仅1次': reason.count('日主：') == 1,
    '地支合局仅1次': reason.count('地支合局：') == 1,
    '命局吉神仅1次': reason.count('命局吉神：') == 1,
    '喜用神段仅1次': reason.count('喜用神：') == 1,
    'tail内大黄道仅1次': _tail.count('大黄道') == 1,
    'tail内小黄道仅1次': _tail.count('小黄道') == 1,
    'tail末宜仅1次': _tail.count('宜：') == 1,
    '无"五行：嫁娶要点"包裹': '五行：嫁娶要点' not in reason,
}
print('\n===== 断言 =====')
ok = True
for k, v in checks.items():
    print(('PASS' if v else 'FAIL'), k)
    ok = ok and v
print('\nRESULT:', 'ALL_PASS' if ok else 'HAS_FAIL')
sys.exit(0 if ok else 1)
