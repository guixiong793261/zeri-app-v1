# -*- coding: utf-8 -*-
"""§66 ③收口验证：三煞家族神煞通道「识别展示，不计分」（2026-10-12 拍板执行）
================================================================================
拍板口径（方案A，用户 2026-10-12 确认）：
  年三煞(-18)/劫煞(-25)/灾煞(-25)/岁煞(-20) 注册保留、score 置 0、
  description 追加「（识别展示，不计分）」；评分器通道甲（三煞扣分 §63/§64）
  与忌事通道（ji -15）原样不动；嫁娶路径 trio 本就仅展示。

权威依据（硬编码，不从被测实现反推）：
  1) B-b 轨一 §9.10/§9.12（docs/典据研究_三煞概念正名_事主四柱全家族.md）：
     两口径均无典据（四书穷尽），与通道甲并存属工程性双重计分
     （受影响日实测三笔并存 -18 神煞 + -15 忌事 + -30 通道甲，279/279）。
  2) 影响面探针（C:\\Temp\\_probe_18_30_result.json / _probe_trio_result.json）：
     -18 影响面 279/1095（2026×入学/求医/签约）、trio 837/3285（2026×9 专属事项）；
     本 verify 的口径与探针补丁逐字一致（条目保留、score=0）。
  3) 2026-02-07 求医 = 7 天抽查释放日（三煞通道仍扣 -60~-70；原「岁破 ji 仍在」
     已随岁破批 001 §140 删除而不再成立）；2026-01-16 开业 = 上吉升级 4 例之一
     （吉神 8-9 个支撑）。

断言设计：
  正向——4 名命中时条目在列、score==0、description 带标注（走 Scorer 生产入口）
  反向——① 非三煞家族负分神煞分值不变、不带标注；
         ①' 岁破日课通道不再产生（-30 观测断言反转）：岁破批（2026-10-20，
            001 §140）删除日课普适岁破注册后，扫描窗内 shensha_list **不得**
            再出现 '岁破' 条目（二选一取「断言不存在」口径，不改断其他值）；
         ② 标注只出现在 4 名（标注⇔4名双向）；
         ③ SHENSHA_SCORES 表值不被回改（shensha_score 仍返回 -18/-25/-20，
            证明对账惯例保留、收口在解析层）；
         ④ 通道甲 sansha_penalty 仍 < 0；⑤ 忌事通道 ji 条目仍在；
         ⑥ 4 名在扫描窗口内逐一被观测到（覆盖保证，防空洞断言）。
退出码：0=全过，1=有失败（FAIL N 计数）
================================================================================
"""
import sys
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

FAILS = []


def check(name, cond, detail=''):
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}  {detail}")
        FAILS.append(name)


def main():
    from modules.四柱计算器 import calculate_sizhu
    from modules.评分器 import Scorer
    from modules.事项标准 import shensha_score

    TRIO_NAMES = ('年三煞', '劫煞', '灾煞', '岁煞')
    MARK = '（识别展示，不计分）'
    OWNER = [{'name': '主', 'role': '事主', 'birth_date': '1972-01-08', '生肖': '亥'}]
    EVENTS = ['求医', '修造']

    # ---------- 断言③ SHENSHA_SCORES 表值不被回改（解析层收口，对账惯例保留） ----------
    print('[1] SHENSHA_SCORES 表值保持原值（收口在解析层，不回改分值表）')
    table_expect = {
        ('入学', '年三煞'): -18, ('求医', '年三煞'): -18, ('签约', '年三煞'): -18,
        ('开业', '劫煞'): -25, ('开业', '灾煞'): -25, ('开业', '岁煞'): -20,
        ('修造', '劫煞'): None,  # 修造未登记 → 沿用注册默认 -25，表查询应返回 None
    }
    for (ev, nm), exp in table_expect.items():
        got = shensha_score(ev, nm, None)
        check(f'shensha_score({ev},{nm})', got == exp, f'期望 {exp} 实得 {got}')

    # ---------- 生产入口扫描（2026 上半年 × 求医/修造） ----------
    print('[2] 扫描 2026-01-01..06-30 × 求医/修造（Scorer 生产入口）')
    observed = {nm: 0 for nm in TRIO_NAMES}
    neg_non_trio_observed = 0
    suipo_observations = []
    invariant_bad = []
    d0, d1 = dt.date(2026, 1, 1), dt.date(2026, 6, 30)
    scorer = Scorer()
    d = d0
    while d <= d1:
        sz = calculate_sizhu(d, 12, 0)
        sz['date'] = d
        sz['year'] = d.year
        sz['month'] = d.month
        sz['day'] = d.day
        for ev in EVENTS:
            r = scorer.score(sz, ev, owners=OWNER)
            for s in r.get('shensha_list', []):
                if not isinstance(s, dict):
                    continue
                nm, sc, desc = s.get('name'), s.get('score'), s.get('description', '')
                if nm in TRIO_NAMES:
                    observed[nm] += 1
                    if sc != 0 or MARK not in desc:
                        invariant_bad.append((d.isoformat(), ev, nm, sc, desc))
                elif MARK in desc:
                    invariant_bad.append((d.isoformat(), ev, nm, sc, '标注泄漏到非三煞名'))
                if isinstance(sc, (int, float)) and sc < 0 and nm not in TRIO_NAMES:
                    neg_non_trio_observed += 1
                    if nm == '岁破':
                        suipo_observations.append((d.isoformat(), ev, sc, desc))
        d += dt.timedelta(days=1)

    print('[3] 正向不变式：4 名 → score==0 且带标注；标注 ⇔ 4 名（双向）')
    check('不变式双向成立（0 违例）', not invariant_bad, f'违例样例 {invariant_bad[:5]}')

    print('[4] 反向①：非三煞负分神煞分值不变、无标注（观测数>0 防空洞断言）')
    check('非三煞负分条目被观测到', neg_non_trio_observed > 0, f'观测数 {neg_non_trio_observed}')
    # ①' 岁破日课通道已删（岁破批 001 §140）：断言不存在，而非改断其他值
    check('岁破日课通道不再产生（岁破在扫描窗内零观测）', len(suipo_observations) == 0,
          f'观测到 {len(suipo_observations)} 条：{suipo_observations[:3]}')
    for dstr, ev, sc, desc in suipo_observations[:3]:   # 反证自检：若出现即报错
        check(f'岁破 {dstr} {ev} 不应存在（残留观测）', False,
              f'score={sc} desc={desc}')

    print('[5] 反向⑥：3 名覆盖保证（扫描窗内逐一观测，防空洞断言）；'
          '年三煞改为零观测（001 §211 墓碑化）')
    for nm in ('劫煞', '灾煞', '岁煞'):
        check(f'{nm} 被观测到（{observed[nm]} 次）', observed[nm] > 0)
    # 001 §211（2026-10-31 拍板二·案 B）：通用神煞「年三煞」以日支∈年三煞方发射，
    # 属四柱柱级判定（三库皆方道神，无柱级明文），与评分器四柱级通道同源一并旁路。
    check('年三煞 §211 墓碑化后零观测（原 279 次 → 0）', observed['年三煞'] == 0,
          f'观测数 {observed["年三煞"]}')

    # ---------- 断言④⑤ 探针实证日：通道甲/忌事通道不动 ----------
    print('[6] 探针实证日 2026-02-07 求医：神煞笔已墓碑、通道甲/忌事通道保留')
    sz = calculate_sizhu(dt.date(2026, 2, 7), 12, 0)
    sz.update({'date': dt.date(2026, 2, 7), 'year': 2026, 'month': 2, 'day': 7})
    r = scorer.score(sz, '求医', owners=OWNER)
    sh = {s.get('name'): s for s in r.get('shensha_list', []) if isinstance(s, dict)}
    check('年三煞条目已不在列（001 §211 墓碑化）', '年三煞' not in sh)
    si = r.get('sansha_info') or {}
    check('通道甲 sansha_penalty 仍 < 0（不动）',
          isinstance(si.get('sansha_penalty'), (int, float)) and si['sansha_penalty'] < 0,
          f"sansha_penalty={si.get('sansha_penalty')}")
    ji_join = ' | '.join(str(j) for j in (r.get('ji_list') or []))
    # 001 §211：年三煞柱级忌项（含 年三煞(月柱)/(日柱)/(时柱)）已随判定层旁路删除
    check('忌事通道 ji 不再含年三煞（柱级通道已删）',
          '年三煞' not in ji_join, f'ji_list={ji_join[:120]}')

    print('[7] 上吉升级实证日 2026-01-16 开业：trio 归零、吉神层不受影响')
    sz2 = calculate_sizhu(dt.date(2026, 1, 16), 12, 0)
    sz2.update({'date': dt.date(2026, 1, 16), 'year': 2026, 'month': 1, 'day': 16})
    r2 = scorer.score(sz2, '开业', owners=OWNER)
    sh2 = [s for s in r2.get('shensha_list', []) if isinstance(s, dict)]
    trio_hit = [s for s in sh2 if s.get('name') in TRIO_NAMES]
    check('至少一名 trio 命中', len(trio_hit) > 0)
    for s in trio_hit:
        check(f"{s.get('name')} score==0 且带标注",
              s.get('score') == 0 and MARK in s.get('description', ''), f"{s}")
    jishen = [s for s in sh2 if isinstance(s.get('score'), (int, float)) and s['score'] > 0]
    check('吉神条目仍为正分且无标注',
          all(MARK not in s.get('description', '') for s in jishen),
          f'吉神数 {len(jishen)}')

    print()
    if FAILS:
        print(f"FAIL {len(FAILS)}：{FAILS}")
        return 1
    print("ALL PASS（§66 三煞家族神煞通道识别展示不计分收口验证通过）")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('FAIL 1（脚本异常）')
        sys.exit(1)
