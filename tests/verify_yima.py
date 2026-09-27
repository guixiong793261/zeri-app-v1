# -*- coding: utf-8 -*-
"""
驿马穷举验证（三合局 → 马星地支）
=================================
2026-10 A6-4 D 批次重构：日辰层驿马口径统一为「仅月支」。

典籍依据（用户拍板 D=典籍直解）：
  《协纪辨方书》卷六·义例四（月神）驿马条——《神枢经》："驿马者，驿骑也，
  其日宜封赠官爵、诏命公卿、远行赴任、移徙迁居"；李鼎祚："正月起申，
  逆行四孟"。逐月即申巳寅亥循环，与月支三合冲支表完全一致。
  年支驿马为年家方位神「岁马到山」（卷十五，开山立向修方吉），已由
  修造神煞扩展._is_sui_ma_daoshan 独立实现，不参日辰吉凶判断。

权威真值表（三合局第一字之冲，硬编码，绝不从软件读取）：
    申子辰 马在寅；巳酉丑 马在亥；
    寅午戌 马在申；亥卯未 马在巳。

入口对照（D 批次后共 4 类，日辰层全部同一口径=仅月支）：
  ① 神煞基类 ShenShaChecker._is_yima            —— 月支（12×12 穷举）
  ② 出行/修造/入宅三 checker                     —— override 已删，继承基类=月支
     （动土/拆舍经 MRO 承修造，同为月支）
  ③ 五行择日法 get_yue_zhi_jishen(月)['驿马']    —— 月支（正月建寅，展示层）
  ④ 五行择日法 get_nian_zhi_jishen()['岁马']     —— 年支（方位神，独立保留）

跨实现等价硬断言：日辰层 ①② 六 checker 对同一 sizhu 必须返回同一布尔值
（旧版缺陷：6 入口各按"各自语义"断言，把基类年∪月 vs 三 override 仅年支
的口径分歧固化进期望值，从未断言跨实现等价，故 2448 样本 0 差异却漏报分歧）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
MONTH_ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']

YIMA_TRUTH = {
    '申': '寅', '子': '寅', '辰': '寅',
    '巳': '亥', '酉': '亥', '丑': '亥',
    '寅': '申', '午': '申', '戌': '申',
    '亥': '巳', '卯': '巳', '未': '巳',
}
assert set(YIMA_TRUTH) == set(DI_ZHI), '权威表必须覆盖12支'


def exp_month_zhi(inp):
    """日辰层统一期望：仅月支。"""
    month_zhi, day_zhi = inp
    return YIMA_TRUTH[month_zhi] == day_zhi


def exp_year(inp):
    year_zhi, day_zhi = inp
    return YIMA_TRUTH[year_zhi] == day_zhi


def exp_month_num(inp):
    month, day_zhi = inp
    return YIMA_TRUTH[MONTH_ZHI[month - 1]] == day_zhi


def _call(owner, method_name, sizhu):
    try:
        return bool(getattr(owner, method_name)(sizhu))
    except Exception:
        return _UNAVAILABLE


def _make_month_adapter(module_path, class_name):
    """月支口径 adapter：传 (月支, 日支)。"""
    def adapter(inp):
        m, z = inp
        try:
            mod = __import__(module_path, fromlist=[class_name])
            checker = getattr(mod, class_name)()
            return _call(checker, '_is_yima',
                         {'year_zhi': '子', 'month_zhi': m, 'day_zhi': z})
        except Exception:
            return _UNAVAILABLE
    return adapter


def adapter_suima(inp):
    y, z = inp
    try:
        from modules.五行择日法 import WuXingZeRiFa
        return WuXingZeRiFa().get_nian_zhi_jishen(y).get('岁马', '') == z
    except Exception:
        return _UNAVAILABLE


def adapter_yuema(inp):
    month, z = inp
    try:
        from modules.五行择日法 import WuXingZeRiFa
        return WuXingZeRiFa().get_yue_zhi_jishen(month).get('驿马', '') == z
    except Exception:
        return _UNAVAILABLE


inputs_mz = [(m, z) for m in DI_ZHI for z in DI_ZHI]
inputs_yz = [(y, z) for y in DI_ZHI for z in DI_ZHI]
inputs_mnum_z = [(mo, z) for mo in range(1, 13) for z in DI_ZHI]

cases = [
    ShenShaCase(name='驿马(神煞基类·月支)', category='A',
                description='仅月支查日支（144穷举）',
                inputs=inputs_mz, expected=exp_month_zhi,
                adapter=_make_month_adapter('modules.shensha.神煞基类', 'ShenShaChecker'),
                compare='bool'),
    ShenShaCase(name='驿马(出行神煞·继承基类)', category='A', description='月支查日支',
                inputs=inputs_mz, expected=exp_month_zhi,
                adapter=_make_month_adapter('modules.shensha.出行神煞', 'TravelShenShaChecker'),
                compare='bool'),
    ShenShaCase(name='驿马(修造神煞·继承基类)', category='A', description='月支查日支',
                inputs=inputs_mz, expected=exp_month_zhi,
                adapter=_make_month_adapter('modules.shensha.修造神煞', 'ConstructionShenShaChecker'),
                compare='bool'),
    ShenShaCase(name='驿马(入宅神煞·继承基类)', category='A', description='月支查日支',
                inputs=inputs_mz, expected=exp_month_zhi,
                adapter=_make_month_adapter('modules.shensha.入宅神煞', 'RuZhaiShenShaChecker'),
                compare='bool'),
    ShenShaCase(name='驿马(动土神煞·MRO承修造)', category='A', description='月支查日支',
                inputs=inputs_mz, expected=exp_month_zhi,
                adapter=_make_month_adapter('modules.shensha.动土神煞', 'DiggingShenShaChecker'),
                compare='bool'),
    ShenShaCase(name='驿马(拆舍神煞·MRO承修造)', category='A', description='月支查日支',
                inputs=inputs_mz, expected=exp_month_zhi,
                adapter=_make_month_adapter('modules.shensha.拆舍神煞', 'DemolitionShenShaChecker'),
                compare='bool'),
    ShenShaCase(name='驿马(五行择日法·月支)', category='A',
                description='月份1-12（正月建寅）查日支',
                inputs=inputs_mnum_z, expected=exp_month_num, adapter=adapter_yuema, compare='bool'),
    ShenShaCase(name='岁马(五行择日法·年支·方位神)', category='A',
                description='年支查日支（岁马到山，独立保留）',
                inputs=inputs_yz, expected=exp_year, adapter=adapter_suima, compare='bool'),
]

# ===== 跨实现等价硬断言：六 checker 同一 sizhu 必须同值 =====
def _cross_impl_equiv():
    mods = [('modules.shensha.神煞基类', 'ShenShaChecker'),
            ('modules.shensha.出行神煞', 'TravelShenShaChecker'),
            ('modules.shensha.修造神煞', 'ConstructionShenShaChecker'),
            ('modules.shensha.入宅神煞', 'RuZhaiShenShaChecker'),
            ('modules.shensha.动土神煞', 'DiggingShenShaChecker'),
            ('modules.shensha.拆舍神煞', 'DemolitionShenShaChecker')]
    checkers = []
    for mp, cn in mods:
        mod = __import__(mp, fromlist=[cn])
        checkers.append(getattr(mod, cn)())
    n_diff = 0
    for y in DI_ZHI:
        for m in DI_ZHI:
            for z in DI_ZHI:
                sz = {'year_zhi': y, 'month_zhi': m, 'day_zhi': z}
                vals = {bool(c._is_yima(sz)) for c in checkers}
                if len(vals) != 1:
                    n_diff += 1
    return n_diff


# ===== 显式正/反断言 =====
_base = _make_month_adapter('modules.shensha.神煞基类', 'ShenShaChecker')
_travel = _make_month_adapter('modules.shensha.出行神煞', 'TravelShenShaChecker')
assert _base(('寅', '申')) is True, '正向：寅月(寅午戌)马在申'
assert _base(('寅', '寅')) is False, '反向：寅月马在申，寅非'
assert _travel(('申', '寅')) is True, '正向：申月(申子辰)马在寅（出行）'
assert _travel(('申', '申')) is False, '反向：申月马在寅，申非（出行）'
assert adapter_suima(('子', '寅')) is True, '正向：子年(申子辰)岁马在寅'
assert adapter_suima(('子', '申')) is False, '反向：子年岁马在寅，申非'
assert adapter_yuema((1, '申')) is True, '正向：正月(寅月)驿马在申'
assert adapter_yuema((1, '寅')) is False, '反向：寅月驿马在申，寅非'

if __name__ == '__main__':
    n_diff = _cross_impl_equiv()
    assert n_diff == 0, f'跨实现等价失败：日辰层 6 checker 存在 {n_diff} 个分歧格'
    print(f'跨实现等价断言：6 checker × 1728 格 0 分歧 ✓')
    sys.exit(run_cli(cases))
