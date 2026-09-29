# -*- coding: utf-8 -*-
"""
================================================================================
真太阳时.py
真太阳时修正模块（纯函数，零依赖）

【拍板口径】（docs/问题跟踪_001 §43.9 / §46 / §48）
- ① 修正顺序：墙钟 → 经度 → 均时差 → 真太阳时 → 子时判定
- ② 必含均时差（EoT）：NOAA 闭式式（5 行零依赖，年误差 <1 分钟）
  依据：D2 探针实测，不含 EoT 时东经120°主体用户区 190 天/年晚子翻转被漏
- ③ 输入形态：直接经度 MVP（GUI 经度框，默认 120°E）
- ⑤ 海外策略：仅支持 UTC+8 墙钟语义，海外用户需自行换算（文档声明）

【启停语义】（v3 拍板）
经度=120 等价于不启用（北京时间基准），调用方在传参前判断；
本模块函数被调用即无条件按公式修正。

【精度口径】
分钟粒度（int 截断），秒不参与——与 D4 交节精度审计结论一致
（引擎交节判定有效粒度同为分钟）。
================================================================================
"""

import math
from datetime import datetime, timedelta

# 东经120°标准时基准；等于此值 = 不启用（北京时间基准）
TRUE_SOLAR_BASE_LONGITUDE = 120.0

# 经度有效域：覆盖中国大陆全境及周边（新疆西端 ~73°E 至黑龙江东端 ~135°E，留裕量）
_LONGITUDE_MIN = 60.0
_LONGITUDE_MAX = 150.0


def equation_of_time_minutes(day_of_year: int) -> float:
    """NOAA 闭式均时差（EoT），单位分钟，年误差 <1 分钟。

    EoT = 9.87·sin(2B) − 7.53·cos(B) − 1.5·sin(B)
    B   = 360°/365 × (N − 81)，N = 年内第几天（1-365/366）

    锚点（2026 平年实测）：2 月约 −14.6min（极小），10 月底/11 月约 +16.5min（极大）。
    """
    B = math.radians(360.0 / 365.0 * (day_of_year - 81))
    return 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)


def true_solar_offset_minutes(longitude: float, day_of_year: int) -> float:
    """真太阳时总偏移（分钟）= 经度修正 4min×(经度−120°) + 均时差 EoT。

    东经 >120 为正（真太阳时早于北京墙钟），西经 <120 为负。
    """
    _validate_longitude(longitude)
    return 4.0 * (longitude - TRUE_SOLAR_BASE_LONGITUDE) + equation_of_time_minutes(day_of_year)


def apply_true_solar(year: int, month: int, day: int, hour: int, minute: int,
                     longitude: float) -> tuple:
    """按拍板①顺序修正墙钟为真太阳时，返回 (year, month, day, hour, minute)。

    内部用 datetime+timedelta 处理跨日/跨月/跨年翻转（如 23:50 修正 +20min
    → 次日 00:10，日柱/晚子时判定由下游四柱计算器按修正后时刻自动得出）。
    精度为分钟粒度（int 截断），秒不参与、不携带。
    """
    _validate_longitude(longitude)
    dt = datetime(year, month, day, hour, minute)
    # EoT 取修正前日期的年内第几天：EoT 日漂移 ≤0.03min，远小于分钟粒度，可忽略
    offset = true_solar_offset_minutes(longitude, dt.timetuple().tm_yday)
    corrected = dt + timedelta(minutes=offset)
    return (corrected.year, corrected.month, corrected.day,
            corrected.hour, corrected.minute)


def _validate_longitude(longitude: float) -> None:
    """经度域校验：越界显式抛错（静默失败家族防御——不静默钳位）。"""
    if not (_LONGITUDE_MIN <= longitude <= _LONGITUDE_MAX):
        raise ValueError(
            f"经度 {longitude} 超出有效域 [{_LONGITUDE_MIN}, {_LONGITUDE_MAX}]°E；"
            f"本软件仅支持 UTC+8 时区（docs/001 §43.9 拍板⑤），"
            f"海外用户请先自行换算为北京墙钟时间")
