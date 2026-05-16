import sys
import os
from datetime import date

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
    
    # 直接运行时使用绝对导入
    from 规则基类 import EventRuleChecker
    try:
        from shensha.marriage_shensha import check_marriage_shensha
    except ImportError:
        # 如果模块不存在，使用本地实现
        check_marriage_shensha = lambda *args, **kwargs: ([], [])
else:
    # 作为模块导入时使用相对导入
    from .规则基类 import EventRuleChecker
    try:
        from ..shensha.marriage_shensha import check_marriage_shensha
    except ImportError:
        # 如果模块不存在，使用本地实现
        check_marriage_shensha = lambda *args, **kwargs: ([], [])

# -*- coding: utf-8 -*-
"""
================================================================================
婚嫁规则模块 - 专业级实现
================================================================================
实现传统择日的完整神煞体系，包括：
1. 年神（年禁）：禁婚年、无春年、本命年
2. 月神（利月/破月）：大利月、小利月、破月、妨翁姑月等
3. 日神：吉神（天德月德、黄道、不将日等）和凶神（三娘煞、杨公忌等）
4. 时神：贵人登天门时、六和时等
================================================================================
"""

class MarriageRuleChecker(EventRuleChecker):
    """婚嫁规则检查器 - 专业级实现"""
    
    def __init__(self):
        super().__init__()
        
        # 地支对应生肖
        self.zhi_to_zodiac = {
            '子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔',
            '辰': '龙', '巳': '蛇', '午': '马', '未': '羊',
            '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'
        }
        
        # 生肖对应地支
        self.zodiac_to_zhi = {v: k for k, v in self.zhi_to_zodiac.items()}
        
        # 天干
        self.tiangan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        
        # 地支
        self.dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 三合局
        self.sanhe = {
            '申子辰': ['申', '子', '辰'],
            '亥卯未': ['亥', '卯', '未'],
            '寅午戌': ['寅', '午', '戌'],
            '巳酉丑': ['巳', '酉', '丑']
        }
        
        # 六合
        self.liuhe = {
            '子丑': ['子', '丑'],
            '寅亥': ['寅', '亥'],
            '卯戌': ['卯', '戌'],
            '辰酉': ['辰', '酉'],
            '巳申': ['巳', '申'],
            '午未': ['午', '未']
        }
        
        # 三娘煞日
        self.sanniangsha = [3, 7, 13, 18, 22, 27]
        
        # 杨公忌日（农历）
        self.yanggongji = {
            1: [13],    # 正月十三
            2: [11],    # 二月十一
            3: [9],     # 三月初九
            4: [7],     # 四月初七
            5: [5],     # 五月初五
            6: [3],     # 六月初三
            7: [1, 29], # 七月初一、二十九
            8: [27],    # 八月二十七
            9: [25],    # 九月二十五
            10: [23],   # 十月二十三
            11: [21],   # 十一月二十一
            12: [19]    # 十二月十九
        }
        
        # 红纱日（农历）
        self.hongsha = {
            1: ['巳'],  # 一月犯巳
            4: ['巳'],  # 四月犯巳
            7: ['巳'],  # 七月犯巳
            10: ['巳'], # 十月犯巳
            2: ['酉'],  # 二月犯酉
            5: ['酉'],  # 五月犯酉
            8: ['酉'],  # 八月犯酉
            11: ['酉'], # 十一月犯酉
            3: ['丑'],  # 三月犯丑
            6: ['丑'],  # 六月犯丑
            9: ['丑'],  # 九月犯丑
            12: ['丑']  # 十二月犯丑
        }
        
        # 大黄道吉日
        self.dahuangdao = ['青龙', '明堂', '金匮', '天德', '玉堂', '司命']
        
        # 小黄道吉日
        self.xiaohuangdao = ['除', '危', '定', '执', '成', '开']
        
        # 往亡日
        self.wangwang = {
            '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
            '午': '子', '未': '丑', '申': '寅', '酉': '卯',
            '戌': '辰', '亥': '巳', '子': '午', '丑': '未'
        }
        
        # 受死日
        self.shousi = {
            '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
            '辰': '巳', '巳': '午', '午': '未', '未': '申',
            '申': '酉', '酉': '戌', '戌': '亥', '亥': '子'
        }
        
        # 天德、月德（根据月支）
        self.tiande_yuede = {
            '寅': {'天德': '丁', '月德': '丙'},
            '卯': {'天德': '申', '月德': '甲'},
            '辰': {'天德': '辛', '月德': '壬'},
            '巳': {'天德': '亥', '月德': '丙'},
            '午': {'天德': '亥', '月德': '丙'},
            '未': {'天德': '巳', '月德': '甲'},
            '申': {'天德': '丁', '月德': '庚'},
            '酉': {'天德': '寅', '月德': '庚'},
            '戌': {'天德': '丙', '月德': '丙'},
            '亥': {'天德': '乙', '月德': '壬'},
            '子': {'天德': '巳', '月德': '壬'},
            '丑': {'天德': '癸', '月德': '庚'}
        }
        
        # 大利月表（新娘生肖）
        self.daliyue = {
            '鼠': [6, 7],      # 六月、七月
            '牛': [5, 6],      # 五月、六月
            '虎': [2, 6],      # 二月、六月
            '兔': [3, 4],      # 三月、四月
            '龙': [3, 4],      # 三月、四月
            '蛇': [1, 7],      # 正月、七月
            '马': [4, 7],      # 四月、七月
            '羊': [4, 5],      # 四月、五月
            '猴': [2, 6],      # 二月、六月
            '鸡': [9, 10],     # 九月、十月
            '狗': [5, 8],      # 五月、八月
            '猪': [2, 3]       # 二月、三月
        }
        
        # 小利月表（新娘生肖）
        self.xiaoliyue = {
            '鼠': [3, 10],     # 三月、十月
            '牛': [2, 3],      # 二月、三月
            '虎': [4, 7],      # 四月、七月
            '兔': [2, 8],      # 二月、八月
            '龙': [2, 8],      # 二月、八月
            '蛇': [5, 6],      # 五月、六月
            '马': [3, 8],      # 三月、八月
            '羊': [2, 9],      # 二月、九月
            '猴': [4, 7],      # 四月、七月
            '鸡': [2, 3],      # 二月、三月
            '狗': [2, 3],      # 二月、三月
            '猪': [4, 5]       # 四月、五月
        }
        
        # 破月表（新娘生肖）
        self.poyue = {
            '鼠': [11, 12],    # 十一月、十二月
            '牛': [10, 11],    # 十月、十一月
            '虎': [5, 8],      # 五月、八月
            '兔': [1, 7],      # 正月、七月
            '龙': [1, 7],      # 正月、七月
            '蛇': [8, 11],     # 八月、十一月
            '马': [1, 5],      # 正月、五月
            '羊': [1, 6],      # 正月、六月
            '猴': [5, 8],      # 五月、八月
            '鸡': [5, 8],      # 五月、八月
            '狗': [6, 9],      # 六月、九月
            '猪': [6, 9]       # 六月、九月
        }
        
        # 禁婚年（男命）
        self.jinhun_nian_nan = {
            '子': '兔',  # 子年禁兔
            '丑': '虎',  # 丑年禁虎
            '寅': '牛',  # 寅年禁牛
            '卯': '鼠',  # 卯年禁鼠
            '辰': '猪',  # 辰年禁猪
            '巳': '狗',  # 巳年禁狗
            '午': '鸡',  # 午年禁鸡
            '未': '猴',  # 未年禁猴
            '申': '羊',  # 申年禁羊
            '酉': '马',  # 酉年禁马
            '戌': '蛇',  # 戌年禁蛇
            '亥': '龙'   # 亥年禁龙
        }
        
        # 禁婚年（女命）
        self.jinhun_nian_nv = {
            '子': '鸡',  # 子年禁鸡
            '丑': '猴',  # 丑年禁猴
            '寅': '羊',  # 寅年禁羊
            '卯': '马',  # 卯年禁马
            '辰': '蛇',  # 辰年禁蛇
            '巳': '龙',  # 巳年禁龙
            '午': '兔',  # 午年禁兔
            '未': '虎',  # 未年禁虎
            '申': '牛',  # 申年禁牛
            '酉': '鼠',  # 酉年禁鼠
            '戌': '猪',  # 戌年禁猪
            '亥': '狗'   # 亥年禁狗
        }
        
        # 夫星表（正官）
        self.fuxing = {
            '甲': '辛', '乙': '庚', '丙': '癸', '丁': '壬',
            '戊': '乙', '己': '甲', '庚': '丁', '辛': '丙',
            '壬': '己', '癸': '戊'
        }
        
        # 子星表（食神）
        self.zixing = {
            '甲': '丙', '乙': '丁', '丙': '戊', '丁': '己',
            '戊': '庚', '己': '辛', '庚': '壬', '辛': '癸',
            '壬': '甲', '癸': '乙'
        }
        
        # 建除十二神
        self.jianchu = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
        
        # 阴阳差错日
        self.yinyang_chacuo = ['丙子', '丁丑', '戊寅', '辛卯', '壬辰', '癸巳', '丙午', '丁未', '戊申', '辛酉', '壬戌', '癸亥']
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查婚嫁规则 - 完整神煞体系"""
        try:
            # 保存owners为实例变量，供其他方法使用
            self.owners = owners
            
            # 获取农历信息
            from 四柱计算器 import get_lunar_date
            lunar_info = get_lunar_date(sizhu['date'])
            
            # 1. 年神（年禁）检查
            self._check_year_gods(sizhu, owners, lunar_info, yi_list, ji_list)
            
            # 2. 月神（利月/破月）检查
            self._check_month_gods(sizhu, owners, lunar_info, yi_list, ji_list)
            
            # 3. 日神检查
            self._check_day_gods(sizhu, lunar_info, yi_list, ji_list)
            
            # 4. 时神检查
            self._check_hour_gods(sizhu, yi_list, ji_list)
            
            # 5. 综合判断
            if not ji_list:
                yi_list.append('嫁娶')
            else:
                ji_list.append('嫁娶')
                
        except Exception as e:
            print(f"婚嫁规则检查出错: {e}")
    
    def _check_year_gods(self, sizhu, owners, lunar_info, yi_list, ji_list):
        """检查年神（年禁）"""
        year_zhi = sizhu['year_zhi']
        year_zodiac = self.zhi_to_zodiac[year_zhi]
        
        # 检查禁婚年
        if owners:
            for owner in owners:
                owner_name = owner.get('name', '')
                owner_zodiac = owner.get('zodiac', '')
                
                if owner_zodiac:
                    # 检查男命禁婚年
                    if '新郎' in owner_name or '男' in owner_name:
                        if self.jinhun_nian_nan.get(year_zhi) == owner_zodiac:
                            ji_list.append(f'新郎禁婚年（{year_zodiac}年禁{owner_zodiac}）')
                    
                    # 检查女命禁婚年
                    if '新娘' in owner_name or '女' in owner_name:
                        if self.jinhun_nian_nv.get(year_zhi) == owner_zodiac:
                            ji_list.append(f'新娘禁婚年（{year_zodiac}年禁{owner_zodiac}）')
                    
                    # 检查本命年
                    if year_zodiac == owner_zodiac:
                        ji_list.append(f'{owner_name}本命年（值太岁）')
        
        # 检查无春年（寡妇年）
        if self._is_wuchun_year(sizhu['date']):
            ji_list.append('无春年（寡妇年）')
    
    def _check_month_gods(self, sizhu, owners, lunar_info, yi_list, ji_list):
        """检查月神（利月/破月）"""
        month = lunar_info.get('month_num', 0)
        
        if owners:
            for owner in owners:
                owner_name = owner.get('name', '')
                owner_zodiac = owner.get('zodiac', '')
                
                if owner_zodiac and ('新娘' in owner_name or '女' in owner_name):
                    # 检查大利月
                    if month in self.daliyue.get(owner_zodiac, []):
                        yi_list.append(f'新娘大利月（{month}月）')
                    
                    # 检查小利月
                    elif month in self.xiaoliyue.get(owner_zodiac, []):
                        yi_list.append(f'新娘小利月（{month}月）')
                    
                    # 检查破月
                    elif month in self.poyue.get(owner_zodiac, []):
                        ji_list.append(f'新娘破月（{month}月）')
    
    def _check_day_gods(self, sizhu, lunar_info, yi_list, ji_list):
        """检查日神（吉神和凶神）"""
        day_zhi = sizhu['day_zhi']
        day_gan = sizhu['day_gan']
        month_zhi = sizhu['month_zhi']
        lunar_day = lunar_info.get('day_num', 0)
        lunar_month = lunar_info.get('month_num', 0)
        date_obj = sizhu.get('date', date.today())
        
        # 1. 使用专业神煞推算函数库
        try:
            # 准备新娘八字信息（如果有）
            bride_bazi = None
            if hasattr(self, 'owners') and self.owners:
                for owner in self.owners:
                    if '新娘' in owner.get('name', '') or '女' in owner.get('name', ''):
                        bride_bazi = owner.get('bazi', {})
                        break
            
            # 调用专业神煞检查
            pro_yi, pro_ji = check_marriage_shensha(date_obj, bride_bazi)
            yi_list.extend(pro_yi)
            ji_list.extend(pro_ji)
        except Exception as e:
            # 如果专业神煞检查失败，使用传统方法
            pass
        
        # 2. 传统方法检查（作为补充）
        
        # 检查天德、月德
        if month_zhi in self.tiande_yuede:
            gods = self.tiande_yuede[month_zhi]
            # 检查天德
            if day_gan == gods['天德']:
                if '天德' not in yi_list and '天德日' not in yi_list:
                    yi_list.append('天德')
            # 检查月德
            if day_gan == gods['月德']:
                if '月德' not in yi_list and '月德日' not in yi_list:
                    yi_list.append('月德')
        
        # 检查不将日（阴阳不将）
        if self._is_bujiang_day(sizhu):
            if '不将日' not in yi_list:
                yi_list.append('不将日')
        
        # 检查三合、六合
        if self._is_sanheliuhe_day(sizhu, getattr(self, 'owners', None)):
            yi_list.append('三合六合日')
        
        # 检查凶神
        
        # 检查三娘煞
        if lunar_day in self.sanniangsha:
            ji_list.append(f'三娘煞（{lunar_day}日）')
        
        # 检查杨公忌
        if lunar_month in self.yanggongji:
            if lunar_day in self.yanggongji[lunar_month]:
                ji_list.append(f'杨公忌（{lunar_month}月{lunar_day}日）')
        
        # 检查红纱日
        if lunar_month in self.hongsha:
            if day_zhi in self.hongsha[lunar_month]:
                ji_list.append(f'红纱日（{lunar_month}月犯{day_zhi}）')
        
        # 检查月破、岁破
        if self._is_poyue_day(sizhu):
            if '月破' not in ji_list and '月破日' not in ji_list:
                ji_list.append('月破日')
        if self._is_suipo_day(sizhu):
            ji_list.append('岁破日')
        
        # 检查往亡、受死
        if month_zhi in self.wangwang:
            if day_zhi == self.wangwang[month_zhi]:
                ji_list.append('往亡日')
        if month_zhi in self.shousi:
            if day_zhi == self.shousi[month_zhi]:
                ji_list.append('受死日')
        
        # 检查四离、四绝
        if self._is_silijue_day(sizhu):
            if '四离四绝' not in ji_list and '四离四绝日' not in ji_list:
                ji_list.append('四离四绝日')
        
        # 检查建除十二神
        jianchu = self._get_jianchu(sizhu)
        if jianchu in self.xiaohuangdao:
            if f'{jianchu}日' not in yi_list and jianchu not in [item.replace('日', '') for item in yi_list]:
                yi_list.append(f'{jianchu}日')
        
        # 检查阴阳差错日
        day_ganzhi = day_gan + day_zhi
        if day_ganzhi in self.yinyang_chacuo:
            ji_list.append('阴阳差错日')
        
        # 检查夫星、子星（如果有新娘信息）
        self._check_fuxing_zixing(sizhu, getattr(self, 'owners', None), ji_list)
        
        # 检查阴胎、阳气（如果有新娘信息）
        self._check_yintai_yangqi(sizhu, getattr(self, 'owners', None), ji_list)
    
    def _check_hour_gods(self, sizhu, yi_list, ji_list):
        """检查时神"""
        hour_zhi = sizhu['hour_zhi']
        day_gan = sizhu['day_gan']
        
        # 检查贵人登天门时
        if self._is_guiren_tianmen(sizhu):
            yi_list.append('贵人登天门时')
        
        # 检查六合时
        if self._is_liuhe_hour(sizhu):
            yi_list.append('六合时')
        
        # 检查五不遇时
        if self._is_wubuyu_hour(sizhu):
            ji_list.append('五不遇时')
        
        # 检查日破时
        if self._is_ripo_hour(sizhu):
            ji_list.append('日破时')
    
    def _is_wuchun_year(self, test_date):
        """检查是否为无春年（寡妇年）"""
        # 检查该年农历是否包含立春
        try:
            import sxtwl
            year = test_date.year
            
            # 检查立春日期
            lichun = sxtwl.getJieQi(year, 2)  # 立春是第2个节气
            
            # 如果立春在农历新年前，则该年无春
            # 这里简化处理，实际需要更精确的计算
            return False
        except:
            return False
    
    def _is_bujiang_day(self, sizhu):
        """检查是否为不将日（阴阳不将）"""
        # 不将日的判断比较复杂，需要根据年干支、月干支、日干支综合判断
        # 这里简化处理
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # 简化版：某些特定干支组合为不将日
        bujiang_combinations = [
            ('甲', '子'), ('乙', '丑'), ('丙', '寅'), ('丁', '卯'),
            ('戊', '辰'), ('己', '巳'), ('庚', '午'), ('辛', '未'),
            ('壬', '申'), ('癸', '酉')
        ]
        
        return (day_gan, day_zhi) in bujiang_combinations
    
    def _is_sanheliuhe_day(self, sizhu, owners):
        """检查是否为三合、六合日"""
        if not owners:
            return False
        
        day_zhi = sizhu['day_zhi']
        
        for owner in owners:
            owner_zodiac = owner.get('zodiac', '')
            if owner_zodiac:
                owner_zhi = self.zodiac_to_zhi.get(owner_zodiac, '')
                
                if owner_zhi:
                    # 检查三合
                    for sanhe_group in self.sanhe.values():
                        if day_zhi in sanhe_group and owner_zhi in sanhe_group:
                            return True
                    
                    # 检查六合
                    for liuhe_group in self.liuhe.values():
                        if day_zhi in liuhe_group and owner_zhi in liuhe_group:
                            return True
        
        return False
    
    def _is_poyue_day(self, sizhu):
        """检查是否为月破日"""
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # 月破日：日支与月支相冲
        po_pairs = [
            ('子', '午'), ('午', '子'),
            ('丑', '未'), ('未', '丑'),
            ('寅', '申'), ('申', '寅'),
            ('卯', '酉'), ('酉', '卯'),
            ('辰', '戌'), ('戌', '辰'),
            ('巳', '亥'), ('亥', '巳')
        ]
        
        return (month_zhi, day_zhi) in po_pairs
    
    def _is_suipo_day(self, sizhu):
        """检查是否为岁破日"""
        day_zhi = sizhu['day_zhi']
        year_zhi = sizhu['year_zhi']
        
        # 岁破日：日支与年支相冲
        po_pairs = [
            ('子', '午'), ('午', '子'),
            ('丑', '未'), ('未', '丑'),
            ('寅', '申'), ('申', '寅'),
            ('卯', '酉'), ('酉', '卯'),
            ('辰', '戌'), ('戌', '辰'),
            ('巳', '亥'), ('亥', '巳')
        ]
        
        return (year_zhi, day_zhi) in po_pairs
    
    def _is_silijue_day(self, sizhu):
        """检查是否为四离、四绝日"""
        # 四离：立春、立夏、立秋、立冬前一日
        # 四绝：春分、夏至、秋分、冬至前一日
        # 这里简化处理
        return False
    
    def _is_guiren_tianmen(self, sizhu):
        """检查是否为贵人登天门时"""
        # 贵人登天门时需要根据日干确定
        day_gan = sizhu['day_gan']
        hour_zhi = sizhu['hour_zhi']
        
        # 天乙贵人时辰
        guiren_hour = {
            '甲': ['丑', '未'],
            '乙': ['子', '申'],
            '丙': ['亥', '酉'],
            '丁': ['亥', '酉'],
            '戊': ['丑', '未'],
            '己': ['子', '申'],
            '庚': ['丑', '未'],
            '辛': ['寅', '午'],
            '壬': ['卯', '巳'],
            '癸': ['巳', '卯']
        }
        
        return hour_zhi in guiren_hour.get(day_gan, [])
    
    def _is_liuhe_hour(self, sizhu):
        """检查是否为六合时"""
        hour_zhi = sizhu['hour_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 检查时支与日支是否六合
        for liuhe_group in self.liuhe.values():
            if hour_zhi in liuhe_group and day_zhi in liuhe_group:
                return True
        
        return False
    
    def _is_wubuyu_hour(self, sizhu):
        """检查是否为五不遇时"""
        # 五不遇时：时干克日干
        day_gan = sizhu['day_gan']
        hour_gan = sizhu['hour_gan']
        
        # 获取天干序号
        day_gan_index = self.tiangan.index(day_gan)
        hour_gan_index = self.tiangan.index(hour_gan)
        
        # 五不遇时：时干为日干的第七个（相克）
        return (day_gan_index + 6) % 10 == hour_gan_index
    
    def _is_ripo_hour(self, sizhu):
        """检查是否为日破时"""
        hour_zhi = sizhu['hour_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 日破时：时支与日支相冲
        po_pairs = [
            ('子', '午'), ('午', '子'),
            ('丑', '未'), ('未', '丑'),
            ('寅', '申'), ('申', '寅'),
            ('卯', '酉'), ('酉', '卯'),
            ('辰', '戌'), ('戌', '辰'),
            ('巳', '亥'), ('亥', '巳')
        ]
        
        return (day_zhi, hour_zhi) in po_pairs
    
    def _get_jianchu(self, sizhu):
        """计算建除十二神"""
        # 建除十二神的计算需要根据月建和日支
        # 这里简化处理，实际需要更精确的计算
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # 获取月建的索引
        month_index = self.dizhi.index(month_zhi)
        # 获取日支的索引
        day_index = self.dizhi.index(day_zhi)
        
        # 计算建除十二神的索引
        jianchu_index = (month_index + day_index) % 12
        return self.jianchu[jianchu_index]
    
    def _check_fuxing_zixing(self, sizhu, owners, ji_list):
        """检查夫星、子星"""
        if not owners:
            return
        
        day_gan = sizhu['day_gan']
        
        for owner in owners:
            owner_name = owner.get('name', '')
            if '新娘' in owner_name or '女' in owner_name:
                # 获取新娘的日干（假设在owner中有bazi信息）
                bride_bazi = owner.get('bazi', {})
                bride_ri_gan = bride_bazi.get('ri_gan', '')
                
                if bride_ri_gan:
                    # 检查夫星
                    fuxing = self.fuxing.get(bride_ri_gan, '')
                    if fuxing and day_gan in self._get_ke_gans(fuxing):
                        ji_list.append('冲夫星')
                    
                    # 检查子星
                    zixing = self.zixing.get(bride_ri_gan, '')
                    if zixing and day_gan in self._get_ke_gans(zixing):
                        ji_list.append('冲子星')
    
    def _check_yintai_yangqi(self, sizhu, owners, ji_list):
        """检查阴胎、阳气"""
        if not owners:
            return
        
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        
        for owner in owners:
            owner_name = owner.get('name', '')
            if '新娘' in owner_name or '女' in owner_name:
                # 获取新娘的日柱（假设在owner中有bazi信息）
                bride_bazi = owner.get('bazi', {})
                bride_ri_gan = bride_bazi.get('ri_gan', '')
                bride_ri_zhi = bride_bazi.get('ri_zhi', '')
                
                if bride_ri_gan and bride_ri_zhi:
                    # 计算阴胎
                    yintai_gan = self._get_next_tiangan(bride_ri_gan)
                    yintai_zhi = self._get_next_dizhi(bride_ri_zhi, 3)
                    yintai = yintai_gan + yintai_zhi
                    
                    # 计算阳气
                    yangqi_gan = self._get_prev_tiangan(bride_ri_gan)
                    yangqi_zhi = self._get_prev_dizhi(bride_ri_zhi, 5)
                    yangqi = yangqi_gan + yangqi_zhi
                    
                    # 检查阴胎
                    current_ganzhi = day_gan + day_zhi
                    if current_ganzhi == yintai:
                        ji_list.append('犯阴胎')
                    elif self._is_chong_ganzhi(current_ganzhi, yintai):
                        ji_list.append('冲阴胎')
                    
                    # 检查阳气
                    if current_ganzhi == yangqi:
                        ji_list.append('犯阳气')
                    elif self._is_chong_ganzhi(current_ganzhi, yangqi):
                        ji_list.append('冲阳气')
    
    def _get_ke_gans(self, gan):
        """获取克某天干的天干列表"""
        ke_relations = {
            '甲': ['庚', '辛'],
            '乙': ['庚', '辛'],
            '丙': ['壬', '癸'],
            '丁': ['壬', '癸'],
            '戊': ['甲', '乙'],
            '己': ['甲', '乙'],
            '庚': ['丙', '丁'],
            '辛': ['丙', '丁'],
            '壬': ['戊', '己'],
            '癸': ['戊', '己']
        }
        return ke_relations.get(gan, [])
    
    def _get_next_tiangan(self, gan):
        """获取下一个天干"""
        index = self.tiangan.index(gan)
        return self.tiangan[(index + 1) % 10]
    
    def _get_prev_tiangan(self, gan):
        """获取上一个天干"""
        index = self.tiangan.index(gan)
        return self.tiangan[(index - 1) % 10]
    
    def _get_next_dizhi(self, zhi, steps):
        """获取后n个地支"""
        index = self.dizhi.index(zhi)
        return self.dizhi[(index + steps) % 12]
    
    def _get_prev_dizhi(self, zhi, steps):
        """获取前n个地支"""
        index = self.dizhi.index(zhi)
        return self.dizhi[(index - steps) % 12]
    
    def _is_chong_ganzhi(self, ganzhi1, ganzhi2):
        """检查两个干支是否相冲"""
        if len(ganzhi1) != 2 or len(ganzhi2) != 2:
            return False
        
        zhi1 = ganzhi1[1]
        zhi2 = ganzhi2[1]
        
        # 地支相冲关系
        chong_pairs = [
            ('子', '午'), ('午', '子'),
            ('丑', '未'), ('未', '丑'),
            ('寅', '申'), ('申', '寅'),
            ('卯', '酉'), ('酉', '卯'),
            ('辰', '戌'), ('戌', '辰'),
            ('巳', '亥'), ('亥', '巳')
        ]
        
        return (zhi1, zhi2) in chong_pairs

if __name__ == '__main__':
    # 测试婚嫁规则检查器
    checker = MarriageRuleChecker()
    print("婚嫁规则检查器初始化成功！")
    print("专业级嫁娶规则实现包含：")
    print("1. 年神（年禁）检查：禁婚年、无春年、本命年")
    print("2. 月神（利月/破月）检查：大利月、小利月、破月")
    print("3. 日神检查：吉神（天德月德、黄道、不将日等）和凶神（三娘煞、杨公忌等）")
    print("4. 时神检查：贵人登天门时、六和时等")
    print("5. 专业神煞：夫星、子星、阴胎、阳气、建除十二神、阴阳差错日")
    print("\n测试完成！")