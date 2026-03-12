# -*- coding: utf-8 -*-
"""
验证月柱计算逻辑，确保正确处理节气分界
"""

import sys
import os

# 添加核心模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '核心模块'))

from datetime import date, datetime
from 精确节气数据 import JieQiCalculator
from 公式计算四柱 import FormulaSiZhuCalculator

# 测试1998年的节气数据
print("=== 1998年节气数据 ===")
calculator = JieQiCalculator()
jie_qi_list = calculator.get_year_jie_qi(1998)

if jie_qi_list:
    for jq in jie_qi_list:
        if '寒露' in jq['名称'] or '立冬' in jq['名称']:
            print(f"{jq['名称']}: {jq['时间']}")

# 测试1998年10月13日的月柱计算
print("\n=== 1998年10月13日 0:00 月柱计算 ===")

# 使用精确节气数据
calc_precise = FormulaSiZhuCalculator(use_precise_jie_qi=True)
result_precise = calc_precise.calculate_si_zhu(date(1998, 10, 13), 0, 0)
print(f"使用精确节气数据: {result_precise['月柱']}")

# 使用简化节气数据
calc_simple = FormulaSiZhuCalculator(use_precise_jie_qi=False)
result_simple = calc_simple.calculate_si_zhu(date(1998, 10, 13), 0, 0)
print(f"使用简化节气数据: {result_simple['月柱']}")

# 验证用户提供的结果
print(f"用户提供的结果: 壬戌")

# 检查1998年10月13日的节气信息
print("\n=== 1998年10月13日 0:00 节气信息 ===")
jie_qi_info = calculator.get_jie_qi_by_date(1998, 10, 13, 0, 0)
if jie_qi_info:
    current_jq = jie_qi_info['当前节气']
    next_jq = jie_qi_info['下一节气']
    if current_jq:
        print(f"当前节气: {current_jq['名称']} - {current_jq['时间']}")
    if next_jq:
        print(f"下一节气: {next_jq['名称']} - {next_jq['时间']}")

# 检查月柱计算逻辑
print("\n=== 月柱计算逻辑验证 ===")
# 计算1998年的年柱
year_gan_zhi = calc_precise.calculate_year_gan_zhi(1998, 10, 13)
print(f"年柱: {year_gan_zhi}")

# 检查年干
year_gan = year_gan_zhi[0]
year_gan_number = calc_precise.tian_gan.index(year_gan) + 1
print(f"年干: {year_gan} (序号: {year_gan_number})")

# 检查农历月份
lunar_month = calculator.get_month_by_jie_qi(1998, 10, 13, 0, 0)
print(f"农历月份: {lunar_month}")

# 计算月干
month_gan_value = year_gan_number * 2 + lunar_month
while month_gan_value > 10:
    month_gan_value -= 10
month_gan_index = month_gan_value - 1
month_gan = calc_precise.tian_gan[month_gan_index]
print(f"月干: {month_gan} (计算值: {month_gan_value})")

# 计算月支
month_zhi = calc_precise.month_zhi[lunar_month - 1]
print(f"月支: {month_zhi}")
print(f"计算得到的月柱: {month_gan + month_zhi}")
