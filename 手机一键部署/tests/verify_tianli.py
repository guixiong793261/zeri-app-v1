# -*- coding: utf-8 -*-
"""
天吏穷举验证
============
典据《协纪辨方书》卷六·义例四「天吏（致死）」条：
  《历例》曰：「天吏者，正月起酉，逆行四仲。」
  曹震圭曰：「天吏者，三合五行死气之位，五行至此死而无气，乃天之凶吏，
  全无生意也。」
即寅午戌月酉、亥卯未月午、申子辰月卯、巳酉丑月子（月建三合局死气位），
月神查**日支**。

双保险：
1. 权威真值表硬编码（月建→日支），绝不从软件读取；
2. 月支/日支由 sxtwl 独立精确节气推导（与 verify_fusheng 同构），
   产品侧只调 _is_tianli 谓词。
另含：3 年 1095 天穷举、端到端 checker 单条目+分值锁（-15）、
旧四季错表误报/漏报日锚点、12 个黄金日干支硬锁、
**安葬异名「天吏日」死分支清理回归**（私有 override 删除后不得双扣）。
旧实现按四季划月（春午夏酉秋子冬卯，恰为典载「民日」表）：2025-2026
共 730 天误命中 39、漏命中 43；安葬另有私有 override（逆行十二辰错表）
注册异名「天吏日」-15，修复后 10 天会异名双扣。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，《协纪》卷六，查日支） =====
TIANLI_CLASSICAL = {
    '寅': '酉', '午': '酉', '戌': '酉',      # 寅午戌火局死在酉
    '亥': '午', '卯': '午', '未': '午',      # 亥卯未木局死在午
    '申': '卯', '子': '卯', '辰': '卯',      # 申子辰水局死在卯
    '巳': '子', '酉': '子', '丑': '子',      # 巳酉丑金局死在子
}

GOLDEN = [
    (datetime.date(2026, 1, 5),   '己卯'),   # 子月 卯日
    (datetime.date(2026, 1, 14),  '戊子'),   # 丑月 子日
    (datetime.date(2026, 2, 4),   '己酉'),   # 寅月 酉日
    (datetime.date(2026, 3, 9),   '壬午'),   # 卯月 午日
    (datetime.date(2026, 4, 11),  '乙卯'),   # 辰月 卯日
    (datetime.date(2026, 5, 14),  '戊子'),   # 巳月 子日
    (datetime.date(2026, 6, 16),  '辛酉'),   # 午月 酉日
    (datetime.date(2026, 7, 7),   '壬午'),   # 未月 午日
    (datetime.date(2026, 8, 9),   '乙卯'),   # 申月 卯日
    (datetime.date(2026, 9, 11),  '戊子'),   # 酉月 子日
    (datetime.date(2026, 10, 14), '辛酉'),   # 戌月 酉日
    (datetime.date(2026, 11, 16), '甲午'),   # 亥月 午日
]

# 旧四季错表误报日（旧命中、典载不命中）
OLD_TABLE_FALSE_POS = [
    datetime.date(2025, 1, 10),   # 丑月 己卯日：旧"冬在卯"误命中，典载丑月在子
    datetime.date(2025, 2, 6),    # 寅月 丙午日：旧"春在午"误命中，典载寅月在酉
    datetime.date(2025, 2, 18),   # 寅月 戊午日：同上
]
# 旧四季错表漏报日（典载命中、旧不命中）
OLD_TABLE_FALSE_NEG = [
    datetime.date(2025, 1, 7),    # 丑月 丙子日：典载在子，旧"冬在卯"漏
    datetime.date(2025, 2, 9),    # 寅月 己酉日：典载在酉，旧"春在午"漏
]
# 安葬私有 override + 异名"天吏日"修复前，与新天吏同日的双扣风险日（2026）
BURIAL_DOUBLE_RISK_2026 = [datetime.date(2026, 5, 14), datetime.date(2026, 5, 26),
                           datetime.date(2026, 11, 16), datetime.date(2026, 11, 28)]


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

# 加载即断言：三合局死气位独立推导 == 硬编码表；旧四季表 != 新表
# 十二长生顺数（长生→沐浴→冠带→临官→帝旺→衰→病→死）第 8 位为死 = 长生 + 7。
_ZHI_ORDER = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
_DERIVED = {}
for _grp, _cs in (('寅午戌', '寅'), ('亥卯未', '亥'), ('申子辰', '申'), ('巳酉丑', '巳')):
    _dead = _ZHI_ORDER[(_ZHI_ORDER.index(_cs) + 7) % 12]     # 死 = 长生 + 7
    for _m in _grp:
        _DERIVED[_m] = _dead
assert _DERIVED == TIANLI_CLASSICAL, f'死气位推导不符: {_DERIVED}'
assert len(TIANLI_CLASSICAL) == 12
_OLD_SEASON = {'寅': '午', '卯': '午', '辰': '午', '巳': '酉', '午': '酉', '未': '酉',
               '申': '子', '酉': '子', '戌': '子', '亥': '卯', '子': '卯', '丑': '卯'}
assert _OLD_SEASON != TIANLI_CLASSICAL


def expected_pred(d):
    mz, dz = _branch(d)
    return dz == TIANLI_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dz = _branch(d)
    try:
        return ShenShaChecker()._is_tianli({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dz = _branch(d)
    return -15 if dz == TIANLI_CLASSICAL.get(mz) else None


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
                 if x.get('name') == '天吏']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == -15:
            return -15
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
        hit = ShenShaChecker()._is_tianli(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='天吏-谓词穷举', category='A',
    description='月神日支，《协纪》卷六"正月起酉逆行四仲"（三合死气位），2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='天吏-端到端分值', category='A',
    description='修造checker 2026全年：命中唯一一条且-15，未命中无条目',
    inputs=[d for d in DAYS if d.year == 2026],
    expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='天吏-黄金日硬锁', category='A',
    description='12个黄金日日柱干支硬锁 + 旧四季错表误报日必须不命中 + 旧漏报日必须命中',
    inputs=[gd for gd, _ in GOLDEN] + OLD_TABLE_FALSE_POS + OLD_TABLE_FALSE_NEG,
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_no_alias_double_count():
    """安葬异名「天吏日」死分支清理回归。

    修复前：安葬私有 _is_tianli（逆行十二辰错表）注册异名"天吏日"-15，
    与新天吏同日时双扣 -30。修复后：私有 override 与异名注册均删除，
    安葬经基类管线恰 1 条 -15。
    """
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha.安葬神煞 import BurialShenShaChecker
    for d in BURIAL_DOUBLE_RISK_2026:
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        items = [x for x in BurialShenShaChecker().check(sz, owners=[])
                 if x.get('name') in ('天吏', '天吏日')]
        assert len(items) == 1, f'{d} 安葬天吏条目数异常（异名双扣）: {items}'
        assert items[0]['name'] == '天吏', f'{d} 安葬仍注册异名: {items}'
        assert items[0]['score'] == -15, f'{d} 安葬天吏分值异常: {items}'


def _assert_single_entry_all_checkers():
    """全 checker 回归：各事项 2026 全年恰好单条 -15。"""
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
            hits = [x for x in c.check(sz, owners=[]) if x.get('name') == '天吏']
            if hits:
                cnt += 1
                assert len(hits) == 1 and hits[0]['score'] == -15, \
                    f'{cls.__name__} {d} 天吏条目异常 {hits}'
            alias = [x for x in c.check(sz, owners=[]) if x.get('name') == '天吏日']
            assert not alias, f'{cls.__name__} {d} 仍有异名"天吏日": {alias}'
        assert cnt == 33, f'{cls.__name__} 天吏命中 {cnt} 天，期望 33'
    for gd, gz in GOLDEN:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz, f'{gd} 日柱期望{gz} 实际{sz["日柱"]}'


if __name__ == '__main__':
    try:
        _assert_no_alias_double_count()
        _assert_single_entry_all_checkers()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
