# -*- coding: utf-8 -*-
"""
测试公式计算四柱模块
"""

import sys
import os
from datetime import date, datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from 核心模块.公式计算四柱 import (
    calculate_si_zhu, calculate_year_gan_zhi,
    calculate_month_gan_zhi, calculate_day_gan_zhi,
    calculate_hour_gan_zhi, FormulaSiZhuCalculator
)

print("=== 测试公式计算四柱模块 ===")

# 测试用例
print("\n1. 测试年柱计算")
test_years = [2000, 1999, 2026, 2025]
for year in test_years:
    gan_zhi = calculate_year_gan_zhi(year)
    print(f"{year}年 → {gan_zhi}")

print("\n2. 测试日柱计算")
test_dates = [
    date(2026, 1, 1),
    date(2025, 6, 6),
    date(2025, 7, 25),
    date(2000, 1, 1)
]
for test_date in test_dates:
    gan_zhi = calculate_day_gan_zhi(test_date)
    print(f"{test_date} → {gan_zhi}")

print("\n3. 测试时柱计算")
test_day_gan_zhi = ['壬午', '甲子', '丙寅', '戊午']
test_hours = [10, 0, 6, 12]
for day_gan_zhi, hour in zip(test_day_gan_zhi, test_hours):
    gan_zhi = calculate_hour_gan_zhi(day_gan_zhi, hour)
    print(f"{day_gan_zhi}日 {hour}时 → {gan_zhi}")

print("\n4. 测试完整四柱计算")
test_cases = [
    (date(2026, 1, 1), 7, 30),
    (date(2025, 6, 6), 6, 6),
    (date(2025, 7, 25), 12, 0),
    (date(2000, 1, 1), 0, 0)
]

for test_date, hour, minute in test_cases:
    si_zhu = calculate_si_zhu(test_date, hour, minute)
    print(f"\n{test_date} {hour:02d}:{minute:02d}")
    print(f"年柱: {si_zhu['年柱']}")
    print(f"月柱: {si_zhu['月柱']}")
    print(f"日柱: {si_zhu['日柱']}")
    print(f"时柱: {si_zhu['时柱']}")

print("\n5. 测试类方法")
calculator = FormulaSiZhuCalculator()
test_date = date(2026, 3, 9)
hour = 10
minute = 30
s_result = calculator.calculate_si_zhu(test_date, hour, minute)
print(f"\n{test_date} {hour:02d}:{minute:02d}")
print(f"年柱: {s_result['年柱']}")
print(f"月柱: {s_result['月柱']}")
print(f"日柱: {s_result['日柱']}")
print(f"时柱: {s_result['时柱']}")

print("\n=== 测试完成 ===")