# -*- coding: utf-8 -*-
"""
§205 红帖分流修复验收（2026-10-30 用户拍板：非零分凶必须分流，不留专项）

背景断层 Bug：评分升级后存在「非零分但等级为凶」的日课（实测 2026-01-15 嫁娶
33 分「❌ 凶」），红帖分流只认 score==0，仍按吉帖印「嫁娶结婚大利」——灾难性误导。

拍板三分流：
  硬否决帖：一票否决或 score==0 → compose_veto_lines（深红，绝无吉语）
  软忌/慎用帖：level 含「凶」但不满足硬否决 → compose_caution_lines（复用深红底色，
    标题「慎用」，吉时栏保留 + 缓冲语「若必用此日，请选以下时辰」，时辰不印等级）
  正常吉帖：level 平/吉/上吉 → 原模板正常渲染

校验段：
  A 分流判定矩阵（prepare_entry 层 _is_vetoed / _is_soft_caution）
  B 慎用帖结构 + 七类事项吉语反向断言（大吉/大利/日吉时良/吉课/吉日 零命中）
  C 吉时栏保留：缓冲语 + 时辰条数口径 + 时辰行不印等级
  D 用户验收口径：33 分嫁娶不再印「大利」
  E 真实链路：评分器实算 2026-01-15（非零分凶）→ 慎用帖 + 忌项软忌块
  F 硬否决回归：0 分凶仍走否决帖（无时辰区、有「不可使用」牌）
  G 正常吉帖回归：吉/平等级仍走原吉帖模板
  H GUI/打印分流：show_detail 深红、print_detail 深红纸型 + 「日课慎用提示」标题

退出码：0=全过，1=有失败
  python tests/verify_205_红帖分流.py
================================================================================
"""
import sys
import inspect
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FAILS = []


def check(name, cond, detail=''):
    if cond:
        print(f'  PASS  {name}')
    else:
        print(f'  FAIL  {name}  {detail}')
        FAILS.append(name)


EVENTS = ['嫁娶', '订婚', '修造', '动土', '入宅', '安葬', '开业']
CAUTION_FORBIDDEN = ('大吉', '大利', '日吉时良', '吉课', '吉日', '发轿大吉')


def _mk(date, ev, **kw):
    from modules import 择日贴 as Z
    d = {'date': date, 'event_type': ev}
    d.update(kw)
    return Z.prepare_entry(d)


def _text(lines):
    return '\n'.join(t for _, t in lines)


def main():
    from modules import 择日贴 as Z

    # ============ A：分流判定矩阵 ============
    print('[A] 分流判定矩阵')
    e = _mk('2026-10-20', '嫁娶', score=33, level='❌ 凶')
    check('A 非零分凶 → 慎用', e['_is_soft_caution'] and not e['_is_vetoed'])
    e = _mk('2026-10-20', '嫁娶', score=50, level='大凶')
    check('A 大凶非零分 → 慎用', e['_is_soft_caution'] and not e['_is_vetoed'])
    e = _mk('2026-10-20', '嫁娶', score=0, level='凶')
    check('A 0 分凶 → 硬否决优先（慎用=False）',
          e['_is_vetoed'] and not e['_is_soft_caution'])
    e = _mk('2026-10-20', '嫁娶', score=88, level='吉',
            veto_reasons=['月破（一票否决）'])
    check('A 有一票否决原因（即便吉级）→ 硬否决优先',
          e['_is_vetoed'] and not e['_is_soft_caution'])
    for lv in ('吉', '上吉', '平', '中吉'):
        e = _mk('2026-10-20', '嫁娶', score=88, level=lv)
        check(f'A level={lv} → 既不否决也不慎用',
              not e['_is_vetoed'] and not e['_is_soft_caution'])

    # ============ B：慎用帖结构 + 七类事项吉语反向 ============
    print('[B] 慎用帖结构与吉语反向（七类事项）')
    for ev in EVENTS:
        ge = _mk('2026-10-20', ev, score=33, level='❌ 凶',
                 reason='忌：红纱日、鬼哭日；正体大凶：子山正体五行受日课四柱克泄')
        lines = Z.compose_detail_lines(ge)
        txt = _text(lines)
        styles = {s for s, _ in lines}
        hit = [k for k in CAUTION_FORBIDDEN if k in txt]
        check(f'B {ev} 慎用帖零吉语（异常 {hit}）', not hit, f'{hit}')
        check(f'B {ev} verdict/stamp/rule/tbl/warn 齐备',
              ('verdict' in styles) and ('stamp' in styles) and ('rule' in styles)
              and ('tbl' in styles) and ('warn' in styles), sorted(styles))
        check(f'B {ev} 标题「本日多煞 建议慎用」', '本日多煞　建议慎用' in txt)
        check(f'B {ev} 慎黄牌在位', ('stamp', '慎　　用') in lines)
    # 无 reason 兜底
    ge = _mk('2026-10-20', '开业', score=33, level='凶')
    wl = [t for s, t in Z.compose_detail_lines(ge) if s == 'warn']
    check('B 无 reason 时 ① 兜底（等级为凶说明）',
          len(wl) == 1 and wl[0].startswith('①') and '等级为凶' in wl[0], f'{wl}')
    # 有 reason 时软忌编号 ①②
    ge = _mk('2026-10-20', '修造', score=33, level='凶',
             reason='凶神：月破；正体大凶：子山正体五行受日课四柱克泄')
    wl = [t for s, t in Z.compose_detail_lines(ge) if s == 'warn']
    check('B 软忌块按 ①② 编号', [w[0] for w in wl] == ['①', '②'], f'{wl}')
    check('B 软忌块含 月破/正体大凶',
          any('月破' in w for w in wl) and any('正体大凶' in w for w in wl), f'{wl}')

    # ============ C：吉时栏保留 ============
    print('[C] 吉时栏保留 + 缓冲语')
    ge = _mk('2026-10-20', '嫁娶', score=33, level='❌ 凶',
             owners_list=[{'name': '新娘', 'role': '新娘', 'year_sx': '猪'}])
    lines = Z.compose_detail_lines(ge)
    txt = _text(lines)
    check('C 缓冲语「若必用此日」在位', '若必用此日，请选以下时辰' in txt)
    n_shi = sum(1 for _, t in lines if '时（' in t)
    check(f'C 时辰条数 ≡ min(len(_jishi),3)（{n_shi} vs {min(len(ge["_jishi"]), 3)}）',
          n_shi == min(len(ge['_jishi']), 3))
    shi_rows = [t for _, t in lines if '时（' in t]
    check('C 时辰行不印等级（大吉/吉/次吉零出现）',
          not any(g in r for r in shi_rows for g in ('大吉', '次吉', '　吉')), f'{shi_rows}')
    check('C 嫁娶慎用帖保留发轿节点（时辰名称不动）',
          any('发轿' in r for r in shi_rows), f'{shi_rows}')

    # ============ D：用户验收口径 ============
    print('[D] 33 分嫁娶不再印「大利」')
    ge = _mk('2026-01-15', '嫁娶', score=33, level='❌ 凶',
             reason='忌：红纱日、鬼哭日',
             owners_list=[{'name': '新娘', 'role': '新娘', 'year_sx': '猪'},
                          {'name': '新郎', 'role': '新郎', 'year_sx': '狗'}])
    txt = _text(Z.compose_detail_lines(ge))
    check('D 33 分嫁娶无「嫁娶结婚大利」', '嫁娶结婚大利' not in txt)
    check('D 33 分嫁娶无「谨择…大利」', '大利' not in txt)
    check('D 33 分嫁娶有「慎用」', '慎' in txt)
    check('D 33 分仍印评分（33分）', '33' in txt)

    # ============ E：真实链路（评分器实算） ============
    print('[E] 真实链路：2026-01-15 嫁娶（非零分凶实算）')
    from modules.四柱计算器 import calculate_sizhu
    from modules.评分器 import calculate_score
    owners = [{'name': '新娘', 'role': '新娘', 'year_sx': '猪', '性别': '女'},
              {'name': '新郎', 'role': '新郎', 'year_sx': '狗', '性别': '男'}]
    sz = calculate_sizhu(dt.date(2026, 1, 15), 10, 0)
    r = calculate_score(sz, '嫁娶', owners=owners)
    check(f"E 实算非零分且等级含凶（score={r.get('score')} level={r.get('level')}）",
          bool(r.get('score')) and '凶' in str(r.get('level')))
    ge = _mk('2026-01-15', '嫁娶', score=r.get('score'), level=r.get('level'),
             reason=r.get('reason'), veto_reasons=r.get('veto_reasons'),
             owners_list=owners)
    lines = Z.compose_detail_lines(ge)
    txt = _text(lines)
    check('E 实算日课分流到慎用帖', ge['_is_soft_caution'] and not ge['_is_vetoed'])
    check('E 实算慎用帖零「大利」', '大利' not in txt)
    check('E 实算慎用帖软忌块含红纱日', '红纱日' in txt)
    check('E 实算慎用帖有缓冲语', '若必用此日' in txt)

    # ============ F：硬否决回归 ============
    print('[F] 硬否决回归')
    ge = _mk('2026-11-13', '嫁娶', score=0, level='大凶',
             veto_reasons=['岁破（一票否决）'])
    lines = Z.compose_detail_lines(ge)
    txt = _text(lines)
    check('F 0 分否决 → stamp 不可使用', ('stamp', '不　可　使　用') in lines)
    check('F 否决帖无时辰区【　时　辰　】', '【　时　辰　】' not in txt)
    check('F 否决帖无慎用牌', ('stamp', '慎　　用') not in lines)
    check('F 否决帖无缓冲语', '若必用此日' not in txt)

    # ============ G：正常吉帖回归 ============
    print('[G] 正常吉帖回归（吉/平 不受影响）')
    ge = _mk('2026-10-20', '嫁娶', score=88, level='吉')
    txt = _text(Z.compose_detail_lines(ge))
    check('G 88 分吉 → 仍印「嫁娶结婚大利」', '嫁娶结婚大利' in txt)
    check('G 88 分吉 → 无「慎用」', '慎　　用' not in txt)
    ge = _mk('2026-10-20', '修造', score=60, level='平', shan_xiang='子山午向')
    txt = _text(Z.compose_detail_lines(ge))
    check('G 60 分平修造 → 仍走修造模板（紫微高照）', '紫微高照' in txt)
    check('G 60 分平 → 不慎用', '本日多煞' not in txt)

    # ============ H：GUI/打印分流 ============
    print('[H] GUI/打印分流')
    src_win = inspect.getsource(Z.ZeriTieWindow)
    check('H show_detail 慎用同走深红', '_is_soft_caution' in src_win)
    check('H print_detail 慎用走 veto 纸型',
          "e.get('_is_vetoed') or e.get('_is_soft_caution')" in src_win)
    check('H print_detail 慎用标题「日课慎用提示」', '日课慎用提示' in src_win)
    ge = _mk('2026-10-20', '嫁娶', score=33, level='凶')
    doc = Z.render_print_html(Z.compose_detail_lines(ge), '日课慎用提示', paper='veto')
    check('H 慎用帖深红纸型渲染', '#8B0000' in doc and '#C11B17' not in doc)
    check('H 慎用帖渲染含 stamp 慎用',
          'class="stamp"' in doc and '慎' in doc)

    # ============ I：S4 收尾（时间轴 + 落款弱化 + 双线框） ============
    print('[I] S4 发轿时间轴 / 落款下沉 / 双线框')
    # I-1 古风行程节点（保留「发轿」字样，verify_205-C 依赖）
    check('I 嫁娶节点改古风行程（起轿/进门/交拜）',
          Z._STAGE_LABELS['marriage'] == ['起轿·发轿', '迎娶·进门', '交拜·合卺'],
          f"{Z._STAGE_LABELS['marriage']}")
    # I-2 七类吉帖吉时行一律 ①②③ 编号
    for ev in EVENTS:
        ge = _mk('2026-10-20', ev, score=88, level='吉')
        rows = [t for _, t in Z.compose_detail_lines(ge) if '时（' in t]
        check(f'I {ev} 吉时行 ①②③ 编号（{len(rows)} 行）',
              bool(rows) and all(r[0] in Z._CIRCLED for r in rows), f'{rows[:2]}')
    # I-3 嫁娶吉帖时间轴节点文案
    ge = _mk('2026-10-20', '嫁娶', score=88, level='吉',
             owners_list=[{'name': '新娘', 'role': '新娘', 'year_sx': '猪'}])
    mtxt = _text(Z.compose_detail_lines(ge))
    check('I 嫁娶吉帖含「① 起轿·发轿」', '① 起轿·发轿' in mtxt)
    # I-4 慎用帖时辰行同步编号（33 分凶嫁娶）
    ge = _mk('2026-10-20', '嫁娶', score=33, level='❌ 凶')
    rows = [t for _, t in Z.compose_detail_lines(ge) if '时（' in t]
    check('I 慎用帖时辰行 ① 编号 + 古风节点',
          bool(rows) and rows[0].startswith('①') and '起轿·发轿' in rows[0], f'{rows[:1]}')
    # I-5 落款下沉弱化：〔廖贵雄印〕+ 前置 rule；七类 + 否决 + 慎用全覆盖
    for ev in EVENTS:
        for kw, tag in ((dict(score=88, level='吉'), '吉'),
                        (dict(score=33, level='❌ 凶'), '慎用'),
                        (dict(score=0, level='大凶', veto_reasons=['月破（一票否决）']), '否决')):
            lines = Z.compose_detail_lines(_mk('2026-10-20', ev, **kw))
            txt = _text(lines)
            seal = '〔廖贵雄印〕' in txt and '择日依据：' in txt
            sig_i = next((i for i, (_, t) in enumerate(lines) if '择日师' in t), -1)
            rule_before = sig_i > 0 and any(s == 'rule' for s, _ in lines[:sig_i])
            check(f'I {ev}-{tag}帖 落款印章+前置金线', seal and rule_before)
    # I-6 嫁娶/通用/总录落款统一（原自带结尾已收编）
    ge = _mk('2026-10-20', '嫁娶', score=88, level='吉')
    check('I 嫁娶帖落款含印章', '〔廖贵雄印〕' in _text(Z.compose_detail_lines(ge)))
    sm = _text(Z.compose_summary_lines([_mk('2026-10-20', '开业', score=88, level='吉')]))
    check('I 择日总录落款含印章+依据', '〔廖贵雄印〕' in sm and '择日依据：' in sm)
    # I-7 双击定位剥圈码（源码级）
    src_win = inspect.getsource(Z.ZeriTieWindow)
    check('I 双击定位剥离圈码', 'line[0] in _CIRCLED' in src_win)
    # I-8 双线框：三纸型均含金色双线边框（veto 经替换继承）
    ge = _mk('2026-10-20', '嫁娶', score=88, level='吉')
    for pp in ('red', 'white', 'veto'):
        doc = Z.render_print_html(Z.compose_detail_lines(ge), 't', paper=pp)
        check(f'I {pp} 纸型金色双线框', 'border: 5px double #C9A227' in doc)
    # I-9 rule 行真实渲染（HTML 不再落 blank；源码级 + 实例）
    doc = Z.render_print_html(Z.compose_detail_lines(ge), 't', paper='red')
    check('I HTML rule 行渲染 <div class="rule">', '<div class="rule">' in doc)
    check('I GUI rule 行渲染金色细线（源码）',
          "elif style == 'rule':" in src_win and "'─' * 30" in src_win)

    print()
    if FAILS:
        print(f'FAIL {len(FAILS)} 项：{FAILS}')
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
