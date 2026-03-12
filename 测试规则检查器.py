# 测试规则检查器模块
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.四柱计算器 import calculate_sizhu
from modules.rules.嫁娶规则 import MarriageRuleChecker
from modules.rules.安葬规则 import BurialRuleChecker
from modules.rules.作灶规则 import StoveRuleChecker
from datetime import datetime

print("=== 测试规则检查器模块 ===")

# 测试用例
# 1. 嫁娶宜日测试（日支为卯，应包含"嫁娶"宜事）
marriage_date = datetime(2024, 5, 20, 12, 0, 0)
# 2. 安葬忌日测试（日支为亥，应包含"安葬"忌事）
burial_date = datetime(2024, 5, 22, 12, 0, 0)
# 3. 作灶测试（日支为午，灶向为丙，火生土，应包含"丙向作灶"）
stove_date = datetime(2024, 5, 21, 12, 0, 0)

# 测试嫁娶规则
print("\n=== 测试嫁娶规则 ===")
marriage_sizhu = calculate_sizhu(marriage_date)
print(f"测试日期: {marriage_date.strftime('%Y-%m-%d')}")
print(f"日支: {marriage_sizhu['day_zhi']}")

marriage_checker = MarriageRuleChecker()
you_list, ji_list = marriage_checker.check(marriage_sizhu)
print(f"宜事项: {you_list}")
print(f"忌事项: {ji_list}")

if '嫁娶' in you_list:
    print("✓ 测试通过：嫁娶宜日包含'嫁娶'宜事")
else:
    print("✗ 测试不通过：嫁娶宜日未包含'嫁娶'宜事")

# 测试安葬规则
print("\n=== 测试安葬规则 ===")
burial_sizhu = calculate_sizhu(burial_date)
print(f"测试日期: {burial_date.strftime('%Y-%m-%d')}")
print(f"日支: {burial_sizhu['day_zhi']}")

burial_checker = BurialRuleChecker()
you_list, ji_list = burial_checker.check(burial_sizhu)
print(f"宜事项: {you_list}")
print(f"忌事项: {ji_list}")

if '安葬' in ji_list:
    print("✓ 测试通过：安葬忌日包含'安葬'忌事")
else:
    print("✗ 测试不通过：安葬忌日未包含'安葬'忌事")

# 测试作灶规则
print("\n=== 测试作灶规则 ===")
stove_sizhu = calculate_sizhu(stove_date)
print(f"测试日期: {stove_date.strftime('%Y-%m-%d')}")
print(f"日支: {stove_sizhu['day_zhi']}")

stove_checker = StoveRuleChecker()
# 灶向为丙（火），日支为午（火），火生土？需要检查五行关系
# 实际上，丙的五行是火，午的五行也是火，火生土，所以应该检查灶向为土的情况
# 重新选择灶向为坤（土），日支为午（火），火生土
zaoxiang = '坤'  # 坤的五行是土
you_list, ji_list = stove_checker.check(stove_sizhu, zaoxiang=zaoxiang)
print(f"灶向: {zaoxiang}")
print(f"宜事项: {you_list}")
print(f"忌事项: {ji_list}")

if f'{zaoxiang}向作灶' in you_list:
    print("✓ 测试通过：灶向与日支相生日包含'灶向宜作灶'")
else:
    print("✗ 测试不通过：灶向与日支相生日未包含'灶向宜作灶'")

# 测试另一个作灶案例：灶向为木，日支为火，木生火
print("\n=== 测试作灶规则（木生火） ===")
zaoxiang2 = '寅'  # 寅的五行是木
you_list, ji_list = stove_checker.check(stove_sizhu, zaoxiang=zaoxiang2)
print(f"灶向: {zaoxiang2}")
print(f"宜事项: {you_list}")
print(f"忌事项: {ji_list}")

if f'{zaoxiang2}向作灶' in you_list:
    print("✓ 测试通过：灶向与日支相生日包含'灶向宜作灶'")
else:
    print("✗ 测试不通过：灶向与日支相生日未包含'灶向宜作灶'")

print("\n=== 测试完成 ===")
