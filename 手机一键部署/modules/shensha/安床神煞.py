# -*- coding: utf-8 -*-
"""
================================================================================
安床神煞模块
================================================================================
实现安床择日专用神煞的检查逻辑
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


class BedShenShaChecker(ShenShaChecker):
    """安床神煞检查器"""

    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)

        # 胎神方位
        year_zhi = sizhu['year_zhi']
        if self._is_taishen_fangwei(sizhu):
            self._add_shensha('胎神方位吉', 10, '胎神方位吉利')

    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)

        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -15, '月破日不宜安床')

        # 土府
        if self._is_tufu(sizhu):
            self._add_shensha('土府', -10, '土府日不宜安床')

    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)

        # 安床吉日
        if self._is_anchuang_jiri(sizhu):
            self._add_shensha('安床吉日', 15, '适合安床的吉日')

        # 床公床母日
        if self._is_chuanggong_chuangmu(sizhu):
            self._add_shensha('床公床母日', 12, '床公床母日利于安床')

        # 胎神日
        if self._is_taishen(sizhu):
            self._add_shensha('胎神日', -15, '胎神日不宜安床')

        # 冲床日
        if self._is_chongchuang(sizhu):
            self._add_shensha('冲床日', -12, '冲床日不宜安床')

        # 杨公忌日
        if self._is_yanggongji(sizhu):
            self._add_shensha('杨公忌日', -20, '杨公忌日不宜安床')

        # 红砂日
        if self._is_hongsha(sizhu):
            self._add_shensha('红砂日', -15, '红砂日不宜安床')

    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞，主要处理事主（安床者）生肖与日课的冲合"""
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
    
    def _is_taishen_fangwei(self, sizhu):
        """是否胎神方位吉利"""
        # 胎神方位根据年支确定
        taishen_fangwei = {
            '子': '门', '丑': '碓磨', '寅': '厨灶', '卯': '大门',
            '辰': '门床', '巳': '碓磨', '午': '厨灶', '未': '灶炉',
            '申': '门床', '酉': '碓磨', '戌': '厨灶', '亥': '床仓'
        }
        year_zhi = sizhu['year_zhi']
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

    def _is_tufu(self, sizhu):
        """是否土府日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        tufu_days = {
            '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申',
            '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
        }
        return day_zhi == tufu_days.get(month_zhi)

    def _is_anchuang_jiri(self, sizhu):
        """是否安床吉日"""
        day_zhi = sizhu['day_zhi']
        # 安床吉日：阳日
        anchuang_jiri = ['午', '未', '申', '酉', '戌', '亥']
        return day_zhi in anchuang_jiri

    def _is_chuanggong_chuangmu(self, sizhu):
        """是否床公床母日"""
        day_zhi = sizhu['day_zhi']
        # 床公床母日
        chuanggong_chuangmu = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in chuanggong_chuangmu

    def _is_taishen(self, sizhu):
        """是否胎神日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 胎神日
        taishen_days = {
            '寅': '子', '卯': '丑', '辰': '寅', '巳': '卯',
            '午': '辰', '未': '巳', '申': '午', '酉': '未',
            '戌': '申', '亥': '酉', '子': '戌', '丑': '亥'
        }
        return day_zhi == taishen_days.get(month_zhi)

    def _is_chongchuang(self, sizhu):
        """是否冲床日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 冲床日
        chongchuang = {
            '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
            '午': '子', '未': '丑', '申': '寅', '酉': '卯',
            '戌': '辰', '亥': '巳', '子': '午', '丑': '未'
        }
        return day_zhi == chongchuang.get(month_zhi)

    def _is_yanggongji(self, sizhu):
        """是否杨公忌日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 杨公忌日
        yanggongji = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == yanggongji.get(month_zhi)

    def _is_hongsha(self, sizhu):
        """是否红砂日"""
        day_zhi = sizhu['day_zhi']
        # 红砂日
        hongsha = ['酉', '巳', '丑']
        return day_zhi in hongsha

    def _check_owner_anchuang_match(self, sizhu, owner):
        """检查事主与安床日是否相合"""
        # 简化判断
        return True
