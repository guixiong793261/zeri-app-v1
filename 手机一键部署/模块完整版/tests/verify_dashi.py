# -*- coding: utf-8 -*-
"""
大时穷举验证
============
典据《协纪辨方书》卷六·义例四「大时（大败、咸池）」条：
  《历例》曰：「大时者，正月起卯，逆行四仲。」
  曹震圭曰：「大时者，乃月建三合五行沐浴之辰也，盖五行至此则败绝，
  是最凶之辰也。」
即寅午戌月卯、申子辰月酉、巳酉丑月午、亥卯未月子（月建三合局沐浴位），
月神查**日支**。

双保险：
1. 权威真值表硬编码（月建→日支），绝不从软件读取；
2. 月支/日支由 sxtwl 独立精确节气推导（与 verify_fusheng 同构），
   产品侧只调 _is_dashi 谓词。
另含：3 年 1095 天穷举、端到端 checker 单条目+分值锁（-12）、
旧四季错表误报日必须不命中、典载正格漏判日必须命中、
12 个黄金日干支硬锁。
旧实现按四季划月（春酉夏子秋卯冬午，恰为典载「守日」表）：2025-2026
共 730 天误命中 42、漏命中 39（12 月中仅季月巧合）。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，《协纪》卷六，查日支） =====
DASHI_CLASSICAL = {
    '寅': '卯', '午': '卯', '戌': '卯',      # 寅午戌火局沐浴在卯
    '申': '酉', '子': '酉', '辰': '酉',      # 申子辰水局沐浴在酉
    '巳': '午', '酉': '午', '丑': '午',      # 巳酉丑金局沐浴在午
    '亥': '子', '卯': '子', '未': '子',      # 亥卯未木局沐浴在子
}

# ===== 黄金日（2026 各月建首个大时日，含日柱干支，可对历书人工核对） =====
GOLDEN = [
    (datetime.date(2026, 1, 8),   '壬午'),   # 丑月 午日
    (datetime.date(2026, 2, 10),  '乙卯'),   # 寅月 卯日
    (datetime.date(2026, 3, 15),  '戊子'),   # 卯月 子日
    (datetime.date(2026, 4, 5),   '己酉'),   # 辰月 酉日
    (datetime.date(2026, 5, 8),   '壬午'),   # 巳月 午日
    (datetime.date(2026, 6, 10),  '乙卯'),   # 午月 卯日
    (datetime.date(2026, 7, 13),  '戊子'),   # 未月 子日
    (datetime.date(2026, 8, 15),  '辛酉'),   # 申月 酉日
    (datetime.date(2026, 9, 17),  '甲午'),   # 酉月 午日
    (datetime.date(2026, 10, 20), '丁卯'),   # 戌月 卯日
    (datetime.date(2026, 11, 10), '戊子'),   # 亥月 子日
    (datetime.date(2026, 12, 13), '辛酉'),   # 子月 酉日
]

# 旧四季错表误报日（旧命中、典载不命中）：日支取"春酉夏子秋卯冬午"值但
# 非本局沐浴位。
OLD_TABLE_FALSE_POS = [
    datetime.date(2025, 1, 1),    # 子月 庚午日：旧"冬在午"误命中，典载子月大时在酉
    datetime.date(2025, 2, 9),    # 寅月 己酉日：旧"春在酉"误命中，典载寅月大时在卯
    datetime.date(2025, 2, 21),   # 寅月 辛酉日：同上
]
# 旧四季错表漏报日（典载命中、旧不命中）
OLD_TABLE_FALSE_NEG = [
    datetime.date(2025, 1, 4),    # 子月 癸酉日：典载在酉，旧"冬在午"漏
    datetime.date(2025, 2, 15),   # 寅月 乙卯日：典载在卯，旧"春在酉"漏
]


def _month_zhi_at(d, hour=12):
    """独立精确节气月支（与 verify_yaoan/verify_fusheng 同构）。"""
    cur = datetime.datetime(d.year, d.month, d.day, hour, 0)
    pts = []
    for y in (d.year - 1, d.year):
        jq = sxtwl.getJieQiByYear(y)
        for idx, mz in ((20, '子'), (22, '丑'), (0, '寅'), (2, '卯'),
                        (4, '辰'), (6, '巳'), (8, '午'), (10, '未'),
                        (12, '申'), (14, '酉'), (16, '戌'), (18, '亥')):
            dd = sxtwl.JD2DD(jq[idx].jd)
            pts.append((datetime.datetime(int(dd.Y), int(dd.M), int(dd.D),
                                          int(dd.h), int(dd.m), int(dd.s)), mz))
    pts.sort()
    mz = '子'
    for t, z in pts:
        if cur >= t:
            mz = z
        else:
            break
    return mz


def _branch(d):
    o = sxtwl.fromSolar(d.year, d.month, d.day)
    return _month_zhi_at(d), ZHI[o.getDayGZ().dz]


def _all_days(*years):
    for y in years:
        d = datetime.date(y, 1, 1)
        end = datetime.date(y, 12, 31)
        while d <= end:
            yield d
            d += datetime.timedelta(days=1)


DAYS = list(_all_days(2025, 2026, 2027))

# 模块加载即断言：由三合局长生位独立推导"沐浴"（长生+1）== 硬编码表；
# 再断言旧四季表与新表不等（防退回错表）。
_ZHI_ORDER = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
_DERIVED = {}
for _grp, _cs in (('寅午戌', '寅'), ('申子辰', '申'), ('巳酉丑', '巳'), ('亥卯未', '亥')):
    _mu = _ZHI_ORDER[(_ZHI_ORDER.index(_cs) + 1) % 12]      # 沐浴 = 长生 + 1
    for _m in _grp:
        _DERIVED[_m] = _mu
assert _DERIVED == DASHI_CLASSICAL, f'沐浴位推导不符: {_DERIVED}'
assert len(DASHI_CLASSICAL) == 12
_OLD_SEASON = {'寅': '酉', '卯': '酉', '辰': '酉', '巳': '子', '午': '子', '未': '子',
               '申': '卯', '酉': '卯', '戌': '卯', '亥': '午', '子': '午', '丑': '午'}
assert _OLD_SEASON != DASHI_CLASSICAL


def expected_pred(d):
    mz, dz = _branch(d)
    return dz == DASHI_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dz = _branch(d)
    try:
        return ShenShaChecker()._is_dashi({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dz = _branch(d)
    return -12 if dz == DASHI_CLASSICAL.get(mz) else None


def adapter_e2e(d):
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.shensha.修造神煞 import ConstructionShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        items = [x for x in ConstructionShenShaChecker().check(sz, owners=[])
                 if x.get('name') == '大时']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == -12:
            return -12
        return f'BAD:{items}'
    except Exception:
        return _UNAVAILABLE


def expected_golden(d):
    if d in OLD_TABLE_FALSE_POS:
        return False
    if d in OLD_TABLE_FALSE_NEG:
        return True
    return next((gz for gd, gz in GOLDEN if gd == d), None)


def adapter_golden(d):
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        sz = calculate_sizhu(d, 12, 0)
        hit = ShenShaChecker()._is_dashi(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='大时-谓词穷举', category='A',
    description='月神日支，《协纪》卷六"正月起卯逆行四仲"（三合沐浴位），2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='大时-端到端分值', category='A',
    description='修造checker 2026全年：命中唯一一条且-12，未命中无条目',
    inputs=[d for d in DAYS if d.year == 2026],
    expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='大时-黄金日硬锁', category='A',
    description='12个黄金日日柱干支硬锁 + 旧四季错表误报日必须不命中 + 旧漏报日必须命中',
    inputs=[gd for gd, _ in GOLDEN] + OLD_TABLE_FALSE_POS + OLD_TABLE_FALSE_NEG,
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_single_entry_all_checkers():
    """全 checker 回归：各事项全年恰好单条 -12（同名重加死分支不双扣）。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha.通用神煞 import CommonShenShaChecker
    from modules.shensha.修造神煞 import ConstructionShenShaChecker
    from modules.shensha.作灶神煞 import StoveShenShaChecker
    from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
    from modules.shensha.出行神煞 import TravelShenShaChecker
    from modules.shensha.开业神煞 import OpeningShenShaChecker
    from modules.shensha.安葬神煞 import BurialShenShaChecker
    from modules.shensha.安床神煞 import BedShenShaChecker
    from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
    days = [d for d in DAYS if d.year == 2026]
    for cls in (CommonShenShaChecker, ConstructionShenShaChecker, StoveShenShaChecker,
                RuZhaiShenShaChecker, TravelShenShaChecker, OpeningShenShaChecker,
                BurialShenShaChecker, BedShenShaChecker, MarriageShenShaChecker):
        c = cls()
        cnt = 0
        for d in days:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            hits = [x for x in c.check(sz, owners=[]) if x.get('name') == '大时']
            if hits:
                cnt += 1
                assert len(hits) == 1 and hits[0]['score'] == -12, \
                    f'{cls.__name__} {d} 大时条目异常 {hits}'
        assert cnt == 30, f'{cls.__name__} 大时命中 {cnt} 天，期望 30'
    for gd, gz in GOLDEN:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz, f'{gd} 日柱期望{gz} 实际{sz["日柱"]}'


if __name__ == '__main__':
    try:
        _assert_single_entry_all_checkers()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
