# -*- coding: utf-8 -*-
"""干支类实现 Bug 清理：影响面快照探针（只读）

用途：在改码前，量化两项实现 Bug 的全年影响面。
  BUG-1 蚕官≡畜官：同一谓词（_is_chuguansheng → _is_canguan）同日双扣 -20。
  BUG-2 大耗/小耗撞月破：通用族（入学/求医/签约/通用）三谓词同值，
        月破日实得 月破-30 + 大耗-20 + 小耗-15 = -65。

输出：snapshot_before.json / snapshot_after.json（由 --tag 指定）
用法：python probe_impact.py --tag before
"""
import argparse
import datetime as dt
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu          # noqa: E402
from modules.事项标准 import get_shensha_checker, shensha_score  # noqa: E402

EVENTS = ['嫁娶', '修造', '动土', '拆舍', '入宅', '移徙', '作灶', '安床',
          '开业', '出行', '安葬', '入学', '求医', '签约', '通用']
# 通用族：无专属 checker，落 CommonShenShaChecker
GENERIC_FAMILY = {'入学', '求医', '签约', '通用'}


def eff_score(ev, name, fallback):
    v = shensha_score(ev, name, None)
    return fallback if v is None else v


def collect(year=2026):
    rows = []
    d = dt.date(year, 1, 1)
    while d <= dt.date(year, 12, 31):
        sz = calculate_sizhu(d, 10, 0)
        for ev in EVENTS:
            c = get_shensha_checker(ev)
            items = c.check(sz, [])
            names = {}
            for s in items:
                nm = s.get('name')
                fb = s.get('score', 0) or 0
                names[nm] = eff_score(ev, nm, fb)
            rows.append({
                'date': d.isoformat(),
                'month_zhi': sz.get('month_zhi'),
                'day_zhi': sz.get('day_zhi'),
                'event': ev,
                'names': names,
            })
        d += dt.timedelta(days=1)
    return rows


def summarize(rows):
    out = {}
    for r in rows:
        ev = r['event']
        b = out.setdefault(ev, {'total': 0, 'days': 0, 'neg_items': 0,
                                'canguan_days': 0, 'chuguan_days': 0,
                                'both_days': 0, 'yuepo65_days': 0,
                                'dahao_days': 0, 'xiaohao_days': 0})
        n = r['names']
        b['total'] += sum(n.values())
        b['days'] += 1
        b['neg_items'] += sum(1 for v in n.values() if v < 0)
        if '蚕官' in n:
            b['canguan_days'] += 1
        if '畜官' in n:
            b['chuguan_days'] += 1
        if '蚕官' in n and '畜官' in n:
            b['both_days'] += 1
        if '大耗' in n:
            b['dahao_days'] += 1
        if '小耗' in n:
            b['xiaohao_days'] += 1
        if '月破' in n and '大耗' in n and '小耗' in n:
            b['yuepo65_days'] += 1
    return out


def simulate_fix(rows):
    """虚拟清理后的快照（不改码）：去畜官；通用族月破日去大耗/小耗。"""
    fixed = []
    for r in rows:
        n = dict(r['names'])
        n.pop('畜官', None)
        if r['event'] in GENERIC_FAMILY and '月破' in n:
            n.pop('大耗', None)
            n.pop('小耗', None)
        fixed.append(dict(r, names=n))
    return fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='before')
    args = ap.parse_args()

    rows = collect()
    before = summarize(rows)
    after = summarize(simulate_fix(rows))

    payload = {
        'year': 2026,
        'bug1_canguan_chuguan': {
            'before_both_days_total': sum(v['both_days'] for v in before.values()),
            'before_penalty_per_day': -20,
            'after_penalty_per_day': -10,
        },
        'bug2_dahao_yuepo': {
            'generic_family': sorted(GENERIC_FAMILY),
            'before_yuepo65_days_total': sum(v['yuepo65_days'] for v in before.values()),
        },
        'per_event_before': before,
        'per_event_after_virtual': after,
        'delta_total': {ev: after[ev]['total'] - before[ev]['total'] for ev in before},
    }

    fn = os.path.join(os.path.dirname(__file__), 'snapshot_%s.json' % args.tag)
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print('=' * 78)
    print('快照标签:', args.tag)
    print('BUG-1 蚕官+畜官 同日双扣天数合计:',
          payload['bug1_canguan_chuguan']['before_both_days_total'])
    print('BUG-2 通用族 月破日 -65 三重扣 天数合计:',
          payload['bug2_dahao_yuepo']['before_yuepo65_days_total'])
    print('-' * 78)
    print('%-6s %10s %10s %10s %10s' % ('事项', '清洗前', '清洗后', '差值', '畜官双扣天'))
    for ev in EVENTS:
        b, a = before[ev], after[ev]
        print('%-6s %10d %10d %10d %10d' % (
            ev, b['total'], a['total'], a['total'] - b['total'], b['both_days']))
    print('-' * 78)
    print('全通道合计: 前 %d → 后 %d (差 %+d)' % (
        sum(v['total'] for v in before.values()),
        sum(v['total'] for v in after.values()),
        sum(v['total'] for v in after.values()) - sum(v['total'] for v in before.values())))
    print('快照已写入:', fn)


if __name__ == '__main__':
    main()
