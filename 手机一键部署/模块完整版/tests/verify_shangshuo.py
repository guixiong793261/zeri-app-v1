# -*- coding: utf-8 -*-
"""
上朔日穷举验证（桩函数普查 P2：第五种排查产出，第四种失效模式"桩函数死链路"第二例）
=========================================================================================
权威规则（年干推算，与婚嫁评分算法原有活实现同源，2026-09-20 用户拍板口径）：
    阳年（甲丙戊庚壬）：年干顺推三位，取该干【亥】日；
    阴年（乙丁己辛癸）：年干顺推四位，取该干【巳】日。
    年干以立春为年界（sxtwl.getYearGZ 在立春前自然返回上一年干支）。
    例：丙午阳年 丙+3=己 → 己亥日；乙巳阴年 乙+4=己 → 己巳日。

失效背景（2026-09-20 桩函数普查 P2）：
    神煞基类.ShenShaChecker._is_shangshuo 原为 return False 桩（旧注"需要公历
    日期信息"，且 docstring 误作"农历初一"），导致基类 pipeline '上朔日' -10
    及全部继承子类（通用/出行/开业/修造/入宅/安葬/作灶/安床/嫁娶神煞类等）
    全年 0 命中；唯婚嫁评分算法 score_marriage_day 有独立年干推算活实现（-35）。
    修复：算法下沉为 shensha 层唯一实现 is_shangshuo_by_ganzhi，基类桩改调它，
    婚嫁算法改委托（逐字等价）。分值按用户拍板 A 保留事项差：非婚嫁 -10、
    婚嫁 -35（SHENSHA_SCORES 未动）。

2026 丙午（阳）权威黄金清单（硬编码，sxtwl 独立推导双保险）：
    己亥日 5 天：03-26 / 05-25 / 07-24 / 09-22 / 11-21
阴年/跨年边界：
    2025-01-18 丁亥（尚属甲辰阳年，立春前年界）；
    2025 立春后乙巳阴年己巳日 6 天：03-01/04-30/06-29/08-28/10-27/12-26；
    2027-01-20 己亥（尚属丙午阳年）；2027-03-03 辛巳（丁未阴年立春后）。

入口：
  ① modules/shensha/神煞基类.py::is_shangshuo_by_ganzhi —— 全项目唯一实现（模块级）
  ② ShenShaChecker._is_shangshuo —— 非婚嫁 pipeline -10
  ③ modules/婚嫁评分算法.py::is_shangshuo —— 委托（-35 路径）
  ④ score_marriage_day details 端到端（-35）
  ⑤ 12 个 shensha checker pipeline 端到端（shensha_list 含上朔日 -10）
  动土 DiggingShenShaChecker 不调 super 且自有日检表无上朔项（13.1 活分支架构债，
  本轮不改，单独断言锁定现状，防未来无声变化）。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli

import sxtwl

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威黄金清单（硬编码，绝不从软件读取） =====
AUTH_2026 = {'2026-03-26', '2026-05-25', '2026-07-24', '2026-09-22', '2026-11-21'}
# 2025 全年（含立春前年界）：01-18 属甲辰阳年→丁亥；其余乙巳阴年→己巳
AUTH_2025 = {'2025-01-18': '丁亥',
             '2025-03-01': '己巳', '2025-04-30': '己巳', '2025-06-29': '己巳',
             '2025-08-28': '己巳', '2025-10-27': '己巳', '2025-12-26': '己巳'}
# 2027 年初边界段：01-20 属丙午阳年→己亥；03-03 属丁未阴年→辛巳
AUTH_2027_HEAD = {'2027-01-20': '己亥', '2027-03-03': '辛巳'}


def _expected_for(d):
    """sxtwl 独立推导（权威双保险：不读软件实现）"""
    day = sxtwl.fromSolar(d.year, d.month, d.day)
    yg = GAN[day.getYearGZ().tg]
    dg = GAN[day.getDayGZ().tg]
    dz = ZHI[day.getDayGZ().dz]
    yi = GAN.index(yg)
    di = GAN.index(dg)
    if yi % 2 == 0:
        return dg == GAN[(yi + 3) % 10] and dz == '亥'
    return dg == GAN[(yi + 4) % 10] and dz == '巳'


def _daterange(y1, m1, d1, y2, m2, d2):
    cur = datetime.date(y1, m1, d1)
    end = datetime.date(y2, m2, d2)
    while cur <= end:
        yield cur
        cur += datetime.timedelta(days=1)


def _d(y, m, dd):
    return datetime.date(y, m, dd)


# ===== 黄金清单自检：sxtwl 推导必须与硬编码完全一致 =====
_calc_2026 = {d.isoformat() for d in _daterange(2026, 1, 1, 2026, 12, 31) if _expected_for(d)}
assert _calc_2026 == AUTH_2026, f'2026 黄金清单自检失败: {sorted(_calc_2026)}'
_calc_2025 = {d.isoformat() for d in _daterange(2025, 1, 1, 2025, 12, 31) if _expected_for(d)}
assert _calc_2025 == set(AUTH_2025), f'2025 黄金清单自检失败: {sorted(_calc_2025)}'
_calc_2027h = {d.isoformat() for d in _daterange(2027, 1, 1, 2027, 3, 10) if _expected_for(d)}
assert _calc_2027h == set(AUTH_2027_HEAD), f'2027 边界段自检失败: {sorted(_calc_2027h)}'
# 干支构成自检
assert AUTH_2025['2025-01-18'] == '丁亥'
assert all(v == '己巳' for k, v in AUTH_2025.items() if k != '2025-01-18')
assert AUTH_2027_HEAD['2027-01-20'] == '己亥' and AUTH_2027_HEAD['2027-03-03'] == '辛巳'


INPUTS_2026 = list(_daterange(2026, 1, 1, 2026, 12, 31))
INPUTS_2025 = list(_daterange(2025, 1, 1, 2025, 12, 31))
INPUTS_2027_HEAD = list(_daterange(2027, 1, 1, 2027, 3, 10))

# ===== 入口①：公共函数（唯一实现） =====
from modules.shensha.神煞基类 import is_shangshuo_by_ganzhi, ShenShaChecker
from modules.四柱计算器 import calculate_sizhu


def _ad_func(d):
    day = sxtwl.fromSolar(d.year, d.month, d.day)
    gz = day.getDayGZ()
    return is_shangshuo_by_ganzhi(GAN[day.getYearGZ().tg], GAN[gz.tg], ZHI[gz.dz])


# ===== 入口②：基类 _is_shangshuo =====
_base = ShenShaChecker()


def _ad_base(d):
    sz = calculate_sizhu(d, 12, 0)
    return bool(_base._is_shangshuo(sz))


# ===== 入口③：婚嫁评分算法委托 =====
from modules.婚嫁评分算法 import is_shangshuo as _hj_impl, score_marriage_day


def _ad_hj(d):
    sz = calculate_sizhu(d, 12, 0)
    return bool(_hj_impl(d, sz))


def _exp_2026(d):
    return d.isoformat() in AUTH_2026


def _exp_2025(d):
    return d.isoformat() in AUTH_2025


def _exp_2027(d):
    return d.isoformat() in AUTH_2027_HEAD


# ===== 入口⑤：12 checker pipeline 端到端（-10），动土排除 =====
from modules.shensha.修造神煞 import ConstructionShenShaChecker
from modules.shensha.拆舍神煞 import DemolitionShenShaChecker
from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
from modules.shensha.安葬神煞 import BurialShenShaChecker
from modules.shensha.作灶神煞 import StoveShenShaChecker
from modules.shensha.安床神煞 import BedShenShaChecker
from modules.shensha.开业神煞 import OpeningShenShaChecker
from modules.shensha.出行神煞 import TravelShenShaChecker
from modules.shensha.通用神煞 import CommonShenShaChecker
from modules.shensha.动土神煞 import DiggingShenShaChecker

_PIPE = [
    ('基类', ShenShaChecker), ('修造', ConstructionShenShaChecker),
    ('拆舍', DemolitionShenShaChecker), ('修造扩展', ConstructionShenShaCheckerExt),
    ('嫁娶神煞类', MarriageShenShaChecker), ('入宅', RuZhaiShenShaChecker),
    ('安葬', BurialShenShaChecker), ('作灶', StoveShenShaChecker),
    ('安床', BedShenShaChecker), ('开业', OpeningShenShaChecker),
    ('出行', TravelShenShaChecker), ('通用', CommonShenShaChecker),
]


def _pipe_ad(tag):
    cls = next(c for t, c in _PIPE if t == tag)

    def _ad(d):
        sz = calculate_sizhu(d, 12, 0)
        c = cls()
        c.check(sz)
        return any(isinstance(x, dict) and x.get('name') == '上朔日' for x in c.shensha_list)
    return _ad


def _pipe_score_ad(tag):
    """分值锁定：命中日上朔条目必须恰好 -10"""
    cls = next(c for t, c in _PIPE if t == tag)

    def _ad(d):
        sz = calculate_sizhu(d, 12, 0)
        c = cls()
        c.check(sz)
        scores = [x.get('score') for x in c.shensha_list
                  if isinstance(x, dict) and x.get('name') == '上朔日']
        return scores == [-10]
    return _ad


# ===== 入口④：婚嫁 score_marriage_day details -35 =====
def _ad_marriage(d):
    r = score_marriage_day(d)
    return any(x[0] == '上朔日' and x[1] == -35 for x in r.get('details', []))


# ===== 显式边界断言 =====
_notes = []

# 边界1：阳年黄金日命中 + 邻近反例
assert _ad_func(_d(2026, 3, 26)) and _ad_base(_d(2026, 3, 26)) and _ad_hj(_d(2026, 3, 26))
assert not _ad_func(_d(2026, 3, 25)), '03-25 戊戌日不应命中'
assert not _ad_func(_d(2026, 3, 27)), '03-27 庚子日不应命中'
_notes.append('03-26 己亥命中（阳年丙+3）/ 03-25、03-27 邻近反例不命中')

# 边界2：立春年界（2025-01-18 尚属甲辰阳年→丁亥，非己巳）
assert _ad_func(_d(2025, 1, 18)), '2025-01-18 甲辰阳年丁亥日应命中'
assert not _ad_func(_d(2025, 1, 19)), '2025-01-19 次日不应命中'
_notes.append('2025-01-18 丁亥命中（立春前取甲辰阳年），年界正确')

# 边界3：阴年己巳（乙+4=己）+ 跨年2027（01-20丙午阳年己亥 / 03-03丁未阴年辛巳）
assert _ad_func(_d(2025, 3, 1)), '乙巳阴年己巳日应命中'
assert _ad_func(_d(2027, 1, 20)), '2027-01-20 尚属丙午阳年→己亥应命中'
assert _ad_func(_d(2027, 3, 3)), '2027-03-03 丁未阴年→辛巳应命中'
assert not _ad_func(_d(2027, 2, 1)), '2027-02-01 不应命中'
_notes.append('阴年己巳/辛巳 + 2027 跨年双边界（01-20 己亥、03-03 辛巳）')

# 边界4：三入口 2025+2026+2027段 逐日完全一致（口径单一实现）
for _d0 in INPUTS_2025 + INPUTS_2026 + INPUTS_2027_HEAD:
    _a, _b, _c = _ad_func(_d0), _ad_base(_d0), _ad_hj(_d0)
    assert _a == _b == _c, f'{_d0} 三入口不一致: {_a}/{_b}/{_c}'
_notes.append('公共函数/基类/婚嫁算法 三入口 2025-2027 共 766 天逐日一致')

# 边界5：分值事项差（非婚嫁 -10、婚嫁 -35，用户拍板A）
_r = score_marriage_day(_d(2026, 3, 26))
assert [x for x in _r['details'] if x[0] == '上朔日'] == [('上朔日', -35)]
_op = OpeningShenShaChecker()
_op.check(calculate_sizhu(_d(2026, 3, 26), 12, 0))
assert [x.get('score') for x in _op.shensha_list if isinstance(x, dict) and x.get('name') == '上朔日'] == [-10]
_notes.append('分值事项差锁定：婚嫁 -35 / 非婚嫁 -10（SHENSHA_SCORES 未动）')

# 边界6：动土活分支现状锁定（不调 super、自有日检表无上朔项 → 不命中）
_dt = DiggingShenShaChecker()
_dt.check(calculate_sizhu(_d(2026, 3, 26), 12, 0))
assert not any(isinstance(x, dict) and x.get('name') == '上朔日' for x in _dt.shensha_list), \
    '动土若开始命中上朔，说明 13.1 活分支架构已变化，需人工复核'
_notes.append('动土不命中上朔＝13.1"不调super活分支"既有架构，本轮不改（锁定防漂移）')

# 边界7：黄金清单构成
assert len(AUTH_2026) == 5 and len(AUTH_2025) == 7 and len(AUTH_2027_HEAD) == 2
_notes.append('黄金清单：2026 阳年5天 / 2025 7天(含年界1) / 2027边界段2天')


cases = [
    ShenShaCase(name='上朔日(公共函数唯一实现·2026穷举)', category='A',
                description='阳年丙+3取亥：365 天中 5 个己亥日命中、360 天不命中',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_ad_func, compare='bool'),
    ShenShaCase(name='上朔日(神煞基类_is_shangshuo桩复活)', category='A',
                description='原 return False 桩改调公共函数；2026 五天命中',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_ad_base, compare='bool'),
    ShenShaCase(name='上朔日(婚嫁算法委托·口径一致)', category='A',
                description='本地推算改委托，命中集合 2026 五天不变',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_ad_hj, compare='bool'),
    ShenShaCase(name='上朔日(阴年+立春年界·2025全年)', category='A',
                description='01-18 甲辰阳年丁亥 + 乙巳阴年六己巳，共 7 天',
                inputs=INPUTS_2025, expected=_exp_2025, adapter=_ad_func, compare='bool'),
    ShenShaCase(name='上朔日(跨年边界段2027)', category='A',
                description='01-20 丙午阳年己亥 / 03-03 丁未阴年辛巳',
                inputs=INPUTS_2027_HEAD, expected=_exp_2027, adapter=_ad_func, compare='bool'),
    ShenShaCase(name='上朔日(婚嫁score_marriage_day端到端-35)', category='A',
                description='details 含(上朔日,-35)；委托前后零行为差异',
                inputs=INPUTS_2026, expected=_exp_2026, adapter=_ad_marriage, compare='bool'),
]

for _tag, _ in _PIPE:
    cases.append(ShenShaCase(
        name=f'pipeline({_tag}·上朔-10端到端)', category='A',
        description='shensha_list 在五个己亥日含上朔日、其余 360 天不含',
        inputs=INPUTS_2026, expected=_exp_2026, adapter=_pipe_ad(_tag), compare='bool'))

# 抽 4 个 checker 锁分值（避免用例膨胀，代表基类/修造系/安葬系/通用）
for _tag in ('基类', '修造', '安葬', '通用'):
    cases.append(ShenShaCase(
        name=f'pipeline({_tag}·分值-10锁定)', category='A',
        description='五个命中日上朔条目分值必须恰为 -10（非婚嫁口径）',
        inputs=sorted(_d(2026, int(iso[5:7]), int(iso[8:10])) for iso in AUTH_2026),
        expected=lambda d: True, adapter=_pipe_score_ad(_tag), compare='bool'))


if __name__ == '__main__':
    print('边界断言说明：')
    for _n in _notes:
        print('  -', _n)
    sys.exit(run_cli(cases))
