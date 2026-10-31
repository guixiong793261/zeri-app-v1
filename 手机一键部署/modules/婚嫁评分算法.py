# -*- coding: utf-8 -*-
"""
婚嫁日课评分算法优化版（基于《协纪辨方书》）

核心功能：
1. 大利月/小利月检查
2. 一票否决项检查（岁破、真三娘煞；月破/上朔/四离四绝为重扣分项，
   重丧日按 001 §196 撤否决并撤扣分）
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
# J2（2026-10-01，001 §57）：起例按《协纪辨方书·卷七》引《考原》——
# 寅申起子、卯酉起寅、辰戌起辰、巳亥起午、子午起申、丑未起戌。
# 本表为惰性镜像（本文件内 0 处读取，仅作与 modules/黄道.py 对齐的参照源），
# 同步防未来误用。
# 青龙、明堂、金匮、天德、玉堂、司命为黄道吉时
# 天刑、朱雀、白虎、天牢、玄武、勾陈为黑道凶时
HUANGDAO_SHI_TABLE = {
    # 子午起于申：申时青龙
    '子': ['金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀'],
    '午': ['金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀'],
    # 丑未起于戌：戌时青龙
    '丑': ['天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂'],
    '未': ['天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂'],
    # 寅申起于子：子时青龙
    '寅': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
    '申': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
    # 卯酉起于寅：寅时青龙
    '卯': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
    '酉': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
    # 辰戌起于辰：辰时青龙
    '辰': ['天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂'],
    '戌': ['天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂'],
    # 巳亥起于午：午时青龙
    '巳': ['白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德'],
    '亥': ['白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德']
}
HUANGDAO_XING = ['青龙', '明堂', '金匮', '天德', '玉堂', '司命']

# 【墓碑】原伪权威表已删，统一见 modules/shensha/时辰系.py（001 §168 收口）。
# 原此处 TIANYI_GUIREN 天乙贵人时辰表全仓零调用（死表），且自标"权威"名不副实，
# 经 2026-10-23 时辰系收口批复决定删除；贵人时辰唯一事实源为
# modules/shensha/时辰系.GUIREN_SHICHEN。

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

# 三合四局按宫位序（长生→帝旺→墓）排列：P1-C-2 修复（2026-10-16 拍板）。
# 原 set 字面量 + list(set) 输出顺序受 PYTHONHASHSEED 影响跨进程可翻转
# （§96.5 挂账：0111 案拱合局 (巳,丑)↔(丑,巳)，fixture 会无故漂移），
# 改为宫位序元组 + 序内过滤，输出与进程无关；属测试基建修正，非业务口径变更。
_SANHE_GONGXU = [
    ('申', '子', '辰'),  # 水局：申长生 子帝旺 辰墓
    ('寅', '午', '戌'),  # 火局：寅长生 午帝旺 戌墓
    ('巳', '酉', '丑'),  # 金局：巳长生 酉帝旺 丑墓
    ('亥', '卯', '未'),  # 木局：亥长生 卯帝旺 未墓
]

def is_sanhe(zhi_list):
    """检查是否构成三合局（三个不同地支）"""
    unique_zhis = set(zhi_list) - {None, ''}
    for group in _SANHE_GONGXU:
        if set(group).issubset(unique_zhis):
            return True, list(group)  # 宫位序（长生→帝旺→墓），输出稳定
    return False, None

def is_banhe(zhi_list):
    """检查是否构成半合局（两个不同地支）"""
    unique_zhis = set(zhi_list) - {None, ''}
    for group in _SANHE_GONGXU:
        common = unique_zhis.intersection(group)
        if len(common) == 2:
            return True, [z for z in group if z in common]  # 宫位序，输出稳定
    return False, None

# ==================== 日课四柱内部合局评分 ====================

def get_zhiju_score(sizhu, hour_zhi=''):
    """
    计算日课四柱内部地支合局得分

    Args:
        sizhu: 包含 year_zhi, month_zhi, day_zhi, hour_zhi 的字典（评分口径
               可传已剔除时柱的 sizhu——时柱分数由十二时辰表独立评估）
        hour_zhi: 可选，实际时柱地支；仅用于命名——拱合所拱支若由时柱补齐，
                  三合已齐，应称“三合局”（E101）；分数仍按年月日拱合口径 +8。

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
        # 2026-10-02 按宫位区分拱合与半合：
        # 长生(0)+帝旺(1)=生地半合，帝旺(1)+墓(2)=墓地半合，长生(0)+墓(2)=拱合。
        _SANHE_GONG = {
            frozenset(['申', '子', '辰']): {'申': 0, '子': 1, '辰': 2, 'zs': '子'},
            frozenset(['寅', '午', '戌']): {'寅': 0, '午': 1, '戌': 2, 'zs': '午'},
            frozenset(['巳', '酉', '丑']): {'巳': 0, '酉': 1, '丑': 2, 'zs': '酉'},
            frozenset(['亥', '卯', '未']): {'亥': 0, '卯': 1, '未': 2, 'zs': '卯'},
        }
        _pair_set = set(banhe_zhis)
        for _gset, _gmap in _SANHE_GONG.items():
            if _pair_set < _gset:
                _pos = sorted(_gmap[z] for z in banhe_zhis)
                _zs = _gmap['zs']
                _que = list(_gset - _pair_set)[0]
                if _pos == [0, 2]:
                    if hour_zhi and hour_zhi == _zs:
                        # 时柱补齐所拱支：三合已齐（E101），年月日部分仍按 +8
                        return 8, (f'三合局({",".join(banhe_zhis)}+时支{_zs}补齐，'
                                   f'年月日按拱合+8)')
                    return 8, f'拱合局({",".join(banhe_zhis)}，拱{_zs})'
                return 8, f'半合局({",".join(banhe_zhis)}半合，缺{_que})'
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
    
    # 情况3：新娘年命五行在日课中过旺耗夫星
    # （day_wuxing 为新娘年干五行，非日课日主；2026-10-02 修正文案，
    #   旧写"日主较旺耗夫星"与月令分析"日课日主休囚"并读时自相矛盾）
    if not reason:
        if day_wuxing_count > 3.0 and fuxing_count < 1.0:
            score = -20
            reason = (f'新娘年命{day_wuxing}气偏旺耗夫星（日课{day_wuxing}元素强度{day_wuxing_count:.1f}，'
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
                    # P1-C-1-a（2026-10-16 拍板）：嫁娶课式六害 -5→-6，与通用四柱六对口径（日课校验器 E207）统一
                    total_penalty -= 6  # 每处六害扣6分
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
            # P1-C-1-b（2026-10-16 拍板）：嫁娶课式自刑 -6→-8，与通用四柱六对口径（日课校验器 E207）及三刑 -8 统一
            total_penalty -= 8  # 自刑扣8分
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

def is_yangcuo(date_obj, sizhu):
    """阳错（嫁娶专属凶神，2026-10 I1 第一批接入 D）

    委托 shensha 层唯一实现 神煞基类.is_yangcuo_by_pillar（《协纪辨方书》
    卷四义例二引《堪舆经》逐月立成），D 与 checker 层共用同一规则源，
    不再各写一份月支→干支表。
    """
    try:
        from .shensha.神煞基类 import is_yangcuo_by_pillar
    except ImportError:
        from modules.shensha.神煞基类 import is_yangcuo_by_pillar
    day_gz = sizhu.get('日柱', '') or (sizhu.get('day_gan', '') + sizhu.get('day_zhi', ''))
    return is_yangcuo_by_pillar(sizhu.get('month_zhi', ''), day_gz)

def is_yandui(date_obj, sizhu):
    """厌对（嫁娶专属凶神，2026-10 I1 第一批接入 D）

    委托 shensha 层唯一实现 神煞基类.is_yandui_by_zhi（《协纪辨方书》
    卷五义例三引《天宝历》，月厌所冲之辰），D 与 checker 层共用同一
    规则源，不再各写一份月支→日支表。
    """
    try:
        from .shensha.神煞基类 import is_yandui_by_zhi
    except ImportError:
        from modules.shensha.神煞基类 import is_yandui_by_zhi
    day_zhi = sizhu.get('day_zhi', '') or (sizhu.get('日柱', '') or ['', ''])[1]
    return is_yandui_by_zhi(sizhu.get('month_zhi', ''), day_zhi)

def is_bazhuan(date_obj, sizhu):
    """八专（凶神，2026-10 I1 第一批接入 D）

    委托 shensha 层唯一实现 神煞基类.is_bazhuan_by_pillar（《历例》
    B5 版 5 柱：丁未、己未、庚申、甲寅、癸丑；不随月建）。卷十嫁娶
    忌之列；八专另有通配键与 9 个非嫁娶事项键（checker 子类自注册），
    D 仅按 ('嫁娶','八专') 取分。
    """
    try:
        from .shensha.神煞基类 import is_bazhuan_by_pillar
    except ImportError:
        from modules.shensha.神煞基类 import is_bazhuan_by_pillar
    day_gz = sizhu.get('日柱', '') or (sizhu.get('day_gan', '') + sizhu.get('day_zhi', ''))
    return is_bazhuan_by_pillar(day_gz)

def is_sifei(date_obj, sizhu):
    """四废（凶神，2026-10 I1 第一批接入 D）

    委托 shensha 层唯一实现 神煞基类.is_sifei_by_pillar（《协纪辨方书》
    四时衰废之气：春庚申辛酉、夏壬子癸亥、秋甲寅乙卯、冬丙午丁巳，
    月支查日柱干支）。卷十嫁娶忌；四废事项键覆盖 15 个事项（无通配，
    checker 基类统一注册），D 按 ('嫁娶','四废') 取分。
    """
    try:
        from .shensha.神煞基类 import is_sifei_by_pillar
    except ImportError:
        from modules.shensha.神煞基类 import is_sifei_by_pillar
    day_gz = sizhu.get('日柱', '') or (sizhu.get('day_gan', '') + sizhu.get('day_zhi', ''))
    return is_sifei_by_pillar(sizhu.get('month_zhi', ''), day_gz)

def is_huangsha(date_obj, sizhu):
    """黄沙日（凶神，2026-10-02 接入 D）

    委托 shensha 层唯一实现 神煞基类.is_huangsha_by_zhi（节气月支版：
    四孟寅申巳亥月逢午日、四仲子午卯酉月逢寅日、四季辰戌丑未月逢子日）。
    《协纪》义例体系黄沙为嫁娶忌日；事项键 ('嫁娶','黄沙')=-12 已存在
    于 事项标准.py，本函数补齐"入评分详情+神煞信息"链路。
    """
    try:
        from .shensha.神煞基类 import is_huangsha_by_zhi
    except ImportError:
        from modules.shensha.神煞基类 import is_huangsha_by_zhi
    return is_huangsha_by_zhi(sizhu.get('month_zhi', ''), sizhu.get('day_zhi', ''))

def is_sansang(date_obj):
    """复日（旧称重丧日；历史函数名沿用，避免外部引用断裂）

    001 §197（2026-10-28 拍板 D3-Q1/Q2/Q3）：起例改协纪正法单干·节气月建，
    与神煞层同委托基类单点出口 is_furi_by_date，两处判定恒等；
    典据见该出口注释与 docs/重丧日起例三库对勘报告_20261028.md。
    """
    try:
        from .shensha.神煞基类 import is_furi_by_date
    except ImportError:
        from modules.shensha.神煞基类 import is_furi_by_date
    return is_furi_by_date(date_obj)

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
    保留的绝对否决项：岁破（日支冲年支）
    （001 §196，2026-10-28 拍板 D1：重丧日三库明言惟丧葬忌、吉事不忌，
    嫁娶撤否决，移出神煞层 0 分纯展示，不再作为本层否决项。）
    （§212，2026-10-31 拍板 1：真三娘煞撤除——三库零载，原为绝对否决项；
    官方嫁娶忌表（协纪卷十一/考原卷六）只认月破、往亡等正牌凶煞。）
    """
    if is_year_break(date_obj, sizhu):
        return True, '岁破（日支冲年支）'
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
# HUANGDAO_SHI_TABLE 常量保留，作为与 modules/黄道.py、
# modules/shensha/通用神煞.py 规则对齐的参照源。
# TIANYI_GUIREN 原伪权威表已删（001 §168），贵人时辰统一见 modules/shensha/时辰系.py。

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
            is_sansha, get_fuxing_zixing,
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
            # P1-C-3a（2026-10-17 拍板）：嫁娶天德 15→20，与通用口径统一（B 族残差清零）
            score += 20  # 天德
            details.append(('天德', 20))

        if is_yuede_day(date_obj):
            # P1-C-3a：嫁娶月德 15→18，与通用口径统一
            score += 18  # 月德
            details.append(('月德', 18))

        # 福星贵人（2026-10-25 001 §175，Q3 拍板方案A「单点补福星」）
        # 时辰派「日干生时干曰福星贵人」，只查时支（001 §169 时辰层正统落地；
        # §165 伪福星谓词已删）。此前嫁娶仅由评分器 _build_fuxing_shensha 写入
        # shensha_list 展示 +10，婚嫁算法无对应 details 项 → 「福星展示不计分」
        # 缺口（实测 2026 全年正常嫁娶日 19 天 × +10 = +190，2 天跨档）。
        # 本批补计分，与羊刃同构（展示/计分双源，分值同查 SHENSHA_SCORES
        # ('嫁娶','福星')=10）。评分器调用本函数时 hour 由当前时柱反算
        # （评分器.py:909-912 _ZHI2HOUR），故与展示条目时支恒一致。
        try:
            from .shensha.时辰系 import get_fuxing_shichen as _get_fuxing_shichen
            from .事项标准 import shensha_score as _ss_score
        except ImportError:
            from shensha.时辰系 import get_fuxing_shichen as _get_fuxing_shichen
            from 事项标准 import shensha_score as _ss_score
        _fx_day_gan = (sizhu.get('日柱') or '')[:1]
        if _fx_day_gan and sizhu.get('hour_zhi') in _get_fuxing_shichen(_fx_day_gan):
            _fx_score = _ss_score('嫁娶', '福星', 10)
            score += _fx_score
            details.append(('福星', _fx_score))
        
        # 大黄道（十二神值日）/小黄道（建除十二神）计分
        # 2026-02-05 统一口径：分值一律取自黄道模块（modules/黄道.py），与详情页
        # 【黄道信息】显示完全一致——大黄道青龙/明堂/天德/玉堂+15、金匮/司命+10、
        # 六黑道-15；小黄道吉（除/定/执/危/成/开）+5、凶（建/满/平/破/收/闭）-10。
        # 批次 2（001 §162）：删除无据的「除/危/执虽黄道为吉却忌嫁娶，按-5计」——
        # 卷十载嫁娶忌仅破/平/收/闭，除/危/执为黄道吉星按+5计。
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

        # 小黄道（建除）：吉建星+5、凶建星-10
        # 批次 2（001 §162）：删除无据的「除/危/执 -5」嫁娶特殊扣分——
        # 卷十载嫁娶忌仅破/平/收/闭，除/危/执为黄道吉星按+5计。
        _xo = _hd.get('xiao_huang_dao') or {}
        _xn = _xo.get('name', '') or (get_jianchu(date_obj) if is_xiao_huangdao_day(date_obj) else '')
        _jianchu_xiong = {'建', '满', '平', '破', '收', '闭'}  # 黑道凶日
        if _xn in _jianchu_xiong:
            score -= 10
            details.append((f'小黄道{_xn}日（黑道凶日）', -10))
        elif _xn:  # 除/危/定/执/成/开等黄道吉日
            _xo_score = int(_xo.get('score', 5) or 5)
            score += _xo_score
            details.append((f'小黄道{_xn}日（宜嫁娶）', _xo_score))
        
        # 凶神扣分（本命三煞＝《陈子性藏书》嫁娶"和尚杀"例，页799：
        # "右例即和尚煞，亦云孤神寡宿，及本命三殺也，犯之主无子息，
        # 其例只论男命不论女命……和尚是男子，若以女命论者错矣；
        # 否则男女俱不犯更妙"。煞局（生年三合对冲三支，依次劫/灾/岁）：
        # 申子辰生人忌巳午未日（煞南）、寅午戌忌亥子丑（煞北）、
        # 亥卯未忌申酉戌（煞西）、巳酉丑忌寅卯辰（煞东）。
        # 2026-10-11 B1 第 2 步（典据研究文档 §8.2 判据(a)、§8.5 判据(d)，
        # 用户拍板 B1）：
        #   ① 查询对象由新娘改为新郎——典据只论男命（旧实现只查新娘系
        #      性别查反）；新娘同犯仅作 0 分对照展示，不参与扣分；
        #   ② 第三位依《星历考原》钦定定名"劫煞/灾煞/岁煞"正名
        #      （旧标"月煞"本曹震圭异名，馆臣体系中"月煞"已配月家
        #      月虚神，年局第三位称月煞易混）。
        # 真假分档与天月德化解已删（上一 commit，判据 b/c）；本煞仍为
        # 扣分通道，不直接置否决。
        _g_year_zhi = groom_bazi.get('year_zhi') if groom_bazi else None
        _b_year_zhi = bride_bazi.get('year_zhi') if bride_bazi else None
        _BENMING_CITE = '依《陈子性藏书》页799"本命三殺其例只论男命不论女命"'
        # 生年局 → 三煞位三支（依次劫/灾/岁）：申子辰煞南巳午未、寅午戌煞北亥子丑、
        # 巳酉丑煞东寅卯辰、亥卯未煞西申酉戌。用于"未犯"行向用户解释为何未犯。
        _BENMING_SANWEI = {'申': '巳午未', '子': '巳午未', '辰': '巳午未',
                           '寅': '亥子丑', '午': '亥子丑', '戌': '亥子丑',
                           '巳': '寅卯辰', '酉': '寅卯辰', '丑': '寅卯辰',
                           '亥': '申酉戌', '卯': '申酉戌', '未': '申酉戌'}
        if _g_year_zhi:
            _, sd_zhi = get_day_ganzhi(date_obj)
            sha_fang = {'巳': '南', '午': '南', '未': '南', '亥': '北', '子': '北', '丑': '北',
                        '申': '西', '酉': '西', '戌': '西', '寅': '东', '卯': '东', '辰': '东'}.get(sd_zhi, '')
            sha_ming = {'巳': '劫煞', '午': '灾煞', '未': '岁煞', '亥': '劫煞', '子': '灾煞', '丑': '岁煞',
                        '申': '劫煞', '酉': '灾煞', '戌': '岁煞', '寅': '劫煞', '卯': '灾煞', '辰': '岁煞'}.get(sd_zhi, '')
            if is_sansha(date_obj, _g_year_zhi):
                penalty = -25
                label = (f"本命三煞【新郎本命三煞之{sha_ming}位·煞{sha_fang}，扣{penalty}分】"
                         f"{_BENMING_CITE}：新郎年命{_g_year_zhi}，日支{sd_zhi}犯本命三煞之{sha_ming}位，宜避")
                score += penalty
                details.append((label, penalty))
                # 新娘对照：典据只论男命，新娘同犯不扣分，仅信息展示供对照新旧口径
                if _b_year_zhi and is_sansha(date_obj, _b_year_zhi):
                    details.append((f"新娘年命{_b_year_zhi}对照：日支{sd_zhi}亦在新娘三煞方之"
                                    f"{sha_ming}位（典据只论男命，新娘项不参与扣分，仅对照展示）", 0))
            else:
                # 新郎不犯：明示一行（含典据说明），新娘若同犯则并列为 0 分对照
                if _b_year_zhi and is_sansha(date_obj, _b_year_zhi):
                    details.append((f"本命三煞：新郎年命{_g_year_zhi}"
                                    f"（三煞位：{_BENMING_SANWEI.get(_g_year_zhi, '?')}）未犯；"
                                    f"新娘年命{_b_year_zhi}对照，日支{sd_zhi}犯其本命三煞之{sha_ming}位"
                                    f"——{_BENMING_CITE}，女命不参与扣分，仅对照展示", 0))
                else:
                    # 未犯也向用户解释"为什么未犯"：标明新郎三煞位与本日日支的关系
                    details.append((f"本命三煞：新郎年命{_g_year_zhi}"
                                    f"（三煞位：{_BENMING_SANWEI.get(_g_year_zhi, '?')}），"
                                    f"日支{sd_zhi}不在其位，未犯（{_BENMING_CITE}，查男命非查女命）", 0))
        elif _b_year_zhi:
            # 有新娘生年而缺新郎生年：无法按典据判定，明示以防静默漏判
            details.append(("本命三煞：新郎生年信息缺失，未作本命三煞判定"
                            "（依《陈子性藏书》页799本命三煞只论男命，请补全新郎生年后再判）", 0))
        else:
            # 双方生年信息均缺失：同样明示，防止用户把静默跳过误读为"没犯"（验收细节②）
            details.append(("本命三煞：新郎、新娘生年信息均缺失，未作本命三煞判定"
                            "（依《陈子性藏书》页799本命三煞只论男命，请补全生年四柱后再判）", 0))
        
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
        
        # 天罡日／河魁日：§212 拍板 1 删除——协纪卷四起例为「阳月/阴月 × 平/收日」，
        # 与软件「日支临月建／日支临月破」不等价（起例错），原 -10/-10 撤销
        # （P1-C-3a 曾自 -40 统一为 -10）。
        
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
    # 2026-10 I1：本批接入的嫁娶专属凶神分值一律查 SHENSHA_SCORES 单一表，
    # 谓词全部委托 modules/shensha/神煞基类.py 模块级单点出口。
    try:
        from .事项标准 import shensha_score as _shensha_score
    except ImportError:
        from 事项标准 import shensha_score as _shensha_score

    # 月破（P1-C-3a：-40→-30，与通用口径统一）
    if is_month_break(date_obj, sizhu):
        score -= 30
        details.append(('月破', -30))
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

    # 阳错（2026-10 I1 第一批接入）：《协纪》卷四义例二《堪舆经》逐月立成，
    # 典载嫁娶忌。谓词委托神煞基类.is_yangcuo_by_pillar 单点出口，
    # 分值查 ('嫁娶','阳错')=-15（非嫁娶事项无键、不接入）。
    if is_yangcuo(date_obj, sizhu):
        _yangcuo_score = _shensha_score('嫁娶', '阳错', -15)
        score += _yangcuo_score
        details.append(('阳错', _yangcuo_score))
        result['warnings'].append('阳错：阴阳错乱之日，忌嫁娶')

    # 厌对（2026-10 I1 第一批接入）：《协纪》卷五义例三《天宝历》月厌所冲
    # 之辰，典载"其日忌嫁娶"。谓词委托神煞基类.is_yandui_by_zhi 单点出口，
    # 分值查 ('嫁娶','厌对')=-10（非嫁娶事项无键、不接入）。
    # 2026-10-21 制化第一批（001 §155，矩阵#13）：「与天德月德天德合月德合
    # 天赦并则不忌（天愿不得与厌对并）」——五德集命中即免扣，details 记
    # 豁免键 0 分（防日课校验器嫁娶负分条目双向追溯误报）。
    try:
        from .shensha.制化引擎 import eval_yandui_exempt
    except ImportError:
        from modules.shensha.制化引擎 import eval_yandui_exempt
    if is_yandui(date_obj, sizhu):
        if eval_yandui_exempt(sizhu)[0]:
            details.append(('厌对·制化豁免', 0))
            result['warnings'].append('厌对：五德并临，典载不忌（已豁免）')
        else:
            _yandui_score = _shensha_score('嫁娶', '厌对', -10)
            score += _yandui_score
            details.append(('厌对', _yandui_score))
            result['warnings'].append('厌对：月厌所冲之日，忌嫁娶')

    # 八专（2026-10 I1 第一批接入）：《历例》B5 版 5 柱
    # （丁未、己未、庚申、甲寅、癸丑），《协纪》卷十嫁娶忌。
    # 谓词委托神煞基类.is_bazhuan_by_pillar 单点出口（不随月建），
    # 分值查 ('嫁娶','八专')=-15。
    if is_bazhuan(date_obj, sizhu):
        _bazhuan_score = _shensha_score('嫁娶', '八专', -15)
        score += _bazhuan_score
        details.append(('八专', _bazhuan_score))
        result['warnings'].append('八专：阴阳不备之日，忌嫁娶')

    # 四废（2026-10 I1 第一批接入）：《协纪》四时衰废之气，春庚申辛酉、
    # 夏壬子癸亥、秋甲寅乙卯、冬丙午丁巳（月支查日柱），卷十嫁娶忌。
    # 谓词委托神煞基类.is_sifei_by_pillar 单点出口，
    # 分值查 ('嫁娶','四废')=-15。
    if is_sifei(date_obj, sizhu):
        _sifei_score = _shensha_score('嫁娶', '四废', -15)
        score += _sifei_score
        details.append(('四废', _sifei_score))
        result['warnings'].append('四废：四时衰废之气，忌嫁娶')

    # 黄沙日：§212 拍板 1 删除（三库零载），原 ('嫁娶','黄沙')=-12 撤销。

    # ==== 2026-10-03 E008 修复：忌项与评分明细同步 ====
    # 阴阳差错日/女命忌嫁日（/红纱日/神号日/鬼哭日 三项已按 §212 拍板 1
    # 撤计分或降 0 分提示）此前仅由嫁娶规则加入 ji_list（报告忌项），
    # 从未计入 marriage score，导致校验器 E008 报
    # "忌项无评分出处"（365 天抽查 112 例，占 30%）。此处补齐扣分，
    # 判定表复用 MarriageRuleChecker 类常量，分值查 SHENSHA_SCORES 单一表。
    try:
        from .rules.嫁娶规则 import MarriageRuleChecker as _MRC
    except ImportError:
        from modules.rules.嫁娶规则 import MarriageRuleChecker as _MRC

    # 农历月/日/闰月（神号/鬼哭按农历月；红纱改用节气月支，闰月不适用）
    _lunar_month_num = 0
    _is_leap_m = False
    _month_zhi = ''
    try:
        import sxtwl as _sxtwl
        _lunar = _sxtwl.fromSolar(date_obj.year, date_obj.month, date_obj.day)
        _lm = _lunar.getLunarMonth()
        _is_leap_m = _lm < 0
        _lunar_month_num = abs(_lm)
    except Exception:
        _lunar_month_num = 0
    # 节气月支取 calculate_sizhu（与 shensha_list/嫁娶规则同源，避免节气交接日
    # sxtwl 月支与产品月支偏差；红砂权威清单以产品月支为准）
    try:
        from .四柱计算器 import calculate_sizhu as _csz
    except ImportError:
        from 四柱计算器 import calculate_sizhu as _csz
    _month_zhi = _csz(date_obj, 12, 0).get('month_zhi', '')
    _day_gan_m, _day_zhi_m = get_day_ganzhi(date_obj)
    _day_gz_m = _day_gan_m + _day_zhi_m

    # 阴阳差错日（12 特定干支日，《协纪》嫁娶忌）
    if _day_gz_m in _MRC.YINYANG_CHACUO:
        _sc = _shensha_score('嫁娶', '阴阳差错日', -15)
        score += _sc
        details.append(('阴阳差错日', _sc))
        result['warnings'].append('阴阳差错日：阴阳不交之日，忌嫁娶')

    # 女命忌嫁日（当梁勾绞：新娘生肖 -> 忌日支）
    if bride_bazi and bride_bazi.get('year_zhi'):
        _bride_zx = str(bride_bazi['year_zhi'])
        if _bride_zx in _MRC.NV_MING_JI_JIA and _day_zhi_m in _MRC.NV_MING_JI_JIA[_bride_zx]:
            _sc = _shensha_score('嫁娶', '女命忌嫁日', -15)
            score += _sc
            details.append((f'女命忌嫁日（{_bride_zx}相忌{_day_zhi_m}日）', _sc))
            result['warnings'].append(f'女命忌嫁日：{_bride_zx}相忌{_day_zhi_m}日，忌嫁娶')

    # 年命冲岁（001 §196 D4，2026-10-28 拍板）：日课年支冲事主本命年支。
    # 原为嫁娶规则层「年柱冲命」整年 HARD_VETO（2026 鼠命仅 13 天可评）；
    # 协纪 p279217「选择亦无专取本命年支一字之例」→ 撤否决，降为普通扣分 -15
    # （不否决，仅影响档位）。神煞层「年命冲岁」同分展示。
    _yr_zhi_cm = sizhu.get('year_zhi', '')
    if _yr_zhi_cm:
        for _who, _bzi in (('新娘', (bride_bazi or {}).get('year_zhi')),
                           ('新郎', (groom_bazi or {}).get('year_zhi'))):
            if _bzi and is_chong(_yr_zhi_cm, _bzi):
                _cm_score = _shensha_score('嫁娶', '年命冲岁', -15)
                score += _cm_score
                details.append((f'年命冲岁（年支{_yr_zhi_cm}冲{_who}本命{_bzi}）', _cm_score))
                result['warnings'].append(
                    f'年命冲岁：日课年支{_yr_zhi_cm}冲{_who}本命{_bzi}，仅扣分不否决')
                break

    # 红纱日／神号日：§212 拍板 1 删除——红纱日协纪 p279217 明斥「甚属无当」、
    # 「应请一并删去」，神号日三库零载（无嫁娶专条），原 ('嫁娶','红纱日')=-20、
    # ('嫁娶','神号')=-15 计分一并撤销。

    # 鬼哭日（农历月 -> 日支）：仅陈书 p622 单典据、无嫁娶专条；
    # §212 拍板 1 降为 0 分提示（原 ('嫁娶','鬼哭')=-15 撤销，保留展示与警示）。
    if _lunar_month_num in _MRC.GUIRU:
        if _day_zhi_m in _MRC.GUIRU[_lunar_month_num]:
            details.append(('鬼哭日（单典据，仅提示不计分）', 0))
            result['warnings'].append('鬼哭日（单典据、无嫁娶专条，仅提示不计分）')

    # 羊刃（2026-10-02 修复漏计）：冠带派日干查地支（甲卯乙辰丙午丁未戊午己未
    # 庚酉辛戌壬子癸丑，与评分器._YANGREN_MAP 同表）。此前羊刃仅由评分器加入
    # shensha_list 供【神煞信息】展示，从未计入 marriage score，导致"凶煞区
    # 显示羊刃-15 而总分公式不含该项"（如日课丙午见丙日应为 85+5+3=93，却出
    # 100+5+3=108）。分值查 SHENSHA_SCORES 单一表（('*','羊刃')=-15）；
    # 两见以上 -25（刃喜一位忌重见，取劫煞/灾煞单犯分量，口径同评分器）。
    _YANGREN_MAP_MRG = {
        '甲': '卯', '乙': '辰', '丙': '午', '丁': '未',
        '戊': '午', '己': '未', '庚': '酉', '辛': '戌',
        '壬': '子', '癸': '丑',
    }
    _day_gan_yr = sizhu.get('日柱', '')[:1]
    _yr_target = _YANGREN_MAP_MRG.get(_day_gan_yr)
    if _yr_target:
        _yr_hits = [f'{pn}{sizhu[pn][1]}' for pn in ('年柱', '月柱', '日柱', '时柱')
                    if len(sizhu.get(pn, '')) >= 2 and sizhu[pn][1] == _yr_target]
        if _yr_hits:
            _yr_score = (_shensha_score('嫁娶', '羊刃', -15)
                         if len(_yr_hits) == 1 else -25)
            score += _yr_score
            details.append((f"羊刃（日干{_day_gan_yr}见{'、'.join(_yr_hits)}）", _yr_score))

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
            # P1-C-1-a：与函数内累加值同步，每处六害 -6
            details.append((reason, -6))
    
    # 4.7 三刑检查（排除示例时柱）
    sanxing_score, sanxing_reasons = check_sanxing_penalty(sizhu_no_hour)
    if sanxing_score != 0:
        score += sanxing_score
        for reason in sanxing_reasons:
            # 根据内容确定扣分
            if '无恩之刑' in reason or '恃势之刑' in reason or '无礼之刑' in reason:
                details.append((reason, -8))
            elif '自刑' in reason:
                # P1-C-1-b：与函数内累加值同步，自刑 -8
                details.append((reason, -8))
    
    # 5. 日课年月日柱内部合局评分（排除示例时柱）
    zhiju_score, zhiju_reason = get_zhiju_score(
        sizhu_no_hour, sizhu.get('时柱', '')[1:2] if sizhu.get('时柱') else '')
    if zhiju_reason:
        score += zhiju_score
        details.append((zhiju_reason, zhiju_score))
    
    # 6. 时辰评分已移除（彻底分离）：日课评分不含时柱因素，
    #    时辰吉凶由十二时辰婚嫁吉凶表（嫁娶神煞扩展.get_lucky_hours）独立评估
    
    # 7. 计算总分并确定等级
    result['raw_score'] = score          # 明细合计（可能为负），供展示层说明归零
    result['score'] = max(0, score)
    result['details'] = details
    
    # （2026-10-25 阶段3·方案C：删除150/130/110/90/70内部等级映射死代码——
    #  产品链唯一等级出口为 评分器._get_level(105/100/85/75/60)，本函数返回的
    #  level 无任何消费方；'level' 键保留为空串以维持返回结构兼容。）

    # 生成理由文本
    positive = [f"{d[0]}" for d in details if d[1] > 0]
    negative = [f"{d[0]}" for d in details if d[1] < 0]
    
    reason_parts = []
    if positive:
        reason_parts.append('；'.join(positive))
    if negative:
        reason_parts.append(f"忌：{'；'.join(negative)}")
    
    result['reason'] = '；'.join(reason_parts) if reason_parts else '普通日课'

    # 否决日：明细完整保留供追溯，理由前置否决原因（等级判定统一在评分器
    # _get_level 完成，本函数不再自赋等级——2026-10-25 阶段3·方案C）
    # 日支冲新娘本命/阴胎/阳气等否决项在第4节才写入 result['reject_reason']，此处回读
    reject_reason = result.get('reject_reason') or reject_reason
    is_reject = bool(reject_reason)
    if is_reject:
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
    
    # 模拟新郎八字（2026-10-11 B1：本命三煞改查男命，须有年柱）
    groom_bazi = {
        'year_gan': '庚',
        'year_zhi': '子',
        'ri_gan': '庚',
        'ri_zhi': '酉'
    }
    
    result = score_marriage_day(test_date, bride_bazi, groom_bazi)
    print("婚嫁日课评分测试结果：")
    print(f"日期：{test_date}")
    print(f"评分：{result['score']}")
    print(f"理由：{result['reason']}")
    print(f"详情：{result['details']}")
    print(f"警告：{result['warnings']}")

if __name__ == '__main__':
    test_score_marriage()
