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
作灶规则模块（基于《协纪辨方书》）
================================================================================
实现作灶择日的宜忌规则

核心规则：
1. 建除十二神：宜成、开、定；忌破、闭
2. 天德、月德日宜
3. 不将日宜
4. 灶君忌日、天火日、地火日、土府日忌
5. 忌与事主生肖相冲、岁破
6. 忌月破、四离四绝
7. 灶向/灶位五行辅助规则（仅供参考）
================================================================================
"""

from .规则基类 import EventRuleChecker
from datetime import date

class StoveRuleChecker(EventRuleChecker):
    """作灶规则检查器"""
    
    # 建除十二神分类
    JIANCHU_YI = ['成', '开', '定']
    JIANCHU_JI = ['破', '闭']
    
    # 基础方向五行映射
    DIRECTION_WUXING = {
        '东': '木', '东南': '木',
        '南': '火', '西南': '土',
        '西': '金', '西北': '金',
        '北': '水', '东北': '土',
    }
    
    # 八卦五行映射
    GUA_WUXING = {
        '乾': '金', '坤': '土', '震': '木', '巽': '木',
        '坎': '水', '离': '火', '艮': '土', '兑': '金'
    }
    
    # 二十四山五行映射
    SHIERSHAN_WUXING = {
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
        # 初始化依赖标志和函数引用
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
            # 备用实现
            self._init_fallback_functions()
    
    def _init_fallback_functions(self):
        """备用函数实现"""
        ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        def zhi_index(zhi):
            return ZHI.index(zhi) if zhi in ZHI else 0
        
        def get_day_ganzhi(date_obj):
            # 简化实现，实际应使用精确算法
            from ..shensha.marriage_shensha import get_day_ganzhi as real_get
            return real_get(date_obj)
        
        def fallback_get_jianchu(date_obj):
            try:
                from ..shensha.marriage_shensha import get_day_ganzhi
                month = date_obj.month
                month_zhi = ZHI[(month - 1) % 12]
                _, day_zhi = get_day_ganzhi(date_obj)
                month_idx = zhi_index(month_zhi)
                day_idx = zhi_index(day_zhi)
                offset = (day_idx - month_idx) % 12
                jianchu_list = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
                return jianchu_list[offset]
            except:
                return ''
        
        self.get_jianchu = fallback_get_jianchu
    
    def _sizhu_to_date(self, sizhu):
        """从sizhu构建日期对象"""
        # 尝试多种方式获取日期
        if 'date' in sizhu:
            return sizhu['date']
        
        # 从年、月、日字段获取
        try:
            year = int(sizhu.get('year', sizhu.get('年柱', '2000')[0:4]))
            month = int(sizhu.get('month', 1))
            day = int(sizhu.get('day', 1))
            return date(year, month, day)
        except:
            pass
        
        return None
    
    def _get_owner_year_zhi(self, owner):
        """获取事主年支（地支）"""
        # 生肖转地支
        zodiac_to_zhi = {
            '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
            '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
            '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
        }
        
        # 尝试从不同字段获取
        if '生肖' in owner:
            return zodiac_to_zhi.get(owner['生肖'], '')
        
        if 'sizhu' in owner:
            sizhu_parts = owner['sizhu'].split()
            if len(sizhu_parts) >= 1:
                return sizhu_parts[0][1]
        
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
    
    def _get_wuxing(self, direction):
        """获取方向/八卦/地支的五行，按优先级依次尝试"""
        # 先尝试基础方向
        if direction in self.DIRECTION_WUXING:
            return self.DIRECTION_WUXING[direction]
        # 再尝试八卦
        if direction in self.GUA_WUXING:
            return self.GUA_WUXING[direction]
        # 再尝试二十四山
        if direction in self.SHIERSHAN_WUXING:
            return self.SHIERSHAN_WUXING[direction]
        # 最后尝试地支
        if direction in self.ZHI_WUXING:
            return self.ZHI_WUXING[direction]
        return None
    
    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查作灶规则"""
        yi_list = []
        ji_list = []
        
        # 获取日期对象
        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list
        
        zaoxiang = kwargs.get('zaoxiang')
        zaowei = kwargs.get('zaowei')
        
        # 1. 建除十二神规则
        self._check_jianchu(date_obj, yi_list, ji_list)
        
        # 2. 天德、月德日（依赖marriage_shensha）
        self._check_tiande_yuede(date_obj, yi_list)
        
        # 3. 不将日（依赖marriage_shensha）
        self._check_bujiang(date_obj, yi_list)
        
        # 4. 月破、四离四绝（依赖marriage_shensha）
        self._check_po_and_sili(date_obj, owners, ji_list)
        
        # 5. 作灶专用神煞
        self._check_stove_special(sizhu, yi_list, ji_list)
        
        # 6. 忌与事主生肖相冲
        self._check_shengxiao_chong(sizhu, owners, ji_list)
        
        # 7. 灶向/灶位五行辅助规则（仅供参考，不影响判定）
        if zaoxiang:
            self._check_zaoxiang(sizhu, zaoxiang, yi_list, ji_list)
        if zaowei:
            self._check_zaowei(sizhu, zaowei, yi_list, ji_list)
        
        return yi_list, ji_list
    
    def _check_jianchu(self, date_obj, yi_list, ji_list):
        """检查建除十二神"""
        if not self.get_jianchu:
            return
        
        try:
            jianchu = self.get_jianchu(date_obj)
            if jianchu in self.JIANCHU_YI:
                yi_list.append(f'建除{jianchu}日宜作灶')
            elif jianchu in self.JIANCHU_JI:
                ji_list.append(f'建除{jianchu}日忌作灶')
        except Exception:
            pass
    
    def _check_tiande_yuede(self, date_obj, yi_list):
        """检查天德、月德日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_tiande_day(date_obj):
                yi_list.append('天德日宜作灶')
            if self.is_yuede_day(date_obj):
                yi_list.append('月德日宜作灶')
        except Exception:
            pass
    
    def _check_bujiang(self, date_obj, yi_list):
        """检查不将日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_bujiang_day(date_obj):
                yi_list.append('不将日宜作灶')
        except Exception:
            pass
    
    def _check_po_and_sili(self, date_obj, owners, ji_list):
        """检查月破、岁破、四离四绝"""
        if not self.has_marriage_shensha:
            return
        
        try:
            # 月破
            if self.is_month_break(date_obj):
                ji_list.append('月破日忌作灶')
            
            # 四离四绝
            if self.is_sili_sijue(date_obj):
                ji_list.append('四离四绝日忌作灶')
            
            # 岁破（与事主年支相冲）
            if owners:
                for owner in owners:
                    year_zhi = self._get_owner_year_zhi(owner)
                    if year_zhi and self.is_year_break(date_obj, year_zhi):
                        name = owner.get('name', '宅主')
                        ji_list.append(f'与{name}岁破，忌作灶')
                        break
        except Exception:
            pass
    
    def _check_stove_special(self, sizhu, yi_list, ji_list):
        """检查作灶专用神煞"""
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        
        # 丙丁日火旺宜作灶
        if day_gan in ['丙', '丁']:
            yi_list.append('丙丁日火旺宜作灶')
        
        # 灶君忌日
        zaojun_jiri = {
            '子': '未', '丑': '申', '寅': '酉', '卯': '戌',
            '辰': '亥', '巳': '子', '午': '丑', '未': '寅',
            '申': '卯', '酉': '辰', '戌': '巳', '亥': '午'
        }
        if month_zhi and zaojun_jiri.get(month_zhi) == day_zhi:
            ji_list.append('灶君忌日忌作灶')
        
        # 天火日
        tianhuo_days = {
            '寅': '子', '卯': '丑', '辰': '寅', '巳': '卯',
            '午': '辰', '未': '巳', '申': '午', '酉': '未',
            '戌': '申', '亥': '酉', '子': '戌', '丑': '亥'
        }
        if month_zhi and tianhuo_days.get(month_zhi) == day_zhi:
            ji_list.append('天火日忌作灶')
        
        # 地火日
        dihuo_days = {
            '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
            '午': '未', '未': '申', '申': '酉', '酉': '戌',
            '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
        }
        if month_zhi and dihuo_days.get(month_zhi) == day_zhi:
            ji_list.append('地火日忌作灶')
        
        # 土府日
        tufu_days = {
            '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申',
            '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
        }
        if month_zhi and tufu_days.get(month_zhi) == day_zhi:
            ji_list.append('土府日忌动土作灶')
    
    def _check_shengxiao_chong(self, sizhu, owners, ji_list):
        """
        检查四柱与事主生肖相冲（作灶专用）
        传统择日：日为主；主妇为主（灶为妇人主事）
        
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
        
        # 检查每个事主
        for owner in owners:
            name = owner.get('name', '事主')
            role = owner.get('role', '').lower()
            gender = owner.get('性别', '')
            
            # 获取事主年支（地支）
            owner_zhi = self._get_owner_year_zhi(owner)
            
            if not owner_zhi:
                continue
            
            # 判断是否为主妇（灶为妇人主事）
            is_housewife = role in ('主妇', '女主人', '夫人', '妻') or name in ('主妇', '女主人') or gender == '女'
            target_chong_zhi = chong_map.get(owner_zhi, '')
            
            if not target_chong_zhi:
                continue
            
            # 检查日柱（最重要）
            if day_zhi == target_chong_zhi:
                if is_housewife:
                    ji_list.append(f'日柱{day_zhi}冲主妇{name}')
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
    
    def _check_zaoxiang(self, sizhu, zaoxiang, yi_list, ji_list):
        """灶向五行辅助规则（仅供参考）"""
        zx_wuxing = self._get_wuxing(zaoxiang)
        dz_wuxing = self.ZHI_WUXING.get(sizhu.get('day_zhi'))
        
        if zx_wuxing and dz_wuxing:
            # 相生则宜
            if self.SHENG.get(zx_wuxing) == dz_wuxing:
                yi_list.append(f'{zaoxiang}向作灶（参考）')
    
    def _check_zaowei(self, sizhu, zaowei, yi_list, ji_list):
        """灶位五行辅助规则（仅供参考）"""
        zw_wuxing = self._get_wuxing(zaowei)
        dz_wuxing = self.ZHI_WUXING.get(sizhu.get('day_zhi'))
        
        if zw_wuxing and dz_wuxing:
            if self.SHENG.get(zw_wuxing) == dz_wuxing:
                yi_list.append(f'{zaowei}位安灶（参考）')

# 测试
if __name__ == '__main__':
    checker = StoveRuleChecker()
    
    test_sizhu = {
        'day_gan': '丙',
        'day_zhi': '寅',
        'month_zhi': '寅',
        'year_zhi': '子',
        '年柱': '甲子',
        'month': 2,
        'day': 10,
        'year': 2024
    }
    
    test_owners = [{
        'name': '张三',
        '生肖': '鸡'
    }]
    
    # 使用新接口测试
    yi_list, ji_list = checker._check_rules(test_sizhu, test_owners, zaoxiang='南', zaowei='乾')
    
    print("宜：", yi_list)
    print("忌：", ji_list)
