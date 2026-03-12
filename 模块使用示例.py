# -*- coding: utf-8 -*-
"""
================================================================================
模块使用示例
================================================================================
展示如何在新旧模块之间进行选择和使用

推荐顺序：
1. 优先使用 八字工具整合.py（统一数据源）
2. 新功能使用 事主八字分析.py（专为择日设计）
3. 旧模块保持兼容，逐步迁移
================================================================================
"""

# ============================================================================
# 示例1：基础工具函数（推荐使用整合模块）
# ============================================================================

def example_basic_tools():
    """基础工具函数示例"""
    print("=" * 80)
    print("示例1：基础工具函数")
    print("=" * 80)
    
    # 推荐：从整合模块导入
    from modules.八字工具整合 import (
        GAN_WUXING, ZHI_WUXING,
        get_gan_wuxing, get_zhi_wuxing,
        get_shishen, get_canggan
    )
    
    # 查询天干五行
    print(f"\n甲的五行: {get_gan_wuxing('甲')}")  # 木
    print(f"丙的五行: {GAN_WUXING['丙']}")  # 火
    
    # 查询地支五行
    print(f"\n寅的五行: {get_zhi_wuxing('寅')}")  # 木
    print(f"申的五行: {ZHI_WUXING['申']}")  # 金
    
    # 查询藏干
    print(f"\n寅的藏干（加权）: {get_canggan('寅', weighted=True)}")
    print(f"寅的藏干（简化）: {get_canggan('寅', weighted=False)}")
    
    # 计算十神
    print(f"\n日干甲见乙: {get_shishen('甲', '乙')}")  # 劫财
    print(f"日干甲见丙: {get_shishen('甲', '丙')}")  # 食神
    print(f"日干甲见庚: {get_shishen('甲', '庚')}")  # 七杀


# ============================================================================
# 示例2：地支关系（新功能）
# ============================================================================

def example_zhi_relations():
    """地支关系示例"""
    print("\n" + "=" * 80)
    print("示例2：地支关系")
    print("=" * 80)
    
    from modules.八字工具整合 import (
        check_liuhe, check_liuchong, check_liuhai,
        check_sanxing, check_sanhe, check_sanhui
    )
    
    # 六合
    result = check_liuhe('子', '丑')
    print(f"\n子丑合: {result}")  # 土
    
    # 六冲
    result = check_liuchong('子', '午')
    print(f"子午冲: {result}")  # True
    
    # 六害
    result = check_liuhai('子', '未')
    print(f"子未害: {result}")  # True
    
    # 三刑
    result = check_sanxing('子', '卯')
    print(f"子卯刑: {result}")  # 无礼之刑
    
    # 三合
    result = check_sanhe(['申', '子', '辰'])
    print(f"申子辰三合: {result}")  # 水
    
    # 三会
    result = check_sanhui(['寅', '卯', '辰'])
    print(f"寅卯辰三会: {result}")  # 木


# ============================================================================
# 示例3：十二长生（新功能）
# ============================================================================

def example_zhangsheng():
    """十二长生示例"""
    print("\n" + "=" * 80)
    print("示例3：十二长生")
    print("=" * 80)
    
    from modules.八字工具整合 import (
        get_zhangsheng, get_zhangsheng_power, get_zhangsheng_explanation
    )
    
    day_gan = '甲'
    zhis = ['亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌']
    
    print(f"\n日干{day_gan}的十二长生状态：")
    for zhi in zhis:
        state = get_zhangsheng(day_gan, zhi)
        power = get_zhangsheng_power(state)
        explanation = get_zhangsheng_explanation(state)
        print(f"  {zhi}: {state} (力量{power}) - {explanation[:20]}...")


# ============================================================================
# 示例4：事主八字分析（专为择日设计）
# ============================================================================

def example_shizhu_analysis():
    """事主八字分析示例"""
    print("\n" + "=" * 80)
    print("示例4：事主八字分析")
    print("=" * 80)
    
    from modules.事主八字分析 import ShiZhuBaZiAnalyzer
    
    # 创建分析器
    analyzer = ShiZhuBaZiAnalyzer(
        year=1984, month=2, day=15, hour=10, minute=0, gender='男'
    )
    
    # 获取分析结果
    result = analyzer.get_analysis_result()
    
    print(f"\n事主信息：")
    print(f"  出生时间：{result['基本信息']['出生时间']}")
    print(f"  性别：{result['基本信息']['性别']}")
    
    print(f"\n日主分析：")
    print(f"  日主：{result['日主信息']['日主']}")
    print(f"  日支：{result['日主信息']['日支']}")
    
    print(f"\n旺衰分析：")
    print(f"  分数：{result['旺衰分析']['旺衰分数']}分")
    print(f"  等级：{result['旺衰分析']['旺衰等级']}")
    print(f"  说明：{result['旺衰分析']['分析']}")
    
    print(f"\n喜用神：")
    print(f"  喜神：{'、'.join(result['喜用神']['喜神'])}")
    print(f"  用神：{'、'.join(result['喜用神']['用神'])}")
    print(f"  忌神：{'、'.join(result['喜用神']['忌神'])}")


# ============================================================================
# 示例5：日课匹配评分（核心功能）
# ============================================================================

def example_rike_matching():
    """日课匹配评分示例"""
    print("\n" + "=" * 80)
    print("示例5：日课匹配评分")
    print("=" * 80)
    
    from modules.事主八字分析 import ShiZhuBaZiAnalyzer
    
    # 创建事主分析器
    analyzer = ShiZhuBaZiAnalyzer(
        year=1984, month=2, day=15, hour=10, minute=0, gender='男'
    )
    
    # 测试多个日课
    test_rikes = [
        {
            'name': '吉日1',
            'year_gan': '甲', 'year_zhi': '辰',
            'month_gan': '丙', 'month_zhi': '寅',
            'day_gan': '戊', 'day_zhi': '辰',
            'hour_gan': '丙', 'hour_zhi': '午'
        },
        {
            'name': '吉日2',
            'year_gan': '甲', 'year_zhi': '辰',
            'month_gan': '己', 'month_zhi': '巳',
            'day_gan': '丁', 'day_zhi': '卯',
            'hour_gan': '丙', 'hour_zhi': '午'
        },
        {
            'name': '凶日',
            'year_gan': '甲', 'year_zhi': '辰',
            'month_gan': '壬', 'month_zhi': '申',
            'day_gan': '壬', 'day_zhi': '申',
            'hour_gan': '庚', 'hour_zhi': '子'
        }
    ]
    
    print(f"\n事主用神：{'、'.join(analyzer.yongshen)}")
    print(f"事主喜神：{'、'.join(analyzer.xishen)}")
    print(f"事主忌神：{'、'.join(analyzer.jishen)}")
    
    print(f"\n日课匹配结果：")
    for rike in test_rikes:
        match_result = analyzer.calculate_rike_match_score(rike)
        print(f"\n  {rike['name']}:")
        print(f"    分数：{match_result['score']}分")
        print(f"    等级：{match_result['level']}")
        print(f"    总结：{match_result['summary']}")


# ============================================================================
# 示例6：多个事主综合评分
# ============================================================================

def example_multi_shizhu():
    """多个事主综合评分示例"""
    print("\n" + "=" * 80)
    print("示例6：多个事主综合评分")
    print("=" * 80)
    
    from modules.事主日课匹配评分 import calculate_multi_match
    
    # 多个事主信息
    shizhu_list = [
        {
            'name': '新郎',
            'year': 1984, 'month': 2, 'day': 15, 'hour': 10,
            'minute': 0, 'gender': '男'
        },
        {
            'name': '新娘',
            'year': 1986, 'month': 5, 'day': 20, 'hour': 14,
            'minute': 30, 'gender': '女'
        }
    ]
    
    # 测试日课
    rike_sizhu = {
        'year_gan': '甲', 'year_zhi': '辰',
        'month_gan': '丙', 'month_zhi': '寅',
        'day_gan': '戊', 'day_zhi': '辰',
        'hour_gan': '丙', 'hour_zhi': '午'
    }
    
    # 计算综合匹配度
    result = calculate_multi_match(shizhu_list, rike_sizhu)
    
    print(f"\n综合评分：{result['score']}分")
    print(f"综合等级：{result['level']}")
    print(f"总结：{result['summary']}")
    
    print(f"\n各事主详情：")
    for detail in result['details']:
        print(f"  {detail['name']}：{detail['score']}分（{detail['level']}）")
        print(f"    用神：{'、'.join(detail['yongshen'])}")


# ============================================================================
# 主函数
# ============================================================================

if __name__ == '__main__':
    print("\n")
    print("█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "八字工具模块使用示例".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    # 运行所有示例
    example_basic_tools()
    example_zhi_relations()
    example_zhangsheng()
    example_shizhu_analysis()
    example_rike_matching()
    example_multi_shizhu()
    
    print("\n" + "=" * 80)
    print("所有示例运行完成！")
    print("=" * 80)
    print("\n使用建议：")
    print("1. 新开发优先使用 modules.八字工具整合")
    print("2. 择日功能使用 modules.事主八字分析")
    print("3. 多事主匹配使用 modules.事主日课匹配评分")
    print("=" * 80)
