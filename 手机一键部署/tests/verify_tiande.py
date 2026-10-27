# -*- coding: utf-8 -*-
"""
天德/天德合穷举验证（B 类锚点③：比较维度 + 四维月口径）
=========================================================
权威规则（《协纪辨方书》天德例，2026-09-19 用户拍板）：
    正丁二坤宫，三壬四辛同，五乾六甲上，七癸八艮逢，
    九丙十居乙，子巽丑庚中。——逐月天德：
    寅丁 卯申 辰壬 巳辛 午亥 未甲 申癸 酉寅 戌丙 亥乙 子巳 丑庚。
    四维月（卯坤/午乾/酉艮/子巽）取宫内地支【后位】：
    坤→申、乾→亥、艮→寅、巽→巳（2026-09-19 拍板②确认，另附前位
    未/戌/丑/辰对照清单供《协纪》核对，本轮不改）。

比较维度（2026-09-19 拍板①⑤，本验证核心）：
    天干型 8 个月（丁/壬/辛/甲/癸/丙/乙/庚）→ 与【日干】比较（五合为天德合）；
    地支型 4 个月（申/亥/寅/巳）→ 与【日支】比较（六合为天德合）。
    原实现地支型月也错比日干，恒为 False —— 第三种失效模式：
    "表值正确 + 比较对象错误"（天赦=表值错、天德=比较对象错、五不遇时=比较方式错）。

2026 丙午年权威黄金清单（硬编码，sxtwl 实测复核，绝不从软件读取）：
    天德 36 天（修复后口径）：干型 8 个月 25 天 + 地支型 4 个月 11 天
      （卯月申日×3、午月亥日×3、酉月寅日×3、子月巳日×2）
    天德合 35 天：干型 24 天（五合干日）+ 地支型 11 天
      （卯月巳日×3、午月寅日×3、酉月亥日×3、子月申日×2）

边界测试点：
    1. 节气月支切换日：2026-08-07 立秋日（未→申）当日即按申月天德癸判定，
       该日癸丑恰为天德日；2026-11-07 立冬日（戌→亥）乙酉同为天德日。
    2. 四维月代表字：卯月甲申/午月辛亥/酉月庚寅/子月丁巳 必须命中。
    3. 四维前位反例：卯月未日/午月戌日/酉月丑日/子月辰日 不得命中
       （锁定"取宫后位"口径，与"取宫前位"另一说区分）。

修复背景（2026-09-19 锚点③）：
    基类/修造/嫁娶/入宅/通用 五处 _is_tiande 及四处天德合实现均存在
    地支型月错比日干；本轮统一为维度感知比较。动土天德日 +15 → +20
    与其他事项统一（拍板③）。修造/嫁娶两处"天德日"守卫重加死分支
    已挂账 001 跟踪项 13.1，不在本验证范围。

入口：
  ① modules/shensha/神煞基类.py ShenShaChecker._is_tiande / _is_tiande_he
     —— 作灶/出行/安床/安葬/开业/嫁娶(he) 继承
  ② ConstructionShenShaChecker._is_tiande / _is_tiandehe —— 动土/拆舍 继承
  ③ MarriageShenShaChecker._is_tiande（内嵌表）
  ④ RuZhaiShenShaChecker._is_tiande / _is_tiande_he（内嵌表）
  ⑤ CommonShenShaChecker._is_tiande / _is_tiandehe（合值直查表）
  ⑥ 端到端：check() 全链路神煞列表应含/不含 天德/天德日/天德合
  ⑦ 评分器._generate_wu_xing_details 八字详情层"天德贵人"（展示口径，
     2026-09-19 A 类比较维度审计时发现的锚点③漏网副本：该层支型月
     仍比日干恒 False，已同轮修复）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli

import sxtwl

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威规则表（硬编码，《协纪辨方书》口径，绝不从软件读取） =====
# 月支 -> 天德值（干或支）
TIANDE_AUTH = {
    '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
    '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
    '戌': '丙', '亥': '乙', '子': '巳', '丑': '庚',
}
# 五合（天干型天德 → 天德合干）；六合（地支型天德 → 天德合支）
WUHE_AUTH = {'甲': '己', '己': '甲', '乙': '庚', '庚': '乙',
             '丙': '辛', '辛': '丙', '丁': '壬', '壬': '丁',
             '戊': '癸', '癸': '戊'}
LIUHE_AUTH = {'寅': '亥', '亥': '寅', '申': '巳', '巳': '申'}


def expected_tiande(month_zhi, day_gan, day_zhi):
    """按权威规则推导：天干型比日干，地支型比日支"""
    td = TIANDE_AUTH[month_zhi]
    if td in ZHI:
        return day_zhi == td
    return day_gan == td


def expected_tiandehe(month_zhi, day_gan, day_zhi):
    """按权威规则推导：干型五合比日干，支型六合比日支"""
    td = TIANDE_AUTH[month_zhi]
    if td in WUHE_AUTH:
        return day_gan == WUHE_AUTH[td]
    return day_zhi == LIUHE_AUTH[td]


def build_calendar_2026():
    """sxtwl 生成 2026 全年 (date_iso, month_zhi, day_gan, day_zhi)"""
    import datetime
    rows = []
    cur = datetime.date(2026, 1, 1)
    end = datetime.date(2026, 12, 31)
    while cur <= end:
        day = sxtwl.fromSolar(cur.year, cur.month, cur.day)
        dgz = day.getDayGZ()
        rows.append((cur.isoformat(), ZHI[day.getMonthGZ().dz], GAN[dgz.tg], ZHI[dgz.dz]))
        cur += datetime.timedelta(days=1)
    return rows


CALENDAR = build_calendar_2026()

# 2026 天德 36 天黄金清单（硬编码：日期 -> (月支, 日干支)）
AUTH_TIANDE_2026 = {
    '2026-01-06': ('丑', '庚辰'),
    '2026-01-16': ('丑', '庚寅'),
    '2026-01-26': ('丑', '庚子'),
    '2026-02-12': ('寅', '丁巳'),
    '2026-02-22': ('寅', '丁卯'),
    '2026-03-04': ('寅', '丁丑'),
    '2026-03-11': ('卯', '甲申'),
    '2026-03-23': ('卯', '丙申'),
    '2026-04-04': ('卯', '戊申'),
    '2026-04-08': ('辰', '壬子'),
    '2026-04-18': ('辰', '壬戌'),
    '2026-04-28': ('辰', '壬申'),
    '2026-05-07': ('巳', '辛巳'),
    '2026-05-17': ('巳', '辛卯'),
    '2026-05-27': ('巳', '辛丑'),
    '2026-06-06': ('午', '辛亥'),
    '2026-06-18': ('午', '癸亥'),
    '2026-06-30': ('午', '乙亥'),
    '2026-07-09': ('未', '甲申'),
    '2026-07-19': ('未', '甲午'),
    '2026-07-29': ('未', '甲辰'),
    '2026-08-07': ('申', '癸丑'),
    '2026-08-17': ('申', '癸亥'),
    '2026-08-27': ('申', '癸酉'),
    '2026-09-06': ('申', '癸未'),
    '2026-09-13': ('酉', '庚寅'),
    '2026-09-25': ('酉', '壬寅'),
    '2026-10-07': ('酉', '甲寅'),
    '2026-10-09': ('戌', '丙辰'),
    '2026-10-19': ('戌', '丙寅'),
    '2026-10-29': ('戌', '丙子'),
    '2026-11-07': ('亥', '乙酉'),
    '2026-11-17': ('亥', '乙未'),
    '2026-11-27': ('亥', '乙巳'),
    '2026-12-09': ('子', '丁巳'),
    '2026-12-21': ('子', '己巳'),
}

# 2026 天德合 35 天黄金清单（硬编码：日期 -> (月支, 日干支)）
AUTH_TIANDEHE_2026 = {
    '2026-01-11': ('丑', '乙酉'),
    '2026-01-21': ('丑', '乙未'),
    '2026-01-31': ('丑', '乙巳'),
    '2026-02-07': ('寅', '壬子'),
    '2026-02-17': ('寅', '壬戌'),
    '2026-02-27': ('寅', '壬申'),
    '2026-03-08': ('卯', '辛巳'),
    '2026-03-20': ('卯', '癸巳'),
    '2026-04-01': ('卯', '乙巳'),
    '2026-04-13': ('辰', '丁巳'),
    '2026-04-23': ('辰', '丁卯'),
    '2026-05-03': ('辰', '丁丑'),
    '2026-05-12': ('巳', '丙戌'),
    '2026-05-22': ('巳', '丙申'),
    '2026-06-01': ('巳', '丙午'),
    '2026-06-09': ('午', '甲寅'),
    '2026-06-21': ('午', '丙寅'),
    '2026-07-03': ('午', '戊寅'),
    '2026-07-14': ('未', '己丑'),
    '2026-07-24': ('未', '己亥'),
    '2026-08-03': ('未', '己酉'),
    '2026-08-12': ('申', '戊午'),
    '2026-08-22': ('申', '戊辰'),
    '2026-09-01': ('申', '戊寅'),
    '2026-09-10': ('酉', '丁亥'),
    '2026-09-22': ('酉', '己亥'),
    '2026-10-04': ('酉', '辛亥'),
    '2026-10-14': ('戌', '辛酉'),
    '2026-10-24': ('戌', '辛未'),
    '2026-11-03': ('戌', '辛巳'),
    '2026-11-12': ('亥', '庚寅'),
    '2026-11-22': ('亥', '庚子'),
    '2026-12-02': ('亥', '庚戌'),
    '2026-12-12': ('子', '庚申'),
    '2026-12-24': ('子', '壬申'),
}

# 黄金清单自检：清单中每日干支/月支必须与 sxtwl 实际一致（防清单笔误）
for _d, (_mz, _gz) in AUTH_TIANDE_2026.items():
    _row = next(r for r in CALENDAR if r[0] == _d)
    assert (_row[1], _row[2] + _row[3]) == (_mz, _gz), \
        f'天德黄金清单自检失败: {_d} 实际{_row[2]}{_row[3]}/{_row[1]} 应为{_gz}/{_mz}'
for _d, (_mz, _gz) in AUTH_TIANDEHE_2026.items():
    _row = next(r for r in CALENDAR if r[0] == _d)
    assert (_row[1], _row[2] + _row[3]) == (_mz, _gz), \
        f'天德合黄金清单自检失败: {_d} 实际{_row[2]}{_row[3]}/{_row[1]} 应为{_gz}/{_mz}'

# 反向自检：按规则表推导的 2026 全部命中日必须恰好等于黄金清单（双保险）
_rule_td = {r[0] for r in CALENDAR if expected_tiande(r[1], r[2], r[3])}
assert _rule_td == set(AUTH_TIANDE_2026), \
    f'天德规则推导与黄金清单不一致: 规则={sorted(_rule_td)} 清单={sorted(AUTH_TIANDE_2026)}'
_rule_he = {r[0] for r in CALENDAR if expected_tiandehe(r[1], r[2], r[3])}
assert _rule_he == set(AUTH_TIANDEHE_2026), \
    f'天德合规则推导与黄金清单不一致: 规则={sorted(_rule_he)} 清单={sorted(AUTH_TIANDEHE_2026)}'

# 总量与逐月分布断言（36 = 干型 25 + 支型 11）
assert len(AUTH_TIANDE_2026) == 36, '天德黄金清单应为 36 天'
assert len(AUTH_TIANDEHE_2026) == 35, '天德合黄金清单应为 35 天'
_mcount = {}
for _d, (_mz, _gz) in AUTH_TIANDE_2026.items():
    _mcount[_mz] = _mcount.get(_mz, 0) + 1
assert _mcount == {'丑': 3, '寅': 3, '卯': 3, '辰': 3, '巳': 3, '午': 3,
                   '未': 3, '申': 4, '酉': 3, '戌': 3, '亥': 3, '子': 2}, \
    f'天德逐月分布异常: {_mcount}'


# ===== 软件入口 adapters =====
def _mk_checker(cls_path):
    mod_path, cls_name = cls_path.rsplit('.', 1)
    mod = __import__(mod_path, fromlist=[cls_name])
    return getattr(mod, cls_name)()


_TD_CLS = [
    ('modules.shensha.神煞基类.ShenShaChecker', '基类'),
    ('modules.shensha.修造神煞.ConstructionShenShaChecker', '修造'),
    ('modules.shensha.动土神煞.DiggingShenShaChecker', '动土'),
    ('modules.shensha.拆舍神煞.DemolitionShenShaChecker', '拆舍'),
    ('modules.shensha.嫁娶神煞.MarriageShenShaChecker', '嫁娶'),
    ('modules.shensha.入宅神煞.RuZhaiShenShaChecker', '入宅'),
    ('modules.shensha.通用神煞.CommonShenShaChecker', '通用'),
    ('modules.shensha.作灶神煞.StoveShenShaChecker', '作灶'),
    ('modules.shensha.安葬神煞.BurialShenShaChecker', '安葬'),
]
_CHECKERS = {tag: _mk_checker(p) for p, tag in _TD_CLS}


def _td_ad(tag):
    def _ad(inp):
        month_zhi, day_gan, day_zhi = inp
        return bool(_CHECKERS[tag]._is_tiande(
            {'month_zhi': month_zhi, 'day_gan': day_gan, 'day_zhi': day_zhi}))
    return _ad


def _he_ad(tag):
    """双名兼容：_is_tiande_he（基类/入宅）或 _is_tiandehe（修造/通用）"""
    c = _CHECKERS[tag]
    f = getattr(c, '_is_tiande_he', None) or getattr(c, '_is_tiandehe', None)
    if f is None:
        raise AttributeError(f'{tag} 检查器无天德合方法')

    def _ad(inp):
        month_zhi, day_gan, day_zhi = inp
        return bool(f({'month_zhi': month_zhi, 'day_gan': day_gan, 'day_zhi': day_zhi}))
    return _ad


def _e2e_ad(cls_path, names):
    """端到端：check() 全链路输出的神煞列表应含指定名称之一"""
    def _ad(inp):
        date, month_zhi, day_gan, day_zhi = inp
        import datetime
        y, m, dd = (int(x) for x in date.split('-'))
        day = sxtwl.fromSolar(y, m, dd)
        yg, mg = day.getYearGZ(), day.getMonthGZ()
        sizhu = {
            'year_gan': GAN[yg.tg], 'year_zhi': ZHI[yg.dz],
            'month_gan': GAN[mg.tg], 'month_zhi': month_zhi,
            'day_gan': day_gan, 'day_zhi': day_zhi,
            'hour_gan': '甲', 'hour_zhi': '子',
        }
        shensha_list = _mk_checker(cls_path).check(sizhu, [])
        got = {s['name'] for s in shensha_list if isinstance(s, dict)}
        return any(n in got for n in names)
    return _ad


inputs_cal = [(r[1], r[2], r[3]) for r in CALENDAR]          # 月支/日干/日支
inputs_full = [(r[0], r[1], r[2], r[3]) for r in CALENDAR]   # 含日期（端到端用）


def expected_td_fn(inp):
    return expected_tiande(*inp)


def expected_he_fn(inp):
    return expected_tiandehe(*inp)


def expected_td_e2e(inp):
    return inp[0] in AUTH_TIANDE_2026


def expected_he_e2e(inp):
    return inp[0] in AUTH_TIANDEHE_2026


# ===== 显式边界断言（修复后必须全绿） =====
def _d(dstr):
    return next(r for r in CALENDAR if r[0] == dstr)


_boundary_notes = []

# 边界1：节气月支切换日——立秋 08-07（未→申）当日即按申月天德癸判定
_rows_aug = [r for r in CALENDAR if r[0].startswith('2026-08') and r[1] == '申']
assert _rows_aug[0][0] == '2026-08-07', f'立秋月支切换异常: {_rows_aug[0][0]}'
assert _d('2026-08-06')[1] == '未', '08-06 应仍属未月'
_boundary_notes.append('08-06 未月/08-07 申月(立秋日) → 当日即按申月天德癸，癸丑命中')
assert _d('2026-11-06')[1] == '戌' and _d('2026-11-07')[1] == '亥'
_boundary_notes.append('11-06 戌月/11-07 亥月(立冬日) → 当日即按亥月天德乙，乙酉命中')

# 边界2：四维月代表字（取宫后位 申/亥/寅/巳）必须命中
assert expected_tiande('卯', '甲', '申') and expected_tiande('午', '辛', '亥')
assert expected_tiande('酉', '庚', '寅') and expected_tiande('子', '丁', '巳')
_boundary_notes.append('四维代表字：卯甲申/午辛亥/酉庚寅/子丁巳 全命中（坤申乾亥艮寅巽巳）')

# 边界3：四维前位反例（未/戌/丑/辰）——锁定"取宫后位"口径
assert not expected_tiande('卯', '癸', '未'), '口径锁定失败：卯月未日(前位)不得命中'
assert not expected_tiande('午', '庚', '戌'), '口径锁定失败：午月戌日(前位)不得命中'
assert not expected_tiande('酉', '己', '丑'), '口径锁定失败：酉月丑日(前位)不得命中'
assert not expected_tiande('子', '丙', '辰'), '口径锁定失败：子月辰日(前位)不得命中'
_boundary_notes.append('四维前位反例：卯未/午戌/酉丑/子辰 全不命中（锁定取宫后位口径）')

# 边界4：天德合维度——支型月六合命中、错合不命中
assert expected_tiandehe('卯', '辛', '巳') and expected_tiandehe('子', '庚', '申')
assert not expected_tiandehe('卯', '乙', '亥'), '卯月(天德申)合巳，亥是寅之合不得命中'
assert not expected_tiandehe('酉', '己', '巳'), '酉月(天德寅)合亥，巳是申之合不得命中'
_boundary_notes.append('天德合维度：卯巳/午寅/酉亥/子申 六合命中；错合（如卯亥/酉巳）不命中')

_ad_base = _td_ad('基类')
assert _ad_base(('卯', '甲', '申')) is True, '正向：卯月(坤宫)申日应命中天德（地支型比日支）'
assert _ad_base(('寅', '丁', '巳')) is True, '正向：寅月丁日应命中天德（天干型比日干）'
assert _ad_base(('酉', '庚', '寅')) is True, '正向：酉月(艮宫)寅日应命中天德'
assert _ad_base(('子', '丁', '巳')) is True, '正向：子月(巽宫)巳日应命中天德'
assert _ad_base(('卯', '甲', '酉')) is False, '反向：卯月酉日不是天德'
assert _ad_base(('巳', '丙', '丑')) is False, '反向：巳月丙日不是天德（天德辛）'

_he_base = _he_ad('基类')
assert _he_base(('卯', '辛', '巳')) is True, '正向：卯月巳日应命中天德合（申六合巳）'
assert _he_base(('寅', '壬', '子')) is True, '正向：寅月壬日应命中天德合（丁五合壬）'
assert _he_base(('卯', '乙', '亥')) is False, '反向：卯月亥日不是天德合'

# ===== 验证用例 =====
def _scorer_td_ad(inp):
    """评分器八字详情层天德贵人 adapter（展示口径，不参与计分）。

    锚点③首批修复（1889a1e）漏网副本：该层支型四维月仍比日干恒 False，
    2026-09-19 A 类比较维度静态审计时补查出并修复，故补此入口防回归。
    """
    mz, dg, dz = inp
    if not hasattr(_scorer_td_ad, '_s'):
        from modules.评分器 import Scorer
        _scorer_td_ad._s = Scorer()
    sizhu = {'年柱': '丙午', '月柱': '甲' + mz, '日柱': dg + dz, '时柱': '甲子'}
    d = _scorer_td_ad._s._generate_wu_xing_details(sizhu, [])
    return any('天德贵人' in x for x in d.get('吉神', []))


cases = [
    ShenShaCase(name='天德(神煞基类·计分入口)', category='B',
                description='维度感知：干型比日干/支型比日支；2026 应命中 36 天；作灶/出行/安床/安葬/开业继承',
                inputs=inputs_cal, expected=expected_td_fn, adapter=_ad_base, compare='bool'),
]
for _p, _tag in _TD_CLS[1:]:
    cases.append(ShenShaCase(
        name=f'天德({_tag}神煞)', category='B',
        description='应与基类同口径命中 36 天' + ('（继承链）' if _tag in ('动土', '拆舍') else ''),
        inputs=inputs_cal, expected=expected_td_fn, adapter=_td_ad(_tag), compare='bool'))

cases += [
    ShenShaCase(name='天德合(神煞基类·双名入口)', category='B',
                description='干型五合比日干/支型六合比日支；2026 应命中 35 天',
                inputs=inputs_cal, expected=expected_he_fn, adapter=_he_ad('基类'), compare='bool'),
    ShenShaCase(name='天德合(修造系_is_tiandehe)', category='B',
                description='修造实现（动土/拆舍继承）；支型月新增六合分支',
                inputs=inputs_cal, expected=expected_he_fn, adapter=_he_ad('修造'), compare='bool'),
    ShenShaCase(name='天德合(入宅_is_tiande_he)', category='B',
                description='入宅内嵌表实现，与基类同修',
                inputs=inputs_cal, expected=expected_he_fn, adapter=_he_ad('入宅'), compare='bool'),
    ShenShaCase(name='天德合(通用_is_tiandehe)', category='B',
                description='通用合值直查表实现（移徙/入学/求医/签约）；合值维度感知',
                inputs=inputs_cal, expected=expected_he_fn, adapter=_he_ad('通用'), compare='bool'),
    ShenShaCase(name='天德(修造check端到端)', category='B',
                description='check() 全链路：36 真日神煞列表含天德，329 非日不含',
                inputs=inputs_full, expected=expected_td_e2e,
                adapter=_e2e_ad('modules.shensha.修造神煞.ConstructionShenShaChecker', ('天德',)),
                compare='bool'),
    ShenShaCase(name='天德日(动土check端到端)', category='B',
                description='check() 全链路：动土异名天德日（+20）应与天德同日命中',
                inputs=inputs_full, expected=expected_td_e2e,
                adapter=_e2e_ad('modules.shensha.动土神煞.DiggingShenShaChecker', ('天德日',)),
                compare='bool'),
    ShenShaCase(name='天德合(修造check端到端)', category='B',
                description='check() 全链路：35 真日神煞列表含天德合，330 非日不含',
                inputs=inputs_full, expected=expected_he_e2e,
                adapter=_e2e_ad('modules.shensha.修造神煞.ConstructionShenShaChecker', ('天德合',)),
                compare='bool'),
    ShenShaCase(name='天德(评分器八字详情层)', category='B',
                description='展示口径：干型"见日干"/支型"见日支"；与计分层同口径命中 36 天（漏网副本补修）',
                inputs=inputs_cal, expected=expected_td_fn, adapter=_scorer_td_ad, compare='bool'),
]

if __name__ == '__main__':
    print('边界断言说明：')
    for _n in _boundary_notes:
        print('  -', _n)
    sys.exit(run_cli(cases))
