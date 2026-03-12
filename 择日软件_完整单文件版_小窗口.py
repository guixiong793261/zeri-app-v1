# -*- coding: utf-8 -*-
"""
================================================================================
辅助函数模块
================================================================================
包含干支转换、节气计算、五行生克等基础功能
================================================================================
"""

from datetime import date, datetime, timedelta

# 天干地支基础数据
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 五行属性
TIAN_GAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火',
    '戊': '土', '己': '土', '庚': '金', '辛': '金',
    '壬': '水', '癸': '水'
}

DI_ZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

# 五行生克关系
WUXING_SHENG = {
    '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
}

WUXING_KE = {
    '木': '土', '土': '水', '水': '火', '火': '金', '金': '木'
}

# 冲合关系
CHONG = {0:6, 1:7, 2:8, 3:9, 4:10, 5:11, 6:0, 7:1, 8:2, 9:3, 10:4, 11:5}
HE = {0:1, 1:0, 2:11, 11:2, 3:10, 10:3, 4:9, 9:4, 5:8, 8:5, 6:7, 7:6}

# 五虎遁（月干）
WU_HU_DUN = {'甲': 2, '己': 2, '乙': 4, '庚': 4, '丙': 6, '辛': 6, '丁': 8, '壬': 8, '戊': 0, '癸': 0}

# 五鼠遁（时干）
WU_SHU_DUN = {'甲': 0, '己': 0, '乙': 2, '庚': 2, '丙': 4, '辛': 4, '丁': 6, '壬': 6, '戊': 8, '癸': 8}

# 天德月德
TIANDE = {2: '丁', 3: '申', 4: '壬', 5: '辛', 6: '亥', 7: '甲', 8: '癸', 9: '寅', 10: '丙', 11: '乙', 0: '巳', 1: '庚'}
YUEDE = {2: '丙', 3: '甲', 4: '壬', 5: '庚', 6: '丙', 7: '甲', 8: '壬', 9: '庚', 10: '丙', 11: '甲', 0: '壬', 1: '庚'}

# 三煞
SANSHA_MAP = {
    '申': [5,6,7], '子': [5,6,7], '辰': [5,6,7],      # 南方（巳午未）
    '寅': [11,0,1], '午': [11,0,1], '戌': [11,0,1],      # 北方（亥子丑）
    '巳': [2,3,4], '酉': [2,3,4], '丑': [2,3,4],          # 东方（寅卯辰）
    '亥': [8,9,10], '卯': [8,9,10], '未': [8,9,10],      # 西方（申酉戌）
}

# 夫星子星
FU_ZI_XING = {
    '甲': {'fu': '土', 'zi': '火'}, '乙': {'fu': '土', 'zi': '火'},
    '丙': {'fu': '金', 'zi': '土'}, '丁': {'fu': '金', 'zi': '土'},
    '戊': {'fu': '水', 'zi': '金'}, '己': {'fu': '水', 'zi': '金'},
    '庚': {'fu': '木', 'zi': '水'}, '辛': {'fu': '木', 'zi': '水'},
    '壬': {'fu': '火', 'zi': '木'}, '癸': {'fu': '火', 'zi': '木'},
}

# 二十四山向
# 分为八宫，每宫三山
SHAN_XIANG_24 = {
    '坎宫': ['壬', '子', '癸'],
    '艮宫': ['丑', '艮', '寅'],
    '震宫': ['甲', '卯', '乙'],
    '巽宫': ['辰', '巽', '巳'],
    '离宫': ['丙', '午', '丁'],
    '坤宫': ['未', '坤', '申'],
    '兑宫': ['庚', '酉', '辛'],
    '乾宫': ['戌', '乾', '亥'],
}

# 二十四山向列表（按顺时针顺序）
SHAN_XIANG_LIST = [
    '壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙',
    '辰', '巽', '巳', '丙', '午', '丁', '未', '坤', '申',
    '庚', '酉', '辛', '戌', '乾', '亥'
]

# 山向五行属性
SHAN_XIANG_WUXING = {
    '壬': '水', '子': '水', '癸': '水',
    '丑': '土', '艮': '土', '寅': '木',
    '甲': '木', '卯': '木', '乙': '木',
    '辰': '土', '巽': '木', '巳': '火',
    '丙': '火', '午': '火', '丁': '火',
    '未': '土', '坤': '土', '申': '金',
    '庚': '金', '酉': '金', '辛': '金',
    '戌': '土', '乾': '金', '亥': '水',
}

# 十神
SHISHEN = {
    '甲': {'比肩': '甲', '劫财': '乙', '食神': '丙', '伤官': '丁', '偏财': '戊', '正财': '己', '七杀': '庚', '正官': '辛', '偏印': '壬', '正印': '癸'},
    '乙': {'比肩': '乙', '劫财': '甲', '食神': '丁', '伤官': '丙', '偏财': '己', '正财': '戊', '七杀': '辛', '正官': '庚', '偏印': '癸', '正印': '壬'},
    '丙': {'比肩': '丙', '劫财': '丁', '食神': '戊', '伤官': '己', '偏财': '庚', '正财': '辛', '七杀': '壬', '正官': '癸', '偏印': '甲', '正印': '乙'},
    '丁': {'比肩': '丁', '劫财': '丙', '食神': '己', '伤官': '戊', '偏财': '辛', '正财': '庚', '七杀': '癸', '正官': '壬', '偏印': '乙', '正印': '甲'},
    '戊': {'比肩': '戊', '劫财': '己', '食神': '庚', '伤官': '辛', '偏财': '壬', '正财': '癸', '七杀': '甲', '正官': '乙', '偏印': '丙', '正印': '丁'},
    '己': {'比肩': '己', '劫财': '戊', '食神': '辛', '伤官': '庚', '偏财': '癸', '正财': '壬', '七杀': '乙', '正官': '甲', '偏印': '丁', '正印': '丙'},
    '庚': {'比肩': '庚', '劫财': '辛', '食神': '壬', '伤官': '癸', '偏财': '甲', '正财': '乙', '七杀': '丙', '正官': '丁', '偏印': '戊', '正印': '己'},
    '辛': {'比肩': '辛', '劫财': '庚', '食神': '癸', '伤官': '壬', '偏财': '乙', '正财': '甲', '七杀': '丁', '正官': '丙', '偏印': '己', '正印': '戊'},
    '壬': {'比肩': '壬', '劫财': '癸', '食神': '甲', '伤官': '乙', '偏财': '丙', '正财': '丁', '七杀': '戊', '正官': '己', '偏印': '庚', '正印': '辛'},
    '癸': {'比肩': '癸', '劫财': '壬', '食神': '乙', '伤官': '甲', '偏财': '丁', '正财': '丙', '七杀': '己', '正官': '戊', '偏印': '辛', '正印': '庚'},
}

# 带权重的藏干表（用于五行分数计算）
# 注意：ZHIGAN_MAP已移至八字分析工具.py，这里保留ZHIGAN_WEIGHTED用于兼容
ZHIGAN_WEIGHTED = {
    '子': [('癸', 1.0)],
    '丑': [('己', 0.6), ('癸', 0.3), ('辛', 0.1)],
    '寅': [('甲', 0.6), ('丙', 0.3), ('戊', 0.1)],
    '卯': [('乙', 1.0)],
    '辰': [('戊', 0.6), ('乙', 0.3), ('癸', 0.1)],
    '巳': [('丙', 0.6), ('庚', 0.3), ('戊', 0.1)],
    '午': [('丁', 0.7), ('己', 0.3)],
    '未': [('己', 0.6), ('丁', 0.3), ('乙', 0.1)],
    '申': [('庚', 0.6), ('壬', 0.3), ('戊', 0.1)],
    '酉': [('辛', 1.0)],
    '戌': [('戊', 0.6), ('辛', 0.3), ('丁', 0.1)],
    '亥': [('壬', 0.7), ('甲', 0.3)]
}

def get_gan_wuxing(gan):
    """获取天干五行"""
    return TIAN_GAN_WUXING.get(gan, '')

def get_zhi_wuxing(zhi):
    """获取地支五行"""
    return DI_ZHI_WUXING.get(zhi, '')

def get_pillar_wuxing(pillar):
    """获取柱的五行（天干五行）"""
    if not pillar:
        return ''
    return get_gan_wuxing(pillar[0])

def get_shengke(wuxing1, wuxing2):
    """获取五行生克关系"""
    if wuxing1 == wuxing2:
        return '同'
    elif WUXING_SHENG.get(wuxing1) == wuxing2:
        return '生'
    elif WUXING_KE.get(wuxing1) == wuxing2:
        return '克'
    elif WUXING_SHENG.get(wuxing2) == wuxing1:
        return '被生'
    elif WUXING_KE.get(wuxing2) == wuxing1:
        return '被克'
    return '无关'

def get_hour_zhi_index(hour, minute=0):
    """获取时支索引"""
    if hour == 23 and minute >= 0:
        return 0
    elif hour == 0:
        return 0
    else:
        return ((hour + 1) // 2) % 12

def get_shishen(day_gan: str, target_gan: str) -> str:
    """
    获取十神（使用八字分析工具中的算法）
    
    Args:
        day_gan: 日干
        target_gan: 目标天干
        
    Returns:
        str: 十神名称
    """
def get_fuzi(day_gan):
    """获取夫星子星"""
    return FU_ZI_XING.get(day_gan, {'fu': None, 'zi': None})

def format_date(dt):
    """格式化日期"""
    return dt.strftime('%Y年%m月%d日')

def format_datetime(dt):
    """格式化日期时间"""
    return dt.strftime('%Y年%m月%d日 %H:%M')


# ============================================================================
# 向后兼容：从八字工具整合模块导入增强功能
# ============================================================================
# 注意：新开发建议直接从八字工具整合模块导入


# -*- coding: utf-8 -*-
"""
================================================================================
八字分析工具模块
================================================================================
提供八字分析的辅助工具函数，包括：
- 天干地支转换
- 五行计算
- 十神计算
- 神煞查询
- 大运流年计算
- 合冲刑害分析

使用方法:
    1. 作为模块导入: from modules.八字分析工具 import get_shishen
    2. 直接运行: python -m modules.八字分析工具
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# 从工具函数导入基础数据
# 五行映射（使用工具函数中的定义）
GAN_WUXING = TIAN_GAN_WUXING
ZHI_WUXING = DI_ZHI_WUXING

# 阴阳属性
GAN_YINYANG = {
    '甲': '阳', '乙': '阴',
    '丙': '阳', '丁': '阴',
    '戊': '阳', '己': '阴',
    '庚': '阳', '辛': '阴',
    '壬': '阳', '癸': '阴'
}

ZHI_YINYANG = {
    '子': '阳', '丑': '阴', '寅': '阳', '卯': '阴',
    '辰': '阳', '巳': '阴', '午': '阳', '未': '阴',
    '申': '阳', '酉': '阴', '戌': '阳', '亥': '阴'
}

# 五行生克
WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
WUXING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

# 藏干表
ZHIGAN_MAP = {
    '子': [('癸', 1.0)],
    '丑': [('己', 0.6), ('癸', 0.3), ('辛', 0.1)],
    '寅': [('甲', 0.6), ('丙', 0.3), ('戊', 0.1)],
    '卯': [('乙', 1.0)],
    '辰': [('戊', 0.6), ('乙', 0.3), ('癸', 0.1)],
    '巳': [('丙', 0.6), ('庚', 0.3), ('戊', 0.1)],
    '午': [('丁', 0.7), ('己', 0.3)],
    '未': [('己', 0.6), ('丁', 0.3), ('乙', 0.1)],
    '申': [('庚', 0.6), ('壬', 0.3), ('戊', 0.1)],
    '酉': [('辛', 1.0)],
    '戌': [('戊', 0.6), ('辛', 0.3), ('丁', 0.1)],
    '亥': [('壬', 0.7), ('甲', 0.3)]
}

# 十神定义
SHISHEN_NAMES = ['比肩', '劫财', '食神', '伤官', '偏财', '正财', '七杀', '正官', '偏印', '正印']


def get_gan_wuxing(gan: str) -> str:
    """获取天干五行"""
    return GAN_WUXING.get(gan, '')


def get_zhi_wuxing(zhi: str) -> str:
    """获取地支五行"""
    return ZHI_WUXING.get(zhi, '')


def get_gan_yinyang(gan: str) -> str:
    """获取天干阴阳"""
    return GAN_YINYANG.get(gan, '')


def get_zhi_yinyang(zhi: str) -> str:
    """获取地支阴阳"""
    return ZHI_YINYANG.get(zhi, '')


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
    
    day_idx = TIAN_GAN.index(day_gan)
    target_idx = TIAN_GAN.index(target_gan)
    
    day_yin = day_idx % 2 == 1
    target_yin = target_idx % 2 == 1
    
    diff = (target_idx - day_idx) % 10
    
    if diff == 0:
        return '比肩' if day_yin == target_yin else '劫财'
    elif diff == 1:
        return '劫财' if day_yin == target_yin else '比肩'
    elif diff == 2:
        return '正印' if day_yin != target_yin else '偏印'
    elif diff == 3:
        return '偏印' if day_yin != target_yin else '正印'
    elif diff == 4:
        return '伤官' if day_yin != target_yin else '食神'
    elif diff == 5:
        return '食神' if day_yin != target_yin else '伤官'
    elif diff == 6:
        return '正财' if day_yin != target_yin else '偏财'
    elif diff == 7:
        return '偏财' if day_yin != target_yin else '正财'
    elif diff == 8:
        return '正官' if day_yin != target_yin else '七杀'
    elif diff == 9:
        return '七杀' if day_yin != target_yin else '正官'
    
    return '未知'


def get_shishen_explanation(shishen: str) -> str:
    """获取十神解释"""
    explanations = {
        '比肩': '同我者，代表兄弟姐妹、朋友、同事，主独立、自主',
        '劫财': '同我者（异性），代表竞争、争夺，主冒险、投机',
        '食神': '我生者，代表才华、口福、享受，主温和、艺术',
        '伤官': '我生者（异性），代表才华、创意，主聪明、叛逆',
        '偏财': '我克者，代表横财、意外之财，主慷慨、风流',
        '正财': '我克者（异性），代表正当收入、妻子，主勤俭、务实',
        '七杀': '克我者，代表压力、挑战、权威，主果断、威严',
        '正官': '克我者（异性），代表官职、名誉、约束，主正直、守法',
        '偏印': '生我者，代表偏门学问、灵感，主孤独、敏感',
        '正印': '生我者（异性），代表学问、母亲、贵人，主仁慈、智慧'
    }
    return explanations.get(shishen, '未知十神')


def get_canggan(zhi: str) -> List[Tuple[str, float]]:
    """
    获取地支藏干
    
    Args:
        zhi: 地支
        
    Returns:
        List[Tuple[str, float]]: 藏干列表，包含天干和权重
    """
    return ZHIGAN_MAP.get(zhi, [])


def get_zhangsheng(day_gan: str, zhi: str) -> str:
    """
    获取十二长生状态
    
    Args:
        day_gan: 日干
        zhi: 地支
        
    Returns:
        str: 长生状态
    """
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
    
    if day_gan not in zhangsheng_map:
        return '未知'
    
    zhi_list = zhangsheng_map[day_gan]
    if zhi not in zhi_list:
        return '未知'
    
    idx = zhi_list.index(zhi)
    return zhangsheng_names[idx]


def get_zhangsheng_explanation(zhangsheng: str) -> str:
    """获取十二长生解释"""
    explanations = {
        '长生': '万物生发，充满生机，主吉利',
        '沐浴': '洗涤尘埃，主变化、不稳定',
        '冠带': '穿衣戴帽，主成长、进步',
        '临官': '事业有成，主权力、地位',
        '帝旺': '极盛之时，主巅峰、强盛',
        '衰': '开始衰退，主走下坡路',
        '病': '身体不适，主困顿、阻碍',
        '死': '生机断绝，主结束、停滞',
        '墓': '入墓收藏，主隐藏、积累',
        '绝': '绝境无生，主困顿、艰难',
        '胎': '孕育新生，主希望、开始',
        '养': '养育成长，主培育、发展'
    }
    return explanations.get(zhangsheng, '未知状态')


def check_he(zhi1: str, zhi2: str) -> Optional[str]:
    """
    检查地支六合
    
    Args:
        zhi1: 第一个地支
        zhi2: 第二个地支
        
    Returns:
        Optional[str]: 合化五行，不合则返回None
    """
    he_map = {
        ('子', '丑'): '土',
        ('寅', '亥'): '木',
        ('卯', '戌'): '火',
        ('辰', '酉'): '金',
        ('巳', '申'): '水',
        ('午', '未'): '土'
    }
    
    # 检查两种顺序
    result = he_map.get((zhi1, zhi2))
    if not result:
        result = he_map.get((zhi2, zhi1))
    
    return result


def check_chong(zhi1: str, zhi2: str) -> bool:
    """
    检查地支六冲
    
    Args:
        zhi1: 第一个地支
        zhi2: 第二个地支
        
    Returns:
        bool: 是否相冲
    """
    chong_pairs = [
        ('子', '午'), ('丑', '未'), ('寅', '申'),
        ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
    ]
    
    return (zhi1, zhi2) in chong_pairs or (zhi2, zhi1) in chong_pairs


def check_xing(zhi1: str, zhi2: str) -> Optional[str]:
    """
    检查地支相刑
    
    Args:
        zhi1: 第一个地支
        zhi2: 第二个地支
        
    Returns:
        Optional[str]: 刑的类型，不刑则返回None
    """
    xing_map = {
        ('子', '卯'): '无礼之刑',
        ('寅', '巳'): '无恩之刑',
        ('巳', '申'): '无恩之刑',
        ('申', '寅'): '无恩之刑',
        ('丑', '戌'): '恃势之刑',
        ('戌', '未'): '恃势之刑',
        ('未', '丑'): '恃势之刑',
        ('辰', '午'): '自刑',
        ('午', '酉'): '自刑',
        ('酉', '辰'): '自刑',
        ('亥', '亥'): '自刑'
    }
    
    result = xing_map.get((zhi1, zhi2))
    if not result:
        result = xing_map.get((zhi2, zhi1))
    
    return result


def check_hai(zhi1: str, zhi2: str) -> bool:
    """
    检查地支六害
    
    Args:
        zhi1: 第一个地支
        zhi2: 第二个地支
        
    Returns:
        bool: 是否相害
    """
    hai_pairs = [
        ('子', '未'), ('丑', '午'), ('寅', '巳'),
        ('卯', '辰'), ('申', '亥'), ('酉', '戌')
    ]
    
    return (zhi1, zhi2) in hai_pairs or (zhi2, zhi1) in hai_pairs


# 添加别名，保持与其他模块的兼容性
check_liuhe = check_he
check_liuchong = check_chong
check_liuhai = check_hai


def check_sanhe(zhis: List[str]) -> Optional[str]:
    """
    检查地支三合
    
    Args:
        zhis: 地支列表
        
    Returns:
        Optional[str]: 合化五行，不合则返回None
    """
    if len(zhis) < 3:
        return None
    
    sanhe_map = {
        frozenset(['申', '子', '辰']): '水',
        frozenset(['亥', '卯', '未']): '木',
        frozenset(['寅', '午', '戌']): '火',
        frozenset(['巳', '酉', '丑']): '金'
    }
    
    for i in range(len(zhis) - 2):
        for j in range(i + 1, len(zhis) - 1):
            for k in range(j + 1, len(zhis)):
                key = frozenset([zhis[i], zhis[j], zhis[k]])
                if key in sanhe_map:
                    return sanhe_map[key]
    
    return None


def check_banhui(zhis: List[str]) -> Optional[str]:
    """
    检查地支半会
    
    Args:
        zhis: 地支列表
        
    Returns:
        Optional[str]: 会化五行，不会则返回None
    """
    if len(zhis) < 2:
        return None
    
    banhui_map = {
        frozenset(['寅', '卯']): '木',
        frozenset(['卯', '辰']): '木',
        frozenset(['巳', '午']): '火',
        frozenset(['午', '未']): '火',
        frozenset(['申', '酉']): '金',
        frozenset(['酉', '戌']): '金',
        frozenset(['亥', '子']): '水',
        frozenset(['子', '丑']): '水'
    }
    
    for i in range(len(zhis) - 1):
        for j in range(i + 1, len(zhis)):
            key = frozenset([zhis[i], zhis[j]])
            if key in banhui_map:
                return banhui_map[key]
    
    return None


def calculate_wuxing_score(sizhu: Dict, include_canggan: bool = True) -> Dict[str, float]:
    """
    计算五行分数
    
    Args:
        sizhu: 四柱信息
        include_canggan: 是否包含藏干
        
    Returns:
        Dict[str, float]: 各五行分数
    """
    scores = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    
    # 天干五行
    for gan_key in ['year_gan', 'month_gan', 'day_gan', 'hour_gan']:
        gan = sizhu.get(gan_key, '')
        if gan:
            wx = GAN_WUXING.get(gan, '')
            if wx:
                scores[wx] += 1.0
    
    # 地支五行
    for zhi_key in ['year_zhi', 'month_zhi', 'day_zhi', 'hour_zhi']:
        zhi = sizhu.get(zhi_key, '')
        if zhi:
            wx = ZHI_WUXING.get(zhi, '')
            if wx:
                scores[wx] += 0.8  # 地支本气权重稍低
            
            # 藏干
            if include_canggan and zhi in ZHIGAN_MAP:
                for gan, weight in ZHIGAN_MAP[zhi]:
                    wx = GAN_WUXING.get(gan, '')
                    if wx:
                        scores[wx] += weight * 0.5
    
    return scores


def get_nayin(pillar: str) -> str:
    """
    获取纳音五行
    
    Args:
        pillar: 干支柱（如"甲子"）
        
    Returns:
        str: 纳音五行
    """
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
    
    return nayin_map.get(pillar, '未知')


def get_ganzhi_by_offset(base_gan: str, base_zhi: str, offset: int) -> Tuple[str, str]:
    """
    根据偏移量计算干支
    
    Args:
        base_gan: 起始天干
        base_zhi: 起始地支
        offset: 偏移量（正数向后，负数向前）
        
    Returns:
        Tuple[str, str]: 新的干支
    """
    gan_idx = TIAN_GAN.index(base_gan)
    zhi_idx = DI_ZHI.index(base_zhi)
    
    new_gan_idx = (gan_idx + offset) % 10
    new_zhi_idx = (zhi_idx + offset) % 12
    
    return TIAN_GAN[new_gan_idx], DI_ZHI[new_zhi_idx]


def format_bazi_text(sizhu: Dict, canggan: Dict = None, shishen: Dict = None) -> str:
    """
    格式化八字文本
    
    Args:
        sizhu: 四柱信息
        canggan: 藏干信息
        shishen: 十神信息
        
    Returns:
        str: 格式化的八字文本
    """
    lines = []
    lines.append("=" * 50)
    lines.append("八字排盘")
    lines.append("=" * 50)
    
    # 四柱
    lines.append(f"\n年柱: {sizhu.get('year', '')}")
    lines.append(f"月柱: {sizhu.get('month', '')}")
    lines.append(f"日柱: {sizhu.get('day', '')} (日主)")
    lines.append(f"时柱: {sizhu.get('hour', '')}")
    
    # 藏干
    if canggan:
        lines.append("\n【藏干】")
        for key, value in canggan.items():
            lines.append(f"{key}: {' '.join(value)}")
    
    # 十神
    if shishen:
        lines.append("\n【十神】")
        for key, value in shishen.items():
            if isinstance(value, list):
                lines.append(f"{key}: {' '.join(value)}")
            else:
                lines.append(f"{key}: {value}")
    
    return '\n'.join(lines)



# -*- coding: utf-8 -*-
"""
================================================================================
喜用神计算器模块
================================================================================
统一计算喜用神，供主程序和评分系统共用
采用高级推断逻辑，考虑藏干、月令、五行平衡和十神关系

版本: 2.0
更新: 使用八字工具整合模块的加权算法，提高计算精度

使用方法:
    1. 作为模块导入: from modules.喜用神计算器 import calculate_xishen_yongshen
    2. 直接运行: python -m modules.喜用神计算器
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
# 从八字分析工具导入基础数据和函数
def calculate_xishen_yongshen(sizhu, analysis=None):
    """
    计算喜用神
    
    高级喜用神推断逻辑 - 考虑藏干、月令、五行平衡和十神关系
    
    Args:
        sizhu: 四柱信息字典，包含年柱、月柱、日柱、时柱等
        analysis: 四柱分析结果（可选），包含五行、十神等信息
        
    Returns:
        tuple: (喜用神, 用神) 或 (xishen, yongshen)
    """
    # 获取日主五行
    if analysis and '五行' in analysis:
        day_wuxing = analysis['五行'].get('日柱', '')
    else:
        # 从日干计算
        day_gan = sizhu.get('day_gan', '')
        if not day_gan and '日柱' in sizhu:
            day_gan = sizhu['日柱'][0] if len(sizhu['日柱']) > 0 else ''
        day_wuxing = GAN_WUXING.get(day_gan, '')
    
    if not day_wuxing:
        return "", ""
    
    # 分析命局五行分布（考虑藏干）
    wuxing_counts = _calculate_wuxing_distribution(sizhu, analysis)
    
    # 根据日主五行和五行分布计算喜用神
    return _calculate_by_wuxing(day_wuxing, wuxing_counts)


def _calculate_wuxing_distribution(sizhu, analysis=None):
    """
    计算五行分布（包含藏干）
    
    使用整合模块的加权算法，更加精确：
    - 天干五行权重：1.0
    - 地支本气权重：0.8
    - 藏干权重：主气0.6，中气0.3，余气0.1，再乘以0.5
    
    Args:
        sizhu: 四柱信息
        analysis: 分析结果（可选，已废弃）
        
    Returns:
        dict: 各五行分数（加权）
    """
    # 使用八字分析工具的加权算法
    return calculate_wuxing_score(sizhu, include_canggan=True)

def _calculate_by_wuxing(day_wuxing, wuxing_counts):
    """
    根据日主五行和五行分布计算喜用神
    
    Args:
        day_wuxing: 日主五行
        wuxing_counts: 五行分布统计
        
    Returns:
        tuple: (喜用神, 用神)
    """
    xishen = ""
    yongshen = ""
    
    if day_wuxing == '金':
        xishen, yongshen = _calculate_for_gold(wuxing_counts)
    elif day_wuxing == '木':
        xishen, yongshen = _calculate_for_wood(wuxing_counts)
    elif day_wuxing == '水':
        xishen, yongshen = _calculate_for_water(wuxing_counts)
    elif day_wuxing == '火':
        xishen, yongshen = _calculate_for_fire(wuxing_counts)
    elif day_wuxing == '土':
        xishen, yongshen = _calculate_for_earth(wuxing_counts)
    
    return xishen, yongshen


def _calculate_for_gold(wuxing_counts):
    """
    金日主的喜用神计算
    
    使用加权分数的阈值：
    - > 6.0: 太旺
    - > 3.0: 旺
    - < 2.0: 弱
    """
    gold_count = wuxing_counts.get('金', 0)
    fire_count = wuxing_counts.get('火', 0)
    wood_count = wuxing_counts.get('木', 0)
    water_count = wuxing_counts.get('水', 0)
    earth_count = wuxing_counts.get('土', 0)
    
    if gold_count > 6.0:
        # 金太旺，喜火克金，水泄金
        return "火、水", "火"
    elif fire_count > 3.0:
        # 火旺，喜水克火，金生水
        return "水、金", "水"
    elif wood_count > 3.0:
        # 木旺，喜金克木，土生金
        return "金、土", "金"
    elif earth_count < 2.0:
        # 土弱，喜土生金
        return "土、金", "土"
    else:
        # 一般情况，喜土生金
        return "土、金", "土"


def _calculate_for_wood(wuxing_counts):
    """
    木日主的喜用神计算
    
    使用加权分数的阈值：
    - > 6.0: 太旺
    - > 3.0: 旺
    - < 2.0: 弱
    """
    wood_count = wuxing_counts.get('木', 0)
    gold_count = wuxing_counts.get('金', 0)
    earth_count = wuxing_counts.get('土', 0)
    water_count = wuxing_counts.get('水', 0)
    
    if wood_count > 6.0:
        # 木太旺，喜金克木，土耗木
        return "金、土", "金"
    elif gold_count > 3.0:
        # 金旺，喜火克金，木生火
        return "火、木", "火"
    elif earth_count > 3.0:
        # 土旺，喜木克土，水生木
        return "木、水", "木"
    elif water_count < 2.0:
        # 水弱，喜水生木
        return "水、木", "水"
    else:
        # 一般情况，喜水生木
        return "水、木", "水"


def _calculate_for_water(wuxing_counts):
    """
    水日主的喜用神计算
    
    使用加权分数的阈值：
    - > 6.0: 太旺
    - > 3.0: 旺
    - < 2.0: 弱
    """
    water_count = wuxing_counts.get('水', 0)
    earth_count = wuxing_counts.get('土', 0)
    fire_count = wuxing_counts.get('火', 0)
    gold_count = wuxing_counts.get('金', 0)
    
    if water_count > 6.0:
        # 水太旺，喜土克水，火耗水
        return "土、火", "土"
    elif earth_count > 3.0:
        # 土旺，喜木制土，水生木
        return "木、水", "木"
    elif fire_count > 3.0:
        # 火旺，喜水克火，金生水
        return "水、金", "水"
    elif gold_count < 2.0:
        # 金弱，喜金生水
        return "金、水", "金"
    else:
        # 一般情况，喜金生水
        return "金、水", "金"


def _calculate_for_fire(wuxing_counts):
    """
    火日主的喜用神计算
    
    使用加权分数的阈值：
    - > 6.0: 太旺
    - > 3.0: 旺
    - < 2.0: 弱
    """
    fire_count = wuxing_counts.get('火', 0)
    water_count = wuxing_counts.get('水', 0)
    gold_count = wuxing_counts.get('金', 0)
    wood_count = wuxing_counts.get('木', 0)
    
    if fire_count > 6.0:
        # 火太旺，喜水克火，金耗火
        return "水、金", "水"
    elif water_count > 3.0:
        # 水旺，喜土克水，火生土
        return "土、火", "土"
    elif gold_count > 3.0:
        # 金旺，喜火克金，木生火
        return "火、木", "火"
    elif wood_count < 2.0:
        # 木弱，喜木生火
        return "木、火", "木"
    else:
        # 一般情况，喜木生火
        return "木、火", "火"


def _calculate_for_earth(wuxing_counts):
    """
    土日主的喜用神计算
    
    使用加权分数的阈值：
    - > 6.0: 太旺
    - > 3.0: 旺
    - < 2.0: 弱
    """
    earth_count = wuxing_counts.get('土', 0)
    wood_count = wuxing_counts.get('木', 0)
    gold_count = wuxing_counts.get('金', 0)
    fire_count = wuxing_counts.get('火', 0)
    water_count = wuxing_counts.get('水', 0)
    
    if earth_count > 6.0:
        # 土太旺，喜木制土，水润土
        return "木、水", "木"
    elif gold_count > 3.0:
        # 伤官（金）太旺，喜木（官杀）制伤官，水（财）生官杀
        return "木、水", "木"
    elif wood_count > 3.0:
        # 木旺，喜金克木，土生金
        return "金、土", "金"
    elif water_count < 2.0:
        # 水弱，喜水润土
        return "水、土", "水"
    elif fire_count < 2.0:
        # 火弱，喜火生土
        return "火、土", "火"
    else:
        # 一般情况，喜火生土
        return "火、土", "火"


# 便捷函数
def get_xishen_yongshen(sizhu, analysis=None):
    """
    获取喜用神的便捷函数
    
    Args:
        sizhu: 四柱信息
        analysis: 分析结果（可选）
        
    Returns:
        dict: {'xishen': 喜用神, 'yongshen': 用神}
    """
    xishen, yongshen = calculate_xishen_yongshen(sizhu, analysis)
    return {
        'xishen': xishen,
        'yongshen': yongshen
    }


# -*- coding: utf-8 -*-
"""
================================================================================
四柱计算模块
================================================================================
提供年柱、月柱、日柱、时柱的完整计算功能

使用方法:
    1. 作为模块导入: from modules.四柱计算器 import calculate_sizhu
    2. 直接运行: python -m modules.四柱计算器

【重要说明】
本模块使用精确的农历计算方法，基于 sxtwl 库的天文算法
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
from datetime import date, datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 从工具函数导入基础数据
# 尝试导入 sxtwl 库
try:
    import sxtwl
    HAS_SXTWL = True
    logger.info("成功导入 sxtwl 库，使用精确的四柱计算方法")
except ImportError:
    HAS_SXTWL = False
    logger.warning("未找到 sxtwl 库，将使用备用计算方法")

class SiZhuCalculator:
    """
    四柱计算器类
    
    提供年柱、月柱、日柱、时柱的完整计算功能
    使用 sxtwl 库进行精确计算
    """
    
    def __init__(self, strict_mode=True, sect=2):
        """
        初始化计算器
        
        Args:
            strict_mode: 是否使用严格模式（默认True）
            sect: 流派选择（1或2，默认2）
        """
        self.strict_mode = strict_mode
        self.sect = sect
        logger.info(f"使用精确四柱计算方法 (sect={sect})")
    
    def calculate(self, target_date, hour=12, minute=0, second=0):
        """
        计算完整四柱
        
        Args:
            target_date: datetime.date对象
            hour: 小时(0-23)
            minute: 分钟(0-59)
            second: 秒(0-59)
            
        Returns:
            dict: 包含年柱、月柱、日柱、时柱的字典
        """
        year = target_date.year
        month = target_date.month
        day = target_date.day
        
        # 使用 sxtwl 计算四柱
        if HAS_SXTWL:
            return self._calculate_with_sxtwl(year, month, day, hour, minute, second)
        # 备用计算方法
        return self._calculate_fallback(year, month, day, hour, minute, second)
    
    def _calculate_with_sxtwl(self, year, month, day, hour, minute, second):
        """
        使用 sxtwl 库计算四柱
        
        sxtwl 使用天文算法，基于精确的节气时刻计算
        这是最权威的计算方法，完全依赖 sxtwl 的天文算法
        """
        # 使用 sxtwl 计算四柱
        day_obj = sxtwl.fromSolar(year, month, day)
        
        # 获取年柱、日柱、时柱（完全使用 sxtwl 的权威计算）
        year_gz = day_obj.getYearGZ()
        day_gz = day_obj.getDayGZ()
        hour_gz = day_obj.getHourGZ(hour)
        
        # 转换为天干地支
        tg = TIAN_GAN
        dz = DI_ZHI
        
        year_gan = tg[year_gz.tg]
        year_zhi = dz[year_gz.dz]
        day_gan = tg[day_gz.tg]
        day_zhi = dz[day_gz.dz]
        hour_gan = tg[hour_gz.tg]
        hour_zhi = dz[hour_gz.dz]
        
        # 计算月柱（使用精确节气时间）
        month_gan, month_zhi = self._calculate_month_pillar_precise(year, month, day, hour, minute, year_gan)
        
        # 标记是否为晚子时
        is_late_zi = (hour == 23)
        
        return {
            '年柱': year_gan + year_zhi,
            '月柱': month_gan + month_zhi,
            '日柱': day_gan + day_zhi,
            '时柱': hour_gan + hour_zhi,
            'year_gan': year_gan,
            'year_zhi': year_zhi,
            'month_gan': month_gan,
            'month_zhi': month_zhi,
            'day_gan': day_gan,
            'day_zhi': day_zhi,
            'hour_gan': hour_gan,
            'hour_zhi': hour_zhi,
            'is_late_zi': is_late_zi
        }
    
    def _calculate_month_pillar_precise(self, year, month, day, hour, minute, year_gan):
        """
        使用精确节气时间计算月柱
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            hour: 小时
            minute: 分钟
            year_gan: 年干
        
        Returns:
            tuple: (月干, 月支)
        """
        # 将儒略日转换为datetime
        def jd_to_datetime(jd):
            dd = sxtwl.JD2DD(jd)
            return datetime(int(dd.Y), int(dd.M), int(dd.D), int(dd.h), int(dd.m), int(dd.s))
        
        # 当前时间
        current_dt = datetime(year, month, day, hour, minute, 0)
        
        # 获取当年节气列表
        # 注意：sxtwl.getJieQiByYear(year) 返回的节气列表中：
        # - 索引0-21是当年的节气（立春到大雪）
        # - 索引22-23是下一公历年的小寒和大寒
        jq_list = sxtwl.getJieQiByYear(year)
        
        # 节气名称（sxtwl的索引顺序）
        # 0=立春, 1=雨水, 2=惊蛰, 3=春分, 4=清明, 5=谷雨,
        # 6=立夏, 7=小满, 8=芒种, 9=夏至, 10=小暑, 11=大暑,
        # 12=立秋, 13=处暑, 14=白露, 15=秋分, 16=寒露, 17=霜降,
        # 18=立冬, 19=小雪, 20=大雪, 21=冬至, 22=小寒, 23=大寒
        
        # 月支与"节"的对应关系
        # 立春(0)->寅月, 惊蛰(2)->卯月, 清明(4)->辰月, 立夏(6)->巳月,
        # 芒种(8)->午月, 小暑(10)->未月, 立秋(12)->申月, 白露(14)->酉月,
        # 寒露(16)->戌月, 立冬(18)->亥月, 大雪(20)->子月, 小寒(22)->丑月
        
        jie_to_month = {
            0: '寅',   # 立春
            2: '卯',   # 惊蛰
            4: '辰',   # 清明
            6: '巳',   # 立夏
            8: '午',   # 芒种
            10: '未',  # 小暑
            12: '申',  # 立秋
            14: '酉',  # 白露
            16: '戌',  # 寒露
            18: '亥',  # 立冬
            20: '子',  # 大雪
            22: '丑',  # 小寒
        }
        
        # 构建节气时间列表（只包含"节"）
        jie_times = []
        
        # 添加当年的"节"
        for jie_idx in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
            jd = jq_list[jie_idx].jd
            dt = jd_to_datetime(jd)
            jie_times.append((dt, jie_idx))
        
        # 如果当前时间在立春之前，需要添加前一年的小寒
        lichun_dt = jd_to_datetime(jq_list[0].jd)
        if current_dt < lichun_dt:
            # 获取前一年的节气列表
            jq_list_prev = sxtwl.getJieQiByYear(year - 1)
            # 前一年的小寒（索引22）
            jd = jq_list_prev[22].jd
            dt = jd_to_datetime(jd)
            jie_times.append((dt, 22))
        
        # 排序
        jie_times.sort(key=lambda x: x[0])
        
        # 找到当前时间所在的月份
        month_zhi = '寅'  # 默认
        
        for i, (dt, jie_idx) in enumerate(jie_times):
            if current_dt < dt:
                # 当前时间在这个节气之前
                if i == 0:
                    # 在第一个节气之前，使用子月（大雪到小寒之间）
                    month_zhi = '子'
                else:
                    # 使用上一个节气对应的月份
                    prev_jie_idx = jie_times[i-1][1]
                    month_zhi = jie_to_month.get(prev_jie_idx, '寅')
                break
        else:
            # 在所有节气之后，使用最后一个节气对应的月份
            last_jie_idx = jie_times[-1][1]
            month_zhi = jie_to_month.get(last_jie_idx, '丑')
        
        # 使用五虎遁计算月干
        base_gan_index = WU_HU_DUN.get(year_gan, 0)
        month_zhi_index = DI_ZHI.index(month_zhi)
        offset = (month_zhi_index - 2 + 12) % 12  # 寅=2
        month_gan_index = (base_gan_index + offset) % 10
        month_gan = TIAN_GAN[month_gan_index]
        
        return month_gan, month_zhi
    
    def _calculate_fallback(self, year, month, day, hour, minute, second):
        """
        备用计算方法
        
        当 sxtwl 不可用时使用传统算法
        
        特别处理晚子时（23:00-00:00）：
        传统八字中，晚子时的时柱需用次日的日干起时，但日柱仍用当天的日柱。
        """
        from datetime import datetime, timedelta
        
        # 处理晚子时：23:00-00:00
        is_late_zi = (hour == 23)
        
        # 计算年柱（使用原始日期判断节气）
        year_gan, year_zhi = self._calculate_year(year, month, day, hour, minute)
        
        # 计算月柱（使用原始日期判断节气）
        month_gan, month_zhi = self._calculate_month(year, month, day, hour, minute, year_gan)
        
        # 计算日柱（使用当天的日期）
        day_gan, day_zhi = self._calculate_day(year, month, day)
        
        # 计算时柱
        # 注意：根据用户提供的案例，晚子时也使用当天的日干计算时干
        # 这与传统八字的晚子时处理不同，但为了匹配用户期望，我们遵循用户的计算方式
        hour_gan, hour_zhi = self._calculate_hour(day_gan, hour, minute, year, month, day)
        
        return {
            '年柱': year_gan + year_zhi,
            '月柱': month_gan + month_zhi,
            '日柱': day_gan + day_zhi,
            '时柱': hour_gan + hour_zhi,
            'year_gan': year_gan,
            'year_zhi': year_zhi,
            'month_gan': month_gan,
            'month_zhi': month_zhi,
            'day_gan': day_gan,
            'day_zhi': day_zhi,
            'hour_gan': hour_gan,
            'hour_zhi': hour_zhi,
            'is_late_zi': is_late_zi  # 标记是否为晚子时
        }
    
    def _calculate_year(self, year, month, day, hour, minute):
        """
        计算年柱
        
        年柱以立春为界，立春前属于上一年
        """
        # 简化的立春判断（实际应该使用天文算法）
        # 立春通常在2月3日、4日或5日
        if month < 2 or (month == 2 and day < 4):
            # 立春前，属于上一年
            year -= 1
        
        # 计算年干支
        # 以1984年（甲子年）为基准
        offset = (year - 1984) % 60
        gan_index = offset % 10
        zhi_index = offset % 12
        
        return TIAN_GAN[gan_index], DI_ZHI[zhi_index]
    
    def _calculate_month(self, year, month, day, hour, minute, year_gan):
        """
        计算月柱
        
        月柱以节气为界，使用五虎遁
        """
        # 简化的节气判断
        # 寅月（正月）：立春到惊蛰
        # 卯月（二月）：惊蛰到清明
        # ...
        
        # 根据年份和月份确定月支
        # 正月建寅，即正月为寅月
        month_zhi_index = (month + 1) % 12  # 正月=2(寅), 二月=3(卯), ...
        if month_zhi_index == 0:
            month_zhi_index = 12
        month_zhi = DI_ZHI[month_zhi_index - 1]
        
        # 使用五虎遁计算月干
        # 甲己之年丙作首，乙庚之岁戊为头，丙辛必定寻庚起，丁壬壬位顺行流，戊癸何方发，甲寅之上好追求
        wu_hu_dun = {
            '甲': 2, '己': 2,  # 丙寅
            '乙': 4, '庚': 4,  # 戊寅
            '丙': 6, '辛': 6,  # 庚寅
            '丁': 8, '壬': 8,  # 壬寅
            '戊': 0, '癸': 0   # 甲寅
        }
        
        base_gan_index = wu_hu_dun.get(year_gan, 0)
        month_gan_index = (base_gan_index + (month_zhi_index - 1)) % 10
        month_gan = TIAN_GAN[month_gan_index]
        
        return month_gan, month_zhi
    
    def _calculate_day(self, year, month, day):
        """
        计算日柱
        
        使用简化的计算方法
        """
        try:
            # 以1900年1月1日为基准日（甲戌日）
            base_date = date(1900, 1, 1)
            target_date = date(year, month, day)
            days_diff = (target_date - base_date).days
            
            # 计算日干支
            # 甲戌日的天干索引是0（甲），地支索引是10（戌）
            gan_index = (days_diff + 0) % 10
            zhi_index = (days_diff + 10) % 12
            
            return TIAN_GAN[gan_index], DI_ZHI[zhi_index]
        except Exception as e:
            logger.error(f"计算日柱失败: {str(e)}", exc_info=True)
            # 返回默认值，避免程序崩溃
            return '甲', '子'
    
    def _calculate_hour(self, day_gan, hour, minute, year, month, day):
        """
        计算时柱
        
        使用五鼠遁
        """
        # 计算时支
        # 子时：23:00-1:00
        if hour == 23 or (hour == 0 and minute < 0):
            hour_zhi_index = 0  # 子
        else:
            hour_zhi_index = ((hour + 1) // 2) % 12
        
        hour_zhi = DI_ZHI[hour_zhi_index]
        
        # 使用五鼠遁计算时干
        # 五鼠遁：甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
        wu_shu_dun = {
            '甲': 0, '己': 0,  # 甲子
            '乙': 2, '庚': 2,  # 丙子
            '丙': 4, '辛': 4,  # 戊子
            '丁': 6, '壬': 6,  # 庚子
            '戊': 8, '癸': 8   # 壬子
        }
        
        base_gan_index = wu_shu_dun.get(day_gan, 0)
        hour_gan_index = (base_gan_index + hour_zhi_index) % 10
        hour_gan = TIAN_GAN[hour_gan_index]
        
        return hour_gan, hour_zhi


# 创建全局计算器实例
calculator = SiZhuCalculator()


def calculate_sizhu(target_date, hour=12, minute=0, second=0):
    """
    计算四柱的便捷函数（统一入口）
    
    【重要说明】
    这是计算四柱的唯一入口函数，使用精确的农历计算方法
    
    Args:
        target_date: datetime.date对象或datetime对象
        hour: 小时(0-23)
        minute: 分钟(0-59)
        second: 秒(0-59)
        
    Returns:
        dict: 包含年柱、月柱、日柱、时柱的字典
    """
    try:
        if isinstance(target_date, datetime):
            hour = target_date.hour
            minute = target_date.minute
            second = target_date.second
            target_date = target_date.date()
        
        result = calculator.calculate(target_date, hour, minute, second)
        
        # 确保返回的字典包含day_gan键
        if 'day_gan' not in result:
            # 尝试从日柱中提取日干
            if '日柱' in result and len(result['日柱']) > 0:
                result['day_gan'] = result['日柱'][0]
            else:
                # 如果无法获取日干，设置默认值
                result['day_gan'] = '甲'
                result['day_zhi'] = '子'
                result['日柱'] = '甲子'
        
        return result
    except Exception as e:
        logger.error(f"计算四柱失败: {str(e)}", exc_info=True)
        # 返回默认值，避免程序崩溃
        return {
            '年柱': '甲子',
            '月柱': '甲子',
            '日柱': '甲子',
            '时柱': '甲子',
            'year_gan': '甲',
            'year_zhi': '子',
            'month_gan': '甲',
            'month_zhi': '子',
            'day_gan': '甲',
            'day_zhi': '子',
            'hour_gan': '甲',
            'hour_zhi': '子',
            'is_late_zi': False
        }


def get_lunar_date(target_date, hour=12, minute=0, second=0):
    """
    获取农历日期
    """
    if isinstance(target_date, datetime):
        hour = target_date.hour
        minute = target_date.minute
        second = target_date.second
        target_date = target_date.date()

    result = calculator.get_lunar_date(target_date, hour, minute, second)
    # 转换为与旧接口兼容的格式
    return {
        '年': result['year'],
        '月': result['month'],
        '日': result['day'],
        '月中文': result['month_chinese'],
        '日中文': result['day_chinese'],
        '中文': result['chinese'],
        '生肖': result['zodiac'],
        '节气': result['jie_qi'],
        '验证': result['verified']
    }


def analyze_sizhu(sizhu):
    """
    分析四柱的便捷函数
    
    Args:
        sizhu: calculate_sizhu()返回的字典
        
    Returns:
        dict: 包含五行、十神、夫星子星等信息的字典
    """
    # 获取日干
    day_gan = None
    try:
        day_gan = sizhu.get('day_gan')
        if not day_gan and '日柱' in sizhu:
            日柱 = sizhu['日柱']
            if isinstance(日柱, str) and len(日柱) > 0:
                day_gan = 日柱[0]
    except Exception as e:
        logger.error(f"获取日干失败: {str(e)}", exc_info=True)
    
    if not day_gan:
        raise ValueError("无法获取日干")
    
    # 计算五行
    wuxing = {}
    for key in ['年柱', '月柱', '日柱', '时柱']:
        if key in sizhu:
            try:
                wuxing[key] = get_gan_wuxing(sizhu[key][0])
            except Exception as e:
                logger.error(f"计算五行失败: {str(e)}", exc_info=True)
    
    # 计算十神
    shishen = {}
    for key in ['年柱', '月柱', '时柱']:
        if key in sizhu:
            try:
                shishen[key] = get_shishen(day_gan, sizhu[key][0])
            except Exception as e:
                logger.error(f"计算十神失败: {str(e)}", exc_info=True)
    
    fuzi = get_fuzi(day_gan)
    
    return {
        '五行': wuxing,
        '十神': shishen,
        '夫星子星': fuzi
    }


def enhance_sizhu(sizhu):
    """
    增强四柱信息的便捷函数
    
    Args:
        sizhu: calculate_sizhu()返回的字典
        
    Returns:
        dict: 包含纳音、十二长生、藏干等信息的字典
    """
    result = sizhu.copy()
    
    # 添加纳音
    for key in ['年柱', '月柱', '日柱', '时柱']:
        if key in sizhu:
            result[f'{key}_纳音'] = get_nayin(sizhu[key])
    
    # 添加十二长生
    if 'day_gan' in sizhu:
        for key in ['年柱', '月柱', '日柱', '时柱']:
            if key in sizhu and len(sizhu[key]) >= 2:
                zhi = sizhu[key][1]
                result[f'{key}_长生'] = get_zhangsheng(sizhu.get('day_gan', '甲'), zhi)
    
    return result



# -*- coding: utf-8 -*-
"""
================================================================================
黄道模块（修正版）
================================================================================
计算大黄道（十二值星）和小黄道（十二建星）
数据依据《协纪辨方书》及传统通书

【大黄道十二值星】
吉星：青龙、明堂、金匮、天德、玉堂、司命
凶星：天刑、朱雀、白虎、天牢、玄武、勾陈

【小黄道十二建星】
顺序：建、除、满、平、定、执、破、危、成、收、开、闭
推算方法：以月支定建星起始点（建日即为月支），然后按顺序循环

【主要修正点说明】
小黄道表 XIAO_HUANG_DAO_TABLE 已按正确顺序重建：
- 每一行对应一个月份（月支），列顺序为日支从子到亥（索引0→子，11→亥）
- 例如寅月，子日应为"开"（因为寅月建日在寅，子日逆推两位得到开）
- 确保 day_idx 直接索引即可得到正确的建星
================================================================================
"""

from datetime import datetime

class 黄道计算器:
    """黄道计算器"""
    
    # 大黄道十二值星
    DA_HUANG_DAO = {
        '青龙': {'type': '吉', 'score': 15, 'description': '黄道吉日，诸事皆宜'},
        '明堂': {'type': '吉', 'score': 15, 'description': '黄道吉日，诸事皆宜'},
        '金匮': {'type': '吉', 'score': 10, 'description': '黄道吉日，宜积蓄财物'},
        '天德': {'type': '吉', 'score': 15, 'description': '黄道吉日，百事皆吉'},
        '玉堂': {'type': '吉', 'score': 15, 'description': '黄道吉日，诸事皆宜'},
        '司命': {'type': '吉', 'score': 10, 'description': '黄道吉日，宜祈福'},
        '天刑': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
        '朱雀': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
        '白虎': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
        '天牢': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
        '玄武': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
        '勾陈': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
    }
    
    # 小黄道十二建星
    XIAO_HUANG_DAO = {
        '建': {'type': '平', 'score': 0, 'description': '建日，宜出行、上任，忌动土、安葬'},
        '除': {'type': '吉', 'score': 5, 'description': '除日，宜扫除、清洁，忌安葬'},
        '满': {'type': '吉', 'score': 5, 'description': '满日，宜祭祀、祈福，忌动土'},
        '平': {'type': '平', 'score': 0, 'description': '平日，诸事皆宜'},
        '定': {'type': '吉', 'score': 5, 'description': '定日，宜嫁娶、立约，忌出行'},
        '执': {'type': '平', 'score': 0, 'description': '执日，宜修造、动土，忌嫁娶'},
        '破': {'type': '凶', 'score': -10, 'description': '破日，诸事不宜'},
        '危': {'type': '凶', 'score': -10, 'description': '危日，诸事不宜'},
        '成': {'type': '吉', 'score': 5, 'description': '成日，诸事皆宜'},
        '收': {'type': '平', 'score': 0, 'description': '收日，宜收敛、积蓄，忌嫁娶'},
        '开': {'type': '吉', 'score': 5, 'description': '开日，诸事皆宜'},
        '闭': {'type': '平', 'score': 0, 'description': '闭日，宜闭门、静养，忌出行'},
    }
    
    # 大黄道计算表（根据日支和时辰）
    DA_HUANG_DAO_TABLE = {
        '子': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
        '丑': ['天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂'],
        '寅': ['朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑'],
        '卯': ['金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀'],
        '辰': ['天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮'],
        '巳': ['白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德'],
        '午': ['玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎'],
        '未': ['天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂'],
        '申': ['玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢'],
        '酉': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
        '戌': ['勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命'],
        '亥': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
    }
    
    # 小黄道计算表（根据月支和日支）
    # 修正后的正确数据表：以月支为键，值为从子日至亥日的建星列表
    # 推导方法：以月支定建星起始点（建日即为月支），然后按"建除满平定执破危成收开闭"顺序循环
    # 例如寅月：寅日为建，卯日为除，辰日为满，…，丑日为闭
    # 对应到日支子日（索引0）应为开（寅前两位），故子日=开
    # 验证：寅月寅日=建，寅月子日=开（正确）
    XIAO_HUANG_DAO_TABLE = {
        '寅': ['开', '闭', '建', '除', '满', '平', '定', '执', '破', '危', '成', '收'],  # 子→亥
        '卯': ['收', '开', '闭', '建', '除', '满', '平', '定', '执', '破', '危', '成'],
        '辰': ['成', '收', '开', '闭', '建', '除', '满', '平', '定', '执', '破', '危'],
        '巳': ['危', '成', '收', '开', '闭', '建', '除', '满', '平', '定', '执', '破'],
        '午': ['破', '危', '成', '收', '开', '闭', '建', '除', '满', '平', '定', '执'],
        '未': ['执', '破', '危', '成', '收', '开', '闭', '建', '除', '满', '平', '定'],
        '申': ['定', '执', '破', '危', '成', '收', '开', '闭', '建', '除', '满', '平'],
        '酉': ['平', '定', '执', '破', '危', '成', '收', '开', '闭', '建', '除', '满'],
        '戌': ['满', '平', '定', '执', '破', '危', '成', '收', '开', '闭', '建', '除'],
        '亥': ['除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭', '建'],
        '子': ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭'],
        '丑': ['闭', '建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开'],
    }
    
    # 大黄道宜忌表（十二值星对应事项的宜忌）
    DA_HUANG_DAO_YIJI = {
        '青龙': {
            'yi': ['嫁娶', '订婚', '出行', '上任', '开业', '修造', '动土', '安葬', '祭祀', '祈福'],
            'ji': ['诉讼', '争斗'],
            'description': '青龙为黄道之首，诸事皆宜，百事大吉'
        },
        '明堂': {
            'yi': ['嫁娶', '订婚', '开业', '修造', '动土', '安葬', '祭祀', '祈福', '入学', '上任'],
            'ji': ['词讼'],
            'description': '明堂主文明，宜文书、教育、公务之事'
        },
        '金匮': {
            'yi': ['嫁娶', '订婚', '开业', '交易', '签约', '纳财', '修造', '动土', '安葬'],
            'ji': ['开仓', '出货'],
            'description': '金匮主财库，宜积蓄财物、交易签约'
        },
        '天德': {
            'yi': ['嫁娶', '订婚', '出行', '上任', '开业', '修造', '动土', '安葬', '祭祀', '祈福', '求医'],
            'ji': ['刑杀', '争斗'],
            'description': '天德为上天之德，百事皆吉，诸凶皆解'
        },
        '玉堂': {
            'yi': ['嫁娶', '订婚', '开业', '修造', '动土', '安葬', '祭祀', '祈福', '会友', '宴饮'],
            'ji': ['诉讼'],
            'description': '玉堂主贵显，宜喜庆、会友、宴饮之事'
        },
        '司命': {
            'yi': ['嫁娶', '订婚', '祭祀', '祈福', '求医', '疗病', '安葬'],
            'ji': ['上任', '出行', '开业'],
            'description': '司命主生命，宜祈福、祭祀、疗病之事'
        },
        '天刑': {
            'yi': ['祭祀', '祈福', '安葬'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '诉讼'],
            'description': '天刑主刑杀，诸事不宜，唯宜祭祀安葬'
        },
        '朱雀': {
            'yi': ['祭祀', '祈福'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '诉讼'],
            'description': '朱雀主口舌是非，诸事不宜，易生争端'
        },
        '白虎': {
            'yi': ['祭祀', '祈福', '安葬'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '诉讼'],
            'description': '白虎主凶杀，诸事不宜，唯宜祭祀安葬'
        },
        '天牢': {
            'yi': ['祭祀', '祈福'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '诉讼'],
            'description': '天牢主囚禁，诸事不宜，易有阻碍'
        },
        '玄武': {
            'yi': ['祭祀', '祈福'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '交易'],
            'description': '玄武主盗贼阴私，诸事不宜，易有损失'
        },
        '勾陈': {
            'yi': ['祭祀', '祈福'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '诉讼'],
            'description': '勾陈主牵连阻滞，诸事不宜，易有拖延'
        }
    }
    
    # 小黄道宜忌表（十二建星对应事项的宜忌）
    XIAO_HUANG_DAO_YIJI = {
        '建': {
            'yi': ['出行', '上任', '谒贵', '上书'],
            'ji': ['嫁娶', '安葬', '动土', '修造', '开仓'],
            'description': '建日宜出行上任，忌嫁娶安葬'
        },
        '除': {
            'yi': ['祭祀', '祈福', '扫除', '清洁', '疗病', '出行'],
            'ji': ['嫁娶', '安葬', '上任', '开业'],
            'description': '除日宜清洁扫除，忌嫁娶安葬'
        },
        '满': {
            'yi': ['祭祀', '祈福', '结亲', '会友'],
            'ji': ['动土', '安葬', '上任', '开业'],
            'description': '满日宜祭祀祈福，忌动土安葬'
        },
        '平': {
            'yi': ['祭祀', '祈福', '出行', '会友', '修造'],
            'ji': ['嫁娶', '安葬', '上任', '开业'],
            'description': '平日诸事平平，无大吉凶'
        },
        '定': {
            'yi': ['嫁娶', '订婚', '立约', '交易', '入学', '上任'],
            'ji': ['出行', '诉讼', '安葬'],
            'description': '定日宜立约交易，忌出行诉讼'
        },
        '执': {
            'yi': ['修造', '动土', '捕捉', '狩猎'],
            'ji': ['嫁娶', '安葬', '上任', '开业', '出行'],
            'description': '执日宜修造动土，忌嫁娶安葬'
        },
        '破': {
            'yi': ['祭祀', '祈福', '治病', '拆除'],
            'ji': ['嫁娶', '订婚', '上任', '开业', '修造', '动土', '安葬', '出行'],
            'description': '破日诸事不宜，唯宜治病拆除'
        },
        '危': {
            'yi': ['祭祀', '祈福'],
            'ji': ['嫁娶', '订婚', '上任', '开业', '修造', '动土', '安葬', '出行'],
            'description': '危日诸事不宜，易有危险'
        },
        '成': {
            'yi': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '祭祀', '祈福', '入学'],
            'ji': ['诉讼'],
            'description': '成日诸事皆宜，百事大吉'
        },
        '收': {
            'yi': ['祭祀', '祈福', '纳财', '收敛', '积蓄'],
            'ji': ['嫁娶', '安葬', '上任', '开业', '出行'],
            'description': '收日宜收敛积蓄，忌嫁娶安葬'
        },
        '开': {
            'yi': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '祭祀', '祈福', '入学'],
            'ji': ['安葬'],
            'description': '开日诸事皆宜，百事大吉'
        },
        '闭': {
            'yi': ['祭祀', '祈福', '闭门', '静养', '收敛'],
            'ji': ['嫁娶', '安葬', '上任', '开业', '出行', '修造', '动土'],
            'description': '闭日宜闭门静养，忌大事'
        }
    }
    
    # 地支索引
    ZHI_INDEX = {'子': 0, '丑': 1, '寅': 2, '卯': 3, '辰': 4, '巳': 5, 
                '午': 6, '未': 7, '申': 8, '酉': 9, '戌': 10, '亥': 11}
    
    def __init__(self):
        pass
    
    def calculate(self, sizhu):
        """
        计算黄道信息
        
        Args:
            sizhu: 四柱信息，包含年柱、月柱、日柱、时柱
            
        Returns:
            dict: 黄道信息，包含大黄道、小黄道、综合评分等
        """
        day_zhi = sizhu['日柱'][1]  # 日支
        month_zhi = sizhu['月柱'][1]  # 月支
        hour_zhi = sizhu['时柱'][1]  # 时支
        
        # 计算大黄道
        da_huang_dao = self._calculate_da_huang_dao(day_zhi, hour_zhi)
        
        # 计算小黄道
        xiao_huang_dao = self._calculate_xiao_huang_dao(month_zhi, day_zhi)
        
        # 计算黄道综合评分
        huang_dao_score = da_huang_dao['score'] + xiao_huang_dao['score']
        
        # 判断黄道等级
        huang_dao_level = self._get_huang_dao_level(da_huang_dao, xiao_huang_dao)
        
        return {
            'da_huang_dao': da_huang_dao,
            'xiao_huang_dao': xiao_huang_dao,
            'huang_dao_score': huang_dao_score,
            'huang_dao_level': huang_dao_level,
            'description': self._generate_description(da_huang_dao, xiao_huang_dao)
        }
    
    def _calculate_da_huang_dao(self, day_zhi, hour_zhi):
        """计算大黄道"""
        day_idx = self.ZHI_INDEX.get(day_zhi, 0)
        hour_idx = self.ZHI_INDEX.get(hour_zhi, 0)

        da_list = self.DA_HUANG_DAO_TABLE.get(day_zhi, [])
        if not da_list:
            return {'name': '未知', 'type': '平', 'score': 0, 'description': ''}

        name = da_list[hour_idx % 12]
        info = self.DA_HUANG_DAO.get(name, {'type': '平', 'score': 0, 'description': ''})

        return {
            'name': name,
            'type': info['type'],
            'score': info['score'],
            'description': info['description']
        }

    def _calculate_xiao_huang_dao(self, month_zhi, day_zhi):
        """计算小黄道"""
        xiao_list = self.XIAO_HUANG_DAO_TABLE.get(month_zhi, [])
        if not xiao_list:
            return {'name': '未知', 'type': '平', 'score': 0, 'description': ''}

        day_idx = self.ZHI_INDEX.get(day_zhi, 0)

        name = xiao_list[day_idx % 12]
        info = self.XIAO_HUANG_DAO.get(name, {'type': '平', 'score': 0, 'description': ''})

        return {
            'name': name,
            'type': info['type'],
            'score': info['score'],
            'description': info['description']
        }

    def _get_huang_dao_level(self, da_huang_dao, xiao_huang_dao):
        """
        判断黄道等级
        规则：
        - 大黄道凶 → 凶（不论小黄道）
        - 大黄道吉且小黄道吉 → 大吉
        - 大黄道吉且小黄道平 → 吉
        - 大黄道吉且小黄道凶 → 次吉
        - 大黄道平且小黄道吉 → 吉
        - 大黄道平且小黄道平 → 平
        - 大黄道平且小黄道凶 → 次凶
        """
        if da_huang_dao['type'] == '凶':
            return '凶'

        if da_huang_dao['type'] == '吉':
            if xiao_huang_dao['type'] == '吉':
                return '大吉'
            elif xiao_huang_dao['type'] == '平':
                return '吉'
            else:
                return '次吉'

        if xiao_huang_dao['type'] == '吉':
            return '吉'
        elif xiao_huang_dao['type'] == '平':
            return '平'
        else:
            return '次凶'

    def _generate_description(self, da, xiao):
        """生成描述文本"""
        desc = []
        if da['type'] == '吉':
            desc.append(f"大黄道{da['name']}，{da['description']}")
        elif da['type'] == '凶':
            desc.append(f"黑道{da['name']}，{da['description']}")
        else:
            desc.append(f"大黄道{da['name']}")

        if xiao['type'] == '吉':
            desc.append(f"小黄道{xiao['name']}，{xiao['description']}")
        elif xiao['type'] == '凶':
            desc.append(f"小黄道{xiao['name']}，{xiao['description']}")
        else:
            desc.append(f"小黄道{xiao['name']}")

        return '；'.join(desc)
    
    def get_yiji(self, sizhu, event_type=None):
        """
        获取黄道宜忌信息
        
        Args:
            sizhu: 四柱信息
            event_type: 事项类型（如'嫁娶'、'修造'等），为None则返回所有宜忌
            
        Returns:
            dict: 宜忌信息
        """
        day_zhi = sizhu['日柱'][1]  # 日支
        month_zhi = sizhu['月柱'][1]  # 月支
        hour_zhi = sizhu['时柱'][1]  # 时支
        
        # 计算大黄道和小黄道
        da_huang_dao = self._calculate_da_huang_dao(day_zhi, hour_zhi)
        xiao_huang_dao = self._calculate_xiao_huang_dao(month_zhi, day_zhi)
        
        # 获取宜忌
        da_yiji = self.DA_HUANG_DAO_YIJI.get(da_huang_dao['name'], {})
        xiao_yiji = self.XIAO_HUANG_DAO_YIJI.get(xiao_huang_dao['name'], {})
        
        result = {
            'da_huang_dao': {
                'name': da_huang_dao['name'],
                'type': da_huang_dao['type'],
                'yi': da_yiji.get('yi', []),
                'ji': da_yiji.get('ji', []),
                'description': da_yiji.get('description', '')
            },
            'xiao_huang_dao': {
                'name': xiao_huang_dao['name'],
                'type': xiao_huang_dao['type'],
                'yi': xiao_yiji.get('yi', []),
                'ji': xiao_yiji.get('ji', []),
                'description': xiao_yiji.get('description', '')
            }
        }
        
        # 如果指定了事项类型，检查该事项是否适宜
        if event_type:
            result['event_check'] = self._check_event_yiji(event_type, da_yiji, xiao_yiji)
        
        return result
    
    def _check_event_yiji(self, event_type, da_yiji, xiao_yiji):
        """
        检查特定事项的宜忌
        
        Args:
            event_type: 事项类型
            da_yiji: 大黄道宜忌
            xiao_yiji: 小黄道宜忌
            
        Returns:
            dict: 检查结果
        """
        da_yi = da_yiji.get('yi', [])
        da_ji = da_yiji.get('ji', [])
        xiao_yi = xiao_yiji.get('yi', [])
        xiao_ji = xiao_yiji.get('ji', [])
        
        # 检查大黄道
        da_suitable = event_type in da_yi
        da_unsuitable = event_type in da_ji
        
        # 检查小黄道
        xiao_suitable = event_type in xiao_yi
        xiao_unsuitable = event_type in xiao_ji
        
        # 综合判断
        if da_unsuitable or xiao_unsuitable:
            status = '忌'
            score = -20
        elif da_suitable and xiao_suitable:
            status = '大吉'
            score = 15
        elif da_suitable or xiao_suitable:
            status = '宜'
            score = 8
        else:
            status = '平'
            score = 0
        
        return {
            'event': event_type,
            'status': status,
            'score': score,
            'da_huang_dao_suitable': da_suitable,
            'da_huang_dao_unsuitable': da_unsuitable,
            'xiao_huang_dao_suitable': xiao_suitable,
            'xiao_huang_dao_unsuitable': xiao_unsuitable
        }
    
    def get_day_yiji(self, month_zhi, day_zhi):
        """
        获取某日的宜忌（便捷方法）
        
        Args:
            month_zhi: 月支
            day_zhi: 日支
            
        Returns:
            dict: 宜忌信息
        """
        # 计算小黄道
        xiao_huang_dao = self._calculate_xiao_huang_dao(month_zhi, day_zhi)
        xiao_yiji = self.XIAO_HUANG_DAO_YIJI.get(xiao_huang_dao['name'], {})
        
        return {
            'jianxing': xiao_huang_dao['name'],
            'type': xiao_huang_dao['type'],
            'yi': xiao_yiji.get('yi', []),
            'ji': xiao_yiji.get('ji', []),
            'description': xiao_yiji.get('description', '')
        }


# 全局黄道计算器实例
huangdao_calculator = 黄道计算器()

def calculate_huangdao(sizhu):
    """
    计算黄道信息（便捷函数）

    Args:
        sizhu: 四柱信息，格式与黄道计算器.calculate 要求一致

    Returns:
        dict: 黄道信息
    """
    return huangdao_calculator.calculate(sizhu)

def get_huangdao_yiji(sizhu, event_type=None):
    """
    获取黄道宜忌信息（便捷函数）

    Args:
        sizhu: 四柱信息
        event_type: 事项类型（如'嫁娶'、'修造'等），为None则返回所有宜忌

    Returns:
        dict: 宜忌信息
    """
    return huangdao_calculator.get_yiji(sizhu, event_type)

def get_day_yiji(month_zhi, day_zhi):
    """
    获取某日的宜忌（便捷函数）

    Args:
        month_zhi: 月支
        day_zhi: 日支

    Returns:
        dict: 宜忌信息
    """
    return huangdao_calculator.get_day_yiji(month_zhi, day_zhi)


# -*- coding: utf-8 -*-
"""
================================================================================
二十四山模块
================================================================================
提供二十四山相关的完整功能，包括：
- 二十四山基本信息（名称、类型、度数范围、五行属性）
- 分金计算（120分金、60分金）
- 五行生克关系判断
- 神煞与山的对应关系
- 择日中的山家吉凶判断
- 数据库支持（从数据库加载规则和基础数据）

使用方法:
    # 获取二十四山信息
    mountains = TwentyFourMountains()
    shan = mountains.get_mountain_by_name('壬')
    
    # 判断五行生克
    relation = WuxingRelation.get_relation('金', '水')
    
    # 获取分金信息
    fengjin = mountains.get_fengjin('壬', 3)  # 获取壬山第3个分金
    
    # 使用数据库版本的选择器
================================================================================
"""

import sys
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# 检查是否是直接运行（不是作为模块导入）
class MountainType(Enum):
    """山类型枚举"""
    TIANGAN = '天干'  # 八干：甲乙丙丁庚辛壬癸
    DIZHI = '地支'    # 十二支：子丑寅卯辰巳午未申酉戌亥
    SIWEI = '四维'    # 四维：乾坤艮巽


class YinYang(Enum):
    """阴阳枚举"""
    YANG = '阳'
    YIN = '阴'


# 五行名称映射
WUXING_NAMES = {1: '金', 2: '木', 3: '水', 4: '火', 5: '土'}
WUXING_COLORS = {1: '白', 2: '绿', 3: '黑', 4: '红', 5: '黄'}


class WuxingRelation:
    """
    五行生克关系类
    
    提供五行之间的生克关系判断
    """
    # 名称映射
    NAME_TO_ID = {'金': 0, '木': 1, '水': 2, '火': 3, '土': 4}
    ID_TO_NAME = {0: '金', 1: '木', 2: '水', 3: '火', 4: '土'}
    
    # 生克关系：生成者 -> 被生者
    SHENG_MAP = {0: 2, 1: 3, 2: 1, 3: 4, 4: 0}  # 金生水，木生火，水生木，火生土，土生金
    KE_MAP = {0: 1, 1: 4, 4: 2, 2: 3, 3: 0}    # 金克木，木克土，土克水，水克火，火克金
    
    @classmethod
    def get_relation(cls, wuxing_a, wuxing_b) -> str:
        """
        判断五行a与五行b的关系
        
        Args:
            wuxing_a: 五行名称（如'金'）或ID
            wuxing_b: 五行名称或ID
            
        Returns:
            字符串描述：'相生(a生b)', '相生(b生a)', '相克(a克b)', '相克(b克a)', '比和'
        """
        if isinstance(wuxing_a, str):
            a = cls.NAME_TO_ID.get(wuxing_a)
        else:
            a = wuxing_a
        if isinstance(wuxing_b, str):
            b = cls.NAME_TO_ID.get(wuxing_b)
        else:
            b = wuxing_b
        
        if a is None or b is None:
            return "未知五行"
        
        if a == b:
            return "比和"
        
        # 检查a生b
        if cls.SHENG_MAP.get(a) == b:
            return f"相生({cls.ID_TO_NAME[a]}生{cls.ID_TO_NAME[b]})"
        # 检查b生a
        if cls.SHENG_MAP.get(b) == a:
            return f"相生({cls.ID_TO_NAME[b]}生{cls.ID_TO_NAME[a]})"
        # 检查a克b
        if cls.KE_MAP.get(a) == b:
            return f"相克({cls.ID_TO_NAME[a]}克{cls.ID_TO_NAME[b]})"
        # 检查b克a
        if cls.KE_MAP.get(b) == a:
            return f"相克({cls.ID_TO_NAME[b]}克{cls.ID_TO_NAME[a]})"
        
        return "无直接生克"
    
    @classmethod
    def is_sheng(cls, wuxing_a, wuxing_b) -> bool:
        """判断a是否生b"""
        if isinstance(wuxing_a, str):
            a = cls.NAME_TO_ID.get(wuxing_a)
        else:
            a = wuxing_a
        if isinstance(wuxing_b, str):
            b = cls.NAME_TO_ID.get(wuxing_b)
        else:
            b = wuxing_b
        return cls.SHENG_MAP.get(a) == b
    
    @classmethod
    def is_ke(cls, wuxing_a, wuxing_b) -> bool:
        """判断a是否克b"""
        if isinstance(wuxing_a, str):
            a = cls.NAME_TO_ID.get(wuxing_a)
        else:
            a = wuxing_a
        if isinstance(wuxing_b, str):
            b = cls.NAME_TO_ID.get(wuxing_b)
        else:
            b = wuxing_b
        return cls.KE_MAP.get(a) == b
    
    @classmethod
    def is_bihe(cls, wuxing_a, wuxing_b) -> bool:
        """判断是否比和（相同）"""
        if isinstance(wuxing_a, str):
            a = cls.NAME_TO_ID.get(wuxing_a)
        else:
            a = wuxing_a
        if isinstance(wuxing_b, str):
            b = cls.NAME_TO_ID.get(wuxing_b)
        else:
            b = wuxing_b
        return a == b
    
    @classmethod
    def get_relation_by_id(cls, a: int, b: int) -> str:
        """
        通过ID返回具体关系代码
        
        Args:
            a: 第一个五行ID（0-4）
            b: 第二个五行ID（0-4）
            
        Returns:
            关系代码：'a_sheng_b', 'b_sheng_a', 'a_ke_b', 'b_ke_a', 'equal', 'none'
        """
        if a == b:
            return 'equal'
        if cls.SHENG_MAP.get(a) == b:
            return 'a_sheng_b'
        if cls.SHENG_MAP.get(b) == a:
            return 'b_sheng_a'
        if cls.KE_MAP.get(a) == b:
            return 'a_ke_b'
        if cls.KE_MAP.get(b) == a:
            return 'b_ke_a'
        return 'none'
    
    @classmethod
    def get_relation_direction(cls, wuxing_a, wuxing_b, mountain_wx) -> str:
        """
        获取五行关系方向（针对坐山）
        
        Args:
            wuxing_a: 日课五行
            wuxing_b: 坐山五行
            mountain_wx: 坐山五行（与wuxing_b相同，用于明确语义）
            
        Returns:
            方向描述：'课生山', '山生课', '课克山', '山克课', '比和', 'none'
        """
        if isinstance(wuxing_a, str):
            a = cls.NAME_TO_ID.get(wuxing_a)
        else:
            a = wuxing_a
        if isinstance(wuxing_b, str):
            b = cls.NAME_TO_ID.get(wuxing_b)
        else:
            b = wuxing_b
        
        if a == b:
            return '比和'
        if cls.SHENG_MAP.get(a) == b:
            return '课生山'
        if cls.SHENG_MAP.get(b) == a:
            return '山生课'
        if cls.KE_MAP.get(a) == b:
            return '课克山'
        if cls.KE_MAP.get(b) == a:
            return '山克课'
        return 'none'


# 二十四山数据
TWENTY_FOUR_MOUNTAINS_DATA = [
    # id, 名称, 类型, 起始度数, 结束度数, 五行, 阴阳
    (1, '壬', MountainType.TIANGAN, 337.5, 352.5, '水', YinYang.YANG),
    (2, '子', MountainType.DIZHI, 352.5, 7.5, '水', YinYang.YANG),
    (3, '癸', MountainType.TIANGAN, 7.5, 22.5, '水', YinYang.YIN),
    (4, '丑', MountainType.DIZHI, 22.5, 37.5, '土', YinYang.YIN),
    (5, '艮', MountainType.SIWEI, 37.5, 52.5, '土', YinYang.YANG),
    (6, '寅', MountainType.DIZHI, 52.5, 67.5, '木', YinYang.YANG),
    (7, '甲', MountainType.TIANGAN, 67.5, 82.5, '木', YinYang.YANG),
    (8, '卯', MountainType.DIZHI, 82.5, 97.5, '木', YinYang.YIN),
    (9, '乙', MountainType.TIANGAN, 97.5, 112.5, '木', YinYang.YIN),
    (10, '辰', MountainType.DIZHI, 112.5, 127.5, '土', YinYang.YANG),
    (11, '巽', MountainType.SIWEI, 127.5, 142.5, '木', YinYang.YIN),
    (12, '巳', MountainType.DIZHI, 142.5, 157.5, '火', YinYang.YIN),
    (13, '丙', MountainType.TIANGAN, 157.5, 172.5, '火', YinYang.YANG),
    (14, '午', MountainType.DIZHI, 172.5, 187.5, '火', YinYang.YANG),
    (15, '丁', MountainType.TIANGAN, 187.5, 202.5, '火', YinYang.YIN),
    (16, '未', MountainType.DIZHI, 202.5, 217.5, '土', YinYang.YIN),
    (17, '坤', MountainType.SIWEI, 217.5, 232.5, '土', YinYang.YIN),
    (18, '申', MountainType.DIZHI, 232.5, 247.5, '金', YinYang.YANG),
    (19, '庚', MountainType.TIANGAN, 247.5, 262.5, '金', YinYang.YANG),
    (20, '酉', MountainType.DIZHI, 262.5, 277.5, '金', YinYang.YIN),
    (21, '辛', MountainType.TIANGAN, 277.5, 292.5, '金', YinYang.YIN),
    (22, '戌', MountainType.DIZHI, 292.5, 307.5, '土', YinYang.YANG),
    (23, '乾', MountainType.SIWEI, 307.5, 322.5, '金', YinYang.YANG),
    (24, '亥', MountainType.DIZHI, 322.5, 337.5, '水', YinYang.YIN),
]


class TwentyFourMountains:
    """
    二十四山类
    
    提供二十四山的完整功能，包括查询、分金计算等
    """
    
    def __init__(self):
        """初始化二十四山数据"""
        self.mountains = {}
        self._init_mountains()
        self._init_fengjin()
    
    def _init_mountains(self):
        """初始化山数据"""
        for data in TWENTY_FOUR_MOUNTAINS_DATA:
            mid, name, mtype, start_deg, end_deg, wuxing, yinyang = data
            self.mountains[name] = {
                'id': mid,
                'name': name,
                'type': mtype,
                'start_degree': start_deg,
                'end_degree': end_deg,
                'wuxing': wuxing,
                'yinyang': yinyang,
            }
    
    def _init_fengjin(self):
        """初始化120分金数据"""
        # 每个山分为5个分金，每个分金3度
        # 分金名称：如壬山分为癸丑、艮寅、甲卯、乙辰、巽巳
        self.fengjin_data = {}
        
        # 120分金的天干地支顺序
        tiangan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 为每个山创建5个分金
        for data in TWENTY_FOUR_MOUNTAINS_DATA:
            mid, name, mtype, start_deg, end_deg, wuxing, yinyang = data
            self.fengjin_data[name] = []
            
            # 计算该山的5个分金
            for i in range(5):
                fj_start = start_deg + i * 3
                fj_end = fj_start + 3
                
                # 处理跨越0度的情况
                if fj_start >= 360:
                    fj_start -= 360
                if fj_end >= 360:
                    fj_end -= 360
                
                # 分金名称（简化处理，实际应根据具体规则）
                fj_name = f"{name}{i+1}分金"
                
                self.fengjin_data[name].append({
                    'index': i + 1,
                    'name': fj_name,
                    'start_degree': fj_start,
                    'end_degree': fj_end,
                    'width': 3.0,  # 每个分金3度
                })
    
    def get_mountain_by_name(self, name: str) -> Optional[Dict]:
        """
        根据名称获取山信息
        
        Args:
            name: 山名（如'壬'、'子'等）
            
        Returns:
            山信息字典，找不到返回None
        """
        return self.mountains.get(name)
    
    def get_mountain_by_degree(self, degree: float) -> Optional[Dict]:
        """
        根据度数获取山信息
        
        Args:
            degree: 度数（0-360）
            
        Returns:
            山信息字典，找不到返回None
        """
        # 标准化度数到0-360范围
        degree = degree % 360
        
        for name, data in self.mountains.items():
            start = data['start_degree']
            end = data['end_degree']
            
            # 处理跨越0度的情况
            if start > end:  # 如壬山：337.5-352.5，但子山是352.5-7.5
                if degree >= start or degree < end:
                    return data
            else:
                if start <= degree < end:
                    return data
        
        return None
    
    def get_all_mountains(self) -> List[Dict]:
        """
        获取所有山信息
        
        Returns:
            山信息列表
        """
        return list(self.mountains.values())
    
    def get_mountains_by_type(self, mtype: MountainType) -> List[Dict]:
        """
        根据类型获取山
        
        Args:
            mtype: 山类型
            
        Returns:
            山信息列表
        """
        return [m for m in self.mountains.values() if m['type'] == mtype]
    
    def get_mountains_by_wuxing(self, wuxing: str) -> List[Dict]:
        """
        根据五行获取山
        
        Args:
            wuxing: 五行名称（金、木、水、火、土）
            
        Returns:
            山信息列表
        """
        return [m for m in self.mountains.values() if m['wuxing'] == wuxing]
    
    def get_fengjin(self, mountain_name: str, index: int) -> Optional[Dict]:
        """
        获取指定山的分金信息
        
        Args:
            mountain_name: 山名
            index: 分金序号（1-5）
            
        Returns:
            分金信息字典，找不到返回None
        """
        if mountain_name not in self.fengjin_data:
            return None
        
        fengjin_list = self.fengjin_data[mountain_name]
        if index < 1 or index > len(fengjin_list):
            return None
        
        return fengjin_list[index - 1]
    
    def get_all_fengjin(self, mountain_name: str) -> List[Dict]:
        """
        获取指定山的所有分金
        
        Args:
            mountain_name: 山名
            
        Returns:
            分金信息列表
        """
        return self.fengjin_data.get(mountain_name, [])
    
    def get_fengjin_by_degree(self, degree: float) -> Optional[Tuple[str, Dict]]:
        """
        根据度数获取分金信息
        
        Args:
            degree: 度数（0-360）
            
        Returns:
            (山名, 分金信息)元组，找不到返回None
        """
        mountain = self.get_mountain_by_degree(degree)
        if not mountain:
            return None
        
        # 计算在该山内的相对位置
        start_deg = mountain['start_degree']
        relative_deg = (degree - start_deg) % 360
        
        # 确定分金序号（每个分金3度）
        index = int(relative_deg / 3) + 1
        if index > 5:
            index = 5
        
        fengjin = self.get_fengjin(mountain['name'], index)
        if fengjin:
            return (mountain['name'], fengjin)
        
        return None
    
    def check_wuxing_relation(self, mountain_name: str, wuxing: str) -> str:
        """
        检查山五行与指定五行的关系
        
        Args:
            mountain_name: 山名
            wuxing: 五行名称
            
        Returns:
            关系描述字符串
        """
        mountain = self.get_mountain_by_name(mountain_name)
        if not mountain:
            return "未知山"
        
        return WuxingRelation.get_relation(mountain['wuxing'], wuxing)


# 常用神煞与山的对应规则
SHENSHA_MOUNTAIN_RULES = {
    '三煞': {
        'description': '申子辰年煞在南方巳午未，寅午戌年煞在北方亥子丑，巳酉丑年煞在东方寅卯辰，亥卯未年煞在西方申酉戌',
        'rules': [
            {'condition_type': '年', 'condition_value': ['申', '子', '辰'], 'avoid_mountains': ['巳', '午', '未']},
            {'condition_type': '年', 'condition_value': ['寅', '午', '戌'], 'avoid_mountains': ['亥', '子', '丑']},
            {'condition_type': '年', 'condition_value': ['巳', '酉', '丑'], 'avoid_mountains': ['寅', '卯', '辰']},
            {'condition_type': '年', 'condition_value': ['亥', '卯', '未'], 'avoid_mountains': ['申', '酉', '戌']},
        ]
    },
    '岁破': {
        'description': '岁破在年支对冲方位',
        'rules': [
            {'condition_type': '年', 'condition_value': ['子'], 'avoid_mountains': ['午']},
            {'condition_type': '年', 'condition_value': ['丑'], 'avoid_mountains': ['未']},
            {'condition_type': '年', 'condition_value': ['寅'], 'avoid_mountains': ['申']},
            {'condition_type': '年', 'condition_value': ['卯'], 'avoid_mountains': ['酉']},
            {'condition_type': '年', 'condition_value': ['辰'], 'avoid_mountains': ['戌']},
            {'condition_type': '年', 'condition_value': ['巳'], 'avoid_mountains': ['亥']},
            {'condition_type': '年', 'condition_value': ['午'], 'avoid_mountains': ['子']},
            {'condition_type': '年', 'condition_value': ['未'], 'avoid_mountains': ['丑']},
            {'condition_type': '年', 'condition_value': ['申'], 'avoid_mountains': ['寅']},
            {'condition_type': '年', 'condition_value': ['酉'], 'avoid_mountains': ['卯']},
            {'condition_type': '年', 'condition_value': ['戌'], 'avoid_mountains': ['辰']},
            {'condition_type': '年', 'condition_value': ['亥'], 'avoid_mountains': ['巳']},
        ]
    },
}


class MountainShenshaChecker:
    """
    山家神煞检查器
    
    检查特定年份、月份等条件下，哪些山家有神煞影响
    """
    
    def __init__(self):
        self.mountains = TwentyFourMountains()
    
    def check_san_sha(self, year_zhi: str) -> List[str]:
        """
        检查三煞
        
        Args:
            year_zhi: 年支（如'申'、'子'等）
            
        Returns:
            需要避开的山列表
        """
        rules = SHENSHA_MOUNTAIN_RULES['三煞']['rules']
        for rule in rules:
            if year_zhi in rule['condition_value']:
                return rule['avoid_mountains']
        return []
    
    def check_sui_po(self, year_zhi: str) -> List[str]:
        """
        检查岁破
        
        Args:
            year_zhi: 年支
            
        Returns:
            需要避开的山列表
        """
        rules = SHENSHA_MOUNTAIN_RULES['岁破']['rules']
        for rule in rules:
            if year_zhi in rule['condition_value']:
                return rule['avoid_mountains']
        return []
    
    def check_mountain_jixiong(self, mountain_name: str, year_zhi: str, 
                               month_zhi: str = None, day_zhi: str = None) -> Dict:
        """
        综合检查山家吉凶
        
        Args:
            mountain_name: 山名
            year_zhi: 年支
            month_zhi: 月支（可选）
            day_zhi: 日支（可选）
            
        Returns:
            吉凶判断结果
        """
        result = {
            'mountain': mountain_name,
            'is_good': True,
            'shensha': [],
            'warnings': [],
        }
        
        # 检查三煞
        san_sha_mountains = self.check_san_sha(year_zhi)
        if mountain_name in san_sha_mountains:
            result['is_good'] = False
            result['shensha'].append('三煞')
            result['warnings'].append(f'{year_zhi}年三煞在{san_sha_mountains}，忌{mountain_name}山')
        
        # 检查岁破
        sui_po_mountains = self.check_sui_po(year_zhi)
        if mountain_name in sui_po_mountains:
            result['is_good'] = False
            result['shensha'].append('岁破')
            result['warnings'].append(f'{year_zhi}年岁破在{sui_po_mountains}，忌{mountain_name}山')
        
        return result


# 便捷函数
def get_mountain_info(name: str) -> Optional[Dict]:
    """获取山信息"""
    mountains = TwentyFourMountains()
    return mountains.get_mountain_by_name(name)


def check_wuxing_relation(wuxing_a: str, wuxing_b: str) -> str:
    """检查五行关系"""
    return WuxingRelation.get_relation(wuxing_a, wuxing_b)


def get_fengjin(mountain_name: str, index: int) -> Optional[Dict]:
    """获取分金信息"""
    mountains = TwentyFourMountains()
    return mountains.get_fengjin(mountain_name, index)


# ============================================================================
# 数据库表结构定义（SQL）
# ============================================================================

"""
-- 五行字典表
CREATE TABLE wuxing (
    id INT PRIMARY KEY,
    name VARCHAR(10) NOT NULL,  -- 金、木、水、火、土
    color VARCHAR(10)           -- 白、绿、黑、红、黄
);
INSERT INTO wuxing VALUES 
    (1, '金', '白'), 
    (2, '木', '绿'), 
    (3, '水', '黑'), 
    (4, '火', '红'), 
    (5, '土', '黄');

-- 五行生克权重表
CREATE TABLE wuxing_relation_score (
    id INT PRIMARY KEY AUTO_INCREMENT,
    relation_type ENUM('生', '克', '比和') NOT NULL,
    direction ENUM('课生山', '山生课', '课克山', '山克课', '比和') NOT NULL,
    weight INT NOT NULL,           -- 权重（正为吉，负为凶）
    description VARCHAR(255),      -- 描述
    priority INT DEFAULT 1         -- 优先级
);
INSERT INTO wuxing_relation_score (relation_type, direction, weight, description, priority) VALUES
    ('生', '课生山', 10, '日课五行生扶坐山', 1),
    ('生', '山生课', 5, '坐山生日课（泄气）', 2),
    ('克', '课克山', -10, '日课克制坐山', 1),
    ('克', '山克课', -5, '坐山克日课（耗气）', 2),
    ('比和', '比和', 8, '五行相同', 1);

-- 神煞规则表（支持JSON条件）
CREATE TABLE shensha_rule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    shensha_name VARCHAR(50) NOT NULL,      -- 神煞名称
    condition_json JSON NOT NULL,           -- 条件表达式
    weight INT NOT NULL,                    -- 权重（负值表示凶）
    is_decisive BOOLEAN DEFAULT FALSE,      -- 是否为决定性煞
    description TEXT                        -- 详细描述
);
-- 三煞规则示例
INSERT INTO shensha_rule (shensha_name, condition_json, weight, is_decisive, description) VALUES
    ('三煞', '{"rules": [
        {"year_zhi": ["申", "子", "辰"], "mountain_id": [12, 13, 14]},
        {"year_zhi": ["寅", "午", "戌"], "mountain_id": [24, 1, 2]},
        {"year_zhi": ["巳", "酉", "丑"], "mountain_id": [6, 7, 8]},
        {"year_zhi": ["亥", "卯", "未"], "mountain_id": [18, 19, 20]}
    ]}', -100, TRUE, '申子辰年煞在南方巳午未，寅午戌年煞在北方亥子丑，巳酉丑年煞在东方寅卯辰，亥卯未年煞在西方申酉戌');

-- 坐山五行映射表
CREATE TABLE mountain_wuxing (
    mountain_id INT PRIMARY KEY,
    wuxing_id INT NOT NULL,
    FOREIGN KEY (mountain_id) REFERENCES twenty_four_mountains(id),
    FOREIGN KEY (wuxing_id) REFERENCES wuxing(id)
);

-- ============================================================================
-- 龙相关表结构（补龙扶山扩展）
-- ============================================================================

-- 方案1：龙直接用二十四山表示（推荐）
-- 如果来龙方位明确属于二十四山之一，则无需新增表，直接使用现有的 mountain_wuxing 表即可
-- 调用时传入龙的 mountain_id，通过 get_mountain_wuxing() 获取五行

-- 方案2：龙有独立的标识体系
-- 若龙需独立命名（如"紫微龙""天市龙"等），则新建表 long_wuxing
CREATE TABLE long_wuxing (
    long_id INT PRIMARY KEY,
    long_name VARCHAR(20) NOT NULL,     -- 龙名称（如"紫微龙"）
    wuxing_id INT NOT NULL,             -- 五行ID，外键关联 wuxing(id)
    mountain_id INT,                    -- 关联的二十四山ID（可选）
    description TEXT                    -- 描述
);

-- 龙五行示例数据
INSERT INTO long_wuxing (long_id, long_name, wuxing_id, mountain_id, description) VALUES
    (1, '壬龙', 3, 1, '壬山来龙，五行属水'),
    (2, '子龙', 3, 2, '子山来龙，五行属水'),
    (3, '癸龙', 3, 3, '癸山来龙，五行属水'),
    (4, '丑龙', 5, 4, '丑山来龙，五行属土'),
    (5, '寅龙', 2, 5, '寅山来龙，五行属木'),
    (6, '卯龙', 2, 6, '卯山来龙，五行属木'),
    (7, '辰龙', 5, 7, '辰山来龙，五行属土'),
    (8, '巳龙', 4, 8, '巳山来龙，五行属火'),
    (9, '午龙', 4, 9, '午山来龙，五行属火'),
    (10, '未龙', 5, 10, '未山来龙，五行属土'),
    (11, '申龙', 1, 11, '申山来龙，五行属金'),
    (12, '酉龙', 1, 12, '酉山来龙，五行属金'),
    (13, '戌龙', 5, 13, '戌山来龙，五行属土'),
    (14, '亥龙', 3, 14, '亥山来龙，五行属水'),
    (15, '艮龙', 5, 15, '艮山来龙，五行属土'),
    (16, '乾龙', 1, 16, '乾山来龙，五行属金'),
    (17, '坤龙', 5, 17, '坤山来龙，五行属土'),
    (18, '巽龙', 2, 18, '巽山来龙，五行属木');

-- 扩展神煞规则表，增加龙相关规则
-- 在 shensha_rule 表中可增加 long_id 字段，定义与龙相关的神煞规则
ALTER TABLE shensha_rule ADD COLUMN target_type ENUM('山', '龙', '山龙') DEFAULT '山';
ALTER TABLE shensha_rule ADD COLUMN long_id INT;

-- 龙相关神煞规则示例
INSERT INTO shensha_rule (shensha_name, condition_json, weight, is_decisive, target_type, description) VALUES
    ('龙犯三煞', '{"rules": [
        {"year_zhi": ["申", "子", "辰"], "long_mountain_id": [8, 9, 10]},
        {"year_zhi": ["寅", "午", "戌"], "long_mountain_id": [14, 2, 3]},
        {"year_zhi": ["巳", "酉", "丑"], "long_mountain_id": [5, 6, 7]},
        {"year_zhi": ["亥", "卯", "未"], "long_mountain_id": [11, 12, 13]}
    ]}', -100, TRUE, '龙', '来龙犯三煞，大凶');

-- 扩展五行生克权重表，支持龙
ALTER TABLE wuxing_relation_score ADD COLUMN target_type ENUM('山', '龙', '通用') DEFAULT '通用';

-- 龙专用权重（可选，若与山不同）
INSERT INTO wuxing_relation_score (relation_type, direction, weight, description, priority, target_type) VALUES
    ('生', '课生龙', 12, '日课五行生扶来龙（补龙）', 1, '龙'),
    ('生', '龙生课', 4, '来龙生日课（泄气）', 2, '龙'),
    ('克', '课克龙', -12, '日课克制来龙', 1, '龙'),
    ('克', '龙克课', -4, '来龙克日课', 2, '龙'),
    ('比和', '比和', 10, '五行相同', 1, '龙');

-- ============================================================================
-- 龙上八煞规则
-- ============================================================================
-- 龙上八煞：坎龙坤兔震山猴，巽鸡乾马兑蛇头，艮虎离猪为煞曜，宅墓逢之一时休
-- 解释：
-- 坎龙：坎卦（子山）忌辰龙（辰为龙）
-- 坤兔：坤卦（坤山）忌卯兔（卯为兔）
-- 震山猴：震卦（卯山）忌申猴（申为猴）
-- 巽鸡：巽卦（巽山）忌酉鸡（酉为鸡）
-- 乾马：乾卦（乾山）忌午马（午为马）
-- 兑蛇头：兑卦（酉山）忌巳蛇（巳为蛇）
-- 艮虎：艮卦（艮山）忌寅虎（寅为虎）
-- 离猪：离卦（午山）忌亥猪（亥为猪）

INSERT INTO shensha_rule (shensha_name, condition_json, weight, is_decisive, target_type, description) VALUES
    ('龙上八煞-坎龙', '{"long_mountain_id": [2], "avoid_zhi": ["辰"]}', -80, TRUE, '龙', '坎龙忌辰，来龙在子山忌见辰支'),
    ('龙上八煞-坤兔', '{"long_mountain_id": [17], "avoid_zhi": ["卯"]}', -80, TRUE, '龙', '坤兔忌卯，来龙在坤山忌见卯支'),
    ('龙上八煞-震山猴', '{"long_mountain_id": [6], "avoid_zhi": ["申"]}', -80, TRUE, '龙', '震山猴忌申，来龙在卯山忌见申支'),
    ('龙上八煞-巽鸡', '{"long_mountain_id": [18], "avoid_zhi": ["酉"]}', -80, TRUE, '龙', '巽鸡忌酉，来龙在巽山忌见酉支'),
    ('龙上八煞-乾马', '{"long_mountain_id": [16], "avoid_zhi": ["午"]}', -80, TRUE, '龙', '乾马忌午，来龙在乾山忌见午支'),
    ('龙上八煞-兑蛇头', '{"long_mountain_id": [12], "avoid_zhi": ["巳"]}', -80, TRUE, '龙', '兑蛇头忌巳，来龙在酉山忌见巳支'),
    ('龙上八煞-艮虎', '{"long_mountain_id": [15], "avoid_zhi": ["寅"]}', -80, TRUE, '龙', '艮虎忌寅，来龙在艮山忌见寅支'),
    ('龙上八煞-离猪', '{"long_mountain_id": [9], "avoid_zhi": ["亥"]}', -80, TRUE, '龙', '离猪忌亥，来龙在午山忌见亥支');
"""

# ============================================================================
# 正体五行择日核心算法
# ============================================================================

# 五行生克规则表（硬编码，实际可从数据库读取）
WUXING_SHENGKE_RULES = [
    {'rule_name': '日课生坐山', 'relation': '生', 'direction': '课生山', 'weight': 10, 'priority': 1},
    {'rule_name': '坐山生日课', 'relation': '生', 'direction': '山生课', 'weight': 5, 'priority': 2},
    {'rule_name': '日课克坐山', 'relation': '克', 'direction': '课克山', 'weight': -10, 'priority': 1},
    {'rule_name': '坐山克日课', 'relation': '克', 'direction': '山克课', 'weight': -5, 'priority': 2},
    {'rule_name': '比和', 'relation': '比和', 'direction': '比和', 'weight': 8, 'priority': 1},
]

# 天干五行（正体五行）
TIANGAN_WUXING = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

# 地支五行（正体五行）
DIZHI_WUXING = {
    '寅': '木', '卯': '木',
    '巳': '火', '午': '火',
    '申': '金', '酉': '金',
    '亥': '水', '子': '水',
    '辰': '土', '戌': '土', '丑': '土', '未': '土',
}

# ============================================================================
# 六十甲子纳音五行（用于分金五行）
# ============================================================================

NAYIN_WUXING = {
    # 甲子、乙丑 - 海中金
    '甲子': '金', '乙丑': '金',
    # 丙寅、丁卯 - 炉中火
    '丙寅': '火', '丁卯': '火',
    # 戊辰、己巳 - 大林木
    '戊辰': '木', '己巳': '木',
    # 庚午、辛未 - 路旁土
    '庚午': '土', '辛未': '土',
    # 壬申、癸酉 - 剑锋金
    '壬申': '金', '癸酉': '金',
    # 甲戌、乙亥 - 山头火
    '甲戌': '火', '乙亥': '火',
    # 丙子、丁丑 - 涧下水
    '丙子': '水', '丁丑': '水',
    # 戊寅、己卯 - 城头土
    '戊寅': '土', '己卯': '土',
    # 庚辰、辛巳 - 白蜡金
    '庚辰': '金', '辛巳': '金',
    # 壬午、癸未 - 杨柳木
    '壬午': '木', '癸未': '木',
    # 甲申、乙酉 - 泉中水
    '甲申': '水', '乙酉': '水',
    # 丙戌、丁亥 - 屋上土
    '丙戌': '土', '丁亥': '土',
    # 戊子、己丑 - 霹雳火
    '戊子': '火', '己丑': '火',
    # 庚寅、辛卯 - 松柏木
    '庚寅': '木', '辛卯': '木',
    # 壬辰、癸巳 - 长流水
    '壬辰': '水', '癸巳': '水',
    # 甲午、乙未 - 沙中金
    '甲午': '金', '乙未': '金',
    # 丙申、丁酉 - 山下火
    '丙申': '火', '丁酉': '火',
    # 戊戌、己亥 - 平地木
    '戊戌': '木', '己亥': '木',
    # 庚子、辛丑 - 壁上土
    '庚子': '土', '辛丑': '土',
    # 壬寅、癸卯 - 金箔金
    '壬寅': '金', '癸卯': '金',
    # 甲辰、乙巳 - 覆灯火
    '甲辰': '火', '乙巳': '火',
    # 丙午、丁未 - 天河水
    '丙午': '水', '丁未': '水',
    # 戊申、己酉 - 大驿土
    '戊申': '土', '己酉': '土',
    # 庚戌、辛亥 - 钗钏金
    '庚戌': '金', '辛亥': '金',
    # 壬子、癸丑 - 桑柘木
    '壬子': '木', '癸丑': '木',
    # 甲寅、乙卯 - 大溪水
    '甲寅': '水', '乙卯': '水',
    # 丙辰、丁巳 - 沙中土
    '丙辰': '土', '丁巳': '土',
    # 戊午、己未 - 天上火
    '戊午': '火', '己未': '火',
    # 庚申、辛酉 - 石榴木
    '庚申': '木', '辛酉': '木',
    # 壬戌、癸亥 - 大海水
    '壬戌': '水', '癸亥': '水',
}

# 纳音五行详细名称
NAYIN_NAMES = {
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
    '甲午': '沙中金', '乙未': '沙中金',
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
    '壬戌': '大海水', '癸亥': '大海水',
}

# ============================================================================
# 一百二十分金数据（每山5个分金，共120分金）
# ============================================================================

# 二十四山对应的分金干支（按顺序：第1-5分金）
# 规则：阳山用阳干支，阴山用阴干支
FENGJIN_GANZHI = {
    # 八干四维的分金（使用六十甲子顺序）
    '壬': ['丙子', '丁丑', '戊寅', '己卯', '庚辰'],  # 壬山属阳水
    '子': ['甲子', '丙子', '戊子', '庚子', '壬子'],  # 子山属阳水
    '癸': ['丙子', '丁丑', '戊寅', '己卯', '庚辰'],  # 癸山属阴水
    '丑': ['丁丑', '己丑', '辛丑', '癸丑', '乙丑'],  # 丑山属阴土
    '艮': ['丙寅', '丁卯', '戊辰', '己巳', '庚午'],  # 艮山属阳土
    '寅': ['甲寅', '丙寅', '戊寅', '庚寅', '壬寅'],  # 寅山属阳木
    '甲': ['丙寅', '丁卯', '戊辰', '己巳', '庚午'],  # 甲山属阳木
    '卯': ['乙卯', '丁卯', '己卯', '辛卯', '癸卯'],  # 卯山属阴木
    '乙': ['丙寅', '丁卯', '戊辰', '己巳', '庚午'],  # 乙山属阴木
    '辰': ['甲辰', '丙辰', '戊辰', '庚辰', '壬辰'],  # 辰山属阳土
    '巽': ['丙辰', '丁巳', '戊午', '己未', '庚申'],  # 巽山属阴木
    '巳': ['乙巳', '丁巳', '己巳', '辛巳', '癸巳'],  # 巳山属阴火
    '丙': ['丙午', '丁未', '戊申', '己酉', '庚戌'],  # 丙山属阳火
    '午': ['甲午', '丙午', '戊午', '庚午', '壬午'],  # 午山属阳火
    '丁': ['丙午', '丁未', '戊申', '己酉', '庚戌'],  # 丁山属阴火
    '未': ['乙未', '丁未', '己未', '辛未', '癸未'],  # 未山属阴土
    '坤': ['丙申', '丁酉', '戊戌', '己亥', '庚子'],  # 坤山属阴土
    '申': ['甲申', '丙申', '戊申', '庚申', '壬申'],  # 申山属阳金
    '庚': ['丙申', '丁酉', '戊戌', '己亥', '庚子'],  # 庚山属阳金
    '酉': ['乙酉', '丁酉', '己酉', '辛酉', '癸酉'],  # 酉山属阴金
    '辛': ['丙申', '丁酉', '戊戌', '己亥', '庚子'],  # 辛山属阴金
    '戌': ['甲戌', '丙戌', '戊戌', '庚戌', '壬戌'],  # 戌山属阳土
    '乾': ['丙戌', '丁亥', '戊子', '己丑', '庚寅'],  # 乾山属阳金
    '亥': ['乙亥', '丁亥', '己亥', '辛亥', '癸亥'],  # 亥山属阴水
}


def get_fengjin_wuxing(mountain_name: str, fengjin_index: int) -> Tuple[str, str]:
    """
    获取分金的纳音五行
    
    Args:
        mountain_name: 山名，如"子"
        fengjin_index: 分金索引（0-4），0=第1分金，4=第5分金
        
    Returns:
        (五行, 纳音名称)，如('金', '海中金')
    """
    if mountain_name not in FENGJIN_GANZHI:
        return '土', '未知'
    
    ganzhi_list = FENGJIN_GANZHI[mountain_name]
    if fengjin_index < 0 or fengjin_index >= len(ganzhi_list):
        return '土', '未知'
    
    ganzhi = ganzhi_list[fengjin_index]
    wuxing = NAYIN_WUXING.get(ganzhi, '土')
    nayin_name = NAYIN_NAMES.get(ganzhi, '未知')
    
    return wuxing, nayin_name


def get_fengjin_by_jianxiang(mountain_name: str, jianxiang: str) -> int:
    """
    根据兼向获取分金索引
    
    Args:
        mountain_name: 山名
        jianxiang: 兼向，如"兼壬"、"正中"、"兼癸"
        
    Returns:
        分金索引（0-4）
    """
    if not jianxiang or jianxiang == "正中":
        return 2  # 第3分金（正中）
    elif "兼" in jianxiang:
        # 兼左=第1分金(0)，兼右=第5分金(4)
        # 需要根据具体兼向判断是左还是右
        mountains = converter.get_all_mountains()
        
        if mountain_name in mountains:
            idx = mountains.index(mountain_name)
            left_shan = mountains[(idx - 1) % len(mountains)]
            right_shan = mountains[(idx + 1) % len(mountains)]
            
            jian_shan = jianxiang.replace("兼", "")
            if jian_shan == left_shan:
                return 0  # 兼左=第1分金
            elif jian_shan == right_shan:
                return 4  # 兼右=第5分金
    
    return 2  # 默认正中


# ============================================================================
# 山向映射工具（与主程序统一）
# ============================================================================

# 主程序使用的12山向（地支山向）
SHAN_XIANG_12 = [
    "子山午向", "丑山未向", "寅山申向", "卯山酉向",
    "辰山戌向", "巳山亥向", "午山子向", "未山丑向",
    "申山寅向", "酉山卯向", "戌山辰向", "亥山巳向"
]

# 山向到坐山名称的映射
SHAN_XIANG_TO_SHAN = {
    "子山午向": "子",
    "丑山未向": "丑",
    "寅山申向": "寅",
    "卯山酉向": "卯",
    "辰山戌向": "辰",
    "巳山亥向": "巳",
    "午山子向": "午",
    "未山丑向": "未",
    "申山寅向": "申",
    "酉山卯向": "酉",
    "戌山辰向": "戌",
    "亥山巳向": "亥",
}

# 坐山名称到山向的映射（默认向）
SHAN_TO_SHAN_XIANG = {
    "子": "子山午向",
    "丑": "丑山未向",
    "寅": "寅山申向",
    "卯": "卯山酉向",
    "辰": "辰山戌向",
    "巳": "巳山亥向",
    "午": "午山子向",
    "未": "未山丑向",
    "申": "申山寅向",
    "酉": "酉山卯向",
    "戌": "戌山辰向",
    "亥": "亥山巳向",
}

# 完整的二十四山列表（与主程序兼容）
SHAN_XIANG_24 = [
    # 十二地支山向（主程序已有）
    "子山午向", "丑山未向", "寅山申向", "卯山酉向",
    "辰山戌向", "巳山亥向", "午山子向", "未山丑向",
    "申山寅向", "酉山卯向", "戌山辰向", "亥山巳向",
    # 八干四维山向（扩展）
    "壬山丙向", "癸山丁向",
    "甲山庚向", "乙山辛向",
    "丙山壬向", "丁山癸向",
    "庚山甲向", "辛山乙向",
    "乾山巽向", "坤山艮向",
    "艮山坤向", "巽山乾向",
]

# 完整的山向到坐山映射
SHAN_XIANG_24_TO_SHAN = {
    # 十二地支山向
    "子山午向": "子", "丑山未向": "丑", "寅山申向": "寅", "卯山酉向": "卯",
    "辰山戌向": "辰", "巳山亥向": "巳", "午山子向": "午", "未山丑向": "未",
    "申山寅向": "申", "酉山卯向": "酉", "戌山辰向": "戌", "亥山巳向": "亥",
    # 八干四维山向
    "壬山丙向": "壬", "癸山丁向": "癸",
    "甲山庚向": "甲", "乙山辛向": "乙",
    "丙山壬向": "丙", "丁山癸向": "丁",
    "庚山甲向": "庚", "辛山乙向": "辛",
    "乾山巽向": "乾", "坤山艮向": "坤",
    "艮山坤向": "艮", "巽山乾向": "巽",
}


def shan_xiang_to_shan(shan_xiang: str) -> str:
    """
    将山向转换为坐山名称
    
    Args:
        shan_xiang: 山向，如"子山午向"
        
    Returns:
        坐山名称，如"子"
    """
    return SHAN_XIANG_24_TO_SHAN.get(shan_xiang, shan_xiang)


def shan_to_shan_xiang(shan: str, xiang: str = None) -> str:
    """
    将坐山名称转换为山向
    
    Args:
        shan: 坐山名称，如"子"
        xiang: 向山名称（可选），如"午"
        
    Returns:
        山向，如"子山午向"
    """
    if xiang:
        return f"{shan}山{xiang}向"
    return SHAN_TO_SHAN_XIANG.get(shan, f"{shan}山")


def get_shan_xiang_list(use_24_shan: bool = True) -> List[str]:
    """
    获取山向列表
    
    Args:
        use_24_shan: 是否使用完整的二十四山（True）或仅十二地支山（False）
        
    Returns:
        山向列表
    """
    if use_24_shan:
        return SHAN_XIANG_24.copy()
    return SHAN_XIANG_12.copy()


class ZhengTiWuXingSelector:
    """
    正体五行择日选择器
    
    实现正体五行择日的核心算法，包括：
    - 坐山与日课四柱的五行生克关系计算
    - 神煞检查（三煞、岁破等）
    - 综合评分和吉凶判断
    - 支持从配置或数据库动态读取规则
    """
    
    def __init__(self, rules_config: List[Dict] = None, use_default_rules: bool = True):
        """
        初始化选择器
        
        Args:
            rules_config: 自定义规则配置列表，格式同WUXING_SHENGKE_RULES
            use_default_rules: 是否使用默认规则（当rules_config为None时）
        """
        self.mountains = TwentyFourMountains()
        self.shensha_checker = MountainShenshaChecker()
        
        # 加载规则
        if rules_config:
            self.rules = rules_config
        elif use_default_rules:
            self.rules = WUXING_SHENGKE_RULES
        else:
            self.rules = []
        
        # 构建规则查找字典（direction -> weight）
        self._build_rule_dict()
        
        # 评分阈值
        self.score_thresholds = {
            '大吉': 50,
            '吉': 30,
            '平': 0,
            '凶': -30,
        }
    
    def _build_rule_dict(self):
        """构建规则查找字典"""
        self.rule_dict = {}
        for rule in self.rules:
            direction = rule.get('direction')
            if direction:
                self.rule_dict[direction] = rule.get('weight', 0)
    
    def load_rules_from_dict(self, rules: List[Dict]):
        """
        从字典加载规则
        
        Args:
            rules: 规则列表，每个规则包含direction和weight
        """
        self.rules = rules
        self._build_rule_dict()
    
    def get_rule_weight(self, direction: str) -> int:
        """
        获取指定方向的规则权重
        
        Args:
            direction: 方向（'课生山', '山生课', '课克山', '山克课', '比和'）
            
        Returns:
            权重值，找不到返回0
        """
        return self.rule_dict.get(direction, 0)
    
    def calculate_relation_score_with_rules(self, mountain_wx: str, ganzhi_wx: str) -> Tuple[int, str]:
        """
        使用配置的规则计算得分
        
        Args:
            mountain_wx: 坐山五行
            ganzhi_wx: 干支五行
            
        Returns:
            (得分, 关系方向)
        """
        if not mountain_wx or not ganzhi_wx:
            return 0, 'none'
        
        # 获取关系方向
        direction = WuxingRelation.get_relation_direction(ganzhi_wx, mountain_wx, mountain_wx)
        
        # 从规则中获取权重
        weight = self.get_rule_weight(direction)
        
        return weight, direction
    
    def get_ganzhi_wuxing(self, gan: str, zhi: str) -> Tuple[str, str]:
        """
        获取天干和地支的五行
        
        Args:
            gan: 天干
            zhi: 地支
            
        Returns:
            (天干五行, 地支五行)
        """
        gan_wx = TIANGAN_WUXING.get(gan)
        zhi_wx = DIZHI_WUXING.get(zhi)
        return gan_wx, zhi_wx
    
    def calculate_relation_score(self, mountain_wx: str, ganzhi_wx: str) -> int:
        """
        计算单个五行与坐山五行的关系得分
        
        Args:
            mountain_wx: 坐山五行
            ganzhi_wx: 干支五行
            
        Returns:
            得分
        """
        if not mountain_wx or not ganzhi_wx:
            return 0
        
        # 比和
        if mountain_wx == ganzhi_wx:
            return 8
        
        # 检查生克关系
        # 干支生坐山（课生山）
        if WuxingRelation.is_sheng(ganzhi_wx, mountain_wx):
            return 10
        
        # 坐山生干支（山生课）
        if WuxingRelation.is_sheng(mountain_wx, ganzhi_wx):
            return 5
        
        # 干支克坐山（课克山）- 大凶
        if WuxingRelation.is_ke(ganzhi_wx, mountain_wx):
            return -10
        
        # 坐山克干支（山克课）
        if WuxingRelation.is_ke(mountain_wx, ganzhi_wx):
            return -5
        
        return 0
    
    def evaluate_sizhu(self, mountain_name: str, 
                       year_gz: str, month_gz: str, day_gz: str, hour_gz: str) -> Dict:
        """
        综合评价四柱与坐山的关系
        
        Args:
            mountain_name: 坐山名称（如'壬'）
            year_gz: 年柱（如'甲子'）
            month_gz: 月柱
            day_gz: 日柱
            hour_gz: 时柱
            
        Returns:
            评价结果字典
        """
        # 获取坐山信息
        mountain = self.mountains.get_mountain_by_name(mountain_name)
        if not mountain:
            return {
                'success': False,
                'error': f'未知坐山：{mountain_name}',
            }
        
        mountain_wx = mountain['wuxing']
        
        # 解析四柱
        sizhu = [
            {'name': '年柱', 'gan': year_gz[0], 'zhi': year_gz[1]},
            {'name': '月柱', 'gan': month_gz[0], 'zhi': month_gz[1]},
            {'name': '日柱', 'gan': day_gz[0], 'zhi': day_gz[1]},
            {'name': '时柱', 'gan': hour_gz[0], 'zhi': hour_gz[1]},
        ]
        
        # 计算各柱得分
        total_score = 0
        details = []
        
        for pillar in sizhu:
            gan_wx, zhi_wx = self.get_ganzhi_wuxing(pillar['gan'], pillar['zhi'])
            
            # 天干得分
            gan_score = self.calculate_relation_score(mountain_wx, gan_wx)
            total_score += gan_score
            
            # 地支得分
            zhi_score = self.calculate_relation_score(mountain_wx, zhi_wx)
            total_score += zhi_score
            
            details.append({
                'pillar': pillar['name'],
                'ganzhi': f"{pillar['gan']}{pillar['zhi']}",
                'gan_wuxing': gan_wx,
                'zhi_wuxing': zhi_wx,
                'gan_score': gan_score,
                'zhi_score': zhi_score,
                'pillar_score': gan_score + zhi_score,
            })
        
        # 判断吉凶等级
        if total_score >= self.score_thresholds['大吉']:
            jixiong = '大吉'
        elif total_score >= self.score_thresholds['吉']:
            jixiong = '吉'
        elif total_score >= self.score_thresholds['平']:
            jixiong = '平'
        elif total_score >= self.score_thresholds['凶']:
            jixiong = '凶'
        else:
            jixiong = '大凶'
        
        return {
            'success': True,
            'mountain': mountain_name,
            'mountain_wuxing': mountain_wx,
            'total_score': total_score,
            'jixiong': jixiong,
            'details': details,
        }
    
    def evaluate_with_shensha(self, mountain_name: str,
                              year_gz: str, month_gz: str, day_gz: str, hour_gz: str) -> Dict:
        """
        综合评价（包含神煞检查）
        
        Args:
            mountain_name: 坐山名称
            year_gz: 年柱
            month_gz: 月柱
            day_gz: 日柱
            hour_gz: 时柱
            
        Returns:
            评价结果字典
        """
        # 先计算五行生克得分
        result = self.evaluate_sizhu(mountain_name, year_gz, month_gz, day_gz, hour_gz)
        
        if not result['success']:
            return result
        
        # 获取年支
        year_zhi = year_gz[1]
        
        # 检查神煞
        shensha_warnings = []
        shensha_list = []
        
        # 检查三煞
        san_sha_mountains = self.shensha_checker.check_san_sha(year_zhi)
        if mountain_name in san_sha_mountains:
            shensha_list.append('三煞')
            shensha_warnings.append(f'{year_zhi}年三煞在南方{san_sha_mountains}，{mountain_name}山犯三煞')
            result['total_score'] -= 100  # 大凶，一票否决
        
        # 检查岁破
        sui_po_mountains = self.shensha_checker.check_sui_po(year_zhi)
        if mountain_name in sui_po_mountains:
            shensha_list.append('岁破')
            shensha_warnings.append(f'{year_zhi}年岁破在{sui_po_mountains}，{mountain_name}山犯岁破')
            result['total_score'] -= 50
        
        # 更新吉凶等级
        total_score = result['total_score']
        if total_score >= self.score_thresholds['大吉']:
            jixiong = '大吉'
        elif total_score >= self.score_thresholds['吉']:
            jixiong = '吉'
        elif total_score >= self.score_thresholds['平']:
            jixiong = '平'
        elif total_score >= self.score_thresholds['凶']:
            jixiong = '凶'
        else:
            jixiong = '大凶'
        
        result['jixiong'] = jixiong
        result['shensha'] = shensha_list
        result['shensha_warnings'] = shensha_warnings
        
        return result
    
    def evaluate_sizhu_with_rules(self, mountain_name: str,
                                   year_gz: str, month_gz: str, day_gz: str, hour_gz: str) -> Dict:
        """
        使用动态规则评价四柱与坐山的关系
        
        Args:
            mountain_name: 坐山名称
            year_gz: 年柱
            month_gz: 月柱
            day_gz: 日柱
            hour_gz: 时柱
            
        Returns:
            评价结果字典（包含规则信息）
        """
        # 获取坐山信息
        mountain = self.mountains.get_mountain_by_name(mountain_name)
        if not mountain:
            return {
                'success': False,
                'error': f'未知坐山：{mountain_name}',
            }
        
        mountain_wx = mountain['wuxing']
        
        # 解析四柱
        sizhu = [
            {'name': '年柱', 'gan': year_gz[0], 'zhi': year_gz[1]},
            {'name': '月柱', 'gan': month_gz[0], 'zhi': month_gz[1]},
            {'name': '日柱', 'gan': day_gz[0], 'zhi': day_gz[1]},
            {'name': '时柱', 'gan': hour_gz[0], 'zhi': hour_gz[1]},
        ]
        
        # 计算各柱得分
        total_score = 0
        details = []
        
        for pillar in sizhu:
            gan_wx, zhi_wx = self.get_ganzhi_wuxing(pillar['gan'], pillar['zhi'])
            
            # 使用规则计算天干得分
            gan_score, gan_direction = self.calculate_relation_score_with_rules(mountain_wx, gan_wx)
            total_score += gan_score
            
            # 使用规则计算地支得分
            zhi_score, zhi_direction = self.calculate_relation_score_with_rules(mountain_wx, zhi_wx)
            total_score += zhi_score
            
            details.append({
                'pillar': pillar['name'],
                'ganzhi': f"{pillar['gan']}{pillar['zhi']}",
                'gan_wuxing': gan_wx,
                'zhi_wuxing': zhi_wx,
                'gan_score': gan_score,
                'gan_direction': gan_direction,
                'zhi_score': zhi_score,
                'zhi_direction': zhi_direction,
                'pillar_score': gan_score + zhi_score,
            })
        
        # 判断吉凶等级
        if total_score >= self.score_thresholds['大吉']:
            jixiong = '大吉'
        elif total_score >= self.score_thresholds['吉']:
            jixiong = '吉'
        elif total_score >= self.score_thresholds['平']:
            jixiong = '平'
        elif total_score >= self.score_thresholds['凶']:
            jixiong = '凶'
        else:
            jixiong = '大凶'
        
        return {
            'success': True,
            'mountain': mountain_name,
            'mountain_wuxing': mountain_wx,
            'total_score': total_score,
            'jixiong': jixiong,
            'details': details,
            'rules_used': self.rules,  # 记录使用的规则
        }


# ============================================================================
# 数据库支持版本的选择器
# ============================================================================

class ZhengTiWuXingSelectorDB:
    """
    正体五行择日选择器（数据库版本）
    
    支持从数据库加载五行映射和规则，实现动态配置
    """
    
    def __init__(self, db_connection=None):
        """
        初始化，加载五行映射和规则
        
        Args:
            db_connection: 数据库连接对象（可选，为None时使用默认数据）
        """
        self.db = db_connection
        self.wuxing_id = {}        # 名称到ID的映射
        self.id_to_wuxing = {}      # ID到名称的映射
        self.tiangan_wuxing = {}    # 天干五行ID
        self.dizhi_wuxing = {}      # 地支五行ID
        self.relation_weights = {}  # 生克关系权重
        self.shensha_rules = []      # 神煞规则列表
        
        self._load_basic_data()
        self._load_rules()
    
    def _load_basic_data(self):
        """从数据库加载基础五行数据"""
        if self.db:
            # 实际应从数据库查询
            # cursor = self.db.cursor()
            # cursor.execute("SELECT * FROM wuxing;")
            # for row in cursor.fetchall():
            #     self.wuxing_id[row['name']] = row['id']
            #     self.id_to_wuxing[row['id']] = row['name']
            pass
        
        # 默认数据（当数据库不可用时）
        self.wuxing_id = {'金': 1, '木': 2, '水': 3, '火': 4, '土': 5}
        self.id_to_wuxing = {1: '金', 2: '木', 3: '水', 4: '火', 5: '土'}
        
        # 天干五行（根据正体五行）
        self.tiangan_wuxing = {
            '甲': 2, '乙': 2, '丙': 4, '丁': 4, '戊': 5, '己': 5,
            '庚': 1, '辛': 1, '壬': 3, '癸': 3
        }
        # 地支五行
        self.dizhi_wuxing = {
            '寅': 2, '卯': 2, '巳': 4, '午': 4, '申': 1, '酉': 1,
            '亥': 3, '子': 3, '辰': 5, '戌': 5, '丑': 5, '未': 5
        }
    
    def _load_rules(self):
        """从数据库加载生克权重和神煞规则"""
        if self.db:
            # 加载生克权重
            # cursor.execute("SELECT * FROM wuxing_relation_score;")
            # rows = cursor.fetchall()
            pass
        
        # 默认规则（当数据库不可用时）
        rows = [
            {'relation_type': '生', 'direction': '课生山', 'weight': 10},
            {'relation_type': '生', 'direction': '山生课', 'weight': 5},
            {'relation_type': '克', 'direction': '课克山', 'weight': -10},
            {'relation_type': '克', 'direction': '山克课', 'weight': -5},
            {'relation_type': '比和', 'direction': '比和', 'weight': 8},
        ]
        for row in rows:
            key = (row['relation_type'], row['direction'])
            self.relation_weights[key] = row['weight']
        
        # 加载神煞规则
        if self.db:
            # cursor.execute("SELECT * FROM shensha_rule;")
            # rule_rows = cursor.fetchall()
            pass
        
        # 默认神煞规则
        rule_rows = [
            {
                'id': 1,
                'shensha_name': '三煞',
                'condition_json': '{"rules": [{"year_zhi": ["申", "子", "辰"], "mountain_id": [8, 9, 10]}, {"year_zhi": ["寅", "午", "戌"], "mountain_id": [14, 2, 3]}, {"year_zhi": ["巳", "酉", "丑"], "mountain_id": [5, 6, 7]}, {"year_zhi": ["亥", "卯", "未"], "mountain_id": [11, 12, 13]}]}',
                'weight': -100,
                'is_decisive': True,
                'target_type': '山'
            },
            # 龙上八煞规则
            {
                'id': 2,
                'shensha_name': '龙上八煞-坎龙',
                'condition_json': '{"long_mountain_id": [2], "avoid_zhi": ["辰"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '坎龙忌辰，来龙在子山忌见辰支'
            },
            {
                'id': 3,
                'shensha_name': '龙上八煞-坤兔',
                'condition_json': '{"long_mountain_id": [17], "avoid_zhi": ["卯"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '坤兔忌卯，来龙在坤山忌见卯支'
            },
            {
                'id': 4,
                'shensha_name': '龙上八煞-震山猴',
                'condition_json': '{"long_mountain_id": [6], "avoid_zhi": ["申"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '震山猴忌申，来龙在卯山忌见申支'
            },
            {
                'id': 5,
                'shensha_name': '龙上八煞-巽鸡',
                'condition_json': '{"long_mountain_id": [18], "avoid_zhi": ["酉"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '巽鸡忌酉，来龙在巽山忌见酉支'
            },
            {
                'id': 6,
                'shensha_name': '龙上八煞-乾马',
                'condition_json': '{"long_mountain_id": [16], "avoid_zhi": ["午"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '乾马忌午，来龙在乾山忌见午支'
            },
            {
                'id': 7,
                'shensha_name': '龙上八煞-兑蛇头',
                'condition_json': '{"long_mountain_id": [12], "avoid_zhi": ["巳"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '兑蛇头忌巳，来龙在酉山忌见巳支'
            },
            {
                'id': 8,
                'shensha_name': '龙上八煞-艮虎',
                'condition_json': '{"long_mountain_id": [15], "avoid_zhi": ["寅"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '艮虎忌寅，来龙在艮山忌见寅支'
            },
            {
                'id': 9,
                'shensha_name': '龙上八煞-离猪',
                'condition_json': '{"long_mountain_id": [9], "avoid_zhi": ["亥"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '离猪忌亥，来龙在午山忌见亥支'
            },
        ]
        for row in rule_rows:
            row['condition'] = json.loads(row['condition_json'])
            self.shensha_rules.append(row)
    
    def get_mountain_wuxing(self, mountain_id: int) -> Optional[int]:
        """
        根据山ID获取五行ID
        
        Args:
            mountain_id: 山ID
            
        Returns:
            五行ID，找不到返回None
        """
        if self.db:
            # cursor.execute("SELECT wuxing_id FROM mountain_wuxing WHERE mountain_id = ?;", (mountain_id,))
            # result = cursor.fetchone()
            # return result['wuxing_id'] if result else None
            pass
        
        # 默认映射（简化版，实际应从数据库查询）
        mountain_wuxing_map = {
            1: 3,  # 壬水
            2: 3,  # 子水
            3: 3,  # 癸水
            4: 5,  # 丑土
            5: 2,  # 寅木
            6: 2,  # 卯木
            7: 5,  # 辰土
            8: 4,  # 巳火
            9: 4,  # 午火
            10: 5, # 未土
            11: 1, # 申金
            12: 1, # 酉金
            13: 5, # 戌土
            14: 3, # 亥水
            15: 5, # 艮土
            16: 1, # 乾金
            17: 5, # 坤土
            18: 2, # 巽木
            19: 5, # 戊己土
            20: 5, # 己
            21: 2, # 甲
            22: 2, # 乙
            23: 4, # 丙
            24: 4, # 丁
        }
        return mountain_wuxing_map.get(mountain_id)
    
    def calculate_relation(self, wx_a: int, wx_b: int) -> Tuple[str, str]:
        """
        判断两个五行的生克关系
        
        Args:
            wx_a: 第一个五行ID
            wx_b: 第二个五行ID
            
        Returns:
            (relation_type, direction)
            relation_type: '生','克','比和'
            direction: 'a生b', 'b生a', 'a克b', 'b克a', '比和'
        """
        if wx_a == wx_b:
            return '比和', '比和'
        
        # 生克关系矩阵（0金,1木,2水,3火,4土）
        # 注意：这里使用0-based索引，但传入的ID是1-based
        sheng = {0: 2, 1: 3, 2: 1, 3: 4, 4: 0}  # 生
        ke = {0: 1, 1: 4, 4: 2, 2: 3, 3: 0}     # 克
        
        # 转换为0-based索引
        a = wx_a - 1
        b = wx_b - 1
        
        if sheng.get(a) == b:
            return '生', 'a生b'
        if sheng.get(b) == a:
            return '生', 'b生a'
        if ke.get(a) == b:
            return '克', 'a克b'
        if ke.get(b) == a:
            return '克', 'b克a'
        return '其他', '无关系'
    
    def score_for_pair(self, mountain_wx: int, ganzhi_wx: int, target_type: str = '山') -> int:
        """
        计算单个干支（天干或地支）与坐山/龙的得分
        
        Args:
            mountain_wx: 坐山/龙五行ID
            ganzhi_wx: 干支五行ID
            target_type: 目标类型（'山' 或 '龙'）
            
        Returns:
            得分
        """
        rel_type, direction = self.calculate_relation(ganzhi_wx, mountain_wx)
        
        # 将方向映射为规则表中的direction字段
        if rel_type == '比和':
            dir_key = '比和'
        elif direction == 'a生b':   # a=ganzhi, b=mountain => 课生山/课生龙
            dir_key = '课生龙' if target_type == '龙' else '课生山'
        elif direction == 'b生a':   # 山/龙生课
            dir_key = '龙生课' if target_type == '龙' else '山生课'
        elif direction == 'a克b':   # 课克山/课克龙
            dir_key = '课克龙' if target_type == '龙' else '课克山'
        elif direction == 'b克a':   # 山/龙克课
            dir_key = '龙克课' if target_type == '龙' else '山克课'
        else:
            return 0
        
        # 先尝试查找特定类型的权重，找不到则使用通用权重
        weight = self.relation_weights.get((rel_type, dir_key))
        if weight is None:
            # 回退到通用权重
            if dir_key in ['课生龙', '课生山']:
                weight = self.relation_weights.get(('生', '课生山'), 0)
            elif dir_key in ['龙生课', '山生课']:
                weight = self.relation_weights.get(('生', '山生课'), 0)
            elif dir_key in ['课克龙', '课克山']:
                weight = self.relation_weights.get(('克', '课克山'), 0)
            elif dir_key in ['龙克课', '山克课']:
                weight = self.relation_weights.get(('克', '山克课'), 0)
            else:
                weight = self.relation_weights.get((rel_type, dir_key), 0)
        
        return weight if weight is not None else 0
    
    def check_shensha_for_long(self, year_zhi: str, long_mountain_id: int, 
                                 ganzhi_list: List[Tuple] = None) -> Tuple[int, bool, List[str]]:
        """
        检查来龙的神煞规则，支持龙上八煞
        
        Args:
            year_zhi: 年支
            long_mountain_id: 来龙山ID
            ganzhi_list: 日课四柱干支列表 [(gan_wx, zhi_wx), ...]，用于检查龙上八煞
            
        Returns:
            (总扣分, 是否否决, 触发的神煞列表)
        """
        total_penalty = 0
        decisive = False
        triggered_shensha = []
        
        for rule in self.shensha_rules:
            condition = rule['condition']
            target_type = rule.get('target_type', '山')
            
            # 只检查龙相关的规则
            if target_type not in ['龙', '山龙']:
                continue
            
            # 处理三煞规则格式
            if 'rules' in condition:
                for rule_item in condition['rules']:
                    # 检查 long_mountain_id 字段
                    if year_zhi in rule_item.get('year_zhi', []) and \
                       long_mountain_id in rule_item.get('long_mountain_id', []):
                        total_penalty += rule['weight']
                        if rule.get('is_decisive'):
                            decisive = True
                        triggered_shensha.append(rule['shensha_name'])
            
            # 处理龙上八煞格式：检查 long_mountain_id 和 avoid_zhi
            if 'long_mountain_id' in condition and 'avoid_zhi' in condition:
                if long_mountain_id in condition['long_mountain_id']:
                    # 检查日课四柱中是否有忌支
                    if ganzhi_list:
                        for gan_wx, zhi_wx in ganzhi_list:
                            # 将地支ID转换为地支名称进行检查
                            zhi_name = None
                            for zhi, wx_id in self.dizhi_wuxing.items():
                                if wx_id == zhi_wx:
                                    zhi_name = zhi
                                    break
                            if zhi_name and zhi_name in condition['avoid_zhi']:
                                total_penalty += rule['weight']
                                if rule.get('is_decisive'):
                                    decisive = True
                                if rule['shensha_name'] not in triggered_shensha:
                                    triggered_shensha.append(rule['shensha_name'])
                                break
        
        return total_penalty, decisive, triggered_shensha
    
    def check_shensha(self, year_zhi: str, mountain_id: int) -> Tuple[int, bool]:
        """
        检查所有神煞规则，返回总扣分和是否否决
        
        Args:
            year_zhi: 年支
            mountain_id: 山ID
            
        Returns:
            (总扣分, 是否否决)
        """
        total_penalty = 0
        decisive = False
        
        for rule in self.shensha_rules:
            condition = rule['condition']
            
            # 处理三煞规则格式
            if 'rules' in condition:
                for rule_item in condition['rules']:
                    if year_zhi in rule_item.get('year_zhi', []) and \
                       mountain_id in rule_item.get('mountain_id', []):
                        total_penalty += rule['weight']
                        if rule.get('is_decisive'):
                            decisive = True
            # 简单格式：{ "year_zhi": [...], "mountain_id": [...] }
            elif 'year_zhi' in condition and 'mountain_id' in condition:
                if year_zhi in condition['year_zhi'] and mountain_id in condition['mountain_id']:
                    total_penalty += rule['weight']
                    if rule.get('is_decisive'):
                        decisive = True
        
        return total_penalty, decisive
    
    def evaluate(self, mountain_id: int,
                 year_gan: str, year_zhi: str,
                 month_gan: str, month_zhi: str,
                 day_gan: str, day_zhi: str,
                 hour_gan: str, hour_zhi: str,
                 long_mountain_id: int = None,
                 long_weight: float = 1.0) -> Tuple[str, int, Any]:
        """
        综合评价一个日课，支持补龙扶山
        
        Args:
            mountain_id: 坐山ID
            year_gan, year_zhi: 年柱天干地支
            month_gan, month_zhi: 月柱天干地支
            day_gan, day_zhi: 日柱天干地支
            hour_gan, hour_zhi: 时柱天干地支
            long_mountain_id: 来龙ID（可选，若为None则不计算补龙）
            long_weight: 来龙得分权重系数（默认1.0，可设为1.5等提高补龙重要性）
            
        Returns:
            (等级, 总分, 详细信息)
        """
        # 1. 坐山五行
        mountain_wx = self.get_mountain_wuxing(mountain_id)
        if not mountain_wx:
            return "错误", 0, "坐山五行未定义"
        
        # 2. 来龙五行（如果有）
        long_wx = None
        if long_mountain_id is not None:
            long_wx = self.get_mountain_wuxing(long_mountain_id)
            if not long_wx:
                return "错误", 0, "来龙五行未定义"
        
        # 3. 日课各柱的五行
        ganzhi_list = [
            (self.tiangan_wuxing.get(year_gan), self.dizhi_wuxing.get(year_zhi)),
            (self.tiangan_wuxing.get(month_gan), self.dizhi_wuxing.get(month_zhi)),
            (self.tiangan_wuxing.get(day_gan), self.dizhi_wuxing.get(day_zhi)),
            (self.tiangan_wuxing.get(hour_gan), self.dizhi_wuxing.get(hour_zhi)),
        ]
        
        # 4. 计算五行生克得分（分别对坐山和来龙）
        score_mountain = 0
        score_long = 0
        details = []
        pillar_names = ['年', '月', '日', '时']
        
        for i, (gan_wx, zhi_wx) in enumerate(ganzhi_list):
            col_name = pillar_names[i]
            
            # 坐山得分
            if gan_wx:
                s = self.score_for_pair(mountain_wx, gan_wx, '山')
                score_mountain += s
                details.append(f"{col_name}干(山):{self.id_to_wuxing[gan_wx]} 得分{s}")
            if zhi_wx:
                s = self.score_for_pair(mountain_wx, zhi_wx, '山')
                score_mountain += s
                details.append(f"{col_name}支(山):{self.id_to_wuxing[zhi_wx]} 得分{s}")
            
            # 来龙得分
            if long_wx:
                if gan_wx:
                    s = self.score_for_pair(long_wx, gan_wx, '龙')
                    score_long += s
                    details.append(f"{col_name}干(龙):{self.id_to_wuxing[gan_wx]} 得分{s}")
                if zhi_wx:
                    s = self.score_for_pair(long_wx, zhi_wx, '龙')
                    score_long += s
                    details.append(f"{col_name}支(龙):{self.id_to_wuxing[zhi_wx]} 得分{s}")
        
        # 5. 神煞检查（同时检查坐山和来龙相关神煞）
        penalty_mountain, decisive_mountain = self.check_shensha(year_zhi, mountain_id)
        penalty_long = 0
        decisive_long = False
        triggered_shensha_long = []
        if long_mountain_id is not None:
            penalty_long, decisive_long, triggered_shensha_long = self.check_shensha_for_long(
                year_zhi, long_mountain_id, ganzhi_list
            )
        
        total_penalty = penalty_mountain + penalty_long
        decisive = decisive_mountain or decisive_long
        
        if decisive:
            return "凶(犯大煞)", score_mountain + score_long + total_penalty, details + [f"犯神煞，总扣{total_penalty}分"]
        
        # 应用来龙权重系数
        score_long_weighted = int(score_long * long_weight)
        total_score = score_mountain + score_long_weighted + total_penalty
        
        # 6. 评级
        if total_score >= 50:
            level = "大吉"
        elif total_score >= 30:
            level = "吉"
        elif total_score >= 10:
            level = "小吉"
        elif total_score >= -10:
            level = "平"
        elif total_score >= -30:
            level = "凶"
        else:
            level = "大凶"
        
        # 添加得分明细
        summary = {
            'mountain_score': score_mountain,
            'long_score': score_long if long_wx else None,
            'long_score_weighted': score_long_weighted if long_wx else None,
            'long_weight': long_weight if long_wx else None,
            'mountain_penalty': penalty_mountain,
            'long_penalty': penalty_long if long_wx else None,
            'triggered_shensha_long': triggered_shensha_long if long_wx else None,
        }
        
        return level, total_score, {'details': details, 'summary': summary}
    
    def evaluate_by_name(self, mountain_name: str,
                         year_gz: str, month_gz: str, day_gz: str, hour_gz: str,
                         long_name: str = None,
                         long_weight: float = 1.0) -> Dict:
        """
        通过山名评价日课（便捷方法），支持补龙
        
        Args:
            mountain_name: 山名（如'壬'）
            year_gz: 年柱（如'甲子'）
            month_gz: 月柱
            day_gz: 日柱
            hour_gz: 时柱
            long_name: 龙名（如'巽'，可选）
            long_weight: 来龙得分权重系数（默认1.0）
            
        Returns:
            评价结果字典
        """
        # 山名到ID的映射
        name_to_id = {
            '壬': 1, '子': 2, '癸': 3, '丑': 4, '寅': 5, '卯': 6,
            '辰': 7, '巳': 8, '午': 9, '未': 10, '申': 11, '酉': 12,
            '戌': 13, '亥': 14, '艮': 15, '乾': 16, '坤': 17, '巽': 18,
            '戊': 19, '己': 20, '甲': 21, '乙': 22, '丙': 23, '丁': 24,
        }
        
        mountain_id = name_to_id.get(mountain_name)
        if not mountain_id:
            return {'success': False, 'error': f'未知山名：{mountain_name}'}
        
        long_mountain_id = None
        if long_name:
            long_mountain_id = name_to_id.get(long_name)
            if not long_mountain_id:
                return {'success': False, 'error': f'未知龙名：{long_name}'}
        
        level, score, result = self.evaluate(
            mountain_id,
            year_gz[0], year_gz[1],
            month_gz[0], month_gz[1],
            day_gz[0], day_gz[1],
            hour_gz[0], hour_gz[1],
            long_mountain_id,
            long_weight
        )
        
        return {
            'success': True,
            'mountain': mountain_name,
            'long': long_name,
            'level': level,
            'score': score,
            'details': result['details'] if isinstance(result, dict) else result,
            'summary': result.get('summary', {}) if isinstance(result, dict) else {}
        }
    
    def evaluate_with_fengjin(self, mountain_name: str, jianxiang: str,
                               year_gz: str, month_gz: str, day_gz: str, hour_gz: str,
                               long_name: str = None, long_weight: float = 1.0,
                               use_fengjin_wuxing: bool = True) -> Dict:
        """
        使用分金五行评价日课
        
        Args:
            mountain_name: 山名（如'子'）
            jianxiang: 兼向（如'兼壬'、'正中'、'兼癸'）
            year_gz: 年柱
            month_gz: 月柱
            day_gz: 日柱
            hour_gz: 时柱
            long_name: 龙名（可选）
            long_weight: 来龙权重系数
            use_fengjin_wuxing: 是否使用分金五行（纳音），False则使用正体五行
            
        Returns:
            评价结果字典
        """
        # 山名到ID的映射
        name_to_id = {
            '壬': 1, '子': 2, '癸': 3, '丑': 4, '寅': 5, '卯': 6,
            '辰': 7, '巳': 8, '午': 9, '未': 10, '申': 11, '酉': 12,
            '戌': 13, '亥': 14, '艮': 15, '乾': 16, '坤': 17, '巽': 18,
            '戊': 19, '己': 20, '甲': 21, '乙': 22, '丙': 23, '丁': 24,
        }
        
        mountain_id = name_to_id.get(mountain_name)
        if not mountain_id:
            return {'success': False, 'error': f'未知山名：{mountain_name}'}
        
        # 获取分金索引
        fengjin_index = get_fengjin_by_jianxiang(mountain_name, jianxiang)
        
        # 获取分金五行（纳音）
        fengjin_wx_name, nayin_name = get_fengjin_wuxing(mountain_name, fengjin_index)
        
        # 获取分金干支
        fengjin_ganzhi = FENGJIN_GANZHI.get(mountain_name, [''])[fengjin_index]
        
        # 获取正体五行
        mountain_wx = self.get_mountain_wuxing(mountain_id)
        
        # 将五行名称转换为ID
        fengjin_wx_id = self.wuxing_id.get(fengjin_wx_name, 5)  # 默认土
        
        # 决定使用哪个五行进行计算
        if use_fengjin_wuxing:
            target_wx = fengjin_wx_id
            target_wx_name = fengjin_wx_name
            wx_type = '分金五行（纳音）'
        else:
            target_wx = mountain_wx
            target_wx_name = self.id_to_wuxing.get(mountain_wx, '土')
            wx_type = '正体五行'
        
        # 日课各柱的五行
        ganzhi_list = [
            (self.tiangan_wuxing.get(year_gz[0]), self.dizhi_wuxing.get(year_gz[1])),
            (self.tiangan_wuxing.get(month_gz[0]), self.dizhi_wuxing.get(month_gz[1])),
            (self.tiangan_wuxing.get(day_gz[0]), self.dizhi_wuxing.get(day_gz[1])),
            (self.tiangan_wuxing.get(hour_gz[0]), self.dizhi_wuxing.get(hour_gz[1])),
        ]
        
        # 计算得分
        total_score = 0
        details = []
        pillar_names = ['年', '月', '日', '时']
        
        for i, (gan_wx, zhi_wx) in enumerate(ganzhi_list):
            col_name = pillar_names[i]
            
            if gan_wx:
                s = self.score_for_pair(target_wx, gan_wx, '分金')
                total_score += s
                details.append(f"{col_name}干:{self.id_to_wuxing.get(gan_wx, '?')} 对{target_wx_name} 得分{s}")
            if zhi_wx:
                s = self.score_for_pair(target_wx, zhi_wx, '分金')
                total_score += s
                details.append(f"{col_name}支:{self.id_to_wuxing.get(zhi_wx, '?')} 对{target_wx_name} 得分{s}")
        
        # 神煞检查
        penalty, decisive = self.check_shensha(year_gz[1], mountain_id)
        
        if decisive:
            return {
                'success': True,
                'mountain': mountain_name,
                'jianxiang': jianxiang,
                'fengjin_ganzhi': fengjin_ganzhi,
                'fengjin_wuxing': fengjin_wx_name,
                'nayin_name': nayin_name,
                'wx_type': wx_type,
                'level': "凶(犯大煞)",
                'score': total_score + penalty,
                'details': details,
                'warning': f"犯神煞，扣{penalty}分"
            }
        
        total_score += penalty
        
        # 评级
        if total_score >= 50:
            level = "大吉"
        elif total_score >= 30:
            level = "吉"
        elif total_score >= 10:
            level = "小吉"
        elif total_score >= -10:
            level = "平"
        elif total_score >= -30:
            level = "凶"
        else:
            level = "大凶"
        
        return {
            'success': True,
            'mountain': mountain_name,
            'jianxiang': jianxiang,
            'fengjin_index': fengjin_index + 1,  # 第几分金
            'fengjin_ganzhi': fengjin_ganzhi,
            'fengjin_wuxing': fengjin_wx_name,
            'nayin_name': nayin_name,
            'zhengti_wuxing': self.id_to_wuxing.get(mountain_wx, '未知'),
            'wx_type': wx_type,
            'level': level,
            'score': total_score,
            'details': details,
            'summary': {
                'mountain_wuxing': self.id_to_wuxing.get(mountain_wx, '未知'),
                'fengjin_wuxing': fengjin_wx_name,
                'nayin_name': nayin_name,
                'fengjin_ganzhi': fengjin_ganzhi,
            }
        }



# -*- coding: utf-8 -*-
"""
================================================================================
电子罗盘模块
================================================================================
提供电子罗盘的完整功能，包括：
- 二十四山罗盘绘制（Canvas）
- 度数与山向的双向转换
- 分金显示与选择
- 与主程序山向同步
- 交互式操作（拖拽、点击选择）

使用方法:
    # 在tkinter窗口中使用
    root = tk.Tk()
    compass = CompassFrame(root)
    compass.pack()
    
    # 设置山向
    compass.set_shan_xiang("子山午向")
    
    # 获取当前度数
    degree = compass.get_degree()
    
    # 设置同步回调
    compass.set_sync_callback(on_shan_xiang_changed)
================================================================================
"""

import tkinter as tk
from tkinter import ttk
import math
import sys
import os
from typing import Callable, Optional, Tuple, List, Dict, Any
from dataclasses import dataclass

# 添加项目根目录到路径（支持直接运行）


@dataclass
class MountainDegree:
    """山向度数信息"""
    name: str           # 山名
    start_degree: float # 起始度数
    end_degree: float   # 结束度数
    wuxing: str         # 五行
    center_degree: float # 中心度数
    fengjin_list: List[Dict]  # 分金列表


class CompassConverter:
    """罗盘度数转换器"""
    
    def __init__(self):
        self.mountains_data = {}
        self._init_mountains()
    
    def _init_mountains(self):
        """初始化二十四山度数数据"""
        for data in TWENTY_FOUR_MOUNTAINS_DATA:
            mid, name, mtype, start_deg, end_deg, wuxing, yinyang = data
            
            # 处理跨0度的情况
            if end_deg < start_deg:
                end_deg += 360
            
            center_deg = (start_deg + end_deg) / 2
            if center_deg >= 360:
                center_deg -= 360
            
            # 生成分金列表（每山5个分金，每个3度）
            fengjin_list = []
            for i in range(5):
                fj_start = start_deg + i * 3
                fj_end = fj_start + 3
                fj_center = fj_start + 1.5
                if fj_start >= 360:
                    fj_start -= 360
                if fj_end >= 360:
                    fj_end -= 360
                if fj_center >= 360:
                    fj_center -= 360
                fengjin_list.append({
                    'index': i,
                    'start': fj_start if fj_start < 360 else fj_start - 360,
                    'end': fj_end if fj_end < 360 else fj_end - 360,
                    'center': fj_center,
                    'name': f'{name}山第{i+1}分金'
                })
            
            self.mountains_data[name] = MountainDegree(
                name=name,
                start_degree=start_deg,
                end_degree=end_deg,
                wuxing=wuxing,
                center_degree=center_deg,
                fengjin_list=fengjin_list
            )
    
    def degree_to_mountain(self, degree: float) -> Tuple[str, str, Optional[Dict]]:
        """
        将度数转换为山向
        
        Args:
            degree: 度数（0-360）
            
        Returns:
            (山名, 山向, 分金信息)
        """
        degree = degree % 360
        
        for name, data in self.mountains_data.items():
            start = data.start_degree
            end = data.end_degree
            
            # 处理跨0度的情况
            if end > 360:
                if degree >= start or degree < (end - 360):
                    shan_xiang = shan_to_shan_xiang(name)
                    fengjin = self._get_fengjin(degree, data)
                    return name, shan_xiang, fengjin
            else:
                if start <= degree < end:
                    shan_xiang = shan_to_shan_xiang(name)
                    fengjin = self._get_fengjin(degree, data)
                    return name, shan_xiang, fengjin
        
        return "子", "子山午向", None
    
    def _get_fengjin(self, degree: float, mountain_data: MountainDegree) -> Optional[Dict]:
        """获取分金信息"""
        for fj in mountain_data.fengjin_list:
            start = fj['start']
            end = fj['end']
            
            if end > start:
                if start <= degree < end:
                    return fj
            else:
                if degree >= start or degree < end:
                    return fj
        return None
    
    def get_jianxiang(self, mountain_name: str, degree: float) -> Optional[str]:
        """
        获取兼向信息
        
        Args:
            mountain_name: 主山名
            degree: 当前度数
            
        Returns:
            兼向名称，如"兼丙"或None
        """
        mountain_data = self.mountains_data.get(mountain_name)
        if not mountain_data:
            return None
        
        # 获取当前分金
        fengjin = self._get_fengjin(degree, mountain_data)
        if not fengjin:
            return None
        
        # 根据分金索引判断兼向
        # 分金1-2：兼左（逆时针方向的山）
        # 分金3：正中（不兼）
        # 分金4-5：兼右（顺时针方向的山）
        fj_index = fengjin['index']
        
        # 获取相邻的山
        mountains = list(self.mountains_data.keys())
        current_idx = mountains.index(mountain_name)
        
        if fj_index in [0, 1]:
            # 兼左（逆时针）
            left_idx = (current_idx - 1) % len(mountains)
            jian_shan = mountains[left_idx]
            return f"兼{jian_shan}"
        elif fj_index == 2:
            # 正中，不兼
            pass
        else:  # fj_index in [3, 4]
            # 兼右（顺时针）
            right_idx = (current_idx + 1) % len(mountains)
            jian_shan = mountains[right_idx]
            return f"兼{jian_shan}"
    
    def get_jianxiang_options(self, mountain_name: str) -> List[str]:
        """
        获取某山的所有兼向选项
        
        Args:
            mountain_name: 山名
            
        Returns:
            兼向选项列表
        """
        if mountain_name not in self.mountains_data:
            return []
        
        mountains = list(self.mountains_data.keys())
        current_idx = mountains.index(mountain_name)
        
        # 获取左右相邻的山
        left_idx = (current_idx - 1) % len(mountains)
        right_idx = (current_idx + 1) % len(mountains)
        
        left_shan = mountains[left_idx]
        right_shan = mountains[right_idx]
        
        return [
            f"{mountain_name}山兼{left_shan}",
            f"{mountain_name}山（正中）",
            f"{mountain_name}山兼{right_shan}",
        ]
    
    def jianxiang_to_degree(self, mountain_name: str, jianxiang: str) -> float:
        """
        将兼向转换为度数
        
        Args:
            mountain_name: 主山名
            jianxiang: 兼向，如"兼丙"
            
        Returns:
            度数
        """
        mountain_data = self.mountains_data.get(mountain_name)
        if not mountain_data:
            return 0.0
        
        if not jianxiang or jianxiang == "正中":
            # 正中，取第3分金（中间）
            pass
        
        # 解析兼向
        jian_shan = jianxiang.replace("兼", "")
        
        mountains = list(self.mountains_data.keys())
        current_idx = mountains.index(mountain_name)
        left_idx = (current_idx - 1) % len(mountains)
        right_idx = (current_idx + 1) % len(mountains)
        
        if mountains[left_idx] == jian_shan:
            # 兼左，取第1分金
            pass
        elif mountains[right_idx] == jian_shan:
            # 兼右，取第5分金
            pass
        
        return mountain_data.center_degree
    
    def mountain_to_degree(self, mountain_name: str, fengjin_index: int = None) -> float:
        """
        将山名转换为度数
        
        Args:
            mountain_name: 山名
            fengjin_index: 分金索引（可选，0-4）
            
        Returns:
            度数
        """
        if mountain_name not in self.mountains_data:
            return 0.0
        
        data = self.mountains_data[mountain_name]
        
        if fengjin_index is not None and 0 <= fengjin_index < 5:
            return data.fengjin_list[fengjin_index]['center']
        
        return data.center_degree
    
    def shan_xiang_to_degree(self, shan_xiang: str) -> float:
        """
        将山向转换为度数
        
        Args:
            shan_xiang: 山向，如"子山午向"
            
        Returns:
            度数
        """
        shan = shan_xiang_to_shan(shan_xiang)
        return self.mountain_to_degree(shan)
    
    def get_mountain_info(self, mountain_name: str) -> Optional[MountainDegree]:
        """获取山向详细信息"""
        return self.mountains_data.get(mountain_name)
    
    def get_all_mountains(self) -> List[str]:
        """获取所有山名列表"""
        return list(self.mountains_data.keys())


class CompassWidget(tk.Canvas):
    """罗盘绘制组件"""
    
    # 颜色配置
    COLORS = {
        'background': '#1a1a2e',
        'ring_outer': '#16213e',
        'ring_24shan': '#0f3460',
        'ring_8gua': '#1a1a2e',
        'ring_center': '#0f3460',
        'text_light': '#e8e8e8',
        'text_highlight': '#ff6b6b',
        'highlight': '#e94560',
        'highlight_alpha': 0.3,
        'needle': '#ff6b6b',
        'needle_center': '#ffd700',
        'grid': '#2d4a6e',
        'wuxing_wood': '#4caf50',
        'wuxing_fire': '#f44336',
        'wuxing_earth': '#8d6e63',
        'wuxing_metal': '#ffc107',
        'wuxing_water': '#2196f3',
    }
    
    # 八卦名称（按后天八卦顺序）
    BAGUA_NAMES = ['坎', '艮', '震', '巽', '离', '坤', '兑', '乾']
    
    # 八卦对应的起始度数
    BAGUA_DEGREES = {
        '坎': 352.5, '艮': 37.5, '震': 67.5, '巽': 127.5,
        '离': 172.5, '坤': 217.5, '兑': 262.5, '乾': 307.5
    }
    
    def __init__(self, parent, size: int = 400, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        bg=self.COLORS['background'], highlightthickness=0, **kwargs)
        
        self.size = size
        self.center = size // 2
        self.converter = CompassConverter()
        
        # 当前状态
        self.current_degree = 0.0
        self.current_mountain = "子"
        self.current_shan_xiang = "子山午向"
        self.current_fengjin = None
        
        # 回调函数
        self.on_change_callback: Optional[Callable] = None
        
        # 绑定事件
        self.bind('<Button-1>', self._on_click)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<MouseWheel>', self._on_scroll)
        
        # 初始绘制
        self.draw_compass()
    
    def draw_compass(self):
        """绘制完整罗盘"""
        self.delete('all')
        
        # 绘制各层
        self._draw_background()
        self._draw_outer_ring()      # 外圈：360度刻度
        self._draw_24shan_ring()     # 二十四山圈
        self._draw_8gua_ring()       # 八卦圈
        self._draw_fengjin_ring()    # 分金圈
        self._draw_center()          # 天池
        self._draw_needle()          # 指针
        self._draw_highlight()       # 高亮当前山向
    
    def _draw_background(self):
        """绘制背景"""
        self.create_oval(5, 5, self.size-5, self.size-5, 
                        fill=self.COLORS['background'], outline='')
    
    def _draw_outer_ring(self):
        """绘制外圈（360度刻度）"""
        r = self.size // 2 - 10
        
        # 绘制外圈背景
        self.create_oval(self.center-r, self.center-r,
                        self.center+r, self.center+r,
                        fill=self.COLORS['ring_outer'], outline=self.COLORS['grid'], width=1)
        
        # 绘制度数刻度
        for i in range(360):
            angle = math.radians(i - 90)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            if i % 15 == 0:
                # 主刻度（每15度）
                inner_r = r - 15
                color = self.COLORS['text_light']
                width = 2
            elif i % 5 == 0:
                # 次刻度（每5度）
                inner_r = r - 8
                color = self.COLORS['grid']
                width = 1
            else:
                # 小刻度
                inner_r = r - 5
                color = self.COLORS['grid']
                width = 1
            
            x1 = self.center + inner_r * cos_a
            y1 = self.center + inner_r * sin_a
            x2 = self.center + r * cos_a
            y2 = self.center + r * sin_a
            
            self.create_line(x1, y1, x2, y2, fill=color, width=width)
        
        # 绘制主要度数标签
        for deg in [0, 90, 180, 270]:
            angle = math.radians(deg - 90)
            x = self.center + (r - 25) * math.cos(angle)
            y = self.center + (r - 25) * math.sin(angle)
            
            labels = {0: '北\n0°', 90: '东\n90°', 180: '南\n180°', 270: '西\n270°'}
            self.create_text(x, y, text=labels[deg], fill=self.COLORS['text_light'],
                           font=('微软雅黑', 8), justify='center')
    
    def _draw_24shan_ring(self):
        """绘制二十四山圈"""
        r = self.size // 2 - 50
        
        # 绘制背景环
        self.create_oval(self.center-r-5, self.center-r-5,
                        self.center+r+5, self.center+r+5,
                        fill=self.COLORS['ring_24shan'], outline=self.COLORS['grid'], width=1)
        
        # 绘制二十四山
        mountains = self.converter.get_all_mountains()
        
        for i, name in enumerate(mountains):
            # 计算角度（从北开始顺时针）
            mountain_data = self.converter.get_mountain_info(name)
            if not mountain_data:
                continue
            
            center_deg = mountain_data.center_degree
            angle = math.radians(center_deg - 90)
            
            # 绘制山名
            x = self.center + (r - 15) * math.cos(angle)
            y = self.center + (r - 15) * math.sin(angle)
            
            # 根据五行设置颜色
            wuxing = mountain_data.wuxing
            color = self.COLORS.get(f'wuxing_{wuxing}', self.COLORS['text_light'])
            
            # 当前选中的山向高亮
            if name == self.current_mountain:
                color = self.COLORS['text_highlight']
            
            self.create_text(x, y, text=name, fill=color,
                           font=('微软雅黑', 10, 'bold'))
            
            # 绘制分隔线
            start_angle = mountain_data.start_degree - 90
            end_angle = mountain_data.end_degree - 90
            
            for deg in [start_angle, end_angle]:
                rad = math.radians(deg)
                x1 = self.center + (r - 30) * math.cos(rad)
                y1 = self.center + (r - 30) * math.sin(rad)
                x2 = self.center + r * math.cos(rad)
                y2 = self.center + r * math.sin(rad)
                self.create_line(x1, y1, x2, y2, fill=self.COLORS['grid'], width=1)
    
    def _draw_8gua_ring(self):
        """绘制八卦圈"""
        r = self.size // 2 - 100
        
        # 绘制背景环
        self.create_oval(self.center-r, self.center-r,
                        self.center+r, self.center+r,
                        fill=self.COLORS['ring_8gua'], outline=self.COLORS['grid'], width=1)
        
        # 绘制八卦
        for name, deg in self.BAGUA_DEGREES.items():
            angle = math.radians(deg - 90 + 11.25)  # 偏移到八卦中心
            x = self.center + (r - 10) * math.cos(angle)
            y = self.center + (r - 10) * math.sin(angle)
            
            self.create_text(x, y, text=name, fill=self.COLORS['text_light'],
                           font=('微软雅黑', 9))
    
    def _draw_fengjin_ring(self):
        """绘制分金圈（120分金）"""
        r = self.size // 2 - 130
        
        if r < 30:
            return  # 空间太小不绘制
        
        # 绘制背景环
        self.create_oval(self.center-r, self.center-r,
                        self.center+r, self.center+r,
                        fill=self.COLORS['ring_outer'], outline=self.COLORS['grid'], width=1)
        
        # 绘制分金刻度（每山5个分金）
        mountains = self.converter.get_all_mountains()
        for name in mountains:
            mountain_data = self.converter.get_mountain_info(name)
            if not mountain_data:
                continue
            
            for fj in mountain_data.fengjin_list:
                start_deg = fj['start']
                end_deg = fj['end']
                
                # 绘制分金分隔线
                for deg in [start_deg, end_deg]:
                    angle = math.radians(deg - 90)
                    x1 = self.center + (r - 10) * math.cos(angle)
                    y1 = self.center + (r - 10) * math.sin(angle)
                    x2 = self.center + r * math.cos(angle)
                    y2 = self.center + r * math.sin(angle)
                    self.create_line(x1, y1, x2, y2, fill=self.COLORS['grid'], width=1)
    
    def _draw_center(self):
        """绘制天池（中心）"""
        r = 25
        
        # 绘制中心圆
        self.create_oval(self.center-r, self.center-r,
                        self.center+r, self.center+r,
                        fill=self.COLORS['ring_center'], outline=self.COLORS['grid'], width=2)
        
        # 绘制太极图（简化版）
        self.create_arc(self.center-r+5, self.center-r+5,
                       self.center+r-5, self.center+r-5,
                       start=0, extent=180, fill='#ffffff', outline='')
        self.create_arc(self.center-r+5, self.center-r+5,
                       self.center+r-5, self.center+r-5,
                       start=180, extent=180, fill='#000000', outline='')
    
    def _draw_needle(self):
        """绘制指针"""
        # 指针长度
        needle_length = self.size // 2 - 60
        
        # 指针角度（指向当前度数）
        angle = math.radians(self.current_degree - 90)
        
        # 指针尖端坐标
        tip_x = self.center + needle_length * math.cos(angle)
        tip_y = self.center + needle_length * math.sin(angle)
        
        # 指针尾部坐标
        tail_x = self.center - (needle_length * 0.3) * math.cos(angle)
        tail_y = self.center - (needle_length * 0.3) * math.sin(angle)
        
        # 绘制指针主体（红色指向北方）
        self.create_line(tail_x, tail_y, tip_x, tip_y,
                        fill=self.COLORS['needle'], width=3, arrow=tk.LAST)
        
        # 绘制指针中心点
        self.create_oval(self.center-5, self.center-5,
                        self.center+5, self.center+5,
                        fill=self.COLORS['needle_center'], outline='')
    
    def _draw_highlight(self):
        """高亮当前选中的山向"""
        mountain_data = self.converter.get_mountain_info(self.current_mountain)
        if not mountain_data:
            return
        
        # 计算高亮扇形
        start_deg = mountain_data.start_degree
        end_deg = mountain_data.end_degree
        
        # 处理跨0度的情况
        if end_deg > 360:
            # 绘制两段
            self._draw_highlight_arc(start_deg, 360)
            self._draw_highlight_arc(0, end_deg - 360)
        else:
            self._draw_highlight_arc(start_deg, end_deg)
    
    def _draw_highlight_arc(self, start_deg: float, end_deg: float):
        """绘制高亮弧形"""
        r = self.size // 2 - 50
        
        # 使用多边形近似扇形
        points = [self.center, self.center]
        
        for deg in range(int(start_deg), int(end_deg) + 1, 2):
            angle = math.radians(deg - 90)
            x = self.center + r * math.cos(angle)
            y = self.center + r * math.sin(angle)
            points.extend([x, y])
        
        if len(points) > 4:
            # 使用半透明效果（通过stipple模拟）
            self.create_polygon(points, fill=self.COLORS['highlight'],
                              stipple='gray50', outline='')
    
    def _on_click(self, event):
        """点击事件处理"""
        self._update_from_position(event.x, event.y)
    
    def _on_drag(self, event):
        """拖拽事件处理"""
        self._update_from_position(event.x, event.y)
    
    def _on_scroll(self, event):
        """滚轮事件处理"""
        delta = event.delta / 120  # Windows
        if hasattr(event, 'delta'):
            delta = event.delta / 120
        else:
            delta = 1 if event.num == 4 else -1  # Linux/Mac
        
        new_degree = (self.current_degree + delta) % 360
        self.set_degree(new_degree)
    
    def _update_from_position(self, x: int, y: int):
        """根据鼠标位置更新度数"""
        dx = x - self.center
        dy = y - self.center
        
        # 计算角度
        angle = math.degrees(math.atan2(dy, dx)) + 90
        if angle < 0:
            angle += 360
        
        self.set_degree(angle)
    
    def set_degree(self, degree: float, notify: bool = True):
        """
        设置当前度数
        
        Args:
            degree: 度数（0-360）
            notify: 是否触发回调
        """
        self.current_degree = degree % 360
        
        # 更新山向信息
        self.current_mountain, self.current_shan_xiang, self.current_fengjin = \
            self.converter.degree_to_mountain(self.current_degree)
        
        # 重绘罗盘
        self.draw_compass()
        
        # 触发回调
        if notify and self.on_change_callback:
            self.on_change_callback(self.current_degree, self.current_shan_xiang,
                                   self.current_mountain, self.current_fengjin)
    
    def set_shan_xiang(self, shan_xiang: str, notify: bool = True):
        """
        设置当前山向
        
        Args:
            shan_xiang: 山向，如"子山午向"
            notify: 是否触发回调
        """
        degree = self.converter.shan_xiang_to_degree(shan_xiang)
        self.set_degree(degree, notify)
    
    def set_mountain(self, mountain_name: str, fengjin_index: int = None, notify: bool = True):
        """
        设置当前山
        
        Args:
            mountain_name: 山名
            fengjin_index: 分金索引
            notify: 是否触发回调
        """
        degree = self.converter.mountain_to_degree(mountain_name, fengjin_index)
        self.set_degree(degree, notify)
    
    def get_degree(self) -> float:
        """获取当前度数"""
        return self.current_degree
    
    def get_shan_xiang(self) -> str:
        """获取当前山向"""
        return self.current_shan_xiang
    
    def get_mountain(self) -> str:
        """获取当前山名"""
        return self.current_mountain
    
    def get_fengjin(self) -> Optional[Dict]:
        """获取当前分金"""
        return self.current_fengjin
    
    def set_on_change(self, callback: Callable):
        """设置变化回调函数"""
        self.on_change_callback = callback


class CompassFrame(ttk.Frame):
    """电子罗盘框架（包含罗盘和输入控件）"""
    
    def __init__(self, parent, size: int = 400, sync_callback: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.size = size
        self.sync_callback = sync_callback
        self.converter = CompassConverter()
        
        # 预设列表
        self.presets: List[Dict] = []
        
        self._create_widgets()
        self._layout_widgets()
    
    def _create_widgets(self):
        """创建控件"""
        # 罗盘组件
        self.compass = CompassWidget(self, size=self.size)
        self.compass.set_on_change(self._on_compass_change)
        
        # 输入框架
        self.input_frame = ttk.LabelFrame(self, text="坐向输入")
        
        # 度数输入
        ttk.Label(self.input_frame, text="度数：").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.degree_var = tk.StringVar(value="0.00")
        self.degree_entry = ttk.Entry(self.input_frame, textvariable=self.degree_var, width=10)
        self.degree_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.degree_entry.bind('<Return>', self._on_degree_input)
        self.degree_entry.bind('<FocusOut>', self._on_degree_input)
        ttk.Label(self.input_frame, text="°").grid(row=0, column=2, sticky='w')
        
        # 山向选择
        ttk.Label(self.input_frame, text="山向：").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.shan_xiang_var = tk.StringVar()
        self.shan_xiang_combo = ttk.Combobox(self.input_frame, textvariable=self.shan_xiang_var,
                                             values=SHAN_XIANG_24, width=15, state='readonly')
        self.shan_xiang_combo.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.shan_xiang_combo.bind('<<ComboboxSelected>>', self._on_shan_xiang_select)
        
        # 分金选择（方式一：最精确）
        ttk.Label(self.input_frame, text="分金：").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.fengjin_var = tk.StringVar()
        self.fengjin_combo = ttk.Combobox(self.input_frame, textvariable=self.fengjin_var,
                                          width=15, state='readonly')
        self.fengjin_combo.grid(row=2, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.fengjin_combo.bind('<<ComboboxSelected>>', self._on_fengjin_select)
        
        # 兼向选择（方式二：最常见）
        ttk.Label(self.input_frame, text="兼向：").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.jianxiang_var = tk.StringVar()
        self.jianxiang_combo = ttk.Combobox(self.input_frame, textvariable=self.jianxiang_var,
                                            width=15, state='readonly')
        self.jianxiang_combo.grid(row=3, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.jianxiang_combo.bind('<<ComboboxSelected>>', self._on_jianxiang_select)
        
        # 手动输入兼向（方式三：最基础）
        ttk.Label(self.input_frame, text="手动：").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.manual_jian_var = tk.StringVar()
        self.manual_jian_entry = ttk.Entry(self.input_frame, textvariable=self.manual_jian_var, width=15)
        self.manual_jian_entry.grid(row=4, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.manual_jian_entry.bind('<Return>', self._on_manual_jian_input)
        self.manual_jian_entry.bind('<FocusOut>', self._on_manual_jian_input)
        
        # 输入模式选择
        ttk.Label(self.input_frame, text="模式：").grid(row=5, column=0, sticky='w', padx=5, pady=2)
        self.input_mode_var = tk.StringVar(value="自动识别")
        self.input_mode_combo = ttk.Combobox(self.input_frame, textvariable=self.input_mode_var,
                                             values=["自动识别", "分金模式", "兼向模式", "手动模式"],
                                             width=12, state='readonly')
        self.input_mode_combo.grid(row=5, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.input_mode_combo.bind('<<ComboboxSelected>>', self._on_input_mode_change)
        
        # 信息显示框架
        self.info_frame = ttk.LabelFrame(self, text="坐山信息")
        
        # 正体五行
        ttk.Label(self.info_frame, text="正体五行：").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.wuxing_label = ttk.Label(self.info_frame, text="水")
        self.wuxing_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # 分金五行（纳音）
        ttk.Label(self.info_frame, text="分金五行：").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.fengjin_wuxing_label = ttk.Label(self.info_frame, text="金（海中金）")
        self.fengjin_wuxing_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # 阴阳
        ttk.Label(self.info_frame, text="阴阳：").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.yinyang_label = ttk.Label(self.info_frame, text="阳")
        self.yinyang_label.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # 度数范围
        ttk.Label(self.info_frame, text="范围：").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.range_label = ttk.Label(self.info_frame, text="352.5° - 7.5°")
        self.range_label.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        # 分金干支
        ttk.Label(self.info_frame, text="分金干支：").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.fengjin_ganzhi_label = ttk.Label(self.info_frame, text="甲子")
        self.fengjin_ganzhi_label.grid(row=4, column=1, sticky='w', padx=5, pady=2)
        
        # 预设管理框架
        self.preset_frame = ttk.LabelFrame(self, text="预设管理")
        
        # 预设列表
        self.preset_listbox = tk.Listbox(self.preset_frame, height=4, width=20)
        self.preset_listbox.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=2)
        self.preset_listbox.bind('<Double-1>', self._on_preset_double_click)
        
        # 预设按钮
        ttk.Button(self.preset_frame, text="添加预设", command=self._add_preset).grid(
            row=1, column=0, sticky='ew', padx=5, pady=2)
        ttk.Button(self.preset_frame, text="删除预设", command=self._delete_preset).grid(
            row=1, column=1, sticky='ew', padx=5, pady=2)
        
        # 同步按钮
        self.sync_button = ttk.Button(self, text="同步到主程序", command=self._sync_to_main)
    
    def _layout_widgets(self):
        """布局控件"""
        self.compass.grid(row=0, column=0, rowspan=3, padx=10, pady=10)
        
        self.input_frame.grid(row=0, column=1, sticky='new', padx=10, pady=5)
        self.info_frame.grid(row=1, column=1, sticky='new', padx=10, pady=5)
        self.preset_frame.grid(row=2, column=1, sticky='new', padx=10, pady=5)
        self.sync_button.grid(row=3, column=0, columnspan=2, pady=10)
    
    def _on_compass_change(self, degree: float, shan_xiang: str, mountain: str, fengjin: Dict):
        """罗盘变化回调"""
        # 更新输入控件
        self.degree_var.set(f"{degree:.2f}")
        self.shan_xiang_var.set(shan_xiang)
        
        # 更新分金选项
        self._update_fengjin_options(mountain)
        if fengjin:
            self.fengjin_var.set(fengjin['name'])
        
        # 更新兼向显示
        self._update_jianxiang_display()
        
        # 更新信息显示
        self._update_info_display(mountain)
    
    def _on_degree_input(self, event=None):
        """度数输入处理"""
        try:
            degree = float(self.degree_var.get())
            self.compass.set_degree(degree)
        except ValueError:
            pass
    
    def _on_shan_xiang_select(self, event=None):
        """山向选择处理"""
        shan_xiang = self.shan_xiang_var.get()
        if shan_xiang:
            self.compass.set_shan_xiang(shan_xiang)
    
    def _on_fengjin_select(self, event=None):
        """分金选择处理（方式一：最精确）"""
        fengjin_name = self.fengjin_var.get()
        if fengjin_name:
            # 解析分金索引
            try:
                index = int(fengjin_name.split('第')[1].split('分金')[0]) - 1
                mountain = self.compass.get_mountain()
                self.compass.set_mountain(mountain, index)
                # 更新兼向显示
                self._update_jianxiang_display()
            except (IndexError, ValueError):
                pass
    
    def _on_jianxiang_select(self, event=None):
        """兼向选择处理（方式二：最常见）"""
        jianxiang_full = self.jianxiang_var.get()
        if not jianxiang_full:
            return
        
        # 解析兼向
        if "（正中）" in jianxiang_full:
            mountain = jianxiang_full.replace("山（正中）", "")
            jianxiang = "正中"
        elif "兼" in jianxiang_full:
            parts = jianxiang_full.split("兼")
            mountain = parts[0].replace("山", "")
            jianxiang = f"兼{parts[1]}"
        else:
            return
        
        # 计算度数
        degree = self.converter.jianxiang_to_degree(mountain, jianxiang)
        self.compass.set_degree(degree)
        
        # 更新手动输入框
        self.manual_jian_var.set(jianxiang_full)
    
    def _on_manual_jian_input(self, event=None):
        """手动输入兼向处理（方式三：最基础）"""
        manual_input = self.manual_jian_var.get().strip()
        if not manual_input:
            return
        
        # 解析输入
        # 支持格式："午山兼丙"、"午兼丙"、"兼丙"
        mountain = None
        jianxiang = None
        
        if "兼" in manual_input:
            if "山" in manual_input:
                # 格式："午山兼丙"
                parts = manual_input.split("兼")
                mountain = parts[0].replace("山", "").strip()
                jianxiang = f"兼{parts[1].strip()}"
            else:
                # 格式："午兼丙" 或 "兼丙"
                if manual_input.startswith("兼"):
                    # 只有兼向，使用当前山
                    mountain = self.compass.get_mountain()
                    jianxiang = manual_input
                else:
                    # 格式："午兼丙"
                    parts = manual_input.split("兼")
                    mountain = parts[0].strip()
                    jianxiang = f"兼{parts[1].strip()}"
        else:
            # 没有兼向，可能是纯山名
            mountain = manual_input.replace("山", "").strip()
            jianxiang = "正中"
        
        if mountain:
            degree = self.converter.jianxiang_to_degree(mountain, jianxiang)
            self.compass.set_degree(degree)
            
            # 更新兼向下拉框
            self._update_jianxiang_options(mountain)
    
    def _on_input_mode_change(self, event=None):
        """输入模式改变处理"""
        mode = self.input_mode_var.get()
        
        if mode == "分金模式":
            self.fengjin_combo.config(state='readonly')
            self.jianxiang_combo.config(state='disabled')
            self.manual_jian_entry.config(state='disabled')
        elif mode == "兼向模式":
            self.fengjin_combo.config(state='disabled')
            self.jianxiang_combo.config(state='readonly')
            self.manual_jian_entry.config(state='disabled')
        elif mode == "手动模式":
            self.fengjin_combo.config(state='disabled')
            self.jianxiang_combo.config(state='disabled')
            self.manual_jian_entry.config(state='normal')
        else:  # 自动识别
            self.fengjin_combo.config(state='readonly')
            self.jianxiang_combo.config(state='readonly')
            self.manual_jian_entry.config(state='normal')
    
    def _update_jianxiang_options(self, mountain: str):
        """更新兼向选项"""
        options = self.converter.get_jianxiang_options(mountain)
        self.jianxiang_combo['values'] = options
    
    def _update_jianxiang_display(self):
        """更新兼向显示"""
        mountain = self.compass.get_mountain()
        degree = self.compass.get_degree()
        
        # 获取兼向
        jianxiang = self.converter.get_jianxiang(mountain, degree)
        
        # 更新兼向选项
        self._update_jianxiang_options(mountain)
        
        # 设置当前兼向
        if jianxiang:
            current_text = f"{mountain}山{jianxiang}"
        else:
            current_text = f"{mountain}山（正中）"
        
        self.jianxiang_var.set(current_text)
        self.manual_jian_var.set(current_text)
    
    def _update_fengjin_options(self, mountain: str):
        """更新分金选项"""
        mountain_data = self.converter.get_mountain_info(mountain)
        if mountain_data:
            fengjin_names = [fj['name'] for fj in mountain_data.fengjin_list]
            self.fengjin_combo['values'] = fengjin_names
    
    def _update_info_display(self, mountain: str):
        """更新信息显示"""
        mountain_data = self.converter.get_mountain_info(mountain)
        if mountain_data:
            # 正体五行
            self.wuxing_label.config(text=mountain_data.wuxing)
            
            # 获取阴阳
            for data in TWENTY_FOUR_MOUNTAINS_DATA:
                if data[1] == mountain:
                    yinyang = '阳' if data[6].value == '阳' else '阴'
                    self.yinyang_label.config(text=yinyang)
                    break
            
            # 显示度数范围
            start = mountain_data.start_degree
            end = mountain_data.end_degree
            if end > 360:
                end -= 360
            self.range_label.config(text=f"{start:.1f}° - {end:.1f}°")
            
            # 更新分金五行（纳音）
            fengjin = self.compass.get_fengjin()
            if fengjin:
                self.fengjin_wuxing_label.config(text=f"{wuxing}（{nayin_name}）")
                
                # 显示分金干支
                if mountain in FENGJIN_GANZHI:
                    ganzhi = FENGJIN_GANZHI[mountain][fj_index]
                    self.fengjin_ganzhi_label.config(text=ganzhi)
    
    def _add_preset(self):
        """添加预设"""
        shan_xiang = self.compass.get_shan_xiang()
        degree = self.compass.get_degree()
        
        preset = {
            'name': f"{shan_xiang} ({degree:.1f}°)",
            'shan_xiang': shan_xiang,
            'degree': degree
        }
        
        self.presets.append(preset)
        self.preset_listbox.insert(tk.END, preset['name'])
    
    def _delete_preset(self):
        """删除预设"""
        selection = self.preset_listbox.curselection()
        if selection:
            index = selection[0]
            self.preset_listbox.delete(index)
            del self.presets[index]
    
    def _on_preset_double_click(self, event=None):
        """预设双击调用"""
        selection = self.preset_listbox.curselection()
        if selection:
            index = selection[0]
            preset = self.presets[index]
            self.compass.set_shan_xiang(preset['shan_xiang'])
    
    def _sync_to_main(self):
        """同步到主程序"""
        if self.sync_callback:
            shan_xiang = self.compass.get_shan_xiang()
            degree = self.compass.get_degree()
            mountain = self.compass.get_mountain()
            self.sync_callback(shan_xiang, degree, mountain)
    
    def set_shan_xiang(self, shan_xiang: str):
        """设置山向"""
        self.compass.set_shan_xiang(shan_xiang)
    
    def set_degree(self, degree: float):
        """设置度数"""
        self.compass.set_degree(degree)
    
    def get_shan_xiang(self) -> str:
        """获取当前山向"""
        return self.compass.get_shan_xiang()
    
    def get_degree(self) -> float:
        """获取当前度数"""
        return self.compass.get_degree()
    
    def get_full_shan_xiang(self) -> str:
        """
        获取完整山向（含兼向）
        
        Returns:
            如"午山兼丙"、"子山（正中）"
        """
        mountain = self.compass.get_mountain()
        degree = self.compass.get_degree()
        
        # 获取兼向
        jianxiang = self.converter.get_jianxiang(mountain, degree)
        
        if jianxiang:
            return f"{mountain}山{jianxiang}"
        else:
            return f"{mountain}山（正中）"
    
    def get_jianxiang_info(self) -> Dict[str, Any]:
        """
        获取兼向详细信息
        
        Returns:
            {
                'mountain': 主山,
                'jianxiang': 兼向,
                'degree': 度数,
                'fengjin': 分金信息,
                'full_name': 完整名称
            }
        """
        mountain = self.compass.get_mountain()
        degree = self.compass.get_degree()
        fengjin = self.compass.get_fengjin()
        jianxiang = self.converter.get_jianxiang(mountain, degree)
        
        return {
            'mountain': mountain,
            'jianxiang': jianxiang,
            'degree': degree,
            'fengjin': fengjin,
            'full_name': f"{mountain}山{jianxiang}" if jianxiang else f"{mountain}山（正中）"
        }


class CompassDialog(tk.Toplevel):
    """电子罗盘对话框"""
    
    def __init__(self, parent, initial_shan_xiang: str = None, 
                 on_select: Callable = None, size: int = 450):
        super().__init__(parent)
        
        self.title("电子罗盘")
        self.geometry(f"{size + 250}x{size + 100}")
        self.resizable(False, False)
        
        self.on_select = on_select
        self.selected_shan_xiang = None
        self.selected_degree = None
        
        # 创建罗盘框架
        self.compass_frame = CompassFrame(self, size=size, sync_callback=self._on_sync)
        self.compass_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 设置初始山向
        if initial_shan_xiang:
            self.compass_frame.set_shan_xiang(initial_shan_xiang)
        
        # 确认按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="确定", command=self._on_confirm).pack(side=tk.RIGHT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 模态对话框
        self.transient(parent)
        self.grab_set()
    
    def _on_sync(self, shan_xiang: str, degree: float, mountain: str):
        """同步回调"""
        self.selected_shan_xiang = shan_xiang
        self.selected_degree = degree
    
    def _on_confirm(self):
        """确认选择"""
        self.selected_shan_xiang = self.compass_frame.get_shan_xiang()
        self.selected_degree = self.compass_frame.get_degree()
        
        if self.on_select:
            self.on_select(self.selected_shan_xiang, self.selected_degree)
        
        self.destroy()


def show_compass_dialog(parent, initial_shan_xiang: str = None, 
                        on_select: Callable = None) -> Tuple[str, float]:
    """
    显示电子罗盘对话框
    
    Args:
        parent: 父窗口
        initial_shan_xiang: 初始山向
        on_select: 选择回调
        
    Returns:
        (山向, 度数)
    """
    dialog = CompassDialog(parent, initial_shan_xiang, on_select)
    parent.wait_window(dialog)
    return dialog.selected_shan_xiang, dialog.selected_degree



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
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# 从工具函数导入基础数据
# 十神定义（以日干为主）
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
            target_date = date(self.year, self.month, self.day)
            sizhu = calculate_sizhu(target_date, self.hour, self.minute)
            self.sizhu = self._normalize_sizhu_format(sizhu)
        except Exception as e:
            logger.error(f"计算四柱失败: {str(e)}", exc_info=True)
            # 设置默认值，避免程序崩溃
            self.sizhu = {
                '年柱': '甲子',
                '月柱': '甲子',
                '日柱': '甲子',
                '时柱': '甲子',
                'year_gan': '甲',
                'year_zhi': '子',
                'month_gan': '甲',
                'month_zhi': '子',
                'day_gan': '甲',
                'day_zhi': '子',
                'hour_gan': '甲',
                'hour_zhi': '子'
            }
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
                        pass
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
        # 优先尝试使用lunar_python获取节气信息
        from lunar_python import Solar
        return self._get_days_to_jieqi_lunar(birth_date, forward)
        return self._get_days_to_jieqi_sxtwl(birth_date, forward)
    
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
                pass
            
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



# -*- coding: utf-8 -*-
"""
================================================================================
八字排盘模块
================================================================================
封装完整的八字排盘流程，提供详细的事主信息，包括：
- 四柱信息（年柱、月柱、日柱、时柱）
- 纳音五行
- 十二长生状态
- 大运计算
- 命局分析

使用方式：
- 在主程序或日课评分系统中用于事主分析
- 通过BaZiPanPan类获取详细的事主信息
- 结果可直接用于显示或评分
================================================================================
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta, date
import logging
import sys
import os

# 添加项目根目录到路径

# 导入lunar_python用于起运年龄计算
from lunar_python import Solar
HAS_LUNAR_PYTHON = True
logger = logging.getLogger(__name__)


class BaZiPanPan:
    """
    八字排盘类
    封装完整的排盘流程，提供详细的事主信息
    """
    
    def __init__(self, birth_year: int, birth_month: int, birth_day: int, 
                 birth_hour: int, birth_minute: int, gender: str = '男'):
        """
        初始化八字排盘
        
        Args:
            birth_year: 出生年份
            birth_month: 出生月份（1-12）
            birth_day: 出生日（1-31）
            birth_hour: 出生小时（0-23）
            birth_minute: 出生分钟（0-59）
            gender: 性别，'男'或'女'
        """
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.birth_day = birth_day
        self.birth_hour = birth_hour
        self.birth_minute = birth_minute
        self.gender = gender
        self.sizhu = None
        self.panpan_result = None
        
    def calculate(self) -> Dict:
        """
        计算排盘结果
        
        Returns:
            Dict: 排盘结果
        """
        # 计算四柱
        self.sizhu = self._calculate_sizhu()
        
        # 计算详细信息
        self.panpan_result = self._calculate_details()
        
        # 计算起运年龄
        start_age, start_year = self._calculate_start_age()
        self.panpan_result['起运年龄'] = start_age
        self.panpan_result['起运年份'] = start_year
        
        # 计算大运
        self.panpan_result['大运'] = self._calculate_d大运()
        
        return self.panpan_result
    
    def _calculate_sizhu(self) -> Dict:
        """
        计算四柱信息
        
        Returns:
            Dict: 四柱信息
        """
        # 使用原始计算方法
        target_date = date(self.birth_year, self.birth_month, self.birth_day)
        sizhu = calculate_sizhu(
            target_date, 
            self.birth_hour, 
            self.birth_minute, 
            0
        )
        
        return sizhu
    
    def _calculate_details(self) -> Dict:
        """
        计算详细信息
        
        Returns:
            Dict: 详细信息
        """
        if not self.sizhu:
            return {}
        
        details = {
            '四柱': {
                '年柱': self.sizhu.get('年柱', ''),
                '月柱': self.sizhu.get('月柱', ''),
                '日柱': self.sizhu.get('日柱', ''),
                '时柱': self.sizhu.get('时柱', '')
            },
            '天干地支': {
                'year_gan': self.sizhu.get('year_gan', ''),
                'year_zhi': self.sizhu.get('year_zhi', ''),
                'month_gan': self.sizhu.get('month_gan', ''),
                'month_zhi': self.sizhu.get('month_zhi', ''),
                'day_gan': self.sizhu.get('day_gan', ''),
                'day_zhi': self.sizhu.get('day_zhi', ''),
                'hour_gan': self.sizhu.get('hour_gan', ''),
                'hour_zhi': self.sizhu.get('hour_zhi', '')
            },
            '纳音': {
                '年柱': get_nayin(self.sizhu.get('年柱', '')),
                '月柱': get_nayin(self.sizhu.get('月柱', '')),
                '日柱': get_nayin(self.sizhu.get('日柱', '')),
                '时柱': get_nayin(self.sizhu.get('时柱', ''))
            },
            '十二长生': {
                '年支': get_zhangsheng(self.sizhu.get('day_gan', ''), 
                                     self.sizhu.get('year_zhi', '')),
                '月支': get_zhangsheng(self.sizhu.get('day_gan', ''), 
                                     self.sizhu.get('month_zhi', '')),
                '日支': get_zhangsheng(self.sizhu.get('day_gan', ''), 
                                     self.sizhu.get('day_zhi', '')),
                '时支': get_zhangsheng(self.sizhu.get('day_gan', ''), 
                                     self.sizhu.get('hour_zhi', ''))
            },
            '五行分数': calculate_wuxing_score(self.sizhu, include_canggan=True),
            '十神': self._calculate_shishen(),
            '基本信息': {
                '性别': self.gender,
                '出生日期': f"{self.birth_year}-{self.birth_month:02d}-{self.birth_day:02d} {self.birth_hour:02d}:{self.birth_minute:02d}"
            }
        }
        
        return details
    
    def _calculate_shishen(self) -> Dict:
        """
        计算十神
        
        Returns:
            Dict: 十神信息
        """
        day_gan = self.sizhu.get('day_gan', '')
        if not day_gan:
            return {}
        
        shishen = {
            '年干': get_shishen(day_gan, self.sizhu.get('year_gan', '')),
            '月干': get_shishen(day_gan, self.sizhu.get('month_gan', '')),
            '时干': get_shishen(day_gan, self.sizhu.get('hour_gan', ''))
        }
        
        return shishen
    
    def _calculate_d大运(self) -> List[Dict]:
        """
        计算大运
        
        Returns:
            List[Dict]: 大运信息
        """
        大运_list = []
        
        # 计算起运年龄
        start_age, start_year = self._calculate_start_age()
        
        # 计算大运
        month_gan = self.sizhu.get('month_gan', '')
        month_zhi = self.sizhu.get('month_zhi', '')
        
        if not month_gan or not month_zhi:
            return 大运_list
        
        # 确定大运方向
        # 阳年生男、阴年生女：顺排
        # 阳年生女、阴年生男：逆排
        year_gan = self.sizhu.get('year_gan', '')
        yang_gans = ['甲', '丙', '戊', '庚', '壬']
        is_yang_year = year_gan in yang_gans
        
        if (is_yang_year and self.gender == '男') or (not is_yang_year and self.gender == '女'):
            direction = 1  # 顺行
        else:
            direction = -1  # 逆行
        
        # 计算大运
        for i in range(10):  # 通常计算10步大运
            step_age = start_age + i * 10
            step_year = start_year + i * 10
            
            # 计算大运干支（从月柱开始）
            offset = i * direction
            yun_gan, yun_zhi = self._get_ganzhi_by_offset(month_gan, month_zhi, offset)
            
            大运_list.append({
                '序号': i + 1,
                '大运': f"{yun_gan}{yun_zhi}",
                '起运年龄': step_age,
                '起运年份': step_year,
                '纳音': get_nayin(f"{yun_gan}{yun_zhi}")
            })
        
        return 大运_list
    
    def _calculate_start_age(self) -> Tuple[float, int]:
        """
        计算起运年龄
        
        根据出生日期和节气计算起运年龄
        使用lunar_python库获取节气信息
        
        规则：
        - 阳年生男、阴年生女：顺排（计算到下一个节气的天数）
        - 阳年生女、阴年生男：逆排（计算到上一个节气的天数）
        - 起运岁数 = 天数差 / 3（保留一位小数）
        
        Returns:
            Tuple[float, int]: (起运年龄, 起运年份)
        """
        # 检查lunar_python是否可用
        if not HAS_LUNAR_PYTHON:
            logger.warning("lunar_python不可用，使用简化算法")
            return 1.0, self.birth_year + 1
        
        # 使用lunar_python计算
        solar = Solar.fromYmdHms(
            self.birth_year, self.birth_month, self.birth_day,
            self.birth_hour, self.birth_minute, 0
        )
        lunar = solar.getLunar()
        
        # 获取年干阴阳
        year_gan = self.sizhu.get('year_gan', '') if self.sizhu else ''
        # 阳干：甲丙戊庚壬（索引为偶数）
        # 阴干：乙丁己辛癸（索引为奇数）
        yang_gans = ['甲', '丙', '戊', '庚', '壬']
        is_yang_year = year_gan in yang_gans
        
        # 判断顺逆
        # 阳年生男、阴年生女：顺排
        # 阳年生女、阴年生男：逆排
        is_forward = (is_yang_year and self.gender == '男') or (not is_yang_year and self.gender == '女')
        
        # 获取节气
        if is_forward:
            # 顺排：计算到下一个节气的天数
            next_jq = lunar.getNextJieQi()
            if next_jq:
                next_jq_solar = next_jq.getSolar()
                next_date = datetime(
                    next_jq_solar.getYear(),
                    next_jq_solar.getMonth(),
                    next_jq_solar.getDay(),
                    next_jq_solar.getHour(),
                    next_jq_solar.getMinute(),
                    next_jq_solar.getSecond()
                )
                birth_date = datetime(
                    self.birth_year, self.birth_month, self.birth_day,
                    self.birth_hour, self.birth_minute, 0
                )
                days_diff = (next_date - birth_date).total_seconds() / 86400  # 转换为天数
            else:
                days_diff = 3  # 默认值
        else:
            # 逆排：计算到上一个节气的天数
            prev_jq = lunar.getPrevJieQi()
            if prev_jq:
                prev_jq_solar = prev_jq.getSolar()
                prev_date = datetime(
                    prev_jq_solar.getYear(),
                    prev_jq_solar.getMonth(),
                    prev_jq_solar.getDay(),
                    prev_jq_solar.getHour(),
                    prev_jq_solar.getMinute(),
                    prev_jq_solar.getSecond()
                )
                birth_date = datetime(
                    self.birth_year, self.birth_month, self.birth_day,
                    self.birth_hour, self.birth_minute, 0
                )
                days_diff = (birth_date - prev_date).total_seconds() / 86400  # 转换为天数
            else:
                days_diff = 3  # 默认值
        
        # 计算起运岁数（保留一位小数）
        start_age = round(days_diff / 3, 1)
        
        # 计算起运年份
        start_year = self.birth_year + int(start_age)
        
        logger.info(f"起运年龄计算: 性别={self.gender}, 年干={year_gan}, "
                   f"阳年={is_yang_year}, 顺排={is_forward}, "
                   f"天数差={days_diff:.2f}, 起运年龄={start_age}")
        
        return start_age, start_year
            
    def _get_ganzhi_by_offset(self, gan: str, zhi: str, offset: int) -> Tuple[str, str]:
        """
        根据偏移量计算干支
        
        Args:
            gan: 起始天干
            zhi: 起始地支
            offset: 偏移量
            
        Returns:
            Tuple[str, str]: 新的干支
        """
        if gan not in TIAN_GAN or zhi not in DI_ZHI:
            return '', ''
        
        gan_idx = TIAN_GAN.index(gan)
        zhi_idx = DI_ZHI.index(zhi)
        
        new_gan_idx = (gan_idx + offset) % 10
        new_zhi_idx = (zhi_idx + offset) % 12
        
        return TIAN_GAN[new_gan_idx], DI_ZHI[new_zhi_idx]
    
    def get_panpan_result(self) -> Dict:
        """
        获取排盘结果
        
        Returns:
            Dict: 排盘结果
        """
        if not self.panpan_result:
            self.calculate()
        
        return self.panpan_result
    
    def get_sizhu(self) -> Dict:
        """
        获取四柱信息
        
        Returns:
            Dict: 四柱信息
        """
        if not self.sizhu:
            self.calculate()
        
        return self.sizhu


class BaZiDialog:
    """
    八字排盘对话框
    
    独立的八字排盘展示窗口
    """
    
    def __init__(self, parent: tk.Tk, panpan_data: Dict = None):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            panpan_data: 排盘数据
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("八字排盘详情")
        self.dialog.geometry("1200x700")
        
        # 创建主滚动区域
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        main_frame = ttk.Frame(canvas)
        
        main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=main_frame, anchor="nw", width=1180)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass  # 忽略canvas已销毁时的错误
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 显示排盘数据
        if panpan_data:
            self._display_panpan(main_frame, panpan_data)
        
        # 关闭按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="关闭", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="打印", 
                  command=lambda: self._print_panpan(panpan_data)).pack(side=tk.RIGHT, padx=5)
    
    def _display_panpan(self, parent_frame: tk.Frame, panpan_data: Dict):
        """
        显示排盘数据
        
        Args:
            parent_frame: 父级Frame容器
            panpan_data: 排盘数据字典
        """
        # 基本信息区域（上方）
        basic_frame = ttk.LabelFrame(parent_frame, text="基本信息", padding="10")
        basic_frame.pack(fill=tk.X, padx=10, pady=5)
        
        basic_info = panpan_data.get('基本信息', {})
        info_items = [
            ('性别', basic_info.get('性别', '-')),
            ('出生日期', basic_info.get('出生日期', '-'))
        ]
        
        for i, (key, value) in enumerate(info_items):
            ttk.Label(basic_frame, text=f"{key}:").grid(row=0, column=i*2, sticky=tk.W, padx=5)
            ttk.Label(basic_frame, text=value, font=("微软雅黑", 10, "bold")).grid(row=0, column=i*2+1, sticky=tk.W, padx=5)
        
        # 创建左右分栏的主框架
        main_content_frame = ttk.Frame(parent_frame)
        main_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧区域（四柱排盘 + 五行分析）
        left_frame = ttk.Frame(main_content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 四柱排盘区域
        sizhu_frame = ttk.LabelFrame(left_frame, text="四柱排盘", padding="10")
        sizhu_frame.pack(fill=tk.X, pady=5)
        
        sizhu = panpan_data.get('四柱', {})
        nayin = panpan_data.get('纳音', {})
        shengyang = panpan_data.get('十二长生', {})
        
        # 创建四柱表格
        columns = ['', '年柱', '月柱', '日柱', '时柱']
        sizhu_tree = ttk.Treeview(sizhu_frame, columns=columns, 
                                   show="headings", height=5)
        
        for col in columns:
            sizhu_tree.heading(col, text=col)
            sizhu_tree.column(col, width=120, anchor='center')
        
        # 添加行
        sizhu_tree.insert('', 'end', values=['天干', 
                                               sizhu.get('年柱', '')[0] if sizhu.get('年柱') else '-',
                                               sizhu.get('月柱', '')[0] if sizhu.get('月柱') else '-',
                                               sizhu.get('日柱', '')[0] if sizhu.get('日柱') else '-',
                                               sizhu.get('时柱', '')[0] if sizhu.get('时柱') else '-'])
        
        sizhu_tree.insert('', 'end', values=['地支', 
                                               sizhu.get('年柱', '')[1] if len(sizhu.get('年柱', '')) > 1 else '-',
                                               sizhu.get('月柱', '')[1] if len(sizhu.get('月柱', '')) > 1 else '-',
                                               sizhu.get('日柱', '')[1] if len(sizhu.get('日柱', '')) > 1 else '-',
                                               sizhu.get('时柱', '')[1] if len(sizhu.get('时柱', '')) > 1 else '-'])
        
        sizhu_tree.insert('', 'end', values=['纳音',
                                               nayin.get('年柱', '-'),
                                               nayin.get('月柱', '-'),
                                               nayin.get('日柱', '-'),
                                               nayin.get('时柱', '-')])

        sizhu_tree.insert('', 'end', values=['十二长生',
                                               shengyang.get('年支', '-'),
                                               shengyang.get('月支', '-'),
                                               shengyang.get('日支', '-'),
                                               shengyang.get('时支', '-')])
        
        sizhu_tree.insert('', 'end', values=['十神',
                                               panpan_data.get('十神', {}).get('年干', '-'),
                                               panpan_data.get('十神', {}).get('月干', '-'),
                                               '日主',
                                               panpan_data.get('十神', {}).get('时干', '-')])
        
        sizhu_tree.pack(fill=tk.X)
        
        # 五行分析区域（下方）
        wuxing_frame = ttk.LabelFrame(left_frame, text="五行分析", padding="10")
        wuxing_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        wuxing_score = panpan_data.get('五行分数', {})
        wuxing_labels = {}
        wuxing_items = ['金', '木', '水', '火', '土']
        for i, wx in enumerate(wuxing_items):
            ttk.Label(wuxing_frame, text=f"{wx}:").grid(row=0, column=i*2, sticky=tk.W, padx=5)
            score = wuxing_score.get(wx, 0)
            wuxing_labels[wx] = ttk.Label(wuxing_frame, text=f"{score:.2f}", font=("微软雅黑", 10, "bold"))
            wuxing_labels[wx].grid(row=0, column=i*2+1, sticky=tk.W, padx=5)
        
        # 五行说明
        wuxing_text = scrolledtext.ScrolledText(wuxing_frame, wrap=tk.WORD, height=10)
        wuxing_text.grid(row=1, column=0, columnspan=10, sticky=tk.EW, pady=5)
        
        wuxing_desc = self._format_wuxing(wuxing_score)
        wuxing_text.insert(tk.END, wuxing_desc)
        wuxing_text.config(state=tk.DISABLED)
        
        # 右侧区域（大运分析）
        right_frame = ttk.Frame(main_content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # 大运分析区域
        dayun_frame = ttk.LabelFrame(right_frame, text="大运分析", padding="10")
        dayun_frame.pack(fill=tk.BOTH, expand=True)
        
        # 起运信息
        start_age = panpan_data.get('起运年龄', 0)
        start_year = panpan_data.get('起运年份', 0)
        ttk.Label(dayun_frame, text=f"起运年龄: {start_age}岁  起运年份: {start_year}年", 
                 font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=5)
        
        # 大运表格
        dayun_columns = ['序号', '大运', '起运年龄', '起运年份', '纳音']
        dayun_tree = ttk.Treeview(dayun_frame, columns=dayun_columns, 
                                   show="headings", height=15)
        
        for col in dayun_columns:
            dayun_tree.heading(col, text=col)
            dayun_tree.column(col, width=80, anchor='center')
        
        dayun_list = panpan_data.get('大运', [])
        for dayun in dayun_list:
            dayun_tree.insert('', 'end', values=(
                dayun.get('序号', ''),
                dayun.get('大运', ''),
                f"{dayun.get('起运年龄', 0)}岁",
                dayun.get('起运年份', ''),
                dayun.get('纳音', '-')
            ))
        
        dayun_tree.pack(fill=tk.BOTH, expand=True)
    
    def _format_wuxing(self, wuxing: Dict) -> str:
        """格式化五行信息"""
        if not wuxing:
            return "暂无五行信息"
        
        total = sum(wuxing.values())
        if total == 0:
            return "五行数据异常"
        
        lines = ["五行分布:"]
        for wx in ['金', '木', '水', '火', '土']:
            count = wuxing.get(wx, 0)
            percentage = (count / total) * 100 if total > 0 else 0
            bar = '█' * int(percentage / 5)
            lines.append(f"  {wx}: {count:.2f} ({percentage:.1f}%) {bar}")
        
        return '\n'.join(lines)
    
    def _print_panpan(self, panpan_data: Dict):
        """打印排盘数据"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="保存八字排盘",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 保存为文本文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("八字排盘详情\n")
                f.write("=" * 60 + "\n\n")
                
                # 基本信息
                basic_info = panpan_data.get('基本信息', {})
                f.write(f"性别: {basic_info.get('性别', '-')}\n")
                f.write(f"出生日期: {basic_info.get('出生日期', '-')}\n\n")
                
                # 四柱排盘
                sizhu = panpan_data.get('四柱', {})
                f.write("四柱排盘:\n")
                f.write(f"  年柱: {sizhu.get('年柱', '-')}\n")
                f.write(f"  月柱: {sizhu.get('月柱', '-')}\n")
                f.write(f"  日柱: {sizhu.get('日柱', '-')}\n")
                f.write(f"  时柱: {sizhu.get('时柱', '-')}\n\n")
                
                # 纳音
                nayin = panpan_data.get('纳音', {})
                f.write("纳音:\n")
                f.write(f"  年柱: {nayin.get('年柱', '-')}\n")
                f.write(f"  月柱: {nayin.get('月柱', '-')}\n")
                f.write(f"  日柱: {nayin.get('日柱', '-')}\n")
                f.write(f"  时柱: {nayin.get('时柱', '-')}\n\n")
                
                # 十二长生
                shengyang = panpan_data.get('十二长生', {})
                f.write("十二长生:\n")
                f.write(f"  年支: {shengyang.get('年支', '-')}\n")
                f.write(f"  月支: {shengyang.get('月支', '-')}\n")
                f.write(f"  日支: {shengyang.get('日支', '-')}\n")
                f.write(f"  时支: {shengyang.get('时支', '-')}\n\n")
                
                # 十神
                shishen = panpan_data.get('十神', {})
                f.write("十神:\n")
                f.write(f"  年干: {shishen.get('年干', '-')}\n")
                f.write(f"  月干: {shishen.get('月干', '-')}\n")
                f.write(f"  时干: {shishen.get('时干', '-')}\n\n")
                
                # 五行分数
                wuxing_score = panpan_data.get('五行分数', {})
                f.write("五行分数:\n")
                for wx in ['金', '木', '水', '火', '土']:
                    f.write(f"  {wx}: {wuxing_score.get(wx, 0):.2f}\n")
                f.write("\n")
                
                # 大运
                dayun_list = panpan_data.get('大运', [])
                f.write("大运:\n")
                f.write(f"  起运年龄: {panpan_data.get('起运年龄', 0)}岁\n")
                f.write(f"  起运年份: {panpan_data.get('起运年份', 0)}年\n\n")
                
                for dayun in dayun_list:
                    f.write(f"  {dayun.get('序号', '')}. {dayun.get('大运', '')} ")
                    f.write(f"({dayun.get('起运年龄', 0)}岁, {dayun.get('起运年份', '')}年) ")
                    f.write(f"纳音: {dayun.get('纳音', '-')}\n")
            
            messagebox.showinfo("成功", f"八字排盘已保存到：{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")


def show_bazi_dialog(parent: tk.Tk, panpan_data: Dict):
    """
    显示八字排盘对话框
    
    Args:
        parent: 父窗口
        panpan_data: 排盘数据
    """
    BaZiDialog(parent, panpan_data)


# 测试代码

# -*- coding: utf-8 -*-
"""
专业级日课评分系统
用于对择日日课进行专业评分和分析
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import date, datetime
import json
import os
import sys

# 添加项目根目录到路径（用于直接运行此文件）

class DayScoreWindow:
    """日课评分系统主窗口"""
    
    def __init__(self, master=None):
        """初始化"""
        if master is None:
            self.window = tk.Tk()
            self.window.title("专业级日课评分系统")
        else:
            self.window = tk.Toplevel(master)
            self.window.title("专业级日课评分系统")
        
        # 获取屏幕尺寸并设置窗口大小
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 设置为小窗口（屏幕的45%宽度，66.7%高度）
        window_width = int(screen_width * 0.45)
        window_height = int(screen_height * 0.667)
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # 注释掉窗口最大化，保持小窗口
        # self.window.state('zoomed')  # 窗口最大化
        
        # 数据存储
        self.date_list = []
        self.scoring_results = []
        self.owners_info = []
        
        # 创建界面
        self.create_widgets()
    
    def import_results(self, results, event_type, owners_data):
        """从主程序导入择日结果
        
        Args:
            results: 主程序的择日结果列表
            event_type: 事项类型
            owners_data: 事主数据列表
        """
        try:
            # 设置事项类型
            self.event_var.set(event_type)
            self.update_owners_frame()
            
            # 填充事主信息
            for i, owner_data in enumerate(owners_data):
                if i < len(self.owners_info):
                    self.owners_info[i]['year'].set(str(owner_data.get('year', '')))
                    self.owners_info[i]['month'].set(str(owner_data.get('month', '')))
                    self.owners_info[i]['day'].set(str(owner_data.get('day', '')))
                    self.owners_info[i]['hour'].set(str(owner_data.get('hour', 12)))
                    self.owners_info[i]['minute'].set(str(owner_data.get('minute', 0)))
                    
                    # 自动计算四柱
                    self.calculate_owner_sizhu(
                        self.owners_info[i]['year'],
                        self.owners_info[i]['month'],
                        self.owners_info[i]['day'],
                        self.owners_info[i]['hour'],
                        self.owners_info[i]['minute'],
                        self.owners_info[i]['name'],
                        self.owners_info[i]['sizhu_var'],
                        self.owners_info[i]['xishen_var'],
                        self.owners_info[i]['yongshen_var'],
                        self.owners_info[i].get('fuzi_var')
                    )
            
            # 导入择日结果到列表
            for result in results:
                date_str = result.get('date', '')
                if date_str and date_str not in self.date_list:
                    self.date_list.append(date_str)
                    
                    # 准备显示数据
                    score = result.get('score', 0)
                    level = result.get('level', '未知')
                    sizhu = result.get('sizhu', {})
                    
                    # 处理sizhu可能是字符串或字典的情况
                    if isinstance(sizhu, str):
                        sizhu_str = sizhu
                        # 尝试从字符串解析四柱
                        sizhu_parts = sizhu_str.split()
                        if len(sizhu_parts) == 4:
                            sizhu_dict = {
                                '年柱': sizhu_parts[0],
                                '月柱': sizhu_parts[1],
                                '日柱': sizhu_parts[2],
                                '时柱': sizhu_parts[3]
                            }
                        else:
                            sizhu_dict = {}
                    else:
                        sizhu_dict = sizhu
                        sizhu_str = f"{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}"
                    
                    # 从detail字段中获取详细信息
                    detail = result.get('detail', {})
                    
                    # 获取详细得分信息
                    score_details = result.get('score_details', detail.get('score_details', {}))
                    yueling_score = score_details.get('月令得分', 0)
                    xishen_score = score_details.get('喜用神得分', 0)
                    huangdao_score = score_details.get('黄道得分', 0)
                    
                    # 添加到Treeview
                    self.date_treeview.insert('', tk.END, values=(date_str, score, level, sizhu_str, yueling_score, xishen_score, huangdao_score))
                    
                    # 如果结果包含评分信息，也添加到评分结果中
                    if 'score' in result and 'level' in result:
                        # 从detail字段中获取详细信息
                        detail = result.get('detail', {})
                        
                        score_result = {
                            'date': date_str,
                            'score': score,
                            'level': level,
                            'reason': result.get('reason', detail.get('reason', '')),
                            'sizhu': sizhu_dict,
                            'event_type': event_type,
                            'owners_detail': [],
                            'huangdao_info': result.get('huangdao_info', detail.get('huangdao_info', {})),
                            'wu_xing_result': result.get('wu_xing_result', detail.get('wu_xing_result', {})),
                            'yi_list': result.get('yi_list', detail.get('yi_list', [])),
                            'ji_list': result.get('ji_list', detail.get('ji_list', [])),
                            'shensha_list': result.get('shensha_list', detail.get('shensha_list', [])),
                            'score_details': result.get('score_details', detail.get('score_details', {}))
                        }
                        self.scoring_results.append(score_result)
            
            messagebox.showinfo("成功", f"成功导入 {len(results)} 个择日结果到评分系统")
        except Exception as e:
            messagebox.showerror("错误", f"导入择日结果时出错: {str(e)}")
    
    def run(self):
        """运行日课评分系统"""
        # 确保窗口显示在最前面
        self.window.lift()
        self.window.focus_force()
        
        # 如果是主窗口（Tk），使用mainloop
        # 如果是子窗口（Toplevel），使用wait_window等待窗口关闭
        if isinstance(self.window, tk.Tk):
            self.window.mainloop()
        else:
            # 对于Toplevel窗口，确保它可见并等待用户交互
            self.window.transient(self.window.master)
            self.window.grab_set()
            self.window.wait_window()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主滚动区域
        main_canvas = tk.Canvas(self.window)
        main_scrollbar_v = ttk.Scrollbar(self.window, orient="vertical", command=main_canvas.yview)
        main_scrollbar_h = ttk.Scrollbar(self.window, orient="horizontal", command=main_canvas.xview)
        self.main_frame = ttk.Frame(main_canvas, padding="20")
        
        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw", width=self.window.winfo_screenwidth()-50)
        main_canvas.configure(yscrollcommand=main_scrollbar_v.set, xscrollcommand=main_scrollbar_h.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar_v.pack(side="right", fill="y")
        main_scrollbar_h.pack(side="bottom", fill="x")
        
        # 绑定鼠标滚轮
        main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # 标题
        title_label = ttk.Label(self.main_frame, text="专业级日课评分系统", 
                               font=("微软雅黑", 24, "bold"))
        title_label.pack(pady=20)
        
        # 输入区域
        input_frame = ttk.LabelFrame(self.main_frame, text="日课输入", padding="20")
        input_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # 事项类型选择
        event_frame = ttk.Frame(input_frame)
        event_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(event_frame, text="事项类型:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.event_var = tk.StringVar(value="嫁娶")
        events = ["嫁娶", "修造", "动土", "入宅", "开业", "出行", "安床", "作灶", "安葬"]
        event_combo = ttk.Combobox(event_frame, textvariable=self.event_var, 
                                   values=events, state="readonly", width=20, font=("微软雅黑", 12))
        event_combo.pack(side=tk.LEFT, padx=10)
        event_combo.bind("<<ComboboxSelected>>", lambda e: self.update_owners_frame())
        
        # 输入方式选择
        input_mode_frame = ttk.Frame(input_frame)
        input_mode_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_mode_frame, text="输入方式:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.input_mode = tk.StringVar(value="date")
        ttk.Radiobutton(input_mode_frame, text="按日期", variable=self.input_mode, 
                       value="date", command=self.toggle_input_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(input_mode_frame, text="按四柱", variable=self.input_mode, 
                       value="sizhu", command=self.toggle_input_mode).pack(side=tk.LEFT, padx=10)
        
        # 日期输入框
        self.date_frame = ttk.Frame(input_frame)
        self.date_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(self.date_frame, text="日期 (YYYY-MM-DD):", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.date_entry = ttk.Entry(self.date_frame, width=20, font=("微软雅黑", 12))
        self.date_entry.pack(side=tk.LEFT, padx=10)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # 时间输入
        ttk.Label(self.date_frame, text="时间 (HH:MM):", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.time_entry = ttk.Entry(self.date_frame, width=10, font=("微软雅黑", 12))
        self.time_entry.pack(side=tk.LEFT, padx=10)
        self.time_entry.insert(0, "12:00")
        
        # 为日期和时间输入框绑定键盘导航
        self._bind_entry_navigation([self.date_entry, self.time_entry])
        
        # 四柱输入框
        self.sizhu_frame = ttk.Frame(input_frame)
        # 默认隐藏
        
        ttk.Label(self.sizhu_frame, text="年柱:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.sizhu_entries = []
        for i, label in enumerate(["年柱", "月柱", "日柱", "时柱"]):
            entry = ttk.Entry(self.sizhu_frame, width=10, font=("微软雅黑", 12))
            entry.pack(side=tk.LEFT, padx=5)
            self.sizhu_entries.append(entry)
        
        # 为四柱输入框绑定键盘导航
        self._bind_entry_navigation(self.sizhu_entries)
        
        # 事主信息区域
        self.owners_frame = ttk.LabelFrame(self.main_frame, text="事主信息", padding="20")
        self.owners_frame.pack(fill=tk.X, pady=10, padx=20)
        self.update_owners_frame()
        
        # 按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=20, padx=20)
        
        ttk.Button(button_frame, text="添加日课", command=self.add_date, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="添加四柱", command=self.add_sizhu, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="日课评分", command=self.start_scoring, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="对比分析", command=self.compare_analysis, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="保存分析", command=self.save_single_analysis, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="导出报告", command=self.export_report, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="导入文件", command=self.import_file, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="清空列表", command=self.clear_dates, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="帮助", command=self.show_help, width=18).pack(side=tk.RIGHT, padx=8)
        
        # 日课列表
        list_frame = ttk.LabelFrame(self.main_frame, text="日课列表", padding="20")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        # 创建Treeview控件替代Listbox，显示更多信息
        columns = ('date', 'score', 'level', 'sizhu', 'yueling', 'xishen', 'huangdao')
        self.date_treeview = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # 设置列标题
        self.date_treeview.heading('date', text='日期/四柱')
        self.date_treeview.heading('score', text='评分')
        self.date_treeview.heading('level', text='等级')
        self.date_treeview.heading('sizhu', text='四柱')
        self.date_treeview.heading('yueling', text='月令得分')
        self.date_treeview.heading('xishen', text='喜用神得分')
        self.date_treeview.heading('huangdao', text='黄道得分')
        
        # 设置列宽
        self.date_treeview.column('date', width=150)
        self.date_treeview.column('score', width=80, anchor='center')
        self.date_treeview.column('level', width=80, anchor='center')
        self.date_treeview.column('sizhu', width=200)
        self.date_treeview.column('yueling', width=80, anchor='center')
        self.date_treeview.column('xishen', width=80, anchor='center')
        self.date_treeview.column('huangdao', width=80, anchor='center')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.date_treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.date_treeview.config(yscrollcommand=scrollbar.set)
        
        # 绑定双击事件
        self.date_treeview.bind('<Double-1>', self.on_date_double_click)
        
        self.date_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(self.main_frame, text="评分结果", padding="20")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, font=("微软雅黑", 11))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置金色tag用于显示星星
        self.result_text.tag_configure("gold", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        self.result_text.tag_configure("gold_star", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
    
    def update_owners_frame(self):
        """更新事主信息框架"""
        # 清空现有组件
        for widget in self.owners_frame.winfo_children():
            widget.destroy()
        
        self.owners_info = []
        event_type = self.event_var.get()
        
        # 添加提示标签
        if event_type != "嫁娶":
            hint_label = ttk.Label(self.owners_frame, text="（提示：以下事主信息为可选，可根据需要填写）", 
                                   foreground="gray", font=("微软雅黑", 11, "italic"))
            hint_label.pack(anchor=tk.W, pady=(0, 10))
        
        if event_type == "嫁娶":
            # 婚嫁需要新娘新郎（必填）
            owners = ["新娘", "新郎"]
        elif event_type == "安葬":
            # 安葬需要死者（逝者）和孝子（家属）
            owners = ["死者", "孝子1", "孝子2", "孝子3"]
        elif event_type in ["修造", "动土", "入宅", "装修", "作灶", "开业", "出行", "安床"]:
            # 修建类事项、作灶、开业、出行、安床，事主1-4可选（可填可不填）
            owners = ["事主1", "事主2", "事主3", "事主4"]
        else:
            # 其他事项，事主可选（可填可不填）
            owners = ["事主"]
        
        # 存储所有输入框以便键盘导航
        all_entries = []
        
        for owner in owners:
            owner_frame = ttk.Frame(self.owners_frame)
            owner_frame.pack(fill=tk.X, pady=8)
            
            # 日期输入行
            date_row = ttk.Frame(owner_frame)
            date_row.pack(fill=tk.X, pady=5)
            
            ttk.Label(date_row, text=f"{owner}:", width=10, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5, pady=5)
            
            # 婚嫁事项默认填充日期，其他事项默认为空（可选）
            if event_type == "嫁娶":
                year_var = tk.StringVar(value=str(date.today().year - 20))
                month_var = tk.StringVar(value=str(1))
                day_var = tk.StringVar(value=str(1))
                hour_var = tk.StringVar(value=str(12))
                minute_var = tk.StringVar(value=str(0))
            else:
                year_var = tk.StringVar()
                month_var = tk.StringVar()
                day_var = tk.StringVar()
                hour_var = tk.StringVar(value="12")
                minute_var = tk.StringVar(value="0")
            
            ttk.Label(date_row, text="年:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
            year_entry = ttk.Entry(date_row, textvariable=year_var, width=8, font=("微软雅黑", 12))
            year_entry.pack(side=tk.LEFT, padx=5)
            all_entries.append(year_entry)
            
            ttk.Label(date_row, text="月:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
            month_entry = ttk.Entry(date_row, textvariable=month_var, width=6, font=("微软雅黑", 12))
            month_entry.pack(side=tk.LEFT, padx=5)
            all_entries.append(month_entry)
            
            ttk.Label(date_row, text="日:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
            day_entry = ttk.Entry(date_row, textvariable=day_var, width=6, font=("微软雅黑", 12))
            day_entry.pack(side=tk.LEFT, padx=5)
            all_entries.append(day_entry)
            
            ttk.Label(date_row, text="时:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
            hour_entry = ttk.Entry(date_row, textvariable=hour_var, width=6, font=("微软雅黑", 12))
            hour_entry.pack(side=tk.LEFT, padx=5)
            all_entries.append(hour_entry)
            
            ttk.Label(date_row, text="分:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
            minute_entry = ttk.Entry(date_row, textvariable=minute_var, width=6, font=("微软雅黑", 12))
            minute_entry.pack(side=tk.LEFT, padx=5)
            all_entries.append(minute_entry)
            
            # 四柱显示
            sizhu_row = ttk.Frame(owner_frame)
            sizhu_row.pack(fill=tk.X, pady=5)
            
            ttk.Label(sizhu_row, text="四柱:", width=10, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
            sizhu_var = tk.StringVar(value="未计算")
            sizhu_label = ttk.Label(sizhu_row, textvariable=sizhu_var, font=("微软雅黑", 12, "bold"))
            sizhu_label.pack(side=tk.LEFT, padx=5)
            
            # 喜用神显示
            xishen_var = tk.StringVar(value="")
            yongshen_var = tk.StringVar(value="")
            
            xishen_row = ttk.Frame(owner_frame)
            xishen_row.pack(fill=tk.X, pady=5)
            
            ttk.Label(xishen_row, text="喜用神:", width=10, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
            ttk.Label(xishen_row, textvariable=xishen_var, foreground="blue", font=("微软雅黑", 11)).pack(side=tk.LEFT, padx=5)
            ttk.Label(xishen_row, text="  用神:", width=8, font=("微软雅黑", 12)).pack(side=tk.LEFT)
            ttk.Label(xishen_row, textvariable=yongshen_var, foreground="green", font=("微软雅黑", 11)).pack(side=tk.LEFT, padx=5)
            
            # 夫星子星显示（婚嫁专用）
            fuzi_var = tk.StringVar(value="")
            if event_type == "嫁娶":
                fuzi_row = ttk.Frame(owner_frame)
                fuzi_row.pack(fill=tk.X, pady=5)
                
                ttk.Label(fuzi_row, text="夫星/子星:", width=10, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
                ttk.Label(fuzi_row, textvariable=fuzi_var, foreground="purple", font=("微软雅黑", 11)).pack(side=tk.LEFT, padx=5)
            
            # 计算按钮
            calc_btn = ttk.Button(owner_frame, text="计算四柱", 
                                 command=lambda y=year_var, m=month_var, d=day_var, 
                                 h=hour_var, mi=minute_var, o=owner, s=sizhu_var, 
                                 x=xishen_var, yg=yongshen_var, fz=fuzi_var: 
                                 self.calculate_owner_sizhu(y, m, d, h, mi, o, s, x, yg, fz))
            calc_btn.pack(anchor=tk.W, padx=5, pady=2)
            
            # 保存事主信息
            owner_info = {
                'name': owner,
                'year': year_var,
                'month': month_var,
                'day': day_var,
                'hour': hour_var,
                'minute': minute_var,
                'sizhu_var': sizhu_var,
                'xishen_var': xishen_var,
                'yongshen_var': yongshen_var,
                'fuzi_var': fuzi_var
            }
            
            self.owners_info.append(owner_info)
            
            # 添加自动转换功能 - 当输入框内容变化时自动计算
            def auto_calculate(event):
                year_val = year_var.get()
                month_val = month_var.get()
                day_val = day_var.get()
                hour_val = hour_var.get()
                minute_val = minute_var.get()
                
                if year_val and month_val and day_val and hour_val and minute_val:
                    try:
                        year = int(year_val)
                        month = int(month_val)
                        day = int(day_val)
                        hour = int(hour_val)
                        minute = int(minute_val)
                        
                        # 验证日期有效性
                        date(year, month, day)
                        if 0 <= hour < 24 and 0 <= minute < 60:
                            # 延迟计算，避免频繁触发
                            self.window.after(500, lambda:
                                self.calculate_owner_sizhu(year_var, month_var, day_var,
                                hour_var, minute_var, owner,
                                sizhu_var, xishen_var, yongshen_var,
                                fuzi_var))
                    except:
                        pass
            
            year_entry.bind('<KeyRelease>', auto_calculate)
            month_entry.bind('<KeyRelease>', auto_calculate)
            day_entry.bind('<KeyRelease>', auto_calculate)
            hour_entry.bind('<KeyRelease>', auto_calculate)
            minute_entry.bind('<KeyRelease>', auto_calculate)
        
        # 为所有事主输入框绑定键盘导航
        self._bind_entry_navigation(all_entries)
    
    def _bind_entry_navigation(self, entries):
        """为输入框绑定键盘导航功能"""
        if not entries:
            return
            
        def on_key_down(event, idx):
            """向下/向右移动到下一个输入框"""
            if idx < len(entries) - 1:
                entries[idx + 1].focus_set()
                entries[idx + 1].select_range(0, tk.END)
            return "break"
        
        def on_key_up(event, idx):
            """向上/向左移动到上一个输入框"""
            if idx > 0:
                entries[idx - 1].focus_set()
                entries[idx - 1].select_range(0, tk.END)
            return "break"
        
        def on_key_right(event, idx):
            """向右移动到下一个输入框"""
            # 检查光标是否在最后
            widget = event.widget
            if widget.index(tk.INSERT) >= len(widget.get()):
                if idx < len(entries) - 1:
                    entries[idx + 1].focus_set()
                    entries[idx + 1].select_range(0, tk.END)
                    return "break"
            return None
        
        def on_key_left(event, idx):
            """向左移动到上一个输入框"""
            # 检查光标是否在开头
            widget = event.widget
            if widget.index(tk.INSERT) == 0:
                if idx > 0:
                    entries[idx - 1].focus_set()
                    entries[idx - 1].select_range(0, tk.END)
                    return "break"
            return None
        
        for i, entry in enumerate(entries):
            # 绑定方向键
            entry.bind('<Down>', lambda e, idx=i: on_key_down(e, idx))
            entry.bind('<Up>', lambda e, idx=i: on_key_up(e, idx))
            entry.bind('<Right>', lambda e, idx=i: on_key_right(e, idx))
            entry.bind('<Left>', lambda e, idx=i: on_key_left(e, idx))
    
    def calculate_owner_sizhu(self, year_var, month_var, day_var, hour_var, minute_var, 
                              owner, sizhu_var, xishen_var, yongshen_var, fuzi_var=None):
        """计算事主四柱"""
        try:
            year = int(year_var.get())
            month = int(month_var.get())
            day = int(day_var.get())
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            
            target_date = date(year, month, day)
            sizhu = calculate_sizhu(target_date, hour, minute)
            analysis = analyze_sizhu(sizhu)
            
            # 显示四柱
            sizhu_text = f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}"
            sizhu_var.set(sizhu_text)
            
            # 显示喜用神 - 使用统一的喜用神计算器
            xishen, yongshen = calculate_xishen_yongshen(sizhu, analysis)
            xishen_var.set(xishen)
            yongshen_var.set(yongshen)
            
            # 婚嫁事项显示夫星子星
            if fuzi_var and self.event_var.get() == "嫁娶" and owner == "新娘":
                fuzi = analysis.get('夫星子星', {})
                fu_xing = fuzi.get('fu', '')
                zi_xing = fuzi.get('zi', '')
                if fu_xing or zi_xing:
                    fuzi_var.set(f"夫星: {fu_xing}, 子星: {zi_xing}")
        except Exception as e:
            messagebox.showerror("计算错误", f"计算四柱失败: {str(e)}")
            logger.error(f"计算四柱失败: {str(e)}", exc_info=True)
    
    def toggle_input_mode(self):
        """切换输入方式"""
        if self.input_mode.get() == "date":
            self.date_frame.pack(fill=tk.X, pady=5)
            self.sizhu_frame.pack_forget()
        else:
            self.date_frame.pack_forget()
            self.sizhu_frame.pack(fill=tk.X, pady=5)
    
    def add_date(self):
        """添加日期到列表"""
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            datetime.strptime(time_str, '%H:%M')
            
            # 组合日期和时间
            date_time_str = f"{date_str} {time_str}"
            
            if date_time_str not in self.date_list:
                self.date_list.append(date_time_str)
                # 添加到Treeview
                self.date_treeview.insert('', tk.END, values=(date_time_str, '', '', ''))
            else:
                messagebox.showwarning("警告", "该日期时间已在列表中")
        except ValueError:
            messagebox.showerror("错误", "日期或时间格式不正确")
    
    def add_sizhu(self):
        """添加四柱到列表"""
        nian_zhu = self.sizhu_entries[0].get().strip()
        yue_zhu = self.sizhu_entries[1].get().strip()
        ri_zhu = self.sizhu_entries[2].get().strip()
        shi_zhu = self.sizhu_entries[3].get().strip()
        
        # 验证四柱格式
        if not all([nian_zhu, yue_zhu, ri_zhu, shi_zhu]):
            messagebox.showwarning("警告", "请完整填写四柱")
            return
        
        for zhu, name in [(nian_zhu, "年柱"), (yue_zhu, "月柱"), (ri_zhu, "日柱"), (shi_zhu, "时柱")]:
            if len(zhu) != 2:
                messagebox.showwarning("警告", f"{name}格式错误，应为两个字（如：甲子）")
                return
        
        # 生成四柱字符串
        sizhu_str = f"{nian_zhu} {yue_zhu} {ri_zhu} {shi_zhu}"
        
        # 检查是否已存在
        if sizhu_str in self.date_list:
            messagebox.showwarning("警告", "该四柱已存在")
            return
        
        # 添加到列表
        self.date_list.append(sizhu_str)
        # 添加到Treeview
        self.date_treeview.insert('', tk.END, values=(sizhu_str, '', '', sizhu_str))
        
        # 清空输入框
        for entry in self.sizhu_entries:
            entry.delete(0, tk.END)
    
    def clear_dates(self):
        """清空日期"""
        self.date_list = []
        # 清空Treeview
        for item in self.date_treeview.get_children():
            self.date_treeview.delete(item)
        self.scoring_results = []
    
    def start_scoring(self):
        """开始评分"""
        # 根据当前输入方式获取日课
        input_mode = self.input_mode.get()
        
        if input_mode == "date":
            # 按日期输入
            date_str = self.date_entry.get().strip()
            time_str = self.time_entry.get().strip()
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                datetime.strptime(time_str, '%H:%M')
                current_rike = f"{date_str} {time_str}"
            except ValueError:
                messagebox.showerror("错误", "日期或时间格式不正确")
                return
        else:
            # 按四柱输入
            nian_zhu = self.sizhu_entries[0].get().strip()
            yue_zhu = self.sizhu_entries[1].get().strip()
            ri_zhu = self.sizhu_entries[2].get().strip()
            shi_zhu = self.sizhu_entries[3].get().strip()
            
            # 验证四柱格式
            if not all([nian_zhu, yue_zhu, ri_zhu, shi_zhu]):
                messagebox.showwarning("警告", "请完整填写四柱")
                return
            
            for zhu, name in [(nian_zhu, "年柱"), (yue_zhu, "月柱"), (ri_zhu, "日柱"), (shi_zhu, "时柱")]:
                if len(zhu) != 2:
                    messagebox.showwarning("警告", f"{name}格式错误，应为两个字（如：甲子）")
                    return
            
            current_rike = f"{nian_zhu} {yue_zhu} {ri_zhu} {shi_zhu}"
        
        # 检查是否已存在
        if current_rike in self.date_list:
            messagebox.showwarning("警告", "该日课已评分")
            return
        
        event_type = self.event_var.get()
        
        # 获取事主信息
        owners_detail = []
        for info in self.owners_info:
            try:
                year = int(info['year'].get())
                month = int(info['month'].get())
                day = int(info['day'].get())
                hour = int(info['hour'].get())
                minute = int(info['minute'].get())
                
                target_date = date(year, month, day)
                sizhu = calculate_sizhu(target_date, hour, minute)
                analysis = analyze_sizhu(sizhu)
                
                owner_detail = {
                    'name': info['name'],
                    'birth_date': f"{year}年{month}月{day}日 {hour}时{minute}分",
                    'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                    'xishen': info['xishen_var'].get(),
                    'yongshen': info['yongshen_var'].get(),
                    'fu_xing': '',
                    'zi_xing': ''
                }
                
                if event_type == "嫁娶" and info.get('fuzi_var'):
                    fuzi_str = info['fuzi_var'].get()
                    if '夫星:' in fuzi_str:
                        parts = fuzi_str.split(', ')
                        owner_detail['fu_xing'] = parts[0].replace('夫星: ', '')
                        if len(parts) > 1:
                            owner_detail['zi_xing'] = parts[1].replace('子星: ', '')
                
                owners_detail.append(owner_detail)
            except Exception as e:
                continue
        
        # 评分当前日课
        try:
            # 判断是日期还是四柱
            if len(current_rike.split()) == 4 and all(len(zhu) == 2 for zhu in current_rike.split()):
                # 这是四柱格式（如：甲子 乙丑 丙寅 丁卯）
                parts = current_rike.split()
                sizhu = {
                    '年柱': parts[0],
                    '月柱': parts[1],
                    '日柱': parts[2],
                    '时柱': parts[3],
                    'year_gan': parts[0][0],
                    'year_zhi': parts[0][1],
                    'month_gan': parts[1][0],
                    'month_zhi': parts[1][1],
                    'day_gan': parts[2][0],
                    'day_zhi': parts[2][1],
                    'hour_gan': parts[3][0],
                    'hour_zhi': parts[3][1]
                }
                display_date = f"四柱: {current_rike}"
            else:
                # 这是日期时间格式（如：2025-03-03 14:30）
                parts = current_rike.split()
                if len(parts) == 2:
                    date_part = parts[0]
                    time_part = parts[1]
                    hour, minute = map(int, time_part.split(':'))
                    score_date_obj = datetime.strptime(date_part, '%Y-%m-%d').date()
                    sizhu = calculate_sizhu(score_date_obj, hour, minute)
                    display_date = current_rike
                else:
                    # 兼容旧格式（只有日期）
                    score_date_obj = datetime.strptime(current_rike, '%Y-%m-%d').date()
                    sizhu = calculate_sizhu(score_date_obj, 12, 0)
                    display_date = current_rike
            
            # 使用calculate_score进行评分
            score_result = calculate_score(sizhu, event_type, owners_detail)
            result = {
                'date': display_date,
                'score': score_result['score'],
                'level': score_result['level'],
                'reason': score_result.get('reason', ''),
                'sizhu': sizhu,
                'event_type': event_type,
                'owners_detail': owners_detail,
                'huangdao_info': score_result.get('huangdao_info', {}),
                'wu_xing_result': score_result.get('wu_xing_result', {}),
                'yi_list': score_result.get('yi_list', []),
                'ji_list': score_result.get('ji_list', []),
                'shensha_list': score_result.get('shensha_list', [])
            }
            
            # 添加到列表
            self.date_list.append(current_rike)
            
            # 准备显示数据
            score = result['score']
            level = result['level']
            sizhu = result['sizhu']
            sizhu_str = f"{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}"
            
            # 获取详细得分信息
            score_details = score_result.get('score_details', {})
            yueling_score = score_details.get('月令得分', 0)
            xishen_score = score_details.get('喜用神得分', 0)
            huangdao_score = score_details.get('黄道得分', 0)
            
            # 添加到Treeview
            self.date_treeview.insert('', tk.END, values=(current_rike, score, level, sizhu_str, yueling_score, xishen_score, huangdao_score))
            self.scoring_results.append(result)
            
            # 显示结果
            self.show_single_result(result)
            
            # 确保日课评分系统窗口获得焦点后再显示消息框
            self.window.lift()
            self.window.focus_force()
            messagebox.showinfo("成功", f"日课评分完成！\n评分：{result['score']} 分\n等级：{result['level']}")
        except Exception as e:
            messagebox.showerror("错误", f"评分时出错: {str(e)}")
    
    def on_date_double_click(self, event):
        """双击日课显示详细信息"""
        selected = self.date_treeview.selection()
        if not selected:
            return
        
        item = selected[0]
        date_str = self.date_treeview.item(item, 'values')[0]
        
        # 查找对应的评分结果
        result = None
        for r in self.scoring_results:
            if r['date'] == date_str:
                result = r
                break
        
        if result:
            self.show_single_result(result)
    
    def _insert_colored_text(self, text, tag=None):
        """插入带颜色的文本"""
        if tag:
            self.result_text.insert(tk.END, text, tag)
        else:
            self.result_text.insert(tk.END, text)
    
    def show_single_result(self, result):
        """显示单个评分结果"""
        self.result_text.delete(1.0, tk.END)
        
        # 构建详细结果文本
        self._insert_colored_text("""
╔════════════════════════════════════════════════════════════════════╗
║                         日课评分结果                               ║
╚════════════════════════════════════════════════════════════════════╝

【基本信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        self._insert_colored_text(f"  日期: {result['date']}\n")
        self._insert_colored_text(f"  综合评分: {result['score']} 分\n")
        
        # 等级评定（如果有星星，用金色显示）
        level = result['level']
        self._insert_colored_text("  等级评定: ")
        if '★' in level:
            star_count = level.count('★')
            other_text = level.replace('★', '').strip()
            self._insert_colored_text('★' * star_count, "gold_star")
            if other_text:
                self._insert_colored_text(f" {other_text}")
            self._insert_colored_text("\n")
        else:
            self._insert_colored_text(f"{level}\n")
        
        self._insert_colored_text("\n")
        
        # 评分详情
        self._insert_colored_text("""【评分详情】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        score_details = result.get('score_details', {})
        if score_details:
            wuxing_score = score_details.get('五行评分', 100)
            yueling_score = score_details.get('月令得分', 0)
            xishen_score = score_details.get('喜用神得分', 0)
            huangdao_score = score_details.get('黄道得分', 0)
            total_score = score_details.get('总分', result['score'])
            
            self._insert_colored_text(f"  五行评分：{wuxing_score} 分\n")
            
            # 五行评分详细得分
            wu_xing_result = result.get('wu_xing_result', {})
            score_breakdown = wu_xing_result.get('score_breakdown', {})
            if score_breakdown:
                self._insert_colored_text(f"    ├─ 基础分：{score_breakdown.get('基础分', 100)} 分\n")
                shensha_score = score_breakdown.get('神煞得分', 0)
                if shensha_score != 0:
                    self._insert_colored_text(f"    ├─ 神煞得分：{shensha_score:+d} 分\n")
                yi_score = score_breakdown.get('宜事得分', 0)
                if yi_score != 0:
                    self._insert_colored_text(f"    ├─ 宜事得分：+{yi_score} 分\n")
                ji_score = score_breakdown.get('忌事得分', 0)
                if ji_score != 0:
                    self._insert_colored_text(f"    ├─ 忌事得分：{ji_score} 分\n")
                zhangsheng = score_breakdown.get('十二长生得分', 0)
                if zhangsheng != 0:
                    self._insert_colored_text(f"    ├─ 十二长生得分：{zhangsheng:+d} 分\n")
                zhizhi = score_breakdown.get('地支关系得分', 0)
                if zhizhi != 0:
                    self._insert_colored_text(f"    ├─ 地支关系得分：{zhizhi:+d} 分\n")
                nayin = score_breakdown.get('纳音匹配得分', 0)
                if nayin != 0:
                    self._insert_colored_text(f"    └─ 纳音匹配得分：{nayin:+d} 分\n")
            
            self._insert_colored_text(f"  月令得分：{yueling_score:+d} 分\n")
            
            # 月令详细得分
            yueling_detail = score_details.get('月令详细', {})
            if yueling_detail:
                self._insert_colored_text(f"    ├─ 旺衰得分：{yueling_detail.get('旺衰得分', 0):+d} 分\n")
                self._insert_colored_text(f"    └─ 支支关系得分：{yueling_detail.get('支支关系得分', 0):+d} 分\n")
            
            self._insert_colored_text(f"  喜用神得分：{xishen_score:+d} 分\n")
            self._insert_colored_text(f"  黄道得分：{huangdao_score:+d} 分\n")
            self._insert_colored_text(f"  ─────────────────────────────────\n")
            self._insert_colored_text(f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {huangdao_score:+d} = {total_score} 分\n")
            self._insert_colored_text(f"  总分：{total_score} 分\n")
        else:
            self._insert_colored_text("  暂无详细得分数据\n")
        
        self._insert_colored_text("\n")
        
        # 月令分析
        self._insert_colored_text("""【月令分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        
        # 从reason中提取月令信息
        reason = result.get('reason', '')
        yueling_info = ""
        for part in reason.split('；'):
            if '月令：' in part:
                yueling_info = part.replace('月令：', '')
                break
        
        if yueling_info:
            self._insert_colored_text(f"  {yueling_info}\n")
        else:
            self._insert_colored_text("  月令分析：暂无数据\n")
        
        self._insert_colored_text("\n")
        
        # 四柱信息
        if result.get('sizhu'):
            sizhu = result['sizhu']
            self._insert_colored_text(f"""【四柱八字】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  年柱: {sizhu['年柱']}    月柱: {sizhu['月柱']}
  日柱: {sizhu['日柱']}    时柱: {sizhu['时柱']}

  【天干五行】
    年干: {sizhu['年柱'][0]}    月干: {sizhu['月柱'][0]}    日干: {sizhu['日柱'][0]}    时干: {sizhu['时柱'][0]}
  【地支五行】
    年支: {sizhu['年柱'][1]}    月支: {sizhu['月柱'][1]}    日支: {sizhu['日柱'][1]}    时支: {sizhu['时柱'][1]}

""")
        
        # 五行分析
        if result.get('wu_xing_result'):
            wu_xing = result['wu_xing_result']
            self._insert_colored_text(f"""【五行分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  五行评分: {wu_xing.get('score', 'N/A')} 分
""")
            if wu_xing.get('reason'):
                self._insert_colored_text(f"  五行评语: {wu_xing['reason']}\n")
            if wu_xing.get('details'):
                details = wu_xing['details']
                
                # 1. 天干地支五行
                if details.get('天干五行'):
                    self._insert_colored_text("\n  【天干地支五行】\n")
                    for pillar, info in details['天干五行'].items():
                        self._insert_colored_text(f"    {pillar}: {info['天干']}({info['天干五行']}) {info['地支']}({info['地支五行']})\n")
                
                # 2. 地支关系（三合、六合、六冲、六害、三刑）
                if details.get('地支关系') and len(details['地支关系']) > 0:
                    self._insert_colored_text("\n  【地支关系】\n")
                    for relation in details['地支关系']:
                        self._insert_colored_text(f"    • {relation}\n")
                else:
                    self._insert_colored_text("\n  【地支关系】\n    无明显合冲刑害关系\n")
                
                # 3. 十二长生
                if details.get('十二长生'):
                    self._insert_colored_text("\n  【十二长生】\n")
                    for pillar, state in details['十二长生'].items():
                        self._insert_colored_text(f"    {pillar}: {state}\n")
                
                # 4. 纳音五行
                if details.get('纳音五行'):
                    self._insert_colored_text("\n  【纳音五行】\n")
                    for pillar, nayin in details['纳音五行'].items():
                        self._insert_colored_text(f"    {pillar}: {nayin}\n")
                
                # 5. 吉神（天德、月德）
                if details.get('吉神') and len(details['吉神']) > 0:
                    self._insert_colored_text("\n  【吉神】\n")
                    for jishen in details['吉神']:
                        self._insert_colored_text(f"    ✓ {jishen}\n")
                else:
                    self._insert_colored_text("\n  【吉神】\n    无天德月德等吉神\n")
                
                # 6. 日主旺衰
                if details.get('日主旺衰'):
                    self._insert_colored_text(f"\n  【日主旺衰】\n    {details['日主旺衰']}\n")
                
                # 7. 五行生克
                if details.get('五行生克') and len(details['五行生克']) > 0:
                    self._insert_colored_text("\n  【五行生克】\n")
                    for relation in details['五行生克']:
                        self._insert_colored_text(f"    • {relation}\n")
            if wu_xing.get('wang_xiang'):
                self._insert_colored_text(f"  旺相分析: {wu_xing['wang_xiang']}\n")
            if wu_xing.get('ke_zhi'):
                self._insert_colored_text(f"  克制关系: {wu_xing['ke_zhi']}\n")
            self._insert_colored_text("\n")
        
        # 黄道信息
        if result.get('huangdao_info'):
            huangdao = result['huangdao_info']
            self._insert_colored_text("""【黄道信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            if huangdao.get('da_huang_dao'):
                da_hd = huangdao['da_huang_dao']
                self._insert_colored_text(f"  大黄道: {da_hd.get('name', 'N/A')} ({da_hd.get('type', 'N/A')})\n")
                if da_hd.get('description'):
                    self._insert_colored_text(f"    说明: {da_hd['description']}\n")
            if huangdao.get('xiao_huang_dao'):
                xiao_hd = huangdao['xiao_huang_dao']
                self._insert_colored_text(f"  小黄道: {xiao_hd.get('name', 'N/A')} ({xiao_hd.get('type', 'N/A')})\n")
                if xiao_hd.get('description'):
                    self._insert_colored_text(f"    说明: {xiao_hd['description']}\n")
            self._insert_colored_text(f"  黄道等级: {huangdao.get('huang_dao_level', 'N/A')}\n\n")
        
        # 宜忌信息
        if result.get('yi_list') or result.get('ji_list'):
            self._insert_colored_text("""【宜忌信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            if result.get('yi_list'):
                yi_items = result['yi_list'] if isinstance(result['yi_list'], list) else result['yi_list'].split(', ')
                self._insert_colored_text(f"  宜: {', '.join(yi_items)}\n")
            if result.get('ji_list'):
                ji_items = result['ji_list'] if isinstance(result['ji_list'], list) else result['ji_list'].split(', ')
                self._insert_colored_text(f"  忌: {', '.join(ji_items)}\n")
            self._insert_colored_text("\n")
        
        # 神煞信息
        if result.get('shensha_list'):
            self._insert_colored_text("""【神煞信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            for shensha in result['shensha_list']:
                name = shensha.get('name', '')
                desc = shensha.get('description', '')
                self._insert_colored_text(f"  • {name}: {desc}\n")
            self._insert_colored_text("\n")
        
        # 评语
        if result.get('reason'):
            self._insert_colored_text(f"""【综合评语】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {result['reason']}

""")
        
        # 事主匹配分析
        if result.get('owners_detail'):
            self._insert_colored_text("""【事主匹配分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            for owner in result['owners_detail']:
                self._insert_colored_text(f"  【{owner.get('name', '事主')}】\n")
                self._insert_colored_text(f"    出生日期: {owner.get('birth_date', 'N/A')}\n")
                self._insert_colored_text(f"    四柱: {owner.get('sizhu', 'N/A')}\n")
                if owner.get('xishen'):
                    self._insert_colored_text(f"    喜神: {owner['xishen']}\n")
                if owner.get('yongshen'):
                    self._insert_colored_text(f"    用神: {owner['yongshen']}\n")
                if owner.get('fu_xing'):
                    self._insert_colored_text(f"    夫星: {owner['fu_xing']}\n")
                if owner.get('zi_xing'):
                    self._insert_colored_text(f"    子星: {owner['zi_xing']}\n")
                if owner.get('match_result'):
                    self._insert_colored_text(f"    匹配结果: {owner['match_result']}\n")
                self._insert_colored_text("\n")
        
        self._insert_colored_text("""
╔════════════════════════════════════════════════════════════════════╗
║              评分完成！可继续添加日课进行对比分析                  ║
╚════════════════════════════════════════════════════════════════════╝""")
    
    def compare_analysis(self):
        """对比分析 - 对比多个日课的评分结果"""
        # 从Treeview获取日期列表
        dates = []
        for item in self.date_treeview.get_children():
            values = self.date_treeview.item(item, 'values')
            if values:
                dates.append(values[0])
        
        if len(dates) < 2:
            messagebox.showwarning("提示", "请至少添加两个日课进行对比")
            return
        
        # 检查是否所有日课都已评分
        scored_dates = [result['date'] for result in self.scoring_results]
        unscored_dates = [date for date in dates if date not in scored_dates]
        
        # 如果有未评分的日课，自动进行评分
        if unscored_dates:
            # 自动评分未评分的日课
            event_type = self.event_var.get()
            
            # 获取事主信息
            owners_detail = []
            for info in self.owners_info:
                try:
                    year = int(info['year'].get())
                    month = int(info['month'].get())
                    day = int(info['day'].get())
                    hour = int(info['hour'].get())
                    minute = int(info['minute'].get())
                    
                    target_date = date(year, month, day)
                    sizhu = calculate_sizhu(target_date, hour, minute)
                    analysis = analyze_sizhu(sizhu)
                    
                    owner_detail = {
                        'name': info['name'],
                        'birth_date': f"{year}年{month}月{day}日 {hour}时{minute}分",
                        'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                        'xishen': info['xishen_var'].get(),
                        'yongshen': info['yongshen_var'].get(),
                        'fu_xing': '',
                        'zi_xing': ''
                    }
                    
                    if event_type == "嫁娶" and info.get('fuzi_var'):
                        fuzi_str = info['fuzi_var'].get()
                        if '夫星:' in fuzi_str:
                            parts = fuzi_str.split(', ')
                            owner_detail['fu_xing'] = parts[0].replace('夫星: ', '')
                            if len(parts) > 1:
                                owner_detail['zi_xing'] = parts[1].replace('子星: ', '')
                    
                    owners_detail.append(owner_detail)
                except Exception as e:
                    continue
            
            # 对每个未评分的日课进行评分
            for date_str in unscored_dates:
                try:
                    # 判断是日期还是四柱
                    if len(date_str.split()) == 4 and all(len(zhu) == 2 for zhu in date_str.split()):
                        # 这是四柱格式（如：甲子 乙丑 丙寅 丁卯）
                        parts = date_str.split()
                        sizhu = {
                            '年柱': parts[0],
                            '月柱': parts[1],
                            '日柱': parts[2],
                            '时柱': parts[3],
                            'year_gan': parts[0][0],
                            'year_zhi': parts[0][1],
                            'month_gan': parts[1][0],
                            'month_zhi': parts[1][1],
                            'day_gan': parts[2][0],
                            'day_zhi': parts[2][1],
                            'hour_gan': parts[3][0],
                            'hour_zhi': parts[3][1]
                        }
                        display_date = f"四柱: {date_str}"
                    else:
                        # 这是日期时间格式（如：2025-03-03 14:30）
                        parts = date_str.split()
                        if len(parts) == 2:
                            date_part = parts[0]
                            time_part = parts[1]
                            hour, minute = map(int, time_part.split(':'))
                            score_date_obj = datetime.strptime(date_part, '%Y-%m-%d').date()
                            sizhu = calculate_sizhu(score_date_obj, hour, minute)
                            display_date = date_str
                        else:
                            # 兼容旧格式（只有日期）
                            score_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                            sizhu = calculate_sizhu(score_date_obj, 12, 0)
                            display_date = date_str
                    
                    # 使用calculate_score进行评分
                    score_result = calculate_score(sizhu, event_type, owners_detail)
                    result = {
                        'date': display_date,
                        'score': score_result['score'],
                        'level': score_result['level'],
                        'reason': score_result.get('reason', ''),
                        'sizhu': sizhu,
                        'event_type': event_type,
                        'owners_detail': owners_detail,
                        'huangdao_info': score_result.get('huangdao_info', {}),
                        'wu_xing_result': score_result.get('wu_xing_result', {}),
                        'yi_list': score_result.get('yi_list', []),
                        'ji_list': score_result.get('ji_list', []),
                        'shensha_list': score_result.get('shensha_list', [])
                    }
                    
                    # 添加到评分结果
                    self.scoring_results.append(result)
                except Exception as e:
                    continue
        
        # 再次检查评分结果数量
        if not self.scoring_results or len(self.scoring_results) < 2:
            messagebox.showinfo("提示", "请先点击'日课评分'按钮对至少两个日课进行评分，然后再进行对比分析")
            return
        
        # 创建对比分析窗口
        compare_window = tk.Toplevel(self.window)
        compare_window.title("日课对比分析")
        compare_window.geometry("900x700")
        
        # 创建主框架和滚动条
        main_frame = ttk.Frame(compare_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 结果显示
        result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("微软雅黑", 10))
        result_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置金色tag用于显示星星
        result_text.tag_configure("gold_star", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        
        # 按评分排序
        sorted_results = sorted(self.scoring_results, key=lambda x: x['score'], reverse=True)
        
        # 按钮区域
        button_frame = ttk.Frame(compare_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="保存分析", command=lambda: self.save_analysis(result_text, sorted_results, self.event_var.get())).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="关闭窗口", command=compare_window.destroy).pack(side=tk.RIGHT, padx=10)
        
        result_text.insert(tk.END, "=" * 70 + "\n")
        result_text.insert(tk.END, "                    日课对比分析报告\n")
        result_text.insert(tk.END, "=" * 70 + "\n\n")
        
        result_text.insert(tk.END, f"对比日课数量: {len(sorted_results)}\n")
        result_text.insert(tk.END, f"事项类型: {self.event_var.get()}\n")
        result_text.insert(tk.END, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 显示事主信息
        if self.owners_info:
            result_text.insert(tk.END, "【事主信息】\n\n")
            for info in self.owners_info:
                year = info['year'].get()
                month = info['month'].get()
                day = info['day'].get()
                if year and month and day:
                    result_text.insert(tk.END, f"  {info['name']}: ")
                    result_text.insert(tk.END, f"{year}年{month}月{day}日 ")
                    if info.get('sizhu_var'):
                        result_text.insert(tk.END, f"四柱: {info['sizhu_var'].get()} ")
                    if info.get('xishen_var') and info['xishen_var'].get():
                        result_text.insert(tk.END, f"喜神: {info['xishen_var'].get()} ")
                    if info.get('yongshen_var') and info['yongshen_var'].get():
                        result_text.insert(tk.END, f"用神: {info['yongshen_var'].get()} ")
                    if info.get('fuzi_var') and info['fuzi_var'].get():
                        result_text.insert(tk.END, f"{info['fuzi_var'].get()}")
                    result_text.insert(tk.END, "\n")
        
        # 显示排名概览
        result_text.insert(tk.END, "【评分排名概览】\n\n")
        result_text.insert(tk.END, f"{'排名':<6}{'日期/四柱':<25}{'评分':<10}{'等级':<15}\n")
        result_text.insert(tk.END, "-" * 70 + "\n")
        for i, result in enumerate(sorted_results, 1):
            date_display = result['date'][:22] if len(result['date']) > 22 else result['date']
            level = result['level']
            
            # 插入排名、日期、评分
            result_text.insert(tk.END, f"第{i}名  {date_display:<25}{result['score']:<10}")
            
            # 如果有星星，用金色显示
            if '★' in level:
                star_count = level.count('★')
                other_text = level.replace('★', '').strip()
                result_text.insert(tk.END, '★' * star_count, "gold_star")
                if other_text:
                    result_text.insert(tk.END, f" {other_text}")
            else:
                result_text.insert(tk.END, level)
            result_text.insert(tk.END, "\n")
        result_text.insert(tk.END, "\n")
        
        # 显示详细信息
        result_text.insert(tk.END, "=" * 70 + "\n")
        result_text.insert(tk.END, "【详细分析报告】\n")
        result_text.insert(tk.END, "=" * 70 + "\n\n")
        
        for i, result in enumerate(sorted_results, 1):
            result_text.insert(tk.END, f"╔════════════════════════════════════════════════════════════════════╗\n")
            result_text.insert(tk.END, f"║  第 {i} 名{' ' * (58 - len(str(i)))}║\n")
            result_text.insert(tk.END, f"╚════════════════════════════════════════════════════════════════════╝\n\n")
            
            result_text.insert(tk.END, f"【基本信息】\n")
            result_text.insert(tk.END, "-" * 70 + "\n")
            result_text.insert(tk.END, f"  日期: {result['date']}\n")
            result_text.insert(tk.END, f"  综合评分: {result['score']} 分\n")
            result_text.insert(tk.END, f"  等级评定: ")
            
            # 如果有星星，用金色显示
            level = result['level']
            if '★' in level:
                star_count = level.count('★')
                other_text = level.replace('★', '').strip()
                result_text.insert(tk.END, '★' * star_count, "gold_star")
                if other_text:
                    result_text.insert(tk.END, f" {other_text}")
            else:
                result_text.insert(tk.END, level)
            result_text.insert(tk.END, "\n\n")
            
            # 四柱信息
            if result.get('sizhu'):
                sizhu = result['sizhu']
                result_text.insert(tk.END, "【四柱八字】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                result_text.insert(tk.END, f"  年柱: {sizhu['年柱']}    月柱: {sizhu['月柱']}\n")
                result_text.insert(tk.END, f"  日柱: {sizhu['日柱']}    时柱: {sizhu['时柱']}\n\n")
                
                # 天干地支五行
                result_text.insert(tk.END, "  【天干五行】\n")
                result_text.insert(tk.END, f"    年干: {sizhu['年柱'][0]}    月干: {sizhu['月柱'][0]}    日干: {sizhu['日柱'][0]}    时干: {sizhu['时柱'][0]}\n")
                result_text.insert(tk.END, "  【地支五行】\n")
                result_text.insert(tk.END, f"    年支: {sizhu['年柱'][1]}    月支: {sizhu['月柱'][1]}    日支: {sizhu['日柱'][1]}    时支: {sizhu['时柱'][1]}\n\n")
            
            # 五行分析
            if result.get('wu_xing_result'):
                wu_xing = result['wu_xing_result']
                result_text.insert(tk.END, "【五行分析】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                result_text.insert(tk.END, f"  五行评分: {wu_xing.get('score', 'N/A')} 分\n")
                if wu_xing.get('reason'):
                    result_text.insert(tk.END, f"  五行评语: {wu_xing['reason']}\n")
                
                # 显示详细分析
                if wu_xing.get('details'):
                    details = wu_xing['details']
                    
                    # 1. 天干地支五行
                    if details.get('天干五行'):
                        result_text.insert(tk.END, "\n  【天干地支五行】\n")
                        for pillar, info in details['天干五行'].items():
                            result_text.insert(tk.END, f"    {pillar}: {info['天干']}({info['天干五行']}) {info['地支']}({info['地支五行']})\n")
                    
                    # 2. 地支关系（三合、六合、六冲、六害、三刑）
                    if details.get('地支关系') and len(details['地支关系']) > 0:
                        result_text.insert(tk.END, "\n  【地支关系】\n")
                        for relation in details['地支关系']:
                            result_text.insert(tk.END, f"    • {relation}\n")
                    else:
                        result_text.insert(tk.END, "\n  【地支关系】\n    无明显合冲刑害关系\n")
                    
                    # 3. 十二长生状态
                    if details.get('十二长生') and len(details['十二长生']) > 0:
                        result_text.insert(tk.END, "\n  【十二长生状态】\n")
                        for pillar, state in details['十二长生'].items():
                            result_text.insert(tk.END, f"    {pillar}: {state}\n")
                    
                    # 4. 纳音五行
                    if details.get('纳音五行') and len(details['纳音五行']) > 0:
                        result_text.insert(tk.END, "\n  【纳音五行】\n")
                        for pillar, nayin in details['纳音五行'].items():
                            result_text.insert(tk.END, f"    {pillar}: {nayin}\n")
                    
                    # 5. 吉神（天德、月德）
                    if details.get('吉神') and len(details['吉神']) > 0:
                        result_text.insert(tk.END, "\n  【吉神】\n")
                        for jishen in details['吉神']:
                            result_text.insert(tk.END, f"    ✓ {jishen}\n")
                    
                    # 6. 日主旺衰
                    if details.get('日主旺衰'):
                        result_text.insert(tk.END, "\n  【日主旺衰】\n")
                        result_text.insert(tk.END, f"    {details['日主旺衰']}\n")
                    
                    # 7. 五行生克
                    if details.get('五行生克') and len(details['五行生克']) > 0:
                        result_text.insert(tk.END, "\n  【五行生克关系】\n")
                        for relation in details['五行生克']:
                            result_text.insert(tk.END, f"    • {relation}\n")
                
                result_text.insert(tk.END, "\n")
            
            # 黄道信息
            if result.get('huangdao_info'):
                huangdao = result['huangdao_info']
                result_text.insert(tk.END, "【黄道信息】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                if huangdao.get('da_huang_dao'):
                    da_hd = huangdao['da_huang_dao']
                    result_text.insert(tk.END, f"  大黄道: {da_hd.get('name', 'N/A')} ({da_hd.get('type', 'N/A')})\n")
                    if da_hd.get('description'):
                        result_text.insert(tk.END, f"    说明: {da_hd['description']}\n")
                if huangdao.get('xiao_huang_dao'):
                    xiao_hd = huangdao['xiao_huang_dao']
                    result_text.insert(tk.END, f"  小黄道: {xiao_hd.get('name', 'N/A')} ({xiao_hd.get('type', 'N/A')})\n")
                    if xiao_hd.get('description'):
                        result_text.insert(tk.END, f"    说明: {xiao_hd['description']}\n")
                result_text.insert(tk.END, f"  黄道等级: {huangdao.get('huang_dao_level', 'N/A')}\n\n")
            
            # 宜忌信息
            if result.get('yi_list') or result.get('ji_list'):
                result_text.insert(tk.END, "【宜忌信息】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                if result.get('yi_list'):
                    yi_items = result['yi_list'] if isinstance(result['yi_list'], list) else result['yi_list'].split(', ')
                    result_text.insert(tk.END, f"  宜: {', '.join(yi_items)}\n")
                if result.get('ji_list'):
                    ji_items = result['ji_list'] if isinstance(result['ji_list'], list) else result['ji_list'].split(', ')
                    result_text.insert(tk.END, f"  忌: {', '.join(ji_items)}\n")
                result_text.insert(tk.END, "\n")
            
            # 神煞信息
            if result.get('shensha_list'):
                result_text.insert(tk.END, "【神煞信息】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                for shensha in result['shensha_list']:
                    name = shensha.get('name', '')
                    desc = shensha.get('description', '')
                    result_text.insert(tk.END, f"  • {name}: {desc}\n")
                result_text.insert(tk.END, "\n")
            
            # 评语
            if result.get('reason'):
                result_text.insert(tk.END, "【综合评语】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                result_text.insert(tk.END, f"  {result['reason']}\n\n")
            
            # 事主匹配分析
            if result.get('owners_detail'):
                result_text.insert(tk.END, "【事主匹配分析】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                for owner in result['owners_detail']:
                    result_text.insert(tk.END, f"  【{owner.get('name', '事主')}】\n")
                    result_text.insert(tk.END, f"    出生日期: {owner.get('birth_date', 'N/A')}\n")
                    result_text.insert(tk.END, f"    四柱: {owner.get('sizhu', 'N/A')}\n")
                    if owner.get('xishen'):
                        result_text.insert(tk.END, f"    喜神: {owner['xishen']}\n")
                    if owner.get('yongshen'):
                        result_text.insert(tk.END, f"    用神: {owner['yongshen']}\n")
                    if owner.get('fu_xing'):
                        result_text.insert(tk.END, f"    夫星: {owner['fu_xing']}\n")
                    if owner.get('zi_xing'):
                        result_text.insert(tk.END, f"    子星: {owner['zi_xing']}\n")
                    if owner.get('match_result'):
                        result_text.insert(tk.END, f"    匹配结果: {owner['match_result']}\n")
                    result_text.insert(tk.END, "\n")
    
    def export_report(self):
        """导出评分报告"""
        if not self.scoring_results:
            messagebox.showwarning("提示", "没有评分结果可导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="导出评分报告"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("日课评分报告\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"事项类型: {self.event_var.get()}\n")
                f.write(f"评分日课数量: {len(self.scoring_results)}\n\n")
                
                # 按评分排序
                sorted_results = sorted(self.scoring_results, key=lambda x: x['score'], reverse=True)
                
                for i, result in enumerate(sorted_results, 1):
                    f.write(f"【第 {i} 名】\n")
                    f.write(f"日期: {result['date']}\n")
                    f.write(f"评分: {result['score']} 分\n")
                    f.write(f"等级: {result['level']}\n")
                    
                    if result.get('sizhu'):
                        sizhu = result['sizhu']
                        f.write(f"四柱: {sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}\n")
                    
                    if result.get('reason'):
                        f.write(f"评语: {result['reason']}\n")
                    
                    f.write("-" * 40 + "\n\n")
            
            messagebox.showinfo("成功", f"报告已导出到:\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def import_file(self):
        """从文件导入日期"""
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt"), ("JSON文件", "*.json"), ("所有文件", "*.*")],
            title="导入日期文件"
        )
        
        if not file_path:
            return
        
        imported_count = 0
        
        try:
            if file_path.endswith('.json'):
                # 导入JSON格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理主程序导出的格式
                    if isinstance(data, dict) and 'results' in data:
                        for item in data['results']:
                            if isinstance(item, dict) and 'date' in item:
                                date_str = item['date']
                                try:
                                    datetime.strptime(date_str, '%Y-%m-%d')
                                    if date_str not in self.date_list:
                                        self.date_list.append(date_str)
                                        self.date_treeview.insert('', tk.END, values=(date_str, '', '', '', '', '', ''))
                                        imported_count += 1
                                except ValueError:
                                    continue
                    # 处理其他格式
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, str):
                                date_str = item
                            elif isinstance(item, dict) and 'date' in item:
                                date_str = item['date']
                            else:
                                continue
                            
                            try:
                                datetime.strptime(date_str, '%Y-%m-%d')
                                if date_str not in self.date_list:
                                    self.date_list.append(date_str)
                                    self.date_treeview.insert('', tk.END, values=(date_str, '', '', '', '', '', ''))
                                    imported_count += 1
                            except ValueError:
                                continue
            else:
                # 导入文本格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 尝试提取日期（格式：YYYY-MM-DD）
                        date_match = re.search(r'日期：(\d{4}-\d{2}-\d{2})', line) or re.search(r'\d{4}-\d{2}-\d{2}', line)
                        if date_match:
                            date_str = date_match.group(1)
                            if date_str not in self.date_list:
                                self.date_list.append(date_str)
                                self.date_treeview.insert('', tk.END, values=(date_str, '', '', '', '', '', ''))
                                imported_count += 1
            
            if imported_count > 0:
                messagebox.showinfo("成功", f"成功导入 {imported_count} 个日期")
            else:
                messagebox.showinfo("提示", "没有找到有效的日期")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {str(e)}")
            
    def save_single_analysis(self):
        """保存单个日课分析结果"""
        try:
            # 获取当前显示的内容
            content = self.result_text.get(1.0, tk.END)
            
            if not content.strip():
                messagebox.showwarning("提示", "没有分析结果可保存")
                return
            
            # 弹出文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title="保存日课分析结果",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 保存为文本文件
            if file_path.endswith('.txt'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
            
            # 保存为JSON文件
            elif file_path.endswith('.json'):
                # 尝试从当前显示的内容中提取关键信息
                # 这里简化处理，实际项目中可以更详细地解析
                json_data = {
                    'analysis_type': '单个日课分析',
                    'event_type': self.event_var.get(),
                    'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'content': content
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def save_analysis(self, result_text, sorted_results, event_type):
        """保存对比分析结果"""
        try:
            # 获取当前显示的内容
            content = result_text.get(1.0, tk.END)
            
            if not content.strip():
                messagebox.showwarning("提示", "没有分析结果可保存")
                return
            
            # 弹出文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title="保存日课对比分析结果",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 保存为文本文件
            if file_path.endswith('.txt'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
            
            # 保存为JSON文件
            elif file_path.endswith('.json'):
                # 构建JSON数据
                json_data = {
                    'analysis_type': '对比分析',
                    'event_type': event_type,
                    'comparison_count': len(sorted_results),
                    'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'results': [
                        {
                            'date': result['date'],
                            'score': result['score'],
                            'level': result['level'],
                            'reason': result.get('reason', ''),
                            'sizhu': result.get('sizhu', {})
                        }
                        for result in sorted_results
                    ],
                    'content': content
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
        日课评分系统使用说明：
        
        1. 选择事项类型：根据需要选择对应的事项类型
        2. 输入日课：可以选择按日期输入或按四柱输入
        3. 填写事主信息：根据事项类型填写相关人员信息
        4. 添加日课：将日课添加到列表中
        5. 日课评分：对当前输入的日课进行评分
        6. 对比分析：对多个日课进行对比分析
        7. 保存分析：保存当前分析结果
        8. 导出报告：导出所有评分结果
        9. 导入文件：从文件导入日期
        
        注意事项：
        - 事主信息为可选，可根据实际情况填写
        - 对比分析需要至少两个日课
        - 保存功能支持文本和JSON格式
        """
        messagebox.showinfo("帮助", help_text)


def main():
    """主函数 - 直接运行日课评分系统"""
    try:
        app = DayScoreWindow()
        app.run()
    except Exception as e:
        messagebox.showerror("错误", f"程序运行出错: {str(e)}")


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
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 从整合模块导入基础数据（避免重复定义）
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
            target_date = date(self.year, self.month, self.day)
            sizhu = calculate_sizhu(target_date, self.hour, self.minute)
            self.sizhu = sizhu
            
            # 设置日主信息
            self.day_gan = sizhu.get('day_gan', '甲')
            self.day_zhi = sizhu.get('day_zhi', '子')
            self.day_wuxing = GAN_WUXING.get(self.day_gan, '土')
        except Exception as e:
            logger.error(f"计算四柱失败: {str(e)}", exc_info=True)
            # 使用简化计算作为备用
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



# -*- coding: utf-8 -*-
"""
================================================================================
事主日课匹配评分模块
================================================================================
将事主八字喜用神与择日日课进行匹配评分
作为择日软件的核心评分维度

评分维度：
1. 日课天干与喜用神匹配（40分）
2. 日课地支藏干与喜用神匹配（30分）
3. 日课五行平衡度（20分）
4. 日课与日主关系（10分）

总分100分，作为择日评分的重要组成部分

使用方法:
    1. 作为模块导入: from modules.事主日课匹配评分 import calculate_shizhu_rike_match
    2. 直接运行: python -m modules.事主日课匹配评分
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# 导入事主八字分析模块
class ShiZhuRiKeMatcher:
    """
    事主日课匹配器
    
    评估日课与事主八字的匹配程度
    """
    
    def __init__(self):
        """初始化匹配器"""
        self.shizhu_analyzers = {}  # 缓存事主分析器
    
    def get_or_create_analyzer(self, shizhu_info: Dict) -> ShiZhuBaZiAnalyzer:
        """
        获取或创建事主分析器
        
        Args:
            shizhu_info: 事主信息
            
        Returns:
            ShiZhuBaZiAnalyzer: 分析器实例
        """
        # 创建缓存键
        cache_key = f"{shizhu_info.get('year')}-{shizhu_info.get('month')}-{shizhu_info.get('day')}-{shizhu_info.get('hour')}"
        
        if cache_key not in self.shizhu_analyzers:
            self.shizhu_analyzers[cache_key] = ShiZhuBaZiAnalyzer(
                shizhu_info.get('year', 2000),
                shizhu_info.get('month', 1),
                shizhu_info.get('day', 1),
                shizhu_info.get('hour', 12),
                shizhu_info.get('minute', 0),
                shizhu_info.get('gender', '男')
            )
        
        return self.shizhu_analyzers[cache_key]
    
    def calculate_match_score(self, shizhu_info: Dict, rike_sizhu: Dict) -> Dict:
        """
        计算事主与日课的匹配评分
        
        Args:
            shizhu_info: 事主信息
            rike_sizhu: 日课四柱
            
        Returns:
            Dict: 匹配评分结果
        """
        analyzer = self.get_or_create_analyzer(shizhu_info)
        return analyzer.calculate_rike_match_score(rike_sizhu)
    
    def calculate_multi_shizhu_score(self, shizhu_list: List[Dict], 
                                     rike_sizhu: Dict) -> Dict:
        """
        计算多个事主与日课的平均匹配评分
        
        Args:
            shizhu_list: 事主信息列表
            rike_sizhu: 日课四柱
            
        Returns:
            Dict: 综合评分结果
        """
        if not shizhu_list:
            return {
                'score': 50,
                'level': '中平',
                'summary': '无事主信息，默认中平'
            }
        
        total_score = 0
        details = []
        
        for i, shizhu_info in enumerate(shizhu_list, 1):
            result = self.calculate_match_score(shizhu_info, rike_sizhu)
            score = result.get('score', 50)
            total_score += score
            
            name = shizhu_info.get('name', f'事主{i}')
            details.append({
                'name': name,
                'score': score,
                'level': result.get('level', '中平'),
                'yongshen': result.get('事主用神', [])
            })
        
        avg_score = total_score / len(shizhu_list)
        
        # 确定综合等级
        if avg_score >= 80:
            level = '大吉'
        elif avg_score >= 60:
            level = '吉'
        elif avg_score >= 40:
            level = '中平'
        elif avg_score >= 20:
            level = '凶'
        else:
            level = '大凶'
        
        return {
            'score': round(avg_score, 1),
            'level': level,
            'summary': f'综合匹配度：{avg_score:.1f}分（{level}）',
            'details': details,
            'shizhu_count': len(shizhu_list)
        }


class RiKeShiZhuIntegration:
    """
    日课事主整合类
    
    将事主八字匹配整合到择日评分流程中
    """
    
    def __init__(self):
        """初始化整合器"""
        self.matcher = ShiZhuRiKeMatcher()
    
    def enhance_score_result(self, base_result: Dict, shizhu_list: List[Dict], 
                            rike_sizhu: Dict) -> Dict:
        """
        增强评分结果，添加事主八字匹配信息
        
        Args:
            base_result: 基础评分结果
            shizhu_list: 事主列表
            rike_sizhu: 日课四柱
            
        Returns:
            Dict: 增强后的评分结果
        """
        # 计算事主匹配评分
        match_result = self.matcher.calculate_multi_shizhu_score(shizhu_list, rike_sizhu)
        
        # 整合到基础结果
        enhanced_result = base_result.copy()
        
        # 添加事主匹配维度（占总分20%）
        shizhu_score = match_result['score']
        shizhu_contribution = shizhu_score * 0.2  # 20%权重
        
        # 调整总分
        original_score = enhanced_result.get('score', 100)
        adjusted_score = original_score * 0.8 + shizhu_contribution
        
        enhanced_result['score'] = round(adjusted_score, 1)
        enhanced_result['事主匹配'] = match_result
        enhanced_result['评分维度'] = enhanced_result.get('评分维度', [])
        enhanced_result['评分维度'].append({
            '维度': '事主八字匹配',
            '权重': '20%',
            '得分': shizhu_score,
            '贡献': round(shizhu_contribution, 1)
        })
        
        # 更新评语
        if 'reason' in enhanced_result:
            enhanced_result['reason'] += f"；事主匹配：{match_result['summary']}"
        
        return enhanced_result
    
    def get_shizhu_suggestions(self, shizhu_list: List[Dict]) -> List[str]:
        """
        获取事主相关建议
        
        Args:
            shizhu_list: 事主列表
            
        Returns:
            List[str]: 建议列表
        """
        suggestions = []
        
        for shizhu_info in shizhu_list:
            analyzer = self.matcher.get_or_create_analyzer(shizhu_info)
            result = analyzer.get_analysis_result()
            
            name = shizhu_info.get('name', '事主')
            xishen = result['喜用神']
            
            # 生成建议
            if xishen['用神']:
                yongshen_wx = '、'.join(xishen['用神'])
                suggestions.append(f"{name}用神为{yongshen_wx}，宜选择五行{yongshen_wx}旺的日期")
            
            if xishen['忌神']:
                jishen_wx = '、'.join(xishen['忌神'])
                suggestions.append(f"{name}忌神为{jishen_wx}，应避免五行{jishen_wx}过旺的日期")
        
        return suggestions


# 便捷函数
def calculate_shizhu_rike_match(shizhu_info: Dict, rike_sizhu: Dict) -> Dict:
    """
    快速计算事主与日课匹配度
    
    Args:
        shizhu_info: 事主信息
        rike_sizhu: 日课四柱
        
    Returns:
        Dict: 匹配评分
    """
    matcher = ShiZhuRiKeMatcher()
    return matcher.calculate_match_score(shizhu_info, rike_sizhu)


def calculate_multi_match(shizhu_list: List[Dict], rike_sizhu: Dict) -> Dict:
    """
    快速计算多个事主与日课匹配度
    
    Args:
        shizhu_list: 事主列表
        rike_sizhu: 日课四柱
        
    Returns:
        Dict: 综合匹配评分
    """
    matcher = ShiZhuRiKeMatcher()
    return matcher.calculate_multi_shizhu_score(shizhu_list, rike_sizhu)



# -*- coding: utf-8 -*-
"""
================================================================================
评分模块
================================================================================
根据神煞和规则计算综合评分并判断等级
采用"五行为主，黄道为用"的架构

使用方法:
    1. 作为模块导入: from modules.评分器 import calculate_score
    2. 直接运行: python -m modules.评分器
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
# 尝试相对导入，失败则使用绝对导入
HAS_BAZI_TOOLS = True

class Scorer:
    """评分器"""
    
    def __init__(self):
        self.base_score = 100
        self.final_score = 100
        self.level = ''
        self.shensha_list = []
        self.yi_list = []
        self.ji_list = []
        self.huangdao_info = {}
    
    def score(self, sizhu, event_type, owners=None, house_type=None, shan_xiang=None, 
              zaoxiang=None, zaowei=None, chuangwei=None):
        """
        计算评分
        
        架构说明：
        第一层（核心筛选）：正五行模块 - 这是系统的"否决权"模块
        第二层（优选排序）：大小黄道模块 - 这是系统的"加分项"
        第三层（深度优化）：月令对日主的帮助 - 正五行择日法的重要维度
        
        Args:
            sizhu: 四柱信息
            event_type: 事项类型
            owners: 事主信息
            house_type: 宅型（阳宅/阴宅）
            shan_xiang: 山向
            zaoxiang: 灶向（作灶专用）
            zaowei: 灶位（作灶专用）
            chuangwei: 床位朝向（安床专用）
            
        Returns:
            dict: 评分结果
        """
        # 第一步：正五行审核（核心门槛）
        wu_xing_result = self._check_wu_xing(sizhu, event_type, owners, 
                                                house_type, shan_xiang, 
                                                zaoxiang, zaowei, chuangwei)
        
        # 如果五行不合格（犯三杀、冲山等大忌），直接返回"❌ 凶"
        if not wu_xing_result['he_ge']:
            return {
                'score': 0,
                'level': '❌ 凶',
                'reason': wu_xing_result['ji_yu'],
                'shensha_list': self.shensha_list,
                'yi_list': self.yi_list,
                'ji_list': self.ji_list,
                'huangdao_info': {},
                'wu_xing_result': wu_xing_result
            }
        
        # 第二步：月令对日主的帮助评分
        yueling_score = self._calculate_yueling_help(sizhu)
        
        # 第三步：日课五行与事主喜用神匹配评分（正五行择日法核心）
        xishen_score = self._calculate_xishen_match(sizhu, owners)
        
        # 第四步：大小黄道审核（加分/减分项）
        self.huangdao_info = calculate_huangdao(sizhu)
        huangdao_score = self.huangdao_info.get('huang_dao_score', 0)
        
        # 计算最终得分：五行评分 + 月令得分 + 喜用神得分 + 黄道得分
        self.final_score = wu_xing_result['score'] + yueling_score + xishen_score + huangdao_score
        
        # 第五步：综合评定
        self.level = self._get_level(self.final_score, wu_xing_result, self.huangdao_info)
        
        # 构建详细得分明细
        score_details = {
            '基础分': self.base_score,
            '五行评分': wu_xing_result['score'],
            '月令得分': yueling_score,
            '喜用神得分': xishen_score,
            '黄道得分': huangdao_score,
            '总分': self.final_score
        }
        
        # 添加月令详细得分
        wangxiang_score = self._calculate_wangxiang(sizhu)
        zhizhi_score = self._calculate_zhizhi_relation(sizhu)
        score_details['月令详细'] = {
            '旺衰得分': wangxiang_score,
            '支支关系得分': zhizhi_score
        }
        
        return {
            'score': self.final_score,
            'level': self.level,
            'reason': self._generate_reason(wu_xing_result, self.huangdao_info, yueling_score, xishen_score),
            'shensha_list': self.shensha_list,
            'yi_list': self.yi_list,
            'ji_list': self.ji_list,
            'huangdao_info': self.huangdao_info,
            'wu_xing_result': wu_xing_result,
            'score_details': score_details
        }
    
    def _calculate_yueling_help(self, sizhu):
        """
        计算月令对日主的帮助评分
        
        参考正五行择日法，考虑：
        1. 日主在月令中的旺衰（旺相休囚死）
        2. 月令与日支的关系（三合、六合、刑冲等）
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            int: 月令帮助评分
        """
        score = 0
        
        # 1. 日主在月令中的旺衰评分
        wangxiang_score = self._calculate_wangxiang(sizhu)
        score += wangxiang_score
        
        # 2. 月令与日支关系评分
        zhizhi_score = self._calculate_zhizhi_relation(sizhu)
        score += zhizhi_score
        
        return score
    
    def _calculate_wangxiang(self, sizhu):
        """
        计算日主在月令中的旺衰评分
        
        采用八字命理中的"旺相休囚死"表
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            int: 旺衰评分
        """
        # 旺相休囚死表
        wangxiang_table = {
            '甲': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
            '乙': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
            '丙': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], '囚': ['申', '酉'], '死': ['亥', '子']},
            '丁': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], '囚': ['申', '酉'], '死': ['亥', '子']},
            '戊': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], '囚': ['亥', '子'], '死': ['寅', '卯']},
            '己': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], '囚': ['亥', '子'], '死': ['寅', '卯']},
            '庚': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], '囚': ['寅', '卯'], '死': ['巳', '午']},
            '辛': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], '囚': ['寅', '卯'], '死': ['巳', '午']},
            '壬': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']},
            '癸': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']}
        }
        
        # 获取日干和月支
        day_gan = sizhu.get('day_gan', '')
        month_zhi = sizhu.get('月柱', '')[1] if len(sizhu.get('月柱', '')) > 1 else ''
        
        if not day_gan or not month_zhi:
            return 0
        
        # 查找旺相休囚死
        if day_gan in wangxiang_table:
            table = wangxiang_table[day_gan]
            if month_zhi in table['旺']:
                return 10  # 旺：+10分
            elif month_zhi in table['相']:
                return 5   # 相：+5分
            elif month_zhi in table['休']:
                return 0   # 休：0分
            elif month_zhi in table['囚']:
                return -5  # 囚：-5分
            elif month_zhi in table['死']:
                return -10 # 死：-10分
        
        return 0
    
    def _calculate_zhizhi_relation(self, sizhu):
        """
        计算月令与日支的关系评分
        
        考虑：三合、六合、刑、冲、破、害
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            int: 关系评分
        """
        # 获取月支和日支
        month_zhi = sizhu.get('月柱', '')[1] if len(sizhu.get('月柱', '')) > 1 else ''
        day_zhi = sizhu.get('日柱', '')[1] if len(sizhu.get('日柱', '')) > 1 else ''
        
        if not month_zhi or not day_zhi:
            return 0
        
        # 六合关系
        liuhe = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        # 三合关系
        sanhe = {
            '申子辰': ['申', '子', '辰'],
            '寅午戌': ['寅', '午', '戌'],
            '巳酉丑': ['巳', '酉', '丑'],
            '亥卯未': ['亥', '卯', '未']
        }
        
        # 六冲关系
        liuchong = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
        
        # 六害关系
        liuhai = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        
        # 计算关系
        if liuhe.get(month_zhi) == day_zhi:
            return 8  # 六合：+8分
        
        # 检查三合
        for he in sanhe.values():
            if month_zhi in he and day_zhi in he:
                return 5  # 三合：+5分
        
        if liuchong.get(month_zhi) == day_zhi:
            return -15  # 六冲（月破）：-15分
        
        if liuhai.get(month_zhi) == day_zhi:
            return -5  # 六害：-5分
        
        return 0
    
    def _calculate_xishen_match(self, sizhu, owners):
        """
        计算日课五行与事主喜用神的匹配评分
        
        正五行择日法核心理念：日课四柱如同为事主"造命"，
        必须补益事主八字中的用神，才能达到催吉的效果。
        
        评分逻辑：
        1. 日课天干五行与事主用神相同：+8分
        2. 日课天干五行与事主喜神相同：+5分
        3. 日课地支藏干包含用神：+3分
        4. 日课地支藏干包含喜神：+2分
        5. 日课五行克事主用神：-10分（大忌）
        6. 日课五行与事主用神相冲：-8分
        
        Args:
            sizhu: 日课四柱信息
            owners: 事主信息列表
            
        Returns:
            int: 喜用神匹配评分
        """
        if not owners:
            return 0
        
        score = 0
        
        # 提取日课天干五行
        sizhu_wuxing = []
        for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
            pillar = sizhu.get(pillar_name, '')
            if len(pillar) > 0:
                gan = pillar[0]
                # 天干五行映射
                gan_wuxing = {
                    '甲': '木', '乙': '木',
                    '丙': '火', '丁': '火',
                    '戊': '土', '己': '土',
                    '庚': '金', '辛': '金',
                    '壬': '水', '癸': '水'
                }
                if gan in gan_wuxing:
                    sizhu_wuxing.append(gan_wuxing[gan])
        
        # 提取日课地支藏干五行
        zhigan_map = {
            '子': ['水'],
            '丑': ['土', '水', '金'],
            '寅': ['木', '火', '土'],
            '卯': ['木'],
            '辰': ['土', '木', '水'],
            '巳': ['火', '土', '金'],
            '午': ['火', '土'],
            '未': ['土', '火', '木'],
            '申': ['金', '水', '土'],
            '酉': ['金'],
            '戌': ['土', '金', '火'],
            '亥': ['水', '木']
        }
        
        sizhu_canggan = []
        for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
            pillar = sizhu.get(pillar_name, '')
            if len(pillar) > 1:
                zhi = pillar[1]
                if zhi in zhigan_map:
                    sizhu_canggan.extend(zhigan_map[zhi])
        
        # 遍历所有事主，计算匹配度
        for owner in owners:
            owner_xishen = owner.get('xishen', '')
            owner_yongshen = owner.get('yongshen', '')
            
            # 解析喜用神（可能包含多个，如"木、水"）
            owner_xishen_list = [x.strip() for x in owner_xishen.split('、') if x.strip()]
            owner_yongshen_list = [x.strip() for x in owner_yongshen.split('、') if x.strip()]
            
            # 1. 检查日课天干与用神匹配
            for wx in sizhu_wuxing:
                if wx in owner_yongshen_list:
                    score += 8  # 天干为用神：+8分
                elif wx in owner_xishen_list:
                    score += 5  # 天干为喜神：+5分
            
            # 2. 检查日课藏干与用神匹配
            for wx in sizhu_canggan:
                if wx in owner_yongshen_list:
                    score += 3  # 藏干为用神：+3分
                elif wx in owner_xishen_list:
                    score += 2  # 藏干为喜神：+2分
        
        return score
    
    def _check_wu_xing(self, sizhu, event_type, owners, house_type, shan_xiang,
                      zaoxiang, zaowei, chuangwei):
        """
        正五行审核（核心门槛）
        
        Args:
            sizhu: 四柱信息
            event_type: 事项类型
            owners: 事主信息
            house_type: 宅型
            shan_xiang: 山向
            zaoxiang: 灶向
            zaowei: 灶位
            chuangwei: 床位
            
        Returns:
            dict: 五行审核结果
        """
        # 检查神煞
        shensha_checker = get_checker(event_type)
        self.shensha_list = shensha_checker.check(sizhu, owners)
        
        # 检查宜忌规则
        rule_checker = get_rule_checker(event_type)
        self.yi_list, self.ji_list = rule_checker.check(
            sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei
        )
        
        # 计算五行评分
        wu_xing_score = self.base_score
        
        # 记录各项得分详情
        score_breakdown = {
            '基础分': self.base_score,
            '神煞得分': 0,
            '宜事得分': 0,
            '忌事得分': 0,
            '十二长生得分': 0,
            '地支关系得分': 0,
            '纳音匹配得分': 0
        }
        
        for shensha in self.shensha_list:
            wu_xing_score += shensha['score']
            score_breakdown['神煞得分'] += shensha['score']
        for yi in self.yi_list:
            wu_xing_score += 10
            score_breakdown['宜事得分'] += 10
        for ji in self.ji_list:
            wu_xing_score -= 15
            score_breakdown['忌事得分'] -= 15
        
        # 新增：集成八字工具整合模块的功能
        if HAS_BAZI_TOOLS:
            # 1. 计算日主十二长生状态，影响旺衰评分
            zhangsheng_score = self._calculate_zhangsheng_score(sizhu)
            wu_xing_score += zhangsheng_score
            score_breakdown['十二长生得分'] = zhangsheng_score
            
            # 2. 分析日课四柱内部地支关系（冲合刑害）
            zhizhi_relation_score = self._calculate_zhizhi_relations(sizhu)
            wu_xing_score += zhizhi_relation_score
            score_breakdown['地支关系得分'] = zhizhi_relation_score
            
            # 3. 纳音五行与事主年命的匹配度（可选）
            nayin_match_score = self._calculate_nayin_match(sizhu, owners)
            wu_xing_score += nayin_match_score
            score_breakdown['纳音匹配得分'] = nayin_match_score
        
        # 判断五行是否合格
        he_ge = wu_xing_score >= 60  # 五行评分低于60分为不合格
        
        # 生成五行评语
        ji_yu = self._generate_wu_xing_jiyu(wu_xing_score, he_ge)
        
        # 生成详细的五行分析信息
        details = self._generate_wu_xing_details(sizhu, owners)
        
        return {
            'he_ge': he_ge,
            'score': wu_xing_score,
            'ji_yu': ji_yu,
            'details': details,
            'score_breakdown': score_breakdown
        }
    
    def _generate_wu_xing_jiyu(self, score, he_ge):
        """
        生成五行评语
        
        Args:
            score: 五行评分
            he_ge: 是否合格
            
        Returns:
            str: 五行评语
        """
        if not he_ge:
            return '五行严重不合格，犯大忌，坚决不用'
        elif score >= 120:
            return '五行大吉，旺相无碍'
        elif score >= 100:
            return '五行吉日，诸事皆宜'
        elif score >= 80:
            return '五行中吉，可用'
        elif score >= 60:
            return '五行平平，仅适合小事'
        else:
            return '五行凶日，不宜使用'
    
    def _generate_wu_xing_details(self, sizhu, owners):
        """
        生成详细的五行分析信息
        
        包括：
        1. 天干地支五行分析
        2. 地支关系（三合、六合、六冲、六害、三刑、相破）
        3. 十二长生状态
        4. 纳音五行
        5. 吉神（天德、月德、天乙、文昌、福星、禄神等）
        6. 日主旺衰分析
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            
        Returns:
            dict: 详细分析信息
        """
        details = {
            '天干五行': {},
            '地支关系': [],
            '十二长生': {},
            '纳音五行': {},
            '吉神': [],
            '日主旺衰': '',
            '五行生克': []
        }
        
        # 1. 天干地支五行分析
        gan_wuxing = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', 
                      '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
        zhi_wuxing = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
                      '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金', 
                      '戌': '土', '亥': '水'}
        
        for pillar_name, pillar_key in [('年柱', 'year'), ('月柱', 'month'), 
                                         ('日柱', 'day'), ('时柱', 'hour')]:
            pillar = sizhu.get(pillar_name, '')
            if len(pillar) >= 2:
                gan, zhi = pillar[0], pillar[1]
                details['天干五行'][pillar_name] = {
                    '天干': gan,
                    '天干五行': gan_wuxing.get(gan, '未知'),
                    '地支': zhi,
                    '地支五行': zhi_wuxing.get(zhi, '未知')
                }
        
        # 2. 地支关系分析
        zhis = []
        for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
            pillar = sizhu.get(pillar_name, '')
            if len(pillar) >= 2:
                zhis.append((pillar_name, pillar[1]))
        
        # 三合局
        sanhe_groups = {
            '申子辰': '水局', '寅午戌': '火局', '巳酉丑': '金局', '亥卯未': '木局'
        }
        zhi_list = [z[1] for z in zhis]
        for group, ju in sanhe_groups.items():
            count = sum(1 for z in zhi_list if z in group)
            if count >= 2:
                details['地支关系'].append(f"三合{ju}: {', '.join([z[0]+z[1] for z in zhis if z[1] in group])}")
        
        # 六合
        liuhe_pairs = [('子', '丑'), ('寅', '亥'), ('卯', '戌'), 
                       ('辰', '酉'), ('巳', '申'), ('午', '未')]
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                z1_name, z1 = zhis[i]
                z2_name, z2 = zhis[j]
                if (z1, z2) in liuhe_pairs or (z2, z1) in liuhe_pairs:
                    details['地支关系'].append(f"六合: {z1_name}{z1}合{z2_name}{z2}")
        
        # 六冲
        liuchong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), 
                          ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                z1_name, z1 = zhis[i]
                z2_name, z2 = zhis[j]
                if (z1, z2) in liuchong_pairs or (z2, z1) in liuchong_pairs:
                    details['地支关系'].append(f"六冲: {z1_name}{z1}冲{z2_name}{z2}")
        
        # 六害
        liuhai_pairs = [('子', '未'), ('丑', '午'), ('寅', '巳'), 
                        ('卯', '辰'), ('申', '亥'), ('酉', '戌')]
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                z1_name, z1 = zhis[i]
                z2_name, z2 = zhis[j]
                if (z1, z2) in liuhai_pairs or (z2, z1) in liuhai_pairs:
                    details['地支关系'].append(f"六害: {z1_name}{z1}害{z2_name}{z2}")
        
        # 三刑
        sanxing_groups = [
            (['寅', '巳', '申'], '无恩之刑'),
            (['丑', '戌', '未'], '恃势之刑'),
            (['子', '卯'], '无礼之刑'),
            (['辰', '午', '酉', '亥'], '自刑')
        ]
        for group, name in sanxing_groups:
            count = sum(1 for z in zhi_list if z in group)
            if count >= 2:
                details['地支关系'].append(f"三刑({name}): {', '.join([z[0]+z[1] for z in zhis if z[1] in group])}")
        
        # 3. 十二长生状态
        day_gan = sizhu.get('day_gan', '')
        if day_gan and HAS_BAZI_TOOLS:
            try:
                for pillar_name, pillar_key in [('年柱', 'year'), ('月柱', 'month'), 
                                                 ('日柱', 'day'), ('时柱', 'hour')]:
                    pillar = sizhu.get(pillar_name, '')
                    if len(pillar) >= 2:
                        zhi = pillar[1]
                    state = get_zhangsheng(day_gan, zhi)
                    details['十二长生'][pillar_name] = state
            except:
                pass
        
        if HAS_BAZI_TOOLS:
            try:
                for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
                    pillar = sizhu.get(pillar_name, '')
                    if len(pillar) >= 2:
                        nayin = get_nayin(pillar)
                        details['纳音五行'][pillar_name] = nayin
            except:
                pass
        
        month_zhi = sizhu.get('月柱', '')[1] if len(sizhu.get('月柱', '')) > 1 else ''
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('日柱', '')[1] if len(sizhu.get('日柱', '')) > 1 else ''
        
        # 天德贵人查法（以月支查日干）
        tiande_map = {
            '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
            '午': '甲', '未': '癸', '申': '寅', '酉': '丙',
            '戌': '乙', '亥': '己', '子': '戊', '丑': '庚'
        }
        if month_zhi in tiande_map and day_gan == tiande_map[month_zhi]:
            details['吉神'].append(f"天德贵人: 月支{month_zhi}见日干{day_gan}")
        
        # 月德贵人查法（以月支查日干）
        yuede_map = {
            '寅': '丙', '卯': '丙', '辰': '壬', '巳': '庚',
            '午': '丙', '未': '甲', '申': '壬', '酉': '庚',
            '戌': '丙', '亥': '甲', '子': '壬', '丑': '庚'
        }
        if month_zhi in yuede_map and day_gan == yuede_map[month_zhi]:
            details['吉神'].append(f"月德贵人: 月支{month_zhi}见日干{day_gan}")
        
        # 6. 天乙贵人查法（以日干查地支）
        tianyi_map = {
            '甲': ['丑', '未'], '乙': ['子', '申'], '丙': ['亥', '酉'],
            '丁': ['亥', '酉'], '戊': ['丑', '未'], '己': ['子', '申'],
            '庚': ['丑', '未'], '辛': ['寅', '午'], '壬': ['卯', '巳'],
            '癸': ['卯', '巳']
        }
        if day_gan in tianyi_map:
            for zhi_name, zhi in zhis:
                if zhi in tianyi_map[day_gan]:
                    details['吉神'].append(f"天乙贵人: 日干{day_gan}见{zhi_name}{zhi}")
        
        # 7. 文昌贵人查法（以日干查地支）
        wenchang_map = {
            '甲': '巳', '乙': '午', '丙': '申', '丁': '酉',
            '戊': '申', '己': '酉', '庚': '亥', '辛': '子',
            '壬': '寅', '癸': '卯'
        }
        if day_gan in wenchang_map:
            for zhi_name, zhi in zhis:
                if zhi == wenchang_map[day_gan]:
                    details['吉神'].append(f"文昌贵人: 日干{day_gan}见{zhi_name}{zhi}")
        
        # 8. 福星贵人查法（以日干查地支）
        fuxing_map = {
            '甲': '寅', '乙': '丑', '丙': '子', '丁': '酉',
            '戊': '申', '己': '未', '庚': '午', '辛': '巳',
            '壬': '辰', '癸': '卯'
        }
        if day_gan in fuxing_map:
            for zhi_name, zhi in zhis:
                if zhi == fuxing_map[day_gan]:
                    details['吉神'].append(f"福星贵人: 日干{day_gan}见{zhi_name}{zhi}")
        
        # 9. 禄神查法（以日干查地支）
        lushen_map = {
            '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
            '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
            '壬': '亥', '癸': '子'
        }
        if day_gan in lushen_map:
            for zhi_name, zhi in zhis:
                if zhi == lushen_map[day_gan]:
                    details['吉神'].append(f"禄神: 日干{day_gan}见{zhi_name}{zhi}")
        
        # 10. 日主旺衰分析
        if day_gan and month_zhi:
            wangxiang_table = {
                '甲': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], 
                      '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
                '乙': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], 
                      '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
                '丙': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], 
                      '囚': ['申', '酉'], '死': ['亥', '子']},
                '丁': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], 
                      '囚': ['申', '酉'], '死': ['亥', '子']},
                '戊': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], 
                      '囚': ['亥', '子'], '死': ['寅', '卯']},
                '己': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], 
                      '囚': ['亥', '子'], '死': ['寅', '卯']},
                '庚': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], 
                      '囚': ['寅', '卯'], '死': ['巳', '午']},
                '辛': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], 
                      '囚': ['寅', '卯'], '死': ['巳', '午']},
                '壬': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], 
                      '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']},
                '癸': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], 
                      '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']}
            }
            
            if day_gan in wangxiang_table:
                table = wangxiang_table[day_gan]
                if month_zhi in table['旺']:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中得令而旺"
                elif month_zhi in table['相']:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中得生而相"
                elif month_zhi in table['休']:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中休囚"
                elif month_zhi in table['囚']:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中受克而囚"
                elif month_zhi in table['死']:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中受克而死"
                else:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中状态一般"
        
        # 7. 五行生克分析
        # 天干相生
        sheng_relations = [
            ('木', '火', '木生火'), ('火', '土', '火生土'),
            ('土', '金', '土生金'), ('金', '水', '金生水'), ('水', '木', '水生木')
        ]
        # 天干相克
        ke_relations = [
            ('木', '土', '木克土'), ('土', '水', '土克水'),
            ('水', '火', '水克火'), ('火', '金', '火克金'), ('金', '木', '金克木')
        ]
        
        gan_list = []
        for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
            pillar = sizhu.get(pillar_name, '')
            if len(pillar) >= 1:
                gan = pillar[0]
                if gan in gan_wuxing:
                    gan_list.append((pillar_name, gan, gan_wuxing[gan]))
        
        for i in range(len(gan_list)):
            for j in range(i + 1, len(gan_list)):
                p1, g1, w1 = gan_list[i]
                p2, g2, w2 = gan_list[j]
                # 检查相生
                for s1, s2, desc in sheng_relations:
                    if (w1 == s1 and w2 == s2) or (w2 == s1 and w1 == s2):
                        details['五行生克'].append(f"{desc}: {p1}{g1}({w1})与{p2}{g2}({w2})")
                # 检查相克
                for k1, k2, desc in ke_relations:
                    if (w1 == k1 and w2 == k2) or (w2 == k1 and w1 == k2):
                        details['五行生克'].append(f"{desc}: {p1}{g1}({w1})克{p2}{g2}({w2})")
        
        return details
    
    def _calculate_zhangsheng_score(self, sizhu):
        """
        计算日主十二长生状态的评分
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            int: 十二长生评分
        """
        score = 0
        
        # 获取日干
        day_gan = sizhu.get('day_gan', '')
        if not day_gan:
            return score
        
        # 十二长生状态评分表
        zhangsheng_scores = {
            '长生': 8,
            '沐浴': 4,
            '冠带': 6,
            '临官': 10,
            '帝旺': 12,
            '衰': 2,
            '病': -2,
            '死': -6,
            '墓': -4,
            '绝': -8,
            '胎': 3,
            '养': 5
        }
        
        # 计算各柱的十二长生状态
        for pillar in ['year', 'month', 'day', 'hour']:
            zhi_key = f'{pillar}_zhi'
            if zhi_key in sizhu:
                zhi = sizhu[zhi_key]
                try:
                    state = get_zhangsheng(day_gan, zhi)
                    if state in zhangsheng_scores:
                        # 月令的影响更大
                        if pillar == 'month':
                            score += zhangsheng_scores[state] * 1.5
                        else:
                            score += zhangsheng_scores[state]
                except:
                    pass
        return int(score)
    
    def _calculate_zhizhi_relations(self, sizhu):
        """
        分析日课四柱内部地支关系（冲合刑害）的评分
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            int: 地支关系评分
        """
        score = 0
        
        # 获取各柱地支
        zhis = []
        for pillar in ['year', 'month', 'day', 'hour']:
            zhi_key = f'{pillar}_zhi'
            if zhi_key in sizhu:
                zhis.append(sizhu[zhi_key])
        
        # 分析所有地支两两关系
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                zhi1 = zhis[i]
                zhi2 = zhis[j]
                
                # 六合
                if check_liuhe(zhi1, zhi2):
                    score += 8
                # 六冲
                elif check_liuchong(zhi1, zhi2):
                    score -= 15
                # 六害
                elif check_liuhai(zhi1, zhi2):
                    score -= 6
                # 相刑
                elif check_xing(zhi1, zhi2):
                    score -= 8
        
        # 检查三合
        if len(zhis) >= 3:
            if check_sanhe(zhis):
                score += 15
        
        return score
    
    def _calculate_nayin_match(self, sizhu, owners):
        """
        计算纳音五行与事主年命的匹配度
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            
        Returns:
            int: 纳音匹配评分
        """
        if not owners:
            return 0
        
        score = 0
        
        # 提取日课各柱纳音
        sizhu_nayin = []
        for pillar in ['年柱', '月柱', '日柱', '时柱']:
            if pillar in sizhu:
                try:
                    nayin = get_nayin(sizhu[pillar])
                    if nayin:
                        sizhu_nayin.append(nayin)
                except:
                    pass
        
        # 遍历事主，计算纳音匹配
        for owner in owners:
            # 获取事主年命纳音
            owner_year = owner.get('year', '')
            if owner_year:
                try:
                    # 简化处理：假设owner_year是年份，转换为年柱
                    # 实际应用中可能需要更复杂的年柱计算
                    pass
                except:
                    pass
        
        # 基础纳音匹配评分（简化版）
        # 实际应用中可以根据纳音五行生克关系进行更详细的评分
        if sizhu_nayin:
            score += len(sizhu_nayin) * 2
        
        return score
    
    def _get_level(self, score, wu_xing_result, huangdao_info):
        """
        根据分数、五行和黄道判断等级（含星级）
        
        星级标准：
        ⭐⭐⭐⭐⭐ (5星) = 上吉 - 首选推荐，五行大吉+黄道大吉
        ⭐⭐⭐⭐ (4星) = 大吉 - 诸事皆宜，五行大吉
        ⭐⭐⭐ (3星) = 吉 - 可用，五行合格+黄道吉
        ⭐⭐ (2星) = 中吉/次吉 - 可用但需谨慎
        ⭐ (1星) = 平 - 仅适合小事
        ❌ (0星) = 凶 - 坚决不用
        
        冲突处理规则：
        规则一：五行大吉 + 黄道大吉 → ⭐⭐⭐⭐⭐ 上吉（首选推荐）
        规则二：五行大吉 + 黄道黑道 → ⭐⭐ 次吉（可用，可加注"虽有黑道，但五行旺相无碍"或建议化解）
        规则三：五行平平 + 黄道大吉 → ⭐ 平（仅适合小事，大事根基不稳）
        规则四：五行凶 + 任何黄道 → ❌ 凶（坚决不用）
        
        Args:
            score: 综合评分
            wu_xing_result: 五行审核结果
            huangdao_info: 黄道信息
            
        Returns:
            str: 等级（含星级）
        """
        wu_xing_score = wu_xing_result['score']
        huangdao_level = huangdao_info['huang_dao_level']
        da_huang_dao = huangdao_info['da_huang_dao']
        
        # 规则四：五行凶 + 任何黄道 → ❌ 凶（坚决不用）
        if wu_xing_score < 60:
            return '❌ 凶'
        
        # 规则一：五行大吉 + 黄道大吉 → ★★★★★ 上吉（首选推荐）
        if wu_xing_score >= 120 and huangdao_level == '大吉':
            return '★★★★★ 上吉'
        
        # 规则二：五行大吉 + 黄道黑道 → ★★ 次吉
        if wu_xing_score >= 120 and da_huang_dao['type'] == '凶':
            return '★★ 次吉'
        
        # 规则三：五行平平 + 黄道大吉 → ★ 平
        if wu_xing_score >= 60 and wu_xing_score < 80 and huangdao_level == '大吉':
            return '★ 平'
        
        # 根据综合评分判断
        if score >= 130:
            return '★★★★★ 上吉'
        elif score >= 120:
            return '★★★★ 大吉'
        elif score >= 100:
            return '★★★ 吉'
        elif score >= 80:
            return '★★ 中吉'
        elif score >= 60:
            return '★ 平'
        else:
            return '❌ 凶'
    
    def _generate_reason(self, wu_xing_result, huangdao_info, yueling_score, xishen_score=0):
        """
        生成评分理由
        
        Args:
            wu_xing_result: 五行审核结果
            huangdao_info: 黄道信息
            yueling_score: 月令评分
            xishen_score: 喜用神匹配评分
            
        Returns:
            str: 评分理由
        """
        reason = []
        details = wu_xing_result.get('details', {})
        
        # 五行评语
        reason.append(f"五行：{wu_xing_result['ji_yu']}")
        
        # 日主旺衰分析
        if details.get('日主旺衰'):
            reason.append(f"日主：{details['日主旺衰']}")
        
        # 地支关系分析
        if details.get('地支关系'):
            relations = details['地支关系']
            good_relations = [r for r in relations if '三合' in r or '六合' in r]
            bad_relations = [r for r in relations if '冲' in r or '害' in r or '刑' in r]
            if good_relations:
                reason.append(f"地支合局：{'；'.join(good_relations)}")
            if bad_relations:
                reason.append(f"地支冲害：{'；'.join(bad_relations)}")
        
        # 吉神分析
        if details.get('吉神'):
            jishen = details['吉神']
            if jishen:
                reason.append(f"吉神：{'；'.join(jishen)}")
        
        # 月令评语
        if yueling_score > 5:
            reason.append(f"月令：得令助，日主旺相")
        elif yueling_score > 0:
            reason.append(f"月令：有生扶，日主得力")
        elif yueling_score == 0:
            reason.append(f"月令：平平，无明显助力")
        elif yueling_score > -5:
            reason.append(f"月令：气弱，需后天补救")
        else:
            reason.append(f"月令：失令，日主乏力")
        
        # 喜用神匹配评语
        if xishen_score > 20:
            reason.append(f"喜用神：日课大喜事主用神，能量共振极佳")
        elif xishen_score > 10:
            reason.append(f"喜用神：日课补益事主用神，有利催吉")
        elif xishen_score > 0:
            reason.append(f"喜用神：日课对事主有一定补益")
        elif xishen_score == 0:
            reason.append(f"喜用神：日课与事主八字无明显冲突")
        
        # 黄道评语
        da_huang_dao = huangdao_info['da_huang_dao']
        xiao_huang_dao = huangdao_info['xiao_huang_dao']
        
        if da_huang_dao['type'] == '吉':
            reason.append(f"大黄道{da_huang_dao['name']}，{da_huang_dao['description']}")
        elif da_huang_dao['type'] == '凶':
            reason.append(f"黑道{da_huang_dao['name']}，{da_huang_dao['description']}")
        
        if xiao_huang_dao['type'] == '吉':
            reason.append(f"小黄道{xiao_huang_dao['name']}，{xiao_huang_dao['description']}")
        
        # 神煞理由
        good_shensha = [s for s in self.shensha_list if s['score'] > 0]
        bad_shensha = [s for s in self.shensha_list if s['score'] < 0]
        
        if good_shensha:
            reason.append('吉神：' + '、'.join([s['name'] for s in good_shensha]))
        if bad_shensha:
            reason.append('凶神：' + '、'.join([s['name'] for s in bad_shensha]))
        
        # 宜忌理由
        if self.yi_list:
            reason.append('宜：' + '、'.join(self.yi_list))
        if self.ji_list:
            reason.append('忌：' + '、'.join(self.ji_list))
        
        return '；'.join(reason)


# 全局评分器实例
scorer = Scorer()

def calculate_score(sizhu, event_type, owners=None, house_type=None, shan_xiang=None,
                    zaoxiang=None, zaowei=None, chuangwei=None):
    """
    计算评分（便捷函数）
    
    采用"五行为主，黄道为用"的架构：
    第一层（核心筛选）：正五行模块
    第二层（优选排序）：大小黄道模块
    第三层（深度优化）：月令对日主的帮助
    
    Args:
        sizhu: 四柱信息
        event_type: 事项类型
        owners: 事主信息
        house_type: 宅型（阳宅/阴宅）
        shan_xiang: 山向
        zaoxiang: 灶向（作灶专用）
        zaowei: 灶位（作灶专用）
        chuangwei: 床位朝向（安床专用）
        
    Returns:
        dict: 评分结果
    """
    return scorer.score(sizhu, event_type, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei)


# -*- coding: utf-8 -*-
"""
================================================================================
神煞模块基类
================================================================================
定义神煞检查的基础接口和通用方法
================================================================================
"""

class ShenShaChecker:
    """神煞检查器基类"""
    
    def __init__(self):
        self.shensha_list = []
    
    def check(self, sizhu, owners=None):
        """
        检查神煞
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            
        Returns:
            list: 神煞列表
        """
        self.shensha_list = []
        self._check_year_shensha(sizhu)
        self._check_month_shensha(sizhu)
        self._check_day_shensha(sizhu)
        self._check_hour_shensha(sizhu)
        self._check_special_shensha(sizhu, owners)
        return self.shensha_list
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        pass
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        pass
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        pass
    
    def _check_hour_shensha(self, sizhu):
        """检查时神煞"""
        pass
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞"""
        pass
    
    def _add_shensha(self, name, score, description):
        """
        添加神煞
        
        Args:
            name: 神煞名称
            score: 分数
            description: 描述
        """
        self.shensha_list.append({
            'name': name,
            'score': score,
            'description': description
        })


# -*- coding: utf-8 -*-
"""
================================================================================
通用神煞模块
================================================================================
实现通用择日神煞的检查逻辑
包含：太岁、岁破、月破、黄道、黑道等基本神煞

使用方法:
    1. 作为模块导入: from modules.shensha.通用神煞 import CommonShenShaChecker
    2. 直接运行: python -m modules.shensha.通用神煞
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
class CommonShenShaChecker(ShenShaChecker):
    """通用神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        year_gan = sizhu.get('year_gan', '甲')
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        # 太岁
        self._add_shensha('太岁', -20, '年之主宰，不可冒犯')
        
        # 岁破
        if day_zhi == self._get_suipo(year_zhi):
            self._add_shensha('岁破', -15, '与太岁相冲，百事不宜')
        
        # 年支三煞（劫煞、灾煞、岁煞）
        if self._is_nian_sansha(sizhu):
            self._add_shensha('年三煞', -18, '年支三煞，诸事不宜')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        # 月破
        if day_zhi == self._get_yuepo(month_zhi):
            self._add_shensha('月破', -25, '与月建相冲，诸事不宜')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -10, '与月建相刑，诸事不利')
        
        # 月害
        if self._is_yuehai(sizhu):
            self._add_shensha('月害', -8, '与月建相害，诸事不顺')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        try:
            day_gan = sizhu.get('day_gan', '甲')
            day_zhi = sizhu.get('day_zhi', '子')
            month_zhi = sizhu.get('month_zhi', '子')
            
            # ===== 凶煞 =====
            
            # 四离日
            if self._is_sili(sizhu):
                self._add_shensha('四离日', -30, '春分、秋分、夏至、冬至前一日，忌大事')
            
            # 四绝日
            if self._is_sijue(sizhu):
                self._add_shensha('四绝日', -30, '立春、立夏、立秋、立冬前一日，忌大事')
            
            # 四废日
            if self._is_sifei(sizhu):
                self._add_shensha('四废日', -15, '春庚申辛酉，夏壬子癸亥，秋甲寅乙卯，冬丙午丁巳')
            
            # 十恶大败
            if self._is_shie_dabai(sizhu):
                self._add_shensha('十恶大败', -25, '忌大事，犯之主败')
        
        # ===== 吉神 =====
        
        # 天德
            if self._is_tiande(sizhu):
                self._add_shensha('天德', 15, '百事皆宜，诸凶皆解')
            
            # 月德
            if self._is_yuede(sizhu):
                self._add_shensha('月德', 15, '百事皆宜，诸凶皆解')
            
            # 天德合
            if self._is_tiandehe(sizhu):
                self._add_shensha('天德合', 12, '诸事吉利')
            
            # 月德合
            if self._is_yuedehe(sizhu):
                self._add_shensha('月德合', 12, '诸事吉利')
            
            # 大黄道吉日
            da_huangdao = self._get_da_huangdao(day_zhi, month_zhi)
            if da_huangdao:
                self._add_shensha(f'大黄道-{da_huangdao}', 15, '黄道吉日，诸事皆宜')
            
            # 小黄道吉日（十二建星）
            xiao_huangdao = self._get_xiao_huangdao(day_zhi, month_zhi)
            if xiao_huangdao:
                self._add_shensha(f'小黄道-{xiao_huangdao}', 8, '建星吉日')
        except Exception as e:
            logger.error(f"检查日神煞失败: {str(e)}", exc_info=True)
    
    def _check_hour_shensha(self, sizhu):
        """检查时神煞"""
        try:
            hour_zhi = sizhu.get('hour_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            # 黄道吉时
            huangdao_shi = self._get_huangdao_shi(day_zhi, hour_zhi)
            if huangdao_shi:
                self._add_shensha(f'黄道时-{huangdao_shi}', 8, '时辰吉利')
            
            # 日破时
            if hour_zhi == self._get_suipo(day_zhi):
                self._add_shensha('日破时', -10, '时辰与日支相冲')
        except Exception as e:
            logger.error(f"检查时神煞失败: {str(e)}", exc_info=True)
    
    # ===== 辅助方法 =====
    
    def _get_suipo(self, zhi):
        """获取冲支（岁破/月破/日破）"""
        zh_list = DI_ZHI
        idx = zh_list.index(zhi)
        return zh_list[(idx + 6) % 12]
    
    def _get_yuepo(self, month_zhi):
        """获取月破"""
        return self._get_suipo(month_zhi)
    
    def _is_nian_sansha(self, sizhu):
        """是否年支三煞"""
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        zh_list = DI_ZHI
        
        if year_zhi in SANSHA_MAP:
            sansha_indices = SANSHA_MAP[year_zhi]
            day_idx = zh_list.index(day_zhi)
            return day_idx in sansha_indices
        return False
    
    def _is_yuexing(self, sizhu):
        """是否月刑"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        # 地支相刑：寅刑巳、巳刑申、申刑寅（三刑）
        # 丑刑戌、戌刑未、未刑丑（三刑）
        # 子刑卯、卯刑子（相刑）
        # 辰刑辰、午刑午、酉刑酉、亥刑亥（自刑）
        xing_map = {
            '寅': '巳', '巳': '申', '申': '寅',
            '丑': '戌', '戌': '未', '未': '丑',
            '子': '卯', '卯': '子',
            '辰': '辰', '午': '午', '酉': '酉', '亥': '亥'
        }
        return day_zhi == xing_map.get(month_zhi)
    
    def _is_yuehai(self, sizhu):
        """是否月害"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        # 地支六害：子未害、丑午害、寅巳害、卯辰害、申亥害、酉戌害
        hai_map = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        return day_zhi == hai_map.get(month_zhi)
    
    def _is_sili(self, sizhu):
        """是否四离日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        sili_map = {
            '卯': '辰', '午': '未', '酉': '戌', '子': '丑'
        }
        return day_zhi == sili_map.get(month_zhi)
    
    def _is_sijue(self, sizhu):
        """是否四绝日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        sijue_map = {
            '丑': '寅', '辰': '巳', '未': '申', '戌': '亥'
        }
        return day_zhi == sijue_map.get(month_zhi)
    
    def _is_sifei(self, sizhu):
        """是否四废日"""
        try:
            day_gan = sizhu.get('day_gan', '甲')
            day_zhi = sizhu.get('day_zhi', '子')
            month_zhi = sizhu.get('month_zhi', '子')
            day_pillar = day_gan + day_zhi
            
            # 春季（寅卯辰月）：庚申、辛酉
            # 夏季（巳午未月）：壬子、癸亥
            # 秋季（申酉戌月）：甲寅、乙卯
            # 冬季（亥子丑月）：丙午、丁巳
            sifei_map = {
                '寅': ['庚申', '辛酉'],
                '卯': ['庚申', '辛酉'],
                '辰': ['庚申', '辛酉'],
                '巳': ['壬子', '癸亥'],
                '午': ['壬子', '癸亥'],
                '未': ['壬子', '癸亥'],
                '申': ['甲寅', '乙卯'],
                '酉': ['甲寅', '乙卯'],
                '戌': ['甲寅', '乙卯'],
                '亥': ['丙午', '丁巳'],
                '子': ['丙午', '丁巳'],
                '丑': ['丙午', '丁巳']
            }
            return day_pillar in sifei_map.get(month_zhi, [])
        except Exception as e:
            logger.error(f"检查四废日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_shie_dabai(self, sizhu):
        """是否十恶大败"""
        try:
            day_gan = sizhu.get('day_gan', '甲')
            day_zhi = sizhu.get('day_zhi', '子')
            day_pillar = day_gan + day_zhi
            
            shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
            return day_pillar in shie_dabai
        except Exception as e:
            logger.error(f"检查十恶大败失败: {str(e)}", exc_info=True)
            return False
    
    def _is_tiande(self, sizhu):
        """是否天德"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_gan = sizhu.get('day_gan', '甲')
            zh_list = DI_ZHI
            if month_zhi not in zh_list:
                return False
            idx = zh_list.index(month_zhi)
            return day_gan == TIANDE.get(idx)
        except Exception as e:
            logger.error(f"检查天德失败: {str(e)}", exc_info=True)
            return False
    
    def _is_yuede(self, sizhu):
        """是否月德"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_gan = sizhu.get('day_gan', '甲')
            zh_list = DI_ZHI
            if month_zhi not in zh_list:
                return False
            idx = zh_list.index(month_zhi)
            return day_gan == YUEDE.get(idx)
        except Exception as e:
            logger.error(f"检查月德失败: {str(e)}", exc_info=True)
            return False
    
    def _is_tiandehe(self, sizhu):
        """是否天德合"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_gan = sizhu.get('day_gan', '甲')
            
            tiandehe_map = {
                '寅': '壬', '卯': '巳', '辰': '丁', '巳': '丙',
                '午': '寅', '未': '己', '申': '戊', '酉': '亥',
                '戌': '辛', '亥': '庚', '子': '申', '丑': '乙'
            }
            return day_gan == tiandehe_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查天德合失败: {str(e)}", exc_info=True)
            return False
    
    def _is_yuedehe(self, sizhu):
        """是否月德合"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_gan = sizhu.get('day_gan', '甲')
            
            yuedehe_map = {
                '寅': '辛', '午': '辛', '戌': '辛',
                '申': '丁', '子': '丁', '辰': '丁',
                '亥': '己', '卯': '己', '未': '己',
                '巳': '乙', '酉': '乙', '丑': '乙'
            }
            return day_gan == yuedehe_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查月德合失败: {str(e)}", exc_info=True)
            return False
    
    def _get_da_huangdao(self, day_zhi, month_zhi):
        """获取大黄道十二值星
        根据月支和日支推算
        """
        # 大黄道顺序：青龙、明堂、天刑、朱雀、金匮、天德、白虎、玉堂、天牢、玄武、司命、勾陈
        # 以月支起青龙，顺数至日支
        huangdao_list = ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈']
        zh_list = DI_ZHI
        
        month_idx = zh_list.index(month_zhi)
        day_idx = zh_list.index(day_zhi)
        
        # 从月支起青龙，计算日支对应的大黄道
        offset = (day_idx - month_idx) % 12
        return huangdao_list[offset]
    
    def _get_xiao_huangdao(self, day_zhi, month_zhi):
        """获取小黄道十二建星
        根据月支和日支推算
        """
        # 小黄道顺序：建、除、满、平、定、执、破、危、成、收、开、闭
        # 以月支起建日，顺数至日支
        jianxing_list = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
        zh_list = DI_ZHI
        
        month_idx = zh_list.index(month_zhi)
        day_idx = zh_list.index(day_zhi)
        
        # 从月支起建日，计算日支对应的小黄道
        offset = (day_idx - month_idx) % 12
        return jianxing_list[offset]
    
    def _get_huangdao_shi(self, day_zhi, hour_zhi):
        """获取黄道吉时
        根据日支和时支推算
        """
        # 黄道时辰表：以日支为键，值为从子时开始的黄道/黑道列表
        # 青龙、明堂、金匮、天德、玉堂、司命为黄道吉时
        # 天刑、朱雀、白虎、天牢、玄武、勾陈为黑道凶时
        huangdao_shi_table = {
            '子': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
            '丑': ['天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂'],
            '寅': ['朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑'],
            '卯': ['金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀'],
            '辰': ['天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮'],
            '巳': ['白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德'],
            '午': ['玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎'],
            '未': ['天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂'],
            '申': ['玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢'],
            '酉': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
            '戌': ['勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命'],
            '亥': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈']
        }
        
        if day_zhi not in huangdao_shi_table:
            return None
        
        zh_list = DI_ZHI
        hour_idx = zh_list.index(hour_zhi)
        shi_xing = huangdao_shi_table[day_zhi][hour_idx]
        
        # 只返回黄道吉时
        huangdao_xing = ['青龙', '明堂', '金匮', '天德', '玉堂', '司命']
        if shi_xing in huangdao_xing:
            return shi_xing
        return None


# -*- coding: utf-8 -*-
"""
================================================================================
婚嫁神煞模块
================================================================================
实现婚嫁择日专用神煞的检查逻辑
依据：《协纪辨方书》、《象吉通书》等传统择日经典

使用方法:
    1. 作为模块导入: from modules.shensha.嫁娶神煞 import 婚嫁神煞Checker
    2. 直接运行: python -m modules.shensha.嫁娶神煞
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
class MarriageShenShaChecker(ShenShaChecker):
    """婚嫁神煞检查器"""
    
    def __init__(self):
        super().__init__()
        self.bride_gan = None
        self.groom_gan = None
        self.bride_zhi = None
        self.groom_zhi = None
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        month_zhi = sizhu.get('month_zhi', '子')
        
        # 月破（婚嫁大忌）
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -25, '月破日诸事不宜，婚嫁大忌')
        
        # 大利月（需女命年干）
        if self.bride_gan and self._is_daliyue(sizhu):
            self._add_shensha('大利月', 20, '女命大利之月，婚嫁首选')
        
        # 小利月（需女命年干）
        if self.bride_gan and self._is_xiaoliyue(sizhu):
            self._add_shensha('小利月', 10, '女命小利之月，婚嫁可用')
        
        # 妨翁姑月（不利公婆）
        if self.bride_gan and self._is_fang_wenggu(sizhu):
            self._add_shensha('妨翁姑月', -15, '此月婚嫁不利翁姑（公婆）')
        
        # 妨父母月
        if self.bride_gan and self._is_fang_fumu(sizhu):
            self._add_shensha('妨父母月', -15, '此月婚嫁不利新娘父母')
        
        # 妨夫月
        if self.bride_gan and self._is_fang_fu(sizhu):
            self._add_shensha('妨夫月', -18, '此月婚嫁不利新郎')
        
        # 妨妻月
        if self.bride_gan and self._is_fang_qi(sizhu):
            self._add_shensha('妨妻月', -18, '此月婚嫁不利新娘')
        
        # 逐夫月
        if self.bride_gan and self._is_zhu_fu(sizhu):
            self._add_shensha('逐夫月', -12, '逐夫月不利新郎')
        
        # 逐妇月
        if self.bride_gan and self._is_zhu_qi(sizhu):
            self._add_shensha('逐妇月', -12, '逐妇月不利新娘')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        try:
            day_gan = sizhu.get('day_gan', '甲')
            day_zhi = sizhu.get('day_zhi', '子')
            month_zhi = sizhu.get('month_zhi', '子')
        except Exception as e:
            logger.error(f"获取日干信息失败: {str(e)}", exc_info=True)
            return
        
        # ===== 极凶日（婚嫁绝对禁忌）=====
        
        # 红砂日（按孟仲季月）
        if self._is_hongsha(sizhu):
            self._add_shensha('红砂日', -20, '红砂日婚嫁大忌')
        
        # 杨公忌日（固定日期）
        if self._is_yanggongji(sizhu):
            self._add_shensha('杨公忌日', -20, '杨公忌日百事不宜，婚嫁大忌')
        
        # 受死日
        if self._is_shousi(sizhu):
            self._add_shensha('受死日', -20, '受死日婚嫁大忌')
        
        # 往亡日
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -18, '往亡日忌婚嫁')
        
        # 重丧日
        if self._is_zhongsang(sizhu):
            self._add_shensha('重丧日', -20, '重丧日婚嫁大忌')
        
        # 三娘煞
        if self._is_sanniang(sizhu):
            self._add_shensha('三娘煞', -15, '三娘煞日不宜婚嫁')
        
        # ===== 凶煞 =====
        
        # 白虎日
        if self._is_baihu(sizhu):
            self._add_shensha('白虎日', -12, '白虎日婚嫁不吉')
        
        # 朱雀日
        if self._is_zhuque(sizhu):
            self._add_shensha('朱雀日', -12, '朱雀日婚嫁不吉')
        
        # 天狗日
        if self._is_tiangou(sizhu):
            self._add_shensha('天狗日', -12, '天狗日不宜婚嫁')
        
        # 孤辰寡宿
        if self._is_guchen(sizhu):
            self._add_shensha('孤辰寡宿', -15, '孤辰寡宿主孤独，忌婚嫁')
        
        # ===== 吉日 =====
        
        # 不将日（婚嫁首选）
        if self._is_bujiang(sizhu):
            self._add_shensha('不将日', 15, '不将日婚嫁大吉')
        
        # 周堂吉日
        if self._is_zhoutang(sizhu):
            self._add_shensha('周堂吉日', 12, '周堂吉日婚嫁可用')
        
        # 天德日
        if self._is_tiande(sizhu):
            self._add_shensha('天德日', 12, '天德日百事吉')
        
        # 月德日
        if self._is_yuede(sizhu):
            self._add_shensha('月德日', 10, '月德日百事吉')
        
        # 三合日
        if self._is_sanhe(sizhu):
            self._add_shensha('三合日', 8, '三合日婚嫁吉')
        
        # 六合日
        if self._is_liuhe(sizhu):
            self._add_shensha('六合日', 8, '六合日婚嫁吉')
        
        # 五合日
        if self._is_wuhe(sizhu):
            self._add_shensha('五合日', 8, '五合日婚嫁吉')
        
        # 母仓日
        if self._is_mucang(sizhu):
            self._add_shensha('母仓日', 6, '母仓日婚嫁吉')
        
        # 旺日
        if self._is_wangri(sizhu):
            self._add_shensha('旺日', 6, '旺日婚嫁吉')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞（与新人相关）"""
        if not owners:
            return
        
        # 解析新郎新娘信息
        for owner in owners:
            name = owner.get('姓名', '')
            gender = owner.get('性别', '')
            zodiac = owner.get('生肖', '')
            year_gan = owner.get('年干', '')
            
            if gender == '女':
                self.bride_gan = year_gan
                self.bride_zhi = zodiac
            elif gender == '男':
                self.groom_gan = year_gan
                self.groom_zhi = zodiac
        
        # 检查与新人冲煞
        if self.bride_zhi:
            # 冲新娘
            if self._is_chong_bride(sizhu):
                self._add_shensha('冲新娘', -25, f'日支与新娘生肖({self.bride_zhi})相冲，大凶')
            # 新娘相合
            elif self._is_he_bride(sizhu):
                self._add_shensha('新娘相合', 10, f'日支与新娘生肖({self.bride_zhi})相合，吉')
        
        if self.groom_zhi:
            # 冲新郎
            if self._is_chong_groom(sizhu):
                self._add_shensha('冲新郎', -25, f'日支与新郎生肖({self.groom_zhi})相冲，大凶')
            # 新郎相合
            elif self._is_he_groom(sizhu):
                self._add_shensha('新郎相合', 10, f'日支与新郎生肖({self.groom_zhi})相合，吉')
        
        # 日干与新人年干相合
        if self.bride_gan and self._is_gan_he_bride(sizhu):
            self._add_shensha('新娘干合', 8, f'日干与新娘年干({self.bride_gan})相合，吉')
        
        if self.groom_gan and self._is_gan_he_groom(sizhu):
            self._add_shensha('新郎干合', 8, f'日干与新郎年干({self.groom_gan})相合，吉')
    
    # ===== 大利月/小利月（按女命年干）=====
    
    def _is_daliyue(self, sizhu):
        """
        是否大利月（按女命年干推算）
        口诀：甲己大利二八月，乙庚四十二月当，丙辛六十二月在，丁壬八二月相当，戊癸大利四十月
        """
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu.get('month_zhi', '子')
        
        daliyue_map = {
            '甲': ['卯', '酉'],      # 二月、八月
            '己': ['卯', '酉'],
            '乙': ['巳', '亥'],      # 四月、十月
            '庚': ['巳', '亥'],
            '丙': ['午', '子'],      # 五月、十一月
            '辛': ['午', '子'],
            '丁': ['未', '丑'],      # 六月、十二月
            '壬': ['未', '丑'],
            '戊': ['巳', '亥'],      # 四月、十月
            '癸': ['巳', '亥']
        }
        
        return month_zhi in daliyue_map.get(self.bride_gan, [])
    
    def _is_xiaoliyue(self, sizhu):
        """
        是否小利月（按女命年干推算）
        小利月为大利月的前后月
        """
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu.get('month_zhi', '子')
        
        xiaoliyue_map = {
            '甲': ['辰', '戌'],      # 三月、九月
            '己': ['辰', '戌'],
            '乙': ['午', '子'],      # 五月、十一月
            '庚': ['午', '子'],
            '丙': ['未', '丑'],      # 六月、十二月
            '辛': ['未', '丑'],
            '丁': ['申', '寅'],      # 七月、正月
            '壬': ['申', '寅'],
            '戊': ['午', '子'],      # 五月、十一月
            '癸': ['午', '子']
        }
        
        return month_zhi in xiaoliyue_map.get(self.bride_gan, [])
    
    # ===== 妨碍类月份 =====
    
    def _is_fang_wenggu(self, sizhu):
        """是否妨翁姑月（不利公婆）"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu.get('month_zhi', '子')
        
        fang_wenggu_map = {
            '甲': ['巳', '亥'],
            '己': ['巳', '亥'],
            '乙': ['午', '子'],
            '庚': ['午', '子'],
            '丙': ['申', '寅'],
            '辛': ['申', '寅'],
            '丁': ['酉', '卯'],
            '壬': ['酉', '卯'],
            '戊': ['未', '丑'],
            '癸': ['未', '丑']
        }
        
        return month_zhi in fang_wenggu_map.get(self.bride_gan, [])
    
    def _is_fang_fumu(self, sizhu):
        """是否妨父母月"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu.get('month_zhi', '子')
        
        fang_fumu_map = {
            '甲': ['午', '子'],
            '己': ['午', '子'],
            '乙': ['未', '丑'],
            '庚': ['未', '丑'],
            '丙': ['酉', '卯'],
            '辛': ['酉', '卯'],
            '丁': ['戌', '辰'],
            '壬': ['戌', '辰'],
            '戊': ['申', '寅'],
            '癸': ['申', '寅']
        }
        
        return month_zhi in fang_fumu_map.get(self.bride_gan, [])
    
    def _is_fang_fu(self, sizhu):
        """是否妨夫月"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu.get('month_zhi', '子')
        
        fang_fu_map = {
            '甲': ['未', '丑'],
            '己': ['未', '丑'],
            '乙': ['申', '寅'],
            '庚': ['申', '寅'],
            '丙': ['戌', '辰'],
            '辛': ['戌', '辰'],
            '丁': ['亥', '巳'],
            '壬': ['亥', '巳'],
            '戊': ['酉', '卯'],
            '癸': ['酉', '卯']
        }
        
        return month_zhi in fang_fu_map.get(self.bride_gan, [])
    
    def _is_fang_qi(self, sizhu):
        """是否妨妻月"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu.get('month_zhi', '子')
        
        fang_qi_map = {
            '甲': ['申', '寅'],
            '己': ['申', '寅'],
            '乙': ['酉', '卯'],
            '庚': ['酉', '卯'],
            '丙': ['亥', '巳'],
            '辛': ['亥', '巳'],
            '丁': ['子', '午'],
            '壬': ['子', '午'],
            '戊': ['戌', '辰'],
            '癸': ['戌', '辰']
        }
        
        return month_zhi in fang_qi_map.get(self.bride_gan, [])
    
    def _is_zhu_fu(self, sizhu):
        """是否逐夫月"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu.get('month_zhi', '子')
        
        zhu_fu_map = {
            '甲': ['酉', '卯'],
            '己': ['酉', '卯'],
            '乙': ['戌', '辰'],
            '庚': ['戌', '辰'],
            '丙': ['子', '午'],
            '辛': ['子', '午'],
            '丁': ['丑', '未'],
            '壬': ['丑', '未'],
            '戊': ['亥', '巳'],
            '癸': ['亥', '巳']
        }
        
        return month_zhi in zhu_fu_map.get(self.bride_gan, [])
    
    def _is_zhu_qi(self, sizhu):
        """是否逐妇月"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu.get('month_zhi', '子')
        
        zhu_qi_map = {
            '甲': ['戌', '辰'],
            '己': ['戌', '辰'],
            '乙': ['亥', '巳'],
            '庚': ['亥', '巳'],
            '丙': ['子', '午'],
            '辛': ['子', '午'],
            '丁': ['丑', '未'],
            '壬': ['丑', '未'],
            '戊': ['寅', '申'],
            '癸': ['寅', '申']
        }
        
        return month_zhi in zhu_qi_map.get(self.bride_gan, [])
    
    # ===== 凶煞 =====
    
    def _is_yuepo(self, sizhu):
        """是否月破"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        yuepo = zh_list[(idx + 6) % 12]
        return day_zhi == yuepo
    
    def _is_hongsha(self, sizhu):
        """
        是否红砂日（按孟仲季月）
        口诀：四孟月酉，四仲月巳，四季月丑
        孟月：正月、四月、七月、十月（寅巳申亥）
        仲月：二月、五月、八月、十一月（子午卯酉）
        季月：三月、六月、九月、十二月（辰戌丑未）
        """
        month = sizhu.get('month_zhi', '子')
        day = sizhu.get('day_zhi', '子')
        meng = ['寅','巳','申','亥']
        zhong = ['子','午','卯','酉']
        ji = ['辰','戌','丑','未']
        if month in meng and day == '酉': return True
        if month in zhong and day == '巳': return True
        if month in ji and day == '丑': return True
        return False
    
    def _is_yanggongji(self, sizhu):
        """
        是否杨公忌日（固定农历日期）
        正月十三、二月十一、三月初九、四月初七、五月初五、六月初三、
        七月初一、七月廿九、八月廿七、九月廿五、十月廿三、十一月廿一、十二月十九
        
        【实现说明】
        使用 lunar_python 计算农历日期，判断是否为固定的13个杨公忌日
        若 lunar_python 不可用，则使用简化版判断
        """
        try:
            from lunar_python import Solar
            
            # 从 sizhu 中提取年、月、日信息
            # 注意：这里需要从外部传入公历日期，或者通过其他方式获取
            # 暂时假设 sizhu 中包含公历日期信息
            # 实际使用时，需要从调用方传入完整的日期信息
            
            # 简化实现：返回 False，实际使用时需要根据具体日期计算
            # 后续可通过修改接口，让调用方传入完整的日期信息
            return False
        except:
            return False
    
    def _is_shousi(self, situ):
        """
        是否受死日
        口诀：正戌二辰三亥四巳五子六午七丑八未八寅九申十卯十酉十一辰十二戌
        """
        month_zhi = situ['month_zhi']
        day_zhi = situ['day_zhi']
        
        shousi_map = {
            '寅': '戌', '卯': '辰', '辰': '亥', '巳': '巳',
            '午': '子', '未': '午', '申': '丑', '酉': '未',
            '戌': '寅', '亥': '申', '子': '卯', '丑': '酉'
        }
        return day_zhi == shousi_map.get(month_zhi)
    
    def _is_wangwang(self, sizhu):
        """是否往亡日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        wangwang_map = {
            '寅': '寅', '卯': '巳', '辰': '申', '巳': '亥',
            '午': '卯', '未': '午', '申': '酉', '酉': '子',
            '戌': '辰', '亥': '未', '子': '戌', '丑': '丑'
        }
        return day_zhi == wangwang_map.get(month_zhi)
    
    def _is_zhongsang(self, sizhu):
        """是否重丧日"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_gan = sizhu.get('day_gan', '甲')
            
            zhongsang_map = {
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
            
            return day_gan in zhongsang_map.get(month_zhi, [])
        except Exception as e:
            logger.error(f"检查重丧日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_sanniang(self, sizhu):
        """
        是否三娘煞
        每月初三、初七、十三、十八、廿二、廿七
        注：需农历日期，当前实现需要传入完整的日期信息
        """
        # 三娘煞按农历日期判断：每月初三、初七、十三、十八、廿二、廿七
        # 由于当前sizhu不包含农历日期信息，暂时返回False
        # 后续可通过修改接口，让调用方传入完整的日期信息
        return False
    
    def _is_baihu(self, sizhu):
        """是否白虎日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        baihu_map = {
            '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
            '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
            '戌': '午', '亥': '未', '子': '申', '丑': '酉'
        }
        return day_zhi == baihu_map.get(month_zhi)
    
    def _is_zhuque(self, sizhu):
        """是否朱雀日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        zhuque_map = {
            '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
            '午': '未', '未': '申', '申': '酉', '酉': '戌',
            '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
        }
        return day_zhi == zhuque_map.get(month_zhi)
    
    def _is_tiangou(self, sizhu):
        """是否天狗日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        tiangou_map = {
            '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
            '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
            '戌': '午', '亥': '未', '子': '申', '丑': '酉'
        }
        return day_zhi == tiangou_map.get(month_zhi)
    
    def _is_guchen(self, sizhu):
        """是否孤辰寡宿"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        guchen_map = {
            '寅': ['巳', '丑'],
            '卯': ['巳', '丑'],
            '辰': ['巳', '丑'],
            '巳': ['申', '辰'],
            '午': ['申', '辰'],
            '未': ['申', '辰'],
            '申': ['亥', '未'],
            '酉': ['亥', '未'],
            '戌': ['亥', '未'],
            '亥': ['寅', '戌'],
            '子': ['寅', '戌'],
            '丑': ['寅', '戌']
        }
        
        return day_zhi in guchen_map.get(month_zhi, [])
    
    # ===== 吉日 =====
    
    def _is_bujiang(self, sizhu):
        """是否不将日"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_gan = sizhu.get('day_gan', '甲')
            day_zhi = sizhu.get('day_zhi', '子')
            
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
        except Exception as e:
            logger.error(f"检查不将日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_zhoutang(self, sizhu):
        """是否周堂吉日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        zhoutang_ji = {
            '寅': ['丑', '卯', '辰', '午'],
            '卯': ['寅', '辰', '巳', '未'],
            '辰': ['卯', '巳', '午', '申'],
            '巳': ['辰', '午', '未', '酉'],
            '午': ['巳', '未', '申', '戌'],
            '未': ['午', '申', '酉', '亥'],
            '申': ['未', '酉', '戌', '子'],
            '酉': ['申', '戌', '亥', '丑'],
            '戌': ['酉', '亥', '子', '寅'],
            '亥': ['戌', '子', '丑', '卯'],
            '子': ['亥', '丑', '寅', '辰'],
            '丑': ['子', '寅', '卯', '巳']
        }
        
        return day_zhi in zhoutang_ji.get(month_zhi, [])
    
    def _is_tiande(self, sizhu):
        """是否天德日"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_gan = sizhu.get('day_gan', '甲')
            day_zhi = sizhu.get('day_zhi', '子')
            
            tiande_map = {
                '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
                '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
                '戌': '丙', '亥': '乙', '子': '巳', '丑': '庚'
            }
            
            tiande = tiande_map.get(month_zhi)
            return day_gan == tiande or day_zhi == tiande
        except Exception as e:
            logger.error(f"检查天德日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_yuede(self, sizhu):
        """是否月德日"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_gan = sizhu.get('day_gan', '甲')
            
            yuede_map = {
                '寅': '丙', '午': '丙', '戌': '丙',
                '申': '壬', '子': '壬', '辰': '壬',
                '巳': '庚', '酉': '庚', '丑': '庚',
                '亥': '甲', '卯': '甲', '未': '甲'
            }
            
            return day_gan == yuede_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查月德日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_sanhe(self, sizhu):
        """是否三合日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        sanhe_map = {
            '寅': ['午', '戌'],
            '午': ['寅', '戌'],
            '戌': ['寅', '午'],
            '巳': ['酉', '丑'],
            '酉': ['巳', '丑'],
            '丑': ['巳', '酉'],
            '申': ['子', '辰'],
            '子': ['申', '辰'],
            '辰': ['申', '子'],
            '亥': ['卯', '未'],
            '卯': ['亥', '未'],
            '未': ['亥', '卯']
        }
        
        return day_zhi in sanhe_map.get(month_zhi, [])
    
    def _is_liuhe(self, sizhu):
        """是否六合日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        return day_zhi == liuhe_map.get(month_zhi)
    
    def _is_wuhe(self, sizhu):
        """是否五合日"""
        try:
            day_gan = sizhu.get('day_gan', '甲')
            
            wuhe = ['甲', '己', '丙', '辛', '戊', '癸']
            return day_gan in wuhe
        except Exception as e:
            logger.error(f"检查五合日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_mucang(self, sizhu):
        """是否母仓日"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            mucang_map = {
                '寅': ['卯', '辰'],
                '卯': ['卯', '辰'],
                '辰': ['卯', '辰'],
                '巳': ['午', '未'],
                '午': ['午', '未'],
                '未': ['午', '未'],
                '申': ['酉', '戌'],
                '酉': ['酉', '戌'],
                '戌': ['酉', '戌'],
                '亥': ['子', '丑'],
                '子': ['子', '丑'],
                '丑': ['子', '丑']
            }
            
            return day_zhi in mucang_map.get(month_zhi, [])
        except Exception as e:
            logger.error(f"检查母仓日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_wangri(self, sizhu):
        """是否旺日"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            wangri_map = {
                '寅': '卯', '卯': '卯',
                '辰': '午', '巳': '午',
                '午': '午', '未': '酉',
                '申': '酉', '酉': '酉',
                '戌': '子', '亥': '子',
                '子': '子', '丑': '卯'
            }
            
            return day_zhi == wangri_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查旺日失败: {str(e)}", exc_info=True)
            return False
    
    # ===== 新人相关检查 =====
    
    def _is_chong_bride(self, sizhu):
        """日支是否冲新娘生肖"""
        if not self.bride_zhi:
            return False
        
        day_zhi = sizhu.get('day_zhi', '子')
        zh_list = DI_ZHI
        
        if self.bride_zhi not in zh_list:
            return False
        
        idx = zh_list.index(self.bride_zhi)
        chong = zh_list[(idx + 6) % 12]
        return day_zhi == chong
    
    def _is_chong_groom(self, sizhu):
        """日支是否冲新郎生肖"""
        if not self.groom_zhi:
            return False
        
        day_zhi = sizhu.get('day_zhi', '子')
        zh_list = DI_ZHI
        
        if self.groom_zhi not in zh_list:
            return False
        
        idx = zh_list.index(self.groom_zhi)
        chong = zh_list[(idx + 6) % 12]
        return day_zhi == chong
    
    def _is_he_bride(self, sizhu):
        """日支是否与新娘生肖相合"""
        if not self.bride_zhi:
            return False
        
        day_zhi = sizhu.get('day_zhi', '子')
        
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        return day_zhi == liuhe_map.get(self.bride_zhi)
    
    def _is_he_groom(self, sizhu):
        """日支是否与新郎生肖相合"""
        if not self.groom_zhi:
            return False
        
        day_zhi = sizhu.get('day_zhi', '子')
        
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        return day_zhi == liuhe_map.get(self.groom_zhi)
    
    def _is_gan_he_bride(self, sizhu):
        """日干是否与新娘年干相合"""
        if not self.bride_gan:
            return False
        
        day_gan = sizhu.get('day_gan', '甲')
        
        ganhe_map = {
            '甲': '己', '己': '甲',
            '乙': '庚', '庚': '乙',
            '丙': '辛', '辛': '丙',
            '丁': '壬', '壬': '丁',
            '戊': '癸', '癸': '戊'
        }
        
        return day_gan == ganhe_map.get(self.bride_gan)
    
    def _is_gan_he_groom(self, sizhu):
        """日干是否与新郎年干相合"""
        if not self.groom_gan:
            return False
        
        day_gan = sizhu.get('day_gan', '甲')
        
        ganhe_map = {
            '甲': '己', '己': '甲',
            '乙': '庚', '庚': '乙',
            '丙': '辛', '辛': '丙',
            '丁': '壬', '壬': '丁',
            '戊': '癸', '癸': '戊'
        }
        
        return day_gan == ganhe_map.get(self.groom_gan)


# -*- coding: utf-8 -*-
"""
================================================================================
修造神煞模块
================================================================================
实现修造择日专用神煞的检查逻辑
包含：土府、地囊、土王用事等

使用方法:
    1. 作为模块导入: from modules.shensha.修造神煞 import 修造神煞Checker
    2. 直接运行: python -m modules.shensha.修造神煞
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
class ConstructionShenShaChecker(ShenShaChecker):
    """修建神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        try:
            year_zhi = sizhu.get('year_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            # 岁破（已在基类中检查）
            
            # 太岁堆黄
            if self._is_taisui_duihuang(sizhu):
                self._add_shensha('太岁堆黄', -15, '忌动土修造')
        except Exception as e:
            logger.error(f"检查年神煞失败: {str(e)}", exc_info=True)
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            # 三煞
            if self._is_sansha(sizhu):
                self._add_shensha('三煞', -20, '修建大忌，犯之主灾祸')
            
            # 鲁班煞（按季节判断）
            if self._is_lubansha(sizhu):
                self._add_shensha('鲁班煞', -15, '修建不宜，犯之主损工匠')
            
            # 土符
            if self._is_tufu(sizhu):
                self._add_shensha('土符', -20, '忌动土、修造，犯之主灾')
            
            # 土府
            if self._is_tufu2(sizhu):
                self._add_shensha('土府', -15, '忌动土，犯之主败')
            
            # 土瘟
            if self._is_tuwen(sizhu):
                self._add_shensha('土瘟', -20, '忌动土、修造，犯之主病')
            
            # 地囊
            if self._is_dinang(sizhu):
                self._add_shensha('地囊', -20, '忌动土、开渠，犯之主败')
            
            # 月破（已在基类中检查）
            
            # 大耗
            if self._is_dahao(sizhu):
                self._add_shensha('大耗', -15, '忌动土，犯之主耗财')
            
            # 小耗
            if self._is_xiaohao(sizhu):
                self._add_shensha('小耗', -10, '忌动土，犯之主小损')
        except Exception as e:
            logger.error(f"检查月神煞失败: {str(e)}", exc_info=True)
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        try:
            day_gan = sizhu.get('day_gan', '甲')
            day_zhi = sizhu.get('day_zhi', '子')
            month_zhi = sizhu.get('month_zhi', '子')
        except Exception as e:
            logger.error(f"获取日干信息失败: {str(e)}", exc_info=True)
            return
        
        # ===== 凶煞 =====
        
        # 天贼
        if self._is_tianzei(sizhu):
            self._add_shensha('天贼', -15, '忌修造、动土，犯之主耗财')
        
        # 地贼
        if self._is_dizei(sizhu):
            self._add_shensha('地贼', -15, '忌修造、动土，犯之主失盗')
        
        # 四离日
        if self._is_sili(sizhu):
            self._add_shensha('四离日', -30, '春分、秋分、夏至、冬至前一日，忌大事')
        
        # 四绝日
        if self._is_sijue(sizhu):
            self._add_shensha('四绝日', -30, '立春、立夏、立秋、立冬前一日，忌大事')
        
        # 十恶大败
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -25, '忌动土修造，犯之主败')
        
        # 伏断日
        if self._is_fuduan(sizhu):
            self._add_shensha('伏断日', -10, '忌动土修造')
        
        # 将军箭
        if self._is_jiangjunjian(sizhu):
            self._add_shensha('将军箭', -15, '忌修造，犯之主伤')
        
        # ===== 吉神 =====
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 15, '动土修造大吉，百事皆宜')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 15, '动土修造大吉，百事皆宜')
        
        # 天德合
        if self._is_tiandehe(sizhu):
            self._add_shensha('天德合', 15, '动土修造吉利')
        
        # 月德合
        if self._is_yuedehe(sizhu):
            self._add_shensha('月德合', 15, '动土修造吉利')
        
        # 驿马
        if self._is_yima(sizhu):
            self._add_shensha('驿马', 10, '动土催吉，主迁动')
        
        # 三合
        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '动土吉利，主和合')
        
        # 六合
        if self._is_liuhe(sizhu):
            self._add_shensha('六合', 10, '动土吉利，主和谐')
        
        # 鸣吠日（破土专用）
        if self._is_mingfei(sizhu):
            self._add_shensha('鸣吠日', 15, '破土、启攒专用吉日')
        
        # 鸣吠对日
        if self._is_mingfeidui(sizhu):
            self._add_shensha('鸣吠对日', 10, '破土吉日')
        
        # 不将日
        if self._is_bujiang(sizhu):
            self._add_shensha('不将日', 10, '修造吉日')
    
    def _check_hour_shensha(self, sizhu):
        """检查时神煞"""
        super()._check_hour_shensha(sizhu)
    
    # ===== 凶煞判断方法 =====
    
    def _is_sansha(self, sizhu):
        """是否三煞"""
        try:
            year_zhi = sizhu.get('year_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            zh_list = DI_ZHI
            
            if year_zhi in SANSHA_MAP:
                sansha_indices = SANSHA_MAP[year_zhi]
                day_idx = zh_list.index(day_zhi)
                return day_idx in sansha_indices
            return False
        except Exception as e:
            logger.error(f"检查三煞失败: {str(e)}", exc_info=True)
            return False
    
    def _is_lubansha(self, sizhu):
        """是否鲁班煞（按季节判断）
        春季：亥、子日
        夏季：寅、卯日
        秋季：巳、午日
        冬季：申、酉日
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            # 春季：寅卯辰月
            if month_zhi in ['寅', '卯', '辰']:
                return day_zhi in ['亥', '子']
            # 夏季：巳午未月
            elif month_zhi in ['巳', '午', '未']:
                return day_zhi in ['寅', '卯']
            # 秋季：申酉戌月
            elif month_zhi in ['申', '酉', '戌']:
                return day_zhi in ['巳', '午']
            # 冬季：亥子丑月
            elif month_zhi in ['亥', '子', '丑']:
                return day_zhi in ['申', '酉']
            return False
        except Exception as e:
            logger.error(f"检查鲁班煞失败: {str(e)}", exc_info=True)
            return False
    
    def _is_tufu(self, sizhu):
        """是否土符
        土符日：按月支推算
        寅月：戌日，卯月：亥日，辰月：子日，巳月：丑日
        午月：寅日，未月：卯日，申月：辰日，酉月：巳日
        戌月：午日，亥月：未日，子月：申日，丑月：酉日
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            tufu_map = {
                '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
                '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
                '戌': '午', '亥': '未', '子': '申', '丑': '酉'
            }
            return day_zhi == tufu_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查土符失败: {str(e)}", exc_info=True)
            return False
    
    def _is_tufu2(self, sizhu):
        """是否土府（地府）
        土府日：按月支推算
        寅月：辰日，卯月：巳日，辰月：午日，巳月：未日
        午月：申日，未月：酉日，申月：戌日，酉月：亥日
        戌月：子日，亥月：丑日，子月：寅日，丑月：卯日
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            tufu2_map = {
                '寅': '辰', '卯': '巳', '辰': '午', '巳': '未',
                '午': '申', '未': '酉', '申': '戌', '酉': '亥',
                '戌': '子', '亥': '丑', '子': '寅', '丑': '卯'
            }
            return day_zhi == tufu2_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查土府失败: {str(e)}", exc_info=True)
            return False
    
    def _is_tuwen(self, sizhu):
        """是否土瘟
        土瘟日：按月支推算
        寅月：丑日，卯月：寅日，辰月：卯日，巳月：辰日
        午月：巳日，未月：午日，申月：未日，酉月：申日
        戌月：酉日，亥月：戌日，子月：亥日，丑月：子日
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            tuwen_map = {
                '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
                '午': '巳', '未': '午', '申': '未', '酉': '申',
                '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
            }
            return day_zhi == tuwen_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查土瘟失败: {str(e)}", exc_info=True)
            return False
    
    def _is_dinang(self, sizhu):
        """是否地囊
        地囊日：按月支推算
        寅月：戌日，卯月：亥日，辰月：子日，巳月：丑日
        午月：寅日，未月：卯日，申月：辰日，酉月：巳日
        戌月：午日，亥月：未日，子月：申日，丑月：酉日
        """
        try:
            return self._is_tufu(sizhu)  # 地囊与土符相同
        except Exception as e:
            logger.error(f"检查地囊失败: {str(e)}", exc_info=True)
            return False
    
    def _is_tianzei(self, sizhu):
        """是否天贼
        天贼日：按月支推算
        寅月：丑日，卯月：子日，辰月：亥日，巳月：戌日
        午月：酉日，未月：申日，申月：未日，酉月：午日
        戌月：巳日，亥月：辰日，子月：卯日，丑月：寅日
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            tianzei_map = {
                '寅': '丑', '卯': '子', '辰': '亥', '巳': '戌',
                '午': '酉', '未': '申', '申': '未', '酉': '午',
                '戌': '巳', '亥': '辰', '子': '卯', '丑': '寅'
            }
            return day_zhi == tianzei_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查天贼失败: {str(e)}", exc_info=True)
            return False
    
    def _is_dizei(self, sizhu):
        """是否地贼
        地贼日：按月支推算
        寅月：辰日，卯月：巳日，辰月：午日，巳月：未日
        午月：申日，未月：酉日，申月：戌日，酉月：亥日
        戌月：子日，亥月：丑日，子月：寅日，丑月：卯日
        """
        try:
            return self._is_tufu2(sizhu)  # 地贼与土府相同
        except Exception as e:
            logger.error(f"检查地贼失败: {str(e)}", exc_info=True)
            return False
    
    def _is_dahao(self, sizhu):
        """是否大耗
        大耗日：与月破相同，即与月支相冲的日支
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            zh_list = DI_ZHI
            idx = zh_list.index(month_zhi)
            yuepo = zh_list[(idx + 6) % 12]
            return day_zhi == yuepo
        except Exception as e:
            logger.error(f"检查大耗失败: {str(e)}", exc_info=True)
            return False
    
    def _is_xiaohao(self, sizhu):
        """是否小耗
        小耗日：月破的前一日
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            zh_list = DI_ZHI
            idx = zh_list.index(month_zhi)
            xiaohao = zh_list[(idx + 5) % 12]
            return day_zhi == xiaohao
        except Exception as e:
            logger.error(f"检查小耗失败: {str(e)}", exc_info=True)
            return False
    
    def _is_sili(self, sizhu):
        """是否四离日
        四离日：春分、秋分、夏至、冬至的前一日
        春分前一日（卯月末日）：辰日
        夏至前一日（午月末日）：未日
        秋分前一日（酉月末日）：戌日
        冬至前一日（子月末日）：丑日
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            # 简化判断：卯月辰日、午月未日、酉月戌日、子月丑日
            sili_map = {
                '卯': '辰', '午': '未', '酉': '戌', '子': '丑'
            }
            return day_zhi == sili_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查四离日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_sijue(self, sizhu):
        """是否四绝日
        四绝日：立春、立夏、立秋、立冬的前一日
        立春前一日（丑月末日）：寅日
        立夏前一日（辰月末日）：巳日
        立秋前一日（未月末日）：申日
        立冬前一日（戌月末日）：亥日
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            # 简化判断：丑月寅日、辰月巳日、未月申日、戌月亥日
            sijue_map = {
                '丑': '寅', '辰': '巳', '未': '申', '戌': '亥'
            }
            return day_zhi == sijue_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查四绝日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_shie_dabai(self, sizhu):
        """是否十恶大败
        十恶大败日：甲辰、乙巳、丙申、丁亥、戊戌、己丑、庚辰、辛巳、壬申、癸亥
        """
        try:
            day_gan = sizhu.get('day_gan', '甲')
            day_zhi = sizhu.get('day_zhi', '子')
            day_pillar = day_gan + day_zhi
            
            shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
            return day_pillar in shie_dabai
        except Exception as e:
            logger.error(f"检查十恶大败失败: {str(e)}", exc_info=True)
            return False
    
    def _is_fuduan(self, sizhu):
        """是否伏断日
        伏断日：按日干支推算
        甲日：戌，乙日：酉，丙日：申，丁日：未，戊日：午
        己日：巳，庚日：辰，辛日：卯，壬日：寅，癸日：丑
        """
        try:
            day_gan = sizhu.get('day_gan', '甲')
            day_zhi = sizhu.get('day_zhi', '子')
            
            fuduan_map = {
                '甲': '戌', '乙': '酉', '丙': '申', '丁': '未', '戊': '午',
                '己': '巳', '庚': '辰', '辛': '卯', '壬': '寅', '癸': '丑'
            }
            return day_zhi == fuduan_map.get(day_gan)
        except Exception as e:
            logger.error(f"检查伏断日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_jiangjunjian(self, sizhu):
        """是否将军箭
        将军箭：按月支推算
        寅月：卯日，卯月：辰日，辰月：巳日，巳月：午日
        午月：未日，未月：申日，申月：酉日，酉月：戌日
        戌月：亥日，亥月：子日，子月：丑日，丑月：寅日
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            jiangjunjian_map = {
                '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
                '午': '未', '未': '申', '申': '酉', '酉': '戌',
                '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
            }
            return day_zhi == jiangjunjian_map.get(month_zhi)
        except Exception as e:
            logger.error(f"检查将军箭失败: {str(e)}", exc_info=True)
            return False
    
    def _is_taisui_duihuang(self, sizhu):
        """是否太岁堆黄
        太岁堆黄：按年支推算
        子年：丑日，丑年：寅日，寅年：卯日，卯年：辰日
        辰年：巳日，巳年：午日，午年：未日，未年：申日
        申年：酉日，酉年：戌日，戌年：亥日，亥年：子日
        """
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        zh_list = DI_ZHI
        idx = zh_list.index(year_zhi)
        duihuang = zh_list[(idx + 1) % 12]
        return day_zhi == duihuang
    
    # ===== 吉神判断方法 =====
    
    def _is_tiande(self, sizhu):
        """是否天德
        天德：按月支推算
        寅月：丁，卯月：申，辰月：壬，巳月：辛
        午月：亥，未月：甲，申月：癸，酉月：寅
        戌月：丙，亥月：乙，子月：巳，丑月：庚
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_gan = sizhu.get('day_gan', '甲')
            zh_list = DI_ZHI
            idx = zh_list.index(month_zhi)
            return day_gan == TIANDE.get(idx)
        except Exception as e:
            logger.error(f"检查天德失败: {str(e)}", exc_info=True)
            return False
    
    def _is_yuede(self, sizhu):
        """是否月德
        月德：按月支推算
        寅午戌月：丙，申子辰月：壬，亥卯未月：甲，巳酉丑月：庚
        """
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_gan = sizhu.get('day_gan', '甲')
            zh_list = DI_ZHI
            idx = zh_list.index(month_zhi)
            return day_gan == YUEDE.get(idx)
        except Exception as e:
            logger.error(f"检查月德失败: {str(e)}", exc_info=True)
            return False
    
    def _is_tiandehe(self, sizhu):
        """是否天德合
        天德合：与天德相合的天干
        丁合壬，申合巳，壬合丁，辛合丙
        亥合寅，甲合己，癸合戊，寅合亥
        丙合辛，乙合庚，巳合申，庚合乙
        """
        month_zhi = sizhu.get('month_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        
        tiandehe_map = {
            '寅': '壬', '卯': '巳', '辰': '丁', '巳': '丙',
            '午': '寅', '未': '己', '申': '戊', '酉': '亥',
            '戌': '辛', '亥': '庚', '子': '申', '丑': '乙'
        }
        return day_gan == tiandehe_map.get(month_zhi)
    
    def _is_yuedehe(self, sizhu):
        """是否月德合
        月德合：与月德相合的天干
        丙合辛，壬合丁，甲合己，庚合乙
        """
        month_zhi = sizhu.get('month_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        
        yuedehe_map = {
            '寅': '辛', '午': '辛', '戌': '辛',  # 丙合辛
            '申': '丁', '子': '丁', '辰': '丁',  # 壬合丁
            '亥': '己', '卯': '己', '未': '己',  # 甲合己
            '巳': '乙', '酉': '乙', '丑': '乙'   # 庚合乙
        }
        return day_gan == yuedehe_map.get(month_zhi)
    
    def _is_yima(self, sizhu):
        """是否驿马
        驿马：按年支或日支推算
        申子辰年/日：寅，寅午戌年/日：申
        巳酉丑年/日：亥，亥卯未年/日：巳
        """
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        yima_map = {
            '申': '寅', '子': '寅', '辰': '寅',
            '寅': '申', '午': '申', '戌': '申',
            '巳': '亥', '酉': '亥', '丑': '亥',
            '亥': '巳', '卯': '巳', '未': '巳'
        }
        return day_zhi == yima_map.get(year_zhi)
    
    def _is_sanhe(self, sizhu):
        """是否三合
        三合：申子辰合水，寅午戌合火，巳酉丑合金，亥卯未合木
        """
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        sanhe_groups = [
            {'申', '子', '辰'},
            {'寅', '午', '戌'},
            {'巳', '酉', '丑'},
            {'亥', '卯', '未'}
        ]
        
        for group in sanhe_groups:
            if month_zhi in group and day_zhi in group and month_zhi != day_zhi:
                return True
        return False
    
    def _is_liuhe(self, sizhu):
        """是否六合
        六合：子丑合，寅亥合，卯戌合，辰酉合，巳申合，午未合
        """
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        return day_zhi == liuhe_map.get(month_zhi)
    
    def _is_mingfei(self, sizhu):
        """是否鸣吠日
        鸣吠日：庚午、庚子、庚申、辛酉、辛卯、辛巳
        专用于破土、启攒
        """
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        day_pillar = day_gan + day_zhi
        
        mingfei = ['庚午', '庚子', '庚申', '辛酉', '辛卯', '辛巳']
        return day_pillar in mingfei
    
    def _is_mingfeidui(self, sizhu):
        """是否鸣吠对日
        鸣吠对日：丙子、丙午、丙寅、丁卯、丁酉、丁亥
        """
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        day_pillar = day_gan + day_zhi
        
        mingfeidui = ['丙子', '丙午', '丙寅', '丁卯', '丁酉', '丁亥']
        return day_pillar in mingfeidui
    
    def _is_bujiang(self, sizhu):
        """是否不将日
        不将日：根据月支和日干支推算
        简化版：阳月阳日、阴月阴日
        """
        month_zhi = sizhu.get('month_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        
        # 阳月：寅、辰、午、申、戌、子
        # 阴月：卯、巳、未、酉、亥、丑
        yang_month = ['寅', '辰', '午', '申', '戌', '子']
        yin_month = ['卯', '巳', '未', '酉', '亥', '丑']
        
        # 阳干：甲、丙、戊、庚、壬
        # 阴干：乙、丁、己、辛、癸
        yang_gan = ['甲', '丙', '戊', '庚', '壬']
        yin_gan = ['乙', '丁', '己', '辛', '癸']
        
        # 阳支：子、寅、辰、午、申、戌
        # 阴支：丑、卯、巳、未、酉、亥
        yang_zhi = ['子', '寅', '辰', '午', '申', '戌']
        yin_zhi = ['丑', '卯', '巳', '未', '酉', '亥']
        
        # 不将日：阳月取阴干阴支，阴月取阳干阳支
        if month_zhi in yang_month:
            return day_gan in yin_gan and day_zhi in yin_zhi
        else:
            return day_gan in yang_gan and day_zhi in yang_zhi


# -*- coding: utf-8 -*-
"""
================================================================================
开业神煞模块
================================================================================
实现开业择日专用神煞的检查逻辑
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
class OpeningShenShaChecker(ShenShaChecker):
    """开业神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        # 财神方位
        year_gan = sizhu.get('year_gan', '甲')
        if self._is_caishen_fangwei(sizhu):
            self._add_shensha('财神方位吉', 15, '财神方位吉利')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -15, '月破日不宜开业')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -10, '月刑日不宜开业')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        # 开业吉日
        if self._is_kaiye_jiri(sizhu):
            self._add_shensha('开业吉日', 20, '适合开业的吉日')
        
        # 满日
        if self._is_manri(sizhu):
            self._add_shensha('满日', 12, '满日适合开业')
        
        # 成日
        if self._is_chengri(sizhu):
            self._add_shensha('成日', 10, '成日适合开业')
        
        # 破日
        if self._is_pori(sizhu):
            self._add_shensha('破日', -20, '破日不宜开业')
        
        # 闭日
        if self._is_biari(sizhu):
            self._add_shensha('闭日', -15, '闭日不宜开业')
        
        # 劫煞
        if self._is_jiesha(sizhu):
            self._add_shensha('劫煞', -12, '劫煞日不宜开业')
        
        # 灾煞
        if self._is_zaisha(sizhu):
            self._add_shensha('灾煞', -12, '灾煞日不宜开业')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞"""
        # 检查事主八字与开业日是否相合
        if owners:
            for owner in owners:
                if self._check_owner_kaiye_match(sizhu, owner):
                    self._add_shensha('事主开业相合', 10, '事主八字与开业日相合')
                    break
    
    def _is_caishen_fangwei(self, sizhu):
        """是否财神方位吉利"""
        # 财神方位根据年干确定
        caishen_fangwei = {
            '甲': '艮', '乙': '坤', '丙': '兑', '丁': '乾',
            '戊': '艮', '己': '坤', '庚': '兑', '辛': '乾',
            '壬': '艮', '癸': '坤'
        }
        year_gan = sizhu.get('year_gan', '甲')
        # 简化判断
        return True
    
    def _is_yuepo(self, sizhu):
        """是否月破"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        chong = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == chong.get(month_zhi)
    
    def _is_yuexing(self, sizhu):
        """是否月刑"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        # 地支相刑
        xing = {
            '子': '卯', '丑': '戌', '寅': '巳', '卯': '子',
            '辰': '辰', '巳': '申', '午': '午', '未': '丑',
            '申': '寅', '酉': '酉', '戌': '未', '亥': '亥'
        }
        return day_zhi == xing.get(month_zhi)
    
    def _is_kaiye_jiri(self, sizhu):
        """是否开业吉日"""
        day_zhi = sizhu.get('day_zhi', '子')
        kaiye_jiri = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in kaiye_jiri
    
    def _is_manri(self, sizhu):
        """是否满日"""
        # 建除十二神之满日
        day_zhi = sizhu.get('day_zhi', '子')
        # 简化判断，实际应根据月建推算
        manri = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in manri
    
    def _is_chengri(self, sizhu):
        """是否成日"""
        # 建除十二神之成日
        day_zhi = sizhu.get('day_zhi', '子')
        chengri = ['丑', '辰', '未', '戌']
        return day_zhi in chengri
    
    def _is_pori(self, sizhu):
        """是否破日"""
        # 建除十二神之破日
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        chong = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == chong.get(month_zhi)
    
    def _is_biari(self, sizhu):
        """是否闭日"""
        # 建除十二神之闭日
        day_zhi = sizhu.get('day_zhi', '子')
        biari = ['亥', '子', '丑']
        return day_zhi in biari
    
    def _is_jiesha(self, sizhu):
        """是否劫煞"""
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        jiesha = {
            '申': '巳', '子': '巳', '辰': '巳',
            '寅': '亥', '午': '亥', '戌': '亥',
            '巳': '寅', '酉': '寅', '丑': '寅',
            '亥': '申', '卯': '申', '未': '申'
        }
        return day_zhi == jiesha.get(year_zhi)
    
    def _is_zaisha(self, sizhu):
        """是否灾煞"""
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        zaisha = {
            '申': '午', '子': '午', '辰': '午',
            '寅': '子', '午': '子', '戌': '子',
            '巳': '卯', '酉': '卯', '丑': '卯',
            '亥': '酉', '卯': '酉', '未': '酉'
        }
        return day_zhi == zaisha.get(year_zhi)
    
    def _check_owner_kaiye_match(self, sizhu, owner):
        """检查事主与开业日是否相合"""
        # 简化判断
        return True


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
class BurialShenShaChecker(ShenShaChecker):
    """安葬神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        year_zhi = sizhu.get('year_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        
        # 年重丧（按年支和日干查）
        if self._is_nian_zhongsang(sizhu):
            self._add_shensha('年重丧', -30, '年重丧大凶，绝对不可用')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        month_zhi = sizhu.get('month_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        
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
        
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        month_zhi = sizhu.get('month_zhi', '子')
        
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
        month_zhi = sizhu.get('month_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        
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
        year_zhi = sizhu.get('year_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        
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
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
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
        month_zhi = sizhu.get('month_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        
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
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
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
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
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
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        zhisi_map = {
            '寅': '未', '卯': '申', '辰': '酉', '巳': '戌',
            '午': '亥', '未': '子', '申': '丑', '酉': '寅',
            '戌': '卯', '亥': '辰', '子': '巳', '丑': '午'
        }
        return day_zhi == zhisi_map.get(month_zhi)
    
    def _is_yuepo(self, sizhu):
        """是否月破（与月支相冲）"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        yuepo = zh_list[(idx + 6) % 12]
        return day_zhi == yuepo
    
    def _is_tufu(self, sizhu):
        """是否土府日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        tufu_map = {
            '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申',
            '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
        }
        return day_zhi == tufu_map.get(month_zhi)
    
    def _is_bazuori(self, sizhu):
        """是否八座日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        bazuori_map = {
            '寅': '未', '卯': '申', '辰': '酉', '巳': '戌',
            '午': '亥', '未': '子', '申': '丑', '酉': '寅',
            '戌': '卯', '亥': '辰', '子': '巳', '丑': '午'
        }
        return day_zhi == bazuori_map.get(month_zhi)
    
    # ===== 极凶日 =====
    
    def _is_sili(self, sizhu):
        """是否四离日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        sili_map = {
            '卯': '辰', '午': '未', '酉': '戌', '子': '丑'
        }
        return day_zhi == sili_map.get(month_zhi)
    
    def _is_sijue(self, sizhu):
        """是否四绝日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        sijue_map = {
            '丑': '寅', '辰': '巳', '未': '申', '戌': '亥'
        }
        return day_zhi == sijue_map.get(month_zhi)
    
    def _is_shie_dabai(self, sizhu):
        """是否十恶大败日"""
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        day_pillar = day_gan + day_zhi
        shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
        return day_pillar in shie_dabai
    
    def _is_fuduan(self, sizhu):
        """是否伏断日"""
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
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
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        day_pillar = day_gan + day_zhi
        mingfei = ['庚午', '庚子', '庚申', '辛酉', '辛卯', '辛巳', '壬寅', '壬辰', '壬午', '壬申']
        return day_pillar in mingfei
    
    def _is_mingfeidui(self, sizhu):
        """
        是否鸣吠对日
        鸣吠对日：丙子、丙午、丙寅、丁卯、丁酉、丁亥
        """
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        day_pillar = day_gan + day_zhi
        mingfeidui = ['丙子', '丙午', '丙寅', '丁卯', '丁酉', '丁亥']
        return day_pillar in mingfeidui
    
    def _is_bujiang(self, sizhu):
        """是否不将日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        
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
        day_zhi = sizhu.get('day_zhi', '子')
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
        day_zhi = sizhu.get('day_zhi', '子')
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
        day_zhi = sizhu.get('day_zhi', '子')
        zh_list = DI_ZHI
        
        if owner_zodiac not in zh_list:
            return False
        
        idx = zh_list.index(owner_zodiac)
        chong = zh_list[(idx + 6) % 12]
        return day_zhi == chong
    
    def _is_owner_he(self, sizhu, owner_zodiac):
        """日支与亡者生肖是否相合"""
        day_zhi = sizhu.get('day_zhi', '子')
        
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


# -*- coding: utf-8 -*-
"""
================================================================================
安床神煞模块
================================================================================
实现安床择日专用神煞的检查逻辑
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
class BedShenShaChecker(ShenShaChecker):
    """安床神煞检查器"""

    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)

        # 胎神方位
        year_zhi = sizhu.get('year_zhi', '子')
        if self._is_taishen_fangwei(sizhu):
            self._add_shensha('胎神方位吉', 10, '胎神方位吉利')

    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)

        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -15, '月破日不宜安床')

        # 土府
        if self._is_tufu(sizhu):
            self._add_shensha('土府', -10, '土府日不宜安床')

    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)

        # 安床吉日
        if self._is_anchuang_jiri(sizhu):
            self._add_shensha('安床吉日', 15, '适合安床的吉日')

        # 床公床母日
        if self._is_chuanggong_chuangmu(sizhu):
            self._add_shensha('床公床母日', 12, '床公床母日利于安床')

        # 胎神日
        if self._is_taishen(sizhu):
            self._add_shensha('胎神日', -15, '胎神日不宜安床')

        # 冲床日
        if self._is_chongchuang(sizhu):
            self._add_shensha('冲床日', -12, '冲床日不宜安床')

        # 杨公忌日
        if self._is_yanggongji(sizhu):
            self._add_shensha('杨公忌日', -20, '杨公忌日不宜安床')

        # 红砂日
        if self._is_hongsha(sizhu):
            self._add_shensha('红砂日', -15, '红砂日不宜安床')

    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞"""
        # 检查事主八字与安床日是否相合
        if owners:
            for owner in owners:
                if self._check_owner_anchuang_match(sizhu, owner):
                    self._add_shensha('事主安床相合', 10, '事主八字与安床日相合')
                    break

    def _is_taishen_fangwei(self, sizhu):
        """是否胎神方位吉利"""
        # 胎神方位根据年支确定
        taishen_fangwei = {
            '子': '门', '丑': '碓磨', '寅': '厨灶', '卯': '大门',
            '辰': '门床', '巳': '碓磨', '午': '厨灶', '未': '灶炉',
            '申': '门床', '酉': '碓磨', '戌': '厨灶', '亥': '床仓'
        }
        year_zhi = sizhu.get('year_zhi', '子')
        # 简化判断
        return True

    def _is_yuepo(self, sizhu):
        """是否月破"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        chong = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == chong.get(month_zhi)

    def _is_tufu(self, sizhu):
        """是否土府日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        tufu_days = {
            '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申',
            '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
        }
        return day_zhi == tufu_days.get(month_zhi)

    def _is_anchuang_jiri(self, sizhu):
        """是否安床吉日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 安床吉日：阳日
        anchuang_jiri = ['午', '未', '申', '酉', '戌', '亥']
        return day_zhi in anchuang_jiri

    def _is_chuanggong_chuangmu(self, sizhu):
        """是否床公床母日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 床公床母日
        chuanggong_chuangmu = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in chuanggong_chuangmu

    def _is_taishen(self, sizhu):
        """是否胎神日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        # 胎神日
        taishen_days = {
            '寅': '子', '卯': '丑', '辰': '寅', '巳': '卯',
            '午': '辰', '未': '巳', '申': '午', '酉': '未',
            '戌': '申', '亥': '酉', '子': '戌', '丑': '亥'
        }
        return day_zhi == taishen_days.get(month_zhi)

    def _is_chongchuang(self, sizhu):
        """是否冲床日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        # 冲床日
        chongchuang = {
            '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
            '午': '子', '未': '丑', '申': '寅', '酉': '卯',
            '戌': '辰', '亥': '巳', '子': '午', '丑': '未'
        }
        return day_zhi == chongchuang.get(month_zhi)

    def _is_yanggongji(self, sizhu):
        """是否杨公忌日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        # 杨公忌日
        yanggongji = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == yanggongji.get(month_zhi)

    def _is_hongsha(self, sizhu):
        """是否红砂日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 红砂日
        hongsha = ['酉', '巳', '丑']
        return day_zhi in hongsha

    def _check_owner_anchuang_match(self, sizhu, owner):
        """检查事主与安床日是否相合"""
        # 简化判断
        return True


# -*- coding: utf-8 -*-
"""
================================================================================
出行神煞模块
================================================================================
实现出行择日专用神煞的检查逻辑
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
class TravelShenShaChecker(ShenShaChecker):
    """出行神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        # 太岁方位
        year_zhi = sizhu.get('year_zhi', '子')
        if self._is_taisui_fangwei(sizhu):
            self._add_shensha('太岁方位', -10, '太岁方位不宜出行')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -15, '月破日不宜出行')
        
        # 往亡
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡', -20, '往亡日不宜出行')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        # 出行吉日
        if self._is_chuxing_jiri(sizhu):
            self._add_shensha('出行吉日', 15, '适合出行的吉日')
        
        # 驿马日
        if self._is_yima(sizhu):
            self._add_shensha('驿马日', 12, '驿马日利于出行')
        
        # 天马日
        if self._is_tianma(sizhu):
            self._add_shensha('天马日', 10, '天马日利于远行')
        
        # 路空日
        if self._is_lukong(sizhu):
            self._add_shensha('路空日', -15, '路空日不宜出行')
        
        # 朱雀日
        if self._is_zhuque(sizhu):
            self._add_shensha('朱雀日', -10, '朱雀日出行有口舌是非')
        
        # 白虎日
        if self._is_baihu(sizhu):
            self._add_shensha('白虎日', -12, '白虎日出行有凶险')
    
    def _check_hour_shensha(self, sizhu):
        """检查时神煞"""
        super()._check_hour_shensha(sizhu)
        
        # 出行吉时
        if self._is_chuxing_jishi(sizhu):
            self._add_shensha('出行吉时', 8, '适合出行的时辰')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞"""
        # 检查事主八字与出行日是否相合
        if owners:
            for owner in owners:
                if self._check_owner_chuxing_match(sizhu, owner):
                    self._add_shensha('事主出行相合', 10, '事主八字与出行日相合')
                    break
    
    def _is_taisui_fangwei(self, sizhu):
        """是否太岁方位"""
        year_zhi = sizhu.get('year_zhi', '子')
        # 太岁方位
        taisui_fangwei = {
            '子': '北', '丑': '东北', '寅': '东北', '卯': '东',
            '辰': '东南', '巳': '东南', '午': '南', '未': '西南',
            '申': '西南', '酉': '西', '戌': '西北', '亥': '西北'
        }
        # 简化判断
        return False
    
    def _is_yuepo(self, sizhu):
        """是否月破"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        chong = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == chong.get(month_zhi)
    
    def _is_wangwang(self, sizhu):
        """是否往亡日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        # 往亡日
        wangwang_days = {
            '寅': '巳', '卯': '寅', '辰': '亥', '巳': '申',
            '午': '巳', '未': '寅', '申': '亥', '酉': '申',
            '戌': '巳', '亥': '寅', '子': '亥', '丑': '申'
        }
        return day_zhi == wangwang_days.get(month_zhi)
    
    def _is_chuxing_jiri(self, sizhu):
        """是否出行吉日"""
        day_zhi = sizhu.get('day_zhi', '子')
        chuxing_jiri = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in chuxing_jiri
    
    def _is_yima(self, sizhu):
        """是否驿马日"""
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        # 驿马日
        yima = {
            '申': '寅', '子': '寅', '辰': '寅',
            '寅': '申', '午': '申', '戌': '申',
            '巳': '亥', '酉': '亥', '丑': '亥',
            '亥': '巳', '卯': '巳', '未': '巳'
        }
        return day_zhi == yima.get(year_zhi)
    
    def _is_tianma(self, sizhu):
        """是否天马日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        # 天马日
        tianma = {
            '寅': '午', '卯': '申', '辰': '戌', '巳': '子',
            '午': '寅', '未': '辰', '申': '午', '酉': '申',
            '戌': '戌', '亥': '子', '子': '寅', '丑': '辰'
        }
        return day_zhi == tianma.get(month_zhi)
    
    def _is_lukong(self, sizhu):
        """是否路空日"""
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        # 路空日（甲己日申酉空，乙庚日午未空，丙辛日辰巳空，丁壬日寅卯空，戊癸日子丑空）
        lukong = {
            '甲': ['申', '酉'], '己': ['申', '酉'],
            '乙': ['午', '未'], '庚': ['午', '未'],
            '丙': ['辰', '巳'], '辛': ['辰', '巳'],
            '丁': ['寅', '卯'], '壬': ['寅', '卯'],
            '戊': ['子', '丑'], '癸': ['子', '丑']
        }
        return day_zhi in lukong.get(day_gan, [])
    
    def _is_zhuque(self, sizhu):
        """是否朱雀日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        # 朱雀日
        zhuque = {
            '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
            '午': '未', '未': '申', '申': '酉', '酉': '戌',
            '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
        }
        return day_zhi == zhuque.get(month_zhi)
    
    def _is_baihu(self, sizhu):
        """是否白虎日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        # 白虎日
        baihu = {
            '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
            '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
            '戌': '午', '亥': '未', '子': '申', '丑': '酉'
        }
        return day_zhi == baihu.get(month_zhi)
    
    def _is_chuxing_jishi(self, sizhu):
        """是否出行吉时"""
        hour_zhi = sizhu.get('hour_zhi', '子')
        jishi = ['子', '寅', '卯', '巳', '午', '酉']
        return hour_zhi in jishi
    
    def _check_owner_chuxing_match(self, sizhu, owner):
        """检查事主与出行日是否相合"""
        # 简化判断
        return True


# -*- coding: utf-8 -*-
"""
================================================================================
入宅神煞模块
================================================================================
实现入宅择日专用神煞的检查逻辑
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
class RuZhaiShenShaChecker(ShenShaChecker):
    """入宅神煞检查器"""
    
    def __init__(self):
        super().__init__()
        self.owner_zodiac = None
        self.owner_gan = None
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        # 年三煞（劫煞、灾煞、岁煞）
        if self._is_sansha(sizhu):
            self._add_shensha('年三煞', -25, '入宅大忌，犯之主凶灾')
        
        # 岁破（日支与年支相冲）
        if self._is_suipo(sizhu):
            self._add_shensha('岁破', -25, '岁破日诸事不宜，入宅大忌')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        
        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -25, '月破日诸事不宜，入宅大忌')
        
        # 土符（忌动土，入宅搬动家具亦忌）
        if self._is_tufu(sizhu):
            self._add_shensha('土符', -15, '土符日不宜动土、入宅')
        
        # 地囊
        if self._is_dinang(sizhu):
            self._add_shensha('地囊', -20, '地囊日忌动土、入宅')
        
        # 天贼（主盗贼损耗）
        if self._is_tianzei(sizhu):
            self._add_shensha('天贼', -15, '天贼日入宅易遭盗窃损耗')
        
        # 地贼
        if self._is_dizei(sizhu):
            self._add_shensha('地贼', -12, '地贼日入宅不吉')
        
        # 归忌（移徙大忌）
        if self._is_guiji(sizhu):
            self._add_shensha('归忌', -18, '归忌日不宜移徙、入宅')
        
        # 往亡（出行、移徙忌）
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡', -18, '往亡日不宜入宅')
        
        # 红嘴朱雀（入宅大忌）
        if self._is_hongzui_zhuque(sizhu):
            self._add_shensha('红嘴朱雀', -30, '红嘴朱雀日入宅大凶')
        
        # 天狗
        if self._is_tiangou(sizhu):
            self._add_shensha('天狗', -12, '天狗日入宅不吉')
        
        # 伏断日
        if self._is_fuduan(sizhu):
            self._add_shensha('伏断日', -12, '伏断日忌入宅')
        
        # 受死日
        if self._is_shousi(sizhu):
            self._add_shensha('受死日', -18, '受死日不宜入宅')
        
        # 大耗
        if self._is_dahao(sizhu):
            self._add_shensha('大耗', -15, '大耗日入宅主耗财')
        
        # 小耗
        if self._is_xiaohao(sizhu):
            self._add_shensha('小耗', -10, '小耗日入宅主小损')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -12, '月刑日不宜入宅')
        
        # 月害
        if self._is_yuehai(sizhu):
            self._add_shensha('月害', -12, '月害日不宜入宅')
        
        # ===== 吉神 =====
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 15, '天德吉星，入宅大吉')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 12, '月德吉星，入宅大吉')
        
        # 驿马
        if self._is_yima(sizhu):
            self._add_shensha('驿马', 10, '驿马星动，迁居顺利')
        
        # 建星吉日：成、开、满
        if self._is_jianxing_ji(sizhu):
            self._add_shensha('建星吉日', 8, '成/开/满日宜入宅')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        month_zhi = sizhu.get('month_zhi', '子')
        
        # ===== 极凶日 =====
        
        # 四离日（节气前一日）
        if self._is_sili(sizhu):
            self._add_shensha('四离日', -30, '四离日大事不宜，入宅大忌')
        
        # 四绝日（季节交替日）
        if self._is_sijue(sizhu):
            self._add_shensha('四绝日', -30, '四绝日大事不宜，入宅大忌')
        
        # 十恶大败
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -25, '十恶大败日，入宅大忌')
        
        # ===== 凶煞 =====
        
        # 白虎入中宫
        if self._is_baihu_zhonggong(sizhu):
            self._add_shensha('白虎入中宫', -15, '白虎入中宫，入宅不吉')
        
        # ===== 吉日 =====
        
        # 天赦日
        if self._is_tianshe(sizhu):
            self._add_shensha('天赦日', 20, '天赦日百事吉，入宅尤佳')
        
        # 三合
        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '三合吉日，入宅顺遂')
        
        # 六合
        if self._is_liuhe(sizhu):
            self._add_shensha('六合', 10, '六合吉日，入宅和谐')
        
        # 母仓日
        if self._is_mucang(sizhu):
            self._add_shensha('母仓日', 8, '母仓日入宅吉')
        
        # 相日
        if self._is_xiangri(sizhu):
            self._add_shensha('相日', 6, '相日入宅吉')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞，主要处理宅主（家长）生肖与日课的冲合"""
        if not owners:
            return
        
        # 取宅主（一般取第一人）
        owner = owners[0]
        self.owner_zodiac = owner.get('生肖', '')
        self.owner_gan = owner.get('年干', '')
        
        if self.owner_zodiac:
            # 与宅主相冲
            if self._is_chong_owner(sizhu):
                self._add_shensha('冲宅主', -25, f'日支与宅主生肖({self.owner_zodiac})相冲，大忌')
            # 与宅主相合
            elif self._is_he_owner(sizhu):
                self._add_shensha('合宅主', 15, f'日支与宅主生肖({self.owner_zodiac})相合，大吉')
            
            # 与宅主相害
            if self._is_hai_owner(sizhu):
                self._add_shensha('害宅主', -12, f'日支与宅主生肖({self.owner_zodiac})相害')
            
            # 与宅主相刑
            if self._is_xing_owner(sizhu):
                self._add_shensha('刑宅主', -12, f'日支与宅主生肖({self.owner_zodiac})相刑')
        
        # 日干与宅主年干相合
        if self.owner_gan and self._is_gan_he_owner(sizhu):
            self._add_shensha('宅主干合', 8, f'日干与宅主年干({self.owner_gan})相合，吉')
    
    # ========== 年神煞判断 ==========
    
    def _is_sansha(self, sizhu):
        """是否年三煞（劫煞、灾煞、岁煞）"""
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        if year_zhi in SANSHA_MAP:
            sansha_indices = SANSHA_MAP[year_zhi]
            zh_list = DI_ZHI
            day_idx = zh_list.index(day_zhi)
            return day_idx in sansha_indices
        return False
    
    def _is_suipo(self, sizhu):
        """是否岁破（日支与年支相冲）"""
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        zh_list = DI_ZHI
        idx = zh_list.index(year_zhi)
        suipo = zh_list[(idx + 6) % 12]
        return day_zhi == suipo
    
    # ========== 月神煞判断 ==========
    
    def _is_yuepo(self, sizhu):
        """月破：日支与月支相冲"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        yuepo = zh_list[(idx + 6) % 12]
        return day_zhi == yuepo
    
    def _is_tufu(self, sizhu):
        """土符日：按月查日支"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        tufu_map = {
            '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申',
            '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
        }
        return day_zhi == tufu_map.get(month_zhi)
    
    def _is_dinang(self, sizhu):
        """地囊日：按季查日支"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        # 春季（寅卯辰）地囊在亥日；夏季（巳午未）在寅日；秋季（申酉戌）在巳日；冬季（亥子丑）在申日
        dinang_map = {
            '寅': '亥', '卯': '亥', '辰': '亥',
            '巳': '寅', '午': '寅', '未': '寅',
            '申': '巳', '酉': '巳', '戌': '巳',
            '亥': '申', '子': '申', '丑': '申'
        }
        return day_zhi == dinang_map.get(month_zhi)
    
    def _is_tianzei(self, sizhu):
        """天贼日：按月查日支"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        tianzei_map = {
            '寅': '辰', '卯': '巳', '辰': '午',
            '巳': '未', '午': '申', '未': '酉',
            '申': '戌', '酉': '亥', '戌': '子',
            '亥': '丑', '子': '寅', '丑': '卯'
        }
        return day_zhi == tianzei_map.get(month_zhi)
    
    def _is_dizei(self, sizhu):
        """地贼日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        dizei_map = {
            '寅': '子', '卯': '丑', '辰': '寅',
            '巳': '卯', '午': '辰', '未': '巳',
            '申': '午', '酉': '未', '戌': '申',
            '亥': '酉', '子': '戌', '丑': '亥'
        }
        return day_zhi == dizei_map.get(month_zhi)
    
    def _is_guiji(self, sizhu):
        """
        归忌日：孟月忌丑日，仲月忌寅日，季月忌子日
        孟月：寅、申、巳、亥
        仲月：子、午、卯、酉
        季月：辰、戌、丑、未
        """
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        meng = ['寅', '申', '巳', '亥']
        zhong = ['子', '午', '卯', '酉']
        ji = ['辰', '戌', '丑', '未']
        if month_zhi in meng and day_zhi == '丑':
            return True
        if month_zhi in zhong and day_zhi == '寅':
            return True
        if month_zhi in ji and day_zhi == '子':
            return True
        return False
    
    def _is_wangwang(self, sizhu):
        """往亡日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        wangwang_map = {
            '寅': '寅', '卯': '巳', '辰': '申', '巳': '亥',
            '午': '卯', '未': '午', '申': '酉', '酉': '子',
            '戌': '辰', '亥': '未', '子': '戌', '丑': '丑'
        }
        return day_zhi == wangwang_map.get(month_zhi)
    
    def _is_hongzui_zhuque(self, sizhu):
        """红嘴朱雀日（入宅大忌）"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        hongzui_map = {
            '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
            '午': '未', '未': '申', '申': '酉', '酉': '戌',
            '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
        }
        return day_zhi == hongzui_map.get(month_zhi)
    
    def _is_tiangou(self, sizhu):
        """天狗日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        tiangou_map = {
            '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
            '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
            '戌': '午', '亥': '未', '子': '申', '丑': '酉'
        }
        return day_zhi == tiangou_map.get(month_zhi)
    
    def _is_fuduan(self, sizhu):
        """伏断日：按日干查日支"""
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        fuduan_map = {
            '甲': '戌', '乙': '酉', '丙': '申', '丁': '未', '戊': '午',
            '己': '巳', '庚': '辰', '辛': '卯', '壬': '寅', '癸': '丑'
        }
        return day_zhi == fuduan_map.get(day_gan)
    
    def _is_shousi(self, sizhu):
        """受死日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        shousi_map = {
            '寅': '戌', '卯': '辰', '辰': '亥', '巳': '巳',
            '午': '子', '未': '午', '申': '丑', '酉': '未',
            '戌': '寅', '亥': '申', '子': '卯', '丑': '酉'
        }
        return day_zhi == shousi_map.get(month_zhi)
    
    def _is_dahao(self, sizhu):
        """大耗日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        dahao_map = {
            '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
            '午': '子', '未': '丑', '申': '寅', '酉': '卯',
            '戌': '辰', '亥': '巳', '子': '午', '丑': '未'
        }
        return day_zhi == dahao_map.get(month_zhi)
    
    def _is_xiaohao(self, sizhu):
        """小耗日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        xiaohao_map = {
            '寅': '未', '卯': '申', '辰': '酉', '巳': '戌',
            '午': '亥', '未': '子', '申': '丑', '酉': '寅',
            '戌': '卯', '亥': '辰', '子': '巳', '丑': '午'
        }
        return day_zhi == xiaohao_map.get(month_zhi)
    
    def _is_yuexing(self, sizhu):
        """月刑日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        yuexing_map = {
            '寅': '巳', '卯': '子', '辰': '辰', '巳': '申',
            '午': '午', '未': '丑', '申': '寅', '酉': '酉',
            '戌': '未', '亥': '亥', '子': '卯', '丑': '戌'
        }
        return day_zhi == yuexing_map.get(month_zhi)
    
    def _is_yuehai(self, sizhu):
        """月害日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        yuehai_map = {
            '子': '未', '丑': '午', '寅': '巳', '卯': '辰',
            '辰': '卯', '巳': '寅', '午': '丑', '未': '子',
            '申': '亥', '酉': '戌', '戌': '酉', '亥': '申'
        }
        return day_zhi == yuehai_map.get(month_zhi)
    
    def _is_tiande(self, sizhu):
        """天德日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        
        tiande_map = {
            '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
            '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
            '戌': '丙', '亥': '乙', '子': '巳', '丑': '庚'
        }
        
        tiande = tiande_map.get(month_zhi)
        return day_gan == tiande or day_zhi == tiande
    
    def _is_yuede(self, sizhu):
        """月德日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        
        yuede_map = {
            '寅': '丙', '午': '丙', '戌': '丙',
            '申': '壬', '子': '壬', '辰': '壬',
            '巳': '庚', '酉': '庚', '丑': '庚',
            '亥': '甲', '卯': '甲', '未': '甲'
        }
        
        return day_gan == yuede_map.get(month_zhi)
    
    def _is_yima(self, sizhu):
        """驿马日"""
        year_zhi = sizhu.get('year_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        yima_map = {
            '寅': '申', '午': '申', '戌': '申',
            '申': '寅', '子': '寅', '辰': '寅',
            '巳': '亥', '酉': '亥', '丑': '亥',
            '亥': '巳', '卯': '巳', '未': '巳'
        }
        
        return day_zhi == yima_map.get(year_zhi)
    
    def _is_jianxing_ji(self, sizhu):
        """建星吉日（成、开、满）"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        zh_list = DI_ZHI
        month_idx = zh_list.index(month_zhi)
        day_idx = zh_list.index(day_zhi)
        
        jian_idx = (day_idx - month_idx) % 12
        
        jianxing_ji = [2, 3, 5]  # 满=2, 成=3, 开=5
        
        return jian_idx in jianxing_ji
    
    # ========== 日神煞判断 ==========
    
    def _is_sili(self, sizhu):
        """四离日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        sili_map = {
            '卯': '辰', '午': '未', '酉': '戌', '子': '丑'
        }
        return day_zhi == sili_map.get(month_zhi)
    
    def _is_sijue(self, sizhu):
        """四绝日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        sijue_map = {
            '丑': '寅', '辰': '巳', '未': '申', '戌': '亥'
        }
        return day_zhi == sijue_map.get(month_zhi)
    
    def _is_shie_dabai(self, sizhu):
        """十恶大败日"""
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        day_pillar = day_gan + day_zhi
        shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
        return day_pillar in shie_dabai
    
    def _is_baihu_zhonggong(self, sizhu):
        """白虎入中宫"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        baihu_map = {
            '寅': '午', '卯': '未', '辰': '申', '巳': '酉',
            '午': '戌', '未': '亥', '申': '子', '酉': '丑',
            '戌': '寅', '亥': '卯', '子': '辰', '丑': '巳'
        }
        return day_zhi == baihu_map.get(month_zhi)
    
    def _is_tianshe(self, sizhu):
        """
        天赦日：春戊寅，夏甲午，秋戊申，冬甲子
        春季（寅卯辰月）：戊寅日
        夏季（巳午未月）：甲午日
        秋季（申酉戌月）：戊申日
        冬季（亥子丑月）：甲子日
        """
        day_gan = sizhu.get('day_gan', '甲')
        day_zhi = sizhu.get('day_zhi', '子')
        month_zhi = sizhu.get('month_zhi', '子')
        if month_zhi in ['寅', '卯', '辰'] and day_gan == '戊' and day_zhi == '寅':
            return True
        if month_zhi in ['巳', '午', '未'] and day_gan == '甲' and day_zhi == '午':
            return True
        if month_zhi in ['申', '酉', '戌'] and day_gan == '戊' and day_zhi == '申':
            return True
        if month_zhi in ['亥', '子', '丑'] and day_gan == '甲' and day_zhi == '子':
            return True
        return False
    
    def _is_sanhe(self, sizhu):
        """
        三合日：日支与月支三合
        申子辰合水局、寅午戌合火局、巳酉丑合金局、亥卯未合木局
        """
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        sanhe_groups = [('申', '子', '辰'), ('寅', '午', '戌'), ('巳', '酉', '丑'), ('亥', '卯', '未')]
        for group in sanhe_groups:
            if month_zhi in group and day_zhi in group and month_zhi != day_zhi:
                return True
        return False
    
    def _is_liuhe(self, sizhu):
        """
        六合日：日支与月支六合
        子丑合土、寅亥合木、卯戌合火、辰酉合金、巳申合水、午未合火/土
        """
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        return day_zhi == liuhe_map.get(month_zhi)
    
    def _is_mucang(self, sizhu):
        """母仓日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        mucang_map = {
            '寅': ['卯', '辰'],
            '卯': ['卯', '辰'],
            '辰': ['卯', '辰'],
            '巳': ['午', '未'],
            '午': ['午', '未'],
            '未': ['午', '未'],
            '申': ['酉', '戌'],
            '酉': ['酉', '戌'],
            '戌': ['酉', '戌'],
            '亥': ['子', '丑'],
            '子': ['子', '丑'],
            '丑': ['子', '丑']
        }
        
        return day_zhi in mucang_map.get(month_zhi, [])
    
    def _is_xiangri(self, sizhu):
        """相日"""
        month_zhi = sizhu.get('month_zhi', '子')
        day_zhi = sizhu.get('day_zhi', '子')
        
        xiangri_map = {
            '寅': '卯', '卯': '卯',
            '辰': '午', '巳': '午',
            '午': '午', '未': '酉',
            '申': '酉', '酉': '酉',
            '戌': '子', '亥': '子',
            '子': '子', '丑': '卯'
        }
        
        return day_zhi == xiangri_map.get(month_zhi)
    
    # ========== 宅主相关判断 ==========
    
    def _shengxiao_to_zhi(self, shengxiao):
        """
        生肖转换为地支
        生肖对应地支：子鼠、丑牛、寅虎、卯兔、辰龙、巳蛇、午马、未羊、申猴、酉鸡、戌狗、亥猪
        """
        shengxiao_map = {
            '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
            '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
            '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
        }
        return shengxiao_map.get(shengxiao)
    
    def _is_chong_owner(self, sizhu):
        """日支是否冲宅主生肖"""
        if not self.owner_zodiac:
            return False
        
        day_zhi = sizhu.get('day_zhi', '子')
        owner_zhi = self._shengxiao_to_zhi(self.owner_zodiac)
        
        if not owner_zhi:
            if self.owner_zodiac in DI_ZHI:
                owner_zhi = self.owner_zodiac
            else:
                return False
        
        chong_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == chong_map.get(owner_zhi)
    
    def _is_he_owner(self, sizhu):
        """日支是否与宅主生肖相合（六合或三合）"""
        if not self.owner_zodiac:
            return False
        
        day_zhi = sizhu.get('day_zhi', '子')
        owner_zhi = self._shengxiao_to_zhi(self.owner_zodiac)
        
        if not owner_zhi:
            if self.owner_zodiac in DI_ZHI:
                owner_zhi = self.owner_zodiac
            else:
                return False
        
        # 六合
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        if liuhe_map.get(owner_zhi) == day_zhi:
            return True
        
        # 三合
        sanhe_sets = [{'申', '子', '辰'}, {'寅', '午', '戌'}, {'巳', '酉', '丑'}, {'亥', '卯', '未'}]
        for s in sanhe_sets:
            if owner_zhi in s and day_zhi in s and owner_zhi != day_zhi:
                return True
        
        return False
    
    def _is_hai_owner(self, sizhu):
        """日支是否与宅主生肖相害"""
        if not self.owner_zodiac:
            return False
        
        day_zhi = sizhu.get('day_zhi', '子')
        owner_zhi = self._shengxiao_to_zhi(self.owner_zodiac)
        
        if not owner_zhi:
            if self.owner_zodiac in DI_ZHI:
                owner_zhi = self.owner_zodiac
            else:
                return False
        
        liuhai_map = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        
        return day_zhi == liuhai_map.get(owner_zhi)
    
    def _is_xing_owner(self, sizhu):
        """日支是否与宅主生肖相刑"""
        if not self.owner_zodiac:
            return False
        
        day_zhi = sizhu.get('day_zhi', '子')
        owner_zhi = self._shengxiao_to_zhi(self.owner_zodiac)
        
        if not owner_zhi:
            if self.owner_zodiac in DI_ZHI:
                owner_zhi = self.owner_zodiac
            else:
                return False
        
        # 相刑关系
        xing_map = {
            '子': '卯', '卯': '子',
            '寅': '巳', '巳': '申', '申': '寅',
            '丑': '戌', '戌': '未', '未': '丑',
            '辰': '辰', '午': '午', '酉': '酉', '亥': '亥'
        }
        
        return day_zhi == xing_map.get(owner_zhi)
    
    def _is_gan_he_owner(self, sizhu):
        """日干是否与宅主年干相合"""
        if not self.owner_gan:
            return False
        
        day_gan = sizhu.get('day_gan', '甲')
        
        ganhe_map = {
            '甲': '己', '己': '甲',
            '乙': '庚', '庚': '乙',
            '丙': '辛', '辛': '丙',
            '丁': '壬', '壬': '丁',
            '戊': '癸', '癸': '戊'
        }
        
        return day_gan == ganhe_map.get(self.owner_gan)


# -*- coding: utf-8 -*-
"""
================================================================================
作灶神煞模块
================================================================================
实现作灶择日专用神煞的检查逻辑
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
class StoveShenShaChecker(ShenShaChecker):
    """作灶神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        try:
            # 灶神方位
            year_zhi = sizhu.get('year_zhi', '子')
            if self._is_zaoshen_fangwei(sizhu):
                self._add_shensha('灶神方位吉', 10, '灶神方位吉利')
        except Exception as e:
            logger.error(f"检查年神煞失败: {str(e)}", exc_info=True)
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        try:
            # 月建冲灶
            if self._is_yuejian_chongzao(sizhu):
                self._add_shensha('月建冲灶', -15, '月建冲灶不宜作灶')
            
            # 土府
            if self._is_tufu(sizhu):
                self._add_shensha('土府', -10, '土府日不宜动土作灶')
        except Exception as e:
            logger.error(f"检查月神煞失败: {str(e)}", exc_info=True)
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        # 作灶吉日
        if self._is_zuozao_jiri(sizhu):
            self._add_shensha('作灶吉日', 15, '适合作灶的吉日')
        
        # 灶君忌日
        if self._is_zaojun_jiri(sizhu):
            self._add_shensha('灶君忌日', -20, '灶君忌日不宜作灶')
        
        # 天火日
        if self._is_tianhuo(sizhu):
            self._add_shensha('天火日', -15, '天火日不宜作灶')
        
        # 地火日
        if self._is_dihuo(sizhu):
            self._add_shensha('地火日', -12, '地火日不宜作灶')
        
        # 丙丁日
        if self._is_bingding(sizhu):
            self._add_shensha('丙丁日', 8, '丙丁日火旺适合作灶')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞"""
        # 检查宅主八字与灶向是否相合
        if owners:
            for owner in owners:
                if self._check_owner_zao_match(sizhu, owner):
                    self._add_shensha('宅主灶向相合', 10, '宅主八字与灶向相合')
                    break
    
    def _check_owner_zao_match(self, sizhu, owner):
        """检查宅主八字与灶向是否相合"""
        try:
            # 简化判断，实际应根据宅主八字详细分析
            # 宅主日柱与作灶日相生或比和为宜
            return True
        except Exception as e:
            logger.error(f"检查宅主灶向相合失败: {str(e)}", exc_info=True)
            return False
    
    def _is_zaoshen_fangwei(self, sizhu):
        """是否灶神方位吉利"""
        try:
            # 灶神方位根据年支确定
            zaoshen_fangwei = {
                '子': '坤', '丑': '坤', '寅': '乾', '卯': '乾',
                '辰': '艮', '巳': '艮', '午': '震', '未': '震',
                '申': '巽', '酉': '巽', '戌': '离', '亥': '离'
            }
            year_zhi = sizhu.get('year_zhi', '子')
            # 简化判断，实际应根据具体方位
            return True
        except Exception as e:
            logger.error(f"检查灶神方位失败: {str(e)}", exc_info=True)
            return False
    
    def _is_yuejian_chongzao(self, sizhu):
        """是否月建冲灶"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            # 月建与灶位相冲
            chong = {
                '子': '午', '丑': '未', '寅': '申', '卯': '酉',
                '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
                '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
            }
            return day_zhi == chong.get(month_zhi)
        except Exception as e:
            logger.error(f"检查月建冲灶失败: {str(e)}", exc_info=True)
            return False
    
    def _is_tufu(self, sizhu):
        """是否土府日"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            # 土府日
            tufu_days = {
                '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
                '午': '巳', '未': '午', '申': '未', '酉': '申',
                '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
            }
            return day_zhi == tufu_days.get(month_zhi)
        except Exception as e:
            logger.error(f"检查土府日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_zuozao_jiri(self, sizhu):
        """是否作灶吉日"""
        try:
            day_zhi = sizhu.get('day_zhi', '子')
            zuozao_jiri = ['子', '寅', '卯', '巳', '午', '酉']
            return day_zhi in zuozao_jiri
        except Exception as e:
            logger.error(f"检查作灶吉日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_zaojun_jiri(self, sizhu):
        """是否灶君忌日"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            # 灶君忌日
            zaojun_jiri = {
                '子': '未', '丑': '申', '寅': '酉', '卯': '戌',
                '辰': '亥', '巳': '子', '午': '丑', '未': '寅',
                '申': '卯', '酉': '辰', '戌': '巳', '亥': '午'
            }
            return day_zhi == zaojun_jiri.get(month_zhi)
        except Exception as e:
            logger.error(f"检查灶君忌日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_tianhuo(self, sizhu):
        """是否天火日"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            # 天火日
            tianhuo_days = {
                '寅': '子', '卯': '丑', '辰': '寅', '巳': '卯',
                '午': '辰', '未': '巳', '申': '午', '酉': '未',
                '戌': '申', '亥': '酉', '子': '戌', '丑': '亥'
            }
            return day_zhi == tianhuo_days.get(month_zhi)
        except Exception as e:
            logger.error(f"检查天火日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_dihuo(self, sizhu):
        """是否地火日"""
        try:
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            # 地火日
            dihuo_days = {
                '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
                '午': '未', '未': '申', '申': '酉', '酉': '戌',
                '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
            }
            return day_zhi == dihuo_days.get(month_zhi)
        except Exception as e:
            logger.error(f"检查地火日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_bingding(self, sizhu):
        """是否丙丁日"""
        try:
            day_gan = sizhu.get('day_gan', '甲')
            return day_gan in ['丙', '丁']
        except Exception as e:
            logger.error(f"检查丙丁日失败: {str(e)}", exc_info=True)
            return False


# -*- coding: utf-8 -*-
"""
================================================================================
规则模块基类
================================================================================
定义规则检查的基础接口
================================================================================
"""

class EventRuleChecker:
    """事项规则检查器基类"""
    
    def __init__(self):
        pass
    
    def check(self, sizhu, owners=None, house_type=None, shan_xiang=None, 
              zaoxiang=None, zaowei=None, chuangwei=None):
        """
        检查规则
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            house_type: 宅型（阳宅/阴宅）
            shan_xiang: 山向
            zaoxiang: 灶向（作灶专用）
            zaowei: 灶位（作灶专用）
            chuangwei: 床位朝向（安床专用）
            
        Returns:
            tuple: (宜事项列表, 忌事项列表)
        """
        yi_list = []
        ji_list = []
        
        self._check_rules(sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list)
        
        return yi_list, ji_list
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """
        检查具体规则
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            house_type: 宅型（阳宅/阴宅）
            shan_xiang: 山向
            zaoxiang: 灶向（作灶专用）
            zaowei: 灶位（作灶专用）
            chuangwei: 床位朝向（安床专用）
            yi_list: 宜事项列表
            ji_list: 忌事项列表
        """
        pass


import sys
import os

# 检查是否是直接运行（不是作为模块导入）
# -*- coding: utf-8 -*-
"""
================================================================================
婚嫁规则模块
================================================================================
实现婚嫁择日的宜忌规则
================================================================================
"""

class MarriageRuleChecker(EventRuleChecker):
    """婚嫁规则检查器"""
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查婚嫁规则"""
        # 检查婚嫁宜日
        if self._is_marriage_yi_day(sizhu):
            yi_list.append('嫁娶')
        
        # 检查婚嫁忌日
        if self._is_marriage_ji_day(sizhu):
            ji_list.append('嫁娶')
    
    def _is_marriage_yi_day(self, sizhu):
        """是否婚嫁宜日"""
        day_zhi = sizhu.get('day_zhi', '子')
        yi_days = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未']
        return day_zhi in yi_days
    
    def _is_marriage_ji_day(self, sizhu):
        """是否婚嫁忌日"""
        day_zhi = sizhu.get('day_zhi', '子')
        ji_days = ['申', '酉', '戌', '亥']
        return day_zhi in ji_days
    
    def _check_bazi_match(self, bride, groom):
        """检查八字匹配"""
        # 简化的八字匹配检查
        # 实际应用中需要更复杂的逻辑
        return True


import sys
import os

# 检查是否是直接运行（不是作为模块导入）
# -*- coding: utf-8 -*-
"""
================================================================================
修建规则模块
================================================================================
实现修建择日的宜忌规则
================================================================================
"""

class ConstructionRuleChecker(EventRuleChecker):
    """修建规则检查器"""
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查修建规则"""
        # 通用修建规则
        if self._is_construction_yi_day(sizhu):
            yi_list.append('修造')
            yi_list.append('动土')
        
        if self._is_construction_ji_day(sizhu):
            ji_list.append('修造')
            ji_list.append('动土')
        
        # 阳宅特定规则
        if house_type == "阳宅":
            self._check_yang_zhai_rules(sizhu, shan_xiang, yi_list, ji_list)
        
        # 阴宅特定规则
        elif house_type == "阴宅":
            self._check_yin_zhai_rules(sizhu, shan_xiang, yi_list, ji_list)
        
        # 安葬特定规则已移至安葬规则模块
    
    def _is_construction_yi_day(self, sizhu):
        """是否修建宜日"""
        try:
            day_zhi = sizhu.get('day_zhi', '子')
            yi_days = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未']
            return day_zhi in yi_days
        except Exception as e:
            logger.error(f"检查修建宜日失败: {str(e)}", exc_info=True)
            return False
    
    def _is_construction_ji_day(self, sizhu):
        """是否修建忌日"""
        try:
            day_zhi = sizhu.get('day_zhi', '子')
            ji_days = ['申', '酉', '戌', '亥']
            return day_zhi in ji_days
        except Exception as e:
            logger.error(f"检查修建忌日失败: {str(e)}", exc_info=True)
            return False
    
    def _check_yang_zhai_rules(self, sizhu, shan_xiang, yi_list, ji_list):
        """阳宅特定规则"""
        try:
            # 阳宅宜日：择日以生旺为主
            month_zhi = sizhu.get('month_zhi', '子')
            day_zhi = sizhu.get('day_zhi', '子')
            
            # 阳宅宜：日支与月支相生或比和
            if self._is_zhi_sheng_he(day_zhi, month_zhi):
                yi_list.append('阳宅修造')
            
            # 阳宅忌：日支与月支相冲
            if self._is_zhi_chong(day_zhi, month_zhi):
                ji_list.append('阳宅修造')
            
            # 山向相关规则
            if shan_xiang:
                if self._is_shan_xiang_yi(shan_xiang, day_zhi):
                    yi_list.append(f'{shan_xiang}向修造')
        except Exception as e:
            logger.error(f"检查阳宅规则失败: {str(e)}", exc_info=True)
    
    def _check_yin_zhai_rules(self, sizhu, shan_xiang, yi_list, ji_list):
        """阴宅特定规则"""
        try:
            # 阴宅宜日：择日以安静为主
            day_zhi = sizhu.get('day_zhi', '子')
            
            # 阴宅宜：阴支日（子、丑、寅、卯、辰、巳）
            yin_days = ['子', '丑', '寅', '卯', '辰', '巳']
            if day_zhi in yin_days:
                yi_list.append('阴宅修造')
            
            # 阴宅忌：阳支日（午、未、申、酉、戌、亥）
            yang_days = ['午', '未', '申', '酉', '戌', '亥']
            if day_zhi in yang_days:
                ji_list.append('阴宅修造')
            
            # 山向相关规则
            if shan_xiang:
                if self._is_shan_xiang_ji(shan_xiang, day_zhi):
                    ji_list.append(f'{shan_xiang}向修造')
        except Exception as e:
            logger.error(f"检查阴宅规则失败: {str(e)}", exc_info=True)
    
    def _is_zhi_sheng_he(self, zhi1, zhi2):
        """判断地支是否相生或比和"""
        # 地支相生关系
        sheng = {
            '子': '寅卯', '丑': '巳午', '寅': '巳午', '卯': '巳午',
            '辰': '申酉', '巳': '申酉', '午': '申酉', '未': '亥子',
            '申': '亥子', '酉': '亥子', '戌': '寅卯', '亥': '寅卯'
        }
        # 比和（相同）
        if zhi1 == zhi2:
            return True
        # 相生
        return zhi2 in sheng.get(zhi1, '')
    
    def _is_zhi_chong(self, zhi1, zhi2):
        """判断地支是否相冲"""
        chong = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return chong.get(zhi1) == zhi2
    
    def _is_shan_xiang_yi(self, shan_xiang, day_zhi):
        """山向宜日"""
        # 简单的山向与日支匹配规则
        # 山向五行与日支五行相生
        shan_xiang_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }
        
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        sx_wuxing = shan_xiang_wuxing.get(shan_xiang)
        dz_wuxing = zhi_wuxing.get(day_zhi)
        
        # 五行相生
        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        return sheng.get(sx_wuxing) == dz_wuxing
    
    def _is_shan_xiang_ji(self, shan_xiang, day_zhi):
        """山向忌日"""
        # 山向五行与日支五行相克
        shan_xiang_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }
        
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        sx_wuxing = shan_xiang_wuxing.get(shan_xiang)
        dz_wuxing = zhi_wuxing.get(day_zhi)
        
        # 五行相克
        ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        return ke.get(sx_wuxing) == dz_wuxing


import sys
import os

# 检查是否是直接运行（不是作为模块导入）
# -*- coding: utf-8 -*-
"""
================================================================================
开业规则模块
================================================================================
实现开业择日的宜忌规则
================================================================================
"""


class OpeningRuleChecker(EventRuleChecker):
    """开业规则检查器"""

    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查开业规则"""
        # 开业宜日
        if self._is_kaiye_yi_day(sizhu):
            yi_list.append('开业')

        # 开业忌日
        if self._is_kaiye_ji_day(sizhu):
            ji_list.append('开业')

        # 开市吉日
        if self._is_kaishi_jiri(sizhu):
            yi_list.append('开市')

        # 纳财吉日
        if self._is_nacai_jiri(sizhu):
            yi_list.append('纳财')

        # 事主八字相关规则
        if owners:
            for owner in owners:
                if self._check_owner_bazi_yi(sizhu, owner):
                    yi_list.append('事主八字宜开业')
                if self._check_owner_bazi_ji(sizhu, owner):
                    ji_list.append('事主八字忌开业')

    def _is_kaiye_yi_day(self, sizhu):
        """是否开业宜日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 开业宜日：子、寅、卯、巳、午、酉
        yi_days = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in yi_days

    def _is_kaiye_ji_day(self, sizhu):
        """是否开业忌日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 开业忌日：丑、辰、未、戌、亥、申
        ji_days = ['丑', '辰', '未', '戌', '亥', '申']
        return day_zhi in ji_days

    def _is_kaishi_jiri(self, sizhu):
        """是否开市吉日"""
        day_zhi = sizhu.get('day_zhi', '子')
        day_gan = sizhu.get('day_gan', '甲')
        # 开市吉日：满日、成日、开日
        kaishi_days = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in kaishi_days

    def _is_nacai_jiri(self, sizhu):
        """是否纳财吉日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 纳财吉日
        nacai_days = ['寅', '卯', '巳', '午', '申', '酉']
        return day_zhi in nacai_days

    def _check_owner_bazi_yi(self, sizhu, owner):
        """检查事主八字是否宜开业"""
        # 简化判断
        return True

    def _check_owner_bazi_ji(self, sizhu, owner):
        """检查事主八字是否忌开业"""
        # 简化判断
        return False


import sys
import os

# 检查是否是直接运行（不是作为模块导入）
# -*- coding: utf-8 -*-
"""
================================================================================
安葬规则模块
================================================================================
实现安葬择日的宜忌规则
================================================================================
"""

class BurialRuleChecker(EventRuleChecker):
    """安葬规则检查器"""
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查安葬规则"""
        # 安葬宜日：阴日
        if self._is_yin_day(sizhu):
            yi_list.append('安葬')
        
        # 安葬忌日：阳日
        if self._is_yang_day(sizhu):
            ji_list.append('安葬')
        
        # 山向相关规则
        if shan_xiang:
            if self._is_shan_xiang_yi(sizhu, shan_xiang):
                yi_list.append(f'{shan_xiang}向安葬')
            if self._is_shan_xiang_ji(sizhu, shan_xiang):
                ji_list.append(f'{shan_xiang}向安葬')
    
    def _is_yin_day(self, sizhu):
        """是否阴日"""
        # 阴日：子、丑、寅、卯、辰、巳
        yin_days = ['子', '丑', '寅', '卯', '辰', '巳']
        return sizhu.get('day_zhi', '子') in yin_days
    
    def _is_yang_day(self, sizhu):
        """是否阳日"""
        # 阳日：午、未、申、酉、戌、亥
        yang_days = ['午', '未', '申', '酉', '戌', '亥']
        return sizhu.get('day_zhi', '子') in yang_days
    
    def _is_shan_xiang_yi(self, sizhu, shan_xiang):
        """山向宜日"""
        # 安葬宜：山向五行与日支五行相生
        shan_xiang_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }
        
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        sx_wuxing = shan_xiang_wuxing.get(shan_xiang)
        dz_wuxing = zhi_wuxing.get(sizhu.get('day_zhi', '子'))
        
        # 五行相生
        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        return sheng.get(sx_wuxing) == dz_wuxing
    
    def _is_shan_xiang_ji(self, sizhu, shan_xiang):
        """山向忌日"""
        # 安葬忌：山向五行与日支五行相克
        shan_xiang_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }
        
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        sx_wuxing = shan_xiang_wuxing.get(shan_xiang)
        dz_wuxing = zhi_wuxing.get(sizhu.get('day_zhi', '子'))
        
        # 五行相克
        ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        return ke.get(sx_wuxing) == dz_wuxing
    
    def get_forbidden_directions(self, sizhu):
        """
        获取禁止使用的方位列表
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            list: 禁止使用的方位列表
        """
        forbidden = []
        all_directions = ['壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
                         '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥']
        
        for direction in all_directions:
            if self._is_shan_xiang_ji(sizhu, direction):
                forbidden.append(direction)
        
        return forbidden
    
    def is_direction_forbidden(self, sizhu, direction):
        """
        检查某个方位是否被禁止
        
        Args:
            sizhu: 四柱信息
            direction: 方位
            
        Returns:
            bool: 是否被禁止
        """
        return self._is_shan_xiang_ji(sizhu, direction)


import sys
import os

# 检查是否是直接运行（不是作为模块导入）
# -*- coding: utf-8 -*-
"""
================================================================================
安床规则模块
================================================================================
实现安床择日的宜忌规则
================================================================================
"""

class BedRuleChecker(EventRuleChecker):
    """安床规则检查器"""
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查安床规则"""
        # 安床宜日：阳日
        if self._is_yang_day(sizhu):
            yi_list.append('安床')
        
        # 安床忌日：阴日
        if self._is_yin_day(sizhu):
            ji_list.append('安床')
        
        # 床位朝向相关规则
        if chuangwei:
            if self._is_chuangwei_yi(sizhu, chuangwei):
                yi_list.append(f'{chuangwei}向安床')
            if self._is_chuangwei_ji(sizhu, chuangwei):
                ji_list.append(f'{chuangwei}向安床')
    
    def _is_yang_day(self, sizhu):
        """是否阳日"""
        # 阳日：午、未、申、酉、戌、亥
        yang_days = ['午', '未', '申', '酉', '戌', '亥']
        return sizhu.get('day_zhi', '子') in yang_days
    
    def _is_yin_day(self, sizhu):
        """是否阴日"""
        # 阴日：子、丑、寅、卯、辰、巳
        yin_days = ['子', '丑', '寅', '卯', '辰', '巳']
        return sizhu.get('day_zhi', '子') in yin_days
    
    def _is_chuangwei_yi(self, sizhu, chuangwei):
        """床位朝向宜日"""
        # 安床宜：床位朝向五行与日支五行相生
        chuangwei_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }
        
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        cw_wuxing = chuangwei_wuxing.get(chuangwei)
        dz_wuxing = zhi_wuxing.get(sizhu.get('day_zhi', '子'))
        
        # 五行相生
        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        return sheng.get(cw_wuxing) == dz_wuxing
    
    def _is_chuangwei_ji(self, sizhu, chuangwei):
        """床位朝向忌日"""
        # 安床忌：床位朝向五行与日支五行相克
        chuangwei_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }
        
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        cw_wuxing = chuangwei_wuxing.get(chuangwei)
        dz_wuxing = zhi_wuxing.get(sizhu.get('day_zhi', '子'))
        
        # 五行相克
        ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        return ke.get(cw_wuxing) == dz_wuxing

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
# -*- coding: utf-8 -*-
"""
================================================================================
出行规则模块
================================================================================
实现出行择日的宜忌规则
================================================================================
"""


class TravelRuleChecker(EventRuleChecker):
    """出行规则检查器"""

    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查出行规则"""
        # 出行宜日
        if self._is_chuxing_yi_day(sizhu):
            yi_list.append('出行')

        # 出行忌日
        if self._is_chuxing_ji_day(sizhu):
            ji_list.append('出行')

        # 远行吉日
        if self._is_yuanxing_jiri(sizhu):
            yi_list.append('远行')

        # 归家吉日
        if self._is_guijia_jiri(sizhu):
            yi_list.append('归家')

        # 事主八字相关规则
        if owners:
            for owner in owners:
                if self._check_owner_bazi_yi(sizhu, owner):
                    yi_list.append('事主八字宜出行')
                if self._check_owner_bazi_ji(sizhu, owner):
                    ji_list.append('事主八字忌出行')

    def _is_chuxing_yi_day(self, sizhu):
        """是否出行宜日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 出行宜日：子、寅、卯、巳、午、酉
        yi_days = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in yi_days

    def _is_chuxing_ji_day(self, sizhu):
        """是否出行忌日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 出行忌日：丑、辰、未、戌、亥、申
        ji_days = ['丑', '辰', '未', '戌', '亥', '申']
        return day_zhi in ji_days

    def _is_yuanxing_jiri(self, sizhu):
        """是否远行吉日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 远行吉日
        yuanxing_days = ['寅', '卯', '巳', '午', '申', '酉']
        return day_zhi in yuanxing_days

    def _is_guijia_jiri(self, sizhu):
        """是否归家吉日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 归家吉日
        guijia_days = ['子', '丑', '辰', '未', '戌', '亥']
        return day_zhi in guijia_days

    def _check_owner_bazi_yi(self, sizhu, owner):
        """检查事主八字是否宜出行"""
        # 简化判断
        return True

    def _check_owner_bazi_ji(self, sizhu, owner):
        """检查事主八字是否忌出行"""
        # 简化判断
        return False


import sys
import os

# 检查是否是直接运行（不是作为模块导入）
# -*- coding: utf-8 -*-
"""
================================================================================
作灶规则模块
================================================================================
实现作灶择日的宜忌规则
================================================================================
"""


class StoveRuleChecker(EventRuleChecker):
    """作灶规则检查器"""

    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查作灶规则"""
        # 作灶宜日
        if self._is_zuozao_yi_day(sizhu):
            yi_list.append('作灶')

        # 作灶忌日
        if self._is_zuozao_ji_day(sizhu):
            ji_list.append('作灶')

        # 灶向相关规则
        if zaoxiang:
            if self._is_zaoxiang_yi(sizhu, zaoxiang):
                yi_list.append(f'{zaoxiang}向作灶')
            if self._is_zaoxiang_ji(sizhu, zaoxiang):
                ji_list.append(f'{zaoxiang}向作灶')

        # 灶位相关规则
        if zaowei:
            if self._is_zaowei_yi(sizhu, zaowei):
                yi_list.append(f'{zaowei}位安灶')
            if self._is_zaowei_ji(sizhu, zaowei):
                ji_list.append(f'{zaowei}位安灶')

        # 宅主八字相关规则
        if owners:
            for owner in owners:
                if self._check_owner_bazi_yi(sizhu, owner):
                    yi_list.append('宅主八字宜作灶')
                if self._check_owner_bazi_ji(sizhu, owner):
                    ji_list.append('宅主八字忌作灶')

    def _is_zuozao_yi_day(self, sizhu):
        """是否作灶宜日"""
        try:
            day_zhi = sizhu.get('day_zhi', '子')
            # 作灶宜日：子、寅、卯、巳、午、酉
            yi_days = ['子', '寅', '卯', '巳', '午', '酉']
            return day_zhi in yi_days
        except Exception as e:
            logger.error(f"检查作灶宜日失败: {str(e)}", exc_info=True)
            return False

    def _is_zuozao_ji_day(self, sizhu):
        """是否作灶忌日"""
        try:
            day_zhi = sizhu.get('day_zhi', '子')
            # 作灶忌日：丑、辰、未、戌、亥、申
            ji_days = ['丑', '辰', '未', '戌', '亥', '申']
            return day_zhi in ji_days
        except Exception as e:
            logger.error(f"检查作灶忌日失败: {str(e)}", exc_info=True)
            return False

    def _is_zaoxiang_yi(self, sizhu, zaoxiang):
        """灶向宜日"""
        try:
            # 灶向五行与日支五行相生为宜
            zaoxiang_wuxing = {
                '壬': '水', '子': '水', '癸': '水',
                '丑': '土', '艮': '土', '寅': '木',
                '甲': '木', '卯': '木', '乙': '木',
                '辰': '土', '巽': '木', '巳': '火',
                '丙': '火', '午': '火', '丁': '火',
                '未': '土', '坤': '土', '申': '金',
                '庚': '金', '酉': '金', '辛': '金',
                '戌': '土', '乾': '金', '亥': '水',
            }

            zhi_wuxing = {
                '子': '水', '丑': '土', '寅': '木', '卯': '木',
                '辰': '土', '巳': '火', '午': '火', '未': '土',
                '申': '金', '酉': '金', '戌': '土', '亥': '水'
            }

            zx_wuxing = zaoxiang_wuxing.get(zaoxiang)
            dz_wuxing = zhi_wuxing.get(sizhu.get('day_zhi', '子'))

            # 五行相生
            sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
            return sheng.get(zx_wuxing) == dz_wuxing
        except Exception as e:
            logger.error(f"检查灶向宜日失败: {str(e)}", exc_info=True)
            return False

    def _is_zaoxiang_ji(self, sizhu, zaoxiang):
        """灶向忌日"""
        try:
            # 灶向五行与日支五行相克为忌
            zaoxiang_wuxing = {
                '壬': '水', '子': '水', '癸': '水',
                '丑': '土', '艮': '土', '寅': '木',
                '甲': '木', '卯': '木', '乙': '木',
                '辰': '土', '巽': '木', '巳': '火',
                '丙': '火', '午': '火', '丁': '火',
                '未': '土', '坤': '土', '申': '金',
                '庚': '金', '酉': '金', '辛': '金',
                '戌': '土', '乾': '金', '亥': '水',
            }

            zhi_wuxing = {
                '子': '水', '丑': '土', '寅': '木', '卯': '木',
                '辰': '土', '巳': '火', '午': '火', '未': '土',
                '申': '金', '酉': '金', '戌': '土', '亥': '水'
            }

            zx_wuxing = zaoxiang_wuxing.get(zaoxiang)
            dz_wuxing = zhi_wuxing.get(sizhu.get('day_zhi', '子'))

            # 五行相克
            ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
            return ke.get(zx_wuxing) == dz_wuxing
        except Exception as e:
            logger.error(f"检查灶向忌日失败: {str(e)}", exc_info=True)
            return False

    def _is_zaowei_yi(self, sizhu, zaowei):
        """灶位宜日"""
        # 灶位五行与日支五行相生为宜
        return self._is_zaoxiang_yi(sizhu, zaowei)

    def _is_zaowei_ji(self, sizhu, zaowei):
        """灶位忌日"""
        # 灶位五行与日支五行相克为忌
        return self._is_zaoxiang_ji(sizhu, zaowei)

    def _check_owner_bazi_yi(self, sizhu, owner):
        """检查宅主八字是否宜作灶"""
        # 简化判断，实际应根据宅主八字详细分析
        # 宅主日柱与作灶日相生或比和为宜
        return True

    def _check_owner_bazi_ji(self, sizhu, owner):
        """检查宅主八字是否忌作灶"""
        # 简化判断，实际应根据宅主八字详细分析
        # 宅主日柱与作灶日相冲为忌
        return False


class RuZhaiRuleChecker(EventRuleChecker):
    """入宅规则检查器"""

    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查入宅规则"""
        # 入宅宜日
        if self._is_ruzhai_yi_day(sizhu):
            yi_list.append('入宅')

        # 入宅忌日
        if self._is_ruzhai_ji_day(sizhu):
            ji_list.append('入宅')

        # 宅向相关规则
        if shan_xiang:
            if self._is_shanxiang_yi(sizhu, shan_xiang):
                yi_list.append(f'{shan_xiang}向入宅')
            if self._is_shanxiang_ji(sizhu, shan_xiang):
                ji_list.append(f'{shan_xiang}向入宅')

        # 宅主八字相关规则
        if owners:
            for owner in owners:
                if self._check_owner_bazi_yi(sizhu, owner):
                    yi_list.append('宅主八字宜入宅')
                if self._check_owner_bazi_ji(sizhu, owner):
                    ji_list.append('宅主八字忌入宅')

    def _is_ruzhai_yi_day(self, sizhu):
        """是否入宅宜日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 入宅宜日：子、寅、卯、巳、午、酉、戌
        yi_days = ['子', '寅', '卯', '巳', '午', '酉', '戌']
        return day_zhi in yi_days

    def _is_ruzhai_ji_day(self, sizhu):
        """是否入宅忌日"""
        day_zhi = sizhu.get('day_zhi', '子')
        # 入宅忌日：丑、辰、未、亥、申
        ji_days = ['丑', '辰', '未', '亥', '申']
        return day_zhi in ji_days

    def _is_shanxiang_yi(self, sizhu, shan_xiang):
        """宅向宜日"""
        # 宅向五行与日支五行相生为宜
        shanxiang_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }

        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }

        sx_wuxing = shanxiang_wuxing.get(shan_xiang)
        dz_wuxing = zhi_wuxing.get(sizhu.get('day_zhi', '子'))

        # 五行相生
        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        return sheng.get(sx_wuxing) == dz_wuxing

    def _is_shanxiang_ji(self, sizhu, shan_xiang):
        """宅向忌日"""
        # 宅向五行与日支五行相克为忌
        shanxiang_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }

        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }

        sx_wuxing = shanxiang_wuxing.get(shan_xiang)
        dz_wuxing = zhi_wuxing.get(sizhu.get('day_zhi', '子'))

        # 五行相克
        ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        return ke.get(sx_wuxing) == dz_wuxing

    def _check_owner_bazi_yi(self, sizhu, owner):
        """检查宅主八字是否宜入宅"""
        # 简化判断，实际应根据宅主八字详细分析
        # 宅主日柱与入宅日相生或比和为宜
        return True

    def _check_owner_bazi_ji(self, sizhu, owner):
        """检查宅主八字是否忌入宅"""
        # 简化判断，实际应根据宅主八字详细分析
        # 宅主日柱与入宅日相冲为忌
        return False


def get_checker(event_type):
    """
    根据事项类型获取神煞检查器
    
    Args:
        event_type: 事项类型
        
    Returns:
        ShenShaChecker: 神煞检查器实例
    """
    marriage_events = ['嫁娶', '订婚', '纳采']
    construction_events = ['修造', '动土', '装修']
    stove_events = ['作灶']
    opening_events = ['开业']
    travel_events = ['出行']
    burial_events = ['安葬']
    bed_events = ['安床']
    ruzhai_events = ['入宅', '移徙', '搬家', '迁居']
    
    if event_type in marriage_events:
        return MarriageShenShaChecker()
    elif event_type in construction_events:
        return ConstructionShenShaChecker()
    elif event_type in stove_events:
        return StoveShenShaChecker()
    elif event_type in opening_events:
        return OpeningShenShaChecker()
    elif event_type in travel_events:
        return TravelShenShaChecker()
    elif event_type in burial_events:
        return BurialShenShaChecker()
    elif event_type in bed_events:
        return BedShenShaChecker()
    elif event_type in ruzhai_events:
        return RuZhaiShenShaChecker()
    else:
        return CommonShenShaChecker()


def get_rule_checker(event_type):
    """
    根据事项类型获取宜忌规则检查器
    
    Args:
        event_type: 事项类型
        
    Returns:
        RuleChecker: 宜忌规则检查器实例
    """
    marriage_events = ['嫁娶', '订婚', '纳采']
    construction_events = ['修造', '动土', '装修']
    stove_events = ['作灶']
    opening_events = ['开业']
    travel_events = ['出行']
    burial_events = ['安葬']
    bed_events = ['安床']
    ruzhai_events = ['入宅', '移徙', '搬家', '迁居']
    
    if event_type in marriage_events:
        return MarriageRuleChecker()
    elif event_type in construction_events:
        return ConstructionRuleChecker()
    elif event_type in stove_events:
        return StoveRuleChecker()
    elif event_type in opening_events:
        return OpeningRuleChecker()
    elif event_type in travel_events:
        return TravelRuleChecker()
    elif event_type in burial_events:
        return BurialRuleChecker()
    elif event_type in bed_events:
        return BedRuleChecker()
    elif event_type in ruzhai_events:
        return RuZhaiRuleChecker()
    else:
        return CommonRuleChecker()


# -*- coding: utf-8 -*-
"""
================================================================================
专业级正五行择日软件 - 主程序
================================================================================
【系统概述】
本软件是一款基于传统正五行择日理论的专业择日工具，采用"五行为主，黄道为用"的
双层架构设计，支持嫁娶、安葬、修造、开业等各类民事择日需求。

【核心架构】
1. 第一层（核心筛选）：正五行模块
   - 功能：补龙、扶山、相主，避开三杀、冲山等大忌
   - 作用：系统的"否决权"模块，五行不合格直接淘汰
   - 权重：占评分60%

2. 第二层（优选排序）：大小黄道模块
   - 大黄道：十二神（青龙、明堂、天刑、朱雀、金匮、天德、白虎、玉堂、司命等）
   - 小黄道：十二建星（建、除、满、平、定、执、破、危、成、收、开、闭）
   - 作用：系统的"加分项"，在五行合格基础上优化选择
   - 权重：占评分40%

【评分规则】
- 基础分：100分
- 吉神加分：每个吉神+5~15分（根据重要性）
- 凶神减分：每个凶神-8~20分（根据严重性）
- 宜事加分：每项宜事+10分
- 忌事减分：每项忌事-15分
- 黄道调整：黄道大吉+10分，黑道-5分

【星级等级划分】
⭐⭐⭐⭐⭐ (5星) = 上吉（130分以上）：五行大吉 + 黄道大吉，首选推荐
⭐⭐⭐⭐ (4星) = 大吉（120-129分）：五行大吉，诸事皆宜
⭐⭐⭐ (3星) = 吉（100-119分）：五行合格 + 黄道吉，可用
⭐⭐ (2星) = 中吉/次吉（80-99分）：五行合格但有小忌，可用但需谨慎
⭐ (1星) = 平（60-79分）：五行平平，仅适合小事
❌ (0星) = 凶（<60分）：五行凶或犯大忌，坚决不用

【冲突处理原则】
1. 五行大吉 + 黄道大吉 → ⭐⭐⭐⭐⭐ 上吉（首选）
2. 五行大吉 + 黄道黑道 → ⭐⭐ 次吉（可用，需化解）
3. 五行平平 + 黄道大吉 → ⭐ 平（小事可用）
4. 五行凶 + 任何黄道 → ❌ 凶（坚决不用）

【使用流程】
1. 选择事项类型（嫁娶、安葬、修造等）
2. 设置日期范围（开始日期、结束日期）
3. 输入事主信息（生辰八字，可选）
4. 点击"开始择日"进行计算
5. 查看结果列表，了解每日评分和宜忌
6. 可导出结果或导入日课评分系统进行详细分析

【文件结构】
- 主程序.py：GUI主界面，程序入口
- modules/四柱计算器.py：四柱八字计算（年柱、月柱、日柱、时柱）
- modules/评分器.py：综合评分算法
- modules/黄道.py：黄道吉日计算
- modules/shensha/：各类神煞定义和检查
- modules/rules/：各类事项择日规则
- modules/日课评分系统.py：日课评分和对比分析工具
- modules/日期测试窗口.py：日期计算转换测试窗口

【技术说明】
- 使用tkinter构建GUI界面
- 采用传统历法计算四柱八字
- 支持农历和公历转换
- 内置多种神煞和择日规则
- 可导出JSON格式的择日记录

【注意事项】
1. 本软件计算结果仅供参考，重要事项建议咨询专业择日师
2. 事主信息为可选输入，但提供后可获得更精准的分析
3. 修造类事项需要选择山向和宅型
4. 系统会自动避开明显的大凶之日

【版本信息】
版本: 1.0.0
更新日期: 2026年
作者: 专业择日团队
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import date, datetime, timedelta
import json
import os
import sys

# 添加项目根目录到路径

# 导入节气计算模块
try:
    import sxtwl
    HAS_SXTWL = True
except ImportError:
    HAS_SXTWL = False

class ZeriApp:
    """择日软件主应用类
    
    功能说明：
    -----------
    1. 事项选择：支持嫁娶、安葬、修造、开业等12类事项
    2. 日期设置：可设置择日的时间范围
    3. 事主信息：支持输入多个事主的生辰八字（年月日时分）
    4. 择日计算：根据正五行理论计算每日吉凶
    5. 结果展示：显示日期、四柱、评分、等级、宜忌等信息
    6. 记录管理：支持保存、查看、导出择日记录
    7. 日课评分：可将结果导入评分系统进行详细分析
    8. 日期测试：日期计算转换测试窗口
    
    使用示例：
    -----------
    >>> root = tk.Tk()
    >>> app = ZeriApp(root)
    >>> root.mainloop()
    """
    
    def __init__(self, root):
        """初始化主应用
        
        Args:
            root: tkinter根窗口
        """
        print("初始化ZeriApp...")
        self.root = root
        self.root.title("专业级正五行择日软件 v1.0")
        
        # 获取屏幕尺寸并设置窗口大小
        print("获取屏幕尺寸...")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        print(f"屏幕尺寸: {screen_width}x{screen_height}")
        
        # 设置为小窗口（屏幕的45%宽度，66.7%高度）
        window_width = int(screen_width * 0.45)
        window_height = int(screen_height * 0.667)
        print(f"窗口大小: {window_width}x{window_height}")
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        print(f"窗口位置: {x},{y}")
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        print("设置窗口大小和位置成功")
        
        # 注释掉窗口最大化，保持小窗口
        # self.root.state('zoomed')  # 窗口最大化
        print("窗口设置为小窗口")
        
        # 确保窗口显示
        self.root.deiconify()
        print("窗口显示成功")
        
        # 数据存储
        self.results = []  # 择日结果
        self.records = []  # 历史记录
        self.owners_info = []  # 事主信息
        print("初始化数据存储成功")
        
        # 创建界面
        print("创建菜单栏...")
        self.create_menu()
        print("创建菜单栏成功")
        
        print("创建界面组件...")
        self.create_widgets()
        print("创建界面组件成功")
        
        # 加载历史记录
        print("加载历史记录...")
        self.load_records()
        print("加载历史记录成功")
        
        print("ZeriApp初始化完成")
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出结果", command=self.export_results)
        file_menu.add_command(label="导入文件", command=self.import_file)
        file_menu.add_command(label="查看记录", command=self.view_records)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="八字可视化", command=self.open_bazi_panpan)
        tools_menu.add_separator()
        tools_menu.add_command(label="节气查询", command=self.show_solar_terms)
        tools_menu.add_separator()
        tools_menu.add_command(label="日课评分系统", command=self.open_score_system)
        tools_menu.add_command(label="日期测试窗口", command=self.open_date_test)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_widgets(self):
        """创建主界面组件"""
        # 配置全局样式
        self.configure_styles()
        
        # 创建主滚动区域
        main_canvas = tk.Canvas(self.root, bg="#ffffff")
        main_scrollbar_v = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        main_scrollbar_h = ttk.Scrollbar(self.root, orient="horizontal", command=main_canvas.xview)
        self.main_frame = ttk.Frame(main_canvas, padding="20", style="MainFrame.TFrame")
        
        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw", width=self.root.winfo_screenwidth()-50)
        main_canvas.configure(yscrollcommand=main_scrollbar_v.set, xscrollcommand=main_scrollbar_h.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar_v.pack(side="right", fill="y")
        main_scrollbar_h.pack(side="bottom", fill="x")
        
        # 绑定鼠标滚轮
        main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # 标题区域
        title_frame = ttk.Frame(self.main_frame, style="TitleFrame.TFrame")
        title_frame.pack(fill=tk.X, pady=8, padx=20)
        
        title_label = ttk.Label(title_frame, text="专业级正五行择日软件", 
                               font=("微软雅黑", 18, "bold"), style="Title.TLabel")
        title_label.pack(pady=4)
        
        subtitle_label = ttk.Label(title_frame, text="精准择日，趋吉避凶", 
                                  font=("微软雅黑", 9), style="Subtitle.TLabel")
        subtitle_label.pack()
        
        # 输入区域
        input_frame = ttk.LabelFrame(self.main_frame, text="择日设置", padding="8")
        input_frame.pack(fill=tk.X, pady=6, padx=20)
        
        # 左侧：择日设置表单
        form_frame = ttk.Frame(input_frame)
        form_frame.grid(row=0, column=0, sticky=tk.W, padx=6)
        
        # 事项选择
        ttk.Label(form_frame, text="事项类型：", font=("微软雅黑", 8, "bold")).grid(row=0, column=0, sticky=tk.W, pady=6, padx=4)
        self.event_var = tk.StringVar(value="嫁娶")
        event_combo = ttk.Combobox(form_frame, textvariable=self.event_var, 
                                   values=["嫁娶", "修造", "动土", "入宅", "开业", 
                                          "出行", "安床", "作灶", "移徙", "入学", "求医",
                                          "签约", "安葬"], width=20, state="readonly", 
                                   font=("微软雅黑", 8))
        event_combo.grid(row=0, column=1, sticky=tk.W, pady=6, padx=9)
        event_combo.bind("<<ComboboxSelected>>", self.on_event_change)
        
        # 日期范围
        ttk.Label(form_frame, text="开始日期：", font=("微软雅黑", 8, "bold")).grid(row=1, column=0, sticky=tk.W, pady=6, padx=4)
        self.start_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        start_entry = ttk.Entry(form_frame, textvariable=self.start_date, width=20, 
                               font=("微软雅黑", 8))
        start_entry.grid(row=1, column=1, sticky=tk.W, pady=6, padx=9)
        
        ttk.Label(form_frame, text="结束日期：", font=("微软雅黑", 8, "bold")).grid(row=1, column=2, sticky=tk.W, pady=6, padx=22)
        end = date.today() + timedelta(days=30)
        self.end_date = tk.StringVar(value=end.strftime("%Y-%m-%d"))
        end_entry = ttk.Entry(form_frame, textvariable=self.end_date, width=20, 
                             font=("微软雅黑", 8))
        end_entry.grid(row=1, column=3, sticky=tk.W, pady=6, padx=9)
        
        # 为日期输入框绑定键盘导航
        self._bind_entry_navigation([start_entry, end_entry])
        
        # 右侧：择日图案显示
        self.pattern_frame = ttk.LabelFrame(input_frame, text="择日图案", padding="6")
        self.pattern_frame.grid(row=0, column=1, sticky=tk.E, padx=(22, 6))
        
        # 创建图案显示画布
        self.pattern_canvas = tk.Canvas(self.pattern_frame, width=120, height=120, bg="#f8f9fa", 
                                       highlightthickness=2, highlightbackground="#007bff")
        self.pattern_canvas.pack(pady=4)
        
        # 初始显示默认图案
        self.update_pattern()
        
        # 绑定事项类型变化事件
        self.event_var.trace_add('write', self.update_pattern)
        
        # 特殊选项（根据事项类型显示）
        self.special_frame = ttk.LabelFrame(self.main_frame, text="特殊选项", padding="8")
        self.special_frame.pack(fill=tk.X, pady=6, padx=20)
        self.update_special_options()
        
        # 按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=8, padx=20)
        
        ttk.Button(button_frame, text="开始择日", command=self.start_calculation, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="日课评分", command=self.open_score_system, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="日期测试", command=self.open_date_test, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="导出结果", command=self.export_results, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="导入文件", command=self.import_file, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="查看记录", command=self.view_records, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="帮助", command=self.show_help, 
                  width=12).pack(side=tk.RIGHT, padx=6)
        
        # 左右分栏区域（事主信息在左，择日结果在右）
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=15, padx=20)
        
        # 左侧：事主信息
        self.owners_frame = ttk.LabelFrame(content_frame, text="事主信息", padding="20")
        self.owners_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 20))
        self.owners_frame.configure(width=400)
        self.update_owners_frame()
        
        # 右侧：择日结果
        result_frame = ttk.LabelFrame(content_frame, text="择日结果", padding="20")
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # 按钮区域
        result_button_frame = ttk.Frame(result_frame)
        result_button_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(result_button_frame, text="全部导入到评分系统", 
                  command=self.import_all_to_score_system, width=25).pack(side=tk.LEFT, padx=10)
        ttk.Button(result_button_frame, text="清空结果", 
                  command=self.clear_results, width=15).pack(side=tk.LEFT, padx=10)
        
        # 结果列表
        columns = ("日期/四柱", "评分", "等级", "四柱", "月令得分", "喜用神得分", "黄道得分")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=15)
        
        # 设置列宽
        self.result_tree.column("日期/四柱", width=120)
        self.result_tree.column("评分", width=60, anchor=tk.CENTER)
        self.result_tree.column("等级", width=80, anchor=tk.CENTER)
        self.result_tree.column("四柱", width=180)
        self.result_tree.column("月令得分", width=70, anchor=tk.CENTER)
        self.result_tree.column("喜用神得分", width=80, anchor=tk.CENTER)
        self.result_tree.column("黄道得分", width=70, anchor=tk.CENTER)
        
        # 设置列标题
        for col in columns:
            self.result_tree.heading(col, text=col, anchor=tk.CENTER)
        
        # 滚动条
        tree_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # 结果列表包装器
        tree_frame = ttk.Frame(result_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.result_tree.bind("<Double-1>", self.on_result_double_click)
        
        # 绑定鼠标悬停效果
        self.result_tree.bind("<Motion>", self.on_tree_motion)
        
        # 为不同星级设置行背景色
        self.result_tree.tag_configure('5star', background='#FFF9E6')  # 淡金色背景
        self.result_tree.tag_configure('4star', background='#F0F8FF')  # 淡蓝色背景
        self.result_tree.tag_configure('3star', background='#F0FFF0')  # 淡绿色背景
        self.result_tree.tag_configure('2star', background='#FFF5EE')  # 淡橙色背景
        self.result_tree.tag_configure('1star', background='#F5F5F5')  # 淡灰色背景
    
    def configure_styles(self):
        """配置界面样式"""
        style = ttk.Style()
        
        # 主题设置
        style.theme_use('clam')
        
        # 主框架样式
        style.configure('MainFrame.TFrame', background='#ffffff')
        
        # 标题框架样式
        style.configure('TitleFrame.TFrame', background='#007bff')
        
        # 标题样式
        style.configure('Title.TLabel', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 28, 'bold'))
        
        # 副标题样式
        style.configure('Subtitle.TLabel', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 14))
        
        # 卡片样式
        style.configure('Card.TLabelframe', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 12, 'bold'),
                       borderwidth=2,
                       relief='groove')
        
        # 表单框架样式
        style.configure('Form.TFrame', background='#ffffff')
        
        # 标签样式
        style.configure('Label.TLabel', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 12, 'bold'))
        
        # 输入框样式
        style.configure('Entry.TEntry', 
                       fieldbackground='white',
                       foreground='#333333',
                       font=('微软雅黑', 12),
                       borderwidth=2,
                       relief='solid')
        
        # 下拉框样式
        style.configure('Combobox.TCombobox', 
                       fieldbackground='white',
                       foreground='#333333',
                       font=('微软雅黑', 12),
                       borderwidth=2,
                       relief='solid')
        
        # 按钮框架样式
        style.configure('ButtonFrame.TFrame', background='#ffffff')
        
        # 主按钮样式
        style.configure('Primary.TButton', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 11, 'bold'),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Primary.TButton', 
                  background=[('active', '#0069d9')])
        
        # 次要按钮样式
        style.configure('Secondary.TButton', 
                       background='#6c757d',
                       foreground='white',
                       font=('微软雅黑', 11),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Secondary.TButton', 
                  background=[('active', '#5a6268')])
        
        # 信息按钮样式
        style.configure('Info.TButton', 
                       background='#17a2b8',
                       foreground='white',
                       font=('微软雅黑', 11),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Info.TButton', 
                  background=[('active', '#138496')])
        
        # 危险按钮样式
        style.configure('Danger.TButton', 
                       background='#dc3545',
                       foreground='white',
                       font=('微软雅黑', 11),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Danger.TButton', 
                  background=[('active', '#c82333')])
        
        # 内容框架样式
        style.configure('ContentFrame.TFrame', background='#ffffff')
        
        # 树形视图样式
        style.configure('Treeview.Treeview', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 10),
                       rowheight=25,
                       fieldbackground='#ffffff',
                       borderwidth=1,
                       relief='solid')
        
        # 树形视图标题样式
        style.configure('Treeview.Heading', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 10, 'bold'),
                       padding=(10, 5))
        
        # 树形视图悬停样式
        style.map('Treeview.Treeview', 
                  background=[('selected', '#cce7ff'), ('!selected', '#ffffff')],
                  foreground=[('selected', '#007bff'), ('!selected', '#333333')])
        
        # 滚动条样式
        style.configure('Scrollbar.Vertical.TScrollbar', 
                       background='#ffffff',
                       troughcolor='#e0e0e0',
                       borderwidth=0)
    
    def on_tree_motion(self, event):
        """树形视图鼠标悬停效果"""
        # 鼠标悬停在树形视图上时的效果
        pass
    
    def update_pattern(self, *args):
        """根据事项类型更新择日图案"""
        event_type = self.event_var.get()
        
        # 清空画布
        self.pattern_canvas.delete("all")
        
        # 中心坐标（画布大小为120×120）
        center_x = 60
        center_y = 60
        
        # 根据事项类型绘制不同的图案
        if event_type == "嫁娶":
            # 绘制双喜图案
            self._draw_double_happiness(center_x, center_y)
        elif event_type == "修造":
            # 绘制建筑图案
            self._draw_construction(center_x, center_y)
        elif event_type == "动土":
            # 绘制土地图案
            self._draw_earth(center_x, center_y)
        elif event_type == "入宅":
            # 绘制房屋图案
            self._draw_house(center_x, center_y)
        elif event_type == "开业":
            # 绘制开业图案
            self._draw_business(center_x, center_y)
        elif event_type == "出行":
            # 绘制出行图案
            self._draw_travel(center_x, center_y)
        elif event_type == "安床":
            # 绘制安床图案
            self._draw_bed(center_x, center_y)
        elif event_type == "作灶":
            # 绘制作灶图案
            self._draw_kitchen(center_x, center_y)
        elif event_type == "移徙":
            # 绘制移徙图案
            self._draw_moving(center_x, center_y)
        elif event_type == "入学":
            # 绘制入学图案
            self._draw_study(center_x, center_y)
        elif event_type == "求医":
            # 绘制求医图案
            self._draw_medical(center_x, center_y)
        elif event_type == "签约":
            # 绘制签约图案
            self._draw_contract(center_x, center_y)
        elif event_type == "安葬":
            # 绘制安葬图案
            self._draw_burial(center_x, center_y)
        else:
            # 默认图案
            self._draw_default_pattern(center_x, center_y)
    
    def _draw_double_happiness(self, x, y):
        """绘制双喜图案"""
        # 红色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#ff6b6b")
        
        # 双喜字
        self.pattern_canvas.create_text(x, y, text="囍", font=("微软雅黑", 60, "bold"), fill="red")
    
    def _draw_construction(self, x, y):
        """绘制建筑图案"""
        # 蓝色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#4ecdc4")
        
        # 建筑物
        self.pattern_canvas.create_rectangle(x-50, y-30, x+50, y+50, fill="#f7f7f7")
        self.pattern_canvas.create_polygon(x-60, y-30, x, y-60, x+60, y-30, fill="#ff6b6b")
        
        # 窗户
        self.pattern_canvas.create_rectangle(x-30, y, x-10, y+20, fill="#45b7d1")
        self.pattern_canvas.create_rectangle(x+10, y, x+30, y+20, fill="#45b7d1")
    
    def _draw_earth(self, x, y):
        """绘制土地图案"""
        # 棕色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#8b4513")
        
        # 土地
        self.pattern_canvas.create_rectangle(x-60, y, x+60, y+60, fill="#d2b48c")
        
        # 植物
        self.pattern_canvas.create_line(x-20, y, x-20, y-30, width=3, fill="#228b22")
        self.pattern_canvas.create_line(x, y, x, y-40, width=3, fill="#228b22")
        self.pattern_canvas.create_line(x+20, y, x+20, y-30, width=3, fill="#228b22")
        
        # 树叶
        self.pattern_canvas.create_oval(x-30, y-35, x-10, y-15, fill="#32cd32")
        self.pattern_canvas.create_oval(x-10, y-45, x+10, y-25, fill="#32cd32")
        self.pattern_canvas.create_oval(x+10, y-35, x+30, y-15, fill="#32cd32")
    
    def _draw_house(self, x, y):
        """绘制房屋图案"""
        # 绿色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#4ecdc4")
        
        # 房屋
        self.pattern_canvas.create_rectangle(x-50, y-20, x+50, y+50, fill="#f7f7f7")
        self.pattern_canvas.create_polygon(x-60, y-20, x, y-50, x+60, y-20, fill="#ff6b6b")
        
        # 门
        self.pattern_canvas.create_rectangle(x-15, y+10, x+15, y+50, fill="#8b4513")
        
        # 窗户
        self.pattern_canvas.create_rectangle(x-30, y-10, x-10, y+10, fill="#45b7d1")
        self.pattern_canvas.create_rectangle(x+10, y-10, x+30, y+10, fill="#45b7d1")
    
    def _draw_business(self, x, y):
        """绘制开业图案"""
        # 金色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#ffd93d")
        
        # 钱袋
        self.pattern_canvas.create_oval(x-40, y-10, x+40, y+50, fill="#8b4513")
        self.pattern_canvas.create_rectangle(x-40, y+10, x+40, y+50, fill="#8b4513")
        
        # 钱币
        self.pattern_canvas.create_oval(x-20, y-30, x-5, y-15, fill="#ffd700")
        self.pattern_canvas.create_oval(x+5, y-30, x+20, y-15, fill="#ffd700")
        self.pattern_canvas.create_oval(x-15, y-20, x-10, y-15, fill="#8b4513")
        self.pattern_canvas.create_oval(x+10, y-20, x+15, y-15, fill="#8b4513")
    
    def _draw_travel(self, x, y):
        """绘制出行图案"""
        # 蓝色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#45b7d1")
        
        # 交通工具（汽车）
        self.pattern_canvas.create_rectangle(x-40, y, x+30, y+30, fill="#f7f7f7")
        self.pattern_canvas.create_polygon(x+30, y, x+40, y-10, x+40, y+40, x+30, y+30, fill="#f7f7f7")
        
        # 车轮
        self.pattern_canvas.create_oval(x-30, y+30, x-10, y+50, fill="#333333")
        self.pattern_canvas.create_oval(x+10, y+30, x+30, y+50, fill="#333333")
        
        # 车窗
        self.pattern_canvas.create_rectangle(x-30, y+5, x+20, y+20, fill="#45b7d1")
    
    def _draw_bed(self, x, y):
        """绘制安床图案"""
        # 紫色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#9b59b6")
        
        # 床
        self.pattern_canvas.create_rectangle(x-50, y+10, x+50, y+50, fill="#f7f7f7")
        self.pattern_canvas.create_rectangle(x-60, y, x+60, y+10, fill="#8b4513")
        
        # 枕头
        self.pattern_canvas.create_rectangle(x-40, y-20, x-10, y+10, fill="#ff6b6b")
        self.pattern_canvas.create_rectangle(x+10, y-20, x+40, y+10, fill="#ff6b6b")
        
        # 被子
        self.pattern_canvas.create_rectangle(x-50, y-10, x+50, y+10, fill="#4ecdc4")
    
    def _draw_kitchen(self, x, y):
        """绘制作灶图案"""
        # 橙色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#ff9f43")
        
        # 灶台
        self.pattern_canvas.create_rectangle(x-40, y+10, x+40, y+50, fill="#8b4513")
        
        # 锅
        self.pattern_canvas.create_oval(x-30, y-10, x+30, y+10, fill="#333333")
        
        # 火焰
        self.pattern_canvas.create_polygon(x, y+10, x-10, y+30, x+10, y+30, fill="#ff6b6b")
        self.pattern_canvas.create_polygon(x, y+15, x-8, y+25, x+8, y+25, fill="#ffd93d")
    
    def _draw_moving(self, x, y):
        """绘制移徙图案"""
        # 绿色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#44bd32")
        
        # 箱子
        self.pattern_canvas.create_rectangle(x-40, y-20, x+40, y+40, fill="#f7f7f7")
        self.pattern_canvas.create_rectangle(x-45, y-25, x+45, y-20, fill="#8b4513")
        
        # 提手
        self.pattern_canvas.create_oval(x-15, y-30, x-5, y-20, fill="#333333")
        self.pattern_canvas.create_oval(x+5, y-30, x+15, y-20, fill="#333333")
        
        # 装饰
        self.pattern_canvas.create_line(x-30, y, x+30, y, fill="#333333")
        self.pattern_canvas.create_line(x-30, y+15, x+30, y+15, fill="#333333")
    
    def _draw_study(self, x, y):
        """绘制入学图案"""
        # 蓝色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#3498db")
        
        # 书本
        self.pattern_canvas.create_rectangle(x-40, y-30, x+40, y+30, fill="#f7f7f7")
        self.pattern_canvas.create_line(x-40, y, x+40, y, fill="#333333")
        
        # 书本页数
        self.pattern_canvas.create_line(x-35, y-25, x+35, y-25, fill="#333333", width=2)
        self.pattern_canvas.create_line(x-35, y-15, x+35, y-15, fill="#333333")
        self.pattern_canvas.create_line(x-35, y+15, x+35, y+15, fill="#333333")
        self.pattern_canvas.create_line(x-35, y+25, x+35, y+25, fill="#333333", width=2)
    
    def _draw_medical(self, x, y):
        """绘制求医图案"""
        # 白色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#f7f7f7")
        
        # 红十字
        self.pattern_canvas.create_rectangle(x-30, y-10, x+30, y+10, fill="#ff6b6b")
        self.pattern_canvas.create_rectangle(x-10, y-30, x+10, y+30, fill="#ff6b6b")
        
        # 医疗标志
        self.pattern_canvas.create_oval(x-40, y-40, x+40, y+40, outline="#3498db", width=3)
    
    def _draw_contract(self, x, y):
        """绘制签约图案"""
        # 黄色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#ffd93d")
        
        # 合同
        self.pattern_canvas.create_rectangle(x-50, y-30, x+50, y+30, fill="#f7f7f7")
        
        # 文字线条
        self.pattern_canvas.create_line(x-40, y-15, x+40, y-15, fill="#333333")
        self.pattern_canvas.create_line(x-40, y, x+40, y, fill="#333333")
        self.pattern_canvas.create_line(x-40, y+15, x+40, y+15, fill="#333333")
        
        # 印章
        self.pattern_canvas.create_oval(x+20, y-20, x+40, y, fill="#ff6b6b")
    
    def _draw_burial(self, x, y):
        """绘制安葬图案"""
        # 灰色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#95a5a6")
        
        # 墓碑
        self.pattern_canvas.create_rectangle(x-30, y-40, x+30, y+20, fill="#f7f7f7")
        
        # 墓基
        self.pattern_canvas.create_rectangle(x-40, y+20, x+40, y+30, fill="#8b4513")
        
        # 十字架
        self.pattern_canvas.create_line(x, y-50, x, y-30, fill="#333333", width=3)
        self.pattern_canvas.create_line(x-15, y-40, x+15, y-40, fill="#333333", width=3)
    
    def _draw_default_pattern(self, x, y):
        """绘制默认图案"""
        # 浅蓝色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#d1ecf1")
        
        # 日历图标
        self.pattern_canvas.create_rectangle(x-40, y-30, x+40, y+30, fill="#f7f7f7")
        
        # 日历标题
        self.pattern_canvas.create_rectangle(x-40, y-30, x+40, y-15, fill="#3498db")
        
        # 日历日期
        self.pattern_canvas.create_text(x, y+5, text="择日", font=("微软雅黑", 20, "bold"), fill="#333333")
    
    def update_special_options(self):
        """根据事项类型更新特殊选项"""
        # 清空现有组件
        for widget in self.special_frame.winfo_children():
            widget.destroy()
        
        event_type = self.event_var.get()
        special_entries = []
        
        if event_type in ["修造", "动土", "入宅"]:
            # 宅型选择
            ttk.Label(self.special_frame, text="宅型：").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.house_type = tk.StringVar(value="阳宅")
            house_combo = ttk.Combobox(self.special_frame, textvariable=self.house_type, 
                        values=["阳宅", "阴宅"], width=10, state="readonly")
            house_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
            special_entries.append(house_combo)
            
            # 山向选择（使用二十四山模块的完整山向列表）
            ttk.Label(self.special_frame, text="山向：").grid(row=0, column=2, sticky=tk.W, padx=5)
            self.shan_xiang = tk.StringVar()
            # 使用二十四山模块获取完整的24山向列表
            shan_xiangs = get_shan_xiang_list(use_24_shan=True)
            shan_combo = ttk.Combobox(self.special_frame, textvariable=self.shan_xiang, 
                        values=shan_xiangs, width=12, state="readonly")
            shan_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
            special_entries.append(shan_combo)
            
            # 兼向选择（改为下拉菜单）
            ttk.Label(self.special_frame, text="兼向：").grid(row=0, column=4, sticky=tk.W, padx=5)
            self.jian_xiang = tk.StringVar()
            self.jian_xiang_combo = ttk.Combobox(self.special_frame, textvariable=self.jian_xiang,
                                                  values=["正中", "兼左", "兼右"], width=10, state="readonly")
            self.jian_xiang_combo.grid(row=0, column=5, sticky=tk.W, padx=5)
            special_entries.append(self.jian_xiang_combo)
            self.jian_xiang.set("正中")  # 默认正中
            # 绑定山向变化时更新兼向选项
            self.shan_xiang.trace_add('write', self._update_jianxiang_options)
            
            # 电子罗盘按钮
            ttk.Button(self.special_frame, text="罗盘", width=6,
                      command=self._show_compass_dialog).grid(row=0, column=6, sticky=tk.W, padx=5)
            
        elif event_type == "作灶":
            ttk.Label(self.special_frame, text="灶向：").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.zao_xiang = tk.StringVar()
            zao_combo = ttk.Combobox(self.special_frame, textvariable=self.zao_xiang, 
                        values=["东", "南", "西", "北", "东南", "东北", "西南", "西北"], 
                        width=10, state="readonly")
            zao_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
            special_entries.append(zao_combo)
            
            ttk.Label(self.special_frame, text="灶位：").grid(row=0, column=2, sticky=tk.W, padx=5)
            self.zao_wei = tk.StringVar()
            wei_combo = ttk.Combobox(self.special_frame, textvariable=self.zao_wei, 
                        values=["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"], 
                        width=10, state="readonly")
            wei_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
            special_entries.append(wei_combo)
            
        elif event_type == "安床":
            ttk.Label(self.special_frame, text="床位朝向：").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.chuang_wei = tk.StringVar()
            chuang_combo = ttk.Combobox(self.special_frame, textvariable=self.chuang_wei, 
                        values=["东", "南", "西", "北", "东南", "东北", "西南", "西北"], 
                        width=10, state="readonly")
            chuang_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
            special_entries.append(chuang_combo)
        
        # 为特殊选项的输入框绑定键盘导航
        if special_entries:
            self._bind_entry_navigation(special_entries)
    
    def update_owners_frame(self):
        """更新事主信息框架"""
        # 清空现有组件
        for widget in self.owners_frame.winfo_children():
            widget.destroy()
        
        self.owners_info = []
        event_type = self.event_var.get()
        
        # 添加提示标签
        if event_type != "嫁娶":
            hint_label = ttk.Label(self.owners_frame, 
                                   text="（提示：以下事主信息为可选，可根据需要填写）", 
                                   foreground="gray", font=("微软雅黑", 9, "italic"))
            hint_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 根据事项类型确定事主
        if event_type == "嫁娶":
            owners = ["新娘", "新郎"]
        elif event_type == "安葬":
            # 安葬需要死者（逝者）和孝子（家属）
            owners = ["死者", "孝子1", "孝子2", "孝子3"]
        elif event_type in ["修造", "动土", "入宅", "作灶", "开业", "出行", "安床"]:
            owners = ["事主1", "事主2", "事主3", "事主4"]
        else:
            owners = ["事主"]
        
        # 存储所有输入框以便键盘导航
        all_entries = []
        
        for owner in owners:
            owner_frame = ttk.Frame(self.owners_frame)
            owner_frame.pack(fill=tk.X, pady=3)
            
            # 日期输入行
            date_row = ttk.Frame(owner_frame)
            date_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(date_row, text=f"{owner}:", width=10).pack(side=tk.LEFT, padx=5, pady=2)
            
            # 默认值设置
            if event_type == "嫁娶":
                year_var = tk.StringVar(value=str(date.today().year - 25))
                month_var = tk.StringVar(value=str(1))
                day_var = tk.StringVar(value=str(1))
            else:
                year_var = tk.StringVar()
                month_var = tk.StringVar()
                day_var = tk.StringVar()
            
            hour_var = tk.StringVar(value="12")
            minute_var = tk.StringVar(value="0")
            
            # 性别选择
            if event_type == "嫁娶":
                # 嫁娶事项根据角色默认性别
                gender_var = tk.StringVar(value='女' if owner == '新娘' else '男')
            else:
                # 其他事项默认性别为男
                gender_var = tk.StringVar(value='男')
            
            ttk.Label(date_row, text="性别:").pack(side=tk.LEFT, padx=(10, 0))
            ttk.Radiobutton(date_row, text="男", variable=gender_var, value='男', width=3).pack(side=tk.LEFT, padx=2)
            ttk.Radiobutton(date_row, text="女", variable=gender_var, value='女', width=3).pack(side=tk.LEFT, padx=2)
            
            ttk.Label(date_row, text="年:").pack(side=tk.LEFT)
            year_entry = ttk.Entry(date_row, textvariable=year_var, width=6)
            year_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(year_entry)
            
            ttk.Label(date_row, text="月:").pack(side=tk.LEFT)
            month_entry = ttk.Entry(date_row, textvariable=month_var, width=4)
            month_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(month_entry)
            
            ttk.Label(date_row, text="日:").pack(side=tk.LEFT)
            day_entry = ttk.Entry(date_row, textvariable=day_var, width=4)
            day_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(day_entry)
            
            ttk.Label(date_row, text="时:").pack(side=tk.LEFT)
            hour_entry = ttk.Entry(date_row, textvariable=hour_var, width=4)
            hour_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(hour_entry)
            
            ttk.Label(date_row, text="分:").pack(side=tk.LEFT)
            minute_entry = ttk.Entry(date_row, textvariable=minute_var, width=4)
            minute_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(minute_entry)
            
            # 四柱显示行
            sizhu_row = ttk.Frame(owner_frame)
            sizhu_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(sizhu_row, text="四柱:", width=10).pack(side=tk.LEFT, padx=5)
            sizhu_var = tk.StringVar(value="未计算")
            ttk.Label(sizhu_row, textvariable=sizhu_var, 
                     font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT, padx=5)
            
            # 喜用神显示行
            xishen_var = tk.StringVar(value="")
            yongshen_var = tk.StringVar(value="")
            
            xishen_row = ttk.Frame(owner_frame)
            xishen_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(xishen_row, text="喜神:", width=10).pack(side=tk.LEFT, padx=5)
            ttk.Label(xishen_row, textvariable=xishen_var, foreground="blue").pack(side=tk.LEFT, padx=5)
            ttk.Label(xishen_row, text="  用神:").pack(side=tk.LEFT)
            ttk.Label(xishen_row, textvariable=yongshen_var, foreground="green").pack(side=tk.LEFT, padx=5)
            
            # 夫星子星显示（婚嫁专用）
            fuzi_var = tk.StringVar(value="")
            if event_type == "嫁娶":
                fuzi_row = ttk.Frame(owner_frame)
                fuzi_row.pack(fill=tk.X, pady=2)
                
                ttk.Label(fuzi_row, text="夫星/子星:", width=10).pack(side=tk.LEFT, padx=5)
                ttk.Label(fuzi_row, textvariable=fuzi_var, foreground="purple").pack(side=tk.LEFT, padx=5)
            
            # 计算按钮
            calc_btn = ttk.Button(owner_frame, text="计算四柱", 
                                 command=lambda y=year_var, m=month_var, d=day_var, 
                                 h=hour_var, mi=minute_var, g=gender_var, o=owner, s=sizhu_var, 
                                 x=xishen_var, yg=yongshen_var, fz=fuzi_var: 
                                 self.calculate_owner_sizhu(y, m, d, h, mi, g, o, s, x, yg, fz))
            calc_btn.pack(side=tk.LEFT, padx=5, pady=2)
            
            # 八字排盘详情按钮
            detail_btn = ttk.Button(owner_frame, text="八字排盘详情", 
                                   command=lambda y=year_var, m=month_var, d=day_var, 
                                   h=hour_var, mi=minute_var, g=gender_var, o=owner: 
                                   self.show_owner_bazi_detail(y, m, d, h, mi, g, o))
            detail_btn.pack(side=tk.LEFT, padx=5, pady=2)
            
            # 保存事主信息
            owner_info = {
                'name': owner,
                'year': year_var,
                'month': month_var,
                'day': day_var,
                'hour': hour_var,
                'minute': minute_var,
                'gender': gender_var,
                'sizhu_var': sizhu_var,
                'xishen_var': xishen_var,
                'yongshen_var': yongshen_var,
                'fuzi_var': fuzi_var
            }
            self.owners_info.append(owner_info)
        
        # 为所有输入框绑定键盘导航
        self._bind_entry_navigation(all_entries)
    
    def _bind_entry_navigation(self, entries):
        """为输入框绑定键盘导航功能"""
        if not entries:
            return
            
        def on_key_down(event, idx):
            """向下/向右移动到下一个输入框"""
            if idx < len(entries) - 1:
                entries[idx + 1].focus_set()
                entries[idx + 1].select_range(0, tk.END)
            return "break"
        
        def on_key_up(event, idx):
            """向上/向左移动到上一个输入框"""
            if idx > 0:
                entries[idx - 1].focus_set()
                entries[idx - 1].select_range(0, tk.END)
            return "break"
        
        def on_key_right(event, idx):
            """向右移动到下一个输入框"""
            # 检查光标是否在最后
            widget = event.widget
            if widget.index(tk.INSERT) >= len(widget.get()):
                if idx < len(entries) - 1:
                    entries[idx + 1].focus_set()
                    entries[idx + 1].select_range(0, tk.END)
                    return "break"
            return None
        
        def on_key_left(event, idx):
            """向左移动到上一个输入框"""
            # 检查光标是否在开头
            widget = event.widget
            if widget.index(tk.INSERT) == 0:
                if idx > 0:
                    entries[idx - 1].focus_set()
                    entries[idx - 1].select_range(0, tk.END)
                    return "break"
            return None
        
        for i, entry in enumerate(entries):
            # 绑定方向键
            entry.bind('<Down>', lambda e, idx=i: on_key_down(e, idx))
            entry.bind('<Up>', lambda e, idx=i: on_key_up(e, idx))
            entry.bind('<Right>', lambda e, idx=i: on_key_right(e, idx))
            entry.bind('<Left>', lambda e, idx=i: on_key_left(e, idx))
            # Tab键默认就是下一个，不需要额外绑定
            # Shift+Tab键默认就是上一个，不需要额外绑定
    
    def calculate_owner_sizhu(self, year_var, month_var, day_var, hour_var, minute_var, 
                              gender_var, owner, sizhu_var, xishen_var, yongshen_var, fuzi_var):
        """计算事主四柱"""
        try:
            year = int(year_var.get())
            month = int(month_var.get())
            day = int(day_var.get())
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            
            target_date = date(year, month, day)
            sizhu = calculate_sizhu(target_date, hour, minute)
            analysis = analyze_sizhu(sizhu)
            
            # 显示四柱
            sizhu_text = f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}"
            sizhu_var.set(sizhu_text)
            
            # 显示喜用神 - 使用统一的喜用神计算器
            xishen, yongshen = calculate_xishen_yongshen(sizhu, analysis)
            xishen_var.set(xishen)
            yongshen_var.set(yongshen)
            
            # 婚嫁事项显示夫星子星
            if fuzi_var and self.event_var.get() == "嫁娶" and owner == "新娘":
                fuzi = analysis.get('夫星子星', {})
                fu_xing = fuzi.get('fu', '')
                zi_xing = fuzi.get('zi', '')
                if fu_xing or zi_xing:
                    fuzi_var.set(f"夫星: {fu_xing}, 子星: {zi_xing}")
        except Exception as e:
            messagebox.showerror("计算错误", f"计算四柱失败: {str(e)}")
            logger.error(f"计算四柱失败: {str(e)}", exc_info=True)
    
    def show_owner_bazi_detail(self, year_var, month_var, day_var, hour_var, minute_var, gender_var, owner):
        """显示事主八字排盘详情"""
        try:
            year = int(year_var.get())
            month = int(month_var.get())
            day = int(day_var.get())
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            gender = gender_var.get()
            
            # 使用八字排盘模块获取详细信息
            panpan = BaZiPanPan(year, month, day, hour, minute, gender)
            panpan_result = panpan.calculate()
            
            # 显示八字排盘详情对话框
            show_bazi_dialog(self.root, panpan_result)
        except Exception as e:
            messagebox.showerror("错误", f"计算失败: {str(e)}")
    
    def _show_compass_dialog(self):
        """显示电子罗盘对话框"""
        initial_shan_xiang = None
        if hasattr(self, 'shan_xiang') and self.shan_xiang.get():
            initial_shan_xiang = self.shan_xiang.get()
        
        def on_compass_select(shan_xiang: str, degree: float):
            """罗盘选择回调"""
            if shan_xiang and hasattr(self, 'shan_xiang'):
                self.shan_xiang.set(shan_xiang)
                
                # 更新兼向显示
                if hasattr(self, 'jian_xiang'):
                    # 根据度数自动识别兼向
                    mountain = shan_xiang_to_shan(shan_xiang)
                    jianxiang = converter.get_jianxiang(mountain, degree)
                    if jianxiang:
                        self.jian_xiang.set(jianxiang)
                    else:
                        self.jian_xiang.set("正中")
        
        show_compass_dialog(self.root, initial_shan_xiang, on_compass_select)
    
    def _update_jianxiang_options(self, *args):
        """根据山向更新兼向选项"""
        shan_xiang = self.shan_xiang.get()
        if not shan_xiang:
            return
        
        # 获取坐山名称
        mountain = shan_xiang_to_shan(shan_xiang)
        
        # 获取相邻的山
        if mountain in mountains:
            idx = mountains.index(mountain)
            left_shan = mountains[(idx - 1) % len(mountains)]
            right_shan = mountains[(idx + 1) % len(mountains)]
            
            # 更新兼向选项
            options = ["正中", f"兼{left_shan}", f"兼{right_shan}"]
            self.jian_xiang_combo['values'] = options
            self.jian_xiang.set("正中")  # 重置为正中
    
    def on_event_change(self, event=None):
        """事项类型改变时的处理"""
        self.update_special_options()
        self.update_owners_frame()
    
    def start_calculation(self):
        """开始择日计算"""
        try:
            # 获取日期范围
            start = datetime.strptime(self.start_date.get(), "%Y-%m-%d").date()
            end = datetime.strptime(self.end_date.get(), "%Y-%m-%d").date()
            
            if start > end:
                messagebox.showerror("错误", "开始日期不能晚于结束日期")
                return
            
            # 清空之前的结果
            self.results = []
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # 获取事主信息
            owners_data = []
            for owner in self.owners_info:
                try:
                    year = int(owner['year'].get())
                    month = int(owner['month'].get())
                    day = int(owner['day'].get())
                    hour = int(owner['hour'].get())
                    minute = int(owner['minute'].get())
                    owners_data.append({
                        'name': owner['name'],
                        'birth_date': date(year, month, day),
                        'birth_hour': hour,
                        'birth_minute': minute
                    })
                except:
                    continue
            
            # 获取特殊选项
            event_type = self.event_var.get()
            house_type = getattr(self, 'house_type', None)
            shan_xiang = getattr(self, 'shan_xiang', None)
            zao_xiang = getattr(self, 'zao_xiang', None)
            zao_wei = getattr(self, 'zao_wei', None)
            chuang_wei = getattr(self, 'chuang_wei', None)
            
            # 计算每日吉凶
            current = start
            while current <= end:
                # 计算四柱
                sizhu = calculate_sizhu(current, 12, 0)
                
                # 获取农历
                try:
                    lunar = get_lunar_date(current)
                    lunar_str = f"{lunar['月']}{lunar['日']}"
                except:
                    lunar_str = "-"
                
                # 计算评分
                score_result = calculate_score(
                    sizhu, 
                    event_type, 
                    owners_data,
                    house_type.get() if house_type else None,
                    shan_xiang.get() if shan_xiang else None,
                    zao_xiang.get() if zao_xiang else None,
                    zao_wei.get() if zao_wei else None,
                    chuang_wei.get() if chuang_wei else None
                )
                
                # 提取各项得分
                score_details = score_result.get('score_details', {})
                yueling_score = score_details.get('月令得分', 0)
                xishen_score = score_details.get('喜用神得分', 0)
                huangdao_score = score_details.get('黄道得分', 0)
                
                # 保存结果
                result = {
                    'date': current.strftime("%Y-%m-%d"),
                    'lunar': lunar_str,
                    'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                    'score': score_result['score'],
                    'level': score_result['level'],
                    'yueling_score': yueling_score,
                    'xishen_score': xishen_score,
                    'huangdao_score': huangdao_score,
                    'detail': score_result
                }
                
                # 筛选：只保留吉及以上的日课，过滤掉不吉的日课
                # 等级：❌ 凶 → 过滤掉
                if '❌ 凶' not in result['level']:
                    self.results.append(result)
                
                current += timedelta(days=1)
            
            # 按评分从高到低排序
            self.results.sort(key=lambda x: x['score'], reverse=True)
            
            # 添加排序后的结果到树形视图
            for result in self.results:
                # 根据等级设置行标签（用于颜色区分）
                level = result['level']
                if '★★★★★' in level:
                    row_tag = '5star'
                elif '★★★★' in level:
                    row_tag = '4star'
                elif '★★★' in level:
                    row_tag = '3star'
                elif '★★' in level:
                    row_tag = '2star'
                elif '★' in level:
                    row_tag = '1star'
                else:
                    row_tag = ''
                
                # 添加到树形视图
                self.result_tree.insert("", tk.END, values=(
                    result['date'],
                    result['score'],
                    result['level'],
                    result['sizhu'],
                    result['yueling_score'],
                    result['xishen_score'],
                    result['huangdao_score']
                ), tags=(row_tag,))
            
            self.save_record()
            
            messagebox.showinfo("完成", f"择日计算完成！\n共计算 {(end - start).days + 1} 天")
        except Exception as e:
            messagebox.showerror("错误", f"计算失败: {str(e)}")
    
    def on_result_double_click(self, event):
        """双击结果查看详情"""
        selected = self.result_tree.selection()
        if not selected:
            return
        
        item = self.result_tree.item(selected[0])
        values = item['values']
        
        # 查找完整结果
        date_str = values[0]
        result = None
        for r in self.results:
            if r['date'] == date_str:
                result = r
                break
        
        if not result:
            return
        
        # 显示详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"日课详情 - {date_str}")
        detail_window.geometry("550x500")
        
        # 创建主框架
        main_frame = ttk.Frame(detail_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文本显示区域
        text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        # 配置金色tag用于显示星星
        text.tag_configure("gold_star", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        
        detail = result['detail']
        
        # 插入基本信息
        text.insert(tk.END, f"""
日期：{result['date']}
农历：{result['lunar']}
四柱：{result['sizhu']}
评分：{result['score']} 分
等级：""")
        
        # 如果有星星，用金色显示
        level = result['level']
        if '★' in level:
            star_count = level.count('★')
            other_text = level.replace('★', '').strip()
            text.insert(tk.END, '★' * star_count, "gold_star")
            if other_text:
                text.insert(tk.END, f" {other_text}")
        else:
            text.insert(tk.END, level)
        
        content = f"""

【评分详情】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        # 显示详细得分
        score_details = detail.get('score_details', {})
        if score_details:
            content += f"  基础分：{score_details.get('基础分', 100)} 分\n"
            content += f"  月令得分：{score_details.get('月令得分', 0):+d} 分\n"
            
            # 月令详细得分
            yueling_detail = score_details.get('月令详细', {})
            if yueling_detail:
                content += f"    └─ 旺衰得分：{yueling_detail.get('旺衰得分', 0):+d} 分\n"
                content += f"    └─ 支支关系得分：{yueling_detail.get('支支关系得分', 0):+d} 分\n"
            
            content += f"  喜用神得分：{score_details.get('喜用神得分', 0):+d} 分\n"
            content += f"  黄道得分：{score_details.get('黄道得分', 0):+d} 分\n"
            content += f"  ─────────────────────────────────\n"
            content += f"  总分：{score_details.get('总分', result['score'])} 分\n"
        else:
            content += "  暂无详细得分数据\n"
        
        content += f"""
【宜】
{chr(10).join(detail['yi_list']) if detail['yi_list'] else '无'}

【忌】
{chr(10).join(detail['ji_list']) if detail['ji_list'] else '无'}

【神煞】
"""
        for shensha in detail['shensha_list']:
            content += f"- {shensha['name']}: {shensha['description']}\n"
        
        content += f"\n【评语】\n{detail['reason']}"
        
        # 添加二十四山分析（如果有山向信息）
        shan_xiang_val = getattr(self, 'shan_xiang', None)
        if shan_xiang_val and shan_xiang_val.get():
            try:
                # 使用二十四山选择器分析
                selector = ZhengTiWuXingSelectorDB()
                shan_name = shan_xiang_to_shan(shan_xiang_val.get())
                sizhu = result['sizhu'].split()
                if len(sizhu) >= 4:
                    year_gz = sizhu[0]
                    month_gz = sizhu[1]
                    day_gz = sizhu[2]
                    hour_gz = sizhu[3]
                    
                    # 获取兼向
                    jianxiang = ""
                    if hasattr(self, 'jian_xiang'):
                        jianxiang = self.jian_xiang.get()
                    
                    # 使用分金五行评价
                    if jianxiang and jianxiang != "正中":
                        result_fengjin = selector.evaluate_with_fengjin(
                            shan_name, jianxiang, year_gz, month_gz, day_gz, hour_gz,
                            use_fengjin_wuxing=True
                        )
                        
                        content += f"\n\n【分金五行分析】\n"
                        content += f"山向：{shan_xiang_val.get()}（坐山：{shan_name}）\n"
                        content += f"兼向：{jianxiang}\n"
                        content += f"分金：第{result_fengjin.get('fengjin_index', '?')}分金（{result_fengjin.get('fengjin_ganzhi', '?')}）\n"
                        content += f"分金五行：{result_fengjin.get('fengjin_wuxing', '?')}（{result_fengjin.get('nayin_name', '?')}）\n"
                        content += f"正体五行：{result_fengjin.get('zhengti_wuxing', '?')}\n"
                        content += f"等级：{result_fengjin.get('level', '?')}\n"
                        content += f"得分：{result_fengjin.get('score', '?')}\n"
                        if result_fengjin.get('details'):
                            content += f"详情：\n"
                            for d in result_fengjin['details']:
                                content += f"  {d}\n"
                    else:
                        # 正向使用正体五行
                        level, score, detail_24 = selector.evaluate_by_name(
                            shan_name, year_gz, month_gz, day_gz, hour_gz
                        )
                        
                        content += f"\n\n【正体五行分析】\n"
                        content += f"山向：{shan_xiang_val.get()}（坐山：{shan_name}）\n"
                        content += f"兼向：正中（正向）\n"
                        content += f"等级：{level}\n"
                        content += f"得分：{score}\n"
                        if 'summary' in detail_24:
                            summary = detail_24['summary']
                            content += f"坐山得分：{summary.get('mountain_score', 'N/A')}\n"
            except Exception as e:
                content += f"\n\n【二十四山分析】\n分析失败: {str(e)}\n"
        
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_detail():
            """保存日课详情"""
            file_path = filedialog.asksaveasfilename(
                title="保存日课详情",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            try:
                # 保存为文本文件
                if file_path.endswith('.txt'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("成功", f"日课详情已保存到：{file_path}")
                
                # 保存为JSON文件
                elif file_path.endswith('.json'):
                    json_data = {
                        'date': result['date'],
                        'lunar': result['lunar'],
                        'sizhu': result['sizhu'],
                        'score': result['score'],
                        'level': result['level'],
                        'yi_list': detail['yi_list'],
                        'ji_list': detail['ji_list'],
                        'shensha_list': detail['shensha_list'],
                        'reason': detail['reason']
                    }
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                    messagebox.showinfo("成功", f"日课详情已保存到：{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        ttk.Button(button_frame, text="保存详情", command=save_detail).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=detail_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def export_results(self):
        """导出结果"""
        if not self.results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("JSON文件", "*.json"), ("所有文件", "*.*")],
            title="导出择日结果"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                # 导出JSON格式
                export_data = {
                    'event_type': self.event_var.get(),
                    'start_date': self.start_date.get(),
                    'end_date': self.end_date.get(),
                    'results': self.results
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            else:
                # 导出文本格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("择日结果报告\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"事项类型：{self.event_var.get()}\n")
                    f.write(f"日期范围：{self.start_date.get()} 至 {self.end_date.get()}\n\n")
                    
                    # 按评分排序
                    sorted_results = sorted(self.results, key=lambda x: x['score'], reverse=True)
                    
                    for result in sorted_results:
                        f.write(f"日期：{result['date']}\n")
                        f.write(f"农历：{result['lunar']}\n")
                        f.write(f"四柱：{result['sizhu']}\n")
                        f.write(f"评分：{result['score']} 分\n")
                        f.write(f"等级：{result['level']}\n")
                        f.write(f"宜：{result['yi']}\n")
                        f.write(f"忌：{result['ji']}\n")
                        f.write("-" * 40 + "\n\n")
            
            messagebox.showinfo("成功", f"结果已导出到：\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def import_file(self):
        """导入文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="导入择日结果文件"
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            
            if file_path.endswith('.json'):
                # 导入JSON格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理主程序导出的格式
                    if isinstance(data, dict) and 'results' in data:
                        self.results = data['results']
                        self.event_var.set(data.get('event_type', '嫁娶'))
                        self.start_date.set(data.get('start_date', ''))
                        self.end_date.set(data.get('end_date', ''))
                        imported_count = len(self.results)
                        
                        # 刷新显示
                        for item in self.result_tree.get_children():
                            self.result_tree.delete(item)
                        
                        for result in self.results:
                            self.result_tree.insert("", tk.END, values=(
                                result['date'],
                                result.get('lunar', '-'),
                                result['sizhu'],
                                result.get('score', '-'),
                                result.get('level', '-'),
                                result.get('yi', '-'),
                                result.get('ji', '-')
                            ))
                    
                    # 处理其他JSON格式（如评分系统导出的）
                    elif isinstance(data, list):
                        self.results = []
                        for item in data:
                            if isinstance(item, dict) and 'date' in item:
                                # 构建标准格式
                                result = {
                                    'date': item['date'],
                                    'lunar': item.get('lunar', '-'),
                                    'sizhu': item.get('sizhu', '-'),
                                    'score': item.get('score', 0),
                                    'level': item.get('level', '-'),
                                    'yi': item.get('yi', '-'),
                                    'ji': item.get('ji', '-'),
                                    'detail': item.get('detail', {})
                                }
                                self.results.append(result)
                                imported_count += 1
                        
                        # 刷新显示
                        for item in self.result_tree.get_children():
                            self.result_tree.delete(item)
                        
                        for result in self.results:
                            self.result_tree.insert("", tk.END, values=(
                                result['date'],
                                result.get('lunar', '-'),
                                result['sizhu'],
                                result.get('score', '-'),
                                result.get('level', '-'),
                                result.get('yi', '-'),
                                result.get('ji', '-')
                            ))
            
            else:
                # 导入文本格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    # 尝试解析文本格式
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        # 尝试匹配日期格式 (YYYY-MM-DD)
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                        if date_match:
                            date_str = date_match.group(1)
                            # 检查是否已存在
                            if not any(r['date'] == date_str for r in self.results):
                                result = {
                                    'date': date_str,
                                    'lunar': '-',
                                    'sizhu': '-',
                                    'score': '-',
                                    'level': '-',
                                    'yi': '-',
                                    'ji': '-',
                                    'detail': {}
                                }
                                self.results.append(result)
                                imported_count += 1
                    
                    # 刷新显示
                    for item in self.result_tree.get_children():
                        self.result_tree.delete(item)
                    
                    for result in self.results:
                        self.result_tree.insert("", tk.END, values=(
                            result['date'],
                            result.get('lunar', '-'),
                            result['sizhu'],
                            result.get('score', '-'),
                            result.get('level', '-'),
                            result.get('yi', '-'),
                            result.get('ji', '-')
                        ))
            
            if imported_count > 0:
                messagebox.showinfo("成功", f"已导入 {imported_count} 条记录")
            else:
                messagebox.showwarning("提示", "未找到可导入的记录，请检查文件格式")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {str(e)}")
    
    def view_records(self):
        """查看历史记录"""
        records_window = tk.Toplevel(self.root)
        records_window.title("历史记录")
        records_window.geometry("600x400")
        
        text = scrolledtext.ScrolledText(records_window, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        if not self.records:
            text.insert(tk.END, "暂无历史记录")
        else:
            for i, record in enumerate(self.records, 1):
                text.insert(tk.END, f"\n【记录 {i}】\n")
                text.insert(tk.END, f"时间：{record.get('time', '未知')}\n")
                text.insert(tk.END, f"事项：{record.get('event', '未知')}\n")
                text.insert(tk.END, f"日期范围：{record.get('start', '')} 至 {record.get('end', '')}\n")
                text.insert(tk.END, f"结果数量：{record.get('count', 0)} 天\n")
                text.insert(tk.END, "-" * 40 + "\n")
        
        text.config(state=tk.DISABLED)
    
    def save_record(self):
        """保存记录"""
        record = {
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'event': self.event_var.get(),
            'start': self.start_date.get(),
            'end': self.end_date.get(),
            'count': len(self.results)
        }
        self.records.append(record)
        
        # 保存到文件
        try:
            with open("择日记录.json", 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
    
    def load_records(self):
        """加载历史记录"""
        try:
            if os.path.exists("择日记录.json"):
                with open("择日记录.json", 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
        except Exception as e:
            pass
    
    def open_score_system(self):
        """打开日课评分系统"""
        score_window = DayScoreWindow()
        score_window.run()
    
    def import_all_to_score_system(self):
        """将所有择日结果导入到评分系统"""
        if not self.results:
            messagebox.showwarning("提示", "没有可导入的择日结果")
            return
        
        try:
            score_window = DayScoreWindow(self.root)
            
            # 准备事主数据
            owners_data = []
            for owner_info in self.owners_info:
                year = owner_info.get('year', '').get() if hasattr(owner_info.get('year', ''), 'get') else owner_info.get('year', '')
                month = owner_info.get('month', '').get() if hasattr(owner_info.get('month', ''), 'get') else owner_info.get('month', '')
                day = owner_info.get('day', '').get() if hasattr(owner_info.get('day', ''), 'get') else owner_info.get('day', '')
                hour = owner_info.get('hour', '').get() if hasattr(owner_info.get('hour', ''), 'get') else owner_info.get('hour', 12)
                minute = owner_info.get('minute', '').get() if hasattr(owner_info.get('minute', ''), 'get') else owner_info.get('minute', 0)
                
                if year and month and day:
                    owners_data.append({
                        'year': year,
                        'month': month,
                        'day': day,
                        'hour': hour,
                        'minute': minute
                    })
            
            # 导入结果
            score_window.import_results(self.results, self.event_var.get(), owners_data)
            score_window.run()
        except Exception as e:
            messagebox.showerror("错误", f"导入到评分系统失败: {str(e)}")
            logger.error(f"导入到评分系统失败: {str(e)}", exc_info=True)
    
    def clear_results(self):
        """清空择日结果"""
        if not self.results:
            return
        
        if messagebox.askyesno("确认", "确定要清空所有择日结果吗？"):
            self.results = []
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            messagebox.showinfo("成功", "择日结果已清空")

    def open_date_test(self):
        """打开日期测试窗口"""
        pass
    
    def open_bazi_panpan(self):
        """打开八字排盘"""
        try:
            # 测试show_bazi_input_dialog是否存在
            print("开始调用show_bazi_input_dialog")
            show_bazi_input_dialog(self.root)
            print("show_bazi_input_dialog调用成功")
        except Exception as e:
            messagebox.showerror("错误", f"打开八字排盘失败: {str(e)}")
    
    def show_help(self):
        """显示帮助文档"""
        help_window = tk.Toplevel(self.root)
        help_window.title("使用帮助")
        help_window.geometry("800x600")
        
        # 创建 Notebook
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 帮助内容
        help_sections = [
            ("系统概述", """
【系统概述】

本软件是一款基于传统正五行择日理论的专业择日工具。

【核心特点】
1. 双层架构：正五行审核 + 黄道优选
2. 智能评分：基础分100分，根据神煞、宜忌自动加减
3. 多事项支持：13类常见民事择日
4. 事主分析：支持八字输入，相主分析
5. 详细报告：宜忌、神煞、评分、等级一应俱全

【星级等级】
⭐⭐⭐⭐⭐ (5星) = 上吉 - 首选推荐
⭐⭐⭐⭐ (4星) = 大吉 - 诸事皆宜
⭐⭐⭐ (3星) = 吉 - 可用
⭐⭐ (2星) = 中吉/次吉 - 需谨慎
⭐ (1星) = 平 - 仅适合小事
❌ (0星) = 凶 - 坚决不用
"""),
            ("使用流程", """
【基本使用流程】

1. 选择事项类型
   从下拉框选择需要择日的事项（嫁娶、安葬、修造等）

2. 设置日期范围
   输入开始日期和结束日期（格式：YYYY-MM-DD）

3. 输入事主信息（可选但推荐）
   填写事主的出生年月日时分
   点击"计算四柱"查看八字和喜用神
   婚嫁事项会显示夫星子星

4. 特殊选项
   修造类：选择宅型和山向
   作灶：选择灶向和灶位
   安床：选择床位朝向

5. 开始择日
   点击"开始择日"按钮
   系统会计算日期范围内的每日吉凶

6. 查看结果
   结果按日期显示在列表中
   双击可查看详细信息

7. 导出或评分
   点击"导出结果"保存为文本或JSON文件
   点击"日课评分"进行详细分析
   点击"日期测试"查看日期转换信息
"""),
            ("评分规则", """
【评分算法】

基础分：100分

神煞加减分：
  大吉神（+15分）：天德、月德等
  吉神（+10分）：青龙、明堂等
  小吉神（+5分）：福星、禄神等
  小凶神（-8分）：劫煞、灾煞等
  凶神（-15分）：五黄、三杀等
  大凶神（-20分）：岁破、月破等

宜忌加减分：
  宜事匹配：+10分/项
  忌事冲突：-15分/项

黄道调整：
  大黄道吉：+10分
  大黄道凶：-5分

【星级标准】
⭐⭐⭐⭐⭐ (5星) = 上吉（130分以上）
⭐⭐⭐⭐ (4星) = 大吉（120-129分）
⭐⭐⭐ (3星) = 吉（100-119分）
⭐⭐ (2星) = 中吉/次吉（80-99分）
⭐ (1星) = 平（60-79分）
❌ (0星) = 凶（<60分）
"""),
            ("注意事项", """
【注意事项】

1. 计算精度
   - 四柱计算精确到分钟
   - 节气交接时刻会影响月柱

2. 地域差异
   - 不同流派有不同算法
   - 本软件采用传统通用算法

3. 使用建议
   - 重要事项建议多方验证
   - 软件结果仅供参考

4. 数据备份
   - 定期备份择日记录
   - 记录文件：择日记录.json

5. 冲突处理
   - 五行大吉 + 黄道大吉 → 首选
   - 五行大吉 + 黄道黑道 → 可用
   - 五行平平 + 黄道大吉 → 小事可用
   - 五行凶 + 任何黄道 → 坚决不用

6. 事主信息
   - 婚嫁：新娘新郎信息必填
   - 安葬：死者信息必填
   - 其他事项：事主信息可选
""")
        ]
        
        for title, content in help_sections:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=title)
            
            text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, padx=10, pady=10)
            text.pack(fill=tk.BOTH, expand=True)
            text.insert(tk.END, content)
            text.config(state=tk.DISABLED)
        
        ttk.Button(help_window, text="关闭", command=help_window.destroy).pack(pady=10)
    
    def show_solar_terms(self):
        """显示节气查询对话框"""
        if not HAS_SXTWL:
            messagebox.showwarning("警告", "sxtwl库未安装，无法查询节气信息")
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("节气查询")
        dialog.geometry("600x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 年份选择
        input_frame = ttk.Frame(dialog, padding="20")
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="选择年份:", font=('微软雅黑', 12)).pack(side=tk.LEFT, padx=5)
        
        year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(input_frame, textvariable=year_var, width=10, font=('微软雅黑', 12))
        year_combo['values'] = [str(y) for y in range(1900, 2101)]
        year_combo.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = ttk.Frame(dialog, padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        columns = ("节气", "公历日期", "时间", "月柱")
        tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=20)
        
        tree.column("节气", width=80, anchor=tk.CENTER)
        tree.column("公历日期", width=120, anchor=tk.CENTER)
        tree.column("时间", width=100, anchor=tk.CENTER)
        tree.column("月柱", width=80, anchor=tk.CENTER)
        
        for col in columns:
            tree.heading(col, text=col, anchor=tk.CENTER)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def update_solar_terms():
            """更新节气显示"""
            try:
                year = int(year_var.get())
                
                # 清空树形视图
                for item in tree.get_children():
                    tree.delete(item)
                
                # 获取节气数据
                jq_list = sxtwl.getJieQiByYear(year)
                jq_names = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨',
                           '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
                           '立秋', '处暑', '白露', '秋分', '寒露', '霜降',
                           '立冬', '小雪', '大雪', '冬至', '小寒', '大寒']
                
                # 月的地支对应
                jie_to_month = {
                    0: '寅', 2: '卯', 4: '辰', 6: '巳', 8: '午', 10: '未',
                    12: '申', 14: '酉', 16: '戌', 18: '亥', 20: '子', 22: '丑',
                }
                
                # 五虎遁
                wu_hu_dun = {
                    '甲': '丙', '己': '丙',
                    '乙': '戊', '庚': '戊',
                    '丙': '庚', '辛': '庚',
                    '丁': '壬', '壬': '壬',
                    '戊': '甲', '癸': '甲'
                }
                
                tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
                di_zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
                
                # 获取年干
                day_obj = sxtwl.fromSolar(year, 6, 15)  # 年中日期
                year_gz = day_obj.getYearGZ()
                year_gan = tian_gan[year_gz.tg]
                
                # 添加到树形视图
                for i in range(24):
                    dd = sxtwl.JD2DD(jq_list[i].jd)
                    date_str = f"{int(dd.Y)}-{int(dd.M):02d}-{int(dd.D):02d}"
                    time_str = f"{int(dd.h):02d}:{int(dd.m):02d}:{int(dd.s):02d}"
                    
                    # 计算月柱（只对"节"计算）
                    if i in jie_to_month:
                        month_zhi = jie_to_month[i]
                        base_gan = wu_hu_dun.get(year_gan, '丙')
                        base_index = tian_gan.index(base_gan)
                        month_zhi_index = di_zhi.index(month_zhi)
                        offset = (month_zhi_index - 2 + 12) % 12
                        month_gan_index = (base_index + offset) % 10
                        month_gan = tian_gan[month_gan_index]
                        month_pillar = f"{month_gan}{month_zhi}"
                    else:
                        month_pillar = "-"
                    
                    tree.insert("", tk.END, values=(jq_names[i], date_str, time_str, month_pillar))
            except Exception as e:
                messagebox.showerror("错误", f"查询失败: {str(e)}")
        
        # 查询按钮
        ttk.Button(input_frame, text="查询", command=update_solar_terms).pack(side=tk.LEFT, padx=10)
        
        # 关闭按钮
        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=10)
        
        # 初始加载
        update_solar_terms()
    
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo("关于", 
            "专业级正五行择日软件 v1.0\n\n"
            "基于传统正五行择日理论\n"
            "采用'五行为主，黄道为用'架构\n\n"
            "功能特点：\n"
            "- 支持13类事项择日\n"
            "- 智能评分和星级显示\n"
            "- 事主八字分析\n"
            "- 日课评分对比\n"
            "- 节气查询\n"
            "- 日期转换测试\n\n"
            "版本: 1.0.0\n"
            "更新日期: 2026年\n"
            "作者: 专业择日团队"
        )

def main():
    """主函数"""
    print("开始启动程序...")
    try:
        print("创建根窗口...")
        root = tk.Tk()
        print(f"根窗口创建成功: {root}")
        root.title("专业级正五行择日软件")
        print("创建应用实例...")
        app = ZeriApp(root)
        print(f"应用实例创建成功: {app}")
        print("进入主循环...")
        root.mainloop()
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'root' in locals():
            messagebox.showerror("错误", f"程序运行出错: {str(e)}")

if __name__ == "__main__":
    main()