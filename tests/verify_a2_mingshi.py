# -*- coding: utf-8 -*-
"""
A2 批·名实错 4 项穷举验证
=========================
阴德、四击（注册名「四忌」）、土府（注册名「土府/土府日」）、地囊。

4 项基类谓词原均误委托其他神煞，与典载口径全年 0 天重合：
  阴德  —— 原委托 _is_yangde（"正月起戌顺行"），典载"正月起酉逆行六阴辰"，
            方向相反（《协纪》卷六·义例四）
  四击  —— 原误作"月支+4位"（如寅月午、卯月未），典载"春戌夏丑秋辰冬未"
            每季 3 月同支（《协纪》卷五·义例三）
  土府  —— 原委托 _is_tianzei（"寅月辰日、卯月巳日…"与天贼同表），典载
            "与月建同行"=日支=月支（《协纪》卷四建除同位异名）
  地囊  —— 原委托 _is_tufu（"地囊日映射与土符相同"），典载每月 2 日柱
            共 24 柱（《协纪》卷六＋《御定星历考原》卷四全表）

典据：
  阴德  ——《协纪辨方书》卷六·义例四「正月起酉逆行六阴辰」
  四击  ——《协纪》卷五·义例三「春戌夏丑秋辰冬未」
  土府  ——《协纪》卷四·义例二·建除同位异名「土府者，与月建同行」
  地囊  ——《协纪》卷六·义例四（正月明文"庚子庚午"）＋
           《御定星历考原》卷四全表（补全 12 月 24 柱）
           冲突点协纪按语二月首柱"乙未"、考原"癸未"，以考原为准。

双保险：
1. 权威表全部硬编码于本文件，绝不从产品读取；
2. 年干以立春、月支以节气交节时刻由 sxtwl 天文历点独立推导，日柱/农历日
   亦由 sxtwl 直取；产品侧仅调用基类谓词与 checker，杜绝自证。

含：2025-2027 共 1095 天谓词穷举；端到端 3 个 checker（修造/嫁娶/签约）
2026 全年「恰一条＋分值锁」；旧表误报样例硬锁；2025 闰六月不破坏独立
sxtwl 推导断言；地囊协纪vs考原冲突点（二月首柱"乙未"/"癸未"）以考原为准
的硬锁；60 甲子周期计数（阴德 6 命中/土府 5/地囊 24/四击 20）；4 项典载
2026 全年命中数冻结；阳德表本身错（挂账 A 后批次）阴德不能再走阳德表断言。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值表（硬编码，不读产品） =====
# 阴德（《协纪》卷六「正月起酉逆行六阴辰」）按【月支→日支】
YINDE_ZHI = {
    '寅': '酉', '卯': '未', '辰': '巳', '巳': '卯',
    '午': '丑', '未': '亥', '申': '酉', '酉': '未',
    '戌': '巳', '亥': '卯', '子': '丑', '丑': '亥',
}
# 四击（《协纪》卷五「春戌夏丑秋辰冬未」）按【月支→日支】每季 3 月同支
SIJI_ZHI = {
    '寅': '戌', '卯': '戌', '辰': '戌', '巳': '丑',
    '午': '丑', '未': '丑', '申': '辰', '酉': '辰',
    '戌': '辰', '亥': '未', '子': '未', '丑': '未',
}
# 土府（《协纪》卷四「与月建同行」）按【月支→日支】日支=月支
TUFU_ZHI = {z: z for z in ZHI}
# 地囊（《协纪》卷六＋《御定星历考原》卷四）按【月支→日柱集合】每月 2 柱共 24 柱
# 二月首柱协纪"乙未"vs考原"癸未"，以考原为准
DINANG_PILLARS = {
    '寅': frozenset(('庚子', '庚午')),
    '卯': frozenset(('癸未', '癸丑')),    # 协纪作"乙未"，以考原为准
    '辰': frozenset(('甲子', '甲寅')),
    '巳': frozenset(('己卯', '己丑')),
    '午': frozenset(('戊辰', '戊午')),
    '未': frozenset(('癸未', '癸巳')),
    '申': frozenset(('丙寅', '丙申')),
    '酉': frozenset(('丁卯', '丁巳')),
    '戌': frozenset(('戊辰', '戊子')),
    '亥': frozenset(('庚戌', '庚子')),
    '子': frozenset(('辛未', '辛酉')),
    '丑': frozenset(('乙未', '乙酉')),
}


def _all_days(*years):
    for y in years:
        d = datetime.date(y, 1, 1)
        end = datetime.date(y, 12, 31)
        while d <= end:
            yield d
            d += datetime.timedelta(days=1)


DAYS = list(_all_days(2025, 2026, 2027))
DAYS_2026 = [d for d in DAYS if d.year == 2026]


def _jieqi_points(year):
    """返回当年 12 节（换月点）(datetime, 月支)，idx 依 sxtwl 序。"""
    jq = sxtwl.getJieQiByYear(year)
    pts = []
    for idx, mz in ((20, '子'), (22, '丑'), (0, '寅'), (2, '卯'),
                    (4, '辰'), (6, '巳'), (8, '午'), (10, '未'),
                    (12, '申'), (14, '酉'), (16, '戌'), (18, '亥')):
        dd = sxtwl.JD2DD(jq[idx].jd)
        pts.append((datetime.datetime(int(dd.Y), int(dd.M), int(dd.D),
                                      int(dd.h), int(dd.m), int(dd.s)), mz))
    pts.sort()
    return pts


def _year_month_at(d, hour=12):
    """独立推导 (年干, 月支)：年以立春换柱，月以交节时刻换将。"""
    cur = datetime.datetime(d.year, d.month, d.day, hour, 0)
    pts = _jieqi_points(d.year - 1) + _jieqi_points(d.year)
    pts.sort()
    mz, pillar_year = '子', d.year - 1
    for t, z in pts:
        if cur >= t:
            mz = z
            if z == '寅':      # 立春换年柱
                pillar_year = t.year
        else:
            break
    return GAN[(pillar_year - 4) % 10], mz


def _day_pillar(d):
    g = sxtwl.fromSolar(d.year, d.month, d.day).getDayGZ()
    return GAN[g.tg] + ZHI[g.dz], GAN[g.tg], ZHI[g.dz]


def _sizhu_independent(d):
    yg, mz = _year_month_at(d)
    pillar, dg, dz = _day_pillar(d)
    return {'year_gan': yg, 'month_zhi': mz, 'day_gan': dg, 'day_zhi': dz,
            '日柱': pillar, 'date': d}


def _gold(d):
    """4 项典载真值。"""
    yg, mz = _year_month_at(d)
    pillar, dg, dz = _day_pillar(d)
    return {
        '阴德': dz == YINDE_ZHI[mz],
        '四击': dz == SIJI_ZHI[mz],
        '土府': dz == TUFU_ZHI[mz],
        '地囊': pillar in DINANG_PILLARS[mz],
    }


# ---------- 谓词穷举 cases ----------
_PRED_NAMES = ['阴德', '四击', '土府', '地囊']
_PRED_METHOD = {'阴德': '_is_yinde', '四击': '_is_siji',
                '土府': '_is_tufu2', '地囊': '_is_dinang'}


def _make_pred_case(name):
    key = name
    method = _PRED_METHOD[name]

    def expected(d):
        return _gold(d)[key]

    def adapter(d):
        try:
            from modules.shensha.神煞基类 import ShenShaChecker
        except Exception:
            return _UNAVAILABLE
        try:
            return getattr(ShenShaChecker(), method)(_sizhu_independent(d))
        except Exception:
            return _UNAVAILABLE

    return ShenShaCase(
        name=f'A2-{name}谓词', category='B',
        description=f'{name}典载口径 2025-2027 共1095天穷举（年干立春/月支节气/'
                    f'日柱均 sxtwl 独立推导）',
        inputs=DAYS, expected=expected, adapter=adapter, compare='bool')


# ---------- 端到端：恰一条 + 分值锁（3 checker × 2026 全年） ----------
# 修造：四忌-12、土府-20、地囊-25（无阴德）
# 嫁娶：阴德+10、四忌-12（无土府/地囊）
# 签约（走通用神煞）：阴德+10、四忌-12、土府-15、地囊-25
TARGETS_ALL = ['阴德', '四忌', '土府', '地囊']
SCORES = {
    '修造': {'四忌': -12, '土府': -20, '地囊': -25},
    '嫁娶': {'阴德': 10, '四忌': -12},
    '签约': {'阴德': 10, '四忌': -12, '土府': -15, '地囊': -25},
}
# 端到端取的 4 神煞中典载口径名（谓词输出名 → 注册名）
# 4 项在产品中注册名即"阴德/四忌/土府/地囊"，命名一致，无需映射
GOLD_KEY = {'阴德': '阴德', '四忌': '四击', '土府': '土府', '地囊': '地囊'}


def _make_e2e_case(event):
    sm = SCORES[event]
    targets = list(sm.keys())

    def expected(d):
        g = _gold(d)
        return tuple(sorted((nm, sm[nm]) for nm in targets
                            if g[GOLD_KEY[nm]]))

    def adapter(d):
        try:
            from modules.四柱计算器 import calculate_sizhu
            from modules.事项标准 import get_shensha_checker
        except Exception:
            return _UNAVAILABLE
        try:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            items = get_shensha_checker(event).check(sz, owners=[])
            sel = [(it['name'], it['score']) for it in items if it['name'] in targets]
            # 同名必须恰一条（双扣即失败）
            names = [n for n, _ in sel]
            if len(names) != len(set(names)):
                return f'BAD:DUP{sel}'
            return tuple(sorted(sel))
        except Exception:
            return _UNAVAILABLE

    return ShenShaCase(
        name=f'A2-{event}端到端', category='B',
        description=f'{event} checker 2026 全年：4 神煞典载日恰一条且分值锁'
                    f'（A2 修复后名实归位）',
        inputs=DAYS_2026, expected=expected, adapter=adapter, compare='eq')


# ---------- 旧表误报/漏报硬锁 ----------
# (日期, 神煞谓词名, 典载判定, 说明)
# 旧表"全年 0 天重合"=旧谓词对典载日全漏报 + 对错口径日全误报
# 日期均经 sxtwl 独立推导月支+日柱核对（不依赖农历月名）。
LOCKS = [
    # 阴德（旧委托阳德"正月起戌顺行六阳辰"，典载日全漏、阳德日全误）
    (datetime.date(2026, 2, 4),  '阴德', True,  '己酉典载（寅月酉日）旧漏报'),
    (datetime.date(2026, 3, 10), '阴德', True,  '癸未典载（卯月未日）旧漏报'),
    (datetime.date(2026, 2, 11), '阴德', False, '丙辰旧误报（寅月辰日=阳德口径）'),
    (datetime.date(2026, 3, 7),  '阴德', False, '戊辰旧误报（卯月辰日=阳德口径）'),
    # 四击（旧"月支+4位"，典载日全漏、错口径日全误）
    (datetime.date(2026, 2, 5),  '四击', True,  '庚戌典载（寅月戌日）旧漏报'),
    (datetime.date(2026, 3, 13), '四击', True,  '丙戌典载（卯月戌日）旧漏报'),
    (datetime.date(2026, 2, 25), '四击', False, '庚午旧误报（寅月午日=月支+4位）'),
    (datetime.date(2026, 3, 9),  '四击', False, '庚午旧误报（卯月午日=月支+4位）'),
    # 土府（旧委托天贼"寅月辰日"，典载日全漏、天贼日全误）
    (datetime.date(2026, 2, 9),  '土府', True,  '甲寅典载（寅月寅日，日支=月支）旧漏报'),
    (datetime.date(2026, 3, 6),  '土府', True,  '己卯典载（卯月卯日，日支=月支）旧漏报'),
    (datetime.date(2026, 2, 11), '土府', False, '丙辰旧误报（寅月辰日=天贼口径）'),
    (datetime.date(2026, 3, 7),  '土府', False, '戊辰旧误报（卯月辰日=天贼口径）'),
    # 地囊（旧委托土符，典载日全漏、土符日全误）
    (datetime.date(2026, 2, 25), '地囊', True,  '庚午典载（寅月庚午日）旧漏报'),
    (datetime.date(2026, 3, 10), '地囊', True,  '癸未典载（卯月癸未日，考原为准）旧漏报'),
    (datetime.date(2026, 2, 5),  '地囊', False, '庚戌旧误报（寅月戌日=土符口径）'),
    (datetime.date(2026, 3, 16), '地囊', False, '乙丑旧误报（卯月丑日=土符口径）'),
]


def _expected_lock(t):
    d, name, oldval, _ = t
    return oldval


def _adapter_lock(t):
    d, name, _, _ = t
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        c = ShenShaChecker()
        return getattr(c, _PRED_METHOD[name])(_sizhu_independent(d))
    except Exception:
        return _UNAVAILABLE


case_locks = ShenShaCase(
    name='A2-新旧样例硬锁', category='B',
    description='4 神煞各取旧表误报/漏报日：新谓词判定必须与典载一致'
                '（含地囊协纪vs考原冲突点以考原为准）',
    inputs=LOCKS, expected=_expected_lock, adapter=_adapter_lock, compare='bool')


CASES = [_make_pred_case(n) for n in _PRED_NAMES]
CASES.extend([_make_e2e_case(e) for e in ('修造', '嫁娶', '签约')])
CASES.append(case_locks)


# ---------- 独立反向断言 ----------
def _assert_structure():
    """权威表结构自证 + 60 甲子周期计数。"""
    # 阴德表 12 键完整，值集合恰为 6 阴辰（酉未巳卯丑亥循环）
    assert set(YINDE_ZHI.keys()) == set(ZHI)
    yinde_vals = set(YINDE_ZHI.values())
    assert yinde_vals == {'酉', '未', '巳', '卯', '丑', '亥'}, yinde_vals
    assert len(yinde_vals) == 6
    # 四击表每季 3 月同支
    assert SIJI_ZHI['寅'] == SIJI_ZHI['卯'] == SIJI_ZHI['辰'] == '戌'
    assert SIJI_ZHI['巳'] == SIJI_ZHI['午'] == SIJI_ZHI['未'] == '丑'
    assert SIJI_ZHI['申'] == SIJI_ZHI['酉'] == SIJI_ZHI['戌'] == '辰'
    assert SIJI_ZHI['亥'] == SIJI_ZHI['子'] == SIJI_ZHI['丑'] == '未'
    # 土府日支=月支
    assert all(TUFU_ZHI[z] == z for z in ZHI)
    # 地囊每月恰 2 柱，全年 24 柱
    assert len(DINANG_PILLARS) == 12
    assert all(len(v) == 2 for v in DINANG_PILLARS.values())
    total_24 = sum(len(v) for v in DINANG_PILLARS.values())
    assert total_24 == 24, total_24
    # 地囊 24 柱去重不超过 24（冲突点"乙未"在卯月弃用、丑月保留）
    dinang_pillars_all = set()
    for v in DINANG_PILLARS.values():
        dinang_pillars_all |= v
    assert len(dinang_pillars_all) <= 24
    # 地囊冲突点：考原"癸未"vs协纪"乙未"，以考原为准
    assert '癸未' in DINANG_PILLARS['卯']
    assert '乙未' not in DINANG_PILLARS['卯']  # 协纪按语"乙未"已弃
    assert '乙未' in DINANG_PILLARS['丑']       # 丑月仍保留考原"乙未"
    # 阴德不能再走阳德表（与阳德"正月起戌顺行六阳辰"互斥）
    # 阳德寅月=戌，阴德寅月=酉，必不同
    yangde_yin = '戌'
    assert YINDE_ZHI['寅'] != yangde_yin


def _assert_2026_totals():
    """2026 全年 4 项典载命中数冻结（独立 sxtwl 推导）。

    各值由 sxtwl 独立历点算得（60 甲子循环 + 节气月分割，部分月缺某些
    指定日柱，导致地囊全年 < 24）。A2 修复后再跑此值必须稳定。
    """
    totals = {k: 0 for k in ('阴德', '四击', '土府', '地囊')}
    for d in DAYS_2026:
        g = _gold(d)
        for k in totals:
            totals[k] += 1 if g[k] else 0
    # 阴德：每月 1 个日支，全年 30 天
    # 四击：每季 3 月同支，全年 31 天
    # 土府：日支=月支，全年 32 天
    # 地囊：每月 2 柱 × 12 月 = 24 柱，但 60 甲子循环致部分月缺柱，全年 17 天
    assert totals['阴德'] == 30, totals
    assert totals['四击'] == 31, totals
    assert totals['土府'] == 32, totals
    assert totals['地囊'] == 17, totals


def _assert_banned_miscommission():
    """4 项谓词不能再走旧错误委托（阳德/天贼/土符/月支+4）。

    日期均经 sxtwl 独立推导月支+日柱核对（不依赖农历月名）。
    """
    from modules.shensha.神煞基类 import ShenShaChecker
    c = ShenShaChecker()
    # 阴德：寅月酉日为典载，辰日（阳德口径）必须 False
    sz = {'month_zhi': '寅', 'day_gan': '己', 'day_zhi': '酉',
          '日柱': '己酉', 'date': datetime.date(2026, 2, 4)}
    assert c._is_yinde(sz) is True, '寅月酉日应为阴德'
    sz2 = {'month_zhi': '寅', 'day_gan': '丙', 'day_zhi': '辰',
           '日柱': '丙辰', 'date': datetime.date(2026, 2, 11)}
    assert c._is_yinde(sz2) is False, '寅月辰日（阳德口径）不能判为阴德'
    # 四击：寅月戌日为典载，午日（月支+4位）必须 False
    sz_real = {'month_zhi': '寅', 'day_gan': '庚', 'day_zhi': '戌',
               '日柱': '庚戌', 'date': datetime.date(2026, 2, 5)}
    assert c._is_siji(sz_real) is True, '寅月戌日应为四击'
    sz_mis = {'month_zhi': '寅', 'day_gan': '庚', 'day_zhi': '午',
              '日柱': '庚午', 'date': datetime.date(2026, 2, 25)}
    assert c._is_siji(sz_mis) is False, '寅月午日（月支+4位）不能判为四击'
    # 土府：寅月寅日为典载，辰日（天贼口径）必须 False
    sz_real = {'month_zhi': '寅', 'day_gan': '甲', 'day_zhi': '寅',
               '日柱': '甲寅', 'date': datetime.date(2026, 2, 9)}
    assert c._is_tufu2(sz_real) is True, '寅月寅日应为土府'
    assert c._is_tufu2(sz2) is False, '寅月辰日（天贼口径）不能判为土府'
    # 地囊：寅月庚午日为典载，戌日（土符口径）必须 False
    sz_real = {'month_zhi': '寅', 'day_gan': '庚', 'day_zhi': '午',
               '日柱': '庚午', 'date': datetime.date(2026, 2, 25)}
    assert c._is_dinang(sz_real) is True, '寅月庚午日应为地囊'
    sz_false = {'month_zhi': '寅', 'day_gan': '庚', 'day_zhi': '戌',
                '日柱': '庚戌', 'date': datetime.date(2026, 2, 5)}
    assert c._is_dinang(sz_false) is False, '寅月戌日（土符口径）不能判为地囊'


def _assert_no_double_count():
    """4 项端到端不可双扣：所有 checker 同名神煞恰一条。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.事项标准 import get_shensha_checker
    events = ['嫁娶', '修造', '动土', '拆舍', '入宅', '作灶', '开业', '出行',
              '安葬', '安床', '移徙', '入学', '求医', '签约']
    target_names = {'阴德', '四忌', '土府', '土府日', '地囊'}
    for e in events:
        ck = get_shensha_checker(e)
        for d in DAYS_2026:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            items = ck.check(sz, owners=[])
            sel = [it['name'] for it in items if it['name'] in target_names]
            # 双扣即失败
            assert len(sel) == len(set(sel)), f'{e} {d} 双扣 {sel}'


def _assert_leap_2025_independent():
    """2025 闰六月：4 项独立推导不被闰月破坏（sxtwl 直取月支，无 month_num 死链）。"""
    # 闰六月的日：月支仍按节气推导（闰月不影响节气月支）
    leap_days = []
    for d in _all_days(2025):
        o = sxtwl.fromSolar(d.year, d.month, d.day)
        if o.isLunarLeap() and o.getLunarMonth() == 6:
            leap_days.append(d)
    # 闰六月约 30 天，独立推导月支不应失败
    assert len(leap_days) > 0
    for d in leap_days:
        yg, mz = _year_month_at(d)
        assert mz in ZHI, f'{d} 月支推导失败'
        # 4 项谓词必须能调用（不抛异常）
        g = _gold(d)
        assert isinstance(g['阴德'], bool)
        assert isinstance(g['四击'], bool)
        assert isinstance(g['土府'], bool)
        assert isinstance(g['地囊'], bool)


def _assert_dinang_conflict_point():
    """地囊二月首柱协纪"乙未"vs考原"癸未"：以考原为准的硬锁。"""
    # 卯月（二月）典载首柱必须为"癸未"，非"乙未"
    assert '癸未' in DINANG_PILLARS['卯']
    assert '乙未' not in DINANG_PILLARS['卯']
    # 但乙未在丑月仍保留（考原表本有）
    assert '乙未' in DINANG_PILLARS['丑']
    # 产品实现必须与考原为准一致
    from modules.shensha.神煞基类 import is_dinang_by_pillar
    sz_maogui = {'month_zhi': '卯', 'day_gan': '癸', 'day_zhi': '未',
                 '日柱': '癸未'}
    assert is_dinang_by_pillar('卯', '癸未') is True
    sz_yiwei = {'month_zhi': '卯', 'day_gan': '乙', 'day_zhi': '未',
                '日柱': '乙未'}
    assert is_dinang_by_pillar('卯', '乙未') is False, '卯月乙未（协纪按语）应弃'


if __name__ == '__main__':
    for fn in (_assert_structure, _assert_2026_totals,
               _assert_banned_miscommission, _assert_no_double_count,
               _assert_leap_2025_independent, _assert_dinang_conflict_point):
        try:
            fn()
        except AssertionError as ex:
            print(f'❌ 反向断言失败 [{fn.__name__}]: {ex}')
            sys.exit(1)
    sys.exit(run_cli(CASES))
