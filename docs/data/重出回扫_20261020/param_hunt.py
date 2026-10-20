# -*- coding: utf-8 -*-
"""旧基线 wt_old2 参数反查：复现 309 / 246 / 259 三个历史总分。
用法:
  python C:\Temp\param_hunt.py r1    # 第1轮: 15事项×12时辰×2宅型×(空+12单事主)
  python C:\Temp\param_hunt.py r2    # 第2轮: 对无命中日期追加坐向变体与双事主组合
结果写 C:\Temp\param_hunt_result.json
"""
import datetime as dt
import io
import itertools
import json
import os
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r'C:\Temp\wt_old2'
OUT_JSON = r'C:\Temp\param_hunt_result.json'
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu          # noqa: E402
from modules.评分器 import calculate_score             # noqa: E402

EVENTS = ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '开业',
          '安床', '作灶', '安葬', '入学', '求医', '签约', '通用']
DATES = {'2026-11-04': 309, '2026-10-23': 246, '2026-06-01': 259}
HOURS = list(range(0, 24, 2))
HOUSE_TYPES = ['阳宅', '阴宅']
ZHIS = list('子丑寅卯辰巳午未申酉戌亥')
SHANXIANGS = ['子山午向', '午山子向', '卯山酉向', '酉山卯向',
              '乾山巽向', '巽山乾向', '艮山坤向', '坤山艮向',
              '壬山丙向', '丙山壬向', '甲山庚向', '庚山甲向']


def mk_owner(z):
    return {'name': '事主%s' % z, '生肖': z, '年支': z}


def single_owner_sets():
    return [[]] + [[mk_owner(z)] for z in ZHIS]


def double_owner_sets():
    return [[mk_owner(a), mk_owner(b)]
            for a, b in itertools.combinations_with_replacement('子午卯酉', 2)]


def total_of(r):
    sd = r.get('score_details') or {}
    return sd.get('总分', r.get('score'))


def level_of(r):
    return r.get('level') or (r.get('score_details') or {}).get('等级', '')


def hit_rec(ev, h, ht, owners, shan, total, level):
    return {'event': ev, 'hour': h, 'house_type': ht,
            'owners': owners if owners else [], 'shan_xiang': shan,
            'total': total, 'level': level}


def load_result():
    if os.path.exists(OUT_JSON):
        with open(OUT_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_result(res):
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)


def sweep(date_s, target, owner_sets, shan_list, space_desc, res):
    d = dt.date.fromisoformat(date_s)
    entry = res.setdefault(date_s, {'target': target, 'hits': [],
                                    'searched_space': '', 'exhausted': False})
    n, t0 = 0, time.time()
    sizhu_cache = {h: calculate_sizhu(d, h, 0) for h in HOURS}
    for ev in EVENTS:
        for h in HOURS:
            sz = sizhu_cache[h]
            for ht in HOUSE_TYPES:
                for owners in owner_sets:
                    for shan in shan_list:
                        n += 1
                        try:
                            r = calculate_score(sz, ev, owners=owners,
                                                house_type=ht, shan_xiang=shan)
                            total = total_of(r)
                        except Exception:
                            continue
                        if total == target:
                            rec = hit_rec(ev, h, ht, owners, shan, total, level_of(r))
                            entry['hits'].append(rec)
                            print('HIT %s %s h=%02d %s owners=%s shan=%s total=%s %s'
                                  % (date_s, ev, h, ht,
                                     [o.get('年支') for o in owners], shan,
                                     total, rec['level']), flush=True)
    if entry['searched_space']:
        entry['searched_space'] += '；'
    entry['searched_space'] += space_desc
    print('%s 扫描 %d 组合, 命中累计 %d, 用时 %.1fs'
          % (date_s, n, len(entry['hits']), time.time() - t0), flush=True)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'r1'
    res = load_result()
    if mode == 'r1':
        for date_s, target in DATES.items():
            sweep(date_s, target, single_owner_sets(), [None],
                  'R1: 15事项×12时辰×house_type{阳宅,阴宅}×owners{[] + 12单事主(年支子..亥)}',
                  res)
            save_result(res)
    elif mode == 'r2':
        for date_s, target in DATES.items():
            entry = res.get(date_s, {'target': target, 'hits': [],
                                     'searched_space': '', 'exhausted': False})
            res[date_s] = entry
            if entry['hits']:
                print('%s R1 已命中 %d 组, 跳过 R2' % (date_s, len(entry['hits'])), flush=True)
                continue
            sweep(date_s, target, [[]], SHANXIANGS,
                  'R2a: 15事项×12时辰×2宅型×owners=[]×12坐向变体', res)
            save_result(res)
            sweep(date_s, target, double_owner_sets(), [None],
                  'R2b: 15事项×12时辰×2宅型×双事主(子午卯酉两两组合10组)×无坐向', res)
            entry['exhausted'] = True
            save_result(res)
    save_result(res)
    print('DONE -> %s' % OUT_JSON, flush=True)


if __name__ == '__main__':
    main()
