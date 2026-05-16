import sys
import os

if __name__ == '__main__' and __package__ is None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# -*- coding: utf-8 -*-
"""
================================================================================
嫁娶规则模块（基于《协纪辨方书》）
================================================================================
实现婚嫁择日的宜忌规则

核心规则：
1. 大利月/小利月：新娘年支与农历月份关系
2. 禁婚年/本命年：年神系统
3. 天德/月德/不将日：日神系统
4. 三娘煞/杨公忌/红纱日：凶神系统
5. 建除十二神：除、定、执、成、开为吉
6. 月破/岁破/四离四绝：否决项
7. 夫星/子星/阴胎/阳气：命理系统
================================================================================
"""

from .规则基类 import EventRuleChecker
from datetime import date, datetime

class MarriageRuleChecker(EventRuleChecker):
    """嫁娶规则检查器"""
    
    ZHI_TO_ZODIAC = {
        '子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔',
        '辰': '龙', '巳': '蛇', '午': '马', '未': '羊',
        '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'
    }
    
    ZODIAC_TO_ZHI = {v: k for k, v in ZHI_TO_ZODIAC.items()}
    
    TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 大利月表（新娘生肖：农历月份）
    DALIYUE = {
        '鼠': [6, 12], '牛': [5, 11], '虎': [2, 8], '兔': [1, 7],
        '龙': [4, 10], '蛇': [3, 9], '马': [6, 12], '羊': [5, 11],
        '猴': [2, 8], '鸡': [1, 7], '狗': [4, 10], '猪': [3, 9]
    }
    
    # 小利月表
    XIAOLIYUE = {
        '鼠': [3, 10], '牛': [2, 9], '虎': [5, 11], '兔': [4, 10],
        '龙': [1, 7], '蛇': [6, 12], '马': [3, 9], '羊': [2, 8],
        '猴': [5, 11], '鸡': [4, 10], '狗': [1, 7], '猪': [6, 12]
    }
    
    # 破月表（妨翁姑月）
    POYUE = {
        '鼠': [11], '牛': [10], '虎': [5, 8], '兔': [1, 7],
        '龙': [1, 7], '蛇': [8, 11], '马': [1, 5], '羊': [1, 6],
        '猴': [5, 8], '鸡': [5, 8], '狗': [6, 9], '猪': [6, 9]
    }
    
    # 禁婚年（男命）
    JINHUN_NAN = {
        '子': '兔', '丑': '虎', '寅': '牛', '卯': '鼠',
        '辰': '猪', '巳': '狗', '午': '鸡', '未': '猴',
        '申': '羊', '酉': '马', '戌': '蛇', '亥': '龙'
    }
    
    # 禁婚年（女命）
    JINHUN_NV = {
        '子': '鸡', '丑': '猴', '寅': '羊', '卯': '马',
        '辰': '蛇', '巳': '龙', '午': '兔', '未': '虎',
        '申': '牛', '酉': '鼠', '戌': '猪', '亥': '狗'
    }
    
    # 三娘煞日（农历）
    SANNIAGSHA = [3, 7, 13, 18, 22, 27]
    
    # 杨公忌日（农历）
    YANGGONGJI = {
        1: [13], 2: [11], 3: [9], 4: [7], 5: [5], 6: [3],
        7: [1, 29], 8: [27], 9: [25], 10: [23], 11: [21], 12: [19]
    }
    
    # 红纱日
    HONGSHA = {
        1: ['巳'], 4: ['巳'], 7: ['巳'], 10: ['巳'],
        2: ['酉'], 5: ['酉'], 8: ['酉'], 11: ['酉'],
        3: ['丑'], 6: ['丑'], 9: ['丑'], 12: ['丑']
    }
    
    # 黄沙日
    HUANGSHA = {
        1: ['午'], 4: ['午'], 7: ['午'], 10: ['午'],
        2: ['寅'], 5: ['寅'], 8: ['寅'], 11: ['寅'],
        3: ['子'], 6: ['子'], 9: ['子'], 12: ['子']
    }
    
    # 真三娘煞日（特定干支）
    ZHEN_SANNIANGSHA = {
        3: ['庚午'],     # 初三庚午
        7: ['辛未'],     # 初七辛未
        13: ['戊申'],    # 十三戊申
        18: ['己酉'],    # 十八己酉
        22: ['丙午'],    # 廿二丙午
        27: ['丁未']     # 廿七丁未
    }
    
    # 女命忌嫁日（当梁勾绞）：生肖 -> 忌日支
    NV_MING_JI_JIA = {
        '子': ['卯', '酉'],    # 子相忌卯酉二日
        '丑': ['辰', '戌'],    # 丑相忌辰戌二日
        '寅': ['巳', '亥'],    # 寅相忌巳亥二日
        '卯': ['子', '午'],    # 卯相忌子午二日
        '辰': ['丑', '未'],    # 辰相忌丑未二日
        '巳': ['寅', '申'],    # 巳相忌寅申二日
        '午': ['卯', '酉'],    # 午相忌卯酉二日
        '未': ['辰', '戌'],    # 未相忌辰戌二日
        '申': ['亥', '巳'],    # 申相忌亥巳二日
        '酉': ['子', '午'],    # 酉相忌子午二日
        '戌': ['丑', '未'],    # 戌相忌丑未二日
        '亥': ['寅', '申']     # 亥相忌寅申二日
    }
    
    # 神号日：月 -> 日支
    SHENHAO = {
        1: ['戌'], 2: ['亥'], 3: ['子'], 4: ['丑'],
        5: ['寅'], 6: ['卯'], 7: ['辰'], 8: ['巳'],
        9: ['午'], 10: ['未'], 11: ['申'], 12: ['酉']
    }
    
    # 鬼哭日：月 -> 日支
    GUIRU = {
        1: ['未'], 2: ['戌'], 3: ['辰'], 4: ['寅'],
        5: ['午'], 6: ['子'], 7: ['酉'], 8: ['申'],
        9: ['巳'], 10: ['亥'], 11: ['丑'], 12: ['卯']
    }
    
    # 天德/月德（根据月支）
    # 天德：正丁二坤三壬四辛五亥六甲七癸八艮九丙十乙十一巳十二庚
    TIANDE_YUDE = {
        '寅': {'天德': '丁', '月德': '丙'},
        '卯': {'天德': '坤', '月德': '甲'},
        '辰': {'天德': '壬', '月德': '壬'},
        '巳': {'天德': '辛', '月德': '丙'},
        '午': {'天德': '亥', '月德': '丙'},
        '未': {'天德': '甲', '月德': '甲'},
        '申': {'天德': '癸', '月德': '庚'},
        '酉': {'天德': '艮', '月德': '庚'},
        '戌': {'天德': '丙', '月德': '壬'},
        '亥': {'天德': '乙', '月德': '甲'},
        '子': {'天德': '巳', '月德': '庚'},
        '丑': {'天德': '庚', '月德': '辛'}
    }
    
    # 建除十二神吉凶（用于嫁娶）
    # 黄道：除、危、定、成、开（吉）
    # 黑道：建、满、平、收、闭、破（凶）
    # 执日：宜修造动土，忌嫁娶（修造吉，嫁娶凶）
    JIANCHU_YI = ['除', '危', '定', '成', '开']
    JIANCHU_JI = ['建', '满', '平', '收', '闭', '破', '执']
    
    # 阴阳差错日
    YINYANG_CHACUO = [
        '丙子', '丁丑', '戊寅', '辛卯', '壬辰', '癸巳',
        '丙午', '丁未', '戊申', '辛酉', '壬戌', '癸亥'
    ]
    
    # 六冲（天干相冲）
    GAN_CHONG = [('甲', '庚'), ('乙', '辛'), ('丙', '壬'), ('丁', '癸')]
    
    def __init__(self):
        super().__init__()
        self._init_dependencies()
    
    def _init_dependencies(self):
        """初始化依赖模块"""
        self.has_marriage_shensha = False
        self.get_jianchu = None
        self.is_tiande_day = None
        self.is_yuede_day = None
        self.is_bujiang_day = None
        self.is_month_break = None
        self.is_year_break = None
        self.is_sili_sijue = None
        
        try:
            from ..shensha.marriage_shensha import (
                get_jianchu, is_tiande_day, is_yuede_day,
                is_bujiang_day, is_month_break, is_year_break, is_sili_sijue
            )
            self.get_jianchu = get_jianchu
            self.is_tiande_day = is_tiande_day
            self.is_yuede_day = is_yuede_day
            self.is_bujiang_day = is_bujiang_day
            self.is_month_break = is_month_break
            self.is_year_break = is_year_break
            self.is_sili_sijue = is_sili_sijue
            self.has_marriage_shensha = True
        except ImportError:
            pass
    
    def _is_male(self, owner):
        """判断是否为男性"""
        name = owner.get('name', '')
        role = owner.get('role', '')
        gender = owner.get('性别', '')
        return '新郎' in name or '男' in name or '男' in role or gender == '男'
    
    def _is_female(self, owner):
        """判断是否为女性"""
        name = owner.get('name', '')
        role = owner.get('role', '')
        gender = owner.get('性别', '')
        return '新娘' in name or '女' in name or '女' in role or gender == '女'
    
    def _sizhu_to_date(self, sizhu):
        """从sizhu构建日期对象"""
        if 'date' in sizhu:
            return sizhu['date']
        
        try:
            year = int(sizhu.get('year', sizhu.get('年柱', '2000')[0:4]))
            month = int(sizhu.get('month', 1))
            day = int(sizhu.get('day', 1))
            return date(year, month, day)
        except:
            return None
    
    def _get_lunar_info(self, date_obj):
        """获取农历信息"""
        try:
            from ..四柱计算器 import get_lunar_date
            lunar_info = get_lunar_date(date_obj)
            
            # 解析农历月份为数字
            month_map = {
                '正月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
                '七月': 7, '八月': 8, '九月': 9, '十月': 10, '冬月': 11, '腊月': 12
            }
            lunar_month_str = lunar_info.get('month', '')
            lunar_month_num = month_map.get(lunar_month_str, date_obj.month)
            
            # 解析农历日期为数字
            day_map = {
                '初一': 1, '初二': 2, '初三': 3, '初四': 4, '初五': 5,
                '初六': 6, '初七': 7, '初八': 8, '初九': 9, '初十': 10,
                '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
                '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
                '廿一': 21, '廿二': 22, '廿三': 23, '廿四': 24, '廿五': 25,
                '廿六': 26, '廿七': 27, '廿八': 28, '廿九': 29, '三十': 30
            }
            lunar_day_str = lunar_info.get('day', '')
            lunar_day_num = day_map.get(lunar_day_str, date_obj.day)
            
            # 添加数字字段
            lunar_info['month_num'] = lunar_month_num
            lunar_info['lunar_day'] = lunar_day_num
            
            return lunar_info
        except:
            return {'month_num': date_obj.month, 'lunar_day': date_obj.day}
    
    def _get_owner_zodiac(self, owner):
        """获取事主生肖"""
        zodiac = owner.get('生肖', '')
        if zodiac:
            return zodiac
        
        zodiac = owner.get('zodiac', '')
        if zodiac:
            return zodiac
        
        if 'birth_date' in owner:
            try:
                from ..四柱计算器 import calculate_sizhu
                birth_sizhu = calculate_sizhu(
                    owner['birth_date'],
                    owner.get('birth_hour', 12),
                    owner.get('birth_minute', 0)
                )
                return birth_sizhu['年柱'][1]
            except:
                pass
        
        return None
    
    def _get_owner_year_zhi(self, owner):
        """获取事主年支（地支）"""
        # 地支对应生肖
        zodiac_to_zhi = {
            '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
            '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
            '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
        }
        
        # 先尝试从生肖获取
        zodiac = owner.get('生肖', '')
        if zodiac:
            return zodiac_to_zhi.get(zodiac, '')
        
        # 从birth_date计算
        if 'birth_date' in owner:
            try:
                from ..四柱计算器 import calculate_sizhu
                birth_sizhu = calculate_sizhu(
                    owner['birth_date'],
                    owner.get('birth_hour', 12),
                    owner.get('birth_minute', 0)
                )
                return birth_sizhu['年柱'][1]
            except:
                pass
        
        # 从birth_year计算
        if 'birth_year' in owner:
            try:
                from ..四柱计算器 import calculate_sizhu
                birth_sizhu = calculate_sizhu(
                    owner['birth_year'],
                    owner.get('birth_month', 1),
                    owner.get('birth_day', 1),
                    owner.get('birth_hour', 12),
                    owner.get('birth_minute', 0)
                )
                return birth_sizhu['年柱'][1]
            except:
                pass
        
        return ''
    
    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查婚嫁规则"""
        yi_list = []
        ji_list = []
        
        # 如果是四柱输入模式，跳过日期相关的检查
        if sizhu.get('is_sizhu_input', False):
            # 对于四柱输入，只进行基本的四柱分析
            day_gan = sizhu.get('day_gan', '')
            day_zhi = sizhu.get('day_zhi', '')
            
            # 基本的宜事项
            yi_list.append('嫁娶')
            
            return yi_list, ji_list
        
        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list
        
        lunar_info = self._get_lunar_info(date_obj)
        lunar_month = lunar_info.get('month_num', date_obj.month)
        lunar_day = lunar_info.get('lunar_day', date_obj.day)
        
        # 1. 检查年神
        self._check_year_gods(sizhu, owners, yi_list, ji_list)
        
        # 2. 检查月神（利月/破月）
        self._check_month_gods(sizhu, owners, lunar_month, yi_list, ji_list)
        
        # 3. 检查日神
        self._check_day_gods(sizhu, date_obj, lunar_month, lunar_day, owners, yi_list, ji_list)
        
        # 4. 检查凶神
        self._check_bad_gods(lunar_month, lunar_day, sizhu, owners, yi_list, ji_list)
        
        # 5. 检查事主相冲（新增）
        self._check_shengxiao_chong(sizhu, owners, ji_list)
        
        # 6. 综合判断
        if not ji_list:
            yi_list.append('嫁娶')
        else:
            ji_list.append('嫁娶')
        
        return yi_list, ji_list
    
    def _check_year_gods(self, sizhu, owners, yi_list, ji_list):
        """检查年神"""
        year_zhi = sizhu.get('year_zhi', '')
        if not year_zhi or len(year_zhi) < 1:
            return
        
        year_zodiac = self.ZHI_TO_ZODIAC.get(year_zhi, '')
        
        if not owners:
            return
        
        for owner in owners:
            name = owner.get('name', '事主')
            zodiac = self._get_owner_zodiac(owner)
            
            if not zodiac:
                continue
            
            if self._is_male(owner):
                if self.JINHUN_NAN.get(year_zhi) == zodiac:
                    ji_list.append(f'{name}禁婚年')
            
            if self._is_female(owner):
                if self.JINHUN_NV.get(year_zhi) == zodiac:
                    ji_list.append(f'{name}禁婚年')
            
            if year_zodiac == zodiac:
                ji_list.append(f'{name}本命年（值太岁）')
    
    def _check_month_gods(self, sizhu, owners, lunar_month, yi_list, ji_list):
        """检查月神（利月/破月）"""
        if not owners or not lunar_month:
            return
        
        for owner in owners:
            name = owner.get('name', '事主')
            zodiac = self._get_owner_zodiac(owner)
            
            if not zodiac or not self._is_female(owner):
                continue
            
            if lunar_month in self.DALIYUE.get(zodiac, []):
                yi_list.append(f'新娘大利月')
            elif lunar_month in self.XIAOLIYUE.get(zodiac, []):
                yi_list.append(f'新娘小利月')
            elif lunar_month in self.POYUE.get(zodiac, []):
                ji_list.append(f'新娘破月（妨翁姑月）')
    
    def _check_day_gods(self, sizhu, date_obj, lunar_month, lunar_day, owners, yi_list, ji_list):
        """检查日神（吉神）"""
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        
        if not date_obj:
            return
        
        # 建除十二神
        if self.get_jianchu:
            try:
                jianchu = self.get_jianchu(date_obj)
                if jianchu in self.JIANCHU_YI:
                    yi_list.append(f'建除{jianchu}日')
                elif jianchu in self.JIANCHU_JI:
                    ji_list.append(f'建除{jianchu}日')
            except:
                pass
        
        # 天德/月德
        if self.has_marriage_shensha:
            try:
                if self.is_tiande_day(date_obj):
                    yi_list.append('天德日')
                if self.is_yuede_day(date_obj):
                    yi_list.append('月德日')
            except:
                pass
        
        # 不将日
        if self.has_marriage_shensha:
            try:
                if self.is_bujiang_day(date_obj):
                    yi_list.append('不将日')
            except:
                pass
        
        # 三合/六合（与事主）
        if owners and day_zhi:
            for owner in owners:
                zodiac = self._get_owner_zodiac(owner)
                if not zodiac:
                    continue
                owner_zhi = self.ZODIAC_TO_ZHI.get(zodiac, '')
                if not owner_zhi:
                    continue
                
                # 六合
                liuhe_pairs = [('子','丑'), ('寅','亥'), ('卯','戌'), ('辰','酉'), ('巳','申'), ('午','未')]
                if (day_zhi, owner_zhi) in liuhe_pairs or (owner_zhi, day_zhi) in liuhe_pairs:
                    yi_list.append('与事主六合')
                    break
        
        # 天德月德表（备用）
        if month_zhi in self.TIANDE_YUDE:
            gods = self.TIANDE_YUDE[month_zhi]
            if day_gan == gods.get('天德') and '天德日' not in yi_list:
                yi_list.append('天德')
            if day_gan == gods.get('月德') and '月德日' not in yi_list:
                yi_list.append('月德')
    
    def _check_bad_gods(self, lunar_month, lunar_day, sizhu, owners, yi_list, ji_list):
        """检查凶神"""
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        year_zhi = sizhu.get('year_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        
        date_obj = self._sizhu_to_date(sizhu)
        
        # 月破/岁破
        if self.has_marriage_shensha and date_obj:
            try:
                if self.is_month_break(date_obj):
                    ji_list.append('月破日')
                if self.is_year_break(date_obj, year_zhi):
                    ji_list.append('岁破日')
                if self.is_sili_sijue(date_obj):
                    ji_list.append('四离四绝日')
            except:
                pass
        
        # 三娘煞
        if lunar_day in self.SANNIAGSHA:
            ji_list.append(f'三娘煞（{lunar_day}日）')
        
        # 杨公忌
        if lunar_month in self.YANGGONGJI:
            if lunar_day in self.YANGGONGJI[lunar_month]:
                ji_list.append(f'杨公忌')
        
        # 红纱日
        if lunar_month in self.HONGSHA:
            if day_zhi in self.HONGSHA[lunar_month]:
                ji_list.append(f'红纱日')
        
        # 黄沙日
        if lunar_month in self.HUANGSHA:
            if day_zhi in self.HUANGSHA[lunar_month]:
                ji_list.append(f'黄沙日')
        
        # 真三娘煞（特定干支）
        if lunar_day in self.ZHEN_SANNIANGSHA:
            ganzhi = day_gan + day_zhi
            if ganzhi in self.ZHEN_SANNIANGSHA[lunar_day]:
                ji_list.append(f'真三娘煞（{ganzhi}）')
        
        # 女命忌嫁日（当梁勾绞）
        if owners and day_zhi:
            for owner in owners:
                zodiac = self._get_owner_zodiac(owner)
                if zodiac and self._is_female(owner):
                    if zodiac in self.NV_MING_JI_JIA:
                        if day_zhi in self.NV_MING_JI_JIA[zodiac]:
                            ji_list.append(f'女命忌嫁日（{zodiac}相忌{day_zhi}日）')
        
        # 神号日
        if lunar_month in self.SHENHAO:
            if day_zhi in self.SHENHAO[lunar_month]:
                ji_list.append(f'神号日')
        
        # 鬼哭日
        if lunar_month in self.GUIRU:
            if day_zhi in self.GUIRU[lunar_month]:
                ji_list.append(f'鬼哭日')
        
        # 阴阳差错日
        ganzhi = day_gan + day_zhi
        if ganzhi in self.YINYANG_CHACUO:
            ji_list.append('阴阳差错日')
        
        # 夫星/子星（冲克）
        if owners:
            for owner in owners:
                if self._is_female(owner):
                    bride_bazi = owner.get('bazi', {})
                    bride_ri_gan = bride_bazi.get('ri_gan', bride_bazi.get('day_gan', ''))
                    
                    if not bride_ri_gan:
                        continue
                    
                    # 夫星（正官）
                    fuxing_map = {
                        '甲': '辛', '乙': '庚', '丙': '癸', '丁': '壬',
                        '戊': '乙', '己': '甲', '庚': '丁', '辛': '丙',
                        '壬': '己', '癸': '戊'
                    }
                    fuxing = fuxing_map.get(bride_ri_gan, '')
                    if fuxing:
                        # 冲夫星：天干相冲
                        if (day_gan, fuxing) in self.GAN_CHONG or (fuxing, day_gan) in self.GAN_CHONG:
                            ji_list.append('冲夫星')
                    
                    # 子星（食神）
                    zixing_map = {
                        '甲': '丙', '乙': '丁', '丙': '戊', '丁': '己',
                        '戊': '庚', '己': '辛', '庚': '壬', '辛': '癸',
                        '壬': '甲', '癸': '乙'
                    }
                    zixing = zixing_map.get(bride_ri_gan, '')
                    if zixing:
                        if (day_gan, zixing) in self.GAN_CHONG or (zixing, day_gan) in self.GAN_CHONG:
                            ji_list.append('冲子星')
                    
                    # 阴胎：日柱天干后两位，地支后三位
                    gan_idx = self.TIANGAN.index(bride_ri_gan) if bride_ri_gan in self.TIANGAN else 0
                    zhi_idx = self.DIZHI.index(sizhu.get('day_zhi', '子')) if sizhu.get('day_zhi', '子') in self.DIZHI else 0
                    
                    yintai_gan = self.TIANGAN[(gan_idx + 2) % 10]
                    yintai_zhi = self.DIZHI[(zhi_idx + 3) % 12]
                    
                    # 阳气：日柱天干后一位，地支后一位
                    yangqi_gan = self.TIANGAN[(gan_idx + 1) % 10]
                    yangqi_zhi = self.DIZHI[(zhi_idx + 1) % 12]
                    
                    if day_gan == yintai_gan and day_zhi == yintai_zhi:
                        ji_list.append('犯阴胎')
                    if day_gan == yangqi_gan and day_zhi == yangqi_zhi:
                        ji_list.append('犯阳气')
    
    def _check_shengxiao_chong(self, sizhu, owners, ji_list):
        """
        检查四柱与事主生肖相冲（嫁娶专用）
        传统择日：日 > 年 > 月 > 时；女方被日柱冲为大忌
        
        参数:
            sizhu: 四柱字典
            owners: 事主列表（男女双方）
            ji_list: 忌项列表，会被修改
        """
        if not owners:
            return
        
        # 获取四柱地支
        year_zhi = sizhu.get('year_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        hour_zhi = sizhu.get('hour_zhi', '')
        
        if not day_zhi:
            return
        
        # 地支六冲表（键值都是地支）
        chong_map = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
        
        # 检查每个事主
        for owner in owners:
            name = owner.get('name', '事主')
            
            # 获取事主年支（地支）
            owner_zhi = self._get_owner_year_zhi(owner)
            
            if not owner_zhi:
                continue
            
            # 判断是否为女方（新娘）
            is_bride = self._is_female(owner)
            target_chong_zhi = chong_map.get(owner_zhi, '')
            
            if not target_chong_zhi:
                continue
            
            # 检查日柱（对女方最重要）
            if day_zhi == target_chong_zhi:
                if is_bride:
                    ji_list.append(f'日柱{day_zhi}冲新娘{name}')
                else:
                    ji_list.append(f'日柱{day_zhi}冲{name}')
            
            # 检查年柱
            if year_zhi == target_chong_zhi:
                ji_list.append(f'年柱{year_zhi}冲{name}')
            
            # 检查月柱
            if month_zhi == target_chong_zhi:
                ji_list.append(f'月柱{month_zhi}冲{name}')
            
            # 检查时柱
            if hour_zhi == target_chong_zhi:
                ji_list.append(f'时柱{hour_zhi}冲{name}')

# 测试
if __name__ == '__main__':
    checker = MarriageRuleChecker()
    
    test_sizhu = {
        'day_gan': '丙',
        'day_zhi': '寅',
        'month_zhi': '寅',
        'year_zhi': '子',
        'month': 2,
        'day': 10,
        'year': 2024
    }
    
    test_owners = [
        {'name': '新娘张三', '性别': '女', '生肖': '兔', 'bazi': {'ri_gan': '庚', 'ri_zhi': '午'}},
        {'name': '新郎李四', '性别': '男', '生肖': '马'}
    ]
    
    # 使用新接口测试
    yi_list, ji_list = checker._check_rules(test_sizhu, test_owners)
    
    print("宜：", yi_list)
    print("忌：", ji_list)
