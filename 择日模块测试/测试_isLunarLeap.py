# -*- coding: utf-8 -*-
"""
测试 sxtwl 库的 isLunarLeap() 方法
"""

import sxtwl

# 测试2026年1月1日
day_obj = sxtwl.fromSolar(2026, 1, 1)

print(f"=== 测试2026年1月1日 ===")
print(f"getLunarYear(): {day_obj.getLunarYear()}")
print(f"getLunarMonth(): {day_obj.getLunarMonth()}")
print(f"getLunarDay(): {day_obj.getLunarDay()}")
print(f"isLunarLeap(): {day_obj.isLunarLeap()}")
print(f"isLunarLeap 类型: {type(day_obj.isLunarLeap())}")

# 测试2025年7月25日（已知是闰月）
day_obj2 = sxtwl.fromSolar(2025, 7, 25)
print(f"\n=== 测试2025年7月25日 ===")
print(f"getLunarYear(): {day_obj2.getLunarYear()}")
print(f"getLunarMonth(): {day_obj2.getLunarMonth()}")
print(f"getLunarDay(): {day_obj2.getLunarDay()}")
print(f"isLunarLeap(): {day_obj2.isLunarLeap()}")

# 测试2025年8月23日（闰月之后）
day_obj3 = sxtwl.fromSolar(2025, 8, 23)
print(f"\n=== 测试2025年8月23日 ===")
print(f"getLunarYear(): {day_obj3.getLunarYear()}")
print(f"getLunarMonth(): {day_obj3.getLunarMonth()}")
print(f"getLunarDay(): {day_obj3.getLunarDay()}")
print(f"isLunarLeap(): {day_obj3.isLunarLeap()}")