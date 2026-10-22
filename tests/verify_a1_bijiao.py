# -*- coding: utf-8 -*-
"""
A1 批·比较对象错 7 项穷举验证
=============================
岁德、岁德合、月空、天马、反支、天恩、鸣吠日、鸣吠对日（8 个谓词）。

典据：
  岁德/岁德合 ——《协纪辨方书》卷三（年干之德／德合比【日干】，非比年支）
  月空      ——《协纪》卷五：寅午戌壬、申子辰丙、亥卯未庚、巳酉丑甲（比【日干】）
  天马      ——《星历考原》卷三：月神「正月起午顺行六阳辰」（比【日支】）
  反支      ——《协纪》卷九立成＋《星历考原》卷四：戌亥朔一日、申酉朔二日、
               午未朔三日、辰巳朔四日、寅卯朔五日、子丑朔六日，其后十二日一遇
               （按【农历月朔支】起算，闰月独立起算）
  天恩      ——《协纪》卷五·义例三：甲子至戊辰、己卯至癸未、己酉至癸丑，
               凡一十五日（比【日柱】）
  鸣吠日    ——《协纪》卷五义例三＋卷九立成：13 日柱（旧误作戌日）
  鸣吠对日  —— 同卷：11 日柱（旧误作辰日）；软件旧名「鸣犬」本批正名

双保险：
1. 权威表全部硬编码于本文件，绝不从产品读取；
2. 年干以立春、月支以节气交节时刻由 sxtwl 天文历点独立推导，日柱/农历日
   亦由 sxtwl 直取；产品侧仅调用基类谓词与 checker，杜绝自证。

含：2025-2027 共 1095 天谓词穷举；端到端 3 个 checker（修造/安葬/签约）
365 天「恰一条＋分值锁」；禁名（鸣犬日/鸣犬对日/天马日）0 出现反向断言；
旧表误报/漏报样例硬锁；60 甲子周期计数（15/13/11）；2025 闰六月反支
=初三/十五/廿七；岁合（挂账待翻书）行为不变锁。
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
SUI_DE = {'甲': '甲', '乙': '庚', '丙': '丙', '丁': '壬', '戊': '戊',
          '己': '甲', '庚': '庚', '辛': '丙', '壬': '壬', '癸': '戊'}
SUI_DE_HE = {'甲': '己', '乙': '乙', '丙': '辛', '丁': '丁', '戊': '癸',
             '己': '己', '庚': '乙', '辛': '辛', '壬': '丁', '癸': '癸'}
YUE_KONG = {}
for _z in '寅午戌': YUE_KONG[_z] = '壬'
for _z in '申子辰': YUE_KONG[_z] = '丙'
for _z in '亥卯未': YUE_KONG[_z] = '庚'
for _z in '巳酉丑': YUE_KONG[_z] = '甲'
# 天马：正月（寅）起午，顺行六阳辰：午申戌子寅辰
TIAN_MA = dict(zip(ZHI[2:] + ZHI[:2], ['午', '申', '戌', '子', '寅', '辰'] * 2))
TIAN_EN = frozenset(['甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己卯', '庚辰',
                     '辛巳', '壬午', '癸未', '己酉', '庚戌', '辛亥', '壬子', '癸丑'])
MING_FEI = frozenset([g + z for g in '甲丙庚壬' for z in ('午', '申')]
                     + [g + '酉' for g in '乙丁己辛癸'])
MING_FEI_DUI = frozenset([g + '子' for g in '丙庚壬']
                         + [g + '寅' for g in '甲丙庚壬']
                         + [g + '卯' for g in '乙丁辛癸'])
FANZHI_N = {0: 6, 1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 3, 7: 3, 8: 2, 9: 2, 10: 1, 11: 1}
# 岁合（年干五合日干）——非本批修复项，冻结其行为，挂账待翻书。
SUI_HE = {'甲': '己', '乙': '庚', '丙': '辛', '丁': '壬', '戊': '癸',
          '己': '甲', '庚': '乙', '辛': '丙', '壬': '丁', '癸': '戊'}


def _all_days(*years):
    for y in years:
        d = datetime.date(y, 1, 1)
        end = datetime.date(y, 12, 31)
        while d <= end:
            yield d
            d += datetime.timedelta(days=1)


DAYS = list(_all_days(2025, 2026, 2027))


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


def _lunar(d):
    o = sxtwl.fromSolar(d.year, d.month, d.day)
    lday = o.getLunarDay()
    shuo_idx = (o.getDayGZ().dz - (lday - 1)) % 12
    return lday, shuo_idx, o.isLunarLeap(), o.getLunarMonth()


def _gold(d):
    yg, mz = _year_month_at(d)
    pillar, dg, dz = _day_pillar(d)
    lday, shuo_idx, _, _ = _lunar(d)
    n = FANZHI_N[shuo_idx]
    return {
        '岁德': dg == SUI_DE[yg],
        '岁德合': dg == SUI_DE_HE[yg],
        '月空': dg == YUE_KONG[mz],
        '天马': dz == TIAN_MA[mz],
        '反支': lday >= n and (lday - n) % 12 == 0,
        '天恩': pillar in TIAN_EN,
        '鸣吠日': pillar in MING_FEI,
        '鸣吠对日': pillar in MING_FEI_DUI,
    }


def _sizhu_independent(d):
    yg, mz = _year_month_at(d)
    pillar, dg, dz = _day_pillar(d)
    return {'year_gan': yg, 'month_zhi': mz, 'day_gan': dg, 'day_zhi': dz,
            '日柱': pillar, 'date': d}


# ---------- 谓词穷举 cases ----------
_PRED_NAMES = ['岁德', '岁德合', '月空', '天马', '天恩', '鸣吠日', '鸣吠对日']
_PRED_METHOD = {'岁德': '_is_suide', '岁德合': '_is_suide_he', '月空': '_is_yuekong',
                '天马': '_is_tianma', '天恩': '_is_tianen',
                '鸣吠日': '_is_mingfei', '鸣吠对日': '_is_mingfeidui'}


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
        name=f'A1-{name}谓词', category='B',
        description=f'{name}典载口径 2025-2027 共1095天穷举（年干立春/月支节气/日柱均 sxtwl 独立推导）',
        inputs=DAYS, expected=expected, adapter=adapter, compare='bool')


def _expected_fanzhi(d):
    return _gold(d)['反支']


def _adapter_fanzhi(d):
    try:
        from modules.shensha.神煞基类 import is_fanzhi_by_lunar
    except Exception:
        return _UNAVAILABLE
    try:
        return is_fanzhi_by_lunar({'date': d})
    except Exception:
        return _UNAVAILABLE


case_fanzhi = ShenShaCase(
    name='A1-反支谓词', category='B',
    description='反支按农历月朔支起算（戌亥1…子丑6），闰月独立；2025-2027 穷举',
    inputs=DAYS, expected=_expected_fanzhi, adapter=_adapter_fanzhi, compare='bool')


# ---------- 端到端：恰一条 + 分值锁（3 checker × 2026 全年） ----------
TARGETS = ['岁德', '岁德合', '月空', '天马', '反支日', '天恩', '鸣吠日', '鸣吠对日']
GOLD_KEY = {'岁德': '岁德', '岁德合': '岁德合', '月空': '月空', '天马': '天马',
            '反支日': '反支', '天恩': '天恩', '鸣吠日': '鸣吠日', '鸣吠对日': '鸣吠对日'}
SCORES = {
    # 口径收口批（001 §153）：反支日全事项删除；天恩仅修造保留（条件增益句
    # 「与修造吉神并尤宜兴作」，取证稿 §1.1/§1.5）。
    '修造': {'岁德': 20, '岁德合': 15, '月空': 10, '天马': 10,
             '天恩': 10, '鸣吠日': 15, '鸣吠对日': 10},
    '安葬': {'岁德': 20, '岁德合': 15, '月空': 10, '天马': 10,
             '鸣吠日': 15, '鸣吠对日': 10},
    '签约': {'岁德': 20, '岁德合': 15, '月空': 10, '天马': 10,
             '鸣吠日': 15, '鸣吠对日': 10},
}
DAYS_2026 = [d for d in DAYS if d.year == 2026]


def _make_e2e_case(event):
    sm = SCORES[event]

    def expected(d):
        g = _gold(d)
        return tuple(sorted((nm, sm[nm]) for nm in TARGETS
                            if nm in sm and g[GOLD_KEY[nm]]))

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
            sel = [(it['name'], it['score']) for it in items if it['name'] in TARGETS]
            # 同名必须恰一条（双扣即失败）
            names = [n for n, _ in sel]
            if len(names) != len(set(names)):
                return f'BAD:DUP{sel}'
            # 口径收口批（001 §153）：反支日任何事项不得发射；
            # 天恩仅修造通道发射（其余事项删除）。
            if '反支日' in names:
                return f'BAD:SCOPE-反支日{sel}'
            if '天恩' in names and event != '修造':
                return f'BAD:SCOPE-天恩{sel}'
            return tuple(sorted(sel))
        except Exception:
            return _UNAVAILABLE

    return ShenShaCase(
        name=f'A1-{event}端到端', category='B',
        description=f'{event} checker 2026 全年：8 神煞典载日恰一条且分值锁'
                    f'（鸣吠批次2 统一高档 15/10，001 §159）',
        inputs=DAYS_2026, expected=expected, adapter=adapter, compare='eq')


# ---------- 旧表误报/漏报硬锁 + 黄金日柱 ----------
# (日期, 神煞, 旧表判定, 说明)
LOCKS = [
    # 岁德（旧比年支，误/漏）
    (datetime.date(2026, 1, 10), '岁德', False, '甲申旧误报'),
    (datetime.date(2026, 1, 6),  '岁德', True,  '庚辰旧漏报'),
    # 岁德合
    (datetime.date(2026, 1, 7),  '岁德合', False, '辛巳旧误报'),
    (datetime.date(2026, 1, 1),  '岁德合', True,  '乙亥旧漏报'),
    # 月空
    (datetime.date(2026, 1, 9),  '月空', False, '癸未旧误报'),
    (datetime.date(2026, 1, 2),  '月空', True,  '丙子旧漏报'),
    # 天马
    (datetime.date(2026, 1, 1),  '天马', False, '乙亥旧误报'),
    (datetime.date(2026, 1, 4),  '天马', True,  '戊寅旧漏报'),
    # 反支
    (datetime.date(2026, 1, 3),  '反支', False, '丁丑旧误报'),
    (datetime.date(2026, 1, 1),  '反支', True,  '乙亥旧漏报'),
    # 天恩
    (datetime.date(2026, 1, 21), '天恩', False, '乙未旧误报(年神错口径)'),
    (datetime.date(2026, 1, 5),  '天恩', True,  '己卯旧漏报'),
    # 鸣吠（旧戌日）/鸣吠对（旧辰日）
    (datetime.date(2026, 1, 12), '鸣吠日', False, '丙戌旧戌日误报'),
    (datetime.date(2026, 1, 8),  '鸣吠日', True,  '壬午典载漏'),
    (datetime.date(2026, 1, 6),  '鸣吠对日', False, '庚辰旧辰日误报'),
    (datetime.date(2026, 1, 2),  '鸣吠对日', True,  '丙子典载漏'),
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
        return getattr(c, _PRED_METHOD.get(name, '_is_fanzhi'))(_sizhu_independent(d))
    except Exception:
        return _UNAVAILABLE


case_locks = ShenShaCase(
    name='A1-新旧样例硬锁', category='B',
    description='8 神煞各取旧表误报/漏报日：新谓词判定必须与典载一致（16 样例）',
    inputs=LOCKS, expected=_expected_lock, adapter=_adapter_lock, compare='bool')


CASES = [_make_pred_case(n) for n in _PRED_NAMES]
CASES.append(case_fanzhi)
CASES.extend([_make_e2e_case(e) for e in ('修造', '安葬', '签约')])
CASES.append(case_locks)


# ---------- 独立反向断言 ----------
def _assert_structure():
    assert len(TIAN_EN) == 15
    assert len(MING_FEI) == 13
    assert len(MING_FEI_DUI) == 11
    assert not (MING_FEI & MING_FEI_DUI)
    jiazi = [GAN[i % 10] + ZHI[i % 12] for i in range(60)]
    assert sum(p in TIAN_EN for p in jiazi) == 15
    assert sum(p in MING_FEI for p in jiazi) == 13
    assert sum(p in MING_FEI_DUI for p in jiazi) == 11
    # 天马六阳辰表自证
    assert [TIAN_MA[z] for z in ZHI[2:] + ZHI[:2]] == ['午', '申', '戌', '子', '寅', '辰'] * 2
    # 2026 全年典载命中数冻结
    for d in DAYS_2026:
        pass
    totals = {k: 0 for k in ('岁德', '岁德合', '月空', '天马', '反支',
                             '天恩', '鸣吠日', '鸣吠对日')}
    for d in DAYS_2026:
        g = _gold(d)
        for k in totals:
            totals[k] += 1 if g[k] else 0
    assert totals == {'岁德': 36, '岁德合': 37, '月空': 37, '天马': 31, '反支': 36,
                      '天恩': 91, '鸣吠日': 78, '鸣吠对日': 67}, totals


def _assert_leap_2025():
    # 2025 闰六月：未朔初三/十五/廿七（sxtwl 独立历点）
    hit = []
    for d in _all_days(2025):
        o = sxtwl.fromSolar(d.year, d.month, d.day)
        if o.isLunarLeap() and o.getLunarMonth() == 6:
            lday, shuo_idx, _, _ = _lunar(d)
            n = FANZHI_N[shuo_idx]
            if lday >= n and (lday - n) % 12 == 0:
                hit.append(lday)
    assert hit == [3, 15, 27], hit
    try:
        from modules.shensha.神煞基类 import is_fanzhi_by_lunar
    except ImportError:
        return
    prod = [lday for d, lday in
            ((d, sxtwl.fromSolar(d.year, d.month, d.day).getLunarDay())
             for d in _all_days(2025))
            if (lambda o: o.isLunarLeap() and o.getLunarMonth() == 6)
            (sxtwl.fromSolar(d.year, d.month, d.day)) and is_fanzhi_by_lunar({'date': d})]
    assert prod == [3, 15, 27], prod


def _assert_banned_names_and_scope():
    """全部 14 事项端到端：旧名 0 出现；反支日全事项 0 发射、
    天恩仅修造发射（口径收口批 001 §153）。"""
    from modules.四柱计算器 import calculate_sizhu
    from modules.事项标准 import get_shensha_checker
    events = ['嫁娶', '修造', '动土', '拆舍', '入宅', '作灶', '开业', '出行',
              '安葬', '安床', '移徙', '入学', '求医', '签约']
    banned = {'鸣犬日', '鸣犬对日', '天马日', '反支日'}
    suihe_total = 0
    for e in events:
        ck = get_shensha_checker(e)
        for d in DAYS_2026:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            names = [it['name'] for it in ck.check(sz, owners=[])]
            assert not (banned & set(names)), f'{e} {d} 出现旧名 {banned & set(names)}'
            if e != '修造':
                assert '天恩' not in names, f'{e} {d} 不应有天恩（仅修造保留）'
            if e == '动土':
                assert '天恩' not in names, f'动土手抄日检查不应有天恩 {d}'
                assert '反支日' not in names, f'动土手抄日检查不应有反支日 {d}'
            if e == '修造' and ck._is_suihe(sz):
                suihe_total += 1
    # 岁合挂账不动：2026 修造 36 命中（冻结旧行为）
    assert suihe_total == 36, f'岁合命中数变化: {suihe_total}'


def _assert_mingfei_rules_text():
    """高级安葬规则鸣吠文案必须走典载 13/11 表（旧 10/6 错表已删）。"""
    from modules.rules.高级安葬规则 import AdvancedBurialRuleChecker
    ck = AdvancedBurialRuleChecker()
    assert ck._is_mingfei('壬午') and ck._is_mingfei('甲申') and ck._is_mingfei('乙酉')
    assert not ck._is_mingfei('丙戌')          # 旧戌日
    assert ck._is_mingfeidui('丙子') and ck._is_mingfeidui('癸卯')
    assert not ck._is_mingfeidui('庚辰')        # 旧辰日
    assert not hasattr(ck, 'MINGFEI'), '旧错表常量 MINGFEI 应已删除'
    assert not hasattr(ck, 'MINGFEIDUI'), '旧错表常量 MINGFEIDUI 应已删除'


if __name__ == '__main__':
    for fn in (_assert_structure, _assert_leap_2025,
               _assert_banned_names_and_scope, _assert_mingfei_rules_text):
        try:
            fn()
        except AssertionError as ex:
            print(f'❌ 反向断言失败 [{fn.__name__}]: {ex}')
            sys.exit(1)
    sys.exit(run_cli(CASES))
