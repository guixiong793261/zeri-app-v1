# -*- coding: utf-8 -*-
"""
禄神穷举验证
=============
定义：以日干查地支，命中即为禄神。
口诀：甲禄在寅，乙禄在卯，丙戊禄在巳，丁己禄在午，
      庚禄在申，辛禄在酉，壬禄在亥，癸禄在子。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码） =====
LUSHEN_TRUTH = {
    '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
    '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
    '壬': '亥', '癸': '子',
}


def expected(inp):
    day_gan, zhi = inp
    return LUSHEN_TRUTH.get(day_gan) == zhi


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
        return any('禄神' in str(x) for x in details.get('吉神', []))
    except Exception:
        return _UNAVAILABLE


case = ShenShaCase(
    name='禄神',
    category='A',
    description='日干查地支（甲禄在寅…）',
    inputs=[(g, z) for g in TIAN_GAN for z in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='bool',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
