# -*- coding: utf-8 -*-
"""
验证用户输入的四柱计算结果
"""

import sys
import os

# 添加核心模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '核心模块'))

from datetime import date
from 公式计算四柱 import FormulaSiZhuCalculator

# 测试用户输入的日期
user_date = date(1998, 10, 13)
hour = 0
minute = 0

# 创建计算器实例，强制使用简化节气数据
calculator = FormulaSiZhuCalculator(use_precise_jie_qi=False)

# 计算四柱
result = calculator.calculate_si_zhu(user_date, hour, minute)

# 显示结果
print("=== 验证用户输入的四柱计算结果 ===")
print(f"日期: {user_date} {hour:02d}:{minute:02d}")
print(f"年柱: {result['年柱']}")
print(f"月柱: {result['月柱']}")
print(f"日柱: {result['日柱']}")
print(f"时柱: {result['时柱']}")

# 对比用户提供的结果
user_result = {
    '年柱': '戊寅',
    '月柱': '壬戌',
    '日柱': '甲午',
    '时柱': '甲子'
}

print("\n=== 对比结果 ===")
for key in ['年柱', '月柱', '日柱', '时柱']:
    match = "✓" if result[key] == user_result[key] else "✗"
    print(f"{key}: {result[key]} vs {user_result[key]} {match}")
