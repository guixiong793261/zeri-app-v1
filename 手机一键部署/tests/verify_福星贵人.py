# -*- coding: utf-8 -*-
"""
福星贵人正统落地验证（001 §169 时辰层专项）
============================================
覆盖：
1. 表值断言：FUXING_SHICHEN 十干表（甲寅/乙丑亥/丙子戌/丁酉/戊申/己未/庚午/辛巳/壬辰/癸卯）；
2. 食神自洽：与五鼠遁全网格闭环——时支在福星表 ⇔ 五鼠遁推出的时干恰为日干食神（同性所生）；
3. 评分器接入：辛巳日 10:00 calculate_score 福星条目 +10 且带 _std_event 戳；
4. 反例：壬日午时（2026-11-04 哨兵日 12:00）不触发，哨兵 226/上吉 零改判
   （§172 P0 大清理岁刑-12置0，214→226）；
5. 分值键：SHENSHA_SCORES 十四通道 ('XX','福星'):10 存在；
6. 嫁娶通道计分接入（001 §176）：辛巳日嫁娶 details 必含福星 +10 且审计
   counted_via_details=True；反向壬午日嫁娶不得出现福星计分项。

退出码：0＝全部通过；1＝存在断言失败（供 CI 集成）。
"""
import sys
import os
from datetime import date

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.shensha.时辰系 import (
    TIAN_GAN, DI_ZHI, WUSHU_DUN, FUXING_SHICHEN,
    get_fuxing_shichen, get_hour_gan_series,
)
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
from modules.事项标准 import SHENSHA_SCORES

FUXING_TRUTH = {
    '甲': ['寅'], '乙': ['丑', '亥'], '丙': ['子', '戌'], '丁': ['酉'],
    '戊': ['申'], '己': ['未'], '庚': ['午'], '辛': ['巳'],
    '壬': ['辰'], '癸': ['卯'],
}
FOURTEEN = ['嫁娶', '修造', '动土', '拆舍', '入宅', '开业', '出行',
            '安床', '作灶', '移徙', '入学', '求医', '签约', '安葬']

errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


# ---- 1. 表值 ----
for g in TIAN_GAN:
    check(sorted(FUXING_SHICHEN.get(g, [])) == sorted(FUXING_TRUTH[g]),
          f'表值：{g} 福星表 {FUXING_SHICHEN.get(g)} != 黄金基准 {FUXING_TRUTH[g]}')
check(set(FUXING_SHICHEN) == set(TIAN_GAN), '表值：福星表键集 ≠ 十干全集')

# ---- 2. 食神自洽（10 干 × 12 支全网格） ----
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
WUXING = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
          '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
YANG = {'甲', '丙', '戊', '庚', '壬'}
n_pos = n_neg = 0
for dg in TIAN_GAN:
    series = get_hour_gan_series(dg)
    expect = set(FUXING_TRUTH[dg])
    got = set()
    for i, zhi in enumerate(DI_ZHI):
        hg = series[i]
        is_shishen = (SHENG[WUXING[dg]] == WUXING[hg]) and ((dg in YANG) == (hg in YANG))
        in_table = zhi in get_fuxing_shichen(dg)
        check(is_shishen == in_table,
              f'食神闭环：{dg}日{zhi}时（时干{hg}）食神判定 {is_shishen} != 福星表 {in_table}')
        if in_table:
            got.add(zhi)
            n_pos += 1
        else:
            n_neg += 1
    check(got == expect, f'食神闭环：{dg} 福星支集 {sorted(got)} != 黄金基准 {sorted(expect)}')
check(n_pos == 12, f'食神闭环：全网格福星支总数 {n_pos} != 12（甲1+乙2+丙2+丁戊己庚辛壬癸各1）')

# ---- 3. 评分器接入：辛巳日 10:00 ----
d = date(2026, 1, 7)  # 辛巳日，10:00 巳时
sz = calculate_sizhu(d, 10, 0)
check(sz['day_gan'] == '辛' and sz.get('hour_zhi') == '巳',
      f'探针样本漂移：{d} 实测 {sz["day_gan"]}日{sz.get("hour_zhi")}时，应为辛日巳时')
sz.update({'year': 2026, 'month': 1, 'day': 7, 'date': d})
r = calculate_score(sz, '通用')
fx = [s for s in r.get('shensha_list', []) if isinstance(s, dict) and s.get('name') == '福星']
check(len(fx) == 1, f'评分器接入：辛巳日通用通道福星条目数 {len(fx)} != 1')
if fx:
    check(fx[0].get('score') == 10, f'评分器接入：福星分值 {fx[0].get("score")} != 10')
    check(fx[0].get('_std_event') == '通用', f'评分器接入：_std_event 戳 {fx[0].get("_std_event")} != 通用')

# 展示层同源：reason/wu_xing 吉神应含福星贵人
reason_txt = str(r.get('reason', '')) + str(r.get('wu_xing_result', ''))
check('福星贵人' in reason_txt, '展示层：reason/五行结果未含「福星贵人」展示')

# ---- 4. 反例与哨兵 ----
d2 = date(2026, 11, 4)  # 壬午日，12:00 丙午时
sz2 = calculate_sizhu(d2, 12, 0)
check(sz2['day_gan'] == '壬' and sz2.get('hour_zhi') == '午',
      f'哨兵样本漂移：{d2} 12:00 实测 {sz2["day_gan"]}日{sz2.get("hour_zhi")}时')
sz2.update({'year': 2026, 'month': 11, 'day': 4, 'date': d2})
r2 = calculate_score(sz2, '入宅')
fx2 = [s for s in r2.get('shensha_list', []) if isinstance(s, dict) and s.get('name') == '福星']
check(not fx2, '反例：壬日午时不应触发福星（午不在壬表）')
check(r2.get('score') == 226 and '上吉' in str(r2.get('level')),
      f'哨兵：2026-11-04 入宅 12:00 = {r2.get("score")}/{r2.get("level")}，冻结值 226/上吉（§172）遭改判')

# 婚嫁路径接入（同日）
r3 = calculate_score(sz, '嫁娶')
fx3 = [s for s in r3.get('shensha_list', []) if isinstance(s, dict) and s.get('name') == '福星']
check(len(fx3) == 1 and fx3[0].get('_std_event') == '嫁娶',
      '婚嫁路径：辛巳日嫁娶通道福星条目缺失或 _std_event 戳错误')

# ---- 5. 十四通道分值键 ----
for ev in FOURTEEN:
    v = SHENSHA_SCORES.get((ev, '福星'))
    check(v == 10, f'分值键：("{ev}","福星") = {v} != 10')

# ---- 6. 嫁娶通道计分接入（001 §176，2026-10-25 Q3 拍板方案A）----
# 修复前：嫁娶仅由评分器 _build_fuxing_shensha 写 shensha_list 展示 +10，
# 婚嫁算法无对应 details 项（"福星展示不计分"缺口）。本段正反双向锁死：
# 正向——辛巳日（辛表含巳）嫁娶 details 必含福星 +10，且阶段1审计
# counted_via_details=True；反向——壬午日（壬表含辰，午不在表）嫁娶不得
# 出现福星计分项。
r4 = calculate_score(sz, '嫁娶')
_fx_d = [x for x in (r4.get('marriage_details') or [])
         if isinstance(x, (list, tuple)) and len(x) >= 2 and '福星' in str(x[0])]
check(len(_fx_d) == 1 and _fx_d[0][1] == 10,
      f'嫁娶计分：辛巳日嫁娶 details 福星项应恰 1 条且分值 10，实际 {_fx_d}')
_fx_a = [a for a in (r4.get('shensha_audit') or []) if a.get('name') == '福星']
check(len(_fx_a) == 1 and _fx_a[0].get('contributed') == 0
      and _fx_a[0].get('counted_via_details') is True,
      f'嫁娶审计：福星 counted_via_details 应为 True（经 details 计分），实际 {_fx_a}')
r5 = calculate_score(sz2, '嫁娶')
_fx_d2 = [x for x in (r5.get('marriage_details') or [])
          if isinstance(x, (list, tuple)) and len(x) >= 1 and '福星' in str(x[0])]
check(not _fx_d2, f'嫁娶计分反向：壬午日（午不在壬表）嫁娶不得出现福星计分项，实际 {_fx_d2}')

# ---- 汇总 ----
print(f'表值断言：10 干；食神闭环：120 网格（福星支 {n_pos}/非福星 {n_neg}）；'
      f'评分器接入：通用/嫁娶两路径；嫁娶计分接入（§176）正反双向；'
      f'哨兵 226 零改判（§172）；十四通道键 14/14')
if errors:
    print(f'\n断言失败 {len(errors)} 项：')
    for e in errors:
        print(f'  ✗ {e}')
    sys.exit(1)
print('全部断言通过：福星贵人正统落地（001 §169）＋嫁娶计分接入（§176）六组验证零缺陷。')
sys.exit(0)
