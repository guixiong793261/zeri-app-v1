# -*- coding: utf-8 -*-
"""卷十一·用事 逐事宜忌解析（只读）：产出 8 项在每事项的 宜/忌/无 标记。"""
import io, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
t = open(r'C:\Temp\xj_full\279229.txt', encoding='utf-8').read()
body = t[t.find('\n祭祀\n\n宜天德') + 1:]
lines = [x.strip() for x in body.split('\n') if x.strip()]

ITEMS = ['天恩', '不将', '飞廉', '伏断', '反支', '月德合', '归忌', '天吏']
out = []
cur = None
for ln in lines:
    if ln.startswith(('宜', '忌', '又', '官日守日相日', '按')):
        if cur is None:
            continue
        if ln.startswith('宜'):
            cur['宜'] += '｜' + ln
        elif ln.startswith('忌'):
            cur['忌'] += '｜' + ln
        continue
    cur = {'事情': ln, '宜': '', '忌': ''}
    out.append(cur)

for r in out:
    r['mark'] = {}
    for it in ITEMS:
        r['mark'][it] = '宜' if it in r['宜'] else ('忌' if it in r['忌'] else '—')

print('事项块数', len(out))
for it in ITEMS:
    yi_list = [r['事情'] for r in out if r['mark'][it] == '宜']
    ji_list = [r['事情'] for r in out if r['mark'][it] == '忌']
    print('\n==', it, '｜宜', len(yi_list), '｜忌', len(ji_list))
    print('  宜:', '、'.join(yi_list) if yi_list else '无')
    print('  忌:', '、'.join(ji_list) if ji_list else '无')

json.dump(out, open(r'C:\Temp\yongshi8.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n事项名:', '、'.join(r['事情'] for r in out))
