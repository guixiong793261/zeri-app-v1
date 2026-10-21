# -*- coding: utf-8 -*-
"""轻重层专项·只读盘点：从五层总表解析「轻重列 ⚠️」全量清单，
并合并冻结集 / 制化相抵挂账 / 2026 实测权重。

只读：不修改任何生产文件。输出 weight_inventory.json + 控制台表格。
用法：python parse_weight_inventory.py
退出码：0=正常 1=异常
"""
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)

DOC = os.path.join(ROOT, 'docs', '神煞五层验证体系_总表.md')
DATA = os.path.join(ROOT, 'docs', 'data', '下半场盘点_20261021',
                    'hou3ceng_2026.json')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'weight_inventory.json')


def parse_tables(path):
    """按二级标题分段解析 markdown 表；返回 [{section,name,cells}]。"""
    lines = open(path, encoding='utf-8').read().splitlines()
    section = ''
    rows = []
    header = None
    for ln in lines:
        if ln.startswith('## '):
            section = ln[3:].strip()
            header = None
            continue
        if not ln.startswith('|'):
            header = None
            continue
        cells = [c.strip().strip('*') for c in ln.strip('|').split('|')]
        if all(re.fullmatch(r':?-{2,}:?', c) for c in cells if c):
            continue
        if '神煞' in cells and ('轻重' in cells or '表源' in cells):
            header = cells
            continue
        if header is None or not cells or not cells[0]:
            continue
        rec = dict(zip(header, cells))
        if rec.get('神煞') in ('神煞', ''):
            continue
        rows.append({'section': section, 'name': rec.get('神煞', ''),
                     'cells': rec})
    return rows


def main():
    from modules.事项标准 import SHENSHA_WEIGHT_PENDING  # noqa: E402
    from modules.shensha.制化引擎 import \
        ZHIHUA_WEIGHT_PENDING_BRANCHES  # noqa: E402

    rows = parse_tables(DOC)
    warn = [r for r in rows if r['cells'].get('轻重') == '⚠️']
    seen = {}
    for r in warn:
        nm = r['name']
        seen.setdefault(nm, []).append(r)

    rank_by = json.load(open(DATA, encoding='utf-8'))['rank']

    items = []
    for nm, rs in seen.items():
        r = rs[0]
        c = r['cells']
        rk = rank_by.get(nm, {})
        items.append({
            'name': nm,
            'section': r['section'],
            'dup_sections': [x['section'] for x in rs[1:]],
            'weight_status': c.get('轻重'),
            'biaoyuan': c.get('表源'),
            'chufa': c.get('触发'),
            'koujing': c.get('口径'),
            'zhihua': c.get('制化'),
            'note': c.get('备注', ''),
            'in_frozen_pending': nm in SHENSHA_WEIGHT_PENDING,
            'score_2026': rk.get('scores'),
            'ct_2026': rk.get('ct'),
            'days_2026': rk.get('days'),
            'events_2026': rk.get('evs'),
            'abs_2026': rk.get('abs'),
        })

    # 冻结集内但总表轻重列未标 ⚠️ 的（理论上应为 0）
    missing = sorted(set(SHENSHA_WEIGHT_PENDING) - set(seen))
    # 总表 ⚠️ 但未入冻结集的
    not_frozen = sorted(set(seen) - set(SHENSHA_WEIGHT_PENDING))

    out = {
        'manifest': {
            'source': 'docs/神煞五层验证体系_总表.md',
            'rank_source': 'docs/data/下半场盘点_20261021/hou3ceng_2026.json',
            'frozen_pending': sorted(SHENSHA_WEIGHT_PENDING),
            'zhihua_pending_branches': ZHIHUA_WEIGHT_PENDING_BRANCHES,
        },
        'summary': {
            'weight_warn_rows': len(warn),
            'weight_warn_unique': len(seen),
            'frozen_missing_in_table': missing,
            'warn_not_frozen': not_frozen,
        },
        'items': items,
    }
    json.dump(out, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('轻重列 ⚠️ 行数=%d 去重后=%d' % (len(warn), len(seen)))
    print('冻结集未见表内：', missing or '无')
    print('表内 ⚠️ 未入冻结集：', not_frozen or '无')
    print('-' * 100)
    for it in sorted(items, key=lambda x: x['section']):
        print(f"{it['name']:<8}{it['section'][:12]:<14}"
              f"分值={str(it['score_2026']):<12}"
              f"天次={str(it['ct_2026']):<6}事项={str(it['events_2026']):<4}"
              f"冻结={'Y' if it['in_frozen_pending'] else '-'}")
    print('->', OUT)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print('FAIL:', repr(e))
        sys.exit(1)
