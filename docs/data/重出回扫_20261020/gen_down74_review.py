# -*- coding: utf-8 -*-
"""生成《复核清单_全年降档74例》及归因 JSON（归档自洽版）。

输入（与本脚本同目录）：yr_old.csv / yr_new.csv（sweep_year.py 产物，5475 行）
输出：down74_attrib.json（同目录）＋ ../../复核清单_全年降档74例_20261020.md
复现：python gen_down74_review.py
"""
import collections
import csv
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))


def load(p):
    return {(r['date'], r['event']): r for r in csv.DictReader(
        open(p, encoding='utf-8-sig'))}


def split(s):
    out = {}
    for x in (s or '').split('|'):
        if not x:
            continue
        for i in range(len(x) - 1, 0, -1):
            if x[i] in '+-':
                try:
                    out[x[:i]] = int(x[i:])
                    break
                except ValueError:
                    continue
    return out


o = load(os.path.join(HERE, 'yr_old.csv'))
n = load(os.path.join(HERE, 'yr_new.csv'))

rows = []
for k in o:
    a, b = o[k], n[k]
    z = a['zeroed'] == '1' or b['zeroed'] == '1'
    d = int(float(b['total'])) - int(float(a['total']))
    if not z and d < 0 and a['level'] != b['level']:
        ow, nw = split(a['watch']), split(b['watch'])
        rows.append({
            'date': k[0], 'event': k[1], 'old': a['total'], 'new': b['total'],
            'delta': d, 'old_level': a['level'], 'new_level': b['level'],
            'added': {x: nw[x] for x in nw if x not in ow},
            'removed': {x: ow[x] for x in ow if x not in nw},
        })
rows.sort(key=lambda r: (r['delta'], r['date']))
assert len(rows) == 74, len(rows)
for r in rows:
    assert sum(r['added'].values()) - sum(r['removed'].values()) == r['delta'], r

json.dump(rows, open(os.path.join(HERE, 'down74_attrib.json'), 'w',
                     encoding='utf-8'), ensure_ascii=False, indent=1)

ev_cnt = collections.Counter(r['event'] for r in rows)
lv_cnt = collections.Counter('%s → %s' % (r['old_level'], r['new_level']) for r in rows)
add_cnt, add_val = collections.Counter(), collections.Counter()
rm_cnt, rm_val = collections.Counter(), collections.Counter()
for r in rows:
    for x, v in r['added'].items():
        add_cnt[x] += 1
        add_val[x] += v
    for x, v in r['removed'].items():
        rm_cnt[x] += 1
        rm_val[x] += -v
net = sum(r['delta'] for r in rows)


def fmt_items(d):
    if not d:
        return '—'
    return '、'.join('%s %+d' % (k, v) for k, v in
                     sorted(d.items(), key=lambda kv: kv[1]))


L = []
A = L.append
A('# 复核清单：2026 全年口径内降档 74 例（2026-10-20 拍板产出）')
A('')
A('**口径**：新旧基线对照（新＝HEAD `787415f`，旧＝`8b9bbb6` 土符修表前），'
  "`calculate_score(sizhu, 事项, owners=[], house_type='阳宅')`，午时；"
  '365 天 × 15 事项 = 5475 格。')
A('**入选条件**：排除「门槛归零」单元格后，总分下降 **且** 等级跨档，共 **74 例**'
  '（占 5475 格的 1.35%）。')
A('**归因方法**：逐例对新旧 `watch` 条目求差——「新增命中」为扣分新因，'
  '「清退」为抬分旧因，两者合计恒等于 Δ（74/74 全等，含 9 例增减对冲）。')
A('')
A('---')
A('')
A('## 一、致因汇总')
A('')
A('| 致因（新增命中，扣分） | 例数 | 分值合计 | 批次归属 |')
A('|---|---|---|---|')
for x, c in add_cnt.most_common():
    batch = {'红嘴朱雀': '红嘴朱雀按陈书九宫重构批（§142）',
             '受死日': '受死日表B→表A 收敛批（§144）',
             '土符': '土符五事项正表裁断批（正表新命中）',
             '土王用事': '土王用事修造扩项批（先行批次）'}[x]
    A('| %s | %d | %+d | %s |' % (x, c, add_val[x], batch))
A('| **合计** | — | **%+d** | — |' % sum(add_val.values()))
A('')
A('| 清退（抬分，对冲） | 例数 | 抬分合计 |')
A('|---|---|---|')
for x, c in rm_cnt.most_common():
    A('| %s | %d | %+d |' % (x, c, rm_val[x]))
A('| **合计** | — | **%+d** |' % sum(rm_val.values()))
A('')
A('74 例净变 **%+d**。按事项分布：%s。'
  % (net, '、'.join('%s %d' % (e, c) for e, c in ev_cnt.most_common())))
A('')
A('等级迁移分布：')
A('')
A('| 迁移 | 例数 |')
A('|---|---|')
for k, c in lv_cnt.most_common():
    A('| %s | %d |' % (k, c))
A('')
A('**「上吉→❌ 凶」仅 2 例**（09-30 动土、10-31 修造），专项深核见 §三；'
  '其余降档均为相邻档位迁移。')
A('')
A('---')
A('')
A('## 二、74 例全表（按 Δ 升序）')
A('')
A('| # | 日期 | 事项 | 旧→新 | Δ | 旧等级 → 新等级 | 新增命中（扣分） | 清退（抬分） |')
A('|---|---|---|---|---|---|---|---|')
for i, r in enumerate(rows, 1):
    A('| %d | %s | %s | %s→%s | %+d | %s → %s | %s | %s |' % (
        i, r['date'], r['event'], r['old'], r['new'], r['delta'],
        r['old_level'], r['new_level'],
        fmt_items(r['added']), fmt_items(r['removed'])))
A('')
A('---')
A('')
A('## 三、专项深核：2 例「上吉 → ❌ 凶」（受死日表A 收敛负面波及是否合理）')
A('')
A('### 3.1 2026-09-30 动土 106→64（-42）')
A('')
A('- **四柱实测**（hour=10）：**酉月 未日**。')
A('- 受死日：表A 八月→**未日** ✅命中；表B 秋→辰日 ❌不命中 → '
  '**表A 收敛新命中**（陈书 p152 逐月表，本日确为受死日）。')
A('- 土符：正表 酉月→**未日** ✅命中 → 同为**正表新命中**'
  '（旧错表本日不命中，属错表清退后的正确回补）。')
A('- 致因：受死日 -22 + 土符 -20 = -42，无对冲项，与 Δ 全等。')
A('')
A('### 3.2 2026-10-31 修造 116→76（-40）')
A('')
A('- **四柱实测**（hour=10）：**戌月 寅日**。')
A('- 受死日：表A 九月→**寅日** ✅命中；表B 秋→辰日 ❌不命中 → '
  '**表A 收敛新命中**。')
A('- 土符：正表 戌月→亥日，本日寅日 ❌不命中（排除土符因素）。')
A('- 土王用事 -18：修造通道扩项（先行批次拍板，非本回扫范围的新增误判）。')
A('- 致因：受死日 -22 + 土王用事 -18 = -40，无对冲项，与 Δ 全等。')
A('')
A('### 3.3 典据本意核对（结论：合理，属纠偏后正确判定）')
A('')
A('1. **受死日在动土/修造两通道为有载保留项**（§138.2 逐通道典据确认表）：'
  '陈书 p152 主条「受死 上官起造嫁娶等凶宜安塟」——「起造」即动土/修造语境，'
  '另有 p580/p122/p578/p585/p622 多处互证；两通道不在删除候选之列。')
A('2. **表A 为唯一正表**（§144.2）：陈书 p152 逐月表 12/12 全等 + 页内 10 处月表互证；'
  '旧表B「春戌夏丑秋辰冬未」系天喜/四击/死别口诀误植，已废弃。'
  '两例日支（未日/寅日）均严格落在表A 对应月份上，扣分是**典据本意的正确命中**，'
  '非收敛误伤。')
A('3. **土符正表命中**（09-30）：酉月未日在正表之内，属错表修正后的正确回补。')
A('4. **风险面可控**：全年 5475 格中「上吉→凶」仅 2 例（0.037%），'
  '且均可逐条归因到有典据的保留项，无"来源不明"降档。')
A('')
A('**复核结论：2 例降档归因属于典据本意，判定合理，予以维持。**')
A('')
A('---')
A('')
A('## 四、数据与复现')
A('')
A('- 逐例归因结构化数据：'
  '[down74_attrib.json](file:///d:/自编择日软件/专业级正五行择日软件/docs/data/重出回扫_20261020/down74_attrib.json)'
  '（含每例新旧 watch 差集，生成时断言 74 例且 致因合计≡Δ）。')
A('- 全年新旧格值：同目录 `yr_old.csv`／`yr_new.csv`（5475 行 × 2）。')
A('- 本清单由同目录 `gen_down74_review.py` 生成；复现命令见 '
  '[manifest.md](file:///d:/自编择日软件/专业级正五行择日软件/docs/data/重出回扫_20261020/manifest.md)。')
A('- 四柱核查（§三）：`calculate_sizhu(date,10,0)`，月支/日支逐日实测，'
  '表A/表B/土符正表逐一对照。')
A('')
A('**时效注记**：本清单基于 HEAD `787415f`。后续 H1-3 批（入宅月破规则层删除）'
  '将使入宅/移徙在月破日再 +15，其中个别行分值会变，但归因结构与本清单结论不变。')

out = '\n'.join(L) + '\n'
dst = os.path.join(HERE, '..', '..', '复核清单_全年降档74例_20261020.md')
open(dst, 'w', encoding='utf-8', newline='\n').write(out)
print('OK rows=%d net=%+d -> %s' % (len(rows), net, os.path.abspath(dst)))
