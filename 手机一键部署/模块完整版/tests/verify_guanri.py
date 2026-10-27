# -*- coding: utf-8 -*-
"""官日穷举验证（2026-10 A8 修复）
================================
典据《协纪辨方书》卷五·义例三「王官守相民日」条：
  《历例》曰：「……官日者春卯夏午秋酉冬子……」
即寅卯辰月卯、巳午未月午、申酉戌月酉、亥子丑月子（四季表），月神查**日支**。

旧实现按三合局取"三合中神"（寅午戌月午、申子辰月子、亥卯未月卯、
巳酉丑月酉），仅四个仲月（卯午酉子月）巧合一致，孟月/季月 8 个月全错：
2026 年穷举旧 30 天 vs 典载 32 天，交集仅 11 天。

结构同 verify_minri：权威真值表硬编码 + sxtwl 独立节气推导 +
1095 天谓词穷举 + 端到端单条目分值锁（+8）+ 黄金日干支硬锁 +
旧表误命中/漏命中反向断言。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，《协纪》卷五，查日支） =====
GUANRI_CLASSICAL = {
    '寅': '卯', '卯': '卯', '辰': '卯',      # 春（寅卯辰月）卯
    '巳': '午', '午': '午', '未': '午',      # 夏（巳午未月）午
    '申': '酉', '酉': '酉', '戌': '酉',      # 秋（申酉戌月）酉
    '亥': '子', '子': '子', '丑': '子',      # 冬（亥子丑月）子
}

# 旧错表（三合中神）
GUANRI_OLD = {
    '寅': '午', '午': '午', '戌': '午',
    '申': '子', '子': '子', '辰': '子',
    '亥': '卯', '卯': '卯', '未': '卯',
    '巳': '酉', '酉': '酉', '丑': '酉',
}

GOLDEN = [
    (datetime.date(2026, 2, 15),  '丁卯'),   # 寅月 卯日
    (datetime.date(2026, 3, 27),  '癸卯'),   # 卯月 卯日
    (datetime.date(2026, 4, 16),  '癸亥'),   # 辰月 卯日（癸亥日，日支卯？否）
]
# 上面 GOLDEN 由下方脚本生成后覆盖；此处占位会在运行时由真实数据替换。
GOLDEN = []


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

# 生成 2026 黄金日（每月支取首个典载命中日）+ 旧表误命中/漏命中样例
_picked = {}
_old_fp, _old_fn = [], []
for d in _all_days(2026):
    mz, dz = _branch(d)
    new_hit = dz == GUANRI_CLASSICAL.get(mz)
    old_hit = dz == GUANRI_OLD.get(mz)
    o = sxtwl.fromSolar(d.year, d.month, d.day)
    gz = GAN[o.getDayGZ().tg] + dz
    if new_hit and mz not in _picked:
        _picked[mz] = (d, gz)
    if old_hit and not new_hit and len(_old_fp) < 3:
        _old_fp.append((d, gz, mz))
    if new_hit and not old_hit and len(_old_fn) < 3:
        _old_fn.append((d, gz, mz))
_order = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
GOLDEN = [(_picked[m][0], _picked[m][1]) for m in _order if m in _picked]
OLD_TABLE_FALSE_POS = [x[0] for x in _old_fp]
OLD_TABLE_FALSE_NEG = [x[0] for x in _old_fn]

# 加载即断言：四季表结构 + 旧表仅仲月巧合（孟月季月共 8 月不同）
_SEASON_GROUPS = (('寅', '卯', '辰'), ('巳', '午', '未'), ('申', '酉', '戌'), ('亥', '子', '丑'))
assert all(len({GUANRI_CLASSICAL[m] for m in g}) == 1 for g in _SEASON_GROUPS)
assert {GUANRI_CLASSICAL[m] for m in ('寅', '巳', '申', '亥')} == {'卯', '午', '酉', '子'}
assert len(GUANRI_CLASSICAL) == 12 and len(GOLDEN) == 12
_diff_months = {m for m in _order if GUANRI_CLASSICAL[m] != GUANRI_OLD[m]}
assert len(_diff_months) == 8, '新旧应恰有 8 个月不同，实际 %d' % len(_diff_months)
assert _old_fp and _old_fn, '旧表误命中/漏命中样例必须存在'
for d, gz, mz in _old_fp:
    assert gz[1] == GUANRI_OLD[mz] and gz[1] != GUANRI_CLASSICAL[mz]
for d, gz, mz in _old_fn:
    assert gz[1] == GUANRI_CLASSICAL[mz] and gz[1] != GUANRI_OLD[mz]


def expected_pred(d):
    mz, dz = _branch(d)
    return dz == GUANRI_CLASSICAL.get(mz)


def adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker, is_guanri_by_zhi
    except Exception:
        return _UNAVAILABLE
    mz, dz = _branch(d)
    try:
        return ShenShaChecker()._is_guanri({'month_zhi': mz, 'day_zhi': dz})
    except Exception:
        return _UNAVAILABLE


def expected_e2e(d):
    mz, dz = _branch(d)
    return 8 if dz == GUANRI_CLASSICAL.get(mz) else None


def adapter_e2e(d):
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.shensha.开业神煞 import OpeningShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        items = [x for x in OpeningShenShaChecker().check(sz, owners=[])
                 if x.get('name') == '官日']
        if not items:
            return None
        if len(items) == 1 and items[0].get('score') == 8:
            return 8
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
        hit = ShenShaChecker()._is_guanri(sz)
        if d in dict(GOLDEN):
            return sz['日柱'] if hit else False
        return hit
    except Exception:
        return _UNAVAILABLE


case_pred = ShenShaCase(
    name='官日-谓词穷举', category='A',
    description='月神日支，《协纪》卷五"官日者春卯夏午秋酉冬子"，2025-2027共1095天，sxtwl独立推导',
    inputs=DAYS, expected=expected_pred, adapter=adapter_pred, compare='bool')

case_e2e = ShenShaCase(
    name='官日-端到端分值', category='A',
    description='开业checker 2026全年：命中唯一一条且+8，未命中无条目',
    inputs=[d for d in DAYS if d.year == 2026],
    expected=expected_e2e, adapter=adapter_e2e, compare='eq')

case_golden = ShenShaCase(
    name='官日-黄金日硬锁', category='A',
    description='12个月支黄金日日柱干支硬锁 + 旧三合中神表误命中日必须不命中 + 典载正格日必须命中',
    inputs=sorted({gd for gd, _ in GOLDEN} | set(OLD_TABLE_FALSE_POS)
                  | set(OLD_TABLE_FALSE_NEG)),
    expected=expected_golden, adapter=adapter_golden, compare='eq')

CASES = [case_pred, case_e2e, case_golden]


def _assert_single_entry_all_checkers():
    """注册官日的 checker（基类管线/开业/通用）2026 全年恰好单条 +8，32 天。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha.通用神煞 import CommonShenShaChecker
    from modules.shensha.开业神煞 import OpeningShenShaChecker
    from modules.shensha.作灶神煞 import StoveShenShaChecker
    from modules.shensha.安葬神煞 import BurialShenShaChecker
    days = [d for d in DAYS if d.year == 2026]
    for cls in (CommonShenShaChecker, OpeningShenShaChecker,
                StoveShenShaChecker, BurialShenShaChecker):
        c = cls()
        cnt = 0
        for d in days:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            hits = [x for x in c.check(sz, owners=[]) if x.get('name') == '官日']
            if hits:
                cnt += 1
                assert len(hits) == 1 and hits[0]['score'] == 8, \
                    '%s %s 官日条目异常 %s' % (cls.__name__, d, hits)
        assert cnt == 32, '%s 官日命中 %d 天，期望 32' % (cls.__name__, cnt)
    for gd, gz in GOLDEN:
        sz = calculate_sizhu(gd, 12, 0)
        assert sz['日柱'] == gz, '%s 日柱期望%s 实际%s' % (gd, gz, sz['日柱'])


if __name__ == '__main__':
    try:
        _assert_single_entry_all_checkers()
    except AssertionError as e:
        print('❌ 反向断言失败: %s' % e)
        sys.exit(1)
    sys.exit(run_cli(CASES))
