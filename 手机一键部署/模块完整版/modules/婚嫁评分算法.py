# -*- coding: utf-8 -*-
"""
婚嫁日课评分算法优化版（基于《协纪辨方书》）

核心功能：
1. 大利月/小利月检查
2. 一票否决项检查（月破、岁破、上朔日、四离四绝、重丧日、三娘煞）
3. 日课年月日柱内部地支合局评分
4. 夫妻命理互补分析

【彻底分离原则】日课评分不含时柱因素：
日课四柱中的时柱为示例时辰（默认午时），实际用课可另选吉时，
时辰吉凶统一由 modules/shensha/嫁娶神煞扩展.py 的 get_lucky_hours
（十二时辰婚嫁吉凶表）独立评估（冲新娘/冲新郎禁用、合新娘/合新郎、
大黄道、建除、红鸾/天喜/贵人/禄神/五不遇/日破等），
不再计入日课总分，避免示例时柱冲合刑害失真及重复扣分。

评分结构：
- 基础分：60分
- 吉神加分：不将日、天德、月德、黄道日等
- 凶神扣分：三煞、阴胎、阳气、冲夫星、冲子星等
- 地支合局加分：三合局、半合局、六合（仅年月日三柱）
"""

from datetime import date, datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 基础常量 ====================
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 黄道时辰表：以日支为键，值为从子时开始的黄道/黑道列表
# 日支起青龙口诀：子午起于子，丑未起于寅，寅申起于申，卯酉起于寅，辰戌起于辰，巳亥起于巳
# 青龙、明堂、金匮、天德、玉堂、司命为黄道吉时
# 天刑、朱雀、白虎、天牢、玄武、勾陈为黑道凶时
HUANGDAO_SHI_TABLE = {
    # 子午起于子：子时青龙
    '子': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
    '午': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
    # 丑未起于寅：寅时青龙
    '丑': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
    '未': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
    # 寅申起于申：申时青龙
    '寅': ['天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂'],
    '申': ['天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂'],
    # 卯酉起于寅：寅时青龙
    '卯': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
    '酉': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
    # 辰戌起于辰：辰时青龙
    '辰': ['天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂'],
    '戌': ['天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂'],
    # 巳亥起于巳：巳时青龙
    '巳': ['玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎'],
    '亥': ['玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎']
}
HUANGDAO_XING = ['青龙', '明堂', '金匮', '天德', '玉堂', '司命']

# 【单一权威规则源】天乙贵人时辰地支表（正宗口诀）
#   甲戊庚牛羊（丑、未）
#   乙己鼠猴乡（子、申）
#   丙丁猪鸡位（亥、酉）
#   壬癸兔蛇藏（卯、巳）
#   六辛逢马虎（寅、午）
# 修正记录：此前 '庚' 误写为 ['寅','午']（与辛混淆），现更正为 ['丑','未']
TIANYI_GUIREN = {
    '甲': ['丑', '未'],
    '戊': ['丑', '未'],
    '庚': ['丑', '未'],   # 修正：甲戊庚牛羊（此前错配为寅午）
    '乙': ['子', '申'],
    '己': ['子', '申'],
    '丙': ['酉', '亥'],
    '丁': ['酉', '亥'],
    '辛': ['寅', '午'],   # 六辛逢马虎（正确）
    '壬': ['卯', '巳'],
    '癸': ['卯', '巳']
}

def gan_index(gan):
    """天干转索引"""
    return GAN.index(gan)

def zhi_index(zhi):
    """地支转索引"""
    return ZHI.index(zhi)

# ==================== 五行映射 ====================
GAN_WUXING = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土',
              '庚': '金', '辛': '金', '壬': '水', '癸': '水'}

ZHI_WUXING = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
              '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'}

# ==================== 大利月/小利月检查 ====================

def get_liyue_score(bride_year_zhi, lunar_month):
    """
    计算大利月/小利月得分
    
    Args:
        bride_year_zhi: 新娘年支
        lunar_month: 农历月份（1-12）
    
    Returns:
        (score, reason): 得分和原因
    """
    # 大利月口诀：正七迎鸡兔，二八虎和猴，三九蛇共猪，四十龙和狗，牛羊五十一，鼠马六腊月
    # 小利月口诀：鼠马二八月，牛羊四十当，虎猴正七月，兔鸡六腊月，龙狗三九月，蛇猪五十一
    # （与 modules/shensha/嫁娶神煞扩展.py get_li_yue_info 保持单源一致，2026-09-15 修正）
    table = {
        '子': {'dali': [6, 12], 'xiaoli': [2, 8]},
        '午': {'dali': [6, 12], 'xiaoli': [2, 8]},
        '丑': {'dali': [5, 11], 'xiaoli': [4, 10]},
        '未': {'dali': [5, 11], 'xiaoli': [4, 10]},
        '寅': {'dali': [2, 8], 'xiaoli': [1, 7]},
        '申': {'dali': [2, 8], 'xiaoli': [1, 7]},
        '卯': {'dali': [1, 7], 'xiaoli': [6, 12]},
        '酉': {'dali': [1, 7], 'xiaoli': [6, 12]},
        '辰': {'dali': [4, 10], 'xiaoli': [3, 9]},
        '戌': {'dali': [4, 10], 'xiaoli': [3, 9]},
        '巳': {'dali': [3, 9], 'xiaoli': [5, 11]},
        '亥': {'dali': [3, 9], 'xiaoli': [5, 11]}
    }
    info = table.get(bride_year_zhi, {})
    if lunar_month in info.get('dali', []):
        return 30, '大利月'
    if lunar_month in info.get('xiaoli', []):
        return 15, '小利月'
    
    # 检查妨夫月/妨妻月（仅提醒，不否决）
    if bride_year_zhi in ['子', '午']:
        if lunar_month in [3, 9]:
            return -25, '妨夫月'
        elif lunar_month in [9, 3]:
            return -25, '妨妻月'
    return 0, None

# ==================== 阴胎、阳气计算 ====================
# 【典籍口径】（《选择求真·卷五》胎元起例 + 通书“天进一兮地三和”）：
#   阴胎（女命/新娘）：生月月柱 月干顺进 1 位 + 月支顺进 3 位 = 胎元
#   阳气（男命/新郎，婚嫁择日用于判断日课是否“犯阳气”）：
#       生月月柱 月干顺进 1 位 + 月支顺进 3 位（与阴胎同法，男称阳气女称阴胎）
#   说明：旧版阳气误作“干+3支+1”对称公式，无典籍依据，2026-09 按典籍修正。

def get_yintai(month_gan, month_zhi):
    """阴胎（女命）= 月干顺进 1 位 + 月支顺进 3 位（=胎元）"""
    gan_idx = gan_index(month_gan)
    zhi_idx = zhi_index(month_zhi)
    yt_gan = GAN[(gan_idx + 1) % 10]
    yt_zhi = ZHI[(zhi_idx + 3) % 12]
    return yt_gan, yt_zhi

def get_yangqi(month_gan, month_zhi):
    """阳气（男命）= 月干顺进 1 位 + 月支顺进 3 位（与阴胎同法，即胎元）"""
    gan_idx = gan_index(month_gan)
    zhi_idx = zhi_index(month_zhi)
    yq_gan = GAN[(gan_idx + 1) % 10]
    yq_zhi = ZHI[(zhi_idx + 3) % 12]
    return yq_gan, yq_zhi

# ==================== 地支关系判断 ====================

def is_chong(zhi1, zhi2):
    """地支六冲"""
    dui = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
           '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
    return dui.get(zhi1) == zhi2

def is_liuhe(zhi1, zhi2):
    """地支六合"""
    he = {('子', '丑'), ('丑', '子'), ('寅', '亥'), ('亥', '寅'), ('卯', '戌'), ('戌', '卯'),
          ('辰', '酉'), ('酉', '辰'), ('巳', '申'), ('申', '巳'), ('午', '未'), ('未', '午')}
    return (zhi1, zhi2) in he

def is_sanhe(zhi_list):
    """检查是否构成三合局（三个不同地支）"""
    sanhe_groups = [{'申', '子', '辰'}, {'寅', '午', '戌'}, {'巳', '酉', '丑'}, {'亥', '卯', '未'}]
    # 使用 set 去重，确保只有不同的地支才算
    unique_zhis = set(zhi_list) - {None, ''}
    for group in sanhe_groups:
        if group.issubset(unique_zhis):
            return True, list(group)
    return False, None

def is_banhe(zhi_list):
    """检查是否构成半合局（两个不同地支）"""
    sanhe_groups = [{'申', '子', '辰'}, {'寅', '午', '戌'}, {'巳', '酉', '丑'}, {'亥', '卯', '未'}]
    # 使用 set 去重，确保只有不同的地支才算
    unique_zhis = set(zhi_list) - {None, ''}
    for group in sanhe_groups:
        common = unique_zhis & group
        if len(common) == 2:
            return True, list(common)
    return False, None

# ==================== 日课四柱内部合局评分 ====================

def get_zhiju_score(sizhu):
    """
    计算日课四柱内部地支合局得分
    
    Args:
        sizhu: 包含 year_zhi, month_zhi, day_zhi, hour_zhi 的字典
    
    Returns:
        (score, reason): 得分和原因
    """
    zhis = [sizhu['year_zhi'], sizhu['month_zhi'], sizhu['day_zhi'], sizhu['hour_zhi']]
    
    # 检查三合局（三个地支）
    is_sanhe_result, sanhe_zhis = is_sanhe(zhis)
    if is_sanhe_result:
        return 15, f'三合局({",".join(sanhe_zhis)})'
    
    # 检查六合
    liuhe_pairs = [('子', '丑'), ('寅', '亥'), ('卯', '戌'), ('辰', '酉'), ('巳', '申'), ('午', '未')]
    for (a, b) in liuhe_pairs:
        if a in zhis and b in zhis:
            return 10, f'六合({a}{b})'
    
    # 检查半合局
    is_banhe_result, banhe_zhis = is_banhe(zhis)
    if is_banhe_result:
        return 8, f'半合局({",".join(banhe_zhis)})'
    
    return 0, None

# ==================== 夫星、子星计算 ====================

def get_fuxing_zixing_by_year(year_gan, year_zhi=None):
    """女命真夫星/七杀、真天嗣（子星）/伤官完整干支——通书五虎遁起例。

    【典籍口径】以年干为"我"：正官（克我、阴阳异）为真夫星，七杀（克我、
    同阴阳）为偏夫，食神（我生、同阴阳）为真天嗣（子星），伤官（我生、
    阴阳异）为子息偏星。四干地支一律从寅月五虎遁起遁到该干首次临宫之支，
    只随年干变化，与年支无关（《选择求真》卷五嫁娶总集）。
    定局（正官/食神）：甲辛未/丙寅，乙庚辰/丁亥，丙癸巳/戊戌，丁壬寅/己酉，
    戊乙卯/庚申，己甲戌/辛未，庚丁亥/壬午，辛丙申/癸巳，壬己酉/甲辰，
    癸戊午/乙卯。

    Args:
        year_gan: 年柱天干
        year_zhi: 年柱地支（兼容旧签名，不参与计算）

    Returns:
        dict: {'fu':正官干支, 'qi':七杀干支, 'zi':食神干支, 'shang':伤官干支}
    """
    # 天干：克我（官杀）、我生（食伤）
    fuxing_gan_map = {
        '甲': '辛', '乙': '庚', '丙': '癸', '丁': '壬', '戊': '乙',
        '己': '甲', '庚': '丁', '辛': '丙', '壬': '己', '癸': '戊'
    }
    qisha_gan_map = {
        '甲': '庚', '乙': '辛', '丙': '壬', '丁': '癸', '戊': '甲',
        '己': '乙', '庚': '丙', '辛': '丁', '壬': '戊', '癸': '己'
    }
    zixing_gan_map = {
        '甲': '丙', '乙': '丁', '丙': '戊', '丁': '己', '戊': '庚',
        '己': '辛', '庚': '壬', '辛': '癸', '壬': '甲', '癸': '乙'
    }
    shangguan_gan_map = {
        '甲': '丁', '乙': '丙', '丙': '己', '丁': '戊', '戊': '辛',
        '己': '庚', '庚': '癸', '辛': '壬', '壬': '乙', '癸': '甲'
    }
    # 五虎遁年上起月首干
    wuhu_start = {'甲': '丙', '己': '丙', '乙': '戊', '庚': '戊',
                  '丙': '庚', '辛': '庚', '丁': '壬', '壬': '壬',
                  '戊': '甲', '癸': '甲'}

    if year_gan not in GAN:
        return {'fu': '', 'qi': '', 'zi': '', 'shang': ''}

    def _dun_zhi(target_gan):
        """从寅月起遁，target_gan 首次临宫的地支"""
        if target_gan not in GAN:
            return ''
        gi = gan_index(wuhu_start[year_gan])
        zi0 = ZHI.index('寅')
        for i in range(12):
            if GAN[(gi + i) % 10] == target_gan:
                return ZHI[(zi0 + i) % 12]
        return ''

    result = {}
    for key, gan_map in (('fu', fuxing_gan_map), ('qi', qisha_gan_map),
                         ('zi', zixing_gan_map), ('shang', shangguan_gan_map)):
        star_gan = gan_map.get(year_gan, '')
        star_zhi = _dun_zhi(star_gan)
        result[key] = star_gan + star_zhi if star_gan and star_zhi else ''
    return result


def get_fuxing_zixing(day_gan):
    """
    根据日干返回夫星（正官）、七杀、子星（食神）、伤官的完整干支
    
    在八字命理中：
    - 夫星：克日干的五行（官杀），女命以官杀为夫
    - 子星：日干所生的五行（食伤），女命以食伤为子
    
    Returns:
        dict: {'fu':正官干支, 'qi':七杀干支, 'zi':食神干支, 'shang':伤官干支}
    """
    # 天干顺序及阴阳属性（偶数为阳，奇数为阴）
    gan_order = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    gan_yang = ['甲', '丙', '戊', '庚', '壬']  # 阳干
    gan_yin = ['乙', '丁', '己', '辛', '癸']   # 阴干
    
    # 地支顺序及阴阳属性（奇数为阳，偶数为阴）
    zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    zhi_yang = ['子', '寅', '辰', '午', '申', '戌']   # 阳支
    zhi_yin = ['丑', '卯', '巳', '未', '酉', '亥']    # 阴支
    
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
    
    # 五行对应的地支（选择长生或临官位）
    wuxing_zhi_map = {
        '金': {'yang': '申', 'yin': '酉'},  # 金长生在巳，但申酉为金的本气
        '水': {'yang': '子', 'yin': '亥'},  # 水长生在申，子为帝旺
        '木': {'yang': '寅', 'yin': '卯'},  # 木长生在亥，寅卯为木的本气
        '火': {'yang': '午', 'yin': '巳'},  # 火长生在寅，午为帝旺
        '土': {'yang': '辰', 'yin': '丑'},  # 土寄生于火，辰戌丑未
    }
    
    gan_wuxing = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', 
                  '戊': '土', '己': '土', '庚': '金', '辛': '金', 
                  '壬': '水', '癸': '水'}
    
    fu_gan, qi_gan = fuxing_gan_map.get(day_gan, ('', ''))
    zi_gan, shang_gan = zixing_gan_map.get(day_gan, ('', ''))
    
    # 确定夫星地支（根据天干阴阳选择对应阴阳的地支）
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

# ==================== 五行分析 ====================

def calculate_wuxing_distribution(sizhu):
    """
    计算日课四柱的五行分布
    
    Args:
        sizhu: 包含年柱、月柱、日柱、时柱的字典
    
    Returns:
        dict: 五行分数 {'金': x, '木': x, '水': x, '火': x, '土': x}
    """
    wuxing_counts = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    
    # 分析天干
    for gan_key in ['year_gan', 'month_gan', 'day_gan', 'hour_gan']:
        gan = sizhu.get(gan_key, '')
        if gan in GAN_WUXING:
            wuxing_counts[GAN_WUXING[gan]] += 1.0
    
    # 分析地支本气
    for zhi_key in ['year_zhi', 'month_zhi', 'day_zhi', 'hour_zhi']:
        zhi = sizhu.get(zhi_key, '')
        if zhi in ZHI_WUXING:
            wuxing_counts[ZHI_WUXING[zhi]] += 0.8
    
    return wuxing_counts

# ==================== 夫星受克检查 ====================

def check_fuxing_being_ke(bride_bazi, sizhu):
    """
    检查日课中是否存在夫星受克的情况

    2026-09-17 口径统一：夫星一律以新娘【年干】起真夫星（通书《选择求真》
    五虎遁，与日课详情头示"夫星"及 get_fuxing_zixing_by_year 完全一致），
    不再用日干支平法——此前头示夫星按年干（如丙年=癸巳·水）、本检查却按
    日干（如己土日主→木夫星），同一份报告两套夫星自相矛盾（庚午日误判
    "庚金克木夫星"，实则庚金生年干法的水夫星）。

    女命真夫星为克年干的五行（正官）：
    - 年干为木：夫星为金
    - 年干为火：夫星为水
    - 年干为土：夫星为木
    - 年干为金：夫星为火
    - 年干为水：夫星为土

    夫星受克的情况：
    1. 克制夫星的五行过旺（如夫星为水，土旺则克水）
    2. 年命本气太旺耗夫星
    3. 夫星本身太弱
    4. 日课中直接有天干克制夫星

    Args:
        bride_bazi: 新娘八字 {'year_gan': '', ...}
        sizhu: 日课四柱信息

    Returns:
        (score, reason): 扣分和原因
    """
    # 优先年干（通书真夫星口径）；缺年干时回退日干（老数据兼容）
    day_gan = bride_bazi.get('year_gan') or bride_bazi.get('ri_gan')
    if not bride_bazi or not day_gan:
        return 0, None
    day_wuxing = GAN_WUXING.get(day_gan, '')
    
    # 夫星五行：克日主的五行
    fuxing_wuxing_map = {
        '木': '金',  # 金克木
        '火': '水',  # 水克火
        '土': '木',  # 木克土
        '金': '火',  # 火克金
        '水': '土'   # 土克水
    }
    
    fuxing_wuxing = fuxing_wuxing_map.get(day_wuxing, '')
    if not fuxing_wuxing:
        return 0, None
    
    # 克制夫星的五行
    ke_fuxing_wuxing_map = {
        '金': '火',  # 火克金
        '水': '土',  # 土克水
        '木': '金',  # 金克木
        '火': '水',  # 水克火
        '土': '木'   # 木克土
    }
    
    ke_fuxing_wuxing = ke_fuxing_wuxing_map.get(fuxing_wuxing, '')
    
    # 计算日课五行分布
    wuxing_counts = calculate_wuxing_distribution(sizhu)
    ke_fuxing_count = wuxing_counts.get(ke_fuxing_wuxing, 0)
    fuxing_count = wuxing_counts.get(fuxing_wuxing, 0)
    day_wuxing_count = wuxing_counts.get(day_wuxing, 0)
    
    # 判断夫星受克程度
    score = 0
    reason = None
    
    # 情况1：检查日课中是否有天干直接克制夫星五行
    # 获取日课中的所有天干
    day_gan_ke = False
    ke_gan_list = []
    for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
        pillar = sizhu.get(pillar_name, '')
        if len(pillar) >= 1:
            gan = pillar[0]
            gan_wuxing = GAN_WUXING.get(gan, '')
            if gan_wuxing == ke_fuxing_wuxing:
                day_gan_ke = True
                ke_gan_list.append(f'{pillar_name}{gan}')
    
    # 如果有克制夫星的天干，扣分
    if day_gan_ke:
        if fuxing_count < 1.0:
            score = -20
            reason = f'夫星受克（{ke_fuxing_wuxing}天干{",".join(ke_gan_list)}克制{fuxing_wuxing}夫星，夫星弱）'
        elif len(ke_gan_list) >= 2:
            # 多重克制（2个及以上天干克制夫星）加重扣分
            score = -20
            reason = f'夫星受克（{ke_fuxing_wuxing}天干{",".join(ke_gan_list)}多重克制{fuxing_wuxing}夫星）'
        elif ke_fuxing_count > 1.5:
            score = -15
            reason = f'夫星稍受克（{ke_fuxing_wuxing}天干{",".join(ke_gan_list)}克制{fuxing_wuxing}夫星）'
        else:
            score = -10
            reason = f'夫星微受克（{ke_fuxing_wuxing}天干{",".join(ke_gan_list)}克制{fuxing_wuxing}夫星）'
    
    # 情况2：克制夫星的五行过旺（如果还没有扣分）
    if not reason:
        if ke_fuxing_count > 2.5 and fuxing_count < 1.0:
            score = -25
            reason = f'夫星受克（{ke_fuxing_wuxing}旺{ke_fuxing_count:.1f}，{fuxing_wuxing}弱{fuxing_count:.1f}）'
        elif ke_fuxing_count > 1.5 and fuxing_count < 0.8:
            score = -15
            reason = f'夫星稍受克（{ke_fuxing_wuxing}较旺{ke_fuxing_count:.1f}）'
    
    # 情况3：日主太旺耗夫星
    if not reason:
        if day_wuxing_count > 3.0 and fuxing_count < 1.0:
            score = -20
            reason = (f'日主较旺耗夫星（日课{day_wuxing}元素强度{day_wuxing_count:.1f}，'
                      f'夫星{fuxing_wuxing}偏弱仅{fuxing_count:.1f}，'
                      f'{day_wuxing}过旺则{fuxing_wuxing}夫星不得力）')
    
    # 情况4：夫星本身太弱
    if not reason:
        if fuxing_count < 0.3:
            score = -10
            reason = f'夫星偏弱（{fuxing_wuxing}不足{fuxing_count:.1f}）'
    
    return score, reason

# ==================== 六害、三刑检查 ====================

def check_liuhai_penalty(sizhu):
    """
    检查六害并扣分
    
    Args:
        sizhu: 四柱信息
        
    Returns:
        (score, reasons): 扣分和原因列表
    """
    total_penalty = 0
    reasons = []
    
    # 六害关系
    liuhai_pairs = [('子', '未'), ('丑', '午'), ('寅', '巳'), 
                    ('卯', '辰'), ('申', '亥'), ('酉', '戌')]
    
    # 获取所有地支
    zhis = [
        ('年柱', sizhu.get('year_zhi', '')),
        ('月柱', sizhu.get('month_zhi', '')),
        ('日柱', sizhu.get('day_zhi', '')),
        ('时柱', sizhu.get('hour_zhi', ''))
    ]
    
    # 检查每一对地支
    for i in range(len(zhis)):
        for j in range(i + 1, len(zhis)):
            z1_name, z1 = zhis[i]
            z2_name, z2 = zhis[j]
            if z1 and z2:
                if (z1, z2) in liuhai_pairs or (z2, z1) in liuhai_pairs:
                    total_penalty -= 5  # 每处六害扣5分
                    reasons.append(f"六害: {z1_name}{z1}害{z2_name}{z2}")
    
    return total_penalty, reasons

def check_sanxing_penalty(sizhu):
    """
    检查三刑并扣分
    
    Args:
        sizhu: 四柱信息
        
    Returns:
        (score, reasons): 扣分和原因列表
    """
    total_penalty = 0
    reasons = []
    
    # 三刑关系（刑名勘正：寅巳申=无恩之刑（寅刑巳巳刑申申刑寅），丑戌未=恃势之刑）
    sanxing_groups = [
        (['寅', '巳', '申'], '无恩之刑'),
        (['丑', '戌', '未'], '恃势之刑'),
        (['子', '卯'], '无礼之刑')
    ]
    
    # 获取所有地支
    zhi_list = [
        sizhu.get('year_zhi', ''),
        sizhu.get('month_zhi', ''),
        sizhu.get('day_zhi', ''),
        sizhu.get('hour_zhi', '')
    ]
    zhi_list = [z for z in zhi_list if z]  # 过滤空值
    
    # 获取所有带名称的地支
    zhis_with_name = [
        ('年柱', sizhu.get('year_zhi', '')),
        ('月柱', sizhu.get('month_zhi', '')),
        ('日柱', sizhu.get('day_zhi', '')),
        ('时柱', sizhu.get('hour_zhi', ''))
    ]
    
    # 检查每一组三刑（三刑局须组内地支齐备方成局：寅巳申/丑戌未须三支全现，
    # 仅两支为相刑未成局不扣分，如巳申两支刑合并见只计六合；子卯无礼之刑两支即成）
    for group, name in sanxing_groups:
        # 获取该组中存在的不同地支
        present_zhis = set(z for z in zhi_list if z in group)
        if len(present_zhis) >= len(group):
            # 找到对应的地支
            matching_zhis = [f"{z_name}{z}" for z_name, z in zhis_with_name if z in present_zhis]
            total_penalty -= 8  # 三刑扣8分
            reasons.append(f"三刑({name}): {', '.join(matching_zhis)}")
    
    # 检查自刑
    zixing_zhi = ['辰', '午', '酉', '亥']
    from collections import Counter
    zhi_counter = Counter(zhi_list)
    for zhi in zixing_zhi:
        if zhi_counter.get(zhi, 0) >= 2:
            matching_zhis = [f"{z_name}{z}" for z_name, z in zhis_with_name if z == zhi]
            total_penalty -= 6  # 自刑扣6分
            reasons.append(f"自刑: {', '.join(matching_zhis)}")
    
    return total_penalty, reasons

# ==================== 一票否决项检查 ====================

def is_month_break(date_obj, sizhu):
    """月破：月支冲日支"""
    return is_chong(sizhu['month_zhi'], sizhu['day_zhi'])

def is_year_break(date_obj, sizhu):
    """岁破：日支冲年支"""
    return is_chong(sizhu['day_zhi'], sizhu['year_zhi'])

def is_shangshuo(date_obj, sizhu):
    """上朔日（阳年干+3取亥日、阴年干+4取巳日）

    2026-09-20 收敛：原本地年干推算已下沉为 shensha 层唯一实现
    神煞基类.is_shangshuo_by_ganzhi，本函数改委托（算法逐字等价，
    下方 -35 扣分分支行为与命中集合不变；非婚嫁 pipeline 同源自 -10，
    事项差按用户拍板A保留）。
    """
    try:
        from .shensha.神煞基类 import is_shangshuo_by_ganzhi
    except ImportError:
        from modules.shensha.神煞基类 import is_shangshuo_by_ganzhi
    day_gan, day_zhi = sizhu['日柱'][0], sizhu['日柱'][1]
    return is_shangshuo_by_ganzhi(sizhu['year_gan'], day_gan, day_zhi)

def is_sili_sijue(date_obj):
    """四离四绝（四离=二分二至前一日；四绝=四立前一日）

    2026-09-20 修复：原桩 return False 恒假（"简化版"待实现），导致下方
    四离四绝扣分分支全年不可达。现委托 shensha 层 sxtwl 精确判定，
    保持单一实现路径（与 marriage_shensha.is_sili_sijue 同源）。
    """
    try:
        from .shensha.marriage_shensha import is_sili_sijue as _impl
    except ImportError:
        from modules.shensha.marriage_shensha import is_sili_sijue as _impl
    return _impl(date_obj)

def is_sansang(date_obj):
    """重丧日（按规则判断）

    规则（按农历月份）：
    - 正月（寅月）：庚日
    - 二月（卯月）：辛日
    - 三月（辰月）：戊日
    - 四月（巳月）：丙日
    - 五月（午月）：丁日
    - 六月（未月）：己日
    - 七月（申月）：甲日
    - 八月（酉月）：乙日
    - 九月（戌月）：戊日
    - 十月（亥月）：壬日
    - 十一月（子月）：癸日
    - 十二月（丑月）：己日
    """
    day_gan, _ = get_day_ganzhi(date_obj)

    try:
        from modules.四柱计算器 import get_lunar_date
        lunar_info = get_lunar_date(date_obj)
        if lunar_info and 'month' in lunar_info:
            lunar_month_name = lunar_info['month']
            zhongsang_map = {
                '正月': ['庚'], '二月': ['辛'], '三月': ['戊'], '四月': ['丙'],
                '五月': ['丁'], '六月': ['己'], '七月': ['甲'], '八月': ['乙'],
                '九月': ['戊'], '十月': ['壬'], '十一月': ['癸'], '十二月': ['己'],
                '腊月': ['己']
            }
            return day_gan in zhongsang_map.get(lunar_month_name, [])
    except Exception as e:
        logger.error(f"获取农历月份失败: {e}")

    return False

def is_sanniangsha(date_obj):
    """真三娘煞：农历日期与日干支同时满足特定条件（全年仅6天）

    真三娘煞对照：初三逢庚午、初七逢辛未、十三逢戊申、十八逢己酉、
    廿二逢丙午、廿七逢丁未。
    仅农历日相符而干支不符的"假三娘煞"（每月固定6天）不再作为婚嫁禁忌。
    注意：三娘煞按农历日期判断，不是公历日期。
    闰月不计（2026-09-20 通用规则，与杨公忌/红纱口径一致）。
    """
    ZHEN_SANNIANG_MAP = {3: '庚午', 7: '辛未', 13: '戊申', 18: '己酉', 22: '丙午', 27: '丁未'}

    try:
        from modules.四柱计算器 import get_lunar_date
        lunar_info = get_lunar_date(date_obj)
        if lunar_info:
            # 闰月不计（get_lunar_date 的 month 已含'闰'前缀，如'闰六月'）
            if '闰' in str(lunar_info.get('month', '')):
                return False
            if 'day' in lunar_info:
                # 解析中文日期为数字
                day_map = {
                    '初一': 1, '初二': 2, '初三': 3, '初四': 4, '初五': 5,
                    '初六': 6, '初七': 7, '初八': 8, '初九': 9, '初十': 10,
                    '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
                    '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
                    '廿一': 21, '廿二': 22, '廿三': 23, '廿四': 24, '廿五': 25,
                    '廿六': 26, '廿七': 27, '廿八': 28, '廿九': 29, '三十': 30
                }
                lunar_day = day_map.get(lunar_info['day'], 0)
                if lunar_day in ZHEN_SANNIANG_MAP:
                    day_gan, day_zhi = get_day_ganzhi(date_obj)
                    return (day_gan + day_zhi) == ZHEN_SANNIANG_MAP[lunar_day]
    except Exception as e:
        logger.error(f"判断三娘煞失败: {e}")

    return False

def check_reject_items(date_obj, sizhu):
    """
    检查一票否决项（真正的绝对禁忌）
    
    注意：月破、上朔日、四离四绝已改为高扣分项（非绝对否决），
    这些日子虽凶但有制化可用，不再一票否决。
    保留的绝对否决项：岁破（日支冲年支）、重丧日、真三娘煞
    """
    if is_year_break(date_obj, sizhu):
        return True, '岁破（日支冲年支）'
    if is_sansang(date_obj):
        return True, '重丧日'
    if is_sanniangsha(date_obj):
        return True, '真三娘煞'
    return False, None

# ==================== 时辰评分（已移除） ====================
# 【彻底分离】原 get_shichen_score（黄道时/天乙贵人时/五不遇时/时支与新娘新郎
# 冲合评分）已删除，不再计入日课总分：
# 1. 日课四柱中的时柱为示例时辰（默认午时），实际用课可另选吉时，
#    用示例时柱冲新娘生肖扣50分等属于对日课的误伤；
# 2. 时辰吉凶统一由 modules/shensha/嫁娶神煞扩展.py 的 get_lucky_hours
#    （十二时辰婚嫁吉凶表）独立评估：冲新娘/冲新郎→禁用、合新娘/合新郎+10、
#    三合+12、大黄道±20、建除±8、红鸾+15、天喜+12、贵人+15、禄神+10、
#    五不遇-15、日破→禁用，信息完整不丢失。
# HUANGDAO_SHI_TABLE、TIANYI_GUIREN 常量保留，作为与 modules/黄道.py、
# modules/shensha/通用神煞.py 规则对齐的参照源。

# ==================== 辅助函数 ====================

def get_day_ganzhi(date_obj):
    """根据公历日期计算日干支"""
    try:
        from .四柱计算器 import calculate_sizhu
    except ImportError:
        from 四柱计算器 import calculate_sizhu
    sizhu = calculate_sizhu(date_obj, 12, 0)
    day_gan = sizhu['日柱'][0]
    day_zhi = sizhu['日柱'][1]
    return day_gan, day_zhi

def get_lunar_month_from_solar(date_obj):
    """从公历日期获取农历月份（简化版）"""
    # 实际应使用农历转换库
    try:
        import sxtwl
        lunar = sxtwl.fromSolar(date_obj.year, date_obj.month, date_obj.day)
        return lunar.getLunarMonth()
    except:
        # 简化：直接返回公历月份作为农历月份
        return date_obj.month

# ==================== 主评分函数 ====================

def score_marriage_day(date_obj, bride_bazi=None, groom_bazi=None, hour=12):
    """
    婚嫁日课评分主函数
    
    Args:
        date_obj: datetime.date 对象
        bride_bazi: 新娘八字字典 {'year_zhi': '', 'ri_gan': '', 'ri_zhi': '', ...}
        groom_bazi: 新郎八字字典 {'ri_gan': '', 'ri_zhi': '', ...}
        hour: 时辰（0-23，默认中午12时）
    
    Returns:
        dict: 评分结果
    """
    result = {
        'score': 0,
        'level': '',
        'reason': '',
        'details': [],
        'reject_reason': None,
        'warnings': []
    }
    
    # 计算四柱
    try:
        from .四柱计算器 import calculate_sizhu
    except ImportError:
        from 四柱计算器 import calculate_sizhu
    
    # 计算日课四柱（使用指定时辰）
    sizhu = calculate_sizhu(date_obj, hour, 0)
    
    # 提取四柱信息
    sizhu['year_zhi'] = sizhu['年柱'][1]
    sizhu['month_zhi'] = sizhu['月柱'][1]
    sizhu['day_zhi'] = sizhu['日柱'][1]
    sizhu['hour_zhi'] = sizhu['时柱'][1]
    sizhu['hour_gan'] = sizhu['时柱'][0]
    
    # 1. 检查一票否决项
    # 2026-09-17 透明度修复：否决日不再提前返回空明细。此前一旦命中（重丧日/岁破/
    # 真三娘煞）直接 return，details=[]，导致日课详情【评分详情】的五行评分无任何
    # 分项（基础分/利月/神煞/合局全丢）、月令也无旺衰明细，与"各项扣分项已完整
    # 显示用于对比"的说明自相矛盾。现继续完整计算全部 details（分数仅供追溯），
    # 调用方（评分器）据 reject_reason 把总分强制归零。
    is_reject, reject_reason = check_reject_items(date_obj, sizhu)
    if is_reject:
        result['reject_reason'] = reject_reason
    
    # 2. 基础分
    score = 60
    details = [('基础分', 60)]
    
    # 3. 大利月/小利月评分
    liyue_score = 0
    if bride_bazi and bride_bazi.get('year_zhi'):
        lunar_month = get_lunar_month_from_solar(date_obj)
        liyue_score, liyue_reason = get_liyue_score(bride_bazi['year_zhi'], lunar_month)
        if liyue_reason:
            score += liyue_score
            details.append((liyue_reason, liyue_score))
            if liyue_score < 0:
                result['warnings'].append(f"{liyue_reason}")
    
    # 4. 神煞评分
    try:
        from .shensha.marriage_shensha import (
            is_tiande_day, is_yuede_day, is_bujiang_day, is_huangdao_day,
            is_sansha, get_fuxing_zixing, is_tiangang_day, is_hekui_day,
            is_da_huangdao_day, is_xiao_huangdao_day, get_jianchu
        )
        
        # 吉神加分
        if is_bujiang_day(date_obj):
            # 2026-10 A6-4 批B：布尔从 D 取（is_bujiang_day → 神煞基类唯一表），
            # 分值改查 事项标准.SHENSHA_SCORES 单一表（('嫁娶','不将日')=15），
            # 替代原硬编码 +25 —— 该 25 为全项目唯一离群值（神煞层各注册点与
            # 12 事项 SHENSHA_SCORES 均为 15），本处硬编码使嫁娶总分相对其它
            # 事项漂移 10 分。
            try:
                from .事项标准 import shensha_score as _shensha_score
            except ImportError:
                from 事项标准 import shensha_score as _shensha_score
            _bujiang_score = _shensha_score('嫁娶', '不将日', 15)
            score += _bujiang_score
            details.append(('不将日', _bujiang_score))
        
        if is_tiande_day(date_obj):
            score += 15  # 天德
            details.append(('天德', 15))
        
        if is_yuede_day(date_obj):
            score += 15  # 月德
            details.append(('月德', 15))
        
        # 大黄道（十二神值日）/小黄道（建除十二神）计分
        # 2026-02-05 统一口径：分值一律取自黄道模块（modules/黄道.py），与详情页
        # 【黄道信息】显示完全一致——大黄道青龙/明堂/天德/玉堂+15、金匮/司命+10、
        # 六黑道-15；小黄道吉（除/定/执/危/成/开）+5、凶（建/满/平/破/收/闭）-10。
        # 建星对嫁娶另有宜忌：除/危/执虽黄道为吉却忌嫁娶，按-5计。
        try:
            from .黄道 import calculate_huangdao as _calc_hd
        except ImportError:
            try:
                from 黄道 import calculate_huangdao as _calc_hd
            except ImportError:
                _calc_hd = None
        _hd = _calc_hd(sizhu) if _calc_hd else {}
        _hd = _hd or {}
        _da = _hd.get('da_huang_dao') or {}
        _da_name = _da.get('name', '')
        if _da.get('type') == '吉':
            _da_score = int(_da.get('score', 10) or 10)
            score += _da_score  # 大黄道吉日（司命/金匮+10，青龙/明堂/天德/玉堂+15）
            details.append((f'大黄道{_da_name}日（黄道吉日）', _da_score))
        else:
            score -= 15  # 六黑道凶日
            details.append((f'大黄道{_da_name}黑道日', -15))

        # 小黄道（建除）：吉建星+5、凶建星-10；除/危/执虽吉但嫁娶忌-5
        _xo = _hd.get('xiao_huang_dao') or {}
        _xn = _xo.get('name', '') or (get_jianchu(date_obj) if is_xiao_huangdao_day(date_obj) else '')
        _jianchu_ji = {'除', '危', '执'}                 # 黄道为吉但嫁娶忌
        _jianchu_xiong = {'建', '满', '平', '破', '收', '闭'}  # 黑道凶日
        if _xn in _jianchu_ji:
            score -= 5
            details.append((f'小黄道{_xn}日忌嫁娶', -5))
        elif _xn in _jianchu_xiong:
            score -= 10
            details.append((f'小黄道{_xn}日（黑道凶日）', -10))
        elif _xn:  # 定/成/开等宜嫁娶的黄道吉日
            _xo_score = int(_xo.get('score', 5) or 5)
            score += _xo_score
            details.append((f'小黄道{_xn}日（宜嫁娶）', _xo_score))
        
        # 凶神扣分（新娘本命三煞：申子辰煞南巳午未、寅午戌煞北亥子丑、
        # 亥卯未煞西申酉戌、巳酉丑煞东寅卯辰；组内依次为劫煞/灾煞/月煞。
        # 真假三煞：三煞日天干克新娘年干＝真三煞，大凶-25宜避；
        # 日干不克年干且得天德/月德化解＝假三煞，-10有吉神解厄可酌情；
        # 不克但无吉神化解＝本命三煞，仍按-25）
        if bride_bazi and bride_bazi.get('year_zhi'):
            if is_sansha(date_obj, bride_bazi['year_zhi']):
                ny_zhi = bride_bazi['year_zhi']
                ny_gan = bride_bazi.get('year_gan', '')
                sd_gan, sd_zhi = get_day_ganzhi(date_obj)
                sha_fang = {'巳': '南', '午': '南', '未': '南', '亥': '北', '子': '北', '丑': '北',
                            '申': '西', '酉': '西', '戌': '西', '寅': '东', '卯': '东', '辰': '东'}.get(sd_zhi, '')
                sha_ming = {'巳': '劫煞', '午': '灾煞', '未': '月煞', '亥': '劫煞', '子': '灾煞', '丑': '月煞',
                            '申': '劫煞', '酉': '灾煞', '戌': '月煞', '寅': '劫煞', '卯': '灾煞', '辰': '月煞'}.get(sd_zhi, '')
                GAN_WX = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
                          '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
                ke_map = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
                zhen = bool(ny_gan and sd_gan in GAN_WX and ny_gan in GAN_WX
                            and ke_map[GAN_WX[sd_gan]] == GAN_WX[ny_gan])
                if zhen:
                    penalty = -25
                    label = (f"真三煞【{sha_ming}·煞{sha_fang}，扣{penalty}分】：新娘年命{ny_zhi}本命三煞，"
                             f"日支{sd_zhi}犯{sha_ming}，日干{sd_gan}克年干{ny_gan}（"
                             f"{GAN_WX.get(sd_gan,'?')}克{GAN_WX.get(ny_gan,'?')}），大凶宜避")
                elif is_tiande_day(date_obj) or is_yuede_day(date_obj):
                    penalty = -10
                    _jie = '、'.join([n for n, f in (('天德', is_tiande_day), ('月德', is_yuede_day)) if f(date_obj)])
                    # 2026-09-03 用户问题3修正：假三煞判定的制化条件（日干不克年干+得吉神化解）
                    # 明确写入本段标签，不再与"庚日主失令（月令分析段）"同段混排，避免阅读时
                    # 把月令判断"日主失令"误读为假三煞的归属依据。
                    _ke_rel = (f"{GAN_WX.get(sd_gan,'?')}不克{GAN_WX.get(ny_gan,'?')}"
                               if ny_gan and sd_gan in GAN_WX and ny_gan in GAN_WX and
                                  ke_map[GAN_WX[sd_gan]] != GAN_WX[ny_gan]
                               else f"日干{sd_gan}不克年干{ny_gan or '未知'}")
                    label = (f"假三煞【{sha_ming}·煞{sha_fang}，扣{penalty}分】：新娘年命{ny_zhi}本命三煞，"
                             f"日支{sd_zhi}犯{sha_ming}；判为'假'的两项依据："
                             f"①{_ke_rel}（真三煞需日干克年干），②得{_jie}化解。属有吉神解厄，可酌情")
                else:
                    penalty = -25
                    label = (f"本命三煞【{sha_ming}·煞{sha_fang}，扣{penalty}分】：新娘年命{ny_zhi}本命三煞，"
                             f"日支{sd_zhi}犯{sha_ming}，日干{sd_gan}不克年干{ny_gan or '未知'}且无吉神化解")
                score += penalty
                details.append((label, penalty))
        
        # 日支冲新娘生肖（年支）- 大凶
        # 2026-09-17 用户口径：日支之冲无法靠换吉时化解（时支冲由时辰表判禁用），
        # 日辰冲新娘本命/阴胎/阳气升为一票否决（-45/-30 明细仍保留供追溯）。
        _day_clash_veto = []
        if bride_bazi and bride_bazi.get('year_zhi'):
            day_gan, day_zhi = get_day_ganzhi(date_obj)
            if is_chong(day_zhi, bride_bazi['year_zhi']):
                score -= 45  # 日支冲新娘生肖
                details.append(('日支冲新娘生肖', -45))
                result['warnings'].append(f"日支{day_zhi}冲新娘生肖{bride_bazi['year_zhi']}")
                _day_clash_veto.append(f'日支{day_zhi}冲新娘本命{bride_bazi["year_zhi"]}')
        
        # 天罡日（妨翁）检查 - 嫁娶大忌
        if is_tiangang_day(date_obj):
            score -= 40  # 天罡日，妨翁
            details.append(('天罡日（妨翁）', -40))
            result['warnings'].append("天罡日：对新郎父亲不利")
        
        # 河魁日（妨姑）检查 - 嫁娶大忌
        if is_hekui_day(date_obj):
            score -= 40  # 河魁日，妨姑
            details.append(('河魁日（妨姑）', -40))
            result['warnings'].append("河魁日：对新郎母亲不利")
        
        # 夫星、子星检查（年干通书口径，与头示"夫星/子星"一致）
        if bride_bazi and bride_bazi.get('year_gan'):
            day_gan, day_zhi = get_day_ganzhi(date_obj)
            fuxing_info = get_fuxing_zixing_by_year(bride_bazi['year_gan'])

            # 冲夫星：日支冲真夫星（完整干支）的地支，如丙年夫星癸巳，日支亥冲巳
            fu_gz = fuxing_info.get('fu', '')
            if len(fu_gz) >= 2:
                fu_zhi = fu_gz[1]
                if is_chong(day_zhi, fu_zhi):
                    score -= 35
                    details.append((f'冲夫星（日支{day_zhi}冲真夫星{fu_gz}）', -35))

            # 冲子星：日支冲真子星（完整干支）的地支，如丙年子星戊戌，日支辰冲戌
            zi_gz = fuxing_info.get('zi', '')
            if len(zi_gz) >= 2:
                zi_zhi = zi_gz[1]
                if is_chong(day_zhi, zi_zhi):
                    score -= 20
                    details.append((f'冲子星（日支{day_zhi}冲真子星{zi_gz}）', -20))

        # 阴胎 / 阳气 检查（只依赖双方生月月柱，独立于新娘日柱 ri_gan）
        # 典籍（《协纪辨方书》嫁娶："日时勿冲犯阴胎阳气"）：日支与胎元地支六冲各-30；
        # 时支冲不入日课总分，由【十二时辰婚嫁吉凶】表判该时辰禁用。
        day_gan_ty, day_zhi_ty = get_day_ganzhi(date_obj)
        _b_yue_gan = (bride_bazi or {}).get('yue_gan') or (bride_bazi or {}).get('month_gan')
        _b_yue_zhi = (bride_bazi or {}).get('yue_zhi') or (bride_bazi or {}).get('month_zhi')
        if _b_yue_gan and _b_yue_zhi:
            yintai_gan, yintai_zhi = get_yintai(_b_yue_gan, _b_yue_zhi)
            if is_chong(day_zhi_ty, yintai_zhi):
                score -= 30
                details.append((f'犯阴胎（日支{day_zhi_ty}冲阴胎{yintai_gan}{yintai_zhi}）', -30))
                _day_clash_veto.append(f'日支{day_zhi_ty}冲阴胎{yintai_gan}{yintai_zhi}')

        _g_yue_gan = (groom_bazi or {}).get('yue_gan') or (groom_bazi or {}).get('month_gan')
        _g_yue_zhi = (groom_bazi or {}).get('yue_zhi') or (groom_bazi or {}).get('month_zhi')
        if _g_yue_gan and _g_yue_zhi:
            yangqi_gan, yangqi_zhi = get_yangqi(_g_yue_gan, _g_yue_zhi)
            if is_chong(day_zhi_ty, yangqi_zhi):
                score -= 30
                details.append((f'犯阳气（日支{day_zhi_ty}冲阳气{yangqi_gan}{yangqi_zhi}）', -30))
                _day_clash_veto.append(f'日支{day_zhi_ty}冲阳气{yangqi_gan}{yangqi_zhi}')

        # 日支冲新娘本命/阴胎/阳气 → 一票否决（与前置 check_reject_items 的硬忌并列）
        if _day_clash_veto:
            _joined = '、'.join(_day_clash_veto)
            _prev_rr = result.get('reject_reason')
            result['reject_reason'] = f'{_prev_rr}、{_joined}' if _prev_rr else _joined

    except Exception as e:
        logger.warning(f"神煞计算异常: {e}")
    
    # 4.5 传统凶煞扣分（原为一票否决，现改为高扣分项）
    # 月破（-40分）
    if is_month_break(date_obj, sizhu):
        score -= 40
        details.append(('月破', -40))
        result['warnings'].append('月破：月支冲日支，大凶之日，慎用')
    
    # 上朔日（-35分）
    if is_shangshuo(date_obj, sizhu):
        score -= 35
        details.append(('上朔日', -35))
        result['warnings'].append('上朔日：阴阳德俱尽，慎用')
    
    # 四离四绝（-35分，2026-09-20 与事项标准.py SHENSHA_SCORES 对齐：原-30为漂移值；
    # 同日桩函数修复后本分支自全年不可达恢复为 8 天可达）
    if is_sili_sijue(date_obj):
        score -= 35
        details.append(('四离四绝', -35))
        result['warnings'].append('四离四绝：节气转换期，慎用')
    
    # 4.6 夫星受克检查
    if bride_bazi and bride_bazi.get('ri_gan'):
        fuxing_ke_score, fuxing_ke_reason = check_fuxing_being_ke(bride_bazi, sizhu)
        if fuxing_ke_score != 0 and fuxing_ke_reason:
            score += fuxing_ke_score
            details.append((fuxing_ke_reason, fuxing_ke_score))
            if fuxing_ke_score < -30:
                result['warnings'].append(f"严重警告：{fuxing_ke_reason}")
    
    # 4.6 六害检查（排除示例时柱：时辰可换，时柱层面由十二时辰吉凶表独立评估）
    sizhu_no_hour = dict(sizhu)
    sizhu_no_hour['hour_zhi'] = ''
    liuhai_score, liuhai_reasons = check_liuhai_penalty(sizhu_no_hour)
    if liuhai_score != 0:
        score += liuhai_score
        for reason in liuhai_reasons:
            details.append((reason, -5))  # 每处六害扣5分
    
    # 4.7 三刑检查（排除示例时柱）
    sanxing_score, sanxing_reasons = check_sanxing_penalty(sizhu_no_hour)
    if sanxing_score != 0:
        score += sanxing_score
        for reason in sanxing_reasons:
            # 根据内容确定扣分
            if '无恩之刑' in reason or '恃势之刑' in reason or '无礼之刑' in reason:
                details.append((reason, -8))
            elif '自刑' in reason:
                details.append((reason, -6))
    
    # 5. 日课年月日柱内部合局评分（排除示例时柱）
    zhiju_score, zhiju_reason = get_zhiju_score(sizhu_no_hour)
    if zhiju_reason:
        score += zhiju_score
        details.append((zhiju_reason, zhiju_score))
    
    # 6. 时辰评分已移除（彻底分离）：日课评分不含时柱因素，
    #    时辰吉凶由十二时辰婚嫁吉凶表（嫁娶神煞扩展.get_lucky_hours）独立评估
    
    # 7. 计算总分并确定等级
    result['raw_score'] = score          # 明细合计（可能为负），供展示层说明归零
    result['score'] = max(0, score)
    result['details'] = details
    
    # 等级映射
    if result['score'] >= 150:
        result['level'] = '★★★★★ 上吉'
    elif result['score'] >= 130:
        result['level'] = '★★★★ 大吉'
    elif result['score'] >= 110:
        result['level'] = '★★★ 吉'
    elif result['score'] >= 90:
        result['level'] = '★★ 次吉'
    elif result['score'] >= 70:
        result['level'] = '★ 平'
    else:
        result['level'] = '❌ 凶'
    
    # 生成理由文本
    positive = [f"{d[0]}" for d in details if d[1] > 0]
    negative = [f"{d[0]}" for d in details if d[1] < 0]
    
    reason_parts = []
    if positive:
        reason_parts.append('；'.join(positive))
    if negative:
        reason_parts.append(f"忌：{'；'.join(negative)}")
    
    result['reason'] = '；'.join(reason_parts) if reason_parts else '普通日课'

    # 否决日：明细完整保留供追溯，但等级强制为凶、理由前置否决原因
    # 日支冲新娘本命/阴胎/阳气等否决项在第4节才写入 result['reject_reason']，此处回读
    reject_reason = result.get('reject_reason') or reject_reason
    is_reject = bool(reject_reason)
    if is_reject:
        result['level'] = '❌ 凶'
        result['reason'] = f'【一票否决：{reject_reason}】' + result['reason']
    
    # 添加四柱信息到结果中，供后续处理使用
    result['sizhu'] = sizhu
    
    return result

# ==================== 测试函数 ====================

def test_score_marriage():
    """测试婚嫁评分"""
    test_date = date(2023, 1, 9)
    
    # 模拟新娘八字
    bride_bazi = {
        'year_zhi': '卯',
        'ri_gan': '丁',
        'ri_zhi': '卯'
    }
    
    # 模拟新郎八字
    groom_bazi = {
        'ri_gan': '庚',
        'ri_zhi': '酉'
    }
    
    result = score_marriage_day(test_date, bride_bazi, groom_bazi)
    print("婚嫁日课评分测试结果：")
    print(f"日期：{test_date}")
    print(f"评分：{result['score']}")
    print(f"等级：{result['level']}")
    print(f"理由：{result['reason']}")
    print(f"详情：{result['details']}")
    print(f"警告：{result['warnings']}")

if __name__ == '__main__':
    test_score_marriage()
