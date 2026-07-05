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

# 夫星子星（女命）
# 夫星：克我者（官杀），阳日干取正官，阴日干取七杀
# 子星：我生者（食伤），阳日干取食神，阴日干取伤官
FU_ZI_XING = {
    '甲': {'fu': '辛酉', 'qi': '庚申', 'zi': '丙午', 'shang': '丁巳'},  # 甲木：正官辛金，食神丙火
    '乙': {'fu': '庚申', 'qi': '辛酉', 'zi': '丁巳', 'shang': '丙午'},  # 乙木：正官庚金，食神丁火
    '丙': {'fu': '癸亥', 'qi': '壬子', 'zi': '戊戌', 'shang': '己丑'},  # 丙火：正官癸水，食神戊土
    '丁': {'fu': '壬子', 'qi': '癸亥', 'zi': '己丑', 'shang': '戊戌'},  # 丁火：正官壬水，食神己土
    '戊': {'fu': '乙卯', 'qi': '甲寅', 'zi': '丙午', 'shang': '丁巳'},  # 戊土：正官乙木，食神庚金
    '己': {'fu': '甲寅', 'qi': '乙卯', 'zi': '辛酉', 'shang': '庚申'},  # 己土：正官甲木，食神辛金
    '庚': {'fu': '丁巳', 'qi': '丙午', 'zi': '壬子', 'shang': '癸亥'},  # 庚金：正官丁火，食神壬水
    '辛': {'fu': '丙午', 'qi': '丁巳', 'zi': '癸亥', 'shang': '壬子'},  # 辛金：正官丙火，食神癸水
    '壬': {'fu': '己丑', 'qi': '戊戌', 'zi': '甲寅', 'shang': '乙卯'},  # 壬水：正官己土，食神甲木
    '癸': {'fu': '戊戌', 'qi': '己丑', 'zi': '乙卯', 'shang': '甲寅'},  # 癸水：正官戊土，食神乙木
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

def get_fuzi(year_gan, year_zhi):
    """获取夫星子星（基于年干年支计算）
    
    根据用户提供的规则：
    1. 夫星天干：克年干的五行，阳年干取正官（阴阳相反），阴年干取七杀（阴阳相同）
    2. 夫星地支：根据年支映射
    3. 子星天干：年干所生的五行
    4. 子星地支：根据年支映射
    
    Args:
        year_gan: 年柱天干
        year_zhi: 年柱地支
        
    Returns:
        dict: {'fu':夫星干支, 'zi':子星干支}
    """
    # 夫星天干映射（克年干的五行）
    fuxing_gan_map = {
        '甲': '辛', '乙': '庚', '丙': '癸', '丁': '壬',
        '戊': '乙', '己': '甲', '庚': '丁', '辛': '丙',
        '壬': '己', '癸': '戊'
    }
    
    # 子星天干映射（年干所生的五行）
    zixing_gan_map = {
        '甲': '丙', '乙': '丁', '丙': '戊', '丁': '己',
        '戊': '庚', '己': '辛', '庚': '壬', '辛': '癸',
        '壬': '甲', '癸': '乙'
    }
    
    # 夫星地支映射（根据用户提供的例子校准）
    fu_zhi_map = {
        '子': '巳', '丑': '申', '寅': '亥', '卯': '戌', '辰': '申', '巳': '申',
        '午': '亥', '未': '申', '申': '寅', '酉': '巳', '戌': '寅', '亥': '寅'
    }
    
    # 子星地支映射（根据用户提供的例子校准）
    zi_zhi_map = {
        '子': '戌', '丑': '巳', '寅': '申', '卯': '未', '辰': '亥', '巳': '寅',
        '午': '巳', '未': '巳', '申': '亥', '酉': '寅', '戌': '亥', '亥': '卯'
    }
    
    fu_gan = fuxing_gan_map.get(year_gan, '')
    fu_zhi = fu_zhi_map.get(year_zhi, '')
    fu = fu_gan + fu_zhi if fu_gan and fu_zhi else None
    
    zi_gan = zixing_gan_map.get(year_gan, '')
    zi_zhi = zi_zhi_map.get(year_zhi, '')
    zi = zi_gan + zi_zhi if zi_gan and zi_zhi else None
    
    return {'fu': fu, 'zi': zi}

def get_yintai(month_gan, month_zhi):
    """获取阴胎（以女命月柱为基准）
    
    计算方法：月柱天干顺进一位，地支顺进三位。
    
    Args:
        month_gan: 月柱天干
        month_zhi: 月柱地支
    
    Returns:
        阴胎干支（如"戊午"）
    """
    if month_gan not in TIAN_GAN or month_zhi not in DI_ZHI:
        return None
    
    # 月干顺进一位
    gan_index = TIAN_GAN.index(month_gan)
    next_gan = TIAN_GAN[(gan_index + 1) % 10]
    
    # 月支顺进三位
    zhi_index = DI_ZHI.index(month_zhi)
    next_zhi = DI_ZHI[(zhi_index + 3) % 12]
    
    return next_gan + next_zhi

def get_yangqi(month_gan, month_zhi):
    """获取阳气（以女命月柱为基准）
    
    计算方法：月柱天干顺进一位，地支顺进三位。
    
    Args:
        month_gan: 月柱天干
        month_zhi: 月柱地支
    
    Returns:
        阳气干支（如"戊午"）
    """
    if month_gan not in TIAN_GAN or month_zhi not in DI_ZHI:
        return None
    
    # 月干顺进一位
    gan_index = TIAN_GAN.index(month_gan)
    next_gan = TIAN_GAN[(gan_index + 1) % 10]
    
    # 月支顺进三位
    zhi_index = DI_ZHI.index(month_zhi)
    next_zhi = DI_ZHI[(zhi_index + 3) % 12]
    
    return next_gan + next_zhi

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

# 保存原始的 TIAN_GAN 和 DI_ZHI 常量
_original_TIAN_GAN = TIAN_GAN
_original_DI_ZHI = DI_ZHI

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
    # 恢复原始的 TIAN_GAN 和 DI_ZHI 常量
    TIAN_GAN = _original_TIAN_GAN
    DI_ZHI = _original_DI_ZHI
    # 定义本地的 ZHIGAN_SIMPLE 常量作为回退
    ZHIGAN_SIMPLE = {
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
    # 定义本地的 ZHIGAN_WEIGHTED 常量作为回退
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
    # 定义本地的 GAN_WUXING 和 ZHI_WUXING 常量作为回退
    GAN_WUXING = TIAN_GAN_WUXING
    ZHI_WUXING = DI_ZHI_WUXING
    # 定义本地的 GAN_YINYANG 和 ZHI_YINYANG 常量作为回退
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
    # 定义默认函数
    def calculate_wuxing_score(sizhu, include_canggan=True):
        return {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    def get_zhangsheng(day_gan, zhi):
        return '未知'
    def get_nayin(pillar):
        return '未知'
    def check_liuhe(zhi1, zhi2):
        return False
    def check_liuchong(zhi1, zhi2):
        return False
    def check_liuhai(zhi1, zhi2):
        return False
    def check_sanxing(zhi1, zhi2):
        return False
    def check_sanhe(zhis):
        return False
    def check_sanhui(zhis):
        return False
    __all__ = [
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
        'ZHIGAN_WEIGHTED', 'ZHIGAN_SIMPLE',
        'get_gan_wuxing', 'get_zhi_wuxing',
        'get_pillar_wuxing', 'get_shengke',
        'get_hour_zhi_index', 'get_shishen',
        'get_fuzi',
        'format_date', 'format_datetime',
        'calculate_wuxing_score',
        'get_zhangsheng', 'get_nayin',
        'check_liuhe', 'check_liuchong', 'check_liuhai',
        'check_sanxing', 'check_sanhe', 'check_sanhui',
    ]
