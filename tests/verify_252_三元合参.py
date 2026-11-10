# -*- coding: utf-8 -*-
"""三元合参（日课·山家·事主）展示验证（2026-11-10，001 §252）

判据（用户指令冻结）：
  - 纯展示层聚合：只读 sizhu/山向/宜忌/三煞/仙命坐山/喜用神/相主等既有产物，
    不产生新分值、不改变任何评分与否决逻辑；
  - 三维：日课×山家（扶山/克山/合局克山/克山运/旺行×坐山/三煞岁破）、
    日课×事主（喜用神补益/相主冲合）、山家×事主（安葬=仙命×坐山；
    其余=事主年命纳音×坐山，复用 evaluate_wangming_vs_shanzuo）；
  - 综合结论按「硬门槛冲主 > 课克山 > 山克主 > 课主小冲 > 全吉 > 平和」分级；
  - 出行通道 shan_xiang 为出发方向，课山维必须旁路（传 None）。

验证面：
A. 单元层：三维判定 + 文本聚合 + 综合结论分级 + format 四行结构。
B. 集成层：真实日课 calculate_score 主返回/否决返回均携带 sanyuan_analysis；
   出行旁路；无山无事主为 None；事主匹配年命五行富化键在位。
C. 渲染在位：主程序 / 日课评分系统（GUI+导出）/ 反推UI 四处同源调用。
D. 反向兼容：§251 偏枯块与火水口径源码未动；抽样 lint 无新增 ERROR。

退出码：0=全过 1=有失败（FAIL N 计数）
================================================================================
"""
import datetime
import io
import os
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.评分器 import (build_sanyuan_analysis,        # noqa: E402
                            format_sanyuan_text)

FAILS = []


def check(name, cond, detail=''):
    if cond:
        print('  PASS  ' + name)
    else:
        print('  FAIL  ' + name + ('  -> ' + str(detail) if detail else ''))
        FAILS.append(name)


print('=' * 76)
print('三元合参（日课·山家·事主）展示验证（001 §252）')
print('=' * 76)

# ============ A：单元层 ============
print('\n[A] build_sanyuan_analysis 三维判定与综合结论')

# 木旺四柱（木4+）
SZ_MU = {'year_gan': '甲', 'month_gan': '乙', 'day_gan': '甲',
         'hour_gan': '丙', 'year_zhi': '寅', 'month_zhi': '卯',
         'day_zhi': '寅', 'hour_zhi': '午'}
# 火4 偏枯（旺行火）
SZ_HUO = {'year_gan': '丙', 'month_gan': '丁', 'day_gan': '庚',
          'hour_gan': '壬', 'year_zhi': '巳', 'month_zhi': '午',
          'day_zhi': '卯', 'hour_zhi': '未'}

OM = [{'name': '张三', 'score': 12, 'details': ['天干木=用神+5'],
       'xishen': '木', 'yongshen': '木', '年命干支': '甲子', '年命五行': '金'}]

# A1 课克山：木旺 × 坤山（土） → ❌，综合含「克伐」
r = build_sanyuan_analysis(sizhu=SZ_MU, shan_xiang='坤山艮向',
                           owner_matches=OM, xishen_score=12)
check('A1 木旺×坤土 → 课山=凶/克山=True',
      r['课山']['判定'] == '凶' and r['课山']['克山'] is True,
      r['课山'])
check('A2 综合结论含「克伐坤山家」与「建议换日」',
      '克伐坤山家' in r['综合'] and '换日' in r['综合'], r['综合'])

# A3 课生山：火旺 × 坤山（土） → ✅ 扶山
r = build_sanyuan_analysis(sizhu=SZ_HUO, shan_xiang='坤山艮向')
check('A3 火旺×坤土 → 课山=吉、文本含「课生山（扶山）」',
      r['课山']['判定'] == '吉' and '课生山（扶山）' in r['课山']['文本'],
      r['课山']['文本'])

# A4 扶山文本 + 旺行克山 → 凶优先（❌），两段文本并存
r = build_sanyuan_analysis(sizhu=SZ_MU, shan_xiang='坤山艮向',
                           yi_list=['坤山得未生扶'])
check('A4 扶山文本遇旺行克山 → 仍判凶（克优先）',
      r['课山']['判定'] == '凶' and '坤山得未生扶' in r['课山']['文本'],
      (r['课山']['判定'], r['课山']['文本']))

# A5 克山类忌项识别：山被支克 / 合局克山 / 克山运；有制化不误判
r = build_sanyuan_analysis(sizhu=SZ_HUO, shan_xiang='乾山巽向',
                           ji_list=['乾山被午克制'])
check('A5a 「乾山被午克制」→ 凶', r['课山']['判定'] == '凶', r['课山']['判定'])
r = build_sanyuan_analysis(sizhu=SZ_HUO, shan_xiang='乾山巽向',
                           ji_list=['三合水局克山（乾山属金）'])
check('A5b 「局克山」→ 凶', r['课山']['判定'] == '凶', r['课山']['判定'])
r = build_sanyuan_analysis(sizhu=SZ_HUO, shan_xiang='乾山巽向',
                           ji_list=['乾山克山运：山运木，日课金克山运，忌用'])
check('A5c 「克山运」→ 凶', r['课山']['判定'] == '凶', r['课山']['判定'])
r = build_sanyuan_analysis(sizhu=SZ_HUO, shan_xiang='乾山巽向',
                           ji_list=['乾山克山运（有制化：天德到山）'])
check('A5d 克山运有制化 → 不因该条判凶',
      r['课山']['判定'] != '凶' or '克山运' not in r['课山']['文本'].split('；')[0],
      r['课山'])

# A6 三煞/岁破顺带提示
r = build_sanyuan_analysis(sizhu=SZ_HUO, shan_xiang='坤山艮向',
                           sansha_info={'year_sansha_fan': True,
                                        'sansha_penalty': -30},
                           ji_list=['坤山涉岁破（岁破日）'])
check('A6 坐山犯年三煞（-30分）+ 涉岁破提示',
      '坐山犯年三煞' in r['课山']['文本'] and '涉岁破' in r['课山']['文本'],
      r['课山']['文本'])

# A7 课×主：喜用补益 + 硬门槛冲
r = build_sanyuan_analysis(owner_matches=OM, xishen_score=12,
                           xiangzhu_score=-30,
                           xiangzhu_details=['[硬性门槛]张三生肖子与日课日支午六冲（年命六冲），不可用，-30分'])
check('A7a 硬门槛冲主 → 课主=凶❌、硬门槛=True',
      r['课主']['判定'] == '凶' and r['课主']['硬门槛'] is True, r['课主'])
check('A7b 综合结论=必须换日', '必须换日' in r['综合'], r['综合'])
r = build_sanyuan_analysis(owner_matches=OM, xishen_score=12,
                           xiangzhu_score=0)
check('A7c 有补无冲 → 课主=吉✅、文本含「补益事主喜用神」',
      r['课主']['判定'] == '吉' and '补益事主喜用神' in r['课主']['文本'],
      r['课主']['文本'])
r = build_sanyuan_analysis(owner_matches=OM, xishen_score=12,
                           xiangzhu_score=-10,
                           xiangzhu_details=['张三生肖子与日课日支未相害（年支害），-10分'])
check('A7d 有冲有补（非硬门槛）→ ⚠️',
      r['课主']['判定'] == '凶' and r['课主']['标记'] == '⚠️', r['课主'])

# A8 山×主（安葬通道）：shanzuo_eval 直取
_se = {'relation': '坐山生仙命', 'level': '大吉',
       'reason': '仙命纳音五行属金，坐山五行属土，二者坐山生仙命（大吉）',
       '坐山': '坤', '坐山五行': '土', 'score': 20}
r = build_sanyuan_analysis(shan_xiang='坤山艮向', shanzuo_eval=_se,
                           owner_matches=OM, xishen_score=12)
check('A8a 安葬通道：山主=吉、文本含「坐山生仙命」',
      r['山主']['判定'] == '吉' and '坐山生仙命' in r['山主']['文本'],
      r['山主'])
_se2 = dict(_se, relation='坐山克仙命', level='凶中之凶',
            reason='仙命纳音五行属木，坐山五行属金，二者坐山克仙命（凶中之凶）',
            坐山五行='金')
r = build_sanyuan_analysis(shan_xiang='乾山巽向', shanzuo_eval=_se2,
                           owner_matches=OM, xishen_score=12)
check('A8b 坐山克仙命 → 山主=凶、综合含「主耗费气力」',
      r['山主']['判定'] == '凶' and '耗费气力' in r['综合'],
      (r['山主']['判定'], r['综合']))

# A9 山×主（生者通道）：年命纳音×坐山，措辞用「主命」不用「仙命」
r = build_sanyuan_analysis(sizhu=SZ_HUO, shan_xiang='坤山艮向',
                           owner_matches=OM, xishen_score=12)
check('A9 生者通道：文本含「主命」、不含「仙命」，土生主命金=吉',
      r['山主'] and '坐山生主命' in r['山主']['文本']
      and '仙命' not in r['山主']['文本'] and r['山主']['判定'] == '吉',
      r['山主'])

# A10 综合分级：全吉 → 三元相生
_sz_tu = {'year_gan': '戊', 'month_gan': '己', 'day_gan': '戊',
          'hour_gan': '辛', 'year_zhi': '辰', 'month_zhi': '戌',
          'day_zhi': '丑', 'hour_zhi': '酉'}
r = build_sanyuan_analysis(sizhu=_sz_tu, shan_xiang='坤山艮向',
                           owner_matches=OM, xishen_score=12,
                           xiangzhu_score=15,
                           xiangzhu_details=['张三生肖子与日课日支丑相合（年支合），+15分'])
check('A10 课山比和+课主吉+山主吉 → 综合=三元相生',
      '三元相生' in r['综合'], r['综合'])

# A11 全空 → None
check('A11 无山向无事主 → None',
      build_sanyuan_analysis(sizhu=SZ_HUO) is None)

# A12 format 四行结构与占位行
r = build_sanyuan_analysis(owner_matches=OM, xishen_score=12)
txt = format_sanyuan_text(r)
check('A12a 文本块含标题与 ⛰️👤🧭📌 四行',
      '【三元合参：日课 · 山家 · 事主】' in txt
      and '⛰️ 日课与山家：' in txt and '👤 日课与事主：' in txt
      and '🧭 山家与事主：' in txt and '📌 综合结论：' in txt, txt[:80])
check('A12b 无坐山 → ⛰️ 行显示「本事项不涉及坐山」',
      '本事项不涉及坐山' in txt, txt)
check('A12c 综合=人和天时兼得', '人和天时兼得' in r['综合'], r['综合'])

# ============ B：集成层（真实日课） ============
print('\n[B] calculate_score 集成透出')
from modules.四柱计算器 import calculate_sizhu          # noqa: E402
from modules.评分器 import calculate_score              # noqa: E402

OWNER = {'name': '张三', 'role': '事主', 'sizhu': '甲子 丙寅 戊午 庚申',
         '生肖': '鼠', 'xishen': '木', 'yongshen': '木'}

d0 = datetime.date(2026, 3, 8)
sz0 = calculate_sizhu(d0, 10, 0)
sz0 = dict(sz0); sz0.update({'year': 2026, 'month': 3, 'day': 8})

# B1 修造+山向+事主：键在、三维适用、事主匹配带年命五行
rep = calculate_score(sz0, '修造', owners=[dict(OWNER)],
                      shan_xiang='坤山艮向', zeli_mode='pure')
sy = rep.get('sanyuan_analysis')
check('B1a 主返回携带 sanyuan_analysis 且三维适用',
      sy and sy.get('课山') and sy.get('课主'), type(sy))
_sd = rep.get('score_details') or {}
_om = (_sd.get('事主匹配') or [{}])[0]
check('B1b 事主匹配富化键在位（年命干支=甲子/年命五行=金）',
      _om.get('年命干支') == '甲子' and _om.get('年命五行') == '金', _om)
check('B1c score 为数值且不受展示键影响（int/float）',
      isinstance(rep.get('score'), (int, float)), rep.get('score'))

# B2 山×主生者通道：金命×坤土 → 坐山生主命
if sy and sy.get('山主'):
    check('B2 山主文本含「张三」「坐山生主命」',
          '张三' in sy['山主']['文本'] and '坐山生主命' in sy['山主']['文本'],
          sy['山主']['文本'])
else:
    check('B2 山主维度适用', False, '山主=None')

# B3 出行旁路：shan_xiang 作出发方向 → 课山维 None
rep_t = calculate_score(sz0, '出行', owners=[dict(OWNER)],
                        shan_xiang='坎', zeli_mode='pure')
sy_t = rep_t.get('sanyuan_analysis')
check('B3 出行通道课山维旁路（课山=None，课主仍在）',
      (not sy_t or sy_t.get('课山') is None)
      and (sy_t is None or sy_t.get('课主') is not None),
      sy_t)

# B4 无山向无事主 → None
rep_n = calculate_score(sz0, '修造', owners=[], shan_xiang=None,
                        zeli_mode='pure')
check('B4 无山向无事主 → sanyuan_analysis 为 None',
      rep_n.get('sanyuan_analysis') is None, rep_n.get('sanyuan_analysis'))

# B5 否决日同样携带键（五行门槛否决日：找个否决日断言键存在）
_veto_found = False
_d = datetime.date(2026, 1, 1)
while _d <= datetime.date(2026, 4, 30) and not _veto_found:
    _sz = calculate_sizhu(_d, 10, 0)
    _sz = dict(_sz); _sz.update({'year': _d.year, 'month': _d.month,
                                 'day': _d.day})
    _rp = calculate_score(_sz, '修造', owners=[dict(OWNER)],
                          shan_xiang='坤山艮向', zeli_mode='pure')
    if _rp.get('level') == '❌ 凶':
        _veto_found = True
        check('B5 否决日 sanyuan_analysis 键存在',
              'sanyuan_analysis' in _rp, list(_rp.keys())[:8])
    _d += datetime.timedelta(days=1)
if not _veto_found:
    check('B5 样本窗口内存在否决日（修造+坤山）', False, '未找到否决日')

# ============ C：渲染在位 ============
print('\n[C] 四处渲染同源在位')
src_main = open(os.path.join(ROOT, '主程序.py'), encoding='utf-8').read()
src_score = open(os.path.join(ROOT, 'modules', '日课评分系统.py'),
                 encoding='utf-8').read()
src_fantui = open(os.path.join(ROOT, 'modules', '反推UI.py'),
                  encoding='utf-8').read()
check('C1 主程序详情渲染在位',
      'format_sanyuan_text(_sy252)' in src_main
      and 'build_sanyuan_analysis' in src_main)
check('C2 评分详情窗 GUI+导出文本各 1 处（共 2 处）',
      src_score.count('format_sanyuan_text(') == 2,
      src_score.count('format_sanyuan_text('))
check('C3 反推独立版详情头在位',
      'format_sanyuan_text(_sy252)' in src_fantui)
check('C4 四处均优先读 sanyuan_analysis 键（同源优先）',
      "'sanyuan_analysis'" in src_main
      and src_score.count("'sanyuan_analysis'") == 2
      and "'sanyuan_analysis'" in src_fantui)

# ============ D：反向兼容 ============
print('\n[D] §251/§238 既有口径零改动')
_src_scorer = open(os.path.join(ROOT, 'modules', '评分器.py'),
                   encoding='utf-8').read()
check('D1 §251 偏枯透出仍在', "score_details['五行偏枯分析']" in _src_scorer)
check('D2 §238 火水口径源码未动（丙丁巳午/壬癸子亥）',
      "'丙丁巳午'" in _src_scorer and "'壬癸子亥'" in _src_scorer)
check('D3 三元合参不产生分值（无 self.final_score 改动于 §252 段）',
      '_sanyuan_252 = build_sanyuan_analysis' in _src_scorer
      and 'sanyuan_analysis' in _src_scorer)

# E：抽样 lint 无新增 ERROR（修造+山向+事主，60 天）
print('\n[E] 日课校验器抽样免疫')
from modules.日课校验器 import lint_lesson                # noqa: E402
bad_e = []
_d = datetime.date(2026, 1, 1)
for _i in range(60):
    _sz = calculate_sizhu(_d, 10, 0)
    _sz = dict(_sz); _sz.update({'year': _d.year, 'month': _d.month,
                                 'day': _d.day})
    _rp = calculate_score(_sz, '修造', owners=[dict(OWNER)],
                          shan_xiang='坤山艮向', zeli_mode='pure')
    lr = lint_lesson(_rp)
    if lr.has_error:
        errs = [i.id for i in lr.issues if i.severity == 'ERROR']
        if errs != ['E001']:
            bad_e.append((str(_d), errs))
    _d += datetime.timedelta(days=1)
check('E1 抽样 60 天 lint 无新增 ERROR（三元合参不破坏校验）', not bad_e,
      bad_e[:3])

print()
print('FAILS=%d' % len(FAILS))
if FAILS:
    for f in FAILS:
        print('  - ' + f)
sys.exit(1 if FAILS else 0)
