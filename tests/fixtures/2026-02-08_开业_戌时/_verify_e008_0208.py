# -*- coding: utf-8 -*-
"""E008 非嫁娶误报修复回归锚点：2026-02-08 开业（一票否决日，注入戌时）

修复背景（2026-10-05，用户裁决）：
该日修复前 E008 误报 5 条 WARN：
1. 事项名误报：「开业/开市/纳财」是开业规则 L246-248 append 的黄历忌事项词，
   被当煞名查"评分/神煞段出处"必然无出处
   -> 修法：_is_xiansha_name 反向判定（复用今日黄历.YIJI_60 词集，不硬编码词典）
2. veto 日假阳性：「年三煞(日柱)/月三煞(日柱)」真煞名，但一票否决日报告砍为单行，
   评分明细/神煞段不存在；且单行里本就写了这两个煞名
   -> 修法：veto 日扩渲染全文查出处——只扩范围，不取消检查

断言（退出码 0=通过 / 1=回归失败）：
- E008 命中 = 0
- E004 ERROR = 1（推荐时柱戌时辰评分为负，凶日照常工作）
用法: python _verify_e008_0208.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)

from tools.llm_baseline import build_report
from modules.日课校验器 import lint_lesson


def main():
    detail, lucky = build_report('2026-02-08', '开业')
    lint = lint_lesson(detail, lucky_hours=lucky,
                       rendered_content=detail.get('reason', ''),
                       bride_year_zhi=None)
    e008 = [i for i in lint.issues if i.rule_id == 'E008']
    e004 = [i for i in lint.issues if i.rule_id == 'E004']

    print('分数/等级:', detail.get('score'), detail.get('level'))
    print('ji_list:', detail.get('ji_list'))
    print('E008 命中=%d (期望0)' % len(e008))
    print('E004 ERROR=%d (期望1)' % len(e004))
    for i in lint.issues:
        print('  [%s/%s] %s' % (i.rule_id, i.severity, i.message[:90]))

    ok = (len(e008) == 0 and len(e004) == 1)
    print('结论:', '通过' if ok else '回归失败！')

    out = os.path.join(HERE, 'detail_0208_e008_boundary.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('E008 非嫁娶回归锚点：2026-02-08 开业（一票否决日，注入戌时）\n')
        f.write('分数：%s  等级：%s\n' % (detail.get('score'), detail.get('level')))
        f.write('ji_list：%s\n' % (detail.get('ji_list'),))
        f.write('E008 命中：%d（修复前 5 条误报：开业/开市/纳财 + 年三煞(日柱)/月三煞(日柱)）\n'
                % len(e008))
        for i in lint.issues:
            f.write('  [%s/%s] %s\n' % (i.rule_id, i.severity, i.message))
        f.write('\n=== 渲染文本（一票否决日为单行） ===\n')
        f.write(detail.get('reason', ''))
    print('已存档:', out)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
