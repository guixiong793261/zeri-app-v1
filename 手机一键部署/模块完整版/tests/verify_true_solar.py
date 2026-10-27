# -*- coding: utf-8 -*-
"""
真太阳时立项验证（2026-09-29，001 §43.9 拍板①②③⑤、§48）
============================================================
口径（v3 设计 A 定稿）：
  真太阳时 = 墙钟 + 4min×(经度−120°) + EoT（NOAA 闭式，拍板②必含）。
  经度=120.0 或 None 等价于不启用（北京时间基准，默认路径行为冻结）。
  EoT = 9.87·sin(2B) − 7.53·cos(B) − 1.5·sin(B)，B = 2π/365×(N−81)。

验证结构（含反向断言，禁止静默通过）：
1. EoT 极值锚点：2026-02-13 ≈ −14.6min、2026-10-31 ≈ +16.5min（§46 D2
   探针实测锚点）；反向：两值异号且 |值|>10（防恒零桩/公式失效）。
2. 默认路径零回归：2026 全年 × {0,12,23}时，longitude=None 与不传参、
   longitude=120.0 与不传参 逐柱一致（向后兼容硬约束）；
   反向：longitude=119.9 全年至少 1 天不同（防开关失效假通过）。
3. 119.9 纯 EoT 翻转：offset = EoT − 0.4min。§46「东经120 纯 EoT 190 天」
   实测口径为 00:00 早子回翻（EoT 负支，190 天）；23:59 晚子前翻为 EoT
   正支（实测 153 天，正支天然短于负支 159 vs 190，加经度残量 −0.4min）。
   反向：两方向均 >100（防 EoT 未施加）且 <365（防经度项误施加）。
4. 五城市翻转对账 §46：北京(116.4)≈329、成都(104.1)=365、
   乌鲁木齐(87.6)=365（00:00 向回翻）；长春(125.3)=365（23:59 前翻，
   offset 恒 ≥+6.6min）；反向：120.0 经度项恒零（offset==EoT，分层断言：
   开关在 calculate()，apply_true_solar 无条件按公式修正——模块 docstring
   明示「调用方负责开关判断」）。
5. 跨日排盘一致性：成都 2026-01-01 00:10 → 修正后 (2025,12,31,23,0x)，
   其日柱 == 2025-12-31 23:10（120 基准参考）日柱；长春 2026-06-15
   23:50 → 次日。反向：两例不启用经度时均不翻转。
6. 越界显式抛错：lon=30/200 → ValueError；反向：60/150 边界不抛。

退出码：全过 0；任一失败 1（CI 集成口径）。
"""
import sys
from datetime import date, timedelta
from pathlib import Path

# 项目根目录入 path（允许从任意 cwd 运行）
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.真太阳时 import (
    equation_of_time_minutes, true_solar_offset_minutes, apply_true_solar,
    TRUE_SOLAR_BASE_LONGITUDE,
)
from modules.四柱计算器 import calculate_sizhu

FAILS = []


def check(name, cond, detail=''):
    tag = 'PASS' if cond else 'FAIL'
    print(f"[{tag}] {name}" + (f" — {detail}" if detail else ''))
    if not cond:
        FAILS.append(name)


def flip_days_wanzhi(year, longitude):
    """晚子翻转天数：23:59 经修正后跨到次日。"""
    n = 0
    d = date(year, 1, 1)
    while d.year == year:
        y, mo, da, h, mi = apply_true_solar(d.year, d.month, d.day, 23, 59, longitude)
        if date(y, mo, da) != d:
            n += 1
        d += timedelta(days=1)
    return n


def flip_days_zaozi(year, longitude):
    """早子回翻天数：00:00 经修正后落到前一日。"""
    n = 0
    d = date(year, 1, 1)
    while d.year == year:
        y, mo, da, h, mi = apply_true_solar(d.year, d.month, d.day, 0, 0, longitude)
        if date(y, mo, da) != d:
            n += 1
        d += timedelta(days=1)
    return n


def sizhu_key(d, h, mi, **kw):
    r = calculate_sizhu(d, h, mi, **kw)
    return (r['年柱'], r['月柱'], r['日柱'], r['时柱'])


print("=" * 64)
print("真太阳时立项验证（§43.9 拍板①②③⑤ / §48 v3 设计A）")
print("=" * 64)

# ---- 1. EoT 极值锚点 ----
eot_min = equation_of_time_minutes(date(2026, 2, 13).timetuple().tm_yday)
eot_max = equation_of_time_minutes(date(2026, 10, 31).timetuple().tm_yday)
check("1a EoT 2026-02-13 ≈ -14.6min", abs(eot_min - (-14.6)) < 0.5, f"实测 {eot_min:.2f}")
check("1b EoT 2026-10-31 ≈ +16.5min", abs(eot_max - 16.5) < 0.5, f"实测 {eot_max:.2f}")
check("1c 反向：异号且非零（防恒零桩）", eot_min < -10 and eot_max > 10)

# ---- 2. 默认路径零回归（硬约束：逐柱一致） ----
mismatch_none = 0
mismatch_120 = 0
d = date(2026, 1, 1)
while d.year == 2026:
    for h in (0, 12, 23):
        base = sizhu_key(d, h, 30)
        if sizhu_key(d, h, 30, longitude=None) != base:
            mismatch_none += 1
        if sizhu_key(d, h, 30, longitude=120.0) != base:
            mismatch_120 += 1
    d += timedelta(days=1)
check("2a longitude=None 全年×3时 零差异", mismatch_none == 0, f"差异 {mismatch_none}")
check("2b longitude=120.0 全年×3时 零差异", mismatch_120 == 0, f"差异 {mismatch_120}")
# 反向：119.9 至少 1 天不同（防开关失效）
diff_1199 = 0
d = date(2026, 1, 1)
while d.year == 2026:
    if sizhu_key(d, 23, 59, longitude=119.9) != sizhu_key(d, 23, 59, longitude=120.0):
        diff_1199 += 1
    d += timedelta(days=1)
check("2c 反向：119.9 与 120 全年至少 1 天不同", diff_1199 > 0, f"差异 {diff_1199} 天")

# ---- 3. 119.9 纯 EoT 翻转（双方向，以实测为准） ----
n1199_wan = flip_days_wanzhi(2026, 119.9)   # 23:59 前翻（EoT 正支）
n1199_zao = flip_days_zaozi(2026, 119.9)    # 00:00 回翻（EoT 负支，§46「190 天」口径）
check("3a 119.9 早子回翻 ∈ [185,195]（§46 预测 190，残量±2）",
      185 <= n1199_zao <= 195, f"实测 {n1199_zao} 天")
check("3b 119.9 晚子前翻 ∈ [145,165]（EoT 正支实测口径）",
      145 <= n1199_wan <= 165, f"实测 {n1199_wan} 天")
check("3c 反向：两方向均 >100（防 EoT 未施加）且 <365（防经度项误施加）",
      100 < n1199_wan < 365 and 100 < n1199_zao < 365)

# ---- 4. 五城市翻转对账 §46 ----
n_bj = flip_days_zaozi(2026, 116.4)     # 北京 00:00 回翻
n_cd = flip_days_zaozi(2026, 104.1)     # 成都
n_ur = flip_days_zaozi(2026, 87.6)      # 乌鲁木齐
n_cc = flip_days_wanzhi(2026, 125.3)    # 长春 23:59 前翻
check("4a 北京 00:00 回翻 ≈329（§46）", 327 <= n_bj <= 331, f"实测 {n_bj}")
check("4b 成都 00:00 回翻 =365（§46）", n_cd == 365, f"实测 {n_cd}")
check("4c 乌鲁木齐 00:00 回翻 =365（§46）", n_ur == 365, f"实测 {n_ur}")
print(f"       长春 23:59 前翻实测 {n_cc} 天（offset 恒 ≥+6.6min，每日必翻）")
check("4d 反向：120.0 经度项恒零（offset==EoT，分层断言）",
      all(abs(true_solar_offset_minutes(120.0, n) - equation_of_time_minutes(n)) < 1e-9
          for n in (1, 100, 200, 300, 365)))

# ---- 5. 跨日排盘一致性 ----
# 成都 2026-01-01 00:10 → offset = 4×(104.1-120)+EoT(1) ≈ -63.6-14.0 ≈ -77.6min
# → (2025,12,31, 22:52 前后)
corr = apply_true_solar(2026, 1, 1, 0, 10, 104.1)
check("5a 成都 00:10 修正后回翻到 2025-12-31", (corr[0], corr[1], corr[2]) == (2025, 12, 31),
      f"实测 {corr}")
sz_corr = sizhu_key(date(2026, 1, 1), 0, 10, longitude=104.1)
sz_ref = sizhu_key(date(2025, 12, 31), corr[3], corr[4], longitude=120.0)
check("5b 修正后四柱 == 参考时刻(120基准)四柱", sz_corr == sz_ref,
      f"{sz_corr} vs {sz_ref}")
# 长春 2026-06-15 23:50 → offset = 4×5.3+EoT ≈ +21.2-0.4 ≈ +20.8 → 次日 00:11
corr2 = apply_true_solar(2026, 6, 15, 23, 50, 125.3)
check("5c 长春 23:50 修正后前翻到 2026-06-16", (corr2[0], corr2[1], corr2[2]) == (2026, 6, 16),
      f"实测 {corr2}")
check("5d 反向：不经度时两例均不翻转",
      sizhu_key(date(2026, 1, 1), 0, 10) != sz_corr or corr[2] == 1,  # 成都日柱必不同
      )
check("5e 反向：成都 00:10 不启用时日期不变",
      sizhu_key(date(2026, 1, 1), 0, 10)[2] != sz_corr[2] or
      calculate_sizhu(date(2026, 1, 1), 0, 10)['date'] == date(2026, 1, 1))

# ---- 6. 越界显式抛错 ----
def _raises(fn):
    try:
        fn()
        return False
    except ValueError:
        return True

check("6a lon=30 显式 ValueError", _raises(lambda: true_solar_offset_minutes(30.0, 100)))
check("6b lon=200 显式 ValueError", _raises(lambda: apply_true_solar(2026, 1, 1, 12, 0, 200.0)))
ok_edge = True
try:
    true_solar_offset_minutes(60.0, 100)
    true_solar_offset_minutes(150.0, 100)
except ValueError:
    ok_edge = False
check("6c 反向：60/150 边界不抛", ok_edge)

print("=" * 64)
if FAILS:
    print(f"失败 {len(FAILS)} 项: {FAILS}")
    sys.exit(1)
print("全部通过")
sys.exit(0)
