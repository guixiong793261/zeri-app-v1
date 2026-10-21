# -*- coding: utf-8 -*-
"""省族表源快验：月破/月刑/月害/太岁 12×12 穷举（只读）
输出：每月（节气月支）各日支命中矩阵 + 典载关系期望对照 + 差异清单。
"""
import sys, io, datetime, json
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')
import sxtwl
from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.shensha.神煞基类 import ShenShaChecker

ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
JQ_MAP = ((20, '子'), (22, '丑'), (0, '寅'), (2, '卯'), (4, '辰'), (6, '巳'),
          (8, '午'), (10, '未'), (12, '申'), (14, '酉'), (16, '戌'), (18, '亥'))


def month_zhi_at(d, hour=12):
    cur = datetime.datetime(d.year, d.month, d.day, hour, 0)
    pts = []
    for y in (d.year - 1, d.year):
        jq = sxtwl.getJieQiByYear(y)
        for idx, mz in JQ_MAP:
            dd = sxtwl.JD2DD(jq[idx].jd)
            pts.append((datetime.datetime(int(dd.Y), int(dd.M), int(dd.D),
                                          int(dd.h), int(dd.m), int(dd.s)), mz))
    pts.sort()
    mz = '子'
    for t, z in pts:
        if cur >= t:
            mz = z
        else:
            break
    return mz


def chong(z):
    return ZHI[(ZHI.index(z) + 6) % 12]


XING = {'子': '卯', '卯': '子', '寅': '巳', '巳': '申', '申': '寅',
        '丑': '戌', '戌': '未', '未': '丑', '辰': '辰', '午': '午', '酉': '酉', '亥': '亥'}
HAI = {'子': '未', '丑': '午', '寅': '巳', '卯': '辰', '辰': '卯', '巳': '寅',
       '午': '丑', '未': '子', '申': '亥', '酉': '戌', '戌': '酉', '亥': '申'}

NAMES = {'月破': lambda m, d: d == chong(m),
         '月刑': lambda m, d: d == XING[m],
         '月害': lambda m, d: d == HAI[m]}

chk = get_checker('通用')
base = ShenShaChecker()
d0, d1 = datetime.date(2026, 1, 1), datetime.date(2026, 12, 31)
days = []
d = d0
while d <= d1:
    mz = month_zhi_at(d)
    sz = calculate_sizhu(d, 10, 0)
    out = chk.check(sz, [])
    names = {o['name']: o['score'] for o in out}
    days.append((d.isoformat(), mz, sz['day_zhi'], sz['year_zhi'],
                 {n: names.get(n) for n in ('月破', '月刑', '月害', '太岁')}))
    d += datetime.timedelta(days=1)

print('=== A. 逐日命中（仅列命中日） ===')
for n in ('月破', '月刑', '月害', '太岁'):
    hit = [(x[0], x[1], x[2], x[4][n]) for x in days if x[4][n] is not None]
    print(f'-- {n}: {len(hit)} 天')
    for h in hit[:80]:
        print('   ', h)

print()
print('=== B. 12×12 矩阵（月建×日支，X=命中） ===')
for n in ('月破', '月刑', '月害'):
    mat = {}
    for x in days:
        mat.setdefault(x[1], set()).add(x[2]) if x[4][n] is not None else None
    print(f'-- {n}')
    print('      ' + ' '.join(t for t in ZHI))
    bad = []
    for m in ZHI:
        got = mat.get(m, set())
        exp = {HAI[m]} if n == '月害' else ({XING[m]} if n == '月刑' else {chong(m)})
        row = ''
        for dz in ZHI:
            row += (' X' if dz in got else ' .')
        mark = '' if got == exp else f'  << 差: 实际{sorted(got)} 期望{sorted(exp)}'
        if mark:
            bad.append((m, sorted(got), sorted(exp)))
        print(f'  月建{m} {row}{mark}')
    print(f'  差异月数: {len(bad)}')

print()
print('=== C. 太岁（年支=2026 午，日支午） ===')
ts = [x for x in days if x[4]['太岁'] is not None]
print('命中天数', len(ts), '年支集合', sorted({x[3] for x in days}))
print('命中日支集合', sorted({x[2] for x in ts}))

print()
print('=== D. 逐月命中天数（月破/月刑/月害） ===')
cnt = {}
for x in days:
    cnt.setdefault(x[1], {n: 0 for n in ('月破', '月刑', '月害')})
    for n in cnt[x[1]]:
        if x[4][n] is not None:
            cnt[x[1]][n] += 1
for m in ZHI:
    print(m, cnt.get(m))

json.dump([{'date': x[0], 'mz': x[1], 'dz': x[2], 'yz': x[3], 'hit': x[4]} for x in days],
          open(r'C:\Temp\kuaiyan_2026.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nJSON -> C:\\Temp\\kuaiyan_2026.json')
