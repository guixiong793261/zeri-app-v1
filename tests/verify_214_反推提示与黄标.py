# -*- coding: utf-8 -*-
"""001 §214 C2：反推零候选强提示与「缺上轿吉时」黄标（S3-2 / S3-6）。

UI 无消息循环时不实例化窗口，按源码接线断言：
  C. 零候选必须走「无可用吉日」显式提示 + messagebox 弹窗
  D. partial 且缺段含发轿/起轿 → 事件级黄标「缺上轿吉时」
退出码：0 全过；1 有失败。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []


def check(name, cond, detail=''):
    ok = bool(cond)
    print('[%s] %s%s' % ('PASS' if ok else 'FAIL', name,
                        ('  → ' + str(detail)) if detail and not ok else ''))
    if not ok:
        FAILS.append(name)


_src = open(os.path.join(ROOT, 'modules', '反推UI.py'), encoding='utf-8').read()

check('S3-2 零候选显式提示已接线（无可用吉日 + messagebox）',
      '无可用吉日' in _src and 'messagebox.showwarning' in _src)
check('S3-2 空榜分支给出可执行指引（扩大日期范围/调整山向）',
      '没有符合条件且能避开冲煞的可用吉日' in _src
      and '扩大日期范围' in _src and '调整山向/事主信息' in _src)
check('S3-6 事件级黄标「缺上轿吉时」已接线',
      '缺上轿吉时' in _src and "('发轿' in x or '起轿' in x)" in _src)

# 反向：不得把提示藏在通用文案里（缺上轿分支必须真的存在条件与文案）
check('S3-6 反向：通用文案之外存在 partial+发轿 专用分支',
      "_status == 'partial' and any" in _src)

print('\n' + ('ALL PASS' if not FAILS else 'FAIL %d：%s' % (len(FAILS), '；'.join(FAILS))))
sys.exit(0 if not FAILS else 1)
