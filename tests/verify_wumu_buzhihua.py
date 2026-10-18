# -*- coding: utf-8 -*-
"""
五墓「不得自动豁免」回归锁（制化层前置断言，2026-10-18）
======================================================
拍板依据：d6 月家P2 续取证发现五墓制化条文「五月十一月与月德并则不忌」
（协纪卷十五墓段明文），用户拍板：
「不批准本批立即改码……标注'五墓制化待制化层统一处理'……
保留回归断言：在制化层裁断前，不得因月德自动豁免五墓
（防止有人看到条文就顺手加豁免）。」

验证面：
A. 源码层：基类/通用 checker 五墓发射附近无月德豁免分支；
B. 行为层（反向锚）：午月丙戌日 = 五墓（四五月丙戌）+ 月德并
   （午月月德=丙干，丙戌日干丙=月德）——协纪典载「不忌」之日，
   软件在制化层裁断前**仍发射五墓 -12**（维持现状，不自动豁免）。
   制化层批次实现豁免时，本断言需随批更新（届时应先改本脚本拍板）。

退出码 0=全过 1=有失败。
"""
import io
import os
import re
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


# ============ A：源码层（无月德豁免分支） ============
SOURCES = ['modules/shensha/神煞基类.py', 'modules/shensha/通用神煞.py']
for rel in SOURCES:
    path = os.path.join(ROOT, rel.replace('/', os.sep))
    with open(path, encoding='utf-8') as f:
        src = f.read()
    # 定位五墓发射块（发射行前后 6 行窗口）
    blocks = []
    lines = src.split('\n')
    for i, ln in enumerate(lines):
        if "_add_shensha('五墓'" in ln:
            blocks.append('\n'.join(lines[max(0, i - 6):i + 2]))
    check('%s 存在五墓发射' % rel, len(blocks) >= 1)
    for j, blk in enumerate(blocks):
        check('%s 五墓发射#%d 无月德豁免分支' % (rel, j + 1),
              '月德' not in blk and 'yuede' not in blk.lower())
    check('%s 五墓发射无 if-not 豁免条件（无条件发射）' % rel,
          all(re.search(r"if self\._is_wumu\([^)]*\):\s*\n\s*self\._add_shensha\('五墓'", blk) for blk in blocks))

# ============ B：行为层（午月丙戌日仍扣分） ============
sys.path.insert(0, ROOT)
try:
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha import get_checker

    def _get(s, k):
        return s.get(k) if isinstance(s, dict) else getattr(s, k, None)

    ck = get_checker('通用')
    # 扫 2025-2027 各年午月窗口找丙戌日（五墓四五月丙戌；午月月德丙干=月德并）
    found = None
    for y in (2025, 2026, 2027):
        # 午月窗口：6/6..7/6（小暑前，按节气月支实时判定兜底）
        cur = datetime.date(y, 6, 6)
        end = datetime.date(y, 7, 6)
        while cur <= end and found is None:
            sz = calculate_sizhu(cur, 10, 0)
            if (sz.get('day_gan') == '丙' and sz.get('day_zhi') == '戌'
                    and sz.get('month_zhi') == '午'):
                found = cur
            cur += datetime.timedelta(days=1)
        if found is not None:
            break
    check('2025-2027 午月找到丙戌日（五墓+月德并）', found is not None)
    if found is not None:
        sz = calculate_sizhu(found, 10, 0)
        # 月德确证：该日应发射月德
        results = ck.check(sz, [])
        names = [(_get(s, 'name'), _get(s, 'score')) for s in results]
        has_yuede = any(n == '月德' for n, _ in names)
        wumu = [(n, sc) for n, sc in names if n == '五墓']
        check('该日确证月德在榜（月德并成立前提）', has_yuede)
        check('五墓+月德并日仍发射五墓（不得自动豁免）', len(wumu) >= 1)
        if wumu:
            check('五墓分值 -12 维持现状', any(sc == -12 for _, sc in wumu))
        # 反向锚：入宅 checker 同日仍扣（通用通道外抽样——择嫁娶抽查五墓发射）
        ck2 = get_checker('嫁娶')
        results2 = ck2.check(sz, [])
        names2 = [_get(s, 'name') for s in results2]
        check('嫁娶通道五墓+月德并日仍发射五墓', '五墓' in names2)
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
