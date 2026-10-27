# -*- coding: utf-8 -*-
"""
相破穷举验证
=============
定义（六破）：子酉、丑辰、寅亥、卯午、巳申、未戌。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码） =====
PO_TRUTH = {('子', '酉'), ('丑', '辰'), ('寅', '亥'), ('卯', '午'), ('巳', '申'), ('未', '戌')}


def expected(inp):
    a, b = inp
    return (a, b) in PO_TRUTH or (b, a) in PO_TRUTH


def adapter(inp):
    try:
        from modules.八字工具整合 import check_po
    except Exception:
        return _UNAVAILABLE
    try:
        return bool(check_po(inp[0], inp[1]))
    except Exception:
        return _UNAVAILABLE


case = ShenShaCase(
    name='相破',
    category='A',
    description='子酉丑辰寅亥卯午巳申未戌',
    inputs=[(a, b) for a in DI_ZHI for b in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='bool',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
