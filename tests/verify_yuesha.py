# -*- coding: utf-8 -*-
"""
月煞穷举验证（月支三合局 → 日支，口径拍板：月煞=月劫煞）
=========================================================
权威规则（《渊海子平》《三命通会》三煞体系：月煞取月支三合局旺方
对冲三方的第一辰，即月劫煞位）：
    寅午戌月 月煞在亥；巳酉丑月 月煞在寅；
    申子辰月 月煞在巳；亥卯未月 月煞在申。

口径说明（2026-09-18 用户拍板）：
  旧实现 docstring 标注"月煞（月虚）"但表值为对调错表，月虚/月劫煞
  两口径均不符。拍板统一走"月煞=月劫煞"口径；"月虚"（寅午戌月在丑、
  巳酉丑月在戌、申子辰月在未、亥卯未月在辰）为另一神煞，不与月煞混用。

入口：
  ① modules/shensha/神煞基类.py ShenShaChecker._is_yuesha
     —— 修造/作灶/入宅 继承计分（-20）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，绝不从软件读取） =====
YUESHA_TRUTH = {
    '寅': '亥', '午': '亥', '戌': '亥',   # 寅午戌月 → 亥
    '巳': '寅', '酉': '寅', '丑': '寅',   # 巳酉丑月 → 寅
    '申': '巳', '子': '巳', '辰': '巳',   # 申子辰月 → 巳
    '亥': '申', '卯': '申', '未': '申',   # 亥卯未月 → 申
}
assert set(YUESHA_TRUTH) == set(DI_ZHI), '权威表必须覆盖12月支'


def expected(inp):
    month_zhi, day_zhi = inp
    return YUESHA_TRUTH[month_zhi] == day_zhi


def adapter_base(inp):
    month_zhi, day_zhi = inp
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
        c = ShenShaChecker()
        return bool(c._is_yuesha({'month_zhi': month_zhi, 'day_zhi': day_zhi}))
    except Exception:
        return _UNAVAILABLE


inputs = [(m, z) for m in DI_ZHI for z in DI_ZHI]

case_base = ShenShaCase(
    name='月煞(神煞基类·计分入口)',
    category='A',
    description='月支查日支；修造/作灶/入宅继承，-20分；口径=月劫煞',
    inputs=inputs, expected=expected, adapter=adapter_base, compare='bool',
)

# ===== 显式正/反断言 =====
assert adapter_base(('寅', '亥')) is True, '正向：寅月(寅午戌)见亥应为月煞'
assert adapter_base(('申', '巳')) is True, '正向：申月(申子辰)见巳应为月煞'
assert adapter_base(('寅', '丑')) is False, '反向：寅月见丑不是月煞（丑为月虚位，口径已拍板不混用）'
assert adapter_base(('子', '亥')) is False, '反向：子月(申子辰)月煞在巳，亥非'
assert adapter_base(('卯', '寅')) is False, '反向：卯月(亥卯未)月煞在申，寅非'

if __name__ == '__main__':
    sys.exit(run_cli([case_base]))
