# -*- coding: utf-8 -*-
"""
伏断日穷举验证（A6-3 修复）
===========================
典据口径（用户拍板冻结，docs/待翻书清单.md §一、
docs/协纪辨方书神煞对照表.md）：伏断日＝日支与月支相害（六害）——
子未、丑午、寅巳、卯辰、申亥、酉戌（按月建查日支）。

旧实现三套互异口径（2025-2027 共 1095 天实测）：
  基类/通用：月支冲日支（与月破同表，94 命中全部与月破同格双扣）；
  安葬 override：日干查日支（甲戌/乙酉/丙申/丁未/戊午/己巳/庚辰/辛卯/
    壬寅/癸丑，182 命中的另一套异表）；
  修造/入宅 override：return False 死桩，经 self 分派屏蔽基类注册，
    致修造/动土/拆舍/入宅/移徙 5 事项 0 命中。
2026-10 A6-3 收敛为模块级单点出口 is_fuduan_by_zhi（关系层 is_liuhai_by_zhi，
与月害 _is_yuehai 同表同源），五份实现全部删除/委托。

验证结构：
1. 权威六害表硬编码 + sxtwl 独立节气月支，1095 天穷举谓词；
2. 基类 self 方法委托一致性；
3. 分值锁（口径收口批 2026-10-21，001 §153 反转）：注册键 9 项已删，
   shensha_score 各事项返回 None（无键）；
4. 12 个黄金日（2026 各节气月首个伏断日）日柱硬锁（谓词层保留：
   伏断本选时之法，A6-3 三派收敛的 is_fuduan_by_zhi 留作选时层唯一出口）；
5. pipeline 端到端（口径收口批反转）：14 事项 checker 全年 0 条「伏断日」
   （日家用忌零载：协纪卷十无条目、卷十一 0 命中、卷三十六辨讹明定，
   docs/下半场第一批_八项三库取证_20261021.md §1.4）；
6. 单点出口锁：各 checker 类自身 __dict__ 不再携带 _is_fuduan override；
7. 反向断言：六害关系表与典载口诀逐字一致；月害与伏断 1095 天同集
   （谓词层关系不变）；9 个原注册键删除后分值返回 None。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# ===== 权威真值表（硬编码六害；月支/日支双向对称） =====
LIUHAI = {
    '子': '未', '未': '子', '丑': '午', '午': '丑', '寅': '巳', '巳': '寅',
    '卯': '辰', '辰': '卯', '申': '亥', '亥': '申', '酉': '戌', '戌': '酉',
}

# ===== 黄金日（2026 各节气月首个伏断日；探针 C:\\Temp\\_golden_fuduan.py） =====
GOLDEN = [
    (datetime.date(2026, 2, 12),  '丁巳', '寅'),
    (datetime.date(2026, 3, 7),   '庚辰', '卯'),
    (datetime.date(2026, 4, 11),  '乙卯', '辰'),
    (datetime.date(2026, 5, 16),  '庚寅', '巳'),
    (datetime.date(2026, 6, 8),   '癸丑', '午'),
    (datetime.date(2026, 7, 13),  '戊子', '未'),
    (datetime.date(2026, 8, 17),  '癸亥', '申'),
    (datetime.date(2026, 9, 9),   '丙戌', '酉'),
    (datetime.date(2026, 10, 14), '辛酉', '戌'),
    (datetime.date(2026, 11, 18), '丙申', '亥'),
    (datetime.date(2026, 12, 11), '己未', '子'),
    (datetime.date(2026, 1, 8),   '壬午', '丑'),
]

# 旧错表反例：冲日非害（旧基类/通用误判）、干表日非害（旧安葬误判）
NEG_CHONG = (datetime.date(2026, 1, 9),)    # 癸未日 丑月：丑未冲，非六害
NEG_GAN = (datetime.date(2026, 1, 6),)      # 庚辰日 丑月：旧安葬干表（庚→辰），非六害

EVENTS = ['嫁娶', '修造', '动土', '拆舍', '入宅', '开业', '出行', '安床',
          '作灶', '移徙', '入学', '求医', '签约', '安葬']


def _month_zhi_at(d, hour=12):
    """独立精确节气月支（与 verify_yandui 同构）。"""
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
    return _day_ganzhi(d)[1] == LIUHAI.get(_month_zhi_at(d))


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import is_fuduan_by_zhi
    except Exception:
        return _UNAVAILABLE
    gz = _day_ganzhi(d)
    try:
        return bool(is_fuduan_by_zhi(_month_zhi_at(d), gz[1]))
    except Exception:
        return _UNAVAILABLE


def adapter_self_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
        return bool(ShenShaChecker()._is_fuduan(
            {'month_zhi': _month_zhi_at(d), 'day_zhi': _day_ganzhi(d)[1]}))
    except Exception:
        return _UNAVAILABLE


def expected_score(_d):
    # 口径收口批（001 §153）：注册键已删，shensha_score 返回 None（无键）。
    return True


def adapter_score(_d):
    try:
        from modules.事项标准 import shensha_score
    except Exception:
        return _UNAVAILABLE
    vals = [shensha_score(ev, '伏断日', None)
            for ev in ('嫁娶', '开业', '出行', '安床', '作灶', '入学',
                       '求医', '签约', '安葬')]
    return all(v is None for v in vals)


def expected_golden(d):
    return next((gz for gd, gz, _ in GOLDEN if gd == d), None)


def adapter_golden(d):
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.shensha.神煞基类 import ShenShaChecker
        sz = calculate_sizhu(d, 12, 0)
        hit = ShenShaChecker()._is_fuduan(sz)
        if d in {gd for gd, _, _ in GOLDEN}:
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


def adapter_pipeline(d):
    """口径收口批反转：14 事项 checker 全年 0 条「伏断日」（日家用忌零载）。"""
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.事项标准 import get_shensha_checker
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        for ev in EVENTS:
            c = get_shensha_checker(ev)
            c.check(sz)
            rows = [x for x in c.shensha_list
                    if isinstance(x, dict) and x.get('name') == '伏断日']
            if rows:
                return False
        return True
    except Exception:
        return _UNAVAILABLE


def adapter_single_source(_d):
    """各 checker 类不得自带 _is_fuduan override（单点出口锁）。"""
    try:
        from modules.shensha import (
            神煞基类 as _base, 通用神煞 as _ty, 修造神煞 as _xz,
            入宅神煞 as _rz, 动土神煞 as _dt, 安葬神煞 as _az,
            拆舍神煞 as _cs, 嫁娶神煞 as _jq, 出行神煞 as _cx,
            开业神煞 as _ky, 安床神煞 as _ac, 作灶神煞 as _zz)
        classes = [_ty.CommonShenShaChecker, _xz.ConstructionShenShaChecker,
                   _rz.RuZhaiShenShaChecker, _dt.DiggingShenShaChecker,
                   _az.BurialShenShaChecker, _cs.DemolitionShenShaChecker,
                   _jq.MarriageShenShaChecker, _cx.TravelShenShaChecker,
                   _ky.OpeningShenShaChecker, _ac.BedShenShaChecker,
                   _zz.StoveShenShaChecker]
        for cls in classes:
            if '_is_fuduan' in cls.__dict__:
                return False
        # 基类必须持有且委托模块函数
        assert callable(_base.is_fuduan_by_zhi)
        return True
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='伏断-谓词穷举', category='B',
    description='月支相害日支（六害：子未丑午寅巳卯辰申亥酉戌），'
                '2025-2027共1095天，sxtwl独立节气月支推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_self = ShenShaCase(
    name='伏断-基类self方法委托', category='B',
    description='ShenShaChecker._is_fuduan 委托 is_fuduan_by_zhi，1095天逐日一致',
    inputs=DAYS, expected=expected_pred, adapter=adapter_self_pred, compare='bool')

case_score = ShenShaCase(
    name='伏断-分值锁', category='B',
    description="口径收口批反转：9 个原注册键已删，shensha_score(ev,'伏断日') 均 None",
    inputs=[datetime.date(2026, 2, 12)], expected=expected_score,
    adapter=adapter_score, compare='eq')

case_golden = ShenShaCase(
    name='伏断-黄金日硬锁', category='B',
    description='12个黄金日（2026各节气月首个伏断日）日柱干支硬锁',
    inputs=[gd for gd, _, _ in GOLDEN],
    expected=expected_golden, adapter=adapter_golden, compare='eq')

case_pipeline = ShenShaCase(
    name='伏断-14事项pipeline删除锁', category='B',
    description='口径收口批反转：14 checker 2025-2027 全期 0 条「伏断日」'
                '（日家用忌零载，取证稿 §1.4；谓词层黄金日锁另行保留）',
    inputs=DAYS, expected=lambda _d: True, adapter=adapter_pipeline,
    compare='bool')

case_single = ShenShaCase(
    name='伏断-单点出口锁', category='B',
    description='11个事项 checker 类自身 __dict__ 不含 _is_fuduan override',
    inputs=[datetime.date(2026, 2, 12)], expected=lambda _d: True,
    adapter=adapter_single_source, compare='bool')

CASES = [case_pred, case_self, case_score, case_golden, case_pipeline, case_single]


def _assert_extra():
    """1) 六害表与典载口诀逐字一致；
    2) 月害关系层 is_liuhai_by_zhi 与伏断 1095 天同集（谓词层关系不变）；
    3) 口径收口批反转（001 §153）：9 个原注册键删除后 shensha_score 返回
       None（发射已同步删除，不存在「无键兜底」泄漏）；
    4) 旧冲表/旧干表反例日显式不命中（谓词层）。"""
    from modules.shensha.神煞基类 import (
        is_fuduan_by_zhi, is_liuhai_by_zhi, _LIUHAI_PARTNER, ShenShaChecker)
    # 口诀逐字
    assert _LIUHAI_PARTNER == LIUHAI
    for d in DAYS:
        mz, dz = _month_zhi_at(d), _day_ganzhi(d)[1]
        assert is_fuduan_by_zhi(mz, dz) == (dz == LIUHAI[mz])
        assert is_liuhai_by_zhi(mz, dz) == is_fuduan_by_zhi(mz, dz)
        assert ShenShaChecker()._is_yuehai(
            {'month_zhi': mz, 'day_zhi': dz}) == is_liuhai_by_zhi(mz, dz)
    # 分值（反转：键已删 → None）
    from modules.事项标准 import shensha_score
    for ev in ('嫁娶', '开业', '出行', '安床', '作灶', '入学', '求医', '签约', '安葬'):
        assert shensha_score(ev, '伏断日', None) is None, ev
    # 反例
    for d in NEG_CHONG + NEG_GAN:
        assert not expected_pred(d), d
        assert not is_fuduan_by_zhi(_month_zhi_at(d), _day_ganzhi(d)[1]), d
    # 黄金日全部命中且月柱月支与标注一致（谓词层保留证据）
    from modules.四柱计算器 import calculate_sizhu
    for gd, gz, mz in GOLDEN:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz and sz['月柱'][1] == mz, (gd, sz['日柱'], sz['月柱'])
        assert is_fuduan_by_zhi(sz['月柱'][1], sz['日柱'][1])


if __name__ == '__main__':
    try:
        _assert_extra()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
