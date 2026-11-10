# -*- coding: utf-8 -*-
"""
§209 开业卷十接线级补齐 + 安床胎神 C 步降级·回归验证（2026-10-31）

依据：
  - 用户 §209 拍板：开业先补「接线级缺口」（天愿/四相/时德/五合/五离），
    顺手清 ('*','小耗')/('*','大耗') 两枚死键；起例级缺口（天仓/四耗/四穷/
    九空）单独立项缓办。胎神走 C→B→A，C 步先降为 0 分展示。
  - 快照 docs/开业协纪卷十神煞发射现状快照_20261031.md（B 组 5 项口径）
  - 立项书 docs/胎神占床方位体系重建专项立项书_20261031.md（C→B→A 路径）

校验段：
  A. 键表层：5 新键与分值在位；('*','小耗')/('*','大耗') 已删；总键 1155。
  B. 发射天次：开业 2026 全年 天愿35 / 四相71 / 时德30 / 五合62 / 五离60；
     五合与五离发射日集合互斥。
  C. 谓词归属：开业走基类 _is_tianyuan/_is_sixiang/_is_shide/_is_wuli；
     五合为本地实现（基类尚无），口径 = 日支寅卯。
  D. 总分：开业 12897→13747（+850 = 420+710+300+620-1200）；安床 12738 不变。
  E. 死键反证：15 通道 2026 全年 小耗/大耗 发射 = 0（删键零行为差）。
  F. 胎神 C 步：占床/占房床 恒 0 分、文案含「家有孕妇」；无 ('安床','胎神*')
     注册键；占位覆盖 122 天（占床49 / 占房床61 / 床+房床合并12）；全通道
     无任何负分「胎神」项。

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

CH15 = ['入宅', '嫁娶', '动土', '修造', '拆舍', '出行', '开业', '安床', '作灶',
        '安葬', '移徙', '入学', '求医', '签约', '通用']
D0, D1 = dt.date(2026, 1, 1), dt.date(2026, 12, 31)


def check(name, cond, detail=''):
    if cond:
        print(f'  PASS  {name}')
    else:
        print(f'  FAIL  {name}  {detail}')
        FAILS.append(name)


def _code_only(src):
    """剥掉 # 注释（墓碑注释含原实现，须剔除后断言）。"""
    return '\n'.join(ln.split('#', 1)[0] for ln in src.splitlines())


def main():
    from modules.四柱计算器 import calculate_sizhu
    from modules.shensha import get_checker
    from modules.shensha import 神煞基类 as BASE
    from modules.shensha import 开业神煞, 通用神煞
    from modules.事项标准 import SHENSHA_SCORES, shensha_score

    days = []
    d = D0
    while d <= D1:
        days.append((d, calculate_sizhu(d, 10, 0)))
        d += dt.timedelta(days=1)

    # ============ A：键表层 ============
    print('[A] 键表层：5 新键 / 2 死键 / 总键数')
    exp5 = {('开业', '天愿'): 12, ('开业', '四相'): 10, ('开业', '时德'): 10,
            ('开业', '五合'): 10, ('开业', '五离'): -20}
    for k, v in exp5.items():
        check(f'A 键 {k} = {v}（实得 {SHENSHA_SCORES.get(k, "<无>")}）',
              SHENSHA_SCORES.get(k) == v)
    for nm in ('小耗', '大耗'):
        check(f"A 死键 ('*','{nm}') 已删（§209 清理）",
              ('*', nm) not in SHENSHA_SCORES)
        check(f"A shensha_score('开业','{nm}') 不因删通配键而报错",
              shensha_score('开业', nm) is None and ('开业', nm) not in SHENSHA_SCORES)
    check(f'A 总键数=1155（§209 加 5 键、删 2 死键，实得 {len(SHENSHA_SCORES)}）',
          len(SHENSHA_SCORES) == 1155)

    # ============ B：发射天次 ============
    print('[B] 发射天次（开业 2026 全年，owners=[]）')
    ck = get_checker('开业')
    cnt = {n: 0 for n in ('天愿', '四相', '时德', '五合', '五离')}
    tot_open = 0
    he_days, li_days = set(), set()
    for dte, sz in days:
        for s in ck.check(sz, []):
            tot_open += s.get('score', 0)
            nm = s.get('name', '')
            if nm in cnt:
                cnt[nm] += 1
            if nm == '五合':
                he_days.add(dte)
            elif nm == '五离':
                li_days.add(dte)
    exp_cnt = {'天愿': 35, '四相': 71, '时德': 30, '五合': 62, '五离': 60}
    for n, v in exp_cnt.items():
        check(f'B {n} 天次={v}（实得 {cnt[n]}）', cnt[n] == v)
    check('B 五合/五离发射日互斥（同日不并出）', not (he_days & li_days),
          f'交集 {len(he_days & li_days)} 天')

    # ============ C：谓词归属 ============
    print('[C] 谓词归属与口径')
    src_open = _code_only(inspect.getsource(开业神煞))
    for call in ('self._is_tianyuan(sizhu)', 'self._is_sixiang(sizhu)',
                 'self._is_shide(sizhu)', 'self._is_wuhe(sizhu)',
                 'self._is_wuli(sizhu)'):
        check(f'C 开业发射点存在 {call}', call in src_open)
    check('C 开业本地实现 _is_wuhe（日支寅卯，与通用神煞同口径）',
          'def _is_wuhe(self, sizhu)' in src_open)
    check('C 基类尚无 _is_wuhe（若已提升为基类，请删本地实现并更新本断言）',
          not hasattr(BASE.ShenShaChecker, '_is_wuhe'))
    src_cm = _code_only(inspect.getsource(通用神煞))
    check('C 通用神煞 _is_wuhe 同以寅卯为日支判据',
          "'寅', '卯'" in inspect.getsource(通用神煞.CommonShenShaChecker._is_wuhe))
    # 逐支语义：寅卯→五合、申酉→五离、其余→两者皆无
    inst = 开业神煞.OpeningShenShaChecker()
    for zhi, want in (('寅', 'he'), ('卯', 'he'), ('申', 'li'), ('酉', 'li'),
                      ('子', 'none'), ('午', 'none')):
        sz = {'day_zhi': zhi, 'day_gan': '甲', 'month_zhi': '寅', 'year_zhi': '子'}
        got = 'he' if inst._is_wuhe(sz) else ('li' if inst._is_wuli(sz) else 'none')
        check(f'C 日支{zhi} → {want}（实得 {got}）', got == want)
    check('C 基类 _is_wuli 判据为日支申酉（五合之对冲）',
          "('申', '酉')" in inspect.getsource(BASE.ShenShaChecker._is_wuli)
          or "'申'" in inspect.getsource(BASE.ShenShaChecker._is_wuli))

    # ============ D：总分 ============
    print('[D] 通道总分（2026 全年，owners=[]）')
    check(f'D 开业总分=16087（§250 天乙 +2340；§209 前 12897，+850，实得 {tot_open}）',
          tot_open == 16087)
    bed = get_checker('安床')
    tot_bed = 0
    for dte, sz in days:
        for s in bed.check(sz, []):
            tot_bed += s.get('score', 0)
    check(f'D 安床总分=15078（§250 天乙 +2340 后重冻；胎神降级不改变通道总分，实得 {tot_bed}）',
          tot_bed == 15078)

    # ============ E：死键反证 ============
    print('[E] 死键反证：15 通道小耗/大耗发射')
    n_emit = 0
    for ev in CH15:
        c = get_checker(ev)
        for dte, sz in days:
            for s in c.check(sz, []):
                if s.get('name') in ('小耗', '大耗'):
                    n_emit += 1
    check(f'E 15 通道全年 小耗/大耗 发射=0（实得 {n_emit}）', n_emit == 0)

    # ============ F：胎神 C 步 ============
    print('[F] 安床胎神 C 步：0 分展示')
    ts_cnt, bad_score, bad_text = {}, [], []
    for dte, sz in days:
        for s in bed.check(sz, []):
            nm = s.get('name', '')
            if nm.startswith('胎神'):
                ts_cnt[nm] = ts_cnt.get(nm, 0) + 1
                if s.get('score', 0) != 0:
                    bad_score.append((str(dte), nm, s.get('score')))
                if '家有孕妇' not in s.get('description', ''):
                    bad_text.append((str(dte), nm, s.get('description', '')))
    check(f'F 胎神占床=49 天（实得 {ts_cnt.get("胎神占床", 0)}）',
          ts_cnt.get('胎神占床', 0) == 49)
    check(f'F 胎神占房床=61 天（实得 {ts_cnt.get("胎神占房床", 0)}）',
          ts_cnt.get('胎神占房床', 0) == 61)
    check(f'F 胎神占床、房床=12 天（实得 {ts_cnt.get("胎神占床、房床", 0)}）',
          ts_cnt.get('胎神占床、房床', 0) == 12)
    check('F 胎神项全部 0 分（无扣分、无否决）', not bad_score, f'{bad_score[:3]}')
    check('F 胎神项文案均含「家有孕妇」前置限定', not bad_text, f'{bad_text[:3]}')
    for k in (('安床', '胎神日'), ('安床', '胎神占床'), ('安床', '胎神占房床'),
              ('安床', '冲床日'), ('*', '胎神日')):
        check(f'F 注册键 {k} 不存在（0 分展示不走分值表）', k not in SHENSHA_SCORES)
    from modules.shensha import 安床神煞
    src_bed = _code_only(inspect.getsource(安床神煞))
    check('F 安床源码剥离注释后无胎神扣分发射（-15/-12 等）',
          '胎神日' not in src_bed and '冲床日' not in src_bed)
    check('F 安床源码含 _taishen_zhanwei（日占部位取数单点）',
          'def _taishen_zhanwei(self, sizhu)' in src_bed)

    print()
    if FAILS:
        print(f'FAIL {len(FAILS)} 项：{FAILS[:10]}')
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
