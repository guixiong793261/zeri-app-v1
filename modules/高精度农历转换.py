# -*- coding: utf-8 -*-
"""
================================================================================
高精度农历转换.py
高精度公历转农历与四柱八字模块（双库校验）
- 主库：sxtwl（天文算法，范围广，精度高）
- 校验库：lunar-python（数据表查询，功能全面）

【关于双库校验差异的说明】
------------------------------------------------------------------------------
由于 sxtwl 和 lunar-python 使用不同的算法计算八字，在节气交界日可能出现
月柱不一致的情况。这是正常现象，原因是：

1. 节气切换时刻的计算精度不同
   - sxtwl 使用天文算法，基于精确的节气时刻
   - lunar-python 使用数据表，可能有分钟级的误差

2. 对择日的影响
   - 影响程度：中等（主要影响月柱相关的分析）
   - 年柱、日柱、时柱通常一致
   - 大部分择日规则基于日柱，影响相对较小

3. 建议
   - 普通择日：使用默认模式（strict_mode=False），以 sxtwl 结果为准
   - 精确择日：在节气交界日（如立春、惊蛰等）前后几天，建议人工复核
   - 严格模式：strict_mode=True 会在不一致时抛出异常，适合调试使用

安装依赖：
    pip install sxtwl lunar-python loguru
================================================================================
"""

import sxtwl
from lunar_python import Solar
from datetime import datetime, date, timedelta
from typing import Dict, Optional, Tuple
from loguru import logger
import warnings


class HighPrecisionLunar:
    """双库校验的农历转换类"""

    def __init__(self, strict_mode: bool = False):
        """
        :param strict_mode: True 时校验不一致则抛出异常；False 仅记录警告
        """
        self.strict_mode = strict_mode
        logger.remove()
        logger.add(lambda msg: print(msg, end=''), level="WARNING")

    @staticmethod
    def _tiangan(idx: int) -> str:
        return ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"][idx]

    @staticmethod
    def _dizhi(idx: int) -> str:
        return ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"][idx]

    @staticmethod
    def _get_zodiac(lunar_year: int) -> str:
        """生肖（sxtwl 已按立春调整）"""
        zodiac = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
        return zodiac[(lunar_year - 4) % 12]

    def _get_eight_char_sxtwl(self, day_obj, hour: int) -> Dict[str, str]:
        """从 sxtwl 的 Day 对象提取八字"""
        year_gz = day_obj.getYearGZ()
        month_gz = day_obj.getMonthGZ()
        day_gz = day_obj.getDayGZ()
        hour_gz = day_obj.getHourGZ(hour)
        
        return {
            'year': self._tiangan(year_gz.tg) + self._dizhi(year_gz.dz),
            'month': self._tiangan(month_gz.tg) + self._dizhi(month_gz.dz),
            'day': self._tiangan(day_gz.tg) + self._dizhi(day_gz.dz),
            'hour': self._tiangan(hour_gz.tg) + self._dizhi(hour_gz.dz)
        }

    @staticmethod
    def _get_jieqi_name(jieqi_idx: int) -> str:
        """将节气索引转换为名称"""
        jieqi_names = [
            "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
            "春分", "清明", "谷雨", "立夏", "小满", "芒种",
            "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
            "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"
        ]
        if 0 <= jieqi_idx < len(jieqi_names):
            return jieqi_names[jieqi_idx]
        return None

    def _get_lunar_info_sxtwl(self, year: int, month: int, day: int,
                               hour: int, minute: int, second: int) -> Dict:
        """使用 sxtwl 计算农历和八字"""
        day_obj = sxtwl.fromSolar(year, month, day)
        
        lunar_year = day_obj.getLunarYear()
        lunar_month = day_obj.getLunarMonth()
        lunar_day = day_obj.getLunarDay()
        is_leap = day_obj.isLunarLeap()
        
        jie_qi = None
        if day_obj.hasJieQi():
            jie_qi_idx = day_obj.getJieQi()
            jie_qi = self._get_jieqi_name(jie_qi_idx)

        return {
            'lunar_year': lunar_year,
            'lunar_month': lunar_month,
            'lunar_day': lunar_day,
            'is_leap': is_leap,
            'leap_month': sxtwl.getRunMonth(year),
            'year_zodiac': self._get_zodiac(lunar_year),
            'eight_char': self._get_eight_char_sxtwl(day_obj, hour),
            'jie_qi': jie_qi
        }

    def _get_lunar_info_lunar_python(self, year: int, month: int, day: int,
                                      hour: int, minute: int, second: int) -> Dict:
        """使用 lunar-python 计算农历和八字"""
        solar = Solar.fromYmdHms(year, month, day, hour, minute, second)
        lunar = solar.getLunar()
        eight_char = lunar.getEightChar()
        
        lunar_month = lunar.getMonth()
        is_leap = lunar_month < 0
        lunar_month = abs(lunar_month)
        
        jie_qi = lunar.getJie() if lunar.getJie() else lunar.getQi()
        
        try:
            from lunar_python import LunarYear
            lunar_year_obj = LunarYear.fromYear(lunar.getYear())
            leap_month = lunar_year_obj.getLeapMonth()
        except:
            leap_month = 0

        return {
            'lunar_year': lunar.getYear(),
            'lunar_month': lunar_month,
            'lunar_day': lunar.getDay(),
            'is_leap': is_leap,
            'leap_month': leap_month,
            'year_zodiac': lunar.getYearShengXiao(),
            'eight_char': {
                'year': eight_char.getYear(),
                'month': eight_char.getMonth(),
                'day': eight_char.getDay(),
                'hour': eight_char.getTime()
            },
            'jie_qi': jie_qi
        }

    def solar_to_lunar_with_check(self, year: int, month: int, day: int,
                                   hour: int = 0, minute: int = 0, second: int = 0) -> Dict:
        """
        公历转农历，返回包含农历信息、八字和校验状态的字典
        结果以 sxtwl 为准，同时附上校验一致性标记
        """
        result_sxtwl = self._get_lunar_info_sxtwl(year, month, day, hour, minute, second)
        result_lp = self._get_lunar_info_lunar_python(year, month, day, hour, minute, second)

        consistent = True
        diffs = []

        if (result_sxtwl['lunar_year'] != result_lp['lunar_year'] or
            result_sxtwl['lunar_month'] != result_lp['lunar_month'] or
            result_sxtwl['lunar_day'] != result_lp['lunar_day'] or
            result_sxtwl['is_leap'] != result_lp['is_leap']):
            consistent = False
            diffs.append(
                f"农历日期不一致: sxtwl={result_sxtwl['lunar_year']}-{result_sxtwl['lunar_month']}-"
                f"{result_sxtwl['lunar_day']}{'(闰)' if result_sxtwl['is_leap'] else ''} vs "
                f"lunar-python={result_lp['lunar_year']}-{result_lp['lunar_month']}-"
                f"{result_lp['lunar_day']}{'(闰)' if result_lp['is_leap'] else ''}"
            )

        ec_s = result_sxtwl['eight_char']
        ec_l = result_lp['eight_char']
        if ec_s != ec_l:
            consistent = False
            diffs.append(
                f"八字不一致: sxtwl={ec_s['year']} {ec_s['month']} {ec_s['day']} {ec_s['hour']} vs "
                f"lunar-python={ec_l['year']} {ec_l['month']} {ec_l['day']} {ec_l['hour']}"
            )

        if result_sxtwl['year_zodiac'] != result_lp['year_zodiac']:
            consistent = False
            diffs.append(
                f"生肖不一致: sxtwl={result_sxtwl['year_zodiac']} vs "
                f"lunar-python={result_lp['year_zodiac']}"
            )

        if not consistent:
            msg = f"双库校验发现差异 [{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}]:\n" + "\n".join(diffs)
            if self.strict_mode:
                raise ValueError(msg)
            else:
                logger.warning(msg)
                warnings.warn(msg)

        return {
            'solar_date': f"{year}-{month:02d}-{day:02d}",
            'solar_time': f"{hour:02d}:{minute:02d}:{second:02d}",
            'lunar_year': result_sxtwl['lunar_year'],
            'lunar_month': result_sxtwl['lunar_month'],
            'lunar_day': result_sxtwl['lunar_day'],
            'is_leap': result_sxtwl['is_leap'],
            'leap_month': result_sxtwl['leap_month'],
            'lunar_date_str': self._format_lunar_date(
                result_sxtwl['lunar_year'],
                result_sxtwl['lunar_month'],
                result_sxtwl['lunar_day'],
                result_sxtwl['is_leap']
            ),
            'year_zodiac': result_sxtwl['year_zodiac'],
            'eight_char': result_sxtwl['eight_char'],
            'sizhu_str': self._format_sizhu(result_sxtwl['eight_char']),
            'jie_qi': result_sxtwl['jie_qi'],
            'verified': consistent,
            'diffs': diffs if not consistent else [],
            '_check_consistent': consistent,
            '_check_details': diffs if not consistent else []
        }

    def _format_lunar_date(self, year: int, month: int, day: int, is_leap: bool) -> str:
        """格式化农历日期字符串"""
        month_names = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
        day_names = [
            "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
            "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
            "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
        ]
        leap_str = "闰" if is_leap else ""
        month_str = month_names[month - 1] if 1 <= month <= 12 else str(month)
        day_str = day_names[day - 1] if 1 <= day <= 30 else str(day)
        return f"农历{year}年{leap_str}{month_str}月{day_str}"

    def _format_sizhu(self, eight_char: Dict[str, str]) -> str:
        """格式化四柱字符串"""
        return f"{eight_char['year']}年 {eight_char['month']}月 {eight_char['day']}日 {eight_char['hour']}时"

    def batch_check(self, start_date: Tuple[int, int, int],
                    end_date: Tuple[int, int, int],
                    hour: int = 12, minute: int = 0, second: int = 0) -> None:
        """
        对日期区间内每天固定时刻进行校验，统计一致率
        :param start_date: (年,月,日)
        :param end_date:   (年,月,日)
        :param hour, minute, second: 每天检查的时刻
        """
        start = date(*start_date)
        end = date(*end_date)
        current = start
        total = 0
        inconsistent = 0
        while current <= end:
            total += 1
            try:
                res = self.solar_to_lunar_with_check(
                    current.year, current.month, current.day,
                    hour, minute, second
                )
                if not res['_check_consistent']:
                    inconsistent += 1
            except Exception as e:
                logger.error(f"处理日期 {current} 出错: {e}")
                inconsistent += 1
            current += timedelta(days=1)
        logger.info(
            f"批量检查完成：总计 {total} 天，不一致 {inconsistent} 天，一致率 {(total-inconsistent)/total*100:.2f}%"
        )

    def get_sizhu(self, year: int, month: int, day: int,
                  hour: int = 0, minute: int = 0, second: int = 0) -> Dict:
        """
        获取四柱八字信息（简化接口）
        返回格式与现有 sizhu_calculator 模块兼容
        """
        result = self.solar_to_lunar_with_check(year, month, day, hour, minute, second)
        ec = result['eight_char']
        # 天干地支列表
        tg = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
        dz = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

        return {
            '年柱': ec['year'],
            '月柱': ec['month'],
            '日柱': ec['day'],
            '时柱': ec['hour'],
            'year_gan_idx': tg.index(ec['year'][0]),
            'year_zhi_idx': dz.index(ec['year'][1]),
            'month_gan_idx': tg.index(ec['month'][0]),
            'month_zhi_idx': dz.index(ec['month'][1]),
            'day_gan_idx': tg.index(ec['day'][0]),
            'day_zhi_idx': dz.index(ec['day'][1]),
            'hour_gan_idx': tg.index(ec['hour'][0]),
            'hour_zhi_idx': dz.index(ec['hour'][1]),
            'year_gan': ec['year'][0],
            'year_zhi': ec['year'][1],
            'month_gan': ec['month'][0],
            'month_zhi': ec['month'][1],
            'day_gan': ec['day'][0],
            'day_zhi': ec['day'][1],
            'hour_gan': ec['hour'][0],
            'hour_zhi': ec['hour'][1],
            'lunar_date_str': result['lunar_date_str'],
            'jie_qi': result['jie_qi'],
            'verified': result['verified']
        }


_lunar_converter: Optional[HighPrecisionLunar] = None


def get_lunar_converter(strict_mode: bool = False) -> HighPrecisionLunar:
    """获取全局农历转换器实例"""
    global _lunar_converter
    if _lunar_converter is None:
        _lunar_converter = HighPrecisionLunar(strict_mode)
    return _lunar_converter


def calculate_sizhu_high_precision(year: int, month: int, day: int,
                                    hour: int = 12, minute: int = 0) -> Dict:
    """
    高精度四柱计算（便捷函数）
    接口与现有 calculate_sizhu 兼容
    """
    converter = get_lunar_converter()
    return converter.get_sizhu(year, month, day, hour, minute, 0)


if __name__ == "__main__":
    cal = HighPrecisionLunar(strict_mode=False)

    print("=" * 60)
    print("高精度农历转换测试")
    print("=" * 60)

    test_cases = [
        (2023, 1, 22, 12, 0, 0),   # 春节
        (2024, 2, 4, 16, 25, 0),   # 立春前
        (2024, 2, 4, 16, 27, 0),   # 立春后
        (2023, 12, 31, 23, 30, 0), # 跨日子时
        (2000, 1, 1, 0, 0, 0),     # 2000年元旦
        (2100, 12, 31, 23, 59, 59) # 边界
    ]

    for case in test_cases:
        print(f"\n输入: {case[0]}-{case[1]:02d}-{case[2]:02d} {case[3]:02d}:{case[4]:02d}:{case[5]:02d}")
        result = cal.solar_to_lunar_with_check(*case)
        print(f"农历: {result['lunar_year']}年{result['lunar_month']}月{result['lunar_day']}日 "
              f"{'闰' if result['is_leap'] else ''}")
        print(f"八字: {result['eight_char']['year']} {result['eight_char']['month']} "
              f"{result['eight_char']['day']} {result['eight_char']['hour']}")
        print(f"生肖: {result['year_zodiac']} | 节气: {result['jie_qi'] or '无'}")
        print(f"校验一致: {result['_check_consistent']}")
        if result['_check_details']:
            print("差异详情:", result['_check_details'])

    # 批量检查示例（可选，范围不宜过大）
    # cal.batch_check((2023,1,1), (2023,1,31), hour=12)
