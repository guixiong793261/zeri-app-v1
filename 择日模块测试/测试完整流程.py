# -*- coding: utf-8 -*-
"""
测试完整的公历转农历流程
"""

import sxtwl
from datetime import date, datetime

# 测试2026年1月1日
day_obj = sxtwl.fromSolar(2026, 1, 1)

print(f"=== 测试2026年1月1日 ===")
print(f"getLunarYear(): {day_obj.getLunarYear()}")
print(f"getLunarMonth(): {day_obj.getLunarMonth()}")
print(f"getLunarDay(): {day_obj.getLunarDay()}")
print(f"isLunarLeap(): {day_obj.isLunarLeap()}")

# 模拟我们的代码逻辑
lunar_year = day_obj.getLunarYear()
lunar_month = day_obj.getLunarMonth()
lunar_day = day_obj.getLunarDay()
is_leap = day_obj.isLunarLeap()

print(f"\n=== 模拟我们的代码逻辑 ===")
print(f"lunar_year: {lunar_year}")
print(f"lunar_month: {lunar_month}")
print(f"lunar_day: {lunar_day}")
print(f"is_leap: {is_leap}")

# 测试数字转中文
print(f"\n=== 测试数字转中文 ===")
def number_to_chinese(num):
    chinese_nums = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    if num <= 10:
        return chinese_nums[num]
    elif num < 20:
        return '十' + chinese_nums[num % 10]
    else:
        return chinese_nums[num // 10] + '十' + chinese_nums[num % 10]

month_chinese = number_to_chinese(lunar_month)
day_chinese = number_to_chinese(lunar_day)
if is_leap:
    month_chinese = "闰" + month_chinese

chinese = f"{lunar_year}年{month_chinese}月{day_chinese}"
print(f"month_chinese: {month_chinese}")
print(f"day_chinese: {day_chinese}")
print(f"最终输出: {chinese}")

# 测试2025年7月25日（闰六月）
print(f"\n=== 测试2025年7月25日（闰六月）===")
day_obj2 = sxtwl.fromSolar(2025, 7, 25)
lunar_year2 = day_obj2.getLunarYear()
lunar_month2 = day_obj2.getLunarMonth()
lunar_day2 = day_obj2.getLunarDay()
is_leap2 = day_obj2.isLunarLeap()

month_chinese2 = number_to_chinese(lunar_month2)
day_chinese2 = number_to_chinese(lunar_day2)
if is_leap2:
    month_chinese2 = "闰" + month_chinese2

chinese2 = f"{lunar_year2}年{month_chinese2}月{day_chinese2}"
print(f"lunar_month: {lunar_month2}")
print(f"is_leap: {is_leap2}")
print(f"month_chinese: {month_chinese2}")
print(f"最终输出: {chinese2}")