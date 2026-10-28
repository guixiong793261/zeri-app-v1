# -*- coding: utf-8 -*-
"""§193 支轨验证：安床红嘴朱雀「乾方」方位门控（陈书 p788）。

判据来源：
  - 陈书 p788「經嘴朱雀丁卯丙子乙酉甲午癸卯壬子辛酉日并不可安床在乾方」
    → 本煞在安床受**方位**限定（p890 起例为日类忌，本批以 p788 收窄）
  - 2026-10-28 拍板：B 案；床位朝乾（西北）维持 -30；朝其他方位 0 分并提示
    方外不忌；**未填朝向维持 -30（未填不放宽）**

A. 源码门控：安床神煞读 chuangwei、三支路文案齐备
B. 触发集合：乾宮 7 日/60 日循环，2026 全年 43 天
C. 分值：西北/乾 = -30；东/南/北/西/东南/东北/西南 = 0 且出「方外不忌」提示
D. 未填 / None / 空串 = -30（不放宽）
E. 反向：非乾宮日任何朝向均无红嘴条目；乾宮日+非乾方不得再计 -30
F. 范围：安床以外事项不透传朝向，红嘴分值与 §192 后口径一致（嫁娶/作灶 -30）
G. 展示：说明含 p788 与「方外不忌」「未填」字样
"""
import sys, os, inspect, datetime as dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
from modules.shensha.安床神煞 import BedShenShaChecker

FAIL = []


def ck(name, cond, detail=''):
    if cond:
        print('  PASS %s' % name)
    else:
        print('  FAIL %s %s' % (name, detail))
        FAIL.append(name)


def red(r):
    return [(s.get('name'), s.get('score')) for s in (r.get('shensha_list') or [])
            if isinstance(s, dict) and '红嘴' in str(s.get('name'))]


def red_of(r):
    """返回 (名称, 分值, 说明) 的红嘴条目。"""
    out = []
    for s in (r.get('shensha_list') or []):
        if isinstance(s, dict) and '红嘴' in str(s.get('name')):
            out.append((s.get('name'), s.get('score'),
                        str(s.get('description') or s.get('desc') or '')))
    return out


DAYS = [(dt.date(2026, 1, 1) + dt.timedelta(days=i)) for i in range(365)]
SZ = {d: calculate_sizhu(d, 10, 0) for d in DAYS}

# ============ A：源码门控 ============
print('[A] 源码：安床红嘴按 chuangwei 门控')
src = inspect.getsource(BedShenShaChecker)
ck('A1 读取 chuangwei 参数', "kwargs.get('chuangwei')" in src)
ck('A2 非乾方分支存在', "'红嘴朱雀（方外不忌）'" in src)
ck('A3 未填按最严口径分支存在', '床位朝向未填，按最严口径计' in src)
ck('A4 三条 L4 文案均引 p788', src.count('p788') >= 3, 'p788 出现 %d 次' % src.count('p788'))

# ============ B：触发集合 ============
print('[B] 乾宮触发集合（2026）')
hit_gan = []
for d in DAYS:
    r = calculate_score(SZ[d], '安床', owners=[], shan_xiang='', chuangwei='西北')
    if red_of(r) and red_of(r)[0][1] == -30:
        hit_gan.append(d)
ck('B1 乾宮 -30 天数 = 43', len(hit_gan) == 43, '实得 %d' % len(hit_gan))

# ============ C：方位分派 ============
print('[C] 方位分派（西北/乾 vs 其余六方）')
sample = hit_gan[0]
r_nw = calculate_score(SZ[sample], '安床', owners=[], shan_xiang='', chuangwei='西北')
r_q = calculate_score(SZ[sample], '安床', owners=[], shan_xiang='', chuangwei='乾')
ck('C1 西北 = -30', red(r_nw) == [('红嘴朱雀', -30)], str(red(r_nw)))
ck('C2 乾（别名）= -30', red(r_q) == [('红嘴朱雀', -30)], str(red(r_q)))
for cw in ('东', '南', '西', '北', '东南', '东北', '西南'):
    r = calculate_score(SZ[sample], '安床', owners=[], shan_xiang='', chuangwei=cw)
    ok = red(r) == [('红嘴朱雀（方外不忌）', 0)]
    ck('C3-%s 方外不忌 = 0' % cw, ok, str(red(r)))

# ============ D：未填不放宽 ============
print('[D] 未填朝向（不放宽）')
for tag, cw in (('空串', ''), ('None', None), ('全空格', '   ')):
    r = calculate_score(SZ[sample], '安床', owners=[], shan_xiang='', chuangwei=cw)
    ck('D-%s 未填 = -30' % tag, red(r) == [('红嘴朱雀', -30)], str(red(r)))

# ============ E：反向断言 ============
print('[E] 反向：非乾宮日不因方位触发；乾宮日非乾方不计 -30')
non_gan = [d for d in DAYS if d not in set(hit_gan)]
bad = []
for d in non_gan[::7]:
    for cw in ('西北', '东'):
        r = calculate_score(SZ[d], '安床', owners=[], shan_xiang='', chuangwei=cw)
        if red_of(r):
            bad.append((str(d), cw, red_of(r)))
ck('E1 非乾宮日任何朝向均无红嘴条目', not bad, str(bad[:2]))
ck('E2 乾宮日非乾方无 -30 条目',
   all(s != -30 for _, s, _ in red_of(calculate_score(
       SZ[sample], '安床', owners=[], shan_xiang='', chuangwei='东'))))
# 直接调检查器（不接评分器）验证透传
direct = BedShenShaChecker().check(SZ[sample], [], chuangwei='东')
ck('E3 检查器直调透传 chuangwei=东 → 0 分',
   [(s['name'], s['score']) for s in direct if '红嘴' in s['name']] == [('红嘴朱雀（方外不忌）', 0)])

# ============ F：范围（其他事项不透传） ============
print('[F] 范围：其他事项不受影响')
for ev, gong in (('嫁娶', '坤'), ('作灶', '震')):
    ck_checker_ok = None
    r = calculate_score(SZ[sample], ev, owners=[], shan_xiang='')
    vals = [s for _, s, _ in red_of(r)]
    ck('F1 %s 红嘴分值仍按 §192 后口径（-30 或未命中）' % ev,
       all(v == -30 for v in vals), str(red_of(r))[:80])
# 修造/入宅不得因本批出现红嘴提示条目
for ev in ('修造', '入宅'):
    r = calculate_score(SZ[sample], ev, owners=[], shan_xiang='子山午向')
    ck('F2 %s 无「方外不忌」提示' % ev,
       not any('方外不忌' in str(s.get('name')) for s in (r.get('shensha_list') or [])
               if isinstance(s, dict)))

# ============ G：展示文案 ============
print('[G] 展示文案')
_, _, desc_gan = red_of(r_nw)[0]
_, _, desc_fang = red_of(calculate_score(
    SZ[sample], '安床', owners=[], shan_xiang='', chuangwei='东'))[0]
_, _, desc_none = red_of(calculate_score(
    SZ[sample], '安床', owners=[], shan_xiang=''))[0]
ck('G1 乾方文案含 p788', 'p788' in desc_gan, desc_gan[:60])
ck('G2 乾方文案含床位朝向', '床位朝西北' in desc_gan, desc_gan[:60])
ck('G3 方外文案含「方外不忌」与所选朝向', '方外不忌' in desc_fang and '东' in desc_fang,
   desc_fang[:60])
ck('G4 未填文案含「未填」与「最严」', '未填' in desc_none and '最严' in desc_none,
   desc_none[:60])

print()
if FAIL:
    print('FAILED %d 项：%s' % (len(FAIL), FAIL))
    sys.exit(1)
print('ALL PASS（§193 支轨 安床红嘴乾方门控）')
sys.exit(0)
