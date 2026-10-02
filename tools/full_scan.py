# -*- coding: utf-8 -*-
"""365天全量校验器扫描：统计各规则命中分布，发现隐藏问题类型。"""
import sys, datetime, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import Counter
from modules.评分器 import Scorer
from modules.四柱计算器 import calculate_sizhu
from modules.推荐时柱 import build_checker
from modules.日课校验器 import lint_lesson

OWNERS = [
    {'name': '欢', 'role': '新娘', '性别': '女', 'birth_date': '1999-04-05'},
    {'name': '文旺', 'role': '新郎', '性别': '男', 'birth_date': '1998-10-13'},
]

def main():
    base = datetime.date(2026, 1, 1)
    cnt = Counter()
    err_samples = {}
    exceptions = []
    for off in range(365):
        d = base + datetime.timedelta(days=off)
        try:
            sz = calculate_sizhu(d, 12, 0)
            sz.update({'year': d.year, 'month': d.month, 'day': d.day, 'date': d})
            res = Scorer().score(sz, '嫁娶', owners=OWNERS)
            ck, _ = build_checker('嫁娶', None, '')
            lucky = ck.get_lucky_hours(res.get('sizhu') or sz)
            lint = lint_lesson(res, lucky_hours=lucky, bride_year_zhi='卯')
            for i in lint.issues:
                cnt[f'{i.rule_id}:{i.severity}'] += 1
                if i.severity == 'ERROR' and i.rule_id != 'E004':
                    err_samples.setdefault(i.rule_id, []).append(
                        {'date': str(d), 'msg': i.message[:120]})
        except Exception as e:
            exceptions.append({'date': str(d), 'err': f'{type(e).__name__}: {e}'})
    print('=== 命中分布 ===')
    for k, v in sorted(cnt.items()):
        print(f'  {k}: {v}')
    print(f'\n=== 非E004 ERROR 案例 ===')
    for rid, cases in err_samples.items():
        print(f'  {rid}: {len(cases)} 例')
        for c in cases[:3]:
            print(f"    {c['date']}: {c['msg']}")
    print(f'\n=== 异常 ===: {len(exceptions)}')
    for e in exceptions[:5]:
        print(f"  {e['date']}: {e['err']}")
    out = {'counts': dict(cnt), 'error_samples': err_samples, 'exceptions': exceptions}
    os.makedirs('data', exist_ok=True)
    with open('data/full_scan_2026.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('\n已保存 data/full_scan_2026.json')

if __name__ == '__main__':
    main()
