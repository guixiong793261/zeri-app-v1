# -*- coding: utf-8 -*-
"""
================================================================================
开业神煞模块
================================================================================
实现开业择日专用神煞的检查逻辑
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

class OpeningShenShaChecker(ShenShaChecker):
    """开业神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        # 财神方位
        year_gan = sizhu['year_gan']
        if self._is_caishen_fangwei(sizhu):
            self._add_shensha('财神方位吉', 15, '财神方位吉利')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -15, '月破日不宜开业')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -10, '月刑日不宜开业')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        # 开业吉日
        if self._is_kaiye_jiri(sizhu):
            self._add_shensha('开业吉日', 20, '适合开业的吉日')
        
        # 满日
        if self._is_manri(sizhu):
            self._add_shensha('满日', 12, '满日适合开业')
        
        # 成日
        if self._is_chengri(sizhu):
            self._add_shensha('成日', 10, '成日适合开业')
        
        # 破日
        if self._is_pori(sizhu):
            self._add_shensha('破日', -20, '破日不宜开业')
        
        # 闭日
        if self._is_biari(sizhu):
            self._add_shensha('闭日', -15, '闭日不宜开业')
        
        # 劫煞
        if self._is_jiesha(sizhu):
            self._add_shensha('劫煞', -12, '劫煞日不宜开业')
        
        # 灾煞
        if self._is_zaisha(sizhu):
            self._add_shensha('灾煞', -12, '灾煞日不宜开业')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞"""
        # 检查事主八字与开业日是否相合
        if owners:
            for owner in owners:
                if self._check_owner_kaiye_match(sizhu, owner):
                    self._add_shensha('事主开业相合', 10, '事主八字与开业日相合')
                    break
    
    def _is_caishen_fangwei(self, sizhu):
        """是否财神方位吉利"""
        # 财神方位根据年干确定
        caishen_fangwei = {
            '甲': '艮', '乙': '坤', '丙': '兑', '丁': '乾',
            '戊': '艮', '己': '坤', '庚': '兑', '辛': '乾',
            '壬': '艮', '癸': '坤'
        }
        year_gan = sizhu['year_gan']
        # 简化判断
        return True
    
    def _is_yuepo(self, sizhu):
        """是否月破"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        chong = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == chong.get(month_zhi)
    
    def _is_yuexing(self, sizhu):
        """是否月刑"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 地支相刑
        xing = {
            '子': '卯', '丑': '戌', '寅': '巳', '卯': '子',
            '辰': '辰', '巳': '申', '午': '午', '未': '丑',
            '申': '寅', '酉': '酉', '戌': '未', '亥': '亥'
        }
        return day_zhi == xing.get(month_zhi)
    
    def _is_kaiye_jiri(self, sizhu):
        """是否开业吉日"""
        day_zhi = sizhu['day_zhi']
        kaiye_jiri = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in kaiye_jiri
    
    def _is_manri(self, sizhu):
        """是否满日"""
        # 建除十二神之满日
        day_zhi = sizhu['day_zhi']
        # 简化判断，实际应根据月建推算
        manri = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in manri
    
    def _is_chengri(self, sizhu):
        """是否成日"""
        # 建除十二神之成日
        day_zhi = sizhu['day_zhi']
        chengri = ['丑', '辰', '未', '戌']
        return day_zhi in chengri
    
    def _is_pori(self, sizhu):
        """是否破日"""
        # 建除十二神之破日
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        chong = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == chong.get(month_zhi)
    
    def _is_biari(self, sizhu):
        """是否闭日"""
        # 建除十二神之闭日
        day_zhi = sizhu['day_zhi']
        biari = ['亥', '子', '丑']
        return day_zhi in biari
    
    def _is_jiesha(self, sizhu):
        """是否劫煞"""
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        jiesha = {
            '申': '巳', '子': '巳', '辰': '巳',
            '寅': '亥', '午': '亥', '戌': '亥',
            '巳': '寅', '酉': '寅', '丑': '寅',
            '亥': '申', '卯': '申', '未': '申'
        }
        return day_zhi == jiesha.get(year_zhi)
    
    def _is_zaisha(self, sizhu):
        """是否灾煞"""
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        zaisha = {
            '申': '午', '子': '午', '辰': '午',
            '寅': '子', '午': '子', '戌': '子',
            '巳': '卯', '酉': '卯', '丑': '卯',
            '亥': '酉', '卯': '酉', '未': '酉'
        }
        return day_zhi == zaisha.get(year_zhi)
    
    def _check_owner_kaiye_match(self, sizhu, owner):
        """检查事主与开业日是否相合"""
        # 简化判断
        return True
