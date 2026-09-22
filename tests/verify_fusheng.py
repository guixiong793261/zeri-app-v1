# -*- coding: utf-8 -*-
"""
福生穷举验证
============
典据《协纪辨方书》卷六·义例四：「福生者，正月酉、二月卯、三月戌、
四月辰、五月亥、六月巳、七月子、八月午、九月丑、十月未、十一月寅、
十二月申」——月神查**日支**。

双保险：
1. 权威真值表硬编码（月建→日支），绝不从软件读取；
2. 月支/日支由 sxtwl 独立精确节气推导（与 verify_yaoan 同构），
   产品侧只调 _is_fusheng 谓词。
另含：3 年 1095 天穷举、端到端 checker 单条目+分值锁（10 分）、
死分支清理回归（通用/修造/入宅/开业/嫁娶全年恰好单条 +10）、
12 个黄金日干支硬锁、旧"日干"错表误报日必须不命中。
旧实现误查日干（正月甲、二月乙……），与典载日支口径全年 0 天重合。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，《协纪辨方书》卷六，查日支） =====
FUSHENG_CLASSICAL = {
    '寅': '酉', '卯': '卯', '辰': '戌', '巳': '辰',
    '午': '亥', '未': '巳', '申': '子', '酉': '午',
    '戌': '丑', '亥': '未', '子': '寅', '丑': '申',
}

# ===== 黄金日（2026 各月建首个福生日，含日柱干支，可对历书人工核对） =====
GOLDEN = [
    (datetime.date(2026, 1, 4),  '戊寅'),   # 子月 寅日
    (datetime.date(2026, 1, 10), '甲申'),   # 丑月 申日
    (datetime.date(2026, 2, 4),  '己酉'),   # 寅月 酉日
    (datetime.date(2026, 3, 6),  '己卯'),   # 卯月 卯日
    (datetime.date(2026, 4, 6),  '庚戌'),   # 辰月 戌日
    (datetime.date(2026, 5, 6),  '庚辰'),   # 巳月 辰日
    (datetime.date(2026, 6, 6),  '辛亥'),   # 午月 亥日
    (datetime.date(2026, 7, 18), '癸巳'),   # 未月 巳日
    (datetime.date(2026, 8, 18), '甲子'),   # 申月 子日
    (datetime.date(2026, 9, 17), '甲午'),   # 酉月 午日
    (datetime.date(2026, 10, 18), '乙丑'),  # 戌月 丑日
    (datetime.date(2026, 11, 17), '乙未'),  # 亥月 未日
]
# 旧"日干"错表误报：2026-02-09 甲寅日，旧表寅月查日干甲→误命中；
# 典载寅月福生在酉日，日支寅≠酉→新表不命中。
OLD_TABLE_FALSE_POS = [datetime.date(2026, 2, 9)]


def _month_zhi_at(d, hour=12):
    """独立精确节气月支（与 verify_yaoan 同构）。"""
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


def expected_pred(d):
    mz, dz = _branch(d)
    return dz == FUSHENG_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dz = _branch(d)
    try:
        return ShenShaChecker()._is_fusheng({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dz = _branch(d)
    return 10 if dz == FUSHENG_CLASSICAL.get(mz) else None


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
                 if x.get('name') == '福生']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == 10:
            return 10
        return f'BAD:{items}'
    except Exception:
        return _UNAVAILABLE


def expected_golden(d):
    if d in OLD_TABLE_FALSE_POS:
        return False
    return next((gz for gd, gz in GOLDEN if gd == d), None)


def adapter_golden(d):
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        sz = calculate_sizhu(d, 12, 0)
        hit = ShenShaChecker()._is_fusheng(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='福生-谓词穷举', category='A',
    description='月神日支，《协纪》卷六正酉二卯…十二申，2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='福生-端到端分值', category='A',
    description='修造checker 2026全年：命中唯一一条且+10，未命中无条目',
    inputs=[d for d in DAYS if d.year == 2026],
    expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='福生-黄金日硬锁', category='A',
    description='12个黄金日日柱干支硬锁+旧日干错表误报日(2026-02-09甲寅)必须不命中',
    inputs=[gd for gd, _ in GOLDEN] + OLD_TABLE_FALSE_POS,
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_single_entry_all_checkers():
    """死分支清理回归：通用/修造/入宅/开业/嫁娶全年恰好单条 +10。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha.通用神煞 import CommonShenShaChecker
    from modules.shensha.修造神煞 import ConstructionShenShaChecker
    from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
    from modules.shensha.开业神煞 import OpeningShenShaChecker
    from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
    days = [d for d in DAYS if d.year == 2026]
    for cls in (CommonShenShaChecker, ConstructionShenShaChecker,
                RuZhaiShenShaChecker, OpeningShenShaChecker, MarriageShenShaChecker):
        c = cls()
        cnt = 0
        for d in days:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            hits = [x for x in c.check(sz, owners=[]) if x.get('name') == '福生']
            if hits:
                cnt += 1
                assert len(hits) == 1 and hits[0]['score'] == 10, \
                    f'{cls.__name__} {d} 福生条目异常 {hits}'
        assert cnt == 31, f'{cls.__name__} 福生命中 {cnt} 天，期望 31'
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
