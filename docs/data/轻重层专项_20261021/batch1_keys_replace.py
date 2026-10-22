# -*- coding: utf-8 -*-
"""轻重层批次1·SHENSHA_SCORES B组10项键值批量替换（一次性，带唯一性断言）。

拍板（001 §158）：月厌-25/月刑-20/月害-12/土王用事-20/受死日-15/月德合+15(通配)/
往亡-15/归忌-10/地囊-20/八专-12。本脚本只改注册键字面量；通配月德合键、
PENDING 集、兜底字面量、L4 标注由编辑器单独落地。
保字节纪律：newline='' 读写，除被替换片段外零字节变化；每模式断言恰 1 处。
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = 'modules/事项标准.py'
with open(P, 'r', encoding='utf-8', newline='') as f:
    src = f.read()

MAP = []


def add(ev, n, old, new):
    MAP.append(("('%s', '%s'): %d" % (ev, n, old), "('%s', '%s'): %d" % (ev, n, new)))


for ev in ['嫁娶', '修造', '动土', '拆舍', '入宅', '开业', '出行', '安床', '作灶', '移徙', '安葬']:
    add(ev, '月厌', -15, -25)          # B1
for ev in ['嫁娶', '修造', '动土', '拆舍', '开业', '出行', '安床', '作灶', '入学', '求医', '签约', '安葬', '*']:
    add(ev, '月刑', -15, -20)          # B2
for ev in ['嫁娶', '开业', '安床', '作灶', '求医', '签约', '安葬', '*']:
    add(ev, '月害', -15, -12)          # B7
for ev in ['嫁娶', '动土', '拆舍', '入宅', '出行', '安床', '移徙', '入学', '求医', '签约']:
    add(ev, '受死日', -22, -15)        # B4
for ev in ['嫁娶', '动土', '拆舍', '开业', '出行', '安床', '作灶', '求医', '安葬']:
    add(ev, '往亡', -20, -15)          # B6
for ev in ['嫁娶', '入宅', '出行', '移徙']:
    add(ev, '归忌', -15, -10)          # B8
for ev in ['修造', '动土', '拆舍']:
    add(ev, '地囊', -25, -20)          # B9
add('修造', '土王用事', -18, -20)      # B3
add('动土', '土王用事', -40, -20)      # B3
add('嫁娶', '八专', -15, -12)          # B10

cnt = 0
for old, new in MAP:
    n = src.count(old)
    assert n == 1, ('PATTERN_NOT_UNIQUE', old, n)
    src = src.replace(old, new)
    cnt += 1

with open(P, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
print('OK replaced %d keys（预期 61）' % cnt)
assert cnt == 61
