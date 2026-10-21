# -*- coding: utf-8 -*-
"""
制化引擎（表驱动·第一批）
================================================================================
矩阵锚：docs/制化矩阵_协纪明文十条_20261021.md（#9 大时丑未支 / #13 厌对 / #15 五墓）
立项锚：docs/制化矩阵落地立项_20261021.md §3-A（德并聚合）/§3-C（映射表）/§3-E（新模块）
判据冻结：001 §155（用户 2026-10-21 拍板六项）：
  1) 止忌子集事项映射表配置化（ZHIJI_EVENT_MAPPING），不得在判断逻辑里写死事项名；
  2) 「军事」在 15 事项体系为空集 → 止忌军事支落地效果=全免，但必须显式输出
     警示【已豁免：原止忌事项(军事)不在当前业务通道内】；未来若增设军事/演武
     通道，只需扩充映射表，止忌自动激活；
  3) 相抵型（大时子午卯酉月德并支）典无力度原文，绝不凭空捏造减半逻辑，
     暂不落地，挂轻重层专项（ZHIHUA_WEIGHT_PENDING_BRANCHES 登记）；
  4) 德神参与制化的吉神集为六神封闭集（矩阵 §3.3），各条目所引子集不同，
     不得自动延伸；天恩不在集内（卷十天恩条「不得与德合赦愿比」，取证稿 §1.1）；
  5) 禁并排除对（矩阵 §3.1）：天赦天愿不得与月破并；天愿不得与厌对并
     （厌对行经 DE_GODS_WUDE 结构性排除天愿；月破行本批不改码，登记备查）。

红线（立项书 §1.1）：德神判定统一走基类单点谓词；子类 override（通用/修造/
入宅/嫁娶）与基类单点经 2026 全年 15 事项×6 谓词×366 日逐日比对零分歧
（2026-10-21 实证，制化第一批 verify 脚本延续断言）。
================================================================================
"""

# ==================== §1 止忌子集事项映射表（判据冻结·配置化） ====================
# 键=协纪典载止忌事项名；值=软件 15 事项体系中的仍忌通道集（空集=该典载事项
# 在当前业务空间无对应通道）。增减通道时只改本表，不改判断逻辑。
# - 军事：现代民用软件无军事/演武通道 → 空集（空集豁免须附警示文案，
#   见 MILITARY_EMPTY_NOTE）；
# - 缓刑：无对应通道 → 空集；
# - 疗病：映射「求医」（卷十忌列「求医疗病」）；
# - 破屋坏垣：映射「拆舍」（沿用 x4 批 (b) 判据先例，001 §126/§127）。
ZHIJI_EVENT_MAPPING = {
    '军事': frozenset(),
    '缓刑': frozenset(),
    '疗病': frozenset({'求医'}),
    '破屋坏垣': frozenset({'拆舍'}),
}

# ==================== §2 德神封闭集（矩阵 §3.3） ====================
# 六神封闭集：天德、月德、天德合、月德合、天赦、天愿。不得自动延伸；
# 天恩不在集内（矩阵 §3：唯天恩条明文「不得与德合赦愿比」，天恩非德神制化集成员）。
DE_GODS_ALL = ('天德', '月德', '天德合', '月德合', '天赦', '天愿')
# 厌对五德集（矩阵 #13 卷十原文「与天德月德天德合月德合天赦并则不忌」）：
# 六神 − 天愿（禁并排除对「天愿不得与厌对并」结构性落地）。
DE_GODS_WUDE = ('天德', '月德', '天德合', '月德合', '天赦')
# 大时丑未支「二德并」（矩阵 #9 卷十原文「丑未月与二德并，止忌军事」）：
# 最严判读=天德+月德同时并临（合日不替代、单德不算；无证据不放宽，
# 001 §155 判读冻结，验收待复核）。
DE_GODS_ERDE = ('天德', '月德')

assert '天恩' not in DE_GODS_ALL, '天恩不在德神制化集内（矩阵 §3.3 红线）'

# ==================== §3 禁并排除对（矩阵 §3.1，登记） ====================
# 键=凶煞名；值=遇到该凶煞时不参与制化的德神集。
# 厌对行已由 DE_GODS_WUDE 结构性排除；月破行本批不改码（犹忌负条款，
# 矩阵 #1），此对登记备查，月破行未来落地时启用。
FORBIDDEN_PAIRS = {
    '月破': ('天赦', '天愿'),
    '厌对': ('天愿',),
}

# ==================== §4 相抵支挂账登记（轻重层专项） ====================
# 典无力度原文（矩阵 #9 子午卯酉支「吉凶相抵」无分值明文），绝不凭空捏造
# 减半逻辑，暂不落地（001 §155 拍板6）。键名供五层总表/001 引用。
ZHIHUA_WEIGHT_PENDING_BRANCHES = {
    '大时·子午卯酉月德并相抵支': '典无力度原文，挂轻重层专项统一裁断（001 §155）',
}

# ==================== §5 豁免注记文案（用户可见，单点维护） ====================
# 豁免注记行的注册键（各发射点统一用键名，保证 _add_shensha 同名去重不被
# 死分支复活——修造/开业/安葬等子类重复发射行在基类豁免日不再发射'大时'/
# '五墓'正名，若子类仍发射正名将复活 -12，故子类行必须同步接线同键名）
DASHI_EXEMPT_KEY = '大时·制化豁免'
WUMU_EXEMPT_KEY = '五墓·制化豁免'
YANDUI_EXEMPT_KEY = '厌对·制化豁免'
# 大时·丑未支（止忌军事→映射空集→全免，警示文案为拍板2 硬性要求）
MILITARY_EMPTY_NOTE = '【已豁免：原止忌事项(军事)不在当前业务通道内（大时·丑未月二德并，矩阵#9）】'
# 五墓·午子支（全不忌）
WUMU_EXEMPT_NOTE = '【已豁免：五月(午)/十一月(子)与月德并，典载不忌（五墓·矩阵#15）】'
# 厌对·五德全豁免（全不忌）
YANDUI_EXEMPT_NOTE = '【已豁免：与天德月德天德合月德合天赦并，典载不忌（厌对·矩阵#13）】'


# ==================== §6 德并聚合函数（立项书 §3-A） ====================
_PRED_CHECKER = None


def _get_predicate_checker():
    """德神谓词载体：惰性导入神煞基类（避免循环导入），模块级缓存单例。

    基类 __init__ 零依赖（仅 shensha_list=[]），谓词均为 sizhu 纯函数；
    不用调用方 checker 实例，保证全通道走基类单点（立项书 §1.1 红线）。
    """
    global _PRED_CHECKER
    if _PRED_CHECKER is None:
        try:
            from .神煞基类 import ShenShaChecker
        except ImportError:
            from 神煞基类 import ShenShaChecker
        _PRED_CHECKER = ShenShaChecker()
    return _PRED_CHECKER


def get_de_gods(sizhu, allow=DE_GODS_ALL):
    """返回当日命中的德神集（frozenset），判定走基类单点谓词。

    Args:
        sizhu: 四柱 dict（day_gan/day_zhi/month_zhi 等）
        allow: 参与制化的德神子集（矩阵：各条目所引德神集不同，不得自动延伸；
               越界即 AssertionError，防调用方擅自扩大豁免面）

    Returns:
        frozenset: 当日命中的德神名集合（⊂ allow ⊂ DE_GODS_ALL）
    """
    unknown = [g for g in allow if g not in DE_GODS_ALL]
    assert not unknown, '制化引擎：德神越界 %s（封闭集不得自动延伸，矩阵 §3.3）' % unknown
    c = _get_predicate_checker()
    gods = set()
    if '天德' in allow and c._is_tiande(sizhu):
        gods.add('天德')
    if '天德合' in allow and c._is_tiande_he(sizhu):
        gods.add('天德合')
    if '月德' in allow and c._is_yuede(sizhu):
        gods.add('月德')
    if '月德合' in allow and c._is_yuede_he(sizhu):
        gods.add('月德合')
    if '天赦' in allow and c._is_tianshe(sizhu):
        gods.add('天赦')
    if '天愿' in allow and c._is_tianyuan(sizhu):
        gods.add('天愿')
    return frozenset(gods)


def map_zhiji_events(canonical_names):
    """典载止忌事项名集 → 软件仍忌通道集（配置化映射，判据冻结 §1）。

    Returns:
        frozenset: 仍忌的软件事项通道集；
        None: 映射表缺项（保守不豁免——无证据不放宽，禁止静默放行）。
    """
    out = set()
    for n in canonical_names:
        if n not in ZHIJI_EVENT_MAPPING:
            return None
        out |= set(ZHIJI_EVENT_MAPPING[n])
    return frozenset(out)


# ==================== §7 三处豁免判定（第一批：#9/#13/#15） ====================

def eval_dashi_chouwei_exempt(sizhu, event):
    """矩阵 #9 大时丑未支：丑未月与二德并（天德+月德同时）→止忌军事。

    军事经 ZHIJI_EVENT_MAPPING 映射为空集 → 当前事项不在仍忌集 → 全免，
    附警示文案（拍板2 硬性要求）。

    Args:
        sizhu: 四柱 dict
        event: 当前事项（_std_event；经 canonical_event 规范化后比对仍忌集）

    Returns:
        (bool, str): (是否豁免, 豁免注记文案；不豁免时为空串)
    """
    if sizhu.get('month_zhi') not in ('丑', '未'):
        return False, ''
    if get_de_gods(sizhu, allow=DE_GODS_ERDE) != frozenset(DE_GODS_ERDE):
        return False, ''
    still = map_zhiji_events(('军事',))
    if still is None:
        return False, ''
    try:
        from ..事项标准 import canonical_event
    except ImportError:
        from 事项标准 import canonical_event
    if canonical_event(event) in still:
        return False, ''
    return True, MILITARY_EMPTY_NOTE


def eval_wumu_exempt(sizhu):
    """矩阵 #15 五墓：五月(午)、十一月(子)与月德并则不忌。

    德神集=仅月德（卷六原文「与月德并」，不含月德合/天德——无证据不放宽，
    001 §155 判读冻结）。

    Returns:
        bool
    """
    if sizhu.get('month_zhi') not in ('午', '子'):
        return False
    return '月德' in get_de_gods(sizhu, allow=('月德',))


def eval_yandui_exempt(sizhu):
    """矩阵 #13 厌对：与天德月德天德合月德合天赦并则不忌（五德集）。

    天愿经 DE_GODS_WUDE 结构性排除（禁并排除对，矩阵 §3.1）。

    Returns:
        (bool, str): (是否豁免, 豁免注记文案；不豁免时为空串)
    """
    if get_de_gods(sizhu, allow=DE_GODS_WUDE):
        return True, YANDUI_EXEMPT_NOTE
    return False, ''
