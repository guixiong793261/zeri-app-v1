# -*- coding: utf-8 -*-
"""
批5 E4 时德修正常驻 verify
==================================
E4 时德：《协纪辨方书》卷五·义例三"时德"条《历例》曰"春午，夏辰，秋子，
  冬寅"（《考原》卷三"四时天德"逐字同载零分歧；曹震圭"各以四时所生之
  阳辰为之"互证；馆臣按"六阳辰……六取四"机制互证）——六阳辰中各取其时
  所生：春木生火取午、夏火生土取辰、秋金生水取子、冬水生木取寅，一季
  一值。旧三值表（春辰巳午、夏未申酉、秋戌亥子、冬丑寅卯）＝"季月支起
  顺行三辰"结构，三库检索穷尽无载——"错误制度化"第五例（官日/四相/
  吉庆/吉期之后；四相支表 b42c31f 勘干表时漏网，批6' 处理）。
  批5 E4 改模块级 _SHIDE_ZHI_BY_SEASON 单点出口（001 §75）。

检查项：
  1. 模块级 is_shide_by_zhi 穷举 12 月×12 支硬锁典载表（一季一值）；
  1b. 新旧表重合结构断言（旧表独有 11 值清单锁定）；
  2. 基类 _is_shide 动态委托抽查 6 探针（含旧表点断开、夏辰新值点）；
  3. 2025-2027 全日穷举命中数区间断言（新表约 30 天/年；旧表对照
     约 91 天/年仅打印）；
  4. 运行时管线探针：修造 checker 典载命中日发射时德、旧表独有日不发射；
     拆舍（继承修造 super 日管线）两断言同步；
  5. 发射位唯一性（静态扫描）：_add_shensha('时德' 恰 4 处（修造/动土/
     入宅/作灶）；拆舍神煞.py 无 '时德' 字面（防继承链外重加）；基类
     无时德发射注册；
  6. 墓碑在位：基类 _is_shide docstring 含旧三值表墓碑标记。

用法：python tests/verify_b5_shide.py
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
from modules.shensha.神煞基类 import is_shide_by_zhi, _SHIDE_ZHI_BY_SEASON

SHIDE = {'寅': '午', '卯': '午', '辰': '午',
         '巳': '辰', '午': '辰', '未': '辰',
         '申': '子', '酉': '子', '戌': '子',
         '亥': '寅', '子': '寅', '丑': '寅'}
# 旧三值表（墓碑对照，仅测试用）：季月支起顺行三辰
OLD_TABLE = {'寅': {'辰', '巳', '午'}, '卯': {'辰', '巳', '午'}, '辰': {'辰', '巳', '午'},
             '巳': {'未', '申', '酉'}, '午': {'未', '申', '酉'}, '未': {'未', '申', '酉'},
             '申': {'戌', '亥', '子'}, '酉': {'戌', '亥', '子'}, '戌': {'戌', '亥', '子'},
             '亥': {'丑', '寅', '卯'}, '子': {'丑', '寅', '卯'}, '丑': {'丑', '寅', '卯'}}
ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']

bad = []
for m in ZHI:
    for d in ZHI:
        if is_shide_by_zhi(m, d) != (d == SHIDE[m]):
            bad.append('时德 %s月%s' % (m, d))
check('1. 时德表穷举 12x12 硬锁（0误0漏）', not bad, '违例 %s' % bad[:6] if bad else
      '一季一值：春午、夏辰、秋子、冬寅（《历例》"春午，夏辰，秋子，冬寅"）')

# 1b. 新旧重合结构：旧表独有值 = 旧三值全集 − 新单值全集（恰 8 值）
old_only = sorted(set(d for m in ZHI for d in OLD_TABLE[m]) -
                  set(SHIDE.values()))
check('1b. 旧表独有 8 值锁定（新表夏辰为旧表所无）',
      old_only == ['丑', '亥', '卯', '巳', '戌', '未', '申', '酉'],
      '旧表独有值 %s（复活反断言见 2/4 项）' % old_only)

# ── 2. 基类委托抽查 ──────────────────────────────────────────────
try:
    from modules.shensha.神煞基类 import ShenShaChecker
    ck = ShenShaChecker()
    probes = [
        ({'month_zhi': '寅', 'day_zhi': '午'}, True),    # 寅月午（新表正点）
        ({'month_zhi': '未', 'day_zhi': '辰'}, True),    # 未月辰（夏辰，旧表所无新值）
        ({'month_zhi': '酉', 'day_zhi': '子'}, True),    # 酉月子（秋子）
        ({'month_zhi': '寅', 'day_zhi': '辰'}, False),   # 旧表独有点，已断
        ({'month_zhi': '巳', 'day_zhi': '未'}, False),   # 旧表独有点，已断
        ({'month_zhi': '', 'day_zhi': '午'}, False),     # 空月支防呆
    ]
    fails = []
    for sz, exp in probes:
        if ck._is_shide(sz) != exp:
            fails.append('%s月%s日→%s(期望%s)' % (sz.get('month_zhi', '?'),
                          sz.get('day_zhi', '?'), ck._is_shide(sz), exp))
    check('2. 基类 _is_shide 委托抽查 6 探针', not fails, '失败 %s' % fails if fails
          else '委托 is_shide_by_zhi 单点出口')
except Exception as e:
    check('2. 基类 _is_shide 委托抽查', False, '异常 %r' % e)

# ── 3. 2025-2027 全日穷举命中数 ─────────────────────────────────
import datetime as dt

def count_hits(years, pred):
    n = 0
    for y in years:
        d = dt.date(y, 1, 1)
        while d.year == y:
            if pred({'month_zhi': _mz(y, d), 'day_zhi': _dz(y, d)}):
                n += 1
            d += dt.timedelta(days=1)
    return n

_SIZHU_CACHE = {}
def _mz(y, d):
    return _sizhu(y, d).get('month_zhi', '')

def _dz(y, d):
    return _sizhu(y, d).get('day_zhi', '')

def _sizhu(y, d):
    key = (y, d.timetuple().tm_yday)
    if key not in _SIZHU_CACHE:
        from modules.四柱计算器 import calculate_sizhu
        _SIZHU_CACHE[key] = calculate_sizhu(dt.datetime(y, d.month, d.day, 12, 0))
    return _SIZHU_CACHE[key]

try:
    new_hits = count_hits([2025, 2026, 2027],
                          lambda sz: is_shide_by_zhi(sz['month_zhi'], sz['day_zhi']))
    # 新表 1/12 → 3 年期望 ~91 天（30.4/年），区间 [85, 97]
    check('3. 新表 2025-2027 命中数区间断言（期望约 30 天/年）',
          85 <= new_hits <= 97, '实测 %d 天（3 年）' % new_hits)
    old_hits = count_hits([2025, 2026, 2027],
                          lambda sz: sz['day_zhi'] in OLD_TABLE.get(sz['month_zhi'], set()))
    print('[INFO] 旧三值表同期命中 %d 天（对照，3 年期望约 273）' % old_hits)
    check('3b. 旧表对照显著偏多（新/旧 < 0.5，错表扩面自证）',
          new_hits * 2 < old_hits, '新 %d vs 旧 %d' % (new_hits, old_hits))
except Exception as e:
    check('3. 命中数穷举', False, '异常 %r' % e)

# ── 4. 运行时管线探针 ───────────────────────────────────────────
def checker_names(checker, y, m, d):
    from modules.四柱计算器 import calculate_sizhu
    sz = calculate_sizhu(dt.datetime(y, m, d, 12, 0))
    res = checker.check(sz) or []
    return [it['name'] for it in res if isinstance(it, dict) and 'name' in it]

try:
    from modules.事项标准 import get_shensha_checker
    cm = get_shensha_checker('修造')
    cd = get_shensha_checker('拆舍')
    # 2025-02-18 寅月午日＝新表命中；2025-02-16 寅月辰日＝旧表独有
    hit_new_m = '时德' in checker_names(cm, 2025, 2, 18)
    hit_old_m = '时德' in checker_names(cm, 2025, 2, 16)
    hit_new_d = '时德' in checker_names(cd, 2025, 2, 18)
    hit_old_d = '时德' in checker_names(cd, 2025, 2, 16)
    check('4. 修造管线典载命中日发射时德', hit_new_m and not hit_old_m,
          '2025-02-18(寅月午)=%s / 2025-02-16(寅月辰,旧表点)=%s' % (hit_new_m, hit_old_m))
    check('4b. 拆舍（继承修造 super 日管线）同步', hit_new_d and not hit_old_d,
          '2025-02-18=%s / 2025-02-16=%s' % (hit_new_d, hit_old_d))
except Exception as e:
    check('4. 运行时管线探针', False, '异常 %r' % e)

# ── 5. 发射位唯一性（静态扫描）──────────────────────────────────
try:
    shensha_dir = ROOT / 'modules' / 'shensha'
    emit_sites = {}
    for f in sorted(shensha_dir.glob('*.py')):
        text = f.read_text(encoding='utf-8')
        n = len(re.findall(r"_add_shensha\(\s*'时德'", text))
        if n:
            emit_sites[f.name] = n
    expect = {'修造神煞.py': 1, '动土神煞.py': 1, '入宅神煞.py': 1, '作灶神煞.py': 1}
    check('5. 时德发射位恰 4 处（修造/动土/入宅/作灶）', emit_sites == expect,
          '实测 %s' % emit_sites)
    chai_text = (shensha_dir / '拆舍神煞.py').read_text(encoding='utf-8')
    check('5b. 拆舍神煞.py 无时德字面（继承覆盖，防重加）',
          '时德' not in chai_text, '')
    base_text = (shensha_dir / '神煞基类.py').read_text(encoding='utf-8')
    n_base = len(re.findall(r"_add_shensha\(\s*'时德'", base_text))
    check('5c. 基类无时德发射注册（月管线不注册）', n_base == 0,
          '基类 _add_shensha(\'时德\' 出现 %d 次' % n_base)
except Exception as e:
    check('5. 发射位静态扫描', False, '异常 %r' % e)

# ── 6. 墓碑在位 ─────────────────────────────────────────────────
try:
    ok6 = ('墓碑' in base_text and '辰巳午' in base_text
           and 'is_shide_by_zhi' in base_text
           and base_text.count('def _is_shide') == 1)
    check('6. 基类墓碑在位 + _is_shide 单一定义', ok6, '')
except Exception as e:
    check('6. 墓碑检查', False, '异常 %r' % e)

print()
print('=' * 60)
print('verify_b5_shide：%s' % ('全部通过 (exit 0)' if PASS else '存在失败 (exit 1)'))
sys.exit(0 if PASS else 1)
