# -*- coding: utf-8 -*-
"""重丧日实现一致性 + 入宅受死日纯展示 综合回归（2026-10-28，001 §195）
================================================================================
被测变更：
  · Commit1：入宅/移徙 受死日剥离扣分（§190 已升 HARD_VETO）——
    modules/事项标准.py 两键 -15→0；modules/shensha/入宅神煞.py 发射 -22→0。
  · Commit2：重丧日纯工程修复（不改判定极性、不改分值）——
    (a) 修造「第三套实现」废弃：修造神煞扩展._is_zhongsang 改委托单点出口
        is_zhongsang_by_lunar（原节令月支查日干，2026 命中 68 天 → 32 天）；
    (b) 死 Bug：原 zhongsang_map 中 '戌' 键重复覆盖（「四十丙壬」分支被吞），
        随第三实现一并废除；
    (c) 空转激活：嫁娶规则 _check_bad_gods 补齐「重丧日」发射，使
        _check_veto_items 的 '重丧日' 关键词可命中（原 ji_list 从不写入 → 空转）。

断言结构（正反双向）：
  A. 源码层：修造委托单点出口、无 zhongsang_map 残留、嫁娶规则层已发射。
  B. 全年一致性：修造 Ext 与单点出口 2026 逐日零分歧（32 天）。
  C. 空转激活：嫁娶规则层 ji 含「重丧日」32 天且全部触发 veto（原 0/0）。
  D. 极性不变：('嫁娶','重丧日') / ('修造','重丧日') 仍 -10；神煞层发射恒 -10。
  E. 入宅/移徙 受死日：键 0、发射恒 0 分、结论仍否决、全年总分 11601。
  F. 反向保留：安葬通道重丧口径不受本批波及（发射仍 >0）。

退出码：0=全过，1=有失败（FAIL N 计数）
================================================================================
"""
import sys
import inspect
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FAILS = []


def check(name, cond, detail=''):
    if cond:
        print(f'  PASS  {name}')
    else:
        print(f'  FAIL  {name}  {detail}')
        FAILS.append(name)


def _code_only(src):
    return '\n'.join(ln.split('#', 1)[0] for ln in src.splitlines())


CH = ['嫁娶', '修造', '入宅', '移徙', '动土', '拆舍', '安葬']
D0, D1 = dt.date(2026, 1, 1), dt.date(2026, 12, 31)


def main():
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha import get_checker
    from modules.shensha.神煞基类 import is_shousi_by_zhi, is_zhongsang_by_lunar
    from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
    from modules.rules.嫁娶规则 import MarriageRuleChecker
    from modules.事项标准 import SHENSHA_SCORES, shensha_score

    days = []
    d = D0
    while d <= D1:
        days.append((d, calculate_sizhu(d, 10, 0)))
        d += dt.timedelta(days=1)

    # ============ A：源码层 ============
    print('[A] 源码层：第三实现废除 / 死 Bug 根除 / 空转激活')
    src_ext = _code_only(inspect.getsource(ConstructionShenShaCheckerExt._is_zhongsang))
    check('A1 修造 _is_zhongsang 已委托单点出口 is_zhongsang_by_lunar',
          'is_zhongsang_by_lunar(' in src_ext)
    check('A1 修造 _is_zhongsang 不再按节令月支自查（无 sizhu 月支取值）',
          "sizhu['month_zhi']" not in src_ext
          and "zhongsang_map =" not in src_ext)
    src_all = _code_only(inspect.getsource(ConstructionShenShaCheckerExt))
    check('A2 修造类内 zhongsang_map 表已彻底废除（剥注释后无赋值残留）',
          'zhongsang_map =' not in src_all)
    src_rc = _code_only(inspect.getsource(MarriageRuleChecker._check_bad_gods))
    check("A3 嫁娶规则层 _check_bad_gods 已发射「重丧日」且走单点出口",
          "ji_list.append('重丧日')" in src_rc
          and 'is_zhongsang_by_lunar(' in src_rc)

    # ============ B：全年一致性 ============
    print('[B] 修造 Ext 与单点出口 2026 逐日零分歧')
    ext = ConstructionShenShaCheckerExt()
    n_ext = n_base = 0
    bad = []
    for d, sz in days:
        e = any(s.get('name') == '重丧日' for s in ext.check(sz, []))
        b = is_zhongsang_by_lunar(d)
        n_ext += e
        n_base += b
        if e != b:
            bad.append(str(d))
    check(f'B1 修造重丧天数=32（原第三实现 68；实得 {n_ext}）', n_ext == 32)
    check(f'B1 单点出口重丧天数=32（实得 {n_base}）', n_base == 32)
    check(f'B2 逐日分歧=0（实得 {len(bad)}）', not bad, f'{bad[:4]}')

    # ============ C：空转激活 ============
    print('[C] 嫁娶规则层关键词空转已激活')
    rc = MarriageRuleChecker()
    n_ji = n_veto = 0
    miss = []
    for d, sz in days:
        out = rc.check(sz, [])
        ji, veto, reason = out[1] or [], out[2], str(out[3] or '')
        hit = [x for x in ji if '重丧' in str(x)]
        if hit:
            n_ji += 1
            if veto and '重丧' in reason:
                n_veto += 1
            else:
                miss.append(str(d))
    check(f'C1 嫁娶规则层 ji 含「重丧日」=32 天（原空转 0；实得 {n_ji}）',
          n_ji == 32)
    check(f'C2 32 天全部触发 veto 且原因含重丧（实得 {n_veto}）', n_veto == 32)
    check(f'C2 无「ji 有重丧但未否决」漏网（实得 {len(miss)}）', not miss,
          f'{miss[:4]}')

    # ============ D：极性不变 ============
    print('[D] 判定极性与分值不变')
    check("D1 ('嫁娶','重丧日')=-10", SHENSHA_SCORES.get(('嫁娶', '重丧日')) == -10)
    check("D1 ('修造','重丧日')=-10", SHENSHA_SCORES.get(('修造', '重丧日')) == -10)
    for ev in ('嫁娶', '修造'):
        # 修造类在 get_checker 中返回基类（ConstructionShenShaChecker），
        # 神煞发射实际由评分器分支使用的 ConstructionShenShaCheckerExt 承担。
        ck = ext if ev == '修造' else get_checker(ev)
        sc = set()
        n = 0
        for d, sz in days:
            for s in ck.check(sz, []):
                if s.get('name') == '重丧日':
                    sc.add(s.get('score'))
                    n += 1
        check(f'D2 {ev} 重丧发射=32 天恒 -10（实得 {n}/{sorted(sc)}）',
              n == 32 and sc == {-10})

    # ============ E：入宅/移徙 受死日纯展示 ============
    print('[E] 入宅/移徙 受死日剥离扣分（§195 Commit1）')
    for ev in ('入宅', '移徙'):
        check(f"E1 shensha_score('{ev}','受死日')=0",
              shensha_score(ev, '受死日') == 0)
    ck_ru = get_checker('入宅')
    n_ss = 0
    bad_ss = []
    tot_ru = 0
    for d, sz in days:
        rows = ck_ru.check(sz, [])
        tot_ru += sum(s.get('score', 0) for s in rows)
        if is_shousi_by_zhi(sz['month_zhi'], sz['day_zhi']):
            hit = [s for s in rows if s.get('name') == '受死日']
            n_ss += 1
            if len(hit) != 1 or hit[0].get('score') != 0:
                bad_ss.append((str(d), [h.get('score') for h in hit]))
    check(f'E2 入宅受死日 31 天（实得 {n_ss}）', n_ss == 31)
    check(f'E2 发射恒 0 分且唯一（异常 {len(bad_ss)}）', not bad_ss, f'{bad_ss[:3]}')
    check(f'E3 入宅神煞全年总分=11601（实得 {tot_ru}）', tot_ru == 11601)

    from modules.评分器 import calculate_score
    sd = next(d for d, sz in days if is_shousi_by_zhi(sz['month_zhi'], sz['day_zhi']))
    r = calculate_score(calculate_sizhu(sd, 10, 0), '入宅', owners=[])
    check(f'E4 受死日（{sd}）0 分但结论仍否决（实得 {r.get("score")}/{r.get("level")}）',
          r.get('score') == 0 and '凶' in str(r.get('level')))

    # ============ F：反向保留 ============
    print('[F] 反向保留：安葬通道重丧口径不受波及')
    ck_az = get_checker('安葬')
    n_az = sum(1 for d, sz in days
               if any('重丧' in str(s.get('name')) for s in ck_az.check(sz, [])))
    check(f'F1 安葬通道重丧类发射仍 >0（实得 {n_az}）', n_az > 0)

    print()
    if FAILS:
        print(f'FAIL {len(FAILS)} 项：' + '、'.join(FAILS))
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
