# -*- coding: utf-8 -*-
"""
================================================================================
排序键（时辰择优 / 日级反推排序的单一事实源）
================================================================================
建立目的（001 §210 Commit 1）：
    历史上"扫日推荐（_rescan_best_hour）"与"详情评分（_inject_best_hour_to_result）"
    各自维护一份 7 元组排序键，靠注释保证同口径；反推引擎若再写第三份，
    必然出现"自动推荐 88 分、点开详情 76 分"的口径分裂。
    本模块把 7 元组构造函数、分金预览、计分侧神煞清单、杀师判据、日级排序键
    全部单点化；主程序与反推引擎只调用这里的函数，禁止再各自拼元组。

约束：
    - 本模块只做"排序与分类"，不计算任何分值（分值一律来自 评分器.calculate_score）；
    - 本模块不 import 主程序/GUI，避免循环导入与 tkinter 依赖；
    - 任何字段顺序变更都属于行为变更，必须同步更新 tests/verify_210_search_top_n.py。
================================================================================
"""

# 计分侧神煞清单键（001 §178）：嫁娶分支先有 'shensha_list_scoring'，其余回退。
_SCORING_KEY = 'shensha_list_scoring'


def scoring_shensha(result):
    """计分侧神煞清单（001 §178，2026-10-25 拍板）。

    嫁娶两分支的展示清单已统一接入通用神煞检查器；计分侧（时辰择优的
    杀师/分金制化判据、block(6) 吉神制化）必须继续读改动前的清单
    'shensha_list_scoring'，保证计分零漂移。非嫁娶路径无该键，回退原键。
    """
    if isinstance(result, dict):
        _s = result.get(_SCORING_KEY)
        if isinstance(_s, list):
            return _s
        return result.get('shensha_list') or []
    return []


def shashi_hour(result):
    """杀师时判据（1=是，0=否）。杀师为匠艺时辰重煞(-30)，非否决，但平局时不取。"""
    for _s in scoring_shensha(result):
        if isinstance(_s, dict) and '杀师' in str(_s.get('name', '')):
            return 1
    return 0


def fenjin_preview_penalty(sx_full, nian, yue, ri, shi, yi_list, ssl):
    """分金复检预览（2026-09-11，原主程序同名函数迁入，逻辑逐字保持不变）。

    Returns:
        (level, deduct): 0=clean, 1=medium hit (deduct applied),
        2=severe without mitigation (veto)。与注入阶段 block(6) 同判据，
        使时辰排序不会优先选择稍后会被 (6) 扣罚的时辰。
    """
    try:
        if not sx_full or '山' not in sx_full:
            return 0, 0
        import importlib as _il
        _m24 = _il.import_module('modules.二十四山')
        _FJ = _m24.ZhengTiWuXingSelectorDB
        _fjs = _FJ()
        _sn = sx_full.split('山')[0].strip()
        if '兼' in sx_full:
            _jx = '兼' + sx_full.rsplit('兼', 1)[1][:1]
            _fjr = _fjs.evaluate_with_fengjin(_sn, _jx, nian, yue, ri, shi,
                                              use_fengjin_wuxing=True)
        else:
            _fjr = _fjs.evaluate_by_name(_sn, nian, yue, ri, shi)
        if not (isinstance(_fjr, dict) and _fjr.get('success', True)):
            return 0, 0
        _fs = _fjr.get('score', 0)
        _lvl = _fjr.get('level', '')
        _hit = _lvl in ('大凶', '凶(犯大煞)') or (
            isinstance(_fs, (int, float)) and _fs <= -30)
        if not _hit:
            return 0, 0
        _severe = isinstance(_fs, (int, float)) and _fs <= -50
        _good_qual = isinstance(ssl, list) and any(
            isinstance(_s, dict) and int(_s.get('score', 0) or 0) >= 10 for _s in ssl)
        _has_zhi = False
        if isinstance(yi_list, list):
            for _j in yi_list:
                _t = str(_j)
                if any(_kw in _t for _kw in
                       ['（有制化：', '天德', '月德', '岁德',
                        '天乙', '太阳', '太阴', '玉堂', '青龙']):
                    _has_zhi = True
                    break
        if not _has_zhi and _good_qual:
            _has_zhi = True
        if _severe and not _has_zhi:
            return 2, 100
        _deduct = 30 if _severe else (20 if _fs <= -40 else (15 if _fs <= -30 else 10))
        return 1, _deduct
    except Exception:
        # 二十四山模块缺失/参数异常时视为"无分金信息"，与历史行为一致
        # （此处不吞业务异常：分金预览失败即不加权，正分与否决仍由评分器决定）。
        return 0, 0


def hour_rank_key(*, disabled=False, veto_count=0, fenjin_level=0, fenjin_deduct=0,
                  ck_score=0, ck_weight=0, score=0, shashi=0, wuxing=0):
    """时辰择优排序键（越小越优），字段顺序为"否决 → 时辰表 → 总分 → 杂项"。

    字段（与 2026-09-17 方案C 的 7 元组逐位一致）：
        0 是否硬禁用时辰（五不遇时）          越大越差（0 优）
        1 否决数 + 分金重罚（fl==2 记 1）      越小越优
        2 时辰表分数 × 权重（仅嫁娶权重 1）    取负，使高分在前
        3 -(总分 - 分金中等扣罚预览)           取负
        4 杀师时                               0 优
        5 分金档                               0 优
        6 -五行原始分                           取负
    """
    return (1 if disabled else 0,
            int(veto_count) + (1 if fenjin_level == 2 else 0),
            -(int(ck_score) * int(ck_weight)),
            -(int(score) - (int(fenjin_deduct) if fenjin_level >= 1 else 0)),
            int(shashi), int(fenjin_level), -int(wuxing))


# ==================== 日级排序（反推引擎专用） ====================

# 主锚级吉神（用于"吉神契合度"排序，仅影响排名，不影响分值）。
# 权重与 事项标准.SHENSHA_SCORES 中同名分值对齐，便于解释"为什么排第一"。
MAIN_AUSPICIOUS = {
    '天赦': 25, '天德': 20, '月德': 18, '天德合': 15, '月德合': 12,
    '天愿': 12, '四相': 10, '时德': 10, '岁德': 15, '岁德合': 12,
    '天医': 12, '三奇日': 15, '三奇月': 12, '三奇星': 10,
}

# 慎用黄标阈值（001 §210 微调，2026-10-31 用户拍板方案 B）：
# 神煞负分总和 <= 该值 才染黄；单一轻扣（月虚 -10 之类）保持吉日红格。
CAUTION_DEDUCT_THRESHOLD = -20

# 吉神星级角标分档（展示用）：契合度 → 星数，39 分显示 3 颗星。
JISHEN_STAR_TIERS = ((60, 5), (45, 4), (30, 3), (20, 2), (10, 1))


def jishen_fit(result):
    """吉神契合度 = 命中主锚吉神加权和（展示侧清单，不做任何扣分/加分）。"""
    total = 0
    for _s in (result.get('shensha_list') or []):
        if isinstance(_s, dict):
            _n = str(_s.get('name', ''))
            if _n in MAIN_AUSPICIOUS and int(_s.get('score', 0) or 0) > 0:
                total += MAIN_AUSPICIOUS[_n]
    return total


def jishen_stars(fit):
    """吉神契合度 → 星数（0~5，展示角标用；39 → 3 星）。"""
    _fit = int(fit or 0)
    for _th, _n in JISHEN_STAR_TIERS:
        if _fit >= _th:
            return _n
    return 0


def deduct_items(result):
    """日级扣分主因清单：[(神煞名, 负分值)]，仅负分项，按原始顺序。

    用于"慎用原因列"展示（001 §210 微调 2026-10-31 拍板），
    不做任何分值计算，数据源与 classify_day 的扣分判据同源。
    """
    _out = []
    for _s in (result.get('shensha_list') or []):
        if isinstance(_s, dict):
            _v = int(_s.get('score', 0) or 0)
            if _v < 0:
                _out.append((str(_s.get('name', '')), _v))
    return _out


def deduct_sum(result):
    """神煞负分总和（正分不计），慎用判据的唯一分值来源。"""
    return sum(_v for _, _v in deduct_items(result))


def day_rank_key(result, event_type=''):
    """日级排序键（越小越优）：否决数 → 吉神契合度 → 总分（用户 §210 拍板）。

    "一票否决全排掉后，优先吉神契合度（如天德/月德），其次才看总分高低"。
    """
    return (len(result.get('veto_reasons') or []),
            -jishen_fit(result),
            -int(result.get('score') or 0))


def classify_day(result, event_type=''):
    """日级收录分类：'吉日' / '慎用' / '否决'。

    否决判据与主程序扫描"正常平分模式"的过滤链同源（主程序 L4323）：
      - 有 veto_reasons；
      - 总分 <= 0；
      - 等级含"凶"；
      - 忌列表含精确的"忌{事项}"。
    说明：扫描链路中的"不宜{事项}"与"大凶/绝对不可用"仅作诊断打印，
    不参与正常模式的收录过滤；故此处也不据此否决（既不否决，也不必然染黄，
    黄标只由下方"负分总和"判据决定），避免反推榜比手动扫日多排掉整日
    （2026-10-31 §210 口径对齐）。

    慎用（001 §210 微调，2026-10-31 用户拍板方案 B）：
      - 判据只看"神煞负分总和 <= -20"，且已被上面四条排除；
      - 单一轻扣（如月虚 -10）与"忌项"（如年三煞(月柱)）不再染黄，
        仅进原因列文字展示；忌项本身是否应扣分属规则面，另行立项。
    """
    import re
    _veto = list(result.get('veto_reasons') or [])
    _score = int(result.get('score') or 0)
    _level = str(result.get('level') or '')
    if _veto or _score <= 0 or '凶' in _level:
        return '否决'
    _re_ji = re.compile(rf'^忌{re.escape(event_type)}[。\s]?$') if event_type else None
    for _ji in (result.get('ji_list') or []):
        if _re_ji and _re_ji.search(str(_ji)):
            return '否决'
    return '慎用' if deduct_sum(result) <= CAUTION_DEDUCT_THRESHOLD else '吉日'


def rank_day(result, event_type=''):
    """反推榜排序键（越小越优）：收录层 → 否决数 → 吉神契合度 → 总分。

    收录层（§210 拍板）：吉日 0 → 慎用 1 → 否决 2。
    "慎用日必须入榜但降权"即由 tier 位实现：吉日恒慎用之前；
    同层内先比吉神契合度，再比总分。
    """
    _tier = {'吉日': 0, '慎用': 1, '否决': 2}[classify_day(result, event_type)]
    return (_tier,) + day_rank_key(result, event_type)


# ==================== 满分画像核验（001 §231/§233，纯展示） ====================

# 德神集（与 SHENSHA_SCORES 注册名一致；含动土的「天德日」变体）。
DEITY_NAMES = ('天德', '天德日', '天德合', '月德', '月德合', '岁德', '岁德合',
               '天赦', '天愿', '四相', '时德', '天医',
               '三奇日', '三奇月', '三奇星')

# 合局判据：评分类 details['地支关系'] 中的正向合局文案关键词。
_HE_PATTERNS = ('三合', '六合', '半合', '拱合')

# ---- 001 §233（2026-11-08 用户拍板）：事项定制判据 ------------------------
# 通用底线（所有事项必有）：得令、硬忌；中间三项按事项替换 1 项为专属核心项。
# 专属项数据源（全部为 calculate_score 既有产出，本模块只读不写）：
#   扶山补龙   shensha_list 名 ∈ _FUSHAN_NAMES 且 score>0（修造神煞扩展.py）
#   利月与吉日 shensha_list 名 ∈ _LIYUE_NAMES（嫁娶神煞.py：大利月/小利月/
#              周堂吉日/不将日）
#   全家相合   score_details['相主得分'] + ['相主详情'] 逐条尾部分值
#   仙命相合   score_details['仙命坐山得分'] + 仙命冲条目（评分器 §186/真冲）
#   出发方向   score_details['出行方位得分']（评分器 §201 出行方位通道）
_FUSHAN_NAMES = ('扶山', '补龙', '山家三合')
_LIYUE_NAMES = ('大利月', '小利月', '周堂吉日', '不将日')
# 与评分器 WANGMING_ROLES 同源（本模块不 import 评分器，保持轻量纯函数定位）
_WM_ROLES = ('死者', '亡命', '仙命', '亡人')

# 事项 → 专属核验项代码；未列出的事项走通用五维（相主）。
_EVENT_SPECIAL = {
    '修造': 'fushan', '动土': 'fushan',
    '嫁娶': 'liyue', '订婚': 'liyue', '纳采': 'liyue',
    '入宅': 'family', '移徙': 'family',
    '安葬': 'xianming',
    '出行': 'travel',
}

# 专属项代码 → 展示名
_SPECIAL_KEYS = {
    'fushan': '扶山补龙',
    'liyue': '利月与吉日',
    'family': '全家相合',
    'xianming': '仙命相合',
    'travel': '出发方向',
}


# ---- 001 §245（2026-11-09 用户拍板）：极品 / 上品 分档 --------------------
# 极品：日课校验 ERROR=0/WARN=0 **且** 详情页顶部决策面板为绿灯（✅ 吉课可用）。
# 上品：仅限动土事（修造/动土/装修/拆舍）——无否决、无「绝不豁免」重煞时，
#       允许鲁班煞、土王用事、向方三煞、五行偏枯等可制化小煞带黄牌入榜。
_DONGTU_EVENTS = frozenset({'修造', '动土', '装修', '拆舍'})
# 绝不豁免（命中即不得列上品）：伐日、克山、坐山三煞（三煞临山）、金神到山
_SHANGPIN_BLOCK_NAMES = ('伐日', '克山', '三煞临山', '金神到山')
# 可制化小煞（仅用于上品说明文案）
_SHANGPIN_ALLOW_NAMES = ('鲁班煞', '土王用事')


def _shangpin_scan(result):
    """动土事上品白名单扫描：返回 (阻断项, 可制化小煞说明项)。"""
    _r = result if isinstance(result, dict) else {}
    _blk, _allow = [], []
    _si = _r.get('sansha_info') or {}
    for _h in (_si.get('heavy_sha_names') or []):
        _s = str(_h)
        if any(_k in _s for _k in _SHANGPIN_BLOCK_NAMES):
            _blk.append(_s)
        else:
            _allow.append(_s)
    for _s in (_r.get('shensha_list') or []):
        if not isinstance(_s, dict):
            continue
        _n = str(_s.get('name') or _s.get('名称') or '')
        if any(_k in _n for _k in _SHANGPIN_ALLOW_NAMES):
            _allow.append(_n)
    _pk = str(_r.get('wuxing_pian_ku') or '')
    if _pk:
        # 001 §246：动土事差异化阈值——火/水 4/8 为轻度偏枯（火生土、可生扶山家，
        # 允许上品并提示）；≥5/8 判重度偏枯，踢出上品。
        _cnt = ((_r.get('score_details') or {}).get('偏枯计数') or {})
        _n = int(_cnt.get('火系' if _pk == '过燥' else '水系') or 0)
        _wx = '火' if _pk == '过燥' else '水'
        if _n >= 5:
            _blk.append('重度偏枯（%s%s%d/8）' % (_pk, _wx, _n))
        else:
            _allow.append('五行%s（%s%d/8，%s气稍旺，有助生扶山家，动土无妨）'
                          % (_pk, _wx, _n, _wx))
    return _blk, list(dict.fromkeys(_allow))


def profile_plan_keys(event_type=''):
    """该事项的满分核验维名称序列（UI 图例 / 手册共用）。

    专属事项（001 §238，2026-11-09 用户拍板）：得令 · 合局 · 德神 · <专属> ·
    相主 · 硬忌（6 项——专属项不再替换相主，两者都查）；
    通用事项：得令 · 合局 · 相主 · 德神 · 硬忌（§231 原序，5 项）。
    """
    _sp = _EVENT_SPECIAL.get(str(event_type or ''))
    if _sp:
        return ['得令', '合局', '德神', _SPECIAL_KEYS[_sp], '相主', '硬忌']
    return ['得令', '合局', '相主', '德神', '硬忌']


def _positive_hit(result, names):
    """shensha_list 中命中 names 且 score>0 的名称列表（保持 names 顺序去重）。"""
    _hit = []
    for _s in (result.get('shensha_list') or []):
        if not isinstance(_s, dict):
            continue
        _n = str(_s.get('name') or '')
        if _n in names and int(_s.get('score', 0) or 0) > 0 and _n not in _hit:
            _hit.append(_n)
    return _hit


def _xz_line_scores(details):
    """相主详情逐条尾部分值（格式 '……，±N分'）；提取不到分值的条目跳过。"""
    import re as _re
    _out = []
    for _t in details:
        _m = _re.findall(r'([+-]?\d+)\s*分', str(_t))
        if _m:
            _xz_line_scores_v = int(_m[-1])
            _out.append((str(_t), _xz_line_scores_v))
    return _out


def perfect_profile(result, owners=None, event_type='',
                    lucky_hours=None, bride_year_zhi=None):
    """满分画像核验（001 §231 通用五维 + §233 事项定制 + §238 六维）。

    通用底线（所有事项必有）：得令、硬忌；
    专属事项（001 §238，2026-11-09 用户拍板）：在专属核心项（扶山补龙/
    利月与吉日/全家相合/仙命相合/出发方向）之外保留「相主」，共 6 项——
    专属与相主两者都查，避免空事主时相主维度整列缺失；
    其余事项维持原通用 5 维（相主居中）。

    纯展示：只从 calculate_score 的既有产出（score_details / shensha_list /
    wu_xing_result.details / veto_reasons）提取，不新增任何分值或否决。

    Returns:
        {'items': [{'key','ok','detail'}]×N(5或6), 'marks': '✓✓✗✓✓',
         'ok_count': int, 'all_ok': bool, 'tips': [缺失项说明],
         'perfect': bool（日课校验无警告 + 顶部决策绿灯；001 §245）,
         'shangpin': bool（仅动土事的上品白名单；001 §245）}
    """
    _r = result if isinstance(result, dict) else {}
    _d = _r.get('score_details') or {}
    # 1) 得令：月令旺衰（+10 旺 / +5 相 / 0 休 / -5 囚 / -10 死）
    _wang = int((_d.get('月令详细') or {}).get('旺衰得分') or 0)
    _wang_desc = {10: '旺', 5: '相', 0: '休', -5: '囚', -10: '死'}.get(_wang, '')
    # 2) 合局：四柱地支三合 / 六合 / 半合 / 拱合
    _rels = (((_r.get('wu_xing_result') or {}).get('details') or {})
             .get('地支关系') or [])
    _he = next((str(_x) for _x in _rels
                if any(_p in str(_x) for _p in _HE_PATTERNS)), '')
    # 3) 相主：相主得分（须填写事主才有意义）
    _xz = int(_d.get('相主得分') or 0)
    _has_owner = bool(owners)
    _xz_details = list(_d.get('相主详情') or [])
    # 4) 德神：计分侧命中任一德神
    _deity = ''
    for _s in (_r.get('shensha_list') or []):
        if isinstance(_s, dict) and int(_s.get('score', 0) or 0) > 0:
            _n = str(_s.get('name') or '')
            if _n in DEITY_NAMES:
                _deity = _n
                break
    # 5) 硬忌：一票否决，或神煞负分合计达慎用阈值（≤-20）
    _veto = [str(_v) for _v in (_r.get('veto_reasons') or [])]
    _ded = deduct_sum(_r)

    _item_wangling = {'key': '得令', 'ok': _wang > 0,
                      'detail': ('月令%s（%+d）' % (_wang_desc, _wang)) if _wang > 0
                      else ('月令%s（%+d），未得令' % (_wang_desc or '休', _wang))}
    _item_heju = {'key': '合局', 'ok': bool(_he),
                  'detail': _he if _he else '地支无三合/六合/半合'}
    _item_deshen = {'key': '德神', 'ok': bool(_deity),
                    'detail': ('命中「%s」' % _deity) if _deity
                    else '未命中天德/月德/岁德/天赦等德神'}
    _item_yingji = {'key': '硬忌',
                    'ok': (not _veto) and _ded > CAUTION_DEDUCT_THRESHOLD,
                    'detail': ('一票否决：' + '；'.join(_veto)) if _veto
                    else ('神煞负分合计 %d（≤%d）' % (_ded, CAUTION_DEDUCT_THRESHOLD))
                    if _ded <= CAUTION_DEDUCT_THRESHOLD else '无硬忌/重扣'}
    _item_xiangzhu = {'key': '相主',
                      'ok': (_xz > 0) and _has_owner,
                      'na': (not _has_owner),
                      'detail': ('相主 %+d 分' % _xz) if (_xz > 0 and _has_owner)
                      else ('未填写事主，无法核验相主适配性' if not _has_owner
                            else '相主无生合加分')}

    # ---- 事项专属核心项（001 §233）----
    _sp = _EVENT_SPECIAL.get(str(event_type or ''))
    _item_sp = None
    if _sp == 'fushan':
        _hit = _positive_hit(_r, _FUSHAN_NAMES)
        _item_sp = {'key': '扶山补龙', 'ok': bool(_hit),
                    'detail': ('命中「%s」' % '、'.join(_hit)) if _hit
                    else '未生扶坐山（扶山/补龙/山家三合均无加分）'}
    elif _sp == 'liyue':
        _hit = _positive_hit(_r, _LIYUE_NAMES)
        _item_sp = {'key': '利月与吉日', 'ok': bool(_hit),
                    'detail': ('命中「%s」' % '、'.join(_hit)) if _hit
                    else '大利月/小利月/周堂/不将日均未命中'}
    elif _sp == 'family':
        if not _has_owner:
            _item_sp = {'key': '全家相合', 'ok': False, 'na': True,
                        'detail': '未填写事主，无法核验相主适配性'}
        else:
            _hard = [str(_t) for _t in _xz_details if str(_t).startswith('[硬性门槛]')]
            _neg = [(_t, _v) for _t, _v in _xz_line_scores(_xz_details) if _v < 0]
            _ok_f = (_xz >= 0) and not _hard and not _neg
            if _ok_f:
                _det_f = '全家相主 %+d 分，无冲' % _xz
            elif _hard:
                _det_f = '含冲命：' + _hard[0]
            elif _neg:
                _det_f = '%d 位事主相主扣分（最低 %+d 分）' % (
                    len(_neg), min(_v for _t, _v in _neg))
            else:
                _det_f = '相主合计 %+d 分' % _xz
            _item_sp = {'key': '全家相合', 'ok': _ok_f, 'detail': _det_f}
    elif _sp == 'xianming':
        _has_wm = any(isinstance(_o, dict)
                      and str(_o.get('role') or '') in _WM_ROLES
                      for _o in (owners or []))
        if not _has_wm:
            _item_sp = {'key': '仙命相合', 'ok': False, 'na': True,
                        'detail': '未填写仙命（死者卡），无法核验'}
        else:
            _sz = int(_d.get('仙命坐山得分') or 0)
            _chong = ([str(_t) for _t in _xz_details
                       if ('真冲' in str(_t) or '冲坐山' in str(_t))]
                      + [str(_v) for _v in _veto
                         if '仙命' in str(_v) and '冲' in str(_v)])
            if _d.get('仙命冲坐山六冲') is not None:
                _chong.append('仙命冲坐山六冲 %+d 分'
                              % int(_d.get('仙命冲坐山六冲') or 0))
            _ok_x = (_sz >= 0) and not _chong
            if _ok_x:
                _det_x = '仙命与坐山相合（%+d），无冲无克' % _sz
            elif _chong:
                _det_x = '仙命犯冲：' + _chong[0]
            else:
                _det_x = ('坐山克仙命（%+d）' % _sz) if _sz <= -30 \
                    else ('仙命克坐山（%+d）' % _sz)
            _item_sp = {'key': '仙命相合', 'ok': _ok_x, 'detail': _det_x}
    elif _sp == 'travel':
        _tds = int(_d.get('出行方位得分') or 0)
        _item_sp = {'key': '出发方向', 'ok': _tds >= 0,
                    'detail': ('出行方位吉（%+d）' % _tds) if _tds > 0
                    else ('未犯煞' if _tds == 0
                          else '出行方位犯煞（%+d）' % _tds)}

    if _item_sp is not None:
        # 001 §238：专属事项 6 项——专属项（索引3）与相主（索引4）都查
        _items = [_item_wangling, _item_heju, _item_deshen, _item_sp,
                  _item_xiangzhu, _item_yingji]
    else:
        _items = [_item_wangling, _item_heju, _item_xiangzhu, _item_deshen,
                  _item_yingji]
    _ok = sum(1 for _i in _items if _i.get('ok'))
    _any_na = any(_i.get('na') for _i in _items)
    # 001 §240：极品口径改为「日课校验无警告」——即详情页【日课校验】结论为
    # ✅ 通过（ERROR=0 且 WARN=0）。五项满分核验仅作展示与分档，不再决定极品。
    _lint_ok = False
    _lint_note = ''
    try:
        from modules.日课校验器 import lint_lesson
        # 001 §243：主程序结果表 detail 通常不带 lucky_hours / bride_year_zhi，
        #   导致 E003(利月)/E004(时辰) 等关键规则被跳过、perfect 恒为 True。
        #   优先使用调用方传入的 lucky_hours / bride_year_zhi；未传则回退
        #   detail 自带值，再不行从 owners 提取新娘/事主年支。
        _lh = lucky_hours
        if _lh is None:
            _lh = _r.get('lucky_hours') if isinstance(_r, dict) else None
        _byz = bride_year_zhi
        if _byz is None:
            for _o in (owners or []):
                if isinstance(_o, dict):
                    _role = str(_o.get('role') or _o.get('身份') or '')
                    if _role in ('新娘', '事主'):
                        _yz = _o.get('year_zhi') or _o.get('年支')
                        if _yz:
                            _byz = str(_yz)
                            break
        _lr = lint_lesson(_r, lucky_hours=_lh, bride_year_zhi=_byz)
        _lint_ok = (not _lr.has_error) and _lr.warn_count == 0
        if _lint_ok:
            _lint_note = '日课校验通过（%d 项规则，无警告）' % len(_lr.executed_ids)
        elif _lr.has_error:
            _lint_note = '日课校验未通过：%d 项错误' % _lr.error_count
        else:
            _lint_note = '日课校验有 %d 项警告' % _lr.warn_count
    except Exception as _e:
        _lint_note = '日课校验未执行：%s' % _e

    # 001 §245（2026-11-09 用户拍板）：极品再收口——除「日课校验无警告」外，
    # 还须详情页顶部决策面板为绿灯。此处与详情窗调用同一 build_decision_report、
    # 同一 score_details 输入，避免「榜单一套、详情一套」的货不对板。
    # 动土事（修造/动土/装修/拆舍）另设「上品」白名单：无否决且无伐日/克山/
    # 三煞临山/金神到山时，允许鲁班煞、土王用事、向方三煞、偏枯带黄牌入榜。
    _dec_key, _dec_reason = '', ''
    try:
        from modules.决策分析 import build_decision_report
        _dec = build_decision_report(_r if isinstance(_r, dict) else {},
                                     event_type)
        _dec_key = str(_dec.get('verdict_key') or '')
        _dec_reason = str(_dec.get('verdict_reason') or '')
    except Exception as _e:
        _dec_reason = '决策面板未执行：%s' % _e
    _dec_ok = (_dec_key == 'ok')
    _blk, _allow = _shangpin_scan(_r)
    _veto = [str(_v) for _v in ((_r or {}).get('veto_reasons') or [])]
    _tier = 'none'
    if _lint_ok and _dec_ok:
        _tier = 'perfect'
    elif (_lint_ok and str(event_type or '') in _DONGTU_EVENTS
          and not _veto and not _blk):
        _tier = 'shangpin'
    if _lint_ok:
        if _tier == 'perfect':
            _lint_note = ('日课校验通过（%d 项规则，无警告），顶部决策绿灯'
                          '（✅ 吉课可用）' % len(_lr.executed_ids))
        elif _tier == 'shangpin':
            _lint_note = ('上品（动土可制化）：本日含动土常态小煞（%s），'
                          '不属于无瑕极品，但可经现场祭拜制化后安全使用'
                          % ('、'.join(_allow) or '慎用黄牌'))
        else:
            _lint_note = ('日课校验通过（%d 项规则，无警告），但顶部决策为「%s」：%s'
                          % (len(_lr.executed_ids),
                             '慎用·需制化' if _dec_key == 'warn' else '不可用',
                             _dec_reason or '—'))
    return {
        'items': _items,
        'marks': ''.join('✓' if _i.get('ok')
                         else ('-' if _i.get('na') else '✗')
                         for _i in _items),
        'ok_count': _ok,
        'all_ok': (not _any_na) and _ok == len(_items),
        'lint_ok': _lint_ok,
        'lint_note': _lint_note,
        'perfect': _tier == 'perfect',
        'shangpin': _tier == 'shangpin',
        'tier': _tier,
        'decision_key': _dec_key,
        'tips': ['%s：%s' % (_i['key'], _i['detail'])
                 for _i in _items if not _i.get('ok')],
    }
