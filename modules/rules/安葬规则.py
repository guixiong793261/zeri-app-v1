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
安葬规则模块
================================================================================
实现安葬择日的宜忌规则
================================================================================
"""

from .规则基类 import EventRuleChecker

class BurialRuleChecker(EventRuleChecker):
    """安葬规则检查器"""
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查安葬规则"""
        # 安葬宜日：阴日
        if self._is_yin_day(sizhu):
            yi_list.append('安葬')
        
        # 安葬忌日：阳日
        if self._is_yang_day(sizhu):
            ji_list.append('安葬')
        
        # 山向相关规则
        if shan_xiang:
            if self._is_shan_xiang_yi(sizhu, shan_xiang):
                yi_list.append(f'{shan_xiang}向安葬')
            if self._is_shan_xiang_ji(sizhu, shan_xiang):
                ji_list.append(f'{shan_xiang}向安葬')
    
    def _is_yin_day(self, sizhu):
        """是否阴日"""
        # 阴日：子、丑、寅、卯、辰、巳
        yin_days = ['子', '丑', '寅', '卯', '辰', '巳']
        return sizhu['day_zhi'] in yin_days
    
    def _is_yang_day(self, sizhu):
        """是否阳日"""
        # 阳日：午、未、申、酉、戌、亥
        yang_days = ['午', '未', '申', '酉', '戌', '亥']
        return sizhu['day_zhi'] in yang_days
    
    def _is_shan_xiang_yi(self, sizhu, shan_xiang):
        """山向宜日"""
        # 安葬宜：山向五行与日支五行相生
        shan_xiang_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }
        
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        sx_wuxing = shan_xiang_wuxing.get(shan_xiang)
        dz_wuxing = zhi_wuxing.get(sizhu['day_zhi'])
        
        # 五行相生
        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        return sheng.get(sx_wuxing) == dz_wuxing
    
    def _is_shan_xiang_ji(self, sizhu, shan_xiang):
        """山向忌日"""
        # 安葬忌：山向五行与日支五行相克
        shan_xiang_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }
        
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        sx_wuxing = shan_xiang_wuxing.get(shan_xiang)
        dz_wuxing = zhi_wuxing.get(sizhu['day_zhi'])
        
        # 五行相克
        ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        return ke.get(sx_wuxing) == dz_wuxing
    
    def get_forbidden_directions(self, sizhu):
        """
        获取禁止使用的方位列表
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            list: 禁止使用的方位列表
        """
        forbidden = []
        all_directions = ['壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
                         '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥']
        
        for direction in all_directions:
            if self._is_shan_xiang_ji(sizhu, direction):
                forbidden.append(direction)
        
        return forbidden
    
    def is_direction_forbidden(self, sizhu, direction):
        """
        检查某个方位是否被禁止
        
        Args:
            sizhu: 四柱信息
            direction: 方位
            
        Returns:
            bool: 是否被禁止
        """
        return self._is_shan_xiang_ji(sizhu, direction)
