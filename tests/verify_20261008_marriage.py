# -*- coding: utf-8 -*-
"""verify：嫁娶路径口径校准（2026-10-08 拍板：裁定1=B/2删宜/3=C/4各自计分/新增1）。

走产品真实入口：Scorer.score()、lint_lesson()、常量表单；
黄金日期/分值取自本轮审计真实管线结果与拍板，不反推实现。
退出码 0=全过。
"""
import sys, io, datetime as dt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer
from modules.日课校验器 import lint_lesson

FAILS = []
def check(name, cond):
    if not cond:
        FAILS.append(name)
        print(f'  FAIL: {name}')

OWNERS = [
    {'name': '欢', 'role': '新娘', '性别': '女', 'birth_date': '1999-04-05'},
    {'name': '文旺', 'role': '新郎', '性别': '男', 'birth_date': '1998-10-13'},
]

def score_date(ds):
    d = dt.date.fromisoformat(ds)
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d; sz['year'] = d.year; sz['month'] = d.month; sz['day'] = d.day
    return Scorer().score(sz, '嫁娶', owners=OWNERS)

# ===== A. 两级降格真实评分 =====
print('A. 两级降格')
r_l1 = score_date('2026-02-22')   # 建除除日 → 一级
check('A1 除日 level含犯忌嫁娶', '犯忌嫁娶' in str(r_l1['level']))
check('A2 除日 reason含降格说明', '降格' in str(r_l1['reason']))

r_l2 = score_date('2024-03-02')   # 建除闭日 → 二级
check('A3 闭日 level含降一格', '降一格' in str(r_l2['level']))
check('A4 闭日 yi不含嫁娶', '嫁娶' not in (r_l2['yi_list'] or []))
check('A5 闭日 reason含降星说明', '降星' in str(r_l2['reason']))

# 普通无调整日（动态找一个，保证断言不建立在错误前提上）
r_none = None
_d = dt.date(2024, 1, 1)
while _d <= dt.date(2024, 1, 31):
    sz = calculate_sizhu(_d, 12, 0)
    sz['date'] = _d; sz['year'] = _d.year; sz['month'] = _d.month; sz['day'] = _d.day
    _r = Scorer().score(sz, '嫁娶', owners=OWNERS)
    if '犯忌嫁娶' not in str(_r['level']) and '降一格' not in str(_r['level']):
        r_none = _r
        break
    _d += dt.timedelta(days=1)
check('A6 存在无调整对照日', r_none is not None)

# ===== B. E206 要求类/事实类 =====
print('B. E206 拆分')
_d_req = {'reason': '综合判断：建除闭日须避，然天德并见，嫁娶可用，须有制化'}
_lr = lint_lesson(_d_req)
check('B1 须有制化不再放行(E206有issue)',
      any(i.rule_id == 'E206' for i in _lr.issues))

_d_fact = {'reason': '综合判断：建除闭日须避，然天德并见，嫁娶可用，巳火合住申金'}
_lr2 = lint_lesson(_d_fact)
check('B2 合住属既成事实放行(无E206 issue)',
      not any(i.rule_id == 'E206' for i in _lr2.issues))
check('B3 事实类跳过文案',
      any(rid == 'E206' and '既成制化' in rs for rid, rs in _lr2.skipped))

# ===== C. E207 嫁娶跳过 / 通用对账 =====
print('C. E207')
_lr_m = lint_lesson(r_l2)
check('C1 嫁娶路径E207明确跳过',
      any(rid == 'E207' and '嫁娶路径不适用' in rs for rid, rs in _lr_m.skipped))

_good = {'sizhu': {'年柱': '甲子', '月柱': '乙丑', '日柱': '丙寅', '时柱': '癸亥'},
         'wu_xing_result': {'score_breakdown': {'地支关系得分': 12}}}
# 独立重算：子丑六合+8；寅亥六合+8又相破-4（破对：寅亥），合计+12
_lr_g = lint_lesson(_good)
check('C2 通用路径恒等式相符(无E207 issue)',
      not any(i.rule_id == 'E207' for i in _lr_g.issues))
_bad = dict(_good)
_bad['wu_xing_result'] = {'score_breakdown': {'地支关系得分': 0}}
_lr_b = lint_lesson(_bad)
check('C3 通用路径恒等式不符报issue(反向)',
      any(i.rule_id == 'E207' for i in _lr_b.issues))

# ===== D. E105 两级说明检查 =====
print('D. E105')
_lr_noexp = lint_lesson(r_l2, rendered_content='等级行：★ 平（小忌，降一格）')
check('D1 二级无降星说明报WARN',
      any(i.rule_id == 'E105' for i in _lr_noexp.issues))
_lr_exp = lint_lesson(r_l2, rendered_content='等级降星一档说明')
check('D2 二级有降星说明通过',
      not any(i.rule_id == 'E105' for i in _lr_exp.issues))
_lr_l1no = lint_lesson(r_l1, rendered_content='等级行：★ 平（犯忌嫁娶，慎用）')
check('D3 一级无降格说明报WARN',
      any(i.rule_id == 'E105' for i in _lr_l1no.issues))
_lr_l1ok = lint_lesson(r_l1, rendered_content='等级降格封顶说明')
check('D4 一级有降格说明通过',
      not any(i.rule_id == 'E105' for i in _lr_l1ok.issues))

# ===== E. 裁定2 表单口径 =====
print('E. 黄道表单')
from modules.黄道 import 黄道计算器 as _HC
check('E1 小黄道闭描述含忌嫁娶',
      '忌嫁娶' in _HC.XIAO_HUANG_DAO['闭']['description'])
check('E2 宜忌表闭.ji含嫁娶',
      '嫁娶' in _HC.XIAO_HUANG_DAO_YIJI['闭']['ji'])

# ===== F. _apply_marriage_level_caps 分级真值 =====
print('F. 两级方法')
rds = Scorer()
_lv, l1, l2 = rds._apply_marriage_level_caps(
    '★★★★ 大吉', {'details': [('小黄道执日忌嫁娶', -5)], 'warnings': []})
check('F1 一级封顶★平+注', _lv == '★ 平（犯忌嫁娶，慎用）' and l1 and not l2)
_lv, l1, l2 = rds._apply_marriage_level_caps(
    '★★★ 吉', {'details': [('小黄道闭日（黑道凶日）', -10)], 'warnings': []})
check('F2 二级降星中吉+注', _lv == '★★ 中吉（小忌，降一格）' and l2 and not l1)
_lv, l1, l2 = rds._apply_marriage_level_caps(
    '★★★ 吉', {'details': [('吉神', 5)], 'warnings': []})
check('F3 无调整原样返回', _lv == '★★★ 吉' and not l1 and not l2)
_lv, l1, l2 = rds._apply_marriage_level_caps(
    '❌ 凶', {'details': [('小黄道除日忌嫁娶', -5)], 'warnings': []})
check('F4 一级本凶保留凶+注', '❌ 凶' in _lv and '犯忌嫁娶' in _lv and l1)
_lv, l1, l2 = rds._apply_marriage_level_caps(
    '❌ 凶', {'details': [('小黄道闭日（黑道凶日）', -10)], 'warnings': []})
check('F5 二级本凶无处可降不记命中', _lv == '❌ 凶' and not l1 and not l2)
_lv, l1, l2 = rds._apply_marriage_level_caps(
    '★★ 中吉', {'details': [], 'warnings': ['阴阳差错日，忌嫁娶']})
check('F6 warnings忌嫁娶触发二级', '降一格' in _lv and l2)

print(f'\n==== {"ALL PASS" if not FAILS else "FAIL %d" % len(FAILS)} ====')
sys.exit(1 if FAILS else 0)
