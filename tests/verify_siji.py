# -*- coding: utf-8 -*-
"""
真四忌穷举验证（A6-5 新建）
============================
典据口径（用户五项拍板①③，docs/待翻书清单.md §七、
docs/协纪辨方书神煞对照表.md）：
  真四忌＝《协纪辨方书》卷五·义例三「四忌 四穷」连条引《历例》
  「春甲子、夏丙子、秋庚子、冬壬子」——日柱干支并论，按节气四季：
  寅卯辰月→甲子、巳午未月→丙子、申酉戌月→庚子、亥子丑月→壬子。

背景：A2 批（§27）将典载「四击」表（《通书》「春戌夏丑秋辰冬未」，
纯日支）误挂在注册名「四忌」下。2025-2027 共 1095 天实测：四击表
93 命中，真四忌 17 命中（6/5/6），**两集交集为 0**，证为两个独立
神煞。A6-5 拍板②选项①：四击改名归宗（注册名「四击」，表不动），
真四忌另立本谓词；③真四忌 -12，典载忌出师兵事/结婚姻/嫁娶/安葬，
本软件无兵事事项，故仅嫁娶/安葬两 checker 注册。

验证结构：
1. 权威四季柱表硬编码 + sxtwl 独立节气月支，1095 天穷举模块谓词与
   基类 self 方法；
2. 2026 年 5 个黄金日日柱硬锁（寅/辰/午/酉/亥月各一）；
3. 反向断言：四季柱表结构；四击反例日（2026-02-05 庚戌）不命中四忌；
   真四忌日不命中四击；1095 天两集交集恒 0；
4. pipeline 端到端：嫁娶/安葬命中日恰 1 条「四忌」-12，其余 12 事项
   任何日均无「四忌」条目（注册范围锁）；
5. 分值锁：嫁娶/安葬显式键 -12；其余事项无四忌键（不注册）。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，不读产品） =====
# 真四忌（《历例》）按【月支→日柱】每季 3 月同一柱
SIJI_JI_PILLAR = {
    '寅': '甲子', '卯': '甲子', '辰': '甲子', '巳': '丙子',
    '午': '丙子', '未': '丙子', '申': '庚子', '酉': '庚子',
    '戌': '庚子', '亥': '壬子', '子': '壬子', '丑': '壬子',
}
# 四击（《通书》「春戌夏丑秋辰冬未」）按【月支→日支】——仅用于交集 0 反向锁
SIJI_ZHI = {
    '寅': '戌', '卯': '戌', '辰': '戌', '巳': '丑',
    '午': '丑', '未': '丑', '申': '辰', '酉': '辰',
    '戌': '辰', '亥': '未', '子': '未', '丑': '未',
}

# 2026 年全部 5 个真四忌黄金日（探针 C:\Temp\siji_ji_probe.py 独立历点核对）
GOLDEN = [
    (datetime.date(2026, 2, 19),  '甲子', '寅'),
    (datetime.date(2026, 4, 20),  '甲子', '辰'),
    (datetime.date(2026, 7, 1),   '丙子', '午'),
    (datetime.date(2026, 9, 23),  '庚子', '酉'),
    (datetime.date(2026, 12, 4),  '壬子', '亥'),
]
# 反例：四击典载日（2026-02-05 庚戌，寅月戌日）必须不命中真四忌
NEG_SIJI = (datetime.date(2026, 2, 5),)

# 真四忌仅注册于 2 事项；其余 12 事项任何日不得出现「四忌」条目
JI_EVENTS = ['嫁娶', '安葬']
OTHER_EVENTS = ['修造', '动土', '拆舍', '入宅', '开业', '出行', '安床',
                '作灶', '移徙', '入学', '求医', '签约']


def _all_days(*years):
    for y in years:
        d = datetime.date(y, 1, 1)
        end = datetime.date(y, 12, 31)
        while d <= end:
            yield d
            d += datetime.timedelta(days=1)


DAYS = list(_all_days(2025, 2026, 2027))


def _month_zhi_at(d, hour=12):
    """独立精确节气月支（与 verify_fuduan 同构）。"""
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


def _day_pillar(d):
    g = sxtwl.fromSolar(d.year, d.month, d.day).getDayGZ()
    return GAN[g.tg] + ZHI[g.dz]


def expected_pred(d):
    return _day_pillar(d) == SIJI_JI_PILLAR[_month_zhi_at(d)]


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import is_siji_ji_by_pillar
    except Exception:
        return _UNAVAILABLE
    try:
        return bool(is_siji_ji_by_pillar(_month_zhi_at(d), _day_pillar(d)))
    except Exception:
        return _UNAVAILABLE


def adapter_self_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
        pillar = _day_pillar(d)
        return bool(ShenShaChecker()._is_siji_ji(
            {'month_zhi': _month_zhi_at(d),
             'day_gan': pillar[0], 'day_zhi': pillar[1]}))
    except Exception:
        return _UNAVAILABLE


def expected_golden(d):
    return next((gz for gd, gz, _ in GOLDEN if gd == d), None)


def adapter_golden(d):
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.shensha.神煞基类 import ShenShaChecker
        sz = calculate_sizhu(d, 12, 0)
        hit = ShenShaChecker()._is_siji_ji(sz)
        return sz['日柱'] if hit else False
    except Exception:
        return _UNAVAILABLE


def adapter_pipeline(d):
    """嫁娶/安葬命中日恰 1 条「四忌」-12；其余 12 事项永无「四忌」条目。"""
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.事项标准 import get_shensha_checker
        sz = calculate_sizhu(d, 12, 0)
        expect_hit = expected_pred(d)
        for ev in JI_EVENTS:
            c = get_shensha_checker(ev)
            c.check(sz)
            rows = [x for x in c.shensha_list
                    if isinstance(x, dict) and x.get('name') == '四忌']
            if expect_hit:
                if len(rows) != 1 or rows[0].get('score') != -12:
                    return False
            elif rows:
                return False
        for ev in OTHER_EVENTS:
            c = get_shensha_checker(ev)
            c.check(sz)
            if any(isinstance(x, dict) and x.get('name') == '四忌'
                   for x in c.shensha_list):
                return False
        return True
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='真四忌-谓词穷举', category='B',
    description='《历例》春甲子夏丙子秋庚子冬壬子（四季柱），'
                '2025-2027共1095天，sxtwl独立节气月支推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_self = ShenShaCase(
    name='真四忌-基类self方法委托', category='B',
    description='ShenShaChecker._is_siji_ji 委托 is_siji_ji_by_pillar，1095天逐日一致',
    inputs=DAYS, expected=expected_pred, adapter=adapter_self_pred, compare='bool')

case_golden = ShenShaCase(
    name='真四忌-2026黄金日硬锁', category='B',
    description='2026 年 5 个真四忌日（寅/辰/午/酉/亥月）日柱干支硬锁',
    inputs=[gd for gd, _, _ in GOLDEN],
    expected=expected_golden, adapter=adapter_golden, compare='eq')

case_pipeline = ShenShaCase(
    name='真四忌-14事项pipeline注册范围锁', category='B',
    description='嫁娶/安葬命中日恰1条「四忌」-12；四击反例日0条；'
                '其余12事项任何日无「四忌」；1095天逐日符合性',
    inputs=DAYS, expected=lambda _d: True, adapter=adapter_pipeline,
    compare='bool')

CASES = [case_pred, case_self, case_golden, case_pipeline]


def _assert_extra():
    """1) 权威表结构：12 月键、四季各 3 月同柱、四干甲丙庚壬配子；
    2) 命中规模冻结：1095 天 17 命中（6/5/6），2026 恰 5；
    3) 与四击两集交集恒 0（1095 天逐日，含反例日双向硬锁）；
    4) 分值锁：嫁娶/安葬显式 -12，其余事项无四忌键；
    5) 黄金日产品 calculate_sizhu 月支/日柱与标注一致。"""
    from modules.shensha.神煞基类 import (
        _SIJI_JI_PILLAR_BY_MONTH, is_siji_ji_by_pillar,
        is_siji_by_zhi, ShenShaChecker)
    # 表结构
    assert set(_SIJI_JI_PILLAR_BY_MONTH.keys()) == set(ZHI)
    for months, pillar in ((('寅', '卯', '辰'), '甲子'),
                           (('巳', '午', '未'), '丙子'),
                           (('申', '酉', '戌'), '庚子'),
                           (('亥', '子', '丑'), '壬子')):
        for m in months:
            assert SIJI_JI_PILLAR[m] == pillar
            assert _SIJI_JI_PILLAR_BY_MONTH[m] == pillar
    # 四柱皆干配子
    assert set(SIJI_JI_PILLAR.values()) == {'甲子', '丙子', '庚子', '壬子'}
    # 命中规模
    totals = {2025: 0, 2026: 0, 2027: 0}
    ji_days, siji_days = set(), set()
    for d in DAYS:
        mz, pillar = _month_zhi_at(d), _day_pillar(d)
        ji = is_siji_ji_by_pillar(mz, pillar)
        sj = is_siji_by_zhi(mz, pillar[1])
        assert ji == expected_pred(d)
        assert ShenShaChecker()._is_siji_ji(
            {'month_zhi': mz, 'day_gan': pillar[0], 'day_zhi': pillar[1]}) == ji
        if ji:
            totals[d.year] += 1
            ji_days.add(d)
        if sj:
            siji_days.add(d)
    assert totals == {2025: 6, 2026: 5, 2027: 6}, totals
    assert len(ji_days) == 17, len(ji_days)
    assert len(siji_days) == 93, len(siji_days)
    # 交集恒 0
    assert ji_days & siji_days == set(), ji_days & siji_days
    # 反例日双向硬锁
    for d in NEG_SIJI:
        mz, pillar = _month_zhi_at(d), _day_pillar(d)
        assert not is_siji_ji_by_pillar(mz, pillar), d
        assert is_siji_by_zhi(mz, pillar[1]), d
    # 黄金日均命中且产品四柱月支/日柱一致
    from modules.四柱计算器 import calculate_sizhu
    for gd, gz, mz in GOLDEN:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz and sz['月柱'][1] == mz, (gd, sz['日柱'], sz['月柱'])
        assert is_siji_ji_by_pillar(sz['月柱'][1], sz['日柱'])
        assert not is_siji_by_zhi(sz['月柱'][1], sz['日柱'][1])
    # 分值锁
    from modules.事项标准 import shensha_score
    assert shensha_score('嫁娶', '四忌', None) == -12
    assert shensha_score('安葬', '四忌', None) == -12
    for ev in OTHER_EVENTS:
        assert shensha_score(ev, '四忌', None) is None, ev
    # 四击分值仍为 -12（归宗不变值），且四忌/四击在表中各自独立
    assert shensha_score('修造', '四击', None) == -12


if __name__ == '__main__':
    try:
        _assert_extra()
    except AssertionError as e:
        print(f'❌ 反向断言失败: {e}')
        sys.exit(1)
    sys.exit(run_cli(CASES))
