# -*- coding: utf-8 -*-
"""
================================================================================
八字排盘模块
================================================================================
封装完整的八字排盘流程，提供详细的事主信息，包括：
- 四柱信息（年柱、月柱、日柱、时柱）
- 纳音五行
- 十二长生状态
- 大运计算
- 命局分析

使用方式：
- 在主程序或日课评分系统中用于事主分析
- 通过BaZiPanPan类获取详细的事主信息
- 结果可直接用于显示或评分
================================================================================
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta, date
import logging
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.八字分析工具 import (
    TIAN_GAN, DI_ZHI,
    GAN_WUXING, ZHI_WUXING,
    get_nayin, get_zhangsheng,
    calculate_wuxing_score,
    get_shishen
)
from modules.四柱计算器 import calculate_sizhu

# 导入lunar_python用于起运年龄计算
try:
    from lunar_python import Solar
    HAS_LUNAR_PYTHON = True
except ImportError:
    HAS_LUNAR_PYTHON = False
    logger.warning("lunar_python模块未安装，起运年龄计算将使用简化算法")

logger = logging.getLogger(__name__)


class BaZiPanPan:
    """
    八字排盘类
    封装完整的排盘流程，提供详细的事主信息
    """
    
    def __init__(self, birth_year: int, birth_month: int, birth_day: int, 
                 birth_hour: int, birth_minute: int, gender: str = '男'):
        """
        初始化八字排盘
        
        Args:
            birth_year: 出生年份
            birth_month: 出生月份（1-12）
            birth_day: 出生日（1-31）
            birth_hour: 出生小时（0-23）
            birth_minute: 出生分钟（0-59）
            gender: 性别，'男'或'女'
        """
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.birth_day = birth_day
        self.birth_hour = birth_hour
        self.birth_minute = birth_minute
        self.gender = gender
        self.sizhu = None
        self.panpan_result = None
        
    def calculate(self) -> Dict:
        """
        计算排盘结果
        
        Returns:
            Dict: 排盘结果
        """
        try:
            # 计算四柱
            self.sizhu = self._calculate_sizhu()
            
            # 计算详细信息
            self.panpan_result = self._calculate_details()
            
            # 计算起运年龄
            start_age, start_year = self._calculate_start_age()
            self.panpan_result['起运年龄'] = start_age
            self.panpan_result['起运年份'] = start_year
            
            # 计算大运
            self.panpan_result['大运'] = self._calculate_d大运()
            
            return self.panpan_result
        except Exception as e:
            logger.error(f"排盘计算失败: {e}")
            return {}
    
    def _calculate_sizhu(self) -> Dict:
        """
        计算四柱信息
        
        Returns:
            Dict: 四柱信息
        """
        # 使用原始计算方法
        target_date = date(self.birth_year, self.birth_month, self.birth_day)
        sizhu = calculate_sizhu(
            target_date, 
            self.birth_hour, 
            self.birth_minute, 
            0
        )
        
        return sizhu
    
    def _calculate_details(self) -> Dict:
        """
        计算详细信息
        
        Returns:
            Dict: 详细信息
        """
        if not self.sizhu:
            return {}
        
        details = {
            '四柱': {
                '年柱': self.sizhu.get('年柱', ''),
                '月柱': self.sizhu.get('月柱', ''),
                '日柱': self.sizhu.get('日柱', ''),
                '时柱': self.sizhu.get('时柱', '')
            },
            '天干地支': {
                'year_gan': self.sizhu.get('year_gan', ''),
                'year_zhi': self.sizhu.get('year_zhi', ''),
                'month_gan': self.sizhu.get('month_gan', ''),
                'month_zhi': self.sizhu.get('month_zhi', ''),
                'day_gan': self.sizhu.get('day_gan', ''),
                'day_zhi': self.sizhu.get('day_zhi', ''),
                'hour_gan': self.sizhu.get('hour_gan', ''),
                'hour_zhi': self.sizhu.get('hour_zhi', '')
            },
            '纳音': {
                '年柱': get_nayin(self.sizhu.get('年柱', '')),
                '月柱': get_nayin(self.sizhu.get('月柱', '')),
                '日柱': get_nayin(self.sizhu.get('日柱', '')),
                '时柱': get_nayin(self.sizhu.get('时柱', ''))
            },
            '十二长生': {
                '年支': get_zhangsheng(self.sizhu.get('day_gan', ''), 
                                     self.sizhu.get('year_zhi', '')),
                '月支': get_zhangsheng(self.sizhu.get('day_gan', ''), 
                                     self.sizhu.get('month_zhi', '')),
                '日支': get_zhangsheng(self.sizhu.get('day_gan', ''), 
                                     self.sizhu.get('day_zhi', '')),
                '时支': get_zhangsheng(self.sizhu.get('day_gan', ''), 
                                     self.sizhu.get('hour_zhi', ''))
            },
            '五行分数': calculate_wuxing_score(self.sizhu, include_canggan=True),
            '十神': self._calculate_shishen(),
            '基本信息': {
                '性别': self.gender,
                '出生日期': f"{self.birth_year}-{self.birth_month:02d}-{self.birth_day:02d} {self.birth_hour:02d}:{self.birth_minute:02d}"
            }
        }
        
        return details
    
    def _calculate_shishen(self) -> Dict:
        """
        计算十神
        
        Returns:
            Dict: 十神信息
        """
        day_gan = self.sizhu.get('day_gan', '')
        if not day_gan:
            return {}
        
        shishen = {
            '年干': get_shishen(day_gan, self.sizhu.get('year_gan', '')),
            '月干': get_shishen(day_gan, self.sizhu.get('month_gan', '')),
            '时干': get_shishen(day_gan, self.sizhu.get('hour_gan', ''))
        }
        
        return shishen
    
    def _calculate_d大运(self) -> List[Dict]:
        """
        计算大运
        
        Returns:
            List[Dict]: 大运信息
        """
        大运_list = []
        
        # 计算起运年龄
        start_age, start_year = self._calculate_start_age()
        
        # 计算大运
        month_gan = self.sizhu.get('month_gan', '')
        month_zhi = self.sizhu.get('month_zhi', '')
        
        if not month_gan or not month_zhi:
            return 大运_list
        
        # 确定大运方向
        # 阳年生男、阴年生女：顺排
        # 阳年生女、阴年生男：逆排
        year_gan = self.sizhu.get('year_gan', '')
        yang_gans = ['甲', '丙', '戊', '庚', '壬']
        is_yang_year = year_gan in yang_gans
        
        if (is_yang_year and self.gender == '男') or (not is_yang_year and self.gender == '女'):
            direction = 1  # 顺行
        else:
            direction = -1  # 逆行
        
        # 计算大运
        for i in range(10):  # 通常计算10步大运
            step_age = start_age + i * 10
            step_year = start_year + i * 10
            
            # 计算大运干支（从月柱开始）
            offset = i * direction
            yun_gan, yun_zhi = self._get_ganzhi_by_offset(month_gan, month_zhi, offset)
            
            大运_list.append({
                '序号': i + 1,
                '大运': f"{yun_gan}{yun_zhi}",
                '起运年龄': step_age,
                '起运年份': step_year,
                '纳音': get_nayin(f"{yun_gan}{yun_zhi}")
            })
        
        return 大运_list
    
    def _calculate_start_age(self) -> Tuple[float, int]:
        """
        计算起运年龄
        
        根据出生日期和节气计算起运年龄
        使用lunar_python库获取节气信息
        
        规则：
        - 阳年生男、阴年生女：顺排（计算到下一个节气的天数）
        - 阳年生女、阴年生男：逆排（计算到上一个节气的天数）
        - 起运岁数 = 天数差 / 3（保留一位小数）
        
        Returns:
            Tuple[float, int]: (起运年龄, 起运年份)
        """
        try:
            # 检查lunar_python是否可用
            if not HAS_LUNAR_PYTHON:
                logger.warning("lunar_python不可用，使用简化算法")
                return 1.0, self.birth_year + 1
            
            # 使用lunar_python计算
            solar = Solar.fromYmdHms(
                self.birth_year, self.birth_month, self.birth_day,
                self.birth_hour, self.birth_minute, 0
            )
            lunar = solar.getLunar()
            
            # 获取年干阴阳
            year_gan = self.sizhu.get('year_gan', '') if self.sizhu else ''
            # 阳干：甲丙戊庚壬（索引为偶数）
            # 阴干：乙丁己辛癸（索引为奇数）
            yang_gans = ['甲', '丙', '戊', '庚', '壬']
            is_yang_year = year_gan in yang_gans
            
            # 判断顺逆
            # 阳年生男、阴年生女：顺排
            # 阳年生女、阴年生男：逆排
            is_forward = (is_yang_year and self.gender == '男') or (not is_yang_year and self.gender == '女')
            
            # 获取节气
            if is_forward:
                # 顺排：计算到下一个节气的天数
                next_jq = lunar.getNextJieQi()
                if next_jq:
                    next_jq_solar = next_jq.getSolar()
                    next_date = datetime(
                        next_jq_solar.getYear(),
                        next_jq_solar.getMonth(),
                        next_jq_solar.getDay(),
                        next_jq_solar.getHour(),
                        next_jq_solar.getMinute(),
                        next_jq_solar.getSecond()
                    )
                    birth_date = datetime(
                        self.birth_year, self.birth_month, self.birth_day,
                        self.birth_hour, self.birth_minute, 0
                    )
                    days_diff = (next_date - birth_date).total_seconds() / 86400  # 转换为天数
                else:
                    days_diff = 3  # 默认值
            else:
                # 逆排：计算到上一个节气的天数
                prev_jq = lunar.getPrevJieQi()
                if prev_jq:
                    prev_jq_solar = prev_jq.getSolar()
                    prev_date = datetime(
                        prev_jq_solar.getYear(),
                        prev_jq_solar.getMonth(),
                        prev_jq_solar.getDay(),
                        prev_jq_solar.getHour(),
                        prev_jq_solar.getMinute(),
                        prev_jq_solar.getSecond()
                    )
                    birth_date = datetime(
                        self.birth_year, self.birth_month, self.birth_day,
                        self.birth_hour, self.birth_minute, 0
                    )
                    days_diff = (birth_date - prev_date).total_seconds() / 86400  # 转换为天数
                else:
                    days_diff = 3  # 默认值
            
            # 计算起运岁数（保留一位小数）
            start_age = round(days_diff / 3, 1)
            
            # 计算起运年份
            start_year = self.birth_year + int(start_age)
            
            logger.info(f"起运年龄计算: 性别={self.gender}, 年干={year_gan}, "
                       f"阳年={is_yang_year}, 顺排={is_forward}, "
                       f"天数差={days_diff:.2f}, 起运年龄={start_age}")
            
            return start_age, start_year
            
        except Exception as e:
            logger.error(f"计算起运年龄失败: {e}")
            # 回退到简单计算
            return 1.0, self.birth_year + 1
    
    def _get_ganzhi_by_offset(self, gan: str, zhi: str, offset: int) -> Tuple[str, str]:
        """
        根据偏移量计算干支
        
        Args:
            gan: 起始天干
            zhi: 起始地支
            offset: 偏移量
            
        Returns:
            Tuple[str, str]: 新的干支
        """
        if gan not in TIAN_GAN or zhi not in DI_ZHI:
            return '', ''
        
        gan_idx = TIAN_GAN.index(gan)
        zhi_idx = DI_ZHI.index(zhi)
        
        new_gan_idx = (gan_idx + offset) % 10
        new_zhi_idx = (zhi_idx + offset) % 12
        
        return TIAN_GAN[new_gan_idx], DI_ZHI[new_zhi_idx]
    
    def get_panpan_result(self) -> Dict:
        """
        获取排盘结果
        
        Returns:
            Dict: 排盘结果
        """
        if not self.panpan_result:
            self.calculate()
        
        return self.panpan_result
    
    def get_sizhu(self) -> Dict:
        """
        获取四柱信息
        
        Returns:
            Dict: 四柱信息
        """
        if not self.sizhu:
            self.calculate()
        
        return self.sizhu


# 测试代码
if __name__ == '__main__':
    print("=" * 80)
    print("八字排盘模块测试")
    print("=" * 80)
    
    # 测试排盘
    panpan = BaZiPanPan(2024, 2, 4, 16, 27, '男')
    result = panpan.calculate()
    
    print("\n【排盘结果】")
    print(f"四柱: {result['四柱']}")
    print(f"纳音: {result['纳音']}")
    print(f"十二长生: {result['十二长生']}")
    print(f"五行分数: {result['五行分数']}")
    print(f"十神: {result['十神']}")
    
    print("\n【大运】")
    for yun in result['大运']:
        print(f"第{yun['序号']}步大运: {yun['大运']}，{yun['起运年龄']}岁起运，{yun['起运年份']}年，纳音: {yun['纳音']}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
