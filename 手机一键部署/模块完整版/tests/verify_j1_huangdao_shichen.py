# -*- coding: utf-8 -*-
"""
verify: J1 大黄道吉时——筛选改调时辰级接口 _calculate_da_huangdao_shichen
J1 只修名实（按时支走表），表值典据校正属 J2，本脚本不裁决典据。
退出码：全过 0 / 有失败 1；结尾打印 FAIL N。
"""
import sys, os, inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAILS = []
def check(name, cond):
    print(("[OK] " if cond else "[FAIL] ") + name)
    if not cond:
        FAILS.append(name)

from modules.黄道 import 黄道计算器
import 主程序 as main_app

# ---------- 1. 主程序接线（源码级；枚举全部命中方法，至少一个正确接线） ----------
hit_methods = []   # (类, 方法, 源码)
for name, obj in inspect.getmembers(main_app, predicate=inspect.isclass):
    for mname, mfn in inspect.getmembers(obj, predicate=inspect.isfunction):
        s = inspect.getsource(mfn)
        if '大黄道吉时' in s:
            hit_methods.append((name, mname, s))
check("找到含'大黄道吉时'的方法", bool(hit_methods))
wired = [h for h in hit_methods
         if "_calculate_da_huangdao_shichen(" in h[2]
         and "_calculate_da_huang_dao(" not in h[2]
         and "J2" in h[2]]
check(f"存在筛选方法已接线时辰接口并标注J2局限（{[h[1] for h in wired]}）", bool(wired))

# ---------- 2. 旧接口名实不符反向坐实（历史行为证据） ----------
calc = 黄道计算器()
r1 = calc._calculate_da_huang_dao('卯', '辰', '子')
r2 = calc._calculate_da_huang_dao('卯', '辰', '午')
check("旧接口忽略时支：子/午时返回同名（证明其非时辰级）",
      r1['name'] == r2['name'])

# ---------- 3. 时辰接口：144 点与 DA_HUANG_DAO_TABLE 逐字一致 ----------
ZHI = list("子丑寅卯辰巳午未申酉戌亥")
n = bad = 0
for dz in ZHI:
    row = calc.DA_HUANG_DAO_TABLE[dz]
    for hz in ZHI:
        got = calc._calculate_da_huangdao_shichen(dz, hz)
        expect_name = row[ZHI.index(hz)]
        if got['name'] != expect_name:
            check(f"{dz}日{hz}时 期望{expect_name} 实得{got['name']}", False)
            bad += 1
        # type/score 与 DA_HUANG_DAO 字典一致
        info = calc.DA_HUANG_DAO[expect_name]
        if got['type'] != info['type'] or got['score'] != info['score']:
            check(f"{dz}日{hz}时 type/score 与字典不符", False)
            bad += 1
        n += 1
check(f"时辰接口 144 点名/type/score 与活表逐字一致（{n-bad}/{n}）", bad == 0)

# ---------- 4. 时支敏感性：同一日 12 时辰值神不全相同 ----------
for dz in ZHI:
    names = [calc._calculate_da_huangdao_shichen(dz, hz)['name'] for hz in ZHI]
    if len(set(names)) < 6:
        check(f"{dz}日 12 时辰值神几乎不变化（异常）", False)
check("12 日支各自时辰值神随时支变化", True)

# ---------- 5. 示例点（客观表值）：卯日午时 = 金匮（接口 docstring 误写"司命"，
# 真值以 DA_HUANG_DAO_TABLE 为准；docstring 留待专项，J1 守边界不动） ----------
check("卯日午时 → 金匮",
      calc._calculate_da_huangdao_shichen('卯', '午')['name'] == '金匮')
check("卯日子时 → 司命",
      calc._calculate_da_huangdao_shichen('卯', '子')['name'] == '司命')

# ---------- 6. 反向：未知地支走兜底不抛异常 ----------
out = calc._calculate_da_huangdao_shichen('X', '子')
check("非法日支：回退兜底且返回结构完整",
      out['name'] in ['青龙','明堂','天刑','朱雀','金匮','天德',
                      '白虎','玉堂','天牢','玄武','司命','勾陈']
      and out['type'] in ('吉', '凶', '平'))

print()
print(f"FAIL {len(FAILS)}")
sys.exit(1 if FAILS else 0)
