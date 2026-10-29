# -*- coding: utf-8 -*-
"""
出行方位吉凶（001 §201 Commit2，2026-10-30 用户拍板）

口径：出行没有固定"坐山"，方位判定一律以用户填写的「出发方向」为准。
轻权重、通用启用（不限元旦/远行场景），未填出发方向则不加不扣。

三库依据（取证全文见 docs/出行方位三库取证报告_20261030.md）：
  · 陈书 p757：「元旦出行：宜向天月二德天道及喜神所在之方出行吉；
    忌鹤神日游方，不宜从此方出行」
  · 协纪 279252：「天德方即天道方」；279251：「正丁二坤之类为天德……
    本月之旺方为金匮星临官帝旺之间为月德」（月德＝三合月官旺之间）
  · 协纪 279223/279238-279248：「天德在X / 月德在Y」逐月条文与下表一致
  · 协纪 279221：「出行则不宜犯鹤神」（鹤神六十日起例）
  · 岁破方/太岁方：三库仅作修方禁忌，出行语境 0 处 → 本通道不纳入（C4）

分值（用户拍板区间 +5～+8 / −5）：
  · 吉方：天德方（含同方之天道方）+8、月德方 +8、喜神方 +5，合计封顶 +8；
  · 凶方：鹤神方 / 日游方 −5；二者同方（己酉起 44 日出游期）时只计一次。
"""

# ============================================================================
# 一、八方位与二十四山/八卦的对应
# ============================================================================
DIR8 = ('正北', '东北', '正东', '东南', '正南', '西南', '正西', '西北')

# 二十四山 → 八方位（每方三山：壬子癸/丑艮寅/甲卯乙/辰巽巳/丙午丁/未坤申/庚酉辛/戌乾亥）
_SHAN_TO_DIR8 = {
    '壬': '正北', '子': '正北', '癸': '正北',
    '丑': '东北', '艮': '东北', '寅': '东北',
    '甲': '正东', '卯': '正东', '乙': '正东',
    '辰': '东南', '巽': '东南', '巳': '东南',
    '丙': '正南', '午': '正南', '丁': '正南',
    '未': '西南', '坤': '西南', '申': '西南',
    '庚': '正西', '酉': '正西', '辛': '正西',
    '戌': '西北', '乾': '西北', '亥': '西北',
}

# 八卦 → 八方位
_GUA_TO_DIR8 = {
    '坎': '正北', '艮': '东北', '震': '正东', '巽': '东南',
    '离': '正南', '坤': '西南', '兑': '正西', '乾': '西北',
}

# 单字简称（北/东/南/西）
_DIR8_SHORT = {'北': '正北', '东': '正东', '南': '正南', '西': '正西'}


def normalize_direction(raw):
    """把用户输入的方向（八方位/简称/八卦/二十四山单字/带"方"后缀）归一为八方位。

    无法识别或为空 → None（由调用方按"未填出发方向"处理）。
    """
    txt = str(raw or '').strip()
    if not txt:
        return None
    base = txt.split('兼')[0].strip()          # 兼容误传的"X山Y向兼Z"串
    if not base:
        return None
    if base in DIR8:
        return base
    if base in _DIR8_SHORT:
        return _DIR8_SHORT[base]
    if len(base) == 1:
        return _SHAN_TO_DIR8.get(base) or _GUA_TO_DIR8.get(base)
    for d in DIR8:                              # "正南方""东南方"等带后缀写法
        if base.startswith(d):
            return d
    return None


# ============================================================================
# 二、天德方（＝天道方，按月支）
# ============================================================================
_TIANDE_BY_MONTH_ZHI = {
    '寅': '正南', '卯': '西南', '辰': '正北', '巳': '正西',
    '午': '西北', '未': '正东', '申': '正北', '酉': '东北',
    '戌': '正南', '亥': '正东', '子': '东南', '丑': '正西',
}
# 天德所居之干/维（展示用原文用字）
_TIANDE_LABEL = {
    '寅': '丁', '卯': '坤', '辰': '壬', '巳': '辛',
    '午': '乾', '未': '甲', '申': '癸', '酉': '艮',
    '戌': '丙', '亥': '乙', '子': '巽', '丑': '庚',
}


def tiande_direction(month_zhi):
    return _TIANDE_BY_MONTH_ZHI.get(month_zhi)


# ============================================================================
# 三、月德方（三合月官旺之间，按月支）
# ============================================================================
_YUEDE_BY_MONTH_ZHI = {
    '寅': '正南', '午': '正南', '戌': '正南',   # 寅午戌火局 → 丙（正南）
    '申': '正北', '子': '正北', '辰': '正北',   # 申子辰水局 → 壬（正北）
    '亥': '正东', '卯': '正东', '未': '正东',   # 亥卯未木局 → 甲（正东）
    '巳': '正西', '酉': '正西', '丑': '正西',   # 巳酉丑金局 → 庚（正西）
}


def yuede_direction(month_zhi):
    return _YUEDE_BY_MONTH_ZHI.get(month_zhi)


# ============================================================================
# 四、喜神方（按日干；与 modules/今日黄历.py 的 XI_SHEN 同表）
# ============================================================================
_XISHEN_BY_DAY_GAN = {
    '甲': '东北', '己': '东北',
    '乙': '西北', '庚': '西北',
    '丙': '西南', '辛': '西南',
    '丁': '正南', '壬': '正南',
    '戊': '东南', '癸': '东南',
}


def xishen_direction(day_gan):
    return _XISHEN_BY_DAY_GAN.get(day_gan)


# ============================================================================
# 五、鹤神方（按日，六十甲子起例）——协纪 279221 原文
# ============================================================================
_GANS = '甲乙丙丁戊己庚辛壬癸'
_ZHIS = '子丑寅卯辰巳午未申酉戌亥'
_JIAZI_60 = [_GANS[i % 10] + _ZHIS[i % 12] for i in range(60)]

# 起例（原文：甲子乙丑在东南（辰巽巳）→ 丙寅起五日正南 → 六日西南 →
# 五日正西 → 六日西北 → 五日正北尽于壬辰 → 癸巳至戊申十六日鹤神上天（无方）
# → 己酉出东北六日 → 正东五日 → 东南四日尽于癸亥 → 甲子乙丑复起巳）
_HESHEN_SEGMENTS = (
    (0, 1, '东南'),      # 甲子、乙丑
    (2, 6, '正南'),      # 丙寅…庚午（5日）
    (7, 12, '西南'),     # 辛未…丙子（6日）
    (13, 17, '正西'),    # 丁丑…辛巳（5日）
    (18, 23, '西北'),    # 壬午…丁亥（6日）
    (24, 28, '正北'),    # 戊子…壬辰（5日）
    (29, 44, None),      # 癸巳…戊申（16日）鹤神上天，无方位
    (45, 50, '东北'),    # 己酉…甲寅（6日）
    (51, 55, '正东'),    # 乙卯…己未（5日）
    (56, 59, '东南'),    # 庚申…癸亥（4日）
)


def _seg_lookup(segments, idx):
    for lo, hi, val in segments:
        if lo <= idx <= hi:
            return val
    return None


def heshend_direction(day_ganzhi):
    """鹤神所在方位（八方位）；上天十六日返回 None。"""
    if day_ganzhi not in _JIAZI_60:
        return None
    return _seg_lookup(_HESHEN_SEGMENTS, _JIAZI_60.index(day_ganzhi))


# ============================================================================
# 六、日游神（按日）——协纪 279221 原文
# ============================================================================
# 癸巳…丁酉房内北 → 戊戌己亥房内中 → 庚子辛丑壬寅房内南 → 癸卯房内西 →
# 甲辰…丁未房内东 → 戊申又在中 → 己酉出游四十四日（其方与鹤神同）
_RIYOU_INDOOR = (
    (29, 33, '房内北'),
    (34, 35, '房内中'),
    (36, 38, '房内南'),
    (39, 39, '房内西'),
    (40, 43, '房内东'),
    (44, 44, '房内中'),
)


def riyou_state(day_ganzhi):
    """返回 {'kind': 'indoor'|'outdoor', 'label': ..., 'direction': ...}，无法识别返回 None。"""
    if day_ganzhi not in _JIAZI_60:
        return None
    idx = _JIAZI_60.index(day_ganzhi)
    indoor = _seg_lookup(_RIYOU_INDOOR, idx)
    if indoor:
        return {'kind': 'indoor', 'label': indoor, 'direction': None}
    return {'kind': 'outdoor', 'label': '', 'direction': heshend_direction(day_ganzhi)}


# ============================================================================
# 七、综合判定
# ============================================================================
_JI_CAP = 8          # 吉方合计封顶（用户拍板区间 +5～+8）
_XIONG_SCORE = 5     # 凶方 -5


def evaluate(direction, sizhu):
    """按"出发方向"给出出行方位吉凶轻权重。

    Args:
        direction: 用户填写的出发方向（任意可归一写法）
        sizhu: 四柱信息（需 month_zhi / day_gan / day_zhi）

    Returns:
        dict: {
            'direction': 归一后的八方位或 None,
            'score': 本通道总分（吉正凶负，未填方向恒 0）,
            'ji_items': 命中吉方明细（含分值与典据说明）,
            'xiong_items': 命中凶方明细,
            'details': 全量参照（本例各吉凶方实际所在，供详情对账）,
            'note': 未填方向时的说明文案,
        }
    """
    out = {'direction': None, 'score': 0, 'ji_items': [], 'xiong_items': [],
           'details': {}, 'note': ''}

    d = normalize_direction(direction)
    out['direction'] = d
    if not d:
        out['note'] = '未填出发方向，方位吉凶不参与计分'
        return out

    month_zhi = str((sizhu or {}).get('month_zhi', '') or '')
    day_gan = str((sizhu or {}).get('day_gan', '') or '')
    day_zhi = str((sizhu or {}).get('day_zhi', '') or '')
    gz = day_gan + day_zhi

    td = tiande_direction(month_zhi)
    yd = yuede_direction(month_zhi)
    xs = xishen_direction(day_gan)
    hs = heshend_direction(gz)
    ry = riyou_state(gz) or {}
    ry_dir = ry.get('direction')

    out['details'] = {
        '天德方（天道方）': td,
        '月德方': yd,
        '喜神方': xs,
        '鹤神方': hs,
        '日游方': ry_dir if ry.get('kind') == 'outdoor' else '（%s）' % ry.get('label', ''),
    }

    # ---- 吉方 ----
    ji = []
    if td and td == d:
        ji.append(('天德方（天道方）', 8,
                   '月支%s·天德在%s' % (month_zhi, _TIANDE_LABEL.get(month_zhi, ''))))
    if yd and yd == d:
        ji.append(('月德方', 8, '月支%s·月德在三合官旺之间' % month_zhi))
    if xs and xs == d:
        ji.append(('喜神方', 5, '日干%s·喜神在此方' % day_gan))
    _ji_score = min(sum(w for _, w, _ in ji), _JI_CAP)
    for name, w, why in ji:
        out['ji_items'].append('%s（+%d分·%s）' % (name, w, why))

    # ---- 凶方 ----
    xiong_hit = False
    if hs and hs == d and ry.get('kind') == 'outdoor' and ry_dir == d:
        out['xiong_items'].append('鹤神方/日游方（同方）（-%d分·日支%s）' % (_XIONG_SCORE, gz))
        xiong_hit = True
    else:
        if hs and hs == d:
            out['xiong_items'].append('鹤神方（-%d分·日支%s）' % (_XIONG_SCORE, gz))
            xiong_hit = True
        if ry.get('kind') == 'outdoor' and ry_dir == d:
            out['xiong_items'].append('日游方（-%d分·日支%s）' % (_XIONG_SCORE, gz))
            xiong_hit = True

    out['score'] = _ji_score - (_XIONG_SCORE if xiong_hit else 0)
    return out
