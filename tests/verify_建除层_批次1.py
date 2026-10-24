# -*- coding: utf-8 -*-
"""
建除层批次 1 验证（2026-10-22，001 §161）

覆盖：单一事实源黄金表、六路等价、2026 全年、开业伪谓词、破日月破双计、
小黄道倒挂、哨兵 224、非法输入反向断言。
退出码：0=全部通过；1=有 FAIL。
"""
import io
import os
import sys
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FAILS = []
NCHK = [0]


def check(name, cond, detail=''):
    NCHK[0] += 1
    print('[%s] %s %s' % ('PASS' if cond else 'FAIL', name, detail))
    if not cond:
        FAILS.append(name)


ZH = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
STARS = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
XIONG = set('建满平收破闭')
JI = set('除危定执成开')

# 黄金表：按《协纪辨方书》卷四「正月建寅，顺行十二辰」独立硬编码，行=月支，列=日支（子→亥）
GOLDEN = {
    '子': ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭'],
    '丑': ['闭', '建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开'],
    '寅': ['开', '闭', '建', '除', '满', '平', '定', '执', '破', '危', '成', '收'],
    '卯': ['收', '开', '闭', '建', '除', '满', '平', '定', '执', '破', '危', '成'],
    '辰': ['成', '收', '开', '闭', '建', '除', '满', '平', '定', '执', '破', '危'],
    '巳': ['危', '成', '收', '开', '闭', '建', '除', '满', '平', '定', '执', '破'],
    '午': ['破', '危', '成', '收', '开', '闭', '建', '除', '满', '平', '定', '执'],
    '未': ['执', '破', '危', '成', '收', '开', '闭', '建', '除', '满', '平', '定'],
    '申': ['定', '执', '破', '危', '成', '收', '开', '闭', '建', '除', '满', '平'],
    '酉': ['平', '定', '执', '破', '危', '成', '收', '开', '闭', '建', '除', '满'],
    '戌': ['满', '平', '定', '执', '破', '危', '成', '收', '开', '闭', '建', '除'],
    '亥': ['除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭', '建'],
}

from modules.建除 import (star, star_by_sizhu, is_jianchu,   # noqa: E402
                          is_jianchu_date, JI_STARS, XIONG_STARS)
from modules.四柱计算器 import calculate_sizhu                 # noqa: E402
from modules.今日黄历 import calc_jianchu                      # noqa: E402
from modules.黄道 import 黄道计算器                             # noqa: E402
from modules.shensha.marriage_shensha import get_jianchu       # noqa: E402
from modules.shensha.通用神煞 import CommonShenShaChecker as _CSC  # noqa: E402
from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt as _XZEXT  # noqa: E402
from modules.shensha.开业神煞 import OpeningShenShaChecker as _OSC  # noqa: E402
from modules.评分器 import calculate_score                    # noqa: E402
from modules.事项标准 import shensha_score, SHENSHA_SCORES     # noqa: E402


# ============ 1. 黄金表 144 格 ============
bad = [{'month': m, 'day': d, 'exp': GOLDEN[m][ZH.index(d)], 'got': star(m, d)}
       for m in ZH for d in ZH if star(m, d) != GOLDEN[m][ZH.index(d)]]
check('1 黄金表 144 格', not bad, 'diff=%d' % len(bad))
check('1b 吉凶集合与黄金表一致',
      JI_STARS == frozenset(JI) and XIONG_STARS == frozenset(XIONG))

# ============ 2. 六路等价（144 格；rules fallback 源级断言） ============
h = 黄道计算器()
inst_common = object.__new__(_CSC)
_xz = _XZEXT()
_cap = [None]
_xz._add_shensha = lambda name, score, desc='': _cap.__setitem__(0, name)

path_bad = []
for m in ZH:
    for d in ZH:
        exp = GOLDEN[m][ZH.index(d)]
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
                path_bad.append({'m': m, 'd': d, 'path': k, 'exp': exp, 'got': v})
check('2 144 格 × 4 路等价', not path_bad, 'diff=%d' % len(path_bad))

_rules_ok = True
for fn in ('修造规则.py', '作灶规则.py', '安葬规则.py'):
    p = os.path.join(ROOT, 'modules', 'rules', fn)
    with io.open(p, encoding='utf-8') as f:
        src = f.read()
    if 'offset = (day_idx - month_idx) % 12' in src or '_jianchu_star' not in src:
        _rules_ok = False
check('2b rules 三处 fallback 已委托（无独立偏移表）', _rules_ok)

# ============ 3. 2026 全年六路口径 ============
d0, d1 = datetime.date(2026, 1, 1), datetime.date(2026, 12, 31)
year_bad = []
day = d0
while day <= d1:
    sz = calculate_sizhu(day, 12, 0)
    exp = GOLDEN[sz['month_zhi']][ZH.index(sz['day_zhi'])]
    vals = {
        'star_by_sizhu': star_by_sizhu(sz),
        'calc_jianchu': calc_jianchu(sz['month_zhi'], sz['day_zhi']),
        'marriage': get_jianchu(day, sz['month_zhi']),
        'is_jianchu_date': exp if is_jianchu_date(day, exp) else 'X',
    }
    for k, v in vals.items():
        if v != exp:
            year_bad.append({'date': str(day), 'path': k, 'exp': exp, 'got': v})
    day += datetime.timedelta(days=1)
check('3 2026 全年 4 路一致', not year_bad, 'diff=%d' % len(year_bad))

# ============ 4. 开业伪谓词 144 格 + 反向 ============
inst_open = object.__new__(_OSC)
pred_bad = []
for m in ZH:
    for d in ZH:
        sz = {'month_zhi': m, 'day_zhi': d}
        exp = GOLDEN[m][ZH.index(d)]
        for name, fn in (('满', '_is_manri'), ('成', '_is_chengri'),
                         ('闭', '_is_biari'), ('破', '_is_pori')):
            got = getattr(inst_open, fn)(sz)
            if got != (exp == name):
                pred_bad.append({'m': m, 'd': d, 'fn': fn, 'exp': exp == name, 'got': got})
check('4 开业四谓词 144 格全等', not pred_bad, 'diff=%d' % len(pred_bad))
rev_ok = True
for m in ZH:
    for d in ZH:
        if GOLDEN[m][ZH.index(d)] == '除':
            sz = {'month_zhi': m, 'day_zhi': d}
            if any(getattr(inst_open, f)(sz) for f in
                   ('_is_manri', '_is_chengri', '_is_biari', '_is_pori')):
                rev_ok = False
check('4b 反向：除日四谓词均 False', rev_ok)

# ============ 5. 全年计分：双计 + 倒挂 ============
check('5a 破日键已删除', ('开业', '破日') not in SHENSHA_SCORES)
double_days = []
pori_score_bad = []
inversion_days = []
ji_missing = []
day = d0
while day <= d1:
    sz = calculate_sizhu(day, 12, 0)
    sz.update({'year': day.year, 'month': day.month, 'day': day.day, 'date': day})
    actual = GOLDEN[sz['month_zhi']][ZH.index(sz['day_zhi'])]
    r = calculate_score(sz, '开业')
    lst = r.get('shensha_list', []) or []
    names = [s.get('name') for s in lst]
    if '月破' in names and '破日' in names:
        double_days.append(str(day))
    if actual == '破':
        ssum = sum((s.get('score', 0) or 0) for s in lst if s.get('name') in ('月破', '破日'))
        if ssum != -30:
            pori_score_bad.append({'date': str(day), 'sum': ssum})
    for ev in ('入学', '求医', '签约', '通用'):
        rr = calculate_score(sz, ev)
        ll = rr.get('shensha_list', []) or []
        sc = 0
        found = False
        for s in ll:
            nm = s.get('name', '')
            if nm == '小黄道-' + actual:
                sc = s.get('score', 0) or 0
                found = True
        if not found:
            ji_missing.append({'date': str(day), 'event': ev, 'star': actual})
        elif actual in XIONG and sc != 0:
            inversion_days.append({'date': str(day), 'event': ev, 'star': actual, 'score': sc})
        elif actual in JI and sc != 8:
            ji_missing.append({'date': str(day), 'event': ev, 'star': actual, 'score': sc})
    day += datetime.timedelta(days=1)
check('5b 开业月破+破日零共现', not double_days, 'days=%d' % len(double_days))
check('5c 破日扣分恒 -30（无双计）', not pori_score_bad, 'bad=%d' % len(pori_score_bad))
check('5d 4 通道凶星零加分（倒挂清零）', not inversion_days, 'days=%d' % len(inversion_days))
check('5e 4 通道吉星恒 +8', not ji_missing, 'days=%d' % len(ji_missing))

for ev in ('入学', '求医', '签约'):
    check('5f %s 解析值：吉8/凶0' % ev,
          all(shensha_score(ev, '小黄道-' + s) == (8 if s in JI else 0) for s in STARS))

# ============ 6. 哨兵 ============
sz = calculate_sizhu(datetime.date(2026, 11, 4), 12, 0)
sz.update({'year': 2026, 'month': 11, 'day': 4, 'date': datetime.date(2026, 11, 4)})
sent = calculate_score(sz, '入宅')
check('6 哨兵 2026-11-04 入宅 226/上吉（批次2移除无据建除宜项，224→214；§172 P0大清理岁刑-12置0，214→226）',
      sent.get('score') == 226 and '上吉' in (sent.get('level') or ''),
      '%s %s' % (sent.get('score'), sent.get('level')))

# ============ 7. 反向输入 ============
def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    except Exception:
        return False
    return False

check('7a star 空月支 raise', _raises(star, '', '子'))
check('7b star 空日支 raise', _raises(star, '寅', ''))
check('7c star 非地支 raise', _raises(star, '甲', '子'))
check('7d 今日黄历非法输入→未知', calc_jianchu('', '') == '未知')
check('7e 黄道非法月支→未知', h._calculate_xiao_huang_dao('', '子')['name'] == '未知')
check('7f is_jianchu 反向', is_jianchu({'month_zhi': '寅', 'day_zhi': '子'}, '建') is False)
check('7g is_jianchu 正向', is_jianchu({'month_zhi': '寅', 'day_zhi': '子'}, '开') is True)

if FAILS:
    print('\nFAIL %d' % len(FAILS))
    sys.exit(1)
print('\nPASS %d' % NCHK[0])
sys.exit(0)
