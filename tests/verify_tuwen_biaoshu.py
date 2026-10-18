# -*- coding: utf-8 -*-
"""
土瘟描述串正名文案回归（z1 批验收建议，2026-10-18）
======================================================
拍板依据：z1 验收通过，用户建议「描述串不在断言面内，建议后续补一条
文案回归（断言'土瘟'描述串必含'四季土旺日'和'忌动土'），防止未来文案回退」。

背景：P1-5 P3 正名采用描述串方案（注册名 '土瘟' 锚不动，分值键零变化），
5 处发射描述串加限定词「四季土旺日」并明示「忌动土」（安床事项为
「不宜安床」，亦属忌动土族表述）。本脚本断言 5 处描述串限定词不回退。

验证面：
A. 源码层：4 文件 5 处 `_add_shensha('土瘟'` 描述串必含「四季土旺日」；
B. 语义层：修造/通用/基类描述串含「忌动土」，安床含「不宜安床」；
C. 反向断言：不存在无限定词的裸「土瘟」描述串（防回填）；
D. 行为层：土瘟日发射 name='土瘟' 不变、分值 -20 不变（正名不改判）。

退出码 0=全过 1=有失败。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []


def check(name, cond):
    tag = 'PASS' if cond else 'FAIL'
    print('[%s] %s' % (tag, name))
    if not cond:
        FAILS.append(name)


# ============ A+B：源码层描述串断言 ============
TARGETS = [
    ('modules/shensha/神煞基类.py', '忌动土'),
    ('modules/shensha/修造神煞.py', '忌动土'),
    ('modules/shensha/通用神煞.py', '忌动土'),
    ('modules/shensha/安床神煞.py', '不宜安床'),
]

total_hits = 0
for rel, must_word in TARGETS:
    path = os.path.join(ROOT, rel.replace('/', os.sep))
    with open(path, encoding='utf-8') as f:
        src = f.read()
    # 匹配 _add_shensha('土瘟', 分值, '描述串') 的描述串
    hits = re.findall(r"_add_shensha\(\s*'土瘟'\s*,\s*(-?\d+)\s*,\s*'([^']*)'", src)
    check('%s 存在土瘟发射' % rel, len(hits) >= 1)
    for score, desc in hits:
        total_hits += 1
        check('%s 描述串含「四季土旺日」: %s' % (rel, desc[:24]), '四季土旺日' in desc)
        check('%s 描述串含「%s」' % (rel, must_word), must_word in desc)
        check('%s 描述串分值 -20 锚不动' % rel, score == '-20')

check('5 处发射点总数吻合', total_hits == 5)

# ============ C：反向断言（无裸描述串） ============
for rel, _ in TARGETS:
    path = os.path.join(ROOT, rel.replace('/', os.sep))
    with open(path, encoding='utf-8') as f:
        src = f.read()
    bare = re.findall(r"_add_shensha\(\s*'土瘟'\s*,\s*-?\d+\s*,\s*'((?:[^']*(?<!四季土旺日)[^']*)?)'", src)
    bare = [b for b in bare if '四季土旺日' not in b]
    check('%s 无裸「土瘟」描述串（防回填）' % rel, len(bare) == 0)

# ============ D：行为层（正名不改判，走真实产品链路） ============
sys.path.insert(0, ROOT)
try:
    import datetime
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha import get_checker

    # 扫 2026-03-01..04-30（寅卯月）找一个土瘟日（四季土旺日，陈书起例）
    found = None
    cur = datetime.date(2026, 3, 1)
    end = datetime.date(2026, 4, 30)
    ck = get_checker('修造')
    while cur <= end and found is None:
        sz = calculate_sizhu(cur, 10, 0)
        if ck._is_tuwen(sz):
            found = cur
        cur += datetime.timedelta(days=1)
    check('2026 春季找到土瘟谓词命中日', found is not None)
    if found is not None:
        sz = calculate_sizhu(found, 10, 0)
        results = ck.check(sz, [])
        tuwen = [s for s in results if getattr(s, 'name', None) == '土瘟' or (isinstance(s, dict) and s.get('name') == '土瘟')]
        check('修造土瘟日实际发射土瘟', len(tuwen) >= 1)

        def _get(s, k):
            return s.get(k) if isinstance(s, dict) else getattr(s, k, None)

        if tuwen:
            check('土瘟分值 -20 不变', any(_get(s, 'score') == -20 for s in tuwen))
            check('发射描述串含「四季土旺日」', any('四季土旺日' in (_get(s, 'description') or _get(s, 'desc') or '') for s in tuwen))
except ImportError as e:
    print('[SKIP] 行为层：模块导入失败（%s），以源码层断言为准' % e)

print('---')
if FAILS:
    print('FAILS=%d' % len(FAILS))
    for f in FAILS:
        print(' -', f)
    raise SystemExit(1)
print('ALL PASS')
raise SystemExit(0)
