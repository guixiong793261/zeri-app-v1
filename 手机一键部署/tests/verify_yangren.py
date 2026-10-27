# -*- coding: utf-8 -*-
"""
羊刃穷举验证
=============
定义：以日干查地支，命中即为羊刃。
口诀：甲刃在卯，乙刃在辰，丙戊刃在午，丁己刃在未，
      庚刃在酉，辛刃在戌，壬刃在子，癸刃在丑。
注：阴干羊刃存在流派争议（冠带派 vs 无羊刃派），本表取冠带派。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，冠带派） =====
YANGREN_TRUTH = {
    '甲': '卯', '乙': '辰', '丙': '午', '丁': '未',
    '戊': '午', '己': '未', '庚': '酉', '辛': '戌',
    '壬': '子', '癸': '丑',
}


def expected(inp):
    day_gan, zhi = inp
    return YANGREN_TRUTH.get(day_gan) == zhi


def adapter(inp):
    """经评分器 details['凶煞'] 列表判定是否含'羊刃'。"""
    day_gan, zhi = inp
    try:
        from modules.评分器 import Scorer
    except Exception:
        return _UNAVAILABLE
    sizhu = {'年柱': day_gan + zhi, '月柱': day_gan + zhi,
             '日柱': day_gan + zhi, '时柱': day_gan + zhi}
    try:
        details = Scorer()._generate_wu_xing_details(sizhu, owners=None)
        return any('羊刃' in str(x) for x in details.get('凶煞', []))
    except Exception:
        return _UNAVAILABLE


case = ShenShaCase(
    name='羊刃',
    category='A',
    description='日干查地支（甲刃在卯…冠带派）；评分器通用凶煞 -15，两见以上 -25',
    inputs=[(g, z) for g in TIAN_GAN for z in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='bool',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
