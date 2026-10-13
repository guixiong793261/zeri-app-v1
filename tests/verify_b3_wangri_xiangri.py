# -*- coding: utf-8 -*-
"""
批3 E1/E2 王日·相日修正常驻 verify
==================================
E2 王日：《历例》"王日者春寅夏巳秋申冬亥"钦定从旧说（三合临官阳支），
  原夏支午＝官日夏支窜用，批3 改夏巳。
E1 相日：《历例》"相日者春巳夏申秋亥冬寅"一支版（按语阳支为相），
  原两支版（当季王+官二支）三库无载，批3 改一支版。

检查项：
  1. 模块级 is_wangri_by_zhi / is_xiangri_by_zhi 穷举 12 月×12 支硬锁口诀；
  2. 王/相/官/民四表逐月取值两两零交集（防同位双扣/交叉污染）；
  3. 基类 _is_wangri/_is_xiangri 动态导入抽查（委托生效）；
  4. 2025-2026 全日穷举命中数区间断言（王/相各约 33-37 天/年）；
  5. 旧表复活反断言（两支结构 `day_zhi in ['寅', '卯']` 等非注释行零出现）；
  6. 全模块谓词唯一性（王/旺/相/官/民谓词仅神煞基类.py 一处定义，
     子类重写=民间表复活通道，批A 已清 入宅 _is_xiangri / 嫁娶 _is_wangri）；
  7. 全模块内联查表反断言（xiangri_map/wangri_map 等民间表变量名零残留）。

用法：python tests/verify_b3_wangri_xiangri.py
退出码：0=全部通过  1=任一失败（CI 可挂）
"""
import sys
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
    is_wangri_by_zhi, is_xiangri_by_zhi,
    is_guanri_by_zhi, is_minri_by_zhi,
)

WANG = {'寅': '寅', '卯': '寅', '辰': '寅',
        '巳': '巳', '午': '巳', '未': '巳',
        '申': '申', '酉': '申', '戌': '申',
        '亥': '亥', '子': '亥', '丑': '亥'}
XIANG = {'寅': '巳', '卯': '巳', '辰': '巳',
         '巳': '申', '午': '申', '未': '申',
         '申': '亥', '酉': '亥', '戌': '亥',
         '亥': '寅', '子': '寅', '丑': '寅'}
ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']

bad = []
for m in ZHI:
    for d in ZHI:
        if is_wangri_by_zhi(m, d) != (d == WANG[m]):
            bad.append('王日 %s月%s' % (m, d))
        if is_xiangri_by_zhi(m, d) != (d == XIANG[m]):
            bad.append('相日 %s月%s' % (m, d))
check('1. 王/相表穷举 12x12 硬锁（0误0漏）', not bad, '违例 %s' % bad[:6] if bad else
      '王日=春寅夏巳秋申冬亥、相日=春巳夏申秋亥冬寅')

# ── 2. 四表两两零交集 ────────────────────────────────────────────
GUAN = {'寅': '卯', '卯': '卯', '辰': '卯', '巳': '午', '午': '午', '未': '午',
        '申': '酉', '酉': '酉', '戌': '酉', '亥': '子', '子': '子', '丑': '子'}
MINRI = {'寅': '午', '卯': '午', '辰': '午', '巳': '酉', '午': '酉', '未': '酉',
         '申': '子', '酉': '子', '戌': '子', '亥': '卯', '子': '卯', '丑': '卯'}
tables = {'王日': WANG, '相日': XIANG, '官日': GUAN, '民日': MINRI}
pairs = []
names = list(tables)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = names[i], names[j]
        clash = [(m, tables[a][m], tables[b][m]) for m in ZHI
                 if m in tables[a] and m in tables[b] and tables[a][m] == tables[b][m]]
        if clash:
            pairs.append('%s×%s 同月同支 %s' % (a, b, clash[:3]))
check('2. 王/相/官/民四表两两零交集', not pairs, '冲突 %s' % pairs if pairs else
      '月支查日支体系内无同位双扣')

# ── 3. 基类委托抽查 ──────────────────────────────────────────────
try:
    from modules.shensha.神煞基类 import ShenShaChecker
    ck = ShenShaChecker()
    probes = [
        ({'month_zhi': '巳', 'day_zhi': '巳'}, ck._is_wangri, True),    # 夏巳=王日（修正点）
        ({'month_zhi': '巳', 'day_zhi': '午'}, ck._is_wangri, False),   # 旧夏午误表
        ({'month_zhi': '寅', 'day_zhi': '巳'}, ck._is_xiangri, True),   # 春巳=相日
        ({'month_zhi': '寅', 'day_zhi': '卯'}, ck._is_xiangri, False),  # 旧两支版（=官日支）
        ({'month_zhi': '寅', 'day_zhi': '寅'}, ck._is_wangri, True),
        ({'module_zhi': '', 'month_zhi': '', 'day_zhi': '寅'}, ck._is_wangri, False),
    ]
    fails = []
    for sz, fn, exp in probes:
        if fn(sz) != exp:
            fails.append('%s→%s' % (sz, fn(sz)))
    check('3. 基类 _is_wangri/_is_xiangri 委托抽查 6 探针', not fails,
          '失败 %s' % fails if fails else '夏巳/春巳修正点生效，旧表点已断')
except Exception as e:
    check('3. 基类委托抽查', False, '异常 %r' % e)

# ── 4. 2025-2026 全日穷举命中数区间 ──────────────────────────────
from datetime import date, timedelta
d0, d1 = date(2025, 1, 1), date(2026, 12, 31)
nw = nx = 0
try:
    from modules.四柱计算器 import calculate_sizhu
    d = d0
    while d <= d1:
        sz = calculate_sizhu(d, 12, 0)
        if is_wangri_by_zhi(sz.get('month_zhi', ''), sz.get('day_zhi', '')):
            nw += 1
        if is_xiangri_by_zhi(sz.get('month_zhi', ''), sz.get('day_zhi', '')):
            nx += 1
        d += timedelta(days=1)
    span = (d1 - d0).days + 1
    check('4. 2025-2026 穷举命中数区间', 30 <= nw / span * 365 <= 40 and 30 <= nx / span * 365 <= 40,
          '王日 %d 天、相日 %d 天 / %d 天（年率 王%.1f 相%.1f）'
          % (nw, nx, span, nw / span * 365, nx / span * 365))
except Exception as e:
    check('4. 全日穷举', False, '异常 %r' % e)

# ── 5. 旧表复活反断言（函数块级：_is_xiangri/_is_wangri 必须为单点委托）──
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

bad_blocks = []
for meth, delegate in (('_is_xiangri', 'is_xiangri_by_zhi'),
                       ('_is_wangri', 'is_wangri_by_zhi')):
    block = _extract_method(src, meth)
    if not block:
        bad_blocks.append('%s 方法缺失' % meth)
        continue
    if delegate not in block:
        bad_blocks.append('%s 未委托 %s' % (meth, delegate))
    if "in ['" in block or 'elif month_zhi' in block:
        bad_blocks.append('%s 残留旧 if/elif 查表结构' % meth)
check('5. 旧表复活反断言（方法块级：仅委托、无 if/elif 查表链）', not bad_blocks,
      bad_blocks[0] if bad_blocks else '_is_xiangri/_is_wangri 均为单点委托（母仓等他表不受影响）')

# ── 6. 全模块谓词唯一性 ──────────────────────────────────────────
import re
shensha_dir = ROOT / 'modules' / 'shensha'
PREDICATES = ('_is_wangri', '_is_xiangri', '_is_guanri', '_is_minri')
base_file = '神煞基类.py'
dup = []
for f in sorted(shensha_dir.glob('*.py')):
    if f.name == base_file:
        continue
    txt = f.read_text(encoding='utf-8')
    for p in PREDICATES:
        if re.search(r'^    def %s\(' % p, txt, re.M):
            dup.append('%s: def %s（子类重写）' % (f.name, p))
check('6. 全模块谓词唯一性（王/相/官/民谓词仅基类定义）', not dup,
      '违例 %s' % dup if dup else '批A 删除入宅 _is_xiangri / 嫁娶 _is_wangri 后无子类重写')

# ── 7. 全模块内联民间表反断言 ────────────────────────────────────
INLINE_PAT = re.compile(r'\b(?:xiangri_map|wangri_map|guanri_map|minri_map)\b')
resid = []
for f in sorted(shensha_dir.glob('*.py')):
    for m in INLINE_PAT.finditer(f.read_text(encoding='utf-8')):
        resid.append('%s: %s' % (f.name, m.group(0)))
check('7. 内联民间表变量零残留（xiangri_map/wangri_map 等）', not resid,
      '残留 %s' % resid[:5] if resid else '全模块无民间帝旺表内联变量')

print('=' * 72)
print('批3 E1/E2 verify：%s' % ('全部通过 PASS' if PASS else '存在失败 FAIL'))
sys.exit(0 if PASS else 1)
