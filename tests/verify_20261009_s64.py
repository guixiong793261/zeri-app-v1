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

§68（2026-10-12）：①基建——sys.path 改相对定位（Path(__file__).parents[1]），
worktree 跨版本对拍自此可信；②D2-4c 断言按 §66 后口径更新（§66 归零使
score 26→51 跨 30 分线、回退分支切换为 60 分线制化放宽，行为殊途同归）。

§172（2026-10-24 P0 大清理·测试重冻）：岁害/天耗/地耗删除＋年家族 16 项
置 0＋年支孤辰寡宿删除＋大小耗伪链清除，作灶/修造全年抬分 +7391，多日本批
抬分后跨 30 分线/60 分线，分支形态重锚（样例日均经重扫/实测锁定）：
- D2-1e 2025-03-09：score <30→59，假低分回退分支切换为 60 分线制化放宽
  （同 D2-4c §68 先例，行为殊途同归：均放行、无 veto）；
- D2-4c 2024-01-09：锚 51（§68 冻结，改前实测已漂移）→实测 113，
  直升「五行吉日」，无任何放宽分支；
- D2-4d 2025-09-20 主样例：锚 -21→实测 1，仍走假低分回退（回退75分→76），
  组合覆盖仍有效；
- D2-4e 2025-10-02 备样例：锚 10→实测 52，跨 30 分线改走 60 分线制化放宽；
  重扫 tools/audit/s68_stage2_probe/zuozao_below30_probe.py 确认 1096 日内
  veto=0 且 he_ge=True 的含灶君假低分日仅余 2025-09-20 一日，备样例无替代，
  重锚为该日新形态留痕（组合覆盖由 D2-4d 独扛）；
- M1/M2 2024-01-03 修造：score 9→61 跨 60 分线，假低分样例失效；换锚
  2024-01-04（五行=23、月三煞时柱/山向 2 条降级忌事-30、回退后 53≥30），
  降级项构成与原样例全等，M1-1c/M2 断言语义不变。

样本均为 12:00（午时）真实排盘 + Scorer.score 真实入口评分得出。
退出码：全过 0，有失败 1。
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # §68 基建：相对定位，worktree 对拍可用
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


# ══════════════════ B3 按柱分级（事主类：签约）══════════════════
# 001 §211（2026-10-31 三煞四柱级全面旁路·案B）：年三煞柱级通道（月柱-30/
# 日柱-30/时柱-20）已删除，判定层不再置 flag；本组改锚为「反向留痕」——
# 断言年三煞柱级条目不再出现、且保留的月三煞/日三煞柱级通道不受影响。
# B3-1 原「年三煞犯日柱」样例：2024-01-09（癸卯年，三煞方申酉戌）
r = run(dt.date(2024, 1, 9), '签约', OWNER1)
_v, _jl = vetos(r), ji_of(r)
check('B3-1a 年三煞(日柱)不再否决', not _v, '; '.join(_v))
check('B3-1b §211 年三煞(日柱)忌项已随柱级通道删除、无任何年三煞柱级条目',
      '年三煞(日柱)' not in _jl and '年三煞(时柱)' not in _jl
      and '年三煞(月柱)' not in _jl, str(_jl))
_sp = (r.get('sansha_info') or {}).get('sansha_penalty_detail') or []
check('B3-1c §211 保留日三煞(时柱)通道-10分（非年三煞）',
      any('日三煞(时柱)' in x and '-10' in x for x in _sp)
      and not any('年三煞(' in x for x in _sp), str(_sp))
check('B3-1d he_ge=True（五行门槛放行）', wx(r).get('he_ge') is True)

# B3-2 年三煞犯时柱样例：2024-03-01（甲辰年三煞方巳午未，午时临方）
r = run(dt.date(2024, 3, 1), '签约', OWNER1)
_v, _jl = vetos(r), ji_of(r)
check('B3-2a 年三煞(时柱)不再否决', not _v, '; '.join(_v))
check('B3-2b §211 年三煞(时柱)已删、月三煞(日柱)/日三煞(时柱)保留',
      '年三煞(时柱)' not in _jl and '月三煞(日柱)' in _jl
      and '日三煞(时柱)' in _jl, str(_jl))
_sp = (r.get('sansha_info') or {}).get('sansha_penalty_detail') or []
check('B3-2c §211 保留柱级通道合计-30（月三煞日柱-20+日三煞时柱-10）',
      any('月三煞(日柱)' in x and '-20' in x for x in _sp)
      and any('日三煞(时柱)' in x and '-10' in x for x in _sp)
      and not any('年三煞(' in x for x in _sp), str(_sp))

# B3-3 原「反向：年三煞犯月柱事主类维持否决」→ §211 案B 整体旁路，改反向留痕
# 2024-05-06（巳月，巳∈三煞方巳午未）
r = run(dt.date(2024, 5, 6), '签约', OWNER1)
_v, _jl = vetos(r), ji_of(r)
check('B3-3 §211 年三煞(月柱)已旁路：无否决、无年三煞忌项、通道0',
      not _v and '年三煞(月柱)' not in _jl
      and (r.get('sansha_info') or {}).get('sansha_penalty') == 0,
      f"veto={'; '.join(_v)} ji={_jl} "
      f"penalty={(r.get('sansha_info') or {}).get('sansha_penalty')}")

# B3-4 反向：坐山犯年三煞维持否决（2024 甲辰年三煞方巳午未，坐山未∈；
# 该样本经"年份不宜"通道提前否决，文案含"犯年三煞"）
r = run(dt.date(2024, 6, 8), '修造', None, shan=KUN)
_v = vetos(r)
check('B3-4 坐山犯年三煞维持否决（年份不宜/三煞大忌任一通道）',
      any('年三煞' in v for v in _v), '; '.join(_v))

# ══════════════════ 必修2 山向类/事主类日时柱口径对齐 ══════════════════
# 同一日 2024-03-01（年三煞时柱+月三煞日柱+日三煞时柱）：两类事项均不得
# 以日/时柱三煞否决；差异只允许出现在月柱/山向。
r_s = run(dt.date(2024, 3, 1), '签约', OWNER1)             # 事主中心
r_m = run(dt.date(2024, 3, 1), '修造', OWNER1, shan=KUN)   # 山向中心
vs, vm = vetos(r_s), vetos(r_m)
check('必修2-1a 事主类日/时柱三煞不否决',
      not any('三煞大忌' in v and ('日柱' in v or '时柱' in v) for v in vs), '; '.join(vs))
check('必修2-1b 山向类日/时柱三煞不否决',
      not any('三煞大忌' in v and ('日柱' in v or '时柱' in v) for v in vm), '; '.join(vm))
check('必修2-2 §211 两类事项均不再检出年三煞柱级条目（同一判定事实：柱级已旁路）',
      all(not any(x in j for x in ('年三煞(月柱)', '年三煞(日柱)', '年三煞(时柱)'))
          for j in (ji_of(r_s), ji_of(r_m)))
      and '年三煞(山向)' in ji_of(r_m),
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
# §185（2026-10-26 向方禁忌批）：明细 5→7 条——乙巳年煞东+丑日煞东，艮宫借
# 丑寅两支并判，寅∈东煞 → 年三煞(向方)+日三煞(向方) 入明细；向方项走专属
# 通道不重复忌事-15（防双扣排除生效），忌事得分仍 -60=4×15
# §187 Q4（2026-10-27 修造深水区批）：三煞双扣根除——年三煞(月柱)/年三煞(向方)/
# 日三煞(向方)/月灾煞/正阴府 5 项均已由 sansha_penalty 通道计分（合计-90），
# 忌事循环排除后仅「天火日忌作灶」计一笔 -15（年柱巳冲属 H1 锚点仅展示）。
# 明细条数仍 7，双扣杜绝语义由「通道-90 + 忌事-15」两笔独立证明。
# §211（2026-10-31 三煞柱级旁路）：原 7 条明细含 年三煞(月柱)（已删）→ 6 条。
check('D2-1d 防双扣：三煞/正阴府归通道不重复忌事（6条明细，忌事仅天火一笔-15）',
      _n_ji == 6 and _bd.get('忌事得分') == -15,
      f"明细{_n_ji}条 忌事得分={_bd.get('忌事得分')}")
# D2-1e §172（2026-10-24）重锚：本批抬分后 score <30→59 跨 30 分线，
# 假低分回退分支切换为 60 分线制化放宽（同 D2-4c §68 先例，行为殊途同归：
# 均放行 he_ge=True、无 veto）。天火神煞分 -15 的在册与防双扣由 D2-1b/d 保持。
# §187 Q4（2026-10-27）：三煞双扣根除后 wx 59→104，跨 60 分线直升五行大吉
# （note=None）；60 分线制化放宽分支覆盖改由 M1（2024-01-04）独扛。
check('D2-1e §187 Q4 后直升五行吉日（score104/note=None）',
      wx(r).get('score') == 104 and wx(r).get('_he_ge_note') is None
      and wx(r).get('he_ge') is True,
      f"score={wx(r).get('score')} note={wx(r).get('_he_ge_note')}")

# D2-2 地火日规则/神煞公式分叉日：2024-01-02（规则 ji 命中、神煞未注册）
r = run(dt.date(2024, 1, 2), '作灶', OWNER1, shan=KUN)
_v, _jl, _ss, _bd = vetos(r), ji_of(r), ss_map(r), bd_of(r)
check('D2-2a 地火日不再否决', not _v, '; '.join(_v))
check('D2-2b 规则 ji 命中', '地火日忌作灶' in _jl, str(_jl))
check('D2-2c 当日神煞通道无地火（分叉实证）', '地火日' not in _ss, str(_ss))
check('D2-2d §187 Q4 分叉日忌事仅地火一笔-15（三煞3项归通道-50）',
      _bd.get('忌事得分') == -15 and '地火日忌作灶' in _bd.get('忌事明细', []),
      f"忌事={_bd.get('忌事得分')} 明细={_bd.get('忌事明细')}")

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
# D2-4c §68（2026-10-12）断言更新：§66 三煞归零后本日 wx.score 26→51（+25 恰为
# 劫煞分差），跨过 30 分放宽线，必修1 假低分回退分支改走 60 分线制化放宽分支
# （行为殊途同归：均放行 he_ge=True、无 veto，仅 note 文案与展示分不同）。
# 灶君忌事-15 仍落忌事明细 4 条（防双扣语义由 D2-1d 保持）；"回退分支+灶君"
# 组合覆盖已由 D2-4d/e 补齐（§69 验收拍板A 2026-10-12）。
# D2-4c §172（2026-10-24）重锚：锚 51（§68 冻结，改前实测已漂移）→实测 113，
# 本批抬分后直升「五行吉日」，不再走任何放宽分支（note=None）。灶君忌事 -15
# 仍落忌事明细 4 条（防双扣语义由 D2-1d 保持）；"回退分支+灶君"组合覆盖由
# D2-4d 独扛（D2-4e 备样例已跨线，重扫确认无替代日）。
# §187 Q4（2026-10-27）：三煞双扣根除后本日 wx 113→158（Δ45=3×15），
# 仍直升「五行大吉」、不走任何放宽分支（note=None）。
check('D2-4c 直升五行吉日（§187 Q4：score158/note=None）',
      wx(r).get('score') == 158 and wx(r).get('_he_ge_note') is None
      and wx(r).get('he_ge') is True,
      f"score={wx(r).get('score')} note={wx(r).get('_he_ge_note')}")

# D2-4d/e §68 阶段2 组合覆盖（§69 验收拍板A 2026-10-12）："必修1 假低分
# 回退分支+灶君"双样例。探测 1096 日（2024-01-01~2026-12-31，s64 同口径
# 作灶×坤山艮向兼未）：五行<30 且忌事含灶君共 143 日，其中 141 日被
# veto 噪声淹没（总分0/he_ge=False，无法承载组合断言），veto=0 且
# he_ge=True（回退分支实际生效）仅 2 日：
#   主样例 2025-09-20（五行=-21，负分边界——直击"扣到负值仍走回退"极限）
#   备样例 2025-10-02（五行=10，正分普通场景；主样例因规则演进失效时顶上）
# 注意：两样例绑定 §66 后规则版本——§65/§66/必修1 逻辑变化时分数漂移
# 即 FAIL（下方各条 detail 均拼重扫提示，仅 FAIL 时打印，零 PASS 噪声）。
# 重扫工具：tools/audit/s68_stage2_probe/zuozao_below30_probe.py
# 操作路径：规则变化 → 重跑该工具 → 样例失效则更新 D2-4d/e 样例日与分数锚定。
_RESCAN = '；样例绑定§66后规则版本，漂移请重跑 tools/audit/s68_stage2_probe/zuozao_below30_probe.py 重扫'
# §187 Q4（2026-10-27）重锚留痕：三煞双扣根除后作灶全年抬分，2025-09-20 五行
# 1→76、2025-10-02 五行 52→112，均跨 60 分线直升吉日（note=None）。重扫
# 2024-01-01~2026-12-31 同口径确认：五行<30 且忌事含灶君且「回退降级项」分支
# 生效日 = 0（Q4 前唯一 2 日已全部抬出），"假低分回退分支+灶君"组合覆盖在本
# 语料内已无替代样本——该分支覆盖改由 M5 动态扫描（修造口径）与 M1（60分线
# 制化放宽）承接，本组 D2-4d/e 重锚为「直升吉日+灶君忌项保留」形态留痕。
r = run(dt.date(2025, 9, 20), '作灶', OWNER1, shan=KUN)
_w = wx(r)
# §187 Q4 重锚：1→76（五行平平，直升），灶君忌项与无 veto 语义保持。
check('D2-4d 主样例五行76（§187 Q4：1→76 直升五行平平）', _w.get('score') == 76,
      f'五行={_w.get("score")}{_RESCAN}')
check('D2-4d 主样例直升吉日 he_ge=True', _w.get('he_ge') is True,
      f'he_ge={_w.get("he_ge")}{_RESCAN}')
check('D2-4d 主样例保留灶君忌日忌作灶忌项', '灶君忌日忌作灶' in ji_of(r),
      f'{ji_of(r)}{_RESCAN}')
check('D2-4d 主样例无 veto', not vetos(r), f'{"; ".join(vetos(r))}{_RESCAN}')
r = run(dt.date(2025, 10, 2), '作灶', OWNER1, shan=KUN)
_w = wx(r)
# §187 Q4 重锚：52→112（五行吉日，直升）。
check('D2-4e 备样例五行112（§187 Q4：52→112 直升五行吉日）',
      _w.get('score') == 112 and _w.get('_he_ge_note') is None,
      f'五行={_w.get("score")} note={_w.get("_he_ge_note")}{_RESCAN}')
check('D2-4e 备样例直升吉日放行 he_ge=True', _w.get('he_ge') is True,
      f'he_ge={_w.get("he_ge")}{_RESCAN}')
check('D2-4e 备样例保留灶君忌日忌作灶忌项', '灶君忌日忌作灶' in ji_of(r),
      f'{ji_of(r)}{_RESCAN}')
check('D2-4e 备样例无 veto', not vetos(r), f'{"; ".join(vetos(r))}{_RESCAN}')

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
# M1 假低分放行：§172（2026-10-24）换锚 2024-01-04 修造（原样例 2024-01-03
# 本批抬分后 score 9→61 跨 60 分线失效）。新样例经 2024~2026 全量重扫锁定：
# wx=23；月三煞时柱/山向 2 条降级忌事-30（构成与原样例全等），回退后 53≥30，
# 无未制化硬煞。
# §187 Q4（2026-10-27）：三煞双扣根除后 wx 23→48，30 分线回退分支不再适用，
# 改走 60 分线制化放宽（原得分48/未制化项=8），行为同型：放行 he_ge=True、无 veto。
# §189 P2（2026-10-27 拍板·方案A）：年运表否定句移出忌项（-15/条 → 0），
# 修造基线整体 +30，2024-01-04 由 48→78 跨过 60 分线、该分支失效；按 2024-2027
# 全量重扫（87 个放宽日）重锚 2024-01-02：走同一 60 分线制化放宽分支，
# 原得分50/未制化项=5，放行 he_ge=True、无 veto、展示分为原值。
r = run(dt.date(2024, 1, 2), '修造', OWNER1, shan=KUN)
_w = wx(r)
check('M1-1a 假低分放行 he_ge=True', _w.get('he_ge') is True)
check('M1-1b 无 veto', not vetos(r), '; '.join(vetos(r)))
check('M1-1c §189 后走60分线制化放宽（原得分50/未制化项=5）',
      '放宽合格：原得分50未达60分' in (_w.get('_he_ge_note') or '')
      and '（未制化项=5）' in (_w.get('_he_ge_note') or ''), _w.get('_he_ge_note'))

# M2 回退仅判定用：展示分保持原值不变
check('M2 假低分展示分不变（§189：仍为50分）',
      _w.get('score') == 50 and '原得分50' in (_w.get('ji_yu') or ''),
      f"score={_w.get('score')} jiyu={_w.get('ji_yu')}")

# M3 反向真低分：2024-01-14 修造（§187 Q4 重锚：原 2024-01-01 三煞双扣根除后
# wx -13、回退75→62 达线转为假低分；重扫 2024-2030 取现行真低分日 2024-01-14
# wx=-40，降级项回退后仍 <30 → 维持否决；断言不含具体分数，仅锁分支形态）
r = run(dt.date(2024, 1, 14), '修造', OWNER1, shan=KUN)
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

# F2 B3 通道分与忌事分两笔独立：2024-01-09 签约（通道、忌事各自独立）
# §187 Q4（2026-10-27）：三煞双扣根除后忌事得分 -30→0——年三煞(日柱)/日三煞(时柱)
# 两项已由 sansha_penalty 通道扣 -40（-30/-10），忌事不再重复；两笔独立语义
# 由「通道-40 + 忌事0 + 明细仍保留 2 条三煞项（仅展示）」共同证明。
# §211（2026-10-31 三煞柱级旁路·案B）：年三煞(日柱) -30 已删，通道仅余
# 日三煞(时柱) -10；明细同步 2→1 条。两笔独立语义由「通道-10 + 忌事0 +
# 明细 1 条（仅展示）」继续证明。
r = run(dt.date(2024, 1, 9), '签约', OWNER1)
_si = (r.get('sansha_info') or {}).get('sansha_info') or (r.get('sansha_info') or {})
check('F2-1 §211 三煞通道合计-10（仅日三煞时柱，年三煞日柱-30已删）',
      (r.get('sansha_info') or {}).get('sansha_penalty') == -10,
      str((r.get('sansha_info') or {}).get('sansha_penalty')))
check('F2-2 §211 忌事通道零重复（1条三煞项归通道，忌事得分=0）',
      bd_of(r).get('忌事得分') == 0
      and len(bd_of(r).get('忌事明细') or []) == 1,
      f"忌事={bd_of(r).get('忌事得分')} 明细={bd_of(r).get('忌事明细')}")

print()
if FAILS:
    print(f'FAILED {len(FAILS)}: ' + '; '.join(FAILS))
    sys.exit(1)
print('ALL PASS')
sys.exit(0)

