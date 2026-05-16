# -*- coding: utf-8 -*-
"""
婚嫁日课评分算法（基于《协纪辨方书》）
"""

try:
    from .marriage_shensha import (
        get_day_ganzhi, is_month_break, is_year_break, is_sili_sijue, is_shangshuo,
        is_bujiang_day, is_tiande_day, is_yuede_day, is_tiandehe_day, is_yuedehe_day,
        is_huangdao_day, get_jianchu, is_liuhe, is_sanhe, is_sansha, is_chong_gan,
        get_fuxing_zixing, get_yintai, get_yangqi, is_chong, is_xing, is_hai
    )
except ImportError:
    # 直接导入marriage_shensha模块
    import sys
    import os
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from marriage_shensha import (
        get_day_ganzhi, is_month_break, is_year_break, is_sili_sijue, is_shangshuo,
        is_bujiang_day, is_tiande_day, is_yuede_day, is_tiandehe_day, is_yuedehe_day,
        is_huangdao_day, get_jianchu, is_liuhe, is_sanhe, is_sansha, is_chong_gan,
        get_fuxing_zixing, get_yintai, get_yangqi, is_chong, is_xing, is_hai
    )

def score_marriage_day(date_obj, bride_bazi, groom_bazi=None):
    """
    对某个具体日子进行婚嫁评分
    bride_bazi: {'year_zhi':,'day_gan':,'day_zhi':} 至少需要年支、日干支
    groom_bazi: 同上，可选
    返回总分（0-100+），等级，详细得分明细
    """
    score = 100
    details = []
    reasons = []
    
    # ========== 一票否决项（直接判为不可用） ==========
    # 1. 月破、岁破
    if is_month_break(date_obj):
        return 0, '凶（月破）', ['月破大凶，不可用'], []
    if bride_bazi and is_year_break(date_obj, bride_bazi['year_zhi']):
        return 0, '凶（岁破）', ['与新娘年支相冲，不可用'], []
    if groom_bazi and is_year_break(date_obj, groom_bazi['year_zhi']):
        return 0, '凶（岁破）', ['与新郎年支相冲，不可用'], []
    
    # 2. 四离四绝（实际需精确节气）
    if is_sili_sijue(date_obj):
        return 0, '凶（四离四绝）', ['四离四绝日，诸事不宜'], []
    
    # 3. 上朔日
    if is_shangshuo(date_obj):
        return 0, '凶（上朔日）', ['上朔日，阴阳德俱尽，忌嫁娶'], []
    
    # ========== 吉神加分 ==========
    # 不将日（+30分）
    if is_bujiang_day(date_obj):
        score += 30
        reasons.append('不将日')
        details.append(('不将日', 30))
    
    # 天德日（+20）
    if is_tiande_day(date_obj):
        score += 20
        reasons.append('天德')
        details.append(('天德', 20))
    
    # 月德日（+20）
    if is_yuede_day(date_obj):
        score += 20
        reasons.append('月德')
        details.append(('月德', 20))
    
    # 天德合、月德合（各+10）
    if is_tiandehe_day(date_obj):
        score += 10
        reasons.append('天德合')
        details.append(('天德合', 10))
    if is_yuedehe_day(date_obj):
        score += 10
        reasons.append('月德合')
        details.append(('月德合', 10))
    
    # 黄道日（+15）
    if is_huangdao_day(date_obj):
        jianchu = get_jianchu(date_obj)
        score += 15
        reasons.append(f'{jianchu}日（黄道）')
        details.append(('黄道', 15))
    
    # 三合、六合与新娘（+10）
    if bride_bazi:
        _, day_zhi = get_day_ganzhi(date_obj)
        bride_zhi = bride_bazi.get('day_zhi', bride_bazi.get('year_zhi'))
        if is_liuhe(day_zhi, bride_zhi):
            score += 10
            reasons.append('与新娘六合')
            details.append(('六合', 10))
        if is_sanhe(day_zhi, bride_zhi):
            score += 8
            reasons.append('与新娘三合')
            details.append(('三合', 8))
    
    # ========== 凶神扣分 ==========
    # 三煞（-30）
    if bride_bazi and is_sansha(date_obj, bride_bazi['year_zhi']):
        score -= 30
        reasons.append('犯三煞')
        details.append(('三煞', -30))
    
    # 冲夫星（-50，严重）
    if bride_bazi and 'day_gan' in bride_bazi:
        bride_day_gan = bride_bazi['day_gan']
        fuxing = get_fuxing_zixing(bride_day_gan)['fu']
        day_gan, _ = get_day_ganzhi(date_obj)
        if is_chong_gan(day_gan, fuxing):
            score -= 50
            reasons.append('冲夫星')
            details.append(('冲夫星', -50))
    
    # 冲子星（-30）
    if bride_bazi and 'day_gan' in bride_bazi:
        bride_day_gan = bride_bazi['day_gan']
        zixing = get_fuxing_zixing(bride_day_gan)['zi']
        day_gan, _ = get_day_ganzhi(date_obj)
        if is_chong_gan(day_gan, zixing):
            score -= 30
            reasons.append('冲子星')
            details.append(('冲子星', -30))
    
    # 犯阴胎（-40）
    if bride_bazi and 'month_gan' in bride_bazi and 'month_zhi' in bride_bazi:
        yt_gan, yt_zhi = get_yintai(bride_bazi['month_gan'], bride_bazi['month_zhi'])
        day_gan, day_zhi = get_day_ganzhi(date_obj)
        if (day_gan == yt_gan and day_zhi == yt_zhi) or is_chong(day_zhi, yt_zhi):
            score -= 40
            reasons.append('犯阴胎')
            details.append(('阴胎', -40))
    
    # 犯阳气（-40）
    if bride_bazi and 'month_gan' in bride_bazi and 'month_zhi' in bride_bazi:
        yq_gan, yq_zhi = get_yangqi(bride_bazi['month_gan'], bride_bazi['month_zhi'])
        day_gan, day_zhi = get_day_ganzhi(date_obj)
        if (day_gan == yq_gan and day_zhi == yq_zhi) or is_chong(day_zhi, yq_zhi):
            score -= 40
            reasons.append('犯阳气')
            details.append(('阳气', -40))
    
    # 刑害（-15）
    if bride_bazi:
        _, day_zhi = get_day_ganzhi(date_obj)
        bride_zhi = bride_bazi.get('day_zhi', bride_bazi.get('year_zhi'))
        if is_xing(day_zhi, bride_zhi):
            score -= 15
            reasons.append('相刑')
            details.append(('刑', -15))
        if is_hai(day_zhi, bride_zhi):
            score -= 15
            reasons.append('相害')
            details.append(('害', -15))
    
    # 建除凶神（执、破、闭等减分）
    jianchu = get_jianchu(date_obj)
    if jianchu in ['执', '破', '闭']:
        score -= 10
        reasons.append(f'{jianchu}日凶')
        details.append((f'{jianchu}日', -10))
    
    # 确定等级
    if score >= 150:
        level = '上吉'
    elif score >= 120:
        level = '大吉'
    elif score >= 100:
        level = '吉'
    elif score >= 70:
        level = '平'
    else:
        level = '凶'
    
    return score, level, reasons, details