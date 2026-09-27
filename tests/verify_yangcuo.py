# -*- coding: utf-8 -*-
"""
阳错穷举验证
============
典据《协纪辨方书》卷四·义例二引《堪舆经》：「以阳建之支配当方之干，阴阳自相
配合为日，以值所冲之宿为阳错。如正月阳建在寅，近于甲，支干相配为甲寅日，
寅冲于申，故正月甲寅之日月宿在申为阳错。三月阳建在辰，近于甲，得甲辰日。
…唯五月十一月阴阳二建会于子午，故无阴错阳错。」
逐月立成（卷四义例二，《汉语大词典》引《协纪·义例二·阳错》补全）：
寅甲寅、卯乙卯、辰甲辰、巳丁巳己巳、（午无）、未丁未己未、申庚申、
酉辛酉、戌庚戌、亥癸亥、（子无）、丑癸丑。
与《蠡海集》"阴错阳差十二日"（固定干支不随月建）为两个体系，勿混用。

三重验证（verify_zhongri 同构）：
1. 权威真值表硬编码（月建→干支元组），绝不从软件读取；
2. 期望与适配的月支/日干支均由 sxtwl 独立推导，产品侧只调 _is_yangcuo；
   2025-2027 共 1095 天穷举（干支 60 循环 vs 月建约 30 天，部分月建整月
   无表值日属正常，如 2026 卯月无乙卯、巳月无丁巳己巳）；
3. 分值锁：shensha_score('嫁娶','阳错')==-15（嫁娶专属，平行表已在嫁娶
   专项宜忌表引用）；非嫁娶事项不得为 -15（发射分 0 防 fallback）。
另含 12 个黄金日（2025-2027 全部实测阳错日）日柱干支硬锁
（探针 C:\\Temp\\_golden_yangcuo.py 推算，独立推导与软件谓词 3 年全等）。

I1 第一批（2026-10）增补 D 端到端入口：
③ 婚嫁评分算法.is_yangcuo 委托模块级 is_yangcuo_by_pillar（单点出口），
   与基类谓词 1095 天逐日一致；
④ score_marriage_day details 端到端：命中日含 ('阳错',-15) 且追加 warning；
   monkeypatch 反事实（关闭阳错分支）验证总分差精确等于 -15 经 max(0)
   截断后的理论差值（未截断日 -15、截断过渡区 0~-15、零分日 0），
   非命中日总分零变化。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# ===== 权威真值表（硬编码，《协纪》卷四义例二《堪舆经》，月建序） =====
YANGCUO_CLASSICAL = {
    '寅': ('甲寅',), '卯': ('乙卯',), '辰': ('甲辰',),
    '巳': ('丁巳', '己巳'), '未': ('丁未', '己未'),
    '申': ('庚申',), '酉': ('辛酉',), '戌': ('庚戌',),
    '亥': ('癸亥',), '丑': ('癸丑',),
}
NO_YUE = ('午', '子')  # 五月十一月阴阳二建会于子午，故无阴错阳错

# ===== 黄金日（2025-2027 全部实测阳错日+日柱，探针 _golden_yangcuo.py） =====
GOLDEN = [
    (datetime.date(2025, 2, 14), '甲寅'),   # 寅月
    (datetime.date(2025, 4, 5),  '甲辰'),   # 辰月
    (datetime.date(2025, 8, 6),  '丁未'),   # 未月
    (datetime.date(2025, 8, 19), '庚申'),   # 申月
    (datetime.date(2025, 10, 8), '庚戌'),   # 戌月
    (datetime.date(2026, 2, 9),  '甲寅'),   # 寅月
    (datetime.date(2026, 8, 1),  '丁未'),   # 未月
    (datetime.date(2026, 8, 14), '庚申'),   # 申月
    (datetime.date(2027, 2, 3),  '癸丑'),   # 丑月
    (datetime.date(2027, 2, 4),  '甲寅'),   # 寅月
    (datetime.date(2027, 7, 27), '丁未'),   # 未月
    (datetime.date(2027, 8, 9),  '庚申'),   # 申月
]


def _month_zhi_at(d, hour=12):
    """独立精确节气月支（与 verify_shengxin 同构）。"""
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
    mz = _month_zhi_at(d)
    return _day_ganzhi(d) in YANGCUO_CLASSICAL.get(mz, ())


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz = _month_zhi_at(d)
    gz = _day_ganzhi(d)
    try:
        return ShenShaChecker()._is_yangcuo(
            {'month_zhi': mz, 'day_gan': gz[0], 'day_zhi': gz[1]})
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
        return shensha_score('嫁娶', '阳错', None)
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
        hit = ShenShaChecker()._is_yangcuo(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='阳错-谓词穷举', category='A',
    description='月建查干支（《协纪》卷四义例二《堪舆经》逐月立成），'
                '2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_score = ShenShaCase(
    name='阳错-分值锁', category='A',
    description="shensha_score('嫁娶','阳错')==-15；非嫁娶事项不得为 -15"
                "（嫁娶专属，发射分0防fallback）",
    inputs=[datetime.date(2026, 2, 9)], expected=expected_score,
    adapter=adapter_score, compare='eq')

case_golden = ShenShaCase(
    name='阳错-黄金日硬锁', category='A',
    description='12个黄金日（2025-2027全部实测阳错日）日柱干支硬锁',
    inputs=[gd for gd, _ in GOLDEN],
    expected=expected_golden, adapter=adapter_golden, compare='eq')

# ===== 入口③：婚嫁评分算法.is_yangcuo 委托（单点出口一致性） =====
from modules.婚嫁评分算法 import is_yangcuo as _d_is_yangcuo
from modules.四柱计算器 import calculate_sizhu as _calc_sizhu


def adapter_d_pred(d):
    try:
        sz = _calc_sizhu(d, 12, 0)
        sz['month_zhi'] = sz['月柱'][1]
        return bool(_d_is_yangcuo(d, sz))
    except Exception:
        return _UNAVAILABLE


case_d_pred = ShenShaCase(
    name='阳错-D引擎委托一致性', category='A',
    description='婚嫁评分算法.is_yangcuo 委托 is_yangcuo_by_pillar，'
                '2025-2027共1095天与权威月建立成逐日一致',
    inputs=DAYS, expected=expected_pred, adapter=adapter_d_pred, compare='bool')

# ===== 入口④：score_marriage_day details 端到端 =====
from modules.婚嫁评分算法 import score_marriage_day


def adapter_d_details(d):
    try:
        r = score_marriage_day(d)
        return [x for x in r.get('details', []) if x[0] == '阳错'] == [('阳错', -15)]
    except Exception:
        return _UNAVAILABLE


case_d_details = ShenShaCase(
    name='阳错-D端到端details(-15)', category='A',
    description='命中日 score_marriage_day details 恰含(阳错,-15)，'
                '非命中日不含；2025-2027共1095天穷举',
    inputs=DAYS, expected=expected_pred, adapter=adapter_d_details, compare='bool')

CASES = [case_pred, case_score, case_golden, case_d_pred, case_d_details]


def _assert_extra():
    """反向断言：1) 午/子月恒 miss（典载五月十一月无阳错）；
    2) 非嫁娶事项不为 -15（无通配键）；
    3) D 端到端反事实：monkeypatch 关闭阳错分支后，命中日总分差精确等于
       -15 经 max(0) 截断理论差值（未截断日 -15、过渡区 0~-15、零分日 0），
       非命中日零变化，关闭分支后 details 不含阳错。"""
    from modules.shensha.神煞基类 import ShenShaChecker
    c = ShenShaChecker()
    all_gz = [g for tup in YANGCUO_CLASSICAL.values() for g in tup]
    for mz in NO_YUE:
        for gz in all_gz:
            assert not c._is_yangcuo(
                {'month_zhi': mz, 'day_gan': gz[0], 'day_zhi': gz[1]}), \
                f'{mz}月不应有阳错（五月十一月无）：{gz}'
    from modules.事项标准 import shensha_score
    for ev in ('修造', '安葬', '出行', '入学', '开业', '动土', '安床', '移徙'):
        v = shensha_score(ev, '阳错', None)
        assert v != -15, f'{ev} 阳错不应为 -15（嫁娶专属，无通配键）: {v}'

    import modules.婚嫁评分算法 as _H
    _orig = _H.is_yangcuo
    hit_days = [d for d in DAYS if expected_pred(d)]
    miss_sample = DAYS[::47]  # 24 个非命中抽样（含未截断日）
    n_delta = 0
    try:
        for d in hit_days:
            r_on = _H.score_marriage_day(d)
            _H.is_yangcuo = lambda date_obj, sizhu: False
            r_off = _H.score_marriage_day(d)
            _H.is_yangcuo = _orig
            delta = r_on['score'] - r_off['score']
            # D 最终分 max(0, raw)：-15 经截断后精确差值
            # = max(0,off)-max(0,off-15)，取值区间 [0,15]
            expect_delta = -(max(0, r_off['score']) - max(0, r_off['score'] - 15))
            assert delta == expect_delta, \
                f'{d} 阳错总分差 {delta} ≠ 截断公式 {expect_delta}（off={r_off["score"]}）'
            assert -15 <= delta <= 0
            assert not any(x[0] == '阳错' for x in r_off['details']), \
                f'{d} 关闭分支后 details 仍含阳错'
            if delta == -15:
                n_delta += 1
        for d in miss_sample:
            if expected_pred(d):
                continue
            _H.is_yangcuo = lambda date_obj, sizhu: False
            r_off = _H.score_marriage_day(d)
            _H.is_yangcuo = _orig
            assert r_off['score'] == _H.score_marriage_day(d)['score'], \
                f'{d} 非命中日关闭分支后总分变化'
        assert n_delta >= 1, '至少 1 个命中日应观察到 -15 总分差（未截断）'
    finally:
        _H.is_yangcuo = _orig


if __name__ == '__main__':
    try:
        _assert_extra()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
