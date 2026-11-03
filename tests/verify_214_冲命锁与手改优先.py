# -*- coding: utf-8 -*-
"""001 §214 C1：手动改吉时的冲命锁与优先级（S3-8 / S3-9）。

A. 手动改时命中禁用清单（冲新娘）→ ValueError 拒绝生成
B. 手动修改优先于 action_plan，缺失段按覆盖后重算
退出码：0 全过；1 有失败。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.择日贴 import prepare_entry

FAILS = []


def check(name, cond, detail=''):
    ok = bool(cond)
    print('[%s] %s%s' % ('PASS' if ok else 'FAIL', name,
                        ('  → ' + str(detail)) if detail and not ok else ''))
    if not ok:
        FAILS.append(name)


# 新娘属猪 → 年支亥 → 冲巳（D4 红线样本）
OWNERS = [{'name': '新娘', 'role': '新娘', 'year_sx': '猪', '性别': '女'},
          {'name': '新郎', 'role': '新郎', 'year_sx': '狗', '性别': '男'}]
BASE = {'date': '2026-10-20', 'event_type': '嫁娶', 'score': 88, 'level': '吉',
        'owners_list': OWNERS}


def _expect_error(entry, label):
    try:
        prepare_entry(dict(entry))
    except ValueError as ex:
        print('  [PASS] %s → ValueError：%s' % (label, ex))
        return
    check(label, False, '未抛 ValueError，非法时辰被直接采纳')


# ===== A. S3-8 =====
_expect_error(dict(BASE, jishi_override={'0': '巳'}), 'S3-8 冲新娘时支「巳」拒绝生成')
_expect_error(dict(BASE, jishi_override={'0': '不存在的时辰'}),
              'S3-8 非法时辰「不存在的时辰」拒绝生成')

_e = prepare_entry(dict(BASE, jishi_override={'0': '午'}))
_got = (_e['_jishi'] or [{}])[0]
check('S3-8 合法手改时辰「午」被采纳且打 manual 标',
      _got.get('zhi') == '午' and bool(_got.get('manual')), _got)

_auto = prepare_entry(dict(BASE))
check('S3-8 反向：自动前三吉时不含冲新娘「巳」',
      all(_j.get('zhi') != '巳' for _j in (_auto['_jishi'] or [])),
      [_j.get('zhi') for _j in (_auto['_jishi'] or [])])

# ===== B. S3-9 =====
_PLAN = {
    'plan': [
        {'seq': 1, 'label': '起轿·发轿', 'zhi': '卯', 'ganzhi': '丁卯',
         'range': '05-07', 'score': 80, 'level': '吉', 'tags': []},
        {'seq': 2, 'label': '迎娶·进门', 'zhi': '', 'ganzhi': '',
         'range': '', 'score': 0, 'level': '', 'tags': []},
        {'seq': 3, 'label': '交拜·合卺', 'zhi': '', 'ganzhi': '',
         'range': '', 'score': 0, 'level': '', 'tags': []},
    ],
    'status': 'partial', 'missing': ['迎娶·进门', '交拜·合卺'], 'checks': [], 'alt': [],
}
_e2 = prepare_entry(dict(BASE, action_plan=_PLAN,
                         jishi_override={'0': '午', '1': '申', '2': '戌'}))
_segs = _e2['_jishi'] or []
check('S3-9 手改优先：plan 首段卯被手改午覆盖',
      len(_segs) >= 1 and _segs[0].get('zhi') == '午' and bool(_segs[0].get('manual')),
      _segs[:3])
check('S3-9 手改补齐缺段后 missing 重算为空',
      _e2.get('_plan_missing') == [], _e2.get('_plan_missing'))
check('S3-9 缺段补齐后状态由 partial 升为 full',
      _e2.get('_plan_status') == 'full', _e2.get('_plan_status'))
check('S3-9 手改来源打标 reverse_action_manual',
      _e2.get('_hour_source') == 'reverse_action_manual', _e2.get('_hour_source'))

_expect_error(dict(BASE, action_plan=_PLAN, jishi_override={'1': '巳'}),
              'S3-9 反向：plan 在场时手改冲命「巳」仍拒绝')

print('\n' + ('ALL PASS' if not FAILS else 'FAIL %d：%s' % (len(FAILS), '；'.join(FAILS))))
sys.exit(0 if not FAILS else 1)
