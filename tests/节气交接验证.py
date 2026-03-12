# -*- coding: utf-8 -*-
"""
================================================================================
节气交接时刻交叉验证
================================================================================
验证每个节气交接时刻前后1分钟的月柱变化
================================================================================
"""

import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sxtwl
from modules.四柱计算器 import calculate_sizhu

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 月支与节的对应关系
JIE_TO_MONTH = {
    0: '寅',   # 立春
    2: '卯',   # 惊蛰
    4: '辰',   # 清明
    6: '巳',   # 立夏
    8: '午',   # 芒种
    10: '未',  # 小暑
    12: '申',  # 立秋
    14: '酉',  # 白露
    16: '戌',  # 寒露
    18: '亥',  # 立冬
    20: '子',  # 大雪
    22: '丑',  # 小寒
}

JQ_NAMES = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨',
            '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
            '立秋', '处暑', '白露', '秋分', '寒露', '霜降',
            '立冬', '小雪', '大雪', '冬至', '小寒', '大寒']


def jd_to_datetime(jd):
    """将儒略日转换为datetime"""
    dd = sxtwl.JD2DD(jd)
    return datetime(int(dd.Y), int(dd.M), int(dd.D), int(dd.h), int(dd.m), int(dd.s))


def get_sxtwl_month_pillar(year, month, day, hour):
    """使用sxtwl库获取月柱"""
    day_obj = sxtwl.fromSolar(year, month, day)
    month_gz = day_obj.getMonthGZ()
    return TIAN_GAN[month_gz.tg] + DI_ZHI[month_gz.dz]


def get_our_month_pillar(year, month, day, hour, minute=0):
    """使用我们的计算器获取月柱"""
    result = calculate_sizhu(date(year, month, day), hour, minute)
    return result['月柱']


def verify_jieqi_transition(year, jie_idx, jie_name):
    """
    验证特定节气的交接时刻
    
    Args:
        year: 年份
        jie_idx: 节气索引 (0=立春, 2=惊蛰, 4=清明...)
        jie_name: 节气名称
    """
    # 获取节气时间
    jq_list = sxtwl.getJieQiByYear(year)
    jie_dt = jd_to_datetime(jq_list[jie_idx].jd)
    
    # 获取交接前后的时间
    before_dt = jie_dt - timedelta(minutes=1)
    after_dt = jie_dt + timedelta(minutes=1)
    
    results = {
        'year': year,
        'jie_name': jie_name,
        'jie_time': jie_dt,
        'before': {},
        'at': {},
        'after': {},
        'correct_transition': False
    }
    
    # 测试交接前1分钟
    results['before']['sxtwl'] = get_sxtwl_month_pillar(
        before_dt.year, before_dt.month, before_dt.day, before_dt.hour)
    results['before']['our'] = get_our_month_pillar(
        before_dt.year, before_dt.month, before_dt.day, before_dt.hour, before_dt.minute)
    
    # 测试交接时刻
    results['at']['sxtwl'] = get_sxtwl_month_pillar(
        jie_dt.year, jie_dt.month, jie_dt.day, jie_dt.hour)
    results['at']['our'] = get_our_month_pillar(
        jie_dt.year, jie_dt.month, jie_dt.day, jie_dt.hour, jie_dt.minute)
    
    # 测试交接后1分钟
    results['after']['sxtwl'] = get_sxtwl_month_pillar(
        after_dt.year, after_dt.month, after_dt.day, after_dt.hour)
    results['after']['our'] = get_our_month_pillar(
        after_dt.year, after_dt.month, after_dt.day, after_dt.hour, after_dt.minute)
    
    # 判断是否正确切换
    # 交接前应该是上一个月，交接后应该是当前月
    expected_month_before = JIE_TO_MONTH.get(jie_idx - 2 if jie_idx >= 2 else 22, '子')
    expected_month_after = JIE_TO_MONTH.get(jie_idx, '寅')
    
    # 检查我们的计算是否正确
    our_before_zhi = results['before']['our'][1]
    our_after_zhi = results['after']['our'][1]
    
    results['correct_transition'] = (
        our_before_zhi == expected_month_before and
        our_after_zhi == expected_month_after
    )
    
    return results


def print_verification_result(result):
    """打印验证结果"""
    print('-' * 70)
    print('%d年 %s (交接时间: %s)' % (result['year'], result['jie_name'], result['jie_time']))
    print('-' * 70)
    
    print('交接前1分钟:')
    print('  sxtwl: %s  我们: %s' % (result['before']['sxtwl'], result['before']['our']))
    
    print('交接时刻:')
    print('  sxtwl: %s  我们: %s' % (result['at']['sxtwl'], result['at']['our']))
    
    print('交接后1分钟:')
    print('  sxtwl: %s  我们: %s' % (result['after']['sxtwl'], result['after']['our']))
    
    # 判断差异
    sxtwl_changed = result['before']['sxtwl'] != result['after']['sxtwl']
    our_changed = result['before']['our'] != result['after']['our']
    
    if sxtwl_changed and our_changed:
        print('结果: ✓ 两者都正确切换')
    elif not sxtwl_changed and our_changed:
        print('结果: ⚠ sxtwl未切换，我们正确切换')
    elif sxtwl_changed and not our_changed:
        print('结果: ✗ sxtwl切换，我们未切换')
    else:
        print('结果: ? 两者都未切换')
    
    print()


def main():
    """主函数"""
    # 选择测试年份
    test_years = [1972, 1984, 1999, 2023, 2026]
    
    # 12个节（决定月柱的节气）
    jie_indices = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
    
    total_tests = 0
    correct_transitions = 0
    sxtwl_correct = 0
    our_correct = 0
    
    for year in test_years:
        print('=' * 70)
        print('%d年 节气交接验证' % year)
        print('=' * 70)
        print()
        
        for jie_idx in jie_indices:
            jie_name = JQ_NAMES[jie_idx]
            result = verify_jieqi_transition(year, jie_idx, jie_name)
            print_verification_result(result)
            
            total_tests += 1
            
            # 检查是否正确切换
            sxtwl_changed = result['before']['sxtwl'] != result['after']['sxtwl']
            our_changed = result['before']['our'] != result['after']['our']
            
            if sxtwl_changed:
                sxtwl_correct += 1
            if our_changed:
                our_correct += 1
            if result['correct_transition']:
                correct_transitions += 1
    
    # 汇总
    print('=' * 70)
    print('验证汇总')
    print('=' * 70)
    print('总测试数: %d' % total_tests)
    print('sxtwl正确切换: %d (%.1f%%)' % (sxtwl_correct, sxtwl_correct / total_tests * 100))
    print('我们正确切换: %d (%.1f%%)' % (our_correct, our_correct / total_tests * 100))
    print('我们完全正确: %d (%.1f%%)' % (correct_transitions, correct_transitions / total_tests * 100))
    print()
    
    if our_correct == total_tests:
        print('✓ 所有节气交接时刻都正确切换！')
    else:
        print('⚠ 部分节气交接时刻有问题，需要检查')


if __name__ == '__main__':
    main()
