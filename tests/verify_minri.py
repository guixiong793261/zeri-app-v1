# -*- coding: utf-8 -*-
"""
民日穷举验证
============
典据《协纪辨方书》卷五·义例三「王官守相民日」条：
  《历例》曰：「王日者春寅夏巳秋申冬亥，官日者春卯夏午秋酉冬子，
  相日者春巳夏申秋亥冬寅，**民日者春午夏酉秋子冬卯**，守日者春酉夏子
  秋卯冬午。」
  曹震圭曰（原注）：「民日者四时死绝之辰，庶民之象。」
  《协纪》按语：「夫春旺木而生火则午为正令，夏旺土而生金则酉为正令，
  相宜以午酉子卯，而以午酉子卯为民日……故为民也。」
即寅卯辰月午、巳午未月酉、申酉戌月子、亥子丑月卯（四季表），月神查**日支**。

双保险：
1. 权威真值表硬编码（月建→日支），绝不从软件读取；
2. 月支/日支由 sxtwl 独立精确节气推导（与 verify_fusheng 同构），
   产品侧只调 _is_minri 谓词。
另含：3 年 1095 天穷举、端到端 checker 单条目+分值锁（+8）、
旧「全季丑辰未戌」错值域日必须不命中、12 个黄金日干支硬锁。
旧实现取 day_zhi ∈ {丑,辰,未,戌}（四季同表、不看月支，属值域错，不是
季节归并错）：2025-2026 共 730 天误命中 243（每年约 121 天假吉），
典载正格 60 天全部漏命中，新旧**零交集**。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，《协纪》卷五，查日支） =====
MINRI_CLASSICAL = {
    '寅': '午', '卯': '午', '辰': '午',      # 春（寅卯辰月）午
    '巳': '酉', '午': '酉', '未': '酉',      # 夏（巳午未月）酉
    '申': '子', '酉': '子', '戌': '子',      # 秋（申酉戌月）子
    '亥': '卯', '子': '卯', '丑': '卯',      # 冬（亥子丑月）卯
}

GOLDEN = [
    (datetime.date(2026, 1, 5),   '己卯'),   # 子月 卯日
    (datetime.date(2026, 1, 17),  '辛卯'),   # 丑月 卯日
    (datetime.date(2026, 2, 13),  '戊午'),   # 寅月 午日
    (datetime.date(2026, 3, 9),   '壬午'),   # 卯月 午日
    (datetime.date(2026, 4, 14),  '戊午'),   # 辰月 午日
    (datetime.date(2026, 5, 11),  '乙酉'),   # 巳月 酉日
    (datetime.date(2026, 6, 16),  '辛酉'),   # 午月 酉日
    (datetime.date(2026, 7, 10),  '乙酉'),   # 未月 酉日
    (datetime.date(2026, 8, 18),  '甲子'),   # 申月 子日
    (datetime.date(2026, 9, 11),  '戊子'),   # 酉月 子日
    (datetime.date(2026, 10, 17), '甲子'),   # 戌月 子日
    (datetime.date(2026, 11, 13), '辛卯'),   # 亥月 卯日
]

# 旧错值域日（日支∈{丑,辰,未,戌}）：旧命中、典载不命中（新旧零交集）
OLD_TABLE_FALSE_POS = [
    datetime.date(2025, 1, 2),    # 子月 辛未日：旧值域命中，典载子月在卯
    datetime.date(2025, 1, 5),    # 子月 甲戌日：同上
    datetime.date(2025, 1, 8),    # 子月 丁丑日：同上
]
# 典载正格日（新命中、旧值域外全漏）；刻意避开 GOLDEN 内日期，避免与干支硬锁重叠
OLD_TABLE_FALSE_NEG = [
    datetime.date(2026, 5, 23),   # 巳月 丁酉日：典载在酉，旧值域{丑辰未戌}外漏判
    datetime.date(2026, 8, 30),   # 申月 丙子日：典载在子，旧值域外漏判
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
    return _month_zhi_at(d), ZHI[o.getDayGZ().dz]


def _all_days(*years):
    for y in years:
        d = datetime.date(y, 1, 1)
        end = datetime.date(y, 12, 31)
        while d <= end:
            yield d
            d += datetime.timedelta(days=1)


DAYS = list(_all_days(2025, 2026, 2027))

# 加载即断言：四季表结构（连续三月同支、四季四仲循环）== 硬编码表；
# 旧值域表与新表零交集。
_SEASON_GROUPS = (('寅', '卯', '辰'), ('巳', '午', '未'), ('申', '酉', '戌'), ('亥', '子', '丑'))
assert all(len({MINRI_CLASSICAL[m] for m in g}) == 1 for g in _SEASON_GROUPS)
assert {MINRI_CLASSICAL[m] for m in ('寅', '巳', '申', '亥')} == {'午', '酉', '子', '卯'}
assert len(MINRI_CLASSICAL) == 12
_OLD_ZHI = {'丑', '辰', '未', '戌'}
assert not _OLD_ZHI & set(MINRI_CLASSICAL.values())      # 新旧零交集


def expected_pred(d):
    mz, dz = _branch(d)
    return dz == MINRI_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dz = _branch(d)
    try:
        return ShenShaChecker()._is_minri({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dz = _branch(d)
    return 8 if dz == MINRI_CLASSICAL.get(mz) else None


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
                 if x.get('name') == '民日']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == 8:
            return 8
        return f'BAD:{items}'
    except Exception:
        return _UNAVAILABLE


def expected_golden(d):
    gz = next((gz for gd, gz in GOLDEN if gd == d), None)
    if gz is not None:
        return gz                       # GOLDEN 优先：日柱干支硬锁
    if d in OLD_TABLE_FALSE_POS:
        return False
    if d in OLD_TABLE_FALSE_NEG:
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
        hit = ShenShaChecker()._is_minri(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='民日-谓词穷举', category='A',
    description='月神日支，《协纪》卷五"民日者春午夏酉秋子冬卯"，2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='民日-端到端分值', category='A',
    description='修造checker 2026全年：命中唯一一条且+8，未命中无条目',
    inputs=[d for d in DAYS if d.year == 2026],
    expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='民日-黄金日硬锁', category='A',
    description='12个黄金日日柱干支硬锁 + 旧丑辰未戌值域误命中日必须不命中 + 典载正格日必须命中',
    inputs=sorted({gd for gd, _ in GOLDEN} | set(OLD_TABLE_FALSE_POS)
                  | set(OLD_TABLE_FALSE_NEG)),
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_single_entry_all_checkers():
    """全 checker 回归：各事项 2026 全年恰好单条 +8。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha.通用神煞 import CommonShenShaChecker
    from modules.shensha.修造神煞 import ConstructionShenShaChecker
    from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
    from modules.shensha.开业神煞 import OpeningShenShaChecker
    from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
    from modules.shensha.安葬神煞 import BurialShenShaChecker
    days = [d for d in DAYS if d.year == 2026]
    for cls in (CommonShenShaChecker, ConstructionShenShaChecker,
                RuZhaiShenShaChecker, OpeningShenShaChecker,
                MarriageShenShaChecker, BurialShenShaChecker):
        c = cls()
        cnt = 0
        for d in days:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            hits = [x for x in c.check(sz, owners=[]) if x.get('name') == '民日']
            if hits:
                cnt += 1
                assert len(hits) == 1 and hits[0]['score'] == 8, \
                    f'{cls.__name__} {d} 民日条目异常 {hits}'
        assert cnt == 30, f'{cls.__name__} 民日命中 {cnt} 天，期望 30'
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
