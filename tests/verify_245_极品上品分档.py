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
    r = _score(2026, 1, 8, '修造', '坤山艮向', OWN, 'feixing')
    c = _pp(r, '修造', OWN)
    check(c.get('lint_ok') is True, '01-08 日课校验无警告', c.get('lint_note'))
    check(build_decision_report(r, '修造').get('verdict_key') == 'warn',
          '01-08 顶部决策为黄牌（慎用）')
    # §256 重冻（2026-11-11 核验）：三取二格局项放行后，01-08 格局项（得令/德神）
    # 已不再单独拦截，仅剩必选项「硬忌」未过 → tier=none。core_miss 仍含三项
    # （得令/德神/硬忌），但 lint_note 只点名必选缺项「硬忌」。
    check(c.get('tier') == 'none' and c.get('shangpin') is False,
          '01-08 三取二后必选缺「硬忌」出局（§256 重冻）', c.get('core_miss'))
    check(c.get('perfect') is False, '01-08 不是极品')
    _n8 = str(c.get('lint_note'))
    check('必选核验缺' in _n8 and '硬忌' in _n8,
          '01-08 悬停文案点名必选缺项「硬忌」（§256 重冻）', _n8)

    # 用户截图原始案例：2026-10-10（火6/8 重度偏枯）现应被白名单踢出
    r0 = _score(2026, 10, 10, '修造', '坤山艮向', OWN, 'feixing')
    c0 = _pp(r0, '修造', OWN)
    check(c0.get('lint_ok') is True, '10-10 日课校验无警告（拦截来自白名单）')
    check(c0.get('tier') == 'none' and c0.get('shangpin') is False,
          '10-10 火6/8 重度偏枯已踢出上品', c0.get('tier'))

    r2 = _score(2026, 1, 31, '修造', '坤山艮向', OWN, 'feixing')
    c2 = _pp(r2, '修造', OWN)
    # §256 重冻：三取二放行格局项后，01-31 仅剩必选「硬忌」未过（core_miss 实测
    # 为「得令/硬忌」，得令属格局项被三取二放过，lint_note 只点名必选缺项）。
    check(c2.get('tier') == 'none' and c2.get('shangpin') is False,
          '01-31 三取二后必选缺「硬忌」出局（§256 重冻）', c2.get('core_miss'))
    check('必选核验缺' in str(c2.get('lint_note'))
          and '硬忌' in str(c2.get('lint_note')),
          '01-31 文案点名必选缺项「硬忌」（§256 重冻）', c2.get('lint_note'))

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

    print('\nD. 同源断言：极品 ⇔ 校验无警告+决策绿灯+core_ok（§256 三取二口径）')
    _bad = 0
    _n = 0
    for _dd in range(1, 32):
        _r = _score(2026, 1, _dd, '入宅')
        _c = _pp(_r, '入宅')
        _green = build_decision_report(_r, '入宅').get('verdict_key') == 'ok'
        # §256 重冻：core_ok 已是「三取二」口径（得令/合局/德神任意两项过 +
        # 必选项全过）。空事主（相主红线恒不触发）时
        # perfect ⇔ lint_ok 且决策绿灯 且 core_ok。
        _expect = bool(_c.get('lint_ok')) and _green and bool(_c.get('core_ok'))
        if _c.get('perfect') != _expect:
            _bad += 1
        _n += 1
    check(_bad == 0, '1月入宅 %d 天：极品⇔绿灯+校验+core_ok(三取二)逐条一致（§256 重冻）'
          % _n, _bad)

    print('\nF. 偏枯差异化阈值（§246：动土事 火/水≥5 判重度）')
    _r7 = _score(2026, 1, 8, '修造', '坤山艮向', OWN, 'feixing')
    _c7 = _pp(_r7, '修造', OWN)
    _n7 = ((_r7.get('score_details') or {}).get('偏枯计数') or {})
    check(_n7.get('火系') == 4, '01-08 偏枯计数已落库（火系=4）', _n7)
    # §256 重冻：01-08 三取二放行格局项后仅剩必选「硬忌」未过（在偏枯门槛之前
    # 即被必选拦截），偏枯计数落库与「火4/8 非重度」事实不变，仅列档结论随 §256 更新。
    check(_c7.get('tier') == 'none' and _c7.get('shangpin') is False,
          '01-08 火4/8 因必选缺「硬忌」出局（§256 重冻）', _c7.get('core_miss'))
    check('必选核验缺' in str(_c7.get('lint_note')),
          '01-08 悬停明示必选缺项（§256 重冻）', _c7.get('lint_note'))

    _r8 = _score(2026, 6, 24, '修造', '坤山艮向', OWN, 'feixing')
    _c8 = _pp(_r8, '修造', OWN)
    _n8 = ((_r8.get('score_details') or {}).get('偏枯计数') or {})
    check(_n8.get('火系') == 5, '06-24 偏枯计数火系=5', _n8)
    check(_c8.get('lint_ok') is True, '06-24 日课校验无警告（区分拦截来源）')
    check(_c8.get('tier') == 'none', '06-24 火5/8 重度偏枯踢出上品',
          _c8.get('tier'))
    from modules.排序键 import _shangpin_scan
    _blk8, _ = _shangpin_scan(_r8)
    check(any('重度偏枯' in x and '5/8' in x for x in _blk8),
          '06-24 阻断原因显式标注重度偏枯5/8', _blk8)

    _r9 = _score(2026, 1, 6, '入宅')
    _n9 = ((_r9.get('score_details') or {}).get('偏枯计数') or {})
    check('火系' in _n9 and '水系' in _n9,
          '偏枯计数对吉事同样落库（吉事阈值仍为4）', _n9)

    print('\nH. §247 相主红线 + 上品兜底（2026-11-09 方案A 拍板）')
    # 事主生肖必须用评分器真实键「生肖」（'year_sx' 是死链，相主恒 0）
    _OX = [{'name': '贵才', 'role': '福主', '生肖': '丑'},
           {'name': '贵林', 'role': '福主', '生肖': '未'}]

    # H1 缺陷复现：2026-11-02 入宅（无山向），相主 -20，旧版被判极品
    _h1 = _score(2026, 11, 2, '入宅', '', _OX, 'pure')
    _c1 = _pp(_h1, '入宅', _OX)
    _xz1 = int((_h1.get('score_details') or {}).get('相主得分') or 0)
    check(_xz1 < 0, '11-02 相主得分为负（缺陷复现）', _xz1)
    check(_c1.get('lint_ok') is True, '11-02 日课校验无警告（区分拦截来源）')
    check(build_decision_report(_h1, '入宅').get('verdict_key') == 'ok',
          '11-02 决策面板仍为绿灯（说明拦截来自相主红线）')
    check(_c1.get('perfect') is False and _c1.get('tier') == 'none',
          '11-02 相主负 → 剥夺极品', _c1.get('tier'))
    check('冲克事主' in str(_c1.get('lint_note'))
          and '剥夺极品/上品资格' in str(_c1.get('lint_note')),
          '11-02 悬停明确写出剥夺原因', _c1.get('lint_note'))

    # H2 上品兜底：2021-01-06 修造·乾山 总分 0(负分clamp)、相主 -100，旧版被判上品
    # （001 §272续 换样本：原 2021-03-21 因杀师时/鲁班煞 -30/-20→-5 总分涨至 +6，
    #   不再满足「总分非正」前提；2021-01-06 在新口径下仍非正且相主负，双要素保持）
    _h2 = _score(2021, 1, 6, '修造', '乾山巽向', _OX, 'pure')
    _c2 = _pp(_h2, '修造', _OX)
    check(int(_h2.get('score') or 0) <= 0, '2021-01-06 总分非正（缺陷复现）',
          _h2.get('score'))
    check(_c2.get('shangpin') is False and _c2.get('tier') == 'none',
          '2021-01-06 负分课不得列上品', _c2.get('tier'))

    import datetime as _dt
    # H3 穷举反向断言一：2026 入宅全年，极品中不得出现相主负分日
    _bad = []
    _d = _dt.date(2026, 1, 1)
    _n_perf = 0
    while _d <= _dt.date(2026, 12, 31):
        _r = _score(_d.year, _d.month, _d.day, '入宅', '', _OX, 'pure')
        _c = _pp(_r, '入宅', _OX)
        _xz = int((_r.get('score_details') or {}).get('相主得分') or 0)
        if _c.get('perfect'):
            _n_perf += 1
            if _xz < 0:
                _bad.append('%s(相主%+d)' % (_d, _xz))
        _d += _dt.timedelta(days=1)
    check(not _bad, '2026 入宅全年 %d 个极品中相主负分 0 个' % _n_perf,
          _bad[:5])

    # H4 穷举反向断言二：2021 修造全年，上品必须 相主≥0 且 总分>0 且 等级不含凶
    _bad2 = []
    _n_sp = 0
    _d = _dt.date(2021, 1, 1)
    while _d <= _dt.date(2021, 12, 31):
        _r = _score(_d.year, _d.month, _d.day, '修造', '乾山巽向', _OX, 'pure')
        _c = _pp(_r, '修造', _OX)
        if _c.get('shangpin'):
            _n_sp += 1
            _xz = int((_r.get('score_details') or {}).get('相主得分') or 0)
            _sc = int(_r.get('score') or 0)
            _lv = str(_r.get('level') or '')
            if _xz < 0 or _sc <= 0 or '凶' in _lv:
                _bad2.append('%s(相主%+d/总分%d/%s)' % (_d, _xz, _sc, _lv))
        _d += _dt.timedelta(days=1)
    check(not _bad2,
          '2021 修造全年 %d 个上品全部满足 相主≥0 且 总分>0 且 等级不含凶' % _n_sp,
          _bad2[:5])

    print('\nG. 源码锚点防回退')
    _src = os.path.join(_ROOT, 'modules', '排序键.py')
    _txt = open(_src, encoding='utf-8').read()
    check('_SHANGPIN_BLOCK_NAMES' in _txt and '三煞临山' in _txt,
          '排序键含上品阻断名单')
    check('build_decision_report' in _txt, '排序键已接入决策面板同源判定')
    _pk_src = open(os.path.join(_ROOT, 'modules', '评分器.py'),
                   encoding='utf-8').read()
    check("score_details['偏枯计数']" in _pk_src, '评分器已补存偏枯计数')
    _ui = open(os.path.join(_ROOT, 'modules', '反推UI.py'), encoding='utf-8').read()
    check('▲上品（动土可制化）' in _ui, '反推UI含上品标记')
    _mp = open(os.path.join(_ROOT, '主程序.py'), encoding='utf-8').read()
    check('上品(动土可制化)' in _mp, '主程序筛选下拉含上品档')
    # 001 §247 锚点
    check('_xz_block' in _txt and '_sp_score_ok' in _txt,
          '排序键含相主红线 _xz_block 与上品兜底 _sp_score_ok')
    check('冲克事主' in _txt and '剥夺极品/上品资格' in _txt,
          '排序键含「冲克事主→剥夺极品/上品」降级文案')

    print('\nFAIL %d' % len(FAILS))
    if FAILS:
        for _f in FAILS:
            print('  - %s' % _f)
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
