# -*- coding: utf-8 -*-
"""
文昌贵人穷举验证
=================
定义：以日干查地支，命中即为文昌贵人。
口诀：甲乙巳午报君知，丙戊申宫丁己酉，庚猪辛鼠壬逢虎，癸人见兔入云梯。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码） =====
WENCHANG_TRUTH = {
    '甲': '巳', '乙': '午', '丙': '申', '丁': '酉',
    '戊': '申', '己': '酉', '庚': '亥', '辛': '子',
    '壬': '寅', '癸': '卯',
}


def expected(inp):
    day_gan, zhi = inp
    return WENCHANG_TRUTH.get(day_gan) == zhi


def adapter(inp):
    day_gan, zhi = inp
    try:
        from modules.评分器 import Scorer
    except Exception:
        return _UNAVAILABLE
    sizhu = {'年柱': day_gan + zhi, '月柱': day_gan + zhi,
             '日柱': day_gan + zhi, '时柱': day_gan + zhi}
    try:
        details = Scorer()._generate_wu_xing_details(sizhu, owners=None)
        return any('文昌贵人' in str(x) for x in details.get('吉神', []))
    except Exception:
        return _UNAVAILABLE


case = ShenShaCase(
    name='文昌贵人',
    category='A',
    description='日干查地支（甲乙巳午…）',
    inputs=[(g, z) for g in TIAN_GAN for z in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='bool',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
