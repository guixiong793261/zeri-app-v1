# -*- coding: utf-8 -*-
"""§64 验证（2026-10-09 拍板）：B3 四柱临三煞按柱分级 + D2 作灶次级神煞降级
+ 必修1 §63 降级回弹修复（真/假低分区分）+ 必修2 山向类/事主类日时柱口径对齐。

拍板口径：
- B3：年三煞犯月柱事主类维持否决；年三煞犯日/时柱两类事项统一强扣分不否决；
  坐山修方犯年三煞仍否决。通道分（日柱-30/时柱-20）只入总分，不进五行门槛。
- D2：天火日/地火日/灶君忌日/土府日从作灶一票否决降级强扣分；月破/岁破/
  四离四绝/冲主妇/冲宅主/灶君朝天/逐月作灶忌日维持否决。防双扣：天火/地火/
  土府当日神煞命中则走神煞分、规则 ji 不计忌事 -15；未命中（规则与神煞两套
  公式存在差异）仍忌事 -15，保证强扣分必落一笔。
- 必修1：五行 <30 时回退"扣分不否决"降级项的忌事实扣分（+作灶神煞分
  +§63 月份不宜传导分）后重判——回退后≥30 且无未制化硬煞为"假低分"放行；
  回退仅用于否决判定，展示分不变；仍 <30 或有硬煞为"真低分"维持否决。
- 必修2：日/时柱临三煞 spv 口径统一（山向类/事主类均不否决）；月柱差异保留
  有典据（修方论坐山 vs 事主四柱论命）。

样本均为 12:00（午时）真实排盘 + Scorer.score 真实入口评分得出。
退出码：全过 0，有失败 1。
"""
import datetime as dt
import sys

sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer

FAILS = []


def check(name, cond, detail=''):
    tag = 'PASS' if cond else 'FAIL'
    print(f'[{tag}] {name}' + (f' | {detail}' if detail and not cond else ''))
    if not cond:
        FAILS.append(name)


OWNER1 = [{'name': '主', 'role': '事主', 'birth_date': '1972-01-08', '生肖': '亥'}]
KUN = '坤山艮向兼未'


def run(d, ev, owners=None, shan=None):
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d; sz['year'] = d.year; sz['month'] = d.month; sz['day'] = d.day
    return Scorer().score(sz, ev, owners=owners, shan_xiang=shan)


def vetos(r):
    return [str(v) for v in (r.get('veto_reasons') or [])]


def wx(r):
    return r.get('wu_xing_result') or {}


def bd_of(r):
    return wx(r).get('score_breakdown') or {}


def ji_of(r):
    return [str(j) for j in (r.get('ji_list') or [])]


def ss_map(r):
    return {s.get('name'): s.get('score')
            for s in (r.get('shensha_list') or []) if isinstance(s, dict)}


# ══════════════════ B3 按柱分级（事主类：开业）══════════════════
# B3-1 年三煞犯日柱：2024-01-09（癸卯年，三煞方申酉戌，日支? 日柱临方）
r = run(dt.date(2024, 1, 9), '开业', OWNER1)
_v, _jl = vetos(r), ji_of(r)
check('B3-1a 年三煞(日柱)不再否决', not _v, '; '.join(_v))
check('B3-1b 保留年三煞(日柱)忌项', '年三煞(日柱)' in _jl, str(_jl))
_sp = (r.get('sansha_info') or {}).get('sansha_penalty_detail') or []
check('B3-1c 日柱通道-30分保留（可用但带扣分）',
      any('年三煞(日柱)' in x and '-30' in x for x in _sp), str(_sp))
check('B3-1d he_ge=True（五行门槛放行）', wx(r).get('he_ge') is True)

# B3-2 年三煞犯时柱：2024-03-01（甲辰年三煞方巳午未，午时临方）
r = run(dt.date(2024, 3, 1), '开业', OWNER1)
_v, _jl = vetos(r), ji_of(r)
check('B3-2a 年三煞(时柱)不再否决', not _v, '; '.join(_v))
check('B3-2b 保留年三煞(时柱)/日三煞(时柱)忌项',
      '年三煞(时柱)' in _jl and '日三煞(时柱)' in _jl, str(_jl))
_sp = (r.get('sansha_info') or {}).get('sansha_penalty_detail') or []
check('B3-2c 时柱通道-20分保留',
      any('年三煞(时柱)' in x and '-20' in x for x in _sp), str(_sp))

# B3-3 反向：年三煞犯月柱事主类维持否决（2024-05-06 巳月，巳∈三煞方巳午未）
r = run(dt.date(2024, 5, 6), '开业', OWNER1)
_v = vetos(r)
check('B3-3 年三煞(月柱)事主类维持一票否决',
      any('三煞大忌' in v and '年三煞(月柱)' in v for v in _v), '; '.join(_v))

# B3-4 反向：坐山犯年三煞维持否决（2024 甲辰年三煞方巳午未，坐山未∈；
# 该样本经"年份不宜"通道提前否决，文案含"犯年三煞"）
r = run(dt.date(2024, 6, 8), '修造', None, shan=KUN)
_v = vetos(r)
check('B3-4 坐山犯年三煞维持否决（年份不宜/三煞大忌任一通道）',
      any('年三煞' in v for v in _v), '; '.join(_v))

# ══════════════════ 必修2 山向类/事主类日时柱口径对齐 ══════════════════
# 同一日 2024-03-01（年三煞时柱+月三煞日柱+日三煞时柱）：两类事项均不得
# 以日/时柱三煞否决；差异只允许出现在月柱/山向。
r_s = run(dt.date(2024, 3, 1), '开业', OWNER1)             # 事主中心
r_m = run(dt.date(2024, 3, 1), '修造', OWNER1, shan=KUN)   # 山向中心
vs, vm = vetos(r_s), vetos(r_m)
check('必修2-1a 事主类日/时柱三煞不否决',
      not any('三煞大忌' in v and ('日柱' in v or '时柱' in v) for v in vs), '; '.join(vs))
check('必修2-1b 山向类日/时柱三煞不否决',
      not any('三煞大忌' in v and ('日柱' in v or '时柱' in v) for v in vm), '; '.join(vm))
check('必修2-2 两类事项该日均检出年三煞(时柱)（同一判定事实）',
      '年三煞(时柱)' in ji_of(r_s) and '年三煞(时柱)' in ji_of(r_m),
      f"{ji_of(r_s)} | {ji_of(r_m)}")
check('必修2-3 事主类口径开关 sansha_pillar_veto=True',
      (r_s.get('sansha_info') or {}).get('sansha_pillar_veto') is True)
check('必修2-4 山向类口径开关 sansha_pillar_veto=False',
      (r_m.get('sansha_info') or {}).get('sansha_pillar_veto') is False)

# ══════════════════ D2 作灶次级神煞降级 + 防双扣 ══════════════════
# D2-1 天火日（规则 ji 与神煞通道同日命中）：2025-03-09
r = run(dt.date(2025, 3, 9), '作灶', OWNER1, shan=KUN)
_v, _jl, _ss, _bd = vetos(r), ji_of(r), ss_map(r), bd_of(r)
check('D2-1a 天火日不再否决', not _v, '; '.join(_v))
check('D2-1b 神煞通道天火日-15分在', _ss.get('天火日') == -15, str(_ss))
check('D2-1c 保留天火日忌作灶忌项文案', '天火日忌作灶' in _jl, str(_jl))
_n_ji = len(_bd.get('忌事明细', []))
check('D2-1d 防双扣：天火 ji 不重复忌事-15（5条明细仅-60=4×15）',
      _n_ji == 5 and _bd.get('忌事得分') == -60,
      f"明细{_n_ji}条 忌事得分={_bd.get('忌事得分')}")
check('D2-1e 假低分回退含天火神煞分（jiyu 列明）',
      '天火日（神煞-15分）' in (wx(r).get('ji_yu') or ''), wx(r).get('ji_yu'))

# D2-2 地火日规则/神煞公式分叉日：2024-01-02（规则 ji 命中、神煞未注册）
r = run(dt.date(2024, 1, 2), '作灶', OWNER1, shan=KUN)
_v, _jl, _ss, _bd = vetos(r), ji_of(r), ss_map(r), bd_of(r)
check('D2-2a 地火日不再否决', not _v, '; '.join(_v))
check('D2-2b 规则 ji 命中', '地火日忌作灶' in _jl, str(_jl))
check('D2-2c 当日神煞通道无地火（分叉实证）', '地火日' not in _ss, str(_ss))
check('D2-2d 分叉日走忌事-15强扣（忌事-45=3×15，地火必落一笔）',
      _bd.get('忌事得分') == -45, str(_bd.get('忌事得分')))

# D2-3 土府日神煞通道单扣：2024-01-14（神煞-20 命中、规则公式未命中）
r = run(dt.date(2024, 1, 14), '作灶', OWNER1, shan=KUN)
_v, _ss = vetos(r), ss_map(r)
check('D2-3a 土府日不再否决', not _v, '; '.join(_v))
check('D2-3b 神煞通道土府日-20分在', _ss.get('土府日') == -20, str(_ss))

# D2-4 灶君忌日降级（无神煞通道，忌事 -15）：2024-01-09
r = run(dt.date(2024, 1, 9), '作灶', OWNER1, shan=KUN)
_v, _jl = vetos(r), ji_of(r)
check('D2-4a 灶君忌日不再否决', not any('灶君忌日' in x for x in _v), '; '.join(_v))
check('D2-4b 保留灶君忌日忌作灶忌项', '灶君忌日忌作灶' in _jl, str(_jl))
# 当日降级忌项 4 条（年三煞日柱/日三煞时柱/日三煞山向/灶君忌日），回退 60 分；
# jiyu 仅列前 3 项+"等"，故以回退总额与忌项存在性证明灶君忌事 -15 已纳入回退
check('D2-4c 假低分回退含灶君忌事-15（4项共60分）',
      wx(r).get('score') == 26 and '扣分60分' in (wx(r).get('_he_ge_note') or '')
      and '（降级项=4）' in (wx(r).get('_he_ge_note') or ''),
      wx(r).get('_he_ge_note'))

# D2-5 反向：月破日维持否决（2024-01-08）
r = run(dt.date(2024, 1, 8), '作灶', OWNER1, shan=KUN)
_v = vetos(r)
check('D2-5 月破日作灶维持否决', any('月破' in x for x in _v), '; '.join(_v))

# D2-6 反向：灶君朝天维持否决（2024-02-06，同日天火同在不影响该否决）
r = run(dt.date(2024, 2, 6), '作灶', OWNER1, shan=KUN)
_v, _jl = vetos(r), ji_of(r)
check('D2-6a 灶君朝天维持否决', any('灶君朝天' in x for x in _v), '; '.join(_v))
check('D2-6b 同日天火 ji 仍记录但不改变否决构成', '天火日忌作灶' in _jl, str(_jl))

# ══════════════════ 必修1 真/假低分区分 ══════════════════
# M1 假低分放行：2024-01-03 修造（wx=9；月三煞时柱/山向 2 条降级忌事-30，
# 回退后 39≥30，无未制化硬煞）
r = run(dt.date(2024, 1, 3), '修造', OWNER1, shan=KUN)
_w = wx(r)
check('M1-1a 假低分放行 he_ge=True', _w.get('he_ge') is True)
check('M1-1b 无 veto', not vetos(r), '; '.join(vetos(r)))
check('M1-1c 回退30分（2条降级忌事）', '回退降级项' in (_w.get('_he_ge_note') or '')
      and '扣分30分' in (_w.get('_he_ge_note') or ''), _w.get('_he_ge_note'))

# M2 回退仅判定用：展示分保持原值不变
check('M2 假低分展示分不变（仍为9分）',
      _w.get('score') == 9 and '原得分9分' in (_w.get('ji_yu') or ''),
      f"score={_w.get('score')} jiyu={_w.get('ji_yu')}")

# M3 反向真低分：2024-01-01 修造（wx=-110；地支刑冲-50结构性低分，
# 仅回退降级忌事75后-35<30 → 维持否决）
r = run(dt.date(2024, 1, 1), '修造', OWNER1, shan=KUN)
_w = wx(r)
check('M3-1a 真低分维持 he_ge=False', _w.get('he_ge') is False)
check('M3-1b 真低分维持五行否决',
      any('五行严重不合格' in x for x in vetos(r)), '; '.join(vetos(r)))
check('M3-1c 未写假低分放宽 note', _w.get('_he_ge_note') is None)

# M4 反向：伴随未制化硬煞（坐山年三煞）时即便回退≥30 也不豁免
r = run(dt.date(2024, 6, 8), '修造', None, shan=KUN)
check('M4 硬煞伴随不触发假低分豁免（无放宽note且有否决）',
      wx(r).get('_he_ge_note') is None and bool(vetos(r)),
      f"note={wx(r).get('_he_ge_note')} veto={vetos(r)}")

# M5 月份不宜传导分回退（动态扫描，§63 正阴府/月破降级项参与假低分判定）
_m5 = None
_d = dt.date(2024, 1, 1)
_end = dt.date(2027, 12, 31)
while _d <= _end:
    _r = run(_d, '修造', None, shan=KUN)
    _w = _r.get('wu_xing_result') or {}
    if (_w.get('he_ge') is True and _w.get('score', 0) < 30
            and '月份不宜' in (_w.get('ji_yu') or '')):
        _m5 = (_d, _w)
        break
    _d += dt.timedelta(days=1)
check('M5-1 前置：找到月份不宜扣分参与回退的假低分日', _m5 is not None)
if _m5:
    _d, _w = _m5
    check('M5-2 月份不宜回退日 he_ge=True 且原展示分<30',
          _w.get('he_ge') is True and _w.get('score') < 30,
          f"{_d} score={_w.get('score')} jiyu={_w.get('ji_yu')}")

# ══════════════════ 防双扣数值闭合 ══════════════════
# F1 D2-1 日 breakdown 数值键加总 == 五行分（天火只扣神煞一笔）
r = run(dt.date(2025, 3, 9), '作灶', OWNER1, shan=KUN)
_bd = bd_of(r)
_s = sum(v for k, v in _bd.items()
         if isinstance(v, (int, float)) and k not in ('忌事明细', '相主得分'))
check('F1 天火日 breakdown 加总==五行分（神煞/忌事各一笔不重）',
      _s == wx(r).get('score'), f'加总={_s} 五行分={wx(r).get("score")}')

# F2 B3 通道分与忌事分两笔独立：2024-01-09 开业（通道-40、忌事-30）
r = run(dt.date(2024, 1, 9), '开业', OWNER1)
_si = (r.get('sansha_info') or {}).get('sansha_info') or (r.get('sansha_info') or {})
check('F2-1 三煞通道合计-40（日柱-30+时柱-10，保留入总分）',
      (r.get('sansha_info') or {}).get('sansha_penalty') == -40,
      str((r.get('sansha_info') or {}).get('sansha_penalty')))
check('F2-2 忌事通道独立-30（2条三煞忌项）',
      bd_of(r).get('忌事得分') == -30, str(bd_of(r).get('忌事得分')))

print()
if FAILS:
    print(f'FAILED {len(FAILS)}: ' + '; '.join(FAILS))
    sys.exit(1)
print('ALL PASS')
sys.exit(0)
