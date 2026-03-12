# -*- coding: utf-8 -*-
"""
详细验证1998年10月13日的日柱计算
"""

import sys
import os
from datetime import date, timedelta

class AuthoritativeDayCalculator:
    """
    权威日柱计算器
    """
    
    TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    @classmethod
    def calculate_day_gan_zhi(cls, target_date):
        """
        计算日柱干支
        使用2000年1月1日（戊午日）作为参考
        """
        base_date = date(2000, 1, 1)
        days_diff = (target_date - base_date).days
        
        print(f"参考日期: 2000年1月1日 (戊午日)")
        print(f"目标日期: {target_date}")
        print(f"天数差: {days_diff}")
        
        if days_diff >= 0:
            # 2000年及以后
            print("\n2000年及以后的计算:")
            print(f"(days_diff - 5) = {days_diff - 5}")
            gan_remainder = (days_diff - 5) % 10
            print(f"(days_diff - 5) % 10 = {gan_remainder} → 日干索引: {gan_remainder}")
            zhi_remainder = (days_diff - 5) % 12
            print(f"(days_diff - 5) % 12 = {zhi_remainder} → 日支索引: {zhi_remainder}")
        else:
            # 2000年以前
            print("\n2000年以前的计算:")
            days_diff_abs = abs(days_diff)
            print(f"天数差绝对值: {days_diff_abs}")
            print(f"(days_diff_abs + 5) = {days_diff_abs + 5}")
            gan_remainder = (days_diff_abs + 5) % 10
            print(f"(days_diff_abs + 5) % 10 = {gan_remainder}")
            gan_index = (10 - gan_remainder) % 10
            print(f"10 - 余数 = {10 - gan_remainder} → 日干索引: {gan_index}")
            
            zhi_remainder = (days_diff_abs + 5) % 12
            print(f"(days_diff_abs + 5) % 12 = {zhi_remainder}")
            zhi_index = (12 - zhi_remainder) % 12
            print(f"12 - 余数 = {12 - zhi_remainder} → 日支索引: {zhi_index}")
        
        # 计算最终结果
        gan = cls.TIAN_GAN[gan_index]
        zhi = cls.DI_ZHI[zhi_index]
        print(f"\n计算结果: {gan}{zhi}")
        
        return gan + zhi

# 测试1998年10月13日的日柱计算
print("=== 1998年10月13日 日柱计算验证 ===")
test_date = date(1998, 10, 13)
result = AuthoritativeDayCalculator.calculate_day_gan_zhi(test_date)

# 显示结果
print(f"\n=== 最终结果 ===")
print(f"1998年10月13日的日柱: {result}")

# 检查公式计算四柱模块的日柱计算
print("\n=== 公式计算四柱模块验证 ===")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '核心模块'))
from 公式计算四柱 import FormulaSiZhuCalculator

calculator = FormulaSiZhuCalculator(use_precise_jie_qi=False)
day_gan_zhi = calculator.calculate_day_gan_zhi(test_date)
print(f"公式计算四柱模块结果: {day_gan_zhi}")

# 手动计算验证
print("\n=== 手动计算验证 ===")
# 2000年1月1日是戊午日
# 1998年10月13日到2000年1月1日的天数差
# 1998年10月剩余天数: 31-13 = 18
# 1998年11月: 30
# 1998年12月: 31
# 1999年全年: 365
# 2000年1月1日: 1
# 总天数: 18+30+31+365+1 = 445
# 所以天数差是 -445

days_diff = -445
days_diff_abs = 445

# 计算日干
gan_remainder = (days_diff_abs + 5) % 10
print(f"(445 + 5) % 10 = {gan_remainder}")
print(f"10 - {gan_remainder} = {10 - gan_remainder} → 日干: {AuthoritativeDayCalculator.TIAN_GAN[(10 - gan_remainder) % 10]}")

# 计算日支
zhi_remainder = (days_diff_abs + 5) % 12
print(f"(445 + 5) % 12 = {zhi_remainder}")
print(f"12 - {zhi_remainder} = {12 - zhi_remainder} → 日支: {AuthoritativeDayCalculator.DI_ZHI[(12 - zhi_remainder) % 12]}")
