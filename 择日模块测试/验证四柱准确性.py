# -*- coding: utf-8 -*-
"""
验证公式计算四柱模块的准确性
"""

from 核心模块.公式计算四柱 import calculate_si_zhu
from datetime import date

print("=== 验证公式计算四柱模块 ===\n")

# 测试用例：用户提供的日期
test_cases = [
    # (日期, 小时, 分钟, 预期年柱, 预期月柱, 预期日柱, 预期时柱, 测试名称)
    (date(1972, 1, 8), 8, 0, '辛亥', '壬子', '己亥', '戊辰', '1972-1-8 8:00'),  # 修正年柱预期
    (date(2026, 1, 1), 10, 0, '乙巳', '戊子', '乙亥', '辛巳', '2026-1-1 10:00'),
    (date(1971, 5, 11), 8, 0, '辛亥', '癸巳', '癸丑', '丙辰', '1971-5-11 8:00'),
    (date(1999, 4, 5), 6, 0, '己卯', '丁卯', '丁亥', '癸卯', '1999-4-5 6:00'),
    (date(2025, 6, 6), 6, 6, '乙巳', '壬午', '丁未', '癸卯', '2025-6-6 6:06'),
    # 新增测试用例：跨越节气的日期
    (date(2023, 2, 3), 12, 0, '壬寅', '癸丑', '壬子', '丙午', '2023-2-3 12:00'),  # 立春前
    (date(2023, 2, 4), 12, 0, '癸卯', '甲寅', '癸丑', '戊午', '2023-2-4 12:00'),  # 立春后
    (date(2023, 3, 4), 12, 0, '癸卯', '甲寅', '癸未', '戊午', '2023-3-4 12:00'),  # 惊蛰前
    (date(2023, 3, 5), 12, 0, '癸卯', '乙卯', '甲申', '戊午', '2023-3-5 12:00'),  # 惊蛰后
]

# 测试结果
print("测试结果：")
print("-" * 100)
print(f"{'测试日期':<20} {'计算年柱':<8} {'预期年柱':<8} {'计算月柱':<8} {'预期月柱':<8} {'计算日柱':<8} {'预期日柱':<8} {'计算时柱':<8} {'预期时柱':<8} {'结果':<6}")
print("-" * 100)

for test_date, hour, minute, expected_year, expected_month, expected_day, expected_hour, test_name in test_cases:
    result = calculate_si_zhu(test_date, hour, minute)
    
    year_match = result['年柱'] == expected_year
    month_match = result['月柱'] == expected_month
    day_match = result['日柱'] == expected_day
    hour_match = result['时柱'] == expected_hour
    
    overall = '✓' if year_match and month_match and day_match and hour_match else '✗'
    
    print(f"{test_date} {hour:02d}:{minute:02d} {' ':3} {result['年柱']:<8} {expected_year:<8} {result['月柱']:<8} {expected_month:<8} {result['日柱']:<8} {expected_day:<8} {result['时柱']:<8} {expected_hour:<8} {overall:<6}")

print("-" * 100)

# 检查时柱计算
print("\n=== 检查时柱计算 ===")
test_day_gan_zhi = ['己亥', '乙亥', '癸丑', '丁亥', '丁未']  # 真实的日柱

test_hour = [8, 10, 8, 6, 6]
expected_hour_gan_zhi = ['戊辰', '辛巳', '丙辰', '癸卯', '癸卯']

from 核心模块.公式计算四柱 import FormulaSiZhuCalculator
calculator = FormulaSiZhuCalculator()

print("-" * 80)
print(f"{'日柱':<6} {'小时':<6} {'计算时柱':<8} {'预期时柱':<8} {'结果':<6}")
print("-" * 80)

for day_gan_zhi, hour, expected in zip(test_day_gan_zhi, test_hour, expected_hour_gan_zhi):
    calculated = calculator.calculate_hour_gan_zhi(day_gan_zhi, hour)
    match = calculated == expected
    result = '✓' if match else '✗'
    print(f"{day_gan_zhi:<6} {hour:<6} {calculated:<8} {expected:<8} {result:<6}")

print("-" * 80)

# 检查年柱计算
print("\n=== 检查年柱计算 ===")
test_years = [1972, 2026, 1971, 1999, 2025]
test_months = [1, 1, 5, 4, 6]
test_days = [8, 1, 11, 5, 6]
expected_years = ['壬子', '乙巳', '辛亥', '己卯', '乙巳']

print("-" * 80)
print(f"{'年份':<6} {'月份':<6} {'日期':<6} {'计算年柱':<8} {'预期年柱':<8} {'结果':<6}")
print("-" * 80)

for year, month, day, expected in zip(test_years, test_months, test_days, expected_years):
    calculated = calculator.calculate_year_gan_zhi(year, month, day)
    match = calculated == expected
    result = '✓' if match else '✗'
    print(f"{year:<6} {month:<6} {day:<6} {calculated:<8} {expected:<8} {result:<6}")

print("-" * 80)