# -*- coding: utf-8 -*-
"""从 weight_scan.json 提取「协纪」力度句（只读，供裁定表引用原文）。"""
import io
import json
import os
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

P = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 'weight_scan.json')
d = json.load(open(P, encoding='utf-8'))
WANT = sys.argv[1:] or ['月厌', '月害', '月煞', '大时', '往亡', '四废', '五墓',
                        '八专', '四忌', '三煞', '鸣吠日', '鸣吠对', '土府',
                        '土王用事', '地囊', '受死日', '红嘴朱雀']
for nm in WANT:
    v = d['terms'].get(nm)
    if not v:
        print('\n### %s  无词条' % nm)
        continue
    print('\n### %s  命中%d 力度句%d' % (nm, v['total'], v['marked_total']))
    n = 0
    for h in v['hits']:
        if h['book'] != '协纪':
            continue
        print('  [%s] %s' % (h['chap'], h['ctx'][:420]))
        n += 1
        if n >= 9:
            break
