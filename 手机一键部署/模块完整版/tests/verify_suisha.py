# -*- coding: utf-8 -*-
"""
岁煞穷举验证（年支三合局 → 日支，三煞之"墓库"位）
===================================================
权威规则（《渊海子平》《三命通会》三煞体系：煞方墓库位为岁煞）：
    申子辰年 岁煞在未；巳酉丑年 岁煞在辰；
    寅午戌年 岁煞在丑；亥卯未年 岁煞在戌。

双入口对照：
  ① modules/shensha/神煞基类.py ShenShaChecker._is_suisha
     —— 通用神煞/拆舍 继承计分；动土神煞.py 内有同表 override（复制同一张错表）
  ② modules/五行择日法.py NIAN_ZHI_XIONGSHEN['岁煞']
     —— 通书查表入口（get_nian_zhi_xiongshen）

注：基类 docstring 称"岁煞与劫煞同（四孟煞位）"为错误说法——
    劫煞在煞方长生（四孟），岁煞在煞方墓库（四季），二者并不同位。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，绝不从软件读取） =====
SUISHA_TRUTH = {
    '申': '未', '子': '未', '辰': '未',   # 申子辰 → 未
    '巳': '辰', '酉': '辰', '丑': '辰',   # 巳酉丑 → 辰
    '寅': '丑', '午': '丑', '戌': '丑',   # 寅午戌 → 丑
    '亥': '戌', '卯': '戌', '未': '戌',   # 亥卯未 → 戌
}
assert set(SUISHA_TRUTH) == set(DI_ZHI), '权威表必须覆盖12年支'


def expected(inp):
    year_zhi, day_zhi = inp
    return SUISHA_TRUTH[year_zhi] == day_zhi


def adapter_base(inp):
    year_zhi, day_zhi = inp
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
        c = ShenShaChecker()
        return bool(c._is_suisha({'year_zhi': year_zhi, 'day_zhi': day_zhi}))
    except Exception:
        return _UNAVAILABLE


def adapter_dongtu(inp):
    """动土神煞自带的同名 override（复制表，预期与基类同错）。"""
    year_zhi, day_zhi = inp
    try:
        from modules.shensha.动土神煞 import DiggingShenShaChecker
        c = DiggingShenShaChecker()
        return bool(c._is_suisha({'year_zhi': year_zhi, 'day_zhi': day_zhi}))
    except Exception:
        return _UNAVAILABLE


def adapter_table(inp):
    year_zhi, day_zhi = inp
    try:
        from modules.五行择日法 import WuXingZeRiFa
        w = WuXingZeRiFa()
        return w.get_nian_zhi_xiongshen(year_zhi).get('岁煞', '') == day_zhi
    except Exception:
        return _UNAVAILABLE


inputs = [(y, z) for y in DI_ZHI for z in DI_ZHI]

case_base = ShenShaCase(
    name='岁煞(神煞基类·计分入口)',
    category='A',
    description='年支查日支；通用神煞/拆舍继承',
    inputs=inputs, expected=expected, adapter=adapter_base, compare='bool',
)
case_dongtu = ShenShaCase(
    name='岁煞(动土神煞·override)',
    category='A',
    description='动土神煞内复制的同名实现',
    inputs=inputs, expected=expected, adapter=adapter_dongtu, compare='bool',
)
case_table = ShenShaCase(
    name='岁煞(五行择日法·查表入口)',
    category='A',
    description='年支查日支；NIAN_ZHI_XIONGSHEN 字典',
    inputs=inputs, expected=expected, adapter=adapter_table, compare='bool',
)

# ===== 对"查表入口"的显式正/反断言 =====
assert adapter_table(('子', '未')) is True, '正向：子年(申子辰)见未应为岁煞'
assert adapter_table(('寅', '丑')) is True, '正向：寅年(寅午戌)见丑应为岁煞'
assert adapter_table(('子', '亥')) is False, '反向：子年见亥不是岁煞（墓库在未）'
assert adapter_table(('巳', '寅')) is False, '反向：巳年(巳酉丑)岁煞在辰，寅非'
assert adapter_table(('亥', '申')) is False, '反向：亥年(亥卯未)岁煞在戌，申非'

if __name__ == '__main__':
    sys.exit(run_cli([case_base, case_dongtu, case_table]))
