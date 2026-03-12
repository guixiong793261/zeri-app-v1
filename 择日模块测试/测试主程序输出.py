# -*- coding: utf-8 -*-
"""
测试主程序的实际输出
"""

import sys
import os
from datetime import date

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from 核心模块.日期转换 import solar_to_lunar

# 测试2026年1月1日
test_date = date(2026, 1, 1)
result = solar_to_lunar(test_date, 7, 30)

print(f"=== 测试2026年1月1日 7:30 ===")
print(f"公历：2026年1月1日 7:30")
print(f"农历：{result['中文']}")
print(f"年：{result['年']}")
print(f"月：{result['月']}")
print(f"日：{result['日']}")
print(f"月中文：{result['月中文']}")
print(f"闰月：{result['闰月']}")
print(f"生肖：{result['生肖']}")

# 测试2025年7月25日（闰六月）
test_date2 = date(2025, 7, 25)
result2 = solar_to_lunar(test_date2, 12, 0)

print(f"\n=== 测试2025年7月25日 12:00 ===")
print(f"公历：2025年7月25日 12:00")
print(f"农历：{result2['中文']}")
print(f"年：{result2['年']}")
print(f"月：{result2['月']}")
print(f"日：{result2['日']}")
print(f"月中文：{result2['月中文']}")
print(f"闰月：{result2['闰月']}")
print(f"生肖：{result2['生肖']}")