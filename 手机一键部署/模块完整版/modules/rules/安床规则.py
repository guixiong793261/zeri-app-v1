import sys
import os

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

# -*- coding: utf-8 -*-
"""
================================================================================
安床规则模块（基于《协纪辨方书》）
================================================================================
实现安床择日的宜忌规则

核心规则：
1. 建除十二神：宜除、定、执、成、开；忌破
2. 天德、月德日宜
3. 不将日宜
4. 忌与事主生肖相冲
5. 忌月破、岁破
6. 床位朝向与日支五行关系（辅助参考）
================================================================================
"""

from .规则基类 import EventRuleChecker
from datetime import date

class BedRuleChecker(EventRuleChecker):
    """安床规则检查器"""
    
    # 建除十二神分类
    JIANCHU_YI = ['除', '定', '执', '成', '开']
    JIANCHU_JI = ['破']
    
    # 基础方向五行映射（支持常用方向和二十四山）
    DIRECTION_WUXING = {
        # 基础方向
        '东': '木', '东南': '木',
        '南': '火', '西南': '土',
        '西': '金', '西北': '金',
        '北': '水', '东北': '土',
        # 二十四山
        '壬': '水', '子': '水', '癸': '水',
        '丑': '土', '艮': '土', '寅': '木',
        '甲': '木', '卯': '木', '乙': '木',
        '辰': '土', '巽': '木', '巳': '火',
        '丙': '火', '午': '火', '丁': '火',
        '未': '土', '坤': '土', '申': '金',
        '庚': '金', '酉': '金', '辛': '金',
        '戌': '土', '乾': '金', '亥': '水',
    }
    
    # 地支五行
    ZHI_WUXING = {
        '子': '水', '丑': '土', '寅': '木', '卯': '木',
        '辰': '土', '巳': '火', '午': '火', '未': '土',
        '申': '金', '酉': '金', '戌': '土', '亥': '水'
    }
    
    # 五行相生
    SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    
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
                get_jianchu,
                is_tiande_day,
                is_yuede_day,
                is_bujiang_day,
                is_month_break,
                is_year_break,
                is_sili_sijue
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
    
    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查安床规则"""
        yi_list = []
        ji_list = []
        
        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list
        
        chuangwei = kwargs.get('chuangwei')
        
        # 1. 建除十二神规则
        self._check_jianchu(date_obj, yi_list, ji_list)
        
        # 2. 天德、月德日
        self._check_tiande_yuede(date_obj, yi_list)
        
        # 3. 不将日
        self._check_bujiang(date_obj, yi_list)
        
        # 4. 月破、岁破、四离四绝
        self._check_po_and_sili(date_obj, sizhu, owners, ji_list)
        
        # 5. 忌与事主生肖相冲
        self._check_shengxiao_chong(sizhu, owners, ji_list)
        
        # 6. 床位朝向辅助规则（仅供参考）
        if chuangwei:
            self._check_chuangwei(sizhu, chuangwei, yi_list, ji_list)
        
        # 7. 综合判断
        if yi_list and not ji_list:
            yi_list.append('安床')
        elif ji_list:
            ji_list.append('安床')
        
        return yi_list, ji_list
    
    def _check_jianchu(self, date_obj, yi_list, ji_list):
        """检查建除十二神"""
        if not self.get_jianchu:
            return
        
        try:
            jianchu = self.get_jianchu(date_obj)
            if jianchu in self.JIANCHU_YI:
                yi_list.append(f'建除{jianchu}日宜安床')
            elif jianchu in self.JIANCHU_JI:
                ji_list.append(f'建除{jianchu}日忌安床')
        except Exception:
            pass
    
    def _check_tiande_yuede(self, date_obj, yi_list):
        """检查天德、月德日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_tiande_day(date_obj):
                yi_list.append('天德日宜安床')
            if self.is_yuede_day(date_obj):
                yi_list.append('月德日宜安床')
        except Exception:
            pass
    
    def _check_bujiang(self, date_obj, yi_list):
        """检查不将日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_bujiang_day(date_obj):
                yi_list.append('不将日宜安床')
        except Exception:
            pass
    
    def _check_po_and_sili(self, date_obj, sizhu, owners, ji_list):
        """检查月破、岁破、四离四绝"""
        if not self.has_marriage_shensha:
            return
        
        try:
            # 月破
            if self.is_month_break(date_obj):
                ji_list.append('月破日忌安床')
            
            # 四离四绝
            if self.is_sili_sijue(date_obj):
                ji_list.append('四离四绝日忌安床')
            
            # 岁破（与事主年支相冲）
            if owners:
                year_zhi = sizhu.get('year_zhi', '')
                if year_zhi and self.is_year_break(date_obj, year_zhi):
                    ji_list.append('岁破日忌安床')
        except Exception:
            pass
    
    def _check_shengxiao_chong(self, sizhu, owners, ji_list):
        """
        检查四柱与事主生肖相冲（安床专用）
        传统择日：日为主；安床人（新婚夫妇/病人）为主
        
        参数:
            sizhu: 四柱字典
            owners: 事主列表
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
        
        # 生肖转地支
        zodiac_to_zhi = {
            '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
            '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
            '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
        }
        
        # 检查每个事主
        for owner in owners:
            name = owner.get('name', '事主')
            
            # 获取事主年支（地支）
            owner_zhi = ''
            
            # 先从生肖获取
            zodiac = owner.get('生肖', '')
            if zodiac:
                owner_zhi = zodiac_to_zhi.get(zodiac, '')
            
            # 如果没有，从sizhu获取
            if not owner_zhi and 'sizhu' in owner:
                sizhu_parts = owner['sizhu'].split()
                if len(sizhu_parts) >= 1:
                    owner_zhi = sizhu_parts[0][1]
            
            # 如果没有，从birth_date计算
            if not owner_zhi and 'birth_date' in owner:
                try:
                    from ..四柱计算器 import calculate_sizhu
                    birth_sizhu = calculate_sizhu(
                        owner['birth_date'],
                        owner.get('birth_hour', 12),
                        owner.get('birth_minute', 0)
                    )
                    owner_zhi = birth_sizhu['年柱'][1]
                except Exception:
                    continue
            
            if not owner_zhi:
                continue
            
            target_chong_zhi = chong_map.get(owner_zhi, '')
            
            if not target_chong_zhi:
                continue
            
            # 检查日柱（最重要）
            if day_zhi == target_chong_zhi:
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
    
    def _check_chuangwei(self, sizhu, chuangwei, yi_list, ji_list):
        """床位朝向辅助规则（仅供参考）"""
        cw_wuxing = self.DIRECTION_WUXING.get(chuangwei)
        dz_wuxing = self.ZHI_WUXING.get(sizhu.get('day_zhi'))
        
        if cw_wuxing and dz_wuxing:
            # 相生则宜
            if self.SHENG.get(cw_wuxing) == dz_wuxing:
                yi_list.append(f'{chuangwei}向安床（朝向生扶日支）')
            # 相克则忌（作为参考）
            else:
                ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
                if ke.get(cw_wuxing) == dz_wuxing:
                    ji_list.append(f'{chuangwei}向安床（朝向克制日支）')

# 测试
if __name__ == '__main__':
    checker = BedRuleChecker()
    
    # 测试数据
    test_sizhu = {
        'day_zhi': '卯',
        'month_zhi': '寅',
        'year_zhi': '子',
        '年柱': '甲子',
        'month': 2,
        'day': 10,
        'year': 2024
    }
    
    test_owners = [{
        'name': '张三',
        '生肖': '鸡'  # 酉
    }]
    
    # 使用新接口测试
    yi_list, ji_list = checker._check_rules(test_sizhu, test_owners, chuangwei='东')
    
    print("宜：", yi_list)
    print("忌：", ji_list)
