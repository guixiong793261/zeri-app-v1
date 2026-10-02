# -*- coding: utf-8 -*-
"""
LLM 语义审查基线测试
用法: python tools/llm_baseline.py [--mock]
输出: data/llm_baseline_YYYYMMDD.json
"""
import json, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.日课校验器 import lint_lesson, llm_review

CASES = [
    ("2026-01-05", "嫁娶"),
    ("2026-02-05", "嫁娶"),
    ("2026-09-25", "嫁娶"),
    ("2026-10-19", "嫁娶"),
]


def build_report(date_str, event):
    """生成结构化数据 + 渲染文本（复用真实流程）。"""
    import datetime as dt
    from modules.四柱计算器 import calculate_sizhu
    from modules.评分器 import calculate_score
    from modules.推荐时柱 import build_checker

    d = dt.datetime.strptime(date_str, '%Y-%m-%d').date()
    sz = calculate_sizhu(d, 12, 0)
    sz.update({'year': d.year, 'month': d.month, 'day': d.day, 'date': d})
    owners = [
        {'name': '欢', 'role': '新娘', '性别': '女', 'birth_date': '1999-04-05'},
        {'name': '文旺', 'role': '新郎', '性别': '男', 'birth_date': '1998-10-13'},
    ]
    result = calculate_score(sz, event, owners, None, None, None, None, None)

    # 重选最佳时柱（与主程序同口径）
    try:
        import tkinter as tk
        root = tk.Tk(); root.withdraw()
        import 主程序 as appmod
        app = appmod.ZeriApp(root)
        sz, result = app._rescan_best_hour(d, event, owners, None, None, None, None, None, None, sz, result)
        root.destroy()
    except Exception:
        pass

    ck, _ = build_checker(event, None, '')
    lucky = ck.get_lucky_hours(result.get('sizhu') or sz)
    return result, lucky


def mock_llm_api(prompt):
    """模拟 LLM 返回（无 API Key 时用）。"""
    import json as _json
    return _json.dumps([
        {'rule_id': 'L001', 'level': 'WARN', 'message': '等级慎用但结论写可用', 'field': '综合判断', 'suggestion': '改为须慎用'},
        {'rule_id': 'L004', 'level': 'WARN', 'message': '综合判断句缺明确结论', 'field': '综合判断', 'suggestion': '补充可用/慎用/不可用'},
    ], ensure_ascii=False)


def run_baseline(use_mock=False):
    has_key = bool(os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY"))
    if not has_key and not use_mock:
        print("⚠ 未配置 API Key，使用 --mock 模拟模式")
        use_mock = True

    results = []
    for date, event in CASES:
        print(f"\n=== {date} {event} ===")
        detail, lucky = build_report(date, event)

        # 硬规则
        lint = lint_lesson(detail, lucky_hours=lucky, bride_year_zhi='卯')

        # LLM 语义审查
        if use_mock:
            llm_issues = llm_review(detail, detail.get('reason', ''), api_func=mock_llm_api, cache={})
        else:
            llm_issues = llm_review(detail, detail.get('reason', ''), cache={})

        rec = {
            'date': date,
            'event': event,
            'score': detail.get('score'),
            'level': detail.get('level'),
            'hard_error_count': lint.error_count,
            'hard_warn_count': lint.warn_count,
            'hard_issues': [
                {'rule_id': i.rule_id, 'severity': i.severity, 'message': i.message}
                for i in lint.issues
            ],
            'llm_count': len(llm_issues),
            'llm_issues': [
                {'rule_id': i.rule_id, 'severity': i.severity, 'message': i.message}
                for i in llm_issues
            ],
        }
        results.append(rec)

        print(f"  硬规则: ERROR={lint.error_count} WARN={lint.warn_count}")
        print(f"  LLM   : {len(llm_issues)} 条")
        for i in llm_issues:
            print(f"    [{i.rule_id}] {i.message[:60]}")

    import datetime as _dt
    out_path = f"data/llm_baseline_{_dt.datetime.now():%Y%m%d}.json"
    os.makedirs("data", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 基线已保存: {out_path}")
    return results


if __name__ == "__main__":
    mock = '--mock' in sys.argv
    run_baseline(use_mock=mock)
