# -*- coding: utf-8 -*-
"""嫁娶两级降格影响面审计（2026-10-08 拍板，裁定3）。

走产品真实管线（非模拟）：Scorer.score() + calculate_sizhu。
枚举 2024-2027 全部嫁娶日，统计两级等级调整触发面，并核对闭日删宜。
这是台账 §61 中"一级 8.6% / 二级 1.5%"影响面数字的唯一复现入口。

用法：
    python tools/audit/marriage_cap/marriage_cap_audit.py
依赖：须在产品仓内运行（脚本自动定位仓根）。
"""
import datetime as dt
import os
import sys

# 仓根 = 本文件向上四级（tools/audit/marriage_cap/ -> 仓根）
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
stats = {'L1': 0, 'L2': 0, 'NONE': 0}
by_year = {}
samples_l2 = []
samples_l1 = []
d = dt.date(2024, 1, 1)
end = dt.date(2027, 12, 31)
while d <= end:
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d; sz['year'] = d.year; sz['month'] = d.month; sz['day'] = d.day
    r = rds.score(sz, '嫁娶', owners=OWNERS)
    lv = str(r.get('level') or '')
    if '犯忌嫁娶' in lv:
        k = 'L1'; samples_l1.append((str(d), lv))
    elif '降一格' in lv:
        k = 'L2'; samples_l2.append((str(d), lv, r.get('yi_list'), r.get('ji_list')))
    else:
        k = 'NONE'
    stats[k] += 1
    by_year.setdefault(d.year, {'L1': 0, 'L2': 0, 'NONE': 0})[k] += 1
    d += dt.timedelta(days=1)

total = sum(stats.values())
print('=== 总览 2024-2027（演示事主） ===')
for k in ('L1', 'L2', 'NONE'):
    print(f'{k}: {stats[k]} 天 ({stats[k]*100/total:.1f}%)')
print('按年:', by_year)
print(f'L1 样例(前5): {samples_l1[:5]}')
print('L2 样例数:', len(samples_l2))
for s in samples_l2[:8]:
    print('  L2:', s[0], s[1], '| yi=', s[2], '| ji=', s[3])

# 专项：闭日嫁娶日——宜项不得含嫁娶
biri = [s for s in samples_l2 if any('闭日' in str(j) for j in (s[3] or []))]
print(f'\n=== 闭日触发样例: {len(biri)} 个（前5）===')
bad = []
for s in biri:
    if '嫁娶' in (s[2] or []):
        bad.append(s[0])
for s in biri[:5]:
    print('  ', s[0], s[1], '| yi=', s[2], '| ji=', s[3])
print('闭日仍宜嫁娶的异常日:', bad)

# 退出码：出现异常日则非 0
sys.exit(1 if bad else 0)
