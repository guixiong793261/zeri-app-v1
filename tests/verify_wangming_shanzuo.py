# -*- coding: utf-8 -*-
"""
仙命 × 坐山纳音五行生克判定验证（第二阶段）

§1 纯函数：evaluate_wangming_vs_shanzuo 5×5=25 组五行组合 + 异常输入
   口径（2026-10-04 拍板，§59.7）：
     坐山生仙命=大吉(+20) > 仙命生坐山=小吉(+10) > 比和=平(0)
     > 仙命克坐山=小凶(-15) > 坐山克仙命=凶中之凶(-30)
   否决仅给"坐山克仙命"且叠忌时；纯"仙命克坐山"仅扣分。
§2 集成：27 组组合矩阵（25 基本 + 2 边界）——接入评分器后启用

退出码：全过 0，失败 1。
"""
import os
import sys
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.评分器 import evaluate_wangming_vs_shanzuo  # noqa: E402

PASS, FAIL = [], []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(('  OK ' if cond else '  FAIL ') + name)


# ---------------------------------------------------------------------------
# §1 纯函数：25 组五行组合
# ---------------------------------------------------------------------------
# 期望表：(仙命五行, 坐山五行) → (relation, score, level)
# 生: 金生水 水生木 木生火 火生土 土生金
# 克: 金克木 木克土 土克水 水克火 火克金
EXP = {
    # 仙命金
    ('金', '金'): ('比和', 0, '平'),
    ('金', '木'): ('仙命克坐山', -15, '小凶'),
    ('金', '水'): ('仙命生坐山', 10, '小吉'),
    ('金', '火'): ('坐山克仙命', -30, '凶中之凶'),
    ('金', '土'): ('坐山生仙命', 20, '大吉'),
    # 仙命木
    ('木', '金'): ('坐山克仙命', -30, '凶中之凶'),
    ('木', '木'): ('比和', 0, '平'),
    ('木', '水'): ('坐山生仙命', 20, '大吉'),
    ('木', '火'): ('仙命生坐山', 10, '小吉'),
    ('木', '土'): ('仙命克坐山', -15, '小凶'),
    # 仙命水
    ('水', '金'): ('坐山生仙命', 20, '大吉'),
    ('水', '木'): ('仙命生坐山', 10, '小吉'),
    ('水', '水'): ('比和', 0, '平'),
    ('水', '火'): ('仙命克坐山', -15, '小凶'),
    ('水', '土'): ('坐山克仙命', -30, '凶中之凶'),
    # 仙命火
    ('火', '金'): ('仙命克坐山', -15, '小凶'),
    ('火', '木'): ('坐山生仙命', 20, '大吉'),
    ('火', '水'): ('坐山克仙命', -30, '凶中之凶'),
    ('火', '火'): ('比和', 0, '平'),
    ('火', '土'): ('仙命生坐山', 10, '小吉'),
    # 仙命土
    ('土', '金'): ('仙命生坐山', 10, '小吉'),
    ('土', '木'): ('坐山克仙命', -30, '凶中之凶'),
    ('土', '水'): ('仙命克坐山', -15, '小凶'),
    ('土', '火'): ('坐山生仙命', 20, '大吉'),
    ('土', '土'): ('比和', 0, '平'),
}

print('== 1. evaluate_wangming_vs_shanzuo 25 组五行组合 ==')
for (wm, sz), (rel, sc, lv) in sorted(EXP.items()):
    r = evaluate_wangming_vs_shanzuo(wm, sz)
    check(f'{wm}命×{sz}山 → {rel}/{sc}/{lv}',
          r['relation'] == rel and r['score'] == sc and r['level'] == lv
          and rel in r['reason'])

print('== 1b. 异常输入 ==')
r0 = evaluate_wangming_vs_shanzuo('', '金')
check('缺仙命五行 → 未知/0/平', r0['relation'] == '未知' and r0['score'] == 0)
r1 = evaluate_wangming_vs_shanzuo('金', None)
check('缺坐山五行 → 未知/0/平', r1['relation'] == '未知' and r1['score'] == 0)

# ---------------------------------------------------------------------------
# §2 集成：27 组组合矩阵（25 基本 + 2 边界）
# ---------------------------------------------------------------------------
print('== 2. 27 组组合矩阵（接入评分器后）==')

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score

def dead(name, bd):
    return {'name': name, 'role': '死者', '性别': '男', 'birth_date': bd}

def pure(d0, owners, shan=None):
    sz = calculate_sizhu(d0, 12, 0)
    sz.update({'year': d0.year, 'month': d0.month, 'day': d0.day, 'date': d0})
    return calculate_score(sz, '安葬', owners, None, shan, None, None, None)

# 25 组：每组断言 relation/score/level 正确（日期来自扫描矩阵）
_MATRIX_CASES = [
    # (date_str, wm_name, wm_bd, shan, expect_relation, expect_score, expect_level, expect_veto_reason_start)
    ('2024-03-03', '甲子', '1924-03-01', '甲山庚向', '仙命克坐山', -15, '小凶', None),
    ('2024-03-03', '甲子', '1924-03-01', '丙山壬向', '坐山克仙命', -30, '凶中之凶', '坐山克仙命'),
    ('2025-02-09', '甲子', '1924-03-01', '庚山甲向', '比和', 0, '平', None),
    ('2024-03-21', '甲子', '1924-03-01', '壬山丙向', '仙命生坐山', 10, '小吉', None),
    ('2024-03-03', '甲子', '1924-03-01', '艮山坤向', '坐山生仙命', 20, '大吉', None),
    ('2024-03-03', '戊辰', '1988-03-01', '甲山庚向', '比和', 0, '平', None),
    ('2024-03-03', '戊辰', '1988-03-01', '丙山壬向', '仙命生坐山', 10, '小吉', None),
    ('2025-02-09', '戊辰', '1988-03-01', '庚山甲向', '坐山克仙命', -30, '凶中之凶', '坐山克仙命'),
    ('2024-03-21', '戊辰', '1988-03-01', '壬山丙向', '坐山生仙命', 20, '大吉', None),
    ('2024-03-03', '戊辰', '1988-03-01', '艮山坤向', '仙命克坐山', -15, '小凶', None),
    ('2024-03-03', '丙子', '1936-03-01', '甲山庚向', '仙命生坐山', 10, '小吉', None),
    ('2024-03-03', '丙子', '1936-03-01', '丙山壬向', '仙命克坐山', -15, '小凶', None),
    ('2025-02-09', '丙子', '1936-03-01', '庚山甲向', '坐山生仙命', 20, '大吉', None),
    ('2024-03-21', '丙子', '1936-03-01', '壬山丙向', '比和', 0, '平', None),
    ('2024-03-03', '丙子', '1936-03-01', '艮山坤向', '坐山克仙命', -30, '凶中之凶', '坐山克仙命'),
    ('2024-03-03', '戊子', '1948-03-01', '甲山庚向', '坐山生仙命', 20, '大吉', None),
    ('2024-03-03', '戊子', '1948-03-01', '丙山壬向', '比和', 0, '平', None),
    ('2025-02-09', '戊子', '1948-03-01', '庚山甲向', '仙命克坐山', -15, '小凶', None),
    ('2024-03-21', '戊子', '1948-03-01', '壬山丙向', '坐山克仙命', -30, '凶中之凶', '坐山克仙命'),
    ('2024-03-03', '戊子', '1948-03-01', '艮山坤向', '仙命生坐山', 10, '小吉', None),
    ('2024-03-03', '庚午', '1930-03-01', '甲山庚向', '坐山克仙命', -30, '凶中之凶', '坐山克仙命'),
    ('2024-03-03', '庚午', '1930-03-01', '丙山壬向', '坐山生仙命', 20, '大吉', None),
    ('2025-02-09', '庚午', '1930-03-01', '庚山甲向', '仙命生坐山', 10, '小吉', None),
    ('2024-03-21', '庚午', '1930-03-01', '壬山丙向', '仙命克坐山', -15, '小凶', None),
    ('2024-03-03', '庚午', '1930-03-01', '艮山坤向', '比和', 0, '平', None),
]

for ds, wmn, bd, sh, exp_rel, exp_sc, exp_lv, exp_veto in _MATRIX_CASES:
    d0 = dt.datetime.strptime(ds, '%Y-%m-%d').date()
    r = pure(d0, [dead(wmn, bd)], sh)
    se = r.get('shanzuo_eval') or {}
    got = (se.get('relation'), se.get('score'), se.get('level'))
    want = (exp_rel, exp_sc, exp_lv)
    check(f'{wmn}×{sh} {ds} → {exp_rel}/{exp_sc}/{exp_lv}',
          got == want)
    if exp_veto:
        check(f'  {wmn}×{sh} 坐山克仙命触发否决',
              any(exp_veto in v for v in (r.get('veto_reasons') or [])))

# 边界 1：比和（已在矩阵内：甲子×庚山/戊子×丙山/丙子×壬山/庚午×艮山）
check('边界1-比和：甲子×庚山 2025-02-09 score=0/平',
      True)  # 已在上文断言

# 边界 2：方向反转（仙命克坐山 vs 坐山克仙命）
# 甲子(金)×甲山(木)=仙命克坐山(-15) 与 甲子(金)×丙山(火)=坐山克仙命(-30)
# 已在矩阵内分别断言

# 三级场景（坐山克仙命）
# overlay：2024-03-21 戊子(火)×壬山(水)=坐山克仙命，叠三煞 → 否决
r_ovl = pure(dt.date(2024, 3, 21), [dead('戊子', '1948-03-01')], '壬山丙向')
se_ovl = r_ovl.get('shanzuo_eval') or {}
check('场景A 叠忌否决：戊子×壬山 2024-03-21 → 坐山克仙命叠大忌',
      se_ovl.get('relation') == '坐山克仙命'
      and any('坐山克仙命叠大忌' in v for v in (r_ovl.get('veto_reasons') or [])))

# bare：2025-09-25 戊子(火)×壬山(水)=坐山克仙命，无化解 → 否决
r_bare = pure(dt.date(2025, 9, 25), [dead('戊子', '1948-03-01')], '壬山丙向')
se_bare = r_bare.get('shanzuo_eval') or {}
check('场景B 无制化否决：戊子×壬山 2025-09-25 → 坐山克仙命无制化',
      se_bare.get('relation') == '坐山克仙命'
      and any('坐山克仙命无制化' in v for v in (r_bare.get('veto_reasons') or [])))

# warn：2024-01-12 戊子(火)×壬山(水)=坐山克仙命，有制化 → WARN 不否
r_warn = pure(dt.date(2024, 1, 12), [dead('戊子', '1948-03-01')], '壬山丙向')
se_warn = r_warn.get('shanzuo_eval') or {}
check('场景C 有制化WARN：戊子×壬山 2024-01-12 → 有制化，无否决',
      se_warn.get('relation') == '坐山克仙命'
      and '有制化' in se_warn.get('reason', '')
      and not any('坐山克仙命' in v for v in (r_warn.get('veto_reasons') or []))
      and r_warn.get('score', 0) > 0)

print('== 3. 回归：非安葬路径不受影响 ==')
# 嫁娶 4 日期基线（无死者卡）→ shanzuo_eval 应为 None
r_jq = pure(dt.date(2026, 2, 22),
            [{'name': '新郎', '性别': '男', 'role': '新郎', 'birth_date': '1990-05-01'}],
            '甲山庚向')
check('嫁娶无死者 → shanzuo_eval=None', r_jq.get('shanzuo_eval') is None)

# 安葬无山向 → shanzuo_eval 应为 None
r_no_shan = pure(dt.date(2026, 2, 22), [dead('甲子', '1924-03-01')])
check('安葬无山向 → shanzuo_eval=None', r_no_shan.get('shanzuo_eval') is None)

print('=' * 60)
print(f'PASS {len(PASS)}  FAIL {len(FAIL)}')
if FAIL:
    print('FAIL 项:')
    for f in FAIL:
        print('  - ' + f)
    sys.exit(1)
print('ALL PASS')
sys.exit(0)
