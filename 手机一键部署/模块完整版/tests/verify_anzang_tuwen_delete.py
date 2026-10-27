# -*- coding: utf-8 -*-
"""P1-5 安葬土瘟删除回归。

拍板依据：2026-10-18 用户批准「P1-5 P1 安葬土瘟 -20 删除候选：陈书明言『止忌破土
不忌安葬』；补协纪/考原对勘确认无相反后删」（docs/P1-5_安葬土瘟_对勘.md，001 §112）。

断言（走真实产品链路）：
  A. 土瘟触发日：安葬无土瘟条目；修造/动土/作灶 -20 保留
  B. 分值键：('安葬','土瘟') 已删；修造/动土/作灶 -20 保留
  C. 反向：安葬 checker 不再因 _is_tuwen 发射任何土族煞
退出码：全过 0，任一失败 1。
"""
import sys
import datetime

sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')

from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.事项标准 import shensha_score

FAILS = []
CHECKS = [0]


def check(name, cond, detail=''):
    CHECKS[0] += 1
    if cond:
        print('  PASS %s' % name)
    else:
        FAILS.append(name)
        print('  FAIL %s %s' % (name, detail))


def make_sizhu(d):
    sz = calculate_sizhu(d, 10, 0)
    sz['year'] = d.year
    sz['month'] = d.month
    sz['day'] = d.day
    sz['date'] = d
    return sz


def names_of(event, sz):
    ck = get_checker(event)
    return {s['name']: s.get('score') for s in ck.check(sz, [])
            if isinstance(s, dict) and s.get('score', 0) < 0}


def main():
    print('=== P1-5 安葬土瘟删除回归 ===')
    pred = get_checker('嫁娶')

    # 找 2026 年土瘟日（四季土旺日）
    d = datetime.date(2026, 1, 1)
    end = datetime.date(2026, 12, 31)
    tw_days = []
    while d <= end and len(tw_days) < 2:
        if pred._is_tuwen(make_sizhu(d)):
            tw_days.append(d)
        d += datetime.timedelta(days=1)
    check('A1 土瘟触发日存在(基线)', len(tw_days) == 2, str(tw_days))

    for d in tw_days:
        sz = make_sizhu(d)
        az = names_of('安葬', sz)
        check('A2 %s 安葬无土瘟条目' % d, '土瘟' not in az, str(az.get('土瘟')))
        check('A3 %s 安葬无土族煞残留' % d,
              not any(n in az for n in ('土瘟', '土府', '地囊', '土符')), str(az))
    sz = make_sizhu(tw_days[0])
    check('A4 修造土瘟-20保留', names_of('修造', sz).get('土瘟') == -20)
    check('A5 动土土瘟-20保留', names_of('动土', sz).get('土瘟') == -20)
    check('A6 作灶土瘟-20保留', names_of('作灶', sz).get('土瘟') == -20)
    # 反向：P2 待证事项（基类通用链服务）土瘟维持现状不被误伤
    for ev in ('嫁娶', '入宅', '安床', '出行'):
        check('A7 %s土瘟维持现状' % ev, names_of(ev, sz).get('土瘟') == -20,
              str(names_of(ev, sz).get('土瘟')))

    print('[B] 分值键')
    check('B1 安葬土瘟键已删', shensha_score('安葬', '土瘟', None) is None)
    check('B2 修造土瘟-20', shensha_score('修造', '土瘟', None) == -20)
    check('B3 动土土瘟-20', shensha_score('动土', '土瘟', None) == -20)
    check('B4 作灶土瘟-20', shensha_score('作灶', '土瘟', None) == -20)

    print('[C] 源码锚')
    import io
    t = io.open(r'modules\shensha\安葬神煞.py', 'r', encoding='utf-8').read()
    check('C1 安葬checker无土瘟发射', "_add_shensha('土瘟'" not in t)
    t2 = io.open(r'modules\事项标准.py', 'r', encoding='utf-8').read()
    check('C2 事项标准无安葬土瘟键', "('安葬', '土瘟')" not in t2)

    print('---')
    print('CHECKS=%d FAILS=%d' % (CHECKS[0], len(FAILS)))
    if FAILS:
        for f in FAILS:
            print('FAILED: %s' % f)
        return 1
    print('P1-5 安葬土瘟删除回归全部通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
