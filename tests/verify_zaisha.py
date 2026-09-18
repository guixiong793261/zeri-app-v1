# -*- coding: utf-8 -*-
"""
灾煞穷举验证（年支三合局 → 日支，三煞之"中神冲"位）
=====================================================
权威规则（《渊海子平》《三命通会》三煞体系：煞方帝旺位为灾煞，
即三合局中神之冲）：
    申子辰年 灾煞在午（子冲午）；巳酉丑年 灾煞在卯（酉冲卯）；
    寅午戌年 灾煞在子（午冲子）；亥卯未年 灾煞在酉（卯冲酉）。

注意：灾煞不是"劫煞对冲位"。神煞基类 _is_zaijiesha 先取一张错误劫煞表
再取六冲，与权威灾煞四局全不符——本脚本以引擎数据定性。

双入口对照：
  ① modules/shensha/神煞基类.py ShenShaChecker._is_zaijiesha
     —— 出行/修造/作灶/入宅/开业/通用神煞 继承计分（-25）
  ② modules/五行择日法.py NIAN_ZHI_XIONGSHEN['灾煞']
     —— 通书查表入口（get_nian_zhi_xiongshen）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，绝不从软件读取） =====
ZAISHA_TRUTH = {
    '申': '午', '子': '午', '辰': '午',   # 申子辰 → 午
    '巳': '卯', '酉': '卯', '丑': '卯',   # 巳酉丑 → 卯
    '寅': '子', '午': '子', '戌': '子',   # 寅午戌 → 子
    '亥': '酉', '卯': '酉', '未': '酉',   # 亥卯未 → 酉
}
assert set(ZAISHA_TRUTH) == set(DI_ZHI), '权威表必须覆盖12年支'


def expected(inp):
    year_zhi, day_zhi = inp
    return ZAISHA_TRUTH[year_zhi] == day_zhi


def _base_checker():
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
        return ShenShaChecker()
    except Exception:
        return None


def adapter_base(inp):
    year_zhi, day_zhi = inp
    c = _base_checker()
    if c is None:
        return _UNAVAILABLE
    try:
        return bool(c._is_zaijiesha({'year_zhi': year_zhi, 'day_zhi': day_zhi}))
    except Exception:
        return _UNAVAILABLE


def adapter_table(inp):
    year_zhi, day_zhi = inp
    try:
        from modules.五行择日法 import WuXingZeRiFa
        w = WuXingZeRiFa()
        return w.get_nian_zhi_xiongshen(year_zhi).get('灾煞', '') == day_zhi
    except Exception:
        return _UNAVAILABLE


inputs = [(y, z) for y in DI_ZHI for z in DI_ZHI]

case_base = ShenShaCase(
    name='灾煞(神煞基类·计分入口)',
    category='A',
    description='年支查日支；继承给全部事项checker，-25分',
    inputs=inputs, expected=expected, adapter=adapter_base, compare='bool',
)
case_table = ShenShaCase(
    name='灾煞(五行择日法·查表入口)',
    category='A',
    description='年支查日支；NIAN_ZHI_XIONGSHEN 字典',
    inputs=inputs, expected=expected, adapter=adapter_table, compare='bool',
)

# ===== 对"查表入口"的显式正/反断言 =====
assert adapter_table(('子', '午')) is True, '正向：子年(申子辰)见午应为灾煞'
assert adapter_table(('寅', '子')) is True, '正向：寅年(寅午戌)见子应为灾煞'
assert adapter_table(('子', '巳')) is False, '反向：子年见巳不是灾煞（巳为劫煞）'
assert adapter_table(('巳', '申')) is False, '反向：巳年(巳酉丑)灾煞在卯，申非'
assert adapter_table(('亥', '寅')) is False, '反向：亥年(亥卯未)灾煞在酉，寅非'

if __name__ == '__main__':
    sys.exit(run_cli([case_base, case_table]))
