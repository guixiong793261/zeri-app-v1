# -*- coding: utf-8 -*-
"""
对比 E 规则与 LLM 在同一日期上的命中情况，检测漏报/误报。
用法: python tools/rule_llm_diff.py 2026-09-25 嫁娶
输出: hard_hits / llm_hits / missed (LLM 命中但 E 规则未命中)
"""
import json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.日课校验器 import lint_lesson, llm_review
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
from modules.推荐时柱 import build_checker


def build_report(date_str, event):
    d = dt.datetime.strptime(date_str, '%Y-%m-%d').date()
    sz = calculate_sizhu(d, 12, 0)
    sz.update({'year': d.year, 'month': d.month, 'day': d.day, 'date': d})
    owners = [
        {'name': '欢', 'role': '新娘', '性别': '女', 'birth_date': '1999-04-05'},
        {'name': '文旺', 'role': '新郎', '性别': '男', 'birth_date': '1998-10-13'},
    ]
    result = calculate_score(sz, event, owners, None, None, None, None, None)
    ck, _ = build_checker(event, None, '')
    lucky = ck.get_lucky_hours(result.get('sizhu') or sz)
    return result, lucky


def diff_report(date_str, event, use_mock=False):
    detail, lucky = build_report(date_str, event)

    # 硬规则
    lint = lint_lesson(detail, lucky_hours=lucky, bride_year_zhi='卯')
    hard_hits = {i.rule_id for i in lint.issues}

    # LLM
    if use_mock:
        def mock_api(prompt):
            import json as _json
            return _json.dumps([
                {'rule_id': 'L001', 'level': 'WARN', 'message': '等级慎用但结论写可用',
                 'field': '综合判断', 'suggestion': '改为须慎用'},
            ], ensure_ascii=False)
        llm_issues = llm_review(detail, detail.get('reason', ''), api_func=mock_api, cache={})
    else:
        llm_issues = llm_review(detail, detail.get('reason', ''), cache={})
    llm_hits = {i.rule_id for i in llm_issues}

    # 关注：LLM 命中但 E 规则未命中 → E 规则漏报
    missed = llm_hits - hard_hits
    # E 规则命中但 LLM 没命中 → 正常（硬规则更强）

    print(f"\n=== {date_str} {event} ===")
    print(f"  硬规则命中: {sorted(hard_hits)}")
    print(f"  LLM 命中  : {sorted(llm_hits)}")
    print(f"  ⚠ 漏报(E规则未覆盖LLM命中): {sorted(missed) if missed else '无'}")

    return {
        'date': date_str, 'event': event,
        'hard': sorted(hard_hits),
        'llm': sorted(llm_hits),
        'missed': sorted(missed),
    }


if __name__ == '__main__':
    mock = '--mock' in sys.argv
    if len(sys.argv) >= 3 and not sys.argv[1].startswith('-'):
        date_str, event = sys.argv[1], sys.argv[2]
    else:
        date_str, event = '2026-09-25', '嫁娶'
    diff_report(date_str, event, use_mock=mock)
