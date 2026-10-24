# -*- coding: utf-8 -*-
"""§62 验证：方案二多人口自动主次打标 + 分金/正体大凶改强扣分（2026-10-09 拍板）。

拍板内容：
1. 方案二：非婚嫁类、事主≥2、无显式打标 → 首位主事人 1.0、其余家眷 0.5，
   辅助成员[硬性门槛]降为半权重扣分不否决（复用作灶 _zaozhu_weight 机制）。
2. 分金大凶：一票否决 → 强扣分（通道真实分值，实测 -34~-40），保留忌项标记；
   正体大凶同通道同处置（避免正向否决/兼向不否决倒挂）。

§67（2026-10-12）：B6 断言按 §63 口径更新——月份不宜类（三煞占月=
山家三煞忌子月）已降级强扣分不否决、落忌事明细，原断言否决串查'月份不宜'
字面过期；共线否决改查相主硬门槛+五行大忌两条门槛（B6a-d 四断言）。

退出码：全过 0，有失败 1。
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # §68 基建：相对定位，worktree 对拍可用
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer

FAILS = []


def check(name, cond, detail=''):
    tag = 'PASS' if cond else 'FAIL'
    print(f'[{tag}] {name}' + (f' | {detail}' if detail and not cond else ''))
    if not cond:
        FAILS.append(name)


OWN4 = [
    {'name': '', '性别': '男', 'birth_date': '1972-01-08', 'birth_hour': 8, 'birth_minute': 0},
    {'name': '', '性别': '女', 'birth_date': '1971-05-11', 'birth_hour': 8, 'birth_minute': 0},
    {'name': '', '性别': '男', 'birth_date': '1994-10-28', 'birth_hour': 4, 'birth_minute': 0},
    {'name': '', '性别': '男', 'birth_date': '1998-10-13', 'birth_hour': 0, 'birth_minute': 0},
]
OWNER1 = [dict(OWN4[0])]
SHAN_EVENTS = {'修造', '动土', '拆舍', '安葬', '作灶', '安床', '入宅'}


def run(d, ev, owners, shan=None):
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d; sz['year'] = d.year; sz['month'] = d.month; sz['day'] = d.day
    sx = shan or ('坤山艮向兼未' if ev in SHAN_EVENTS else None)
    return Scorer().score(sz, ev, owners=owners, shan_xiang=sx)


# ── A. 方案二自动打标 ──
owners = [dict(o) for o in OWN4]
run(dt.date(2024, 6, 8), '修造', owners)
check('A1 修造4人口自动打标 首位1.0', owners[0].get('_zaozhu_weight') == 1.0)
check('A2 其余家眷0.5', all(o.get('_zaozhu_weight') == 0.5 for o in owners[1:]))

owners_m = [dict(o) for o in OWN4]
run(dt.date(2024, 6, 8), '嫁娶', owners_m)
check('A3 婚嫁类不打标（双方皆主事人）', '_zaozhu_weight' not in owners_m[0])

owners_e = [dict(o) for o in OWN4]
owners_e[2]['_zaozhu_weight'] = 0.7
run(dt.date(2024, 6, 8), '修造', owners_e)
check('A4 显式打标不覆盖',
      '_zaozhu_weight' not in owners_e[0] and owners_e[2]['_zaozhu_weight'] == 0.7)

owners_s = [dict(o) for o in OWNER1]
run(dt.date(2024, 6, 8), '修造', owners_s)
check('A5 单事主不打标', '_zaozhu_weight' not in owners_s[0])

# A6 半权重效果：辅助成员被冲不否决。
# 事主年命：事主1=亥（1972-01-08 立春前属辛亥）、事主2=亥、事主3=戌、事主4=寅。
# 取日支辰日：主事人（亥）不冲辰，辅助者3（戌）冲辰——单人口无相主否决；
# 4人口若辅助者仍否决则方案二未生效，不否决则生效。
d_aux = None
d = dt.date(2024, 1, 1)
while d <= dt.date(2024, 12, 31):
    sz = calculate_sizhu(d, 12, 0)
    if sz.get('day_zhi') == '辰':
        d_aux = d
        break
    d += dt.timedelta(days=1)
check('A6 前置：找到辅助者年命被冲样本日', d_aux is not None, str(d_aux))
if d_aux:
    r4 = run(d_aux, '修造', [dict(o) for o in OWN4])
    vrs4 = [str(v) for v in (r4.get('veto_reasons') or [])]
    r1 = run(d_aux, '修造', [dict(o) for o in OWNER1])
    vrs1 = [str(v) for v in (r1.get('veto_reasons') or [])]
    check('A6a 单人口：主事人未冲则不否决',
          not any('相主硬门槛' in v for v in vrs1),
          '; '.join(vrs1))
    check('A6b 4人口：辅助者被冲不再否决',
          not any('相主硬门槛' in v for v in vrs4),
          '; '.join(vrs4))

# ── B. 分金/正体大凶强扣分 ──
# B1-B3 端到端样本：2027-11-14 乾山巽向兼亥（全年扫描确认无其他否决来源）
r = run(dt.date(2027, 11, 14), '修造', [dict(o) for o in OWNER1], shan='乾山巽向兼亥')
vrs = [str(v) for v in (r.get('veto_reasons') or [])]
jl = [str(j) for j in (r.get('ji_list') or [])]
bd = (r.get('wu_xing_result') or {}).get('score_breakdown') or {}
check('B1 分金大凶日不再否决', not vrs, '; '.join(vrs))
check('B2 忌项保留分金大凶标记', any('分金大凶' in j for j in jl))
check('B3 分金扣分=通道真实值(-35)', bd.get('分金扣分') == -35,
      f"实际={bd.get('分金扣分')}")
# B4 无双扣：breakdown 数值键加总（除相主披露键）== 五行分
wx_sc = (r.get('wu_xing_result') or {}).get('score')
_bd_sum = sum(v for k, v in bd.items()
              if isinstance(v, (int, float)) and k not in ('忌事明细', '相主得分'))
check('B4 breakdown加总==五行分（忌事不含分金条目）', _bd_sum == wx_sc,
      f'加总={_bd_sum} 五行分={wx_sc}')
# B5 文案已改强扣分
check('B5 忌项文案为强扣分',
      any('分金大凶' in j and '强扣分' in j for j in jl),
      str([j for j in jl if '分金大凶' in j]))

# B6 共线日仍由其他门槛否决（2027-01-02 坤山艮向兼未：相主+五行大忌，非分金）。
# §67（2026-10-12）按 §63 口径更新：月份不宜类（三煞占月=山家三煞忌子月）已
# 降级强扣分不否决、落忌事明细；共线否决改查相主硬门槛+五行大忌。
# H4 批（测试基建清零）：原锚点 2027-12-10 经口径收口批（001 §153）
# 神煞分清洗后五行分升至 33（≥30 放宽线）→ 五行门槛不再触发，
# 改取现行仍双门槛共线的 2027-01-02（实测 wx=18，五行+相主双否决）。
r2 = run(dt.date(2027, 1, 2), '修造', [dict(o) for o in OWN4])
vrs2 = [str(v) for v in (r2.get('veto_reasons') or [])]
mx2 = [str(x) for x in ((r2.get('wu_xing_result') or {}).get('score_breakdown') or {}).get('忌事明细') or []]
check('B6a 月份类共线项降级强扣分保留（山家三煞忌子月，§63 拍板E）',
      any('山家三煞' in x and '忌子月' in x for x in mx2),
      str([x for x in mx2 if '山家三煞' in x]))
check('B6b 共线否决仍在：相主硬门槛一票否决',
      any('相主硬门槛' in v for v in vrs2), '; '.join(vrs2))
check('B6c 共线否决仍在：五行大忌门槛',
      any('五行' in v and '坚决不用' in v for v in vrs2), '; '.join(vrs2))
check('B6d 分金非否决（§62 方案二语义保持）',
      not any('分金大凶' in v for v in vrs2), '; '.join(vrs2))

# ── C. 等价性：单事主普通日无分金触发时 breakdown 无分金键 ──
r3 = run(dt.date(2024, 6, 8), '修造', [dict(o) for o in OWNER1])
bd3 = (r3.get('wu_xing_result') or {}).get('score_breakdown') or {}
check('C1 普通吉日无分金扣分键', '分金扣分' not in bd3)

print()
if FAILS:
    print(f'FAIL {len(FAILS)}: ' + ', '.join(FAILS))
    sys.exit(1)
print('ALL PASS')
sys.exit(0)
