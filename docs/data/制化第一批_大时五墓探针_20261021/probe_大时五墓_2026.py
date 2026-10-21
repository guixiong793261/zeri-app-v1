# -*- coding: utf-8 -*-
"""
制化第一批·大时/五墓 2026 全年影响面探针（只读，不改任何代码）
================================================================
任务锚：001 §155 用户拍板「补测探针先跑：输出 2026 全年大时、五墓的影响面快照
（豁免前/后）」。
矩阵锚：docs/制化矩阵_协纪明文十条_20261021.md #9（大时丑未支）、#15（五墓午子支）。
判据冻结（与制化引擎一致）：
  - 大时豁免支：月支∈{丑,未} 且 天德+月德同时并临（「二德并」最严判读）
    → 止忌军事；军事经映射表=空集 → 当前事项全免（附警示）。
  - 五墓豁免支：月支∈{午,子} 且 月德并（仅月德，不含月德合/天德）→ 不忌。
  - 大时子午卯酉相抵支、寅申巳亥除日官日支：不落地（轻重层/建除阻塞）。
方法：monkey-patch ShenShaChecker._is_dashi/_is_wumu（运行时模拟，进程内，
不落盘改码），patch 仅影响发射行谓词（全库消费面已核查：5+3 条发射链，
评分器不直接消费谓词）。同日双煞 firing 时分三次模拟拆分归因。
退出码：0=完成 1=异常。
"""
import io
import os
import sys
import json
import datetime
import hashlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
from modules.shensha.神煞基类 import ShenShaChecker, is_dashi_by_zhi, is_wumu_by_pillar

EVENTS = ['嫁娶', '修造', '动土', '拆舍', '入宅', '开业', '出行', '安床',
          '作灶', '安葬', '入学', '求医', '签约', '通用', '祭祀']
YEAR = 2026
HOUR = 12

_ORIG_DASHI = ShenShaChecker._is_dashi
_ORIG_WUMU = ShenShaChecker._is_wumu


def _erde_bing(sizhu):
    """二德并：天德+月德同时并临（基类单点谓词，2026 全年同源性已实证）。"""
    return (ShenShaChecker._is_tiande(None, sizhu)
            and ShenShaChecker._is_yuede(None, sizhu))


def _wumu_exempt_cond(sizhu):
    """五墓豁免条件：午/子月 + 月德并。"""
    if sizhu.get('month_zhi') not in ('午', '子'):
        return False
    return ShenShaChecker._is_yuede(None, sizhu)


def _make_patched(patch_dashi, patch_wumu):
    def _dashi(self, sizhu):
        if not _ORIG_DASHI(self, sizhu):
            return False
        if patch_dashi and sizhu.get('month_zhi') in ('丑', '未') and _erde_bing(sizhu):
            return False
        return True

    def _wumu(self, sizhu):
        if not _ORIG_WUMU(self, sizhu):
            return False
        if patch_wumu and _wumu_exempt_cond(sizhu):
            return False
        return True

    return _dashi, _wumu


def _apply(patch_dashi, patch_wumu):
    pd, pw = _make_patched(patch_dashi, patch_wumu)
    ShenShaChecker._is_dashi = pd
    ShenShaChecker._is_wumu = pw


def _restore():
    ShenShaChecker._is_dashi = _ORIG_DASHI
    ShenShaChecker._is_wumu = _ORIG_WUMU


def _shensha_entries(result, name):
    return [s for s in result.get('shensha_list', []) if s.get('name') == name]


def main():
    _restore()
    stat = {
        '大时': {'cond_days': 0, 'fire_days': 0, 'deduct_event_days': 0,
                 'exempt_event_days': 0, 'score_delta_total': 0,
                 'by_event': {e: {'deduct_days': 0, 'exempt_days': 0, 'delta': 0} for e in EVENTS}},
        '五墓': {'cond_days': 0, 'fire_days': 0, 'deduct_event_days': 0,
                 'exempt_event_days': 0, 'score_delta_total': 0,
                 'by_event': {e: {'deduct_days': 0, 'exempt_days': 0, 'delta': 0} for e in EVENTS}},
        '同日双煞': {'deduct_event_days': 0, 'exempt_event_days': 0, 'score_delta_total': 0},
    }
    cond_day_list = {'大时丑未二德并': [], '五墓午子月德并': []}
    sentinel = None

    d = datetime.date(YEAR, 1, 1)
    while d <= datetime.date(YEAR, 12, 31):
        sz = calculate_sizhu(d, HOUR, 0)
        mz, dz = sz.get('month_zhi', ''), sz.get('day_zhi', '')
        day_gz = sz.get('day_gan', '') + dz
        fire_dashi = is_dashi_by_zhi(mz, dz)
        fire_wumu = is_wumu_by_pillar(mz, day_gz)
        cond_dashi = mz in ('丑', '未') and _erde_bing(sz)
        cond_wumu = _wumu_exempt_cond(sz)
        if cond_dashi:
            cond_day_list['大时丑未二德并'].append(str(d))
        if cond_wumu:
            cond_day_list['五墓午子月德并'].append(str(d))

        if (fire_dashi or fire_wumu) and d == datetime.date(2026, 11, 4):
            pass  # 哨兵日单独全量跑（下方）

        if fire_dashi or fire_wumu:
            for ev in EVENTS:
                _restore()
                r1 = calculate_score(sz, ev)
                e1 = _shensha_entries(r1, '大时')
                w1 = _shensha_entries(r1, '五墓')
                ded_dashi = any(s.get('score', 0) != 0 for s in e1)
                ded_wumu = any(s.get('score', 0) != 0 for s in w1)

                # 单豁免大时
                if fire_dashi:
                    _apply(True, False)
                    r2d = calculate_score(sz, ev)
                    _restore()
                    delta_d = r1['score'] - r2d['score']
                else:
                    delta_d = 0
                # 单豁免五墓
                if fire_wumu:
                    _apply(False, True)
                    r2w = calculate_score(sz, ev)
                    _restore()
                    delta_w = r1['score'] - r2w['score']
                else:
                    delta_w = 0
                # 双豁免（校验合成）
                if fire_dashi and fire_wumu:
                    _apply(True, True)
                    r2b = calculate_score(sz, ev)
                    _restore()
                    stat['同日双煞']['score_delta_total'] += r1['score'] - r2b['score']
                    if ded_dashi or ded_wumu:
                        stat['同日双煞']['deduct_event_days'] += 1
                        if (cond_dashi and ded_dashi) or (cond_wumu and ded_wumu):
                            stat['同日双煞']['exempt_event_days'] += 1

                if ded_dashi:
                    stat['大时']['deduct_event_days'] += 1
                    stat['大时']['by_event'][ev]['deduct_days'] += 1
                    if cond_dashi:
                        stat['大时']['exempt_event_days'] += 1
                        stat['大时']['by_event'][ev]['exempt_days'] += 1
                        stat['大时']['score_delta_total'] += delta_d
                        stat['大时']['by_event'][ev]['delta'] += delta_d
                if ded_wumu:
                    stat['五墓']['deduct_event_days'] += 1
                    stat['五墓']['by_event'][ev]['deduct_days'] += 1
                    if cond_wumu:
                        stat['五墓']['exempt_event_days'] += 1
                        stat['五墓']['by_event'][ev]['exempt_days'] += 1
                        stat['五墓']['score_delta_total'] += delta_w
                        stat['五墓']['by_event'][ev]['delta'] += delta_w

        if fire_dashi:
            stat['大时']['fire_days'] += 1
        if fire_wumu:
            stat['五墓']['fire_days'] += 1

        # 哨兵：2026-11-04 入宅
        if d == datetime.date(2026, 11, 4):
            _restore()
            r1s = calculate_score(sz, '入宅')
            _apply(True, True)
            r2s = calculate_score(sz, '入宅')
            _restore()
            sentinel = {
                'date': str(d), 'event': '入宅',
                'dashi_fired': bool(is_dashi_by_zhi(mz, dz)),
                'wumu_fired': bool(is_wumu_by_pillar(mz, day_gz)),
                'cond_dashi': bool(cond_dashi), 'cond_wumu': bool(cond_wumu),
                'score_before': r1s['score'], 'level_before': r1s.get('level'),
                'score_after': r2s['score'], 'level_after': r2s.get('level'),
            }
        d += datetime.timedelta(days=1)

    out = {
        'meta': {
            'title': '制化第一批·大时/五墓 2026 影响面探针',
            'year': YEAR, 'hour': HOUR, 'events': EVENTS,
            'method': 'monkey-patch ShenShaChecker._is_dashi/_is_wumu（进程内模拟，未改码）',
            'dashi_exempt_rule': '月支∈{丑,未} 且 天德+月德同时并临 → 止忌军事(映射空集)=全免',
            'wumu_exempt_rule': '月支∈{午,子} 且 月德并(仅月德) → 不忌',
            'generated_at': datetime.datetime.now().isoformat(timespec='seconds'),
        },
        'stat': stat,
        'cond_day_lists': {k: {'days': v, 'count': len(v)} for k, v in cond_day_list.items()},
        'sentinel_20261104_ruzhai': sentinel,
    }
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '大时五墓_2026_影响面.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print('=== 大时 ===')
    print('  豁免条件日（丑未月二德并）：%d 天' % len(cond_day_list['大时丑未二德并']))
    print('  全年 firing 天次：%d' % stat['大时']['fire_days'])
    print('  实扣 day×event：%d，其中豁免条件成立：%d' % (
        stat['大时']['deduct_event_days'], stat['大时']['exempt_event_days']))
    print('  豁免总分影响（扣分减少合计）：%d' % stat['大时']['score_delta_total'])
    for ev, s in stat['大时']['by_event'].items():
        if s['deduct_days']:
            print('    %s: 扣%d天 豁%d天 Δ%d' % (ev, s['deduct_days'], s['exempt_days'], s['delta']))
    print('=== 五墓 ===')
    print('  豁免条件日（午子月月德并）：%d 天' % len(cond_day_list['五墓午子月德并']))
    print('  全年 firing 天次：%d' % stat['五墓']['fire_days'])
    print('  实扣 day×event：%d，其中豁免条件成立：%d' % (
        stat['五墓']['deduct_event_days'], stat['五墓']['exempt_event_days']))
    print('  豁免总分影响（扣分减少合计）：%d' % stat['五墓']['score_delta_total'])
    for ev, s in stat['五墓']['by_event'].items():
        if s['deduct_days']:
            print('    %s: 扣%d天 豁%d天 Δ%d' % (ev, s['deduct_days'], s['exempt_days'], s['delta']))
    print('=== 同日双煞 ===')
    print('  实扣 day×event：%d，豁免条件成立：%d，Δ%d' % (
        stat['同日双煞']['deduct_event_days'], stat['同日双煞']['exempt_event_days'],
        stat['同日双煞']['score_delta_total']))
    print('=== 哨兵 2026-11-04 入宅 ===')
    print(' ', json.dumps(sentinel, ensure_ascii=False))
    print('JSON ->', out_path)


if __name__ == '__main__':
    try:
        main()
        raise SystemExit(0)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print('PROBE ERROR:', exc)
        raise SystemExit(1)
