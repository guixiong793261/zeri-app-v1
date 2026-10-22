# -*- coding: utf-8 -*-
"""
轻重层批次1·落地前前置探针（只读，monkey-patch 进程内模拟，主仓零改动）
======================================================================
目的：按拍板 B 组 10 项新分值，实测 2026 全年 15 通道总分变化，
     重点核对三个冻结通道（入宅/移徙/嫁娶）与哨兵日、移徙键数。

方法：全表快照 → 就地改 10 神煞全部注册键 + 新增 ('*','月德合')=15
     → 跑 15 通道（10:00 时柱）→ 还原快照断言。

退出码 0=跑完且基线复核通过；1=基线复核失败（说明发射面与 JSON 不符）。
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

# B 组 10 项拍板新值（B5 月德合走通配键，不属实键）
NEW = {'月厌': -25, '月刑': -20, '月害': -12, '土王用事': -20, '受死日': -15,
       '往亡': -15, '归忌': -10, '地囊': -20, '八专': -12}

Y0 = datetime.date(2026, 1, 1)
Y1 = datetime.date(2026, 12, 31)


def run_year(ev):
    ck = get_checker(ev)
    tot = 0
    per = {}
    d = Y0
    while d <= Y1:
        sz = calculate_sizhu(d, 10, 0)
        for s in ck.check(sz, []):
            tot += s['score']
            per[s['name']] = per.get(s['name'], 0) + s['score']
        d += datetime.timedelta(days=1)
    return tot, per


def run_day(ev, day, hh):
    sz = calculate_sizhu(day, hh, 0)
    return [(s['name'], s['score']) for s in get_checker(ev).check(sz, [])]


def main():
    out = {'baseline': {}, 'after': {}, 'delta': {}, 'per_shensha_delta': {},
           'changed_keys': [], 'sentinel': {}, 'key_count': {}}

    # ---- 改前基线 ----
    base = {ev: run_year(ev) for ev in EVENTS}
    for ev in EVENTS:
        out['baseline'][ev] = base[ev][0]
    print('[基线] 入宅=%d 移徙=%d 嫁娶=%d' % (base['入宅'][0], base['移徙'][0], base['嫁娶'][0]))

    # ---- 进程内改分 ----
    snap = dict(SHENSHA_SCORES)
    for (e, n), v in list(SHENSHA_SCORES.items()):
        if n in NEW:
            out['changed_keys'].append([e, n, v, NEW[n]])
            SHENSHA_SCORES[(e, n)] = NEW[n]
    SHENSHA_SCORES[('*', '月德合')] = 15  # B5 通配键方案（不增移徙实键）

    yi_n = sum(1 for (e, n) in SHENSHA_SCORES if e == '移徙')
    out['key_count']['移徙'] = yi_n
    print('[键数] 移徙=%d（须=71）' % yi_n)
    print("[通配] shensha_score('移徙','月德合')=%r（须=15）" % shensha_score('移徙', '月德合'))
    print("[通配] shensha_score('嫁娶','月德合')=%r（须=15）" % shensha_score('嫁娶', '月德合'))

    # ---- 改后实测 ----
    after = {ev: run_year(ev) for ev in EVENTS}
    for ev in EVENTS:
        out['after'][ev] = after[ev][0]
        out['delta'][ev] = after[ev][0] - base[ev][0]
    print('[改后] 入宅=%d 移徙=%d 嫁娶=%d' % (after['入宅'][0], after['移徙'][0], after['嫁娶'][0]))
    print('[Δ]   入宅=%+d 移徙=%+d 嫁娶=%+d' % (out['delta']['入宅'], out['delta']['移徙'], out['delta']['嫁娶']))

    # 逐神煞贡献（改后分值和 − 改前分值和，按发射名归集）
    names = set(NEW) | {'月德合'}
    for ev in EVENTS:
        out['per_shensha_delta'][ev] = {
            n: after[ev][1].get(n, 0) - base[ev][1].get(n, 0)
            for n in names if after[ev][1].get(n, 0) != base[ev][1].get(n, 0)}
    for ev in ('入宅', '移徙', '嫁娶'):
        print('[%s 逐项Δ] %s' % (ev, json.dumps(out['per_shensha_delta'][ev], ensure_ascii=False)))

    # ---- 哨兵：2026-11-04 入宅 12:00 命中清单须无 B 组项 ----
    sd = datetime.date(2026, 11, 4)
    for hh in (10, 12, 18):
        hits = run_day('入宅', sd, hh)
        touched = [(n, s) for n, s in hits if n in names]
        out['sentinel']['%02d:00' % hh] = {'hits': hits, 'touched': touched}
        print('[哨兵 %02d:00] 命中 B 组/月德合：%s' % (hh, touched if touched else '无'))

    # ---- 还原并断言 ----
    SHENSHA_SCORES.clear()
    SHENSHA_SCORES.update(snap)
    assert dict(SHENSHA_SCORES) == snap

    jpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'probe_batch1_preview.json')
    with open(jpath, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('[落盘] %s' % jpath)

    ok = (base['入宅'][0] == 3188 and base['移徙'][0] == 3188 and base['嫁娶'][0] == -153
          and yi_n == 71)
    print('[基线复核] %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
