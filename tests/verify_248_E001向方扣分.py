# -*- coding: utf-8 -*-
"""001 §248：E001 必须同源汇总「向方扣分」等附加分项（2026-11-10）。

背景：修造·乾山巽向兼亥（2021-11-12 辛丑 己亥 甲子 丙寅）实测
  五行272 + 月令5 + 喜用17 + 相主-13 + 黄道-10 + 太阳太阴0 + 三煞-13
  + 向方扣分-20 = 238，
而 E001 只汇总前七项得 258，误报 ERROR「总分与分项和不一致」，
导致整份日课详情被标「未通过日课校验，不应直接交付」。

A. 正向：该案例 lint 无 E001，has_error=False
B. 反向：人为把总分改大 10 分，E001 必须重新触发（防规则被弱化成恒真）
C. 源码锚点：E001 可选分项集合含四项附加键
"""
import copy
import io
import os
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
from modules.日课校验器 import lint_lesson

FAILS = []


def check(cond, label, detail=''):
    print('  [%s] %s%s' % ('PASS' if cond else 'FAIL', label,
                          ('  | ' + str(detail)) if detail and not cond else ''))
    if not cond:
        FAILS.append(label)


def _e001(res):
    return [i for i in (getattr(res, 'issues', None) or [])
            if getattr(i, 'rule_id', '') == 'E001']


def _case():
    sz = calculate_sizhu((2021, 11, 12), 4, 0, longitude=120)
    sz['year'], sz['month'], sz['day'] = 2021, 11, 12
    own = [{'name': '贵才', 'role': '福主', '生肖': '丑', '日支': '酉'},
           {'name': '贵林', 'role': '福主', '生肖': '未'}]
    r = calculate_score(sz, '修造', owners=[dict(o) for o in own],
                        shan_xiang='乾山巽向兼亥', zeli_mode='pure')
    r['event_type'] = '修造'
    r['shan_xiang'] = '乾山巽向兼亥'
    return r


print('[A] 正向：向方扣分参与恒等式')
r = _case()
sd = r.get('score_details') or {}
check(int(sd.get('向方扣分') or 0) != 0, 'A1 本案例确含向方扣分（-20）',
      sd.get('向方扣分'))
_base = sum(int(sd.get(k) or 0) for k in
            ('五行评分', '月令得分', '喜用神得分', '相主得分', '黄道得分',
             '太阳太阴得分', '三煞扣分'))
check(int(sd.get('总分') or 0) != _base,
      'A2 旧七项和与总分本就不等（缺陷前置条件）', (_base, sd.get('总分')))
res = lint_lesson(r, {})
check(not _e001(res), 'A3 E001 不再误报', [i.message for i in _e001(res)])
check(getattr(res, 'has_error', True) is False, 'A4 has_error=False（可交付）')

print('\n[B] 反向：恒等式被破坏时仍须报错')
bad = copy.deepcopy(r)
bad['score_details'] = dict(bad.get('score_details') or {})
bad['score_details']['总分'] = int(bad['score_details'].get('总分') or 0) + 10
bad['score'] = bad['score_details']['总分']
_res2 = lint_lesson(bad, {})
check(bool(_e001(_res2)), 'B1 总分人为 +10 后 E001 触发', len(_e001(_res2)))

print('\n[C] 源码锚点')
with open(os.path.join(ROOT, 'modules', '日课校验器.py'), encoding='utf-8') as f:
    _src = f.read()
for _k in ('向方扣分', '出行方位得分', '仙命坐山得分', '仙命冲坐山六冲'):
    check("'%s'" % _k in _src, 'C1 E001 可选分项含「%s」' % _k)

print('\n' + ('ALL PASS' if not FAILS else 'FAIL %d：%s' % (len(FAILS), '；'.join(FAILS))),
      flush=True)
sys.exit(0 if not FAILS else 1)
