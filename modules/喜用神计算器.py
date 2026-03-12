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
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)

# 从八字分析工具导入基础数据和函数
try:
    from .八字分析工具 import (
        GAN_WUXING, ZHI_WUXING,
        ZHIGAN_MAP,
        calculate_wuxing_score
    )
except ImportError:
    from 八字分析工具 import (
        GAN_WUXING, ZHI_WUXING,
        ZHIGAN_MAP,
        calculate_wuxing_score
    )


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
    try:
        return calculate_wuxing_score(sizhu, include_canggan=True)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"使用加权算法失败，回退到简化算法: {e}")
        
        # 回退到简化算法（仅统计次数）
        wuxing_counts = {
            '金': 0,
            '木': 0,
            '水': 0,
            '火': 0,
            '土': 0
        }
        
        # 统计天干五行
        for gan_key in ['year_gan', 'month_gan', 'day_gan', 'hour_gan']:
            gan = sizhu.get(gan_key, '')
            if gan:
                wx = GAN_WUXING.get(gan, '')
                if wx:
                    wuxing_counts[wx] += 1
        
        # 统计地支五行
        for zhi_key in ['year_zhi', 'month_zhi', 'day_zhi', 'hour_zhi']:
            zhi = sizhu.get(zhi_key, '')
            if zhi:
                wx = ZHI_WUXING.get(zhi, '')
                if wx:
                    wuxing_counts[wx] += 1
        
        return wuxing_counts


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
        return "水、木", "水"
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
