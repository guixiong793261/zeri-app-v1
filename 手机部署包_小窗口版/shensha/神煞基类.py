# -*- coding: utf-8 -*-
"""
================================================================================
神煞模块基类
================================================================================
定义神煞检查的基础接口和通用方法
================================================================================
"""

class ShenShaChecker:
    """神煞检查器基类"""
    
    def __init__(self):
        self.shensha_list = []
    
    def check(self, sizhu, owners=None):
        """
        检查神煞
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            
        Returns:
            list: 神煞列表
        """
        self.shensha_list = []
        self._check_year_shensha(sizhu)
        self._check_month_shensha(sizhu)
        self._check_day_shensha(sizhu)
        self._check_hour_shensha(sizhu)
        self._check_special_shensha(sizhu, owners)
        return self.shensha_list
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        pass
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        pass
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        pass
    
    def _check_hour_shensha(self, sizhu):
        """检查时神煞"""
        pass
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞"""
        pass
    
    def _add_shensha(self, name, score, description):
        """
        添加神煞
        
        Args:
            name: 神煞名称
            score: 分数
            description: 描述
        """
        self.shensha_list.append({
            'name': name,
            'score': score,
            'description': description
        })
