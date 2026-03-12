# -*- coding: utf-8 -*-
"""公式计算四柱模块

根据提供的快速推算方法计算四柱干支
"""

from datetime import date, datetime, timedelta

# 尝试导入精确节气数据模块
try:
    from .精确节气数据 import JieQiCalculator, get_precise_month
    HAS_PRECISE_JIE_QI = True
except ImportError:
    try:
        from 精确节气数据 import JieQiCalculator, get_precise_month
        HAS_PRECISE_JIE_QI = True
    except ImportError:
        HAS_PRECISE_JIE_QI = False


class FormulaSiZhuCalculator:
    """
    公式计算四柱类
    
    使用提供的快速推算方法计算年柱、月柱、日柱、时柱
    """
    
    def __init__(self, use_precise_jie_qi=True):
        """初始化计算器
        
        Args:
            use_precise_jie_qi: 是否使用精确节气数据（需要sxtwl库）
        """
        # 天干（索引0对应甲，1对应乙，以此类推）
        self.tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        # 地支（索引0对应子，1对应丑，以此类推）
        self.di_zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        # 月份对应的地支（以节令为准）
        self.month_zhi = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
        # 时辰对应的地支
        self.hour_zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 初始化精确节气计算器
        self.use_precise_jie_qi = use_precise_jie_qi and HAS_PRECISE_JIE_QI
        if self.use_precise_jie_qi:
            self.jie_qi_calculator = JieQiCalculator()
        else:
            self.jie_qi_calculator = None
            # 节气数据（简化版，当精确数据不可用时使用）
            self.jie_qi = {
                1: (4, '立春'),    # 立春通常在2月4日
                2: (4, '惊蛰'),    # 惊蛰通常在3月5日
                3: (5, '清明'),    # 清明通常在4月5日
                4: (5, '立夏'),    # 立夏通常在5月5日
                5: (6, '芒种'),    # 芒种通常在6月6日
                6: (7, '小暑'),    # 小暑通常在7月7日
                7: (7, '立秋'),    # 立秋通常在8月7日
                8: (8, '白露'),    # 白露通常在9月8日
                9: (8, '寒露'),    # 寒露通常在10月8日
                10: (7, '立冬'),   # 立冬通常在11月7日
                11: (7, '大雪'),   # 大雪通常在12月7日
                12: (6, '小寒')    # 小寒通常在1月6日
            }
    
    def calculate_year_gan_zhi(self, year, month, day):
        """
        计算年柱干支
        
        Args:
            year: 公元年份
            month: 公历月份
            day: 公历日期
            
        Returns:
            str: 年柱干支
        """
        # 年柱以立春为界
        # 立春通常在2月4-5日左右
        if month < 2 or (month == 2 and day < 4):
            # 还没过立春，属于上一年
            year -= 1
        
        if year > 0:
            # 公元后
            # 公式：公元年末位数-3=年干，负数则加10
            last_digit = year % 10
            gan_value = last_digit - 3
            if gan_value < 0:
                gan_value += 10
            # 天干索引：1-10对应0-9
            gan_index = (gan_value - 1) % 10
            
            # 公式：（公元年数-3）÷12，得余数0-11为年支，负数则加12，0视做12
            remainder = (year - 3) % 12
            if remainder == 0:
                zhi_index = 11  # 0视做12，对应di_zhi[11]即亥
            else:
                zhi_index = remainder - 1  # 地支索引：1-12对应0-11
        else:
            # 公元前
            last_digit = abs(year) % 10
            gan_value = last_digit + 8
            if gan_value >= 10:
                gan_value -= 10
            gan_index = gan_value - 1
            
            remainder = (abs(year) - 2) % 12
            if remainder == 0:
                zhi_index = 11
            else:
                zhi_index = remainder - 1
        
        gan = self.tian_gan[gan_index]
        zhi = self.di_zhi[zhi_index]
        return gan + zhi
    
    def calculate_month_gan_zhi(self, year_gan_zhi, year, month, day, hour=12, minute=0):
        """
        计算月柱干支
        
        Args:
            year_gan_zhi: 年柱干支
            year: 年份
            month: 公历月份(1-12)
            day: 公历日期
            hour: 小时
            minute: 分钟
            
        Returns:
            str: 月柱干支
        """
        # 确定月份（基于节气）
        if self.use_precise_jie_qi and self.jie_qi_calculator:
            # 使用精确节气数据
            lunar_month = self.jie_qi_calculator.get_month_by_jie_qi(year, month, day, hour, minute)
        else:
            # 使用简化节气数据
            lunar_month = self._get_month_simplified(month, day)
        
        # 调整月份范围
        if lunar_month < 1:
            lunar_month = 12
        elif lunar_month > 12:
            lunar_month = 1
        
        # 获取年干
        year_gan = year_gan_zhi[0]
        # 年干序号（1开始：甲=1, 乙=2, ..., 癸=10）
        year_gan_number = self.tian_gan.index(year_gan) + 1
        
        # 计算月干
        # 公式：年干x2+月数=月干，超过10则减去10的倍数
        month_gan_value = year_gan_number * 2 + lunar_month
        while month_gan_value > 10:
            month_gan_value -= 10
        # 转换为0-9的索引
        month_gan_index = month_gan_value - 1
        if month_gan_index < 0:
            month_gan_index = 9  # 0视做10，对应癸
        month_gan = self.tian_gan[month_gan_index]
        
        # 获取月支（以节令为准）
        month_zhi = self.month_zhi[lunar_month - 1]
        
        return month_gan + month_zhi
    
    def calculate_day_gan_zhi(self, target_date):
        """
        计算日柱干支
        
        Args:
            target_date: datetime.date对象
            
        Returns:
            str: 日柱干支
        """
        # 以2000年元旦戊午日为参考
        base_date = date(2000, 1, 1)
        days_diff = (target_date - base_date).days
        
        if days_diff >= 0:
            # 2000年及以后
            # 公式：(A-5)÷10取余数0-9为日干，(A-5)÷12取余数0-11为日支
            gan_index = (days_diff - 5) % 10
            if gan_index < 0:
                gan_index += 10
            zhi_index = (days_diff - 5) % 12
            if zhi_index < 0:
                zhi_index += 12
        else:
            # 2000年以前
            # 公式：(A+5)÷10，用10减去余数0-9为日干；(A+5)÷12，用12减去余数0-11为日支
            days_diff_abs = abs(days_diff)
            gan_remainder = (days_diff_abs + 5) % 10
            gan_index = (10 - gan_remainder) % 10
            zhi_remainder = (days_diff_abs + 5) % 12
            zhi_index = (12 - zhi_remainder) % 12
        
        gan = self.tian_gan[gan_index]
        zhi = self.di_zhi[zhi_index]
        return gan + zhi
    
    def _get_month_simplified(self, month, day):
        """
        简化的月份计算（当精确节气数据不可用时使用）
        
        Args:
            month: 公历月份
            day: 日期
            
        Returns:
            int: 农历月份
        """
        # 简化的节气日期（近似值）
        # 格式：(节气月份, 节气日期, 对应农历月份)
        jie_qi_info = [
            (1, 6, 12),   # 小寒在1月6日左右，对应农历十二月
            (2, 4, 1),    # 立春在2月4日左右，对应农历正月
            (3, 6, 2),    # 惊蛰在3月6日左右，对应农历二月
            (4, 5, 3),    # 清明在4月5日左右，对应农历三月
            (5, 6, 4),    # 立夏在5月6日左右，对应农历四月
            (6, 6, 5),    # 芒种在6月6日左右，对应农历五月
            (7, 7, 6),    # 小暑在7月7日左右，对应农历六月
            (8, 8, 7),    # 立秋在8月8日左右，对应农历七月
            (9, 8, 8),    # 白露在9月8日左右，对应农历八月
            (10, 8, 9),   # 寒露在10月8日左右，对应农历九月
            (11, 7, 10),  # 立冬在11月7日左右，对应农历十月
            (12, 7, 11)   # 大雪在12月7日左右，对应农历十一月
        ]
        
        # 找到当前月份的节气
        for i, (jq_month, jq_day, lunar_month) in enumerate(jie_qi_info):
            if jq_month == month:
                if day >= jq_day:
                    return lunar_month
                else:
                    # 未到节气，返回前一个月
                    if i == 0:
                        return 11  # 小寒前是农历十一月
                    else:
                        prev_jq_month, prev_jq_day, prev_lunar_month = jie_qi_info[i-1]
                        return prev_lunar_month
        
        return month
    
    def calculate_hour_gan_zhi(self, day_gan_zhi, hour):
        """
        计算时柱干支
        
        Args:
            day_gan_zhi: 日柱干支
            hour: 小时(0-23)
            
        Returns:
            str: 时柱干支
        """
        # 获取日干
        day_gan = day_gan_zhi[0]
        # 天干索引从1开始：甲=1, 乙=2, 丙=3, 丁=4, 戊=5, 己=6, 庚=7, 辛=8, 壬=9, 癸=10
        day_gan_number = self.tian_gan.index(day_gan) + 1
        
        # 计算时支
        # 子时: 23-1 → 1
        # 丑时: 1-3 → 2
        # 寅时: 3-5 → 3
        # 卯时: 5-7 → 4
        # 辰时: 7-9 → 5
        # 巳时: 9-11 → 6
        # 午时: 11-13 → 7
        # 未时: 13-15 → 8
        # 申时: 15-17 → 9
        # 酉时: 17-19 → 10
        # 戌时: 19-21 → 11
        # 亥时: 21-23 → 12
        if hour < 1:
            hour_zhi_number = 1  # 子时
        elif hour < 3:
            hour_zhi_number = 2  # 丑时
        elif hour < 5:
            hour_zhi_number = 3  # 寅时
        elif hour < 7:
            hour_zhi_number = 4  # 卯时
        elif hour < 9:
            hour_zhi_number = 5  # 辰时
        elif hour < 11:
            hour_zhi_number = 6  # 巳时
        elif hour < 13:
            hour_zhi_number = 7  # 午时
        elif hour < 15:
            hour_zhi_number = 8  # 未时
        elif hour < 17:
            hour_zhi_number = 9  # 申时
        elif hour < 19:
            hour_zhi_number = 10  # 酉时
        elif hour < 21:
            hour_zhi_number = 11  # 戌时
        else:
            hour_zhi_number = 12  # 亥时
        
        # 时支
        hour_zhi_index = hour_zhi_number - 1  # 转换为0-11的索引
        hour_zhi = self.hour_zhi[hour_zhi_index]
        
        # 计算时干
        # 公式：日干x2+时支数-2=时干数
        hour_gan_value = day_gan_number * 2 + hour_zhi_number - 2
        # 时干数：1-10对应0-9的索引
        hour_gan_index = (hour_gan_value - 1) % 10
        if hour_gan_index < 0:
            hour_gan_index += 10
        hour_gan = self.tian_gan[hour_gan_index]
        
        return hour_gan + hour_zhi
    
    def calculate_si_zhu(self, target_date, hour=12, minute=0):
        """
        计算四柱
        
        Args:
            target_date: datetime.date或datetime对象
            hour: 小时(0-23)
            minute: 分钟(0-59)
            
        Returns:
            dict: 四柱信息
        """
        if isinstance(target_date, datetime):
            hour = target_date.hour
            minute = target_date.minute
            target_date = target_date.date()
        
        # 计算年柱
        year_gan_zhi = self.calculate_year_gan_zhi(target_date.year, target_date.month, target_date.day)
        
        # 计算月柱
        month_gan_zhi = self.calculate_month_gan_zhi(year_gan_zhi, target_date.year, target_date.month, target_date.day, hour, minute)
        
        # 计算日柱
        day_gan_zhi = self.calculate_day_gan_zhi(target_date)
        
        # 计算时柱
        hour_gan_zhi = self.calculate_hour_gan_zhi(day_gan_zhi, hour)
        
        return {
            '年柱': year_gan_zhi,
            '月柱': month_gan_zhi,
            '日柱': day_gan_zhi,
            '时柱': hour_gan_zhi
        }


# 便捷函数
def calculate_si_zhu(target_date, hour=12, minute=0):
    """
    计算四柱的便捷函数
    
    Args:
        target_date: datetime.date或datetime对象
        hour: 小时(0-23)
        minute: 分钟(0-59)
        
    Returns:
        dict: 四柱信息
    """
    calculator = FormulaSiZhuCalculator()
    return calculator.calculate_si_zhu(target_date, hour, minute)


def calculate_year_gan_zhi(year, month, day):
    """
    计算年柱的便捷函数
    
    Args:
        year: 公元年份
        month: 公历月份
        day: 公历日期
        
    Returns:
        str: 年柱干支
    """
    calculator = FormulaSiZhuCalculator()
    return calculator.calculate_year_gan_zhi(year, month, day)


def calculate_month_gan_zhi(year_gan_zhi, month, day, hour=12, minute=0):
    """
    计算月柱的便捷函数
    
    Args:
        year_gan_zhi: 年柱干支
        month: 公历月份(1-12)
        day: 公历日期
        hour: 小时
        minute: 分钟
        
    Returns:
        str: 月柱干支
    """
    calculator = FormulaSiZhuCalculator()
    return calculator.calculate_month_gan_zhi(year_gan_zhi, month, day, hour, minute)


def calculate_day_gan_zhi(target_date):
    """
    计算日柱的便捷函数
    
    Args:
        target_date: datetime.date对象
        
    Returns:
        str: 日柱干支
    """
    calculator = FormulaSiZhuCalculator()
    return calculator.calculate_day_gan_zhi(target_date)


def calculate_hour_gan_zhi(day_gan_zhi, hour):
    """
    计算时柱的便捷函数
    
    Args:
        day_gan_zhi: 日柱干支
        hour: 小时(0-23)
        
    Returns:
        str: 时柱干支
    """
    calculator = FormulaSiZhuCalculator()
    return calculator.calculate_hour_gan_zhi(day_gan_zhi, hour)