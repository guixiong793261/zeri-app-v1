# -*- coding: utf-8 -*-
"""
================================================================================
四柱计算批量验证
================================================================================
使用精确节气时间作为权威参考，批量验证四柱计算的正确性
================================================================================
"""

import sys
import os
import random
from datetime import date, timedelta, datetime

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
    jq_list_current = sxtwl.getJieQiByYear(year)
    jq_list_prev = sxtwl.getJieQiByYear(year - 1)
    
    jie_indices = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
    month_zhi_list = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
    
    jie_times = []
    
    for idx in [22, 23]:
        jd = jq_list_prev[idx].jd
        dt = jd_to_datetime(jd)
        jie_times.append((dt, idx))
    
    for idx in range(24):
        jd = jq_list_current[idx].jd
        dt = jd_to_datetime(jd)
        jie_times.append((dt, idx))
    
    jq_list_next = sxtwl.getJieQiByYear(year + 1)
    jd = jq_list_next[22].jd
    dt = jd_to_datetime(jd)
    jie_times.append((dt, 22))
    
    jie_times.sort(key=lambda x: x[0])
    
    current_dt = datetime(year, month, day, hour, minute, 0)
    month_zhi = '寅'
    
    for i, (dt, idx) in enumerate(jie_times):
        if current_dt < dt:
            if i == 0:
                month_zhi = '丑'
            else:
                prev_idx = jie_times[i-1][1]
                for j, jie_idx in enumerate(jie_indices):
                    if prev_idx == jie_idx:
                        month_zhi = month_zhi_list[j]
                        break
                    elif prev_idx == jie_idx + 1:
                        month_zhi = month_zhi_list[j]
                        break
            break
    else:
        month_zhi = '丑'
    
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


def compare_sizhu(our_result, ref_result):
    """对比两个四柱结果"""
    differences = []
    
    for pillar in ['年柱', '月柱', '日柱', '时柱']:
        if our_result[pillar] != ref_result[pillar]:
            differences.append({
                'pillar': pillar,
                'our': our_result[pillar],
                'ref': ref_result[pillar]
            })
    
    return differences


def batch_verify(start_year, end_year, sample_count=100):
    """批量验证四柱计算"""
    print("=" * 60)
    print(f"四柱计算批量验证 ({start_year}-{end_year}年)")
    print(f"随机抽样: {sample_count} 个日期")
    print("参考标准: sxtwl库 + 精确节气时间")
    print("=" * 60)
    print()
    
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    total_days = (end_date - start_date).days
    
    random.seed(42)
    sampled_days = random.sample(range(total_days), min(sample_count, total_days))
    
    total_tests = 0
    total_errors = 0
    error_details = []
    
    for day_offset in sampled_days:
        test_date = start_date + timedelta(days=day_offset)
        year, month, day = test_date.year, test_date.month, test_date.day
        
        for hour in [0, 6, 8, 12, 18, 23]:
            total_tests += 1
            
            our_result = calculate_sizhu(date(year, month, day), hour, 0)
            ref_result = get_reference_sizhu(year, month, day, hour, 0)
            
            differences = compare_sizhu(our_result, ref_result)
            
            if differences:
                total_errors += 1
                error_details.append({
                    'date': f"{year}-{month:02d}-{day:02d} {hour:02d}:00",
                    'differences': differences
                })
    
    print(f"总测试数: {total_tests}")
    print(f"错误数: {total_errors}")
    print(f"正确率: {(total_tests - total_errors) / total_tests * 100:.2f}%")
    print()
    
    if error_details:
        print("=" * 60)
        print("错误详情:")
        print("=" * 60)
        for detail in error_details[:20]:
            print(f"\n日期: {detail['date']}")
            for diff in detail['differences']:
                print(f"  {diff['pillar']}: 我们={diff['our']}, 参考={diff['ref']}")
        
        if len(error_details) > 20:
            print(f"\n... 还有 {len(error_details) - 20} 个错误未显示")
    
    return total_tests, total_errors


def verify_specific_dates():
    """验证特定日期"""
    print("=" * 60)
    print("特定日期验证")
    print("=" * 60)
    print()
    
    test_cases = [
        (1972, 1, 8, 8, "用户确认: 辛亥 辛丑 戊戌 丙辰"),
        (1999, 4, 5, 6, "用户确认: 己卯 丁卯 丁亥 癸卯"),
        (1972, 11, 7, 12, "立冬15:39前: 庚戌"),
        (1972, 11, 7, 18, "立冬15:39后: 辛亥"),
        (1999, 4, 5, 13, "清明13:44前: 丁卯"),
        (1999, 4, 5, 14, "清明13:44后: 戊辰"),
    ]
    
    for year, month, day, hour, note in test_cases:
        our_result = calculate_sizhu(date(year, month, day), hour, 0)
        ref_result = get_reference_sizhu(year, month, day, hour, 0)
        
        print(f"{year}-{month:02d}-{day:02d} {hour:02d}:00 ({note})")
        print(f"  我们的结果: {our_result['年柱']} {our_result['月柱']} {our_result['日柱']} {our_result['时柱']}")
        print(f"  参考结果:   {ref_result['年柱']} {ref_result['月柱']} {ref_result['日柱']} {ref_result['时柱']}")
        
        differences = compare_sizhu(our_result, ref_result)
        if differences:
            print("  [有差异]")
            for diff in differences:
                print(f"    {diff['pillar']}: 我们={diff['our']}, 参考={diff['ref']}")
        else:
            print("  [一致] ✓")
        print()


if __name__ == '__main__':
    verify_specific_dates()
    batch_verify(1970, 2020, sample_count=50)
