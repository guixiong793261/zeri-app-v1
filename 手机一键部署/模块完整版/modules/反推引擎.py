# -*- coding: utf-8 -*-
"""
================================================================================
反推引擎（001 §210 Commit 1）：给定事项 → 反推指定日期范围内的 Top-N 吉日
================================================================================
边界（预研草案 §二 / §五，用户 2026-10-31 拍板 P1）：
    - 只做"单事项 Top-N"，不做同日多动作组局（P2）；
    - 动作级（发轿/迎娶/交拜）独立立项，禁止复用嫁娶评分；
    - 每日本就逐时辰实评（与主程序扫日同口径），算力≈现有扫日成本，
      因此不另做外围粗筛（90 天实测 2.9s~6.6s）。

单一事实源：
    - 时辰择优排序键：modules.排序键.hour_rank_key（与主程序 _rescan/_inject 同源）；
    - 分金预览、计分侧神煞清单、杀师判据：modules.排序键；
    - 日级收录/排序：modules.排序键.classify_day / rank_day。
    本模块禁止再手写任何元组或复制分值，只负责"调度 + 逐时四柱 + 记录整理"。

交节防雷：
    - calculate_sizhu 按时辰精度返回年月日柱（权威值）；
    - 仅当某时辰的年/月/日柱与午时基准完全一致时才复用基准字段；
      不一致（跨节气时辰，如 2026-01-05 小寒 16:23 后的酉/戌/亥月柱己丑）
      一律保留该时辰自己的权威值，禁止套用午时柱。
================================================================================
"""

import time
from datetime import date, timedelta

from modules.四柱计算器 import calculate_sizhu, get_lunar_date
from modules.评分器 import calculate_score
from modules.事项标准 import UI_EVENTS, MARRIAGE_EVENTS
from modules.排序键 import (fenjin_preview_penalty, scoring_shensha,
                           shashi_hour, hour_rank_key,
                           classify_day, rank_day, jishen_fit,
                           deduct_items, deduct_sum)

# 十二时辰（起始小时 → 地支），与主程序扫日候选一致
HOURS = [(0, '子'), (2, '丑'), (4, '寅'), (6, '卯'), (8, '辰'), (10, '巳'),
         (12, '午'), (14, '未'), (16, '申'), (18, '酉'), (20, '戌'), (22, '亥')]

# 时段标签（反推时间轴展示用）
HOUR_SPAN = {'子': '23-01', '丑': '01-03', '寅': '03-05', '卯': '05-07',
             '辰': '07-09', '巳': '09-11', '午': '11-13', '未': '13-15',
             '申': '15-17', '酉': '17-19', '戌': '19-21', '亥': '21-23'}

WEEKDAY_CN = ('周一', '周二', '周三', '周四', '周五', '周六', '周日')

MAX_DAYS = 90          # 用户 §210 拍板：默认 30 天，最大 90 天
DEFAULT_DAYS = 30
DEFAULT_TOP_N = 10


def _pillar_text(sizhu):
    """四柱文本 '年 月 日 时'（缺柱留空，不臆造）。"""
    if not isinstance(sizhu, dict):
        return ''
    return ' '.join(str(sizhu.get(_k, '')) for _k in ('年柱', '月柱', '日柱', '时柱'))


def _compact_hour(sizhu, result, zhi, disabled):
    """单个时辰的紧凑记录（时间轴展示 + 交节核验用，不含大字段）。"""
    _ssl = result.get('shensha_list') or []
    _positive = [str(_s.get('name', '')) for _s in _ssl
                 if isinstance(_s, dict) and int(_s.get('score', 0) or 0) > 0]
    _negative = [str(_s.get('name', '')) for _s in _ssl
                 if isinstance(_s, dict) and int(_s.get('score', 0) or 0) < 0]
    return {
        '地支': zhi,
        '时辰': zhi + '时',
        '时段': HOUR_SPAN.get(zhi, ''),
        '时柱': str((sizhu or {}).get('时柱', '')),
        '年柱': str((sizhu or {}).get('年柱', '')),
        '月柱': str((sizhu or {}).get('月柱', '')),
        '日柱': str((sizhu or {}).get('日柱', '')),
        'score': int(result.get('score') or 0),
        'level': str(result.get('level') or ''),
        'veto': len(result.get('veto_reasons') or []),
        'disabled': bool(disabled),
        'shashi': bool(shashi_hour(result)),
        '凶': _negative[:3],
        '吉神': _positive[:3],
    }


def scan_day(d, event_type, owners=None, context=None):
    """单日 12 时辰实评择优（与主程序 _rescan_best_hour 同口径）。

    Args:
        d: datetime.date
        event_type: 事项名（UI_EVENTS 之一）
        owners: 主程序口径的事主 dict 列表（可空）
        context: dict，可含 house_type / shan_xiang（已含兼向）/ zao_xiang /
                 zao_wei / chuang_wei / zaozhu_mode / zeli_mode

    Returns:
        (best_sizhu, best_result, hour_records)
        hour_records 为 12 项（按子→亥时序），每项见 _compact_hour。

    说明：calculate_score 的 jian_xiang 不传——主程序扫日同样把兼向并入
    shan_xiang 字符串后传入，此处保持一致。
    """
    _ctx = context or {}
    _house_type = _ctx.get('house_type')
    _shan = _ctx.get('shan_xiang')
    _zao_xiang = _ctx.get('zao_xiang')
    _zao_wei = _ctx.get('zao_wei')
    _chuang_wei = _ctx.get('chuang_wei')
    _zaozhu_mode = _ctx.get('zaozhu_mode')
    _zeli_mode = _ctx.get('zeli_mode') or 'feixing'

    def _score_of(_sz):
        return calculate_score(_sz, event_type, owners, _house_type, _shan,
                               _zao_xiang, _zao_wei, _chuang_wei,
                               zaozhu_mode=_zaozhu_mode, zeli_mode=_zeli_mode)

    # 午时基准（与扫日一致：先算 12:00 作为初值代表）
    _base = calculate_sizhu(d, 12, 0)
    _base['year'] = d.year
    _base['month'] = d.month
    _base['day'] = d.day
    _base['date'] = d
    _base_ymd = {_k: _base.get(_k, '') for _k in
                 ('年柱', '月柱', '日柱', 'year_gan', 'year_zhi',
                  'month_gan', 'month_zhi', 'day_gan', 'day_zhi')}
    _init_result = _score_of(_base)

    # 时辰表分数 / 禁用时辰（仅嫁娶加权，与主程序 _ck0915 方案C 同口径）
    _ck_scores, _disabled_zhi = {}, set()
    try:
        from modules.推荐时柱 import resolve_recommended_hour
        _rec = resolve_recommended_hour(_base, event_type,
                                        owners if isinstance(owners, list) else [],
                                        _shan or '')
        for _h in ((_rec or {}).get('lucky_hours') or []):
            if isinstance(_h, dict):
                _ck_scores[str(_h.get('地支', ''))] = int(_h.get('分值', 0) or 0)
                if _h.get('禁用'):
                    _disabled_zhi.add(str(_h.get('地支', '')))
    except Exception as _re:  # 推荐时柱缺失/异常 → 不加权，与扫日一致
        print(f"[反推] resolve_recommended_hour 失败：{_re}")
    _ck_w = 1 if event_type in MARRIAGE_EVENTS else 0

    _best_sz, _best_r = _base, _init_result
    _records = []

    for _hh, _hz in HOURS:
        if _hz == '午':
            _hs, _hr = _base, _init_result
        else:
            try:
                _hs = calculate_sizhu(d, _hh, 0)
                _hs['year'] = d.year
                _hs['month'] = d.month
                _hs['day'] = d.day
                _hs['date'] = d
                # 交节防雷：仅当三柱与午时基准完全一致才复用基准字段；
                # 否则（跨节气时辰）保留该时辰自己的权威年月日柱。
                if (_hs.get('年柱') == _base_ymd['年柱']
                        and _hs.get('月柱') == _base_ymd['月柱']
                        and _hs.get('日柱') == _base_ymd['日柱']):
                    for _k, _v in _base_ymd.items():
                        _hs[_k] = _v
                _hr = _score_of(_hs)
            except Exception:
                # 与主程序 _rescan 一致：单个时辰计算失败即跳过该时辰，
                # 不影响整日择优（异常本身仍会由调用方在日志中暴露）
                continue
        _records.append(_compact_hour(_hs, _hr, _hz, _hz in _disabled_zhi))

        #  incumbent 的时柱地支 → 时辰表分数
        _cur_zhi = ''
        _sv = _best_sz.get('时柱', '') if isinstance(_best_sz, dict) else ''
        if isinstance(_sv, str) and len(_sv) >= 2:
            _cur_zhi = _sv[1]
        _fl, _fd = fenjin_preview_penalty(
            _shan or '', *_pillar_fields(_best_sz),
            _best_r.get('yi_list') or [], scoring_shensha(_best_r))
        _hfl, _hfd = fenjin_preview_penalty(
            _shan or '', *_pillar_fields(_hs),
            _hr.get('yi_list') or [], scoring_shensha(_hr))
        if hour_rank_key(
                disabled=(_hz in _disabled_zhi),
                veto_count=len(_hr.get('veto_reasons') or []),
                fenjin_level=_hfl, fenjin_deduct=_hfd,
                ck_score=_ck_scores.get(_hz, 0), ck_weight=_ck_w,
                score=int(_hr.get('score') or 0),
                shashi=shashi_hour(_hr),
                wuxing=int((_hr.get('score_details') or {}).get('五行评分') or 0)
        ) < hour_rank_key(
                disabled=(_cur_zhi in _disabled_zhi),
                veto_count=len(_best_r.get('veto_reasons') or []),
                fenjin_level=_fl, fenjin_deduct=_fd,
                ck_score=_ck_scores.get(_cur_zhi, 0), ck_weight=_ck_w,
                score=int(_best_r.get('score') or 0),
                shashi=shashi_hour(_best_r),
                wuxing=int((_best_r.get('score_details') or {}).get('五行评分') or 0)
        ):
            _best_sz, _best_r = _hs, _hr

    return _best_sz, _best_r, _records


def _pillar_fields(sizhu):
    """(年柱, 月柱, 日柱, 时柱) 四元组，供分金预览（缺柱以空串）。"""
    _s = sizhu if isinstance(sizhu, dict) else {}
    return (str(_s.get('年柱', '')), str(_s.get('月柱', '')),
            str(_s.get('日柱', '')), str(_s.get('时柱', '')),)


def _day_record(d, best_sz, best_r, hours, kind):
    """单日展示记录（反推榜 + 热力图 + 时间轴）。"""
    _level = str(best_r.get('level') or '')
    _sizhu_str = _pillar_text(best_sz)
    _gz = str(best_sz.get('时柱', '')) if isinstance(best_sz, dict) else ''
    try:
        _lunar = get_lunar_date(d)
        _lunar_str = f"{_lunar.get('month', '')}{_lunar.get('day', '')}"
    except Exception:
        _lunar_str = '-'
    # 001 §210 Commit 4：吉神名清单 + 评分器理由串（详情窗与择日贴消费，
    # 只做展示/透传，不参与任何分值计算）
    _pos = [str(_s.get('name', '')) for _s in (best_r.get('shensha_list') or [])
            if isinstance(_s, dict) and int(_s.get('score', 0) or 0) > 0]
    return {
        'date': d.strftime('%Y-%m-%d'),
        'weekday': WEEKDAY_CN[d.weekday()],
        'lunar': _lunar_str,
        'sizhu': _sizhu_str,
        'score': int(best_r.get('score') or 0),
        'level': _level,
        'kind': kind,
        'veto_reasons': [str(_v) for _v in (best_r.get('veto_reasons') or [])],
        'jishen_fit': jishen_fit(best_r),
        # 001 §210 微调：慎用原因列数据源（负分神煞 + 忌项），只做展示
        'deduct_sum': deduct_sum(best_r),
        'deduct_items': [{'name': _n, 'score': _v}
                         for _n, _v in deduct_items(best_r)],
        'ji_items': [str(_j) for _j in (best_r.get('ji_list') or [])],
        'jishen': '、'.join(_pos),
        'reason': str(best_r.get('reason') or ''),
        'best_hour': {
            '时柱': _gz,
            '时辰': (_gz[1:2] + '时') if len(_gz) >= 2 else '',
            '地支': _gz[1:2],
            '时段': HOUR_SPAN.get(_gz[1:2], ''),
        },
        'hours': hours,
    }


def search_top_n(days=DEFAULT_DAYS, event_type='', owners=None, start=None,
                 top_n=DEFAULT_TOP_N, context=None, progress=None, cancel=None):
    """反推 Top-N 吉日（后台线程可直接调用；本函数自身不触碰任何 GUI）。

    Args:
        days: 扫描天数，1..90（默认 30）
        event_type: 事项名，须为 modules.事项标准.UI_EVENTS 之一
        owners: 主程序口径的事主 dict 列表（可空）
        start: 起始日期（date），默认今天
        top_n: 榜单条数（默认 10）
        context: 见 scan_day
        progress: 回调 progress(done, total, date)，用于后台线程回主线程刷新
        cancel: 回调 bool，返回 True 则中止并返回已算部分（'cancelled': True）

    Returns:
        dict:
          meta: 扫描参数/耗时/计数
          all_days: 每日 {'date','kind','score','level'}（热力日历用，含否决日）
          days: 入榜前 top_n 条完整记录（吉日+慎用，慎用带 kind='慎用' 黄标）
          vetoed: 否决日 {'date','score','level','reasons'}
    """
    if event_type not in UI_EVENTS:
        raise ValueError(f'未知事项：{event_type!r}（须为 UI_EVENTS 之一）')
    _days = int(days)
    if not 1 <= _days <= MAX_DAYS:
        raise ValueError(f'扫描天数须在 1~{MAX_DAYS} 之间，收到 {days!r}')
    _top_n = int(top_n)
    if _top_n < 1:
        raise ValueError(f'Top N 须 ≥ 1，收到 {top_n!r}')
    _start = start or date.today()
    if not isinstance(_start, date):
        raise ValueError(f'start 须为 datetime.date，收到 {type(start).__name__}')

    _t0 = time.time()
    _owners = owners if isinstance(owners, list) else []
    _cands = []      # (raw_result, record)
    _vetoed = []
    _all = []

    for _i in range(_days):
        if cancel is not None and cancel():
            break
        _d = _start + timedelta(days=_i)
        _best_sz, _best_r, _hours = scan_day(_d, event_type, _owners, context)
        _kind = classify_day(_best_r, event_type)
        _rec = _day_record(_d, _best_sz, _best_r, _hours, _kind)
        _all.append({'date': _rec['date'], 'kind': _kind,
                     'score': _rec['score'], 'level': _rec['level'],
                     'jishen_fit': _rec['jishen_fit'],
                     'deduct_sum': _rec['deduct_sum'],
                     # 热力格悬浮提示用（与 Top-N 原因列同一数据源）
                     'deduct_items': _rec['deduct_items'],
                     'ji_items': _rec['ji_items'],
                     'veto_reasons': _rec['veto_reasons']})
        if _kind == '否决':
            _vetoed.append({'date': _rec['date'], 'weekday': _rec['weekday'],
                            'score': _rec['score'], 'level': _rec['level'],
                            'reasons': _rec['veto_reasons']})
        else:
            _cands.append((_best_r, _rec))
        if progress is not None:
            progress(_i + 1, _days, _d)

    _cands.sort(key=lambda _p: rank_day(_p[0], event_type))
    _top = [dict(_p[1]) for _p in _cands[:_top_n]]

    _end = _start + timedelta(days=max(0, len(_all) - 1))
    return {
        'meta': {
            'start': _start.strftime('%Y-%m-%d'),
            'end': _end.strftime('%Y-%m-%d'),
            'days': len(_all),
            'event_type': event_type,
            'owners': len(_owners),
            'top_n': _top_n,
            'scanned': len(_all),
            'candidates': len(_cands),
            'vetoed': len(_vetoed),
            'elapsed': round(time.time() - _t0, 2),
            'cancelled': len(_all) < _days,
            'engine': 'modules/反推引擎.py',
            'policy': '单事项 Top-N（P1）；排序=收录层→否决数→吉神契合度→总分',
        },
        'all_days': _all,
        'days': _top,
        'vetoed': _vetoed,
    }
