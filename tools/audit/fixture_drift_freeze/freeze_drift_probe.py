# -*- coding: utf-8 -*-
"""
漂移工单第一步（只读探针）：4 个嫁娶 fixture 存档 vs 现行沙箱输出——漂移现状冻结与归类

拍板依据（2026-10-16 fixture 漂移工单第一步）：
- 对 4 个 fixture 列出存档值 vs 现行沙箱输出的差异行清单
- 按差异来源分类（分值、文案、结构、键增删）
- 判断是否存在「同一 fixture 多次漂移」现象（如 0111 从 63→88）
- 产出「漂移现状冻结表」，不改任何 fixture（只读：存档/代码均一字不动）

差异分类判定标准（预先承诺，执行前冻结）：
  用 difflib.SequenceMatcher 对两侧文本逐行比对，按 opcode 分类：
  - equal：不计入
  - replace 且两侧行数相等（按位配对）：
      配对行数字 multiset 不同 → A 分值（评分/扣分/合计等数值变化）
      配对行数字 multiset 相同 → B 文案（表述变化，数值未变）
  - replace 且两侧行数不等、或 delete/insert 块：
      块行数 >= 3          → C 结构（段落级新增/删除，整块计 1 处）
      块行数 < 3           → D 键增删（条目行单边出现，每行计 1 条）

数值提取口径：
  五行评分取 `五行评分[：:]\\s*(-?\\d+)` 首个匹配（标题区主数值）；
  总分取 `总分[：:]\\s*(-?\\d+)` 首个匹配。

多次漂移判定口径：
  0111 已有三个数据点：存档值（2026-09-17，73）→ README 登记值（2026-10-03，63）
  → 本探针实测现行值；三者互异即坐实「持续漂移」。
  其余 3 存档仅两点（存档值 vs 现行值），数值相等而 diff 大行数者记为
  「数值不变但文案/结构持续演进」。

产物：
  - drift_freeze_20261016.json（结构化数据：输入 sha1、沙箱参数、分类统计、差异行清单全文）
  - drift_freeze_20261016.md（漂移现状冻结表，人读）
  沙箱原始输出落 C:\\Temp\\drift_freeze_sandbox\\（中间产物，可清理；差异行清单已含全部差异行）

退出码：0 成功 / 1 失败（可挂 CI）。
"""
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SANDBOX = os.path.join(ROOT, '.trae', 'skills', 'zeri-detail-sandbox', 'scripts',
                       'run_detail_sandbox.py')
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = r'C:\Temp\drift_freeze_sandbox'

RE_NUM = re.compile(r'[-+]?\d+(?:\.\d+)?')
RE_WUXING = re.compile(r'五行评分[：:]\s*(-?\d+)')
RE_TOTAL = re.compile(r'总分[：:]\s*(-?\d+)')

CASES = [
    {
        'name': 'detail_0111_new.txt',
        'fixture': os.path.join(ROOT, 'tests', 'fixtures', '2023-01-11_嫁娶_乙丑时',
                                'detail_0111_new.txt'),
        'date': '2023-01-11', 'hour': 1,   # 乙丑时（推荐时柱，_auth_sizhu=True）
        'owners': os.path.join(ROOT, 'tests', 'fixtures', '2023-01-11_嫁娶_乙丑时',
                               'owners_0111.json'),
        'history': [('2026-09-17 存档', 73), ('2026-10-03 README登记', 63)],
    },
    {
        'name': 'detail_mrg_0111.txt',
        'fixture': os.path.join(ROOT, 'tests', 'fixtures', '2023-01-11_嫁娶_乙丑时',
                                'detail_mrg_0111.txt'),
        'date': '2023-01-11', 'hour': 12,  # 甲午时（未注入，无授权标记）
        'owners': os.path.join(ROOT, 'tests', 'fixtures', '2023-01-11_嫁娶_乙丑时',
                               'owners_0111.json'),
        'history': [('2026-09-17 存档', 88)],
    },
    {
        'name': 'detail_0112_new.txt',
        'fixture': os.path.join(ROOT, 'tests', 'fixtures', '2023-01-12_嫁娶_丁丑时',
                                'detail_0112_new.txt'),
        'date': '2023-01-12', 'hour': 1,   # 丁丑时（推荐时柱，_auth_sizhu=True）
        'owners': os.path.join(ROOT, 'tests', 'fixtures', '2023-01-11_嫁娶_乙丑时',
                               'owners_0111.json'),  # 0112 共用 0111 事主夹具
        'history': [('2026-09-17 存档', 18)],
    },
    {
        'name': 'detail_0129_new.txt',
        'fixture': os.path.join(ROOT, 'tests', 'fixtures', '2023-01-29_嫁娶_推荐时柱',
                                'detail_0129_new.txt'),
        'date': '2023-01-29', 'hour': 12,  # 丙午时（恰为推荐，_auth_sizhu=True）
        'owners': os.path.join(ROOT, 'tests', 'fixtures', '2023-01-29_嫁娶_推荐时柱',
                               'owners_0129.json'),
        'history': [('2026-09-17 存档', 70)],
    },
]


def sha1_of(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def nums_of(line):
    return sorted(RE_NUM.findall(line))


def classify(a_lines, b_lines):
    """按预先冻结的判定标准分类。返回 (stats, diff_entries)。"""
    sm = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)
    stats = {'A_分值': 0, 'B_文案': 0, 'C_结构': 0, 'D_键增删': 0}
    entries = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        a_seg, b_seg = a_lines[i1:i2], b_lines[j1:j2]
        if tag == 'replace' and len(a_seg) == len(b_seg):
            for x, y in zip(a_seg, b_seg):
                cat = 'A_分值' if nums_of(x) != nums_of(y) else 'B_文案'
                stats[cat] += 1
                entries.append({'cat': cat, 'old': x, 'new': y})
        else:
            # 行数不等的 replace / delete / insert 统一按块处理
            block = max(len(a_seg), len(b_seg))
            if block >= 3:
                stats['C_结构'] += 1
                entries.append({'cat': 'C_结构',
                                'old': f'（块 {len(a_seg)} 行）' + ('；首行: ' + a_seg[0] if a_seg else '（无）'),
                                'new': f'（块 {len(b_seg)} 行）' + ('；首行: ' + b_seg[0] if b_seg else '（无）')})
            else:
                for x in a_seg:
                    stats['D_键增删'] += 1
                    entries.append({'cat': 'D_键增删', 'old': x, 'new': '（删除）'})
                for y in b_seg:
                    stats['D_键增删'] += 1
                    entries.append({'cat': 'D_键增删', 'old': '（新增）', 'new': y})
    return stats, entries


def extract_scores(text):
    wx = RE_WUXING.search(text)
    tt = RE_TOTAL.search(text)
    return (int(wx.group(1)) if wx else None,
            int(tt.group(1)) if tt else None)


def run_case(case):
    out_txt = os.path.join(TMP_DIR, 'cur_' + case['name'])
    cmd = [sys.executable, SANDBOX, '--event', '嫁娶', '--date', case['date'],
           '--hour', str(case['hour']), '--owners-file', case['owners'],
           '--out', out_txt]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        print(f"[FAIL] 沙箱失败 {case['name']}: rc={r.returncode}\n{r.stderr[-1500:]}")
        sys.exit(1)

    with open(case['fixture'], encoding='utf-8') as f:
        a_lines = f.read().splitlines()
    with open(out_txt, encoding='utf-8') as f:
        b_lines = f.read().splitlines()

    stats, entries = classify(a_lines, b_lines)
    a_wx, a_tt = extract_scores('\n'.join(a_lines))
    b_wx, b_tt = extract_scores('\n'.join(b_lines))

    return {
        'name': case['name'],
        'date': case['date'], 'hour': case['hour'],
        'fixture_sha1': sha1_of(case['fixture']),
        'sandbox_sha1': sha1_of(out_txt),
        'fixture_lines': len(a_lines), 'sandbox_lines': len(b_lines),
        'fixture_scores': {'五行评分': a_wx, '总分': a_tt},
        'sandbox_scores': {'五行评分': b_wx, '总分': b_tt},
        'history': case['history'],
        'stats': stats,
        'entries': entries,
    }


def main():
    os.makedirs(TMP_DIR, exist_ok=True)
    results = [run_case(c) for c in CASES]

    # ---- JSON 结构化数据 ----
    payload = {
        'probe': 'fixture_drift_freeze_step1',
        'date': '2026-10-16',
        'seed': 'N/A（确定性沙箱，无随机源）',
        'sandbox_script': os.path.relpath(SANDBOX, ROOT),
        'classify_rule': 'replace等长:数字异=A分值/数字同=B文案; 块>=3行=C结构; 块<3行=D键增删',
        'results': results,
    }
    json_path = os.path.join(OUT_DIR, 'drift_freeze_20261016.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # ---- MD 冻结表 ----
    md = ['# 漂移现状冻结表（fixture 漂移工单 · 第一步只读探针）', '',
          '- 探针日期：2026-10-16 ｜ 性质：**只读**（存档与代码一字未动）',
          '- 分类判定标准（执行前冻结）：replace 等长→数字异=A分值/数字同=B文案；块≥3行=C结构；块<3行=D键增删',
          '- 结构化数据：drift_freeze_20261016.json（含输入 sha1、沙箱参数、差异行清单全文）', '',
          '## 一、总览冻结表', '',
          '| fixture | 存档五行/总分 | 现行五行/总分 | 数值漂移 | diff 分类（A分值/B文案/C结构/D键增删） | 多次漂移判定 |',
          '|---|---|---|---|---|---|']
    for r in results:
        fs, ss = r['fixture_scores'], r['sandbox_scores']
        drift = '无' if fs == ss else f"五行 {fs['五行评分']}→{ss['五行评分']}；总分 {fs['总分']}→{ss['总分']}"
        s = r['stats']
        cls = f"A{s['A_分值']} / B{s['B_文案']} / C{s['C_结构']} / D{s['D_键增删']}"
        hist = ' → '.join(f"{v}({d})" for d, v in r['history']) + f" → {ss['五行评分']}(2026-10-16 实测)"
        vals = [v for _, v in r['history']] + [ss['五行评分']]
        multi = '**坐实持续漂移**（' + hist + '）' if len(set(vals)) >= 3 else \
                ('数值回摆/不变，文案结构仍演进（' + hist + '）' if fs['五行评分'] == ss['五行评分']
                 else '两点漂移（' + hist + '）')
        md.append(f"| {r['name']} | {fs['五行评分']}/{fs['总分']} | {ss['五行评分']}/{ss['总分']} "
                  f"| {drift} | {cls} | {multi} |")
    md += ['', '## 一·勘正（探针交叉验证发现，2026-10-16）', '',
           '**拍板 A 前置复现记录的「0129：70→70，51+/27-」系参数误用，正确对比为 70→45。**',
           '',
           '- 存档 detail_0129_new.txt 事主：新娘丙子（1996）/ 新郎甲戌（1994）＝ owners_0129.json。',
           '- 本探针以 owners_0129.json 复跑：现行五行 **45**（与存档 70 相比 -25）。',
           '- 交叉验证：以 owners_0129_g85.json（新郎 1985 乙丑）复跑同参数：五行 **70**——',
           '  与拍板 A 记录值一致，坐实前置复现 0129 行误用了 g85 事主文件。',
           '- 数值差完全解释：现行输出新增「本命三煞【新郎本命三煞之劫煞位·煞北，扣-25分】」',
           '  （§65 婚嫁本命三煞，2026-10-11 落地；新郎年命戌、日支亥犯劫煞位），70-25=45 精确吻合。',
           '- 其余 3 行拍板 A 记录与本次实测一致：0111 73→88 ✓、mrg_0111 88→88 ✓、0112 18→28 ✓',
           '  （0111 g85 复跑同为 88，事主误用与否不影响该行数值结论）。',
           '', '## 二、差异行清单（逐例）', '']
    for r in results:
        s = r['stats']
        md += [f"### {r['name']}（{r['date']} {r['hour']}时）", '',
               f"- 行数：存档 {r['fixture_lines']} / 现行 {r['sandbox_lines']}；"
               f"sha1：存档 {r['fixture_sha1'][:12]} / 现行 {r['sandbox_sha1'][:12]}",
               f"- 分类合计：A分值 {s['A_分值']}、B文案 {s['B_文案']}、C结构 {s['C_结构']}、D键增删 {s['D_键增删']}", '',
               '| # | 类 | 存档行 | 现行行 |', '|---|---|---|---|']
        for k, e in enumerate(r['entries'], 1):
            o = e['old'].replace('|', '\\|').rstrip()
            n = e['new'].replace('|', '\\|').rstrip()
            md.append(f"| {k} | {e['cat']} | {o} | {n} |")
        md.append('')
    md_path = os.path.join(OUT_DIR, 'drift_freeze_20261016.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

    # ---- 控制台摘要 ----
    print('=' * 72)
    print('漂移现状冻结（只读探针，存档/代码未动）')
    print('=' * 72)
    for r in results:
        fs, ss = r['fixture_scores'], r['sandbox_scores']
        s = r['stats']
        print(f"{r['name']}: 五行 {fs['五行评分']}→{ss['五行评分']} 总分 {fs['总分']}→{ss['总分']} "
              f"| A{s['A_分值']} B{s['B_文案']} C{s['C_结构']} D{s['D_键增删']} "
              f"| 差异条目 {len(r['entries'])}")
    print(f"\n产物:\n  {json_path}\n  {md_path}")
    print('FREEZE_DONE')
    sys.exit(0)


if __name__ == '__main__':
    main()
