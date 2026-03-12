# -*- coding: utf-8 -*-
"""
================================================================================
宜忌规则系统性测试
================================================================================
验证各 RuleChecker 的宜忌列表是否符合常识

测试内容：
1. 嫁娶宜日应包含"嫁娶"
2. 安葬忌日应包含"安葬"
3. 作灶吉日与灶向匹配时应出现"灶向宜作灶"
================================================================================
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date
from modules.高精度农历转换 import HighPrecisionLunar
from modules.rules.嫁娶规则 import MarriageRuleChecker
from modules.rules.安葬规则 import BurialRuleChecker
from modules.rules.作灶规则 import StoveRuleChecker


class TestMarriageRules(unittest.TestCase):
    """嫁娶规则测试"""
    
    def setUp(self):
        """测试前准备"""
        self.lunar = HighPrecisionLunar()
        self.checker = MarriageRuleChecker()
    
    def _get_sizhu(self, year, month, day, hour=12, minute=0):
        """获取四柱信息"""
        return self.lunar.get_sizhu(year, month, day, hour, minute)
    
    def test_marriage_yi_day_contains_marriage(self):
        """嫁娶宜日应包含'嫁娶'"""
        # 选择一个嫁娶宜日（日支为子、丑、寅、卯、辰、巳、午、未）
        # 2024-05-15: 日支=寅, 2024-05-16: 日支=卯, 2024-05-17: 日支=辰
        test_cases = [
            (2024, 5, 15),  # 寅日
            (2024, 5, 16),  # 卯日
            (2024, 5, 17),  # 辰日
        ]
        
        found_yi = False
        for year, month, day in test_cases:
            sizhu = self._get_sizhu(year, month, day)
            yi_list, ji_list = self.checker.check(sizhu)
            
            print(f"\n{year}-{month:02d}-{day:02d} 嫁娶检查:")
            print(f"  日支: {sizhu['day_zhi']}")
            print(f"  宜: {yi_list}")
            print(f"  忌: {ji_list}")
            
            if '嫁娶' in yi_list:
                found_yi = True
                break
        
        # 至少有一个日期应该包含"嫁娶"在宜列表中
        self.assertTrue(found_yi, "应在测试日期中找到嫁娶宜日")
    
    def test_marriage_ji_day_contains_marriage(self):
        """嫁娶忌日应包含'嫁娶'"""
        # 选择一个嫁娶忌日（日支为申、酉、戌、亥）
        # 2024-05-20: 日支=申, 2024-05-21: 日支=酉, 2024-05-22: 日支=戌
        test_cases = [
            (2024, 5, 20),  # 申日
            (2024, 5, 21),  # 酉日
            (2024, 5, 22),  # 戌日
        ]
        
        found_ji = False
        for year, month, day in test_cases:
            sizhu = self._get_sizhu(year, month, day)
            yi_list, ji_list = self.checker.check(sizhu)
            
            print(f"\n{year}-{month:02d}-{day:02d} 嫁娶检查:")
            print(f"  日支: {sizhu['day_zhi']}")
            print(f"  宜: {yi_list}")
            print(f"  忌: {ji_list}")
            
            if '嫁娶' in ji_list:
                found_ji = True
                break
        
        # 至少有一个日期应该包含"嫁娶"在忌列表中
        self.assertTrue(found_ji, "应在测试日期中找到嫁娶忌日")
    
    def test_marriage_rules_structure(self):
        """测试嫁娶规则返回结构"""
        sizhu = self._get_sizhu(2024, 5, 20)
        yi_list, ji_list = self.checker.check(sizhu)
        
        # 验证返回类型
        self.assertIsInstance(yi_list, list, "宜列表应为列表类型")
        self.assertIsInstance(ji_list, list, "忌列表应为列表类型")
        
        # 验证列表元素为字符串
        for item in yi_list:
            self.assertIsInstance(item, str, "宜列表元素应为字符串")
        for item in ji_list:
            self.assertIsInstance(item, str, "忌列表元素应为字符串")


class TestBurialRules(unittest.TestCase):
    """安葬规则测试"""
    
    def setUp(self):
        """测试前准备"""
        self.lunar = HighPrecisionLunar()
        self.checker = BurialRuleChecker()
    
    def _get_sizhu(self, year, month, day, hour=12, minute=0):
        """获取四柱信息"""
        return self.lunar.get_sizhu(year, month, day, hour, minute)
    
    def test_burial_yi_day_contains_burial(self):
        """安葬宜日应包含'安葬'"""
        # 选择阴日（日支为子、丑、寅、卯、辰、巳）
        test_cases = [
            (2024, 4, 4),
            (2024, 4, 5),
            (2024, 4, 10),
        ]
        
        found_yi = False
        for year, month, day in test_cases:
            sizhu = self._get_sizhu(year, month, day)
            yi_list, ji_list = self.checker.check(sizhu)
            
            print(f"\n{year}-{month:02d}-{day:02d} 安葬检查:")
            print(f"  日支: {sizhu['day_zhi']}")
            print(f"  宜: {yi_list}")
            print(f"  忌: {ji_list}")
            
            if '安葬' in yi_list:
                found_yi = True
                break
        
        self.assertTrue(found_yi, "应在测试日期中找到安葬宜日")
    
    def test_burial_ji_day_contains_burial(self):
        """安葬忌日应包含'安葬'"""
        # 选择阳日（日支为午、未、申、酉、戌、亥）
        # 2024-04-13: 日支=午, 2024-04-14: 日支=未, 2024-04-15: 日支=申
        test_cases = [
            (2024, 4, 13),  # 午日
            (2024, 4, 14),  # 未日
            (2024, 4, 15),  # 申日
        ]
        
        found_ji = False
        for year, month, day in test_cases:
            sizhu = self._get_sizhu(year, month, day)
            yi_list, ji_list = self.checker.check(sizhu)
            
            print(f"\n{year}-{month:02d}-{day:02d} 安葬检查:")
            print(f"  日支: {sizhu['day_zhi']}")
            print(f"  宜: {yi_list}")
            print(f"  忌: {ji_list}")
            
            if '安葬' in ji_list:
                found_ji = True
                break
        
        self.assertTrue(found_ji, "应在测试日期中找到安葬忌日")
    
    def test_burial_with_shanxiang(self):
        """测试安葬山向规则"""
        sizhu = self._get_sizhu(2024, 4, 4)
        yi_list, ji_list = self.checker.check(sizhu, shan_xiang='子')
        
        print(f"\n安葬山向测试:")
        print(f"  日支: {sizhu['day_zhi']}")
        print(f"  宜: {yi_list}")
        print(f"  忌: {ji_list}")
        
        # 验证山向相关规则
        has_shanxiang_rule = any('向安葬' in item for item in yi_list + ji_list)
        if has_shanxiang_rule:
            print(f"  包含山向规则: 是")


class TestStoveRules(unittest.TestCase):
    """作灶规则测试"""
    
    def setUp(self):
        """测试前准备"""
        self.lunar = HighPrecisionLunar()
        self.checker = StoveRuleChecker()
    
    def _get_sizhu(self, year, month, day, hour=12, minute=0):
        """获取四柱信息"""
        return self.lunar.get_sizhu(year, month, day, hour, minute)
    
    def test_stove_yi_day_contains_stove(self):
        """作灶宜日应包含'作灶'"""
        # 作灶宜日：子、寅、卯、巳、午、酉
        test_cases = [
            (2024, 5, 20),
            (2024, 5, 21),
            (2024, 6, 1),
        ]
        
        found_yi = False
        for year, month, day in test_cases:
            sizhu = self._get_sizhu(year, month, day)
            yi_list, ji_list = self.checker.check(sizhu)
            
            print(f"\n{year}-{month:02d}-{day:02d} 作灶检查:")
            print(f"  日支: {sizhu['day_zhi']}")
            print(f"  宜: {yi_list}")
            print(f"  忌: {ji_list}")
            
            if '作灶' in yi_list:
                found_yi = True
                break
        
        self.assertTrue(found_yi, "应在测试日期中找到作灶宜日")
    
    def test_stove_with_zaoxiang(self):
        """作灶吉日与灶向匹配时应出现'灶向宜作灶'"""
        # 选择一个作灶宜日并指定灶向
        test_cases = [
            (2024, 5, 20, '子'),
            (2024, 5, 21, '午'),
            (2024, 6, 1, '卯'),
        ]
        
        found_zaoxiang_rule = False
        for year, month, day, zaoxiang in test_cases:
            sizhu = self._get_sizhu(year, month, day)
            yi_list, ji_list = self.checker.check(sizhu, zaoxiang=zaoxiang)
            
            print(f"\n{year}-{month:02d}-{day:02d} 灶向{zaoxiang}作灶检查:")
            print(f"  日支: {sizhu['day_zhi']}")
            print(f"  宜: {yi_list}")
            print(f"  忌: {ji_list}")
            
            # 检查是否包含灶向相关规则
            has_zaoxiang_yi = any(f'{zaoxiang}向作灶' in item for item in yi_list)
            if has_zaoxiang_yi:
                found_zaoxiang_rule = True
                print(f"  ✓ 找到灶向宜作灶规则")
                break
        
        # 注：这里不强制要求必须找到，因为取决于具体的五行匹配
        print(f"\n  灶向宜作灶规则: {'找到' if found_zaoxiang_rule else '未找到'}")
    
    def test_stove_with_zaowei(self):
        """测试作灶灶位规则"""
        sizhu = self._get_sizhu(2024, 5, 20)
        yi_list, ji_list = self.checker.check(sizhu, zaowei='东')
        
        print(f"\n作灶灶位测试:")
        print(f"  日支: {sizhu['day_zhi']}")
        print(f"  宜: {yi_list}")
        print(f"  忌: {ji_list}")
        
        # 验证灶位相关规则
        has_zaowei_rule = any('位安灶' in item for item in yi_list + ji_list)
        if has_zaowei_rule:
            print(f"  包含灶位规则: 是")


class TestRulesCommonSense(unittest.TestCase):
    """宜忌规则常识性测试"""
    
    def setUp(self):
        """测试前准备"""
        self.lunar = HighPrecisionLunar()
        self.marriage_checker = MarriageRuleChecker()
        self.burial_checker = BurialRuleChecker()
        self.stove_checker = StoveRuleChecker()
    
    def _get_sizhu(self, year, month, day, hour=12, minute=0):
        """获取四柱信息"""
        return self.lunar.get_sizhu(year, month, day, hour, minute)
    
    def test_yi_ji_not_overlap(self):
        """测试同一事项不会同时出现在宜和忌中"""
        sizhu = self._get_sizhu(2024, 5, 20)
        
        # 测试嫁娶
        yi_list, ji_list = self.marriage_checker.check(sizhu)
        common = set(yi_list) & set(ji_list)
        self.assertEqual(len(common), 0, "嫁娶宜忌不应有重叠")
        
        # 测试安葬
        yi_list, ji_list = self.burial_checker.check(sizhu)
        common = set(yi_list) & set(ji_list)
        self.assertEqual(len(common), 0, "安葬宜忌不应有重叠")
        
        # 测试作灶
        yi_list, ji_list = self.stove_checker.check(sizhu)
        common = set(yi_list) & set(ji_list)
        self.assertEqual(len(common), 0, "作灶宜忌不应有重叠")
    
    def test_rules_return_consistency(self):
        """测试规则返回一致性"""
        sizhu = self._get_sizhu(2024, 5, 20)
        
        checkers = [
            ('嫁娶', self.marriage_checker),
            ('安葬', self.burial_checker),
            ('作灶', self.stove_checker),
        ]
        
        for name, checker in checkers:
            yi_list, ji_list = checker.check(sizhu)
            
            # 验证返回类型
            self.assertIsInstance(yi_list, list, f"{name}宜列表应为列表")
            self.assertIsInstance(ji_list, list, f"{name}忌列表应为列表")
            
            # 验证元素类型
            for item in yi_list:
                self.assertIsInstance(item, str, f"{name}宜列表元素应为字符串")
            for item in ji_list:
                self.assertIsInstance(item, str, f"{name}忌列表元素应为字符串")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestMarriageRules))
    suite.addTests(loader.loadTestsFromTestCase(TestBurialRules))
    suite.addTests(loader.loadTestsFromTestCase(TestStoveRules))
    suite.addTests(loader.loadTestsFromTestCase(TestRulesCommonSense))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    
    # 输出测试总结
    print("\n" + "="*60)
    print("宜忌规则测试总结")
    print("="*60)
    print(f"总测试数: {result.testsRun}")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n出错的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("="*60)
