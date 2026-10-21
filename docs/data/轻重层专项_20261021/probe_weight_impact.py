# -*- coding: utf-8 -*-
"""轻重层专项·影响面探针（只读，2026 全年）

口径与 docs/data/下半场盘点_20261021/probe_hou3ceng.py 一致：
  - 2026-01-01~12-31，时柱 10:00
  - 15 事项 × get_checker(ev).check(sizhu, []) 实发 name/score
  - 逐项统计：发射天数 / 天次(day×event) / 事项集 / 分值集 / 分值影响面(Σscore)
同时输出各事项逐通道分值（识别同名跨通道不平）。
用法：python probe_weight_impact.py
退出码：0=正常 1=异常
"""
import datetime as dt
import io
import json
import os
import sys
from collections import defaultdict

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu   # noqa: E402
from modules.shensha import get_checker          # noqa: E402
from modules.事项标准 import SHENSHA_WEIGHT_PENDING  # noqa: E402

EV15 = ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '开业',
        '安床', '作灶', '安葬', '入学', '求医', '签约', '通用']

# 本专项关注清单：总表轻重列 ⚠️ 去重 29 项 + 鸣吠两族（跨通道不平）+ 大时相抵支
TARGET = ['土府', '土王用事', '地囊', '年三煞', '三煞', '月破', '月厌', '月刑',
          '月害', '劫煞', '灾煞', '岁煞', '月煞', '大时', '天吏', '归忌',
          '往亡', '四废', '五墓', '八专', '四击', '四忌', '月德合', '反支',
          '反支日', '飞廉', '伏断', '伏断日', '不将', '不将日', '天恩',
          '受死日', '红嘴朱雀', '鸣吠日', '鸣吠对日']
ALT = {'反支': ['反支', '反支日'], '伏断': ['伏断', '伏断日'],
       '不将': ['不将', '不将日']}

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'weight_impact_2026.json')


def main():
    days = []
    d = dt.date(2026, 1, 1)
    while d <= dt.date(2026, 12, 31):
        days.append((d.isoformat(), calculate_sizhu(d, 10, 0)))
        d += dt.timedelta(days=1)

    agg = defaultdict(lambda: {'ct': 0, 'days': set(), 'evs': defaultdict(int),
                               'scores': defaultdict(int), 'abs': 0})
    for iso, sz in days:
        for ev in EV15:
            for it in get_checker(ev).check(sz, []):
                nm = it.get('name')
                if nm not in TARGET:
                    continue
                sc = it.get('score', 0) or 0
                a = agg[nm]
                a['ct'] += 1
                a['days'].add(iso)
                a['evs'][ev] += 1
                a['scores'][sc] += 1
                a['abs'] += abs(sc)

    # 合并别名（反支/反支日 等）
    merged = dict(agg)
    out = {}
    for base, alts in ALT.items():
        cur = {'ct': 0, 'days': set(), 'evs': defaultdict(int),
               'scores': defaultdict(int), 'abs': 0}
        for k in alts:
            if k not in agg:
                continue
            a = agg[k]
            cur['ct'] += a['ct']
            cur['days'] |= a['days']
            for e, v in a['evs'].items():
                cur['evs'][e] += v
            for s, v in a['scores'].items():
                cur['scores'][s] += v
            cur['abs'] += a['abs']
        out[base] = cur
        for k in alts:
            merged.pop(k, None)
    for k, v in merged.items():
        if k not in out:
            out[k] = v

    res = {'shensha_weight_pending': sorted(SHENSHA_WEIGHT_PENDING),
           'items': {}}
    print('%-10s %6s %6s %6s %-34s %s' % ('神煞', '天数', '天次', '影响面',
                                           '分值分布', '事项数'))
    print('-' * 110)
    for nm in TARGET:
        key = nm if nm in out else ALT.get(nm, [None])[0]
        if key not in out:
            print('%-10s %6s %6s %6s %-34s %s' % (nm, '-', '0', '0', '未发射', 0))
            res['items'][nm] = None
            continue
        a = out[key]
        res['items'][nm] = {
            'days': len(a['days']), 'ct': a['ct'], 'abs': a['abs'],
            'scores': {str(k): v for k, v in sorted(a['scores'].items())},
            'events': dict(sorted(a['evs'].items())),
            'event_count': len(a['evs']),
        }
        print('%-10s %6d %6d %6d %-34s %d' % (
            nm, len(a['days']), a['ct'], a['abs'],
            str({k: v for k, v in sorted(a['scores'].items())}),
            len(a['evs'])))

    json.dump(res, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\n->', OUT)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print('FAIL:', repr(e))
        sys.exit(1)
