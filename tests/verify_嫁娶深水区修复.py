# -*- coding: utf-8 -*-
"""
嫁娶深水区修复批 · 回归验证（001 §193，2026-10-28）

依据（用户拍板原文，Commit1/2 三个独立 commit 的验收口径）：
  Commit1（P0）解除时柱整日否决；红纸帖吉时引入新人年命冲克过滤
  Commit2（P1）废弃子串匹配、男女+附加事主平权 HARD_VETO；黄沙/红纱重名去重；
                 受死日升 HARD_VETO；重丧双口径对齐
  Commit3     全量回归 + 基线重冻 + 影响面快照 + 001 记账

校验段：
  A 源码层：时柱忌项发射已删（剥注释后 0 命中）、veto_keywords 无「冲新娘」、
    含「受死日」、_hard_veto_chong 结构化登记、择日贴 _avoid_zhi 过滤在位。
  B 时柱解绑：同日换时辰不再改变日课结论（2026-03-02 猪命 五时辰同结论）；
    ji_list 无「时柱」条目。
  C 平权：2026-01-08 壬午日 新郎鼠/新娘鼠/父亲鼠 三者同 0 分否决，牛命不否决；
    12 抽样月（每节气月各 1 天）bride_pig 否决集 ≡ groom_pig 否决集。
  D 受死日：2026 全部 31 天规则层 veto=True（改前 13 天漏网）。
  E 重丧对齐：神煞层谓词 ≡ 算法层谓词（365 天逐日零分歧，32 天）；检查器发射
    32 天次。
  F 去重：全年含黄沙/红纱的日期，评分 shensha_list 无别名并存、无「黄沙日」
    「红砂日」残留。
  G 键表：('嫁娶','红纱日')=-20 在位；无 ('嫁娶','红砂日') 键。
  H 红纸帖：未命/鼠命新娘 抽样日 前三吉时不含冲命时辰；入宅模板不受过滤影响。
  I §194 挂账3/4：受死日嫁娶剥离扣分（0 分纯展示、规则层否决仍在）；红纸帖按
    实际吉时条数输出（无辰/寅/酉固定占位，0 条时提示谨慎择时）。

退出码：0=全过，1=有失败（FAIL N 计数）
  python tests/verify_嫁娶深水区修复.py
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


def _veto(d, owners):
    from modules.四柱计算器 import calculate_sizhu
    from modules.评分器 import calculate_score
    sz = calculate_sizhu(d, 10, 0)
    r = calculate_score(sz, '嫁娶', owners=owners)
    return r, sz


def main():
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha import get_checker
    from modules.评分器 import calculate_score, get_rule_checker
    from modules.rules import 嫁娶规则 as MARR
    from modules import 择日贴
    from modules.shensha.神煞基类 import is_shousi_by_zhi
    from modules.婚嫁评分算法 import is_sansang
    from modules.事项标准 import SHENSHA_SCORES

    # ============ A：源码层 ============
    print('[A] 源码层（剥注释后断言）')
    src_rule = _code_only(inspect.getsource(MARR))
    check('A 嫁娶规则剥注释后无「时柱」忌项发射',
          '时柱' not in src_rule, f"命中 {src_rule.count('时柱')} 次")
    check('A veto_keywords 无「冲新娘」子串口径', "'冲新娘'" not in src_rule)
    check("A veto_keywords 含「受死日」", "'受死日'" in src_rule)
    check('A 四柱冲事主走结构化登记 _hard_veto_chong',
          '_hard_veto_chong' in src_rule and 'self._hard_veto_chong.append' in src_rule)
    src_tie = _code_only(inspect.getsource(择日贴.prepare_entry))
    check('A 择日贴吉时接 _avoid_zhi 冲命过滤', '_avoid_zhi' in src_tie
          and "'嫁娶'" in src_tie)

    # ============ B：时柱解绑 ============
    print('[B] 时柱解绑（同日换时辰不改日课结论）')
    from modules.评分器 import calculate_score as _cs
    d = dt.date(2026, 3, 2)
    res = []
    for hh in (2, 6, 10, 14, 22):
        sz = calculate_sizhu(d, hh, 0)
        r = _cs(sz, '嫁娶', owners=[{'name': '新娘', '生肖': '猪', '性别': '女'}])
        res.append((hh, sz.get('hour_zhi'), r.get('score'), r.get('level')))
    vetoed = [x for x in res if not x[2]]
    check(f'B 2026-03-02 猪命五时辰结论一致（实测 {res}）',
          all(x[2] > 0 for x in res), f'{res}')
    sz = calculate_sizhu(d, 10, 0)
    rc = get_rule_checker('嫁娶')
    v = rc.check(sz, [{'name': '新娘', '生肖': '猪', '性别': '女'}])
    check('B 忌项无「时柱」条目（时柱不入日课）',
          not any('时柱' in str(x) for x in v[1]), f'{v[1]}')

    # ============ C：平权 ============
    print('[C] 事主平权 HARD_VETO（男女 + 附加事主同权）')
    d8 = dt.date(2026, 1, 8)   # 壬午日，午冲子（鼠）
    for tag, owner in (('新郎', {'name': '新郎', '生肖': '鼠', '性别': '男'}),
                       ('新娘', {'name': '新娘', '生肖': '鼠', '性别': '女'}),
                       ('父亲', {'name': '父亲', '生肖': '鼠', '性别': '男'})):
        r, _ = _veto(d8, [owner])
        check(f'C 2026-01-08 {tag}鼠 → 0 分否决（实得 {r.get("score")}/{r.get("level")}）',
              r.get('score') == 0 and '凶' in str(r.get('level')))
        check(f'C {tag} 否决原因含「冲{tag}」', f'冲{tag}' in str(r.get('reason')))
    r, _ = _veto(d8, [{'name': '新郎', '生肖': '牛', '性别': '男'}])
    check(f'C 反向：2026-01-08 新郎牛 不否决（实得 {r.get("score")}）',
          bool(r.get('score')))
    r6, _ = _veto(dt.date(2026, 6, 6), [{'name': '新郎', '生肖': '鼠', '性别': '男'}])
    check(f'C 2026-06-06（甲午月）新郎鼠 → 0 分否决（改前 62 分；实得 {r6.get("score")}）',
          r6.get('score') == 0)
    # 12 抽样（每节气月 1 天）：男女否决集恒等
    samples = [dt.date(2026, 1, 15), dt.date(2026, 2, 20), dt.date(2026, 3, 20),
               dt.date(2026, 4, 20), dt.date(2026, 5, 20), dt.date(2026, 6, 20),
               dt.date(2026, 7, 20), dt.date(2026, 8, 20), dt.date(2026, 9, 20),
               dt.date(2026, 10, 20), dt.date(2026, 11, 20), dt.date(2026, 12, 20)]
    diff = []
    for s in samples:
        rb, _ = _veto(s, [{'name': '新娘', '生肖': '猪', '性别': '女'}])
        rg, _ = _veto(s, [{'name': '新郎', '生肖': '猪', '性别': '男'}])
        if (rb.get('score') == 0) != (rg.get('score') == 0):
            diff.append((str(s), rb.get('score'), rg.get('score')))
    check(f'C 12 抽样日 男女否决集恒等（差异 {len(diff)}）', not diff, f'{diff}')

    # ============ D：受死日升 HARD_VETO ============
    print('[D] 受死日 HARD_VETO（2026 全 31 天）')
    d0, d1 = dt.date(2026, 1, 1), dt.date(2026, 12, 31)
    ss_days = []
    dd = d0
    while dd <= d1:
        sz = calculate_sizhu(dd, 10, 0)
        if is_shousi_by_zhi(sz['month_zhi'], sz['day_zhi']):
            ss_days.append(dd)
        dd += dt.timedelta(days=1)
    check(f'D 受死日天数=31（实得 {len(ss_days)}）', len(ss_days) == 31)
    leak = []
    for s in ss_days:
        v = get_rule_checker('嫁娶').check(calculate_sizhu(s, 10, 0), [])
        if not v[2]:
            leak.append(str(s))
    check(f'D 31 天全部 veto=True（漏网 {len(leak)}）', not leak, f'{leak[:5]}')
    check('D 否决原因含「受死日」（抽样 2026-01-05）',
          '受死日' in str(get_rule_checker('嫁娶').check(calculate_sizhu(dt.date(2026, 1, 5), 10, 0), [])[3]))

    # ============ E：重丧双口径对齐 ============
    print('[E] 重丧双口径对齐（神煞层 ≡ 算法层）')
    ck_jq = get_checker('嫁娶')
    mism = []
    zs_days = 0
    emit = 0
    dd = d0
    while dd <= d1:
        sz = calculate_sizhu(dd, 10, 0)
        sz['date'] = dd
        a = ck_jq._is_zhongsang(sz)
        b = is_sansang(dd)
        if a != b:
            mism.append(str(dd))
        if a:
            zs_days += 1
        if any(s.get('name') == '复日' for s in ck_jq.check(sz, [])):
            emit += 1
        dd += dt.timedelta(days=1)
    check(f'E 365 天两口径零分歧（不一致 {len(mism)}）', not mism, f'{mism[:5]}')
    # §197（2026-10-28 复日起例改正）重冻：农历双干混拼表 → 协纪正法单干·
    # 节气月建，2026 命中 32→34 天；注册名正名「复日」，旧「重丧日」名下线。
    check(f'E 复日天数=34（§197 起例改正；实得 {zs_days}）', zs_days == 34)
    check(f'E 检查器发射复日=34 天次（实得 {emit}）', emit == 34)

    # ============ F：重名去重 ============
    print('[F] 黄沙/红纱 重名去重（评分链路展示清单）')
    from modules.shensha.神煞基类 import _SHENSHA_ALIAS_KEY as ALIAS
    check("F 别名表 黄沙日→黄沙", ALIAS.get('黄沙日') == '黄沙')
    check("F 别名表 红砂日→红纱日", ALIAS.get('红砂日') == '红纱日')
    tgt_days = []
    dd = d0
    while dd <= d1:
        sz = calculate_sizhu(dd, 10, 0)
        # 用谓词口径取全量目标日（§212 后发射已剥离，不能靠发射清单取样）
        if ck_jq._is_huangsha(sz) or ck_jq._is_hongsha(sz):
            tgt_days.append(dd)
        dd += dt.timedelta(days=1)
    bad = []
    for s in tgt_days:
        r = calculate_score(calculate_sizhu(s, 10, 0), '嫁娶', owners=[])
        names = [x.get('name') for x in (r.get('shensha_list') or []) if isinstance(x, dict)]
        if any(n in ('黄沙日', '红砂日') for n in names):
            bad.append((str(s), [n for n in names if n in ('黄沙日', '红砂日')]))
        if any(n in ('黄沙', '红纱日') for n in names):
            bad.append((str(s), '§212 后不应发射'))
    check(f'F 目标日 {len(tgt_days)} 天 展示清单无别名/无残留（异常 {len(bad)}）',
          not bad, f'{bad[:4]}')
    # 抽样：2026-01-15 嫁娶 §212 后已剥离红纱日（0 条）
    r = calculate_score(calculate_sizhu(dt.date(2026, 1, 15), 10, 0), '嫁娶', owners=[])
    names = [x.get('name') for x in (r.get('shensha_list') or []) if isinstance(x, dict)]
    check(f'F 2026-01-15 红纱日 §212 后 0 条（清单={[n for n in names if "纱" in str(n) or "砂" in str(n)]}）',
          names.count('红纱日') == 0 and '红砂日' not in names)

    # ============ G：键表 ============
    print('[G] 键表')
    check("G ('嫁娶','红纱日')=-20 在位", SHENSHA_SCORES.get(('嫁娶', '红纱日')) == -20)
    check("G 无 ('嫁娶','红砂日') 键（归一后不再双计）",
          ('嫁娶', '红砂日') not in SHENSHA_SCORES)

    # ============ H：红纸帖吉时过滤 ============
    print('[H] 红纸帖吉时（冲命时辰不得印为吉时）')
    BAD = {'羊': '丑', '鼠': '午', '猪': '巳'}
    sample_days = [dt.date(2026, 1, 1), dt.date(2026, 3, 15), dt.date(2026, 6, 15),
                   dt.date(2026, 8, 15), dt.date(2026, 10, 15), dt.date(2026, 12, 15)]
    for zhi_sx, chong in BAD.items():
        bad = []
        empty = []
        for s in sample_days:
            e = 择日贴.prepare_entry({
                'date': s.strftime('%Y-%m-%d'), 'event_type': '嫁娶',
                'owners_list': [{'name': '新娘', 'role': '新娘', 'year_sx': zhi_sx}]})
            zhis = [j['zhi'] for j in e.get('_jishi', [])]
            if chong in zhis:
                bad.append((str(s), zhis))
            if len(zhis) < 3:
                empty.append((str(s), zhis))
        check(f'H {zhi_sx}命 抽样日 前三吉时不含冲命「{chong}」（违规 {len(bad)}）',
              not bad, f'{bad}')
        check(f'H {zhi_sx}命 抽样日吉时仍满 3 条（不足 {len(empty)}）', not empty, f'{empty}')

    e = 择日贴.prepare_entry({'date': '2026-01-01', 'event_type': '入宅'})
    from modules.今日黄历 import calc_shichen_jixiong
    sz = calculate_sizhu(dt.date(2026, 1, 1), 12, 0)
    hours = calc_shichen_jixiong(sz['day_gan'], sz['day_zhi'], sz['year_zhi'], sz['month_zhi'])
    top = [h['zhi'] for h in sorted([h for h in hours if h['score'] > 0],
                                    key=lambda x: -x['score'])[:4]]
    check(f'H 入宅模板吉时不受婚嫁过滤影响（{top} vs {[j["zhi"] for j in e.get("_jishi", [])]}）',
          top == [j['zhi'] for j in e.get('_jishi', [])])

    # ============ I：§194 挂账3/4 ============
    print('[I] §194：受死日纯展示 0 分 + 红纸帖按实际吉时条数输出')
    from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
    from modules.事项标准 import shensha_score
    src_m = _code_only(inspect.getsource(MarriageShenShaChecker))
    check("I1 受死日发射已剥离扣分（0 分纯展示）",
          "_add_shensha('受死日', 0" in src_m
          and "_add_shensha('受死日', -" not in src_m)
    check("I1 键表 ('嫁娶','受死日')=0 且 shensha_score=0",
          SHENSHA_SCORES.get(('嫁娶', '受死日')) == 0
          and shensha_score('嫁娶', '受死日') == 0)
    bad_ss = []
    for s in ss_days:
        sz = calculate_sizhu(s, 10, 0)
        rows = [x for x in ck_jq.check(sz, []) if x.get('name') == '受死日']
        if len(rows) != 1 or rows[0].get('score') != 0:
            bad_ss.append((str(s), [r.get('score') for r in rows]))
    check(f'I1 31 天受死日发射恒 0 分且唯一（异常 {len(bad_ss)}）', not bad_ss,
          f'{bad_ss[:4]}')
    r = calculate_score(calculate_sizhu(dt.date(2026, 1, 5), 10, 0), '嫁娶', owners=[])
    check(f'I1 受死日 0 分但结论仍否决（实得 {r.get("score")}/{r.get("level")}）',
          r.get('score') == 0 and '凶' in str(r.get('level')))

    # I2 红纸帖：按实际吉时条数输出，不得用固定辰/寅/酉 占位凑数
    src_cm = _code_only(inspect.getsource(择日贴.compose_marriage_lines))
    check('I2 红纸帖无固定占位时辰（辰/寅/酉 兜底已删）',
          '辰时（07:00' not in src_cm and '寅时（03:00' not in src_cm
          and '酉时（17:00' not in src_cm)
    check('I2 无可用吉时时给「今日吉时有限，请谨慎选择」提示',
          '今日吉时有限，请谨慎选择' in src_cm)
    e0 = 择日贴.prepare_entry({
        'date': '2026-01-01', 'event_type': '嫁娶',
        'owners_list': [{'name': '新娘', 'role': '新娘', 'year_sx': '羊'}]})
    e0['_jishi'] = []
    zero_txt = '\n'.join(t for _, t in 择日贴.compose_marriage_lines(e0))
    check('I2 无可用吉时：仅提示、不补任何时辰',
          '今日吉时有限，请谨慎选择' in zero_txt
          and not any(z in zero_txt for z in ('：辰时（', '：寅时（', '：酉时（')))
    bad_n = []
    for sx in ('羊', '鼠', '猪'):
        dd = d0
        while dd <= d1:
            ee = 择日贴.prepare_entry({
                'date': str(dd), 'event_type': '嫁娶',
                'owners_list': [{'name': '新娘', 'role': '新娘', 'year_sx': sx}]})
            _js = ee.get('_jishi') or []
            if _js:
                got = sum(1 for _, t in 择日贴.compose_marriage_lines(ee) if '时（' in t)
                if got != min(len(_js), 3):
                    bad_n.append((sx, str(dd), len(_js), got))
            dd += dt.timedelta(days=1)
    check(f'I2 全年×三生肖吉时行数恒等实际条数（异常 {len(bad_n)}）', not bad_n,
          f'{bad_n[:4]}')

    print()
    if FAILS:
        print(f'FAIL {len(FAILS)} 项：' + '、'.join(FAILS))
        return 1
    print('ALL PASS：嫁娶深水区修复批全绿')
    return 0


if __name__ == '__main__':
    sys.exit(main())
