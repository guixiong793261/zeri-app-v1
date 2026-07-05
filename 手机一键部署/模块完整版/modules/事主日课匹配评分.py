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
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# 导入事主八字分析模块
try:
    from .事主八字分析 import ShiZhuBaZiAnalyzer, analyze_shizhu_bazi
except ImportError:
    from 事主八字分析 import ShiZhuBaZiAnalyzer, analyze_shizhu_bazi


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
        try:
            analyzer = self.get_or_create_analyzer(shizhu_info)
            return analyzer.calculate_rike_match_score(rike_sizhu)
        except Exception as e:
            logger.error(f"计算匹配评分失败: {e}")
            return {
                'score': 50,
                'level': '中平',
                'error': str(e),
                'summary': '评分计算出错，默认中平'
            }
    
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


if __name__ == '__main__':
    # 测试代码
    print("=" * 80)
    print("事主日课匹配评分模块测试")
    print("=" * 80)
    
    # 测试事主信息
    shizhu_list = [
        {
            'name': '新郎',
            'year': 1984,
            'month': 2,
            'day': 15,
            'hour': 10,
            'minute': 0,
            'gender': '男'
        },
        {
            'name': '新娘',
            'year': 1986,
            'month': 5,
            'day': 20,
            'hour': 14,
            'minute': 30,
            'gender': '女'
        }
    ]
    
    # 测试日课
    test_rike = {
        'year': '甲辰', 'month': '己巳', 'day': '甲申', 'hour': '庚午',
        'year_gan': '甲', 'year_zhi': '辰',
        'month_gan': '己', 'month_zhi': '巳',
        'day_gan': '甲', 'day_zhi': '申',
        'hour_gan': '庚', 'hour_zhi': '午'
    }
    
    print("\n【测试事主信息】")
    for shizhu in shizhu_list:
        print(f"{shizhu['name']}：{shizhu['year']}年{shizhu['month']}月{shizhu['day']}日 {shizhu['hour']:02d}:{shizhu['minute']:02d}")
    
    print(f"\n【测试日课】")
    print(f"日课四柱：{test_rike['year']} {test_rike['month']} {test_rike['day']} {test_rike['hour']}")
    
    # 测试单个匹配
    print("\n" + "=" * 80)
    print("单个事主匹配测试")
    print("=" * 80)
    
    for shizhu in shizhu_list:
        result = calculate_shizhu_rike_match(shizhu, test_rike)
        print(f"\n{shizhu['name']}：")
        print(f"  匹配分数：{result['score']}分")
        print(f"  匹配等级：{result['level']}")
        print(f"  用神：{'、'.join(result.get('事主用神', []))}")
        print(f"  总结：{result['summary']}")
    
    # 测试综合匹配
    print("\n" + "=" * 80)
    print("综合匹配测试")
    print("=" * 80)
    
    multi_result = calculate_multi_match(shizhu_list, test_rike)
    print(f"\n综合评分：{multi_result['score']}分")
    print(f"综合等级：{multi_result['level']}")
    print(f"总结：{multi_result['summary']}")
    
    print(f"\n【各事主评分详情】")
    for detail in multi_result['details']:
        print(f"  {detail['name']}：{detail['score']}分（{detail['level']}）")
    
    # 测试整合功能
    print("\n" + "=" * 80)
    print("评分整合测试")
    print("=" * 80)
    
    integration = RiKeShiZhuIntegration()
    
    # 模拟基础评分结果
    base_result = {
        'score': 85,
        'level': '吉',
        'reason': '五行平衡，黄道吉日',
        '评分维度': [
            {'维度': '五行平衡', '权重': '30%', '得分': 90, '贡献': 27},
            {'维度': '黄道吉凶', '权重': '20%', '得分': 80, '贡献': 16}
        ]
    }
    
    enhanced = integration.enhance_score_result(base_result, shizhu_list, test_rike)
    
    print(f"\n原始评分：{base_result['score']}分")
    print(f"增强后评分：{enhanced['score']}分")
    print(f"\n评分维度：")
    for dim in enhanced['评分维度']:
        print(f"  {dim['维度']}：{dim['得分']}分 × {dim['权重']} = {dim['贡献']}分")
    
    # 获取建议
    print(f"\n【择日建议】")
    suggestions = integration.get_shizhu_suggestions(shizhu_list)
    for suggestion in suggestions:
        print(f"  - {suggestion}")
    
    print("\n" + "=" * 80)
