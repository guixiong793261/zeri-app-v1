# -*- coding: utf-8 -*-
"""取证命中上下文查看器（只读，ASCII 别名避免 PowerShell 中文参数乱码）"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DATA = os.path.join(os.path.dirname(__file__), 'scan_p0.json')
d = json.load(open(DATA, encoding='utf-8'))

ALIAS = {
    'gc': '孤辰', 'gs': '寡宿', 'gcg': '孤辰寡宿', 'hf': '黄幡', 'bw': '豹尾',
    'ws': '亡神', 'dh': '大祸', 'sx': '岁刑', 'sh': '岁害', 'ls': '力士',
    'cg': '蚕官', 'xg': '畜官', 'wg': '五鬼', 'pb': '破败', 'gf': '官符',
    'sm': '丧门', 'dk': '吊客', 'th': '天耗', 'di': '地耗', 'da': '大耗',
    'xa': '小耗', 'tf': '土府', 'tfu': '土符', 'yp': '月破', 'kg': '魁罡',
}

term = ALIAS.get(sys.argv[1], sys.argv[1])
kw = sys.argv[2] if len(sys.argv) > 2 else ''
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 60

n = 0
for h in d['hits']:
    if h['term'] != term:
        continue
    if kw and kw not in h['ctx']:
        continue
    n += 1
    if n > limit:
        break
    print('[%s %s] %s' % (h['book'][:4], h['chap'], h['ctx']))
    print('-' * 100)
print('shown', n)
