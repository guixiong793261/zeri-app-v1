# -*- coding: utf-8 -*-
"""
往亡穷举验证
============
典据《协纪辨方书》往亡条口诀：
  「正寅二巳三申四亥五卯六午七酉八子九辰十未十一戌十二丑」
即按节气月支查**日支**：
  寅月寅、卯月巳、辰月申、巳月亥、午月卯、未月午、
  申月酉、酉月子、戌月辰、亥月未、子月戌、丑月丑。

双保险：
1. 权威真值表硬编码（月建→日支），绝不从软件读取；
2. 月支/日支由 sxtwl 独立精确节气推导（与 verify_minri 同构），
   产品侧只调 _is_wangwang 谓词。

另含：2026 全年 365 天穷举、端到端 checker 单条目+分值锁、
30 个黄金日（日支硬锁）、旧基类"寅巳申亥每 4 月循环"的假命中日必须
不命中、旧基类漏判日必须命中。

旧实现（git HEAD 神煞基类.py）为"寅巳申亥每 4 月循环"变体：
2026 实测命中 29 天（19 天假命中 + 20 天漏判，与口诀交集仅 10）。
出行神煞另有与口诀零交集的错表，本批不动，另开挂账诊断。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# ===== 权威真值表（硬编码，《协纪》往亡口诀，月支查日支） =====
WANGWANG_CLASSICAL = {
    '寅': '寅', '卯': '巳', '辰': '申', '巳': '亥',
    '午': '卯', '未': '午', '申': '酉', '酉': '子',
    '戌': '辰', '亥': '未', '子': '戌', '丑': '丑',
}

# 旧基类"寅巳申亥每 4 月循环"错表（git HEAD 实测）
WANGWANG_OLD_BASE = {
    '寅': '寅', '卯': '巳', '辰': '申', '巳': '亥',
    '午': '寅', '未': '巳', '申': '申', '酉': '亥',
    '戌': '寅', '亥': '巳', '子': '申', '丑': '亥',
}

# 30 个黄金日：2026 全年口诀命中日（日支硬锁）
GOLDEN_HIT = [
    (datetime.date(2026, 1, 15), '己丑'), (datetime.date(2026, 1, 27), '辛丑'),
    (datetime.date(2026, 2, 9),  '甲寅'), (datetime.date(2026, 2, 21), '丙寅'),
    (datetime.date(2026, 3, 5),  '戊寅'),
    (datetime.date(2026, 3, 8),  '辛巳'), (datetime.date(2026, 3, 20), '癸巳'),
    (datetime.date(2026, 4, 1),  '乙巳'),
    (datetime.date(2026, 4, 16), '庚申'), (datetime.date(2026, 4, 28), '壬申'),
    (datetime.date(2026, 5, 13), '丁亥'), (datetime.date(2026, 5, 25), '己亥'),
    (datetime.date(2026, 6, 10), '乙卯'), (datetime.date(2026, 6, 22), '丁卯'),
    (datetime.date(2026, 7, 4),  '己卯'),
    (datetime.date(2026, 7, 7),  '壬午'), (datetime.date(2026, 7, 19), '甲午'),
    (datetime.date(2026, 7, 31), '丙午'),
    (datetime.date(2026, 8, 15), '辛酉'), (datetime.date(2026, 8, 27), '癸酉'),
    (datetime.date(2026, 9, 11), '戊子'), (datetime.date(2026, 9, 23), '庚子'),
    (datetime.date(2026, 10, 5), '壬子'),
    (datetime.date(2026, 10, 9), '丙辰'), (datetime.date(2026, 10, 21), '戊辰'),
    (datetime.date(2026, 11, 2), '庚辰'),
    (datetime.date(2026, 11, 17), '乙未'), (datetime.date(2026, 11, 29), '丁未'),
    (datetime.date(2026, 12, 14), '壬戌'), (datetime.date(2026, 12, 26), '甲戌'),
]

# 旧基类假命中日（旧命中、口诀不命中）：新实现必须不命中
OLD_FALSE_POS = [
    datetime.date(2026, 1, 13),   # 丑月 丁亥日：旧丑月亥，口诀丑月丑
    datetime.date(2026, 6, 9),    # 午月 甲寅日：旧午月寅，口诀午月卯
    datetime.date(2026, 9, 7),    # 申月 甲申日：旧申月申，口诀申月酉
    datetime.date(2026, 11, 15),  # 亥月 癸巳日：旧亥月巳，口诀亥月未
]

# 旧基类漏判日（旧不命中、口诀命中）：新实现必须命中
NEW_ONLY = [
    datetime.date(2026, 1, 15),   # 丑月 己丑日：口诀丑月丑，旧丑月亥
    datetime.date(2026, 6, 10),   # 午月 乙卯日：口诀午月卯，旧午月寅
    datetime.date(2026, 9, 11),   # 酉月 戊子日：口诀酉月子，旧酉月亥
    datetime.date(2026, 11, 17),  # 亥月 乙未日：口诀亥月未，旧亥月巳
]


def _month_zhi_at(d, hour=12):
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
    gz = o.getDayGZ()
    return _month_zhi_at(d), GAN[gz.tg], ZHI[gz.dz]


def _all_days(*years):
    for y in years:
        d = datetime.date(y, 1, 1)
        end = datetime.date(y, 12, 31)
        while d <= end:
            yield d
            d += datetime.timedelta(days=1)


DAYS = list(_all_days(2026))

# 加载即断言：口诀表 12 月全覆盖、值域非空、旧错表与新表不同且交集为部分月
assert len(WANGWANG_CLASSICAL) == 12
assert all(v in ZHI for v in WANGWANG_CLASSICAL.values())
assert len(WANGWANG_OLD_BASE) == 12
_diff_months = {m for m in WANGWANG_CLASSICAL if WANGWANG_CLASSICAL[m] != WANGWANG_OLD_BASE[m]}
assert _diff_months == {'午', '未', '申', '酉', '戌', '亥', '子', '丑'}
assert {m for m in WANGWANG_CLASSICAL
        if WANGWANG_CLASSICAL[m] == WANGWANG_OLD_BASE[m]} == {'寅', '卯', '辰', '巳'}


def expected_pred(d):
    mz, dg, dz = _branch(d)
    return dz == WANGWANG_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dg, dz = _branch(d)
    try:
        return ShenShaChecker()._is_wangwang({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dg, dz = _branch(d)
    return -20 if dz == WANGWANG_CLASSICAL.get(mz) else None


def adapter_e2e(d):
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.shensha.安葬神煞 import BurialShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        items = [x for x in BurialShenShaChecker().check(sz, owners=[])
                 if x.get('name') == '往亡']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == -20:
            return -20
        return f'BAD:{items}'
    except Exception:
        return _UNAVAILABLE


def expected_golden(d):
    gz = next((gz for gd, gz in GOLDEN_HIT if gd == d), None)
    if gz is not None:
        return gz                       # 日柱干支硬锁
    if d in OLD_FALSE_POS:
        return False
    if d in NEW_ONLY:
        return True
    return None


def adapter_golden(d):
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        sz = calculate_sizhu(d, 12, 0)
        hit = ShenShaChecker()._is_wangwang(sz)
        if d in dict(GOLDEN_HIT):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='往亡-谓词穷举', category='B',
    description='月支查日支，《协纪》口诀"正寅二巳三申四亥…"，2026 共 365 天，sxtwl 独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='往亡-端到端分值', category='B',
    description='安葬 checker 2026 全年：命中唯一一条且 -20，未命中无条目',
    inputs=DAYS, expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='往亡-黄金日硬锁', category='B',
    description='30 个黄金日日柱干支硬锁 + 旧 4 月循环假命中日必须不命中 + 旧漏判日必须命中',
    inputs=sorted({gd for gd, _ in GOLDEN_HIT} | set(OLD_FALSE_POS) | set(NEW_ONLY)),
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_single_entry_checkers():
    """安葬/入宅/嫁娶：2026 命中日恰好单条往亡 -20（2026-10 A6-3 异名收口后
    全事项统一典载正名 '往亡'）。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha.安葬神煞 import BurialShenShaChecker
    from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
    from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
    hit_days = [gd for gd, _ in GOLDEN_HIT]
    for cls, name in ((BurialShenShaChecker, '往亡'),
                      (RuZhaiShenShaChecker, '往亡'),
                      (MarriageShenShaChecker, '往亡')):
        c = cls()
        for d in hit_days:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            hits = [x for x in c.check(sz, owners=[]) if x.get('name') == name]
            assert len(hits) == 1 and hits[0]['score'] == -20, \
                f'{cls.__name__} {d} {name} 条目异常 {hits}'
    for gd, gz in GOLDEN_HIT:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz, f'{gd} 日柱期望{gz} 实际{sz["日柱"]}'


if __name__ == '__main__':
    try:
        _assert_single_entry_checkers()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
