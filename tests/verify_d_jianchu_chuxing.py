# -*- coding: utf-8 -*-
"""
verify: D 专项——建除十二神×出行 shensha 评分落地（001 §184）
==============================================================
卷十「宜建开；忌破平收闭」。档位为「修造同款」：宜建/开 +5、忌破 -15、忌平/收/闭 -5。

复用底座（逆向断言）：发射代码必须委托 modules/建除.py 的 star_by_sizhu 取星名、
get_event_yiji('出行') 取宜忌，不得在此重造轮子（内嵌星表/宜忌表）。

覆盖：
1. 黄金矩阵：子/卯/午/酉 四个月×12 日支，6 发射星（建开宜、破平收闭忌）分值正确，
   其余 6 星（除/满/定/执/危/成）不发射。
2. 分值经 _add_shensha → 事项标准 SHENSHA_SCORES 解析（非调用处爆锤值）。
3. SHENSHA_SCORES 恰含 6 个 (出行,建除十二神-×) 键且分值与档位一致。
4. 反向：出行神煞.py 源码含 star_by_sizhu / get_event_yiji 委托，无内嵌建除星表。

退出码：全过 0 / 有失败 1；结尾打印 FAIL N。
"""
import sys, os, inspect
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.shensha.出行神煞 import TravelShenShaChecker
from modules.建除 import star_by_sizhu, get_event_yiji

FAILS = []
def check(name, cond):
    print(("[OK] " if cond else "[FAIL] ") + name)
    if not cond:
        FAILS.append(name)

# ---------- 卷十宜忌（伪独立：直接引用建除.py 事实源，避免双测同一份错表） ----------
# 档位：宜建/开 +5、忌破 -15、忌平/收/闭 -5；其余 6 星不发射。
SCORE = {
    '建': 5, '开': 5,
    '破': -15,
    '平': -5, '收': -5, '闭': -5,
}
EMIT = set(SCORE)
NOEMIT = {'除', '满', '定', '执', '危', '成'}

# ---------- 黄金矩阵（独立硬编码：以月建起建，顺推十二神） ----------
JC = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
ZHI = list("子丑寅卯辰巳午未申酉戌亥")
GOLD = {
    '子': dict(zip(ZHI, JC)),                       # 子月：子日建…亥日闭
    '卯': dict(zip(ZHI[-9:] + ZHI[:3], JC)),       # 卯月：卯建、辰除…寅闭
    '午': dict(zip(ZHI[-6:] + ZHI[:6], JC)),       # 午月：午建…巳闭
    '酉': dict(zip(ZHI[-3:] + ZHI[:9], JC)),       # 酉月：酉建…申闭
}

def _emit_shensha_list(sizhu):
    chk = TravelShenShaChecker()
    chk._std_event = '出行'
    chk._check_day_shensha(sizhu)
    return [s for s in chk.shensha_list if s['name'].startswith('建除十二神-')]

def _check_gold_gate(mz):
    """对某月全部 12 日支运行发射矩阵；返回该月 (fail 数, 总点次)。"""
    fails = n = 0
    for dz, expect in GOLD[mz].items():
        sizhu = {'month_zhi': mz, 'day_zhi': dz, 'month_gan': '甲', 'day_gan': '甲'}
        got = _emit_shensha_list(sizhu)
        n += 1
        name = f'建除十二神-{expect}'
        matches = [s for s in got if s['name'] == name]
        if expect in EMIT:
            # 应收发 1 条，分值与档位一致
            if len(matches) != 1 or len(got) != 1:
                check(f"建除 {mz}月{dz}日 {expect}：(期望1条 {name} {SCORE[expect]}，实得 {got})", False)
                fails += 1
            elif matches[0]['score'] != SCORE[expect]:
                check(f"建除 {mz}月{dz}日 {expect} 分值应={SCORE[expect]} 实得={matches[0]['score']}", False)
                fails += 1
        else:
            # 应收发 0 条
            if got:
                check(f"建除 {mz}月{dz}日 {expect}：(卷十出行无宜忌，应不发射，实得 {got})", False)
                fails += 1
    return fails, n

tot_fail = tot_pts = 0
for mz in GOLD:
    f, n = _check_gold_gate(mz)
    # 先登记矩阵点（不逐点打印，基类建除 golden 已覆子/卯/午/酉四月）
    tot_fail += f
    tot_pts += n
check(f"建除×出行黄金矩阵 {tot_pts - tot_fail}/{tot_pts} 点对（子/卯/午/酉四月×12 日）", tot_fail == 0)

# ---------- 2. 分值经 SHENSHA_SCORES 解析（非调用处爆锤） ----------
from modules.事项标准 import SHENSHA_SCORES, shensha_score
for star, expect in SCORE.items():
    got = shensha_score('出行', f'建除十二神-{star}')
    check(f"SHENSHA_SCORES (出行,建除十二神-{star}) = {got}（应 {expect}）", got == expect)

# 恰 6 键
keys = [k for k in SHENSHA_SCORES if k[0] == '出行' and k[1].startswith('建除十二神-')]
check(f"SHENSHA_SCORES 出行建除键恰 6 个（实得 {len(keys)}）", len(keys) == 6)

# ---------- 3. 复用底座（逆向源码断言） ----------
src = inspect.getsource(TravelShenShaChecker)
check("发射复用 star_by_sizhu（未重造轮子）", "_jc_star_by_sizhu" in src)
check("发射复用 get_event_yiji('出行')", "_jc_get_event_yiji('出行')" in src)
# 反向：源码不得内嵌「星名→得分」的建除表（仅允许 建除.py 的 SCORE 逻辑）
no_inline = True
# 剥注释后检查是否出现内嵌 建开/破平收闭 字面量表（用分数 15/5 冷启动即表）
code = '\n'.join(ln.split('#', 1)[0] for ln in src.splitlines())
for forbid in ("'建': 5", "'破': -15", "'平': -5", "'开': 5", "'闭': -5", "'收': -5"):
    if forbid in code:
        check(f"源码不得内嵌建除档位字面量 {forbid}", False)
        no_inline = False
if no_inline:
    check("源码无内嵌建除档位字面量表（档位在 SHENSHA_SCORES，发射只委托建除.py）", True)

print()
print(f"FAIL {len(FAILS)}")
sys.exit(1 if FAILS else 0)