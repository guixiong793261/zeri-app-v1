# -*- coding: utf-8 -*-
"""8 项现状：SHENSHA_SCORES 注册面 + 2026 各事项实测天数（只读）"""
import io, sys, datetime, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')
from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.事项标准 import SHENSHA_SCORES
ITEMS = ['天恩', '不将日', '不将', '飞廉', '伏断日', '伏断', '反支日', '反支', '月德合', '归忌', '天吏']
EV = ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '开业', '安床', '作灶', '安葬', '入学', '求医', '签约', '通用']
print('=== A. SHENSHA_SCORES 注册 ===')
for it in ITEMS:
    reg = {k[0]: v for k, v in SHENSHA_SCORES.items() if isinstance(k, tuple) and k[1] == it}
    if it in SHENSHA_SCORES:
        reg['(无名事项键)'] = SHENSHA_SCORES[it]
    wild = {k[0]: v for k, v in SHENSHA_SCORES.items() if isinstance(k, tuple) and k[1] == '*'}
    print(it, json.dumps(reg, ensure_ascii=False), '| 通配', json.dumps(wild, ensure_ascii=False))

print()
print('=== B. 2026 实测（365 天 × 15 事项，10:00 时柱） ===')
name_map = {'不将': '不将日', '伏断': '伏断日', '反支': '反支日'}
res = {it: {} for it in ['天恩', '不将日', '飞廉', '伏断日', '反支日', '月德合', '归忌', '天吏']}
d0 = datetime.date(2026, 1, 1)
for ev in EV:
    c = get_checker(ev)
    d = d0
    while d <= datetime.date(2026, 12, 31):
        out = c.check(calculate_sizhu(d, 10, 0), [])
        for o in out:
            n = o['name']
            for tgt in res:
                if n == tgt:
                    rec = res[tgt].setdefault(ev, {'days': 0, 'scores': set()})
                    rec['days'] += 1
                    rec['scores'].add(o['score'])
        d += datetime.timedelta(days=1)
for tgt, evs in res.items():
    tot = sum(v['days'] for v in evs.values())
    print(tgt, '事次数', len(evs), '合计天数', tot)
    for ev, v in evs.items():
        print('   ', ev, v['days'], sorted(v['scores']))
