# -*- coding: utf-8 -*-
"""
================================================================================
日课校验器（DayLesson Linter）
================================================================================
独立于评分器的【第三方只读校验通道】：

    评分器 → 结构化数据(score_details/marriage_details/shensha_list ...)
                    ↓
              日课校验器（本模块，只读、无共享状态）
                    ↓
              诊断报告（ERROR / WARN / INFO 问题列表 + 出处 + 修复建议）

设计原则（对应 2026-10-02 架构审查）：
1. 规则校验【结构化字段】，不依赖正则匹配渲染文本；少数文案完整性规则
   可选读取 rendered_content（仅兜底）。
2. 规则注册表 RULE_REGISTRY 是唯一来源；新增问题 → 注册一条规则永久生效。
3. ctx.issue 是 Issue 唯一入口，rule_id 必须在注册表白名单，
   禁止散落硬编码（防止"凭空生成扣分理由"式幻觉）。
4. 检查统计由 RULE_FUNCS 常量列表驱动：每条规则
   executed(失败/通过) / skipped 单列，杜绝"文档说13项实际跑12项"的口径漂移。
5. 只读输入 dict，不修改评分结果。

严重级别：
    ERROR  算术错误、逻辑矛盾 —— 应拒绝出报告或显著打标
    WARN   措辞不当、信息遗漏 —— 提示但不阻断
    INFO   可选优化

CLI（CI 集成，退出码 0/1）：
    python -m modules.日课校验器 2026-09-25 嫁娶
================================================================================
"""

from collections import OrderedDict

# ==================== 严重级别 ====================
SEVERITY_ERROR = 'ERROR'
SEVERITY_WARN = 'WARN'
SEVERITY_INFO = 'INFO'
_VALID_SEVERITY = {SEVERITY_ERROR, SEVERITY_WARN, SEVERITY_INFO}

# ==================== 规则注册表（单一来源） ====================
# rule_id -> {'severity': str, 'title': str}
RULE_REGISTRY = OrderedDict()
# (rule_id, rule_fn) 常量列表：执行顺序与统计口径的唯一驱动源
RULE_FUNCS = []


def register_rule(rule_id, severity, title):
    """规则注册装饰器。重复注册或非法级别直接报错（fail fast）。"""
    def _deco(fn):
        if rule_id in RULE_REGISTRY:
            raise ValueError(f'规则重复注册: {rule_id}')
        if severity not in _VALID_SEVERITY:
            raise ValueError(f'规则 {rule_id} 非法级别: {severity}')
        RULE_REGISTRY[rule_id] = {'severity': severity, 'title': title}
        RULE_FUNCS.append((rule_id, fn))
        return fn
    return _deco


# ==================== 问题 / 结果数据结构 ====================

class Issue:
    """单条诊断问题（带证据链：出处 + 修复建议）。"""

    __slots__ = ('rule_id', 'severity', 'message', 'source', 'suggestion')

    def __init__(self, rule_id, severity, message, source='', suggestion=''):
        self.rule_id = rule_id
        self.severity = severity
        self.message = message
        self.source = source
        self.suggestion = suggestion

    def __repr__(self):
        return f'Issue({self.rule_id}, {self.severity}, {self.message!r})'


class LintResult:
    """一次日课校验的聚合结果。"""

    def __init__(self, issues, executed_ids, skipped):
        """
        Args:
            issues: list[Issue]
            executed_ids: 实际执行了的规则 rule_id 列表（顺序同 RULE_FUNCS）
            skipped: [(rule_id, reason)] 前置数据不满足而跳过的规则
        """
        self.issues = issues
        self.executed_ids = executed_ids
        self.skipped = skipped

    @property
    def total_rules(self):
        return len(RULE_FUNCS)

    @property
    def error_count(self):
        return sum(1 for i in self.issues if i.severity == SEVERITY_ERROR)

    @property
    def warn_count(self):
        return sum(1 for i in self.issues if i.severity == SEVERITY_WARN)

    @property
    def info_count(self):
        return sum(1 for i in self.issues if i.severity == SEVERITY_INFO)

    @property
    def failed_rule_ids(self):
        """有 ≥1 个 issue 的规则集合。"""
        return {i.rule_id for i in self.issues}

    @property
    def passed_count(self):
        return len(self.executed_ids) - len(self.failed_rule_ids
                                           & set(self.executed_ids))

    @property
    def has_error(self):
        return self.error_count > 0

    @property
    def passed(self):
        """门禁口径：无 ERROR 即通过（WARN 不阻断）。"""
        return not self.has_error

    def format_text(self):
        """渲染【日课校验】报告段（人读文本）。"""
        lines = []
        lines.append('\n\n【日课校验】')
        lines.append('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        lines.append(
            f"  ✅ 通过 {self.passed_count} 项 · "
            f"❌ 失败 {len(self.failed_rule_ids & set(self.executed_ids))} 项 · "
            f"⏭ 跳过 {len(self.skipped)} 项（共 {self.total_rules} 条规则）"
        )

        def _sev_icon(s):
            return {'ERROR': '⛔', 'WARN': '⚠', 'INFO': 'ℹ'}.get(s, '·')

        # 按注册表顺序输出问题
        order = {rid: i for i, (rid, _) in enumerate(RULE_FUNCS)}
        for issue in sorted(self.issues, key=lambda i: order.get(i.rule_id, 999)):
            lines.append(
                f"  {_sev_icon(issue.severity)} [{issue.severity}] "
                f"{issue.rule_id} {issue.message}"
            )
            if issue.source:
                lines.append(f"      出处：{issue.source}")
            if issue.suggestion:
                lines.append(f"      建议：{issue.suggestion}")

        if self.skipped:
            sk = '、'.join(f'{rid}({r})' for rid, r in self.skipped)
            lines.append(f"  （跳过规则：{sk}）")

        lines.append(
            '  校验结论：' +
            ('❌ 未通过（存在 ERROR，本报告不应直接交付）' if self.has_error
             else ('⚠ 通过但有警告项，建议复核' if self.warn_count else '✅ 通过'))
        )
        return '\n'.join(lines)


# ==================== 校验上下文 ====================

class LintContext:
    """规则函数的运行上下文：持有输入与 issue 唯一入口。"""

    def __init__(self, detail, lucky_hours=None, rendered_content=None,
                 bride_year_zhi=None):
        self.detail = detail if isinstance(detail, dict) else {}
        self.sd = self.detail.get('score_details')
        self.sd = self.sd if isinstance(self.sd, dict) else {}
        self.reason = str(self.detail.get('reason') or '')
        self.lucky_hours = lucky_hours if isinstance(lucky_hours, list) else None
        self.rendered_content = (str(rendered_content)
                                 if rendered_content is not None else None)
        self.bride_year_zhi = bride_year_zhi
        self.issues = []

    def issue(self, rule_id, message, source='', suggestion='', severity=None):
        """Issue 唯一入口：强制 rule_id 白名单校验。
        severity 可覆盖注册级（用于同一规则内“禁用=ERROR/负分=WARN”分级）。"""
        meta = RULE_REGISTRY.get(rule_id)
        if meta is None:
            raise ValueError(f'未注册规则，禁止生成 issue: {rule_id}')
        self.issues.append(Issue(rule_id, severity or meta['severity'], message,
                                 source, suggestion))

    # ---------- 便捷取值 ----------
    @property
    def is_marriage(self):
        return ('嫁娶评分' in self.sd or '嫁娶明细(分项)' in self.sd
                or self.detail.get('marriage_score') is not None)

    @property
    def veto(self):
        return bool(self.detail.get('veto_reasons'))

    @property
    def marriage_details(self):
        md = self.detail.get('marriage_details')
        return md if isinstance(md, list) else []

    @property
    def shensha_list(self):
        sl = self.detail.get('shensha_list')
        return sl if isinstance(sl, list) else []


# ==================== 通用辅助 ====================

_ZHI_ALL = ['子', '丑', '寅', '卯', '辰', '巳',
            '午', '未', '申', '酉', '戌', '亥']

# 三合局：分组串 -> {'ju':局名, 'gong':{支:宫位0长生/1帝旺/2墓}, 'zs':帝旺}
_SANHE = {
    frozenset('申子辰'): {'ju': '水局',
                          'gong': {'申': 0, '子': 1, '辰': 2}, 'zs': '子'},
    frozenset('寅午戌'): {'ju': '火局',
                          'gong': {'寅': 0, '午': 1, '戌': 2}, 'zs': '午'},
    frozenset('巳酉丑'): {'ju': '金局',
                          'gong': {'巳': 0, '酉': 1, '丑': 2}, 'zs': '酉'},
    frozenset('亥卯未'): {'ju': '木局',
                          'gong': {'亥': 0, '卯': 1, '未': 2}, 'zs': '卯'},
}

_LIUHE_PAIRS = {('子', '丑'), ('寅', '亥'), ('卯', '戌'),
                ('辰', '酉'), ('巳', '申'), ('午', '未')}


def _is_liuhe(a, b):
    return (a, b) in _LIUHE_PAIRS or (b, a) in _LIUHE_PAIRS


def _num(v):
    return v if isinstance(v, (int, float)) else 0


def _name_prefix(s):
    """神煞名去括注前缀，用于跨段名称匹配。"""
    return str(s).split('（')[0].split('(')[0].strip()


def _shensha_name_match(n1, n2):
    """两个神煞名是否指向同一项：前缀相同，或互相包含。"""
    a, b = _name_prefix(n1), _name_prefix(n2)
    if not a or not b:
        return False
    return a == b or a in b or b in a


def _expected_level_base(score, wuxing_score=None):
    """按评分器 _get_level 同口径，返回基础等级（不含嫁娶降级后缀）。"""
    if wuxing_score is not None and wuxing_score < 60:
        return '❌ 凶'
    if score >= 105:
        return '★★★★★ 上吉'
    if score >= 100:
        return '★★★★ 大吉'
    if score >= 85:
        return '★★★ 吉'
    if score >= 75:
        return '★★ 中吉'
    if score >= 60:
        return '★ 平'
    return '❌ 凶'


def _resolve_lunar_month_zhi(ctx):
    """从结构化数据解析农历月份（只读，复用四柱计算器农历转换）。"""
    dsize = ctx.detail.get('sizhu')
    d = None
    if isinstance(dsize, dict):
        d = dsize.get('date')
    if d is None:
        d = ctx.detail.get('date')
    if hasattr(d, 'year') and hasattr(d, 'month'):
        try:
            try:
                from .四柱计算器 import get_lunar_date
            except Exception:
                from 四柱计算器 import get_lunar_date
            lun = get_lunar_date(d)
            mc = str(lun.get('month_chinese') or lun.get('month') or '')
            _map = {'正月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5,
                    '六月': 6, '七月': 7, '八月': 8, '九月': 9, '十月': 10,
                    '十一月': 11, '冬月': 11, '腊月': 12,
                    '闰正月': 1, '闰二月': 2, '闰三月': 3, '闰四月': 4,
                    '闰五月': 5, '闰六月': 6, '闰七月': 7, '闰八月': 8,
                    '闰九月': 9, '闰十月': 10, '闰冬月': 11, '闰腊月': 12}
            if mc in _map:
                return _map[mc]
        except Exception:
            return None
    return None


# ==================== 第一类：算术与结构一致性规则 ====================

@register_rule('E001', SEVERITY_ERROR, '总分与各分项之和一致')
def rule_e001(ctx):
    """总分 = 各分项之和；否决日总分强制归零；飞星日按 0.7/0.3 加权式核对。"""
    sd = ctx.sd
    if '总分' not in sd:
        return 'score_details 无总分键'
    reported_total = sd.get('总分')
    result_score = ctx.detail.get('score')

    # 否决日：总分必须强制归零（分项和仅供追溯）
    if ctx.veto:
        if reported_total != 0 or result_score != 0:
            ctx.issue(
                'E001',
                f'一票否决日总分必须为 0：score_details={reported_total}，'
                f'result={result_score}',
                source='score_details[总分]',
                suggestion='否决分支须将总分与 result.score 一并置 0')
        return None

    # 飞星加权日：总分 = 正五行总分×0.7 + (50+飞星评分)×0.3
    if '飞星评分' in sd:
        zhengwu = sd.get('正五行总分')
        fx = sd.get('飞星评分')
        if zhengwu is None or fx is None:
            return '飞星加权数据不完整'
        expected = int(_num(zhengwu) * 0.7 + (50 + _num(fx)) * 0.3)
        if expected != reported_total or result_score != reported_total:
            ctx.issue(
                'E001',
                f'飞星加权总分不一致：按 正五行{zhengwu}×0.7+(50+{fx})×0.3 '
                f'应为 {expected}，score_details={reported_total}，'
                f'result={result_score}',
                source='score_details[飞星评分/正五行总分]',
                suggestion='核对加权系数 0.7/0.3 与取整口径')
        return None

    if ctx.is_marriage:
        keys = ['五行评分', '月令得分', '喜用神得分', '太阳太阴得分']
    else:
        keys = ['五行评分', '月令得分', '喜用神得分', '相主得分',
                '黄道得分', '太阳太阴得分', '三煞扣分']
    missing = [k for k in keys if k not in sd]
    if missing:
        return f'score_details 缺键: {",".join(missing)}'

    expected = sum(_num(sd.get(k)) for k in keys)
    if expected != reported_total:
        ctx.issue(
            'E001',
            f'总分与分项和不一致：分项和={expected}，'
            f'score_details 总分={reported_total}',
            source='score_details：' + '、'.join(
                f'{k}={sd.get(k)}' for k in keys),
            suggestion='核对各分项取数，或在评分器修正计算')
    if result_score != reported_total:
        ctx.issue(
            'E001',
            f'结果分与明细总分不一致：result.score={result_score}，'
            f'score_details={reported_total}',
            source='detail[score] vs score_details[总分]',
            suggestion='两处必须由同一 total_score 回填')
    return None


@register_rule('E002', SEVERITY_ERROR, '等级与总分区间匹配')
def rule_e002(ctx):
    """分数区间→等级映射；嫁娶忌嫁娶日基础等级封顶★平并须带慎用后缀。"""
    score = ctx.detail.get('score')
    if not isinstance(score, (int, float)):
        return 'detail 无 score'
    actual = str(ctx.detail.get('level') or '')
    actual_base = actual.split('（')[0].strip()

    # 否决日等级必须为凶
    if ctx.veto:
        if actual_base != '❌ 凶':
            ctx.issue(
                'E002',
                f'否决日等级应为 ❌ 凶，实际为 {actual}',
                source='detail[level]',
                suggestion='否决分支 level 固定为 ❌ 凶')
        return None

    wuxing = ctx.sd.get('五行评分')
    expected_base = _expected_level_base(score, wuxing)

    # 嫁娶硬禁忌封顶：明细含"忌嫁娶" → 基础等级 ≤ ★ 平
    capped = False
    if ctx.is_marriage:
        capped = any(
            '忌嫁娶' in str(d[0])
            for d in ctx.marriage_details
            if isinstance(d, (list, tuple)) and len(d) >= 1)
        if capped:
            exp_stars = expected_base.count('★')
            if exp_stars > 1:
                expected_base = '★ 平'

    if actual_base != expected_base:
        ctx.issue(
            'E002',
            f'等级与总分不匹配：{score:g} 分应为「{expected_base}」，'
            f'实际为「{actual_base}」',
            source='detail[level]',
            suggestion='等级必须是总分的纯函数（阈值 105/100/85/75/60）')

    # 封顶时必须带「（犯忌嫁娶，慎用）」后缀
    if capped and '犯忌嫁娶' not in actual:
        ctx.issue(
            'E002',
            f'因忌嫁娶降为平的等级须带「犯忌嫁娶，慎用」后缀，实际：{actual}',
            source='detail[level]',
            suggestion='等级追加（犯忌嫁娶，慎用）标注')
    return None


@register_rule('E003', SEVERITY_ERROR, '利月判断与新娘年支/农历月份一致')
def rule_e003(ctx):
    """新娘年支×农历月 → 大利月/小利月/普通月，须与神煞列表一致。"""
    if not ctx.is_marriage:
        return '非嫁娶路径'
    bz = ctx.bride_year_zhi
    if not bz:
        return '缺新娘年支'
    month = _resolve_lunar_month_zhi(ctx)
    if not month:
        return '无法解析农历月份'

    table = {
        '子': {'大利月': [6, 12], '小利月': [2, 8]},
        '午': {'大利月': [6, 12], '小利月': [2, 8]},
        '丑': {'大利月': [5, 11], '小利月': [4, 10]},
        '未': {'大利月': [5, 11], '小利月': [4, 10]},
        '寅': {'大利月': [2, 8], '小利月': [1, 7]},
        '申': {'大利月': [2, 8], '小利月': [1, 7]},
        '卯': {'大利月': [1, 7], '小利月': [6, 12]},
        '酉': {'大利月': [1, 7], '小利月': [6, 12]},
        '辰': {'大利月': [4, 10], '小利月': [3, 9]},
        '戌': {'大利月': [4, 10], '小利月': [3, 9]},
        '巳': {'大利月': [3, 9], '小利月': [5, 11]},
        '亥': {'大利月': [3, 9], '小利月': [5, 11]},
    }
    info = table.get(bz)
    if not info:
        return f'未知新娘年支: {bz}'
    if month in info['大利月']:
        expected = '大利月'
    elif month in info['小利月']:
        expected = '小利月'
    else:
        expected = '普通月'

    ss_names = [_name_prefix(s.get('name', ''))
                for s in ctx.shensha_list if isinstance(s, dict)]
    has_dali = any('大利月' in n for n in ss_names)
    has_xiaoli = any('小利月' in n for n in ss_names)

    if expected == '大利月' and not has_dali:
        ctx.issue(
            'E003',
            f'新娘{bz}农历{month}月应为大利月，神煞列表未列大利月',
            source='shensha_list / 新娘年支 × 农历月',
            suggestion='按高精度农历月份补大利月条目（+30）')
    elif expected == '小利月' and not has_xiaoli:
        ctx.issue(
            'E003',
            f'新娘{bz}农历{month}月应为小利月，神煞列表未列小利月',
            source='shensha_list / 新娘年支 × 农历月',
            suggestion='补小利月条目（+15）')
    elif expected == '普通月' and (has_dali or has_xiaoli):
        ctx.issue(
            'E003',
            f'新娘{bz}农历{month}月为普通月，神煞列表却列'
            f'{"大利月" if has_dali else "小利月"}',
            source='shensha_list / 新娘年支 × 农历月',
            suggestion='利月判定须按真实农历月，节气月与农历月错位日尤须注意')
    return None


@register_rule('E004', SEVERITY_ERROR, '推荐时柱在时辰表中不禁用')
def rule_e004(ctx):
    """推荐时柱对应时辰不得为禁用；负分须 WARN 提示。"""
    if ctx.lucky_hours is None:
        return '缺十二时辰表数据'
    dsize = ctx.detail.get('sizhu')
    hour_zhi = None
    if isinstance(dsize, dict):
        hp = dsize.get('时柱')
        if isinstance(hp, str) and len(hp) >= 2:
            hour_zhi = hp[1]
    if not hour_zhi:
        hour_zhi = dsize.get('hour_zhi') if isinstance(dsize, dict) else None
    if not hour_zhi:
        return '缺推荐时柱'

    item = next((h for h in ctx.lucky_hours
                 if isinstance(h, dict) and h.get('地支') == hour_zhi), None)
    if not item:
        ctx.issue(
            'E004',
            f'推荐时柱地支「{hour_zhi}」在时辰表中无对应条目',
            source='sizhu[时柱] vs lucky_hours',
            suggestion='时辰表须覆盖全部十二地支')
        return None

    if item.get('禁用'):
        ctx.issue(
            'E004',
            f'推荐时柱「{hour_zhi}」在时辰表中标记为禁用：'
            f'{"、".join(item.get("说明", []))}',
            source=f'lucky_hours[{hour_zhi}]',
            suggestion='推荐时柱不得取禁用时辰，应改选吉时')
    elif _num(item.get('分值')) < 0:
        # 负分按本规则文档口径为 WARN（时辰表与推荐时柱本为两套标准，
        # 推荐柱在表中负分提示但不阻断交付；“禁用”才是 ERROR）
        ctx.issue(
            'E004',
            f'推荐时柱「{hour_zhi}」时辰表评分为负（{item.get("分值")}分）：'
            f'{"、".join(item.get("说明", []))}',
            source=f'lucky_hours[{hour_zhi}]',
            suggestion='推荐时柱宜取正分吉时',
            severity=SEVERITY_WARN)
    return None


@register_rule('E005', SEVERITY_ERROR, '宜项与忌项不包含同一事项')
def rule_e005(ctx):
    """yi ∩ ji = 空集（精确匹配 + 事项词包含双重检查）。"""
    yi = [str(y).strip() for y in (ctx.detail.get('yi_list') or []) if y]
    ji = [str(j).strip() for j in (ctx.detail.get('ji_list') or []) if j]
    if not yi and not ji:
        return '宜忌列表均为空'

    overlaps = []
    yi_set, ji_set = set(yi), set(ji)
    for common in yi_set & ji_set:
        overlaps.append(common)
    # 事项词包含检查（如 宜：嫁娶 vs 忌：小黄道执日忌嫁娶）
    for y in yi:
        if y in ('嫁娶',) and any(y in j for j in ji):
            if y not in overlaps:
                overlaps.append(f'{y}（忌项提及）')
    if overlaps:
        ctx.issue(
            'E005',
            f'宜忌冲突，同一事项同时出现：{"、".join(overlaps)}',
            source=f'yi_list={yi} / ji_list={ji}',
            suggestion='犯硬禁忌时须从宜项移除该事项，保持双向清晰')
    return None


@register_rule('E006', SEVERITY_ERROR, '综合判断口径与等级一致')
def rule_e006(ctx):
    """平（慎用）→ 综合判断须含慎用且不得写嫁娶可用；凶→须含不宜。"""
    if not ctx.is_marriage:
        return '非嫁娶路径'
    if ctx.detail.get('veto_reasons'):
        return '一票否决日，reason 为否决词，无综合判断段'
    level = str(ctx.detail.get('level') or '')
    # 提取综合判断句（按行取，行内"；"皆属该句成分，不得截断——
    # 2026-10-03 修复：凶慎用句"不宜嫁娶；如确需使用…"被截断致误报）
    sentence = ''
    for line in ctx.reason.split('\n'):
        if '综合判断' in line:
            sentence = line.strip()
            break

    if not sentence:
        ctx.issue(
            'E006',
            '综合评语缺少「综合判断：……」结论句',
            source='detail[reason]',
            suggestion='嫁娶评语末尾必须给出 可用/慎用/不宜 明确结论')
        return None

    # 禁用/凶级（含 ❌ 前缀）
    if '❌' in level or ctx.veto:
        # 统一底线：凶级不得写"嫁娶可用"（无论带不带制化说明）
        if '嫁娶可用' in sentence:
            ctx.issue(
                'E006',
                f'等级为「{level}」但综合判断写「嫁娶可用」：{sentence}',
                source='detail[level] vs reason 综合判断句',
                suggestion='凶级禁用日应写「不宜嫁娶」')
        if '不宜' not in sentence:
            ctx.issue(
                'E006',
                f'等级为「{level}」但综合判断未写「不宜」：{sentence}',
                source='detail[level] vs reason 综合判断句',
                suggestion='凶日结论须含「不宜嫁娶」')
        # 区分：凶（慎用）须同时有"不宜"和"制化/择吉"；纯凶只须"不宜"
        if '慎用' in level and '不宜' in sentence:
            if not ('制化' in sentence or '择吉' in sentence or '另择' in sentence):
                ctx.issue(
                    'E006',
                    f'等级为「{level}」但综合判断缺制化/择吉说明：{sentence}',
                    source='detail[level] vs reason 综合判断句',
                    suggestion='凶（慎用）日须写"不宜嫁娶；如确需使用，须严格制化并择吉时"')
    elif '犯忌嫁娶' in level:
        # 仅针对"平（犯忌嫁娶，慎用）"封顶日——
        # 纯平级（★ 平，无犯忌后缀）吉神到位时写"嫁娶可用"是允许的（score>=60）
        if '慎用' not in sentence:
            ctx.issue(
                'E006',
                f'等级为「{level}」而综合判断未写「慎用」：{sentence}',
                source='detail[level] vs reason 综合判断句',
                suggestion='口径统一为「嫁娶须慎用，宜择吉时」')
        if '嫁娶可用' in sentence and '须慎用' not in sentence:
            ctx.issue(
                'E006',
                f'等级为「{level}」而综合判断写「嫁娶可用」：{sentence}',
                source='detail[level] vs reason 综合判断句',
                suggestion='删除「嫁娶可用」措辞，与等级口径一致')
    return None


@register_rule('E007', SEVERITY_ERROR, '神煞段负分项与评分明细一致')
def rule_e007(ctx):
    """嫁娶路径：评分负分项 ↔ 神煞列表双向可追溯（利月类由 E003 校验，豁免）。"""
    if not ctx.is_marriage:
        return '非嫁娶路径（通用路径神煞已含于五行评分，无逐项映射）'

    md_neg = [d for d in ctx.marriage_details
              if isinstance(d, (list, tuple)) and len(d) >= 2
              and isinstance(d[1], (int, float)) and d[1] < 0
              and _name_prefix(d[0]) != '基础分']
    ss_items = [s for s in ctx.shensha_list if isinstance(s, dict)]
    _LIYUE = ('大利月', '小利月')

    # 正向：评分扣了 → 神煞段必须有
    for d in md_neg:
        name = str(d[0])
        found = any(_shensha_name_match(name, s.get('name', ''))
                    for s in ss_items)
        if not found:
            ctx.issue(
                'E007',
                f'评分明细负分项「{name}」在神煞信息段缺失',
                source=f'marriage_details（{d[1]:g}分） vs shensha_list',
                suggestion='非veto分支须回填 marriage_details 负分项到 shensha_list')

    # 反向：神煞段负分条目 → 评分明细必须有出处（利月豁免）
    for s in ss_items:
        score = s.get('score', 0)
        name = str(s.get('name', ''))
        if not isinstance(score, (int, float)) or score >= 0:
            continue
        if _name_prefix(name) in _LIYUE or '利月' in name:
            continue
        found = any(_shensha_name_match(name, d[0]) for d in md_neg)
        if not found:
            ctx.issue(
                'E007',
                f'神煞信息段条目「{name}」在评分明细中无对应负分项',
                source=f'shensha_list（{score:g}分） vs marriage_details',
                suggestion='神煞段条目必须能在评分明细找到出处，禁止凭空列煞')
    return None


_YIJI_EVENT_WORDS = None


def _is_xiansha_name(item, event=None):
    """E008 反向判定：忌项名是否煞名（而非黄历宜忌事项词）。

    不硬编码事项词典——复用今日黄历.YIJI_60（六十甲子日宜忌表）的
    宜/忌词全集 + 当前事项名反查（开业规则 L246-248 append 的
    开业/开市/纳财同属黄历忌事项词，词表与煞名集语义不相交）：
    - 在词集中 → 黄历事项词，无"煞名出处"可言，E008 跳过
    - 不在词集中 → 按煞名处理，继续出处检查
      （黄沙/红纱等"出现在忌项就必须有扣分"的真煞仍被抓，安全阀不阉割；
       切勿改用"是否在评分明细/神煞段"来判煞名——那是 E008 要检查的出处本身，
       会把真煞无出处误判为非煞名）
    今日黄历不可用时词集为空 → 全部按煞名处理（保守降级，等同修复前行为）。
    """
    global _YIJI_EVENT_WORDS
    if _YIJI_EVENT_WORDS is None:
        words = set()
        try:
            from modules.今日黄历 import YIJI_60 as _y60
            for _yi, _ji in _y60.values():
                words.update(str(w) for w in _yi)
                words.update(str(w) for w in _ji)
        except ImportError:
            pass  # 保守降级：词集为空 = 全按煞名检查（宁多查不漏抓）
        _YIJI_EVENT_WORDS = words
    if event and str(item) == str(event):
        return False
    return str(item) not in _YIJI_EVENT_WORDS


@register_rule('E008', SEVERITY_WARN, '忌项煞名在评分或神煞段有出处')
def rule_e008(ctx):
    """忌项煞名须能在评分负分项/神煞列表找到，或属结构性硬规则白名单。

    2026-10-05 两类非嫁娶误报修复（用户裁决，2026-02-08 开业案例）：
    1. 事项名误报（开业/开市/纳财）：_is_xiansha_name 反向判定，黄历事项词跳过
    2. veto 日假阳性（年三煞(日柱)）：一票否决日报告砍为单行，
       评分明细/神煞段不存在；扩到渲染全文查出处——只扩范围，不取消检查
    """
    ji = [str(j).strip() for j in (ctx.detail.get('ji_list') or []) if j]
    if not ji:
        return '忌项为空'

    sources = [str(d[0]) for d in ctx.marriage_details
               if isinstance(d, (list, tuple)) and len(d) >= 1]
    sources += [str(s.get('name', '')) for s in ctx.shensha_list
                if isinstance(s, dict)]
    # 山向中心事项（安葬/修造等）三煞独立扣分通道：不进 marriage_details/
    # shensha_list，曾致真煞"年三煞(日柱)"被误报无出处；明细行含忌项名作子串。
    _sd = ctx.detail.get('score_details') if isinstance(
        ctx.detail.get('score_details'), dict) else None
    if _sd:
        sources += [str(x) for x in (_sd.get('三煞扣分明细') or [])]
    veto_srcs = [str(v) for v in (ctx.detail.get('veto_reasons') or [])]
    sources += veto_srcs

    # 结构性硬规则来源（规则检查器 deterministic 产出，非神煞扣分项）
    # 注意：黄沙/红纱不在其列——它们出现在忌项就必须有扣分，正是 E008 要抓的问题。
    _STRUCT_PREFIXES = ('建除', '月破', '岁破', '日破', '四离', '四绝',
                        '重丧', '三娘', '杨公', '冲',
                        '阴胎', '阳气', '夫星', '子星')
    is_veto = bool(veto_srcs)
    _event = ctx.detail.get('event') or ctx.detail.get('事项')

    for item in ji:
        if item in veto_srcs:
            continue
        if not _is_xiansha_name(item, _event):
            continue  # 黄历事项词（开业/开市/纳财…），非煞名，无出处可言
        hit = any(_shensha_name_match(item, src) for src in sources)
        if not hit:
            hit = any(item.startswith(p) or p in item
                      for p in _STRUCT_PREFIXES)
        if not hit and is_veto:
            # 一票否决日：报告砍为单行，评分明细/神煞段不存在；
            # 扩到渲染全文查出处（煞名在全文中出现即有出处）
            hit = bool(ctx.reason) and item in ctx.reason
        if not hit:
            ctx.issue(
                'E008',
                f'忌项「{item}」在评分明细与神煞信息段均无出处',
                source='detail[ji_list]',
                suggestion='若确为凶煞须补扣分并列神煞；否则从忌项删除')
    return None


@register_rule('E207', SEVERITY_ERROR, '时柱自述已含与地支关系恒等式一致')
def rule_e207(ctx):
    """时柱关系块自述“已计入五行评分·地支关系得分”时，用八字工具整合原语
    独立重算四柱六对合计，须与 breakdown 地支关系得分一致；防止“自述已含、
    实际未计/重复计”（Q5，2026-10-08 拍板）。

    分值口径与评分器 _calc_all_zhi_relations_detail 一致：
        六合+8/半合+6/六冲-15/六害-6/相刑-8/相破-4；伏吟0分。
    枚举与原语调用在本规则内独立完成，不读取评分器算出的明细。

    嫁娶路径不适用（2026-10-08 拍板，裁定1=B）：该路径
    score_breakdown 结构性为空 dict（评分器.py 正常/否决两路径硬置），
    且合局分值家族不同（嫁娶六合+10/半合+8，本规则+8/+6），
    即使补字段也无法对账。明确跳过而非"缺键被动跳过"，不再假装检查；
    分值家族统一随"两套评分架构"另案处理，到期改回本规则覆盖。
    """
    if 'marriage_details' in ctx.detail:
        return '嫁娶路径不适用（无恒等式，2026-10-08拍板，随架构另案统一）'

    sz = ctx.detail.get('sizhu')
    if not isinstance(sz, dict):
        return '无四柱结构数据'
    zhis = []
    for k in ('年柱', '月柱', '日柱', '时柱'):
        v = str(sz.get(k) or '')
        if len(v) == 2:
            zhis.append(v[1])
    if len(zhis) != 4:
        return '四柱地支不全'
    try:
        from .八字工具整合 import (check_liuhe, check_liuchong, check_liuhai,
                                   check_xing, check_po)
    except ImportError:
        from 八字工具整合 import (check_liuhe, check_liuchong, check_liuhai,
                                  check_xing, check_po)

    # 半合：同一三合局内两支不同（与评分器 _check_banhe 同定义，此处独立枚举）
    _SANHE_GROUPS = (('申', '子', '辰'), ('寅', '午', '戌'),
                     ('巳', '酉', '丑'), ('亥', '卯', '未'))

    def _is_banhe(a, b):
        if a == b:
            return False
        return any(a in g and b in g for g in _SANHE_GROUPS)

    calc = 0
    for i in range(4):
        for j in range(i + 1, 4):
            a, b = zhis[i], zhis[j]
            if check_liuhe(a, b):
                calc += 8
            elif _is_banhe(a, b):
                calc += 6
            if check_liuchong(a, b):
                calc -= 15
            if check_liuhai(a, b):
                calc -= 6
            if check_xing(a, b):
                calc -= 8
            if check_po(a, b):
                calc -= 4

    wxr = ctx.detail.get('wu_xing_result')
    bd = wxr.get('score_breakdown') if isinstance(wxr, dict) else None
    bd = bd if isinstance(bd, dict) else {}
    claimed = bd.get('地支关系得分')
    if claimed is None:
        return '无五行恒等式地支关系分项'
    if int(claimed) != calc:
        ctx.issue(
            'E207',
            f'地支关系恒等式不符：独立重算六对合计 {calc:+d}，'
            f'breakdown 记 {int(claimed):+d}',
            source='八字工具整合原语重算 vs wu_xing_result.score_breakdown',
            suggestion='核对时柱关系是否漏计或重复计')

    # 自述措辞一致性：渲染文本存在时柱关系块时，须注明“已计入”
    text = ctx.rendered_content
    if text and '时柱地支关系' in text:
        if '已计入五行评分·地支关系得分' not in text:
            ctx.issue(
                'E207',
                '时柱关系块未注明“已计入五行评分·地支关系得分”',
                source='rendered_content',
                suggestion='统一时柱关系块措辞，避免误读为独立分项')
    return None


# ============ 第二类（命理规则）：本次手工 bug 永久回归规则 ============

@register_rule('E101', SEVERITY_ERROR, '三合/半合/拱合术语与地支组合匹配')
def rule_e101(ctx):
    """拱合(a,b，拱c)：c须为帝旺且a,b居长生/墓；半合(a,b半合，缺c)：c须为第三支。"""
    if not ctx.is_marriage:
        return '非嫁娶路径'
    import re

    for d in ctx.marriage_details:
        if not (isinstance(d, (list, tuple)) and len(d) >= 1):
            continue
        name = str(d[0])
        # 拱合局(a,b，拱c)
        m = re.search(r'拱合局\((\S)\s*[,，]\s*(\S)\S*?拱(\S)\)', name)
        if m:
            a, b, c = m.group(1), m.group(2), m.group(3)
            pair = {a, b}
            group = next((g for g in _SANHE if pair < g), None)
            if group is None:
                ctx.issue(
                    'E101',
                    f'「{name}」中 {a}{b} 不属于任何三合局',
                    source=f'marriage_details[{name}]',
                    suggestion='核对地支组合')
                continue
            gong = _SANHE[group]['gong']
            if c in pair:
                ctx.issue(
                    'E101',
                    f'「{name}」拱出的「{c}」已在 {a}{b} 之中（不能拱自身局内支）',
                    source=f'marriage_details[{name}]',
                    suggestion=f'寅午类长生+帝旺组合应称半合、缺{next(iter(group - pair))}，'
                               f'不得称拱合')
                continue
            # 2026-11-22 用户审查新增：被拱支若已在日课四柱中，则三合齐全，
            # 应称"三合局"而非"拱合局"（如亥卯未齐全却写"拱合局(亥,未，拱卯)"）
            _sizhu = ctx.detail.get('sizhu') or {}
            _zhis_in_pillars = {str(_sizhu.get(k, ''))[-1:]
                                for k in ('年柱', '月柱', '日柱', '时柱')
                                if _sizhu.get(k)}
            if c in _zhis_in_pillars:
                ctx.issue(
                    'E101',
                    f'「{name}」所拱「{c}」已在日课四柱中，'
                    f'{a}{b}{c}三字齐全，应称「三合局」而非「拱合局」',
                    source=f'marriage_details[{name}]',
                    suggestion=f'改为 三合局({a},{c},{b})；若因推荐时柱注入导致，'
                               f'需重算 marriage_details')
                continue
            if c != _SANHE[group]['zs']:
                ctx.issue(
                    'E101',
                    f'「{name}」应拱帝旺「{_SANHE[group]["zs"]}」而非「{c}」',
                    source=f'marriage_details[{name}]',
                    suggestion='拱合拱的是三合局帝旺（中神）')
                continue
            positions = sorted([gong.get(a), gong.get(b)])
            if positions != [0, 2]:
                ctx.issue(
                    'E101',
                    f'「{name}」{a}{b} 宫位为 {positions}，非长生+墓，不应称拱合',
                    source=f'marriage_details[{name}]',
                    suggestion='长生+帝旺/帝旺+墓称半合；仅长生+墓称拱合')
            continue

        # 半合局(a,b半合，缺c)
        m = re.search(r'半合局\((\S)\s*[,，]\s*(\S)半合[，,]缺(\S)\)', name)
        if m:
            a, b, c = m.group(1), m.group(2), m.group(3)
            pair = {a, b}
            group = next((g for g in _SANHE if pair < g), None)
            if group is None:
                ctx.issue(
                    'E101',
                    f'「{name}」中 {a}{b} 不属于任何三合局',
                    source=f'marriage_details[{name}]',
                    suggestion='核对地支组合')
                continue
            real_missing = group - pair
            if c not in real_missing:
                ctx.issue(
                    'E101',
                    f'「{name}」{a}{b} 所缺为「{next(iter(real_missing))}」'
                    f'而非「{c}」',
                    source=f'marriage_details[{name}]',
                    suggestion='缺支必须是三合局第三支')
                continue
            positions = sorted([_SANHE[group]['gong'][a],
                                _SANHE[group]['gong'][b]])
            if positions == [0, 2]:
                ctx.issue(
                    'E101',
                    f'「{name}」{a}{b} 为长生+墓（拱合位），不应称半合',
                    source=f'marriage_details[{name}]',
                    suggestion=f'改为 拱合局({a},{b}，拱{_SANHE[group]["zs"]})')
    return None


@register_rule('E102', SEVERITY_ERROR, '时辰六合关系不得误标为破')
def rule_e102(ctx):
    """时支与日课支为六合时，时辰说明不得出现针对该支的"破"标注。"""
    if ctx.lucky_hours is None:
        return '缺十二时辰表数据'
    dsize = ctx.detail.get('sizhu')
    course_zhi = {}
    if isinstance(dsize, dict):
        for pn in ('年柱', '月柱', '日柱'):
            p = dsize.get(pn)
            if isinstance(p, str) and len(p) >= 2:
                course_zhi[pn] = p[1]

    import re

    def _po_target(rel):
        """解析破注所针对的目标支：破X支（时支破目标支）→ 取括号内"破"后的支。"""
        m = re.search(r'[（(][^）)]*破(\S)[）)]', rel)
        if m and m.group(1) in _ZHI_ALL:
            return m.group(1)
        # 无括注时按 破年支/破月支/破日支 标签定位
        for _label, _z in course_zhi.items():
            if f'破{_label.replace("柱", "支")}' in rel:
                return _z
        return None

    for h in ctx.lucky_hours:
        if not isinstance(h, dict):
            continue
        hz = h.get('地支', '')
        rels = [str(r) for r in h.get('说明', [])]
        po_rels = [r for r in rels if '破' in r]
        for pn, z in course_zhi.items():
            # 仅当该破注的【目标支正是与 hour 六合的那一支】才报错——
            # hour 与日柱六合、同时与年支相破是两类并存关系，不得以"任意破"误判。
            if _is_liuhe(hz, z):
                bad = [r for r in po_rels if _po_target(r) == z]
                if bad:
                    ctx.issue(
                        'E102',
                        f'{h.get("天干","")}{hz}时与{pn}{z}为六合，'
                        f'时辰说明却出现针对{z}的「破」标注：{"、".join(bad)}',
                        source=f'lucky_hours[{hz}] 说明',
                        suggestion='六合优先于相破，应标六合，删除该破注')
    return None


@register_rule('E103', SEVERITY_ERROR, '月令评语与日主旺衰段同源')
def rule_e103(ctx):
    """旺衰句 得令而旺/得生而相 ↔ 评语月令句 得令/得生 必须一致。"""
    if ctx.detail.get('veto_reasons'):
        return '一票否决日，reason 为否决词，无月令段'
    wxr = ctx.detail.get('wu_xing_result')
    wang = ''
    if isinstance(wxr, dict):
        wd = wxr.get('details')
        if isinstance(wd, dict):
            wang = str(wd.get('日主旺衰') or '')

    # 提取评语中的月令句
    yue_sentence = ''
    for seg in ctx.reason.replace('\n', '；').split('；'):
        if seg.strip().startswith('月令：'):
            yue_sentence = seg.strip()
            break

    if not wang:
        return '缺结构化日主旺衰文本'
    if not yue_sentence:
        ctx.issue(
            'E103',
            '综合评语缺少「月令：……」句，与旺衰段无法对账',
            source='wu_xing_result.details[日主旺衰] vs reason',
            suggestion='评语须按月令旺衰同源措辞')
        return None

    if '得令而旺' in wang:
        if '得令' not in yue_sentence:
            ctx.issue(
                'E103',
                f'旺衰段为「得令而旺」，月令评语却为「{yue_sentence}」',
                source='旺衰段 vs reason 月令句',
                suggestion='旺地应写「得令得助，日主旺相」')
    elif '得生而相' in wang:
        if '得生' not in yue_sentence or '得令' in yue_sentence:
            ctx.issue(
                'E103',
                f'旺衰段为「得生而相」，月令评语却为「{yue_sentence}」',
                source='旺衰段 vs reason 月令句',
                suggestion='相地（如酉月壬水）应写「得生得助，日主相旺」，'
                           '不得写「得令」')
    elif '失令偏弱' in wang or '日主休' in wang:
        # 仅拦截"明确旺断"固定措辞；'休囚泄气，得生扶有根不弱'这类
        # 有保留的软描述不属矛盾，不得以'得生'子串误判。
        # （2026-10-15 S2：匹配词随旺衰文案十二长生口径同步，
        #   囚/死档新文案以"失令偏弱"收尾、休档以"日主休"收尾。）
        if ('得令' in yue_sentence or '日主旺相' in yue_sentence
                or '日主相旺' in yue_sentence):
            ctx.issue(
                'E103',
                f'旺衰段为「{wang}」，月令评语却为「{yue_sentence}」',
                source='旺衰段 vs reason 月令句',
                suggestion='失令偏弱/日主休不得写得令/旺相')
    return None


@register_rule('E104', SEVERITY_WARN, '综合评语地支合局覆盖评分合局项')
def rule_e104(ctx):
    """评分中的三合/半合/拱合/六合吉项，评语「地支合局」句均须列出。"""
    if not ctx.is_marriage:
        return '非嫁娶路径'
    if ctx.detail.get('veto_reasons'):
        return '一票否决日，reason 为否决词，无评语段'

    good_terms = []
    for d in ctx.marriage_details:
        if not (isinstance(d, (list, tuple)) and len(d) >= 2):
            continue
        if not (isinstance(d[1], (int, float)) and d[1] > 0):
            continue
        nm = str(d[0])
        if any(k in nm for k in ('三合', '半合', '拱合', '六合')):
            good_terms.append(nm)
    if not good_terms:
        return '评分无合局项'

    # 按行提取，截取"地支合局"到"地支冲害"之间的全部内容——
    # 2026-10-03 修复：原按"；"截断，"地支合局：A；B"中 B 丢失致误报
    heju_sentence = ''
    for line in ctx.reason.split('\n'):
        if '地支合局' in line:
            seg = line[line.index('地支合局'):]
            if '地支冲害' in seg:
                seg = seg[:seg.index('地支冲害')]
            heju_sentence = seg
            break
    if not heju_sentence:
        ctx.issue(
            'E104',
            f'评语无「地支合局」句，评分合局项遗漏：'
            f'{"、".join(good_terms)}',
            source='marriage_details 合局正分项 vs reason',
            suggestion='评语地支合局句须列出全部合局（含年日半合）')
        return None

    import re
    for term in good_terms:
        zhis_in_term = [c for c in term if c in _ZHI_ALL]
        if not all(z in heju_sentence for z in zhis_in_term[:2]):
            ctx.issue(
                'E104',
                f'评分合局项「{term}」未在评语地支合局句列出',
                source='marriage_details vs reason 地支合局句',
                suggestion='合局信息不得遗漏（如年日寅午半合）')
    return None


@register_rule('E105', SEVERITY_WARN, '因嫁娶禁忌降格/降星时报告须有说明')
def rule_e105(ctx):
    """因嫁娶禁忌等级被下调的日课，渲染文本须含下调说明（两级，2026-10-08拍板）。

    一级（level 含"犯忌嫁娶"，封顶★平）：评语须含"降格"说明；
    二级（level 含"降一格"，降星）：评语须含"降星"说明。
    等级行自身后缀（犯忌嫁娶/降一格）不含"降格/降星"，故检查不会恒真；
    说明句由评分器 _build_marriage_reason_tail 末尾生成。
    """
    level = str(ctx.detail.get('level') or '')
    is_l1 = '犯忌嫁娶' in level
    is_l2 = (not is_l1) and ('降一格' in level)
    if not is_l1 and not is_l2:
        return '未因嫁娶禁忌降格/降星'

    text = ctx.rendered_content if ctx.rendered_content is not None else ctx.reason
    if is_l1:
        _need = '降格'
        _kind = '一级封顶（犯嫁娶大忌）'
    else:
        _need = '降星'
        _kind = '二级降星（闭日、夫星等小忌）'
    if _need not in text:
        ctx.issue(
            'E105',
            f'等级已按{_kind}下调，但报告缺少「{_need}」说明',
            source='level vs 渲染文本',
            suggestion=f'综合评语补等级{_need}原因，避免等级与评语脱节')
    return None


# ==================== 对外入口 ====================

def lint_lesson(detail, lucky_hours=None, rendered_content=None,
                bride_year_zhi=None):
    """对一份评分器结构化结果执行全部已注册规则。

    Args:
        detail: Scorer.score() 返回的完整 dict（只读）
        lucky_hours: 十二时辰表（主程序渲染时已生成的 get_lucky_hours 结果）；
                     None 则依赖时辰表的规则记为 skipped
        rendered_content: 渲染后完整文本（仅文案兜底类规则使用）
        bride_year_zhi: 新娘年支（利月规则需要）

    Returns:
        LintResult
    """
    ctx = LintContext(detail, lucky_hours=lucky_hours,
                      rendered_content=rendered_content,
                      bride_year_zhi=bride_year_zhi)
    executed_ids = []
    skipped = []
    for rule_id, fn in RULE_FUNCS:
        skip_reason = fn(ctx)
        if skip_reason:
            skipped.append((rule_id, str(skip_reason)))
        else:
            executed_ids.append(rule_id)

    return LintResult(ctx.issues, executed_ids, skipped)


# ==================== CLI（CI 集成，退出码 0/1） ====================

def _main_cli(argv):
    """python -m modules.日课校验器 YYYY-MM-DD 嫁娶"""
    import datetime as _dt
    if len(argv) < 2:
        print('用法: python -m modules.日课校验器 YYYY-MM-DD [事项]')
        return 1
    try:
        d = _dt.datetime.strptime(argv[0], '%Y-%m-%d').date()
    except ValueError:
        print(f'日期格式错误: {argv[0]}（应为 YYYY-MM-DD）')
        return 1
    event = argv[1] if len(argv) >= 2 else '嫁娶'

    from .四柱计算器 import calculate_sizhu
    from .评分器 import Scorer
    owners = [
        {'name': '欢', 'role': '新娘', '性别': '女', 'birth_date': '1999-04-05'},
        {'name': '文旺', 'role': '新郎', '性别': '男', 'birth_date': '1998-10-13'},
    ]
    sizhu = calculate_sizhu(d, 12, 0)
    sizhu['date'] = d
    sizhu['year'] = d.year
    sizhu['month'] = d.month
    sizhu['day'] = d.day
    result = Scorer().score(sizhu, event, owners=owners)

    # 与主程序完全同口径：重选最佳时柱（午时初值→12时辰实评择优）。
    # 直接复用 ZeriApp._rescan_best_hour，避免CLI与GUI两套逻辑漂移。
    import os as _os
    import sys as _sys
    _root_dir = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    if _root_dir not in _sys.path:
        _sys.path.insert(0, _root_dir)
    try:
        import tkinter as _tk
        _root = _tk.Tk()
        _root.withdraw()
        import 主程序 as _appmod
        _app = _appmod.ZeriApp(_root)
        sizhu, result = _app._rescan_best_hour(
            d, event, owners, None, None, None, None, None, None, sizhu, result)
        _root.destroy()
    except Exception as e:
        print(f'(重选最佳时柱失败，回退午时结果: {type(e).__name__}: {e})')

    # 构造时辰表（与主程序详情渲染同源；以最终时柱为准）
    lucky_hours = None
    bride_year_zhi = None
    if event in ('嫁娶', '订婚', '纳采'):
        bride_year_zhi = '卯'
        try:
            from .推荐时柱 import build_checker
            ck, _ = build_checker(event, None, '')
            lucky_hours = ck.get_lucky_hours(result.get('sizhu') or sizhu)
        except Exception as e:
            print(f'(时辰表构造失败，相关规则将跳过: {e})')

    lint = lint_lesson(result, lucky_hours=lucky_hours,
                       bride_year_zhi=bride_year_zhi)
    print(lint.format_text())
    return 0 if lint.passed else 1


if __name__ == '__main__':
    import sys
    sys.exit(_main_cli(sys.argv[1:]))


# ==================== 阶段四：LLM 高频问题固化（E201-E203） ====================
# 从真基线数据中提取的稳定硬规则，降低对 LLM 的依赖。

@register_rule('E201', SEVERITY_ERROR, '嫁娶路径综合判断句必须有明确结论')
def rule_e201(ctx):
    """嫁娶路径的综合判断句须含"可用/慎用/不可用/不宜"明确结论。"""
    # 嫁娶路径判定：detail 含 marriage_details（嫁娶专属）或 yi_list 含嫁娶
    _yi = ctx.detail.get('yi_list') or []
    _md = ctx.detail.get('marriage_details')
    if not (isinstance(_md, list) and _md) and '嫁娶' not in str(_yi):
        return '非嫁娶路径'
    if ctx.detail.get('veto_reasons'):
        return '一票否决日，reason 为否决词，无综合判断段'
    reason = ctx.reason
    if '综合判断' not in reason:
        ctx.issue('E201', '嫁娶路径缺少「综合判断」结论句',
                  source='reason', suggestion='补写「综合判断：…可用/慎用/不可用」')
        return None
    tail = reason.split('综合判断')[-1]
    verdicts = ('可用', '慎用', '不可用', '不宜用', '不宜嫁娶')
    if not any(v in tail for v in verdicts):
        ctx.issue('E201', '嫁娶路径综合判断句缺少明确结论（可用/慎用/不可用/不宜）',
                  source='reason 综合判断尾段', suggestion='补充明确结论词')
    return None


@register_rule('E202', SEVERITY_WARN, '喜用神评语措辞与得分档位匹配')
def rule_e202(ctx):
    """喜用神评语必须落在得分对应档位，不得出现越档褒词。"""
    score = int(ctx.sd.get('喜用神得分') or 0)
    # 从 reason 提取喜用神评语句
    xys_sentences = []
    for seg in ctx.reason.replace('\n', '；').split('；'):
        if '喜用神' in seg:
            xys_sentences.append(seg.strip())
    if not xys_sentences:
        return 'reason 无喜用神评语句'
    text = '；'.join(xys_sentences)

    # 档位 → 允许措辞 / 禁用措辞（先做禁用，避免误伤）
    PHRASE_TABLE = [
        (0, 5, ['补益有限'], ['有一定补益', '补益较大', '能量共振极佳']),
        (6, 10, ['补益有限', '略有助益'], ['补益较大', '能量共振极佳']),
        (11, 15, ['有一定补益'], ['补益有限', '能量共振极佳']),
        (16, 999, ['补益较大', '能量共振极佳'], ['补益有限', '略有助益']),
    ]
    for lo, hi, _, forbidden in PHRASE_TABLE:
        if lo <= score <= hi:
            for bad in forbidden:
                if bad in text:
                    ctx.issue(
                        'E202',
                        f'喜用神得分{score}分（{lo}-{hi}档），评语不应出现越档措辞「{bad}」',
                        source='score_details[喜用神得分] vs reason 喜用神句',
                        suggestion=f'该档允许措辞：{bad} 不属于 {lo}-{hi} 分档位')
            break
    return None


@register_rule('E203', SEVERITY_WARN, '报告文本干支/日期/占位符一致性')
def rule_e203(ctx):
    """检测文本中的干支、日期、占位符是否与结构化数据一致。"""
    import re
    text = ctx.rendered_content if ctx.rendered_content is not None else ctx.reason

    # 1. 日柱干支一致性：reason 中出现的日柱干支不应与 detail 日柱矛盾
    sizhu = ctx.detail.get('sizhu')
    if isinstance(sizhu, dict):
        day_pillar = str(sizhu.get('日柱') or '')
        # 简单检查：文本中是否有"日柱XX"但与实际日柱不同
        m = re.search(r'日柱[：:]\s*(\S{2})', text)
        if m and m.group(1) != day_pillar and day_pillar:
            ctx.issue('E203',
                      f'文本写「日柱{m.group(1)}」，实际日柱为{day_pillar}',
                      source='rendered_content vs detail[sizhu][日柱]',
                      suggestion='核对日柱干支是否串台')

    # 2. 未替换占位符（先剔除有意保留的事主角色标签：相主角色后缀、生肖/日支
    #    前缀、喜用匹配行——空名事主以角色名“事主N”作展示标签，非模板占位符）
    _text_lab = re.sub(r'（事主[1-4]）', '', text)
    _text_lab = re.sub(r'事主[1-4](生肖|日支|年命)', '', _text_lab)
    _text_lab = re.sub(r'事主[1-4]：', '', _text_lab)
    placeholders = ['事主1', '事主2', '事主3', '事主4', '{{姓名}}', '{{日期}}']
    for ph in placeholders:
        if ph in _text_lab:
            ctx.issue('E203', f'报告文本出现未替换占位符「{ph}」',
                      source='rendered_content',
                      suggestion='检查模板渲染逻辑（已排除事主角色标签）')

    # 3. 日期串台：检查是否有不属于当前日期的 YYYY-MM-DD
    date_obj = None
    if isinstance(sizhu, dict):
        date_obj = sizhu.get('date')
    if date_obj is None:
        date_obj = ctx.detail.get('date')
    if date_obj:
        cur_str = str(date_obj)
        for m in re.finditer(r'20\d{2}-\d{2}-\d{2}', text):
            if m.group() != cur_str:
                ctx.issue('E203',
                          f'文本出现无关日期「{m.group()}」，当前日期为{cur_str}',
                          source='rendered_content',
                          suggestion='检查日期串台')
    return None


@register_rule('E204', SEVERITY_WARN, '日主旺衰描述跨段落一致性')
def rule_e204(ctx):
    """月令分析/日主旺衰段/综合评语对日主强弱的描述必须同极性。"""
    # 收集三段文本
    texts = {}
    wxr = ctx.detail.get('wu_xing_result')
    if isinstance(wxr, dict):
        wd = wxr.get('details')
        if isinstance(wd, dict):
            texts['旺衰段'] = str(wd.get('日主旺衰') or '')
    # 月令分析句（按行 split，因 reason 是多行文本）
    for line in ctx.reason.split('\n'):
        if line.strip().startswith('月令分析：'):
            texts['月令分析'] = line.strip()
            break
    # 综合判断尾句（按行 split）
    # 注意：综合判断通常只含"可用/慎用"结论词，不含旺衰词。
    # 若该行同时含强/弱关键词（如"日主旺相"），才纳入 polarity 比较；
    # 否则视为不参与旺衰一致性判定，避免误报。
    for line in ctx.reason.split('\n'):
        if '综合判断' in line:
            _line = line.strip()
            if any(k in _line for k in ('得令','旺相','得力','旺','得生而相','得生','相地',
                                        '失令','休囚','受克','乏力','弱','囚','死','墓')):
                texts['综合判断'] = _line
            break

    if len(texts) < 2:
        return '可判定段落不足2段'

    STRONG = ('得令', '旺相', '得力', '旺', '得生而相', '得生', '相地')
    WEAK = ('失令', '休囚', '受克', '乏力', '弱', '囚', '死', '墓', '日主休')
    # 排除混合措辞（"失令但得生扶有根不弱"等软描述）
    MIXED = ('有根不弱', '得生扶', '得助不弱')

    polarity = {}
    for name, text in texts.items():
        if not text:
            continue
        # 2026-10-15 S2：新旺衰文案"土旺克水/金旺耗木"类机制说明中的"旺"
        # 是月令五行之旺，非日主之旺，判定 STRONG 前须剔除"旺克/旺耗"，
        # 否则弱文案被误判为强弱并存而漏报。
        _t_strong = text.replace('旺克', '').replace('旺耗', '')
        has_strong = any(k in _t_strong for k in STRONG)
        has_weak = any(k in text for k in WEAK)
        has_mixed = any(k in text for k in MIXED)
        if has_mixed:
            polarity[name] = '混合'
        elif has_strong and not has_weak:
            polarity[name] = '强'
        elif has_weak and not has_strong:
            polarity[name] = '弱'
        else:
            polarity[name] = '不明'

    values = [v for v in polarity.values() if v in ('强', '弱')]
    if len(set(values)) > 1:
        ctx.issue('E204',
                  f'日主旺衰描述不一致：{polarity}',
                  source='月令分析/旺衰段/综合判断 三段对日主强弱描述',
                  suggestion='统一措辞，避免"失令"与"旺相"并存')
    return None


@register_rule('E205', SEVERITY_WARN, '评分明细吉神凶煞须在评语中解释')
def rule_e205(ctx):
    """评分明细中 |value|>=10 的吉神/凶煞，综合评语必须提及（简写匹配）。"""
    if ctx.detail.get('veto_reasons'):
        return '一票否决日，reason 为否决词，无综合评语段'
    sd = ctx.sd
    text = ctx.reason

    # 收集需解释的项：嫁娶明细 + 神煞明细
    explainable = []
    for key in ('嫁娶明细(分项)', '神煞明细', '神煞分项(利月/天德等)'):
        items = sd.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                name, value = str(item[0]), item[1]
            elif isinstance(item, dict):
                name, value = str(item.get('事项') or item.get('name') or ''), item.get('得分') or item.get('score') or 0
            else:
                continue
            try:
                value = int(value)
            except (ValueError, TypeError):
                continue
            if abs(value) >= 10:
                explainable.append((name, value))

    # 白名单1：基础项/结构性项不要求解释
    WHITELIST = {'基础分', '月令得分', '旺衰得分', '支支关系得分', '五行评分', '月令', '喜用神'}
    # 白名单2：已入专属段落的结构性神煞（利月/黄道/夫星等在独立段落输出，
    # 综合评语不必重复提及；2026-10-03 真基线误报暴露）
    STRUCT_EXEMPT = ('大利月', '小利月', '利月', '大黄道', '小黄道', '黄道吉日',
                     '黑道凶日', '夫星', '子星', '阳气', '阴胎')
    explainable = [
        x for x in explainable
        if x[0] not in WHITELIST
        and not any(ex in x[0] for ex in STRUCT_EXEMPT)
    ]

    reported = set()  # 同名只报一次
    for name, value in explainable:
        # 主干词：去括号/去后缀，取前 2 字匹配
        short = name.split('（')[0].split('(')[0].strip()
        if len(short) > 2:
            short = short[:2]  # "天德贵人"→"天德"
        if short in reported:
            continue
        if short and short not in text:
            reported.add(short)
            sign = '加分' if value > 0 else '扣分'
            ctx.issue('E205',
                      f'综合评语未提及{sign}项「{name}」（{value:+d}）',
                      source=f'score_details[{name}]',
                      suggestion='评语中补充该神煞的说明')
    return None


@register_rule('E206', SEVERITY_WARN, '忌项「并见即可用」须说明化解方式')
def rule_e206(ctx):
    """综合判断只罗列吉神"并见"而不说明如何化解所忌，即写「可用」的，告警。

    固化自 LLM 维度 L007：GLM-4-Flash 不具备该元判断能力，
    2026-10-03 三版 prompt 均漏报，转为确定性规则。

    边界案例（2026-01-05 嫁娶，tests/fixtures/2026-01-05_嫁娶_甲戌时/）：
    综合判断"建除平日、小黄道满日须避，然不将日…并见，嫁娶可用"——
    唯一扣分忌项小黄道满日（黑道凶日）-10 分（婚嫁评分算法 L1029），
    恰达"实质凶煞 ≥10"门槛，全文无化解词，命中正确（真阳性，边界）。
    纯轻度场景（仅建除平日 0 扣分须避、无其他扣分忌）尚未出现，
    白名单待实际案例再议；调整命中条件前先复核该 fixture。
    """
    # 综合判断行按行提取（E006/E104 教训：不按"；"截断）
    verdict_line = ''
    for line in ctx.reason.split('\n'):
        if '综合判断' in line:
            verdict_line = line.strip()
            break
    if not verdict_line:
        return 'reason 无综合判断行（缺失情形由 E201 覆盖）'

    # 必要特征：明确"须避"的忌项 ＋ "并见" ＋ 结论"可用"（排除"不可用"）
    if '不可用' in verdict_line or not (
            '须避' in verdict_line and '并见' in verdict_line and '可用' in verdict_line):
        return '综合判断非「须避+并见+可用」句式'

    # 已有既成制化/化解说明则放行（2026-10-08 拍板，新增1：拆"要求类/事实类"）。
    # 只认事实性搭配——"合住/合去/制伏/制住/克制/化解/合化/有制/得制/已制"；
    # 裸"制化"移出白名单：评语"须有制化"只是提出要求（须/需/应/要+制化），
    # 未给时辰/方位等方向，不得据此放行。
    # 要求句式（须/需/应/要…制化/化解）先整体抹除——否则"须有制化"中的
    # "有制"会被误当既成事实（2026-10-08 verify 发现的子串陷阱）。
    import re as _re
    _probe = _re.sub(
        r'[须需要应][^，；。]{0,6}(?:制化|化解|制伏|制住|克制|合住|合去)',
        '', verdict_line)
    RESOLVED_FACT = ('合住', '合去', '制伏', '制住', '克制', '化解',
                     '合化', '有制', '得制', '已制')
    if any(k in _probe for k in RESOLVED_FACT):
        return '结论已含既成制化/化解说明'

    ctx.issue('E206',
              '综合判断只说吉神「并见」、未说明如何化解所忌，即写「可用」',
              source='reason 综合判断行',
              suggestion='补充吉神如何制化/合住所忌的说明，或把结论改为慎用')
    return None


# ==================== 阶段三：LLM 语义兜底审查 ====================
# 定位：只抓硬规则（E001-E105）覆盖不到的语义级矛盾。
# 边界：不做算术、不做命理判定；只输出 WARN/INFO，不阻断报告。

LLM_SYSTEM_PROMPT = """你是择日报告的独立文字审查员。只做语义/文字一致性检查，不做算术，不做命理判断，不重复硬规则的工作。

【两种错误都要避免】
- 不要凑数：没有确凿矛盾时必须返回 []，严禁输出"正常/无问题"之类的通过项。
- 不要漏报：一旦发现下列【明确矛盾】且能在报告中逐字引用，就必须输出。
你的价值在于抓住文本里自相矛盾、一眼可辨的错误。

【必须报告的明确矛盾】
L001 等级或语气是"慎用/凶/不宜"，综合判断结论却写"可用/大吉"（二者直接相反）。
L002 对日主旺衰，一处写"旺相/得令/有力"，另一处写"失令/休囚/身弱"（非"失令但有根不弱"这类同一句内的转折）。
L003 喜用神得分很低（个位数）却写"补益较大/能量共振极佳"，或得分高却写"补益有限"。
L004 综合判断句没有任何结论词（可用/慎用/不可用/不宜）。
L005 术语明显误用或生造。
L006 有显著扣分/吉神，报告却完全没有对应解释。
L007 已由硬规则 E206 固化覆盖：你无需检查、也不要输出 L007。
L008 日期、干支、姓名前后不一致，或残留占位符/复制痕迹。

【证据要求】
每条问题的 actual 必须是从报告原文【逐字复制】的片段（L004 除外，可引用缺结论的那句）。
找不到原文佐证的猜测，一律不输出。每个维度至多 1 条。

【输出格式】严格 JSON 数组，每个元素：
{"rule_id": "L001", "level": "WARN"|"INFO", "message": "一句话描述",
 "field": "出问题的段落", "actual": "报告原文逐字片段", "suggestion": "修复建议"}

无确凿矛盾时输出 []。除 JSON 外不要输出任何文字。"""

# 约束：report_text（渲染全文）是 LLM 引用的唯一事实来源，重构时不可从模板删除；
# facts 仅结构化摘要辅助（yi_list/ji_list 可能窄于渲染文本的宜/忌行，
# 以渲染文本为准，见 tests/fixtures/2026-01-05_嫁娶_甲戌时/ 复核记录）。
LLM_USER_TEMPLATE = """【基本信息】
{facts_json}

【渲染报告（唯一事实来源，引用必须逐字取自此处）】
{report_text}

请审查：有确凿、可逐字引用的问题才输出 JSON 数组，否则输出 []。"""


def _llm_result_to_issues(items):
    """LLM JSON 数组 → Issue 列表（统一 WARN/INFO，标记来源）。"""
    issues = []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict):
            continue
        rid = str(it.get('rule_id') or 'L000')
        lvl = str(it.get('level') or 'WARN').upper()
        if lvl not in ('WARN', 'INFO'):
            lvl = 'WARN'
        msg = str(it.get('message') or '')
        if not msg:
            continue
        src = str(it.get('field') or 'LLM')
        actual = str(it.get('actual') or '').strip()
        sug = str(it.get('suggestion') or '')
        # 附原文证据，便于人工核验真假阳性（无引用则不附）
        full_msg = f'[LLM] {msg}'
        if actual and actual != src:
            full_msg += f'（原文：{actual}）'
        issues.append(Issue(rid, lvl, full_msg, source=src, suggestion=sug))
    return issues


def llm_review(detail, report_text, api_func=None, timeout=30, cache=None):
    """LLM 语义兜底审查。

    Args:
        detail: Scorer.score() 返回的完整 dict
        report_text: 渲染后的完整报告文本
        api_func: 可选，自定义 LLM 调用函数 (prompt) -> str。
                  None 则尝试内置的 OpenAI/通义兼容调用。
        timeout: 秒，硬超时
        cache: dict，可选缓存 {(date_str, event, score): issues}。

    Returns:
        list[Issue]：LLM 产出的问题列表（WARN/INFO）。
        - 未配置 Key（功能关闭）：返回 []。
        - 已配置 Key 但本次调用/解析失败：返回 1 条 L000 INFO，明确告知
          语义审查本次不可用，避免与"审查通过、零问题"混淆（不静默吞错）。
    """
    import json, logging
    logger = logging.getLogger(__name__)

    def _unavailable(reason):
        # 失败不写缓存，便于下次重试。
        return [Issue(
            'L000', SEVERITY_INFO,
            '[LLM] 语义审查本次不可用，已降级为纯硬规则模式',
            source='LLM', suggestion=str(reason)[:160])]

    # 缓存键：日期 + 事项 + 总分（报告内容实质等价）
    _cache_key = None
    if cache is not None and isinstance(cache, dict):
        _sd = detail.get('score_details') or {}
        _cache_key = (
            str(detail.get('date') or ''),
            str(detail.get('event_type') or ''),
            int(_sd.get('总分') or detail.get('score') or 0),
        )
        if _cache_key in cache:
            return cache[_cache_key]

    # 1) 构造精简事实（不喂整份 detail，避免弱模型跨字段串味 + 降低延迟）
    facts = {
        '日期': str(detail.get('date') or ''),
        '事项': str(detail.get('event_type') or ''),
        '总分': detail.get('score'),
        '等级': detail.get('level'),
        '宜': detail.get('yi_list'),
        '忌': detail.get('ji_list'),
    }
    try:
        facts_json = json.dumps(facts, ensure_ascii=False, default=str)
    except Exception:
        facts_json = str(facts)
    prompt = LLM_USER_TEMPLATE.format(facts_json=facts_json,
                                      report_text=report_text or '')

    # 2) 调用 LLM
    raw = ''
    try:
        if api_func:
            raw = api_func(prompt)
        else:
            # 内置：尝试 OpenAI 兼容接口（无 key 则静默跳过＝功能关闭）
            import os
            api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('DASHSCOPE_API_KEY')
            if not api_key:
                logger.info('LLM 审查未配置 API Key，跳过语义审查')
                if cache is not None and _cache_key:
                    cache[_cache_key] = []
                return []
            base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            model = os.environ.get('LLM_REVIEW_MODEL', 'gpt-4o-mini')
            import urllib.request
            req = urllib.request.Request(
                f'{base_url}/chat/completions',
                data=json.dumps({
                    'model': model,
                    'messages': [
                        {'role': 'system', 'content': LLM_SYSTEM_PROMPT},
                        {'role': 'user', 'content': prompt},
                    ],
                    'temperature': 0.1,
                    'max_tokens': 1000,
                }, ensure_ascii=False).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}',
                },
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode('utf-8'))
                raw = body['choices'][0]['message']['content']
    except Exception as e:
        logger.warning('LLM 审查调用失败，降级为纯硬规则模式：%s', e)
        return _unavailable(e)

    # 3) 解析 JSON（容错剥离 markdown 围栏）
    raw = raw.strip()
    if raw.startswith('```'):
        raw = raw.strip('`').lstrip('json').strip()
    try:
        items = json.loads(raw)
    except Exception as e:
        logger.warning('LLM 返回非 JSON，降级：%s | raw=%s', e, raw[:200])
        return _unavailable(f'返回非JSON: {raw[:80]}')

    issues = _llm_result_to_issues(items)
    if cache is not None and _cache_key:
        cache[_cache_key] = issues
    return issues
