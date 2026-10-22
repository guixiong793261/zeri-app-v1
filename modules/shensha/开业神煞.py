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

# 制化引擎（2026-10-21 制化第一批，001 §155）：大时豁免判定单点。
# 本行原为死链（super 先行占位），基类接线豁免后若不同步接线会在豁免日
# 复活 -12（基类豁免日不发射'大时'正名，同名去重失效）。
try:
    from .制化引擎 import eval_dashi_chouwei_exempt, DASHI_EXEMPT_KEY
except ImportError:
    from 制化引擎 import eval_dashi_chouwei_exempt, DASHI_EXEMPT_KEY

# 批次 1（2026-10-22，001 §161）：建除谓词统一走 modules/建除.py
try:
    from ..建除 import is_jianchu as _is_jianchu
except ImportError:
    from 建除 import is_jianchu as _is_jianchu

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

        # 2026-10 A1：'岁德'/'岁德合' 同名重加删除（基类年作用域统一注册，
        # 年干比日干典载口径）。

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

        # 大煞发射已删（2026-10-18 月家P1：协纪卷十仅忌军事，开业超范围；
        # docs/月家P1_大煞八专四击_对勘.md）

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
        
        # 2026-10 批4（001 §74）：'吉期' 重加删除——基类月作用域已统一
        # 注册 '吉期' +10（E3 修正后委托典载《历例》"常居月建前一辰"表），
        # 本块 super 先行后同名重加被 _add_shensha 先到先得去重，从未生效。
        
        # 王日
        if self._is_wangri(sizhu):
            self._add_shensha('王日', 10, '王日主旺相')
        
        # 官日
        if self._is_guanri(sizhu):
            self._add_shensha('官日', 8, '官日主官禄')
        
        # 2026-10 批1（001 §70）：'吉庆' 删除——《协纪》卷三十六·辨讹钦定判伪
        # （《选择宗镜》「满德吉庆为伪吉日……毋庸深辨」）。
        
        # 月厌
        if self._is_yueyan(sizhu):
            self._add_shensha('月厌', -15, '月厌主厌恶')
        
        # 月虚
        if self._is_yuexu(sizhu):
            self._add_shensha('月虚', -10, '月虚主虚耗')
        
        # 大时
        if self._is_dashi(sizhu):
            # 2026-10-21 制化第一批（001 §155，矩阵#9）：与基类同键豁免注记
            # （丑未月二德并止忌军事=映射空集全免附警示）。
            _da, _dn = eval_dashi_chouwei_exempt(sizhu, getattr(self, '_std_event', None))
            if _da:
                self._add_shensha(DASHI_EXEMPT_KEY, 0, _dn)
            else:
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
        
        # 破日（批次 1，001 §161）：破日 ≡ 月破（同为月支六冲），
        # 月破已在月神煞块扣 -30；此处原再发 '破日' -20 属双计，已删除。日下为谓词说明。
        # if self._is_pori(sizhu):
        #     self._add_shensha('破日', -20, '破日不宜开业')
        
        # 闭日
        if self._is_biari(sizhu):
            self._add_shensha('闭日', -15, '闭日不宜开业')
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 20, '天德日百事吉')
        
        # 天德合
        if self._is_tiande_he(sizhu):
            self._add_shensha('天德合', 15, '天德合，大吉')
        
        # 2026-10 A4：异名 '{日/月}三奇' 重加删除——基类 super 日块已按顺布
        # 连珠单点注册 '三奇{日/月/星}'；旧日块异名与其同日双扣（各 +15），
        # ('开业','日三奇')/('开业','月三奇') 分值键同步从 SHENSHA_SCORES 删除。

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

        # 2026-10 A1：'天马' 同名重加删除（典载天马为月神，基类月作用域注册）。

        # 天赦
        if self._is_tianshe(sizhu):
            self._add_shensha('天赦', 25, '天赦日百事吉')
        
        # 母仓
        if self._is_mucang(sizhu):
            self._add_shensha('母仓', 10, '母仓日吉')
        
        # 受死日发射已删（2026-10-20 受死日删除批，001 §145）：陈书受死语境
        # 无「忌开业」明文（快照 docs/影响面快照_受死日删除候选.md §一），
        # 基类日块同步加 _std_event 门控。原发射为：
        #     if self._is_shousi_day(sizhu):
        #         self._add_shensha('受死日', -22, '受死日不宜开业')
        
        # 往亡日
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -20, '往亡日不宜开业')
        
        # 十恶大败发射行已注释（2026-10-19 全删批·一档，001 §139）：三库无
        # 「十恶大败」普适日课忌明文（取证 aa47dcd／快照 2ca7b4e；协纪
        # 「然惟随各年及本命避之」属本命避忌，非日课普适扣分）；谓词保留作无禄日载体。
        # if self._is_shie_dabai(sizhu):
        #     self._add_shensha('十恶大败', -30, '十恶大败日大忌')
    
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
        """是否满日（批次 1：统一建除谓词，废弃固定地支名单）"""
        return _is_jianchu(sizhu, '满')
    
    def _is_chengri(self, sizhu):
        """是否成日（批次 1：统一建除谓词，废弃固定地支名单）"""
        return _is_jianchu(sizhu, '成')
    
    def _is_pori(self, sizhu):
        """是否破日（批次 1：统一建除谓词；破日 ≡ 月破）
        保留谓词供核对，发射侧已去重（月破 -30 唯一扣分）。
        """
        return _is_jianchu(sizhu, '破')
    
    def _is_biari(self, sizhu):
        """是否闭日（批次 1：统一建除谓词，废弃固定地支名单）"""
        return _is_jianchu(sizhu, '闭')
    
    def _check_owner_kaiye_match(self, sizhu, owner):
        """检查事主与开业日是否相合"""
        return True