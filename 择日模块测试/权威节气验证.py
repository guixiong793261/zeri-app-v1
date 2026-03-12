# -*- coding: utf-8 -*-
"""
使用权威节气数据源验证月柱计算
"""

import sys
import os

# 添加核心模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '核心模块'))

from datetime import date, datetime
from 公式计算四柱 import FormulaSiZhuCalculator

class AuthoritativeJieQi:
    """
    权威节气数据类
    基于标准节气日期计算
    """
    
    # 标准节气日期（近似值，实际会有1-2天的误差）
    # 格式：(月份, 日期, 节气名称)
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
    def get_month_by_jie_qi(cls, year, month, day, hour=0, minute=0):
        """
        根据权威节气数据确定农历月份
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            hour: 小时
            minute: 分钟
            
        Returns:
            int: 农历月份（1-12）
        """
        current_date = datetime(year, month, day, hour, minute)
        
        # 找到当前日期所在的节气区间
        for i, (jq_month, jq_day, jq_name) in enumerate(cls.STANDARD_JIE_QI):
            jq_date = datetime(year, jq_month, jq_day)
            
            # 检查是否是最后一个节气
            if i == len(cls.STANDARD_JIE_QI) - 1:
                # 最后一个节气（冬至），对应农历十一月
                return 11
            
            # 下一个节气
            next_jq_month, next_jq_day, next_jq_name = cls.STANDARD_JIE_QI[i + 1]
            next_jq_date = datetime(year, next_jq_month, next_jq_day)
            
            # 检查当前日期是否在两个节气之间
            if jq_date <= current_date < next_jq_date:
                # 根据节气确定月份
                # 立春(2) = 正月, 惊蛰(4) = 二月, 清明(6) = 三月, ...
                # 小寒(0) = 十二月, 大寒(1) = 十二月
                if i == 0 or i == 1:  # 小寒、大寒
                    return 12  # 农历十二月
                elif i == 2:  # 立春
                    return 1   # 农历正月
                elif i == 4:  # 惊蛰
                    return 2   # 农历二月
                elif i == 6:  # 清明
                    return 3   # 农历三月
                elif i == 8:  # 立夏
                    return 4   # 农历四月
                elif i == 10:  # 芒种
                    return 5   # 农历五月
                elif i == 12:  # 小暑
                    return 6   # 农历六月
                elif i == 14:  # 立秋
                    return 7   # 农历七月
                elif i == 16:  # 白露
                    return 8   # 农历八月
                elif i == 18:  # 寒露
                    return 9   # 农历九月
                elif i == 20:  # 立冬
                    return 10  # 农历十月
                elif i == 22:  # 大雪
                    return 11  # 农历十一月
                else:
                    # 对于中气，使用前一个节气的月份
                    return cls._get_month_from_zhong_qi(i)
        
        return month
    
    @staticmethod
    def _get_month_from_zhong_qi(index):
        """
        根据中气索引确定月份
        """
        if index == 3:   # 雨水
            return 1   # 正月
        elif index == 5:  # 春分
            return 2   # 二月
        elif index == 7:  # 谷雨
            return 3   # 三月
        elif index == 9:  # 小满
            return 4   # 四月
        elif index == 11:  # 夏至
            return 5   # 五月
        elif index == 13:  # 大暑
            return 6   # 六月
        elif index == 15:  # 处暑
            return 7   # 七月
        elif index == 17:  # 秋分
            return 8   # 八月
        elif index == 19:  # 霜降
            return 9   # 九月
        elif index == 21:  # 小雪
            return 10  # 十月
        elif index == 23:  # 冬至
            return 11  # 十一月
        else:
            return 1

# 测试1998年10月13日的月柱计算
print("=== 权威节气数据源验证 ===")

# 使用权威节气数据计算农历月份
lunar_month = AuthoritativeJieQi.get_month_by_jie_qi(1998, 10, 13, 0, 0)
print(f"1998年10月13日 0:00 的农历月份: {lunar_month}")

# 计算正确的月柱
calculator = FormulaSiZhuCalculator(use_precise_jie_qi=False)
year_gan_zhi = calculator.calculate_year_gan_zhi(1998, 10, 13)
year_gan = year_gan_zhi[0]
year_gan_number = calculator.tian_gan.index(year_gan) + 1

# 计算月干
month_gan_value = year_gan_number * 2 + lunar_month
while month_gan_value > 10:
    month_gan_value -= 10
month_gan_index = month_gan_value - 1
month_gan = calculator.tian_gan[month_gan_index]

# 计算月支
month_zhi = calculator.month_zhi[lunar_month - 1]

correct_month_gan_zhi = month_gan + month_zhi
print(f"正确的月柱: {correct_month_gan_zhi}")

# 验证用户提供的结果
user_month_gan_zhi = "壬戌"
print(f"用户提供的月柱: {user_month_gan_zhi}")
print(f"是否匹配: {'✓' if correct_month_gan_zhi == user_month_gan_zhi else '✗'}")

# 显示1998年10月的节气信息
print("\n=== 1998年10月节气信息 ===")
for jq_month, jq_day, jq_name in AuthoritativeJieQi.STANDARD_JIE_QI:
    if jq_month == 10:
        print(f"{jq_name}: 10月{jq_day}日")

# 验证其他日期
print("\n=== 验证其他日期 ===")
test_dates = [
    (1998, 10, 7, "寒露前"),
    (1998, 10, 8, "寒露当天"),
    (1998, 10, 9, "寒露后"),
    (1998, 10, 22, "霜降前"),
    (1998, 10, 23, "霜降当天"),
    (1998, 10, 24, "霜降后"),
]

for year, month, day, description in test_dates:
    lm = AuthoritativeJieQi.get_month_by_jie_qi(year, month, day)
    print(f"{year}-{month:02d}-{day:02d} ({description}): 农历{lm}月")
