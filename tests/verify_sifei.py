# -*- coding: utf-8 -*-
"""
四废穷举验证
============
典据《协纪辨方书》四废条：四废者四时衰废之气，被当令旺气所克。
  春（寅卯辰月）木旺金废 → 庚申、辛酉
  夏（巳午未月）火旺水废 → 壬子、癸亥
  秋（申酉戌月）金旺木废 → 甲寅、乙卯
  冬（亥子丑月）水旺火废 → 丙午、丁巳
即月支查**日柱干支**（8 柱，含阴干支）。

双保险：
1. 权威真值表硬编码（月建→日柱干支），绝不从软件读取；
2. 月支/日干支由 sxtwl 独立精确节气推导（与 verify_minri 同构），
   产品侧只调 _is_sifei 谓词。

另含：2026 全年 365 天穷举、端到端 checker 单条目+分值锁（-15）、
14 个黄金日（日柱干支硬锁）、旧基类"仅比日干"的假命中日必须不命中、
旧基类漏判的 6 个阴干支日必须命中。

旧实现（git HEAD 神煞基类.py）只比日干（春见庚日、夏见壬日、秋见甲日、
冬见丙日），属放宽口径：2026 实测命中 39 天，典载仅 14 天——多出 31 天
假四废，且漏判 6 天阴干支日（辛酉/癸亥/乙卯/丁巳）。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# ===== 权威真值表（硬编码，《协纪》四废，月支查日柱干支，8 柱） =====
SIFEI_CLASSICAL = {
    '寅': ('庚申', '辛酉'), '卯': ('庚申', '辛酉'), '辰': ('庚申', '辛酉'),
    '巳': ('壬子', '癸亥'), '午': ('壬子', '癸亥'), '未': ('壬子', '癸亥'),
    '申': ('甲寅', '乙卯'), '酉': ('甲寅', '乙卯'), '戌': ('甲寅', '乙卯'),
    '亥': ('丙午', '丁巳'), '子': ('丙午', '丁巳'), '丑': ('丙午', '丁巳'),
}

# 14 个黄金日：2026 全年典载四废命中日（日柱干支硬锁）
GOLDEN_HIT = [
    (datetime.date(2026, 2, 1),  '丙午'),   # 丑月
    (datetime.date(2026, 2, 15), '庚申'),   # 寅月
    (datetime.date(2026, 2, 16), '辛酉'),   # 寅月
    (datetime.date(2026, 4, 16), '庚申'),   # 辰月
    (datetime.date(2026, 4, 17), '辛酉'),   # 辰月
    (datetime.date(2026, 6, 7),  '壬子'),   # 午月
    (datetime.date(2026, 6, 18), '癸亥'),   # 午月
    (datetime.date(2026, 8, 6),  '壬子'),   # 未月
    (datetime.date(2026, 8, 8),  '甲寅'),   # 申月
    (datetime.date(2026, 8, 9),  '乙卯'),   # 申月
    (datetime.date(2026, 10, 7), '甲寅'),   # 酉月
    (datetime.date(2026, 10, 8), '乙卯'),   # 酉月
    (datetime.date(2026, 11, 28), '丙午'),  # 亥月
    (datetime.date(2026, 12, 9), '丁巳'),   # 子月
]

# 旧基类"仅比日干"的假命中日（旧命中、典载不命中）：新实现必须不命中
OLD_FALSE_POS = [
    datetime.date(2026, 1, 2),    # 子月 丙子日：旧见丙日命中，典载冬在丙午丁巳
    datetime.date(2026, 2, 5),    # 寅月 庚戌日：旧见庚日命中，典载春在庚申辛酉
    datetime.date(2026, 2, 25),   # 寅月 庚午日：同上
    datetime.date(2026, 3, 7),    # 卯月 庚辰日：同上
    datetime.date(2026, 5, 8),    # 巳月 壬午日：旧见壬日命中，典载夏在壬子癸亥
    datetime.date(2026, 8, 18),   # 申月 甲子日：旧见甲日命中，典载秋在甲寅乙卯
]

# 旧基类漏判日（旧不命中、典载命中）：新实现必须命中（6 个阴干支日）
NEW_ONLY = [
    datetime.date(2026, 2, 16),   # 寅月 辛酉日
    datetime.date(2026, 4, 17),   # 辰月 辛酉日
    datetime.date(2026, 6, 18),   # 午月 癸亥日
    datetime.date(2026, 8, 9),    # 申月 乙卯日
    datetime.date(2026, 10, 8),   # 酉月 乙卯日
    datetime.date(2026, 12, 9),   # 子月 丁巳日
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

# 加载即断言：四季连续三月同表、四季各 2 柱、共 8 个不同日柱干支
_SEASON_GROUPS = (('寅', '卯', '辰'), ('巳', '午', '未'), ('申', '酉', '戌'), ('亥', '子', '丑'))
assert all(SIFEI_CLASSICAL[g[0]] == SIFEI_CLASSICAL[g[1]] == SIFEI_CLASSICAL[g[2]]
           for g in _SEASON_GROUPS)
assert len(SIFEI_CLASSICAL) == 12
assert all(len(v) == 2 for v in SIFEI_CLASSICAL.values())
assert {SIFEI_CLASSICAL[g[0]] for g in _SEASON_GROUPS} == {
    ('庚申', '辛酉'), ('壬子', '癸亥'), ('甲寅', '乙卯'), ('丙午', '丁巳')}
assert len({p for vs in SIFEI_CLASSICAL.values() for p in vs}) == 8
# 旧宽口径（仅日干）与新表的关系：旧命中集 ⊋ 新命中集，差集为阴干支日
_OLD_GAN_BY_MONTH = {}
for _g, _old_gan in (('寅', '庚'), ('卯', '庚'), ('辰', '庚'),
                     ('巳', '壬'), ('午', '壬'), ('未', '壬'),
                     ('申', '甲'), ('酉', '甲'), ('戌', '甲'),
                     ('亥', '丙'), ('子', '丙'), ('丑', '丙')):
    _OLD_GAN_BY_MONTH[_g] = _old_gan
assert all(g in SIFEI_CLASSICAL[m][0] or g in SIFEI_CLASSICAL[m][1]
           for m, g in _OLD_GAN_BY_MONTH.items())          # 旧口径日干 ⊂ 新表首字
assert all(SIFEI_CLASSICAL[m][0][0] == _OLD_GAN_BY_MONTH[m] for m in SIFEI_CLASSICAL)


def expected_pred(d):
    mz, dg, dz = _branch(d)
    return (dg + dz) in SIFEI_CLASSICAL.get(mz, ())


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dg, dz = _branch(d)
    try:
        return ShenShaChecker()._is_sifei(
            {'month_zhi': mz, 'day_gan': dg, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dg, dz = _branch(d)
    return -15 if (dg + dz) in SIFEI_CLASSICAL.get(mz, ()) else None


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
                 if x.get('name') == '四废']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == -15:
            return -15
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
        hit = ShenShaChecker()._is_sifei(sz)
        if d in dict(GOLDEN_HIT):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='四废-谓词穷举', category='B',
    description='月支查日柱干支，《协纪》四季衰废之气（8 柱），2026 共 365 天，sxtwl 独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='四废-端到端分值', category='B',
    description='安葬 checker 2026 全年：命中唯一一条且 -15，未命中无条目',
    inputs=DAYS, expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='四废-黄金日硬锁', category='B',
    description='14 个黄金日日柱干支硬锁 + 旧仅日干假命中日必须不命中 + 旧漏判阴干支日必须命中',
    inputs=sorted({gd for gd, _ in GOLDEN_HIT} | set(OLD_FALSE_POS) | set(NEW_ONLY)),
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_single_entry_base_checkers():
    """继承基类的事项回归：2026 命中日恰好单条 '四废' -15。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha.安葬神煞 import BurialShenShaChecker
    from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
    from modules.shensha.开业神煞 import OpeningShenShaChecker
    hit_days = [gd for gd, _ in GOLDEN_HIT]
    for cls in (BurialShenShaChecker, RuZhaiShenShaChecker, OpeningShenShaChecker):
        c = cls()
        for d in hit_days:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            hits = [x for x in c.check(sz, owners=[]) if x.get('name') == '四废']
            assert len(hits) == 1 and hits[0]['score'] == -15, \
                f'{cls.__name__} {d} 四废条目异常 {hits}'
    # 日柱硬锁
    for gd, gz in GOLDEN_HIT:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz, f'{gd} 日柱期望{gz} 实际{sz["日柱"]}'


if __name__ == '__main__':
    try:
        _assert_single_entry_base_checkers()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
