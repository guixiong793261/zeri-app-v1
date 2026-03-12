# -*- coding: utf-8 -*-
"""
日期转换模块

提供完整的日期转换功能：
1. 公历转农历
2. 农历转公历
3. 节气查询
4. 日期格式转换
5. 真太阳时计算
6. 干支计算
"""

import sys
import os
from datetime import date, datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 尝试导入 sxtwl 库
try:
    import sxtwl
    HAS_SXTWL = True
    logger.info("成功导入 sxtwl 库")
except ImportError:
    HAS_SXTWL = False
    logger.warning("sxtwl 库未安装")


class DateConverter:
    """
    日期转换器类
    
    提供完整的日期转换功能
    """
    
    def __init__(self):
        """初始化转换器"""
        self.has_sxtwl = HAS_SXTWL
    
    def solar_to_lunar(self, solar_date, hour=12, minute=0, second=0):
        """
        公历转农历
        
        Args:
            solar_date: datetime.date或datetime对象
            hour: 小时(0-23)
            minute: 分钟(0-59)
            second: 秒(0-59)
            
        Returns:
            dict: 农历日期信息
        """
        if isinstance(solar_date, datetime):
            hour = solar_date.hour
            minute = solar_date.minute
            second = solar_date.second
            solar_date = solar_date.date()
        
        if not self.has_sxtwl:
            raise ImportError("sxtwl 库未安装，无法进行公历转农历")
        
        day_obj = sxtwl.fromSolar(solar_date.year, solar_date.month, solar_date.day)
        
        # 获取农历信息
        lunar_year = day_obj.getLunarYear()
        lunar_month = day_obj.getLunarMonth()
        lunar_day = day_obj.getLunarDay()
        
        # 判断是否闰月
        is_leap = day_obj.isLunarLeap()
        
        # 转换为中文
        month_chinese = self._number_to_chinese(lunar_month)
        day_chinese = self._number_to_chinese(lunar_day)
        if is_leap:
            month_chinese = "闰" + month_chinese
        
        chinese = f"{lunar_year}年{month_chinese}月{day_chinese}"
        
        # 获取生肖
        zodiac = self._get_zodiac(lunar_year)
        
        # 获取节气
        jie_qi = self._get_jie_qi(solar_date.year, solar_date.month, solar_date.day, hour, minute)
        
        return {
            '年': lunar_year,
            '月': lunar_month,
            '日': lunar_day,
            '月中文': month_chinese,
            '日中文': day_chinese,
            '中文': chinese,
            '闰月': is_leap,
            '生肖': zodiac,
            '节气': jie_qi
        }
    
    def lunar_to_solar(self, lunar_year, lunar_month, lunar_day, is_leap=False):
        """
        农历转公历
        
        Args:
            lunar_year: 农历年
            lunar_month: 农历月
            lunar_day: 农历日
            is_leap: 是否闰月
            
        Returns:
            datetime.date: 公历日期
        """
        if not self.has_sxtwl:
            raise ImportError("sxtwl 库未安装，无法进行农历转公历")
        
        day_obj = sxtwl.fromLunar(lunar_year, lunar_month, lunar_day, is_leap)
        
        return date(day_obj.getSolarYear(), day_obj.getSolarMonth(), day_obj.getSolarDay())
    
    def get_jie_qi(self, year, month, day, hour=12, minute=0):
        """
        获取节气信息
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            hour: 小时
            minute: 分钟
            
        Returns:
            dict: 节气信息
        """
        if not self.has_sxtwl:
            raise ImportError("sxtwl 库未安装，无法获取节气信息")
        
        return self._get_jie_qi(year, month, day, hour, minute)
    
    def _get_jie_qi(self, year, month, day, hour=12, minute=0):
        """
        获取节气信息（内部方法）
        """
        if not self.has_sxtwl:
            return None
        
        # 获取当年节气列表
        jq_list = sxtwl.getJieQiByYear(year)
        
        # 节气名称
        jie_qi_names = [
            '立春', '雨水', '惊蛰', '春分', '清明', '谷雨',
            '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
            '立秋', '处暑', '白露', '秋分', '寒露', '霜降',
            '立冬', '小雪', '大雪', '冬至', '小寒', '大寒'
        ]
        
        # 当前时间
        current_dt = datetime(year, month, day, hour, minute, 0)
        
        # 查找当前节气
        current_jq = None
        next_jq = None
        prev_jq = None
        
        for i, jq in enumerate(jq_list):
            jd = jq.jd
            dd = sxtwl.JD2DD(jd)
            jq_dt = datetime(int(dd.Y), int(dd.M), 
                           int(dd.D), int(dd.h), 
                           int(dd.m), int(dd.s))
            
            if jq_dt <= current_dt:
                prev_jq = {
                    '名称': jie_qi_names[i],
                    '时间': jq_dt,
                    '索引': i
                }
            else:
                next_jq = {
                    '名称': jie_qi_names[i],
                    '时间': jq_dt,
                    '索引': i
                }
                break
        
        return {
            '当前节气': prev_jq,
            '下一节气': next_jq
        }
    
    def calculate_true_solar_time(self, solar_date, hour, minute, second=0, longitude=116.4074):
        """
        计算真太阳时
        
        Args:
            solar_date: datetime.date或datetime对象
            hour: 小时(0-23)
            minute: 分钟(0-59)
            second: 秒(0-59)
            longitude: 经度（默认北京经度116.4074）
            
        Returns:
            dict: 真太阳时信息
        """
        if isinstance(solar_date, datetime):
            hour = solar_date.hour
            minute = solar_date.minute
            second = solar_date.second
            solar_date = solar_date.date()
        
        # 北京经度
        beijing_longitude = 116.4074
        
        # 计算经度差（每度4分钟）
        longitude_diff = longitude - beijing_longitude
        time_diff = longitude_diff * 4  # 分钟
        
        # 转换为总秒数
        total_seconds = hour * 3600 + minute * 60 + second
        total_seconds += time_diff * 60
        
        # 计算真太阳时
        true_hour = int(total_seconds // 3600) % 24
        true_minute = int((total_seconds % 3600) // 60)
        true_second = int(total_seconds % 60)
        
        return {
            '标准时间': f"{hour:02d}:{minute:02d}:{second:02d}",
            '真太阳时': f"{true_hour:02d}:{true_minute:02d}:{true_second:02d}",
            '经度': longitude,
            '时间差': time_diff,
            '时差说明': f"经度差{longitude_diff:.2f}度，时间差{time_diff:.2f}分钟"
        }
    
    def calculate_gan_zhi(self, solar_date, hour=12, minute=0, second=0):
        """
        计算干支（年干支、月干支、日干支、时干支）
        
        Args:
            solar_date: datetime.date或datetime对象
            hour: 小时(0-23)
            minute: 分钟(0-59)
            second: 秒(0-59)
            
        Returns:
            dict: 干支信息
        """
        if isinstance(solar_date, datetime):
            hour = solar_date.hour
            minute = solar_date.minute
            second = solar_date.second
            solar_date = solar_date.date()
        
        if not self.has_sxtwl:
            raise ImportError("sxtwl 库未安装，无法计算干支")
        
        day_obj = sxtwl.fromSolar(solar_date.year, solar_date.month, solar_date.day)
        
        # 获取干支
        year_gz = day_obj.getYearGZ()
        day_gz = day_obj.getDayGZ()
        hour_gz = day_obj.getHourGZ(hour)
        
        # 天干地支
        tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        di_zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 转换为干支
        year_gan_zhi = tian_gan[year_gz.tg] + di_zhi[year_gz.dz]
        day_gan_zhi = tian_gan[day_gz.tg] + di_zhi[day_gz.dz]
        hour_gan_zhi = tian_gan[hour_gz.tg] + di_zhi[hour_gz.dz]
        
        # 计算月干支（使用精确节气时间）
        month_gan_zhi = self._calculate_month_gan_zhi(solar_date.year, solar_date.month, 
                                                      solar_date.day, hour, minute, 
                                                      tian_gan[year_gz.tg])
        
        return {
            '年干支': year_gan_zhi,
            '月干支': month_gan_zhi,
            '日干支': day_gan_zhi,
            '时干支': hour_gan_zhi
        }
    
    def _calculate_month_gan_zhi(self, year, month, day, hour, minute, year_gan):
        """
        计算月干支（使用精确节气时间）
        """
        # 五虎遁
        wu_hu_dun = {
            '甲': 2, '己': 2,
            '乙': 3, '庚': 3,
            '丙': 4, '辛': 4,
            '丁': 5, '壬': 5,
            '戊': 6, '癸': 6
        }
        
        # 节气与月支对应
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
            22: '丑'   # 小寒
        }
        
        # 当前时间
        current_dt = datetime(year, month, day, hour, minute, 0)
        
        # 获取当年节气列表
        jq_list = sxtwl.getJieQiByYear(year)
        
        # 构建节气时间列表
        jie_times = []
        for jie_idx in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
            jd = jq_list[jie_idx].jd
            dd = sxtwl.JD2DD(jd)
            dt = datetime(int(dd.Y), int(dd.M), 
                        int(dd.D), int(dd.h), 
                        int(dd.m), int(dd.s))
            jie_times.append((dt, jie_idx))
        
        # 如果当前时间在立春之前，需要添加前一年的小寒
        lichun_jd = jq_list[0].jd
        lichun_dd = sxtwl.JD2DD(lichun_jd)
        lichun_dt = datetime(int(lichun_dd.Y), 
                            int(lichun_dd.M), 
                            int(lichun_dd.D), 
                            int(lichun_dd.h), 
                            int(lichun_dd.m), 
                            int(lichun_dd.s))
        if current_dt < lichun_dt:
            jq_list_prev = sxtwl.getJieQiByYear(year - 1)
            jd = jq_list_prev[22].jd
            dd = sxtwl.JD2DD(jd)
            dt = datetime(int(dd.Y), int(dd.M), 
                        int(dd.D), int(dd.h), 
                        int(dd.m), int(dd.s))
            jie_times.append((dt, 22))
        
        # 排序
        jie_times.sort(key=lambda x: x[0])
        
        # 找到当前时间所在的月份
        month_zhi = '寅'
        
        for i, (dt, jie_idx) in enumerate(jie_times):
            if current_dt < dt:
                if i == 0:
                    month_zhi = '子'
                else:
                    prev_jie_idx = jie_times[i-1][1]
                    month_zhi = jie_to_month.get(prev_jie_idx, '寅')
                break
        else:
            last_jie_idx = jie_times[-1][1]
            month_zhi = jie_to_month.get(last_jie_idx, '丑')
        
        # 使用五虎遁计算月干
        base_gan_index = wu_hu_dun.get(year_gan, 0)
        di_zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        month_zhi_index = di_zhi.index(month_zhi)
        offset = (month_zhi_index - 2 + 12) % 12
        tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        month_gan_index = (base_gan_index + offset) % 10
        month_gan = tian_gan[month_gan_index]
        
        return month_gan + month_zhi
    
    def format_date(self, date_obj, format_type='标准'):
        """
        日期格式转换
        
        Args:
            date_obj: datetime.date或datetime对象
            format_type: 格式类型（标准、中文、ISO、短格式）
            
        Returns:
            str: 格式化后的日期字符串
        """
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        if format_type == '标准':
            return date_obj.strftime("%Y年%m月%d日")
        elif format_type == '中文':
            return self._date_to_chinese(date_obj)
        elif format_type == 'ISO':
            return date_obj.isoformat()
        elif format_type == '短格式':
            return date_obj.strftime("%Y-%m-%d")
        else:
            return str(date_obj)
    
    def _number_to_chinese(self, num):
        """
        数字转中文
        """
        chinese_nums = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        if num <= 10:
            return chinese_nums[num]
        elif num < 20:
            return '十' + chinese_nums[num - 10]
        else:
            return chinese_nums[num // 10] + '十' + (chinese_nums[num % 10] if num % 10 != 0 else '')
    
    def _date_to_chinese(self, date_obj):
        """
        日期转中文
        """
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        
        year_chinese = ''.join([self._number_to_chinese(int(d)) for d in str(year)])
        month_chinese = self._number_to_chinese(month)
        day_chinese = self._number_to_chinese(day)
        
        return f"{year_chinese}年{month_chinese}月{day_chinese}"
    
    def _get_zodiac(self, year):
        """
        获取生肖
        """
        zodiacs = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        return zodiacs[(year - 4) % 12]


# 创建全局转换器实例
converter = DateConverter()


def solar_to_lunar(solar_date, hour=12, minute=0, second=0):
    """
    公历转农历（便捷函数）
    """
    return converter.solar_to_lunar(solar_date, hour, minute, second)


def lunar_to_solar(lunar_year, lunar_month, lunar_day, is_leap=False):
    """
    农历转公历（便捷函数）
    """
    return converter.lunar_to_solar(lunar_year, lunar_month, lunar_day, is_leap)


def get_jie_qi(year, month, day, hour=12, minute=0):
    """
    获取节气信息（便捷函数）
    """
    return converter.get_jie_qi(year, month, day, hour, minute)


def calculate_true_solar_time(solar_date, hour, minute, second=0, longitude=116.4074):
    """
    计算真太阳时（便捷函数）
    """
    return converter.calculate_true_solar_time(solar_date, hour, minute, second, longitude)


def calculate_gan_zhi(solar_date, hour=12, minute=0, second=0):
    """
    计算干支（便捷函数）
    """
    return converter.calculate_gan_zhi(solar_date, hour, minute, second)


def format_date(date_obj, format_type='标准'):
    """
    日期格式转换（便捷函数）
    """
    return converter.format_date(date_obj, format_type)
