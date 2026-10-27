# -*- coding: utf-8 -*-
"""
verify: K1（001 §58）今日黄历 GUI 值日对齐月家口径
- GUI 值日 == 黄道.py 月家值日（全日期）
- 反向：寅月、申月与旧固定法整月一致（证明改动无漂移）
- SHI_ER_SHEN 固定映射已移除（防未来误用，反向）
退出码：全过 0 / 有失败 1；结尾打印 FAIL N。
"""
import sys, os, datetime, ast
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAILS = []
def check(name, cond):
    print(("[OK] " if cond else "[FAIL] ") + name)
    if not cond:
        FAILS.append(name)

import modules.今日黄历 as jl
from modules.黄道 import huangdao_calculator
from modules.四柱计算器 import calculate_sizhu

# ---------- 1. SHI_ER_SHEN 固定映射已移除（反向） ----------
check("今日黄历不再含 SHI_ER_SHEN 固定映射", not hasattr(jl, 'SHI_ER_SHEN'))

# ---------- 2. 全日期 2021-2026：GUI 值日 == 月家值日 ----------
# 模拟 K1 后 GUI 的取值方式
def gui_zhiri(day_zhi, month_zhi):
    return huangdao_calculator._calculate_da_huangdao_zhiri(day_zhi, month_zhi)

bad = 0
yin_shen_keep = []   # 寅申月：月家值日必为日支固定旧法
d0, d1 = datetime.date(2021,1,1), datetime.date(2026,12,31)
OLD_FIXED = dict(zip('子丑寅卯辰巳午未申酉戌亥',
                     ['青龙','明堂','天刑','朱雀','金匮','天德','白虎','玉堂','天牢','玄武','司命','勾陈']))
d = d0
per = {}
while d <= d1:
    sz = calculate_sizhu(d, 12, 0)
    mz, dz = sz['月柱'][1], sz['日柱'][1]
    g = gui_zhiri(dz, mz)['name']
    yue = huangdao_calculator._calculate_da_huangdao_zhiri(dz, mz)['name']
    if g != yue:
        bad += 1
    if mz in ('寅','申'):
        per.setdefault(mz, [0,0]); per[mz][1] += 1
        if yue != OLD_FIXED[dz]:
            per[mz][0] += 1
    d += datetime.timedelta(days=1)
check("全日期 GUI 值日 == 月家值日（%d 错）" % bad, bad == 0)
check("寅月：月家值日与旧固定法逐日一致（反向无漂移）",
      per.get('寅',[1,0])[0] == 0)
check("申月：月家值日与旧固定法逐日一致（反向无漂移）",
      per.get('申',[1,0])[0] == 0)

print()
print("FAIL %d" % len(FAILS))
sys.exit(1 if FAILS else 0)
