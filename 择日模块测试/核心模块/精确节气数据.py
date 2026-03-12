# -*- coding: utf-8 -*-
"""
精确节气数据模块

提供基于 sxtwl 库的精确节气点计算功能
用于替代简化版的节气数据，提高月柱计算准确性
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 尝试导入 sxtwl 库
try:
    import sxtwl
    HAS_SXTWL = True
except ImportError:
    HAS_SXTWL = False
    print("警告: sxtwl 库未安装，将使用简化节气数据")


class JieQiCalculator:
    """
    精确节气计算器
    
    使用 sxtwl 库计算精确的节气时间点
    """
    
    # 节气名称列表
    JIE_QI_NAMES = [
        '小寒', '大寒', '立春', '雨水', '惊蛰', '春分',
        '清明', '谷雨', '立夏', '小满', '芒种', '夏至',
        '小暑', '大暑', '立秋', '处暑', '白露', '秋分',
        '寒露', '霜降', '立冬', '小雪', '大雪', '冬至'
    ]
    
    def __init__(self):
        """初始化计算器"""
        self.has_sxtwl = HAS_SXTWL
        # 缓存节气数据，避免重复计算
        self._cache = {}
    
    def get_year_jie_qi(self, year):
        """
        获取指定年份的所有节气时间点
        
        Args:
            year: 年份
            
        Returns:
            list: 节气列表，每个元素包含名称和时间
        """
        if not self.has_sxtwl:
            return None
        
        # 检查缓存
        if year in self._cache:
            return self._cache[year]
        
        # 获取节气列表
        jq_list = sxtwl.getJieQiByYear(year)
        
        result = []
        for i, jq in enumerate(jq_list):
            # 确保索引不超出范围
            if i >= len(self.JIE_QI_NAMES):
                break
                
            jd = jq.jd
            dd = sxtwl.JD2DD(jd)
            jq_datetime = datetime(
                int(dd.Y), int(dd.M), int(dd.D),
                int(dd.h), int(dd.m), int(dd.s)
            )
            
            result.append({
                '名称': self.JIE_QI_NAMES[i],
                '时间': jq_datetime,
                '索引': i
            })
        
        # 存入缓存
        self._cache[year] = result
        
        return result
    
    def get_jie_qi_by_date(self, year, month, day, hour=0, minute=0):
        """
        获取指定日期前后的节气信息
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            hour: 小时
            minute: 分钟
            
        Returns:
            dict: 包含当前节气和下一节气的信息
        """
        if not self.has_sxtwl:
            return None
        
        # 获取当年所有节气
        year_jie_qi = self.get_year_jie_qi(year)
        if not year_jie_qi:
            return None
        
        # 当前时间
        current_dt = datetime(year, month, day, hour, minute, 0)
        
        # 查找当前节气
        current_jq = None
        next_jq = None
        
        for i, jq in enumerate(year_jie_qi):
            if jq['时间'] <= current_dt:
                current_jq = jq
            else:
                next_jq = jq
                break
        
        return {
            '当前节气': current_jq,
            '下一节气': next_jq
        }
    
    def get_month_by_jie_qi(self, year, month, day, hour=0, minute=0):
        """
        根据节气确定农历月份
        
        用于月柱计算，确保月份以节气为界
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            hour: 小时
            minute: 分钟
            
        Returns:
            int: 农历月份（1-12）
        """
        if not self.has_sxtwl:
            # 使用简化逻辑
            return self._get_month_simplified(year, month, day)
        
        # 获取节气信息
        jie_qi_info = self.get_jie_qi_by_date(year, month, day, hour, minute)
        if not jie_qi_info or not jie_qi_info['当前节气']:
            return month
        
        current_jq = jie_qi_info['当前节气']
        jq_name = current_jq['名称']
        jq_index = current_jq['索引']
        
        # 根据节气索引确定月份
        # 节气索引与月份的对应关系：
        # 立春(2) = 正月, 惊蛰(4) = 二月, 清明(6) = 三月, ...
        # 小寒(0) = 十二月, 大寒(1) = 十二月
        
        if jq_index == 0 or jq_index == 1:  # 小寒、大寒
            return 12  # 农历十二月
        elif jq_index == 2:  # 立春
            return 1   # 农历正月
        elif jq_index == 4:  # 惊蛰
            return 2   # 农历二月
        elif jq_index == 6:  # 清明
            return 3   # 农历三月
        elif jq_index == 8:  # 立夏
            return 4   # 农历四月
        elif jq_index == 10:  # 芒种
            return 5   # 农历五月
        elif jq_index == 12:  # 小暑
            return 6   # 农历六月
        elif jq_index == 14:  # 立秋
            return 7   # 农历七月
        elif jq_index == 16:  # 白露
            return 8   # 农历八月
        elif jq_index == 18:  # 寒露
            return 9   # 农历九月
        elif jq_index == 20:  # 立冬
            return 10  # 农历十月
        elif jq_index == 22:  # 大雪
            return 11  # 农历十一月
        else:
            # 对于中气（雨水、春分、谷雨、小满、夏至、大暑、处暑、秋分、霜降、小雪、冬至）
            # 使用前一个节气的月份
            return self._get_month_from_zhong_qi(jq_index)
    
    def _get_month_from_zhong_qi(self, jq_index):
        """
        根据中气索引确定月份
        
        中气位于两个节气之间，使用前一个节气的月份
        """
        # 中气索引：3(雨水), 5(春分), 7(谷雨), 9(小满), 11(夏至), 13(大暑)
        #           15(处暑), 17(秋分), 19(霜降), 21(小雪), 23(冬至)
        
        if jq_index == 3:   # 雨水
            return 1   # 正月
        elif jq_index == 5:  # 春分
            return 2   # 二月
        elif jq_index == 7:  # 谷雨
            return 3   # 三月
        elif jq_index == 9:  # 小满
            return 4   # 四月
        elif jq_index == 11:  # 夏至
            return 5   # 五月
        elif jq_index == 13:  # 大暑
            return 6   # 六月
        elif jq_index == 15:  # 处暑
            return 7   # 七月
        elif jq_index == 17:  # 秋分
            return 8   # 八月
        elif jq_index == 19:  # 霜降
            return 9   # 九月
        elif jq_index == 21:  # 小雪
            return 10  # 十月
        elif jq_index == 23:  # 冬至
            return 11  # 十一月
        else:
            return 1
    
    def _get_month_simplified(self, year, month, day):
        """
        简化的月份计算（当 sxtwl 不可用时使用）
        """
        # 简化的节气日期（近似值）
        jie_qi_dates = {
            1: 6,   # 小寒在1月6日左右
            2: 4,   # 立春在2月4日左右
            3: 6,   # 惊蛰在3月6日左右
            4: 5,   # 清明在4月5日左右
            5: 6,   # 立夏在5月6日左右
            6: 6,   # 芒种在6月6日左右
            7: 7,   # 小暑在7月7日左右
            8: 8,   # 立秋在8月8日左右
            9: 8,   # 白露在9月8日左右
            10: 8,  # 寒露在10月8日左右
            11: 7,  # 立冬在11月7日左右
            12: 7   # 大雪在12月7日左右
        }
        
        if month in jie_qi_dates:
            if day >= jie_qi_dates[month]:
                return month
            else:
                return month - 1 if month > 1 else 12
        
        return month


# 便捷函数
def get_jie_qi_calculator():
    """
    获取节气计算器实例
    
    Returns:
        JieQiCalculator: 节气计算器实例
    """
    return JieQiCalculator()


def get_precise_month(year, month, day, hour=0, minute=0):
    """
    获取精确的农历月份（基于节气）
    
    Args:
        year: 年份
        month: 月份
        day: 日期
        hour: 小时
        minute: 分钟
        
    Returns:
        int: 农历月份
    """
    calculator = JieQiCalculator()
    return calculator.get_month_by_jie_qi(year, month, day, hour, minute)


if __name__ == '__main__':
    # 测试代码
    calculator = JieQiCalculator()
    
    # 测试2023年的节气
    print("=== 2023年节气数据 ===")
    jie_qi_list = calculator.get_year_jie_qi(2023)
    if jie_qi_list:
        for jq in jie_qi_list:
            print(f"{jq['名称']}: {jq['时间']}")
    
    # 测试特定日期的月份计算
    print("\n=== 特定日期月份计算 ===")
    test_dates = [
        (2023, 2, 3, 12, 0),   # 立春前
        (2023, 2, 4, 12, 0),   # 立春后
        (2023, 3, 5, 12, 0),   # 惊蛰前
        (2023, 3, 6, 12, 0),   # 惊蛰后
    ]
    
    for year, month, day, hour, minute in test_dates:
        lunar_month = calculator.get_month_by_jie_qi(year, month, day, hour, minute)
        jie_qi_info = calculator.get_jie_qi_by_date(year, month, day, hour, minute)
        current_jq = jie_qi_info['当前节气']['名称'] if jie_qi_info and jie_qi_info['当前节气'] else '未知'
        print(f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} -> 农历{lunar_month}月 (当前节气: {current_jq})")
