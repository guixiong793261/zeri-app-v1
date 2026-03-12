# -*- coding: utf-8 -*-
"""
验证2025年闰月情况
"""

import sxtwl
from datetime import date

# 测试2025年7月25日
print("=== 测试2025年7月25日 ===")
day_obj = sxtwl.fromSolar(2025, 7, 25)
lunar_year = day_obj.getLunarYear()
lunar_month = day_obj.getLunarMonth()
lunar_day = day_obj.getLunarDay()
is_leap = day_obj.isLunarLeap()

print(f"公历：2025年7月25日")
print(f"农历：{lunar_year}年{lunar_month}月{lunar_day}日")
print(f"是否闰月：{is_leap}")

# 测试2025年8月22日
print("\n=== 测试2025年8月22日 ===")
day_obj = sxtwl.fromSolar(2025, 8, 22)
lunar_year = day_obj.getLunarYear()
lunar_month = day_obj.getLunarMonth()
lunar_day = day_obj.getLunarDay()
is_leap = day_obj.isLunarLeap()

print(f"公历：2025年8月22日")
print(f"农历：{lunar_year}年{lunar_month}月{lunar_day}日")
print(f"是否闰月：{is_leap}")

# 测试2025年12月1日
print("\n=== 测试2025年12月1日 ===")
day_obj = sxtwl.fromSolar(2025, 12, 1)
lunar_year = day_obj.getLunarYear()
lunar_month = day_obj.getLunarMonth()
lunar_day = day_obj.getLunarDay()
is_leap = day_obj.isLunarLeap()

print(f"公历：2025年12月1日")
print(f"农历：{lunar_year}年{lunar_month}月{lunar_day}日")
print(f"是否闰月：{is_leap}")

# 测试2026年1月1日
print("\n=== 测试2026年1月1日 ===")
day_obj = sxtwl.fromSolar(2026, 1, 1)
lunar_year = day_obj.getLunarYear()
lunar_month = day_obj.getLunarMonth()
lunar_day = day_obj.getLunarDay()
is_leap = day_obj.isLunarLeap()

print(f"公历：2026年1月1日")
print(f"农历：{lunar_year}年{lunar_month}月{lunar_day}日")
print(f"是否闰月：{is_leap}")