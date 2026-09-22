# -*- coding: utf-8 -*-
"""
玄空飞星 · 日课展示 (手机自适应全功能版 / 单文件独立运行版)
全屏显示，所有输入为下拉框，支持触摸滚动

【单文件版说明 2026-09-13】
排盘 / 农历 / 四柱 / 坐山判级 / 评语 / 评分 / 吉日搜索全部内联在本文件内
（工具函数、高精度农历转换、四柱计算器、玄空飞星引擎四份 modules 源码构建时嵌入，
逻辑与桌面及4端 modules 同源同口径，由 C:/Temp/build_phone_standalone_0913.py 生成）。
单独把本文件拷到手机即可运行，不需要 modules 文件夹。
依赖（手机 Python IDE 里 pip 安装）：sxtwl、lunar-python；tkinter 一般 IDE 自带。
"""

import sys
import os

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime, date, timedelta
import calendar

# ============================================================
#  第三方库自检（缺库时中文弹框提示，避免手机上一堆英文报错）
# ============================================================
try:
    import sxtwl
except ImportError:
    try:
        messagebox.showerror("缺少依赖", "未安装农历库 sxtwl。\n请在 Python IDE 的终端里执行：pip install sxtwl")
    except Exception:
        print("缺少依赖 sxtwl，请先 pip install sxtwl")
    sys.exit(1)

try:
    import lunar_python  # noqa: F401  高精度农历转换需要
except ImportError:
    try:
        messagebox.showerror("缺少依赖", "未安装农历库 lunar-python。\n请在 Python IDE 的终端里执行：pip install lunar-python")
    except Exception:
        print("缺少依赖 lunar-python，请先 pip install lunar-python")
    sys.exit(1)


# ======================================================================
# 【内联模块】工具函数（构建自 modules/，勿手改；改算法请改 modules 后重新构建）
# ======================================================================

# -*- coding: utf-8 -*-
"""
================================================================================
辅助函数模块
================================================================================
包含干支转换、节气计算、五行生克等基础功能
================================================================================
"""

from datetime import date, datetime, timedelta

# 天干地支基础数据
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 五行属性
TIAN_GAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火',
    '戊': '土', '己': '土', '庚': '金', '辛': '金',
    '壬': '水', '癸': '水'
}

DI_ZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

# 五行生克关系
WUXING_SHENG = {
    '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
}

WUXING_KE = {
    '木': '土', '土': '水', '水': '火', '火': '金', '金': '木'
}

# 冲合关系
CHONG = {0:6, 1:7, 2:8, 3:9, 4:10, 5:11, 6:0, 7:1, 8:2, 9:3, 10:4, 11:5}
HE = {0:1, 1:0, 2:11, 11:2, 3:10, 10:3, 4:9, 9:4, 5:8, 8:5, 6:7, 7:6}

# 五虎遁（月干）
WU_HU_DUN = {'甲': 2, '己': 2, '乙': 4, '庚': 4, '丙': 6, '辛': 6, '丁': 8, '壬': 8, '戊': 0, '癸': 0}

# 五鼠遁（时干）
WU_SHU_DUN = {'甲': 0, '己': 0, '乙': 2, '庚': 2, '丙': 4, '辛': 4, '丁': 6, '壬': 6, '戊': 8, '癸': 8}

# 天德月德
TIANDE = {2: '丁', 3: '申', 4: '壬', 5: '辛', 6: '亥', 7: '甲', 8: '癸', 9: '寅', 10: '丙', 11: '乙', 0: '巳', 1: '庚'}
YUEDE = {2: '丙', 3: '甲', 4: '壬', 5: '庚', 6: '丙', 7: '甲', 8: '壬', 9: '庚', 10: '丙', 11: '甲', 0: '壬', 1: '庚'}

# 三煞
SANSHA_MAP = {
    '申': [5,6,7], '子': [5,6,7], '辰': [5,6,7],      # 南方（巳午未）
    '寅': [11,0,1], '午': [11,0,1], '戌': [11,0,1],      # 北方（亥子丑）
    '巳': [2,3,4], '酉': [2,3,4], '丑': [2,3,4],          # 东方（寅卯辰）
    '亥': [8,9,10], '卯': [8,9,10], '未': [8,9,10],      # 西方（申酉戌）
}

# 夫星子星（女命）
# 夫星：克我者（官杀），阳日干取正官，阴日干取七杀
# 子星：我生者（食伤），阳日干取食神，阴日干取伤官
FU_ZI_XING = {
    '甲': {'fu': '辛酉', 'qi': '庚申', 'zi': '丙午', 'shang': '丁巳'},  # 甲木：正官辛金，食神丙火
    '乙': {'fu': '庚申', 'qi': '辛酉', 'zi': '丁巳', 'shang': '丙午'},  # 乙木：正官庚金，食神丁火
    '丙': {'fu': '癸亥', 'qi': '壬子', 'zi': '戊戌', 'shang': '己丑'},  # 丙火：正官癸水，食神戊土
    '丁': {'fu': '壬子', 'qi': '癸亥', 'zi': '己丑', 'shang': '戊戌'},  # 丁火：正官壬水，食神己土
    '戊': {'fu': '乙卯', 'qi': '甲寅', 'zi': '丙午', 'shang': '丁巳'},  # 戊土：正官乙木，食神庚金
    '己': {'fu': '甲寅', 'qi': '乙卯', 'zi': '辛酉', 'shang': '庚申'},  # 己土：正官甲木，食神辛金
    '庚': {'fu': '丁巳', 'qi': '丙午', 'zi': '壬子', 'shang': '癸亥'},  # 庚金：正官丁火，食神壬水
    '辛': {'fu': '丙午', 'qi': '丁巳', 'zi': '癸亥', 'shang': '壬子'},  # 辛金：正官丙火，食神癸水
    '壬': {'fu': '己丑', 'qi': '戊戌', 'zi': '甲寅', 'shang': '乙卯'},  # 壬水：正官己土，食神甲木
    '癸': {'fu': '戊戌', 'qi': '己丑', 'zi': '乙卯', 'shang': '甲寅'},  # 癸水：正官戊土，食神乙木
}

# 二十四山向
# 分为八宫，每宫三山
SHAN_XIANG_24 = {
    '坎宫': ['壬', '子', '癸'],
    '艮宫': ['丑', '艮', '寅'],
    '震宫': ['甲', '卯', '乙'],
    '巽宫': ['辰', '巽', '巳'],
    '离宫': ['丙', '午', '丁'],
    '坤宫': ['未', '坤', '申'],
    '兑宫': ['庚', '酉', '辛'],
    '乾宫': ['戌', '乾', '亥'],
}

# 二十四山向列表（按顺时针顺序）
SHAN_XIANG_LIST = [
    '壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙',
    '辰', '巽', '巳', '丙', '午', '丁', '未', '坤', '申',
    '庚', '酉', '辛', '戌', '乾', '亥'
]

# 山向五行属性
SHAN_XIANG_WUXING = {
    '壬': '水', '子': '水', '癸': '水',
    '丑': '土', '艮': '土', '寅': '木',
    '甲': '木', '卯': '木', '乙': '木',
    '辰': '土', '巽': '木', '巳': '火',
    '丙': '火', '午': '火', '丁': '火',
    '未': '土', '坤': '土', '申': '金',
    '庚': '金', '酉': '金', '辛': '金',
    '戌': '土', '乾': '金', '亥': '水',
}

# 十神
SHISHEN = {
    '甲': {'比肩': '甲', '劫财': '乙', '食神': '丙', '伤官': '丁', '偏财': '戊', '正财': '己', '七杀': '庚', '正官': '辛', '偏印': '壬', '正印': '癸'},
    '乙': {'比肩': '乙', '劫财': '甲', '食神': '丁', '伤官': '丙', '偏财': '己', '正财': '戊', '七杀': '辛', '正官': '庚', '偏印': '癸', '正印': '壬'},
    '丙': {'比肩': '丙', '劫财': '丁', '食神': '戊', '伤官': '己', '偏财': '庚', '正财': '辛', '七杀': '壬', '正官': '癸', '偏印': '甲', '正印': '乙'},
    '丁': {'比肩': '丁', '劫财': '丙', '食神': '己', '伤官': '戊', '偏财': '辛', '正财': '庚', '七杀': '癸', '正官': '壬', '偏印': '乙', '正印': '甲'},
    '戊': {'比肩': '戊', '劫财': '己', '食神': '庚', '伤官': '辛', '偏财': '壬', '正财': '癸', '七杀': '甲', '正官': '乙', '偏印': '丙', '正印': '丁'},
    '己': {'比肩': '己', '劫财': '戊', '食神': '辛', '伤官': '庚', '偏财': '癸', '正财': '壬', '七杀': '乙', '正官': '甲', '偏印': '丁', '正印': '丙'},
    '庚': {'比肩': '庚', '劫财': '辛', '食神': '壬', '伤官': '癸', '偏财': '甲', '正财': '乙', '七杀': '丙', '正官': '丁', '偏印': '戊', '正印': '己'},
    '辛': {'比肩': '辛', '劫财': '庚', '食神': '癸', '伤官': '壬', '偏财': '乙', '正财': '甲', '七杀': '丁', '正官': '丙', '偏印': '己', '正印': '戊'},
    '壬': {'比肩': '壬', '劫财': '癸', '食神': '甲', '伤官': '乙', '偏财': '丙', '正财': '丁', '七杀': '戊', '正官': '己', '偏印': '庚', '正印': '辛'},
    '癸': {'比肩': '癸', '劫财': '壬', '食神': '乙', '伤官': '甲', '偏财': '丁', '正财': '丙', '七杀': '己', '正官': '戊', '偏印': '辛', '正印': '庚'},
}

# 带权重的藏干表（用于五行分数计算）
# 注意：ZHIGAN_MAP已移至八字分析工具.py，这里保留ZHIGAN_WEIGHTED用于兼容
ZHIGAN_WEIGHTED = {
    '子': [('癸', 1.0)],
    '丑': [('己', 0.6), ('癸', 0.3), ('辛', 0.1)],
    '寅': [('甲', 0.6), ('丙', 0.3), ('戊', 0.1)],
    '卯': [('乙', 1.0)],
    '辰': [('戊', 0.6), ('乙', 0.3), ('癸', 0.1)],
    '巳': [('丙', 0.6), ('庚', 0.3), ('戊', 0.1)],
    '午': [('丁', 0.7), ('己', 0.3)],
    '未': [('己', 0.6), ('丁', 0.3), ('乙', 0.1)],
    '申': [('庚', 0.6), ('壬', 0.3), ('戊', 0.1)],
    '酉': [('辛', 1.0)],
    '戌': [('戊', 0.6), ('辛', 0.3), ('丁', 0.1)],
    '亥': [('壬', 0.7), ('甲', 0.3)]
}

def get_gan_wuxing(gan):
    """获取天干五行"""
    return TIAN_GAN_WUXING.get(gan, '')

def get_zhi_wuxing(zhi):
    """获取地支五行"""
    return DI_ZHI_WUXING.get(zhi, '')

def get_pillar_wuxing(pillar):
    """获取柱的五行（天干五行）"""
    if not pillar:
        return ''
    return get_gan_wuxing(pillar[0])

def get_shengke(wuxing1, wuxing2):
    """获取五行生克关系"""
    if wuxing1 == wuxing2:
        return '同'
    elif WUXING_SHENG.get(wuxing1) == wuxing2:
        return '生'
    elif WUXING_KE.get(wuxing1) == wuxing2:
        return '克'
    elif WUXING_SHENG.get(wuxing2) == wuxing1:
        return '被生'
    elif WUXING_KE.get(wuxing2) == wuxing1:
        return '被克'
    return '无关'

def get_hour_zhi_index(hour, minute=0):
    """获取时支索引（晚子时派口径，与本文件 SiZhuCalculator._calculate_hour 一致）

    23:00-23:59 时支为子（索引0）；日柱换日不在此函数职责内——
    本软件 0:00 子正换日，晚子时日柱仍属当日。
    """
    if hour == 23 or hour == 0:
        return 0
    return ((hour + 1) // 2) % 12

def get_shishen(day_gan: str, target_gan: str) -> str:
    """
    获取十神（使用八字分析工具中的算法）
    
    Args:
        day_gan: 日干
        target_gan: 目标天干
        
    Returns:
        str: 十神名称
    """
    try:
        from .八字分析工具 import get_shishen as new_get_shishen
        return new_get_shishen(day_gan, target_gan)
    except ImportError:
        # 回退到旧算法
        if day_gan == target_gan:
            return '比肩'
        
        if day_gan not in TIAN_GAN or target_gan not in TIAN_GAN:
            return '未知'
        
        day_idx = TIAN_GAN.index(day_gan)
        target_idx = TIAN_GAN.index(target_gan)
        
        # 判断阴阳（偶数为阳，奇数为阴）
        day_yang = day_idx % 2 == 0
        target_yang = target_idx % 2 == 0
        is_same_yin_yang = (day_yang == target_yang)
        
        # 计算五行关系
        day_wx = TIAN_GAN_WUXING[day_gan]
        target_wx = TIAN_GAN_WUXING[target_gan]
        
        # 同我
        if target_wx == day_wx:
            return '劫财'
        
        # 我生
        if WUXING_SHENG.get(day_wx) == target_wx:
            return '食神' if is_same_yin_yang else '伤官'
        
        # 我克
        if WUXING_KE.get(day_wx) == target_wx:
            return '偏财' if is_same_yin_yang else '正财'
        
        # 克我
        if WUXING_KE.get(target_wx) == day_wx:
            return '七杀' if is_same_yin_yang else '正官'
        
        # 生我
        if WUXING_SHENG.get(target_wx) == day_wx:
            return '偏印' if is_same_yin_yang else '正印'
        
        return '未知'

# 【通书嫁娶·五虎遁真夫星/真天嗣起例】（2026-09 修正，替换旧"按年支硬查表"）
# 年上起月：甲己丙寅、乙庚戊寅、丙辛庚寅、丁壬壬寅、戊癸甲寅
_WUHU_START_GAN = {'甲': '丙', '己': '丙', '乙': '戊', '庚': '戊',
                   '丙': '庚', '辛': '庚', '丁': '壬', '壬': '壬',
                   '戊': '甲', '癸': '甲'}
# 女命以年干为"我"：正官（克我、阴阳异）= 真夫星；食神（我生、同阴阳）= 真天嗣（子星）
_FUZHUANG_GAN = {'甲': '辛', '乙': '庚', '丙': '癸', '丁': '壬', '戊': '乙',
                 '己': '甲', '庚': '丁', '辛': '丙', '壬': '己', '癸': '戊'}
_TIANSI_GAN = {'甲': '丙', '乙': '丁', '丙': '戊', '丁': '己', '戊': '庚',
               '己': '辛', '庚': '壬', '辛': '癸', '壬': '甲', '癸': '乙'}


def _wuhu_dun_zhi(year_gan, target_gan):
    """五虎遁：从寅月起遁，返回 target_gan 首次临宫的地支。

    如甲年（丙寅起）遁到辛临未、遁到丙临寅，故真夫星辛未、真天嗣丙寅。
    """
    if year_gan not in _WUHU_START_GAN or target_gan not in TIAN_GAN:
        return ''
    start = TIAN_GAN.index(_WUHU_START_GAN[year_gan])
    yin = DI_ZHI.index('寅')
    for i in range(12):
        if TIAN_GAN[(start + i) % 10] == target_gan:
            return DI_ZHI[(yin + i) % 12]
    return ''


def get_fuzi(year_gan, year_zhi=None):
    """获取女命真夫星、真天嗣（子星）——通书嫁娶五虎遁起例，只取决于年干。

    【典籍口径】以女命年干为"我"：克我且阴阳异者为正官（真夫星），
    我生且同阴阳者为食神（真天嗣/子星）；地支一律以五虎遁从寅月起遁，
    遁到该星天干首次临宫之支（《选择求真》卷五嫁娶总集）。
    定局：夫星 甲辛未/乙庚辰/丙癸巳/丁壬寅/戊乙卯/己甲戌/庚丁亥/辛丙申/
          壬己酉/癸戊午；
          天嗣 甲丙寅/乙丁亥/丙戊戌/丁己酉/戊庚申/己辛未/庚壬午/辛癸巳/
          壬甲辰/癸乙卯。

    Args:
        year_gan: 年柱天干
        year_zhi: 年柱地支（仅为兼容旧调用保留，真夫星/真天嗣不随年支变）

    Returns:
        dict: {'fu': 真夫星干支, 'zi': 真天嗣干支}；年干非法时两值为 None
    """
    if year_gan not in TIAN_GAN:
        return {'fu': None, 'zi': None}
    fu_gan = _FUZHUANG_GAN[year_gan]
    zi_gan = _TIANSI_GAN[year_gan]
    fu_zhi = _wuhu_dun_zhi(year_gan, fu_gan)
    zi_zhi = _wuhu_dun_zhi(year_gan, zi_gan)
    return {
        'fu': fu_gan + fu_zhi if fu_zhi else None,
        'zi': zi_gan + zi_zhi if zi_zhi else None,
    }


def get_yintai(month_gan, month_zhi):
    """获取阴胎（以女命月柱为基准，= 胎元）

    【单一权威公式】（《渊海子平》胎元法，阴阳二气对称）：
    计算方法：月柱天干顺进一位，地支顺进三位（= 干+1，支+3）。

    Args:
        month_gan: 月柱天干
        month_zhi: 月柱地支

    Returns:
        阴胎干支（如"戊午"），若输入非法返回 None
    """
    if month_gan not in TIAN_GAN or month_zhi not in DI_ZHI:
        return None

    gan_index = TIAN_GAN.index(month_gan)
    next_gan = TIAN_GAN[(gan_index + 1) % 10]

    zhi_index = DI_ZHI.index(month_zhi)
    next_zhi = DI_ZHI[(zhi_index + 3) % 12]

    return next_gan + next_zhi

def get_yangqi(month_gan, month_zhi):
    """获取阳气（男命/新郎，以生月月柱为基准）

    【典籍口径】（《选择求真·卷五》胎元起例 + 通书口诀“天进一兮地三和”）：
    阳气与阴胎同法：月柱天干顺进一位，地支顺进三位（= 干+1，支+3，即胎元）。
    男命所得称阳气、女命所得称阴胎；嫁娶日时忌冲犯。
    注：旧版误作“干+3支+1”对称公式，无典籍依据，2026-09 按典籍修正。

    Args:
        month_gan: 月柱天干
        month_zhi: 月柱地支

    Returns:
        阳气干支（如"乙卯"），若输入非法返回 None
    """
    if month_gan not in TIAN_GAN or month_zhi not in DI_ZHI:
        return None

    gan_index = TIAN_GAN.index(month_gan)
    next_gan = TIAN_GAN[(gan_index + 1) % 10]

    zhi_index = DI_ZHI.index(month_zhi)
    next_zhi = DI_ZHI[(zhi_index + 3) % 12]

    return next_gan + next_zhi

def format_date(dt):
    """格式化日期"""
    return dt.strftime('%Y年%m月%d日')

def format_datetime(dt):
    """格式化日期时间"""
    return dt.strftime('%Y年%m月%d日 %H:%M')


# ============================================================================
# 向后兼容：从八字工具整合模块导入增强功能
# ============================================================================
# 注意：新开发建议直接从八字工具整合模块导入

# 保存原始的 TIAN_GAN 和 DI_ZHI 常量
_original_TIAN_GAN = TIAN_GAN
_original_DI_ZHI = DI_ZHI

try:
    from .八字工具整合 import (
        # 数据定义
        GAN_WUXING,
        ZHI_WUXING,
        GAN_YINYANG,
        ZHI_YINYANG,
        ZHIGAN_WEIGHTED,
        ZHIGAN_SIMPLE,
        # 函数
        get_gan_wuxing as _get_gan_wuxing_new,
        get_zhi_wuxing as _get_zhi_wuxing_new,
        get_shishen as _get_shishen_new,
        calculate_wuxing_score,
        get_zhangsheng,
        get_nayin,
        check_liuhe,
        check_liuchong,
        check_liuhai,
        check_sanxing,
        check_sanhe,
        check_sanhui,
    )
    
    # 导出给外部使用
    __all__ = [
        # 基础数据
        'TIAN_GAN', 'DI_ZHI',
        'TIAN_GAN_WUXING', 'DI_ZHI_WUXING',
        'GAN_WUXING', 'ZHI_WUXING',
        'GAN_YINYANG', 'ZHI_YINYANG',
        'WUXING_SHENG', 'WUXING_KE',
        'CHONG', 'HE',
        'WU_HU_DUN', 'WU_SHU_DUN',
        'TIANDE', 'YUEDE',
        'SANSHA_MAP',
        'FU_ZI_XING',
        'SHAN_XIANG_24', 'SHAN_XIANG_LIST', 'SHAN_XIANG_WUXING',
        'SHISHEN',
        # 基础函数
        'get_gan_wuxing', 'get_zhi_wuxing',
        'get_pillar_wuxing', 'get_shengke',
        'get_hour_zhi_index', 'get_shishen',
        'get_fuzi',
        'format_date', 'format_datetime',
        # 八字工具整合的增强功能
        'ZHIGAN_WEIGHTED', 'ZHIGAN_SIMPLE',
        'calculate_wuxing_score',
        'get_zhangsheng', 'get_nayin',
        'check_liuhe', 'check_liuchong', 'check_liuhai',
        'check_sanxing', 'check_sanhe', 'check_sanhui',
    ]
    
    _BAZI_TOOLS_AVAILABLE = True
    
except ImportError:
    _BAZI_TOOLS_AVAILABLE = False
    # 恢复原始的 TIAN_GAN 和 DI_ZHI 常量
    TIAN_GAN = _original_TIAN_GAN
    DI_ZHI = _original_DI_ZHI
    # 定义本地的 ZHIGAN_SIMPLE 常量作为回退
    ZHIGAN_SIMPLE = {
        '子': ['癸'],
        '丑': ['己', '癸', '辛'],
        '寅': ['甲', '丙', '戊'],
        '卯': ['乙'],
        '辰': ['戊', '乙', '癸'],
        '巳': ['丙', '庚', '戊'],
        '午': ['丁', '己'],
        '未': ['己', '丁', '乙'],
        '申': ['庚', '壬', '戊'],
        '酉': ['辛'],
        '戌': ['戊', '辛', '丁'],
        '亥': ['壬', '甲']
    }
    # 定义本地的 ZHIGAN_WEIGHTED 常量作为回退
    ZHIGAN_WEIGHTED = {
        '子': [('癸', 1.0)],
        '丑': [('己', 0.6), ('癸', 0.3), ('辛', 0.1)],
        '寅': [('甲', 0.6), ('丙', 0.3), ('戊', 0.1)],
        '卯': [('乙', 1.0)],
        '辰': [('戊', 0.6), ('乙', 0.3), ('癸', 0.1)],
        '巳': [('丙', 0.6), ('庚', 0.3), ('戊', 0.1)],
        '午': [('丁', 0.7), ('己', 0.3)],
        '未': [('己', 0.6), ('丁', 0.3), ('乙', 0.1)],
        '申': [('庚', 0.6), ('壬', 0.3), ('戊', 0.1)],
        '酉': [('辛', 1.0)],
        '戌': [('戊', 0.6), ('辛', 0.3), ('丁', 0.1)],
        '亥': [('壬', 0.7), ('甲', 0.3)]
    }
    # 定义本地的 GAN_WUXING 和 ZHI_WUXING 常量作为回退
    GAN_WUXING = TIAN_GAN_WUXING
    ZHI_WUXING = DI_ZHI_WUXING
    # 定义本地的 GAN_YINYANG 和 ZHI_YINYANG 常量作为回退
    GAN_YINYANG = {
        '甲': '阳', '乙': '阴',
        '丙': '阳', '丁': '阴',
        '戊': '阳', '己': '阴',
        '庚': '阳', '辛': '阴',
        '壬': '阳', '癸': '阴'
    }
    ZHI_YINYANG = {
        '子': '阳', '丑': '阴', '寅': '阳', '卯': '阴',
        '辰': '阳', '巳': '阴', '午': '阳', '未': '阴',
        '申': '阳', '酉': '阴', '戌': '阳', '亥': '阴'
    }
    # 定义默认函数
    def calculate_wuxing_score(sizhu, include_canggan=True):
        return {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    def get_zhangsheng(day_gan, zhi):
        return '未知'
    def get_nayin(pillar):
        return '未知'
    def check_liuhe(zhi1, zhi2):
        return False
    def check_liuchong(zhi1, zhi2):
        return False
    def check_liuhai(zhi1, zhi2):
        return False
    def check_sanxing(zhi1, zhi2):
        return False
    def check_sanhe(zhis):
        return False
    def check_sanhui(zhis):
        return False
    __all__ = [
        'TIAN_GAN', 'DI_ZHI',
        'TIAN_GAN_WUXING', 'DI_ZHI_WUXING',
        'GAN_WUXING', 'ZHI_WUXING',
        'GAN_YINYANG', 'ZHI_YINYANG',
        'WUXING_SHENG', 'WUXING_KE',
        'CHONG', 'HE',
        'WU_HU_DUN', 'WU_SHU_DUN',
        'TIANDE', 'YUEDE',
        'SANSHA_MAP',
        'FU_ZI_XING',
        'SHAN_XIANG_24', 'SHAN_XIANG_LIST', 'SHAN_XIANG_WUXING',
        'SHISHEN',
        'ZHIGAN_WEIGHTED', 'ZHIGAN_SIMPLE',
        'get_gan_wuxing', 'get_zhi_wuxing',
        'get_pillar_wuxing', 'get_shengke',
        'get_hour_zhi_index', 'get_shishen',
        'get_fuzi',
        'format_date', 'format_datetime',
        'calculate_wuxing_score',
        'get_zhangsheng', 'get_nayin',
        'check_liuhe', 'check_liuchong', 'check_liuhai',
        'check_sanxing', 'check_sanhe', 'check_sanhui',
    ]

# ======================================================================
# 【内联模块】高精度农历转换（构建自 modules/，勿手改；改算法请改 modules 后重新构建）
# ======================================================================

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
try:
    from lunar_python import Solar
except ImportError:  # 单文件头部已强检查，此处仅构建期兜底
    Solar = None
from datetime import datetime, date, timedelta
from typing import Dict, Optional, Tuple
try:
    from loguru import logger
except ImportError:
    # 手机端可能没有 loguru：注入最小兼容桩（农历模块用到 logger.remove()/add() 等专有 API）
    import logging as _logging
    class _LoggerStub:
        def __init__(self):
            self._lg = _logging.getLogger("nongli")
        def remove(self):
            pass
        def add(self, *a, **k):
            pass
        def __getattr__(self, name):
            return getattr(self._lg, name)
    logger = _LoggerStub()
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

    def lunar_to_solar(self, lunar_year: int, lunar_month: int, lunar_day: int,
                       hour: int = 0, minute: int = 0, second: int = 0) -> Dict:
        """
        农历转公历
        :param lunar_year: 农历年
        :param lunar_month: 农历月（闰月为负数，如闰五月为-5）
        :param lunar_day: 农历日
        :param hour, minute, second: 时间
        :return: {'year': 公历年, 'month': 公历月, 'day': 公历日, 'hour': 时, 'minute': 分, 'second': 秒}
        """
        # 使用 sxtwl 进行农历转公历
        is_leap = lunar_month < 0
        lunar_month_abs = abs(lunar_month)
        
        # sxtwl 的农历转公历
        try:
            day_obj = sxtwl.fromLunar(lunar_year, lunar_month_abs, lunar_day, is_leap)
            solar_year = day_obj.getSolarYear()
            solar_month = day_obj.getSolarMonth()
            solar_day = day_obj.getSolarDay()
            
            return {
                'year': solar_year,
                'month': solar_month,
                'day': solar_day,
                'hour': hour,
                'minute': minute,
                'second': second
            }
        except Exception as e:
            logger.error(f"sxtwl 农历转公历失败: {e}")
            # 尝试使用 lunar-python
            try:
                from lunar_python import Lunar
                lunar = Lunar.fromYmd(lunar_year, lunar_month, lunar_day)
                solar = lunar.getSolar()
                return {
                    'year': solar.getYear(),
                    'month': solar.getMonth(),
                    'day': solar.getDay(),
                    'hour': hour,
                    'minute': minute,
                    'second': second
                }
            except Exception as e2:
                logger.error(f"lunar-python 农历转公历失败: {e2}")
                raise
        
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

# ======================================================================
# 【内联模块】四柱计算器（构建自 modules/，勿手改；改算法请改 modules 后重新构建）
# ======================================================================

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
import calendar
import re

# 配置日志
logging.basicConfig(level=logging.WARNING)
# logger 沿用农历转换块的 loguru/兼容桩实例（info/warning/error 同名方法均兼容，勿覆盖）

# 工具函数已内联于本单文件前部（TIAN_GAN/DI_ZHI/WU_HU_DUN 等同名全局可直接使用）

# 尝试导入 sxtwl 库
try:
    import sxtwl
    HAS_SXTWL = True
    logger.info("成功导入 sxtwl 库，使用精确的四柱计算方法")
except ImportError:
    HAS_SXTWL = False
    logger.warning("sxtwl 库未安装，使用备用计算方法")


def _parse_chinese_date_string(s):
    """
    尝试把多种常见中文/字符串日期格式解析成 (date, hour, minute)。

    支持格式：
      1. "YYYY年MM月DD日"
      2. "YYYY年MM月DD日 HH时MM分"
      3. "YYYY-MM-DD"
      4. "YYYY-MM-DD HH:MM:SS"
      5. "YYYY-MM-DD HH:MM"

    Returns:
        tuple: (date对象, hour_int, minute_int)，失败返回 None
    """
    if not isinstance(s, str):
        return None
    text = s.strip()
    if not text:
        return None

    # ---- 中文格式 ----
    m = re.match(
        r'^(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'
        r'(?:\s*(\d{1,2})\s*[时点\:：])?'
        r'(?:\s*(\d{1,2})\s*分)?'
        r'\s*$',
        text
    )
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        h = int(m.group(4)) if m.group(4) else 12
        mi = int(m.group(5)) if m.group(5) else 0
        try:
            return date(y, mo, d), h, mi
        except ValueError:
            return None

    # ---- ISO 格式 ----
    iso = re.match(
        r'^(\d{4})-(\d{1,2})-(\d{1,2})'
        r'(?:[\sT]+(\d{1,2})\:(\d{1,2})(?:\:(\d{1,2}))?)?'
        r'\s*$',
        text
    )
    if iso:
        y, mo, d = int(iso.group(1)), int(iso.group(2)), int(iso.group(3))
        h = int(iso.group(4)) if iso.group(4) else 12
        mi = int(iso.group(5)) if iso.group(5) else 0
        try:
            return date(y, mo, d), h, mi
        except ValueError:
            return None
    return None


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
        但经校验，sxtwl的日柱计算与标准八字计算有偏差，因此日柱使用修正后的计算方法
        """
        # 晚子时（23:00-23:59）口径——晚子时派：
        # 日柱仍属当日（0:00 子正换日），时支为子，时干按【当日日干】五鼠遁。
        # sxtwl.getHourGZ(23) 走子初派（按次日日干遁干），与本软件口径不符，
        # 故晚子时柱不用 sxtwl，改由本模块 _calculate_hour 遁出。
        is_late_zi = (hour == 23)

        # 计算日柱的日期：晚子时不进次日，仍用当日
        day_calc_year = year
        day_calc_month = month
        day_calc_day = day

        # 使用 sxtwl 计算时柱
        day_obj = sxtwl.fromSolar(year, month, day)

        # 转换为天干地支
        tg = TIAN_GAN
        dz = DI_ZHI

        # 日柱先于晚子时时柱算出（晚子时干依当日日干五鼠遁）
        day_gan, day_zhi = self._calculate_day(day_calc_year, day_calc_month, day_calc_day)

        # 获取时柱
        if is_late_zi:
            # 晚子时：时支子、时干按当日日干遁
            hour_gan, hour_zhi = self._calculate_hour(day_gan, 23, minute)
        else:
            hour_gz = day_obj.getHourGZ(hour)
            hour_gan = tg[hour_gz.tg]
            hour_zhi = dz[hour_gz.dz]
        
        # 计算年柱（根据立春时刻判断）
        # 获取当年立春时刻
        jq_list = sxtwl.getJieQiByYear(year)
        lichun_jd = jq_list[0].jd
        # 转换立春时刻为datetime
        lichun_dd = sxtwl.JD2DD(lichun_jd)
        from datetime import datetime
        lichun_dt = datetime(int(lichun_dd.Y), int(lichun_dd.M), int(lichun_dd.D), int(lichun_dd.h), int(lichun_dd.m), int(lichun_dd.s))
        # 当前时间
        current_dt = datetime(year, month, day, hour, minute, second)
        
        # 判断是否在立春之前
        if current_dt < lichun_dt:
            # 立春前，使用上一年的年柱
            prev_year = year - 1
            prev_day_obj = sxtwl.fromSolar(prev_year, 12, 31)
            year_gz = prev_day_obj.getYearGZ()
        else:
            # 立春后，使用下一年的年柱
            next_year = year + 1
            next_day_obj = sxtwl.fromSolar(next_year, 1, 1)
            year_gz = next_day_obj.getYearGZ()
        
        year_gan = tg[year_gz.tg]
        year_zhi = dz[year_gz.dz]
        
        # 计算月柱（使用精确节气时间）
        month_gan, month_zhi = self._calculate_month_pillar_precise(year, month, day, hour, minute, year_gan)

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
        try:
            current_dt = datetime(year, month, day, hour, minute, 0)
        except ValueError as e:
            # 处理无效日期，使用当月最后一天
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            current_dt = datetime(year, month, last_day, hour, minute, 0)
            logger.warning(f"无效日期 {year}-{month}-{day}，使用当月最后一天 {last_day}")
        
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
        
        当 sxtwl 计算四柱失败时使用此方法
        日柱使用基准日推算法，年柱和月柱使用sxtwl精确节气判断
        
        晚子时（23:00-23:59）按晚子时派：日柱仍属当日，时支为子、
        时干按当日日干五鼠遁（与 sxtwl 主链同一口径）。
        """
        from datetime import datetime, timedelta

        # 晚子时标记（23:00-23:59）
        is_late_zi = (hour == 23)

        # 计算日柱的日期：晚子时不进次日，仍用当日
        day_calc_year = year
        day_calc_month = month
        day_calc_day = day

        # 计算年柱（使用sxtwl精确节气判断立春）
        year_gan, year_zhi = self._calculate_year_precise(year, month, day, hour, minute, second)

        # 计算月柱（使用sxtwl精确节气判断）
        month_gan, month_zhi = self._calculate_month_pillar_precise(year, month, day, hour, minute, year_gan)

        # 计算日柱（晚子时日柱仍属当日）
        day_gan, day_zhi = self._calculate_day(day_calc_year, day_calc_month, day_calc_day)

        # 计算时柱（当日日干五鼠遁）。_calculate_hour 已按晚子时派处理 23 点，无需特判
        hour_gan, hour_zhi = self._calculate_hour(day_gan, hour, minute)
        
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
    
    def _calculate_year_precise(self, year, month, day, hour, minute, second):
        """
        使用sxtwl精确节气判断年柱
        
        年柱以立春为界，立春前属于上一年
        """
        if HAS_SXTWL:
            try:
                jq_list = sxtwl.getJieQiByYear(year)
                lichun_jd = jq_list[0].jd
                lichun_dd = sxtwl.JD2DD(lichun_jd)
                lichun_dt = datetime(int(lichun_dd.Y), int(lichun_dd.M), int(lichun_dd.D),
                                     int(lichun_dd.h), int(lichun_dd.m), int(lichun_dd.s))
                current_dt = datetime(year, month, day, hour, minute, second)
                
                if current_dt < lichun_dt:
                    calc_year = year - 1
                else:
                    calc_year = year
            except Exception:
                calc_year = self._get_year_by_simple_rule(year, month, day)
        else:
            calc_year = self._get_year_by_simple_rule(year, month, day)
        
        offset = (calc_year - 1984) % 60
        gan_index = offset % 10
        zhi_index = offset % 12
        return TIAN_GAN[gan_index], DI_ZHI[zhi_index]
    
    def _get_year_by_simple_rule(self, year, month, day):
        """
        简化的立春判断规则（当sxtwl不可用时使用）
        """
        if month < 2 or (month == 2 and day < 4):
            return year - 1
        return year
    
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
        基准日：1900年1月1日为甲戌日（与寿星天文历一致）
        """
        # 以1900年1月1日为基准日（甲戌日）
        base_date = date(1900, 1, 1)
        try:
            target_date = date(year, month, day)
        except ValueError as e:
            # 处理无效日期，使用当月最后一天
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            target_date = date(year, month, last_day)
            logger.warning(f"无效日期 {year}-{month}-{day}，使用当月最后一天 {last_day}")
        days_diff = (target_date - base_date).days
        
        # 计算日干支
        # 基准日1900年1月1日为甲戌日
        # 甲戌日的天干索引是0（甲），地支索引是10（戌）
        gan_index = (days_diff + 0) % 10  # 甲的索引是0
        zhi_index = (days_diff + 10) % 12  # 戌的索引是10
        
        # 特殊处理已移除，现在使用正确的基准日计算
        
        return TIAN_GAN[gan_index], DI_ZHI[zhi_index]
    
    def _calculate_hour(self, day_gan, hour, minute, year=None, month=None, day=None):
        """
        计算时柱
        
        使用五鼠遁
        """
        # 计算时支（晚子时派口径：23:00-23:59 与 0:00-0:59 同为子时；
        # 晚子时日柱归属由调用方保证，时干按传入的"当日日干"五鼠遁遁出）
        if hour == 23 or hour == 0:
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
        target_date: datetime.date对象、datetime对象，或(year, month, day)元组，
                     或常见日期字符串（支持 "YYYY年MM月DD日 HH时MM分" / "YYYY-MM-DD HH:MM:SS" 等）
        hour: 小时(0-23)
        minute: 分钟(0-59)
        second: 秒(0-59)
        
    Returns:
        dict: 包含年柱、月柱、日柱、时柱的字典，同时包含year, month, day字段
    """
    # 保存原始日期信息
    year = None
    month = None
    day = None
    
    # ==========================================================
    #  兼容：字符串日期（事主birth_date常为"1972年1月8日 8时0分"这类中文格式）
    #  如果字符串能解析，就转成 date 对象，并把字符串里的时分覆盖外部默认的 12/0
    # ==========================================================
    if isinstance(target_date, str):
        parsed = _parse_chinese_date_string(target_date)
        if parsed:
            target_date, h_parsed, m_parsed = parsed
            # 只有在外部没显式传 hour/minute（仍是默认值）时，才用字符串里解析出的时分
            if hour == 12 and minute == 0:
                hour, minute = h_parsed, m_parsed
        else:
            # 字符串解析失败 → 抛一个带说明的 ValueError，让上层except能识别
            raise ValueError(f"无法解析日期字符串: {repr(target_date)}")
    
    # 处理不同类型的target_date
    if isinstance(target_date, tuple) and len(target_date) == 3:
        # 处理(year, month, day)元组
        year, month, day = target_date
        try:
            target_date = date(year, month, day)
        except ValueError as e:
            # 处理无效日期，使用当月最后一天
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            target_date = date(year, month, last_day)
            day = last_day
            logger.warning(f"无效日期 {year}-{month}-{day}，使用当月最后一天 {last_day}")
    elif isinstance(target_date, datetime):
        hour = target_date.hour
        minute = target_date.minute
        second = target_date.second
        year = target_date.year
        month = target_date.month
        day = target_date.day
        target_date = target_date.date()
    elif isinstance(target_date, date):
        # 对于date对象，直接使用
        year = target_date.year
        month = target_date.month
        day = target_date.day
    
    # 计算四柱
    result = calculator.calculate(target_date, hour, minute, second)
    
    # 添加日期字段
    if year is not None:
        result['year'] = year
    if month is not None:
        result['month'] = month
    if day is not None:
        result['day'] = day
    
    # 添加date字段（供神煞检查使用）
    if isinstance(target_date, date):
        result['date'] = target_date
    elif year and month and day:
        try:
            result['date'] = date(year, month, day)
        except ValueError:
            pass
    
    return result


def get_lunar_date(target_date, hour=12, minute=0, second=0):
    """
    获取农历日期（支持 date/datetime/tuple/字符串日期格式，同 calculate_sizhu）
    """
    # 兼容字符串日期
    if isinstance(target_date, str):
        parsed = _parse_chinese_date_string(target_date)
        if parsed:
            target_date, h_parsed, m_parsed = parsed
            if hour == 12 and minute == 0:
                hour, minute = h_parsed, m_parsed
        else:
            raise ValueError(f"无法解析日期字符串: {repr(target_date)}")
    # 兼容元组
    if isinstance(target_date, tuple) and len(target_date) == 3:
        try:
            target_date = date(*target_date)
        except (TypeError, ValueError) as e:
            raise ValueError(f"无效日期元组 {target_date}: {e}")

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
        # 没有sxtwl库时的备用方案 - 使用lunar_python
        try:
            from lunar_python import Solar
            solar = Solar.fromYmd(year, month, day)
            lunar = solar.getLunar()
            
            lunar_year = lunar.getYear()
            lunar_month = lunar.getMonth()
            lunar_day = lunar.getDay()
            is_leap = lunar.getMonth() != lunar.getMonthInChinese()  # 简单判断是否闰月
            
            # 格式化农历月份和日期
            month_names = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
            day_names = [
                "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
            ]
            
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
                'month': f"{month_str}月",
                'day': day_str,
                'month_chinese': f"{month_str}月",
                'day_chinese': day_str,
                '中文': f"{lunar_year}年{month_str}月{day_str}",
                '生肖': zodiac_str,
                '节气': None,
                '验证': True
            }
        except Exception as e:
            logger.warning(f"备用农历计算失败: {e}")
            # 最后的备用方案
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
    
    # 获取年干年支用于计算夫星子星
    year_gan = sizhu.get('year_gan')
    year_zhi = sizhu.get('year_zhi')
    if not year_gan and '年柱' in sizhu:
        year_gan = sizhu['年柱'][0] if len(sizhu['年柱']) > 0 else ''
    if not year_zhi and '年柱' in sizhu:
        year_zhi = sizhu['年柱'][1] if len(sizhu['年柱']) > 1 else ''
    
    fuzi = get_fuzi(year_gan, year_zhi)
    
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
    try:
        from 八字分析工具 import get_nayin, get_zhangsheng
    except ImportError:  # 单文件版不含八字分析工具（飞星功能不需要）
        get_nayin = get_zhangsheng = None
    
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

# ======================================================================
# 【内联模块】玄空飞星引擎（构建自 modules/，勿手改；改算法请改 modules 后重新构建）
# ======================================================================

# -*- coding: utf-8 -*-
"""
玄空飞星引擎（单一数据源 / 纯函数核心）

历史背景：玄空飞星存在两套独立实现——
  1) 评分器 Scorer._calculate_feixing_score：手抄飞星常量并自行排盘，产出
     feixing_score(-20~+20) 用于加权/否决；
  2) 玄空飞星_日课展示.py：独立排盘引擎，用于九宫格窗口展示。
两者靠"保持一致"的注释维系，常量与日星算法手抄两份，极易漂移。
本模块将排盘常量、洛书飞布、冬至/夏至日星、坐山分析、数值评分全部收敛为
纯函数，评分器与玄空窗口统一调用，杜绝双标准。

排盘规则（紫白择日典籍口径，歌诀见《选择宗镜》《沈氏玄空学》）：
  年星：下元1984甲子年七赤入中，逐年逆飞 norm(7-(年-1984)%9)，年以立春为界
  月星：年支定寅月(正月)起星(BASE_MONTH_STAR)，寅月起逐月逆飞
  日星：六中气换元——冬至1白/雨水7赤/谷雨4绿顺飞，夏至9紫/处暑3碧/霜降6白逆飞；
        各以该中气后第一个甲子日起星（日家紫白歌诀"冬至一宫雨水七…"）
  时星：依日段阳顺阴逆。阳遁(冬至后) 仲(子午卯酉)子起1白/季(辰戌丑未)4绿/孟(寅申巳亥)7赤顺飞；
        阴遁(夏至后) 仲9紫/季6白/孟3碧逆飞（"孟日七宫仲一白，季日四绿；孟归三碧季加六，仲在九宫"）
  九宫：洛书序 LUO_SHU_ORDER 顺飞，中宫立极（入中星定后八方永远顺布）
"""

from datetime import datetime, date as _date, timedelta

try:
    import sxtwl
    _HAS_SXTWL = True
except Exception:
    sxtwl = None
    _HAS_SXTWL = False

# ============================================================
#  常量（唯一来源，评分器与窗口共用，禁止再手抄）
# ============================================================
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
MONTH_ZHI_TO_INDEX = {z: i + 1 for i, z in enumerate(DIZHI)}
HOUR_ZHI_TO_INDEX = {z: i + 1 for i, z in enumerate(DIZHI)}

BASE_MONTH_STAR = {
    '子': 8, '午': 8, '卯': 8, '酉': 8,
    '辰': 5, '戌': 5, '丑': 5, '未': 5,
    '寅': 2, '申': 2, '巳': 2, '亥': 2,
}
# 时星起例：阳遁（冬至→夏至，顺飞）仲1/季4/孟7
BASE_HOUR_STAR_YANG = {
    '子': 1, '午': 1, '卯': 1, '酉': 1,
    '辰': 4, '戌': 4, '丑': 4, '未': 4,
    '寅': 7, '申': 7, '巳': 7, '亥': 7,
}
# 时星起例：阴遁（夏至→冬至，逆飞）仲9/季6/孟3
BASE_HOUR_STAR_YIN = {
    '子': 9, '午': 9, '卯': 9, '酉': 9,
    '辰': 6, '戌': 6, '丑': 6, '未': 6,
    '寅': 3, '申': 3, '巳': 3, '亥': 3,
}
# 兼容旧导出名：BASE_HOUR_STAR 即阳遁起例
BASE_HOUR_STAR = dict(BASE_HOUR_STAR_YANG)
# 日家紫白六段换元：sxtwl节气数组自立春起，索引 雨水1/谷雨5/夏至9/处暑13/霜降17/冬至21。
# 每项 (节气索引, 节后第一个甲子日入中星, +1顺飞/-1逆飞)
DAY_JIEQI_SEGMENTS = [(21, 1, +1), (1, 7, +1), (5, 4, +1),
                      (9, 9, -1), (13, 3, -1), (17, 6, -1)]
STAR_NAMES = ['一白', '二黑', '三碧', '四绿', '五黄', '六白', '七赤', '八白', '九紫']
LUO_SHU_ORDER = [4, 9, 2, 3, 5, 7, 8, 1, 6]

# 二十四山（罗盘顺时针）
MOUNTAINS_CW = ['壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
                '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥']
MOUNTAIN_DIRECTION = {
    '壬': '北偏西', '子': '正北',   '癸': '北偏东',
    '丑': '东北偏北', '艮': '东北',  '寅': '东北偏东',
    '甲': '东偏北', '卯': '正东',   '乙': '东偏南',
    '辰': '东南偏东', '巽': '东南',  '巳': '东南偏南',
    '丙': '南偏东', '午': '正南',   '丁': '南偏西',
    '未': '西南偏南', '坤': '西南',  '申': '西南偏西',
    '庚': '西偏南', '酉': '正西',   '辛': '西偏北',
    '戌': '西北偏西', '乾': '西北',  '亥': '西北偏北',
}
MOUNTAIN_LABELS = [f"{m}山 · {MOUNTAIN_DIRECTION[m]}" for m in MOUNTAINS_CW]
# 九宫索引 -> 该宫所辖三山（索引序：0巽/1离/2坤/3震/4中/5兑/6艮/7坎/8乾）
MOUNTAIN_TO_INDEX = {
    '壬': 7, '子': 7, '癸': 7,
    '丑': 6, '艮': 6, '寅': 6,
    '甲': 3, '卯': 3, '乙': 3,
    '辰': 0, '巽': 0, '巳': 0,
    '丙': 1, '午': 1, '丁': 1,
    '未': 2, '坤': 2, '申': 2,
    '庚': 5, '酉': 5, '辛': 5,
    '戌': 8, '乾': 8, '亥': 8,
}
POS_NAMES = ['东南', '南', '西南', '东', '中', '西', '东北', '北', '西北']
# 九宫索引对应八卦宫名（评分器断语用"乾宫"等）
GONG_NAMES = ['巽宫', '离宫', '坤宫', '震宫', '中宫', '兑宫', '艮宫', '坎宫', '乾宫']
# 九宫索引对应卦名（窗口展示用"乾"等）
GUA_NAMES = ['巽', '离', '坤', '震', '中', '兑', '艮', '坎', '乾']

GOOD_STARS = [1, 6, 8, 9]
BAD_STARS = [2, 3, 5, 7]


# ============================================================
#  排盘核心（纯函数）
# ============================================================
def get_grid_by_middle(middle_star):
    """中宫立极，按洛书序顺飞布出九宫星曜。"""
    return [(middle_star + (pos - 5) - 1) % 9 + 1 for pos in LUO_SHU_ORDER]


def get_solstice_info(year, month, day):
    """返回 (距上一冬至/夏至的天数, 是否冬至后阳遁)。
    冬至(index21)后顺飞，夏至(index9)后逆飞。"""
    dt = datetime(year, month, day, 12, 0, 0)
    candidates = []
    if _HAS_SXTWL:
        for y in (year - 1, year, year + 1):
            try:
                jqs_y = sxtwl.getJieQiByYear(y)

                def _jd_to_dt(jd):
                    dd = sxtwl.JD2DD(jd)
                    return datetime(int(dd.Y), int(dd.M), int(dd.D),
                                    int(dd.h), int(dd.m), int(dd.s))

                candidates.append((_jd_to_dt(jqs_y[21].jd), 'winter'))
                candidates.append((_jd_to_dt(jqs_y[9].jd), 'summer'))
            except Exception:
                continue
    candidates.sort(key=lambda x: x[0])
    prev = None
    for c in candidates:
        if c[0] <= dt:
            prev = c
        else:
            break
    if prev is None and candidates:
        prev = candidates[0]
    if prev is None:
        return 0, True
    day_diff = (dt.date() - prev[0].date()).days
    return day_diff, (prev[1] == 'winter')


def _day_gz_index(y, m, d):
    """公历日的六十甲子序号（甲子=0）。sxtwl 不可用时返回 None。"""
    if not _HAS_SXTWL:
        return None
    try:
        g = sxtwl.fromSolar(int(y), int(m), int(d)).getDayGZ()
        return (g.tg * 6 - g.dz * 5) % 60
    except Exception:
        return None


def _day_segment_info(dt):
    """日家紫白六段换元：返回 dt 所属段 (段首甲子日date, 甲子日起星, 顺逆±1)。

    各段以六个中气后的【第一个甲子日】为界（冬至/雨水/谷雨为阳三元：
    1白/7赤/4绿顺飞；夏至/处暑/霜降为阴三元：9紫/3碧/6白逆飞）。
    中气与段首甲子日之间的日子仍归上一元。
    """
    if not _HAS_SXTWL:
        return None
    cands = []
    for y in (dt.year - 1, dt.year, dt.year + 1):
        try:
            jqs = sxtwl.getJieQiByYear(y)
            for jq_idx, base, dr in DAY_JIEQI_SEGMENTS:
                dd = sxtwl.JD2DD(jqs[jq_idx].jd)
                seg_dt = datetime(int(dd.Y), int(dd.M), int(dd.D),
                                  int(dd.h), int(dd.m), int(dd.s))
                gz0 = _day_gz_index(seg_dt.year, seg_dt.month, seg_dt.day)
                if gz0 is None:
                    continue
                off = (-gz0) % 60   # 中气后第一个甲子日距中气天数（0=当日即甲子）
                jiazi_day = (seg_dt + timedelta(days=off)).date()
                cands.append((jiazi_day, base, dr))
        except Exception:
            continue
    cands.sort(key=lambda c: c[0])
    prev = None
    cur_date = dt.date()
    for c in cands:
        if c[0] <= cur_date:
            prev = c
        else:
            break
    return prev


def _year_middle_star(year_val, year_zhi, year_gan=None):
    """年星：下元1984甲子七赤入中，逐年逆飞；年以立春为界。

    优先用年柱干支六十甲子序号推算（天然不受立春年界影响）；
    缺年干时由公历年反推，并以八字年支校正立春前退一年。
    """
    try:
        gan_idx = year_gan
        if isinstance(gan_idx, str):
            gan_idx = TIANGAN.index(gan_idx) if gan_idx in TIANGAN else None
        if gan_idx is None and year_zhi in DIZHI:
            gan_idx = (int(year_val) - 4) % 10
            # 公历元旦至立春前，八字年支属上一年：年干同步退一
            if DIZHI[(int(year_val) - 4) % 12] != year_zhi:
                gan_idx = (gan_idx - 1) % 10
        if gan_idx is not None and year_zhi in DIZHI:
            gz_idx = (int(gan_idx) * 6 - DIZHI.index(year_zhi) * 5) % 60
            return _norm_star(7 - (gz_idx % 9))
    except Exception:
        pass
    return _norm_star(7 - ((int(year_val) - 1984) % 9))


def _norm_star(v):
    return (v - 1) % 9 + 1


def compute_stars(year_val, year_zhi, month_zhi, day_zhi, hour_zhi, date_obj=None,
                  year_gan=None):
    """按四柱地支 + 公历日期排出年/月/日/时四盘。

    返回 {'year'/'month'/'day'/'hour': {'star':中宫星, 'grid':九宫星列表}}。
    评分器四柱地支已知时直接调用本函数，避免重复反推干支。
    year_gan 可传年干（字或0..9序号），用于精确定位干支年（立春年界）。
    """
    # 年星：七赤起下元甲子，逐年逆飞（年以立春为界）
    year_star = _year_middle_star(year_val, year_zhi, year_gan)
    # 月星：年支定寅月起星，寅月起逐月逆飞
    if month_zhi in DIZHI:
        month_seq = (DIZHI.index(month_zhi) - 2) % 12 + 1   # 寅月=1
        base_m = BASE_MONTH_STAR.get(year_zhi, 5)
        month_star = _norm_star(base_m - (month_seq - 1))
    else:
        month_star = 5
    # 日星：六中气换元，各以节后第一个甲子日起星，阳三元顺飞/阴三元逆飞
    day_star = 5
    hour_yang = True   # 时星随日段分阳顺阴逆
    if date_obj is not None:
        try:
            seg = _day_segment_info(datetime(date_obj.year, date_obj.month, date_obj.day, 12))
        except Exception:
            seg = None
        if seg is not None:
            jiazi_day, d_base, d_dr = seg
            n_days = (date_obj.date() - jiazi_day).days
            day_star = _norm_star(d_base + d_dr * n_days)
            hour_yang = (d_dr > 0)
        else:
            # sxtwl 不可用时退回旧的冬至顺/夏至逆（节气当日起算，近似）
            day_diff, is_winter = get_solstice_info(date_obj.year, date_obj.month, date_obj.day)
            if is_winter:
                day_star = (day_diff % 9) + 1
            else:
                day_star = 9 - (day_diff % 9)
                if day_star == 0:
                    day_star = 9
            hour_yang = is_winter
    # 时星：阳遁仲1/季4/孟7顺飞；阴遁仲9/季6/孟3逆飞
    hour_index = HOUR_ZHI_TO_INDEX.get(hour_zhi, 1)
    if hour_yang:
        base_h = BASE_HOUR_STAR_YANG.get(day_zhi, 1)
        hour_star = _norm_star(base_h + (hour_index - 1))
    else:
        base_h = BASE_HOUR_STAR_YIN.get(day_zhi, 9)
        hour_star = _norm_star(base_h - (hour_index - 1))
    return {
        'year': {'star': year_star, 'grid': get_grid_by_middle(year_star)},
        'month': {'star': month_star, 'grid': get_grid_by_middle(month_star)},
        'day': {'star': day_star, 'grid': get_grid_by_middle(day_star)},
        'hour': {'star': hour_star, 'grid': get_grid_by_middle(hour_star)},
    }


def _extract_zhi(sizhu):
    """从 sizhu(dict) 提取年/月/日/时支与公历年份/日期，兼容四柱键与 *_zhi 键。"""
    def _zhi_of(pillar_key, zhi_key):
        z = sizhu.get(zhi_key)
        if z:
            return z
        p = sizhu.get(pillar_key, '')
        return p[1] if isinstance(p, str) and len(p) >= 2 else ''

    year_zhi = _zhi_of('年柱', 'year_zhi')
    month_zhi = _zhi_of('月柱', 'month_zhi')
    day_zhi = _zhi_of('日柱', 'day_zhi')
    hour_zhi = _zhi_of('时柱', 'hour_zhi')
    year_gan = sizhu.get('year_gan')
    if not year_gan:
        p = sizhu.get('年柱', '')
        year_gan = p[0] if isinstance(p, str) and len(p) >= 2 else None
    year_val = sizhu.get('year')
    date_obj = sizhu.get('date')
    if date_obj is not None and not isinstance(date_obj, datetime):
        try:
            date_obj = datetime(date_obj.year, date_obj.month, date_obj.day)
        except Exception:
            date_obj = None
    if not year_val and date_obj is not None:
        year_val = date_obj.year
    return year_zhi, month_zhi, day_zhi, hour_zhi, year_val, date_obj, year_gan


def get_xuan_kong_data(year, month, day, hour, minute=0, second=0):
    """窗口接口：由公历日期反推四柱后排盘，附带农历/节气信息。"""
    conv = get_lunar_converter(strict_mode=False)  # 已内联于本单文件
    info = conv.solar_to_lunar_with_check(year, month, day, hour, minute, second)
    ec = info['eight_char']
    year_zhi = ec['year'][1]
    month_zhi = ec['month'][1]
    day_zhi = ec['day'][1]
    hour_zhi = ec['hour'][1]
    grids = compute_stars(year, year_zhi, month_zhi, day_zhi, hour_zhi,
                          datetime(year, month, day), year_gan=ec['year'][0])
    return {
        'year': grids['year'],
        'month': grids['month'],
        'day': grids['day'],
        'hour': grids['hour'],
        'sizhu': {'year': ec['year'], 'month': ec['month'],
                  'day': ec['day'], 'hour': ec['hour']},
        'summary': f"年{STAR_NAMES[grids['year']['star'] - 1]} "
                   f"月{STAR_NAMES[grids['month']['star'] - 1]} "
                   f"日{STAR_NAMES[grids['day']['star'] - 1]} "
                   f"时{STAR_NAMES[grids['hour']['star'] - 1]}",
        'lunar_date': info['lunar_date_str'],
        'jie_qi': info['jie_qi'],
    }


# ============================================================
#  坐山分析（窗口展示用）
# ============================================================
def get_mountain_label(mountain, offset_degree):
    if not mountain or mountain not in MOUNTAINS_CW:
        return mountain or "未知"
    if abs(offset_degree) < 3.0:
        return f"{mountain}山（正向）"
    idx = MOUNTAINS_CW.index(mountain)
    if offset_degree > 0:
        target = MOUNTAINS_CW[(idx + 1) % 24]
    else:
        target = MOUNTAINS_CW[(idx - 1) % 24]
    return f"{mountain}山兼{target}"


def _judge_mountain_stars(star_list, mountain, pos_name, is_partial):
    """坐山方年/月/日/时四星的统一打分与判级（唯一数据源，2026-09-12）。

    score_feixing（评分器/主程序/吉日搜索）与窗口文字结论均须调用本函数，
    杜绝"盘面正确、但文字另按全盘他宫判大凶"的双标准。

    Returns:
        fx_score(-20~+20) / fx_level / fx_comment / details /
        good_count / bad_count / has_5 / has_2 / combos(坐山凶格名list)
    """
    good_count = sum(1 for s in star_list if s in GOOD_STARS)
    bad_count = sum(1 for s in star_list if s in BAD_STARS)
    has_5 = any(s == 5 for s in star_list)
    has_2 = any(s == 2 for s in star_list)

    er_wu = (2 in star_list and 5 in star_list)
    san_qi = (3 in star_list and 7 in star_list)
    liu_qi = (6 in star_list and 7 in star_list)

    fx_score = 0
    details = []
    stars = {'年': star_list[0], '月': star_list[1],
             '日': star_list[2], '时': star_list[3]}

    if has_5 or has_2:
        fx_score -= 15
        _bad = [f"{_p}{STAR_NAMES[_s - 1]}" for _p, _s in stars.items() if _s in (2, 5)]
        details.append(f"{'、'.join(_bad)}到{GONG_NAMES[MOUNTAIN_TO_INDEX[mountain]]}（坐山，-15）")

    if bad_count >= 3:
        fx_score -= 10
        details.append(f"凶星{bad_count}颗汇聚（-10）")

    if good_count >= 3:
        fx_score += 15
        details.append(f"吉星{good_count}颗汇聚（+15）")
    elif good_count >= 2:
        fx_score += 8
        details.append(f"吉星{good_count}颗汇聚（+8）")

    if er_wu:
        fx_score -= 5
        details.append("二五叠临（额外-5，合计-20）")
    if san_qi:
        fx_score -= 15
        details.append("三七叠临（-15）")
    if liu_qi:
        fx_score -= 15
        details.append("六七交剑（-15）")

    if is_partial:
        fx_score -= 10
        details.append("兼向需替卦复核（-10）")

    _fx_raw = fx_score
    fx_score = max(-20, min(20, fx_score))
    if fx_score != _fx_raw:
        if _fx_raw < -20:
            details.append(f"明细合计{_fx_raw:+d}，低于下限-20，按-20计")
        else:
            details.append(f"明细合计{_fx_raw:+d}，高于上限+20，按+20计")

    # 定级（2026-09-12 用户拍板：以 fx_score 终判，坐山凶格硬性封顶）：
    #   五黄/二五 → 大凶；二黑且凶星汇聚 → 凶；
    #   坐山六七交剑/三七叠临 → 等级不得高于"平"（再高的吉星也不许判吉）；
    #   无坐山凶格 → 按分数：≥15大吉、≥5吉、[-5,5)平、<-5凶。
    combo_desp = None
    if liu_qi:
        combo_desp = ('六七交剑', '六白七赤同宫，主争斗、刑伤官非')
    elif san_qi:
        combo_desp = ('三七叠临', '三碧七赤同宫，主官非、盗贼')

    if has_5:
        fx_level = "大凶"
        fx_comment = f"坐{mountain}（{pos_name}方）五黄到山，切忌动土修造"
    elif er_wu:
        fx_level = "大凶"
        fx_comment = f"坐{mountain}（{pos_name}方）二五叠临，主疾病灾祸"
    elif has_2 and bad_count >= 2:
        fx_level = "凶"
        fx_comment = f"坐{mountain}（{pos_name}方）二黑加临且凶星汇聚，防疾病"
    else:
        if fx_score >= 15:
            fx_level = "大吉"
        elif fx_score >= 5:
            fx_level = "吉"
        elif fx_score >= -5:
            fx_level = "平"
        else:
            fx_level = "凶"
        # 坐山凶格封顶：交剑/叠临在山，吉星再多也只作"平"论
        if combo_desp is not None and fx_level in ("大吉", "吉"):
            fx_level = "平"
        if combo_desp is not None:
            if fx_level == "平":
                fx_comment = (f"坐{mountain}（{pos_name}方）{combo_desp[0]}，{combo_desp[1]}；"
                              f"虽有吉星会合，凶格在山仅作平论，慎用")
            else:
                fx_comment = (f"坐{mountain}（{pos_name}方）{combo_desp[0]}，{combo_desp[1]}，"
                              f"又逢凶象，不取")
        elif fx_level == "大吉":
            fx_comment = f"坐{mountain}（{pos_name}方）吉星高照，用之大吉"
        elif fx_level == "吉":
            fx_comment = f"坐{mountain}（{pos_name}方）吉星汇聚，可用"
        elif fx_level == "凶":
            fx_comment = f"坐{mountain}（{pos_name}方）凶星较众，不利"
        else:
            fx_comment = f"坐{mountain}（{pos_name}方）吉凶参半，需结合日课综合判断"

    combos = [_n for _n, _ok in
              (('二五叠临', er_wu), ('三七叠临', san_qi), ('六七交剑', liu_qi))
              if _ok]
    return {
        'fx_score': fx_score, 'fx_level': fx_level, 'fx_comment': fx_comment,
        'details': details, 'good_count': good_count, 'bad_count': bad_count,
        'has_5': has_5, 'has_2': has_2, 'combos': combos,
    }


def analyze_mountain(selected_mountain, data, offset_degree=0.0):
    if not selected_mountain or selected_mountain not in MOUNTAIN_TO_INDEX:
        return None
    idx = MOUNTAIN_TO_INDEX[selected_mountain]
    pos_name = POS_NAMES[idx]
    is_partial = abs(offset_degree) >= 3.0
    stars = {
        '年': data['year']['grid'][idx],
        '月': data['month']['grid'][idx],
        '日': data['day']['grid'][idx],
        '时': data['hour']['grid'][idx],
    }
    star_list = list(stars.values())

    # 判级/打分统一走 _judge_mountain_stars（与 score_feixing 同源；
    # 兼向只在分数上按替卦口径-10，不再把等级改写成"慎用（兼向）"）
    _judge = _judge_mountain_stars(star_list, selected_mountain, pos_name, is_partial)
    level = _judge['fx_level']
    good_count = _judge['good_count']
    bad_count = _judge['bad_count']
    has_5 = _judge['has_5']
    has_2 = _judge['has_2']
    combo_warnings = list(_judge['combos'])

    mountain_label = get_mountain_label(selected_mountain, offset_degree)
    suggestion = _judge['fx_comment'] + "。"
    if is_partial:
        suggestion += f" 偏移{offset_degree:.1f}°，已属兼向，分数按替卦口径计，实际用事仍建议替卦（起星）重排。"
    else:
        suggestion += " 此为正向，可用本宫星断之。"
    if combo_warnings:
        suggestion += " 注意（坐山方）：" + "；".join(combo_warnings)

    return {
        'mountain_label': mountain_label,
        'mountain': selected_mountain,
        'position': pos_name,
        'offset': offset_degree,
        'is_partial': is_partial,
        'stars': stars,
        'level': level,
        'suggestion': suggestion,
        'good_count': good_count,
        'bad_count': bad_count,
        'has_5': has_5,
        'has_2': has_2,
        'combo_warnings': combo_warnings,
        'fx_score': _judge['fx_score'],
        'fx_details': _judge['details'],
    }


def generate_xuankong_comment(data, selected_mountain=None, offset_degree=0.0):
    """生成窗口文字结论。口径（2026-09-12 修正双标准）：

    日课吉凶**只以坐山方年/月/日/时四星为纲**，判级/打分与 score_feixing
    完全同源；他宫（非坐山八方）的二黑五黄、凶星汇聚与凶格只作"修方宜避"
    的方位提示，不再把整个日课判成"飞星大凶"。旧版按全盘 36 格吉凶计数
    （九星每盘恒 4 吉 4 凶 1 平，全盘恒为 16:16）再因他宫凶格扣分，导致
    坐山聚 3 吉也几乎必判大凶，与排盘及主程序评分矛盾。
    """
    disks = {'年': data['year'], '月': data['month'], '日': data['day'], '时': data['hour']}
    mountain_idx = (MOUNTAIN_TO_INDEX[selected_mountain]
                    if selected_mountain and selected_mountain in MOUNTAIN_TO_INDEX else None)

    # —— 各方吉/凶星计数 ——
    pos_good_count = [0] * 9
    pos_bad_count = [0] * 9
    for disk in disks.values():
        for idx, val in enumerate(disk['grid']):
            if val in GOOD_STARS:
                pos_good_count[idx] += 1
            if val in BAD_STARS:
                pos_bad_count[idx] += 1

    good_points = []
    mountain_warnings = []     # 坐山宫的警示（参与日课判级）
    other_warnings = []        # 他宫提示（只关乎修方，不否决日课）
    for idx, count in enumerate(pos_good_count):
        tag = "★坐山 " if idx == mountain_idx else ""
        if count >= 3:
            good_points.append(f"{tag}「{POS_NAMES[idx]}」方{count}颗吉星汇聚，大吉")
        elif count == 2:
            good_points.append(f"{tag}「{POS_NAMES[idx]}」方{count}颗吉星，可用")
    good_points.sort(key=lambda t: 0 if t.startswith("★") else 1)  # 坐山项置顶
    for idx, count in enumerate(pos_bad_count):
        is_ms = (idx == mountain_idx)
        if count >= 3:
            msg = (f"「{POS_NAMES[idx]}」方{count}颗凶星汇聚，大凶勿用" if is_ms else
                   f"「{POS_NAMES[idx]}」方{count}颗凶星汇聚，修方宜避")
        elif count == 2:
            msg = (f"「{POS_NAMES[idx]}」方{count}颗凶星，坐山忌用" if is_ms else
                   f"「{POS_NAMES[idx]}」方{count}颗凶星，修方宜避")
        else:
            continue
        (mountain_warnings if is_ms else other_warnings).append(msg)

    # —— 单星二黑/五黄临方 ——
    for disk_name, disk in disks.items():
        for idx, val in enumerate(disk['grid']):
            pos = POS_NAMES[idx]
            if val == 5:
                msg = f"{disk_name}盘五黄在「{pos}」方，忌动土修造"
            elif val == 2:
                msg = f"{disk_name}盘二黑在「{pos}」方，宜静防病"
            else:
                continue
            if idx == mountain_idx:
                mountain_warnings.append(msg + "（坐山）")
            else:
                other_warnings.append(msg)

    # —— 凶格（坐山/他宫分组）——
    mountain_combos = []
    other_combos = []
    for idx in range(9):
        s4 = [disk['grid'][idx] for disk in disks.values()]
        names = []
        if 2 in s4 and 5 in s4:
            names.append("二五叠临，主疾病灾祸")
        if 3 in s4 and 7 in s4:
            names.append("三七叠临，主官非盗贼")
        if 6 in s4 and 7 in s4:
            names.append("六七交剑，主争斗")
        for nm in names:
            item = f"「{POS_NAMES[idx]}」{nm}"
            if idx == mountain_idx:
                mountain_combos.append(item)
            else:
                other_combos.append(item)

    # —— 坐山判级（analyze_mountain 内与 score_feixing 同源）——
    mountain_analysis = None
    fx_score = fx_level = None
    if mountain_idx is not None:
        mountain_analysis = analyze_mountain(selected_mountain, data, offset_degree)
        fx_score = mountain_analysis['fx_score']
        fx_level = mountain_analysis['level']

    if mountain_analysis is not None:
        ma = mountain_analysis
        if fx_level == "大凶":
            summary = f"飞星大凶，建议另择他日：{ma['suggestion'].split('。')[0]}"
        elif fx_level == "凶":
            # 等级"凶"+断语"不取"时，综合文案语气必须一致（2026-09-13 用户纠正：
            # 旧文案"飞星偏弱，慎用"与"凶/不取"矛盾），"慎用"只保留给封顶级"平"
            summary = f"飞星凶，不取，宜另择他日：{ma['suggestion'].split('。')[0]}"
        elif fx_level == "大吉":
            if other_combos:
                summary = (f"坐山吉星汇聚，飞星大吉，可用；他宫另有 {len(other_combos)} 处凶格"
                           f"（修方避其方即可，不碍坐山）")
            else:
                summary = "坐山吉星汇聚，飞星大吉，可为重要日课备选"
        elif fx_level == "吉":
            summary = "飞星偏吉，坐山可用"
            if other_combos:
                summary += f"；他宫另有 {len(other_combos)} 处凶格，修方避之即可"
        else:
            if mountain_combos:
                summary = (f"飞星平：坐山方{'、'.join(mountain_combos)}，"
                           f"凶格在山，仅作平论，宜慎用")
            else:
                summary = "飞星平：坐山吉凶参半，需结合日课综合判断"
            if other_combos:
                summary += "；他宫另有凶格，修方避之"
        if ma['is_partial']:
            summary += "（兼向，分数已按替卦口径计）"
    else:
        summary = ("未选坐山：日课吉凶以坐山方年/月/日/时四盘为准，请先选择山向；"
                   "下列为全盘各方飞星提示")

    return {
        'summary': summary,
        'warnings': mountain_warnings + other_warnings,   # 兼容旧键
        'mountain_warnings': mountain_warnings,
        'other_warnings': other_warnings,
        'good_points': good_points,
        'bad_combos': mountain_combos + other_combos,      # 兼容旧键
        'mountain_combos': mountain_combos,
        'other_combos': other_combos,
        'score': fx_score if fx_score is not None else 0,
        'fx_score': fx_score,
        'fx_level': fx_level,
        'mountain_analysis': mountain_analysis,
    }


# ============================================================
#  数值评分（评分器加权/否决用）——规则与原 Scorer._calculate_feixing_score 逐行一致
# ============================================================
def score_feixing(sizhu, full_shan_xiang):
    """计算坐山方年/月/日/时四盘飞星的数值评分。

    Returns:
        dict: {feixing_score(-20~+20), feixing_level, feixing_details,
               feixing_comment, feixing_stars, feixing_star_count}
        None: 坐山无法识别 / 数据不足时跳过
    """
    try:
        year_zhi, month_zhi, day_zhi, hour_zhi, year_val, date_obj, year_gan = _extract_zhi(sizhu)
        if not all([year_zhi, month_zhi, day_zhi, hour_zhi]):
            return None
        if not year_val:
            return None

        # 提取坐山（按罗盘顺时针顺序取首个匹配，与原实现一致）
        mountain = None
        if full_shan_xiang:
            for m in MOUNTAINS_CW:
                if str(full_shan_xiang).startswith(m):
                    mountain = m
                    break
        if not mountain or mountain not in MOUNTAIN_TO_INDEX:
            return None

        is_partial = '兼' in (full_shan_xiang or '')

        grids = compute_stars(int(year_val), year_zhi, month_zhi, day_zhi,
                              hour_zhi, date_obj, year_gan=year_gan)
        year_grid = grids['year']['grid']
        month_grid = grids['month']['grid']
        day_grid = grids['day']['grid']
        hour_grid = grids['hour']['grid']

        idx = MOUNTAIN_TO_INDEX[mountain]
        pos_name = POS_NAMES[idx]
        star_list = [year_grid[idx], month_grid[idx], day_grid[idx], hour_grid[idx]]

        # 打分/判级统一走 _judge_mountain_stars（与窗口文字结论同源）
        _judge = _judge_mountain_stars(star_list, mountain, pos_name, is_partial)
        fx_score = _judge['fx_score']
        fx_level = _judge['fx_level']
        fx_comment = _judge['fx_comment']
        details = _judge['details']
        good_count = _judge['good_count']
        bad_count = _judge['bad_count']
        has_5 = _judge['has_5']
        has_2 = _judge['has_2']
        _combos = _judge['combos']

        stars_str = (f"年{STAR_NAMES[year_grid[idx] - 1]}"
                     f"月{STAR_NAMES[month_grid[idx] - 1]}"
                     f"日{STAR_NAMES[day_grid[idx] - 1]}"
                     f"时{STAR_NAMES[hour_grid[idx] - 1]}")

        # 结构化字段（2026-09-12 增，供吉日搜索等批量过滤；既有消费者不受影响）
        return {
            'feixing_score': fx_score,
            'feixing_level': fx_level,
            'feixing_details': details,
            'feixing_comment': fx_comment,
            'feixing_stars': stars_str,
            'feixing_star_count': f"吉星{good_count}颗，凶星{bad_count}颗",
            'stars_list': star_list,        # 年/月/日/时四盘到坐山星（1..9）
            'good_count': good_count,
            'bad_count': bad_count,
            'has_5': has_5,
            'has_2': has_2,
            'combos': _combos,              # 坐山方凶格名
            'mountain': mountain,
            'position': pos_name,
            'is_partial': is_partial,
        }
    except Exception as e:
        print(f"[飞星评分] 计算出错: {e}")
        return None


# ============================================================
#  GUI 界面 (手机自适应)
# ============================================================
STAR_TYPES = [0, '吉','凶','凶','平','凶','吉','凶','吉','吉']
COLORS = {
    '吉': '#3c6e3c', '凶': '#6e3c3c', '平': '#3a4558',
    '吉_text': '#8bc34a', '凶_text': '#e57373', '平_text': '#7fc1b0',
    'star_num': '#f5c542'
}

class XuanKongApp:
    def __init__(self, root, preset=None):
        self.root = root
        self.root.title("玄空飞星 · 日课模块 (二十四山兼向)")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#0b0e14')
        self.root.bind('<Escape>', lambda e: self.exit_fullscreen())
        self._preset = preset or {}   # 由择日结果/搜索联动带入

        # 屏幕尺寸
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.base_font_size = max(10, int(self.screen_w / 45))

        # 主滚动容器
        self.main_canvas = tk.Canvas(root, bg='#0b0e14', highlightthickness=0)
        self.v_scroll = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.h_scroll = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.main_canvas.xview)
        self.main_canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.inner_frame = tk.Frame(self.main_canvas, bg='#0b0e14')
        self.canvas_window = self.main_canvas.create_window((0,0), window=self.inner_frame, anchor=tk.NW)
        self.inner_frame.bind('<Configure>', self.on_frame_configure)
        self.main_canvas.bind('<Configure>', self.on_canvas_configure)

        # 滚轮绑定（手机可能无效，但有滚动条）
        self.main_canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.main_canvas.bind('<Button-4>', self.on_mousewheel)
        self.main_canvas.bind('<Button-5>', self.on_mousewheel)

        # 构建UI
        self.build_ui()
        self.current_offset = 0.0
        self.current_data = None
        self._apply_preset(self._preset)
        self.update_face_and_offset()
        self.update_grids()

    def exit_fullscreen(self):
        self.root.attributes('-fullscreen', False)
        self.root.destroy()

    def on_frame_configure(self, event):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox('all'))

    def on_canvas_configure(self, event):
        self.main_canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        if event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            self.main_canvas.yview_scroll(1, "units")
        elif event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            self.main_canvas.yview_scroll(-1, "units")

    def build_ui(self):
        top = tk.Frame(self.inner_frame, bg='#141a24', pady=10)
        top.pack(fill='x', padx=10, pady=10)

        # 标题
        tk.Label(top, text="📅 选择日期时间", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', self.base_font_size+2, 'bold')).pack(anchor='w', padx=5, pady=2)

        # 年、月、日
        row_date = tk.Frame(top, bg='#141a24')
        row_date.pack(fill='x', pady=2)
        tk.Label(row_date, text="年", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', self.base_font_size-1)).pack(side='left', padx=(5,0))
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(row_date, textvariable=self.year_var,
                                  values=list(range(1900, 2101)), width=6,
                                  state='readonly', font=('微软雅黑', self.base_font_size-2))
        year_combo.pack(side='left', padx=2)

        tk.Label(row_date, text="月", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', self.base_font_size-1)).pack(side='left', padx=(5,0))
        self.month_var = tk.StringVar(value=str(datetime.now().month))
        month_combo = ttk.Combobox(row_date, textvariable=self.month_var,
                                   values=list(range(1, 13)), width=3,
                                   state='readonly', font=('微软雅黑', self.base_font_size-2))
        month_combo.pack(side='left', padx=2)

        tk.Label(row_date, text="日", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', self.base_font_size-1)).pack(side='left', padx=(5,0))
        self.day_var = tk.StringVar(value=str(datetime.now().day))
        day_combo = ttk.Combobox(row_date, textvariable=self.day_var,
                                 values=list(range(1, 32)), width=3,
                                 state='readonly', font=('微软雅黑', self.base_font_size-2))
        day_combo.pack(side='left', padx=2)

        # 时、分
        row_time = tk.Frame(top, bg='#141a24')
        row_time.pack(fill='x', pady=2)
        tk.Label(row_time, text="时", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', self.base_font_size-1)).pack(side='left', padx=(5,0))
        self.hour_var = tk.StringVar(value=str(datetime.now().hour))
        hour_combo = ttk.Combobox(row_time, textvariable=self.hour_var,
                                  values=list(range(0, 24)), width=3,
                                  state='readonly', font=('微软雅黑', self.base_font_size-2))
        hour_combo.pack(side='left', padx=2)

        tk.Label(row_time, text="分", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', self.base_font_size-1)).pack(side='left', padx=(5,0))
        self.minute_var = tk.StringVar(value=str(datetime.now().minute))
        minute_combo = ttk.Combobox(row_time, textvariable=self.minute_var,
                                    values=list(range(0, 60)), width=3,
                                    state='readonly', font=('微软雅黑', self.base_font_size-2))
        minute_combo.pack(side='left', padx=2)

        # 坐山、朝向
        row_shan = tk.Frame(top, bg='#141a24')
        row_shan.pack(fill='x', pady=2)
        tk.Label(row_shan, text="坐山：", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', self.base_font_size-1)).pack(side='left')
        self.mountain_var = tk.StringVar()
        self.mountain_combo = ttk.Combobox(row_shan, textvariable=self.mountain_var,
                                           values=MOUNTAINS_CW, width=4,
                                           state='readonly', font=('微软雅黑', self.base_font_size-2))
        self.mountain_combo.pack(side='left', padx=2)
        self.mountain_combo.set('子')

        tk.Label(row_shan, text="朝向：", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', self.base_font_size-1)).pack(side='left', padx=(5,0))
        self.face_label = tk.Label(row_shan, text="午", fg='#d4af70', bg='#141a24',
                                   font=('微软雅黑', self.base_font_size, 'bold'))
        self.face_label.pack(side='left', padx=2)

        # 兼向、偏移
        row_jian = tk.Frame(top, bg='#141a24')
        row_jian.pack(fill='x', pady=2)
        tk.Label(row_jian, text="兼向：", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', self.base_font_size-1)).pack(side='left')
        self.jian_var = tk.StringVar()
        self.jian_combo = ttk.Combobox(row_jian, textvariable=self.jian_var,
                                       values=[], width=6,
                                       state='readonly', font=('微软雅黑', self.base_font_size-2))
        self.jian_combo.pack(side='left', padx=2)

        tk.Label(row_jian, text="偏移：", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', self.base_font_size-1)).pack(side='left', padx=(5,0))
        self.offset_display = tk.Label(row_jian, text="0.0°", fg='#d4af70', bg='#141a24',
                                       font=('微软雅黑', self.base_font_size, 'bold'))
        self.offset_display.pack(side='left', padx=2)

        # 山向完整名称
        self.mountain_label_var = tk.StringVar(value="")
        self.mountain_label_display = tk.Label(top, textvariable=self.mountain_label_var,
                                               fg='#d4af70', bg='#141a24',
                                               font=('微软雅黑', self.base_font_size, 'bold'))
        self.mountain_label_display.pack(fill='x', pady=2)

        # 按钮
        btn_frame = tk.Frame(top, bg='#141a24')
        btn_frame.pack(fill='x', pady=5)
        tk.Button(btn_frame, text="📄 查看报告", command=self.show_report,
                  bg='#28a745', fg='white', font=('微软雅黑', self.base_font_size-1), padx=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="刷新飞星", command=self.update_grids,
                  bg='#d4af70', fg='#0b0e14', font=('微软雅黑', self.base_font_size-1), padx=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="🔍 吉日搜索", command=self._open_feixing_search,
                  bg='#3a6ea5', fg='#ffffff', font=('微软雅黑', self.base_font_size-1), padx=5).pack(side='left', padx=5)

        # 绑定事件
        self.mountain_combo.bind('<<ComboboxSelected>>', self.update_face_and_offset)
        self.jian_combo.bind('<<ComboboxSelected>>', self.update_face_and_offset)

        # 信息标签
        self.info_label = tk.Label(self.inner_frame, text="", fg='#d4af70', bg='#0b0e14',
                                   font=('微软雅黑', self.base_font_size))
        self.info_label.pack(pady=5)

        # 九宫格容器
        self.grid_frame = tk.Frame(self.inner_frame, bg='#0b0e14')
        self.grid_frame.pack(fill='both', padx=10, pady=5)
        self.cells = []
        for i in range(4):
            f = tk.Frame(self.grid_frame, bg='#141a24', relief='ridge', bd=2)
            row, col = divmod(i, 2)
            f.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            self.cells.append(f)
        self.grid_frame.grid_rowconfigure(0, weight=1)
        self.grid_frame.grid_rowconfigure(1, weight=1)
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)

        # 摘要
        self.summary_label = tk.Label(self.inner_frame, text="", fg='#6f7d98', bg='#0b0e14',
                                      font=('微软雅黑', self.base_font_size-1))
        self.summary_label.pack(pady=5)

        # 评语框
        self.comment_text = scrolledtext.ScrolledText(self.inner_frame, wrap=tk.WORD,
                                                      fg='#e8edf5', bg='#1a222e',
                                                      font=('微软雅黑', self.base_font_size), relief='flat', height=10)
        self.comment_text.pack(fill='both', expand=True, padx=10, pady=5)

    def _apply_preset(self, preset):
        """带入外部（择日结果/搜索联动）日期、坐山、兼向；无效字段静默忽略。"""
        if not preset:
            return
        try:
            if preset.get('year'):
                y = int(preset['year'])
                if 1900 <= y <= 2100:
                    self.year_var.set(str(y))
            if preset.get('month'):
                m = int(preset['month'])
                if 1 <= m <= 12:
                    self.month_var.set(str(m))
            if preset.get('day'):
                d = int(preset['day'])
                if 1 <= d <= 31:
                    self.day_var.set(str(d))
            if preset.get('hour') is not None:
                h = int(preset['hour'])
                if 0 <= h <= 23:
                    self.hour_var.set(str(h))
            if preset.get('minute') is not None:
                mi = int(preset['minute'])
                if 0 <= mi <= 59:
                    self.minute_var.set(str(mi))
            m = preset.get('mountain')
            if m in MOUNTAINS_CW:
                self.mountain_var.set(m)
                self.update_face_and_offset()   # 重建兼向下拉选项
            jx = preset.get('jianxiang')
            if jx and jx in list(self.jian_combo['values']):
                self.jian_var.set(jx)
        except Exception:
            pass

    def update_face_and_offset(self, event=None):
        mountain = self.mountain_var.get().strip()
        if not mountain or mountain not in MOUNTAINS_CW:
            self.face_label.config(text="")
            self.jian_combo.config(values=[])
            self.jian_var.set("")
            self.offset_display.config(text="")
            self.mountain_label_var.set("")
            self.current_offset = 0.0
            return

        idx = MOUNTAINS_CW.index(mountain)
        face_idx = (idx + 12) % 24
        face = MOUNTAINS_CW[face_idx]
        self.face_label.config(text=face)

        prev_mountain = MOUNTAINS_CW[(idx - 1) % 24]
        next_mountain = MOUNTAINS_CW[(idx + 1) % 24]
        jian_options = ['正向', f'兼{prev_mountain}', f'兼{next_mountain}']
        self.jian_combo.config(values=jian_options)
        if self.jian_var.get() not in jian_options:
            self.jian_var.set('正向')

        jian_selected = self.jian_var.get()
        if jian_selected == '正向':
            offset = 0.0
            jian_name = "正向"
        else:
            jian_target = jian_selected[1:]
            if jian_target == prev_mountain:
                offset = -3.5
                jian_name = f"兼{prev_mountain}"
            elif jian_target == next_mountain:
                offset = 3.5
                jian_name = f"兼{next_mountain}"
            else:
                offset = 0.0
                jian_name = "正向"

        self.current_offset = offset
        self.offset_display.config(text=f"{offset:.1f}°")
        if offset == 0:
            full_name = f"{mountain}山{face}向（正向）"
        else:
            full_name = f"{mountain}山{face}向，{jian_name}"
        self.mountain_label_var.set(full_name)

    def update_grids(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())

            if month < 1 or month > 12 or day < 1 or day > calendar.monthrange(year, month)[1]:
                messagebox.showerror("日期错误", "无效日期")
                return

            data = get_xuan_kong_data(year, month, day, hour, minute)
            self.current_data = data
            sizhu = data['sizhu']
            self.info_label.config(text=f"{data['lunar_date']}  {sizhu['year']}年 {sizhu['month']}月 {sizhu['day']}日 {sizhu['hour']}时")

            titles = ['年飞星', '月飞星', '日飞星', '时飞星']
            keys = ['year','month','day','hour']
            sub_texts = [f"{sizhu['year']}年", f"{sizhu['month']}月", f"{sizhu['day']}日", f"{sizhu['hour']}时"]

            for idx, frame in enumerate(self.cells):
                for widget in frame.winfo_children():
                    widget.destroy()

                key = keys[idx]
                item = data[key]
                star = item['star']
                grid = item['grid']

                tk.Label(frame, text=f"{titles[idx]}  {sub_texts[idx]}", fg='#b0c0d8',
                         bg='#10161e', font=('微软雅黑', self.base_font_size, 'bold')).pack(pady=(5,0))
                tk.Label(frame, text=f"入中：{STAR_NAMES[star-1]}", fg='#d4af70',
                         bg='#10161e', font=('微软雅黑', self.base_font_size-1)).pack()

                inner = tk.Frame(frame, bg='#0b1018', pady=5)
                inner.pack(expand=True, fill='both', padx=5, pady=5)

                for i in range(9):
                    val = grid[i]
                    typ = STAR_TYPES[val]
                    bg_color = COLORS[typ]
                    txt_color = COLORS.get(typ+'_text', '#ffffff')
                    cell = tk.Frame(inner, bg=bg_color, relief='flat', bd=1)
                    cell.grid(row=i//3, column=i%3, padx=1, pady=1, sticky='nsew')
                    if i == 4:
                        cell.config(bd=2, relief='solid', highlightbackground='#d4af70')

                    cell.grid_columnconfigure(0, weight=1)
                    cell.grid_columnconfigure(1, weight=1)
                    cell.grid_columnconfigure(2, weight=1)
                    cell.grid_rowconfigure(0, weight=1)

                    # 方位（左）—— 卦名·方位，与桌面及手机一键部署版同口径；中宫显"中宫"
                    # 2026-09-13 应要求：九宫格内三列文字整体调小一档（-3/-2/+1）
                    _gua = GUA_NAMES[i]
                    _pos_text = f"{_gua}·{POS_NAMES[i]}" if _gua != '中' else "中宫"
                    tk.Label(cell, text=_pos_text, fg='#6f7d98', bg=bg_color,
                             font=('微软雅黑', self.base_font_size-3)).grid(row=0, column=0, sticky='nsew', padx=1)
                    tk.Label(cell, text=STAR_NAMES[val-1], fg=txt_color, bg=bg_color,
                             font=('微软雅黑', self.base_font_size-2, 'bold')).grid(row=0, column=1, sticky='nsew', padx=1)
                    tk.Label(cell, text=str(val), fg=COLORS['star_num'], bg=bg_color,
                             font=('微软雅黑', self.base_font_size+1, 'bold')).grid(row=0, column=2, sticky='nsew', padx=1)

                    inner.grid_rowconfigure(i//3, weight=1)
                    inner.grid_columnconfigure(i%3, weight=1)

                frame.update_idletasks()

            self.summary_label.config(text=f"星曜：{data['summary']}  |  节气：{data['jie_qi'] or '无'}")

            mountain = self.mountain_var.get().strip()
            offset = self.current_offset

            comment = generate_xuankong_comment(data, mountain if mountain else None, offset)

            # —— 评语分组口径与桌面/4端完全一致（坐山为纲，他宫仅修方提示）——
            lines = []
            lines.append(f"【综合】{comment['summary']}")
            if comment['good_points']:
                lines.append("【吉利】" + "；".join(comment['good_points']))
            if comment.get('mountain_warnings'):
                lines.append("【坐山警示】" + "；".join(comment['mountain_warnings']))
            if comment.get('other_warnings'):
                lines.append("【他宫提示】" + "；".join(comment['other_warnings']))
            if comment.get('mountain_combos'):
                lines.append("【坐山凶格】" + "；".join(comment['mountain_combos']))
            if comment.get('other_combos'):
                lines.append("【他宫凶格】" + "；".join(comment['other_combos']))
            if comment.get('fx_score') is not None:
                lines.append(f"【飞星评分】{comment['fx_score']:+d} 分（坐山口径，-20~+20）｜等级：{comment['fx_level']}")
                # 2026-09-13 追加分项明细（吉星汇聚/凶格/兼向替卦各值），使总分可逐项核对
                _fx_det = (comment.get('mountain_analysis') or {}).get('fx_details') or []
                if _fx_det:
                    lines.append("【得分明细】" + "；".join(_fx_det))
            else:
                lines.append("【飞星评分】未选坐山，暂无坐山评分")

            if comment['mountain_analysis']:
                ma = comment['mountain_analysis']
                lines.append(f"\n【山向分析】{ma['mountain_label']}（{ma['position']}方） 偏移：{ma['offset']:.1f}°")
                lines.append(f"  年星：{STAR_NAMES[ma['stars']['年']-1]}，月星：{STAR_NAMES[ma['stars']['月']-1]}，"
                             f"日星：{STAR_NAMES[ma['stars']['日']-1]}，时星：{STAR_NAMES[ma['stars']['时']-1]}")
                lines.append(f"  吉星数：{ma['good_count']}，凶星数：{ma['bad_count']}")
                lines.append(f"  断语：{ma['level']} —— {ma['suggestion']}")
                if ma['is_partial']:
                    lines.append("  ⚠️ 注意：此日课若用于此兼向，需用替卦飞星重新复核。")
            else:
                lines.append("\n【山向】未选择或无效。")

            self.comment_text.config(state='normal')
            self.comment_text.delete(1.0, tk.END)
            self.comment_text.insert(tk.END, "\n".join(lines))
            self.comment_text.config(state='disabled')

        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")

    def _open_feixing_search(self):
        """打开纯飞星吉日批量搜索窗口（自动带入当前日期/坐山/兼向）。"""
        try:
            preset = {
                'year': int(self.year_var.get()),
                'month': int(self.month_var.get()),
                'day': int(self.day_var.get()),
                'mountain': self.mountain_var.get().strip(),
                'jianxiang': self.jian_var.get().strip(),
            }
        except Exception:
            preset = {}
        FeixingSearchDialog(self.root, preset=preset)

    def generate_report_text(self):
        if not self.current_data:
            return "暂无日课数据，请先刷新飞星。"
        data = self.current_data
        sizhu = data['sizhu']
        lines = []
        lines.append(f"典籍版本：协纪辨方书")
        lines.append(f"日期：{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}")
        lines.append(f"农历：{data['lunar_date']}")
        lines.append(f"四柱：{sizhu['year']} {sizhu['month']} {sizhu['day']} {sizhu['hour']}")
        lines.append(f"评分：{self.summary_label.cget('text')}")
        lines.append("")
        comment_text = self.comment_text.get(1.0, tk.END).strip()
        lines.append("【综合评语】")
        lines.append(comment_text)
        return "\n".join(lines)

    def show_report(self):
        report_text = self.generate_report_text()
        report_window = tk.Toplevel(self.root)
        report_window.title("日课报告")
        report_window.attributes('-fullscreen', True)
        report_window.configure(bg='#0b0e14')
        report_window.bind('<Escape>', lambda e: report_window.destroy())

        st = scrolledtext.ScrolledText(report_window, wrap=tk.WORD,
                                       font=('微软雅黑', self.base_font_size),
                                       bg='#ffffff', fg='#1a2332')
        st.pack(fill=tk.BOTH, expand=True)
        st.insert(tk.END, report_text)
        st.config(state=tk.DISABLED)


# ============================================================
#  飞星吉日搜索（纯飞星批量条件搜索，2026-09-12；2026-09-13 同步至手机版）
#  遍历时间范围每日12时辰，按坐山方年/月/日/时四盘飞星过滤排序；
#  排盘/评分只调用玄空飞星引擎 score_feixing，与单点窗口、评分器同源。
# ============================================================
# (子时初, 时支, 时辰时段显示)
_FX_SEARCH_HOURS = [
    (0, '子', '23-1'), (2, '丑', '1-3'), (4, '寅', '3-5'), (6, '卯', '5-7'),
    (8, '辰', '7-9'), (10, '巳', '9-11'), (12, '午', '11-13'), (14, '未', '13-15'),
    (16, '申', '15-17'), (18, '酉', '17-19'), (20, '戌', '19-21'), (22, '亥', '21-23'),
]
_WEEK = '一二三四五六日'


class FeixingSearchDialog:
    """玄空飞星·吉日搜索对话框（纯飞星口径，不含正五行）。

    过滤项：排除五黄/二黑到坐山、排除凶格（二五/三七/六七）、到山吉星≥N、
    最低飞星分；可选"仅保留每日最佳时辰"。结果按飞星分降序，双击行打开
    该日该时的单点飞星排盘，支持导出 CSV。
    """

    def __init__(self, parent, preset=None):
        self.parent = parent
        self._rows = []          # 当前结果（dict 列表，导出/联动用）
        self._row_iid = {}       # tree iid -> row
        preset = preset or {}

        # 手机自适应字号/尺寸（逻辑与桌面版逐行一致，仅缩放外观）
        sw = parent.winfo_screenwidth()
        sh = parent.winfo_screenheight()
        self.fs = max(10, int(sw / 55))
        _font = ('微软雅黑', self.fs)
        _font_s = ('微软雅黑', self.fs - 1)
        _scale = self.fs / 10.0

        self.win = tk.Toplevel(parent)
        self.win.title("玄空飞星 · 吉日搜索（纯飞星，不涉正五行）")
        self.win.geometry(f"{sw}x{sh}+0+0")
        self.win.configure(bg='#0b0e14')
        self.win.transient(parent)
        self.win.bind('<Escape>', lambda e: self.win.destroy())

        frm = tk.Frame(self.win, bg='#141a24', padx=12, pady=10)
        frm.pack(fill='x', padx=14, pady=(14, 8))

        # —— 第1行：日期范围 + 坐山兼向 ——
        r1 = tk.Frame(frm, bg='#141a24'); r1.pack(fill='x', pady=3)
        tk.Label(r1, text="起：", fg='#e8edf5', bg='#141a24', font=_font).pack(side='left')
        self.start_var = tk.StringVar()
        tk.Entry(r1, textvariable=self.start_var, width=11, bg='#1f2838',
                 fg='#e8edf5', insertbackground='#e8edf5', font=_font).pack(side='left')
        tk.Label(r1, text=" 止：", fg='#e8edf5', bg='#141a24', font=_font).pack(side='left')
        self.end_var = tk.StringVar()
        tk.Entry(r1, textvariable=self.end_var, width=11, bg='#1f2838',
                 fg='#e8edf5', insertbackground='#e8edf5', font=_font).pack(side='left')
        tk.Label(r1, text="（YYYY-MM-DD）   坐山：", fg='#8fa0b8', bg='#141a24',
                 font=_font).pack(side='left')
        self.mountain_var = tk.StringVar()
        self.mountain_combo = ttk.Combobox(r1, textvariable=self.mountain_var,
                                           values=MOUNTAIN_LABELS, width=13, state='readonly',
                                           font=_font)
        self.mountain_combo.pack(side='left', padx=2)
        tk.Label(r1, text=" 兼向：", fg='#e8edf5', bg='#141a24', font=_font).pack(side='left')
        self.jx_var = tk.StringVar(value='正向')
        self.jx_combo = ttk.Combobox(r1, textvariable=self.jx_var, values=['正向'],
                                     width=7, state='readonly', font=_font)
        self.jx_combo.pack(side='left', padx=2)

        # —— 第2行：过滤条件 ——
        r2 = tk.Frame(frm, bg='#141a24'); r2.pack(fill='x', pady=3)
        self.var_no5 = tk.IntVar(value=1)
        self.var_no2 = tk.IntVar(value=1)
        self.var_nocombo = tk.IntVar(value=1)
        self.var_best_only = tk.IntVar(value=1)
        for txt, var in [("排除五黄到山", self.var_no5), ("排除二黑到山", self.var_no2),
                         ("排除凶格(二五/三七/六七)", self.var_nocombo),
                         ("仅保留每日最佳时辰", self.var_best_only)]:
            tk.Checkbutton(r2, text=txt, variable=var, bg='#141a24', fg='#e8edf5',
                           selectcolor='#1f2838', activebackground='#141a24',
                           activeforeground='#e8edf5', font=_font).pack(side='left', padx=6)
        tk.Label(r2, text="  到山吉星≥", fg='#e8edf5', bg='#141a24', font=_font).pack(side='left')
        self.good_min_var = tk.IntVar(value=0)
        tk.Spinbox(r2, from_=0, to=4, width=3, textvariable=self.good_min_var,
                   bg='#1f2838', fg='#e8edf5', font=_font).pack(side='left', padx=2)
        tk.Label(r2, text="颗  最低飞星分", fg='#e8edf5', bg='#141a24', font=_font).pack(side='left')
        self.min_score_var = tk.IntVar(value=-20)
        tk.Spinbox(r2, from_=-20, to=20, increment=1, width=4,
                   textvariable=self.min_score_var, bg='#1f2838', fg='#e8edf5',
                   font=_font).pack(side='left', padx=2)
        tk.Label(r2, text="(-20=不限)", fg='#8fa0b8', bg='#141a24', font=_font_s).pack(side='left')

        # —— 第3行：按钮 + 进度 ——
        r3 = tk.Frame(frm, bg='#141a24'); r3.pack(fill='x', pady=(6, 0))
        self.btn_search = tk.Button(r3, text="🔍 开始搜索", command=self.do_search,
                                    bg='#d4af70', fg='#0b0e14', font=('微软雅黑', self.fs, 'bold'),
                                    padx=14)
        self.btn_search.pack(side='left')
        tk.Button(r3, text="导出CSV", command=self.export_csv, bg='#3a6ea5', fg='#ffffff',
                  font=_font, padx=12).pack(side='left', padx=8)
        self.status_var = tk.StringVar(value="请设置条件后开始搜索")
        tk.Label(r3, textvariable=self.status_var, fg='#d4af70', bg='#141a24',
                 font=_font).pack(side='left', padx=12)
        self.pbar = ttk.Progressbar(frm, mode='determinate')
        self.pbar.pack(fill='x', pady=(6, 0))

        # —— 结果表 ——
        cols = ('date', 'week', 'hour', 'shizhu', 'stars', 'good', 'score', 'level', 'warn')
        headers = {'date': '公历', 'week': '星期', 'hour': '时辰', 'shizhu': '时柱',
                   'stars': '到山星(年月日时)', 'good': '吉星', 'score': '飞星分',
                   'level': '等级', 'warn': '凶格/断语'}
        widths = {'date': 92, 'week': 48, 'hour': 92, 'shizhu': 58, 'stars': 150,
                  'good': 46, 'score': 58, 'level': 58, 'warn': 420}
        tree_frame = tk.Frame(self.win, bg='#0b0e14')
        tree_frame.pack(fill='both', expand=True, padx=14, pady=10)
        row_h = max(24, int(26 * _scale))
        tree_style = ttk.Style()
        tree_style.configure('Fx.Treeview', font=_font, rowheight=row_h)
        tree_style.configure('Fx.Treeview.Heading', font=_font)
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings',
                                 height=max(12, (sh - 320) // row_h), style='Fx.Treeview')
        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=max(36, int(widths[c] * _scale)), anchor='center',
                             stretch=(c == 'warn'))
        self.tree.tag_configure('大吉', foreground='#8bc34a')
        self.tree.tag_configure('吉', foreground='#b8d98a')
        self.tree.tag_configure('平', foreground='#9fb0c8')
        self.tree.tag_configure('凶', foreground='#e5a073')
        self.tree.tag_configure('大凶', foreground='#e57373')
        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        self.tree.bind('<Double-1>', self.open_detail)

        # —— 带入 preset ——
        m0 = preset.get('mountain')
        if m0 and m0 in MOUNTAINS_CW:
            self.mountain_var.set(f"{m0}山 · {MOUNTAIN_DIRECTION.get(m0, '')}")
        else:
            self.mountain_var.set('乾山 · 西北')
        self._refresh_jx_options()
        jx0 = preset.get('jianxiang')
        if jx0 and jx0 in self.jx_combo['values']:
            self.jx_var.set(jx0)
        try:
            d0 = date(int(preset.get('year') or datetime.now().year),
                      int(preset.get('month') or datetime.now().month),
                      int(preset.get('day') or datetime.now().day))
        except Exception:
            d0 = date.today()
        self.start_var.set(str(d0))
        self.end_var.set(str(d0 + timedelta(days=30)))
        self.mountain_combo.bind('<<ComboboxSelected>>', self._on_mountain_change)

    # ---------- 山向辅助 ----------
    def _selected_mountain(self):
        text = self.mountain_var.get().strip()
        for m in MOUNTAINS_CW:
            if text.startswith(m + '山'):
                return m
        return text if text in MOUNTAINS_CW else None

    def _refresh_jx_options(self):
        m = self._selected_mountain()
        if m in MOUNTAINS_CW:
            idx = MOUNTAINS_CW.index(m)
            prev_m = MOUNTAINS_CW[(idx - 1) % 24]
            next_m = MOUNTAINS_CW[(idx + 1) % 24]
            self.jx_combo['values'] = ['正向', f'兼{prev_m}', f'兼{next_m}']
        else:
            self.jx_combo['values'] = ['正向']

    def _on_mountain_change(self, event=None):
        self.jx_var.set('正向')
        self._refresh_jx_options()

    # ---------- 搜索主流程 ----------
    def do_search(self):
        try:
            d0 = datetime.strptime(self.start_var.get().strip(), '%Y-%m-%d').date()
            d1 = datetime.strptime(self.end_var.get().strip(), '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("日期错误", "请输入正确的日期格式：YYYY-MM-DD", parent=self.win)
            return
        if d0 > d1:
            messagebox.showerror("日期错误", "开始日期不能晚于结束日期", parent=self.win)
            return
        m = self._selected_mountain()
        if not m:
            messagebox.showerror("山向错误", "请选择坐山", parent=self.win)
            return
        jx = self.jx_var.get().strip()
        sx_full = m + '山' + ('' if jx == '正向' else jx)

        no5, no2 = bool(self.var_no5.get()), bool(self.var_no2.get())
        no_combo = bool(self.var_nocombo.get())
        best_only = bool(self.var_best_only.get())
        good_min = int(self.good_min_var.get())
        min_score = int(self.min_score_var.get())

        days_total = (d1 - d0).days + 1
        self.pbar.configure(maximum=days_total, value=0)
        self.btn_search.configure(state='disabled')
        rows = []
        try:
            cur, di = d0, 0
            while cur <= d1:
                day_hits = []
                for h, hz, hr_txt in _FX_SEARCH_HOURS:
                    try:
                        sz = calculate_sizhu(cur, h, 0)
                        sz['year'] = cur.year
                        sz['month'] = cur.month
                        sz['day'] = cur.day
                        sz['date'] = cur
                        r = score_feixing(sz, sx_full)
                        if not r:
                            continue
                        if no5 and r['has_5']:
                            continue
                        if no2 and r['has_2']:
                            continue
                        if no_combo and r['combos']:
                            continue
                        if r['good_count'] < good_min:
                            continue
                        if r['feixing_score'] < min_score:
                            continue
                        warns = '、'.join(r['combos'])
                        if warns:
                            warns += '；'
                        if r['combos'] or r['feixing_level'] in ('凶', '大凶', '平'):
                            warns += r['feixing_comment']
                        day_hits.append({
                            'date': cur, 'hour': h, 'hour_zhi': hz, 'hour_range': hr_txt,
                            'shizhu': sz.get('时柱', ''),
                            'stars': r['stars_list'], 'good': r['good_count'],
                            'bad': r['bad_count'], 'score': r['feixing_score'],
                            'level': r['feixing_level'], 'warns': warns,
                            'details': '；'.join(r['feixing_details']),
                            'mountain': m, 'jianxiang': jx, 'sx_full': sx_full,
                        })
                    except Exception as e:
                        print(f"[飞星搜索] {cur} {hz}时 计算失败: {e}")
                # 每日仅取综合最优（飞星分→吉星数→早时优先），避免一日占满列表
                if day_hits:
                    if best_only:
                        best = max(day_hits, key=lambda x: (x['score'], x['good'], -x['hour']))
                        rows.append(best)
                    else:
                        rows.extend(day_hits)
                cur += timedelta(days=1)
                di += 1
                self.pbar.configure(value=di)
                self.status_var.set(f"搜索中… {di}/{days_total} 天，已命中 {len(rows)} 条")
                if di % 5 == 0:
                    self.win.update_idletasks()
        finally:
            self.btn_search.configure(state='normal')

        rows.sort(key=lambda x: (-x['score'], -x['good'], x['date'].toordinal(), x['hour']))
        self._rows = rows
        self._populate(rows)
        self.status_var.set(f"完成：{days_total} 天，命中 {len(rows)} 条（{sx_full}），按飞星分降序")

    def _populate(self, rows):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._row_iid = {}
        for row in rows:
            stars_txt = ' · '.join(str(s) for s in row['stars'])
            iid = self.tree.insert(
                '', 'end',
                values=(str(row['date']), '周' + _WEEK[row['date'].weekday()],
                        f"{row['hour_zhi']}时({row['hour_range']})", row['shizhu'],
                        stars_txt, row['good'], row['score'], row['level'], row['warns']),
                tags=(row['level'],))
            self._row_iid[iid] = row

    # ---------- 双击：打开该时辰单点排盘 ----------
    def open_detail(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        row = self._row_iid.get(sel[0])
        if not row:
            return
        win2 = tk.Toplevel(self.win)
        XuanKongApp(win2, preset={
            'year': row['date'].year, 'month': row['date'].month, 'day': row['date'].day,
            'hour': row['hour'], 'minute': 0,
            'mountain': row['mountain'], 'jianxiang': row['jianxiang'],
        })

    # ---------- 导出 ----------
    def export_csv(self):
        if not self._rows:
            messagebox.showinfo("提示", "没有可导出的搜索结果", parent=self.win)
            return
        path = filedialog.asksaveasfilename(
            title="导出飞星吉日搜索结果",
            defaultextension='.csv', filetypes=[('CSV 文件', '*.csv')],
            initialfile=f"飞星吉日_{self.start_var.get()}_{self.end_var.get()}.csv",
            parent=self.win)
        if not path:
            return
        import csv
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['公历', '星期', '时辰', '时柱', '坐山', '兼向',
                        '年到山星', '月到山星', '日到山星', '时到山星',
                        '吉星数', '凶星数', '飞星分', '等级', '凶格/断语', '评分明细'])
            for r in self._rows:
                w.writerow([str(r['date']), '周' + _WEEK[r['date'].weekday()],
                            f"{r['hour_zhi']}时({r['hour_range']})", r['shizhu'],
                            r['mountain'], r['jianxiang'],
                            r['stars'][0], r['stars'][1], r['stars'][2], r['stars'][3],
                            r['good'], r['bad'], r['score'], r['level'],
                            r['warns'], r['details']])
        messagebox.showinfo("导出成功", f"已导出 {len(self._rows)} 条：\n{path}", parent=self.win)


if __name__ == '__main__':
    try:
        import sxtwl
        import lunar_python
    except ImportError:
        print("请先安装依赖：pip install sxtwl lunar-python loguru")
        sys.exit(1)

    root = tk.Tk()
    app = XuanKongApp(root)
    root.mainloop()
