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
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)
        
        # 2026-09-16修复：原此处为 '财神方位吉' +15 —— _is_caishen_fangwei 内部
        # 按年干算出财神方位字典后并未使用、直接 return True，导致任何一天开业
        # 都恒定 +15。财神方位是“方位”概念（日干定方位），判定吉凶须与店门/神位
        # 坐向比对，而本检查器拿不到坐向参数，无法判断，故该项不计分、予以删除。
        # （每日财神方位本身已在【今日黄历】模块按通书口径展示。）
        
        # 岁德
        if self._is_suide(sizhu):
            self._add_shensha('岁德', 20, '岁之德神，主化凶为吉')
        
        # 岁德合
        if self._is_suide_he(sizhu):
            self._add_shensha('岁德合', 15, '岁德合，大吉')
        
        # 岁合
        if self._is_suihe(sizhu):
            self._add_shensha('岁合', 12, '岁合主和合')
        
        # 岁禄
        if self._is_sui_lu(sizhu):
            self._add_shensha('岁禄', 15, '岁禄主财禄')
        
        # 劫煞
        if self._is_jiesha(sizhu):
            self._add_shensha('劫煞', -25, '劫煞日不宜开业')
        
        # 灾煞
        if self._is_zaijiesha(sizhu):
            self._add_shensha('灾煞', -25, '灾煞日不宜开业')
        
        # 亡神
        if self._is_fubing(sizhu):
            self._add_shensha('亡神', -12, '亡神主凶亡')
        
        # 大煞
        if self._is_dasha(sizhu):
            self._add_shensha('大煞', -12, '大煞主破败')
        
        # 五鬼
        if self._is_wugui(sizhu):
            self._add_shensha('五鬼', -15, '五鬼主耗散')
        
        # 金神：年神方位煞，不用于日课评分（见基类 _get_jinshen_positions）
        
        # 破败
        if self._is_pobai(sizhu):
            self._add_shensha('破败', -10, '破败主耗散')
    
    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        super()._check_month_shensha(sizhu, **kwargs)
        
        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -30, '月破日不宜开业')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -15, '月刑日不宜开业')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 18, '月德日百事吉')
        
        # 月德合
        if self._is_yuede_he(sizhu):
            self._add_shensha('月德合', 12, '月德合，吉')
        
        # 月恩
        if self._is_yueen(sizhu):
            self._add_shensha('月恩', 10, '月恩日主恩泽')
        
        # 五富
        if self._is_wufu(sizhu):
            self._add_shensha('五富', 12, '五富主财富')
        
        # 吉期
        if self._is_jiqi(sizhu):
            self._add_shensha('吉期', 10, '吉期主吉庆')
        
        # 王日
        if self._is_wangri(sizhu):
            self._add_shensha('王日', 10, '王日主旺相')
        
        # 官日
        if self._is_guanri(sizhu):
            self._add_shensha('官日', 8, '官日主官禄')
        
        # 福生
        if self._is_fusheng(sizhu):
            self._add_shensha('福生', 10, '福生主福生')
        
        # 吉庆
        if self._is_jiqing(sizhu):
            self._add_shensha('吉庆', 10, '吉庆主吉庆')
        
        # 月厌
        if self._is_yueyan(sizhu):
            self._add_shensha('月厌', -15, '月厌主厌恶')
        
        # 月虚
        if self._is_yuexu(sizhu):
            self._add_shensha('月虚', -10, '月虚主虚耗')
        
        # 大时
        if self._is_dashi(sizhu):
            self._add_shensha('大时', -12, '大时主凶')
        
        # 天吏
        if self._is_tianli(sizhu):
            self._add_shensha('天吏', -15, '天吏主凶')
    
    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        super()._check_day_shensha(sizhu, **kwargs)
        
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
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 20, '天德日百事吉')
        
        # 天德合
        if self._is_tiande_he(sizhu):
            self._add_shensha('天德合', 15, '天德合，大吉')
        
        # 三奇
        sanqi_result = self._is_sanqi(sizhu)
        if sanqi_result:
            self._add_shensha(f'{sanqi_result}三奇', 15, f'{sanqi_result}三奇照临，百事皆宜')
        
        # 将星
        if self._is_jiangxing(sizhu):
            self._add_shensha('将星', 12, '将星到座，吉')
        
        # 六合
        if self._is_liuhe(sizhu):
            self._add_shensha('六合', 12, '六合日吉')
        
        # 三合
        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '三合日吉')
        
        # 驿马
        if self._is_yima(sizhu):
            self._add_shensha('驿马', 10, '驿马主行动')
        
        # 天马
        if self._is_tianma(sizhu):
            self._add_shensha('天马', 10, '天马主行动')
        
        # 天赦
        if self._is_tianshe(sizhu):
            self._add_shensha('天赦', 25, '天赦日百事吉')
        
        # 母仓
        if self._is_mucang(sizhu):
            self._add_shensha('母仓', 10, '母仓日吉')
        
        # 受死日
        if self._is_shousi_day(sizhu):
            self._add_shensha('受死日', -22, '受死日不宜开业')
        
        # 往亡日
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -20, '往亡日不宜开业')
        
        # 十恶大败
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -30, '十恶大败日大忌')
    
    def _check_special_shensha(self, sizhu, owners, **kwargs):
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
    
    def _is_yuexing(self, sizhu):
        """是否月刑"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
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
        day_zhi = sizhu['day_zhi']
        manri = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in manri
    
    def _is_chengri(self, sizhu):
        """是否成日"""
        day_zhi = sizhu['day_zhi']
        chengri = ['丑', '辰', '未', '戌']
        return day_zhi in chengri
    
    def _is_pori(self, sizhu):
        """是否破日"""
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
        day_zhi = sizhu['day_zhi']
        biari = ['亥', '子', '丑']
        return day_zhi in biari
    
    def _check_owner_kaiye_match(self, sizhu, owner):
        """检查事主与开业日是否相合"""
        return True