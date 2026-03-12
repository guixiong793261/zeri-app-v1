# -*- coding: utf-8 -*-
"""
全面验证1998年10月13日 0:00的四柱计算
"""

import sys
import os

# 添加核心模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '核心模块'))

from datetime import date, datetime, timedelta

class AuthoritativeSiZhuCalculator:
    """
    权威四柱计算器
    使用标准方法计算四柱
    """
    
    TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 标准节气日期（近似值）
    STANDARD_JIE_QI = [
        (1, 5, '小寒'),
        (1, 20, '大寒'),
        (2, 4, '立春'),
        (2, 19, '雨水'),
        (3, 6, '惊蛰'),
        (3, 21, '春分'),
        (4, 5, '清明'),
        (4, 20, '谷雨'),
        (5, 5, '立夏'),
        (5, 21, '小满'),
        (6, 6, '芒种'),
        (6, 21, '夏至'),
        (7, 7, '小暑'),
        (7, 23, '大暑'),
        (8, 7, '立秋'),
        (8, 23, '处暑'),
        (9, 7, '白露'),
        (9, 23, '秋分'),
        (10, 8, '寒露'),
        (10, 23, '霜降'),
        (11, 7, '立冬'),
        (11, 22, '小雪'),
        (12, 7, '大雪'),
        (12, 22, '冬至')
    ]
    
    @classmethod
    def calculate_year_gan_zhi(cls, year, month, day):
        """
        计算年柱干支
        """
        # 年柱以立春为界
        if month < 2 or (month == 2 and day < 4):
            year -= 1
        
        # 计算年干
        last_digit = year % 10
        gan_value = last_digit - 3
        if gan_value < 0:
            gan_value += 10
        gan_index = (gan_value - 1) % 10
        
        # 计算年支
        remainder = (year - 3) % 12
        if remainder == 0:
            zhi_index = 11
        else:
            zhi_index = remainder - 1
        
        return cls.TIAN_GAN[gan_index] + cls.DI_ZHI[zhi_index]
    
    @classmethod
    def get_lunar_month(cls, year, month, day):
        """
        根据节气确定农历月份
        """
        current_date = date(year, month, day)
        
        for i, (jq_month, jq_day, jq_name) in enumerate(cls.STANDARD_JIE_QI):
            jq_date = date(year, jq_month, jq_day)
            
            if i == len(cls.STANDARD_JIE_QI) - 1:
                return 11
            
            next_jq_month, next_jq_day, next_jq_name = cls.STANDARD_JIE_QI[i + 1]
            next_jq_date = date(year, next_jq_month, next_jq_day)
            
            if jq_date <= current_date < next_jq_date:
                if i == 0 or i == 1:
                    return 12
                elif i == 2:
                    return 1
                elif i == 4:
                    return 2
                elif i == 6:
                    return 3
                elif i == 8:
                    return 4
                elif i == 10:
                    return 5
                elif i == 12:
                    return 6
                elif i == 14:
                    return 7
                elif i == 16:
                    return 8
                elif i == 18:
                    return 9
                elif i == 20:
                    return 10
                elif i == 22:
                    return 11
                else:
                    return cls._get_month_from_zhong_qi(i)
        
        return month
    
    @staticmethod
    def _get_month_from_zhong_qi(index):
        """
        根据中气索引确定月份
        """
        if index == 3:
            return 1
        elif index == 5:
            return 2
        elif index == 7:
            return 3
        elif index == 9:
            return 4
        elif index == 11:
            return 5
        elif index == 13:
            return 6
        elif index == 15:
            return 7
        elif index == 17:
            return 8
        elif index == 19:
            return 9
        elif index == 21:
            return 10
        elif index == 23:
            return 11
        else:
            return 1
    
    @classmethod
    def calculate_month_gan_zhi(cls, year_gan_zhi, year, month, day):
        """
        计算月柱干支
        """
        lunar_month = cls.get_lunar_month(year, month, day)
        
        # 计算月干
        year_gan = year_gan_zhi[0]
        year_gan_number = cls.TIAN_GAN.index(year_gan) + 1
        
        month_gan_value = year_gan_number * 2 + lunar_month
        while month_gan_value > 10:
            month_gan_value -= 10
        month_gan_index = month_gan_value - 1
        month_gan = cls.TIAN_GAN[month_gan_index]
        
        # 计算月支
        month_zhi = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'][lunar_month - 1]
        
        return month_gan + month_zhi
    
    @classmethod
    def calculate_day_gan_zhi(cls, target_date):
        """
        计算日柱干支
        使用2000年1月1日（戊午日）作为参考
        """
        base_date = date(2000, 1, 1)
        days_diff = (target_date - base_date).days
        
        if days_diff >= 0:
            gan_index = (days_diff - 5) % 10
            if gan_index < 0:
                gan_index += 10
            zhi_index = (days_diff - 5) % 12
            if zhi_index < 0:
                zhi_index += 12
        else:
            days_diff_abs = abs(days_diff)
            gan_remainder = (days_diff_abs + 5) % 10
            gan_index = (10 - gan_remainder) % 10
            zhi_remainder = (days_diff_abs + 5) % 12
            zhi_index = (12 - zhi_remainder) % 12
        
        return cls.TIAN_GAN[gan_index] + cls.DI_ZHI[zhi_index]
    
    @classmethod
    def calculate_hour_gan_zhi(cls, day_gan_zhi, hour):
        """
        计算时柱干支
        """
        day_gan = day_gan_zhi[0]
        day_gan_number = cls.TIAN_GAN.index(day_gan) + 1
        
        # 计算时支
        if hour < 1:
            hour_zhi_number = 1
        elif hour < 3:
            hour_zhi_number = 2
        elif hour < 5:
            hour_zhi_number = 3
        elif hour < 7:
            hour_zhi_number = 4
        elif hour < 9:
            hour_zhi_number = 5
        elif hour < 11:
            hour_zhi_number = 6
        elif hour < 13:
            hour_zhi_number = 7
        elif hour < 15:
            hour_zhi_number = 8
        elif hour < 17:
            hour_zhi_number = 9
        elif hour < 19:
            hour_zhi_number = 10
        elif hour < 21:
            hour_zhi_number = 11
        else:
            hour_zhi_number = 12
        
        # 计算时干
        hour_gan_value = day_gan_number * 2 + hour_zhi_number - 2
        hour_gan_index = (hour_gan_value - 1) % 10
        if hour_gan_index < 0:
            hour_gan_index += 10
        hour_gan = cls.TIAN_GAN[hour_gan_index]
        
        # 计算时支
        hour_zhi = cls.DI_ZHI[hour_zhi_number - 1]
        
        return hour_gan + hour_zhi
    
    @classmethod
    def calculate_si_zhu(cls, target_date, hour=12, minute=0):
        """
        计算完整四柱
        """
        # 计算年柱
        year_gan_zhi = cls.calculate_year_gan_zhi(target_date.year, target_date.month, target_date.day)
        
        # 计算月柱
        month_gan_zhi = cls.calculate_month_gan_zhi(year_gan_zhi, target_date.year, target_date.month, target_date.day)
        
        # 计算日柱
        day_gan_zhi = cls.calculate_day_gan_zhi(target_date)
        
        # 计算时柱
        hour_gan_zhi = cls.calculate_hour_gan_zhi(day_gan_zhi, hour)
        
        return {
            '年柱': year_gan_zhi,
            '月柱': month_gan_zhi,
            '日柱': day_gan_zhi,
            '时柱': hour_gan_zhi
        }

# 测试1998年10月13日 0:00的四柱计算
print("=== 1998年10月13日 0:00 四柱计算验证 ===")

test_date = date(1998, 10, 13)
hour = 0
minute = 0

# 使用权威计算器计算
result = AuthoritativeSiZhuCalculator.calculate_si_zhu(test_date, hour, minute)

print(f"日期: {test_date} {hour:02d}:{minute:02d}")
print(f"年柱: {result['年柱']}")
print(f"月柱: {result['月柱']}")
print(f"日柱: {result['日柱']}")
print(f"时柱: {result['时柱']}")

# 对比用户提供的结果
user_result = {
    '年柱': '戊寅',
    '月柱': '壬戌',
    '日柱': '甲午',
    '时柱': '甲子'
}

print("\n=== 对比结果 ===")
for key in ['年柱', '月柱', '日柱', '时柱']:
    match = "✓" if result[key] == user_result[key] else "✗"
    print(f"{key}: {result[key]} vs {user_result[key]} {match}")

# 验证日柱计算
print("\n=== 日柱计算验证 ===")
base_date = date(2000, 1, 1)
days_diff = (test_date - base_date).days
print(f"与2000年1月1日的天数差: {days_diff}")
print(f"(days_diff - 5) % 10 = {(days_diff - 5) % 10} → 日干: {AuthoritativeSiZhuCalculator.TIAN_GAN[(days_diff - 5) % 10]}")
print(f"(days_diff - 5) % 12 = {(days_diff - 5) % 12} → 日支: {AuthoritativeSiZhuCalculator.DI_ZHI[(days_diff - 5) % 12]}")

# 验证时柱计算
print("\n=== 时柱计算验证 ===")
day_gan = result['日柱'][0]
day_gan_number = AuthoritativeSiZhuCalculator.TIAN_GAN.index(day_gan) + 1
hour_zhi_number = 1  # 子时
print(f"日干: {day_gan} (序号: {day_gan_number})")
print(f"时支: 子 (序号: {hour_zhi_number})")
hour_gan_value = day_gan_number * 2 + hour_zhi_number - 2
print(f"时干计算值: {hour_gan_value}")
hour_gan_index = (hour_gan_value - 1) % 10
print(f"时干索引: {hour_gan_index} → 时干: {AuthoritativeSiZhuCalculator.TIAN_GAN[hour_gan_index]}")
