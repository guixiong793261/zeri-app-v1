# -*- coding: utf-8 -*-
"""
================================================================================
修造神煞模块
================================================================================
实现修造择日专用神煞的检查逻辑
包含：土府、地囊、土王用事等

使用方法:
    1. 作为模块导入: from modules.shensha.修造神煞 import 修造神煞Checker
    2. 直接运行: python -m modules.shensha.修造神煞
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
    from ..工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE
except ImportError:
    from 神煞基类 import ShenShaChecker
    from 工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE


class ConstructionShenShaChecker(ShenShaChecker):
    """修建神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 岁破（已在基类中检查）
        
        # 太岁堆黄
        if self._is_taisui_duihuang(sizhu):
            self._add_shensha('太岁堆黄', -15, '忌动土修造')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 三煞
        if self._is_sansha(sizhu):
            self._add_shensha('三煞', -20, '修建大忌，犯之主灾祸')
        
        # 鲁班煞（按季节判断）
        if self._is_lubansha(sizhu):
            self._add_shensha('鲁班煞', -15, '修建不宜，犯之主损工匠')
        
        # 土符
        if self._is_tufu(sizhu):
            self._add_shensha('土符', -20, '忌动土、修造，犯之主灾')
        
        # 土府
        if self._is_tufu2(sizhu):
            self._add_shensha('土府', -15, '忌动土，犯之主败')
        
        # 土瘟
        if self._is_tuwen(sizhu):
            self._add_shensha('土瘟', -20, '忌动土、修造，犯之主病')
        
        # 地囊
        if self._is_dinang(sizhu):
            self._add_shensha('地囊', -20, '忌动土、开渠，犯之主败')
        
        # 月破（已在基类中检查）
        
        # 大耗
        if self._is_dahao(sizhu):
            self._add_shensha('大耗', -15, '忌动土，犯之主耗财')
        
        # 小耗
        if self._is_xiaohao(sizhu):
            self._add_shensha('小耗', -10, '忌动土，犯之主小损')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # ===== 凶煞 =====
        
        # 天贼
        if self._is_tianzei(sizhu):
            self._add_shensha('天贼', -15, '忌修造、动土，犯之主耗财')
        
        # 地贼
        if self._is_dizei(sizhu):
            self._add_shensha('地贼', -15, '忌修造、动土，犯之主失盗')
        
        # 四离日
        if self._is_sili(sizhu):
            self._add_shensha('四离日', -30, '春分、秋分、夏至、冬至前一日，忌大事')
        
        # 四绝日
        if self._is_sijue(sizhu):
            self._add_shensha('四绝日', -30, '立春、立夏、立秋、立冬前一日，忌大事')
        
        # 十恶大败
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -25, '忌动土修造，犯之主败')
        
        # 伏断日
        if self._is_fuduan(sizhu):
            self._add_shensha('伏断日', -10, '忌动土修造')
        
        # 将军箭
        if self._is_jiangjunjian(sizhu):
            self._add_shensha('将军箭', -15, '忌修造，犯之主伤')
        
        # ===== 吉神 =====
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 15, '动土修造大吉，百事皆宜')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 15, '动土修造大吉，百事皆宜')
        
        # 天德合
        if self._is_tiandehe(sizhu):
            self._add_shensha('天德合', 15, '动土修造吉利')
        
        # 月德合
        if self._is_yuedehe(sizhu):
            self._add_shensha('月德合', 15, '动土修造吉利')
        
        # 驿马
        if self._is_yima(sizhu):
            self._add_shensha('驿马', 10, '动土催吉，主迁动')
        
        # 三合
        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '动土吉利，主和合')
        
        # 六合
        if self._is_liuhe(sizhu):
            self._add_shensha('六合', 10, '动土吉利，主和谐')
        
        # 鸣吠日（破土专用）
        if self._is_mingfei(sizhu):
            self._add_shensha('鸣吠日', 15, '破土、启攒专用吉日')
        
        # 鸣吠对日
        if self._is_mingfeidui(sizhu):
            self._add_shensha('鸣吠对日', 10, '破土吉日')
        
        # 不将日
        if self._is_bujiang(sizhu):
            self._add_shensha('不将日', 10, '修造吉日')
    
    def _check_hour_shensha(self, sizhu):
        """检查时神煞"""
        super()._check_hour_shensha(sizhu)
    
    # ===== 凶煞判断方法 =====
    
    def _is_sansha(self, sizhu):
        """是否三煞"""
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        
        if year_zhi in SANSHA_MAP:
            sansha_indices = SANSHA_MAP[year_zhi]
            day_idx = zh_list.index(day_zhi)
            return day_idx in sansha_indices
        return False
    
    def _is_lubansha(self, sizhu):
        """是否鲁班煞（按季节判断）
        春季：亥、子日
        夏季：寅、卯日
        秋季：巳、午日
        冬季：申、酉日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 春季：寅卯辰月
        if month_zhi in ['寅', '卯', '辰']:
            return day_zhi in ['亥', '子']
        # 夏季：巳午未月
        elif month_zhi in ['巳', '午', '未']:
            return day_zhi in ['寅', '卯']
        # 秋季：申酉戌月
        elif month_zhi in ['申', '酉', '戌']:
            return day_zhi in ['巳', '午']
        # 冬季：亥子丑月
        elif month_zhi in ['亥', '子', '丑']:
            return day_zhi in ['申', '酉']
        return False
    
    def _is_tufu(self, sizhu):
        """是否土符
        土符日：按月支推算
        寅月：戌日，卯月：亥日，辰月：子日，巳月：丑日
        午月：寅日，未月：卯日，申月：辰日，酉月：巳日
        戌月：午日，亥月：未日，子月：申日，丑月：酉日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        tufu_map = {
            '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
            '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
            '戌': '午', '亥': '未', '子': '申', '丑': '酉'
        }
        return day_zhi == tufu_map.get(month_zhi)
    
    def _is_tufu2(self, sizhu):
        """是否土府（地府）
        土府日：按月支推算
        寅月：辰日，卯月：巳日，辰月：午日，巳月：未日
        午月：申日，未月：酉日，申月：戌日，酉月：亥日
        戌月：子日，亥月：丑日，子月：寅日，丑月：卯日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        tufu2_map = {
            '寅': '辰', '卯': '巳', '辰': '午', '巳': '未',
            '午': '申', '未': '酉', '申': '戌', '酉': '亥',
            '戌': '子', '亥': '丑', '子': '寅', '丑': '卯'
        }
        return day_zhi == tufu2_map.get(month_zhi)
    
    def _is_tuwen(self, sizhu):
        """是否土瘟
        土瘟日：按月支推算
        寅月：丑日，卯月：寅日，辰月：卯日，巳月：辰日
        午月：巳日，未月：午日，申月：未日，酉月：申日
        戌月：酉日，亥月：戌日，子月：亥日，丑月：子日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        tuwen_map = {
            '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申',
            '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
        }
        return day_zhi == tuwen_map.get(month_zhi)
    
    def _is_dinang(self, sizhu):
        """是否地囊
        地囊日：按月支推算
        寅月：戌日，卯月：亥日，辰月：子日，巳月：丑日
        午月：寅日，未月：卯日，申月：辰日，酉月：巳日
        戌月：午日，亥月：未日，子月：申日，丑月：酉日
        """
        return self._is_tufu(sizhu)  # 地囊与土符相同
    
    def _is_tianzei(self, sizhu):
        """是否天贼
        天贼日：按月支推算
        寅月：丑日，卯月：子日，辰月：亥日，巳月：戌日
        午月：酉日，未月：申日，申月：未日，酉月：午日
        戌月：巳日，亥月：辰日，子月：卯日，丑月：寅日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        tianzei_map = {
            '寅': '丑', '卯': '子', '辰': '亥', '巳': '戌',
            '午': '酉', '未': '申', '申': '未', '酉': '午',
            '戌': '巳', '亥': '辰', '子': '卯', '丑': '寅'
        }
        return day_zhi == tianzei_map.get(month_zhi)
    
    def _is_dizei(self, sizhu):
        """是否地贼
        地贼日：按月支推算
        寅月：辰日，卯月：巳日，辰月：午日，巳月：未日
        午月：申日，未月：酉日，申月：戌日，酉月：亥日
        戌月：子日，亥月：丑日，子月：寅日，丑月：卯日
        """
        return self._is_tufu2(sizhu)  # 地贼与土府相同
    
    def _is_dahao(self, sizhu):
        """是否大耗
        大耗日：与月破相同，即与月支相冲的日支
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        yuepo = zh_list[(idx + 6) % 12]
        return day_zhi == yuepo
    
    def _is_xiaohao(self, sizhu):
        """是否小耗
        小耗日：月破的前一日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        xiaohao = zh_list[(idx + 5) % 12]
        return day_zhi == xiaohao
    
    def _is_sili(self, sizhu):
        """是否四离日
        四离日：春分、秋分、夏至、冬至的前一日
        春分前一日（卯月末日）：辰日
        夏至前一日（午月末日）：未日
        秋分前一日（酉月末日）：戌日
        冬至前一日（子月末日）：丑日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 简化判断：卯月辰日、午月未日、酉月戌日、子月丑日
        sili_map = {
            '卯': '辰', '午': '未', '酉': '戌', '子': '丑'
        }
        return day_zhi == sili_map.get(month_zhi)
    
    def _is_sijue(self, sizhu):
        """是否四绝日
        四绝日：立春、立夏、立秋、立冬的前一日
        立春前一日（丑月末日）：寅日
        立夏前一日（辰月末日）：巳日
        立秋前一日（未月末日）：申日
        立冬前一日（戌月末日）：亥日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 简化判断：丑月寅日、辰月巳日、未月申日、戌月亥日
        sijue_map = {
            '丑': '寅', '辰': '巳', '未': '申', '戌': '亥'
        }
        return day_zhi == sijue_map.get(month_zhi)
    
    def _is_shie_dabai(self, sizhu):
        """是否十恶大败
        十恶大败日：甲辰、乙巳、丙申、丁亥、戊戌、己丑、庚辰、辛巳、壬申、癸亥
        """
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi
        
        shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
        return day_pillar in shie_dabai
    
    def _is_fuduan(self, sizhu):
        """是否伏断日
        伏断日：按日干支推算
        甲日：戌，乙日：酉，丙日：申，丁日：未，戊日：午
        己日：巳，庚日：辰，辛日：卯，壬日：寅，癸日：丑
        """
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        
        fuduan_map = {
            '甲': '戌', '乙': '酉', '丙': '申', '丁': '未', '戊': '午',
            '己': '巳', '庚': '辰', '辛': '卯', '壬': '寅', '癸': '丑'
        }
        return day_zhi == fuduan_map.get(day_gan)
    
    def _is_jiangjunjian(self, sizhu):
        """是否将军箭
        将军箭：按月支推算
        寅月：卯日，卯月：辰日，辰月：巳日，巳月：午日
        午月：未日，未月：申日，申月：酉日，酉月：戌日
        戌月：亥日，亥月：子日，子月：丑日，丑月：寅日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        jiangjunjian_map = {
            '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
            '午': '未', '未': '申', '申': '酉', '酉': '戌',
            '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
        }
        return day_zhi == jiangjunjian_map.get(month_zhi)
    
    def _is_taisui_duihuang(self, sizhu):
        """是否太岁堆黄
        太岁堆黄：按年支推算
        子年：丑日，丑年：寅日，寅年：卯日，卯年：辰日
        辰年：巳日，巳年：午日，午年：未日，未年：申日
        申年：酉日，酉年：戌日，戌年：亥日，亥年：子日
        """
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        
        zh_list = DI_ZHI
        idx = zh_list.index(year_zhi)
        duihuang = zh_list[(idx + 1) % 12]
        return day_zhi == duihuang
    
    # ===== 吉神判断方法 =====
    
    def _is_tiande(self, sizhu):
        """是否天德
        天德：按月支推算
        寅月：丁，卯月：申，辰月：壬，巳月：辛
        午月：亥，未月：甲，申月：癸，酉月：寅
        戌月：丙，亥月：乙，子月：巳，丑月：庚
        """
        from ..工具函数 import TIANDE
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        return day_gan == TIANDE.get(idx)
    
    def _is_yuede(self, sizhu):
        """是否月德
        月德：按月支推算
        寅午戌月：丙，申子辰月：壬，亥卯未月：甲，巳酉丑月：庚
        """
        from ..工具函数 import YUEDE
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        return day_gan == YUEDE.get(idx)
    
    def _is_tiandehe(self, sizhu):
        """是否天德合
        天德合：与天德相合的天干
        丁合壬，申合巳，壬合丁，辛合丙
        亥合寅，甲合己，癸合戊，寅合亥
        丙合辛，乙合庚，巳合申，庚合乙
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        tiandehe_map = {
            '寅': '壬', '卯': '巳', '辰': '丁', '巳': '丙',
            '午': '寅', '未': '己', '申': '戊', '酉': '亥',
            '戌': '辛', '亥': '庚', '子': '申', '丑': '乙'
        }
        return day_gan == tiandehe_map.get(month_zhi)
    
    def _is_yuedehe(self, sizhu):
        """是否月德合
        月德合：与月德相合的天干
        丙合辛，壬合丁，甲合己，庚合乙
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        yuedehe_map = {
            '寅': '辛', '午': '辛', '戌': '辛',  # 丙合辛
            '申': '丁', '子': '丁', '辰': '丁',  # 壬合丁
            '亥': '己', '卯': '己', '未': '己',  # 甲合己
            '巳': '乙', '酉': '乙', '丑': '乙'   # 庚合乙
        }
        return day_gan == yuedehe_map.get(month_zhi)
    
    def _is_yima(self, sizhu):
        """是否驿马
        驿马：按年支或日支推算
        申子辰年/日：寅，寅午戌年/日：申
        巳酉丑年/日：亥，亥卯未年/日：巳
        """
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        
        yima_map = {
            '申': '寅', '子': '寅', '辰': '寅',
            '寅': '申', '午': '申', '戌': '申',
            '巳': '亥', '酉': '亥', '丑': '亥',
            '亥': '巳', '卯': '巳', '未': '巳'
        }
        return day_zhi == yima_map.get(year_zhi)
    
    def _is_sanhe(self, sizhu):
        """是否三合
        三合：申子辰合水，寅午戌合火，巳酉丑合金，亥卯未合木
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        sanhe_groups = [
            {'申', '子', '辰'},
            {'寅', '午', '戌'},
            {'巳', '酉', '丑'},
            {'亥', '卯', '未'}
        ]
        
        for group in sanhe_groups:
            if month_zhi in group and day_zhi in group and month_zhi != day_zhi:
                return True
        return False
    
    def _is_liuhe(self, sizhu):
        """是否六合
        六合：子丑合，寅亥合，卯戌合，辰酉合，巳申合，午未合
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        return day_zhi == liuhe_map.get(month_zhi)
    
    def _is_mingfei(self, sizhu):
        """是否鸣吠日
        鸣吠日：庚午、庚子、庚申、辛酉、辛卯、辛巳
        专用于破土、启攒
        """
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi
        
        mingfei = ['庚午', '庚子', '庚申', '辛酉', '辛卯', '辛巳']
        return day_pillar in mingfei
    
    def _is_mingfeidui(self, sizhu):
        """是否鸣吠对日
        鸣吠对日：丙子、丙午、丙寅、丁卯、丁酉、丁亥
        """
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi
        
        mingfeidui = ['丙子', '丙午', '丙寅', '丁卯', '丁酉', '丁亥']
        return day_pillar in mingfeidui
    
    def _is_bujiang(self, sizhu):
        """是否不将日
        不将日：根据月支和日干支推算
        简化版：阳月阳日、阴月阴日
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        
        # 阳月：寅、辰、午、申、戌、子
        # 阴月：卯、巳、未、酉、亥、丑
        yang_month = ['寅', '辰', '午', '申', '戌', '子']
        yin_month = ['卯', '巳', '未', '酉', '亥', '丑']
        
        # 阳干：甲、丙、戊、庚、壬
        # 阴干：乙、丁、己、辛、癸
        yang_gan = ['甲', '丙', '戊', '庚', '壬']
        yin_gan = ['乙', '丁', '己', '辛', '癸']
        
        # 阳支：子、寅、辰、午、申、戌
        # 阴支：丑、卯、巳、未、酉、亥
        yang_zhi = ['子', '寅', '辰', '午', '申', '戌']
        yin_zhi = ['丑', '卯', '巳', '未', '酉', '亥']
        
        # 不将日：阳月取阴干阴支，阴月取阳干阳支
        if month_zhi in yang_month:
            return day_gan in yin_gan and day_zhi in yin_zhi
        else:
            return day_gan in yang_gan and day_zhi in yang_zhi
