# -*- coding: utf-8 -*-
"""
================================================================================
神煞模块基类
================================================================================
定义神煞检查的基础接口和通用方法
================================================================================
"""

# 导入工具函数
try:
    from ..工具函数 import TIANDE, YUEDE, DI_ZHI
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from 工具函数 import TIANDE, YUEDE, DI_ZHI


class ShenShaChecker:
    """神煞检查器基类"""
    
    def __init__(self):
        self.shensha_list = []
    
    def check(self, sizhu, owners=None, **kwargs):
        """
        检查神煞
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            **kwargs: 额外参数（如 zaoxiang, zaowei 等）
            
        Returns:
            list: 神煞列表
        """
        self.shensha_list = []
        self._check_year_shensha(sizhu, **kwargs)
        self._check_month_shensha(sizhu, **kwargs)
        self._check_day_shensha(sizhu, **kwargs)
        self._check_hour_shensha(sizhu, **kwargs)
        self._check_special_shensha(sizhu, owners, **kwargs)
        return self.shensha_list
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        pass
    
    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        pass
    
    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        pass
    
    def _check_hour_shensha(self, sizhu, **kwargs):
        """检查时神煞"""
        pass
    
    def _check_special_shensha(self, sizhu, owners, **kwargs):
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
    
    # ============ 通用吉星检查方法 ============
    
    def _is_tiande(self, sizhu):
        """是否天德"""
        month_zhi = sizhu.get('month_zhi', '')
        day_gan = sizhu.get('day_gan', '')
        if not month_zhi or not day_gan:
            return False
        try:
            idx = DI_ZHI.index(month_zhi)
            return day_gan == TIANDE.get(idx)
        except (ValueError, KeyError):
            return False
    
    def _is_yuede(self, sizhu):
        """是否月德"""
        month_zhi = sizhu.get('month_zhi', '')
        day_gan = sizhu.get('day_gan', '')
        if not month_zhi or not day_gan:
            return False
        try:
            idx = DI_ZHI.index(month_zhi)
            return day_gan == YUEDE.get(idx)
        except (ValueError, KeyError):
            return False
    
    def _is_tiande_he(self, sizhu):
        """天德合日"""
        month_zhi = sizhu.get('month_zhi', '')
        day_gan = sizhu.get('day_gan', '')
        
        tiande_map = {
            '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
            '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
            '戌': '丙', '亥': '乙', '子': '巳', '丑': '庚'
        }
        
        tiande = tiande_map.get(month_zhi, '')
        if not tiande:
            return False
        
        he_map = {'甲': '己', '乙': '庚', '丙': '辛', '丁': '壬', '戊': '癸',
                 '己': '甲', '庚': '乙', '辛': '丙', '壬': '丁', '癸': '戊',
                 '寅': '亥', '申': '巳', '亥': '寅', '巳': '申'}
        
        tiande_he = he_map.get(tiande, '')
        return day_gan == tiande_he or tiande_he == day_gan
    
    def _is_yuede_he(self, sizhu):
        """月德合日"""
        month_zhi = sizhu.get('month_zhi', '')
        day_gan = sizhu.get('day_gan', '')
        
        yuede_map = {
            '寅': '丙', '午': '丙', '戌': '丙',
            '申': '壬', '子': '壬', '辰': '壬',
            '巳': '庚', '酉': '庚', '丑': '庚',
            '亥': '甲', '卯': '甲', '未': '甲'
        }
        
        yuede = yuede_map.get(month_zhi, '')
        if not yuede:
            return False
        
        he_map = {'甲': '己', '乙': '庚', '丙': '辛', '丁': '壬', '戊': '癸',
                 '己': '甲', '庚': '乙', '辛': '丙', '壬': '丁', '癸': '戊'}
        
        yuede_he = he_map.get(yuede, '')
        return day_gan == yuede_he
    
    def _is_sanqi(self, sizhu):
        """三奇日（乙丙丁日奇、甲戊庚月奇、壬癸辛星奇）"""
        year_gan = sizhu.get('year_gan', '')
        month_gan = sizhu.get('month_gan', '')
        day_gan = sizhu.get('day_gan', '')
        hour_gan = sizhu.get('hour_gan', '')
        
        all_gans = [year_gan, month_gan, day_gan, hour_gan]
        
        # 日奇：乙丙丁
        riqi = ['乙', '丙', '丁']
        riqi_count = sum(1 for g in riqi if g in all_gans)
        
        # 月奇：甲戊庚
        yueqi = ['甲', '戊', '庚']
        yueqi_count = sum(1 for g in yueqi if g in all_gans)
        
        # 星奇：壬癸辛
        xingqi = ['壬', '癸', '辛']
        xingqi_count = sum(1 for g in xingqi if g in all_gans)
        
        # 有两奇以上为吉
        if riqi_count >= 2:
            return '日'
        if yueqi_count >= 2:
            return '月'
        if xingqi_count >= 2:
            return '星'
        
        return None
    
    def _is_jiangxing(self, sizhu):
        """将星日"""
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        
        # 将星：日支三合方为将星
        sanhe_groups = {
            '寅': ['午', '戌'],  # 寅午戌三合
            '午': ['寅', '戌'],
            '戌': ['寅', '午'],
            '亥': ['卯', '未'],  # 亥卯未三合
            '卯': ['亥', '未'],
            '未': ['亥', '卯'],
            '申': ['子', '辰'],  # 申子辰三合
            '子': ['申', '辰'],
            '辰': ['申', '子'],
            '巳': ['酉', '丑'],  # 巳酉丑三合
            '酉': ['巳', '丑'],
            '丑': ['巳', '酉']
        }
        
        jiangxing_list = sanhe_groups.get(day_zhi, [])
        return month_zhi in jiangxing_list
