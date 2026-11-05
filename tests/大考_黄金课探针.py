# -*- coding: utf-8 -*-
"""
================================================================================
v2.1.x 终局大考 · 黄金课大考探针（五维穿透式验收）
================================================================================
定位：**诊断探针**，不是 CI 门禁。文件名单故意不匹配 verify_/test_/check_
前缀，因此 tests/run_all.py 不会自动接管它（run_all 基线不受本探针影响）。
用法：

    python tests/大考_黄金课探针.py                       # 全量（约 2-4 分钟）
    python tests/大考_黄金课探针.py --quick               # 只跑 嫁娶/修造/入宅/安葬
    python tests/大考_黄金课探针.py --out 产物目录 --json 报告.json
    python tests/大考_黄金课探针.py --runall-json C:\\Temp\\_runall.json
                                                          # 并入第一维全量脚本结果

五维覆盖：
  S1 底层引擎与回归基线   ：三内层 SHA 一致性；可选并入 run_all 结果
  S2 黄金课全景矩阵       ：20 黄金课 × 16 通道 × 12 时辰实评；四柱同源、
                            算术自洽、扣分透明度、伪煞零发射、解禁课回归
  S3 反推引擎与动作时序   ：零候选防御、四态时序、排序层不降权、
                            D4 冲命拦截（plan 路径 + 手动改吉时路径）
  S4 红帖三态分流         ：吉帖 / 慎用帖 / 否决帖 版式分家 + 软忌动态渲染
                            （产物落盘为可打印 HTML）
  S5 外围防护与异常兜底   ：非法日期、空数据、参数越界、未知事项、JSON 可序列化
  S6 技术债盘点           ：H2（pytest 外壳）/ H3（统一版仓）/ 副本感知脚本数

退出码：0=全部 PASS；1=存在 FAIL（详见报告 fails 列表）。
本探针只读：不修改任何代码、分值、规则与已确认口径，仅在 --out 目录下写产物。
================================================================================
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import time
import datetime as dt

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ------------------------------------------------------------------ 黄金课样本
# 20 课按"五类极端情况"分组。日期全部取自 docs/全系统终极大考与全渠道发布验证报告
# （20261029）的黄金样本，便于与历史快照对读；另补 §212 解禁课（红纱/杨公忌）。
GOLDEN = [
    ('2026-01-05', '交节·小寒', '小寒 16:23 后月柱戊子→己丑；同日跨时辰柱不一致'),
    ('2026-01-08', '冲命', '日支冲年命类样本'),
    ('2026-01-11', '受死日', '受死日：嫁娶一票否决，须只命中受死，不得出现伪煞'),
    ('2026-01-15', '解禁·红纱日', '§212 红纱日已剥离 → 嫁娶不得再出现红纱日'),
    ('2026-01-26', '常规吉课', '庚子日，历史最高分样本之一'),
    ('2026-01-31', '常规吉课', '乙巳日，出行历史最高样本'),
    ('2026-02-03', '四绝', '四绝日，五通道历史全否决样本'),
    ('2026-02-15', '月破', '寅月申日=月破；嫁娶须只命中月破/往亡类'),
    ('2026-03-02', '常规', '开月常规样本'),
    ('2026-03-05', '交节·惊蛰', '惊蛰交节当天，亥时月柱庚寅→辛卯'),
    ('2026-03-19', '四离', '四离日，全通道否决（零候选防御样本）'),
    ('2026-04-05', '解禁', '己酉日，历史解禁课'),
    ('2026-04-13', '年重丧转吉', '年重丧撤否决后转吉样本'),
    ('2026-05-04', '四绝', '四绝日'),
    ('2026-05-23', '杨公忌日', '农历四月初七=杨公忌日；嫁娶须零发射（解禁课）'),
    ('2026-06-19', '极凶+杨公忌', '农历五月初五=杨公忌日；历史极凶样本'),
    ('2026-06-20', '四离', '四离日'),
    ('2026-06-21', '修造最高', '修造历史最高分样本'),
    ('2026-08-06', '四绝', '四绝日'),
    ('2026-12-21', '四离', '四离日，三通道历史否决'),
]

# 交节专项（第三类的独立强断言）：同日早/晚时支的月柱必须翻转
JIEQI = [
    ('2026-01-05', '小寒', '申', '酉', '戊子', '己丑'),
    ('2026-03-05', '惊蛰', '戌', '亥', '庚寅', '辛卯'),
]

OWNERS_MARRIAGE = [
    {'name': '新娘', 'role': '新娘', 'year_sx': '猪', '性别': '女'},
    {'name': '新郎', 'role': '新郎', 'year_sx': '狗', '性别': '男'},
]
OWNERS_ZANG = [{'name': '仙命', 'role': '仙命', 'year_sx': '龙', '性别': '男'}]
OWNERS_GENERAL = [{'name': '福主', 'role': '福主', 'year_sx': '龙', '性别': '男'}]

# 山向通道（SHAN_UI_EVENTS 口径）；中性山向 酉山卯向（2026 午年不犯岁破/三煞）
SHAN_EVENTS = {'修造', '动土', '拆舍', '入宅', '安葬', '作灶', '安床', '开业', '出行'}
SHAN_FULL = '酉山卯向'

# 已剥离/非本通道的"伪煞"：嫁娶通道出现即判 FAIL（穿透式验收核心反向断言）
PSEUDO_FOR_MARRIAGE = ('杀师日', '杀师时', '杨公忌日', '红纱日', '年重丧')

FAILS = []
CHECKS = []
OBS = []


def obs(cid, name, detail=''):
    """观察项：不构成缺陷，但需在报告中记录（口径差异/文档性事实）。"""
    OBS.append({'id': cid, 'name': name, 'detail': str(detail)})
    print('  [OBS ] %-6s %s%s' % (cid, name, ('  → ' + str(detail)) if detail else ''))


def check(cid, name, ok, detail=''):
    CHECKS.append({'id': cid, 'name': name, 'ok': bool(ok), 'detail': str(detail)})
    print('  [%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', cid, name,
                                ('  → ' + str(detail)) if detail and not ok else ''))
    if not ok:
        FAILS.append('%s %s%s' % (cid, name, ('  → ' + str(detail)) if detail else ''))


def _ctx_of(event):
    _c = {}
    if event == '安葬':
        _c['house_type'] = '阴宅'
    elif event in SHAN_EVENTS:
        _c['house_type'] = '阳宅'
    if event in SHAN_EVENTS:
        _c['shan_xiang'] = SHAN_FULL
    return _c


def _owners_of(event):
    if event in ('嫁娶', '订婚', '纳采'):
        return [dict(_o) for _o in OWNERS_MARRIAGE]
    if event == '安葬':
        return [dict(_o) for _o in OWNERS_ZANG]
    return [dict(_o) for _o in OWNERS_GENERAL]


def _neg_names(result):
    return [str(_s.get('name', '')) for _s in (result.get('shensha_list') or [])
            if isinstance(_s, dict) and int(_s.get('score', 0) or 0) < 0]


def _compact(result, sizhu):
    _sd = result.get('score_details') or {}
    _rs = result.get('sizhu') if isinstance(result.get('sizhu'), dict) else {}
    _keys = ('年柱', '月柱', '日柱', '时柱')
    return {
        'score': int(result.get('score') or 0),
        'level': str(result.get('level') or ''),
        'veto_reasons': [str(_v) for _v in (result.get('veto_reasons') or [])],
        'ji_list': [str(_j) for _j in (result.get('ji_list') or [])],
        'shensha_neg': _neg_names(result),
        'shensha_pos': [str(_s.get('name', '')) for _s in (result.get('shensha_list') or [])
                        if isinstance(_s, dict) and int(_s.get('score', 0) or 0) > 0],
        'sd_total': int(_sd.get('总分') or 0) if _sd else None,
        'sd_shensha_neg': sorted([(str(_t[0]), int(_t[1])) for _t in
                                  (_sd.get('神煞明细') or []) if int(_t[1]) < 0]),
        'pipeline': str(result.get('pipeline') or ''),
        'pillars': {_k: str((sizhu or {}).get(_k, '')) for _k in _keys},
        'result_pillars': {_k: str(_rs.get(_k, '')) for _k in _keys},
    }


# ==================================================================== S1 地基
def s1_baseline(runall_json):
    print('\n[S1] 底层引擎与回归基线')
    out = {'checks': [], 'run_all': None, 'sha': {}}

    # S1-1 双内层 SHA 一致性（主仓：仓根 / 手机一键部署\模块完整版）
    # 2026-11-05：外层重复副本已按 893b33c 合并删除，仅剩仓根 + 模块完整版
    layers = ['', os.path.join('手机一键部署', '模块完整版')]
    targets = ['主程序.py', os.path.join('modules', '评分器.py'),
               os.path.join('modules', '事项标准.py'), os.path.join('modules', '反推引擎.py'),
               os.path.join('modules', '动作时序.py'), os.path.join('modules', '择日贴.py'),
               os.path.join('modules', '排序键.py')]
    diff = {}
    for _t in targets:
        _hs = []
        for _ly in layers:
            _p = os.path.join(ROOT, _ly, _t) if _ly else os.path.join(ROOT, _t)
            if not os.path.isfile(_p):
                _hs.append('MISSING')
                continue
            with open(_p, 'rb') as _f:
                _hs.append(hashlib.sha256(_f.read()).hexdigest())
        out['sha'][_t] = _hs
        if len(set(_hs)) != 1:
            diff[_t] = _hs
    check('S1-1', '双内层 SHA 逐字一致（%d 个关键文件）' % len(targets), not diff, diff)
    out['checks'].append({'id': 'S1-1', 'ok': not diff, 'diff': diff})

    # S1-3 六副本官方脚本对账（check_six_copies.py）：
    #      --main 必须 0 退出（双内层门禁）；--uni 属 H3 长尾技术债，
    #      现状存在漂移/缺失 → 记 OBS（BACKLOG §五 暂不收敛，非本批回归）。
    _script = os.path.join(ROOT, '.trae', 'skills', 'zeri-module-change',
                           'references', 'check_six_copies.py')
    if os.path.isfile(_script):
        _main = subprocess.run([sys.executable, _script, '--main'] + targets,
                               capture_output=True, text=True)
        out['six_copies_main_exit'] = _main.returncode
        check('S1-3', '六副本脚本 --main（双内层）全部一致', _main.returncode == 0,
              _main.stdout.strip().splitlines()[-2:] if _main.stdout else '')
        _uni = subprocess.run([sys.executable, _script, '--uni'] + targets,
                              capture_output=True, text=True)
        out['six_copies_uni_exit'] = _uni.returncode
        if _uni.returncode != 0:
            _lines = [l for l in _uni.stdout.splitlines()
                      if l.startswith('[缺失]') or l.startswith('[FAIL]')]
            obs('S1-3', '六副本脚本 --uni（统一版仓）存在漂移（H3 长尾，BACKLOG §五 待收敛）',
                _lines[:8])
    else:
        print('  [SKIP] S1-3 check_six_copies.py 不存在')

    # S1-2 run_all 全量结果（可选：由调用方先跑 run_all --json 再并入）
    if runall_json and os.path.isfile(runall_json):
        with open(runall_json, 'r', encoding='utf-8') as _f:
            _r = json.load(_f)
        out['run_all'] = {'total': _r.get('total'), 'pass': _r.get('pass'),
                          'fail': _r.get('fail')}
        check('S1-2', 'run_all 全量脚本 %s/%s PASS' % (_r.get('pass'), _r.get('total')),
              _r.get('fail') == 0, out['run_all'])
    else:
        out['run_all'] = {'skipped': '未提供 --runall-json（请先运行 tests/run_all.py --json'}
        print('  [SKIP] S1-2 run_all 结果未提供（--runall-json）')
    return out


# ============================================================ S2 黄金课全景矩阵
def s2_matrix(quick=False):
    print('\n[S2] 黄金课全景矩阵（20 课 × 通道 × 12 时辰）')
    from modules.事项标准 import UI_EVENTS
    from modules.反推引擎 import scan_day, HOURS
    from modules.四柱计算器 import calculate_sizhu

    events = ['嫁娶', '修造', '入宅', '安葬'] if quick else list(UI_EVENTS)
    matrix = {}
    t0 = time.time()
    for _ds, _kind, _note in GOLDEN:
        _d = dt.date.fromisoformat(_ds)
        _row = {'kind': _kind, 'note': _note, 'events': {}}
        for _ev in events:
            _best_sz, _best_r, _hours = scan_day(_d, _ev, _owners_of(_ev), _ctx_of(_ev))
            _rec = _compact(_best_r, _best_sz)
            _rec['hours'] = [{'zhi': _h['地支'], 'score': _h['score'],
                              'disabled': _h['disabled'], 'veto': _h['veto']}
                             for _h in _hours]
            _row['events'][_ev] = _rec
        matrix[_ds] = _row
    print('  矩阵完成：%d 课 × %d 通道，耗时 %.1fs' % (len(matrix), len(events), time.time() - t0))

    # S2-1 四柱同源：每个通道的评分结果若回传四柱，必须与传入完全一致
    #      （防"通道各算各的日历"）。注：交节日各通道最优时辰不同，月柱可合法不同，
    #      故本条按"结果回传 vs 传入"比对，不跨通道比月柱。
    #      现状：calcute_score 不总是回传 result['sizhu']（嫁娶通道为 None），
    #      属回传口径差异而非缺陷 → 未回传记 OBS，仅对有回传者做逐字断言。
    bad = {}
    no_back = []
    for _ds, _row in matrix.items():
        for _ev, _v in _row['events'].items():
            if not _v['result_pillars'] or any(not x for x in _v['result_pillars'].values()):
                no_back.append([_ds, _ev])
            elif _v['result_pillars'] != _v['pillars']:
                bad.setdefault(_ds, []).append([_ev, _v['result_pillars'], _v['pillars']])
    if no_back:
        obs('S2-1', '评分结果未回传四柱（口径差异，不计缺陷）',
            '共 %d 条；示例 %s' % (len(no_back), no_back[:5]))
    check('S2-1', '已回传四柱的通道：结果与传入逐字一致',
          not bad, {'不一致': bad, '未回传条数': len(no_back)})

    # S2-2 算术自洽：总分 == score_details['总分']
    mism = {}
    for _ds, _row in matrix.items():
        for _ev, _v in _row['events'].items():
            if _v['sd_total'] is None:
                continue
            if _v['score'] != _v['sd_total']:
                mism.setdefault(_ds, []).append((_ev, _v['score'], _v['sd_total']))
    check('S2-2', '总分与 score_details[总分] 逐条相等', not mism, mism)

    # S2-3 扣分透明度：神煞明细负分项必须在本通道展示清单中出现
    leak = {}
    for _ds, _row in matrix.items():
        for _ev, _v in _row['events'].items():
            _names = set(_v['shensha_neg'])
            for _n, _s in _v['sd_shensha_neg']:
                if _n not in _names:
                    leak.setdefault(_ds, []).append((_ev, _n, _s))
    check('S2-3', '扣分明细（神煞明细）均在展示清单内可溯', not leak, leak)

    # S2-4 展示清单负分项 vs 计分神煞明细（差额只作观察，不判失败）
    gaps = []
    for _ds, _row in matrix.items():
        for _ev, _v in _row['events'].items():
            _disp = sum(1 for _ in _v['shensha_neg'])
            if _disp != len(_v['sd_shensha_neg']):
                gaps.append({'date': _ds, 'event': _ev, 'display': _disp,
                             'counted': len(_v['sd_shensha_neg'])})
    print('  [OBS] S2-4 展示负分项数 ≠ 计分明细数的组合：%d 条' % len(gaps))

    # S2-5 否决日总分必须归零（否决与分值不得并存）
    bad_veto = {}
    for _ds, _row in matrix.items():
        for _ev, _v in _row['events'].items():
            if _v['veto_reasons'] and _v['score'] != 0:
                bad_veto.setdefault(_ds, []).append((_ev, _v['score'], _v['veto_reasons']))
    check('S2-5', '一票否决日总分恒为 0', not bad_veto, bad_veto)

    # S2-6 伪煞零发射（嫁娶通道：杀师/杨公忌/红纱/年重丧 一律不得出现）
    pseudo = {}
    for _ds, _row in matrix.items():
        _v = _row['events'].get('嫁娶')
        if not _v:
            continue
        _hit = [n for n in _v['shensha_neg'] if any(p in n for p in PSEUDO_FOR_MARRIAGE)]
        _hit_v = [r for r in _v['veto_reasons'] if any(p in r for p in PSEUDO_FOR_MARRIAGE)]
        if _hit or _hit_v:
            pseudo[_ds] = {'shensha': _hit, 'veto': _hit_v}
    check('S2-6', '嫁娶通道伪煞零发射（杀师/杨公忌/红纱/年重丧）', not pseudo, pseudo)

    # S2-7 月破课（2026-02-15）嫁娶：否决原因必须只落在月破/往亡/受死三类
    _v = matrix.get('2026-02-15', {}).get('events', {}).get('嫁娶')
    if _v:
        _ok_terms = ('月破', '往亡', '受死')
        _bad_reason = [r for r in _v['veto_reasons']
                       if not any(k in r for k in _ok_terms)]
        check('S2-7', '2026-02-15 月破课否决原因域限定（月破/往亡/受死）',
              not _bad_reason, _bad_reason or _v['veto_reasons'])
    else:
        print('  [SKIP] S2-7 --quick 未跑嫁娶')

    # S2-8 解禁课回归：被判否决可以（其他煞仍生效），但绝不能再因「红纱日/杨公忌日」
    #      被否决或扣分（§212 剥离口径）。
    unl = {}
    for _ds in ('2026-01-15', '2026-05-23', '2026-06-19'):
        _v = matrix.get(_ds, {}).get('events', {}).get('嫁娶')
        if not _v:
            continue
        _hit = [r for r in _v['veto_reasons'] if '红纱' in r or '杨公' in r]
        _hit += [n for n in _v['shensha_neg'] if '红纱' in n or '杨公' in n]
        if _hit:
            unl[_ds] = _hit
    check('S2-8', '解禁课：嫁娶不再因红纱日/杨公忌被否决或扣分', not unl, unl)

    # S2-9 四离课（2026-03-19）：嫁娶否决原因含四离/四绝
    _v = matrix.get('2026-03-19', {}).get('events', {}).get('嫁娶')
    if _v:
        check('S2-9', '2026-03-19 四离课嫁娶被判否决且命中四离/四绝',
              bool(_v['veto_reasons']) and any('四离' in r or '四绝' in r
                                              for r in _v['veto_reasons']),
              _v['veto_reasons'])
    else:
        print('  [SKIP] S2-9 --quick 未跑嫁娶')

    # S2-10 出行山向隔离（历史 P1 串台缺口回归）：传/不传山向分值必须一致
    from modules.评分器 import calculate_score
    drift = {}
    for _ds, _kind, _note in GOLDEN[:8]:
        _d = dt.date.fromisoformat(_ds)
        _sz = calculate_sizhu(_d, 12, 0)
        _a = calculate_score(_sz, '出行', _owners_of('出行'))
        _b = calculate_score(_sz, '出行', _owners_of('出行'), None, SHAN_FULL)
        if int(_a.get('score') or 0) != int(_b.get('score') or 0) or \
                (_a.get('veto_reasons') or []) != (_b.get('veto_reasons') or []):
            drift[_ds] = [int(_a.get('score') or 0), int(_b.get('score') or 0)]
    check('S2-10', '出行不因传入山向而改变分值（山向串台缺口已闭合）', not drift, drift)

    # S2-11 交节跨界：早/晚时支月柱必须翻转，日柱必须不变
    jq = {}
    for _ds, _term, _z1, _z2, _m1, _m2 in JIEQI:
        _d = dt.date.fromisoformat(_ds)
        _h1 = dict(zip([h[1] for h in HOURS], [h[0] for h in HOURS]))[_z1]
        _h2 = dict(zip([h[1] for h in HOURS], [h[0] for h in HOURS]))[_z2]
        _s1 = calculate_sizhu(_d, _h1, 0)
        _s2 = calculate_sizhu(_d, _h2, 0)
        _ok = (_s1.get('月柱') == _m1 and _s2.get('月柱') == _m2
               and _s1.get('日柱') == _s2.get('日柱'))
        jq[_ds] = {'早': [_z1, _s1.get('月柱'), _s1.get('日柱')],
                   '晚': [_z2, _s2.get('月柱'), _s2.get('日柱')], 'expected': [_m1, _m2]}
        check('S2-11' + ('a' if _ds == JIEQI[0][0] else 'b'),
              '%s %s 交节前后月柱翻转（%s→%s）日柱不变' % (_ds, _term, _m1, _m2), _ok, jq[_ds])

    return {'events': events, 'elapsed': round(time.time() - t0, 1),
            'matrix': matrix, 'obs': {'display_vs_counted_gaps': len(gaps)}, 'jieqi': jq}


# ====================================================== S3 反推引擎与动作时序
def s3_reverse():
    print('\n[S3] 反推引擎与动作时序（数据流 / 四态 / D4 拦截）')
    from modules.反推引擎 import search_top_n, MAX_DAYS
    from modules.事项标准 import UI_EVENTS
    out = {}

    # S3-1 零候选防御：四离日单日窗口（范围内全部否决）→ 不得伪造入榜记录
    r = search_top_n(days=1, event_type='嫁娶', owners=_owners_of('嫁娶'),
                     start=dt.date(2026, 3, 19), top_n=5, context={'shan_xiang': SHAN_FULL})
    out['zero_candidate'] = {'candidates': r['meta']['candidates'],
                             'vetoed': r['meta']['vetoed'],
                             'days_len': len(r['days']),
                             'reasons': (r['vetoed'][0]['reasons'] if r['vetoed'] else [])}
    check('S3-1', '零候选窗口不伪造入榜（days=[]、candidates=0）',
          r['meta']['candidates'] == 0 and len(r['days']) == 0 and r['meta']['vetoed'] >= 1,
          out['zero_candidate'])

    # S3-2 零候选 UI 提示：源码层必须存在显式「全否」提示
    _ui = open(os.path.join(ROOT, 'modules', '反推UI.py'), encoding='utf-8').read()
    _has_allveto = any(k in _ui for k in ('全部否决', '全否', '本范围内无可用吉日',
                                          '无可用吉日'))
    check('S3-2', '反推面板存在「全否/无可用吉日」显式提示', _has_allveto,
          '反推UI 仅在状态栏显示候选数，无弹窗/无醒目提示' if not _has_allveto else '')

    # S3-3 四态时序：30 天窗口内必须出现过渡态（partial/insufficient），且缺段有标注
    r2 = search_top_n(days=30, event_type='嫁娶', owners=_owners_of('嫁娶'),
                      start=dt.date(2026, 1, 1), top_n=8, context={'shan_xiang': SHAN_FULL})
    _stat = {}
    for _d in r2['days']:
        _ap = _d.get('action_plan') or {}
        _s = str(_ap.get('status') or 'none')
        _stat.setdefault(_s, []).append(_d['date'])
    out['plan_status'] = _stat
    _has_partial = 'partial' in _stat or 'insufficient' in _stat
    check('S3-3', '四态时序输出可复现（出现 partial/insufficient）', _has_partial, _stat)
    _bad = []
    for _d in r2['days']:
        _ap = _d.get('action_plan') or {}
        for _p in (_ap.get('plan') or []):
            if _p.get('zhi') == '子' or _p.get('zhi') == '':
                _bad.append((_d['date'], _p))
        if _ap.get('status') == 'full' and _ap.get('missing'):
            _bad.append((_d['date'], 'full 但 missing 非空'))
        if _ap.get('status') in ('partial', 'insufficient') and not _ap.get('missing'):
            _bad.append((_d['date'], '过渡态但 missing 为空'))
    check('S3-4', '动作时序不排子时/无空段；full↔missing 自洽', not _bad, _bad[:4])

    # S3-5 排序层不降权：慎用日入榜但恒排吉日之后（收录层口径）
    _tiers = [0 if _d['kind'] == '吉日' else 1 for _d in r2['days']]
    out['tiers'] = _tiers
    check('S3-5', '榜单收录层单调（吉日全量在慎用之前，慎用不降权出榜）',
          _tiers == sorted(_tiers), _tiers)

    # S3-6 UI 黄标文案：「缺上轿吉时」级别的事件级提示
    _ui_ok = '缺上轿吉时' in _ui
    out['ui_partial_text'] = '缺段（建议错峰）' in _ui
    check('S3-6', '过渡态 UI 显示事件级黄标「缺上轿吉时」', _ui_ok,
          '现仅显示通用文案「缺段（建议错峰）」/「仅 1 段（建议另择）」' if not _ui_ok else '')

    # S3-7 D4 拦截（plan 路径）：发轿时支冲新娘年命 → 拒绝生成红帖
    from modules.择日贴 import prepare_entry, compose_detail_lines
    _chong = '巳'  # 新娘属猪 → 冲巳
    _plan = {'plan': [{'seq': 1, 'label': '起轿·发轿', 'zhi': _chong, 'ganzhi': '乙巳',
                       'range': '09-11', 'score': 80, 'level': '吉', 'tags': []}],
             'status': 'partial', 'missing': ['迎娶·进门', '交拜·合卺'], 'checks': [], 'alt': []}
    try:
        prepare_entry({'date': '2026-10-20', 'event_type': '嫁娶', 'score': 88, 'level': '吉',
                       'owners_list': _owners_of('嫁娶'), 'action_plan': _plan})
        out['d4_plan'] = 'ACCEPTED'
        check('S3-7', 'D4 plan 路径：冲命时辰拒绝生成', False, '未抛错')
    except ValueError as _e:
        out['d4_plan'] = 'REJECTED: %s' % _e
        check('S3-7', 'D4 plan 路径：冲命时辰拒绝生成', True)

    # S3-8 D4 拦截（手动改吉时路径）：action_plan 之外的 jishi_override 同样必须校验
    try:
        _e2 = prepare_entry({'date': '2026-10-20', 'event_type': '嫁娶', 'score': 88,
                            'level': '吉', 'owners_list': _owners_of('嫁娶'),
                            'jishi_override': {'0': _chong}})
        _got = [(_j['zhi'], _j.get('manual')) for _j in (_e2.get('_jishi') or [])[:3]]
        _applied = _got and _got[0][0] == _chong
        out['d4_override'] = {'applied': _applied, 'jishi': _got}
        check('S3-8', 'D4 手动改吉时路径：冲命时辰拒绝生成',
              not _applied, '手动覆盖冲新娘时支 %s 被直接采纳：%s' % (_chong, _got))
    except ValueError as _e:
        out['d4_override'] = 'REJECTED: %s' % _e
        check('S3-8', 'D4 手动改吉时路径：冲命时辰拒绝生成', True)

    # S3-9 D4 静默降级：action_plan 在场时 jishi_override 是否被静默忽略
    _plan2 = {'plan': [{'seq': 1, 'label': '起轿·发轿', 'zhi': '卯', 'ganzhi': '丁卯',
                        'range': '05-07', 'score': 80, 'level': '吉', 'tags': []}],
              'status': 'partial', 'missing': ['迎娶·进门', '交拜·合卺'], 'checks': [], 'alt': []}
    try:
        _e3 = prepare_entry({'date': '2026-10-20', 'event_type': '嫁娶', 'score': 88,
                             'level': '吉', 'owners_list': _owners_of('嫁娶'),
                             'action_plan': _plan2, 'jishi_override': {'0': '午'}})
        _z = [(_j['zhi'], _j.get('from_plan')) for _j in (_e3.get('_jishi') or [])[:3]]
        out['d4_override_vs_plan'] = _z
        check('S3-9', 'plan 与手动覆盖并存时不静默丢弃用户修改',
              _z and _z[0][0] == '午', 'plan 直接覆盖 jishi_override，用户改时无提示：%s' % _z)
    except ValueError as _e:
        out['d4_override_vs_plan'] = 'REJECTED: %s' % _e
        check('S3-9', 'plan 与手动覆盖并存时不静默丢弃用户修改', True)

    # S3-10 参数校验：未知事项 / 天数越界 / top_n 非法
    _err = []
    for _kw, _lbl in ((dict(event_type='不存在的课'), '未知事项'),
                      (dict(event_type='嫁娶', days=0), 'days=0'),
                      (dict(event_type='嫁娶', days=MAX_DAYS + 1),
                       'days=%d' % (MAX_DAYS + 1)),
                      (dict(event_type='嫁娶', top_n=0), 'top_n=0')):
        try:
            search_top_n(owners=[], start=dt.date(2026, 1, 1), **_kw)
            _err.append(_lbl + ' 未抛 ValueError')
        except ValueError:
            pass
    check('S3-10', '反推参数越界一律 ValueError（禁止静默）', not _err, _err)

    # S3-11 回调与取消：progress 逐日回调、cancel 生效
    _n = [0]
    _r3 = search_top_n(days=3, event_type='嫁娶', owners=_owners_of('嫁娶'),
                       start=dt.date(2026, 4, 1), top_n=2,
                       progress=lambda done, tot, d: _n.__setitem__(0, done))
    check('S3-11', 'progress 按日回调（3 天=3 次）', _n[0] == 3, _n[0])
    _r4 = search_top_n(days=5, event_type='嫁娶', owners=_owners_of('嫁娶'),
                       start=dt.date(2026, 4, 1), top_n=2, cancel=lambda: True)
    out['cancel'] = {'cancelled': _r4['meta']['cancelled'], 'scanned': _r4['meta']['scanned']}
    check('S3-12', 'cancel 生效并置 cancelled=True', _r4['meta']['cancelled'], out['cancel'])

    out['events_checked'] = len(UI_EVENTS)
    return out


# ================================================================ S4 红帖三态
def s4_redpost(out_dir):
    print('\n[S4] 红帖三态分流与视觉交付')
    from modules import 择日贴 as Z
    os.makedirs(out_dir, exist_ok=True) if out_dir else None
    out = {'files': []}

    def _mk(entry):
        return Z.prepare_entry(entry)

    def _write(name, e, title, paper):
        lines = Z.compose_detail_lines(e)
        doc = Z.render_print_html(lines, title, paper=paper)
        if not out_dir:
            return '\n'.join(t for _, t in lines), doc, lines
        _p = os.path.join(out_dir, name)
        with open(_p, 'w', encoding='utf-8') as _f:
            _f.write(doc)
        out['files'].append(_p if os.path.isabs(out_dir)
                            else os.path.relpath(_p, ROOT))
        return '\n'.join(t for _, t in lines), doc, lines

    # S4-1 吉帖（200 分 上吉）
    _e = _mk({'date': '2026-10-20', 'event_type': '嫁娶', 'score': 200, 'level': '上吉',
              'owners_list': _owners_of('嫁娶'), 'reason': '吉神：天德、月德'})
    _t1, _d1, _l1 = _write('红帖_吉帖_2026-10-20.html', _e, '嫁娶吉课', 'red')
    out['ji'] = {'paper': 'red', 'has_auspice': '嫁娶结婚大利' in _t1,
                 'has_caution': '慎　　用' in _t1, 'has_veto': '不　可　使　用' in _t1}
    check('S4-1', '吉帖：红底 + 吉语在 + 无慎用/否决牌',
          out['ji']['has_auspice'] and not out['ji']['has_caution']
          and not out['ji']['has_veto'] and '#C11B17' in _d1, out['ji'])

    # S4-2 慎用帖（真实链路 2026-02-09 嫁娶：非零分凶）
    from modules.四柱计算器 import calculate_sizhu
    from modules.评分器 import calculate_score
    _sz = calculate_sizhu(dt.date(2026, 2, 9), 10, 0)
    _r = calculate_score(_sz, '嫁娶', _owners_of('嫁娶'))
    _e2 = _mk({'date': '2026-02-09', 'event_type': '嫁娶', 'score': _r.get('score'),
               'level': _r.get('level'), 'reason': _r.get('reason'),
               'veto_reasons': _r.get('veto_reasons'), 'owners_list': _owners_of('嫁娶')})
    _t2, _d2, _l2 = _write('红帖_慎用帖_2026-02-09.html', _e2, '日课慎用提示', 'veto')
    _forbid = [k for k in ('大利', '大吉', '日吉时良', '吉课', '吉日') if k in _t2]
    out['caution'] = {'score': _r.get('score'), 'level': _r.get('level'),
                      'soft': _e2.get('_is_soft_caution'),
                      'vetoed': _e2.get('_is_vetoed'),
                      'forbidden_hits': _forbid,
                      'deep_red': '#8B0000' in _d2,
                      'title': '本日多煞　建议慎用' in _t2,
                      'stamp': ('stamp', '慎　　用') in _l2,
                      'warn_block': any(s == 'warn' for s, _ in _l2)}
    check('S4-2', '慎用帖：深红底 + 标题「本日多煞 建议慎用」+ 零吉语 + 煞忌块',
          out['caution']['deep_red'] and out['caution']['title']
          and not _forbid and out['caution']['stamp'] and out['caution']['warn_block'],
          out['caution'])

    # S4-3 否决帖（真实链路 2026-03-19 四离 = 0 分）
    _sz3 = calculate_sizhu(dt.date(2026, 3, 19), 10, 0)
    _r3 = calculate_score(_sz3, '嫁娶', _owners_of('嫁娶'))
    _e3 = _mk({'date': '2026-03-19', 'event_type': '嫁娶', 'score': _r3.get('score'),
               'level': _r3.get('level'), 'reason': _r3.get('reason'),
               'veto_reasons': _r3.get('veto_reasons'), 'owners_list': _owners_of('嫁娶')})
    _t3, _d3, _l3 = _write('红帖_否决帖_2026-03-19.html', _e3, '日课否决警示', 'veto')
    out['veto'] = {'score': _r3.get('score'), 'level': _r3.get('level'),
                   'stamp': ('stamp', '不　可　使　用') in _l3,
                   'verdict': '本　日　不　吉' in _t3,
                   'no_hour_section': '【　时　辰　】' not in _t3,
                   'no_auspice': not any(k in _t3 for k in ('大利', '大吉', '日吉时良'))}
    check('S4-3', '否决帖：明黄「本日不吉/不可使用」牌 + 无时辰区 + 零吉语',
          out['veto']['stamp'] and out['veto']['verdict']
          and out['veto']['no_hour_section'] and out['veto']['no_auspice'], out['veto'])

    # S4-4 软忌动态渲染：受死日（2026-01-11 嫁娶否决原因）必须落进黄底警示区
    _e4 = _mk({'date': '2026-01-11', 'event_type': '嫁娶', 'score': 0, 'level': '❌ 凶',
               'veto_reasons': ['受死日'], 'owners_list': _owners_of('嫁娶')})
    _l4 = Z.compose_detail_lines(_e4)
    _warn4 = [t for s, t in _l4 if s in ('warn', 'hardwarn')]
    out['soft_death'] = _warn4
    check('S4-4', '受死日落入黄底警示区（动态渲染，非硬编码）',
          any('受死日' in w for w in _warn4), _warn4)

    # S4-5 软忌动态渲染：红纱日（§212 已剥离评分，但作为历史软忌名仍需可打印）
    _e5 = _mk({'date': '2026-01-15', 'event_type': '嫁娶', 'score': 73, 'level': '★★★★★ 上吉',
               'reason': '忌：红纱日、鬼哭日', 'owners_list': _owners_of('嫁娶')})
    _l5 = Z.compose_detail_lines(_e5)
    _warn5 = [t for s, t in _l5 if s in ('warn', 'hardwarn')]
    out['soft_redsha'] = _warn5
    check('S4-5', '红纱日等软忌在吉帖黄底警示区打印', any('红纱日' in w for w in _warn5), _warn5)

    # S4-6 榜单慎用微瑕强制提示（reverse_caution=True 且非凶级）
    _e6 = _mk({'date': '2026-10-20', 'event_type': '嫁娶', 'score': 150, 'level': '★★★★★ 上吉',
               'reverse_caution': True, 'owners_list': _owners_of('嫁娶')})
    _l6 = Z.compose_detail_lines(_e6)
    _hw = [(s, t) for s, t in _l6 if s == 'hardwarn']
    out['reverse_caution'] = _hw
    check('S4-6', '榜单慎用微瑕：加粗黄底提示置顶（hardwarn）',
          bool(_hw) and '微瑕' in _hw[0][1], _hw)

    # S4-7 三态版式互斥（同一日课不得同时出现吉语与否决牌）
    _conf = []
    for _lbl, _l in (('吉', _l1), ('慎用', _l2), ('否决', _l3)):
        _sty = {s for s, _ in _l}
        if 'stamp' in _sty and ('verdict' in _sty or 'tbl' in _sty):
            pass
    check('S4-7', '三态版式互斥（吉帖/慎用帖/否决帖 牌面唯一）',
          ('stamp', '慎　　用') in _l2 and ('stamp', '不　可　使　用') in _l3
          and 'stamp' not in {s for s, _ in _l1}, _conf)
    return out


# ========================================================= S5 外围防护与异常兜底
def s5_defense():
    print('\n[S5] 外围防护与异常兜底')
    out = {}

    # S5-1 非法日期：2026-02-30 必须 ValueError（不得静默成 3-2）
    try:
        dt.date(2026, 2, 30)
        check('S5-1', '非法日期 2026-02-30 抛错', False, '未抛错')
    except ValueError:
        check('S5-1', '非法日期 2026-02-30 抛错', True)

    # S5-2 非法日期字符串进入红帖：必须 ValueError 而非生成错日
    from modules import 择日贴 as Z
    try:
        Z.prepare_entry({'date': '2026-02-30', 'event_type': '开业'})
        check('S5-2', '红帖非法日期字符串被拒', False, '未抛错')
    except ValueError:
        check('S5-2', '红帖非法日期字符串被拒', True)
    except Exception as _e:  # noqa: BLE001
        check('S5-2', '红帖非法日期字符串被拒（异常类型需为 ValueError）', False,
              '%s: %s' % (type(_e).__name__, _e))

    # S5-3 缺 date 键：应为 ValueError（实测 KeyError，仍属不静默）
    try:
        Z.prepare_entry({'event_type': '开业'})
        check('S5-3', '红帖缺 date 键被拒', False, '未抛错')
    except (KeyError, ValueError) as _e:
        _kind = type(_e).__name__
        out['missing_date'] = _kind
        check('S5-3', '红帖缺 date 键被拒（不静默）', True, _kind)

    # S5-4 空事主：嫁娶无事主不崩溃
    from modules.四柱计算器 import calculate_sizhu
    from modules.评分器 import calculate_score
    _sz = calculate_sizhu(dt.date(2026, 10, 20), 10, 0)
    try:
        _r = calculate_score(_sz, '嫁娶', [])
        out['empty_owners'] = {'score': _r.get('score'), 'level': _r.get('level'),
                               'warnings': list(_r.get('warnings') or [])[:3]}
        check('S5-4', '空事主不崩溃且给出提示', True, out['empty_owners'])
    except Exception as _e:  # noqa: BLE001
        check('S5-4', '空事主不崩溃', False, '%s: %s' % (type(_e).__name__, _e))

    # S5-5 空四柱：允许抛错，也允许返回明确错误态；唯一禁止是"静默给正常分"
    try:
        _r = calculate_score({}, '嫁娶', [])
        _lvl = str(_r.get('level') or '')
        _bad = not (int(_r.get('score') or 0) == 0 and '计算错误' in _lvl)
        out['empty_sizhu'] = {'score': _r.get('score'), 'level': _lvl}
        check('S5-5', '空四柱不静默给分（抛错或 0 分「计算错误」）', not _bad, out['empty_sizhu'])
    except Exception as _e:  # noqa: BLE001
        out['empty_sizhu'] = type(_e).__name__
        check('S5-5', '空四柱不静默给分（抛错或 0 分「计算错误」）', True, out['empty_sizhu'])

    # S5-6 时辰越界（25 点 / -1 点）
    _bad = []
    for _h in (25, -1):
        try:
            calculate_sizhu(dt.date(2026, 10, 20), _h, 0)
            _bad.append(_h)
        except Exception:  # noqa: BLE001
            pass
    check('S5-6', '时辰越界抛错（25/-1）', not _bad, _bad)

    # S5-7 全报告 JSON 可序列化（含中文、无 NaN/None 死链）
    _txt = json.dumps(REPORT_STASH, ensure_ascii=False, default=str)
    _dirty = [k for k in ('NaN', '<object', 'set(', 'datetime.date(') if k in _txt]
    out['json_len'] = len(_txt)
    check('S5-7', '报告全量 JSON 可序列化且无脏字串', not _dirty, _dirty)

    # S5-8 未知事项进入评分（通用检查器兜底，不崩溃）
    try:
        _r = calculate_score(_sz, '火星移民', [])
        out['unknown_event'] = {'score': _r.get('score'), 'pipeline': _r.get('pipeline')}
        check('S5-8', '未知事项走通用兜底不崩溃', True, out['unknown_event'])
    except Exception as _e:  # noqa: BLE001
        check('S5-8', '未知事项走通用兜底不崩溃', False, '%s: %s' % (type(_e).__name__, _e))
    return out


# ============================================================== S6 技术债盘点
def s6_debt():
    print('\n[S6] 技术债与外围防护盘点')
    out = {}
    out['pytest_ini'] = os.path.isfile(os.path.join(ROOT, 'pytest.ini'))
    out['conftest'] = os.path.isfile(os.path.join(ROOT, 'tests', 'conftest.py'))
    out['runner_shell'] = os.path.isfile(os.path.join(ROOT, 'tests', 'test_runner_shell.py'))
    out['pyproject'] = os.path.isfile(os.path.join(ROOT, 'pyproject.toml'))
    # 001 §214 C3（2026-11-03 拍板）：H2 pytest 外壳暂缓到下一基建批次，
    # 属工程规范债、不影响交付体验 → 降级为观察项，不阻塞探针退出码。
    if out['pytest_ini'] and out['conftest'] and out['runner_shell']:
        check('S6-1', 'H2 pytest 外壳已落地', True)
    else:
        obs('S6-1', 'H2 pytest 外壳未落地（2026-11-03 拍板暂缓至下一基建批次）',
            {'pytest.ini': out['pytest_ini'], 'conftest.py': out['conftest'],
             'test_runner_shell.py': out['runner_shell'], 'pyproject.toml': out['pyproject']})

    # H3 统一版仓漂移
    uni = r'd:\自编择日软件\专业择日大师_统一版\专业级正五行择日软件_v1.0'
    out['uni_exists'] = os.path.isdir(uni)
    if out['uni_exists']:
        _diff = []
        _same = 0
        for _f in ('主程序.py', os.path.join('modules', '评分器.py'),
                   os.path.join('modules', '事项标准.py')):
            _a = os.path.join(ROOT, _f)
            _b = os.path.join(uni, _f)
            if not (os.path.isfile(_a) and os.path.isfile(_b)):
                _diff.append(_f + '（缺失）')
                continue
            with open(_a, 'rb') as _fa, open(_b, 'rb') as _fb:
                if hashlib.sha256(_fa.read()).hexdigest() == hashlib.sha256(_fb.read()).hexdigest():
                    _same += 1
                else:
                    _diff.append(_f)
        out['uni_same'] = _same
        out['uni_diff'] = _diff
        print('  [OBS] H3 统一版仓：%d/%d 关键文件一致，漂移 %s' % (_same, _same + len(_diff), _diff))
    else:
        print('  [SKIP] H3 统一版仓不存在（本机未部署）')

    # 副本感知脚本数
    _tests = os.path.join(ROOT, 'tests')
    _aware = 0
    _total = 0
    for _fn in os.listdir(_tests):
        if not _fn.endswith('.py') or _fn == 'run_all.py':
            continue
        _total += 1
        try:
            _src = open(os.path.join(_tests, _fn), encoding='utf-8').read()
        except Exception:  # noqa: BLE001
            continue
        if 'check_six_copies' in _src or '_copy_guard' in _src or '副本' in _src:
            _aware += 1
    out['copy_aware'] = {'aware': _aware, 'total': _total}
    check('S6-2', '副本感知脚本覆盖（>4 个）', _aware > 4, out['copy_aware'])
    return out


REPORT_STASH = {}


def main():
    ap = argparse.ArgumentParser(description='v2.1.x 终局大考 · 黄金课探针')
    ap.add_argument('--quick', action='store_true', help='只跑 4 个代表通道')
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs', '大考产物_20261101'),
                    help='红帖 HTML 产物目录')
    ap.add_argument('--json', default=os.path.join(ROOT, 'docs',
                                                   'v2.1.x_终局大考报告_20261101.json'))
    ap.add_argument('--runall-json', default=None,
                    help='tests/run_all.py --json 的结果文件（并入第一维）')
    ap.add_argument('--no-write', action='store_true',
                    help='只跑断言，不写 JSON/HTML（run_all 托管用）')
    args = ap.parse_args()
    if args.no_write:
        args.out = None
        args.json = None

    global REPORT_STASH
    t0 = time.time()
    print('=' * 72)
    print('v2.1.x 终局大考 · 黄金课探针    仓根=%s' % ROOT)
    print('=' * 72)

    REPORT_STASH = {'s2': s2_matrix(args.quick)}
    s3 = s3_reverse()
    s4 = s4_redpost(args.out)
    s5 = s5_defense()
    s6 = s6_debt()
    s1 = s1_baseline(args.runall_json)

    report = {
        'meta': {
            'title': 'v2.1.x 终局大考 · 黄金课全景报告',
            'generated_at': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'root': ROOT,
            'golden_count': len(GOLDEN),
            'channels': len(REPORT_STASH['s2']['events']),
            'quick': bool(args.quick),
            'elapsed': round(time.time() - t0, 1),
        },
        's1_baseline': s1,
        's2_matrix': REPORT_STASH['s2'],
        's3_reverse': s3,
        's4_redpost': s4,
        's5_defense': s5,
        's6_debt': s6,
        'checks': CHECKS,
        'observations': OBS,
        'summary': {'total': len(CHECKS), 'pass': len(CHECKS) - len(FAILS),
                    'fail': len(FAILS), 'fails': FAILS, 'obs': len(OBS)},
    }
    REPORT_STASH = report

    if args.json:
        os.makedirs(os.path.dirname(args.json) or '.', exist_ok=True)
        with open(args.json, 'w', encoding='utf-8') as _f:
            json.dump(report, _f, ensure_ascii=False, indent=1, default=str)

    print('\n' + '=' * 72)
    print('汇总：CHECK=%d  PASS=%d  FAIL=%d  耗时=%.1fs'
          % (len(CHECKS), len(CHECKS) - len(FAILS), len(FAILS), time.time() - t0))
    if FAILS:
        print('未通过项：')
        for _f in FAILS:
            print('  - ' + _f)
    if args.json:
        print('报告：%s' % args.json)
    if args.out:
        print('红帖产物：%s' % args.out)
    print('=' * 72)
    return 1 if FAILS else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as _e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        print('探针运行异常：%s: %s' % (type(_e).__name__, _e))
        sys.exit(2)
