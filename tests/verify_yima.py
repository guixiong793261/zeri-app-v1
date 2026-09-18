# -*- coding: utf-8 -*-
"""
驿马穷举验证（三合局 → 马星地支）
=================================
权威规则（《渊海子平》：三合局第一字（长生）之冲为驿马）：
    申子辰 马在寅；巳酉丑 马在亥；
    寅午戌 马在申；亥卯未 马在巳。
年支、月支入三合局同理。

入口对照（共 6 个）：
  ① 神煞基类 ShenShaChecker._is_yima      —— 年支或月支任一命中（12×12×12 穷举）
  ② 出行 TravelShenShaChecker._is_yima    —— 年支
  ③ 修造 ConstructionShenShaChecker._is_yima —— 年支
  ④ 入宅 RuZhaiShenShaChecker._is_yima    —— 年支
  ⑤ 五行择日法 get_nian_zhi_jishen()['岁马'] —— 年支
  ⑥ 五行择日法 get_yue_zhi_jishen(月)['驿马'] —— 月支（正月建寅）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
# 农历月份 1-12 对应月支（正月建寅）
MONTH_ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']

# ===== 权威真值表（硬编码，绝不从软件读取） =====
YIMA_TRUTH = {
    '申': '寅', '子': '寅', '辰': '寅',   # 申子辰 → 寅
    '巳': '亥', '酉': '亥', '丑': '亥',   # 巳酉丑 → 亥
    '寅': '申', '午': '申', '戌': '申',   # 寅午戌 → 申
    '亥': '巳', '卯': '巳', '未': '巳',   # 亥卯未 → 巳
}
assert set(YIMA_TRUTH) == set(DI_ZHI), '权威表必须覆盖12支'


def exp_year(inp):
    year_zhi, day_zhi = inp
    return YIMA_TRUTH[year_zhi] == day_zhi


def exp_year_or_month(inp):
    year_zhi, month_zhi, day_zhi = inp
    return YIMA_TRUTH[year_zhi] == day_zhi or YIMA_TRUTH[month_zhi] == day_zhi


def exp_month(inp):
    month, day_zhi = inp
    return YIMA_TRUTH[MONTH_ZHI[month - 1]] == day_zhi


def _call(method_owner, method_name, sizhu):
    try:
        return bool(getattr(method_owner, method_name)(sizhu))
    except Exception:
        return _UNAVAILABLE


def adapter_base(inp):
    y, m, z = inp
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
        return _call(ShenShaChecker(), '_is_yima',
                     {'year_zhi': y, 'month_zhi': m, 'day_zhi': z})
    except Exception:
        return _UNAVAILABLE


def _make_year_adapter(module_path, class_name):
    def adapter(inp):
        y, z = inp
        try:
            mod = __import__(module_path, fromlist=[class_name])
            checker = getattr(mod, class_name)()
            return _call(checker, '_is_yima', {'year_zhi': y, 'day_zhi': z})
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


inputs_yz = [(y, z) for y in DI_ZHI for z in DI_ZHI]
inputs_ymz = [(y, m, z) for y in DI_ZHI for m in DI_ZHI for z in DI_ZHI]
inputs_mz = [(mo, z) for mo in range(1, 13) for z in DI_ZHI]

cases = [
    ShenShaCase(name='驿马(神煞基类·年或月)', category='A',
                description='年支或月支查日支，任一命中即真（1728穷举）',
                inputs=inputs_ymz, expected=exp_year_or_month,
                adapter=adapter_base, compare='bool'),
    ShenShaCase(name='驿马(出行神煞)', category='A', description='年支查日支',
                inputs=inputs_yz, expected=exp_year,
                adapter=_make_year_adapter('modules.shensha.出行神煞', 'TravelShenShaChecker'),
                compare='bool'),
    ShenShaCase(name='驿马(修造神煞)', category='A', description='年支查日支',
                inputs=inputs_yz, expected=exp_year,
                adapter=_make_year_adapter('modules.shensha.修造神煞', 'ConstructionShenShaChecker'),
                compare='bool'),
    ShenShaCase(name='驿马(入宅神煞)', category='A', description='年支查日支',
                inputs=inputs_yz, expected=exp_year,
                adapter=_make_year_adapter('modules.shensha.入宅神煞', 'RuZhaiShenShaChecker'),
                compare='bool'),
    ShenShaCase(name='岁马(五行择日法·年支)', category='A', description='年支查日支',
                inputs=inputs_yz, expected=exp_year, adapter=adapter_suima, compare='bool'),
    ShenShaCase(name='驿马(五行择日法·月支)', category='A',
                description='月份1-12（正月建寅）查日支',
                inputs=inputs_mz, expected=exp_month, adapter=adapter_yuema, compare='bool'),
]

# ===== 显式正/反断言（每入口取代表，至少1反向） =====
assert adapter_suima(('子', '寅')) is True, '正向：子年(申子辰)马在寅'
assert adapter_yuema((1, '申')) is True, '正向：正月(寅月，寅午戌)马在申'
assert adapter_suima(('子', '申')) is False, '反向：子年马在寅，申非'
assert adapter_yuema((1, '寅')) is False, '反向：寅月马在申，寅非'
assert _make_year_adapter('modules.shensha.出行神煞', 'TravelShenShaChecker')(('午', '寅')) is False, \
    '反向：午年(寅午戌)马在申，寅非'

if __name__ == '__main__':
    sys.exit(run_cli(cases))
