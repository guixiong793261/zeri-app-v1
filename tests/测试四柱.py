# -*- coding: utf-8 -*-
"""
================================================================================
四柱计算测试
================================================================================
验证年柱、月柱、日柱、时柱计算的正确性
================================================================================
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date
from modules.四柱计算器 import calculate_sizhu

class TestSiZhu(unittest.TestCase):
    """四柱计算测试"""
    
    def test_year_pillar(self):
        """测试年柱计算"""
        # 测试1972年1月1日（立春前，属于1971年辛亥年）
        result = calculate_sizhu(date(1972, 1, 1))
        self.assertEqual(result['年柱'], '辛亥')
        
        # 测试1972年2月5日（立春后，属于1972年壬子年）
        result = calculate_sizhu(date(1972, 2, 5))
        self.assertEqual(result['年柱'], '壬子')
        
        # 测试1998年
        result = calculate_sizhu(date(1998, 2, 5))
        self.assertEqual(result['年柱'], '戊寅')
        
        # 测试2023年
        result = calculate_sizhu(date(2023, 2, 5))
        self.assertEqual(result['年柱'], '癸卯')
    
    def test_month_pillar(self):
        """测试月柱计算"""
        # 测试1972年5月11日（立夏后，巳月）
        result = calculate_sizhu(date(1972, 5, 11))
        self.assertEqual(result['月柱'], '乙巳')
        
        # 测试1998年10月13日（寒露后，戌月）
        result = calculate_sizhu(date(1998, 10, 13))
        self.assertEqual(result['月柱'], '壬戌')
        
        # 测试1999年4月5日（清明后，辰月）
        # 注意：1999年4月5日清明在12:00，所以6时还在卯月
        result = calculate_sizhu(date(1999, 4, 5), 6, 0)
        self.assertEqual(result['月柱'], '丁卯')
        
        # 测试1999年4月5日14时（清明后，辰月）
        result = calculate_sizhu(date(1999, 4, 5), 14, 0)
        self.assertEqual(result['月柱'], '戊辰')
    
    def test_day_pillar(self):
        """测试日柱计算"""
        # 测试1972年1月8日
        result = calculate_sizhu(date(1972, 1, 8))
        self.assertEqual(result['日柱'], '戊戌')
        
        # 测试1972年5月11日
        result = calculate_sizhu(date(1972, 5, 11))
        self.assertEqual(result['日柱'], '壬寅')
        
        # 测试1998年10月13日
        result = calculate_sizhu(date(1998, 10, 13))
        self.assertEqual(result['日柱'], '癸巳')
        
        # 测试1999年4月5日
        result = calculate_sizhu(date(1999, 4, 5))
        self.assertEqual(result['日柱'], '丁亥')
    
    def test_hour_pillar(self):
        """测试时柱计算"""
        # 测试1998年10月13日23点（晚子时）
        # 晚子时用次日日干起时干
        result = calculate_sizhu(date(1998, 10, 13), 23, 0)
        # 10月14日是甲午日，甲日的子时是甲子
        self.assertEqual(result['时柱'], '甲子')
        
        # 测试1972年5月11日8点（辰时）
        result = calculate_sizhu(date(1972, 5, 11), 8, 0)
        # 5月11日是壬寅日，壬日的辰时是甲辰
        self.assertEqual(result['时柱'], '甲辰')
        
        # 测试1972年1月8日8点（辰时）
        result = calculate_sizhu(date(1972, 1, 8), 8, 0)
        # 1月8日是戊戌日，戊日的辰时是丙辰
        self.assertEqual(result['时柱'], '丙辰')

if __name__ == '__main__':
    unittest.main()
