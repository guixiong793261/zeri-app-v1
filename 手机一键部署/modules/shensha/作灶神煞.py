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
    
    def __init__(self):
        super().__init__()
        # 五行映射
        self.zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        self.direction_wuxing = {
            '东': '木', '南': '火', '西': '金', '北': '水',
            '东南': '木', '西南': '土', '东北': '土', '西北': '金',
            '艮': '土', '坤': '土', '震': '木', '巽': '木',
            '离': '火', '坎': '水', '兑': '金', '乾': '金'
        }
        self.wuxing_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)
        # 灶神方位检查暂时禁用（需要方位信息）
        # 如需启用，请传入 zaoxiang 或 zaowei 参数
    
    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        super()._check_month_shensha(sizhu, **kwargs)
        # 土府日暂时禁用（无可靠依据）
    
    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        super()._check_day_shensha(sizhu, **kwargs)
        
        # 丙丁日（火旺适合作灶）
        if self._is_bingding(sizhu):
            self._add_shensha('丙丁日', 5, '丙丁日火旺适合作灶（需结合其他神煞）')
        
        # 天火日（传统公式：正月子、二月丑、三月寅...）
        if self._is_tianhuo(sizhu):
            self._add_shensha('天火日', -15, '天火日不宜作灶')
        
        # 地火日（传统公式：正月戌、二月亥、三月子...）
        if self._is_dihuo(sizhu):
            self._add_shensha('地火日', -12, '地火日不宜作灶')
    
    def _check_special_shensha(self, sizhu, owners, **kwargs):
        """检查特殊神煞，主要处理事主（宅主）生肖与日课的冲合"""
        zaoxiang = kwargs.get('zaoxiang')
        zaowei = kwargs.get('zaowei')
        
        if not owners:
            return
        
        for i, owner in enumerate(owners):
            owner_zodiac = owner.get('生肖', '')
            owner_year_zhi = owner.get('年支', '')
            owner_name = owner.get('姓名', f'宅主{i+1}')
            
            # 宅主灶向相合
            if self._check_owner_zao_match(sizhu, owner, zaoxiang, zaowei):
                self._add_shensha('宅主灶向相合', 10, '宅主八字与灶向相合')
            
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
            elif self._check_owner_sanhe_liuhe(sizhu, owner):
                self._add_shensha('日支与宅主合', 8, '日支与宅主年支相合')
            
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
    
    def _check_owner_zao_match(self, sizhu, owner, zaoxiang=None, zaowei=None):
        """检查宅主与灶向是否相合"""
        # 获取宅主年命五行
        owner_year_zhi = owner.get('year_zhi', '')
        owner_wuxing = self.zhi_wuxing.get(owner_year_zhi, '')
        
        # 获取灶向或灶位五行
        direction = zaoxiang or zaowei
        if not direction:
            return False
        
        # 尝试从方向获取五行
        dir_wuxing = self.direction_wuxing.get(direction)
        if not dir_wuxing:
            # 尝试从第一个字获取五行
            dir_wuxing = self.direction_wuxing.get(direction[0])
        
        if not dir_wuxing:
            return False
        
        # 灶向生宅主命为吉
        return self.wuxing_sheng.get(dir_wuxing) == owner_wuxing
    
    def _check_owner_sanhe_liuhe(self, sizhu, owner):
        """检查日支与宅主年支是否三合或六合"""
        day_zhi = sizhu.get('day_zhi', '')
        owner_year_zhi = owner.get('year_zhi', '')
        
        if not day_zhi or not owner_year_zhi:
            return False
        
        # 六合检查
        liuhe = {('子', '丑'), ('寅', '亥'), ('卯', '戌'), ('辰', '酉'), ('巳', '申'), ('午', '未')}
        if (day_zhi, owner_year_zhi) in liuhe or (owner_year_zhi, day_zhi) in liuhe:
            return True
        
        # 三合检查
        sanhe_groups = [{'申', '子', '辰'}, {'寅', '午', '戌'}, {'巳', '酉', '丑'}, {'亥', '卯', '未'}]
        for group in sanhe_groups:
            if day_zhi in group and owner_year_zhi in group:
                return True
        
        return False
    
    def _is_bingding(self, sizhu):
        """是否丙丁日"""
        day_gan = sizhu.get('day_gan', '')
        return day_gan in ['丙', '丁']
    
    def _is_tianhuo(self, sizhu):
        """是否天火日（传统公式：正月子、二月丑、三月寅...，即月支前2位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        
        if not month_zhi or not day_zhi:
            return False
        
        # 天火日：月支前2位（正月寅→子，二月卯→丑，...）
        zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        try:
            month_idx = zhi_order.index(month_zhi)
            tianhuo_zhi = zhi_order[(month_idx - 2) % 12]
            return day_zhi == tianhuo_zhi
        except ValueError:
            return False
    
    def _is_dihuo(self, sizhu):
        """是否地火日（传统公式：正月戌、二月亥、三月子...，即月支后2位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        
        if not month_zhi or not day_zhi:
            return False
        
        # 地火日：月支后2位（正月寅→辰，二月卯→巳，...）
        zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        try:
            month_idx = zhi_order.index(month_zhi)
            dihuo_zhi = zhi_order[(month_idx + 2) % 12]
            return day_zhi == dihuo_zhi
        except ValueError:
            return False
