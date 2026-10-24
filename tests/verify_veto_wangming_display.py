# -*- coding: utf-8 -*-
"""
§59.3 否决日仙命信息展示验证（2026-10-07）

背景：此前 6+ 处一票否决提前返回（五行门槛/年月不宜/分金大凶/忌事否决等）
不构建 wangming_info/shanzuo_eval，veto 日仅渲染单行否决，无亡命段。
修补：仙命构建点前移至五行门槛审核之前，否决返回块补齐
  - 返回 dict 增 wangming_info / shanzuo_eval 键
  - score_details 增 仙命坐山得分/详情、仙命兼向得分/详情
  - reason 增 亡命（仙命）段、仙命×坐山段、仙命×兼向段
  - 坐山克仙命时标注"因否决未计算"（制化探测/双凶叠加通道未运行）

3 个 veto 日案例（2026-10-07 探针实测定位）：
  V1 正体大凶    2023-01-02 甲子亡命×丙山壬向
  V2 月份不宜    2023-09-15 甲子亡命×丙山壬向（月家五黄到坐山）
  V3 五行低分    2023-01-01 甲子亡命×丙山壬向（月三煞山向）
反向断言：
  R1 比和坐山（庚山甲向）的否决日 → 有仙命段、无"因否决未计算"标注
  R2 兼向坐山克（巽山乾向兼巳）的否决日 → 有仙命×兼向段
  R3 非安葬事项否决日 → 不带仙命段（不误扩）
  R4 正常日（非否决）→ 仙命段维持正常路径原有结构（无"因否决未计算"）

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


def dead(name='甲子', bd='1924-03-01'):
    return {'name': name, 'role': '死者', '性别': '男', 'birth_date': bd}


def run(d0, owners, shan='丙山壬向', jian=None, event='安葬'):
    sz = calculate_sizhu(d0, 12, 0)
    sz.update({'year': d0.year, 'month': d0.month, 'day': d0.day, 'date': d0})
    return calculate_score(sz, event, owners, None, shan, None, None, None,
                           jian_xiang=jian)


# ---------------------------------------------------------------------------
# V1/V2/V3：三类提前返回否决日，仙命信息完整性
# ---------------------------------------------------------------------------
print('== V. 否决日仙命信息完整性（§59.3）==')
_CASES = [
    ('V1 正体大凶', dt.date(2023, 1, 2)),
    ('V2 月份不宜', dt.date(2023, 9, 15)),
    # H4 批：原 2023-01-01 经 001 §153 分数清洗后已不触发五行早退
    # （改由仙命×坐山叠大忌否决），换现行五行低分早退日 2023-01-25（wx=14）。
    ('V3 五行低分', dt.date(2023, 1, 25)),
]
for tag, d0 in _CASES:
    r = run(d0, [dead()])
    wm = r.get('wangming_info')
    se = r.get('shanzuo_eval')
    sd = r.get('score_details') or {}
    rs = r.get('reason', '')
    check(f'{tag} {d0}：确为否决日（score=0，❌ 凶）',
          r.get('score') == 0 and r.get('level') == '❌ 凶'
          and bool(r.get('veto_reasons')))
    check(f'{tag}：wangming_info 携带（甲子/海中金/金）',
          bool(wm) and wm.get('年柱') == '甲子'
          and wm.get('纳音') == '海中金' and wm.get('五行') == '金')
    check(f'{tag}：shanzuo_eval 携带（坐山克仙命/-30/凶中之凶）',
          bool(se) and se.get('relation') == '坐山克仙命'
          and se.get('score') == -30 and se.get('level') == '凶中之凶')
    check(f'{tag}：score_details 仙命坐山得分=-30、详情非空',
          sd.get('仙命坐山得分') == -30 and bool(sd.get('仙命坐山详情')))
    check(f'{tag}：reason 含亡命（仙命）段',
          '亡命（仙命）：甲子，甲子年生，海中金命（金）' in rs)
    check(f'{tag}：reason 含仙命×坐山段（-30分，因否决未计入总分）',
          '仙命×坐山：' in rs and '（-30分，因否决未计入总分）' in rs)
    check(f'{tag}：reason 标注"因否决未计算"（坐山克仙命）',
          '因否决未计算' in rs)
    check(f'{tag}：仙命分仅披露不进总分（总分=0）',
          sd.get('总分') == 0)

# ---------------------------------------------------------------------------
# V4：多否决源叠加（五行门槛 + 相主硬门槛），仙命信息仍完整
# ---------------------------------------------------------------------------
print('== V4. 多否决源叠加（§59.3 验收后补）==')
# H4 批：原 2023-01-11 双否决已随 §62 方案二（2026-10-09，非婚嫁≥2 人自动
# 半权重）失效（孝子硬门槛降为扣分不否决）；且该日经 001 §153 清洗后
# 不再走五行早退。改取现行五行早退日 2023-03-24，第二事主显式
# _zaozhu_weight=1.0 保留硬门槛（显式打标优先于自动降权，§62 原机制）。
_owners4 = [dead(), {'name': '事主', 'role': '事主', '性别': '男',
                     'birth_date': '1947-06-15', '_zaozhu_weight': 1.0}]
_r4v = run(dt.date(2023, 3, 24), _owners4)
_vr4 = _r4v.get('veto_reasons') or []
check('V4 2023-03-24：双否决源（veto_reasons 含 五行门槛+相主硬门槛）',
      len(_vr4) == 2
      and any('五行' in str(v) for v in _vr4)
      and any('相主硬门槛' in str(v) for v in _vr4))
check('V4：wangming_info/shanzuo_eval 在多否决源下仍携带',
      bool(_r4v.get('wangming_info')) and bool(_r4v.get('shanzuo_eval')))
check('V4：reason 同时含两类否决与仙命段',
      '五行严重不合格' in _r4v.get('reason', '')
      and '亡命（仙命）' in _r4v.get('reason', '')
      and '仙命×坐山：' in _r4v.get('reason', ''))
check('V4：score_details 仙命坐山详情含"因否决未计入总分，仅披露"',
      '因否决未计入总分，仅披露'
      in (_r4v.get('score_details') or {}).get('仙命坐山详情', ''))

# ---------------------------------------------------------------------------
# R1：比和坐山的否决日 → 有仙命段、无"因否决未计算"标注
# ---------------------------------------------------------------------------
print('== R. 反向断言 ==')
# 探针：找一个庚山甲向（金，与甲子金比和）的否决日
_r1_date = None
_d = dt.date(2023, 1, 1)
while _d < dt.date(2023, 4, 1):
    _r = run(_d, [dead()], shan='庚山甲向')
    if _r.get('score', 1) == 0 and _r.get('veto_reasons'):
        _r1_date, _r1 = _d, _r
        break
    _d += dt.timedelta(days=1)
check('R1：找到庚山甲向（比和）否决日', _r1_date is not None)
if _r1_date:
    _se = _r1.get('shanzuo_eval') or {}
    check('R1：比和坐山否决日仍带仙命段',
          '亡命（仙命）' in _r1.get('reason', '')
          and '仙命×坐山：' in _r1.get('reason', ''))
    check('R1：比和坐山否决日无"因否决未计算"标注',
          '因否决未计算' not in _r1.get('reason', '')
          and _se.get('relation') == '比和')

# R2：兼向坐山克的否决日 → 有仙命×兼向段
_r2 = run(dt.date(2023, 1, 2), [dead()], shan='巽山乾向', jian='兼巳')
_se2 = _r2.get('shanzuo_eval') or {}
_jxe2 = _se2.get('兼向判定') or {}
check('R2：兼向否决日 shanzuo_eval 含兼向判定',
      bool(_jxe2) and _jxe2.get('relation') == '坐山克仙命')
check('R2：reason 含仙命×兼向段（穴线兼巳）',
      '仙命×兼向：穴线兼巳' in _r2.get('reason', ''))
check('R2：score_details 仙命兼向得分=-30、详情非空',
      (_r2.get('score_details') or {}).get('仙命兼向得分') == -30
      and bool((_r2.get('score_details') or {}).get('仙命兼向详情')))

# R3：非安葬事项否决日 → 不带仙命段（不误扩）
_r3 = run(dt.date(2023, 1, 2), [{'name': '张三', 'role': '事主', '性别': '男',
                                 'birth_date': '1990-05-01'}],
          shan='丙山壬向', event='修造')
check('R3：非安葬事项否决日 shanzuo_eval=None、reason 无亡命段',
      _r3.get('shanzuo_eval') is None
      and '亡命（仙命）' not in _r3.get('reason', ''))

# R4：正常日（非否决）→ 仙命段维持原有结构（无"因否决未计算"）
_r4 = run(dt.date(2024, 3, 16), [dead()], shan='艮山坤向')
check('R4：正常日（坐山生仙命+20）非否决、仙命段无"因否决未计算"',
      _r4.get('score', 0) > 0
      and '亡命（仙命）' in _r4.get('reason', '')
      and '因否决未计算' not in _r4.get('reason', ''))

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
