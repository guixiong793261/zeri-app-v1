# -*- coding: utf-8 -*-
"""001 §275 作灶通道四项修复验证：
1. 红嘴朱雀/伐日 → 作灶高分不可豁免（决策分析黄牌）
2. 伐日 → 作灶一票否决（评分器 zao_fari_veto）
3. 作灶吉神正向加分封顶 +40
4. E008 地火日/灶君忌日不再误报（忌事明细已纳入出处）
"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.评分器 import Scorer as ScoreCalculator
from modules.决策分析 import build_decision_report as analyze
from modules.日课校验器 import lint_lesson
from modules.四柱计算器 import calculate_sizhu

OWNERS = [
    {'name': '宅主', 'year_ganzhi': '辛亥', 'role': '主',
     'day_zhi': '戌', 'is_xianming': False},
    {'name': '女主人', 'year_ganzhi': '辛亥', 'role': '辅',
     'day_zhi': '戌', 'is_xianming': False, 'weight': 0.5},
]

# 甲午年丁丑月，6 份报告对应公历日期与时辰
CASES = {
    '作灶1': {'date': date(2015, 1, 9), 'hour': 16, '原分': 244,
              '期望': '吉课仍可用但分数大降（吉神封顶）'},
    '作灶2': {'date': date(2015, 2, 2), 'hour': 16, '原分': 232,
              '期望': '黄牌（红嘴朱雀临震宫）'},
    '作灶3': {'date': date(2015, 1, 21), 'hour': 18, '原分': 220,
              '期望': '分数大降（双酉自刑+吉神封顶）'},
    '作灶4': {'date': date(2015, 1, 1), 'hour': 18, '原分': 196,
              '期望': '地火日E008清零，分数降'},
    '作灶5': {'date': date(2015, 1, 8), 'hour': 18, '原分': 183,
              '期望': '一票否决（伐日）'},
    '作灶6': {'date': date(2015, 1, 20), 'hour': 18, '原分': 146,
              '期望': '一票否决（伐日+过燥）'},
}


def run_one(name, info):
    sz = calculate_sizhu(info['date'], hour=info['hour'])
    sc = ScoreCalculator()
    # 用辰山（巽宫，不犯甲午年三煞亥子丑、不犯年家二黑震宫、不被日破），
    # 避免山向类否决掩盖作灶重煞/吉神封顶/E008 修复的验证。
    result = sc.score(
        sz, '作灶', OWNERS, '阳宅', shan_xiang='辰', zeli_mode='pure')
    score = result.get('score', 0)
    veto = result.get('veto_reasons') or []
    level = result.get('level', '')
    decision = analyze(result, '作灶')
    vk = decision.get('verdict_key', '')
    vlabel = decision.get('verdict_label', '')
    advice = decision.get('advice', '')
    lr = lint_lesson(result)
    issues = lr.issues if hasattr(lr, 'issues') else list(lr or [])
    e008 = [i for i in issues if getattr(i, 'rule_id', None) == 'E008']
    print(f"\n=== {name}  原分={info['原分']}  期望：{info['期望']} ===")
    print(f"  四柱: {sz.get('year_gan')}{sz.get('year_zhi')} "
          f"{sz.get('month_gan')}{sz.get('month_zhi')} "
          f"{sz.get('day_gan')}{sz.get('day_zhi')} "
          f"{sz.get('hour_gan')}{sz.get('hour_zhi')}")
    print(f"  现分={score}  等级={level}  veto={bool(veto)}  "
          f"verdict_key={vk}  label={vlabel}")
    if veto:
        print(f"  veto_reasons: {veto}")
    print(f"  advice: {advice}")
    print(f"  E008 条数: {len(e008)}")
    for i in e008[:3]:
        print(f"    E008: {getattr(i, 'detail', '')}")
    return {
        'name': name, 'score': score, 'veto': bool(veto),
        'vk': vk, 'label': vlabel, 'e008': len(e008),
    }


def mock_decision_check():
    """直接验证决策分析的红嘴朱雀黄牌逻辑（绕开山向类 veto 干扰）。"""
    mock_result = {
        'score': 250, 'level': '★★★★★ 上吉', 'veto_reasons': [],
        'shensha_list': [
            {'name': '红嘴朱雀', 'score': -30,
             'description': '红嘴朱雀临震宮，忌修厨（作灶）'},
            {'name': '天乙贵人', 'score': 20},
        ],
        'score_details': {'三煞扣分明细': [], '相主详情': []},
        'sansha_info': {'sansha_penalty': 0, 'sansha_penalty_detail': [],
                        'heavy_sha_names': []},
    }
    d = analyze(mock_result, '作灶')
    print("\n=== Mock：作灶+红嘴朱雀+高分250（无veto） ===")
    print(f"  verdict_key={d.get('verdict_key')}  label={d.get('verdict_label')}")
    print(f"  advice={d.get('advice')}")
    cond = d.get('verdict_key') == 'warn' and '作灶重煞' in d.get('verdict_label', '')
    print(f"[{'OK' if cond else 'FAIL'}] 红嘴朱雀强制黄牌 "
          f"(vk={d.get('verdict_key')}, label={d.get('verdict_label')})")
    return cond


def main():
    results = [run_one(n, i) for n, i in CASES.items()]
    print("\n========== 断言 ==========")
    ok = True
    # Mock 验证红嘴朱雀黄牌
    ok = mock_decision_check() and ok
    for r in results:
        n = r['name']
        if n in ('作灶5', '作灶6'):
            cond = r['veto'] and r['vk'] == 'veto'
            print(f"[{'OK' if cond else 'FAIL'}] {n}: 伐日一票否决 "
                  f"(veto={r['veto']}, vk={r['vk']})")
            ok = ok and cond
        elif n == '作灶2':
            cond = r['vk'] == 'warn' and '作灶重煞' in r['label']
            print(f"[{'OK' if cond else 'FAIL'}] {n}: 红嘴朱雀黄牌 "
                  f"(vk={r['vk']}, label={r['label']})")
            ok = ok and cond
        elif n == '作灶1':
            cond = r['score'] < 200
            print(f"[{'OK' if cond else 'FAIL'}] {n}: 吉神封顶后分数<200 "
                  f"(score={r['score']})")
            ok = ok and cond
        elif n == '作灶4':
            cond = r['e008'] == 0
            print(f"[{'OK' if cond else 'FAIL'}] {n}: 地火日E008清零 "
                  f"(e008={r['e008']})")
            ok = ok and cond
        elif n == '作灶3':
            cond = r['score'] < 200
            print(f"[{'OK' if cond else 'FAIL'}] {n}: 分数<200 "
                  f"(score={r['score']})")
            ok = ok and cond
    print(f"\n{'全部通过' if ok else '存在失败'}")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
