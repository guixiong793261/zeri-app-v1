# -*- coding: utf-8 -*-
"""
轻重层批次2·改后复测探针（鸣吠日/鸣吠对日 跨通道分值统一高档）
======================================================================
批次2（001 §159）改码：9 个原低档通道（入宅/开业/出行/安床/作灶/移徙/
入学/求医/签约）鸣吠日 12→15、鸣吠对日 8→10；另 2 处发射兜底字面量
（通用神煞/神煞基类）同步 15/10，彻底消灭双轨。

核验方式（不依赖外部推算，全程自洽）：
1. 15 通道 2026 全年总分实测；
2. Δ == 理论 Δ：遍历时按 checker 实际发射的鸣吠命中日累加
   （鸣吠日 +3/天、鸣吠对日 +2/天），与「实测总分 − 批次1 实测总分」严格相等；
3. 高档 5 通道（修造/动土/拆舍/嫁娶/安葬）Δ 必为 0（原即 15/10）；
4. 键数 1200、移徙 71 不变（本批只改值不改键）；
5. 全 14 事项键值统一：鸣吠日=15、鸣吠对日=10，无残留低档；
6. 哨兵 2026-11-04 入宅三时柱记录神煞分和（全链路 221→224 由
   tests/verify_wumu_buzhihua.py 核验，本探针不断言日课总分）。

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

# 批次1 落地后实测基线（probe_batch1_after.json，Commit1 已归档）
BASE_B1 = {
    '修造': -7972, '动土': -7866, '拆舍': -8882,
    '入宅': 3377, '移徙': 3377, '嫁娶': 214,
    '安葬': -2749, '安床': 5242, '出行': 6920,
    '开业': 7804, '作灶': -1315, '入学': 10158,
    '求医': 8856, '签约': 9306, '通用': 9321,
}

# 本批零变化通道（原即高档 15/10）
HIGH_CHANNELS = {'修造', '动土', '拆舍', '嫁娶', '安葬'}

Y0 = datetime.date(2026, 1, 1)
Y1 = datetime.date(2026, 12, 31)


def run_year(ev):
    """返回 (总分, 鸣吠日命中天次, 鸣吠对日命中天次, 理论Δ)。

    理论Δ：原高档 5 通道本批零变化→0；其余 9 通道按鸣吠日 +3/天、
    鸣吠对日 +2/天累计。
    """
    ck = get_checker(ev)
    tot = 0
    n_mf = n_mfd = 0
    d = Y0
    while d <= Y1:
        sz = calculate_sizhu(d, 10, 0)
        for s in ck.check(sz, []):
            tot += s['score']
            if s['name'] == '鸣吠日':
                n_mf += 1
            elif s['name'] == '鸣吠对日':
                n_mfd += 1
        d += datetime.timedelta(days=1)
    theo = 0 if ev in HIGH_CHANNELS else n_mf * 3 + n_mfd * 2
    return tot, n_mf, n_mfd, theo


def main():
    out = {'after': {}, 'base_b1': {}, 'delta': {}, 'theo': {},
           'mingfei': {}, 'match': {}, 'key_count': {}, 'sentinel': {}}
    fails = []

    for ev in EVENTS:
        v, n_mf, n_mfd, theo = run_year(ev)
        delta = v - BASE_B1[ev]
        ok = (delta == theo)
        out['after'][ev] = v
        out['base_b1'][ev] = BASE_B1[ev]
        out['delta'][ev] = delta
        out['theo'][ev] = theo
        out['mingfei'][ev] = {'鸣吠日': n_mf, '鸣吠对日': n_mfd}
        out['match'][ev] = ok
        mark = 'OK ' if ok else 'MISMATCH'
        print('[%s] %-2s 改后=%6d 批次1=%6d Δ=%+5d 理论Δ=%+5d'
              ' (鸣吠日×%d, 鸣吠对日×%d)' % (mark, ev, v, BASE_B1[ev],
                                              delta, theo, n_mf, n_mfd))
        if not ok:
            fails.append(ev)
        if ev in HIGH_CHANNELS and delta != 0:
            print('[FAIL] %s 属原高档通道，Δ 应为 0，实得 %+d' % (ev, delta))
            fails.append(ev + '_high')

    # 键数不变
    total_n = len(SHENSHA_SCORES)
    yi_n = sum(1 for (e, n) in SHENSHA_SCORES if e == '移徙')
    out['key_count'] = {'total': total_n, '移徙': yi_n}
    print('[键数] 总=%d（须=1200） 移徙=%d（须=71）' % (total_n, yi_n))
    if total_n != 1200 or yi_n != 71:
        fails.append('key_count')

    # 14 事项键值统一
    bad = []
    for ev in ('修造', '动土', '拆舍', '入宅', '移徙', '嫁娶', '安葬', '安床',
               '出行', '开业', '作灶', '入学', '求医', '签约'):
        a = shensha_score(ev, '鸣吠日')
        b = shensha_score(ev, '鸣吠对日')
        if a != 15 or b != 10:
            bad.append((ev, a, b))
    print('[键值] 14 事项统一 15/10：%s' % ('OK' if not bad else 'FAIL %s' % bad))
    if bad:
        fails.append('key_values')

    # 哨兵：只记录神煞分和，日课总分 221→224 由 verify_wumu_buzhihua 核验
    sd = datetime.date(2026, 11, 4)
    for hh in (10, 12, 18):
        sz = calculate_sizhu(sd, hh, 0)
        hits = [(s['name'], s['score']) for s in get_checker('入宅').check(sz, [])]
        mf = [(n, sc) for n, sc in hits if n in ('鸣吠日', '鸣吠对日')]
        day_tot = sum(sc for _, sc in hits)
        out['sentinel']['%02d:00' % hh] = {'shensha_subtotal': day_tot,
                                           'mingfei': mf}
        print('[哨兵 %02d:00] 神煞分和=%d 鸣吠命中=%s'
              % (hh, day_tot, mf if mf else '无'))

    jpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'probe_batch2_after.json')
    with open(jpath, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('[落盘] %s' % jpath)

    print('[复测结论] %s' % ('PASS' if not fails else 'FAIL: %s' % fails))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
