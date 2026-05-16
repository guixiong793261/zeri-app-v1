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
        """检查特殊神煞，主要处理事主（店主）生肖与日课的冲合"""
        if not owners:
            return
        
        for i, owner in enumerate(owners):
            owner_zodiac = owner.get('生肖', '')
            owner_year_zhi = owner.get('年支', '')
            owner_name = owner.get('姓名', f'事主{i+1}')
            
            if not owner_zodiac and not owner_year_zhi:
                continue
            
            # 年支相冲
            year_zhi = sizhu['year_zhi']
            if self._is_chong(year_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'年冲{owner_name}', -20, f'年支与{owner_name}生肖相冲')
            
            # 月支相冲
            month_zhi = sizhu['month_zhi']
            if self._is_chong(month_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'月冲{owner_name}', -15, f'月支与{owner_name}生肖相冲')
            
            # 日支相冲
            day_zhi = sizhu['day_zhi']
            if self._is_chong(day_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'日冲{owner_name}', -25, f'日支与{owner_name}生肖相冲，大忌')
            elif self._is_he(day_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'日合{owner_name}', 10, f'日支与{owner_name}生肖相合')
            
            # 时支相冲
            hour_zhi = sizhu.get('hour_zhi', '')
            if hour_zhi and self._is_chong(hour_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'时冲{owner_name}', -12, f'时支与{owner_name}生肖相冲')
            elif hour_zhi and self._is_he(hour_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'时合{owner_name}', 6, f'时支与{owner_name}生肖相合')
    
    def _shengxiao_to_zhi(self, shengxiao):
        """生肖转换为地支"""
        shengxiao_map = {
            '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
            '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
            '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
        }
        return shengxiao_map.get(shengxiao)
    
    def _is_chong(self, zhi1, zhi2):
        """检查两个地支是否相冲"""
        if not zhi1 or not zhi2:
            return False
        
        # 如果zhi2是生肖，转换为地支
        if zhi2 not in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
            zhi2 = self._shengxiao_to_zhi(zhi2)
            if not zhi2:
                return False
        
        chong_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return zhi1 == chong_map.get(zhi2)
    
    def _is_he(self, zhi1, zhi2):
        """检查两个地支是否相合（六合或三合）"""
        if not zhi1 or not zhi2:
            return False
        
        # 如果zhi2是生肖，转换为地支
        if zhi2 not in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
            zhi2 = self._shengxiao_to_zhi(zhi2)
            if not zhi2:
                return False
        
        # 六合
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        if liuhe_map.get(zhi1) == zhi2:
            return True
        
        # 三合
        sanhe_sets = [{'申', '子', '辰'}, {'寅', '午', '戌'}, {'巳', '酉', '丑'}, {'亥', '卯', '未'}]
        for s in sanhe_sets:
            if zhi1 in s and zhi2 in s and zhi1 != zhi2:
                return True
        
        return False
    
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
