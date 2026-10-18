# -*- coding: utf-8 -*-
"""
P2 部分匹配拆分回归（2026-10-18，001 §123）
======================================================
拍板依据：「部分匹配 2 项拆分处理：有载子项保留，无载子项（入学）
列入删除候选；'通用'事项须逐子项对勘后再定，不整项处理；
与删除候选 7 项分开 commit。」

d6 逐子项判定事实（docs/月家P2_月害大时往亡五墓_续取证.md §六）：
- 月害×通用：求医✅ 签约✅（立劵交易条） 入学❌（入学条无月害）
- 往亡×通用：求医✅（求医疗病条+陈书 p696） 入学❌ 签约❌（立劵交易条无）
删除子项：月害×入学、往亡×入学、往亡×签约（无载）；保留：月害×求医/
签约、往亡×求医。

验证面：
A. 行为层（2026 Q1 实测）：月害×入学=0、往亡×入学=0、往亡×签约=0；
   月害×求医/签约>0、往亡×求医>0（有载子项保留）；
B. 键层：('入学','月害')/('入学','往亡')/('签约','往亡') 已删；
   ('求医','月害')/('求医','往亡')/('签约','月害') 保留；
C. 源码层：通用神煞.py 月害/往亡发射带 _std_event 拆分条件
   （往亡为月块「往亡」+日块「往亡日」归一同名双活链，两处同拦）；
D. 反向断言：通用大时/五墓现状不变（大时×通用、五墓×通用三事项
   全有载，不属拆分面）。

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
    tag = 'PASS' if cond else 'FAIL'
    print('[%s] %s' % (tag, name))
    if not cond:
        FAILS.append(name)


def _get(s, k):
    return s.get(k) if isinstance(s, dict) else getattr(s, k, None)


sys.path.insert(0, ROOT)
from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.事项标准 import SHENSHA_SCORES

# ============ B：键层 ============
for k in [('入学', '月害'), ('入学', '往亡'), ('签约', '往亡')]:
    check('键 %s×%s 已删除' % k, k not in SHENSHA_SCORES)
for k in [('求医', '月害'), ('求医', '往亡'), ('签约', '月害')]:
    check('键 %s×%s 保留' % k, k in SHENSHA_SCORES)

# ============ C：源码层 ============
p = os.path.join(ROOT, 'modules', 'shensha', '通用神煞.py')
with open(p, encoding='utf-8') as f:
    src = f.read()
check('月害发射带入学拆分条件', "and getattr(self, '_std_event', None) != '入学'" in src)
check('往亡发射双链拆分条件(月块+日块)', src.count("not in ('入学', '签约')") >= 2)

# ============ A：行为层（2026 Q1） ============
checkers = {ev: get_checker(ev) for ev in ('入学', '求医', '签约')}
cnt = {
    ('月害', '入学'): 0, ('月害', '求医'): 0, ('月害', '签约'): 0,
    ('往亡', '入学'): 0, ('往亡', '求医'): 0, ('往亡', '签约'): 0,
    ('大时', '入学'): 0, ('大时', '求医'): 0, ('大时', '签约'): 0,
    ('五墓', '入学'): 0, ('五墓', '求医'): 0, ('五墓', '签约'): 0,
}
d = datetime.date(2026, 1, 1)
end = datetime.date(2026, 3, 31)
while d <= end:
    sz = calculate_sizhu(d, 10, 0)
    for ev, ck in checkers.items():
        names = set(_get(s, 'name') for s in ck.check(sz, []))
        for (sha, ev2) in cnt:
            if ev == ev2 and sha in names:
                cnt[(sha, ev2)] += 1
    d += datetime.timedelta(days=1)

for k in [('月害', '入学'), ('往亡', '入学'), ('往亡', '签约')]:
    check('删除子项 %s×%s 零条目 (Q1 x%d)' % (k[0], k[1], cnt[k]), cnt[k] == 0)
for k in [('月害', '求医'), ('月害', '签约'), ('往亡', '求医')]:
    check('保留子项 %s×%s 保持命中 (Q1 x%d)' % (k[0], k[1], cnt[k]), cnt[k] > 0)
for k in [('大时', '入学'), ('大时', '求医'), ('大时', '签约'),
          ('五墓', '入学'), ('五墓', '求医'), ('五墓', '签约')]:
    check('拆分面外现状 %s×%s 保持命中 (Q1 x%d)' % (k[0], k[1], cnt[k]), cnt[k] > 0)

print('---')
if FAILS:
    print('FAILS=%d' % len(FAILS))
    for f in FAILS:
        print(' -', f)
    raise SystemExit(1)
print('ALL PASS')
raise SystemExit(0)
