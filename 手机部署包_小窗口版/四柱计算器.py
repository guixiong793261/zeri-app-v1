# -*- coding: utf-8 -*-
"""
================================================================================
四柱计算模块
================================================================================
提供年柱、月柱、日柱、时柱的完整计算功能

使用方法:
    1. 作为模块导入: from modules.四柱计算器 import calculate_sizhu
    2. 直接运行: python -m modules.四柱计算器

【重要说明】
本模块使用精确的农历计算方法，基于 sxtwl 库的天文算法
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

from datetime import date, datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 从工具函数导入基础数据
try:
    from .工具函数 import (
        TIAN_GAN, DI_ZHI, WU_HU_DUN, WU_SHU_DUN,
        get_gan_wuxing, get_zhi_wuxing, get_hour_zhi_index,
        get_shishen, get_fuzi, format_date
    )
except ImportError:
    from 工具函数 import (
        TIAN_GAN, DI_ZHI, WU_HU_DUN, WU_SHU_DUN,
        get_gan_wuxing, get_zhi_wuxing, get_hour_zhi_index,
        get_shishen, get_fuzi, format_date
    )

# 尝试导入 sxtwl 库
try:
    import sxtwl
    HAS_SXTWL = True
    logger.info("成功导入 sxtwl 库，使用精确的四柱计算方法")
except ImportError:
    HAS_SXTWL = False
    logger.warning("sxtwl 库未安装，使用备用计算方法")


class SiZhuCalculator:
    """
    四柱计算器类
    
    提供年柱、月柱、日柱、时柱的完整计算功能
    使用 sxtwl 库进行精确计算
    """
    
    def __init__(self, strict_mode=True, sect=2):
        """
        初始化计算器
        
        Args:
            strict_mode: 是否使用严格模式（默认True）
            sect: 流派选择（1或2，默认2）
        """
        self.strict_mode = strict_mode
        self.sect = sect
        logger.info(f"使用精确四柱计算方法 (sect={sect})")
    
    def calculate(self, target_date, hour=12, minute=0, second=0):
        """
        计算完整四柱
        
        Args:
            target_date: datetime.date对象
            hour: 小时(0-23)
            minute: 分钟(0-59)
            second: 秒(0-59)
            
        Returns:
            dict: 包含年柱、月柱、日柱、时柱的字典
        """
        year = target_date.year
        month = target_date.month
        day = target_date.day
        
        # 使用 sxtwl 计算四柱
        if HAS_SXTWL:
            try:
                return self._calculate_with_sxtwl(year, month, day, hour, minute, second)
            except Exception as e:
                logger.warning(f"sxtwl 计算失败，使用备用方法: {e}")
        
        # 备用计算方法
        return self._calculate_fallback(year, month, day, hour, minute, second)
    
    def _calculate_with_sxtwl(self, year, month, day, hour, minute, second):
        """
        使用 sxtwl 库计算四柱
        
        sxtwl 使用天文算法，基于精确的节气时刻计算
        这是最权威的计算方法，完全依赖 sxtwl 的天文算法
        """
        # 使用 sxtwl 计算四柱
        day_obj = sxtwl.fromSolar(year, month, day)
        
        # 获取年柱、日柱、时柱（完全使用 sxtwl 的权威计算）
        year_gz = day_obj.getYearGZ()
        day_gz = day_obj.getDayGZ()
        hour_gz = day_obj.getHourGZ(hour)
        
        # 转换为天干地支
        tg = TIAN_GAN
        dz = DI_ZHI
        
        year_gan = tg[year_gz.tg]
        year_zhi = dz[year_gz.dz]
        day_gan = tg[day_gz.tg]
        day_zhi = dz[day_gz.dz]
        hour_gan = tg[hour_gz.tg]
        hour_zhi = dz[hour_gz.dz]
        
        # 计算月柱（使用精确节气时间）
        month_gan, month_zhi = self._calculate_month_pillar_precise(year, month, day, hour, minute, year_gan)
        
        # 标记是否为晚子时
        is_late_zi = (hour == 23)
        
        return {
            '年柱': year_gan + year_zhi,
            '月柱': month_gan + month_zhi,
            '日柱': day_gan + day_zhi,
            '时柱': hour_gan + hour_zhi,
            'year_gan': year_gan,
            'year_zhi': year_zhi,
            'month_gan': month_gan,
            'month_zhi': month_zhi,
            'day_gan': day_gan,
            'day_zhi': day_zhi,
            'hour_gan': hour_gan,
            'hour_zhi': hour_zhi,
            'is_late_zi': is_late_zi
        }
    
    def _calculate_month_pillar_precise(self, year, month, day, hour, minute, year_gan):
        """
        使用精确节气时间计算月柱
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            hour: 小时
            minute: 分钟
            year_gan: 年干
        
        Returns:
            tuple: (月干, 月支)
        """
        # 将儒略日转换为datetime
        def jd_to_datetime(jd):
            dd = sxtwl.JD2DD(jd)
            return datetime(int(dd.Y), int(dd.M), int(dd.D), int(dd.h), int(dd.m), int(dd.s))
        
        # 当前时间
        current_dt = datetime(year, month, day, hour, minute, 0)
        
        # 获取当年节气列表
        # 注意：sxtwl.getJieQiByYear(year) 返回的节气列表中：
        # - 索引0-21是当年的节气（立春到大雪）
        # - 索引22-23是下一公历年的小寒和大寒
        jq_list = sxtwl.getJieQiByYear(year)
        
        # 节气名称（sxtwl的索引顺序）
        # 0=立春, 1=雨水, 2=惊蛰, 3=春分, 4=清明, 5=谷雨,
        # 6=立夏, 7=小满, 8=芒种, 9=夏至, 10=小暑, 11=大暑,
        # 12=立秋, 13=处暑, 14=白露, 15=秋分, 16=寒露, 17=霜降,
        # 18=立冬, 19=小雪, 20=大雪, 21=冬至, 22=小寒, 23=大寒
        
        # 月支与"节"的对应关系
        # 立春(0)->寅月, 惊蛰(2)->卯月, 清明(4)->辰月, 立夏(6)->巳月,
        # 芒种(8)->午月, 小暑(10)->未月, 立秋(12)->申月, 白露(14)->酉月,
        # 寒露(16)->戌月, 立冬(18)->亥月, 大雪(20)->子月, 小寒(22)->丑月
        
        jie_to_month = {
            0: '寅',   # 立春
            2: '卯',   # 惊蛰
            4: '辰',   # 清明
            6: '巳',   # 立夏
            8: '午',   # 芒种
            10: '未',  # 小暑
            12: '申',  # 立秋
            14: '酉',  # 白露
            16: '戌',  # 寒露
            18: '亥',  # 立冬
            20: '子',  # 大雪
            22: '丑',  # 小寒
        }
        
        # 构建节气时间列表（只包含"节"）
        jie_times = []
        
        # 添加当年的"节"
        for jie_idx in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
            jd = jq_list[jie_idx].jd
            dt = jd_to_datetime(jd)
            jie_times.append((dt, jie_idx))
        
        # 如果当前时间在立春之前，需要添加前一年的小寒
        lichun_dt = jd_to_datetime(jq_list[0].jd)
        if current_dt < lichun_dt:
            # 获取前一年的节气列表
            jq_list_prev = sxtwl.getJieQiByYear(year - 1)
            # 前一年的小寒（索引22）
            jd = jq_list_prev[22].jd
            dt = jd_to_datetime(jd)
            jie_times.append((dt, 22))
        
        # 排序
        jie_times.sort(key=lambda x: x[0])
        
        # 找到当前时间所在的月份
        month_zhi = '寅'  # 默认
        
        for i, (dt, jie_idx) in enumerate(jie_times):
            if current_dt < dt:
                # 当前时间在这个节气之前
                if i == 0:
                    # 在第一个节气之前，使用子月（大雪到小寒之间）
                    month_zhi = '子'
                else:
                    # 使用上一个节气对应的月份
                    prev_jie_idx = jie_times[i-1][1]
                    month_zhi = jie_to_month.get(prev_jie_idx, '寅')
                break
        else:
            # 在所有节气之后，使用最后一个节气对应的月份
            last_jie_idx = jie_times[-1][1]
            month_zhi = jie_to_month.get(last_jie_idx, '丑')
        
        # 使用五虎遁计算月干
        base_gan_index = WU_HU_DUN.get(year_gan, 0)
        month_zhi_index = DI_ZHI.index(month_zhi)
        offset = (month_zhi_index - 2 + 12) % 12  # 寅=2
        month_gan_index = (base_gan_index + offset) % 10
        month_gan = TIAN_GAN[month_gan_index]
        
        return month_gan, month_zhi
    
    def _calculate_fallback(self, year, month, day, hour, minute, second):
        """
        备用计算方法
        
        当 sxtwl 不可用时使用传统算法
        
        特别处理晚子时（23:00-00:00）：
        传统八字中，晚子时的时柱需用次日的日干起时，但日柱仍用当天的日柱。
        """
        from datetime import datetime, timedelta
        
        # 处理晚子时：23:00-00:00
        is_late_zi = (hour == 23)
        
        # 计算年柱（使用原始日期判断节气）
        year_gan, year_zhi = self._calculate_year(year, month, day, hour, minute)
        
        # 计算月柱（使用原始日期判断节气）
        month_gan, month_zhi = self._calculate_month(year, month, day, hour, minute, year_gan)
        
        # 计算日柱（使用当天的日期）
        day_gan, day_zhi = self._calculate_day(year, month, day)
        
        # 计算时柱
        # 注意：根据用户提供的案例，晚子时也使用当天的日干计算时干
        # 这与传统八字的晚子时处理不同，但为了匹配用户期望，我们遵循用户的计算方式
        hour_gan, hour_zhi = self._calculate_hour(day_gan, hour, minute, year, month, day)
        
        return {
            '年柱': year_gan + year_zhi,
            '月柱': month_gan + month_zhi,
            '日柱': day_gan + day_zhi,
            '时柱': hour_gan + hour_zhi,
            'year_gan': year_gan,
            'year_zhi': year_zhi,
            'month_gan': month_gan,
            'month_zhi': month_zhi,
            'day_gan': day_gan,
            'day_zhi': day_zhi,
            'hour_gan': hour_gan,
            'hour_zhi': hour_zhi,
            'is_late_zi': is_late_zi  # 标记是否为晚子时
        }
    
    def _calculate_year(self, year, month, day, hour, minute):
        """
        计算年柱
        
        年柱以立春为界，立春前属于上一年
        """
        # 简化的立春判断（实际应该使用天文算法）
        # 立春通常在2月3日、4日或5日
        if month < 2 or (month == 2 and day < 4):
            # 立春前，属于上一年
            year -= 1
        
        # 计算年干支
        # 以1984年（甲子年）为基准
        offset = (year - 1984) % 60
        gan_index = offset % 10
        zhi_index = offset % 12
        
        return TIAN_GAN[gan_index], DI_ZHI[zhi_index]
    
    def _calculate_month(self, year, month, day, hour, minute, year_gan):
        """
        计算月柱
        
        月柱以节气为界，使用五虎遁
        """
        # 简化的节气判断
        # 寅月（正月）：立春到惊蛰
        # 卯月（二月）：惊蛰到清明
        # ...
        
        # 根据年份和月份确定月支
        # 正月建寅，即正月为寅月
        month_zhi_index = (month + 1) % 12  # 正月=2(寅), 二月=3(卯), ...
        if month_zhi_index == 0:
            month_zhi_index = 12
        month_zhi = DI_ZHI[month_zhi_index - 1]
        
        # 使用五虎遁计算月干
        # 甲己之年丙作首，乙庚之岁戊为头，丙辛必定寻庚起，丁壬壬位顺行流，戊癸何方发，甲寅之上好追求
        wu_hu_dun = {
            '甲': 2, '己': 2,  # 丙寅
            '乙': 4, '庚': 4,  # 戊寅
            '丙': 6, '辛': 6,  # 庚寅
            '丁': 8, '壬': 8,  # 壬寅
            '戊': 0, '癸': 0   # 甲寅
        }
        
        base_gan_index = wu_hu_dun.get(year_gan, 0)
        month_gan_index = (base_gan_index + (month_zhi_index - 1)) % 10
        month_gan = TIAN_GAN[month_gan_index]
        
        return month_gan, month_zhi
    
    def _calculate_day(self, year, month, day):
        """
        计算日柱
        
        使用简化的计算方法
        """
        # 以1900年1月1日为基准日（甲戌日）
        base_date = date(1900, 1, 1)
        target_date = date(year, month, day)
        days_diff = (target_date - base_date).days
        
        # 计算日干支
        # 甲戌日的天干索引是0（甲），地支索引是10（戌）
        gan_index = (days_diff + 0) % 10
        zhi_index = (days_diff + 10) % 12
        
        return TIAN_GAN[gan_index], DI_ZHI[zhi_index]
    
    def _calculate_hour(self, day_gan, hour, minute, year, month, day):
        """
        计算时柱
        
        使用五鼠遁
        """
        # 计算时支
        # 子时：23:00-1:00
        if hour == 23 or (hour == 0 and minute < 0):
            hour_zhi_index = 0  # 子
        else:
            hour_zhi_index = ((hour + 1) // 2) % 12
        
        hour_zhi = DI_ZHI[hour_zhi_index]
        
        # 使用五鼠遁计算时干
        # 五鼠遁：甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
        wu_shu_dun = {
            '甲': 0, '己': 0,  # 甲子
            '乙': 2, '庚': 2,  # 丙子
            '丙': 4, '辛': 4,  # 戊子
            '丁': 6, '壬': 6,  # 庚子
            '戊': 8, '癸': 8   # 壬子
        }
        
        base_gan_index = wu_shu_dun.get(day_gan, 0)
        hour_gan_index = (base_gan_index + hour_zhi_index) % 10
        hour_gan = TIAN_GAN[hour_gan_index]
        
        return hour_gan, hour_zhi


# 创建全局计算器实例
calculator = SiZhuCalculator()


def calculate_sizhu(target_date, hour=12, minute=0, second=0):
    """
    计算四柱的便捷函数（统一入口）
    
    【重要说明】
    这是计算四柱的唯一入口函数，使用精确的农历计算方法
    
    Args:
        target_date: datetime.date对象或datetime对象
        hour: 小时(0-23)
        minute: 分钟(0-59)
        second: 秒(0-59)
        
    Returns:
        dict: 包含年柱、月柱、日柱、时柱的字典
    """
    if isinstance(target_date, datetime):
        hour = target_date.hour
        minute = target_date.minute
        second = target_date.second
        target_date = target_date.date()
    
    return calculator.calculate(target_date, hour, minute, second)


def get_lunar_date(target_date, hour=12, minute=0, second=0):
    """
    获取农历日期
    """
    if isinstance(target_date, datetime):
        hour = target_date.hour
        minute = target_date.minute
        second = target_date.second
        target_date = target_date.date()

    year = target_date.year
    month = target_date.month
    day = target_date.day

    if HAS_SXTWL:
        try:
            # 使用sxtwl直接获取农历信息
            day_obj = sxtwl.fromSolar(year, month, day)
            
            lunar_year = day_obj.getLunarYear()
            lunar_month = day_obj.getLunarMonth()
            lunar_day = day_obj.getLunarDay()
            is_leap = day_obj.isLunarLeap()
            
            # 获取节气
            jie_qi = None
            if day_obj.hasJieQi():
                jie_qi_idx = day_obj.getJieQi()
                jie_qi_names = [
                    "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
                    "春分", "清明", "谷雨", "立夏", "小满", "芒种",
                    "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
                    "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"
                ]
                if 0 <= jie_qi_idx < len(jie_qi_names):
                    jie_qi = jie_qi_names[jie_qi_idx]
            
            # 格式化农历月份和日期
            month_names = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
            day_names = [
                "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
            ]
            
            leap_str = "闰" if is_leap else ""
            
            # 安全获取月份
            if 1 <= lunar_month <= 12:
                month_str = month_names[lunar_month - 1]
            else:
                month_str = str(lunar_month)
            
            # 安全获取日期
            if 1 <= lunar_day <= len(day_names):
                day_str = day_names[lunar_day - 1]
            else:
                day_str = str(lunar_day)
            
            # 计算生肖
            zodiac = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
            zodiac_str = zodiac[(lunar_year - 4) % 12]
            
            return {
                'year': lunar_year,
                'month': f"{leap_str}{month_str}月",
                'day': day_str,
                'month_chinese': f"{leap_str}{month_str}月",
                'day_chinese': day_str,
                '中文': f"{lunar_year}年{leap_str}{month_str}月{day_str}",
                '生肖': zodiac_str,
                '节气': jie_qi,
                '验证': True
            }
        except Exception as e:
            logger.warning(f"获取农历信息失败: {e}")
            return {
                'year': year,
                'month': f"{month}月",
                'day': f"{day}日",
                'month_chinese': f"{month}月",
                'day_chinese': f"{day}日",
                '中文': f"{year}年{month}月{day}日",
                '生肖': "",
                '节气': None,
                '验证': False
            }
    else:
        # 没有sxtwl库时的备用方案
        return {
            'year': year,
            'month': f"{month}月",
            'day': f"{day}日",
            'month_chinese': f"{month}月",
            'day_chinese': f"{day}日",
            '中文': f"{year}年{month}月{day}日",
            '生肖': "",
            '节气': None,
            '验证': False
        }


def analyze_sizhu(sizhu):
    """
    分析四柱的便捷函数
    
    Args:
        sizhu: calculate_sizhu()返回的字典
        
    Returns:
        dict: 包含五行、十神、夫星子星等信息的字典
    """
    # 获取日干
    day_gan = sizhu.get('day_gan')
    if not day_gan and '日柱' in sizhu:
        day_gan = sizhu['日柱'][0]
    
    if not day_gan:
        raise ValueError("无法获取日干")
    
    # 计算五行
    wuxing = {}
    for key in ['年柱', '月柱', '日柱', '时柱']:
        if key in sizhu:
            wuxing[key] = get_gan_wuxing(sizhu[key][0])
    
    # 计算十神
    shishen = {}
    for key in ['年柱', '月柱', '时柱']:
        if key in sizhu:
            shishen[key] = get_shishen(day_gan, sizhu[key][0])
    
    fuzi = get_fuzi(day_gan)
    
    return {
        '五行': wuxing,
        '十神': shishen,
        '夫星子星': fuzi
    }


def enhance_sizhu(sizhu):
    """
    增强四柱信息的便捷函数
    
    Args:
        sizhu: calculate_sizhu()返回的字典
        
    Returns:
        dict: 包含纳音、十二长生、藏干等信息的字典
    """
    from .八字分析工具 import get_nayin, get_zhangsheng
    
    result = sizhu.copy()
    
    # 添加纳音
    for key in ['年柱', '月柱', '日柱', '时柱']:
        if key in sizhu:
            result[f'{key}_纳音'] = get_nayin(sizhu[key])
    
    # 添加十二长生
    if 'day_gan' in sizhu:
        for key in ['年柱', '月柱', '日柱', '时柱']:
            if key in sizhu and len(sizhu[key]) >= 2:
                zhi = sizhu[key][1]
                result[f'{key}_长生'] = get_zhangsheng(sizhu['day_gan'], zhi)
    
    return result


if __name__ == '__main__':
    print("=" * 80)
    print("四柱计算器测试")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        (2024, 1, 1, 12, 0),   # 测试2024年1月1日
        (2024, 2, 4, 16, 25),  # 立春前
        (2024, 2, 4, 16, 28),  # 立春后
        (1984, 2, 5, 12, 0),   # 甲子年
        (1990, 2, 5, 12, 0),   # 庚午年
        (2000, 2, 5, 12, 0),   # 庚辰年
        (2023, 2, 5, 12, 0),   # 癸卯年
        (1972, 1, 8, 12, 0),    # 测试1972年1月8日
        (1972, 5, 11, 8, 0),    # 测试1972年5月11日
        (1998, 10, 13, 23, 0),  # 测试1998年10月13日23点
        (1999, 4, 5, 12, 0),    # 测试1999年4月5日
    ]
    
    for case in test_cases:
        year, month, day, hour, minute = case
        target_date = date(year, month, day)
        result = calculate_sizhu(target_date, hour, minute)
        print(f"\n日期: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
        print(f"年柱: {result['年柱']}")
        print(f"月柱: {result['月柱']}")
        print(f"日柱: {result['日柱']}")
        print(f"时柱: {result['时柱']}")
    
    print("\n" + "=" * 80)