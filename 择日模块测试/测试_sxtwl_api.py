# -*- coding: utf-8 -*-
"""
测试 sxtwl 库的 API
"""

import sxtwl
from datetime import date, datetime

# 测试 fromSolar 方法
day_obj = sxtwl.fromSolar(2024, 1, 1)
print("=== 测试 fromSolar 方法 ===")
print(f"类型: {type(day_obj)}")
print(f"可用方法/属性: {dir(day_obj)}")

# 测试获取农历信息
print("\n=== 测试获取农历信息 ===")
try:
    print(f"getLunarYear(): {day_obj.getLunarYear()}")
except Exception as e:
    print(f"getLunarYear() 错误: {e}")

try:
    print(f"getLunarMonth(): {day_obj.getLunarMonth()}")
except Exception as e:
    print(f"getLunarMonth() 错误: {e}")

try:
    print(f"getLunarDay(): {day_obj.getLunarDay()}")
except Exception as e:
    print(f"getLunarDay() 错误: {e}")

try:
    print(f"isLunarLeap: {day_obj.isLunarLeap}")
except Exception as e:
    print(f"isLunarLeap 错误: {e}")

# 测试获取公历信息
print("\n=== 测试获取公历信息 ===")
try:
    print(f"getSolarYear(): {day_obj.getSolarYear()}")
except Exception as e:
    print(f"getSolarYear() 错误: {e}")

try:
    print(f"getSolarMonth(): {day_obj.getSolarMonth()}")
except Exception as e:
    print(f"getSolarMonth() 错误: {e}")

try:
    print(f"getSolarDay(): {day_obj.getSolarDay()}")
except Exception as e:
    print(f"getSolarDay() 错误: {e}")

# 测试节气信息
print("\n=== 测试节气信息 ===")
try:
    jq_list = sxtwl.getJieQiByYear(2024)
    print(f"节气数量: {len(jq_list)}")
    
    # 测试 JD2DD
    jd = jq_list[0].jd
    dd = sxtwl.JD2DD(jd)
    print(f"JD2DD 结果类型: {type(dd)}")
    print(f"JD2DD 可用属性: {dir(dd)}")
    print(f"Y: {dd.Y}, M: {dd.M}, D: {dd.D}, h: {dd.h}, m: {dd.m}, s: {dd.s}")
except Exception as e:
    print(f"节气测试错误: {e}")