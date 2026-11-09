# -*- coding: utf-8 -*-
"""专家决策分析面板（001 §238.12，纯展示层汇总，不改评分/否决逻辑）。

从评分器 result dict 提取现有数据（否决项 / 三煞山家 / 相主明细 / 偏枯与
重煞预警），在日课详情窗顶部渲染「红绿灯决策面板」：

    🚫 绝对不可用（深红底白字）：veto_reasons 非空
    ⚠️ 慎用（需制化）（黄底黑字）：无否决，但命中重煞预警 / 五行偏枯 /
        神煞负分合计 ≤ -20 / 等级含「凶」
    ✅ 吉课可用（绿底黑字）：其余

公共接口：
    build_decision_report(result, event_type='') -> dict
    render_decision_panel(parent, report) -> tk.Frame（未 pack，调用方自 pack）
"""
import re

# ── 否决项分类关键词（事主优先，避免「本命三煞」被「三煞」抢分类）──────────
_OWNER_KEYS = ('事主', '命主', '年命', '生肖', '仙命', '亡命', '相主',
               '新郎', '新娘', '福主', '户主', '冲命', '生合')
_SHAN_KEYS = ('山家', '坐山', '坐向', '封禁', '三煞', '岁破', '阴府',
              '金神', '分金', '扶山', '补龙', '克山', '山', '向')

_VERDICT_STYLES = {
    'ok':   {'bg': '#66BB6A', 'fg': '#000000', 'icon': '✅', 'label': '吉课可用'},
    'warn': {'bg': '#FFD54F', 'fg': '#000000', 'icon': '⚠️',
             'label': '慎用（需制化）'},
    'veto': {'bg': '#B71C1C', 'fg': '#FFFFFF', 'icon': '🚫',
             'label': '绝对不可用'},
}
_PANEL_BG = {'ok': '#E8F5E9', 'warn': '#FFF8E1', 'veto': '#FFEBEE'}

_SCORE_RE = re.compile(r'([+-]\s*\d+)\s*分')


def _classify_veto(text):
    """否决文案分类：'owner'（对事主）/ 'shan'（对山家）/ 'other'。"""
    t = str(text)
    for k in _OWNER_KEYS:
        if k in t:
            return 'owner'
    for k in _SHAN_KEYS:
        if k in t:
            return 'shan'
    return 'other'


def _line_score(line):
    """从明细文本尾部提取分值（如「…：+10分」），无分值返回 None。"""
    m = None
    for m in _SCORE_RE.finditer(str(line)):
        pass
    if m:
        try:
            return int(m.group(1).replace(' ', ''))
        except ValueError:
            return None
    return None


def _tail_items(items, limit=5):
    """每列最多展示 limit 条，超出折叠为「…另有 N 项」。"""
    if len(items) <= limit:
        return items
    return items[:limit] + [(None, '…另有 %d 项，详见下文明细'
                             % (len(items) - limit))]


def build_decision_report(result, event_type=''):
    """汇总评分器 result 为决策报告（纯读取，不改写任何键）。

    返回 dict：
        verdict_key: 'ok' / 'warn' / 'veto'
        verdict:     展示文案（如 '🚫 绝对不可用'）
        verdict_reason: 裁决依据一句话
        shan_items:  [(is_good, text)] 对山家影响明细
        owner_items: [(is_good, text)] 对事主影响明细
        advice:      补救与建议（veto/warn 时非空）
        score/level: 总分与等级（展示用）
    """
    r = result if isinstance(result, dict) else {}
    veto = [str(v) for v in (r.get('veto_reasons') or [])]
    level = str(r.get('level') or '')
    try:
        score = int(r.get('score') or 0)
    except (TypeError, ValueError):
        score = 0
    heavy = str(r.get('heavy_sha_warning') or '')
    pianku = str(r.get('wuxing_pian_ku') or '')
    neg_total = 0
    for s in (r.get('shensha_list') or []):
        if isinstance(s, dict):
            try:
                v = int(s.get('score') or 0)
            except (TypeError, ValueError):
                v = 0
            if v < 0:
                neg_total += v

    shan_items, owner_items, other_veto = [], [], []

    # 1) 一票否决项分类入列
    for v in veto:
        cls = _classify_veto(v)
        if cls == 'owner':
            owner_items.append((False, v))
        elif cls == 'shan':
            shan_items.append((False, v))
        else:
            other_veto.append(v)

    # 2) 山家数据（全部来自 sansha_info / shanzuo_eval / sun_moon_info）
    si = r.get('sansha_info') or {}
    for d in (si.get('sansha_penalty_detail') or []):
        shan_items.append((False, str(d)))
    for w in (si.get('mountain_warnings') or []):
        shan_items.append((False, str(w)))
    for mt in (si.get('mountain_warnings_mitigated') or []):
        shan_items.append((True, '%s（已制化）' % str(mt)))
    for j in (si.get('mountain_jishen') or []):
        shan_items.append((True, str(j)))
    _mdt = str(si.get('mountain_day_type') or '')
    if _mdt:
        if any(k in _mdt for k in ('扶', '补', '生', '旺')):
            shan_items.append((True, '日课「%s」坐山' % _mdt))
        elif any(k in _mdt for k in ('伐', '克', '煞')):
            shan_items.append((False, '日课「%s」坐山' % _mdt))
    sz = r.get('shanzuo_eval')
    if isinstance(sz, dict) and sz.get('relation') not in (None, '', '未知'):
        try:
            _sv = int(sz.get('score') or 0)
        except (TypeError, ValueError):
            _sv = 0
        _reason = str(sz.get('reason') or '')
        if _reason:
            shan_items.append((_sv >= 0, _reason))
    _smd = ((r.get('sun_moon_info') or {}).get('taiyang_taiyin_detail') or {})
    if _smd.get('sun_effective'):
        shan_items.append((True, '☀️ 太阳%s'
                           % ('到山' if _smd.get('sun_to_mountain') else '到向')))
    if _smd.get('moon_effective'):
        shan_items.append((True, '🌙 太阴%s'
                           % ('到山' if _smd.get('moon_to_mountain') else '到向')))

    # 3) 事主数据（xiangzhu_notes 逐条定吉凶；[硬性门槛]行已由 veto 覆盖，跳过）
    for line in (r.get('xiangzhu_notes') or []):
        t = str(line)
        if '[硬性门槛]' in t:
            continue
        sc = _line_score(t)
        if sc is not None:
            owner_items.append((sc >= 0, t))
        elif any(k in t for k in ('冲', '刑', '害', '破', '克')):
            owner_items.append((False, t))
        else:
            owner_items.append((True, t))

    # 4) 综合裁决
    if veto:
        verdict_key = 'veto'
        verdict_reason = '；'.join(veto[:2]) + (' 等' if len(veto) > 2 else '')
    else:
        warn_reasons = []
        if heavy:
            warn_reasons.append('重煞预警')
        if pianku:
            warn_reasons.append('五行极度偏枯（%s）' % pianku)
        if neg_total <= -20:
            warn_reasons.append('凶煞扣分合计 %d 分' % neg_total)
        if '凶' in level:
            warn_reasons.append('总分 %d 分（%s）' % (score, level))
        if warn_reasons:
            verdict_key = 'warn'
            verdict_reason = '；'.join(warn_reasons)
        else:
            verdict_key = 'ok'
            verdict_reason = '无一票否决，无重大凶煞叠加'

    # 5) 补救与建议
    advice = ''
    if verdict_key == 'veto':
        advice = ('此日课犯 %s 大忌，没有任何制化余地，请立刻另择吉日！'
                  % (veto[0] if veto else ''))
    elif verdict_key == 'warn':
        _heavy_names = r.get('heavy_sha_names') or []
        if any('鲁班' in str(n) for n in _heavy_names) or '鲁班' in heavy:
            advice = '犯鲁班煞，建议择吉时并依规制化（如动土前祭拜），或另择吉日。'
        elif '燥' in pianku:
            advice = '此日五行过燥，建议配合下午（金水旺）的时辰使用。'
        elif '寒' in pianku:
            advice = '此日五行过寒，建议配合上午（木火旺）的时辰使用。'
        elif heavy:
            advice = '本日有重煞扣分（%s），须确认制化到位方可使用。' % heavy
        elif '凶' in level:
            advice = '本课总分偏低（%d 分，%s），建议另择高分吉日。' % (score, level)
        else:
            advice = '本日存在扣分项，请结合制化条件酌情使用。'

    style = _VERDICT_STYLES[verdict_key]
    return {
        'verdict_key': verdict_key,
        'verdict': '%s %s' % (style['icon'], style['label']),
        'verdict_reason': verdict_reason,
        'shan_items': _tail_items(shan_items),
        'owner_items': _tail_items(owner_items),
        'other_veto': other_veto,
        'advice': advice,
        'score': score,
        'level': level,
        'event_type': str(event_type or ''),
    }


def render_decision_panel(parent, report):
    """在 parent 内构建决策面板 Frame（未 pack，调用方自 pack）。

    结构：顶部大色块裁决条 → 两列（对山家影响 / 对事主影响）→ 底部结论建议。
    """
    import tkinter as tk

    rep = report if isinstance(report, dict) else {}
    key = rep.get('verdict_key') or 'ok'
    style = _VERDICT_STYLES.get(key, _VERDICT_STYLES['ok'])
    bg_main = style['bg']
    fg_main = style['fg']
    bg_sub = _PANEL_BG.get(key, '#F5F5F5')

    root = tk.Frame(parent, bd=1, relief=tk.SOLID, bg=bg_sub)

    # ── 顶部大色块裁决条 ────────────────────────────────────────────
    head_text = '%s 【综合裁决：%s】　总分 %s 分 · %s' % (
        style['icon'], style['label'], rep.get('score', 0),
        rep.get('level', '') or '—')
    tk.Label(root, text=head_text, bg=bg_main, fg=fg_main,
             font=('Microsoft YaHei UI', 13, 'bold'),
             anchor='w', padx=10, pady=6).pack(fill=tk.X)
    if rep.get('verdict_reason'):
        tk.Label(root, text='裁决依据：%s' % rep['verdict_reason'],
                 bg=bg_main, fg=fg_main,
                 font=('Microsoft YaHei UI', 10),
                 anchor='w', padx=10, pady=2).pack(fill=tk.X)

    # ── 两列：对山家影响 / 对事主影响 ──────────────────────────────
    cols = tk.Frame(root, bg=bg_sub)
    cols.pack(fill=tk.X, padx=8, pady=(6, 2))
    cols.columnconfigure(0, weight=1)
    cols.columnconfigure(1, weight=1)
    for ci, (title, items) in enumerate((
            ('⛰️ 对坐山的影响', rep.get('shan_items') or []),
            ('👪 对事主的影响', rep.get('owner_items') or []))):
        cell = tk.Frame(cols, bg=bg_sub)
        cell.grid(row=0, column=ci, sticky='new',
                  padx=(0, 6) if ci == 0 else (6, 0))
        tk.Label(cell, text=title, bg=bg_sub, fg='#333333',
                 font=('Microsoft YaHei UI', 10, 'bold'),
                 anchor='w').pack(fill=tk.X)
        if items:
            for is_good, text in items:
                if is_good is None:
                    mark, fg_it = 'ℹ', '#666666'
                elif is_good:
                    mark, fg_it = '✓', '#1B5E20'
                else:
                    mark, fg_it = '✗', '#B71C1C'
                tk.Label(cell, text='%s %s' % (mark, text),
                         bg=bg_sub, fg=fg_it,
                         font=('Microsoft YaHei UI', 9),
                         anchor='w', justify=tk.LEFT,
                         wraplength=320).pack(fill=tk.X, padx=(4, 0))
        else:
            tk.Label(cell, text='— 无显著影响', bg=bg_sub, fg='#888888',
                     font=('Microsoft YaHei UI', 9),
                     anchor='w').pack(fill=tk.X, padx=(4, 0))

    # ── 底部结论与补救建议 ──────────────────────────────────────────
    if rep.get('other_veto'):
        tk.Label(root, text='其他否决：' + '；'.join(rep['other_veto']),
                 bg=bg_sub, fg='#B71C1C', font=('Microsoft YaHei UI', 9),
                 anchor='w', justify=tk.LEFT, wraplength=680,
                 padx=10).pack(fill=tk.X)
    if rep.get('advice'):
        tk.Label(root, text='结论：%s' % rep['advice'],
                 bg=bg_sub, fg=('#B71C1C' if key == 'veto' else '#5D4037'),
                 font=('Microsoft YaHei UI', 10, 'bold'),
                 anchor='w', justify=tk.LEFT, wraplength=680,
                 padx=10, pady=4).pack(fill=tk.X)
    return root
