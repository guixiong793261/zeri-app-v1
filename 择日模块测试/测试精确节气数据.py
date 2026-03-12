# -*- coding: utf-8 -*-
"""
测试精确节气数据模块的整合
"""

import sys
import os

# 添加核心模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '核心模块'))

from datetime import date

# 测试精确节气数据模块
print("=== 测试精确节气数据模块 ===\n")

try:
    from 精确节气数据 import JieQiCalculator, get_precise_month
    print("✓ 成功导入精确节气数据模块")
    
    # 创建计算器实例
    calculator = JieQiCalculator()
    
    # 测试2023年的节气数据
    print("\n=== 2023年节气数据 ===")
    jie_qi_list = calculator.get_year_jie_qi(2023)
    if jie_qi_list:
        for jq in jie_qi_list[:6]:  # 只显示前6个节气
            print(f"{jq['名称']}: {jq['时间']}")
        print("...")
    
    # 测试特定日期的月份计算
    print("\n=== 特定日期月份计算 ===")
    test_dates = [
        (2023, 2, 3, 12, 0),   # 立春前
        (2023, 2, 4, 12, 0),   # 立春后
        (2023, 3, 5, 12, 0),   # 惊蛰前
        (2023, 3, 6, 12, 0),   # 惊蛰后
    ]
    
    for year, month, day, hour, minute in test_dates:
        lunar_month = calculator.get_month_by_jie_qi(year, month, day, hour, minute)
        jie_qi_info = calculator.get_jie_qi_by_date(year, month, day, hour, minute)
        current_jq = jie_qi_info['当前节气']['名称'] if jie_qi_info and jie_qi_info['当前节气'] else '未知'
        print(f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} -> 农历{lunar_month}月 (当前节气: {current_jq})")
    
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print("  可能原因: sxtwl库未安装")

# 测试公式计算四柱模块的整合
print("\n=== 测试公式计算四柱模块整合 ===\n")

try:
    from 公式计算四柱 import FormulaSiZhuCalculator
    
    # 使用精确节气数据
    print("使用精确节气数据:")
    calculator_precise = FormulaSiZhuCalculator(use_precise_jie_qi=True)
    
    # 测试日期
    test_date = date(2023, 2, 4)
    result = calculator_precise.calculate_si_zhu(test_date, 12, 0)
    
    print(f"日期: {test_date}")
    print(f"年柱: {result['年柱']}")
    print(f"月柱: {result['月柱']}")
    print(f"日柱: {result['日柱']}")
    print(f"时柱: {result['时柱']}")
    
    # 使用简化节气数据
    print("\n使用简化节气数据:")
    calculator_simple = FormulaSiZhuCalculator(use_precise_jie_qi=False)
    
    result_simple = calculator_simple.calculate_si_zhu(test_date, 12, 0)
    
    print(f"日期: {test_date}")
    print(f"年柱: {result_simple['年柱']}")
    print(f"月柱: {result_simple['月柱']}")
    print(f"日柱: {result_simple['日柱']}")
    print(f"时柱: {result_simple['时柱']}")
    
except ImportError as e:
    print(f"✗ 导入失败: {e}")

print("\n=== 测试完成 ===")
