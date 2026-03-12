# -*- coding: utf-8 -*-
"""
择日模块测试主程序

用于测试和开发新的择日算法
"""

import sys
import os
from datetime import date, datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
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


def print_menu():
    """打印菜单"""
    print("\n" + "=" * 60)
    print("择日模块测试主程序")
    print("=" * 60)
    print("1. 公历转农历")
    print("2. 农历转公历")
    print("3. 节气查询")
    print("4. 真太阳时计算")
    print("5. 干支计算")
    print("6. 日期格式转换")
    print("7. 运行所有测试")
    print("0. 退出")
    print("=" * 60)


def solar_to_lunar_menu():
    """公历转农历菜单"""
    print("\n--- 公历转农历 ---")
    try:
        year = int(input("请输入年份（例如：2024）："))
        month = int(input("请输入月份（1-12）："))
        day = int(input("请输入日期（1-31）："))
        hour = int(input("请输入小时（0-23，默认12）：") or "12")
        minute = int(input("请输入分钟（0-59，默认0）：") or "0")
        
        test_date = date(year, month, day)
        result = solar_to_lunar(test_date, hour, minute)
        
        print(f"\n公历：{year}年{month}月{day}日 {hour}:{minute}")
        print(f"农历：{result['中文']}")
        print(f"生肖：{result['生肖']}")
        if result['节气']['当前节气']:
            print(f"当前节气：{result['节气']['当前节气']['名称']}")
            print(f"节气时间：{result['节气']['当前节气']['时间']}")
        if result['节气']['下一节气']:
            print(f"下一节气：{result['节气']['下一节气']['名称']}")
            print(f"节气时间：{result['节气']['下一节气']['时间']}")
    except Exception as e:
        print(f"错误：{e}")


def lunar_to_solar_menu():
    """农历转公历菜单"""
    print("\n--- 农历转公历 ---")
    try:
        year = int(input("请输入农历年份（例如：2024）："))
        month = int(input("请输入农历月份（1-12）："))
        day = int(input("请输入农历日期（1-30）："))
        is_leap = input("是否闰月（y/n，默认n）：").lower() == 'y'
        
        result = lunar_to_solar(year, month, day, is_leap)
        
        print(f"\n农历：{year}年{month}月{day}日{'(闰)' if is_leap else ''}")
        print(f"公历：{result}")
    except Exception as e:
        print(f"错误：{e}")


def jie_qi_menu():
    """节气查询菜单"""
    print("\n--- 节气查询 ---")
    try:
        year = int(input("请输入年份（例如：2024）："))
        month = int(input("请输入月份（1-12）："))
        day = int(input("请输入日期（1-31）："))
        hour = int(input("请输入小时（0-23，默认12）：") or "12")
        minute = int(input("请输入分钟（0-59，默认0）：") or "0")
        
        result = get_jie_qi(year, month, day, hour, minute)
        
        print(f"\n日期：{year}年{month}月{day}日 {hour}:{minute}")
        if result['当前节气']:
            print(f"当前节气：{result['当前节气']['名称']}")
            print(f"节气时间：{result['当前节气']['时间']}")
        if result['下一节气']:
            print(f"下一节气：{result['下一节气']['名称']}")
            print(f"节气时间：{result['下一节气']['时间']}")
    except Exception as e:
        print(f"错误：{e}")


def true_solar_time_menu():
    """真太阳时计算菜单"""
    print("\n--- 真太阳时计算 ---")
    try:
        year = int(input("请输入年份（例如：2024）："))
        month = int(input("请输入月份（1-12）："))
        day = int(input("请输入日期（1-31）："))
        hour = int(input("请输入小时（0-23）："))
        minute = int(input("请输入分钟（0-59）："))
        longitude = float(input("请输入经度（默认116.4074）：") or "116.4074")
        
        test_date = date(year, month, day)
        result = calculate_true_solar_time(test_date, hour, minute, 0, longitude)
        
        print(f"\n日期：{year}年{month}月{day}日")
        print(f"经度：{longitude}")
        print(f"标准时间：{result['标准时间']}")
        print(f"真太阳时：{result['真太阳时']}")
        print(f"{result['时差说明']}")
    except Exception as e:
        print(f"错误：{e}")


def gan_zhi_menu():
    """干支计算菜单"""
    print("\n--- 干支计算 ---")
    try:
        year = int(input("请输入年份（例如：2024）："))
        month = int(input("请输入月份（1-12）："))
        day = int(input("请输入日期（1-31）："))
        hour = int(input("请输入小时（0-23，默认12）：") or "12")
        minute = int(input("请输入分钟（0-59，默认0）：") or "0")
        
        test_date = date(year, month, day)
        result = calculate_gan_zhi(test_date, hour, minute)
        
        print(f"\n日期：{year}年{month}月{day}日 {hour}:{minute}")
        print(f"年干支：{result['年干支']}")
        print(f"月干支：{result['月干支']}")
        print(f"日干支：{result['日干支']}")
        print(f"时干支：{result['时干支']}")
    except Exception as e:
        print(f"错误：{e}")


def format_date_menu():
    """日期格式转换菜单"""
    print("\n--- 日期格式转换 ---")
    try:
        year = int(input("请输入年份（例如：2024）："))
        month = int(input("请输入月份（1-12）："))
        day = int(input("请输入日期（1-31）："))
        
        test_date = date(year, month, day)
        
        print(f"\n原始日期：{test_date}")
        print(f"标准格式：{format_date(test_date, '标准')}")
        print(f"中文格式：{format_date(test_date, '中文')}")
        print(f"ISO格式：{format_date(test_date, 'ISO')}")
        print(f"短格式：{format_date(test_date, '短格式')}")
    except Exception as e:
        print(f"错误：{e}")


def run_all_tests():
    """运行所有测试"""
    print("\n--- 运行所有测试 ---")
    try:
        from 测试.测试日期转换 import main as run_tests
        run_tests()
    except Exception as e:
        print(f"错误：{e}")


def main():
    """主函数"""
    while True:
        print_menu()
        choice = input("请选择功能（0-7）：")
        
        if choice == '0':
            print("\n感谢使用择日模块测试程序！")
            break
        elif choice == '1':
            solar_to_lunar_menu()
        elif choice == '2':
            lunar_to_solar_menu()
        elif choice == '3':
            jie_qi_menu()
        elif choice == '4':
            true_solar_time_menu()
        elif choice == '5':
            gan_zhi_menu()
        elif choice == '6':
            format_date_menu()
        elif choice == '7':
            run_all_tests()
        else:
            print("\n无效选择，请重新输入！")
        
        input("\n按回车键继续...")


if __name__ == '__main__':
    main()
