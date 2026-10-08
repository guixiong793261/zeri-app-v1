# -*- coding: utf-8 -*-
"""二级降格触发来源核查（2026-10-08，裁定3 分级归属佐证）。

审计中出现 ji_list 为空却被二级触发的日期，用本脚本打印其真实
marriage_details/warnings，确认触发源（厌对、夫星受克等）非误判。

用法：
    python tools/audit/marriage_cap/check_l2_source.py
"""
import datetime as dt
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer

OWNERS = [
    {'name': '欢', 'role': '新娘', '性别': '女', 'birth_date': '1999-04-05'},
    {'name': '文旺', 'role': '新郎', '性别': '男', 'birth_date': '1998-10-13'},
]
rds = Scorer()
for ds in ('2024-04-08', '2025-05-03'):
    d = dt.date.fromisoformat(ds)
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d; sz['year'] = d.year; sz['month'] = d.month; sz['day'] = d.day
    r = rds.score(sz, '嫁娶', owners=OWNERS)
    print(f'--- {ds} level={r["level"]} score={r["score"]} ---')
    print('details:')
    for t in (r.get('marriage_details') or []):
        print('   ', t)
    print('warnings:')
    for w in (r.get('warnings') or []):
        print('   ', w)
    print('reason 末尾:')
    for ln in str(r.get('reason')).split('\n')[-3:]:
        print('   ', ln[:160])
    print()
