# -*- coding: utf-8 -*-
"""批次 1 影响面基线/快照探针（T0 改前 / T1 改后）。

用法：
  python docs/data/建除层专项_批次1_20261022/probe_channel_totals.py t0_before
  python docs/data/建除层专项_批次1_20261022/probe_channel_totals.py t1_after

只读：不修改源码、分值、键表。退出码 0=断言全过，1=有 FAIL。
"""
import io
import os
import sys
import json
import re
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = r'd:\自编择日软件\专业级正五行择日软件'
OUT = os.path.join(ROOT, 'docs', 'data', '建除层专项_批次1_20261022')
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, ROOT)

FAILS = []
NCHK = [0]


def check(name, cond, detail=''):
    NCHK[0] += 1
    print('[%s] %s %s' % ('PASS' if cond else 'FAIL', name, detail))
    if not cond:
        FAILS.append(name)


def dump(fn, obj):
    p = os.path.join(OUT, fn)
    with io.open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
    return p


ZH = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
STARS = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
XIONG = set('建满平收破闭')
JI = set('除危定执成开')
EVENTS = ['修造', '动土', '拆舍', '入宅', '移徙', '嫁娶', '安葬', '安床',
          '出行', '开业', '作灶', '入学', '求医', '签约', '通用']

from modules.四柱计算器 import calculate_sizhu            # noqa: E402
from modules.今日黄历 import calc_jianchu                 # noqa: E402
from modules.黄道 import 黄道计算器                        # noqa: E402
from modules.shensha.marriage_shensha import get_jianchu  # noqa: E402
from modules.shensha.通用神煞 import CommonShenShaChecker as _CSC  # noqa: E402
from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt as _XZEXT  # noqa: E402
from modules.shensha.开业神煞 import OpeningShenShaChecker as _OSC  # noqa: E402
from modules.评分器 import calculate_score                # noqa: E402


def canon(m, d):
    return STARS[(ZH.index(d) - ZH.index(m)) % 12]


def star_of(name):
    if name in ('满日', '成日', '破日', '闭日'):
        return name[0]
    if name.startswith('建除十二神-'):
        return name.split('-', 1)[1]
    if name.startswith('小黄道-'):
        return name.split('-', 1)[1]
    return None


tag = sys.argv[1] if len(sys.argv) > 1 else 't0_before'

# ============ 网格：144 格 × 5 路（含开业四谓词） ============
print('\n=== 144 格表源与谓词 ===')
h = 黄道计算器()
grid_err = []
inst_common = object.__new__(_CSC)
inst_open = object.__new__(_OSC)
_xz = _XZEXT()
_cap = [None]
_xz._add_shensha = lambda name, score, desc='': _cap.__setitem__(0, name)
pred = {'满': [], '成': [], '闭': [], '破': []}
for m in ZH:
    for d in ZH:
        exp = canon(m, d)
        got = {
            '黄道': h._calculate_xiao_huang_dao(m, d)['name'],
            '今日黄历': calc_jianchu(m, d),
            '通用': _CSC._get_xiao_huangdao(inst_common, d, m),
        }
        _cap[0] = None
        _xz._check_jianchu({'month_zhi': m, 'day_zhi': d})
        nm = _cap[0] or ''
        got['修造扩展'] = nm.split('-', 1)[1] if '-' in nm else None
        for k, v in got.items():
            if v != exp:
                grid_err.append({'month_zhi': m, 'day_zhi': d, 'path': k,
                                 'exp': exp, 'got': v})
        for s in pred:
            fn = {'满': '_is_manri', '成': '_is_chengri',
                  '闭': '_is_biari', '破': '_is_pori'}[s]
            if getattr(inst_open, fn)({'month_zhi': m, 'day_zhi': d}):
                pred[s].append('%s%s' % (m, d))
pred_wrong = {}
for s, hits in pred.items():
    exp_hits = ['%s%s' % (m, d) for m in ZH for d in ZH if canon(m, d) == s]
    if set(hits) != set(exp_hits):
        pred_wrong[s] = {'extra': sorted(set(hits) - set(exp_hits))[:20],
                         'missing': sorted(set(exp_hits) - set(hits))[:20],
                         'n_extra': len(set(hits) - set(exp_hits)),
                         'n_missing': len(set(exp_hits) - set(hits))}
dump('%s_grid.json' % tag, {'errors': grid_err, 'predicate_wrong': pred_wrong,
                            'predicate_hits': {k: len(v) for k, v in pred.items()}})
check('144 格 4 路表源等值', not grid_err, 'diff=%d' % len(grid_err))
print('谓词偏差：%s' % json.dumps(pred_wrong, ensure_ascii=False))

# ============ 2026 全年 15 通道 ============
print('\n=== 2026 全年 15 通道总分 ===')
d0, d1 = datetime.date(2026, 1, 1), datetime.date(2026, 12, 31)
totals = {ev: 0 for ev in EVENTS}
jc_sum = {ev: 0 for ev in EVENTS}
xiong_nonzero_days = {ev: 0 for ev in EVENTS}
star_days = {ev: {s: 0 for s in STARS} for ev in EVENTS}
shape_err = []
sentinel = None
double_days = []
star_year_err = []
open_days = 0
day = d0
while day <= d1:
    sz = calculate_sizhu(day, 12, 0)
    sz.update({'year': day.year, 'month': day.month, 'day': day.day, 'date': day})
    actual = canon(sz['month_zhi'], sz['day_zhi'])
    for ev in EVENTS:
        r = calculate_score(sz, ev)
        sc_total = r.get('score', 0) or 0
        totals[ev] += sc_total
        lst = r.get('shensha_list', []) or []
        if ev == '入宅' and str(day) == '2026-11-04':
            sentinel = {'score': sc_total, 'level': r.get('level')}
        day_stars = {}
        for s in lst:
            nm = s.get('name', '')
            sc = s.get('score', 0) or 0
            st = star_of(nm)
            if not st:
                continue
            jc_sum[ev] += sc
            day_stars.setdefault(st, 0)
            day_stars[st] += sc
            if nm.startswith('满日') or nm.startswith('成日') or \
               nm.startswith('破日') or nm.startswith('闭日') or nm.startswith('小黄道-'):
                if st != actual:
                    star_year_err.append({'date': str(day), 'event': ev, 'name': nm,
                                          'claimed': st, 'actual': actual})
        for st in day_stars:
            star_days[ev][st] += 1
            if st in XIONG and day_stars[st] > 0:
                xiong_nonzero_days[ev] += 1
        if ev == '开业':
            open_days += 1
            names = [s.get('name') for s in lst]
            if '月破' in names and '破日' in names:
                double_days.append(str(day))
    day += datetime.timedelta(days=1)

result = {
    'tag': tag,
    'events': EVENTS,
    'totals': totals,
    'jianchu_sum': jc_sum,
    'xiong_nonzero_days': xiong_nonzero_days,
    'star_days': star_days,
    'star_year_errors': {'count': len(star_year_err), 'items': star_year_err[:200]},
    'opening_double_days': double_days,
    'sentinel_20261104_inhouse': sentinel,
    'grid_errors': len(grid_err),
    'predicate_wrong': pred_wrong,
}
p = dump('%s_channel_totals.json' % tag, result)
print('输出：%s' % p)
print('总分：%s' % json.dumps(totals, ensure_ascii=False))
print('建除分：%s' % json.dumps(jc_sum, ensure_ascii=False))
print('凶星仍加分天数：%s' % json.dumps(xiong_nonzero_days, ensure_ascii=False))
print('开业月破+破日共现天数：%d' % len(double_days))
print('建星名错：%d' % len(star_year_err))
print('哨兵：%s' % json.dumps(sentinel, ensure_ascii=False))

if FAILS:
    print('\nFAIL %d' % len(FAILS))
    sys.exit(1)
print('\nPASS %d' % NCHK[0])
sys.exit(0)
