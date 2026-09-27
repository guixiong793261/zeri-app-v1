# -*- coding: utf-8 -*-
"""
重日穷举验证
============
典据《协纪辨方书》卷五·义例三引《天宝历》：「重日者，以阴阳混合于亥，阳起于
甲子而顺，阴起于甲戌而逆，至己亥而同，故曰重日。其日忌为凶事，利为吉事。」
《历例》：「重日者，己亥二日也。」卷十所忌段：复日重日忌破土安葬启攒。

三重验证（verify_shengxin 同构）：
1. 权威真值表硬编码（巳亥命中、十柱反例），绝不从软件读取；
2. 期望与适配的日支均由 sxtwl 独立推导，产品侧只调 _is_zhongri；
   2025-2027 共 1095 天穷举；
3. 分值锁：shensha_score('安葬','重日')==-15（典载忌破土安葬启攒，事项全集
   仅安葬落键）；非安葬事项不得为 -15（典载"利为吉事"，发射分 0 防 fallback）。
另含 12 个黄金日（2026 各节气月首个巳/亥日）日柱硬锁
（探针 C:\\Temp\\_golden_zhongri.py 推算）。
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
HIT_ZHI = ('巳', '亥')
NEG_GZ = {'甲子', '乙丑', '丙寅', '丁卯', '戊戌', '己未', '庚辰', '壬午', '癸酉', '甲申'}

# ===== 黄金日（2026 各节气月首个巳/亥日+日柱，探针 _golden_zhongri.py 推算） =====
GOLDEN = [
    (datetime.date(2026, 1, 7),  '辛巳'),   # 丑月
    (datetime.date(2026, 2, 6),  '辛亥'),   # 寅月
    (datetime.date(2026, 3, 8),  '辛巳'),   # 卯月
    (datetime.date(2026, 4, 7),  '辛亥'),   # 辰月
    (datetime.date(2026, 5, 7),  '辛巳'),   # 巳月
    (datetime.date(2026, 6, 6),  '辛亥'),   # 午月
    (datetime.date(2026, 7, 12), '丁亥'),   # 未月
    (datetime.date(2026, 8, 11), '丁巳'),   # 申月
    (datetime.date(2026, 9, 10), '丁亥'),   # 酉月
    (datetime.date(2026, 10, 10), '丁巳'),  # 戌月
    (datetime.date(2026, 11, 9), '丁亥'),   # 亥月
    (datetime.date(2026, 1, 1),  '乙亥'),   # 子月
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
        return ShenShaChecker()._is_zhongri({'day_zhi': _day_ganzhi(d)[1]})
    except Exception:
        return _UNAVAILABLE


def expected_score(d):
    return -15


def adapter_score(d):
    try:
        from modules.事项标准 import shensha_score
    except Exception:
        return _UNAVAILABLE
    try:
        return shensha_score('安葬', '重日', None)
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
        hit = ShenShaChecker()._is_zhongri(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='重日-谓词穷举', category='A',
    description='日支巳亥命中，《协纪》卷五《历例》"重日者己亥二日也"，'
                '2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_score = ShenShaCase(
    name='重日-分值锁', category='A',
    description="shensha_score('安葬','重日')==-15；非安葬事项不得为 -15"
                "（典载利吉事，发射分0防fallback）",
    inputs=[datetime.date(2026, 2, 6)], expected=expected_score,
    adapter=adapter_score, compare='eq')

case_golden = ShenShaCase(
    name='重日-黄金日硬锁', category='A',
    description='12个黄金日（2026各节气月首个巳/亥日）日柱干支硬锁',
    inputs=[gd for gd, _ in GOLDEN],
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_score, case_golden]


def _assert_extra():
    """反向断言：1) 反例十柱不命中；2) 非安葬事项不为 -15（无通配键）。"""
    from modules.shensha.神煞基类 import ShenShaChecker
    c = ShenShaChecker()
    for gz in NEG_GZ:
        assert not c._is_zhongri({'day_zhi': gz[1]}), f'反例误命中: {gz}'
    from modules.事项标准 import shensha_score
    for ev in ('修造', '嫁娶', '出行', '入学', '开业', '动土'):
        v = shensha_score(ev, '重日', None)
        assert v != -15, f'{ev} 重日不应为 -15（典载利吉事，无通配键）: {v}'


if __name__ == '__main__':
    try:
        _assert_extra()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
