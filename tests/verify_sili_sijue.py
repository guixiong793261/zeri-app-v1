# -*- coding: utf-8 -*-
"""
四离四绝穷举验证（B 类锚点④：桩函数复活 + 文案链可达）
=========================================================
权威规则（《协纪辨方书》）：
    四离日 = 春分/夏至/秋分/冬至（二分二至）前一日
    四绝日 = 立春/立夏/立秋/立冬（四立）前一日
    按自然日判定（sxtwl 节气日期 -1 天），含跨年（冬至/立冬后 → 次年立春前）。

失效模式（2026-09-20 修复背景）：
    本神煞是第四种模式——"桩函数死链路"：shensha 计分层独立实现正确
    （-35 照扣），但 marriage_shensha.is_sili_sijue 为 return False 桩，
    导致 11 个 rules 检查器的"四离四绝日忌X"文案链全年不命中，
    用户只见分数降低不见原因。婚嫁评分算法内同名桩 + -30 分值漂移
    （与事项标准 -35 不符），同轮修复。

2026 丙午年权威黄金清单（硬编码，sxtwl 实测复核，绝不从软件读取）：
    四离 4 天：03-19（春分前）、06-20（夏至前）、09-22（秋分前）、12-21（冬至前）
    四绝 4 天：02-03（立春前）、05-04（立夏前）、08-06（立秋前）、11-06（立冬前）
    跨年边界：2027-02-03（2027 立春 02-04 前一日）必须命中。

正当缺位说明（非缺陷，已断言验证）：
    2026-02-03 普通安葬曾无四离四绝文案（旧死模块 安葬规则.py 重丧日
    一票否决 early-return 在四离四绝检查之前）。
    §186（2026-10-27 安葬深水区批）：安葬规则.py 废弃为薄别名继承
    高级安葬规则；活跃口径中大凶日否决 return 位于四离四绝等全部
    凶项检查之后——否决日忌项完整披露（含四离四绝）再否决，更为
    合理。02-03（丑月戊日）四离四绝文案在位，正当。
    §197（2026-10-28 复日起例改正）：丑月取「己」，02-03 戊日不再
    属复日，该日仅四离四绝忌事（非否决）；复日否决锚点改 01-15。

入口：
  ① modules/shensha/marriage_shensha.py::is_sili_sijue —— 11 个 rules 检查器共用
  ② modules/shensha/神煞基类.py ShenShaChecker._is_sili / _is_sijue
     —— shensha 计分层（作灶/出行/安床/安葬/开业/修造/动土/入宅/通用继承）
  ③ rules 层 11 检查器 _check_rules 忌项文案链端到端
  ④ modules/婚嫁评分算法.py score_marriage_day —— details 含四离四绝 -35
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli

import sxtwl
import datetime

# ===== 权威黄金清单（硬编码，绝不从软件读取） =====
AUTH_SILI_2026 = ['2026-03-19', '2026-06-20', '2026-09-22', '2026-12-21']
AUTH_SIJUE_2026 = ['2026-02-03', '2026-05-04', '2026-08-06', '2026-11-06']
AUTH_ALL_2026 = set(AUTH_SILI_2026) | set(AUTH_SIJUE_2026)
AUTH_2027_LICHUN_EVE = '2027-02-03'

# 普通安葬正当缺位日——§186 起为空集：安葬规则.py 废弃为薄别名继承
# 高级安葬规则后，大凶日否决 return 在四离四绝检查之后，否决日文案
# 完整披露（含四离四绝），不再缺位。
NORMAL_BURIAL_VETO_OK = set()


def _sxtwl_sili_sijue(year):
    """用 sxtwl 节气独立推导 year 年的四离四绝（权威双保险）。

    sxtwl 索引：立春0 春分3 立夏6 夏至9 立秋12 秋分15 立冬18 冬至21
    """
    jq = sxtwl.getJieQiByYear(year)
    out = set()
    for idx in (3, 9, 15, 21):      # 二分二至 → 四离
        dd = sxtwl.JD2DD(jq[idx].jd)
        d = datetime.date(int(dd.Y), int(dd.M), int(dd.D)) - datetime.timedelta(days=1)
        out.add(d.isoformat())
    for idx in (0, 6, 12, 18):      # 四立 → 四绝
        dd = sxtwl.JD2DD(jq[idx].jd)
        d = datetime.date(int(dd.Y), int(dd.M), int(dd.D)) - datetime.timedelta(days=1)
        out.add(d.isoformat())
    return out


# 双保险自检：sxtwl 独立推导必须与硬编码黄金清单一致
_calc_2026 = _sxtwl_sili_sijue(2026)
assert _calc_2026 == AUTH_ALL_2026, \
    f'黄金清单自检失败: sxtwl推导={sorted(_calc_2026)} 硬编码={sorted(AUTH_ALL_2026)}'
_calc_2027_lichun = _sxtwl_sili_sijue(2027)
assert AUTH_2027_LICHUN_EVE in _calc_2027_lichun, \
    f'2027 跨年四绝自检失败: 推导={sorted(_calc_2027_lichun)}'


def _daterange(y1, m1, d1, y2, m2, d2):
    cur = datetime.date(y1, m1, d1)
    end = datetime.date(y2, m2, d2)
    while cur <= end:
        yield cur
        cur += datetime.timedelta(days=1)


INPUTS_2026 = list(_daterange(2026, 1, 1, 2026, 12, 31))          # 365 天穷举
INPUTS_2027_HEAD = list(_daterange(2027, 1, 1, 2027, 2, 10))      # 跨年边界段

# ===== 入口①：marriage_shensha.is_sili_sijue（单桩） =====
from modules.shensha.marriage_shensha import is_sili_sijue as _impl


def _ad_impl(d):
    return bool(_impl(d))


# ===== 入口②：神煞基类计分层 =====
from modules.shensha.神煞基类 import ShenShaChecker

_BASE = ShenShaChecker()


def _ad_base_sili(d):
    return bool(_BASE._is_sili({'date': d}))


def _ad_base_sijue(d):
    return bool(_BASE._is_sijue({'date': d}))


# ===== 入口③：rules 层文案链端到端 =====
from modules.四柱计算器 import calculate_sizhu

_RULES_CLS = [
    ('modules.rules.修造规则.ConstructionRuleChecker', '修造', '四离四绝日忌修造', set()),
    ('modules.rules.动土规则.DongTuRuleChecker', '动土', '四离四绝日忌动土', set()),
    ('modules.rules.拆舍规则.ChaiSheRuleChecker', '拆舍', '四离四绝日忌拆舍', set()),
    ('modules.rules.入宅规则.RuZhaiRuleChecker', '入宅', '四离四绝日忌入宅', set()),
    ('modules.rules.安葬规则.BurialRuleChecker', '安葬', '四离四绝日忌安葬', NORMAL_BURIAL_VETO_OK),
    ('modules.rules.高级安葬规则.AdvancedBurialRuleChecker', '高级安葬', '四离四绝日忌安葬', set()),
    ('modules.rules.安床规则.BedRuleChecker', '安床', '四离四绝日忌安床', set()),
    ('modules.rules.作灶规则.StoveRuleChecker', '作灶', '四离四绝日忌作灶', set()),
    ('modules.rules.开业规则.OpeningRuleChecker', '开业', '四离四绝日忌开业', set()),
    ('modules.rules.嫁娶规则.MarriageRuleChecker', '嫁娶', '四离四绝日', set()),
    ('modules.rules.通用规则.GenericRuleChecker', '通用', '四离四绝日', set()),
]
_RULE_CHECKERS = []
for _path, _tag, _text, _ok in _RULES_CLS:
    _mod_p, _cls_p = _path.rsplit('.', 1)
    _mod = __import__(_mod_p, fromlist=[_cls_p])
    _c = getattr(_mod, _cls_p)()
    if _tag == '通用':
        _c.event_type = '订婚'   # 通用规则 event_type 取实例属性
    _RULE_CHECKERS.append((_tag, _c, _text, _ok))


def _rules_ad(tag):
    _c = next(c for t, c, _, _ in _RULE_CHECKERS if t == tag)

    def _ad(d):
        sz = dict(calculate_sizhu(d, 12, 0))
        sz['date'] = d
        res = _c._check_rules(sz, date_obj=d)
        ji = res[1]
        return any('四离' in str(x) or '四绝' in str(x) for x in ji)
    return _ad


def _rules_expected(tag):
    ok = next(o for t, _, _, o in _RULE_CHECKERS if t == tag)

    def _exp(d):
        return d.isoformat() in (AUTH_ALL_2026 - ok)
    return _exp


# ===== 入口④：婚嫁评分算法 details/warning =====
from modules.婚嫁评分算法 import score_marriage_day


def _ad_marriage(d):
    r = score_marriage_day(d)
    has = any('四离四绝' in str(x[0]) for x in r.get('details', []))
    warn = any('四离四绝' in str(w) for w in r.get('warnings', []))
    return bool(has and warn)


# ===== 显式边界断言 =====
def _d(y, m, dd):
    return datetime.date(y, m, dd)


_boundary_notes = []

# 边界1：2026-02-03 立春前一日 → 命中四绝；02-04 立春当日 → 不命中
assert _impl(_d(2026, 2, 3)) is True, '2026-02-03 应命中四绝'
assert _impl(_d(2026, 2, 4)) is False, '2026-02-04 立春当日不应命中'
_boundary_notes.append('02-03(立春前一日)命中四绝 / 02-04(立春日)不命中')

# 边界2：跨年 2027-02-03（2027 立春前一日）必须命中
assert _impl(_d(2027, 2, 3)) is True, '2027-02-03 跨年四绝应命中'
_boundary_notes.append('2027-02-03 跨年命中（立冬/冬至后取次年立春）')

# 边界3：黄金清单 8 天总数与构成
assert len(AUTH_ALL_2026) == 8 and len(AUTH_SILI_2026) == 4 and len(AUTH_SIJUE_2026) == 4
_boundary_notes.append('2026 黄金清单 8 天 = 四离4(二分二至前) + 四绝4(四立前)')

# 边界4：安葬四离四绝文案 + 复日否决（§197 D3 起例改正后重冻）
# §197（2026-10-28）复日起例改协纪正法单干·节气月建后，丑月取「己」不再是
# 戊日，2026-02-03（丑月戊日）**不再是复日**，仅剩四离四绝忌事（非否决）；
# 复日否决锚点改取 2026-01-15（丑月己日，复日成立）。
_b = next(c for t, c, _, _ in _RULE_CHECKERS if t == '安葬')
_sz = dict(calculate_sizhu(_d(2026, 2, 3), 12, 0))
_sz['date'] = _d(2026, 2, 3)
_res4 = _b._check_rules(_sz, date_obj=_d(2026, 2, 3))
_ji = _res4[1]
assert not any('复日' in str(x) or '重丧日' in str(x) for x in _ji), \
    '2026-02-03（丑月戊日）按协纪单干表已非复日，不应复日否决'
assert any('四离四绝' in str(x) for x in _ji), \
    '2026-02-03 安葬四离四绝文案应在位（§186 完整披露口径）'
assert len(_res4) == 2, '2026-02-03 非否决日应返回 2-tuple'
_boundary_notes.append('02-03(丑月戊日) 按单干表已非复日 → 非否决，四离四绝忌事在位（§197 重冻）')

_sz2 = dict(calculate_sizhu(_d(2026, 1, 15), 12, 0))
_sz2['date'] = _d(2026, 1, 15)
_res4b = _b._check_rules(_sz2, date_obj=_d(2026, 1, 15))
assert any('复日' in str(x) for x in _res4b[1]), '2026-01-15（丑月己日）安葬应发复日忌项'
assert len(_res4b) == 4 and _res4b[2] is True, '2026-01-15 复日应返回 4-tuple 否决位'
_boundary_notes.append('01-15（丑月己日）＝复日一票否决，否决日忌项完整披露（§197 新锚点）')

# 边界5：单桩正反抽检（修复前桩恒 False 的直接反证）
assert _impl(_d(2026, 3, 19)) is True, '春分前一日应命中四离'
assert _impl(_d(2026, 3, 18)) is False, '03-18 非四离四绝日不应命中'
_boundary_notes.append('03-19 命中 / 03-18 反例不命中（桩函数修复直接反证）')


# ===== 验证用例 =====
def _exp_impl(d):
    return d.isoformat() in AUTH_ALL_2026


def _exp_sili(d):
    return d.isoformat() in set(AUTH_SILI_2026)


def _exp_sijue(d):
    return d.isoformat() in set(AUTH_SIJUE_2026)


def _exp_2027(d):
    return d.isoformat() == AUTH_2027_LICHUN_EVE


cases = [
    ShenShaCase(name='四离四绝(marriage_shensha单桩·11rules共用)', category='B',
                description='2026 穷举 365 天：8 天命中、357 天不命中；修复前桩恒 False 全年漏',
                inputs=INPUTS_2026, expected=_exp_impl, adapter=_ad_impl, compare='bool'),
    ShenShaCase(name='四离(神煞基类·计分层)', category='B',
                description='二分二至前一日 4 天命中；计分层与文案层同源复核',
                inputs=INPUTS_2026, expected=_exp_sili, adapter=_ad_base_sili, compare='bool'),
    ShenShaCase(name='四绝(神煞基类·计分层)', category='B',
                description='四立前一日 4 天命中；计分层与文案层同源复核',
                inputs=INPUTS_2026, expected=_exp_sijue, adapter=_ad_base_sijue, compare='bool'),
    ShenShaCase(name='四离四绝(跨年2027边界段)', category='B',
                description='2027-01-01~02-10：仅 2027-02-03（立春前一日）命中',
                inputs=INPUTS_2027_HEAD, expected=_exp_2027, adapter=_ad_impl, compare='bool'),
]

for _tag, _, _text, _ in _RULE_CHECKERS:
    cases.append(ShenShaCase(
        name=f'文案链({_tag}rules忌项端到端)', category='B',
        description=f'_check_rules 忌项应含"{_text}"；8 天全可达'
                    + ('（安葬 8 天文案全可达；02-03 按 §197 单干表已非复日，非否决日）' if _tag == '安葬' else ''),
        inputs=INPUTS_2026, expected=_rules_expected(_tag), adapter=_rules_ad(_tag),
        compare='bool'))

cases.append(ShenShaCase(
    name='文案链(婚嫁score_marriage_day端到端)', category='B',
    description='details 含(四离四绝,-35)且 warning 出现；-30→-35 对齐后口径',
    inputs=INPUTS_2026, expected=_exp_impl, adapter=_ad_marriage, compare='bool'))

if __name__ == '__main__':
    print('边界断言说明：')
    for _n in _boundary_notes:
        print('  -', _n)
    sys.exit(run_cli(cases))
