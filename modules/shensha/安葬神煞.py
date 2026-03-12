# -*- coding: utf-8 -*-
"""
================================================================================
安葬神煞模块
================================================================================
实现安葬择日专用神煞的检查逻辑
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

class BurialShenShaChecker(ShenShaChecker):
    """安葬神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        year_zhi = sizhu['year_zhi']
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        
        # 年重丧（按年支和日干查）
        if self._is_nian_zhongsang(sizhu):
            self._add_shensha('年重丧', -30, '年重丧大凶，绝对不可用')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        
        # 重丧（按月查日干）
        if self._is_zhongsang(sizhu):
            self._add_shensha('重丧', -30, '重丧日大凶，绝对不宜安葬')
        
        # 三丧（按季节查日支）
        if self._is_sansang(sizhu):
            self._add_shensha('三丧', -25, '三丧日不宜安葬')
        
        # 复日（重丧类）
        if self._is_furi(sizhu):
            self._add_shensha('复日', -25, '复日重丧，不宜安葬')
        
        # 往亡日
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -20, '往亡日忌安葬、出行')
        
        # 天吏日
        if self._is_tianli(sizhu):
            self._add_shensha('天吏日', -15, '天吏日不宜安葬')
        
        # 致死日
        if self._is_zhisi(sizhu):
            self._add_shensha('致死日', -15, '致死日不宜安葬')
        
        # 月破（已在基类中检查，但安葬需特别强调）
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -25, '月破日诸事不宜，安葬大忌')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # ===== 极凶日（安葬绝对禁忌）=====
        
        # 四离日
        if self._is_sili(sizhu):
            self._add_shensha('四离日', -30, '春分、秋分、夏至、冬至前一日，安葬大忌')
        
        # 四绝日
        if self._is_sijue(sizhu):
            self._add_shensha('四绝日', -30, '立春、立夏、立秋、立冬前一日，安葬大忌')
        
        # 十恶大败日
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -30, '十恶大败日，诸事不宜，安葬大忌')
        
        # 伏断日
        if self._is_fuduan(sizhu):
            self._add_shensha('伏断日', -15, '伏断日不宜安葬')
        
        # ===== 凶煞 =====
        
        # 土府
        if self._is_tufu(sizhu):
            self._add_shensha('土府', -15, '土府日不宜安葬')
        
        # 八座日
        if self._is_bazuori(sizhu):
            self._add_shensha('八座日', -12, '八座日不宜安葬')
        
        # ===== 吉日 =====
        
        # 鸣吠日（正确的天干地支组合）
        if self._is_mingfei(sizhu):
            self._add_shensha('鸣吠日', 15, '鸣吠日利于安葬，大吉')
        
        # 鸣吠对日
        if self._is_mingfeidui(sizhu):
            self._add_shensha('鸣吠对日', 10, '鸣吠对日利于安葬')
        
        # 不将日
        if self._is_bujiang(sizhu):
            self._add_shensha('不将日', 8, '不将日安葬可用')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞（与亡者相关）"""
        if not owners:
            return
        
        for owner in owners:
            # 获取亡者生肖
            owner_zodiac = owner.get('生肖', '')
            if not owner_zodiac:
                continue
            
            # 的呼日（与亡者生肖相冲）
            if self._is_dihu(sizhu, owner_zodiac):
                self._add_shensha('的呼日', -15, f'的呼日与亡者生肖({owner_zodiac})相冲，呼人')
            
            # 人呼日（与孝子生肖相冲）
            if self._is_renhu(sizhu, owner_zodiac):
                self._add_shensha('人呼日', -12, f'人呼日与亡者生肖({owner_zodiac})相关')
            
            # 亡者生肖与日支相冲
            if self._is_owner_chong(sizhu, owner_zodiac):
                self._add_shensha('亡者相冲', -20, f'日支与亡者生肖({owner_zodiac})相冲，大凶')
            
            # 亡者生肖与日支相合
            if self._is_owner_he(sizhu, owner_zodiac):
                self._add_shensha('亡者相合', 10, f'日支与亡者生肖({owner_zodiac})相合，吉')
    
    # ===== 重丧类神煞 =====
    
    def _is_zhongsang(self, sizhu):
        """
        是否重丧日（按月查日干）
        口诀：正七连庚甲，二八乙辛当，五十一丁癸，四十丙壬方，三六九十二，戊己是重丧
        即：正月、七月逢庚日、甲日；二月、八月逢乙日、辛日；以此类推
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        # 月份对应的天干映射
        zhongsang_map = {
            '寅': ['庚', '甲'],  # 正月
            '卯': ['乙', '辛'],  # 二月
            '辰': ['戊', '己'],  # 三月
            '巳': ['丙', '壬'],  # 四月
            '午': ['丁', '癸'],  # 五月
            '未': ['戊', '己'],  # 六月
            '申': ['庚', '甲'],  # 七月
            '酉': ['乙', '辛'],  # 八月
            '戌': ['戊', '己'],  # 九月
            '亥': ['丙', '壬'],  # 十月
            '子': ['丁', '癸'],  # 十一月
            '丑': ['戊', '己']   # 十二月
        }
        
        return day_gan in zhongsang_map.get(month_zhi, [])
    
    def _is_nian_zhongsang(self, sizhu):
        """
        是否年重丧（按年支查日干）
        口诀与月重丧类似，但以年支为准
        """
        year_zhi = sizhu['year_zhi']
        day_gan = sizhu['day_gan']
        
        # 年支对应的天干映射（与月重丧相同规律）
        nian_zhongsang_map = {
            '寅': ['庚', '甲'],
            '卯': ['乙', '辛'],
            '辰': ['戊', '己'],
            '巳': ['丙', '壬'],
            '午': ['丁', '癸'],
            '未': ['戊', '己'],
            '申': ['庚', '甲'],
            '酉': ['乙', '辛'],
            '戌': ['戊', '己'],
            '亥': ['丙', '壬'],
            '子': ['丁', '癸'],
            '丑': ['戊', '己']
        }
        
        return day_gan in nian_zhongsang_map.get(year_zhi, [])
    
    def _is_sansang(self, sizhu):
        """
        是否三丧日（按季节查日支）
        口诀：春辰夏未秋戌冬丑
        即：春季（寅卯辰月）逢辰日，夏季（巳午未月）逢未日，秋季（申酉戌月）逢戌日，冬季（亥子丑月）逢丑日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 按季节判断
        if month_zhi in ['寅', '卯', '辰']:  # 春季
            return day_zhi == '辰'
        elif month_zhi in ['巳', '午', '未']:  # 夏季
            return day_zhi == '未'
        elif month_zhi in ['申', '酉', '戌']:  # 秋季
            return day_zhi == '戌'
        elif month_zhi in ['亥', '子', '丑']:  # 冬季
            return day_zhi == '丑'
        return False
    
    def _is_furi(self, sizhu):
        """
        是否复日（重丧类）
        复日：正月甲日、二月乙日、三月丙日……依此类推
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        furi_map = {
            '寅': '甲', '卯': '乙', '辰': '丙',
            '巳': '丁', '午': '戊', '未': '己',
            '申': '庚', '酉': '辛', '戌': '壬',
            '亥': '癸', '子': '甲', '丑': '乙'
        }
        return day_gan == furi_map.get(month_zhi)
    
    # ===== 其他凶煞 =====
    
    def _is_wangwang(self, sizhu):
        """
        是否往亡日
        口诀：正寅二巳三申四亥五卯六午七酉八子九辰十未十一戌十二丑
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        wangwang_map = {
            '寅': '寅', '卯': '巳', '辰': '申', '巳': '亥',
            '午': '卯', '未': '午', '申': '酉', '酉': '子',
            '戌': '辰', '亥': '未', '子': '戌', '丑': '丑'
        }
        return day_zhi == wangwang_map.get(month_zhi)
    
    def _is_tianli(self, sizhu):
        """
        是否天吏日
        口诀：正卯二寅三丑四子五亥六戌七酉八申九未十午十一巳十二辰
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        tianli_map = {
            '寅': '卯', '卯': '寅', '辰': '丑', '巳': '子',
            '午': '亥', '未': '戌', '申': '酉', '酉': '申',
            '戌': '未', '亥': '午', '子': '巳', '丑': '辰'
        }
        return day_zhi == tianli_map.get(month_zhi)
    
    def _is_zhisi(self, sizhu):
        """
        是否致死日
        口诀：正未二申三酉四戌五亥六子七丑八寅九卯十辰十一巳十二午
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        zhisi_map = {
            '寅': '未', '卯': '申', '辰': '酉', '巳': '戌',
            '午': '亥', '未': '子', '申': '丑', '酉': '寅',
            '戌': '卯', '亥': '辰', '子': '巳', '丑': '午'
        }
        return day_zhi == zhisi_map.get(month_zhi)
    
    def _is_yuepo(self, sizhu):
        """是否月破（与月支相冲）"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        yuepo = zh_list[(idx + 6) % 12]
        return day_zhi == yuepo
    
    def _is_tufu(self, sizhu):
        """是否土府日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        tufu_map = {
            '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申',
            '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
        }
        return day_zhi == tufu_map.get(month_zhi)
    
    def _is_bazuori(self, sizhu):
        """是否八座日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        bazuori_map = {
            '寅': '未', '卯': '申', '辰': '酉', '巳': '戌',
            '午': '亥', '未': '子', '申': '丑', '酉': '寅',
            '戌': '卯', '亥': '辰', '子': '巳', '丑': '午'
        }
        return day_zhi == bazuori_map.get(month_zhi)
    
    # ===== 极凶日 =====
    
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
    
    def _is_shie_dabai(self, sizhu):
        """是否十恶大败日"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi
        shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
        return day_pillar in shie_dabai
    
    def _is_fuduan(self, sizhu):
        """是否伏断日"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        fuduan_map = {
            '甲': '戌', '乙': '酉', '丙': '申', '丁': '未', '戊': '午',
            '己': '巳', '庚': '辰', '辛': '卯', '壬': '寅', '癸': '丑'
        }
        return day_zhi == fuduan_map.get(day_gan)
    
    # ===== 吉日 =====
    
    def _is_mingfei(self, sizhu):
        """
        是否鸣吠日（正确的天干地支组合）
        鸣吠日：庚午、庚子、庚申、辛酉、辛卯、辛巳、壬寅、壬辰、壬午、壬申
        """
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi
        mingfei = ['庚午', '庚子', '庚申', '辛酉', '辛卯', '辛巳', '壬寅', '壬辰', '壬午', '壬申']
        return day_pillar in mingfei
    
    def _is_mingfeidui(self, sizhu):
        """
        是否鸣吠对日
        鸣吠对日：丙子、丙午、丙寅、丁卯、丁酉、丁亥
        """
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi
        mingfeidui = ['丙子', '丙午', '丙寅', '丁卯', '丁酉', '丁亥']
        return day_pillar in mingfeidui
    
    def _is_bujiang(self, sizhu):
        """是否不将日"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        
        yang_month = ['寅', '辰', '午', '申', '戌', '子']
        yin_month = ['卯', '巳', '未', '酉', '亥', '丑']
        yang_gan = ['甲', '丙', '戊', '庚', '壬']
        yin_gan = ['乙', '丁', '己', '辛', '癸']
        yang_zhi = ['子', '寅', '辰', '午', '申', '戌']
        yin_zhi = ['丑', '卯', '巳', '未', '酉', '亥']
        
        if month_zhi in yang_month:
            return day_gan in yin_gan and day_zhi in yin_zhi
        else:
            return day_gan in yang_gan and day_zhi in yang_zhi
    
    # ===== 亡者相关检查 =====
    
    def _is_dihu(self, sizhu, owner_zodiac):
        """
        是否的呼日（与亡者生肖相冲）
        的呼日：日支与亡者生肖相冲
        """
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        
        if owner_zodiac not in zh_list:
            return False
        
        idx = zh_list.index(owner_zodiac)
        chong = zh_list[(idx + 6) % 12]
        return day_zhi == chong
    
    def _is_renhu(self, sizhu, owner_zodiac):
        """
        是否人呼日（与孝子生肖相冲，简化处理为与亡者生肖相关）
        实际应根据孝子生肖判断，这里简化处理
        """
        # 简化：与亡者生肖相害的日子
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        
        if owner_zodiac not in zh_list:
            return False
        
        # 六害关系
        hai_map = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        
        return day_zhi == hai_map.get(owner_zodiac)
    
    def _is_owner_chong(self, sizhu, owner_zodiac):
        """日支与亡者生肖是否相冲"""
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        
        if owner_zodiac not in zh_list:
            return False
        
        idx = zh_list.index(owner_zodiac)
        chong = zh_list[(idx + 6) % 12]
        return day_zhi == chong
    
    def _is_owner_he(self, sizhu, owner_zodiac):
        """日支与亡者生肖是否相合"""
        day_zhi = sizhu['day_zhi']
        
        # 六合关系
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        return day_zhi == liuhe_map.get(owner_zodiac)
