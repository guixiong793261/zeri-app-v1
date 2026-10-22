# -*- coding: utf-8 -*-
"""T3b/T4/T5 聚合分析 + T6 卷十原文切片（只读）。"""
import io, os, sys, json, re, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'd:\自编择日软件\专业级正五行择日软件\docs\data\建除层专项_20261022'
XJ = r'C:\Temp\xj_full\279229.txt'


def load(fn):
    with io.open(os.path.join(OUT, fn), encoding='utf-8') as f:
        return json.load(f)


v3 = load('v3_emission.json')
v3b = load('v3b_trigger_errors.json')
v4 = load('v4_inversion.json')

# ---- T3b 触发错聚合 ----
g = collections.Counter()
for it in v3b['items']:
    g[(it['event'], it['name'], it['claimed'])] += 1
print('=== T3b 触发错（星名≠实际建除）===')
for (ev, nm, cl), c in sorted(g.items(), key=lambda x: -x[1]):
    print('  %-4s %-8s 声称=%s  %d 天' % (ev, nm, cl, c))
tot = collections.Counter(it['event'] for it in v3b['items'])
print('  按通道：', dict(tot))

# ---- T4 倒挂聚合 ----
g4 = collections.Counter()
s4 = collections.Counter()
for it in v4['items']:
    g4[(it['event'], it['star'])] += 1
    s4[(it['event'], it['star'])] += it['sum']
print('\n=== T4 倒挂（凶星实际值且合计>0）===')
for (ev, st), c in sorted(g4.items(), key=lambda x: -x[1]):
    print('  %-4s %s  %d 天  合计 %+d  单日均 %+.2f' % (ev, st, c, s4[(ev, st)], s4[(ev, st)] / c))
print('  按通道：', dict(collections.Counter(it['event'] for it in v4['items'])))

# ---- T5 双计：破日/月破同罚 ----
print('\n=== T5 破日×月破 同罚（开业）===')
em = v3['emission_counts'].get('开业', {})
print('  开业发射次数：', {k: v for k, v in sorted(em.items()) if '日' in k or '破' in k})
both = 0
for day, items in v3.get('per_star', {}).items():
    pass
# 从 v5 只覆盖 shensha_list 同名；单独统计同日两罚
d_bl = 0
d0, d1 = __import__('datetime').date(2026, 1, 1), __import__('datetime').date(2026, 12, 31)
import datetime
sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
day = d0
samples = []
while day <= d1:
    sz = calculate_sizhu(day, 12, 0)
    sz.update({'year': day.year, 'month': day.month, 'day': day.day, 'date': day})
    r = calculate_score(sz, '开业')
    names = {x.get('name'): x.get('score') for x in r.get('shensha_list', [])}
    if '月破' in names and '破日' in names:
        both += 1
        if len(samples) < 3:
            samples.append({'date': str(day), '月破': names.get('月破'), '破日': names.get('破日')})
    day += datetime.timedelta(days=1)
print('  同日同时发射 月破 与 破日：%d 天；样例 %s' % (both, samples))

# ---- T6 卷十原文切片 ----
STAR_RE = re.compile(r'(建日|除日|满日|平日|定日|执日|破日|危日|成日|收日|开日|闭日)')
slices = []
with io.open(XJ, encoding='utf-8', errors='replace') as f:
    for i, line in enumerate(f, 1):
        s = line.strip()
        if not s or not STAR_RE.search(s):
            continue
        for m in STAR_RE.finditer(s):
            a = max(0, m.start() - 40)
            b = min(len(s), m.end() + 40)
            slices.append({'line': i, 'star': m.group(1), 'slice': s[a:b]})
with io.open(os.path.join(OUT, 'v6_corpus_slices.json'), 'w', encoding='utf-8') as f:
    json.dump({'source': XJ, 'count': len(slices), 'items': slices}, f, ensure_ascii=False, indent=1)
print('\n=== T6 卷十切片 === 共 %d 条，星名分布：%s' %
      (len(slices), dict(collections.Counter(x['star'] for x in slices))))

# ---- 汇总 JSON ----
summary = {'t3b_trigger': {('%s|%s|%s' % k): v for k, v in g.items()},
           't3b_by_event': dict(tot),
           't4_inversion': {('%s|%s' % k): {'days': v, 'sum': s4[k]} for k, v in g4.items()},
           't4_by_event': dict(collections.Counter(it['event'] for it in v4['items'])),
           't5_poyue_both_days': both,
           't1_mismatch': 0,
           't2_year_diff': 0,
           't2_hour_cross_term_days': 10}
with io.open(os.path.join(OUT, 'v8_summary.json'), 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)
print('\n已写 v8_summary.json')
