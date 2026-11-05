# -*- coding: utf-8 -*-
"""
大利年/小利年删除锁定验证（跟踪项24，2026-09-22 用户拍板"全部按《协纪》"）
=========================================================================================
背景：
    《协纪辨方书》嫁娶篇有"大利月/小利月"正式条目（女命年支×农历月），
    无"大利年/小利年"条目。软件原 analyze_year 中的大利年（天干五合+30）
    /小利年（同极相生+15）为无典籍依据的自创规则，2026-09-22 三副本删除。

本验证锁定四项断言：
  ① Scorer 无 _is_dali_year / _is_xiaoli_year 属性（运行时删除锁定）
  ② analyze_year 行为锁定：甲申年（2004）新娘 × 2026 丙午流年——删除前
     该组合必命中"新娘小利年"（删除前实证见 001 跟踪项24），删除后
     reasons 不得再出现"大利年/小利年"（反向断言）
  ③ 利月功能仍在：_check_li_yue 保留（防误删锁定）
  ④ 利月行为仍生效：丁卯年（1987）新娘 × 2026-03（含农历正月）→
     《协纪》"正七迎鸡兔"（卯命大利正月），analyze_month reasons 含
     "新娘大利月"（正向断言，排除利月被连带误删）
  ⑤ 三副本源码扫描：主源 + 两手机副本 评分器.py 无大利年/小利年残留

退出码 0/1，可挂 CI。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SCORER_COPIES = [
    ROOT / 'modules' / '评分器.py',
    ROOT / '手机一键部署' / '模块完整版' / 'modules' / '评分器.py',
]

from modules.评分器 import Scorer

fails = []


def check(name, ok, detail=''):
    tag = 'OK' if ok else 'FAIL'
    print(f"[{tag}] {name}" + (f" — {detail}" if detail else ''))
    if not ok:
        fails.append(name)


scorer = Scorer()

def main():
    # ① 运行时删除锁定
    check("① Scorer 无 _is_dali_year 属性", not hasattr(scorer, '_is_dali_year'))
    check("① Scorer 无 _is_xiaoli_year 属性", not hasattr(scorer, '_is_xiaoli_year'))

    # ② analyze_year 行为锁定（删除前必命中组合的反向断言）
    bride_2004 = {'name': '验证新娘甲申', 'role': '新娘', 'gender': '女',
                  'birth_date': date(2004, 6, 15), 'birth_hour': 12, 'birth_minute': 0}
    r_year = scorer.analyze_year(2026, '嫁娶', owners=[bride_2004])
    reasons_year = [str(x) for x in r_year.get('reasons', [])]
    hit_li_year = [x for x in reasons_year if ('大利年' in x or '小利年' in x)]
    check("② analyze_year reasons 无大利年/小利年", not hit_li_year,
          f"命中={hit_li_year}" if hit_li_year else f"reasons={reasons_year}")

    # ③ 利月功能仍在（防误删锁定）
    check("③ _check_li_yue 保留", hasattr(scorer, '_check_li_yue'))

    # ④ 利月行为仍生效：卯命新娘 × 2026-03（农历正月）→ 大利月
    bride_1987 = {'name': '验证新娘丁卯', 'role': '新娘', 'gender': '女',
                  'birth_date': date(1987, 6, 15), 'birth_hour': 12, 'birth_minute': 0}
    r_month = scorer.analyze_month(date(2026, 3, 1), '嫁娶', owners=[bride_1987])
    reasons_month = [str(x) for x in r_month.get('reasons', [])]
    hit_dali_month = [x for x in reasons_month if '新娘大利月' in x]
    check("④ analyze_month 命中 新娘大利月（卯命大利正月）", bool(hit_dali_month),
          f"命中={hit_dali_month}" if hit_dali_month else f"reasons={reasons_month}")

    # ⑤ 三副本源码扫描（无利年残留）
    for p in SCORER_COPIES:
        text = p.read_text(encoding='utf-8')
        residue = [kw for kw in ('_is_dali_year', '_is_xiaoli_year', '大利年', '小利年')
                   if kw in text]
        check(f"⑤ {p.relative_to(ROOT)} 无利年残留", not residue,
              f"残留={residue}" if residue else '')
        keep = ('_check_li_yue' in text and '大利月' in text and '小利月' in text)
        check(f"⑤ {p.relative_to(ROOT)} 利月功能保留", keep)

    print('=' * 60)
    if fails:
        print(f"VERIFY LIYUE FAIL（{len(fails)} 项）: {fails}")
        sys.exit(1)
    print("VERIFY LIYUE PASS：大利年/小利年已删除且利月功能完整保留")
    sys.exit(0)


if __name__ == '__main__':
    main()
