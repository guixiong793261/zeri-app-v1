"""择日核心模块

提供择日算法的核心功能
"""

from datetime import date, timedelta
from 核心模块.评分器 import ScoreCalculator


class SelectDayCore:
    """
    择日核心类
    
    提供日期选择和吉日筛选功能
    """
    
    def __init__(self):
        """初始化择日核心"""
        self.score_calculator = ScoreCalculator()
    
    def select_days(self, start_date, end_date, event_type='婚嫁'):
        """
        选择指定日期范围内的吉日
        
        Args:
            start_date: 开始日期 (datetime.date)
            end_date: 结束日期 (datetime.date)
            event_type: 事件类型 (婚嫁、入宅、开业等)
            
        Returns:
            list: 吉日列表
        """
        吉日 = []
        current_date = start_date
        
        while current_date <= end_date:
            # 计算该日期的评分
            score_result = self.score_calculator.calculate_score(current_date, 12, 0, event_type)
            
            # 只选择评分较高的日期
            if score_result['score'] >= 70:
                吉日.append({
                    'date': current_date,
                    'score': score_result['score'],
                    'level': score_result['level'],
                    'reason': score_result['reason']
                })
            
            current_date += timedelta(days=1)
        
        # 按评分排序
        吉日.sort(key=lambda x: x['score'], reverse=True)
        
        return 吉日
    
    def get_best_day(self, start_date, end_date, event_type='婚嫁'):
        """
        获取最佳吉日
        
        Args:
            start_date: 开始日期 (datetime.date)
            end_date: 结束日期 (datetime.date)
            event_type: 事件类型
            
        Returns:
            dict: 最佳吉日信息
        """
        吉日列表 = self.select_days(start_date, end_date, event_type)
        return 吉日列表[0] if 吉日列表 else None