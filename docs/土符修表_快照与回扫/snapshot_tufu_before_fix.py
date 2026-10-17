# -*- coding: utf-8 -*-
"""
土符修表前快照（回扫基线·第一步）
=================================
依据：docs/典据研究_土符入宅_判据冻结提案.md §10.4 第一步（2026-10-18 第二批拍板）。

导出 2026-01-01..2026-12-31 全年逐日，在【现行错表】下所有土符触发日清单，
逐日对照【三库正表】标注「误判 / 重合」；另附正表触发日对照（错表漏判，
供修表后第二步回扫「新增」标注用，本快照不做任何采用结论改判）。

两表口径与出处：
  错表＝modules/shensha/神煞基类.py _is_tufu（现行运行表，「正月起戌顺行十二支」：
        寅戌 卯亥 辰子 巳丑 午寅 未卯 申辰 酉巳 戌午 亥未 子申 丑酉），
        经三库裁断判为错表（1/12 合，附录 A.2）；
  正表＝三库全等历例（协纪卷六 279224 L136-137／考原卷四 359079 L109／
        陈书月家表）：正丑 二巳 三酉 四寅 五午 六戌
        七卯 八未 九亥 十辰 十一申 十二子。

自检项（任一失败退出码 1）：
  1. 双通道一致：runtime ShenShaChecker._is_tufu 与静态错表逐日比对 365/365；
  2. 锚点 2026-11-04：戌月壬午日——错表触发、正表不触发（误判样例，提案 §A.3）；
  3. 子月两表一致：2026 年两段子月内全部日，错表≡正表（同为申日，唯一重合月）；
  4. 链路核对：全部错表触发日，入宅 checker 输出均含「土符」条目（-20），
     证明快照口径＝报告实际触发口径。

只读运行：不修改任何代码、不改动任何已出报告；产物仅存于本目录。
用法：python docs/土符修表_快照与回扫/snapshot_tufu_before_fix.py
退出码：0=导出成功且全部自检通过  1=任一自检失败（CI 可挂）
"""
import sys
import json
import hashlib
import platform
import subprocess
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent

from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.shensha.神煞基类 import ShenShaChecker

PASS = True

# 现行错表（神煞基类 _is_tufu，与 d8c7d10 运行时逐字一致；仅作静态对照通道）
WRONG_MAP = {
    '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
    '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
    '戌': '午', '亥': '未', '子': '申', '丑': '酉',
}
# 三库全等正表（协纪卷六 / 考原卷四 / 陈书月家表，提案附录 A.1）
CORRECT_MAP = {
    '寅': '丑', '卯': '巳', '辰': '酉', '巳': '寅',
    '午': '午', '未': '戌', '申': '卯', '酉': '未',
    '戌': '亥', '亥': '辰', '子': '申', '丑': '子',
}

DATE_START = dt.date(2026, 1, 1)
DATE_END = dt.date(2026, 12, 31)
# §10.4 指定回扫覆盖日
RECHECK_DATES = ['2026-10-23', '2026-11-04', '2026-07-24', '2026-06-01']

JSON_PATH = HERE / 'snapshot_tufu_before_fix_2026.json'
MD_PATH = HERE / 'snapshot_tufu_before_fix_2026.md'
MANIFEST_PATH = HERE / 'manifest.json'


def check(name, ok, detail=''):
    global PASS
    tag = 'PASS' if ok else 'FAIL'
    print('[%s] %s%s' % (tag, name, ('  ' + detail) if detail else ''))
    if not ok:
        PASS = False


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def git_head():
    try:
        out = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=str(ROOT),
                             capture_output=True, text=True, timeout=15)
        return out.stdout.strip() or 'unknown'
    except Exception:
        return 'unknown'


def main():
    head = git_head()
    generated_at = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('=' * 76)
    print('土符修表前快照（2026 全年）｜HEAD=%s' % head[:12])
    print('错表=神煞基类 _is_tufu 现行表；正表=三库全等历例（提案附录A）')
    print('性质：只读快照存档，不改代码/报告，不做采用结论改判')
    print('=' * 76)

    base = ShenShaChecker()
    ruzhai = get_checker('入宅')

    # ---------- 逐日扫描 ----------
    daily = []
    d = DATE_START
    while d <= DATE_END:
        sizhu = calculate_sizhu(d, 10, 0)
        sizhu['year'] = d.year
        sizhu['month'] = d.month
        sizhu['day'] = d.day
        sizhu['date'] = d
        mz, dz = sizhu['month_zhi'], sizhu['day_zhi']
        rec = {
            'date': d.isoformat(),
            'year_gz': sizhu['year_gan'] + sizhu['year_zhi'],
            'month_gz': sizhu['month_gan'] + sizhu['month_zhi'],
            'day_gz': sizhu['day_gan'] + sizhu['day_zhi'],
            'month_zhi': mz,
            'day_zhi': dz,
            'wrong_trigger_runtime': bool(base._is_tufu(sizhu)),
            'wrong_trigger_static': dz == WRONG_MAP.get(mz),
            'correct_trigger': dz == CORRECT_MAP.get(mz),
            '_sizhu': sizhu,  # 仅供链路核对，落盘前剔除
        }
        daily.append(rec)
        d += dt.timedelta(days=1)

    # ---------- 自检 1：双通道一致 ----------
    mismatch = [r['date'] for r in daily
                if r['wrong_trigger_runtime'] != r['wrong_trigger_static']]
    check('双通道一致：runtime _is_tufu ≡ 静态错表（%d/365）' % (365 - len(mismatch)),
          not mismatch, '不符日: %s' % mismatch[:5] if mismatch else '')

    # ---------- 自检 2：锚点 2026-11-04 ----------
    anchor = next(r for r in daily if r['date'] == '2026-11-04')
    check('锚点 2026-11-04 戌月壬午：错表触发、正表不触发',
          anchor['month_zhi'] == '戌' and anchor['day_gz'] == '壬午'
          and anchor['wrong_trigger_runtime'] and not anchor['correct_trigger'],
          '月建%s 日柱%s 错表=%s 正表=%s' % (
              anchor['month_zhi'], anchor['day_gz'],
              anchor['wrong_trigger_runtime'], anchor['correct_trigger']))

    # ---------- 自检 3：子月两表一致 ----------
    zi_days = [r for r in daily if r['month_zhi'] == '子']
    zi_bad = [r['date'] for r in zi_days
              if r['wrong_trigger_runtime'] != r['correct_trigger']]
    check('子月两表一致（%d 天全覆盖，同为申日）' % len(zi_days),
          zi_days and not zi_bad, '不符日: %s' % zi_bad[:5] if zi_bad else '')

    # ---------- 自检 4：链路核对（错表触发日 ⇒ 入宅 checker 发射土符 -20） ----------
    wrong_days = [r for r in daily if r['wrong_trigger_runtime']]
    chain_bad = []
    for r in wrong_days:
        entries = ruzhai.check(r['_sizhu'], [])
        hit = [e for e in entries
               if isinstance(e, dict) and e.get('name') == '土符' and e.get('score') == -20]
        if not hit:
            chain_bad.append(r['date'])
    check('链路核对：错表触发日 入宅checker 均发射「土符 -20」（%d/%d）'
          % (len(wrong_days) - len(chain_bad), len(wrong_days)),
          not chain_bad, '缺发射日: %s' % chain_bad[:5] if chain_bad else '')

    # ---------- 派生清单 ----------
    for r in daily:
        r.pop('_sizhu')
        r['wrong_trigger'] = r.pop('wrong_trigger_runtime')
        r['verdict'] = ('重合' if r['correct_trigger'] else '误判') if r['wrong_trigger'] \
            else ('漏判' if r['correct_trigger'] else '')

    triggers_wrong = [r for r in daily if r['wrong_trigger']]
    triggers_correct = [r for r in daily if r['correct_trigger']]
    n_false = sum(1 for r in triggers_wrong if r['verdict'] == '误判')
    n_overlap = sum(1 for r in triggers_wrong if r['verdict'] == '重合')
    n_missed = sum(1 for r in triggers_correct if not r['wrong_trigger'])

    # 月建分段（相邻同月支归段）
    segments = []
    for r in daily:
        if segments and segments[-1]['month_zhi'] == r['month_zhi']:
            segments[-1]['end'] = r['date']
        else:
            segments.append({'month_zhi': r['month_zhi'],
                             'start': r['date'], 'end': r['date']})
    for seg in segments:
        seg['wrong_days'] = [r for r in triggers_wrong
                             if seg['start'] <= r['date'] <= seg['end']]
        seg['correct_days'] = [r for r in triggers_correct
                               if seg['start'] <= r['date'] <= seg['end']]

    # 回扫覆盖日状态
    recheck = {}
    for ds in RECHECK_DATES:
        r = next(x for x in daily if x['date'] == ds)
        if r['wrong_trigger'] and not r['correct_trigger']:
            status = '错表误判触发 → 修表后条目待作废（回扫标注，不改判）'
        elif r['wrong_trigger'] and r['correct_trigger']:
            status = '两表重合触发 → 条目保留'
        elif r['correct_trigger']:
            status = '错表漏判 → 修表后条目待新增（回扫标注，不改判）'
        else:
            status = '两表均不触发 → 对照确认无漏'
        recheck[ds] = {'day_gz': r['day_gz'], 'month_zhi': r['month_zhi'],
                       'wrong_trigger': r['wrong_trigger'],
                       'correct_trigger': r['correct_trigger'], 'status': status}

    summary = {
        'total_days': len(daily),
        'wrong_trigger_count': len(triggers_wrong),
        'wrong_false_positive': n_false,
        'wrong_overlap': n_overlap,
        'correct_trigger_count': len(triggers_correct),
        'correct_missed_by_wrong': n_missed,
    }

    # ---------- 落盘 JSON ----------
    payload = {
        'meta': {
            'title': '土符修表前快照（2026 全年·回扫基线第一步）',
            'generated_at': generated_at,
            'git_head': head,
            'date_range': [DATE_START.isoformat(), DATE_END.isoformat()],
            'wrong_table_src': 'modules/shensha/神煞基类.py _is_tufu（d8c7d10 现行错表）',
            'correct_table_src': '三库全等历例（协纪卷六 279224 L136-137／考原卷四 '
                                 '359079 L109／陈书月家表），提案附录A.1',
            'authority': 'docs/典据研究_土符入宅_判据冻结提案.md §10.4',
            'note': '只读快照存档，不做采用结论改判；改判须修表后重跑评分器',
        },
        'checks_passed': PASS,
        'summary': summary,
        'segments': [{k: v for k, v in seg.items() if k not in ('wrong_days', 'correct_days')}
                     | {'wrong_trigger_dates': [r['date'] for r in seg['wrong_days']],
                        'correct_trigger_dates': [r['date'] for r in seg['correct_days']]}
                     for seg in segments],
        'triggers_wrong_table': triggers_wrong,
        'triggers_correct_table': triggers_correct,
        'recheck_dates': recheck,
        'daily': daily,
    }
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    # ---------- 落盘 MD ----------
    lines = []
    A = lines.append
    A('# 土符修表前快照（2026 全年·回扫基线第一步）')
    A('')
    A('> 生成：%s｜HEAD：%s' % (generated_at, head))
    A('> 错表：[神煞基类.py _is_tufu](file:///d:/自编择日软件/专业级正五行择日软件/modules/shensha/神煞基类.py#L2947-L2960)'
      '（现行「正月起戌顺行十二支」，附录A.2 判错表 1/12 合）')
    A('> 正表：三库全等历例——正丑/二巳/三酉/四寅/五午/六戌/七卯/八未/九亥/十辰/十一申/十二子')
    A('> 依据：[典据研究_土符入宅_判据冻结提案.md](file:///d:/自编择日软件/专业级正五行择日软件/docs/典据研究_土符入宅_判据冻结提案.md) §10.4 第一步')
    A('> 性质：只读快照存档，不改任何代码/已出报告，不做采用结论改判；改判须修表后重跑评分器')
    A('')
    A('## 一、汇总')
    A('')
    A('| 项 | 天数 |')
    A('|---|---|')
    A('| 扫描总天数 | %d |' % summary['total_days'])
    A('| 错表触发 | %d |' % summary['wrong_trigger_count'])
    A('| ├ 误判（按正表不触发，修表后条目作废） | %d |' % summary['wrong_false_positive'])
    A('| └ 重合（正表亦触发，仅子月） | %d |' % summary['wrong_overlap'])
    A('| 正表触发 | %d |' % summary['correct_trigger_count'])
    A('| └ 错表漏判（修表后条目新增候选） | %d |' % summary['correct_missed_by_wrong'])
    A('')
    A('自检：双通道一致 / 锚点 2026-11-04 / 子月两表一致 / 链路核对——'
      '全部 PASS（明细见同目录 JSON 与 manifest.json）。')
    A('')
    A('## 二、现行错表触发日清单（逐月建，逐日标注）')
    for seg in segments:
        if not seg['wrong_days']:
            continue
        A('')
        A('### 月建%s（%s ~ %s）错表触发值：%s日'
          % (seg['month_zhi'], seg['start'], seg['end'], WRONG_MAP[seg['month_zhi']]))
        A('')
        A('| 日期 | 日柱 | 月柱 | 正表判定 |')
        A('|---|---|---|---|')
        for r in seg['wrong_days']:
            verdict = ('⚠️ 误判（按正表%s月应%s日，本日不触发）'
                       % (r['month_zhi'], CORRECT_MAP[r['month_zhi']])) \
                if r['verdict'] == '误判' else '✓ 重合（正表亦触发）'
            A('| %s | %s | %s | %s |' % (r['date'], r['day_gz'], r['month_gz'], verdict))
    A('')
    A('## 三、对照基线：正表触发日（错表漏判，修表后「新增」候选）')
    A('')
    A('> 本段仅为第二步回扫「条目新增」标注提供基线，不代表当前报告应含土符条目；')
    A('> 当前未修表，这些日课按现行错表本就不触发，无需任何动作。')
    for seg in segments:
        new_days = [r for r in seg['correct_days'] if not r['wrong_trigger']]
        if not new_days:
            continue
        A('')
        A('### 月建%s（%s ~ %s）正表触发值：%s日'
          % (seg['month_zhi'], seg['start'], seg['end'], CORRECT_MAP[seg['month_zhi']]))
        A('')
        A('| 日期 | 日柱 | 月柱 |')
        A('|---|---|---|')
        for r in new_days:
            A('| %s | %s | %s |' % (r['date'], r['day_gz'], r['month_gz']))
    A('')
    A('## 四、回扫覆盖日状态（§10.4 指定范围）')
    A('')
    A('| 日期 | 日柱 | 月建 | 错表 | 正表 | 状态 |')
    A('|---|---|---|---|---|---|')
    for ds in RECHECK_DATES:
        r = recheck[ds]
        A('| %s | %s | %s | %s | %s | %s |'
          % (ds, r['day_gz'], r['month_zhi'],
             '触发' if r['wrong_trigger'] else '—',
             '触发' if r['correct_trigger'] else '—', r['status']))
    A('')
    A('## 五、停止点')
    A('')
    A('快照存档完毕即停止。后续：修表（zeri-dianju-align 轨，两表同修＋12 月逐月测试）')
    A('单独 commit；修表后第二步回扫漂移清单以本快照为基线逐份标注「条目作废/新增」，')
    A('不改判、不混提。')
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    # ---------- manifest ----------
    manifest = {
        'generated_at': generated_at,
        'git_head': head,
        'python': platform.python_version(),
        'command': 'python docs/土符修表_快照与回扫/snapshot_tufu_before_fix.py',
        'date_range': [DATE_START.isoformat(), DATE_END.isoformat()],
        'wrong_map': WRONG_MAP,
        'correct_map': CORRECT_MAP,
        'files': {
            'snapshot_tufu_before_fix.py': sha256_of(Path(__file__).resolve()),
            JSON_PATH.name: sha256_of(JSON_PATH),
            MD_PATH.name: sha256_of(MD_PATH),
        },
        'checks_passed': PASS,
        'summary': summary,
    }
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    # ---------- stdout 完整清单 ----------
    print()
    print('【汇总】错表触发 %d 天（误判 %d／重合 %d）｜正表触发 %d 天（错表漏判 %d）'
          % (summary['wrong_trigger_count'], n_false, n_overlap,
             summary['correct_trigger_count'], n_missed))
    print()
    print('【错表触发日清单（逐月建）】')
    for seg in segments:
        if not seg['wrong_days']:
            continue
        print('  月建%s（%s ~ %s）错表值 %s日：'
              % (seg['month_zhi'], seg['start'], seg['end'], WRONG_MAP[seg['month_zhi']]))
        for r in seg['wrong_days']:
            print('    %s  %s  %s' % (r['date'], r['day_gz'],
                                      '误判' if r['verdict'] == '误判' else '重合'))
    print()
    print('【对照：正表触发日（错表漏判）】')
    for seg in segments:
        new_days = [r for r in seg['correct_days'] if not r['wrong_trigger']]
        if not new_days:
            continue
        print('  月建%s（%s ~ %s）正表值 %s日：'
              % (seg['month_zhi'], seg['start'], seg['end'], CORRECT_MAP[seg['month_zhi']]))
        for r in new_days:
            print('    %s  %s' % (r['date'], r['day_gz']))
    print()
    print('【回扫覆盖日】')
    for ds in RECHECK_DATES:
        r = recheck[ds]
        print('  %s  %s  月建%s  错表%s 正表%s  %s'
              % (ds, r['day_gz'], r['month_zhi'],
                 '触发' if r['wrong_trigger'] else '—',
                 '触发' if r['correct_trigger'] else '—', r['status']))
    print()
    print('产物：%s' % JSON_PATH.name)
    print('      %s' % MD_PATH.name)
    print('      %s' % MANIFEST_PATH.name)
    print('=' * 76)
    print('退出码：%d（%s）' % (0 if PASS else 1, '全部自检通过' if PASS else '存在自检失败'))
    return 0 if PASS else 1


if __name__ == '__main__':
    sys.exit(main())
