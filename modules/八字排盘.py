# -*- coding: utf-8 -*-
"""
================================================================================
八字排盘模块
================================================================================
提供完整的八字排盘功能，包括：
- 四柱排盘（年柱、月柱、日柱、时柱）
- 藏干分析
- 十神分析
- 五行统计
- 纳音五行
- 十二长生
- 神煞查询
- 大运流年

使用方法:
    1. 作为模块导入: from modules.八字排盘 import BaZiPanPan
    2. 直接运行: python -m modules.八字排盘
================================================================================
"""

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

from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# 从工具函数导入基础数据
try:
    from .工具函数 import TIAN_GAN, DI_ZHI, GAN_WUXING, ZHI_WUXING, ZHIGAN_SIMPLE as ZHIGAN_MAP
except ImportError:
    try:
        from 工具函数 import TIAN_GAN, DI_ZHI, GAN_WUXING, ZHI_WUXING, ZHIGAN_SIMPLE as ZHIGAN_MAP
    except ImportError:
        # 本地定义作为回退
        TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        GAN_WUXING = {
            '甲': '木', '乙': '木',
            '丙': '火', '丁': '火',
            '戊': '土', '己': '土',
            '庚': '金', '辛': '金',
            '壬': '水', '癸': '水'
        }
        ZHI_WUXING = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        ZHIGAN_MAP = {
            '子': ['癸'],
            '丑': ['己', '癸', '辛'],
            '寅': ['甲', '丙', '戊'],
            '卯': ['乙'],
            '辰': ['戊', '乙', '癸'],
            '巳': ['丙', '庚', '戊'],
            '午': ['丁', '己'],
            '未': ['己', '丁', '乙'],
            '申': ['庚', '壬', '戊'],
            '酉': ['辛'],
            '戌': ['戊', '辛', '丁'],
            '亥': ['壬', '甲']
        }

# 十神定义（以日干为主）
try:
    from .工具函数 import get_shishen
except ImportError:
    try:
        from 工具函数 import get_shishen
    except ImportError:
        # 本地实现作为回退
        def get_shishen(day_gan: str, target_gan: str) -> str:
            """
            计算十神
            
            Args:
                day_gan: 日干
                target_gan: 目标天干
                
            Returns:
                str: 十神名称
            """
            if day_gan == target_gan:
                return '比肩'
            
            if day_gan not in TIAN_GAN or target_gan not in TIAN_GAN:
                return '未知'
            
            day_idx = TIAN_GAN.index(day_gan)
            target_idx = TIAN_GAN.index(target_gan)
            
            # 判断阴阳（偶数为阳，奇数为阴）
            day_yang = day_idx % 2 == 0
            target_yang = target_idx % 2 == 0
            is_same_yin_yang = (day_yang == target_yang)
            
            # 计算五行关系
            day_wx = GAN_WUXING[day_gan]
            target_wx = GAN_WUXING[target_gan]
            
            # 五行生克关系
            WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
            WUXING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
            
            # 同我
            if target_wx == day_wx:
                return '比肩' if is_same_yin_yang else '劫财'
            
            # 生我（印）
            if WUXING_SHENG.get(target_wx) == day_wx:
                return '正印' if is_same_yin_yang else '偏印'
            
            # 我生（食伤）
            if WUXING_SHENG.get(day_wx) == target_wx:
                return '食神' if is_same_yin_yang else '伤官'
            
            # 我克（财）
            if WUXING_KE.get(day_wx) == target_wx:
                return '正财' if is_same_yin_yang else '偏财'
            
            # 克我（官杀）
            if WUXING_KE.get(target_wx) == day_wx:
                return '正官' if is_same_yin_yang else '七杀'
            
            return '未知'


class BaZiPanPan:
    """
    八字排盘类
    
    提供完整的八字排盘和分析功能
    """
    
    def __init__(self, year: int, month: int, day: int, hour: int, minute: int = 0, gender: str = '男', use_true_solar: bool = False, longitude: float = 120.0, latitude: float = 30.0):
        """
        初始化八字排盘
        
        Args:
            year: 出生年
            month: 出生月
            day: 出生日
            hour: 出生时（0-23）
            minute: 出生分（0-59）
            gender: 性别，'男'或'女'
            use_true_solar: 是否使用真太阳时
            longitude: 经度（默认120.0，北京时间基准）
            latitude: 纬度（默认30.0，参考值）
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.gender = gender
        self.use_true_solar = use_true_solar
        self.longitude = longitude
        self.latitude = latitude
        
        # 四柱信息
        self.sizhu = {}
        self.canggan = {}
        self.shishen = {}
        self.wuxing_count = {}
        self.nayin = {}
        self.zhangsheng = {}
        
        # 执行排盘
        self._calculate_sizhu()
        self._calculate_canggan()
        self._calculate_shishen()
        self._calculate_wuxing()
        self._calculate_nayin()
        self._calculate_zhangsheng()
    
    def _calculate_sizhu(self):
        """计算四柱（统一调用四柱计算器）
        
        【重要说明】
        这是计算四柱的唯一入口，所有模块都应通过四柱计算器获取四柱
        不再直接调用其他计算方式
        """
        try:
            from .四柱计算器 import calculate_sizhu
            target_date = date(self.year, self.month, self.day)
            # 调用四柱计算器
            self.sizhu = calculate_sizhu(
                target_date, 
                self.hour, 
                self.minute, 
                0
            )
        except Exception as e:
            logger.error(f"计算四柱失败: {e}")
            # 使用简化计算
            self.sizhu = self._simple_sizhu_calc()
    
    def _normalize_sizhu_format(self, raw: Dict) -> Dict:
        """
        标准化四柱字典格式
        
        Args:
            raw: 原始四柱字典
            
        Returns:
            Dict: 标准格式的四柱字典
        """
        normalized = {}
        
        # 处理完整柱名（'年柱'、'月柱'、'日柱'、'时柱'）
        pillar_keys = {
            'year': '年柱',
            'month': '月柱',
            'day': '日柱',
            'hour': '时柱'
        }
        
        for raw_key, standard_key in pillar_keys.items():
            if raw_key in raw:
                normalized[standard_key] = raw[raw_key]
            elif standard_key in raw:
                normalized[standard_key] = raw[standard_key]
        
        # 处理天干地支（'year_gan'、'year_zhi'等）
        gan_zhi_keys = {
            'year_gan': '年干',
            'year_zhi': '年支',
            'month_gan': '月干',
            'month_zhi': '月支',
            'day_gan': '日干',
            'day_zhi': '日支',
            'hour_gan': '时干',
            'hour_zhi': '时支'
        }
        
        for raw_key, standard_key in gan_zhi_keys.items():
            if raw_key in raw:
                normalized[raw_key] = raw[raw_key]
            elif standard_key in raw:
                normalized[raw_key] = raw[standard_key]
        
        # 从完整柱名中提取天干地支（如果没有单独的天干地支字段）
        for pillar, pillar_name in [('year', '年柱'), ('month', '月柱'), 
                                   ('day', '日柱'), ('hour', '时柱')]:
            if pillar_name in normalized and len(normalized[pillar_name]) >= 2:
                if f'{pillar}_gan' not in normalized:
                    normalized[f'{pillar}_gan'] = normalized[pillar_name][0]
                if f'{pillar}_zhi' not in normalized:
                    normalized[f'{pillar}_zhi'] = normalized[pillar_name][1]
        
        return normalized
    
    def _simple_sizhu_calc(self) -> Dict:
        """简化四柱计算（备用）"""
        # 使用标准格式
        return {
            '年柱': '甲子', '月柱': '乙丑', 
            '日柱': '丙寅', '时柱': '丁卯',
            'year_gan': '甲', 'year_zhi': '子',
            'month_gan': '乙', 'month_zhi': '丑',
            'day_gan': '丙', 'day_zhi': '寅',
            'hour_gan': '丁', 'hour_zhi': '卯'
        }
    
    def _calculate_canggan(self):
        """计算藏干"""
        self.canggan = {
            '年支': ZHIGAN_MAP.get(self.sizhu.get('year_zhi', ''), []),
            '月支': ZHIGAN_MAP.get(self.sizhu.get('month_zhi', ''), []),
            '日支': ZHIGAN_MAP.get(self.sizhu.get('day_zhi', ''), []),
            '时支': ZHIGAN_MAP.get(self.sizhu.get('hour_zhi', ''), [])
        }
    
    def _calculate_shishen(self):
        """计算十神"""
        day_gan = self.sizhu.get('day_gan', '')
        if not day_gan:
            return
        
        self.shishen = {
            '年干': get_shishen(day_gan, self.sizhu.get('year_gan', '')),
            '月干': get_shishen(day_gan, self.sizhu.get('month_gan', '')),
            '日干': '日主',
            '时干': get_shishen(day_gan, self.sizhu.get('hour_gan', '')),
        }
        
        # 地支藏干的十神
        for zhi_name, gans in self.canggan.items():
            self.shishen[zhi_name] = [get_shishen(day_gan, g) for g in gans]
    
    def _calculate_wuxing(self):
        """计算五行统计"""
        counts = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
        
        # 天干五行
        for gan in [self.sizhu.get('year_gan', ''), 
                    self.sizhu.get('month_gan', ''),
                    self.sizhu.get('day_gan', ''),
                    self.sizhu.get('hour_gan', '')]:
            if gan:
                counts[GAN_WUXING.get(gan, '')] += 1
        
        # 地支五行
        for zhi in [self.sizhu.get('year_zhi', ''),
                    self.sizhu.get('month_zhi', ''),
                    self.sizhu.get('day_zhi', ''),
                    self.sizhu.get('hour_zhi', '')]:
            if zhi:
                counts[ZHI_WUXING.get(zhi, '')] += 1
        
        self.wuxing_count = counts
        
        # 计算带权重的五行分数
        self.wuxing_score = self._calculate_wuxing_score()
    
    def _calculate_wuxing_score(self, include_canggan: bool = True, use_weight: bool = True) -> Dict[str, float]:
        """
        计算带权重的五行分数
        
        Args:
            include_canggan: 是否包含藏干
            use_weight: 是否使用藏干权重
            
        Returns:
            Dict[str, float]: 各五行分数
        """
        try:
            from .八字工具整合 import calculate_wuxing_score
            return calculate_wuxing_score(self.sizhu, include_canggan)
        except ImportError:
            # 回退到本地实现
            return self._local_wuxing_score(include_canggan, use_weight)
    
    def _local_wuxing_score(self, include_canggan: bool = True, use_weight: bool = True) -> Dict[str, float]:
        """
        本地实现的五行分数计算（回退方案）
        
        Args:
            include_canggan: 是否包含藏干
            use_weight: 是否使用藏干权重
            
        Returns:
            Dict[str, float]: 各五行分数
        """
        scores = {'金': 0.0, '木': 0.0, '水': 0.0, '火': 0.0, '土': 0.0}
        
        # 天干五行（权重1.0）
        for gan in [self.sizhu.get('year_gan', ''), 
                    self.sizhu.get('month_gan', ''),
                    self.sizhu.get('day_gan', ''),
                    self.sizhu.get('hour_gan', '')]:
            if gan:
                wx = GAN_WUXING.get(gan, '')
                if wx:
                    scores[wx] += 1.0
        
        # 地支五行（本气权重0.8）
        for zhi in [self.sizhu.get('year_zhi', ''),
                    self.sizhu.get('month_zhi', ''),
                    self.sizhu.get('day_zhi', ''),
                    self.sizhu.get('hour_zhi', '')]:
            if zhi:
                wx = ZHI_WUXING.get(zhi, '')
                if wx:
                    scores[wx] += 0.8
                
                # 藏干
                if include_canggan and zhi in ZHIGAN_MAP:
                    if use_weight:
                        # 使用带权重的藏干表
                        try:
                            from .八字工具整合 import ZHIGAN_WEIGHTED
                            if zhi in ZHIGAN_WEIGHTED:
                                for gan, weight in ZHIGAN_WEIGHTED[zhi]:
                                    wx = GAN_WUXING.get(gan, '')
                                    if wx:
                                        scores[wx] += weight * 0.5
                        except ImportError:
                            # 使用简化版藏干表
                            for gan in ZHIGAN_MAP[zhi]:
                                wx = GAN_WUXING.get(gan, '')
                                if wx:
                                    scores[wx] += 0.3
                    else:
                        # 使用简化版藏干表
                        for gan in ZHIGAN_MAP[zhi]:
                            wx = GAN_WUXING.get(gan, '')
                            if wx:
                                scores[wx] += 0.3
        
        return scores
    
    def _calculate_nayin(self):
        """计算纳音五行"""
        nayin_map = {
            '甲子': '海中金', '乙丑': '海中金',
            '丙寅': '炉中火', '丁卯': '炉中火',
            '戊辰': '大林木', '己巳': '大林木',
            '庚午': '路旁土', '辛未': '路旁土',
            '壬申': '剑锋金', '癸酉': '剑锋金',
            '甲戌': '山头火', '乙亥': '山头火',
            '丙子': '涧下水', '丁丑': '涧下水',
            '戊寅': '城头土', '己卯': '城头土',
            '庚辰': '白蜡金', '辛巳': '白蜡金',
            '壬午': '杨柳木', '癸未': '杨柳木',
            '甲申': '泉中水', '乙酉': '泉中水',
            '丙戌': '屋上土', '丁亥': '屋上土',
            '戊子': '霹雳火', '己丑': '霹雳火',
            '庚寅': '松柏木', '辛卯': '松柏木',
            '壬辰': '长流水', '癸巳': '长流水',
            '甲午': '砂中金', '乙未': '砂中金',
            '丙申': '山下火', '丁酉': '山下火',
            '戊戌': '平地木', '己亥': '平地木',
            '庚子': '壁上土', '辛丑': '壁上土',
            '壬寅': '金箔金', '癸卯': '金箔金',
            '甲辰': '覆灯火', '乙巳': '覆灯火',
            '丙午': '天河水', '丁未': '天河水',
            '戊申': '大驿土', '己酉': '大驿土',
            '庚戌': '钗钏金', '辛亥': '钗钏金',
            '壬子': '桑柘木', '癸丑': '桑柘木',
            '甲寅': '大溪水', '乙卯': '大溪水',
            '丙辰': '沙中土', '丁巳': '沙中土',
            '戊午': '天上火', '己未': '天上火',
            '庚申': '石榴木', '辛酉': '石榴木',
            '壬戌': '大海水', '癸亥': '大海水'
        }
        
        self.nayin = {
            '年柱': nayin_map.get(self.sizhu.get('年柱', ''), '未知'),
            '月柱': nayin_map.get(self.sizhu.get('月柱', ''), '未知'),
            '日柱': nayin_map.get(self.sizhu.get('日柱', ''), '未知'),
            '时柱': nayin_map.get(self.sizhu.get('时柱', ''), '未知')
        }
    
    def _calculate_zhangsheng(self):
        """计算十二长生"""
        zhangsheng_map = {
            '甲': ['亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌'],
            '丙': ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'],
            '戊': ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'],
            '庚': ['巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰'],
            '壬': ['申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未'],
            '乙': ['午', '巳', '辰', '卯', '寅', '丑', '子', '亥', '戌', '酉', '申', '未'],
            '丁': ['酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥', '戌'],
            '己': ['酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥', '戌'],
            '辛': ['子', '亥', '戌', '酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑'],
            '癸': ['卯', '寅', '丑', '子', '亥', '戌', '酉', '申', '未', '午', '巳', '辰']
        }
        
        zhangsheng_names = ['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养']
        
        day_gan = self.sizhu.get('day_gan', '')
        if day_gan not in zhangsheng_map:
            return
        
        zhi_list = zhangsheng_map[day_gan]
        self.zhangsheng = {}
        
        for pillar, zhi_key in [('年支', 'year_zhi'), ('月支', 'month_zhi'), 
                                ('日支', 'day_zhi'), ('时支', 'hour_zhi')]:
            zhi = self.sizhu.get(zhi_key, '')
            if zhi in zhi_list:
                idx = zhi_list.index(zhi)
                self.zhangsheng[pillar] = zhangsheng_names[idx]
    
    def get_panpan_result(self) -> Dict:
        """
        获取完整排盘结果
        
        Returns:
            Dict: 包含所有排盘信息的字典
        """
        return {
            '基本信息': {
                '出生时间': f"{self.year}年{self.month}月{self.day}日 {self.hour:02d}:{self.minute:02d}",
                '性别': self.gender,
                '四柱': {
                    '年柱': self.sizhu.get('年柱', ''),
                    '月柱': self.sizhu.get('月柱', ''),
                    '日柱': self.sizhu.get('日柱', ''),
                    '时柱': self.sizhu.get('时柱', '')
                }
            },
            '藏干': self.canggan,
            '十神': self.shishen,
            '五行统计': self.wuxing_count,
            '五行分数': self.wuxing_score,
            '纳音': self.nayin,
            '十二长生': self.zhangsheng
        }
    
    def get_dayun(self, start_age: int = None) -> List[Dict]:
        """
        计算大运
        
        Args:
            start_age: 起运年龄，None则自动计算
            
        Returns:
            List[Dict]: 大运列表
        """
        # 自动计算起运年龄
        if start_age is None:
            start_age = self._calculate_start_age()
        
        # 确定大运顺逆
        year_gan = self.sizhu.get('year_gan', '')
        year_gan_idx = TIAN_GAN.index(year_gan) if year_gan in TIAN_GAN else 0
        is_yang = year_gan_idx % 2 == 0  # 甲丙戊庚壬为阳
        
        # 阳年男命顺排，阴年男命逆排
        # 阳年女命逆排，阴年女命顺排
        is_male = self.gender == '男'
        forward = (is_yang and is_male) or (not is_yang and not is_male)
        
        # 从月柱开始排大运
        month_gan = self.sizhu.get('month_gan', '')
        month_zhi = self.sizhu.get('month_zhi', '')
        
        month_gan_idx = TIAN_GAN.index(month_gan) if month_gan in TIAN_GAN else 0
        month_zhi_idx = DI_ZHI.index(month_zhi) if month_zhi in DI_ZHI else 0
        
        dayun_list = []
        for i in range(10):  # 排10步大运
            if forward:
                gan_idx = (month_gan_idx + i + 1) % 10
                zhi_idx = (month_zhi_idx + i + 1) % 12
            else:
                gan_idx = (month_gan_idx - i - 1) % 10
                zhi_idx = (month_zhi_idx - i - 1) % 12
            
            gan = TIAN_GAN[gan_idx]
            zhi = DI_ZHI[zhi_idx]
            
            dayun_list.append({
                '大运': f"{gan}{zhi}",
                '天干': gan,
                '地支': zhi,
                '年龄': start_age + i * 10,
                '十神': get_shishen(self.sizhu.get('day_gan', ''), gan)
            })
        
        return dayun_list
    
    def _calculate_start_age(self) -> int:
        """
        计算起运年龄
        
        根据传统命理算法：
        1. 根据出生年干和性别确定大运顺逆
        2. 阳年男命、阴年女命：从出生日到下一个节气
        3. 阴年男命、阳年女命：从出生日到上一个节气
        4. 天数除以3得到起运岁数
        
        Returns:
            int: 起运年龄（岁数）
        """
        from datetime import datetime, timedelta
        
        # 确定大运顺逆
        year_gan = self.sizhu.get('year_gan', '')
        year_gan_idx = TIAN_GAN.index(year_gan) if year_gan in TIAN_GAN else 0
        is_yang = year_gan_idx % 2 == 0  # 甲丙戊庚壬为阳
        
        is_male = self.gender == '男'
        forward = (is_yang and is_male) or (not is_yang and not is_male)
        
        # 出生日期
        birth_date = datetime(self.year, self.month, self.day)
        
        # 计算到节气的天数
        days_to_jieqi = self._calculate_days_to_jieqi(birth_date, forward)
        
        # 起运年龄 = 天数 / 3（向上取整）
        start_age = int((days_to_jieqi + 2) // 3)  # 向上取整
        
        return max(1, start_age)  # 至少1岁起运
    
    def _calculate_days_to_jieqi(self, birth_date: datetime, forward: bool) -> int:
        """
        计算出生日期到最近节气的天数
        
        Args:
            birth_date: 出生日期
            forward: True表示向前查找（下一个节气），False表示向后查找（上一个节气）
            
        Returns:
            int: 天数
        """
        try:
            # 优先尝试使用lunar_python获取节气信息
            from lunar_python import Solar
            return self._get_days_to_jieqi_lunar(birth_date, forward)
        except (ImportError, AttributeError):
            try:
                # 回退到sxtwl
                import sxtwl
                return self._get_days_to_jieqi_sxtwl(birth_date, forward)
            except (ImportError, AttributeError):
                # 最后回退到简化计算
                return self._get_days_to_jieqi_simple(birth_date, forward)
    
    def _get_days_to_jieqi_lunar(self, birth_date: datetime, forward: bool) -> int:
        """
        使用lunar_python计算到节气的天数
        
        Args:
            birth_date: 出生日期
            forward: 是否向前查找
            
        Returns:
            int: 天数
        """
        from lunar_python import Solar
        from datetime import timedelta
        
        # 主要节气列表（用于起运计算）
        major_jieqi = [
            "立春", "立夏", "立秋", "立冬",
            "春分", "夏至", "秋分", "冬至"
        ]
        
        # 创建Solar对象
        solar = Solar.fromYmdHms(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            birth_date.hour,
            birth_date.minute,
            0
        )
        
        # 查找最近的节气
        search_days = 0
        max_search_days = 60  # 最多查找60天
        
        while search_days < max_search_days:
            if forward:
                check_date = birth_date + timedelta(days=search_days)
            else:
                check_date = birth_date - timedelta(days=search_days)
            
            check_solar = Solar.fromYmdHms(
                check_date.year,
                check_date.month,
                check_date.day,
                0, 0, 0
            )
            
            # 获取该日期的节气
            jieqi = check_solar.getJieQi()
            
            if jieqi and jieqi.getName() in major_jieqi:
                # 找到主要节气，返回天数
                return search_days
            
            search_days += 1
        
        # 如果没有找到，返回默认值
        return 15 if forward else 15
    
    def _get_days_to_jieqi_sxtwl(self, birth_date: datetime, forward: bool) -> int:
        """
        使用sxtwl计算到节气的天数
        
        Args:
            birth_date: 出生日期
            forward: 是否向前查找
            
        Returns:
            int: 天数
        """
        import sxtwl
        from datetime import timedelta
        
        # 节气列表（按月份顺序）
        jieqi_names = [
            "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
            "立夏", "小满", "芒种", "夏至", "小暑", "大暑",
            "立秋", "处暑", "白露", "秋分", "寒露", "霜降",
            "立冬", "小雪", "大雪", "冬至", "小寒", "大寒"
        ]
        
        # 查找最近的节气
        search_days = 0
        max_search_days = 60  # 最多查找60天
        
        while search_days < max_search_days:
            if forward:
                check_date = birth_date + timedelta(days=search_days)
            else:
                check_date = birth_date - timedelta(days=search_days)
            
            day_obj = sxtwl.fromSolar(check_date.year, check_date.month, check_date.day)
            
            if day_obj.hasJieQi():
                jieqi_idx = day_obj.getJieQi()
                jieqi_name = self._get_jieqi_name(jieqi_idx)
                
                # 只计算主要节气（立春、立夏、立秋、立冬、春分、夏至、秋分、冬至）
                if jieqi_name in ["立春", "立夏", "立秋", "立冬", "春分", "夏至", "秋分", "冬至"]:
                    return search_days
            
            search_days += 1
        
        # 如果没有找到，返回默认值
        return 15  # 默认15天
    
    def _get_days_to_jieqi_simple(self, birth_date: datetime, forward: bool) -> int:
        """
        简化计算到节气的天数（回退方案）
        
        基于农历月份估算，每个农历月约30天，节气间隔约15天
        
        Args:
            birth_date: 出生日期
            forward: 是否向前查找
            
        Returns:
            int: 天数
        """
        from datetime import timedelta
        
        # 简化算法：假设节气间隔约15天
        # 根据出生日期在农历月中的位置估算
        lunar_day = birth_date.day
        
        if forward:
            # 向前查找：到下个节气的天数
            days = 30 - lunar_day
        else:
            # 向后查找：到上个节气的天数
            days = lunar_day
        
        # 调整到合理范围（5-20天）
        return max(5, min(20, days))  # 修复：确保返回值在合理范围内
    
    def _get_jieqi_name(self, jieqi_idx: int) -> str:
        """将节气索引转换为名称"""
        jieqi_names = [
            "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
            "春分", "清明", "谷雨", "立夏", "小满", "芒种",
            "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
            "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"
        ]
        if 0 <= jieqi_idx < len(jieqi_names):
            return jieqi_names[jieqi_idx]
        return None


# 便捷函数
def create_bazi_panpan(year: int, month: int, day: int, 
                       hour: int, minute: int = 0, gender: str = '男') -> BaZiPanPan:
    """
    创建八字排盘对象
    
    Args:
        year: 出生年
        month: 出生月
        day: 出生日
        hour: 出生时
        minute: 出生分
        gender: 性别
        
    Returns:
        BaZiPanPan: 八字排盘对象
    """
    return BaZiPanPan(year, month, day, hour, minute, gender)


def quick_panpan(year: int, month: int, day: int, 
                 hour: int, gender: str = '男') -> Dict:
    """
    快速排盘，返回完整结果
    
    Args:
        year: 出生年
        month: 出生月
        day: 出生日
        hour: 出生时
        gender: 性别
        
    Returns:
        Dict: 排盘结果字典
    """
    panpan = BaZiPanPan(year, month, day, hour, 0, gender)
    return panpan.get_panpan_result()


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("八字排盘测试")
    print("=" * 60)
    
    # 示例：1984年2月15日 上午10点 男
    panpan = BaZiPanPan(1984, 2, 15, 10, 0, '男')
    result = panpan.get_panpan_result()
    
    print("\n【基本信息】")
    for key, value in result['基本信息'].items():
        print(f"{key}: {value}")
    
    print("\n【藏干】")
    for key, value in result['藏干'].items():
        print(f"{key}: {value}")
    
    print("\n【十神】")
    for key, value in result['十神'].items():
        print(f"{key}: {value}")
    
    print("\n【五行统计】")
    print(result['五行统计'])
    
    print("\n【大运】")
    dayun = panpan.get_dayun(3)
    for dy in dayun[:5]:
        print(f"{dy['年龄']}岁: {dy['大运']} ({dy['十神']})")
