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
    # 001 §238.15：评分器已把 mountain_warnings 原始列表分流为三类：
    #   - 有制化 → mountain_warnings_mitigated（进 ✓）
    #   - 无制化/制化不全 → sansha_penalty_detail + ji_list（进 ✗）
    # 故此处直接消费分流结果，跳过原始 mountain_warnings，避免同一煞
    # 同时出现在 ✗（原始）和 ✓（已制化）造成视觉混乱。
    #
    # 额外去重：veto（一票否决）和 sansha_penalty_detail 可能重叠
    # （如"年三煞(山向)"既是否决又扣分），veto 已经在顶部大红色
    # 展示过，下方山家影响里应过滤掉避免同一煞出现两次。
    si = r.get('sansha_info') or {}

    def _in_veto(text):
        """text 含任一 veto 条目的关键煞名 → True。

        用"关键煞名"（去掉括号/括号内文字后的核心词）做匹配，
        避免全角/半角括号差异导致漏匹配。
        例：sansha_penalty_detail = "年三煞(山向)（-25分）"
            veto = "月建丑正当年三煞（亥子丑）方" → 都含 "年三煞" → True
        """
        _key = str(text)
        for _v in veto:
            _vs = str(_v)
            # 尝试所有常见三煞名
            for _n in ('年三煞', '月三煞', '日三煞', '年劫煞', '时劫煞',
                       '伐日', '山家封禁'):
                if _n in _key and _n in _vs:
                    return True
        return False

    for d in (si.get('sansha_penalty_detail') or []):
        if _in_veto(d):
            continue  # 已在否决区展示，不再重复
        shan_items.append((False, str(d)))
    for mt in (si.get('mountain_warnings_mitigated') or []):
        if _in_veto(mt):
            continue
        shan_items.append((True, '%s（已制化）' % str(mt)))
    for j in (si.get('mountain_jishen') or []):
        if _in_veto(j):
            continue
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

    # 4) 综合裁决（001 §238.15 阶梯式高分豁免）
    #
    # 核心矛盾：修造择日几乎必然向方犯三煞（日三煞/月三煞向方各 -15/-6/-3），
    # 导致 neg_total 轻易踩 -20 阈值弹黄牌。但总分≥200 的吉日，向方扣分被
    # 高分（五行 + 吉神 + 补龙扶山）完全覆盖，实际可用率极高。
    #
    # 阶梯阈值（按总分分档，越严越往上）：
    #   否决 → 任何 veto_reasons = 🚫
    #   上吉/大吉（≥250） → sansha_penalty < -60 或 neg_total < -70 才黄牌
    #   吉（200~249）     → sansha_penalty < -40 或 neg_total < -50 才黄牌
    #   普通（<200）      → 保持原逻辑 neg_total < -20 即黄牌
    # 五行偏枯 / 重煞预警标记（鲁班煞等高危）任何分数都触发黄牌。
    sansha_penalty = int(si.get('sansha_penalty') or 0)

    # 001 §238.15c：重煞名分两类——
    #   真重煞（伐日/三煞临山/金神到山/合局克山）→ 硬触发黄牌
    #   可豁免（三煞向方）→ 只有扣分不否决，几乎所有修造课都有，不触发
    # 先统一解析（裁决块 + advice 块都要复用）
    _heavy_names = si.get('heavy_sha_names') or []
    _ZHEN_KW = ('伐日', '临山', '金神', '克山')
    zhen_heavy = [n for n in _heavy_names
                  if any(kw in str(n) for kw in _ZHEN_KW)]
    has_zhen_heavy = bool(zhen_heavy)
    # 鲁班煞属于 shensha_list 里的重煞（不在 heavy_sha_names），也硬触发
    _has_luban = any('鲁班' in str(s) for s in (r.get('shensha_list') or []))
    real_heavy = has_zhen_heavy or _has_luban

    if veto:
        verdict_key = 'veto'
        verdict_reason = '；'.join(veto[:2]) + (' 等' if len(veto) > 2 else '')
    else:
        warn_reasons = []
        # 先判真重煞硬触发（不看分数）
        if real_heavy:
            _hit = zhen_heavy + (['鲁班煞'] if _has_luban else [])
            warn_reasons.append('重煞预警（%s）' % '；'.join(_hit))
        # 五行偏枯分数阈值偏低时触发
        if pianku and score < 250:
            warn_reasons.append('五行极度偏枯（%s）' % pianku)
        # 阶梯式重煞扣分阈值
        if score >= 250:
            # 上吉/大吉：只有真重煞才黄牌，向方扣分完全豁免
            if sansha_penalty <= -60:
                warn_reasons.append('三煞扣分合计 %d 分（含重煞）' % sansha_penalty)
            if neg_total <= -70:
                warn_reasons.append('凶煞扣分合计 %d 分' % neg_total)
        elif score >= 200:
            # 吉：中等重煞黄牌
            if sansha_penalty <= -40:
                warn_reasons.append('三煞扣分合计 %d 分（含重煞）' % sansha_penalty)
            if neg_total <= -50:
                warn_reasons.append('凶煞扣分合计 %d 分' % neg_total)
        else:
            # 普通分数：保持原逻辑
            if neg_total <= -20:
                warn_reasons.append('凶煞扣分合计 %d 分' % neg_total)
            if '凶' in level:
                warn_reasons.append('总分 %d 分（%s）' % (score, level))
        if warn_reasons:
            verdict_key = 'warn'
            verdict_reason = '；'.join(warn_reasons)
        else:
            verdict_key = 'ok'
            # 绿灯时附带简要扣分说明，让用户知道有小扣分但不影响可用
            if neg_total < 0 or sansha_penalty < 0:
                verdict_reason = ('无一票否决，无重煞叠加（三煞扣分 %d 分 / '
                                  '凶煞扣分 %d 分，已被高分化解）'
                                  % (sansha_penalty, neg_total))
            else:
                verdict_reason = '无一票否决，无重大凶煞叠加'

    # 5) 补救与建议（001 §238.15 对齐阶梯式裁决）
    advice = ''
    if verdict_key == 'veto':
        advice = ('此日课犯 %s 大忌，没有任何制化余地，请立刻另择吉日！'
                  % (veto[0] if veto else ''))
    elif verdict_key == 'warn':
        # 用外层已解析好的 real_heavy / zhen_heavy / _has_luban，不重复定义
        if _has_luban:
            advice = '犯鲁班煞，建议择吉时并依规制化（如动土前祭拜），或另择吉日。'
        elif '燥' in pianku:
            advice = '此日五行过燥，建议配合下午（金水旺）的时辰使用。'
        elif '寒' in pianku:
            advice = '此日五行过寒，建议配合上午（木火旺）的时辰使用。'
        elif real_heavy:
            _hit = zhen_heavy + (['鲁班煞'] if _has_luban else [])
            advice = '本日有真重煞（%s），须确认制化到位方可使用。' % '；'.join(_hit)
        elif sansha_penalty <= -60:
            advice = '三煞扣分较重（%d 分），建议确认制化条件后使用，或另择吉日。' % sansha_penalty
        elif neg_total <= -50:
            advice = '凶煞扣分较重（%d 分），建议另择高分吉日。' % neg_total
        elif '凶' in level:
            advice = '本课总分偏低（%d 分，%s），建议另择高分吉日。' % (score, level)
        else:
            advice = '本日存在扣分项，请结合制化条件酌情使用。'
    else:
        # 绿灯时若有扣分，给友好提示
        if sansha_penalty < 0 or neg_total < 0:
            advice = ('本日有轻微向方扣分（三煞 %d 分 / 凶煞 %d 分），但高分化解，'
                      '可用。建议配合贵人时辰使用。' % (sansha_penalty, neg_total))

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
