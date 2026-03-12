# -*- coding: utf-8 -*-
"""
自定义测试公式计算四柱模块
"""

from 核心模块.公式计算四柱 import calculate_si_zhu
from datetime import date

print("=== 自定义测试公式计算四柱 ===\n")

# 测试您关心的日期
test_dates = [
    (date(2026, 3, 9), 10, 30),  # 今天
    (date(2025, 6, 6), 6, 6),    # 之前测试过的日期
    (date(2025, 7, 25), 12, 0),  # 闰六月
    (date(1999, 4, 5), 6, 0),    # 用户提到的日期
]

for test_date, hour, minute in test_dates:
    si_zhu = calculate_si_zhu(test_date, hour, minute)
    print(f"{test_date} {hour:02d}:{minute:02d}")
    print(f"  年柱: {si_zhu['年柱']}")
    print(f"  月柱: {si_zhu['月柱']}")
    print(f"  日柱: {si_zhu['日柱']}")
    print(f"  时柱: {si_zhu['时柱']}")
    print()

# 交互式测试
print("=== 交互式测试 ===")
while True:
    try:
        year = int(input("输入年份（0退出）: "))
        if year == 0:
            break
        month = int(input("输入月份: "))
        day = int(input("输入日期: "))
        hour = int(input("输入小时: "))
        minute = int(input("输入分钟: "))
        
        si_zhu = calculate_si_zhu(date(year, month, day), hour, minute)
        print(f"\n四柱:")
        print(f"  年柱: {si_zhu['年柱']}")
        print(f"  月柱: {si_zhu['月柱']}")
        print(f"  日柱: {si_zhu['日柱']}")
        print(f"  时柱: {si_zhu['时柱']}\n")
    except Exception as e:
        print(f"错误: {e}\n")

print("测试结束")