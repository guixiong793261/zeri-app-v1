# -*- coding: utf-8 -*-
"""
shensha_score 三级查找改造回归（2026-10-19，移徙休眠键修复·选A）
==================================================================
拍板依据：「移徙修复方向选A」条件②③④——
②三级查找顺序与回退明确：原事项→canonical→通配，逐级命中即返回；
  通配级不得覆盖前两级已命中项；
③多链同拦回归：移徙专属键可命中、且不与入宅通道重复发射；
  78 共有键同值须断言「评分零变化」；
④x4/P2 删除项（10 煞）在移徙通道保持删除，不得因「通配」复活。
前置：cb3f8cb 已删 10 键（条件①）；bb196e7 §四证全表非 canonical 键
仅「入宅←移徙」一族，改造全局影响面上限即移徙 88 键。

验证面：
A. 三级顺序与回退：78 键 shensha_score('移徙',n)==('移徙',n) 值（原事项
   级命中）；与 ('*',n) 交集名逐项断言不被通配覆盖；别名（搬家/迁居）
   落入 canonical 级与入宅同值。
B. 全事项对照零变化：本地复刻旧两级逻辑，对 键表全部事项名 ∪
   EVENT_ALIASES 全别名 × 键表全部煞名 逐对断言 新==旧。
C. 78 共有键评分零变化：shensha_score('移徙',n)==('入宅',n) 值。
D. 10 煞不复活：shensha_score('移徙',n)＝8×None＋月刑-15＋月害-15
   （快照 bb196e7 §二基线）；移徙通道 2026 全年 10 煞零发射。
E. 发射链零变化：入宅/移徙通道 2026 全年逐日发射清单逐项一致、
   总分=1148（改造前基线）；嫁娶总分=-2308（非别名族对照）。

退出码 0=全过 1=有失败。
"""
import io
import os
import sys
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []


def check(name, cond):
    print('[%s] %s' % ('PASS' if cond else 'FAIL', name))
    if not cond:
        FAILS.append(name)


sys.path.insert(0, ROOT)
from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.事项标准 import (SHENSHA_SCORES, shensha_score, canonical_event,
                             EVENT_ALIASES)

D10 = ['月破', '劫煞', '灾煞', '往亡', '月煞', '月刑', '天吏', '大时', '五墓', '月害']
EXPECT10 = {'月破': None, '劫煞': None, '灾煞': None, '往亡': None, '月煞': None,
            '月刑': -15, '天吏': None, '大时': None, '五墓': None, '月害': -15}


def old_score(ev, n, default=None):
    """旧两级逻辑复刻（canonical→通配），作改造前对照。"""
    c = canonical_event(ev)
    if (c, n) in SHENSHA_SCORES:
        return SHENSHA_SCORES[(c, n)]
    if ('*', n) in SHENSHA_SCORES:
        return SHENSHA_SCORES[('*', n)]
    return default


# ============ A：三级顺序与回退 ============
yi = {n: v for (e, n), v in SHENSHA_SCORES.items() if e == '移徙'}
check('移徙键数=78（cb3f8cb 删除后）', len(yi) == 78)
for n, v in yi.items():
    if shensha_score('移徙', n) != v:
        check("原事项级命中：shensha_score('移徙',%r)==%r" % (n, v), False)
        break
else:
    check('原事项级命中：78键 shensha_score(移徙,n)==(移徙,n) 值', True)
# 通配不覆盖前两级：交集名逐项断言
wild_names = {n for (e, n) in SHENSHA_SCORES if e == '*'}
inter_yi = wild_names & set(yi)
ok_cov = all(shensha_score('移徙', n) == yi[n] for n in inter_yi)
check('通配不覆盖原事项命中：(移徙,n)∩(*,n) 交集 %d 名逐项=移徙值' % len(inter_yi),
      ok_cov)
inter_ru = wild_names & {n for (e, n) in SHENSHA_SCORES if e == '入宅'}
ok_cov2 = all(shensha_score('入宅', n) == SHENSHA_SCORES[('入宅', n)] for n in inter_ru)
check('通配不覆盖canonical命中：(入宅,n)∩(*,n) 交集 %d 名逐项=入宅值' % len(inter_ru),
      ok_cov2)
# 别名落入 canonical 级
ok_alias = all(shensha_score(a, n) == shensha_score('入宅', n)
               for a in ('搬家', '迁居') for n in list(yi)[:20])
check('别名（搬家/迁居）落入 canonical 级：抽样20名与入宅同值', ok_alias)

# ============ B：全事项对照零变化（全量遍历） ============
events = {e for (e, n) in SHENSHA_SCORES if e != '*'}
for aliases in EVENT_ALIASES.values():
    events.update(aliases)
names = {n for (e, n) in SHENSHA_SCORES}
pairs = 0
bad = []
for ev in events:
    for n in names:
        pairs += 1
        if shensha_score(ev, n) != old_score(ev, n):
            bad.append((ev, n))
check('全事项×全煞名 新旧逻辑逐对同值（%d 对，差异 %d）' % (pairs, len(bad)),
      not bad)

# ============ C：78 共有键评分零变化 ============
ok78 = all(shensha_score('移徙', n) == SHENSHA_SCORES.get(('入宅', n)) for n in yi)
check('78键 shensha_score(移徙,n)==(入宅,n) 值（评分零变化）', ok78)

# ============ D：10 煞不复活 ============
for n in D10:
    check("shensha_score('移徙',%r)=%r（10煞不复活）" % (n, EXPECT10[n]),
          shensha_score('移徙', n) == EXPECT10[n])


def _run(ev, start, end):
    ck = get_checker(ev)
    days = {}
    cnt10 = {n: 0 for n in D10}
    d = start
    while d <= end:
        sz = calculate_sizhu(d, 10, 0)
        hits = [(s['name'], s['score']) for s in ck.check(sz, [])]
        days[d.isoformat()] = hits
        for n, _ in hits:
            if n in cnt10:
                cnt10[n] += 1
        d += datetime.timedelta(days=1)
    return days, cnt10


y0 = datetime.date(2026, 1, 1)
y1 = datetime.date(2026, 12, 31)
ru_days, ru10 = _run('入宅', y0, y1)
yi_days, yi10 = _run('移徙', y0, y1)
for n in D10:
    check('移徙通道 %s 全年零发射·不复活 (x%d)' % (n, yi10[n]), yi10[n] == 0)

# ============ E：发射链零变化 ============
check('移徙通道==入宅通道 2026 全年逐日发射清单逐项一致',
      all(ru_days[k] == yi_days[k] for k in ru_days))
tot_ru = sum(s for hits in ru_days.values() for _, s in hits)
check('入宅通道全年总分=1148（改造前基线）', tot_ru == 1148)
tot_yi = sum(s for hits in yi_days.values() for _, s in hits)
check('移徙通道全年总分=1148（=入宅，改造前基线）', tot_yi == 1148)
dup = sum(1 for hits in yi_days.values()
          if len([n for n, _ in hits]) != len({n for n, _ in hits}))
check('移徙通道逐日同名至多1条·不与入宅重复发射（重复日=%d）' % dup, dup == 0)
jq_days, _ = _run('嫁娶', y0, y1)
tot_jq = sum(s for hits in jq_days.values() for _, s in hits)
check('嫁娶通道全年总分=-2308（非别名族对照基线）', tot_jq == -2308)

# ============ F：通配不覆盖前两级·边界用例（2026-10-19 拍板提醒项） ============
# 防未来新增通配键时回退：前两级已命中时通配级不得覆盖。三类边界逐条断言，
# 且必须至少含 1 条「值可区分」样本（否则断言空转、无法暴露覆盖风险）。
_alias2canon = {}
for _c, _al in EVENT_ALIASES.items():
    for _a in _al:
        if _a != _c:
            _alias2canon[_a] = _c
_wild = {n: v for (e, n), v in SHENSHA_SCORES.items() if e == '*'}

# F1 原事项级无键 + canonical有键 + 通配有键 → 必须命中 canonical（不得落通配）
f1 = []
for a2, canon in _alias2canon.items():
    for (ce, n), v in SHENSHA_SCORES.items():
        if ce != canon or (a2, n) in SHENSHA_SCORES or n not in _wild:
            continue
        f1.append((a2, canon, n, v, _wild[n]))
check('F1 样本非空转（实测 %d 对）' % len(f1), len(f1) >= 1)
f1_bad = [r for r in f1 if shensha_score(r[0], r[2]) != r[3]]
check('F1 原事项级无键时逐对命中 canonical 值（%d 对，差异 %d）'
      % (len(f1), len(f1_bad)), not f1_bad)
f1_disc = [r for r in f1 if r[3] != r[4]]
check("F1 含「值可区分」样本≥1（canonical≠通配，实测 %d 对）" % len(f1_disc),
      len(f1_disc) >= 1)
check("F1 强断言：移徙×日破时 原事项级无键、canonical(入宅)=-20、通配=-10"
      " → shensha_score('移徙','日破时')=-20（非通配 -10）",
      ('移徙', '日破时') not in SHENSHA_SCORES
      and SHENSHA_SCORES.get(('入宅', '日破时')) == -20
      and _wild.get('日破时') == -10
      and shensha_score('移徙', '日破时') == -20)

# F2 原事项级无键 + canonical无键 + 通配有键 → 命中通配（回退可用）
f2 = [(a2, n, _wild[n]) for a2, canon in _alias2canon.items() for n in _wild
      if (a2, n) not in SHENSHA_SCORES and (canon, n) not in SHENSHA_SCORES]
check('F2 样本非空转（实测 %d 对）' % len(f2), len(f2) >= 1)
f2_bad = [r for r in f2 if shensha_score(r[0], r[1]) != r[2]]
check('F2 前两级皆无键时逐对命中通配值（%d 对，差异 %d）'
      % (len(f2), len(f2_bad)), not f2_bad)
check("F2 已删项仅经通配保持既有值不复活：shensha_score('移徙','月刑')=-15"
      "（(',移徙',月刑)/('入宅',月刑) 均无键）",
      ('移徙', '月刑') not in SHENSHA_SCORES
      and ('入宅', '月刑') not in SHENSHA_SCORES
      and shensha_score('移徙', '月刑') == -15)

# F3 原事项级有键 + 通配有键（值冲突时）→ 必须命中原事项级。
# 现实表内该层无「值可区分」样本（移徙∩通配 6 名值与通配相等），故用运行期
# 临时注入制造可区分样本：断言后立即还原（不改源码、不落库、不改键表终态）。
_inj = [('移徙', '__边界用例煞__'), ('*', '__边界用例煞__')]
_old = [SHENSHA_SCORES.get(k, '__ABSENT__') for k in _inj]
try:
    SHENSHA_SCORES[_inj[0]] = -7   # 原事项级
    SHENSHA_SCORES[_inj[1]] = -3   # 通配级（值可区分）
    check('F3 运行期注入：原事项级有键时命中 -7（非通配 -3）',
          shensha_score('移徙', '__边界用例煞__') == -7)
finally:
    for _k, _ov in zip(_inj, _old):
        if _ov == '__ABSENT__':
            SHENSHA_SCORES.pop(_k, None)
        else:
            SHENSHA_SCORES[_k] = _ov
check('F3 注入已还原（键表与注入前一致）',
      ('移徙', '__边界用例煞__') not in SHENSHA_SCORES
      and ('*', '__边界用例煞__') not in SHENSHA_SCORES)

print('---')
if FAILS:
    print('FAILS=%d' % len(FAILS))
    for f in FAILS:
        print(' -', f)
    raise SystemExit(1)
print('ALL PASS')
raise SystemExit(0)
