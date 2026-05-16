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
        """检查与事主生肖相冲"""
        if not owners:
            return
        
        day_zhi = sizhu.get('day_zhi', '')
        if not day_zhi:
            return
        
        # 地支相冲关系
        chong_map = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
        
        for owner in owners:
            name = owner.get('name', '事主')
            # 尝试从不同字段获取生肖
            shengxiao = owner.get('生肖', '')
            if not shengxiao:
                # 从年柱地支获取
                if 'sizhu' in owner:
                    sizhu_parts = owner['sizhu'].split()
                    if len(sizhu_parts) >= 1:
                        shengxiao = sizhu_parts[0][1]
            if not shengxiao:
                # 从birth_date计算
                if 'birth_date' in owner:
                    try:
                        from ..四柱计算器 import calculate_sizhu
                        birth_sizhu = calculate_sizhu(
                            owner['birth_date'],
                            owner.get('birth_hour', 12),
                            owner.get('birth_minute', 0)
                        )
                        shengxiao = birth_sizhu['年柱'][1]
                    except Exception:
                        continue
            
            if shengxiao and chong_map.get(shengxiao) == day_zhi:
                ji_list.append(f'与{name}生肖相冲')
    
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
