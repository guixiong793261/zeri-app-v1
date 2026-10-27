# -*- coding: utf-8 -*-
"""
§59.11 太阳到山文案区分验证（2026-10-07）

命理差异：太阳到坐山对"坐山克仙命"是正照对症（直接照化坐山之凶），
对"仙命真冲"是间接增吉。原 _detect_wm_resolvers 对两场景不区分权重，
太阳到山与天德等均布尔命中、文案无差别。

落地（仅文案层，判定层维持宽集布尔口径不变）：
1. 坐山克仙命场景命中太阳到山时，制化吉神列表改写为
   "太阳到坐山正照制化"并置顶（相对天德/月德等其他化解）；
2. 真冲场景维持原"太阳到山"文案（不标正照）；
3. shanzuo_eval['制化吉神']/reason/ji_list 三处同步。

正向案例（2026-10-07 探针实测；T1 经 §186 重冻）：
  T1 2022-06-07 甲子×丙山壬向 → [太阳到坐山正照制化, 月德]
       （§186：原 2023-06-06 乙未日犯年重丧+三丧，大凶日一票否决短路，
       制化探测不运行；2019-2030 全扫"正照+六合"组合 0 候选，
       取语义等价替代日 2022-06-07，保持"正照置顶"语义核心）
  T2 2023-06-13 甲子×丙山壬向 → [太阳到坐山正照制化, 天德, 三合]
反向断言：
  R1 真冲场景命中太阳到山 → 文案仍为"太阳到山"（无"正照"）
  R2 坐山克无太阳到山 → 文案无"正照"字样（不误标）
退出码：全过 0，失败 1。
"""
import os
import sys
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.四柱计算器 import calculate_sizhu  # noqa: E402
from modules.评分器 import calculate_score  # noqa: E402

PASS, FAIL = [], []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(('  OK ' if cond else '  FAIL ') + name)


def run(d0, owners, shan='丙山壬向'):
    sz = calculate_sizhu(d0, 12, 0)
    sz.update({'year': d0.year, 'month': d0.month, 'day': d0.day, 'date': d0})
    return calculate_score(sz, '安葬', owners, None, shan, None, None, None)


_DEAD = [{'name': '甲子', 'role': '死者', '性别': '男', 'birth_date': '1924-03-01'}]

# ---------------------------------------------------------------------------
# T1/T2：坐山克仙命 + 太阳到山 → "太阳到坐山正照制化"置顶
# ---------------------------------------------------------------------------
print('== T. 坐山克×太阳到山 正照制化（§59.11）==')
for tag, d0, expect_rest in [
        ('T1', dt.date(2022, 6, 7), ['月德']),   # §186 重冻：原 2023-06-06 犯年重丧+三丧
        ('T2', dt.date(2023, 6, 13), ['天德', '三合'])]:
    r = run(d0, _DEAD)
    se = r.get('shanzuo_eval') or {}
    hj = se.get('制化吉神') or []
    check(f'{tag} {d0}：坐山克仙命有制化（不否决）',
          se.get('relation') == '坐山克仙命' and se.get('_with_huajie'))
    check(f'{tag}：制化吉神首项=太阳到坐山正照制化（置顶）',
          bool(hj) and hj[0] == '太阳到坐山正照制化')
    check(f'{tag}：制化吉神其余项={expect_rest}（相对顺序不变）',
          hj[1:] == expect_rest)
    check(f'{tag}：reason 含"有制化：太阳到坐山正照制化"',
          '（有制化：太阳到坐山正照制化' in se.get('reason', ''))
    check(f'{tag}：reason 不再含裸"太阳到山"（已改写为正照）',
          '太阳到山' not in se.get('reason', '').replace('太阳到坐山正照制化', ''))
    check(f'{tag}：ji_list 坐山克仙命忌项同步正照文案',
          any('坐山克仙命（有制化：太阳到坐山正照制化' in str(j)
              for j in r.get('ji_list', [])))

# ---------------------------------------------------------------------------
# R1：真冲场景命中太阳到山 → 维持"太阳到山"，不标正照
# ---------------------------------------------------------------------------
print('== R. 反向断言 ==')
# R1：真冲场景命中太阳到山 → 维持"太阳到山"，不标正照
# 探针实测案例：2023-06-17 甲子×丙山壬向，相主详情真冲行
# "（有制化：月德、太阳到山）"
_r1 = run(dt.date(2023, 6, 17), _DEAD)
_r1_xz = [str(x) for x in (_r1.get('score_details') or {}).get('相主详情', [])]
_r1_hit = next((x for x in _r1_xz if '真冲' in x and '有制化' in x), None)
check('R1：2023-06-17 真冲行含制化标注', _r1_hit is not None)
if _r1_hit is not None:
    check('R1：真冲制化文案含"太阳到山"',
          '太阳到山' in _r1_hit)
    check('R1：真冲制化文案无"正照"（仅坐山克标正照）',
          '正照' not in _r1_hit)

# R2：坐山克但无太阳到山（其他吉神制化）→ 无"正照"字样
_r2 = None
_d = dt.date(2023, 1, 1)
while _d < dt.date(2025, 12, 31):
    _r = run(_d, _DEAD)
    _se = _r.get('shanzuo_eval') or {}
    _hj = _se.get('制化吉神') or []
    if _se.get('_with_huajie') and _hj and not any('太阳' in str(x) for x in _hj):
        _r2, _r2_hj = _r, _hj
        break
    _d += dt.timedelta(days=1)
check('R2：找到坐山克无太阳到山（其他吉神制化）案例', _r2 is not None)
if _r2 is not None:
    check('R2：制化吉神无"正照"字样',
          not any('正照' in str(x) for x in _r2_hj))
    check('R2：reason 无"正照"字样',
          '正照' not in (_r2.get('shanzuo_eval') or {}).get('reason', ''))

# ---------------------------------------------------------------------------
print('=' * 60)
print(f'PASS {len(PASS)}  FAIL {len(FAIL)}')
if FAIL:
    print('FAILED ITEMS:')
    for f in FAIL:
        print('  - ' + f)
    sys.exit(1)
print('ALL PASS')
sys.exit(0)
