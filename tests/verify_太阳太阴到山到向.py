# -*- coding: utf-8 -*-
"""太阳太阴到山到向 · 结构透传 / 时辰生效 / 不救否决 回归断言（001 §222）。

覆盖：
  T1 白天太阳到山 → taiyang_taiyin_detail 结构完整、sun_effective=True、
     effective_text 含"已生效"；
  T2 同一日夜间时辰 → sun_effective=False、effective_text 含"未生效"；
  T3 岁破/三煞等 HARD_VETO 日：即使太阳到山并登记了 +25，总分必须为 0，
     不得被日月加分"救活"；
  T4 未提供山向（嫁娶等）→ 不报错且不产生到山到向标记。

退出码：0 全通过；1 有失败。
"""

import sys
from datetime import date

sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')

from modules.评分器 import calculate_score
from modules.四柱计算器 import calculate_sizhu

FAILS = []


def _check(cond, msg):
    print(('  PASS ' if cond else '  FAIL ') + msg)
    if not cond:
        FAILS.append(msg)


def _score(d, hour, minute, event='修造', shan='酉山卯向'):
    sz = calculate_sizhu(d, hour, minute)
    sz['year'], sz['month'], sz['day'] = d.year, d.month, d.day
    sz['date'] = d
    return calculate_score(sz, event, [], '阳宅', shan, None, None, None,
                           zeli_mode='pure')


def t1_daytime_sun_to_mountain():
    """2015-10-01 太阳在酉方，取酉山卯向 → 太阳到坐山，午时白天应生效。"""
    d = date(2015, 10, 1)
    r = _score(d, 12, 0)
    smi = r.get('sun_moon_info') or {}
    det = smi.get('taiyang_taiyin_detail') or {}
    print('T1 白天太阳到山')
    _check(bool(det), 'taiyang_taiyin_detail 存在')
    _check(det.get('sun_position') == '酉',
           '太阳宫位=酉（实际 %s）' % det.get('sun_position'))
    _check(det.get('sun_to_mountain') is True, 'sun_to_mountain=True')
    _check(det.get('sun_effective') is True, 'sun_effective=True（午时白天）')
    _check('太阳到坐山' in str(det.get('sun_text')), 'sun_text 含"太阳到坐山"')
    _check('已生效' in str(det.get('effective_text')),
           'effective_text 含"已生效"（实际：%s）' % det.get('effective_text'))
    _check(score_details_has(r), "score_details['太阳太阴明细'] 已透传")


def score_details_has(r):
    sd = r.get('score_details') or {}
    return isinstance(sd.get('太阳太阴明细'), dict) and bool(sd.get('太阳太阴明细'))


def t2_night_sun_not_effective():
    """同日 23 时（子时，夜间）→ 太阳即使到山也不生效。"""
    d = date(2015, 10, 1)
    r = _score(d, 23, 0)
    det = ((r.get('sun_moon_info') or {}).get('taiyang_taiyin_detail') or {})
    print('T2 夜间太阳到山')
    _check(det.get('sun_to_mountain') is True, '仍判定为太阳到坐山')
    _check(det.get('sun_effective') is False, 'sun_effective=False（子时夜间）')
    _check('太阳吉力不发挥' in str(det.get('effective_text')),
           '夜间明确写"太阳吉力不发挥"（实际：%s）' % det.get('effective_text'))


def t3_veto_not_rescued():
    """酉山卯向在乙未年犯年三煞（申酉戌）→ HARD_VETO，总分必须 0。"""
    d = date(2015, 10, 1)
    r = _score(d, 12, 0)
    det = ((r.get('sun_moon_info') or {}).get('taiyang_taiyin_detail') or {})
    names = [s.get('name') for s in (r.get('shensha_list') or [])
             if isinstance(s, dict)]
    _sm_names = ('太阳到山', '太阳到向', '太阴到山', '太阴到向')
    bonus = sum(int(s.get('score') or 0) for s in (r.get('shensha_list') or [])
                if isinstance(s, dict) and s.get('name') in _sm_names)
    print('T3 否决不被日月加分救活')
    _check(bool(r.get('veto_reasons')), '存在 veto_reasons（否决生效）')
    _check(int(r.get('score') or 0) == 0,
           '总分=0（实际 %s）' % r.get('score'))
    _check(det.get('sun_to_mountain') is True, '该日仍判定太阳到坐山')
    _check([n for n in names if n in _sm_names] != [], '神煞档仍登记了日月项')
    # 核心断言：不论日月档登记多少分，否决日总分恒为 0（不得被"救活"）
    _check(int(r.get('score') or 0) == 0,
           '日月档合计 %+d 分，总分仍为 0' % bonus)


def t4_no_shan_no_crash():
    """嫁娶未提供山向：不产生到山到向标记，也不报错。"""
    d = date(2015, 10, 1)
    sz = calculate_sizhu(d, 12, 0)
    sz['year'], sz['month'], sz['day'] = d.year, d.month, d.day
    sz['date'] = d
    r = calculate_score(sz, '嫁娶', [], '阳宅', None, None, None, None,
                        zeli_mode='pure')
    det = ((r.get('sun_moon_info') or {}).get('taiyang_taiyin_detail') or {})
    print('T4 无山向')
    _check(isinstance(r, dict) and 'score' in r, '无山向评分返回正常')
    _check(not det.get('sun_to_mountain') and not det.get('moon_to_mountain'),
           '无山向不产生到山标记')


if __name__ == '__main__':
    t1_daytime_sun_to_mountain()
    t2_night_sun_not_effective()
    t3_veto_not_rescued()
    t4_no_shan_no_crash()
    print('\n结果：%d 失败' % len(FAILS))
    for f in FAILS:
        print('  - ' + f)
    sys.exit(0 if not FAILS else 1)
