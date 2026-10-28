# -*- coding: utf-8 -*-
"""
十恶大败全删批·删除回归（2026-10-19，三步走第三步）
======================================================
拍板依据（2026-10-19 第四轮拍板）：
- 一档：注释留痕＋谓词保留作「无禄日」载体（1b6c0e2，10 处发射行注释＋5 谓词标注）；
- 二档：全删（9035747）——13 键日课扣分删（无独立无禄展示键可留）、规则引擎
  一票否决必删（无典据不得一票否决）、文案删无典据、校准表同步删、部署副本
  主仓 commit 后按纪律统一重建（本批不动）；
- 执行条件：15 通道逐一断言清零（含通用神煞.py 第 5 个 override 链路，不得遗漏）；
  快照含删除前后 15 通道对比（2ca7b4e §二），合计 -27000/年归零；
  「无禄日」展示与扣分分离——谓词保留作历法概念载体，不参与评分。
典据链：取证 aa47dcd（三库无普适日课忌明文；协纪「然惟随各年及本命避之」属
本命避忌）＋快照 2ca7b4e（引用面全清单）。

验证面：
A. 15 通道逐一断言清零：2026 全年（hour=10）十恶大败发射各通道 == 0，
   合计 == 0（-27000/年归零）。
B. 反向断言非目标煞不变：受死日 11 个保留通道=31（2026-10-20 受死日收敛批：
   基类表B 改挂表A，入宅/嫁娶/移徙 由 59 降至 31——001 §144）；
   开业/作灶/通用/安葬 四通道=0（受死日删除批——001 §145）。
   【2026-10-20 岁破批·B 段语义反转】原断言为「岁破 8 通道=31、其余 7 通道=0」
   （基线＝本批删除前实测，快照 B1/B3 一致）——语义是「岁破反向不波及」。岁破批
   删除日课普适岁破注册（001 §140）后，反转语义为「15 通道岁破 shensha **全 0**」，
   逐通道断言（非仅改汇总数）：8 个原非零通道 31→0，原已 0 的 7 通道仍 0。
C. 13 键不存在：('X','十恶大败') ∉ SHENSHA_SCORES；shensha_score 查无
   （无通配键可落，原 -30 不复活）。
D. 谓词 5 个保留作无禄日载体：基类（嫁娶 MRO）/修造/安葬/入宅/通用
   _is_shie_dabai 在位，甲辰→True、甲子→False（起例合典据，仅离评分）。
E. 源码层：10 处发射行注释留痕在位（9 文件计数）；高级安葬规则
   SHIE_DABAI/_is_shie_dabai/append 三无＋墓碑注释在位；评分器/校准表/
   入宅规则/动土规则 无十恶大败残留；事项标准无键残留。
F. 通道总分基线：入宅 +4464（2948＋岁破批 930＋病符批 360＋红嘴朱雀批 -390
   ＋受死日收敛批 616）、嫁娶 -612（红嘴朱雀批新增坤宮 -1080＋受死日收敛 616）。

退出码 0=全过 1=有失败。
"""
import io
import os
import sys
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []

_STAT = {'checks': 0, 'pass': 0}


def check(name, cond):
    """断言计数就地自汇报（001 §135.4：计数以脚本自报为准，不依赖 Shell 回显）。"""
    _STAT['checks'] += 1
    if cond:
        _STAT['pass'] += 1
    print('[%s] %s' % ('PASS' if cond else 'FAIL', name))
    if not cond:
        FAILS.append(name)


sys.path.insert(0, ROOT)
from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.事项标准 import SHENSHA_SCORES, shensha_score

EV15 = ['入宅', '嫁娶', '动土', '修造', '拆舍', '出行', '开业', '安床', '作灶',
        '安葬', '移徙', '入学', '求医', '签约', '通用']
# 删除前基线（快照 2ca7b4e §二）
SS_BASE = {'入宅': 31, '嫁娶': 31, '移徙': 31}   # 受死日：表A（收敛后，旧 59）
# 受死日删除批（2026-10-20，001 §145）：开业/作灶/通用/安葬 四通道发射删除 → 0
SS_DEL = ('开业', '作灶', '通用', '安葬')
# 岁破批（2026-10-20，001 §140）：日课普适岁破注册删除 → 15 通道岁破 shensha 全 0
# （原 8 通道=31 基线已按拍板反转，逐通道断言见下）

y0 = datetime.date(2026, 1, 1)
y1 = datetime.date(2026, 12, 31)

# ============ A+B+F：15 通道全年逐日（同趟累计） ============
total_hits = 0
tot_ru = tot_hun = None
for ev in EV15:
    ck = get_checker(ev)
    n_sdb = n_ss = n_sp = 0
    tot = 0
    d = y0
    while d <= y1:
        sz = calculate_sizhu(d, 10, 0)
        res = ck.check(sz, [])
        names = set(s['name'] for s in res)
        if '十恶大败' in names:
            n_sdb += 1
        if '受死日' in names:
            n_ss += 1
        if '岁破' in names:
            n_sp += 1
        tot += sum(s.get('score', 0) for s in res)
        d += datetime.timedelta(days=1)
    total_hits += n_sdb
    check('A 通道清零：%s 十恶大败全年发射=0 (x%d)' % (ev, n_sdb), n_sdb == 0)
    exp_ss = 0 if ev in SS_DEL else SS_BASE.get(ev, 31)
    check('B 反向·受死日不变：%s =%d (x%d)' % (ev, exp_ss, n_ss), n_ss == exp_ss)
    exp_sp = 0
    check('B 反向·岁破全通道清零：%s =%d (x%d)' % (ev, exp_sp, n_sp), n_sp == exp_sp)
    if ev == '入宅':
        tot_ru = tot
    if ev == '嫁娶':
        tot_hun = tot
check('A 合计归零：15 通道十恶大败总发射=0（-27000/年归零）(x%d)' % total_hits,
      total_hits == 0)
check('F 总分基线：入宅全年=+11601（批次1 3377；批次2 +368 → 3745；福星批 001 §165 删伪福星 -310 → 3435；§171 蚕官/畜官去重 +310 → 3745；§172 P0 大清理 +7391 → 11136；§195 Commit1 受死日剥离扣分 31 天次×+15 → 11601）(x%d)' % tot_ru, tot_ru == 11601)
check('F 总分基线：嫁娶全年=6490（批次1 重冻 214；福星批 001 §165 删伪福星 -310 → -96；§171 蚕官/畜官去重 +310 → 214；§172 P0 大清理 +6081 → 6295；§193 主轨 C2 重丧双口径对齐 -270 → 6025；§194 受死日剥离扣分（HARD_VETO 纯展示 0 分）+465 → 6490）(x%d)' % tot_hun, tot_hun == 6490)

# ============ C：13 键不存在 ============
EV13 = ['嫁娶', '动土', '拆舍', '入宅', '开业', '出行', '安床', '作灶', '移徙',
        '入学', '求医', '签约', '安葬']
for ev in EV13:
    check("C 删除键 ('%s','十恶大败') 不存在" % ev, (ev, '十恶大败') not in SHENSHA_SCORES)
check("C shensha_score('入宅','十恶大败') 查无=None（不复活）",
      shensha_score('入宅', '十恶大败') is None)
check("C 无通配键可落：('*','十恶大败') 不存在", ('*', '十恶大败') not in SHENSHA_SCORES)

# ============ D：谓词 5 个保留作无禄日载体 ============
PRED = [('嫁娶', '基类（嫁娶 MRO）'), ('修造', '修造'), ('安葬', '安葬'),
        ('入宅', '入宅'), ('通用', '通用')]
for ev, tag in PRED:
    ck = get_checker(ev)
    fn = getattr(ck, '_is_shie_dabai', None)
    ok = (fn is not None
          and fn({'day_gan': '甲', 'day_zhi': '辰'}) is True
          and fn({'day_gan': '甲', 'day_zhi': '子'}) is False)
    check('D 谓词保留·无禄日载体：%s _is_shie_dabai 甲辰=T/甲子=F' % tag, ok)

# ============ E：源码层 ============
EMIT = [  # (相对路径, 注释留痕应有条数)
    ('神煞基类.py', 1), ('修造神煞.py', 1), ('动土神煞.py', 1), ('安床神煞.py', 1),
    ('出行神煞.py', 1), ('开业神煞.py', 1), ('安葬神煞.py', 1), ('作灶神煞.py', 1),
    ('通用神煞.py', 2),
]
MARK = "#     self._add_shensha('十恶大败', -30,"
for fn, exp in EMIT:
    p = os.path.join(ROOT, 'modules', 'shensha', fn)
    with open(p, encoding='utf-8') as f:
        src = f.read()
    check('E 注释留痕在位：%s 发射行注释 x%d' % (fn, exp), src.count(MARK) == exp)

p = os.path.join(ROOT, 'modules', 'rules', '高级安葬规则.py')
with open(p, encoding='utf-8') as f:
    src = f.read()
check('E 安葬规则三无：SHIE_DABAI/_is_shie_dabai def/append 全删',
      'SHIE_DABAI' not in src.replace('SHIE_DABAI 表与一票否决', '')
      and 'def _is_shie_dabai' not in src
      and "append('十恶大败" not in src)
check('E 安葬规则墓碑注释在位', '十恶大败日表与一票否决引用已删' in src
      and '无典据不得一票否决' in src)

for rel, bad in [('评分器.py', "('十恶大败',"),
                 ('神煞验证与校准.py', "'十恶大败': -30")]:
    p = os.path.join(ROOT, 'modules', rel)
    with open(p, encoding='utf-8') as f:
        src = f.read()
    check('E 残留清零：%s 无 %r' % (rel, bad), bad not in src)

for rel in ['入宅规则.py', '动土规则.py']:
    p = os.path.join(ROOT, 'modules', 'rules', rel)
    with open(p, encoding='utf-8') as f:
        src = f.read()
    check('E docstring 无典据文案清零：%s 无「十恶大败」' % rel, '十恶大败' not in src)

p = os.path.join(ROOT, 'modules', '事项标准.py')
with open(p, encoding='utf-8') as f:
    src = f.read()
check('E 事项标准无键残留', "'十恶大败'):" not in src)

print('---')
print('CHECKS=%d PASS=%d FAIL=%d' % (_STAT['checks'], _STAT['pass'], len(FAILS)))
if FAILS:
    print('FAILS=%d' % len(FAILS))
    for f in FAILS:
        print(' -', f)
    raise SystemExit(1)
print('ALL PASS')
raise SystemExit(0)
