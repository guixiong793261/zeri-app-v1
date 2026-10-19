# -*- coding: utf-8 -*-
"""
移徙删候10键批·删除回归（2026-10-19，三步走第三步）
======================================================
拍板依据：「移徙修复方向选A」条件①——先删10键再改查找；
条件④——x4/P2 删除项在移徙通道保持删除，不得因后续三级查找「通配」复活。
判据（与 x4/P2 同）：9键＝x4已删（4226267，三库零逐字明文系般移映射）；
月害＝P2已删（001 §122/§125）。快照基线：bb196e7 §六。

验证面：
A. 10键不存在：('移徙',n) ∉ SHENSHA_SCORES（n∈D10）。
B. 删除前后同值：shensha_score('移徙',n)＝8×None＋月刑-15＋月害-15
   （快照 bb196e7 §二固化；月刑/月害经 ('*',名) 通配，与移徙键无关）。
C. 移徙通道不复活：10煞×移徙 2026 全年零发射（谓词侧 x4 入宅排除不动）。
D. 77共有键评分零变化：移徙块现剩77键（十恶大败键随 2026-10-19 全删批移除），
   逐键 ('移徙',n)值==('入宅',n)值
   且 shensha_score('移徙',n)==该值（与删除前 47b7dd7 §3.1 一致）。
E. 非移徙不波及：('入宅',10名) 仍不存在（x4删除保持）；通配键15个不变；
   嫁娶/安葬/开业 10煞上半年发射>0（x4 排除仅入宅通道，verify_x4 D段同款）。

退出码 0=全过 1=有失败。
"""
import io
import os
import sys
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []


_STAT = {'checks': 0, 'pass': 0}


def check(name, cond):
    """断言计数就地自汇报（001 §135.4：计数以脚本自报为准，不依赖 Shell 回显）。"""
    _STAT['checks'] += 1
    if cond:
        _STAT['pass'] += 1
    print('[%s] %s' % ('PASS' if cond else 'FAIL', name))
    if not cond:
        FAILS.append(name)


sys.path.insert(0, ROOT)
from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.事项标准 import SHENSHA_SCORES, shensha_score

D10 = ['月破', '劫煞', '灾煞', '往亡', '月煞', '月刑', '天吏', '大时', '五墓', '月害']
# 快照 bb196e7 §二 固化的删除前返回值（前后同值基线）
EXPECT = {'月破': None, '劫煞': None, '灾煞': None, '往亡': None, '月煞': None,
          '月刑': -15, '天吏': None, '大时': None, '五墓': None, '月害': -15}


def _count(ev, names, start, end):
    ck = get_checker(ev)
    cnt = {n: 0 for n in names}
    d = start
    while d <= end:
        sz = calculate_sizhu(d, 10, 0)
        present = set(s['name'] for s in ck.check(sz, []))
        for n in names:
            if n in present:
                cnt[n] += 1
        d += datetime.timedelta(days=1)
    return cnt


# ============ A：10键不存在 ============
for n in D10:
    check("删除键 ('移徙',%r) 不存在" % n, ('移徙', n) not in SHENSHA_SCORES)
yi = {k: v for k, v in SHENSHA_SCORES.items() if k[0] == '移徙'}
check('移徙块键数=77（88-10-1，十恶大败全删批同步）', len(yi) == 77)

# ============ B：删除前后同值（快照基线） ============
for n in D10:
    check("shensha_score('移徙',%r)=%r 与删除前同值" % (n, EXPECT[n]),
          shensha_score('移徙', n) == EXPECT[n])

# ============ C：移徙通道不复活（2026 全年） ============
y0 = datetime.date(2026, 1, 1)
y1 = datetime.date(2026, 12, 31)
ru = _count('移徙', D10, y0, y1)
for n in D10:
    check('移徙通道 %s 全年零发射·不复活 (x%d)' % (n, ru[n]), ru[n] == 0)

# ============ D：77共有键评分零变化 ============
same = all(SHENSHA_SCORES.get(('入宅', n)) == v and shensha_score('移徙', n) == v
           for (ev, n), v in yi.items())
check('77键逐键 (移徙,n)==(入宅,n) 且 shensha_score 同值（评分零变化）', same)

# ============ E：非移徙不波及 ============
for n in D10:
    check("('入宅',%r) 仍不存在（x4/P2删除保持）" % n,
          ('入宅', n) not in SHENSHA_SCORES)
wild = sum(1 for k in SHENSHA_SCORES if k[0] == '*')
check('通配(*,名)键数=15 不变（快照 §四）', wild == 15)
h0 = datetime.date(2026, 1, 1)
h1 = datetime.date(2026, 6, 30)
for ev in ('嫁娶', '安葬', '开业'):
    c = _count(ev, D10, h0, h1)
    check('非移徙不波及：%s 的 10 煞仍发射（上半年合计 %d）'
          % (ev, sum(c.values())), sum(c.values()) > 0)

print('---')
print('CHECKS=%d PASS=%d FAIL=%d' % (_STAT['checks'], _STAT['pass'], len(FAILS)))
if FAILS:
    print('FAILS=%d' % len(FAILS))
    for f in FAILS:
        print(' -', f)
    raise SystemExit(1)
print('ALL PASS')
raise SystemExit(0)
