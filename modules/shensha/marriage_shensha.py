# -*- coding: utf-8 -*-
"""
婚嫁专用神煞推算模块（基于《协纪辨方书》）
"""

from datetime import date, datetime
import math

# ==================== 基础干支转换 ====================

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

def gan_index(gan):
    """天干转索引"""
    return GAN.index(gan)

def zhi_index(zhi):
    """地支转索引"""
    return ZHI.index(zhi)

def get_day_ganzhi(date_obj):
    """根据公历日期计算日干支（返回(gan, zhi)）"""
    # 使用公式：日干支基数 = (年尾二位数+7)*5+15+(年尾二位数+19)/4
    # 这里简化为调用已有函数，实际项目中可用 sxtwl 或预置函数
    try:
        from ..四柱计算器 import calculate_sizhu
    except ImportError:
        from 四柱计算器 import calculate_sizhu
    sizhu = calculate_sizhu(date_obj, 12, 0)
    day_gan = sizhu['日柱'][0]
    day_zhi = sizhu['日柱'][1]
    return day_gan, day_zhi

# ==================== 月神 ====================

def get_tiande_month(month):
    """
    天德月（月神，返回天干或地支）
    正月在丁，二月在坤，三月在壬，四月在辛，五月在亥，六月在甲，
    七月在癸，八月在艮，九月在丙，十月在乙，十一月在巳，十二月在庚
    返回：对应的天干、地支
    """
    map_month = {
        1: '丁', 2: '坤', 3: '壬', 4: '辛', 5: '亥', 6: '甲',
        7: '癸', 8: '艮', 9: '丙', 10: '乙', 11: '巳', 12: '庚'
    }
    return map_month.get(month)

def is_tiande_day(date_obj):
    """判断某日是否为天德日（日干或日支符合当月天德）"""
    # 获取农历月份（天德按农历月份判断）
    try:
        from ..四柱计算器 import get_lunar_date
        lunar_info = get_lunar_date(date_obj)
        # 解析农历月份
        month_map = {
            '正月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
            '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '腊月': 12
        }
        lunar_month_str = lunar_info.get('month', '')
        month = month_map.get(lunar_month_str, date_obj.month)
    except:
        # 回退到公历月份
        month = _get_lunar_month(date_obj)
    
    tiande = get_tiande_month(month)
    day_gan, day_zhi = get_day_ganzhi(date_obj)
    
    # 天德可能是天干、地支或卦名（坤、乾、艮、巽）
    if tiande in GAN and day_gan == tiande:
        return True
    if tiande in ZHI and day_zhi == tiande:
        return True
    # 当夭德为卦名时，传统认为该日整体吉利，直接视为天德日
    if tiande in ['坤', '乾', '艮', '巽']:
        return True
    return False

def get_yuede_month(year_gan, month):
    """
    月德月：寅午戌月在丙，亥卯未月在甲，申子辰月在壬，巳酉丑月在庚
    根据年支（非月支）？《协纪辨方书》以月支三合局定月德。
    正确方法：月德以月支定：
    寅月、午月、戌月 -> 天干丙
    亥月、卯月、未月 -> 天干甲
    申月、子月、辰月 -> 天干壬
    巳月、酉月、丑月 -> 天干庚
    """
    month_zhi = ZHI[(month - 1) % 12]  # 月地支
    if month_zhi in ['寅', '午', '戌']:
        return '丙'
    elif month_zhi in ['亥', '卯', '未']:
        return '甲'
    elif month_zhi in ['申', '子', '辰']:
        return '壬'
    elif month_zhi in ['巳', '酉', '丑']:
        return '庚'
    return None

def _get_lunar_month(date_obj):
    """获取命理月份（按节气划分，用于天德、月德等神煞判断）
    
    命理月份与节气的对应关系：
    寅月：立春 -> 惊蛰
    卯月：惊蛰 -> 清明
    辰月：清明 -> 立夏
    巳月：立夏 -> 芒种
    午月：芒种 -> 小暑
    未月：小暑 -> 立秋
    申月：立秋 -> 白露
    酉月：白露 -> 寒露
    戌月：寒露 -> 立冬
    亥月：立冬 -> 大雪
    子月：大雪 -> 小寒
    丑月：小寒 -> 立春
    """
    try:
        from ..四柱计算器 import calculate_sizhu
        # 使用中午12点来计算，避免时辰影响
        sizhu = calculate_sizhu(date_obj, 12, 0)
        # 获取月支并转换为月份数字
        month_zhi = sizhu.get('month_zhi', '')
        zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        if month_zhi in zhi_order:
            # 月支与农历月份对应：子=11, 丑=12, 寅=1, 卯=2...
            index = zhi_order.index(month_zhi)
            if index <= 1:  # 子或丑
                return index + 11
            else:  # 寅到亥
                return index - 1
    except:
        pass
    
    # 回退到使用get_lunar_date获取农历月份
    try:
        from ..四柱计算器 import get_lunar_date
        lunar_info = get_lunar_date(date_obj)
        # 解析农历月份
        month_map = {
            '正月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
            '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '腊月': 12,
            '闰正月': 1, '闰二月': 2, '闰三月': 3, '闰四月': 4, '闰五月': 5, '闰六月': 6,
            '闰七月': 7, '闰八月': 8, '闰九月': 9, '闰十月': 10, '闰十一月': 11, '闰腊月': 12
        }
        lunar_month_str = lunar_info.get('month', '')
        return month_map.get(lunar_month_str, date_obj.month)
    except:
        # 最终回退到公历月份
        return date_obj.month


def is_yuede_day(date_obj):
    """判断是否为月德日"""
    month = _get_lunar_month(date_obj)
    yuede_gan = get_yuede_month(None, month)
    if not yuede_gan:
        return False
    day_gan, _ = get_day_ganzhi(date_obj)
    return day_gan == yuede_gan


def is_yuedehe_day(date_obj):
    """月德合：与月德相合的天干日"""
    month = _get_lunar_month(date_obj)
    yuede = get_yuede_month(None, month)
    if not yuede:
        return False
    # 五合：甲己、乙庚、丙辛、丁壬、戊癸
    he_map = {'甲': '己', '乙': '庚', '丙': '辛', '丁': '壬', '戊': '癸',
              '己': '甲', '庚': '乙', '辛': '丙', '壬': '丁', '癸': '戊'}
    yuede_he = he_map.get(yuede)
    if not yuede_he:
        return False
    day_gan, _ = get_day_ganzhi(date_obj)
    return day_gan == yuede_he


def is_tiandehe_day(date_obj):
    """天德合：与天德相合的天干或地支日"""
    month = _get_lunar_month(date_obj)
    tiande = get_tiande_month(month)
    if not tiande:
        return False
    
    day_gan, day_zhi = get_day_ganzhi(date_obj)
    
    # 天德可能是天干、地支或卦名
    if tiande in GAN:
        # 五合：甲己、乙庚、丙辛、丁壬、戊癸
        he_map = {'甲': '己', '乙': '庚', '丙': '辛', '丁': '壬', '戊': '癸',
                  '己': '甲', '庚': '乙', '辛': '丙', '壬': '丁', '癸': '戊'}
        tiande_he = he_map.get(tiande)
        if tiande_he:
            return day_gan == tiande_he
    elif tiande in ZHI:
        # 六合：子丑、寅亥、卯戌、辰酉、巳申、午未
        he_map = {'子': '丑', '丑': '子', '寅': '亥', '亥': '寅',
                  '卯': '戌', '戌': '卯', '辰': '酉', '酉': '辰',
                  '巳': '申', '申': '巳', '午': '未', '未': '午'}
        tiande_he = he_map.get(tiande)
        if tiande_he:
            return day_zhi == tiande_he
    elif tiande in ['坤', '乾', '艮', '巽']:
        # 天德为卦名时，天德合日为与卦位相合的方位
        # 简化处理：卦名天德的合日也视为吉利
        return True
    
    return False

# ==================== 不将日 ====================

# 不将日查表（按农历月份）
# 口诀：正七迎鸡兔，二八虎和猴，三九蛇共猪，四十龙和狗，牛羊五十一，鼠马六腊月
# 但不将日需要具体干支组合
BU_JIANG_TABLE = {
    1: ['丙子', '丙寅', '庚寅', '丁卯', '丁丑', '丁亥', '辛亥', '辛丑', '辛未', '己卯', '己亥', '己丑'],
    2: ['乙丑', '乙亥', '丁丑', '丁亥', '丙寅', '丙子', '丙戌', '己亥', '己丑', '庚寅', '庚子', '庚戌'],
    3: ['己亥', '己丑', '己酉', '丁亥', '丁丑', '丁酉', '丙子', '丙戌', '乙亥', '乙丑', '乙卯', '甲子', '甲戌'],
    4: ['甲子', '甲戌', '甲申', '丁亥', '丁酉', '丙子', '丙戌', '丙申', '乙亥', '乙酉', '戊子', '戊戌', '戊申'],
    5: ['丙戌', '丙申', '乙亥', '乙酉', '乙未', '甲戌', '甲申', '戊戌', '戊申', '癸亥', '癸酉', '癸未'],
    6: ['乙酉', '乙未', '甲戌', '甲申', '戊戌', '戊子', '戊申', '癸酉', '癸未', '壬戌', '壬申', '壬午'],
    7: ['乙酉', '乙未', '乙巳', '甲申', '甲午', '戊申', '戊戌', '戊午', '癸酉', '癸未', '癸巳', '壬申', '壬午'],
    8: ['甲申', '甲午', '甲辰', '戊申', '戊辰', '戊午', '壬申', '壬午', '壬辰', '癸未', '癸巳', '辛未', '辛巳'],
    9: ['己未', '己巳', '己卯', '癸未', '癸巳', '癸卯', '壬午', '壬辰', '辛未', '辛巳', '辛卯', '庚午', '庚辰'],
    10: ['庚午', '己卯', '庚辰', '壬午', '庚寅', '辛卯', '壬辰', '壬寅', '癸卯', '己巳', '辛巳', '癸巳'],
    11: ['壬辰', '壬寅', '辛巳', '辛卯', '辛丑', '庚辰', '庚寅', '己巳', '己卯', '己丑', '丁巳', '丁卯', '丁丑'],
    12: ['丙寅', '丁卯', '丁丑', '丙子', '丙辰', '己卯', '己丑', '庚寅', '庚子', '庚辰', '辛卯', '辛丑']
}

def is_bujiang_day(date_obj):
    """
    不将日：阴阳不相妨之日，嫁娶首选。
    根据用户提供的逐月不将日干支列表判断。
    """
    month = _get_lunar_month(date_obj)
    day_gan, day_zhi = get_day_ganzhi(date_obj)
    ganzhi = day_gan + day_zhi

    if month in BU_JIANG_TABLE:
        return ganzhi in BU_JIANG_TABLE[month]
    return False

# ==================== 建除十二神 ====================

def get_jianchu(date_obj):
    """
    建除十二神：建、除、满、平、定、执、破、危、成、收、开、闭
    按月建（月地支）起建，顺数至日地支。
    返回神名（如'建'、'除'...）
    """
    # 直接从四柱获取月支，避免从农历月份反推的错误
    try:
        from ..四柱计算器 import calculate_sizhu
        sizhu = calculate_sizhu(date_obj, 12, 0)
        month_zhi = sizhu.get('month_zhi', '')
    except:
        # 回退方案：从农历月份计算月支
        month = _get_lunar_month(date_obj)
        # 正确的农历月份到月支映射：子=11, 丑=12, 寅=1, 卯=2...
        zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        idx = (month - 1) % 12
        month_zhi = zhi_order[(idx + 2) % 12]  # 调整偏移：农历1月(寅)对应索引2
    
    _, day_zhi = get_day_ganzhi(date_obj)
    # 地支顺序索引
    month_idx = zhi_index(month_zhi)
    day_idx = zhi_index(day_zhi)
    offset = (day_idx - month_idx) % 12
    jianchu_list = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
    return jianchu_list[offset]

def is_xiao_huangdao_day(date_obj):
    """小黄道（建除）吉日：除、危、定、执、成、开"""
    jianchu = get_jianchu(date_obj)
    huangdao = ['除', '危', '定', '执', '成', '开']
    return jianchu in huangdao

def is_da_huangdao_day(date_obj):
    """大黄道（十二神）吉日：青龙、明堂、金匮、天德、玉堂、司命
    
    使用汉程黄历算法：result = (日支索引 - 2*月支索引 + 4) % 12
    """
    try:
        from ..四柱计算器 import calculate_sizhu
        sizhu = calculate_sizhu(date_obj, 12, 0)
        month_zhi = sizhu.get('month_zhi', '')
        _, day_zhi = get_day_ganzhi(date_obj)
        
        zhi_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        huangdao_list = ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德',
                        '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈']
        jiri_list = ['青龙', '明堂', '金匮', '天德', '玉堂', '司命']
        
        if month_zhi not in zhi_list or day_zhi not in zhi_list:
            return False
            
        month_idx = zhi_list.index(month_zhi)
        day_idx = zhi_list.index(day_zhi)
        huangdao_idx = (day_idx - 2 * month_idx + 4) % 12
        huangdao_name = huangdao_list[huangdao_idx]
        
        return huangdao_name in jiri_list
    except:
        return False

def is_huangdao_day(date_obj):
    """大黄道（十二神）吉日：青龙、明堂、金匮、天德、玉堂、司命
    
    使用汉程黄历算法
    """
    return is_da_huangdao_day(date_obj)

# ==================== 冲克刑害 ====================

def is_chong_gan(gan1, gan2):
    """天干相冲：甲庚、乙辛、丙壬、丁癸、戊己（戊己同中央，不冲）"""
    chong_pairs = [('甲','庚'),('乙','辛'),('丙','壬'),('丁','癸')]
    return (gan1, gan2) in chong_pairs or (gan2, gan1) in chong_pairs

def is_chong(zhi1, zhi2):
    """地支六冲"""
    dui = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅',
           '卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}
    return dui.get(zhi1) == zhi2

def is_liuhe(zhi1, zhi2):
    """地支六合"""
    he = {('子','丑'),('丑','子'),('寅','亥'),('亥','寅'),('卯','戌'),('戌','卯'),
          ('辰','酉'),('酉','辰'),('巳','申'),('申','巳'),('午','未'),('未','午')}
    return (zhi1, zhi2) in he

def is_sanhe(zhi1, zhi2, zhi3=None):
    """三合（返回是否在同一局）"""
    groups = [{'申','子','辰'}, {'亥','卯','未'}, {'寅','午','戌'}, {'巳','酉','丑'}]
    for g in groups:
        if zhi1 in g and zhi2 in g:
            return True
    return False

def is_xing(zhi1, zhi2):
    """地支三刑（简化版）"""
    xing_map = {
        ('寅','巳'):True, ('巳','寅'):True, ('寅','申'):True, ('申','寅'):True,
        ('巳','申'):True, ('申','巳'):True, ('丑','未'):True, ('未','丑'):True,
        ('丑','戌'):True, ('戌','丑'):True, ('未','戌'):True, ('戌','未'):True,
        ('子','卯'):True, ('卯','子'):True,
    }
    return xing_map.get((zhi1, zhi2), False)

def is_hai(zhi1, zhi2):
    """地支六害"""
    hai = {('子','未'),('未','子'),('丑','午'),('午','丑'),('寅','巳'),('巳','寅'),
           ('卯','辰'),('辰','卯'),('申','亥'),('亥','申'),('酉','戌'),('戌','酉')}
    return (zhi1, zhi2) in hai

# ==================== 夫星、子星 ====================

def get_fuxing_zixing(day_gan):
    """
    根据日干返回夫星（正官）、七杀、子星（食神）、伤官的完整干支
    
    在八字命理中：
    - 夫星：克日干的五行（官杀），女命以官杀为夫
    - 子星：日干所生的五行（食伤），女命以食伤为子
    
    Returns:
        dict: {'fu':正官干支, 'qi':七杀干支, 'zi':食神干支, 'shang':伤官干支}
    """
    # 天干阴阳属性
    gan_yang = ['甲', '丙', '戊', '庚', '壬']  # 阳干
    gan_yin = ['乙', '丁', '己', '辛', '癸']   # 阴干
    
    # 夫星（官杀）天干映射：阳日干取正官，阴日干取七杀
    fuxing_gan_map = {
        '甲': ('辛', '庚'),  # 甲木：正官辛金，七杀庚金
        '乙': ('庚', '辛'),  # 乙木：正官庚金，七杀辛金
        '丙': ('癸', '壬'),  # 丙火：正官癸水，七杀壬水
        '丁': ('壬', '癸'),  # 丁火：正官壬水，七杀癸水
        '戊': ('乙', '甲'),  # 戊土：正官乙木，七杀甲木
        '己': ('甲', '乙'),  # 己土：正官甲木，七杀乙木
        '庚': ('丁', '丙'),  # 庚金：正官丁火，七杀丙火
        '辛': ('丙', '丁'),  # 辛金：正官丙火，七杀丁火
        '壬': ('己', '戊'),  # 壬水：正官己土，七杀戊土
        '癸': ('戊', '己'),  # 癸水：正官戊土，七杀己土
    }
    
    # 子星（食伤）天干映射：日干所生的五行
    zixing_gan_map = {
        '甲': ('丙', '丁'),  # 甲木：食神丙火，伤官丁火
        '乙': ('丁', '丙'),  # 乙木：食神丁火，伤官丙火
        '丙': ('戊', '己'),  # 丙火：食神戊土，伤官己土
        '丁': ('己', '戊'),  # 丁火：食神己土，伤官戊土
        '戊': ('庚', '辛'),  # 戊土：食神庚金，伤官辛金
        '己': ('辛', '庚'),  # 己土：食神辛金，伤官庚金
        '庚': ('壬', '癸'),  # 庚金：食神壬水，伤官癸水
        '辛': ('癸', '壬'),  # 辛金：食神癸水，伤官壬水
        '壬': ('甲', '乙'),  # 壬水：食神甲木，伤官乙木
        '癸': ('乙', '甲'),  # 癸水：食神乙木，伤官甲木
    }
    
    # 五行对应的地支（根据天干阴阳选择）
    wuxing_zhi_map = {
        '金': {'yang': '申', 'yin': '酉'},
        '水': {'yang': '子', 'yin': '亥'},
        '木': {'yang': '寅', 'yin': '卯'},
        '火': {'yang': '午', 'yin': '巳'},
        '土': {'yang': '辰', 'yin': '丑'},
    }
    
    gan_wuxing = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', 
                  '戊': '土', '己': '土', '庚': '金', '辛': '金', 
                  '壬': '水', '癸': '水'}
    
    fu_gan, qi_gan = fuxing_gan_map.get(day_gan, ('', ''))
    zi_gan, shang_gan = zixing_gan_map.get(day_gan, ('', ''))
    
    # 确定地支（根据天干阴阳选择对应阴阳的地支）
    def get_zhi(gan, wuxing):
        if not gan or not wuxing:
            return ''
        if gan in gan_yang:
            return wuxing_zhi_map.get(wuxing, {}).get('yang', '')
        else:
            return wuxing_zhi_map.get(wuxing, {}).get('yin', '')
    
    fu_wuxing = gan_wuxing.get(fu_gan, '')
    fu_zhi = get_zhi(fu_gan, fu_wuxing)
    
    qi_wuxing = gan_wuxing.get(qi_gan, '')
    qi_zhi = get_zhi(qi_gan, qi_wuxing)
    
    zi_wuxing = gan_wuxing.get(zi_gan, '')
    zi_zhi = get_zhi(zi_gan, zi_wuxing)
    
    shang_wuxing = gan_wuxing.get(shang_gan, '')
    shang_zhi = get_zhi(shang_gan, shang_wuxing)
    
    return {
        'fu': fu_gan + fu_zhi if fu_gan and fu_zhi else '',
        'qi': qi_gan + qi_zhi if qi_gan and qi_zhi else '',
        'zi': zi_gan + zi_zhi if zi_gan and zi_zhi else '',
        'shang': shang_gan + shang_zhi if shang_gan and shang_zhi else ''
    }

# ==================== 阴胎、阳气 ====================

def get_yintai(month_gan, month_zhi):
    """阴胎 = 月干顺进一位 + 月支顺进三位"""
    gan_idx = gan_index(month_gan)
    zhi_idx = zhi_index(month_zhi)
    yintai_gan = GAN[(gan_idx + 1) % 10]   # 月干顺进一位
    yintai_zhi = ZHI[(zhi_idx + 3) % 12]   # 月支顺进三位
    return yintai_gan, yintai_zhi

def get_yangqi(month_gan, month_zhi):
    """阳气 = 月干顺进一位 + 月支顺进三位"""
    gan_idx = gan_index(month_gan)
    zhi_idx = zhi_index(month_zhi)
    yangqi_gan = GAN[(gan_idx + 1) % 10]   # 月干顺进一位
    yangqi_zhi = ZHI[(zhi_idx + 3) % 12]   # 月支顺进三位
    return yangqi_gan, yangqi_zhi

# ==================== 其它凶神 ====================

def is_month_break(date_obj):
    """月破：日支与月支相冲"""
    try:
        from ..四柱计算器 import calculate_sizhu
        sizhu = calculate_sizhu(date_obj, 12, 0)
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        if month_zhi and day_zhi:
            return is_chong(month_zhi, day_zhi)
    except:
        pass
    
    # 备用方案：使用农历月份计算
    month = _get_lunar_month(date_obj)
    # 农历月份与地支对应：正月寅(1)、二月卯(2)、三月辰(3)...
    # ZHI数组顺序：['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    # 正月寅对应ZHI[2]，所以偏移量为2
    month_zhi = ZHI[(month + 1) % 12]  # 修正：(month-1+2) % 12 = (month+1) % 12
    _, day_zhi = get_day_ganzhi(date_obj)
    return is_chong(month_zhi, day_zhi)

def is_year_break(date_obj, year_zhi):
    """岁破：日支与年支相冲"""
    _, day_zhi = get_day_ganzhi(date_obj)
    return is_chong(year_zhi, day_zhi)

def is_sili_sijue(date_obj):
    """四离四绝：立春、立夏、立秋、立冬前一日为四离；春分、秋分、夏至、冬至前一日为四绝"""
    # 简化：检查是否在节气前一日，需要精确节气数据，这里用月份粗略判断
    # 实际应调用节气计算函数
    return False  # 待实现

def is_sansha(date_obj, year_zhi):
    """
    三煞日：年支对冲的三合局
    申子辰年：三煞在南方（巳午未）
    寅午戌年：三煞在北方（亥子丑）
    亥卯未年：三煞在西方（申酉戌）
    巳酉丑年：三煞在东方（寅卯辰）
    """
    groups = {
        '申':'巳午未', '子':'巳午未', '辰':'巳午未',
        '寅':'亥子丑', '午':'亥子丑', '戌':'亥子丑',
        '亥':'申酉戌', '卯':'申酉戌', '未':'申酉戌',
        '巳':'寅卯辰', '酉':'寅卯辰', '丑':'寅卯辰'
    }
    _, day_zhi = get_day_ganzhi(date_obj)
    return day_zhi in groups.get(year_zhi, '')

def is_tiangang_day(date_obj):
    """
    判断是否为天罡日（妨翁日）
    
    根据《协纪辨方书》规则：
    正月寅月→巳日、二月卯月→辰日、三月辰月→卯日、四月巳月→寅日
    五月午月→丑日、六月未月→子日、七月申月→亥日、八月酉月→戌日
    九月戌月→酉日、十月亥月→申日、十一月子月→未日、十二月丑月→午日
    """
    # 获取月支和日支
    try:
        from ..四柱计算器 import calculate_sizhu
        sizhu = calculate_sizhu(date_obj, 12, 0)
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        
        # 天罡日规则（妨翁）
        tiangang_map = {
            '寅': '巳',  # 正月（寅月）的巳日是天罡日
            '卯': '辰',  # 二月（卯月）的辰日是天罡日
            '辰': '卯',  # 三月（辰月）的卯日是天罡日
            '巳': '寅',  # 四月（巳月）的寅日是天罡日
            '午': '丑',  # 五月（午月）的丑日是天罡日
            '未': '子',  # 六月（未月）的子日是天罡日
            '申': '亥',  # 七月（申月）的亥日是天罡日
            '酉': '戌',  # 八月（酉月）的戌日是天罡日
            '戌': '酉',  # 九月（戌月）的酉日是天罡日
            '亥': '申',  # 十月（亥月）的申日是天罡日
            '子': '未',  # 十一月（子月）的未日是天罡日
            '丑': '午'   # 十二月（丑月）的午日是天罡日
        }
        
        return tiangang_map.get(month_zhi) == day_zhi
    except Exception as e:
        return False

def is_hekui_day(date_obj):
    """
    判断是否为河魁日（妨姑日）
    
    根据《协纪辨方书》规则：
    正月寅月→亥日、二月卯月→戌日、三月辰月→酉日、四月巳月→申日
    五月午月→未日、六月未月→午日、七月申月→巳日、八月酉月→辰日
    九月戌月→卯日、十月亥月→寅日、十一月子月→丑日、十二月丑月→子日
    """
    # 获取月支和日支
    try:
        from ..四柱计算器 import calculate_sizhu
        sizhu = calculate_sizhu(date_obj, 12, 0)
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        
        # 河魁日规则（妨姑）
        hekui_map = {
            '寅': '亥',  # 正月（寅月）的亥日是河魁日
            '卯': '戌',  # 二月（卯月）的戌日是河魁日
            '辰': '酉',  # 三月（辰月）的酉日是河魁日
            '巳': '申',  # 四月（巳月）的申日是河魁日
            '午': '未',  # 五月（午月）的未日是河魁日
            '未': '午',  # 六月（未月）的午日是河魁日
            '申': '巳',  # 七月（申月）的巳日是河魁日
            '酉': '辰',  # 八月（酉月）的辰日是河魁日
            '戌': '卯',  # 九月（戌月）的卯日是河魁日
            '亥': '寅',  # 十月（亥月）的寅日是河魁日
            '子': '丑',  # 十一月（子月）的丑日是河魁日
            '丑': '子'   # 十二月（丑月）的子日是河魁日
        }
        
        return hekui_map.get(month_zhi) == day_zhi
    except Exception as e:
        return False

def is_shangshuo(date_obj):
    """
    上朔日：阳年以年干加寅顺数至亥，阴年以年干加丑顺数至巳
    简化版：上朔日有固定干支，共12日：
    甲寅、乙卯、丙辰、丁巳、戊午、己未、庚申、辛酉、壬戌、癸亥、甲子、乙丑
    实际根据年份不同，可查表。此处简化为固定列表（不完全准确）
    """
    day_gan, day_zhi = get_day_ganzhi(date_obj)
    shangshuo_list = [('甲','寅'),('乙','卯'),('丙','辰'),('丁','巳'),('戊','午'),
                      ('己','未'),('庚','申'),('辛','酉'),('壬','戌'),('癸','亥'),
                      ('甲','子'),('乙','丑')]
    return (day_gan, day_zhi) in shangshuo_list

# ==================== 综合检查 ====================

def check_marriage_shensha(date_obj, bride_bazi=None, groom_bazi=None):
    """
    综合检查婚嫁神煞
    返回：(yi_list, ji_list)
    """
    yi_list = []
    ji_list = []
    
    # 1. 检查吉神
    if is_tiande_day(date_obj):
        yi_list.append('天德日')
    if is_yuede_day(date_obj):
        yi_list.append('月德日')
    if is_yuedehe_day(date_obj):
        yi_list.append('月德合日')
    if is_bujiang_day(date_obj):
        yi_list.append('不将日')
    if is_huangdao_day(date_obj):
        yi_list.append('黄道日')
    
    # 2. 检查凶神
    if is_month_break(date_obj):
        ji_list.append('月破')
    
    # 3. 检查夫星、子星（如果有新娘八字）
    if bride_bazi:
        day_gan, day_zhi = get_day_ganzhi(date_obj)
        # 假设新娘八字包含日柱信息
        bride_ri_gan = bride_bazi.get('ri_gan', '')
        if bride_ri_gan:
            fuxing_info = get_fuxing_zixing(bride_ri_gan)
            # 检查夫星冲克
            if day_gan in [fuxing_info['fu'], fuxing_info['qi']]:
                # 这里需要更复杂的冲克判断，暂时简化
                pass
    
    return yi_list, ji_list
