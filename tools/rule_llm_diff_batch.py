# -*- coding: utf-8 -*-
"""
过去 N 天的硬规则 vs LLM 对比，输出汇总表。
用法: python tools/rule_llm_diff_batch.py [days_back] [--mock]
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, timedelta
from tools.rule_llm_diff import build_report
from modules.日课校验器 import lint_lesson, llm_review


def _mock_api(prompt):
    return json.dumps([
        {'rule_id': 'L001', 'level': 'WARN', 'message': '等级慎用但结论写可用',
         'field': '综合判断', 'suggestion': '改为须慎用'},
    ], ensure_ascii=False)


def batch_diff(days_back=7, event='嫁娶', use_mock=False):
    summary = {'total': 0, 'missed': [], 'agree': []}
    for i in range(days_back):
        d = (date.today() - timedelta(days=i)).isoformat()
        try:
            detail, lucky = build_report(d, event)
            lint = lint_lesson(detail, lucky_hours=lucky, bride_year_zhi='卯')
            hard = {x.rule_id for x in lint.issues}
            if use_mock:
                llm_issues = llm_review(detail, detail.get('reason', ''), api_func=_mock_api, cache={})
            else:
                llm_issues = llm_review(detail, detail.get('reason', ''), cache={})
            llm = {x.rule_id for x in llm_issues}
            missed = llm - hard
            summary['total'] += 1
            if missed:
                summary['missed'].append({'date': d, 'missed': sorted(missed)})
            else:
                summary['agree'].append(d)
        except Exception as e:
            print(f'[SKIP] {d}: {e}')
    print(f"\n总天数: {summary['total']}")
    print(f"无漏报: {len(summary['agree'])}")
    print(f"有漏报: {len(summary['missed'])}")
    for m in summary['missed']:
        print(f"  {m['date']}: {m['missed']}")
    return summary


if __name__ == '__main__':
    days = 7
    mock = '--mock' in sys.argv
    for a in sys.argv[1:]:
        if a.isdigit():
            days = int(a)
    batch_diff(days, use_mock=mock)
