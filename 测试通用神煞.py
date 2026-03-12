# -*- coding: utf-8 -*-
"""
================================================================================
测试通用神煞模块
================================================================================
验证天德、月德的索引对应关系及其他通用神煞的准确性
================================================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.四柱计算器 import calculate_sizhu
from modules.shensha.通用神煞 import CommonShenShaChecker
from modules.工具函数 import DI_ZHI, TIANDE, YUEDE
from datetime import date


def test_tiande():
    """测试天德"""
    print("\n=== 测试天德 ===")
    
    # 验证索引对应关系
    print("天德索引对应关系:")
    for i, zhi in enumerate(DI_ZHI):
        tiande = TIANDE.get(i)
        print(f"  {zhi}月（索引{i}）: {tiande}")
    
    # 测试每个月的天德日
    test_cases = [
        ('寅', '丁'),  # 寅月天德在丁
        ('卯', '申'),  # 卯月天德在申
        ('辰', '壬'),  # 辰月天德在壬
        ('巳', '辛'),  # 巳月天德在辛
        ('午', '亥'),  # 午月天德在亥
        ('未', '甲'),  # 未月天德在甲
        ('申', '癸'),  # 申月天德在癸
        ('酉', '寅'),  # 酉月天德在寅
        ('戌', '丙'),  # 戌月天德在丙
        ('亥', '乙'),  # 亥月天德在乙
        ('子', '巳'),  # 子月天德在巳
        ('丑', '庚'),  # 丑月天德在庚
    ]
    
    for month_zhi, expected_gan in test_cases:
        # 创建一个测试四柱
        test_sizhu = {
            'month_zhi': month_zhi,
            'day_gan': expected_gan,
            'day_zhi': '子',  # 任意日支
            'year_zhi': '子',  # 任意年支
            'hour_gan': '甲',   # 任意时干
            'hour_zhi': '子',   # 任意时支
            '年柱': '甲子',     # 任意年柱
            '月柱': '丙寅',     # 任意月柱
            '日柱': f'{expected_gan}子',  # 天德日
            '时柱': '甲子',     # 任意时柱
            'year_gan': '甲',   # 任意年干
            'month_gan': '丙',  # 任意月干
        }
        
        checker = CommonShenShaChecker()
        shensha_list = checker.check(test_sizhu, {})
        
        # 检查是否包含天德
        has_tiande = any(item['name'] == '天德' for item in shensha_list)
        print(f"{month_zhi}月{expected_gan}日: {'✓ 正确' if has_tiande else '✗ 错误'}")


def test_yuede():
    """测试月德"""
    print("\n=== 测试月德 ===")
    
    # 验证索引对应关系
    print("月德索引对应关系:")
    for i, zhi in enumerate(DI_ZHI):
        yuede = YUEDE.get(i)
        print(f"  {zhi}月（索引{i}）: {yuede}")
    
    # 测试每个月的月德日
    test_cases = [
        ('寅', '丙'),  # 寅月（寅午戌月）月德在丙
        ('午', '丙'),  # 午月（寅午戌月）月德在丙
        ('戌', '丙'),  # 戌月（寅午戌月）月德在丙
        ('申', '壬'),  # 申月（申子辰月）月德在壬
        ('子', '壬'),  # 子月（申子辰月）月德在壬
        ('辰', '壬'),  # 辰月（申子辰月）月德在壬
        ('亥', '甲'),  # 亥月（亥卯未月）月德在甲
        ('卯', '甲'),  # 卯月（亥卯未月）月德在甲
        ('未', '甲'),  # 未月（亥卯未月）月德在甲
        ('巳', '庚'),  # 巳月（巳酉丑月）月德在庚
        ('酉', '庚'),  # 酉月（巳酉丑月）月德在庚
        ('丑', '庚'),  # 丑月（巳酉丑月）月德在庚
    ]
    
    for month_zhi, expected_gan in test_cases:
        # 创建一个测试四柱
        test_sizhu = {
            'month_zhi': month_zhi,
            'day_gan': expected_gan,
            'day_zhi': '子',  # 任意日支
            'year_zhi': '子',  # 任意年支
            'hour_gan': '甲',   # 任意时干
            'hour_zhi': '子',   # 任意时支
            '年柱': '甲子',     # 任意年柱
            '月柱': '丙寅',     # 任意月柱
            '日柱': f'{expected_gan}子',  # 月德日
            '时柱': '甲子',     # 任意时柱
            'year_gan': '甲',   # 任意年干
            'month_gan': '丙',  # 任意月干
        }
        
        checker = CommonShenShaChecker()
        shensha_list = checker.check(test_sizhu, {})
        
        # 检查是否包含月德
        has_yuede = any(item['name'] == '月德' for item in shensha_list)
        print(f"{month_zhi}月{expected_gan}日: {'✓ 正确' if has_yuede else '✗ 错误'}")


def test_common_shensha():
    """测试其他通用神煞"""
    print("\n=== 测试其他通用神煞 ===")
    
    # 测试岁破
    print("\n1. 测试岁破:")
    test_sizhu = {
        'year_zhi': '子',  # 子年
        'day_zhi': '午',   # 午日（子冲午）
        'month_zhi': '寅',  # 任意月支
        'day_gan': '甲',    # 任意日干
        'hour_gan': '甲',   # 任意时干
        'hour_zhi': '子',   # 任意时支
        '年柱': '甲子',     # 任意年柱
        '月柱': '丙寅',     # 任意月柱
        '日柱': '甲午',     # 岁破日
        '时柱': '甲子',     # 任意时柱
        'year_gan': '甲',   # 任意年干
        'month_gan': '丙',  # 任意月干
    }
    
    checker = CommonShenShaChecker()
    shensha_list = checker.check(test_sizhu, {})
    
    has_suipo = any(item['name'] == '岁破' for item in shensha_list)
    print(f"子年午日: {'✓ 岁破' if has_suipo else '✗ 错误'}")
    
    # 测试月破
    print("\n2. 测试月破:")
    test_sizhu = {
        'month_zhi': '寅',  # 寅月
        'day_zhi': '申',   # 申日（寅冲申）
        'year_zhi': '子',  # 任意年支
        'day_gan': '甲',    # 任意日干
        'hour_gan': '甲',   # 任意时干
        'hour_zhi': '子',   # 任意时支
        '年柱': '甲子',     # 任意年柱
        '月柱': '丙寅',     # 任意月柱
        '日柱': '甲申',     # 月破日
        '时柱': '甲子',     # 任意时柱
        'year_gan': '甲',   # 任意年干
        'month_gan': '丙',  # 任意月干
    }
    
    checker = CommonShenShaChecker()
    shensha_list = checker.check(test_sizhu, {})
    
    has_yuepo = any(item['name'] == '月破' for item in shensha_list)
    print(f"寅月申日: {'✓ 月破' if has_yuepo else '✗ 错误'}")
    
    # 测试四离日
    print("\n3. 测试四离日:")
    test_sizhu = {
        'month_zhi': '卯',  # 卯月
        'day_zhi': '辰',   # 辰日（春分前一日）
        'year_zhi': '子',  # 任意年支
        'day_gan': '甲',    # 任意日干
        'hour_gan': '甲',   # 任意时干
        'hour_zhi': '子',   # 任意时支
        '年柱': '甲子',     # 任意年柱
        '月柱': '丙寅',     # 任意月柱
        '日柱': '甲辰',     # 四离日
        '时柱': '甲子',     # 任意时柱
        'year_gan': '甲',   # 任意年干
        'month_gan': '丙',  # 任意月干
    }
    
    checker = CommonShenShaChecker()
    shensha_list = checker.check(test_sizhu, {})
    
    has_sili = any(item['name'] == '四离日' for item in shensha_list)
    print(f"卯月辰日: {'✓ 四离日' if has_sili else '✗ 错误'}")
    
    # 测试四绝日
    print("\n4. 测试四绝日:")
    test_sizhu = {
        'month_zhi': '丑',  # 丑月
        'day_zhi': '寅',   # 寅日（立春前一日）
        'year_zhi': '子',  # 任意年支
        'day_gan': '甲',    # 任意日干
        'hour_gan': '甲',   # 任意时干
        'hour_zhi': '子',   # 任意时支
        '年柱': '甲子',     # 任意年柱
        '月柱': '丙寅',     # 任意月柱
        '日柱': '甲寅',     # 四绝日
        '时柱': '甲子',     # 任意时柱
        'year_gan': '甲',   # 任意年干
        'month_gan': '丙',  # 任意月干
    }
    
    checker = CommonShenShaChecker()
    shensha_list = checker.check(test_sizhu, {})
    
    has_sijue = any(item['name'] == '四绝日' for item in shensha_list)
    print(f"丑月寅日: {'✓ 四绝日' if has_sijue else '✗ 错误'}")


if __name__ == '__main__':
    print("=======================================================================")
    print("测试通用神煞模块")
    print("=======================================================================")
    
    test_tiande()
    test_yuede()
    test_common_shensha()
    
    print("\n=======================================================================")
    print("测试完成")
    print("=======================================================================")
