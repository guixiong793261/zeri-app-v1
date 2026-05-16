import sys
import os

if __name__ == '__main__' and __package__ is None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# -*- coding: utf-8 -*-
"""
================================================================================
开业规则模块（基于《协纪辨方书》）
================================================================================
实现开业、开市、纳财等事项的宜忌规则

核心规则：
1. 建除十二神：宜成、开、定、满；忌破、闭、平
2. 天德、月德日宜
3. 不将日宜
4. 忌月破、岁破、四离四绝
5. 黄道吉日（青龙、明堂等）
6. 与事主年命相合（三合、六合）
================================================================================
"""

from .规则基类 import EventRuleChecker
from datetime import date

class OpeningRuleChecker(EventRuleChecker):
    """开业规则检查器"""
    
    # 地支对应生肖
    ZHI_TO_ZODIAC = {
        '子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔',
        '辰': '龙', '巳': '蛇', '午': '马', '未': '羊',
        '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'
    }
    
    ZODIAC_TO_ZHI = {v: k for k, v in ZHI_TO_ZODIAC.items()}
    
    # 建除十二神吉凶
    JIANCHU_YI = ['成', '开', '定', '满']
    JIANCHU_JI = ['破', '闭', '平']
    
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
    
    def _get_owner_year_zhi(self, owner):
        """获取事主年支"""
        if '生肖' in owner:
            return self.ZODIAC_TO_ZHI.get(owner['生肖'], '')
        
        if 'zodiac' in owner:
            return self.ZODIAC_TO_ZHI.get(owner['zodiac'], '')
        
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
        
        return ''
    
    def _is_sanheliuhe(self, zhi1, zhi2):
        """检查两个地支是否三合或六合"""
        # 六合
        liuhe_pairs = [('子','丑'), ('寅','亥'), ('卯','戌'), ('辰','酉'), ('巳','申'), ('午','未')]
        if (zhi1, zhi2) in liuhe_pairs or (zhi2, zhi1) in liuhe_pairs:
            return True
        
        # 三合
        sanhe_groups = [['申','子','辰'], ['寅','午','戌'], ['巳','酉','丑'], ['亥','卯','未']]
        for group in sanhe_groups:
            if zhi1 in group and zhi2 in group:
                return True
        
        return False
    
    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查开业规则"""
        yi_list = []
        ji_list = []
        
        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list
        
        day_zhi = sizhu.get('day_zhi', '')
        day_gan = sizhu.get('day_gan', '')
        year_zhi = sizhu.get('year_zhi', '')
        
        # 1. 建除十二神
        self._check_jianchu(date_obj, yi_list, ji_list)
        
        # 2. 天德、月德日
        self._check_tiande_yuede(date_obj, yi_list)
        
        # 3. 不将日
        self._check_bujiang(date_obj, yi_list)
        
        # 4. 月破、岁破、四离四绝
        self._check_po_and_sili(date_obj, year_zhi, owners, ji_list)
        
        # 5. 与事主年命相合
        self._check_owner_match(sizhu, owners, yi_list)
        
        # 6. 综合判断开业、开市、纳财
        self._check_opening_types(sizhu, yi_list, ji_list)
        
        return yi_list, ji_list
    
    def _check_jianchu(self, date_obj, yi_list, ji_list):
        """检查建除十二神"""
        if not self.get_jianchu:
            return
        
        try:
            jianchu = self.get_jianchu(date_obj)
            if jianchu in self.JIANCHU_YI:
                yi_list.append(f'建除{jianchu}日宜开业')
            elif jianchu in self.JIANCHU_JI:
                ji_list.append(f'建除{jianchu}日忌开业')
        except Exception:
            pass
    
    def _check_tiande_yuede(self, date_obj, yi_list):
        """检查天德、月德日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_tiande_day(date_obj):
                yi_list.append('天德日宜开业')
            if self.is_yuede_day(date_obj):
                yi_list.append('月德日宜开业')
        except Exception:
            pass
    
    def _check_bujiang(self, date_obj, yi_list):
        """检查不将日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_bujiang_day(date_obj):
                yi_list.append('不将日宜开业')
        except Exception:
            pass
    
    def _check_po_and_sili(self, date_obj, year_zhi, owners, ji_list):
        """检查月破、岁破、四离四绝"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_month_break(date_obj):
                ji_list.append('月破日忌开业')
            
            if self.is_sili_sijue(date_obj):
                ji_list.append('四离四绝日忌开业')
            
            if year_zhi and self.is_year_break(date_obj, year_zhi):
                ji_list.append('岁破日忌开业')
            
            if owners:
                for owner in owners:
                    owner_zhi = self._get_owner_year_zhi(owner)
                    if owner_zhi and self.is_year_break(date_obj, owner_zhi):
                        name = owner.get('name', '事主')
                        ji_list.append(f'与{name}岁破，忌开业')
                        break
        except Exception:
            pass
    
    def _check_owner_match(self, sizhu, owners, yi_list):
        """检查与事主年命相合"""
        if not owners:
            return
        
        day_zhi = sizhu.get('day_zhi', '')
        if not day_zhi:
            return
        
        for owner in owners:
            name = owner.get('name', '事主')
            owner_zhi = self._get_owner_year_zhi(owner)
            
            if owner_zhi and self._is_sanheliuhe(day_zhi, owner_zhi):
                yi_list.append(f'与{name}年支相合')
    
    def _check_opening_types(self, sizhu, yi_list, ji_list):
        """综合判断开业、开市、纳财"""
        # 如果有忌项，添加开业忌
        if ji_list:
            ji_list.append('开业')
            ji_list.append('开市')
            ji_list.append('纳财')
        # 如果有宜项且没有忌项，添加开业宜
        elif yi_list:
            yi_list.append('开业')
            yi_list.append('开市')
            yi_list.append('纳财')

# 测试
if __name__ == '__main__':
    checker = OpeningRuleChecker()
    
    test_sizhu = {
        'day_gan': '丙',
        'day_zhi': '寅',
        'month_zhi': '寅',
        'year_zhi': '子',
        'month': 2,
        'day': 10,
        'year': 2024
    }
    
    test_owners = [{
        'name': '张三',
        '生肖': '虎'
    }]
    
    # 使用新接口测试
    yi_list, ji_list = checker._check_rules(test_sizhu, test_owners)
    
    print("宜：", yi_list)
    print("忌：", ji_list)
