# -*- coding: utf-8 -*-
"""P0 大清理（001 §172）2026 全年通道对拍探针（只读）

按评分器口径（s.get('score') 求和，评分器.py:1774）统计 15 通道全年神煞总分，
并记录清理目标神煞的命中天次。支持 --root 指向旧版本 git worktree，做改前/改后对拍。

用法：
    python probe_totals.py --root <repo_root> --tag before
    python probe_totals.py --root <repo_root> --tag after
"""
import argparse
import datetime as dt
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

AP = argparse.ArgumentParser()
AP.add_argument('--root', default=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
AP.add_argument('--tag', default='after')
ARGS = AP.parse_args()

ROOT = os.path.abspath(ARGS.root)
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu          # noqa: E402
from modules.事项标准 import get_shensha_checker       # noqa: E402

EVENTS = ['嫁娶', '修造', '动土', '拆舍', '入宅', '移徙', '作灶', '安床',
          '开业', '出行', '安葬', '入学', '求医', '签约', '通用']

WATCH = ['孤辰寡宿', '岁害', '天耗', '地耗', '黄幡', '豹尾', '丧门', '吊客',
         '官符', '岁刑', '力士', '大祸', '破败', '亡神', '蚕官', '五鬼',
         '土府', '土府日', '大耗', '小耗', '月破']


def collect(year=2026):
    per_event = {ev: {'total': 0, 'names': {}} for ev in EVENTS}
    d = dt.date(year, 1, 1)
    while d <= dt.date(year, 12, 31):
        sz = calculate_sizhu(d, 10, 0)
        for ev in EVENTS:
            items = get_shensha_checker(ev).check(sz, [])
            b = per_event[ev]
            b['total'] += sum((s.get('score', 0) or 0) for s in items)
            for s in items:
                nm = s.get('name', '')
                b['names'][nm] = b['names'].get(nm, 0) + 1
        d += dt.timedelta(days=1)
    return per_event


def main():
    per_event = collect()
    payload = {'year': 2026, 'root': ROOT, 'per_event': {}}
    for ev in EVENTS:
        b = per_event[ev]
        payload['per_event'][ev] = {
            'total': b['total'],
            'watch_days': {w: b['names'].get(w, 0) for w in WATCH if b['names'].get(w, 0)},
        }
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'totals_%s.json' % ARGS.tag)
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print('=' * 72)
    print('tag=%s root=%s' % (ARGS.tag, ROOT))
    for ev in EVENTS:
        wd = payload['per_event'][ev]['watch_days']
        wd = {k: v for k, v in wd.items() if k in ('孤辰寡宿', '岁害', '天耗', '地耗',
                                                   '土府', '土府日', '大耗', '小耗',
                                                   '黄幡', '豹尾', '丧门', '吊客',
                                                   '官符', '岁刑', '力士', '大祸',
                                                   '破败', '亡神', '蚕官', '五鬼')}
        print('%-4s total=%7d  %s' % (ev, payload['per_event'][ev]['total'], wd))
    print('全通道合计:', sum(payload['per_event'][ev]['total'] for ev in EVENTS))
    print('已写入:', fn)


if __name__ == '__main__':
    main()
