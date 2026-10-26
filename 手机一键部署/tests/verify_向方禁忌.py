# -*- coding: utf-8 -*-
"""verify_向方禁忌.py —— 向方判定层 + 死链修复批验证（001 §185）

判据（用户拍板 2026-10-26，镜像解读）：
  1. 向方月破：协纪279252:163「月破可向不可坐」有载 → 补注册，重扣分 -20
     （PENDING 档）不否决。向首＝「向」字前一山，与坐山恒对宫，坐向天然互斥。
  2. 向方三煞：协纪卷八/陈书13处「三煞可向不可坐」→ 补注册，-25/-20/-15，
     不否决，不列大忌。
  3. 向首犯岁破/向首犯太岁：镜像承接不另计（坐太岁可用 / Layer1.1 坐山岁破否决）。
  4. D1 出行太岁方位谓词复活：协纪卷三「太岁所在之辰必不可犯」→ 日支临流年
     太岁支（day==year）发射 -10。
  5. D2 '日支未冲太岁' 死关键词彻底删除（全库无生产者）。

硬性要求：退出码 0 全过 / 1 有失败；正反断言成对；走生产入口 calculate_score。
黄金用例为月份级静态条件（不依赖日期干支猜测）：
  2026 丙午年（年煞北 亥子丑）；2026-03 辛卯月（月破酉；亥卯未局煞西 申酉戌）；
  2026-10 戊戌月（寅午戌局煞北 亥子丑；月破辰）。
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))

from datetime import date, timedelta
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score

FAILS = []


def check(name, cond, extra=''):
    tag = 'PASS' if cond else 'FAIL'
    print(f'{tag} {name}' + (f' | {extra}' if extra else ''))
    if not cond:
        FAILS.append(name)


def run(y, m, d, ev, sx=None):
    sz = calculate_sizhu(date(y, m, d), 12, 0)
    kw = {'shan_xiang': sx} if sx else {}
    return calculate_score(sz, ev, owners=[], **kw)


def shensha_names(result):
    return [s if isinstance(s, str) else s.get('name', '')
            for s in (result.get('shensha_list') or [])]


# ---------- 一、向方月破（-20 PENDING 档，不否决） ----------
r = run(2026, 3, 15, '修造', '乙山辛向')  # 卯月月破酉；向首辛→酉
ji = r.get('ji_list', [])
check('1.1 向方月破发射(卯月乙山辛向)', '向方月破' in ji, f'ji={ji}')
check('1.2 不否决', not r.get('is_veto'), f'level={r.get("level")} is_veto={r.get("is_veto")}')
check('1.3 扣分进分项', r.get('score_details', {}).get('向方扣分', 0) == -20
      or (r.get('score_details', {}).get('向方扣分', 0) == 0 and not ji),
      f"向方扣分={r.get('score_details', {}).get('向方扣分')}")
xd = r.get('score_details', {}).get('向方扣分明细', [])
check('1.4 明细含PENDING档标注', any('PENDING' in str(x) for x in xd), f'明细={xd}')

r2 = run(2026, 10, 15, '修造', '乙山辛向')  # 戌月月破辰；向首酉≠辰（反向）
check('1.5 反向:非月破月不发射', '向方月破' not in r2.get('ji_list', []),
      f"ji={r2.get('ji_list', [])}")

r3 = run(2026, 3, 15, '修造', '艮山坤向')  # 四维宫全宫并判：坤→未申，未申≠酉
check('1.6 反向:四维宫未中月破不发射向方月破', '向方月破' not in r3.get('ji_list', []),
      f"ji={r3.get('ji_list', [])}")

# ---------- 二、向方三煞（-25/-20/-15，不否决不列大忌） ----------
r = run(2026, 10, 15, '修造', '丙山壬向')  # 午年煞北子∈、戌月煞北子∈
ji = r.get('ji_list', [])
check('2.1 年三煞(向方)发射', '年三煞(向方)' in ji, f'ji={ji}')
check('2.2 月三煞(向方)发射', '月三煞(向方)' in ji, f'ji={ji}')
check('2.3 不否决', not r.get('is_veto'), f'is_veto={r.get("is_veto")}')
si = r.get('sansha_info') or {}
check('2.4 向方三煞进三煞明细', any('向方' in str(x) for x in si.get('sansha_penalty_detail', [])),
      f"detail={si.get('sansha_penalty_detail')}")

r2 = run(2026, 3, 15, '修造', '乙山辛向')  # 卯月煞西申酉戌⊃酉
check('2.5 月三煞(向方)卯月发射', '月三煞(向方)' in r2.get('ji_list', []),
      f"ji={r2.get('ji_list', [])}")

r3 = run(2026, 10, 15, '修造', '乙山辛向')  # 戌月煞北；向首酉∉亥子丑（反向）
check('2.6 反向:向首不犯煞不发射',
      not any(k in r3.get('ji_list', []) for k in ('年三煞(向方)', '月三煞(向方)', '日三煞(向方)')),
      f"ji={r3.get('ji_list', [])}")

# (向方) 项不列大忌（_generate_wu_xing_jiyu 排除）
r4 = run(2026, 10, 15, '修造', '丙山壬向')
wx = r4.get('wu_xing_result') or {}
daji_text = str(wx.get('jiyu', '') or '')
check('2.7 向方项不列大忌评语', '年三煞(向方)' not in daji_text or '向方' not in daji_text,
      f'评语含向方大忌={("年三煞(向方)" in daji_text)}')

# ---------- 三、镜像承接（不另计） ----------
# 向首犯岁破 ⟺ 坐太岁（轻侧）：午年 丙山壬向? 坐太岁=坐山午；向首犯岁破=向首子。
# 子山午向：坐子（岁破位，Layer1.1 管坐山）向首午=太岁位——镜像判定向侧不产
# '向方岁破'/'向方太岁' 扣分键。
r = run(2026, 10, 15, '修造', '子山午向')
ji = r.get('ji_list', [])
check('3.1 无向方岁破/向方太岁键',
      not any(('岁破' in k and '向方' in k) or ('太岁' in k and '向方' in k) for k in ji),
      f'ji={ji}')

# ---------- 四、D1 出行太岁方位复活 ----------
hit, miss = None, None
d = date(2026, 6, 1)
while d < date(2026, 7, 1) and (hit is None or miss is None):
    dz = calculate_sizhu(d, 12, 0).get('day_zhi')
    if dz == '午' and hit is None:
        hit = d
    elif dz != '午' and hit and d > hit and miss is None:
        miss = d
    d += timedelta(days=1)

r = calculate_score(calculate_sizhu(hit, 12, 0), '出行', owners=[])
check('4.1 午日出行太岁方位发射', '太岁方位' in shensha_names(r), f'{hit} names={shensha_names(r)}')
r2 = calculate_score(calculate_sizhu(miss, 12, 0), '出行', owners=[])
check('4.2 反向:非午日不发射', '太岁方位' not in shensha_names(r2), f'{miss} names={shensha_names(r2)}')

# ---------- 五、D2 死关键词已删除 ----------
import re
src = open(os.path.join(os.path.dirname(__file__), '..', 'modules', '评分器.py'),
           encoding='utf-8').read()
check('5.1 D2关键词已从硬否决表删除', '日支未冲太岁' not in re.sub(r'#.*', '', src),
      '评分器.py 代码区无 日支未冲太岁')

# ---------- 六、坐向互斥（同课无叠计） ----------
# 乙山辛向 卯月：坐乙=卯=月建（坐山临月建非禁项），向首酉=月破——同一月支只落一侧
sz = calculate_sizhu(date(2026, 3, 15), 12, 0)
r = calculate_score(sz, '修造', owners=[], shan_xiang='乙山辛向')
si = r.get('sansha_info') or {}
zx = si.get('xiangfang_zhis', [])
check('6.1 向首解析=辛→酉', zx == ['酉'], f'xiangfang_zhis={zx}')

print()
if FAILS:
    print(f'FAIL {len(FAILS)}: ' + '; '.join(FAILS))
    sys.exit(1)
print('ALL PASS')
sys.exit(0)
