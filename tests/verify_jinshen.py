# -*- coding: utf-8 -*-
"""金神 验证 —— 年家方位煞（《协纪》体系）

口径（2026-09-21 拍板）：
    金神为年神，按年干查方位，主开山立向修方之吉凶，不用于日课评分。
    废弃原日家金神桩（按日干查、恒 False、概念误为六甲旬空亡）。

年干口诀：
    甲己年：午、未、申、酉
    乙庚年：辰、巳
    丙辛年：子、丑、寅、卯、午、未
    丁壬年：寅、卯、戌、亥
    戊癸年：申、酉、子、丑

入口：
  ① ShenShaChecker._get_jinshen_positions(year_gan) —— 年干方位表
  ② ConstructionShenShaCheckerExt.check —— 坐山犯金神方位 → '金神到山' -15
  ③ 日课评分路径（ShenShaChecker._check_day_shensha）不再产出'金神'条目
"""
import sys, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli
from modules.四柱计算器 import calculate_sizhu
from modules.shensha.神煞基类 import ShenShaChecker
from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt


# 权威年干方位表（硬编码，5 组年干口诀，绝不从软件读取）
# 年界：年干取 calculate_sizhu 年柱，sxtwl 以【立春】换年柱（非正月初一），
# 故金神年家方位同样以立春为界。
AUTH_JINSHEN = {
    '甲': ['午', '未', '申', '酉'],
    '己': ['午', '未', '申', '酉'],
    '乙': ['辰', '巳'],
    '庚': ['辰', '巳'],
    '丙': ['子', '丑', '寅', '卯', '午', '未'],
    '辛': ['子', '丑', '寅', '卯', '午', '未'],
    '丁': ['寅', '卯', '戌', '亥'],
    '壬': ['寅', '卯', '戌', '亥'],
    '戊': ['申', '酉', '子', '丑'],
    '癸': ['申', '酉', '子', '丑'],
}

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']


def _ad_positions(inp):
    gan = inp[0]
    return tuple(ShenShaChecker()._get_jinshen_positions(gan))


# 山向接入：2024 甲辰年，金神方位午未申酉；坐山午 → 犯金神到山
def _ad_jinshen_daoshan(d_and_shan):
    d, shan = d_and_shan
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d
    c = ConstructionShenShaCheckerExt(zuoshan=shan)
    c.check(sz)
    return any(isinstance(x, dict) and x.get('name') == '金神到山' for x in c.shensha_list)


def _expected_daoshan(d_and_shan):
    d, shan = d_and_shan
    sz = calculate_sizhu(d, 12, 0)
    year_gan = sz.get('year_gan', '')
    # 坐山转地支
    shan_zhi_map = {
        '子':'子','丑':'丑','艮':'丑','寅':'寅','卯':'卯','辰':'辰','巽':'辰',
        '巳':'巳','午':'午','未':'未','坤':'未','申':'申','酉':'酉','戌':'戌',
        '乾':'亥','亥':'亥',
    }
    shan_zhi = shan_zhi_map.get(shan, shan)
    return shan_zhi in AUTH_JINSHEN.get(year_gan, [])


# 日课评分路径不再有金神条目
def _ad_no_jinshen_day(inp):
    d = inp[0]
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d
    c = ShenShaChecker()
    c.check(sz)
    return any(isinstance(x, dict) and '金神' in str(x.get('name', '')) for x in c.shensha_list)


# ===== 边界断言 =====
_notes = []
# 年干方位表逐干校验
for g in TIAN_GAN:
    assert list(ShenShaChecker()._get_jinshen_positions(g)) == AUTH_JINSHEN[g], \
        f'{g}年 金神方位不符'
_notes.append('年干方位表：10干全量校验通过')

# 山向正例：2024-06-01 甲辰年，坐山午（金神方位）
_d2024 = datetime.date(2024, 6, 1)
assert _ad_jinshen_daoshan((_d2024, '午')), '2024甲辰年午山应犯金神到山'
# 山向反例：2024-06-01 坐山子（不在金神方位午未申酉）
assert not _ad_jinshen_daoshan((_d2024, '子')), '2024甲辰年子山不应犯金神'
_notes.append('山向接入：2024甲辰年午山犯金神/子山不犯')

# 日家桩废弃：任意日 check 不产出金神条目
assert not _ad_no_jinshen_day((datetime.date(2026, 5, 1),)), '日课评分路径不应产出金神条目'
_notes.append('日家桩废弃：_check_day_shensha 无金神条目')

# 年界：立春换年柱（2026 立春=02-04，sxtwl 当天即换丙午；02-03 仍乙巳）
# 乙年金神在辰巳；丙年金神在子丑寅卯午未。午山/辰山交叉断言：
assert not _ad_jinshen_daoshan((datetime.date(2026, 2, 3), '午')), \
    '立春前 02-03 年干乙（金神辰巳），午山不应犯金神'
assert _ad_jinshen_daoshan((datetime.date(2026, 2, 4), '午')), \
    '立春当天 02-04 年干换丙（金神含午），午山应犯金神到山'
assert _ad_jinshen_daoshan((datetime.date(2026, 2, 3), '辰')), \
    '立春前 02-03 年干乙（金神辰巳），辰山应犯金神到山'
assert not _ad_jinshen_daoshan((datetime.date(2026, 2, 4), '辰')), \
    '立春当天 02-04 年干换丙（金神不含辰），辰山不应犯金神'
_notes.append('年界锁：2026-02-03 乙巳 vs 02-04 立春换丙午，午/辰山交叉断言通过')


# 穷举：年干方位表
cases = [
    ShenShaCase(name='金神(年干方位表·10干)', category='B',
                description='甲己午未申酉/乙庚辰巳/丙辛子丑寅卯午未/丁壬寅卯戌亥/戊癸申酉子丑',
                inputs=[(g,) for g in TIAN_GAN],
                expected=lambda g: tuple(AUTH_JINSHEN[g[0]]),
                adapter=_ad_positions),
    ShenShaCase(name='金神(日课评分路径无金神条目·2026穷举)', category='B',
                description='废弃日家金神桩，_check_day_shensha 全年无金神条目',
                inputs=[(datetime.date(2026, 1, 1) + datetime.timedelta(days=i),)
                        for i in range(365)],
                expected=lambda d: False,
                adapter=_ad_no_jinshen_day, compare='bool'),
]


if __name__ == '__main__':
    run_cli(cases)
