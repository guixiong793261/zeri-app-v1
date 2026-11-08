# -*- coding: utf-8 -*-
"""太阳太阴到山到向 · 结构透传 / 时辰门控计分 / 不救否决 回归断言（001 §222-§223）。

覆盖：
  T1 白天太阳到山 → 结构完整、sun_effective=True、effective_text 含"已生效"，
     且日月档仅登记太阳 +25（太阴到向被白天门控为 0）；
  T2 同一日夜间时辰 → 太阳到山不登记、太阴到向 +15 生效，
     effective_text 明确写"太阳吉力不发挥"（展示与计分自洽）；
  T3 岁破/三煞等 HARD_VETO 日：即使太阳到山并登记 +25，总分必须为 0，
     不得被日月加分"救活"；
  T4 未提供山向（嫁娶等）→ 不报错且不产生到山到向标记；
  T5 时支缺失 → 昼夜判定回落（白天 False），日月两边均不计分入口。

退出码：0 全通过；1 有失败。
"""

import sys
from datetime import date

sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')

from modules.评分器 import calculate_score
from modules.四柱计算器 import calculate_sizhu
from modules.shensha.神煞基类 import DAY_HOUR_ZHI, get_hour_zhi, is_daytime_hour

FAILS = []

_SM_NAMES = ('太阳到山', '太阳到向', '太阴到山', '太阴到向')


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


def _sm_items(r):
    return [{'name': s.get('name'), 'score': int(s.get('score') or 0)}
            for s in (r.get('shensha_list') or [])
            if isinstance(s, dict) and s.get('name') in _SM_NAMES]


def _sm_bonus(r):
    return sum(_i['score'] for _i in _sm_items(r))


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
    # §223 时辰门控：白天只认太阳，太阴（本日在卯=向首）不得计分
    _items = _sm_items(r)
    _names = [i['name'] for i in _items]
    _check('太阳到山' in _names, '白天已生效 → 太阳到山登记（实际 %s）' % _names)
    _check('太阴到向' not in _names,
           '太阴到向被白天门控 → 不登记（实际 %s）' % _names)
    _check(_sm_bonus(r) == 25,
           '日月档合计=+25（仅太阳到山，实际 %+d）' % _sm_bonus(r))
    _check(int(det.get('score_applied') or 0) == 25,
           'score_applied=+25（实际 %s）' % det.get('score_applied'))


def score_details_has(r):
    sd = r.get('score_details') or {}
    return isinstance(sd.get('太阳太阴明细'), dict) and bool(sd.get('太阳太阴明细'))


def t2_night_sun_not_effective():
    """同日 23 时（子时，夜间）→ 太阳即使到山也不计分，太阴到向 +15 生效。"""
    d = date(2015, 10, 1)
    r = _score(d, 23, 0)
    det = ((r.get('sun_moon_info') or {}).get('taiyang_taiyin_detail') or {})
    print('T2 夜间太阳到山')
    _check(det.get('sun_to_mountain') is True, '仍判定为太阳到坐山')
    _check(det.get('sun_effective') is False, 'sun_effective=False（子时夜间）')
    _check('太阳吉力不发挥' in str(det.get('effective_text')),
           '夜间明确写"太阳吉力不发挥"（实际：%s）' % det.get('effective_text'))
    # §223 时辰门控：夜间太阳到山不计分，太阴到向（卯=向首）+15 生效
    _items = _sm_items(r)
    _names = [i['name'] for i in _items]
    _check('太阳到山' not in _names,
           '夜间太阳到山不登记（实际 %s）' % _names)
    _check('太阴到向' in _names, '夜间太阴到向登记（实际 %s）' % _names)
    _check(_sm_bonus(r) == 15,
           '日月档合计=+15（仅太阴到向，实际 %+d）' % _sm_bonus(r))
    _check(int(det.get('score_applied') or 0) == 15,
           'score_applied=+15（实际 %s）' % det.get('score_applied'))


def t3_veto_not_rescued():
    """酉山卯向在乙未年犯年三煞（申酉戌）→ HARD_VETO，总分必须 0。"""
    d = date(2015, 10, 1)
    r = _score(d, 12, 0)
    det = ((r.get('sun_moon_info') or {}).get('taiyang_taiyin_detail') or {})
    print('T3 否决不被日月加分救活')
    _check(bool(r.get('veto_reasons')), '存在 veto_reasons（否决生效）')
    _check(int(r.get('score') or 0) == 0,
           '总分=0（实际 %s）' % r.get('score'))
    _check(det.get('sun_to_mountain') is True, '该日仍判定太阳到坐山')
    _check(_sm_items(r) != [], '神煞档仍登记了生效的日月项')
    _check(_sm_bonus(r) == 25,
           '门控后仅太阳到山 +25（实际 %+d）' % _sm_bonus(r))
    # 核心断言：不论日月档登记多少分，否决日总分恒为 0（不得被"救活"）
    _check(int(r.get('score') or 0) == 0,
           '日月档合计 %+d 分，总分仍为 0' % _sm_bonus(r))


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


def t5_hour_gate_boundary():
    """时支缺失/边界时辰：门控单一事实源判定正确（不臆造白天）。"""
    print('T5 时辰门控边界')
    _check(get_hour_zhi({}) == '', '无时支/时柱 → 返回空串')
    _check(get_hour_zhi({'时柱': '甲子'}) == '子', '时柱回退取第二字=子')
    _check(is_daytime_hour({'时支': '卯'}) is True, '卯时判为白天')
    _check(is_daytime_hour({'时支': '申'}) is True, '申时判为白天')
    _check(is_daytime_hour({'时支': '酉'}) is False, '酉时判为夜间')
    _check(is_daytime_hour({'时支': '寅'}) is False, '寅时判为夜间')
    _check(is_daytime_hour({}) is False, '时支缺失不臆造白天')
    _check(set(DAY_HOUR_ZHI) == {'卯', '辰', '巳', '午', '未', '申'},
           '白天分界为卯—申（实际 %s）' % (DAY_HOUR_ZHI,))


if __name__ == '__main__':
    t1_daytime_sun_to_mountain()
    t2_night_sun_not_effective()
    t3_veto_not_rescued()
    t4_no_shan_no_crash()
    t5_hour_gate_boundary()
    print('\n结果：%d 失败' % len(FAILS))
    for f in FAILS:
        print('  - ' + f)
    sys.exit(0 if not FAILS else 1)
