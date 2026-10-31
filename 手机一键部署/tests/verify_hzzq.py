# -*- coding: utf-8 -*-
"""
红嘴朱雀按典修批·回归验证（2026-10-20）

依据：
  - 判据冻结提案 docs/判据冻结提案_红嘴朱雀按典修专项.md（3ed2cdf）D-HZZQ-1~7
  - 影响面快照 docs/影响面快照_红嘴朱雀六集合.md（91a5bcb）六集合 A~F
  - 用户第十轮拍板：有载则 -30（拒 -12 弱化档）、通用 5 键直删、
    中宮文案含「归火」、移徙随入宅同改

校验段：
  A. D-HZZQ-1 表源：60 甲子宫序 (n-1) mod 9 与陈书 p890 九宫全等（逐宫逐柱）。
  B. 旧起例彻底消失：源码剥注释后，入宅/通用两处森林无
     _is_hongzui_zhuque 定义、无 hongzui_map/chong_map 月起例、无红嘴朱雀发射；
     基类唯一实现且按 day_pillar 判定（不含 month_zhi）。
  C. D-HZZQ-2/3 触发：入宅红嘴朱雀日 ≡ 中宮集合（43 天）；反向 A（月支+1）
     与 B（月支对冲+2）旧起例日除与中宮重合者外一律不触发。
  D. 新增三通道：嫁娶 ≡ 坤宮（36）、安床 ≡ 乾宮（43）、作灶 ≡ 震宮（42），
     分值均 -30（拒 -12 弱化档）。
  E. 通用四通道（入学/求医/签约/通用）红嘴朱雀 = 0 天。
  F. 键表：3 新键 -30 在位；5 旧键（含移徙休眠键）不存在；无通配；总键 1262
     （受死日删除批 1265→1262）。
  G. 天次与总分基线：业务五通道 147→207；入宅/移徙 4464、嫁娶 -612、
     安床 5451、作灶 -1369（受死日删除批抬分 +682；2026 全年，owners=[]）。
  H. 文案：中宮日描述含「归火」（对齐陈书「忌入宅歸火」）；非中宮日无。
  I. 非目标煞不变：入宅受死日 31（受死日收敛后表A）；其余 6 通道红嘴朱雀 0。

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


ZH = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
GAN = '甲乙丙丁戊己庚辛壬癸'
ALL60 = [GAN[i % 10] + ZH[i % 12] for i in range(60)]
GONG_ORDER = ['震', '巽', '中', '乾', '兌', '艮', '離', '坎', '坤']
GONG = {
    '震': ['甲子', '癸酉', '壬午', '辛卯', '庚子', '己酉', '戊午'],
    '巽': ['乙丑', '甲戌', '癸未', '壬辰', '辛丑', '庚戌', '己未'],
    '中': ['丙寅', '乙亥', '甲申', '癸巳', '壬寅', '辛亥', '庚申'],
    '乾': ['丁卯', '丙子', '乙酉', '甲午', '癸卯', '壬子', '辛酉'],
    '兌': ['戊辰', '丁丑', '丙戌', '乙未', '甲辰', '癸丑', '壬戌'],
    '艮': ['己巳', '戊寅', '丁亥', '丙申', '乙巳', '甲寅', '癸亥'],
    '離': ['庚午', '己卯', '戊子', '丁酉', '丙午', '乙卯'],
    '坎': ['辛未', '庚辰', '己丑', '戊戌', '丁未', '丙辰'],
    '坤': ['壬申', '辛巳', '庚寅', '己亥', '戊申', '丁巳'],
}
CHONG = {'子': '午', '丑': '未', '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
         '午': '子', '未': '丑', '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'}
D0, D1 = dt.date(2026, 1, 1), dt.date(2026, 12, 31)


def pillar(sz):
    return sz['day_gan'] + sz['day_zhi']


def main():
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha import get_checker
    from modules.shensha import 神煞基类 as BASE
    from modules.shensha import 入宅神煞, 通用神煞
    from modules.事项标准 import SHENSHA_SCORES, shensha_score

    days = []
    d = D0
    while d <= D1:
        days.append((d, calculate_sizhu(d, 10, 0)))
        d += dt.timedelta(days=1)

    # ============ A：D-HZZQ-1 表源（60 甲子宫序） ============
    print('[A] D-HZZQ-1 表源：60 甲子宫序 (n-1) mod 9 ↔ 陈书 p890')
    bad = []
    for g, lst in GONG.items():
        for gz in lst:
            if ALL60.index(gz) % 9 != GONG_ORDER.index(g):
                bad.append((g, gz))
    check('A 九宫干支表与 (n-1) mod 9 全等（bad=0）', not bad, f'{bad}')
    check('A 60 甲子九宫无重无漏（60 柱）',
          sorted(sum(GONG.values(), [])) == sorted(ALL60))
    lib = BASE._HONGZUI_PILLARS_BY_GONG
    diff = [(g, sorted(set(GONG[g]) ^ set(lib.get(g, ())))) for g in GONG
            if set(GONG[g]) != set(lib.get(g, ()))]
    check('A 基类 _HONGZUI_PILLARS_BY_GONG 与典载九宫逐宫全等', not diff, f'{diff}')

    # ============ B：旧起例彻底消失 ============
    print('[B] 旧起例删除（源码剥注释 + 谓词归属）')
    src_ru = _code_only(inspect.getsource(入宅神煞))
    src_cm = _code_only(inspect.getsource(通用神煞))
    for nm, src in (('入宅', src_ru), ('通用', src_cm)):
        check(f'B {nm} 无 _is_hongzui_zhuque 定义（子类旧谓词已删）',
              'def _is_hongzui_zhuque' not in src)
        check(f'B {nm} 无月起例残留（hongzui_map 已删）',
              'hongzui_map' not in src)
    check('B 入宅红嘴朱雀发射唯一且为 -30（中宮）',
          src_ru.count("'红嘴朱雀'") == 1
          and "self._is_hongzui_zhuque(sizhu, '中')" in src_ru,
          f"发射数={src_ru.count(chr(39) + '红嘴朱雀' + chr(39))}")
    check('B 通用红嘴朱雀发射/引用全删（剥注释后 0 命中）',
          '红嘴朱雀' not in src_cm)
    base_src = inspect.getsource(BASE.ShenShaChecker._is_hongzui_zhuque)
    check('B 基类唯一实现按 day_pillar 判定（不含 month_zhi）',
          'day_gan' in base_src and 'month_zhi' not in base_src)
    check('B 基类实现委托 is_hongzui_in_gong',
          'is_hongzui_in_gong' in base_src)

    # ============ C：触发集合 ≡ 中宮；旧 A/B 反向不触发 ============
    print('[C] 入宅 ≡ 中宮（C）；反向 A/B 旧起例不触发')
    ck_ru = get_checker('入宅')
    hit_ru = {}
    desc_ru = {}
    for d, sz in days:
        for s in ck_ru.check(sz, []):
            if s.get('name') == '红嘴朱雀':
                hit_ru[d] = s.get('score')
                desc_ru[d] = s.get('desc') or s.get('description') or ''
    C = {d for d, sz in days if pillar(sz) in GONG['中']}
    check(f'C 入宅红嘴朱雀日 ≡ 中宮集合（{len(C)} 天）',
          set(hit_ru) == C,
          f'多={sorted(set(hit_ru) - C)[:3]} 少={sorted(C - set(hit_ru))[:3]}')
    check('C 中宮日命中率=100%（3/43 旧 → 43/43 新）', len(set(hit_ru) & C) == len(C))
    check('C 入宅红嘴朱雀分值恒 -30', set(hit_ru.values()) == {-30}, f'{set(hit_ru.values())}')

    # 旧起例 A（月支+1）与 B（月支对冲+2）复算，除与中宮重合者外不得触发
    old_A = {d for d, sz in days
             if sz['day_zhi'] == ZH[(ZH.index(sz['month_zhi']) + 1) % 12]}
    old_B = {d for d, sz in days
             if sz['day_zhi'] == ZH[(ZH.index(CHONG[sz['month_zhi']]) + 2) % 12]}
    check(f'C 反向：A\\C（{len(old_A - C)} 天）旧起例日不触发',
          not (old_A - C) & set(hit_ru))
    check(f'C 反向：B\\C（{len(old_B - C)} 天）旧起例日不触发',
          not (old_B - C) & set(hit_ru))
    check('C A∩C=3、C\\A=40（快照 91a5bcb 口径）',
          len(old_A & C) == 3 and len(C - old_A) == 40,
          f'A∩C={len(old_A & C)} C\\A={len(C - old_A)}')

    # ============ D：新增三通道 ≡ 坤/乾/震 ============
    print('[D] 新增三通道（嫁娶/安床/作灶）≡ 典三宫')
    for ev, g in (('嫁娶', '坤'), ('安床', '乾'), ('作灶', '震')):
        ck = get_checker(ev)
        hits = {}
        for d, sz in days:
            for s in ck.check(sz, []):
                if s.get('name') == '红嘴朱雀':
                    hits[d] = s.get('score')
        exp = {d for d, sz in days if pillar(sz) in GONG[g]}
        check(f'D {ev} ≡ {g}宮（{len(exp)} 天）',
              set(hits) == exp,
              f'多={len(set(hits) - exp)} 少={len(exp - set(hits))}')
        check(f'D {ev} 分值恒 -30（拒 -12 弱化档）',
              set(hits.values()) == {-30}, f'{set(hits.values())}')

    # ============ E：通用四通道清零 ============
    print('[E] 通用四通道红嘴朱雀清零')
    for ev in ('入学', '求医', '签约', '通用'):
        ck = get_checker(ev)
        n = sum(1 for _, sz in days
                for s in ck.check(sz, []) if s.get('name') == '红嘴朱雀')
        check(f'E {ev} 红嘴朱雀=0（实得 {n}）', n == 0)

    # ============ F：键表 ============
    print('[F] 键表（3 新键 / 5 旧键 / 总键 1262）')
    for ev in ('嫁娶', '安床', '作灶'):
        check(f"F ('{ev}','红嘴朱雀')=-30",
              SHENSHA_SCORES.get((ev, '红嘴朱雀')) == -30,
              f"{SHENSHA_SCORES.get((ev, '红嘴朱雀'))}")
        check(f"F shensha_score('{ev}','红嘴朱雀')=-30",
              shensha_score(ev, '红嘴朱雀') == -30)
    for ev in ('入宅', '移徙', '入学', '求医', '签约'):
        check(f"F 旧键 ('{ev}','红嘴朱雀') 已删",
              (ev, '红嘴朱雀') not in SHENSHA_SCORES)
        check(f"F shensha_score('{ev}','红嘴朱雀')=None（无通配兜底）",
              shensha_score(ev, '红嘴朱雀') is None)
    check("F 通配键 ('*','红嘴朱雀') 不存在", ('*', '红嘴朱雀') not in SHENSHA_SCORES)
    check(f'F 总键数=1154（批次1 1200 → 建除批次1 001 §161 删 (开业,破日) → 1199；'
          f'福星批 001 §165 删 福星×14 键 → 1185；福星正统落地批 001 §169 加回 14 键 → 1199；'
          f'P0 大清理 001 §172 删 岁害14/天耗13/地耗14/非嫁娶孤辰寡宿11 → 1147；'
          f'出行双通道割裂修复批 001 §183 新增 (出行,日破时) → 1148；建除十二神×出行 D 专项 001 §184 新增 6 键 → 1154；'
          f'§196 D4 新增 (嫁娶,年命冲岁) -15 → 1155；§197 D3-Q1/Q5 安葬「重丧」并入「复日」净删 1 键 → 1154；'
          f'§208 错表作废批删 (安床,冲床日)/(安床,胎神日) 2 键 → 1152；'
          f"§209 开业卷十接线级补齐加 天愿/四相/时德/五合/五离 5 键，"
          f"清 ('*','小耗')/('*','大耗') 2 死键 → 1155；实得 {len(SHENSHA_SCORES)}）",
          len(SHENSHA_SCORES) == 1155)
    n_yi = len([k for k in SHENSHA_SCORES if k[0] == '移徙'])
    check(f'F 移徙块键数=67（§165 删 福星×移徙 → 70；福星正统落地批 001 §169 +1 恢复 → 71；'
          f'§172 删 岁害/天耗/地耗/孤辰寡宿×移徙 4 键 → 67；实得 {n_yi}）',
          n_yi == 67)

    # ============ G：天次与总分基线 ============
    print('[G] 天次与总分基线（2026 全年，owners=[]）')
    tot = {}
    cnt = {}
    for ev in ('入宅', '移徙', '嫁娶', '安床', '作灶', '开业', '入学', '求医', '签约', '通用'):
        ck = get_checker(ev)
        n = 0
        s_tot = 0
        for _, sz in days:
            for s in ck.check(sz, []):
                s_tot += s.get('score', 0)
                if s.get('name') == '红嘴朱雀':
                    n += 1
        tot[ev], cnt[ev] = s_tot, n
    check('G 业务五通道红嘴朱雀天次合计=207（快照 147→207）',
          sum(cnt[e] for e in ('入宅', '移徙', '嫁娶', '安床', '作灶')) == 207,
          f"{sum(cnt[e] for e in ('入宅','移徙','嫁娶','安床','作灶'))}")
    # 轻重层批次1（001 §158）：B 组 10 项调档后实测重冻——入宅/移徙 3377、
    # 嫁娶 214、安床 5242、作灶 -1315（前值 4464/4464/-612/5451/-1369）。
    # 轻重层批次2（001 §159）：鸣吠统一高档后，9 低档通道各 +368——
    # 入宅/移徙 3745、安床 5610、作灶 -947（嫁娶属原高档，维持 214）。
    # 福星批（001 §165）：删伪福星（岁破同构）——凡持键通道各 -310
    # （2026 伪福星 31 天次×10，对拍探针批前批后实测），嫁娶 214→-96。
    # 干支类实现Bug清理批（001 §171）：蚕官/畜官去重（同谓词双扣消除）
    # ——15 通道各 +310（31 天次×10），嫁娶 -96→214、入宅/移徙 3435→3745、
    # 安床 5300→5610、作灶 -1257→-947。
    # P0 大清理批（001 §172）：岁害/天耗/地耗全删（+982）＋年家族 12 项置 0
    # （+4439）＋非嫁娶年支孤辰删（+900）＋修造族大耗620/小耗450 删；
    # 嫁娶孤辰年支法删（月令法保留，105→61 天次）→ 各通道抬分：
    # 入宅/移徙 +7391 → 11136，嫁娶 +6081 → 6295，安床 +6321 → 11931，
    # 作灶 +7391 → 6444。
    # §193 主轨 C2（2026-10-28）重丧日双口径对齐：嫁娶神煞重丧发射 5→32 天
    # （表值 -10/日，净 -270），嫁娶 6295→6025；其余通道不受影响。
    # §194 挂账3（2026-10-28）受死日嫁娶剥离扣分（HARD_VETO 后纯展示 0 分）：
    # 31 天次 × +15 → 6025→6490；其余通道（含入宅）不受影响。
    # §195 Commit1（2026-10-28）入宅/移徙 受死日剥离扣分（§190 HARD_VETO）：
    # 31 天次 × +15 → 11136→11601。
    # §196 D1（2026-10-28）嫁娶重丧日撤否决撤扣分（三库明言吉事不忌）：
    # 32 天次 × +10 → 6490→6810；其余通道不受影响。
    # §208（2026-10-31）错表作废批：安床删「胎神日」（错表，29 天次×+15=+435）
    # 与「冲床日」（月破别名，31 天次×+12=+372）→ 11931+807=12738；其余通道不变。
    # §209（2026-10-31）开业卷十接线级补齐：天愿 35×+12=+420、四相 71×+10=+710、
    # 时德 30×+10=+300、五合 62×+10=+620、五离 60×-20=-1200，净 +850
    # → 开业 12897→13747。
    for ev, exp in (('入宅', 11601), ('移徙', 11601), ('嫁娶', 6810),
                    ('安床', 12738), ('作灶', 6444), ('开业', 13747)):
        check(f'G {ev} 全年总分={exp}（实得 {tot[ev]}）', tot[ev] == exp)

    # ============ H：中宮日文案含「归火」 ============
    print('[H] 中宮日文案（忌入宅、归火）')
    bad_desc = [str(d) for d, dz in desc_ru.items() if '归火' not in dz]
    check('H 全部中宮日描述含「归火」', not bad_desc, f'{bad_desc[:3]}')
    others = [s.get('desc') or s.get('description') or ''
              for d, sz in days if d not in C
              for s in ck_ru.check(sz, []) if s.get('name') == '红嘴朱雀']
    check('H 非中宮日无红嘴朱雀（反向文案面为空）', not others)

    # ============ I：非目标煞不变 ============
    print('[I] 非目标煞基线')
    n_ss = sum(1 for _, sz in days
               for s in ck_ru.check(sz, []) if s.get('name') == '受死日')
    check(f'I 入宅受死日=31（受死日收敛后表A基线，实得 {n_ss}）', n_ss == 31)
    for ev in ('修造', '动土', '拆舍', '出行', '开业', '安葬'):
        ck = get_checker(ev)
        n = sum(1 for _, sz in days
                for s in ck.check(sz, []) if s.get('name') == '红嘴朱雀')
        check(f'I {ev} 红嘴朱雀=0（无关联注册，实得 {n}）', n == 0)

    print()
    if FAILS:
        print(f'FAIL {len(FAILS)} 项：')
        for f in FAILS:
            print('  -', f)
        return 1
    print('ALL PASS：红嘴朱雀按典修批全绿')
    return 0


if __name__ == '__main__':
    sys.exit(main())
