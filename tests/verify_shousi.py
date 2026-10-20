# -*- coding: utf-8 -*-
"""受死日收敛批独立验证（2026-10-20，001 §144）

判据：表A 逐月表（《陈子性藏书》p152 主条＋10 处月表互证）
      正戌、二辰、三亥、四巳、五子、六午、七丑、八未、九寅、十申、十一卯、十二酉
      （月支查日支）；分值 -22；全 15 通道统一。

验证面：
A. 表源层：基类 _is_shousi_day 源码（剥注释）为 12 键映射，无季节三合分组残留。
B. 谓词层：12×12＝144 组（月支×日支）逐组断言，每月仅 1 真、命中合计 12。
C. 子类一致性：入宅/嫁娶 _is_shousi 与基类 _is_shousi_day 144 组输出逐项相等。
D. 通道层：15 通道 2026 全年受死日集合逐通道 == 表A（31 天）；
   反向断言表B（春戌夏丑秋辰冬未）独占的 28 天零命中。
E. 发射层：15 通道受死日恒 -22、单日至多 1 条、通道·天合计 465（15×31）。
F. 非复活：源码/键表内无「春戌」「夏丑」「秋辰」「冬未」作为受死日起例的活用法。

退出码：0=全过 1=有失败（FAIL N 计数）
================================================================================
"""
import datetime
import io
import os
import re
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu      # noqa: E402
from modules.shensha import get_checker            # noqa: E402

TABLE_A = {'寅': '戌', '卯': '辰', '辰': '亥', '巳': '巳',
           '午': '子', '未': '午', '申': '丑', '酉': '未',
           '戌': '寅', '亥': '申', '子': '卯', '丑': '酉'}
TABLE_B = {'寅': '戌', '卯': '戌', '辰': '戌', '巳': '丑', '午': '丑',
           '未': '丑', '申': '辰', '酉': '辰', '戌': '辰', '亥': '未',
           '子': '未', '丑': '未'}
ZHI = list(TABLE_A)
EV15 = ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '开业',
        '安床', '作灶', '安葬', '入学', '求医', '签约', '通用']
SS = -22

FAILS = []


def check(name, cond, detail=''):
    if cond:
        print('  PASS  ' + name)
    else:
        print('  FAIL  ' + name + ('  -> ' + str(detail) if detail else ''))
        FAILS.append(name)


def strip_comments(src):
    out = []
    for line in src.splitlines():
        s = line.split('#', 1)[0]
        if s.strip():
            out.append(s)
    return '\n'.join(out)


print('=' * 76)
print('受死日收敛批验证（001 §144）')
print('=' * 76)

# ============ A：表源层 ============
print('\n[A] 基类表源（12 键映射，季节分组已消失）')
p_base = os.path.join(ROOT, 'modules', 'shensha', '神煞基类.py')
src = strip_comments(open(p_base, encoding='utf-8').read())
m = re.search(r'def _is_shousi_day\(self, sizhu\):(.*?)(?=\n    def )', src, re.S)
body = m.group(1) if m else ''
check('A _is_shousi_day 定义在位', bool(m))
check('A 映射含 12 个月支键', all(("'%s': '%s'" % (k, v)) in body
                                  for k, v in TABLE_A.items()),
      [k for k, v in TABLE_A.items() if "'%s': '%s'" % (k, v) not in body])
check("A 无季节三合分组残留（['寅', '卯', '辰'] 等）",
      not re.search(r"in \['寅', '卯', '辰'\]|in \['巳', '午', '未'\]"
                    r"|in \['申', '酉', '戌'\]|in \['亥', '子', '丑'\]", body))
check('A 表A 用满 12 日支（逐月表），表B 仅 4 日支（季节三合表）',
      len(set(TABLE_A.values())) == 12 and set(TABLE_B.values()) == {'戌', '丑', '辰', '未'})

# ============ B：谓词层 144 组 ============
print('\n[B] 谓词层 144 组（12 月支 × 12 日支）')
from modules.shensha.神煞基类 import ShenShaChecker  # noqa: E402

base = ShenShaChecker.__new__(ShenShaChecker)
bad = []
for mz in ZHI:
    hits = []
    for dz in ZHI:
        got = base._is_shousi_day({'month_zhi': mz, 'day_zhi': dz})
        exp = (dz == TABLE_A[mz])
        if got != exp:
            bad.append((mz, dz, got, exp))
        if got:
            hits.append(dz)
    if hits != [TABLE_A[mz]]:
        bad.append(('月' + mz, '每月唯一真', hits, [TABLE_A[mz]]))
check('B 144 组逐组与表A 一致', not bad, bad[:4])
check('B 每月恰 1 真、12 月合计 12',
      sum(1 for mz in ZHI for dz in ZHI
          if base._is_shousi_day({'month_zhi': mz, 'day_zhi': dz})) == 12)

# ============ C：子类一致性 ============
print('\n[C] 子类 _is_shousi 与基类同表同集合')
from modules.shensha.入宅神煞 import RuZhaiShenShaChecker   # noqa: E402
from modules.shensha.嫁娶神煞 import MarriageShenShaChecker  # noqa: E402

for cls, label in ((RuZhaiShenShaChecker, '入宅'), (MarriageShenShaChecker, '嫁娶')):
    obj = cls.__new__(cls)
    diffs = [(mz, dz) for mz in ZHI for dz in ZHI
             if obj._is_shousi({'month_zhi': mz, 'day_zhi': dz})
             != base._is_shousi_day({'month_zhi': mz, 'day_zhi': dz})]
    check('C %s 子类与基类 144 组逐项相等' % label, not diffs, diffs[:4])

# ============ D/E：通道层 ============
print('\n[D/E] 15 通道 2026 全年（hour=10）')
days = []
d = datetime.date(2026, 1, 1)
while d <= datetime.date(2026, 12, 31):
    days.append((d, calculate_sizhu(d, 10, 0)))
    d += datetime.timedelta(days=1)

a_set = {d for d, sz in days if sz['day_zhi'] == TABLE_A[sz['month_zhi']]}
b_set = {d for d, sz in days if sz['day_zhi'] == TABLE_B[sz['month_zhi']]}
check('D 表A 命中 31 天', len(a_set) == 31, len(a_set))
check('D 表B 命中 31 天、独占 28 天', len(b_set) == 31 and len(b_set - a_set) == 28)

total_ct = 0
for ev in EV15:
    ck = get_checker(ev)
    hit, scores, dup = set(), set(), 0
    for d, sz in days:
        rows = [s for s in ck.check(sz, []) if s.get('name') == '受死日']
        if rows:
            hit.add(d)
            if len(rows) > 1:
                dup += 1
            scores.update(s.get('score') for s in rows)
    check('D %s 受死日集合 == 表A（31 天）' % ev, hit == a_set,
          '仅表B:%d 漏表A:%d' % (len(hit & (b_set - a_set)), len(a_set - hit)))
    check('D %s 表B 独占日零命中（28 天）' % ev, not (hit & (b_set - a_set)),
          sorted(str(x) for x in (hit & (b_set - a_set)))[:3])
    check('E %s 受死日恒 -22、单日至多 1 条' % ev,
          scores == {SS} and dup == 0, (sorted(scores), dup))
    total_ct += len(hit)

check('E 通道·天合计 465（15×31）', total_ct == 465, total_ct)

# ============ F：非复活 ============
print('\n[F] 受死日谓词内表B 不得复活（只扫 _is_shousi* 函数体）')
hits = []
found = []
p_dir = os.path.join(ROOT, 'modules', 'shensha')
for fn in sorted(os.listdir(p_dir)):
    if not fn.endswith('.py'):
        continue
    s = strip_comments(open(os.path.join(p_dir, fn), encoding='utf-8').read())
    for m in re.finditer(r'def _is_shousi\w*\(self[^)]*\):(.*?)(?=\n    def |\n\ndef |\Z)',
                         s, re.S):
        body = m.group(1)
        found.append(fn)
        for pat in ("'卯': '戌'", "'辰': '戌'", "'亥': '未'", "'子': '未'"):
            if pat in body:
                hits.append('%s:%s' % (fn, pat))
        if re.search(r"in \['寅', '卯', '辰'\]", body):
            hits.append(fn + ':季节分组')
check('F 找到受死日谓词 ≥3 处（基类/入宅/嫁娶）', len(found) >= 3, found)
check('F 谓词体内无表B 映射/季节分组残留', not hits, hits[:5])
check('F 未新增第 4 个受死日谓词（防多实现再分叉）', len(found) == 3, found)

print('\n' + '=' * 76)
print('FAIL %d 项' % len(FAILS))
for f in FAILS:
    print('  - ' + f)
print('ALL PASS' if not FAILS else 'HAS FAILURES')
sys.exit(0 if not FAILS else 1)
