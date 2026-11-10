# -*- coding: utf-8 -*-
"""§250（2026-11-10 用户报障）：天乙贵人进入神煞计分与条件择日。

现象：日课【吉神】段显示「天乙贵人: 日干庚见月柱丑」，但【神煞信息】的
【吉神(加分项)】没有该条、也未加分；条件择日勾选「天乙贵人」形同死选项。

根因：天乙贵人只在评分器八字「吉神」展示段写入 details['吉神']，
神煞计分层 _check_day_shensha 从未发射同名条目。

修复：
1. 神煞基类新增 TIANYI_GUIREN_MAP（单一表源）与 _is_tianyi_guiren 谓词；
2. _check_day_shensha 发射「天乙贵人 +15」（四柱任一柱命中即贵，同名去重）；
3. 评分器展示层改为引用同一张表，杜绝双表分叉；
4. 条件择日吉神清单本已含「天乙贵人」，计分发射后即可真正命中。

退出码：全过 0，任一失败 1。
"""
import datetime
import io
import os
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu          # noqa: E402
from modules.评分器 import calculate_score              # noqa: E402
from modules.shensha.神煞基类 import ShenShaChecker     # noqa: E402

_fail = []


def check(name, cond, detail=''):
    print('%s %s %s' % ('PASS' if cond else 'FAIL', name, detail))
    if not cond:
        _fail.append(name)


def _score(d, event='修造'):
    sz = calculate_sizhu((d.year, d.month, d.day), 0, 0, longitude=120)
    sz['year'], sz['month'], sz['day'] = d.year, d.month, d.day
    return sz, calculate_score(sz, event, owners=[], zeli_mode='pure')


def main():
    # A1 谓词：日干庚见月支丑 → 月柱
    _p = ShenShaChecker._is_tianyi_guiren(
        ShenShaChecker.__new__(ShenShaChecker),
        {'day_gan': '庚', 'year_zhi': '子', 'month_zhi': '丑',
         'day_zhi': '申', 'hour_zhi': '子'})
    check('A1 谓词命中月柱', _p == '月柱', str(_p))

    # A2 谓词：日干甲见未（年柱）→ 年柱；四柱皆不中 → None
    _q = ShenShaChecker._is_tianyi_guiren(
        ShenShaChecker.__new__(ShenShaChecker),
        {'day_gan': '甲', 'year_zhi': '未', 'month_zhi': '子',
         'day_zhi': '申', 'hour_zhi': '午'})
    check('A2 谓词命中年柱', _q == '年柱', str(_q))
    _r = ShenShaChecker._is_tianyi_guiren(
        ShenShaChecker.__new__(ShenShaChecker),
        {'day_gan': '甲', 'year_zhi': '子', 'month_zhi': '子',
         'day_zhi': '申', 'hour_zhi': '午'})
    check('A3 未命中返回None', _r is None, str(_r))

    # B1 真实日课（2021-01-12 庚申日·己丑月）：发射且 +15
    sz, res = _score(datetime.date(2021, 1, 12))
    hit = [s for s in (res.get('shensha_list') or [])
           if s.get('name') == '天乙贵人']
    check('B1 发射天乙贵人', len(hit) == 1, str(hit))
    check('B2 分值15', bool(hit) and hit[0].get('score') == 15,
          str(hit[0].get('score') if hit else None))
    check('B3 描述含柱名', bool(hit) and '月柱' in str(hit[0].get('description')),
          str(hit[0].get('description') if hit else None))

    # B4 展示层仍输出命局贵人（单一表源改造后不丢）
    js = ((res.get('wu_xing_result') or {}).get('details') or {}).get('吉神') or []
    check('B4 展示层含天乙贵人', any('天乙贵人' in str(x) for x in js), str(js))

    # C1 多柱同时命中仍只计一次（穷举 2026 全年，找命中>=2柱的日）
    multi = 0
    d = datetime.date(2026, 1, 1)
    while d < datetime.date(2027, 1, 1):
        sz2 = calculate_sizhu((d.year, d.month, d.day), 0, 0, longitude=120)
        tg = ShenShaChecker.TIANYI_GUIREN_MAP.get(sz2.get('day_gan'))
        if tg:
            n = sum(1 for k in ('year_zhi', 'month_zhi', 'day_zhi', 'hour_zhi')
                    if sz2.get(k) in tg)
            if n >= 2:
                _, rr = _score(d)
                cnt = sum(1 for s in (rr.get('shensha_list') or [])
                          if s.get('name') == '天乙贵人')
                multi += 1
                if cnt != 1:
                    check('C1 多柱去重', False, '%s 命中%d柱 实得%d条' % (d, n, cnt))
                    break
        d += datetime.timedelta(days=1)
    check('C1 多柱去重', True, '覆盖 %d 个多柱命中日' % multi)

    # C2 反向断言：不命中日绝不发射（防恒真）
    sz3 = calculate_sizhu((2026, 3, 3), 0, 0, longitude=120)
    tg3 = ShenShaChecker.TIANYI_GUIREN_MAP.get(sz3.get('day_gan'))
    if tg3 and not any(sz3.get(k) in tg3 for k in
                       ('year_zhi', 'month_zhi', 'day_zhi', 'hour_zhi')):
        _, r3 = _score(datetime.date(2026, 3, 3))
        cnt = sum(1 for s in (r3.get('shensha_list') or [])
                  if s.get('name') == '天乙贵人')
        check('C2 不命中不发射', cnt == 0, '实得%d条' % cnt)
    else:
        check('C2 不命中不发射', True, '该日不适用（跳过取样）')

    # D1 条件择日吉神清单含天乙贵人（主程序源码，各事项组）
    src = open(os.path.join(ROOT, '主程序.py'), encoding='utf-8').read()
    seg = src[src.find('common_gods = ['): src.find('event_gods_map = ')]
    n = seg.count("'天乙贵人'")
    check('D1 条件择日含天乙贵人', n >= 5, '清单出现 %d 组' % n)

    # D2 单一表源：评分器不得再自带天乙字面表
    src2 = open(os.path.join(ROOT, 'modules', '评分器.py'), encoding='utf-8').read()
    check('D2 评分器无双表', "TIANYI_GUIREN_MAP" in src2
          and "'甲': ['丑', '未']" not in src2)

    # E1 15 通道发射一致性（含动土/通用两条手工副本，防「有展示无计分」复现）
    # 旧基线（§250 前 2026 全年 owners=[] 实测），每通道应恰好 +2340 = 156 天 ×15。
    from modules.shensha import get_checker
    EV15 = ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '开业',
            '安床', '作灶', '安葬', '入学', '求医', '签约', '通用']
    OLD = {'入宅': 11601, '移徙': 11601, '嫁娶': 10070, '动土': 35,
           '修造': 829, '拆舍': -81, '出行': 12374, '开业': 13747,
           '安床': 12738, '作灶': 6444, '安葬': 5647, '入学': 16444,
           '求医': 15142, '签约': 15592, '通用': 15607}
    days = []
    d = datetime.date(2026, 1, 1)
    while d <= datetime.date(2026, 12, 31):
        days.append(calculate_sizhu(d, 10, 0))
        d += datetime.timedelta(days=1)
    bad = []
    for ev in EV15:
        ck = get_checker(ev)
        tot, nty, dup = 0, 0, 0
        for sz in days:
            rows = ck.check(sz, [])
            tot += sum(s.get('score', 0) for s in rows)
            ty = [s for s in rows if s.get('name') == '天乙贵人']
            if ty:
                nty += 1
                if len(ty) > 1:
                    dup += 1
        if nty != 156 or dup or tot - OLD[ev] != 2340:
            bad.append('%s 天数%d 重复%d 增量%d' % (ev, nty, dup, tot - OLD[ev]))
    check('E1 15 通道各 156 天次、增量 2340、无重复', not bad, bad)

    print()
    if _fail:
        print('FAIL %d 项：%s' % (len(_fail), _fail))
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
