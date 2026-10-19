# -*- coding: utf-8 -*-
"""
7 条同名重加死链清理回归（2026-10-19，非般移源补齐前置）
======================================================
拍板依据：「非般移源补齐主任务批准启动，但启动前先清 7 条同名重加死链」——
按 §120.3/§123.4/§127 同族处理，带双链/多链同拦回归；分值两侧一致、
零行为差（dump diff=0），确认后单独 commit。

清理面：
- 入宅神煞.py 子类日块 6 行死链→注释留痕（A1 式）：十恶大败/丧门/吊客/
  病符/官符/五鬼（活链分别为基类日块:1711、基类年块:1489/1491/1493/
  1485/1478，先到先得去重，两侧分值一致）。
- 神煞基类.py 日块受死日×入宅通道死链：仅注释登记（子类月块先行），
  不删行——对其余事项为活链。

验证面：
A. 源码层死链清除：入宅神煞.py 不再含 6 条子类发射行；注释留痕存在。
B. 活链保持：基类 7 条发射行源码在位（防误删活链）。
C. 行为层零变化：入宅通道 2026 全年 7 煞计数=基线（60/30/31/30/31/30/59）
   且分值一致（dump diff=0 已由本批 commit 实证）。
D. 多链同拦：入宅/移徙通道逐日同名神煞至多 1 条（无重复发射）；
   移徙通道 7 煞计数与入宅一致（同类同戳）。
E. 非入宅不波及：嫁娶通道 受死日/十恶大败/丧门 等上半年发射>0
   （基类受死日行对其余事项活链未删）。

退出码 0=全过 1=有失败。
"""
import io
import os
import sys
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []


def check(name, cond):
    print('[%s] %s' % ('PASS' if cond else 'FAIL', name))
    if not cond:
        FAILS.append(name)


sys.path.insert(0, ROOT)
from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker

W7 = ['十恶大败', '丧门', '吊客', '病符', '官符', '五鬼', '受死日']
# 基线（修改前 dump C:\Temp\emit_before.json，与盘点 §二一致）
BASE = {'十恶大败': (60, -30), '丧门': (30, -15), '吊客': (31, -12),
        '病符': (30, -12), '官符': (31, -10), '五鬼': (30, -15), '受死日': (59, -22)}

# ============ A：源码层死链清除 ============
p_z = os.path.join(ROOT, 'modules', 'shensha', '入宅神煞.py')
with open(p_z, encoding='utf-8') as f:
    z_src = f.read()
for n, s in [('十恶大败', -30), ('丧门', -15), ('吊客', -12),
             ('病符', -12), ('官符', -10), ('五鬼', -15)]:
    check("子类日块死链行已清除：_add_shensha('%s', %d" % (n, s),
          "_add_shensha('%s', %d," % (n, s) not in z_src)
check('死链清理注释留痕在位（同批7条）', z_src.count('死链清理（同批 7 条之') == 5
      and '死链清理（非般移源补齐前置' in z_src)

# ============ B：活链保持（源码层） ============
p_b = os.path.join(ROOT, 'modules', 'shensha', '神煞基类.py')
with open(p_b, encoding='utf-8') as f:
    b_src = f.read()
for n, s in [('十恶大败', -30), ('受死日', -22), ('五鬼', -15), ('官符', -10),
             ('丧门', -15), ('吊客', -12), ('病符', -12)]:
    check("基类活链在位：_add_shensha('%s', %d" % (n, s),
          "_add_shensha('%s', %d," % (n, s) in b_src)
check('受死日基类行未删·仅注释登记（入宅注记在位）',
      '入宅通道注记（2026-10-19 死链清理同批 7 条之⑦' in b_src)

# ============ C：行为层零变化（入宅通道 2026 全年） ============
def _run(ev, start, end):
    ck = get_checker(ev)
    cnt = {n: 0 for n in W7}
    sc = {}
    dup = 0
    d = start
    while d <= end:
        sz = calculate_sizhu(d, 10, 0)
        hits = ck.check(sz, [])
        names = [s['name'] for s in hits]
        if len(names) != len(set(names)):
            dup += 1
        for s in hits:
            if s['name'] in cnt:
                cnt[s['name']] += 1
                sc[s['name']] = s['score']
        d += datetime.timedelta(days=1)
    return cnt, sc, dup


y0 = datetime.date(2026, 1, 1)
y1 = datetime.date(2026, 12, 31)
cnt, sc, dup_ru = _run('入宅', y0, y1)
for n in W7:
    c0, s0 = BASE[n]
    check('入宅通道 %s 计数=%d 分值=%d 与基线一致 (x%d/%d)'
          % (n, c0, s0, cnt[n], sc.get(n, 0)),
          cnt[n] == c0 and sc.get(n) == s0)

# ============ D：多链同拦 ============
check('入宅通道逐日同名至多1条·无重复发射（重复日=%d）' % dup_ru, dup_ru == 0)
cnt_y, sc_y, dup_y = _run('移徙', y0, y1)
check('移徙通道 7 煞计数与入宅逐项一致（同类同戳）',
      all(cnt_y[n] == BASE[n][0] for n in W7))
check('移徙通道逐日同名至多1条（重复日=%d）' % dup_y, dup_y == 0)

# ============ E：非入宅不波及 ============
h0 = datetime.date(2026, 1, 1)
h1 = datetime.date(2026, 6, 30)
for ev in ('嫁娶', '安葬'):
    c2, _, _ = _run(ev, h0, h1)
    check('非入宅不波及：%s 通道 7 煞上半年仍发射（合计 %d；受死日 x%d）'
          % (ev, sum(c2.values()), c2['受死日']),
          sum(c2.values()) > 0 and c2['受死日'] > 0)

print('---')
if FAILS:
    print('FAILS=%d' % len(FAILS))
    for f in FAILS:
        print(' -', f)
    raise SystemExit(1)
print('ALL PASS')
raise SystemExit(0)
