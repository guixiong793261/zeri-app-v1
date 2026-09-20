# -*- coding: utf-8 -*-
"""
杨公忌日穷举验证（桩函数普查 P3：口径收敛 + 第五种失效模式"字段名隐性死链"修复）
=========================================================================================
权威规则（2026-09-20 用户拍板）：
    杨公忌日 = 农历月日 13 日固定日期：
        正月十三、二月十一、三月初九、四月初七、五月初五、六月初三、
        七月初一、七月廿九、八月廿七、九月廿五、十月廿三、十一月廿一、十二月十九。
    闰月不计：闰月中同序号日期不命中（2025 闰六月初三 → 2025-07-27 不算）。
    年内命中文案：公历年通常 14 天（如 2026：冬月廿一在 01-09 与 12-29 出现两次），
    2025 因闰六月 + 冬月廿一落于次年，公历年仅 12 天。

失效模式背景（2026-09-20 桩函数普查 P3）：
    收敛前 6 处实现：rules/嫁娶规则（农历13日，唯一真活 14/14）；修造神煞扩展
    （表对但取不存在的 'month_num'/'day_num' 键 → 全年静默 0 命中，第五种失效
    模式：字段名隐性死链 + except:pass 包裹）；神煞基类/通用神煞（月支日支表，
    与真表仅 2/28 重合=错表）；安床神煞（六冲表，2/31=错表）；嫁娶神煞（反转桩
    恒 False）。收敛后统一委托 modules/shensha/神煞基类.py::is_yanggongji_by_lunar
    （sxtwl 直取农历数字月日，不吞异常）。分值：基类/通用/修造扩展/嫁娶神煞 -20，
    安床维持 -10 事项差（SHENSHA_SCORES ('安床','杨公忌日') 单一表）。

2026 丙午年权威黄金清单（硬编码，sxtwl 独立推导双保险）：
    14 天：01-09(冬月廿一) 02-06(腊十九) 03-01(正十三) 03-29(二月十一)
           04-25(三月初九) 05-23(四月初七) 06-19(五月初五) 07-16(六月初三)
           08-13(七月初一) 09-10(七月廿九) 10-07(八月廿七) 11-03(九月廿五)
           12-01(十月廿三) 12-29(冬月廿一)

入口：
  ① modules/shensha/神煞基类.py::is_yanggongji_by_lunar —— 全项目唯一实现
  ② ShenShaChecker._is_yanggongji（基类，月支错表已删）
  ③ CommonShenShaChecker._is_yanggongji（通用副本已删）
  ④ ConstructionShenShaCheckerExt._is_yanggongji（字段名死链已修）
  ⑤ BedShenShaChecker._is_yanggongji（六冲错表已删）
  ⑥ MarriageShenShaChecker._is_yanggongji（反转桩已复活）
  ⑦ rules/嫁娶规则._check_bad_gods 忌项文案链端到端（'杨公忌'）
  ⑧ pipeline shensha_list 端到端 + 分值锁定（安床 _std_event → -10）
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli

import sxtwl

# ===== 权威黄金清单（硬编码，绝不从软件读取） =====
AUTH_2026 = {
    '2026-01-09', '2026-02-06', '2026-03-01', '2026-03-29',
    '2026-04-25', '2026-05-23', '2026-06-19', '2026-07-16',
    '2026-08-13', '2026-09-10', '2026-10-07', '2026-11-03',
    '2026-12-01', '2026-12-29',
}
AUTH_2025 = {
    '2025-01-18', '2025-02-10', '2025-03-10', '2025-04-06',
    '2025-05-04', '2025-05-31', '2025-06-27',
    '2025-08-23', '2025-09-20', '2025-10-18', '2025-11-14', '2025-12-12',
}
# 闰月不计边界（2025 闰六月）
ZHENG_LIU_CHUSAN_2025 = '2025-06-27'    # 正六月初三 → 命中
RUN_LIU_CHUSAN_2025 = '2025-07-27'      # 闰六月初三 → 不命中


def _expected_for(d):
    """sxtwl 独立推导（权威双保险：不读软件实现，闰月不计）"""
    day = sxtwl.fromSolar(d.year, d.month, d.day)
    if day.isLunarLeap():
        return False
    table = {1: (13,), 2: (11,), 3: (9,), 4: (7,), 5: (5,), 6: (3,),
             7: (1, 29), 8: (27,), 9: (25,), 10: (23,), 11: (21,), 12: (19,)}
    days = table.get(day.getLunarMonth())
    return days is not None and day.getLunarDay() in days


def _daterange(y1, m1, d1, y2, m2, d2):
    cur = datetime.date(y1, m1, d1)
    end = datetime.date(y2, m2, d2)
    while cur <= end:
        yield cur
        cur += datetime.timedelta(days=1)


def _d(y, m, dd):
    return datetime.date(y, m, dd)


# ===== 黄金清单自检：sxtwl 推导必须与硬编码完全一致 =====
_calc_2026 = {d.isoformat() for d in _daterange(2026, 1, 1, 2026, 12, 31) if _expected_for(d)}
assert _calc_2026 == AUTH_2026, f'2026 黄金清单自检失败: {sorted(_calc_2026)}'
_calc_2025 = {d.isoformat() for d in _daterange(2025, 1, 1, 2025, 12, 31) if _expected_for(d)}
assert _calc_2025 == AUTH_2025, f'2025 黄金清单自检失败: {sorted(_calc_2025)}'
# 2025 农历结构自检：闰六月存在，且闰六月初三为 2025-07-27
_leap_found = False
for _dd in _daterange(2025, 1, 1, 2025, 12, 31):
    _o = sxtwl.fromSolar(_dd.year, _dd.month, _dd.day)
    if _o.isLunarLeap() and _o.getLunarMonth() == 6 and _o.getLunarDay() == 3:
        assert _dd.isoformat() == RUN_LIU_CHUSAN_2025, f'闰六月初三日期漂移: {_dd}'
        _leap_found = True
assert _leap_found, '2025 未找到闰六月初三，黄金清单边界失效'

INPUTS_2026 = list(_daterange(2026, 1, 1, 2026, 12, 31))
INPUTS_2025 = list(_daterange(2025, 1, 1, 2025, 12, 31))

# ===== 入口①：公共函数（唯一实现） =====
from modules.shensha.神煞基类 import is_yanggongji_by_lunar
from modules.四柱计算器 import calculate_sizhu


def _ad_func(d):
    return is_yanggongji_by_lunar(d)


# ===== 入口②~⑥：各 checker 的 _is_yanggongji（sizhu 形态） =====
from modules.shensha.神煞基类 import ShenShaChecker
from modules.shensha.通用神煞 import CommonShenShaChecker
from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
from modules.shensha.安床神煞 import BedShenShaChecker
from modules.shensha.嫁娶神煞 import MarriageShenShaChecker


def _make_judge(cls, **kw):
    checker = cls(**kw)

    def _ad(d):
        sz = calculate_sizhu(d, 12, 0)
        return bool(checker._is_yanggongji(sz))
    return _ad


def _exp_2026(d):
    return d.isoformat() in AUTH_2026


def _exp_2025(d):
    return d.isoformat() in AUTH_2025


# ===== 入口⑦：rules 嫁娶文案链端到端 =====
from modules.rules.嫁娶规则 import MarriageRuleChecker

_rc = MarriageRuleChecker()


def _ad_rules(d):
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d
    ji = _rc._check_rules(sz, date_obj=d)[1]
    return any('杨公忌' in str(x) for x in ji)


# ===== 入口⑧：pipeline shensha_list 端到端 =====
_PIPE = [
    ('基类', ShenShaChecker, {}),
    ('通用', CommonShenShaChecker, {}),
    ('修造扩展', ConstructionShenShaCheckerExt, {'zuoshan': None, 'zhuming': None}),
    ('安床', BedShenShaChecker, {}),
    ('嫁娶神煞', MarriageShenShaChecker, {}),
]


def _pipe_ad(tag):
    cls, kw = next((c, k) for t, c, k in _PIPE if t == tag)

    def _ad(d):
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        c = cls(**kw)
        c.check(sz)
        return any(isinstance(x, dict) and x.get('name') == '杨公忌日' for x in c.shensha_list)
    return _ad


# ===== 显式边界断言 =====
_notes = []

# 边界1：同农历日期跨公历年出现两次（2026 冬月廿一 = 01-09 与 12-29）
assert _ad_func(_d(2026, 1, 9)) and _ad_func(_d(2026, 12, 29))
assert not _ad_func(_d(2026, 1, 10)), '2026-01-10 冬月廿二不应命中'
assert not _ad_func(_d(2026, 12, 30)), '2026-12-30 冬月廿二不应命中'
_notes.append('冬月廿一在 2026 出现两次（01-09/12-29）均命中，次日反例不命中')

# 边界2：七月初一/廿九 双日（同一农历月两个忌日）
assert _ad_func(_d(2026, 8, 13)) and _ad_func(_d(2026, 9, 10))
_notes.append('七月双忌日（初一 08-13 / 廿九 09-10）均命中')

# 边界3：闰月不计（2025 正六月初三命中 / 闰六月初三不命中）
assert _ad_func(_d(2025, 6, 27)), '2025-06-27 正六月初三应命中'
assert not _ad_func(_d(2025, 7, 27)), '2025-07-27 闰六月初三不应命中（闰月不计）'
_notes.append('2025 闰六月口径：正六月初三(06-27)命中 / 闰六月初三(07-27)不命中')

# 边界4：无日期信息不误判（dict 缺 date 键 / 非法输入）
assert is_yanggongji_by_lunar({}) is False
assert is_yanggongji_by_lunar(None) is False
assert is_yanggongji_by_lunar({'month_zhi': '寅', 'day_zhi': '酉'}) is False, \
    '旧月支表口径（寅月酉日）必须不再命中——错表已删'
_notes.append('dict 缺 date / None / 纯月支日支输入均 False（错表口径不可复活）')

# 边界5：pipeline 无双条目（收敛前修造扩展会出现 '杨公忌'+'杨公忌日' 两条）
_ext = ConstructionShenShaCheckerExt(zuoshan=None, zhuming=None)
_sz = calculate_sizhu(_d(2026, 3, 1), 12, 0)
_sz['date'] = _d(2026, 3, 1)
_ext.check(_sz)
_names = [x.get('name') for x in _ext.shensha_list if isinstance(x, dict) and '杨公忌' in str(x.get('name', ''))]
assert _names == ['杨公忌日'], f'修造扩展杨公忌条目应恰为1条"杨公忌日"，实际 {_names}'
_notes.append('修造扩展 pipeline 单条目"杨公忌日"（原 _check_additional_shensha 独立分支已删，防不同名双扣）')

# 边界6：分值锁定——安床 _std_event 走 SHENSHA_SCORES 单一表 = -10；其余 -20
_bed = BedShenShaChecker()
_bed._std_event = '安床'
_bed.check(_sz)
_bed_scores = [x.get('score') for x in _bed.shensha_list if isinstance(x, dict) and x.get('name') == '杨公忌日']
assert _bed_scores == [-10], f'安床杨公忌日应-10（事项标准单一表），实际 {_bed_scores}'
for _tag, _cls, _kw in [('基类', ShenShaChecker, {}), ('嫁娶神煞', MarriageShenShaChecker, {})]:
    _c = _cls(**_kw)
    _c._std_event = {'基类': '修造', '嫁娶神煞': '嫁娶'}[_tag]
    _c.check(_sz)
    _sc = [x.get('score') for x in _c.shensha_list if isinstance(x, dict) and x.get('name') == '杨公忌日']
    assert _sc == [-20], f'{_tag}杨公忌日应-20，实际 {_sc}'
_notes.append('分值锁定：安床-10（SHENSHA_SCORES 事项差）/ 基类-20 / 嫁娶-20')

# 边界7：黄金清单构成
assert len(AUTH_2026) == 14 and len(AUTH_2025) == 12
_notes.append('黄金清单：2026 公历年 14 天（冬月廿一两次）/ 2025 公历年 12 天（闰六月不计+冬月廿一落次年）')


cases = [
    ShenShaCase(name='杨公忌(公共函数唯一实现·2026穷举)', category='A',
                description='农历月日13日口径：365 天中 14 天命中、351 天不命中',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_ad_func, compare='bool'),
    ShenShaCase(name='杨公忌(基类·错表已删)', category='A',
                description='原月支日支表(2/14重合)删除改委托；2026 十四天全命中',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_make_judge(ShenShaChecker), compare='bool'),
    ShenShaCase(name='杨公忌(通用·副本已删)', category='A',
                description='原月支表副本删除改委托；与基类同源',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_make_judge(CommonShenShaChecker), compare='bool'),
    ShenShaCase(name='杨公忌(修造扩展·字段名死链已修)', category='A',
                description='第五种失效模式修复：month_num/day_num 不存在键→sxtwl 直取；原 0/14 → 14/14',
                inputs=INPUTS_2026, expected=_exp_2026,
                adapter=_make_judge(ConstructionShenShaCheckerExt, zuoshan=None, zhuming=None), compare='bool'),
    ShenShaCase(name='杨公忌(安床·六冲错表已删)', category='A',
                description='原六冲表(2/14重合)删除改委托；分值 -10 由 SHENSHA_SCORES 锁定',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_make_judge(BedShenShaChecker), compare='bool'),
    ShenShaCase(name='杨公忌(嫁娶神煞·反转桩复活)', category='A',
                description='原 lunar_python 恒 False 桩复活；except 死分支表(0/14)删除',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_make_judge(MarriageShenShaChecker), compare='bool'),
    ShenShaCase(name='杨公忌(rules嫁娶文案链端到端)', category='A',
                description='_check_rules 忌项含"杨公忌"；原唯一真活(14/14)收敛后口径不变',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_ad_rules, compare='bool'),
    ShenShaCase(name='杨公忌(2025全年·闰月不计)', category='A',
                description='公历年 12 天：闰六月初三不计；正六月初三 06-27 命中',
                inputs=INPUTS_2025, expected=_exp_2025, adapter=_ad_func, compare='bool'),
]

for _tag, _, _ in _PIPE:
    cases.append(ShenShaCase(
        name=f'pipeline({_tag}·杨公忌日-20/-10端到端)', category='A',
        description='shensha_list 在 14 个真日含杨公忌日、其余 351 天不含',
        inputs=INPUTS_2026, expected=_exp_2026, adapter=_pipe_ad(_tag), compare='bool'))


if __name__ == '__main__':
    print('边界断言说明：')
    for _n in _notes:
        print('  -', _n)
    sys.exit(run_cli(cases))
