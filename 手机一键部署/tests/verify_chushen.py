# -*- coding: utf-8 -*-
"""
除神穷举验证
============
典据《协纪辨方书》卷五·义例三「五离」条下考原按语：「按通书以申酉日为除神，
与五合对冲之日也，宜沐浴祓除灾眚。」（《历例》「五离者申酉日是也」同条互证）
卷十宜忌：「除神，宜解除沐浴整容剃头整手足甲求医疗病扫舍宇，义同除日。」

三重验证（verify_shengxin 同构）：
1. 权威真值表硬编码（申酉日命中、十柱反例），绝不从软件读取；
2. 期望与适配的日支均由 sxtwl 独立推导，产品侧只调 _is_chushen；
   2025-2027 共 1095 天穷举；
3. 分值锁：shensha_score('求医','除神')==8（典载"求医疗病"）；
   非（通配）事项不为 8——除神非"百事皆宜"，无 '*' 键。
另含 12 个黄金日（2026 各节气月首个申酉日）日柱硬锁
（探针 C:\\Temp\\_golden_chushen.py 推算）。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# ===== 权威真值表（硬编码） =====
HIT_ZHI = ('申', '酉')
# 反例十柱（非申酉）
NEG_GZ = {'甲子', '乙丑', '丙寅', '丁卯', '戊戌', '己未', '庚辰', '辛亥', '壬午', '癸巳'}

# ===== 黄金日（2026 各节气月首个申酉日+日柱，探针 _golden_chushen.py 推算） =====
GOLDEN = [
    (datetime.date(2026, 1, 10), '甲申'),   # 丑月
    (datetime.date(2026, 2, 4),  '己酉'),   # 寅月
    (datetime.date(2026, 3, 11), '甲申'),   # 卯月
    (datetime.date(2026, 4, 5),  '己酉'),   # 辰月
    (datetime.date(2026, 5, 10), '甲申'),   # 巳月
    (datetime.date(2026, 6, 15), '庚申'),   # 午月
    (datetime.date(2026, 7, 9),  '甲申'),   # 未月
    (datetime.date(2026, 8, 14), '庚申'),   # 申月
    (datetime.date(2026, 9, 8),  '乙酉'),   # 酉月
    (datetime.date(2026, 10, 13), '庚申'),  # 戌月
    (datetime.date(2026, 11, 18), '丙申'),  # 亥月
    (datetime.date(2026, 12, 12), '庚申'),  # 子月
]


def _day_ganzhi(d):
    o = sxtwl.fromSolar(d.year, d.month, d.day)
    gz = o.getDayGZ()
    return GAN[gz.tg] + ZHI[gz.dz]


def _all_days(*years):
    for y in years:
        d = datetime.date(y, 1, 1)
        end = datetime.date(y, 12, 31)
        while d <= end:
            yield d
            d += datetime.timedelta(days=1)


DAYS = list(_all_days(2025, 2026, 2027))


def expected_pred(d):
    return _day_ganzhi(d)[1] in HIT_ZHI


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        return ShenShaChecker()._is_chushen({'day_zhi': _day_ganzhi(d)[1]})
    except Exception:
        return _UNAVAILABLE


def expected_score(d):
    return 8


def adapter_score(d):
    try:
        from modules.事项标准 import shensha_score
    except Exception:
        return _UNAVAILABLE
    try:
        return shensha_score('求医', '除神', None)
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
        hit = ShenShaChecker()._is_chushen(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='除神-谓词穷举', category='A',
    description='日支申酉命中，《协纪》卷五考原按语"通书以申酉日为除神"，'
                '2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_score = ShenShaCase(
    name='除神-分值锁', category='A',
    description="shensha_score('求医','除神')==8；非通配事项(修造/嫁娶/安葬)不得为 8",
    inputs=[datetime.date(2026, 8, 14)], expected=expected_score,
    adapter=adapter_score, compare='eq')

case_golden = ShenShaCase(
    name='除神-黄金日硬锁', category='A',
    description='12个黄金日（2026各节气月首个申酉日）日柱干支硬锁',
    inputs=[gd for gd, _ in GOLDEN],
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_score, case_golden]


def _assert_extra():
    """反向断言：1) 反例十柱不命中；2) 无通配键——非求医事项不为 8。"""
    from modules.shensha.神煞基类 import ShenShaChecker
    c = ShenShaChecker()
    for gz in NEG_GZ:
        assert not c._is_chushen({'day_zhi': gz[1]}), f'反例误命中: {gz}'
    from modules.事项标准 import shensha_score
    for ev in ('修造', '嫁娶', '安葬', '出行', '入学'):
        v = shensha_score(ev, '除神', None)
        assert v != 8, f'{ev} 除神不应为 8（无通配键）: {v}'


if __name__ == '__main__':
    try:
        _assert_extra()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
