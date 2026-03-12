"""评分器模块

提供择日评分功能
"""

from datetime import date, datetime
from 核心模块.日期转换 import calculate_gan_zhi, get_jie_qi


class ScoreCalculator:
    """
    评分计算器类
    
    提供日期评分功能
    """
    
    def __init__(self):
        """初始化评分计算器"""
        pass
    
    def calculate_score(self, target_date, hour=12, minute=0, event_type='婚嫁'):
        """
        计算日期评分
        
        Args:
            target_date: 目标日期 (datetime.date)
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
            event_type: 事件类型
            
        Returns:
            dict: 评分结果
        """
        score = 0
        reasons = []
        
        # 1. 计算干支信息
        gan_zhi = calculate_gan_zhi(target_date, hour, minute)
        
        # 2. 检查节气
        jie_qi_info = get_jie_qi(target_date.year, target_date.month, target_date.day, hour, minute)
        
        # 3. 基本评分
        score += 60  # 基础分
        
        # 4. 事件类型加分
        event_bonus = {
            '婚嫁': 10,
            '入宅': 8,
            '开业': 12,
            '动土': 6,
            '出行': 5
        }
        score += event_bonus.get(event_type, 5)
        
        # 5. 日期加分（示例规则）
        if target_date.day in [1, 6, 8, 9, 16, 18, 28]:
            score += 5
            reasons.append("日期数字吉利")
        
        # 6. 星期加分
        if target_date.weekday() in [5, 6]:  # 周末
            score += 3
            reasons.append("周末吉日")
        
        # 7. 干支加分（示例规则）
        if '辰' in gan_zhi['日干支'] or '午' in gan_zhi['日干支']:
            score += 2
            reasons.append("日干支吉利")
        
        # 8. 限制最高分
        score = min(score, 100)
        
        # 9. 计算等级
        if score >= 90:
            level = '★★★★★'
        elif score >= 80:
            level = '★★★★'
        elif score >= 70:
            level = '★★★'
        elif score >= 60:
            level = '★★'
        else:
            level = '★'
        
        return {
            'score': score,
            'level': level,
            'reason': '; '.join(reasons),
            'gan_zhi': gan_zhi,
            'jie_qi': jie_qi_info
        }
    
    def calculate_wu_xing_score(self, gan_zhi):
        """
        计算五行评分
        
        Args:
            gan_zhi: 干支信息
            
        Returns:
            int: 五行评分
        """
        # 简化的五行评分逻辑
        score = 50
        
        # 示例：根据日干支计算五行得分
        ri_gan = gan_zhi['日干支'][0]  # 日干
        
        # 五行相生相克加分减分
        wu_xing_bonus = {
            '甲': 5,
            '乙': 4,
            '丙': 6,
            '丁': 5,
            '戊': 4,
            '己': 3,
            '庚': 6,
            '辛': 5,
            '壬': 4,
            '癸': 3
        }
        
        score += wu_xing_bonus.get(ri_gan, 0)
        return min(score, 100)