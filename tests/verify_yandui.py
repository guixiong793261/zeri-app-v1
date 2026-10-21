# -*- coding: utf-8 -*-
"""
厌对穷举验证
============
典据《协纪辨方书》卷五·义例三引《天宝历》：「厌对者，月厌所冲之辰也，
其日忌嫁娶，又为招摇，忌乘船渡水。」《历例》：「厌对者正月起辰，逆行十二辰。」
逐月（月建序寅→丑）：寅辰、卯卯、辰寅、巳丑、午子、未亥、申戌、酉酉、
戌申、亥未、子午、丑巳。六仪同起例但宜视事临官（卷四按语裁断，不另实现）。

三重验证（verify_yangcuo 同构）：
1. 权威真值表硬编码（月建→日支），绝不从软件读取；
2. 期望与适配的月支/日支均由 sxtwl 独立推导，产品侧只调 _is_yandui；
   2025-2027 共 1095 天穷举；
3. 分值锁：shensha_score('嫁娶','厌对')==-10（嫁娶专属，典载"忌嫁娶"）；
   非嫁娶事项不得为 -10（发射分 0 防 fallback）。
另含 12 个黄金日（2026 各月建首个厌对日）日柱干支硬锁
（探针 C:\\Temp\\_golden_yandui.py 推算，2026 命中 31 天）。

I1 第一批（2026-10）增补 D 端到端入口：
③ 婚嫁评分算法.is_yandui 委托模块级 is_yandui_by_zhi（单点出口），
   与基类谓词 1095 天逐日一致；
④ score_marriage_day details 端到端：命中日含 ('厌对',-10) 且追加
   warning；monkeypatch 反事实（关闭厌对分支）验证总分差精确等于
   -10 经 max(0) 截断后的理论差值，非命中日总分零变化。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# ===== 权威真值表（硬编码，《协纪》卷五义例三《历例》"正月起辰逆行"，月建序） =====
YANDUI_CLASSICAL = {
    '寅': '辰', '卯': '卯', '辰': '寅', '巳': '丑', '午': '子', '未': '亥',
    '申': '戌', '酉': '酉', '戌': '申', '亥': '未', '子': '午', '丑': '巳',
}

# ===== 黄金日（2026 各节气月首个厌对日+日柱，探针 _golden_yandui.py） =====
GOLDEN = [
    (datetime.date(2026, 1, 7),   '辛巳'),   # 丑月
    (datetime.date(2026, 2, 11),  '丙辰'),   # 寅月
    (datetime.date(2026, 3, 6),   '己卯'),   # 卯月
    (datetime.date(2026, 4, 10),  '甲寅'),   # 辰月
    (datetime.date(2026, 5, 15),  '己丑'),   # 巳月
    (datetime.date(2026, 6, 7),   '壬子'),   # 午月
    (datetime.date(2026, 7, 12),  '丁亥'),   # 未月
    (datetime.date(2026, 8, 16),  '壬戌'),   # 申月
    (datetime.date(2026, 9, 8),   '乙酉'),   # 酉月
    (datetime.date(2026, 10, 13), '庚申'),   # 戌月
    (datetime.date(2025, 12, 4),  '丁未'),   # 亥月
    (datetime.date(2025, 12, 15), '戊午'),   # 子月
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
    return _day_ganzhi(d)[1] == YANDUI_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz = _month_zhi_at(d)
    gz = _day_ganzhi(d)
    try:
        return ShenShaChecker()._is_yandui(
            {'month_zhi': mz, 'day_zhi': gz[1]})
    except Exception:
        return _UNAVAILABLE


def expected_score(d):
    return -10


def adapter_score(d):
    try:
        from modules.事项标准 import shensha_score
    except Exception:
        return _UNAVAILABLE
    try:
        return shensha_score('嫁娶', '厌对', None)
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
        hit = ShenShaChecker()._is_yandui(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='厌对-谓词穷举', category='A',
    description='月厌所冲之辰（《协纪》卷五义例三《天宝历》/《历例》'
                '"正月起辰逆行十二辰"），2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_score = ShenShaCase(
    name='厌对-分值锁', category='A',
    description="shensha_score('嫁娶','厌对')==-10；非嫁娶事项不得为 -10"
                "（典载忌嫁娶，嫁娶专属，发射分0防fallback）",
    inputs=[datetime.date(2026, 2, 11)], expected=expected_score,
    adapter=adapter_score, compare='eq')

case_golden = ShenShaCase(
    name='厌对-黄金日硬锁', category='A',
    description='12个黄金日（2026各月建首个厌对日）日柱干支硬锁',
    inputs=[gd for gd, _ in GOLDEN],
    expected=expected_golden, adapter=adapter_golden, compare='eq')

# ===== 入口③：婚嫁评分算法.is_yandui 委托（单点出口一致性） =====
from modules.婚嫁评分算法 import is_yandui as _d_is_yandui
from modules.四柱计算器 import calculate_sizhu as _calc_sizhu


def adapter_d_pred(d):
    try:
        sz = _calc_sizhu(d, 12, 0)
        sz['month_zhi'] = sz['月柱'][1]
        sz['day_zhi'] = sz['日柱'][1]
        return bool(_d_is_yandui(d, sz))
    except Exception:
        return _UNAVAILABLE


case_d_pred = ShenShaCase(
    name='厌对-D引擎委托一致性', category='A',
    description='婚嫁评分算法.is_yandui 委托 is_yandui_by_zhi，'
                '2025-2027共1095天与权威月厌所冲表逐日一致',
    inputs=DAYS, expected=expected_pred, adapter=adapter_d_pred, compare='bool')

# ===== 入口④：score_marriage_day details 端到端 =====
from modules.婚嫁评分算法 import score_marriage_day
from modules.shensha.制化引擎 import eval_yandui_exempt
from modules.四柱计算器 import calculate_sizhu


def adapter_d_details(d):
    try:
        r = score_marriage_day(d)
        items = [x for x in r.get('details', [])
                 if x[0] in ('厌对', '厌对·制化豁免')]
        # 2026-10-21 制化第一批（001 §155，矩阵#13）：五德并日豁免——details
        # 记 ('厌对·制化豁免', 0)；非豁免日仍恰含 ('厌对', -10)。
        sz = calculate_sizhu(d, 12, 0)
        if eval_yandui_exempt(sz)[0]:
            return items == [('厌对·制化豁免', 0)]
        return items == [('厌对', -10)]
    except Exception:
        return _UNAVAILABLE


case_d_details = ShenShaCase(
    name='厌对-D端到端details(-10/豁免)', category='A',
    description='命中日 score_marriage_day details 恰含(厌对,-10)，'
                '五德并豁免日恰含(厌对·制化豁免,0)（制化第一批 001 §155）；'
                '2025-2027共1095天穷举',
    inputs=DAYS, expected=expected_pred, adapter=adapter_d_details, compare='bool')

CASES = [case_pred, case_score, case_golden, case_d_pred, case_d_details]


def _assert_extra():
    """反向断言：1) 月厌本位月支不命中（对冲自检：卯月厌对=卯，月厌=酉，
    逐一验证表值为月厌之冲）；2) 非嫁娶事项不为 -10（无通配键）；
    3) D 端到端反事实：monkeypatch 关闭厌对分支后，命中日总分差精确等于
       -10 经 max(0) 截断理论差值，非命中日零变化，关闭分支后 details
       不含厌对。"""
    # 月厌逐月表（月建序）：正月起戌逆行十二辰——寅戌、卯酉、辰申、巳未、
    # 午午、未巳、申辰、酉卯、戌寅、亥丑、子子、丑亥——厌对表值应=月厌六冲
    YUE_YAN = {
        '寅': '戌', '卯': '酉', '辰': '申', '巳': '未', '午': '午',
        '未': '巳', '申': '辰', '酉': '卯', '戌': '寅', '亥': '丑',
        '子': '子', '丑': '亥',
    }
    CHONG = {'子': '午', '午': '子', '丑': '未', '未': '丑',
             '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
             '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
    for mz, yandui in YANDUI_CLASSICAL.items():
        assert yandui == CHONG[YUE_YAN[mz]], \
            f'{mz}月厌对{yandui} ≠ 月厌{YUE_YAN[mz]}之冲{CHONG[YUE_YAN[mz]]}'
    from modules.事项标准 import shensha_score
    for ev in ('修造', '安葬', '出行', '入学', '开业', '动土', '安床', '移徙'):
        v = shensha_score(ev, '厌对', None)
        assert v != -10, f'{ev} 厌对不应为 -10（嫁娶专属，无通配键）: {v}'

    import modules.婚嫁评分算法 as _H
    _orig = _H.is_yandui
    hit_days = [d for d in DAYS if expected_pred(d)]
    # 制化第一批（001 §155）：命中日按是否五德并分为豁免/非豁免两组，
    # 分别锚定「关断分支总分差=-10 截断公式」与「豁免日零变化+豁免键」。
    hit_days_ex = [d for d in hit_days
                   if eval_yandui_exempt(calculate_sizhu(d, 12, 0))[0]]
    _ex_set = set(hit_days_ex)
    hit_days_nx = [d for d in hit_days if d not in _ex_set]
    miss_sample = DAYS[::47]
    n_delta = 0
    try:
        for d in hit_days_nx:
            r_on = _H.score_marriage_day(d)
            _H.is_yandui = lambda date_obj, sizhu: False
            r_off = _H.score_marriage_day(d)
            _H.is_yandui = _orig
            delta = r_on['score'] - r_off['score']
            expect_delta = -(max(0, r_off['score']) - max(0, r_off['score'] - 10))
            assert delta == expect_delta, \
                f'{d} 厌对总分差 {delta} ≠ 截断公式 {expect_delta}（off={r_off["score"]}）'
            assert -10 <= delta <= 0
            assert not any(x[0] == '厌对' for x in r_off['details']), \
                f'{d} 关闭分支后 details 仍含厌对'
            if delta == -10:
                n_delta += 1
        for d in hit_days_ex:
            r_on = _H.score_marriage_day(d)
            _H.is_yandui = lambda date_obj, sizhu: False
            r_off = _H.score_marriage_day(d)
            _H.is_yandui = _orig
            assert r_on['score'] == r_off['score'], \
                f'{d} 五德并豁免日关断分支总分应零变化（豁免已免扣）'
            ks = [x[0] for x in r_on['details']]
            assert '厌对·制化豁免' in ks and '厌对' not in ks, \
                f'{d} 豁免日 details 应记豁免键 0 分: {ks}'
        for d in miss_sample:
            if expected_pred(d):
                continue
            _H.is_yandui = lambda date_obj, sizhu: False
            r_off = _H.score_marriage_day(d)
            _H.is_yandui = _orig
            assert r_off['score'] == _H.score_marriage_day(d)['score'], \
                f'{d} 非命中日关闭分支后总分变化'
        assert n_delta >= 1, '至少 1 个命中日应观察到 -10 总分差（未截断）'
    finally:
        _H.is_yandui = _orig


if __name__ == '__main__':
    try:
        _assert_extra()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
