# -*- coding: utf-8 -*-
"""受死日收敛批独立验证（2026-10-20，001 §144）

判据：表A 逐月表（《陈子性藏书》p152 主条＋10 处月表互证）
      正戌、二辰、三亥、四巳、五子、六午、七丑、八未、九寅、十申、十一卯、十二酉
      （月支查日支）；分值 -15（轻重层批次1 001 §158 由 -22 调档）；全 15 通道统一。

验证面：
A. 表源层：基类 _is_shousi_day 源码（剥注释）为 12 键映射，无季节三合分组残留。
B. 谓词层：12×12＝144 组（月支×日支）逐组断言，每月仅 1 真、命中合计 12。
C. 子类一致性：入宅/嫁娶 _is_shousi 与基类 _is_shousi_day 144 组输出逐项相等。
D. 通道层：11 个保留通道 2026 全年受死日集合逐通道 == 表A（31 天）；
   反向断言表B（春戌夏丑秋辰冬未）独占的 28 天零命中。
D2. 删除层：开业/作灶/通用/安葬 四通道全年零发射；基类谓词仍在表A 31 天为真
   （删的是发射门控而非谓词）。
E. 发射层：保留 11 通道受死日恒 -15（批次1 调档）、单日至多 1 条、通道·天合计 341（11×31）。
F. 非复活：源码/键表内无「春戌」「夏丑」「秋辰」「冬未」作为受死日起例的活用法。
G. 键表层：三键已删（1265→1262；轻重层批次1 001 §158 增月德合通配键后总键数=1200），
   ('通用','受死日') 本不存在，四通道无分值兜底。
H. 总分基线：轻重层批次1（001 §158）受死日 -22→-15 等 B 组 10 项落地后，
   15 通道按实测值重冻（详见 H 段断言行；原 §144 删除批基线作废）。
I. 门控/墓碑源码在位：基类四事项门控、通用 `!= '通用'` 门控、开业/安葬墓碑。

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
SS = -15  # 轻重层批次1（001 §158）：受死日 -22→-15

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
print('\n[D/E] 保留 11 通道 2026 全年（hour=10）')
days = []
d = datetime.date(2026, 1, 1)
while d <= datetime.date(2026, 12, 31):
    days.append((d, calculate_sizhu(d, 10, 0)))
    d += datetime.timedelta(days=1)

KEEP11 = ['入宅', '移徙', '嫁娶', '动土', '修造', '拆舍', '出行', '安床',
          '入学', '求医', '签约']
DEL4 = ['开业', '作灶', '通用', '安葬']

a_set = {d for d, sz in days if sz['day_zhi'] == TABLE_A[sz['month_zhi']]}
b_set = {d for d, sz in days if sz['day_zhi'] == TABLE_B[sz['month_zhi']]}
check('D 表A 命中 31 天', len(a_set) == 31, len(a_set))
check('D 表B 命中 31 天、独占 28 天', len(b_set) == 31 and len(b_set - a_set) == 28)

total_ct = 0
for ev in KEEP11:
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
    check('E %s 受死日恒 -15、单日至多 1 条' % ev,
          scores == {SS} and dup == 0, (sorted(scores), dup))
    total_ct += len(hit)

check('E 保留 11 通道·天合计 341（11×31）', total_ct == 341, total_ct)

# ============ D2：删除四通道零发射 ============
print('\n[D2] 删除四通道零发射（开业/作灶/通用/安葬）')
tot_del = 0
for ev in DEL4:
    ck = get_checker(ev)
    hit = set()
    for d, sz in days:
        if any(s.get('name') == '受死日' for s in ck.check(sz, [])):
            hit.add(d)
    check('D2 %s 受死日全年零发射' % ev, not hit,
          sorted(str(x) for x in hit)[:3])
    tot_del += len(hit)
check('D2 删除四通道·天合计 0（原 124=4×31）', tot_del == 0, tot_del)
pred_hits = sum(1 for _, sz in days if base._is_shousi_day(sz))
check('D2 基类谓词在表A 31 天仍为真（门控非谓词删除）', pred_hits == 31, pred_hits)

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

# ============ G：键表层 ============
print('\n[G] 键表（三键已删；建除批次1 后 1199 → 福星批 001 §165 删 福星×14 键 =1185 → 福星正统落地批 001 §169 加回 =1199 → §172 P0 大清理删 岁害14/天耗13/地耗14/非嫁娶孤辰寡宿11 =1147 → 出行双通道割裂修复批 001 §183 新增 (出行,日破时) =1148）')
from modules.事项标准 import SHENSHA_SCORES, shensha_score  # noqa: E402

check('G 总键数=1154（§165 删 福星×14 键 → 1185；福星正统落地批 001 §169 加回 14 键 → 1199；§172 P0 大清理删 52 键 → 1147；出行双通道割裂修复批 001 §183 新增 (出行,日破时) → 1148；建除十二神×出行 D 专项 001 §184 新增 6 键（建/开+5、破-15、平/收/闭-5）→ 1154；实得 %d）' % len(SHENSHA_SCORES),
      len(SHENSHA_SCORES) == 1154)
for ev in ('开业', '作灶', '安葬'):
    check("G ('%s','受死日') 注册键已删" % ev,
          (ev, '受死日') not in SHENSHA_SCORES)
check("G ('通用','受死日') 键本不存在（通用靠发射值计分）",
      ('通用', '受死日') not in SHENSHA_SCORES)
check("G 无通配键 ('*','受死日')", ('*', '受死日') not in SHENSHA_SCORES)
for ev in DEL4:
    check("G shensha_score('%s','受死日')=None（无兜底）" % ev,
          shensha_score(ev, '受死日') is None)
for ev in KEEP11:
    if ev == '修造':
        check("G 修造无注册键、以发射值 -15 计分（批次1 兜底同步 -22→-15）",
              ('修造', '受死日') not in SHENSHA_SCORES
              and shensha_score('修造', '受死日') is None)
    else:
        got = shensha_score(ev, '受死日')
        check("G shensha_score('%s','受死日')=-15（实得 %s）" % (ev, got),
              got == -15 and (ev, '受死日') in SHENSHA_SCORES)

# ============ H：总分基线 ============
print('\n[H] §172 P0 大清理后总分基线（2026 全年，owners=[]，实测重冻）')
tot = {}
for ev in EV15:
    ck = get_checker(ev)
    tot[ev] = sum(s.get('score', 0) for _, sz in days for s in ck.check(sz, []))
# §172 重冻（2026-10-24）：岁害/天耗/地耗删除＋年家族 16 项置 0＋年支孤辰寡宿
# 删除＋大小耗伪链清除，全通道抬分合计 +100095（快照 docs/data/P0大清理_20261024/）。
for ev in DEL4:
    exp = {'开业': 12897, '作灶': 6444, '通用': 15607, '安葬': 3572}[ev]
    check('H %s 总分=%d（§172 P0 大清理重冻；实得 %d）'
          % (ev, exp, tot[ev]), tot[ev] == exp)
# 福星批（001 §165）：凡持键通道各 -310（2026 伪福星 31 天次×10，对拍探针实测）。
# §185（2026-10-26 向方禁忌批）：出行 12674→12374——D1 太岁方位谓词复活
# （原 _is_taisui_fangwei 硬编码 False 死链），午年 30 个午日×-10=-300。
# §187（2026-10-27 修造深水区修复批）：Q4 三煞忌事双扣根除后，修建三类
# （修造/动土/拆舍）全年总分各 +1410（三煞/杀师/临方项不再既走 sansha 通道
# 又重复落忌事 -15；三事项同构故增量全等）。入宅等其余通道不受影响。
for ev, exp in (('入宅', 11136), ('移徙', 11136), ('嫁娶', 6295),
                ('动土', 35), ('修造', 829), ('拆舍', -81),
                ('出行', 12374), ('安床', 11931), ('入学', 16444),
                ('求医', 15142), ('签约', 15592)):
    check('H 保留通道 %s 总分=%d（§172 P0 大清理重冻；§183 出行双通道割裂修复批 出行 -310 当日破时加分；§184 建除十二神×出行 D 专项 出行 13299→12674（6 星发射净 -625）；§185 D1 复活 出行 12674→12374；§187 Q4 修建三类三煞双扣根除各 +1410，实得 %d）'
          % (ev, exp, tot[ev]),
          tot[ev] == exp)

# ============ I：门控/墓碑源码层 ============
print('\n[I] 门控与墓碑（防复活）')
check("I 基类门控四事项元组在位",
      "('开业', '作灶', '通用', '安葬')" in src)
check("I 基类受死日活码仍在（受死日忌用；批次1 兜底 -22→-15）",
      "_add_shensha('受死日', -15, '受死日忌用')" in src)
gen = strip_comments(open(os.path.join(p_dir, '通用神煞.py'),
                          encoding='utf-8').read())
check("I 通用神煞 `!= '通用'` 门控在位",
      re.search(r"and getattr\(self, '_std_event', None\) != '通用'\):", gen)
      is not None)
check("I 通用神煞受死日活码仍在（入学/求医/签约）",
      "_add_shensha('受死日', -22, '受死之日，大忌')" in gen)
for fn in ('开业神煞.py', '安葬神煞.py'):
    s = strip_comments(open(os.path.join(p_dir, fn), encoding='utf-8').read())
    check('I %s 无活码受死日发射' % fn,
          "_add_shensha('受死日'" not in s)

print('\n' + '=' * 76)
print('FAIL %d 项' % len(FAILS))
for f in FAILS:
    print('  - ' + f)
print('ALL PASS' if not FAILS else 'HAS FAILURES')
sys.exit(0 if not FAILS else 1)
