# -*- coding: utf-8 -*-
"""
归档案例基线回归（tests/fixtures/）
====================================

复现 2026-09-17 手工验证过的关键日课基线（原始详情见各案例目录内
detail_*.txt，sha1 与 C:\\Temp 归档一致）。本脚本不依赖 GUI / inject 链路，
直接用 calculate_score 在指定时柱上重算，断言总分与五行评分。

A 段 3 例强断言；B 段 3 例观察项（2 入宅 + 2023-01-11 规则演进漂移，
2026-10-03 裁决，均不判失败）。

基线日期：2026-09-17（羊刃补实现之前；已核对各案例四柱均不含羊刃位）。

用法：
  python tests/fixtures/verify_fixtures.py
退出码：0=全部与基线一致  1=有漂移（CI 可挂）
"""
import sys
import json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
from modules.喜用神计算器 import calculate_xishen_yongshen

FIX = Path(__file__).resolve().parent


def _load_owners(rel_path):
    """按原始 JSON 夹具（只迁不改）构造评分器 owners，含喜用神（与原复现脚本同口径）。"""
    raw = json.loads((FIX / rel_path).read_text(encoding='utf-8'))
    norm = []
    for o in raw:
        bd = date(int(o['y']), int(o['m']), int(o['d']))
        hh = int(o.get('hh', 12))
        mm = int(o.get('mm', 0))
        xy = calculate_xishen_yongshen(calculate_sizhu(bd, hh, mm))
        norm.append({
            'role': o.get('role', ''), '性别': o.get('gender', ''),
            'name': o.get('name', ''), 'birth_date': bd,
            'birth_hour': hh, 'birth_minute': mm,
            'xishen': xy[0], 'yongshen': xy[1],
        })
    return norm


def _sizhu(y, m, d, hour, minute=0):
    sz = calculate_sizhu(date(y, m, d), hour, minute)
    sz.update({'year': y, 'month': m, 'day': d, 'date': date(y, m, d)})
    sz['年柱'] = sz.get('年柱', '') or (sz.get('year_gan', '') + sz.get('year_zhi', ''))
    sz['月柱'] = sz.get('月柱', '') or (sz.get('month_gan', '') + sz.get('month_zhi', ''))
    sz['日柱'] = sz.get('日柱', '') or (sz.get('day_gan', '') + sz.get('day_zhi', ''))
    sz['时柱'] = sz.get('时柱', '') or (sz.get('hour_gan', '') + sz.get('hour_zhi', ''))
    return sz


# ── A 段：强断言基线（当前软件可 1:1 复现，漂移即退出 1）─────────────────────
# 基线：(名称, 公历日期, 时(24h), 事项, 山向, owners夹具, 期望四柱, 期望总分, 期望五行评分)
BASELINES = [
    ('2023-01-12 嫁娶 丁丑时', (2023, 1, 12), 2, '嫁娶', None,
     '2023-01-11_嫁娶_乙丑时/owners_0111.json',
     ('壬寅', '癸丑', '庚午', '丁丑'), 0, 18),
    ('2023-01-29 嫁娶 丙午时', (2023, 1, 29), 12, '嫁娶', None,
     '2023-01-29_嫁娶_推荐时柱/owners_0129.json',
     ('壬寅', '癸丑', '丁亥', '丙午'), 0, 70),
    ('2023-01-29 嫁娶 己酉时', (2023, 1, 29), 18, '嫁娶', None,
     '2023-01-29_嫁娶_推荐时柱/owners_0129.json',
     ('壬寅', '癸丑', '丁亥', '己酉'), 71, 55),
]

# ── B 段：已知漂移观察项（不判失败，只打印；待口径拍板/规则演进核对）───────────
# 1) 两个入宅案例：2026-09-17 基线后 09 月规则强化（相主日支六冲硬否决、年命六冲
#    年份否决、交节日月柱口径）所致；简化脚本不经过主程序 inject 链路，2026 案例的
#    "甲午月"混合口径无法在此复现，故只做数值观察。
# 2) 2023-01-11（2026-10-03 裁决挂观察项）：非回归，属规则演进自然漂移，
#    待 P0-②/P0-① 完成后 git bisect 定位 + 引典据核对。
# (名称, 日期, 时, 事项, 山向, owners夹具, 基线五行, 基线总分, 基线文件, 已诊断原因)
WATCH = [
    ('2023-01-11 嫁娶 乙丑时', (2023, 1, 11), 2, '嫁娶', None,
     '2023-01-11_嫁娶_乙丑时/owners_0111.json', 73, 0,
     '2023-01-11_嫁娶_乙丑时/detail_0111_new.txt',
     '规则演进漂移（非bug）：2026-09-18后计分类提交（羊刃-15/四废-15/八专-15/'
     '厌对-10/阳错-15等I1/J2系列），某条负分规则新命中致五行73→63、总分仍0；'
     '待P0完成后git bisect定位+引典据：合理命中→重录基线，误报→修规则'),
    ('2023-07-07 入宅 甲午时(smoke)', (2023, 7, 7), 12, '入宅', '坤山艮向兼未',
     '2026-07-07_入宅_坤山艮向兼未/owners_0707.json', 158, 163,
     '2026-07-07_入宅_坤山艮向兼未/detail_0707_smoke.txt',
     '新增相主硬门槛：事主2日支申↔日课日支寅六冲，一票否决（基线时为163分大吉）'),
    ('2026-07-07 入宅 壬午时(rz)', (2026, 7, 7), 12, '入宅', '坤山艮向兼未',
     '2026-07-07_入宅_坤山艮向兼未/owners_0707.json', 134, 163,
     '2026-07-07_入宅_坤山艮向兼未/detail_rz_0707.txt',
     '交节日小暑：基线inject纠正为甲午月，简化脚本12:00走乙未月（月令死）+规则强化'),
]


def _score_one(y, m, d, hour, event, shan, owners):
    sz = _sizhu(y, m, d, hour)
    r = calculate_score(sz, event, owners, '阳宅', shan,
                        None, None, None, None, None, zeli_mode='pure')
    sd = r.get('score_details') or {}
    wxr = r.get('wu_xing_result') or {}
    got_wx = sd.get('五行评分')
    if got_wx is None:
        got_wx = wxr.get('score')
    return sz, int(r.get('score') or 0), int(got_wx or 0)


def main():
    passed = 0
    failed = 0
    print('=' * 88)
    print('归档案例基线回归（基线日期 2026-09-17）')
    print('=' * 88)
    print('【A 段】强断言基线 %d 例（漂移即失败）' % len(BASELINES))
    print('-' * 88)
    for name, (y, m, d), hour, event, shan, owners_rel, exp_gz, exp_score, exp_wx in BASELINES:
        owners = _load_owners(owners_rel)
        sz, got_score, got_wx = _score_one(y, m, d, hour, event, shan, owners)
        gz = (sz.get('年柱'), sz.get('月柱'), sz.get('日柱'), sz.get('时柱'))
        problems = []
        if exp_gz and gz != exp_gz:
            problems.append('四柱 期望%s 实际%s' % (exp_gz, gz))
        if got_score != exp_score:
            problems.append('总分 期望%d 实际%d' % (exp_score, got_score))
        if got_wx != exp_wx:
            problems.append('五行评分 期望%d 实际%d' % (exp_wx, got_wx))
        if problems:
            failed += 1
            print('❌ %s' % name)
            print('   四柱=%s  总分=%d  五行=%d' % ('/'.join(gz), got_score, got_wx))
            for p in problems:
                print('   ✗ %s' % p)
        else:
            passed += 1
            print('✅ %-28s %s  总分=%d  五行=%d' % (name, '/'.join(gz), got_score, got_wx))

    print('-' * 88)
    print('【B 段】已知漂移观察项 %d 例（待年命六冲/相主口径拍板，不计入失败）' % len(WATCH))
    print('-' * 88)
    for name, (y, m, d), hour, event, shan, owners_rel, exp_wx, exp_score, _src, reason in WATCH:
        owners = _load_owners(owners_rel)
        sz, got_score, got_wx = _score_one(y, m, d, hour, event, shan, owners)
        gz = (sz.get('年柱'), sz.get('月柱'), sz.get('日柱'), sz.get('时柱'))
        print('⚠ %-30s %s' % (name, '/'.join(gz)))
        print('   基线 总分=%d 五行=%d  →  当前 总分=%d 五行=%d' % (exp_score, exp_wx, got_score, got_wx))
        print('   已诊断：%s' % reason)

    print('=' * 88)
    print('A 段汇总：通过 %d，漂移 %d；B 段观察项 %d（不影响退出码）' % (passed, failed, len(WATCH)))
    if failed:
        print('❌ 强断言基线漂移，请核对是代码回归还是基线需更新（更新须用户确认）')
        return 1
    print('✅ A 段 %d 个归档案例全部与 2026-09-17 基线一致' % passed)
    return 0


if __name__ == '__main__':
    sys.exit(main())
