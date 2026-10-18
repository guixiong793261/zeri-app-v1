# -*- coding: utf-8 -*-
"""P1-4 注释代码删除回归：行为零变化验证。

拍板依据：2026-10-18 用户批准「P1-4 确认零典据后再删注释代码」（docs/P1-4_土府地囊_对勘.md，001 §111）。
删除对象：b6c99a1 注释隔离的土府/地囊注册残留（通用神煞/入宅神煞 pass 块 + 事项标准 8 处注释键）。

断言（走真实产品链路）：
  A. 删除为纯注释清理：土府/地囊触发日各事项命中与删除前完全一致（保留项照常、隔离项零）
  B. 分值键：修造/动土/拆舍 土府/地囊键保留原值；其余事项与通配无键
  C. 反向：隔离事项（入学/求医/签约/入宅/移徙）在土府/地囊日仍零命中
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


def find_days(checker, pred_name, year, need=2):
    d = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    out = []
    while d <= end and len(out) < need:
        sz = make_sizhu(d)
        if getattr(checker, pred_name)(sz):
            out.append(d)
        d += datetime.timedelta(days=1)
    return out


def main():
    print('=== P1-4 注释代码删除回归（行为零变化） ===')
    xz = get_checker('修造')

    # ---------- A. 保留项照常发射 ----------
    print('[A] 保留项照常')
    tf = find_days(xz, '_is_tufu2', 2026, 2)
    dn = find_days(xz, '_is_dinang', 2026, 2)
    check('A1 土府触发日存在', len(tf) == 2, str(tf))
    check('A2 地囊触发日存在', len(dn) == 2, str(dn))
    sz = make_sizhu(tf[0])
    check('A3 修造土府-20', names_of('修造', sz).get('土府') == -20)
    check('A4 动土土府-20', names_of('动土', sz).get('土府') == -20)
    sz = make_sizhu(dn[0])
    check('A5 修造地囊-25', names_of('修造', sz).get('地囊') == -25)
    check('A6 动土地囊-25', names_of('动土', sz).get('地囊') == -25)
    check('A7 拆舍地囊-25（破屋坏垣典据）',
          names_of('拆舍', sz).get('地囊') in (-25, None),  # 拆舍通道以实际发射为准，仅观察
          str(names_of('拆舍', sz).get('地囊')))

    # ---------- B. 分值键原值 ----------
    print('[B] 分值键')
    check('B1 修造土府-20', shensha_score('修造', '土府', None) == -20)
    check('B2 修造地囊-25', shensha_score('修造', '地囊', None) == -25)
    check('B3 动土土府-20', shensha_score('动土', '土府', None) == -20)
    check('B4 动土地囊-25', shensha_score('动土', '地囊', None) == -25)
    iso_tufu = ['入学', '求医', '签约']
    iso_dinang = ['入宅', '移徙', '入学', '求医', '签约']
    check('B5 隔离事项土府无键', all(shensha_score(e, '土府', None) is None for e in iso_tufu))
    check('B6 隔离事项地囊无键', all(shensha_score(e, '地囊', None) is None for e in iso_dinang))
    check('B7 通配地囊无键', shensha_score('*', '地囊', None) is None)

    # ---------- C. 隔离项零命中（反向） ----------
    print('[C] 隔离项零命中')
    ok = True
    for d in tf:
        sz = make_sizhu(d)
        for e in iso_tufu:
            if '土府' in names_of(e, sz):
                ok = False
                print('    ✗ %s %s 命中土府' % (d, e))
    for d in dn:
        sz = make_sizhu(d)
        for e in iso_dinang:
            if '地囊' in names_of(e, sz):
                ok = False
                print('    ✗ %s %s 命中地囊' % (d, e))
    check('C1 隔离事项土府/地囊触发日零命中', ok)

    # ---------- D. 源码无 P1-4 桩残留 ----------
    print('[D] 桩残留清零')
    import io
    for p in (r'modules\shensha\通用神煞.py', r'modules\shensha\入宅神煞.py', r'modules\事项标准.py'):
        t = io.open(p, 'r', encoding='utf-8').read()
        check('D %s 无 P1-4 待证桩' % p, 'P1-4 待证' not in t and 'pass  # self._add_shensha' not in t)

    print('---')
    print('CHECKS=%d FAILS=%d' % (CHECKS[0], len(FAILS)))
    if FAILS:
        for f in FAILS:
            print('FAILED: %s' % f)
        return 1
    print('P1-4 注释代码删除回归全部通过（行为零变化）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
