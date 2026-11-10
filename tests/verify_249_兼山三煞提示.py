# -*- coding: utf-8 -*-
"""§249（2026-11-10 拍板）：兼山不减免三煞——UI 提示与活管线口径锚点。

背景：修造·乾山巽向兼亥·亥月课，月令表出「犯兼山山家三煞」忌项但判可用，
暴露判据分叉。三库全卷扫描（见 docs/三煞兼山检索报告.md）确认：兼山/兼向
避三煞无独立明文，三煞按年支三合绝位推算、以主山主向为准。

冻结口径：
1. 评分器维持主山/主向硬门槛，兼向不构成豁免或加重（零代码改动）。
2. 主程序修造、安葬两处山向输入行下加小字提示（纯展示层）。

本脚本断言：
A. 展示层——提示文案在主程序源码中恰好 2 处（修造+安葬），评分器不含该文案；
B. 活管线阴性锚点——兼山月令表口径不影响 check_sansha 主山判定；
C. 活管线阳性锚点——主山犯三煞正常触发（防口径被弱化为恒不触发）；
D. 检索报告文件存在且含结论句。

退出码：全过 0，任一失败 1。
"""
import io
import os
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

NOTE = '注：三煞以主山主向为准，兼山不减免三煞凶性。'
_fail = []


def check(name, cond, detail=''):
    print('%s %s %s' % ('PASS' if cond else 'FAIL', name, detail))
    if not cond:
        _fail.append(name)


def main():
    # A1 提示文案在主程序恰好 2 处（修造 + 安葬）
    src = open(os.path.join(ROOT, '主程序.py'), encoding='utf-8').read()
    n = src.count(NOTE)
    check('A1 提示文案恰2处', n == 2, '实际=%d' % n)

    # A2 评分器不含该文案（防展示层文案误入评分逻辑）
    src2 = open(os.path.join(ROOT, 'modules', '评分器.py'), encoding='utf-8').read()
    check('A2 评分器不含提示文案', '兼山不减免' not in src2)

    # B1 阴性锚点：乾山巽向兼亥·亥月·丑年——月令表称「犯兼山山家三煞」，
    #    但活管线按主山主向口径不触发
    from modules.二十四山择吉天机 import check_sansha
    r1 = check_sansha('乾山巽向兼亥', '亥', '丑')
    check('B1 兼山不加重（乾兼亥不触发）', r1.get('犯煞') is False, str(r1))

    # C1 阳性锚点：艮山坤向·寅日·丑年（丑年煞在寅卯辰，艮兼寅位犯灾煞）——
    #    主山硬门槛正常触发，防口径被弱化为恒不触发
    r2 = check_sansha('艮山坤向', '寅', '丑')
    check('C1 主山犯煞正常触发', r2.get('犯煞') is True, str(r2))

    # D1 检索报告存在且含用户拍板的结论句
    rp = os.path.join(ROOT, 'docs', '三煞兼山检索报告.md')
    ok = os.path.isfile(rp)
    if ok:
        doc = open(rp, encoding='utf-8').read()
        ok = ('均无针对' in doc and '兼山/兼向避三煞' in doc
              and '三煞按年支三合绝位推算' in doc)
    check('D1 检索报告含结论句', ok, rp)

    print()
    if _fail:
        print('FAIL %d 项：%s' % (len(_fail), _fail))
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
