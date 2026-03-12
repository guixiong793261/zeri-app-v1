# -*- coding: utf-8 -*-
"""
================================================================================
作灶神煞模块
================================================================================
实现作灶择日专用神煞的检查逻辑
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
    # 添加 shensha 目录到路径
    shensha_dir = os.path.dirname(os.path.abspath(__file__))
    if shensha_dir not in sys.path:
        sys.path.insert(0, shensha_dir)

try:
    from .神煞基类 import ShenShaChecker
except ImportError:
    from 神煞基类 import ShenShaChecker

class StoveShenShaChecker(ShenShaChecker):
    """作灶神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        # 灶神方位
        year_zhi = sizhu['year_zhi']
        if self._is_zaoshen_fangwei(sizhu):
            self._add_shensha('灶神方位吉', 10, '灶神方位吉利')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        # 月建冲灶
        if self._is_yuejian_chongzao(sizhu):
            self._add_shensha('月建冲灶', -15, '月建冲灶不宜作灶')
        
        # 土府
        if self._is_tufu(sizhu):
            self._add_shensha('土府', -10, '土府日不宜动土作灶')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        # 作灶吉日
        if self._is_zuozao_jiri(sizhu):
            self._add_shensha('作灶吉日', 15, '适合作灶的吉日')
        
        # 灶君忌日
        if self._is_zaojun_jiri(sizhu):
            self._add_shensha('灶君忌日', -20, '灶君忌日不宜作灶')
        
        # 天火日
        if self._is_tianhuo(sizhu):
            self._add_shensha('天火日', -15, '天火日不宜作灶')
        
        # 地火日
        if self._is_dihuo(sizhu):
            self._add_shensha('地火日', -12, '地火日不宜作灶')
        
        # 丙丁日
        if self._is_bingding(sizhu):
            self._add_shensha('丙丁日', 8, '丙丁日火旺适合作灶')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞"""
        # 检查宅主八字与灶向是否相合
        if owners:
            for owner in owners:
                if self._check_owner_zao_match(sizhu, owner):
                    self._add_shensha('宅主灶向相合', 10, '宅主八字与灶向相合')
                    break
    
    def _is_zaoshen_fangwei(self, sizhu):
        """是否灶神方位吉利"""
        # 灶神方位根据年支确定
        zaoshen_fangwei = {
            '子': '坤', '丑': '坤', '寅': '乾', '卯': '乾',
            '辰': '艮', '巳': '艮', '午': '震', '未': '震',
            '申': '巽', '酉': '巽', '戌': '离', '亥': '离'
        }
        year_zhi = sizhu['year_zhi']
        # 简化判断，实际应根据具体方位
        return True
    
    def _is_yuejian_chongzao(self, sizhu):
        """是否月建冲灶"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 月建与灶位相冲
        chong = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == chong.get(month_zhi)
    
    def _is_tufu(self, sizhu):
        """是否土府日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 土府日
        tufu_days = {
            '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申',
            '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
        }
        return day_zhi == tufu_days.get(month_zhi)
    
    def _is_zuozao_jiri(self, sizhu):
        """是否作灶吉日"""
        day_zhi = sizhu['day_zhi']
        zuozao_jiri = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in zuozao_jiri
    
    def _is_zaojun_jiri(self, sizhu):
        """是否灶君忌日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 灶君忌日
        zaojun_jiri = {
            '子': '未', '丑': '申', '寅': '酉', '卯': '戌',
            '辰': '亥', '巳': '子', '午': '丑', '未': '寅',
            '申': '卯', '酉': '辰', '戌': '巳', '亥': '午'
        }
        return day_zhi == zaojun_jiri.get(month_zhi)
    
    def _is_tianhuo(self, sizhu):
        """是否天火日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 天火日
        tianhuo_days = {
            '寅': '子', '卯': '丑', '辰': '寅', '巳': '卯',
            '午': '辰', '未': '巳', '申': '午', '酉': '未',
            '戌': '申', '亥': '酉', '子': '戌', '丑': '亥'
        }
        return day_zhi == tianhuo_days.get(month_zhi)
    
    def _is_dihuo(self, sizhu):
        """是否地火日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 地火日
        dihuo_days = {
            '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
            '午': '未', '未': '申', '申': '酉', '酉': '戌',
            '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
        }
        return day_zhi == dihuo_days.get(month_zhi)
    
    def _is_bingding(self, sizhu):
        """是否丙丁日"""
        day_gan = sizhu['day_gan']
        return day_gan in ['丙', '丁']
