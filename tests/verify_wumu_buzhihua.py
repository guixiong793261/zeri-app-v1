# -*- coding: utf-8 -*-
"""
五墓制化豁免回归锁（制化第一批 2026-10-21 随批更新）
======================================================
沿革：
- 2026-10-18 d6 批初版：拍板「制化层裁断前不得因月德自动豁免五墓」，
  本锁反向锚定「午月丙戌日仍发射五墓 -12」。
- 2026-10-21 制化第一批（001 §155 六项拍板，矩阵 #15 批准落地）：五墓豁免
  正式落地——「五月(午)、十一月(子)与月德并则不忌」（《协纪》卷六义例四；
  德神集仅月德，不含月德合/天德，无证据不放宽）。本锁随批更新（原脚本
  自注协议：制化层批次实现豁免时，本断言需随批更新）：
  A. 源码层：基类/通用 checker 五墓发射存在豁免分支（eval_wumu_exempt +
     WUMU_EXEMPT_KEY + 矩阵#15 锚注记），else 分支保留原 -12 发射；
  B. 行为层正锚：午月丙戌日（五墓+月德并）→ 发射豁免注记键 0 分，
     不再发射'五墓'正名（通用+嫁娶通道）；
  C. 行为层反锚：巳月丙戌日（五墓 fired，月德庚≠丙 无月德并）→ 仍发射
     '五墓' -12；
  D. 排除面：入宅/作灶仍零五墓发射（基类排除不动）；
  E. 哨兵：2026-11-04 入宅 224/★★★★★上吉（批次2 001 §159 鸣吠日 12→15
     统一高档后由 221 重冻；2026 全年无豁免触发日，
     探针 manifest 佐证）。

退出码 0=全过 1=有失败。
"""
import io
import os
import sys
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FAILS = []


def check(name, cond, extra=''):
    print(('  PASS  ' if cond else '  FAIL  ') + name + (('  | ' + extra) if (extra and not cond) else ''))
    if not cond:
        FAILS.append(name)


def main():
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha import get_checker
    from modules.shensha.制化引擎 import (eval_wumu_exempt, WUMU_EXEMPT_KEY,
                                          DE_GODS_ALL)

    print('== A. 源码层：发射块豁免分支与锚注记 ==')
    base = open(os.path.join(ROOT, 'modules', 'shensha', '神煞基类.py'),
                encoding='utf-8').read()
    common = open(os.path.join(ROOT, 'modules', 'shensha', '通用神煞.py'),
                  encoding='utf-8').read()
    for tag, src in (('基类', base), ('通用', common)):
        i = src.find("self._add_shensha('五墓'")
        check('%s 仍存在五墓发射块' % tag, i > 0)
        blk = src[max(0, i - 700):i + 200]
        check('%s 豁免分支接线 eval_wumu_exempt' % tag, 'eval_wumu_exempt' in blk)
        check('%s 豁免键 WUMU_EXEMPT_KEY' % tag, 'WUMU_EXEMPT_KEY' in blk)
        check('%s 矩阵#15 锚注记' % tag, '矩阵#15' in blk)
    check('基类 else 分支保留 -12', "self._add_shensha('五墓', -12, '五墓主死丧')" in base)
    check('通用 else 分支保留 -12', "self._add_shensha('五墓', -12, '五墓之日，忌埋葬')" in common)

    print('== B. 行为层正锚：午月丙戌（五墓+月德并）→ 豁免键 0 分 ==')
    anchor_b = None
    d = datetime.date(2020, 1, 1)
    while d <= datetime.date(2035, 12, 31):
        sz = calculate_sizhu(d, 12, 0)
        if sz['month_zhi'] == '午' and sz['day_gan'] + sz['day_zhi'] == '丙戌':
            anchor_b = (d, sz)
            break
        d += datetime.timedelta(days=1)
    check('2020–2035 找到午月丙戌锚日', anchor_b is not None)
    if anchor_b:
        d, sz = anchor_b
        check('引擎 eval_wumu_exempt(锚日)=True', eval_wumu_exempt(sz) is True)
        for ev in ('通用', '嫁娶'):
            names = [(s['name'], s['score']) for s in get_checker(ev).check(sz, [])]
            ex = [x for x in names if x[0] == WUMU_EXEMPT_KEY]
            wm = [x for x in names if x[0] == '五墓']
            check('%s通道 锚日发射豁免键0分' % ev, ex == [(WUMU_EXEMPT_KEY, 0)], str(names))
            check('%s通道 锚日不再发射五墓正名' % ev, not wm, str(names))

    print('== C. 行为层反锚：巳月丙戌（无月德并）→ 仍 -12 ==')
    anchor_c = None
    d = datetime.date(2020, 1, 1)
    while d <= datetime.date(2035, 12, 31):
        sz = calculate_sizhu(d, 12, 0)
        if sz['month_zhi'] == '巳' and sz['day_gan'] + sz['day_zhi'] == '丙戌':
            anchor_c = (d, sz)
            break
        d += datetime.timedelta(days=1)
    check('2020–2035 找到巳月丙戌锚日', anchor_c is not None)
    if anchor_c:
        d, sz = anchor_c
        check('引擎 eval_wumu_exempt(反锚日)=False', eval_wumu_exempt(sz) is False)
        names = [(s['name'], s['score']) for s in get_checker('通用').check(sz, [])]
        check('反锚日仍发射五墓 -12', ('五墓', -12) in names, str(names))
        check('反锚日无豁免键', not any(x[0] == WUMU_EXEMPT_KEY for x in names))

    print('== D. 排除面：入宅/作灶零五墓发射（2026 全年抽查） ==')
    bad = []
    d = datetime.date(2026, 1, 1)
    while d <= datetime.date(2026, 12, 31):
        sz = calculate_sizhu(d, 12, 0)
        for ev in ('入宅', '作灶'):
            for s in get_checker(ev).check(sz, []):
                if s['name'] in ('五墓', WUMU_EXEMPT_KEY):
                    bad.append((str(d), ev, s['name']))
        d += datetime.timedelta(days=1)
    check('入宅/作灶 2026 全年无五墓/豁免键发射', not bad, str(bad[:5]))

    print('== E. 哨兵：2026-11-04 入宅 224/上吉（批次2 001 §159 重冻） ==')
    from modules.评分器 import calculate_score
    sz = calculate_sizhu(datetime.date(2026, 11, 4), 12, 0)
    r = calculate_score(sz, '入宅')
    check('哨兵分=224', r['score'] == 224, str(r['score']))
    check('哨兵级=上吉', '上吉' in str(r.get('level', '')))
    check('哨兵日无五墓/豁免键', not any(
        s['name'] in ('五墓', WUMU_EXEMPT_KEY) for s in r.get('shensha_list', [])))
    check('德神封闭集不含天恩', '天恩' not in DE_GODS_ALL)

    print()
    print('FAILS=%d' % len(FAILS))
    return 1 if FAILS else 0


if __name__ == '__main__':
    raise SystemExit(main())
