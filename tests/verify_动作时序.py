# -*- coding: utf-8 -*-
"""
================================================================================
001 §214 P2-A：动作时序编排纯函数验证（modules/动作时序.py）
================================================================================
测试计划（设计书 §九 测试计划 1-4，P2-A 范围）：
  1. plan_actions 对递增组合穷举，断言最优解 = 暴力解。
  2. 构造只有 2 个可用时辰的日 → status='partial'、missing 准确、alt 有文案。
  3. 猪命新娘日（年支亥）→ 入选三段均非冲亥（冲支巳）。
  4. 断言 '子' 不出现在任何 plan（子时禁用）。
  5. （附加）R1 硬排除：disabled / veto>0 / score<=0 / shashi 不入选。
  6. （附加）R2 交叉校验：冲命但 disabled 未标 → checks.ok=False。
  7. （附加）actions 为空 → status='none'。

退出码：0=全通过，1=有失败。
================================================================================
"""

import sys
from itertools import combinations

sys.path.insert(0, '.')
from modules.动作时序 import plan_actions, _ZHI_ORDER, _chong_zhi  # noqa: E402
from modules.事项标准 import action_sequence_of  # noqa: E402


# 12 时辰（子→亥）的构造辅助
def _mk_hour(zhi, score=100, level='吉', veto=0, disabled=False,
             shashi=False, shizhu='', xiong=None):
    h = {
        '地支': zhi, '时辰': zhi + '时', '时段': '',
        '时柱': shizhu or ('甲' + zhi),
        'score': score, 'level': level, 'veto': veto,
        'disabled': disabled, 'shashi': shashi,
        '凶': list(xiong or []), '吉神': [],
    }
    return h


def _full_12(**kw):
    """12 时辰，默认全可用、同分；可按地支覆盖参数。"""
    return [_mk_hour(z, **{**{'score': 100}, **kw.get(z, {})})
            for z in _ZHI_ORDER]


ACTIONS = action_sequence_of('嫁娶')
assert ACTIONS and len(ACTIONS) == 3, '嫁娶动作段配置应为 3 段'

failures = []


def check(name, cond, detail=''):
    if cond:
        print(f'  PASS  {name}')
    else:
        print(f'  FAIL  {name}  {detail}')
        failures.append(name)


# ---------- 测试 1：穷举与暴力解一致 ----------
print('\n[1] 穷举最优解 = 暴力解')
# 给 12 时辰不同分数，断言 plan 选出的 3 个时辰总分 = 所有 3 递增组合的最大总分
scores = {'子': 50, '丑': 80, '寅': 90, '卯': 70, '辰': 60, '巳': 95,
          '午': 85, '未': 75, '申': 65, '酉': 88, '戌': 92, '亥': 78}
# 子时禁用，构造时子时 score>0 但会被 R6 排除
hours = [_mk_hour(z, score=s) for z, s in scores.items()]
res = plan_actions(hours, owners=[], actions=ACTIONS)

# 暴力：排除子时 + 不可用后，穷举所有 3 递增组合取最大总分
from modules.动作时序 import _ZHI_START_HOUR, _is_candidate
valid = [(z, _ZHI_START_HOUR[z], scores[z]) for z in _ZHI_ORDER
         if _is_candidate({'地支': z, 'disabled': False, 'veto': 0,
                           'score': scores[z], 'shashi': False})]
valid.sort(key=lambda x: x[1])  # 按时钟点升序
best_sum = 0
best_combo = None
for combo in combinations(range(len(valid)), 3):
    s = sum(valid[i][2] for i in combo)
    if s > best_sum:
        best_sum = s
        best_combo = combo
plan_sum = sum(p['score'] for p in res['plan'])
check('status=full', res['status'] == 'full', res['status'])
check('3 段入选', len(res['plan']) == 3, str(len(res['plan'])))
check('最优总分 = 暴力解', plan_sum == best_sum,
      f'plan={plan_sum} brute={best_sum}')
check('无缺失段', res['missing'] == [], str(res['missing']))

# ---------- 测试 2：只有 2 个可用时辰 → partial ----------
print('\n[2] 仅 2 可用时辰 → partial + missing + alt')
hours2 = [_mk_hour(z, score=(80 if z in ('丑', '卯') else 0))
          for z in _ZHI_ORDER]
res2 = plan_actions(hours2, owners=[], actions=ACTIONS)
check('status=partial', res2['status'] == 'partial', res2['status'])
check('2 段入选', len(res2['plan']) == 2, str(len(res2['plan'])))
check('missing 含第三段', any('交拜' in m for m in res2['missing']),
      str(res2['missing']))
check('alt 非空', len(res2['alt']) > 0, str(res2['alt']))

# ---------- 测试 3：猪命（亥）新娘 → 入选段均非冲亥（冲支巳） ----------
print('\n[3] 亥命新娘交叉校验：入选段不含巳')
hours3 = _full_12()  # 全可用
res3 = plan_actions(hours3, owners=[{'年支': '亥'}], actions=ACTIONS)
chong_si = _chong_zhi('亥')
check('冲支=巳', chong_si == '巳', chong_si)
check('入选段均非巳', all(p['zhi'] != '巳' for p in res3['plan']),
      str([p['zhi'] for p in res3['plan']]))
# 因为巳时可用且分数高，正常会入选；但亥命冲巳，disabled 未标 → 交叉校验应 warn
# 这里全可用且同分，选最早 3 段（丑寅卯），不含巳，cross_ok 应为 True
check('cross_check 存在', len(res3['checks']) > 0, str(res3['checks']))

# 构造一个一定会选中巳时的场景（巳时分数远高于其他），验证交叉校验 warn
hours3b = [_mk_hour(z, score=(200 if z == '巳' else 10)) for z in _ZHI_ORDER]
res3b = plan_actions(hours3b, owners=[{'年支': '亥'}], actions=ACTIONS)
has_si = any(p['zhi'] == '巳' for p in res3b['plan'])
check('高分巳时入选', has_si, str([p['zhi'] for p in res3b['plan']]))
if has_si:
    cc = [c for c in res3b['checks'] if c['name'] == 'cross_check']
    check('交叉校验 ok=False', cc and not cc[0]['ok'],
          str(cc[0]) if cc else 'no check')

# ---------- 测试 4：子时不出现在 plan ----------
print('\n[4] 子时禁用：任何 plan 不含子')
hours4 = [_mk_hour(z, score=(300 if z == '子' else 100)) for z in _ZHI_ORDER]
res4 = plan_actions(hours4, owners=[], actions=ACTIONS)
check('plan 不含子', all(p['zhi'] != '子' for p in res4['plan']),
      str([p['zhi'] for p in res4['plan']]))

# ---------- 测试 5：R1 硬排除 ----------
print('\n[5] R1 硬排除：disabled/veto/score<=0/shashi 不入选')
hours5 = [
    _mk_hour('丑', score=200, disabled=True),       # 排除
    _mk_hour('寅', score=200, veto=1),              # 排除
    _mk_hour('卯', score=0),                        # 排除
    _mk_hour('辰', score=200, shashi=True),         # 排除
    _mk_hour('巳', score=200),                      # 可用
    _mk_hour('午', score=200),                      # 可用
    _mk_hour('未', score=200),                      # 可用
] + [_mk_hour(z, score=0) for z in ('申', '酉', '戌', '亥', '子')]
res5 = plan_actions(hours5, owners=[], actions=ACTIONS)
zhis = [p['zhi'] for p in res5['plan']]
check('仅巳午未入选', zhis == ['巳', '午', '未'], str(zhis))

# ---------- 测试 6：actions 为空 → none ----------
print('\n[6] actions 为空 → status=none')
res6 = plan_actions(_full_12(), owners=[], actions=[])
check('status=none', res6['status'] == 'none', res6['status'])
check('plan 为空', res6['plan'] == [], str(res6['plan']))

# ---------- 测试 7：时序单调 ----------
print('\n[7] 入选段钟点严格递增')
hours7 = _full_12()
res7 = plan_actions(hours7, owners=[], actions=ACTIONS)
starts = [_ZHI_START_HOUR[p['zhi']] for p in res7['plan']]
check('钟点递增', all(starts[i] < starts[i + 1] for i in range(len(starts) - 1)),
      str(starts))

# ---------- 汇总 ----------
print('\n' + '=' * 60)
if failures:
    print(f'FAIL：{len(failures)} 项失败：{failures}')
    sys.exit(1)
else:
    print('ALL PASS：P2-A 动作时序纯函数验证通过')
    sys.exit(0)
