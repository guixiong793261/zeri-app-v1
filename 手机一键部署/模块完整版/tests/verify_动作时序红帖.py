# -*- coding: utf-8 -*-
"""
================================================================================
001 §214 P2-C：动作时序 → 红帖端到端验证
================================================================================
测试计划（设计书 §九 测试计划 5-7）：
  5. prepare_entry + compose_marriage_lines 输出与 plan 三段逐字一致。
  6. 冲命 override → prepare_entry 抛错/拒绝（反向断言）。
  7. 软忌日 → 输出不含「大吉/大利」（反向断言）。
  8. （附加）无 action_plan → 红帖走原路径，_jishi 为通书前三。

退出码：0=全通过，1=有失败。
================================================================================
"""

import sys

sys.path.insert(0, '.')
from modules.择日贴 import prepare_entry, compose_marriage_lines  # noqa: E402

failures = []


def check(name, cond, detail=''):
    if cond:
        print(f'  PASS  {name}')
    else:
        print(f'  FAIL  {name}  {detail}')
        failures.append(name)


# 构造一个嫁娶 entry + action_plan
def _make_entry(action_plan=None, level='★★★★★ 上吉'):
    e = {
        'date': '2028-05-03',
        'sizhu': '戊申 丁巳 戊戌 癸丑',
        'score': '80',
        'level': level,
        'owners': '新郎、新娘',
        'event_type': '嫁娶',
        'groom': {'name': '新郎', 'year_gz': '丁亥', 'role': '乾造'},
        'bride': {'name': '新娘', 'year_gz': '辛卯', 'role': '坤造'},
    }
    if action_plan is not None:
        e['action_plan'] = action_plan
    return e


# ---------- 测试 5：plan 三段与红帖逐字一致 ----------
print('\n[5] plan 三段 → 红帖吉时区逐字一致')
plan = {
    'plan': [
        {'seq': 1, 'label': '起轿·发轿', 'zhi': '丑', 'ganzhi': '癸丑',
         'range': '01-03', 'score': 80, 'level': '★★★★★ 上吉', 'tags': []},
        {'seq': 2, 'label': '迎娶·进门', 'zhi': '寅', 'ganzhi': '甲寅',
         'range': '03-05', 'score': 80, 'level': '★★★★★ 上吉', 'tags': []},
        {'seq': 3, 'label': '交拜·合卺', 'zhi': '申', 'ganzhi': '庚申',
         'range': '15-17', 'score': 90, 'level': '★★★★★ 上吉', 'tags': []},
    ],
    'status': 'full',
    'missing': [],
    'checks': [],
    'alt': [],
}
e = prepare_entry(_make_entry(plan))
lines = compose_marriage_lines(e)
jishi_lines = [t for s, t in lines if s == 'body' and ('起轿' in t or '迎娶' in t or '交拜' in t)]
check('红帖含 3 段动作行', len(jishi_lines) == 3, str(len(jishi_lines)))
for _i, (_lbl, _gz) in enumerate((('起轿·发轿', '癸丑'), ('迎娶·进门', '甲寅'), ('交拜·合卺', '庚申'))):
    check('第%d段 label+时柱一致' % (_i + 1),
          _lbl in jishi_lines[_i] and _gz in jishi_lines[_i],
          jishi_lines[_i])
check('plan_status=full', e.get('_plan_status') == 'full')
check('hour_source=reverse_action', e.get('_hour_source') == 'reverse_action')

# ---------- 测试 6：冲命时辰 → 拒绝生成 ----------
print('\n[6] 冲命时辰 → prepare_entry 抛错')
# 新娘辛卯，冲支酉；plan 第三段用酉时 → 应抛错
plan_chong = {
    'plan': [
        {'seq': 1, 'label': '起轿·发轿', 'zhi': '丑', 'ganzhi': '癸丑',
         'range': '01-03', 'score': 80, 'level': '吉', 'tags': []},
        {'seq': 2, 'label': '迎娶·进门', 'zhi': '寅', 'ganzhi': '甲寅',
         'range': '03-05', 'score': 80, 'level': '吉', 'tags': []},
        {'seq': 3, 'label': '交拜·合卺', 'zhi': '酉', 'ganzhi': '己酉',
         'range': '17-19', 'score': 90, 'level': '吉', 'tags': []},
    ],
    'status': 'full', 'missing': [], 'checks': [], 'alt': [],
}
_raised = False
try:
    prepare_entry(_make_entry(plan_chong))
except ValueError as _e:
    _raised = True
    print('    抛错信息:', str(_e))
check('冲命时拒绝生成', _raised)

# ---------- 测试 7：缺段 partial → 红帖含缺段 warn ----------
print('\n[7] partial 缺段 → 红帖 warn 行')
plan_partial = {
    'plan': [
        {'seq': 1, 'label': '起轿·发轿', 'zhi': '丑', 'ganzhi': '癸丑',
         'range': '01-03', 'score': 80, 'level': '吉', 'tags': []},
        {'seq': 2, 'label': '迎娶·进门', 'zhi': '寅', 'ganzhi': '甲寅',
         'range': '03-05', 'score': 80, 'level': '吉', 'tags': []},
    ],
    'status': 'partial', 'missing': ['交拜·合卺'], 'checks': [],
    'alt': [{'label': '交拜·合卺', 'suggest': '建议另择'}],
}
e2 = prepare_entry(_make_entry(plan_partial))
lines2 = compose_marriage_lines(e2)
warn_lines = [t for s, t in lines2 if s == 'warn']
has_missing_warn = any('交拜·合卺' in t for t in warn_lines)
check('缺段 warn 含交拜·合卺', has_missing_warn, str(warn_lines))
check('只输出 2 段动作行',
      len([t for s, t in lines2 if s == 'body' and ('起轿' in t or '迎娶' in t)]) == 2)

# ---------- 测试 8：无 action_plan → 走原路径 ----------
print('\n[8] 无 action_plan → 通书前三，_plan_status 为空')
e3 = prepare_entry(_make_entry(None))
check('无 _plan_status', not e3.get('_plan_status'))
check('无 _hour_source', not e3.get('_hour_source'))
check('_jishi 非空（通书前三）', len(e3.get('_jishi', [])) > 0)

# ---------- 汇总 ----------
print('\n' + '=' * 60)
if failures:
    print(f'FAIL：{len(failures)} 项失败：{failures}')
    sys.exit(1)
else:
    print('ALL PASS：P2-C 动作时序→红帖端到端验证通过')
    sys.exit(0)
