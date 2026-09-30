# -*- coding: utf-8 -*-
"""
玄空飞星引擎（单一数据源 / 纯函数核心）

历史背景：玄空飞星存在两套独立实现——
  1) 评分器 Scorer._calculate_feixing_score：手抄飞星常量并自行排盘，产出
     feixing_score(-20~+20) 用于加权/否决；
  2) 玄空飞星_日课展示.py：独立排盘引擎，用于九宫格窗口展示。
两者靠"保持一致"的注释维系，常量与日星算法手抄两份，极易漂移。
本模块将排盘常量、洛书飞布、冬至/夏至日星、坐山分析、数值评分全部收敛为
纯函数，评分器与玄空窗口统一调用，杜绝双标准。

排盘规则（紫白择日典籍口径，歌诀见《选择宗镜》《沈氏玄空学》）：
  年星：下元1984甲子年七赤入中，逐年逆飞 norm(7-(年-1984)%9)，年以立春为界
  月星：年支定寅月(正月)起星(BASE_MONTH_STAR)，寅月起逐月逆飞
  日星：六中气换元——冬至1白/雨水7赤/谷雨4绿顺飞，夏至9紫/处暑3碧/霜降6白逆飞；
        各以该中气后第一个甲子日起星（日家紫白歌诀"冬至一宫雨水七…"）
  时星：依日段阳顺阴逆。阳遁(冬至后) 仲(子午卯酉)子起1白/季(辰戌丑未)4绿/孟(寅申巳亥)7赤顺飞；
        阴遁(夏至后) 仲9紫/季6白/孟3碧逆飞（"孟日七宫仲一白，季日四绿；孟归三碧季加六，仲在九宫"）
  九宫：洛书序 LUO_SHU_ORDER 顺飞，中宫立极（入中星定后八方永远顺布）
"""

from datetime import datetime, date as _date, timedelta

try:
    import sxtwl
    _HAS_SXTWL = True
except Exception:
    sxtwl = None
    _HAS_SXTWL = False

# ============================================================
#  常量（唯一来源，评分器与窗口共用，禁止再手抄）
# ============================================================
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
MONTH_ZHI_TO_INDEX = {z: i + 1 for i, z in enumerate(DIZHI)}
HOUR_ZHI_TO_INDEX = {z: i + 1 for i, z in enumerate(DIZHI)}

BASE_MONTH_STAR = {
    '子': 8, '午': 8, '卯': 8, '酉': 8,
    '辰': 5, '戌': 5, '丑': 5, '未': 5,
    '寅': 2, '申': 2, '巳': 2, '亥': 2,
}
# 时星起例：阳遁（冬至→夏至，顺飞）仲1/季4/孟7
BASE_HOUR_STAR_YANG = {
    '子': 1, '午': 1, '卯': 1, '酉': 1,
    '辰': 4, '戌': 4, '丑': 4, '未': 4,
    '寅': 7, '申': 7, '巳': 7, '亥': 7,
}
# 时星起例：阴遁（夏至→冬至，逆飞）仲9/季6/孟3
BASE_HOUR_STAR_YIN = {
    '子': 9, '午': 9, '卯': 9, '酉': 9,
    '辰': 6, '戌': 6, '丑': 6, '未': 6,
    '寅': 3, '申': 3, '巳': 3, '亥': 3,
}
# 兼容旧导出名：BASE_HOUR_STAR 即阳遁起例
BASE_HOUR_STAR = dict(BASE_HOUR_STAR_YANG)
# 日家紫白六段换元：sxtwl节气数组自立春起，索引 雨水1/谷雨5/夏至9/处暑13/霜降17/冬至21。
# 每项 (节气索引, 节后第一个甲子日入中星, +1顺飞/-1逆飞)
DAY_JIEQI_SEGMENTS = [(21, 1, +1), (1, 7, +1), (5, 4, +1),
                      (9, 9, -1), (13, 3, -1), (17, 6, -1)]
STAR_NAMES = ['一白', '二黑', '三碧', '四绿', '五黄', '六白', '七赤', '八白', '九紫']
LUO_SHU_ORDER = [4, 9, 2, 3, 5, 7, 8, 1, 6]

# 二十四山（罗盘顺时针）
MOUNTAINS_CW = ['壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
                '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥']
MOUNTAIN_DIRECTION = {
    '壬': '北偏西', '子': '正北',   '癸': '北偏东',
    '丑': '东北偏北', '艮': '东北',  '寅': '东北偏东',
    '甲': '东偏北', '卯': '正东',   '乙': '东偏南',
    '辰': '东南偏东', '巽': '东南',  '巳': '东南偏南',
    '丙': '南偏东', '午': '正南',   '丁': '南偏西',
    '未': '西南偏南', '坤': '西南',  '申': '西南偏西',
    '庚': '西偏南', '酉': '正西',   '辛': '西偏北',
    '戌': '西北偏西', '乾': '西北',  '亥': '西北偏北',
}
MOUNTAIN_LABELS = [f"{m}山 · {MOUNTAIN_DIRECTION[m]}" for m in MOUNTAINS_CW]
# 九宫索引 -> 该宫所辖三山（索引序：0巽/1离/2坤/3震/4中/5兑/6艮/7坎/8乾）
MOUNTAIN_TO_INDEX = {
    '壬': 7, '子': 7, '癸': 7,
    '丑': 6, '艮': 6, '寅': 6,
    '甲': 3, '卯': 3, '乙': 3,
    '辰': 0, '巽': 0, '巳': 0,
    '丙': 1, '午': 1, '丁': 1,
    '未': 2, '坤': 2, '申': 2,
    '庚': 5, '酉': 5, '辛': 5,
    '戌': 8, '乾': 8, '亥': 8,
}
POS_NAMES = ['东南', '南', '西南', '东', '中', '西', '东北', '北', '西北']
# 九宫索引对应八卦宫名（评分器断语用"乾宫"等）
GONG_NAMES = ['巽宫', '离宫', '坤宫', '震宫', '中宫', '兑宫', '艮宫', '坎宫', '乾宫']
# 九宫索引对应卦名（窗口展示用"乾"等）
GUA_NAMES = ['巽', '离', '坤', '震', '中', '兑', '艮', '坎', '乾']

GOOD_STARS = [1, 6, 8, 9]
BAD_STARS = [2, 3, 5, 7]


# ============================================================
#  排盘核心（纯函数）
# ============================================================
def get_grid_by_middle(middle_star):
    """中宫立极，按洛书序顺飞布出九宫星曜。"""
    return [(middle_star + (pos - 5) - 1) % 9 + 1 for pos in LUO_SHU_ORDER]


def get_solstice_info(year, month, day):
    """返回 (距上一冬至/夏至的天数, 是否冬至后阳遁)。
    冬至(index21)后顺飞，夏至(index9)后逆飞。"""
    dt = datetime(year, month, day, 12, 0, 0)
    candidates = []
    if _HAS_SXTWL:
        for y in (year - 1, year, year + 1):
            try:
                jqs_y = sxtwl.getJieQiByYear(y)

                def _jd_to_dt(jd):
                    dd = sxtwl.JD2DD(jd)
                    return datetime(int(dd.Y), int(dd.M), int(dd.D),
                                    int(dd.h), int(dd.m), int(dd.s))

                candidates.append((_jd_to_dt(jqs_y[21].jd), 'winter'))
                candidates.append((_jd_to_dt(jqs_y[9].jd), 'summer'))
            except Exception:
                continue
    candidates.sort(key=lambda x: x[0])
    prev = None
    for c in candidates:
        if c[0] <= dt:
            prev = c
        else:
            break
    if prev is None and candidates:
        prev = candidates[0]
    if prev is None:
        return 0, True
    day_diff = (dt.date() - prev[0].date()).days
    return day_diff, (prev[1] == 'winter')


def _day_gz_index(y, m, d):
    """公历日的六十甲子序号（甲子=0）。sxtwl 不可用时返回 None。"""
    if not _HAS_SXTWL:
        return None
    try:
        g = sxtwl.fromSolar(int(y), int(m), int(d)).getDayGZ()
        return (g.tg * 6 - g.dz * 5) % 60
    except Exception:
        return None


def _day_segment_info(dt):
    """日家紫白六段换元：返回 dt 所属段 (段首甲子日date, 甲子日起星, 顺逆±1)。

    各段以六个中气后的【第一个甲子日】为界（冬至/雨水/谷雨为阳三元：
    1白/7赤/4绿顺飞；夏至/处暑/霜降为阴三元：9紫/3碧/6白逆飞）。
    中气与段首甲子日之间的日子仍归上一元。
    两段首同日（同一甲子日恰为两中气之界，仅霜降→冬至间距59天可现）时，
    取中气时序靠后者之元。
    """
    if not _HAS_SXTWL:
        return None
    cands = []
    for y in (dt.year - 1, dt.year, dt.year + 1):
        try:
            jqs = sxtwl.getJieQiByYear(y)
            for jq_idx, base, dr in DAY_JIEQI_SEGMENTS:
                dd = sxtwl.JD2DD(jqs[jq_idx].jd)
                seg_dt = datetime(int(dd.Y), int(dd.M), int(dd.D),
                                  int(dd.h), int(dd.m), int(dd.s))
                gz0 = _day_gz_index(seg_dt.year, seg_dt.month, seg_dt.day)
                if gz0 is None:
                    continue
                off = (-gz0) % 60   # 中气后第一个甲子日距中气天数（0=当日即甲子）
                jiazi_day = (seg_dt + timedelta(days=off)).date()
                cands.append((jiazi_day, seg_dt, base, dr))
        except Exception:
            continue
    # 段首同日冲突决胜：排序键含中气时刻，同日时中气靠后者排末位，
    # 末位覆盖即取靠后中气之元（无冲突时行为与旧逻辑完全一致）
    cands.sort(key=lambda c: (c[0], c[1]))
    prev = None
    cur_date = dt.date()
    for c in cands:
        if c[0] <= cur_date:
            prev = (c[0], c[2], c[3])
        else:
            break
    return prev


def _year_middle_star(year_val, year_zhi, year_gan=None):
    """年星：下元1984甲子七赤入中，逐年逆飞；年以立春为界。

    优先用年柱干支六十甲子序号推算（天然不受立春年界影响）；
    缺年干时由公历年反推，并以八字年支校正立春前退一年。
    """
    try:
        gan_idx = year_gan
        if isinstance(gan_idx, str):
            gan_idx = TIANGAN.index(gan_idx) if gan_idx in TIANGAN else None
        if gan_idx is None and year_zhi in DIZHI:
            gan_idx = (int(year_val) - 4) % 10
            # 公历元旦至立春前，八字年支属上一年：年干同步退一
            if DIZHI[(int(year_val) - 4) % 12] != year_zhi:
                gan_idx = (gan_idx - 1) % 10
        if gan_idx is not None and year_zhi in DIZHI:
            gz_idx = (int(gan_idx) * 6 - DIZHI.index(year_zhi) * 5) % 60
            return _norm_star(7 - (gz_idx % 9))
    except Exception:
        pass
    return _norm_star(7 - ((int(year_val) - 1984) % 9))


def _norm_star(v):
    return (v - 1) % 9 + 1


def compute_stars(year_val, year_zhi, month_zhi, day_zhi, hour_zhi, date_obj=None,
                  year_gan=None):
    """按四柱地支 + 公历日期排出年/月/日/时四盘。

    返回 {'year'/'month'/'day'/'hour': {'star':中宫星, 'grid':九宫星列表}}。
    评分器四柱地支已知时直接调用本函数，避免重复反推干支。
    year_gan 可传年干（字或0..9序号），用于精确定位干支年（立春年界）。
    """
    # 年星：七赤起下元甲子，逐年逆飞（年以立春为界）
    year_star = _year_middle_star(year_val, year_zhi, year_gan)
    # 月星：年支定寅月起星，寅月起逐月逆飞
    if month_zhi in DIZHI:
        month_seq = (DIZHI.index(month_zhi) - 2) % 12 + 1   # 寅月=1
        base_m = BASE_MONTH_STAR.get(year_zhi, 5)
        month_star = _norm_star(base_m - (month_seq - 1))
    else:
        month_star = 5
    # 日星：六中气换元，各以节后第一个甲子日起星，阳三元顺飞/阴三元逆飞
    day_star = 5
    hour_yang = True   # 时星随日段分阳顺阴逆
    if date_obj is not None:
        try:
            seg = _day_segment_info(datetime(date_obj.year, date_obj.month, date_obj.day, 12))
        except Exception:
            seg = None
        if seg is not None:
            jiazi_day, d_base, d_dr = seg
            n_days = (date_obj.date() - jiazi_day).days
            day_star = _norm_star(d_base + d_dr * n_days)
            hour_yang = (d_dr > 0)
        else:
            # sxtwl 不可用时退回旧的冬至顺/夏至逆（节气当日起算，近似）
            day_diff, is_winter = get_solstice_info(date_obj.year, date_obj.month, date_obj.day)
            if is_winter:
                day_star = (day_diff % 9) + 1
            else:
                day_star = 9 - (day_diff % 9)
                if day_star == 0:
                    day_star = 9
            hour_yang = is_winter
    # 时星：阳遁仲1/季4/孟7顺飞；阴遁仲9/季6/孟3逆飞
    hour_index = HOUR_ZHI_TO_INDEX.get(hour_zhi, 1)
    if hour_yang:
        base_h = BASE_HOUR_STAR_YANG.get(day_zhi, 1)
        hour_star = _norm_star(base_h + (hour_index - 1))
    else:
        base_h = BASE_HOUR_STAR_YIN.get(day_zhi, 9)
        hour_star = _norm_star(base_h - (hour_index - 1))
    return {
        'year': {'star': year_star, 'grid': get_grid_by_middle(year_star)},
        'month': {'star': month_star, 'grid': get_grid_by_middle(month_star)},
        'day': {'star': day_star, 'grid': get_grid_by_middle(day_star)},
        'hour': {'star': hour_star, 'grid': get_grid_by_middle(hour_star)},
    }


def _extract_zhi(sizhu):
    """从 sizhu(dict) 提取年/月/日/时支与公历年份/日期，兼容四柱键与 *_zhi 键。"""
    def _zhi_of(pillar_key, zhi_key):
        z = sizhu.get(zhi_key)
        if z:
            return z
        p = sizhu.get(pillar_key, '')
        return p[1] if isinstance(p, str) and len(p) >= 2 else ''

    year_zhi = _zhi_of('年柱', 'year_zhi')
    month_zhi = _zhi_of('月柱', 'month_zhi')
    day_zhi = _zhi_of('日柱', 'day_zhi')
    hour_zhi = _zhi_of('时柱', 'hour_zhi')
    year_gan = sizhu.get('year_gan')
    if not year_gan:
        p = sizhu.get('年柱', '')
        year_gan = p[0] if isinstance(p, str) and len(p) >= 2 else None
    year_val = sizhu.get('year')
    date_obj = sizhu.get('date')
    if date_obj is not None and not isinstance(date_obj, datetime):
        try:
            date_obj = datetime(date_obj.year, date_obj.month, date_obj.day)
        except Exception:
            date_obj = None
    if not year_val and date_obj is not None:
        year_val = date_obj.year
    return year_zhi, month_zhi, day_zhi, hour_zhi, year_val, date_obj, year_gan


def get_xuan_kong_data(year, month, day, hour, minute=0, second=0):
    """窗口接口：由公历日期反推四柱后排盘，附带农历/节气信息。"""
    try:
        from .高精度农历转换 import get_lunar_converter
    except ImportError:
        from 高精度农历转换 import get_lunar_converter
    conv = get_lunar_converter(strict_mode=False)
    info = conv.solar_to_lunar_with_check(year, month, day, hour, minute, second)
    ec = info['eight_char']
    year_zhi = ec['year'][1]
    month_zhi = ec['month'][1]
    day_zhi = ec['day'][1]
    hour_zhi = ec['hour'][1]
    grids = compute_stars(year, year_zhi, month_zhi, day_zhi, hour_zhi,
                          datetime(year, month, day), year_gan=ec['year'][0])
    return {
        'year': grids['year'],
        'month': grids['month'],
        'day': grids['day'],
        'hour': grids['hour'],
        'sizhu': {'year': ec['year'], 'month': ec['month'],
                  'day': ec['day'], 'hour': ec['hour']},
        'summary': f"年{STAR_NAMES[grids['year']['star'] - 1]} "
                   f"月{STAR_NAMES[grids['month']['star'] - 1]} "
                   f"日{STAR_NAMES[grids['day']['star'] - 1]} "
                   f"时{STAR_NAMES[grids['hour']['star'] - 1]}",
        'lunar_date': info['lunar_date_str'],
        'jie_qi': info['jie_qi'],
    }


# ============================================================
#  坐山分析（窗口展示用）
# ============================================================
def get_mountain_label(mountain, offset_degree):
    if not mountain or mountain not in MOUNTAINS_CW:
        return mountain or "未知"
    if abs(offset_degree) < 3.0:
        return f"{mountain}山（正向）"
    idx = MOUNTAINS_CW.index(mountain)
    if offset_degree > 0:
        target = MOUNTAINS_CW[(idx + 1) % 24]
    else:
        target = MOUNTAINS_CW[(idx - 1) % 24]
    return f"{mountain}山兼{target}"


def _judge_mountain_stars(star_list, mountain, pos_name, is_partial):
    """坐山方年/月/日/时四星的统一打分与判级（唯一数据源，2026-09-12）。

    score_feixing（评分器/主程序/吉日搜索）与窗口文字结论均须调用本函数，
    杜绝"盘面正确、但文字另按全盘他宫判大凶"的双标准。

    Returns:
        fx_score(-20~+20) / fx_level / fx_comment / details /
        good_count / bad_count / has_5 / has_2 / combos(坐山凶格名list)
    """
    good_count = sum(1 for s in star_list if s in GOOD_STARS)
    bad_count = sum(1 for s in star_list if s in BAD_STARS)
    has_5 = any(s == 5 for s in star_list)
    has_2 = any(s == 2 for s in star_list)

    er_wu = (2 in star_list and 5 in star_list)
    san_qi = (3 in star_list and 7 in star_list)
    liu_qi = (6 in star_list and 7 in star_list)

    fx_score = 0
    details = []
    stars = {'年': star_list[0], '月': star_list[1],
             '日': star_list[2], '时': star_list[3]}

    if has_5 or has_2:
        fx_score -= 15
        _bad = [f"{_p}{STAR_NAMES[_s - 1]}" for _p, _s in stars.items() if _s in (2, 5)]
        details.append(f"{'、'.join(_bad)}到{GONG_NAMES[MOUNTAIN_TO_INDEX[mountain]]}（坐山，-15）")

    if bad_count >= 3:
        fx_score -= 10
        details.append(f"凶星{bad_count}颗汇聚（-10）")

    if good_count >= 3:
        fx_score += 15
        details.append(f"吉星{good_count}颗汇聚（+15）")
    elif good_count >= 2:
        fx_score += 8
        details.append(f"吉星{good_count}颗汇聚（+8）")

    if er_wu:
        fx_score -= 5
        details.append("二五叠临（额外-5，合计-20）")
    if san_qi:
        fx_score -= 15
        details.append("三七叠临（-15）")
    if liu_qi:
        fx_score -= 15
        details.append("六七交剑（-15）")

    if is_partial:
        fx_score -= 10
        details.append("兼向需替卦复核（-10）")

    _fx_raw = fx_score
    fx_score = max(-20, min(20, fx_score))
    if fx_score != _fx_raw:
        if _fx_raw < -20:
            details.append(f"明细合计{_fx_raw:+d}，低于下限-20，按-20计")
        else:
            details.append(f"明细合计{_fx_raw:+d}，高于上限+20，按+20计")

    # 定级（2026-09-12 用户拍板：以 fx_score 终判，坐山凶格硬性封顶）：
    #   五黄/二五 → 大凶；二黑且凶星汇聚 → 凶；
    #   坐山六七交剑/三七叠临 → 等级不得高于"平"（再高的吉星也不许判吉）；
    #   无坐山凶格 → 按分数：≥15大吉、≥5吉、[-5,5)平、<-5凶。
    combo_desp = None
    if liu_qi:
        combo_desp = ('六七交剑', '六白七赤同宫，主争斗、刑伤官非')
    elif san_qi:
        combo_desp = ('三七叠临', '三碧七赤同宫，主官非、盗贼')

    if has_5:
        fx_level = "大凶"
        fx_comment = f"坐{mountain}（{pos_name}方）五黄到山，切忌动土修造"
    elif er_wu:
        fx_level = "大凶"
        fx_comment = f"坐{mountain}（{pos_name}方）二五叠临，主疾病灾祸"
    elif has_2 and bad_count >= 2:
        fx_level = "凶"
        fx_comment = f"坐{mountain}（{pos_name}方）二黑加临且凶星汇聚，防疾病"
    else:
        if fx_score >= 15:
            fx_level = "大吉"
        elif fx_score >= 5:
            fx_level = "吉"
        elif fx_score >= -5:
            fx_level = "平"
        else:
            fx_level = "凶"
        # 坐山凶格封顶：交剑/叠临在山，吉星再多也只作"平"论
        if combo_desp is not None and fx_level in ("大吉", "吉"):
            fx_level = "平"
        if combo_desp is not None:
            if fx_level == "平":
                fx_comment = (f"坐{mountain}（{pos_name}方）{combo_desp[0]}，{combo_desp[1]}；"
                              f"虽有吉星会合，凶格在山仅作平论，慎用")
            else:
                fx_comment = (f"坐{mountain}（{pos_name}方）{combo_desp[0]}，{combo_desp[1]}，"
                              f"又逢凶象，不取")
        elif fx_level == "大吉":
            fx_comment = f"坐{mountain}（{pos_name}方）吉星高照，用之大吉"
        elif fx_level == "吉":
            fx_comment = f"坐{mountain}（{pos_name}方）吉星汇聚，可用"
        elif fx_level == "凶":
            fx_comment = f"坐{mountain}（{pos_name}方）凶星较众，不利"
        else:
            fx_comment = f"坐{mountain}（{pos_name}方）吉凶参半，需结合日课综合判断"

    combos = [_n for _n, _ok in
              (('二五叠临', er_wu), ('三七叠临', san_qi), ('六七交剑', liu_qi))
              if _ok]
    return {
        'fx_score': fx_score, 'fx_level': fx_level, 'fx_comment': fx_comment,
        'details': details, 'good_count': good_count, 'bad_count': bad_count,
        'has_5': has_5, 'has_2': has_2, 'combos': combos,
    }


def analyze_mountain(selected_mountain, data, offset_degree=0.0):
    if not selected_mountain or selected_mountain not in MOUNTAIN_TO_INDEX:
        return None
    idx = MOUNTAIN_TO_INDEX[selected_mountain]
    pos_name = POS_NAMES[idx]
    is_partial = abs(offset_degree) >= 3.0
    stars = {
        '年': data['year']['grid'][idx],
        '月': data['month']['grid'][idx],
        '日': data['day']['grid'][idx],
        '时': data['hour']['grid'][idx],
    }
    star_list = list(stars.values())

    # 判级/打分统一走 _judge_mountain_stars（与 score_feixing 同源；
    # 兼向只在分数上按替卦口径-10，不再把等级改写成"慎用（兼向）"）
    _judge = _judge_mountain_stars(star_list, selected_mountain, pos_name, is_partial)
    level = _judge['fx_level']
    good_count = _judge['good_count']
    bad_count = _judge['bad_count']
    has_5 = _judge['has_5']
    has_2 = _judge['has_2']
    combo_warnings = list(_judge['combos'])

    mountain_label = get_mountain_label(selected_mountain, offset_degree)
    suggestion = _judge['fx_comment'] + "。"
    if is_partial:
        suggestion += f" 偏移{offset_degree:.1f}°，已属兼向，分数按替卦口径计，实际用事仍建议替卦（起星）重排。"
    else:
        suggestion += " 此为正向，可用本宫星断之。"
    if combo_warnings:
        suggestion += " 注意（坐山方）：" + "；".join(combo_warnings)

    return {
        'mountain_label': mountain_label,
        'mountain': selected_mountain,
        'position': pos_name,
        'offset': offset_degree,
        'is_partial': is_partial,
        'stars': stars,
        'level': level,
        'suggestion': suggestion,
        'good_count': good_count,
        'bad_count': bad_count,
        'has_5': has_5,
        'has_2': has_2,
        'combo_warnings': combo_warnings,
        'fx_score': _judge['fx_score'],
        'fx_details': _judge['details'],
    }


def generate_xuankong_comment(data, selected_mountain=None, offset_degree=0.0):
    """生成窗口文字结论。口径（2026-09-12 修正双标准）：

    日课吉凶**只以坐山方年/月/日/时四星为纲**，判级/打分与 score_feixing
    完全同源；他宫（非坐山八方）的二黑五黄、凶星汇聚与凶格只作"修方宜避"
    的方位提示，不再把整个日课判成"飞星大凶"。旧版按全盘 36 格吉凶计数
    （九星每盘恒 4 吉 4 凶 1 平，全盘恒为 16:16）再因他宫凶格扣分，导致
    坐山聚 3 吉也几乎必判大凶，与排盘及主程序评分矛盾。
    """
    disks = {'年': data['year'], '月': data['month'], '日': data['day'], '时': data['hour']}
    mountain_idx = (MOUNTAIN_TO_INDEX[selected_mountain]
                    if selected_mountain and selected_mountain in MOUNTAIN_TO_INDEX else None)

    # —— 各方吉/凶星计数 ——
    pos_good_count = [0] * 9
    pos_bad_count = [0] * 9
    for disk in disks.values():
        for idx, val in enumerate(disk['grid']):
            if val in GOOD_STARS:
                pos_good_count[idx] += 1
            if val in BAD_STARS:
                pos_bad_count[idx] += 1

    good_points = []
    mountain_warnings = []     # 坐山宫的警示（参与日课判级）
    other_warnings = []        # 他宫提示（只关乎修方，不否决日课）
    for idx, count in enumerate(pos_good_count):
        tag = "★坐山 " if idx == mountain_idx else ""
        if count >= 3:
            good_points.append(f"{tag}「{POS_NAMES[idx]}」方{count}颗吉星汇聚，大吉")
        elif count == 2:
            good_points.append(f"{tag}「{POS_NAMES[idx]}」方{count}颗吉星，可用")
    good_points.sort(key=lambda t: 0 if t.startswith("★") else 1)  # 坐山项置顶
    for idx, count in enumerate(pos_bad_count):
        is_ms = (idx == mountain_idx)
        if count >= 3:
            msg = (f"「{POS_NAMES[idx]}」方{count}颗凶星汇聚，大凶勿用" if is_ms else
                   f"「{POS_NAMES[idx]}」方{count}颗凶星汇聚，修方宜避")
        elif count == 2:
            msg = (f"「{POS_NAMES[idx]}」方{count}颗凶星，坐山忌用" if is_ms else
                   f"「{POS_NAMES[idx]}」方{count}颗凶星，修方宜避")
        else:
            continue
        (mountain_warnings if is_ms else other_warnings).append(msg)

    # —— 单星二黑/五黄临方 ——
    for disk_name, disk in disks.items():
        for idx, val in enumerate(disk['grid']):
            pos = POS_NAMES[idx]
            if val == 5:
                msg = f"{disk_name}盘五黄在「{pos}」方，忌动土修造"
            elif val == 2:
                msg = f"{disk_name}盘二黑在「{pos}」方，宜静防病"
            else:
                continue
            if idx == mountain_idx:
                mountain_warnings.append(msg + "（坐山）")
            else:
                other_warnings.append(msg)

    # —— 凶格（坐山/他宫分组）——
    mountain_combos = []
    other_combos = []
    for idx in range(9):
        s4 = [disk['grid'][idx] for disk in disks.values()]
        names = []
        if 2 in s4 and 5 in s4:
            names.append("二五叠临，主疾病灾祸")
        if 3 in s4 and 7 in s4:
            names.append("三七叠临，主官非盗贼")
        if 6 in s4 and 7 in s4:
            names.append("六七交剑，主争斗")
        for nm in names:
            item = f"「{POS_NAMES[idx]}」{nm}"
            if idx == mountain_idx:
                mountain_combos.append(item)
            else:
                other_combos.append(item)

    # —— 坐山判级（analyze_mountain 内与 score_feixing 同源）——
    mountain_analysis = None
    fx_score = fx_level = None
    if mountain_idx is not None:
        mountain_analysis = analyze_mountain(selected_mountain, data, offset_degree)
        fx_score = mountain_analysis['fx_score']
        fx_level = mountain_analysis['level']

    if mountain_analysis is not None:
        ma = mountain_analysis
        if fx_level == "大凶":
            summary = f"飞星大凶，建议另择他日：{ma['suggestion'].split('。')[0]}"
        elif fx_level == "凶":
            # 等级"凶"+断语"不取"时，综合文案语气必须一致（2026-09-13 用户纠正：
            # 旧文案"飞星偏弱，慎用"与"凶/不取"矛盾），"慎用"只保留给封顶级"平"
            summary = f"飞星凶，不取，宜另择他日：{ma['suggestion'].split('。')[0]}"
        elif fx_level == "大吉":
            if other_combos:
                summary = (f"坐山吉星汇聚，飞星大吉，可用；他宫另有 {len(other_combos)} 处凶格"
                           f"（修方避其方即可，不碍坐山）")
            else:
                summary = "坐山吉星汇聚，飞星大吉，可为重要日课备选"
        elif fx_level == "吉":
            summary = "飞星偏吉，坐山可用"
            if other_combos:
                summary += f"；他宫另有 {len(other_combos)} 处凶格，修方避之即可"
        else:
            if mountain_combos:
                summary = (f"飞星平：坐山方{'、'.join(mountain_combos)}，"
                           f"凶格在山，仅作平论，宜慎用")
            else:
                summary = "飞星平：坐山吉凶参半，需结合日课综合判断"
            if other_combos:
                summary += "；他宫另有凶格，修方避之"
        if ma['is_partial']:
            summary += "（兼向，分数已按替卦口径计）"
    else:
        summary = ("未选坐山：日课吉凶以坐山方年/月/日/时四盘为准，请先选择山向；"
                   "下列为全盘各方飞星提示")

    return {
        'summary': summary,
        'warnings': mountain_warnings + other_warnings,   # 兼容旧键
        'mountain_warnings': mountain_warnings,
        'other_warnings': other_warnings,
        'good_points': good_points,
        'bad_combos': mountain_combos + other_combos,      # 兼容旧键
        'mountain_combos': mountain_combos,
        'other_combos': other_combos,
        'score': fx_score if fx_score is not None else 0,
        'fx_score': fx_score,
        'fx_level': fx_level,
        'mountain_analysis': mountain_analysis,
    }


# ============================================================
#  数值评分（评分器加权/否决用）——规则与原 Scorer._calculate_feixing_score 逐行一致
# ============================================================
def score_feixing(sizhu, full_shan_xiang):
    """计算坐山方年/月/日/时四盘飞星的数值评分。

    Returns:
        dict: {feixing_score(-20~+20), feixing_level, feixing_details,
               feixing_comment, feixing_stars, feixing_star_count}
        None: 坐山无法识别 / 数据不足时跳过
    """
    try:
        year_zhi, month_zhi, day_zhi, hour_zhi, year_val, date_obj, year_gan = _extract_zhi(sizhu)
        if not all([year_zhi, month_zhi, day_zhi, hour_zhi]):
            return None
        if not year_val:
            return None

        # 提取坐山（按罗盘顺时针顺序取首个匹配，与原实现一致）
        mountain = None
        if full_shan_xiang:
            for m in MOUNTAINS_CW:
                if str(full_shan_xiang).startswith(m):
                    mountain = m
                    break
        if not mountain or mountain not in MOUNTAIN_TO_INDEX:
            return None

        is_partial = '兼' in (full_shan_xiang or '')

        grids = compute_stars(int(year_val), year_zhi, month_zhi, day_zhi,
                              hour_zhi, date_obj, year_gan=year_gan)
        year_grid = grids['year']['grid']
        month_grid = grids['month']['grid']
        day_grid = grids['day']['grid']
        hour_grid = grids['hour']['grid']

        idx = MOUNTAIN_TO_INDEX[mountain]
        pos_name = POS_NAMES[idx]
        star_list = [year_grid[idx], month_grid[idx], day_grid[idx], hour_grid[idx]]

        # 打分/判级统一走 _judge_mountain_stars（与窗口文字结论同源）
        _judge = _judge_mountain_stars(star_list, mountain, pos_name, is_partial)
        fx_score = _judge['fx_score']
        fx_level = _judge['fx_level']
        fx_comment = _judge['fx_comment']
        details = _judge['details']
        good_count = _judge['good_count']
        bad_count = _judge['bad_count']
        has_5 = _judge['has_5']
        has_2 = _judge['has_2']
        _combos = _judge['combos']

        stars_str = (f"年{STAR_NAMES[year_grid[idx] - 1]}"
                     f"月{STAR_NAMES[month_grid[idx] - 1]}"
                     f"日{STAR_NAMES[day_grid[idx] - 1]}"
                     f"时{STAR_NAMES[hour_grid[idx] - 1]}")

        # 结构化字段（2026-09-12 增，供吉日搜索等批量过滤；既有消费者不受影响）
        return {
            'feixing_score': fx_score,
            'feixing_level': fx_level,
            'feixing_details': details,
            'feixing_comment': fx_comment,
            'feixing_stars': stars_str,
            'feixing_star_count': f"吉星{good_count}颗，凶星{bad_count}颗",
            'stars_list': star_list,        # 年/月/日/时四盘到坐山星（1..9）
            'good_count': good_count,
            'bad_count': bad_count,
            'has_5': has_5,
            'has_2': has_2,
            'combos': _combos,              # 坐山方凶格名
            'mountain': mountain,
            'position': pos_name,
            'is_partial': is_partial,
        }
    except Exception as e:
        print(f"[飞星评分] 计算出错: {e}")
        return None
