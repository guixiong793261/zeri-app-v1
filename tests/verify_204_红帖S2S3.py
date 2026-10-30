# -*- coding: utf-8 -*-
"""
§204 红帖 S2/S3 验收（2026-10-30，用户拍板 Commit1=S2、Commit2=S3）

S2 否决帖独立渲染：
  A 否决帖结构——verdict 大字 + stamp 牌 + rule 双线 + tbl 信息行 + 编号 warn 原因
  B 吉语反向断言——「大吉／日吉时良／发轿／大利／吉时／吉日／吉课」零出现（七类事项全覆盖）
  C 编号制——多条否决原因按 ①②③ 顺序编号，无原因时 ① 兜底
S3 吉日帖信息表化与软忌补漏：
  D 七类模板均含 tbl 信息行
  E _degrade_warn_lines 两态——有「凶神／正体大凶」理由则必显 warn，无 reason 则返回空
  F 软忌块接入——七类模板在带 reason 的吉课中均出现 warn 行（有软忌必显）
  G 渲染器三纸型——veto=#8B0000 且不残留 #C11B17；white=#ffffff；red=#C11B17
  H warn 块不与 warnhl 叠加（<div class="warn"> 计数 > 0 且无 "warn warnhl"）
  I GUI 双端——否决配色 #8B0000 / print_detail 走 veto 纸型（源码级断言）；
    择日贴吉时条数口径不变（含「时（」行数 ≡ min(len(_jishi),3)）

退出码：0=全过，1=有失败
  python tests/verify_204_红帖S2S3.py
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


# 七类事项 → 模板键（覆盖 compose_detail_lines 全部分派）
EVENTS = [('嫁娶', 'marriage'), ('订婚', 'engagement'), ('修造', 'xiuzao'),
          ('动土', 'dongtu'), ('入宅', 'ruzhai'), ('安葬', 'anzhang'),
          ('开业', 'common')]
AUS = ('大吉', '日吉时良', '发轿', '大利', '吉时', '吉日', '吉课', '迎娶', '拜堂')


def _mk(date, ev, **kw):
    from modules import 择日贴 as Z
    d = {'date': date, 'event_type': ev}
    d.update(kw)
    return Z.prepare_entry(d)


def _text(lines):
    return '\n'.join(t for _, t in lines)


def main():
    from modules import 择日贴 as Z

    # ============ A：否决帖结构 ============
    print('[A] S2 否决帖结构')
    e = _mk('2026-11-13', '嫁娶',
            veto_reasons=['三煞大忌：年三煞犯亥方（一票否决）',
                          '冲新娘：日柱冲坤造年命',
                          '红纱日：婚嫁大忌'],
            score=0, level='大凶')
    lines = Z.compose_detail_lines(e)
    styles = {s for s, _ in lines}
    txt = _text(lines)
    check('A 否决日走 compose_veto_lines（_is_vetoed=True）', e.get('_is_vetoed'))
    check('A 结论大字 verdict 在位', ('verdict', '本　日　不　吉') in lines)
    check('A 明黄否决牌 stamp 在位', ('stamp', '不　可　使　用') in lines)
    check('A 双线分隔 rule ≥2 条', sum(1 for s, _ in lines if s == 'rule') >= 2)
    check('A 信息表 tbl ≥3 行', sum(1 for s, _ in lines if s == 'tbl') >= 3,
          f'实得 {sum(1 for s, _ in lines if s == "tbl")}')
    check('A 版式集合不含吉帖大字/h2 混排（verdict 唯一）',
          sum(1 for s, _ in lines if s == 'verdict') == 1)
    check('A 否决帖无「吉时/大吉」段落', not any(k in txt for k in ('【　吉　时　】', '大吉')))

    # ============ B：吉语反向断言（七类事项 × 否决日） ============
    print('[B] S2 吉语反向断言（七类事项全覆盖）')
    bad_all = []
    for ev, _tpl in EVENTS:
        ev_e = _mk('2026-11-13', ev, veto_reasons=['月破（一票否决）', '受死日'],
                   score=0, level='大凶')
        t = _text(Z.compose_detail_lines(ev_e))
        hit = [k for k in AUS if k in t]
        if hit:
            bad_all.append((ev, hit))
    check(f'B 七类否决帖零吉语（异常 {len(bad_all)}）', not bad_all, f'{bad_all}')

    # ============ C：编号制 ============
    print('[C] S2 编号制（①②③）')
    wr = [t for s, t in lines if s == 'warn']
    check('C 三条否决原因 → 三条 warn 块', len(wr) == 3, f'{wr}')
    check('C 编号按序 ①②③', [w[0] for w in wr] == ['①', '②', '③'], f'{[w[0] for w in wr]}')
    e0 = _mk('2026-11-13', '开业', score=0, level='大凶')   # 无 veto_reasons
    w0 = [t for s, t in Z.compose_detail_lines(e0) if s == 'warn']
    check('C 无原因时 ① 兜底', len(w0) == 1 and w0[0].startswith('①'), f'{w0}')

    # ============ D：七类模板 tbl 信息表 ============
    print('[D] S3 信息表化（tbl）')
    for ev, tpl in EVENTS:
        ge = _mk('2026-10-20', ev, score=88, level='吉')
        n = sum(1 for s, _ in Z.compose_detail_lines(ge) if s == 'tbl')
        check(f'D {tpl} 模板含 tbl ≥1（实得 {n}）', n >= 1)
    # 坐山类：修造/动土/安葬 坐向行走 tbl（入宅模板本无坐向行，不在此列）
    for ev, tpl in (('修造', 'xiuzao'), ('动土', 'dongtu'), ('安葬', 'anzhang')):
        ge = _mk('2026-10-20', ev, score=88, level='吉', shan_xiang='子山午向',
                 fenjin='庚子庚午')
        tl = [t for s, t in Z.compose_detail_lines(ge) if s == 'tbl']
        check(f'D {tpl} 坐向信息入 tbl', any('子山午向' in t for t in tl), f'{tl[:4]}')

    # ============ E：_degrade_warn_lines 两态 ============
    print('[E] S3 _degrade_warn_lines 两态')
    with_reason = {'reason': '五行：木旺；凶神：红纱日、受死日；正体大凶：子山正体五行受日课四柱克泄；吉神：天德'}
    dw = Z._degrade_warn_lines(with_reason)
    check('E 有凶神 → 出 warn（含煞名）',
          len(dw) >= 1 and '红纱日' in dw[0][1], f'{dw}')
    check('E 有正体大凶 → 出 warn（含原文）',
          any('正体大凶' in t for _, t in dw), f'{dw}')
    check('E 凶神段不重复成两条（同一煞名只一条）',
          sum(1 for _, t in dw if '红纱日' in t) == 1)
    check('E 无 reason → 返回空列表', Z._degrade_warn_lines({}) == [])
    check('E reason 仅吉神/宜 → 返回空',
          Z._degrade_warn_lines({'reason': '吉神：天德；宜：嫁娶'}) == [])
    # 事类忌（「忌：词讼」）只作避用提示，不得谎称计入评分
    dw3 = Z._degrade_warn_lines({'reason': '宜：嫁娶；忌：词讼'})
    check('E 忌项段出 warn（事类忌也提示）', len(dw3) == 1, f'{dw3}')
    check('E 忌项段不谎称「计入评分」', '已按轻扣' not in dw3[0][1], f'{dw3}')
    check('E 否决原因不与软忌重复（不含否决括号文案）',
          not any('（一票否决）' in t or '该日评分为 0 分' in t for _, t in dw))
    # 真实理由串形态（评分器 reason 实测：软忌在「忌：」段）
    real_reason = ('嫁娶要点：基础分；扣分：大黄道朱雀黑道日；红纱日；鬼哭日\n'
                   '宜：不将日、嫁娶\n'
                   '忌：红纱日、鬼哭日、大黄道朱雀黑道日、小黄道建日（黑道凶日）')
    dw2 = Z._degrade_warn_lines({'reason': real_reason})
    check('E 真实 reason（忌：段）→ 出 warn', len(dw2) >= 1, f'{dw2}')
    check('E 真实 reason 软忌含 红纱日/鬼哭日',
          len(dw2) >= 1 and '红纱日' in dw2[0][1] and '鬼哭日' in dw2[0][1], f'{dw2}')
    check('E 真实 reason 不把「宜：」吉神误当软忌',
          len(dw2) >= 1 and '不将日' not in dw2[0][1], f'{dw2}')

    # ============ F：软忌块接入七类模板 ============ 
    print('[F] S3 软忌必显（七类模板）')
    for ev, tpl in EVENTS:
        ge = _mk('2026-10-20', ev, score=88, level='吉',
                 reason='凶神：红纱日；正体大凶：子山正体五行受日课四柱克泄')
        wl = [t for s, t in Z.compose_detail_lines(ge) if s == 'warn']
        check(f'F {tpl} 模板软忌入 warn（实得 {len(wl)}）', len(wl) >= 1, f'{wl}')
    # 无软忌时不得虚构（模板固有避煞 warn 不算软忌，只查「注意事项」块）
    for ev, tpl in EVENTS:
        ge = _mk('2026-10-20', ev, score=88, level='吉')
        wl = [t for s, t in Z.compose_detail_lines(ge) if s == 'warn' and t.startswith('注意事项')]
        check(f'F {tpl} 无软忌时零软忌 warn（实得 {len(wl)}）', len(wl) == 0, f'{wl}')

    # ============ G：渲染器三纸型 ============
    print('[G] S3 渲染器三纸型')
    doc_v = Z.render_print_html(lines, '日课否决警示', paper='veto')
    doc_r = Z.render_print_html(lines, '吉课', paper='red')
    doc_w = Z.render_print_html(lines, '安葬', paper='white')
    check('G veto 纸底 #8B0000', '#8B0000' in doc_v)
    check('G veto 不残留吉帖纸底 #C11B17', '#C11B17' not in doc_v)
    check('G veto 墨色 #FFF0C2', '#FFF0C2' in doc_v)
    check('G red 纸底 #C11B17', 'background: #C11B17' in doc_r and '#FFF0C2' not in doc_r)
    check('G white 白底 #ffffff', 'background: #ffffff' in doc_w and '#C11B17' not in doc_w)
    check('G veto 渲染含 verdict/stamp class',
          'class="verdict"' in doc_v and 'class="stamp"' in doc_v)
    check('G 三纸型文档互异', doc_v != doc_r and doc_r != doc_w and doc_v != doc_w)

    # ============ H：warn 块不高亮叠加 ============
    print('[H] S3 warn 与 warnhl 不叠加')
    check('H veto 文档含 <div class="warn">', '<div class="warn">' in doc_v,
          f'warn 计数 {doc_v.count("class=" + chr(34) + "warn")}')
    check('H 无 "warn warnhl" 叠加', 'warn warnhl' not in doc_v)
    check('H warn 行文本不含 ⚠ 前缀',
          not any('⚠' in t for s, t in lines if s == 'warn'))

    # ============ I：GUI 双端 + 吉时口径回归 ============
    print('[I] GUI 双端与吉时口径')
    src_win = inspect.getsource(Z.ZeriTieWindow)
    for tag in ('verdict', 'stamp', 'tbl', 'warn', 'rule'):
        n = src_win.count(f"('{tag}', {{")
        check(f'I tkinter 双文本框均注册 {tag} tag（实得 {n}）', n >= 2, f'{n}')
    check('I show_detail 否决配色 #8B0000', '#8B0000' in src_win)
    check("I print_detail 否决走 veto 纸型", "paper = 'veto'" in src_win)
    # 嫁娶吉时条数口径（verify_嫁娶深水区修复.py 依赖）不变
    me = _mk('2026-10-20', '嫁娶', score=88, level='吉',
             owners_list=[{'name': '新娘', 'role': '新娘', 'year_sx': '猪'}])
    ml = Z.compose_detail_lines(me)
    n_shi = sum(1 for _, t in ml if '时（' in t)
    check(f'I 嫁娶「时（」行数 ≡ min(len(_jishi),3)（{n_shi} vs {min(len(me["_jishi"]), 3)}）',
          n_shi == min(len(me['_jishi']), 3))
    check('I 嫁娶吉帖仍含吉时分区与吉语（未被 S2 误伤）',
          '【　吉　时　】' in _text(ml) and '嫁娶结婚大利' in _text(ml))

    print()
    if FAILS:
        print(f'FAIL {len(FAILS)} 项：{FAILS}')
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
