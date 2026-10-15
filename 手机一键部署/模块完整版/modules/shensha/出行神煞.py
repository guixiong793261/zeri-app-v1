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
    from .神煞基类 import ShenShaChecker, is_wangwang_by_zhi
except ImportError:
    from 神煞基类 import ShenShaChecker, is_wangwang_by_zhi

class TravelShenShaChecker(ShenShaChecker):
    """出行神煞检查器"""
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)
        
        # 太岁方位
        if self._is_taisui_fangwei(sizhu):
            self._add_shensha('太岁方位', -10, '太岁方位不宜出行')

        # 2026-10 A1：'岁德'/'岁德合' 同名重加删除（基类年作用域统一注册，
        # 年干比日干典载口径）；'天马' 年作用域注册删除（典载天马为月神，
        # 已由基类月作用域统一注册）。

        # 2026-10 A3：'飞廉' 年作用域注册删除（典载飞廉为月神，
        # 已由基类月作用域统一注册）。
        
        # 亡神（伏兵）
        if self._is_fubing(sizhu):
            self._add_shensha('亡神', -12, '亡神主暗害，不宜出行')
        
        # 劫煞
        if self._is_jiesha(sizhu):
            self._add_shensha('劫煞', -25, '劫煞凶，切忌出行')
        
        # 灾煞
        if self._is_zaijiesha(sizhu):
            self._add_shensha('灾煞', -25, '灾煞主灾祸，切忌出行')
    
    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        super()._check_month_shensha(sizhu, **kwargs)
        
        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -30, '月破日不宜出行')
        
        # 往亡
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡', -20, '往亡日不宜出行')

        # 2026-10 A1：'月空' 同名重加删除（基类月作用域统一注册，
        # 月神比日干典载口径）。

        # 月恩
        if self._is_yueen(sizhu):
            self._add_shensha('月恩', 10, '月恩吉星，宜出行')
        
        # 2026-10 批4（001 §74）：'吉期' 重加删除——基类月作用域已统一
        # 注册 '吉期' +10（E3 修正后委托典载《历例》"常居月建前一辰"表），
        # 本块 super 先行后同名重加被 _add_shensha 先到先得去重，从未生效。
        
        # 阳德
        if self._is_yangde(sizhu):
            self._add_shensha('阳德', 10, '阳德吉星，宜出行')
        
        # 阴德
        if self._is_yinde(sizhu):
            self._add_shensha('阴德', 10, '阴德吉星，宜出行')
        
        # 不将日
        if self._is_bujiang(sizhu):
            self._add_shensha('不将日', 15, '不将日利于出行')
        
        # 月厌
        if self._is_yueyan(sizhu):
            self._add_shensha('月厌', -15, '月厌日不宜出行')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -15, '月刑日不宜出行')
        
        # 月害
        if self._is_yuehai(sizhu):
            self._add_shensha('月害', -15, '月害日不宜出行')
        
        # 大时（咸池）
        if self._is_dashi(sizhu):
            self._add_shensha('大时', -12, '大时（咸池）主凶，不宜出行')
        
        # 天吏（致死）
        if self._is_tianli(sizhu):
            self._add_shensha('天吏', -15, '天吏（致死）主凶，不宜出行')
        
        # 四废
        if self._is_sifei(sizhu):
            self._add_shensha('四废', -15, '四废日不宜出行')
    
    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        super()._check_day_shensha(sizhu, **kwargs)
        
        # 出行吉日
        if self._is_chuxing_jiri(sizhu):
            self._add_shensha('出行吉日', 15, '适合出行的吉日')
        
        # 2026-10 A6-4：异名 '驿马日' 重加删除——基类 super 日块已按正名 '驿马'
        # (+10) 单点注册（同一 self._is_yima；本类 override 为仅年支），旧异名与其
        # 同日**双扣**（10+12=22）、且异名键 ('出行','驿马日') 只此一处注册。
        # ('出行','驿马日') 分值键同步从 SHENSHA_SCORES 删除。

        # 2026-10 A1：异名 '天马日' 重加删除——典载天马（月神）已由基类月
        # 作用域以正名 '天马' 注册；旧日作用域 '天马日' 与其同日双扣（各 +10），
        # ('出行','天马日') 分值键同步从 SHENSHA_SCORES 删除。

        # 路空日（D4 阶段1 止损：名实错位待重建）
        # 当前 _is_lukong 按日干五合查日支（甲己申酉、乙庚午未…），与标准
        # 旬空法零重叠（2026 年当前实现 60 天 vs 旬空 50 天，交集 0），
        # 推法待《协纪》核实。止损禁用发射，避免出行评分含错误 -15。
        # if self._is_lukong(sizhu):
        #     self._add_shensha('路空日', -15, '路空日不宜出行')
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 20, '天德吉星，宜出行')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 18, '月德吉星，宜出行')
        
        # 天德合
        if self._is_tiande_he(sizhu):
            self._add_shensha('天德合', 15, '天德合吉星，宜出行')
        
        # 月德合
        if self._is_yuede_he(sizhu):
            self._add_shensha('月德合', 12, '月德合吉星，宜出行')
        
        # 2026-10 A4：异名 '三奇' 重加删除——基类 super 日块已按顺布连珠
        # 单点注册 '三奇{日/月/星}'；旧日块异名 '三奇' 与其同日双扣（各 +15），
        # ('出行','三奇') 分值键同步从 SHENSHA_SCORES 删除。

        # 将星
        if self._is_jiangxing(sizhu):
            self._add_shensha('将星', 12, '将星吉星，宜出行')
        
        # 六合
        if self._is_liuhe(sizhu):
            self._add_shensha('六合', 12, '六合日利于出行')
        
        # 三合
        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '三合日利于出行')
        
        # 天赦
        if self._is_tianshe(sizhu):
            self._add_shensha('天赦', 25, '天赦大吉，宜出行')
        
        # 母仓
        if self._is_mucang(sizhu):
            self._add_shensha('母仓', 10, '母仓吉星，宜出行')
        
        # 受死日
        if self._is_shousi_day(sizhu):
            self._add_shensha('受死日', -22, '受死日不宜出行')
        
        # 往亡日
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -20, '往亡日不宜出行')
        
        # 十恶大败
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -30, '十恶大败日不宜出行')

        # 2026-10 A1：'反支日' 同名重加删除（基类日作用域统一注册，
        # 谓词已修为按农历月朔支起算的典载口径）。

        # 上朔日
        if self._is_shangshuo(sizhu):
            self._add_shensha('上朔日', -10, '上朔日不宜出行')
    
    def _check_hour_shensha(self, sizhu, **kwargs):
        """检查时神煞"""
        super()._check_hour_shensha(sizhu, **kwargs)
        
        # 出行吉时
        if self._is_chuxing_jishi(sizhu):
            self._add_shensha('出行吉时', 8, '适合出行的时辰')
    
    def _check_special_shensha(self, sizhu, owners, **kwargs):
        """检查特殊神煞，主要处理事主（出行者）生肖与日课的冲合"""
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
    
    def _is_yuexing(self, sizhu):
        """是否月刑"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
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
        
        hai_map = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        return day_zhi == hai_map.get(month_zhi)
    
    # 2026-10 出行往亡修复（方案A）：原内嵌错表已删除（巳寅亥申 4 位周期，
    # 与《协纪》口诀零交集、与全部已知神煞无重合、无典据），
    # 改为委托基类 is_wangwang_by_zhi（与安葬/嫁娶/入宅/动土/拆舍/通用一致）。
    def _is_wangwang(self, sizhu):
        """往亡（《协纪》口诀"正寅二巳三申四亥…"，月支查日支）"""
        return is_wangwang_by_zhi(sizhu.get('month_zhi', ''),
                                  sizhu.get('day_zhi', ''))
    
    def _is_chuxing_jiri(self, sizhu):
        """是否出行吉日"""
        day_zhi = sizhu['day_zhi']
        chuxing_jiri = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in chuxing_jiri
    
    # 2026-10 A6-4 D 批次：原 _is_yima override（仅年支）已删除，改继承
    # 基类仅月支口径（《协纪》卷六：驿马为月神，正月起申逆行四孟）。

    # 2026-10 A1：本类 _is_tianma override 已删除——其月支表（寅午卯申
    # 辰戌巳子午寅未辰）与《星历考原》典载逐月一致，基类谓词修正后同表
    # 同源，收口到 神煞基类.is_tianma_by_zhi（含年作用域旧注册一并移除）。

    def _is_lukong(self, sizhu):
        """路空日谓词（D4 阶段1 名实错位止损，待阶段2 重建）

        2026-10-15 D4 诊断：当前实现按日干五合查日支（甲己申酉、乙庚午未、
        丙辛辰巳、丁壬寅卯、戊癸子丑），与标准六甲旬空法 2026 年零重叠
        （当前 60 天 vs 旬空 50 天，交集 0），推法待《协纪》核实。
        发射块已墓碑禁用（见 _check_day_shensha L139），本谓词保留待重建。

        墓碑（旧推法，勿复活）：
            甲己→申酉 / 乙庚→午未 / 丙辛→辰巳 / 丁壬→寅卯 / 戊癸→子丑
        """
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        lukong = {
            '甲': ['申', '酉'], '己': ['申', '酉'],
            '乙': ['午', '未'], '庚': ['午', '未'],
            '丙': ['辰', '巳'], '辛': ['辰', '巳'],
            '丁': ['寅', '卯'], '壬': ['寅', '卯'],
            '戊': ['子', '丑'], '癸': ['子', '丑']
        }
        return day_zhi in lukong.get(day_gan, [])
    
    def _is_chuxing_jishi(self, sizhu):
        """是否出行吉时"""
        hour_zhi = sizhu['hour_zhi']
        jishi = ['子', '寅', '卯', '巳', '午', '酉']
        return hour_zhi in jishi
    
    def _check_owner_chuxing_match(self, sizhu, owner):
        """检查事主与出行日是否相合"""
        # 简化判断
        return True