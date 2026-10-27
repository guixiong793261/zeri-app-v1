# -*- coding: utf-8 -*-
"""
圣心穷举验证
============
典据《协纪辨方书》卷六·义例四引《枢要历》：「圣心者，月中福神也。其日宜上表章，
行恩泽，营百事。」《历例》：「正月亥，二月巳，三月子，四月午，五月丑，六月未，
七月寅，八月申，九月卯，十月酉，十一月辰，十二月戌。」（《星历考原》卷三同载）

双保险（verify_wufu 同构）：
1. 权威真值表硬编码（月建→日支），绝不从软件读取；
2. 期望与适配的月支/日支均由 sxtwl 独立精确节气推导，产品侧只调 _is_shengxin。
另含：3 年 1095 天穷举、端到端 checker 单条目+分值锁（+8 通配）、
12 个黄金日干支硬锁（2026 各月建首个圣心日，探针 C:\\Temp\\_golden_sxjs.py 推算）。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，《协纪辨方书》卷六，月建序寅→丑） =====
SHENGXIN_CLASSICAL = {
    '寅': '亥', '卯': '巳', '辰': '子', '巳': '午', '午': '丑', '未': '未',
    '申': '寅', '酉': '申', '戌': '卯', '亥': '酉', '子': '辰', '丑': '戌'
}

# ===== 黄金日（2026 各月建首个圣心日+日柱，可对历书人工核对） =====
GOLDEN = [
    (datetime.date(2026, 1, 12), '丙戌'),   # 丑月 戌日
    (datetime.date(2026, 2, 6),  '辛亥'),   # 寅月 亥日
    (datetime.date(2026, 3, 8),  '辛巳'),   # 卯月 巳日
    (datetime.date(2026, 4, 8),  '壬子'),   # 辰月 子日
    (datetime.date(2026, 5, 8),  '壬午'),   # 巳月 午日
    (datetime.date(2026, 6, 8),  '癸丑'),   # 午月 丑日
    (datetime.date(2026, 7, 8),  '癸未'),   # 未月 未日
    (datetime.date(2026, 8, 8),  '甲寅'),   # 申月 寅日
    (datetime.date(2026, 9, 19), '丙申'),   # 酉月 申日
    (datetime.date(2026, 10, 20), '丁卯'),  # 戌月 卯日
    (datetime.date(2026, 11, 19), '丁酉'),  # 亥月 酉日
    (datetime.date(2026, 12, 8),  '丙辰'),  # 子月 辰日
]


def _month_zhi_at(d, hour=12):
    """独立精确节气月支（与 verify_wufu 同构），不复用 sxtwl 粗月柱。"""
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
    return dz == SHENGXIN_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dz = _branch(d)
    try:
        return ShenShaChecker()._is_shengxin({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dz = _branch(d)
    return 8 if dz == SHENGXIN_CLASSICAL.get(mz) else None


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
                 if x.get('name') == '圣心']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == 8:
            return 8
        return f'BAD:{items}'
    except Exception:
        return _UNAVAILABLE


def expected_golden(d):
    return next((gz for gd, gz in GOLDEN if gd == d), None)


def adapter_golden(d):
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        sz = calculate_sizhu(d, 12, 0)
        hit = ShenShaChecker()._is_shengxin(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='圣心-谓词穷举', category='A',
    description='月神日支，《协纪》卷六"正月亥二月巳…十二月戌"，2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='圣心-端到端分值', category='A',
    description='修造checker 2026全年：命中唯一一条且+8（通配键），未命中无条目',
    inputs=[d for d in DAYS if d.year == 2026],
    expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='圣心-黄金日硬锁', category='A',
    description='12个黄金日（2026各月建首个圣心日）日柱干支硬锁',
    inputs=[gd for gd, _ in GOLDEN],
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_golden_ganzhi():
    """黄金日日柱反断言：12 个日期的日柱必须与硬编码一致。"""
    from modules.四柱计算器 import calculate_sizhu
    for gd, gz in GOLDEN:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz, f'{gd} 日柱期望{gz} 实际{sz["日柱"]}'


if __name__ == '__main__':
    try:
        _assert_golden_ganzhi()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
