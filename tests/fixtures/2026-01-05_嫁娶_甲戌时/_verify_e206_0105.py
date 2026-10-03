# -*- coding: utf-8 -*-
"""E206 边界案例存档：2026-01-05 嫁娶（新娘1999-04-05 / 新郎1998-10-13，年支卯）

复核目的（用户指定观察点）：
1. 忌项清单里是否有 >=10 扣分的实质凶煞（月破/红纱一类）——决定 E206 命中是否正确
2. 综合判断行（及全文）是否含化解类吉神说明（合住/制伏/化解/有制等）
3. 结论：真阳性 -> E206 检出率比预期更广；仅轻度忌项 -> 需调阈值/白名单

用法: python _verify_e206_0105.py
输出: 同目录 detail_0105_e206_boundary.txt（完整报告+lint+忌项扣分分析）
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)

from tools.llm_baseline import build_report
from modules.日课校验器 import lint_lesson

RESOLVED_KW = ['合住', '合去', '制伏', '制住', '克制', '制化', '化解', '合化', '有制', '得制']


def main():
    detail, lucky = build_report('2026-01-05', '嫁娶')
    lint = lint_lesson(detail, lucky_hours=lucky, bride_year_zhi='卯')
    reason = detail.get('reason', '')

    zong_lines = [ln.strip() for ln in reason.splitlines() if '综合判断' in ln]
    e206 = [i for i in lint.issues if i.rule_id == 'E206']

    # LLM facts 实际取用的键是 yi_list/ji_list（日课校验器 L1439-1440）
    yi = detail.get('yi_list', detail.get('宜'))
    ji = detail.get('ji_list', detail.get('忌'))
    hit_kw_line = [k for k in RESOLVED_KW if any(k in ln for ln in zong_lines)]
    hit_kw_full = [k for k in RESOLVED_KW if k in reason]

    # 忌项在正文中的扣分行（通常含 -N 分值）
    ji_names = []
    for it in ji:
        if isinstance(it, str):
            ji_names.append(it)
        elif isinstance(it, (list, tuple)) and it:
            ji_names.append(str(it[0]))
        elif isinstance(it, dict):
            ji_names.append(str(it.get('name') or it.get('神煞') or it))
    ji_lines = {}
    for nm in ji_names:
        for ln in reason.splitlines():
            if nm and nm in ln:
                ji_lines[nm] = ln.strip()
                break

    print('=== 分数/等级 ===')
    print(detail.get('score'), detail.get('level'))
    print('=== 硬规则 ===')
    print('ERROR=%d WARN=%d' % (lint.error_count, lint.warn_count))
    for i in lint.issues:
        print('[%s/%s] %s' % (i.rule_id, i.severity, i.message))
    print('=== E206 命中 %d 条 ===' % len(e206))
    for i in e206:
        print('message:', i.message)
        print('suggestion:', getattr(i, 'suggestion', ''))
    print('=== 综合判断行 ===')
    for ln in zong_lines:
        print(ln)
    print('=== 宜 ===')
    print(yi)
    print('=== 忌 ===')
    print(ji)
    print('=== 忌项扣分行 ===')
    for nm, ln in ji_lines.items():
        print('%s -> %s' % (nm, ln))
    print('=== 化解词：综合判断行命中=%s / 全文命中=%s ===' % (hit_kw_line, hit_kw_full))

    # 存档
    out = os.path.join(HERE, 'detail_0105_e206_boundary.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('E206 边界案例：2026-01-05 嫁娶（新娘1999-04-05/新郎1998-10-13，年支卯）\n')
        f.write('分数：%s  等级：%s\n' % (detail.get('score'), detail.get('level')))
        f.write('硬规则：ERROR=%d WARN=%d\n' % (lint.error_count, lint.warn_count))
        for i in lint.issues:
            f.write('  [%s/%s] %s\n' % (i.rule_id, i.severity, i.message))
        f.write('\n=== 综合判断行 ===\n')
        for ln in zong_lines:
            f.write(ln + '\n')
        f.write('\n=== 宜 ===\n%s\n\n=== 忌 ===\n%s\n' % (yi, ji))
        f.write('\n=== 忌项扣分行 ===\n')
        for nm, ln in ji_lines.items():
            f.write('%s -> %s\n' % (nm, ln))
        f.write('\n化解词（综合判断行）：%s\n化解词（全文）：%s\n' % (hit_kw_line, hit_kw_full))
        f.write('\n=== 完整渲染文本 ===\n')
        f.write(reason)
    print('\n✅ 已存档:', out)


if __name__ == '__main__':
    main()
