# -*- coding: utf-8 -*-
"""
================================================================================
双立春年份月柱验证
================================================================================
验证农历年内有两个立春的年份的月柱计算正确性
================================================================================
"""

import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sxtwl
from modules.四柱计算器 import calculate_sizhu

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

WU_HU_DUN = {
    '甲': 2, '己': 2,
    '乙': 4, '庚': 4,
    '丙': 6, '辛': 6,
    '丁': 8, '壬': 8,
    '戊': 0, '癸': 0
}


def jd_to_datetime(jd):
    """将儒略日转换为datetime"""
    dd = sxtwl.JD2DD(jd)
    return datetime(int(dd.Y), int(dd.M), int(dd.D), int(dd.h), int(dd.m), int(dd.s))


def get_precise_month_pillar(year, month, day, hour, minute, year_gan):
    """使用精确节气时间计算月柱（作为权威参考）"""
    jq_list = sxtwl.getJieQiByYear(year)
    
    jie_to_month = {
        0: '寅', 2: '卯', 4: '辰', 6: '巳', 8: '午', 10: '未',
        12: '申', 14: '酉', 16: '戌', 18: '亥', 20: '子', 22: '丑',
    }
    
    jie_times = []
    
    for jie_idx in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
        jd = jq_list[jie_idx].jd
        dt = jd_to_datetime(jd)
        jie_times.append((dt, jie_idx))
    
    current_dt = datetime(year, month, day, hour, minute, 0)
    lichun_dt = jd_to_datetime(jq_list[0].jd)
    
    if current_dt < lichun_dt:
        jq_list_prev = sxtwl.getJieQiByYear(year - 1)
        jd = jq_list_prev[22].jd
        dt = jd_to_datetime(jd)
        jie_times.append((dt, 22))
    
    jie_times.sort(key=lambda x: x[0])
    
    month_zhi = '寅'
    
    for i, (dt, jie_idx) in enumerate(jie_times):
        if current_dt < dt:
            if i == 0:
                month_zhi = '子'
            else:
                prev_jie_idx = jie_times[i-1][1]
                month_zhi = jie_to_month.get(prev_jie_idx, '寅')
            break
    else:
        last_jie_idx = jie_times[-1][1]
        month_zhi = jie_to_month.get(last_jie_idx, '丑')
    
    base_gan_index = WU_HU_DUN.get(year_gan, 0)
    month_zhi_index = DI_ZHI.index(month_zhi)
    offset = (month_zhi_index - 2 + 12) % 12
    month_gan_index = (base_gan_index + offset) % 10
    month_gan = TIAN_GAN[month_gan_index]
    
    return month_gan, month_zhi


def get_reference_sizhu(year, month, day, hour=12, minute=0):
    """使用sxtwl库+精确节气时间计算四柱（作为权威参考）"""
    day_obj = sxtwl.fromSolar(year, month, day)
    
    year_gz = day_obj.getYearGZ()
    day_gz = day_obj.getDayGZ()
    hour_gz = day_obj.getHourGZ(hour)
    
    year_gan = TIAN_GAN[year_gz.tg]
    year_zhi = DI_ZHI[year_gz.dz]
    day_gan = TIAN_GAN[day_gz.tg]
    day_zhi = DI_ZHI[day_gz.dz]
    hour_gan = TIAN_GAN[hour_gz.tg]
    hour_zhi = DI_ZHI[hour_gz.dz]
    
    month_gan, month_zhi = get_precise_month_pillar(year, month, day, hour, minute, year_gan)
    
    return {
        '年柱': year_gan + year_zhi,
        '月柱': month_gan + month_zhi,
        '日柱': day_gan + day_zhi,
        '时柱': hour_gan + hour_zhi,
    }


def verify_double_lichun_year(year, leap_month):
    """验证双立春年份的月柱计算"""
    print('=' * 70)
    print('%d年（闰%d月，双立春）月柱验证' % (year, leap_month))
    print('=' * 70)
    print()
    
    # 获取该年的立春时间
    jq_list = sxtwl.getJieQiByYear(year)
    lichun_dt = jd_to_datetime(jq_list[0].jd)
    
    # 获取下一年的立春时间
    jq_list_next = sxtwl.getJieQiByYear(year + 1)
    lichun_next_dt = jd_to_datetime(jq_list_next[0].jd)
    
    print('立春时间:')
    print('  第一个立春: %s' % lichun_dt)
    print('  第二个立春: %s' % lichun_next_dt)
    print()
    
    # 验证立春前后的月柱变化
    print('=== 立春前后月柱变化验证 ===')
    print()
    
    # 第一个立春前后
    print('第一个立春前后:')
    test_times = [
        (lichun_dt.year, lichun_dt.month, lichun_dt.day, lichun_dt.hour - 1 if lichun_dt.hour > 0 else 23),
        (lichun_dt.year, lichun_dt.month, lichun_dt.day, lichun_dt.hour),
        (lichun_dt.year, lichun_dt.month, lichun_dt.day, lichun_dt.hour + 1 if lichun_dt.hour < 23 else 0),
    ]
    
    for y, m, d, h in test_times:
        our_result = calculate_sizhu(date(y, m, d), h, 0)
        ref_result = get_reference_sizhu(y, m, d, h, 0)
        status = '✓' if our_result['月柱'] == ref_result['月柱'] else '✗'
        print('  %04d-%02d-%02d %02d:00 我们=%s 参考=%s %s' % (y, m, d, h, our_result['月柱'], ref_result['月柱'], status))
    
    print()
    
    # 第二个立春前后
    print('第二个立春前后:')
    test_times = [
        (lichun_next_dt.year, lichun_next_dt.month, lichun_next_dt.day, lichun_next_dt.hour - 1 if lichun_next_dt.hour > 0 else 23),
        (lichun_next_dt.year, lichun_next_dt.month, lichun_next_dt.day, lichun_next_dt.hour),
        (lichun_next_dt.year, lichun_next_dt.month, lichun_next_dt.day, lichun_next_dt.hour + 1 if lichun_next_dt.hour < 23 else 0),
    ]
    
    for y, m, d, h in test_times:
        our_result = calculate_sizhu(date(y, m, d), h, 0)
        ref_result = get_reference_sizhu(y, m, d, h, 0)
        status = '✓' if our_result['月柱'] == ref_result['月柱'] else '✗'
        print('  %04d-%02d-%02d %02d:00 我们=%s 参考=%s %s' % (y, m, d, h, our_result['月柱'], ref_result['月柱'], status))
    
    print()
    
    # 验证整年的月柱
    print('=== 整年月柱验证 ===')
    print()
    
    total_tests = 0
    total_errors = 0
    error_details = []
    
    # 验证该年每个月
    for month in range(1, 13):
        for day in [1, 15, 28]:
            total_tests += 1
            
            our_result = calculate_sizhu(date(year, month, day), 12, 0)
            ref_result = get_reference_sizhu(year, month, day, 12, 0)
            
            if our_result['月柱'] != ref_result['月柱']:
                total_errors += 1
                error_details.append({
                    'date': '%d-%02d-%02d' % (year, month, day),
                    'our': our_result['月柱'],
                    'ref': ref_result['月柱']
                })
    
    # 验证次年1月（第二个立春前）
    for day in [1, 15, 28]:
        total_tests += 1
        
        our_result = calculate_sizhu(date(year + 1, 1, day), 12, 0)
        ref_result = get_reference_sizhu(year + 1, 1, day, 12, 0)
        
        if our_result['月柱'] != ref_result['月柱']:
            total_errors += 1
            error_details.append({
                'date': '%d-01-%02d' % (year + 1, day),
                'our': our_result['月柱'],
                'ref': ref_result['月柱']
            })
    
    # 验证次年2月（第二个立春后）
    for day in [5, 15, 28]:
        total_tests += 1
        
        our_result = calculate_sizhu(date(year + 1, 2, day), 12, 0)
        ref_result = get_reference_sizhu(year + 1, 2, day, 12, 0)
        
        if our_result['月柱'] != ref_result['月柱']:
            total_errors += 1
            error_details.append({
                'date': '%d-02-%02d' % (year + 1, day),
                'our': our_result['月柱'],
                'ref': ref_result['月柱']
            })
    
    print('验证结果:')
    print('  总测试数: %d' % total_tests)
    print('  错误数: %d' % total_errors)
    print('  正确率: %.2f%%' % ((total_tests - total_errors) / total_tests * 100))
    print()
    
    if error_details:
        print('错误详情:')
        for detail in error_details:
            print('  %s: 我们=%s, 参考=%s' % (detail['date'], detail['our'], detail['ref']))
        print()
    
    return total_tests, total_errors


def main():
    """主函数"""
    # 找出有闰月的年份（这些年份通常有双立春）
    double_lichun_years = []
    
    for year in range(1970, 2030):
        leap_month = sxtwl.getRunMonth(year)
        if leap_month > 0:
            jq_list_next = sxtwl.getJieQiByYear(year + 1)
            lichun_next_dt = jd_to_datetime(jq_list_next[0].jd)
            
            if lichun_next_dt.year == year + 1 and lichun_next_dt.month <= 2:
                double_lichun_years.append((year, leap_month))
    
    print('农历年内有两个立春的年份（1970-2030）:')
    for year, leap_month in double_lichun_years:
        print('  %d年(闰%d月)' % (year, leap_month))
    print()
    
    # 选择几个有代表性的双立春年份进行详细验证
    test_years = [
        (1971, 5),   # 闰五月
        (1984, 10),  # 闰十月
        (1998, 5),   # 闰五月
        (2023, 2),   # 闰二月
    ]
    
    total_tests = 0
    total_errors = 0
    
    for year, leap_month in test_years:
        tests, errors = verify_double_lichun_year(year, leap_month)
        total_tests += tests
        total_errors += errors
    
    print('=' * 70)
    print('总体验证结果')
    print('=' * 70)
    print('总测试数: %d' % total_tests)
    print('总错误数: %d' % total_errors)
    print('总体正确率: %.2f%%' % ((total_tests - total_errors) / total_tests * 100))


if __name__ == '__main__':
    main()
