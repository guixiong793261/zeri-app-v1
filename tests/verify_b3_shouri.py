# -*- coding: utf-8 -*-
"""
批3 F5 守日钦定口径重建 常驻 verify
==================================
F5 甲（批B）：《历例》原表"守日者春酉夏子秋卯冬午"经《协纪》钦定按语判为
"守与牢二字相近而讹易之……今从之"之牢日表；钦定守日＝春辰夏未秋戌冬丑
（四序土旺）。批B：建 is_shouri_by_zhi 单点出口 + _is_shouri 委托（暂不
注册发射），删 _is_shouriminri 死函数（王日表复制，零调用），清 3 悬空死键。

检查项：
  1. is_shouri_by_zhi 穷举 12 月×12 支硬锁（辰未戌丑）；
  2. 王/相/官/民/守五表两两零交集；
  3. 基类 _is_shouri 委托抽查（含空输入）；
  4. 不注册断言：全模块无 '守日' 发射点、事项标准无 ('X','守日') 活键；
  5. 复活反断言：无 def _is_shouriminri；_is_shouri 方法块仅委托。

用法：python tests/verify_b3_shouri.py
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
from modules.shensha.神煞基类 import (
    is_shouri_by_zhi, is_wangri_by_zhi, is_xiangri_by_zhi,
    is_guanri_by_zhi, is_minri_by_zhi,
)

SHOURI = {'寅': '辰', '卯': '辰', '辰': '辰',
          '巳': '未', '午': '未', '未': '未',
          '申': '戌', '酉': '戌', '戌': '戌',
          '亥': '丑', '子': '丑', '丑': '丑'}
ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']

bad = []
for m in ZHI:
    for d in ZHI:
        if is_shouri_by_zhi(m, d) != (d == SHOURI[m]):
            bad.append('守日 %s月%s' % (m, d))
check('1. 守日表穷举 12x12 硬锁（0误0漏）', not bad,
      '违例 %s' % bad[:6] if bad else '守日=春辰夏未秋戌冬丑（四序土旺，钦定从"守牢讹易……今从之"）')

# ── 2. 五表两两零交集 ────────────────────────────────────────────
WANG = {'寅': '寅', '卯': '寅', '辰': '寅', '巳': '巳', '午': '巳', '未': '巳',
        '申': '申', '酉': '申', '戌': '申', '亥': '亥', '子': '亥', '丑': '亥'}
XIANG = {'寅': '巳', '卯': '巳', '辰': '巳', '巳': '申', '午': '申', '未': '申',
         '申': '亥', '酉': '亥', '戌': '亥', '亥': '寅', '子': '寅', '丑': '寅'}
GUAN = {'寅': '卯', '卯': '卯', '辰': '卯', '巳': '午', '午': '午', '未': '午',
        '申': '酉', '酉': '酉', '戌': '酉', '亥': '子', '子': '子', '丑': '子'}
MINRI = {'寅': '午', '卯': '午', '辰': '午', '巳': '酉', '午': '酉', '未': '酉',
         '申': '子', '酉': '子', '戌': '子', '亥': '卯', '子': '卯', '丑': '卯'}
tables = {'守日': SHOURI, '王日': WANG, '相日': XIANG, '官日': GUAN, '民日': MINRI}
pairs = []
names = list(tables)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = names[i], names[j]
        clash = [(m, tables[a][m], tables[b][m]) for m in ZHI
                 if tables[a][m] == tables[b][m]]
        if clash:
            pairs.append('%s×%s 同月同支 %s' % (a, b, clash[:3]))
check('2. 王/相/官/民/守五表两两零交集', not pairs,
      '冲突 %s' % pairs if pairs else '五表月支查日支体系内无同位冲突')

# ── 3. 基类委托抽查 ──────────────────────────────────────────────
try:
    from modules.shensha.神煞基类 import ShenShaChecker
    ck = ShenShaChecker()
    probes = [
        ({'month_zhi': '寅', 'day_zhi': '辰'}, True),    # 春辰=守日
        ({'month_zhi': '巳', 'day_zhi': '未'}, True),    # 夏未=守日
        ({'month_zhi': '申', 'day_zhi': '戌'}, True),    # 秋戌=守日
        ({'month_zhi': '子', 'day_zhi': '丑'}, True),    # 冬丑=守日
        ({'month_zhi': '子', 'day_zhi': '子'}, False),   # 官日支非守日
        ({'month_zhi': '寅', 'day_zhi': '酉'}, False),   # 牢日原表支非守日
        ({'month_zhi': '', 'day_zhi': '辰'}, False),     # 空月支
        ({'month_zhi': '寅', 'day_zhi': ''}, False),     # 空日支
    ]
    fails = []
    for sz, exp in probes:
        if ck._is_shouri(sz) != exp:
            fails.append('%s→%s' % (sz, ck._is_shouri(sz)))
    check('3. 基类 _is_shouri 委托抽查 8 探针', not fails,
          '失败 %s' % fails if fails else '辰未戌丑生效、牢日原表支已断、空输入安全')
except Exception as e:
    check('3. 基类委托抽查', False, '异常 %r' % e)

# ── 4. 不注册断言 ────────────────────────────────────────────────
shensha_dir = ROOT / 'modules' / 'shensha'
emit = []
for f in sorted(shensha_dir.glob('*.py')):
    for i, ln in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
        s = ln.strip()
        if s.startswith('#'):
            continue
        if re.search(r"_add_shensha\(\s*['\"]守日['\"]", s):
            emit.append('%s:%d' % (f.name, i))
check('4a. 全模块无 \'守日\' 发射点（F5 甲不注册）', not emit,
      '违例 %s' % emit if emit else '守日谓词已建但不进入评分/展示')

std_src = (ROOT / 'modules' / '事项标准.py').read_text(encoding='utf-8')
live_keys = [ln for ln in std_src.splitlines()
             if re.match(r"^\s*\(\s*'[^']+'\s*,\s*'守日'\s*\)", ln)]
check('4b. 事项标准无 (X,守日) 活键（3 死键已清）', not live_keys,
      '残留 %s' % live_keys[:3] if live_keys else '入学/求医/签约 三悬空键已删')

# ── 5. 复活反断言 ────────────────────────────────────────────────
revived = []
for f in sorted(shensha_dir.glob('*.py')):
    if re.search(r'^\s*def _is_shouriminri\(', f.read_text(encoding='utf-8'), re.M):
        revived.append(f.name)
check('5a. def _is_shouriminri 零复活', not revived,
      '违例 %s' % revived if revived else '王日表复制死函数已删')

base_src = (shensha_dir / '神煞基类.py').read_text(encoding='utf-8')
lines = base_src.splitlines()
block, grab = [], False
for ln in lines:
    if ln.startswith('    def _is_shouri('):
        grab = True
    elif grab and ln.startswith('    def '):
        break
    if grab:
        block.append(ln)
block_txt = '\n'.join(block)
ok5 = bool(block_txt) and 'is_shouri_by_zhi' in block_txt and 'in [' not in block_txt
check('5b. _is_shouri 方法块仅委托（无内联查表）', ok5,
      '块缺失或结构不符' if not ok5 else '单点委托 is_shouri_by_zhi')

print('=' * 72)
print('批3 F5 守日 verify：%s' % ('全部通过 PASS' if PASS else '存在失败 FAIL'))
sys.exit(0 if PASS else 1)
