# -*- coding: utf-8 -*-
"""
批8a 土王用事口径修复常驻 verify
==================================
J2 甲案①：修造神煞 `_is_tuwang_yongshi` 原实现把节气月支映射到公历月号
＋ monthrange 取公历月天数，节气月跨公历月导致判定失真（旧 73 天/年且与
典载交集仅约 53 天）。

典载口径（《神枢经》/《历例》"土於四立之前各旺一十八日"，协纪卷一·五行；
考原逐字同载零分歧）：土王用事＝四立（立春/立夏/立秋/立冬）之前各 18 日，
即距下一个四立天数∈[1, 18]（四立当日归本令不算土王）。

批8a：神煞基类新增模块级 `is_tuwang_yongshi_by_date` 单点出口（sxtwl 四立
＋年度缓存）；修造神煞 `_is_tuwang_yongshi` 改委托；动土/拆舍经继承自动
跟随（001 §81.3）。

检查项：
  1. sxtwl 四立索引 sanity（2024-2028 立春/立夏/立秋/立冬落典载窗口）；
  2. 边界穷举（2024-2028 共 20 立 ×4 点：[L-18,L-1] 命中、L-19/L 不命中）；
  3. 2024-2027 每年 72 天硬锁（18×4）＋独立公式 0 误 0 漏；
  4. 命中日恒在四季月（辰未戌丑）；
  5. 委托唯一性：`def _is_tuwang_yongshi` 全模块仅修造神煞一处定义
     （动土/拆舍继承）＋错位实现（monthrange）复活反断言；
  6. 运行时管线：动土/拆舍 checker 在翻转日发射断言（土王用事 ∓40 唯一变化）；
  7. 修造零变化断言：修造 checker 走 _is_tuwang→_is_tuwen（土瘟表），
     与本谓词无涉，翻转日发射零变化（名实错另立，001 §81.1）。

用法：python tests/verify_b8_tuwang.py
退出码：0=全部通过  1=任一失败（CI 可挂）
"""
import sys
import re
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sxtwl
from modules.四柱计算器 import calculate_sizhu
from modules.shensha.神煞基类 import ShenShaChecker, is_tuwang_yongshi_by_date
from modules.shensha.修造神煞 import ConstructionShenShaChecker
from modules.shensha.动土神煞 import DiggingShenShaChecker
from modules.shensha.拆舍神煞 import DemolitionShenShaChecker

PASS = True


def check(name, ok, detail=''):
    global PASS
    tag = 'PASS' if ok else 'FAIL'
    print('[%s] %s%s' % (tag, name, ('  ' + detail) if detail else ''))
    if not ok:
        PASS = False


def jd_to_date(jd):
    dd = sxtwl.JD2DD(jd)
    return dt.date(int(dd.Y), int(dd.M), int(dd.D))


# 独立真值：用 sxtwl 四立独立实现（与产品函数同据但代码路径独立）
_SILIQ = (0, 6, 12, 18)


def truth_twws(y, m, d):
    today = dt.date(y, m, d)
    out = []
    for yy in (y, y + 1):
        for i in _SILIQ:
            out.append(jd_to_date(sxtwl.getJieQiByYear(yy)[i].jd))
    for L in sorted(out):
        delta = (L - today).days
        if 1 <= delta <= 18:
            return True
    return False


# ── 1. 四立索引 sanity（2024-2028）──────────────────────────
for y in range(2024, 2029):
    lst = sxtwl.getJieQiByYear(y)
    lichun = jd_to_date(lst[0].jd)
    lixia = jd_to_date(lst[6].jd)
    liqiu = jd_to_date(lst[12].jd)
    lidong = jd_to_date(lst[18].jd)
    check('%d 立春∈2/3-2/5' % y,
          dt.date(y, 2, 3) <= lichun <= dt.date(y, 2, 5),
          '%s' % lichun)
    check('%d 立夏∈5/4-5/6' % y,
          dt.date(y, 5, 4) <= lixia <= dt.date(y, 5, 6),
          '%s' % lixia)
    check('%d 立秋∈8/6-8/8' % y,
          dt.date(y, 8, 6) <= liqiu <= dt.date(y, 8, 8),
          '%s' % liqiu)
    check('%d 立冬∈11/6-11/8' % y,
          dt.date(y, 11, 6) <= lidong <= dt.date(y, 11, 8),
          '%s' % lidong)

# ── 2. 边界穷举（2024-2028 全部四立）────────────────────────
bad = []
for y in range(2024, 2029):
    for i in _SILIQ:
        L = jd_to_date(sxtwl.getJieQiByYear(y)[i].jd)
        for delta, expect in ((18, True), (19, False), (1, True), (0, False)):
            dd = L - dt.timedelta(days=delta)
            got = is_tuwang_yongshi_by_date(dd.year, dd.month, dd.day)
            if got != expect:
                bad.append('L=%s delta=%d expect=%s got=%s'
                           % (L, delta, expect, got))
check('边界：[L-18,L-1] 命中、L-19 与四立当日不命中（%d 立×4 点）'
      % (len(range(2024, 2029)) * 4), not bad, '; '.join(bad[:5]))

# ── 3. 每年 72 天硬锁 ＋ 独立公式 0 误 0 漏 ──────────────────
SZ_CACHE = {}


def get_sizhu(y, m, d):
    key = (y, m, d)
    if key not in SZ_CACHE:
        sz = calculate_sizhu(dt.datetime(y, m, d, 12, 0))
        sz['year'], sz['month'], sz['day'] = y, m, d
        SZ_CACHE[key] = sz
    return SZ_CACHE[key]


for y in range(2024, 2028):
    count, miss, false_pos = 0, 0, 0
    d0 = dt.date(y, 1, 1)
    for i in range((dt.date(y, 12, 31) - d0).days + 1):
        cur = d0 + dt.timedelta(days=i)
        got = is_tuwang_yongshi_by_date(cur.year, cur.month, cur.day)
        truth = truth_twws(cur.year, cur.month, cur.day)
        if got:
            count += 1
        if got != truth:
            if got:
                false_pos += 1
            else:
                miss += 1
    check('%d 命中 72 天（18×4）' % y, count == 72, 'got %d' % count)
    check('%d 独立公式 0 误 0 漏' % y,
          miss == 0 and false_pos == 0,
          'miss=%d false_pos=%d' % (miss, false_pos))

# ── 4. 命中日恒在四季月 ──────────────────────────────────────
bad_mz = []
CONS = ConstructionShenShaChecker()
for y in range(2024, 2028):
    d0 = dt.date(y, 1, 1)
    for i in range((dt.date(y, 12, 31) - d0).days + 1):
        cur = d0 + dt.timedelta(days=i)
        if is_tuwang_yongshi_by_date(cur.year, cur.month, cur.day):
            sz = get_sizhu(cur.year, cur.month, cur.day)
            if sz.get('month_zhi') not in ('辰', '未', '戌', '丑'):
                bad_mz.append('%s mz=%s' % (cur, sz.get('month_zhi')))
check('命中日恒在四季月（辰未戌丑）', not bad_mz, '; '.join(bad_mz[:5]))

# ── 5. 委托唯一性 ＋ 错位实现复活反断言 ───────────────────────
base_src = Path(ROOT / 'modules/shensha/神煞基类.py').read_text(encoding='utf-8')
cons_src = Path(ROOT / 'modules/shensha/修造神煞.py').read_text(encoding='utf-8')

# 修造神煞中 def _is_tuwang_yongshi 唯一
check('修造神煞 def _is_tuwang_yongshi 唯一',
      cons_src.count('def _is_tuwang_yongshi') == 1)

# 错位实现残留清零：修造神煞中不得再含 calendar.monthrange 调用或公历月号映射表
check('错位实现残留清零（无 calendar.monthrange / 公历月号映射表）',
      'calendar.monthrange' not in cons_src
      and "{'辰': 3, '未': 6, '戌': 9, '丑': 12}" not in cons_src
      and "{'辰':3,'未':6,'戌':9,'丑':12}" not in cons_src)

# 动土/拆舍不重写（继承修造）
for fname, tag in (('动土神煞.py', '动土'), ('拆舍神煞.py', '拆舍')):
    src = Path(ROOT / 'modules/shensha' / fname).read_text(encoding='utf-8')
    check('%s 不重写 _is_tuwang_yongshi（继承修造）' % tag,
          'def _is_tuwang_yongshi' not in src)

# 修造谓词体委托单点出口（静态扫描）
check('修造谓词委托 is_tuwang_yongshi_by_date',
      'is_tuwang_yongshi_by_date(' in cons_src)


# ── 6. 运行时：动土/拆舍翻转日发射断言 ───────────────────────
# 注意：修造神煞 L290-292 用 _is_tuwang（=土瘟表）发射「土王用事 -18」（名实
# 错，另立）。同日 _is_tuwang_yongshi（-40）会被去重抑制。故本节只取
# 土瘟表为 False 的翻转日，隔离 -40 发射变化（名实错 -18 不受批8a 影响）。
def names_scores(checker, sz):
    out = {}
    for it in checker.check(sz, {}):
        if isinstance(it, dict):
            out[it.get('name')] = it.get('score')
        else:
            out[it[0]] = it[1]
    return out


# 土瘟表（月支查日支，月建后一辰）
tuwen_map = {'寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰', '午': '巳', '未': '午',
             '申': '未', '酉': '申', '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'}

# 找 2026 翻转日（旧口径 vs 新口径），仅取土瘟表为 False 的日子
old_only, new_only = [], []
d0 = dt.date(2026, 1, 1)
for i in range((dt.date(2026, 12, 31) - d0).days + 1):
    cur = d0 + dt.timedelta(days=i)
    sz = get_sizhu(cur.year, cur.month, cur.day)
    new = is_tuwang_yongshi_by_date(cur.year, cur.month, cur.day)
    month_zhi = sz.get('month_zhi')
    day = sz.get('day', 0)
    tuwang_months = {'辰': 3, '未': 6, '戌': 9, '丑': 12}
    old = False
    tm = tuwang_months.get(month_zhi)
    if tm:
        import calendar
        _, last_day = calendar.monthrange(cur.year, tm)
        old = day > last_day - 18
    is_tuwen = sz.get('day_zhi') == tuwen_map.get(month_zhi)
    if is_tuwen:
        continue  # 土瘟表日 -18 去重抑制 -40，跳过
    if old and not new:
        old_only.append(cur)
    elif new and not old:
        new_only.append(cur)

sample = (new_only[:3] + new_only[-3:] + old_only[:3] + old_only[-3:])
sample = sorted(set(sample))

emit_bad = []
for cur in sample:
    sz = get_sizhu(cur.year, cur.month, cur.day)
    new_hit = is_tuwang_yongshi_by_date(cur.year, cur.month, cur.day)
    for cls, tag in ((DiggingShenShaChecker, '动土'),
                     (DemolitionShenShaChecker, '拆舍')):
        ns = names_scores(cls(), sz)
        present = '土王用事' in ns
        score = ns.get('土王用事')
        expect_present = new_hit
        if present != expect_present:
            emit_bad.append('%s %s present=%s expect=%s'
                            % (cur, tag, present, expect_present))
        elif expect_present and score != -40:
            emit_bad.append('%s %s score=%s expect=-40'
                            % (cur, tag, score))
check('运行时：翻转日（土瘟表非命中）动土/拆舍 土王用事 -40 发射与新口径一致'
      '（抽样 %d 天）' % len(sample), not emit_bad, '; '.join(emit_bad[:5]))

# ── 7. 修造零变化断言（走 _is_tuwang→_is_tuwen，名实错另立）───
# 在样本翻转日上，修造发射集与"谓词独立"无关联——即修造不发射土王用事
# 当且仅当日非土瘟表日（与土王段无关）。
tuwen_map = {'寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰', '午': '巳', '未': '午',
             '申': '未', '酉': '申', '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'}
xz_bad = []
for cur in sample:
    sz = get_sizhu(cur.year, cur.month, cur.day)
    ns = names_scores(ConstructionShenShaChecker(), sz)
    is_tuwen = sz.get('day_zhi') == tuwen_map.get(sz.get('month_zhi'))
    # 修造 土王用事 -18 当且仅当土瘟日（与新口径土王段无涉）
    expect = is_tuwen
    actual = ns.get('土王用事') == -18
    if actual != expect:
        xz_bad.append('%s tuwen=%s 发射=%s' % (cur, is_tuwen, actual))
check('修造 土王用事 -18 实为土瘟表发射（与土王段无涉，名实错另立）',
      not xz_bad, '; '.join(xz_bad[:5]))

print()
print('FAIL 0' if PASS else 'FAIL 1')
sys.exit(0 if PASS else 1)
