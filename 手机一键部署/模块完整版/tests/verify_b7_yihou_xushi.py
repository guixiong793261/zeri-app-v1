# -*- coding: utf-8 -*-
"""
批7a F2/F3 益后+续世修正常驻 verify
==================================
F2 益后：《协纪辨方书》卷六·义例四"益后"条（279224 L123）《历例》曰
  "正月子、二月午、三月丑、四月未、五月寅、六月申、七月卯、八月酉、
  九月辰、十月戌、十一月巳、十二月亥"（《考原》卷三 359078 L108-112
  逐字同载零分歧）——旧基类内联表"未戌丑辰四库循环×3"12 值中仅辰月丑、
  亥月戌与典载巧合，10/12 月值失准，自录口诀三库无载（"错误制度化"
  第六例）。批7a 改模块级 _YIHOU_ZHI_BY_MONTH 权威表+is_yihou_by_zhi
  单点出口（001 §79/§80）。
F3 续世：同卷"续世"条（279224 L124）《历例》曰"正月丑、二月未、三月寅、
  四月申、五月卯、六月酉、七月辰、八月戌、九月巳、十月亥、十一月午、
  十二月子"，考原按"常在益后后一辰"——旧实现"与益后查法相同"直接委托
  _is_yihou（同一命中集双注册），违背考原按（典载两集 2026 全年 0 天
  重合）。批7a 独立 _XUSHI_ZHI_BY_MONTH 表+is_xushi_by_zhi 单点出口，
  两表互以"+1辰"结构断言硬锁（防单表漂移）。
血忌备查：《考原》（359079 L135）血忌《历例》表与续世表逐字相同，
  曹注"与续世义同"（同位异名，与天吏【致死】同型）；软件全库零血忌
  实现（2026-10 批7a 前置核实），本表不兼作血忌发射。

检查项：
  1. is_yihou_by_zhi 穷举 12 月×12 支硬锁典载表（0 误 0 漏）；
  2. is_xushi_by_zhi 穷举 12 月×12 支硬锁典载表（0 误 0 漏）；
  3. 结构断言：典载硬编码表自洽（考原按"续世=益后+1辰"）＋模块级
     _XUSHI_ZHI_BY_MONTH 与 _YIHOU_ZHI_BY_MONTH 同结构互锁；
  4. 基类 _is_yihou/_is_xushi 委托抽查 8 探针（典载正点、旧表点断开、
     空值防呆）；
  5. 旧四库循环表复活反断言（10 个旧独有点二神皆不命中）＋益后∩续世
     互斥（反断言旧"续世恒=益后"同集复活）；
  6. def _is_yihou / def _is_xushi 全模块唯一定义（反断言子类重写复活）；
  7. 运行时管线探针（真实 calculate_sizhu + check(sz,{})，六 checker）：
     寅月子日（典益后）含益后不含续世；寅月丑日（典续世）含续世不含
     益后；寅月未日（旧软命中日）二神皆零发射。

用法：python tests/verify_b7_yihou_xushi.py
退出码：0=全部通过  1=任一失败（CI 可挂）
"""
import sys
import re
import datetime as dt
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


# ── 典载硬编码（协纪卷六·义例四 279224 L123-124；考原 359078 同载）────
YIHOU = {'寅': '子', '卯': '午', '辰': '丑', '巳': '未',
         '午': '寅', '未': '申', '申': '卯', '酉': '酉',
         '戌': '辰', '亥': '戌', '子': '巳', '丑': '亥'}
XUSHI = {'寅': '丑', '卯': '未', '辰': '寅', '巳': '申',
         '午': '卯', '未': '酉', '申': '辰', '酉': '戌',
         '戌': '巳', '亥': '亥', '子': '午', '丑': '子'}
ZHI12 = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
ZHI_SEQ = '子丑寅卯辰巳午未申酉戌亥'

from modules.shensha.神煞基类 import (is_yihou_by_zhi, is_xushi_by_zhi,
                                      _YIHOU_ZHI_BY_MONTH, _XUSHI_ZHI_BY_MONTH,
                                      ShenShaChecker)

# ── 1. 益后表穷举硬锁 ────────────────────────────────────────────
bad = []
for m in ZHI12:
    for dz in ZHI_SEQ:
        if is_yihou_by_zhi(m, dz) != (dz == YIHOU[m]):
            bad.append('益后 %s月%s' % (m, dz))
check('1. 益后表穷举 12x12 硬锁（0误0漏）', not bad,
      '违例 %s' % bad[:6] if bad else '《历例》正月子…十二月亥')

# ── 2. 续世表穷举硬锁 ────────────────────────────────────────────
bad = []
for m in ZHI12:
    for dz in ZHI_SEQ:
        if is_xushi_by_zhi(m, dz) != (dz == XUSHI[m]):
            bad.append('续世 %s月%s' % (m, dz))
check('2. 续世表穷举 12x12 硬锁（0误0漏）', not bad,
      '违例 %s' % bad[:6] if bad else '《历例》正月丑…十二月子')

# ── 3. 结构断言：续世＝益后+1辰 ──────────────────────────────────
canon_bad = [m for m in ZHI12
             if XUSHI[m] != ZHI_SEQ[(ZHI_SEQ.index(YIHOU[m]) + 1) % 12]]
check('3a. 典载硬编码表结构自洽（考原按"常在益后后一辰"）', not canon_bad,
      '违例 %s' % canon_bad if canon_bad else '')
mod_bad = []
for m in ZHI12:
    y = _YIHOU_ZHI_BY_MONTH.get(m)
    x = _XUSHI_ZHI_BY_MONTH.get(m)
    if y is None or x is None or x != ZHI_SEQ[(ZHI_SEQ.index(y) + 1) % 12]:
        mod_bad.append('%s月(益后=%s,续世=%s)' % (m, y, x))
check('3b. 模块级两表 +1辰 结构互锁（防单表漂移）', not mod_bad,
      '违例 %s' % mod_bad if mod_bad else '')
mod_missing = [m for m in ZHI12
               if m not in _YIHOU_ZHI_BY_MONTH or m not in _XUSHI_ZHI_BY_MONTH]
check('3c. 模块级两表 12 月键齐全', not mod_missing,
      '缺键 %s' % mod_missing if mod_missing else '')

# ── 4. 基类委托抽查 ──────────────────────────────────────────────
try:
    ck = ShenShaChecker()
    probes = [
        ('yihou', {'month_zhi': '寅', 'day_zhi': '子'}, True),   # 典载益后正点
        ('yihou', {'month_zhi': '酉', 'day_zhi': '酉'}, True),   # 八月酉
        ('yihou', {'month_zhi': '寅', 'day_zhi': '未'}, False),  # 旧四库循环表首值，已断
        ('xushi', {'month_zhi': '寅', 'day_zhi': '丑'}, True),   # 典载续世正点
        ('xushi', {'month_zhi': '亥', 'day_zhi': '亥'}, True),   # 十月亥
        ('xushi', {'month_zhi': '寅', 'day_zhi': '子'}, False),  # 旧"同益后"点，已断
        ('yihou', {'month_zhi': '', 'day_zhi': '子'}, False),    # 空月支防呆
        ('xushi', {'month_zhi': '寅', 'day_zhi': ''}, False),    # 空日支防呆
    ]
    fails = []
    for kind, sz, exp in probes:
        got = ck._is_yihou(sz) if kind == 'yihou' else ck._is_xushi(sz)
        if got != exp:
            fails.append('%s %s月%s日→%s(期望%s)' % (
                kind, sz.get('month_zhi', '?'), sz.get('day_zhi', '?'), got, exp))
    check('4. 基类委托抽查 8 探针（单点出口）', not fails,
          '失败 %s' % fails if fails else 'is_yihou_by_zhi / is_xushi_by_zhi')
except Exception as e:
    check('4. 基类委托抽查', False, '异常 %r' % e)

# ── 5. 旧表复活反断言 + 两集互斥 ─────────────────────────────────
# 旧四库循环表 12 值中辰月丑、亥月戌与典载巧合，其余 10 点为旧独有点
OLD_ONLY = [('寅', '未'), ('卯', '戌'), ('巳', '辰'), ('午', '未'), ('未', '戌'),
            ('申', '丑'), ('酉', '辰'), ('戌', '未'), ('子', '丑'), ('丑', '辰')]
revive = ['%s月%s' % (m, d) for m, d in OLD_ONLY
          if ck._is_yihou({'month_zhi': m, 'day_zhi': d})
          or ck._is_xushi({'month_zhi': m, 'day_zhi': d})]
check('5a. 旧四库循环表复活反断言（10 旧独有点二神皆不命中）', not revive,
      '复活 %s' % revive if revive else '')
both = ['%s月%s' % (m, d) for m in ZHI12 for d in ZHI_SEQ
        if ck._is_yihou({'month_zhi': m, 'day_zhi': d})
        and ck._is_xushi({'month_zhi': m, 'day_zhi': d})]
check('5b. 益后∩续世互斥（+1辰错位；反断言旧"续世恒=益后"同集复活）', not both,
      '同中 %s' % both[:6] if both else '')

# ── 6. 谓词全模块唯一定义 ────────────────────────────────────────
mod_dir = ROOT / 'modules'
defs_yh, defs_xs = [], []
for p in sorted(mod_dir.rglob('*.py')):
    try:
        text = p.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        continue
    if re.search(r'^\s*def _is_yihou\b', text, re.M):
        defs_yh.append(p.name)
    if re.search(r'^\s*def _is_xushi\b', text, re.M):
        defs_xs.append(p.name)
check('6a. _is_yihou 全模块唯一（反断言子类重写复活）', defs_yh == ['神煞基类.py'],
      '定义位 %s' % defs_yh)
check('6b. _is_xushi 全模块唯一', defs_xs == ['神煞基类.py'], '定义位 %s' % defs_xs)

# ── 7. 运行时管线探针（真实 calculate_sizhu + check(sz,{})）──────
from modules.四柱计算器 import calculate_sizhu
from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
from modules.shensha.修造神煞 import ConstructionShenShaChecker
from modules.shensha.通用神煞 import CommonShenShaChecker
from modules.shensha.安葬神煞 import BurialShenShaChecker
from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
from modules.shensha.安床神煞 import BedShenShaChecker

SIX = [(MarriageShenShaChecker, '嫁娶'), (ConstructionShenShaChecker, '修造'),
       (CommonShenShaChecker, '通用'), (BurialShenShaChecker, '安葬'),
       (RuZhaiShenShaChecker, '入宅'), (BedShenShaChecker, '安床')]

_SIZHU_CACHE = {}


def _sizhu(y, m, d):
    key = (y, m, d)
    if key not in _SIZHU_CACHE:
        _SIZHU_CACHE[key] = calculate_sizhu(dt.datetime(y, m, d, 12, 0))
    return _SIZHU_CACHE[key]


def names_of(cls, sz):
    """真实 check() 管线，按 dict 列表解析 names（§75.7 清单④）。异常上抛不吞。"""
    return [i.get('name', '') if isinstance(i, dict) else str(i)
            for i in cls().check(sz, {})]


try:
    yin = []
    d = dt.date(2026, 1, 1)
    while d.year == 2026:
        sz = _sizhu(d.year, d.month, d.day)
        if sz.get('month_zhi') == '寅':
            yin.append((d, sz))
        d += dt.timedelta(days=1)

    def first_day(zhi):
        hit = [(d, sz) for d, sz in yin if sz.get('day_zhi') == zhi]
        return hit[0] if hit else None

    zi = first_day('子')   # 典载益后日（寅月子）
    chou = first_day('丑')  # 典载续世日（寅月丑）
    wei = first_day('未')   # 旧软命中日（寅月未，典载二神皆不命中）
    if not (zi and chou and wei):
        check('7. 运行时管线探针样本', False,
              '2026 寅月子/丑/未日样本缺失（zi=%s chou=%s wei=%s），须人工复核'
              % (bool(zi), bool(chou), bool(wei)))
    else:
        d_zi, sz_zi = zi
        d_chou, sz_chou = chou
        d_wei, sz_wei = wei
        for cls, lbl in SIX:
            n_zi = names_of(cls, sz_zi)
            check('7. %s 寅月子日(%s)含益后、不含续世（典益后日回归）' % (lbl, d_zi),
                  '益后' in n_zi and '续世' not in n_zi,
                  'names=%s' % [n for n in n_zi if n in ('益后', '续世')])
            n_chou = names_of(cls, sz_chou)
            check('7. %s 寅月丑日(%s)含续世、不含益后（典续世日回归）' % (lbl, d_chou),
                  '续世' in n_chou and '益后' not in n_chou,
                  'names=%s' % [n for n in n_chou if n in ('益后', '续世')])
            n_wei = names_of(cls, sz_wei)
            check('7. %s 寅月未日(%s)二神皆零发射（旧软命中日断开）' % (lbl, d_wei),
                  '益后' not in n_wei and '续世' not in n_wei,
                  'names=%s' % [n for n in n_wei if n in ('益后', '续世')])
except Exception as e:
    check('7. 运行时管线探针', False, '异常 %r' % e)

# ── 汇总 ─────────────────────────────────────────────────────────
print('=' * 60)
print('批7a 益后/续世 verify：%s' % ('全部通过' if PASS else '存在失败项'))
sys.exit(0 if PASS else 1)
