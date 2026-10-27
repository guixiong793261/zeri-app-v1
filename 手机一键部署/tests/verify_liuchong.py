# -*- coding: utf-8 -*-
"""
六冲穷举验证
=============
定义：子午、丑未、寅申、卯酉、辰戌、巳亥。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码） =====
LIUCHONG_TRUTH = {('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')}


def expected(inp):
    a, b = inp
    return (a, b) in LIUCHONG_TRUTH or (b, a) in LIUCHONG_TRUTH


def adapter(inp):
    try:
        from modules.八字工具整合 import check_liuchong
    except Exception:
        return _UNAVAILABLE
    try:
        return bool(check_liuchong(inp[0], inp[1]))
    except Exception:
        return _UNAVAILABLE


case = ShenShaCase(
    name='六冲',
    category='A',
    description='子午丑未寅申卯酉辰戌巳亥',
    inputs=[(a, b) for a in DI_ZHI for b in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='bool',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
