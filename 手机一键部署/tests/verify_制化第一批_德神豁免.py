# -*- coding: utf-8 -*-
"""
制化第一批·德神豁免 verify（2026-10-21，001 §155）
====================================================
矩阵锚：docs/制化矩阵_协纪明文十条_20261021.md #9/#13/#15。
覆盖面：
  M1 德神封闭集与禁并排除对（矩阵 §3.1/§3.3）：六神集、厌对五德集=六神−天愿、
     大时二德集=天德+月德、天恩不在集内、allow 越界拦截；
  M2 止忌子集映射表（配置化判据冻结）：军事=∅/缓刑=∅/疗病=求医/破屋坏垣=拆舍；
     缺项保守不豁免（返回 None）；
  M3 谓词同源性：2026 全年 15 事项 checker × 6 德神谓词 vs 基类单点零分歧
     （立项书 §1.1 红线延续断言）；
  M4 引擎行为（合成四柱）：五墓午/子+月德→True、巳月→False、午月无月德→False；
     厌对任一五德→True；大时丑/未月二德并→(True, 军事警示文案)、单德→False、
     寅月→False；
  M5 行为锚定（真实日）：厌对豁免日/非豁免日 checker 发射；大时/五墓 2026
     firing 日仍 -12 且无豁免键；2020–2035 扫描大时真实豁免日（未命中记
     SKIP 不判败——2026 探针已证全年零重合）；
  M6 哨兵：2026-11-04 入宅 216/上吉、无豁免键；豁免键未注册分值（fallback 0
     by design，防误配 -12）。（哨兵分史：§159 冻 224；§162 真值 214 本脚本
     漏更属历史漂移；§172 P0 大清理岁刑-12置0 → 226，2026-10-24 统一收敛；
     §190 C3 不将日×入宅停发（嫁娶专用误挂 +10 清理）→ 216，等级不变。）

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
    from modules.shensha.神煞基类 import ShenShaChecker
    from modules.shensha.制化引擎 import (
        DE_GODS_ALL, DE_GODS_WUDE, DE_GODS_ERDE, FORBIDDEN_PAIRS,
        ZHIJI_EVENT_MAPPING, map_zhiji_events, get_de_gods,
        eval_wumu_exempt, eval_yandui_exempt, eval_dashi_chouwei_exempt,
        MILITARY_EMPTY_NOTE)
    from modules.事项标准 import shensha_score

    print('== M1 封闭集/禁并排除对 ==')
    check('DE_GODS_ALL=六神封闭集',
          set(DE_GODS_ALL) == {'天德', '月德', '天德合', '月德合', '天赦', '天愿'})
    check('厌对五德集=六神−天愿（禁并排除）',
          set(DE_GODS_WUDE) == set(DE_GODS_ALL) - {'天愿'})
    check('大时二德集=天德+月德', set(DE_GODS_ERDE) == {'天德', '月德'})
    check('禁并排除对登记（月破×天赦天愿/厌对×天愿）',
          FORBIDDEN_PAIRS.get('月破') == ('天赦', '天愿')
          and FORBIDDEN_PAIRS.get('厌对') == ('天愿',))
    check('天恩不在德神制化集内', '天恩' not in DE_GODS_ALL)
    try:
        get_de_gods({'month_zhi': '午', 'day_gan': '丙', 'day_zhi': '戌'},
                    allow=('天德', '天恩'))
        check('allow 越界拦截', False)
    except AssertionError:
        check('allow 越界拦截', True)

    print('== M2 止忌子集映射表（配置化判据冻结） ==')
    check('军事=∅', ZHIJI_EVENT_MAPPING['军事'] == frozenset())
    check('缓刑=∅', ZHIJI_EVENT_MAPPING['缓刑'] == frozenset())
    check('疗病=求医', ZHIJI_EVENT_MAPPING['疗病'] == frozenset({'求医'}))
    check('破屋坏垣=拆舍', ZHIJI_EVENT_MAPPING['破屋坏垣'] == frozenset({'拆舍'}))
    check('map(军事)=空集', map_zhiji_events(('军事',)) == frozenset())
    check('map(军事,疗病)={求医}', map_zhiji_events(('军事', '疗病')) == frozenset({'求医'}))
    check('映射表缺项保守不豁免', map_zhiji_events(('入学',)) is None)

    print('== M3 谓词同源性（2026 全年×15 事项×6 谓词） ==')
    PRED = ['_is_tiande', '_is_yuede', '_is_tiande_he', '_is_yuede_he',
            '_is_tianshe', '_is_tianyuan']
    EVENTS = ['嫁娶', '修造', '动土', '拆舍', '入宅', '开业', '出行', '安床',
              '作灶', '安葬', '入学', '求医', '签约', '通用', '祭祀']
    div = []
    d = datetime.date(2026, 1, 1)
    while d <= datetime.date(2026, 12, 31):
        sz = calculate_sizhu(d, 12, 0)
        for ev in EVENTS:
            ck = get_checker(ev)
            for p in PRED:
                if getattr(ck, p)(sz) != getattr(ShenShaChecker, p)(ck, sz):
                    div.append((str(d), ev, p))
        d += datetime.timedelta(days=1)
    check('子类 override 与基类单点零分歧', not div, str(div[:3]))

    print('== M4 引擎行为（合成四柱） ==')
    s_wumu_hit = {'month_zhi': '午', 'day_gan': '丙', 'day_zhi': '戌'}
    s_wumu_miss1 = {'month_zhi': '巳', 'day_gan': '丙', 'day_zhi': '戌'}
    s_wumu_miss2 = {'month_zhi': '午', 'day_gan': '甲', 'day_zhi': '戌'}
    check('五墓：午月丙戌(月德并)→True', eval_wumu_exempt(s_wumu_hit) is True)
    check('五墓：巳月丙戌(月外)→False', eval_wumu_exempt(s_wumu_miss1) is False)
    check('五墓：午月甲戌(无月德)→False', eval_wumu_exempt(s_wumu_miss2) is False)
    s_yd_td = {'month_zhi': '午', 'day_gan': '丙', 'day_zhi': '子',
               'day_pillar_gan': '丙'}
    check('厌对：月德日→True', eval_yandui_exempt(s_wumu_hit)[0] is True)
    check('厌对：非五德日→False', eval_yandui_exempt(s_wumu_miss2)[0] is False)
    s_dashi_hit = {'month_zhi': '丑', 'day_gan': '庚', 'day_zhi': '午'}
    s_dashi_one = {'month_zhi': '丑', 'day_gan': '甲', 'day_zhi': '午'}
    s_dashi_out = {'month_zhi': '寅', 'day_gan': '庚', 'day_zhi': '午'}
    da, dn = eval_dashi_chouwei_exempt(s_dashi_hit, '通用')
    check('大时：丑月庚午(二德并)→豁免', da is True)
    check('大时：豁免文案含军事警示', '军事' in dn and '已豁免' in dn, dn)
    check('大时：文案含矩阵#9锚', '矩阵#9' in dn, dn)
    check('大时：文案=单点常量', dn == MILITARY_EMPTY_NOTE)
    check('大时：丑月甲午(单德)→不豁免',
          eval_dashi_chouwei_exempt(s_dashi_one, '通用') == (False, ''))
    check('大时：寅月(非丑未)→不豁免',
          eval_dashi_chouwei_exempt(s_dashi_out, '通用') == (False, ''))

    print('== M5 行为锚定（真实日） ==')
    # 厌对豁免日：2026-02-11 寅月丙辰（月德并）
    sz = calculate_sizhu(datetime.date(2026, 2, 11), 12, 0)
    check('引擎：2026-02-11 厌对豁免=True', eval_yandui_exempt(sz)[0] is True)
    names = [(s['name'], s['score']) for s in get_checker('嫁娶').check(sz, [])]
    check('嫁娶通道豁免日发射豁免键0分',
          ('厌对·制化豁免', 0) in names and ('厌对', -10) not in names, str(names))
    names = [(s['name'], s['score']) for s in get_checker('修造').check(sz, [])]
    check('非嫁娶通道豁免日发射豁免键0分',
          ('厌对·制化豁免', 0) in names and ('厌对', 0) not in names, str(names))
    # 厌对非豁免日：2026-01-07 丑月辛巳
    sz = calculate_sizhu(datetime.date(2026, 1, 7), 12, 0)
    check('引擎：2026-01-07 厌对豁免=False', eval_yandui_exempt(sz)[0] is False)
    names = [(s['name'], s['score']) for s in get_checker('嫁娶').check(sz, [])]
    check('嫁娶通道非豁免日仍 -10', ('厌对', -10) in names, str(names))
    names = [(s['name'], s['score']) for s in get_checker('修造').check(sz, [])]
    check('非嫁娶通道非豁免日仍 0 展示', ('厌对', 0) in names, str(names))
    # 大时/五墓 2026 firing 日（首个）仍 -12
    first_dashi = first_wumu = None
    d = datetime.date(2026, 1, 1)
    while d <= datetime.date(2026, 12, 31) and not (first_dashi and first_wumu):
        sz = calculate_sizhu(d, 12, 0)
        if first_dashi is None and get_checker('通用')._is_dashi(sz):
            first_dashi = (d, sz)
        if first_wumu is None and get_checker('通用')._is_wumu(sz):
            first_wumu = (d, sz)
        d += datetime.timedelta(days=1)
    check('2026 找到大时 firing 日', first_dashi is not None)
    if first_dashi:
        d, sz = first_dashi
        names = [(s['name'], s['score']) for s in get_checker('通用').check(sz, [])]
        check('大时 firing 日仍 -12（%s）' % d, ('大时', -12) in names, str(names))
        check('大时 firing 日无豁免键', not any(
            '制化豁免' in x[0] for x in names))
    check('2026 找到五墓 firing 日', first_wumu is not None)
    if first_wumu:
        d, sz = first_wumu
        names = [(s['name'], s['score']) for s in get_checker('通用').check(sz, [])]
        check('五墓 firing 日仍 -12（%s）' % d, ('五墓', -12) in names, str(names))
    # 大时真实豁免日扫描（2020–2035；未命中记 SKIP）
    dashi_ex_day = None
    d = datetime.date(2020, 1, 1)
    while d <= datetime.date(2035, 12, 31):
        sz = calculate_sizhu(d, 12, 0)
        if sz['month_zhi'] in ('丑', '未') and get_checker('通用')._is_dashi(sz) \
                and eval_dashi_chouwei_exempt(sz, '通用')[0]:
            dashi_ex_day = (d, sz)
            break
        d += datetime.timedelta(days=1)
    if dashi_ex_day:
        d, sz = dashi_ex_day
        names = [(s['name'], s['score']) for s in get_checker('通用').check(sz, [])]
        check('大时真实豁免日（%s）发射豁免键' % d,
              any(x[0] == '大时·制化豁免' for x in names)
              and ('大时', -12) not in names, str(names))
    else:
        print('  SKIP  2020–2035 无大时真实豁免日（2026 探针已证全年零重合，'
              '引擎层 M4 已覆盖逻辑）')

    print('== M6 哨兵与注册面 ==')
    from modules.评分器 import calculate_score
    sz = calculate_sizhu(datetime.date(2026, 11, 4), 12, 0)
    r = calculate_score(sz, '入宅')
    check('哨兵分=216', r['score'] == 216, str(r['score']))
    check('哨兵级=上吉', '上吉' in str(r.get('level', '')))
    check('哨兵日无制化豁免键', not any(
        '制化豁免' in s['name'] for s in r.get('shensha_list', [])))
    check('豁免键未注册分值（fallback 0 by design）',
          shensha_score('通用', '大时·制化豁免', None) is None
          and shensha_score('通用', '五墓·制化豁免', None) is None
          and shensha_score('嫁娶', '厌对·制化豁免', None) is None)

    print()
    print('FAILS=%d' % len(FAILS))
    return 1 if FAILS else 0


if __name__ == '__main__':
    raise SystemExit(main())
