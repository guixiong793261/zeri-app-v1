# -*- coding: utf-8 -*-
"""
批6' E6/F4 母仓+四相修正常驻 verify
==================================
F4 四相：《协纪辨方书》卷五·义例三"四相"条《历例》曰"春丙丁，夏戊巳，
  秋壬癸，冬甲乙"（天干表，月支查日干；《考原》卷三逐字同载零分歧；
  同卷时德条按语"四相取天干，时德取地支"互证；曹注庚辛不取）——旧支表
  "春亥子、夏寅卯、秋辰戌丑未、冬申酉"系母仓《历例》表逐字窜用（仅查
  day_zhi，天干不涉），三库无载。批6' 批1 勘正（0cb42a1，001 §76）。
E6 母仓：基类季节表"春亥子，夏寅卯，秋辰戌丑未，冬申酉"＝典载 ✅ 全等
  （《历例》原文；"土王后巳午"补充段按拍板 D1 选项 A 本批不补）；嫁娶
  "月支+1/+2 顺行表"三库无载且经动态派发污染基类日块发射（嫁娶母仓＝纯
  顺行表实证），入宅冗余表与基类逐字相同——批2 删表统一继承（8245200）。

检查项：
  1. is_sixiang_by_gan 穷举 12 月×10 干硬锁典载表（0 误 0 漏）＋庚辛恒 False；
  1b. 四相判据字段断言：day_zhi 变化不影响判定（天干单判据）；
  2. 基类 _is_sixiang 委托抽查 6 探针（旧表点断开、新干表正点）；
  3. 旧支表复活反断言：真实寅月亥日（日干非丙丁）四相不发射；
  4. 母仓：基类表 12×12 穷举硬锁 + def _is_mucang/_is_sixiang 全模块唯一性
     （反断言子类重写复活）；
  5. 运行时管线探针（清单④⑤）：嫁娶/入宅/修造/拆舍/动土/作灶 真实 check()
     命中日含/不含断言（嫁娶母仓已回归典载集；四相按日干判定）；
  6. 发射位唯一性静态扫描：'母仓'×5（基类/出行/开业/安葬/安床）、
     '母仓日'×4（嫁娶/入宅/作灶/通用）、'四相'×4（修造/动土/入宅/作灶）；
  7. 墓碑在位：基类 _is_sixiang 旧支表墓碑 + 嫁娶/入宅 _is_mucang 删表墓碑。

用法：python tests/verify_b6_mucang_sixiang.py
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


# ── 1. 四相表穷举硬锁 ────────────────────────────────────────────
from modules.shensha.神煞基类 import (is_sixiang_by_gan, _SIXIANG_GAN_BY_SEASON,
                                      ShenShaChecker, is_shide_by_zhi)

SIXIANG = {'寅': ('丙', '丁'), '卯': ('丙', '丁'), '辰': ('丙', '丁'),
           '巳': ('戊', '己'), '午': ('戊', '己'), '未': ('戊', '己'),
           '申': ('壬', '癸'), '酉': ('壬', '癸'), '戌': ('壬', '癸'),
           '亥': ('甲', '乙'), '子': ('甲', '乙'), '丑': ('甲', '乙')}
GAN10 = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI12 = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']

bad = []
for m in ZHI12:
    for g in GAN10:
        if is_sixiang_by_gan(m, g) != (g in SIXIANG[m]):
            bad.append('四相 %s月%s' % (m, g))
check('1. 四相表穷举 12x10 硬锁（0误0漏）', not bad, '违例 %s' % bad[:6] if bad else
      '春丙丁/夏戊巳/秋壬癸/冬甲乙（《历例》原文）')
gengxin = [g for g in ('庚', '辛') if any(is_sixiang_by_gan(m, g) for m in ZHI12)]
check('1a. 庚辛恒不取（曹注"金能杀万物"）', not gengxin, '命中 %s' % gengxin if gengxin else '')

# 1b. 判据字段＝天干（day_zhi 变化不影响）
try:
    ck0 = ShenShaChecker()
    pairs = [({'month_zhi': '寅', 'day_gan': '甲', 'day_zhi': '亥'},
              {'month_zhi': '寅', 'day_gan': '甲', 'day_zhi': '午'}),
             ({'month_zhi': '申', 'day_gan': '壬', 'day_zhi': '辰'},
              {'month_zhi': '申', 'day_gan': '壬', 'day_zhi': '子'})]
    f = [p for p, q in pairs if ck0._is_sixiang(p) != ck0._is_sixiang(q)]
    check('1b. 四相判据字段＝日干（day_zhi 无涉，旧支表机制反断言）', not f, '不一致 %s' % f if f else '')
except Exception as e:
    check('1b. 四相判据字段断言', False, '异常 %r' % e)

# ── 2. 基类委托抽查 ──────────────────────────────────────────────
try:
    ck = ShenShaChecker()
    probes = [
        ({'month_zhi': '寅', 'day_gan': '丙', 'day_zhi': '午'}, True),   # 新表正点（旧表点）
        ({'month_zhi': '未', 'day_gan': '己', 'day_zhi': '卯'}, True),   # 夏戊己
        ({'month_zhi': '戌', 'day_gan': '癸', 'day_zhi': '辰'}, True),   # 秋壬癸（旧表四值月）
        ({'month_zhi': '寅', 'day_gan': '甲', 'day_zhi': '亥'}, False),  # 旧支表正点，已断
        ({'month_zhi': '申', 'day_gan': '庚', 'day_zhi': '戌'}, False),  # 庚不取
        ({'month_zhi': '', 'day_gan': '丙'}, False),                     # 空月支防呆
    ]
    fails = []
    for sz, exp in probes:
        if ck._is_sixiang(sz) != exp:
            fails.append('%s月%s日→%s(期望%s)' % (sz.get('month_zhi', '?'),
                          sz.get('day_zhi', '?'), ck._is_sixiang(sz), exp))
    check('2. 基类 _is_sixiang 委托抽查 6 探针', not fails, '失败 %s' % fails if fails
          else '委托 is_sixiang_by_gan 单点出口')
except Exception as e:
    check('2. 基类 _is_sixiang 委托抽查', False, '异常 %r' % e)

# ── 3/5. 真实日期扫描 + 运行时管线探针 ───────────────────────────
from modules.四柱计算器 import calculate_sizhu
from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
from modules.shensha.修造神煞 import ConstructionShenShaChecker
from modules.shensha.拆舍神煞 import DemolitionShenShaChecker
from modules.shensha.动土神煞 import DiggingShenShaChecker
from modules.shensha.作灶神煞 import StoveShenShaChecker

_SIZHU_CACHE = {}


def _sizhu(y, m, d):
    key = (y, m, d)
    if key not in _SIZHU_CACHE:
        _SIZHU_CACHE[key] = calculate_sizhu(dt.datetime(y, m, d, 12, 0))
    return _SIZHU_CACHE[key]


def names_of(cls, sz):
    """真实 check() 管线，按 dict 列表解析 names（清单④）。异常上抛不吞。"""
    return [i.get('name', '') if isinstance(i, dict) else str(i)
            for i in cls().check(sz, {})]


def scan_month(month_zhi, year=2026):
    out = []
    d = dt.date(year, 1, 1)
    while d.year == year:
        sz = _sizhu(d.year, d.month, d.day)
        if sz.get('month_zhi') == month_zhi:
            out.append((d, sz))
        d += dt.timedelta(days=1)
    return out


try:
    yin = scan_month('寅')
    # 3. 旧支表复活反断言：寅月亥日且日干∉{丙,丁} → 四相不发射
    hai_non_cd = [(d, sz) for d, sz in yin
                  if sz.get('day_zhi') == '亥' and sz.get('day_gan') not in ('丙', '丁')]
    if hai_non_cd:
        d0, sz0 = hai_non_cd[0]
        n = names_of(ConstructionShenShaChecker, sz0)
        check('3. 旧支表复活反断言（寅月%s亥日，日干%s，管线）' % (d0, sz0.get('day_gan')),
              '四相' not in n, 'names 含四相 %s' % n if '四相' in n else '旧表 day_zhi 判据已断')
    else:
        check('3. 旧支表复活反断言', False, '2026 寅月无日干非丙丁之亥日，样本缺失须人工复核')

    # 5. 运行时管线：母仓（嫁娶回归典载集）+ 四相（按日干）
    hai_all = [(d, sz) for d, sz in yin if sz.get('day_zhi') == '亥']
    mao = [(d, sz) for d, sz in yin if sz.get('day_zhi') == '卯']
    bing_chen = [(d, sz) for d, sz in yin
                 if sz.get('day_gan') in ('丙', '丁') and sz.get('day_zhi') == '辰']
    jia_chen = [(d, sz) for d, sz in yin
                if sz.get('day_gan') not in ('丙', '丁') and sz.get('day_zhi') == '辰']
    ok5 = []
    if hai_all and mao:
        dh, sh = hai_all[0]
        dm, sm = mao[0]
        for cls in (MarriageShenShaChecker, RuZhaiShenShaChecker):
            lbl = '嫁娶' if cls is MarriageShenShaChecker else '入宅'
            ok5.append(check('5. %s 寅月%s日含母仓（典载集回归）' % (lbl, dh),
                             '母仓' in names_of(cls, sh)))
            ok5.append(check('5. %s 寅月%s日不含母仓（顺行集移除）' % (lbl, dm),
                             '母仓' not in names_of(cls, sm)))
        dup = names_of(MarriageShenShaChecker, sh)
        check('5a. 嫁娶母仓发射无重复（别名归一去重）',
              (dup.count('母仓') + dup.count('母仓日')) == 1,
              '计数 %d' % (dup.count('母仓') + dup.count('母仓日')))
    else:
        check('5. 母仓管线探针', False, '样本缺失（寅月亥日/卯日）')
    if bing_chen and jia_chen:
        db, sb = bing_chen[0]
        dj, sj = jia_chen[0]
        for cls in (ConstructionShenShaChecker, DemolitionShenShaChecker,
                    DiggingShenShaChecker, RuZhaiShenShaChecker, StoveShenShaChecker):
            lbl = {ConstructionShenShaChecker: '修造', DemolitionShenShaChecker: '拆舍(继承)',
                   DiggingShenShaChecker: '动土', RuZhaiShenShaChecker: '入宅',
                   StoveShenShaChecker: '作灶'}[cls]
            check('5. %s 寅月%s日(日干%s)含四相（新干表）' % (lbl, db, sb.get('day_gan')),
                  '四相' in names_of(cls, sb))
            check('5. %s 寅月%s日(日干%s)不含四相' % (lbl, dj, sj.get('day_gan')),
                  '四相' not in names_of(cls, sj))
    else:
        check('5. 四相管线探针', False, '样本缺失（寅月丙/丁辰日或非丙丁辰日）')
except Exception as e:
    check('3/5. 运行时管线探针', False, '异常 %r' % e)

# ── 4. 母仓表穷举 + 谓词唯一性 ───────────────────────────────────
MUCANG = {'寅': {'亥', '子'}, '卯': {'亥', '子'}, '辰': {'亥', '子'},
          '巳': {'寅', '卯'}, '午': {'寅', '卯'}, '未': {'寅', '卯'},
          '申': {'辰', '戌', '丑', '未'}, '酉': {'辰', '戌', '丑', '未'},
          '戌': {'辰', '戌', '丑', '未'}, '亥': {'申', '酉'}, '子': {'申', '酉'},
          '丑': {'申', '酉'}}
badm = []
for m in ZHI12:
    for dz in ZHI12:
        if ck._is_mucang({'month_zhi': m, 'day_zhi': dz}) != (dz in MUCANG[m]):
            badm.append('母仓 %s月%s' % (m, dz))
check('4. 母仓基类表穷举 12x12 硬锁（0误0漏，现状回归）', not badm,
      '违例 %s' % badm[:6] if badm else '《历例》"春亥子，夏寅卯，秋辰戌丑未，冬申酉"')

mod_dir = ROOT / 'modules'
defs_mucang, defs_sixiang = [], []
for p in sorted(mod_dir.rglob('*.py')):
    try:
        text = p.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        continue
    if re.search(r'^\s*def _is_mucang\b', text, re.M):
        defs_mucang.append(p.name)
    if re.search(r'^\s*def _is_sixiang\b', text, re.M):
        defs_sixiang.append(p.name)
check('4a. _is_mucang 全模块唯一（反断言子类重写复活）', defs_mucang == ['神煞基类.py'],
      '定义位 %s' % defs_mucang)
check('4b. _is_sixiang 全模块唯一', defs_sixiang == ['神煞基类.py'], '定义位 %s' % defs_sixiang)

# ── 6. 发射位唯一性静态扫描 ──────────────────────────────────────
expect_emit = {'母仓': {'神煞基类.py': 1, '出行神煞.py': 1, '开业神煞.py': 1,
                        '安葬神煞.py': 1, '安床神煞.py': 1},
               '母仓日': {'嫁娶神煞.py': 1, '入宅神煞.py': 1, '作灶神煞.py': 1,
                          '通用神煞.py': 1},
               '四相': {'修造神煞.py': 1, '动土神煞.py': 1, '入宅神煞.py': 1,
                        '作灶神煞.py': 1}}
for name, expect in expect_emit.items():
    got = {}
    for p in sorted(mod_dir.rglob('*.py')):
        try:
            t = p.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        cnt = len(re.findall(r"_add_shensha\('%s'" % name, t))
        if cnt:
            got[p.name] = cnt
    check('6. 发射位唯一性 %s' % name, got == expect,
          '实测 %s' % got if got != expect else '%d 处' % sum(expect.values()))

# ── 7. 墓碑在位 ──────────────────────────────────────────────────
base_text = (ROOT / 'modules' / 'shensha' / '神煞基类.py').read_text(encoding='utf-8')
jq_text = (ROOT / 'modules' / 'shensha' / '嫁娶神煞.py').read_text(encoding='utf-8')
rz_text = (ROOT / 'modules' / 'shensha' / '入宅神煞.py').read_text(encoding='utf-8')
check('7. 基类 _is_sixiang 旧支表墓碑在位', '墓碑（旧支表，勿复活）' in base_text)
check('7a. 嫁娶 _is_mucang 顺行表墓碑在位',
      '_is_mucang 子类重写删除' in jq_text and '顺行表' in jq_text and
      'def _is_mucang' not in jq_text)
check('7b. 入宅 _is_mucang 冗余表墓碑在位',
      '_is_mucang 子类重写删除' in rz_text and 'def _is_mucang' not in rz_text)

print('=' * 60)
print('verify_b6_mucang_sixiang：%s (exit %d)' % ('全部通过' if PASS else '存在失败',
                                                  0 if PASS else 1))
sys.exit(0 if PASS else 1)
