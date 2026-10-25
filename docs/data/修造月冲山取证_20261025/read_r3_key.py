# -*- coding: utf-8 -*-
"""核读 scan_r3.json：输出协纪造命体用/考原/陈书关键命中"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open(r'C:\Temp\scan_r3.json', encoding='utf-8'))
h = d['theme_hits']
n = 0
for x in h:
    if x['库'] == '陈书' or x['出处'] in ('279251', '279252'):
        n += 1
        print(f"[{x['库']} {x['出处']}] {x['原文'][:110]}")
        if x['库'] == '协纪' and x['出处'] in ('279251', '279252'):
            print(f"    前: {x['前'][:80]}")
            print(f"    后: {x['后'][:80]}")
print('共', n, '条')
