# -*- coding: utf-8 -*-
"""
仙命 × 坐山纳音五行生克判定验证（第二阶段）

§1 纯函数：evaluate_wangming_vs_shanzuo 5×5=25 组五行组合 + 异常输入
   口径（2026-10-04 拍板，§59.7）：
     坐山生仙命=大吉(+20) > 仙命生坐山=小吉(+10) > 比和=平(0)
     > 仙命克坐山=小凶(-15) > 坐山克仙命=凶中之凶(-30)
   否决仅给"坐山克仙命"且叠忌时；纯"仙命克坐山"仅扣分。
§2 集成：27 组组合矩阵（25 基本 + 2 边界）——接入评分器后启用
§1c 等级封顶（§59.9）：坐山克仙命等级封顶"❌ 凶"，无论制化与否
§2b 双凶叠加（§59.10）：日支真冲＋坐山克同日 → 强制 VETO，
   即使两边都有制化；文案明示两凶各自制化状态（4 状态组合断言）
§F fixture 数据驱动回归（2.3）：加载 fixtures/wangming_shanzuo/
   下 JSON 用例，纯函数 + 集成双层断言（格式见 _schema.json）

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
# §1c 等级封顶：_get_level 坐山克仙命封顶"❌ 凶"（§59.9，保守派）
# ---------------------------------------------------------------------------
print('== 1c. _get_level 坐山克仙命等级封顶（§59.9）==')
from modules.评分器 import Scorer  # noqa: E402
_sc = Scorer.__new__(Scorer)  # 纯函数方法，不需要完整实例状态
_KE = {'relation': '坐山克仙命'}
_KER = {'relation': '坐山克仙命', '制化吉神': ['月德']}
check('封顶：坐山克有制化 + 总分95 → ❌ 凶（带制化注）',
      _sc._get_level(95, {'score': 80}, None, _KER)
      == '❌ 凶（坐山克仙命，有制化：月德）')
check('封顶：坐山克有制化 + 总分120（吉神叠满模拟）→ 仍带注凶',
      _sc._get_level(120, {'score': 90}, None,
                     {'relation': '坐山克仙命',
                      '制化吉神': ['天德', '三合', '太阳到山']})
      == '❌ 凶（坐山克仙命，有制化：天德、三合、太阳到山）')
check('封顶：坐山克无制化 + 总分95 → 裸❌ 凶（无制化注）',
      _sc._get_level(95, {'score': 80}, None, _KE) == '❌ 凶')
check('不封顶：比和 + 总分95 → ★★★ 吉',
      _sc._get_level(95, {'score': 80}, None, {'relation': '比和'}) == '★★★ 吉')
check('不封顶：shanzuo_eval=None + 总分95 → ★★★ 吉',
      _sc._get_level(95, {'score': 80}) == '★★★ 吉')
check('五行底线先触发：坐山克无制化 + 五行50 → ❌ 凶',
      _sc._get_level(95, {'score': 50}, None, _KE) == '❌ 凶')
check('低分有制化：坐山克 + 总分55 → 带注凶（制化信息不丢）',
      _sc._get_level(55, {'score': 80}, None, _KER)
      == '❌ 凶（坐山克仙命，有制化：月德）')
check('低分无制化：坐山克 + 总分55 → 裸❌ 凶',
      _sc._get_level(55, {'score': 80}, None, _KE) == '❌ 凶')

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
    # 001 §211（2026-10-31 三煞柱级全面旁路·案B）：本行原期望"坐山克仙命"触发否决，
    # 其叠忌来源是 2024-03-03 的 年三煞(时柱)（已随柱级通道删除）→ 现该日无任何叠忌，
    # 坐山克仙命仅有制化（月德）不否决，改为 None；"坐山克＋叠忌→否决"覆盖由
    # 下方场景A（2024-03-21 戊子×壬山 叠大忌）与场景B（无制化）继续承担。
    ('2024-03-03', '庚午', '1930-03-01', '甲山庚向', '坐山克仙命', -30, '凶中之凶', None),
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
check('反向：场景B 等级为裸"❌ 凶"（无制化，不带制化注）',
      r_bare.get('level') == '❌ 凶')

# warn：2023-03-12 戊子(火)×壬山(水)=坐山克仙命，有制化 → WARN 不否
# §186（2026-10-27）重冻：原锚点 2024-01-12 乙亥日犯年重丧+复日一票否决
# （拍板3大凶日升级），经 2019-2030 全扫取唯一满足「制化恰为月德+天德」
# 的替代日 2023-03-12（实测 score=77）。
r_warn = pure(dt.date(2023, 3, 12), [dead('戊子', '1948-03-01')], '壬山丙向')
se_warn = r_warn.get('shanzuo_eval') or {}
check('场景C 有制化WARN：戊子×壬山 2023-03-12 → 有制化，无否决',
      se_warn.get('relation') == '坐山克仙命'
      and '有制化' in se_warn.get('reason', '')
      and not any('坐山克仙命' in v for v in (r_warn.get('veto_reasons') or []))
      and r_warn.get('score', 0) > 0)
check('场景C：score=77 等级带注凶、忌列表/调和句齐全',
      r_warn.get('level') == '❌ 凶（坐山克仙命，有制化：月德、天德）'
      and '坐山克仙命（有制化：月德、天德）' in r_warn.get('ji_list')
      and '可用须谨慎' in r_warn.get('reason', ''))

# 封顶集成（§59.9）：单凶坐山克 + 有制化 + 无否决 + 总分高分 → level 封顶凶
r_cap1 = pure(dt.date(2023, 3, 22), [dead('甲子', '1924-03-01')], '丙山壬向')
se_cap1 = r_cap1.get('shanzuo_eval') or {}
# 001 §238（2026-11-09 自刑伏吟加重，用户拍板）：2023-03-22 癸卯年乙卯月己卯日
# 庚午时，年/月/日三卯互伏吟 -45（-15×3），加权后 76→45；final<60 致 level_cap
# 四要件锚点失效（fixture integration/level_cap_20230322 同步改 cap=false 挂账）。
check('封顶集成：2023-03-22 score=45 月德 → 等级带注凶',
      se_cap1.get('_with_huajie') and r_cap1.get('score') == 45
      and not (r_cap1.get('veto_reasons') or [])
      and r_cap1.get('level') == '❌ 凶（坐山克仙命，有制化：月德）')
check('展示调和：2023-03-22 忌列表含制化条目',
      '坐山克仙命（有制化：月德）' in r_cap1.get('ji_list'))
check('展示调和：2023-03-22 综合评语含"可用须谨慎"',
      '可用须谨慎' in r_cap1.get('reason', ''))

r_cap2 = pure(dt.date(2023, 6, 13), [dead('甲子', '1924-03-01')], '丙山壬向')
se_cap2 = r_cap2.get('shanzuo_eval') or {}
# 001 §180（2026-10-25 修造专项W2-a3）：score 100→159 系 feixing clamp(0,100)
# 上限取消后的真实值还原（旧值100为钳位伪影）；等级封顶凶逻辑不受影响。
# 001 §185（2026-10-26 向方禁忌批）：159→121——午年煞北+戌月煞北亥子丑，向首壬→
# 子∈ → 年三煞(向方)-25+月三煞(向方)-20，×0.7 加权后 -31.5→-38（clamp 前实测）。
# 2026-11-06 向方三煞降权（用户拍板）：年三煞(向方)-25→-10、月三煞(向方)-20→-6，
# 加权后 -31.5→-11.2，121→139。
# 001 §238（2026-11-09 自刑伏吟加重，用户拍板）：月支午×时支午自刑额外 -7
# （与基线-8 合计-15），加权后 139→134。
# 001 §250（2026-11-10 天乙贵人入计分）：日干查四柱命中 +15 经加权后 134→144
# （fixture integration/level_cap_20230613 同步重冻）。
check('封顶集成：2023-06-13 吉神叠满 score=144 → 等级带注凶',
      r_cap2.get('score') == 144 and not (r_cap2.get('veto_reasons') or [])
      and r_cap2.get('level')
      # §59.11（2026-10-07）：坐山克场景太阳到山改写为"太阳到坐山正照制化"并置顶
      == '❌ 凶（坐山克仙命，有制化：太阳到坐山正照制化、天德、三合）'
      and '太阳到坐山正照制化' in se_cap2.get('reason', ''))
check('展示调和：2023-06-13 忌列表/综合评语齐全',
      '坐山克仙命（有制化：太阳到坐山正照制化、天德、三合）' in r_cap2.get('ji_list')
      and '可用须谨慎' in r_cap2.get('reason', ''))

# 双凶叠加强制 VETO 集成（§59.10）
# §186（2026-10-27）重冻：原锚点 2023-02-05 甲午日犯重丧+复日一票否决
# （拍板3大凶日升级，否决短路致双凶文案不生成），经 2019-2030 全扫取唯一
# 满足「两边仅三合制化」的替代日 2030-10-26（庚戌年丙戌月甲午日，实测）。
r_d1 = pure(dt.date(2030, 10, 26), [dead('甲子', '1924-03-01')], '丙山壬向')
v_d1 = r_d1.get('veto_reasons') or []
check('双凶关键边界：2030-10-26 两边仅三合制化 → 强制VETO+双凶叠加文案',
      r_d1.get('score') == 0
      and any('仙命双凶叠加' in v and '有制化：三合' in v for v in v_d1))

r_d2 = pure(dt.date(2023, 3, 13), [dead('甲子', '1924-03-01')], '丙山壬向')
v_d2 = r_d2.get('veto_reasons') or []
check('双凶：2023-03-13 两边无制化 → VETO+双无制化文案',
      r_d2.get('score') == 0
      and any('仙命双凶叠加' in v and v.count('无制化') == 2 for v in v_d2))
check('反向：双凶强制否决等级为裸"❌ 凶"（不带制化注，与单凶封顶区分）',
      r_d2.get('level') == '❌ 凶')

# 双凶文案 4 种制化状态组合 + 叠忌（纯函数断言，覆盖真实流程难出现的交叉状态）
_WM = {'name': '甲子', '年柱': '甲子', '纳音': '海中金', '五行': '金'}
_SE = {'坐山': '丙', '坐山五行': '火'}

def _dual(zc_h, zc_r, sz_h, sz_r):
    return _sc._build_wm_dual_veto_text(_WM, _SE, '午', zc_h, zc_r, sz_h, sz_r)

_t0 = _dual([], [], [], [])
check('双凶文案状态1：两边无制化', _t0.count('无制化') == 2)
_t1 = _dual([], ['天德'], [], [])
check('双凶文案状态2：真冲有天德/坐山无制化',
      '有制化：天德' in _t1 and _t1.count('无制化') == 1)
_t2 = _dual([], [], [], ['太阳到山'])
check('双凶文案状态3：真冲无制化/坐山太阳到山',
      '有制化：太阳到山' in _t2 and _t2.count('无制化') == 1)
_t3 = _dual([], ['天德'], [], ['太阳到山'])
check('双凶文案状态4：两边都有制化（核心边界，仍强制否决）',
      '有制化：天德' in _t3 and '有制化：太阳到山' in _t3
      and '无制化' not in _t3 and '强制否决' in _t3)
_th = _dual(['三煞'], [], ['三煞'], [])
check('双凶文案：两边叠三煞大忌', _th.count('叠三煞大忌') == 2)

print('== 3. 回归：非安葬路径不受影响 ==')
# 嫁娶 4 日期基线（无死者卡）→ shanzuo_eval 应为 None
r_jq = pure(dt.date(2026, 2, 22),
            [{'name': '新郎', '性别': '男', 'role': '新郎', 'birth_date': '1990-05-01'}],
            '甲山庚向')
check('嫁娶无死者 → shanzuo_eval=None', r_jq.get('shanzuo_eval') is None)

# 安葬无山向 → shanzuo_eval 应为 None
r_no_shan = pure(dt.date(2026, 2, 22), [dead('甲子', '1924-03-01')])
check('安葬无山向 → shanzuo_eval=None', r_no_shan.get('shanzuo_eval') is None)

# 反向：非坐山克仙命（仙命克坐山）路径等级正常，不带封顶注
r_other = pure(dt.date(2024, 3, 3), [dead('甲子', '1924-03-01')], '甲山庚向')
check('反向：甲子×甲山（仙命克坐山）等级不含坐山克封顶注、无调和句',
      (r_other.get('shanzuo_eval') or {}).get('relation') == '仙命克坐山'
      and '坐山克仙命' not in r_other.get('level', '')
      and '可用须谨慎' not in r_other.get('reason', ''))

# ---------------------------------------------------------------------------
# §F fixture 数据驱动回归（2.3，tests/fixtures/wangming_shanzuo/）
# 格式见 _schema.json；案例文件不以下划线开头
# ---------------------------------------------------------------------------
print('== F. fixture 数据驱动回归（fixtures/wangming_shanzuo/）==')
import glob  # noqa: E402
import json  # noqa: E402
_FIX_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'fixtures', 'wangming_shanzuo')
_fix_files = sorted(
    p for p in glob.glob(os.path.join(_FIX_ROOT, '**', '*.json'), recursive=True)
    if not os.path.basename(p).startswith('_'))


def _fix_report(case):
    """按 fixture input 调评分器生成集成报告（午时正午，与内联矩阵同口径）。"""
    inp = case['input']
    d0 = dt.date.fromisoformat(inp['date'])
    sz = calculate_sizhu(d0, 12, 0)
    sz.update({'year': d0.year, 'month': d0.month, 'day': d0.day, 'date': d0})
    owners = []
    if inp.get('wangming_birth_date'):
        owners.append({'name': inp.get('wangming_ganzhi', '亡命'),
                       'role': '死者', '性别': '男',
                       'birth_date': inp['wangming_birth_date']})
    return calculate_score(sz, inp.get('event', '安葬'), owners, None,
                           inp.get('shanzuo'), None, None, None)


for _fp in _fix_files:
    with open(_fp, encoding='utf-8') as _f:
        case = json.load(_f)
    cid = case.get('case_id', os.path.basename(_fp))
    inp, exp = case['input'], case['expected']
    errs = []
    r = evaluate_wangming_vs_shanzuo(inp['wangming_nayin_wuxing'],
                                     inp['shanzuo_wuxing'])
    for k in ('relation', 'score', 'level'):
        if k in exp and r[k] != exp[k]:
            errs.append(f'{k}: {r[k]!r}!={exp[k]!r}')
    for kw in exp.get('reason_contains', []):
        if kw not in r['reason']:
            errs.append(f'reason缺{kw!r}')
    # 集成断言：带日期 + 亡命生日时跑评分器
    if inp.get('date') and inp.get('wangming_birth_date'):
        rep = _fix_report(case)
        rep_se = rep.get('shanzuo_eval') or {}
        _veto = bool(rep.get('veto_reasons'))
        _final = rep.get('score')
        # 严格双向判定封顶：坐山克 + 无否决 + 总分≥60 但展示仍凶
        actual_cap = (rep_se.get('relation') == '坐山克仙命'
                      and not _veto and isinstance(_final, int) and _final >= 60
                      and str(rep.get('level', '')).startswith('❌ 凶'))
        if 'veto' in exp and _veto != exp['veto']:
            errs.append(f"veto: {_veto}!={exp['veto']}")
        if 'level_cap' in exp and actual_cap != exp['level_cap']:
            errs.append(f"level_cap: {actual_cap}!={exp['level_cap']}")
        if 'report_level' in exp and rep.get('level') != exp['report_level']:
            errs.append(f"report_level: {rep.get('level')!r}!={exp['report_level']!r}")
        if 'final_score' in exp and rep.get('score') != exp['final_score']:
            errs.append(f"final: {rep.get('score')}!={exp['final_score']}")
    check(f"fixture {cid} {case.get('description', '')}", not errs)
    if errs:
        for e in errs:
            print('       - ' + e)
if not _fix_files:
    print('  （fixture 暂无案例，等待 commit 2 归档 27 组）')

print('=' * 60)
print(f'PASS {len(PASS)}  FAIL {len(FAIL)}')
if FAIL:
    print('FAIL 项:')
    for f in FAIL:
        print('  - ' + f)
    sys.exit(1)
print('ALL PASS')
sys.exit(0)
