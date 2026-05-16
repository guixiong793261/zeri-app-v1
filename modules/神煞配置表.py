# -*- coding: utf-8 -*-
"""
二十四山神煞配置表
根据用户提供的速查表整理
"""

# ==================== 神煞权重配置 ====================
SHEN_SHA_WEIGHT = {
    '一票否决': ['山家三煞', '星曜煞', '正阴府', '岁破', '月破', '年克山运'],
    '高权重': {'星曜煞': -50, '消灭煞': -35, '傍阴府': -50},
    '中权重': {'山方煞': -25, '弓箭煞': -25, '剑锋煞': -20, '八曜煞': -40, '冲丁煞': -15, '日流太岁': -15},
    '低权重': {'巡山罗睺': -12, '戊己都天': -15, '天地燥火': -10, '文曲煞': -10}
}

# ==================== 山家三煞配置 ====================
# 三合局 -> 三煞方位 -> 所煞之山
SHANJIA_SANSHA_MAP = {
    '申子辰': {
        'sansha_zhis': ['巳', '丙', '午', '丁', '未'],
        'affected_mountains': ['巳山', '丙山', '午山', '丁山', '未山']
    },
    '寅午戌': {
        'sansha_zhis': ['亥', '壬', '子', '癸', '丑'],
        'affected_mountains': ['亥山', '壬山', '子山', '癸山', '丑山']
    },
    '亥卯未': {
        'sansha_zhis': ['申', '庚', '酉', '辛', '戌'],
        'affected_mountains': ['申山', '庚山', '酉山', '辛山', '戌山']
    },
    '巳酉丑': {
        'sansha_zhis': ['寅', '甲', '卯', '乙', '辰'],
        'affected_mountains': ['寅山', '甲山', '卯山', '乙山', '辰山']
    }
}

# ==================== 星曜煞配置（按坐山五行） ====================
# 坐山五行 -> 坐山列表 -> 忌日
XINGYAO_SHA_MAP = {
    '水': {
        'mountains': ['亥山', '壬山', '子山', '癸山'],
        '忌日': ['戊辰', '己未', '戊戌', '己丑']
    },
    '木': {
        'mountains': ['寅山', '甲山', '卯山', '乙山', '巽山'],
        '忌日': ['庚申', '辛酉']
    },
    '火': {
        'mountains': ['巳山', '丙山', '午山', '丁山'],
        '忌日': ['壬子', '癸亥']
    },
    '金': {
        'mountains': ['申山', '庚山', '酉山', '辛山', '乾山'],
        '忌日': ['丙午', '丁巳']
    },
    '土': {
        'mountains': ['辰山', '戌山', '丑山', '未山', '艮山', '坤山'],
        '忌日': ['甲寅', '乙卯']
    }
}

# ==================== 八曜煞配置（按八卦） ====================
# 八卦 -> 所辖山 -> 曜煞忌日
BAYAO_SHA_MAP = {
    '坎': {
        'mountains': ['壬山', '子山', '癸山'],
        '忌日': ['戊辰', '戊戌']
    },
    '艮': {
        'mountains': ['丑山', '艮山', '寅山'],
        '忌日': ['丙寅']
    },
    '震': {
        'mountains': ['甲山', '卯山', '乙山'],
        '忌日': ['庚申']
    },
    '巽': {
        'mountains': ['辰山', '巽山', '巳山'],
        '忌日': ['辛酉']
    },
    '离': {
        'mountains': ['丙山', '午山', '丁山'],
        '忌日': ['己亥']
    },
    '坤': {
        'mountains': ['未山', '坤山', '申山'],
        '忌日': ['乙卯', '癸卯']
    },
    '兑': {
        'mountains': ['庚山', '酉山', '辛山'],
        '忌日': ['丁巳']
    },
    '乾': {
        'mountains': ['戌山', '乾山', '亥山'],
        '忌日': ['甲午', '壬午']
    }
}

# ==================== 山方煞配置（按坐山） ====================
SHANFANG_SHA_MAP = {
    '壬山': {'忌日': ['己亥', '丙寅'], '忌时': ['己亥', '丙寅']},
    '子山': {'忌日': ['庚申', '戊辰'], '忌时': ['庚申', '戊辰']},
    '癸山': {'忌日': ['辛酉', '戊辰'], '忌时': ['辛酉', '戊辰']},
    '丑山': {'忌日': ['丙寅', '乙卯'], '忌时': ['丙寅', '乙卯']},
    '艮山': {'忌日': ['壬午', '癸未'], '忌时': ['壬午', '癸未']},
    '寅山': {'忌日': ['乙卯', '壬午'], '忌时': ['乙卯', '壬午']},
    '甲山': {'忌日': ['己亥', '丙寅'], '忌时': ['己亥', '丙寅']},
    '卯山': {'忌日': ['庚申', '辛酉'], '忌时': ['庚申', '辛酉']},
    '乙山': {'忌日': ['辛酉', '庚申'], '忌时': ['辛酉', '庚申']},
    '辰山': {'忌日': ['丙寅', '丁巳'], '忌时': ['丙寅', '丁巳']},
    '巽山': {'忌日': ['辛酉', '戊辰'], '忌时': ['辛酉', '戊辰']},
    '巳山': {'忌日': ['丁巳', '乙卯'], '忌时': ['丁巳', '乙卯']},
    '丙山': {'忌日': ['壬午', '庚申'], '忌时': ['壬午', '庚申']},
    '午山': {'忌日': ['甲午', '壬午', '庚申'], '忌时': ['甲午', '壬午', '庚申']},
    '丁山': {'忌日': ['癸未', '戊戌'], '忌时': ['癸未', '戊戌']},
    '未山': {'忌日': ['辛酉', '戊辰'], '忌时': ['辛酉', '戊辰']},
    '坤山': {'忌日': ['乙卯', '癸卯'], '忌时': ['乙卯', '癸卯']},
    '申山': {'忌日': ['乙卯', '癸卯'], '忌时': ['乙卯', '癸卯']},
    '庚山': {'忌日': ['壬午', '癸未'], '忌时': ['壬午', '癸未']},
    '酉山': {'忌日': ['甲午', '丁巳'], '忌时': ['甲午', '丁巳']},
    '辛山': {'忌日': ['丙寅', '甲午'], '忌时': ['丙寅', '甲午']},
    '戌山': {'忌日': ['癸未', '壬午'], '忌时': ['癸未', '壬午']},
    '乾山': {'忌日': ['丙寅', '己亥'], '忌时': ['丙寅', '己亥']},
    '亥山': {'忌日': ['乙卯', '壬午'], '忌时': ['乙卯', '壬午']}
}

# ==================== 消灭煞配置（按坐山和节气） ====================
# 格式：坐山 -> {节气: [忌日列表]}
XIAOMIE_SHA_MAP = {
    '壬山': {'夏至后五天': ['辛未']},
    '癸山': {'冬至后五天': ['庚午']},
    '艮山': {'处暑后五天': ['乙卯'], '小雪后五天': ['癸酉']},
    '甲山': {'夏至后五天': ['辛丑'], '秋分后五天': ['辛未']},
    '乙山': {'冬至后五天': ['庚子'], '春分后五天': ['庚午']},
    '巽山': {'霜降后五天': ['丙子'], '大暑后五天': ['丙午']},
    '丙山': {'处暑后五天': ['乙卯'], '小雪后五天': ['癸酉']},
    '丁山': {'雨水后五天': ['甲辰'], '小满后五天': ['壬戌']},
    '坤山': {'冬至后五天': ['庚子'], '春分后五天': ['庚午']},
    '庚山': {'大寒后五天': ['丁卯'], '谷雨后五天': ['丁酉']},
    '辛山': {'霜降后五天': ['丙子'], '大暑后五天': ['丙午']},
    '乾山': {'夏至后五天': ['辛丑'], '秋分后五天': ['辛未']}
}

# ==================== 冲丁煞配置（按坐山和兼向） ====================
# 格式：坐山 -> {兼向: 忌日}
CHONGDING_SHA_MAP = {
    '壬山': {'兼亥': '丁巳', '兼子': '辛亥'},
    '子山': {'兼壬': '丙午', '兼癸': '庚午'},
    '癸山': {'兼子': '丙辰', '兼丑': '庚辰'},
    '丑山': {'兼癸': '丁未', '兼艮': '辛丑'},
    '艮山': {'兼丑': '丁未', '兼寅': '辛未'},
    '寅山': {'兼艮': '丙申', '兼甲': '庚申'},
    '甲山': {'兼寅': '丙申', '兼卯': '庚申'},
    '卯山': {'兼甲': '丁酉', '兼乙': '辛酉'},
    '乙山': {'兼卯': '丁酉', '兼辰': '癸酉'},
    '辰山': {'兼乙': '丙戌', '兼巽': '庚戌'},
    '巽山': {'兼辰': '丙辰', '兼巳': '庚辰'},
    '巳山': {'兼巽': '丁巳', '兼丙': '辛巳'},
    '丙山': {'兼巳': '丁亥', '兼午': '辛亥'},
    '午山': {'兼丙': '丙子', '兼丁': '庚子'},
    '丁山': {'兼午': '丙午', '兼未': '庚午'},
    '未山': {'兼丁': '丁丑', '兼坤': '辛丑'},
    '坤山': {'兼未': '丁未', '兼申': '辛未'},
    '申山': {'兼坤': '丙寅', '兼庚': '庚寅'},
    '庚山': {'兼申': '丙寅', '兼酉': '庚寅'},
    '酉山': {'兼庚': '丁卯', '兼辛': '辛卯'},
    '辛山': {'兼酉': '丁巳', '兼戌': '辛巳'},
    '戌山': {'兼辛': '丙辰', '兼乾': '庚辰'},
    '乾山': {'兼戌': '丙辰', '兼亥': '庚辰'},
    '亥山': {'兼乾': '丁巳', '兼壬': '辛巳'}
}

# ==================== 弓箭煞配置（按坐山类型） ====================
# 天干山：甲、乙、丙、丁、庚、辛、壬、癸
# 地支山和四维山无弓箭煞
GONGJIAN_SHA_MAP = {
    '卯酉类': ['甲山', '乙山', '庚山', '辛山'],  # 忌卯酉二支全
    '子午类': ['丙山', '丁山', '壬山', '癸山']   # 忌子午二支全
}

# ==================== 剑锋煞配置（按坐山） ====================
# 仅安葬忌，建造不忌
JIANFENG_SHA_MAP = {
    '寅山': ['寅月'],
    '申山': ['寅月'],
    '巳山': ['寅月'],
    '亥山': ['寅月'],
    '辰山': ['戌月'],
    '戌山': ['辰月'],
    '未山': ['丑月'],
    '丑山': ['未月'],
    '丙山': ['巳月'],  # 亥年巳月
    '乾山': ['戌月'],  # 辰年戌月
    '坤山': ['戌月'],  # 辰年戌月
    '艮山': ['丑月']   # 未年丑月
}

# ==================== 日流太岁配置 ====================
# 以年干起五虎遁，遁至坐山的墓库地支
RILIU_TAISUI_MAP = {
    '壬山': '忌戊子旬克山日',
    '子山': '忌戊子旬克山日',
    '癸山': '忌戊子旬克山日',
    '丑山': '忌己丑旬克山日',
    '艮山': '忌己丑旬克山日',
    '寅山': '忌庚寅旬克山日',
    '甲山': '忌庚寅旬克山日',
    '卯山': '忌辛卯旬克山日',
    '乙山': '忌辛卯旬克山日',
    '辰山': '忌壬辰旬克山日',
    '巽山': '忌壬辰旬克山日',
    '巳山': '忌癸巳旬克山日',
    '丙山': '忌癸巳旬克山日',
    '午山': '忌甲午旬克山日',
    '丁山': '忌甲午旬克山日',
    '未山': '忌乙未旬克山日',
    '坤山': '忌乙未旬克山日',
    '申山': '忌丙申旬克山日',
    '庚山': '忌丙申旬克山日',
    '酉山': '忌丁酉旬克山日',
    '辛山': '忌丁酉旬克山日',
    '戌山': '忌戊戌旬克山日',
    '乾山': '忌戊戌旬克山日',
    '亥山': '忌己亥旬克山日'
}

# ==================== 文曲煞配置（按坐山） ====================
# 文曲煞忌旬空
WENQU_SHA_MAP = {
    '壬山': ['甲辰旬'],
    '子山': ['甲午旬'],
    '癸山': ['甲辰旬'],
    '丑山': ['甲午旬'],
    '艮山': ['甲申旬'],
    '寅山': ['甲午旬'],
    '甲山': ['甲辰旬'],
    '卯山': ['甲午旬'],
    '乙山': ['甲午旬'],
    '辰山': ['甲午旬'],
    '巽山': ['甲申旬'],
    '巳山': ['甲寅旬'],
    '丙山': {'兼巳': ['甲午旬'], '兼午': ['甲申旬']},
    '午山': ['甲辰旬'],
    '丁山': ['甲寅旬'],
    '未山': ['甲申旬'],
    '坤山': ['甲戌旬'],
    '申山': ['甲戌旬'],
    '庚山': ['甲申旬'],
    '酉山': ['甲午旬'],
    '辛山': ['甲申旬'],
    '戌山': ['甲辰旬'],
    '乾山': ['甲子旬'],
    '亥山': ['甲寅旬']
}

# ==================== 戊己都天配置（按坐山） ====================
# 只忌岁干或岁支纳音克山家的年份
WUJI_DUTIAN_MAP = {
    '未山': ['戊', '癸'],
    '乾山': ['丙', '辛'],
    '甲山': ['乙', '庚'],
    '坤山': ['丙', '辛'],
    '艮山': ['甲', '己'],
    '巽山': ['甲', '己']
}

# ==================== 天地燥火配置（按坐山） ====================
# 天燥火忌修造，地燥火忌安葬
TIANDI_ZAOHUO_MAP = {
    '壬山': {'天燥火': ['寅时', '申时'], '地燥火': ['巳时', '亥时']},
    '子山': {'天燥火': ['寅时', '申时'], '地燥火': ['巳时', '亥时']},
    '癸山': {'天燥火': ['寅时', '申时'], '地燥火': ['巳时', '亥时']},
    '丑山': {'天燥火': ['巳时', '亥时'], '地燥火': ['寅时', '申时']},
    '艮山': {'天燥火': ['巳时', '亥时'], '地燥火': ['寅时', '申时']},
    '寅山': {'天燥火': ['巳时', '亥时'], '地燥火': ['寅时', '申时']},
    '甲山': {'天燥火': ['寅时', '申时'], '地燥火': ['巳时', '亥时']},
    '卯山': {'天燥火': ['寅时', '申时'], '地燥火': ['巳时', '亥时']},
    '乙山': {'天燥火': ['寅时', '申时'], '地燥火': ['巳时', '亥时']},
    '辰山': {'天燥火': ['巳时', '亥时'], '地燥火': ['寅时', '申时']},
    '巽山': {'天燥火': ['巳时', '亥时'], '地燥火': ['寅时', '申时']},
    '巳山': {'天燥火': ['巳时', '亥时'], '地燥火': ['寅时', '申时']},
    '丙山': {'天燥火': ['子时', '午时'], '地燥火': ['卯时', '酉时']},
    '午山': {'天燥火': ['子时', '午时'], '地燥火': ['卯时', '酉时']},
    '丁山': {'天燥火': ['子时', '午时'], '地燥火': ['卯时', '酉时']},
    '未山': {'天燥火': ['巳时', '亥时'], '地燥火': ['寅时', '申时']},
    '坤山': {'天燥火': ['巳时', '亥时'], '地燥火': ['寅时', '申时']},
    '申山': {'天燥火': ['巳时', '亥时'], '地燥火': ['寅时', '申时']},
    '庚山': {'天燥火': ['寅时', '申时'], '地燥火': ['巳时', '亥时']},
    '酉山': {'天燥火': ['寅时', '申时'], '地燥火': ['巳时', '亥时']},
    '辛山': {'天燥火': ['寅时', '申时'], '地燥火': ['巳时', '亥时']},
    '戌山': {'天燥火': ['丑时', '未时'], '地燥火': ['辰时', '戌时']},
    '乾山': {'天燥火': ['丑时', '未时'], '地燥火': ['辰时', '戌时']},
    '亥山': {'天燥火': ['丑时', '未时'], '地燥火': ['辰时', '戌时']}
}

# ==================== 巡山罗睺配置（按坐山） ====================
# 巡山罗睺忌立向与修方
XUNSHAN_LUOHU_MAP = {
    '甲山': ['寅'],
    '乙山': ['丑'],
    '丙山': ['巳'],
    '丁山': ['未'],
    '乾山': ['亥', '子', '戌'],
    '坤山': ['巳', '申', '辰'],
    '艮山': ['寅', '午', '卯'],
    '巽山': ['子', '辰', '寅']
}

# ==================== 神煞检测函数 ====================

def check_shanjia_sansha(mountain, year_zhi, month_zhi, day_zhi, hour_zhi):
    """检查山家三煞"""
    for sanhe, config in SHANJIA_SANSHA_MAP.items():
        if mountain in config['affected_mountains']:
            sansha_zhis = config['sansha_zhis']
            if year_zhi in sansha_zhis or month_zhi in sansha_zhis or day_zhi in sansha_zhis or hour_zhi in sansha_zhis:
                return True, f'{mountain}犯山家三煞（{sanhe}局）'
    return False, ''

def check_xingyao_sha(mountain, day_ganzhi):
    """检查星曜煞（仅日柱）"""
    for wuxing, config in XINGYAO_SHA_MAP.items():
        if mountain in config['mountains']:
            if day_ganzhi in config['忌日']:
                return True, f'{mountain}犯星曜煞（{day_ganzhi}日）'
    return False, ''

def check_bayao_sha(mountain, day_ganzhi, hour_ganzhi):
    """检查八曜煞"""
    for gua, config in BAYAO_SHA_MAP.items():
        if mountain in config['mountains']:
            if day_ganzhi in config['忌日']:
                return True, f'{mountain}犯八曜煞（{day_ganzhi}日）', 'day'
            if hour_ganzhi in config['忌日']:
                return True, f'{mountain}犯八曜煞（{hour_ganzhi}时）', 'hour'
    return False, '', ''

def check_shanfang_sha(mountain, day_ganzhi, hour_ganzhi):
    """检查山方煞"""
    config = SHANFANG_SHA_MAP.get(mountain)
    if config:
        if day_ganzhi in config['忌日']:
            return True, f'{mountain}犯山方煞（{day_ganzhi}日）', 'day'
        if hour_ganzhi in config['忌时']:
            return True, f'{mountain}犯山方煞（{hour_ganzhi}时）', 'hour'
    return False, '', ''

def check_xiaomie_sha(mountain, day_ganzhi, solar_term, days_after_term):
    """检查消灭煞"""
    config = XIAOMIE_SHA_MAP.get(mountain)
    if config and days_after_term <= 5:
        term_key = f'{solar_term}后五天'
        if term_key in config and day_ganzhi in config[term_key]:
            return True, f'{mountain}犯消灭煞（{day_ganzhi}日，{solar_term}后{days_after_term}天）'
    return False, ''

def check_chongding_sha(mountain, jianxiang, day_ganzhi, hour_ganzhi):
    """检查冲丁煞"""
    config = CHONGDING_SHA_MAP.get(mountain)
    if config and jianxiang:
        ji_ri = config.get(jianxiang)
        if ji_ri:
            if day_ganzhi == ji_ri:
                return True, f'{mountain}{jianxiang}犯冲丁煞（{day_ganzhi}日）', 'day'
            if hour_ganzhi == ji_ri:
                return True, f'{mountain}{jianxiang}犯冲丁煞（{hour_ganzhi}时）', 'hour'
    return False, '', ''

def check_gongjian_sha(mountain, year_zhi, month_zhi, day_zhi, hour_zhi):
    """检查弓箭煞"""
    # 获取所有地支
    all_zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]
    
    if mountain in GONGJIAN_SHA_MAP['卯酉类']:
        if '卯' in all_zhis and '酉' in all_zhis:
            return True, f'{mountain}犯弓箭煞（卯酉二支全见）'
    elif mountain in GONGJIAN_SHA_MAP['子午类']:
        if '子' in all_zhis and '午' in all_zhis:
            return True, f'{mountain}犯弓箭煞（子午二支全见）'
    return False, ''

def check_jianfeng_sha(mountain, month, event_type):
    """检查剑锋煞（仅安葬忌）"""
    if event_type != '安葬':
        return False, ''
    
    config = JIANFENG_SHA_MAP.get(mountain)
    if config and f'{month}月' in config:
        return True, f'{mountain}犯剑锋煞（{month}月）'
    return False, ''

def check_riliu_taisui(mountain, day_ganzhi):
    """检查日流太岁"""
    config = RILIU_TAISUI_MAP.get(mountain)
    if config:
        return True, f'{mountain}{config}'
    return False, ''

def check_wenqu_sha(mountain, xun, jianxiang=None):
    """检查文曲煞"""
    config = WENQU_SHA_MAP.get(mountain)
    if not config:
        return False, ''
    
    if isinstance(config, dict) and jianxiang:
        ji_xun_list = config.get(jianxiang, [])
    else:
        ji_xun_list = config if isinstance(config, list) else []
    
    if xun in ji_xun_list:
        return True, f'{mountain}犯文曲煞（{xun}）'
    return False, ''

def check_wuji_dutian(mountain, year_gan):
    """检查戊己都天"""
    config = WUJI_DUTIAN_MAP.get(mountain)
    if config and year_gan in config:
        return True, f'{mountain}犯戊己都天（{year_gan}年）'
    return False, ''

def check_tiandi_zaohuo(mountain, hour_zhi, event_type):
    """检查天地燥火"""
    config = TIANDI_ZAOHUO_MAP.get(mountain)
    if not config:
        return False, ''
    
    hour_str = f'{hour_zhi}时'
    
    if event_type == '修造':
        if hour_str in config.get('天燥火', []):
            return True, f'{mountain}犯天燥火（{hour_str}）'
    elif event_type == '安葬':
        if hour_str in config.get('地燥火', []):
            return True, f'{mountain}犯地燥火（{hour_str}）'
    return False, ''

def check_xunshan_luohu(mountain, year_zhi):
    """检查巡山罗睺"""
    config = XUNSHAN_LUOHU_MAP.get(mountain)
    if config and year_zhi in config:
        return True, f'{mountain}犯巡山罗睺（{year_zhi}年）'
    return False, ''

# ==================== 神煞检测主函数 ====================
def check_all_shensha(mountain, jianxiang, event_type, year_zhi, month_zhi, day_zhi, hour_zhi, 
                      day_ganzhi, hour_ganzhi, solar_term, days_after_term):
    """
    检查所有神煞
    
    Returns:
        list: 神煞结果列表，每个元素包含 (名称, 描述, 权重, 级别)
    """
    results = []
    
    # 山家三煞（一票否决）
    flag, desc = check_shanjia_sansha(mountain, year_zhi, month_zhi, day_zhi, hour_zhi)
    if flag:
        results.append(('山家三煞', desc, '一票否决', '大凶'))
    
    # 星曜煞（日柱犯则一票否决）
    flag, desc = check_xingyao_sha(mountain, day_ganzhi)
    if flag:
        results.append(('星曜煞', desc, '一票否决', '大凶'))
    
    # 八曜煞
    flag, desc, level = check_bayao_sha(mountain, day_ganzhi, hour_ganzhi)
    if flag:
        weight = -40 if level == 'day' else -10
        results.append(('八曜煞', desc, weight, '大凶' if level == 'day' else '小凶'))
    
    # 山方煞
    flag, desc, level = check_shanfang_sha(mountain, day_ganzhi, hour_ganzhi)
    if flag:
        weight = -25 if level == 'day' else -10
        results.append(('山方煞', desc, weight, '大凶' if level == 'day' else '小凶'))
    
    # 消灭煞
    flag, desc = check_xiaomie_sha(mountain, day_ganzhi, solar_term, days_after_term)
    if flag:
        results.append(('消灭煞', desc, -35, '大凶'))
    
    # 冲丁煞
    flag, desc, level = check_chongding_sha(mountain, jianxiang, day_ganzhi, hour_ganzhi)
    if flag:
        weight = -15 if level == 'day' else -8
        results.append(('冲丁煞', desc, weight, '大凶' if level == 'day' else '小凶'))
    
    # 弓箭煞
    flag, desc = check_gongjian_sha(mountain, year_zhi, month_zhi, day_zhi, hour_zhi)
    if flag:
        results.append(('弓箭煞', desc, -25, '大凶'))
    
    # 剑锋煞（仅安葬）
    flag, desc = check_jianfeng_sha(mountain, month_zhi, event_type)
    if flag:
        results.append(('剑锋煞', desc, -20, '大凶'))
    
    # 日流太岁
    flag, desc = check_riliu_taisui(mountain, day_ganzhi)
    if flag:
        results.append(('日流太岁', desc, -15, '中凶'))
    
    # 文曲煞
    # 需要计算旬信息，简化处理：日柱干支直接判断
    # 实际应用中需要根据日柱计算旬
    # flag, desc = check_wenqu_sha(mountain, xun, jianxiang)
    # if flag:
    #     results.append(('文曲煞', desc, -10, '小凶'))
    
    # 戊己都天
    flag, desc = check_wuji_dutian(mountain, year_zhi)
    if flag:
        results.append(('戊己都天', desc, -15, '中凶'))
    
    # 天地燥火
    flag, desc = check_tiandi_zaohuo(mountain, hour_zhi, event_type)
    if flag:
        results.append(('天地燥火', desc, -10, '小凶'))
    
    # 巡山罗睺
    flag, desc = check_xunshan_luohu(mountain, year_zhi)
    if flag:
        results.append(('巡山罗睺', desc, -12, '中凶'))
    
    return results