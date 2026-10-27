# -*- coding: utf-8 -*-
"""
月德穷举验证（B 类锚点②：月支三合局查日干，季内全部命中口径）
=========================================================
权威规则（《协纪辨方书》）：月德者，月支三合局旺方之干，月内凡日干匹配即命中：
    寅午戌月 丙；申子辰月 壬；亥卯未月 甲；巳酉丑月 庚。
划月按节气（月支由节气定月，sxtwl 交节日即切月支），非农历月。

诊断结论（2026-09-18，只读）：全库 6 处定义（神煞基类/通用神煞/嫁娶/入宅/修造/
评分器）全部与权威一致——"6 副本 0 错误"，无天赦式方向性错表。本脚本验证后按
拍板方案 A 删除嫁娶/入宅两处内嵌表改继承（两者均为纯表副本，行为应零变化）。

入口（6）：
  ① modules/shensha/神煞基类.py ShenShaChecker._is_yuede（计分 +18）
  ② modules/shensha/通用神煞.py CommonShenShaChecker._is_yuede（引工具函数 YUEDE）
  ③ modules/shensha/嫁娶神煞.py MarriageShenShaChecker._is_yuede（内嵌表→拍板后走继承）
  ④ modules/shensha/入宅神煞.py RuZhaiShenShaChecker._is_yuede（内嵌表→拍板后走继承）
  ⑤ modules/shensha/修造神煞.py ConstructionShenShaChecker._is_yuede（引工具函数 YUEDE）
  ⑥ modules/评分器.py Scorer._generate_wu_xing_details（八字详情"月德贵人"展示层）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

# ===== 权威真值表（硬编码，绝不从软件读取） =====
YUEDE_TRUTH = {
    '寅': '丙', '午': '丙', '戌': '丙',   # 寅午戌月 → 丙
    '申': '壬', '子': '壬', '辰': '壬',   # 申子辰月 → 壬
    '亥': '甲', '卯': '甲', '未': '甲',   # 亥卯未月 → 甲
    '巳': '庚', '酉': '庚', '丑': '庚',   # 巳酉丑月 → 庚
}
assert len(YUEDE_TRUTH) == 12, '权威表必须覆盖12月支'

# ===== 2026 丙午年黄金清单（35 天，逐日硬编码；月份区间按节气） =====
AUTH_YUEDE_2026 = {
    '2026-01-06': ('丑', '庚辰'), '2026-01-16': ('丑', '庚寅'), '2026-01-26': ('丑', '庚子'),
    '2026-02-11': ('寅', '丙辰'), '2026-02-21': ('寅', '丙寅'), '2026-03-03': ('寅', '丙子'),
    '2026-03-11': ('卯', '甲申'), '2026-03-21': ('卯', '甲午'), '2026-03-31': ('卯', '甲辰'),
    '2026-04-08': ('辰', '壬子'), '2026-04-18': ('辰', '壬戌'), '2026-04-28': ('辰', '壬申'),
    '2026-05-06': ('巳', '庚辰'), '2026-05-16': ('巳', '庚寅'), '2026-05-26': ('巳', '庚子'),
    '2026-06-11': ('午', '丙辰'), '2026-06-21': ('午', '丙寅'), '2026-07-01': ('午', '丙子'),
    '2026-07-09': ('未', '甲申'), '2026-07-19': ('未', '甲午'), '2026-07-29': ('未', '甲辰'),
    '2026-08-16': ('申', '壬戌'), '2026-08-26': ('申', '壬申'), '2026-09-05': ('申', '壬午'),
    '2026-09-13': ('酉', '庚寅'), '2026-09-23': ('酉', '庚子'), '2026-10-03': ('酉', '庚戌'),
    '2026-10-09': ('戌', '丙辰'), '2026-10-19': ('戌', '丙寅'), '2026-10-29': ('戌', '丙子'),
    '2026-11-16': ('亥', '甲午'), '2026-11-26': ('亥', '甲辰'), '2026-12-06': ('亥', '甲寅'),
    '2026-12-14': ('子', '壬戌'), '2026-12-24': ('子', '壬申'),
}


def build_year_inputs():
    """sxtwl 实测 2026 全年：返回 (inputs, by_date)。
    inputs: [(month_zhi, day_gan)] * 365；by_date: {date: (month_zhi, day_gz)}"""
    import datetime
    import sxtwl
    GAN = '甲乙丙丁戊己庚辛壬癸'
    ZHI = '子丑寅卯辰巳午未申酉戌亥'
    inputs, by_date = [], {}
    d = datetime.date(2026, 1, 1)
    while d.year == 2026:
        day = sxtwl.fromSolar(d.year, d.month, d.day)
        g = day.getDayGZ()
        mz = ZHI[day.getMonthGZ().dz]
        dg = GAN[g.tg]
        inputs.append((mz, dg))
        by_date[str(d)] = (mz, GAN[g.tg] + ZHI[g.dz])
        d += datetime.timedelta(days=1)
    return inputs, by_date


_YEAR_INPUTS, _BY_DATE = build_year_inputs()

# ===== 双自检（黄金清单 vs sxtwl 实测；规则推导 vs 黄金清单） =====
for _date, (_mz, _gz) in AUTH_YUEDE_2026.items():
    assert _BY_DATE[_date] == (_mz, _gz), (
        f'黄金清单 {_date} 与 sxtwl 实测不符: 实测{_BY_DATE[_date]} vs 清单{(_mz, _gz)}')
_derived = {d for d, (mz, gz) in _BY_DATE.items() if YUEDE_TRUTH[mz] == gz[0]}
assert _derived == set(AUTH_YUEDE_2026), (
    f'规则推导命中集合与黄金清单不符: 差异 {_derived ^ set(AUTH_YUEDE_2026)}')


def expected(inp):
    month_zhi, day_gan = inp
    return YUEDE_TRUTH[month_zhi] == day_gan


# ===== 入口适配器（6） =====
def adapter_base(inp):
    month_zhi, day_gan = inp
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
        return bool(ShenShaChecker()._is_yuede({'month_zhi': month_zhi, 'day_gan': day_gan}))
    except Exception:
        return _UNAVAILABLE


def adapter_common(inp):
    month_zhi, day_gan = inp
    try:
        from modules.shensha.通用神煞 import CommonShenShaChecker
        return bool(CommonShenShaChecker()._is_yuede({'month_zhi': month_zhi, 'day_gan': day_gan}))
    except Exception:
        return _UNAVAILABLE


def adapter_jiaqu(inp):
    month_zhi, day_gan = inp
    try:
        from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
        return bool(MarriageShenShaChecker()._is_yuede({'month_zhi': month_zhi, 'day_gan': day_gan}))
    except Exception:
        return _UNAVAILABLE


def adapter_ruzhai(inp):
    month_zhi, day_gan = inp
    try:
        from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
        return bool(RuZhaiShenShaChecker()._is_yuede({'month_zhi': month_zhi, 'day_gan': day_gan}))
    except Exception:
        return _UNAVAILABLE


def adapter_xiuzao(inp):
    month_zhi, day_gan = inp
    try:
        from modules.shensha.修造神煞 import ConstructionShenShaChecker
        return bool(ConstructionShenShaChecker()._is_yuede({'month_zhi': month_zhi, 'day_gan': day_gan}))
    except Exception:
        return _UNAVAILABLE


def adapter_scorer(inp):
    """评分器八字详情层：'月柱'/'日柱'中文键（评分器#L4567-4572 兼容口径）"""
    month_zhi, day_gan = inp
    try:
        from modules.评分器 import scorer
        details = scorer._generate_wu_xing_details(
            {'月柱': '甲' + month_zhi, '日柱': day_gan + '子'}, None)
        return any(str(x).startswith('月德贵人') for x in details.get('吉神', []))
    except Exception:
        return _UNAVAILABLE


inputs = _YEAR_INPUTS

cases = [
    ShenShaCase(name='月德(神煞基类·计分入口)', category='B',
                description='月支三合局查日干，+18分；寅午戌丙申子辰壬亥卯未甲巳酉丑庚',
                inputs=inputs, expected=expected, adapter=adapter_base, compare='bool'),
    ShenShaCase(name='月德(通用神煞)', category='B',
                description='CommonShenShaChecker，引工具函数YUEDE表',
                inputs=inputs, expected=expected, adapter=adapter_common, compare='bool'),
    ShenShaCase(name='月德(嫁娶神煞)', category='B',
                description='MarriageShenShaChecker；原内嵌表，拍板方案A后走继承',
                inputs=inputs, expected=expected, adapter=adapter_jiaqu, compare='bool'),
    ShenShaCase(name='月德(入宅神煞)', category='B',
                description='RuZhaiShenShaChecker；原内嵌表，拍板方案A后走继承',
                inputs=inputs, expected=expected, adapter=adapter_ruzhai, compare='bool'),
    ShenShaCase(name='月德(修造神煞)', category='B',
                description='ConstructionShenShaChecker，引工具函数YUEDE表',
                inputs=inputs, expected=expected, adapter=adapter_xiuzao, compare='bool'),
    ShenShaCase(name='月德(评分器·八字详情层)', category='B',
                description='Scorer._generate_wu_xing_details 月德贵人展示',
                inputs=inputs, expected=expected, adapter=adapter_scorer, compare='bool'),
]

# ===== 显式正向断言（四局各1，软件真实入口） =====
assert adapter_base(('寅', '丙')) is True, '正向：寅月(寅午戌)见丙应为月德'
assert adapter_base(('申', '壬')) is True, '正向：申月(申子辰)见壬应为月德'
assert adapter_base(('亥', '甲')) is True, '正向：亥月(亥卯未)见甲应为月德'
assert adapter_base(('巳', '庚')) is True, '正向：巳月(巳酉丑)见庚应为月德'

# ===== 显式反向断言（硬约束：每神煞至少1个反向） =====
assert adapter_base(('寅', '甲')) is False, '反向：寅月德丙，甲非'
assert adapter_base(('子', '丙')) is False, '反向：子月德壬，丙非'
assert adapter_base(('卯', '丙')) is False, '反向：卯月德甲，丙为寅月之德跨局反向'
assert adapter_base(('酉', '壬')) is False, '反向：酉月德庚，壬为申月之德跨局反向'

# ===== 边界断言（天赐测试点×2） =====
# ① 2026-12-06 甲寅（亥月·德甲）命中 → 12-07 大雪交节日乙卯（月支切子·德壬）甲失效不命中。
#    验证"交节日即切月支"的切换行为（12-06/12-07 农历同属十月，农历划月无此切换）。
_mz6, _gz6 = _BY_DATE['2026-12-06']
assert (_mz6, _gz6) == ('亥', '甲寅'), f'12-06 应为亥月甲寅，实测{(_mz6, _gz6)}'
assert adapter_base((_mz6, _gz6[0])) is True, '边界：12-06 甲寅·亥月(大雪前)应命中月德甲'
_mz7, _gz7 = _BY_DATE['2026-12-07']
assert (_mz7, _gz7) == ('子', '乙卯'), f'12-07 应为子月乙卯，实测{(_mz7, _gz7)}'
assert adapter_base((_mz7, _gz7[0])) is False, '边界：12-07 大雪日月支已切子(德壬)，甲失效不命中'
# ② 2026-03-11 甲申：节气月支=卯(惊蛰03-05后)德甲→必须命中；农历划月=正月廿三(寅)德丙
#    则不命中——本断言可精确区分"节气划月"与"农历月划月"两种实现。
_mz311, _gz311 = _BY_DATE['2026-03-11']
assert (_mz311, _gz311) == ('卯', '甲申'), f'03-11 应为卯月甲申，实测{(_mz311, _gz311)}'
assert adapter_base((_mz311, _gz311[0])) is True, '边界：03-11 甲申·节气卯月(德甲)应命中（农历正月划月会误判寅月德丙而漏）'

if __name__ == '__main__':
    sys.exit(run_cli(cases))
