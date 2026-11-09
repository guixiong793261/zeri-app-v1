# -*- coding: utf-8 -*-
"""001 §245 极品 / 上品 分档回归（2026-11-09 用户拍板）。

口径：
  极品 = 日课校验无警告（§240）**且** 详情页顶部决策面板绿灯（verdict_key='ok'）
  上品 = 仅动土事（修造/动土/装修/拆舍）：校验无警告、无否决、无伐日/克山/
         三煞临山/金神到山；鲁班煞/土王用事/向方三煞/偏枯等可制化小煞放行。

A. 修造白名单：带向方三煞/土王用事/过燥 → 上品（非极品）
B. 绝不豁免：伐日 / 克山 → 不得上品（即使高分）
C. 非动土事不外溢：入宅黄牌日只能是「未列」，不得标上品
D. 同源断言：极品日与详情页决策绿灯逐条一致
E. 源码锚点防回退
"""
import io
import os
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
from modules.排序键 import perfect_profile
from modules.决策分析 import build_decision_report

FAILS = []
OWN = [{'name': '福主', 'role': '福主', 'year_sx': '龙'}]


def check(cond, label, detail=''):
    print('  [%s] %s%s' % ('PASS' if cond else 'FAIL', label,
                          ('  | ' + str(detail)) if detail else ''))
    if not cond:
        FAILS.append(label)


def _sz(y, m, d, h=12):
    r = calculate_sizhu((y, m, d), h, 0, longitude=120)
    r['year'], r['month'], r['day'] = y, m, d
    return r


def _score(y, m, d, ev, sx='', owners=None, mode='pure'):
    return calculate_score(_sz(y, m, d), ev,
                           owners=[dict(o) for o in (owners or [])],
                           shan_xiang=sx, zeli_mode=mode)


def _pp(r, ev, owners=None):
    return perfect_profile(r, [dict(o) for o in (owners or [])], ev)


def main():
    print('\nA. 动土事白名单 → 上品')
    r = _score(2026, 10, 10, '修造', '坤山艮向', OWN, 'feixing')
    c = _pp(r, '修造', OWN)
    check(c.get('lint_ok') is True, '10-10 日课校验无警告', c.get('lint_note'))
    check(build_decision_report(r, '修造').get('verdict_key') == 'warn',
          '10-10 顶部决策为黄牌（慎用）')
    check(c.get('tier') == 'shangpin' and c.get('shangpin') is True,
          '10-10 落入上品', c.get('tier'))
    check(c.get('perfect') is False, '10-10 不是极品')
    check('上品（动土可制化）' in str(c.get('lint_note')),
          '10-10 悬停文案含上品说明', c.get('lint_note'))

    r2 = _score(2026, 1, 31, '修造', '坤山艮向', OWN, 'feixing')
    c2 = _pp(r2, '修造', OWN)
    check(c2.get('tier') == 'shangpin', '01-31（土王用事）落入上品', c2.get('tier'))
    check('土王用事' in str(c2.get('lint_note')), '01-31 文案点名土王用事',
          c2.get('lint_note'))

    print('\nB. 绝不豁免重煞 → 不得上品（反向断言）')
    r3 = _score(2026, 5, 11, '修造', '坤山艮向', OWN, 'feixing')
    c3 = _pp(r3, '修造', OWN)
    _h3 = [str(x) for x in ((r3.get('sansha_info') or {}).get('heavy_sha_names') or [])]
    check(any('伐日' in x for x in _h3), '05-11 确含伐日重煞', _h3)
    check(int(r3.get('score') or 0) >= 150, '05-11 分数不低（非低分兜底）',
          r3.get('score'))
    check(c3.get('lint_ok') is True, '05-11 日课校验无警告（说明拦截的是白名单而非校验）')
    check(c3.get('tier') == 'none' and c3.get('shangpin') is False,
          '05-11 仍不得列上品', c3.get('tier'))

    r4 = _score(2026, 7, 12, '修造', '坤山艮向', OWN, 'feixing')
    _h4 = [str(x) for x in ((r4.get('sansha_info') or {}).get('heavy_sha_names') or [])]
    check(any('克山' in x for x in _h4), '07-12 确含克山', _h4)
    check(_pp(r4, '修造', OWN).get('tier') == 'none', '07-12 克山不得列上品')

    print('\nC. 非动土事不外溢')
    r5 = _score(2026, 1, 6, '入宅')
    c5 = _pp(r5, '入宅')
    check(c5.get('tier') == 'perfect' and c5.get('perfect') is True,
          '01-06 入宅为极品', c5.get('lint_note'))
    check(c5.get('shangpin') is False, '01-06 入宅同时不得标上品')
    r6 = _score(2026, 1, 8, '入宅')
    c6 = _pp(r6, '入宅')
    check(c6.get('lint_ok') is True, '01-08 入宅日课校验无警告')
    check(c6.get('tier') == 'none' and c6.get('shangpin') is False,
          '01-08 入宅黄牌不因动土白名单外溢', c6.get('tier'))

    print('\nD. 同源断言：极品 ⇔ 详情页决策绿灯')
    _bad = 0
    _n = 0
    for _dd in range(1, 32):
        _r = _score(2026, 1, _dd, '入宅')
        _c = _pp(_r, '入宅')
        _green = build_decision_report(_r, '入宅').get('verdict_key') == 'ok'
        if _c.get('perfect') != (_c.get('lint_ok') and _green):
            _bad += 1
        _n += 1
    check(_bad == 0, '1月入宅 %d 天：极品判定与决策绿灯逐条一致' % _n, _bad)

    print('\nE. 源码锚点防回退')
    _src = os.path.join(_ROOT, 'modules', '排序键.py')
    _txt = open(_src, encoding='utf-8').read()
    check('_SHANGPIN_BLOCK_NAMES' in _txt and '三煞临山' in _txt,
          '排序键含上品阻断名单')
    check('build_decision_report' in _txt, '排序键已接入决策面板同源判定')
    _ui = open(os.path.join(_ROOT, 'modules', '反推UI.py'), encoding='utf-8').read()
    check('▲上品（动土可制化）' in _ui, '反推UI含上品标记')
    _mp = open(os.path.join(_ROOT, '主程序.py'), encoding='utf-8').read()
    check('上品(动土可制化)' in _mp, '主程序筛选下拉含上品档')

    print('\nFAIL %d' % len(FAILS))
    if FAILS:
        for _f in FAILS:
            print('  - %s' % _f)
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
