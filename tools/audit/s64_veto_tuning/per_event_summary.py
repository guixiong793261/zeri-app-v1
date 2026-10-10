# -*- coding: utf-8 -*-
"""s63_remain 剩余门槛专项分析：per-event/per-pop/per-year 否决率与通道贡献汇总。

输入：同目录 veto_remain_raw_{tag}.json（由 veto_remain_audit.py 生成）。
输出：veto_remain_per_event_{tag}.json + stdout 四段式汇总表。
口径：分类逻辑 import veto_remain_audit（classify_text/to_channel），不另造。

用法：
    python tools/audit/s63_remain/per_event_summary.py --tag 2024-2027
"""
import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, '..', '..', '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)  # import 同目录 veto_remain_audit

from veto_remain_audit import classify_text, to_channel  # noqa: E402

# 主类口径：剔除交叉项与子标签（与主脚本 aggregate 一致）
_SUB_TAGS = ('五行兜底·内含', '仙命·叠大忌', '仙命·无制化')


def main_cats_of(cats):
    return [c for c in cats if not any(c.startswith(p) for p in _SUB_TAGS)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='2024-2027')
    args = ap.parse_args()

    raw_path = os.path.join(_HERE, f'veto_remain_raw_{args.tag}.json')
    if not os.path.exists(raw_path):
        print(f'[exit 1] raw 数据不存在: {raw_path}')
        sys.exit(1)
    raw = json.load(open(raw_path, encoding='utf-8'))

    # per (year, event, pop)：总评分单元数未知（raw 只含否决日），
    # 总天数 = 2024-2027 闰年规则逐年天数 × 该事件该档是否参评
    YEAR_DAYS = {'2024': 366, '2025': 365, '2026': 365, '2027': 365}
    table = {}
    chan_hit = {}   # (y,ev,pop) -> {channel: n}
    chan_solo = {}  # (y,ev,pop) -> {channel: n}
    fine_hit = {}   # (y,ev,pop) -> {fine: n}
    for y, yd in raw.items():
        for ev, pd in yd.items():
            for pop, days in pd.items():
                k = (y, ev, pop)
                chan_hit[k] = {}
                chan_solo[k] = {}
                fine_hit[k] = {}
                for dateiso, texts in days.items():
                    cats = []
                    for t in texts:
                        for c in classify_text(t):
                            if c not in cats:
                                cats.append(c)
                    mc = main_cats_of(cats)
                    chans = sorted({to_channel(c) for c in mc})
                    for c in mc:
                        fine_hit[k][c] = fine_hit[k].get(c, 0) + 1
                    for ch in chans:
                        chan_hit[k][ch] = chan_hit[k].get(ch, 0) + 1
                    if len(chans) == 1:
                        ch = chans[0]
                        chan_solo[k][ch] = chan_solo[k].get(ch, 0) + 1
                total = YEAR_DAYS.get(y, 0)
                table[k] = {'vetoed': len(days), 'total': total,
                            'rate': round(len(days) / total, 4) if total else None}

    # stdout 汇总
    print('===== 否决率 per (year, event, pop) =====')
    for (y, ev, pop), v in sorted(table.items()):
        print(f"{y} {ev} pop{pop}: {v['vetoed']}/{v['total']} = {v['rate']:.1%}")

    print('\n===== 通道贡献 per (year, event, pop)（命中率 | 仅因该通道） =====')
    for (y, ev, pop), v in sorted(table.items()):
        k = (y, ev, pop)
        tot = v['vetoed']
        parts = [f"{ch}:{chan_hit[k].get(ch, 0)}"
                 + (f"({chan_solo[k][ch]})" if chan_solo[k].get(ch) else '')
                 for ch in sorted(chan_hit[k], key=lambda c: -chan_hit[k][c])]
        print(f"{y} {ev} pop{pop} 否决{tot}: " + ' '.join(parts))

    # 落盘
    out = {
        'rate': {f'{y}|{ev}|{pop}': v for (y, ev, pop), v in sorted(table.items())},
        'channel_hit': {f'{y}|{ev}|{pop}': v for (y, ev, pop), v in sorted(chan_hit.items())},
        'channel_solo': {f'{y}|{ev}|{pop}': v for (y, ev, pop), v in sorted(chan_solo.items())},
        'fine_hit': {f'{y}|{ev}|{pop}': v for (y, ev, pop), v in sorted(fine_hit.items())},
    }
    out_path = os.path.join(_HERE, f'veto_remain_per_event_{args.tag}.json')
    json.dump(out, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n[save] {out_path}')
    sys.exit(0)


if __name__ == '__main__':
    main()

