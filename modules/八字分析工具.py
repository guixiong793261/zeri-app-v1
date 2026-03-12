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
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# 从工具函数导入基础数据
try:
    from .工具函数 import TIAN_GAN, DI_ZHI, TIAN_GAN_WUXING, DI_ZHI_WUXING
except ImportError:
    from 工具函数 import TIAN_GAN, DI_ZHI, TIAN_GAN_WUXING, DI_ZHI_WUXING

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


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("八字分析工具测试")
    print("=" * 60)
    
    # 测试十神
    print("\n【十神测试】")
    day_gan = '甲'
    test_gans = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    for gan in test_gans:
        shishen = get_shishen(day_gan, gan)
        explanation = get_shishen_explanation(shishen)
        print(f"日干{day_gan} 见 {gan}: {shishen} - {explanation}")
    
    # 测试地支关系
    print("\n【地支关系测试】")
    print(f"子丑合: {check_he('子', '丑')}")
    print(f"子午冲: {check_chong('子', '午')}")
    print(f"子卯刑: {check_xing('子', '卯')}")
    print(f"子未害: {check_hai('子', '未')}")
    print(f"申子辰三合: {check_sanhe(['申', '子', '辰'])}")
    
    # 测试十二长生
    print("\n【十二长生测试】")
    day_gan = '甲'
    for zhi in DI_ZHI:
        zhangsheng = get_zhangsheng(day_gan, zhi)
        print(f"甲见{zhi}: {zhangsheng}")
    
    # 测试纳音
    print("\n【纳音测试】")
    test_pillars = ['甲子', '丙寅', '戊辰', '庚午', '壬申']
    for pillar in test_pillars:
        print(f"{pillar}: {get_nayin(pillar)}")
