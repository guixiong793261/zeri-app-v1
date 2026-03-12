# -*- coding: utf-8 -*-
"""
测试sxtwl库的月柱计算
"""

import sxtwl
from modules.四柱计算器 import TIAN_GAN, DI_ZHI

# 测试日期：1999年4月5日
year = 1999
month = 4
day = 5

# 使用sxtwl库计算
day_obj = sxtwl.fromSolar(year, month, day)
month_gz = day_obj.getMonthGZ()

month_gan = TIAN_GAN[month_gz.tg]
month_zhi = DI_ZHI[month_gz.dz]

print("sxtwl库计算结果:")
print(f"月柱: {month_gan + month_zhi}")
print(f"月干: {month_gan}")
print(f"月支: {month_zhi}")

# 预期结果
print("\n预期结果:")
print("月柱: 丁卯")
print("月干: 丁")
print("月支: 卯")
