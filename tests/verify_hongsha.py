# -*- coding: utf-8 -*-
"""
红纱日穷举验证（农历月版三入口：修造扩展 / 安床 / 嫁娶规则文案链）
=========================================================================================
权威规则（2026-09-21 用户拍板，依据《协纪辨方书》辨讹篇）：
    "查红沙乃巳酉丑金局日，孟月巳日，仲月酉日，季月丑日，相传又误以为
    孟月酉日，仲月巳日，甚属无当。"——以【农历月】+【日支】判定：
        孟月（正/四/七/十月）见巳日
        仲月（二/五/八/十一月）见酉日
        季月（三/六/九/腊月）见丑日
    闰月不计（通用规则，与杨公忌/三娘煞/黄沙一致）：闰月任何日不命中。

修复背景（第六种失效模式"多实现一致的结构性抄错"+ 过宽活错表）：
    - 嫁娶规则 HONGSHA / 修造扩展 self.hongsha 原表为"孟酉仲巳"，正是《协纪》
      所斥"相传误"版本；2026-09-21 纠正为《协纪》正解"孟巳仲酉"。
    - 修造扩展 _is_hongsha 原读 get_lunar_date() 不存在的 'month_num' 键
      （第五种失效模式·字段名隐性死链），2026-09-20 已修复；自有'红纱日'分支
      删除防与基类'红砂日'不同名双扣。
    - 安床 _is_hongsha 原不看月、日支∈{酉,巳,丑}即命中（"按日命中"过宽
      错表）：2026 实测 91 天 vs 正确 29 天、误扣 62 天，2026-09-20
      commit f29eca8 改农历月版与修造扩展同构，自有同名死分支删除。
    - 本 verify 仅锁农历月版三入口。另有节气月支版三实现（神煞基类/通用神煞/
      嫁娶神煞，month_zhi 寅巳申亥=孟/子卯午酉=仲/辰戌丑未=季），2026-09-21
      同步改为孟巳仲酉季丑，与农历月版口径一致（交节日附近仍有 1~2 天差，
      属农历月与节气月的固有分界差，非口径冲突）。

权威黄金清单（硬编码，sxtwl 独立推导双保险；日干支取 sxtwl Day.getDayGZ().dz，
与产品 calculate_sizhu 已逐日核对一致——探针基准规范：日干支禁止自算）：
    2026 公历年 29 天；2025 公历年 31 天（2025 闰六月不计）。

入口：
  ① ConstructionShenShaCheckerExt._is_hongsha（孟仲对调+死链双修复）
  ② BedShenShaChecker._is_hongsha（过宽 91 天 → 农历月版 29 天）
  ③ MarriageRuleChecker._check_rules 忌项文案链端到端（'红纱日'，婚嫁 veto 源）
  ④ pipeline shensha_list 端到端：修造扩展/安床 '红砂日' 恰 1 条、-15 分（双扣锁）

独立运行：python tests/verify_hongsha.py    退出码 0=通过 1=失败
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli

import sxtwl

_DZ = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
_MENG, _ZHONG, _JI = {1, 4, 7, 10}, {2, 5, 8, 11}, {3, 6, 9, 12}

# ===== 权威黄金清单（硬编码，绝不从软件读取） =====
AUTH_2026 = {
    '2026-01-11', '2026-01-27', '2026-02-08', '2026-02-24',
    '2026-03-08', '2026-03-24', '2026-04-05', '2026-04-21',
    '2026-05-03', '2026-05-15', '2026-05-19', '2026-05-31',
    '2026-06-12', '2026-06-16', '2026-06-28', '2026-07-10',
    '2026-07-14', '2026-07-26', '2026-08-07', '2026-08-23',
    '2026-09-04', '2026-09-20', '2026-10-02', '2026-10-18',
    '2026-10-30', '2026-11-15', '2026-11-27', '2026-12-13',
    '2026-12-25',
}
AUTH_2025 = {
    '2025-01-08', '2025-01-20', '2025-02-05', '2025-02-17',
    '2025-03-05', '2025-03-17', '2025-04-02', '2025-04-14',
    '2025-04-26', '2025-04-30', '2025-05-12', '2025-05-24',
    '2025-05-28', '2025-06-09', '2025-06-21', '2025-06-25',
    '2025-07-07', '2025-07-19', '2025-08-28', '2025-09-09',
    '2025-09-21', '2025-09-25', '2025-10-07', '2025-10-19',
    '2025-10-23', '2025-11-04', '2025-11-16', '2025-11-20',
    '2025-12-02', '2025-12-14', '2025-12-30',
}
# 闰月不计边界（2025 闰六月，季月本应见丑；干支均已经 calculate_sizhu 核对）
NORM_CHOU_2025 = ('2025-06-25', '2025-07-07', '2025-07-19')   # 正六月 乙丑/丁丑/丁丑
LEAP_CHOU_2025 = ('2025-07-31', '2025-08-12')                  # 闰六月 辛丑/癸丑
NORM_MAO_2025 = '2025-06-27'                                   # 正六月初三丁卯：季月非丑，反例


def _expected_for(d):
    """sxtwl 独立推导（权威双保险：不读软件实现；闰月不计）"""
    o = sxtwl.fromSolar(d.year, d.month, d.day)
    if o.isLunarLeap():
        return False
    lm, zhi = o.getLunarMonth(), _DZ[o.getDayGZ().dz]
    if lm in _MENG:
        return zhi == '巳'
    if lm in _ZHONG:
        return zhi == '酉'
    if lm in _JI:
        return zhi == '丑'
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


# ===== 黄金清单自检：sxtwl 推导必须与硬编码完全一致 =====
_calc_2026 = {d.isoformat() for d in _daterange(2026, 1, 1, 2026, 12, 31) if _expected_for(d)}
assert _calc_2026 == AUTH_2026, f'2026 黄金清单自检失败: {sorted(_calc_2026 ^ AUTH_2026)}'
_calc_2025 = {d.isoformat() for d in _daterange(2025, 1, 1, 2025, 12, 31) if _expected_for(d)}
assert _calc_2025 == AUTH_2025, f'2025 黄金清单自检失败: {sorted(_calc_2025 ^ AUTH_2025)}'
# 2025 农历结构自检：锚点日闰月标记与预期一致
assert sxtwl.fromSolar(2025, 7, 31).isLunarLeap() and not sxtwl.fromSolar(2025, 6, 25).isLunarLeap()

INPUTS_2026 = list(_daterange(2026, 1, 1, 2026, 12, 31))
INPUTS_2025 = list(_daterange(2025, 1, 1, 2025, 12, 31))

# ===== 入口①②：checker._is_hongsha（sizhu 形态） =====
from modules.四柱计算器 import calculate_sizhu
from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
from modules.shensha.安床神煞 import BedShenShaChecker


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


# ===== 入口③：rules 嫁娶文案链端到端（婚嫁 veto 源） =====
from modules.rules.嫁娶规则 import MarriageRuleChecker

_rc = MarriageRuleChecker()


def _ad_rules(d):
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d
    ji = _rc._check_rules(sz, date_obj=d)[1]
    return any('红纱日' in str(x) for x in ji)


# ===== 入口④：pipeline shensha_list 单条目/分值锁 =====
def _pipe_ad(cls, kw):
    def _ad(d):
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        c = cls(**kw)
        c.check(sz)
        return any(isinstance(x, dict) and x.get('name') == '红砂日' for x in c.shensha_list)
    return _ad


# ===== 显式边界断言（含反向断言） =====
_notes = []

_ad_xz = _make_judge(ConstructionShenShaCheckerExt, zuoshan=None, zhuming=None)
_ad_bed = _make_judge(BedShenShaChecker)

# 边界1：口诀三档正例（《协纪》孟巳仲酉季丑）
assert _ad_xz(_d('2026-02-24')) and _ad_bed(_d('2026-02-24')), '孟月（正月）己巳应命中'
assert _ad_xz(_d('2026-01-11')), '仲月（十一月）乙酉应命中'
assert _ad_xz(_d('2026-01-27')), '季月（腊月）辛丑应命中'
_notes.append('口诀三档正例：孟巳(02-24己巳)/仲酉(01-11乙酉)/季丑(01-27辛丑)')

# 边界2：反向——同支不同月一律不命中（《协纪》斥孟酉仲巳为相传误）
assert not _ad_xz(_d('2026-02-28')), '正月（孟月）癸酉不应命中——孟月见巳非酉'
assert not _ad_bed(_d('2026-02-28')), '安床：正月癸酉不应命中'
assert not _ad_xz(_d('2026-03-20')), '二月（仲月）癸巳不应命中——仲月见酉非巳'
assert not _ad_bed(_d('2025-06-27')), '安床：六月丁卯（季月非丑）不应命中'
_notes.append('反向断言：孟月酉(02-28癸酉)/仲月巳(03-20癸巳)/季月非丑均不命中')

# 边界3：闰月不计（2025 闰六月；正六月对照）
for s in LEAP_CHOU_2025:
    assert not _ad_xz(_d(s)), f'{s} 闰六月丑日不应命中（闰月不计）'
    assert not _ad_bed(_d(s)), f'安床 {s} 闰六月丑日不应命中'
    assert not _ad_rules(_d(s)), f'嫁娶规则 {s} 闰六月不应出红纱日忌项'
for s in NORM_CHOU_2025:
    assert _ad_xz(_d(s)), f'{s} 正六月丑日应命中'
    assert _ad_bed(_d(s)), f'安床 {s} 正六月丑日应命中'
assert not _ad_xz(_d(NORM_MAO_2025)), '正六月丁卯（季月非丑）不命中'
_notes.append('2025 闰六月：07-31辛丑/08-12癸丑不命中；正六月 06-25/07-07/07-19 三丑日命中；06-27丁卯反例')

# 边界4：无 date 键早退 False（修造/安床农历月版均要求 sizhu['date']）
_ext0 = ConstructionShenShaCheckerExt(zuoshan=None, zhuming=None)
_bed0 = BedShenShaChecker()
assert _ext0._is_hongsha({'day_zhi': '酉'}) is False
assert _bed0._is_hongsha({'day_zhi': '酉'}) is False
_notes.append('缺 date 键早退 False（不抛异常、不回退月支表）')

# 边界5：pipeline 单条目锁（防不同名双扣复活）——真红砂日恰 1 条"红砂日" -15
for tag, cls, kw in [('修造扩展', ConstructionShenShaCheckerExt, {'zuoshan': None, 'zhuming': None}),
                     ('安床', BedShenShaChecker, {})]:
    sz = calculate_sizhu(_d('2026-02-24'), 12, 0)
    sz['date'] = _d('2026-02-24')
    c = cls(**kw)
    c.check(sz)
    hs = [x for x in c.shensha_list if isinstance(x, dict) and '红' in str(x.get('name', ''))]
    assert [x.get('name') for x in hs] == ['红砂日'], f'{tag} 红砂条目异常: {hs}'
    assert hs[0].get('score') == -15, f'{tag} 红砂应 -15，实际 {hs[0].get("score")}'
_notes.append('pipeline 双扣锁：修造扩展/安床真红砂日恰 1 条"红砂日"-15')

# 边界6：黄金清单构成
assert len(AUTH_2026) == 29 and len(AUTH_2025) == 31
_notes.append('黄金清单：2026 公历年 29 天 / 2025 公历年 31 天（闰六月不计）')


cases = [
    ShenShaCase(name='红纱(修造扩展·孟仲对调+死链修复·2026穷举)', category='B',
                description='农历月版口诀表：365 天中 29 天命中、336 天不命中',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_make_judge(ConstructionShenShaCheckerExt, zuoshan=None, zhuming=None),
                compare='bool'),
    ShenShaCase(name='红纱(安床·过宽91天改农历月版·2026穷举)', category='B',
                description='原"日支∈酉巳丑全收"91天误判62天；修复后与修造扩展逐日一致',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_make_judge(BedShenShaChecker), compare='bool'),
    ShenShaCase(name='红纱(嫁娶规则文案链端到端·2026穷举)', category='B',
                description='_check_rules 忌项含"红纱日"（婚嫁 veto_keywords 源）',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_ad_rules, compare='bool'),
    ShenShaCase(name='红纱(修造扩展·2025全年含闰六月不计)', category='B',
                description='公历年 28 天：闰六月（07-25~08-22段）零命中',
                inputs=INPUTS_2025, expected=_exp_2025,
                adapter=_make_judge(ConstructionShenShaCheckerExt, zuoshan=None, zhuming=None),
                compare='bool'),
    ShenShaCase(name='红纱(安床·2025全年含闰六月不计)', category='B',
                description='安床与修造扩展 2025 逐日一致；闰六月辛丑/癸丑不命中',
                inputs=INPUTS_2025, expected=_exp_2025,
                adapter=_make_judge(BedShenShaChecker), compare='bool'),
    ShenShaCase(name='pipeline(修造扩展·红砂日-15单条目端到端)', category='B',
                description='shensha_list 在 29 个真日含红砂日恰1条、其余 336 天不含',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_pipe_ad(ConstructionShenShaCheckerExt, {'zuoshan': None, 'zhuming': None}),
                compare='bool'),
    ShenShaCase(name='pipeline(安床·红砂日-15单条目端到端)', category='B',
                description='shensha_list 单条目（自有同名死分支已删）',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_pipe_ad(BedShenShaChecker, {}), compare='bool'),
]


if __name__ == '__main__':
    print('边界断言说明：')
    for _n in _notes:
        print('  -', _n)
    sys.exit(run_cli(cases))
