# -*- coding: utf-8 -*-
"""
天乙贵人穷举验证
=================
定义：以日干查地支，命中即为天乙贵人。
口诀：甲戊庚牛羊（丑未），乙己鼠猴乡（子申），丙丁猪鸡位（亥酉），
      壬癸兔蛇藏（卯巳），六辛逢马虎（寅午）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码） =====
TIANYI_TRUTH = {
    '甲': ['丑', '未'], '戊': ['丑', '未'], '庚': ['丑', '未'],
    '乙': ['子', '申'], '己': ['子', '申'],
    '丙': ['亥', '酉'], '丁': ['亥', '酉'],
    '辛': ['寅', '午'],
    '壬': ['卯', '巳'], '癸': ['卯', '巳'],
}


def expected(inp):
    day_gan, zhi = inp
    return zhi in TIANYI_TRUTH.get(day_gan, [])


def adapter(inp):
    """经评分器吉神列表判定是否含'天乙贵人'。"""
    day_gan, zhi = inp
    try:
        from modules.评分器 import Scorer
    except Exception:
        return _UNAVAILABLE
    sizhu = {'年柱': day_gan + zhi, '月柱': day_gan + zhi,
             '日柱': day_gan + zhi, '时柱': day_gan + zhi}
    try:
        details = Scorer()._generate_wu_xing_details(sizhu, owners=None)
        return any('天乙贵人' in str(x) for x in details.get('吉神', []))
    except Exception:
        return _UNAVAILABLE


case = ShenShaCase(
    name='天乙贵人',
    category='A',
    description='日干查地支（甲戊庚牛羊…）',
    inputs=[(g, z) for g in TIAN_GAN for z in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='bool',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
