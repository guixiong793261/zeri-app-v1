# -*- coding: utf-8 -*-
"""
A3 批·表本身错 3 项穷举验证
============================
飞廉、八专、五墓——三项均非"名实错"（委托错神煞），而是表本身错
（谓词内联的查法表值错误），修复后新旧命中集发生真实位移。

典据与拍板：
  飞廉  ——《协纪辨方书》卷四·月神：寅月戌、卯月巳、辰月午、巳月未、
            午月寅、未月卯、申月辰、酉月亥、戌月子、亥月丑、子月申、
            丑月酉。原"正五行查"（月支五行=日支五行）与典载全年 0 天
            重合（只读诊断交集=0），属表本身错。月神，注册点由年作用域
            移入月作用域。
  八专  ——《历例》B5 版 5 柱：丁未、己未、庚申、甲寅、癸丑。原 12 柱
            错表（含丙午、戊申、己酉等伪柱）与 B5 全年仅 24 天重合。
            拍板采 B5，废弃《协纪》A8 版 8 柱（口径分歧留档 001）。
  五墓  ——《协纪》卷四·月神：寅卯月乙未、巳午月丙戌、申酉月辛丑、
            亥子月壬辰、辰戌丑未月戊辰。原"春未夏戌秋丑冬辰"纯地支
            过宽且月分组错（辰月入春 vs 典载入四季），与典载全年仅
            5 天重合，属表本身错。

顺带修复：
  通用神煞守日误用八专访词（同日守日 +8 与八专 -15 并挂）——断开注册，
  守日归批次 D「王官守相民」体系待翻《协纪》原诀（挂账）。
  修造五墓 -20 死分支删除——基类 super 先行注册五墓且事项标准修造无键，
  有效值恒为基类兜底 -12，对齐事项标准（单独 commit）。

双保险：
1. 权威表全部硬编码于本文件，绝不从产品读取；
2. 年干以立春、月支以节气交节时刻由 sxtwl 天文历点独立推导，日柱
   由 sxtwl 直取；产品侧仅调用基类谓词与 checker，杜绝自证。

含：2025-2027 共 1095 天谓词穷举；端到端 3 个 checker（修造/嫁娶/签约）
2026 全年「恰一条＋分值锁」；新旧样例硬锁（典载日命中＋旧表误报日不命中）；
60 甲子周期计数（飞廉 6 命中/八专 5/五墓按月支变）；3 项典载 2026 全年
命中数冻结；飞廉月神注册点断言（基类年作用域不再注册飞廉）。
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
# 飞廉（《协纪》卷四·月神）按【月支→日支】
FEILIAN_ZHI = {
    '寅': '戌', '卯': '巳', '辰': '午', '巳': '未',
    '午': '寅', '未': '卯', '申': '辰', '酉': '亥',
    '戌': '子', '亥': '丑', '子': '申', '丑': '酉',
}
# 八专（《历例》B5 版）按【日柱集合】
BAZHUAN_PILLARS = frozenset(('丁未', '己未', '庚申', '甲寅', '癸丑'))
# 五墓（《协纪》卷四·月神）按【月支→日柱】
WUMU_PILLAR = {
    '寅': '乙未', '卯': '乙未', '辰': '戊辰',
    '巳': '丙戌', '午': '丙戌', '未': '戊辰',
    '申': '辛丑', '酉': '辛丑', '戌': '戊辰',
    '亥': '壬辰', '子': '壬辰', '丑': '戊辰',
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
    """3 项典载真值。"""
    yg, mz = _year_month_at(d)
    pillar, dg, dz = _day_pillar(d)
    return {
        '飞廉': dz == FEILIAN_ZHI[mz],
        '八专': pillar in BAZHUAN_PILLARS,
        '五墓': pillar == WUMU_PILLAR[mz],
    }


# ---------- 谓词穷举 cases ----------
_PRED_NAMES = ['飞廉', '八专', '五墓']
_PRED_METHOD = {'飞廉': '_is_flyinglian', '八专': '_is_bazhuan', '五墓': '_is_wumu'}


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
        name=f'A3-{name}谓词', category='B',
        description=f'{name}典载口径 2025-2027 共1095天穷举（年干立春/月支节气/'
                    f'日柱均 sxtwl 独立推导）',
        inputs=DAYS, expected=expected, adapter=adapter, compare='bool')


# ---------- 端到端：恰一条 + 分值锁（3 checker × 2026 全年） ----------
# 修造：五墓-12（基类月作用域）
#   （八专已删——2026-10-18 月家P1：协纪仅忌军事+嫁娶，修造超范围；
#     飞廉已删——2026-10-21 口径收口批 001 §153 拍板选2：岁方神→撤日辰
#     发射与计分，谓词保留历法展示，docs/下半场第一批_八项三库取证_20261021.md §1.3）
# 嫁娶：八专-15（嫁娶，有典据保留）、五墓-12（基类月作用域）（飞廉已删同上）
# 签约（走通用神煞）：五墓-12（通用）（飞廉/八专均已删）
TARGETS_ALL = ['飞廉', '八专', '五墓']
SCORES = {
    '修造': {'五墓': -12},
    '嫁娶': {'八专': -15, '五墓': -12},
    '签约': {'五墓': -12},
}
GOLD_KEY = {'飞廉': '飞廉', '八专': '八专', '五墓': '五墓'}


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
            # 口径收口批（001 §153）：飞廉任何事项不得发射（岁方神撤日辰发射）
            if '飞廉' in names:
                return f'BAD:SCOPE-飞廉{sel}'
            return tuple(sorted(sel))
        except Exception:
            return _UNAVAILABLE

    return ShenShaCase(
        name=f'A3-{event}端到端', category='B',
        description=f'{event} checker 2026 全年：在册神煞典载日恰一条且分值锁'
                    f'（A3 修复后表归位；飞廉已按口径收口批 001 §153 撤发射）',
        inputs=DAYS_2026, expected=expected, adapter=adapter, compare='eq')


# ---------- 新旧样例硬锁 ----------
# (日期, 神煞谓词名, 典载判定, 说明)
# 日期均经 sxtwl 独立推导月支+日柱核对。
LOCKS = [
    # 飞廉（旧"正五行查"月支五行=日支五行，与典载 0 天重合）
    (datetime.date(2026, 2, 5),  '飞廉', True,  '庚戌典载（寅月戌日）旧漏报'),
    (datetime.date(2026, 3, 8),  '飞廉', True,  '辛巳典载（卯月巳日）旧漏报'),
    (datetime.date(2026, 2, 9),  '飞廉', False, '甲寅旧误报（寅月寅日=正五行查）'),
    # 八专（旧 12 柱错表，与 B5 全年仅 24 天重合）
    (datetime.date(2026, 2, 2),  '八专', True,  '丁未典载（B5）'),
    (datetime.date(2026, 2, 8),  '八专', True,  '癸丑典载（B5）'),
    (datetime.date(2026, 2, 9),  '八专', True,  '甲寅典载（B5）'),
    (datetime.date(2026, 2, 14), '八专', True,  '己未典载（B5，新旧表均含）'),
    (datetime.date(2026, 2, 15), '八专', True,  '庚申典载（B5，新旧表均含）'),
    (datetime.date(2026, 2, 1),  '八专', False, '丙午旧误报（旧 12 柱表有，B5 无）'),
    # 五墓（旧"春未夏戌秋丑冬辰"纯地支过宽+辰月分组错，与典载仅 5 天重合）
    (datetime.date(2026, 4, 24), '五墓', True,  '戊辰典载（辰月戊辰日）旧漏报'),
    (datetime.date(2026, 5, 12), '五墓', True,  '丙戌典载（巳月丙戌日）'),
    (datetime.date(2026, 11, 14),'五墓', True,  '壬辰典载（亥月壬辰日）'),
    (datetime.date(2026, 2, 14), '五墓', False, '己未旧误报（寅月未日，旧"春在未"纯地支）'),
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
    name='A3-新旧样例硬锁', category='B',
    description='3 神煞各取典载命中日＋旧表误报日：新谓词判定必须与典载一致'
                '（飞廉旧表 0 天重合全漏全误/八专旧 12 柱表/五墓旧纯地支过宽）',
    inputs=LOCKS, expected=_expected_lock, adapter=_adapter_lock, compare='bool')


CASES = [_make_pred_case(n) for n in _PRED_NAMES]
CASES.extend([_make_e2e_case(e) for e in ('修造', '嫁娶', '签约')])
CASES.append(case_locks)


# ---------- 独立反向断言 ----------
def _assert_structure():
    """权威表结构自证 + 60 甲子周期计数。"""
    # 飞廉表 12 键完整
    assert len(FEILIAN_ZHI) == 12 and set(FEILIAN_ZHI) == set(ZHI)
    # 飞廉值无重复（12 月支映射 12 个不同日支）
    assert len(set(FEILIAN_ZHI.values())) == 12, '飞廉 12 月值应互异'
    # 八专 B5 恰 5 柱
    assert len(BAZHUAN_PILLARS) == 5
    # 五墓表 12 键完整，值仅 4 个日柱（乙未/丙戌/辛丑/壬辰/戊辰=5 个）
    assert len(WUMU_PILLAR) == 12 and set(WUMU_PILLAR) == set(ZHI)
    assert set(WUMU_PILLAR.values()) == {'乙未', '丙戌', '辛丑', '壬辰', '戊辰'}


def _assert_cycle_counts():
    """60 甲子周期内各神煞命中数（典载口径冻结）。"""
    # 飞廉按月支比日支：60 甲子表中每月支对应固定日支，跨周期均匀
    # 八专 5 柱：每个 60 甲子周期恰 5 天
    bz = [p for p in _cycle60() if p in BAZHUAN_PILLARS]
    assert len(bz) == 5, f'八专 60 甲子应 5 天命中，实 {len(bz)}'
    # 五墓按月支分组，日柱与月支绑定，不做 60 甲子计数（月支非周期函数）


def _cycle60():
    out = []
    for gi in range(60):
        out.append(GAN[gi % 10] + ZHI[gi % 12])
    return out


def _assert_feilian_month_scope():
    """飞廉注册点已移入基类月作用域，年作用域不再注册飞廉。"""
    import inspect
    from modules.shensha.神煞基类 import ShenShaChecker
    year_src = inspect.getsource(ShenShaChecker._check_year_shensha)
    month_src = inspect.getsource(ShenShaChecker._check_month_shensha)
    assert '飞廉' not in year_src, '基类年作用域不应再注册飞廉（典载为月神）'
    assert '飞廉' in month_src, '基类月作用域应注册飞廉'


def _assert_2026_counts():
    """3 项典载 2026 全年命中数冻结（反向断言防回归）。"""
    counts = {'飞廉': 0, '八专': 0, '五墓': 0}
    for d in DAYS_2026:
        g = _gold(d)
        for k in counts:
            if g[k]:
                counts[k] += 1
    # 实测冻结（本脚本 sxtwl 独立推导，交节时刻换将）：
    #   2025 {飞廉28 八专30 五墓6} / 2026 {飞廉31 八专30 五墓6} / 2027 {飞廉29 八专30 五墓7}
    # 飞廉 2026=31（每月 1 日支×12 月，跨立春月边界致年度浮动 28~31）
    assert counts['飞廉'] == 31, f'飞廉 2026 典载命中应 31 天，实 {counts["飞廉"]}'
    # 八专 5 柱×6 次/年=30（60甲子周期恒定）
    assert counts['八专'] == 30, f'八专 2026 典载命中应 30 天，实 {counts["八专"]}'
    # 五墓 5 日柱按月支分组，2026=6（跨节气月边界浮动 6~7）
    assert counts['五墓'] == 6, f'五墓 2026 典载命中应 6 天，实 {counts["五墓"]}'
    return counts


def main():
    _assert_structure()
    _assert_cycle_counts()
    _assert_feilian_month_scope()
    counts = _assert_2026_counts()
    print(f'[A3] 反向断言通过；2026 典载命中冻结：{counts}')
    print('[A3 批·表本身错 3 项（飞廉/八专/五墓）穷举验证]')
    return run_cli(CASES)


if __name__ == '__main__':
    sys.exit(main())
