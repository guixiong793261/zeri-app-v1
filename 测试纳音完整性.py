# -*- coding: utf-8 -*-
"""
测试纳音完整性
验证纳音表是否包含所有60甲子组合
"""

from modules.八字排盘 import create_bazi_panpan
from modules.八字工具整合 import get_nayin


print("=== 测试纳音完整性 ===")

# 生成所有60甲子组合
tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
di_zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

all_combinations = []
for gan in tian_gan:
    for zhi in di_zhi:
        all_combinations.append(gan + zhi)

print(f"\n1. 检查纳音表完整性：")
print(f"   应该包含 {len(all_combinations)} 个组合")

# 检查八字工具整合模块的纳音表
missing_count = 0
missing_combinations = []
for combo in all_combinations:
    nayin = get_nayin(combo)
    if nayin == '未知':
        missing_count += 1
        missing_combinations.append(combo)

if missing_count == 0:
    print("   ✅ 所有60甲子组合都有对应的纳音")
else:
    print(f"   ❌ 缺少 {missing_count} 个组合的纳音")
    print(f"   缺少的组合: {missing_combinations}")

print(f"\n2. 测试实际排盘的纳音计算：")
test_cases = [
    (2024, 2, 4, 12, 0, '男'),  # 甲辰 丙寅 戊戌 戊午
    (2023, 2, 4, 12, 0, '女'),  # 癸卯 乙丑 戊戌 戊午
]

for i, test_case in enumerate(test_cases, 1):
    try:
        bazi = create_bazi_panpan(*test_case)
        result = bazi.get_panpan_result()
        
        print(f"\n   测试{i}: {test_case[0]}年{test_case[1]}月{test_case[2]}日 {test_case[5]}命")
        print(f"   四柱: {result['基本信息']['四柱']}")
        print(f"   纳音: {result['纳音']}")
        
        # 检查是否有'未知'
        has_unknown = any(v == '未知' for v in result['纳音'].values())
        if has_unknown:
            print(f"   ⚠️  存在未知的纳音")
        else:
            print(f"   ✅ 所有纳音都正确计算")
        
    except Exception as e:
        print(f"   ❌ 测试{i}失败: {e}")

print(f"\n3. 测试特定组合的纳音：")
test_combinations = [
    ('甲子', '海中金'),
    ('乙丑', '海中金'),
    ('甲辰', '覆灯火'),
    ('乙巳', '覆灯火'),
    ('丙午', '天河水'),
    ('丁未', '天河水'),
    ('戊申', '大驿土'),
    ('己酉', '大驿土'),
    ('庚戌', '钗钏金'),
    ('辛亥', '钗钏金'),
]

all_correct = True
for combo, expected in test_combinations:
    actual = get_nayin(combo)
    status = "✅" if actual == expected else "❌"
    print(f"   {status} {combo}: {actual} (期望: {expected})")
    if actual != expected:
        all_correct = False

if all_correct:
    print("   ✅ 所有测试组合的纳音都正确")
else:
    print("   ❌ 部分测试组合的纳音不正确")

print(f"\n=== 测试完成 ===")
