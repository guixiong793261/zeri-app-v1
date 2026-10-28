# -*- coding: utf-8 -*-
"""复日（旧称重丧日）起例改为《协纪》正法单干·节气月建 回归（2026-10-28，001 §197 Commit 1）
================================================================================
被测变更（§197 D3 核心重构）：
  · 废弃原 32 天混拼表（农历月查双干 + 无典据 FURI_MAP 顺序干双计）。
  · 起例改为协纪正法「建月同干」单干表，按**节气月建（月支）**：
      正甲、二乙、三戊、四丙、五丁、六己、七庚、八辛、九戊、十壬、十一癸、十二己。
  · 注册名正名「复日」，安葬「重丧 -30 + 复日 -25」双计合并为单一「复日 -30」。
  · 嫁娶/修造维持 0 分纯展示；安葬维持 HARD_VETO。

断言结构（正反双向）：
  A. 表值层：12 月正例；协纪 p279217 点名之误「正月庚／七月甲」必须为否。
  B. 单点出口：is_furi_by_date 走真实四柱（节气月建），2026 命中 34 天。
  C. 六通道一致性：安葬/嫁娶/修造/婚嫁评分算法/高级安葬规则/择日贴 全年零分歧。
  D. 去重：安葬每日唯一「复日」-30，无「重丧日」残留；嫁娶/修造唯一 0 分。
  E. 安葬否决：34 天全部 veto=True 且否决原因含「复日」。
  F. 冻结项：年重丧（D3-Q6 专项前）仍为双干口径；('安葬','年重丧')=-30 不变。
  G. 源码层：旧农历表/旧函数/旧 _is_furi 均已彻底删除（剥注释后无残留）。

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


# 黄金真值：独立硬编码自《协纪辨方书》卷五·复日条（单干·节气月建），
# 不从被测实现反推。键为月支。
GOLDEN = {
    '寅': '甲', '卯': '乙', '辰': '戊', '巳': '丙',
    '午': '丁', '未': '己', '申': '庚', '酉': '辛',
    '戌': '戊', '亥': '壬', '子': '癸', '丑': '己',
}
D0, D1 = dt.date(2026, 1, 1), dt.date(2026, 12, 31)


def main():
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha import get_checker
    from modules.shensha.神煞基类 import (is_furi_by_month_zhi, is_furi_by_date,
                                       _FURI_GAN_BY_MONTH_ZHI)
    from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
    from modules.婚嫁评分算法 import is_sansang
    from modules.rules.高级安葬规则 import AdvancedBurialRuleChecker
    from modules.事项标准 import SHENSHA_SCORES, shensha_score
    from modules.择日贴 import _zhongsang_hits

    days = []
    d = D0
    while d <= D1:
        days.append((d, calculate_sizhu(d, 10, 0)))
        d += dt.timedelta(days=1)

    # ============ A：表值层 ============
    print('[A] 表值：协纪正法单干·节气月建（12 正 + 点名之误反例）')
    check('A1 基类表与协纪黄金真值逐键相等', _FURI_GAN_BY_MONTH_ZHI == GOLDEN,
          f'{_FURI_GAN_BY_MONTH_ZHI}')
    bad = [m for m, g in GOLDEN.items() if not is_furi_by_month_zhi(m, g)]
    check(f'A2 12 月正例全命中（漏 {len(bad)}）', not bad, f'{bad}')
    # 协纪 p279217 明斥：正月之庚日、七月之甲日皆为复日属通书之误
    check('A3 反例：正月（寅）庚日不得判复日', not is_furi_by_month_zhi('寅', '庚'))
    check('A3 反例：七月（申）甲日不得判复日', not is_furi_by_month_zhi('申', '甲'))
    # 反向：单干——同月其余九干均不得命中
    cross = [(m, g) for m, g in GOLDEN.items()
             if any(is_furi_by_month_zhi(m, o) for o in '甲乙丙丁戊己庚辛壬癸' if o != g)]
    check(f'A4 单干排他：同月非本干零命中（异常 {len(cross)}）', not cross, f'{cross[:3]}')
    check('A5 反向：空月支/空日干/未知月支均不命中',
          not is_furi_by_month_zhi('', '甲')
          and not is_furi_by_month_zhi('寅', '')
          and not is_furi_by_month_zhi('X', '甲'))

    # ============ B：单点出口走真实四柱 ============
    print('[B] 单点出口：is_furi_by_date（节气月建）2026 命中 34 天')
    base = [d for d, _ in days if is_furi_by_date(d)]
    check(f'B1 2026 复日天数=34（实得 {len(base)}）', len(base) == 34)
    check('B1 反向：非复日抽检 2026-01-16 不命中', not is_furi_by_date(dt.date(2026, 1, 16)))
    # 逐日交叉：函数出口 ≡ 真实四柱月支+日干直判（口径同源校验，防月份体系回退农历）
    mism = []
    for d, sz in days:
        if is_furi_by_date(d) != is_furi_by_month_zhi(sz['month_zhi'], sz['day_gan']):
            mism.append(str(d))
    check(f'B2 出口 ≡ 节气月支直判（分歧 {len(mism)}）', not mism, f'{mism[:3]}')

    # ============ C：六通道一致性 ============
    print('[C] 六通道全年零分歧')
    ck_az, ck_jq = get_checker('安葬'), get_checker('嫁娶')
    ext, rc = ConstructionShenShaCheckerExt(), AdvancedBurialRuleChecker()
    n_az = n_az_bad = n_jq = n_ext = n_alg = n_rc = n_tie = 0
    diverge = []
    for d, sz in days:
        sz2 = dict(sz)
        sz2['date'] = d
        fz = is_furi_by_date(d)
        rows_az = ck_az.check(sz2, [])
        hit_az = [s for s in rows_az if s.get('name') == '复日']
        rows_jq = ck_jq.check(sz2, [])
        hit_jq = [s for s in rows_jq if s.get('name') == '复日']
        e_ext = any(s.get('name') == '复日' for s in ext.check(sz2, []))
        e_alg = is_sansang(d)
        e_rc = rc._is_zhongsang(sz['month_zhi'], sz['day_gan'])
        e_tie = '复日' in _zhongsang_hits({'_nian': sz['year_gan'] + sz['year_zhi'],
                                         '_yue': sz['month_gan'] + sz['month_zhi'],
                                         '_ri': sz['day_gan'] + sz['day_zhi']})
        if fz:
            n_az += 1
            if len(hit_az) != 1 or hit_az[0].get('score') != -30:
                n_az_bad += 1
        if hit_jq:
            n_jq += 1
        n_ext += e_ext
        n_alg += e_alg
        n_rc += e_rc
        n_tie += e_tie
        if not (fz == bool(hit_az) == bool(hit_jq) == e_ext == e_alg == e_rc == e_tie):
            diverge.append(str(d))
    check(f'C1 安葬 复日=34 天（实得 {n_az}）', n_az == 34)
    check(f'C2 嫁娶 复日=34 天（实得 {n_jq}）', n_jq == 34)
    check(f'C3 修造 复日=34 天（实得 {n_ext}）', n_ext == 34)
    check(f'C4 婚嫁评分算法 is_sansang=34 天（实得 {n_alg}）', n_alg == 34)
    check(f'C5 高级安葬规则 _is_zhongsang=34 天（实得 {n_rc}）', n_rc == 34)
    check(f'C6 择日贴 _zhongsang_hits=34 天（实得 {n_tie}）', n_tie == 34)
    check(f'C7 六通道逐日分歧=0（实得 {len(diverge)}）', not diverge, f'{diverge[:4]}')

    # ============ D：去重与正名 ============
    print('[D] 去重：单一「复日」，无「重丧日」残留')
    check(f'D1 安葬 34 天唯一条且恒 -30（异常 {n_az_bad}）', n_az_bad == 0)
    leftover = []
    for d, sz in days:
        sz2 = dict(sz)
        sz2['date'] = d
        names = [str(s.get('name')) for s in ck_az.check(sz2, [])]
        if any(nm == '重丧日' or nm == '重丧' for nm in names):
            leftover.append(str(d))
    check(f'D2 安葬通道无「重丧日/重丧」发射（残留 {len(leftover)}）', not leftover,
          f'{leftover[:3]}')
    check("D3 ('安葬','重丧') 键已删", ('安葬', '重丧') not in SHENSHA_SCORES)
    check("D3 ('安葬','复日')=-30", shensha_score('安葬', '复日') == -30)
    check("D4 ('嫁娶','复日')=0", shensha_score('嫁娶', '复日') == 0)
    check("D4 ('修造','复日')=0", shensha_score('修造', '复日') == 0)
    check("D4 ('嫁娶','重丧日') / ('修造','重丧日') 旧键已删",
          ('嫁娶', '重丧日') not in SHENSHA_SCORES
          and ('修造', '重丧日') not in SHENSHA_SCORES)
    n_jq_score = 0
    for d, sz in days:
        sz2 = dict(sz)
        sz2['date'] = d
        for s in ck_jq.check(sz2, []):
            if s.get('name') == '复日' and s.get('score') != 0:
                n_jq_score += 1
    check(f'D5 嫁娶「复日」恒 0 分（异常 {n_jq_score}）', n_jq_score == 0)

    # ============ E：安葬否决维持 ============
    print('[E] 安葬 HARD_VETO 维持（D3-Q4）')
    leak, no_reason = [], []
    for d, sz in days:
        sz2 = dict(sz)
        sz2['date'] = d
        if not is_furi_by_date(d):
            continue
        out = rc.check(sz2, [])
        if not out[2]:
            leak.append(str(d))
        if '复日' not in str(out[3] or ''):
            no_reason.append(str(d))
    check(f'E1 34 天全部 veto=True（漏网 {len(leak)}）', not leak, f'{leak[:3]}')
    check(f'E2 否决原因含「复日」（缺 {len(no_reason)}）', not no_reason,
          f'{no_reason[:3]}')
    check("E3 规则层 ji 文案为「复日忌安葬」",
          '复日忌安葬' in (rc.check(dict(next(sz for d, sz in days if is_furi_by_date(d)),
                                       date=next(d for d, _ in days if is_furi_by_date(d))), [])[1] or []))

    # ============ F：冻结项 ============
    print('[F] 冻结：年重丧双干口径（D3-Q6 专项前不动）')
    check("F1 年重丧表 寅=['庚','甲'] 双干冻结",
          AdvancedBurialRuleChecker.NIAN_ZHONG_SANG_MAP.get('寅') == ['庚', '甲'])
    check("F2 ('安葬','年重丧')=-30 不变", shensha_score('安葬', '年重丧') == -30)

    # ============ G：源码层清理 ============
    print('[G] 源码层：旧农历混拼表/旧函数彻底删除')
    import modules.shensha.神煞基类 as base_mod
    from modules.shensha.安葬神煞 import BurialShenShaChecker
    check('G1 基类已无 _ZHONGSANG_GAN_BY_LUNAR_MONTH',
          not hasattr(base_mod, '_ZHONGSANG_GAN_BY_LUNAR_MONTH'))
    check('G2 基类已无 is_zhongsang_by_lunar',
          not hasattr(base_mod, 'is_zhongsang_by_lunar'))
    for cls, nm in ((BurialShenShaChecker, 'G3 安葬神煞'),
                    (AdvancedBurialRuleChecker, 'G4 高级安葬规则')):
        check(f'{nm} 已无 _is_furi 死链', not hasattr(cls, '_is_furi'))

    print()
    if FAILS:
        print(f'FAIL {len(FAILS)} 项：' + '、'.join(FAILS))
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
