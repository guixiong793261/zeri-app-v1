# -*- coding: utf-8 -*-
"""
α 批：A 类 5 项分值漂移收敛锁（2026-10-17 P1-C-3a 起改为"统一至通用值"锁）
================================
背景：SHENSHA_SCORES('嫁娶',X) 表值与 D（modules/婚嫁评分算法.py
score_marriage_day，正常嫁娶日唯一计分引擎）硬编码分值长期漂移：

    神煞     旧表值   D 实际值   α 后表值   P1-C-3a 统一值（表值=D 硬编码同步改）
    天德       +20       +15        +15   →  +20  （通用值）
    月德       +18       +15        +15   →  +18  （通用值）
    天罡日     -25       -40        -40   →  -10  （通用值，仅入学/求医/签约口径）
    河魁日     -25       -40        -40   →  -10  （通用值）
    月破       -30       -40        -40   →  -30  （通用值）

2026-10 用户拍板 α：改 5 个嫁娶键向 D 对齐（历史批次）。
2026-10-17 用户拍板 P1-C-3a（B 族统一至通用值）：表键与 D 硬编码**双轨同步**
改至通用值——α 批"表值随硬编码"的历史结构就此终结，本脚本锁改为
"表值=通用值 且 D 硬编码=同一值"（端到端分值锁随新值）。影响面证据：
  ① 5 名均无 ('*',X) 通配键；
  ② D 硬编码已在 P1-C-3a 同步改值 → 正常嫁娶日总分按新值生效（黄金课
     天德 +5：五行 38→43、总分 43→48，gold 已同步）；
  ③ 表值唯一消费方 MarriageShenShaChecker 仅否决分支运行，本脚本锁其
     否决追溯明细解析值；
  ④ 非嫁娶 13 事项各有独立键（天德 20/月德 18/月破 -30；天罡日/河魁日
     仅入学/求医/签约有键=-10），反向锁确保未被波及。

典据附注（D 既有语义，本批只改数字、不改判定）：
  河魁日＝日支临月破（marriage_shensha.is_hekui_day），与月破同条件，
  D 对月破日同时记 月破-30 与 河魁日-10（P1-C-3a 后值）。

既有谓词漂移（本批不处理，仅记录锁定状态，待后续专项拍板）：
  D 的 is_tiande_day 按【农历月名】取天德（marriage_shensha.py L78-106），
  checker 层 _is_tiande 按【节气月支】（verify_tiande 典据口径）。2026 全年
  两套命中集仅 14 天重合（农历口径 27 天/节气口径 34 天）。故天德 D 端到端
  只锁分值恒为 +15（不锁命中集合）；月德 D 谓词走节气月，2026 与典据 36 天
  全等，按典据口径锁。
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli
import sxtwl

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
CHONG = {'子': '午', '丑': '未', '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
         '午': '子', '未': '丑', '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'}

# 天德月德起例（《协纪》，独立硬编码，不读软件实现）
# 天德：正丁二坤申三壬四辛五乾亥六甲七癸八艮寅九丙十乙子巽巳丑庚
TIANDE = {
    '寅': ('gan', '丁'), '卯': ('zhi', '申'), '辰': ('gan', '壬'), '巳': ('gan', '辛'),
    '午': ('zhi', '亥'), '未': ('gan', '甲'), '申': ('gan', '癸'), '酉': ('zhi', '寅'),
    '戌': ('gan', '丙'), '亥': ('gan', '乙'), '子': ('zhi', '巳'), '丑': ('gan', '庚'),
}
# 月德：寅午戌丙、亥卯未甲、申子辰壬、巳酉丑庚（日干）
_YUEDE_JU = (
    (('寅', '午', '戌'), '丙'), (('亥', '卯', '未'), '甲'),
    (('申', '子', '辰'), '壬'), (('巳', '酉', '丑'), '庚'),
)
YUDE_GAN = {mz: g for zhis, g in _YUEDE_JU for mz in zhis}


# ===== sxtwl 独立推导（节气月支/日柱，verify_yangcuo 同构） =====
def _month_zhi_at(d, hour=12):
    cur = datetime.datetime(d.year, d.month, d.day, hour, 0)
    pts = []
    for y in (d.year - 1, d.year):
        jq = sxtwl.getJieQiByYear(y)
        for idx, mz in ((20, '子'), (22, '丑'), (0, '寅'), (2, '卯'),
                        (4, '辰'), (6, '巳'), (8, '午'), (10, '未'),
                        (12, '申'), (14, '酉'), (16, '戌'), (18, '亥')):
            dd = sxtwl.JD2DD(jq[idx].jd)
            pts.append((datetime.datetime(int(dd.Y), int(dd.M), int(dd.D),
                                          int(dd.h), int(dd.m), int(dd.s)), mz))
    pts.sort()
    mz = '子'
    for t, z in pts:
        if cur >= t:
            mz = z
        else:
            break
    return mz


def _day_gz(d):
    o = sxtwl.fromSolar(d.year, d.month, d.day)
    gz = o.getDayGZ()
    return GAN[gz.tg], ZHI[gz.dz]


def _daterange(y):
    d = datetime.date(y, 1, 1)
    end = datetime.date(y, 12, 31)
    while d <= end:
        yield d
        d += datetime.timedelta(days=1)


DAYS = list(_daterange(2026))


def _hit(name, d):
    """权威命中（sxtwl 独立推月支日柱 + 典载起例）。"""
    mz = _month_zhi_at(d)
    dg, dz = _day_gz(d)
    if name == '天德':
        kind, val = TIANDE[mz]
        return dg == val if kind == 'gan' else dz == val
    if name == '月德':
        return dg == YUDE_GAN[mz]
    if name == '天罡日':
        return dz == mz
    if name in ('月破', '河魁日'):
        return dz == CHONG[mz]
    raise ValueError(name)


# ===== 表值锁 / 反向锁 / 通配锁（失败即 exit 1） =====
def _assert_locks():
    from modules.事项标准 import SHENSHA_SCORES, shensha_score
    # 1) 5 嫁娶键=P1-C-3a 统一通用值（表键与 D 硬编码双轨同步）
    new_vals = {'天德': 20, '月德': 18, '天罡日': -10, '河魁日': -10, '月破': -30}
    for n, v in new_vals.items():
        got = shensha_score('嫁娶', n, None)
        assert got == v, f"('嫁娶','{n}') 应为 {v}（P1-C-3a 统一通用值），实际 {got}"
        assert SHENSHA_SCORES[('嫁娶', n)] == v
    # 2) 反向：非嫁娶 13 事项独立键未受影响
    #    天德：除动土外 12 事项有显式键=20；动土无键（运行时走基类默认 +20）
    all_ev = ('修造', '动土', '拆舍', '入宅', '开业', '出行', '安床', '作灶',
              '移徙', '入学', '求医', '签约', '安葬')
    for ev in all_ev:
        exp_tiande = None if ev == '动土' else 20
        # 入宅/移徙 月破键随删除批（入宅 x4 001 §127；移徙删候10键 001 §125）
        # 移除，现行口径 shensha_score 返回 None（H4 批同步，不再锁 -30）。
        exp_yuepo = None if ev in ('入宅', '移徙') else -30
        assert shensha_score(ev, '天德', None) == exp_tiande, f'{ev} 天德应保持 {exp_tiande}'
        assert shensha_score(ev, '月德', None) == 18, f'{ev} 月德应保持 18'
        assert shensha_score(ev, '月破', None) == exp_yuepo, f'{ev} 月破应保持 {exp_yuepo}'
    for ev in ('入学', '求医', '签约'):
        assert shensha_score(ev, '天罡日', None) == -10, f'{ev} 天罡日应保持 -10'
        assert shensha_score(ev, '河魁日', None) == -10, f'{ev} 河魁日应保持 -10'
    # 非通用事项不得有天罡/河魁键（嫁娶专属外仅通用兜底三事项）
    for ev in ('修造', '安葬', '出行', '开业'):
        assert shensha_score(ev, '天罡日', None) is None, f'{ev} 不应有天罡日键'
        assert shensha_score(ev, '河魁日', None) is None, f'{ev} 不应有河魁日键'
    # 3) 5 名无通配键（改嫁娶键不波及其余事项的结构前提）
    for n in new_vals:
        assert ('*', n) not in SHENSHA_SCORES, f"('*','{n}') 通配键不应存在"


# ===== D 端到端：月德/天罡/河魁/月破 按典据命中集全年穷举；
#         天德因 D 谓词农历月漂移，仅锁"凡发射必为 +20"（分值锁，不锁命中集） =====
from modules.婚嫁评分算法 import score_marriage_day

_CANON_LABEL = {'月德': ('月德', 18),
                '天罡日': ('天罡日（妨翁）', -10), '河魁日': ('河魁日（妨姑）', -10),
                '月破': ('月破', -30)}


def _make_d_adapter(name):
    label, val = _CANON_LABEL[name]

    def _ad(d):
        r = score_marriage_day(d)
        return any(x[0] == label and x[1] == val for x in r.get('details', []))
    return _ad


def _d_tiande_value_lock(d):
    """天德纯分值锁：当日 D 若无天德条目→通过；有则必须恰好一条 +20（不得出现旧值 15）。"""
    r = score_marriage_day(d)
    vals = [x[1] for x in r.get('details', []) if x[0] == '天德']
    return (not vals) or vals == [20]


# ===== checker 层（表值消费方）端到端：必须按工厂链路打 _std_event 戳 =====
from modules.四柱计算器 import calculate_sizhu
from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
from modules.shensha.修造神煞 import ConstructionShenShaChecker


def _make_pipe_adapter(name, score):
    def _ad(d):
        c = MarriageShenShaChecker()
        c._std_event = '嫁娶'   # 与 事项标准.get_shensha_checker 工厂链路一致
        c.check(calculate_sizhu(d, 12, 0))
        return [x.get('score') for x in c.shensha_list
                if isinstance(x, dict) and x.get('name') == name] == [score]
    return _ad


def _make_xianzao_reverse_adapter(d):
    """反向：修造 checker 月破日仍解析 ('修造','月破')=-30。"""
    def _ad(_):
        c = ConstructionShenShaChecker()
        c._std_event = '修造'
        c.check(calculate_sizhu(d, 12, 0))
        return [x.get('score') for x in c.shensha_list
                if isinstance(x, dict) and x.get('name') == '月破'] == [-30]
    return _ad


def _build_cases():
    cases = [ShenShaCase(
        name='P1C3a-D端到端·天德分值锁(+20)', category='A',
        description='D 天德谓词走农历月（与节气典据漂移待专项），全年 365 天'
                    '凡发射必为 +20（P1-C-3a 统一值），绝不出现旧值 +15',
        inputs=DAYS, expected=lambda d: True,
        adapter=_d_tiande_value_lock, compare='bool')]
    for name in ('月德', '天罡日', '河魁日', '月破'):
        # §212 后嫁娶通道已剥离天罡日/河魁日（D 硬编码块删除）→ 期望恒 False
        exp = (lambda d, n=name: False) if name in ('天罡日', '河魁日') \
            else (lambda d, n=name: _hit(n, d))
        cases.append(ShenShaCase(
            name=f'α-D端到端·{name}', category='A',
            description=f"score_marriage_day details 在权威命中日含 {_CANON_LABEL[name]}，"
                        f'非命中日不含（2026 全年穷举，sxtwl 独立推月支/日柱）'
                        + ('；§212 后嫁娶已剥离 → 恒 False' if name in ('天罡日', '河魁日') else ''),
            inputs=DAYS, expected=exp,
            adapter=_make_d_adapter(name), compare='bool'))
    for name, score in (('天德', 20), ('月德', 18), ('天罡日', -10),
                        ('河魁日', -10), ('月破', -30)):
        hit_days = [d for d in DAYS if _hit(name, d)]
        # §212 后嫁娶 checker 不再发射天罡日/河魁日 → 期望恒 False
        exp = (lambda d: False) if name in ('天罡日', '河魁日') else (lambda d: True)
        cases.append(ShenShaCase(
            name=f'α-嫁娶checker·{name}={score}', category='A',
            description=f'否决追溯明细：工厂链路 MarriageShenShaChecker 在典据命中日解析表值 {score}'
                        + ('；§212 后已剥离 → 恒 False' if name in ('天罡日', '河魁日') else ''),
            inputs=hit_days, expected=exp,
            adapter=_make_pipe_adapter(name, score), compare='bool'))
    # 修造月破反向锁（独立键 -30，全年取一个月破日）
    po_day = next(d for d in DAYS if _hit('月破', d))
    cases.append(ShenShaCase(
        name='α-反向·修造月破保持-30', category='A',
        description=f'{po_day} 月破日 ConstructionShenShaChecker 仍解析修造独立键 -30',
        inputs=[po_day], expected=lambda d: True,
        adapter=_make_xianzao_reverse_adapter(po_day), compare='bool'))
    return cases


if __name__ == '__main__':
    try:
        _assert_locks()
    except AssertionError as e:
        print(f'❌ α 表值/反向/通配锁失败: {e}')
        sys.exit(1)
    # 命中集健全性：D 口径=小时级精确节气（calculate_sizhu 12:00），交节日
    # 12:00 前仍属旧月，故 2026 天德为 34 天（日界口径 verify_tiande=36 天，
    # 差异仅立秋/立冬两个交节日，为既有口径差，与 α 无关）。
    _n_tiande = sum(1 for d in DAYS if _hit('天德', d))
    assert _n_tiande == 34, f'D 口径 2026 天德应为 34 天，实际 {_n_tiande}'
    for n in ('月德', '天罡日', '河魁日', '月破'):
        assert sum(1 for d in DAYS if _hit(n, d)) > 20, f'{n} 2026 命中集异常偏少'
    print('P1-C-3a 锁自检通过：5 键=通用值（表+D 双轨同值）；非嫁娶键不变；无通配；2026 天德 D 口径 34 天')
    sys.exit(run_cli(_build_cases()))
