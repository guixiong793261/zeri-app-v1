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
  A. 结构：恰11键；映射族45。
     （2026-10-19 十恶大败批 -1（安葬族）、2026-10-20 岁破批 -4：动土/拆舍/
      入宅/签约四事项「岁破」锚点族随岁破日课普适忌删除而移除；2026-10-20
      H1-3 批 -1：入宅「月破」锚点族随规则层发射删除而移除）。原「veto族3」
      随 _h1_is_veto_reason 一并删除（001 §140，岁破日 veto 文案不再产生）。
  B/B'. 每日对账（通用：数值；嫁娶：结构）。
  C. 56 个 tx 串（出行12串逐串）锚点同日共存全部至少1次。
  D. 通用非veto日：old=new+10停宜-15停忌；枚举真实等级跨档。
  E. 停分文本全集 ⊆ 表内56 tx；单边样本从未停；入宅月破清零（H1-3）。
  F. 映射族发射源守卫（H1-4）：每 tx 在 modules 源码有字面量命中
     （剔除 H1_ANCHOR_MAP 定义块自身）或命中登记的动态发射模式，
     改名/删发射即时报 FAIL，防 647 式批量腐烂。
  G. H1_ANCHOR_MAP 双向对账（H1-5）：测试侧独立硬编码清单 ⟷ 生产
     常量双向等式，多余族/错族/缺族/tx 漂移即时报 FAIL。
退出码 0/1，打印 FAIL 计数。
"""
import sys, io, os, re, datetime
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

# H1-5（2026-10-20 拍板⑤）：H1_ANCHOR_MAP 独立清单双向对账。
# 该常量由生产代码提供，运行期断言（A/C 段）无法发现"多余族/错族"——
# 批量改名或重构可致表与发射"两边一致地错"。本清单在测试侧硬编码
# 冻结 45 族全量（与 2026-10-20 H1-3 后生产一致），双向等式对账，
# 任何漂移即时报 FAIL，迫使用户显式评审改表动作。
# 注：入宅族 tx『不将日宜修造』为历史既成串（非笔误修正对象），
# 按原样冻结；变更须先改本清单再改生产，顺序不可反。
EXPECT_H1_FAMILIES = {
    '嫁娶': [
        ('不将日', '不将日'), ('月德', '月德日'), ('黄沙', '黄沙日'),
        ('月破', '月破日'), ('杨公忌日', '杨公忌'), ('神号', '神号日'),
        ('天德', '天德日'), ('鬼哭', '鬼哭日'), ('红砂日', '红纱日'),
    ],
    '修造': [
        ('建除十二神-建', '建除建日忌修造'), ('建除十二神-除', '建除除日宜修造'),
        ('建除十二神-满', '建除满日忌修造'), ('建除十二神-平', '建除平日忌修造'),
        ('建除十二神-定', '建除定日宜修造'), ('建除十二神-执', '建除执日宜修造'),
        ('建除十二神-破', '建除破日忌修造'), ('建除十二神-危', '建除危日宜修造'),
        ('建除十二神-成', '建除成日宜修造'), ('建除十二神-收', '建除收日忌修造'),
        ('建除十二神-开', '建除开日宜修造'), ('建除十二神-闭', '建除闭日忌修造'),
        ('月破', '月破日忌修造'),
    ],
    '动土': [('月破', '月破日忌动土')],
    '拆舍': [('月破', '月破日忌拆舍')],
    '入宅': [('不将日', '不将日宜修造')],
    '作灶': [
        ('不将日', '不将日宜作灶'), ('丙丁日', '丙丁日火旺宜作灶'),
        ('天火日', '天火日忌作灶'), ('灶君朝天', '灶君朝天日忌作灶'),
        ('月破', '月破日忌作灶'),
    ],
    '开业': [
        ('不将日', '不将日宜开业'), ('月破', '月破日忌开业'),
        ('破日', '建除破日忌开业'),
    ],
    '出行': [
        ('月破', '月破日(子月午日)忌出行'), ('月破', '月破日(丑月未日)忌出行'),
        ('月破', '月破日(寅月申日)忌出行'), ('月破', '月破日(卯月酉日)忌出行'),
        ('月破', '月破日(辰月戌日)忌出行'), ('月破', '月破日(巳月亥日)忌出行'),
        ('月破', '月破日(午月子日)忌出行'), ('月破', '月破日(未月丑日)忌出行'),
        ('月破', '月破日(申月寅日)忌出行'), ('月破', '月破日(酉月卯日)忌出行'),
        ('月破', '月破日(戌月辰日)忌出行'), ('月破', '月破日(亥月巳日)忌出行'),
    ],
    '安葬': [
        ('不将日', '不将日宜安葬'), ('鸣吠日', '鸣吠日宜安葬'),
        ('鸣吠对日', '鸣吠对日宜安葬'), ('往亡', '往亡日忌安葬'),
        ('重丧', '重丧日忌安葬'), ('年重丧', '年重丧忌安葬'),
        ('复日', '复日忌安葬'), ('月破', '月破日忌安葬'),
    ],
    '安床': [('不将日', '不将日宜安床'), ('月破', '月破日忌安床')],
    '签约': [('月破', '月破日忌签约')],
}


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

        # H1-3（2026-10-20 拍板①）：入宅月破规则层发射已删（入宅规则.py
        # 原:121-122），反向断言全期清零、防复活（移徙 canonical 归并入宅）。
        if cev == '入宅' and '月破日忌入宅' in (yi + ji):
            fails.append(f"E: {d} {ev} 已删月破规则残留发射: 月破日忌入宅")

        if is_marriage:
            # B'：规则文本不进嫁娶总分（score_breakdown 必须为 {}）
            if bd != {}:
                fails.append(f"B': {d} {ev} score_breakdown应为空dict, 实际={bd}")
            # 等级断言（H1-2，2026-10-20 拍板③：强断言二级降格，严禁放宽）。
            # 生产 _apply_marriage_level_caps（评分器.py:6250-6313）两级互斥：
            #   一级「（犯忌嫁娶，慎用）」：details 名含"忌嫁娶"→封顶★平；
            #   二级「（小忌，降一格）」：（一级未命中）details 名含"闭日/夫星"
            #     或 warnings 含"忌嫁娶"→按 MARRIAGE_LEVEL_ORDER 降恰一档；
            #     已是❌凶（idx=0）则无处可降、不加注。
            # 测试侧结果 dict 无 warnings，故对二级降格做"档序反推"强断言：
            #   带二级后缀 ⟺ 基础级 ≡ 总分纯函数等级降恰好一档（ORDER 相邻）。
            if r.get('score', 0) > 0:
                raw_lvl = r.get('level', '') or ''
                suf1, suf2 = '（犯忌嫁娶，慎用）', '（小忌，降一格）'
                c1, c2 = suf1 in raw_lvl, suf2 in raw_lvl
                if c1 and c2:
                    fails.append(f"B': {d} {ev} 两级后缀互斥却被同注: {raw_lvl}")
                base_lvl = raw_lvl.replace(suf1, '').replace(suf2, '')
                mrg_details = r.get('marriage_details') or []
                has_ji = any(
                    '忌嫁娶' in str(_d[0])
                    for _d in mrg_details
                    if isinstance(_d, (list, tuple)) and len(_d) >= 1)
                ORDER = scorer.MARRIAGE_LEVEL_ORDER
                chk_lvl = scorer._get_level(r['score'], wx, r.get('huangdao_info'))
                if has_ji:
                    # 一级封顶：必带 suf1、不带 suf2，基础级≤★平
                    if not c1 or c2 or base_lvl not in ('❌ 凶', '★ 平'):
                        fails.append(
                            f"B': {d} {ev} 忌嫁娶应封顶(≤★平)带后缀, 实际={raw_lvl}")
                elif c1:
                    # 反向断言：无一级触发（details 无"忌嫁娶"）不得带一级后缀
                    fails.append(
                        f"B': {d} {ev} 无忌嫁娶触发却带一级后缀: {raw_lvl}")
                elif c2:
                    # 二级降格强断言：基础级≡纯函数等级按 ORDER 降恰好一档
                    try:
                        _i_pure = ORDER.index(chk_lvl)
                        _i_base = ORDER.index(base_lvl)
                        if _i_pure < 1 or _i_base != _i_pure - 1:
                            fails.append(
                                f"B': {d} {ev} 降一格档序错: "
                                f"基础={base_lvl} 纯函数={chk_lvl}")
                    except ValueError:
                        fails.append(
                            f"B': {d} {ev} 降一格等级不在ORDER: "
                            f"基础={base_lvl} 纯函数={chk_lvl}")
                else:
                    # 无后缀（含二级触发但❌凶无处可降）：等级==总分纯函数
                    if base_lvl != chk_lvl:
                        fails.append(
                            f"B': {d} {ev} 等级非总分纯函数: {base_lvl} vs {chk_lvl}")
        else:
            # H1-1（2026-10-20 拍板）：分金/正体大凶不走忌事 -15——生产侧
            # 评分器.py:4918-4919 显式跳过，扣分由 _fj_penalty 单列
            # '分金扣分' 键（评分器.py:5117-5119 取 -abs(得分)、:5306-5308 入账）。
            # 本段不做简单排除，双向强断言：
            #   ① 忌事分期望 = -15×(忌项-被停-大凶条数)；
            #   ② 各大凶条目文本内「得分N」取 -abs(N) 合计 == breakdown['分金扣分']
            #      （验证扣分真实落入单列键、未丢失）。
            _fj_items = [t for t in ji if t.startswith(('分金大凶', '正体大凶'))]
            exp_yi = 10 * (len(yi) - len(po_yi))
            exp_ji = -15 * (len(ji) - len(po_ji) - len(_fj_items))
            if bd.get('宜事得分') != exp_yi:
                fails.append(f"B: {d} {ev} 宜事分={bd.get('宜事得分')} 期望={exp_yi} yi={yi}")
            if bd.get('忌事得分') != exp_ji:
                fails.append(f"B: {d} {ev} 忌事分={bd.get('忌事得分')} 期望={exp_ji} ji={ji}")
            _exp_fj = 0
            for _t in _fj_items:
                _m = re.search(r'得分(-?\d+)', _t)
                if not _m:
                    fails.append(f"B: {d} {ev} 大凶条目无『得分N』可校: {_t}")
                    continue
                _exp_fj += -abs(int(_m.group(1)))
            _fj_actual = bd.get('分金扣分', 0) or 0
            if _fj_actual != _exp_fj:
                # 唯一合法例外：一票否决日早退（评分器.py:5123-5132）——当日
                # breakdown 由 _build_wu_xing_breakdown 重建，不含'分金扣分'
                # 键；总分强制归零，强扣分本不落账。此时 r['score'] 必为 0；
                # 其余情形（键在而值不符，或非否决日缺键）均为真异常。
                if not (_exp_fj != 0 and _fj_actual == 0
                        and r.get('score', 1) == 0):
                    fails.append(
                        f"B: {d} {ev} 分金扣分={bd.get('分金扣分', 0)} "
                        f"期望={_exp_fj} 大凶条目={_fj_items}")
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
    if len(map_families) != 45:
        fails.append(f"A: 映射族数={len(map_families)}（应45，H1-3 删入宅月破族后）")

    # ---------- F. 映射族发射源守卫（H1-4，2026-10-20 拍板④） ----------
    # 每 tx 必须有生产发射源：① modules 源码字面量命中（剔除评分器.py 内
    # H1_ANCHOR_MAP 定义块自身，防止"只改表不改发射"自检通过）；② 或命中
    # 下列登记的动态发射 f-string 模式（fullmatch，源见各条注释）。
    import glob as _glob
    _srcs = []
    for _p in _glob.glob(os.path.join(_REPO_ROOT, 'modules', '**', '*.py'),
                         recursive=True):
        with open(_p, encoding='utf-8') as _f:
            _s = _f.read()
        if _p.endswith('评分器.py'):
            _i = _s.find('H1_ANCHOR_MAP = {')
            if _i >= 0:
                _s = _s[:_i] + _s[_s.find('\n}', _i):]
        _srcs.append(_s)
    _DYN_TX = [
        # 修造规则.py:286/288 f'建除{jianchu}日[宜忌]修造'
        (re.compile(r'建除.+日宜修造'), '修造规则.py:286'),
        (re.compile(r'建除.+日忌修造'), '修造规则.py:288'),
        # 开业规则.py:171/173 f'建除{jianchu}日[宜忌]开业'
        (re.compile(r'建除.+日[宜忌]开业'), '开业规则.py:171/173'),
        # 出行规则.py:180 f'月破日({month_zhi}月{day_zhi}日)忌出行'
        (re.compile(r'月破日\(.{1}月.{1}日\)忌出行'), '出行规则.py:180'),
        # 通用规则.py:230 f'月破日忌{event_type}'（签约走通用链）
        (re.compile(r'月破日忌签约'), '通用规则.py:230'),
    ]
    for tx in sorted(all_tx):
        if any(tx in _s for _s in _srcs):
            continue
        if any(_pat.fullmatch(tx) for _pat, _ in _DYN_TX):
            continue
        fails.append(f"F: 映射tx无发射源（字面量/动态模式均无）: {tx}")

    # ---------- G. H1_ANCHOR_MAP 双向对账（H1-5，2026-10-20 拍板⑤） ----------
    # 测试侧独立清单 ⟷ 生产常量双向等式：键集合、每族 (ss,tx) 集合均须
    # 全等；多余族/错族/缺族/tx 漂移逐条列出。改表须先改清单（见清单注释）。
    if set(EXPECT_H1_FAMILIES.keys()) != set(H1_ANCHOR_MAP.keys()):
        fails.append(
            f"G: 映射表键对账不符: 多出={sorted(set(H1_ANCHOR_MAP) - set(EXPECT_H1_FAMILIES))} "
            f"缺少={sorted(set(EXPECT_H1_FAMILIES) - set(H1_ANCHOR_MAP))}")
    for ev in set(EXPECT_H1_FAMILIES) & set(H1_ANCHOR_MAP):
        exp_set = set(EXPECT_H1_FAMILIES[ev])
        act_set = {tuple(p) for p in H1_ANCHOR_MAP[ev]}
        if exp_set != act_set:
            fails.append(
                f"G: {ev} 族清单对账不符: 多出={sorted(act_set - exp_set)} "
                f"缺少={sorted(exp_set - act_set)}")

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
    print("PASS：结构45 + 每日对账一致(无溢出) + 锚点全命中 + 单边未停 + 嫁娶零影响 + 发射源在位 + 双向对账一致")
    sys.exit(0)


if __name__ == '__main__':
    main()
