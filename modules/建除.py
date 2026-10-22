# -*- coding: utf-8 -*-
"""
================================================================================
建除十二神单一事实源
================================================================================
批次 1（2026-10-22，001 §161）建立：全项目建除星名计算只此一处。

起例（J1，0001 §57/卷四）：
    正月建寅，二月建卯，依月建顺行十二辰；
    日支与月支同支为「建」，顺数十二辰：
    建、除、满、平、定、执、破、危、成、收、开、闭。
    公式：(日支序 − 月支序) % 12。

吉凶（J2，卷四/卷十）：
    吉：除、危、定、执、成、开
    凶：建、满、平、破、收、闭

两种口径：
- **按日判**（默认）：`star_by_sizhu(sizhu)` 用传入四柱的月支/日支；
  `is_jianchu_date(date_obj, name, hour=12)` 默认取当日 12:00 月支，
  与历史 `calculate_sizhu(date, 12, 0)` 口径一致。
- **按时辰判**（交节日特判）：评分链路应把真实时柱月支放进 sizhu 后
  调用 `star_by_sizhu` / `is_jianchu`；或把所用时辰的 hour 传给
  `is_jianchu_date`，不得再回落 12:00。

非法输入一律抛 ValueError（不得静默按索引 0 计成「建」）；
各调用方保留自己的兜底文案（'未知' / ''），仅负责捕获。
================================================================================
"""

ZHI_ORDER = ('子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥')

STARS = ('建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭')

JIXIONG = {
    '建': '凶', '除': '吉', '满': '凶', '平': '凶', '定': '吉', '执': '吉',
    '破': '凶', '危': '吉', '成': '吉', '收': '凶', '开': '吉', '闭': '凶',
}

JI_STARS = frozenset(('除', '危', '定', '执', '成', '开'))
XIONG_STARS = frozenset(('建', '满', '平', '破', '收', '闭'))

_ZHI_INDEX = {z: i for i, z in enumerate(ZHI_ORDER)}


def star(month_zhi, day_zhi):
    """按月支、日支取建除星名；非法地支抛 ValueError。"""
    m = _ZHI_INDEX.get(month_zhi)
    if m is None:
        raise ValueError('未知月支：%r' % (month_zhi,))
    d = _ZHI_INDEX.get(day_zhi)
    if d is None:
        raise ValueError('未知日支：%r' % (day_zhi,))
    return STARS[(d - m) % 12]


def _zhi_of(sizhu, keys, label):
    """从四柱字典取地支（键名兼容 month_zhi/月支/月柱[1] 等）。"""
    if not isinstance(sizhu, dict):
        raise ValueError('四柱不是字典，无法取%s' % label)
    for k in keys:
        v = sizhu.get(k)
        if isinstance(v, str) and len(v) >= 2:
            return v[1]
    raise ValueError('缺少%s：%r' % (label, keys))


def _month_zhi_of(sizhu):
    return _zhi_of(sizhu, ('month_zhi', '月支', '月柱'), '月支')


def _day_zhi_of(sizhu):
    return _zhi_of(sizhu, ('day_zhi', '日支', '日柱'), '日支')


def star_by_sizhu(sizhu):
    """按四柱（真实时柱月支）取建除星名。"""
    return star(_month_zhi_of(sizhu), _day_zhi_of(sizhu))


def is_jianchu(sizhu, name):
    """四柱当日的建除星是否等于 name。"""
    return star_by_sizhu(sizhu) == name


def is_jianchu_date(date_obj, name, hour=12, minute=0):
    """按公历日期判建除星；默认 12:00（按日判），交节日传真实 hour（按时辰判）。"""
    from .四柱计算器 import calculate_sizhu
    sizhu = calculate_sizhu(date_obj, hour, minute)
    return is_jianchu(sizhu, name)


# ==================== 导入自检 ====================
if not (len(ZHI_ORDER) == 12 and len(STARS) == 12):
    raise RuntimeError('建除自检失败：地支或星名数量不是 12')
if set(STARS) != set(JIXIONG):
    raise RuntimeError('建除自检失败：JIXIONG 与 STARS 不匹配')
if JI_STARS | XIONG_STARS != set(STARS):
    raise RuntimeError('建除自检失败：吉凶集合未覆盖全部星名')
if JI_STARS & XIONG_STARS:
    raise RuntimeError('建除自检失败：吉凶集合相交')
