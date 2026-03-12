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
    try:
        from .八字分析工具 import get_shishen as new_get_shishen
        return new_get_shishen(day_gan, target_gan)
    except ImportError:
        # 回退到旧算法
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
        day_wx = TIAN_GAN_WUXING[day_gan]
        target_wx = TIAN_GAN_WUXING[target_gan]
        
        # 同我
        if target_wx == day_wx:
            return '劫财'
        
        # 我生
        if WUXING_SHENG.get(day_wx) == target_wx:
            return '食神' if is_same_yin_yang else '伤官'
        
        # 我克
        if WUXING_KE.get(day_wx) == target_wx:
            return '偏财' if is_same_yin_yang else '正财'
        
        # 克我
        if WUXING_KE.get(target_wx) == day_wx:
            return '七杀' if is_same_yin_yang else '正官'
        
        # 生我
        if WUXING_SHENG.get(target_wx) == day_wx:
            return '偏印' if is_same_yin_yang else '正印'
        
        return '未知'

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

try:
    from .八字工具整合 import (
        # 数据定义
        GAN_WUXING,
        ZHI_WUXING,
        GAN_YINYANG,
        ZHI_YINYANG,
        ZHIGAN_WEIGHTED,
        ZHIGAN_SIMPLE,
        # 函数
        get_gan_wuxing as _get_gan_wuxing_new,
        get_zhi_wuxing as _get_zhi_wuxing_new,
        get_shishen as _get_shishen_new,
        calculate_wuxing_score,
        get_zhangsheng,
        get_nayin,
        check_liuhe,
        check_liuchong,
        check_liuhai,
        check_sanxing,
        check_sanhe,
        check_sanhui,
    )
    
    # 导出给外部使用
    __all__ = [
        # 基础数据
        'TIAN_GAN', 'DI_ZHI',
        'TIAN_GAN_WUXING', 'DI_ZHI_WUXING',
        'GAN_WUXING', 'ZHI_WUXING',
        'GAN_YINYANG', 'ZHI_YINYANG',
        'WUXING_SHENG', 'WUXING_KE',
        'CHONG', 'HE',
        'WU_HU_DUN', 'WU_SHU_DUN',
        'TIANDE', 'YUEDE',
        'SANSHA_MAP',
        'FU_ZI_XING',
        'SHAN_XIANG_24', 'SHAN_XIANG_LIST', 'SHAN_XIANG_WUXING',
        'SHISHEN',
        # 基础函数
        'get_gan_wuxing', 'get_zhi_wuxing',
        'get_pillar_wuxing', 'get_shengke',
        'get_hour_zhi_index', 'get_shishen',
        'get_fuzi',
        'format_date', 'format_datetime',
        # 八字工具整合的增强功能
        'ZHIGAN_WEIGHTED', 'ZHIGAN_SIMPLE',
        'calculate_wuxing_score',
        'get_zhangsheng', 'get_nayin',
        'check_liuhe', 'check_liuchong', 'check_liuhai',
        'check_sanxing', 'check_sanhe', 'check_sanhui',
    ]
    
    _BAZI_TOOLS_AVAILABLE = True
    
except ImportError:
    _BAZI_TOOLS_AVAILABLE = False
    __all__ = [
        'TIAN_GAN', 'DI_ZHI',
        'TIAN_GAN_WUXING', 'DI_ZHI_WUXING',
        'WUXING_SHENG', 'WUXING_KE',
        'CHONG', 'HE',
        'WU_HU_DUN', 'WU_SHU_DUN',
        'TIANDE', 'YUEDE',
        'SANSHA_MAP',
        'FU_ZI_XING',
        'SHAN_XIANG_24', 'SHAN_XIANG_LIST', 'SHAN_XIANG_WUXING',
        'SHISHEN',
        'get_gan_wuxing', 'get_zhi_wuxing',
        'get_pillar_wuxing', 'get_shengke',
        'get_hour_zhi_index', 'get_shishen',
        'get_fuzi',
        'format_date', 'format_datetime',
    ]
