# -*- coding: utf-8 -*-
"""001 §236 嫁娶冲夫妻宫（B1/B2/B3/B4 + A 档提示）回归验证。

判据来源：2026-11-08 用户拍板
- B1 月支（提纲）冲事主日支 → 一票否决
- B2 时支冲事主日支 → 只禁用该时辰，不否决整日
- B3 相主得分并入嫁娶总分
- B4 年命伏吟 → 一票否决（2026-11-13 用户拍板修订；原 -15 不否决）；事主日支伏吟 -15；日课内部伏吟维持 0
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
from modules.shensha.嫁娶神煞扩展 import MarriageShenShaCheckerExt

FAILS = []


def check(cond, label, detail=''):
    if cond:
        print('  PASS  ' + label)
    else:
        print('  FAIL  ' + label + ('  | ' + str(detail) if detail != '' else ''))
        FAILS.append(label)


BRIDE = {'name': '新娘', 'role': '新娘', '性别': '女',
         'sizhu': '己卯 丁卯 丁亥 癸卯', 'xishen': '水、金', 'yongshen': '水'}
GROOM = {'name': '新郎', 'role': '新郎', '性别': '男',
         'sizhu': '戊寅 壬戌 癸巳 壬子', 'xishen': '金、水', 'yongshen': '金'}


def _score(y, m, d, h=12, owners=None, ev='嫁娶'):
    sz = calculate_sizhu((y, m, d), h, 0, longitude=120)
    return calculate_score(sz, ev, owners=[dict(o) for o in (owners or [BRIDE, GROOM])],
                           zeli_mode='pure')


def test_b1_month_chong():
    print('\n[B1] 月支（提纲）冲事主日支 → 一票否决')
    r = _score(2026, 5, 12, 12)
    vr = '；'.join(str(v) for v in (r.get('veto_reasons') or []))
    check(int(r.get('score') or 0) == 0, '05-12 丙戌日（巳月）分归零', r.get('score'))
    check('月支' in vr and '提纲' in vr, '否决原因写明月支提纲冲夫妻宫', vr)
    check('新娘' in vr and '亥' in vr, '否决原因点名新娘亥', vr)

    # 12-07 当日大雪交节：亥月（0时）才构成提纲冲，12时已进气子月，故取 0 时。
    r2 = _score(2026, 12, 7, 0)
    vr2 = '；'.join(str(v) for v in (r2.get('veto_reasons') or []))
    check(int(r2.get('score') or 0) == 0, '12-07 乙卯日（亥月）分归零', r2.get('score'))
    check('新郎' in vr2 and '月支' in vr2, '否决原因点名新郎且写明月支', vr2)


def test_b1_reverse():
    print('\n[B1-反向] 非冲月日不被误伤')
    r = _score(2026, 3, 13, 0)
    vr = r.get('veto_reasons') or []
    check(not vr, '03-13 丙戌日（卯月）无否决', vr)
    check(int(r.get('score') or 0) > 0, '分数正常', r.get('score'))


def test_b2_hour_disable():
    print('\n[B2] 时支冲事主日支 → 仅禁用该时辰')
    sizhu = {'year_gan': '丙', 'year_zhi': '午', 'month_gan': '癸', 'month_zhi': '巳',
             'day_gan': '丙', 'day_zhi': '戌', 'hour_gan': '戊', 'hour_zhi': '子'}
    ck = MarriageShenShaCheckerExt(bride_day_zhi='亥', groom_day_zhi='巳')
    hours = {h['地支']: h for h in ck.get_lucky_hours(sizhu)}
    check(hours['巳']['禁用'] is True, '巳时（冲新娘亥）禁用', hours['巳']['说明'])
    check(any('冲新娘夫妻宫' in s for s in hours['巳']['说明']), '禁用原因写明冲新娘夫妻宫')
    check(hours['亥']['禁用'] is True, '亥时（冲新郎巳）禁用', hours['亥']['说明'])
    check(any('冲新郎夫妻宫' in s for s in hours['亥']['说明']), '禁用原因写明冲新郎夫妻宫')
    check(hours['子']['禁用'] is False, '子时未被误禁（反向断言）', hours['子']['说明'])

    ck2 = MarriageShenShaCheckerExt()
    h2 = {h['地支']: h for h in ck2.get_lucky_hours(sizhu)}
    check(h2['巳']['禁用'] is False, '未提供日支时不触发冲夫妻宫禁时（反向断言）')


def test_b4_fuyin():
    print('\n[B4] 年命伏吟 → 一票否决；事主日支伏吟 → -15（不否决）')
    r = _score(2026, 2, 22, 4)
    sd = r.get('score_details') or {}
    det = [str(x) for x in (sd.get('相主详情') or [])]
    vr = '；'.join(str(v) for v in (r.get('veto_reasons') or []))
    check(any('年命伏吟' in x and '一票否决' in x for x in det),
          '02-22 女年命卯伏吟 → 硬性门槛', det)
    check('年命伏吟' in vr and '新娘' in vr, '否决原因写明新娘年命伏吟', vr)
    check(int(r.get('score') or 0) == 0, '伏吟日总分归零', r.get('score'))
    check('凶' in str(r.get('level') or ''), '伏吟日等级为凶', r.get('level'))

    # 反向：非嫁娶通道 strict_fuyin=False，年命伏吟不得否决（避免全事项漂移）
    own_y = [{'name': '事主', 'role': '福主', 'sizhu': '己卯 丁卯 丁亥 癸卯'}]
    r_y = _score(2026, 2, 22, 4, own_y, ev='开业')
    vr_y = r_y.get('veto_reasons') or []
    check(not any('年命伏吟' in str(v) for v in vr_y),
          '开业通道年命伏吟不否决（反向断言）', vr_y)

    own = [{'name': '事主', 'role': '新娘', 'sizhu': '甲子 丙寅 庚戌 丁亥'}]
    r_m = _score(2026, 3, 13, 0, own)
    det_m = [str(x) for x in ((r_m.get('score_details') or {}).get('相主详情') or [])]
    check(any('夫妻宫伏吟' in x and '-15' in x for x in det_m),
          '嫁娶：事主日支伏吟仍 -15（不在本次升级范围）', det_m)
    check(int(r_m.get('score') or 0) > 0, '夫妻宫伏吟不否决（反向断言）', r_m.get('score'))

    r_g = _score(2026, 3, 13, 0, own, ev='开业')
    det_g = [str(x) for x in ((r_g.get('score_details') or {}).get('相主详情') or [])]
    check(any('伏吟' in x and '+3' in x for x in det_g),
          '通用通道维持 +3（反向断言，避免全事项漂移）', det_g)


def test_a_notes():
    print('\n[A] 相主核验提示（纯展示）')
    sd = (_score(2026, 5, 12, 12).get('score_details') or {})
    notes = [str(x) for x in (sd.get('相主核验提示') or [])]
    check(any('月支' in x and '夫妻宫' in x for x in notes), '否决日含月支冲夫妻宫提示', notes)

    sd2 = (_score(2026, 3, 13, 10).get('score_details') or {})
    notes2 = [str(x) for x in (sd2.get('相主核验提示') or [])]
    check(any('时支' in x for x in notes2), '巳时（冲女亥）含时支提示', notes2)

    sd3 = (_score(2026, 2, 22, 4).get('score_details') or {})
    notes3 = [str(x) for x in (sd3.get('相主核验提示') or [])]
    check(any('年命伏吟' in x for x in notes3), '伏吟日含年命伏吟提示', notes3)


def test_source_anchors():
    print('\n[H] 源码锚点防回退')
    p = os.path.join(_ROOT, 'modules', '评分器.py')
    with open(p, 'r', encoding='utf-8') as f:
        s = f.read()
    check('chong_month = liuchong_map.get(month_zhi' in s, '评分器：月支冲查表')
    check('（提纲冲夫妻宫，婚嫁大忌）' in s, '评分器：月支冲否决文案')
    check('strict_fuyin=True' in s, '评分器：嫁娶从严伏吟入参')
    check('+ sun_moon_score + xiangzhu_score)' in s, '评分器：相主并入嫁娶总分')
    p2 = os.path.join(_ROOT, 'modules', 'shensha', '嫁娶神煞扩展.py')
    with open(p2, 'r', encoding='utf-8') as f:
        s2 = f.read()
    check('bride_day_zhi' in s2 and '冲新娘夫妻宫' in s2, '嫁娶扩展：冲新娘夫妻宫禁时')
    check('groom_day_zhi' in s2 and '冲新郎夫妻宫' in s2, '嫁娶扩展：冲新郎夫妻宫禁时')


def main():
    print('=' * 74)
    print('001 §236 嫁娶冲夫妻宫（B1/B2/B3/B4 + A 档）回归')
    print('=' * 74)
    test_b1_month_chong()
    test_b1_reverse()
    test_b2_hour_disable()
    test_b4_fuyin()
    test_a_notes()
    test_source_anchors()
    print('\n' + '=' * 74)
    if FAILS:
        print('FAIL %d 项：' % len(FAILS))
        for f in FAILS:
            print('  -', f)
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
