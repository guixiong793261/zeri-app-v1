# -*- coding: utf-8 -*-
"""
批8b 母仓「土王用事段巳午」添段 verify
========================================
J2 甲案②：基类 `_is_mucang` 在土王用事段（四立前各 18 日）内 day_zhi
∈{巳,午} 时**添**命母仓（《协纪辨方书》卷三·义例二母仓条引《神枢经》
"土王用事後忌修造动土巳午日"，四季月立成同诀）。

口径＝并集非替换：季节表（春亥子/夏寅卯/秋辰戌丑未/冬申酉）段内命中
仍保留；巳午为土王段叠加项。巳午与四季月季节表零重叠，故添段＝纯新增
无翻转（预期每年 +12 天 × 全事项 +10）。

检查项：
  1. 土王段×巳午穷举硬锁（2024-2027 四季土王段内巳午日必命中母仓）；
  2. 添非替断言：辰月土王段亥子日仍命中（季节表不被替换）；
  3. 段外巳午不命中（非土王段巳午日母仓＝False，除非季节表命中——
     四季月季节表不含巳午，故段外巳午必 False）；
  4. 每年新增约 12 天断言（18 日段内巳午约 3 次 ×4 季）；
  5. 批6' verify_b6_mucang_sixiang 回归（季节表口径不变）；
  6. 运行时 checker 命中断言（土王段巳午日母仓 +10 发射）；
  7. 发射位唯一性静态扫描（'母仓' 发射点仅基类一处）；
  8. `_is_mucang` 全模块仅基类定义（无子类重写）。

用法：python tests/verify_b8_mucang.py
退出码：0=全部通过  1=任一失败
"""
import sys
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sxtwl
from modules.四柱计算器 import calculate_sizhu
from modules.shensha.神煞基类 import (
    ShenShaChecker, is_tuwang_yongshi_by_date)
from modules.shensha.修造神煞 import ConstructionShenShaChecker
from modules.shensha.动土神煞 import DiggingShenShaChecker
from modules.shensha.拆舍神煞 import DemolitionShenShaChecker
from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
from modules.shensha.入宅神煞 import RuZhaiShenShaChecker as HouseMovingShenShaChecker

PASS = True


def check(name, ok, detail=''):
    global PASS
    tag = 'PASS' if ok else 'FAIL'
    print('[%s] %s%s' % (tag, name, ('  ' + detail) if detail else ''))
    if not ok:
        PASS = False


def jd_to_date(jd):
    dd = sxtwl.JD2DD(jd)
    return dt.date(int(dd.Y), int(dd.M), int(dd.D))


def get_sizhu(y, m, d):
    sz = calculate_sizhu(dt.datetime(y, m, d, 12, 0))
    sz['year'], sz['month'], sz['day'] = y, m, d
    return sz


_SILIQ = (0, 6, 12, 18)


def tuwang_days_of_year(y):
    """返回 y 年所有土王用事日的 date 集合。"""
    days = set()
    for yy in (y, y + 1):
        for i in _SILIQ:
            L = jd_to_date(sxtwl.getJieQiByYear(yy)[i].jd)
            for delta in range(1, 19):
                d = L - dt.timedelta(days=delta)
                if d.year == y:
                    days.add(d)
    return days


# ── 1. 土王段×巳午穷举硬锁 ─────────────────────────────────────
bad1 = []
checker = ShenShaChecker()
for y in range(2024, 2028):
    for d in tuwang_days_of_year(y):
        sz = get_sizhu(d.year, d.month, d.day)
        if sz['day_zhi'] in ('巳', '午'):
            if not checker._is_mucang(sz):
                bad1.append('%s dz=%s' % (d, sz['day_zhi']))
check('土王段内巳午日必命中母仓（2024-2027）', not bad1,
      '; '.join(bad1[:5]))

# ── 2. 添非替断言：季节表命中不受影响 ──────────────────────────
bad2 = []
for y in range(2024, 2028):
    for d in tuwang_days_of_year(y):
        sz = get_sizhu(d.year, d.month, d.day)
        mz = sz['month_zhi']
        dz = sz['day_zhi']
        season_hit = ((mz in ('寅', '卯', '辰') and dz in ('亥', '子')) or
                      (mz in ('巳', '午', '未') and dz in ('寅', '卯')) or
                      (mz in ('申', '酉', '戌') and dz in ('辰', '戌', '丑', '未')) or
                      (mz in ('亥', '子', '丑') and dz in ('申', '酉')))
        if season_hit and not checker._is_mucang(sz):
            bad2.append('%s 季节表命中但母仓=False' % d)
check('添非替：土王段内季节表命中日母仓仍为 True', not bad2,
      '; '.join(bad2[:5]))

# ── 3. 段外巳午不命中 ──────────────────────────────────────────
bad3 = []
for y in range(2024, 2028):
    tw = tuwang_days_of_year(y)
    d0 = dt.date(y, 1, 1)
    for i in range((dt.date(y, 12, 31) - d0).days + 1):
        cur = d0 + dt.timedelta(days=i)
        if cur in tw:
            continue
        sz = get_sizhu(cur.year, cur.month, cur.day)
        if sz['day_zhi'] in ('巳', '午') and checker._is_mucang(sz):
            bad3.append('%s 段外巳午误命中' % cur)
check('段外巳午日母仓=False（四季月季节表不含巳午）', not bad3,
      '; '.join(bad3[:5]))

# ── 4. 每年新增约 12 天 ────────────────────────────────────────
bad4 = []
for y in range(2024, 2028):
    added = 0
    for d in tuwang_days_of_year(y):
        sz = get_sizhu(d.year, d.month, d.day)
        if sz['day_zhi'] in ('巳', '午'):
            added += 1
    # 18 日段内 12 地支循环，巳午占 2/12 → 18×2/12 = 3 日/季 ×4 季 = 12
    if not (10 <= added <= 14):
        bad4.append('%d 新增=%d（预期 10-14）' % (y, added))
check('每年土王段巳午日约 12 天（10-14 区间）', not bad4,
      '; '.join(bad4))

# ── 5. 批6' 回归 ──────────────────────────────────────────────
import importlib
b6 = importlib.import_module('tests.verify_b6_mucang_sixiang')
# verify_b6 用 if __name__=='__main__' 保护，直接调用其断言需重构；
# 此处用 subprocess 调用确保独立验证
import subprocess
r = subprocess.run([sys.executable, str(ROOT / 'tests' / 'verify_b6_mucang_sixiang.py')],
                   capture_output=True, text=True)
check('批6\' verify_b6_mucang_sixiang 回归（季节表口径不变）',
      r.returncode == 0, r.stdout.strip().split('\n')[-1] if r.stdout else '')

# ── 6. 运行时 checker 命中断言 ─────────────────────────────────
bad6 = []
checkers = [
    ('修造', ConstructionShenShaChecker),
    ('动土', DiggingShenShaChecker),
    ('拆舍', DemolitionShenShaChecker),
    ('嫁娶', MarriageShenShaChecker),
    ('入宅', HouseMovingShenShaChecker),
]
# 取 2026 丑月土王段巳午日
sample = []
for d in tuwang_days_of_year(2026):
    sz = get_sizhu(d.year, d.month, d.day)
    if sz['day_zhi'] in ('巳', '午'):
        sample.append((d, sz))
        if len(sample) >= 4:
            break
for name, cls in checkers:
    for d, sz in sample:
        c = cls()
        res = c.check(sz, {})
        has_mucang = any(
            (it.get('name') if isinstance(it, dict) else it[0]) == '母仓'
            for it in res)
        if not has_mucang:
            bad6.append('%s %s 未发射母仓' % (name, d))
check('运行时：土王段巳午日 5 checker 均发射母仓 +10（抽样 4 日）',
      not bad6, '; '.join(bad6[:5]))

# ── 7. 发射位唯一性 ────────────────────────────────────────────
import re
base_src = (ROOT / 'modules' / 'shensha' / '神煞基类.py').read_text(encoding='utf-8')
emit_lines = [i + 1 for i, ln in enumerate(base_src.split('\n'))
              if "_add_shensha('母仓'" in ln]
check("'母仓' 发射点仅基类一处（共 %d 处）" % len(emit_lines),
      len(emit_lines) == 1, 'lines=%s' % emit_lines)

# ── 8. _is_mucang 全模块仅基类定义 ────────────────────────────
import glob
all_mucang_defs = []
for f in glob.glob(str(ROOT / 'modules' / 'shensha' / '*.py')):
    src = Path(f).read_text(encoding='utf-8')
    for i, ln in enumerate(src.split('\n'), 1):
        if ln.strip().startswith('def _is_mucang'):
            all_mucang_defs.append('%s:%d' % (Path(f).name, i))
check('_is_mucang 全模块仅基类定义（无子类重写）',
      len(all_mucang_defs) == 1, str(all_mucang_defs))

print()
sys.exit(0 if PASS else 1)
