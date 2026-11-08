# -*- coding: utf-8 -*-
"""verify：E002/E207 误报修复回归（2026-02-22 嫁娶 126分降一格案例）。

修复内容：
1. E207（主程序.py _inject_best_hour_to_result 合局重算块）：合局 delta
   只同步了 score_details 的 '五行评分'/'总分'，漏同步同源键 '嫁娶评分'，
   致轻量总分恒等式（嫁娶评分+月令+喜用+太阳太阴=总分）误报
   （原案：嫁娶评分滞留 103 vs 五行评分 110，103+5+11+0=119≠126）。
2. E002（日课校验器.py rule_e002）：旧口径只认"原始总分纯函数+一级封顶"，
   不认识 §179 分位归一化与 2026-10-08 拍板的二级降一格，凡归一化/降格
   生效的嫁娶日必误报。改为与生产链完全同源复算。

黄金断言走产品真实入口（Scorer.score → 主程序._inject_best_hour_to_result
→ lint_lesson，与 GUI 择日链路同源）；反向断言用篡改/合成 detail。
分值真值取自 2026-02-22 实报（§236 重冻后 111 分 / ★★★★ 大吉（小忌，降一格）；
§236 前为 126 分，差异 = 相主并入总分且年命伏吟 -15），不反推实现逻辑。

退出码 0=全过，1=有失败。
"""
import sys, io, datetime as dt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import date
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer
from modules.日课校验器 import lint_lesson

FAILS = []
def check(name, cond):
    if not cond:
        FAILS.append(name)
        print(f'  FAIL: {name}')


def _gui_owner(name, role, gender, y, m, d, hh, mm, xishen='', yongshen=''):
    """与主程序择日入口同款的事主信息（含出生四柱与喜用神字段）。"""
    bd = date(y, m, d)
    sz = calculate_sizhu(bd, hh, mm)
    return {
        'name': name, 'role': role, 'birth_date': bd,
        'birth_hour': hh, 'birth_minute': mm,
        '性别': gender,
        '年干': sz.get('year_gan', ''), '年支': sz.get('year_zhi', ''),
        '日干': sz.get('day_gan', ''), '日支': sz.get('day_zhi', ''),
        '生肖': sz.get('year_zhi', ''),
        'xishen': xishen, 'yongshen': yongshen,
    }


OWNERS = [
    _gui_owner('欢', '新娘', '女', 1999, 4, 5, 6, 0, xishen='水、金'),
    _gui_owner('文旺', '新郎', '男', 1998, 10, 13, 23, 30, yongshen='金、水'),
]


def _pipeline_20260222():
    """2026-02-22 嫁娶全链路（与 GUI 择日同源：午时初评→注入最佳时柱，
    注入内含12时辰权威重算与合局重算）。"""
    d = dt.date(2026, 2, 22)
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d; sz['year'] = d.year; sz['month'] = d.month; sz['day'] = d.day
    score_result = Scorer().score(sz, '嫁娶', owners=OWNERS)
    import tkinter as _tk
    root = _tk.Tk(); root.withdraw()
    try:
        import 主程序 as _appmod
        app = _appmod.ZeriApp(root)
        display = {}
        app._inject_best_hour_to_result(
            display, score_result, '嫁娶', OWNERS, d, sz)
    finally:
        root.destroy()
    return score_result


# ===== A. 真实链路：2026-02-22 嫁娶（E207/E002 原案） =====
print('A. 真实链路 2026-02-22 嫁娶')
r = _pipeline_20260222()
from modules.推荐时柱 import build_checker
_ck, _ = build_checker('嫁娶', None, '')
_lh = _ck.get_lucky_hours(r.get('sizhu'))
lint = lint_lesson(r, lucky_hours=_lh, bride_year_zhi='卯')
sd = r.get('score_details') or {}

check('A1 合局重算已生效（五行评分=110，三合局+15 替换半合局+8）',
      sd.get('五行评分') == 110)
check('A2 修复后嫁娶评分键与五行评分键同值（不再漂移）',
      sd.get('嫁娶评分') == sd.get('五行评分'))
check('A3 恒等式成立：嫁娶评分+月令+喜用+太阳太阴+相主=总分',
      (sd.get('嫁娶评分', 0) + sd.get('月令得分', 0)
       + sd.get('喜用神得分', 0) + sd.get('太阳太阴得分', 0)
       + sd.get('相主得分', 0)) == sd.get('总分'))
# §236（2026-11-08）：B3 相主并入总分（-15 年命伏吟）+ B4 伏吟 -15，
# 原锚点 126 → 111（110+5+11+0-15），以本轮 GUI 同源链路实报为准。
check('A4 行为锚点：§236 重冻后总分为 111', r.get('score') == 111)
check('A5 行为锚点：等级仍为 ★★★★ 大吉（小忌，降一格）',
      r.get('level') == '★★★★ 大吉（小忌，降一格）')
_e207 = [i for i in lint.issues if i.rule_id == 'E207']
_e002 = [i for i in lint.issues if i.rule_id == 'E002']
check('A6 E207 不再误报', not _e207)
check('A7 E002 不再误报', not _e002)
check('A8 校验整体无 ERROR', lint.passed)

# A9 反向：篡改嫁娶评分键 → E207 必报（还原修复前漂移态）
_rt = dict(r)
_sdt = dict(sd)
_sdt['嫁娶评分'] = (sd.get('嫁娶评分') or 0) - 7
_rt['score_details'] = _sdt
_lt = lint_lesson(_rt)
check('A9 反向：嫁娶评分漂移时 E207 必报',
      any(i.rule_id == 'E207' and '恒等式不符' in i.message
          for i in _lt.issues))

# A10 反向：篡改等级（摘掉降一格）→ E002 必报
_rt2 = dict(r)
_rt2['level'] = '★★★★★ 上吉'
_lt2 = lint_lesson(_rt2)
check('A10 反向：夫星受克日等级未降一格时 E002 必报',
      any(i.rule_id == 'E002' for i in _lt2.issues))


# ===== B. E002 合成用例（嫁娶生产链复算口径） =====
print('B. E002 合成用例')

def _mk(score, wx, level, details, warnings=None):
    return {'score': score, 'level': level,
            'score_details': {'嫁娶评分': wx, '五行评分': wx},
            'marriage_details': details,
            'warnings': warnings or []}

# B1 正向：126 分（归一化后上吉）+夫星触发 → 大吉（小忌，降一格）合法
_d = _mk(126, 110, '★★★★ 大吉（小忌，降一格）', [('夫星受克（测试）', -20)])
check('B1 二级降一格合法样例不报 E002',
      not any(i.rule_id == 'E002' for i in lint_lesson(_d).issues))

# B2 反向：同上但未降格（自称上吉）→ 必报
_d = _mk(126, 110, '★★★★★ 上吉', [('夫星受克（测试）', -20)])
check('B2 应降未降报 E002',
      any(i.rule_id == 'E002' for i in lint_lesson(_d).issues))

# B3 反向：降两格（吉）→ 必报
_d = _mk(126, 110, '★★★ 吉（小忌，降一格）', [('夫星受克（测试）', -20)])
check('B3 降格幅度错误报 E002',
      any(i.rule_id == 'E002' for i in lint_lesson(_d).issues))

# B4 正向：一级封顶（details 含"忌嫁娶"）→ ★ 平（犯忌嫁娶，慎用）合法
_d = _mk(126, 110, '★ 平（犯忌嫁娶，慎用）', [('小黄道除日忌嫁娶（测试）', -5)])
check('B4 一级封顶合法样例不报 E002',
      not any(i.rule_id == 'E002' for i in lint_lesson(_d).issues))

# B5 反向：一级封顶缺后缀 → 必报
_d = _mk(126, 110, '★ 平', [('小黄道除日忌嫁娶（测试）', -5)])
check('B5 一级封顶缺慎用后缀报 E002',
      any(i.rule_id == 'E002' for i in lint_lesson(_d).issues))

# B6 正向：无触发源 → 归一化后上吉，等级不降为合法
_d = _mk(126, 110, '★★★★★ 上吉', [('基础分', 60)])
check('B6 无触发源高分为上吉不报 E002',
      not any(i.rule_id == 'E002' for i in lint_lesson(_d).issues))

# B7 反向：无触发源却自称降一格 → 必报
_d = _mk(126, 110, '★★★★ 大吉（小忌，降一格）', [('基础分', 60)])
check('B7 无触发源伪降格报 E002',
      any(i.rule_id == 'E002' for i in lint_lesson(_d).issues))

# B8 正向：warnings 含"忌嫁娶"触发二级（阳错/阴差阳错通道）
_d = _mk(126, 110, '★★★★ 大吉（小忌，降一格）', [('基础分', 60)],
         warnings=['阴阳差错日，忌嫁娶'])
check('B8 warnings 忌嫁娶触发二级降格合法',
      not any(i.rule_id == 'E002' for i in lint_lesson(_d).issues))

# B9 非嫁娶回归：旧口径不变（原始总分纯函数）
_d = {'score': 126, 'level': '★★★★ 大吉',
      'score_details': {'五行评分': 110}}
check('B9a 非嫁娶 126 分自称大吉仍报 E002（旧口径保持）',
      any(i.rule_id == 'E002' for i in lint_lesson(_d).issues))
_d = {'score': 126, 'level': '★★★★★ 上吉',
      'score_details': {'五行评分': 110}}
check('B9b 非嫁娶 126 分上吉不报 E002（旧口径不变）',
      not any(i.rule_id == 'E002' for i in lint_lesson(_d).issues))

print(f'\n==== {"ALL PASS" if not FAILS else "FAIL %d" % len(FAILS)} ====')
sys.exit(1 if FAILS else 0)
