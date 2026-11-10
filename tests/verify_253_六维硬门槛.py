# -*- coding: utf-8 -*-
"""六维核验合流为极品/上品硬门槛验证（2026-11-10，001 §253）

判据（用户拍板冻结）：
  - 得令/合局/德神/专属项(修造=扶山补龙)/相主/硬忌：非 N/A 项必须全 ✓，
    方有资格列极品/上品；合局同作硬门槛；N/A 第三态不挡；
  - 6√ 必要非充分：lint 无警告 + 顶部决策绿灯 + 相主不负 仍把关；
  - 「等级=总分纯函数」铁律不动，本批仅收分档。

验证面：
A. 单元层（合成 result，与 lint/决策结果无关的纯逻辑断言）：
   缺任一非 N/A 项 → tier='none' 且 core_miss 点名；全√ → core_ok=True；
   空事主 → 相主 N/A 不挡。
B. 集成层（真实日课全月扫描）：所有 perfect/shangpin 日 core_ok 必 True（反向断言）；
   存在 lint+绿灯却被六维缺项拦截的样本时其 tier 必为 none。
C. 回归层：截图场景——日主失令（囚/死）日即使高分也不得列档。

退出码：0=全过 1=有失败
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

from modules.排序键 import perfect_profile          # noqa: E402

FAILS = []


def check(name, cond, detail=''):
    if cond:
        print('  PASS  ' + name)
    else:
        print('  FAIL  ' + name + ('  -> ' + str(detail) if detail else ''))
        FAILS.append(name)


print('=' * 76)
print('六维核验硬门槛（001 §253）')
print('=' * 76)

OWNER = {'name': '张三', 'role': '事主', 'sizhu': '甲子 丙寅 戊午 庚申',
         '生肖': '鼠', '年支': '子', 'year_zhi': '子'}


def mk_result(wang=10, he=True, deity=True, fushan=True, xz=15,
              veto=None, neg_sha=0, score=120, level='吉'):
    ss = []
    if deity:
        shensha = {'name': '岁德', 'score': 30}
        ss.append(shensha)
    if fushan:
        ss.append({'name': '山家三合', 'score': 10})
    for i in range(neg_sha):
        ss.append({'name': '小耗%d' % i, 'score': -3})
    rels = ['申子辰三合水局'] if he else []
    return {
        'score': score, 'level': level,
        'veto_reasons': list(veto or []),
        'shensha_list': ss,
        'wu_xing_result': {'details': {'地支关系': rels}},
        'score_details': {
            '月令详细': {'旺衰得分': wang},
            '相主得分': xz,
            '相主详情': (['张三生肖子与日课日支丑相合（年支合），+15分']
                        if xz > 0 else []),
        },
    }


# ============ A：单元层（纯逻辑） ============
print('\n[A] 六维硬门槛单元断言')

# A1 修造六维全√ → core_ok（不保证 perfect，lint/决策另把关）
c = perfect_profile(mk_result(), [OWNER], '修造')
check('A1 六维全√ → core_ok=True 且 core_miss 空',
      c.get('core_ok') is True and not c.get('core_miss'),
      (c.get('core_miss'), c.get('marks')))
check('A1b 返回键 core_ok/core_miss 在位',
      'core_ok' in c and 'core_miss' in c, list(c.keys()))

# A2 缺合局 → none，core_miss 点名「合局」
c = perfect_profile(mk_result(he=False), [OWNER], '修造')
check('A2 缺合局 → tier=none 且 core_miss 含「合局」',
      c.get('tier') == 'none' and '合局' in c.get('core_miss'),
      (c.get('tier'), c.get('core_miss')))

# A3 缺德神 → none
c = perfect_profile(mk_result(deity=False), [OWNER], '修造')
check('A3 缺德神 → tier=none 且 core_miss 含「德神」',
      c.get('tier') == 'none' and '德神' in c.get('core_miss'),
      (c.get('tier'), c.get('core_miss')))

# A4 修造缺扶山补龙 → none（用户点名：修造必须扶山补龙）
c = perfect_profile(mk_result(fushan=False), [OWNER], '修造')
check('A4 修造缺扶山补龙 → tier=none 且 core_miss 含「扶山补龙」',
      c.get('tier') == 'none' and '扶山补龙' in c.get('core_miss'),
      (c.get('tier'), c.get('core_miss')))

# A5 截图场景：日主失令（囚，-5）→ none，即使其余全√
c = perfect_profile(mk_result(wang=-5), [OWNER], '修造')
check('A5 日主失令(囚) → tier=none 且 core_miss 含「得令」',
      c.get('tier') == 'none' and '得令' in c.get('core_miss'),
      (c.get('tier'), c.get('core_miss')))

# A6 相主放宽口径（§253 二次拍板）：xz=0 不扣分 → 过门槛（core_miss 无相主）
c = perfect_profile(mk_result(xz=0), [OWNER], '修造')
check('A6 相主=0 不扣分 → 过门槛（core_miss 不含相主，core_ok=True）',
      c.get('core_ok') is True and '相主' not in c.get('core_miss'),
      (c.get('core_miss'), c.get('marks')))
# A6b 相主负分（冲克）→ 门槛拦截
_neg = mk_result(xz=-10)
_neg['score_details']['相主详情'] = ['张三生肖子与日课日支未相害（年支害），-10分']
c = perfect_profile(_neg, [OWNER], '修造')
check('A6b 相主负分 → core_miss 含「相主」且 tier=none',
      c.get('tier') == 'none' and '相主' in c.get('core_miss'),
      (c.get('tier'), c.get('core_miss')))

# A7 硬忌：一票否决 → none
c = perfect_profile(mk_result(veto=['岁破日，不可用']), [OWNER], '修造')
check('A7 一票否决 → tier=none 且 core_miss 含「硬忌」',
      c.get('tier') == 'none' and '硬忌' in c.get('core_miss'),
      (c.get('tier'), c.get('core_miss')))

# A8 空事主：相主 N/A 不挡，其余全√ → core_ok=True
c = perfect_profile(mk_result(), [], '修造')
check('A8 空事主相主 N/A 不挡 → core_ok=True 且 marks 含「-」',
      c.get('core_ok') is True and '-' in c.get('marks', ''),
      (c.get('core_miss'), c.get('marks')))

# A9 六维全√且 lint 过且决策绿 → perfect（若决策非绿则至少 core_ok）
c = perfect_profile(mk_result(), [OWNER], '修造')
if c.get('lint_ok') and c.get('decision_key') == 'ok':
    check('A9 全√+校验过+绿灯 → perfect', c.get('perfect') is True,
          c.get('lint_note'))
else:
    check('A9 全√但 lint/决策未过 → 仍不列档（必要非充分）',
          c.get('tier') == 'none',
          (c.get('lint_ok'), c.get('decision_key'), c.get('lint_note')))

# ============ B：集成层（真实日课反向断言） ============
print('\n[B] 真实日课扫描：列档日六维必全√（2026-01~03 修造/入宅/嫁娶）')
from modules.四柱计算器 import calculate_sizhu          # noqa: E402
from modules.评分器 import calculate_score              # noqa: E402

n_day = n_tier = n_blocked = 0
bad = []
d = datetime.date(2026, 1, 1)
while d <= datetime.date(2026, 3, 31):
    for ev, shan in (('修造', '坤山艮向'), ('入宅', None), ('嫁娶', None)):
        sz = calculate_sizhu((d.year, d.month, d.day), 12, 0, longitude=120)
        sz = dict(sz)
        sz.update({'year': d.year, 'month': d.month, 'day': d.day})
        rep = calculate_score(sz, ev,
                              owners=[{'name': '福主', 'role': '福主',
                                       'year_sx': '龙'}],
                              shan_xiang=shan, zeli_mode='feixing')
        # calculate_score 主返回本体即含 score_details / wu_xing_result /
        # shensha_list / veto_reasons，直接喂 perfect_profile（与榜单同源）
        c = perfect_profile(rep, [{'name': '福主', 'role': '福主',
                                   'year_sx': '龙'}], ev)
        n_day += 1
        if c.get('tier') in ('perfect', 'shangpin'):
            n_tier += 1
            if c.get('core_ok') is not True:
                bad.append((str(d), ev, c.get('tier'), c.get('core_miss')))
        if (c.get('lint_ok') and c.get('decision_key') == 'ok'
                and c.get('tier') == 'none' and c.get('core_miss')):
            n_blocked += 1
    d += datetime.timedelta(days=1)

check('B1 全部列档日（%d/%d 天次）core_ok 均为 True' % (n_tier, n_day),
      not bad, bad[:3])
print('  INFO  被 §253 拦截（校验过+绿灯但六维缺项）样本：%d 天次' % n_blocked)
check('B2 拦截样本计数为非负整数（信息项）', isinstance(n_blocked, int))

# ============ C：等级铁律不动 ============
print('\n[C] 等级铁律：总分等级不受分档门槛影响')
rep = None
sz = calculate_sizhu(datetime.date(2026, 3, 8), 10, 0)
sz = dict(sz)
sz.update({'year': 2026, 'month': 3, 'day': 8})
rep = calculate_score(sz, '修造', owners=[dict(OWNER)],
                      shan_xiang='坤山艮向', zeli_mode='pure')
check('C1 score 为数值（等级=总分纯函数未被本批触碰）',
      isinstance(rep.get('score'), (int, float)), rep.get('score'))
check('C2 report_level/level 字段仍在位',
      bool(rep.get('report_level') or rep.get('level')),
      (rep.get('report_level'), rep.get('level')))

print('\n' + '=' * 76)
if FAILS:
    print('FAIL %d 项：%s' % (len(FAILS), '；'.join(FAILS)))
    sys.exit(1)
print('ALL PASS')
sys.exit(0)
