# -*- coding: utf-8 -*-
"""
================================================================================
动作时序编排（001 §214 P2-A，纯函数层）
================================================================================
职责：给定某日 12 时辰逐时实评结果（反推引擎 hours）与动作段配置，
      穷举选出「3 个不相冲、按时序单调」的时辰分配方案。

边界（设计书 §三 / §八，用户拍板 Q1~Q6）：
    - 不碰评分、不碰神煞、不碰排序键（rank_day 零漂移）；
    - 纯函数，无 GUI、无 IO，单日 <1ms，不影响 30 天反推；
    - 候选池 = 反推逐时实评的 12 项（_compact_hour 产出）；
    - 冲命唯一源 = disabled（含冲新娘/新郎/阴胎/阳气），本层只做交叉校验；
    - 子时禁用（23:00 子时日柱已换日，四柱与时辰不配套）；
    - 缺段不补齐、不占位、不拉凶时充数；alt 只给错峰建议文案。

事实源约定：
    - 时辰记录字段：地支/时辰/时段/时柱/score/level/veto/disabled/shashi
      （反推引擎 _compact_hour，见 modules/反推引擎.py L60-L82）
    - 动作段配置：modules/事项标准.ACTION_SEQUENCES（唯一事实源）
================================================================================
"""

from itertools import combinations

# 十二地支 → 钟点起点（子时 23:00 排最后，保证时序单调）
_ZHI_START_HOUR = {
    '子': 23, '丑': 1, '寅': 3, '卯': 5, '辰': 7, '巳': 9,
    '午': 11, '未': 13, '申': 15, '酉': 17, '戌': 19, '亥': 21,
}

# 地支序（冲支计算用：年支 + 6 mod 12）
_ZHI_ORDER = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 民俗时间偏好权重（命中 ACTION_SEQUENCES[*]['prefer_zhis'] 时每段加此分，
# 仅用于选优排序，不写入 plan 展示的实际 score；非硬排除）
PREFER_BONUS = 20


def _start_hour(zhi):
    """地支 → 钟点起点；未知地支返回 0（不参与排序但不会崩溃）。"""
    return _ZHI_START_HOUR.get(str(zhi or ''), 0)


def _chong_zhi(year_zhi):
    """年支 → 冲支（年支 + 6 mod 12）；无效返回空串。"""
    yz = str(year_zhi or '')
    if yz not in _ZHI_ORDER:
        return ''
    return _ZHI_ORDER[(_ZHI_ORDER.index(yz) + 6) % 12]


def _extract_owner_zhis(owners):
    """从事主列表提取年支集合（兼容 '年支'/'year_zhi'/'生肖' 键名）。"""
    zhis = set()
    if not isinstance(owners, list):
        return zhis
    for _o in owners:
        if not isinstance(_o, dict):
            continue
        _z = (_o.get('年支') or _o.get('year_zhi')
              or _o.get('生肖') or '')
        _z = str(_z).strip()
        if _z in _ZHI_ORDER:
            zhis.add(_z)
    return zhis


def _is_candidate(h):
    """R1+R6 硬排除：disabled / veto>0 / score<=0 / shashi / 子时。"""
    if not isinstance(h, dict):
        return False
    if h.get('disabled'):
        return False
    if int(h.get('veto') or 0) > 0:
        return False
    if int(h.get('score') or 0) <= 0:
        return False
    if h.get('shashi'):
        return False
    if str(h.get('地支') or '') == '子':
        return False
    return True


def plan_actions(hours, owners=None, actions=None):
    """从 12 时辰实评中选出按时序单调的动作段分配方案。

    Args:
        hours: 反推引擎 _compact_hour 产出的 12 项列表（按子→亥时序）
        owners: 事主 dict 列表（仅用于冲命交叉校验，可空）
        actions: ACTION_SEQUENCES[event] 的动作段配置列表；
                 None 或空 → 返回 status='none' 空方案

    Returns:
        dict: {
            'plan': [{'seq','label','key','zhi','ganzhi','range','score','level','tags'}],
            'status': 'full' | 'partial' | 'insufficient' | 'none',
            'missing': [str],   # 缺失段的 label 列表
            'checks': [{'name','ok','detail'}],
            'alt': [{'label','suggest'}],
        }
    """
    actions = actions or []
    k = len(actions)
    empty = {
        'plan': [], 'status': 'none', 'missing': [a['label'] for a in actions],
        'checks': [], 'alt': [],
    }
    if k == 0:
        return empty

    # 候选池（R1+R6）
    cands = [h for h in (hours or []) if _is_candidate(h)]
    # 按钟点起点升序（R3）
    cands.sort(key=lambda h: _start_hour(h.get('地支')))

    n = len(cands)
    if n == 0:
        return empty

    # 段数上限 = min(k, n)
    seg_count = min(k, n)

    # 穷举 seg_count 个递增组合（R4 一辰一动作，按时钟点升序天然单调）
    best = None          # (sum_score, earliest_start, combo_tuple)
    best_seg = 0
    for seg in range(seg_count, 0, -1):
        found_this_seg = False
        for combo in combinations(range(n), seg):
            combo_hours = [cands[i] for i in combo]
            # 时序单调校验（理论上 sort 后 combinations 已单调，双保险）
            starts = [_start_hour(h.get('地支')) for h in combo_hours]
            if any(starts[i] >= starts[i + 1] for i in range(len(starts) - 1)):
                continue
            sum_score = sum(int(h.get('score') or 0) for h in combo_hours)
            # 民俗时间偏好加权：命中 actions[idx]['prefer_zhis'] 的段 +PREFER_BONUS
            # （仅用于选优排序，不写入 plan 的实际 score；非硬排除）
            prefer_bonus = 0
            for _idx, _h in enumerate(combo_hours):
                if _idx < len(actions):
                    _pref = actions[_idx].get('prefer_zhis') or []
                    if _pref and str(_h.get('地支') or '') in _pref:
                        prefer_bonus += PREFER_BONUS
            adjusted = sum_score + prefer_bonus
            earliest = starts[0]
            cand_key = (adjusted, -earliest)  # 同分取更早起点（更大 -earliest）
            if best is None or cand_key > best[0]:
                best = (cand_key, combo_hours)
                best_seg = seg
                found_this_seg = True
        # 找到该段数的最优解即停（段数优先：不往更少段降）
        if found_this_seg and best is not None:
            break

    if best is None or best_seg == 0:
        return empty

    chosen = best[1]
    # 状态分级
    if best_seg == k:
        status = 'full'
    elif best_seg == k - 1:
        status = 'partial'
    elif best_seg == 1:
        status = 'insufficient'
    else:
        status = 'partial'

    # 组装 plan（按 actions 顺序填前 best_seg 段）
    plan = []
    used_labels = set()
    for idx in range(best_seg):
        act = actions[idx]
        h = chosen[idx]
        zhi = str(h.get('地支') or '')
        ganzhi = str(h.get('时柱') or '')
        plan.append({
            'seq': act['seq'],
            'label': act['label'],
            'key': act['key'],
            'zhi': zhi,
            'ganzhi': ganzhi,
            'range': str(h.get('时段') or ''),
            'score': int(h.get('score') or 0),
            'level': str(h.get('level') or ''),
            'tags': list(h.get('凶') or []),
        })
        used_labels.add(act['label'])

    missing = [a['label'] for a in actions if a['label'] not in used_labels]

    # 交叉校验（R2）：对每个入选时辰，检查是否冲某事主年支但未标 disabled
    checks = []
    owner_zhis = _extract_owner_zhis(owners)
    if owner_zhis:
        cross_ok = True
        cross_detail = []
        for p in plan:
            chong = {_chong_zhi(yz) for yz in owner_zhis}
            if p['zhi'] in chong:
                cross_ok = False
                cross_detail.append(
                    '段「%s」时支 %s 冲事主年支（%s），但反推 disabled 未标'
                    % (p['label'], p['zhi'], '、'.join(sorted(chong))))
        checks.append({
            'name': 'cross_check',
            'ok': cross_ok,
            'detail': '；'.join(cross_detail) if cross_detail else '入选时辰均未冲命',
        })

    # 错峰建议（仅文案，不自动替换）
    alt = []
    if status != 'full' and missing:
        # 对每个缺失段，给一个"可怎么错峰"的提示（不虚构具体时辰）
        for ml in missing:
            alt.append({
                'label': ml,
                'suggest': '本日吉时不足，建议另择日或调整行程错峰（软件不自动以凶时充数）',
            })

    return {
        'plan': plan,
        'status': status,
        'missing': missing,
        'checks': checks,
        'alt': alt,
    }
