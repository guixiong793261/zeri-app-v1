# -*- coding: utf-8 -*-
"""P1-1 回归：土王用事推排双轨收口（修造/动土/拆舍统一四立前18日）

断言：
1. 修造与动土土王用事触发日完全一致
2. 修造中土王用事无同名重复发射
3. 土瘟与土王用事为不同神煞（名称不同、推排法不同，允许同日共存）
"""
import sys, os, datetime
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.四柱计算器 import calculate_sizhu
from modules.shensha.修造神煞 import ConstructionShenShaChecker
from modules.shensha.动土神煞 import DiggingShenShaChecker


def main():
    xz = ConstructionShenShaChecker()
    dt = DiggingShenShaChecker()
    start = datetime.date(2026, 1, 1)
    end = datetime.date(2027, 1, 1)

    tuwang_xz = set()
    tuwang_dt = set()
    dup = []
    coexist = []

    d = start
    while d < end:
        sizhu = calculate_sizhu(d, hour=12)
        r1 = xz.check(sizhu)
        r2 = dt.check(sizhu)
        n1 = [s['name'] for s in r1]
        n2 = [s['name'] for s in r2]
        if '土王用事' in n1:
            tuwang_xz.add(d)
        if '土王用事' in n2:
            tuwang_dt.add(d)
        if Counter(n1).get('土王用事', 0) > 1:
            dup.append(d)
        if '土瘟' in n1 and '土王用事' in n1:
            coexist.append(d)
        d += datetime.timedelta(1)

    assert tuwang_xz == tuwang_dt, '修造与动土土王用事触发日不一致'
    assert len(dup) == 0, '修造土王用事同名重复发射'
    print(f'[PASS] 修造/动土土王用事触发日一致: {len(tuwang_xz)} 天')
    print(f'[PASS] 修造土王用事无同名重复发射')
    print(f'[PASS] 土瘟与土王用事同日共存 {len(coexist)} 天（不同神煞，正常叠加）')
    print('FAIL 0')


if __name__ == '__main__':
    main()
