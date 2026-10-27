# -*- coding: utf-8 -*-
"""
A4 批·逻辑错（判定条件放宽）2 项穷举验证
=========================================
将星、三奇——两项与 A1-A3 的"表错/名实错/比较对象错"不同：典据表值本身
无勘误表可对，错在**判定条件被放宽**（集合变大）。修复方向为收紧判定：
三奇为严格缩窄（新集⊂旧集）；将星主体为缩窄（180→91，旧独有 120 半合
撤销），另 31 天新独有为旧实现"另两支"写法结构性漏判的中神本气月自临
（午月午日等典载正格），属顺带恢复，已逐日断言留档。

典据与拍板（2026-09-25 用户拍板）：
  将星——命理神煞，《协纪辨方书》年神/月神义例均未收。《三命通会》：
         "将星者，如大将驻扎中军中也，故以三合中位为将星"。旧谓词以
         日支起局、月支为日支三合"另两支"之一即算（半合也算，且结构上
         排除月支=日支），2025-2027 命中 180 天。拍板 C 口径（月神查日支
         惯例）：月支三合局中神专位比日支（寅午戌月午日/巳酉丑月酉日/
         申子辰月子日/亥卯未月卯日），同期 91 天，交 60、旧独有 120
         （半合误报撤销）、新独有 31（午月午日等中神本气月自临，旧实现
         因"另两支"写法结构性漏判的典载最正宗配置，顺带恢复）。
  三奇——四柱天干三奇《协纪》未立义例（卷八"八节三奇"为九宫到山到方
         法，与此无关）。《三命通会》卷三："三奇要顺布，不欲倒乱，如
         乙丙丁、甲戊庚，天干年月日时顺布为吉"。旧谓词"四柱含齐即算"
         （乱序/隔位/干重复均算），74 天/三年。拍板顺布连珠：奇干按序
         占连续三柱（年月日 或 月日时），同期仅 3 天（2025-10-15/25、
         11-04，均乙丙丁），交 3、旧独有 71、新独有 0。

顺带修复：
  出行日块异名'三奇'、开业日块异名'{日/月}三奇'与基类 super 日块
  '三奇{日/月/星}'异名双扣（各 +15）——删除；六事项同名死分支清理
  （super 已注册，_add_shensha 同名去重屏蔽）；通用'三奇-{type}'
  统一正名。

双保险：
1. 权威表/旧放宽口径全部硬编码于本文件，绝不从产品读取；
2. 年干立春界、月支交节时刻、月干五虎遁、时干五鼠遁、日柱均由 sxtwl
   天文历点独立推导；产品侧仅调用基类谓词与 checker，杜绝自证。

含：2025-2027 共 1095 天谓词穷举；新旧集合代数五数硬锁（三奇新⊂旧；
将星新独有 31 全部断言为中神本气月自临）；端到端 3 个 checker
（修造/嫁娶/签约，签约走通用）将星 2026 全年、三奇 2025 全年
「恰一条＋分值锁」；新旧样例硬锁；双扣消除结构断言。
"""
import sys
import datetime
import inspect
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值（硬编码，不读产品） =====
# 将星：月支三合局【中神】比日支（C 口径）
JIANGXING_ZHONG = {
    '寅': '午', '午': '午', '戌': '午',
    '巳': '酉', '酉': '酉', '丑': '酉',
    '申': '子', '子': '子', '辰': '子',
    '亥': '卯', '卯': '卯', '未': '卯',
}
# 三奇顺布连珠序列
SANQI_SEQ = (('乙', '丙', '丁'), ('甲', '戊', '庚'), ('壬', '癸', '辛'))
SANQI_LABEL = {('乙', '丙', '丁'): '日', ('甲', '戊', '庚'): '月',
               ('壬', '癸', '辛'): '星'}

# ===== 旧放宽口径（仅用于集合代数硬锁，同样硬编码） =====
# 旧代码实际语义：日支 -> 三合【另两支】（注意排除日支自身）。
# 后果：半合月（月支为日支同局另支）误报；同时月支=日支的中神本气月
# （午月午日等）结构上永不可命中——此为旧实现附带漏判。
_OLD_JIANGXING_MATES = {
    '寅': ('午', '戌'), '午': ('寅', '戌'), '戌': ('寅', '午'),
    '巳': ('酉', '丑'), '酉': ('巳', '丑'), '丑': ('巳', '酉'),
    '申': ('子', '辰'), '子': ('申', '辰'), '辰': ('申', '子'),
    '亥': ('卯', '未'), '卯': ('亥', '未'), '未': ('亥', '卯'),
}


def _all_days(*years):
    for y in years:
        d = datetime.date(y, 1, 1)
        end = datetime.date(y, 12, 31)
        while d <= end:
            yield d
            d += datetime.timedelta(days=1)


DAYS = list(_all_days(2025, 2026, 2027))
DAYS_2025 = [d for d in DAYS if d.year == 2025]
DAYS_2026 = [d for d in DAYS if d.year == 2026]


def _jieqi_points(year):
    """当年 12 节（换月点）(datetime, 月支)；getJieQiByYear idx 立春=0。"""
    jq = sxtwl.getJieQiByYear(year)
    pts = []
    for idx, mz in ((20, '子'), (22, '丑'), (0, '寅'), (2, '卯'),
                    (4, '辰'), (6, '巳'), (8, '午'), (10, '未'),
                    (12, '申'), (14, '酉'), (16, '戌'), (18, '亥')):
        dd = sxtwl.JD2DD(jq[idx].jd)
        pts.append((datetime.datetime(int(dd.Y), int(dd.M), int(dd.D),
                                      int(dd.h), int(dd.m), int(dd.s)), mz))
    return sorted(pts)


_MORDER = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']


def _sizhu_independent(d, hour=12):
    """四柱干支全独立推导：年干立春界、月支交节时刻、月干五虎遁、
    日柱 sxtwl 直取、时干五鼠遁（午时）。"""
    cur = datetime.datetime(d.year, d.month, d.day, hour, 0)
    pts = _jieqi_points(d.year - 1) + _jieqi_points(d.year)
    pts.sort()
    mz, pillar_year = '子', d.year - 1
    for t, z in pts:
        if cur >= t:
            mz = z
            if z == '寅':
                pillar_year = t.year
        else:
            break
    yg = GAN[(pillar_year - 4) % 10]
    mg = GAN[((GAN.index(yg) % 5) * 2 + 2 + _MORDER.index(mz)) % 10]
    g = sxtwl.fromSolar(d.year, d.month, d.day).getDayGZ()
    dg, dz = GAN[g.tg], ZHI[g.dz]
    hg = GAN[((GAN.index(dg) % 5) * 2 + 6) % 10]   # 午时=子后第6支
    return {'year_gan': yg, 'month_gan': mg, 'day_gan': dg, 'hour_gan': hg,
            'month_zhi': mz, 'day_zhi': dz, 'date': d}


def _gold(d):
    """将星 bool / 三奇 '日'|'月'|'星'|None 典载真值。"""
    s = _sizhu_independent(d)
    jx = s['day_zhi'] == JIANGXING_ZHONG[s['month_zhi']]
    seq = (s['year_gan'], s['month_gan'], s['day_gan'], s['hour_gan'])
    sq = None
    for q in SANQI_SEQ:
        if tuple(seq[0:3]) == q or tuple(seq[1:4]) == q:
            sq = SANQI_LABEL[q]
            break
    return {'将星': jx, '三奇': sq}


def _old_jiangxing(s):
    """旧放宽口径（产品实际语义）：月支 ∈ 日支三合另两支（半合即算，
    但排除日支自身，故中神本气月自临反成漏判）。"""
    return s['month_zhi'] in _OLD_JIANGXING_MATES.get(s['day_zhi'], ())


def _old_sanqi(s):
    """旧放宽口径：四柱含齐 3 奇干即算（乱序/隔位/重复均算）。"""
    g = {s['year_gan'], s['month_gan'], s['day_gan'], s['hour_gan']}
    return any(all(x in g for x in q) for q in SANQI_SEQ)


# ---------- 谓词穷举 cases ----------
def _adapter_pred(d):
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        c = ShenShaChecker()
        s = _sizhu_independent(d)
        return {'将星': c._is_jiangxing(s), '三奇': c._is_sanqi(s)}
    except Exception:
        return _UNAVAILABLE


def _make_pred_case(name, compare):
    key = name

    def expected(d):
        return _gold(d)[key]

    def adapter(d):
        r = _adapter_pred(d)
        return r if r is _UNAVAILABLE else r[key]

    return ShenShaCase(
        name=f'A4-{name}谓词', category='B',
        description=f'{name}典载收紧口径 2025-2027 共1095天穷举（四柱干支均 '
                    f'sxtwl 独立推导：年干立春/月支交节/五虎遁/五鼠遁）',
        inputs=DAYS, expected=expected, adapter=adapter, compare=compare)


# ---------- 端到端：恰一条 + 分值锁 ----------
def _make_e2e_case(event, target, year_days):
    is_jx = target == '将星'

    def expected(d):
        g = _gold(d)
        if is_jx:
            return (('将星', 12),) if g['将星'] else ()
        return ((f'三奇{g["三奇"]}', 15),) if g['三奇'] else ()

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
            if is_jx:
                sel = [(it['name'], it['score']) for it in items
                       if it['name'] == '将星']
            else:
                sel = [(it['name'], it['score']) for it in items
                       if it['name'] in ('三奇日', '三奇月', '三奇星')]
            names = [n for n, _ in sel]
            if len(names) != len(set(names)):
                return f'BAD:DUP{sel}'
            return tuple(sorted(sel))
        except Exception:
            return _UNAVAILABLE

    win = '2026' if is_jx else '2025'
    reason = ('将星 30 天典载' if is_jx else
              '三奇 3 天典载（2026 零命中，窗口移 2025）')
    return ShenShaCase(
        name=f'A4-{target}{event}端到端', category='B',
        description=f'{event} checker {win} 全年：{target}典载日恰一条且分值锁'
                    f'（异名双扣消除，{reason}）',
        inputs=year_days, expected=expected, adapter=adapter, compare='eq')


# ---------- 新旧样例硬锁 ----------
# (日期, 项, 典载判定, 说明)；均经 sxtwl 独立推导核对
LOCKS = [
    # 将星（新=中神专位；旧独有=同局半合；新独有=中神本气月自临）
    (datetime.date(2026, 1, 2),  '将星', True,  '子月子日典载（中神本气月自临，旧漏判）'),
    (datetime.date(2026, 1, 11), '将星', True,  '丑月酉日典载（巳酉丑中神酉，新旧交）'),
    (datetime.date(2025, 3, 23), '将星', True,  '卯月卯日典载（中神本气月自临，旧漏判）'),
    (datetime.date(2025, 6, 18), '将星', True,  '午月午日典载（中神本气月自临，旧漏判）'),
    (datetime.date(2026, 1, 7),  '将星', False, '丑月巳日旧误报（巳酉丑半合）'),
    (datetime.date(2026, 1, 15), '将星', False, '丑月丑日旧误报（丑酉半合）'),
    # 三奇（新=顺布连珠；旧独有=含齐而倒乱）
    (datetime.date(2025, 10, 15),'三奇', True,  '乙丙丁年月日顺布典载'),
    (datetime.date(2025, 11, 4), '三奇', True,  '乙丙丁年月日顺布典载'),
    (datetime.date(2026, 1, 3),  '三奇', False, '乙戊丁丙旧误报（含齐倒乱）'),
    (datetime.date(2026, 7, 12), '三奇', False, '丙乙丁丙旧误报（乱序+重复）'),
    (datetime.date(2026, 10, 17),'三奇', False, '丙戊甲庚旧误报（隔位倒乱）'),
]


def _expected_lock(t):
    return bool(t[2])


def _adapter_lock(t):
    d, name, _, _ = t
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        c = ShenShaChecker()
        s = _sizhu_independent(d)
        r = c._is_jiangxing(s) if name == '将星' else bool(c._is_sanqi(s))
        return r
    except Exception:
        return _UNAVAILABLE


case_locks = ShenShaCase(
    name='A4-新旧样例硬锁', category='B',
    description='将星中神专位日命中＋同局半合旧误报日不命中；三奇顺布连珠日'
                '命中＋含齐倒乱旧误报日不命中',
    inputs=LOCKS, expected=_expected_lock, adapter=_adapter_lock, compare='bool')


CASES = [_make_pred_case('将星', 'bool'), _make_pred_case('三奇', 'eq')]
CASES.extend(_make_e2e_case(e, '将星', DAYS_2026)
             for e in ('修造', '嫁娶', '签约'))
CASES.extend(_make_e2e_case(e, '三奇', DAYS_2025)
             for e in ('修造', '嫁娶', '签约'))
CASES.append(case_locks)


# ---------- 独立反向断言 ----------
def _assert_structure():
    assert len(JIANGXING_ZHONG) == 12
    assert set(JIANGXING_ZHONG) == set(ZHI)
    assert set(JIANGXING_ZHONG.values()) == {'午', '酉', '子', '卯'}
    assert len(SANQI_SEQ) == 3 and all(len(q) == 3 for q in SANQI_SEQ)
    # 三奇 9 干互斥（乙丙丁/甲戊庚/壬癸辛，唯己干不入奇）
    allq = [g for q in SANQI_SEQ for g in q]
    assert len(allq) == 9 and len(set(allq)) == 9 and '己' not in allq


def _assert_set_algebra():
    """新旧集合代数硬锁。

    将星（旧半合 vs 新中神专位）：180→91，交 60、旧独有 120（半合误报
    撤销）、新独有 31——新独有全部为中神本气月自临（午月午日/卯月卯日/
    酉月酉日/子月子日），旧代码月支比"另两支"结构上漏判，属典载最正宗
    配置的顺带恢复（非新口径误增）。
    三奇：74→3，严格缩窄，新集⊂旧集，新独有=0。
    """
    oj = nj = osq = nsq = 0
    jx_newonly = []
    for d in DAYS:
        s = _sizhu_independent(d)
        o1, n1 = _old_jiangxing(s), _gold(d)['将星']
        o2, n2 = _old_sanqi(s), bool(_gold(d)['三奇'])
        oj += o1; nj += n1; osq += o2; nsq += n2
        assert not (n2 and not o2), '三奇新集必须⊂旧集（严格缩窄）'
        if n1 and not o1:
            jx_newonly.append((s['month_zhi'], s['day_zhi']))
    assert (oj, nj) == (180, 91), (oj, nj)
    assert (osq, nsq) == (74, 3), (osq, nsq)
    assert len(jx_newonly) == 31, len(jx_newonly)
    # 新独有 31 格必须全部 月支=日支=该局中神
    assert all(mz == dz == JIANGXING_ZHONG[mz] for mz, dz in jx_newonly)
    return {'将星': (oj, nj, 60, 120, 31), '三奇': (osq, nsq, 3, 71, 0)}


def _assert_year_counts():
    c = {y: {'将星': 0, '三奇': 0} for y in (2025, 2026, 2027)}
    for d in DAYS:
        g = _gold(d)
        if g['将星']:
            c[d.year]['将星'] += 1
        if g['三奇']:
            c[d.year]['三奇'] += 1
    assert c[2025]['将星'] == 30 and c[2026]['将星'] == 30 and c[2027]['将星'] == 31
    assert c[2025]['三奇'] == 3 and c[2026]['三奇'] == 0 and c[2027]['三奇'] == 0
    return c


def _assert_no_double_registration():
    """双扣消除结构断言：出行/开业日块不再注册三奇；通用正名；
    入宅手抄谓词 override 已删。"""
    from modules.shensha import 出行神煞, 开业神煞, 入宅神煞, 通用神煞
    cx = inspect.getsource(出行神煞)
    ky = inspect.getsource(开业神煞)
    assert "_add_shensha('三奇'" not in cx, '出行异名三奇块应删除'
    assert "_add_shensha(f'{sanqi_result}三奇'" not in ky, '开业异名三奇块应删除'
    rz_src = inspect.getsource(入宅神煞)
    assert 'def _is_sanqi(' not in rz_src, '入宅三奇手抄 override 应删除'
    ty_src = inspect.getsource(通用神煞.CommonShenShaChecker._check_day_shensha)
    assert "f'三奇{sanqi_type}'" in ty_src, '通用三奇应统一正名 三奇{type}'
    assert "add_shensha(f'三奇-" not in ty_src, '通用不应再注册旧名 三奇-{type}'


def main():
    _assert_structure()
    alg = _assert_set_algebra()
    yc = _assert_year_counts()
    _assert_no_double_registration()
    print(f'[A4] 反向断言通过；五数(旧,新,交,旧独有,新独有)={alg}；分年={yc}')
    print('[A4 批·逻辑错 2 项（将星中神专位/三奇顺布连珠）穷举验证]')
    return run_cli(CASES)


if __name__ == '__main__':
    sys.exit(main())
