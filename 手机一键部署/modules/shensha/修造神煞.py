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

        # 杀师日（修造大忌，伤工匠）
        if self._is_shashi(sizhu):
            self._add_shensha('杀师日', -25, '修造大忌，犯之伤害工匠')

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

    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞，主要处理事主（宅主/工匠）生肖与日课的冲合"""
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
        if zhi2 not in DI_ZHI:
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
        if zhi2 not in DI_ZHI:
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
        注：传统鲁班煞有多种说法，常见版本是按天干：
        春三月忌庚辛日，夏三月忌壬癸日，秋三月忌甲乙日，冬三月忌丙丁日。
        此处用地支版本，与常见版本不同，供参考使用。
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
        注：传统土符映射表因流派不同而有差异，当前映射表来源待验证。
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
        注：传统土府映射表因流派不同而有差异，当前映射表来源待验证。
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
        注：传统土瘟映射表因流派不同而有差异，当前映射表来源待验证。
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
        注：传统地囊是"土王用事后"，不是固定日支，当前映射与土符相同，来源待验证。
        地囊日：按月支推算
        寅月：戌日，卯月：亥日，辰月：子日，巳月：丑日
        午月：寅日，未月：卯日，申月：辰日，酉月：巳日
        戌月：午日，亥月：未日，子月：申日，丑月：酉日
        """
        return self._is_tufu(sizhu)  # 地囊与土符相同
    
    def _is_tianzei(self, sizhu):
        """是否天贼
        注：传统天贼映射表因流派不同而有差异，当前映射表来源待验证。
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
        注：传统地贼映射表因流派不同而有差异，当前映射表与土府相同，来源待验证。
        地贼日：按月支推算
        寅月：辰日，卯月：巳日，辰月：午日，巳月：未日
        午月：申日，未月：酉日，申月：戌日，酉月：亥日
        戌月：子日，亥月：丑日，子月：寅日，丑月：卯日
        """
        return self._is_tufu2(sizhu)  # 地贼与土府相同
    
    def _is_dahao(self, sizhu):
        """是否大耗
        注：简化版本。传统大耗是月神煞，并非简单的月破。
        此处简化为月破日，仅供参考。
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
        注：简化版本。传统小耗定义不一，并非简单的月破前一日。
        此处简化为月破前一日，仅供参考。
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
        注：简化版本，不考虑节气具体日期。
        传统四离日是春分、夏至、秋分、冬至的前一日。
        此处用月支+日支组合简化判断，可能有偏差。
        春分前一日（卯月末日）：辰日
        夏至前一日（午月末日）：未日
        秋分前一日（酉月末日）：戌日
        冬至前一日（子月末日）：丑日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']

        sili_map = {
            '卯': '辰', '午': '未', '酉': '戌', '子': '丑'
        }
        return day_zhi == sili_map.get(month_zhi)
    
    def _is_sijue(self, sizhu):
        """是否四绝日
        注：简化版本，不考虑节气具体日期。
        传统四绝日是立春、立夏、立秋、立冬的前一日。
        此处用月支+日支组合简化判断，可能有偏差。
        立春前一日（丑月末日）：寅日
        立夏前一日（辰月末日）：巳日
        立秋前一日（未月末日）：申日
        立冬前一日（戌月末日）：亥日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']

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
        注意：传统伏断日指"建除十二神"中的"危"日，并非按天干查地支。
        当前实现无权威依据，已禁用。
        如需使用，请使用建除十二神判断。
        """
        return False
    
    def _is_jiangjunjian(self, sizhu):
        """是否将军箭
        注：将军箭有多个版本，此处为简化版本，仅供参考。
        传统版本可能更复杂，需结合时柱判断。
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

    def _is_shashi(self, sizhu):
        """是否杀师日（修造大忌，伤工匠）

        杀师日传统算法：
        1. 根据年支和月支的关系确定：
           - 子午卯酉年：辰戌丑未月为杀师月
           - 辰戌丑未年：寅申巳亥月为杀师月
           - 寅申巳亥年：丙丁壬癸月为杀师月
        2. 杀师之日：春戌夏丑秋辰冬未（四季月的丑、辰、戌、未日）

        这里采用简化版本：四季月（辰戌丑未）的特定日支为杀师日
        另一种常用算法：基于年支确定杀师之时
        """
        year_zhi = sizhu['year_zhi']
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']

        # 算法1：四季月（辰戌丑未月）的特定日支为杀师日
        # 春季（寅卯辰月）的戌日、夏季（巳午未月）的丑日
        # 秋季（申酉戌月）的辰日、冬季（亥子丑月）的未日
        season_to_month = {
            '寅': '辰', '卯': '戌', '辰': '丑',  # 春：辰戌丑
            '巳': '未', '午': '辰', '未': '戌',  # 夏：未辰戌
            '申': '丑', '酉': '未', '戌': '辰',  # 秋：丑未辰
            '亥': '戌', '子': '丑', '丑': '未'   # 冬：戌丑未
        }

        expected_day_zhi = season_to_month.get(month_zhi)
        if expected_day_zhi and day_zhi == expected_day_zhi:
            return True

        # 算法2：基于年支的杀师日
        # 子午年：卯酉月；卯酉年：子午月；辰戌年：丑未月；丑未年：辰戌月
        # 寅申年：巳亥月；巳亥年：寅申月
        year_to_month = {
            '子': ['卯', '酉'], '午': ['卯', '酉'],
            '卯': ['子', '午'], '酉': ['子', '午'],
            '辰': ['丑', '未'], '戌': ['丑', '未'],
            '丑': ['辰', '戌'], '未': ['辰', '戌'],
            '寅': ['巳', '亥'], '申': ['巳', '亥'],
            '巳': ['寅', '申'], '亥': ['寅', '申']
        }

        if year_zhi in year_to_month and month_zhi in year_to_month[year_zhi]:
            # 这些月份的特定日支为杀师日
            # 子午卯酉年：忌辰戌丑未日；辰戌丑未年：忌寅申巳亥日
            shashi_day_for_year = {
                '子': ['辰', '戌', '丑', '未'], '午': ['辰', '戌', '丑', '未'],
                '卯': ['辰', '戌', '丑', '未'], '酉': ['辰', '戌', '丑', '未'],
                '辰': ['寅', '申', '巳', '亥'], '戌': ['寅', '申', '巳', '亥'],
                '丑': ['寅', '申', '巳', '亥'], '未': ['寅', '申', '巳', '亥'],
                '寅': ['子', '午', '卯', '酉'], '申': ['子', '午', '卯', '酉'],
                '巳': ['子', '午', '卯', '酉'], '亥': ['子', '午', '卯', '酉']
            }
            if year_zhi in shashi_day_for_year and day_zhi in shashi_day_for_year[year_zhi]:
                return True

        return False

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
        五合规则：甲己合、乙庚合、丙辛合、丁壬合、戊癸合
        天德为天干时，检查日干是否为其五合
        """
        from ..工具函数 import TIANDE
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        tiande = TIANDE.get(idx)

        if not tiande:
            return False

        # 五合天干
        wuhe = {'甲': '己', '己': '甲', '乙': '庚', '庚': '乙',
                '丙': '辛', '辛': '丙', '丁': '壬', '壬': '丁', '戊': '癸', '癸': '戊'}

        # 天德为天干时，日干为其五合即为天德合
        if tiande in wuhe:
            return day_gan == wuhe.get(tiande)
        return False
    
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
        注意：简化版不将日判断不可靠，易产生大量误判。
        正确的实现需要参考婚嫁模块的 is_bujiang_day 函数，
        但该函数需要完整的 date_obj 来计算日干支。
        此处简化版已禁用，返回 False。
        如需使用不将日，请在调用前通过日期对象调用婚嫁模块的 is_bujiang_day。
        """
        return False
