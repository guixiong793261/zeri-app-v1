# -*- coding: utf-8 -*-
"""
八专穷举验证（I1 第一批 2026-10 新建，D 引擎接入配套）
======================================================
典据：《协纪辨方书》卷十嫁娶所忌明列八专；查法采《历例》B5 版 5 柱——
丁未、己未、庚申、甲寅、癸丑（A3 批拍板，废弃《协纪》A8 版 8 柱，
口径分歧留档 001）。八专只论日柱、不随月建；60 甲子轮中固定 5 柱，
每年（公历岁，干支日连续）约 30 命中。

与阳错/厌对不同：八专非嫁娶专属。SHENSHA_SCORES 中
('嫁娶','八专') 为 -12（轻重层批次1 001 §158 由 -15 调档；月家P1 后
通配与其余事项键已删）；checker 侧由嫁娶子类自注册
（嫁娶神煞.py，发射字面量经键表覆写 -12），
本批不动 checker；D（婚嫁评分算法）此前无八专分支，本批接入。

入口（verify_shangshuo/verify_yangcuo 同构）：
① 神煞基类.is_bazhuan_by_pillar —— 全项目唯一实现（模块级，A3 批已建）
② ShenShaChecker._is_bazhuan —— 委托①
③ 婚嫁评分算法.is_bazhuan —— 委托①（本批新增）
④ score_marriage_day details 端到端（-12，批次1 调档）

验证：
- 权威 5 柱硬编码，绝不从软件读取；日柱由 sxtwl 直取；
- 2025-2027 共 1095 天穷举（每年恰 30 命中，5 柱各 18 次）；
- 2026 全年 30 个命中日+日柱硬锁；
- 分值现状锁：嫁娶键 -12（批次1 调档；通配/其余事项键已删）；
- monkeypatch 反事实：关闭分支后命中日总分差精确符合 -12 经 max(0)
  截断理论公式，非命中日零变化；
- 嫁娶 checker pipeline 黄金日恰一条八专 -12（verify_a3 全年断言的
  单点复核）。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# ===== 权威真值（硬编码，《历例》B5 版，A3 批拍板） =====
BAZHUAN_CLASSICAL = frozenset(('丁未', '己未', '庚申', '甲寅', '癸丑'))

# ===== 2026 全年 30 个八专日（sxtwl 独立推导探针，日柱硬锁） =====
GOLDEN_2026 = [
    (datetime.date(2026, 2, 2),  '丁未'), (datetime.date(2026, 2, 8),  '癸丑'),
    (datetime.date(2026, 2, 9),  '甲寅'), (datetime.date(2026, 2, 14), '己未'),
    (datetime.date(2026, 2, 15), '庚申'), (datetime.date(2026, 4, 3),  '丁未'),
    (datetime.date(2026, 4, 9),  '癸丑'), (datetime.date(2026, 4, 10), '甲寅'),
    (datetime.date(2026, 4, 15), '己未'), (datetime.date(2026, 4, 16), '庚申'),
    (datetime.date(2026, 6, 2),  '丁未'), (datetime.date(2026, 6, 8),  '癸丑'),
    (datetime.date(2026, 6, 9),  '甲寅'), (datetime.date(2026, 6, 14), '己未'),
    (datetime.date(2026, 6, 15), '庚申'), (datetime.date(2026, 8, 1),  '丁未'),
    (datetime.date(2026, 8, 7),  '癸丑'), (datetime.date(2026, 8, 8),  '甲寅'),
    (datetime.date(2026, 8, 13), '己未'), (datetime.date(2026, 8, 14), '庚申'),
    (datetime.date(2026, 9, 30), '丁未'), (datetime.date(2026, 10, 6), '癸丑'),
    (datetime.date(2026, 10, 7), '甲寅'), (datetime.date(2026, 10, 12), '己未'),
    (datetime.date(2026, 10, 13), '庚申'), (datetime.date(2026, 11, 29), '丁未'),
    (datetime.date(2026, 12, 5), '癸丑'), (datetime.date(2026, 12, 6), '甲寅'),
    (datetime.date(2026, 12, 11), '己未'), (datetime.date(2026, 12, 12), '庚申'),
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
    return _day_ganzhi(d) in BAZHUAN_CLASSICAL


# ===== 入口①：模块级唯一实现 =====
from modules.shensha.神煞基类 import is_bazhuan_by_pillar, ShenShaChecker


def adapter_func(d):
    try:
        return is_bazhuan_by_pillar(_day_ganzhi(d))
    except Exception:
        return _UNAVAILABLE


# ===== 入口②：基类方法 =====
def adapter_method(d):
    try:
        gz = _day_ganzhi(d)
        return ShenShaChecker()._is_bazhuan(
            {'day_gan': gz[0], 'day_zhi': gz[1]})
    except Exception:
        return _UNAVAILABLE


# ===== 入口③：D 引擎委托 =====
from modules.婚嫁评分算法 import is_bazhuan as _d_is_bazhuan
from modules.四柱计算器 import calculate_sizhu as _calc_sizhu


def adapter_d_pred(d):
    try:
        sz = _calc_sizhu(d, 12, 0)
        return bool(_d_is_bazhuan(d, sz))
    except Exception:
        return _UNAVAILABLE


# ===== 入口④：score_marriage_day details =====
from modules.婚嫁评分算法 import score_marriage_day


def adapter_d_details(d):
    try:
        r = score_marriage_day(d)
        return [x for x in r.get('details', []) if x[0] == '八专'] == [('八专', -12)]
    except Exception:
        return _UNAVAILABLE


def expected_score(d):
    return -12


def adapter_score(d):
    try:
        from modules.事项标准 import shensha_score
        return shensha_score('嫁娶', '八专', None)
    except Exception:
        return _UNAVAILABLE


def expected_golden(d):
    return next((gz for gd, gz in GOLDEN_2026 if gd == d), None)


def adapter_golden(d):
    try:
        sz = _calc_sizhu(d, 12, 0)
        hit = ShenShaChecker()._is_bazhuan(sz)
        if d in dict(GOLDEN_2026):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


CASES = [
    ShenShaCase(name='八专-模块谓词穷举', category='A',
                description='《历例》B5 五柱（丁未己未庚申甲寅癸丑），'
                            '2025-2027共1095天，sxtwl 直取日柱',
                inputs=DAYS, expected=expected_pred, adapter=adapter_func,
                compare='bool'),
    ShenShaCase(name='八专-基类方法委托', category='A',
                description='_is_bazhuan 委托模块谓词，命中集逐日一致',
                inputs=DAYS, expected=expected_pred, adapter=adapter_method,
                compare='bool'),
    ShenShaCase(name='八专-分值锁(嫁娶-12)', category='A',
                description="shensha_score('嫁娶','八专')==-12（批次1 001 §158 调档）",
                inputs=[datetime.date(2026, 2, 9)], expected=expected_score,
                adapter=adapter_score, compare='eq'),
    ShenShaCase(name='八专-黄金日硬锁(2026三十天)', category='A',
                description='2026 全年 30 个八专日+日柱硬锁（每柱 6 次）',
                inputs=[gd for gd, _ in GOLDEN_2026],
                expected=expected_golden, adapter=adapter_golden,
                compare='eq'),
    ShenShaCase(name='八专-D引擎委托一致性', category='A',
                description='婚嫁评分算法.is_bazhuan 委托模块谓词，'
                            '1095 天逐日一致',
                inputs=DAYS, expected=expected_pred, adapter=adapter_d_pred,
                compare='bool'),
    ShenShaCase(name='八专-D端到端details(-12)', category='A',
                description='命中日 details 恰含(八专,-12)，非命中日不含；'
                            '1095 天穷举',
                inputs=DAYS, expected=expected_pred, adapter=adapter_d_details,
                compare='bool'),
]


def _assert_extra():
    """1) 计数锁：每年恰 30 命中、三年每柱各 18 次；
    2) 分值现状锁：八专嫁娶专属化——仅嫁娶键 -12（2026-10-18 月家P1：
       协纪仅忌军事+嫁娶，9 事项键+通配已删；docs/月家P1_大煞八专四击_对勘.md；
       轻重层批次1 001 §158 由 -15 调档）；
    3) D 反事实：关闭分支后命中日总分差精确符合 -12 经 max(0) 截断
       理论公式，非命中日零变化；
    4) 嫁娶 checker 黄金日恰一条八专 -12。"""
    import collections
    by_year = {y: 0 for y in (2025, 2026, 2027)}
    pillar_count = collections.Counter()
    for d in DAYS:
        if expected_pred(d):
            by_year[d.year] += 1
            pillar_count[_day_ganzhi(d)] += 1
    assert by_year == {2025: 30, 2026: 30, 2027: 30}, f'年度计数异常: {by_year}'
    assert dict(pillar_count) == {p: 18 for p in BAZHUAN_CLASSICAL}, \
        f'柱次计数异常: {dict(pillar_count)}'

    from modules.事项标准 import shensha_score
    assert shensha_score('嫁娶', '八专', None) == -12
    # 月家P1 删除后：通配与其余 13 事项均无键（防未来误回填）
    assert shensha_score('*', '八专', None) is None, '通配键应已删除'
    for ev in ('修造', '拆舍', '入宅', '作灶', '移徙', '入学', '求医', '签约'):
        v = shensha_score(ev, '八专', None)
        assert v is None, f'{ev} 八专键应已删除: {v}'
    for ev in ('安葬', '出行', '开业', '动土', '安床'):
        assert shensha_score(ev, '八专', None) is None, \
            f'{ev} 八专键应已删除: {shensha_score(ev, "八专", None)}'

    import modules.婚嫁评分算法 as _H
    _orig = _H.is_bazhuan
    hit_days = [d for d in DAYS if expected_pred(d)]
    miss_sample = DAYS[::47]
    n_delta = 0
    try:
        for d in hit_days:
            r_on = _H.score_marriage_day(d)
            _H.is_bazhuan = lambda date_obj, sizhu: False
            r_off = _H.score_marriage_day(d)
            _H.is_bazhuan = _orig
            delta = r_on['score'] - r_off['score']
            expect_delta = -(max(0, r_off['score']) - max(0, r_off['score'] - 12))
            assert delta == expect_delta, \
                f'{d} 八专总分差 {delta} ≠ 截断公式 {expect_delta}（off={r_off["score"]}）'
            assert -12 <= delta <= 0
            assert not any(x[0] == '八专' for x in r_off['details']), \
                f'{d} 关闭分支后 details 仍含八专'
            if delta == -12:
                n_delta += 1
        for d in miss_sample:
            if expected_pred(d):
                continue
            _H.is_bazhuan = lambda date_obj, sizhu: False
            r_off = _H.score_marriage_day(d)
            _H.is_bazhuan = _orig
            assert r_off['score'] == _H.score_marriage_day(d)['score'], \
                f'{d} 非命中日关闭分支后总分变化'
        assert n_delta >= 1, '至少 1 个命中日应观察到 -12 总分差（未截断）'
    finally:
        _H.is_bazhuan = _orig

    from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
    g = datetime.date(2026, 2, 9)  # 甲寅：八专，且阳错（双凶并挂合法）
    c = MarriageShenShaChecker()
    c._std_event = '嫁娶'
    c.check(_calc_sizhu(g, 12, 0))
    rows = [x for x in c.shensha_list
            if isinstance(x, dict) and x.get('name') == '八专']
    assert [x.get('score') for x in rows] == [-12], \
        f'嫁娶 checker 八专应恰一条 -12: {rows}'


if __name__ == '__main__':
    try:
        _assert_extra()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
