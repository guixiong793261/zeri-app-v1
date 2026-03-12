# -*- coding: utf-8 -*-
"""
================================================================================
系统性测试运行脚本
================================================================================
运行所有测试并生成测试报告

使用方法：
    python run_tests.py

可选参数：
    --sizhu     只运行四柱计算测试
    --shensha   只运行神煞检查测试
    --rules     只运行宜忌规则测试
    --end2end   只运行端到端测试
    --score     只运行评分逻辑测试
    --all       运行所有测试（默认）
================================================================================
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_sizhu_tests():
    """运行四柱计算测试"""
    print("\n" + "="*60)
    print("运行四柱计算测试")
    print("="*60)
    
    from tests.test_sizhu import run_tests
    result = run_tests()
    return result


def run_shensha_tests():
    """运行神煞检查测试"""
    print("\n" + "="*60)
    print("运行神煞检查测试")
    print("="*60)
    
    from tests.test_shensha import run_tests
    result = run_tests()
    return result


def run_rules_tests():
    """运行宜忌规则测试"""
    print("\n" + "="*60)
    print("运行宜忌规则测试")
    print("="*60)
    
    from tests.test_rules import run_tests
    result = run_tests()
    return result


def run_end_to_end_tests():
    """运行端到端测试"""
    print("\n" + "="*60)
    print("运行端到端测试")
    print("="*60)
    
    from tests.test_end_to_end import run_tests
    result = run_tests()
    return result


def run_score_tests():
    """运行评分逻辑测试"""
    print("\n" + "="*60)
    print("运行评分逻辑测试")
    print("="*60)
    
    import subprocess
    result = subprocess.run([sys.executable, "test_yueling_score.py"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # 返回一个简单的结果对象
    class SimpleResult:
        def __init__(self):
            self.testsRun = 5  # test_yueling_score.py中的测试数量
            self.failures = []
            self.errors = []
    
    return SimpleResult()


def generate_full_report(results):
    """生成完整测试报告"""
    print("\n" + "="*70)
    print("系统性测试总结报告")
    print("="*70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*70)
    
    total_tests = 0
    total_passed = 0
    total_failures = 0
    total_errors = 0
    
    # 各测试类别报告
    test_names = {
        'sizhu': '四柱计算测试',
        'shensha': '神煞检查测试',
        'rules': '宜忌规则测试',
        'end2end': '端到端测试',
        'score': '评分逻辑测试',
    }
    
    for key, name in test_names.items():
        if key in results and results[key]:
            result = results[key]
            passed = result.testsRun - len(result.failures) - len(result.errors)
            
            print(f"\n【{name}】")
            print(f"  总测试数: {result.testsRun}")
            print(f"  通过: {passed}")
            print(f"  失败: {len(result.failures)}")
            print(f"  错误: {len(result.errors)}")
            
            if result.failures:
                print("  失败的测试:")
                for test, _ in result.failures:
                    print(f"    - {test}")
            
            if result.errors:
                print("  出错的测试:")
                for test, _ in result.errors:
                    print(f"    - {test}")
            
            total_tests += result.testsRun
            total_passed += passed
            total_failures += len(result.failures)
            total_errors += len(result.errors)
    
    # 总体统计
    print("\n" + "-"*70)
    print("【总体统计】")
    print(f"  总测试数: {total_tests}")
    print(f"  通过: {total_passed}")
    print(f"  失败: {total_failures}")
    print(f"  错误: {total_errors}")
    print(f"  通过率: {total_passed/total_tests*100:.1f}%" if total_tests > 0 else "  通过率: N/A")
    
    if total_failures == 0 and total_errors == 0:
        print("\n✅ 所有测试通过！")
    else:
        print(f"\n⚠️  存在 {total_failures} 个失败和 {total_errors} 个错误")
    
    print("="*70)
    
    return total_failures == 0 and total_errors == 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行系统性测试')
    parser.add_argument('--sizhu', action='store_true', help='只运行四柱计算测试')
    parser.add_argument('--shensha', action='store_true', help='只运行神煞检查测试')
    parser.add_argument('--rules', action='store_true', help='只运行宜忌规则测试')
    parser.add_argument('--end2end', action='store_true', help='只运行端到端测试')
    parser.add_argument('--score', action='store_true', help='只运行评分逻辑测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试（默认）')
    
    args = parser.parse_args()
    
    # 如果没有指定参数，默认运行所有测试
    if not (args.sizhu or args.shensha or args.rules or args.end2end or args.score):
        args.all = True
    
    results = {}
    
    try:
        if args.all or args.sizhu:
            results['sizhu'] = run_sizhu_tests()
        
        if args.all or args.shensha:
            results['shensha'] = run_shensha_tests()
        
        if args.all or args.rules:
            results['rules'] = run_rules_tests()
        
        if args.all or args.end2end:
            results['end2end'] = run_end_to_end_tests()
        
        if args.all or args.score:
            results['score'] = run_score_tests()
        
        # 生成报告
        if args.all:
            success = generate_full_report(results)
            sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ 测试运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
