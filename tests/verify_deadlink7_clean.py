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

2026-10-19 同步注记：十恶大败全删批（一档 1b6c0e2／二档 9035747，001 §139）
后，十恶大败日课扣分全系统归零——本脚本 W7 收为 W6（十恶大败移出），
基线/活链/计数断言同步；历史「基类日块:1711 活链」表述以该批为准失效。

2026-10-20 同步注记（病符批，001 §141）：病符日课普适注册全删（7 发射＋1 谓词
＋14 键）后，本脚本 W6 收为 **W5**（病符移出）；B 段「基类活链在位」中的病符项
**语义反转**为「病符全链清零」（基类/子类源码无可执行发射、入宅/移徙/嫁娶/安葬
通道 2026 全年病符计数=0），C 段 BASE 同步移出病符 (30,-12)。

验证面：
A. 源码层死链清除：入宅神煞.py 不再含 6 条子类发射行；注释留痕存在。
B. 活链保持：基类 5 条发射行源码在位（防误删活链）；病符反向断言全链清零。
C. 行为层零变化：入宅通道 2026 全年 5 煞计数=基线（30/31/31/30/59→31 见 §144）
   且分值一致（dump diff=0 已由本批 commit 实证）；
   §172 注记：丧门/吊客/官符/五鬼属年家 16 项置 0（识别展示保留），
   计数不变、分值基线同步置 0。
D. 多链同拦：入宅/移徙通道逐日同名神煞至多 1 条（无重复发射）；
   移徙通道 5 煞计数与入宅一致（同类同戳）。
E. 非入宅不波及：嫁娶通道 受死日/丧门 等上半年发射>0
   （基类受死日行对其余事项活链未删）；安葬通道受死日=0（受死日删除批，
   001 §145），其余四煞仍发射>0。

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

W6 = ['丧门', '吊客', '官符', '五鬼', '受死日']   # 病符已移出（001 §141，W6→W5）
# 基线（修改前 dump C:\Temp\emit_before.json，与盘点 §二一致；
# 十恶大败 (60,-30) 已于 2026-10-19 全删批移出本回归——001 §139；
# 病符 (30,-12) 已于 2026-10-20 病符批移出——001 §141；
# §172 P0 大清理（2026-10-24）：丧门/吊客/官符/五鬼属年家 16 项岁神方位，
# 日辰仅识别展示不计分——发射保留（计数不变）分值置 0）
BASE = {'丧门': (30, 0), '吊客': (31, 0),
        '官符': (31, 0), '五鬼': (30, 0), '受死日': (31, -15)}
# 受死日 59→31（2026-10-20 受死日收敛批：基类表B 改挂表A逐月表，与入宅月块同集合；
# 旧 59=表A∪表B 去重后合计数，现统一为表A 31 天）——001 §144
# 受死日分值 -22→-15（轻重层批次1 001 §158，B4 调档；发射兜底同步消双轨）

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
for n, s in [('受死日', -15), ('五鬼', -15), ('官符', -10),
             ('丧门', -15), ('吊客', -12)]:
    check("基类活链在位：_add_shensha('%s', %d" % (n, s),
          "_add_shensha('%s', %d," % (n, s) in b_src)
check('受死日基类行未删·仅注释登记（入宅注记在位）',
      '入宅通道注记（2026-10-19 死链清理同批 7 条之⑦' in b_src)

# B'：病符全链清零（病符批 2026-10-20，001 §141——原「基类活链在位」语义反转）
# 反转原因：病符日课普适注册经拍板删除（三库病符皆方位/年神语境，无日课普适
# 忌明文），基类发射行不再存在，原「活链箭头应可达」断言失去对象，改断清零。
# 注：墓碑注释按惯例留原实现（含 _add_shensha('病符' 字样），故断言须先剥注释。
_bingfu_srcs = [('入宅', z_src), ('基类', b_src)]
for _m in ('修造神煞', '动土神煞', '嫁娶神煞', '安床神煞', '安葬神煞', '通用神煞'):
    with open(os.path.join(ROOT, 'modules', 'shensha', _m + '.py'),
              encoding='utf-8') as f:
        _bingfu_srcs.append((_m, f.read()))
for _m, _src in _bingfu_srcs:
    _code = '\n'.join(ln.split('#', 1)[0] for ln in _src.splitlines())
    check("B' %s 无可执行病符发射" % _m, "_add_shensha('病符'" not in _code)

# ============ C：行为层零变化（入宅通道 2026 全年） ============
def _run(ev, start, end):
    ck = get_checker(ev)
    cnt = {n: 0 for n in W6}
    sc = {}
    dup = 0
    bf = 0      # 病符计数（001 §141 后应恒 0）
    d = start
    while d <= end:
        sz = calculate_sizhu(d, 10, 0)
        hits = ck.check(sz, [])
        names = [s['name'] for s in hits]
        if len(names) != len(set(names)):
            dup += 1
        for s in hits:
            if s['name'] == '病符':
                bf += 1
            if s['name'] in cnt:
                cnt[s['name']] += 1
                sc[s['name']] = s['score']
        d += datetime.timedelta(days=1)
    return cnt, sc, dup, bf


y0 = datetime.date(2026, 1, 1)
y1 = datetime.date(2026, 12, 31)
cnt, sc, dup_ru, bf_ru = _run('入宅', y0, y1)
for n in W6:
    c0, s0 = BASE[n]
    check('入宅通道 %s 计数=%d 分值=%d 与基线一致 (x%d/%d)'
          % (n, c0, s0, cnt[n], sc.get(n, 0)),
          cnt[n] == c0 and sc.get(n) == s0)
check("C' 入宅通道 2026 全年病符发射=0（实得 %d）" % bf_ru, bf_ru == 0)

# ============ D：多链同拦 ============
check('入宅通道逐日同名至多1条·无重复发射（重复日=%d）' % dup_ru, dup_ru == 0)
cnt_y, sc_y, dup_y, bf_y = _run('移徙', y0, y1)
check('移徙通道 5 煞计数与入宅逐项一致（同类同戳）',
      all(cnt_y[n] == BASE[n][0] for n in W6))
check('移徙通道逐日同名至多1条（重复日=%d）' % dup_y, dup_y == 0)
check("D' 移徙通道 2026 全年病符发射=0（实得 %d）" % bf_y, bf_y == 0)

# ============ E：非入宅不波及 ============
h0 = datetime.date(2026, 1, 1)
h1 = datetime.date(2026, 6, 30)
for ev, need_ss in (('嫁娶', True), ('安葬', False)):
    c2, _, _, bf2 = _run(ev, h0, h1)
    # 受死日删除批（2026-10-20，001 §145）：安葬通道受死日已删（三条不忌明载），
    # 其余四煞仍发射；嫁娶通道受死日保留（>0）。
    check('非入宅不波及：%s 通道 5 煞上半年仍发射（合计 %d；受死日 x%d）'
          % (ev, sum(c2.values()), c2['受死日']),
          sum(c2.values()) > 0
          and (c2['受死日'] > 0 if need_ss else c2['受死日'] == 0))
    check("E' %s 通道 上半年病符发射=0（实得 %d）" % (ev, bf2), bf2 == 0)

print('---')
print('CHECKS=%d PASS=%d FAIL=%d' % (_STAT['checks'], _STAT['pass'], len(FAILS)))
if FAILS:
    print('FAILS=%d' % len(FAILS))
    for f in FAILS:
        print(' -', f)
    raise SystemExit(1)
print('ALL PASS')
raise SystemExit(0)
