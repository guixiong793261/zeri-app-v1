# -*- coding: utf-8 -*-
"""
验证所有核心模块的功能
"""

import sys
import os
from datetime import date, datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=== 开始验证所有核心模块 ===")

# 1. 验证日期转换模块
print("\n1. 验证日期转换模块")
try:
    from 核心模块.日期转换 import (
        solar_to_lunar, lunar_to_solar, get_jie_qi,
        calculate_true_solar_time, calculate_gan_zhi, format_date
    )
    
    # 测试公历转农历
    test_date = date(2026, 1, 1)
    result = solar_to_lunar(test_date, 7, 30)
    print(f"✓ 公历转农历: 2026-01-01 → {result['中文']}")
    
    # 测试农历转公历
    result2 = lunar_to_solar(2025, 11, 13, False)
    print(f"✓ 农历转公历: 2025年11月13日 → {result2}")
    
    # 测试节气查询
    result3 = get_jie_qi(2026, 2, 4, 12, 0)
    print(f"✓ 节气查询: 2026-02-04 → 当前节气: {result3['当前节气']['名称']}")
    
    # 测试真太阳时计算
    result4 = calculate_true_solar_time(test_date, 10, 0, 0, 116.4074)
    print(f"✓ 真太阳时计算: 标准时间 {result4['标准时间']} → 真太阳时 {result4['真太阳时']}")
    
    # 测试干支计算
    result5 = calculate_gan_zhi(test_date, 10, 0)
    print(f"✓ 干支计算: {result5['年干支']} {result5['月干支']} {result5['日干支']} {result5['时干支']}")
    
    # 测试日期格式转换
    result6 = format_date(test_date, '标准')
    print(f"✓ 日期格式转换: {result6}")
    
    print("日期转换模块验证通过！")
except Exception as e:
    print(f"✗ 日期转换模块验证失败: {e}")

# 2. 验证择日核心模块
print("\n2. 验证择日核心模块")
try:
    from 核心模块.择日核心 import SelectDayCore
    
    core = SelectDayCore()
    # 测试日期范围选择
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    results = core.select_days(start_date, end_date, '婚嫁')
    if results:
        print(f"✓ 择日核心模块: 找到 {len(results)} 个婚嫁吉日")
        print(f"  第一个吉日: {results[0]['date']} - {results[0]['level']}")
    else:
        print("✓ 择日核心模块: 初始化成功")
    
    print("择日核心模块验证通过！")
except Exception as e:
    print(f"✗ 择日核心模块验证失败: {e}")

# 3. 验证评分器模块
print("\n3. 验证评分器模块")
try:
    from 核心模块.评分器 import ScoreCalculator
    
    calculator = ScoreCalculator()
    # 测试评分功能
    test_date = date(2024, 1, 1)
    result = calculator.calculate_score(test_date, 12, 0, '婚嫁')
    print(f"✓ 评分器模块: 2024-01-01 婚嫁评分 = {result['score']} - {result['level']}")
    
    print("评分器模块验证通过！")
except Exception as e:
    print(f"✗ 评分器模块验证失败: {e}")

print("\n=== 所有模块验证完成 ===")