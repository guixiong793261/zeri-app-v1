# -*- coding: utf-8 -*-
"""
劫煞穷举验证（年支三合局 → 日支）
=================================
权威规则（《渊海子平》《三命通会》三煞体系：煞方长生位为劫煞）：
    申子辰年 劫煞在巳；巳酉丑年 劫煞在寅；
    寅午戌年 劫煞在亥；亥卯未年 劫煞在申。

双入口对照：
  ① modules/shensha/神煞基类.py ShenShaChecker._is_jiesha
     —— 出行/修造/作灶/入宅/开业/通用神煞 等全部事项 checker 经继承命中
     （2026-10-12 §66 起识别展示不计分，score 置 0）
  ② modules/五行择日法.py WuXingZeRiFa.NIAN_ZHI_XIONGSHEN['劫煞']
     —— 通书查表入口（get_nian_zhi_xiongshen）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，绝不从软件读取） =====
JIESHA_TRUTH = {
    '申': '巳', '子': '巳', '辰': '巳',   # 申子辰 → 巳
    '巳': '寅', '酉': '寅', '丑': '寅',   # 巳酉丑 → 寅
    '寅': '亥', '午': '亥', '戌': '亥',   # 寅午戌 → 亥
    '亥': '申', '卯': '申', '未': '申',   # 亥卯未 → 申
}
assert set(JIESHA_TRUTH) == set(DI_ZHI), '权威表必须覆盖12年支'


def expected(inp):
    year_zhi, day_zhi = inp
    return JIESHA_TRUTH[year_zhi] == day_zhi


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
        return bool(c._is_jiesha({'year_zhi': year_zhi, 'day_zhi': day_zhi}))
    except Exception:
        return _UNAVAILABLE


def adapter_table(inp):
    year_zhi, day_zhi = inp
    try:
        from modules.五行择日法 import WuXingZeRiFa
        w = WuXingZeRiFa()
        return w.get_nian_zhi_xiongshen(year_zhi).get('劫煞', '') == day_zhi
    except Exception:
        return _UNAVAILABLE


inputs = [(y, z) for y in DI_ZHI for z in DI_ZHI]

case_base = ShenShaCase(
    name='劫煞(神煞基类·计分入口)',
    category='A',
    description='年支查日支；继承给全部事项checker；§66 起识别展示不计分',
    inputs=inputs, expected=expected, adapter=adapter_base, compare='bool',
)
case_table = ShenShaCase(
    name='劫煞(五行择日法·查表入口)',
    category='A',
    description='年支查日支；NIAN_ZHI_XIONGSHEN 字典',
    inputs=inputs, expected=expected, adapter=adapter_table, compare='bool',
)

# ===== 对"查表入口"的显式正/反断言（每神煞≥1反向断言） =====
assert adapter_table(('子', '巳')) is True, '正向：子年(申子辰)见巳应为劫煞'
assert adapter_table(('寅', '亥')) is True, '正向：寅年(寅午戌)见亥应为劫煞'
assert adapter_table(('子', '亥')) is False, '反向：子年见亥不是劫煞（亥为寅午戌局劫煞）'
assert adapter_table(('寅', '巳')) is False, '反向：寅年见巳不是劫煞（巳为申子辰局劫煞）'
assert adapter_table(('酉', '午')) is False, '反向：巳酉丑局劫煞在寅，午非'

if __name__ == '__main__':
    sys.exit(run_cli([case_base, case_table]))
