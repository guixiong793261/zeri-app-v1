# -*- coding: utf-8 -*-
"""精确核读：1)「月冲山」三字连用三库命中  2) 陈书冲山定局页  3) 协纪279252月破山原文"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def norm(t):
    return re.sub(r'\s+', '', t or '')

print('=== 1) 「月冲山」三字连用 ===')
for lib, d in (('协纪', r'C:\Temp\xj_full'), ('考原', r'C:\Temp\xl_full')):
    for fn in sorted(os.listdir(d)):
        if fn.endswith('.txt'):
            t = open(os.path.join(d, fn), encoding='utf-8', errors='ignore').read()
            if '月冲山' in t:
                for m in re.finditer('月冲山', t):
                    s = max(0, m.start()-25); e = min(len(t), m.end()+25)
                    print(f'  [{lib} {fn[:-4]}] ...{t[s:e]}...')
czx = json.load(open(r'C:\Temp\czx_full\czx_pages.json', encoding='utf-8'))
for page, text in czx:
    if text and '月冲山' in text:
        s = max(0, text.find('月冲山')-30); e = min(len(text), text.find('月冲山')+30)
        print(f'  [陈书 p{page}] ...{text[s:e]}...')

print('\n=== 2) 陈书「冲山」定局页（竖造除X月冲山不载） ===')
for page, text in czx:
    if text and '冲山不載' in text:
        s = text.find('冲山不載')
        print(f'  [陈书 p{page}] ...{text[max(0,s-60):s+20]}...')

print('\n=== 3) 协纪 279252「月破山」完整原文（含前后文） ===')
t = open(r'C:\Temp\xj_full\279252.txt', encoding='utf-8', errors='ignore').read()
for m in re.finditer('月破山', t):
    s = max(0, m.start()-60); e = min(len(t), m.end()+60)
    print(f'  ...{t[s:e]}...')

print('\n=== 4) 协纪 279252「月建可坐不可向」段 ===')
for m in re.finditer('月建可坐', t):
    s = max(0, m.start()-80); e = min(len(t), m.end()+40)
    print(f'  ...{t[s:e]}...')
