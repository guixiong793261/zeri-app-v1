# -*- coding: utf-8 -*-
"""
截路空亡时 穷举验证（《协纪辨方书》卷七·义例五）
==================================================
权威规则（《历例》+《考原》）：
    甲己日申酉时，乙庚日午未时，丙辛日辰巳时，
    丁壬日寅卯时，戊癸日子丑戌亥时。
推法原理：五鼠遁起甲子，得壬申癸酉之时为截路空亡
（壬癸属水，行路遇水不可行）。

D4 重建背景：原"路空日"误作日支神煞（日干五合查日支），与典载
时辰神煞维度错位，且戊癸缺戌亥。A1 正名为"截路空亡"时辰凶煞。

入口：
  ① TravelShenShaChecker._is_jielu_kongwang（谓词层）
  ② pipeline shensha_list 端到端（时神煞发射，分值 -15）

独立运行：python tests/verify_jielu.py    退出码 0=通过 1=失败
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli
from modules.shensha.出行神煞 import TravelShenShaChecker

_GAN = '甲乙丙丁戊己庚辛壬癸'
_ZHI = '子丑寅卯辰巳午未申酉戌亥'

# ===== 权威表（硬编码，绝不从软件读取） =====
AUTH = {
    '甲': ['申', '酉'], '己': ['申', '酉'],
    '乙': ['午', '未'], '庚': ['午', '未'],
    '丙': ['辰', '巳'], '辛': ['辰', '巳'],
    '丁': ['寅', '卯'], '壬': ['寅', '卯'],
    '戊': ['子', '丑', '戌', '亥'], '癸': ['子', '丑', '戌', '亥']
}

_c = TravelShenShaChecker()


def _ad_pred(sz):
    return _c._is_jielu_kongwang(sz)


# 全量输入：10干×12支 = 120 组合
INPUTS = [{'day_gan': g, 'hour_zhi': z} for g in _GAN for z in _ZHI]


def _exp(sz):
    return sz['hour_zhi'] in AUTH.get(sz['day_gan'], [])


# ===== 显式边界断言（含戊癸四时辰专项） =====
_notes = []

# 边界1：戊癸四时辰专项（D4 阶段2 新增发现：戊癸空子丑戌亥四时辰）
for g in ['戊', '癸']:
    for z in ['子', '丑', '戌', '亥']:
        assert _c._is_jielu_kongwang({'day_gan': g, 'hour_zhi': z}), f'{g}日{z}时应命中'
    for z in ['寅', '卯', '辰', '巳', '午', '未', '申', '酉']:
        assert not _c._is_jielu_kongwang({'day_gan': g, 'hour_zhi': z}), f'{g}日{z}时不应命中'
_notes.append('戊癸四时辰边界：子丑戌亥命中、其余8支不命中（2干×4=8命中）')

# 边界2：其余八干各 2 时辰
for g in ['甲', '己', '乙', '庚', '丙', '辛', '丁', '壬']:
    cnt = sum(1 for z in _ZHI if _c._is_jielu_kongwang({'day_gan': g, 'hour_zhi': z}))
    assert cnt == 2, f'{g}日应 2 个空亡时辰，实际 {cnt}'
_notes.append('八干各 2 时辰边界：甲己/乙庚/丙辛/丁壬各 2 个空亡时辰')

# 边界3：pipeline 端到端（时神煞发射 + 分值 -15）
sz = {'day_gan': '甲', 'hour_zhi': '申', 'day_zhi': '子',
      'month_zhi': '寅', 'year_zhi': '午'}
_c.check(sz)
jl = [x for x in _c.shensha_list if isinstance(x, dict) and x.get('name') == '截路空亡']
assert len(jl) == 1, f'甲日申时应发射截路空亡 1 条，实际 {len(jl)}'
assert jl[0].get('score') == -15, f'截路空亡应 -15，实际 {jl[0].get("score")}'
_notes.append('pipeline 端到端：甲日申时发射截路空亡 -15')

# 边界4：非空亡时辰不发射
sz2 = {'day_gan': '甲', 'hour_zhi': '子', 'day_zhi': '子',
       'month_zhi': '寅', 'year_zhi': '午'}
_c2 = TravelShenShaChecker()
_c2.check(sz2)
jl2 = [x for x in _c2.shensha_list if isinstance(x, dict) and x.get('name') == '截路空亡']
assert len(jl2) == 0, '甲日子时不应发射截路空亡'
_notes.append('反向断言：甲日子时不发射截路空亡')

cases = [
    ShenShaCase(name='截路空亡(谓词层·10干×12支穷举)', category='B',
                description='《协纪》卷七：甲己申酉/乙庚午未/丙辛辰巳/丁壬寅卯/戊癸子丑戌亥',
                inputs=INPUTS, expected=_exp, adapter=_ad_pred, compare='bool'),
]


if __name__ == '__main__':
    print('边界断言说明：')
    for _n in _notes:
        print('  -', _n)
    sys.exit(run_cli(cases))
