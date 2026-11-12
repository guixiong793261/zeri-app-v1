# -*- coding: utf-8 -*-
"""001 §275 作灶极品/上品全量扫描：确认高分假绿灯是否掉出。
扫 2025 全年（甲午年）作灶×辰山，检查：
1. 伐日作灶必须 veto（不得出现在绿灯）
2. 红嘴朱雀作灶必须 warn（不得出现在绿灯）
3. 统计极品/上品（score>=200 且 ok）清单
"""
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.评分器 import Scorer
from modules.决策分析 import build_decision_report
from modules.四柱计算器 import calculate_sizhu

OWNERS = [{'name': '宅主', 'year_ganzhi': '辛亥', 'role': '主',
           'day_zhi': '戌', 'is_xianming': False}]


def main():
    sc = Scorer()
    start = date(2014, 2, 4)  # 甲午年立春
    total_days = 365
    high_green = []       # score>=200 且 ok
    fari_green = []       # 伐日却绿灯（应为 veto）
    hongsha_green = []    # 红嘴朱雀却绿灯（应为 warn）
    top_list = []         # 极品/上品（score>=200 ok）
    warn_count = 0
    veto_count = 0
    fari_total = 0
    hongsha_total = 0

    for i in range(total_days):
        d = start + timedelta(days=i)
        sz = calculate_sizhu(d, hour=12)
        r = sc.score(sz, '作灶', OWNERS, '阳宅', shan_xiang='辰', zeli_mode='pure')
        score = r.get('score', 0)
        veto = bool(r.get('veto_reasons'))
        shensha = r.get('shensha_list') or []
        ji = r.get('ji_list') or []
        sd = (r.get('sansha_info') or {}).get('sansha_penalty_detail') or []
        veto_text = ' '.join(r.get('veto_reasons') or [])
        has_fari = (any('伐日' in str(s.get('name', ''))
                        for s in shensha if isinstance(s, dict))
                    or any('伐日' in str(x) for x in ji)
                    or any('伐日' in str(x) for x in sd)
                    or '伐日' in veto_text)
        has_hongsha = any('红嘴朱雀' in str(s.get('name', ''))
                          for s in shensha if isinstance(s, dict))
        if has_fari:
            fari_total += 1
        if has_hongsha:
            hongsha_total += 1
        if veto:
            veto_count += 1
            continue
        dec = build_decision_report(r, '作灶')
        vk = dec.get('verdict_key', '')
        if vk == 'warn':
            warn_count += 1
        # 假绿灯：非 veto 且非 warn（即 ok），却命中伐日/红嘴朱雀
        if vk == 'ok':
            if has_fari:
                fari_green.append((d, score, '伐日绿灯'))
            if has_hongsha:
                hongsha_green.append((d, score, '红嘴朱雀绿灯'))
        if vk == 'ok' and score >= 200:
            high_green.append((d, score))
            top_list.append((d, score))

    print(f"扫描 2025 全年作灶×辰山 共 {total_days} 日")
    print(f"  veto 日: {veto_count}")
    print(f"  warn 日: {warn_count}")
    print(f"  伐日总数: {fari_total}")
    print(f"  红嘴朱雀总数: {hongsha_total}")
    print(f"  高分绿灯(score>=200 ok): {len(high_green)}")
    print(f"  伐日却绿灯(应为veto): {len(fari_green)}")
    for x in fari_green[:5]:
        print(f"    {x}")
    print(f"  红嘴朱雀却绿灯(应为warn): {len(hongsha_green)}")
    for x in hongsha_green[:5]:
        print(f"    {x}")
    print(f"\n极品/上品 Top10（score>=200）:")
    for d, s in sorted(top_list, key=lambda x: -x[1])[:10]:
        print(f"  {d}  score={s}")

    ok = len(fari_green) == 0 and len(hongsha_green) == 0
    print(f"\n结论: {'假绿灯全部掉出 ✓' if ok else '仍有假绿灯 ✗'}")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
