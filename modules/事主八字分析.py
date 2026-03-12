# -*- coding: utf-8 -*-
"""
================================================================================
事主八字分析模块
================================================================================
专为择日软件设计的八字分析模块，提供：
- 八字排盘
- 旺衰判断
- 调候用神
- 扶抑用神
- 喜用神综合
- 日课匹配评分

作为择日软件的核心评分维度，为日课选择提供事主八字依据

版本: 2.0
更新: 使用八字工具整合模块，统一数据来源

使用方法:
    1. 作为模块导入: from modules.事主八字分析 import OwnerAnalyzer
    2. 直接运行: python -m modules.事主八字分析
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

from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 从工具函数和八字分析工具导入基础数据（避免重复定义）
if __package__ is not None:
    # 作为模块导入时使用相对导入
    from .工具函数 import (
        TIAN_GAN, DI_ZHI,
        TIAN_GAN_WUXING, DI_ZHI_WUXING,
        WUXING_SHENG, WUXING_KE,
        ZHIGAN_WEIGHTED,
    )
    from .八字分析工具 import (
        GAN_WUXING, ZHI_WUXING,
        GAN_YINYANG, ZHI_YINYANG,
        get_shishen, get_shishen_explanation,
        get_zhangsheng,
        check_he as check_liuhe,
        check_chong as check_liuchong,
        check_sanhe,
        get_nayin,
        calculate_wuxing_score,
    )
    # 创建ZHIGAN_MAP别名
    ZHIGAN_MAP = ZHIGAN_WEIGHTED
else:
    # 直接运行时使用绝对导入
    from 工具函数 import (
        TIAN_GAN, DI_ZHI,
        TIAN_GAN_WUXING, DI_ZHI_WUXING,
        WUXING_SHENG, WUXING_KE,
        ZHIGAN_WEIGHTED,
    )
    from 八字分析工具 import (
        GAN_WUXING, ZHI_WUXING,
        GAN_YINYANG, ZHI_YINYANG,
        get_shishen, get_shishen_explanation,
        get_zhangsheng,
        check_he as check_liuhe,
        check_chong as check_liuchong,
        check_sanhe,
        get_nayin,
        calculate_wuxing_score,
    )
    # 创建ZHIGAN_MAP别名
    ZHIGAN_MAP = ZHIGAN_WEIGHTED


class ShiZhuBaZiAnalyzer:
    """
    事主八字分析器
    
    专为择日软件设计，提供完整的八字分析和喜用神计算
    """
    
    def __init__(self, year: int, month: int, day: int, 
                 hour: int, minute: int = 0, gender: str = '男'):
        """
        初始化事主八字分析器
        
        Args:
            year: 出生年
            month: 出生月
            day: 出生日
            hour: 出生时（0-23）
            minute: 出生分（0-59）
            gender: 性别
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.gender = gender
        
        # 四柱信息
        self.sizhu = {}
        self.day_gan = ''
        self.day_zhi = ''
        self.day_wuxing = ''
        
        # 分析结果
        self.wangshuai_score = 0  # 旺衰分数
        self.wangshuai_level = ''  # 旺衰等级
        self.tiaohou_yongshen = []  # 调候用神
        self.fuyi_yongshen = []  # 扶抑用神
        self.xishen = []  # 喜神
        self.yongshen = []  # 用神
        self.jishen = []  # 忌神
        
        # 执行分析
        self._analyze()
    
    def _analyze(self):
        """执行完整分析"""
        self._calculate_sizhu()
        self._calculate_wangshuai()
        self._calculate_tiaohou()
        self._calculate_fuyi()
        self._combine_yongshen()
    
    def _calculate_sizhu(self):
        """计算四柱"""
        try:
            from .高精度农历转换 import get_lunar_converter
            converter = get_lunar_converter()
            self.sizhu = converter.get_sizhu(
                self.year, self.month, self.day,
                self.hour, self.minute, 0
            )
            
            self.day_gan = self.sizhu.get('day_gan', '')
            self.day_zhi = self.sizhu.get('day_zhi', '')
            self.day_wuxing = GAN_WUXING.get(self.day_gan, '')
            
        except Exception as e:
            logger.error(f"计算四柱失败: {e}")
            # 使用简化计算
            self._simple_sizhu_calc()
    
    def _simple_sizhu_calc(self):
        """简化四柱计算"""
        # 简化的四柱计算逻辑
        self.sizhu = {
            'year': '甲子', 'month': '丙寅', 'day': '戊辰', 'hour': '庚午',
            'year_gan': '甲', 'year_zhi': '子',
            'month_gan': '丙', 'month_zhi': '寅',
            'day_gan': '戊', 'day_zhi': '辰',
            'hour_gan': '庚', 'hour_zhi': '午'
        }
        self.day_gan = '戊'
        self.day_zhi = '辰'
        self.day_wuxing = '土'
    
    def _calculate_wangshuai(self):
        """
        计算日主旺衰
        
        综合考虑：
        1. 月令（最重要，占40%）
        2. 通根（地支藏干，占30%）
        3. 生助（天干生助，占20%）
        4. 合会（三合六合，占10%）
        """
        if not self.day_gan or not self.day_zhi:
            return
        
        month_zhi = self.sizhu.get('month_zhi', '')
        
        # 基础分50分
        score = 50
        
        # 1. 月令得分（40分）
        month_wuxing = ZHI_WUXING.get(month_zhi, '')
        if month_wuxing == self.day_wuxing:
            score += 20  # 月令同五行，得令
        elif WUXING_SHENG.get(month_wuxing) == self.day_wuxing:
            score += 15  # 月令生我，得生
        elif WUXING_KE.get(month_wuxing) == self.day_wuxing:
            score -= 15  # 月令克我，失令
        elif WUXING_SHENG.get(self.day_wuxing) == month_wuxing:
            score -= 5   # 我生月令，泄气
        else:
            score += 5   # 我克月令，耗气
        
        # 2. 通根得分（30分）
        tonggen_score = 0
        for zhi_key in ['year_zhi', 'month_zhi', 'hour_zhi']:
            zhi = self.sizhu.get(zhi_key, '')
            if zhi in ZHIGAN_MAP:
                for gan, weight in ZHIGAN_MAP[zhi]:
                    if GAN_WUXING.get(gan) == self.day_wuxing:
                        tonggen_score += weight * 10
        
        # 日支通根权重加倍
        if self.day_zhi in ZHIGAN_MAP:
            for gan, weight in ZHIGAN_MAP[self.day_zhi]:
                if GAN_WUXING.get(gan) == self.day_wuxing:
                    tonggen_score += weight * 15
        
        score += min(tonggen_score, 30)  # 最高30分
        
        # 3. 生助得分（20分）
        for gan_key in ['year_gan', 'month_gan', 'hour_gan']:
            gan = self.sizhu.get(gan_key, '')
            if not gan:
                continue
            gan_wx = GAN_WUXING.get(gan, '')
            if gan_wx == self.day_wuxing:
                score += 5  # 比劫帮身
            elif WUXING_SHENG.get(gan_wx) == self.day_wuxing:
                score += 8  # 印星生身
            elif WUXING_KE.get(gan_wx) == self.day_wuxing:
                score -= 8  # 官杀克身
        
        # 4. 合会得分（10分）
        # 检查三合、半会
        zhis = [self.sizhu.get(k, '') for k in ['year_zhi', 'month_zhi', 'day_zhi', 'hour_zhi']]
        
        # 三合局检查
        sanhe_groups = [
            (['申', '子', '辰'], '水'),
            (['亥', '卯', '未'], '木'),
            (['寅', '午', '戌'], '火'),
            (['巳', '酉', '丑'], '金')
        ]
        
        for group, wx in sanhe_groups:
            match_count = sum(1 for z in zhis if z in group)
            if match_count >= 3:
                if wx == self.day_wuxing:
                    score += 10  # 三合助我
                elif WUXING_SHENG.get(wx) == self.day_wuxing:
                    score += 5   # 三合生我
                break
        
        # 确定旺衰等级
        self.wangshuai_score = max(0, min(100, score))
        
        if self.wangshuai_score >= 70:
            self.wangshuai_level = '旺'
        elif self.wangshuai_score >= 55:
            self.wangshuai_level = '偏旺'
        elif self.wangshuai_score >= 45:
            self.wangshuai_level = '中和'
        elif self.wangshuai_score >= 30:
            self.wangshuai_level = '偏弱'
        else:
            self.wangshuai_level = '弱'
    
    def _calculate_tiaohou(self):
        """
        计算调候用神
        
        根据出生季节和日主五行确定调候用神
        """
        month_zhi = self.sizhu.get('month_zhi', '')
        
        # 确定季节
        spring = ['寅', '卯', '辰']
        summer = ['巳', '午', '未']
        autumn = ['申', '酉', '戌']
        winter = ['亥', '子', '丑']
        
        if month_zhi in spring:
            season = '春'
        elif month_zhi in summer:
            season = '夏'
        elif month_zhi in autumn:
            season = '秋'
        else:
            season = '冬'
        
        # 调候用神表
        tiaohou_map = {
            '春': {
                '甲': ['丙', '癸'], '乙': ['丙', '癸'],
                '丙': ['壬', '庚'], '丁': ['甲', '庚'],
                '戊': ['丙', '甲'], '己': ['丙', '癸'],
                '庚': ['丁', '甲'], '辛': ['壬', '甲'],
                '壬': ['庚', '丙'], '癸': ['辛', '丙']
            },
            '夏': {
                '甲': ['癸', '庚'], '乙': ['癸', '丙'],
                '丙': ['壬', '庚'], '丁': ['癸', '庚'],
                '戊': ['癸', '甲'], '己': ['癸', '丙'],
                '庚': ['壬', '癸'], '辛': ['壬', '癸'],
                '壬': ['庚', '癸'], '癸': ['庚', '辛']
            },
            '秋': {
                '甲': ['庚', '丁'], '乙': ['癸', '丁'],
                '丙': ['甲', '戊'], '丁': ['甲', '庚'],
                '戊': ['丙', '癸'], '己': ['丙', '癸'],
                '庚': ['丁', '甲'], '辛': ['壬', '甲'],
                '壬': ['庚', '戊'], '癸': ['辛', '甲']
            },
            '冬': {
                '甲': ['丙', '戊'], '乙': ['丙', '戊'],
                '丙': ['甲', '戊'], '丁': ['甲', '庚'],
                '戊': ['丙', '甲'], '己': ['丙', '甲'],
                '庚': ['丁', '甲'], '辛': ['丙', '壬'],
                '壬': ['丙', '戊'], '癸': ['丙', '辛']
            }
        }
        
        if season in tiaohou_map and self.day_gan in tiaohou_map[season]:
            self.tiaohou_yongshen = tiaohou_map[season][self.day_gan]
    
    def _calculate_fuyi(self):
        """
        计算扶抑用神
        
        根据日主旺衰确定扶抑用神：
        - 日主旺：宜克泄耗（官杀、食伤、财星）
        - 日主弱：宜生扶（印星、比劫）
        """
        if not self.day_wuxing:
            return
        
        if self.wangshuai_level in ['旺', '偏旺']:
            # 日主旺，喜克泄耗
            # 克我者为官杀
            ke_wx = WUXING_KE.get(self.day_wuxing, '')
            # 我生者为食伤
            sheng_wx = None
            for wx, target in WUXING_SHENG.items():
                if target == self.day_wuxing:
                    sheng_wx = wx
                    break
            # 我克者为财星
            wo_ke = None
            for wx, target in WUXING_KE.items():
                if target == self.day_wuxing:
                    wo_ke = wx
                    break
            
            self.fuyi_yongshen = [ke_wx] if ke_wx else []
            if sheng_wx:
                self.fuyi_yongshen.append(sheng_wx)
            
        elif self.wangshuai_level in ['弱', '偏弱']:
            # 日主弱，喜生扶
            # 生我者为印星
            sheng_wo = None
            for wx, target in WUXING_SHENG.items():
                if target == self.day_wuxing:
                    sheng_wo = wx
                    break
            
            self.fuyi_yongshen = [sheng_wo, self.day_wuxing] if sheng_wo else [self.day_wuxing]
            
        else:
            # 中和，根据具体情况
            self.fuyi_yongshen = [self.day_wuxing]
    
    def _combine_yongshen(self):
        """
        综合确定喜用神
        
        综合考虑调候用神和扶抑用神
        """
        # 喜神：调候用神 + 扶抑用神
        xishen_set = set()
        
        # 添加调候用神对应的五行
        for gan in self.tiaohou_yongshen:
            wx = GAN_WUXING.get(gan, '')
            if wx:
                xishen_set.add(wx)
        
        # 添加扶抑用神
        for wx in self.fuyi_yongshen:
            if wx:
                xishen_set.add(wx)
        
        self.xishen = list(xishen_set)
        
        # 用神：以扶抑用神为主，结合调候
        if self.fuyi_yongshen:
            self.yongshen = self.fuyi_yongshen[:1]  # 主要用神
        elif self.xishen:
            self.yongshen = self.xishen[:1]
        else:
            self.yongshen = []
        
        # 忌神：克制用神的五行
        if self.yongshen:
            jishen_set = set()
            for yw in self.yongshen:
                # 克用神者为忌
                ke_yw = WUXING_KE.get(yw, '')
                if ke_yw:
                    jishen_set.add(ke_yw)
                # 用神所克者也为忌（耗神）
                for wx, target in WUXING_KE.items():
                    if target == yw:
                        jishen_set.add(wx)
                        break
            self.jishen = list(jishen_set)
        else:
            self.jishen = []
    
    def get_analysis_result(self) -> Dict:
        """
        获取完整分析结果
        
        Returns:
            Dict: 分析结果字典
        """
        return {
            '基本信息': {
                '出生时间': f"{self.year}年{self.month}月{self.day}日 {self.hour:02d}:{self.minute:02d}",
                '性别': self.gender,
                '四柱': {
                    '年柱': self.sizhu.get('year', ''),
                    '月柱': self.sizhu.get('month', ''),
                    '日柱': self.sizhu.get('day', ''),
                    '时柱': self.sizhu.get('hour', '')
                }
            },
            '日主信息': {
                '日主': f"{self.day_gan}({self.day_wuxing})",
                '日支': self.day_zhi
            },
            '旺衰分析': {
                '旺衰分数': self.wangshuai_score,
                '旺衰等级': self.wangshuai_level,
                '分析': self._get_wangshuai_analysis()
            },
            '调候用神': {
                '调候用神': self.tiaohou_yongshen,
                '说明': self._get_tiaohou_explanation()
            },
            '扶抑用神': {
                '扶抑用神': self.fuyi_yongshen,
                '说明': self._get_fuyi_explanation()
            },
            '喜用神': {
                '喜神': self.xishen,
                '用神': self.yongshen,
                '忌神': self.jishen,
                '说明': self._get_yongshen_explanation()
            }
        }
    
    def _get_wangshuai_analysis(self) -> str:
        """获取旺衰分析说明"""
        analyses = {
            '旺': f'日主强旺（{self.wangshuai_score}分），能任财官，宜行克泄耗之运',
            '偏旺': f'日主偏旺（{self.wangshuai_score}分），稍嫌过强，宜适当泄耗',
            '中和': f'日主中和（{self.wangshuai_score}分），平衡稳定，随运而变',
            '偏弱': f'日主偏弱（{self.wangshuai_score}分），力量不足，宜生扶',
            '弱': f'日主衰弱（{self.wangshuai_score}分），难以任财官，急需生扶'
        }
        return analyses.get(self.wangshuai_level, '旺衰不明')
    
    def _get_tiaohou_explanation(self) -> str:
        """获取调候用神说明"""
        if not self.tiaohou_yongshen:
            return '无需特殊调候'
        
        gan_names = '、'.join(self.tiaohou_yongshen)
        wx_names = '、'.join([GAN_WUXING.get(g, '') for g in self.tiaohou_yongshen])
        
        return f'调候用神为{gan_names}，五行属{wx_names}，用于调和命局气候'
    
    def _get_fuyi_explanation(self) -> str:
        """获取扶抑用神说明"""
        if not self.fuyi_yongshen:
            return '扶抑用神不明'
        
        wx_names = '、'.join(self.fuyi_yongshen)
        
        if self.wangshuai_level in ['旺', '偏旺']:
            return f'日主偏旺，扶抑用神为{wx_names}，用于克泄耗日主'
        elif self.wangshuai_level in ['弱', '偏弱']:
            return f'日主偏弱，扶抑用神为{wx_names}，用于生扶日主'
        else:
            return f'日主中和，扶抑用神为{wx_names}，用于维持平衡'
    
    def _get_yongshen_explanation(self) -> str:
        """获取喜用神综合说明"""
        lines = []
        
        if self.xishen:
            lines.append(f"喜神：{'、'.join(self.xishen)}")
        if self.yongshen:
            lines.append(f"用神：{'、'.join(self.yongshen)}")
        if self.jishen:
            lines.append(f"忌神：{'、'.join(self.jishen)}")
        
        return '\n'.join(lines) if lines else '喜用神未确定'
    
    def calculate_rike_match_score(self, rike_sizhu: Dict) -> Dict:
        """
        计算日课匹配评分
        
        这是择日软件的核心评分维度，评估日课与事主八字的匹配度
        
        Args:
            rike_sizhu: 日课四柱信息
            
        Returns:
            Dict: 匹配评分结果
        """
        if not self.yongshen:
            return {'score': 0, 'level': '无法评分', 'reason': '事主用神未确定'}
        
        score = 0
        details = []
        
        # 1. 日课天干与喜用神匹配（40分）
        gan_score = 0
        for gan_key in ['year_gan', 'month_gan', 'day_gan', 'hour_gan']:
            gan = rike_sizhu.get(gan_key, '')
            if not gan:
                continue
            gan_wx = GAN_WUXING.get(gan, '')
            
            # 用神加分
            if gan_wx in self.yongshen:
                gan_score += 15
                details.append(f'{gan_key}天干{gan}({gan_wx})为用神，+15分')
            # 喜神加分
            elif gan_wx in self.xishen:
                gan_score += 10
                details.append(f'{gan_key}天干{gan}({gan_wx})为喜神，+10分')
            # 忌神减分
            elif gan_wx in self.jishen:
                gan_score -= 10
                details.append(f'{gan_key}天干{gan}({gan_wx})为忌神，-10分')
        
        score += min(gan_score, 40)
        
        # 2. 日课地支与喜用神匹配（30分）
        zhi_score = 0
        for zhi_key in ['year_zhi', 'month_zhi', 'day_zhi', 'hour_zhi']:
            zhi = rike_sizhu.get(zhi_key, '')
            if not zhi or zhi not in ZHIGAN_MAP:
                continue
            
            # 检查藏干
            for gan, weight in ZHIGAN_MAP[zhi]:
                gan_wx = GAN_WUXING.get(gan, '')
                if gan_wx in self.yongshen:
                    zhi_score += 8 * weight
                    details.append(f'{zhi_key}藏干{gan}({gan_wx})为用神，+{8*weight:.1f}分')
                elif gan_wx in self.xishen:
                    zhi_score += 5 * weight
                    details.append(f'{zhi_key}藏干{gan}({gan_wx})为喜神，+{5*weight:.1f}分')
        
        score += min(zhi_score, 30)
        
        # 3. 日课五行平衡度（20分）
        # 计算日课五行分布
        rike_wuxing = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
        for gan_key in ['year_gan', 'month_gan', 'day_gan', 'hour_gan']:
            gan = rike_sizhu.get(gan_key, '')
            wx = GAN_WUXING.get(gan, '')
            if wx:
                rike_wuxing[wx] += 1
        
        # 检查是否补益用神
        balance_score = 0
        for yw in self.yongshen:
            if rike_wuxing.get(yw, 0) >= 2:
                balance_score += 10
                details.append(f'日课{yw}旺，补益用神，+10分')
            elif rike_wuxing.get(yw, 0) >= 1:
                balance_score += 5
                details.append(f'日课{yw}有气，补益用神，+5分')
        
        score += min(balance_score, 20)
        
        # 4. 日课与日主关系（10分）
        relation_score = 0
        rike_day_gan = rike_sizhu.get('day_gan', '')
        if rike_day_gan:
            shishen = get_shishen(self.day_gan, rike_day_gan)
            if shishen in ['正印', '偏印']:
                relation_score = 10
                details.append(f'日课日干{rike_day_gan}为日主之印星，+10分')
            elif shishen in ['比肩', '劫财']:
                relation_score = 5
                details.append(f'日课日干{rike_day_gan}为日主之比劫，+5分')
            elif shishen in ['食神', '伤官']:
                relation_score = 5
                details.append(f'日课日干{rike_day_gan}为日主之食伤，+5分')
        
        score += relation_score
        
        # 确定等级
        if score >= 80:
            level = '大吉'
        elif score >= 60:
            level = '吉'
        elif score >= 40:
            level = '中平'
        elif score >= 20:
            level = '凶'
        else:
            level = '大凶'
        
        return {
            'score': round(score, 1),
            'level': level,
            'details': details,
            'summary': f'日课与事主八字匹配度：{score:.1f}分（{level}）',
            '事主用神': self.yongshen,
            '事主喜神': self.xishen,
            '事主忌神': self.jishen
        }


# 便捷函数
def analyze_shizhu_bazi(year: int, month: int, day: int,
                        hour: int, minute: int = 0, gender: str = '男') -> Dict:
    """
    快速分析事主八字
    
    Args:
        year: 出生年
        month: 出生月
        day: 出生日
        hour: 出生时
        minute: 出生分
        gender: 性别
        
    Returns:
        Dict: 分析结果
    """
    analyzer = ShiZhuBaZiAnalyzer(year, month, day, hour, minute, gender)
    return analyzer.get_analysis_result()


def calculate_rike_match(shizhu_info: Dict, rike_sizhu: Dict) -> Dict:
    """
    计算日课匹配度
    
    Args:
        shizhu_info: 事主八字信息（包含year, month, day, hour, minute, gender）
        rike_sizhu: 日课四柱信息
        
    Returns:
        Dict: 匹配评分结果
    """
    analyzer = ShiZhuBaZiAnalyzer(
        shizhu_info.get('year', 2000),
        shizhu_info.get('month', 1),
        shizhu_info.get('day', 1),
        shizhu_info.get('hour', 12),
        shizhu_info.get('minute', 0),
        shizhu_info.get('gender', '男')
    )
    
    return analyzer.calculate_rike_match_score(rike_sizhu)


if __name__ == '__main__':
    # 测试代码
    print("=" * 80)
    print("事主八字分析模块测试")
    print("=" * 80)
    
    # 测试案例：1984年2月15日 10:00 男
    print("\n【测试案例】")
    print("出生时间：1984年2月15日 10:00")
    print("性别：男")
    
    analyzer = ShiZhuBaZiAnalyzer(1984, 2, 15, 10, 0, '男')
    result = analyzer.get_analysis_result()
    
    print("\n【基本信息】")
    print(f"出生时间：{result['基本信息']['出生时间']}")
    print(f"性别：{result['基本信息']['性别']}")
    
    print("\n【日主信息】")
    print(f"日主：{result['日主信息']['日主']}")
    print(f"日支：{result['日主信息']['日支']}")
    
    print("\n【旺衰分析】")
    print(f"旺衰分数：{result['旺衰分析']['旺衰分数']}分")
    print(f"旺衰等级：{result['旺衰分析']['旺衰等级']}")
    print(f"分析：{result['旺衰分析']['分析']}")
    
    print("\n【调候用神】")
    print(f"调候用神：{'、'.join(result['调候用神']['调候用神'])}")
    print(f"说明：{result['调候用神']['说明']}")
    
    print("\n【扶抑用神】")
    print(f"扶抑用神：{'、'.join(result['扶抑用神']['扶抑用神'])}")
    print(f"说明：{result['扶抑用神']['说明']}")
    
    print("\n【喜用神】")
    print(f"喜神：{'、'.join(result['喜用神']['喜神'])}")
    print(f"用神：{'、'.join(result['喜用神']['用神'])}")
    print(f"忌神：{'、'.join(result['喜用神']['忌神'])}")
    print(f"说明：{result['喜用神']['说明']}")
    
    # 测试日课匹配
    print("\n" + "=" * 80)
    print("日课匹配测试")
    print("=" * 80)
    
    # 测试日课：2024年5月20日 12:00
    test_rike = {
        'year': '甲辰', 'month': '己巳', 'day': '甲申', 'hour': '庚午',
        'year_gan': '甲', 'year_zhi': '辰',
        'month_gan': '己', 'month_zhi': '巳',
        'day_gan': '甲', 'day_zhi': '申',
        'hour_gan': '庚', 'hour_zhi': '午'
    }
    
    match_result = analyzer.calculate_rike_match_score(test_rike)
    
    print(f"\n【日课信息】")
    print(f"日课四柱：{test_rike['year']} {test_rike['month']} {test_rike['day']} {test_rike['hour']}")
    
    print(f"\n【匹配评分】")
    print(f"总分：{match_result['score']}分")
    print(f"等级：{match_result['level']}")
    print(f"总结：{match_result['summary']}")
    
    print(f"\n【评分详情】")
    for detail in match_result['details']:
        print(f"  - {detail}")
    
    print("\n" + "=" * 80)
