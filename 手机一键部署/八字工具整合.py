# -*- coding: utf-8 -*-
"""
================================================================================
八字工具整合模块
================================================================================
整合八字相关的工具函数和数据，为其他模块提供统一的接口
================================================================================
"""

# 天干地支基础数据
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 五行属性
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

# 藏干表（简单版）
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

# 藏干表（加权版）
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

# 十神定义
SHISHEN = ['比肩', '劫财', '食神', '伤官', '偏财', '正财', '七杀', '正官', '偏印', '正印']

# 十二长生状态
ZHANGSHENG_STATES = ['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养']

# 十二长生表
ZHANGSHENG_MAP = {
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

# 纳音五行表
NAYIN_MAP = {
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

# 六合关系
LIUHE_PAIRS = [('子', '丑'), ('寅', '亥'), ('卯', '戌'), ('辰', '酉'), ('巳', '申'), ('午', '未')]

# 六冲关系
LIUCHONG_PAIRS = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]

# 六害关系
LIUHAI_PAIRS = [('子', '未'), ('丑', '午'), ('寅', '巳'), ('卯', '辰'), ('申', '亥'), ('酉', '戌')]

# 三刑关系
SANXING_GROUPS = [
    (['寅', '巳', '申'], '无恩之刑'),
    (['丑', '戌', '未'], '恃势之刑'),
    (['子', '卯'], '无礼之刑'),
    (['辰', '午', '酉', '亥'], '自刑')
]

# 三合关系
SANHE_GROUPS = {
    ('申', '子', '辰'): '水局',
    ('寅', '午', '戌'): '火局',
    ('亥', '卯', '未'): '木局',
    ('巳', '酉', '丑'): '金局'
}

# 三会关系
SANHUI_GROUPS = {
    ('寅', '卯', '辰'): '东方木',
    ('巳', '午', '未'): '南方火',
    ('申', '酉', '戌'): '西方金',
    ('亥', '子', '丑'): '北方水'
}


def get_gan_wuxing(gan):
    """获取天干五行"""
    return GAN_WUXING.get(gan, '')


def get_zhi_wuxing(zhi):
    """获取地支五行"""
    return ZHI_WUXING.get(zhi, '')


def get_shishen(day_gan, target_gan):
    """
    计算十神
    
    Args:
        day_gan: 日干
        target_gan: 目标天干
        
    Returns:
        str: 十神名称
    """
    if day_gan not in TIAN_GAN or target_gan not in TIAN_GAN:
        return '未知'
    
    day_idx = TIAN_GAN.index(day_gan)
    target_idx = TIAN_GAN.index(target_gan)
    diff = (target_idx - day_idx) % 10
    
    # 十神对应关系
    shishen_map = {
        0: '比肩', 1: '劫财', 2: '食神', 3: '伤官', 4: '偏财',
        5: '正财', 6: '七杀', 7: '正官', 8: '偏印', 9: '正印'
    }
    
    return shishen_map.get(diff, '未知')


def get_zhangsheng(day_gan, zhi):
    """
    获取十二长生状态
    
    Args:
        day_gan: 日干
        zhi: 地支
        
    Returns:
        str: 长生状态
    """
    if day_gan not in ZHANGSHENG_MAP:
        return '未知'
    
    zhi_list = ZHANGSHENG_MAP[day_gan]
    if zhi not in zhi_list:
        return '未知'
    
    idx = zhi_list.index(zhi)
    return ZHANGSHENG_STATES[idx]


def get_nayin(pillar):
    """
    获取纳音五行
    
    Args:
        pillar: 干支柱（如"甲子"）
        
    Returns:
        str: 纳音五行
    """
    return NAYIN_MAP.get(pillar, '未知')


def check_liuhe(zhi1, zhi2):
    """
    检查六合
    
    Args:
        zhi1: 地支1
        zhi2: 地支2
        
    Returns:
        bool: 是否六合
    """
    return (zhi1, zhi2) in LIUHE_PAIRS or (zhi2, zhi1) in LIUHE_PAIRS


def check_liuchong(zhi1, zhi2):
    """
    检查六冲
    
    Args:
        zhi1: 地支1
        zhi2: 地支2
        
    Returns:
        bool: 是否六冲
    """
    return (zhi1, zhi2) in LIUCHONG_PAIRS or (zhi2, zhi1) in LIUCHONG_PAIRS


def check_liuhai(zhi1, zhi2):
    """
    检查六害
    
    Args:
        zhi1: 地支1
        zhi2: 地支2
        
    Returns:
        bool: 是否六害
    """
    return (zhi1, zhi2) in LIUHAI_PAIRS or (zhi2, zhi1) in LIUHAI_PAIRS


def check_sanxing(zhi1, zhi2):
    """
    检查三刑
    
    Args:
        zhi1: 地支1
        zhi2: 地支2
        
    Returns:
        str: 三刑类型或None
    """
    for group, name in SANXING_GROUPS:
        if zhi1 in group and zhi2 in group:
            return name
    return None


def check_sanhe(zhis):
    """
    检查三合
    
    Args:
        zhis: 地支列表
        
    Returns:
        str: 三合局名称或None
    """
    # 排序地支列表
    sorted_zhis = sorted(zhis)
    for group, name in SANHE_GROUPS.items():
        if sorted(group) == sorted_zhis:
            return name
    return None


def check_sanhui(zhis):
    """
    检查三会
    
    Args:
        zhis: 地支列表
        
    Returns:
        str: 三会局名称或None
    """
    # 排序地支列表
    sorted_zhis = sorted(zhis)
    for group, name in SANHUI_GROUPS.items():
        if sorted(group) == sorted_zhis:
            return name
    return None


def calculate_wuxing_score(sizhu, include_canggan=True):
    """
    计算五行分数
    
    Args:
        sizhu: 四柱信息
        include_canggan: 是否包含藏干
        
    Returns:
        dict: 各五行分数
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
            if include_canggan and zhi in ZHIGAN_WEIGHTED:
                for gan, weight in ZHIGAN_WEIGHTED[zhi]:
                    wx = GAN_WUXING.get(gan, '')
                    if wx:
                        scores[wx] += weight * 0.5
    
    return scores


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("八字工具整合模块测试")
    print("=" * 60)
    
    # 测试五行获取
    print("\n【五行测试】")
    print(f"甲的五行: {get_gan_wuxing('甲')}")
    print(f"子的五行: {get_zhi_wuxing('子')}")
    
    # 测试十神
    print("\n【十神测试】")
    print(f"甲见甲: {get_shishen('甲', '甲')}")
    print(f"甲见乙: {get_shishen('甲', '乙')}")
    print(f"甲见丙: {get_shishen('甲', '丙')}")
    
    # 测试十二长生
    print("\n【十二长生测试】")
    print(f"甲见亥: {get_zhangsheng('甲', '亥')}")
    print(f"甲见子: {get_zhangsheng('甲', '子')}")
    
    # 测试纳音
    print("\n【纳音测试】")
    print(f"甲子: {get_nayin('甲子')}")
    print(f"丙寅: {get_nayin('丙寅')}")
    
    # 测试地支关系
    print("\n【地支关系测试】")
    print(f"子丑合: {check_liuhe('子', '丑')}")
    print(f"子午冲: {check_liuchong('子', '午')}")
    print(f"子未害: {check_liuhai('子', '未')}")
    print(f"寅巳刑: {check_sanxing('寅', '巳')}")
    print(f"申子辰三合: {check_sanhe(['申', '子', '辰'])}")
    print(f"寅卯辰三会: {check_sanhui(['寅', '卯', '辰'])}")
    
    # 测试五行分数计算
    print("\n【五行分数计算测试】")
    test_sizhu = {
        'year_gan': '甲', 'year_zhi': '子',
        'month_gan': '丙', 'month_zhi': '寅',
        'day_gan': '戊', 'day_zhi': '辰',
        'hour_gan': '庚', 'hour_zhi': '午'
    }
    scores = calculate_wuxing_score(test_sizhu)
    print(f"五行分数: {scores}")
