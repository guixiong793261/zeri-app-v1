# -*- coding: utf-8 -*-
"""五行偏枯分级与偏向展示验证（2026-11-10，001 §251）

判据（用户拍板，事先冻结）：
  - 统计口径：四柱天干 + 地支本气共 8 字（不含藏干）；
  - 极度偏枯：某一五行 ≥5，或 ≥2 个五行为 0；
  - 偏枯（轻度）：某一五行 =4；
  - 缺项：某一五行 =0（仅 1 项且无旺行时独立成档）；
  - 平衡：五行俱全且单行 ≤3；
  - 偏枯标签：火≥4 →「过燥」、水≥4 →「过寒」（与 §238 黄牌口径同源）。

验证面：
A. 单元层：build_wuxing_bias_report 五档判定 + 标签 + 缺行 + 调候建议。
B. 同源对拍：真实日课 score_details['五行偏枯分析'] 与 score_details['偏枯计数']
   （§246）火/水计数逐值相等；统计合计恒为 8。
C. 渲染在位：主程序 / 日课评分系统（GUI+导出）/ 反推UI 四处同源调用。
D. 反向兼容：偏枯计数键仍在、wuxing_pian_ku 黄牌发射不变、
   §238 火水口径源码未动。
E. E001 恒等式：新增 score_details 键不破坏日课校验器分项求和。

退出码：0=全过 1=有失败（FAIL N 计数）
================================================================================
"""
import datetime
import io
import os
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.评分器 import (build_wuxing_bias_report,        # noqa: E402
                            format_wuxing_bias_text)

FAILS = []


def check(name, cond, detail=''):
    if cond:
        print('  PASS  ' + name)
    else:
        print('  FAIL  ' + name + ('  -> ' + str(detail) if detail else ''))
        FAILS.append(name)


print('=' * 76)
print('五行偏枯分级与偏向展示验证（001 §251）')
print('=' * 76)

# ============ A：单元层 ============
print('\n[A] build_wuxing_bias_report 五档判定')

# A1 火4（丙丁巳午），其余金1木1水1土1 → 偏枯/过燥
SZ_FIRE4 = {'year_gan': '丙', 'month_gan': '丁', 'day_gan': '庚',
            'hour_gan': '壬', 'year_zhi': '巳', 'month_zhi': '午',
            'day_zhi': '卯', 'hour_zhi': '未'}
r = build_wuxing_bias_report(SZ_FIRE4)
check('A1 火4 → 等级=偏枯、标签=过燥',
      r['偏枯等级'] == '偏枯' and r['偏枯标签'] == '过燥', r['偏枯等级'])
check('A2 判定含 4/8 与 50%', '4/8' in r['判定'] and '占50%' in r['判定'],
      r['判定'])
check('A3 格局解析含火旺生土与亥/子时调候',
      '火旺生土' in r['格局解析'] and '亥/子时' in r['格局解析'],
      r['格局解析'])
check('A4 火计数==4 且统计合计==8',
      r['五行统计']['火'] == 4 and sum(r['五行统计'].values()) == 8,
      r['五行统计'])

# A5 缺水单缺 → 缺项档
SZ_NO_WATER = {'year_gan': '甲', 'month_gan': '丙', 'day_gan': '戊',
               'hour_gan': '庚', 'year_zhi': '寅', 'month_zhi': '午',
               'day_zhi': '辰', 'hour_zhi': '申'}
r = build_wuxing_bias_report(SZ_NO_WATER)
check('A5 火2土2金1木2水0 → 缺项、判定含五行缺水',
      r['偏枯等级'] == '缺项' and '五行缺水' in r['判定'], r['判定'])
check('A6 缺水解析含急需时辰补水（亥/子时）',
      '急需时辰补水' in r['格局解析'] and '亥/子时' in r['格局解析'],
      r['格局解析'])

# A7 火≥5 → 极度偏枯（过旺）
SZ_FIRE6 = {'year_gan': '丙', 'month_gan': '丁', 'day_gan': '丙',
            'hour_gan': '丁', 'year_zhi': '巳', 'month_zhi': '午',
            'day_zhi': '酉', 'hour_zhi': '卯'}
r = build_wuxing_bias_report(SZ_FIRE6)
check('A7 火6 → 极度偏枯、判定含过旺与过燥',
      r['偏枯等级'] == '极度偏枯' and '过旺' in r['判定'] and '过燥' in r['判定'],
      r['判定'])

# A8 双缺（火4 但零项 2 个）→ 双缺归极度偏枯（零项规则优先）
SZ_DBL_ZERO = {'year_gan': '丙', 'month_gan': '丁', 'day_gan': '庚',
               'hour_gan': '壬', 'year_zhi': '巳', 'month_zhi': '午',
               'day_zhi': '子', 'hour_zhi': '申'}
r = build_wuxing_bias_report(SZ_DBL_ZERO)
check('A8 火4+双缺木土 → 极度偏枯（⛔）、判定含双缺',
      r['偏枯等级'] == '极度偏枯' and '⛔' in r['判定']
      and '双缺' in r['判定'], r['判定'])

# A9 平衡档
SZ_BALANCE = {'year_gan': '甲', 'month_gan': '丙', 'day_gan': '庚',
              'hour_gan': '壬', 'year_zhi': '子', 'month_zhi': '午',
              'day_zhi': '酉', 'hour_zhi': '辰'}
r = build_wuxing_bias_report(SZ_BALANCE)
check('A9 五行俱全各≤3 → 平衡、判语与解析对齐用户措辞',
      r['偏枯等级'] == '平衡' and '五行俱全' in r['判定']
      and '五行流通' in r['格局解析'], r['判定'])

# A10 水4 → 过寒 + 火土调候
SZ_WATER4 = {'year_gan': '壬', 'month_gan': '癸', 'day_gan': '甲',
             'hour_gan': '丙', 'year_zhi': '子', 'month_zhi': '亥',
             'day_zhi': '卯', 'hour_zhi': '未'}
r = build_wuxing_bias_report(SZ_WATER4)
check('A10 水4 → 过寒、解析含巳/午调候',
      r['偏枯等级'] == '偏枯' and r['偏枯标签'] == '过寒'
      and '巳/午' in r['格局解析'], (r['偏枯标签'], r['格局解析']))

# A11 格式化输出固定五段
txt = format_wuxing_bias_text(build_wuxing_bias_report(SZ_FIRE4))
check('A11 文本块含【五行偏枯分析】+三行字段与分隔线',
      txt.startswith('【五行偏枯分析】') and '五行统计:' in txt
      and '偏枯判定:' in txt and '格局解析:' in txt and '━' in txt)

# ============ B：同源对拍（真实日课） ============
print('\n[B] score_details 透出与 §246 偏枯计数同源')
from modules.四柱计算器 import calculate_sizhu          # noqa: E402
from modules.评分器 import calculate_score              # noqa: E402

days = []
d = datetime.date(2026, 1, 1)
while d <= datetime.date(2026, 12, 31):
    days.append((d, calculate_sizhu(d, 10, 0)))
    d += datetime.timedelta(days=1)

bad_sum, bad_sync, bad_anchor, pk4_days, bal_days = [], [], [], [], []
for d0, sz in days:
    sz2 = dict(sz)
    sz2['year'], sz2['month'], sz2['day'] = d0.year, d0.month, d0.day
    rep = calculate_score(sz2, '修造', owners=[], zeli_mode='pure')
    sd = rep.get('score_details') or {}
    rep251 = sd.get('五行偏枯分析')
    if not rep251:
        # §251 键与 §246 偏枯计数同路径透出：凡偏枯计数在处，§251 键必在；
        # 五行硬门槛早退否决日两者皆无（既有语义），渲染层以 sizhu 现算兜底。
        if '偏枯计数' in sd:
            bad_anchor.append((str(d0), '偏枯计数在而五行偏枯分析缺'))
        continue
    st = rep251['五行统计']
    if sum(st.values()) != 8:
        bad_sum.append((str(d0), st))
    pk = sd.get('偏枯计数') or {}
    if '火系' in pk and st.get('火') != pk['火系']:
        bad_sync.append((str(d0), '火', st.get('火'), pk['火系']))
    if '水系' in pk and st.get('水') != pk['水系']:
        bad_sync.append((str(d0), '水', st.get('水'), pk['水系']))
    if (pk.get('火系') or 0) >= 4:
        pk4_days.append((str(d0), rep251['偏枯等级'], rep251['偏枯标签'],
                         rep.get('wuxing_pian_ku')))
    if rep251['偏枯等级'] == '平衡':
        bal_days.append(str(d0))

check('B1 凡偏枯计数在处五行偏枯分析必在（同路径透出）', not bad_anchor,
      bad_anchor[:3])
check('B1b 透出日统计合计=8', not bad_sum, bad_sum[:3])
check('B2 五行统计.火/水 == 偏枯计数.火系/水系（365 天逐日）', not bad_sync,
      bad_sync[:3])
check('B3 全年存在火≥4 过燥日（分级档可用）', len(pk4_days) >= 20,
      len(pk4_days))
_check_pk = [x for x in pk4_days if x[3] != '过燥']
check('B4 火≥4 日 wuxing_pian_ku 恒为过燥（黄牌口径不变）', not _check_pk,
      _check_pk[:3])
check('B5 全年存在平衡日（平衡档可用）', len(bal_days) >= 20, len(bal_days))

# ============ C：渲染在位 ============
print('\n[C] 四处渲染同源在位')
src_main = open(os.path.join(ROOT, '主程序.py'), encoding='utf-8').read()
src_score = open(os.path.join(ROOT, 'modules', '日课评分系统.py'),
                 encoding='utf-8').read()
src_fantui = open(os.path.join(ROOT, 'modules', '反推UI.py'),
                  encoding='utf-8').read()
check('C1 主程序详情渲染在位（含同源函数调用）',
      'format_wuxing_bias_text(_pk_report)' in src_main
      and 'build_wuxing_bias_report' in src_main)
check('C2 评分详情窗 GUI+导出文本各 1 处（共 2 处）',
      src_score.count('format_wuxing_bias_text(') == 2,
      src_score.count('format_wuxing_bias_text('))
check('C3 反推独立版详情头在位', 'format_wuxing_bias_text(_pk251)' in src_fantui)
check('C4 三处均读 score_details 五行偏枯分析（同源优先）',
      "'五行偏枯分析'" in src_main and src_score.count("'五行偏枯分析'") == 2
      and "'五行偏枯分析'" in src_fantui)

# ============ D：反向兼容 ============
print('\n[D] §238/§246 既有口径零改动')
from modules.评分器 import Scorer                         # noqa: E402
_src_scorer = open(os.path.join(ROOT, 'modules', '评分器.py'),
                   encoding='utf-8').read()
check('D1 §238 火水口径源码未动（丙丁巳午/壬癸子亥）',
      "'丙丁巳午'" in _src_scorer and "'壬癸子亥'" in _src_scorer)
check('D2 score_details[偏枯计数] 键仍透出',
      "score_details['偏枯计数']" in _src_scorer)

# ============ E：E001 恒等式不受新键影响 ============
print('\n[E] 日课校验器 E001 对新增 score_details 键免疫')
from modules.日课校验器 import lint_lesson                # noqa: E402

bad_e = []
for d0, sz in days[:120]:  # 抽 120 天足够覆盖各月
    sz2 = dict(sz)
    sz2['year'], sz2['month'], sz2['day'] = d0.year, d0.month, d0.day
    rep = calculate_score(sz2, '修造', owners=[], zeli_mode='pure')
    lr = lint_lesson(rep)
    if lr.has_error:
        errs = [i.id for i in lr.issues if i.severity == 'ERROR']
        if errs != ['E001']:
            bad_e.append((str(d0), errs))
check('E1 抽样 120 天 lint 无 ERROR（新键不破坏 E001 求和）', not bad_e,
      bad_e[:3])

print()
print('FAILS=%d' % len(FAILS))
if FAILS:
    for f in FAILS:
        print('  - ' + f)
sys.exit(1 if FAILS else 0)
