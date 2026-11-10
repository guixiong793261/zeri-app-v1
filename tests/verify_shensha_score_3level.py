# -*- coding: utf-8 -*-
"""
shensha_score 三级查找改造回归（2026-10-19，移徙休眠键修复·选A）
==================================================================
拍板依据：「移徙修复方向选A」条件②③④——
②三级查找顺序与回退明确：原事项→canonical→通配，逐级命中即返回；
  通配级不得覆盖前两级已命中项；
③多链同拦回归：移徙专属键可命中、且不与入宅通道重复发射；
  75 共有键同值须断言「评分零变化」（78-1-1-1，十恶大败键随 2026-10-19 全删批移除，
  ('移徙','岁破')随岁破批 2026-10-20 移除——001 §140，
  ('移徙','病符')随病符批 2026-10-20 移除——001 §141）；
④x4/P2 删除项（10 煞）在移徙通道保持删除，不得因「通配」复活。
前置：cb3f8cb 已删 10 键（条件①）；bb196e7 §四证全表非 canonical 键
仅「入宅←移徙」一族，改造全局影响面上限即移徙 88 键。

验证面：
A. 三级顺序与回退：75 键 shensha_score('移徙',n)==('移徙',n) 值（原事项
   级命中）；与 ('*',n) 交集名逐项断言不被通配覆盖；别名（搬家/迁居）
   落入 canonical 级与入宅同值。
B. 全事项对照零变化：本地复刻旧两级逻辑，对 键表全部事项名 ∪
   EVENT_ALIASES 全别名 × 键表全部煞名 逐对断言 新==旧。
C. 共有键评分零变化：shensha_score('移徙',n)==('入宅',n) 值。
D. 10 煞分值（口径收口批 2026-10-21，001 §153 修订；轻重层批次1 001 §158
   通配随批调整）：
   shensha_score('移徙',n)＝7×None＋天吏-15（恢复）＋月刑-20＋月害-12
   （快照 bb196e7 §二基线）；移徙通道 7 煞零发射、天吏恢复发射。
E. 发射链零变化：入宅/移徙通道 2026 全年逐日发射清单逐项一致、
   总分=11601（轻重层批次1 001 §158 受死日+217/月德合+117/归忌+155/月厌-300
   后实测重冻为 3377；批次2 001 §159 鸣吠统一高档 +368 重冻为 3745；
   福星批 001 §165 删伪福星 -310 → 3435；干支类实现Bug清理批 001 §171
   蚕官/畜官去重 +310 → 3745；P0 大清理 001 §172 岁害/天耗/地耗删 982＋
   年家族 12 项置 0 收 4439＋年支孤辰删 900＋大耗620＋小耗450 → +7391 → 11136；
   §195 Commit1 入宅/移徙 受死日剥离扣分（§190 HARD_VETO 纯展示 0 分，31 天次×+15）
   → +465 → 11601）。
   嫁娶总分=6490（轻重层批次1 001 §158 后重冻 214；福星批 -310 → -96；
   §171 蚕官/畜官去重 +310 → 214；§172 孤辰年支法删（105→61 月令保留）＋
   岁害/天耗/地耗删＋年家族置 0 → +6081 → 6295；§193 重丧双口径对齐 -270 →
   6025；§194 受死日剥离扣分（HARD_VETO 纯展示 0 分）+465 → 6490）。

退出码 0=全过 1=有失败。
"""
import io
import os
import sys
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []


_STAT = {'checks': 0, 'pass': 0}


def check(name, cond):
    """断言计数就地自汇报（001 §135.4：计数以脚本自报为准，不依赖 Shell 回显）。"""
    _STAT['checks'] += 1
    if cond:
        _STAT['pass'] += 1
    print('[%s] %s' % ('PASS' if cond else 'FAIL', name))
    if not cond:
        FAILS.append(name)


sys.path.insert(0, ROOT)
from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.事项标准 import (SHENSHA_SCORES, shensha_score, canonical_event,
                             EVENT_ALIASES)

D10 = ['月破', '劫煞', '灾煞', '往亡', '月煞', '月刑', '天吏', '大时', '五墓', '月害']
# 口径收口批（001 §153）：天吏×移徙恢复 -15（般移【移徙同】双明文，x4 误排反转）
EXPECT10 = {'月破': None, '劫煞': None, '灾煞': None, '往亡': None, '月煞': None,
            '月刑': -20, '天吏': -15, '大时': None, '五墓': None, '月害': -12}
# 发射零复活名单（天吏移出：恢复发射）
NOTREVIVED = ['月破', '劫煞', '灾煞', '往亡', '月煞', '大时', '五墓']


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
check('移徙键数=67（P0 大清理 001 §172：删 岁害/天耗/地耗×移徙 3 键＋'
      '孤辰寡宿×移徙 1 键 → 71-4=67；福星正统落地批 2026-10-23，001 §169：'
      '+1 恢复 福星×移徙；历史：口径收口批 2026-10-21，001 §153 删 '
      '反支日/天恩/不将日 3 键；天吏批 +1 恢复；飞廉批 -1 删 飞廉×移徙；'
      '红嘴朱雀批 75→74；福星批 001 §165 删 福星×移徙 → 70；§169 正统加回 → 71）',
      len(yi) == 67)
for n, v in yi.items():
    if shensha_score('移徙', n) != v:
        check("原事项级命中：shensha_score('移徙',%r)==%r" % (n, v), False)
        break
else:
    check('原事项级命中：74键 shensha_score(移徙,n)==(移徙,n) 值', True)
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

# ============ C：共有键评分零变化 ============
ok77 = all(shensha_score('移徙', n) == SHENSHA_SCORES.get(('入宅', n)) for n in yi)
check('共有键 shensha_score(移徙,n)==(入宅,n) 值（评分零变化，n=%d）' % len(yi),
      ok77)

# ============ D：10 煞分值锁定 ============
for n in D10:
    check("shensha_score('移徙',%r)=%r（口径收口批后分值）" % (n, EXPECT10[n]),
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
for n in NOTREVIVED:
    check('移徙通道 %s 全年零发射·不复活 (x%d)' % (n, yi10[n]), yi10[n] == 0)
check('移徙通道 天吏 恢复发射 (x%d，口径收口批 001 §153 反转)' % yi10['天吏'],
      yi10['天吏'] > 0)
check('移徙通道 月刑/月害 发射已被 x4 通道排除 (x%d/x%d)'
      % (yi10['月刑'], yi10['月害']), yi10['月刑'] == 0 and yi10['月害'] == 0)

# ============ E：发射链零变化 ============
check('移徙通道==入宅通道 2026 全年逐日发射清单逐项一致',
      all(ru_days[k] == yi_days[k] for k in ru_days))
tot_ru = sum(s for hits in ru_days.values() for _, s in hits)
check('入宅通道全年总分=13941（批次1 001 §158 受死日+217/月德合+117/'
      '归忌+155/月厌-300 → 3377；批次2 001 §159 鸣吠统一高档 +368 → 3745；'
      '福星批 001 §165 删伪福星 -310 → 3435；干支类实现Bug清理批 001 §171 '
      '蚕官/畜官去重 +310（31 天次×10，谓词同值双扣消除）→ 3745；'
      'P0 大清理 001 §172 +7391 → 11136；§195 Commit1 受死日剥离扣分 '
      '31 天次×+15 → 11601；§250 天乙贵人 156 天次×+15 → 13941）',
      tot_ru == 13941)
tot_yi = sum(s for hits in yi_days.values() for _, s in hits)
check('移徙通道全年总分=13941（=入宅，红嘴/受死日同链；批次2 +368；福星批 -310；'
      '§171 蚕官/畜官去重 +310；§172 P0 大清理 +7391 → 11136；'
      '§195 Commit1 受死日剥离扣分 31 天次×+15 → 11601；§250 天乙贵人 → 13941）',
      tot_yi == 13941)
dup = sum(1 for hits in yi_days.values()
          if len([n for n, _ in hits]) != len({n for n, _ in hits}))
check('移徙通道逐日同名至多1条·不与入宅重复发射（重复日=%d）' % dup, dup == 0)
jq_days, _ = _run('嫁娶', y0, y1)
tot_jq = sum(s for hits in jq_days.values() for _, s in hits)
check('嫁娶通道全年总分=12410（轻重层批次1 001 §158 后实测重冻 214；'
      '福星批 001 §165 删伪福星 -310 → -96；干支类实现Bug清理批 001 §171 '
      '蚕官/畜官去重 +310（31 天次×10）→ 214；P0 大清理 001 §172 '
      '孤辰年支法删＋岁害/天耗/地耗删＋年家族置 0 → +6081 → 6295；'
      '§193 主轨 C2 重丧双口径对齐 5→32 天（-10/日）→ -270 → 6025；'
      '§194 受死日剥离扣分（HARD_VETO 纯展示 0 分，31 天次×+15）→ 6490；'
      '§196 D1 重丧日撤否决撤扣分（三库明言吉事不忌，32 天次×+10）→ 6810；'
      '§212 嫁娶去伪存真批（12 项删除/4 项降 0 分/白虎朱雀下沉时辰级）'
      ' 6810→10070（+3260）；§250 天乙贵人 156 天次×+15 → 12410）',
      tot_jq == 12410)

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
check("F2 已删项仅经通配保持既有值不复活：shensha_score('移徙','月刑')=-20"
      "（(',移徙',月刑)/('入宅',月刑) 均无键；轻重层批次1 001 §158 通配 -15→-20）",
      ('移徙', '月刑') not in SHENSHA_SCORES
      and ('入宅', '月刑') not in SHENSHA_SCORES
      and shensha_score('移徙', '月刑') == -20)

# F3 原事项级有键 + 通配有键（值冲突）→ 必须命中原事项级。
# 【注入型用例·不得与并行测试同跑】（防护③ 隔离标记）——现实表内该层无
# 「值可区分」样本（移徙∩通配 6 名值与通配相等），故以运行期临时注入制造
# 可区分样本（不改源码、不落库、不改键表终态）。
# 拍板三项防护：①注入范围最小化（仅注入被测单键，注入前后各做一次全表
# 快照断言）；②还原失败硬失败（还原后断言回原状，失败 raise 非 pass）；
# ③测试隔离标记（本块注释与断言名显式标「注入型」）。
_INJECT_NAME = '__边界用例煞__'
_inj_keys = [('移徙', _INJECT_NAME), ('*', _INJECT_NAME)]
_snap_before = dict(SHENSHA_SCORES)                 # 防护① 全表快照（注入前）
_old = {k: SHENSHA_SCORES.get(k, '__ABSENT__') for k in _inj_keys}
try:
    SHENSHA_SCORES[_inj_keys[0]] = -7               # 原事项级
    SHENSHA_SCORES[_inj_keys[1]] = -3               # 通配级（值可区分）
    _snap_mid = dict(SHENSHA_SCORES)                # 防护① 全表快照（注入后）
    _delta = {k for k in set(_snap_mid) | set(_snap_before)
              if _snap_mid.get(k, '__ABSENT__') != _snap_before.get(k, '__ABSENT__')}
    check('F3【注入型】防护①范围最小化：全表仅被测 2 键变动（实测变动 %d 键）'
          % len(_delta), _delta == set(_inj_keys))
    check('F3【注入型】原事项级有键时命中 -7（非通配 -3）',
          shensha_score('移徙', _INJECT_NAME) == -7)
finally:
    for _k, _ov in _old.items():                    # 还原
        if _ov == '__ABSENT__':
            SHENSHA_SCORES.pop(_k, None)
        else:
            SHENSHA_SCORES[_k] = _ov
    _restored = dict(SHENSHA_SCORES) == _snap_before

# 防护② 经 check() 汇报（确保「自报计数 == 逐行点数」，口径一致）
check('F3【注入型】防护②还原硬校验：键表与注入前全表一致', _restored)
if not _restored:                                   # 防护② 失败即 raise 非 pass
    raise RuntimeError(
        'F3【注入型】还原失败：键表已被污染，硬失败退出'
        '（防污染后续测试/并行运行）')

print('---')
print('CHECKS=%d PASS=%d FAIL=%d' % (_STAT['checks'], _STAT['pass'], len(FAILS)))
if FAILS:
    print('FAILS=%d' % len(FAILS))
    for f in FAILS:
        print(' -', f)
    raise SystemExit(1)
print('ALL PASS')
raise SystemExit(0)
