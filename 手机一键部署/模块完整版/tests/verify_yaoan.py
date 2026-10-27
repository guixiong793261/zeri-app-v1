# -*- coding: utf-8 -*-
"""
要安穷举验证
============
典据《协纪辨方书》卷六·义例四：「要安者，正月寅、二月申、三月卯、
四月酉、五月辰、六月戌、七月巳、八月亥、九月午、十月子、十一月未、
十二月丑」（《星历考原》卷三同载）。

双保险：
1. 权威真值表硬编码（月建→日支），绝不从软件读取；
2. 期望与适配的月支/日支均由 sxtwl 独立推导（节气界月柱+日柱），
   产品侧只调 _is_yaoan 谓词，杜绝共用同一套月日支逻辑导致的"自证"。
另含：3 年 1095 天穷举、端到端 checker 单条目+分值锁（8 分）、
月厌不同日（消除凶吉双扣）反向断言、12 个黄金日干支硬锁。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，《协纪辨方书》卷六） =====
YAOAN_CLASSICAL = {
    '寅': '寅', '卯': '申', '辰': '卯', '巳': '酉',
    '午': '辰', '未': '戌', '申': '巳', '酉': '亥',
    '戌': '午', '亥': '子', '子': '未', '丑': '丑',
}

# ===== 黄金日（2026 各月建首个要安日，含日柱干支，可对历书人工核对） =====
# (公历日, 期望日柱)；月建依节气
GOLDEN = [
    (datetime.date(2026, 1, 15), '己丑'),   # 丑月（十二月）丑日
    (datetime.date(2026, 2, 9),  '甲寅'),   # 寅月 寅日
    (datetime.date(2026, 3, 11), '甲申'),   # 卯月 申日
    (datetime.date(2026, 4, 11), '乙卯'),   # 辰月 卯日
    (datetime.date(2026, 5, 11), '乙酉'),   # 巳月 酉日
    (datetime.date(2026, 6, 11), '丙辰'),   # 午月 辰日
    (datetime.date(2026, 7, 11), '丙戌'),   # 未月 戌日
    (datetime.date(2026, 8, 11), '丁巳'),   # 申月 巳日
    (datetime.date(2026, 9, 10), '丁亥'),   # 酉月 亥日
    (datetime.date(2026, 10, 11), '戊午'),  # 戌月 午日
    (datetime.date(2026, 11, 10), '戊子'),  # 亥月 子日
    (datetime.date(2026, 12, 11), '己未'),  # 子月（十一月）未日
]
# 旧错表（=月厌表）误报样例：2026-01-02 子月丙子日，典载要安子月在未
OLD_TABLE_FALSE_POS = [datetime.date(2026, 1, 2), datetime.date(2026, 1, 13)]


def _month_zhi_at(d, hour=12):
    """独立精确节气月支：以当日 hour 点（默认午时12:00）与交节时刻比较。

    sxtwl.Day.getMonthGZ() 在交节当日按整日归属，不到分钟，故此处不复用；
    改用 getJieQiByYear 天文历点自行判断（换月点：大雪→子、小寒→丑、
    立春→寅…），与典载"过节换月"口径一致。推导代码独立，仅与产品共用
    sxtwl 天文数据源。
    """
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
    """独立取（精确节气月支, 日支），不经产品四柱接口。"""
    o = sxtwl.fromSolar(d.year, d.month, d.day)
    return _month_zhi_at(d), ZHI[o.getDayGZ().dz], None


def _day_gz(d):
    o = sxtwl.fromSolar(d.year, d.month, d.day)
    GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    g = o.getDayGZ()
    return GAN[g.tg] + ZHI[g.dz]


def _all_days(*years):
    for y in years:
        d = datetime.date(y, 1, 1)
        end = datetime.date(y, 12, 31)
        while d <= end:
            yield d
            d += datetime.timedelta(days=1)


DAYS = list(_all_days(2025, 2026, 2027))


# ---------- Case 1：谓词层 3 年穷举（sxtwl 独立月日支） ----------
def expected_pred(d):
    mz, dz, _ = _branch(d)
    return dz == YAOAN_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dz, _ = _branch(d)
    try:
        return ShenShaChecker()._is_yaoan({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


# ---------- Case 2：端到端 2026 全年（修造 checker：单条目+分值 8 锁） ----------
def expected_e2e(d):
    mz, dz, _ = _branch(d)
    return 8 if dz == YAOAN_CLASSICAL.get(mz) else None


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
                 if x.get('name') == '要安']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == 8:
            return 8
        return f'BAD:{items}'
    except Exception:
        return _UNAVAILABLE


# ---------- Case 3：黄金日 + 旧误报日 + 月厌不同日（硬锁） ----------
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
        hit = ShenShaChecker()._is_yaoan(sz)
        if d in dict(GOLDEN):
            # 黄金日：谓词必须命中且产品日柱必须等于硬编码干支
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='要安-谓词穷举', category='A',
    description='月神日支，《协纪》卷六（正寅二申…），2025-2027 共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='要安-端到端分值', category='A',
    description='修造checker 2026全年：命中唯一一条且+8，未命中无条目',
    inputs=[d for d in DAYS if d.year == 2026],
    expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='要安-黄金日硬锁', category='A',
    description='12个黄金日（各月建首个）日柱干支硬锁+2个旧表误报日必须不命中',
    inputs=[gd for gd, _ in GOLDEN] + OLD_TABLE_FALSE_POS,
    expected=expected_golden, adapter=adapter_golden, compare='eq')


CASES = [case_pred, case_e2e, case_golden]


# 月厌双扣反向断言（独立于引擎，失败抛 AssertionError → 退出码1）
def _assert_no_yueyan_overlap():
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha.神煞基类 import ShenShaChecker
    c = ShenShaChecker()
    bad = []
    for d in [d for d in DAYS if d.year == 2026]:
        sz = calculate_sizhu(d, 12, 0)
        if c._is_yaoan(sz) and c._is_yueyan(sz):
            bad.append(d.isoformat())
    assert not bad, f'要安与月厌仍有同日双扣: {bad[:5]}'
    # 12 黄金日额外断言日柱字符串（不依赖 adapter 的条件返回）
    for gd, gz in GOLDEN:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz, f'{gd} 日柱期望{gz} 实际{sz["日柱"]}'
        assert c._is_yaoan(sz), f'{gd} 应为要安'


if __name__ == '__main__':
    try:
        _assert_no_yueyan_overlap()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli([case_pred, case_e2e, case_golden]))
