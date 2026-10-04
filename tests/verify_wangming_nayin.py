# -*- coding: utf-8 -*-
"""verify：安葬亡命（仙命）纳音核心 · 第一阶段

覆盖：
1. 六十甲子纳音 30 组：独立权威值（纳音口诀）与 二十四山.NAYIN_NAMES 双向断言
2. 亡命信息生成：5 样本（甲子海中金/戊辰大林木/丙子涧下水/戊子霹雳火/庚午路旁土）
3. 仙命真冲三级判定（2026-10-04 用户拍板 + 验收补档）：
   - 叠三煞/岁破/月破（日破）→ 直接否决（有制化也不救）
   - 无宽集化解吉神 → 显式一票否决（不再靠五行分间接门槛）
   - 有宽集化解吉神（天德/月德/岁德/太阳到山/天赦/天愿/三合/六合）
     → 仅扣分（WARN），真冲行标注"有制化：…"
   - 反：不冲之日不出现该条
4. 月支与亡命破刑害降为提示（info_reasons，第一阶段临时降级，第二阶段重估）
5. 流年（太岁）层：仙命六冲 = 岁破级否决（analyze_year + 相主硬门槛双保险）；
   破/刑/害 = 临时降级提示
6. 兼容性：无亡命 owner / 非安葬典型 owners → wangming_info 为 None
退出码：全过 0，失败 1。
"""
import sys
import datetime as dt

sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')

FAILS = []


def check(name, cond):
    print(('  OK ' if cond else '  FAIL ') + name)
    if not cond:
        FAILS.append(name)


# ---- 独立权威纳音表（30组，口诀：海炉大林路锋山涧城白柳泉屋霹松长沙下平壁金覆天驿钗桑大沙大海）----
AUTH_NAYIN = {
    0: '海中金', 1: '炉中火', 2: '大林木', 3: '路旁土', 4: '剑锋金',
    5: '山头火', 6: '涧下水', 7: '城头土', 8: '白蜡金', 9: '杨柳木',
    10: '泉中水', 11: '屋上土', 12: '霹雳火', 13: '松柏木', 14: '长流水',
    15: '沙中金', 16: '山下火', 17: '平地木', 18: '壁上土', 19: '金箔金',
    20: '覆灯火', 21: '天河水', 22: '大驿土', 23: '钗钏金', 24: '桑柘木',
    25: '大溪水', 26: '沙中土', 27: '天上火', 28: '石榴木', 29: '大海水',
}
GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
JIAZI = [GAN[i % 10] + ZHI[i % 12] for i in range(60)]

from modules.二十四山 import NAYIN_NAMES, NAYIN_WUXING

print('== 1. 纳音表独立权威双向断言 ==')
for i in range(60):
    gz = JIAZI[i]
    check('%s 纳音=%s' % (gz, AUTH_NAYIN[i // 2]),
          NAYIN_NAMES[gz] == AUTH_NAYIN[i // 2])
# 反向：被测表60项全部来自30组权威值（无表外值）
check('NAYIN_NAMES 60 项值域 ⊆ 30 组权威值',
      set(NAYIN_NAMES.values()) == set(AUTH_NAYIN.values()))
# 五行自洽：纳音名末字 = NAYIN_WUXING
check('NAYIN_WUXING 与纳音名末字自洽（60项）',
      all(NAYIN_WUXING[gz] == NAYIN_NAMES[gz][-1] for gz in JIAZI))

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score


def pure_score(d0, owners, event='安葬'):
    sz = calculate_sizhu(d0, 12, 0)
    sz.update({'year': d0.year, 'month': d0.month, 'day': d0.day, 'date': d0})
    return calculate_score(sz, event, owners, None, None, None, None, None)


def dead(name, bd):
    return {'name': name, 'role': '死者', '性别': '男', 'birth_date': bd}


print('== 2. 亡命信息 5 样本（走生产入口，立春后日期）==')
SAMPLES = [
    ('甲子命', '1924-03-01', '甲子', '海中金', '金'),
    ('戊辰命', '1928-03-01', '戊辰', '大林木', '木'),
    ('丙子命', '1936-03-01', '丙子', '涧下水', '水'),
    ('戊子命', '1948-03-01', '戊子', '霹雳火', '火'),
    ('庚午命', '1930-03-01', '庚午', '路旁土', '土'),
]
D_BASE = dt.date(2026, 1, 19)  # 已实证中性日，确保非提前返回
for label, bd, ygz, nayin, wx in SAMPLES:
    r = pure_score(D_BASE, [dead(label, bd)])
    wm = r.get('wangming_info')
    check('%s wangming_info=%s/%s/%s' % (label, ygz, nayin, wx),
          bool(wm) and wm['年柱'] == ygz and wm['纳音'] == nayin
          and wm['五行'] == wx)
    check('%s 综合评语含亡命段' % label,
          ('亡命（仙命）：%s，%s年生，%s命（%s）'
           % (label, ygz, nayin, wx)) in r.get('reason', ''))

print('== 3. 仙命真冲三级判定 ==')

# 3a. 基础冲扣分：01-05 卯日 / 乙酉仙命（当天五行19走提前返回，仍否决）
D0105 = dt.date(2026, 1, 5)
owners_chong = [dead('某公', '1945-08-15'),
                {'name': '孝子甲', 'role': '孝子1', '性别': '男',
                 'birth_date': '1999-04-05'},
                {'name': '孝子乙', 'role': '孝子2', '性别': '男',
                 'birth_date': '1998-10-13'}]
r_chong = pure_score(D0105, owners_chong)
sd = r_chong.get('score_details') or {}
xz = sd.get('相主详情') or []
print('   相主详情=%s' % xz)
chong_lines = [d for d in xz if '真冲' in d]
check('仙命真冲 -30 且文案含"须见吉神制化"',
      len(chong_lines) == 1 and '-30分' in chong_lines[0]
      and '仙命' in chong_lines[0] and '制化' in chong_lines[0])
check('仙命真冲不带 [硬性门槛] 前缀（三级判定独立于相主否决通道）',
      all(not str(d).startswith('[硬性门槛]') for d in xz))
check('当天总分0、❌凶、有否决原因（不裸放）',
      r_chong.get('score') == 0 and r_chong.get('level') == '❌ 凶'
      and bool(r_chong.get('veto_reasons')))
check('亡命日支害已剔除（相主仅 -30，不再有 -5 日支害）',
      sd.get('相主得分') == -30)

# 反向断言：同一仙命在不冲之日（2026-01-19 巳日，巳酉半合）无真冲条
D0119 = dt.date(2026, 1, 19)
r_no = pure_score(D0119, owners_chong)
xz_no = (r_no.get('score_details') or {}).get('相主详情') or []
check('反向：巳日无仙命真冲条', not any('真冲' in str(d) for d in xz_no))

# 3b. 叠重煞直否：2026-04-25 巳日乙亥仙命，叠月三煞 → 直接否决（不论制化）
r_heavy = pure_score(dt.date(2026, 4, 25), [dead('乙亥命', '1935-03-01')])
_vh = [v for v in (r_heavy.get('veto_reasons') or []) if '仙命真冲叠大忌' in v]
check('叠三煞 → "仙命真冲叠大忌"显式否决',
      bool(_vh) and '叠三煞' in _vh[0]
      and r_heavy.get('score') == 0 and r_heavy.get('level') == '❌ 凶')

# 3c. 无制化否决：2026-06-24 巳日乙亥仙命，无宽集吉神 → 显式否决
r_bare = pure_score(dt.date(2026, 6, 24), [dead('乙亥命', '1935-03-01')])
_vb = [v for v in (r_bare.get('veto_reasons') or []) if '仙命真冲无制化' in v]
check('无化解吉神 → "仙命真冲无制化"显式否决',
      bool(_vb) and '大忌不用' in _vb[0]
      and r_bare.get('score') == 0 and r_bare.get('level') == '❌ 凶')

# 3d. 有制化 WARN：2026-02-22 卯日乙酉仙命，天德制化 → 仅 -30 扣分，不否决
r_warn = pure_score(dt.date(2026, 2, 22), [dead('乙酉命', '1945-08-15')])
xz_warn = (r_warn.get('score_details') or {}).get('相主详情') or []
_wline = [str(d) for d in xz_warn if '真冲' in str(d)]
check('有制化：真冲行标注"（有制化：天德）"',
      len(_wline) == 1 and '有制化：天德' in _wline[0])
check('有制化：不否决、总分>0、等级非凶',
      not r_warn.get('veto_reasons') and r_warn.get('score', 0) > 0
      and r_warn.get('level') != '❌ 凶')

print('== 4. 月支与亡命破刑害：临时降级提示 ==')
# 01-05 月支子；子酉相破。直接单测 analyze_month 通道：
analysis = None
from modules.评分器 import Scorer
_m_date = dt.date(2026, 1, 5)
ma = Scorer().analyze_month(
    _m_date, '安葬', owners_chong, None, None,
    day_sizhu=calculate_sizhu(D0105, 12, 0), zeli_mode='feixing')
print('   month score=%s reasons=%s info=%s'
      % (ma.get('score'), ma.get('reasons'), ma.get('info_reasons')))
check('月支破亡命不扣分（score 无 -15 破罚）',
      not any('相破' in r_ for r_ in (ma.get('reasons') or [])))
check('月支破亡命进 info_reasons 提示且标注临时降级',
      any('相破' in r_ and '亡命' in r_ and '第一阶段临时降级' in r_
          for r_ in (ma.get('info_reasons') or [])))

print('== 5. 流年（太岁）层：冲否 / 破刑害提示 ==')
# analyze_year 整数年 2026 = 丙午年：子 wm 冲午太岁 → 岁破级否决
ya = Scorer().analyze_year(2026, '安葬', [dead('丙子命', '1936-03-01')], None)
check('仙命冲流年太岁 → suitable=False/大凶',
      ya.get('suitable') is False and ya.get('level') == '大凶'
      and any('冲流年太岁' in r and '岁破级' in r
              for r in (ya.get('reasons') or [])))
# 午卯破 → 临时降级提示，可否
ya2 = Scorer().analyze_year(2026, '安葬', [dead('己卯命', '1939-03-01')], None)
check('流年破亡命 → 临时降级提示、不否决',
      ya2.get('suitable') is True
      and any('相破' in r and '第一阶段临时降级' in r
              for r in (ya2.get('info_reasons') or [])))
# sizhu 直传路径双保险：2026-01-19（年支巳）乙亥仙命 → 相主硬门槛否决
r_yc = pure_score(D0119, [dead('乙亥命', '1935-03-01')])
check('sizhu 直传：仙命冲太岁走相主硬门槛否决',
      any('冲流年太岁' in v for v in (r_yc.get('veto_reasons') or []))
      and r_yc.get('score') == 0 and r_yc.get('level') == '❌ 凶')

print('== 6. 兼容性 ==')
r_none = pure_score(D0119, [
    {'name': '孝子甲', 'role': '孝子1', '性别': '男', 'birth_date': '1999-04-05'}])
check('无死者卡 → wangming_info=None', r_none.get('wangming_info') is None)
r_marr = pure_score(D0119, [
    {'name': '新娘', 'role': '新娘', '性别': '女', 'birth_date': '1999-04-05'},
    {'name': '新郎', 'role': '新郎', '性别': '男', 'birth_date': '1998-10-13'}],
    event='嫁娶')
check('嫁娶典型 owners → wangming_info=None', r_marr.get('wangming_info') is None)
# 别名兼容
r_alias = pure_score(D0119, [
    {'name': '仙命某', 'role': '仙命', '性别': '男',
     'birth_date': '1945-08-15'}])
check('role 别名"仙命"同样被识别',
      bool(r_alias.get('wangming_info'))
      and r_alias['wangming_info']['年柱'] == '乙酉')

print('=' * 60)
if FAILS:
    print('FAIL %d: %s' % (len(FAILS), FAILS))
    sys.exit(1)
print('ALL PASS')
sys.exit(0)
