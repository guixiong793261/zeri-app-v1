# -*- coding: utf-8 -*-
"""
P2 删除候选 7 项删除批回归（2026-10-18，001 §122）
======================================================
拍板依据：三步走第三步「删除 commit 单独提交，保留有载确认项；
月害×动土/拆舍注明'本次逐字重提更正诊断'」。

验证面：
A. 行为层：730 天中抽样 2026 Q1 三个月，7 项（月害×入宅/出行/动土/拆舍、
   大时×作灶/安葬、五墓×作灶）零条目；有载确认项（月害×安葬/开业、
   大时×修造/开业/出行、五墓×安葬、往亡×出行/入宅）保持命中；
B. 键层：7 个 SHENSHA_SCORES 键不存在；有载键原值保留；
C. 源码层：基类排除集存在；6 文件死链块残留清零（防回填）；
D. 反向断言：通用通道（入学/求医/签约）月害/往亡现状不变（w6 拆分前基线）。

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
DELETED_KEYS = [
    ('动土', '月害'), ('拆舍', '月害'), ('入宅', '月害'), ('出行', '月害'),
    ('作灶', '大时'), ('安葬', '大时'), ('作灶', '五墓'),
]
KEPT_KEYS = [
    ('安葬', '月害'), ('安葬', '五墓'), ('出行', '大时'), ('修造', '大时'),
    ('开业', '大时'), ('开业', '月害'), ('动土', '大时'), ('动土', '五墓'),
    ('拆舍', '大时'), ('拆舍', '五墓'), ('出行', '五墓'), ('入宅', '大时'),
    ('入宅', '五墓'), ('往亡_placeholder',) if False else ('出行', '往亡'),
    ('入宅', '往亡'), ('安葬', '月害'),
]
for k in DELETED_KEYS:
    check('键 %s×%s 已删除' % k, k not in SHENSHA_SCORES)
for k in KEPT_KEYS:
    check('键 %s×%s 保留' % k, k in SHENSHA_SCORES)

# ============ C：源码层 ============
base_p = os.path.join(ROOT, 'modules', 'shensha', '神煞基类.py')
with open(base_p, encoding='utf-8') as f:
    base_src = f.read()
check('基类月害事项排除存在', "_p2_ev not in ('入宅', '出行', '动土', '拆舍')" in base_src)
check('基类大时事项排除存在', "_p2_ev not in ('作灶', '安葬')" in base_src)
check('基类五墓事项排除存在', "_p2_ev not in ('作灶',)" in base_src)

DEAD_STRINGS = [
    ('modules/shensha/出行神煞.py', '月害日不宜出行'),
    ('modules/shensha/动土神煞.py', '月害日，忌动土修造'),
    ('modules/shensha/拆舍神煞.py', '月害日忌拆舍'),
    ('modules/shensha/入宅神煞.py', '月害日不宜入宅'),
    ('modules/shensha/作灶神煞.py', '五墓日忌作灶'),
    ('modules/shensha/作灶神煞.py', '大时日忌作灶'),
    ('modules/shensha/安葬神煞.py', '大时凶日，不宜安葬'),
]
for rel, s in DEAD_STRINGS:
    p = os.path.join(ROOT, rel.replace('/', os.sep))
    with open(p, encoding='utf-8') as f:
        src = f.read()
    check('%s 死链描述串残留清零: %s' % (os.path.basename(rel), s[:12]), ("'" + s + "'") not in src)

# ============ A：行为层（2026 Q1 抽样） ============
EVENTS = ['嫁娶', '修造', '动土', '拆舍', '入宅', '开业', '出行', '安床', '作灶', '移徙', '入学', '求医', '签约', '安葬']
checkers = {ev: get_checker(ev) for ev in EVENTS}

DELETED = [('月害', '入宅'), ('月害', '出行'), ('月害', '动土'), ('月害', '拆舍'),
           ('大时', '作灶'), ('大时', '安葬'), ('五墓', '作灶')]
KEPT = [('月害', '安葬'), ('月害', '开业'), ('大时', '修造'), ('大时', '开业'),
        ('大时', '出行'), ('五墓', '安葬'), ('往亡', '出行'), ('往亡', '入宅')]
cnt_del = {k: 0 for k in DELETED}
cnt_kept = {k: 0 for k in KEPT}

d = datetime.date(2026, 1, 1)
end = datetime.date(2026, 3, 31)
while d <= end:
    sz = calculate_sizhu(d, 10, 0)
    for ev in EVENTS:
        names = set(_get(s, 'name') for s in checkers[ev].check(sz, []))
        for (sha, ev2) in DELETED:
            if ev == ev2 and sha in names:
                cnt_del[(sha, ev2)] += 1
        for (sha, ev2) in KEPT:
            if ev == ev2 and sha in names:
                cnt_kept[(sha, ev2)] += 1
    d += datetime.timedelta(days=1)

for k in DELETED:
    check('删除项 %s×%s 零条目 (Q1 x%d)' % (k[0], k[1], cnt_del[k]), cnt_del[k] == 0)
for k in KEPT:
    check('有载项 %s×%s 保持命中 (Q1 x%d)' % (k[0], k[1], cnt_kept[k]), cnt_kept[k] > 0)

# ============ D：反向断言（通用通道现状不变基线） ============
g_cnt = {('月害', '入学'): 0, ('月害', '求医'): 0, ('往亡', '求医'): 0}
d = datetime.date(2026, 1, 1)
while d <= end:
    sz = calculate_sizhu(d, 10, 0)
    for ev in ('入学', '求医'):
        names = set(_get(s, 'name') for s in checkers[ev].check(sz, []))
        for sha in ('月害', '往亡'):
            if (sha, ev) in g_cnt and sha in names:
                g_cnt[(sha, ev)] += 1
    d += datetime.timedelta(days=1)
for k, v in g_cnt.items():
    check('通用现状基线 %s×%s 保持命中 (Q1 x%d)' % (k[0], k[1], v), v > 0)

print('---')
if FAILS:
    print('FAILS=%d' % len(FAILS))
    for f in FAILS:
        print(' -', f)
    raise SystemExit(1)
print('ALL PASS')
raise SystemExit(0)
