# -*- coding: utf-8 -*-
"""
verify_standalone_consistency.py —— 精准择时独立版 vs 主程序 一致性对拍（阶段三）

校验目标（用户指令原文）：
  1) 独立版调用的是共享的 modules/评分器.py、modules/反推引擎.py，而非私包一份；
  2) 随机挑 10 天，「主程序口径」与「独立版口径」组装的 owners/context
     喂给同一反推引擎，Top-N 榜单（分数、吉神、排序、动作时序）逐字相同。

对拍方法：
  - 主程序口径：直接调用主程序 ZeriApp._collect_owners_data 真实代码路径
    （unbound 调用 + StringVar 假事主行），不走任何复制重抄；
  - 独立版口径：实例化 精准择时版_主程序.精准择时版App（隐藏主窗），
    走真实 UI 字段 → _collect_owners_data() / _build_context()；
  - 引擎：modules.反推引擎.search_top_n 双跑，序列化逐字比对。

退出码：0 全过 / 1 有失败（CI 口径）。
"""
import json
import os
import random
import sys
from datetime import date, timedelta
from types import SimpleNamespace

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FAILURES = []


def check(name, ok, detail=''):
    print(f"[{'PASS' if ok else 'FAIL'}] {detail}")
    if not ok:
        FAILURES.append(detail)


def serialize_rank(result):
    """Top-N 榜单序列化：分数、吉神、排序、动作时序、否决清单、热力日历全量比对。"""
    def one_day(rec):
        return {
            'date': rec.get('date'),
            'score': rec.get('score'),
            'level': rec.get('level'),
            'kind': rec.get('kind'),
            'jishen': rec.get('jishen'),
            'deduct_items': rec.get('deduct_items'),
            'ji_items': rec.get('ji_items'),
            'best_hour': rec.get('best_hour'),
            'veto_reasons': rec.get('veto_reasons'),
            'action_plan': rec.get('action_plan'),
        }
    return json.dumps({
        'days': [one_day(d) for d in result.get('days', [])],
        'vetoed': result.get('vetoed'),
        'all_days': result.get('all_days'),
    }, ensure_ascii=False, sort_keys=True, default=str)


def main():
    import tkinter as tk
    import modules.反推引擎 as engine
    import modules.评分器 as scorer
    import modules.四柱计算器 as sizhu_mod
    import modules.反推UI as reverse_ui
    import 精准择时版_主程序 as sa

    # ---------- 1) 共享底层断言：独立版不得私包计分逻辑 ----------
    check('shared_reverse_ui', sa.open_reverse_window is reverse_ui.open_reverse_window,
          '独立版 open_reverse_window 与 modules.反推UI 为同一函数对象')
    check('shared_sizhu', sa.calculate_sizhu is sizhu_mod.calculate_sizhu,
          '独立版 calculate_sizhu 与 modules.四柱计算器 为同一函数对象')
    scorer_path = os.path.normcase(os.path.abspath(scorer.__file__))
    expect_path = os.path.normcase(os.path.join(PROJECT_ROOT, 'modules', '评分器.py'))
    check('shared_scorer_path', scorer_path == expect_path,
          f'评分器加载路径 == 主仓 modules/评分器.py（实际：{scorer_path}）')
    check('no_private_score', 'calculate_score' not in sa.__dict__ and 'Scorer' not in sa.__dict__,
          '独立版模块命名空间内不存在自有 calculate_score/Scorer（未私包计分）')

    # ---------- 2) 事主/context 组装双口径对拍 ----------
    import 主程序 as main_prog

    root = tk.Tk()
    root.withdraw()
    app = sa.精准择时版App(root)

    # 固定测试事主（嫁娶双事主：新郎 1990-05-16 08:30 成都；新娘 1992-09-02 14:05 北京）
    from modules.城市经度 import get_longitude
    raw_owners = [
        dict(role='新郎', name='测试郎', gender='男', year='1990', month='5', day='16',
             hour='8', minute='30', city='成都'),
        dict(role='新娘', name='测试娘', gender='女', year='1992', month='9', day='2',
             hour='14', minute='5', city='北京'),
    ]
    # 独立版：写入真实 UI 字段
    for row, raw in zip(app.owner_rows, raw_owners):
        row['role'].set(raw['role'])
        for key in ('name', 'year', 'month', 'day', 'hour', 'minute', 'city'):
            w = row[key]
            widget = row[key]
            widget.delete(0, tk.END)
            widget.insert(0, raw[key])
        row['gender'].set(raw['gender'])
    app.event_var.set('嫁娶')
    owners_sa = app._collect_owners_data()

    # 主程序口径：ZeriApp._collect_owners_data 真实代码路径（StringVar 假事主行）
    def _sv(v):
        var = tk.StringVar(master=root)
        var.set(v)
        return var
    fake_infos = []
    for raw in raw_owners:
        fake_infos.append({
            'year': _sv(raw['year']), 'month': _sv(raw['month']), 'day': _sv(raw['day']),
            'hour': _sv(raw['hour']), 'minute': _sv(raw['minute']),
            'gender': _sv(raw['gender']), 'name': _sv(raw['name']),
            'role': raw['role'],
            'longitude': _sv(str(get_longitude(raw['city']))),
        })
    fake_self = SimpleNamespace(owners_info=fake_infos)
    owners_main = main_prog.ZeriApp._collect_owners_data(fake_self, silent=True)

    keys = ['name', 'role', 'birth_date', 'birth_hour', 'birth_minute', 'birth_longitude',
            '性别', '年干', '年支', '日干', '日支', '生肖']
    sa_flat = [{k: str(o.get(k)) for k in keys} for o in owners_sa]
    main_flat = [{k: str(o.get(k)) for k in keys} for o in owners_main]
    check('owners_equal', sa_flat == main_flat and len(sa_flat) == 2,
          f'owners_data 逐字段一致（独立版 {len(sa_flat)} 人 vs 主程序 {len(main_flat)} 人）')
    if sa_flat != main_flat:
        print('  独立版:', json.dumps(sa_flat, ensure_ascii=False))
        print('  主程序:', json.dumps(main_flat, ensure_ascii=False))

    # context 对拍（修造 + 子山午向 + 兼左 → 兼向拼接规则与主程序 L4442-4458 同口径）
    app.event_var.set('修造')
    app.shan_xiang_var.set('子山午向')
    app.jian_xiang_var.set('兼左')
    app.house_type_var.set('阳宅')
    ctx_sa = app._build_context()
    ctx_main = {  # 主程序 open_reverse_panel 内联规则的原样参照
        'house_type': '阳宅',
        'shan_xiang': '子山午向兼左',
        'zao_xiang': None, 'zao_wei': None, 'chuang_wei': None, 'zaozhu_mode': None,
        'zeli_mode': 'pure',
    }
    check('context_equal', ctx_sa == ctx_main,
          f'context 一致（独立版：{ctx_sa}）')

    # ---------- 3) 随机 10 天引擎双跑：Top-N 榜单逐字相同 ----------
    rng = random.Random(20261109)
    starts = sorted(rng.sample(range(1, 360), 10))
    base = date(2026, 1, 1)
    ok_all = True
    for i, off in enumerate(starts, 1):
        start_d = base + timedelta(days=off)
        r_sa = engine.search_top_n(days=10, event_type='修造', owners=owners_sa,
                                   start=start_d, top_n=5, context=ctx_sa)
        r_main = engine.search_top_n(days=10, event_type='修造', owners=owners_main,
                                     start=start_d, top_n=5, context=ctx_main)
        same = serialize_rank(r_sa) == serialize_rank(r_main)
        ok_all = ok_all and same
        n_sa = len(r_sa.get('days', []))
        print(f"  [对拍 {i:02d}/10] 起始 {start_d} 入榜 {n_sa} 条 → {'逐字相同' if same else '不一致!!'}")
    check('topn_identical_10days', ok_all, '随机 10 天 Top-N 榜单（分数/吉神/排序/动作时序）逐字相同')

    try:
        root.destroy()
    except Exception as e:
        print(f'（清理 Tk 根窗时出现异常，已忽略：{e}）')

    print('=' * 60)
    if FAILURES:
        print(f'共 {len(FAILURES)} 项失败：')
        for f in FAILURES:
            print('  -', f)
        return 1
    print('全部通过：独立版与主程序共享底层、榜单输出逐字一致。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
