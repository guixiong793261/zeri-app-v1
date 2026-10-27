# -*- coding: utf-8 -*-
"""
批4 E3 吉期修正常驻 verify
==================================
E3 吉期：《协纪》卷六·义例四"吉期【兵宝】"条《历例》曰"常居月建前一辰也"
  （《考原》逐字同载零分歧；兵宝同条起例互证），即日支取月支后一辰
  （寅月卯、卯月辰……丑月寅）。旧内联表 {寅卯,卯亥,辰酉,巳丑,午亥,未酉,
  申丑,酉卯,戌亥,亥酉,子丑,丑卯} 12 值中仅寅/戌/子三月与新表巧合重合，
  其余 9 个月全部失准，docstring 自录口诀三库无载——"错误制度化"
  第四例（王日夏支窜用、相日两支版、要安月厌同表之后）。
  批4 E3 改模块级 _JIQI_ZHI_BY_MONTH 单点出口。

检查项：
  1. 模块级 is_jiqi_by_zhi 穷举 12 月×12 支硬锁口诀（月建前一辰）；
  2. 基类 _is_jiqi 动态委托抽查 6 探针（含旧表点断开）；
  3. 2025-2026 全日穷举命中数区间断言（约 30 天/年）；
  4. 旧表复活反断言（方法块级：_is_jiqi 仅单点委托，无 jiqi_map 内联表）；
  5. 五处子类死链重加块零复活 + 墓碑在位（嫁娶/安葬/出行/安床/开业）；
  6. 全模块'吉期'发射位唯一性（仅神煞基类.py 月作用域 + 通用神煞.py
     自有月管线两处活链；_is_jiqi 谓词仅基类定义）。

用法：python tests/verify_b4_jiqi.py
退出码：0=全部通过  1=任一失败（CI 可挂）
"""
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PASS = True


def check(name, ok, detail=''):
    global PASS
    tag = 'PASS' if ok else 'FAIL'
    print('[%s] %s%s' % (tag, name, ('  ' + detail) if detail else ''))
    if not ok:
        PASS = False


# ── 1. 表值穷举硬锁 ──────────────────────────────────────────────
from modules.shensha.神煞基类 import is_jiqi_by_zhi

JIQI = {'寅': '卯', '卯': '辰', '辰': '巳', '巳': '午', '午': '未', '未': '申',
        '申': '酉', '酉': '戌', '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'}
OLD_TABLE = {'寅': '卯', '卯': '亥', '辰': '酉', '巳': '丑', '午': '亥', '未': '酉',
             '申': '丑', '酉': '卯', '戌': '亥', '亥': '酉', '子': '丑', '丑': '卯'}
ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']

bad = []
for m in ZHI:
    for d in ZHI:
        if is_jiqi_by_zhi(m, d) != (d == JIQI[m]):
            bad.append('吉期 %s月%s' % (m, d))
check('1. 吉期表穷举 12x12 硬锁（0误0漏）', not bad, '违例 %s' % bad[:6] if bad else
      '月建前一辰：寅月卯、卯月辰……丑月寅（《历例》"常居月建前一辰也"）')

# 旧表与新表同月同值仅寅/戌/子三月巧合（其余 9 个月失准；错表性质自证）
overlap = [m for m in ZHI if JIQI[m] == OLD_TABLE[m]]
check('1b. 旧表仅寅/戌/子三月巧合重合（其余 9 月失准）',
      overlap == ['寅', '戌', '子'],
      '重合月 %s' % overlap)

# ── 2. 基类委托抽查 ──────────────────────────────────────────────
try:
    from modules.shensha.神煞基类 import ShenShaChecker
    ck = ShenShaChecker()
    probes = [
        ({'month_zhi': '寅', 'day_zhi': '卯'}, True),    # 正月卯（新旧重合点）
        ({'month_zhi': '卯', 'day_zhi': '辰'}, True),    # 二月辰（修正点）
        ({'month_zhi': '丑', 'day_zhi': '寅'}, True),    # 十二月寅（循环闭合）
        ({'month_zhi': '卯', 'day_zhi': '亥'}, False),   # 旧表点，已断
        ({'month_zhi': '未', 'day_zhi': '酉'}, False),   # 旧表点，已断
        ({'month_zhi': '', 'day_zhi': '卯'}, False),     # 空月支防呆
    ]
    fails = []
    for sz, exp in probes:
        if ck._is_jiqi(sz) != exp:
            fails.append('%s→%s' % (sz, ck._is_jiqi(sz)))
    check('2. 基类 _is_jiqi 委托抽查 6 探针', not fails,
          '失败 %s' % fails if fails else '月建前一辰表生效，旧表点已断')
except Exception as e:
    check('2. 基类委托抽查', False, '异常 %r' % e)

# ── 3. 2025-2026 全日穷举命中数区间 ─────────────────────────────
from datetime import date, timedelta
d0, d1 = date(2025, 1, 1), date(2026, 12, 31)
nq = 0
try:
    from modules.四柱计算器 import calculate_sizhu
    d = d0
    while d <= d1:
        sz = calculate_sizhu(d, 12, 0)
        if is_jiqi_by_zhi(sz.get('month_zhi', ''), sz.get('day_zhi', '')):
            nq += 1
        d += timedelta(days=1)
    span = (d1 - d0).days + 1
    check('3. 2025-2026 穷举命中数区间', 25 <= nq / span * 365 <= 35,
          '吉期 %d 天 / %d 天（年率 %.1f）' % (nq, span, nq / span * 365))
except Exception as e:
    check('3. 全日穷举', False, '异常 %r' % e)

# ── 4. 旧表复活反断言（方法块级：_is_jiqi 必须为单点委托）────────
src = (ROOT / 'modules' / 'shensha' / '神煞基类.py').read_text(encoding='utf-8')


def _extract_method(src, name):
    """提取类方法源码块（def 行至下一个同缩进 def/文件尾）。"""
    lines = src.splitlines()
    out, grab = [], False
    for ln in lines:
        if ln.startswith('    def %s(' % name):
            grab = True
        elif grab and ln.startswith('    def '):
            break
        if grab:
            out.append(ln)
    return '\n'.join(out)


block = _extract_method(src, '_is_jiqi')
bad_blocks = []
if not block:
    bad_blocks.append('_is_jiqi 方法缺失')
else:
    if 'is_jiqi_by_zhi' not in block:
        bad_blocks.append('_is_jiqi 未委托 is_jiqi_by_zhi')
    if 'jiqi_map' in block or "{'" in block.replace("{'寅'", "''", 1):
        bad_blocks.append('_is_jiqi 残留内联查表结构')
# 模块级权威表在位且键值完整
mtable = re.search(r'_JIQI_ZHI_BY_MONTH\s*=\s*\{([^}]*)\}', src)
if not mtable:
    bad_blocks.append('模块级 _JIQI_ZHI_BY_MONTH 缺失')
else:
    keys = set(re.findall(r"'([寅卯辰巳午未申酉戌亥子丑])'\s*:\s*'([寅卯辰巳午未申酉戌亥子丑])'", mtable.group(1)))
    if len(keys) != 12 or dict(keys) != JIQI:
        bad_blocks.append('_JIQI_ZHI_BY_MONTH 表值与典载口诀不符')
check('4. 旧表复活反断言（仅委托、无内联表；模块级表 12 键全对）', not bad_blocks,
      bad_blocks[0] if bad_blocks else '_is_jiqi 单点委托 + _JIQI_ZHI_BY_MONTH 权威表在位')

# ── 5. 五处子类死链重加块零复活 + 墓碑在位 ───────────────────────
shensha_dir = ROOT / 'modules' / 'shensha'
FIVE = ['嫁娶神煞.py', '安葬神煞.py', '出行神煞.py', '安床神煞.py', '开业神煞.py']
resid = []
for fname in FIVE:
    txt = (shensha_dir / fname).read_text(encoding='utf-8')
    if re.search(r"self\._add_shensha\('吉期'", txt):
        resid.append('%s: 残留 吉期 发射行' % fname)
    if re.search(r'^    def _is_jiqi\(', txt, re.M):
        resid.append('%s: 残留 _is_jiqi 子类重写' % fname)
    if '批4（001 §74）：' not in txt or "'吉期' 重加删除" not in txt:
        resid.append('%s: 墓碑缺失' % fname)
check('5. 五处死链重加块零复活 + 墓碑在位', not resid,
      '违例 %s' % resid[:5] if resid else '嫁娶/安葬/出行/安床/开业 均已收口')

# ── 6. 全模块'吉期'发射位与谓词唯一性 ────────────────────────────
emit_sites = []
for f in sorted(shensha_dir.glob('*.py')):
    txt = f.read_text(encoding='utf-8')
    n = len(re.findall(r"self\._add_shensha\('吉期'", txt))
    if n:
        emit_sites.append('%s x%d' % (f.name, n))
    if f.name != '神煞基类.py' and re.search(r'^    def _is_jiqi\(', txt, re.M):
        emit_sites.append('%s: def _is_jiqi（子类重写）' % f.name)
sites_ok = sorted(emit_sites) == sorted(['神煞基类.py x1', '通用神煞.py x1'])
check('6. 吉期发射位唯一性（基类月作用域 + 通用月管线两处活链；谓词仅基类定义）', sites_ok,
      '发射位 %s' % emit_sites if not sites_ok else '通用神煞.py L183-184 活链保留（自有月管线）')

print('=' * 72)
print('批4 E3 verify：%s' % ('全部通过 PASS' if PASS else '存在失败 FAIL'))
sys.exit(0 if PASS else 1)
