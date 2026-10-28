# -*- coding: utf-8 -*-
"""§192 验证：红嘴朱雀入宅否决权 + 事主年命×向首六冲否决。

判据：docs/判据冻结提案_入宅两项按典取证_20261028.md（A-V1／B-Y1 已拍板）
典据：陈书 p96「切不可犯紅嘴朱雀入中宮，犯者不吉、屢見甚驗」（红嘴，中宫日）
      p96「移徙…與宅主本命無尅犯者吉」／p635「坐向…利宅主年庚不相沖尅」／
      p166「本命尅山向主冷退」（年命×向首）
口径：仅入宅/移徙（移徙 canonical→入宅）；嫁娶/安床/作灶不升格；
      未填山向/无向字/无年支 → 不触发（容错不误伤）。
"""
import sys
import os
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.评分器 import Scorer, calculate_score, _canonical_event
from modules.四柱计算器 import calculate_sizhu

FAIL = []
ZHONG_GONG = ['丙寅', '乙亥', '甲申', '癸巳', '壬寅', '辛亥', '庚申']
HZ_TXT = '红嘴朱雀'
XS_TXT = '年命冲大门朝向'


def ck(name, cond, detail=''):
    if cond:
        print('  PASS  ' + name)
    else:
        print('  FAIL  ' + name + '  -> ' + str(detail))
        FAIL.append(name)


def owners_of(zhi):
    return [{'name': '主', 'role': '事主',
             'sizhu': '甲%s 丙寅 戊辰 庚午' % zhi}]


def has(reasons, txt):
    return any(txt in str(v) for v in (reasons or []))


def zhong_gong_days(y0, y1):
    out, d = [], dt.date(y0, 1, 1)
    while d <= dt.date(y1, 12, 31):
        sz = calculate_sizhu(d, 10, 0)
        if sz['day_gan'] + sz['day_zhi'] in ZHONG_GONG:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


print('[0] 通道归并口径')
ck('0.1 移徙 canonical→入宅', _canonical_event('移徙') == '入宅',
   _canonical_event('移徙'))
ck('0.2 嫁娶/安床/作灶 不并入入宅',
   all(_canonical_event(e) == e for e in ('嫁娶', '安床', '作灶')))

print('[A] 红嘴朱雀入宅否决（陈书 p96「切不可犯」）')
zg = zhong_gong_days(2026, 2026)
ck('A1 2026 中宫日 43 天', len(zg) == 43, len(zg))
for ev in ('入宅', '移徙'):
    bad = []
    for d in zg:
        r = calculate_score(calculate_sizhu(d, 10, 0), ev, owners=[], shan_xiang='')
        if not (has(r.get('veto_reasons'), HZ_TXT) and r.get('score') == 0
                and str(r.get('level', '')).startswith('❌')):
            bad.append((d, r.get('score'), r.get('level')))
    ck('A2 %s：43/43 中宫日皆红嘴否决且总分 0' % ev, not bad, bad[:3])

# 非中宫日不得因红嘴被否决（抽查全年 1/7 日）
bad = []
for d in [dt.date(2026, 1, 1) + dt.timedelta(days=i) for i in range(0, 365, 7)]:
    sz = calculate_sizhu(d, 10, 0)
    if sz['day_gan'] + sz['day_zhi'] in ZHONG_GONG:
        continue
    r = calculate_score(sz, '入宅', owners=[], shan_xiang='')
    if has(r.get('veto_reasons'), HZ_TXT):
        bad.append(d)
ck('A3 非中宫日不触发红嘴否决', not bad, bad[:3])

# 嫁娶/安床/作灶 不升格（同日不得出现红嘴否决语）
bad = []
for ev in ('嫁娶', '安床', '作灶'):
    for d in zg[:6]:
        r = calculate_score(calculate_sizhu(d, 10, 0), ev, owners=[], shan_xiang='')
        if has(r.get('veto_reasons'), HZ_TXT):
            bad.append((ev, d))
ck('A4 嫁娶/安床/作灶 不升红嘴否决（三宫仅「忌」）', not bad, bad[:3])

print('[B] 年命×向首六冲否决（陈书 p96／p635／p166）')
S = Scorer()
ck('B1 子命×午向（子山午向）→ 命中',
   len(S._check_owner_xiangshou_chong('子山午向', owners_of('子'))) == 1)
ck('B2 丑命×午向 → 不冲', S._check_owner_xiangshou_chong('子山午向', owners_of('丑')) == [])
ck('B3 未填山向 → 空（容错）', S._check_owner_xiangshou_chong('', owners_of('子')) == [])
ck('B4 山向无「向」字 → 空', S._check_owner_xiangshou_chong('子山', owners_of('子')) == [])
ck('B5 四维宫坤山艮向×未命 → 丑未冲命中',
   len(S._check_owner_xiangshou_chong('坤山艮向', owners_of('未'))) == 1)
ck('B6 坤山艮向兼寅×未命 → 兼向收窄寅，不命中',
   S._check_owner_xiangshou_chong('坤山艮向兼寅', owners_of('未')) == [])
ck('B7 无年支信息 → 空（不误伤）',
   S._check_owner_xiangshou_chong('子山午向', [{'name': '主', 'role': '事主'}]) == [])

# 端到端：酉山卯向 × 酉命 → 全年 365 天否决；酉山卯向 × 子命 → 全年不触发
n_bad = 0
for i in range(0, 365, 5):
    d = dt.date(2026, 1, 1) + dt.timedelta(days=i)
    sz = calculate_sizhu(d, 10, 0)
    r = calculate_score(sz, '入宅', owners=owners_of('酉'), shan_xiang='酉山卯向')
    if not (has(r.get('veto_reasons'), XS_TXT) and r.get('score') == 0):
        n_bad += 1
    r2 = calculate_score(sz, '入宅', owners=owners_of('子'), shan_xiang='酉山卯向')
    if has(r2.get('veto_reasons'), XS_TXT):
        n_bad += 1
ck('B8 酉山卯向：酉命全否决 / 子命全不触发（抽样 73 天）', n_bad == 0, n_bad)

# 修造/安葬 不受本项影响（域外不落地）
bad = []
for ev in ('修造', '安葬'):
    for d in [dt.date(2026, 1, 1) + dt.timedelta(days=i) for i in range(0, 365, 30)]:
        r = calculate_score(calculate_sizhu(d, 10, 0), ev,
                            owners=owners_of('酉'), shan_xiang='酉山卯向')
        if has(r.get('veto_reasons'), XS_TXT):
            bad.append((ev, d))
ck('B9 修造/安葬 不触发本项否决（域外）', not bad, bad[:3])

print('[C] 回归：受死日否决未被挤掉')
SS = [d for d in [dt.date(2026, 1, 1) + dt.timedelta(days=i) for i in range(365)]
      if has(calculate_score(calculate_sizhu(d, 10, 0), '入宅', owners=[],
                             shan_xiang='').get('veto_reasons'), '受死日')]
ck('C1 2026 受死日仍触发入宅否决（天次>0）', len(SS) > 0, len(SS))

print()
if FAIL:
    print('FAILED %d 项：%s' % (len(FAIL), FAIL))
    sys.exit(1)
print('ALL PASS（§192 红嘴朱雀入宅否决 + 年命×向首六冲否决）')
sys.exit(0)
