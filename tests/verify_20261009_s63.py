# -*- coding: utf-8 -*-
"""§63 验证：三煞D（年煞否、月煞扣）+ 月份不宜E（飞星否、其余扣）（2026-10-09 拍板）。

拍板内容（报告 538f081 推荐组合）：
1. 三煞 D：年三煞犯山向维持否决；三煞占月/月三煞犯山向降级强扣分不否决。
   防双扣：三煞占月与主流程 year_sansha_month_fan(-30) 同一判定，月层不传导；
   月三煞(山向) 扣分由 sansha_penalty(-20) 既有通道承担。
2. 月份不宜 E：月家五黄/二黑到坐山维持否决；正阴府无制化(-30)/三煞占月(-30)/
   月破犯坐山(-25) 降级强扣分。正阴府/月破犯坐山经 month_penalty 传导日课
   五行评分（与 §62 分金扣分同构）；降级项隔离月分末尾 suitable 兜底阈值。

样本日期依据（月支=农历月对齐节气）：
- 2024-06-08 甲辰年(午)三煞方巳午未，坤山兼未坐山未∈ → 年三煞犯山向
- 2026-08-15 丙午年申月煞南巳午未，未∈；申∉亥子丑无三煞占月 → 纯月三煞
- 2026-12-15 丙午年子月：子∈亥子丑三煞占月 + 子月煞南巳午未未∈ → 叠加
- 2027-01-15 立春前乙巳年(巳)三煞方寅卯辰：丑∉无三煞占月；丑月煞东寅卯辰
  未∉无月三煞；丑冲未月破犯坐山 → 纯月破样本
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


OWNER1 = [{'name': '', '性别': '男', 'birth_date': '1972-01-08',
           'birth_hour': 8, 'birth_minute': 0}]
KUN = '坤山艮向兼未'


def run(d, ev, owners=None, shan=None):
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d; sz['year'] = d.year; sz['month'] = d.month; sz['day'] = d.day
    return Scorer().score(sz, ev, owners=owners, shan_xiang=shan)


def vetos(r):
    return [str(v) for v in (r.get('veto_reasons') or [])]


def bd_of(r):
    return (r.get('wu_xing_result') or {}).get('score_breakdown') or {}


# ── A. 三煞 D ──
# A1 年三煞犯山向维持否决：2024 甲辰年三煞方巳午未，坤山艮向兼未坐山未∈巳午未
r = run(dt.date(2024, 6, 8), '修造', [dict(o) for o in OWNER1], shan=KUN)
_v = vetos(r)
check('A1 年三煞犯山向维持否决',
      any(('年三煞' in v) for v in _v), '; '.join(_v))

# A2 月三煞犯山向降级：2026-08-15 申月（月三煞方巳午未，未∈；申∉亥子丑无三煞占月）
r = run(dt.date(2026, 8, 15), '修造', None, shan=KUN)
_v = vetos(r)
_jl = [str(j) for j in (r.get('ji_list') or [])]
check('A2a 月三煞犯山向不再一票否决',
      not any('三煞大忌' in v for v in _v), '; '.join(_v))
check('A2b 忌项保留月三煞(山向)标记', '月三煞(山向)' in _jl, str(_jl))

# A3+A4 三煞占月降级且不传导：2026-12-15 子月（三煞占月+坐山犯月三煞叠加）
r = run(dt.date(2026, 12, 15), '修造', None, shan=KUN)
_v = vetos(r)
_bd = bd_of(r)
check('A3 三煞占月+月三煞叠加不再月份不宜否决（隔离兜底生效）',
      not any('月份不宜' in v for v in _v), '; '.join(_v))
check('A4 三煞占月不传导日课（breakdown 无月份不宜扣分键，防双扣）',
      '月份不宜扣分' not in _bd, str({k: v for k, v in _bd.items() if '月份' in str(k)}))

# ── B. 月份不宜 E ──
# B1 月破犯坐山降级传导：2027-01-15 丑月（丑冲未坐山；乙巳年三煞方寅卯辰
# 丑∉无三煞占月；丑月煞东寅卯辰未∉无月三煞）→ 纯月破样本
r = run(dt.date(2027, 1, 15), '修造', None, shan=KUN)
_v = vetos(r)
_bd = bd_of(r)
check('B1a 月破犯坐山不再否决（强扣分）',
      not any('月份不宜' in v for v in _v), '; '.join(_v))
check('B1b 月破犯坐山扣分传导日课(-25)',
      _bd.get('月份不宜扣分') == -25, f"实际={_bd.get('月份不宜扣分')}")

# B2 正阴府无制化降级（analyze_month 层）：扫描 2025-2026 月代表日找正阴府月
#（排除月家五黄到坐山月——飞星否决维持，非本项验证对象）
_yf_month = None
for _y in (2025, 2026):
    for _m in range(1, 13):
        _d = dt.date(_y, _m, 15)
        try:
            _ma = Scorer().analyze_month(_d, '修造', None, KUN, None,
                                         day_sizhu=None, zeli_mode='feixing')
        except Exception:
            continue
        _rs = [str(x) for x in _ma.get('reasons', [])]
        if any('正阴府' in x for x in _rs) and not any('五黄到坐山' in x for x in _rs):
            _yf_month = (_d, _ma)
            break
    if _yf_month:
        break
check('B2a 前置：找到月干犯正阴府且无五黄样本月', _yf_month is not None)
if _yf_month:
    _d, _ma = _yf_month
    check('B2b 正阴府无制化不再整月否决（suitable=True）',
          _ma.get('suitable') is True,
          f"{_d} suitable={_ma.get('suitable')} reasons={_ma.get('reasons')}")
    check('B2c 正阴府扣分-30 入 month_penalty',
          _ma.get('month_penalty') == -30, f"实际={_ma.get('month_penalty')}")

# B3 防双扣：B1 日 breakdown 数值键加总 == 五行分（§62 B4 同款）
r = run(dt.date(2027, 1, 15), '修造', None, shan=KUN)
_bd = bd_of(r)
_wx = (r.get('wu_xing_result') or {}).get('score')
_s = sum(v for k, v in _bd.items()
         if isinstance(v, (int, float)) and k not in ('忌事明细', '相主得分'))
check('B3 breakdown加总==五行分（含月份不宜扣分无重复计）', _s == _wx,
      f'加总={_s} 五行分={_wx}')

# B4 月家五黄到坐山维持否决：扫描月代表日找五黄到坤山月
_w5 = None
for _y in (2024, 2025, 2026, 2027):
    for _m in range(1, 13):
        _d = dt.date(_y, _m, 15)
        try:
            _ma = Scorer().analyze_month(_d, '修造', None, KUN, None,
                                         day_sizhu=None, zeli_mode='feixing')
        except Exception:
            continue
        if any('五黄到坐山' in str(x) for x in _ma.get('reasons', [])):
            _w5 = (_d, _ma)
            break
    if _w5:
        break
check('B4a 前置：找到月家五黄到坐山样本月', _w5 is not None)
if _w5:
    _d, _ma = _w5
    check('B4b 月家五黄到坐山维持整月否决（suitable=False）',
          _ma.get('suitable') is False,
          f"suitable={_ma.get('suitable')} reasons={_ma.get('reasons')}")

# B5 边界：三煞占月+坐山犯月三煞月分隔离后仍为可用低分（2026-12-15）
try:
    _ma = Scorer().analyze_month(dt.date(2026, 12, 15), '修造', None, KUN,
                                 None, day_sizhu=None, zeli_mode='feixing')
    check('B5 月分隔离：三煞占月-30+坐山犯月三煞-20 后 suitable 仍 True',
          _ma.get('suitable') is True,
          f"suitable={_ma.get('suitable')} score={_ma.get('score')} "
          f"reasons={_ma.get('reasons')}")
except Exception as _e:
    check('B5 月分隔离', False, f'异常 {_e}')

# ── C. 普通日无新键/旧行为 ──
r = run(dt.date(2024, 6, 8), '修造', [dict(o) for o in OWNER1])
_bd = bd_of(r)
check('C1 无山向不触发月份不宜扣分键', '月份不宜扣分' not in _bd)

# C2 嫁娶不受影响（婚嫁路径无 month_penalty）
r = run(dt.date(2026, 5, 20), '嫁娶', [dict(o) for o in OWNER1])
_bd = bd_of(r)
check('C2 嫁娶日 breakdown 无月份不宜扣分键', '月份不宜扣分' not in _bd,
      str(_bd.get('月份不宜扣分')))

print()
if FAILS:
    print(f'FAILED {len(FAILS)}: ' + '; '.join(FAILS))
    sys.exit(1)
print('ALL PASS')
sys.exit(0)
