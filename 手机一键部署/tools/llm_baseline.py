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

    # 重选最佳时柱 + 注入（与主程序完整流程同口径）
    try:
        import tkinter as tk
        root = tk.Tk(); root.withdraw()
        import 主程序 as appmod
        app = appmod.ZeriApp(root)
        sz, result = app._rescan_best_hour(d, event, owners, None, None, None, None, None, None, sz, result)
        _wrapper = {
            'date': date_str,
            'sizhu': ' '.join([sz['年柱'], sz['月柱'], sz['日柱'], sz['时柱']]),
            'score': result.get('score'), 'level': result.get('level'),
            'detail': result,
        }
        app._inject_best_hour_to_result(_wrapper, result, event, owners, d, sz)
        root.destroy()
    except Exception as e:
        # 不静默吞错：注入失败须可见，避免基线口径悄悄退回注入前
        print(f'⚠ 重选/注入失败，使用午时初值: {e}')

    ck, _ = build_checker(event, None, '')
    lucky = ck.get_lucky_hours(_norm_sizhu_for_lucky(result.get('sizhu'))
                               or _norm_sizhu_for_lucky(sz))
    return result, lucky


def _norm_sizhu_for_lucky(s):
    """归一化 sizhu 供 get_lucky_hours 使用（与主程序 norm_sizhu 口径一致）。

    calculate_score 的 result['sizhu'] 在部分日期缺失（如 2026-01-04，
    评分器某返回分支未带该键），回退对象的键集也不稳定；而
    get_lucky_hours 直接下标访问 day_gan/day_zhi，缺键即 KeyError。
    此处统一从中文键（年柱/月柱/日柱/时柱，必定存在）重建小写键；
    已有完整小写键则原样返回。
    """
    if not isinstance(s, dict):
        return None
    _need = ('year_gan', 'year_zhi', 'month_gan', 'month_zhi',
             'day_gan', 'day_zhi', 'hour_gan', 'hour_zhi')
    if all(k in s for k in _need):
        return s

    def _g2(v):
        v = str(v or '')
        return (v[:1], v[1:2]) if len(v) >= 2 else ('', '')

    yg, yz = _g2(s.get('年柱'))
    mg, mz = _g2(s.get('月柱'))
    dg, dz = _g2(s.get('日柱'))
    hg, hz = _g2(s.get('时柱'))
    n = dict(s)
    n.update({'year_gan': yg, 'year_zhi': yz, 'month_gan': mg, 'month_zhi': mz,
              'day_gan': dg, 'day_zhi': dz, 'hour_gan': hg, 'hour_zhi': hz})
    return n


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
