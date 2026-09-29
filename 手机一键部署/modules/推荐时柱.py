# -*- coding: utf-8 -*-
"""
推荐时柱 · 单一权威数据源（2026-09-09 P0 重构）

历史问题：系统里"选最佳吉时/推荐时柱"的逻辑散落在多处（扫日注入、双击详情预计算、
详情弹窗、玄空开窗反推），各自构造 checker 或调用不同算法（修造扩展 vs 择日贴
calc_shichen_jixiong），导致同一日课在不同界面给出不同推荐时柱（巳/亥混合等）。

本模块统一为一个纯函数 resolve_recommended_hour()：
  - 按事项类型构造唯一正确的 checker（修造带坐山/主命、婚姻带新郎新娘、其它通用）；
  - 调 checker.get_lucky_hours(norm_sizhu) 得十二时辰吉凶表；
  - 统一选时规则（正分未禁用优先，否则分值最高）；
  - 一并给出时支反推的代表小时（供玄空飞星时盘等使用）。

所有界面（扫日结果、日课详情、玄空开窗）都只消费本函数的结果，禁止各自重算。
"""

# 时支 → 该时辰代表小时（用于时飞星/时辰换算；同一时辰内不同小时得同一时干支）
ZHI_TO_HOUR = {
    '子': 0, '丑': 2, '寅': 4, '卯': 6, '辰': 8, '巳': 10,
    '午': 12, '未': 14, '申': 16, '酉': 18, '戌': 20, '亥': 22,
}

# 事项分类（2026-09-16 口径统一：唯一来源 modules/事项标准.py）
from modules.事项标准 import (
    RECOMMEND_HOUR_SHAN_EVENTS as CONSTRUCTION_EVENTS,
    MARRIAGE_UI_EVENTS as MARRIAGE_EVENTS,
    canonical_event,
)


def _gz(s):
    """'辛亥' -> ('辛','亥')；非法返回 ('','')。"""
    if isinstance(s, str) and len(s) >= 2:
        return s[0], s[1]
    return '', ''


def _owner_nian_ganzhi(owner):
    """取事主年干支：优先年干/年支字段，否则从 birth_date 反算。"""
    if not isinstance(owner, dict):
        return '', ''
    zg = owner.get('年干', '') or owner.get('year_gan', '')
    zz = owner.get('年支', '') or owner.get('year_zhi', '')
    if zg and zz:
        return zg, zz
    bd = owner.get('birth_date')
    if bd:
        try:
            from modules.四柱计算器 import calculate_sizhu
            bh = owner.get('birth_hour', 12) or 12
            bm = owner.get('birth_minute', 0) or 0
            osz = calculate_sizhu(bd, int(bh), int(bm),
                                  longitude=owner.get('birth_longitude'))
            return _gz(osz.get('年柱', ''))
        except Exception:
            return '', ''
    return '', ''


def _owner_yue_ganzhi(owner):
    """取事主月干支：优先月干/月支字段，否则从 birth_date 反算。 # _yt0915"""
    if not isinstance(owner, dict):
        return '', ''
    mg = owner.get('月干', '') or owner.get('month_gan', '')
    mz = owner.get('月支', '') or owner.get('month_zhi', '')
    if mg and mz:
        return mg, mz
    bd = owner.get('birth_date')
    if bd:
        try:
            from modules.四柱计算器 import calculate_sizhu
            bh = owner.get('birth_hour', 12) or 12
            bm = owner.get('birth_minute', 0) or 0
            osz = calculate_sizhu(bd, int(bh), int(bm),
                                  longitude=owner.get('birth_longitude'))
            return _gz(osz.get('月柱', ''))
        except Exception:
            return '', ''
    return '', ''


def _normalize_sizhu(sizhu):
    """完整 sizhu dict 或四柱字符串 -> {year_gan,...day_zhi} 六字字典。"""
    if isinstance(sizhu, dict):
        if sizhu.get('day_gan') and sizhu.get('day_zhi'):
            return {
                'year_gan': sizhu.get('year_gan', ''), 'year_zhi': sizhu.get('year_zhi', ''),
                'month_gan': sizhu.get('month_gan', ''), 'month_zhi': sizhu.get('month_zhi', ''),
                'day_gan': sizhu.get('day_gan', ''), 'day_zhi': sizhu.get('day_zhi', ''),
            }
        y_g, y_z = _gz(sizhu.get('年柱', ''))
        m_g, m_z = _gz(sizhu.get('月柱', ''))
        d_g, d_z = _gz(sizhu.get('日柱', ''))
        return {
            'year_gan': y_g, 'year_zhi': y_z,
            'month_gan': m_g, 'month_zhi': m_z,
            'day_gan': d_g, 'day_zhi': d_z,
        }
    return {}


def build_checker(event_type, owners_info=None, shan_xiang_str=''):
    """按事项类型构造唯一正确的时辰 checker。"""
    owners_info = owners_info or []
    # 2026-09-16 口径统一：选时 checker 一律打规范事项戳，
    # 时辰项目中与日课同名的神煞（如"日破时"）按事项自身口径取 SHENSHA_SCORES，
    # 动土/入宅/安葬等不再沿用"修造"分值。
    std_event = canonical_event(event_type)
    if event_type in CONSTRUCTION_EVENTS:
        from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
        zuoshan = None
        if shan_xiang_str and '山' in shan_xiang_str:
            zuoshan = shan_xiang_str.split('山')[0].strip()
        zhuming = None
        if isinstance(owners_info, list) and owners_info:
            try:
                zg, zz = _owner_nian_ganzhi(owners_info[0])
                if zg and zz:
                    zhuming = zg + zz
            except Exception:
                zhuming = None
        checker = ConstructionShenShaCheckerExt(zuoshan=zuoshan, zhuming=zhuming)
        checker._std_event = std_event
        return checker, 'construction'

    if event_type in MARRIAGE_EVENTS:
        from modules.shensha.嫁娶神煞扩展 import MarriageShenShaCheckerExt
        bride_gan = bride_zhi = groom_gan = groom_zhi = None
        # _yt0915：提取新娘月生干支（推阴胎）与新郎月生干支（推阳气），
        # 否则 get_lucky_hours 中冲阴胎/冲阳气检查被跳过，禁用时柱可能被推荐。
        bride_m_gan = bride_m_zhi = groom_m_gan = groom_m_zhi = None
        if isinstance(owners_info, list):
            for owner in owners_info:
                role = owner.get('role', '') if hasattr(owner.get('role'), 'lower') else owner.get('role')
                gender = owner.get('gender', '') if hasattr(owner.get('gender'), 'lower') else owner.get('gender')
                role = role.strip() if isinstance(role, str) else ''
                gender = gender.strip() if isinstance(gender, str) else ''
                is_bride = (role in ['新娘', '坤造']) or (not role and gender == '女')
                is_groom = (role in ['新郎', '乾造']) or (not role and gender == '男')
                zg, zz = _owner_nian_ganzhi(owner)
                mg, mz = _owner_yue_ganzhi(owner)
                if is_bride and not bride_gan:
                    bride_gan, bride_zhi = zg, zz
                    bride_m_gan, bride_m_zhi = mg, mz
                if is_groom and not groom_gan:
                    groom_gan, groom_zhi = zg, zz
                    groom_m_gan, groom_m_zhi = mg, mz
        checker = MarriageShenShaCheckerExt(
            bride_gan=bride_gan, bride_zhi=bride_zhi,
            groom_gan=groom_gan, groom_zhi=groom_zhi,
            bride_month_gan=bride_m_gan, bride_month_zhi=bride_m_zhi,
            groom_month_gan=groom_m_gan, groom_month_zhi=groom_m_zhi
        )
        checker._std_event = std_event
        return checker, 'marriage'

    # 其它事项：修造扩展通用评分（不含坐山/主命）
    from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
    checker = ConstructionShenShaCheckerExt(zuoshan=None, zhuming=None)
    checker._std_event = std_event
    return checker, 'generic'


def pick_best_hour(lucky_hours):
    """统一选时规则：非禁用中取正分最高；无正分则取非禁用分值最高；返回时辰 dict 或 None。"""
    if not isinstance(lucky_hours, list):
        return None
    avail = [h for h in lucky_hours if isinstance(h, dict) and not h.get('禁用', False)]
    good = [h for h in avail if int(h.get('分值', 0) or 0) > 0]
    if good:
        good.sort(key=lambda h: int(h.get('分值', 0) or 0), reverse=True)
        return good[0]
    if avail:
        avail.sort(key=lambda h: int(h.get('分值', 0) or 0), reverse=True)
        return avail[0]
    return None


def resolve_recommended_hour(sizhu, event_type, owners_info=None, shan_xiang_str=''):
    """权威推荐时柱（单一数据源）。

    参数
    ----
    sizhu : dict  —— 完整 sizhu（含 年柱/月柱/日柱 或 year_gan..day_zhi）。时柱无需提供，
                     推荐时柱由十二时辰吉凶表选出。
    event_type : str
    owners_info : list[dict]
    shan_xiang_str : str  —— 如 "寅山申向"

    返回
    ----
    dict 或 None：
      {
        'best_gz': '辛亥', 'best_gan':'辛', 'best_zhi':'亥', 'best_hour': 22,
        'best': {时辰dict}, 'lucky_hours': [...], 'checker_kind': 'construction'...
      }
    """
    try:
        norm = _normalize_sizhu(sizhu)
        if not (norm.get('day_gan') and norm.get('day_zhi')):
            return None
        checker, kind = build_checker(event_type, owners_info, shan_xiang_str)
        lucky_hours = checker.get_lucky_hours(norm)
        best = pick_best_hour(lucky_hours)
        if not best:
            return None
        b_gan = best.get('天干', '') or ''
        b_zhi = best.get('地支', '') or ''
        return {
            'best_gz': f"{b_gan}{b_zhi}",
            'best_gan': b_gan,
            'best_zhi': b_zhi,
            'best_hour': ZHI_TO_HOUR.get(b_zhi, 12),
            'best': best,
            'lucky_hours': lucky_hours,
            'checker_kind': kind,
        }
    except Exception as e:
        print(f"[推荐时柱] resolve_recommended_hour 失败: {e}")
        return None
