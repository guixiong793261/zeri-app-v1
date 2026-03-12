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
修建规则模块
================================================================================
实现修建择日的宜忌规则
================================================================================
"""

from .规则基类 import EventRuleChecker

class ConstructionRuleChecker(EventRuleChecker):
    """修建规则检查器"""
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查修建规则"""
        # 通用修建规则
        if self._is_construction_yi_day(sizhu):
            yi_list.append('修造')
            yi_list.append('动土')
        
        if self._is_construction_ji_day(sizhu):
            ji_list.append('修造')
            ji_list.append('动土')
        
        # 阳宅特定规则
        if house_type == "阳宅":
            self._check_yang_zhai_rules(sizhu, shan_xiang, yi_list, ji_list)
        
        # 阴宅特定规则
        elif house_type == "阴宅":
            self._check_yin_zhai_rules(sizhu, shan_xiang, yi_list, ji_list)
        
        # 安葬特定规则已移至安葬规则模块
    
    def _is_construction_yi_day(self, sizhu):
        """是否修建宜日"""
        day_zhi = sizhu['day_zhi']
        yi_days = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未']
        return day_zhi in yi_days
    
    def _is_construction_ji_day(self, sizhu):
        """是否修建忌日"""
        day_zhi = sizhu['day_zhi']
        ji_days = ['申', '酉', '戌', '亥']
        return day_zhi in ji_days
    
    def _check_yang_zhai_rules(self, sizhu, shan_xiang, yi_list, ji_list):
        """阳宅特定规则"""
        # 阳宅宜日：择日以生旺为主
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 阳宅宜：日支与月支相生或比和
        if self._is_zhi_sheng_he(day_zhi, month_zhi):
            yi_list.append('阳宅修造')
        
        # 阳宅忌：日支与月支相冲
        if self._is_zhi_chong(day_zhi, month_zhi):
            ji_list.append('阳宅修造')
        
        # 山向相关规则
        if shan_xiang:
            if self._is_shan_xiang_yi(shan_xiang, day_zhi):
                yi_list.append(f'{shan_xiang}向修造')
    
    def _check_yin_zhai_rules(self, sizhu, shan_xiang, yi_list, ji_list):
        """阴宅特定规则"""
        # 阴宅宜日：择日以安静为主
        day_zhi = sizhu['day_zhi']
        
        # 阴宅宜：阴支日（子、丑、寅、卯、辰、巳）
        yin_days = ['子', '丑', '寅', '卯', '辰', '巳']
        if day_zhi in yin_days:
            yi_list.append('阴宅修造')
        
        # 阴宅忌：阳支日（午、未、申、酉、戌、亥）
        yang_days = ['午', '未', '申', '酉', '戌', '亥']
        if day_zhi in yang_days:
            ji_list.append('阴宅修造')
        
        # 山向相关规则
        if shan_xiang:
            if self._is_shan_xiang_ji(shan_xiang, day_zhi):
                ji_list.append(f'{shan_xiang}向修造')
    
    def _is_zhi_sheng_he(self, zhi1, zhi2):
        """判断地支是否相生或比和"""
        # 地支相生关系
        sheng = {
            '子': '寅卯', '丑': '巳午', '寅': '巳午', '卯': '巳午',
            '辰': '申酉', '巳': '申酉', '午': '申酉', '未': '亥子',
            '申': '亥子', '酉': '亥子', '戌': '寅卯', '亥': '寅卯'
        }
        # 比和（相同）
        if zhi1 == zhi2:
            return True
        # 相生
        return zhi2 in sheng.get(zhi1, '')
    
    def _is_zhi_chong(self, zhi1, zhi2):
        """判断地支是否相冲"""
        chong = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return chong.get(zhi1) == zhi2
    
    def _is_shan_xiang_yi(self, shan_xiang, day_zhi):
        """山向宜日"""
        # 简单的山向与日支匹配规则
        # 山向五行与日支五行相生
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
        dz_wuxing = zhi_wuxing.get(day_zhi)
        
        # 五行相生
        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        return sheng.get(sx_wuxing) == dz_wuxing
    
    def _is_shan_xiang_ji(self, shan_xiang, day_zhi):
        """山向忌日"""
        # 山向五行与日支五行相克
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
        dz_wuxing = zhi_wuxing.get(day_zhi)
        
        # 五行相克
        ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        return ke.get(sx_wuxing) == dz_wuxing
