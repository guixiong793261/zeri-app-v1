# -*- coding: utf-8 -*-
"""重丧日实现一致性 + 年命冲岁降级 + 入宅受死日纯展示 综合回归（2026-10-28，001 §196）
================================================================================
被测变更（§196 撤回伪否决批）：
  · D1 嫁娶重丧日：撤 HARD_VETO、撤扣分（三库明言吉事不忌），改为 0 分纯展示。
  · D2 修造重丧日：同上，0 分纯展示。
  · D4 嫁娶年柱冲命：撤「整年一票否决」，降级为 -15 普通扣分（神煞层「年命冲岁」）。
  ·（修造第三实现废除、受死日入宅纯展示等 §195 口径继续保留。）

断言结构（正反双向）：
  A. 源码层：修造委托单点出口、无 zhongsang_map 残留；
     嫁娶规则层不再发射「重丧日」（撤否决后空转不再激活）。
  B. 全年一致性：修造 Ext 与单点出口 2026 逐日零分歧（32 天）。
  C. 撤否决验证：嫁娶规则层 ji 不含「重丧日」、32 天不触发重丧 veto。
  D. 极性变更：('嫁娶','重丧日') / ('修造','重丧日') = 0；神煞层发射恒 0。
  E. 入宅/移徙 受死日：键 0、发射恒 0 分、结论仍否决、全年总分 11601。
  F. 反向保留：安葬通道重丧口径不受波及（发射仍 >0）。
  G. 年命冲岁：键 -15；年柱冲命仅扣分不否决（鼠命新娘可评上吉）。

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
    return '\n'.join(ln.split('#', 1)[0] for ln in src.splitlines())


CH = ['嫁娶', '修造', '入宅', '移徙', '动土', '拆舍', '安葬']
D0, D1 = dt.date(2026, 1, 1), dt.date(2026, 12, 31)


def main():
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha import get_checker
    from modules.shensha.神煞基类 import is_shousi_by_zhi, is_zhongsang_by_lunar
    from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
    from modules.rules.嫁娶规则 import MarriageRuleChecker
    from modules.事项标准 import SHENSHA_SCORES, shensha_score

    days = []
    d = D0
    while d <= D1:
        days.append((d, calculate_sizhu(d, 10, 0)))
        d += dt.timedelta(days=1)

    # ============ A：源码层 ============
    print('[A] 源码层：第三实现废除 / 死 Bug 根除 / 重丧撤否决')
    src_ext = _code_only(inspect.getsource(ConstructionShenShaCheckerExt._is_zhongsang))
    check('A1 修造 _is_zhongsang 已委托单点出口 is_zhongsang_by_lunar',
          'is_zhongsang_by_lunar(' in src_ext)
    check('A1 修造 _is_zhongsang 不再按节令月支自查（无 sizhu 月支取值）',
          "sizhu['month_zhi']" not in src_ext
          and "zhongsang_map =" not in src_ext)
    src_all = _code_only(inspect.getsource(ConstructionShenShaCheckerExt))
    check('A2 修造类内 zhongsang_map 表已彻底废除（剥注释后无赋值残留）',
          'zhongsang_map =' not in src_all)
    src_rc = _code_only(inspect.getsource(MarriageRuleChecker._check_bad_gods))
    # §196 D1：撤否决后规则层不再 append「重丧日」（改由神煞层 0 分纯展示）
    check("A3 嫁娶规则层 _check_bad_gods 不再发射「重丧日」",
          "ji_list.append('重丧日')" not in src_rc)

    # ============ B：全年一致性 ============
    print('[B] 修造 Ext 与单点出口 2026 逐日零分歧')
    ext = ConstructionShenShaCheckerExt()
    n_ext = n_base = 0
    bad = []
    for d, sz in days:
        e = any(s.get('name') == '重丧日' for s in ext.check(sz, []))
        b = is_zhongsang_by_lunar(d)
        n_ext += e
        n_base += b
        if e != b:
            bad.append(str(d))
    check(f'B1 修造重丧天数=32（原第三实现 68；实得 {n_ext}）', n_ext == 32)
    check(f'B1 单点出口重丧天数=32（实得 {n_base}）', n_base == 32)
    check(f'B2 逐日分歧=0（实得 {len(bad)}）', not bad, f'{bad[:4]}')

    # ============ C：撤否决验证 ============
    print('[C] 嫁娶规则层重丧 veto 已撤（ji 不含、不触发否决）')
    rc = MarriageRuleChecker()
    n_ji = n_veto = 0
    leak = []
    for d, sz in days:
        out = rc.check(sz, [])
        ji, veto, reason = out[1] or [], out[2], str(out[3] or '')
        hit = [x for x in ji if '重丧' in str(x)]
        if hit:
            n_ji += 1
        if veto and '重丧' in reason:
            n_veto += 1
            leak.append(str(d))
    check(f'C1 嫁娶规则层 ji 不含「重丧日」（实得 {n_ji} 天）', n_ji == 0)
    check(f'C2 无「重丧」触发 veto（实得 {n_veto} 天）', n_veto == 0,
          f'{leak[:4]}')

    # ============ D：极性变更（撤扣分） ============
    print('[D] 重丧日分值=0（吉事不忌，纯展示）')
    check("D1 ('嫁娶','重丧日')=0", SHENSHA_SCORES.get(('嫁娶', '重丧日')) == 0)
    check("D1 ('修造','重丧日')=0", SHENSHA_SCORES.get(('修造', '重丧日')) == 0)
    for ev in ('嫁娶', '修造'):
        ck = ext if ev == '修造' else get_checker(ev)
        sc = set()
        n = 0
        for d, sz in days:
            for s in ck.check(sz, []):
                if s.get('name') == '重丧日':
                    sc.add(s.get('score'))
                    n += 1
        check(f'D2 {ev} 重丧发射=32 天恒 0（实得 {n}/{sorted(sc)}）',
              n == 32 and sc == {0})

    # ============ E：入宅/移徙 受死日纯展示 ============
    print('[E] 入宅/移徙 受死日剥离扣分（§195 Commit1）')
    for ev in ('入宅', '移徙'):
        check(f"E1 shensha_score('{ev}','受死日')=0",
              shensha_score(ev, '受死日') == 0)
    ck_ru = get_checker('入宅')
    n_ss = 0
    bad_ss = []
    tot_ru = 0
    for d, sz in days:
        rows = ck_ru.check(sz, [])
        tot_ru += sum(s.get('score', 0) for s in rows)
        if is_shousi_by_zhi(sz['month_zhi'], sz['day_zhi']):
            hit = [s for s in rows if s.get('name') == '受死日']
            n_ss += 1
            if len(hit) != 1 or hit[0].get('score') != 0:
                bad_ss.append((str(d), [h.get('score') for h in hit]))
    check(f'E2 入宅受死日 31 天（实得 {n_ss}）', n_ss == 31)
    check(f'E2 发射恒 0 分且唯一（异常 {len(bad_ss)}）', not bad_ss, f'{bad_ss[:3]}')
    check(f'E3 入宅神煞全年总分=11601（实得 {tot_ru}）', tot_ru == 11601)

    from modules.评分器 import calculate_score
    sd = next(d for d, sz in days if is_shousi_by_zhi(sz['month_zhi'], sz['day_zhi']))
    r = calculate_score(calculate_sizhu(sd, 10, 0), '入宅', owners=[])
    check(f'E4 受死日（{sd}）0 分但结论仍否决（实得 {r.get("score")}/{r.get("level")}）',
          r.get('score') == 0 and '凶' in str(r.get('level')))

    # ============ F：反向保留 ============
    print('[F] 反向保留：安葬通道重丧口径不受波及')
    ck_az = get_checker('安葬')
    n_az = sum(1 for d, sz in days
               if any('重丧' in str(s.get('name')) for s in ck_az.check(sz, [])))
    check(f'F1 安葬通道重丧类发射仍 >0（实得 {n_az}）', n_az > 0)

    # ============ G：年命冲岁降级（§196 D4） ============
    print('[G] 年柱冲命：撤整年否决，降级为 -15 扣分（年命冲岁）')
    check("G1 ('嫁娶','年命冲岁')=-15",
          SHENSHA_SCORES.get(('嫁娶', '年命冲岁')) == -15)
    ncm = {'name': '新娘', '姓名': '新娘', '生肖': '鼠', '性别': '女',
           'birth_date': (1984, 6, 15), 'birth_hour': 12}  # 甲子年，2026 丙午年子午冲
    ck_jq = get_checker('嫁娶')
    n_cm = 0
    bad_cm = []
    for d, sz in days:
        rows = ck_jq.check(sz, [ncm])
        hit = [s for s in rows if s.get('name') == '年命冲岁']
        if hit:
            n_cm += 1
            if hit[0].get('score') != -15:
                bad_cm.append((str(d), hit[0].get('score')))
    check(f'G2 鼠命新娘「年命冲岁」全年发射（实得 {n_cm} 天）', n_cm > 300)
    check(f'G2 「年命冲岁」分值恒 -15（异常 {len(bad_cm)}）', not bad_cm,
          f'{bad_cm[:3]}')
    # G3 计分侧：-15 真正进嫁娶评分明细（非仅展示），且不产生否决
    n_detail, bad_detail, n_year_veto = 0, [], 0
    for d, sz in days:
        r = calculate_score(sz, '嫁娶', owners=[ncm])
        det = [x for x in (r.get('marriage_details') or [])
               if str(x[0]).startswith('年命冲岁')]
        if det:
            n_detail += 1
            if det[0][1] != -15:
                bad_detail.append((str(d), det[0]))
        if any('年柱' in str(x) for x in (r.get('否决原因') or [])):
            n_year_veto += 1
    check(f'G3 年命冲岁进入评分明细（丙午年内 331 天，实得 {n_detail} 天）',
          n_detail == 331)
    check(f'G3 评分明细分值恒 -15（异常 {len(bad_detail)}）', not bad_detail,
          f'{bad_detail[:3]}')
    check(f'G3 年柱冲命不再触发否决（否决原因含年柱 0 天，实得 {n_year_veto}）',
          n_year_veto == 0)
    # G4 可评性：全年存在无否决且非凶的鼠命吉日（旧口径整年仅 13 天可评）
    good = 0
    for d, sz in days:
        r = calculate_score(sz, '嫁娶', owners=[ncm])
        if not r.get('否决原因') and '凶' not in str(r.get('level')):
            good += 1
    check(f'G4 鼠命无否决且非凶的吉日 >13 天（实得 {good}）', good > 13)

    print()
    if FAILS:
        print(f'FAIL {len(FAILS)} 项：' + '、'.join(FAILS))
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
