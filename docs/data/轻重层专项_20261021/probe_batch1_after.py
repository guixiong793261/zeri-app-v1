# -*- coding: utf-8 -*-
"""
轻重层批次1·改后复测探针（真实改码已落地，无 monkey-patch）
======================================================================
目的：Commit 1 改码完成后，实测 2026 全年 15 通道总分，逐通道核验
     Δ==推定表（weight_impact_2026.json × 拍板 Δ 分值），并复核
     哨兵 221 不漂移、键数 1200/移徙 71、通配月德合=15。

退出码 0=全部核验通过；1=任一不符（须停下呈报，不得自行调值）。
"""
import io
import os
import sys
import json
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu          # noqa: E402
from modules.shensha import get_checker               # noqa: E402
from modules.事项标准 import SHENSHA_SCORES, shensha_score  # noqa: E402

EVENTS = ['修造', '动土', '拆舍', '入宅', '移徙', '嫁娶', '安葬', '安床',
          '出行', '开业', '作灶', '入学', '求医', '签约', '通用']

# 推定表：改前基线（HEAD 实测）→ 改后预期（Δ 逐项推定，入宅/移徙/嫁娶已经
# monkey-patch 探针实证；其余 12 通道本次实测核验）
EXPECT = {
    '修造': (-7942, -7972), '动土': (-9420, -7866), '拆舍': (-10436, -8882),
    '入宅': (3188, 3377), '移徙': (3188, 3377), '嫁娶': (-153, 214),
    '安葬': (-2654, -2749), '安床': (5120, 5242), '出行': (6736, 6920),
    '开业': (7899, 7804), '作灶': (-1220, -1315), '入学': (9979, 10158),
    '求医': (8434, 8856), '签约': (9034, 9306), '通用': (9116, 9321),
}

Y0 = datetime.date(2026, 1, 1)
Y1 = datetime.date(2026, 12, 31)
B_NAMES = {'月厌', '月刑', '月害', '土王用事', '受死日', '往亡', '归忌',
           '地囊', '八专', '月德合'}


def run_year(ev):
    ck = get_checker(ev)
    tot = 0
    d = Y0
    while d <= Y1:
        sz = calculate_sizhu(d, 10, 0)
        for s in ck.check(sz, []):
            tot += s['score']
        d += datetime.timedelta(days=1)
    return tot


def main():
    out = {'after': {}, 'expect': {e: v[1] for e, v in EXPECT.items()},
           'delta': {}, 'match': {}, 'sentinel': {}, 'key_count': {}}
    fails = []

    for ev in EVENTS:
        v = run_year(ev)
        out['after'][ev] = v
        out['delta'][ev] = v - EXPECT[ev][0]
        ok = (v == EXPECT[ev][1])
        out['match'][ev] = ok
        mark = 'OK ' if ok else 'MISMATCH'
        print('[%s] %s 改后=%d 预期=%d (Δ=%+d)' % (mark, ev, v, EXPECT[ev][1], out['delta'][ev]))
        if not ok:
            fails.append(ev)

    # 键数
    total_n = len(SHENSHA_SCORES)
    yi_n = sum(1 for (e, n) in SHENSHA_SCORES if e == '移徙')
    out['key_count'] = {'total': total_n, '移徙': yi_n}
    print('[键数] 总=%d（须=1200） 移徙=%d（须=71）' % (total_n, yi_n))
    if total_n != 1200 or yi_n != 71:
        fails.append('key_count')

    # 通配月德合
    w1 = shensha_score('移徙', '月德合')
    w2 = shensha_score('嫁娶', '月德合')
    print('[通配] 移徙/月德合=%r 嫁娶/月德合=%r（须=15）' % (w1, w2))
    if w1 != 15 or w2 != 15:
        fails.append('wildcard')

    # 哨兵 2026-11-04 入宅三时柱：B 组零命中（本批安全性质）。
    # 注：全链路日课分 221 由 tests/verify_wumu_buzhihua.py 核验（主程序口径），
    # 本探针仅记录神煞分和作参照，不断言 221。
    sd = datetime.date(2026, 11, 4)
    for hh in (10, 12, 18):
        sz = calculate_sizhu(sd, hh, 0)
        hits = [(s['name'], s['score']) for s in get_checker('入宅').check(sz, [])]
        touched = [(n, sc) for n, sc in hits if n in B_NAMES]
        day_tot = sum(sc for _, sc in hits)
        out['sentinel']['%02d:00' % hh] = {'shensha_subtotal': day_tot, 'touched': touched}
        print('[哨兵 %02d:00] 神煞分和=%d B组命中=%s' % (hh, day_tot, touched if touched else '无'))
        if touched:
            fails.append('sentinel_%02d' % hh)

    jpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'probe_batch1_after.json')
    with open(jpath, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('[落盘] %s' % jpath)

    print('[复测结论] %s' % ('PASS' if not fails else 'FAIL: %s' % fails))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
