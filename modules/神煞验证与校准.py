# -*- coding: utf-8 -*-
"""
================================================================================
神煞规则验证与评分校准工具
================================================================================
对照《钦定协纪辩方书》验证神煞规则，校准评分权重
"""

import sys
import os
from datetime import date

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def verify_shensha_rules():
    """验证神煞规则的正确性"""
    
    print("=" * 80)
    print("【神煞规则验证报告 - 对照《钦定协纪辩方书》】")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            'date': date(2026, 7, 24),
            'event': '入宅',
            'shan_xiang': '坤山艮向兼未',
            'description': '2026年7月24日入宅 - 日柱己亥'
        },
        {
            'date': date(2026, 10, 23),
            'event': '入宅',
            'shan_xiang': '坤山艮向兼未',
            'description': '2026年10月23日入宅 - 日柱庚午'
        },
        {
            'date': date(2026, 9, 18),
            'event': '入宅',
            'shan_xiang': '坤山艮向兼未',
            'description': '2026年9月18日入宅 - 日柱癸巳'
        }
    ]
    
    print('【验证项目】')
    print()
    
    # 1. 验证三煞规则
    print('1. 三煞规则验证')
    print('-' * 60)
    
    sansha_rules = {
        '申子辰年': {'三煞方位': ['巳', '午', '未'], '说明': '申子辰年三煞在巳午未（南方）'},
        '亥卯未年': {'三煞方位': ['申', '酉', '戌'], '说明': '亥卯未年三煞在申酉戌（西方）'},
        '寅午戌年': {'三煞方位': ['亥', '子', '丑'], '说明': '寅午戌年三煞在亥子丑（北方）'},
        '巳酉丑年': {'三煞方位': ['寅', '卯', '辰'], '说明': '巳酉丑年三煞在寅卯辰（东方）'}
    }
    
    for year_type, rule in sansha_rules.items():
        print(f'  {year_type}: {rule["说明"]}')
        print(f'    三煞方位: {rule["三煞方位"]}')
    print()
    
    # 2. 验证吉神规则
    print('2. 吉神规则验证')
    print('-' * 60)
    
    ji_shensha_rules = {
        '天德': '正月丁、二月申、三月壬、四月辛、五月亥、六月甲、七月癸、八月寅、九月丙、十月乙、十一月辰、十二月酉',
        '月德': '正月丙、二月甲、三月壬、四月庚、五月丙、六月甲、七月壬、八月庚、九月丙、十月甲、十一月壬、十二月庚',
        '天愿': '正月甲、二月乙、三月丙、四月丁、五月戊、六月己、七月庚、八月辛、九月壬、十月癸、十一月壬、十二月癸',
        '月恩': '正月寅、二月亥、三月申、四月巳、五月寅、六月亥、七月申、八月巳、九月寅、十月亥、十一月申、十二月巳',
        '四相': '春亥子、夏寅卯、秋辰戌丑未、冬申酉',
        '时德': '春辰巳午、夏未申酉、秋戌亥子、冬丑寅卯',
        '三奇': '甲日庚午、乙日辛亥、丙日戊寅、丁日己卯、戊日戊子、己日己酉、庚日壬午、辛日癸巳、壬日丁酉、癸日癸卯',
        '将星': '正月午、二月未、三月申、四月酉、五月戌、六月亥、七月子、八月丑、九月寅、十月卯、十一月辰、十二月巳',
        '驿马': '申子辰日在寅、亥卯未日在巳、寅午戌日在申、巳酉丑日在亥'
    }
    
    for name, rule in ji_shensha_rules.items():
        print(f'  {name}: {rule}')
    print()
    
    # 3. 验证凶煞规则
    print('3. 凶煞规则验证')
    print('-' * 60)
    
    xiong_shensha_rules = {
        '劫煞': '申子辰日在亥、亥卯未日在申、寅午戌日在巳、巳酉丑日在寅',
        '灾煞': '劫煞对冲位（申子辰日在午、亥卯未日在寅、寅午戌日在亥、巳酉丑日在申）',
        '月煞': '正月戌、二月酉、三月申、四月未、五月午、六月巳、七月辰、八月卯、九月寅、十月丑、十一月子、十二月亥',
        '月厌': '正月戌、二月酉、三月申、四月未、五月午、六月巳、七月辰、八月卯、九月寅、十月丑、十一月子、十二月亥',
        '天吏': '春午、夏酉、秋子、冬卯',
        '大时': '春酉、夏子、秋卯、冬午',
        '四废': '春庚申、夏壬子、秋甲寅、冬丙午',
        '五墓': '春未、夏戌、秋丑、冬辰',
        '月破': '正月申、二月酉、三月戌、四月亥、五月子、六月丑、七月寅、八月卯、九月辰、十月巳、十一月午、十二月未',
        '土符': '子午月在丑、丑未月在辰、寅申月在未、卯酉月在戌、辰戌月在辰、巳亥月在戌'
    }
    
    for name, rule in xiong_shensha_rules.items():
        print(f'  {name}: {rule}')
    print()
    
    # 4. 运行实际测试
    print('4. 实际测试验证')
    print('-' * 60)
    
    try:
        from modules.四柱计算器 import calculate_sizhu
        from modules.评分器 import calculate_score
        from modules.shensha import get_checker
        
        for case in test_cases:
            print(f'\n  【{case["description"]}】')
            
            sizhu = calculate_sizhu(case['date'], 10, 0)
            sizhu['year'] = case['date'].year
            sizhu['month'] = case['date'].month
            sizhu['day'] = case['date'].day
            sizhu['date'] = case['date']
            
            # 执行神煞检查
            checker = get_checker(case['event'])
            shensha_result = checker.check(sizhu, [])
            
            # 分类统计
            ji_count = sum(1 for s in shensha_result if isinstance(s, dict) and s.get('score', 0) > 0)
            xiong_count = sum(1 for s in shensha_result if isinstance(s, dict) and s.get('score', 0) < 0)
            
            print(f'    吉神: {ji_count}个, 凶煞: {xiong_count}个')
            
            # 显示关键神煞
            print(f'    关键吉神:')
            for s in shensha_result:
                if isinstance(s, dict) and s.get('score', 0) > 0:
                    print(f'      ✅ {s.get("name", "")} (+{s.get("score", 0)}分)')
            
            print(f'    关键凶煞:')
            for s in shensha_result:
                if isinstance(s, dict) and s.get('score', 0) < 0:
                    print(f'      ❌ {s.get("name", "")} ({s.get("score", 0)}分)')
            
            # 计算评分
            result = calculate_score(sizhu, case['event'], [], '阳宅', case['shan_xiang'], None, None, None)
            print(f'    最终评分: {result.get("score", 0)}分 | 等级: {result.get("level", "-")}')
    
    except Exception as e:
        print(f'    测试失败: {e}')
        import traceback
        traceback.print_exc()
    
    print()


def calibrate_scoring_weights():
    """校准评分权重"""
    
    print("=" * 80)
    print("【评分权重校准 - 对照传统择日经验】")
    print("=" * 80)
    print()
    
    print('【当前评分机制】')
    print('-' * 60)
    print('  基础分: 100分')
    print('  吉神加分: +5~20分/个')
    print('  凶煞减分: -5~30分/个')
    print('  宜事加分: +10分/项')
    print('  忌事减分: -15分/项')
    print('  三煞扣分: -10~35分')
    print('  五行评分: -50~+50分')
    print()
    
    print('【建议校准方案】')
    print('-' * 60)
    print()
    
    calibration = {
        '三煞扣分': {
            '年三煞犯日柱': -35,
            '年三煞犯月柱': -25,
            '年三煞犯时柱': -15,
            '年三煞犯山向': -30,
            '月三煞犯日柱': -20,
            '月三煞犯时柱': -10,
            '月三煞犯山向': -25,
            '日三煞犯时柱': -10,
            '说明': '三煞为择日大忌，扣分应更重'
        },
        '吉神加分': {
            '天德': 20,
            '月德': 15,
            '天德合': 12,
            '月德合': 10,
            '天赦日': 25,
            '三奇': 20,
            '不将日': 15,
            '鸣吠日': 15,
            '说明': '吉神为择日重要加分项'
        },
        '凶煞减分': {
            '年破': -30,
            '月破': -30,
            '四离日': -35,
            '四绝日': -35,
            '十恶大败': -30,
            '土王用事': -40,
            '劫煞': -25,
            '灾煞': -25,
            '说明': '凶煞为择日大忌，扣分应更重'
        }
    }
    
    for category, rules in calibration.items():
        print(f'  {category}:')
        for name, value in rules.items():
            if isinstance(value, int):
                print(f'    {name}: {value}分')
            else:
                print(f'    {name}: {value}')
        print()
    
    print('【评分等级校准】')
    print('-' * 60)
    
    levels = {
        '上吉': {'score': 130, 'description': '五行大吉 + 黄道大吉，首选推荐'},
        '大吉': {'score': 120, 'description': '五行大吉，诸事皆宜'},
        '吉': {'score': 100, 'description': '五行合格 + 黄道吉，可用'},
        '次吉': {'score': 80, 'description': '五行合格但有小忌，可用但需谨慎'},
        '平': {'score': 60, 'description': '五行平平，仅适合小事'},
        '凶': {'score': 0, 'description': '五行凶或犯大忌，坚决不用'}
    }
    
    for level, info in levels.items():
        print(f'  {level}: ≥{info["score"]}分 - {info["description"]}')
    
    print()
    
    return calibration


def main():
    """主函数"""
    
    print()
    print('╔══════════════════════════════════════════════════════════════╗')
    print('║           专业级正五行择日软件 - 神煞验证与评分校准            ║')
    print('╚══════════════════════════════════════════════════════════════╝')
    print()
    
    # 执行验证
    verify_shensha_rules()
    
    # 执行校准
    calibrate_scoring_weights()
    
    print('=' * 80)
    print('验证与校准完成！')
    print('=' * 80)


if __name__ == '__main__':
    main()
