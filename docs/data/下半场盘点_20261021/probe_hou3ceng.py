# -*- coding: utf-8 -*-
"""下半场第一批·高频已验表源神煞「后三层」只读盘点（2026-10-21）

只读脚本：不修改任何生产代码，仅调用 modules 既有接口做聚合。
口径：
  - 时间窗：2026-01-01~2026-12-31（365 天），时柱取 10:00（与 §144/§147 一致）
  - 事项：15 通道（入宅/移徙/嫁娶/动土/修造/拆舍/出行/开业/安床/作灶/
    安葬/入学/求医/签约/通用）
  - 取分：modules.shensha.get_checker(ev).check(sizhu, []) 的 name/score
  - 登记：modules.事项标准.SHENSHA_SCORES 三级查找（原事项→canonical→通配）

输出三段：
  A. 全年神煞「天次×|分值|」权重排行（选批依据）
  B. 候选神煞「注册事项 vs 实际发射事项」白名单对账
  C. 各事项「实发神煞是否有分值表登记」覆盖率（口径层脱钩面）

用法：python probe_hou3ceng.py [--json out.json]
退出码：0=正常 1=异常
"""
import sys
import os
import io
import json
import datetime as dt
from collections import defaultdict

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _ROOT)

from modules.四柱计算器 import calculate_sizhu        # noqa: E402
from modules.shensha import get_checker               # noqa: E402
from modules.事项标准 import (SHENSHA_SCORES, canonical_event)  # noqa: E402

EV15 = ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '开业',
        '安床', '作灶', '安葬', '入学', '求医', '签约', '通用']
CAND = ['月破', '月刑', '月害', '归忌', '伏断日', '往亡', '天吏', '反支日',
        '飞廉', '孤辰寡宿', '土瘟', '黄幡', '丧门', '五鬼', '吊客', '大祸',
        '大耗', '红砂日', '三煞', '年三煞', '太岁', '月煞', '大时',
        '受死日', '土王用事', '天德', '月德']
ALT = {'伏断日': ['伏断日', '伏断'], '反支日': ['反支日', '反支']}


def registered(ev, nm):
    """分值表是否登记（三级查找，与 shensha_score 同口径）"""
    if (ev, nm) in SHENSHA_SCORES:
        return True
    if (canonical_event(ev), nm) in SHENSHA_SCORES:
        return True
    return ('*', nm) in SHENSHA_SCORES


def main():
    days = []
    d = dt.date(2026, 1, 1)
    while d <= dt.date(2026, 12, 31):
        days.append((d, calculate_sizhu(d, 10, 0)))
        d += dt.timedelta(days=1)

    agg = defaultdict(lambda: {'ct': 0, 'days': set(), 'evs': set(),
                               'scores': set(), 'abs': 0, 'net': 0})
    emit = defaultdict(lambda: defaultdict(lambda: {'days': set(),
                                                    'scores': set()}))
    cov = {}
    unreg_all = defaultdict(lambda: {'ct': 0, 'abs': 0, 'evs': set(),
                                     'scores': set()})

    for ev in EV15:
        ck = get_checker(ev)
        unreg = defaultdict(lambda: [0, set()])
        ev_sort = set()
        for dd, sz in days:
            for s in ck.check(sz, []):
                nm = s.get('name', '')
                sc = s.get('score', 0) or 0
                ev_sort.add(nm)
                a = agg[nm]
                a['ct'] += 1
                a['days'].add(dd)
                a['evs'].add(ev)
                a['scores'].add(sc)
                a['abs'] += abs(sc)
                a['net'] += sc
                e = emit[nm][ev]
                e['days'].add(dd)
                e['scores'].add(sc)
                if sc != 0 and not registered(ev, nm):
                    unreg[nm][0] += 1
                    unreg[nm][1].add(sc)
                    u = unreg_all[nm]
                    u['ct'] += 1
                    u['abs'] += abs(sc)
                    u['evs'].add(ev)
                    u['scores'].add(sc)
        cov[ev] = {
            'kinds': len(ev_sort),
            'unreg_kinds': len(unreg),
            'unreg_ct': sum(v[0] for v in unreg.values()),
            'unreg_abs': sum(v[0] * abs(max(v[1], key=abs))
                             for v in unreg.values()),
            'unreg': {k: {'ct': v[0], 'scores': sorted(v[1])}
                      for k, v in unreg.items()},
        }

    # A：权重排行
    print('=' * 96)
    print('[A] 2026 全年神煞权重排行（天次×|分值|，前 30 负权重）')
    print('=' * 96)
    neg = [(n, a) for n, a in agg.items() if a['net'] < 0]
    for nm, a in sorted(neg, key=lambda kv: -kv[1]['abs'])[:30]:
        print(f"{nm:<10}天次={a['ct']:>5} 天数={len(a['days']):>4} "
              f"事项={len(a['evs']):>2} 分值={sorted(a['scores'])} "
              f"|分|={a['abs']}")

    # B：白名单对账
    print('\n' + '=' * 96)
    print('[B] 候选神煞：注册事项 vs 实际发射事项')
    print('=' * 96)
    cand_out = {}
    for nm in CAND:
        reg = {k[0]: v for k, v in SHENSHA_SCORES.items() if k[1] == nm}
        act = {}
        for n2 in ALT.get(nm, [nm]):
            for ev, e in emit.get(n2, {}).items():
                a = act.setdefault(ev, {'days': set(), 'scores': set()})
                a['days'] |= e['days']
                a['scores'] |= e['scores']
        onlyreg = sorted(set(reg) - set(act))
        onlyact = sorted(set(act) - {k for k in act if registered(k, nm)})
        day_all = set()
        for a in act.values():
            day_all |= a['days']
        cand_out[nm] = {
            'days': len(day_all),
            'ct': sum(len(a['days']) for a in act.values()),
            'reg': reg,
            'act': {ev: {'days': len(a['days']),
                         'scores': sorted(a['scores'])}
                    for ev, a in act.items()},
            'only_reg': onlyreg,
            'only_act_unregistered': onlyact,
        }
        print(f"\n【{nm}】天数={len(day_all)} 天次={cand_out[nm]['ct']} "
              f"注册={len(reg)} 实发={len(act)}")
        print('  注册: ' + (', '.join(f'{k}={v}' for k, v in
                                      sorted(reg.items(),
                                             key=lambda x: -abs(x[1])))
                           or '（无）'))
        print('  实发: ' + (', '.join(
            f'{ev}:{len(a["days"])}d/{",".join(str(x) for x in sorted(a["scores"]))}'
            for ev, a in sorted(act.items(), key=lambda x: -len(x[1]['days'])))
            or '（无）'))
        if onlyreg:
            print(f'  ⚠ 注册未发射: {onlyreg}')
        if onlyact:
            print(f'  ⚠ 发射未注册: {onlyact}')

    # C：覆盖率
    print('\n' + '=' * 96)
    print('[C] 口径层覆盖率：实发神煞中未登记分值的面')
    print('=' * 96)
    print(f"{'事项':<6}{'实发种类':>8}{'未注册种类':>10}{'未注册天次':>10}"
          f"{'未注册|分|':>10}")
    for ev in EV15:
        c = cov[ev]
        print(f"{ev:<6}{c['kinds']:>8}{c['unreg_kinds']:>10}"
              f"{c['unreg_ct']:>10}{c['unreg_abs']:>10}")

    out = {'meta': {'year': 2026, 'hour': 10, 'events': EV15,
                    'days': len(days), 'cells': len(days) * len(EV15)},
           'rank': {nm: {'ct': a['ct'], 'days': len(a['days']),
                         'evs': sorted(a['evs']), 'scores': sorted(a['scores']),
                         'abs': a['abs'], 'net': a['net']}
                    for nm, a in agg.items()},
           'candidates': cand_out,
           'coverage': cov,
           'unregistered_total': {nm: {'ct': u['ct'], 'abs': u['abs'],
                                       'evs': sorted(u['evs']),
                                       'scores': sorted(u['scores'])}
                                  for nm, u in unreg_all.items()}}
    return out


if __name__ == '__main__':
    try:
        data = main()
        if '--json' in sys.argv:
            p = sys.argv[sys.argv.index('--json') + 1]
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            print(f'\nJSON → {p}')
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
