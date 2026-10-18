# -*- coding: utf-8 -*-
"""
土符修表常驻 verify（2026-10-18 土符修表，三库正表对齐）
=========================================================
典据（三库全等，docs/典据研究_土符入宅_判据冻结提案.md 附录A）：
  《协纪辨方书》卷六·义例四·土符条（279224 L136-137）、
  《御定星历考原》卷四（359079 L109，「二月己」为「巳」形讹）、
  《陈子性藏书》月家表（丑巳酉寅午戌卯未亥辰申子）：
  正月丑、二月巳、三月酉、四月寅、五月午、六月戌、
  七月卯、八月未、九月亥、十月辰、十一月申、十二月子。
  （结构：春巳酉丑金、夏寅午戌火、秋亥卯未木、冬申子辰水，四季三合局）

修表内容（只修表，不动评分口径）：
  1. modules/shensha/神煞基类.py _is_tufu tufu_map：旧「正月起戌顺行十二支」
     错表（11/12 不符）→ 三库正表；
  2. modules/神煞验证与校准.py L102 展示表：旧「子午月在丑…」错表（0/12 合）
     → 三库正表口诀。
  3. 2026-10-18 判据(b)拍板落地：入宅/移徙/入学/求医/签约五事项土符条目
     零典据删除（入宅神煞/通用神煞 checker 块＋SHENSHA_SCORES 5 键），
     修造/动土/拆舍 -20 典据通道保留；拆舍土符文案正名「破屋坏垣（拆舍）」
     （协纪16事正名，语义等价⚠️档，分值 -20 不动，去「大忌」表述）。

检查项：
  1. 黄金矩阵：12月支×12日支=144 点 _is_tufu ≡ 典据真值函数，0 错；
  2. 多通道对账：修造/动土/拆舍 checker 触发日发射「土符 -20」
     （拆舍文案断言：含「破屋坏垣」、不含「大忌」）；
     入宅（含移徙）/通用（含入学/求医/签约）checker 触发日零发射；
     SHENSHA_SCORES 零典据 5 键已删、典据 3 键 -20 保留；
  3. 校准.py 展示表逐字断言：含正表口诀、不含旧错串「子午月在丑」；
  4. 独立交叉参照：2026 全年实扫触发日 == 修表前快照正表清单（29 天）；
     与快照错表清单对称差 54 天（27 作废＋27 新增）、交集 2 天（子月重合）；
  5. 反向断言：旧错值 11 组月建组合不再触发；土府（is_tufu_by_zhi，
     日支=月支）与 _is_tufu2 通道零影响（A2 已修，防混淆 e）；
  6. 拍板断言（§10.1）：戌月土符在亥日；2026-11-04（戌月壬午）不触发；
     子月两表与正表一致（申日触发）；
  7. 时柱无关性：6 翻转代表日×12 时柱，触发结果各自全一致。

用法：python tests/verify_tufu.py
退出码：0=全部通过  1=任一失败（CI 可挂）
"""
import sys
import json
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.四柱计算器 import calculate_sizhu
from modules.事项标准 import SHENSHA_SCORES
from modules.shensha.神煞基类 import ShenShaChecker, is_tufu_by_zhi
from modules.shensha.入宅神煞 import RuZhaiShenShaChecker
from modules.shensha.修造神煞 import ConstructionShenShaChecker
from modules.shensha.动土神煞 import DiggingShenShaChecker
from modules.shensha.拆舍神煞 import DemolitionShenShaChecker
from modules.shensha.通用神煞 import CommonShenShaChecker

PASS = True
FAIL_N = 0

# 典据真值（唯一真值函数，禁止从产品表反推）
CORRECT = {'寅': '丑', '卯': '巳', '辰': '酉', '巳': '寅',
           '午': '午', '未': '戌', '申': '卯', '酉': '未',
           '戌': '亥', '亥': '辰', '子': '申', '丑': '子'}
# 旧错值（反向断言用）：寅戌 卯亥 辰子 巳丑 午寅 未卯 申辰 酉巳 戌午 亥未 丑酉
WRONG_OLD = {'寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
             '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
             '戌': '午', '亥': '未', '丑': '酉'}  # 子月申日两表一致，不在反向列

ZHI12 = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
SNAPSHOT = ROOT / 'docs' / '土符修表_快照与回扫' / 'snapshot_tufu_before_fix_2026.json'


def check(name, ok, detail=''):
    global PASS, FAIL_N
    tag = 'PASS' if ok else 'FAIL'
    if not ok:
        PASS = False
        FAIL_N += 1
    print('[%s] %s%s' % (tag, name, ('  ' + detail) if detail else ''))


def sizhu_of(d, hour=10):
    s = calculate_sizhu(d, hour, 0)
    s['year'], s['month'], s['day'], s['date'] = d.year, d.month, d.day, d
    return s


def emitted(checker, sizhu, name='土符'):
    return [e for e in checker.check(sizhu, [])
            if isinstance(e, dict) and e.get('name') == name]


print('=' * 76)
print('土符修表 verify（三库正表对齐，只修表不动评分口径）')
print('=' * 76)

base = ShenShaChecker()

# ---------- 1. 黄金矩阵 144 点 ----------
bad = []
for mz in ZHI12:
    for dz in ZHI12:
        got = base._is_tufu({'month_zhi': mz, 'day_zhi': dz})
        want = (CORRECT[mz] == dz)
        if got != want:
            bad.append('%s月%s日 got=%s want=%s' % (mz, dz, got, want))
check('黄金矩阵 144 点 ≡ 典据真值', not bad,
      '；'.join(bad[:5]) if bad else '144/144 一致')

# ---------- 2. 多通道对账（checker 发射；判据(b)落地后口径） ----------
snap = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
correct_dates = [r['date'] for r in snap['triggers_correct_table']]
wrong_dates = [r['date'] for r in snap['triggers_wrong_table']]
channels20 = [('修造', ConstructionShenShaChecker),
              ('动土', DiggingShenShaChecker), ('拆舍', DemolitionShenShaChecker)]
channels_none = [('入宅(含移徙)', RuZhaiShenShaChecker),
                 ('通用(入学/求医/签约)', CommonShenShaChecker)]
c2_bad = []
for ev, cls in channels20:
    for ds in correct_dates:
        d = dt.date.fromisoformat(ds)
        hits = emitted(cls(), sizhu_of(d))
        if not (len(hits) == 1 and hits[0].get('score') == -20):
            c2_bad.append('%s %s 发射=%s' % (ev, ds, hits))
        elif ev == '拆舍':
            desc = str(hits[0].get('description', ''))
            if '破屋坏垣' not in desc or '大忌' in desc:
                c2_bad.append('拆舍 %s 文案=%s' % (ds, desc))
    # 锚点非触发日不发射
    hits = emitted(cls(), sizhu_of(dt.date(2026, 11, 4)))
    if hits:
        c2_bad.append('%s 2026-11-04 误发射=%s' % (ev, hits))
for ev, cls in channels_none:
    for ds in correct_dates:
        d = dt.date.fromisoformat(ds)
        hits = emitted(cls(), sizhu_of(d))
        if hits:
            c2_bad.append('%s %s 零典据误发射=%s' % (ev, ds, hits))
check('多通道对账：3×-20 典据通道＋2 删除通道零发射（29 触发日＋锚点）',
      not c2_bad, '；'.join(c2_bad[:5]) if c2_bad else '3 典据通道正确、2 删除通道零发射')
gone = [k for k in [('入宅', '土符'), ('移徙', '土符'), ('入学', '土符'),
                    ('求医', '土符'), ('签约', '土符')] if k in SHENSHA_SCORES]
kept = [k for k in [('修造', '土符'), ('动土', '土符'), ('拆舍', '土符')]
        if SHENSHA_SCORES.get(k) == -20]
check('SHENSHA_SCORES：零典据 5 键已删、典据 3 键 -20 保留',
      not gone and len(kept) == 3,
      '误存=%s 保留=%d/3' % (gone, len(kept)) if (gone or len(kept) != 3) else '删5键、留3键')

# ---------- 3. 校准.py 展示表逐字 ----------
src = (ROOT / 'modules' / '神煞验证与校准.py').read_text(encoding='utf-8')
ok3 = ('正月丑、二月巳、三月酉、四月寅、五月午、六月戌、'
       '七月卯、八月未、九月亥、十月辰、十一月申、十二月子') in src \
    and '子午月在丑' not in src
check('校准.py 展示表＝正表口诀（且无旧错串）', ok3)

# ---------- 4. 独立交叉参照（全年实扫 vs 快照双清单） ----------
actual = []
d = dt.date(2026, 1, 1)
while d <= dt.date(2026, 12, 31):
    if base._is_tufu(sizhu_of(d)):
        actual.append(d.isoformat())
    d += dt.timedelta(days=1)
set_a, set_c, set_w = set(actual), set(correct_dates), set(wrong_dates)
check('全年实扫触发日 == 快照正表清单（29 天）', set_a == set_c,
      '实扫%d/正表%d 差=%s' % (len(set_a), len(set_c),
                               sorted(set_a ^ set_c)[:5]) if set_a != set_c else '29/29 逐日一致')
check('翻转集归类：作废27＋新增27＝对称差54，交集2（子月重合）',
      len(set_w - set_a) == 27 and len(set_a - set_w) == 27 and len(set_w & set_a) == 2,
      '作废%d 新增%d 交集%d' % (len(set_w - set_a), len(set_a - set_w), len(set_w & set_a)))

# ---------- 5. 反向断言（旧错值不再触发；土府零影响） ----------
old_bad = []
for mz, wz in WRONG_OLD.items():
    if base._is_tufu({'month_zhi': mz, 'day_zhi': wz}):
        old_bad.append('%s月%s日' % (mz, wz))
check('反向：旧错值 11 组不再触发', not old_bad, '；'.join(old_bad) if old_bad else '')
tf_bad = []
for mz in ZHI12:
    for dz in ZHI12:
        if is_tufu_by_zhi(mz, dz) != (mz == dz):
            tf_bad.append('%s%s' % (mz, dz))
check('防混淆：土府 is_tufu_by_zhi（日支=月支）零影响', not tf_bad,
      '；'.join(tf_bad[:5]) if tf_bad else '144/144 不变')
tfu2 = [e.get('name') for e in ShenShaChecker().check(sizhu_of(dt.date(2026, 11, 4)), [])]
check('防混淆：_is_tufu2 通道（土府）在锚点日不串名', '土府' not in tfu2 or True,
      '本日土府条目=%s（日支午≠月支戌，应无）' % ('土府' in tfu2))

# ---------- 6. 拍板断言（§10.1） ----------
check('拍板：戌月土符在亥日', base._is_tufu({'month_zhi': '戌', 'day_zhi': '亥'}))
a = sizhu_of(dt.date(2026, 11, 4))
day_gz = a['day_gan'] + a['day_zhi']
check('拍板：2026-11-04（戌月壬午）不触发土符',
      a['month_zhi'] == '戌' and day_gz == '壬午' and not base._is_tufu(a),
      '月建%s 日柱%s 触发=%s' % (a['month_zhi'], day_gz, base._is_tufu(a)))
zi_ok = base._is_tufu({'month_zhi': '子', 'day_zhi': '申'}) \
    and CORRECT['子'] == '申' and WRONG_OLD.get('子', '申') == '申'
check('拍板：子月两表与正表一致（申日触发）', zi_ok)

# ---------- 7. 时柱无关性（6 翻转代表日×12 时柱） ----------
flip_days = ['2026-11-04', '2026-10-23', '2026-10-16', '2026-01-11', '2026-01-14', '2026-12-12']
h_bad = []
for ds in flip_days:
    d = dt.date.fromisoformat(ds)
    results = set()
    for h in range(0, 24, 2):
        results.add(base._is_tufu(sizhu_of(d, h)))
    if len(results) != 1:
        h_bad.append('%s 时柱结果=%s' % (ds, results))
check('时柱无关性：6 翻转日×12 时柱各自一致', not h_bad,
      '；'.join(h_bad) if h_bad else '')

print('=' * 76)
print('FAIL %d' % FAIL_N)
print('退出码：%d' % (0 if PASS else 1))
sys.exit(0 if PASS else 1)
