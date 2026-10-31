# -*- coding: utf-8 -*-
"""
反推引擎（单事项 Top-N）命令行验证（001 §210 Commit 1）
================================================================================
验证面：
A. 排序键单点化：hour_rank_key 7 位字段顺序/取值锁定；day_rank_key / classify_day /
   rank_day 的收录层与"吉神契合度优先于总分"口径。
B. 交节防雷：2026-01-05（小寒 16:23）酉/戌/亥时月柱为己丑、午时仍戊子；
   12 时辰日柱一致、时柱各异（逐时四柱按权威值，不套午时柱）。
C. 对拍零漂移：反推榜每日最优时辰的分数/时柱，与"直调 calculate_sizhu +
   calculate_score"逐条相等（禁止分数分裂）。
D. 收录与排序：否决日不入榜但仍进 vetoed/all_days；慎用日入榜且排吉日之后；
   榜单按 (收录层, 否决数, 吉神契合度, 总分) 非降序。
E. 时间轴：入榜日 12 条时辰记录齐备，best_hour 与其中之一完全对上。
F. 参数校验：未知事项 / days 越界（0、91）/ top_n<1 均抛 ValueError。
G. 线程与回调：后台线程内调用可完成且结果与同步一致；progress 按日回调；
   cancel 生效时返回已算部分并置 cancelled=True。

退出码：0=全过 1=有失败（FAIL N 计数）
================================================================================
"""
import io
import json
import os
import sys
import threading
import time
from datetime import date

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu       # noqa: E402
from modules.评分器 import calculate_score           # noqa: E402
from modules.排序键 import (hour_rank_key, day_rank_key, classify_day,   # noqa: E402
                           rank_day, jishen_fit)
from modules.反推引擎 import (search_top_n, scan_day, HOURS, MAX_DAYS)  # noqa: E402

FAILS = []
CHECKS = [0]


def check(cond, label, detail=''):
    CHECKS[0] += 1
    if cond:
        print('  [PASS] %s' % label)
    else:
        FAILS.append(label + (('  → ' + detail) if detail else ''))
        print('  [FAIL] %s %s' % (label, detail))


def _score(sz, ev='入宅', ctx=None):
    _c = ctx or {}
    return calculate_score(sz, ev, [], _c.get('house_type'), _c.get('shan_xiang'),
                           _c.get('zao_xiang'), _c.get('zao_wei'),
                           _c.get('chuang_wei'),
                           zaozhu_mode=_c.get('zaozhu_mode'),
                           zeli_mode=_c.get('zeli_mode') or 'feixing')


# ==================== A. 排序键字段锁定 ====================
def test_rank_keys():
    print('\n[A] 排序键单点化')
    _k = hour_rank_key(disabled=True, veto_count=2, fenjin_level=2,
                       fenjin_deduct=100, ck_score=8, ck_weight=1,
                       score=88, shashi=1, wuxing=30)
    check(_k == (1, 3, -8, -(88 - 100), 1, 2, -30),
          'hour_rank_key 7 位字段顺序与取值', str(_k))

    # 吉神契合度优先于总分（用户 §210 拍板）
    _r_high_score = {'veto_reasons': [], 'score': 100, 'level': '上吉',
                     'shensha_list': [], 'ji_list': []}
    _r_jishen = {'veto_reasons': [], 'score': 90, 'level': '上吉',
                 'shensha_list': [{'name': '天德', 'score': 20}], 'ji_list': []}
    check(day_rank_key(_r_jishen) < day_rank_key(_r_high_score),
          '吉神契合度（天德）优先于更高总分')

    # 慎用降权：分数更高的慎用日仍排在吉日之后
    _r_cautious = {'veto_reasons': [], 'score': 200, 'level': '上吉',
                   'shensha_list': [{'name': '月德', 'score': 18}],
                   'ji_list': ['忌动土']}
    check(classify_day(_r_cautious, '入宅') == '慎用',
          '有扣分项且不禁本事项 → 慎用', classify_day(_r_cautious, '入宅'))
    check(rank_day(_r_cautious, '入宅') > rank_day(_r_jishen, '入宅'),
          '慎用（收录层 1）恒排吉日（收录层 0）之后')

    # 否决判据与扫日过滤链同源：否决不因"不宜X"文案翻转为慎用
    _r_buyi = {'veto_reasons': [], 'score': 60, 'level': '上吉', 'ji_list': [],
               'shensha_list': [{'name': '某煞', 'score': -5,
                                 'description': '不宜入宅'}]}
    check(classify_day(_r_buyi, '入宅') == '慎用',
          '"不宜X"不构成否决（仅黄标慎用）')
    _r_ji = {'veto_reasons': [], 'score': 60, 'level': '上吉',
             'ji_list': ['忌入宅'], 'shensha_list': []}
    check(classify_day(_r_ji, '入宅') == '否决', '忌本事项 → 否决')

    check(jishen_fit(_r_jishen) == 20, 'jishen_fit 主锚吉神加权', str(jishen_fit(_r_jishen)))


# ==================== B. 交节逐时四柱 ====================
def test_jieqi():
    print('\n[B] 交节逐时四柱（2026-01-05 小寒）')
    _sz, _r, _hrs = scan_day(date(2026, 1, 5), '入宅', [])
    check(len(_hrs) == 12, '12 时辰记录齐备', str(len(_hrs)))
    _by = {_h['地支']: _h for _h in _hrs}
    check(_by['午']['月柱'] == '戊子', '午时月柱=戊子（交节前）', _by['午']['月柱'])
    for _z in ('酉', '戌', '亥'):
        check(_by[_z]['月柱'] == '己丑', '%s时月柱=己丑（交节后权威值）' % _z,
              _by[_z]['月柱'])
    check(len({_h['日柱'] for _h in _hrs}) == 1, '12 时辰日柱一致')
    check(len({_h['时柱'] for _h in _hrs}) == 12, '12 时辰时柱互异')


# ==================== C/D/E. 反推榜单 ====================
def test_ranking():
    print('\n[C/D/E] 反推榜（入宅，2026-06-01 起 30 天）')
    t0 = time.time()
    _res = search_top_n(days=30, event_type='入宅', owners=[], start=date(2026, 6, 1))
    _meta = _res['meta']
    _wall = time.time() - t0
    check(_meta['days'] == 30 and len(_res['all_days']) == 30,
          '扫描 30 天全覆盖', str(_meta['days']))
    check(_meta['candidates'] + _meta['vetoed'] == 30,
          '候选数 + 否决数 = 扫描数')
    check(_meta['elapsed'] < 20, '30 天耗时 < 20s（实测 %.2fs）' % _meta['elapsed'])
    check(len(_res['days']) == min(10, _meta['candidates']),
          'Top N 默认 10 条', str(len(_res['days'])))

    _veto_dates = {_v['date'] for _v in _res['vetoed']}
    _top_dates = {_d['date'] for _d in _res['days']}
    check(not (_veto_dates & _top_dates), '否决日不入榜')
    check(all(_d['kind'] in ('吉日', '慎用') for _d in _res['days']),
          '入榜日仅吉日/慎用')
    check(any(_d['kind'] == '慎用' for _d in _res['days']),
          '慎用日入榜（本窗口应有）')
    check(all(_d['kind'] != '慎用' for _d in _res['days'][:5]),
          '前 5 名均为吉日（慎用已降权）')

    # 排序单调：收录层 → 否决数 → 吉神契合度 → 总分
    _keys = [(0 if _d['kind'] == '吉日' else 1, len(_d['veto_reasons']),
              -_d['jishen_fit'], -_d['score']) for _d in _res['days']]
    check(all(_keys[i] <= _keys[i + 1] for i in range(len(_keys) - 1)),
          '榜单排序键非降序（吉神优先、总分其后）', str(_keys))

    # 对拍零漂移：直调 calculate_sizhu + calculate_score 复核每日最优时辰
    _zhi2h = {_z: _h for _h, _z in HOURS}
    _mismatch = []
    for _d in _res['days']:
        _z = _d['best_hour']['地支']
        _sz = calculate_sizhu(date.fromisoformat(_d['date']), _zhi2h[_z], 0)
        _sz['year'] = int(_d['date'][:4])
        _sz['month'] = int(_d['date'][5:7])
        _sz['day'] = int(_d['date'][8:10])
        _r = _score(_sz, '入宅')
        if int(_r.get('score') or 0) != _d['score']:
            _mismatch.append('%s %s 反推=%s 直算=%s' % (
                _d['date'], _z, _d['score'], _r.get('score')))
        if str(_sz.get('时柱', '')) != _d['sizhu'].split(' ')[-1]:
            _mismatch.append('%s 时柱不一致' % _d['date'])
    check(not _mismatch, '每日最优时辰分数/时柱与直调评分逐条相等',
          '; '.join(_mismatch[:4]))

    # 时间轴：12 条记录，best_hour 与其中之一完全对上
    _bad_tl = []
    for _d in _res['days']:
        _n = len(_d['hours'])
        if _n != 12:
            _bad_tl.append('%s hours=%d' % (_d['date'], _n))
            continue
        _hit = [h for h in _d['hours']
                if h['地支'] == _d['best_hour']['地支']
                and h['score'] == _d['score']]
        if not _hit:
            _bad_tl.append('%s best_hour 未命中' % _d['date'])
    check(not _bad_tl, '入榜日时间轴 12 时辰齐备且最优时辰命中',
          '; '.join(_bad_tl[:3]))
    return _res


# ==================== F. 参数校验 ====================
def test_validation():
    print('\n[F] 参数校验')
    for _kw, _label in (
            ({'event_type': '不存在的事项'}, '未知事项'),
            ({'days': 0}, 'days=0'),
            ({'days': MAX_DAYS + 1}, 'days=91'),
            ({'top_n': 0}, 'top_n=0')):
        _args = {'days': 1, 'event_type': '入学', 'owners': [],
                 'start': date(2026, 6, 1)}
        _args.update(_kw)
        try:
            search_top_n(**_args)
            check(False, '%s 应抛 ValueError' % _label)
        except ValueError:
            check(True, '%s 抛 ValueError' % _label)


# ==================== G. 线程/回调/取消与确定性 ====================
def test_thread_and_cancel():
    print('\n[G] 线程 / 回调 / 取消 / 确定性')
    _res1 = search_top_n(days=7, event_type='入学', owners=[], start=date(2026, 6, 1))
    _res2 = search_top_n(days=7, event_type='入学', owners=[], start=date(2026, 6, 1))
    check(json.dumps(_res1['days'], ensure_ascii=False, sort_keys=True) ==
          json.dumps(_res2['days'], ensure_ascii=False, sort_keys=True),
          '同输入两次调用结果逐字段一致（确定性）')

    _box = {}

    def _worker():
        _box['res'] = search_top_n(days=7, event_type='入学', owners=[],
                                   start=date(2026, 6, 1),
                                   progress=lambda done, tot, d:
                                   _box.setdefault('prog', []).append((done, tot)))

    _th = threading.Thread(target=_worker)
    _th.start()
    _th.join(timeout=120)
    check(not _th.is_alive(), '后台线程内调用可完成')
    check(_box.get('res') is not None and
          json.dumps(_box['res']['days'], ensure_ascii=False, sort_keys=True) ==
          json.dumps(_res1['days'], ensure_ascii=False, sort_keys=True),
          '线程内结果与同步调用一致')
    _prog = _box.get('prog') or []
    check(len(_prog) == 7 and all(_p[1] == 7 for _p in _prog)
          and [p[0] for p in _prog] == list(range(1, 8)),
          'progress 按日递增回调 7 次')

    _calls = []

    def _cancel():
        _calls.append(1)
        return len(_calls) > 3

    _res3 = search_top_n(days=30, event_type='入学', owners=[],
                         start=date(2026, 6, 1), cancel=_cancel)
    check(_res3['meta']['cancelled'] is True and _res3['meta']['scanned'] == 3,
          'cancel 生效：返回已算 3 天并置 cancelled',
          str((_res3['meta']['cancelled'], _res3['meta']['scanned'])))


if __name__ == '__main__':
    print('=' * 72)
    print('反推引擎验证（001 §210 Commit 1）')
    print('=' * 72)
    test_rank_keys()
    test_jieqi()
    test_ranking()
    test_validation()
    test_thread_and_cancel()
    print('\n' + '=' * 72)
    if FAILS:
        print('FAIL %d / %d 项断言' % (len(FAILS), CHECKS[0]))
        for _f in FAILS:
            print('  - %s' % _f)
        sys.exit(1)
    print('全部通过：%d 项断言' % CHECKS[0])
    print('=' * 72)
    sys.exit(0)
