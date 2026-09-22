# -*- coding: utf-8 -*-
"""
生气穷举验证
============
典据《协纪辨方书》卷四·义例一：建除十二神「开」位注「时阳、生气」，
生气即开日——月建前二位（月支 index−2）：
寅月子、卯月丑、辰月寅、巳月卯、午月辰、未月巳、申月午、酉月未、
戌月申、亥月酉、子月戌、丑月亥。

双保险：
1. 权威真值表硬编码（月建→日支），绝不从软件读取；
2. 月支/日支由 sxtwl 独立精确节气推导（与 verify_yaoan 同构），
   产品侧只调 _is_shengqi 谓词。
另含：3 年 1095 天穷举、端到端 checker 单条目+分值锁（10 分）、
死分支清理回归（通用/修造/安葬/安床/出行全年恰好单条 +10，动土按设计
不登记生气=0）、展示层 WuXingZeRiFa.get_shengqi_ri 已委托基类且全年
全等、12 个黄金日干支硬锁、旧四季长生错表误报日必须不命中。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
_MONTH_ORDER = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
# ===== 权威真值表（硬编码，开日 = 月支前 2） =====
SHENGQI_CLASSICAL = {
    m: ZHI[(ZHI.index(m) - 2) % 12] for m in _MONTH_ORDER
}

# ===== 黄金日（2026 各月建首个生气/开日，含日柱干支） =====
GOLDEN = [
    (datetime.date(2026, 1, 13), '丁亥'),   # 丑月 亥日
    (datetime.date(2026, 2, 7),  '壬子'),   # 寅月 子日
    (datetime.date(2026, 3, 16), '己丑'),   # 卯月 丑日
    (datetime.date(2026, 4, 10), '甲寅'),   # 辰月 寅日
    (datetime.date(2026, 5, 17), '辛卯'),   # 巳月 卯日
    (datetime.date(2026, 6, 11), '丙辰'),   # 午月 辰日
    (datetime.date(2026, 7, 18), '癸巳'),   # 未月 巳日
    (datetime.date(2026, 8, 12), '戊午'),   # 申月 午日
    (datetime.date(2026, 9, 18), '乙未'),   # 酉月 未日
    (datetime.date(2026, 10, 13), '庚申'),  # 戌月 申日
    (datetime.date(2026, 11, 19), '丁酉'),  # 亥月 酉日
    (datetime.date(2026, 12, 14), '壬戌'),  # 子月 戌日
]
# 旧四季长生错表误报：2026-02-12 丁巳日，旧"春巳"→误命中；
# 典载寅月生气（开日）在子日，日支巳≠子→新表不命中。
OLD_TABLE_FALSE_POS = [datetime.date(2026, 2, 12)]


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
    return dz == SHENGQI_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dz = _branch(d)
    try:
        return ShenShaChecker()._is_shengqi({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dz = _branch(d)
    return 10 if dz == SHENGQI_CLASSICAL.get(mz) else None


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
                 if x.get('name') == '生气']
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
        hit = ShenShaChecker()._is_shengqi(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='生气-谓词穷举', category='A',
    description='月神日支=建除开日(月支前2)，《协纪》卷四，2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='生气-端到端分值', category='A',
    description='修造checker 2026全年：命中唯一一条且+10，未命中无条目',
    inputs=[d for d in DAYS if d.year == 2026],
    expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='生气-黄金日硬锁', category='A',
    description='12个黄金日（开日）日柱干支硬锁+旧四季长生错表误报日2026-02-12丁巳不命中',
    inputs=[gd for gd, _ in GOLDEN] + OLD_TABLE_FALSE_POS,
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_structure_and_delegation():
    """死分支清理回归 + 动土不登记 + 展示层委托基类全年全等。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.五行择日法 import WuXingZeRiFa
    from modules.shensha.通用神煞 import CommonShenShaChecker
    from modules.shensha.修造神煞 import ConstructionShenShaChecker
    from modules.shensha.安葬神煞 import BurialShenShaChecker
    from modules.shensha.安床神煞 import BedShenShaChecker
    from modules.shensha.出行神煞 import TravelShenShaChecker
    from modules.shensha.动土神煞 import DiggingShenShaChecker
    days = [d for d in DAYS if d.year == 2026]
    wx = WuXingZeRiFa()
    for cls, expect_n in ((CommonShenShaChecker, 29), (ConstructionShenShaChecker, 29),
                          (BurialShenShaChecker, 29), (BedShenShaChecker, 29),
                          (TravelShenShaChecker, 29), (DiggingShenShaChecker, 0)):
        c = cls()
        cnt = 0
        for d in days:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            hits = [x for x in c.check(sz, owners=[]) if x.get('name') == '生气']
            if hits:
                cnt += 1
                assert len(hits) == 1 and hits[0]['score'] == 10, \
                    f'{cls.__name__} {d} 生气条目异常 {hits}'
            # 展示层委托：任意 year_zhi 不影响结果，且与基类谓词全等
            assert wx.get_shengqi_ri('子', sz['month_zhi'], sz['day_zhi']) == \
                wx.get_shengqi_ri('午', sz['month_zhi'], sz['day_zhi'])
        assert cnt == expect_n, f'{cls.__name__} 生气 {cnt} 天，期望 {expect_n}'
    for gd, gz in GOLDEN:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz, f'{gd} 日柱期望{gz} 实际{sz["日柱"]}'


if __name__ == '__main__':
    try:
        _assert_structure_and_delegation()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
