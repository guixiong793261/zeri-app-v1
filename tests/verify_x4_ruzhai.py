# -*- coding: utf-8 -*-
"""
x4 入宅般移映射删除批 回归（2026-10-19，001 §127）
======================================================
拍板依据：「x4 入宅删除面 9 条 选①全删，附五项执行条件」；
三步走：标注隔离 → 影响面快照 → 删除；条件 2 往亡双活链同拦，
条件 3 保留 3 条加独立明文标注且不得连带删。

判据（取证前冻结）：入宅/归火条目逐字含煞名方算独立明文；
三库零逐字明文者系般移【移徙同】忌列映射（001 §126 复核表）。

验证面：
A. 行为层（2026 全年）：8 删除候选 × 入宅 = 0
   （往亡/大时/五墓/月破/月刑/劫煞/灾煞/月煞）；
   天吏×入宅 恢复发射（口径收口批 2026-10-21，001 §153：卷十天吏忌列
   明文含「般移」+卷十一「般移【移徙同】」双明文，x4「三库零逐字明文」
   注释有误，001 §127 判定反转，取证稿 §1.8 判 ⚠️ 漏）。
   保留 3（归忌/月厌/四废）× 入宅 > 0。
B. 往亡双活链同拦（条件 2，w6 同款）：神煞基类.py 月块「往亡」与
   日块「往亡日」两处均带「入宅」排除（源码层 count≥2 防单链误删）。
C. 保留 3 不连带删（条件 3）：键 ('入宅','归忌')/('入宅','月厌')/
   ('入宅','四废') 保留；源码/行为均发射。
D. 非入宅不波及：嫁娶/安葬/开业 的 9 煞发射 > 0（仅入宅通道排除）。

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
from modules.事项标准 import SHENSHA_SCORES

# 天吏已移出删除候选（口径收口批 2026-10-21，001 §153 判定反转：恢复发射）
DEL8 = ['往亡', '大时', '五墓', '月破', '月刑', '劫煞', '灾煞', '月煞']
KEEP3 = ['归忌', '月厌', '四废']


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


# ============ A：行为层（2026 全年） ============
y0 = datetime.date(2026, 1, 1)
y1 = datetime.date(2026, 12, 31)
ru = _count('入宅', DEL8 + KEEP3 + ['天吏'], y0, y1)
for n in DEL8:
    check('删除候选 %s×入宅 零发射 (全年 x%d)' % (n, ru[n]), ru[n] == 0)
check('天吏×入宅 恢复发射 (全年 x%d，口径收口批 001 §153 反转)' % ru['天吏'],
      ru['天吏'] > 0)
check("恢复键 ('入宅','天吏') 存在", ('入宅', '天吏') in SHENSHA_SCORES)
for n in KEEP3:
    check('保留项 %s×入宅 保持发射 (全年 x%d)' % (n, ru[n]), ru[n] > 0)

# ============ B：往亡双活链同拦（源码层） ============
p = os.path.join(ROOT, 'modules', 'shensha', '神煞基类.py')
with open(p, encoding='utf-8') as f:
    base_src = f.read()
check('往亡双活链同拦：基类月块「往亡」带入宅排除',
      "self._is_wangwang(sizhu) and _p2_ev not in ('入宅',)" in base_src)
check('往亡双活链同拦：基类日块「往亡日」带入宅排除 (count>=2 防单链误删)',
      base_src.count("_is_wangwang(sizhu) and") >= 2)
check('往亡双活链同拦：日块往亡日发射行含入宅排除',
      "_add_shensha('往亡日', -20, '往亡日忌用')" in base_src
      and "getattr(self, '_std_event', None) != '入宅'" in base_src)

# ============ C：保留 3 不连带删 ============
for n in KEEP3:
    check("保留键 ('入宅',%r) 存在（防般移映射清理连带删）" % n,
          ('入宅', n) in SHENSHA_SCORES)

# ============ D：非入宅不波及（上半年） ============
h0 = datetime.date(2026, 1, 1)
h1 = datetime.date(2026, 6, 30)
for ev in ('嫁娶', '安葬', '开业'):
    c = _count(ev, DEL8, h0, h1)
    check('非入宅不波及：%s 的 8 煞仍发射（合计 %d）'
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
