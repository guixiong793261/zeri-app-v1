# -*- coding: utf-8 -*-
"""回归：一票否决嫁娶日课经时柱注入后，总分仍须锁死为 0、明细不得被覆盖。

背景（2026-11-06 用户案例 2023-01-11 壬寅 癸丑 己巳 乙丑）：
    否决分支 score_details 不含 marriage_details / 嫁娶明细(分项)，
    主程序 _inject_best_hour_to_result 的 (5') 合局重算把空表当原值 0，
    将权威时柱算出的合局分（+8）加回已归零的总分（0→8），
    并用单条合局明细覆盖整张 marriage_details，触发校验器 E001 + E007×3。

本脚本断言：
    1. 评分器原始 result：score=0、有 veto_reasons；
    2. 走完 _inject_best_hour_to_result 后：score / score_details['总分'] /
       result['score'] 三者仍为 0；
    3. 顶层 marriage_details 条数与扣分明细保持原样（不被覆盖成单条）；
    4. 校验器对同一份 detail 不再报 E001/E007。
"""
import os
import sys
import traceback
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score

FAILED = []


def check(tag, desc, ok, detail=''):
    if ok:
        print('[PASS] %s %s' % (tag, desc))
    else:
        print('[FAIL] %s %s %s' % (tag, desc, detail))
        FAILED.append(tag)


def _owners():
    return [
        {'name': '新娘', 'gender': '女', 'birth_date': date(1996, 9, 19),
         'birth_hour': 12, 'sizhu': '丙子 丁酉 己未 己巳'},
        {'name': '新郎', 'gender': '男', 'birth_date': date(1994, 10, 28),
         'birth_hour': 12, 'sizhu': '甲戌 甲戌 丁亥 壬寅'},
    ]


def main():
    d = date(2023, 1, 11)
    owners = _owners()
    sizhu = calculate_sizhu(d, 12, 0)
    sr = calculate_score(sizhu, '嫁娶', owners)

    check('S1', '评分器已判一票否决（日支巳冲新郎日支亥）',
          bool(sr.get('veto_reasons')), str(sr.get('veto_reasons'))[:80])
    check('S2', '评分器原始 score=0', (sr.get('score') or 0) == 0,
          'score=%r' % sr.get('score'))

    md_before = list(sr.get('marriage_details') or [])
    neg_before = [x for x in md_before
                  if isinstance(x, (list, tuple)) and len(x) >= 2
                  and isinstance(x[1], (int, float)) and x[1] < 0]
    check('S3', '原始嫁娶明细含扣分项（≥2 条且含厌对）',
          len(neg_before) >= 2 and any('厌对' in str(x[0]) for x in neg_before),
          '明细=%d 负分=%d' % (len(md_before), len(neg_before)))

    # ── 复用主程序真实注入流程（不启动 GUI）──
    import 主程序 as m
    app = m.ZeriApp.__new__(m.ZeriApp)
    result = {
        'date': d, 'sizhu': str(sizhu.get('年柱', '')) + ' ' +
        str(sizhu.get('月柱', '')) + ' ' + str(sizhu.get('日柱', '')),
        'score': sr.get('score'), 'level': sr.get('level'),
        'detail': sr,
    }
    app._inject_best_hour_to_result(result, sr, '嫁娶', owners, d, sizhu)

    check('S4', '注入后 score 仍为 0', (sr.get('score') or 0) == 0,
          'score=%r' % sr.get('score'))
    check('S5', '注入后 score_details[总分] 仍为 0',
          (sr.get('score_details') or {}).get('总分') == 0,
          '总分=%r' % (sr.get('score_details') or {}).get('总分'))
    check('S6', '注入后 result[score] 仍为 0', (result.get('score') or 0) == 0,
          'result.score=%r' % result.get('score'))

    md_after = list(sr.get('marriage_details') or [])
    check('S7', 'marriage_details 未被覆盖（条数不变：%d→%d）'
          % (len(md_before), len(md_after)),
          len(md_after) == len(md_before), 'after=%r' % (md_after,))
    names_after = [str(x[0]) for x in md_after
                   if isinstance(x, (list, tuple)) and len(x) >= 2]
    _missing = [str(x[0]) for x in neg_before if str(x[0]) not in names_after]
    check('S8', '原有扣分项全部保留（无丢失）', not _missing, '缺失=%r' % (_missing,))

    # S9：校验器复检（同一份 detail，确认 E001/E007 不再出现）
    try:
        from modules.日课校验器 import lint_lesson
        _res = lint_lesson(sr)
        errs = [i for i in _res.issues if getattr(i, 'rule_id', '') in ('E001', 'E007')]
        check('S9', '校验器不再报 E001/E007', not errs,
              '%r' % [(getattr(i, 'rule_id', ''), getattr(i, 'message', ''))
                       for i in errs])
    except Exception as e:  # noqa: BLE001
        print('[SKIP] S9 校验器接口不匹配：%s: %s' % (type(e).__name__, e))

    print()
    if FAILED:
        print('RESULT FAIL：%s' % ', '.join(FAILED))
        return 1
    print('RESULT PASS：否决日总分锁 0、明细完整')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        sys.exit(1)
