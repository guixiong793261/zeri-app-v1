# -*- coding: utf-8 -*-
"""
日期转换模块测试
"""

import sys
import os
from datetime import date, datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from 核心模块.日期转换 import (
    solar_to_lunar,
    lunar_to_solar,
    get_jie_qi,
    calculate_true_solar_time,
    calculate_gan_zhi,
    format_date
)


def test_solar_to_lunar():
    """测试公历转农历"""
    print("=" * 50)
    print("测试：公历转农历")
    print("=" * 50)
    
    test_dates = [
        date(2024, 1, 1),
        date(2024, 2, 10),
        date(2024, 6, 10),
        date(2024, 10, 1)
    ]
    
    for test_date in test_dates:
        try:
            result = solar_to_lunar(test_date)
            print(f"\n公历：{test_date}")
            print(f"农历：{result['中文']}")
            print(f"生肖：{result['生肖']}")
            if result['节气']['当前节气']:
                print(f"当前节气：{result['节气']['当前节气']['名称']}")
        except Exception as e:
            print(f"错误：{e}")


def test_lunar_to_solar():
    """测试农历转公历"""
    print("\n" + "=" * 50)
    print("测试：农历转公历")
    print("=" * 50)
    
    test_cases = [
        (2024, 1, 1, False),
        (2024, 2, 15, False),
        (2024, 5, 5, False),
        (2024, 8, 15, False)
    ]
    
    for lunar_year, lunar_month, lunar_day, is_leap in test_cases:
        try:
            result = lunar_to_solar(lunar_year, lunar_month, lunar_day, is_leap)
            print(f"\n农历：{lunar_year}年{lunar_month}月{lunar_day}日{'(闰)' if is_leap else ''}")
            print(f"公历：{result}")
        except Exception as e:
            print(f"错误：{e}")


def test_get_jie_qi():
    """测试节气查询"""
    print("\n" + "=" * 50)
    print("测试：节气查询")
    print("=" * 50)
    
    test_dates = [
        (2024, 2, 4, 12, 0),
        (2024, 6, 21, 12, 0),
        (2024, 12, 21, 12, 0)
    ]
    
    for year, month, day, hour, minute in test_dates:
        try:
            result = get_jie_qi(year, month, day, hour, minute)
            print(f"\n日期：{year}年{month}月{day}日 {hour}:{minute}")
            if result['当前节气']:
                print(f"当前节气：{result['当前节气']['名称']} - {result['当前节气']['时间']}")
            if result['下一节气']:
                print(f"下一节气：{result['下一节气']['名称']} - {result['下一节气']['时间']}")
        except Exception as e:
            print(f"错误：{e}")


def test_calculate_true_solar_time():
    """测试真太阳时计算"""
    print("\n" + "=" * 50)
    print("测试：真太阳时计算")
    print("=" * 50)
    
    test_cases = [
        (date(2024, 1, 1), 12, 0, 116.4074),
        (date(2024, 6, 21), 12, 0, 121.4737),
        (date(2024, 12, 21), 12, 0, 113.2644)
    ]
    
    for test_date, hour, minute, longitude in test_cases:
        try:
            result = calculate_true_solar_time(test_date, hour, minute, 0, longitude)
            print(f"\n日期：{test_date}")
            print(f"经度：{longitude}")
            print(f"标准时间：{result['标准时间']}")
            print(f"真太阳时：{result['真太阳时']}")
            print(f"{result['时差说明']}")
        except Exception as e:
            print(f"错误：{e}")


def test_calculate_gan_zhi():
    """测试干支计算"""
    print("\n" + "=" * 50)
    print("测试：干支计算")
    print("=" * 50)
    
    test_dates = [
        (date(2024, 1, 1), 12, 0),
        (date(2024, 6, 21), 12, 0),
        (date(2024, 12, 21), 12, 0)
    ]
    
    for test_date, hour, minute in test_dates:
        try:
            result = calculate_gan_zhi(test_date, hour, minute)
            print(f"\n日期：{test_date} {hour}:{minute}")
            print(f"年干支：{result['年干支']}")
            print(f"月干支：{result['月干支']}")
            print(f"日干支：{result['日干支']}")
            print(f"时干支：{result['时干支']}")
        except Exception as e:
            print(f"错误：{e}")


def test_format_date():
    """测试日期格式转换"""
    print("\n" + "=" * 50)
    print("测试：日期格式转换")
    print("=" * 50)
    
    test_date = date(2024, 6, 21)
    
    format_types = ['标准', '中文', 'ISO', '短格式']
    
    for format_type in format_types:
        try:
            result = format_date(test_date, format_type)
            print(f"\n格式类型：{format_type}")
            print(f"结果：{result}")
        except Exception as e:
            print(f"错误：{e}")


def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("日期转换模块测试")
    print("=" * 50)
    
    test_solar_to_lunar()
    test_lunar_to_solar()
    test_get_jie_qi()
    test_calculate_true_solar_time()
    test_calculate_gan_zhi()
    test_format_date()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == '__main__':
    main()
