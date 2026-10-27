# -*- coding: utf-8 -*-
"""
verify: A1 出行规则——死代码清理 + 建除函数就位（不接入产出）
退出码：全过 0 / 有失败 1；结尾打印 FAIL N。
"""
import sys, os, inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.rules.出行规则 import TravelRuleChecker

FAILS = []
def check(name, cond):
    print(("[OK] " if cond else "[FAIL] ") + name)
    if not cond:
        FAILS.append(name)

checker = TravelRuleChecker()

# ---------- 1. 死代码清理（源码级反向断言） ----------
src = inspect.getsource(TravelRuleChecker)
check("源码不再引用 黄历宜忌", "黄历宜忌" not in src)
check("源码不再含 has_marriage_shensha", "has_marriage_shensha" not in src)
check("源码不再含 _check_dependencies", "_check_dependencies" not in src)

# ---------- 2. 建除掌诀黄金值（独立硬编码：以月建起建，顺推十二神） ----------
# 顺序：建 除 满 平 定 执 破 危 成 收 开 闭
JC = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
ZHI = list("子丑寅卯辰巳午未申酉戌亥")
GOLD = {
    '子': dict(zip(ZHI, JC)),                       # 子月：子日建…亥日闭
    '卯': dict(zip(ZHI[-9:] + ZHI[:3], JC)),       # 卯月：卯建、辰除…寅闭
    '午': dict(zip(ZHI[-6:] + ZHI[:6], JC)),       # 午月：午建…巳闭
    '酉': dict(zip(ZHI[-3:] + ZHI[:9], JC)),       # 酉月：酉建…申闭
}
def sz_for(mz, dz):
    return {'month_zhi': mz, 'day_zhi': dz, 'month_gan': '甲', 'day_gan': '甲'}

n_gold = 0
bad_gold = 0
for mz, table in GOLD.items():
    for dz, expect in table.items():
        got = checker._calc_jianchu_value(sz_for(mz, dz))
        if got != expect:
            check(f"建除 {mz}月{dz}日 期望{expect} 实得{got}", False)
            bad_gold += 1
        n_gold += 1
check(f"建除掌诀黄金值 {n_gold-bad_gold}/{n_gold} 点对（子/卯/午/酉四月×12日）", bad_gold == 0)

# ---------- 3. 反向断言：非法/缺失输入 ----------
check("空 dict → None", checker._calc_jianchu_value({}) is None)
check("None 输入 → None", checker._calc_jianchu_value(None) is None)
check("字符串输入 → None", checker._calc_jianchu_value('甲子') is None)
check("仅月支无日支 → None", checker._calc_jianchu_value({'month_zhi': '子'}) is None)
check("非法地支 → '未知'（calc_jianchu 契约）",
      checker._calc_jianchu_value({'month_zhi': 'X', 'day_zhi': '子'}) == '未知')

# ---------- 4. A1 硬边界：_check_rules 未接入建除函数 ----------
rules_src = inspect.getsource(TravelRuleChecker._check_rules)
check("_check_rules 不调用 _calc_jianchu_value（函数就位但不接入产出）",
      "_calc_jianchu_value" not in rules_src)

# ---------- 5. 模板入口仍可正常返回四元组 ----------
yi, ji, veto, vr = checker.check(sz_for('子', '午'), [])
check("check() 月破日仍产出忌项且触发否决",
      any('月破' in x for x in ji) and veto is True)

print()
print(f"FAIL {len(FAILS)}")
sys.exit(1 if FAILS else 0)
