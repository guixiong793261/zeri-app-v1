# -*- coding: utf-8 -*-
"""
================================================================================
规则模块基类
================================================================================
定义规则检查的基础接口
================================================================================
"""

class EventRuleChecker:
    """事项规则检查器基类"""
    
    def __init__(self):
        pass
    
    def check(self, sizhu, owners=None, house_type=None, shan_xiang=None, 
              zaoxiang=None, zaowei=None, chuangwei=None):
        """
        检查规则
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            house_type: 宅型（阳宅/阴宅）
            shan_xiang: 山向
            zaoxiang: 灶向（作灶专用）
            zaowei: 灶位（作灶专用）
            chuangwei: 床位朝向（安床专用）
            
        Returns:
            tuple: (宜事项列表, 忌事项列表)
        """
        yi_list = []
        ji_list = []
        
        self._check_rules(sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list)
        
        return yi_list, ji_list
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """
        检查具体规则
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            house_type: 宅型（阳宅/阴宅）
            shan_xiang: 山向
            zaoxiang: 灶向（作灶专用）
            zaowei: 灶位（作灶专用）
            chuangwei: 床位朝向（安床专用）
            yi_list: 宜事项列表
            ji_list: 忌事项列表
        """
        pass
