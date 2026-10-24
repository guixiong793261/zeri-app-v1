# -*- coding: utf-8 -*-
"""
时辰系五鼠遁全网格互证（001 §168 收口批·互证断言测试）
========================================================
目的：锁定 modules/shensha/时辰系.py 的 WUSHU_DUN（五鼠遁表）与
modules/四柱计算器.py 的实测时柱永不漂移。

方法：
1. 2026 全年扫描，按日干分组取代表日（首日＋中间日，兼顾节气分布）；
2. 每个代表日跑 12 时辰实测（calculate_sizhu），构成 10 日干 × 12 时支
   全网格样本（子时取 23 点＝晚子时派口径：日柱不换日、时干按当日日干遁）；
3. 逐样本断言：时辰系.get_hour_gan_series(日干)[时支] == 实测 hour_gan；
4. 网格覆盖断言：120 组合每格 ≥1 样本，缺格即失败；
5. 自洽断言：get_hour_gan_series 子位起遁干 == WUSHU_DUN[日干]、12 支顺推
   十干循环。

退出码：0＝全部通过；1＝存在断言失败（供 CI 集成）。
"""
import sys
import os
from datetime import date, timedelta

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.shensha.时辰系 import (
    TIAN_GAN, DI_ZHI, WUSHU_DUN, get_hour_gan_series,
)
from modules.四柱计算器 import calculate_sizhu

# 时支 → 代表时刻（小时）。子时取 23 点验证晚子时派五鼠遁口径。
HOUR_REP = {'子': 23, '丑': 1, '寅': 3, '卯': 5, '辰': 7, '巳': 9,
            '午': 11, '未': 13, '申': 15, '酉': 17, '戌': 19, '亥': 21}


def check_series_selfconsistent():
    """自洽断言：起遁干与五鼠遁表一致、12 支顺推十干循环。"""
    errors = []
    for dg in TIAN_GAN:
        series = get_hour_gan_series(dg)
        if len(series) != 12:
            errors.append(f'自洽：{dg} 时干序列长度 {len(series)} != 12')
            continue
        if series[0] != WUSHU_DUN.get(dg):
            errors.append(f'自洽：{dg} 子位起遁干 {series[0]} != WUSHU_DUN[{dg}]={WUSHU_DUN.get(dg)}')
            continue
        zi_idx = TIAN_GAN.index(WUSHU_DUN[dg])
        for i in range(12):
            expect = TIAN_GAN[(zi_idx + i) % 10]
            if series[i] != expect:
                errors.append(f'自洽：{dg} 第{i}位（{DI_ZHI[i]}）时干 {series[i]} != 顺推 {expect}')
    return errors


def main():
    # ---- 1. 自洽断言 ----
    errors = check_series_selfconsistent()

    # ---- 2. 2026 全年按日干取代表日（首、中两日） ----
    rep_days = {}  # day_gan -> [date, ...]
    d = date(2026, 1, 1)
    while d <= date(2026, 12, 31):
        dg = calculate_sizhu(d, 10, 0)['day_gan']
        rep_days.setdefault(dg, []).append(d)
        d += timedelta(days=1)
    chosen = {}
    for dg, days in rep_days.items():
        chosen[dg] = [days[0], days[len(days) // 2]]

    # ---- 3. 全网格实测互证 ----
    covered = {(dg, zhi): 0 for dg in TIAN_GAN for zhi in DI_ZHI}
    n_samples = 0
    for dg in TIAN_GAN:
        for d in chosen.get(dg, []):
            for zhi, hh in HOUR_REP.items():
                sz = calculate_sizhu(d, hh, 0)
                actual_dg, actual_zhi = sz['day_gan'], sz['hour_zhi']
                # 晚子时派：23 点日柱不换日；其余时刻日柱即当日。防漂移双断言。
                if actual_dg != dg:
                    errors.append(f'互证：{d} {hh}点 日干漂移 实测{actual_dg} != 预期{dg}')
                    continue
                if actual_zhi != zhi:
                    errors.append(f'互证：{d} {hh}点 时支漂移 实测{actual_zhi} != 预期{zhi}')
                    continue
                expected_gan = get_hour_gan_series(dg)[DI_ZHI.index(zhi)]
                if sz['hour_gan'] != expected_gan:
                    errors.append(
                        f'互证：{d} {hh}点 {dg}日{zhi}时 实测时干 {sz["hour_gan"]}'
                        f' != 五鼠遁表推导 {expected_gan}')
                    continue
                covered[(dg, zhi)] += 1
                n_samples += 1

    # ---- 4. 网格覆盖断言 ----
    missing = [(dg, zhi) for (dg, zhi), n in covered.items() if n == 0]
    if missing:
        for dg, zhi in missing:
            errors.append(f'覆盖：{dg}日×{zhi}时 全网格缺样')

    # ---- 5. 汇总 ----
    print(f'互证样本总数：{n_samples}（目标 ≥ 240 = 10干×2日×12时）')
    print(f'网格覆盖：{sum(1 for n in covered.values() if n > 0)}/120 组合')
    if errors:
        print(f'\n断言失败 {len(errors)} 项：')
        for e in errors[:50]:
            print(f'  ✗ {e}')
        if len(errors) > 50:
            print(f'  ...（其余 {len(errors) - 50} 项省略）')
        return 1
    print('全部断言通过：五鼠遁表与四柱计算器 10日干×12时支 全网格零漂移。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
