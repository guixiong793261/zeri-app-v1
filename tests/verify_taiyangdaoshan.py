# -*- coding: utf-8 -*-
"""太阳/太阴到山到向 穷举验证（B3，跟踪项22）—— sxtwl 二十四节气过宫口径

权威口径（《协纪辨方书》太阳二十四节气过宫）：
    冬至日太阳到子山，其后每交一节气顺行一山；节气日当天即属新段（交节换宫）。
    山序（冬至起）：子癸丑艮寅甲卯乙辰巽巳丙午丁未坤申庚酉辛戌乾亥壬。
    太阴与太阳恒对冲（相差六宫十二山）：太阳在子则太阴在午。

本脚本权威表独立构造（仅 import sxtwl + 典籍山序，不读取任何软件模块的判定
结果），并与硬编码节气锚点双向锁定；软件侧三个入口逐一穷举比对：
  ① 神煞基类 get_sun_moon_mountains（层1/层2 单点出口，2026-09-22 起唯一实现）
  ② 评分器 calculate_sun_moon_position（层3 收敛：委托单点；score 恒 0，
     到山/到向计分唯一走修造神煞档 +25/+20/+20/+15）
  ③ 修造神煞扩展 _check_taiyang_taiyin（神煞登记端到端：名称+分值）

历史病灶（本验证永久锁死，防回归）：
  - 层1 死链：原实现取 get_lunar_date() 不存在的 month_num/day_num 键，恒 -1；
  - 层2 错口径：农历正月当冬至后第一段，365 天无一与节气序一致；
  - 层3 分叉：评分器另有公历月序 12 支山表（且八干四维归支，乾→亥），
    2021-12-03 小雪段太阳在亥，乾山被误判"太阳到山"+10。
"""
import bisect
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sxtwl
from shensha_verify_engine import ShenShaCase, run_cli
from modules.shensha.神煞基类 import (
    get_sun_moon_mountains, get_xiangshan_24, TAIYANG_DAOSHAN_24SHAN,
)
from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
from modules.评分器 import calculate_sun_moon_position


# ===== 典籍常量（独立硬编码，非从软件读取） =====
# 太阳过宫序（冬至=0 号节气起）
SUN_ORDER = ('子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳', '丙',
             '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥', '壬')
# 二十四山罗盘序（坐山 +12 为向山）
COMPASS = ('壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
           '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥')
JQ_NAMES = ('冬至', '小寒', '大寒', '立春', '雨水', '惊蛰', '春分', '清明',
            '谷雨', '立夏', '小满', '芒种', '夏至', '小暑', '大暑', '立秋',
            '处暑', '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪')
# 神煞档分值（SHENSHA_SCORES 登记，本脚本只锁不改）
SCORE_DAOSHAN, SCORE_DAOXIANG = 25, 20
MOON_SCORE_DAOSHAN, MOON_SCORE_DAOXIANG = 20, 15


def _d(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d').date()


# ===== 权威推导（独立 sxtwl 实现） =====
_ANCHORS = {}
for _y in (2025, 2026, 2027, 2028):
    for _item in sxtwl.getJieQiByYear(_y):
        _dd = sxtwl.JD2DD(_item.jd)
        if 0 <= int(_item.jqIndex) <= 23:
            _ANCHORS[datetime.date(int(_dd.Y), int(_dd.M), int(_dd.D))] = int(_item.jqIndex)
_ANCHOR_DATES = sorted(_ANCHORS)


def auth_sun_moon(d):
    """权威：(太阳山, 太阴山)；d 早于表内最早节气时返回 ('','')。"""
    i = bisect.bisect_right(_ANCHOR_DATES, d) - 1
    if i < 0:
        return '', ''
    jq = _ANCHORS[_ANCHOR_DATES[i]]
    return SUN_ORDER[jq], SUN_ORDER[(jq + 12) % 24]


def auth_xiang(shan):
    return COMPASS[(COMPASS.index(shan) + 12) % 24]


def auth_flags(d, z):
    """权威四布尔：(太阳到山, 太阳到向, 太阴到山, 太阴到向)。"""
    s, m = auth_sun_moon(d)
    x = auth_xiang(z)
    return (s == z, s == x, m == z, m == x)


# ===== 硬编码锚点一：2026 太阳过宫 25 个节气交节日（含跨年两端冬至） =====
JQ_2026_SEGMENT_START = (
    ('2025-12-21', '冬至', '子'), ('2026-01-05', '小寒', '癸'),
    ('2026-01-20', '大寒', '丑'), ('2026-02-04', '立春', '艮'),
    ('2026-02-18', '雨水', '寅'), ('2026-03-05', '惊蛰', '甲'),
    ('2026-03-20', '春分', '卯'), ('2026-04-05', '清明', '乙'),
    ('2026-04-20', '谷雨', '辰'), ('2026-05-05', '立夏', '巽'),
    ('2026-05-21', '小满', '巳'), ('2026-06-05', '芒种', '丙'),
    ('2026-06-21', '夏至', '午'), ('2026-07-07', '小暑', '丁'),
    ('2026-07-23', '大暑', '未'), ('2026-08-07', '立秋', '坤'),
    ('2026-08-23', '处暑', '申'), ('2026-09-07', '白露', '庚'),
    ('2026-09-23', '秋分', '酉'), ('2026-10-08', '寒露', '辛'),
    ('2026-10-23', '霜降', '戌'), ('2026-11-07', '立冬', '乾'),
    ('2026-11-22', '小雪', '亥'), ('2026-12-07', '大雪', '壬'),
    ('2026-12-22', '冬至', '子'),
)
_notes = []

# 双向锁：硬编码交节日当天权威太阳必在该山，节气名与 jqIndex 体系一致；
# 交节前一日必仍属旧段（太阳 != 新山）。
for ds, jq_name, shan in JQ_2026_SEGMENT_START:
    day = _d(ds)
    assert auth_sun_moon(day)[0] == shan, f'权威锚点失配 {ds} {jq_name} 应为 {shan}'
    prev_s = auth_sun_moon(day - datetime.timedelta(days=1))[0]
    assert prev_s != shan, f'{ds} 交节前一日不应已入 {shan} 段'
    # 软件单点出口与硬编码锚点一致
    assert get_sun_moon_mountains(day)[0] == shan, f'软件单点 {ds} 应为 {shan}'
assert JQ_NAMES[0] == '冬至' and SUN_ORDER[0] == '子'
_notes.append(f'节气交节日硬锚点 {len(JQ_2026_SEGMENT_START)} 个：当天换新段、前一日属旧段（双向锁）')

# 典籍山序与软件表单点常量逐字一致（防表序漂移）
assert TAIYANG_DAOSHAN_24SHAN == SUN_ORDER
_notes.append('太阳山序单点常量与典籍序逐字一致（24山）')

# ===== 硬编码锚点二：2026 公历年各山太阳到山天数（合计闭合 365） =====
DAYS_2026 = {
    '子': 14,  # 01-01~04（4）+ 12-22~31（10），跨年两段
    '癸': 15, '丑': 15, '艮': 14, '寅': 15, '甲': 15, '卯': 16, '乙': 15,
    '辰': 15, '巽': 16, '巳': 15, '丙': 16, '午': 16, '丁': 16, '未': 15,
    '坤': 16, '申': 15, '庚': 16, '酉': 15, '辛': 15, '戌': 15, '乾': 15,
    '亥': 15, '壬': 15,
}
_year_days = []
_d0 = datetime.date(2026, 1, 1)
while _d0 <= datetime.date(2026, 12, 31):
    _year_days.append(_d0)
    _d0 += datetime.timedelta(days=1)
for shan in COMPASS:
    _n = sum(1 for d in _year_days if auth_sun_moon(d)[0] == shan)
    assert _n == DAYS_2026[shan], f'{shan}山 2026 命中天数 期望{DAYS_2026[shan]} 实际{_n}'
assert sum(DAYS_2026.values()) == 365
_notes.append('2026 全年 24 山太阳到山天数硬编码锁（子山跨年两段共14天，合计365）')

# ===== 硬编码锚点三：关键边界日 + 端到端登记（含历史冒烟锚点） =====
# 跨年冬至段：2025-12-21~2026-01-04 太阳在子；2026-12-22 起新子段
assert auth_sun_moon(_d('2025-12-21')) == ('子', '午')
assert auth_sun_moon(_d('2026-01-03')) == ('子', '午')
assert auth_sun_moon(_d('2026-01-04')) == ('子', '午')
assert auth_sun_moon(_d('2026-01-05')) == ('癸', '丁')
assert auth_sun_moon(_d('2026-12-21')) == ('壬', '丙')
assert auth_sun_moon(_d('2026-12-22')) == ('子', '午')
# 立春艮 / 雨水寅 / 春分卯 / 夏至午
assert auth_sun_moon(_d('2026-02-04'))[0] == '艮'
assert auth_sun_moon(_d('2026-02-17'))[0] == '艮'  # 雨水前一日仍属立春段（艮）
assert auth_sun_moon(_d('2026-02-18')) == ('寅', '申')
assert auth_sun_moon(_d('2026-03-20'))[0] == '卯'
assert auth_sun_moon(_d('2026-06-21'))[0] == '午'
_notes.append('关键边界：冬至跨年子段、立春艮、雨水寅、春分卯、夏至午（含交界前一日）')

# 对宫 helper：四正/八干/四维抽样
assert get_xiangshan_24('子') == '午' and get_xiangshan_24('寅') == '申'
assert get_xiangshan_24('艮') == '坤' and get_xiangshan_24('壬') == '丙'
assert get_xiangshan_24('X') == ''


def _ext_register(d, z, hour='午'):
    """修造扩展端到端：跑 _check_taiyang_taiyin，返回 {名称: 分值}。

    001 §223 时辰门控（2026-11-08 用户拍板）后，日月加分只在时辰生效时登记：
    hour 为白天支（卯—申）只登记太阳，夜间支（酉—寅）只登记太阴；
    hour=None 表示时支缺失 → 日月均不计分（返回空）。
    """
    c = _checkers[z]
    c.shensha_list = []
    _sz = {'date': d}
    if hour:
        _sz['时支'] = hour
    c._check_taiyang_taiyin(_sz)
    return {item.get('name'): item.get('score') for item in c.shensha_list
            if isinstance(item, dict) and ('太阳' in str(item.get('name', '')) or '太阴' in str(item.get('name', '')))}


_checkers = {z: ConstructionShenShaCheckerExt(zuoshan=z) for z in COMPASS}

# 端到端锚点（午时·白天：只认太阳；001 §223 门控后太阴不计分）
assert _ext_register(_d('2026-02-24'), '寅') == {'太阳到山': SCORE_DAOSHAN}
assert _ext_register(_d('2026-01-03'), '子') == {'太阳到山': SCORE_DAOSHAN}
# 同段太阳在寅：坐申山寅向 → 太阳到向（白天）
assert _ext_register(_d('2026-02-24'), '申') == {'太阳到向': SCORE_DAOXIANG}
# 邻山（艮/甲）同日既不到山也不到向
assert _ext_register(_d('2026-02-24'), '艮') == {}
assert _ext_register(_d('2026-02-24'), '甲') == {}
# 端到端锚点（子时·夜间：只认太阴）
assert _ext_register(_d('2026-02-24'), '寅', '子') == {'太阴到向': MOON_SCORE_DAOXIANG}
assert _ext_register(_d('2026-02-24'), '申', '子') == {'太阴到山': MOON_SCORE_DAOSHAN}
# 时支缺失：无法判定昼夜 → 日月均不计分（不臆造白天）
assert _ext_register(_d('2026-02-24'), '寅', None) == {}
_notes.append('端到端登记锁：02-24 寅山(午时太阳到山25/子时太阴到向15)、'
              '申山(午时太阳到向20/子时太阴到山20)、邻山空、时支缺失空')

# 评分器：标志位正确、score 恒 0（计分已下线）；无山向/无日期不炸
_info = calculate_sun_moon_position({'date': _d('2026-02-24')}, '寅山申向')
assert (_info['sun_to_mountain'], _info['sun_to_direction'],
        _info['moon_to_mountain'], _info['moon_to_direction']) == (True, False, False, True)
assert _info['score'] == 0 and _info['sun_position'] == '寅' and _info['moon_position'] == '申'
assert calculate_sun_moon_position({'date': _d('2026-02-24')}, None)['score'] == 0
assert calculate_sun_moon_position({}, '寅山申向')['score'] == 0
_notes.append('评分器层3：标志位与单点一致、score 恒 0（无山向/无日期安全降级)')


# ===== 穷举输入：2026 全年 365 天 × 24 山 + 跨年边界段 =====
def _range_days(a, b):
    out, d = [], _d(a)
    end = _d(b)
    while d <= end:
        out.append(d)
        d += datetime.timedelta(days=1)
    return out


_boundary_days = _range_days('2025-12-19', '2026-01-06') + _range_days('2026-12-19', '2027-01-06')
ALL_DAYS = _year_days + [d for d in _boundary_days if d not in set(_year_days)]
INPUTS = [(d, z) for d in ALL_DAYS for z in COMPASS]


# ===== 入口适配器（软件三处） =====
def _ad_base(inp):
    d, z = inp
    s, m = get_sun_moon_mountains(d)
    x = get_xiangshan_24(z)
    return (s, m, s == z, s == x, m == z, m == x)


def _exp_base(inp):
    d, z = inp
    s, m = auth_sun_moon(d)
    x = auth_xiang(z)
    return (s, m, s == z, s == x, m == z, m == x)


def _ad_scorer(inp):
    d, z = inp
    info = calculate_sun_moon_position({'date': d, 'year': d.year, 'month': d.month, 'day': d.day},
                                       f'{z}山{auth_xiang(z)}向')
    return (info['sun_position'], info['moon_position'],
            info['sun_to_mountain'], info['sun_to_direction'],
            info['moon_to_mountain'], info['moon_to_direction'], info['score'])


def _exp_scorer(inp):
    d, z = inp
    s, m = auth_sun_moon(d)
    return (s, m) + auth_flags(d, z) + (0,)  # score 恒 0（计分下线锁）


def _sm_items(f_sun_m, f_sun_x, f_moon_m, f_moon_x, night=False):
    """按 001 §223 时辰门控生成期望登记项：白天只认太阳，夜间只认太阴。"""
    items = []
    if not night:
        if f_sun_m:
            items.append(('太阳到山', SCORE_DAOSHAN))
        elif f_sun_x:
            items.append(('太阳到向', SCORE_DAOXIANG))
    else:
        if f_moon_m:
            items.append(('太阴到山', MOON_SCORE_DAOSHAN))
        elif f_moon_x:
            items.append(('太阴到向', MOON_SCORE_DAOXIANG))
    return tuple(sorted(items))


def _ad_ext_day(inp):
    d, z = inp
    return tuple(sorted(_ext_register(d, z, '午').items()))


def _exp_ext_day(inp):
    d, z = inp
    return _sm_items(*auth_flags(d, z), night=False)


def _ad_ext_night(inp):
    d, z = inp
    return tuple(sorted(_ext_register(d, z, '子').items()))


def _exp_ext_night(inp):
    d, z = inp
    return _sm_items(*auth_flags(d, z), night=True)


cases = [
    ShenShaCase(name='太阳太阴到山到向(神煞基类单点·365×24+跨年)', category='B',
                description='get_sun_moon_mountains 山名+四布尔 与 sxtwl 权威逐日逐山一致',
                inputs=INPUTS, expected=_exp_base, adapter=_ad_base),
    ShenShaCase(name='太阳太阴到山到向(评分器层3收敛·365×24+跨年)', category='B',
                description='calculate_sun_moon_position 标志位与单点一致且 score 恒 0',
                inputs=INPUTS, expected=_exp_scorer, adapter=_ad_scorer),
    ShenShaCase(name='太阳太阴到山到向(修造扩展·午时白天只认太阳·365×24+跨年)', category='B',
                description='_check_taiyang_taiyin 端到端：白天太阳到山25/到向20，太阴门控为0',
                inputs=INPUTS, expected=_exp_ext_day, adapter=_ad_ext_day),
    ShenShaCase(name='太阳太阴到山到向(修造扩展·子时夜间只认太阴·365×24+跨年)', category='B',
                description='_check_taiyang_taiyin 端到端：夜间太阴到山20/到向15，太阳门控为0',
                inputs=INPUTS, expected=_exp_ext_night, adapter=_ad_ext_night),
]


if __name__ == '__main__':
    for n in _notes:
        print(f'[锚点] {n}')
    sys.exit(run_cli(cases))
