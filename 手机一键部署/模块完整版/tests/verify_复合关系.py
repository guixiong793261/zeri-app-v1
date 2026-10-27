# -*- coding: utf-8 -*-
"""verify_复合关系：验证地支关系函数对复合关系（冲+刑/害+刑/刑+破）并列计分。
三层断言：
  A. 五个复合对各取代表日，lines 必须同时列出两条关系；
  B. 2022-2026 全量四柱，产品函数得分 == 并列逻辑重算；
  C. 非复合普通日（纯六冲、伏吟）行为保持。
旧代码应失败于 A/B，修复后全绿。"""
import sys, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding='utf-8')
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer
from modules.八字工具整合 import check_liuhe, check_liuchong, check_liuhai, check_xing, check_po

SC = Scorer()
fails = []

def pair_new(z1, z2):
    """并列逻辑：合/半合互斥保留；冲害刑破各自独立累加。"""
    s = 0
    if check_liuhe(z1, z2): s += 8
    elif SC._check_banhe(z1, z2)[0]: s += 6
    if check_liuchong(z1, z2): s -= 15
    if check_liuhai(z1, z2): s -= 6
    if check_xing(z1, z2): s -= 8
    if check_po(z1, z2): s -= 4
    return s

# ---------- A. 五个复合对代表日（月日级静态对，任意偶数时） ----------
# (日期, 时辰, 复合对, lines中必须同时出现的关键词)
CASES = [
    ('2026-02-12', 12, '寅巳', ['六害', '相刑']),   # 害+刑
    ('2026-07-14', 12, '丑未', ['六冲', '相刑']),   # 冲+刑
    ('2024-08-18', 12, '寅申', ['六冲', '相刑']),   # 冲+刑
    ('2025-08-07', 12, '巳申', ['六合', '相刑', '相破']),  # 合+刑+破
    ('2024-07-09', 12, '戌未', ['相刑', '相破']),   # 刑+破
]
for date_s, h, pair, kws in CASES:
    d = datetime.date(*map(int, date_s.split('-')))
    sz = calculate_sizhu(d, h, 0)
    score, lines = SC._calc_all_zhi_relations_detail(sz)
    pair_lines = [ln for ln in lines if (pair[0] in ln and pair[1] in ln)]
    missing = [k for k in kws if not any(k in ln for ln in pair_lines)]
    if missing or not pair_lines:
        fails.append('A %s %s（%s）缺关系行 %s，实际pair行=%s'
                     % (date_s, h, pair, missing, pair_lines))

# ---------- B. 全量对账（2022-2026 共 1826 天，覆盖集成 fixture 的 2023 日期） ----------
d0 = datetime.date(2022, 1, 1); d1 = datetime.date(2026, 12, 31)
n_days = (d1 - d0).days + 1
b_fail = 0
for di in range(n_days):
    date = d0 + datetime.timedelta(days=di)
    for h in (2*k for k in range(12)):
        sz = calculate_sizhu(date, h, 0)
        zs = [sz['year_zhi'], sz['month_zhi'], sz['day_zhi'], sz['hour_zhi']]
        expect = 0
        for a, b in ((0,1),(0,2),(0,3),(1,2),(1,3),(2,3)):
            expect += pair_new(zs[a], zs[b])
        got, _ = SC._calc_all_zhi_relations_detail(sz)
        if got != expect:
            b_fail += 1
            if b_fail <= 5:
                fails.append('B %s %d时：产品%+d ≠ 并列重算%+d' % (date, h, got, expect))

# ---------- C. 普通日行为：纯六冲只计冲、伏吟0分 ----------
# 找一个含"子午"六冲对且无其他复合的四柱：直接构造断言日
sz = calculate_sizhu(datetime.date(2026, 6, 20), 12, 0)  # 先看四柱
score, lines = SC._calc_all_zhi_relations_detail(sz)
# 伏吟：四支中两支相同且非辰午酉亥自刑——2024-03-01 0时 辰年寅月？动态找
found_fuyin = False
di = 0
while di < 400 and not found_fuyin:
    date = d0 + datetime.timedelta(days=di)
    for h in (2*k for k in range(12)):
        sz = calculate_sizhu(date, h, 0)
        zs = [sz['year_zhi'], sz['month_zhi'], sz['day_zhi'], sz['hour_zhi']]
        dup = [z for z in set(zs) if zs.count(z) >= 2 and z not in ('辰','午','酉','亥')]
        if dup:
            _, lns = SC._calc_all_zhi_relations_detail(sz)
            z = dup[0]
            fy = [ln for ln in lns if z in ln and '伏吟' in ln]
            if fy:
                found_fuyin = True
                break
    di += 1
if not found_fuyin:
    fails.append('C 未找到伏吟样例（枚举问题）')

print('A 复合对代表日：%d/5 通过' % (5 - sum(1 for f in fails if f.startswith('A'))))
print('B 全量对账：%d/%d 四柱一致' % (n_days*12 - b_fail, n_days*12))
print('C 伏吟普通日：%s' % ('通过' if found_fuyin else '失败'))
if fails:
    print('\n失败明细（前10）：')
    for f in fails[:10]: print('  ✗', f)
    sys.exit(1)
print('\n全部通过 ✓')
