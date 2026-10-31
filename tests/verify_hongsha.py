# -*- coding: utf-8 -*-
"""
红砂日穷举验证（节气月支版，全事项唯一出口基类 ShenShaChecker._is_hongsha）
=========================================================================================
权威规则（2026-09-21 用户拍板，依据《协纪辨方书》辨讹篇；2026-10-15 D3 拍板统一节气月口径）：
    "查红沙乃巳酉丑金局日，孟月巳日，仲月酉日，季月丑日，相传又误以为
    孟月酉日，仲月巳日，甚属无当。"——以【节气月支】+【日支】判定：
        孟月（寅申巳亥）见巳日
        仲月（子午卯酉）见酉日
        季月（辰戌丑未）见丑日
    节气月支由产品 calculate_sizhu 依交节日正午判定；节气交接日 sxtwl 与
    产品月支可能不一致（节气时刻在午后者），verify 以产品月支为准（与
    checker 同源），日支取 sxtwl（与产品已逐日核对一致，独立双保险）。

D3 收敛背景（2026-10-15）：
    原 6 处实现分两口径：基类/通用/嫁娶神煞＝节气月支；修造扩展/安床/嫁娶
    规则＝农历月，4 年分歧 55 天（3.8%），且嫁娶内部自相矛盾（神煞节气月
    支 vs 规则农历月）。参照黄沙（2026-09-21 已统一节气月）先例，统一为
    节气月支：删除修造扩展/安床/通用/嫁娶 override，继承基类；嫁娶规则
    HONGSHA 表改节气月支键。嫁娶 -20 极凶日加重保留（《协纪》"其日忌
    嫁娶"，极凶日设计组与杨公忌/往亡 -20 并列）。

权威黄金清单（硬编码，产品 month_zhi + sxtwl 日支独立推导）：
    2026 公历年 29 天；2025 公历年 33 天。

入口：
  ① 基类 _is_hongsha（节气月支唯一出口，修造扩展/安床/通用/嫁娶均继承；
     §212 后嫁娶通道谓词保留、发射已剥离，此处仅验证谓词）
  ② 嫁娶规则 _check_rules 忌项文案链端到端（§212 后嫁娶已剥离 → 全期零发射）
  ③ pipeline shensha_list 端到端：四事项统一正名 '红纱日'（001 §193 C2
     异名归一：红砂日→红纱日），修造/安床 恰 1 条 -15；嫁娶 0 条（§212 删除）
  ④ 嫁娶内部一致性（§212 后 shensha_list 与 ji_list 双向均为零）

§212（2026-10-31 拍板 1）：红纱日「协纪 p279217 奏疏明斥『甚属无当』
『应请一并删去』」→ 嫁娶通道撤 -20、撤 ji_list 发射、撤 shensha_list 发射；
修造/安床/通用通道不受影响（仍 -15）。

独立运行：python tests/verify_hongsha.py    退出码 0=通过 1=失败
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli

import sxtwl
from modules.四柱计算器 import calculate_sizhu

_DZ = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
_MENG = {'寅', '申', '巳', '亥'}
_ZHONG = {'子', '午', '卯', '酉'}
_JI = {'辰', '戌', '丑', '未'}

# ===== 权威黄金清单（硬编码，绝不从软件 checker 读取） =====
AUTH_2026 = {
    '2026-01-15', '2026-01-27', '2026-02-12', '2026-02-24',
    '2026-03-12', '2026-03-24', '2026-04-09', '2026-04-21',
    '2026-05-03', '2026-05-07', '2026-05-19', '2026-05-31',
    '2026-06-16', '2026-06-28', '2026-07-14', '2026-07-26',
    '2026-08-07', '2026-08-11', '2026-08-23', '2026-09-04',
    '2026-09-08', '2026-09-20', '2026-10-02', '2026-10-18',
    '2026-10-30', '2026-11-15', '2026-11-27', '2026-12-13',
    '2026-12-25',
}
AUTH_2025 = {
    '2025-01-04', '2025-01-08', '2025-01-20', '2025-02-01',
    '2025-02-05', '2025-02-17', '2025-03-01', '2025-03-17',
    '2025-03-29', '2025-04-14', '2025-04-26', '2025-05-12',
    '2025-05-24', '2025-06-05', '2025-06-09', '2025-06-21',
    '2025-07-03', '2025-07-07', '2025-07-19', '2025-07-31',
    '2025-08-16', '2025-08-28', '2025-09-13', '2025-09-25',
    '2025-10-07', '2025-10-11', '2025-10-23', '2025-11-04',
    '2025-11-08', '2025-11-20', '2025-12-02', '2025-12-18',
    '2025-12-30',
}


def _expected_for(d):
    """节气月支版独立推导：产品 month_zhi（与 checker 同源）+ sxtwl 日支（独立）"""
    sz = calculate_sizhu(d, 12, 0)
    mz = sz['month_zhi']
    o = sxtwl.fromSolar(d.year, d.month, d.day)
    dz = _DZ[o.getDayGZ().dz]
    if mz in _MENG:
        return dz == '巳'
    if mz in _ZHONG:
        return dz == '酉'
    if mz in _JI:
        return dz == '丑'
    return False


def _daterange(y1, m1, d1, y2, m2, d2):
    cur = datetime.date(y1, m1, d1)
    end = datetime.date(y2, m2, d2)
    while cur <= end:
        yield cur
        cur += datetime.timedelta(days=1)


def _d(s):
    y, m, dd = map(int, s.split('-'))
    return datetime.date(y, m, dd)


# ===== 黄金清单自检：独立推导必须与硬编码完全一致 =====
_calc_2026 = {d.isoformat() for d in _daterange(2026, 1, 1, 2026, 12, 31) if _expected_for(d)}
assert _calc_2026 == AUTH_2026, f'2026 黄金清单自检失败: {sorted(_calc_2026 ^ AUTH_2026)}'
_calc_2025 = {d.isoformat() for d in _daterange(2025, 1, 1, 2025, 12, 31) if _expected_for(d)}
assert _calc_2025 == AUTH_2025, f'2025 黄金清单自检失败: {sorted(_calc_2025 ^ AUTH_2025)}'

INPUTS_2026 = list(_daterange(2026, 1, 1, 2026, 12, 31))
INPUTS_2025 = list(_daterange(2025, 1, 1, 2025, 12, 31))

# ===== 入口①：checker._is_hongsha（继承基类节气月支版） =====
from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
from modules.shensha.安床神煞 import BedShenShaChecker
from modules.shensha.通用神煞 import CommonShenShaChecker
from modules.shensha.嫁娶神煞 import MarriageShenShaChecker


def _make_judge(cls, **kw):
    checker = cls(**kw)

    def _ad(d):
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        return bool(checker._is_hongsha(sz))
    return _ad


def _exp_2026(d):
    return d.isoformat() in AUTH_2026


def _exp_2025(d):
    return d.isoformat() in AUTH_2025


def _exp_none(d):
    """§212 后嫁娶通道剥离口径：全期零命中"""
    return False


# ===== 入口②：rules 嫁娶文案链端到端（婚嫁 veto 源） =====
from modules.rules.嫁娶规则 import MarriageRuleChecker

_rc = MarriageRuleChecker()


def _ad_rules(d):
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d
    ji = _rc._check_rules(sz, date_obj=d)[1]
    return any('红纱日' in str(x) for x in ji)


# ===== 入口③：pipeline shensha_list 单条目/分值锁 =====
def _pipe_ad(cls, kw):
    def _ad(d):
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        c = cls(**kw)
        c.check(sz)
        return any(isinstance(x, dict) and x.get('name') == '红纱日' for x in c.shensha_list)
    return _ad


# ===== 入口④：嫁娶内部一致性（shensha_list 红纱日 IFF ji_list 红纱日） =====
def _ad_marriage_consistency(d):
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d
    mc = MarriageShenShaChecker()
    mc.check(sz)
    shensha_hit = any(isinstance(x, dict) and x.get('name') == '红纱日' for x in mc.shensha_list)
    ji = _rc._check_rules(sz, date_obj=d)[1]
    rules_hit = any('红纱日' in str(x) for x in ji)
    return shensha_hit == rules_hit


# ===== 显式边界断言（含反向断言） =====
_notes = []

_ad_xz = _make_judge(ConstructionShenShaCheckerExt, zuoshan=None, zhuming=None)
_ad_bed = _make_judge(BedShenShaChecker)
_ad_common = _make_judge(CommonShenShaChecker)
_ad_marriage = _make_judge(MarriageShenShaChecker)

# 边界1：口诀三档正例（《协纪》孟巳仲酉季丑）
assert _ad_xz(_d('2026-02-24')), '孟月（寅月）己巳应命中'
assert _ad_bed(_d('2026-02-24')), '安床孟月己巳应命中'
assert _ad_common(_d('2026-01-27')), '通用季月（丑月）辛丑应命中'
assert _ad_marriage(_d('2026-01-27')), '嫁娶季月辛丑应命中'
_notes.append('口诀三档正例：孟巳(02-24)/季丑(01-27) 四事项一致命中')

# 边界2：反向——同支不同月一律不命中（《协纪》斥孟酉仲巳为相传误）
assert not _ad_xz(_d('2026-02-28')), '寅月（孟月）癸酉不应命中——孟月见巳非酉'
assert not _ad_bed(_d('2026-02-28')), '安床：寅月癸酉不应命中'
assert not _ad_common(_d('2026-03-20')), '卯月（仲月）癸巳不应命中——仲月见酉非巳'
assert not _ad_marriage(_d('2026-03-20')), '嫁娶：卯月癸巳不应命中'
_notes.append('反向断言：孟月酉/仲月巳均不命中（相传误版已斥）')

# 边界3：四事项 _is_hongsha 逐日一致（单点出口继承验证）
for d in INPUTS_2026:
    a = _ad_xz(d); b = _ad_bed(d); c = _ad_common(d); e = _ad_marriage(d)
    assert a == b == c == e, f'{d} 四事项 _is_hongsha 不一致: 修造={a} 安床={b} 通用={c} 嫁娶={e}'
_notes.append('四事项 _is_hongsha 2026 逐日一致（基类单点出口继承生效）')

# 边界4：pipeline 单条目锁 + 分值锁
# 修造/安床 -15；§212 后嫁娶通道已剥离红纱日（0 条）
for tag, cls, kw, score in [
    ('修造扩展', ConstructionShenShaCheckerExt, {'zuoshan': None, 'zhuming': None}, -15),
    ('安床', BedShenShaChecker, {}, -15),
]:
    sz = calculate_sizhu(_d('2026-02-24'), 12, 0)
    sz['date'] = _d('2026-02-24')
    c = cls(**kw)
    c.check(sz)
    hs = [x for x in c.shensha_list if isinstance(x, dict) and '红' in str(x.get('name', ''))]
    assert [x.get('name') for x in hs] == ['红纱日'], f'{tag} 红纱条目异常: {hs}'
    assert hs[0].get('score') == score, f'{tag} 红砂应 {score}，实际 {hs[0].get("score")}'

# 反向：嫁娶通道 2026 全部红纱日（29 天）shensha_list 均无红纱条目
for d in sorted(AUTH_2026):
    sz = calculate_sizhu(_d(d), 12, 0)
    sz['date'] = _d(d)
    c = MarriageShenShaChecker()
    c.check(sz)
    assert not [x for x in c.shensha_list
                if isinstance(x, dict) and x.get('name') in ('红纱日', '红砂日')], \
        f'§212 后嫁娶通道不应发射红纱日: {d} {c.shensha_list}'
_notes.append('pipeline 分值锁：修造/安床 -15；嫁娶通道 §212 后 0 条（已删除）')

# 边界5：嫁娶内部一致性（§212 后 shensha_list 与 ji_list 双向均为零）
for d in INPUTS_2026:
    assert _ad_marriage_consistency(d), f'{d} 嫁娶 shensha_list 与 ji_list 红砂不一致'
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d
    mc = MarriageShenShaChecker()
    mc.check(sz)
    assert not any(isinstance(x, dict) and x.get('name') == '红纱日'
                   for x in mc.shensha_list), f'{d} shensha_list 仍发射红纱日'
    assert not any('红纱日' in str(x) for x in _rc._check_rules(sz, date_obj=d)[1]), \
        f'{d} ji_list 仍含红纱日'
_notes.append('嫁娶内部一致性：§212 后 shensha_list 与 ji_list 红砂双向均为零')

# 边界6：黄金清单构成
assert len(AUTH_2026) == 29 and len(AUTH_2025) == 33
_notes.append('黄金清单：2026 公历年 29 天 / 2025 公历年 33 天（节气月支版）')

# 边界7：婚嫁评分算法红砂日扣分回归锁（§212 后已撤扣分）
# §212 拍板 1：红纱日嫁娶通道撤 -20。锁定：红砂日评分不再含红纱条目，
# 且红砂日与非红砂日总分相等（无差值）。
from modules.婚嫁评分算法 import score_marriage_day as _smd
_hs_day = _d('2026-02-24')  # 寅月巳日，红砂日
_non_hs = _d('2026-02-20')  # 寅月卯日，非红砂
_r_hs = _smd(_hs_day, bride_bazi={'year_zhi': '子'}, groom_bazi={'year_zhi': '丑'})
_r_non = _smd(_non_hs, bride_bazi={'year_zhi': '子'}, groom_bazi={'year_zhi': '丑'})
assert not any('红纱' in x[0] for x in _r_hs['details']), \
    f'§212 后红砂日不应在嫁娶评分 details 中: {_r_hs["details"]}'
assert not any('红纱' in x[0] for x in _r_non['details']), '非红砂日不应含红纱扣分'
assert _r_hs['score'] == _r_non['score'], \
    f'§212 后红砂日与非红砂日总分应相等，实际 {_r_hs["score"]} vs {_r_non["score"]}'
_notes.append('婚嫁评分算法回归锁：§212 后红砂日撤 -20，红砂/非红砂总分相等')

# 边界8：两套路径口径一致性（§212 后 2025-2026 730 天双向均为零）
from modules.婚嫁评分算法 import score_marriage_day as _smd2
for _yr, _auth in [(2025, AUTH_2025), (2026, AUTH_2026)]:
    for _d in _daterange(_yr, 1, 1, _yr, 12, 31):
        _sz = calculate_sizhu(_d, 12, 0)
        _sz['date'] = _d
        _mc2 = MarriageShenShaChecker()
        _mc2.check(_sz)
        _s_hit = any(isinstance(x, dict) and x.get('name') == '红纱日' for x in _mc2.shensha_list)
        _r2 = _smd2(_d, bride_bazi={'year_zhi': '子'}, groom_bazi={'year_zhi': '丑'})
        _sc_hit = any('红纱' in x[0] for x in _r2['details'])
        assert not _s_hit and not _sc_hit, \
            f'§212 后两套路径均应为零: {_d} shensha={_s_hit} score={_sc_hit}'
_notes.append('两套路径口径一致：§212 后 2025-2026 共 730 天红砂双向均为零')


cases = [
    ShenShaCase(name='红砂(修造扩展·继承基类节气月支·2026穷举)', category='B',
                description='节气月支版：365 天中 29 天命中、336 天不命中',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_make_judge(ConstructionShenShaCheckerExt, zuoshan=None, zhuming=None),
                compare='bool'),
    ShenShaCase(name='红砂(安床·继承基类节气月支·2026穷举)', category='B',
                description='与修造扩展逐日一致（单点出口）',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_make_judge(BedShenShaChecker), compare='bool'),
    ShenShaCase(name='红砂(通用神煞·继承基类节气月支·2026穷举)', category='B',
                description='与修造扩展逐日一致（单点出口）',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_make_judge(CommonShenShaChecker), compare='bool'),
    ShenShaCase(name='红砂(嫁娶神煞·继承基类节气月支·2026穷举)', category='B',
                description='与修造扩展逐日一致；分值 -20 在发射侧',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_make_judge(MarriageShenShaChecker), compare='bool'),
    ShenShaCase(name='红砂(嫁娶规则文案链端到端·2026穷举)', category='B',
                description='§212 后 _check_rules 忌项已剥离红纱日（全期零发射）',
                inputs=INPUTS_2026, expected=_exp_none, adapter=_ad_rules, compare='bool'),
    ShenShaCase(name='红纱(修造扩展·2025全年)', category='B',
                description='公历年 33 天命中',
                inputs=INPUTS_2025, expected=_exp_2025,
                adapter=_make_judge(ConstructionShenShaCheckerExt, zuoshan=None, zhuming=None),
                compare='bool'),
    ShenShaCase(name='pipeline(修造扩展·红砂日-15单条目端到端)', category='B',
                description='shensha_list 在 29 个真日含红砂日恰1条、其余不含',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_pipe_ad(ConstructionShenShaCheckerExt, {'zuoshan': None, 'zhuming': None}),
                compare='bool'),
    ShenShaCase(name='pipeline(安床·红砂日-15单条目端到端)', category='B',
                description='shensha_list 单条目 -15',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_pipe_ad(BedShenShaChecker, {}), compare='bool'),
    ShenShaCase(name='pipeline(嫁娶·红砂日§212后零条目端到端)', category='B',
                description='§212 后嫁娶通道 shensha_list 已剥离红纱日（全期 0 条）',
                inputs=INPUTS_2026, expected=_exp_none,
                adapter=_pipe_ad(MarriageShenShaChecker, {}), compare='bool'),
]


if __name__ == '__main__':
    print('边界断言说明：')
    for _n in _notes:
        print('  -', _n)
    sys.exit(run_cli(cases))
