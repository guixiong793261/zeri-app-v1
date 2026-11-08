# -*- coding: utf-8 -*-
"""001 §233 事项定制判据：perfect_profile(result, owners, event_type) 锁定。

A. profile_plan_keys：各事项五维名称序列锁定（专属替换 1 项，通用原序）。
B. perfect_profile 结构自洽：items×5 / marks / ok_count / all_ok / tips。
C. 专属分支判定：扶山补龙 / 利月与吉日 / 全家相合 / 仙命相合 / 出发方向。
D. 向后兼容：event_type 缺省（''）→ §231 通用五维（相主）。

说明：本测试全部使用合成 dict（不跑 calculate_score），只锁定排序键层
"从既有产出提取判据"的行为，不验证评分器本身的分值口径。
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from modules.排序键 import perfect_profile, profile_plan_keys  # noqa: E402

FAILS = []


def check(cond, label, detail=''):
    tag = 'PASS' if cond else 'FAIL'
    print('  [%s] %s%s' % (tag, label, ('  | ' + str(detail)) if detail else ''))
    if not cond:
        FAILS.append(label)


# ---------------- 合成数据 ----------------
def _base_result():
    """一个五维全 ✓ 的合成 result（得令+10/三合/相主+15/天德+20/无硬忌）。"""
    return {
        'score': 60, 'level': '大吉', 'veto_reasons': [],
        'shensha_list': [{'name': '天德', 'score': 20}],
        'score_details': {
            '月令详细': {'旺衰得分': 10},
            '相主得分': 15,
            '相主详情': ['福主生肖龙与日课日支申三合，+15分'],
        },
        'wu_xing_result': {'details': {'地支关系': ['申子辰三合水局']}},
    }


OWNERS = [{'name': '福主', 'role': '福主', 'year_sx': '龙', '性别': '男'}]
OWNERS_XM = [{'name': '亡人', 'role': '死者', 'year_sx': '鼠', '性别': '男'}]


# ==================== A. profile_plan_keys 序列锁定 ====================
def test_plan_keys():
    print('\n[A] profile_plan_keys 五维名称序列')
    _cases = [
        ('修造', '扶山补龙'), ('动土', '扶山补龙'),
        ('嫁娶', '利月与吉日'), ('订婚', '利月与吉日'), ('纳采', '利月与吉日'),
        ('入宅', '全家相合'), ('移徙', '全家相合'),
        ('安葬', '仙命相合'),
        ('出行', '出发方向'),
    ]
    for _ev, _sp in _cases:
        check(profile_plan_keys(_ev) == ['得令', '合局', '德神', _sp, '相主', '硬忌'],
              '%s → 得令/合局/德神/%s/相主/硬忌' % (_ev, _sp),
              str(profile_plan_keys(_ev)))
    for _ev in ('开业', '入学', '', '通用'):
        check(profile_plan_keys(_ev) == ['得令', '合局', '相主', '德神', '硬忌'],
              '通用事项(%s) → 原五维' % (_ev or '空'), str(profile_plan_keys(_ev)))


# ==================== B. 结构自洽 ====================
def test_structure():
    print('\n[B] perfect_profile 结构自洽')
    for _ev in ('修造', '嫁娶', '入宅', '安葬', '出行', '开业', ''):
        _r = perfect_profile(_base_result(), OWNERS_XM if _ev == '安葬' else OWNERS, _ev)
        _keys = [i['key'] for i in _r['items']]
        check(_keys == profile_plan_keys(_ev),
              '%s items.key 序列 == profile_plan_keys' % (_ev or '空'), str(_keys))
        _n = len(_r['items'])
        check(_n == (6 if _ev in ('修造', '嫁娶', '入宅', '安葬', '出行') else 5)
              and len(_r['marks']) == _n,
              '%s %d 维齐备' % (_ev or '空', _n))
        check(_r['ok_count'] == sum(1 for i in _r['items'] if i['ok']),
              '%s ok_count 自洽' % (_ev or '空'))
        check(_r['all_ok'] == (_r['ok_count'] == _n), '%s all_ok 自洽' % (_ev or '空'))
        check(len(_r['tips']) == _n - _r['ok_count'], '%s tips 自洽' % (_ev or '空'))


# ==================== C. 专属分支判定 ====================
def test_fushan():
    print('\n[C1] 扶山补龙（修造/动土）')
    _r = _base_result()
    _r['shensha_list'].append({'name': '补龙', 'score': 12})
    _chk = perfect_profile(_r, OWNERS, '修造')
    _sp = _chk['items'][3]
    check(_sp['key'] == '扶山补龙' and _sp['ok'] and '补龙' in _sp['detail'],
          '补龙+12 → ✓', _sp['detail'])
    _r2 = _base_result()
    _r2['shensha_list'].append({'name': '扶山', 'score': -10})  # 负分不算
    _sp2 = perfect_profile(_r2, OWNERS, '动土')['items'][3]
    check(not _sp2['ok'] and '未生扶坐山' in _sp2['detail'],
          '扶山负分 → ✗ 未生扶坐山', _sp2['detail'])


def test_liyue():
    print('\n[C2] 利月与吉日（嫁娶）')
    for _n in ('大利月', '小利月', '周堂吉日', '不将日'):
        _r = _base_result()
        _r['shensha_list'].append({'name': _n, 'score': 15})
        _sp = perfect_profile(_r, OWNERS, '嫁娶')['items'][3]
        check(_sp['key'] == '利月与吉日' and _sp['ok'] and _n in _sp['detail'],
              '%s → ✓' % _n, _sp['detail'])
    _sp = perfect_profile(_base_result(), OWNERS, '嫁娶')['items'][3]
    check(not _sp['ok'] and '未命中' in _sp['detail'], '均未命中 → ✗', _sp['detail'])


def test_family():
    print('\n[C3] 全家相合（入宅/移徙）')
    # 无事主 → ✗
    _sp = perfect_profile(_base_result(), [], '入宅')['items'][3]
    check(not _sp['ok'] and '未填写事主' in _sp['detail'], '未填事主 → ✗', _sp['detail'])
    # 有事主、相主详情无负 → ✓
    _sp = perfect_profile(_base_result(), OWNERS, '入宅')['items'][3]
    check(_sp['ok'] and '无冲' in _sp['detail'], '相主+15 无冲 → ✓', _sp['detail'])
    # 硬性门槛（六冲）→ ✗
    _r = _base_result()
    _r['score_details']['相主得分'] = -30
    _r['score_details']['相主详情'] = ['[硬性门槛]福主生肖龙与日课日支戌六冲（年命六冲），不可用，-30分']
    _sp = perfect_profile(_r, OWNERS, '移徙')['items'][3]
    check(not _sp['ok'] and '含冲命' in _sp['detail'], '硬性门槛 → ✗ 含冲命', _sp['detail'])
    # 普通负分条目 → ✗ 扣分
    _r = _base_result()
    _r['score_details']['相主得分'] = -10
    _r['score_details']['相主详情'] = ['福主生肖龙与日课日支巳相害，-10分']
    _sp = perfect_profile(_r, OWNERS, '入宅')['items'][3]
    check(not _sp['ok'] and '扣分' in _sp['detail'], '相害-10 → ✗ 扣分', _sp['detail'])


def test_xianming():
    print('\n[C4] 仙命相合（安葬）')
    # 无仙命卡 → ✗
    _sp = perfect_profile(_base_result(), OWNERS, '安葬')['items'][3]
    check(not _sp['ok'] and '未填写仙命' in _sp['detail'], '无仙命卡 → ✗', _sp['detail'])
    # 仙命卡 + 坐山得分>=0 无冲 → ✓
    _r = _base_result()
    _r['score_details']['仙命坐山得分'] = 20
    _sp = perfect_profile(_r, OWNERS_XM, '安葬')['items'][3]
    check(_sp['ok'] and '无冲无克' in _sp['detail'], '坐山生仙命+20 → ✓', _sp['detail'])
    # 坐山克仙命 -30 → ✗
    _r = _base_result()
    _r['score_details']['仙命坐山得分'] = -30
    _sp = perfect_profile(_r, OWNERS_XM, '安葬')['items'][3]
    check(not _sp['ok'] and '坐山克仙命' in _sp['detail'], '坐山克仙命-30 → ✗', _sp['detail'])
    # 仙命真冲条目 → ✗
    _r = _base_result()
    _r['score_details']['仙命坐山得分'] = 0
    _r['score_details']['相主详情'] = ['亡人年命（仙命）鼠与日课日支午真冲（仙命大忌，须见吉神制化），-30分']
    _sp = perfect_profile(_r, OWNERS_XM, '安葬')['items'][3]
    check(not _sp['ok'] and '犯冲' in _sp['detail'], '仙命真冲 → ✗', _sp['detail'])


def test_travel():
    print('\n[C5] 出发方向（出行）')
    _r = _base_result()
    _r['score_details']['出行方位得分'] = 15
    _sp = perfect_profile(_r, OWNERS, '出行')['items'][3]
    check(_sp['ok'] and '吉' in _sp['detail'], '方位+15 → ✓ 吉', _sp['detail'])
    _r = _base_result()
    _r['score_details']['出行方位得分'] = 0
    _sp = perfect_profile(_r, OWNERS, '出行')['items'][3]
    check(_sp['ok'] and '未犯煞' in _sp['detail'], '方位 0 → ✓ 未犯煞', _sp['detail'])
    _r = _base_result()
    _r['score_details']['出行方位得分'] = -20
    _sp = perfect_profile(_r, OWNERS, '出行')['items'][3]
    check(not _sp['ok'] and '犯煞' in _sp['detail'], '方位-20 → ✗ 犯煞', _sp['detail'])


# ==================== D. 向后兼容 ====================
def test_compat():
    print('\n[D] event_type 缺省 → §231 通用五维')
    _r = perfect_profile(_base_result(), OWNERS)
    check([i['key'] for i in _r['items']] == ['得令', '合局', '相主', '德神', '硬忌'],
          '缺省 event_type → 相主居中', str([i['key'] for i in _r['items']]))


if __name__ == '__main__':
    test_plan_keys()
    test_structure()
    test_fushan()
    test_liyue()
    test_family()
    test_xianming()
    test_travel()
    test_compat()
    print('\n========================================================')
    if FAILS:
        print('FAIL: %d 项未过：%s' % (len(FAILS), FAILS))
        sys.exit(1)
    print('ALL PASS')
    sys.exit(0)
