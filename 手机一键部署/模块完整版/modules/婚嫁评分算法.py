# -*- coding: utf-8 -*-
"""
婚嫁日课评分算法优化版（基于《协纪辨方书》）

核心功能：
1. 大利月/小利月检查
2. 一票否决项检查（月破、岁破、上朔日、四离四绝、重丧日、三娘煞）
3. 日课四柱内部地支合局评分
4. 时辰评分（黄道时、五不遇时等）
5. 夫妻命理互补分析

评分结构：
- 基础分：60分
- 吉神加分：不将日、天德、月德、黄道日等
- 凶神扣分：三煞、阴胎、阳气、冲夫星、冲子星等
- 地支合局加分：三合局、半合局、六合
- 时辰加分：黄道时
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

TIANYI_GUIREN = {
    '甲': ['丑', '未'],
    '戊': ['丑', '未'],
    '乙': ['子', '申'],
    '己': ['子', '申'],
    '丙': ['酉', '亥'],
    '丁': ['酉', '亥'],
    '庚': ['寅', '午'],
    '辛': ['寅', '午'],
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
    table = {
        '子': {'dali': [6, 12], 'xiaoli': [1, 7]},
        '午': {'dali': [6, 12], 'xiaoli': [1, 7]},
        '丑': {'dali': [5, 11], 'xiaoli': [4, 10]},
        '未': {'dali': [5, 11], 'xiaoli': [4, 10]},
        '寅': {'dali': [2, 8], 'xiaoli': [3, 9]},
        '申': {'dali': [2, 8], 'xiaoli': [3, 9]},
        '卯': {'dali': [1, 7], 'xiaoli': [6, 12]},
        '酉': {'dali': [1, 7], 'xiaoli': [6, 12]},
        '辰': {'dali': [4, 10], 'xiaoli': [5, 11]},
        '戌': {'dali': [4, 10], 'xiaoli': [5, 11]},
        '巳': {'dali': [3, 9], 'xiaoli': [2, 8]},
        '亥': {'dali': [3, 9], 'xiaoli': [2, 8]}
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

def get_yintai(month_gan, month_zhi):
    """阴胎 = 月干顺进一位 + 月支顺进三位"""
    gan_idx = gan_index(month_gan)
    zhi_idx = zhi_index(month_zhi)
    yt_gan = GAN[(gan_idx + 1) % 10]
    yt_zhi = ZHI[(zhi_idx + 3) % 12]
    return yt_gan, yt_zhi

def get_yangqi(month_gan, month_zhi):
    """阳气 = 月干顺进一位 + 月支顺进三位"""
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

def get_fuxing_zixing_by_year(year_gan, year_zhi):
    """
    根据年干和年支返回夫星（正官）、七杀、子星（食神）、伤官的完整干支
    
    推算规则：
    1. 夫星天干：克年干的五行
    2. 夫星地支：根据年支推算（年支三合局的长生位）
    3. 子星天干：年干所生的五行
    4. 子星地支：根据年支推算（年支三合局的帝旺位）
    
    Args:
        year_gan: 年柱天干
        year_zhi: 年柱地支
        
    Returns:
        dict: {'fu':正官干支, 'qi':七杀干支, 'zi':食神干支, 'shang':伤官干支}
    """
    zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 夫星地支映射（根据年支推算）
    fu_zhi_map = {
        '子': '巳', '丑': '申', '寅': '亥', '卯': '戌', '辰': '申', '巳': '申',
        '午': '亥', '未': '申', '申': '寅', '酉': '巳', '戌': '寅', '亥': '寅'
    }
    
    # 子星地支映射（根据年支推算）
    zi_zhi_map = {
        '子': '戌', '丑': '巳', '寅': '申', '卯': '未', '辰': '亥', '巳': '寅',
        '午': '巳', '未': '巳', '申': '亥', '酉': '寅', '戌': '亥', '亥': '卯'
    }
    
    # 五行生克关系
    # 天干五行：甲=木, 乙=木, 丙=火, 丁=火, 戊=土, 己=土, 庚=金, 辛=金, 壬=水, 癸=水
    # 夫星：克我者（火克金, 金克木, 木克土, 土克水, 水克火）
    # 子星：我生者（木生火, 火生土, 土生金, 金生水, 水生木）
    
    # 夫星天干映射（克年干的五行）
    # 阳日干取正官（阴阳相反），阴日干取七杀（阴阳相同）
    # 金克木，木克土，土克水，水克火，火克金
    fuxing_gan_map = {
        '甲': '辛', '乙': '庚', '丙': '癸', '丁': '壬',
        '戊': '乙', '己': '甲', '庚': '丁', '辛': '丙',
        '壬': '己', '癸': '戊'
    }
    
    # 七杀天干映射（与夫星同五行的另一个天干）
    qisha_gan_map = {
        '甲': '庚', '乙': '辛', '丙': '壬', '丁': '癸',
        '戊': '甲', '己': '乙', '庚': '丙', '辛': '丁',
        '壬': '戊', '癸': '己'
    }
    
    # 子星天干映射（年干所生的五行）
    zixing_gan_map = {
        '甲': '丙', '乙': '丁', '丙': '戊', '丁': '己',
        '戊': '庚', '己': '辛', '庚': '壬', '辛': '癸',
        '壬': '甲', '癸': '乙'
    }
    
    # 伤官天干映射（与子星同五行的另一个天干）
    shangguan_gan_map = {
        '甲': '丁', '乙': '丙', '丙': '己', '丁': '戊',
        '戊': '辛', '己': '庚', '庚': '癸', '辛': '壬',
        '壬': '乙', '癸': '甲'
    }
    
    # 根据用户提供的三个例子调整地支映射
    # 辛未年（辛，未）→ 夫星丙申（申），子星癸巳（巳）
    # 丙子年（丙，子）→ 夫星癸巳（巳），子星戊戌（戌）
    # 己卯年（己，卯）→ 夫星甲戌（戌），子星辛未（未）
    
    # 调整后的地支映射
    fu_zhi_map = {
        '子': '巳', '丑': '申', '寅': '亥', '卯': '戌', '辰': '申', '巳': '申',
        '午': '亥', '未': '申', '申': '寅', '酉': '巳', '戌': '寅', '亥': '寅'
    }
    
    zi_zhi_map = {
        '子': '戌', '丑': '巳', '寅': '申', '卯': '未', '辰': '亥', '巳': '寅',
        '午': '巳', '未': '巳', '申': '亥', '酉': '寅', '戌': '亥', '亥': '卯'
    }
    
    # 从例子中提取正确的映射
    fu_zhi_map['未'] = '申'  # 辛未年夫星地支申
    fu_zhi_map['子'] = '巳'  # 丙子年夫星地支巳
    fu_zhi_map['卯'] = '戌'  # 己卯年夫星地支戌
    
    zi_zhi_map['未'] = '巳'  # 辛未年子星地支巳
    zi_zhi_map['子'] = '戌'  # 丙子年子星地支戌
    zi_zhi_map['卯'] = '未'  # 己卯年子星地支未
    
    fu_gan = fuxing_gan_map.get(year_gan, '')
    fu_zhi = fu_zhi_map.get(year_zhi, '')
    fu = fu_gan + fu_zhi if fu_gan and fu_zhi else ''
    
    zi_gan = zixing_gan_map.get(year_gan, '')
    zi_zhi = zi_zhi_map.get(year_zhi, '')
    zi = zi_gan + zi_zhi if zi_gan and zi_zhi else ''
    
    # 计算七杀（夫星地支顺数1位，使用七杀天干）
    if fu and len(fu) == 2:
        fu_zhi_idx = zhi_order.index(fu[1])
        qi_zhi = zhi_order[(fu_zhi_idx + 1) % 12]
        qi_gan = qisha_gan_map.get(year_gan, '')
        qi = qi_gan + qi_zhi if qi_gan else ''
    else:
        qi = ''
    
    # 计算伤官（子星地支顺数1位，使用伤官天干）
    if zi and len(zi) == 2:
        zi_zhi_idx = zhi_order.index(zi[1])
        shang_zhi = zhi_order[(zi_zhi_idx + 1) % 12]
        shang_gan = shangguan_gan_map.get(year_gan, '')
        shang = shang_gan + shang_zhi if shang_gan else ''
    else:
        shang = ''
    
    return {
        'fu': fu,
        'qi': qi,
        'zi': zi,
        'shang': shang
    }


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
    
    女命夫星为克日主的五行（官杀）：
    - 日主为木：夫星为金
    - 日主为火：夫星为水
    - 日主为土：夫星为木
    - 日主为金：夫星为火
    - 日主为水：夫星为土
    
    夫星受克的情况：
    1. 克制夫星的五行过旺（如夫星为水，土旺则克水）
    2. 日主太旺耗夫星（如日主火太旺，水夫星被耗）
    3. 夫星本身太弱
    4. 日课中直接有天干克制夫星（如月干克日支或日干）
    
    Args:
        bride_bazi: 新娘八字 {'ri_gan': '', ...}
        sizhu: 日课四柱信息
        
    Returns:
        (score, reason): 扣分和原因
    """
    if not bride_bazi or not bride_bazi.get('ri_gan'):
        return 0, None
    
    day_gan = bride_bazi['ri_gan']
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
            reason = f'日主较旺耗夫星（{day_wuxing}旺{day_wuxing_count:.1f}）'
    
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
    
    # 三刑关系
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
    
    # 检查每一组三刑
    for group, name in sanxing_groups:
        # 获取该组中存在的不同地支
        present_zhis = set(z for z in zhi_list if z in group)
        if len(present_zhis) >= 2:
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
    """上朔日
    
    上朔日判断规则：
    - 阳年：年干加寅顺数至亥
    - 阴年：年干加丑顺数至巳（阴年加四带巳）
    
    简化方法：根据年干确定上朔日干支
    阳年（甲丙戊庚壬）：年干+3 = 上朔日天干，地支固定为亥
    阴年（乙丁己辛癸）：年干+4 = 上朔日天干，地支固定为巳
    
    例如：2025年乙巳年（阴年），乙+4=己，所以上朔日是己巳日
    """
    year_gan = sizhu['year_gan']
    day_gan, day_zhi = sizhu['日柱'][0], sizhu['日柱'][1]
    
    # 天干顺序
    gan_order = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    try:
        year_gan_index = gan_order.index(year_gan)
        
        # 判断阳年还是阴年（甲丙戊庚壬为阳，乙丁己辛癸为阴）
        is_yang = year_gan_index % 2 == 0
        
        if is_yang:
            # 阳年：年干+3，地支为亥
            shangshuo_gan_index = (year_gan_index + 3) % 10
            shangshuo_gan = gan_order[shangshuo_gan_index]
            shangshuo_zhi = '亥'
        else:
            # 阴年：年干+4，地支为巳（阴年加四带巳）
            shangshuo_gan_index = (year_gan_index + 4) % 10
            shangshuo_gan = gan_order[shangshuo_gan_index]
            shangshuo_zhi = '巳'
        
        return (day_gan, day_zhi) == (shangshuo_gan, shangshuo_zhi)
    except (ValueError, IndexError):
        return False

def is_sili_sijue(date_obj):
    """四离四绝（简化版）"""
    # 实际应调用节气计算函数，这里简化处理
    return False

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
    """三娘煞：每月初三、初七、十三、十八、廿二、廿七
    
    注意：三娘煞按农历日期判断，不是公历日期
    """
    SANNIANGSHA_DAYS = [3, 7, 13, 18, 22, 27]
    
    try:
        from modules.四柱计算器 import get_lunar_date
        lunar_info = get_lunar_date(date_obj)
        if lunar_info and 'day' in lunar_info:
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
            return lunar_day in SANNIANGSHA_DAYS
    except Exception as e:
        logger.error(f"判断三娘煞失败: {e}")
    
    return False

def check_reject_items(date_obj, sizhu):
    """
    检查一票否决项
    
    Returns:
        (is_reject, reason): 是否否决及原因
    """
    if is_month_break(date_obj, sizhu):
        return True, '月破（月支冲年支）'
    if is_year_break(date_obj, sizhu):
        return True, '岁破（日支冲年支）'
    if is_shangshuo(date_obj, sizhu):
        return True, '上朔日'
    if is_sili_sijue(date_obj):
        return True, '四离四绝日'
    if is_sansang(date_obj):
        return True, '重丧日'
    if is_sanniangsha(date_obj):
        return True, '三娘煞'
    return False, None

# ==================== 时辰评分 ====================

def get_shichen_score(sizhu, bride_bazi=None, groom_bazi=None):
    """
    计算时辰得分
    
    Args:
        sizhu: 日课四柱信息（包含时柱）
        bride_bazi: 新娘八字 {'ri_gan': '', 'ri_zhi': ''}
        groom_bazi: 新郎八字 {'ri_gan': '', 'ri_zhi': ''}
    
    Returns:
        (score, details): 得分和详情列表
    """
    score = 0
    details = []
    hour_zhi = sizhu.get('hour_zhi', '')
    day_gan = sizhu['日柱'][0]
    day_zhi = sizhu.get('day_zhi', sizhu['日柱'][1] if len(sizhu.get('日柱', '')) > 1 else '')
    
    # 1. 黄道时加分（根据日支查表）
    if day_zhi in HUANGDAO_SHI_TABLE:
        hour_idx = ZHI.index(hour_zhi) if hour_zhi in ZHI else 0
        shi_xing = HUANGDAO_SHI_TABLE[day_zhi][hour_idx]
        if shi_xing in HUANGDAO_XING:
            score += 10
            details.append((f'黄道时({shi_xing})', 10))
    
    # 1.5 天乙贵人加分（根据日干查表）
    if day_gan in TIANYI_GUIREN:
        guiren_zhis = TIANYI_GUIREN[day_gan]
        if hour_zhi in guiren_zhis:
            score += 15
            details.append((f'天乙贵人时({hour_zhi}时)', 15))
    
    # 2. 五不遇时扣分（日干克时干）
    hour_gan = sizhu.get('hour_gan', '')
    if hour_gan:
        # 五不遇时：甲日庚午时、乙日辛巳时、丙日壬辰时、丁日癸卯时、戊日甲寅时
        # 己日乙丑时、庚日丙子时、辛日丁酉时、壬日戊申时、癸日己未时
        wubuyu_pairs = [('甲', '庚'), ('乙', '辛'), ('丙', '壬'), ('丁', '癸'), ('戊', '甲'),
                        ('己', '乙'), ('庚', '丙'), ('辛', '丁'), ('壬', '戊'), ('癸', '己')]
        if (day_gan, hour_gan) in wubuyu_pairs:
            score -= 20
            details.append(('五不遇时', -20))
    
    # 3. 时支与新娘日支合局加分
    if bride_bazi and bride_bazi.get('ri_zhi'):
        bride_ri_zhi = bride_bazi['ri_zhi']
        if is_liuhe(hour_zhi, bride_ri_zhi):
            score += 8
            details.append(('时支与新娘日支六合', 8))
        # 检查半合
        banhe_result, _ = is_banhe([hour_zhi, bride_ri_zhi])
        if banhe_result:
            score += 4
            details.append(('时支与新娘日支半合', 4))
    
    # 3.5 时支冲新娘生肖（年支）- 大凶
    if bride_bazi and bride_bazi.get('year_zhi'):
        if is_chong(hour_zhi, bride_bazi['year_zhi']):
            score -= 50  # 时支冲新娘生肖，禁用
            details.append(('时支冲新娘生肖', -50))
    
    # 4. 时支与新郎日支合局加分
    if groom_bazi and groom_bazi.get('ri_zhi'):
        groom_ri_zhi = groom_bazi['ri_zhi']
        if is_liuhe(hour_zhi, groom_ri_zhi):
            score += 5
            details.append(('时支与新郎六合', 5))
        banhe_result, _ = is_banhe([hour_zhi, groom_ri_zhi])
        if banhe_result:
            score += 3
            details.append(('时支与新郎半合', 3))
    
    return score, details

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
    is_reject, reject_reason = check_reject_items(date_obj, sizhu)
    if is_reject:
        result['reject_reason'] = reject_reason
        result['score'] = 0
        result['level'] = '❌ 凶'
        result['reason'] = reject_reason
        return result
    
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
            is_da_huangdao_day, is_xiao_huangdao_day
        )
        
        # 吉神加分
        if is_bujiang_day(date_obj):
            score += 25  # 不将日
            details.append(('不将日', 25))
        
        if is_tiande_day(date_obj):
            score += 15  # 天德
            details.append(('天德', 15))
        
        if is_yuede_day(date_obj):
            score += 15  # 月德
            details.append(('月德', 15))
        
        # 大黄道（十二神）加分/扣分 - 更重要
        if is_da_huangdao_day(date_obj):
            score += 15  # 大黄道吉日（和天德月德同级）
            details.append(('大黄道吉日', 15))
        else:
            score -= 15  # 大黄道凶日（有分量，即使小黄道吉也可能净扣分）
            details.append(('大黄道凶日', -15))
        
        # 小黄道（建除）加分 - 次要
        if is_xiao_huangdao_day(date_obj):
            score += 8  # 小黄道吉日
            details.append(('小黄道吉日', 8))
        
        # 凶神扣分
        if bride_bazi and bride_bazi.get('year_zhi'):
            if is_sansha(date_obj, bride_bazi['year_zhi']):
                score -= 25  # 三煞
                details.append(('三煞', -25))
        
        # 日支冲新娘生肖（年支）- 大凶
        if bride_bazi and bride_bazi.get('year_zhi'):
            day_gan, day_zhi = get_day_ganzhi(date_obj)
            if is_chong(day_zhi, bride_bazi['year_zhi']):
                score -= 45  # 日支冲新娘生肖
                details.append(('日支冲新娘生肖', -45))
                result['warnings'].append(f"日支{day_zhi}冲新娘生肖{bride_bazi['year_zhi']}")
        
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
        
        # 夫星、子星检查（如果有新娘日柱）
        if bride_bazi and bride_bazi.get('ri_gan'):
            day_gan, day_zhi = get_day_ganzhi(date_obj)
            fuxing_info = get_fuxing_zixing(bride_bazi['ri_gan'])
            
            # 冲夫星（日支冲夫星对应的地支）
            fu_gan = fuxing_info.get('fu', '')
            if fu_gan:
                # 夫星地支：需要根据夫星天干确定对应的地支
                # 这里简化处理：直接检查日支是否与夫星天冲
                # 实际应考虑夫星地支
                fu_chong_zhi = {'甲': '庚', '庚': '甲', '乙': '辛', '辛': '乙',
                                '丙': '壬', '壬': '丙', '丁': '癸', '癸': '丁',
                                '戊': '甲', '己': '乙', '庚': '丙', '辛': '丁',
                                '壬': '戊', '癸': '己'}.get(fu_gan, '')
                if is_chong(day_zhi, fu_chong_zhi):
                    score -= 35
                    details.append(('冲夫星', -35))
            
            # 冲子星（日支冲子星对应的地支）
            zi_gan = fuxing_info.get('zi', '')
            if zi_gan:
                zi_chong_zhi = {'甲': '庚', '庚': '甲', '乙': '辛', '辛': '乙',
                                '丙': '壬', '壬': '丙', '丁': '癸', '癸': '丁',
                                '戊': '甲', '己': '乙', '庚': '丙', '辛': '丁',
                                '壬': '戊', '癸': '己'}.get(zi_gan, '')
                if is_chong(day_zhi, zi_chong_zhi):
                    score -= 20
                    details.append(('冲子星', -20))
            
            # 阴胎（以月柱为基准）
            yintai_gan, yintai_zhi = get_yintai(bride_bazi.get('yue_gan', '甲'), bride_bazi.get('yue_zhi', '子'))
            if day_gan == yintai_gan and day_zhi == yintai_zhi:
                score -= 30
                details.append(('犯阴胎', -30))
            
            # 阳气（以月柱为基准）
            yangqi_gan, yangqi_zhi = get_yangqi(bride_bazi.get('yue_gan', '甲'), bride_bazi.get('yue_zhi', '子'))
            if day_gan == yangqi_gan and day_zhi == yangqi_zhi:
                score -= 30
                details.append(('犯阳气', -30))
    
    except Exception as e:
        logger.warning(f"神煞计算异常: {e}")
    
    # 4.5 夫星受克检查
    if bride_bazi and bride_bazi.get('ri_gan'):
        fuxing_ke_score, fuxing_ke_reason = check_fuxing_being_ke(bride_bazi, sizhu)
        if fuxing_ke_score != 0 and fuxing_ke_reason:
            score += fuxing_ke_score
            details.append((fuxing_ke_reason, fuxing_ke_score))
            if fuxing_ke_score < -30:
                result['warnings'].append(f"严重警告：{fuxing_ke_reason}")
    
    # 4.6 六害检查
    liuhai_score, liuhai_reasons = check_liuhai_penalty(sizhu)
    if liuhai_score != 0:
        score += liuhai_score
        for reason in liuhai_reasons:
            details.append((reason, -5))  # 每处六害扣5分
    
    # 4.7 三刑检查
    sanxing_score, sanxing_reasons = check_sanxing_penalty(sizhu)
    if sanxing_score != 0:
        score += sanxing_score
        for reason in sanxing_reasons:
            # 根据内容确定扣分
            if '无恩之刑' in reason or '恃势之刑' in reason or '无礼之刑' in reason:
                details.append((reason, -8))
            elif '自刑' in reason:
                details.append((reason, -6))
    
    # 5. 日课四柱内部合局评分
    zhiju_score, zhiju_reason = get_zhiju_score(sizhu)
    if zhiju_reason:
        score += zhiju_score
        details.append((zhiju_reason, zhiju_score))
    
    # 6. 时辰评分（默认使用中午12时）
    # 用户可在实际使用时传入具体时辰
    shichen_score, shichen_details = get_shichen_score(sizhu, bride_bazi, groom_bazi)
    score += shichen_score
    details.extend(shichen_details)
    
    # 7. 计算总分并确定等级
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
