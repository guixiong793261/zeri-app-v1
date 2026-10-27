# -*- coding: utf-8 -*-
"""
verify: J2 时辰大黄道起例对齐《协纪辨方书·卷七》（001 §57）
- 144 点黄金矩阵：口诀程序化生成（《考原》起例）为唯一真值
- 四通道对账：黄道.py 活表 / 婚嫁评分算法.py 镜像 / 通用神煞.py 方法 /
  嫁娶神煞扩展.py 方法
- 独立交叉：今日黄历.py QINGLONG_SHICHEN_MAP（独立实现，起例等价）
退出码：全过 0 / 有失败 1；结尾打印 FAIL N。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAILS = []
def check(name, cond):
    print(("[OK] " if cond else "[FAIL] ") + name)
    if not cond:
        FAILS.append(name)

from modules.黄道 import 黄道计算器
from modules.婚嫁评分算法 import HUANGDAO_SHI_TABLE
from modules.今日黄历 import QINGLONG_SHICHEN_MAP, QINGLONG_NAMES, get_da_huangdao

ZHI = list('子丑寅卯辰巳午未申酉戌亥')
NAMES = ['青龙','明堂','天刑','朱雀','金匮','天德','白虎','玉堂','天牢','玄武','司命','勾陈']
JI = {'青龙','明堂','金匮','天德','玉堂','司命'}

# 《协纪》卷七引《考原》：寅申起子、卯酉起寅、辰戌起辰、
# 巳亥起午、子午起申、丑未起戌
START = {dz: q for pair, q in [
    (('子','午'),8),(('丑','未'),10),(('寅','申'),0),
    (('卯','酉'),2),(('辰','戌'),4),(('巳','亥'),6)] for dz in pair}

def gold(dz, hz):
    return NAMES[(ZHI.index(hz) - START[dz]) % 12]

calc = 黄道计算器()

# ---------- 1. 起例六组口诀锁（青龙位 + 旧错位反向） ----------
check("六组青龙时支与《考原》口诀一致",
      all(calc.DA_HUANG_DAO_TABLE[dz][START[dz]] == '青龙' for dz in ZHI))
OLD_WRONG = {'子':0,'午':0,'丑':2,'未':2,'寅':10,'申':10,'巳':5,'亥':5}
check("四个错组旧错表青龙位不再为青龙（反向）",
      all(calc.DA_HUANG_DAO_TABLE[dz][i] != '青龙' for dz, i in OLD_WRONG.items()))

# ---------- 2. 144 点黄金矩阵 × 黄道.py 接口 ----------
bad = 0
for dz in ZHI:
    for hz in ZHI:
        g = gold(dz, hz)
        r = calc._calculate_da_huangdao_shichen(dz, hz)
        if r['name'] != g: bad += 1
check("黄道.py 接口 144 点 == 黄金矩阵（%d 错）" % bad, bad == 0)

# ---------- 3. 四通道对账 ----------
# 通道2：婚嫁评分算法镜像
check("婚嫁评分算法 HUANGDAO_SHI_TABLE == 黄道活表",
      calc.DA_HUANG_DAO_TABLE == HUANGDAO_SHI_TABLE)

# 通道3：通用神煞 _get_huangdao_shi（吉时返回星名、凶时返回 None）
from modules.shensha.通用神煞 import CommonShenShaChecker
gen = CommonShenShaChecker.__new__(CommonShenShaChecker)
b3 = []
for dz in ZHI:
    for hz in ZHI:
        g = gold(dz, hz)
        got = gen._get_huangdao_shi(dz, hz)
        exp = g if g in JI else None
        if got != exp:
            b3.append("%s%s:%r!=%r" % (dz, hz, got, exp))
check("通用神煞 _get_huangdao_shi 144 点对账（%d 错）" % len(b3), not b3)

# 通道4：嫁娶神煞扩展 _get_da_huangdao（参数顺序：时支, 日支）
from modules.shensha.嫁娶神煞扩展 import MarriageShenShaCheckerExt
mar = MarriageShenShaCheckerExt.__new__(MarriageShenShaCheckerExt)
b4 = []
for dz in ZHI:
    for hz in ZHI:
        got = mar._get_da_huangdao(hz, dz)
        if got != gold(dz, hz):
            b4.append("%s%s:%r" % (dz, hz, got))
check("嫁娶神煞扩展 _get_da_huangdao 144 点对账（%d 错）" % len(b4), not b4)

# ---------- 4. 独立交叉：今日黄历 QINGLONG_SHICHEN_MAP ----------
b5 = []
for dz in ZHI:
    for hz in ZHI:
        nm, _jx = get_da_huangdao(dz, hz)
        if nm != gold(dz, hz):
            b5.append("%s%s:%r" % (dz, hz, nm))
check("今日黄历 get_da_huangdao 144 点交叉对账（%d 错）" % len(b5), not b5)

# ---------- 5. 每日恰 6 吉时 ----------
check("每个日支吉时恰 6 个",
      all(sum(1 for hz in ZHI if gold(dz, hz) in JI) == 6 for dz in ZHI))

print()
print("FAIL %d" % len(FAILS))
sys.exit(1 if FAILS else 0)
