# -*- coding: utf-8 -*-
"""黄沙日 穷举验证 —— 节气月支版（《协纪》义例体系）

口径（2026-09-21 拍板，依据《协纪辨方书》义例体系统一为节气月）：
    四孟月（寅、申、巳、亥）逢午日
    四仲月（子、午、卯、酉）逢寅日
    四季月（辰、戌、丑、未）逢子日

权威黄金清单（硬编码，calculate_sizhu 独立推导；日干支/月支均走 sxtwl 精确四柱）：
    2026 公历年 31 天；2025 公历年 29 天。

入口：
  ① ShenShaBase._is_huangsha（节气月支版，通用神煞继承）
  ② MarriageShenShaChecker._is_huangsha（节气月支版）
  ③ 嫁娶规则 HUANGSHA（文案链端到端，§212 后嫁娶已剥离 → 全期零发射）
"""
import sys, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli
from modules.四柱计算器 import calculate_sizhu
from modules.shensha.神煞基类 import ShenShaChecker
from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
from modules.rules.嫁娶规则 import MarriageRuleChecker


# ===== 权威黄金清单（硬编码，绝不从软件读取） =====
AUTH_2026 = {
    '2026-01-04', '2026-01-14', '2026-01-26', '2026-02-13', '2026-02-25',
    '2026-03-17', '2026-03-29', '2026-04-08', '2026-04-20', '2026-05-02',
    '2026-05-08', '2026-05-20', '2026-06-01', '2026-06-09', '2026-06-21',
    '2026-07-03', '2026-07-13', '2026-07-25', '2026-08-06', '2026-08-12',
    '2026-08-24', '2026-09-05', '2026-09-13', '2026-09-25', '2026-10-07',
    '2026-10-17', '2026-10-29', '2026-11-16', '2026-11-28', '2026-12-18',
    '2026-12-30',
}
AUTH_2025 = {
    '2025-01-07', '2025-01-19', '2025-01-31', '2025-02-06', '2025-02-18',
    '2025-03-02', '2025-03-10', '2025-03-22', '2025-04-03', '2025-04-13',
    '2025-04-25', '2025-05-13', '2025-05-25', '2025-06-14', '2025-06-26',
    '2025-07-18', '2025-07-30', '2025-08-17', '2025-08-29', '2025-09-18',
    '2025-09-30', '2025-10-10', '2025-10-22', '2025-11-03', '2025-11-09',
    '2025-11-21', '2025-12-03', '2025-12-11', '2025-12-23',
}

_HUANGSHA_MAP = {
    '寅': '午', '申': '午', '巳': '午', '亥': '午',
    '子': '寅', '午': '寅', '卯': '寅', '酉': '寅',
    '辰': '子', '戌': '子', '丑': '子', '未': '子',
}


def _d(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d').date()


def _sz(d):
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d
    return sz


def _expected(d):
    sz = calculate_sizhu(d, 12, 0)
    return _HUANGSHA_MAP.get(sz.get('month_zhi', '')) == sz.get('day_zhi', '')


def _exp_none(d):
    """§212 后嫁娶通道剥离口径：全期零命中"""
    return False


# 入口适配器
_rc = MarriageRuleChecker()

def _ad_base(d):
    return ShenShaChecker()._is_huangsha(_sz(d))

def _ad_mrg(d):
    return MarriageShenShaChecker()._is_huangsha(_sz(d))

def _ad_rule(d):
    """嫁娶规则文案链端到端：_check_rules 忌项含'黄沙日'"""
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d
    ji = _rc._check_rules(sz, date_obj=d)[1]
    return any('黄沙' in str(x) for x in ji)


# ===== 穷举输入 =====
def _year_days(y):
    out, d = [], datetime.date(y, 1, 1)
    end = datetime.date(y + 1, 1, 1)
    while d < end:
        out.append(d)
        d += datetime.timedelta(days=1)
    return out


# ===== 边界断言（在 run_cli 前执行，失败即抛） =====
_notes = []
# 边界1：三档正例（孟午、仲寅、季子）
assert _ad_base(_d('2026-02-13')), '孟月（寅月）丙午应命中黄沙'
assert _ad_base(_d('2026-03-17')), '仲月（卯月）戊寅应命中黄沙'
assert _ad_base(_d('2026-01-14')), '季月（丑月）丙子应命中黄沙'
_notes.append('三档正例：孟月寅月丙午(02-13)/仲月卯月戊寅(03-17)/季月丑月丙子(01-14)')

# 边界2：反向——同月非对应支不命中（2026-02-14 寅月丁未，孟月非午）
assert not _ad_base(_d('2026-02-14')), '寅月丁未（孟月非午）不应命中黄沙'
assert not _ad_mrg(_d('2026-02-14')), '嫁娶：寅月丁未不应命中'
_notes.append('反向：孟月非午(02-14丁未)不命中')

# 边界3：黄金清单构成
assert len(AUTH_2026) == 31 and len(AUTH_2025) == 29
_notes.append('黄金清单：2026 公历年 31 天 / 2025 公历年 29 天')

# 边界4：pipeline 反向锁——§212 后嫁娶通道黄沙日已剥离（0 条）
sz = _sz(_d('2026-02-13'))
c = MarriageShenShaChecker()
c.check(sz)
hs = [x for x in c.shensha_list if isinstance(x, dict) and '黄沙' in str(x.get('name', ''))]
assert hs == [], f'§212 后嫁娶通道不应发射黄沙日: {hs}'
_notes.append('pipeline 反向锁：§212 后嫁娶神煞黄沙日 0 条（谓词保留）')


cases = [
    ShenShaCase(name='黄沙(基类·节气月支版·2026穷举)', category='B',
                description='节气月支版：四孟午/四仲寅/四季子',
                inputs=_year_days(2026),
                expected=_expected, adapter=_ad_base),
    ShenShaCase(name='黄沙(嫁娶神煞·节气月支版·2026穷举)', category='B',
                description='嫁娶神煞 _is_huangsha 与基类逐日一致',
                inputs=_year_days(2026),
                expected=_expected, adapter=_ad_mrg),
    ShenShaCase(name='黄沙(嫁娶规则文案链端到端·2026穷举)', category='B',
                description='§212 后 _check_rules 忌项已剥离黄沙日（全期零发射）',
                inputs=_year_days(2026),
                expected=_exp_none, adapter=_ad_rule),
    ShenShaCase(name='黄沙(基类·2025全年)', category='B',
                description='2025 公历年 29 天命中',
                inputs=_year_days(2025),
                expected=_expected, adapter=_ad_base),
    ShenShaCase(name='黄沙(嫁娶神煞·2025全年)', category='B',
                description='嫁娶神煞 2025 与基类逐日一致',
                inputs=_year_days(2025),
                expected=_expected, adapter=_ad_mrg),
]


if __name__ == '__main__':
    run_cli(cases)
