# -*- coding: utf-8 -*-
"""
测试八字计算
计算1999年4月5日6时的八字
"""

from datetime import date, datetime
from modules.四柱计算器 import calculate_sizhu

# 测试日期：1999年4月5日6时
target_date = date(1999, 4, 5)
hour = 6
minute = 0

# 计算四柱
result = calculate_sizhu(target_date, hour, minute)

print("=" * 80)
print("八字计算测试")
print("=" * 80)
print(f"日期: 1999-04-05 {hour:02d}:{minute:02d}")
print(f"年柱: {result['年柱']}")
print(f"月柱: {result['月柱']}")
print(f"日柱: {result['日柱']}")
print(f"时柱: {result['时柱']}")
print("=" * 80)

# 预期结果
print("预期结果:")
print("年柱: 己卯")
print("月柱: 丁卯")
print("日柱: 丁亥")
print("时柱: 癸卯")
print("=" * 80)

# 检查结果是否正确
if result['年柱'] == '己卯' and result['月柱'] == '丁卯' and result['日柱'] == '丁亥' and result['时柱'] == '癸卯':
    print("✓ 计算结果与预期一致！")
else:
    print("✗ 计算结果与预期不一致！")
