# -*- coding: utf-8 -*-
"""
================================================================================
出行神煞模块
================================================================================
实现出行择日专用神煞的检查逻辑
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

class TravelShenShaChecker(ShenShaChecker):
    """出行神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        # 太岁方位
        year_zhi = sizhu['year_zhi']
        if self._is_taisui_fangwei(sizhu):
            self._add_shensha('太岁方位', -10, '太岁方位不宜出行')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -15, '月破日不宜出行')
        
        # 往亡
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡', -20, '往亡日不宜出行')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        # 出行吉日
        if self._is_chuxing_jiri(sizhu):
            self._add_shensha('出行吉日', 15, '适合出行的吉日')
        
        # 驿马日
        if self._is_yima(sizhu):
            self._add_shensha('驿马日', 12, '驿马日利于出行')
        
        # 天马日
        if self._is_tianma(sizhu):
            self._add_shensha('天马日', 10, '天马日利于远行')
        
        # 路空日
        if self._is_lukong(sizhu):
            self._add_shensha('路空日', -15, '路空日不宜出行')
        
        # 朱雀日
        if self._is_zhuque(sizhu):
            self._add_shensha('朱雀日', -10, '朱雀日出行有口舌是非')
        
        # 白虎日
        if self._is_baihu(sizhu):
            self._add_shensha('白虎日', -12, '白虎日出行有凶险')
    
    def _check_hour_shensha(self, sizhu):
        """检查时神煞"""
        super()._check_hour_shensha(sizhu)
        
        # 出行吉时
        if self._is_chuxing_jishi(sizhu):
            self._add_shensha('出行吉时', 8, '适合出行的时辰')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞"""
        # 检查事主八字与出行日是否相合
        if owners:
            for owner in owners:
                if self._check_owner_chuxing_match(sizhu, owner):
                    self._add_shensha('事主出行相合', 10, '事主八字与出行日相合')
                    break
    
    def _is_taisui_fangwei(self, sizhu):
        """是否太岁方位"""
        year_zhi = sizhu['year_zhi']
        # 太岁方位
        taisui_fangwei = {
            '子': '北', '丑': '东北', '寅': '东北', '卯': '东',
            '辰': '东南', '巳': '东南', '午': '南', '未': '西南',
            '申': '西南', '酉': '西', '戌': '西北', '亥': '西北'
        }
        # 简化判断
        return False
    
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
    
    def _is_wangwang(self, sizhu):
        """是否往亡日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 往亡日
        wangwang_days = {
            '寅': '巳', '卯': '寅', '辰': '亥', '巳': '申',
            '午': '巳', '未': '寅', '申': '亥', '酉': '申',
            '戌': '巳', '亥': '寅', '子': '亥', '丑': '申'
        }
        return day_zhi == wangwang_days.get(month_zhi)
    
    def _is_chuxing_jiri(self, sizhu):
        """是否出行吉日"""
        day_zhi = sizhu['day_zhi']
        chuxing_jiri = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in chuxing_jiri
    
    def _is_yima(self, sizhu):
        """是否驿马日"""
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        # 驿马日
        yima = {
            '申': '寅', '子': '寅', '辰': '寅',
            '寅': '申', '午': '申', '戌': '申',
            '巳': '亥', '酉': '亥', '丑': '亥',
            '亥': '巳', '卯': '巳', '未': '巳'
        }
        return day_zhi == yima.get(year_zhi)
    
    def _is_tianma(self, sizhu):
        """是否天马日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 天马日
        tianma = {
            '寅': '午', '卯': '申', '辰': '戌', '巳': '子',
            '午': '寅', '未': '辰', '申': '午', '酉': '申',
            '戌': '戌', '亥': '子', '子': '寅', '丑': '辰'
        }
        return day_zhi == tianma.get(month_zhi)
    
    def _is_lukong(self, sizhu):
        """是否路空日"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        # 路空日（甲己日申酉空，乙庚日午未空，丙辛日辰巳空，丁壬日寅卯空，戊癸日子丑空）
        lukong = {
            '甲': ['申', '酉'], '己': ['申', '酉'],
            '乙': ['午', '未'], '庚': ['午', '未'],
            '丙': ['辰', '巳'], '辛': ['辰', '巳'],
            '丁': ['寅', '卯'], '壬': ['寅', '卯'],
            '戊': ['子', '丑'], '癸': ['子', '丑']
        }
        return day_zhi in lukong.get(day_gan, [])
    
    def _is_zhuque(self, sizhu):
        """是否朱雀日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 朱雀日
        zhuque = {
            '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
            '午': '未', '未': '申', '申': '酉', '酉': '戌',
            '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
        }
        return day_zhi == zhuque.get(month_zhi)
    
    def _is_baihu(self, sizhu):
        """是否白虎日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 白虎日
        baihu = {
            '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
            '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
            '戌': '午', '亥': '未', '子': '申', '丑': '酉'
        }
        return day_zhi == baihu.get(month_zhi)
    
    def _is_chuxing_jishi(self, sizhu):
        """是否出行吉时"""
        hour_zhi = sizhu['hour_zhi']
        jishi = ['子', '寅', '卯', '巳', '午', '酉']
        return hour_zhi in jishi
    
    def _check_owner_chuxing_match(self, sizhu, owner):
        """检查事主与出行日是否相合"""
        # 简化判断
        return True
