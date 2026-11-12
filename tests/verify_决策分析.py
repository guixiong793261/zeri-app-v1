# -*- coding: utf-8 -*-
"""专家决策分析面板验证（001 §238.12，tests/verify_决策分析.py）。

A 段（合成，零扫描）：三场景分类断言（veto/warn/ok）、鲁班煞提示级回归
    （001 §272 续：-5 提示，不再黄牌）、偏枯建议文案、纯度断言
    （build_decision_report 不变异入参）、明细折叠。
B 段（真实链路）：2023-01-12 庚午日嫁娶（owners_0111_g85.json 夹具，
    基线确认一票否决）→ verdict_key == 'veto' 且事主列非空；
    2026 年 1 月嫁娶有限扫描（≤8 天）找首个非否决日，断言报告结构完整。

用法：python tests/verify_决策分析.py
退出码：0=全过  1=有失败（CI 可挂）
"""
import sys
import copy
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests' / 'fixtures'))

from modules.决策分析 import build_decision_report, _tail_items  # noqa: E402
from modules.评分器 import calculate_score  # noqa: E402
from verify_fixtures import _load_owners, _sizhu  # noqa: E402

PASS = 0
FAIL = 0


def check(name, cond, extra=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print('✅ %s' % name)
    else:
        FAIL += 1
        print('❌ %s  %s' % (name, extra))


def main():
    print('=' * 78)
    print('专家决策分析面板验证（001 §238.12）')
    print('=' * 78)

    # ── A 段：合成场景（三档分类 + 建议文案 + 纯度）─────────────────────
    print('【A 段】合成场景分类与纯度')
    # A1 一票否决（冲命=事主类；三煞=山家类）
    r_veto = {
        'score': 0, 'level': '❌凶',
        'veto_reasons': ['日支"申"冲新郎年命"寅"（一票否决）',
                         '犯年三煞，山家封禁（一票否决）'],
        'shensha_list': [], 'xiangzhu_notes': [],
    }
    rep = build_decision_report(r_veto, '嫁娶')
    check('A1 否决日裁决为 veto', rep['verdict_key'] == 'veto')
    check('A1 否决文案含「绝对不可用」', '绝对不可用' in rep['verdict'])
    check('A1 冲命归入事主列', any('新郎' in t for _, t in rep['owner_items']),
          str(rep['owner_items']))
    check('A1 三煞归入山家列', any('三煞' in t for _, t in rep['shan_items']),
          str(rep['shan_items']))
    check('A1 否决建议含「另择吉日」', '另择吉日' in rep['advice'])

    # A2 鲁班煞高分日（001 §272 续：鲁班煞降为 -5 提示级，不再硬触发黄牌，
    #    合成单日 -10 未达普通档 neg_total<=-20 阈值）→ ok，且无鲁班专属建议
    r_luban = {
        'score': 96, 'level': '★★★★ 吉',
        'veto_reasons': [],
        'heavy_sha_warning': '鲁班煞',
        'heavy_sha_names': ['鲁班煞'],
        'wuxing_pian_ku': None,
        'shensha_list': [{'name': '鲁班煞', 'score': -10}],
        'xiangzhu_notes': [],
    }
    rep2 = build_decision_report(r_luban, '修造')
    check('A2 鲁班煞提示级不再黄牌（裁决为 ok）', rep2['verdict_key'] == 'ok',
          rep2['verdict_key'])
    check('A2 建议不再含「鲁班煞」专属文案',
          '鲁班煞' not in rep2['advice'], rep2['advice'])

    # A3 偏枯过燥 → warn + 金水时辰建议
    r_pk = {'score': 80, 'level': '★★★ 中吉', 'veto_reasons': [],
            'wuxing_pian_ku': '过燥', 'shensha_list': [],
            'xiangzhu_notes': []}
    rep3 = build_decision_report(r_pk, '修造')
    check('A3 偏枯裁决为 warn', rep3['verdict_key'] == 'warn')
    check('A3 建议含「金水旺」', '金水旺' in rep3['advice'], rep3['advice'])

    # A4 凶煞负分合计 ≤ -20 → warn
    r_neg = {'score': 70, 'level': '★★ 平', 'veto_reasons': [],
             'shensha_list': [{'name': '甲', 'score': -15},
                              {'name': '乙', 'score': -10}],
             'xiangzhu_notes': []}
    rep4 = build_decision_report(r_neg, '修造')
    check('A4 负分合计-25裁决为 warn', rep4['verdict_key'] == 'warn')

    # A5 完美吉日 → ok
    r_ok = {
        'score': 108, 'level': '★★★★★ 上吉',
        'veto_reasons': [], 'shensha_list': [{'name': '天德', 'score': 20}],
        'xiangzhu_notes': ['与新郎生肖六合：+10分'],
        'sansha_info': {'mountain_jishen': ['太阳到山']},
    }
    rep5 = build_decision_report(r_ok, '嫁娶')
    check('A5 完美吉日裁决为 ok', rep5['verdict_key'] == 'ok')
    check('A5 吉课可用文案', '吉课可用' in rep5['verdict'])
    check('A5 山家吉神入列', any('太阳到山' in t for _, t in rep5['shan_items']))
    check('A5 相主六合入事主列且为吉',
          any(g and '六合' in t for g, t in rep5['owner_items']),
          str(rep5['owner_items']))

    # A5b 001 §273：入宅 300 分 + 向方三煞 → 必须黄牌（修造同数据仍绿灯）
    r_rz = {
        'score': 300, 'level': '★★★★★ 上吉', 'veto_reasons': [],
        'heavy_sha_warning': '', 'heavy_sha_names': [],
        'wuxing_pian_ku': None,
        'shensha_list': [{'name': '月德', 'score': 18}],
        'xiangzhu_notes': [],
        'sansha_info': {'sansha_penalty': -20,
                        'sansha_penalty_detail': ['年三煞(向方)（-10分）',
                                                  '日三煞(向方)（-3分）']},
        'score_details': {'相主得分': 29,
                          '相主详情': ['事主1年命属金（辛亥），与日课相生 +6分']},
    }
    check('A5b 入宅300分向方三煞=黄牌',
          build_decision_report(dict(r_rz), '入宅')['verdict_key'] == 'warn')
    check('A5b 入宅黄牌文案含「向首」',
          '向首' in build_decision_report(dict(r_rz), '入宅')['verdict_reason'])
    check('A5b 修造300分同数据仍绿灯（阶梯豁免不受影响）',
          build_decision_report(dict(r_rz), '修造')['verdict_key'] == 'ok')
    # A5b-2 001 §273：canonical 归并——移徙/搬家/迁居同属入宅，向首三煞同样黄牌
    for _alias in ('移徙', '搬家', '迁居'):
        _rep = build_decision_report(dict(r_rz), _alias)
        check('A5b-2 %s向首三煞=黄牌（canonical归并）' % _alias,
              _rep['verdict_key'] == 'warn', _rep['verdict_key'])
        check('A5b-2 %s黄牌文案含「向首」' % _alias,
              '向首' in _rep['verdict_reason'], _rep['verdict_reason'])
    # A5c 001 §273：相主详情接入「对事主的影响」，修复相主空转
    _it = build_decision_report(dict(r_rz), '入宅')['owner_items']
    check('A5c 相主详情进入事主影响列', len(_it) >= 1, str(_it))
    check('A5c 相主行带分值', all('分' in str(t) for _, t in _it), str(_it))

    # A5d 001 §274：修造/动土 + 事主流年冲太岁 = 命理红线，
    # 绝不被五行高分豁免（1000 分也不放行，必须黄牌）。
    r_ts = {
        'score': 327, 'level': '★★★★★ 上吉', 'veto_reasons': [],
        'heavy_sha_warning': '', 'heavy_sha_names': [],
        'wuxing_pian_ku': None,
        'shensha_list': [{'name': '月德', 'score': 18}],
        'xiangzhu_notes': [],
        'sansha_info': {'sansha_penalty': 0, 'sansha_penalty_detail': []},
        'score_details': {
            '相主得分': -23,
            '相主详情': [
                '[流年冲太岁]贵雄年命亥与流年巳六冲（冲太岁），此年课慎用，-15分',
                '[流年冲太岁]美园年命亥与流年巳六冲（冲太岁），此年课慎用，-8分']},
    }
    rep_ts = build_decision_report(dict(r_ts), '修造')
    check('A5d 修造327分冲太岁=黄牌', rep_ts['verdict_key'] == 'warn',
          rep_ts['verdict_key'])
    check('A5d 裁决头标注「事主流年犯太岁」',
          '犯太岁' in rep_ts.get('verdict_label', ''), rep_ts.get('verdict_label'))
    check('A5d 裁决依据含「冲太岁」', '冲太岁' in rep_ts['verdict_reason'],
          rep_ts['verdict_reason'])
    check('A5d 建议含「切勿强行开工」', '切勿强行开工' in rep_ts['advice'],
          rep_ts['advice'])
    check('A5d 1000分仍黄牌（高分不得豁免）',
          build_decision_report(dict(r_ts, score=1000), '修造')['verdict_key']
          == 'warn')
    check('A5d 动土同口径黄牌',
          build_decision_report(dict(r_ts), '动土')['verdict_key'] == 'warn')
    check('A5d 嫁娶不套用修造红线（同数据仍绿灯）',
          build_decision_report(dict(r_ts), '嫁娶')['verdict_key'] == 'ok')
    check('A5d 无冲太岁明细的修造高分日不误伤',
          build_decision_report(dict(r_rz), '修造')['verdict_key'] == 'ok')

    # A6 纯度断言：build_decision_report 不变异入参
    r_pure = copy.deepcopy(r_veto)
    build_decision_report(r_veto, '嫁娶')
    check('A6 入参未被改写（纯度）', r_veto == r_pure)

    # A7 相主硬性门槛行不与 veto 重复入列
    r_dup = {'score': 0, 'level': '❌凶',
             'veto_reasons': ['[硬性门槛] 日支冲事主年命（一票否决）'],
             'xiangzhu_notes': ['[硬性门槛] 日支冲事主年命：-100分'],
             'shensha_list': []}
    rep7 = build_decision_report(r_dup, '入宅')
    check('A7 硬性门槛行不重复入事主列',
          len(rep7['owner_items']) == 1, str(rep7['owner_items']))

    # A8 明细折叠（>5 条）
    items = [(True, 'x%d' % i) for i in range(8)]
    tailed = _tail_items(items)
    check('A8 超 5 条折叠为 6 行', len(tailed) == 6 and tailed[-1][0] is None)

    # ── B 段：真实链路（夹具否决日 + 有限扫描非否决日）───────────────────
    print('-' * 78)
    print('【B 段】真实评分链路')
    owners = _load_owners('2023-01-11_嫁娶_乙丑时/owners_0111_g85.json')
    sz = _sizhu(2023, 1, 12, 2)  # 庚午日 丁丑时（夹具基线 veto 总分 0）
    r_real = calculate_score(sz, '嫁娶', owners, '阳宅', None,
                             None, None, None, None, None, zeli_mode='pure')
    rep_real = build_decision_report(r_real, '嫁娶')
    check('B1 2023-01-12 庚午日裁决为 veto',
          rep_real['verdict_key'] == 'veto',
          '%s | veto=%s' % (rep_real['verdict_key'],
                            r_real.get('veto_reasons')))
    check('B1 事主影响列非空', len(rep_real['owner_items']) >= 1,
          str(rep_real['owner_items']))
    check('B1 建议含「另择吉日」', '另择吉日' in rep_real['advice'])

    # B2：2026 年上半年嫁娶有限扫描（≤60 天），找首个非否决日验证结构完整
    rep_ok = None
    _scanned = 0
    for mo in range(1, 7):
        for d in range(1, 29):
            _scanned += 1
            if _scanned > 60:
                break
            sz2 = _sizhu(2026, mo, d, 10)
            r2 = calculate_score(sz2, '嫁娶', owners, '阳宅', None,
                                 None, None, None, None, None, zeli_mode='pure')
            if not (r2.get('veto_reasons') or []):
                rep_ok = build_decision_report(r2, '嫁娶')
                print('   ℹ 非否决日样本：2026-%02d-%02d 总分=%s 等级=%s 裁决=%s'
                      % (mo, d, r2.get('score'), r2.get('level'),
                         rep_ok['verdict_key']))
                break
        if rep_ok is not None or _scanned > 60:
            break
    check('B2 60 天内找到非否决日（实扫 %d 天）' % _scanned, rep_ok is not None)
    if rep_ok is not None:
        check('B2 非否决日裁决为 ok/warn',
              rep_ok['verdict_key'] in ('ok', 'warn'), rep_ok['verdict_key'])
        check('B2 报告结构完整（score/level/两列/advice 键）',
              all(k in rep_ok for k in
                  ('score', 'level', 'shan_items', 'owner_items', 'advice')))

    # B4：与详情页同源一致性——面板文案必须原样取自 result 现有字段，
    # 证明面板不臆造内容（详情页其余板块消费的也是同一批字段）
    def _all_strings(obj):
        out, stack = set(), [obj]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                stack.extend(cur.values())
            elif isinstance(cur, (list, tuple)):
                stack.extend(list(cur))
            elif isinstance(cur, str):
                out.add(cur)
        return out

    _pool = _all_strings(r_real)

    def _derived(text):
        t = str(text)
        if t.startswith(('☀️', '🌙')):
            return True                    # 日月角标为组合文案
        t = t.replace('（已制化）', '')
        if t.startswith('日课「') and t.endswith('」坐山'):
            return t[3:-4] in _pool
        return t in _pool

    _bad = [t for _, t in (rep_real['shan_items'] + rep_real['owner_items'])
            if not _derived(t)]
    check('B4 面板文案全部源自 result 字段（无臆造）', not _bad, str(_bad[:3]))

    _veto_txt = [str(v) for v in (r_real.get('veto_reasons') or [])]
    _shown = ([t for _, t in rep_real['shan_items']]
              + [t for _, t in rep_real['owner_items']]
              + list(rep_real['other_veto']))
    _folded = any('…另有' in str(t)
                  for _, t in rep_real['shan_items'] + rep_real['owner_items'])
    check('B4 每条否决项均出现在面板（未折叠时）',
          _folded or all(v in _shown for v in _veto_txt),
          '%s | shown=%s' % (_veto_txt, _shown))

    # B3：GUI 渲染冒烟（无显示环境时跳过）
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        from modules.决策分析 import render_decision_panel
        for rp, tag in ((rep_real, 'veto'), (rep2, 'warn'), (rep5, 'ok')):
            frm = render_decision_panel(root, rp)
            frm.pack()
        root.update_idletasks()
        root.destroy()
        check('B3 三档面板 GUI 渲染不抛异常', True)
    except tk.TclError as _e:
        print('   ⚠ 无显示环境，跳过 GUI 渲染冒烟（%s）' % _e)

    print('=' * 78)
    print('汇总：通过 %d，失败 %d' % (PASS, FAIL))
    if FAIL:
        print('❌ 存在失败项')
        return 1
    print('✅ 全部通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
