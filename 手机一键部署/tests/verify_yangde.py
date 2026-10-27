# -*- coding: utf-8 -*-
"""阳德穷举验证（2026-10 A8 修复）
================================
典据《协纪辨方书》卷三·月事吉神 / 《御定星历考原》卷三引《历例》：
  「正月起戌，顺行六阳辰。」
六阳辰=子寅辰午申戌，自戌起顺行：戌→子→寅→辰→午→申（循环），
寅月戌、卯月子、辰月寅、巳月辰、午月午、未月申、申月戌、酉月子、
戌月寅、亥月辰、子月午、丑月申，月神查**日支**。
曹震圭曰："五月一阴生即配于午……六阳月居于寅午戌"——午月午、
寅月戌、戌月寅，三阳月所值恰为火局寅午戌，可互证。

旧实现序列 酉辰亥午卯戌：起点"酉"为阴支，且亥卯皆阴，与"六阳辰"
名义内部矛盾；2026 年穷举新旧命中零交集（旧 32 天 vs 典载 30 天）。

跨实现互证：modules/五行择日法.py 的月家神煞表 L250 阳德列本就是
戌子寅辰午申循环（另一套独立实现长期正确），本验证直接断言两表一致。

结构同 verify_minri/verify_guanri：权威真值表硬编码 + sxtwl 独立
节气推导 + 1095 天谓词穷举 + 端到端单条目分值锁（+10）+ 黄金日干支
硬锁 + 旧表误命中/漏命中反向断言 + 阳德/阴德同月不同支对偶断言。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
LIU_YANG = {'子', '寅', '辰', '午', '申', '戌'}
LIU_YIN = {'丑', '卯', '巳', '未', '酉', '亥'}

# ===== 权威真值表（硬编码，《协纪》卷三，查日支；月建序寅→丑） =====
YANGDE_CLASSICAL = {
    '寅': '戌', '卯': '子', '辰': '寅',
    '巳': '辰', '午': '午', '未': '申',
    '申': '戌', '酉': '子', '戌': '寅',
    '亥': '辰', '子': '午', '丑': '申',
}

# 旧错表（内联，起点酉、含阴支，与六阳辰名义矛盾）
YANGDE_OLD = {
    '寅': '酉', '卯': '辰', '辰': '亥', '巳': '午',
    '午': '卯', '未': '戌', '申': '酉', '酉': '辰',
    '戌': '亥', '亥': '午', '子': '卯', '丑': '戌',
}

# 阴德表（A2 已修，用于对偶断言：正月起酉逆行六阴辰）
YINDE = {
    '寅': '酉', '卯': '未', '辰': '巳', '巳': '卯',
    '午': '丑', '未': '亥', '申': '酉', '酉': '未',
    '戌': '巳', '亥': '卯', '子': '丑', '丑': '亥',
}

# 月建序对应的顺行六阳辰序列（寅月起戌）
_SEQ = ['戌', '子', '寅', '辰', '午', '申']
_MONTH_ORDER = ['寅', '卯', '辰', '巳', '午', '未',
                '申', '酉', '戌', '亥', '子', '丑']


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
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 加载即结构断言
assert len(YANGDE_CLASSICAL) == 12
assert set(YANGDE_CLASSICAL.values()) <= LIU_YANG, '阳德值必须全为六阳辰'
assert not (set(YANGDE_OLD.values()) <= LIU_YANG), '旧表必须含阴支（矛盾实锤）'
# 表 == 顺行六阳辰循环（正月起戌）
assert [YANGDE_CLASSICAL[m] for m in _MONTH_ORDER] == [_SEQ[i % 6] for i in range(12)]
# 午月午（五月配午）、寅月戌、戌月寅（六阳月居寅午戌）
assert YANGDE_CLASSICAL['午'] == '午'
assert {YANGDE_CLASSICAL[m] for m in ('寅', '午', '戌')} == {'寅', '午', '戌'}
# 阳德/阴德同月日支必不同，且阳德全阳、阴德全阴
assert all(YANGDE_CLASSICAL[m] != YINDE[m] for m in _MONTH_ORDER)
assert set(YINDE.values()) <= LIU_YIN
# 新旧零交集月（旧表 12 月值无一与新表相同）
assert all(YANGDE_OLD[m] != YANGDE_CLASSICAL[m] for m in _MONTH_ORDER)

# 跨实现互证：五行择日法.py 月家神煞表的阳德列必须与本表一致
_src = (Path(__file__).resolve().parents[1] / 'modules' / '五行择日法.py').read_text(encoding='utf-8')
_line = next(l for l in _src.splitlines() if l.strip().startswith("'阳德'") and '[' in l)
_nums = _line.split('[', 1)[1].split(']', 1)[0]
_wx_table = [x.strip().strip("'\"") for x in _nums.split(',') if x.strip()]
assert len(_wx_table) == 12 and _wx_table == [_SEQ[i % 6] for i in range(12)], \
    '五行择日法.py 阳德列与权威表不一致: %r' % _wx_table

# 生成 2026 黄金日（每月支取首个典载命中日）+ 旧表误命中/漏命中样例
_picked, _old_fp, _old_fn = {}, [], []
for d in _all_days(2026):
    mz, dz = _branch(d)
    new_hit = dz == YANGDE_CLASSICAL.get(mz)
    old_hit = dz == YANGDE_OLD.get(mz)
    o = sxtwl.fromSolar(d.year, d.month, d.day)
    gz = GAN[o.getDayGZ().tg] + dz
    if new_hit and mz not in _picked:
        _picked[mz] = (d, gz)
    if old_hit and not new_hit and len(_old_fp) < 3:
        _old_fp.append((d, gz, mz))
    if new_hit and not old_hit and len(_old_fn) < 3:
        _old_fn.append((d, gz, mz))
GOLDEN = [(_picked[m][0], _picked[m][1]) for m in _MONTH_ORDER if m in _picked]
OLD_TABLE_FALSE_POS = [x[0] for x in _old_fp]
OLD_TABLE_FALSE_NEG = [x[0] for x in _old_fn]
assert len(GOLDEN) == 12 and _old_fp and _old_fn


def expected_pred(d):
    mz, dz = _branch(d)
    return dz == YANGDE_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    mz, dz = _branch(d)
    try:
        return ShenShaChecker()._is_yangde({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dz = _branch(d)
    return 10 if dz == YANGDE_CLASSICAL.get(mz) else None


def adapter_e2e(d):
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.shensha.通用神煞 import CommonShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        items = [x for x in CommonShenShaChecker().check(sz, owners=[])
                 if x.get('name') == '阳德']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == 10:
            return 10
        return 'BAD:%s' % items
    except Exception:
        return _UNAVAILABLE


def expected_golden(d):
    gz = next((gz for gd, gz in GOLDEN if gd == d), None)
    if gz is not None:
        return gz
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
        hit = ShenShaChecker()._is_yangde(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='阳德-谓词穷举', category='A',
    description='月神日支，《协纪》卷三"正月起戌顺行六阳辰"，2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='阳德-端到端分值', category='A',
    description='通用checker 2026全年：命中唯一一条且+10，未命中无条目',
    inputs=[d for d in DAYS if d.year == 2026],
    expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='阳德-黄金日硬锁', category='A',
    description='12个月支黄金日日柱干支硬锁 + 旧表误命中日必须不命中 + 典载正格日必须命中',
    inputs=sorted({gd for gd, _ in GOLDEN} | set(OLD_TABLE_FALSE_POS)
                  | set(OLD_TABLE_FALSE_NEG)),
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_single_entry_all_checkers():
    """注册阳德的各 checker 2026 全年恰好单条 +10，30 天。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha.通用神煞 import CommonShenShaChecker
    from modules.shensha.开业神煞 import OpeningShenShaChecker
    from modules.shensha.作灶神煞 import StoveShenShaChecker
    from modules.shensha.安葬神煞 import BurialShenShaChecker
    from modules.shensha.神煞基类 import is_yangde_by_zhi, is_yinde_by_zhi
    days = [d for d in DAYS if d.year == 2026]
    for cls in (CommonShenShaChecker, OpeningShenShaChecker,
                StoveShenShaChecker, BurialShenShaChecker):
        c = cls()
        cnt = 0
        for d in days:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            hits = [x for x in c.check(sz, owners=[]) if x.get('name') == '阳德']
            if hits:
                cnt += 1
                assert len(hits) == 1 and hits[0]['score'] == 10, \
                    '%s %s 阳德条目异常 %s' % (cls.__name__, d, hits)
        assert cnt == 30, '%s 阳德命中 %d 天，期望 30' % (cls.__name__, cnt)
    for gd, gz in GOLDEN:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz, '%s 日柱期望%s 实际%s' % (gd, gz, sz['日柱'])
    # 模块级函数对偶：12 月阳德/阴德不同支；阳德函数与硬编码表一致
    for m in _MONTH_ORDER:
        assert is_yangde_by_zhi(m, YANGDE_CLASSICAL[m])
        assert not is_yangde_by_zhi(m, YINDE[m])
        assert is_yinde_by_zhi(m, YINDE[m])


if __name__ == '__main__':
    try:
        _assert_single_entry_all_checkers()
    except AssertionError as e:
        print('❌ 反向断言失败: %s' % e)
        sys.exit(1)
    sys.exit(run_cli(CASES))
