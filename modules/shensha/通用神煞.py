# -*- coding: utf-8 -*-
"""
================================================================================
通用神煞模块
================================================================================
实现通用择日神煞的检查逻辑
包含：太岁、岁破、月破、黄道、黑道等基本神煞

使用方法:
    1. 作为模块导入: from modules.shensha.通用神煞 import CommonShenShaChecker
    2. 直接运行: python -m modules.shensha.通用神煞
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
    from ..工具函数 import TIANDE, YUEDE, DI_ZHI
except ImportError:
    from 神煞基类 import ShenShaChecker
    from 工具函数 import TIANDE, YUEDE, DI_ZHI

class CommonShenShaChecker(ShenShaChecker):
    """通用神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        year_gan = sizhu['year_gan']
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 太岁
        self._add_shensha('太岁', -20, '年之主宰，不可冒犯')
        
        # 岁破
        if day_zhi == self._get_suipo(year_zhi):
            self._add_shensha('岁破', -15, '与太岁相冲，百事不宜')
        
        # 年支三煞（劫煞、灾煞、岁煞）
        if self._is_nian_sansha(sizhu):
            self._add_shensha('年三煞', -18, '年支三煞，诸事不宜')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 月破
        if day_zhi == self._get_yuepo(month_zhi):
            self._add_shensha('月破', -25, '与月建相冲，诸事不宜')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -10, '与月建相刑，诸事不利')
        
        # 月害
        if self._is_yuehai(sizhu):
            self._add_shensha('月害', -8, '与月建相害，诸事不顺')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # ===== 凶煞 =====
        
        # 四离日
        if self._is_sili(sizhu):
            self._add_shensha('四离日', -30, '春分、秋分、夏至、冬至前一日，忌大事')
        
        # 四绝日
        if self._is_sijue(sizhu):
            self._add_shensha('四绝日', -30, '立春、立夏、立秋、立冬前一日，忌大事')
        
        # 四废日
        if self._is_sifei(sizhu):
            self._add_shensha('四废日', -15, '春庚申辛酉，夏壬子癸亥，秋甲寅乙卯，冬丙午丁巳')
        
        # 十恶大败
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -25, '忌大事，犯之主败')
        
        # ===== 吉神 =====
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 15, '百事皆宜，诸凶皆解')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 15, '百事皆宜，诸凶皆解')
        
        # 天德合
        if self._is_tiandehe(sizhu):
            self._add_shensha('天德合', 12, '诸事吉利')
        
        # 月德合
        if self._is_yuedehe(sizhu):
            self._add_shensha('月德合', 12, '诸事吉利')
        
        # 大黄道吉日
        da_huangdao = self._get_da_huangdao(day_zhi, month_zhi)
        if da_huangdao:
            self._add_shensha(f'大黄道-{da_huangdao}', 15, '黄道吉日，诸事皆宜')
        
        # 小黄道吉日（十二建星）
        xiao_huangdao = self._get_xiao_huangdao(day_zhi, month_zhi)
        if xiao_huangdao:
            self._add_shensha(f'小黄道-{xiao_huangdao}', 8, '建星吉日')
    
    def _check_hour_shensha(self, sizhu):
        """检查时神煞"""
        hour_zhi = sizhu['hour_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 黄道吉时
        huangdao_shi = self._get_huangdao_shi(day_zhi, hour_zhi)
        if huangdao_shi:
            self._add_shensha(f'黄道时-{huangdao_shi}', 8, '时辰吉利')
        
        # 日破时
        if hour_zhi == self._get_suipo(day_zhi):
            self._add_shensha('日破时', -10, '时辰与日支相冲')
    
    # ===== 辅助方法 =====
    
    def _get_suipo(self, zhi):
        """获取冲支（岁破/月破/日破）"""
        zh_list = DI_ZHI
        idx = zh_list.index(zhi)
        return zh_list[(idx + 6) % 12]
    
    def _get_yuepo(self, month_zhi):
        """获取月破"""
        return self._get_suipo(month_zhi)
    
    def _is_nian_sansha(self, sizhu):
        """是否年支三煞"""
        try:
            from ..工具函数 import SANSHA_MAP
        except ImportError:
            from 工具函数 import SANSHA_MAP
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        
        if year_zhi in SANSHA_MAP:
            sansha_indices = SANSHA_MAP[year_zhi]
            day_idx = zh_list.index(day_zhi)
            return day_idx in sansha_indices
        return False
    
    def _is_yuexing(self, sizhu):
        """是否月刑"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 地支相刑：寅刑巳、巳刑申、申刑寅（三刑）
        # 丑刑戌、戌刑未、未刑丑（三刑）
        # 子刑卯、卯刑子（相刑）
        # 辰刑辰、午刑午、酉刑酉、亥刑亥（自刑）
        xing_map = {
            '寅': '巳', '巳': '申', '申': '寅',
            '丑': '戌', '戌': '未', '未': '丑',
            '子': '卯', '卯': '子',
            '辰': '辰', '午': '午', '酉': '酉', '亥': '亥'
        }
        return day_zhi == xing_map.get(month_zhi)
    
    def _is_yuehai(self, sizhu):
        """是否月害"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 地支六害：子未害、丑午害、寅巳害、卯辰害、申亥害、酉戌害
        hai_map = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        return day_zhi == hai_map.get(month_zhi)
    
    def _is_sili(self, sizhu):
        """是否四离日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        sili_map = {
            '卯': '辰', '午': '未', '酉': '戌', '子': '丑'
        }
        return day_zhi == sili_map.get(month_zhi)
    
    def _is_sijue(self, sizhu):
        """是否四绝日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        sijue_map = {
            '丑': '寅', '辰': '巳', '未': '申', '戌': '亥'
        }
        return day_zhi == sijue_map.get(month_zhi)
    
    def _is_sifei(self, sizhu):
        """是否四废日"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        day_pillar = day_gan + day_zhi
        
        # 春季（寅卯辰月）：庚申、辛酉
        # 夏季（巳午未月）：壬子、癸亥
        # 秋季（申酉戌月）：甲寅、乙卯
        # 冬季（亥子丑月）：丙午、丁巳
        sifei_map = {
            '寅': ['庚申', '辛酉'],
            '卯': ['庚申', '辛酉'],
            '辰': ['庚申', '辛酉'],
            '巳': ['壬子', '癸亥'],
            '午': ['壬子', '癸亥'],
            '未': ['壬子', '癸亥'],
            '申': ['甲寅', '乙卯'],
            '酉': ['甲寅', '乙卯'],
            '戌': ['甲寅', '乙卯'],
            '亥': ['丙午', '丁巳'],
            '子': ['丙午', '丁巳'],
            '丑': ['丙午', '丁巳']
        }
        return day_pillar in sifei_map.get(month_zhi, [])
    
    def _is_shie_dabai(self, sizhu):
        """是否十恶大败"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi
        
        shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
        return day_pillar in shie_dabai
    
    def _is_tiande(self, sizhu):
        """是否天德"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        return day_gan == TIANDE.get(idx)
    
    def _is_yuede(self, sizhu):
        """是否月德"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        return day_gan == YUEDE.get(idx)
    
    def _is_tiandehe(self, sizhu):
        """是否天德合"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        tiandehe_map = {
            '寅': '壬', '卯': '巳', '辰': '丁', '巳': '丙',
            '午': '寅', '未': '己', '申': '戊', '酉': '亥',
            '戌': '辛', '亥': '庚', '子': '申', '丑': '乙'
        }
        return day_gan == tiandehe_map.get(month_zhi)
    
    def _is_yuedehe(self, sizhu):
        """是否月德合"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        yuedehe_map = {
            '寅': '辛', '午': '辛', '戌': '辛',
            '申': '丁', '子': '丁', '辰': '丁',
            '亥': '己', '卯': '己', '未': '己',
            '巳': '乙', '酉': '乙', '丑': '乙'
        }
        return day_gan == yuedehe_map.get(month_zhi)
    
    def _get_da_huangdao(self, day_zhi, month_zhi):
        """获取大黄道十二值星
        根据月支和日支推算
        """
        # 大黄道顺序：青龙、明堂、天刑、朱雀、金匮、天德、白虎、玉堂、天牢、玄武、司命、勾陈
        # 以月支起青龙，顺数至日支
        huangdao_list = ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈']
        zh_list = DI_ZHI
        
        month_idx = zh_list.index(month_zhi)
        day_idx = zh_list.index(day_zhi)
        
        # 从月支起青龙，计算日支对应的大黄道
        offset = (day_idx - month_idx) % 12
        return huangdao_list[offset]
    
    def _get_xiao_huangdao(self, day_zhi, month_zhi):
        """获取小黄道十二建星
        根据月支和日支推算
        """
        # 小黄道顺序：建、除、满、平、定、执、破、危、成、收、开、闭
        # 以月支起建日，顺数至日支
        jianxing_list = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
        zh_list = DI_ZHI
        
        month_idx = zh_list.index(month_zhi)
        day_idx = zh_list.index(day_zhi)
        
        # 从月支起建日，计算日支对应的小黄道
        offset = (day_idx - month_idx) % 12
        return jianxing_list[offset]
    
    def _get_huangdao_shi(self, day_zhi, hour_zhi):
        """获取黄道吉时
        根据日支和时支推算
        """
        # 黄道时辰表：以日支为键，值为从子时开始的黄道/黑道列表
        # 青龙、明堂、金匮、天德、玉堂、司命为黄道吉时
        # 天刑、朱雀、白虎、天牢、玄武、勾陈为黑道凶时
        huangdao_shi_table = {
            '子': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
            '丑': ['天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂'],
            '寅': ['朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑'],
            '卯': ['金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀'],
            '辰': ['天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮'],
            '巳': ['白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德'],
            '午': ['玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎'],
            '未': ['天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂'],
            '申': ['玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢'],
            '酉': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
            '戌': ['勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命'],
            '亥': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈']
        }
        
        if day_zhi not in huangdao_shi_table:
            return None
        
        zh_list = DI_ZHI
        hour_idx = zh_list.index(hour_zhi)
        shi_xing = huangdao_shi_table[day_zhi][hour_idx]
        
        # 只返回黄道吉时
        huangdao_xing = ['青龙', '明堂', '金匮', '天德', '玉堂', '司命']
        if shi_xing in huangdao_xing:
            return shi_xing
        return None
