# -*- coding: utf-8 -*-
"""红纱日嫁娶通道处置回归（§197 Commit 2 降 -20 → §212 全面剥离）
================================================================================
§197（2026-10-28）：嫁娶规则 veto_keywords 移除「红纱日」，降级 -20 扣分提示。
§212（2026-10-31 拍板 1）：协纪 p279217 奏疏明斥「甚属无当」「应请一并删去」，
    嫁娶通道**全面剥离**：撤 -20、撤 ji_list 发射、撤 shensha_list 发射；
    谓词/起例保留（孟巳仲酉季丑），修造/安床/通用通道不受影响。
  · 受死日维持 HARD_VETO（D6-Q2，三库只免丧葬、吉事仍凶）。

断言结构（正反双向，§212 口径）：
  A. 源码层：veto_keywords 无「红纱日」、仍含「受死日」；注释归属已正名。
  B. 全年：红纱日 29 天（谓词口径），无任何一天的 ji_list / 否决原因含「红纱」。
  C. 受死日 31 天全部 veto=True 且原因含「受死日」（反向保留，防误撤）。
  D. 红纱且非受死日 26 天：无否决，评分明细**不含**「红纱日」（§212 撤 -20）。
  E. 反向：红纱日叠加月破等其它硬忌时仍否决（撤红纱未波及他项）。

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


D0, D1 = dt.date(2026, 1, 1), dt.date(2026, 12, 31)


def main():
    from modules.四柱计算器 import calculate_sizhu
    from modules.评分器 import calculate_score
    from modules.rules.嫁娶规则 import MarriageRuleChecker
    from modules.shensha.神煞基类 import is_shousi_by_zhi

    src = inspect.getsource(MarriageRuleChecker._check_veto_items)
    code = '\n'.join(ln.split('#', 1)[0] for ln in src.splitlines())
    print('[A] 源码层：红纱日已出否决集，受死日仍在')
    kw = code[code.index('veto_keywords'):code.index('veto_keywords') + 200]
    check('A1 veto_keywords 不含「红纱日」', "'红纱日'" not in kw)
    check('A2 veto_keywords 仍含「受死日」', "'受死日'" in kw)
    src_cls = inspect.getsource(MarriageRuleChecker)
    check('A3 HONGSHA 注释归属正名为 p279217 奏疏明斥',
          'p279217' in src_cls and '奏疏' in src_cls)
    check('A4 HONGSHA 起例维持孟巳仲酉季丑（寅月巳/子月酉/辰月丑）',
          MarriageRuleChecker.HONGSHA.get('寅') == ['巳']
          and MarriageRuleChecker.HONGSHA.get('子') == ['酉']
          and MarriageRuleChecker.HONGSHA.get('辰') == ['丑'])

    days = []
    d = D0
    while d <= D1:
        days.append((d, calculate_sizhu(d, 10, 0)))
        d += dt.timedelta(days=1)

    rc = MarriageRuleChecker()
    print('[B] 红纱日 29 天（谓词口径）：ji_list / 否决原因均不含「红纱」')
    hs_days = [d for d, sz in days
               if sz['day_zhi'] in rc.HONGSHA.get(sz['month_zhi'], [])]
    hs_leak = []
    ss_days, ss_veto_ok = [], []
    for d, sz in [(x, calculate_sizhu(x, 10, 0)) for x in hs_days]:
        out = rc.check(sz, [])
        ji, veto, reason = out[1] or [], out[2], str(out[3] or '')
        if any('红纱' in str(x) for x in ji) or '红纱' in reason:
            hs_leak.append((str(d), ji, reason))
    for d, sz in days:
        if is_shousi_by_zhi(sz['month_zhi'], sz['day_zhi']):
            ss_days.append(d)
            out = rc.check(sz, [])
            if out[2] and '受死日' in str(out[3] or ''):
                ss_veto_ok.append(d)
    check(f'B1 红纱日天数=29（实得 {len(hs_days)}）', len(hs_days) == 29)
    check(f'B2 §212 后 ji_list/否决原因无「红纱」残留（残留 {len(hs_leak)}）', not hs_leak,
          f'{hs_leak[:3]}')

    print('[C] 受死日 31 天：HARD_VETO 维持')
    check(f'C1 受死日天数=31（实得 {len(ss_days)}）', len(ss_days) == 31)
    check(f'C2 31 天全部 veto=True 且原因含「受死日」（实得 {len(ss_veto_ok)}）',
          len(ss_veto_ok) == 31)

    print('[D] 红纱且非受死日：§212 后评分明细不含「红纱日」（撤 -20）')
    red_only = [d for d in hs_days if d not in set(ss_days)]
    n_veto, leak_score = 0, []
    for d in red_only:
        sz = calculate_sizhu(d, 10, 0)
        r = calculate_score(sz, '嫁娶', owners=[])
        if r.get('否决原因'):
            n_veto += 1
        det = [x for x in (r.get('marriage_details') or []) if '红纱' in str(x[0])]
        if det:
            leak_score.append((str(d), det))
    check(f'D1 红纱单因日=26（实得 {len(red_only)}）', len(red_only) == 26)
    check(f'D2 红纱单因日无否决（异常 {n_veto}）', n_veto == 0)
    check(f'D3 §212 后评分明细不含「红纱日」-20（残留 {len(leak_score)}）', not leak_score,
          f'{leak_score[:3]}')

    print('[E] 反向：红纱叠加其它硬忌时仍否决（未波及他项）')
    over = []
    for d in hs_days:
        out = rc.check(calculate_sizhu(d, 10, 0), [])
        if out[2]:
            over.append((str(d), str(out[3])))
    check(f'E1 红纱日仍被他项否决=14 天（实得 {len(over)}）', len(over) == 14,
          f'{over[:3]}')
    check('E2 他项否决原因均不含「红纱」',
          all('红纱' not in r for _, r in over), f'{over[:3]}')
    sample = [(d, r) for d, r in over if d == '2026-03-12']
    check('E3 抽样 2026-03-12（红纱+月破）仍 veto=True 且原因为月破',
          bool(sample) and '月破' in sample[0][1], f'{sample}')

    print()
    if FAILS:
        print(f'FAIL {len(FAILS)} 项：' + '、'.join(FAILS))
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
