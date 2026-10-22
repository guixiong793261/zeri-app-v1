# -*- coding: utf-8 -*-
"""建除层只读盘点探针（2026-10-22，T1/T2/T3/T4/T5/T7）。

只读：不修改任何源码、分值、键表；仅输出 JSON 与 stdout。
退出码：0=全部断言通过；1=有 FAIL。

输出目录：docs/data/建除层专项_20261022/
  v1_matrix.json       12x12 表源穷举
  v2_year.json         2026 全年 + 时柱口径差异
  v3_emission.json     15 通道触发/计分普查
  v4_inversion.json    倒挂清单
  v5_double.json       双计清单
  v7_predicates.json   统一谓词改造影响面
"""
import io
import os
import sys
import json
import re
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = r'd:\自编择日软件\专业级正五行择日软件'
OUT = os.path.join(ROOT, 'docs', 'data', '建除层专项_20261022')
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

from modules.四柱计算器 import calculate_sizhu
from modules.今日黄历 import calc_jianchu
from modules.黄道 import 黄道计算器
from modules.shensha.marriage_shensha import get_jianchu
from modules.shensha.通用神煞 import CommonShenShaChecker as _CSC
from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt as _XZEXT
from modules.评分器 import calculate_score, H1_ANCHOR_MAP
from modules.事项标准 import shensha_score, SHENSHA_SCORES


def canon(m, d):
    return STARS[(ZH.index(d) - ZH.index(m)) % 12]


# ============ T1 12×12 穷举 ============
print('\n=== T1 12x12 表源穷举 ===')
h = 黄道计算器()
# S1 黄道字面表
s1 = {(m, d): h.XIAO_HUANG_DAO_TABLE[m][ZH.index(d)] for m in ZH for d in ZH}
# S2 今日黄历
s2 = {(m, d): calc_jianchu(m, d) for m in ZH for d in ZH}
# S4 通用神煞（实例方法，用哑对象绑定）
s4 = {}
_inst = object.__new__(_CSC)
for m in ZH:
    for d in ZH:
        s4[(m, d)] = _CSC._get_xiao_huangdao(_inst, d, m)
# S5 修造神煞扩展 _check_jianchu（monkeypatch 捕获发射名）
s5 = {}
_xz = _XZEXT()
_cap = [None]
_xz._add_shensha = lambda name, score, desc='': _cap.__setitem__(0, name)
for m in ZH:
    for d in ZH:
        _cap[0] = None
        _xz._check_jianchu({'month_zhi': m, 'day_zhi': d})
        nm = _cap[0] or ''
        s5[(m, d)] = nm.split('-', 1)[1] if '-' in nm else None
# S3 marriage.get_jianchu：显式 month_zhi，选 12 个不同日支的真实日期
_days = {}
_d = datetime.date(2026, 1, 1)
while len(_days) < 12 and _d <= datetime.date(2026, 3, 31):
    _sz = calculate_sizhu(_d, 12, 0)
    _days.setdefault(_sz['day_zhi'], _d)
    _d += datetime.timedelta(days=1)
s3 = {(m, d): get_jianchu(_days[d], m) for m in ZH for d in ZH}

mat = {}
mismatch = []
for m in ZH:
    for d in ZH:
        vals = {'canon': canon(m, d), 'S1_黄道表': s1[(m, d)], 'S2_今日黄历': s2[(m, d)],
                'S3_marriage': s3[(m, d)], 'S4_通用神煞': s4[(m, d)], 'S5_修造扩展': s5[(m, d)]}
        ok = len(set(vals.values())) == 1
        mat['%s月%s日' % (m, d)] = dict(vals, ok=ok)
        if not ok:
            mismatch.append(mat['%s月%s日' % (m, d)])
dump('v1_matrix.json', {'cells': mat, 'mismatch': mismatch,
                        'note': 'canon=(日支序-月支序)%12；S6 rules fallback 依赖日期无法 12x12，归 T2'})
check('T1 144 格 × 5 路全等', not mismatch, 'mismatch=%d' % len(mismatch))

# ============ T2 2026 全年 + 时柱口径 ============
print('\n=== T2 2026 全年与时柱口径 ===')
year_diff = []
hour_diff_days = 0
hour_diff_samples = []
d0, d1 = datetime.date(2026, 1, 1), datetime.date(2026, 12, 31)
d = d0
while d <= d1:
    sz = calculate_sizhu(d, 12, 0)
    m, dz = sz['month_zhi'], sz['day_zhi']
    a = calc_jianchu(m, dz)
    b = h.XIAO_HUANG_DAO_TABLE[m][ZH.index(dz)]
    c = get_jianchu(d, m)
    if not (a == b == c):
        year_diff.append({'date': str(d), 'month_zhi': m, 'day_zhi': dz, 'a': a, 'b': b, 'c': c})
    # 12 时辰月支是否跨节
    ms = set()
    for hh in range(0, 24, 2):
        ms.add(calculate_sizhu(d, hh, 0)['month_zhi'])
    if len(ms) > 1:
        hour_diff_days += 1
        hour_diff_samples.append({'date': str(d), 'months': sorted(ms)})
    d += datetime.timedelta(days=1)
dump('v2_year.json', {'year_diff': year_diff, 'hour_cross_term_days': hour_diff_days,
                      'hour_samples': hour_diff_samples[:40]})
check('T2 全年三路一致（12:00 月支）', not year_diff, 'diff=%d' % len(year_diff))
print('T2 时柱跨节天数（12 时辰月支不唯一）= %d' % hour_diff_days)

# ============ T3/T4/T5 全年触发与计分普查 ============
print('\n=== T3/T4/T5 2026 全年 15 通道普查 ===')
EVENTS = ['修造', '动土', '拆舍', '入宅', '移徙', '嫁娶', '安葬', '安床',
          '出行', '开业', '作灶', '入学', '求医', '签约', '通用']
JC_RE = re.compile(r'(?:建除十二神-|小黄道-)?([建除满平定执破危成收开闭])(?:日)?$')


def star_of(name):
    if name in ('满日', '成日', '破日', '闭日'):
        return name[0]
    if name.startswith('建除十二神-'):
        return name.split('-', 1)[1]
    if name.startswith('小黄道-'):
        return name.split('-', 1)[1]
    return None


h1 = {(ev, ss, tx) for ev, pairs in H1_ANCHOR_MAP.items() for ss, tx in pairs}
emiss = {ev: {} for ev in EVENTS}
star_days = {ev: {s: {'days': 0, 'sum': 0} for s in STARS} for ev in EVENTS}
trigger_err = []
inversion = []
double = []
distinct_names = set()
sentinel = None
agg = {}
day = d0
while day <= d1:
    sz = calculate_sizhu(day, 12, 0)
    sz.update({'year': day.year, 'month': day.month, 'day': day.day, 'date': day})
    actual = canon(sz['month_zhi'], sz['day_zhi'])
    for ev in EVENTS:
        r = calculate_score(sz, ev)
        lst = r.get('shensha_list', []) or []
        if ev == '入宅' and str(day) == '2026-11-04':
            sentinel = (r.get('score'), r.get('level'))
        per_star = {}
        for s in lst:
            nm = s.get('name', '')
            sc = s.get('score', 0) or 0
            st = star_of(nm)
            if not st:
                continue
            distinct_names.add(nm)
            emiss[ev][nm] = emiss[ev].get(nm, 0) + 1
            if st != actual:
                trigger_err.append({'date': str(day), 'event': ev, 'name': nm,
                                    'claimed': st, 'actual': actual, 'score': sc})
            if sc != 0 and st == actual:
                per_star.setdefault(st, []).append((nm, sc))
        for st, items in per_star.items():
            star_days[ev][st]['days'] += 1
            star_days[ev][st]['sum'] += sum(x[1] for x in items)
            k = '%s/%s' % (ev, st)
            agg.setdefault(k, {'days': 0, 'sum': 0, 'multi': 0})
            agg[k]['days'] += 1
            agg[k]['sum'] += sum(x[1] for x in items)
            if len(items) > 1:
                agg[k]['multi'] += 1
                double.append({'date': str(day), 'event': ev, 'star': st, 'items': items})
            if st in XIONG and sum(x[1] for x in items) > 0:
                inversion.append({'date': str(day), 'event': ev, 'star': st,
                                  'items': items, 'sum': sum(x[1] for x in items)})
    day += datetime.timedelta(days=1)

dump('v3_emission.json', {'distinct_names': sorted(distinct_names),
                          'emission_counts': emiss, 'per_star': star_days,
                          'agg': agg})
dump('v3b_trigger_errors.json', {'count': len(trigger_err), 'items': trigger_err,
                                 'by_event_name': {}})
dump('v4_inversion.json', {'count': len(inversion), 'items': inversion})
dump('v5_double.json', {'count': len(double), 'items': double})
check('T3b 建除星名与实际值一致（触发零错）', len(trigger_err) == 0,
      'trigger_err=%d' % len(trigger_err))
check('T4 凶星正向（倒挂）为 0', len(inversion) == 0, 'inversion=%d' % len(inversion))
check('T5 同星双计为 0', len(double) == 0, 'double=%d' % len(double))
check('哨兵 2026-11-04 入宅 = 224', sentinel and sentinel[0] == 224, str(sentinel))

# ============ T7 谓词改造影响面 ============
print('\n=== T7 统一谓词影响面扫描 ===')
PATTERNS = {
    'calc_jianchu': r'calc_jianchu\(',
    'get_jianchu': r'get_jianchu\(',
    '_get_xiao_huangdao': r'_get_xiao_huangdao\(',
    '_check_jianchu': r'_check_jianchu\(',
    '_calculate_xiao_huang_dao': r'_calculate_xiao_huang_dao\(',
    'fallback_get_jianchu': r'fallback_get_jianchu\(',
    'JIANCHU_TABLE': r'JIANCHU_YI|JIANCHU_JI|XIAO_HUANG_DAO_TABLE',
}
scan = {}
for base, dirs, files in os.walk(ROOT):
    if any(x in base for x in ('.git', '__pycache__', '手机一键部署', '统一版')):
        continue
    for f in files:
        if not f.endswith('.py'):
            continue
        p = os.path.join(base, f)
        rel = os.path.relpath(p, ROOT)
        if rel.startswith('docs'):
            continue
        try:
            src = io.open(p, encoding='utf-8').read()
        except Exception:
            continue
        for k, pat in PATTERNS.items():
            for i, line in enumerate(src.splitlines(), 1):
                if re.search(pat, line):
                    scan.setdefault(k, []).append({'file': rel, 'line': i, 'code': line.strip()[:120]})
dump('v7_predicates.json', {'callers': scan,
                            'counts': {k: len(v) for k, v in scan.items()}})
print('T7 调用点数：' + ', '.join('%s=%d' % (k, len(v)) for k, v in scan.items()))

print('\n---')
print('CHECKS=%d FAILS=%d' % (NCHK[0], len(FAILS)))
for f in FAILS:
    print('FAILED: %s' % f)
sys.exit(1 if FAILS else 0)
