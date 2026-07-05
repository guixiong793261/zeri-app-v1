# -*- coding: utf-8 -*-
"""
================================================================================
高级安葬规则模块（基于《协纪辨方书》）
================================================================================
实现高级安葬择日的宜忌规则

核心规则：
1. 一票否决：重丧日、三丧日、年重丧、冲山日、月破、岁破、四离四绝、十恶大败
2. 吉神：天德、月德、不将日、黄道吉日、鸣吠日、鸣吠对日
3. 扶山：日课五行生扶坐山
4. 三合六合：日课与坐山相合
5. 相主：日课与孝子年命不冲克
================================================================================
"""

import sys
import os

# 处理导入路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
modules_dir = os.path.dirname(os.path.abspath(__file__))
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)

try:
    from .规则基类 import EventRuleChecker
except ImportError:
    from 规则基类 import EventRuleChecker

from datetime import date

class AdvancedBurialRuleChecker(EventRuleChecker):
    """高级安葬规则检查器"""
    
    # 建除十二神吉凶
    JIANCHU_YI = ['除', '定', '成', '开']
    JIANCHU_JI = ['破', '平', '收', '闭']
    
    # 二十四山五行属性
    ER_SHI_SI_SHAN_WUXING = {
        '壬': '水', '子': '水', '癸': '水',
        '丑': '土', '艮': '土', '寅': '木',
        '甲': '木', '卯': '木', '乙': '木',
        '辰': '土', '巽': '木', '巳': '火',
        '丙': '火', '午': '火', '丁': '火',
        '未': '土', '坤': '土', '申': '金',
        '庚': '金', '酉': '金', '辛': '金',
        '戌': '土', '乾': '金', '亥': '水'
    }
    
    # 地支五行
    ZHI_WUXING = {
        '子': '水', '丑': '土', '寅': '木', '卯': '木',
        '辰': '土', '巳': '火', '午': '火', '未': '土',
        '申': '金', '酉': '金', '戌': '土', '亥': '水'
    }
    
    # 五行生克（用于扶山判断：日课生坐山为吉）
    SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
    
    # 三煞方位（年支对应）
    SAN_SHA = {
        '申': ['巳', '午', '未'],  # 申子辰年煞南方
        '子': ['巳', '午', '未'],
        '辰': ['巳', '午', '未'],
        '寅': ['亥', '子', '丑'],  # 寅午戌年煞北方
        '午': ['亥', '子', '丑'],
        '戌': ['亥', '子', '丑'],
        '巳': ['寅', '卯', '辰'],  # 巳酉丑年煞东方
        '酉': ['寅', '卯', '辰'],
        '丑': ['寅', '卯', '辰'],
        '亥': ['申', '酉', '戌'],  # 亥卯未年煞西方
        '卯': ['申', '酉', '戌'],
        '未': ['申', '酉', '戌']
    }
    
    # 岁破方位（年支对冲）
    SUI_PO = {
        '子': '午', '午': '子',
        '丑': '未', '未': '丑',
        '寅': '申', '申': '寅',
        '卯': '酉', '酉': '卯',
        '辰': '戌', '戌': '辰',
        '巳': '亥', '亥': '巳'
    }
    
    # 三合局
    SANHE_GROUPS = [
        ['申', '子', '辰'],  # 水局
        ['寅', '午', '戌'],  # 火局
        ['巳', '酉', '丑'],  # 金局
        ['亥', '卯', '未']   # 木局
    ]
    
    # 重丧日口诀映射（按月查日干）
    # 口诀：正七连庚甲，二八乙辛当，五十一丁癸，四十丙壬方，三六九十二，戊己是重丧
    ZHONG_SANG_MAP = {
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
    
    # 年重丧映射（按年支查日干）
    NIAN_ZHONG_SANG_MAP = ZHONG_SANG_MAP  # 规律相同
    
    # 复日映射（正月甲日、二月乙日...）
    FURI_MAP = {
        '寅': '甲', '卯': '乙', '辰': '丙',
        '巳': '丁', '午': '戊', '未': '己',
        '申': '庚', '酉': '辛', '戌': '壬',
        '亥': '癸', '子': '甲', '丑': '乙'
    }
    
    # 往亡日映射
    WANGWANG_MAP = {
        '寅': '寅', '卯': '巳', '辰': '申', '巳': '亥',
        '午': '卯', '未': '午', '申': '酉', '酉': '子',
        '戌': '辰', '亥': '未', '子': '戌', '丑': '丑'
    }
    
    # 十恶大败日
    SHIE_DABAI = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
    
    # 鸣吠日（利于安葬）
    MINGFEI = ['庚午', '庚子', '庚申', '辛酉', '辛卯', '辛巳', '壬寅', '壬辰', '壬午', '壬申']
    
    # 鸣吠对日
    MINGFEIDUI = ['丙子', '丙午', '丙寅', '丁卯', '丁酉', '丁亥']
    
    # 地支列表
    DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
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
    
    def _get_lunar_info(self, date_obj):
        """获取农历信息"""
        try:
            from ..四柱计算器 import get_lunar_date
            return get_lunar_date(date_obj)
        except:
            return {}
    
    def _extract_zuoshan(self, shan_xiang):
        """从山向字符串中提取坐山"""
        if not shan_xiang:
            return None
        
        # 处理"子山午向"格式
        if '山' in shan_xiang:
            return shan_xiang.split('山')[0]
        
        # 处理"乾山巽向"格式或单字
        if len(shan_xiang) >= 1:
            return shan_xiang[0]
        
        return shan_xiang
    
    def _extract_zuoshan_jianxiang(self, shan_xiang):
        """从山向字符串中提取坐山（支持兼向）"""
        if not shan_xiang:
            return None
        
        # 处理"子山兼壬"或"壬山兼子"格式
        if '兼' in shan_xiang:
            parts = shan_xiang.split('兼')
            zuoshan_base = parts[0].replace('山', '')
            jianxiang = parts[1][0] if len(parts[1]) > 0 else ''
            return zuoshan_base, jianxiang
        
        # 处理"子山午向"格式
        if '山' in shan_xiang:
            zuoshan_base = shan_xiang.split('山')[0]
            return zuoshan_base, ''
        
        return shan_xiang[0] if len(shan_xiang) >= 1 else None, ''
    
    def _get_owner_year_zhi(self, owner):
        """获取事主年支"""
        if '生肖' in owner:
            return owner['生肖']
        
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
    
    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查安葬规则（基于《协纪辨方书》）"""
        yi_list = []
        ji_list = []
        
        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list
        
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        year_zhi = sizhu.get('year_zhi', '')
        shan_xiang = kwargs.get('shan_xiang')
        
        # 提取坐山
        zuoshan = self._extract_zuoshan(shan_xiang)
        
        # ===== 一票否决项（大凶）=====
        # 1. 重丧日（按月查日干）
        if month_zhi and day_gan and self._is_zhongsang(month_zhi, day_gan):
            ji_list.append('重丧日忌安葬')
        
        # 2. 年重丧（按年支查日干）
        if year_zhi and day_gan and self._is_nian_zhongsang(year_zhi, day_gan):
            ji_list.append('年重丧忌安葬')
        
        # 3. 三丧日（按季节查日支）
        if month_zhi and day_zhi and self._is_sansang(month_zhi, day_zhi):
            ji_list.append('三丧日忌安葬')
        
        # 4. 复日（重丧类）
        if month_zhi and day_gan and self._is_furi(month_zhi, day_gan):
            ji_list.append('复日忌安葬')
        
        # 5. 十恶大败日
        if day_gan and day_zhi and self._is_shie_dabai(day_gan + day_zhi):
            ji_list.append('十恶大败日忌安葬')
        
        # 6. 月破日
        if self.has_marriage_shensha:
            try:
                if self.is_month_break(date_obj):
                    ji_list.append('月破日忌安葬')
            except:
                pass
        else:
            # 备用检查：日支与月支相冲
            if month_zhi and day_zhi and self._is_chong(month_zhi, day_zhi):
                ji_list.append('月破日忌安葬')
        
        # 7. 岁破日
        if year_zhi and day_zhi and self._is_sui_po_day(year_zhi, day_zhi):
            ji_list.append('岁破日忌安葬')
        
        # 8. 四离四绝
        if self.has_marriage_shensha:
            try:
                if self.is_sili_sijue(date_obj):
                    ji_list.append('四离四绝日忌安葬')
            except:
                pass
        else:
            # 备用检查
            if month_zhi and day_zhi:
                if self._is_sili(month_zhi, day_zhi):
                    ji_list.append('四离日忌安葬')
                if self._is_sijue(month_zhi, day_zhi):
                    ji_list.append('四绝日忌安葬')
        
        # 9. 往亡日
        if month_zhi and day_zhi and self._is_wangwang(month_zhi, day_zhi):
            ji_list.append('往亡日忌安葬')
        
        # 10. 冲山日（日支冲坐山）
        if zuoshan and day_zhi:
            if self._is_chong(day_zhi, zuoshan):
                ji_list.append(f'{zuoshan}山被日支冲克')
        
        # 如果有一票否决项，直接返回
        if ji_list:
            ji_list.append('安葬')
            return yi_list, ji_list
        
        # ===== 吉神检查 =====
        # 1. 建除十二神
        self._check_jianchu(date_obj, yi_list, ji_list)
        
        # 2. 天德月德
        self._check_tiande_yuede(date_obj, yi_list)
        
        # 3. 不将日
        self._check_bujiang(date_obj, yi_list)
        
        # 4. 鸣吠日
        if day_gan and day_zhi and self._is_mingfei(day_gan + day_zhi):
            yi_list.append('鸣吠日宜安葬')
        
        # 5. 鸣吠对日
        if day_gan and day_zhi and self._is_mingfeidui(day_gan + day_zhi):
            yi_list.append('鸣吠对日宜安葬')
        
        # ===== 扶山检查（日课生扶坐山）=====
        if zuoshan:
            self._check_fushan(sizhu, zuoshan, yi_list, ji_list)
            
            # 三合局检查
            self._check_sanhe(sizhu, zuoshan, yi_list)
            
            # 三煞检查
            if year_zhi and self._is_san_sha(year_zhi, zuoshan):
                ji_list.append(f'{zuoshan}山犯年三煞')
            
            # 岁破检查（方位）
            if year_zhi and self._is_sui_po_direction(year_zhi, zuoshan):
                ji_list.append(f'{zuoshan}山犯岁破')
        
        # ===== 相主检查（与孝子年命关系）=====
        self._check_owner_match(sizhu, owners, yi_list, ji_list)
        
        # 综合判断
        if yi_list and not ji_list:
            yi_list.append('安葬')
        elif ji_list:
            ji_list.append('安葬')
        
        return yi_list, ji_list
    
    # ===== 重丧类神煞 =====
    
    def _is_zhongsang(self, month_zhi, day_gan):
        """
        是否重丧日（按月查日干）
        口诀：正七连庚甲，二八乙辛当，五十一丁癸，四十丙壬方，三六九十二，戊己是重丧
        """
        return day_gan in self.ZHONG_SANG_MAP.get(month_zhi, [])
    
    def _is_nian_zhongsang(self, year_zhi, day_gan):
        """
        是否年重丧（按年支查日干）
        口诀与月重丧相同规律
        """
        return day_gan in self.NIAN_ZHONG_SANG_MAP.get(year_zhi, [])
    
    def _is_sansang(self, month_zhi, day_zhi):
        """
        是否三丧日（按季节查日支）
        口诀：春辰夏未秋戌冬丑
        """
        if month_zhi in ['寅', '卯', '辰']:  # 春季
            return day_zhi == '辰'
        elif month_zhi in ['巳', '午', '未']:  # 夏季
            return day_zhi == '未'
        elif month_zhi in ['申', '酉', '戌']:  # 秋季
            return day_zhi == '戌'
        elif month_zhi in ['亥', '子', '丑']:  # 冬季
            return day_zhi == '丑'
        return False
    
    def _is_furi(self, month_zhi, day_gan):
        """
        是否复日（重丧类）
        复日：正月甲日、二月乙日、三月丙日……依此类推
        """
        return day_gan == self.FURI_MAP.get(month_zhi)
    
    def _is_wangwang(self, month_zhi, day_zhi):
        """
        是否往亡日
        口诀：正寅二巳三申四亥五卯六午七酉八子九辰十未十一戌十二丑
        """
        return day_zhi == self.WANGWANG_MAP.get(month_zhi)
    
    def _is_shie_dabai(self, day_pillar):
        """是否十恶大败日"""
        return day_pillar in self.SHIE_DABAI
    
    def _is_sili(self, month_zhi, day_zhi):
        """是否四离日"""
        sili_map = {'卯': '辰', '午': '未', '酉': '戌', '子': '丑'}
        return day_zhi == sili_map.get(month_zhi)
    
    def _is_sijue(self, month_zhi, day_zhi):
        """是否四绝日"""
        sijue_map = {'丑': '寅', '辰': '巳', '未': '申', '戌': '亥'}
        return day_zhi == sijue_map.get(month_zhi)
    
    def _is_sui_po_day(self, year_zhi, day_zhi):
        """是否岁破日（日支与年支相冲）"""
        return self._is_chong(year_zhi, day_zhi)
    
    def _is_mingfei(self, day_pillar):
        """是否鸣吠日"""
        return day_pillar in self.MINGFEI
    
    def _is_mingfeidui(self, day_pillar):
        """是否鸣吠对日"""
        return day_pillar in self.MINGFEIDUI
    
    def _is_chong(self, zhi1, zhi2):
        """检查两个地支是否相冲"""
        chong_pairs = [('子','午'), ('丑','未'), ('寅','申'), 
                       ('卯','酉'), ('辰','戌'), ('巳','亥')]
        return (zhi1, zhi2) in chong_pairs or (zhi2, zhi1) in chong_pairs
    
    def _check_jianchu(self, date_obj, yi_list, ji_list):
        """检查建除十二神"""
        if not self.get_jianchu:
            return
        
        try:
            jianchu = self.get_jianchu(date_obj)
            if jianchu in self.JIANCHU_YI:
                yi_list.append(f'建除{jianchu}日宜安葬')
            elif jianchu in self.JIANCHU_JI:
                ji_list.append(f'建除{jianchu}日忌安葬')
        except Exception:
            pass
    
    def _check_tiande_yuede(self, date_obj, yi_list):
        """检查天德、月德日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_tiande_day(date_obj):
                yi_list.append('天德日宜安葬')
            if self.is_yuede_day(date_obj):
                yi_list.append('月德日宜安葬')
        except Exception:
            pass
    
    def _check_bujiang(self, date_obj, yi_list):
        """检查不将日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_bujiang_day(date_obj):
                yi_list.append('不将日宜安葬')
        except Exception:
            pass
    
    def _check_fushan(self, sizhu, zuoshan, yi_list, ji_list):
        """扶山检查：日课生扶坐山"""
        zuoshan_wuxing = self.ER_SHI_SI_SHAN_WUXING.get(zuoshan)
        if not zuoshan_wuxing:
            return
        
        # 获取日课地支五行
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        year_zhi = sizhu.get('year_zhi', '')
        
        # 检查日课地支是否生扶坐山
        for zhi in [year_zhi, month_zhi, day_zhi]:
            if not zhi:
                continue
            
            zhi_wuxing = self.ZHI_WUXING.get(zhi)
            if not zhi_wuxing:
                continue
            
            # 日课生坐山为吉（扶山）
            if self.SHENG.get(zhi_wuxing) == zuoshan_wuxing:
                yi_list.append(f'{zuoshan}山得{zhi}生扶')
                break
            
            # 日课克坐山为凶
            if self.KE.get(zhi_wuxing) == zuoshan_wuxing:
                ji_list.append(f'{zuoshan}山被{zhi}克制')
                break
    
    def _check_sanhe(self, sizhu, zuoshan, yi_list):
        """三合局检查"""
        zhis = []
        for key in ['year_zhi', 'month_zhi', 'day_zhi']:
            zhi = sizhu.get(key)
            if zhi:
                zhis.append(zhi)
        
        # 检查是否与坐山形成三合局
        for group in self.SANHE_GROUPS:
            if zuoshan in group:
                count = sum(1 for z in zhis if z in group)
                if count >= 1:
                    other_zhis = [z for z in group if z != zuoshan]
                    present = [z for z in other_zhis if z in zhis]
                    yi_list.append(f'{zuoshan}山与{"、".join(present)}半合{self._get_sanhe_name(group)}')
    
    def _get_sanhe_name(self, group):
        """获取三合局名称"""
        if '申' in group:
            return '水局'
        elif '寅' in group:
            return '火局'
        elif '巳' in group:
            return '金局'
        elif '亥' in group:
            return '木局'
        return '局'
    
    def _is_san_sha(self, year_zhi, zuoshan):
        """检查坐山是否犯三煞"""
        san_sha_directions = self.SAN_SHA.get(year_zhi, [])
        return zuoshan in san_sha_directions
    
    def _is_sui_po_direction(self, year_zhi, zuoshan):
        """检查坐山是否犯岁破方位"""
        sui_po_direction = self.SUI_PO.get(year_zhi, '')
        return zuoshan == sui_po_direction
    
    def _check_owner_match(self, sizhu, owners, yi_list, ji_list):
        """检查与事主年命关系"""
        if not owners:
            return
        
        day_zhi = sizhu.get('day_zhi', '')
        if not day_zhi:
            return
        
        for owner in owners:
            name = owner.get('name', '事主')
            owner_zhi = self._get_owner_year_zhi(owner)
            
            if not owner_zhi:
                continue
            
            # 检查相冲
            if self._is_chong(day_zhi, owner_zhi):
                ji_list.append(f'与{name}年命相冲')
                break
            
            # 检查三合六合
            if self._is_sanheliuhe(day_zhi, owner_zhi):
                yi_list.append(f'与{name}年命相合')
    
    def _is_sanheliuhe(self, zhi1, zhi2):
        """检查两个地支是否三合或六合"""
        # 六合
        liuhe_pairs = [('子','丑'), ('寅','亥'), ('卯','戌'), 
                       ('辰','酉'), ('巳','申'), ('午','未')]
        if (zhi1, zhi2) in liuhe_pairs or (zhi2, zhi1) in liuhe_pairs:
            return True
        
        # 三合
        for group in self.SANHE_GROUPS:
            if zhi1 in group and zhi2 in group:
                return True
        
        return False
    
    def get_forbidden_directions(self, sizhu):
        """获取禁止使用的方位列表"""
        forbidden = []
        all_directions = ['壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
                         '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥']
        
        year_zhi = sizhu.get('year_zhi', '')
        if not year_zhi:
            year_zhu = sizhu.get('年柱', '')
            if len(year_zhu) >= 2:
                year_zhi = year_zhu[1]
        
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        
        for direction in all_directions:
            # 三煞
            if year_zhi and self._is_san_sha(year_zhi, direction):
                forbidden.append(direction)
                continue
            
            # 岁破方位
            if year_zhi and self._is_sui_po_direction(year_zhi, direction):
                forbidden.append(direction)
                continue
            
            # 冲山（日支冲坐山）
            if day_zhi and self._is_chong(day_zhi, direction):
                forbidden.append(direction)
                continue
        
        return forbidden
    
    def is_direction_forbidden(self, sizhu, direction):
        """检查某个方位是否被禁止"""
        year_zhi = sizhu.get('year_zhi', '')
        if not year_zhi:
            year_zhu = sizhu.get('年柱', '')
            if len(year_zhu) >= 2:
                year_zhi = year_zhu[1]
        
        day_zhi = sizhu.get('day_zhi', '')
        
        return (year_zhi and self._is_san_sha(year_zhi, direction)) or \
               (year_zhi and self._is_sui_po_direction(year_zhi, direction)) or \
               (day_zhi and self._is_chong(day_zhi, direction))

if __name__ == '__main__':
    checker = AdvancedBurialRuleChecker()
    
    test_sizhu = {
        '年柱': '戊子',
        '月柱': '庚申',
        '日柱': '辛亥',
        '时柱': '甲午',
        'year_zhi': '子',
        'month_zhi': '申',
        'day_zhi': '亥',
        'day_gan': '辛',
        'hour_zhi': '午',
        'year': 2008,
        'month': 8,
        'day': 31
    }
    
    test_owners = [{'name': '孝子张三', '生肖': '鼠'}]
    
    yi_list, ji_list = checker._check_rules(test_sizhu, test_owners, shan_xiang='壬山丙向')
    
    print("宜：", yi_list)
    print("忌：", ji_list)
    
    forbidden = checker.get_forbidden_directions(test_sizhu)
    print(f"\n禁止使用的方位: {forbidden}")
    
    # 测试重丧日
    print("\n=== 重丧日测试 ===")
    # 申月（七月）庚日、甲日为重丧
    test_sizhu2 = {
        'month_zhi': '申',
        'day_gan': '庚',
        'day_zhi': '午'
    }
    print(f"申月庚日是否重丧: {checker._is_zhongsang('申', '庚')}")
    print(f"申月甲日是否重丧: {checker._is_zhongsang('申', '甲')}")
    print(f"申月乙日是否重丧: {checker._is_zhongsang('申', '乙')}")
    
    # 测试三丧日
    print("\n=== 三丧日测试 ===")
    print(f"春季辰日是否三丧: {checker._is_sansang('寅', '辰')}")
    print(f"夏季未日是否三丧: {checker._is_sansang('巳', '未')}")
    print(f"秋季戌日是否三丧: {checker._is_sansang('申', '戌')}")
    print(f"冬季丑日是否三丧: {checker._is_sansang('亥', '丑')}")
    
    # 测试岁破日
    print("\n=== 岁破日测试 ===")
    print(f"子年午日是否岁破: {checker._is_sui_po_day('子', '午')}")
    print(f"午年子日是否岁破: {checker._is_sui_po_day('午', '子')}")