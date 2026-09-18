# -*- coding: utf-8 -*-
"""
三刑穷举验证
=============
定义（两支相刑）：
  无礼之刑：子卯
  无恩之刑：寅巳、巳申、申寅
  恃势之刑：丑戌、戌未、未丑
  自刑：辰辰、午午、酉酉、亥亥（同支相见）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码） =====
XING_TRUTH = {
    ('子', '卯'): '无礼之刑', ('卯', '子'): '无礼之刑',
    ('寅', '巳'): '无恩之刑', ('巳', '寅'): '无恩之刑',
    ('巳', '申'): '无恩之刑', ('申', '巳'): '无恩之刑',
    ('申', '寅'): '无恩之刑', ('寅', '申'): '无恩之刑',
    ('丑', '戌'): '恃势之刑', ('戌', '丑'): '恃势之刑',
    ('戌', '未'): '恃势之刑', ('未', '戌'): '恃势之刑',
    ('未', '丑'): '恃势之刑', ('丑', '未'): '恃势之刑',
    ('辰', '辰'): '自刑', ('午', '午'): '自刑',
    ('酉', '酉'): '自刑', ('亥', '亥'): '自刑',
}


def expected(inp):
    return XING_TRUTH.get((inp[0], inp[1]))


def adapter(inp):
    try:
        from modules.八字工具整合 import check_xing
    except Exception:
        return _UNAVAILABLE
    try:
        return check_xing(inp[0], inp[1])
    except Exception:
        return _UNAVAILABLE


case = ShenShaCase(
    name='三刑',
    category='A',
    description='子卯/寅巳申/丑戌未/辰午酉亥自刑',
    inputs=[(a, b) for a in DI_ZHI for b in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='eq',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
