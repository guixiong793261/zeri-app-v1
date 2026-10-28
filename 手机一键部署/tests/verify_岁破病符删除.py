# -*- coding: utf-8 -*-
"""岁破／病符 日课普适注册删除 综合回归（2026-10-20，001 §140／§141）
================================================================================
被测变更：
  · 岁破批（001 §140）：清单内面 8c67d1f（谓词3＋发射4＋键7＋文案4＋出行规则
    :50＋校验器前缀）＋清单外面 f6d39bd（9 规则 ji＋veto 继承链 7 通道＋
    评分器 6 处＋2 tests 同步）。
  · 病符批（001 §141）：e6e4bf4（7 发射＋1 谓词＋14 键＋tests 同步）。

判据（三库层级·无载不放宽）：
  · 岁破——协纪卷内「岁破日」0 命中；「岁破最凶／例无制法」系山向造命语境
    （方位），非日课普适忌明文。
  · 病符——协纪「其地」、考原「所理之地」、陈书「病符方」，皆方位/年神语境；
    无「病符日，忌某事」明文。

断言结构（正反双向，防空洞断言）：
  A. 15 通道 × 2026 全年：神煞层 shensha_list / check 输出中 岁破、病符 = 0（逐通道）。
  B. 规则层 ji_list / veto 含「岁破」= 0（逐通道，含 f-string 覆盖的
     入学/求医/签约/通用 4 事项逐一）。
  C. veto 继承链 7 通道逐通道：修造系 5 继承通道（修造/入宅/动土/拆舍/移徙）
     ＋ 出行 ＋ 嫁娶，veto 文本不含「岁破」。
  D. 反向保留面（不得连带删，也不得捞回日课面）：
     D1 开业 / 作灶 本命语境「与…岁破」仍存在（owners 非空时必须 > 0）；
     D2 修造规则 扶山冲突 ji 含「（岁破日）」仍存在（山向语境）；
     D3 二十四山 二黑病符星到山评分仍在（方位神语境）；
     D4 评分器 _HARD_VETO_KEYWORDS 仍含 '岁破'（承 D2 之文本）。
  E. 表层：SHENSHA_SCORES 无岁破/病符键；键数 1148／移徙块 67
     （…→福星正统落地批 001 §169 1199/71；§172 P0 大清理删 岁害14/天耗13/
     地耗14/非嫁娶孤辰寡宿11 → 1147，移徙块删 4 键 → 67；出行双通道割裂
     修复批 001 §183 新增 (出行,日破时) → 1148）；
     shensha_score 对两名返回 None。
  F. 谓词：_is_suipo／_is_bingfu／_get_suipo／_is_sui_po_day／_h1_is_veto_reason
     全库不可调用（剥注释后无定义、无调用）；_get_suipo 保留（日破/月破消费）例外。
  G. 总分基线：入宅/移徙 11601、嫁娶 6490（2026 全年，owners=[]；§172 P0
     大清理重冻：岁害/天耗/地耗删除＋年家族 16 项置 0＋年支孤辰寡宿删除
     ＋大小耗伪链清除，前值 3435/-96；§193 重丧双口径对齐 → 6025；
     §194 受死日嫁娶剥离扣分（HARD_VETO 纯展示）→ 6490；
     §195 Commit1 入宅/移徙 受死日剥离扣分 → 11136→11601）。

退出码：0=全过，1=有失败（FAIL N 计数）
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


def _code_only(src):
    """剥掉 # 注释（墓碑注释含原实现，须剔除后断言）。"""
    return '\n'.join(ln.split('#', 1)[0] for ln in src.splitlines())


CH = ['入宅', '嫁娶', '动土', '修造', '拆舍', '出行', '开业', '安床', '作灶',
      '安葬', '移徙', '入学', '求医', '签约', '通用']
D0, D1 = dt.date(2026, 1, 1), dt.date(2026, 12, 31)


def main():
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha import get_checker
    from modules.事项标准 import (SHENSHA_SCORES, shensha_score,
                                  get_rule_checker, canonical_event)

    # ---------- 预扫描：全年逐日 × 15 通道，缓存 sizhu 避免重复计算 ----------
    days = []
    d = D0
    while d <= D1:
        days.append((d, calculate_sizhu(d, 10, 0)))
        d += dt.timedelta(days=1)

    # ============ A：神煞层 岁破/病符 逐通道清零 ============
    print('[A] 神煞层逐通道清零（2026 全年 × 15 通道，owners=[]）')
    for ev in CH:
        ck = get_checker(ev)
        n_sp = n_bf = 0
        for _, sz in days:
            for s in ck.check(sz, []):
                if s.get('name') == '岁破':
                    n_sp += 1
                elif s.get('name') == '病符':
                    n_bf += 1
        check(f'A {ev:<4} 岁破发射=0（实得 {n_sp}）', n_sp == 0)
        check(f'A {ev:<4} 病符发射=0（实得 {n_bf}）', n_bf == 0)

    # ============ B：规则层 ji / veto_reason 含岁破 = 0 ============
    # check() 返回 (yi_list, ji_list, veto:bool, veto_reason:str)
    print('[B] 规则层 ji/veto_reason 含「岁破」逐通道清零')
    for ev in CH:
        rc = get_rule_checker(ev)
        n_ji = n_veto = 0
        for _, sz in days:
            out = rc.check(sz, [])
            if not isinstance(out, tuple) or len(out) < 4:
                continue
            ji_list, veto, reason = out[1] or [], out[2], out[3] or ''
            n_ji += sum(1 for x in ji_list if '岁破' in str(x))
            if veto and '岁破' in str(reason):
                n_veto += 1
        check(f'B {ev:<4} ji 含岁破=0（实得 {n_ji}）', n_ji == 0)
        check(f'B {ev:<4} veto_reason 含岁破=0（实得 {n_veto}）', n_veto == 0)

    # 通用规则 f-string 覆盖 4 事项（显式点名，防 canonical 归并漏检）
    print('[B2] 通用规则 f-string 覆盖 4 事项逐一断言')
    gen_evs = ['入学', '求医', '签约', '通用']
    for ev in gen_evs:
        rc = get_rule_checker(ev)
        n = 0
        for _, sz in days:
            out = rc.check(sz, [])
            if isinstance(out, tuple) and len(out) >= 2:
                n += sum(1 for x in (out[1] or []) if '岁破' in str(x))
        check(f"B2 {ev} 通道 ji 含岁破=0（实得 {n}）", n == 0)

    # ============ C：veto 继承链 7 通道 ============
    print('[C] veto 继承链 7 通道（修造系 5 继承 ＋ 出行 ＋ 嫁娶）')
    chain = {
        '修造': '父级（修造规则）',
        '入宅': '继承自 ConstructionRuleChecker',
        '动土': '继承自 ConstructionRuleChecker',
        '拆舍': '继承自 ConstructionRuleChecker',
        '移徙': '继承自 ConstructionRuleChecker（canonical=入宅）',
        '出行': '出行规则 veto_keywords',
        '嫁娶': '嫁娶规则 veto_keywords',
    }
    for ev, why in chain.items():
        rc = get_rule_checker(ev)
        hit = []
        n_veto_any = 0
        for _, sz in days:
            out = rc.check(sz, [])
            if not isinstance(out, tuple) or len(out) < 4:
                continue
            veto, reason = out[2], str(out[3] or '')
            if veto:
                n_veto_any += 1
                if '岁破' in reason:
                    hit.append((sz.get('day'), reason[:30]))
        check(f'C {ev:<3} veto 无岁破（{why}；岁破命中 {len(hit)} 天／'
              f'该通道 veto 总数 {n_veto_any}）', not hit, f'{hit[:3]}')

    # ============ D：保留面（反面断言） ============
    print('[D] 保留面：非日课语境不得连带删（逐项 >0 防空洞）')
    # 注：开业规则 ZODIAC_TO_ZHI 用生肖字（'猪'），作灶用支字（'亥'）亦可；
    # 统一取 '猪'（1972 壬子年）令两通道本命分支均可命中。
    OWNERS = [{'name': '主', 'role': '事主', 'birth_date': '1972-01-08', '生肖': '猪'}]
    d1_ok = {}
    for ev in ('开业', '作灶'):
        rc = get_rule_checker(ev)
        n = 0
        for _, sz in days:
            out = rc.check(sz, OWNERS)
            if isinstance(out, tuple) and len(out) >= 2:
                n += sum(1 for x in (out[1] or []) if '岁破' in str(x))
        d1_ok[ev] = n
        check(f'D1 {ev} 本命语境「与…岁破」仍存在（{n} 天，应 >0）', n > 0)
    # D2 扶山冲突 ji（山向语境）
    from modules.rules.修造规则 import ConstructionRuleChecker
    src_xz = _code_only(inspect.getsource(ConstructionRuleChecker))
    check("D2 修造 扶山冲突 ji 含「（岁破日）」仍在（山向语境）",
          '（岁破日）' in inspect.getsource(ConstructionRuleChecker))
    # D3 二十四山 二黑病符星到山评分
    from modules import 二十四山 as M24
    src_24 = _code_only(inspect.getsource(M24))
    check('D3 二十四山 二黑病符星到山 -40 评分仍在（方位神语境）',
          '二黑' in src_24 and '-= 40' in src_24)
    # D4 评分器 _HARD_VETO_KEYWORDS 仍含 '岁破'（类属性，非模块级）
    from modules.评分器 import Scorer
    kws = Scorer._HARD_VETO_KEYWORDS
    check("D4 Scorer._HARD_VETO_KEYWORDS 仍含 '岁破'（承 D2 文本·山向/扶山）",
          '岁破' in kws)

    # ============ E：表层 ============
    print('[E] 表层：键删除与键数基线')
    sp_keys = [k for k in SHENSHA_SCORES if k[1] == '岁破']
    bf_keys = [k for k in SHENSHA_SCORES if k[1] == '病符']
    check(f'表内无岁破键（实得 {len(sp_keys)}）', not sp_keys)
    check(f'表内无病符键（实得 {len(bf_keys)}）', not bf_keys)
    check("通配键 ('*','岁破') 不存在", ('*', '岁破') not in SHENSHA_SCORES)
    check("通配键 ('*','病符') 不存在", ('*', '病符') not in SHENSHA_SCORES)
    check(f'总表键数=1154（批次1 1200 → 建除批次1 001 §161 删 (开业,破日) → 1199；福星批 001 §165 删 福星×14 键 → 1185；福星正统落地批 001 §169 加回 14 键 → 1199；§172 P0 大清理删 岁害14/天耗13/地耗14/非嫁娶孤辰寡宿11 → 1147；出行双通道割裂修复批 001 §183 新增 (出行,日破时) → 1148；建除十二神×出行 D 专项 001 §184 新增 6 键 → 1154；实得 {len(SHENSHA_SCORES)}）', len(SHENSHA_SCORES) == 1154)
    n_yi = len([k for k in SHENSHA_SCORES if k[0] == '移徙'])
    check(f'移徙块键数=67（§165 删 福星×移徙 → 70；福星正统落地批 001 §169 +1 恢复 → 71；§172 P0 大清理删 移徙岁害/天耗/地耗/孤辰寡宿 4 键 → 67；实得 {n_yi}）', n_yi == 67)
    for ev in CH:
        check(f'E shensha_score({ev},岁破)=None', shensha_score(ev, '岁破') is None)
        check(f'E shensha_score({ev},病符)=None', shensha_score(ev, '病符') is None)

    # ============ F：谓词/函数全线不可调用 ============
    print('[F] 谓词与函数删除（剥注释后无定义、全库无调用）')
    from modules.shensha import 神煞基类 as BASE
    for fn in ('_is_suipo', '_is_bingfu'):
        check(f'F ShenShaChecker.{fn} 已删除', not hasattr(BASE.ShenShaChecker, fn))
    from modules.shensha.通用神煞 import CommonShenShaChecker
    check('F CommonShenShaChecker._get_suipo 保留（日破:511/月破:524 消费）',
          hasattr(CommonShenShaChecker, '_get_suipo'))
    from modules.rules.高级安葬规则 import AdvancedBurialRuleChecker as ADV
    check('F AdvancedBurialRuleChecker._is_sui_po_day 已删除',
          not hasattr(ADV, '_is_sui_po_day'))
    check('F AdvancedBurialRuleChecker._is_sui_po_direction 保留（方位语境）',
          hasattr(ADV, '_is_sui_po_direction'))
    from modules import 评分器 as SC
    check('F 评分器._h1_is_veto_reason 已删除',
          not hasattr(SC, '_h1_is_veto_reason'))

    dead = ['_is_suipo(', '_is_bingfu(', '_h1_is_veto_reason(']
    hits = []
    for p in sorted((ROOT / 'modules').rglob('*.py')):
        code = _code_only(p.read_text(encoding='utf-8'))
        for k in dead:
            # 定义与调用均应消失；_is_suipo 需排除 _get_suipo 误匹配
            for ln in code.splitlines():
                s = ln.strip()
                if k == '_is_suipo(' and '_get_suipo(' in s:
                    continue
                if k in s:
                    hits.append(f'{p.name}: {s[:70]}')
    check('F modules/ 全库无可执行调用残余', not hits, f'{hits[:5]}')

    # ============ G：总分基线 ============
    print('[G] 总分基线（2026 全年，owners=[]）')
    # §172 P0 大清理重冻（2026-10-24）：岁害/天耗/地耗删除＋年家族 16 项置 0
    # ＋年支孤辰寡宿删除＋大小耗伪链清除——入宅/移徙 3435→11136、嫁娶 -96→6295。
    # §193 重丧双口径对齐嫁娶 -270 → 6025；§194 受死日嫁娶剥离扣分 → 6490。
    # §195 Commit1 入宅/移徙 受死日剥离扣分 31 天次×+15 → 11601。
    for ev, exp in (('入宅', 11601), ('移徙', 11601), ('嫁娶', 6490)):
        ck = get_checker(ev)
        tot = 0
        for _, sz in days:
            tot += sum(s.get('score', 0) for s in ck.check(sz, []))
        check(f'G {ev} 全年神煞总分={exp}（实得 {tot}）', tot == exp)

    print()
    if FAILS:
        print(f'FAIL {len(FAILS)}：{FAILS[:12]}')
        return 1
    print('ALL PASS（岁破／病符 日课普适注册删除综合回归：15通道＋veto7链＋f-string4事项'
          '＋保留面反向＋表层＋谓词＋总分）')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc()
        print('FAIL 1（脚本异常）')
        sys.exit(1)
