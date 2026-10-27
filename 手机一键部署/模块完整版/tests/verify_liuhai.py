# -*- coding: utf-8 -*-
"""
六害穷举验证
=============
定义：子未、丑午、寅巳、卯辰、申亥、酉戌。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码） =====
LIUHAI_TRUTH = {('子', '未'), ('丑', '午'), ('寅', '巳'), ('卯', '辰'), ('申', '亥'), ('酉', '戌')}


def expected(inp):
    a, b = inp
    return (a, b) in LIUHAI_TRUTH or (b, a) in LIUHAI_TRUTH


def adapter(inp):
    try:
        from modules.八字工具整合 import check_liuhai
    except Exception:
        return _UNAVAILABLE
    try:
        return bool(check_liuhai(inp[0], inp[1]))
    except Exception:
        return _UNAVAILABLE


case = ShenShaCase(
    name='六害',
    category='A',
    description='子未丑午寅巳卯辰申亥酉戌',
    inputs=[(a, b) for a in DI_ZHI for b in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='bool',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
