# -*- coding: utf-8 -*-
"""
================================================================================
评分权重校准脚本
================================================================================
根据《钦定协纪辩方书》和传统择日经验，校准神煞评分权重
"""

import sys
import os
import re

# 配置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SHENSHA_DIR = os.path.join(BASE_DIR, 'shensha')
MOBILE_SHENSHA_DIR = os.path.join(PROJECT_ROOT, '手机一键部署', '模块完整版', 'modules', 'shensha')

# 评分权重配置
SCORE_CONFIG = {
    # 吉神加分（根据重要性）
    'ji_shensha': {
        '天德': 20,      # 天德：+20分
        '月德': 18,      # 月德：+18分
        '天德合': 15,    # 天德合：+15分
        '月德合': 12,    # 月德合：+12分
        '天赦日': 25,    # 天赦日：+25分
        '天愿': 12,      # 天愿：+12分
        '月恩': 10,      # 月恩：+10分
        '四相': 10,      # 四相：+10分
        '时德': 10,      # 时德：+10分
        '民日': 10,      # 民日：+10分
        '天马': 10,      # 天马：+10分
        '三奇': 20,      # 三奇：+20分
        '将星': 12,      # 将星：+12分
        '驿马': 12,      # 驿马：+12分
        '建星吉日': 10,  # 建星吉日：+10分
        '三合': 12,      # 三合：+12分
        '六合': 12,      # 六合：+12分
        '母仓日': 10,    # 母仓日：+10分
        '相日': 8,       # 相日：+8分
        '不将日': 15,    # 不将日：+15分
        '鸣吠日': 15,    # 鸣吠日：+15分
        '鸣吠对日': 10,  # 鸣吠对日：+10分
        '益后': 10,      # 益后：+10分
        '续世': 10,      # 续世：+10分
        '五合': 10,      # 五合：+10分
        '圣心': 8,       # 圣心：+8分
        '益盛': 8,       # 益盛：+8分
        '天仓': 8,       # 天仓：+8分
    },
    
    # 凶煞减分（根据严重性）
    'xiong_shensha': {
        '岁破': -30,          # 岁破：-30分
        '月破': -30,          # 月破：-30分
        '四离日': -35,        # 四离日：-35分
        '四绝日': -35,        # 四绝日：-35分
        '十恶大败': -30,      # 十恶大败：-30分
        '土王用事': -40,      # 土王用事：-40分
        '劫煞': -25,          # 劫煞：-25分
        '灾煞': -25,          # 灾煞：-25分
        '月煞': -20,          # 月煞：-20分
        '月厌': -20,          # 月厌：-20分
        '大时': -15,          # 大时：-15分
        '天吏': -20,          # 天吏：-20分
        '四废': -25,          # 四废：-25分
        '五墓': -20,          # 五墓：-20分
        '土符': -20,          # 土符：-20分
        '地囊': -25,          # 地囊：-25分
        '土瘟': -25,          # 土瘟：-25分
        '土府': -20,          # 土府：-20分
        '大耗': -20,          # 大耗：-20分
        '小耗': -15,          # 小耗：-15分
        '天贼': -20,          # 天贼：-20分
        '地贼': -15,          # 地贼：-15分
        '归忌': -22,          # 归忌：-22分
        '往亡': -22,          # 往亡：-22分
        '红嘴朱雀': -30,      # 红嘴朱雀：-30分
        '天狗': -15,          # 天狗：-15分
        '伏断日': -15,        # 伏断日：-15分
        '受死日': -22,        # 受死日：-22分
        '月刑': -18,          # 月刑：-18分
        '月害': -18,          # 月害：-18分
        '死别': -20,          # 死别：-20分
        '离披': -20,          # 离披：-20分
        '冰消瓦解': -20,      # 冰消瓦解：-20分
        '白虎入中宫': -20,    # 白虎入中宫：-20分
        '鲁班煞': -20,        # 鲁班煞：-20分
        '将军箭': -20,        # 将军箭：-20分
        '杀师日': -30,        # 杀师日：-30分
    }
}


def update_file_scores(filepath, score_config):
    """更新文件中的神煞评分
    
    Args:
        filepath: 文件路径
        score_config: 评分配置
    """
    if not os.path.exists(filepath):
        print(f'  文件不存在: {filepath}')
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = 0
    
    # 更新吉神加分
    for name, score in score_config.get('ji_shensha', {}).items():
        # 匹配 _add_shensha('name', 旧分数, ...) 或 _add_shensha("name", 旧分数, ...)
        pattern = rf'(_add_shensha\([\'"]{re.escape(name)}[\'"]\s*,\s*)([-]?\d+)(\s*,)'
        
        def replace_match(match, new_score=score):
            nonlocal changes
            old_score = int(match.group(2))
            if old_score != new_score:
                changes += 1
                return f'{match.group(1)}{new_score}{match.group(3)}'
            return match.group(0)
        
        new_content = re.sub(pattern, replace_match, content)
        content = new_content
    
    # 更新凶煞减分
    for name, score in score_config.get('xiong_shensha', {}).items():
        pattern = rf'(_add_shensha\([\'"]{re.escape(name)}[\'"]\s*,\s*)([-]?\d+)(\s*,)'
        
        def replace_match(match, new_score=score):
            nonlocal changes
            old_score = int(match.group(2))
            if old_score != new_score:
                changes += 1
                return f'{match.group(1)}{new_score}{match.group(3)}'
            return match.group(0)
        
        new_content = re.sub(pattern, replace_match, content)
        content = new_content
    
    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  ✓ 更新了 {changes} 处评分: {os.path.basename(filepath)}')
        return True
    else:
        print(f'  - 无需更新: {os.path.basename(filepath)}')
        return False


def main():
    """主函数"""
    
    print()
    print('=' * 80)
    print('【评分权重校准工具】')
    print('=' * 80)
    print()
    
    # 获取所有神煞文件
    shensha_files = []
    
    # 桌面版
    if os.path.exists(SHENSHA_DIR):
        for filename in os.listdir(SHENSHA_DIR):
            if filename.endswith('.py') and not filename.startswith('__'):
                shensha_files.append(os.path.join(SHENSHA_DIR, filename))
    
    # 手机版
    if os.path.exists(MOBILE_SHENSHA_DIR):
        for filename in os.listdir(MOBILE_SHENSHA_DIR):
            if filename.endswith('.py') and not filename.startswith('__'):
                shensha_files.append(os.path.join(MOBILE_SHENSHA_DIR, filename))
    
    print(f'找到 {len(shensha_files)} 个神煞文件')
    print()
    
    total_changes = 0
    
    for filepath in shensha_files:
        print(f'处理文件: {os.path.basename(filepath)}')
        result = update_file_scores(filepath, SCORE_CONFIG)
    
    print()
    print('=' * 80)
    print('校准完成！')
    print('=' * 80)
    
    # 显示校准摘要
    print()
    print('【校准摘要】')
    print()
    print('吉神加分调整:')
    for name, score in SCORE_CONFIG['ji_shensha'].items():
        print(f'  {name}: +{score}分')
    print()
    print('凶煞减分调整:')
    for name, score in SCORE_CONFIG['xiong_shensha'].items():
        print(f'  {name}: {score}分')


if __name__ == '__main__':
    main()
