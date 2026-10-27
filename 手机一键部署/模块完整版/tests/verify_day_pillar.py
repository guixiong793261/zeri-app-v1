# -*- coding: utf-8 -*-
"""
verify_day_pillar — 玄空日星「段首同日冲突错向」修复验证（001 §49 缺陷 → §50 修复）

验收项：
  1. 四个边界日：2025-12-21 入冬至元(一白顺) / 2026-01-01 三碧+阳遁 /
     2026-02-18 仍冬至元 / 2026-02-19 入雨水元
  2. 影响面审计 D=0：1701-01-01~2100-12-31 逐日比对旧/新两套选择规则，
     分歧日集合必须恰为 1716/1796/1819/1922/2025 五个窗口（各 60 天）
  3. 引擎输出 vs 独立新规则：60 天窗 + 窗外 400 抽样 + 窗前后各 1 日（反向断言）
  4. 年/月盘不随本次修复变化（抽查）

运行：python tests/verify_day_pillar.py    退出码 0=全通过 / 1=失败
"""
import os
import sys
import random
from datetime import date, datetime, timedelta

_this_dir = os.path.dirname(os.path.abspath(__file__))
_proj = os.path.dirname(_this_dir)
for _p in [_proj, os.path.join(_proj, 'modules')]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sxtwl
from modules import 玄空飞星引擎 as eng
from modules.四柱计算器 import calculate_sizhu

FAILS = []


def check(name, cond, extra=''):
    tag = '[PASS] ' if cond else '[FAIL] '
    print(tag + name + (('  >> ' + extra) if (extra and not cond) else ''))
    if not cond:
        FAILS.append(name)


def norm(v):
    return (v - 1) % 9 + 1


# 典籍起例（硬编码，独立于引擎常量）
SEG_DEF = [(21, 1, +1), (1, 7, +1), (5, 4, +1),
           (9, 9, -1), (13, 3, -1), (17, 6, -1)]
Y_BASE_YANG = {'子': 1, '午': 1, '卯': 1, '酉': 1,
               '辰': 4, '戌': 4, '丑': 4, '未': 4,
               '寅': 7, '申': 7, '巳': 7, '亥': 7}
Y_BASE_YIN = {'子': 9, '午': 9, '卯': 9, '酉': 9,
              '辰': 6, '戌': 6, '丑': 6, '未': 6,
              '寅': 3, '申': 3, '巳': 3, '亥': 3}


def build_rows(y0, y1):
    """返回候选行（插入序=年升序内按SEG_DEF序）：(段首日, 中气日, 起星, 顺逆)。"""
    rows = []
    for y in range(y0, y1 + 1):
        jqs = sxtwl.getJieQiByYear(y)
        for idx, base, dr in SEG_DEF:
            dd = sxtwl.JD2DD(jqs[idx].jd)
            jd = date(int(dd.Y), int(dd.M), int(dd.D))
            g = sxtwl.fromSolar(jd.year, jd.month, jd.day).getDayGZ()
            gz0 = (g.tg * 6 - g.dz * 5) % 60
            start = jd + timedelta(days=(-gz0) % 60)
            rows.append((start, jd, base, dr))
    return rows


def day_val(row, d):
    return norm(row[2] + row[3] * (d - row[0]).days)


def engine_stars(d, hour_zhi='午'):
    sz = calculate_sizhu(d, 12, 0)
    dt_d = datetime(d.year, d.month, d.day, 12)
    r = eng.compute_stars(d.year, sz['year_zhi'], sz['month_zhi'], sz['day_zhi'],
                          hour_zhi, date_obj=dt_d, year_gan=sz['year_gan'])
    return r, sz


def indep_hour(row, d, day_zhi, hour_zhi='午'):
    hi = eng.DIZHI.index(hour_zhi) + 1
    if row[3] > 0:
        return norm(Y_BASE_YANG[day_zhi] + (hi - 1))
    return norm(Y_BASE_YIN[day_zhi] - (hi - 1))


# ============================================================
# 1. 边界日断言（用户指定四项 + 段归属）
# ============================================================
seg_dz = eng._day_segment_info(datetime(2025, 12, 21, 12))
check('2025-12-21 段=冬至元(段首当日,一白顺)', seg_dz == (date(2025, 12, 21), 1, 1),
      str(seg_dz))

r, _ = engine_stars(date(2025, 12, 21))
check('2025-12-21 日星=一白', r['day']['star'] == 1, str(r['day']['star']))

r, sz = engine_stars(date(2026, 1, 1))
check('2026-01-01 日星=三碧', r['day']['star'] == 3, str(r['day']['star']))
exp_h = indep_hour((None, None, None, +1), None, sz['day_zhi'])
check('2026-01-01 时盘=阳遁(壬午时四绿)', r['hour']['star'] == exp_h == 4,
      f"引擎{r['hour']['star']} 期望{exp_h}")

seg_0218 = eng._day_segment_info(datetime(2026, 2, 18, 12))
check('2026-02-18 仍属冬至上元(段首2025-12-21)',
      seg_0218 == (date(2025, 12, 21), 1, 1), str(seg_0218))
r, _ = engine_stars(date(2026, 2, 18))
check('2026-02-18 日星=六白', r['day']['star'] == 6, str(r['day']['star']))

seg_0219 = eng._day_segment_info(datetime(2026, 2, 19, 12))
check('2026-02-19 入雨水元(七赤顺)', seg_0219 == (date(2026, 2, 19), 7, 1),
      str(seg_0219))
r, _ = engine_stars(date(2026, 2, 19))
check('2026-02-19 日星=七赤', r['day']['star'] == 7, str(r['day']['star']))

# 窗前一日仍归处暑段（三碧逆，119天=一白）
r, _ = engine_stars(date(2025, 12, 20))
check('2025-12-20 窗前一日=处暑段一白', r['day']['star'] == 1, str(r['day']['star']))

# ============================================================
# 2. 影响面审计：1701-2100 旧/新规则逐日比对
# ============================================================
rows = build_rows(1700, 2101)
old_rows = sorted(rows, key=lambda x: x[0])              # 稳定排序=旧引擎
new_rows = sorted(rows, key=lambda x: (x[0], x[1]))      # 冲突按中气时序=新引擎

d = date(1701, 1, 1)
end = date(2100, 12, 31)
oi = ni = -1
diffs = []
while d <= end:
    while oi + 1 < len(old_rows) and old_rows[oi + 1][0] <= d:
        oi += 1
    while ni + 1 < len(new_rows) and new_rows[ni + 1][0] <= d:
        ni += 1
    o, n = old_rows[oi], new_rows[ni]
    oval = (day_val(o, d), o[3] > 0)
    nval = (day_val(n, d), n[3] > 0)
    if oval != nval:
        diffs.append(d)
    d += timedelta(days=1)

# 分歧日按连续段分组
groups = []
for dd in diffs:
    if groups and dd - groups[-1][-1] == timedelta(days=1):
        groups[-1].append(dd)
    else:
        groups.append([dd])
group_info = [(g[0], g[-1], len(g)) for g in groups]
print('分歧窗口：', group_info)
expected_starts = [date(1716, 12, 21), date(1796, 12, 21), date(1819, 12, 22),
                   date(1922, 12, 22), date(2025, 12, 21)]
ok_audit = ([g[0] for g in group_info] == expected_starts
            and all(info[2] == 60 for info in group_info))
check('影响面 D=0：分歧恰为 1716/1796/1819/1922/2025 五窗口(各60天)',
      ok_audit, str(group_info))
expected_window = [dd for g in groups for dd in g]

# ============================================================
# 3. 引擎 vs 独立新规则（60天窗 + 窗外抽样，含反向断言）
# ============================================================
random.seed(49)
span = (date(2099, 12, 31) - date(1950, 1, 1)).days
sample = [date(1950, 1, 1) + timedelta(days=k)
          for k in sorted(random.sample(range(span + 1), 400))]
check_dates = sample + expected_window + [date(2025, 12, 20), date(2026, 2, 19)]

import bisect
starts = [r[0] for r in new_rows]
mismatch = 0
for dd in check_dates:
    mrow = new_rows[bisect.bisect_right(starts, dd) - 1]
    r, sz = engine_stars(dd)
    if r['day']['star'] != day_val(mrow, dd):
        mismatch += 1
        print(f'  [FAIL] {dd} 引擎日星{r["day"]["star"]} != 独立{day_val(mrow, dd)}')
    if r['hour']['star'] != indep_hour(mrow, dd, sz['day_zhi']):
        mismatch += 1
        print(f'  [FAIL] {dd} 引擎时星{r["hour"]["star"]} != 独立遁')
check(f'引擎 vs 独立模型 日/时全等（{len(check_dates)}日）', mismatch == 0, f'{mismatch}处')

# 反向断言：窗外两个邻接日新旧规则必须一致（证明窗口边界精确）
for dd in (date(2025, 12, 20), date(2026, 2, 19)):
    op_i = np_i = -1
    for i, r0 in enumerate(old_rows):
        if r0[0] <= dd:
            op_i = i
        else:
            break
    for i, r0 in enumerate(new_rows):
        if r0[0] <= dd:
            np_i = i
        else:
            break
    op, nrow = old_rows[op_i], new_rows[np_i]
    same = (day_val(op, dd), op[3] > 0) == (day_val(nrow, dd), nrow[3] > 0)
    check(f'反向断言 {dd} 窗外新旧规则一致', same)

# ============================================================
# 4. 已发表锚点 + 年/月盘不随修复变化
# ====================================================
for dd, exp_day in [(date(2024, 12, 26), 1), (date(2025, 6, 21), 7),
                    (date(2026, 2, 15), 3), (date(2026, 4, 20), 4)]:
    r, _ = engine_stars(dd)
    check(f'锚点 {dd} 日星={exp_day}', r['day']['star'] == exp_day,
          str(r['day']['star']))

r, _ = engine_stars(date(2026, 1, 1))
check('年/月盘不变：2026-01-01 年二黑/月一白',
      r['year']['star'] == 2 and r['month']['star'] == 1,
      f"年{r['year']['star']} 月{r['month']['star']}")
r, _ = engine_stars(date(2026, 2, 18))
check('年/月盘不变：2026-02-18 年一白/月八白',
      r['year']['star'] == 1 and r['month']['star'] == 8,
      f"年{r['year']['star']} 月{r['month']['star']}")

print('=' * 60)
print('FAIL', len(FAILS), '项')
sys.exit(1 if FAILS else 0)
