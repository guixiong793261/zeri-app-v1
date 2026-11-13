# -*- coding: utf-8 -*-
"""001 §277「实战上品」快捷通道回归验证（2026-11-13 用户拍板）。

判据：
- 评分器在 score_details 显式输出 6 个布尔标志位；
- 排序键 perfect_profile 在「无否决 + 日课校验零警告」前提下，
  嫁娶通道（得令+相主+六合+大利月）／山向通道（得令+相主+扶山补龙+合局不克山）
  四要素齐备即 tier='shangpin'（tier_kind='practical_shangpin'）；
- 不改底层加减分、不改否决、不改极品（perfect）严格判定；
- 反向：缺任一要素、有否决、非该通道事项，一律不列上品。
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer, calculate_score
from modules.排序键 import perfect_profile, tier_flags

FAILS = []
FLAG_KEYS = ('flag_deling', 'flag_xiangzhu', 'flag_liuhe',
             'flag_dali_or_xiaoli', 'flag_fushan_bulong', 'flag_heju_li_shan')

BRIDE = {'name': '新娘', 'role': '新娘', '性别': '女',
         'sizhu': '己卯 丁卯 丁亥 癸卯', 'xishen': '水、金', 'yongshen': '水'}
GROOM = {'name': '新郎', 'role': '新郎', '性别': '男',
         'sizhu': '戊寅 壬戌 癸巳 壬子', 'xishen': '金、水', 'yongshen': '金'}


def check(cond, label, detail=''):
    if cond:
        print('  PASS  ' + label)
    else:
        print('  FAIL  ' + label + ('  | ' + str(detail) if detail != '' else ''))
        FAILS.append(label)


def _score(y, m, d, h, ev, owners, shan=''):
    sz = calculate_sizhu((y, m, d), h, 0, longitude=120)
    return calculate_score(sz, ev, owners=[dict(o) for o in owners],
                           shan_xiang=shan, zeli_mode='pure')


# ---------------- 1) 评分器字段输出 ----------------
def test_flags_emitted():
    print('\n[1] 评分器 score_details 显式输出 6 个布尔标志位')
    r = _score(2026, 8, 4, 12, '嫁娶', [BRIDE, GROOM])
    _d = r.get('score_details') or {}
    check(all(k in _d for k in FLAG_KEYS),
          '嫁娶链路 6 个 flag_* 齐全', sorted(set(FLAG_KEYS) - set(_d)))
    check(all(isinstance(_d.get(k), bool) for k in FLAG_KEYS),
          '嫁娶链路 flag 值均为 bool')
    r2 = _score(2026, 8, 4, 12, '修造', [{'name': '福主', 'role': '事主',
                                          '性别': '男', 'sizhu': '戊寅 壬戌 癸巳 壬子'}],
                shan='坤')
    _d2 = r2.get('score_details') or {}
    check(all(k in _d2 for k in FLAG_KEYS),
          '修造链路 6 个 flag_* 齐全', sorted(set(FLAG_KEYS) - set(_d2)))
    check(FLAG_KEYS and not any(k not in _d2 for k in FLAG_KEYS),
          '修造链路 flag 无缺键')


# ---------------- 2) 标志位口径 ----------------
def test_flag_semantics():
    print('\n[2] 标志位口径（得分/神煞/克山判据）')
    sc = Scorer()
    _d = {'月令详细': {'旺衰得分': 10}, '相主得分': 15}
    _ss = [{'name': '大利月（新娘）', 'score': 30},
           {'name': '扶山', 'score': 10},
           {'name': '六合', 'score': 8}]
    _wx = {'地支关系': ['时柱午 与 日柱未 六合', '三合火局']}
    sc._attach_tier_flags(_d, _ss, _wx, {'heavy_sha_names': []}, [BRIDE])
    check(_d.get('flag_deling') is True, '旺衰+10 → 得令 True')
    check(_d.get('flag_xiangzhu') is True, '相主+15 且有事主 → 相主 True')
    check(_d.get('flag_liuhe') is True, '地支关系含六合 → 六合 True')
    check(_d.get('flag_dali_or_xiaoli') is True, '神煞命中大利月 → 利月 True')
    check(_d.get('flag_fushan_bulong') is True, '神煞命中扶山 → 扶山补龙 True')
    check(_d.get('flag_heju_li_shan') is True, '有合局且无克山 → 合局不克山 True')

    # 反向：克山 → 合局不克山 False
    _d2 = {'月令详细': {'旺衰得分': 10}, '相主得分': 15}
    sc._attach_tier_flags(_d2, _ss, _wx, {'heavy_sha_names': ['克山运']}, [BRIDE])
    check(_d2.get('flag_heju_li_shan') is False, '重煞含克山运 → 合局不克山 False')
    # 空事主 → 相主维度不适用，视为已过（001 §280，2026-11-14 用户拍板）
    _d3 = {'月令详细': {'旺衰得分': -5}, '相主得分': 0}
    sc._attach_tier_flags(_d3, [], {'地支关系': []}, {}, [])
    check(_d3.get('flag_deling') is False and _d3.get('flag_xiangzhu') is True,
          '囚地 + 空事主 → 得令 False、相主视为不适用 True')
    # 反向：有事主且相主为 0 → 相主 False（不适用豁免不得外溢到有事主场景）
    _d4x = {'月令详细': {'旺衰得分': 5}, '相主得分': 0}
    sc._attach_tier_flags(_d4x, [], {'地支关系': []}, {}, [BRIDE])
    check(_d4x.get('flag_xiangzhu') is False,
          '有事主且相主0 → 相主 False（反向）')


def test_shan_dual_standards():
    print('\n[2b] 山向通道双口径（2026-11-13 用户拍板）')
    sc = Scorer()
    # 相主：山向取「喜用神匹配>0 且相主得分≥0」（修造底层从不给相主正分）
    _d = {'月令详细': {'旺衰得分': 10}, '相主得分': 0,
          '事主匹配': [{'name': '福主', 'score': 10}]}
    sc._attach_tier_flags(_d, [], {'地支关系': ['年支午 与 日支未 六合']}, {},
                          [BRIDE], event_type='修造',
                          sanyuan_analysis={'课山': {'判定': '吉'}})
    check(_d.get('flag_xiangzhu') is True,
          '山向：相主0 但喜用神+10 → 相主 True', _d.get('flag_xiangzhu'))
    check(_d.get('flag_fushan_bulong') is True,
          '山向：三元合参课山判定吉 → 扶山补龙 True', _d.get('flag_fushan_bulong'))
    # 反向：相主冲克（负分）即便喜用神有补益也不给
    _d2 = {'月令详细': {'旺衰得分': 10}, '相主得分': -20,
           '事主匹配': [{'name': '福主', 'score': 10}]}
    sc._attach_tier_flags(_d2, [], {'地支关系': []}, {}, [BRIDE],
                          event_type='修造')
    check(_d2.get('flag_xiangzhu') is False,
          '山向：相主冲克 -20 → 相主 False（反向）', _d2.get('flag_xiangzhu'))
    # 反向：喜用神为0 → 相主 False
    _d3 = {'月令详细': {'旺衰得分': 10}, '相主得分': 0,
           '事主匹配': [{'name': '福主', 'score': 0}]}
    sc._attach_tier_flags(_d3, [], {'地支关系': []}, {}, [BRIDE],
                          event_type='修造')
    check(_d3.get('flag_xiangzhu') is False,
          '山向：喜用神匹配0 → 相主 False（反向）', _d3.get('flag_xiangzhu'))
    # 对照：嫁娶通道仍按「相主得分>0」严格口径
    _d4 = {'月令详细': {'旺衰得分': 10}, '相主得分': 0,
           '事主匹配': [{'name': '福主', 'score': 10}]}
    sc._attach_tier_flags(_d4, [], {'地支关系': []}, {}, [BRIDE],
                          event_type='嫁娶')
    check(_d4.get('flag_xiangzhu') is False,
          '嫁娶：相主0 时不同用山向宽口径（反向）', _d4.get('flag_xiangzhu'))
    # 排序键回退路径同样生效（删键重算）
    _r = {'score_details': {'月令详细': {'旺衰得分': 10}, '相主得分': 0,
                            '事主匹配': [{'name': '福主', 'score': 10}]},
          'wu_xing_result': {'details': {'地支关系': ['年支午 与 日支未 六合']}},
          'shensha_list': [], 'heavy_sha_names': [], 'sansha_info': {},
          'sanyuan_analysis': {'课山': {'判定': '吉'}}}
    _tf = tier_flags(_r, [BRIDE], '修造')
    check(_tf['flag_xiangzhu'] is True and _tf['flag_fushan_bulong'] is True,
          '排序键回退：山向双口径与评分器同源', _tf)


# ---------------- 3) 排序键回退一致性 ----------------
def test_tier_flags_fallback():
    print('\n[3] tier_flags：历史记录缺键回退与评分器同口径')
    r = _score(2026, 8, 4, 12, '嫁娶', [BRIDE, GROOM])
    _live = tier_flags(r, [BRIDE, GROOM])
    _stripped = dict(r)
    _sd = dict(r.get('score_details') or {})
    for _k in FLAG_KEYS:
        _sd.pop(_k, None)
    _stripped['score_details'] = _sd
    _fb = tier_flags(_stripped, [BRIDE, GROOM])
    check(_live == _fb, '删键回退重算 == 评分器直出', (_live, _fb))


# ---------------- 4) 实战上品命中（patch lint 为通过） ----------------
class _FakeLint(object):
    has_error = False
    warn_count = 0
    error_count = 0
    executed_ids = ['E001', 'E002']


def _patch_lint():
    import modules.日课校验器 as _jc
    _jc.lint_lesson = lambda *a, **kw: _FakeLint()


def _fake_result(ev, flags, veto=None, score=88, level='★★★★ 大吉'):
    _sd = {'月令详细': {'旺衰得分': 10}, '相主得分': 15}
    _sd.update({k: bool(v) for k, v in flags.items()})
    return {
        'score': score, 'level': level,
        'score_details': _sd,
        'shensha_list': [], 'veto_reasons': list(veto or []),
        'wu_xing_result': {'details': {'地支关系': []}},
        'sansha_info': {}, 'heavy_sha_names': [],
        'sizhu': {'year': '丙午', 'month': '庚寅', 'day': '甲子', 'hour': '乙丑'},
    }


def test_practical_marriage():
    print('\n[4] 嫁娶通道：四要素齐备 + 总分≥100 → 实战上品')
    _patch_lint()
    _f = {k: True for k in FLAG_KEYS}
    _r = perfect_profile(_fake_result('嫁娶', _f, score=120), [BRIDE], '嫁娶')
    check(_r.get('tier_kind') == 'practical_shangpin', '嫁娶四要素齐 → practical_shangpin',
          _r.get('tier_kind'))
    check(_r.get('tier') == 'shangpin' and _r.get('shangpin') is True,
          'tier=shangpin 且 shangpin=True')
    check('得令、相主、六合、大利月俱全' == str(_r.get('tier_reason')),
          'tier_reason 写明凑齐要素', _r.get('tier_reason'))
    check('🌟 实战上品' in str(_r.get('lint_note')), '悬停文案含🌟实战上品',
          _r.get('lint_note'))

    # 001 §278 新增：总分门槛（嫁娶 100）
    _r99 = perfect_profile(_fake_result('嫁娶', _f, score=99), [BRIDE], '嫁娶')
    check(_r99.get('tier') == 'none', '总分99 → 不上品（门槛100）', _r99.get('tier'))
    check('门槛' in str(_r99.get('lint_note')), '悬停写明分数门槛拦截',
          _r99.get('lint_note'))
    _r100 = perfect_profile(_fake_result('嫁娶', _f, score=100), [BRIDE], '嫁娶')
    check(_r100.get('tier') == 'shangpin', '总分100 → 恰好达标（边界）', _r100.get('tier'))

    # 反向：缺六合
    _f2 = dict(_f); _f2['flag_liuhe'] = False
    _r2 = perfect_profile(_fake_result('嫁娶', _f2, score=120), [BRIDE], '嫁娶')
    check(_r2.get('tier') == 'none', '缺六合 → 不上品', _r2.get('tier'))
    # 反向：缺利月
    _f3 = dict(_f); _f3['flag_dali_or_xiaoli'] = False
    _r3 = perfect_profile(_fake_result('嫁娶', _f3, score=120), [BRIDE], '嫁娶')
    check(_r3.get('tier') == 'none', '缺大利月 → 不上品', _r3.get('tier'))
    # 反向：有否决
    _r4 = perfect_profile(_fake_result('嫁娶', _f, veto=['年命伏吟'], score=120),
                          [BRIDE], '嫁娶')
    check(_r4.get('tier') == 'none', '有 veto_reasons → 不上品', _r4.get('tier'))
    # 反向：总分 ≤0
    _r5 = perfect_profile(_fake_result('嫁娶', _f, score=0, level='❌ 凶'),
                          [BRIDE], '嫁娶')
    check(_r5.get('tier') == 'none', '总分0/含凶 → 不上品', _r5.get('tier'))


def test_practical_shan():
    print('\n[5] 山向通道：得令+相主+扶山补龙+合局不克山 + 总分≥150 → 实战上品')
    _f = {k: True for k in FLAG_KEYS}
    _r = perfect_profile(_fake_result('修造', _f, score=200), [BRIDE], '修造')
    check(_r.get('tier_kind') == 'practical_shangpin', '修造四要素齐 → practical_shangpin',
          _r.get('tier_kind'))
    check('扶山补龙' in str(_r.get('tier_reason')), 'tier_reason 含扶山补龙',
          _r.get('tier_reason'))
    # 001 §278 新增：总分门槛（山向 150）；68 / 149 分一律剔除
    _r68 = perfect_profile(_fake_result('修造', _f, score=68, level='★ 平'),
                           [BRIDE], '修造')
    check(_r68.get('tier') == 'none', '★平 68 分 → 不上品（§278 核心回归）',
          _r68.get('tier'))
    _r149 = perfect_profile(_fake_result('修造', _f, score=149), [BRIDE], '修造')
    check(_r149.get('tier') == 'none', '149 分 → 不上品（门槛150）', _r149.get('tier'))
    _r150 = perfect_profile(_fake_result('修造', _f, score=150), [BRIDE], '修造')
    check(_r150.get('tier') == 'shangpin', '150 分 → 恰好达标（边界）',
          _r150.get('tier'))
    _f2 = dict(_f); _f2['flag_heju_li_shan'] = False
    _r2 = perfect_profile(_fake_result('修造', _f2, score=200), [BRIDE], '修造')
    check(_r2.get('tier') == 'none', '合局克山 → 不上品', _r2.get('tier'))
    _f3 = dict(_f); _f3['flag_fushan_bulong'] = False
    _r3 = perfect_profile(_fake_result('入宅', _f3, score=200), [BRIDE], '入宅')
    check(_r3.get('tier') == 'none', '入宅缺扶山补龙 → 不上品', _r3.get('tier'))
    # 别名口径：装修/移徙同属通道
    _r4 = perfect_profile(_fake_result('装修', _f, score=200), [BRIDE], '装修')
    check(_r4.get('tier_kind') == 'practical_shangpin', '别名「装修」同走山向通道',
          _r4.get('tier_kind'))


def test_other_event_not_affected():
    print('\n[6] 反向：非嫁娶/非山向事项不受影响')
    _f = {k: True for k in FLAG_KEYS}
    _r = perfect_profile(_fake_result('开业', _f, score=200), [BRIDE], '开业')
    check(_r.get('tier') == 'none', '开业四要素齐也不列实战上品', _r.get('tier'))


def test_278_dual_and_thresholds_source():
    print('\n[7] 001 §278：双上品合并 + 门槛常量源码锚点')
    p = os.path.join(_ROOT, 'modules', '排序键.py')
    with open(p, 'r', encoding='utf-8') as f:
        s = f.read()
    check('_TIER_MIN_SCORE_MARRIAGE = 100' in s, '嫁娶门槛常量=100')
    check('_TIER_MIN_SCORE_SHAN = 150' in s, '山向门槛常量=150')
    check("_tier_kind = 'dual_shangpin'" in s, '双上品合并分支存在')
    check("elif _dongtu_ok and _practical_ok:" in s, '双绝判定先于单通道')
    check('上品分数门槛拦截' in s, '门槛拦截悬停文案')
    p2 = os.path.join(_ROOT, '主程序.py')
    with open(p2, 'r', encoding='utf-8') as f:
        s2 = f.read()
    check('【上品·双绝】' in s2 and '【实战上品】' in s2 and '【制化上品】' in s2,
          '主程序三档上品标签齐全且不重叠')
    p3 = os.path.join(_ROOT, 'modules', '反推UI.py')
    with open(p3, 'r', encoding='utf-8') as f:
        s3 = f.read()
    check('🌟 上品·双绝' in s3 and '🌟 实战上品' in s3 and '▲ 制化上品' in s3,
          '反推UI三档标签齐全')


def main():
    print('=' * 62)
    print('001 §277 实战上品快捷通道验证')
    print('=' * 62)
    test_flags_emitted()
    test_flag_semantics()
    test_shan_dual_standards()
    test_tier_flags_fallback()
    test_practical_marriage()
    test_practical_shan()
    test_other_event_not_affected()
    test_278_dual_and_thresholds_source()
    print('\n' + '=' * 62)
    if FAILS:
        print('FAILED %d 项：%s' % (len(FAILS), '；'.join(FAILS)))
        sys.exit(1)
    print('ALL PASS')
    sys.exit(0)


if __name__ == '__main__':
    main()
