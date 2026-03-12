import sys
import os

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)

# -*- coding: utf-8 -*-
"""
================================================================================
婚嫁规则模块
================================================================================
实现婚嫁择日的宜忌规则
================================================================================
"""

from .规则基类 import EventRuleChecker

class MarriageRuleChecker(EventRuleChecker):
    """婚嫁规则检查器"""
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查婚嫁规则"""
        # 检查婚嫁宜日
        if self._is_marriage_yi_day(sizhu):
            yi_list.append('嫁娶')
        
        # 检查婚嫁忌日
        if self._is_marriage_ji_day(sizhu):
            ji_list.append('嫁娶')
    
    def _is_marriage_yi_day(self, sizhu):
        """是否婚嫁宜日"""
        day_zhi = sizhu['day_zhi']
        yi_days = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未']
        return day_zhi in yi_days
    
    def _is_marriage_ji_day(self, sizhu):
        """是否婚嫁忌日"""
        day_zhi = sizhu['day_zhi']
        ji_days = ['申', '酉', '戌', '亥']
        return day_zhi in ji_days
    
    def _check_bazi_match(self, bride, groom):
        """检查八字匹配"""
        # 简化的八字匹配检查
        # 实际应用中需要更复杂的逻辑
        return True
