# -*- coding: utf-8 -*-
"""
天赦日穷举验证（B 类锚点①：节气划季 + 全部命中口径）
=========================================================
权威规则（《协纪辨方书·卷五》义例，2026-09-18 用户拍板为 B 类基准）：
    春戊寅、夏甲午、秋戊申、冬甲子——天赦日，百无禁忌。
    四季按节气划分（立春~立夏前为春，立夏~立秋前为夏，
    立秋~立冬前为秋，立冬~次年立春前为冬），不按农历月。
    命中口径（2026-09-18 用户拍板）：季度内全部命中，不限序次。

2026 丙午年权威黄金清单（硬编码，sxtwl 实测复核，绝不从软件读取）：
    春（立春02-04~立夏前）：03-05 戊寅、05-04 戊寅（立夏前一日！）
    夏（立夏05-05~立秋前）：05-20 甲午、07-19 甲午
    秋（立秋08-07~立冬前）：10-01 戊申
    冬（立冬11-07~次年立春前）：12-16 甲子

边界测试点（节气 vs 农历月划季的区分器）：
    2026-05-04 戊寅、月支辰（春）→ 立夏前一日，应命中"春戊寅"
      （若误按农历月划季，此日农历三月仍属春会巧合命中；
        而 2026-05-05 立夏当日农历三月十九，按农历月仍属"三月(春)"，
        但节气口径已入夏——若该日为戊寅则会暴露差异。故边界断言
        同时锁定 05-04 命中与 05-05 不命中。）
    2026-08-07 立秋日（月支申）→ 夏甲午失效，应改查秋戊申。

修复背景（2026-09-18 诊断）：
    基类 _is_tianshe 旧表"春乙卯、夏丙午、秋辛酉、冬壬子"为错表
    （2026 年误命中 7 天、漏 6 天真值）；修造/入宅两处 override 为
    权威表。拍板方案一：改基类为权威表 + 删两处 override，走继承统一表。

入口：
  ① modules/shensha/神煞基类.py ShenShaChecker._is_tianshe —— 通用计分入口（+25）
  ② ConstructionShenShaChecker（修造）/ RuZhaiShenShaChecker（入宅）
     / DemolitionShenShaChecker（拆舍，继承修造）/ MarriageShenShaChecker（嫁娶）
     —— 删除 override 后四者应与基类判定完全一致
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

import sxtwl

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威规则表（硬编码，《协纪辨方书》口径，绝不从软件读取） =====
# 季节 -> (月支组, 天赦日柱干支)
TIANSHE_TRUTH = [
    ('春', ('寅', '卯', '辰'), ('戊', '寅')),
    ('夏', ('巳', '午', '未'), ('甲', '午')),
    ('秋', ('申', '酉', '戌'), ('戊', '申')),
    ('冬', ('亥', '子', '丑'), ('甲', '子')),
]

# 2026 丙午年权威黄金清单（硬编码；节气季按立春02-04/立夏05-05/立秋08-07/立冬11-07）
AUTH_TIANSHE_2026 = {
    '2026-03-05': ('春', '戊寅', '卯'),
    '2026-05-04': ('春', '戊寅', '辰'),
    '2026-05-20': ('夏', '甲午', '巳'),
    '2026-07-19': ('夏', '甲午', '未'),
    '2026-10-01': ('秋', '戊申', '酉'),
    '2026-12-16': ('冬', '甲子', '子'),
}


def _gz(day_obj):
    g = day_obj.getDayGZ()
    return GAN[g.tg], ZHI[g.dz]


def _mgz(day_obj):
    g = day_obj.getMonthGZ()
    return ZHI[g.dz]


def season_of(month_zhi):
    for name, group, _ in TIANSHE_TRUTH:
        if month_zhi in group:
            return name, group
    raise ValueError(f'非法月支: {month_zhi!r}')


def expected_by_rule(month_zhi, day_gan, day_zhi):
    """按权威规则表推导：月支划季（节气等效）+ 全部命中口径"""
    _, group = season_of(month_zhi)
    for name, g, (eg, ez) in TIANSHE_TRUTH:
        if month_zhi in g:
            return day_gan == eg and day_zhi == ez
    return False


def build_calendar_2026():
    """sxtwl 生成 2026 全年 (date, month_zhi, day_gan, day_zhi)"""
    import datetime
    rows = []
    cur = datetime.date(2026, 1, 1)
    end = datetime.date(2026, 12, 31)
    while cur <= end:
        day = sxtwl.fromSolar(cur.year, cur.month, cur.day)
        dg, dz = _gz(day)
        rows.append((cur.isoformat(), _mgz(day), dg, dz))
        cur += datetime.timedelta(days=1)
    return rows


CALENDAR = build_calendar_2026()

# 黄金清单自检：清单中每日干支/月支必须与权威规则推导一致（防清单笔误）
_SEASON_GZ = {name: gz for name, _, gz in TIANSHE_TRUTH}
for _d, (_season, _gz2, _mz) in AUTH_TIANSHE_2026.items():
    _row = next(r for r in CALENDAR if r[0] == _d)
    _eg, _ez = _SEASON_GZ[_season]
    assert (_row[2], _row[3]) == (_eg, _ez), \
        f'黄金清单自检失败: {_d} 实际{_row[2]}{_row[3]} 应为{_eg}{_ez}'
    assert _row[1] == _mz, f'黄金清单自检失败: {_d} 月支实际{_row[1]} 应为{_mz}'
    _sn, _ = season_of(_row[1])
    assert _sn == _season, f'黄金清单自检失败: {_d} 季节实际{_sn} 应为{_season}'

# 反向自检：按规则表推导的 2026 全部命中日必须恰好等于黄金清单（双保险）
_rule_hits = {r[0] for r in CALENDAR if expected_by_rule(r[1], r[2], r[3])}
assert _rule_hits == set(AUTH_TIANSHE_2026), \
    f'规则推导与黄金清单不一致: 规则={sorted(_rule_hits)} 清单={sorted(AUTH_TIANSHE_2026)}'


# ===== 软件入口 adapters =====
def _mk_checker(cls_path):
    try:
        mod_path, cls_name = cls_path.rsplit('.', 1)
        mod = __import__(mod_path, fromlist=[cls_name])
        return getattr(mod, cls_name)()
    except Exception:
        return None


def adapter_base(inp):
    """① 基类计分入口（通用兜底 + 嫁娶/出行/开业/安葬/安床/作灶/动土 继承）"""
    month_zhi, day_gan, day_zhi = inp
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
        c = ShenShaChecker()
        return bool(c._is_tianshe({'month_zhi': month_zhi,
                                   'day_gan': day_gan, 'day_zhi': day_zhi}))
    except Exception:
        return _UNAVAILABLE


def adapter_override(cls_path):
    """②④⑤ 修造/入宅/拆舍 事项入口（删 override 后应与基类同表）"""
    def _ad(inp):
        month_zhi, day_gan, day_zhi = inp
        c = _mk_checker(cls_path)
        if c is None:
            return _UNAVAILABLE
        try:
            return bool(c._is_tianshe({'month_zhi': month_zhi,
                                       'day_gan': day_gan, 'day_zhi': day_zhi}))
        except Exception:
            return _UNAVAILABLE
    return _ad


def adapter_check_e2e(cls_path):
    """⑥ 端到端：check() 全链路输出的神煞列表应含/不含'天赦'"""
    def _ad(inp):
        date, month_zhi, day_gan, day_zhi = inp
        c = _mk_checker(cls_path)
        if c is None:
            return _UNAVAILABLE
        try:
            # 最小 sizhu：年柱用 sxtwl 立春切换口径；时柱不影响天赦判定
            import datetime
            y, m, d = (int(x) for x in date.split('-'))
            day = sxtwl.fromSolar(y, m, d)
            yg = day.getYearGZ()
            sizhu = {
                'year_gan': GAN[yg.tg], 'year_zhi': ZHI[yg.dz],
                'month_gan': '', 'month_zhi': month_zhi,
                'day_gan': day_gan, 'day_zhi': day_zhi,
                'hour_gan': '甲', 'hour_zhi': '子',
            }
            shensha_list = c.check(sizhu, [])
            names = [s['name'] for s in shensha_list if isinstance(s, dict)]
            return '天赦' in names or '天赦日' in names
        except Exception:
            return _UNAVAILABLE
    return _ad


inputs_cal = [(r[1], r[2], r[3]) for r in CALENDAR]          # 月支/日干/日支
inputs_full = [(r[0], r[1], r[2], r[3]) for r in CALENDAR]   # 含日期（端到端用）


def expected_hit(inp):
    month_zhi, day_gan, day_zhi = inp
    return expected_by_rule(month_zhi, day_gan, day_zhi)


def expected_e2e(inp):
    date = inp[0]
    return date in AUTH_TIANSHE_2026


# ===== 显式边界断言（修复后必须全绿；修复前基类入口会失败——此即错表证据） =====
def _d(dstr):
    return next(r for r in CALENDAR if r[0] == dstr)


_boundary_notes = []

# 边界1：2026-05-04 戊寅 + 立夏前一日（月支辰=春）→ 应命中"春戊寅"
_r = _d('2026-05-04')
assert (_r[2], _r[3]) == ('戊', '寅') and _r[1] == '辰', \
    f'边界日历自检失败: 2026-05-04 应为戊寅/月支辰，实测{_r[2]}{_r[3]}/{_r[1]}'
_boundary_notes.append('05-04 戊寅·月支辰(立夏前一日) → 应命中春戊寅（天赐测试点）')

# 边界2：2026-05-05 立夏日（月支巳=夏）→ 己卯非甲午，不应命中任何天赦
_r = _d('2026-05-05')
assert (_r[2], _r[3]) == ('己', '卯') and _r[1] == '巳', \
    f'边界日历自检失败: 2026-05-05 应为己卯/月支巳，实测{_r[2]}{_r[3]}/{_r[1]}'
_boundary_notes.append('05-05 己卯·月支巳(立夏日) → 入夏，戊寅失效且非甲午，不应命中')

# 边界3：2026-08-06 立秋前一日（月支未=夏）→ 壬子非甲午，不应命中
_r = _d('2026-08-06')
assert (_r[2], _r[3]) == ('壬', '子') and _r[1] == '未'
_boundary_notes.append('08-06 壬子·月支未(立秋前一日) → 仍属夏，非甲午不命中')

# 边界4：2026-08-07 立秋日（月支申=秋）→ 若为戊申应命中秋戊申（本年该日为癸丑，反例锁定月支切换）
_r = _d('2026-08-07')
assert (_r[2], _r[3]) == ('癸', '丑') and _r[1] == '申'
_boundary_notes.append('08-07 癸丑·月支申(立秋日) → 月支已切申（夏甲午失效），非戊申不命中')

# 边界5：2026-11-06/07 立冬交界（戌→亥）
_r1, _r2 = _d('2026-11-06'), _d('2026-11-07')
assert _r1[1] == '戌' and _r2[1] == '亥'
_boundary_notes.append('11-06 月支戌(秋)/11-07 月支亥(冬) → 节气切换无残留')

# 修复前基线证据（错表）：基类入口对 2026-03-05 真天赦应判 False（错表漏检）
# ——此断言在修复后转为 True 侧；脚本不因修复阶段不同而失效：统一断言
# "基类入口命中集合 == 权威清单"，修复前 FAIL 输出即为错表基线证据。

case_base = ShenShaCase(
    name='天赦(神煞基类·计分入口)',
    category='B',
    description='节气划季(月支等效)+全部命中；《协纪》春戊寅夏甲午秋戊申冬甲子；+25分',
    inputs=inputs_cal, expected=expected_hit, adapter=adapter_base, compare='bool',
)
case_xiuzao = ShenShaCase(
    name='天赦(修造神煞·删override后)',
    category='B',
    description='修造删 override 走继承，应与基类判定一致',
    inputs=inputs_cal, expected=expected_hit, adapter=adapter_override('modules.shensha.修造神煞.ConstructionShenShaChecker'), compare='bool',
)
case_ruzhai = ShenShaCase(
    name='天赦(入宅神煞·删override后)',
    category='B',
    description='入宅删 override 走继承，应与基类判定一致',
    inputs=inputs_cal, expected=expected_hit, adapter=adapter_override('modules.shensha.入宅神煞.RuZhaiShenShaChecker'), compare='bool',
)
case_chaishe = ShenShaCase(
    name='天赦(拆舍神煞·继承链)',
    category='B',
    description='拆舍继承修造；修造删 override 后拆舍→修造→基类链路不得断',
    inputs=inputs_cal, expected=expected_hit, adapter=adapter_override('modules.shensha.拆舍神煞.DemolitionShenShaChecker'), compare='bool',
)
case_jiaqu = ShenShaCase(
    name='天赦(嫁娶神煞·原错表事项)',
    category='B',
    description='嫁娶原继承基类错表，修复后应命中权威 6 天',
    inputs=inputs_cal, expected=expected_hit, adapter=adapter_override('modules.shensha.嫁娶神煞.MarriageShenShaChecker'), compare='bool',
)
case_e2e = ShenShaCase(
    name='天赦(修造check端到端)',
    category='B',
    description='check() 全链路：6 真日神煞列表含天赦，359 非日不含',
    inputs=inputs_full, expected=expected_e2e, adapter=adapter_check_e2e('modules.shensha.修造神煞.ConstructionShenShaChecker'), compare='bool',
)

# ===== 显式正/反断言（基类入口，修复后口径） =====
# --baseline 模式（TIANSHE_BASELINE=1）：修复前基线证据采集，跳过显式断言，
# 仅输出引擎统计对照（预期：错表误 7 漏 6）；正常模式断言必须全绿。
import os
_BASELINE = os.environ.get('TIANSHE_BASELINE') == '1'

if not _BASELINE:
    assert adapter_base(('卯', '戊', '寅')) is True, '正向：春(卯月)戊寅日应命中天赦'
    assert adapter_base(('未', '甲', '午')) is True, '正向：夏(未月)甲午日应命中天赦'
    assert adapter_base(('酉', '戊', '申')) is True, '正向：秋(酉月)戊申日应命中天赦'
    assert adapter_base(('子', '甲', '子')) is True, '正向：冬(子月)甲子日应命中天赦'
    assert adapter_base(('卯', '乙', '卯')) is False, '反向：春乙卯不是天赦（旧基类错表值，必须为False）'
    assert adapter_base(('巳', '丙', '午')) is False, '反向：夏丙午不是天赦（旧基类错表值，必须为False）'
    assert adapter_base(('申', '辛', '酉')) is False, '反向：秋辛酉不是天赦（旧基类错表值，必须为False）'
    assert adapter_base(('亥', '壬', '子')) is False, '反向：冬壬子不是天赦（旧基类错表值，必须为False）'
    assert adapter_base(('辰', '戊', '寅')) is True, '边界正向：辰月(暮春)戊寅应命中——05-04天赐测试点'
    assert adapter_base(('巳', '戊', '寅')) is False, '边界反向：巳月(入夏)戊寅不得再命中春戊寅'

if __name__ == '__main__':
    print('边界断言说明：')
    for _n in _boundary_notes:
        print('  -', _n)
    sys.exit(run_cli([case_base, case_xiuzao, case_ruzhai,
                      case_chaishe, case_jiaqu, case_e2e]))
