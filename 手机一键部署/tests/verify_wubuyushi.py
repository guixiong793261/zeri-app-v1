# -*- coding: utf-8 -*-
"""
五不遇时穷举验证（样板）
=========================

定义：时干克日干，且阴阳属性相同。
权威表（10 日干，共 12 个五不遇时）：
  甲→庚午  乙→辛巳  丙→壬辰  丁→癸卯  戊→甲寅
  己→乙丑、乙亥  庚→丙子、丙戌  辛→丁酉  壬→戊申  癸→己未

适配器同时调用软件三处实现（今日黄历.is_wubuyu / 修造 / 嫁娶），
三处必须一致；不一致则以 'DISAGREE' 暴露跨入口口径分歧。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
WUSHU_DUN = {'甲': '甲', '己': '甲', '乙': '丙', '庚': '丙',
             '丙': '戊', '辛': '戊', '丁': '庚', '壬': '庚', '戊': '壬', '癸': '壬'}


def hour_pillar(day_gan, hour_zhi):
    zi_idx = TIAN_GAN.index(WUSHU_DUN[day_gan])
    zhi_idx = DI_ZHI.index(hour_zhi)
    return TIAN_GAN[(zi_idx + zhi_idx) % 10] + hour_zhi


# ===== 权威真值表（硬编码） =====
WUBUYUSHI_TRUTH = {
    '甲': ['午'], '乙': ['巳'], '丙': ['辰'], '丁': ['卯'],
    '戊': ['寅'], '己': ['丑', '亥'], '庚': ['子', '戌'],
    '辛': ['酉'], '壬': ['申'], '癸': ['未'],
}


def expected(inp):
    day_gan, hour_zhi = inp
    return hour_zhi in WUBUYUSHI_TRUTH.get(day_gan, [])


def _is_wubuyu_standalone(day_gan, hour_zhi):
    try:
        from modules.今日黄历 import is_wubuyu
    except Exception:
        return _UNAVAILABLE
    hp = hour_pillar(day_gan, hour_zhi)
    try:
        return bool(is_wubuyu(hp[0], day_gan))
    except Exception:
        return _UNAVAILABLE


def _is_wubuyu_xiuzao(day_gan, hour_zhi):
    try:
        from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
    except Exception:
        return _UNAVAILABLE
    try:
        try:
            checker = ConstructionShenShaCheckerExt(zuoshan=None, zhuming=None)
        except TypeError:
            checker = ConstructionShenShaCheckerExt()
        hp = hour_pillar(day_gan, hour_zhi)
        sizhu = {'year_gan': '甲', 'year_zhi': '子', 'month_gan': '甲', 'month_zhi': '子',
                 'day_gan': day_gan, 'day_zhi': '子', 'hour_gan': hp[0], 'hour_zhi': hour_zhi}
        lucky = checker.get_lucky_hours(sizhu)
        for h in lucky or []:
            if h.get('地支') == hour_zhi:
                text = ' '.join(str(x) for x in (h.get('说明') or []))
                return '五不遇时' in text
        return False
    except Exception:
        return _UNAVAILABLE


def _is_wubuyu_jiaqu(day_gan, hour_zhi):
    try:
        from modules.shensha.嫁娶神煞扩展 import MarriageShenShaCheckerExt
    except Exception:
        return _UNAVAILABLE
    try:
        checker = MarriageShenShaCheckerExt(bride_gan='甲', bride_zhi='子',
                                            groom_gan='甲', groom_zhi='丑')
        hp = hour_pillar(day_gan, hour_zhi)
        sizhu = {'year_gan': '甲', 'year_zhi': '子', 'month_gan': '甲', 'month_zhi': '子',
                 'day_gan': day_gan, 'day_zhi': '子', 'hour_gan': hp[0], 'hour_zhi': hour_zhi}
        lucky = checker.get_lucky_hours(sizhu)
        for h in lucky or []:
            if h.get('地支') == hour_zhi:
                text = ' '.join(str(x) for x in (h.get('说明') or []))
                return '五不遇时' in text
        return False
    except Exception:
        return _UNAVAILABLE


def adapter(inp):
    """三入口一致性校验：全 True→True，全 False→False，不一致→'DISAGREE'。"""
    day_gan, hour_zhi = inp
    r1 = _is_wubuyu_standalone(day_gan, hour_zhi)
    r2 = _is_wubuyu_xiuzao(day_gan, hour_zhi)
    r3 = _is_wubuyu_jiaqu(day_gan, hour_zhi)
    if r1 is _UNAVAILABLE or r2 is _UNAVAILABLE or r3 is _UNAVAILABLE:
        return _UNAVAILABLE
    if r1 == r2 == r3:
        return r1
    return f'DISAGREE(standalone={r1},xiuzao={r2},jiaqu={r3})'


case = ShenShaCase(
    name='五不遇时',
    category='A',
    description='时干克日干且阴阳同（12 个）；三入口一致性校验',
    inputs=[(g, z) for g in TIAN_GAN for z in DI_ZHI],
    expected=expected,
    adapter=adapter,
    compare='bool',
)


if __name__ == '__main__':
    sys.exit(run_cli([case]))
