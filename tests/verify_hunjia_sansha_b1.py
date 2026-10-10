# -*- coding: utf-8 -*-
"""
B1 婚嫁本命三煞典据修正 verify（2026-10-11 用户拍板 B1）
=========================================================
典据：《陈子性藏书》页799 和尚杀例："即和尚煞，亦云孤神寡宿，及本命三殺也，
犯之主无子息，其例只论男命不论女命……若以女命论者错矣"。
研究文档：docs/典据研究_三煞概念正名_事主四柱全家族.md §8（判据 a-d）。

修正点（最终态）：
  ① 删除"日干克年干＝真三煞-25／不克得天月德＝假三煞-10"分档：
     真假分档四书 0 载；本命层天月德化解与《协纪辨方书》卷33"吉不能制"、
     卷34"四德走天干不走地支，不能制地支方煞"冲突。统一一档 -25。
  ② 查询对象由新娘改为新郎（典据只论男命）；新娘同犯仅 0 分对照展示。
  ③ 第三位依《考原》"劫煞/灾煞/岁煞"定名，旧标"月煞"正名为"岁煞"。

真值独立：煞局/命名/方向表硬编码自陈书页799 + 协纪卷3，不从软件反推；
日期干支用生产函数 get_day_ganzhi 历查定位（仅历法查表）。
走生产入口：modules.婚嫁评分算法.score_marriage_day / Scorer._extract_bride_groom。
"""
import io
import sys
from datetime import date, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.婚嫁评分算法 import score_marriage_day, get_day_ganzhi
from modules.shensha import marriage_shensha
from modules.评分器 import Scorer

FAILS = []


def check(name, cond, extra=''):
    print(('[OK] ' if cond else '[FAIL] ') + name + (('  ' + extra) if extra else ''))
    if not cond:
        FAILS.append(name)


# ===== 权威真值（硬编码，典据见模块 docstring） =====
# 生年局三合 → 对冲三支（劫/灾/岁）与方向
SHA_TABLE = {
    '申': (('巳', '劫煞', '南'), ('午', '灾煞', '南'), ('未', '岁煞', '南')),
    '子': (('巳', '劫煞', '南'), ('午', '灾煞', '南'), ('未', '岁煞', '南')),
    '辰': (('巳', '劫煞', '南'), ('午', '灾煞', '南'), ('未', '岁煞', '南')),
    '寅': (('亥', '劫煞', '北'), ('子', '灾煞', '北'), ('丑', '岁煞', '北')),
    '午': (('亥', '劫煞', '北'), ('子', '灾煞', '北'), ('丑', '岁煞', '北')),
    '戌': (('亥', '劫煞', '北'), ('子', '灾煞', '北'), ('丑', '岁煞', '北')),
    '亥': (('申', '劫煞', '西'), ('酉', '灾煞', '西'), ('戌', '岁煞', '西')),
    '卯': (('申', '劫煞', '西'), ('酉', '灾煞', '西'), ('戌', '岁煞', '西')),
    '未': (('申', '劫煞', '西'), ('酉', '灾煞', '西'), ('戌', '岁煞', '西')),
    '巳': (('寅', '劫煞', '东'), ('卯', '灾煞', '东'), ('辰', '岁煞', '东')),
    '酉': (('寅', '劫煞', '东'), ('卯', '灾煞', '东'), ('辰', '岁煞', '东')),
    '丑': (('寅', '劫煞', '东'), ('卯', '灾煞', '东'), ('辰', '岁煞', '东')),
}
FORBIDDEN = {yz: {t[0] for t in tri} for yz, tri in SHA_TABLE.items()}
MING_OF = {}
FANG_OF = {}
for _yz, _tri in SHA_TABLE.items():
    for _dz, _ming, _fang in _tri:
        MING_OF[_dz] = _ming
        FANG_OF[_dz] = _fang


def find_days(want_zhi, start=date(2023, 1, 1), days=1500):
    """在生产历法中找日支命中的日期列表（仅查表，不涉规则）。"""
    out = []
    d = start
    for _ in range(days):
        if get_day_ganzhi(d)[1] == want_zhi:
            out.append(d)
        d += timedelta(days=1)
    return out


def sansha_rows(result):
    """返回 (负分三煞标签列表, 0分信息三煞行列表)。"""
    neg, info = [], []
    for nm, sc in result.get('details', []):
        s = str(nm)
        if '三煞' in s or '和尚杀' in s:
            if sc < 0:
                neg.append(s)
            elif sc == 0:
                info.append(s)
    return neg, info


# 定位 4 类关键日
D_WU = find_days('午')[0]            # 新郎子局犯（灾煞）；新娘卯局不犯
D_WEI = find_days('未')[0]           # 新郎子局犯（岁煞）
D_SHEN = find_days('申')[0]          # 新郎子局不犯；新娘卯局犯（劫煞）
D_YIN = find_days('寅')[0]           # 双方均不犯
print(f'历查定位：午日={D_WU} 未日={D_WEI} 申日={D_SHEN} 寅日={D_YIN}')
check('定位日支正确（午/未/申/寅）',
      [get_day_ganzhi(d)[1] for d in (D_WU, D_WEI, D_SHEN, D_YIN)] == ['午', '未', '申', '寅'])

BRIDE_MAO = {'year_gan': '己', 'year_zhi': '卯'}
GROOM_ZI = {'year_gan': '戊', 'year_zhi': '子'}

# ===== A. 性别方向：改查新郎，新娘不参与扣分 =====
r = score_marriage_day(D_WU, BRIDE_MAO, GROOM_ZI)
neg, info = sansha_rows(r)
check('A1 午日新郎子局犯：恰 1 条负分三煞', len(neg) == 1, str(neg))
check('A2 负分恒为 -25（无 -10 假三煞档）',
      all(dict(r['details'])[nm] == -25 for nm in neg))
check('A3 负分标签指向新郎且引陈书典据',
      neg and '新郎' in neg[0] and '陈子性藏书' in neg[0] and '只论男命' in neg[0])
check('A4 负分标签不再出现新娘年命/真三煞/假三煞字样',
      neg and '新娘年命' not in neg[0] and '真三煞' not in neg[0] and '假三煞' not in neg[0])
check('A5 新郎犯且新娘不犯：无 0 分新娘对照行',
      not any('新娘' in x for x in info), str(info))

r = score_marriage_day(D_SHEN, BRIDE_MAO, GROOM_ZI)
neg, info = sansha_rows(r)
check('A6 申日只新娘犯：无负分三煞（女命不扣分）', len(neg) == 0, str(neg))
check('A7 出现 0 分行：新郎未犯+新娘对照不扣分+典据说明',
      len(info) == 1 and '新郎' in info[0] and '新娘' in info[0]
      and '对照' in info[0] and '陈子性藏书' in info[0], str(info))

r = score_marriage_day(D_YIN, BRIDE_MAO, GROOM_ZI)
neg, info = sansha_rows(r)
check('A8 寅日双方不犯：无负分', len(neg) == 0)
check('A9 出现"新郎未犯（依典据查男命）"信息行',
      any('新郎' in x and '未犯' in x and '陈子性藏书' in x for x in info), str(info))

# 双方同犯（新郎丑? 取辰日：新郎子局不犯辰——换：新郎用巳酉丑局，辰日犯；新娘卯局辰不犯。
# 改构造双方同犯：新郎子局+新娘寅午戌局，午日双方皆犯）
BRIDE_WU = {'year_gan': '丙', 'year_zhi': '午'}   # 寅午戌局忌亥子丑——午日不犯
# 午日：申子辰方巳午未、寅午戌方亥子丑 → 午日只犯申子辰局。构造双犯须用日支同时在
# 两局禁支——两局禁支不相交，故同犯只可能同日支在同一禁支集，即两人年局相同：
BRIDE_SHEN = {'year_gan': '壬', 'year_zhi': '申'}  # 与子同局，午日同犯
r = score_marriage_day(D_WU, BRIDE_SHEN, GROOM_ZI)
neg, info = sansha_rows(r)
check('A10 同局男女午日同犯：仍只 1 条 -25（新郎）', len(neg) == 1
      and dict(r['details'])[neg[0]] == -25)
check('A11 同犯时附新娘 0 分对照行（不扣分）',
      any('新娘' in x and '对照' in x for x in info), str(info))

# ===== B. 删真假档/天月德化解：犯则恒 -25，天月德不减免 =====
tiande_hits = 0
ke_hits = 0
GAN_WX = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
          '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
d = date(2020, 1, 1)
for _ in range(365 * 6):
    dg, dz = get_day_ganzhi(d)
    if dz in FORBIDDEN['子']:
        rr = score_marriage_day(d, BRIDE_MAO, GROOM_ZI)
        nn, _ = sansha_rows(rr)
        check_pen = nn and dict(rr['details'])[nn[0]] == -25
        check_no_label = nn and ('假三煞' not in nn[0] and '真三煞' not in nn[0])
        if not (check_pen and check_no_label):
            check(f'B 犯煞日恒-25且无真假标签 {d}（{dg}{dz}）', False, str(nn))
        if marriage_shensha.is_tiande_day(d) or marriage_shensha.is_yuede_day(d):
            tiande_hits += 1
            check(f'B-德 天月德日不减免 {d}（{dg}{dz}）', bool(nn), str(nn))
        if GAN_WX.get(dg) and KE[GAN_WX[dg]] == '土':   # 日干木克新郎年干戊土
            ke_hits += 1
    d += timedelta(days=1)
check('B1 2020-2025 犯煞日枚举中存在天月德日（探针有效）', tiande_hits >= 1, f'命中{tiande_hits}天')
check('B2 枚举中存在日干克新郎年干日（旧真三煞情形，探针有效）', ke_hits >= 1, f'命中{ke_hits}天')

# ===== C. 岁煞正名（及劫/灾位命名） =====
for d0, yz_groom, expect_ming in [(D_WEI, '子', '岁煞'), (D_WU, '子', '灾煞')]:
    rr = score_marriage_day(d0, BRIDE_MAO, {'year_gan': '戊', 'year_zhi': yz_groom})
    nn, _ = sansha_rows(rr)
    check(f'C {d0} 日支{get_day_ganzhi(d0)[1]} 命名为{expect_ming}（非月煞）',
         nn and expect_ming in nn[0] and '月煞' not in nn[0], str(nn))
D_SI = find_days('巳')[0]
rr = score_marriage_day(D_SI, BRIDE_MAO, GROOM_ZI)
nn, _ = sansha_rows(rr)
check('C 巳日命名劫煞', nn and '劫煞' in nn[0], str(nn))

# ===== D. 反向/缺参断言 =====
rr = score_marriage_day(D_WU, None, None)
neg, info = sansha_rows(rr)
check('D1 无双方八字：不产生任何三煞行', not neg and not info)

rr = score_marriage_day(D_WU, BRIDE_MAO, {'ri_gan': '庚'})  # 新郎无年柱
neg, info = sansha_rows(rr)
check('D2 新郎缺年柱：不误扣且给缺失提示行',
      not neg and any('新郎' in x and ('缺' in x or '未' in x) for x in info), str(info))

rr = score_marriage_day(D_YIN, BRIDE_MAO, GROOM_ZI)
check('D3 不犯日 details 可正常计总分（>=0）', rr['score'] >= 0)

# ===== E. 生产接线：Scorer._extract_bride_groom 必须取到新郎年柱 =====
sc = Scorer()
owners = [
    {'role': '新郎', '性别': '男', 'sizhu': '甲子 丙寅 丁丑 戊申'},
    {'role': '新娘', '性别': '女', 'sizhu': '己卯 丁卯 戊辰 庚申'},
]
b, g = sc._extract_bride_groom(owners)
check('E1 新郎年柱已提取（year_gan/year_zhi）',
      g and g.get('year_gan') == '甲' and g.get('year_zhi') == '子', str(g))
check('E2 新郎月/日柱提取不受影响',
      g.get('yue_gan') == '丙' and g.get('ri_gan') == '丁', str(g))
check('E3 新娘年柱提取不回归',
      b and b.get('year_gan') == '己' and b.get('year_zhi') == '卯', str(b))

print('\n' + '=' * 56)
print('FAIL %d' % len(FAILS))
sys.exit(1 if FAILS else 0)
