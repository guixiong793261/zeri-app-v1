# -*- coding: utf-8 -*-
"""
三合穷举验证
=============
定义：三支恰好构成申子辰水局 / 寅午戌火局 / 亥卯未木局 / 巳酉丑金局。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码） =====
SANHE_TRUTH = {
    frozenset({'申', '子', '辰'}): '水局',
    frozenset({'寅', '午', '戌'}): '火局',
    frozenset({'亥', '卯', '未'}): '木局',
    frozenset({'巳', '酉', '丑'}): '金局',
}


def expected(inp):
    z1, z2, z3 = inp
    return SANHE_TRUTH.get(frozenset({z1, z2, z3}))


def adapter(inp):
    try:
        from modules.八字工具整合 import check_sanhe
    except Exception:
        return _UNAVAILABLE
    try:
        return check_sanhe(list(inp))
    except Exception:
        return _UNAVAILABLE


case = ShenShaCase(
    name='三合',
    category='A',
    description='申子辰/寅午戌/亥卯未/巳酉丑',
    inputs=[(a, b, c) for a in DI_ZHI for b in DI_ZHI for c in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='eq',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
