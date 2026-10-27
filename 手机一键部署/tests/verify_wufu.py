# -*- coding: utf-8 -*-
"""
五富穷举验证
============
典据《协纪辨方书》卷六·义例四：「五富者，正月起亥，顺行四孟」，
即按月建序循环四孟（亥、寅、巳、申）：
寅月亥、卯月寅、辰月巳、巳月申、午月亥、未月寅、申月巳、酉月申、
戌月亥、亥月寅、子月巳、丑月申。

双保险：
1. 权威真值表硬编码（月建→日支），绝不从软件读取；
2. 期望与适配的月支/日支均由 sxtwl 独立精确节气推导（见
   verify_yaoan._month_zhi_at 同构实现），产品侧只调 _is_wufu 谓词。
另含：3 年 1095 天穷举、端到端 checker 单条目+分值锁（12 分）、
死分支清理回归（7 个事项 checker 删除重复登记后仍经基类 super 单条命中）、
12 个黄金日干支硬锁、2 个旧三合局错表误报日必须不命中。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# ===== 权威真值表（硬编码，《协纪辨方书》卷六，四孟循环） =====
_MONTH_ORDER = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
_SIMENG = ['亥', '寅', '巳', '申']
WUFU_CLASSICAL = {m: _SIMENG[i % 4] for i, m in enumerate(_MONTH_ORDER)}

# ===== 黄金日（2026 各月建首个五富日，含日柱干支，可对历书人工核对） =====
GOLDEN = [
    (datetime.date(2026, 1, 10), '甲申'),   # 丑月 申日
    (datetime.date(2026, 2, 6),  '辛亥'),   # 寅月 亥日
    (datetime.date(2026, 3, 17), '庚寅'),   # 卯月 寅日
    (datetime.date(2026, 4, 13), '丁巳'),   # 辰月 巳日
    (datetime.date(2026, 5, 10), '甲申'),   # 巳月 申日
    (datetime.date(2026, 6, 6),  '辛亥'),   # 午月 亥日
    (datetime.date(2026, 7, 15), '庚寅'),   # 未月 寅日
    (datetime.date(2026, 8, 11), '丁巳'),   # 申月 巳日
    (datetime.date(2026, 9, 19), '丙申'),   # 酉月 申日
    (datetime.date(2026, 10, 16), '癸亥'),  # 戌月 亥日
    (datetime.date(2026, 11, 12), '庚寅'),  # 亥月 寅日
    (datetime.date(2026, 12, 9),  '丁巳'),  # 子月 巳日
]
# 旧三合局错表误报样例：卯月申日（旧"亥卯未→申"）、申月寅日（旧"申子辰→寅"）
OLD_TABLE_FALSE_POS = [datetime.date(2026, 3, 11), datetime.date(2026, 8, 8)]


def _month_zhi_at(d, hour=12):
    """独立精确节气月支（与 verify_yaoan 同构），不复用 sxtwl 粗月柱。"""
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
    return dz == WUFU_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dz = _branch(d)
    try:
        return ShenShaChecker()._is_wufu({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dz = _branch(d)
    return 12 if dz == WUFU_CLASSICAL.get(mz) else None


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
                 if x.get('name') == '五富']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == 12:
            return 12
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
        hit = ShenShaChecker()._is_wufu(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='五富-谓词穷举', category='A',
    description='月神日支，《协纪》卷六"正月起亥顺行四孟"，2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='五富-端到端分值', category='A',
    description='修造checker 2026全年：命中唯一一条且+12，未命中无条目',
    inputs=[d for d in DAYS if d.year == 2026],
    expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='五富-黄金日硬锁', category='A',
    description='12个黄金日（各月建首个）日柱干支硬锁+2个旧三合局错表误报日必须不命中',
    inputs=[gd for gd, _ in GOLDEN] + OLD_TABLE_FALSE_POS,
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_single_entry_all_checkers():
    """死分支清理回归：删除 7 checker 重复登记后，全年仍恰好单条 +12。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha.通用神煞 import CommonShenShaChecker
    from modules.shensha.修造神煞 import ConstructionShenShaChecker
    from modules.shensha.动土神煞 import DiggingShenShaChecker
    from modules.shensha.出行神煞 import TravelShenShaChecker
    from modules.shensha.安葬神煞 import BurialShenShaChecker
    from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
    from modules.shensha.安床神煞 import BedShenShaChecker
    from modules.shensha.开业神煞 import OpeningShenShaChecker
    days = [d for d in DAYS if d.year == 2026]
    for cls in (CommonShenShaChecker, ConstructionShenShaChecker,
                DiggingShenShaChecker, TravelShenShaChecker, BurialShenShaChecker,
                RuZhaiShenShaChecker, BedShenShaChecker, OpeningShenShaChecker):
        c = cls()
        cnt = 0
        for d in days:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            hits = [x for x in c.check(sz, owners=[]) if x.get('name') == '五富']
            if hits:
                cnt += 1
                assert len(hits) == 1 and hits[0]['score'] == 12, \
                    f'{cls.__name__} {d} 五富条目异常 {hits}'
        assert cnt == 30, f'{cls.__name__} 五富命中 {cnt} 天，期望 30'
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
