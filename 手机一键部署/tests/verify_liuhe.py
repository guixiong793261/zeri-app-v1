# -*- coding: utf-8 -*-
"""
六合穷举验证
=============
定义：子丑、寅亥、卯戌、辰酉、巳申、午未。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码） =====
LIUHE_TRUTH = {('子', '丑'), ('寅', '亥'), ('卯', '戌'), ('辰', '酉'), ('巳', '申'), ('午', '未')}


def expected(inp):
    a, b = inp
    return (a, b) in LIUHE_TRUTH or (b, a) in LIUHE_TRUTH


def adapter(inp):
    try:
        from modules.八字工具整合 import check_liuhe
    except Exception:
        return _UNAVAILABLE
    try:
        return bool(check_liuhe(inp[0], inp[1]))
    except Exception:
        return _UNAVAILABLE


case = ShenShaCase(
    name='六合',
    category='A',
    description='子丑寅亥卯戌辰酉巳申午未',
    inputs=[(a, b) for a in DI_ZHI for b in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='bool',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
