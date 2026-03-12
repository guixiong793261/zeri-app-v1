# -*- coding: utf-8 -*-
"""
测试评分器集成新功能
"""

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer
from datetime import date

# 测试日期
target_date = date(2024, 5, 20)
sizhu = calculate_sizhu(target_date, 12, 0)

print('=== 测试评分器集成新功能 ===')
print(f'测试日期: {target_date}')
print(f'四柱: 年={sizhu.get("year_gan", "")}{sizhu.get("year_zhi", "")}, '  
      f'月={sizhu.get("month_gan", "")}{sizhu.get("month_zhi", "")}, ' 
      f'日={sizhu.get("day_gan", "")}{sizhu.get("day_zhi", "")}, ' 
      f'时={sizhu.get("hour_gan", "")}{sizhu.get("hour_zhi", "")}')
print()

# 测试评分器
scorer = Scorer()

# 测试事项：嫁娶
event_type = '嫁娶'

# 事主信息（简化版）
owners = [{
    'year': 1990,
    'xishen': '木、火',
    'yongshen': '火'
}]

# 测试评分
result = scorer.score(sizhu, event_type, owners)

print('=== 评分结果 ===')
print(f'综合评分: {result.get("score", 0)}')
print(f'等级: {result.get("level", "")}')
print(f'评语: {result.get("reason", "")}')
print()

print('=== 五行审核结果 ===')
wu_xing_result = result.get('wu_xing_result', {})
print(f'五行评分: {wu_xing_result.get("score", 0)}')
print(f'是否合格: {wu_xing_result.get("he_ge", False)}')
print(f'五行评语: {wu_xing_result.get("ji_yu", "")}')
print()

print('=== 神煞信息 ===')
shensha_list = result.get('shensha_list', [])
print(f'神煞数量: {len(shensha_list)}')
for i, shensha in enumerate(shensha_list[:5]):  # 只显示前5个
    print(f'  {i+1}. {shensha.get("name", "")}: {shensha.get("description", "")} (评分: {shensha.get("score", 0)})')
if len(shensha_list) > 5:
    print(f'  ... 还有{len(shensha_list) - 5}个神煞')
print()

print('=== 宜忌信息 ===')
yi_list = result.get('yi_list', [])
ji_list = result.get('ji_list', [])
print(f'宜: {yi_list}')
print(f'忌: {ji_list}')
print()

print('=== 黄道信息 ===')
huangdao_info = result.get('huangdao_info', {})
print(f'黄道等级: {huangdao_info.get("huang_dao_level", "")}')
print(f'黄道评分: {huangdao_info.get("huang_dao_score", 0)}')
print(f'大黄道: {huangdao_info.get("da_huang_dao", "")}')
print(f'小黄道: {huangdao_info.get("xiao_huang_dao", "")}')
print()

print('=== 测试完成 ===')
