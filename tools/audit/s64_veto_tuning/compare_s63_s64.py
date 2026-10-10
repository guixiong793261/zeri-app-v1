# -*- coding: utf-8 -*-
"""§64 影响面前后对照（v2 同 SEED 同口径 93,504 评分）。

输入：
  前 tools/audit/s63_remain/veto_remain_raw_2024-2027.json（§64 前基线 79.2%）
  后 tools/audit/s64_veto_tuning/veto_remain_raw_2024-2027.json（§64 后）
输出：s64_compare_2024-2027.json + stdout 对照表。
口径：否决单元 (year,event,pop,date)；raw 只存否决日，总单元=93,504。
"""
import json
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, '..', '..', '..'))
PRE = os.path.join(_ROOT, 'tools', 'audit', 's63_remain', 'veto_remain_raw_2024-2027.json')
POST = os.path.join(_HERE, 'veto_remain_raw_2024-2027.json')

EVENTS = ['嫁娶', '订婚', '纳采', '修造', '装修', '动土', '拆舍', '入宅',
          '作灶', '安床', '安葬', '开业', '出行', '签约', '入学', '求医']
YEARS = ['2024', '2025', '2026', '2027']
YEAR_DAYS = {'2024': 366, '2025': 365, '2026': 365, '2027': 365}
POPS = ['1', '2', '3', '4']


def veto_set(raw, y, ev, pop):
    return set((raw.get(y, {}).get(ev, {}).get(pop, {}) or {}).keys())


def main():
    pre = json.load(open(PRE, encoding='utf-8'))
    post = json.load(open(POST, encoding='utf-8'))

    per = {}
    freed_list = {}
    tot_pre = tot_post = 0
    for ev in EVENTS:
        for pop in POPS:
            ep_pre = ep_post = 0
            ep_freed = 0
            n_days = 0
            for y in YEARS:
                a = veto_set(pre, y, ev, pop)
                b = veto_set(post, y, ev, pop)
                ep_pre += len(a)
                ep_post += len(b)
                freed = a - b
                ep_freed += len(freed)
                n_days += YEAR_DAYS[y]
                if freed:
                    freed_list.setdefault(f'{ev}|pop{pop}', {})[y] = sorted(freed)
            tot_pre += ep_pre
            tot_post += ep_post
            per[f'{ev}|pop{pop}'] = {
                'pre': ep_pre, 'post': ep_post, 'freed': ep_freed,
                'total': n_days,
                'pre_rate': round(ep_pre / n_days, 4),
                'post_rate': round(ep_post / n_days, 4),
                'delta_pp': round((ep_post - ep_pre) / n_days * 100, 2),
            }

    total_units = sum(YEAR_DAYS.values()) * len(EVENTS) * len(POPS)
    print(f'总否决：{tot_pre} → {tot_post}（释放 {tot_pre - tot_post}）')
    print(f'总否决率：{tot_pre/total_units:.2%} → {tot_post/total_units:.2%} '
          f'（{(tot_post-tot_pre)/total_units*100:+.2f}pp）')
    print()
    print('事项/人口档          前否决率 → 后否决率   Δpp    释放天数')
    for k in sorted(per, key=lambda k: (per[k]['delta_pp'], k)):
        v = per[k]
        print(f"{k:<18} {v['pre_rate']:6.1%} → {v['post_rate']:6.1%}  "
              f"{v['delta_pp']:+6.2f}  {v['freed']}")

    # 事项汇总（4 档合计）
    print('\n事项合计（4人口档 1461×4 单元）')
    evsum = {}
    for ev in EVENTS:
        a = sum(per[f'{ev}|pop{p}']['pre'] for p in POPS)
        b = sum(per[f'{ev}|pop{p}']['post'] for p in POPS)
        t = sum(YEAR_DAYS.values()) * 4
        evsum[ev] = {'pre': a, 'post': b, 'freed': a-b,
                     'pre_rate': round(a/t, 4), 'post_rate': round(b/t, 4),
                     'delta_pp': round((b-a)/t*100, 2)}
        print(f"{ev:<4} {a:5d} → {b:5d}  {a/t:6.1%} → {b/t:6.1%}  {evsum[ev]['delta_pp']:+6.2f}pp  释放{a-b}")

    out = {'total': {'pre': tot_pre, 'post': tot_post, 'freed': tot_pre-tot_post,
                     'units': total_units,
                     'pre_rate': round(tot_pre/total_units, 4),
                     'post_rate': round(tot_post/total_units, 4)},
           'per_event_pop': per, 'per_event': evsum,
           'freed_days': freed_list}
    outp = os.path.join(_HERE, 's64_compare_2024-2027.json')
    json.dump(out, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n[save] {outp}')


if __name__ == '__main__':
    main()
