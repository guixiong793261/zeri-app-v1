# -*- coding: utf-8 -*-
"""H1 verify + 全量回归 v2（2026-10-01，多进程）。

真实 Scorer.score() 入口，2024-01-01~2026-12-31（1096 天）× 11 事项。

口径（v2 运行时核实修正）：
  · 10 个通用事项（修造/动土/拆舍/入宅/作灶/开业/出行/安葬/安床/签约）：
    规则 yi/ji 在 _build_wu_xing_breakdown 内 +10/-15，锚点日双扣真实存在 →
    B 每日数值对账（无溢出）；D 非veto日 old/new 总分与等级硬对账。
  · 嫁娶：score() 走婚嫁专用链（总分=marriage评分+月令+喜用+太阳太阴，
    L843），规则 yi/ji 仅展示、从不计分（score_breakdown 被置 {}）。
    故嫁娶 9 锚点为"展示锚点"：B' 结构断言 score_breakdown={}，
    等级=score纯函数一致；无分可停、H1 对嫁娶总分为零影响。

断言汇总：
  A. 结构：恰11键；映射族46。
     （2026-10-19 十恶大败批 -1（安葬族）、2026-10-20 岁破批 -4：动土/拆舍/
      入宅/签约四事项「岁破」锚点族随岁破日课普适忌删除而移除）。原「veto族3」
      随 _h1_is_veto_reason 一并删除（001 §140，岁破日 veto 文案不再产生）。
  B/B'. 每日对账（通用：数值；嫁娶：结构）。
  C. 62 个 tx 串（出行12串逐串）锚点同日共存全部至少1次。
  D. 通用非veto日：old=new+10停宜-15停忌；枚举真实等级跨档。
  E. 停分文本全集 ⊆ 表内62 tx；单边样本从未停。
退出码 0/1，打印 FAIL 计数。
"""
import sys, io, os, datetime
from collections import Counter

# 仓库根＝本脚本所在 tests/ 的上一层（两仓通用，避免硬编码路径）
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

EVENTS = ['嫁娶', '修造', '动土', '拆舍', '入宅', '作灶', '开业', '出行', '安葬', '安床', '签约']
D0, D1 = datetime.date(2024, 1, 1), datetime.date(2026, 12, 31)
# SIDE_SAMPLES 原 {'修造': '岁破日忌修造'}——『岁破日忌修造』随岁破批（001 §140）
# 删除后不再产生（该文本本非修造 H1 映射族成员，留之即「悬空样本」）。今取
# 修造忌项中非锚点的单边样本『时冲山』替换，不留悬空（2026-10-20 用户拍板
# 「锚点不存在」或「替换为新锚点」→取替换）。
SIDE_SAMPLES = {'动土': '建除闭日忌动土', '修造': '时冲山'}
# VETO_EVS 原 ['动土','拆舍','入宅']——其「岁破日 veto 理由族」随岁破批
# （2026-10-20，001 §140）删除 _h1_is_veto_reason 而消失，清空（不再断言）。
VETO_EVS = []


def _worker(task):
    """单 (事项, 日期ordinal区间) 扫描。返回可 pickle 的 dict。"""
    import sys
    sys.stdout = open(os.devnull, 'w')
    from modules.四柱计算器 import calculate_sizhu
    from modules.评分器 import Scorer, H1_ANCHOR_MAP
    from modules.事项标准 import canonical_event, event_profile

    ev, o0, o1 = task
    fails, fired, level_changes, stopped = [], Counter(), [], set()
    po_yi_n = po_ji_n = 0
    n_cells = 0
    is_marriage = event_profile(ev)['marriage']

    od = o0
    while od <= o1:
        d = datetime.date.fromordinal(od)
        sz = calculate_sizhu(d, 12)
        scorer = Scorer()
        r = scorer.score(sz, ev, owners=[],
                         shan_xiang='子山午向' if ev == '修造' else None)
        wx = r.get('wu_xing_result') or {}
        bd = wx.get('score_breakdown')
        yi = r.get('yi_list') or []
        ji = r.get('ji_list') or []
        ss_names = {s.get('name') for s in (r.get('shensha_list') or [])
                    if isinstance(s, dict)}
        cev = canonical_event(ev)

        def is_stopped(text):
            for ss_n, tx in H1_ANCHOR_MAP.get(cev, []):
                if text == tx and ss_n in ss_names:
                    return True
            return False

        po_yi = [t for t in yi if is_stopped(t)]
        po_ji = [t for t in ji if is_stopped(t)]
        po_yi_n += len(po_yi); po_ji_n += len(po_ji)
        stopped.update(po_yi + po_ji)

        for ss_n, tx in H1_ANCHOR_MAP.get(cev, []):
            if ss_n in ss_names:
                for t in yi + ji:
                    if t == tx:
                        fired[(ev, ss_n, tx)] += 1
        # veto理由族计数已删（岁破批 001 §140：_h1_is_veto_reason 及其 3 族取消）

        if ev in SIDE_SAMPLES:
            txt = SIDE_SAMPLES[ev]
            if txt in (yi + ji) and txt in (po_yi + po_ji):
                fails.append(f"E: {d} {ev} 单边样本被误停: {txt}")

        if is_marriage:
            # B'：规则文本不进嫁娶总分（score_breakdown 必须为 {}）
            if bd != {}:
                fails.append(f"B': {d} {ev} score_breakdown应为空dict, 实际={bd}")
            # 等级=总分纯函数一致（须纳入"忌嫁娶封顶"设计：封顶日基础级≤★平
            # 且必带后缀；未封顶日等级==纯函数等级）
            if r.get('score', 0) > 0:
                raw_lvl = r.get('level', '') or ''
                capped = raw_lvl.endswith('（犯忌嫁娶，慎用）')
                base_lvl = raw_lvl.replace('（犯忌嫁娶，慎用）', '')
                mrg_details = r.get('marriage_details') or []
                has_ji = any(
                    '忌嫁娶' in str(_d[0])
                    for _d in mrg_details
                    if isinstance(_d, (list, tuple)) and len(_d) >= 1)
                if has_ji:
                    # 封顶：基础级不高于★平（总分本就<60时为❌凶，否则★平），必带后缀
                    if not capped or base_lvl not in ('❌ 凶', '★ 平'):
                        fails.append(
                            f"B': {d} {ev} 忌嫁娶应封顶(≤★平)带后缀, 实际={raw_lvl}")
                else:
                    chk_lvl = scorer._get_level(r['score'], wx, r.get('huangdao_info'))
                    if base_lvl != chk_lvl:
                        fails.append(
                            f"B': {d} {ev} 等级非总分纯函数: {base_lvl} vs {chk_lvl}")
        else:
            exp_yi = 10 * (len(yi) - len(po_yi))
            exp_ji = -15 * (len(ji) - len(po_ji))
            if bd.get('宜事得分') != exp_yi:
                fails.append(f"B: {d} {ev} 宜事分={bd.get('宜事得分')} 期望={exp_yi} yi={yi}")
            if bd.get('忌事得分') != exp_ji:
                fails.append(f"B: {d} {ev} 忌事分={bd.get('忌事得分')} 期望={exp_ji} ji={ji}")
            # D：非veto日总分/等级硬对账
            if r.get('score', 0) > 0:
                delta = 10 * len(po_yi) - 15 * len(po_ji)
                old_total = r['score'] + delta
                old_wx = dict(wx)
                if isinstance(old_wx.get('score'), (int, float)):
                    old_wx['score'] = old_wx['score'] + delta
                old_lvl = scorer._get_level(old_total, old_wx, r.get('huangdao_info'))
                if old_lvl != r.get('level'):
                    level_changes.append((str(d), ev, old_total, r['score'],
                                          old_lvl, r.get('level')))
        n_cells += 1
        od += 1

    return {
        'ev': ev, 'fails': fails,
        'fired': {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in fired.items()},
        'stopped': list(stopped),
        'level_changes': level_changes,
        'po_yi': po_yi_n, 'po_ji': po_ji_n, 'cells': n_cells,
    }


def main():
    import multiprocessing as mp
    from modules.评分器 import H1_ANCHOR_MAP
    from modules.事项标准 import canonical_event

    fails = []

    # ---------- A. 结构 ----------
    if set(H1_ANCHOR_MAP.keys()) != set(EVENTS):
        fails.append(f"A: 映射表键 != 11事项: {sorted(H1_ANCHOR_MAP.keys())}")
    map_families, all_tx = set(), set()
    tx_by_family = {}
    for ev in EVENTS:
        for ss_name, tx in H1_ANCHOR_MAP[ev]:
            map_families.add((ev, ss_name))
            all_tx.add(tx)
            tx_by_family.setdefault((ev, ss_name), []).append(tx)
    if len(map_families) != 46:
        fails.append(f"A: 映射族数={len(map_families)}（应46）")

    # ---------- 任务分片（按 季度×事项） ----------
    tasks = []
    od = D0.toordinal()
    ends = []
    while od <= D1.toordinal():
        end = min(od + 90, D1.toordinal())
        ends.append((od, end))
        od = end + 1
    for ev in EVENTS:
        for a, b in ends:
            tasks.append((ev, a, b))

    nworkers = min(8, os.cpu_count() or 2)
    t0 = datetime.datetime.now()
    with mp.Pool(processes=nworkers) as pool:
        results = pool.map(_worker, tasks)
    elapsed = (datetime.datetime.now() - t0).total_seconds()

    # ---------- 汇总 ----------
    fired = Counter()
    stopped_all = set()
    level_changes_all = []
    sum_po_yi = sum_po_ji = n_cells = 0
    for res in results:
        fails.extend(res['fails'])
        for k, v in res['fired'].items():
            fired[k] += v
        stopped_all.update(res['stopped'])
        level_changes_all.extend(res['level_changes'])
        sum_po_yi += res['po_yi']; sum_po_ji += res['po_ji']
        n_cells += res['cells']

    # ---------- C. 锚点全命中 ----------
    for (ev, ss_n), txs in tx_by_family.items():
        for tx in txs:   # 出行12串逐串
            if fired.get(f"{ev}|{ss_n}|{tx}", 0) < 1:
                fails.append(f"C: 锚点无同日共存: {ev} | {ss_n} | {tx}")
    # veto理由族命中断言已删（岁破批 001 §140：_h1_is_veto_reason 及 3 族取消）

    # ---------- E. 停分文本全集 ----------
    for t in stopped_all:
        if t not in all_tx:
            fails.append(f"E: 表外文本被停分: {t}")

    # ---------- 报告 ----------
    level_changes_all.sort()
    real_lvl = [x for x in level_changes_all]
    print("=" * 64)
    print(f"单元格={n_cells}（1096天×11事项）  耗时={elapsed:.0f}s  进程={nworkers}")
    print(f"映射族={len(map_families)}；tx串={len(all_tx)}")
    print(f"通用链停分事件: 宜 {sum_po_yi} 条 / 忌 {sum_po_ji} 条（嫁娶规则本就不计分，不含在内）")
    print(f"锚点共存命中: tx串 {sum(1 for k in fired)} / {len(all_tx)}")
    print(f"通用事项真实等级跨档日: {len(real_lvl)}")
    for row in real_lvl[:60]:
        print("   ", row)
    if len(real_lvl) > 60:
        print(f"    ... 其余 {len(real_lvl)-60} 条略")
    print("=" * 64)
    if fails:
        print(f"FAIL 计数={len(fails)}")
        for m in fails[:60]:
            print("  [FAIL]", m)
        sys.exit(1)
    print("PASS：结构46 + 每日对账一致(无溢出) + 锚点全命中 + 单边未停 + 嫁娶零影响")
    sys.exit(0)


if __name__ == '__main__':
    main()
