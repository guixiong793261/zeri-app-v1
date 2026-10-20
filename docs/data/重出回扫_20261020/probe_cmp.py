# -*- coding: utf-8 -*-
"""四日期入宅日课复算（同参数新旧对照）。用法：python probe_cmp.py <ROOT>"""
import datetime as dt
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = sys.argv[1]
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.评分器 import calculate_score

TARGETS = ['2026-11-04', '2026-10-23', '2026-07-24', '2026-06-01']
WATCH = ('土符', '红嘴朱雀', '受死日', '十恶大败', '岁破', '病符',
         '天刑', '自刑', '天吏', '八专', '四击', '大煞', '吉庆')

out = {}
for s in TARGETS:
    d = dt.date.fromisoformat(s)
    sz = calculate_sizhu(d, 12, 0)
    ck = get_checker('入宅')
    rows = ck.check(sz, [])
    res = calculate_score(sz, '入宅', owners=[], house_type='阳宅')
    sd = res.get('score_details') or {}
    out[s] = {
        'pillars': '%s%s %s%s %s%s %s%s' % (
            sz['year_gan'], sz['year_zhi'], sz['month_gan'], sz['month_zhi'],
            sz['day_gan'], sz['day_zhi'], sz['hour_gan'], sz['hour_zhi']),
        'shensha': [[r.get('name'), r.get('score', 0)] for r in rows],
        'ss_sum': sum(r.get('score', 0) for r in rows),
        'total': sd.get('总分'),
        'score': res.get('score'),
        'level': res.get('level'),
        'details': {k: sd.get(k) for k in ('正五行', '神煞', '黄道', '月令',
                                          '事主', '太阳太阴', '总分')},
        'watch': {n: v for n, v in
                  [(r.get('name'), r.get('score', 0)) for r in rows]
                  if n in WATCH},
    }
    print('%s | %s | 神煞合计 %+d | 总分 %s | %s' % (
        s, out[s]['pillars'], out[s]['ss_sum'], out[s]['total'], out[s]['level']))
    print('    条目: ' + ' '.join('%s%+d' % (n, v) for n, v in out[s]['shensha']))
    print('    分项: ' + json.dumps(out[s]['details'], ensure_ascii=False))
    print('    关注煞: ' + (json.dumps(out[s]['watch'], ensure_ascii=False)
                            if out[s]['watch'] else '无'))

print('\nJSON_BEGIN')
print(json.dumps(out, ensure_ascii=False))
