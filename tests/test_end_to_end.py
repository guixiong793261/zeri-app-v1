# -*- coding: utf-8 -*-
"""
================================================================================
端到端系统性测试
================================================================================
通过主程序选择一段日期（如2026年3月），计算所有事项，检查结果是否无报错，
且评分分布合理。

测试内容：
1. 测试2026年3月所有日期的择日计算
2. 验证所有事项类型都能正常计算
3. 检查评分分布是否合理
4. 验证没有报错信息
================================================================================
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, timedelta
from modules.高精度农历转换 import HighPrecisionLunar
from modules.评分器 import calculate_score

# 导入所有事项类型
EVENT_TYPES = [
    '嫁娶',
    '安葬',
    '修造',
    '作灶',
    '安床',
    '出行',
    '开业',
]


class TestEndToEnd2026March(unittest.TestCase):
    """2026年3月端到端测试"""
    
    def setUp(self):
        """测试前准备"""
        self.lunar = HighPrecisionLunar()
        self.start_date = date(2026, 3, 1)
        self.end_date = date(2026, 3, 31)
    
    def _get_sizhu(self, target_date, hour=12, minute=0):
        """获取四柱信息"""
        return self.lunar.get_sizhu(
            target_date.year, target_date.month, target_date.day,
            hour, minute
        )
    
    def test_all_dates_no_errors(self):
        """测试所有日期计算无报错"""
        errors = []
        total_calculations = 0
        
        current_date = self.start_date
        while current_date <= self.end_date:
            try:
                sizhu = self._get_sizhu(current_date)
                
                # 测试所有事项类型
                for event_type in EVENT_TYPES:
                    try:
                        result = calculate_score(sizhu, event_type)
                        total_calculations += 1
                        
                        # 验证返回结果结构
                        self.assertIn('score', result, f"{current_date} {event_type} 应有score字段")
                        self.assertIn('level', result, f"{current_date} {event_type} 应有level字段")
                        self.assertIn('reason', result, f"{current_date} {event_type} 应有reason字段")
                        
                        # 验证分数范围
                        self.assertIsInstance(result['score'], (int, float), 
                                            f"{current_date} {event_type} score应为数字")
                        self.assertGreaterEqual(result['score'], 0, 
                                              f"{current_date} {event_type} score应>=0")
                        
                    except Exception as e:
                        errors.append(f"{current_date} {event_type}: {str(e)}")
                
            except Exception as e:
                errors.append(f"{current_date} 四柱计算: {str(e)}")
            
            current_date += timedelta(days=1)
        
        print(f"\n2026年3月端到端测试:")
        print(f"  总计算次数: {total_calculations}")
        print(f"  错误次数: {len(errors)}")
        
        if errors:
            print("\n  错误详情:")
            for error in errors[:10]:  # 只显示前10个错误
                print(f"    - {error}")
            if len(errors) > 10:
                print(f"    ... 还有 {len(errors) - 10} 个错误")
        
        # 验证没有错误
        self.assertEqual(len(errors), 0, f"应无计算错误，但发现 {len(errors)} 个错误")
    
    def test_score_distribution(self):
        """测试评分分布是否合理"""
        score_distribution = {
            '0-20': 0,   # 凶
            '21-40': 0,  # 平
            '41-60': 0,  # 中吉
            '61-80': 0,  # 吉
            '81-100': 0, # 大吉
            '100+': 0,   # 上吉
        }
        
        current_date = self.start_date
        while current_date <= self.end_date:
            try:
                sizhu = self._get_sizhu(current_date)
                
                # 以嫁娶为例统计评分分布
                result = calculate_score(sizhu, '嫁娶')
                score = result['score']
                
                if score <= 20:
                    score_distribution['0-20'] += 1
                elif score <= 40:
                    score_distribution['21-40'] += 1
                elif score <= 60:
                    score_distribution['41-60'] += 1
                elif score <= 80:
                    score_distribution['61-80'] += 1
                elif score <= 100:
                    score_distribution['81-100'] += 1
                else:
                    score_distribution['100+'] += 1
                
            except Exception as e:
                pass  # 忽略错误，只统计成功的
            
            current_date += timedelta(days=1)
        
        print(f"\n2026年3月嫁娶评分分布:")
        total = sum(score_distribution.values())
        for range_name, count in score_distribution.items():
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {range_name}: {count}天 ({percentage:.1f}%)")
        
        # 验证评分分布合理
        # 应该有不同等级的日期，而不是全部集中在某一等级
        non_zero_ranges = sum(1 for count in score_distribution.values() if count > 0)
        self.assertGreaterEqual(non_zero_ranges, 2, "评分分布应覆盖多个等级")
        
        # 验证没有极端情况（全部0分或全部100+分）
        self.assertLess(score_distribution['0-20'], total * 0.8, "不应超过80%为凶日")
        self.assertLess(score_distribution['100+'], total * 0.5, "不应超过50%为上吉日")
    
    def test_event_type_variation(self):
        """测试不同事项类型的评分计算"""
        # 选择几个特定日期
        test_dates = [
            date(2026, 3, 5),
            date(2026, 3, 15),
            date(2026, 3, 25),
        ]
        
        all_success = True
        
        for test_date in test_dates:
            scores = {}
            
            try:
                sizhu = self._get_sizhu(test_date)
                
                for event_type in EVENT_TYPES:
                    result = calculate_score(sizhu, event_type)
                    scores[event_type] = result['score']
                    
                    # 验证每个事项都有有效的评分结果
                    self.assertIn('score', result, f"{test_date} {event_type} 应有score")
                    self.assertIn('level', result, f"{test_date} {event_type} 应有level")
                    self.assertIn('reason', result, f"{test_date} {event_type} 应有reason")
                
                print(f"\n{test_date} 各事项评分:")
                for event_type, score in scores.items():
                    print(f"  {event_type}: {score}")
                
            except Exception as e:
                print(f"\n{test_date} 计算出错: {e}")
                all_success = False
        
        # 验证所有事项类型都能成功计算
        self.assertTrue(all_success, "所有事项类型应能成功计算评分")
    
    def test_specific_date_details(self):
        """测试特定日期的详细信息"""
        # 选择2026年3月15日进行详细检查
        test_date = date(2026, 3, 15)
        
        try:
            sizhu = self._get_sizhu(test_date)
            
            print(f"\n{test_date} 详细信息:")
            print(f"  四柱: {sizhu.get('year_gan', '')}{sizhu.get('year_zhi', '')}年 "
                  f"{sizhu.get('month_gan', '')}{sizhu.get('month_zhi', '')}月 "
                  f"{sizhu.get('day_gan', '')}{sizhu.get('day_zhi', '')}日")
            
            for event_type in ['嫁娶', '安葬']:
                result = calculate_score(sizhu, event_type)
                print(f"\n  {event_type}:")
                print(f"    评分: {result.get('score', 'N/A')}")
                print(f"    等级: {result.get('level', 'N/A')}")
                print(f"    理由: {result.get('reason', 'N/A')[:50]}...")
            
            # 验证有结果返回
            self.assertIsNotNone(sizhu)
            
        except Exception as e:
            self.fail(f"{test_date} 详细检查失败: {e}")


class TestSystemStability(unittest.TestCase):
    """系统稳定性测试"""
    
    def setUp(self):
        """测试前准备"""
        self.lunar = HighPrecisionLunar()
    
    def test_boundary_dates(self):
        """测试边界日期"""
        boundary_dates = [
            date(1900, 1, 1),   # 最早日期
            date(2100, 12, 31), # 最晚日期
            date(2000, 2, 29),  # 闰年2月29日
            date(2026, 2, 28),  # 非闰年2月28日
        ]
        
        for test_date in boundary_dates:
            with self.subTest(date=test_date):
                try:
                    sizhu = self.lunar.get_sizhu(
                        test_date.year, test_date.month, test_date.day, 12, 0
                    )
                    result = calculate_score(sizhu, '嫁娶')
                    
                    print(f"\n{test_date} 边界日期测试:")
                    print(f"  四柱计算: 成功")
                    print(f"  评分计算: 成功 (score={result.get('score', 'N/A')})")
                    
                    self.assertIsNotNone(sizhu)
                    self.assertIn('score', result)
                    
                except Exception as e:
                    self.fail(f"{test_date} 边界日期测试失败: {e}")
    
    def test_consecutive_dates(self):
        """测试连续日期计算"""
        start_date = date(2026, 3, 1)
        days_to_test = 7
        
        print(f"\n连续{days_to_test}天测试:")
        
        for i in range(days_to_test):
            test_date = start_date + timedelta(days=i)
            
            try:
                sizhu = self.lunar.get_sizhu(
                    test_date.year, test_date.month, test_date.day, 12, 0
                )
                result = calculate_score(sizhu, '嫁娶')
                
                print(f"  {test_date}: score={result.get('score', 'N/A')}, "
                      f"level={result.get('level', 'N/A')}")
                
                self.assertIn('score', result)
                self.assertIn('level', result)
                
            except Exception as e:
                self.fail(f"{test_date} 连续日期测试失败: {e}")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd2026March))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemStability))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    
    # 输出测试总结
    print("\n" + "="*60)
    print("端到端测试总结")
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
